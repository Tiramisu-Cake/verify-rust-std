#!/usr/bin/env python3
"""macOS copy of the organizers' kani_autoharness job: command extraction and a SmallSort summary.

`extract` writes the literal `Run Kani Verification` body of kani.yml (via the pinned kani_k1 extractor).
`summarize` parses the terse log with the pinned per-thread kani_k1.parse_log plus an independent per-worker
event scan, and reports three separate results:
  evidence_integrity - the log is complete and every event binds to exactly one harness block; the SmallSort
                       rows equal the expected name list; the footer and the exit code agree with the rows;
  job_success        - integrity, exit 0 and no failing harness anywhere (the organizers' job would be green);
  groups             - the coordinator's admission policy per candidate group (all members SUCCESS, no failed
                       check, exactly the source-derived covers satisfied, VT <= threshold). Without integrity
                       every group is BLOCKED; a group is admitted or demoted only as a whole.
The exit status is 3 when integrity fails, else 0 (the job's own outcome is the verification step's).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kani_k1  # noqa: E402  (pinned K-1 parser; not modified here)

PARSER_VERSION = "mac-autoharness-3"
RESULT_RES = (kani_k1.STATUS_RE, kani_k1.TIME_RE, kani_k1.CHECKS_RE, kani_k1.COVER_RE, kani_k1.FAILED_CHECK_RE,
              kani_k1.TIMEOUT_RE, kani_k1.OOM_RE)
GROUP_LINE_RE = re.compile(r"^([a-z0-9]+) (\d+|\*) (\S+)$")


def _sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _lines(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text().splitlines() if line.strip() and not line.startswith("#")]


def load_candidates(path: Path, sizes: dict[str, int], expected: set[str]) -> dict[str, dict[str, Any]]:
    """`<group> <expected covers or *> <full harness name>` per line; validated before any run."""
    groups: dict[str, dict[str, Any]] = {}
    seen: set[str] = set()
    for line in _lines(path):
        m = GROUP_LINE_RE.match(line)
        if not m:
            raise ValueError(f"candidate line must be '<group> <covers|*> <name>': {line!r}")
        group, covers, name = m.groups()
        if group not in sizes:
            raise ValueError(f"unknown candidate group {group!r}")
        if name in seen:
            raise ValueError(f"candidate listed twice: {name}")
        if name not in expected:
            raise ValueError(f"candidate not in the expected list: {name}")
        seen.add(name)
        groups.setdefault(group, {})[name] = None if covers == "*" else int(covers)
    for group, size in sizes.items():
        if len(groups.get(group, {})) != size:
            raise ValueError(f"group {group} must have exactly {size} members, has {len(groups.get(group, {}))}")
    return groups


def scan_events(text: str) -> dict[str, int]:
    """Independent per-worker scan: result events outside a block, starts over an open block, unclosed blocks,
    and repeated result records inside one block.

    A block is open from its start to its Verification Time. After a timeout/OOM marker (or a TIMEOUT status) it is
    terminal: one trailing status and the time line still belong to it, and the worker's next start is not an
    overlap. Any other second status, checks or cover record in one block is a contradiction.
    """
    state: dict[str | None, str] = {}   # worker -> "open" | "terminal" | "closed"
    counts: dict[str | None, dict[str, int]] = {}
    orphans = overlaps = repeated = 0
    for raw in text.splitlines():
        line = raw.rstrip("\r")
        worker = None
        m = kani_k1.THREAD_RE.match(line)
        if m:
            worker, line = m.group(1), m.group(2)
        if kani_k1.CHECKING_RE.match(line):
            overlaps += state.get(worker) == "open"
            state[worker] = "open"
            counts[worker] = {"status": 0, "checks": 0, "covers": 0, "time": 0}
            continue
        if not any(r.match(line) for r in RESULT_RES):
            continue
        current = state.get(worker, "closed")
        if current == "closed":
            orphans += 1
            continue
        c = counts[worker]
        status = kani_k1.STATUS_RE.match(line)
        for key, rx in (("status", kani_k1.STATUS_RE), ("checks", kani_k1.CHECKS_RE), ("covers", kani_k1.COVER_RE),
                        ("time", kani_k1.TIME_RE)):
            if rx.match(line):
                c[key] += 1
                limit = 2 if key == "status" and current == "terminal" else 1
                repeated += c[key] > limit
        if kani_k1.TIME_RE.match(line):
            state[worker] = "closed"
        elif kani_k1.TIMEOUT_RE.match(line) or kani_k1.OOM_RE.match(line) or (status and status.group(1) == "TIMEOUT"):
            state[worker] = "terminal"
    return {"orphans": orphans, "overlaps": overlaps, "repeated": repeated,
            "unclosed": sum(v == "open" for v in state.values())}


def _row(block: dict[str, Any]) -> dict[str, Any]:
    return {"status": kani_k1._block_status(block), "time_s": block["time_s"],
            "checks_failed": block["checks_failed"], "checks_total": block["checks_total"],
            "unreachable": block["unreachable"], "covers_satisfied": block["covers_satisfied"],
            "covers_total": block["covers_total"], "failed_checks": block["failed_checks"]}


def _row_anomaly(row: dict[str, Any]) -> str | None:
    if row["status"] == "SUCCESS" and row["checks_failed"] not in (0, None):
        return "success_with_failed_checks"
    if row["status"] == "FAILED" and row["checks_failed"] == 0:
        return "failed_without_failed_checks"
    t = row["time_s"]
    if t is not None and (not math.isfinite(t) or t < 0):
        return "bad_time"
    if row["status"] == "UNKNOWN":
        return "unknown_status"
    return None


def _admit(row: dict[str, Any] | None, covers: int | None, threshold: float) -> tuple[str, str]:
    """Returns (class, reason); class is ok, slow, resource, correctness or evidence."""
    if row is None:
        return "evidence", "MISSING"
    if row["status"] == "FAILED":
        return "correctness", "FAILED"
    if row["status"] in ("TIMEOUT", "OUT_OF_MEMORY"):
        return "resource", row["status"]
    if row["status"] != "SUCCESS":
        return "evidence", row["status"]
    if row["checks_failed"] != 0:
        return "evidence", "checks_failed_not_zero"
    if row["covers_total"] is None or row["covers_satisfied"] is None:
        return "evidence", "covers_missing"
    if covers is not None and row["covers_total"] != covers:
        return "evidence", f"covers_total_{row['covers_total']}_expected_{covers}"
    if row["covers_satisfied"] != row["covers_total"] or row["covers_total"] == 0:
        return "evidence", "covers_not_all_satisfied"
    if row["time_s"] is None:
        return "evidence", "time_missing"
    if row["time_s"] > threshold:
        return "slow", "over_threshold"
    return "ok", "ok"


def summarize(log: Path, expected_path: Path, candidates: Path, sizes: dict[str, int], threshold: float,
              exit_code: str, identities: dict[str, str]) -> dict[str, Any]:
    if not (math.isfinite(threshold) and threshold > 0):
        raise ValueError("threshold must be a positive finite number")
    want = _lines(expected_path)
    if len(set(want)) != len(want):
        raise ValueError("expected list has duplicate names")
    want_set = set(want)
    groups_in = load_candidates(candidates, sizes, want_set)
    text = log.read_text(errors="replace") if log.is_file() else ""
    parsed = kani_k1.parse_log(text)
    events = scan_events(text)
    seen: dict[str, list[dict[str, Any]]] = {}
    other_bad: list[str] = []
    statuses_all: dict[str, int] = {}
    anomalies: list[str] = []
    for block in parsed["blocks"]:
        row = _row(block)
        statuses_all[row["status"]] = statuses_all.get(row["status"], 0) + 1
        anomaly = _row_anomaly(row)
        if anomaly:
            anomalies.append(f"{block['name']} {anomaly}")
        if block["name"].startswith(kani_k1.HARNESS_PREFIX):
            seen.setdefault(block["name"], []).append(block)
        elif row["status"] != "SUCCESS" and len(other_bad) < 50:
            other_bad.append(f"{block['name']} {row['status']}")
    missing = sorted(want_set - set(seen))
    extra = sorted(set(seen) - want_set)
    duplicate = sorted(n for n, b in seen.items() if len(b) > 1)
    rows = {n: _row(b[0]) for n, b in seen.items() if len(b) == 1 and n in want_set}
    complete = parsed["complete_line"]
    n_blocks = len(parsed["blocks"])
    n_success = statuses_all.get("SUCCESS", 0)
    problems: list[str] = []
    if not log.is_file():
        problems.append("log_missing")
    if complete is None:
        problems.append("complete_line_missing")
    elif (complete["total"], complete["success"], complete["failures"]) != (n_blocks, n_success, n_blocks - n_success):
        problems.append(f"footer_mismatch footer={complete} blocks={n_blocks} success={n_success}")
    if parsed["errors"]:
        problems.append("compiler_or_driver_errors")
    if parsed["overlaps"] or parsed["orphans"] or any(events.values()):
        problems.append(f"event_binding parse_overlaps={parsed['overlaps']} parse_orphans={parsed['orphans']} "
                        f"scan={events}")
    if missing or extra or duplicate:
        problems.append("smallsort_set_not_exact")
    if anomalies:
        problems.append("row_anomalies")
    if not re.fullmatch(r"[0-9]{1,3}", exit_code):
        problems.append(f"exit_code_invalid_{exit_code[:20]}")
    elif int(exit_code) > 128:
        problems.append(f"exit_by_signal_{exit_code}")
    elif exit_code != "0" and (complete is None or complete["failures"] == 0):
        problems.append(f"nonzero_exit_{exit_code}_unexplained")
    if exit_code == "0" and complete is not None and complete["failures"] > 0:
        problems.append("zero_exit_with_failures")
    integrity = not problems
    # A failed check or an OOM anywhere outside the candidates needs a manual look before any automatic admission.
    candidate_names = {n for members in groups_in.values() for n in members}
    review_reasons = sorted(f"{b['name']} {kani_k1._block_status(b)}" for b in parsed["blocks"]
                            if b["name"] not in candidate_names
                            and kani_k1._block_status(b) in ("FAILED", "OUT_OF_MEMORY"))[:50]
    manual_review_required = bool(review_reasons)
    job_success = integrity and exit_code == "0" and complete is not None and complete["failures"] == 0
    decisions: dict[str, Any] = {}
    for group, members in groups_in.items():
        verdicts = {n: _admit(rows.get(n), c, threshold) for n, c in members.items()}
        classes = {c for c, _ in verdicts.values()}
        if not integrity:
            decision = "BLOCKED"
        elif classes == {"ok"}:
            decision = "ADMIT_PENDING_REVIEW" if manual_review_required else "ADMIT"
        elif "correctness" in classes:
            decision = "CORRECTNESS_FAILURE"
        elif "evidence" in classes:
            decision = "BLOCKED"
        else:
            decision = "DEMOTE"
        decisions[group] = {"decision": decision,
                            "members": {n: {"class": c, "reason": r, "expected_covers": members[n]}
                                        for n, (c, r) in verdicts.items()}}
    return {
        "parser_version": PARSER_VERSION, "identities": identities,
        "log_sha256": _sha256(log), "log_present": log.is_file(), "exit_code": exit_code,
        "complete_line": complete, "blocks_total": n_blocks, "statuses_all": statuses_all,
        "evidence_integrity": integrity, "integrity_problems": problems, "job_success": job_success,
        "manual_review_required": manual_review_required, "manual_review_reasons": review_reasons,
        "errors": parsed["errors"][:20], "anomalies": anomalies[:50],
        "smallsort": {"expected": len(want), "rows": len(rows),
                      "success": sum(1 for r in rows.values() if r["status"] == "SUCCESS"),
                      "missing": missing, "extra": extra, "duplicate": duplicate},
        "other_non_success_first50": other_bad, "threshold_s": threshold, "groups": decisions, "rows": rows,
    }


def markdown(s: dict[str, Any]) -> str:
    ss = s["smallsort"]
    out = [f"# macOS autoharness summary ({s['parser_version']})", "",
           f"**evidence_integrity {s['evidence_integrity']}**, job_success {s['job_success']}; "
           f"problems {s['integrity_problems']}", "",
           f"manual_review_required {s['manual_review_required']}: {s['manual_review_reasons']}", "",
           f"exit `{s['exit_code']}`; Complete `{s['complete_line']}`; blocks {s['blocks_total']} "
           f"{s['statuses_all']}; log sha256 `{s['log_sha256']}`", "",
           f"SmallSort: expected {ss['expected']}, rows {ss['rows']}, SUCCESS {ss['success']}; missing "
           f"{len(ss['missing'])}, extra {len(ss['extra'])}, duplicate {len(ss['duplicate'])}", "",
           f"Other std non-SUCCESS (first 50): {s['other_non_success_first50']}", "",
           f"## Candidate groups (threshold {s['threshold_s']} s)", ""]
    for group, d in s["groups"].items():
        out.append(f"- **{group}**: {d['decision']} — " + ", ".join(
            f"{n.rsplit('::', 1)[-1]}={m['reason']} ({(s['rows'].get(n) or {}).get('time_s')} s)"
            for n, m in d["members"].items()))
    out += ["", "## Top 25 SmallSort VT (no VT first)", "",
            "| harness | status | VT s | checks | unreachable | covers |", "|---|---|---:|---|---:|---|"]
    ranked = sorted(s["rows"].items(), key=lambda kv: (kv[1]["time_s"] is not None, -(kv[1]["time_s"] or 0.0)))
    for name, r in ranked[:25]:
        out.append(f"| {name.removeprefix(kani_k1.HARNESS_PREFIX)} | {r['status']} | {r['time_s']} | "
                   f"{r['checks_failed']}/{r['checks_total']} | {r['unreachable']} | "
                   f"{r['covers_satisfied']}/{r['covers_total']} |")
    return "\n".join(out) + "\n"


def _sizes(items: list[str]) -> dict[str, int]:
    sizes = {}
    for item in items:
        name, _, count = item.partition("=")
        sizes[name] = int(count)
    if not sizes:
        raise ValueError("at least one --group NAME=SIZE is required")
    return sizes


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="mac_autoharness")
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("extract")
    e.add_argument("--workflow", required=True)
    e.add_argument("--out", required=True)
    c = sub.add_parser("check-inputs")
    c.add_argument("--expected", required=True)
    c.add_argument("--expected-count", type=int, required=True)
    c.add_argument("--candidates", required=True)
    c.add_argument("--group", action="append", default=[], metavar="NAME=SIZE")
    s = sub.add_parser("summarize")
    s.add_argument("--log", required=True)
    s.add_argument("--expected", required=True)
    s.add_argument("--candidates", required=True)
    s.add_argument("--group", action="append", default=[], metavar="NAME=SIZE")
    s.add_argument("--threshold", type=float, default=300.0)
    s.add_argument("--exit-code", required=True)
    s.add_argument("--identities", help="KEY=VALUE lines recorded in the summary")
    s.add_argument("--out-dir", required=True)
    a = ap.parse_args(argv)
    if a.cmd == "extract":
        body = kani_k1.extract_autoharness_command(Path(a.workflow).read_text())
        Path(a.out).write_text(body)
        print(hashlib.sha256(body.encode()).hexdigest())
        return 0
    if a.cmd == "check-inputs":
        want = _lines(Path(a.expected))
        if len(want) != a.expected_count or len(set(want)) != len(want):
            print(f"expected list: {len(want)} names ({len(set(want))} unique), need {a.expected_count}")
            return 2
        load_candidates(Path(a.candidates), _sizes(a.group), set(want))
        print("inputs ok")
        return 0
    ids: dict[str, str] = {}
    if a.identities and Path(a.identities).is_file():
        for line in Path(a.identities).read_text().splitlines():
            key, sep, value = line.partition("=")
            if sep:
                ids.setdefault(key.strip(), value.strip())
    summary = summarize(Path(a.log), Path(a.expected), Path(a.candidates), _sizes(a.group), a.threshold,
                        a.exit_code, ids)
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(json.dumps(summary, indent=1, sort_keys=True) + "\n")
    (out / "summary.md").write_text(markdown(summary))
    return 0 if summary["evidence_integrity"] else 3


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
