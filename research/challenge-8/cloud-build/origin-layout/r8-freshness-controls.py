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
import uuid
from pathlib import Path


CAMPAIGN = "r8-owned-array-freshness-controls-v1"
PROFILE = "experimental-merge-owned-array-allocation-r8-v1"
R9_PROFILE = "experimental-merge-guard-current-return-r9-v1"
R10_PROFILE = "experimental-merge-moving-gap-r10-v1"
SUPPORTED_PROFILES = (PROFILE, R9_PROFILE, R10_PROFILE)
STAGES = ("exporter", "decode", "refinement", "verifast")
R10_TOOL_KEYS = ("vf-rust-mir-exporter", "verifast", "refinement-checker")
HEADER = "#![no_std]\n#![allow(dead_code)]\n"
SPAN_DIAGNOSTIC = "Assertion might not hold."
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
        # RawPtr MIR statements are not supported by the refinement bridge.
        # A normal mutable reference followed by Rust's pointer cast preserves
        # the same runtime address-taking while staying in the supported MIR
        # subset; it does not add a verifier premise or change ownership.
        "    let _address = &mut local as *mut u64;\n"
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
        tokens = ["Cannot prove", *SPAN_TOKENS, "get_pointer_address(local_addr)"]
        if name == "wrong_root":
            tokens.append("get_pointer_address(q)")
        else:
            element_type = "int64_t_typeid" if name == "wrong_element" else "uint64_t_typeid"
            tokens.append(f"ptr_add_(p, 1, {element_type})")
        return {"contains": SPAN_DIAGNOSTIC,
                "tokens": tokens}
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


def _stage_gate(case: Path, meta: dict, stages, *, expected_run_identity=None,
                original_export_stages=None, stage_receipt_sha256=None) -> dict:
    admitted = isinstance(stages, dict)
    stages = stages if isinstance(stages, dict) else {}
    original_export_stages = (original_export_stages if isinstance(original_export_stages, dict)
                              else {})
    stage_receipt_sha256 = (stage_receipt_sha256 if isinstance(stage_receipt_sha256, dict)
                            else {})
    stage_names = (STAGES if expected_run_identity is None else
                   ("exporter", "decode", "original-exporter", "original-decode",
                    "refinement", "verifast"))
    details = {}
    for stage in stage_names:
        expected = (meta["expected_stages"][stage] if stage in STAGES else 0)
        callback_stages = (stages if stage in STAGES else original_export_stages)
        callback_key = stage if stage in STAGES else stage.removeprefix("original-")
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
                if expected_run_identity is not None:
                    source_match = (source_match and
                                    before.get("small_sort_source") ==
                                    expected_run_identity.get("source_sha256"))
                status = receipt.get("status") if isinstance(receipt, dict) else None
                status_ok = (status is None or
                             (isinstance(status, str) and
                              status in {"SUCCESS", "SUCCEEDED", "COMPLETED"}))
                code = receipt.get("exit_code") if isinstance(receipt, dict) else None
                ok = (isinstance(receipt, dict) and receipt.get("stage") == stage and
                      type(code) is int and code == expected and
                      type(callback_stages.get(callback_key)) is int and
                      callback_stages.get(callback_key) == expected and
                      receipt.get("source_unchanged") is True and source_match and status_ok)
                receipt_sha256 = _sha(path.read_bytes())
                identity_match = (expected_run_identity is None or
                                  (receipt.get("r10_run_identity") == expected_run_identity and
                                   stage_receipt_sha256.get(stage) == receipt_sha256))
                ok = ok and identity_match
                row = {"admitted": ok, "exit_code": code,
                       "callback_exit_code": callback_stages.get(callback_key),
                       "source_identity_matches": source_match,
                       "source_unchanged": receipt.get("source_unchanged")
                       if isinstance(receipt, dict) else None,
                       "status": status, "status_matches": status_ok}
                if expected_run_identity is not None:
                    row["run_identity_matches"] = identity_match
                    row["receipt_sha256"] = receipt_sha256
            except (OSError, json.JSONDecodeError, AttributeError) as error:
                row = {"admitted": False, "reason": f"invalid stage receipt: {error}"}
        details[stage] = row
        admitted = admitted and row["admitted"]
    return {"admitted": admitted, "stages": details}


def classify(name: str, case: Path, meta: dict, execution, *, expected_run_identity=None) -> dict:
    if not isinstance(execution, dict):
        execution = {"execution_receipt_error": "execute_case returned a non-object"}
    source_gate = _source_gate(case, meta, execution)
    stage_gate = _stage_gate(case, meta, execution.get("stages"),
                             expected_run_identity=expected_run_identity,
                             original_export_stages=execution.get("original_export_stages"),
                             stage_receipt_sha256=execution.get("r10_stage_receipt_sha256"))
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
    if selected not in SUPPORTED_PROFILES or profile.get("profile") != selected:
        raise ValueError("selected profile differs from the supported owner-array profile")
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


def _validated_r10_run_identity(validated_run, args, env: dict, binding: dict) -> dict:
    if not isinstance(validated_run, dict):
        raise ValueError("R10 validated parent run identity is required")
    selected = getattr(args, "profile", None)
    profile = validated_run.get("profile")
    if profile != selected or profile not in SUPPORTED_PROFILES:
        raise ValueError("R10 parent profile differs from the selected profile")
    build_id = validated_run.get("cloud_build_id")
    provider = validated_run.get("provider")
    if not isinstance(build_id, str):
        raise ValueError("R10 parent Cloud Build UUID is absent")
    try:
        if str(uuid.UUID(build_id)) != build_id:
            raise ValueError
    except (ValueError, AttributeError):
        raise ValueError("R10 parent Cloud Build UUID is malformed") from None
    if (not isinstance(provider, dict) or provider.get("provider") != "cloud-build" or
            provider.get("build_id") != build_id or
            not isinstance(provider.get("project"), str) or not provider["project"] or
            not isinstance(provider.get("region"), str) or not provider["region"]):
        raise ValueError("R10 parent provider identity differs from the Build UUID")
    current_build = env.get("CLOUD_BUILD_ID")
    current_proof = env.get("PROOF_SHA")
    if current_build != build_id or current_proof != validated_run.get("proof_sha"):
        raise ValueError("R10 parent Build/proof identity differs from current hosted environment")
    if (provider.get("project") != env.get("CLOUD_BUILD_PROJECT_ID") or
            provider.get("region") != env.get("CLOUD_BUILD_REGION")):
        raise ValueError("R10 parent provider project/region differs from current hosted environment")
    proof_sha = validated_run.get("proof_sha")
    source_sha = validated_run.get("source_sha256")
    profile_sha = validated_run.get("profile_sha256")
    tool_commit = validated_run.get("tool_commit")
    tool_hashes = validated_run.get("tool_sha256")
    if not isinstance(proof_sha, str) or not re.fullmatch(r"[0-9a-f]{40}", proof_sha):
        raise ValueError("R10 parent proof SHA is malformed")
    if not isinstance(source_sha, str) or not re.fullmatch(r"[0-9a-f]{64}", source_sha):
        raise ValueError("R10 parent source SHA is malformed")
    if profile_sha != binding["profile_sha256"]:
        raise ValueError("R10 parent profile SHA differs from current profile file")
    if tool_commit != binding["effective_tool_commit"]:
        raise ValueError("R10 parent effective tool commit differs from current profile")
    if not isinstance(tool_hashes, dict) or set(tool_hashes) != set(R10_TOOL_KEYS) or any(
            not isinstance(tool_hashes.get(key), str) or
            not re.fullmatch(r"[0-9a-f]{64}", tool_hashes[key]) for key in R10_TOOL_KEYS):
        raise ValueError("R10 parent tool binary SHA map is malformed or incomplete")
    tool_home = getattr(args, "tool_home", None)
    if tool_home is None:
        raise ValueError("R10 current tool-home path is unavailable")
    current_tool_hashes = {}
    for name, relative in (("vf-rust-mir-exporter", "bin/vf-rust-mir-exporter"),
                           ("verifast", "bin/verifast"),
                           ("refinement-checker", "bin/refinement-checker")):
        path = Path(tool_home) / relative
        if not path.is_file():
            raise ValueError(f"R10 current tool binary is missing: {name}")
        current_tool_hashes[name] = _sha(path.read_bytes())
    if current_tool_hashes != {key: tool_hashes[key] for key in R10_TOOL_KEYS}:
        raise ValueError("R10 parent tool binary SHA map differs from current tool binaries")
    return {"cloud_build_id": build_id, "proof_sha": proof_sha,
            "source_sha256": source_sha, "profile": profile,
            "profile_sha256": profile_sha, "tool_commit": tool_commit,
            "tool_sha256": {key: tool_hashes[key] for key in R10_TOOL_KEYS},
            "provider": {key: provider[key] for key in ("provider", "build_id", "project", "region")}}


def _case_run_identity(run_identity: dict, name: str, meta: dict, case: Path) -> dict:
    lines = (case / "verified/lib.rs").read_text().splitlines()
    target_line = meta["target"]["line"]
    identity = {**run_identity, "case": name,
                "case_source_sha256": {
                    "original/lib.rs": meta["original_sha256"],
                    "verified/lib.rs": meta["verified_sha256"]},
                "target": dict(meta["target"]),
                "target_source_line": lines[target_line - 1],
                "expected_class": meta["expected_class"],
                "expected_error": meta.get("expected_error")}
    identity["identity_sha256"] = _sha(json.dumps(
        identity, sort_keys=True, separators=(",", ":")).encode())
    return identity


def run(evidence: Path, args, env: dict, execute_case, *, validated_run=None) -> dict:
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
    run_identity = None
    if getattr(args, "profile", None) == R10_PROFILE:
        try:
            run_identity = _validated_r10_run_identity(validated_run, args, env, binding)
        except Exception as error:
            return {"schema": CAMPAIGN, **binding, "accepted": False, "proof_credit": False,
                    "classification": "INCONCLUSIVE", "r10_run_identity_error": str(error),
                    "cases": {name: _inconclusive(name, "R10 run identity unavailable")
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
        if run_identity is not None:
            manifest["r10_run_identity"] = run_identity
            case_identities = {}
            for name, meta in rows.items():
                case_identity = _case_run_identity(
                    run_identity, name, meta, evidence / name)
                case_identities[name] = case_identity
                meta["r10_run_identity"] = case_identity
                manifest["cases"][name]["r10_run_identity"] = case_identity
            manifest["r10_case_run_identities"] = case_identities
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
            case_identity = meta.get("r10_run_identity")
            if case_identity is not None:
                child_args.r10_run_identity = case_identity
                meta["r10_run_identity"] = case_identity
            execution = execute_case(case, child_args, env)
            results[name] = classify(name, case, meta, execution,
                                     expected_run_identity=case_identity)
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
    if run_identity is not None:
        aggregate["r10_run_identity"] = run_identity
        aggregate["r10_case_run_identities"] = {
            name: results[name].get("r10_run_identity") for name in CASES}
        aggregate["r10_receipt_scope"] = "SOURCE_REPORTED; no independent proof credit"
        aggregate["all_r10_case_receipts_bound"] = (
            set(aggregate["r10_case_run_identities"]) == set(CASES) and
            all(isinstance(aggregate["r10_case_run_identities"][name], dict) and
                results[name].get("stage_gate", {}).get("admitted") is True for name in CASES))
        if not aggregate["all_r10_case_receipts_bound"]:
            aggregate["all_classified"] = False
            aggregate["classification"] = "INCONCLUSIVE"
    try:
        (evidence / "aggregate.json").write_text(json.dumps(aggregate, indent=2, sort_keys=True) + "\n")
    except OSError:
        aggregate["classification"] = "INCONCLUSIVE"
        aggregate["all_classified"] = False
        aggregate["aggregate_write_error"] = "could not persist aggregate receipt"
    return aggregate
