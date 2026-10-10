#!/usr/bin/env python3
"""Hosted-only bounded normal composition of the one-cell constructor and copy body.

Import and source preparation are inert.  The hosted runner supplies the only
verification callback; this file never starts a compiler or verifier locally.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCE = ROOT / "library/core/src/slice/sort/shared/smallsort.rs"
PREP = ROOT / "research/challenge-8/merge/overnight/guard-ownership/insertion-onecell/prepare.py"
ONECELL = HERE / "onecell-drop-interface.py"
CONSUMER = HERE / "concrete-consumer.py"
CASES = ("positive", "after_call_current_false", "caller_entry_false")
PROFILE = "experimental-merge-qualified-guard-onecell-v1"
HELPER_NAME = b"checked_len1_body"
CALL = b"        checked_len1_body(guard_ptr);\n"
POINTER = b"        let guard_ptr = &raw mut gap_guard;\n"
CALLER_NAME = b"unsafe fn composed_onecell(tail: *mut u64)"
BODY_COPY = b"            ptr::copy_nonoverlapping((*guard).src, (*guard).dst, (*guard).len);\n"
AFTER_FALSE = b"        //@ assert false; // TARGET: after checked body CURRENT effect\n"
ENTRY_FALSE = b"        //@ assert false; // TARGET: caller supplies checked body entry\n"


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


def _line(data: bytes, token: bytes) -> int:
    if data.count(token) != 1:
        raise ValueError(f"expected exactly one source anchor: {token!r}")
    return data[:data.index(token)].count(b"\n") + 1


def _once(data: bytes, old: bytes, new: bytes, label: str) -> bytes:
    if data.count(old) != 1:
        raise ValueError(f"{label}: source anchor missing or duplicated")
    return data.replace(old, new, 1)


def _ghost(fragment: bytes) -> bytes:
    lines = fragment.splitlines()
    if not lines or any(not line.startswith(b"    ") for line in lines):
        raise ValueError("expected four-space-indented proof statements")
    return b"".join(b"        //@ " + line[4:] + b"\n" for line in lines)


def _source_parts(body, prep):
    source, _, drop_original, _, copy_call, own, alignment = body._source_inputs()
    raw = SOURCE.read_bytes()
    if (raw.count(prep.READ) != 1 or raw.count(prep.GUARD) != 1 or
            raw.index(prep.GUARD) != raw.index(prep.READ) + len(prep.READ) or
            copy_call.strip() != b"ptr::copy_nonoverlapping(self.src, self.dst, self.len);"):
        raise ValueError("actual read/constructor/Drop-body source anchors changed")
    marker = b"impl Drop for CopyOnDrop {\n"
    if drop_original.count(marker) != 1:
        raise ValueError("mechanically specialized Drop block changed")
    prefix, drop_part = drop_original.split(marker, 1)
    if (prefix.count(b"struct CopyOnDrop {\n") != 1 or
            drop_part.count(copy_call) != 1 or
            drop_part.count(b"    fn drop(&mut self) {\n") != 1):
        raise ValueError("Drop body cannot be uniquely mapped to helper")
    runtime = (b"unsafe fn checked_len1_body(guard: *mut CopyOnDrop) {\n"
               b"    unsafe {\n" + BODY_COPY + b"    }\n}\n\n")
    if (BODY_COPY.strip() != copy_call.strip().replace(b"self.src", b"(*guard).src")
            .replace(b"self.dst", b"(*guard).dst").replace(b"self.len", b"(*guard).len")):
        raise ValueError("helper body is not the exact field-receiver substitution")
    struct = prefix.replace(b"use core::ptr;", b"use core::{mem::ManuallyDrop, ptr};", 1)
    if struct.count(b"use core::{mem::ManuallyDrop, ptr};") != 1:
        raise ValueError("specialized import anchor changed")
    return source, struct, runtime, own, alignment, copy_call


def _helper_contract(body):
    contract = body._specialize(body.ONECELL_CONTRACT)
    contract = contract.replace(b"(*self)", b"(*guard)").replace(
        b"struct_CopyOnDrop_padding(self)", b"struct_CopyOnDrop_padding(guard)")
    proof_open = (b"    open CopyOnDrop_full_borrow_content(_t, self)();\n"
                  b"    open <CopyOnDrop>.own(_t, *self);\n")
    # This helper already requires the exact singleton arrays and geometry.
    # Reopening own/FBC here would invent a second physical guard frame; that
    # conversion belongs to the caller and is checked at its call site.
    bridge = body.CALL + b"    close CopyOnDrop_drop_effect(_t, src, dst, len);\n"
    contract = _once(contract, proof_open, bridge, "strong helper proof")
    payload_ens = (b"ens thread_token(t) &*& type_interp::<u64>() &*&\n"
                   b"    (*guard).src |-> src &*& (*guard).dst |-> dst &*& (*guard).len |-> 1 &*&\n"
                   b"    struct_CopyOnDrop_padding(guard) &*&\n"
                   b"    [1/4]src[..1] |-> cons(current, nil) &*&\n"
                   b"    dst[..1] |-> cons(current, nil) &*& <u64>.own(t, current);")
    contract = _once(contract, payload_ens,
                     b"ens thread_token(t) &*&\n"
                     b"    (*guard).src |-> src &*& (*guard).dst |-> dst &*& (*guard).len |-> 1 &*&\n"
                     b"    struct_CopyOnDrop_padding(guard) &*&\n"
                     b"    CopyOnDrop_drop_effect(t, src, dst, 1);",
                     "helper effect post")
    if (b"(*self)" in contract or b"self)" in contract or
            b"on_unwind_ens false" not in contract or
            b"[1/4]src[..1] |-> cons(?current, nil)" not in contract):
        raise ValueError("strong helper contract retained old receiver or lost obligations")
    return contract


def _caller_proof(body, prep, consumer):
    # No standalone helper pre is given to the caller.  These chunks all come
    # from tail.read, the live guard initializer, and the established FBC.
    proof = (prep.SOURCE_IDENTITY + body._specialize_alignment_lemmas(prep.CONSTRUCTOR_GEOMETRY) +
             b"        //@ assert guard_ptr == &gap_guard as *mut CopyOnDrop; // LIVE: actual guard address\n"
             b"        //@ close <CopyOnDrop>.own(t, gap_guard);\n"
             b"        //@ close [1/2]CopyOnDrop_full_borrow_content(t, &gap_guard)();\n"
             b"        //@ open [1/2]CopyOnDrop_full_borrow_content(t, &gap_guard)();\n" +
             consumer.FBC_FIELD_FRAME + consumer.POST_FBC_LADDER +
             b"        //@ assert gap_guard.src |-> ?guard_src &*& gap_guard.dst |-> ?guard_dst &*& gap_guard.len |-> ?guard_len;\n"
             b"        //@ assert guard_src == held_ref &*& guard_dst == tail &*& guard_len == 1;\n")
    proof += (body._specialize_alignment_lemmas(prep.ALIGNMENT) +
              body._specialize(prep.SOURCE_LIMITS) +
              b"".join(body._specialize(item) for item in prep.GEOMETRY) +
              body._specialize_alignment_lemmas(prep.DESTINATION_GEOMETRY))
    proof += (_ghost(body.SOURCE_ARRAY.replace(b"guard_src", b"guard_src")) +
              _ghost(body.DEST_ARRAY.replace(b"guard_dst", b"guard_dst")))
    proof += (
        b"        //@ assert thread_token(t) &*& type_interp::<u64>() &*& "
        b"gap_guard.src |-> guard_src &*& gap_guard.dst |-> guard_dst &*& "
        b"gap_guard.len |-> guard_len &*& struct_CopyOnDrop_padding(&gap_guard) &*& "
        b"[1/4]guard_src[..1] |-> cons(?entry_current, nil) &*& "
        b"guard_dst[..1] |-> _ &*& <u64>.own(t, entry_current); // ENTRY: actual resources\n")
    return proof


def _prepare(evidence: Path) -> dict:
    if evidence.exists():
        raise FileExistsError(f"refusing to reuse composition evidence: {evidence}")
    body = _load("composition_onecell", ONECELL)
    prep = _load("composition_prep", PREP)
    consumer = _load("composition_consumer", CONSUMER)
    source, struct, helper_runtime, own, alignment, source_copy = _source_parts(body, prep)
    helper_contract = _helper_contract(body)
    caller_contract = body._specialize(prep.CONTRACT)
    caller_runtime = (CALLER_NAME + b" {\n    unsafe {\n" + prep.READ + prep.GUARD +
                      POINTER + CALL + b"    }\n}\n")
    original = struct + helper_runtime + caller_runtime
    effect = b"/*@\n" + body.EFFECT_DEF + b"@*/\n\n"
    intro = own + alignment + effect
    annotations = prep.ANNOTATIONS
    caller_proof = _caller_proof(body, prep, consumer)
    recovery = body._specialize(prep.RECOVER).replace(b"gap_guard.src", b"recovery_src").replace(
        b"gap_guard.dst", b"recovery_dst")
    recovery = recovery.replace(b"        //@ end_ref_readonly(held_ref);\n",
                                consumer.POST_COPY_LADDER +
                                b"        //@ end_ref_readonly(held_ref);\n", 1)
    recovery_setup = (b"        //@ let recovery_src = held_ref;\n"
                      b"        //@ let recovery_dst = tail;\n")
    effect_open = b"        //@ open CopyOnDrop_drop_effect(t, recovery_src, recovery_dst, 1);\n"
    rows = {}
    for name in CASES:
        proof = caller_proof + (ENTRY_FALSE if name == "caller_entry_false" else b"")
        tail = effect_open + (AFTER_FALSE if name == "after_call_current_false" else b"") + recovery
        verified = _once(original, b"}\n\n" + b"unsafe fn checked_len1_body",
                         b"}\n\n" + intro + b"unsafe fn checked_len1_body",
                         "predicate placement")
        verified = _once(verified, b"unsafe fn checked_len1_body(guard: *mut CopyOnDrop)",
                         b"unsafe fn checked_len1_body(guard: *mut CopyOnDrop)" + helper_contract,
                         "helper contract")
        verified = _once(verified, CALLER_NAME, CALLER_NAME + caller_contract,
                         "caller contract")
        verified = _once(verified, prep.READ,
                         prep.READ + annotations + recovery_setup, "held reference setup")
        verified = _once(verified, POINTER, POINTER + proof, "guard resources")
        verified = _once(verified, CALL, CALL + tail, "normal return recovery")
        stripped = verified
        ghosts = (intro, helper_contract, caller_contract, annotations,
                  recovery_setup, proof, tail)
        for fragment in ghosts:
            stripped = _once(stripped, fragment, b"", "ghost strip")
        if stripped != original:
            raise ValueError(f"{name}: ghost stripping changed runtime adapter")
        case = evidence / "cases" / name
        (case / "original").mkdir(parents=True)
        (case / "verified").mkdir()
        (case / "original/lib.rs").write_bytes(original)
        (case / "verified/lib.rs").write_bytes(verified)
        rows[name] = {
            "case": name, "original_sha256": _sha(original),
            "verified_sha256": _sha(verified),
            "ghost_fragments": [fragment.decode("ascii") for fragment in ghosts],
            "read_line": _line(verified, prep.READ),
            "guard_line": _line(verified, prep.GUARD),
            "pointer_line": _line(verified, POINTER),
            "call_line": _line(verified, CALL),
            "helper_copy_line": _line(verified, BODY_COPY),
            "helper_call_proof_line": _line(verified, body.CALL),
            "effect_open_line": _line(verified, effect_open),
            "entry_line": _line(verified, b"// ENTRY: actual resources"),
            "false_line": (_line(verified, ENTRY_FALSE) if name == "caller_entry_false"
                           else _line(verified, AFTER_FALSE) if name == "after_call_current_false"
                           else None),
            "expected": ("pass" if name == "positive" else "after_call_false" if
                         name == "after_call_current_false" else "caller_entry_false"),
        }
    metadata = {
        "schema": "source-derived-u64-onecell-normal-composition-v1",
        "profile": PROFILE, "accepted": False,
        "source_sha256": source.SOURCE_SHA256,
        "source_git_blob": source.SOURCE_GIT_BLOB,
        "source_block_sha256": source.BLOCK_SHA256,
        "actual_drop_copy_sha256": _sha(source_copy),
        "helper_copy_sha256": _sha(BODY_COPY),
        "helper_runtime_sha256": _sha(helper_runtime),
        "adapter_runtime_sha256": _sha(caller_runtime),
        "source_mapping": "actual Drop body with only self.field to (*guard).field substitution; no Drop impl or compiler glue",
        "external_premises": "inherited u64 tail owner/geometry/thread/type_interp and no exercised unwind; all helper resources constructed by caller",
        "scope": "bounded u64 normal composition; no generic insert_tail, comparator, panic, compiler Drop glue, or actual method receiver-origin credit",
        "cases": rows,
    }
    (evidence / "extraction.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    return metadata


def _source_gate(case: Path, row: dict) -> dict:
    original = (case / "original/lib.rs").read_bytes()
    verified = (case / "verified/lib.rs").read_bytes()
    stripped = verified
    try:
        for text in row["ghost_fragments"]:
            stripped = _once(stripped, text.encode("ascii"), b"", "ghost strip")
        caller = original[original.index(CALLER_NAME):]
        helper = original[original.index(b"unsafe fn checked_len1_body"):original.index(CALLER_NAME)]
        admitted = (stripped == original and original.count(prep_read :=
                    b"let tmp = ManuallyDrop::new(tail.read());") == 1 and
                    original.count(b"let mut gap_guard = CopyOnDrop { src: &*tmp, dst: tail, len: 1 };") == 1 and
                    caller.count(CALL) == 1 and caller.count(POINTER) == 1 and
                    helper.count(BODY_COPY) == 1 and b"(*guard).len" in helper and
                    b"impl Drop for CopyOnDrop" not in original and
                    b"ptr::copy_nonoverlapping" not in caller and
                    b"on_unwind_ens false" in verified and
                    verified.count(b"pred CopyOnDrop_drop_effect") == 1 and
                    not any(x in verified for x in
                            (b"//@ assume", b"//@ leak", b"assume_correct", b"Freeze")))
        return {"admitted": admitted, "ghost_strip_equal": stripped == original,
                "actual_constructor": original.count(prep_read) == 1,
                "actual_dynamic_body_copy": helper.count(BODY_COPY) == 1,
                "no_compiler_drop_glue": b"impl Drop for CopyOnDrop" not in original}
    except Exception as error:
        return {"admitted": False, "reason": f"source gate failed: {error}"}


def _mir_gate(case: Path, row: dict, mir) -> dict:
    path = case / "decode.out"
    if not path.is_file():
        return {"admitted": False, "reason": "decoded MIR absent"}
    try:
        tree = mir.CapnpText(path.read_text(errors="replace")).parse()
        bodies = mir.path(tree, "bodies")
        helper = [b for b in bodies if mir.path(b, "defPath") == "checked_len1_body"]
        caller = [b for b in bodies if mir.path(b, "defPath") == "composed_onecell"]
        if len(helper) != 1 or len(caller) != 1:
            raise ValueError("helper/caller bodies are not each unique")
        def calls(b):
            out = []
            for block in mir.path(b, "basicBlocks"):
                kind = mir.path(block, "terminator", "kind")
                if isinstance(kind, dict) and "call" in kind:
                    call = kind["call"]
                    out.append((mir.call_name(call), mir.path(
                        call, "callSpan", "regular", "lo", "line")))
            return out
        hc, cc = calls(helper[0]), calls(caller[0])
        debug = mir.path(caller[0], "varDebugInfo")
        names = [mir.path(item, "name", "name") for item in debug]
        aggregates = []
        for block in mir.path(caller[0], "basicBlocks"):
            for statement in mir.path(block, "statements"):
                assignment = mir.assignment(statement)
                if assignment is None:
                    continue
                rhs = mir.path(assignment, "rhsRvalue")
                if not isinstance(rhs, dict) or "aggregate" not in rhs:
                    continue
                aggregate = rhs["aggregate"]
                adt = mir.path(aggregate, "aggregateKind", "adt")
                if isinstance(adt, dict) and mir.path(adt, "adtId", "name") == "CopyOnDrop":
                    aggregates.append((mir.path(statement, "sourceInfo", "span",
                                                "regular", "lo", "line"),
                                       len(mir.path(aggregate, "operands")),
                                       [mir.path(field, "name") for field in mir.path(adt, "fields")]))
        admitted = (len([x for x in hc if "copy_nonoverlapping" in x[0] and
                         x[1] == row["helper_copy_line"]]) == 1 and
                    len([x for x in cc if "checked_len1_body" in x[0] and
                         x[1] == row["call_line"]]) == 1 and
                    aggregates == [(row["guard_line"], 3, ["src", "dst", "len"])] and
                    "tmp" in names and "gap_guard" in names and "guard_ptr" in names and
                    not any("drop_in_place" in x[0] or "Drop::drop" in x[0] for x in cc))
        return {"admitted": admitted, "helper_calls": hc, "caller_calls": cc,
                "caller_live_debug_names": names, "constructor_aggregates": aggregates,
                "actual_body_copy_origin": "checked helper body only"}
    except Exception as error:
        return {"admitted": False, "reason": f"MIR gate failed closed: {error}"}


def _ast_gate(case: Path, row: dict, ast, body) -> dict:
    path = case / "proof-ast.ml"
    if not path.is_file():
        return {"admitted": False, "reason": "proof AST absent"}
    try:
        tree = ast.OcamlAstText(path.read_text(errors="replace")).parse()
        effect_definition = body._effect_definition_gate(case, tree, ast)
        funcs = [node for node in ast.nodes(tree, "Func") if len(node.args) == 13]
        helper = [node for node in funcs if node.args[4] == "checked_len1_body"]
        caller = [node for node in funcs if node.args[4] == "composed_onecell"]
        if len(helper) != 1 or len(caller) != 1:
            raise ValueError("AST helper/caller functions absent or duplicated")
        hc = [node for node in ast.nodes(helper[0].args[10], "CallExpr")
              if len(node.args) > 1 and isinstance(node.args[1], str)]
        cc = [node for node in ast.nodes(caller[0].args[10], "CallExpr")
              if len(node.args) > 1 and isinstance(node.args[1], str)]
        helper_copy = [n for n in hc if "copy_nonoverlapping" in n.args[1] and
                       ast.location_line(n.args[0]) == row["helper_copy_line"]]
        caller_call = [n for n in cc if "checked_len1_body" in n.args[1] and
                       ast.location_line(n.args[0]) == row["call_line"]]
        own = [n for n in ast.nodes(tree, "TypePredDef") if len(n.args) == 5 and
               n.args[3] == "own" and "CopyOnDrop" in repr(n.args[2])]
        fbc = [n for n in ast.nodes(tree, "PredCtorDecl") if len(n.args) == 7 and
               n.args[1] == "CopyOnDrop_full_borrow_content"]
        effect_decl = [n for n in ast.nodes(tree, "PredFamilyDecl") if
                       len(n.args) > 1 and n.args[1] == "CopyOnDrop_drop_effect"]
        effect_body = [n for n in ast.nodes(tree, "PredFamilyInstanceDecl") if
                       len(n.args) > 1 and n.args[1] == "CopyOnDrop_drop_effect"]
        closes = [n for n in ast.nodes(caller[0].args[10], "Close") if
                  "CopyOnDrop_full_borrow_content" in repr(n)]
        opens = [n for n in ast.nodes(caller[0].args[10], "Open") if
                 "CopyOnDrop_full_borrow_content" in repr(n)]
        admitted = (effect_definition.get("admitted") is True and
                    len(helper_copy) == len(caller_call) == len(own) == len(fbc) ==
                    len(effect_decl) == len(effect_body) == len(closes) == len(opens) == 1 and
                    "False" not in repr(own[0].args[4]) and
                    "False" not in repr(effect_body[0].args[5]) and
                    b"(*guard).src" in (case / "verified/lib.rs").read_bytes())
        return {"admitted": admitted, "helper_copy_count": len(helper_copy),
                "caller_helper_call_count": len(caller_call),
                "nonempty_own_count": len(own), "fbc_count": len(fbc),
                "effect_declaration_count": len(effect_decl),
                "effect_definition_count": len(effect_body),
                "effect_definition_gate": effect_definition,
                "caller_fbc_close_count": len(closes),
                "caller_fbc_open_count": len(opens),
                "caller_call_args": [repr(n.args) for n in caller_call]}
    except Exception as error:
        return {"admitted": False, "reason": f"AST gate failed closed: {error}"}


def _classify(case: Path, row: dict, execution: dict, mir, ast, body) -> dict:
    stages = execution.get("stages", {})
    source = _source_gate(case, row)
    mir_result = _mir_gate(case, row, mir) if stages.get("decode") == 0 else {"admitted": False}
    ast_result = _ast_gate(case, row, ast, body) if stages.get("decode") == 0 else {"admitted": False}
    log_path = case / "verifast.log"
    log = log_path.read_text(errors="replace") if log_path.is_file() else ""
    errors = [line for line in log.splitlines() if re.search(r"\berror:", line, re.I)]
    executed = lambda line: bool(re.search(
        rf"verified/lib\.rs\({line},\d+.*\): (?:note: )?Executing statement", log))
    setup = (execution.get("source_unchanged_at_every_stage") is True and
             all(stages.get(s) == 0 for s in ("exporter", "decode", "refinement")) and
             source["admitted"] and mir_result["admitted"] and ast_result["admitted"])
    positive = (setup and stages.get("verifast") == 0 and not errors and
                executed(row["helper_copy_line"]) and executed(row["call_line"]) and
                executed(row["effect_open_line"]) and "0 errors found" in log and
                "Executing return statement" in log and "Leak check." in log)
    negative = False
    if setup and stages.get("verifast") == 1 and len(errors) == 1 and row["false_line"]:
        negative = bool(re.search(
            rf"verified/lib\.rs\({row['false_line']},\d+-\d+\): error: "
            r"Assertion might not hold\. \(Cannot prove false\.\)", errors[0]))
        if row["expected"] == "after_call_false":
            negative = negative and executed(row["helper_copy_line"]) and executed(row["call_line"])
        if row["expected"] == "caller_entry_false":
            negative = negative and not executed(row["call_line"])
    classification = ("BOUNDED_NORMAL_COMPOSITION_PASS_FRAGMENT_ONLY" if
                      row["expected"] == "pass" and positive else
                      "EXPECTED_AFTER_CALL_CURRENT_REJECTION" if
                      row["expected"] == "after_call_false" and negative else
                      "EXPECTED_CALLER_ENTRY_REJECTION" if
                      row["expected"] == "caller_entry_false" and negative else
                      "INCONCLUSIVE")
    return {"case": row["case"], "classification": classification, "accepted": False,
            "source_gate": source, "mir_gate": mir_result, "ast_gate": ast_result,
            "stages": stages, "errors": errors, "targeted_negative": negative,
            "helper_copy_executed": executed(row["helper_copy_line"]),
            "caller_checked_call_executed": executed(row["call_line"]),
            "normal_effect_open_executed": executed(row["effect_open_line"]),
            "full_normal_return_and_leak": "Executing return statement" in log and "Leak check." in log,
            "actual_drop_glue_credit": False, "whole_insert_tail_credit": False}


def run(evidence: Path, args, env: dict, execute_case, validated_receipt: dict) -> dict:
    """Run only from the existing hosted Cloud runner after len1 qualification."""
    if not callable(execute_case):
        raise TypeError("hosted execute_case callback required")
    consumer = _load("composition_receipt_gate", CONSUMER)
    body = _load("composition_body_gate", ONECELL)
    prep = _load("composition_prep_gate", PREP)
    proof = _load("composition_hosted_proof", ROOT /
                  "research/challenge-8/merge/overnight/copy-on-drop-prove.py")
    provider, proof_sha = proof.require_hosted_cloud()
    receipt = consumer._validate_receipt(args, validated_receipt, provider, proof_sha)
    if evidence.exists():
        raise FileExistsError(f"refusing to reuse composition evidence: {evidence}")
    extraction = _prepare(evidence)
    (evidence / "receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    rows = {}
    for name, row in extraction["cases"].items():
        case = evidence / "cases" / name
        before = consumer._hashes(case)
        execution = execute_case(case, args, env)
        after = consumer._hashes(case)
        execution["stage_receipt_gate"] = consumer._stage_receipts(
            case, execution.get("stages", {}), before)
        execution["source_unchanged_at_every_stage"] = (
            before == after and execution["stage_receipt_gate"]["admitted"])
        result = _classify(case, row, execution, proof.mir_helper, proof.ast_helper, body)
        (case / "classification.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        rows[name] = result["classification"]
    complete = (rows.get("positive") == "BOUNDED_NORMAL_COMPOSITION_PASS_FRAGMENT_ONLY" and
                rows.get("after_call_current_false") == "EXPECTED_AFTER_CALL_CURRENT_REJECTION" and
                rows.get("caller_entry_false") == "EXPECTED_CALLER_ENTRY_REJECTION")
    aggregate = {"schema": "source-derived-u64-onecell-normal-composition-v1",
                 "accepted": False, "qualified_fragment": complete,
                 "profile": extraction["profile"], "receipt_sha256": receipt["receipt_sha256"],
                 "cases": rows, "actual_drop_glue_credit": False,
                 "whole_insert_tail_credit": False, "scope": extraction["scope"]}
    (evidence / "aggregate.json").write_text(json.dumps(aggregate, indent=2, sort_keys=True) + "\n")
    return aggregate
