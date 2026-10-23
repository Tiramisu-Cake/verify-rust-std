#!/usr/bin/env python3
"""Source-bound distinguishing controls for the R19 insert_tail unwind cleanup."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys


STAGES = ("exporter", "decode", "refinement", "verifast")
SETUP_CODES = {124, 125, 126, 127, 134, 137, 139}
CAMPAIGN = "r19-unwind-controls-v1"
RESULT_SCHEMA = "r19-unwind-controls-result-v1"
SYNTHETIC_CASE = "synthetic_unwind_resource"
SYNTHETIC_DIAGNOSTIC = "No matching heap chunks for array<u64> of length 4"
SYNTHETIC_TRACE_RE = re.compile(
    r"^\s*\d+(?:\.\d+)?s: [^\s(]+\([0-9]+,[0-9]+"
    r"(?:-[0-9]+(?:,[0-9]+)?)?\): Verifying function '([^']+)'$", re.M)
NATIVE_CALL_TRACE = r"(?:Verifying function call|Verifying call)"
SOURCE_TRACE_PREFIX = r"verified/lib\.rs\({line},\d+(?:-\d+(?:,\d+)?)?\): "
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


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"missing pinned source helper: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _parent_raw_preparation(raw_case: Path, callback) -> tuple[dict | None, str | None]:
    prep_path = raw_case.parents[1] / "preparation.json"
    try:
        data = prep_path.read_bytes()
        record = json.loads(data)
        original = (raw_case / "original/lib.rs").read_bytes()
        verified = (raw_case / "verified/lib.rs").read_bytes()
        if (type(record) is not dict or record.get("case") != callback.RAW_LOCAL_CALLER_NAME or
                record.get("original_sha256") != _sha(original) or
                record.get("verified_sha256") != _sha(verified)):
            return None, None
        return record, _sha(data)
    except (OSError, ValueError, KeyError, TypeError):
        return None, None


def _synthetic_unwind_pair(callback, body) -> tuple[bytes, bytes, dict]:
    """Build a proof-only always-panicking callee and an exact R19 caller."""
    original_suffix, verified_suffix = callback._raw_local_caller_suffixes(body)
    synthetic_after = R19_AFTER.replace(b"array::<u64>(begin, 3,", b"array::<u64>(begin, 4,")
    if synthetic_after == R19_AFTER or verified_suffix.count(CALL + R19_AFTER) != 1:
        raise ValueError("synthetic unwind fixture lost the exact R19 marker anchor")
    verified_suffix = _replace(verified_suffix, CALL + R19_AFTER, CALL + synthetic_after)

    signature = (b"unsafe fn insert_tail<F: FnMut(&u64, &u64) -> bool>"
                 b"(begin: *mut u64, tail: *mut u64, is_less: &mut F)")
    contract = (b"/*@\n"
                b"req thread_token(?t) &*& t == currentThread &*&\n"
                b"    type_interp::<u64>() &*& type_interp::<F>() &*&\n"
                b"    begin[..3] |-> ?xs &*& length(xs) == 3 &*&\n"
                b"    foreach(xs, own::<u64>(t)) &*& tail == begin + 2 &*&\n"
                b"    *is_less |-> ?f0 &*& <F>.own(t, f0);\n"
                b"@*//*@\nens false;\n@*//*@\n"
                b"on_unwind_ens thread_token(t) &*& type_interp::<u64>() &*&\n"
                b"    type_interp::<F>() &*& begin[..3] |-> ?panic_current &*&\n"
                b"    length(panic_current) == 3 &*&\n"
                b"    foreach(panic_current, own::<u64>(t)) &*&\n"
                b"    tail == begin + 2 &*& *is_less |-> ?panic_f &*&\n"
                b"    <F>.own(t, panic_f);\n@*/\n")
    panic_call = b'    core::panicking::panic("explicit panic");'
    callee_original = signature + b"\n{\n" + panic_call + b"\n}\n\n"
    callee_verified = signature + b"\n" + contract + b"{\n" + panic_call + b"\n}\n\n"

    helper = callback._raw_owner_lemma_body()
    wrapper_at = verified_suffix.index(body.WRAPPER_SIGNATURE)
    verified_suffix = (verified_suffix[:wrapper_at] + helper + verified_suffix[wrapper_at:])
    crate_header = b"#![no_std]\n#![feature(panic_internals)]\n"
    original = crate_header + callee_original + original_suffix
    verified = crate_header + callee_verified + verified_suffix
    call_line = _line_at(verified, _unique_offset(verified, CALL))
    marker_assert = b"        assert array::<u64>(begin, 4, ?r16_normal_current);"
    marker_line = _line_at(verified, _unique_offset(verified, marker_assert))
    panic_line = _line_at(verified, _unique_offset(verified, panic_call))
    if callback._body_runtime_equal(original, verified) is not True:
        raise ValueError("synthetic source pair changes runtime behavior")
    if (b"ens false;" not in verified or b"on_unwind_ens thread_token(t)" not in verified or
            verified.count(panic_call) != 1 or original.count(panic_call) != 1 or
            b"core::panic!" in original or b"core::panic!" in verified or
            b"assume" in verified or b"leak" in verified):
        raise ValueError("synthetic callee contract or checked-source gate changed")
    return original, verified, {"call_line": call_line, "marker_line": marker_line,
                                "panic_line": panic_line}


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
    return {"admitted": len(exact) == 1,
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


def _synthetic_trace(log: str, function: str) -> list[tuple[int, int, str]]:
    headers = list(SYNTHETIC_TRACE_RE.finditer(log))
    found = []
    for index, header in enumerate(headers):
        if header.group(1) == function:
            end = headers[index + 1].start() if index + 1 < len(headers) else len(log)
            found.append((header.start(), end, log[header.start():end]))
    return found


def _classify_synthetic(case: Path, expected_hashes: dict, execution: object,
                        lines: dict, consumer) -> dict:
    name = SYNTHETIC_CASE
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
    expected_route = {
        "actual_callback_case": False,
        "body_isolation_native": False,
        "first_fnmut_continue": False,
        "r8_owned_array_allocation": True,
        "refinement_argv": {"omit": ["--check-first-fnmut-continue"]},
        "verifier_argv": {"include": ["-rust_owned_array_allocation_r8"]},
        "case_environment": {key: "removed" for key in (
            "SMALLSORT_R9_GUARD_TRACE",
            "SMALLSORT_R9_GUARD_RETURN_RECOVERY",
            "SMALLSORT_R11_LABEL_STORAGE_TRACE",
            "SMALLSORT_R11_LABEL_STORAGE_PLACEMENT",
        )},
        "r11_native_receipt_argument": "absent",
    }
    try:
        recorded_route = json.loads((case / "case.json").read_text()).get("execution_route")
    except Exception:
        recorded_route = None
    if recorded_route != expected_route or execution.get("synthetic_execution_route") != expected_route:
        return _outcome(name, "INCONCLUSIVE", "synthetic per-case execution route is absent or changed",
                        stages=stages, execution_route=recorded_route,
                        observed_execution_route=execution.get("synthetic_execution_route"))
    actual_hashes = consumer._hashes(case)
    if any(actual_hashes.get(key) != value for key, value in expected_hashes.items()):
        return _outcome(name, "INCONCLUSIVE", "synthetic source hashes changed or mismatched",
                        source_hashes=actual_hashes)
    gate = execution.get("stage_receipt_gate")
    if (execution.get("source_unchanged_at_every_stage") is not True or type(gate) is not dict or
            gate.get("admitted") is not True):
        return _outcome(name, "INCONCLUSIVE", "typed source/stage receipts did not match",
                        stages=stages, source_hashes=actual_hashes)
    parent_gate = execution.get("parent_raw_preparation_gate")
    if type(parent_gate) is not dict or parent_gate.get("admitted") is not True:
        return _outcome(name, "INCONCLUSIVE", "parent raw-caller preparation identity changed",
                        stages=stages, source_hashes=actual_hashes,
                        parent_raw_preparation_gate=parent_gate)
    if any(code in SETUP_CODES for code in stages.values()):
        return _outcome(name, "INCONCLUSIVE", "a stage timed out, was skipped or failed setup",
                        stages=stages)

    log_path = case / "verifast.log"
    log = log_path.read_text(errors="replace") if log_path.is_file() else ""
    errors = [entry for entry in log.splitlines()
              if re.search(r"\berror:", entry, re.I)]
    dead = [entry for entry in log.splitlines()
            if re.search(r"dead code", entry, re.I)]
    callee = _synthetic_trace(log, "insert_tail")
    caller = _synthetic_trace(log, "b2_three_from_local")
    caller_segment = caller[0][2] if len(caller) == 1 else ""
    callee_segment = callee[0][2] if len(callee) == 1 else ""
    ordered_headers = (len(callee) == 1 and len(caller) == 1 and
                       callee[0][0] < caller[0][0])

    target_line = lines["marker_line"]
    target_errors = [entry for entry in errors if
                     re.search(rf"verified/lib\.rs\({target_line},\d+(?:-\d+)?\): error:", entry)]
    resource_message = (len(target_errors) == 1 and
                        "No matching heap chunks" in target_errors[0] and
                        re.search(r"array(?:::<u64>|<u64>)?\([^\n]*,\s*4,\s*_\)",
                                  target_errors[0]) is not None)
    callee_called = (re.search(
        SOURCE_TRACE_PREFIX.format(line=lines["panic_line"]) +
        rf"(?:note: )?{NATIVE_CALL_TRACE}$",
        callee_segment, re.M) is not None)
    caller_call = (re.search(
        SOURCE_TRACE_PREFIX.format(line=lines["call_line"]) +
        rf"(?:note: )?{NATIVE_CALL_TRACE}$", caller_segment, re.M) is not None)
    target_trace_count = len(re.findall(
        rf"verified/lib\.rs\({target_line},\d+[^\n]*\): (?:note: )?Executing statement",
        caller_segment))
    target_executed = target_trace_count >= 1
    only_target_error = (len(errors) == 1 and len(target_errors) == 1 and
                         errors[0] == target_errors[0] and
                         target_errors[0] in caller_segment and target_errors[0] not in callee_segment)
    matched = (stages["exporter"] == 0 and stages["decode"] == 0 and
               stages["refinement"] == 0 and stages["verifast"] != 0 and
               ordered_headers and not dead and only_target_error and resource_message and
               callee_called and caller_call and target_executed)
    reason = ("callee and caller traces reached the exact synthetic unwind resource refusal"
              if matched else
              "the callee proof, wrapper unwind trace, exact resource diagnostic, or stage gate did not match")
    return _outcome(name, "EXPECTED_SYNTHETIC_RESOURCE_REFUSAL" if matched else "INCONCLUSIVE",
                    reason, matched=matched, stages=stages, source_hashes=actual_hashes,
                    verifier_errors=errors, verifier_dead_code=dead,
                    callee_header_count=len(callee), caller_header_count=len(caller),
                    callee_body_trace=callee_called, caller_call_trace=caller_call,
                    target_line=target_line, target_executed=target_executed,
                    target_trace_count=target_trace_count,
                    target_error_count=len(target_errors), resource_message=resource_message)


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

    synthetic_root = root / SYNTHETIC_CASE
    synthetic_case = synthetic_root / "cases" / SYNTHETIC_CASE
    synthetic_setup_error = None
    try:
        callback = _load_module("r19_synthetic_callback", Path(__file__).with_name("first-callback.py"))
        body = _load_module("r19_synthetic_b2", Path(__file__).with_name("actual-insert-tail-b2.py"))
        parent_record, parent_preparation_sha = _parent_raw_preparation(raw_case, callback)
    except Exception as error:
        synthetic_setup_error = {"type": type(error).__name__, "message": str(error)}
        parent_record = parent_preparation_sha = None
    (synthetic_case / "original").mkdir(parents=True)
    (synthetic_case / "verified").mkdir()
    if synthetic_setup_error is not None:
        synthetic_result = _outcome(
            SYNTHETIC_CASE, "INCONCLUSIVE",
            "synthetic control setup/import raised an exception",
            setup_exception=synthetic_setup_error,
            parent_raw_caller_case=str(Path(raw_case).resolve()))
        (synthetic_case / "classification.json").write_text(
            json.dumps(synthetic_result, indent=2, sort_keys=True) + "\n")
        lines = None
        original = verified = b""
    elif parent_record is None or parent_preparation_sha is None:
        synthetic_result = _outcome(
            SYNTHETIC_CASE, "INCONCLUSIVE",
            "matching actual raw-caller preparation record is absent or changed",
            parent_raw_caller_case=str(Path(raw_case).resolve()))
        (synthetic_case / "classification.json").write_text(
            json.dumps(synthetic_result, indent=2, sort_keys=True) + "\n")
        lines = None
        original = verified = b""
    else:
        try:
            original, verified, lines = _synthetic_unwind_pair(callback, body)
        except Exception as error:
            synthetic_result = _outcome(
                SYNTHETIC_CASE, "INCONCLUSIVE",
                "synthetic source fixture could not be constructed",
                construction_error={"type": type(error).__name__, "message": str(error)},
                parent_raw_caller_case=str(Path(raw_case).resolve()))
            (synthetic_case / "classification.json").write_text(
                json.dumps(synthetic_result, indent=2, sort_keys=True) + "\n")
            original = verified = b""
            lines = None
        if lines is None:
            pass
        else:
            (synthetic_case / "original/lib.rs").write_bytes(original)
            (synthetic_case / "verified/lib.rs").write_bytes(verified)
            source_hashes = {"original/lib.rs": _sha(original),
                             "verified/lib.rs": _sha(verified),
                             "small_sort_source": source_sha256}
            case_record = {
                "schema": "r19-synthetic-unwind-resource-v1",
                "profile": selected_profile,
                "case": SYNTHETIC_CASE,
                "control_kind": "synthetic_always_panicking_callee_resource_negative",
                "execution_route": {
                    "actual_callback_case": False,
                    "body_isolation_native": False,
                    "first_fnmut_continue": False,
                    "r8_owned_array_allocation": True,
                    "refinement_argv": {"omit": ["--check-first-fnmut-continue"]},
                    "verifier_argv": {"include": ["-rust_owned_array_allocation_r8"]},
                    "case_environment": {key: "removed" for key in (
                        "SMALLSORT_R9_GUARD_TRACE",
                        "SMALLSORT_R9_GUARD_RETURN_RECOVERY",
                        "SMALLSORT_R11_LABEL_STORAGE_TRACE",
                        "SMALLSORT_R11_LABEL_STORAGE_PLACEMENT",
                    )},
                    "r11_native_receipt_argument": "absent",
                },
                "actual_raw_caller_case": str(Path(raw_case).resolve()),
                "actual_raw_caller_preparation_sha256": parent_preparation_sha,
                "actual_raw_caller_preparation_case": parent_record.get("case"),
                "actual_raw_caller_original_sha256": parent_record.get("original_sha256"),
                "actual_raw_caller_verified_sha256": parent_record.get("verified_sha256"),
                "source_hashes": source_hashes,
                "call_line": lines["call_line"], "marker_line": lines["marker_line"],
                "panic_line": lines["panic_line"],
                "expected_diagnostic": SYNTHETIC_DIAGNOSTIC,
                "accepted": False, "proof_credit": False, "b2_achieved": False,
            }
            (synthetic_case / "case.json").write_text(
                json.dumps(case_record, indent=2, sort_keys=True) + "\n")
            before = consumer._hashes(synthetic_case)
            synthetic_args = copy.copy(args)
            synthetic_args.r8_owned_array_allocation = True
            # This synthetic callee intentionally lacks insert_tail's
            # comparison body. Do not ask the actual-callback source gate or
            # R11 invariant-placement transformation to process it. The actual
            # R19 cases above and their flags remain unchanged.
            synthetic_args.first_fnmut_continue = False
            try:
                execution = dispatch(synthetic_case, synthetic_args, actual_callback_case=False,
                                     body_isolation_native=False)
            except Exception as error:
                execution = {"exception": {"type": type(error).__name__, "message": str(error)},
                             "status": "FAILED", "stages": None}
            if type(execution) is dict:
                execution["synthetic_execution_route"] = case_record["execution_route"]
                stages = execution.get("stages")
                execution["stage_receipt_gate"] = consumer._stage_receipts(
                    synthetic_case, stages if type(stages) is dict else {}, before)
                execution["source_unchanged_at_every_stage"] = (
                    before == consumer._hashes(synthetic_case) and
                    execution["stage_receipt_gate"].get("admitted") is True)
                current_record, current_sha = _parent_raw_preparation(raw_case, callback)
                execution["parent_raw_preparation_gate"] = {
                    "admitted": current_record == parent_record and
                               current_sha == parent_preparation_sha,
                    "preparation_sha256": current_sha,
                    "case": current_record.get("case") if current_record else None,
                }
            (synthetic_case / "execution.json").write_text(
                json.dumps(execution, indent=2, sort_keys=True, default=str) + "\n")
            synthetic_result = _classify_synthetic(
                synthetic_case, source_hashes, execution, lines, consumer)
            (synthetic_case / "classification.json").write_text(
                json.dumps(synthetic_result, indent=2, sort_keys=True) + "\n")

    aggregate = {"schema": RESULT_SCHEMA, "campaign": CAMPAIGN, "profile": selected_profile,
                 "cases": results, "all_matched": all_matched,
                 "classification": "ALL_R19_UNWIND_CONTROLS_MATCHED" if all_matched else
                                   "R19_UNWIND_CONTROLS_INCONCLUSIVE",
                 "synthetic_unwind_resource": synthetic_result,
                 "accepted": False, "proof_credit": False, "b2_achieved": False,
                 "independent_credit": False}
    (root / "result.json").write_text(json.dumps(aggregate, indent=2, sort_keys=True) + "\n")
    return aggregate
