#!/usr/bin/env python3
"""Cloud-only controls for the R5/R7 address-taken continuation candidates.

This module prepares isolated source pairs and classifies receipts supplied by
the authorized hosted runner. It never starts a compiler or verifier.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path


PROFILE = "experimental-merge-guard-addressability-emitter-r5-v1"
R7_PROFILE = "experimental-merge-late-callback-recovery-r7-v1"
R8_PROFILE = "experimental-merge-owned-array-allocation-r8-v1"
R9_PROFILE = "experimental-merge-guard-current-return-r9-v1"
SUPPORTED_PROFILES = (PROFILE, R7_PROFILE, R8_PROFILE, R9_PROFILE)
CAMPAIGN = "r5-addressability-controls-v1"

HEADER = "#![allow(dead_code)]\n"
CONTRACT = """\n/*@ req *anchor |-> ?old; @*/\n/*@ ens *anchor |-> old; @*/\n/*@ on_unwind_ens *anchor |-> old; @*/\n"""

# The before_storage_live ghost assertion deliberately refers to the later
# local declaration. It is admitted only if the real source pipeline reaches
# the expected storage/permission refusal at that annotation.
CASES: dict[str, dict] = {
    "address_before_merge": {
        "source": """pub unsafe fn address_before_merge(anchor: *mut u64)\n{contract}\n{{\n    let mut local = 7u64;\n    let _address = &raw mut local; // TARGET: address before merge\n    //@ let k = begin_lifetime();\n    //@ merge_fractions lifetime_token(k);\n    //@ end_lifetime(k);\n    local = local + 1;\n    //@ assert local == 8;\n}\n""",
        "target_markers": ["address before merge"],
        "class": "positive", "locals": {"local": True},
    },
    "address_after_merge": {
        "source": """pub unsafe fn address_after_merge(anchor: *mut u64)\n{contract}\n{{\n    let mut local = 7u64;\n    //@ let k = begin_lifetime();\n    //@ merge_fractions lifetime_token(k);\n    let _address = &raw mut local; // TARGET: address after merge\n    //@ end_lifetime(k);\n    local = local + 1;\n    //@ assert local == 8;\n}\n""",
        "target_markers": ["address after merge"],
        "class": "positive", "locals": {"local": True},
    },
    "address_in_merge_assertion": {
        "source": """pub unsafe fn address_in_merge_assertion(anchor: *mut u64)\n{contract}\n{{\n    let local = 7u64;\n    //@ merge_fractions points_to::<u64>(&local, _); // TARGET: AddressOf is inside merge assertion\n    //@ assert local == 7;\n}\n""",
        "target_markers": ["AddressOf is inside merge assertion"],
        "class": "positive", "locals": {"local": True},
    },
    "multiple_merges_unrelated_local": {
        "source": """pub unsafe fn multiple_merges_unrelated_local(anchor: *mut u64)\n{contract}\n{{\n    let mut local = 3u64;\n    let unrelated = 11u64;\n    //@ let k1 = begin_lifetime();\n    //@ merge_fractions lifetime_token(k1);\n    let first = &raw mut local; // TARGET: first continuation\n    //@ end_lifetime(k1);\n    //@ let k2 = begin_lifetime();\n    //@ merge_fractions lifetime_token(k2);\n    let second = &raw mut local; // TARGET: second continuation\n    //@ end_lifetime(k2);\n    //@ assert first == second;\n    //@ assert points_to::<u64>(first, 3); // TARGET: physical ownership of the shared address\n    unsafe { *first = 5; }\n    let through_second = unsafe { *second };\n    //@ assert through_second == 5;\n    //@ assert local == 5;\n    //@ assert unrelated == 11;\n}\n""",
        "target_markers": ["first continuation", "second continuation",
                           "physical ownership of the shared address"],
        "class": "positive", "locals": {"local": True, "unrelated": False},
    },
    "address_normal_unwind": {
        "source": """#[inline(never)]\nfn may_panic(flag: bool)\n/*@ req true; @*/\n/*@ ens true; @*/\n/*@ on_unwind_ens true; @*/\n{{\n    assert!(!flag);\n}}\n\npub unsafe fn address_normal_unwind(anchor: *mut u64, flag: bool)\n{contract}\n{{\n    let mut local = 19u64;\n    //@ let k = begin_lifetime();\n    //@ merge_fractions lifetime_token(k);\n    let _address = &raw mut local; // TARGET: address after merge on normal/unwind paths\n    //@ end_lifetime(k);\n    may_panic(flag);\n    //@ assert local == 19;\n}}\n""",
        "target_markers": ["address after merge on normal/unwind paths"],
        "class": "positive", "locals": {"local": True},
    },
    "missing_physical_owner": {
        "source": """pub unsafe fn missing_physical_owner(anchor: *mut u64)\n/*@ req true; @*/\n/*@ ens true; @*/\n/*@ on_unwind_ens true; @*/\n{{\n    //@ assert *anchor |-> ?observed; // TARGET: physical owner is deliberately absent\n}}\n""",
        "class": "negative", "target": "physical owner is deliberately absent",
        "error_contains": "No matching heap chunks",
    },
    "after_storage_dead": {
        "source": """pub unsafe fn after_storage_dead(anchor: *mut u64)\n{contract}\n{{\n    let mut stale: *mut u64 = anchor;\n    {{\n        let mut local = 23u64;\n        stale = &raw mut local;\n    }} // local StorageDead precedes the TARGET assertion\n    //@ assert *stale |-> ?observed; // TARGET: dereference after StorageDead\n}}\n""",
        "class": "negative", "target": "dereference after StorageDead",
        "error_contains": "No matching heap chunks",
    },
    "unsupported_address_operand": {
        "source": """pub unsafe fn unsupported_address_operand(anchor: *mut u64)\n{contract}\n{{\n    //@ assert &(1 + 2) == &(1 + 2); // TARGET: unsupported AddressOf operand\n}}\n""",
        "class": "negative", "target": "unsupported AddressOf operand",
        "error_contains": "Taking the address of this expression is not supported.",
    },
    "before_storage_live": {
        "source": """pub unsafe fn before_storage_live(anchor: *mut u64)\n{contract}\n{{\n    //@ assert *(&local) |-> _; // TARGET: ghost address precedes local StorageLive\n    let local = 31u64;\n    assert!(local == 31);\n}}\n""",
        "class": "negative", "target": "ghost address precedes local StorageLive",
        "error_contains": "No matching heap chunks",
    },
}


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _unit(name: str, spec: dict) -> bytes:
    if spec["class"] == "not_run":
        raise ValueError(f"{name} is an explicit NOT_RUN control")
    source = (HEADER + spec["source"].replace("{contract}", CONTRACT)
              .replace("{{", "{").replace("}}", "}"))
    if source.count("pub unsafe fn ") != 1:
        raise ValueError(f"{name}: expected one isolated target function")
    return source.encode()


def prepare(evidence: Path, *, profile: str = PROFILE) -> dict:
    if profile not in SUPPORTED_PROFILES:
        raise ValueError("unsupported R5/R7 addressability-control profile")
    if evidence.exists():
        raise FileExistsError(f"refusing to reuse addressability-control evidence: {evidence}")
    evidence.mkdir(parents=True)
    rows = {}
    for name, spec in CASES.items():
        if spec["class"] == "not_run":
            rows[name] = {"classification": "NOT_RUN", "reason": spec["reason"]}
            continue
        unit = _unit(name, spec)
        target_labels = spec.get("target_markers", [])
        if spec.get("target"):
            target_labels = [spec["target"]]
        source_lines = unit.decode().splitlines()
        target_lines = []
        for target in target_labels:
            found = [i for i, line in enumerate(source_lines, 1)
                     if f"TARGET: {target}" in line]
            if len(found) != 1:
                raise ValueError(f"{name}: target marker is not unique: {target}")
            target_lines.append(found[0])
        case = evidence / name
        for tree in ("original", "verified"):
            directory = case / tree
            directory.mkdir(parents=True, exist_ok=True)
            (directory / "lib.rs").write_bytes(unit)
        rows[name] = {
            "source_sha256": _sha(unit), "original_sha256": _sha(unit),
            "verified_sha256": _sha(unit), "target_lines": target_lines,
            "expected_stages": {"exporter": 0, "decode": 0, "refinement": 0,
                                "verifast": 0 if spec["class"] == "positive" else 1},
            "expected_class": spec["class"], "locals": spec.get("locals", {}),
            "error_contains": spec.get("error_contains"),
        }
    manifest = {"schema": CAMPAIGN, "profile": profile, "accepted": False,
                "case_details": rows}
    (evidence / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return rows


def _rocq_local_flags(case: Path) -> dict:
    candidates = (case / "verified/lib.v", case / "lib.v")
    path = next((candidate for candidate in candidates if candidate.is_file()), None)
    if path is None:
        return {"admitted": False, "reason": "final verifier-emitted Rocq file is absent"}
    text = path.read_text(errors="replace")
    flags = {}
    for name, flag in re.findall(r'LocalAddrTaken\s+"([^"\\]*(?:\\.[^"\\]*)*)"\s+(true|false)', text):
        flags.setdefault(name, []).append(flag == "true")
    return {"admitted": True, "path": str(path.name), "sha256": _sha(path.read_bytes()),
            "flags": flags}


def _stage_receipt_gate(case: Path, meta: dict, stages: dict) -> dict:
    rows = {}
    admitted = True
    for stage, expected_code in meta["expected_stages"].items():
        path = case / f"{stage}-stage.json"
        if not path.is_file():
            rows[stage] = {"admitted": False, "reason": "stage receipt is absent"}
            admitted = False
            continue
        try:
            receipt = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError) as error:
            rows[stage] = {"admitted": False, "reason": f"invalid stage receipt: {error}"}
            admitted = False
            continue
        source_before = receipt.get("source_before") if isinstance(receipt, dict) else None
        source_after = receipt.get("source_after") if isinstance(receipt, dict) else None
        source_hashes_match = (isinstance(source_before, dict) and
                               source_before == source_after and
                               source_before.get("original/lib.rs") == meta["original_sha256"] and
                               source_before.get("verified/lib.rs") == meta["verified_sha256"])
        ok = (isinstance(receipt, dict) and receipt.get("stage") == stage and
              receipt.get("exit_code") == expected_code and
              receipt.get("source_unchanged") is True and source_hashes_match and
              stages.get(stage) == expected_code)
        rows[stage] = {"admitted": ok, "exit_code": receipt.get("exit_code") if isinstance(receipt, dict) else None,
                       "source_unchanged": receipt.get("source_unchanged") if isinstance(receipt, dict) else None,
                       "source_hashes_match": source_hashes_match}
        admitted = admitted and ok
    return {"admitted": admitted, "stages": rows}


def classify(name: str, case: Path, meta: dict, execution: dict) -> dict:
    spec = CASES[name]
    if not isinstance(execution, dict):
        execution = {"execution_receipt_error": "execute_case returned a non-object"}
    stages = execution.get("stages")
    if not isinstance(stages, dict):
        stages = {}
    source_paths = [case / "original/lib.rs", case / "verified/lib.rs"]
    actual_hashes = [_sha(path.read_bytes()) if path.is_file() else None for path in source_paths]
    source_ok = (actual_hashes == [meta["original_sha256"], meta["verified_sha256"]] and
                 execution.get("source_unchanged_at_every_stage") is True)
    stage_receipts = _stage_receipt_gate(case, meta, stages)
    stage_ok = stage_receipts["admitted"]
    log_path = case / "verifast.log"
    log = log_path.read_text(errors="replace") if log_path.is_file() else ""
    error_lines = re.findall(r"^.*\berror:.*$", log, re.M | re.I)
    target_line = meta.get("target_lines", [None])[0]
    target_error = (bool(target_line) and len(error_lines) == 1 and
                    re.search(rf"verified/lib\.rs\({target_line},\d+(?:-\d+(?:,\d+)?)?\): error:",
                              error_lines[0]) is not None)
    error_match = bool(error_lines and meta.get("error_contains") and
                       meta["error_contains"] in error_lines[0])
    rocq = _rocq_local_flags(case) if spec["class"] == "positive" else {
        "admitted": False, "reason": "Rocq flag gate applies to positive allocation controls"}
    local_gate = True
    observed = {}
    if spec["class"] == "positive":
        local_gate = rocq.get("admitted") is True
        if local_gate:
            for local, expected in meta["locals"].items():
                values = rocq["flags"].get(local, [])
                observed[local] = values
                local_gate = local_gate and values == [expected]
    target_execution = [
        bool(re.search(rf"verified/lib\.rs\({line},\d+(?:-\d+(?:,\d+)?)?\): "
                       r"(?:note: )?Executing statement", log))
        for line in meta.get("target_lines", [])]
    positive = (spec["class"] == "positive" and source_ok and stage_ok and
                stages.get("verifast") == 0 and not error_lines and local_gate and
                "Executing return statement" in log and "Leak check." in log and
                "0 errors found" in log and all(target_execution))
    negative = (spec["class"] == "negative" and source_ok and stage_ok and
                stages.get("verifast") == 1 and target_error and error_match and
                len(error_lines) == 1)
    if positive:
        classification = "PASS_CONTROL"
    elif negative:
        classification = "EXPECTED_REJECTION"
    else:
        classification = "INCONCLUSIVE"
    result = {**execution, **meta, "case": name,
              "classification": classification, "accepted": False,
              "source_hashes_after": actual_hashes, "stage_receipts_match": stage_ok,
              "stage_receipts": stage_receipts,
              "source_receipts_match": source_ok, "target_error": target_error,
              "target_execution": target_execution,
              "error_match": error_match, "errors": error_lines,
              "rocq_final_local_flags": rocq, "expected_local_flags": meta.get("locals", {}),
              "observed_local_flags": observed,
              "evidence_class": "diagnostic control only; no profile acceptance or proof credit"}
    (case / "classification.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def _receipt_gate(args, receipt: dict) -> dict:
    if not isinstance(receipt, dict):
        raise TypeError("validated_receipt must be a dictionary")
    profile = getattr(args, "profile", None)
    if profile not in SUPPORTED_PROFILES or receipt.get("profile") != profile:
        raise RuntimeError("addressability profile identity differs")
    provider = receipt.get("provider")
    build_id = (provider.get("build_id") if isinstance(provider, dict) else None) or \
        receipt.get("build_id") or receipt.get("cloud_build_id")
    proof_sha = receipt.get("proof_sha")
    profile_sha = receipt.get("profile_sha256") or receipt.get("profile_sha")
    tool_commit = receipt.get("tool_commit")
    verify_expr_sha = receipt.get("verify_expr_sha256")
    if (not isinstance(build_id, str) or not build_id or
            not isinstance(proof_sha, str) or not re.fullmatch(r"[0-9a-f]{40}", proof_sha)):
        raise RuntimeError("validated receipt lacks exact Cloud build/proof identity")
    if not isinstance(profile_sha, str) or not re.fullmatch(r"[0-9a-f]{64}", profile_sha):
        raise RuntimeError("validated receipt lacks the exact profile SHA-256")
    if not isinstance(tool_commit, str) or not re.fullmatch(r"[0-9a-f]{40}", tool_commit):
        raise RuntimeError("validated receipt lacks the exact tool commit")
    if not isinstance(verify_expr_sha, str) or not re.fullmatch(r"[0-9a-f]{64}", verify_expr_sha):
        raise RuntimeError("validated receipt lacks the exact verify_expr SHA-256")
    if receipt.get("accepted") is not False:
        raise RuntimeError("experimental profile receipt must explicitly remain unaccepted")
    return {"build_id": build_id, "proof_sha": proof_sha,
            "profile_sha256": profile_sha, "tool_commit": tool_commit,
            "verify_expr_sha256": verify_expr_sha, "profile": profile}


def _inconclusive_row(name: str, meta: dict, error: Exception) -> dict:
    return {**meta, "case": name, "classification": "INCONCLUSIVE",
            "accepted": False, "reason": f"case execution/classification failed: {error}",
            "evidence_class": "diagnostic control only; setup/execution failure is not a negative"}


def run(evidence: Path, args, env: dict, execute_case, validated_receipt: dict) -> dict:
    """Execute prepared cases through the parent's exact hosted candidate callback."""
    if not callable(execute_case):
        raise TypeError("hosted execute_case callback required")
    identity = _receipt_gate(args, validated_receipt)
    rows = prepare(evidence / "r5-addressability", profile=identity["profile"])
    result_rows = {}
    for name, meta in rows.items():
        case = evidence / "r5-addressability" / name
        try:
            child_args = copy.copy(args)
            child_args.r4_addressability_rocq = True
            execution = execute_case(case, child_args, env)
            result_rows[name] = classify(name, case, meta, execution)
        except Exception as error:
            result_rows[name] = _inconclusive_row(name, meta, error)
    controls = {name: row.get("classification", "NOT_RUN") for name, row in result_rows.items()}
    required_names = tuple(CASES)
    all_matched = (set(controls) == set(required_names) and
                   all(controls[name] in {"PASS_CONTROL", "EXPECTED_REJECTION"}
                       for name in required_names))
    aggregate = {"schema": CAMPAIGN, "profile": identity["profile"], "accepted": False,
                 "proof_credit": False, "receipt_identity": identity,
                 "controls": controls, "cases": controls,
                 "case_details": result_rows, "all_matched": all_matched,
                 "all_dispatched_controls_classified": all(
                     value in {"PASS_CONTROL", "EXPECTED_REJECTION"} for value in controls.values()),
                 "evidence_class": "diagnostic only; NOT_RUN and INCONCLUSIVE remain explicit"}
    aggregate_path = evidence / "aggregate.json"
    aggregate_path.write_text(json.dumps(aggregate, indent=2, sort_keys=True) + "\n")
    (evidence / "r5-addressability-results.json").write_text(
        json.dumps(aggregate, indent=2, sort_keys=True) + "\n")
    return aggregate
