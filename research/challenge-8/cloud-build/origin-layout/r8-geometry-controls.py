#!/usr/bin/env python3
"""Cloud-only probes for native StorageLive numeric-span eligibility.

Importing this module is inert. Compilation and verification are supplied only
by the authorized hosted execute_case callback.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path


CAMPAIGN = "r8-native-allocation-geometry-controls-v1"
PROFILE = "experimental-merge-late-callback-recovery-r7-v1"
TOOL_COMMIT = "43c1fdc2f08825fa81303a902ea9e718bba901f0"
HEADER = "#![no_std]\n#![allow(dead_code)]\n"
STAGES = ("exporter", "decode", "refinement", "verifast")
EXPECTED_DIAGNOSTIC = "Cannot prove condition."
EXPECTED_SPAN_DIAGNOSTIC_TOKENS = ("<=", "||")


_CONTRACT_CELL = (
    "/*@ req [1/4](*p |-> ?v); @*/"
    "/*@ ens [1/4](*p |-> v); @*/"
    "/*@ on_unwind_ens [1/4](*p |-> v); @*/"
)
_CONTRACT_ARRAY = (
    "/*@ req [1/4]array::<u64>(p,1,cons(?v,nil)); @*/"
    "/*@ ens [1/4]array::<u64>(p,1,cons(v,nil)); @*/"
    "/*@ on_unwind_ens [1/4]array::<u64>(p,1,cons(v,nil)); @*/"
)

CASES = {
    "incoming_cells": {
        "class": "positive",
        "entry": "cells",
        "contract": _CONTRACT_CELL,
        "before_local": "",
        "target": "incoming cell fresh-local span",
    },
    "incoming_array": {
        "class": "geometry_refusal",
        "entry": "array",
        "contract": _CONTRACT_ARRAY,
        "before_local": "",
        "target": "incoming array fresh-local span",
    },
    "opened_entry_array": {
        "class": "geometry_refusal",
        "entry": "array",
        "contract": _CONTRACT_ARRAY,
        "before_local": "    //@ open [1/4]array::<u64>(p,1,cons(v,nil));\n",
        "target": "opened entry array fresh-local span",
        "after_target": "    //@ close [1/4]array::<u64>(p,1,cons(v,nil));\n",
    },
}


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _source(name: str, *, verified: bool) -> bytes:
    spec = CASES[name]
    contract = (" " + spec["contract"]) if verified else ""
    before_local = spec["before_local"] if verified else ""
    assertion = (
        f"    //@ assert (_address as usize) + 8 <= p as usize || "
        f"(p as usize) + 8 <= _address as usize; // TARGET: {spec['target']}\n"
        if verified else ""
    )
    after = spec.get("after_target", "") if verified else ""
    function = (
        f"pub unsafe fn {name}(p: *mut u64){contract}\n"
        "{\n"
        f"    let mut local = 19u64;\n"
        "    let _address = &raw mut local;\n"
        f"{assertion}"
        f"{after}"
        "    local = local + 1;\n"
        "    let _keep_address_live = _address;\n"
        "}\n"
    )
    # The opening uses the value bound by the precondition.
    if before_local:
        function = function.replace(
            "    let mut local = 19u64;\n",
            before_local + "    let mut local = 19u64;\n",
            1,
        )
    return (HEADER + function).encode()


def _baseline_source(name: str) -> bytes:
    """Keep the same runtime body with all contracts and ghost code erased."""
    return _source(name, verified=False)


def prepare(evidence: Path) -> dict:
    evidence = Path(evidence)
    if evidence.exists():
        raise FileExistsError(f"refusing to reuse R8 geometry-control evidence: {evidence}")
    evidence.mkdir(parents=True)
    rows = {}
    for name, spec in CASES.items():
        original = _baseline_source(name)
        verified = _source(name, verified=True)
        marker = ("TARGET: " + spec["target"]).encode()
        target_lines = [line_no for line_no, line in enumerate(verified.splitlines(), 1)
                        if marker in line]
        if len(target_lines) != 1:
            raise ValueError(f"{name}: expected exactly one marked target statement")
        rows[name] = {
            "case": name,
            "expected_class": spec["class"],
            "entry_representation": spec["entry"],
            "target": {"line": target_lines[0], "marker": spec["target"]},
            "original_sha256": _sha(original),
            "verified_sha256": _sha(verified),
            "expected_stages": {stage: (1 if stage == "verifast" and
                                           spec["class"] == "geometry_refusal" else 0)
                                for stage in STAGES},
            "expected_diagnostic": (EXPECTED_DIAGNOSTIC
                                    if spec["class"] == "geometry_refusal" else None),
            "accepted": False,
            "proof_credit": False,
        }
        case = evidence / name
        for tree, content in (("original", original), ("verified", verified)):
            folder = case / tree
            folder.mkdir(parents=True)
            (folder / "lib.rs").write_bytes(content)
    manifest = {"schema": CAMPAIGN, "profile": PROFILE, "tool_commit": TOOL_COMMIT,
                "accepted": False, "proof_credit": False, "cases": rows}
    (evidence / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return rows


def _source_gate(case: Path, meta: dict, execution: dict) -> dict:
    hashes = {}
    for relative in ("original/lib.rs", "verified/lib.rs"):
        path = case / relative
        hashes[relative] = _sha(path.read_bytes()) if path.is_file() else None
    expected = {"original/lib.rs": meta["original_sha256"],
                "verified/lib.rs": meta["verified_sha256"]}
    unchanged = hashes == expected and execution.get("source_unchanged_at_every_stage") is True
    return {"admitted": unchanged, "hashes_after": hashes,
            "source_unchanged_at_every_stage": execution.get("source_unchanged_at_every_stage")}


def _stage_gate(case: Path, meta: dict, stages) -> dict:
    stages_ok = isinstance(stages, dict)
    stages = stages if isinstance(stages, dict) else {}
    details = {}
    for stage in STAGES:
        expected = meta["expected_stages"][stage]
        path = case / f"{stage}-stage.json"
        row = {"admitted": False, "reason": "stage receipt is absent"}
        if path.is_file():
            try:
                receipt = json.loads(path.read_text())
                before = receipt.get("source_before") if isinstance(receipt, dict) else None
                after = receipt.get("source_after") if isinstance(receipt, dict) else None
                source_match = (isinstance(before, dict) and before == after and
                                before.get("original/lib.rs") == meta["original_sha256"] and
                                before.get("verified/lib.rs") == meta["verified_sha256"])
                status = receipt.get("status") if isinstance(receipt, dict) else None
                status_ok = (status is None or
                             (isinstance(status, str) and
                              status in {"SUCCESS", "SUCCEEDED", "COMPLETED"}))
                code = receipt.get("exit_code") if isinstance(receipt, dict) else None
                ok = (isinstance(receipt, dict) and receipt.get("stage") == stage and
                      type(code) is int and code == expected and
                      type(stages.get(stage)) is int and stages.get(stage) == expected and
                      receipt.get("source_unchanged") is True and source_match and status_ok)
                row = {"admitted": ok, "exit_code": code,
                       "callback_exit_code": stages.get(stage),
                       "source_unchanged": (receipt.get("source_unchanged")
                                             if isinstance(receipt, dict) else None),
                       "source_identity_matches": source_match,
                       "status": status, "status_matches": status_ok}
            except (OSError, json.JSONDecodeError, AttributeError) as error:
                row = {"admitted": False, "reason": f"invalid stage receipt: {error}"}
        details[stage] = row
        stages_ok = stages_ok and row["admitted"]
    return {"admitted": stages_ok, "stages": details}


def classify(name: str, case: Path, meta: dict, execution) -> dict:
    if not isinstance(execution, dict):
        execution = {"execution_receipt_error": "execute_case returned a non-object"}
    source = _source_gate(case, meta, execution)
    stage_gate = _stage_gate(case, meta, execution.get("stages"))
    service_errors = []
    for key in ("error", "errors", "execution_error", "execution_receipt_error"):
        value = execution.get(key)
        if value not in (None, "", [], {}):
            service_errors.append({"field": key, "value": value})
    log_path = case / "verifast.log"
    log = log_path.read_text(errors="replace") if log_path.is_file() else ""
    errors = re.findall(r"^.*\berror:.*$", log, re.M | re.I)
    target_line = meta["target"]["line"]
    statement_events = [int(n) for n in re.findall(
        r"verified/lib\.rs\((\d+),\d+(?:-\d+(?:,\d+)?)?\): "
        r"(?:note: )?Executing statement", log)]
    target_executed = target_line in statement_events
    pre_error = log.split(errors[0], 1)[0] if errors else log
    prior_events = [int(n) for n in re.findall(
        r"verified/lib\.rs\((\d+),\d+(?:-\d+(?:,\d+)?)?\): "
        r"(?:note: )?Executing statement", pre_error)]
    last_execution_is_target = bool(prior_events) and prior_events[-1] == target_line
    error_at_target = (len(errors) == 1 and re.search(
        rf"verified/lib\.rs\({target_line},\d+(?:-\d+(?:,\d+)?)?\): error:",
        errors[0]) is not None)
    diagnostic_matches = (len(errors) == 1 and
                          isinstance(meta.get("expected_diagnostic"), str) and
                          meta["expected_diagnostic"] in errors[0] and
                          all(token in errors[0]
                              for token in EXPECTED_SPAN_DIAGNOSTIC_TOKENS))
    stages = execution.get("stages")
    stages = stages if isinstance(stages, dict) else {}
    common = source["admitted"] and stage_gate["admitted"] and not service_errors
    positive = (meta["expected_class"] == "positive" and common and
                stages.get("verifast") == 0 and not errors and target_executed and
                "Executing return statement" in log and "Leak check." in log and
                "0 errors found" in log)
    refusal = (meta["expected_class"] == "geometry_refusal" and common and
               stages.get("verifast") == 1 and error_at_target and
               diagnostic_matches and target_executed and last_execution_is_target and
               len(errors) == 1)
    classification = ("PASS_CONTROL" if positive else
                      "OBSERVED_GEOMETRY_REFUSAL" if refusal else "INCONCLUSIVE")
    return {**execution, **meta, "case": name, "classification": classification,
            "accepted": False, "proof_credit": False,
            "source_gate": source, "stage_gate": stage_gate,
            "target_executed": target_executed,
            "last_execution_is_target": last_execution_is_target,
            "error_at_target": error_at_target,
            "diagnostic_matches": diagnostic_matches, "errors": errors,
            "service_errors": service_errors,
            "evidence_class": "isolated native geometry diagnostic; no proof credit"}


def _inconclusive(name: str, reason: str) -> dict:
    return {"case": name, "classification": "INCONCLUSIVE", "accepted": False,
            "proof_credit": False, "reason": reason,
            "evidence_class": "setup or execution failure is not an observed geometry refusal"}


def _profile_binding(args, env: dict) -> dict:
    selected = getattr(args, "profile", None)
    profile_path = (env.get("SMALLSORT_MERGE_PROFILE") if isinstance(env, dict) else None)
    if not profile_path:
        raise ValueError("SMALLSORT_MERGE_PROFILE is required for R8 source binding")
    raw = Path(profile_path).read_bytes()
    profile = json.loads(raw)
    if not isinstance(profile, dict) or selected != PROFILE or profile.get("profile") != selected:
        raise ValueError("R8 selected profile does not match the pinned source profile")
    tool = profile.get("effective_tool_commit")
    if tool != TOOL_COMMIT:
        raise ValueError("R8 effective tool commit differs from the observed native rule source")
    return {"profile": selected, "profile_sha256": _sha(raw), "tool_commit": tool,
            "profile_path": str(Path(profile_path).resolve())}


def run(evidence: Path, args, env: dict, execute_case) -> dict:
    """Prepare three source probes and classify only hosted service receipts."""
    evidence = Path(evidence)
    try:
        binding = _profile_binding(args, env)
    except Exception as error:
        return {"schema": CAMPAIGN, "accepted": False, "proof_credit": False,
                "classification": "INCONCLUSIVE", "source_binding_error": str(error),
                "cases": {name: _inconclusive(name, "profile/tool source binding unavailable")
                          for name in CASES}}
    if not callable(execute_case):
        return {"schema": CAMPAIGN, **binding, "accepted": False, "proof_credit": False,
                "classification": "INCONCLUSIVE", "cases": {
                    name: _inconclusive(name, "hosted execute_case callback is unavailable")
                    for name in CASES}}
    try:
        rows = prepare(evidence)
    except Exception as error:
        return {"schema": CAMPAIGN, **binding, "accepted": False, "proof_credit": False,
                "classification": "INCONCLUSIVE", "cases": {
                    name: _inconclusive(name, f"preparation failed: {error}") for name in CASES}}
    results = {}
    for name, meta in rows.items():
        case = evidence / name
        try:
            child_args = copy.copy(args)
            child_args.first_fnmut_continue = False
            execution = execute_case(case, child_args, env)
            results[name] = classify(name, case, meta, execution)
        except Exception as error:
            results[name] = _inconclusive(name, f"execute_case/classification failed: {error}")
    classifications = {name: row["classification"] for name, row in results.items()}
    all_classified = (set(results) == set(CASES) and
                      classifications.get("incoming_cells") == "PASS_CONTROL" and
                      all(classifications.get(name) == "OBSERVED_GEOMETRY_REFUSAL"
                          for name in ("incoming_array", "opened_entry_array")))
    aggregate = {"schema": CAMPAIGN, **binding, "accepted": False, "proof_credit": False,
                 "all_classified": all_classified,
                 "classification": "DIAGNOSTIC_CONTROLS_CLASSIFIED" if all_classified else "INCONCLUSIVE",
                 "cases": classifications, "case_details": results,
                 "evidence_class": "bounded native allocation-rule eligibility probes only"}
    try:
        (evidence / "aggregate.json").write_text(json.dumps(aggregate, indent=2, sort_keys=True) + "\n")
    except OSError:
        aggregate["classification"] = "INCONCLUSIVE"
        aggregate["all_classified"] = False
        aggregate["aggregate_write_error"] = "could not persist aggregate receipt"
    return aggregate
