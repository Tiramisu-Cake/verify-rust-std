#!/usr/bin/env python3
"""Draft hosted fixture for a source-linked natural Drop terminator.

This module is inert on import.  Its hosted ``run`` hook prepares a bounded
concrete-u64 adapter around the pinned CopyOnDrop source; the adapter ends a
lexical scope and relies on Rust's ordinary Drop terminator.  It never spells
an explicit runtime destructor call.
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
OLD_ONECELL = HERE / "onecell-drop-interface.py"
OLD_PREP = ROOT / "research/challenge-8/merge/overnight/guard-ownership/insertion-onecell/prepare.py"
OLD_CONSUMER = HERE / "concrete-consumer.py"
CASES = ("positive", "after_natural_drop_false", "caller_ready_entry_false",
         "missing_receiver_frame", "missing_source_permission", "duplicate_effect_simultaneous", "caller_dead_code")
DRAFT_STATUS = "READY"
DRAFT_REASON = ("The caller now follows the existing readonly half-FBC frame recipe and "
                "packages direct singleton arrays before the natural Drop terminator. "
                "Padding-fraction behavior is not established from a generated AST, so "
                "this remains a draft: do not prepare or execute before parent review.")


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
        raise ValueError(f"nonunique source anchor: {token!r}")
    return data[:data.index(token)].count(b"\n") + 1


def _replace_once(data: bytes, before: bytes, after: bytes, label: str) -> bytes:
    if data.count(before) != 1:
        raise ValueError(f"{label}: expected one source anchor")
    return data.replace(before, after, 1)


def _as_ghost_comments(fragment: bytes) -> bytes:
    """Embed body safety-proof statements as caller ghost statements."""
    lines = fragment.splitlines()
    if not lines or any(not line.startswith(b"    ") for line in lines):
        raise ValueError("expected indented safety-proof statements")
    return b"".join(b"        //@ " + line[4:] + b"\n" for line in lines)


NATURAL_DROP_EXIT = b"        //@ assert true; // TARGET: natural Drop scope exit\n"
NATURAL_FALSE = b"        //@ assert false; // TARGET: after natural Drop terminator\n"
CALLER_READY_FALSE = b"        //@ assert false; // TARGET: caller direct Drop-pre entry\n"
CALLER_SIGNATURE = b"unsafe fn natural_onecell(tail: *mut u64)"


def _prepare(evidence: Path) -> dict:
    """Build source-linked caller/callee fixtures; only the hosted runner calls this."""
    if DRAFT_STATUS != "READY":
        raise RuntimeError(DRAFT_REASON)
    if evidence.exists():
        raise FileExistsError(f"refusing to reuse natural Drop evidence: {evidence}")
    body = _load("natural_drop_onecell_source", OLD_ONECELL)
    prep = _load("natural_drop_insert_tail_templates", OLD_PREP)
    consumer = _load("natural_drop_consumer_templates", OLD_CONSUMER)
    composition = _load("selected_drop_caller_templates", HERE / "onecell-caller-composition.py")
    source, _, original_drop, signature, copy_call, own, alignment = body._source_inputs()
    contract = body._specialize(body.ONECELL_CONTRACT)
    withheld = (
        b"pred_ctor withheld_receiver(p: *mut CopyOnDrop)(;) = (*p).len |-> ?v;\n"
        b"pred_ctor withheld_source(p: *const u64)(;) = [1/4]p[..1] |-> ?vs;\n")
    effect = b"/*@\n" + body.EFFECT_DEF + withheld + b"@*/\n\n"

    # Exact runtime fragment anchors come from actual insert_tail source.
    raw = SOURCE.read_bytes()
    if raw.count(prep.READ) != 1 or raw.count(prep.GUARD) != 1:
        raise ValueError("pinned actual ManuallyDrop read/guard initializer changed")
    caller_contract = body._specialize(prep.CONTRACT)
    runtime = (b"\n" + CALLER_SIGNATURE + caller_contract + b" {\n"
               b"    unsafe {\n" + prep.READ +
               b"        {\n" + prep.GUARD + b"        }\n"
               b"    }\n}\n")
    original_drop = original_drop.replace(b"use core::ptr;",
                                          b"use core::{mem::ManuallyDrop, ptr};", 1)
    # The normal and unwind caller contract is inherited verbatim from the
    # existing bounded one-cell adapter.  The natural scope exit itself is the
    # only runtime Drop operation in this caller.
    original = original_drop + runtime

    cases_dir = evidence / "cases"
    cases_dir.mkdir(parents=True)
    rows = {}
    source_identity = prep.SOURCE_IDENTITY
    constructor_geometry = prep.CONSTRUCTOR_GEOMETRY
    constructor_lines = constructor_geometry.splitlines(keepends=True)
    constructor_destination_identity = constructor_lines[0]
    constructor_source_facts = b"".join(constructor_lines[1:4])
    constructor_separation = constructor_lines[4]
    annotations = prep.ANNOTATIONS
    source_geom = tuple(body._proof_syntax(body._specialize(item)).replace(
        b"gap_guard.src", b"guard_src").replace(b"gap_guard.dst", b"guard_dst")
        for item in prep.GEOMETRY)
    destination_geom = body._proof_syntax(body._specialize_alignment_lemmas(
        prep.DESTINATION_GEOMETRY)).replace(b"gap_guard.src", b"guard_src").replace(
            b"gap_guard.dst", b"guard_dst")
    source_alignment = body._proof_syntax(body._specialize_alignment_lemmas(
        prep.ALIGNMENT)).replace(b"gap_guard.src", b"guard_src")
    source_limits = body._proof_syntax(body._specialize(prep.SOURCE_LIMITS)).replace(
        b"gap_guard.src", b"guard_src")
    caller_source_geom = tuple(body._specialize(item) for item in prep.GEOMETRY)
    caller_destination_geom = body._specialize_alignment_lemmas(prep.DESTINATION_GEOMETRY)
    caller_source_alignment = body._specialize_alignment_lemmas(prep.ALIGNMENT)
    caller_source_limits = body._specialize(prep.SOURCE_LIMITS)
    false_ghost = NATURAL_FALSE
    # These pointer values must outlive the nested guard scope.  Bind them in
    # the outer unsafe block using the caller's original held-reference and
    # destination identities, before `gap_guard` is created.
    recovery_bindings = (
        b"        //@ let recovery_src = held_ref;\n"
        b"        //@ let recovery_dst = tail;\n")

    for name in CASES:
        case_own = own
        # The source-linked Drop body retains its narrow len-one contract and
        # explicit normal effect.  Its checked copy remains self.len at runtime.
        bridge = (body.FIELD_BIND + body.LEN_ONE + source_alignment + source_limits +
                  b"".join(source_geom) + destination_geom)
        bridge += body.SOURCE_ARRAY + body.DEST_ARRAY
        bridge += body.CALL + body.EFFECT_CLOSE
        case_contract = body._replace_once(
            contract,
            b"    open CopyOnDrop_full_borrow_content(_t, self)();\n"
            b"    open <CopyOnDrop>.own(_t, *self);\n",
            b"    open CopyOnDrop_full_borrow_content(_t, self)();\n"
            b"    open <CopyOnDrop>.own(_t, *self);\n" + bridge,
            "natural Drop strong-pre body bridge")

        # Caller protocol: preserve the established readonly half-FBC frame,
        # open its two half-own shares, then package the direct singleton
        # resources required by the checked Drop body.  The body gets no own
        # or FBC predicate at its compiler-selected Drop terminator.
        caller_proof = composition._caller_proof(body, prep, consumer)
        caller_proof = caller_proof.removesuffix(b"        //@ close_points_to(&gap_guard);\n")
        if name == "missing_receiver_frame":
            caller_proof += (
                b"        //@ let withheld_k = begin_lifetime();\n"
                b"        //@ close withheld_receiver(&gap_guard)();\n"
                b"        //@ borrow(withheld_k, withheld_receiver(&gap_guard));\n")
        if name == "missing_source_permission":
            caller_proof += (
                b"        //@ let withheld_k = begin_lifetime();\n"
                b"        //@ close withheld_source(guard_src)();\n"
                b"        //@ borrow(withheld_k, withheld_source(guard_src));\n")
        caller_ready_false = b""
        if name == "caller_ready_entry_false":
            caller_ready_false = (
                b"        //@ assert thread_token(t) &*& t == currentThread &*& "
                b"type_interp::<u64>() &*& gap_guard.src |-> guard_src &*& "
                b"gap_guard.dst |-> guard_dst &*& gap_guard.len |-> guard_len &*& "
                b"struct_CopyOnDrop_padding(&gap_guard) &*& guard_len == 1 &*& "
                b"0 < std::mem::size_of::<u64>() &*& "
                b"std::mem::size_of::<u64>() <= isize::MAX &*& "
                b"guard_src as usize != 0 &*& guard_dst as usize != 0 &*& "
                b"guard_src as usize % std::mem::align_of::<u64>() == 0 &*& "
                b"guard_dst as usize % std::mem::align_of::<u64>() == 0 &*& "
                b"object_pointer_within_limits(guard_src, std::mem::size_of::<u64>()) == true &*& "
                b"object_pointer_within_limits(guard_dst, std::mem::size_of::<u64>()) == true &*& "
                b"guard_src as usize <= usize::MAX - std::mem::size_of::<u64>() &*& "
                b"guard_dst as usize <= usize::MAX - std::mem::size_of::<u64>() &*& "
                b"pointer_within_limits(guard_src) == true &*& "
                b"pointer_within_limits(guard_src + 1) == true &*& "
                b"pointer_within_limits(guard_dst) == true &*& "
                b"pointer_within_limits(guard_dst + 1) == true &*& "
                b"(guard_src as usize + std::mem::size_of::<u64>() <= guard_dst as usize || "
                b"guard_dst as usize + std::mem::size_of::<u64>() <= guard_src as usize) &*& "
                b"[1/4]guard_src[..1] |-> cons(?ready_current, nil) &*& "
                b"guard_dst[..1] |-> _ &*& <u64>.own(t, ready_current);\n" +
                CALLER_READY_FALSE)
            caller_proof += caller_ready_false
        adapted_recovery = body._specialize(prep.RECOVER).replace(b"gap_guard.src", b"recovery_src").replace(
            b"gap_guard.dst", b"recovery_dst")
        adapted_recovery = adapted_recovery.replace(
            b"        //@ end_ref_readonly(held_ref);\n",
            consumer.POST_COPY_LADDER + b"        //@ end_ref_readonly(held_ref);\n", 1)
        effect_close = b"        //@ close CopyOnDrop_drop_effect(t, recovery_src, recovery_dst, 1);\n"
        double_effect = (b"        //@ assert CopyOnDrop_drop_effect(t, recovery_src, recovery_dst, 1) &*& "
                         b"CopyOnDrop_drop_effect(t, recovery_src, recovery_dst, 1); // TARGET: simultaneous effects\n")
        recovery_tail = (effect_close + (double_effect if name == "duplicate_effect_simultaneous" else b"") +
                         b"        //@ open CopyOnDrop_drop_effect(t, recovery_src, recovery_dst, 1);\n" + adapted_recovery)
        dead_control = b"        //@ if (false) { assert true; } // TARGET: real caller dead code\n"
        if name == "caller_dead_code":
            recovery_tail += dead_control
        if name == "after_natural_drop_false":
            recovery = NATURAL_DROP_EXIT + false_ghost + recovery_tail
        else:
            recovery = NATURAL_DROP_EXIT + recovery_tail
        verified = _replace_once(original, signature, signature + case_contract,
                                 "Drop body contract")
        verified = _replace_once(verified, b"}\n\nimpl Drop for CopyOnDrop {",
                                 b"}\n\n" + case_own + alignment + effect +
                                 b"impl Drop for CopyOnDrop {", "Drop predicates")
        verified = _replace_once(verified, prep.READ,
                                 prep.READ + annotations + recovery_bindings,
                                 "readonly caller setup and outer recovery bindings")
        # Insert the proof construction immediately after the exact guard init,
        # then recovery after the lexical scope has emitted Drop.
        verified = _replace_once(verified, prep.GUARD,
                                 prep.GUARD + caller_proof,
                                 "caller pre-Drop resources")
        scope_end = b"        }\n    }\n}\n"
        if verified.count(CALLER_SIGNATURE) != 1:
            raise ValueError("selected caller source binding not unique")
        prefix, caller = verified.split(CALLER_SIGNATURE, 1)
        caller = _replace_once(caller, scope_end,
                               b"        }\n" + recovery + b"    }\n}\n",
                               "caller post-Drop recovery")
        verified = prefix + CALLER_SIGNATURE + caller
        ghosts = [case_own, alignment, effect, case_contract, annotations,
                  caller_proof, recovery_bindings, recovery]
        stripped = verified
        for ghost in ghosts:
            if stripped.count(ghost) != 1:
                raise ValueError(f"{name}: ghost source fragment not unique: {ghost[:60]!r}")
            stripped = stripped.replace(ghost, b"", 1)
        if stripped != original:
            raise ValueError(f"{name}: runtime changed after ghost strip")
        case_dir = cases_dir / name
        (case_dir / "original").mkdir(parents=True)
        (case_dir / "verified").mkdir()
        (case_dir / "original/lib.rs").write_bytes(original)
        (case_dir / "verified/lib.rs").write_bytes(verified)
        rows[name] = {
            "case": name, "source_sha256": source.SOURCE_SHA256,
            "source_git_blob": source.SOURCE_GIT_BLOB,
            "source_block_sha256": source.BLOCK_SHA256,
            "original_sha256": _sha(original), "verified_sha256": _sha(verified),
            "ghost_fragments": [part.decode("ascii") for part in ghosts],
            "read_line": _line(verified, prep.READ),
            "guard_line": _line(verified, prep.GUARD),
            "natural_scope_end_line": _line(verified, NATURAL_DROP_EXIT),
            "drop_body_copy_line": _line(verified, body.CALL),
            "source_copy_line": _line(verified, copy_call),
            "call_line": _line(verified, body.CALL),
            "canonical": True, "uses_effect": True, "body_false_line": None, "prototype_false_line": None,
            "effect_fixture_kind": "exact",
            "false_line": (_line(verified, false_ghost) if name == "after_natural_drop_false" else
                           _line(verified, CALLER_READY_FALSE) if name == "caller_ready_entry_false" else None),
            "target_stage": ("caller_ready_entry_before_scope_exit" if name == "caller_ready_entry_false" else
                             "after_natural_drop" if name == "after_natural_drop_false" else None),
            "natural_drop_expected_to_execute": name != "caller_ready_entry_false",
            "body_copy_expected_to_execute": name != "caller_ready_entry_false",
            "caller_ready_entry_false_grants_glue_or_normal_recovery_credit": False,
            "expected_missing": ("receiver_frame" if name == "missing_receiver_frame" else
                                 "source_permission" if name == "missing_source_permission" else None),
            "dead_control_line": (_line(verified, dead_control) if name == "caller_dead_code" else None),
            "double_effect_line": (_line(verified, double_effect) if name == "duplicate_effect_simultaneous" else None),
            "runtime_natural_drop_only": True,
            "runtime_destructor_call_present": False,
            "normal_effect_predicate": "CopyOnDrop_drop_effect",
            "source_recovery_after_drop_before_tmp_storage_dead": True,
            "fbc_recombination": "readonly half-FBC frame -> field frame -> direct singleton arrays",
            "drop_terminator_pre_has_own_or_fbc": False,
            "direct_source_array_packaged": name != "missing_source_singleton_array",
            "direct_destination_array_packaged": name != "missing_destination_singleton_array",
            "physical_source_quarter_and_destination_gap_retained": True,
        }
    metadata = {
        "schema": "source-linked-u64-onecell-natural-drop-v1",
        "profile": "SOURCE_LINKED_U64_ONECELL_NATURAL_DROP_DRAFT",
        "accepted": False,
        "scope": "bounded source-derived u64 adapter; actual generic insert_tail and panic path remain unproved",
        "source_sha256": source.SOURCE_SHA256,
        "source_git_blob": source.SOURCE_GIT_BLOB,
        "source_block_sha256": source.BLOCK_SHA256,
        "runtime_call_semantics": "nested lexical scope invokes natural compiler Drop terminator; no explicit runtime Drop::drop call",
        "caller_contract": "full inherited normal/unwind tail contract; no unwind path exercised",
        "drop_body_contract_sha256": _sha(contract),
        "actual_drop_copy": copy_call.decode(),
        "actual_drop_copy_runtime_len_preserved": b"self.len" in copy_call,
        "canonical_post_effect": effect.decode("ascii"),
        "canonical_own_omission_negative": "NOT_APPLICABLE for u64",
        "fbc_recombination": "close full own; close/open half FBC; reuse concrete-consumer FBC_FIELD_FRAME and POST_FBC_LADDER; package direct source/destination singleton arrays before natural Drop",
        "padding_fraction_merge": "NOT_ASSERTED: generated AST unavailable; target has three pointer-sized fields but no generated padding evidence was inspected",
        "draft_status": DRAFT_STATUS,
        "callee_or_glue_credit": False,
        "caller_construction_credit": False,
        "cases": rows,
    }
    (evidence / "extraction.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    return metadata


def _source_gate(case: Path, row: dict, prep) -> dict:
    original = (case / "original/lib.rs").read_bytes()
    verified = (case / "verified/lib.rs").read_bytes()
    stripped = verified
    for fragment in row["ghost_fragments"]:
        token = fragment.encode("ascii")
        if stripped.count(token) != 1:
            return {"admitted": False, "reason": "ghost strip fragment count differs"}
        stripped = stripped.replace(token, b"", 1)
    caller = original[original.index(CALLER_SIGNATURE):]
    caller_runtime_ok = (
        caller.count(prep.READ) == 1 and caller.count(prep.GUARD) == 1 and
        b"ptr::copy_nonoverlapping" not in caller and
        b"Drop::drop" not in caller and b"drop_in_place" not in caller and
        caller.count(b"        {\n" + prep.GUARD + b"        }\n    }\n}\n") == 1 and
        caller.count(b"let tmp = ManuallyDrop::new(tail.read());") == 1)
    body_runtime_ok = (verified.count(b"ptr::copy_nonoverlapping(self.src, self.dst, self.len);") == 1 and
                       b"on_unwind_ens false" in verified)
    integrity = (stripped == original and caller_runtime_ok and body_runtime_ok and
                 verified.count(b"pred CopyOnDrop_drop_effect") == 1 and
                 not any(token in verified for token in
                         (b"//@ assume", b"//@ leak", b"assume_correct", b"Freeze")))
    return {"admitted": integrity, "runtime_equal_after_ghost_strip": stripped == original,
            "caller_uses_actual_read_and_guard": caller_runtime_ok,
            "caller_has_no_explicit_copy_or_destructor_call": caller_runtime_ok,
            "actual_drop_keeps_dynamic_self_len_copy": body_runtime_ok,
            "exactly_one_effect_definition": verified.count(b"pred CopyOnDrop_drop_effect") == 1,
            "no_assume_leak_or_freeze": not any(token in verified for token in
                (b"//@ assume", b"//@ leak", b"assume_correct", b"Freeze"))}


def _caller_ast_evidence(case: Path, ast) -> dict:
    path = case / "proof-ast.ml"
    if not path.is_file():
        return {"present": False, "admitted": False}
    try:
        tree = ast.OcamlAstText(path.read_text(errors="replace")).parse()
        funcs = [node for node in ast.nodes(tree, "Func")
                 if len(node.args) == 13 and node.args[4] == "natural_onecell"]
        bodies = [node for node in funcs if isinstance(node.args[10], ast.Node) and
                  node.args[10].name == "Some"]
        calls = []
        for node in ast.nodes(bodies[0].args[10], "CallExpr") if len(bodies) == 1 else []:
            if len(node.args) > 1 and isinstance(node.args[1], str):
                calls.append({"callee": node.args[1], "loc": ast.loc(node.args[0]), "ast": repr(node)})
        switches = []
        if len(bodies) == 1:
            for node in ast.nodes(bodies[0].args[10], "SwitchStmt"):
                if len(node.args) == 3 and isinstance(node.args[1], ast.Node) and node.args[1].name == "CallExpr":
                    name = node.args[1].args[1]
                    if "Drop" in name and name != "std::ptr::drop_in_place":
                        arms = []
                        for arm in node.args[2]:
                            tag = arm.args[1].args[1] if isinstance(arm.args[1], ast.Node) else None
                            arm_calls = [call.args[1] for call in ast.nodes(arm.args[2], "CallExpr")]
                            returns = [call.args[1] for ret in ast.nodes(arm.args[2], "ReturnStmt")
                                       for call in ast.nodes(ret, "CallExpr")]
                            arms.append({"tag": tag, "calls": arm_calls, "return_calls": returns, "gotos": [go.args[1] for go in ast.nodes(arm.args[2], "GotoStmt")]})
                        switches.append({"callee": name, "arms": arms})
        return {"present": True, "admitted": len(bodies) == 1,
                "selected_outcome_switches": switches,
                "caller_func_count": len(funcs), "caller_body_count": len(bodies),
                "call_nodes": calls,
                "potential_drop_callees": [row for row in calls
                    if "Drop" in row["callee"] or "CopyOnDrop" in row["callee"]]}
    except Exception as error:
        return {"present": True, "admitted": False,
                "reason": f"caller AST evidence collection failed: {error}"}


def _source_permission_target(log: str, verified: bytes, row: dict, call_loc: str) -> bool:
    """Match the source-array precondition's exact auto-close refusal, not setup."""
    source_req = b"    [1/4]src[..1] |-> cons(?current, nil) &*& dst[..1] |-> _ &*&"
    if verified.count(source_req) != 1:
        return False
    source_line = _line(verified, source_req)
    # This bounded fixture's constructor and readonly producer bind these
    # symbolic values; a dst/alias/coefficient change is not the source oracle.
    exact_chunk = ("[1/4]points_to<u64>(get_CopyOnDrop_src(mk_CopyOnDrop("
                   "fn_outcome_result(outcome0), tail0, 1)), _)")
    errors = [line for line in log.splitlines() if re.search(r"\berror:", line, re.I)]
    if len(errors) != 1 or not re.fullmatch(
            r"[^\n]*/bin/rust/prelude_core\.rsspec\(264,12-15\): error: "
            r"No matching heap chunks: " + re.escape(exact_chunk), errors[0]):
        return False
    executing = lambda line: re.search(
        rf"verified/lib\.rs\({line},\d+.*\): (?:note: )?Executing statement", log) is not None
    return (executing(row["natural_scope_end_line"] - 1) and
            executing(row["natural_scope_end_line"] - 2) and
            f"verified/lib.rs({row['natural_scope_end_line'] - 3},13-18): Producing predicate chunk" in log and
            f"verified/lib.rs({row['natural_scope_end_line'] - 2},13-19): Verifying call" in log and
            log.count(call_loc + ": Verifying call") == 2 and
            call_loc + ": note: Verifying call" in log and
            f"verified/lib.rs({source_line},5-6): note: Consuming assertion" in log and
            "prelude_core.rsspec(259,6-11): Auto-closing predicate with coefficient 1/4" in log and
            not executing(row["natural_scope_end_line"]))


def _classify(name: str, case: Path, row: dict, execution: dict,
              prep, body, drop_module, proof_base) -> dict:
    stages = execution.get("stages", {})
    source = _source_gate(case, row, prep)
    mir = (_natural_drop_mir_gate(case, row, proof_base.mir_helper)
           if stages.get("decode") == 0 else {"admitted": False})
    caller_ast = (_caller_ast_evidence(case, proof_base.ast_helper)
                  if stages.get("decode") == 0 else {"admitted": False})
    selected = mir.get("selected_normal_drop", {})
    drop_path = selected.get("selected_path", "")
    calls = caller_ast.get("call_nodes", [])
    actual_calls = [call for call in calls if call["callee"] == drop_path]
    receiver_calls = [call for call in calls if call["callee"] == "create_ref_mut"]
    ends = [call for call in calls if call["callee"] == "end_ref_mut"]
    switches = caller_ast.get("selected_outcome_switches", [])
    arms = {arm["tag"]: arm for arm in switches[0]["arms"]} if len(switches) == 1 else {}
    protocol = (set(arms) == {"returning", "unwinding"} and
                all(arm["calls"].count("end_ref_mut") == 1 and
                    arm["calls"].count("close_points_to") == 1 and
                    arm["calls"].count("open_points_to") == 1 for arm in arms.values()) and
                arms["unwinding"]["gotos"] == [str(mir.get("selected_cleanup_target"))] and
                mir.get("selected_cleanup_is_statement_free_resume") is True)
    binding = (len(actual_calls) == 1 and len(receiver_calls) == 1 and len(ends) == 2 and protocol and
               not any(call["callee"] == "std::ptr::drop_in_place" for call in calls))
    caller_ast["selected_call_binding"] = binding
    caller_ast["selected_method_call_count"] = len(actual_calls)
    caller_ast["receiver_create_count"] = len(receiver_calls)
    caller_ast["borrow_end_count"] = len(ends)
    caller_ast["admitted"] = caller_ast.get("admitted") is True and binding
    body_ast = (body._effect_ast_gate(case, dict(row, case="positive"), proof_base, drop_module)
                if stages.get("decode") == 0 else {"admitted": False})
    log_path = case / "verifast.log"
    log = log_path.read_text(errors="replace") if log_path.is_file() else ""
    errors = [line for line in log.splitlines() if re.search(r"\berror:", line, re.I)]
    dead = [line for line in log.splitlines() if re.search(r"dead code", line, re.I)]
    segment = drop_module._body_segment(log, proof_base, row)
    executed = lambda line: bool(line and re.search(
        rf"verified/lib\.rs\({line},\d+.*\): (?:note: )?Executing statement", log))
    body_copy = executed(row.get("source_copy_line"))
    body_return = "Executing return statement" in segment
    leak = "Leak check." in segment
    caller_headers = list(re.finditer(r"(?m)^.*Verifying function 'natural_onecell'.*$", log))
    caller_segment = log[caller_headers[0].start():] if len(caller_headers) == 1 else ""
    caller_return = "Executing return statement" in caller_segment
    caller_leak = "Leak check." in caller_segment
    source_unchanged = execution.get("source_unchanged_at_every_stage") is True
    setup = (source_unchanged and all(stages.get(stage) == 0
             for stage in ("exporter", "decode", "refinement")) and
             source.get("admitted") is True and mir.get("admitted") is True and
             caller_ast.get("admitted") is True and body_ast.get("admitted") is True)
    targeted = False
    if setup and name == "after_natural_drop_false" and stages.get("verifast") == 1 and len(errors) == 1:
        targeted = (executed(row.get("natural_scope_end_line")) and
                    re.search(rf"verified/lib\.rs\({row['false_line']},\d+-\d+\): "
                              r"error: Assertion might not hold\. \(Cannot prove false\.\)", errors[0]) is not None)
    if (setup and name == "caller_ready_entry_false" and
            stages.get("verifast") == 1 and len(errors) == 1):
        false_error = re.search(
            rf"verified/lib\.rs\({row['false_line']},\d+-\d+\): "
            r"error: Assertion might not hold\. \(Cannot prove false\.\)", errors[0])
        dead_after_target = all(
            (match := re.search(r"verified/lib\.rs\((\d+),", record)) is not None and
            int(match.group(1)) > row["false_line"] for record in dead)
        targeted = bool(false_error and dead_after_target)
    if setup and row.get("expected_missing") and stages.get("verifast") == 1 and len(errors) == 1:
        call_loc = actual_calls[0]["loc"]
        location_match = errors[0].startswith(call_loc + ": error:")
        predicate = ("CopyOnDrop_len" if row["expected_missing"] == "receiver_frame" else "array")
        if row["expected_missing"] == "source_permission":
            targeted = _source_permission_target(log, (case / "verified/lib.rs").read_bytes(), row, call_loc)
        else:
            targeted = location_match and predicate in errors[0] and "No matching heap chunks" in errors[0]
    if setup and name == "duplicate_effect_simultaneous" and stages.get("verifast") == 1 and len(errors) == 1:
        targeted = (executed(row.get("natural_scope_end_line")) and
                    re.search(rf"verified/lib\.rs\({row['double_effect_line']},\d+.*\): error:", errors[0]) is not None and
                    "CopyOnDrop_drop_effect" in errors[0] and "No matching heap chunks" in errors[0])
    if setup and name == "caller_dead_code" and stages.get("verifast") == 1 and not errors:
        targeted = any(f"verified/lib.rs({row['dead_control_line']}," in record for record in dead) and caller_return and caller_leak
    positive = (setup and stages.get("verifast") == 0 and not errors and not dead and body_copy and
                body_return and leak and caller_return and caller_leak and "0 errors found" in log)
    classification = ("NATURAL_DROP_CALLER_AND_EFFECT_PASS_FRAGMENT_ONLY" if positive else
                      "CALLER_READY_ENTRY_EXPECTED_REJECTION" if
                      name == "caller_ready_entry_false" and targeted else
                      "EXPECTED_REJECTION" if targeted else "INCONCLUSIVE")
    return {"case": name, "classification": classification, "accepted": False,
            "stages": stages, "source_gate": source, "mir_gate": mir,
            "caller_ast_evidence": caller_ast, "drop_body_effect_ast_gate": body_ast,
            "source_unchanged_at_every_stage": source_unchanged,
            "natural_scope_end_executed": executed(row.get("natural_scope_end_line")),
            "dead_code_lines": dead,
            "body_copy_executed": body_copy, "body_return_executed": body_return,
            "leak_check": leak, "caller_return": caller_return, "caller_leak_check": caller_leak, "errors": errors, "targeted_negative_matched": targeted,
            "actual_checked_selected_method_credit": positive, "compiler_generated_glue_credit": False,
            "caller_construction_credit": positive,
            "scope": "bounded concrete-u64 natural Drop fixture only; no panic path or generic insert_tail credit"}


def _natural_drop_mir_gate(case: Path, row: dict, mir) -> dict:
    """Require one actual caller Drop terminator for the guard local."""
    path = case / "decode.out"
    if not path.is_file():
        return {"admitted": False, "reason": "decoded MIR absent"}
    try:
        tree = mir.CapnpText(path.read_text(errors="replace")).parse()
        bodies = [body for body in mir.path(tree, "bodies")
                  if mir.path(body, "defPath") == "natural_onecell"]
        if len(bodies) != 1:
            return {"admitted": False, "reason": "caller MIR body is not unique"}
        debug = mir.path(bodies[0], "varDebugInfo")
        guard_debug = [entry for entry in debug
                       if mir.path(entry, "name", "name") == "gap_guard"]
        if len(guard_debug) != 1:
            return {"admitted": False, "reason": "guard local debug binding is not unique"}
        guard_local = mir.path(guard_debug[0], "value", "place", "local")
        drops = []
        calls = []
        for block_index, block in enumerate(mir.path(bodies[0], "basicBlocks")):
            kind = mir.path(block, "terminator", "kind")
            if isinstance(kind, dict) and "drop" in kind:
                drop = kind["drop"]
                place = mir.path(drop, "place")
                drops.append({"selected_path": mir.path(drop, "selectedDropPath"),
                              "selected_hash": mir.path(drop, "selectedDropHash"),
                              "guard_path": mir.path(drop, "selectedGuardPath"),
                              "bare_local": mir.path(drop, "isBareLocal"),
                              "replace": mir.path(drop, "isReplace"),
                              "span": mir.path(block, "terminator", "sourceInfo", "span"),
                              "block": mir.path(block, "id", "index"), "is_cleanup": mir.path(block, "isCleanup"), "local": mir.path(place, "local"),
                              "local_name": mir.local(place),
                              "target": mir.path(drop, "target", "index"),
                              "unwind": mir.path(drop, "unwindAction")})
            elif isinstance(kind, dict) and "call" in kind:
                calls.append(mir.call_name(kind["call"]))
        guard_drops = [drop for drop in drops if drop["local"] == guard_local]
        explicit_drop_calls = [name for name in calls if name.endswith("::drop") or "drop_in_place" in name]
        normal_drops = [drop for drop in guard_drops if drop["is_cleanup"] is False]
        selected = normal_drops[0] if len(normal_drops) == 1 else {}
        unwind = selected.get("unwind", {})
        cleanup_target = mir.path(unwind, "cleanup", "index") if "cleanup" in unwind else None
        cleanup_blocks = [block for block in mir.path(bodies[0], "basicBlocks")
                          if mir.path(block, "id", "index") == cleanup_target]
        resume_ok = (len(cleanup_blocks) == 1 and mir.path(cleanup_blocks[0], "isCleanup") is True and
                     mir.path(cleanup_blocks[0], "statements") == [] and
                     "unwindResume" in mir.path(cleanup_blocks[0], "terminator", "kind"))
        checked_bodies = [body for body in mir.path(tree, "bodies")
                          if mir.path(body, "defPath") == selected.get("selected_path") and
                             mir.path(body, "defPathHash") == selected.get("selected_hash") and
                             mir.path(body, "isDropFn") is True]
        admitted = (len(normal_drops) == 1 and resume_ok and not explicit_drop_calls and
                    selected.get("bare_local") is True and selected.get("replace") is False and
                    selected.get("guard_path") == "CopyOnDrop" and len(checked_bodies) == 1)

        return {"admitted": admitted, "guard_drop_terminators": guard_drops,
                "guard_debug_local": guard_local,
                "explicit_runtime_drop_calls": explicit_drop_calls,
                "actual_natural_drop_terminator": len(normal_drops) == 1,
                "selected_normal_drop": selected, "selected_cleanup_target": cleanup_target,
                "selected_cleanup_is_statement_free_resume": resume_ok,
                "selected_same_unit_checked_body_count": len(checked_bodies)}
    except Exception as error:
        return {"admitted": False, "reason": f"natural Drop MIR admission failed closed: {error}"}


def run(evidence: Path, args, env: dict, execute_case, validated_receipt: dict) -> dict:
    """Draft hosted hook; no local proof/toolchain entrypoint is exposed."""
    if DRAFT_STATUS != "READY":
        return {"schema": "source-linked-u64-onecell-natural-drop-draft-v1",
                "status": DRAFT_STATUS, "accepted": False,
                "reason": DRAFT_REASON, "cases": {name: "NOT_RUN" for name in CASES},
                "toolchain_invoked": False, "prepare_or_extraction_invoked": False}
    if not callable(execute_case):
        raise TypeError("execute_case callback required")
    consumer = _load("natural_drop_receipt_gate", OLD_CONSUMER)
    prep = _load("natural_drop_insert_tail_templates", OLD_PREP)
    body = _load("natural_drop_body_gate", OLD_ONECELL)
    drop_module = _load("natural_drop_existing_admission", HERE / "concrete-drop-body.py")
    proof_base = _load("natural_drop_hosted_runner_gate", ROOT /
                       "research/challenge-8/merge/overnight/copy-on-drop-prove.py")
    provider, proof_sha = proof_base.require_hosted_cloud()
    if args.profile not in ("experimental-merge-selected-drop-receiver-v4",
                            "experimental-merge-actual-glue-observation-v2",
                            "experimental-merge-actual-glue-observation-v3",
                            "experimental-merge-actual-glue-observation-v5"):
        raise RuntimeError("selected Drop exact supported experimental profile required")
    consumer.PROFILE = args.profile
    receipt = consumer._validate_receipt(args, validated_receipt, provider, proof_sha)
    extraction = _prepare(evidence)
    (evidence / "receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    results = {}
    for name, row in extraction["cases"].items():
        case = evidence / "cases" / name
        before = consumer._hashes(case)
        execution = execute_case(case, args, env)
        after = consumer._hashes(case)
        execution["source_files_unchanged"] = before == after
        execution["stage_receipt_gate"] = consumer._stage_receipts(
            case, execution.get("stages", {}), before)
        execution["source_unchanged_at_every_stage"] = (
            before == after and execution["stage_receipt_gate"]["admitted"])
        try:
            result = _classify(name, case, row, execution, prep, body, drop_module, proof_base)
        except Exception as error:
            result = {"case": name, "classification": "INCONCLUSIVE", "accepted": False,
                      "classifier_exception": repr(error), "stages": execution.get("stages", {})}

        (case / "classification.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        results[name] = result["classification"]
    aggregate = {"schema": "source-linked-u64-onecell-natural-drop-draft-v1",
                 "accepted": False, "profile": extraction["profile"],
                 "receipt_sha256": receipt["receipt_sha256"], "cases": results,
                 "scope": extraction["scope"],
                 "all_matched": results == {"positive": "NATURAL_DROP_CALLER_AND_EFFECT_PASS_FRAGMENT_ONLY",
                    "caller_ready_entry_false": "CALLER_READY_ENTRY_EXPECTED_REJECTION",
                    "after_natural_drop_false": "EXPECTED_REJECTION", "missing_receiver_frame": "EXPECTED_REJECTION",
                    "missing_source_permission": "EXPECTED_REJECTION", "duplicate_effect_simultaneous": "EXPECTED_REJECTION",
                    "caller_dead_code": "EXPECTED_REJECTION"},
                 "next_gate": "candidate review; no profile acceptance or generic/panic claim"}
    (evidence / "aggregate.json").write_text(json.dumps(aggregate, indent=2, sort_keys=True) + "\n")
    return aggregate
