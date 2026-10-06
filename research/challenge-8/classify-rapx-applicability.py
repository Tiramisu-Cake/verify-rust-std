#!/usr/bin/env python3
"""Fail-closed classifier for RAPx 0.7.50 gate A's separate hosted logs.

--debug-contracts returns before verification.  Only the separate verify log's
per-path report and final verdict can establish detector behavior.
"""
import argparse
import json
import re
from collections import Counter
from pathlib import Path

CASES = {
    "zst_aligned": ("positive", "zst::aligned", None),
    "zst_source_misaligned": ("negative", "zst::source_misaligned", "src"),
    "zst_destination_misaligned": ("negative", "zst::destination_misaligned", "dst"),
    "u64_aligned": ("positive", "u64_controls::aligned", None),
    "u64_source_misaligned": ("negative", "u64_controls::source_misaligned", "src"),
    "u64_destination_misaligned": ("negative", "u64_controls::destination_misaligned", "dst"),
}
KINDS = ("Align", "Align", "ValidPtr", "ValidPtr", "NonOverlap", "ValidNum")
PREFIX = re.compile(r"^.*?\|RAPx\|(?P<level>[^|]+)\|:\s?(?P<message>.*)$")
ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
CONTRACT_FN = re.compile(r"^\s*fn (?P<path>rapx_applicability::\S+?::copy)(?:\(|\s|$)")
CONTRACT_CALLEE = re.compile(r"^\s*(?:\|-|`-) fn (?P<path>\S+)")
CONTRACT_PROP = re.compile(r"^\s*(?:\|-|`-) (?P<call>\w+\([^\n]*\))$")
COPY = re.compile(r"^core::ptr::copy_nonoverlapping(?:::<[^>]+>)?(?:\(|$)")
TARGET = re.compile(r"^\[rapx::verify\] function: (?P<path>\S+)$")
REPORT = re.compile(r"^\[rapx::verify::diagnostics\] function (?P<id>DefId\(.+\)): (?P<count>\d+) check item\(s\)$")
CHECK = re.compile(r"^\s*check #(?P<check>\d+): checkpoint #(?P<checkpoint>\d+), bb(?P<bb>\d+), path #(?P<path>\d+), property #(?P<property>\d+) (?P<kind>Some\(\w+\)|None), result (?P<result>Proved|Failed|Unknown)$")
VM = re.compile(r"^\s*vm-check: (?P<result>ProvedByRule|ProvedBySmt|Failed|Unknown)$")
CHECKPOINT = re.compile(r"^\s*unsafe checkpoint: bb(?P<bb>\d+) -> (?P<callee>\S+)$")
PATH = re.compile(r"^\s*path (?P<description>.+):$")
PROP_ROW = re.compile(r"^\s*(?:[├└]──\s*)?(?P<kind>\w+) \| (?P<result>Proved|Failed|Unknown)(?: \(x(?P<count>\d+)\))?$")
VERDICT = re.compile(r"^\s*result: (?P<result>SOUND|UNSOUND|UNKNOWN)(?:\s|$)")
ISSUE = re.compile(r"matched no (?:targets|functions)|no safety contracts found|skipping .+|unsupported|not supported|unknown intrinsic|panicked|verifier crashed", re.I)


def defid_matches_target(defid, target):
    """Match pinned rustc's local DefId debug path, including crate hash.

    rustc_interface::callbacks::def_id_debug renders the `~` path while a
    TyCtxt is active; TyCtxt::def_path_debug_str inserts the four-digit crate
    hash before the path returned by to_string_no_crate_verbose().
    """
    crate, suffix = target.split("::", 1)
    expected = rf"DefId\(0:[1-9]\d* ~ {re.escape(crate)}\[[0-9a-f]{{4}}\]::{re.escape(suffix)}\)"
    return re.fullmatch(expected, defid) is not None


def read_log(path):
    if not path.is_file():
        return [], []
    lines, warnings = [], []
    for raw in path.read_text(errors="replace").splitlines():
        raw = ANSI.sub("", raw)
        m = PREFIX.match(raw)
        line = m.group("message") if m else raw
        lines.append(line)
        if m and re.search("warn|error", m.group("level"), re.I):
            # The pinned renderer uses rap_warn! for an adverse verdict/row.
            if not (VERDICT.match(line) and "UNSOUND" in line) and not PROP_ROW.match(line):
                warnings.append(line)
        elif ISSUE.search(line):
            warnings.append(line)
    return lines, warnings


def parse_contract(lines, target):
    if sum("[rapx::debug-contracts] Expanded Contract Assertions" in x for x in lines) != 1:
        return None, "Missing or repeated expanded-contracts header"
    headers = [(i, m.group("path")) for i, x in enumerate(lines) if (m := CONTRACT_FN.match(x))]
    if len(headers) != 1 or headers[0][1] != target:
        return None, f"Expected only contract target {target}; observed {[p for _, p in headers]}"
    start = headers[0][0]
    end = next((i for i in range(start + 1, len(lines)) if not lines[i].strip()), len(lines))
    block = lines[start:end]
    if sum("[Unsafe Callees]:" in x for x in block) != 1:
        return None, "Target has no unique Unsafe Callees section"
    callees = [(i, m.group("path")) for i, x in enumerate(block) if (m := CONTRACT_CALLEE.match(x))]
    copy = [(i, p) for i, p in callees if COPY.match(p)]
    if len(copy) != 1 or len(callees) != 1:
        return None, f"Expected only copy_nonoverlapping callee; observed {callees}"
    property_lines = [x for x in block[copy[0][0] + 1:]
                      if re.match(r"^\s*(?:\|-|`-) ", x)]
    parsed = [CONTRACT_PROP.match(x) for x in property_lines]
    if any(m is None for m in parsed):
        return None, f"Unparsed copy contract property lines: {property_lines}"
    calls = [m.group("call") for m in parsed]
    if tuple(x.split("(", 1)[0] for x in calls) != KINDS:
        return None, f"Pinned six primitive properties absent or unmapped: {calls}"
    mapping = []
    for i, arg in enumerate(("src", "dst")):
        if not re.fullmatch(rf"Align\(\s*{arg}\s*,\s*T\s*\)", calls[i]):
            return None, f"Cannot map Align({arg},T) at property index {i}: {calls}"
        mapping.append({"argument": arg, "property_index": i, "call": calls[i]})
    return mapping, ""


def parse_reports(lines):
    headers = [(i, m) for i, x in enumerate(lines) if (m := REPORT.match(x))]
    if not headers:
        return None, "No report.describe() diagnostic in verification log"
    consumed, reports = set(), []
    for n, (start, header) in enumerate(headers):
        stop = headers[n + 1][0] if n + 1 < len(headers) else len(lines)
        rows = []
        for i in range(start + 1, stop):
            m = CHECK.match(lines[i])
            if not m:
                continue
            consumed.add(i)
            vm = VM.match(lines[i + 1]) if i + 1 < stop else None
            if not vm:
                return None, f"check row at line {i + 1} lacks its own vm-check"
            row = {k: int(m.group(k)) for k in ("check", "checkpoint", "bb", "path", "property")}
            row.update(kind=m.group("kind"), result=m.group("result"), vm_check=vm.group("result"))
            label = "Proved" if row["vm_check"].startswith("Proved") else row["vm_check"]
            if row["result"] != label:
                return None, f"check #{row['check']} disagrees with vm-check"
            rows.append(row)
        if len(rows) != int(header.group("count")) or [r["check"] for r in rows] != list(range(len(rows))):
            return None, "Report count or check indexes do not match parsed rows"
        reports.append({"defid": header.group("id"), "rows": rows})
    if {i for i, x in enumerate(lines) if CHECK.match(x)} != consumed or len({r["defid"] for r in reports}) != 1:
        return None, "Orphan check rows or multiple diagnostic functions"
    return reports, ""


def parse_summary(lines, target):
    headers = [(i, m.group("path")) for i, x in enumerate(lines) if (m := TARGET.match(x))]
    if len(headers) != 1 or headers[0][1] != target:
        return None, f"Expected only verified function {target}; observed {[p for _, p in headers]}"
    start = headers[0][0]
    end = next((i for i in range(start + 1, len(lines)) if VERDICT.match(lines[i])), len(lines))
    if end == len(lines):
        return None, "Target emitted no final verdict"
    if "no unsafe checkpoints" in lines[end]:
        return None, "Target verdict claims no unsafe checkpoints"
    block = lines[start:end + 1]
    checkpoints = [(i, int(m.group("bb")), m.group("callee")) for i, x in enumerate(block) if (m := CHECKPOINT.match(x))]
    if len(checkpoints) != 1 or not COPY.match(checkpoints[0][2]):
        return None, f"Expected unique copy checkpoint; observed {checkpoints}"
    paths, current = [], None
    for line in block[checkpoints[0][0] + 1:-1]:
        if m := PATH.match(line):
            current = {"description": m.group("description"), "align": [], "properties": []}
            paths.append(current)
        elif m := PROP_ROW.match(line):
            if current is None:
                return None, "Property row outside checkpoint path"
            current["properties"].append({"kind": m.group("kind"),
                                          "result": m.group("result"),
                                          "count": int(m.group("count") or 1)})
            if m.group("kind") == "Align":
                current["align"].extend([m.group("result")] * int(m.group("count") or 1))
        elif current is not None and " | " in line:
            return None, f"Unparsed checkpoint property row: {line}"
    if not paths or any(len(p["align"]) < 2 for p in paths):
        return None, "Final copy summary lacks path-local Align rows"
    return {"verdict": VERDICT.match(lines[end]).group("result"), "bb": checkpoints[0][1], "paths": paths}, ""


def classify(name, exit_code, log_path, contracts_path, contract_exit_code=0):
    expectation, module, bad_arg = CASES[name]
    target = f"rapx_applicability::{module}::copy"
    verify, verify_warnings = read_log(log_path)
    contracts, contract_warnings = read_log(contracts_path)
    record = {"case": name, "expected": expectation, "module": module, "target": target,
              "outcome": "INCONCLUSIVE", "reason": "Incomplete evidence",
              "raw_exit_code": exit_code, "contract_exit_code": contract_exit_code,
              "verification_log": str(log_path),
              "contract_log": str(contracts_path), "align_mapping": [],
              "copy_checkpoint_bb": None, "path_count": 0, "align_rows": [],
              "summary_paths": [], "diagnostic_reports": [],
              "overall_sound": False, "overall_unsound": False,
              "relevant_warnings": verify_warnings + contract_warnings}
    def finish(outcome, reason):
        record.update(outcome=outcome, reason=reason)
        return record
    if exit_code == 124:
        return finish("TIMEOUT", "Verification timed out")
    if exit_code != 0:
        return finish("COMMAND_FAILURE", f"Verification command exited {exit_code}")
    if contract_exit_code != 0:
        return finish("CONTRACT_COMMAND_FAILURE", f"Contract command exited {contract_exit_code}")
    if not verify or not contracts or log_path.resolve() == contracts_path.resolve():
        return finish("MISSING_LOG", "Separate contract and verification logs are required")
    if any(re.search("unsupported|not supported|unknown intrinsic", x, re.I) for x in record["relevant_warnings"]):
        return finish("UNSUPPORTED_OPERATION", "RAPx reported an unsupported operation")
    if record["relevant_warnings"]:
        return finish("UNEXPECTED_WARNING", "RAPx warning/error requires review")
    mapping, error = parse_contract(contracts, target)
    if error:
        return finish("CONTRACT_EVIDENCE_MISSING_OR_UNMAPPED", error)
    record["align_mapping"] = mapping
    summary, error = parse_summary(verify, target)
    if error:
        return finish("MISSING_TARGET_OR_CHECKPOINT", error)
    record["copy_checkpoint_bb"] = summary["bb"]
    record["path_count"] = len(summary["paths"])
    record["summary_paths"] = summary["paths"]
    record["overall_sound"] = summary["verdict"] == "SOUND"
    record["overall_unsound"] = summary["verdict"] == "UNSOUND"
    if summary["verdict"] == "UNKNOWN":
        return finish("UNKNOWN", "Final target verdict is UNKNOWN")
    reports, error = parse_reports(verify)
    if error:
        return finish("MISSING_OR_UNPARSEABLE_OBLIGATION", error)
    record["diagnostic_reports"] = [
        {"defid": report["defid"], "path_indexes": sorted({r["path"] for r in report["rows"]}),
         "check_count": len(report["rows"])} for report in reports
    ]
    if any(not defid_matches_target(report["defid"], target) for report in reports):
        return finish("MISSING_OR_UNPARSEABLE_OBLIGATION",
                      "Diagnostic DefId path does not name the verified target")
    all_rows = [r for report in reports for r in report["rows"]]
    if not all_rows:
        return finish("MISSING_OR_UNPARSEABLE_OBLIGATION", "No path/property checks executed")
    for report in reports:
        rows = report["rows"]
        if any(r["bb"] != summary["bb"] or r["checkpoint"] != 0 for r in rows):
            return finish("MISSING_OR_UNPARSEABLE_OBLIGATION", "Diagnostic checkpoint differs from copy")
        paths = {r["path"] for r in rows}
        if not paths or paths != set(range(len(paths))):
            return finish("MISSING_OR_UNPARSEABLE_OBLIGATION", "Diagnostic paths absent or gapped")
        for path in paths:
            path_rows = [r for r in rows if r["path"] == path]
            if len(path_rows) != len(KINDS) or {r["property"] for r in path_rows} != set(range(len(KINDS))):
                return finish("MISSING_OR_UNPARSEABLE_OBLIGATION", "Copy path lacks a primitive obligation")
            if any(r["kind"] != f"Some({KINDS[r['property']]})" for r in path_rows):
                return finish("CONTRACT_EVIDENCE_MISSING_OR_UNMAPPED", "Property indexes disagree with copy contract")
    record["align_rows"] = [r for r in all_rows if r["property"] in (0, 1)]
    detail_counts = Counter((KINDS[r["property"]], r["result"]) for r in all_rows)
    summary_counts = Counter()
    for path in summary["paths"]:
        for prop in path["properties"]:
            summary_counts[(prop["kind"], prop["result"])] += prop["count"]
    if detail_counts != summary_counts:
        return finish("SUMMARY_DIAGNOSTIC_MISMATCH",
                      "Final summary property counts differ from per-path diagnostics")
    if any(r["result"] == "Unknown" for r in all_rows) or any("Unknown" in p["align"] for p in summary["paths"]):
        return finish("UNKNOWN", "A copy property/path is Unknown")
    if expectation == "positive":
        if any(set(p["align"]) != {"Proved"} for p in summary["paths"]):
            return finish("SUMMARY_DIAGNOSTIC_MISMATCH", "Aligned summary has a non-proved Align")
        if summary["verdict"] == "SOUND" and all(r["result"] == "Proved" for r in all_rows):
            return finish("PROVED_VALID", "All copy properties proved on every path")
        return finish("UNRELATED_FAILURE", "Aligned control did not prove every copy obligation")
    bad_index = next(x["property_index"] for x in mapping if x["argument"] == bad_arg)
    if all(r["result"] == "Proved" for r in record["align_rows"]):
        if summary["verdict"] == "SOUND" and all(r["result"] == "Proved" for r in all_rows) \
                and all(set(p["align"]) == {"Proved"} for p in summary["paths"]):
            return finish("SOUND_MISS", f"Deliberate Align({bad_arg},T) violation was proved")
        if summary["verdict"] == "UNSOUND" and all(set(p["align"]) == {"Proved"} for p in summary["paths"]):
            return finish("ALIGN_PROVED_OTHER_FAILURE",
                          f"Align({bad_arg},T) was proved but another obligation made target UNSOUND")
    if any(set(p["align"]) != {"Proved", "Failed"} for p in summary["paths"]):
        return finish("SUMMARY_DIAGNOSTIC_MISMATCH", "Failed/Proved Align pair absent on a summary path")
    align_isolated = all(
        r["result"] == ("Failed" if r["property"] == bad_index else "Proved")
        for r in all_rows if r["property"] in (0, 1)
    )
    if summary["verdict"] == "UNSOUND" and align_isolated:
        record["other_failed_rows"] = [r for r in all_rows
                                       if r["property"] not in (0, 1) and r["result"] == "Failed"]
        return finish("INTENDED_DETECTION", f"Align({bad_arg},T) Failed on every copy path")
    return finish("UNRELATED_FAILURE", "Expected Align failure was not isolated on every path")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", choices=CASES, required=True)
    parser.add_argument("--exit-code", type=int, required=True)
    parser.add_argument("--contract-exit-code", type=int, default=0)
    parser.add_argument("--verify-log", "--log", dest="verify_log", type=Path, required=True)
    parser.add_argument("--contracts", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    record = classify(args.case, args.exit_code, args.verify_log, args.contracts,
                      args.contract_exit_code)
    args.out.write_text(json.dumps(record, indent=2) + "\n")
    print(f"{record['case']}: {record['outcome']}: {record['reason']}")
    return 0  # An adverse classification is still experiment evidence.

if __name__ == "__main__":
    raise SystemExit(main())
