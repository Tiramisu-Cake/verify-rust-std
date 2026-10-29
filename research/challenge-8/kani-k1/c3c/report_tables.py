#!/usr/bin/env python3
"""Render bounded C3c evidence tables without CI, Kani, or verifier execution."""
from __future__ import annotations

import csv
import datetime as dt
import json
import math
import re
import statistics
import sys
import unittest
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

BASE = Path(__file__).resolve().parent
EVIDENCE = BASE / "evidence"
INPUTS = BASE.parent / "c3c-inputs"
PREFIX = "slice::sort::shared::smallsort::verify::"
SESSION = json.loads((BASE / "session.json").read_text())
MEASUREMENTS_PATH = BASE / "measurements.json"


def read_json(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return default


def parse_duration(value: str | None) -> float | None:
    if not value:
        return None
    value = value.strip().split()[0]
    try:
        parts = [float(p) for p in value.split(":")]
    except ValueError:
        return None
    if len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    if len(parts) == 2:
        return parts[0] * 60 + parts[1]
    return parts[0] if len(parts) == 1 else None


def cloud_wall(status: dict[str, Any]) -> float | None:
    try:
        start = dt.datetime.fromisoformat(status["startTime"].replace("Z", "+00:00"))
        finish = dt.datetime.fromisoformat(status["finishTime"].replace("Z", "+00:00"))
        return (finish - start).total_seconds()
    except (KeyError, TypeError, ValueError):
        return None


def summary_fields(label: str) -> dict[str, Any]:
    p = EVIDENCE / f"{label}.summary.md"
    if not p.exists():
        return {}
    text = p.read_text()
    m = re.search(r"^# K-1 run `[^`]+`: (\w+)", text, re.M)
    gate = re.search(r"^- gate: (\w+);", text, re.M)
    wall = re.search(r"whole run, including compilation: max RSS (\S+) KiB, wall ([^ ]+)", text)
    command_wall = wall.group(2) if wall else None
    if command_wall and command_wall.lower() in {"none", "missing", "?"}:
        command_wall = None
    return {
        "kani_status": m.group(1) if m else None,
        "gate": gate.group(1) if gate else None,
        "kani_command_wall": command_wall,
        "kani_command_wall_seconds": parse_duration(command_wall),
        "whole_run_max_rss_kb": wall.group(1) if wall else None,
    }


def read_rows(label: str, measured: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    # Bounded row exports are authoritative when present; derived rows fill gaps.
    rows: list[dict[str, Any]] = []
    for p in sorted(EVIDENCE.glob(f"{label}.*.rows.tsv")):
        lines = p.read_text().splitlines()
        try:
            head = lines.index("name\tstatus\ttime_s\tchecks\tcovers")
        except ValueError:
            continue
        for line in lines[head + 1 :]:
            cols = line.split("\t")
            if len(cols) < 5:
                continue
            name, status, seconds, checks, covers = cols[:5]
            try:
                sec = float(seconds) if seconds not in ("", "None", "NA") else None
                if sec is not None and (not math.isfinite(sec) or sec < 0):
                    sec = None
            except ValueError:
                sec = None
            rows.append({"name": name, "status": status, "time_s": sec,
                         "checks": checks, "covers": covers, "evidence": p.name})
    if rows:
        return rows
    if measured:
        return [dict(r) for r in measured.get("rows", [])]
    return []


def read_memory(label: str, measured: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    out = []
    for p in sorted(EVIDENCE.glob(f"{label}.process-*.txt")):
        for line in p.read_text().splitlines():
            if not line.startswith("{"):
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            row.setdefault("evidence_file", p.name)
            out.append(row)
    if out:
        return out
    return [dict(r) for r in (measured or {}).get("process_memory", [])]


def read_peaks(label: str, measured: dict[str, Any] | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {"commands": {}, "roles": {}, "source_file": None}
    path = EVIDENCE / f"{label}.peaks.txt"
    if path.exists():
        result["source_file"] = path.name
        for line in path.read_text().splitlines():
            if line.startswith("cmd="):
                m = re.fullmatch(r"cmd=(\S+) peak_kb=(\d+) first_s=(\d+) last_s=(\d+) peak_s=(\d+)", line)
                if m:
                    n, hwm, first, last, sec = m.groups()
                    result["commands"][n] = {"hwm_kb": int(hwm), "first_s": int(first),
                                              "last_s": int(last), "peak_s": int(sec)}
            elif line.startswith("role="):
                m = re.fullmatch(r"role=(\S+) simultaneous_rss_peak_kb=(\d+) peak_s=(\d+)", line)
                if m:
                    n, rss, sec = m.groups()
                    result["roles"][n] = {"simultaneous_rss_peak_kb": int(rss), "peak_s": int(sec)}
            elif line.startswith(("total_rss_peak_kb=", "total_peak_s=")):
                k, v = line.split("=", 1)
                result[k] = int(v)
        return result
    p = (measured or {}).get("peaks", {})
    if p:
        result["source_file"] = f"measurements.json:builds.{label}.peaks"
        for row in p.get("commands", []):
            result["commands"][row.get("cmd", "?")] = {
                "hwm_kb": row.get("peak_kb"), "first_s": row.get("first_s"),
                "last_s": row.get("last_s"), "peak_s": row.get("peak_s")}
        for row in p.get("roles", []):
            result["roles"][row.get("role", "?")] = {
                "simultaneous_rss_peak_kb": row.get("simultaneous_rss_peak_kb"),
                "peak_s": row.get("peak_s")}
        result["total_rss_peak_kb"] = p.get("total_rss_peak_kb")
        result["total_peak_s"] = p.get("total_peak_s")
    return result


def measurement_builds(measurements: dict[str, Any]) -> dict[str, dict[str, Any]]:
    builds = measurements.get("builds", {})
    return builds if isinstance(builds, dict) else {}


def build_rows(measurements: dict[str, Any]) -> list[dict[str, Any]]:
    measured = measurement_builds(measurements)
    result = []
    for entry in SESSION.get("builds", []):
        label = entry["label"]
        m = measured.get(label, {})
        status = read_json(EVIDENCE / f"{label}.status.json", {}) or m.get("build_metadata", {})
        sf = summary_fields(label)
        wall = cloud_wall(status)
        # Match analyze_results.py's wall-time ledger calculation; keep it distinct from reserves.
        cost = m.get("build_metadata", {}).get("ledger_cost_usd")
        if cost is None:
            cost = status.get("ledger_cost_usd")
        if cost is None and wall is not None:
            cost = math.ceil(wall / 60) * 0.0135
        peaks = read_peaks(label, m)
        commands = peaks["commands"]
        solvers = {k: v for k, v in commands.items()
                   if any(s in k.lower() for s in ("kissat", "cadical", "minisat", "z3", "cvc5", "boolector", "bitwuzla"))}
        roles = peaks.get("roles", {})
        rows = read_rows(label, m)
        timed = [r.get("time_s") for r in rows if r.get("time_s") is not None]
        rows_available = bool(rows)
        ours = [r for r in rows if str(r.get("name", "")).startswith(PREFIX)]
        ours_timed = [r.get("time_s") for r in ours if r.get("time_s") is not None]
        evidence = sorted(p.name for p in EVIDENCE.glob(f"{label}.*") if p.is_file())
        if not evidence:
            evidence = ["NA: no bounded evidence page available"]
        result.append({
            "label": label, "build_id": status.get("id", entry.get("build_id")),
            "source_sha": status.get("source_sha", entry.get("sha")),
            "cloud_status": status.get("status", entry.get("terminal_status", "NA")),
            "kani_status": sf.get("kani_status", m.get("summary_status", "NA")),
            "gate": sf.get("gate", m.get("gate", "NA")),
            "cloud_wall_s": wall,
            "kani_command_wall": sf.get("kani_command_wall", m.get("command_wall")),
            "kani_command_wall_s": sf.get("kani_command_wall_seconds"),
            "used_ledger_cost_usd": cost,
            "cost_basis": "measured ledger value" if m.get("build_metadata", {}).get("ledger_cost_usd") is not None
                          else "wall-based ledger calculation at $0.0135/min; not reservation",
            "reserved_usd": entry.get("reserve_usd"),
            "driver_hwm_kb": commands.get("kani-driver", {}).get("hwm_kb"),
            "driver_hwm_peak_s": commands.get("kani-driver", {}).get("peak_s"),
            "cbmc_hwm_kb": commands.get("cbmc", {}).get("hwm_kb"),
            "cbmc_hwm_peak_s": commands.get("cbmc", {}).get("peak_s"),
            "cbmc_simultaneous_rss_kb": roles.get("cbmc", {}).get("simultaneous_rss_peak_kb"),
            "cbmc_simultaneous_rss_peak_s": roles.get("cbmc", {}).get("peak_s"),
            "driver_simultaneous_rss_kb": roles.get("driver", {}).get("simultaneous_rss_peak_kb"),
            "driver_simultaneous_rss_peak_s": roles.get("driver", {}).get("peak_s"),
            "solver_hwm": solvers or None,
            "solver_simultaneous_rss": roles.get("solver"),
            "sampled_total_rss_peak_kb": peaks.get("total_rss_peak_kb"),
            "sampled_total_rss_peak_s": peaks.get("total_peak_s"),
            "row_count": len(rows) if rows_available else None,
            "success_rows": sum(r.get("status") == "SUCCESS" for r in rows) if rows_available else None,
            "censored_or_untimed_rows": sum(r.get("time_s") is None for r in rows) if rows_available else None,
            "observed_vt_sum_s": round(sum(timed), 6) if rows_available else None,
            "smallsort_row_count": len(ours) if rows_available else None,
            "smallsort_success_count": sum(r.get("status") == "SUCCESS" for r in ours) if rows_available else None,
            "smallsort_observed_vt_sum_s": round(sum(ours_timed), 6) if rows_available else None,
            "evidence": evidence,
        })
    return result


def load_mac() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = []
    for i, line in enumerate((INPUTS / "mac-times.tsv").read_text().splitlines(), 1):
        cols = line.split("\t")
        if len(cols) != 3:
            continue
        try:
            seconds = float(cols[1])
        except ValueError:
            continue
        rows.append({"name": cols[0], "time_s": seconds, "status": cols[2], "line": i})
    ours = [r for r in rows if r["name"].startswith(PREFIX)]
    timeouts = [PREFIX + s for s in (
        "merge::merge_contract_u64_n16", "network::insertion_permutation_u64_n12",
        "network::insert_tail_contract_u64_start1")]
    return rows, {"all_rows": len(rows), "all_sum_s": round(sum(r["time_s"] for r in rows), 1),
                  "smallsort_rows": len(ours), "smallsort_sum_s": round(sum(r["time_s"] for r in ours), 1),
                  "smallsort_timeouts_600s": timeouts,
                  "sum_includes_timeouts": False,
                  "input": "../c3c-inputs/mac-times.tsv",
                  "source_identity": "Actions run 40748125754, P6 pre-C3a SHA 6cfc76cb211d088aebaff8a449bcac953e97f942 (task/source binding)",
                  "source_limitation": "TSV has only harness, elapsed seconds, status; no RAM, job wall, thread, or stop-time state."}


def typed_group(name: str) -> str:
    short = name.removeprefix(PREFIX)
    bits = short.split("::")
    if len(bits) < 2:
        return "unclassified"
    module, leaf = bits[0], bits[-1]
    scalar = next((x for x in ("u64", "u8") if f"_{x}_" in leaf), "untyped")
    if module == "correct":
        if "fallback_" in leaf: return f"correct.fallback.{scalar}"
        if "sorted_permutation_" in leaf: return f"correct.general_stable.{scalar}"
    if module == "merge":
        if leaf.startswith("merge_contract_"): return f"merge.contract.{scalar}"
        if leaf.startswith("route_safety_"): return "merge.upper_route_safety"
        if "sorted_permutation_" in leaf and not leaf.startswith("fallback_"): return f"merge.general_stable.{scalar}"
    if module == "network":
        if leaf.startswith("network_correctness_"): return f"network.correctness.{scalar}"
        if leaf.startswith("insert_tail_contract_"): return "network.tail_contract"
        if leaf.startswith("insertion_permutation_"): return f"network.insertion_permutation.{scalar}"
    if module == "assembly": return "assembly.zst" if "stable_unit_" in leaf else "assembly.primitive_witness"
    return f"{module}.unmatched"


def quantile_nearest_rank(values: list[float], q: float) -> float | None:
    if not values:
        return None
    values = sorted(values)
    return values[max(0, math.ceil(q * len(values)) - 1)]


def calibration(measurements: dict[str, Any], mac_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    # Prefer parent's refreshed calibration rows, retaining eligibility/censor labels.
    builds = measurement_builds(measurements)
    rows = measurements.get("calibration_rows", [])
    if rows:
        base = builds.get("baseline-memory") or builds.get("baseline") or {}
        base_label = "baseline-memory" if "baseline-memory" in builds else "baseline"
        entry = next((x for x in SESSION.get("builds", []) if x["label"] == base_label), {})
        enriched = []
        for row in rows:
            r = dict(row)
            r.setdefault("build_id", base.get("build_id", entry.get("build_id")))
            r.setdefault("source_sha", base.get("head_sha", entry.get("sha")))
            r.setdefault("library_sha", SESSION.get("baseline_library_sha"))
            r.setdefault("mac_run_id", "40748125754")
            r.setdefault("mac_source_sha", "6cfc76cb211d088aebaff8a449bcac953e97f942")
            enriched.append(r)
        return enriched
    base = builds.get("baseline-memory") or builds.get("baseline")
    if not base:
        return []
    mac = {r["name"]: r["time_s"] for r in mac_rows if r["status"] == "SUCCESSFUL"}
    mac_timeout = {PREFIX + x for x in ("merge::merge_contract_u64_n16",
                    "network::insertion_permutation_u64_n12", "network::insert_tail_contract_u64_start1")}
    cutoff = float(base.get("request", {}).get("harness_timeout_minutes", 3)) * 60
    result = []
    for r in base.get("rows", []):
        name, status, gcb = r.get("name", ""), r.get("status"), r.get("time_s")
        mt = mac.get(name)
        point = lower = upper = None
        mac_censored = 600 if name in mac_timeout else None
        eligible = not base.get("summary_status") or base.get("summary_status") == "COMPLETE"
        if eligible and status == "SUCCESS" and gcb is not None and mt is not None:
            point = mt / gcb
        elif eligible and status == "TIMEOUT" and mt is not None:
            upper = mt / cutoff
        elif eligible and mac_censored and status == "SUCCESS" and gcb:
            lower = mac_censored / gcb
        result.append({"name": name, "group": typed_group(name), "gcb_status": status,
                       "gcb_time_s": gcb, "mac_time_s": mt, "mac_censored_timeout_s": mac_censored,
                       "point_ratio": point, "ratio_lower_bound": lower, "ratio_upper_bound": upper,
                       "eligible": eligible, "eligibility_note": "P6 to e965 common source/model pairing; transfer to changed candidate remains forecast",
                       "build_id": base.get("build_id"), "source_sha": base.get("head_sha"),
                       "library_sha": SESSION.get("baseline_library_sha"), "mac_run_id": "40748125754",
                       "mac_source_sha": "6cfc76cb211d088aebaff8a449bcac953e97f942"})
    return result


def calibration_groups(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        groups[r.get("calibration_group") or r.get("group") or typed_group(r.get("name", ""))].append(r)
    result = []
    for name, rs in sorted(groups.items()):
        points = [float(r[k]) for r in rs if (k := "point_ratio") in r and r[k] is not None]
        lowers = [float(r["ratio_lower_bound"]) for r in rs if r.get("ratio_lower_bound") is not None]
        uppers = [float(r["ratio_upper_bound"]) for r in rs if r.get("ratio_upper_bound") is not None]
        censored = sum(r.get("gcb_status") == "TIMEOUT" or r.get("mac_censored_timeout_s") is not None for r in rs)
        result.append({"group": name, "n_rows": len(rs), "n_point": len(points), "n_censored": censored,
                       "median": statistics.median(points) if points else None,
                       "p90": quantile_nearest_rank(points, .9), "max_point": max(points, default=None),
                       "lower_censor_bounds": lowers, "upper_censor_bounds": uppers,
                       "n_dual_censored": sum(r.get("gcb_status") == "TIMEOUT" and r.get("mac_censored_timeout_s") is not None for r in rs),
                       "source_ids": sorted({str(r.get(k)) for r in rs for k in ("build_id", "source_sha", "library_sha", "mac_run_id", "mac_source_sha") if r.get(k)}),
                       "acceptance": False})
    return result


def process_records(label: str, measured: dict[str, Any] | None) -> list[dict[str, Any]]:
    records = read_memory(label, measured)
    for r in records:
        r.setdefault("source_build_label", label)
    return records


def choose_pair_series(five_minute_complete: bool, three_minute_complete: bool) -> tuple[str, tuple[str, ...], int | None]:
    """Select one matched cutoff series; never combine rows from different cutoffs."""
    if five_minute_complete:
        return "memory-5m", ("baseline-memory", "candidate-memory-1", "candidate-memory-2"), 5
    if three_minute_complete:
        return "matched-3m", ("baseline", "candidate"), 3
    return "unavailable", (), None


def per_harness_memory(measurements: dict[str, Any]) -> list[dict[str, Any]]:
    labels = ("baseline-memory", "candidate-memory-1", "candidate-memory-2")
    builds = measurement_builds(measurements)
    out = []
    solver_names = ("kissat", "cadical", "minisat", "z3", "cvc5", "boolector", "bitwuzla")
    for label in labels:
        m = builds.get(label, {})
        entry = next((x for x in SESSION.get("builds", []) if x["label"] == label), {})
        status_meta = read_json(EVIDENCE / f"{label}.status.json", {}) or m.get("build_metadata", {})
        rows = read_rows(label, m)
        by_name = {r["name"]: r for r in rows}
        records = process_records(label, m)
        direct_cbmc = {}
        cbmc_pid_harness = {}
        for r in records:
            if r.get("cmd") == "cbmc" and r.get("attribution") == "direct" and r.get("direct_harness"):
                name = r["direct_harness"]
                direct_cbmc.setdefault(name, []).append(r)
                if r.get("pid") is not None:
                    cbmc_pid_harness[str(r["pid"])] = name
        solver_by_harness: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for r in records:
            cmd = str(r.get("cmd", "")).lower()
            if not any(s in cmd for s in solver_names):
                continue
            # A solver record is harness-bound only through its exact CBMC parent PID.
            parent_harness = cbmc_pid_harness.get(str(r.get("ppid")))
            if parent_harness:
                solver_by_harness[parent_harness].append(r)
        names = set(by_name) | set(direct_cbmc) | set(solver_by_harness)
        for name in sorted(names):
            mem = direct_cbmc.get(name, [])
            solver = solver_by_harness.get(name, [])
            peak = max(mem, key=lambda x: x.get("peak_kb", -1), default=None)
            solver_peak = max(solver, key=lambda x: x.get("peak_kb", -1), default=None)
            meta = peak or solver_peak or {}
            row = by_name.get(name, {})
            out.append({"source_label": label, "source_sha": status_meta.get("source_sha", entry.get("sha", "NA")),
                        "build_id": status_meta.get("id", entry.get("build_id", "NA")),
                        "request_id": m.get("request_id", "NA"), "metadata_sha256": meta.get("metadata_sha256", "NA"),
                        "harness": name, "status": row.get("status", "NA"), "verification_time_s": row.get("time_s"),
                        "cbmc_direct_hwm_kb": peak.get("peak_kb") if peak else None,
                        "cbmc_peak_s": peak.get("peak_s") if peak else None,
                        "cbmc_metadata_sha256": peak.get("metadata_sha256", "NA") if peak else "NA",
                        "solver_name": solver_peak.get("cmd") if solver_peak else None,
                        "solver_direct_parent_hwm_kb": solver_peak.get("peak_kb") if solver_peak else None,
                        "solver_peak_s": solver_peak.get("peak_s") if solver_peak else None,
                        "attribution": "direct" if peak else ("solver-direct-parent" if solver_peak else "NA"),
                        "evidence": ",".join(sorted({r.get("evidence_file", f"{label}.process-*.txt") for r in mem + solver})) or f"{label}.process-*.txt (missing/no direct match)",
                        "result_evidence": row.get("evidence", f"{label}.*.rows.tsv (missing)")})
    return out


def memory_validation(measurements: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    builds = measurement_builds(measurements)
    for label in ("baseline-memory", "candidate-memory-1", "candidate-memory-2"):
        m = builds.get(label, {})
        rows = read_rows(label, m)
        records = read_memory(label, m)
        direct = [r for r in records if r.get("cmd") == "cbmc" and r.get("attribution") == "direct" and r.get("direct_harness")]
        all_cbmc = [r for r in records if r.get("cmd") == "cbmc"]
        unmatched = [r for r in all_cbmc if r not in direct]
        out.append({"label": label, "result_rows": len(rows), "unique_result_names": len({r.get("name") for r in rows}),
                    "direct_cbmc_pid_rows": len(direct), "unique_direct_harnesses": len({r.get("direct_harness") for r in direct}),
                    "unattributed_or_non_direct_cbmc_rows": len(unmatched),
                    "source_sha_values": sorted({str(r.get("source_sha", r.get("head_sha"))) for r in records if r.get("source_sha", r.get("head_sha"))}),
                    "build_id_values": sorted({str(r.get("build_id")) for r in records if r.get("build_id")}),
                    "metadata_sha256_values": sorted({str(r.get("metadata_sha256")) for r in direct if r.get("metadata_sha256")}),
                    "state": "AVAILABLE" if rows or records else "NOT_YET_AVAILABLE"})
    return out


def paired_domains(measurements: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    d = read_json(BASE / "paired-domain-map.json", {}) or {}
    builds = measurement_builds(measurements)
    def rows_for(label: str) -> list[dict[str, Any]]:
        m = builds.get(label, {})
        rows = [dict(r) for r in m.get("rows", [])]
        if not rows:
            rows = read_rows(label, None)
        b_id = m.get("build_id") or m.get("build_metadata", {}).get("id")
        b_sha = m.get("head_sha") or m.get("build_metadata", {}).get("source_sha")
        for r in rows:
            if b_id: r.setdefault("build_id", b_id)
            if b_sha: r.setdefault("source_sha", b_sha)
        return rows

    def series_ok(labels: tuple[str, ...], cutoff: int, expected: tuple[int, ...]) -> bool:
        for label, count in zip(labels, expected):
            b = builds.get(label)
            if not b:
                return False
            timeout = b.get("request", {}).get("harness_timeout_minutes")
            rows = rows_for(label)
            names = [r.get("name") for r in rows]
            if len(rows) != count or len(set(names)) != count or timeout is None or int(timeout) != cutoff:
                return False
            requested = [h.get("name") for h in b.get("request", {}).get("harnesses", []) if isinstance(h, dict)]
            if requested and set(requested) != set(names):
                return False
        return True

    five_labels = ("baseline-memory", "candidate-memory-1", "candidate-memory-2")
    five_ok = series_ok(five_labels, 5, (26, 30, 24))
    if five_ok:
        candidate_memory_names = [r.get("name") for label in five_labels[1:] for r in rows_for(label)]
        five_ok = len(candidate_memory_names) == len(set(candidate_memory_names))
    three_labels = ("baseline", "candidate")
    three_ok = series_ok(three_labels, 3, (22, 50))
    series, labels, cutoff = choose_pair_series(five_ok, three_ok)
    if series == "memory-5m":
        mapping = dict(d.get("old_domains", {}))
        mapping.update(d.get("additional_memory_calibration_domains", {}))
    elif series == "matched-3m":
        mapping = dict(d.get("old_domains", {}))
    else:
        series, labels, cutoff = "unavailable", (), None
        mapping = dict(d.get("old_domains", {}))

    selected = {label: rows_for(label) for label in labels}
    baseline_label = labels[0] if labels else None
    candidate_labels = labels[1:] if labels else ()
    baseline = builds.get(baseline_label, {}) if baseline_label else {}
    base_rows = selected.get(baseline_label, []) if baseline_label else []
    base_by_name = {r.get("name"): r for r in base_rows}
    cand_rows = [r for label in candidate_labels for r in selected[label]]
    cand_by_name: dict[str, dict[str, Any]] = {}
    for r in cand_rows:
        name = r.get("name", "")
        if name in cand_by_name:
            # Duplicate result identity makes this successor explicitly unresolved.
            cand_by_name[name] = {"name": name, "status": "DUPLICATE", "time_s": None}
        else:
            cand_by_name[name] = r
    full_map = []
    fam: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for old, successors in mapping.items():
        succ = [cand_by_name.get(n, {"name": n, "status": "MISSING", "time_s": None}) for n in successors]
        timed = [float(r["time_s"]) for r in succ if r.get("time_s") is not None]
        item = {"old_name": old, "family": old.removeprefix(PREFIX).split("::", 1)[0],
                "series": series, "cutoff_minutes": cutoff,
                "baseline": base_by_name.get(old, {"status": "MISSING", "time_s": None}),
                "baseline_build_id": baseline.get("build_id"), "baseline_source_sha": baseline.get("head_sha"),
                "successors": [{"name": r.get("name"), "status": r.get("status", "NA"),
                                "time_s": r.get("time_s"), "source_build_id": r.get("build_id")} for r in succ],
                "successor_count": len(successors), "candidate_observed_vt_sum_s": round(sum(timed), 6),
                "candidate_max_observed_vt_s": max(timed, default=None),
                "candidate_success_count": sum(r.get("status") == "SUCCESS" for r in succ),
                "candidate_censored_or_missing_count": sum(r.get("time_s") is None for r in succ),
                "candidate_source_ids": sorted({str(r.get("build_id")) for r in succ if r.get("build_id")}),
                "note": "Только сумма наблюдаемого Verification Time; цензурированные строки не восстанавливаются."}
        full_map.append(item)
        fam[item["family"]].append(item)
    family_rows = []
    for family, groups in sorted(fam.items()):
        all_times = [r["time_s"] for g in groups for r in g["successors"] if r.get("time_s") is not None]
        family_rows.append({"family": family, "old_domains": len(groups),
                            "successor_rows": sum(g["successor_count"] for g in groups),
                            "observed_vt_sum_s": round(sum(all_times), 6),
                            "max_observed_vt_s": max(all_times, default=None),
                            "censored_or_missing": sum(g["candidate_censored_or_missing_count"] for g in groups),
                            "source_ids": sorted({x for g in groups for x in g["candidate_source_ids"]})})
    # Store selection audit on return object metadata for explicit non-mixing evidence.
    series_inputs = []
    for label, expected_count, cutoff_value in [("baseline-memory", 26, 5), ("candidate-memory-1", 30, 5),
                                                 ("candidate-memory-2", 24, 5), ("baseline", 22, 3), ("candidate", 50, 3)]:
        part = builds.get(label, {})
        actual = len(rows_for(label)) if part else 0
        timeout = part.get("request", {}).get("harness_timeout_minutes")
        series_inputs.append({"label": label, "expected_rows": expected_count, "actual_rows": actual,
                              "requested_cutoff_minutes": timeout, "required_cutoff_minutes": cutoff_value,
                              "rows_and_cutoff_match": actual == expected_count and (timeout is None or int(timeout) == cutoff_value)})
    for item in full_map:
        item["series_status"] = {"five_minute_complete": five_ok, "three_minute_complete": three_ok,
                                 "selected_inputs": list(labels), "inputs_audit": series_inputs,
                                 "not_selected_5m": "missing/incomplete build or row export" if not five_ok else None}
    return full_map, family_rows


def control_audit(measurements: dict[str, Any]) -> list[dict[str, Any]]:
    results = []
    for entry in SESSION.get("builds", []):
        label = entry["label"]
        if "control" not in label.lower():
            continue
        measured = measurement_builds(measurements).get(label, {})
        summary = summary_fields(label)
        rows = read_rows(label, measured)
        for r in rows:
            covers = r.get("covers", "")
            match = re.fullmatch(r"\s*(\d+)\s*/\s*(\d+)\s*", str(covers))
            sat, total = (int(match.group(1)), int(match.group(2))) if match else (None, None)
            ok = r.get("status") == "SUCCESS" and total is not None and total > 0 and sat == total
            results.append({"label": label, "build_id": entry.get("build_id"), "harness": r.get("name"),
                            "status": r.get("status"), "covers": covers, "covers_audit_ok": ok,
                            "gate": summary.get("gate", measured.get("gate", "NA")),
                            "acceptance": False, "evidence": r.get("evidence")})
    return results


def covers_sample_passes(rows: list[dict[str, Any]], expected: list[str], complete: bool) -> bool:
    names = [r.get("harness") for r in rows]
    return (complete and bool(expected) and len(names) == len(expected)
            and len(set(names)) == len(names) and set(names) == set(expected)
            and all(r.get("covers_audit_ok") is True for r in rows))


def risk_items(measurements: dict[str, Any]) -> list[dict[str, Any]]:
    return list(measurements.get("ordinary_risk_register", []))


def risk_priority(row: dict[str, Any]) -> tuple[int, float]:
    status = str(row.get("status", "NA")).upper()
    flags = " ".join(map(str, row.get("flags", []))).upper()
    missing = status == "NO_RESULT_ROW" or "MISSING" in status or "MISSING" in flags or "DUPLICATE" in status
    non_success = status not in {"SUCCESS", "SUCCESSFUL"}
    cls = 0 if missing else (1 if non_success else 2)
    numeric = max((v for v in (row.get("mac_observed_tail_transfer_s"), row.get("mac_point_forecast_s"))
                   if isinstance(v, (int, float))), default=-1)
    return cls, -numeric


def fmt(value: Any, digits: int = 3) -> str:
    if value is None or value == "": return "NA"
    if isinstance(value, str) and value.strip().lower() in {"none", "null", "missing", "?"}: return "NA"
    if isinstance(value, float): return f"{value:.{digits}f}"
    if isinstance(value, dict): return "; ".join(f"{k}:{fmt(v)}" for k, v in sorted(value.items()))
    if isinstance(value, list): return ", ".join(fmt(v, digits) for v in value) or "NA"
    return str(value).replace("|", "\\|")


def render(measurements: dict[str, Any]) -> tuple[str, list[dict[str, Any]], dict[str, Any]]:
    mac_rows, mac = load_mac()
    builds = build_rows(measurements)
    cals = calibration(measurements, mac_rows)
    cal_groups = calibration_groups(cals)
    memory = per_harness_memory(measurements)
    paired, paired_families = paired_domains(measurements)
    controls = control_audit(measurements)
    risks = risk_items(measurements)
    mem_validation = memory_validation(measurements)
    full = next((b for b in builds if b["label"] == "autoharness"), None)
    p6 = {"source_identity": mac["source_identity"], "all_harmonics_count": mac["all_rows"],
          "all_harmonics_observed_vt_sum_s": mac["all_sum_s"], "smallsort_count": mac["smallsort_rows"],
          "smallsort_observed_vt_sum_s": mac["smallsort_sum_s"],
          "smallsort_share_of_all_observed_vt": mac["smallsort_sum_s"] / mac["all_sum_s"] if mac["all_sum_s"] else None,
          "task_mac_timeouts_600s": mac["smallsort_timeouts_600s"],
          "whole_job_wall_s": None, "peak_memory": None, "cost_usd": None,
          "timed_sum_includes_timeout_rows": False}
    c3c_full = {"kani_status": full.get("kani_status") if full else None,
                "gate": full.get("gate") if full else None,
                "cloud_wall_s": full.get("cloud_wall_s") if full else None,
                "observed_vt_rows": full.get("row_count") if full else None,
                "observed_vt_sum_s": full.get("observed_vt_sum_s") if full else None,
                "smallsort_rows": full.get("smallsort_row_count") if full else None,
                "smallsort_observed_vt_sum_s": full.get("smallsort_observed_vt_sum_s") if full else None,
                "peak_memory": full.get("sampled_total_rss_peak_kb") if full else None,
                "cost_usd": full.get("used_ledger_cost_usd") if full else None}
    full_job = {"p6_mac_ci_reference": p6, "c3c_autoharness": c3c_full,
                "c3c_request_budget_minutes": 270, "c3c_build_overhead_minutes": 30,
                "measured_full_job_improvement": None, "historical_ubuntu_shutdown_cause": None}
    full_cloud_wall = f"{fmt(full['cloud_wall_s'],1)}s" if full and full["cloud_wall_s"] is not None else "NA"
    pair_series = (paired[0].get("series") if paired else "unavailable")
    pair_cutoff = (paired[0].get("cutoff_minutes") if paired else None)
    pair_inputs_audit = paired[0].get("series_status", {}).get("inputs_audit", []) if paired else []
    pair_inputs_summary = "; ".join(f"{x['label']} {x['actual_rows']}/{x['expected_rows']} rows, cutoff {fmt(x['requested_cutoff_minutes'])}m" for x in pair_inputs_audit)
    measured_full = bool(measurement_builds(measurements).get("autoharness", {}).get("ordinary_inventory"))
    risk_available = measured_full or bool(risks)
    ranked_risks = sorted(risks, key=risk_priority)[:15]
    limitations = ["Нет полного baseline-autoharness запуска: нельзя утверждать измеренное улучшение полного задания или причину исторического завершения Ubuntu.",
                   "Три точных Ubuntu harnesses, активных при остановке, не определяются по предоставленному TSV; имена не угадываются.",
                   "Суммы VT P6 не являются wall time, памятью или стоимостью задания; бюджет текущего C3c build задаётся отдельно.",
                   "В Mac TSV нет RAM или wall-time; суммы включают только строки со временем, без трёх timeout по 600 секунд.",
                   "Время — Verification Time. Сумма split successors — наблюдаемая сумма VT, не wall time и не время одного harness.",
                   "Отдельные максимумы HWM по процессам не складываются как RAM; для общей нагрузки используйте одновременный RSS с временем измерения.",
                   "Censor bounds не являются точечными коэффициентами; перенос к изменённым моделям — прогноз, не приёмка."]
    if full is None or full.get("row_count") is None:
        limitations.append("Результаты полного C3c autoharness ещё не экспортированы.")
    if next((v for v in mem_validation if v["label"] == "candidate-memory-2"), {}).get("state") != "AVAILABLE":
        limitations.append("Результаты candidate-memory-2 ещё не экспортированы.")
    if pair_series != "memory-5m":
        limitations.append("Полная пятиминутная парная серия недоступна; показана цельная доступная трёхминутная серия либо NA.")
    control_entries = [e for e in SESSION.get("builds", []) if "control" in e["label"].lower()]
    sample_audit_passed = bool(control_entries) and all(
        covers_sample_passes([r for r in controls if r["label"] == e["label"]],
                             [h["name"] for h in measurement_builds(measurements).get(e["label"], {}).get("request", {}).get("harnesses", [])],
                             measurement_builds(measurements).get(e["label"], {}).get("summary_status") == "COMPLETE")
        for e in control_entries)
    metrics = {"schema": "c3c-report-tables-v1", "builds": builds, "mac": mac,
               "full_autoharness_vs_p6": full_job, "calibration_rows": cals,
               "calibration_groups": cal_groups, "per_harness_memory_rows": len(memory),
               "memory_validation": mem_validation,
               "pairing_series": {"selected": pair_series, "cutoff_minutes": pair_cutoff,
                                  "five_minute_series_complete": bool(paired and paired[0].get("series_status", {}).get("five_minute_complete")),
                                  "three_minute_series_complete": bool(paired and paired[0].get("series_status", {}).get("three_minute_complete")),
                                  "inputs_audit": paired[0].get("series_status", {}).get("inputs_audit", []) if paired else [],
                                  "mixed_cutoffs": False},
               "paired_domains": paired, "paired_domain_families": paired_families,
               "controls_audit": {"state": "NO_CONTROL_EXPORT" if not controls else "ROWS_AUDITED",
                                   "rows": controls, "sample_audit_passed": sample_audit_passed, "acceptance": False},
               "risk": {"available": risk_available, "count": len(risks) if risk_available else None,
                        "label": "AVAILABLE" if risk_available else "UNAVAILABLE", "top15": ranked_risks,
                        "source": "Реестр ordinary_risk_register в measurements.json; см. risk-register.tsv"},
               "limitations": limitations}
    if risks:
        metrics["risk"]["top15"] = ranked_risks
    md = ["# Таблицы bounded-результатов C3c", "",
          "Сформировано по bounded summary pages, exports строк, peaks/process summaries, metadata сессии и входным TSV времени. Полные verifier logs не читались; proof/build команды не запускались.", "",
          "## Сборки и время", "",
          "Стоимость — расчёт по Cloud wall при ставке `$0.0135/min`, если в derived measurements нет готового ledger value; резерв показан отдельно. `NA` означает, что bounded evidence отсутствует.", "",
          "| Запуск | Build ID | Source SHA | Статус Cloud | Статус Kani | Gate | Cloud wall, с | Kani wall | Расчётная стоимость, USD | Резерв, USD | Evidence |",
          "|---|---|---|---|---|---|---:|---|---:|---:|---|"]
    for b in builds:
        md.append("| " + " | ".join([
            f"[{fmt(b['label'])}](evidence/)", fmt(b["build_id"]), fmt(b["source_sha"]), fmt(b["cloud_status"]),
            fmt(b["kani_status"]), fmt(b["gate"]), fmt(b["cloud_wall_s"], 1), fmt(b["kani_command_wall"]),
            fmt(b["used_ledger_cost_usd"], 4), fmt(b["reserved_usd"], 4),
            "[папка evidence](evidence/)"]) + " |")
    md += ["", "## Память процессов", "",
           "HWM — независимый максимум каждого процесса; одновременные RSS максимумы измерены совместно и указаны со временем. Независимые HWM не складываются как общая RAM.", "",
           "| Запуск | HWM driver KiB @с | HWM CBMC KiB @с | HWM solver | Одновременный RSS CBMC KiB @с | Одновременный RSS driver KiB @с | Суммарный sampled RSS KiB @с | Источник |",
           "|---|---:|---:|---|---:|---:|---:|---|"]
    for b in builds:
        md.append("| " + " | ".join([
            fmt(b["label"]),
            fmt(f'{b["driver_hwm_kb"]}@{b["driver_hwm_peak_s"]}' if b["driver_hwm_kb"] is not None else None),
            fmt(f'{b["cbmc_hwm_kb"]}@{b["cbmc_hwm_peak_s"]}' if b["cbmc_hwm_kb"] is not None else None),
            fmt(b["solver_hwm"]),
            fmt(f'{b["cbmc_simultaneous_rss_kb"]}@{b["cbmc_simultaneous_rss_peak_s"]}' if b["cbmc_simultaneous_rss_kb"] is not None else None),
            fmt(f'{b["driver_simultaneous_rss_kb"]}@{b["driver_simultaneous_rss_peak_s"]}' if b["driver_simultaneous_rss_kb"] is not None else None),
            fmt(f'{b["sampled_total_rss_peak_kb"]}@{b["sampled_total_rss_peak_s"]}' if b["sampled_total_rss_peak_kb"] is not None else None),
            "[peaks/process summaries](evidence/)"]) + " |")
    p6_share = p6["smallsort_share_of_all_observed_vt"]
    p6_share_pct = fmt(p6_share * 100, 1) + "%" if p6_share is not None else "NA"
    md += ["", "## P6 Mac CI: известные VT и сравнение с C3c autoharness", "",
           "Сравнительные метрики P6 — предоставленные Verification Time counts/sums/share. Для P6 нет whole-job wall, RAM или стоимости. Три task-заданных Mac timeout по 600s показаны отдельно и не входят в TSV-суммы.", "",
           "| Запуск | Все гармоники: строки / VT, с | SmallSort: строки / VT, с | Доля SmallSort | Cloud wall | Пик памяти | Стоимость |",
           "|---|---:|---:|---:|---:|---:|---:|"]
    md.append(f"| P6 Mac TSV, run 40748125754 | {p6['all_harmonics_count']} / {p6['all_harmonics_observed_vt_sum_s']:.1f} | {p6['smallsort_count']} / {p6['smallsort_observed_vt_sum_s']:.1f} | {p6_share_pct} | NA | NA | NA |")
    md.append(f"| C3c autoharness | {fmt(full['row_count'] if full else None)} / {fmt(full['observed_vt_sum_s'] if full else None)} | {fmt(full['smallsort_row_count'] if full else None)} / {fmt(full['smallsort_observed_vt_sum_s'] if full else None)} | NA | {full_cloud_wall} | {fmt(full['sampled_total_rss_peak_kb'] if full else None)} KiB | {fmt(full['used_ledger_cost_usd'] if full else None)} USD |")
    md += ["", f"Mac timeout names: {fmt([n.removeprefix(PREFIX) for n in mac['smallsort_timeouts_600s']])}. C3c request limit is 270 min work plus 30 min build overhead; это бюджет текущего build, не метрика P6. Без полного baseline autoharness нельзя утверждать измеренное улучшение полного задания или причину исторического завершения Ubuntu.", "",
           "## Калибровка по типизированным группам моделей", "",
           "Отношение — Mac/GCB Verification Time. Точечная оценка требует timed Mac и успешного timed GCB. При Mac timeout 600s и GCB success приводится нижняя граница; при GCB timeout и Mac success — верхняя. Dual-censored наблюдение не задаёт конечную границу. Калибровка не является приёмкой.", "",
           "| Группа моделей | Точечных | Цензурированных | Медиана | P90 | Максимум точек | Нижние границы | Верхние границы | Дважды цензурировано | ID источников |",
           "|---|---:|---:|---:|---:|---:|---|---|---:|---|"]
    for g in cal_groups:
        md.append(f"| {fmt(g['group'])} | {g['n_point']} | {g['n_censored']} | {fmt(g['median'])} | {fmt(g['p90'])} | {fmt(g['max_point'])} | {fmt(g['lower_censor_bounds'])} | {fmt(g['upper_censor_bounds'])} | {g['n_dual_censored']} | {fmt(g['source_ids'])} |")
    md += ["", "## Память по отдельным harnesses", "",
           f"Подробности: [per-harness-memory.tsv](per-harness-memory.tsv), {len(memory)} строк. Проверка прямой атрибуции: " + "; ".join(f"{v['label']}: {v['result_rows']} rows / {v['unique_direct_harnesses']} однозначных CBMC harnesses ({v['state']})" for v in mem_validation) + ". Если прямой привязки нет, поле остаётся `NA`; active-set не связывает пик CBMC с отдельным harness. Solver HWM приписывается harness только через точный CBMC parent PID.", "",
           "## Старые домены и все successor-модели", "",
           f"Выбрана серия **{pair_series}**, cutoff **{fmt(pair_cutoff)} min**. Серии 3m и 5m не смешиваются. Пятиминутная серия полная: **{str(bool(paired and paired[0].get('series_status', {}).get('five_minute_complete'))).lower()}**; трёхминутная серия полная: **{str(bool(paired and paired[0].get('series_status', {}).get('three_minute_complete'))).lower()}**. Проверка inputs: {pair_inputs_summary}. Если серия 5m неполна, отсутствующие rows/pages/builds показаны как `NA`, а парное сравнение использует целиком 3m серию либо `NA`. Candidate суммы содержат только наблюдавшиеся VT; timeout/untimed successors остаются censored и считаются отдельно. Build IDs показаны как source IDs.", "",
           "| Семейство | Старых доменов | Строк successor | Наблюдаемая сумма VT, с | Максимум VT, с | Цензурировано/нет данных | ID источников |",
           "|---|---:|---:|---:|---:|---:|---|"]
    for g in paired_families:
        md.append(f"| {g['family']} | {g['old_domains']} | {g['successor_rows']} | {g['observed_vt_sum_s']:.3f} | {fmt(g['max_observed_vt_s'])} | {g['censored_or_missing']} | {fmt(g['source_ids'])} |")
    md += ["", "Полные per-domain/per-successor данные находятся в `report-metrics.json`.", "",
           "## Аудит controls", ""]
    if not controls:
        md.append("В этом наборе нет controls build/row export. Сам по себе gate=true не доказывает прохождение covers.")
    else:
        md += ["| Сборка | Harness | Статус | Covers satisfied/total | Gate | Аудит cover |", "|---|---|---|---:|---|---|"]
        for c in controls:
            md.append(f"| {c['label']} | {c['harness']} | {c['status']} | {fmt(c['covers'])} | {fmt(c['gate'])} | {'PASS' if c['covers_audit_ok'] else 'FAIL'} |")
        md.append(f"Выборочный covers-аудит: {'PASS' if sample_audit_passed else 'FAIL / INCOMPLETE'}. Полнота request names и COMPLETE summary проверены.")
        md.append("Строки controls проверяются на SUCCESS и covers `satisfied == total > 0`; это не автоматическая приёмка.")
    md += ["", "## Реестр риска ordinary inventory", "",
           f"Строк, привязанных к inventory: **{fmt(len(risks) if risk_available else None)}**; реестр **{'доступен' if risk_available else 'недоступен'}**. См. [risk-register.tsv](risk-register.tsv). Сначала идут TIMEOUT/FAILURE/пропущенные результаты, затем числовые прогнозы. Source-predicted inventory не считается завершённым remote inventory.", ""]
    if metrics["risk"]["top15"]:
        md += ["| Harness | Статус | GCB VT, с | Точечный прогноз Mac, с | Перенос наблюдённого хвоста, с | Флаги |", "|---|---|---:|---:|---:|---|"]
        for r in metrics["risk"]["top15"]:
            md.append(f"| {r.get('name')} | {fmt(r.get('status'))} | {fmt(r.get('gcb_time_s'))} | {fmt(r.get('mac_point_forecast_s'))} | {fmt(r.get('mac_observed_tail_transfer_s'))} | {fmt(r.get('flags'))} |")
    md += ["", "## Ограничения", ""]
    md.extend(f"- {x}" for x in metrics["limitations"])
    md += ["", f"Вход генератора: `measurements.json`, schema `{measurements.get('schema','NA')}`; session и bounded pages находятся в `evidence/`. Отсутствующие данные отмечаются `NA`, а не восстанавливаются догадками.", ""]
    return "\n".join(md), memory, metrics


def write_outputs() -> dict[str, Any]:
    measurements = read_json(MEASUREMENTS_PATH, {}) or {}
    markdown, memory, metrics = render(measurements)
    (BASE / "report-tables.md").write_text(markdown)
    fields = ["source_label", "source_sha", "build_id", "request_id", "metadata_sha256", "harness", "status",
              "verification_time_s", "cbmc_direct_hwm_kb", "cbmc_peak_s", "cbmc_metadata_sha256", "solver_name",
              "solver_direct_parent_hwm_kb", "solver_peak_s", "attribution", "evidence", "result_evidence"]
    headers = {"source_label": "запуск", "source_sha": "исходный_SHA", "build_id": "ID_сборки",
               "request_id": "ID_запроса", "metadata_sha256": "SHA256_metadata", "harness": "harness",
               "status": "status", "verification_time_s": "время_VT_с", "cbmc_direct_hwm_kb": "CBMC_HWM_KiB",
               "cbmc_peak_s": "время_пика_CBMC_с", "cbmc_metadata_sha256": "SHA256_CBMC_metadata",
               "solver_name": "solver", "solver_direct_parent_hwm_kb": "solver_HWM_KiB",
               "solver_peak_s": "время_пика_solver_с", "attribution": "атрибуция", "evidence": "источник_памяти",
               "result_evidence": "источник_результата"}
    with (BASE / "per-harness-memory.tsv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter="\t", lineterminator="\n", extrasaction="ignore")
        f.write("\t".join(headers[k] for k in fields) + "\n")
        for row in memory:
            w.writerow({k: "NA" if row.get(k) is None or row.get(k) == "" else row[k] for k in fields})
    (BASE / "report-metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False) + "\n")
    return metrics


class Fixtures(unittest.TestCase):
    def test_missing_metrics_are_not_invented(self) -> None:
        self.assertIsNone(parse_duration(None))
        self.assertIsNone(cloud_wall({}))
        self.assertEqual(read_rows("definitely-missing", None), [])

    def test_timeout_is_censored_not_cutoff_time(self) -> None:
        row = {"gcb_status": "TIMEOUT", "gcb_time_s": None, "mac_time_s": 450.0,
               "mac_censored_timeout_s": None, "ratio_upper_bound": 2.5}
        self.assertIsNone(row["gcb_time_s"])
        self.assertEqual(row["ratio_upper_bound"], 450.0 / 180.0)

    def test_censored_successor_excluded_from_observed_sum(self) -> None:
        successors = [{"time_s": 12.5, "status": "SUCCESS"}, {"time_s": None, "status": "TIMEOUT"}]
        self.assertEqual(sum(r["time_s"] for r in successors if r["time_s"] is not None), 12.5)
        self.assertEqual(sum(r["time_s"] is None for r in successors), 1)

    def test_pair_series_never_mixes_cutoffs(self) -> None:
        self.assertEqual(choose_pair_series(False, True), ("matched-3m", ("baseline", "candidate"), 3))
        self.assertEqual(choose_pair_series(True, True), ("memory-5m", ("baseline-memory", "candidate-memory-1", "candidate-memory-2"), 5))
        self.assertEqual(choose_pair_series(False, False), ("unavailable", (), None))

    def test_covers_audit_needs_complete_exact_request_not_only_gate(self) -> None:
        rows = [{"harness": "a", "covers_audit_ok": True}, {"harness": "b", "covers_audit_ok": True}]
        self.assertTrue(covers_sample_passes(rows, ["a", "b"], True))
        self.assertFalse(covers_sample_passes(rows[:1], ["a", "b"], True))
        self.assertFalse(covers_sample_passes(rows, ["a", "b"], False))
        self.assertFalse(covers_sample_passes(rows + rows[:1], ["a", "b"], True))
        self.assertFalse(covers_sample_passes([{"harness": "a", "covers_audit_ok": False}], ["a"], True))

    def test_risk_failures_and_missing_rows_precede_large_forecasts(self) -> None:
        missing = {"status": "NO_RESULT_ROW", "mac_point_forecast_s": 1}
        timeout = {"status": "TIMEOUT", "mac_point_forecast_s": 2}
        success = {"status": "SUCCESS", "mac_point_forecast_s": 1000}
        self.assertLess(risk_priority(missing), risk_priority(timeout))
        self.assertLess(risk_priority(timeout), risk_priority(success))


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        unittest.main(argv=[sys.argv[0]])
    else:
        m = write_outputs()
        print(json.dumps({"builds": len(m["builds"]), "memory_rows": m["per_harness_memory_rows"],
                          "calibration_groups": len(m["calibration_groups"]),
                          "paired_domains": len(m["paired_domains"]), "risks": m["risk"]["count"]}, indent=2))
