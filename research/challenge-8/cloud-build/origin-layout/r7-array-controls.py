#!/usr/bin/env python3
"""Cloud-only controls for singleton u64 array witness normalization."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


CAMPAIGN = "r7-singleton-array-controls-v2"
HEADER = b"#![no_std]\n#![allow(dead_code)]\n"
STAGES = ("exporter", "decode", "refinement", "verifast")
EXPECTED_HELPER = b"""/*@
lem r7_guard_empty_tail(p: *u64)
    req [?f](*p |-> ?v);
    ens [f](*p |-> v) &*& [1/4]array::<u64>(p + 1, 0, nil);
{
    points_to_limits::<u64>(p);
    assert pointer_within_limits(p + 1) == true;
    close [1/4]array::<u64>(p + 1, 0, nil);
}
@*/
"""

CASES = {
    "positive": {
        "lemma": b"""lem r7_positive(p: *u64, v: u64)
    req [1/4](*p |-> v);
    ens [1/4]array::<u64>(p,1,cons(v,nil));
{
    points_to_limits::<u64>(p);
    r7_guard_empty_tail(p); // TARGET: singleton helper call
    close [1/4]array::<u64>(p,1,cons(v,nil));
}
""",
        "target": "singleton helper call", "class": "positive",
    },
    "missing_physical_quarter": {
        "lemma": b"""lem r7_missing_physical_quarter(p: *u64)
    req pointer_within_limits(p) == true &*& pointer_within_limits(p + 1) == true;
    ens true;
{
    r7_guard_empty_tail(p); // TARGET: missing physical quarter helper call
}
""",
        "target": "missing physical quarter helper call", "class": "negative",
        "error_at": "helper_req",
        "error_contains": "No matching heap chunks: [_]points_to<u64>(p, _)",
    },
    "wrong_referent": {
        "lemma": b"""lem r7_wrong_referent(p: *u64, q: *u64, v: u64)
    req [1/4](*p |-> v) &*& p != q;
    ens true;
{
    r7_guard_empty_tail(q); // TARGET: wrong referent helper call
}
""",
        "target": "wrong referent helper call", "class": "negative",
        "error_at": "helper_req",
        "error_contains": "No matching heap chunks: [_]points_to<u64>(q, _)",
    },
    "wrong_value": {
        "lemma": b"""lem r7_wrong_value(p: *u64, v: u64, w: u64)
    req [1/4](*p |-> v) &*& v != w;
    ens true;
{
    points_to_limits::<u64>(p);
    r7_guard_empty_tail(p);
    close [1/4]array::<u64>(p,1,cons(w,nil)); // TARGET: wrong value singleton close
}
""",
        "target": "wrong value singleton close", "class": "negative",
        "error_at": "spec", "error_file": "prelude_core.rsspec",
        "error_line": 264, "error_columns": "72-74",
        "error_contains": "Cannot prove condition. (Cannot prove cons(w, nil) = cons(v, nil).)",
    },
    "fractional_singleton_roundtrip": {
        "lemma": b"""lem r7_fractional_singleton_roundtrip(p: *u64)
    req [1/4]array::<u64>(p,1,?vs);
    ens [1/4]array::<u64>(p,1,vs);
{
    open [1/4]array::<u64>(p,1,vs);
    open [1/4]array::<u64>(p + 1,0,?rest);
    close [1/4]array::<u64>(p + 1,0,nil);
    close [1/4]array::<u64>(p,1,vs); // TARGET: fractional singleton rejoin
}
""",
        "target": "fractional singleton rejoin", "class": "positive",
    },
    "adjacent_nonempty_rejoin": {
        "lemma": b"""lem r7_adjacent_nonempty_rejoin(p: *u64)
    req [1/4]array::<u64>(p,2,?vs);
    ens [1/4]array::<u64>(p,2,vs);
{
    array_split::<u64>(p,1);
    open [1/4]array::<u64>(p,1,take(1,vs));
    open [1/4]array::<u64>(p + 1,0,_);
    close [1/4]array::<u64>(p + 1,0,nil);
    close [1/4]array::<u64>(p,1,take(1,vs));
    array_join::<u64>(p);
    assert [1/4]array::<u64>(p,2,vs); // TARGET: adjacent nonempty rejoin
}
""",
        "target": "adjacent nonempty rejoin", "class": "positive",
    },
    "post_drop_array3_reconstruction": {
        "lemma": b"""lem r7_post_drop_array3_reconstruction(p: *u64)
    req [1/4]array::<u64>(p,1,?first) &*& [1/4]array::<u64>(p + 1,1,?current) &*&
        [1/4]array::<u64>(p + 2,1,?last) &*& [1/4]array::<u64>(p + 2,0,nil) &*&
        [1/4]array::<u64>(p + 3,0,nil);
    ens [1/4]array::<u64>(p,3,append(first,append(current,last)));
{
    open [1/4]array::<u64>(p + 2,1,last);
    assert [1/4](*(p + 2) |-> ?r15_tail_current);
    open [1/4]array::<u64>(p + 3,0,_);
    close [1/4]array::<u64>(p + 3,0,nil);
    close [1/4]array::<u64>(p + 2,1,cons(r15_tail_current,nil));
    open [1/4]array::<u64>(p + 1,1,current);
    assert [1/4](*(p + 1) |-> ?r15_middle_current);
    open [1/4]array::<u64>(p + 2,0,_);
    close [1/4]array::<u64>(p + 2,0,nil);
    close [1/4]array::<u64>(p + 1,2,cons(r15_middle_current,cons(r15_tail_current,nil)));
    open [1/4]array::<u64>(p,1,first);
    assert [1/4](*p |-> ?r15_first_current);
    open [1/4]array::<u64>(p + 1,0,_);
    close [1/4]array::<u64>(p + 1,0,nil);
    close [1/4]array::<u64>(p,3,cons(r15_first_current,cons(r15_middle_current,cons(r15_tail_current,nil)))); // TARGET: post-Drop array-three reconstruction
    assert [1/4]array::<u64>(p,3,append(first,append(current,last)));
}
""",
        "target": "post-Drop array-three reconstruction", "class": "positive",
    },
    "array3_slice_full_borrow_roundtrip": {
        "lemma": b"""lem r16_drop_u64_owners(t: thread_id_t, vs: list<u64>)
    req foreach(vs, own::<u64>(t));
    ens true;
{
    open foreach(vs, own::<u64>(t));
    match vs {
        nil => { }
        cons(v, rest) => {
            open own::<u64>(t)(v);
            open u64_own(t, v);
            r16_drop_u64_owners(t, rest);
        }
    }
}

lem r16_make_u64_owners(t: thread_id_t, vs: list<u64>)
    req true;
    ens foreach(vs, own::<u64>(t));
{
    match vs {
        nil => { close foreach(nil, own::<u64>(t)); }
        cons(v, rest) => {
            r16_make_u64_owners(t, rest);
            close u64_own(t, v);
            close own::<u64>(t)(v);
            close foreach(vs, own::<u64>(t));
        }
    }
}

pred_ctor r16_array3_content(t: thread_id_t, p: *[u64; 3])() =
    *p |-> ?current &*& foreach(Array_elems(current), own::<u64>(t));

lem r16_array3_slice_full_borrow_roundtrip(k: lifetime_t, t: thread_id_t, p: *[u64; 3], s: *[u64])
    req full_borrow(k, r16_array3_content(t, p)) &*& s.len() == 3 &*& s as *u64 == p as *u64;
    ens full_borrow(k, r16_array3_content(t, p));
{
    produce_lem_ptr_chunk implies(r16_array3_content(t, p), slice_full_borrow_content::<u64>(t, s))(){
        open r16_array3_content(t, p)();
        Array_to_array(p);
        close slice_full_borrow_content::<u64>(t, s)();
    }{
        produce_lem_ptr_chunk implies(slice_full_borrow_content::<u64>(t, s), r16_array3_content(t, p))(){
            open slice_full_borrow_content::<u64>(t, s)();
            assert foreach(?r16_slice_current, own::<u64>(t));
            r16_drop_u64_owners(t, r16_slice_current);
            array_to_Array(p);
            assert *p |-> ?r16_array_current;
            r16_make_u64_owners(t, Array_elems(r16_array_current));
            close r16_array3_content(t, p)();
        }{
            full_borrow_implies(k, r16_array3_content(t, p), slice_full_borrow_content::<u64>(t, s));
            assert full_borrow(k, slice_full_borrow_content::<u64>(t, s));
            full_borrow_implies(k, slice_full_borrow_content::<u64>(t, s), r16_array3_content(t, p));
            assert full_borrow(k, r16_array3_content(t, p)); // TARGET: array-three slice full-borrow roundtrip
        }
    }
}
""",
        "target": "array-three slice full-borrow roundtrip", "class": "positive",
    },
    "array3_slice_wrong_metadata_length": {
        "lemma": b"""pred_ctor r16_array3_content(t: thread_id_t, p: *[u64; 3])() =
    *p |-> ?current &*& foreach(Array_elems(current), own::<u64>(t));

lem r16_array3_slice_wrong_metadata_length(k: lifetime_t, t: thread_id_t, p: *[u64; 3], s: *[u64])
    req full_borrow(k, r16_array3_content(t, p)) &*& s.len() == 4 &*& s as *u64 == p as *u64;
    ens full_borrow(k, r16_array3_content(t, p));
{
    assert s.len() == 3; // TARGET: reject array-three slice metadata length four
}
""",
        "target": "reject array-three slice metadata length four", "class": "negative",
        "error_at": "target", "error_contains": "Assertion might not hold. (Cannot prove ptr_len(s) = 3.)",
    },
    "nonempty_zero_witness": {
        "lemma": b"""lem r7_nonempty_zero_witness(p: *u64, v: u64)
    req pointer_within_limits(p) == true;
    ens true;
{
    close [1/4]array::<u64>(p,0,cons(v,nil)); // TARGET: reject nonempty count-zero witness
}
""",
        "target": "reject nonempty count-zero witness", "class": "negative",
        "error_at": "spec", "error_file": "prelude_core.rsspec",
        "error_line": 262, "error_columns": "16-18",
        "error_contains": "Cannot prove condition. (Cannot prove cons(v, nil) = nil.)",
    },
    "wrong_length_fold": {
        "lemma": b"""lem r7_wrong_length_fold(p: *u64, v: u64)
    req [1/4](*p |-> v) &*& [1/4]array::<u64>(p + 1,0,nil);
    ens true;
{
    points_to_limits::<u64>(p);
    close [1/4]array::<u64>(p,2,cons(v,nil)); // TARGET: reject singleton folded at length two
}
""",
        "target": "reject singleton folded at length two", "class": "negative",
        "error_at": "spec", "error_file": "prelude_core.rsspec",
        "error_line": 264, "error_columns": "27-32",
        "error_contains": "No matching heap chunks: [1/4]array<u64>(ptr_add_(p, 1, uint64_t_typeid), (2 - 1), _)",
    },
}

ARRAY3_BORROW_LIFECYCLE = {
    **CASES["array3_slice_full_borrow_roundtrip"],
    "target": "construct exact mutable slice metadata",
    "original_runtime": b"""pub unsafe fn r17_array3_slice_borrow_lifecycle(p: *mut [u64; 3]) -> *mut [u64] {
    let slice = core::ptr::slice_from_raw_parts_mut::<u64>(p as *mut u64, 3); // TARGET: construct exact mutable slice metadata
    slice
}
pub fn r7_runtime_empty() {}
""",
    "runtime": b"""pub unsafe fn r17_array3_slice_borrow_lifecycle(p: *mut [u64; 3]) -> *mut [u64]
/*@ req *p |-> ?current &*& foreach(Array_elems(current), own::<u64>(default_tid())); @*/
/*@ ens *p |-> ?restored_current &*&
        foreach(Array_elems(restored_current), own::<u64>(default_tid())) &*&
        full_borrow(?k, r16_array3_content(default_tid(), p));
@*/
{
    let slice = core::ptr::slice_from_raw_parts_mut::<u64>(p as *mut u64, 3); // TARGET: construct exact mutable slice metadata
    //@ close r16_array3_content(default_tid(), p)();
    //@ let k = begin_lifetime();
    //@ borrow(k, r16_array3_content(default_tid(), p));
    //@ r16_array3_slice_full_borrow_roundtrip(k, default_tid(), p, slice);
    //@ end_lifetime(k);
    //@ borrow_end(k, r16_array3_content(default_tid(), p));
    //@ open r16_array3_content(default_tid(), p)();
    slice
}
pub fn r7_runtime_empty() {}
""",
    "class": "positive",
}
CASES["array3_borrow_lifecycle"] = ARRAY3_BORROW_LIFECYCLE


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _unit(spec: dict, helper: bytes, verified: bool) -> bytes:
    runtime = spec.get("runtime", b"pub fn r7_runtime_empty() {}\n")
    if not verified:
        return HEADER + spec.get("original_runtime", runtime)
    return HEADER + helper + b"\n/*@\n" + spec["lemma"] + b"@*/\n" + runtime


def _helper_req_line(verified: bytes) -> int:
    lines = verified.splitlines()
    starts = [i for i, line in enumerate(lines) if b"lem r7_guard_empty_tail(" in line]
    if len(starts) != 1:
        raise ValueError("expected exactly one r7_guard_empty_tail helper")
    body_start = next((i for i in range(starts[0] + 1, len(lines))
                       if lines[i].strip() == b"{"), None)
    if body_start is None:
        raise ValueError("R7 helper body is absent")
    reqs = [i for i in range(starts[0] + 1, body_start)
            if lines[i].lstrip().startswith(b"req ")]
    if len(reqs) != 1:
        raise ValueError("expected exactly one R7 helper precondition")
    return reqs[0] + 1


def prepare(evidence: Path, *, helper: bytes) -> dict:
    """Write isolated source pairs using the caller's exact helper bytes."""
    evidence = Path(evidence)
    if evidence.exists():
        raise FileExistsError(f"refusing to reuse R7 array-control evidence: {evidence}")
    if not isinstance(helper, bytes) or helper != EXPECTED_HELPER:
        raise ValueError("helper bytes differ from the owner-authorized empty-tail helper")
    evidence.mkdir(parents=True)
    rows = {}
    for name, spec in CASES.items():
        original = _unit(spec, helper, False)
        verified = _unit(spec, helper, True)
        target_lines = [i for i, line in enumerate(verified.splitlines(), 1)
                        if b"TARGET: " + spec["target"].encode() in line]
        if len(target_lines) != 1:
            raise ValueError(f"{name}: expected one unique target statement")
        rows[name] = {
            "case": name, "expected_class": spec["class"],
            "target": {"line": target_lines[0], "marker": spec["target"]},
            "expected_error_line": (_helper_req_line(verified) if spec.get("error_at") == "helper_req"
                                     else target_lines[0] if spec.get("error_at") == "target" else None),
            "expected_error_location": ({"file": spec["error_file"], "line": spec["error_line"],
                                          "columns": spec["error_columns"]}
                                         if spec.get("error_at") == "spec" else None),
            "helper_sha256": _sha(helper),
            "original_sha256": _sha(original), "verified_sha256": _sha(verified),
            "expected_stages": {stage: (1 if stage == "verifast" and spec["class"] == "negative" else 0)
                                for stage in STAGES},
            "error_contains": spec.get("error_contains"),
            "proof_credit": False,
        }
        case = evidence / name
        for tree, content in (("original", original), ("verified", verified)):
            directory = case / tree
            directory.mkdir(parents=True)
            (directory / "lib.rs").write_bytes(content)
    (evidence / "manifest.json").write_text(json.dumps({
        "schema": CAMPAIGN, "accepted": False, "proof_credit": False,
        "helper_sha256": _sha(helper), "cases": rows,
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
                row = {"admitted": ok,
                       "exit_code": receipt.get("exit_code") if isinstance(receipt, dict) else None,
                       "callback_exit_code": stages.get(stage),
                       "source_unchanged": receipt.get("source_unchanged") if isinstance(receipt, dict) else None,
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
    executed_lines = [int(line) for line in re.findall(
        r"verified/lib\.rs\((\d+),\d+(?:-\d+(?:,\d+)?)?\): (?:note: )?Executing statement", log)]
    target_executed = target_line in executed_lines
    before_error = log.split(errors[0], 1)[0] if errors else log
    pre_error_executed_lines = [int(line) for line in re.findall(
        r"verified/lib\.rs\((\d+),\d+(?:-\d+(?:,\d+)?)?\): (?:note: )?Executing statement",
        before_error)]
    last_execution_is_target = (bool(pre_error_executed_lines) and
                                pre_error_executed_lines[-1] == target_line)
    expected_error_line = meta.get("expected_error_line")
    spec_location = meta.get("expected_error_location")
    if spec_location:
        expected_file = re.escape(spec_location["file"])
        expected_columns = re.escape(spec_location["columns"])
        error_at_expected_line = (len(errors) == 1 and re.search(
            rf"(?:^|/){expected_file}\({spec_location['line']},{expected_columns}\): error:",
            errors[0]) is not None)
    else:
        error_at_expected_line = (len(errors) == 1 and expected_error_line is not None and
            re.search(rf"verified/lib\.rs\({expected_error_line},\d+(?:-\d+(?:,\d+)?)?\): error:", errors[0]) is not None)
    error_match = bool(errors and meta.get("error_contains") and meta["error_contains"] in errors[0])
    stages = stages if isinstance(stages, dict) else {}
    common = source_gate["admitted"] and stage_gate["admitted"]
    positive = (meta["expected_class"] == "positive" and common and
                stages.get("verifast") == 0 and not errors and target_executed and
                "Executing return statement" in log and "Leak check." in log and
                "0 errors found" in log)
    negative = (meta["expected_class"] == "negative" and common and
                stages.get("verifast") == 1 and error_at_expected_line and error_match and
                target_executed and last_execution_is_target and len(errors) == 1)
    classification = "PASS_CONTROL" if positive else "EXPECTED_REJECTION" if negative else "INCONCLUSIVE"
    return {**execution, **meta, "case": name, "classification": classification,
            "accepted": False, "proof_credit": False,
            "source_gate": source_gate, "stage_gate": stage_gate,
            "target_executed": target_executed,
            "last_execution_is_target": last_execution_is_target,
            "error_at_expected_line": error_at_expected_line,
            "error_match": error_match, "errors": errors,
            "evidence_class": "isolated array control only; no actual std proof credit"}


def _inconclusive(name: str, reason: str, *, execution_failure=None) -> dict:
    row = {"case": name, "classification": "INCONCLUSIVE", "accepted": False,
           "proof_credit": False, "reason": reason,
           "evidence_class": "setup/execution failure is not an intended negative"}
    if execution_failure is not None:
        row["execution_failure"] = execution_failure
    return row


def _execution_failure(error: Exception) -> dict:
    """Retain the original hosted exception summary and any last receipt snapshot."""
    failure = {"type": f"{type(error).__module__}.{type(error).__qualname__}",
               "repr": repr(error), "args_repr": [repr(arg) for arg in error.args]}
    for name in ("exit_code", "returncode", "last_snapshot", "last_completed_snapshot"):
        if hasattr(error, name):
            value = getattr(error, name)
            try:
                json.dumps(value)
                failure[name] = value
            except (TypeError, ValueError):
                failure[name] = repr(value)
    return failure


def run(evidence: Path, args, env: dict, execute_case, *, helper: bytes) -> dict:
    """Prepare controls and classify exact hosted stage/execution receipts."""
    evidence = Path(evidence)
    if not callable(execute_case):
        return {"schema": CAMPAIGN, "accepted": False, "proof_credit": False,
                "classification": "INCONCLUSIVE", "cases": {
                    name: _inconclusive(name, "hosted execute_case callback is unavailable")
                    for name in CASES}}
    try:
        rows = prepare(evidence, helper=helper)
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
            results[name] = _inconclusive(
                name, f"execute_case/classification failed: {error}",
                execution_failure=_execution_failure(error))
    classifications = {name: row["classification"] for name, row in results.items()}
    all_matched = (set(results) == set(CASES) and all(
        classifications[name] == ("PASS_CONTROL" if meta["class"] == "positive"
                                   else "EXPECTED_REJECTION")
        for name, meta in CASES.items()))
    aggregate = {"schema": CAMPAIGN, "accepted": False, "proof_credit": False,
                 "helper_sha256": _sha(helper), "all_matched": all_matched,
                 "classification": "DIAGNOSTIC_CONTROLS_CLASSIFIED" if all_matched else "INCONCLUSIVE",
                 "cases": classifications, "case_details": results,
                 "evidence_class": "bounded isolated array controls; not actual insert_tail proof"}
    try:
        (evidence / "aggregate.json").write_text(json.dumps(aggregate, indent=2, sort_keys=True) + "\n")
    except OSError:
        aggregate["classification"] = "INCONCLUSIVE"
        aggregate["all_matched"] = False
        aggregate["aggregate_write_error"] = "could not persist aggregate receipt"
    return aggregate
