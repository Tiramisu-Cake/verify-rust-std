#!/usr/bin/env python3
"""Isolated, source-bound RawPtr controls for the R17 refiner."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re


STAGES = ("exporter", "decode", "refinement", "verifast")
SETUP_CODES = {124, 125, 126, 127, 134, 137, 139}
CAMPAIGN = "r17-rawptr-controls-v1"
RESULT_SCHEMA = "r17-rawptr-controls-result-v1"
CONTROL_FUNCTION = "r17_rawptr_control"
VALUES = b"let mut values = [10_u64, 20_u64, 5_u64];"
RAW_MUT = b"let begin = &raw mut values as *mut [u64; 3];"
BASE = (b"#![no_std]\n"
        b"pub unsafe fn r17_rawptr_control() -> *mut [u64; 3]\n"
        b"/*@ req true; @*/ /*@ ens true; @*/ {\n"
        b"    let mut values = [10_u64, 20_u64, 5_u64];\n"
        b"    let begin = &raw mut values as *mut [u64; 3];\n"
        b"    begin\n}\n")
DIAGNOSTICS = {
    "mutability_mismatch": "RawPtr: mutabilities do not match",
    "changed_local_contents": (
        "The states of the two locals values and values whose address is taken are not equal"),
    "unsupported_index_projection": "RawPtr: projected places are not supported",
    "raw_ref_cross_kind": "Command kinds do not match",
}
CASES = ("identical_local_rawmut", "mutability_mismatch",
         "changed_local_contents", "unsupported_index_projection",
         "raw_ref_cross_kind")


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _line(data: bytes, anchor: bytes) -> int:
    matches = [m.start() for m in re.finditer(re.escape(anchor), data)]
    if len(matches) != 1:
        raise ValueError("control source target is missing or ambiguous")
    return data[:matches[0]].count(b"\n") + 1


def _replace(data: bytes, old: bytes, new: bytes) -> bytes:
    if data.count(old) != 1:
        raise ValueError("control source anchor is missing or ambiguous")
    return data.replace(old, new, 1)


def _variants():
    return {
        "identical_local_rawmut": (BASE, RAW_MUT),
        "mutability_mismatch": (_replace(BASE, RAW_MUT,
            b"let begin = &raw const values as *const [u64; 3] as *mut [u64; 3];"),
            b"let begin = &raw const values"),
        "changed_local_contents": (_replace(BASE, VALUES,
            b"let mut values = [11_u64, 20_u64, 5_u64];"), RAW_MUT),
        "unsupported_index_projection": (_replace(BASE, RAW_MUT,
            b"let begin = &raw mut values[0] as *mut u64 as *mut [u64; 3];"),
            b"let begin = &raw mut values[0]"),
        "raw_ref_cross_kind": (_replace(BASE, RAW_MUT,
            b"let begin = &mut values as *mut [u64; 3];"),
            b"let begin = &mut values"),
    }


def _run_logs(case: Path) -> list[tuple[str, str]]:
    found = []
    for filename in ("refinement.log", "refinement.out", "refinement.out1", "refinement.err"):
        path = case / filename
        if path.is_file():
            found.append((filename, path.read_text(errors="replace")))
    return found


def _target_binding(name: str, source: bytes, anchor: bytes, logs) -> dict:
    text = "\n".join(content for _, content in logs)
    expected = DIAGNOSTICS.get(name)
    if name == "changed_local_contents":
        exact = [line for line in text.splitlines() if line.strip().endswith(expected)]
        local_names = len(exact) == 1
        function_bound = local_names
        command_listing = True
        cross_kind_listing = True
    else:
        exact = [line for line in text.splitlines()
                 if expected is not None and line.strip().endswith(expected)]
        function_bound = CONTROL_FUNCTION in text
        command_listing = ("Commands of basic block" in text and "RawPtr" in text)
        cross_kind_listing = name != "raw_ref_cross_kind" or "Ref" in text
    # The refiner reports MIR basic-block command coordinates, not Rust source
    # line numbers. Bind the exact source/hash to its sole RawPtr expression,
    # then require the diagnostic block for this isolated function to expose
    # the corresponding command listing. Missing context remains inconclusive.
    admitted = (len(exact) == 1 and function_bound and command_listing and
                cross_kind_listing and _line(source, anchor) > 0)
    return {"admitted": admitted, "function": CONTROL_FUNCTION,
            "source_target_anchor": anchor.decode("ascii"),
            "source_target_line": _line(source, anchor),
            "source_target_unique": source.count(anchor) == 1,
            "exact_diagnostic_count": len(exact),
            "function_context_present": function_bound,
            "local_names_bound": (local_names if name == "changed_local_contents" else None),
            "command_listing_present": command_listing,
            "cross_kind_listing_present": cross_kind_listing,
            "diagnostic_lines": exact,
            "diagnostic_files": [filename for filename, _ in logs]}


def _strict_stage_gate(case: Path, stages, source_hashes: dict,
                       consumer_gate: dict, name: str) -> dict:
    rows = {}
    valid = type(stages) is dict and type(consumer_gate) is dict and consumer_gate.get("admitted") is True
    for index, stage in enumerate(STAGES):
        path = case / f"{stage}-stage.json"
        row = {"admitted": False, "reason": "stage receipt is absent"}
        if path.is_file():
            try:
                receipt = json.loads(path.read_text())
                code = stages.get(stage) if type(stages) is dict else None
                before, after = receipt.get("source_before"), receipt.get("source_after")
                status = receipt.get("status")
                source_ok = (type(before) is dict and before == source_hashes and
                             after == source_hashes and receipt.get("source_unchanged") is True)
                typed = (type(code) is int and type(code) is not bool and
                         type(receipt.get("exit_code")) is int and
                         type(receipt.get("exit_code")) is not bool and
                         receipt.get("exit_code") == code)
                status_ok = status is None or (type(status) is str and
                                               status in {"SUCCESS", "SUCCEEDED", "COMPLETED"})
                if name == "identical_local_rawmut":
                    semantic_ok = (code == 0 if stage in ("exporter", "decode", "refinement")
                                   else code not in SETUP_CODES)
                elif stage in ("exporter", "decode"):
                    semantic_ok = code == 0
                elif stage == "refinement":
                    semantic_ok = code not in (None, 0) and code not in SETUP_CODES
                else:
                    semantic_ok = code not in (None, *SETUP_CODES)
                admitted = (type(receipt) is dict and receipt.get("stage") == stage and
                            source_ok and typed and status_ok and semantic_ok)
                row = {"admitted": admitted, "exit_code": code if type(code) is int else None,
                       "status": status if type(status) is str else None,
                       "source_identity_matches": source_ok, "typed_exit_matches": typed,
                       "successful_stage_wrapper": status_ok,
                       "required_stage_result_matches": semantic_ok}
            except (OSError, json.JSONDecodeError, AttributeError, TypeError) as error:
                row = {"admitted": False,
                       "reason": f"invalid stage receipt: {type(error).__name__}: {error}"}
        rows[stage] = row
        valid = valid and row["admitted"]
    return {"admitted": bool(valid), "consumer_gate": consumer_gate, "stages": rows}


def _outcome(name: str, classification: str, reason: str, **fields) -> dict:
    return {"schema": RESULT_SCHEMA, "case": name, "classification": classification,
            "reason": reason, "matched": False, "accepted": False,
            "proof_credit": False, "b2_achieved": False, **fields}


def _classify(case: Path, name: str, expected_hashes: dict,
              execution, anchor: bytes, consumer) -> dict:
    if type(execution) is not dict:
        return _outcome(name, "INCONCLUSIVE", "executor returned the wrong type",
                        execution_type=type(execution).__name__)
    if execution.get("exception") is not None:
        return _outcome(name, "INCONCLUSIVE", "executor raised an exception",
                        execution_exception=execution.get("exception"),
                        execution_status=execution.get("status"))
    if execution.get("status") == "NOT_RUN" or execution.get("classification") == "NOT_RUN":
        return _outcome(name, "NOT_RUN", "executor explicitly marked the control NOT_RUN",
                        execution_status=execution.get("status"),
                        execution_classification=execution.get("classification"))
    stages = execution.get("stages")
    if type(stages) is not dict:
        return _outcome(name, "INCONCLUSIVE", "typed stage result map is missing or malformed",
                        execution_status=execution.get("status"))
    actual_hashes = consumer._hashes(case)
    files_match = all(actual_hashes.get(key) == value for key, value in expected_hashes.items())
    if not files_match:
        return _outcome(name, "INCONCLUSIVE", "source hashes changed or mismatched",
                        source_hashes=actual_hashes)
    consumer_gate = consumer._stage_receipts(case, stages, actual_hashes)
    stage_gate = _strict_stage_gate(case, stages, actual_hashes, consumer_gate, name)
    if execution.get("source_unchanged_at_every_stage") is not True or not stage_gate["admitted"]:
        return _outcome(name, "INCONCLUSIVE", "typed source/stage receipts did not match",
                        stages=stages, source_hashes=actual_hashes,
                        stage_receipt_gate=stage_gate)
    source = (case / "verified/lib.rs").read_bytes()
    binding = _target_binding(name, source, anchor, _run_logs(case))
    if name == "identical_local_rawmut":
        matched = (binding["source_target_unique"] and
                   all(stages[stage] == 0 for stage in ("exporter", "decode", "refinement")))
        return _outcome(name, "RAW_LOCAL_RAWMUT_MATCHED" if matched else "INCONCLUSIVE",
                        "identical local rawmut pair passed source, refinement and stage gates" if matched else
                        "positive local rawmut pair did not pass its required gates",
                        matched=matched, target_binding=binding, stages=stages,
                        stage_receipt_gate=stage_gate, source_hashes=actual_hashes)
    matched = binding["admitted"] and stages["refinement"] not in (0, *SETUP_CODES)
    return _outcome(name, "EXPECTED_REFINER_REFUSAL" if matched else "INCONCLUSIVE",
                    "exact refiner refusal matched the isolated function and command target" if matched else
                    "diagnostic, command target, or typed stage identity did not match",
                    matched=matched, target_binding=binding, stages=stages,
                    stage_receipt_gate=stage_gate, source_hashes=actual_hashes)


def run(evidence, args, env, dispatch, consumer, selected_profile, *, source_sha256):
    """Run tiny RawPtr-only functions through the existing Cloud dispatch."""
    root = Path(evidence) / "r17-rawptr-controls"
    root.mkdir(parents=True, exist_ok=False)
    if type(source_sha256) is not str or re.fullmatch(r"[0-9a-f]{64}", source_sha256) is None:
        raise ValueError("pinned campaign source SHA-256 is absent")
    results = {}
    for name, (verified, anchor) in _variants().items():
        case = root / "cases" / name
        (case / "original").mkdir(parents=True)
        (case / "verified").mkdir()
        (case / "original/lib.rs").write_bytes(BASE)
        (case / "verified/lib.rs").write_bytes(verified)
        hashes = {"original/lib.rs": _sha(BASE), "verified/lib.rs": _sha(verified),
                  "small_sort_source": source_sha256}
        target = {"function": CONTROL_FUNCTION, "anchor": anchor.decode("ascii"),
                  "line": _line(verified, anchor)}
        record = {"schema": CAMPAIGN, "profile": selected_profile, "case": name,
                  "source_sha256": source_sha256, "source_hashes": hashes,
                  "target": target, "expected_diagnostic": DIAGNOSTICS.get(name),
                  "accepted": False, "proof_credit": False}
        (case / "case.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
        before = consumer._hashes(case)
        try:
            execution = dispatch(case, args, env)
        except Exception as error:
            execution = {"exception": {"type": type(error).__name__, "message": str(error)},
                         "status": "FAILED", "stages": None}
        after = consumer._hashes(case)
        source_stable = before == after
        if type(execution) is dict:
            execution["source_unchanged_at_every_stage"] = (
                source_stable and execution.get("source_unchanged_at_every_stage", True))
            execution["stage_receipt_gate"] = consumer._stage_receipts(
                case, execution.get("stages") if type(execution.get("stages")) is dict else {}, before)
        (case / "execution.json").write_text(
            json.dumps(execution, indent=2, sort_keys=True, default=str) + "\n")
        result = _classify(case, name, hashes, execution, anchor, consumer)
        (case / "classification.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        results[name] = result
    all_matched = all(result.get("matched") is True for result in results.values())
    aggregate = {"schema": RESULT_SCHEMA, "campaign": CAMPAIGN,
                 "profile": selected_profile, "cases": results,
                 "all_matched": all_matched,
                 "classification": "ALL_RAWPTR_CONTROLS_MATCHED" if all_matched else
                                  "RAW_PTR_CONTROLS_INCONCLUSIVE",
                 "accepted": False, "proof_credit": False, "b2_achieved": False,
                 "caller_or_prefix_gate": False, "independent_credit": False}
    (root / "result.json").write_text(json.dumps(aggregate, indent=2, sort_keys=True) + "\n")
    return aggregate
