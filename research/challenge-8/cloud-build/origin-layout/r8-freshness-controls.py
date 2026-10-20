#!/usr/bin/env python3
"""Cloud-only controls for the opt-in R8 owned-array freshness rule.

Importing this module is inert. The authorized hosted execute_case callback
performs every compiler and verifier stage.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path


CAMPAIGN = "r8-owned-array-freshness-controls-v1"
PROFILE = "experimental-merge-owned-array-allocation-r8-v1"
STAGES = ("exporter", "decode", "refinement", "verifast")
HEADER = "#![no_std]\n#![allow(dead_code)]\n"
SPAN_DIAGNOSTIC = "Cannot prove condition."
OWNER_DIAGNOSTIC = "No matching heap chunks"
SPAN_TOKENS = ("<=", "||")


def _contract_array(ty: str, base: str, count: int, binder: str = "xs") -> str:
    return (
        f"/*@ req [1/4]array::<{ty}>({base},{count},?{binder}); @*/"
        f"/*@ ens [1/4]array::<{ty}>({base},{count},{binder}); @*/"
        f"/*@ on_unwind_ens [1/4]array::<{ty}>({base},{count},{binder}); @*/"
    )


CASES = {
    "wholearray3": {
        "function": "wholearray3",
        "class": "positive",
        "entry": "u64 array length 3; current range length 3",
        "contract": _contract_array("u64", "p", 3),
        "setup": "",
        "target_expr": "(_address as usize) + 8 <= (p + 1) as usize || "
                       "((p + 1) as usize) + 8 <= _address as usize",
        "target": "wholearray3 local span is apart from p + 1 cell",
    },
    "currentprefix2": {
        "function": "currentprefix2",
        "class": "positive",
        "entry": "u64 array length 3; current range is the owned prefix length 2",
        "contract": _contract_array("u64", "p", 3),
        "setup": "    //@ array_split::<u64>(p, 2);\n",
        "target_expr": "(_address as usize) + 8 <= (p + 1) as usize || "
                       "((p + 1) as usize) + 8 <= _address as usize",
        "target": "current prefix2 local span is apart from p + 1 cell",
        "restore": "    //@ array_join::<u64>(p);\n",
    },
    "default_off": {
        "source_case": "wholearray3",
        "function": "wholearray3",
        "class": "span_refusal",
        "entry": "u64 array length 3; allocation option explicitly disabled",
        "flag": False,
    },
    "wrong_entry_count": {
        "function": "wrong_entry_count",
        "class": "span_refusal",
        "entry": "u64 array length 2",
        "contract": _contract_array("u64", "p", 2),
        "setup": "",
        "target_expr": "(_address as usize) + 8 <= (p + 1) as usize || "
                       "((p + 1) as usize) + 8 <= _address as usize",
        "target": "wrong entry count local span is apart from p + 1 cell",
    },
    "wrong_element": {
        "function": "wrong_element",
        "class": "span_refusal",
        "entry": "i64 array length 3",
        "contract": _contract_array("i64", "p", 3),
        "setup": "",
        "target_expr": "(_address as usize) + 8 <= (p + 1) as usize || "
                       "((p + 1) as usize) + 8 <= _address as usize",
        "target": "wrong element type local span is apart from p + 1 cell",
    },
    "missing_current_owner": {
        "function": "missing_current_owner",
        "class": "span_refusal",
        "entry": "u64 array length 3 opened fully into cells before StorageLive",
        "contract": _contract_array("u64", "p", 3),
        "setup": (
            "    //@ open [1/4]array::<u64>(p, 3, xs);\n"
            "    //@ open [1/4]array::<u64>(p + 1, 2, drop(1, xs));\n"
            "    //@ open [1/4]array::<u64>(p + 2, 1, drop(2, xs));\n"
        ),
        "target_expr": "(_address as usize) + 8 <= (p + 1) as usize || "
                       "((p + 1) as usize) + 8 <= _address as usize",
        "target": "missing current canonical owner local span assertion",
        "restore": (
            "    //@ close [1/4]array::<u64>(p + 2, 1, drop(2, xs));\n"
            "    //@ close [1/4]array::<u64>(p + 1, 2, drop(1, xs));\n"
            "    //@ close [1/4]array::<u64>(p, 3, xs);\n"
        ),
    },
    "wrong_root": {
        "function": "wrong_root",
        "class": "span_refusal",
        "entry": "u64 array length 3 at p and separate u64 array length 1 at q",
        "contract": (
            "/*@ req [1/4]array::<u64>(p,3,?xs) &*& [1/4]array::<u64>(q,1,?ys); @*/"
            "/*@ ens [1/4]array::<u64>(p,3,xs) &*& [1/4]array::<u64>(q,1,ys); @*/"
            "/*@ on_unwind_ens [1/4]array::<u64>(p,3,xs) &*& [1/4]array::<u64>(q,1,ys); @*/"
        ),
        "setup": "",
        "target_expr": "(_address as usize) + 8 <= q as usize || "
                       "(q as usize) + 8 <= _address as usize",
        "target": "wrong root local span assertion at q",
        "restore": "",
    },
    "numeric_same_address_no_owner": {
        "function": "numeric_same_address_no_owner",
        "class": "missing_owner_refusal",
        "entry": "no incoming resource; p is only a raw pointer parameter",
        "contract": "/*@ req true; @*//*@ ens true; @*//*@ on_unwind_ens true; @*/",
        "setup": "",
        "target_expr": None,
        "target": "numeric equality cannot establish points_to ownership",
    },
}


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _case_spec(name: str) -> dict:
    return CASES[CASES[name].get("source_case", name)]


def _source(name: str, *, verified: bool) -> bytes:
    spec = _case_spec(name)
    function = spec["function"]
    contract = (" " + spec["contract"]) if verified else ""
    setup = spec.get("setup", "") if verified else ""
    restore = spec.get("restore", "") if verified else ""
    if verified and spec["class"] == "missing_owner_refusal":
        target = ("    //@ if p as usize == _address as usize { assert *p |-> _; } "
                  f"// TARGET: {spec['target']}\n")
    elif verified:
        target = (f"    //@ assert {spec['target_expr']}; "
                  f"// TARGET: {spec['target']}\n")
    else:
        target = ""
    args = "p: *mut u64"
    if name == "wrong_element":
        args = "p: *mut i64"
    elif name == "wrong_root":
        args = "p: *mut u64, q: *mut u64"
    function_source = (
        f"pub unsafe fn {function}({args}){contract}\n"
        "{\n"
        f"{setup}"
        "    let mut local = 19u64;\n"
        "    let _address = &raw mut local;\n"
        f"{target}"
        f"{restore}"
        "    local = local + 1;\n"
        "    let _keep_address_live = _address;\n"
        "}\n"
    )
    return (HEADER + function_source).encode()


def _expected_error(name: str) -> dict | None:
    expected_class = CASES[name]["class"]
    if expected_class == "span_refusal":
        return {"contains": SPAN_DIAGNOSTIC, "tokens": list(SPAN_TOKENS)}
    if expected_class == "missing_owner_refusal":
        return {"contains": OWNER_DIAGNOSTIC, "tokens": ["points_to"]}
    return None


def prepare(evidence: Path) -> dict:
    evidence = Path(evidence)
    if evidence.exists():
        raise FileExistsError(f"refusing to reuse R8 freshness-control evidence: {evidence}")
    evidence.mkdir(parents=True)
    rows = {}
    for name, spec in CASES.items():
        source_spec = _case_spec(name)
        original = _source(name, verified=False)
        verified = _source(name, verified=True)
        marker = ("TARGET: " + source_spec["target"]).encode()
        target_lines = [line for line, content in enumerate(verified.splitlines(), 1)
                        if marker in content]
        if len(target_lines) != 1:
            raise ValueError(f"{name}: expected exactly one target marker")
        flag = spec.get("flag", True)
        rows[name] = {
            "case": name,
            "expected_class": spec["class"],
            "entry_shape": source_spec["entry"],
            "expected_flag": flag,
            "target": {"line": target_lines[0], "marker": source_spec["target"]},
            "original_sha256": _sha(original),
            "verified_sha256": _sha(verified),
            "expected_stages": {stage: (1 if stage == "verifast" and
                                           spec["class"] in {"span_refusal", "missing_owner_refusal"}
                                           else 0) for stage in STAGES},
            "expected_error": _expected_error(name),
            "accepted": False,
            "proof_credit": False,
        }
        case = evidence / name
        for tree, content in (("original", original), ("verified", verified)):
            folder = case / tree
            folder.mkdir(parents=True)
            (folder / "lib.rs").write_bytes(content)
    (evidence / "manifest.json").write_text(json.dumps({
        "schema": CAMPAIGN, "profile": PROFILE, "accepted": False,
        "proof_credit": False, "cases": rows,
    }, indent=2, sort_keys=True) + "\n")
    return rows


def _source_gate(case: Path, meta: dict, execution: dict) -> dict:
    after = {}
    for relative in ("original/lib.rs", "verified/lib.rs"):
        path = case / relative
        after[relative] = _sha(path.read_bytes()) if path.is_file() else None
    expected = {"original/lib.rs": meta["original_sha256"],
                "verified/lib.rs": meta["verified_sha256"]}
    admitted = (after == expected and
                execution.get("source_unchanged_at_every_stage") is True)
    return {"admitted": admitted, "hashes_after": after,
            "source_unchanged_at_every_stage": execution.get("source_unchanged_at_every_stage")}


def _stage_gate(case: Path, meta: dict, stages) -> dict:
    admitted = isinstance(stages, dict)
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
                       "source_identity_matches": source_match,
                       "source_unchanged": receipt.get("source_unchanged")
                       if isinstance(receipt, dict) else None,
                       "status": status, "status_matches": status_ok}
            except (OSError, json.JSONDecodeError, AttributeError) as error:
                row = {"admitted": False, "reason": f"invalid stage receipt: {error}"}
        details[stage] = row
        admitted = admitted and row["admitted"]
    return {"admitted": admitted, "stages": details}


def classify(name: str, case: Path, meta: dict, execution) -> dict:
    if not isinstance(execution, dict):
        execution = {"execution_receipt_error": "execute_case returned a non-object"}
    source_gate = _source_gate(case, meta, execution)
    stage_gate = _stage_gate(case, meta, execution.get("stages"))
    flag_ok = (type(execution.get("r8_owned_array_allocation")) is bool and
               execution.get("r8_owned_array_allocation") is meta["expected_flag"])
    service_errors = []
    for key in ("error", "errors", "execution_error", "execution_receipt_error"):
        value = execution.get(key)
        if value not in (None, "", [], {}):
            service_errors.append({"field": key, "value": value})
    log_path = case / "verifast.log"
    log = log_path.read_text(errors="replace") if log_path.is_file() else ""
    errors = re.findall(r"^.*\berror:.*$", log, re.M | re.I)
    target_line = meta["target"]["line"]
    events = [int(line) for line in re.findall(
        r"verified/lib\.rs\((\d+),\d+(?:-\d+(?:,\d+)?)?\): "
        r"(?:note: )?Executing statement", log)]
    target_executed = target_line in events
    before_error = log.split(errors[0], 1)[0] if errors else log
    before_events = [int(line) for line in re.findall(
        r"verified/lib\.rs\((\d+),\d+(?:-\d+(?:,\d+)?)?\): "
        r"(?:note: )?Executing statement", before_error)]
    last_execution_is_target = bool(before_events) and before_events[-1] == target_line
    error_at_target = (len(errors) == 1 and re.search(
        rf"verified/lib\.rs\({target_line},\d+(?:-\d+(?:,\d+)?)?\): error:",
        errors[0]) is not None)
    expected_error = meta.get("expected_error")
    diagnostic_matches = (len(errors) == 1 and isinstance(expected_error, dict) and
                          expected_error.get("contains") in errors[0] and
                          all(token in errors[0] for token in expected_error.get("tokens", [])))
    stages = execution.get("stages")
    stages = stages if isinstance(stages, dict) else {}
    common = (source_gate["admitted"] and stage_gate["admitted"] and flag_ok and
              not service_errors)
    positive = (meta["expected_class"] == "positive" and common and
                stages.get("verifast") == 0 and not errors and target_executed and
                "Executing return statement" in log and "Leak check." in log and
                "0 errors found" in log)
    refusal = (meta["expected_class"] in {"span_refusal", "missing_owner_refusal"} and
               common and stages.get("verifast") == 1 and error_at_target and
               diagnostic_matches and target_executed and last_execution_is_target and
               len(errors) == 1)
    classification = ("PASS_CONTROL" if positive else
                      "EXPECTED_REJECTION_DIAGNOSTIC" if refusal else "INCONCLUSIVE")
    return {**execution, **meta, "case": name, "classification": classification,
            "accepted": False, "proof_credit": False,
            "source_gate": source_gate, "stage_gate": stage_gate,
            "flag_receipt_matches": flag_ok, "target_executed": target_executed,
            "last_execution_is_target": last_execution_is_target,
            "error_at_target": error_at_target,
            "diagnostic_matches": diagnostic_matches, "errors": errors,
            "service_errors": service_errors,
            "evidence_class": "experimental allocation freshness control only; no proof credit"}


def _inconclusive(name: str, reason: str) -> dict:
    return {"case": name, "classification": "INCONCLUSIVE", "accepted": False,
            "proof_credit": False, "reason": reason,
            "evidence_class": "setup/execution failure is not an intended refusal"}


def _profile_binding(args, env: dict) -> dict:
    selected = getattr(args, "profile", None)
    profile_path = env.get("SMALLSORT_MERGE_PROFILE") if isinstance(env, dict) else None
    if not profile_path:
        raise ValueError("SMALLSORT_MERGE_PROFILE is required for R8 profile binding")
    raw = Path(profile_path).read_bytes()
    profile = json.loads(raw)
    if not isinstance(profile, dict):
        raise ValueError("R8 profile must be a JSON object")
    if selected != PROFILE or profile.get("profile") != selected:
        raise ValueError("selected profile differs from the owner-array R8 profile")
    schema = profile.get("schema")
    if not isinstance(schema, str) or not schema:
        raise ValueError("R8 profile schema is absent")
    if profile.get("accepted") is not False:
        raise ValueError("experimental R8 profile must remain explicitly unaccepted")
    tool_commit = profile.get("effective_tool_commit")
    if not isinstance(tool_commit, str) or not re.fullmatch(r"[0-9a-f]{40}", tool_commit):
        raise ValueError("R8 profile lacks its current effective tool commit")
    return {"profile": selected, "profile_schema": schema, "profile_accepted": False,
            "profile_sha256": _sha(raw), "effective_tool_commit": tool_commit,
            "profile_path": str(Path(profile_path).resolve())}


def run(evidence: Path, args, env: dict, execute_case) -> dict:
    """Run all bounded controls through the hosted callback and classify receipts."""
    evidence = Path(evidence)
    try:
        binding = _profile_binding(args, env)
    except Exception as error:
        return {"schema": CAMPAIGN, "accepted": False, "proof_credit": False,
                "classification": "INCONCLUSIVE", "profile_binding_error": str(error),
                "cases": {name: _inconclusive(name, "profile binding unavailable") for name in CASES}}
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
                    name: _inconclusive(name, f"source preparation failed: {error}")
                    for name in CASES}}
    manifest_path = evidence / "manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text())
        manifest.update(binding)
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        for meta in rows.values():
            meta["source_binding"] = binding
    except (OSError, json.JSONDecodeError, AttributeError) as error:
        return {"schema": CAMPAIGN, **binding, "accepted": False, "proof_credit": False,
                "classification": "INCONCLUSIVE", "manifest_binding_error": str(error),
                "cases": {name: _inconclusive(name, "could not persist profile binding")
                          for name in CASES}}
    results = {}
    for name, meta in rows.items():
        case = evidence / name
        try:
            child_args = copy.copy(args)
            child_args.r8_owned_array_allocation = meta["expected_flag"]
            child_args.first_fnmut_continue = False
            execution = execute_case(case, child_args, env)
            results[name] = classify(name, case, meta, execution)
        except Exception as error:
            results[name] = _inconclusive(name, f"execute_case/classification failed: {error}")
    classifications = {name: row["classification"] for name, row in results.items()}
    expected = {name: ("PASS_CONTROL" if spec["class"] == "positive"
                       else "EXPECTED_REJECTION_DIAGNOSTIC") for name, spec in CASES.items()}
    all_classified = set(classifications) == set(expected) and classifications == expected
    aggregate = {"schema": CAMPAIGN, **binding, "accepted": False, "proof_credit": False,
                 "all_classified": all_classified,
                 "classification": "DIAGNOSTIC_CONTROLS_CLASSIFIED" if all_classified else "INCONCLUSIVE",
                 "cases": classifications, "case_details": results,
                 "evidence_class": "diagnostic controls for an unaccepted experimental profile"}
    try:
        (evidence / "aggregate.json").write_text(json.dumps(aggregate, indent=2, sort_keys=True) + "\n")
    except OSError:
        aggregate["classification"] = "INCONCLUSIVE"
        aggregate["all_classified"] = False
        aggregate["aggregate_write_error"] = "could not persist aggregate receipt"
    return aggregate
