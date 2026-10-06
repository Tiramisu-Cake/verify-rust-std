#!/usr/bin/env python3
"""Replay the six frozen RAPx 0.7.50 gate-A controls from paired hosted logs.

The case metadata is scoped to source 929ea80 / run 37508888778 on x86_64.
It binds this evidence's exact MIR checkpoint/path/DefId, not future builds or a
whole-function SmallSort proof.  No executable fixture is run by this parser.
"""
import argparse
import json
import re
from pathlib import Path

# The observed six isolated functions each have one copy checkpoint and path.
CASES = {
    "zst_aligned": ("zst::aligned::copy", 43, 0, "[0]", "positive", None),
    "zst_source_misaligned": ("zst::source_misaligned::copy", 44, 3,
                              "[0, 5, 1, 2, 6, 3]", "negative", 0),
    "zst_destination_misaligned": ("zst::destination_misaligned::copy", 45, 3,
                                   "[0, 5, 1, 2, 6, 3]", "negative", 1),
    "u64_aligned": ("u64_controls::aligned::copy", 34, 2,
                    "[0, 4, 1, 5, 2]", "positive", None),
    "u64_source_misaligned": ("u64_controls::source_misaligned::copy", 37, 4,
                              "[0, 6, 1, 2, 7, 3, 8, 4]", "negative", 0),
    "u64_destination_misaligned": ("u64_controls::destination_misaligned::copy", 40, 4,
                                   "[0, 6, 1, 7, 2, 3, 8, 4]", "negative", 1),
}
# ValidPtr(src/dst) each expands to NonNull + a compound remainder (kind None).
PRIMITIVE_KINDS = ("Some(Align)", "Some(Align)", "Some(NonNull)", "None",
                   "Some(NonNull)", "None", "Some(NonOverlap)", "Some(ValidNum)")
PRIMITIVE_ROLES = ("Align(src,T)", "Align(dst,T)", "ValidPtr(src).NonNull",
                   "ValidPtr(src).remainder", "ValidPtr(dst).NonNull",
                   "ValidPtr(dst).remainder", "NonOverlap", "ValidNum")
CONTRACT_CALLS = ("Align(src, T)", "Align(dst, T)", "ValidPtr(src, T, count)",
                  "ValidPtr(dst, T, count)", "NonOverlap(dst, src, T, count)",
                  "ValidNum(size_of(T) * count <= 9223372036854775807)")
ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
PREFIX = re.compile(r"^.*?\|RAPx\|(?P<level>[^|]+)\|:\s?(?P<message>.*)$")
CONTRACT_FN = re.compile(r"^\s*fn (?P<path>(?:zst|u64_controls)::\S+?::copy)(?:\(|\s|$)")
CONTRACT_CALLEE = re.compile(r"^\s*(?:\|-|`-) fn (?P<signature>.+)$")
CONTRACT_PROP = re.compile(r"^\s*(?:\|-|`-) (?P<call>\w+\([^\n]*\))$")
COPY_CONTRACT = re.compile(r"^(?:std|core)::ptr::copy_nonoverlapping::<T>\(src: \*const T, dst: \*mut T, count: usize\)$")
COPY_SUMMARY = re.compile(r"^(?:std|core)::ptr::copy_nonoverlapping$")
TARGET = re.compile(r"^\[rapx::verify\] function: (?P<path>\S+)$")
REPORT = re.compile(r"^\[rapx::verify::diagnostics\] function (?P<id>DefId\(.+\)): (?P<count>\d+) check item\(s\)$")
CHECK = re.compile(r"^\s*check #(?P<check>\d+): checkpoint #(?P<checkpoint>\d+), bb(?P<bb>\d+), path #(?P<path>\d+), property #(?P<property>\d+) (?P<kind>Some\(\w+\)|None), result (?P<result>Proved|Failed|Unknown)$")
VM = re.compile(r"^\s*vm-check: (?P<result>ProvedByRule|ProvedBySmt|Failed|Unknown)$")
CHECKPOINT = re.compile(r"^\s*unsafe checkpoint: bb(?P<bb>\d+) -> (?P<callee>\S+)$")
PATH = re.compile(r"^\s*path (?P<description>\[[^\]]+\]):$")
PROP_ROW = re.compile(r"^\s*(?:[├└]──\s*)?(?P<kind>Align|ValidPtr|NonOverlap|ValidNum) \| (?P<result>Proved|Failed|Unknown)(?: \(x(?P<count>\d+)\))?$")
VERDICT = re.compile(r"^\s*result: (?P<result>SOUND|UNSOUND|UNKNOWN)(?: \((?P<unproved>\d+) unproved, (?P<hazard>\d+) hazard\))?$")
ISSUE = re.compile(r"matched no (?:targets|functions)|no safety contracts found|skipping .+|unsupported|not supported|unknown intrinsic|panicked|verifier crashed", re.I)


def read_log(path):
    if not path.is_file():
        return [], []
    lines, warnings = [], []
    for raw in path.read_text(errors="replace").splitlines():
        raw = ANSI.sub("", raw)
        match = PREFIX.match(raw)
        line = match.group("message") if match else raw
        lines.append(line)
        if match and re.search(r"warn|error", match.group("level"), re.I):
            # The renderer deliberately uses rap_warn! for adverse property
            # rows and UNSOUND. Other warnings need investigation.
            if not PROP_ROW.match(line) and not (VERDICT.match(line) and "UNSOUND" in line):
                warnings.append(line)
        elif ISSUE.search(line):
            warnings.append(line)
    return lines, warnings


def parse_contract(lines, target):
    if sum("[rapx::debug-contracts] Expanded Contract Assertions" in line for line in lines) != 1:
        return None, "Missing or duplicate expanded-contract header"
    if any(REPORT.match(line) or TARGET.match(line) for line in lines):
        return None, "Contract-print invocation contains verification output"
    if sum(re.match(r"^\s*fn ", line) is not None for line in lines) != 1 or \
            sum(CONTRACT_CALLEE.match(line) is not None for line in lines) != 1:
        return None, "Extra or unparsed contract function/callee header"
    functions = [(i, match.group("path")) for i, line in enumerate(lines)
                 if (match := CONTRACT_FN.match(line))]
    if len(functions) != 1 or functions[0][1] != target:
        return None, f"Wrong/duplicate contract function: {functions}"
    start = functions[0][0]
    end = next((i for i in range(start + 1, len(lines)) if not lines[i].strip()), len(lines))
    block = lines[start:end]
    if sum("[Unsafe Callees]:" in line for line in block) != 1:
        return None, "Target lacks one Unsafe Callees section"
    callees = [(i, match.group("signature")) for i, line in enumerate(block)
               if (match := CONTRACT_CALLEE.match(line))]
    if len(callees) != 1 or not COPY_CONTRACT.fullmatch(callees[0][1]):
        return None, f"Unexpected contract callee: {callees}"
    property_lines = [line for line in block[callees[0][0] + 1:]
                      if re.match(r"^\s*(?:\|-|`-) ", line)]
    parsed = [CONTRACT_PROP.match(line) for line in property_lines]
    if any(match is None for match in parsed):
        return None, f"Unparsed contract property: {property_lines}"
    calls = tuple(match.group("call") for match in parsed)
    if calls != CONTRACT_CALLS:
        return None, f"Six displayed copy contracts differ: {calls}"
    return {"function": target, "callee": callees[0][1], "calls": calls,
            "align_mapping": {"src": 0, "dst": 1}}, ""


def parse_diagnostic(lines, target, def_index, bb):
    headers = [(i, match) for i, line in enumerate(lines) if (match := REPORT.match(line))]
    if len(headers) != 1:
        return None, f"Expected one report.describe() header; observed {len(headers)}"
    start, header = headers[0]
    expected_id = f"DefId(0:{def_index} ~ rapx_applicability[e215]::{target})"
    if header.group("id") != expected_id or int(header.group("count")) != 8:
        return None, f"Wrong DefId or check count: {header.group('id')}, {header.group('count')}"
    if sum("[rapx::verify::diagnostics] function" in line for line in lines) != 1:
        return None, "Unparsed or duplicate diagnostic header"
    if len([line for line in lines if re.match(r"^\s*check #", line)]) != 8 or \
            len([line for line in lines if re.match(r"^\s*vm-check:", line)]) != 8:
        return None, "Missing, duplicate, or unparsed check/vm-check record"
    rows = []
    for index in range(8):
        row_line = lines[start + 1 + 2 * index] if start + 1 + 2 * index < len(lines) else ""
        vm_line = lines[start + 2 + 2 * index] if start + 2 + 2 * index < len(lines) else ""
        check, vm = CHECK.match(row_line), VM.match(vm_line)
        if check is None or vm is None:
            return None, f"Unparsed or unmatched check/vm-check at property {index}"
        row = {key: int(check.group(key)) for key in
               ("check", "checkpoint", "bb", "path", "property")}
        row.update(kind=check.group("kind"), result=check.group("result"),
                   vm_check=vm.group("result"), role=PRIMITIVE_ROLES[index])
        if (row["check"], row["checkpoint"], row["bb"], row["path"],
                row["property"], row["kind"]) != (index, 0, bb, 0, index, PRIMITIVE_KINDS[index]):
            return None, f"Wrong check/checkpoint/path/property/kind: {row}"
        label = "Proved" if row["vm_check"].startswith("Proved") else row["vm_check"]
        if row["result"] != label:
            return None, f"check #{index} result disagrees with its vm-check"
        rows.append(row)
    return {"defid": expected_id, "checkpoint": 0, "bb": bb, "path_index": 0,
            "rows": rows}, ""


def summary_rows_from_detail(rows):
    align = [row["result"] for row in rows[:2]]
    result = [["Align", align[0], 2]] if align[0] == align[1] else [
        ["Align", align[0], 1], ["Align", align[1], 1]]
    valid_ptr_parts = [row["result"] for row in rows[2:6]]
    valid_ptr = "Failed" if "Failed" in valid_ptr_parts else \
        "Unknown" if "Unknown" in valid_ptr_parts else "Proved"
    result.extend([["ValidPtr", valid_ptr, 1], ["NonOverlap", rows[6]["result"], 1],
                   ["ValidNum", rows[7]["result"], 1]])
    return result


def parse_summary(lines, target, bb, path, rows):
    headers = [(i, match.group("path")) for i, line in enumerate(lines)
               if (match := TARGET.match(line))]
    if len(headers) != 1 or headers[0][1] != target:
        return None, f"Wrong or duplicate final function header: {headers}"
    if sum("[rapx::verify] function:" in line for line in lines) != 1:
        return None, "Unparsed final function header"
    if any("[rapx::debug-contracts] Expanded Contract Assertions" in line for line in lines):
        return None, "Verification invocation also printed debug contracts"
    verdicts = [(i, match) for i, line in enumerate(lines) if (match := VERDICT.match(line))]
    if len(verdicts) != 1 or sum(re.match(r"^\s*result:", line) is not None for line in lines) != 1:
        return None, f"Expected one final verdict; observed {len(verdicts)}"
    start, stop = headers[0][0], verdicts[0][0]
    if stop <= start:
        return None, "Verdict precedes target function"
    block = lines[start:stop + 1]
    checkpoints = [(i, match) for i, line in enumerate(block)
                   if (match := CHECKPOINT.match(line))]
    if len(checkpoints) != 1 or int(checkpoints[0][1].group("bb")) != bb or \
            not COPY_SUMMARY.fullmatch(checkpoints[0][1].group("callee")):
        return None, f"Wrong or duplicate copy checkpoint: {[m.groupdict() for _, m in checkpoints]}"
    if sum("unsafe checkpoint:" in line for line in lines) != 1:
        return None, "Unparsed or duplicate checkpoint header"
    paths = [(i, match.group("description")) for i, line in enumerate(block)
             if (match := PATH.match(line))]
    if len(paths) != 1 or paths[0][1] != path or paths[0][0] <= checkpoints[0][0]:
        return None, f"Wrong, absent, or duplicate summary path: {paths}"
    if sum(re.match(r"^\s*path \[", line) is not None for line in lines) != 1:
        return None, "Unparsed or duplicate path header"
    path_lines = block[paths[0][0] + 1:-1]
    actual = []
    for line in path_lines:
        if not line.strip():
            continue
        match = PROP_ROW.match(line)
        if match is None:
            return None, f"Unparsed summary property row: {line}"
        actual.append([match.group("kind"), match.group("result"),
                       int(match.group("count") or 1)])
    expected = summary_rows_from_detail(rows)
    if actual != expected:
        return None, f"Summary rows differ from diagnostic origin-folding: {actual} != {expected}"
    verdict = verdicts[0][1]
    unproved = sum(row["result"] != "Proved" for row in rows)
    if unproved == 0:
        valid_verdict = verdict.group("result") == "SOUND" and verdict.group("unproved") is None
    else:
        valid_verdict = (verdict.group("result") == "UNSOUND" and
                         verdict.group("unproved") == str(unproved) and verdict.group("hazard") == "0")
    if not valid_verdict:
        return None, f"Verdict contradicts {unproved} unproved primitive rows"
    return {"function": target, "checkpoint_bb": bb,
            "callee": checkpoints[0][1].group("callee"),
            "path_description": path, "property_rows": actual,
            "verdict": verdict.group("result"), "unproved_count": unproved}, ""


def classify(name, exit_code, log_path, contracts_path, contract_exit_code=0):
    target, def_index, bb, path, expectation, bad_index = CASES[name]
    verify, verify_warnings = read_log(log_path)
    contracts, contract_warnings = read_log(contracts_path)
    record = {"case": name, "expected": expectation, "target": target,
              "profile_scope": "run37508888778/source929ea80/x86_64/RAPx0.7.50",
              "evidence_complete": False, "outcome": "INCONCLUSIVE",
              "reason": "Incomplete evidence", "raw_exit_code": exit_code,
              "contract_exit_code": contract_exit_code,
              "verification_log": str(log_path), "contract_log": str(contracts_path),
              "contract": None, "diagnostic": None, "summary": None,
              "targeted_align_status": "NOT_ESTABLISHED", "align_rows": [],
              "other_failed_rows": [], "unknown_rows": [],
              "relevant_warnings": verify_warnings + contract_warnings}
    def finish(outcome, reason):
        record.update(outcome=outcome, reason=reason)
        return record
    if exit_code == 124 or contract_exit_code == 124:
        return finish("TIMEOUT", "A paired RAPx invocation timed out")
    if exit_code != 0 or contract_exit_code != 0:
        return finish("COMMAND_FAILURE", f"Contract/verify exit: {contract_exit_code}/{exit_code}")
    if not verify or not contracts or log_path.resolve() == contracts_path.resolve():
        return finish("MISSING_LOG", "Two separate, nonempty logs are required")
    if any(re.search(r"unsupported|not supported|unknown intrinsic", x, re.I)
           for x in record["relevant_warnings"]):
        return finish("UNSUPPORTED_OPERATION", "RAPx reported an unsupported operation")
    if record["relevant_warnings"]:
        return finish("UNEXPECTED_WARNING", "RAPx warning/error requires review")
    contract, error = parse_contract(contracts, target)
    if error:
        return finish("CONTRACT_EVIDENCE_MISSING_OR_UNMAPPED", error)
    record["contract"] = contract
    diagnostic, error = parse_diagnostic(verify, target, def_index, bb)
    if error:
        return finish("MISSING_OR_UNPARSEABLE_OBLIGATION", error)
    record["diagnostic"] = diagnostic
    rows = diagnostic["rows"]
    record["align_rows"] = rows[:2]
    record["other_failed_rows"] = [row for row in rows[2:] if row["result"] == "Failed"]
    record["unknown_rows"] = [row for row in rows if row["result"] == "Unknown"]
    summary, error = parse_summary(verify, target, bb, path, rows)
    if error:
        return finish("SUMMARY_DIAGNOSTIC_MISMATCH", error)
    record["summary"] = summary
    record["evidence_complete"] = True
    if expectation == "positive":
        if summary["verdict"] == "SOUND" and all(row["result"] == "Proved" for row in rows):
            record["targeted_align_status"] = "BOTH_PROVED"
            return finish("PROVED_VALID", "All eight primitive copy obligations proved")
        record["targeted_align_status"] = "UNRESOLVED"
        return finish("INCONCLUSIVE", "Aligned control has an unproved property")
    other_index = 1 - bad_index
    if rows[bad_index]["result"] == "Proved" and rows[other_index]["result"] == "Proved":
        record["targeted_align_status"] = "MISALIGNED_ALIGN_PROVED"
        if summary["verdict"] == "SOUND" and not record["other_failed_rows"] and not record["unknown_rows"]:
            return finish("SOUND_MISS", "Deliberately misaligned Align obligation was proved")
        return finish("ALIGN_PROVED_OTHER_UNPROVED", "Target Align proved while another obligation remained unproved")
    if rows[bad_index]["result"] == "Failed" and rows[other_index]["result"] == "Proved":
        record["targeted_align_status"] = "FAILED_EXPECTED_ALIGN"
        if record["other_failed_rows"] or record["unknown_rows"]:
            return finish("INTENDED_ALIGN_DETECTION_WITH_OTHER_UNPROVED",
                          "Expected Align failed; other obligations Failed/Unknown")
        return finish("INTENDED_DETECTION", "Only the expected Align obligation failed")
    record["targeted_align_status"] = "UNRESOLVED"
    return finish("INCONCLUSIVE", "Expected Align failure was not isolated")


def summarize(records):
    """Keep process success, parsed evidence, and gate decision separate."""
    records = list(records)
    by_case = {record.get("case"): record for record in records if isinstance(record, dict)}
    exact_set = len(records) == len(CASES) and set(by_case) == set(CASES)
    commands_succeeded = exact_set and all(
        isinstance(record, dict) and record.get("raw_exit_code") == 0 and
        record.get("contract_exit_code") == 0
        for record in records
    )
    def consistent(record):
        if not isinstance(record, dict):
            return False
        name = record.get("case")
        if name not in CASES or record.get("evidence_complete") is not True or \
                record.get("raw_exit_code") != 0 or record.get("contract_exit_code") != 0:
            return False
        detail = record.get("diagnostic") or {}
        summary = record.get("summary") or {}
        if not isinstance(detail, dict) or not isinstance(summary, dict):
            return False
        rows = detail.get("rows")
        if not isinstance(rows, list) or len(rows) != 8 or summary.get("verdict") not in ("SOUND", "UNSOUND"):
            return False
        if any(not isinstance(row, dict) or row.get("result") not in ("Proved", "Failed", "Unknown")
               or row.get("property") != i for i, row in enumerate(rows)):
            return False
        target, def_index, bb, path = CASES[name][:4]
        unproved = sum(r.get("result") != "Proved" for r in rows)
        if detail.get("defid") != f"DefId(0:{def_index} ~ rapx_applicability[e215]::{target})" or \
                detail.get("bb") != bb or detail.get("path_index") != 0 or \
                summary.get("function") != target or summary.get("checkpoint_bb") != bb or \
                summary.get("path_description") != path or \
                summary.get("property_rows") != summary_rows_from_detail(rows) or \
                summary.get("unproved_count") != unproved or \
                summary.get("verdict") != ("SOUND" if unproved == 0 else "UNSOUND"):
            return False
        if record.get("align_rows") != rows[:2] or \
                record.get("other_failed_rows") != [r for r in rows[2:] if r.get("result") == "Failed"] or \
                record.get("unknown_rows") != [r for r in rows if r.get("result") == "Unknown"]:
            return False
        expectation, bad_index = CASES[name][4:6]
        if expectation == "positive":
            derived = ("PROVED_VALID", "BOTH_PROVED") if summary["verdict"] == "SOUND" and \
                all(r.get("result") == "Proved" for r in rows) else ("INCONCLUSIVE", "UNRESOLVED")
        elif rows[0].get("result") == rows[1].get("result") == "Proved":
            derived = ("SOUND_MISS", "MISALIGNED_ALIGN_PROVED") if summary["verdict"] == "SOUND" and \
                all(r.get("result") == "Proved" for r in rows) else \
                ("ALIGN_PROVED_OTHER_UNPROVED", "MISALIGNED_ALIGN_PROVED")
        elif rows[bad_index].get("result") == "Failed" and rows[1 - bad_index].get("result") == "Proved":
            derived = (("INTENDED_ALIGN_DETECTION_WITH_OTHER_UNPROVED" if
                        record["other_failed_rows"] or record["unknown_rows"] else
                        "INTENDED_DETECTION"), "FAILED_EXPECTED_ALIGN")
        else:
            derived = ("INCONCLUSIVE", "UNRESOLVED")
        return (record.get("outcome"), record.get("targeted_align_status")) == derived

    trusted = [record for record in records if consistent(record)]
    evidence_parsed = exact_set and len(trusted) == len(CASES)
    expected = all(
        by_case[name].get("outcome") ==
        ("PROVED_VALID" if CASES[name][4] == "positive" else "INTENDED_DETECTION")
        for name in CASES
    ) if evidence_parsed else False
    if any(record.get("outcome") == "SOUND_MISS" for record in trusted):
        gate_outcome = "NO-GO"
    elif evidence_parsed and expected:
        gate_outcome = "PASS"
    else:
        gate_outcome = "INCONCLUSIVE"
    result_counts = {name: sum(row["result"] == name for record in trusted
                               for row in record["diagnostic"]["rows"])
                     for name in ("Proved", "Failed", "Unknown")}
    return {"commands_succeeded": commands_succeeded,
            "evidence_parsed": evidence_parsed, "gate_outcome": gate_outcome,
            "primitive_result_counts": result_counts, "records": records,
            "case_outcomes": {name: by_case[name].get("outcome", "MISSING_CASE")
                              if name in by_case else "MISSING_CASE" for name in CASES}}


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
    return 0  # A failed gate classification remains usable evidence.

if __name__ == "__main__":
    raise SystemExit(main())
