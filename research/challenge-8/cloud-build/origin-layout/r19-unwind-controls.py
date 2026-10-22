#!/usr/bin/env python3
"""Source-bound distinguishing controls for the R19 insert_tail unwind cleanup."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re


STAGES = ("exporter", "decode", "refinement", "verifast")
SETUP_CODES = {124, 125, 126, 127, 134, 137, 139}
CAMPAIGN = "r19-unwind-controls-v1"
RESULT_SCHEMA = "r19-unwind-controls-result-v1"
CALL = b"    insert_tail(begin, begin.add(2), is_less);\n"
R19_AFTER = (b"    /*@ { r19_insert_tail_unwind_cleanup();\n"
             b"        assert array::<u64>(begin, 3, ?r16_normal_current);\n"
             b"        r9_drop_u64_owners(t, r16_normal_current);\n"
             b"        array_to_array_(begin); } @*/\n")
R18_AFTER = (b"    /*@ { assert array::<u64>(begin, 3, ?r16_normal_current);\n"
             b"        r9_drop_u64_owners(t, r16_normal_current);\n"
             b"        array_to_array_(begin); } @*/\n")
NO_OWNER_DROP_AFTER = (b"    /*@ { r19_insert_tail_unwind_cleanup();\n"
                       b"        assert array::<u64>(begin, 3, ?r16_normal_current);\n"
                       b"        array_to_array_(begin); } @*/\n")
WRAPPER = b"pub unsafe fn b2_three_from_local"
KEEP_TYPE = (b"\npub struct R19Keep;\n\n"
             b"impl Drop for R19Keep {\n"
             b"    fn drop(&mut self) {}\n"
             b"}\n")
KEEP_LOCAL = b"    let r19_keep = R19Keep;\n"
OTHER_FUNCTION = (b"\npub unsafe fn r19_other_function()\n"
                  b"/*@ req true; @*/ /*@ ens true; @*/\n"
                  b"{\n"
                  b"    /*@ { r19_insert_tail_unwind_cleanup();\n"
                  b"        assert array::<u64>(begin, 3, ?r16_normal_current);\n"
                  b"        r9_drop_u64_owners(t, r16_normal_current);\n"
                  b"        array_to_array_(begin); } @*/\n"
                  b"}\n")
OTHER_MARKER = b"\n{\n    /*@ { r19_insert_tail_unwind_cleanup();\n"
DIAGNOSTICS = {
    "missing_marker": "No matching heap chunks: array_<u64>(values_addr, 3, _)",
    "displaced_marker": "R19 cleanup marker did not follow insert_tail",
    "other_function": "R19 cleanup marker outside b2_three_from_local",
    "cleanup_edge": "R19 cleanup needs a Continue insert_tail call",
    "missing_owner_drop": "R19 cleanup block shape mismatch",
}
CASES = tuple(DIAGNOSTICS)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _replace(data: bytes, old: bytes, new: bytes) -> bytes:
    if data.count(old) != 1:
        raise ValueError("R19 control source anchor is missing or ambiguous")
    return data.replace(old, new, 1)


def _line_at(data: bytes, offset: int) -> int:
    return data[:offset].count(b"\n") + 1


def _unique_offset(data: bytes, anchor: bytes) -> int:
    if data.count(anchor) != 1:
        raise ValueError("R19 control target anchor is missing or ambiguous")
    return data.index(anchor)


def _variants(original: bytes, verified: bytes) -> dict:
    if (verified.count(CALL + R19_AFTER) != 1 or verified.count(WRAPPER) != 1 or
            original.count(CALL) != 1 or verified.count(b"R19Keep") or
            verified.count(b"r19_other_function")):
        raise ValueError("R19 controls require the exact marked raw caller")
    wrapper_at = verified.index(WRAPPER)
    if verified.index(CALL + R19_AFTER) < wrapper_at:
        raise ValueError("R19 marked call is outside the raw wrapper")
    out = {}
    missing = _replace(verified, CALL + R19_AFTER, CALL + R18_AFTER)
    close = _unique_offset(missing, CALL + R18_AFTER + b"}\n") + len(CALL + R18_AFTER)
    out["missing_marker"] = (original, missing, _line_at(missing, close))
    displaced = _replace(verified, CALL + R19_AFTER, CALL + b"\n" + R19_AFTER)
    out["displaced_marker"] = (original, displaced,
                               _line_at(displaced, _unique_offset(displaced, CALL + b"\n" + R19_AFTER)) + 2)
    other = verified + OTHER_FUNCTION
    out["other_function"] = (original + b"\npub unsafe fn r19_other_function()\n{\n}\n", other,
                             _line_at(other, _unique_offset(other, OTHER_MARKER)) + 2)
    keep_original = _replace(original, CALL, KEEP_LOCAL + CALL) + KEEP_TYPE
    keep_verified = _replace(verified, CALL + R19_AFTER, KEEP_LOCAL + CALL + R19_AFTER) + KEEP_TYPE
    out["cleanup_edge"] = (keep_original, keep_verified,
                           _line_at(keep_verified, _unique_offset(keep_verified, CALL + R19_AFTER)))
    no_drop = _replace(verified, CALL + R19_AFTER, CALL + NO_OWNER_DROP_AFTER)
    out["missing_owner_drop"] = (original, no_drop,
                                 _line_at(no_drop, _unique_offset(no_drop, CALL + NO_OWNER_DROP_AFTER)) + 1)
    return out


def _target_binding(name: str, line: int, log: str) -> dict:
    expected = DIAGNOSTICS[name]
    located = f"lib.rs({line},"
    message_lines = sorted({entry.strip() for entry in log.splitlines() if expected in entry})
    exact = [entry for entry in message_lines if located in entry]
    return {"admitted": len(exact) == 1 and len(message_lines) == 1,
            "expected_diagnostic": expected, "expected_line": line,
            "message_line_count": len(message_lines), "exact_line_count": len(exact),
            "diagnostic_lines": message_lines[:4]}


def _outcome(name: str, classification: str, reason: str, **fields) -> dict:
    return {"schema": RESULT_SCHEMA, "case": name, "classification": classification,
            "reason": reason, "matched": False, "accepted": False,
            "proof_credit": False, "b2_achieved": False, **fields}


def _classify(case: Path, name: str, expected_hashes: dict, execution, line: int,
              consumer) -> dict:
    if type(execution) is not dict:
        return _outcome(name, "INCONCLUSIVE", "executor returned the wrong type",
                        execution_type=type(execution).__name__)
    if execution.get("exception") is not None:
        return _outcome(name, "INCONCLUSIVE", "executor raised an exception",
                        execution_exception=execution.get("exception"),
                        execution_status=execution.get("status"))
    if execution.get("status") == "NOT_RUN" or execution.get("classification") == "NOT_RUN":
        return _outcome(name, "NOT_RUN", "executor explicitly marked the control NOT_RUN",
                        execution_status=execution.get("status"))
    stages = execution.get("stages")
    if type(stages) is not dict or any(type(stages.get(stage)) is not int or
                                       type(stages.get(stage)) is bool for stage in STAGES):
        return _outcome(name, "INCONCLUSIVE", "typed stage result map is missing or malformed",
                        stages=stages if type(stages) is dict else None)
    actual_hashes = consumer._hashes(case)
    if any(actual_hashes.get(key) != value for key, value in expected_hashes.items()):
        return _outcome(name, "INCONCLUSIVE", "source hashes changed or mismatched",
                        source_hashes=actual_hashes)
    gate = execution.get("stage_receipt_gate")
    if (execution.get("source_unchanged_at_every_stage") is not True or type(gate) is not dict or
            gate.get("admitted") is not True):
        return _outcome(name, "INCONCLUSIVE", "typed source/stage receipts did not match",
                        stages=stages, source_hashes=actual_hashes)
    if any(code in SETUP_CODES for code in stages.values()):
        return _outcome(name, "INCONCLUSIVE", "a stage timed out, was skipped or failed setup",
                        stages=stages)
    log_path = case / "verifast.log"
    log = log_path.read_text(errors="replace") if log_path.is_file() else ""
    binding = _target_binding(name, line, log)
    matched = (stages["exporter"] == 0 and stages["decode"] == 0 and
               stages["verifast"] != 0 and binding["admitted"])
    return _outcome(name, "EXPECTED_VERIFAST_REFUSAL" if matched else "INCONCLUSIVE",
                    "exact verifier refusal matched its source-bound control line" if matched else
                    "diagnostic, line, or typed stage identity did not match",
                    matched=matched, target_binding=binding, stages=stages,
                    source_hashes=actual_hashes)


def run(evidence, raw_case, args, dispatch, consumer, selected_profile, *, source_sha256):
    root = Path(evidence) / "r19-unwind-controls"
    root.mkdir(parents=True, exist_ok=False)
    if type(source_sha256) is not str or re.fullmatch(r"[0-9a-f]{64}", source_sha256) is None:
        raise ValueError("pinned campaign source SHA-256 is absent")
    raw_case = Path(raw_case)
    variants = _variants((raw_case / "original/lib.rs").read_bytes(),
                         (raw_case / "verified/lib.rs").read_bytes())
    results = {}
    for name in CASES:
        original, verified, line = variants[name]
        case = root / "cases" / name
        (case / "original").mkdir(parents=True)
        (case / "verified").mkdir()
        (case / "original/lib.rs").write_bytes(original)
        (case / "verified/lib.rs").write_bytes(verified)
        hashes = {"original/lib.rs": _sha(original), "verified/lib.rs": _sha(verified),
                  "small_sort_source": source_sha256}
        record = {"schema": CAMPAIGN, "profile": selected_profile, "case": name,
                  "raw_caller_case": str(raw_case.resolve()),
                  "raw_caller_verified_sha256": _sha((raw_case / "verified/lib.rs").read_bytes()),
                  "source_hashes": hashes, "expected_line": line,
                  "expected_diagnostic": DIAGNOSTICS[name],
                  "accepted": False, "proof_credit": False}
        (case / "case.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
        before = consumer._hashes(case)
        previous_r8 = getattr(args, "r8_owned_array_allocation", False)
        args.r8_owned_array_allocation = True
        try:
            execution = dispatch(case, args, actual_callback_case=True, body_isolation_native=True)
        except Exception as error:
            execution = {"exception": {"type": type(error).__name__, "message": str(error)},
                         "status": "FAILED", "stages": None}
        finally:
            args.r8_owned_array_allocation = previous_r8
        if type(execution) is dict:
            stages = execution.get("stages")
            execution["stage_receipt_gate"] = consumer._stage_receipts(
                case, stages if type(stages) is dict else {}, before)
            execution["source_unchanged_at_every_stage"] = (
                before == consumer._hashes(case) and
                execution["stage_receipt_gate"].get("admitted") is True)
        (case / "execution.json").write_text(
            json.dumps(execution, indent=2, sort_keys=True, default=str) + "\n")
        result = _classify(case, name, hashes, execution, line, consumer)
        (case / "classification.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        results[name] = result
    all_matched = all(result.get("matched") is True for result in results.values())
    aggregate = {"schema": RESULT_SCHEMA, "campaign": CAMPAIGN, "profile": selected_profile,
                 "cases": results, "all_matched": all_matched,
                 "classification": "ALL_R19_UNWIND_CONTROLS_MATCHED" if all_matched else
                                   "R19_UNWIND_CONTROLS_INCONCLUSIVE",
                 "accepted": False, "proof_credit": False, "b2_achieved": False,
                 "independent_credit": False}
    (root / "result.json").write_text(json.dumps(aggregate, indent=2, sort_keys=True) + "\n")
    return aggregate
