#!/usr/bin/env python3
"""Fail-closed classifier for isolated RAPx gate-A output."""
import argparse
import json
import re
from pathlib import Path

CASES = {
    "zst_aligned": ("positive", "zst::aligned", None),
    "zst_source_misaligned": ("negative", "zst::source_misaligned", 0),
    "zst_destination_misaligned": ("negative", "zst::destination_misaligned", 1),
    "u64_aligned": ("positive", "u64_controls::aligned", None),
    "u64_source_misaligned": ("negative", "u64_controls::source_misaligned", 0),
    "u64_destination_misaligned": ("negative", "u64_controls::destination_misaligned", 1),
}


def classify(name: str, exit_code: int, log_path: Path, contracts_path: Path) -> dict:
    expectation, module, expected_failed_index = CASES[name]
    raw_with_ansi = log_path.read_text(errors="replace") if log_path.exists() else ""
    raw = re.sub(r"\x1b\[[0-9;]*m", "", raw_with_ansi)
    raw = re.sub(r"^.*?\|RAPx\|[^|]*\|: ", "", raw, flags=re.M)
    target_path = f"rapx_applicability::{module}::copy"
    target_present = f"[rapx::verify] function: {target_path}" in raw
    summary_target = raw.find(f"[rapx::verify] function: {target_path}")
    summary_tail = raw[summary_target:] if summary_target >= 0 else ""
    copy_headers = re.findall(r"unsafe checkpoint: (bb\d+) -> ([^\n]+)", summary_tail)
    copy_blocks = [bb for bb, callee in copy_headers if "copy_nonoverlapping" in callee]
    # driver.rs emits report.describe() before the user-facing checkpoint table.
    # A diagnostic block carries its checkpoint and per-property VM result.
    diagnostic = "\n".join(line for line in raw.splitlines() if "[rapx::verify::diagnostics]" in line or "check #" in line or "vm-check:" in line)
    check_records = re.findall(
        r"check #(\d+): checkpoint #(\d+), (bb\d+), path #(\d+), property #(\d+) Some\((Align)\), result ([^\n]+)",
        diagnostic,
    )
    copy_bb_set = set(copy_blocks)
    exact_align_rows = [
        {"check": int(check), "checkpoint": int(checkpoint), "bb": bb, "path": int(path),
         "property_index": int(prop), "property": kind, "result": result.strip()}
        for check, checkpoint, bb, path, prop, kind, result in check_records
        if bb in copy_bb_set
    ]
    proved_align = [row for row in exact_align_rows if row["result"] == "Proved"]
    failed_align = [row for row in exact_align_rows if row["result"] == "Failed"]
    has_vm_failed = any("vm-check: Failed" in line for line in raw.splitlines())
    has_sound = bool(re.search(r"result: SOUND(?:\s|$)", summary_tail))
    has_unsound = "result: UNSOUND" in summary_tail
    contract_raw = contracts_path.read_text(errors="replace") if contracts_path.exists() else ""
    contract_align_args = re.findall(r"\bAlign\(\s*(src|dst)\s*,", contract_raw)
    contract_src_dst_pair = contract_align_args[-2:] == ["src", "dst"]
    property_indices = {row["property_index"] for row in exact_align_rows}
    exact_src_dst_rows = property_indices == {0, 1} and contract_src_dst_pair

    outcome = "INCONCLUSIVE"
    reason = "Output did not establish the expected target, checkpoint, and property result."
    if exit_code != 0:
        outcome, reason = "COMMAND_FAILURE", f"RAPx command exit code {exit_code}; preserve as setup/frontend/analysis evidence."
    elif not target_present:
        outcome, reason = "MISSING_TARGET", "Annotated target was not found in the emitted log."
    elif not copy_blocks:
        if re.search(r"unsupported|not supported|unknown intrinsic", raw, re.I):
            outcome, reason = "UNSUPPORTED_OPERATION", "RAPx reported an unsupported operation before a copy checkpoint was established."
        else:
            outcome, reason = "MISSING_CHECKPOINT", "Target emitted no copy_nonoverlapping unsafe-checkpoint group."
    elif len(exact_align_rows) < 2:
        outcome, reason = "MISSING_OR_UNPARSEABLE_OBLIGATION", f"Expected two parseable source/destination Align rows; found {len(exact_align_rows)}."
    elif not exact_src_dst_rows:
        outcome, reason = "CONTRACT_EVIDENCE_MISSING_OR_UNMAPPED", (
            f"Cannot map property indexes to both ordered Align(src,T)/Align(dst,T) requirements; "
            f"contract Align args={contract_align_args}, observed property indexes={sorted(property_indices)}."
        )
    elif expectation == "positive" and has_sound and len(proved_align) >= 2:
        outcome, reason = "PROVED_VALID", "The aligned control has both Align rows proved and the target verdict SOUND."
    elif expectation == "negative" and has_sound and len(proved_align) >= 2:
        outcome, reason = "SOUND_MISS", "The deliberately misaligned case has a SOUND verdict and both Align rows proved."
    elif expectation == "negative" and has_unsound and any(row["property_index"] == expected_failed_index for row in failed_align) \
            and any(row["property_index"] == 1 - expected_failed_index for row in proved_align) and has_vm_failed:
        outcome, reason = "INTENDED_DETECTION", "The copy checkpoint has a failed Align row and vm-check reports Failed."
    elif "Unknown" in "\n".join(str(row) for row in exact_align_rows):
        outcome, reason = "UNKNOWN", "Align result is Unknown; UNSOUND alone is not a detected violation."
    elif has_unsound and not failed_align:
        outcome, reason = "UNRELATED_FAILURE", "UNSOUND lacks a failed Align row at copy_nonoverlapping; this is not an intended negative."
    elif has_unsound:
        outcome, reason = "UNRELATED_FAILURE", "Target verdict is UNSOUND but the expected alignment failure was not confirmed."

    return {
        "case": name,
        "expected": expectation,
        "module": module,
        "outcome": outcome,
        "reason": reason,
        "target_present": target_present,
        "copy_nonoverlapping_checkpoint_count": len(copy_blocks),
        "align_rows": exact_align_rows,
        "copy_contract_align_arguments": contract_align_args,
        "source_destination_alignment_rows_mapped": exact_src_dst_rows,
        "contract_log": str(contracts_path),
        "raw_exit_code": exit_code,
        "full_log": str(log_path),
        "overall_sound": has_sound,
        "overall_unsound": has_unsound,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", choices=CASES, required=True)
    parser.add_argument("--exit-code", type=int, required=True)
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--contracts", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    record = classify(args.case, args.exit_code, args.log, args.contracts)
    args.out.write_text(json.dumps(record, indent=2) + "\n")
    print(f"{record['case']}: {record['outcome']}: {record['reason']}")
    # A complete but adverse classification is evidence, not a runner failure;
    # retain subsequent controls and let the phase report choose NO-GO/INCONCLUSIVE.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
