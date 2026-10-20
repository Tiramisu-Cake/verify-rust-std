#!/usr/bin/env python3
"""Five isolated Cloud-only units for the canonical u64 share representation."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


CAMPAIGN = "r6-u64-share-representation-controls-v1"
HEADER = b"#![no_std]\n#![allow(dead_code)]\n"
STAGES = ("exporter", "decode", "refinement", "verifast")

CASES = {
    "positive": {
        "lemma": b"""lem r6_positive(k: lifetime_t, t: thread_id_t, p: *u64)
    req [_]frac_borrow(k, u64_full_borrow_content(t, p));
    ens [_](<u64>.share)(k, t, p);
{
    r6_close_u64_share(k, t, p); // TARGET: positive bridge call
}
""",
        "target": "positive bridge call", "class": "positive",
    },
    "missing_resource": {
        "lemma": b"""lem r6_missing_resource(k: lifetime_t, t: thread_id_t, p: *u64)
    req true;
    ens true;
{
    r6_close_u64_share(k, t, p); // TARGET: missing-resource bridge call
}
""",
        "target": "missing-resource bridge call", "class": "negative",
        "error_contains": "frac_borrow(k, u64_full_borrow_content(t, p))",
    },
    "wrong_referent": {
        "lemma": b"""lem r6_wrong_referent(k: lifetime_t, t: thread_id_t, p: *u64, q: *u64)
    req [_]frac_borrow(k, u64_full_borrow_content(t, p)) &*& p != q;
    ens true;
{
    r6_close_u64_share(k, t, q); // TARGET: wrong-referent bridge call
}
""",
        "target": "wrong-referent bridge call", "class": "negative",
        "error_contains": "frac_borrow(k, u64_full_borrow_content(t, q))",
    },
    "wrong_lifetime": {
        "lemma": b"""lem r6_wrong_lifetime(k: lifetime_t, k1: lifetime_t, t: thread_id_t, p: *u64)
    req [_]frac_borrow(k, u64_full_borrow_content(t, p)) &*& k != k1;
    ens true;
{
    r6_close_u64_share(k1, t, p); // TARGET: wrong-lifetime bridge call
}
""",
        "target": "wrong-lifetime bridge call", "class": "negative",
        "error_contains": "frac_borrow(k1, u64_full_borrow_content(t, p))",
    },
    "wrong_thread": {
        "lemma": b"""lem r6_wrong_thread(k: lifetime_t, t: thread_id_t, t1: thread_id_t, p: *u64)
    req [_]frac_borrow(k, u64_full_borrow_content(t, p)) &*& t != t1;
    ens true;
{
    r6_close_u64_share(k, t1, p); // TARGET: wrong-thread bridge call
}
""",
        "target": "wrong-thread bridge call", "class": "negative",
        "error_contains": "frac_borrow(k, u64_full_borrow_content(t1, p))",
    },
}


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _bridge_representation(representation: bytes) -> bytes:
    """Retain the exact predicate/bridge bytes and omit unrelated lemmas."""
    if not isinstance(representation, bytes) or not representation:
        raise TypeError("the exact nonempty representation bytes are required")
    marker = b"\nlem r6_u64_share_mono("
    start = representation.find(marker)
    if start < 0:
        return representation
    end = representation.rfind(b"@*/")
    if end < start:
        raise ValueError("representation has an unterminated monotonicity lemma")
    return representation[:start] + representation[end:]


def _unit(name: str, spec: dict, representation: bytes, verified: bool) -> bytes:
    runtime = b"pub fn r6_runtime_empty() {}\n"
    if not verified:
        return HEADER + runtime
    bridge = _bridge_representation(representation)
    if b"r6_close_u64_share" not in bridge:
        raise ValueError("representation bytes do not define the checked bridge")
    return HEADER + bridge + b"\n/*@\n" + spec["lemma"] + b"@*/\n" + runtime


def _bridge_req_line(verified: bytes) -> int:
    lines = verified.splitlines()
    starts = [i for i, line in enumerate(lines) if b"lem r6_close_u64_share(" in line]
    if len(starts) != 1:
        raise ValueError("expected exactly one r6_close_u64_share helper")
    body_start = next((i for i in range(starts[0] + 1, len(lines))
                       if lines[i].strip() == b"{"), None)
    if body_start is None:
        raise ValueError("bridge helper body is absent")
    reqs = [i for i in range(starts[0] + 1, body_start)
            if lines[i].lstrip().startswith(b"req ")]
    if len(reqs) != 1:
        raise ValueError("expected exactly one bridge precondition")
    return reqs[0] + 1


def prepare(evidence: Path, *, representation: bytes) -> dict:
    """Write four isolated Rust source pairs using the caller's exact bytes."""
    evidence = Path(evidence)
    if evidence.exists():
        raise FileExistsError(f"refusing to reuse R6 share-control evidence: {evidence}")
    if not isinstance(representation, bytes):
        raise TypeError("representation must be the exact bytes passed by the caller")
    bridge_representation = _bridge_representation(representation)
    evidence.mkdir(parents=True)
    rows = {}
    for name, spec in CASES.items():
        original = _unit(name, spec, representation, False)
        verified = _unit(name, spec, representation, True)
        target_lines = [i for i, line in enumerate(verified.splitlines(), 1)
                        if b"TARGET: " + spec["target"].encode() in line]
        if len(target_lines) != 1:
            raise ValueError(f"{name}: expected one unique bridge target")
        bridge_req_line = _bridge_req_line(verified)
        case = evidence / name
        for tree, content in (("original", original), ("verified", verified)):
            directory = case / tree
            directory.mkdir(parents=True)
            (directory / "lib.rs").write_bytes(content)
        rows[name] = {
            "case": name, "expected_class": spec["class"],
            "target": {"line": target_lines[0], "marker": spec["target"]},
            "bridge_req_line": bridge_req_line,
            "original_sha256": _sha(original), "verified_sha256": _sha(verified),
            "representation_sha256": _sha(representation),
            "embedded_bridge_representation_sha256": _sha(bridge_representation),
            "expected_stages": {stage: (1 if stage == "verifast" and spec["class"] == "negative" else 0)
                                for stage in STAGES},
            "error_contains": spec.get("error_contains"),
            "proof_credit": False,
        }
    (evidence / "manifest.json").write_text(json.dumps({
        "schema": CAMPAIGN, "accepted": False, "proof_credit": False,
        "representation_sha256": _sha(representation), "cases": rows,
        "embedded_bridge_representation_sha256": _sha(bridge_representation),
    }, indent=2, sort_keys=True) + "\n")
    return rows


def _stage_gate(case: Path, meta: dict, stages) -> dict:
    rows = {}
    admitted = isinstance(stages, dict)
    stages = stages if isinstance(stages, dict) else {}
    for stage in STAGES:
        path = case / f"{stage}-stage.json"
        expected = meta["expected_stages"][stage]
        row = {"admitted": False, "reason": "stage receipt is absent"}
        if path.is_file():
            try:
                receipt = json.loads(path.read_text())
                before = receipt.get("source_before") if isinstance(receipt, dict) else None
                after = receipt.get("source_after") if isinstance(receipt, dict) else None
                identity_ok = (isinstance(before, dict) and before == after and
                               before.get("original/lib.rs") == meta["original_sha256"] and
                               before.get("verified/lib.rs") == meta["verified_sha256"])
                status = receipt.get("status") if isinstance(receipt, dict) else None
                status_ok = status is None or status in {"SUCCESS", "SUCCEEDED", "COMPLETED"}
                ok = (isinstance(receipt, dict) and receipt.get("stage") == stage and
                      type(receipt.get("exit_code")) is int and receipt.get("exit_code") == expected and
                      type(stages.get(stage)) is int and stages.get(stage) == expected and
                      status_ok and receipt.get("source_unchanged") is True and identity_ok)
                row = {"admitted": ok, "exit_code": receipt.get("exit_code") if isinstance(receipt, dict) else None,
                       "callback_exit_code": stages.get(stage), "source_unchanged": receipt.get("source_unchanged") if isinstance(receipt, dict) else None,
                       "source_identity_matches": identity_ok, "status": status,
                       "status_matches": status_ok}
            except (OSError, json.JSONDecodeError, AttributeError) as error:
                row = {"admitted": False, "reason": f"invalid stage receipt: {error}"}
        rows[stage] = row
        admitted = admitted and row["admitted"]
    return {"admitted": admitted, "stages": rows}


def _source_gate(case: Path, meta: dict, execution: dict) -> dict:
    hashes = {}
    for relative in ("original/lib.rs", "verified/lib.rs"):
        path = case / relative
        hashes[relative] = _sha(path.read_bytes()) if path.is_file() else None
    admitted = (hashes == {"original/lib.rs": meta["original_sha256"],
                           "verified/lib.rs": meta["verified_sha256"]} and
                execution.get("source_unchanged_at_every_stage") is True)
    return {"admitted": admitted, "hashes_after": hashes}


def classify(name: str, case: Path, meta: dict, execution) -> dict:
    if not isinstance(execution, dict):
        execution = {"execution_receipt_error": "execute_case returned a non-object"}
    stages = execution.get("stages")
    stage_gate = _stage_gate(case, meta, stages)
    source_gate = _source_gate(case, meta, execution)
    log_path = case / "verifast.log"
    log = log_path.read_text(errors="replace") if log_path.is_file() else ""
    errors = re.findall(r"^.*\berror:.*$", log, re.M | re.I)
    target_line = meta["target"]["line"]
    bridge_req_error = (len(errors) == 1 and re.search(
        rf"verified/lib\.rs\({meta['bridge_req_line']},\d+(?:-\d+(?:,\d+)?)?\): error:", errors[0]) is not None)
    executed_lines = [int(line) for line in re.findall(
        r"verified/lib\.rs\((\d+),\d+(?:-\d+(?:,\d+)?)?\): (?:note: )?Executing statement", log)]
    target_executed = target_line in executed_lines
    before_error = log.split(errors[0], 1)[0] if errors else log
    return_before_error = "Executing return statement" in before_error
    pre_error_executed_lines = [int(line) for line in re.findall(
        r"verified/lib\.rs\((\d+),\d+(?:-\d+(?:,\d+)?)?\): (?:note: )?Executing statement",
        before_error)]
    last_execution_is_target = (bool(pre_error_executed_lines) and
                                pre_error_executed_lines[-1] == target_line)
    error_match = bool(errors and meta.get("error_contains") and meta["error_contains"] in errors[0])
    stages = stages if isinstance(stages, dict) else {}
    common = source_gate["admitted"] and stage_gate["admitted"]
    positive = (meta["expected_class"] == "positive" and common and
                stages.get("verifast") == 0 and not errors and target_executed and
                "Executing return statement" in log and "Leak check." in log and
                "0 errors found" in log)
    negative = (meta["expected_class"] == "negative" and common and
                stages.get("verifast") == 1 and bridge_req_error and error_match and
                target_executed and last_execution_is_target and len(errors) == 1)
    classification = ("PASS_CONTROL" if positive else "EXPECTED_REJECTION" if negative
                      else "INCONCLUSIVE")
    return {**execution, **meta, "case": name, "classification": classification,
            "accepted": False, "proof_credit": False,
            "source_gate": source_gate, "stage_gate": stage_gate,
            "bridge_req_error": bridge_req_error, "target_executed": target_executed,
            "last_execution_is_target": last_execution_is_target,
            "return_before_error": return_before_error,
            "error_match": error_match, "errors": errors,
            "evidence_class": "diagnostic representation control only; no actual std proof credit"}


def _inconclusive(name: str, reason: str) -> dict:
    return {"case": name, "classification": "INCONCLUSIVE", "accepted": False,
            "proof_credit": False, "reason": reason,
            "evidence_class": "setup/execution failure is not an intended negative"}


def run(evidence: Path, args, env: dict, execute_case, *, representation: bytes) -> dict:
    """Prepare controls and classify only exact hosted stage/execution receipts."""
    evidence = Path(evidence)
    if not callable(execute_case):
        return {"schema": CAMPAIGN, "accepted": False, "proof_credit": False,
                "classification": "INCONCLUSIVE", "cases": {
                    name: _inconclusive(name, "hosted execute_case callback is unavailable")
                    for name in CASES}}
    try:
        rows = prepare(evidence, representation=representation)
    except Exception as error:
        return {"schema": CAMPAIGN, "accepted": False, "proof_credit": False,
                "classification": "INCONCLUSIVE", "cases": {
                    name: _inconclusive(name, f"preparation failed: {error}") for name in CASES}}
    results = {}
    for name, meta in rows.items():
        case = evidence / name
        try:
            execution = execute_case(case, args, env)
            results[name] = classify(name, case, meta, execution)
        except Exception as error:
            results[name] = _inconclusive(name, f"execute_case/classification failed: {error}")
    classifications = {name: row["classification"] for name, row in results.items()}
    all_matched = (set(results) == set(CASES) and all(
        classifications[name] == ("PASS_CONTROL" if CASES[name]["class"] == "positive"
                                   else "EXPECTED_REJECTION") for name in CASES))
    aggregate = {"schema": CAMPAIGN, "accepted": False, "proof_credit": False,
                 "representation_sha256": _sha(representation), "all_matched": all_matched,
                 "classification": "DIAGNOSTIC_CONTROLS_CLASSIFIED" if all_matched else "INCONCLUSIVE",
                 "cases": classifications, "case_details": results,
                 "evidence_class": "bounded representation controls; not actual insert_tail proof"}
    try:
        (evidence / "aggregate.json").write_text(json.dumps(aggregate, indent=2, sort_keys=True) + "\n")
    except OSError:
        aggregate["classification"] = "INCONCLUSIVE"
        aggregate["all_matched"] = False
        aggregate["aggregate_write_error"] = "could not persist aggregate receipt"
    return aggregate
