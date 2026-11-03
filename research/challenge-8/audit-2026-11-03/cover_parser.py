#!/usr/bin/env python3
"""Cover/result parser PROTOTYPE for SmallSort Kani terse logs (audit-2026-11-03).

Prototype only: not integrated into any CI workflow, never runs Kani, and establishes no
historical cover acceptance. Python standard library only.

Input
  * one or more Kani `--output-format=terse` logs (one per job/partition);
  * an explicit JSON manifest of the expected harness set, per-harness expectations and covers;
  * the verifier's own exit status (`--verifier-exit`), and optionally observed source/tool identities.

Output: a JSON report (stdout) and a verdict:
  PASS        every expectation met, nothing missing, unknown, malformed or conflicting;
  FAIL        a definite violation (wrong status, unreached required cover, identity mismatch,
              count mismatch, verifier failure, ...);
  INCOMPLETE  something needed for PASS is missing or UNKNOWN (no result, no cover record,
              unknown cover total, truncated log, missing identity, ...);
  INPUT_ERROR the manifest itself is invalid.

Exit status: if the verifier exit is non-zero it is returned unchanged (the parser never masks a
verifier failure); otherwise 0 = PASS, 10 = FAIL, 11 = INCOMPLETE, 12 = INPUT_ERROR.

Terse record format assumed (the format read by the K-1 lane parser; see COVER-PARSER.md):
    [Thread <w>: ]Checking harness <name>...
    [Thread <w>: ]VERIFICATION:- SUCCESSFUL|FAILED|TIMEOUT
    [Thread <w>: ] ** <f> of <t> failed[ (<u> unreachable)]
    [Thread <w>: ] ** <s> of <n> cover properties satisfied
    [Thread <w>: ]Failed Checks: <description>
    [Thread <w>: ]Verification Time: <x>s
    [Thread <w>: ]CBMC timed out ... | CBMC appears to have run out of memory ...
    Verification failed for - <name>
    Complete - <s> successfully verified harnesses, <f> failures, <t> total.
Every event is attributed to (log, worker) -> that worker's open harness; never to the last
`Checking harness` line of another worker.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from typing import Any

MANIFEST_FORMAT = "smallsort-cover-manifest/0"
DEFAULT_NAMESPACE = "slice::sort::shared::smallsort::verify::"
IDENTITY_KEYS = ("source_commit", "library_tree", "kani_commit", "toolchain")
EXIT = {"PASS": 0, "FAIL": 10, "INCOMPLETE": 11, "INPUT_ERROR": 12}
RANK = {"PASS": 0, "INCOMPLETE": 1, "FAIL": 2, "INPUT_ERROR": 3}

THREAD = re.compile(r"^Thread (\d+): ?(.*)$")
CHECKING = re.compile(r"^Checking harness (\S+?)\.\.\.\s*$")
STATUS = re.compile(r"^VERIFICATION:-\s*(\S+)(.*)$")
CHECKS = re.compile(r"^\s*\*\*\s*(\S+) of (\S+) failed(.*)$")
COVERS = re.compile(r"^\s*\*\*\s*(\S+) of (\S+) cover propert(?:y|ies) satisfied\s*$")
FAILED_CHECK = re.compile(r"^Failed Checks:\s*(.*)$")
VTIME = re.compile(r"^Verification Time:\s*(\S+?)s\s*$")
TIMEOUT = re.compile(r"^CBMC timed out\b")
OOM = re.compile(r"^CBMC appears to have run out of memory\b")
FAILED_FOR = re.compile(r"^Verification failed for - (\S+)\s*$")
COMPLETE = re.compile(r"^Complete - (\S+) successfully verified harness(?:es)?, (\S+) failures?, (\S+) total\.\s*$")
ERROR_LINE = re.compile(r"^error(\[E\d{4}\])?:")
NUM = re.compile(r"^(0|[1-9][0-9]*)$")
RESULT_LINES = (STATUS, CHECKS, COVERS, FAILED_CHECK, VTIME, TIMEOUT, OOM)


def _int(s: str) -> int | None:
    return int(s) if NUM.match(s) else None


# --------------------------------------------------------------------------- terse adapter

def parse_terse(text: str, log_id: str) -> dict[str, Any]:
    """Split one terse log into per-harness records keyed by (log, worker)."""
    records: list[dict[str, Any]] = []
    open_by_worker: dict[str | None, dict[str, Any]] = {}
    # A record closed by a timeout/OOM marker may still receive its own trailing status/time line.
    capped_by_worker: dict[str | None, dict[str, Any]] = {}
    problems: list[str] = []
    failed_for: list[str] = []
    complete: dict[str, Any] | None = None
    error_lines = 0
    lines = text.splitlines()
    for no, raw in enumerate(lines, 1):
        line = raw.rstrip("\r")
        worker = None
        m = THREAD.match(line)
        if m:
            worker, line = m.group(1), m.group(2)
        where = f"{log_id}:{no}"
        m = CHECKING.match(line)
        if m:
            prev = open_by_worker.get(worker)
            if prev is not None:
                prev["closed"] = False
                problems.append(f"{where}: worker {worker} starts {m.group(1)} before {prev['name']} ended")
            rec = {"name": m.group(1), "log": log_id, "worker": worker, "line": no, "status_line": None,
                   "checks": None, "covers": None, "failed_checks": [], "time_s": None, "timeout": False,
                   "oom": False, "closed": None, "malformed": []}
            records.append(rec)
            open_by_worker[worker] = rec
            capped_by_worker.pop(worker, None)
            continue
        if ERROR_LINE.match(line):
            error_lines += 1
        m = FAILED_FOR.match(line)
        if m and worker is None:
            failed_for.append(m.group(1))
            continue
        m = COMPLETE.match(line)
        if m and worker is None:
            vals = [_int(g) for g in m.groups()]
            if complete is not None:
                problems.append(f"{where}: second 'Complete' line")
            if None in vals or vals[0] + vals[1] != vals[2]:
                problems.append(f"{where}: malformed 'Complete' counts {m.groups()}")
                complete = {"malformed": True}
            else:
                complete = {"success": vals[0], "failures": vals[1], "total": vals[2]}
            for w, rec in open_by_worker.items():
                if rec is not None and rec["closed"] is None:
                    rec["closed"] = False
                    problems.append(f"{where}: {rec['name']} (worker {w}) still open at 'Complete'")
            open_by_worker.clear()
            continue
        if not any(r.match(line) for r in RESULT_LINES):
            continue
        rec = open_by_worker.get(worker)
        if rec is None and worker in capped_by_worker and (STATUS.match(line) or VTIME.match(line)):
            rec = capped_by_worker[worker]
            if (m := STATUS.match(line)) and rec["status_line"] is None:
                rec["status_line"] = m.group(1)
            elif (m := VTIME.match(line)) and rec["time_s"] is None:
                rec["time_s"] = float(m.group(1)) if re.match(r"^[0-9]+(\.[0-9]+)?$", m.group(1)) else None
            else:
                rec["malformed"].append("repeated trailing line after resource cap")
            continue
        if rec is None:
            # A result line that cannot be bound to an open harness of the same worker.
            problems.append(f"{where}: result line without an open harness on worker {worker}: {line.strip()[:80]}")
            continue
        if (m := STATUS.match(line)):
            if rec["status_line"] is not None:
                rec["malformed"].append("second VERIFICATION line")
            rec["status_line"] = m.group(1)
        elif (m := CHECKS.match(line)):
            f, t = _int(m.group(1)), _int(m.group(2))
            if f is None or t is None or f > t or rec["checks"] is not None:
                rec["malformed"].append(f"check counts {m.group(1)}/{m.group(2)}")
            else:
                rec["checks"] = (f, t)
        elif (m := COVERS.match(line)):
            s, n = _int(m.group(1)), _int(m.group(2))
            if s is None or n is None or s > n or rec["covers"] is not None:
                rec["malformed"].append(f"cover counts {m.group(1)}/{m.group(2)}")
            else:
                rec["covers"] = (s, n)
        elif (m := FAILED_CHECK.match(line)):
            rec["failed_checks"].append(m.group(1).strip())
        elif TIMEOUT.match(line):
            rec["timeout"] = True
            rec["closed"] = True
            open_by_worker[worker] = None
            capped_by_worker[worker] = rec
        elif OOM.match(line):
            rec["oom"] = True
            rec["closed"] = True
            open_by_worker[worker] = None
            capped_by_worker[worker] = rec
        elif (m := VTIME.match(line)):
            try:
                rec["time_s"] = float(m.group(1))
            except ValueError:
                rec["malformed"].append(f"verification time {m.group(1)}")
            rec["closed"] = True
            open_by_worker[worker] = None
    for w, rec in open_by_worker.items():
        if rec is not None and rec["closed"] is None:
            rec["closed"] = False
            problems.append(f"{log_id}: {rec['name']} (worker {w}) not closed at end of log (truncated?)")
    if complete is None:
        problems.append(f"{log_id}: no 'Complete - ...' line (truncated or aborted log)")
    return {"log": log_id, "records": records, "problems": problems, "failed_for": failed_for,
            "complete": complete, "error_lines": error_lines}


def record_status(rec: dict[str, Any]) -> str:
    if rec["malformed"]:
        return "MALFORMED"
    if rec["oom"]:
        return "OUT_OF_MEMORY"
    if rec["timeout"] or rec["status_line"] == "TIMEOUT":
        return "TIMEOUT"
    if rec["closed"] is not True:
        return "PARTIAL"
    if rec["status_line"] == "SUCCESSFUL":
        return "SUCCESS"
    if rec["status_line"] == "FAILED":
        return "FAILED"
    return "UNKNOWN"


# --------------------------------------------------------------------------- manifest

def load_manifest(data: Any) -> tuple[dict[str, Any] | None, list[str]]:
    errs: list[str] = []
    if not isinstance(data, dict) or data.get("format") != MANIFEST_FORMAT:
        return None, [f"manifest: format must be {MANIFEST_FORMAT!r}"]
    suite = data.get("suite")
    if suite not in ("ordinary", "controls"):
        errs.append("manifest: suite must be 'ordinary' or 'controls'")
    ns = data.get("namespace", DEFAULT_NAMESPACE)
    if not isinstance(ns, str) or not ns.endswith("::"):
        errs.append("manifest: namespace must end with '::'")
    policy = data.get("cover_policy", {})
    if not isinstance(policy, dict) or not isinstance(policy.get("explicit_zero_allowed", False), bool):
        errs.append("manifest: cover_policy.explicit_zero_allowed must be a boolean")
        policy = {}
    zero_ok = policy.get("explicit_zero_allowed", False)
    ident = data.get("identity", {})
    if not isinstance(ident, dict) or any(k not in IDENTITY_KEYS or not isinstance(v, str) or not v
                                          for k, v in ident.items()):
        errs.append(f"manifest: identity keys must be among {IDENTITY_KEYS} with non-empty string values")
        ident = {}
    exp_exit = data.get("expected_verifier_exit", 0 if suite == "ordinary" else None)
    if suite == "ordinary" and exp_exit != 0:
        errs.append("manifest: an ordinary suite requires expected_verifier_exit 0")
    if suite == "controls" and not isinstance(exp_exit, int):
        errs.append("manifest: a controls suite must state expected_verifier_exit explicitly")
    hs = data.get("harnesses")
    if not isinstance(hs, list) or not hs:
        return None, errs + ["manifest: harnesses must be a non-empty list"]
    if "expected_count" in data and data["expected_count"] != len(hs):
        errs.append(f"manifest: expected_count {data['expected_count']} != {len(hs)} harness entries")
    names = Counter(h.get("name") if isinstance(h, dict) else None for h in hs)
    for n, c in names.items():
        if c > 1:
            errs.append(f"manifest: duplicate harness {n}")
    out = []
    for h in hs:
        if not isinstance(h, dict) or not isinstance(h.get("name"), str) or not h["name"].startswith(ns):
            errs.append(f"manifest: harness entry without a name in namespace {ns}: {h!r}"[:200])
            continue
        n = h["name"]
        exp = h.get("expect")
        if exp not in ("SUCCESS", "FAILED"):
            errs.append(f"manifest: {n}: expect must be SUCCESS or FAILED")
        if exp == "FAILED":
            if suite == "ordinary":
                errs.append(f"manifest: {n}: expected-FAILED (negative) row in the ordinary set")
            if not isinstance(h.get("expect_check"), str) or not h["expect_check"]:
                errs.append(f"manifest: {n}: an expected failure needs expect_check")
        total = h.get("covers_total", "UNKNOWN")
        if total != "UNKNOWN" and not (isinstance(total, int) and not isinstance(total, bool) and total >= 0):
            errs.append(f"manifest: {n}: covers_total must be a non-negative integer or 'UNKNOWN'")
        if total == 0 and not zero_ok:
            errs.append(f"manifest: {n}: covers_total 0 is not allowed by cover_policy")
        covers = h.get("covers", [])
        if not isinstance(covers, list) or any(not isinstance(c, dict) or c.get("kind") not in ("route", "panic", "other")
                                               or not isinstance(c.get("label"), str) for c in covers):
            errs.append(f"manifest: {n}: covers must be a list of {{label, kind: route|panic|other}}")
            covers = []
        if isinstance(total, int) and covers and len(covers) != total:
            errs.append(f"manifest: {n}: {len(covers)} listed covers != covers_total {total}")
        panic_cut = h.get("panic_cut", False)
        if not isinstance(panic_cut, bool):
            errs.append(f"manifest: {n}: panic_cut must be a boolean")
        if panic_cut and exp == "SUCCESS" and not any(c.get("kind") == "route" for c in covers):
            errs.append(f"manifest: {n}: panic-cut root needs a normal-return/route witness cover, "
                        "not only panic covers")
        out.append({"name": n, "expect": exp, "expect_check": h.get("expect_check"), "covers_total": total,
                    "covers": covers, "panic_cut": panic_cut})
    m = {"suite": suite, "namespace": ns, "identity": ident, "expected_verifier_exit": exp_exit,
         "harnesses": out}
    return (None if errs else m), errs


# --------------------------------------------------------------------------- evaluation

def evaluate(manifest: dict[str, Any], logs: list[dict[str, Any]], verifier_exit: int | None,
             observed_identity: dict[str, str]) -> dict[str, Any]:
    fail: list[str] = []
    incomplete: list[str] = []
    ns = manifest["namespace"]
    expected = {h["name"]: h for h in manifest["harnesses"]}

    # verifier exit is never overridden by parser success
    if verifier_exit is None:
        incomplete.append("verifier exit status not given (UNKNOWN)")
    elif verifier_exit != manifest["expected_verifier_exit"]:
        fail.append(f"verifier exit {verifier_exit} != expected {manifest['expected_verifier_exit']}")

    # identities
    for k, want in manifest["identity"].items():
        got = observed_identity.get(k)
        if got is None:
            incomplete.append(f"identity {k}: not observed (UNKNOWN)")
        elif got != want:
            fail.append(f"identity {k}: observed {got} != expected {want}")

    # log-level integrity
    by_name: dict[str, list[dict[str, Any]]] = {}
    other_ns: Counter = Counter()
    for lg in logs:
        for p in lg["problems"]:
            incomplete.append(p)
        if lg["error_lines"]:
            incomplete.append(f"{lg['log']}: {lg['error_lines']} error line(s) from compiler/driver")
        recs = lg["records"]
        c = lg["complete"]
        if c and not c.get("malformed"):
            succ = sum(1 for r in recs if record_status(r) == "SUCCESS")
            if c["total"] != len(recs) or c["success"] != succ:
                fail.append(f"{lg['log']}: 'Complete' says {c['success']}/{c['total']} successful, "
                            f"records give {succ}/{len(recs)}")
        failed_names = sorted(r["name"] for r in recs if record_status(r) not in ("SUCCESS",))
        if c and not c.get("malformed") and sorted(lg["failed_for"]) != failed_names and lg["failed_for"]:
            fail.append(f"{lg['log']}: 'Verification failed for' list conflicts with per-harness records")
        for r in recs:
            if r["name"].startswith(ns):
                by_name.setdefault(r["name"], []).append(r)
            else:
                other_ns[r["name"].split("::")[0]] += 1

    rows = []
    for name, recs in sorted(by_name.items()):
        if name not in expected:
            fail.append(f"{name}: SmallSort row not in the manifest (unexpected)")
            rows.append({"name": name, "verdict": "FAIL", "reason": "unexpected SmallSort row"})
    for name, h in expected.items():
        recs = by_name.get(name, [])
        row: dict[str, Any] = {"name": name, "expect": h["expect"], "records": len(recs)}
        rows.append(row)
        if not recs:
            row.update(verdict="INCOMPLETE", reason="no result record")
            incomplete.append(f"{name}: no result record")
            continue
        if len(recs) > 1:
            sigs = {(record_status(r), r["covers"], r["checks"]) for r in recs}
            kind = "conflicting" if len(sigs) > 1 else "duplicate"
            row.update(verdict="FAIL" if kind == "conflicting" else "INCOMPLETE",
                       reason=f"{kind} records at " + ", ".join(f"{r['log']}:{r['line']}" for r in recs))
            (fail if kind == "conflicting" else incomplete).append(f"{name}: {row['reason']}")
            continue
        r = recs[0]
        st = record_status(r)
        row.update(status=st, worker=r["worker"], log=r["log"], covers=r["covers"], checks=r["checks"])
        reasons_f, reasons_i = [], []
        if st == "MALFORMED":
            reasons_f.append("malformed: " + "; ".join(r["malformed"]))
        elif st in ("PARTIAL", "UNKNOWN"):
            reasons_i.append(f"status {st}")
        elif st in ("TIMEOUT", "OUT_OF_MEMORY"):
            reasons_f.append(f"status {st} (resource cap, not a counterexample)")
        elif h["expect"] == "SUCCESS" and st != "SUCCESS":
            reasons_f.append(f"status {st}, expected SUCCESS")
        elif h["expect"] == "FAILED":
            if st != "FAILED":
                reasons_f.append(f"status {st}, expected FAILED")
            elif not any(h["expect_check"] in d for d in r["failed_checks"]):
                reasons_f.append(f"FAILED, but not at the designated check {h['expect_check']!r}")
        # covers
        total = h["covers_total"]
        if st not in ("MALFORMED",):
            if total == "UNKNOWN":
                reasons_i.append("expected cover total UNKNOWN (not treated as 0)")
            elif r["covers"] is None:
                if total == 0:
                    pass  # explicit zero allowed by manifest policy (checked at load time)
                else:
                    reasons_i.append(f"no cover record, expected {total}")
            else:
                s, n = r["covers"]
                if n != total:
                    reasons_f.append(f"cover total {n} != expected {total}")
                elif s < n:
                    reasons_f.append(f"{n - s} of {n} cover(s) unreached")
                    if h["panic_cut"]:
                        reasons_f.append("normal-return/route witness not established (terse counts only)")
        if reasons_f:
            row.update(verdict="FAIL", reason="; ".join(reasons_f + reasons_i))
            fail.append(f"{name}: {row['reason']}")
        elif reasons_i:
            row.update(verdict="INCOMPLETE", reason="; ".join(reasons_i))
            incomplete.append(f"{name}: {row['reason']}")
        else:
            row.update(verdict="PASS")

    if fail:
        verdict = "FAIL"
    elif incomplete:
        verdict = "INCOMPLETE"
    else:
        verdict = "PASS"
    ordinary_success = sum(1 for r in rows if r.get("verdict") == "PASS" and r.get("expect") == "SUCCESS")
    expected_failures_met = sum(1 for r in rows if r.get("verdict") == "PASS" and r.get("expect") == "FAILED")
    return {"tool": "cover_parser.py (prototype, not integrated into CI)", "verdict": verdict,
            "suite": manifest["suite"], "verifier_exit": verifier_exit,
            "expected_harnesses": len(expected), "success_rows_passed": ordinary_success,
            "expected_failures_met": expected_failures_met,
            "other_namespaces": dict(sorted(other_ns.items())), "fail": fail, "incomplete": incomplete,
            "rows": rows}


def run(manifest_data: Any, log_texts: list[tuple[str, str]], verifier_exit: int | None,
        observed_identity: dict[str, str]) -> dict[str, Any]:
    manifest, errs = load_manifest(manifest_data)
    if manifest is None:
        return {"tool": "cover_parser.py (prototype, not integrated into CI)", "verdict": "INPUT_ERROR",
                "verifier_exit": verifier_exit, "fail": errs, "incomplete": [], "rows": []}
    logs = [parse_terse(text, log_id) for log_id, text in log_texts]
    if not logs:
        rep = evaluate(manifest, [], verifier_exit, observed_identity)
        rep["incomplete"].insert(0, "no log given")
        if rep["verdict"] == "PASS":
            rep["verdict"] = "INCOMPLETE"
        return rep
    return evaluate(manifest, logs, verifier_exit, observed_identity)


def exit_code(report: dict[str, Any]) -> int:
    v = report.get("verifier_exit")
    if isinstance(v, int) and v != 0:
        return v  # never mask a verifier failure, whatever the parser concluded
    return EXIT[report["verdict"]]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="SmallSort cover/result parser prototype (no Kani run, not in CI)")
    ap.add_argument("--manifest", required=True, help="JSON manifest (format %s)" % MANIFEST_FORMAT)
    ap.add_argument("--log", action="append", default=[], help="terse log file; repeat per job/partition")
    ap.add_argument("--verifier-exit", type=int, default=None, help="exit status of the verifier run")
    ap.add_argument("--identity", action="append", default=[], metavar="KEY=VALUE",
                    help="observed identity, KEY in %s" % ", ".join(IDENTITY_KEYS))
    a = ap.parse_args(argv)
    ident: dict[str, str] = {}
    for kv in a.identity:
        k, sep, v = kv.partition("=")
        if not sep or k not in IDENTITY_KEYS or k in ident:
            print(f"bad or repeated --identity {kv!r}", file=sys.stderr)
            return EXIT["INPUT_ERROR"]
        ident[k] = v
    try:
        with open(a.manifest, encoding="utf-8") as f:
            manifest = json.load(f)
        texts = []
        for i, p in enumerate(a.log):
            with open(p, encoding="utf-8", errors="replace") as f:
                texts.append((f"log{i + 1}", f.read()))
    except (OSError, ValueError) as e:
        print(f"cannot read input: {e}", file=sys.stderr)
        return EXIT["INPUT_ERROR"]
    report = run(manifest, texts, a.verifier_exit, ident)
    json.dump(report, sys.stdout, indent=1, sort_keys=True)
    print()
    print(f"verdict: {report['verdict']} (prototype; verifier exit {report['verifier_exit']})", file=sys.stderr)
    return exit_code(report)


if __name__ == "__main__":
    sys.exit(main())
