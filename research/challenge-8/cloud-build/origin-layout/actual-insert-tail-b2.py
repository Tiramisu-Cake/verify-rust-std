#!/usr/bin/env python3
"""Cloud-only causal fixture for the full, concrete-u64 actual insert_tail.

Preparation and imports are inert. The hosted merge runner supplies execute_case;
this module never starts a compiler, extractor, verifier, or Cloud Build itself.
This is an intentionally failing full-contract diagnostic until callback cleanup
and the moving-gap proof are derived from the actual caller resources.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCE = ROOT / "library/core/src/slice/sort/shared/smallsort.rs"
PINNED_SOURCE_SHA256 = "85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1"
PINNED_SOURCE_BLOB = "40939f922bcb6fdc7ee0d30427fa861827043827"
PINNED_DROP_SHA256 = "caff1edbfa3a8d9fd29459e49c43abd0f8f987f9061c75e7bf6ecedbbba26a6a"
PINNED_DROP_BYTES = 364
PINNED_INSERT_SHA256 = "9bc00f3913373e5879769b9970d66b1a56ada05a10205d51cafdf6533ecc2f29"
PINNED_INSERT_BYTES = 1380
CASE = "actual_three_current_full_posts"
PROFILE = "experimental-merge-actual-glue-body-v8"
INSERT_START = b"unsafe fn insert_tail<T, F: FnMut(&T, &T) -> bool>("
INSERT_END = b"\n}\n\n/// Sort `v` assuming"
DROP_START = b"struct CopyOnDrop<T> {\n"
DROP_END = b"}\n\nfn small_sort_network"
INSERT_SIGNATURE = (b"unsafe fn insert_tail<F: FnMut(&u64, &u64) -> bool>"
                    b"(begin: *mut u64, tail: *mut u64, is_less: &mut F)")
DROP_SIGNATURE = b"    fn drop(&mut self)"

# The entry owns the three initialized cells and the comparator through its
# ordinary &mut F parameter. There is no guard, receiver, FBC, origin or end
# token in this precondition. The wrapper must obtain the cells from its local.
INSERT_CONTRACT = b"""/*@
req thread_token(?t) &*& t == currentThread &*&
    type_interp::<u64>() &*& type_interp::<F>() &*&
    begin[..3] |-> ?xs &*& length(xs) == 3 &*&
    foreach(xs, own::<u64>(t)) &*& tail == begin + 2 &*&
    *is_less |-> ?f0 &*& <F>.own(t, f0);
@*//*@
ens thread_token(t) &*& type_interp::<u64>() &*& type_interp::<F>() &*&
    begin[..3] |-> ?normal_current &*& length(normal_current) == 3 &*&
    foreach(normal_current, own::<u64>(t)) &*&
    *is_less |-> ?normal_f &*& <F>.own(t, normal_f);
@*//*@
on_unwind_ens thread_token(t) &*& type_interp::<u64>() &*& type_interp::<F>() &*&
    begin[..3] |-> ?panic_current &*& length(panic_current) == 3 &*&
    foreach(panic_current, own::<u64>(t)) &*&
    *is_less |-> ?panic_f &*& <F>.own(t, panic_f);
@*/"""

# A real local array exercises the source-owned call; its only incoming state
# is a canonical comparator borrow. The actual callee contract above is the
# proof target. Local cleanup and a checked F post remain wrapper obligations.
WRAPPER_SIGNATURE = b"pub unsafe fn b2_three_from_local<F: FnMut(&u64, &u64) -> bool>(is_less: &mut F)"
WRAPPER_RUNTIME = b"""
pub unsafe fn b2_three_from_local<F: FnMut(&u64, &u64) -> bool>(is_less: &mut F)
{
    let mut values = [10_u64, 20_u64, 5_u64];
    let begin = values.as_mut_ptr();
    insert_tail(begin, begin.add(2), is_less);
}
"""
WRAPPER_CONTRACT = b"""/*@
req thread_token(?t) &*& t == currentThread &*&
    type_interp::<u64>() &*& type_interp::<F>() &*&
    *is_less |-> ?f0 &*& <F>.own(t, f0);
@*//*@
ens thread_token(t) &*& type_interp::<u64>() &*& type_interp::<F>() &*&
    *is_less |-> ?normal_f &*& <F>.own(t, normal_f);
@*//*@
on_unwind_ens thread_token(t) &*& type_interp::<u64>() &*& type_interp::<F>() &*&
    *is_less |-> ?panic_f &*& <F>.own(t, panic_f);
@*/"""


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"pinned module unavailable: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git_blob(data: bytes) -> str:
    import hashlib as _hashlib
    return _hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def _once(data: bytes, before: bytes, after: bytes, label: str) -> bytes:
    if data.count(before) != 1:
        raise ValueError(f"{label}: source anchor is not unique")
    return data.replace(before, after, 1)


def _line(data: bytes, anchor: bytes) -> int:
    if data.count(anchor) != 1:
        raise ValueError(f"source line anchor is not unique: {anchor!r}")
    return data[:data.index(anchor)].count(b"\n") + 1


def _extract(raw: bytes, start: bytes, end: bytes, included_end: bytes) -> bytes:
    if raw.count(start) != 1 or raw.count(end) != 1:
        raise ValueError("actual source extraction anchors changed")
    left = raw.index(start)
    right = raw.index(end, left)
    if not end.startswith(included_end):
        raise ValueError("source extraction end suffix changed")
    return raw[left:right + len(included_end)]


def _specialize_drop(data: bytes) -> bytes:
    data = data.replace(b"CopyOnDrop<T>", b"CopyOnDrop")
    data = data.replace(b"impl<T> Drop", b"impl Drop")
    data = re.sub(rb"\bT\b", b"u64", data)
    if re.search(rb"\bT\b|CopyOnDrop<T>|impl<T>", data):
        raise ValueError("unsubstituted generic Drop token")
    return data


def _specialize_insert(data: bytes) -> bytes:
    data = _once(data, INSERT_START,
                 b"unsafe fn insert_tail<F: FnMut(&u64, &u64) -> bool>(",
                 "insert_tail generic signature")
    data = re.sub(rb"\bT\b", b"u64", data)
    if re.search(rb"\bT\b", data) or data.count(INSERT_SIGNATURE) != 1:
        raise ValueError("concrete insert_tail signature is not exact")
    return data


def _prepare(evidence: Path) -> dict:
    """Cloud preparation only; retain original/verified bytes for every stage."""
    if evidence.exists():
        raise FileExistsError(f"refusing to reuse B2 evidence: {evidence}")
    raw = SOURCE.read_bytes()
    if _sha(raw) != PINNED_SOURCE_SHA256 or _git_blob(raw) != PINNED_SOURCE_BLOB:
        raise ValueError("actual SmallSort source pin changed")
    drop_raw = _extract(raw, DROP_START, DROP_END, b"}\n\n")
    if _sha(drop_raw) != PINNED_DROP_SHA256 or len(drop_raw) != PINNED_DROP_BYTES:
        raise ValueError("actual CopyOnDrop block pin changed")
    insert_raw = _extract(raw, INSERT_START, INSERT_END, b"\n}\n")
    if (_sha(insert_raw) != PINNED_INSERT_SHA256 or len(insert_raw) != PINNED_INSERT_BYTES):
        raise ValueError("actual insert_tail full-body pin changed")
    ordered_runtime = (
        b"let mut sift = tail.sub(1);",
        b"if !is_less(&*tail, &*sift) {",
        b"let tmp = ManuallyDrop::new(tail.read());",
        b"let mut gap_guard = CopyOnDrop { src: &*tmp, dst: tail, len: 1 };",
        b"ptr::copy_nonoverlapping(sift, gap_guard.dst, 1);",
        b"gap_guard.dst = sift;",
        b"if sift == begin {",
        b"sift = sift.sub(1);",
        b"if !is_less(&tmp, &*sift) {",
    )
    if (any(insert_raw.count(anchor) != 1 for anchor in ordered_runtime) or
            [insert_raw.index(anchor) for anchor in ordered_runtime] != sorted(
                insert_raw.index(anchor) for anchor in ordered_runtime) or
            insert_raw.count(b"if !is_less") != 2 or
            insert_raw.count(b"ptr::copy_nonoverlapping(sift, gap_guard.dst, 1);") != 1 or
            drop_raw.count(b"ptr::copy_nonoverlapping(self.src, self.dst, self.len);") != 1 or
            WRAPPER_RUNTIME.count(b"let mut values = [10_u64, 20_u64, 5_u64];") != 1 or
            WRAPPER_RUNTIME.count(b"insert_tail(begin, begin.add(2), is_less);") != 1 or
            b"/*@" in WRAPPER_RUNTIME or b"//@" in WRAPPER_RUNTIME or
            insert_raw.count(b"let tmp = ManuallyDrop::new(tail.read());") != 1 or
            insert_raw.count(b"let mut gap_guard = CopyOnDrop { src: &*tmp, dst: tail, len: 1 };") != 1 or
            insert_raw.count(b"ptr::copy_nonoverlapping(sift, gap_guard.dst, 1);") != 1 or
            insert_raw.count(b"gap_guard.dst = sift;") != 1 or
            insert_raw.count(b"if !is_less(&tmp, &*sift) {") != 1):
        raise ValueError("actual insertion runtime control-flow anchor changed")
    drop_body = _specialize_drop(drop_raw)
    insert_body = _specialize_insert(insert_raw)
    prefix = b"#![no_std]\nuse core::{mem::ManuallyDrop, ptr};\n\n"
    original = prefix + drop_body + b"\n" + insert_body + WRAPPER_RUNTIME

    # The checked selected Drop method is the same bounded one-cell contract
    # as B1. Keep its proof body in the unit so no unverified callee summary is
    # used. This only prepares the existing body proof; B2's caller resources
    # are still absent until the actual insertion establishes them.
    onecell = _load("b2_onecell_contract", HERE / "onecell-drop-interface.py")
    owned = _load("b2_guard_own", ROOT / "research/challenge-8/merge/overnight/guard-ownership/insertion-onecell/prepare.py")
    drop_contract = onecell._specialize(onecell.ONECELL_CONTRACT)
    source_own = onecell._specialize(owned.OWN).replace(
        b"[?f](*v.src |-> ?current)", b"[1/4](*v.src |-> ?current)")
    alignment = onecell._specialize_alignment_lemmas(owned.ALIGNMENT_LEMMA)
    source_geom = tuple(onecell._proof_syntax(onecell._specialize(item)).replace(
        b"gap_guard.src", b"guard_src").replace(b"gap_guard.dst", b"guard_dst")
        for item in owned.GEOMETRY)
    destination_geom = onecell._proof_syntax(onecell._specialize_alignment_lemmas(
        owned.DESTINATION_GEOMETRY)).replace(b"gap_guard.src", b"guard_src").replace(
            b"gap_guard.dst", b"guard_dst")
    source_alignment = onecell._proof_syntax(onecell._specialize_alignment_lemmas(
        owned.ALIGNMENT)).replace(b"gap_guard.src", b"guard_src")
    source_limits = onecell._proof_syntax(onecell._specialize(
        owned.SOURCE_LIMITS)).replace(b"gap_guard.src", b"guard_src")
    bridge = (onecell.FIELD_BIND + onecell.LEN_ONE + source_alignment +
              source_limits + b"".join(source_geom) + destination_geom +
              onecell.SOURCE_ARRAY + onecell.DEST_ARRAY + onecell.CALL +
              onecell.EFFECT_CLOSE)
    drop_contract = _once(drop_contract,
        b"    open CopyOnDrop_full_borrow_content(_t, self)();\n"
        b"    open <CopyOnDrop>.own(_t, *self);\n",
        b"    open CopyOnDrop_full_borrow_content(_t, self)();\n"
        b"    open <CopyOnDrop>.own(_t, *self);\n" + bridge,
        "checked selected Drop safety proof")
    verified = _once(original, DROP_SIGNATURE, DROP_SIGNATURE + drop_contract,
                     "actual selected Drop contract")
    verified = _once(verified, b"}\n\nimpl Drop for CopyOnDrop {",
                     b"}\n\n" + source_own + alignment +
                     b"/*@\n" + onecell.EFFECT_DEF + b"@*/\n\n" +
                     b"impl Drop for CopyOnDrop {", "guard predicates")
    verified = _once(verified, INSERT_SIGNATURE,
                     INSERT_SIGNATURE + INSERT_CONTRACT,
                     "full actual insert_tail safety contract")
    verified = _once(verified, WRAPPER_SIGNATURE,
                     WRAPPER_SIGNATURE + WRAPPER_CONTRACT,
                     "local three-cell wrapper contract")
    ghosts = (drop_contract, source_own, alignment,
              b"/*@\n" + onecell.EFFECT_DEF + b"@*/\n\n",
              INSERT_CONTRACT, WRAPPER_CONTRACT)
    stripped = verified
    for ghost in ghosts:
        stripped = _once(stripped, ghost, b"", "ghost strip")
    if stripped != original:
        raise ValueError("ghost stripping changed runtime bytes")
    if (original.count(b"insert_tail(begin, begin.add(2), is_less);") != 1 or
            original.count(b"ptr::copy_nonoverlapping(self.src, self.dst, self.len);") != 1 or
            original.count(b"ptr::copy_nonoverlapping(sift, gap_guard.dst, 1);") != 1 or
            verified.count(b"begin[..3] |-> ?normal_current") != 1 or
            verified.count(b"begin[..3] |-> ?panic_current") != 1 or
            verified.count(b"foreach(normal_current, own::<u64>(t))") != 1 or
            verified.count(b"foreach(panic_current, own::<u64>(t))") != 1 or
            any(token in verified for token in (
                b"assume_correct", b"//@ assume", b"//@ leak", b"ens true;",
                b"FreezeMarker", b"F: Copy", b"u64: Copy")) or
            b"on_unwind_ens false;" in INSERT_CONTRACT):
        raise ValueError("B2 full-source/full-post integrity gate failed")
    case = evidence / "cases" / CASE
    (case / "original").mkdir(parents=True)
    (case / "verified").mkdir()
    (case / "original/lib.rs").write_bytes(original)
    (case / "verified/lib.rs").write_bytes(verified)
    record = {
        "source_sha256": PINNED_SOURCE_SHA256,
        "source_git_blob": PINNED_SOURCE_BLOB,
        "actual_drop_sha256": PINNED_DROP_SHA256,
        "actual_insert_tail_sha256": PINNED_INSERT_SHA256,
        "actual_insert_tail_bytes": PINNED_INSERT_BYTES,
        "mechanically_specialized_insert_sha256": _sha(insert_body),
        "original_sha256": _sha(original), "verified_sha256": _sha(verified),
        "ghost_strip_exact": True, "profile": PROFILE,
        "actual_read_line": _line(verified, b"let tmp = ManuallyDrop::new(tail.read());"),
        "actual_first_pointer_line": _line(verified, b"let mut sift = tail.sub(1);"),
        "actual_first_call_line": _line(verified, b"if !is_less(&*tail, &*sift) {"),
        "actual_guard_line": _line(verified, b"let mut gap_guard = CopyOnDrop { src: &*tmp, dst: tail, len: 1 };"),
        "actual_shift_line": _line(verified, b"ptr::copy_nonoverlapping(sift, gap_guard.dst, 1);"),
        "actual_update_line": _line(verified, b"gap_guard.dst = sift;"),
        "actual_late_call_line": _line(verified, b"if !is_less(&tmp, &*sift) {"),
        "actual_drop_copy_line": _line(verified, b"ptr::copy_nonoverlapping(self.src, self.dst, self.len);"),
        "wrapper_line": _line(verified, b"let mut values = [10_u64, 20_u64, 5_u64];"),
        "target_normal_and_unwind": "full current initialized 3-cell array, one own per current value, current F/thread/type/frame",
        "expected_first_causal_blocker": "source line 540 tail.sub(1) pointer_within_limits, if three-cell array alone does not expose the interior bound; then first comparator loans at line 541",
        "proof_credit": False,
    }
    (evidence / "preparation.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    return record


def _classify(case: Path, record: dict, execution: dict, proof) -> dict:
    stages = execution.get("stages", {})
    source = (case / "verified/lib.rs").read_bytes()
    exact = (_sha(source) == record["verified_sha256"] and
             _sha((case / "original/lib.rs").read_bytes()) == record["original_sha256"] and
             execution.get("source_unchanged_at_every_stage") is True)
    mir_gate = {"admitted": False, "reason": "decoded MIR unavailable"}
    decoded = case / "decode.out"
    if decoded.is_file() and stages.get("decode") == 0:
        try:
            mir = proof.mir_helper
            tree = mir.CapnpText(decoded.read_text(errors="replace")).parse()
            bodies = [body for body in mir.path(tree, "bodies")
                      if mir.path(body, "defPath") == "insert_tail"]
            if len(bodies) == 1:
                calls, drops = [], []
                for index, block in enumerate(mir.path(bodies[0], "basicBlocks")):
                    kind = mir.path(block, "terminator", "kind")
                    if isinstance(kind, dict):
                        if "call" in kind:
                            calls.append({"block": index, "unwind": repr(mir.path(kind["call"], "unwindAction"))})
                        if "drop" in kind:
                            drops.append({"block": index, "cleanup": mir.path(block, "isCleanup"),
                                          "unwind": repr(mir.path(kind["drop"], "unwindAction"))})
                mir_gate = {"admitted": False,
                            "observed_minimal_shape": len(calls) >= 2 and len(drops) >= 2,
                            "call_edges": calls, "drop_edges": drops,
                            "reason": "exact late Call→cleanup Drop routing and unwind refinement remain unqualified"}
            else:
                mir_gate = {"admitted": False, "reason": "actual insert_tail MIR body is not unique",
                            "body_count": len(bodies)}
        except Exception as error:
            mir_gate = {"admitted": False, "reason": f"MIR parse failed closed: {error}"}
    ast_gate = {"admitted": False, "reason": "proof AST unavailable"}
    ast_path = case / "proof-ast.ml"
    if ast_path.is_file():
        try:
            ast = proof.ast_helper
            tree = ast.OcamlAstText(ast_path.read_text(errors="replace")).parse()
            functions = [node for node in ast.nodes(tree, "Func")
                         if len(node.args) == 13 and node.args[4] == "insert_tail" and
                         isinstance(node.args[10], ast.Node) and node.args[10].name == "Some"]
            calls = [node.args[1] for node in ast.nodes(functions[0].args[10], "CallExpr")
                     if len(functions) == 1 and len(node.args) > 1 and isinstance(node.args[1], str)]
            fnmut = [name for name in calls if name.endswith("FnMut::call_mut")]
            glue = [name for name in calls if name.endswith("__vf_generated_drop_glue")]
            ast_gate = {"admitted": False,
                        "observed_minimal_shape": len(functions) == 1 and len(fnmut) >= 2 and len(glue) >= 1,
                        "fnmut_call_nodes": len(fnmut), "generated_glue_call_nodes": len(glue),
                        "reason": "actual callback and cleanup nodes lack exact MIR outcome qualification"}
        except Exception as error:
            ast_gate = {"admitted": False, "reason": f"AST parse failed closed: {error}"}
    log_path = case / "verifast.log"
    log = log_path.read_text(errors="replace") if log_path.is_file() else ""
    errors = [line for line in log.splitlines() if re.search(r"\berror:", line, re.I)]
    dead = [line for line in log.splitlines() if "dead code" in line.lower()]
    reached_late = bool(re.search(rf"verified/lib\.rs\({record['actual_late_call_line']},\d+.*\): (?:note: )?Executing statement", log))
    return {"classification": "INCONCLUSIVE_CAUSAL_DIAGNOSTIC",
            "accepted": False, "proof_credit": False,
            "stages": stages, "source_exact": exact, "mir_gate": mir_gate,
            "ast_gate": ast_gate,
            "late_callback_executed": reached_late,
            "first_error": errors[0] if errors else None,
            "errors": errors, "dead_code": dead,
            "refinement_unwind_qualified": False,
            "full_normal_and_unwind_proved": False}


def run(evidence: Path, args, env: dict, execute_case, validated_receipt: dict) -> dict:
    """Use only from the existing hosted merge runner after B1 qualification."""
    if not callable(execute_case):
        raise TypeError("hosted execute_case callback required")
    profile_path = os.environ.get("SMALLSORT_MERGE_PROFILE")
    if not profile_path or json.loads(Path(profile_path).read_text()).get("profile") != PROFILE:
        raise RuntimeError("B2 requires the exact qualified generated-glue v8 profile")
    consumer = _load("b2_receipt_gate", HERE / "concrete-consumer.py")
    proof = _load("b2_hosted_proof", ROOT / "research/challenge-8/merge/overnight/copy-on-drop-prove.py")
    provider, proof_sha = proof.require_hosted_cloud()
    receipt = consumer._validate_receipt(args, validated_receipt, provider, proof_sha)
    record = _prepare(evidence)
    (evidence / "receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    case = evidence / "cases" / CASE
    before = consumer._hashes(case)
    execution = execute_case(case, args, env)
    after = consumer._hashes(case)
    execution["stage_receipt_gate"] = consumer._stage_receipts(case, execution.get("stages", {}), before)
    execution["source_unchanged_at_every_stage"] = (before == after and
        execution["stage_receipt_gate"].get("admitted") is True)
    result = _classify(case, record, execution, proof)
    (case / "classification.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    aggregate = {"schema": "actual-insert-tail-b2-causal-v1", "accepted": False,
                 "proof_credit": False, "profile": PROFILE, "case": CASE,
                 "classification": result["classification"],
                 "first_error": result["first_error"],
                 "late_callback_executed": result["late_callback_executed"],
                 "refinement_unwind_qualified": False}
    (evidence / "aggregate.json").write_text(json.dumps(aggregate, indent=2, sort_keys=True) + "\n")
    return aggregate
