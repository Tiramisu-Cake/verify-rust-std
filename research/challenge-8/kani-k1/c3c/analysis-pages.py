#!/usr/bin/env python3
"""Aggregate explicitly supplied bounded K-1 row/inventory summary pages.

This consumes exported summary pages only (for example *.rows.tsv and
*.inventory-*.page). It does not fetch evidence or read verifier logs.
Incomplete pagination and conflicting source identities remain visible in the
JSON output; no missing result or timeout is imputed as a duration.
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


ROW_COLUMNS = ("name", "status", "time_s", "checks", "covers")
IDENTITY_FIELDS = ("request_id", "request_sha256", "build_id", "head_sha", "kani_commit")


def expand(items: list[str]) -> list[Path]:
    result: list[Path] = []
    for item in items:
        matches = [Path(p) for p in sorted(glob.glob(item))]
        result.extend(matches if matches else [Path(item)])
    return sorted(set(result))


def parse_page(path: Path) -> tuple[dict[str, str], list[str], list[list[str]]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    metadata: dict[str, str] = {}
    split = None
    for index, line in enumerate(lines):
        if line == "name\tstatus\ttime_s\tchecks\tcovers":
            split = index
            break
        if "=" in line:
            key, value = line.split("=", 1)
            metadata[key] = value
    if split is None:
        raise ValueError(f"{path}: expected bounded summary row header")
    reader = csv.reader(lines[split:], delimiter="\t")
    header = next(reader)
    rows = list(reader)
    if tuple(header) != ROW_COLUMNS:
        raise ValueError(f"{path}: unsupported columns {header!r}")
    return metadata, header, rows


def parse_inventory(path: Path) -> tuple[dict[str, str], list[str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    metadata: dict[str, str] = {}
    names: list[str] = []
    data_started = False
    for line in lines:
        if not data_started and "=" in line:
            key, value = line.split("=", 1)
            metadata[key] = value
        elif line:
            data_started = True
            names.append(line)
    return metadata, names


def page_range(meta: dict[str, str], path: Path) -> tuple[int, int, int, str]:
    try:
        offset, count, total = (int(meta[key]) for key in ("offset", "count", "total"))
        following = meta["next_offset"]
    except (KeyError, ValueError) as error:
        raise ValueError(f"{path}: missing/invalid pagination metadata") from error
    if offset < 0 or count < 0 or total < 0 or offset + count > total:
        raise ValueError(f"{path}: invalid page range {offset}+{count}/{total}")
    if following != "done" and int(following) != offset + count:
        raise ValueError(f"{path}: next_offset does not follow this page")
    return offset, count, total, following


def summarize(rows: list[dict], inventory_names: list[str], limit: float) -> dict:
    inventory_counts = Counter(inventory_names)
    row_counts = Counter(r["name"] for r in rows)
    by_family: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        name = row["name"]
        parts = name.split("::")
        family = parts[-2] if len(parts) >= 2 else "unknown"
        by_family[family].append(row)

    family_summary = {}
    for family, family_rows in sorted(by_family.items()):
        timed = [r["time_s"] for r in family_rows if r["time_s"] is not None]
        statuses = Counter(r["status"] for r in family_rows)
        family_summary[family] = {
            "rows": len(family_rows),
            "statuses": dict(sorted(statuses.items())),
            "timed_rows": len(timed),
            "sum_observed_time_s": sum(timed),
            "max_observed_time_s": max(timed, default=None),
            "over_limit": sorted(r["name"] for r in family_rows
                                  if r["time_s"] is not None and r["time_s"] > limit),
            "censored_or_untimed": sorted(r["name"] for r in family_rows
                                           if r["time_s"] is None),
        }

    absent = sorted((inventory_counts - row_counts).elements())
    unlisted = sorted((row_counts - inventory_counts).elements()) if inventory_names else []
    failures = sorted(r["name"] for r in rows
                      if r["status"].upper() not in ("SUCCESS", "SUCCESSFUL"))
    slow = sorted((r["name"], r["time_s"]) for r in rows
                  if r["time_s"] is not None and r["time_s"] > limit)
    timed = [r["time_s"] for r in rows if r["time_s"] is not None]
    return {
        "inventory_count": len(inventory_names),
        "observed_rows": len(rows),
        "duplicate_inventory_name_counts": {k: v for k, v in sorted(inventory_counts.items()) if v > 1},
        "duplicate_row_name_counts": {k: v for k, v in sorted(row_counts.items()) if v > 1},
        "missing_from_rows": absent,
        "rows_not_in_inventory": unlisted,
        "failures_or_timeouts": failures,
        "over_limit_rows": [{"name": name, "time_s": seconds} for name, seconds in slow],
        "timed_rows": len(timed),
        "sum_observed_time_s": sum(timed),
        "max_observed_time_s": max(timed, default=None),
        "limit_seconds": limit,
        "family_summary": family_summary,
    }


def analyze(row_paths: list[Path], inventory_paths: list[Path], limit: float) -> dict:
    identities: dict[str, set[str]] = defaultdict(set)
    page_errors: list[str] = []
    rows: list[dict] = []
    row_pages = []
    for path in row_paths:
        meta, _, raw_rows = parse_page(path)
        for key in IDENTITY_FIELDS:
            if key in meta:
                identities[key].add(meta[key])
        offset, count, total, following = page_range(meta, path)
        if count != len(raw_rows):
            page_errors.append(f"{path}: count={count}, parsed_rows={len(raw_rows)}")
        row_pages.append({"path": str(path), "offset": offset, "count": count,
                          "total": total, "next_offset": following})
        for fields in raw_rows:
            if len(fields) != len(ROW_COLUMNS):
                page_errors.append(f"{path}: malformed row with {len(fields)} fields")
                continue
            name, status, value, checks, covers = fields
            try:
                seconds = None if value in ("", "None", "null") else float(value)
            except ValueError:
                page_errors.append(f"{path}: invalid time for {name}")
                continue
            if seconds is not None and (not math.isfinite(seconds) or seconds < 0):
                page_errors.append(f"{path}: invalid nonnegative time for {name}")
                continue
            row = {"name": name, "status": status, "time_s": seconds,
                   "checks": checks or None, "covers": covers or None,
                   "page": str(path), "source": {k: meta.get(k) for k in IDENTITY_FIELDS}}
            rows.append(row)

    inventory_names: list[str] = []
    inventory_pages = []
    inventory_totals = set()
    for path in inventory_paths:
        meta, names = parse_inventory(path)
        for key in IDENTITY_FIELDS:
            if key in meta:
                identities[key].add(meta[key])
        offset, count, total, following = page_range(meta, path)
        inventory_totals.add(total)
        if count != len(names):
            page_errors.append(f"{path}: count={count}, parsed_names={len(names)}")
        inventory_names.extend(names)
        inventory_pages.append({"path": str(path), "offset": offset, "count": count,
                                "total": total, "next_offset": following})

    identity_conflicts = {k: sorted(v) for k, v in identities.items() if len(v) > 1}
    for pages, label in ((row_pages, "row"), (inventory_pages, "inventory")):
        if pages:
            totals = {page["total"] for page in pages}
            if len(totals) > 1:
                page_errors.append(f"{label} pages disagree on total: {sorted(totals)}")
            covered = {n for page in pages for n in range(page["offset"], page["offset"] + page["count"])}
            total = max(totals)
            missing_offsets = sorted(set(range(total)) - covered)
            if missing_offsets:
                page_errors.append(f"{label} pagination incomplete: {len(missing_offsets)} offsets missing")
            if len(covered) != sum(page["count"] for page in pages):
                page_errors.append(f"{label} page ranges overlap")
    if inventory_totals and len(inventory_names) != max(inventory_totals):
        page_errors.append(f"inventory row count {len(inventory_names)} != total {max(inventory_totals)}")

    row_names = Counter(row["name"] for row in rows)
    inventory_counts = Counter(inventory_names)
    missing_counts = inventory_counts - row_names
    extra_counts = row_names - inventory_counts

    return {
        "schema": "c3c-bounded-summary-analysis-v1",
        "inputs_are_bounded_summary_pages": True,
        "raw_logs_read": False,
        "source_identities": {k: (next(iter(v)) if len(v) == 1 else sorted(v))
                              for k, v in sorted(identities.items())},
        "identity_conflicts": identity_conflicts,
        "row_pages": row_pages,
        "inventory_pages": inventory_pages,
        "page_errors": page_errors,
        "duplicate_row_name_counts": {k: v for k, v in sorted(row_names.items()) if v > 1},
        "summary": summarize(rows, inventory_names, limit),
        "rows": sorted(rows, key=lambda row: (row["name"], row["page"])),
        "complete": bool(inventory_paths and row_paths and not page_errors
                          and not identity_conflicts and not missing_counts and not extra_counts),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", nargs="+", required=True,
                        help="bounded *.rows.tsv page paths or shell-style globs")
    parser.add_argument("--inventory-pages", nargs="+", required=True,
                        help="bounded *.inventory-*.page paths or shell-style globs")
    parser.add_argument("--limit", type=float, default=300.0,
                        help="ordinary timing risk threshold in seconds (default: 300)")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = analyze(expand(args.rows), expand(args.inventory_pages), args.limit)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"complete": result["complete"], "rows": len(result["rows"]),
                      "inventory": result["summary"]["inventory_count"],
                      "sum_observed_time_s": result["summary"]["sum_observed_time_s"],
                      "max_observed_time_s": result["summary"]["max_observed_time_s"],
                      "page_errors": len(result["page_errors"]),
                      "identity_conflicts": len(result["identity_conflicts"])}, indent=2))


if __name__ == "__main__":
    main()
