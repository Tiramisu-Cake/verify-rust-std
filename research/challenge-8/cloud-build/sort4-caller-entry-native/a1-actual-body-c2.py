"""Source-only c2 annotations layered on the existing c1 constructor output.

Import is inert. The caller supplies the already pinned c1 constructor,
pair-recovery source, four-source recovery source, and base constructor. This
module never runs a compiler, exporter, MIR consumer, or verifier.
"""
from __future__ import annotations

import hashlib


TARGET = b"pub unsafe fn sort4_stable<"
C2_CALL = b"        let c2 = is_less(&*v_base.add(3), &*v_base.add(2));\n"
C2_TYPED_CALL = b"        let c2 = is_less/*@::<F, (&'cmp2 T, &'cmp2 T), 'cmp2>@*/(&*v_base.add(3), &*v_base.add(2));\n"
C2_LEFT_PRECREATE = b"        //@ let left2_ref = precreate_ref::<T>(v_base + 3);\n"
C2_RIGHT_PRECREATE = b"        //@ let right2_ref = precreate_ref::<T>(v_base + 2);\n"
C1_HEADER_LIFETIME = b"/*@ let_lft 'cmp = cmp_k; @*/"
C2_HEADER_LIFETIMES = (
    b"/*@ let_lft 'cmp = cmp_k;\n"
    b"    let_lft 'cmp2 = cmp2_k; @*/"
)
C2_SCOPE_MARKER = b"        //@ __vf_callback_scope2();\n"
COMPARATOR_NAMES = ("interior_pointer_limits", "split_four_owned_cells",
                    "join_four_owned_cells", "recover_pair",
                    "recover_four_sources")

C2_SETUP = b'''        //@ let cmp2_k = begin_lifetime();
        //@ __vf_callback_scope2();
        //@ interior_pointer_limits::<T>(v_base, 4, 3);
        //@ interior_pointer_limits::<T>(v_base, 4, 2);
        //@ split_four_owned_cells::<T>(v_base, t);
        //@ close_full_borrow_content::<T>(t, v_base);
        //@ close_full_borrow_content::<T>(t, v_base + 1);
        //@ close_full_borrow_content::<T>(t, v_base + 2);
        //@ close_full_borrow_content::<T>(t, v_base + 3);
        //@ borrow(cmp2_k, <T>.full_borrow_content(t, v_base));
        //@ borrow(cmp2_k, <T>.full_borrow_content(t, v_base + 1));
        //@ borrow(cmp2_k, <T>.full_borrow_content(t, v_base + 2));
        //@ borrow(cmp2_k, <T>.full_borrow_content(t, v_base + 3));
        //@ share_full_borrow::<T>(cmp2_k, t, v_base + 3);
        //@ share_full_borrow::<T>(cmp2_k, t, v_base + 2);
        //@ let left2_ref = precreate_ref::<T>(v_base + 3);
        //@ let right2_ref = precreate_ref::<T>(v_base + 2);
        //@ init_ref_share::<T>(cmp2_k, t, left2_ref);
        //@ init_ref_share::<T>(cmp2_k, t, right2_ref);
        //@ close_ref_own::<'cmp2, T>(left2_ref);
        //@ close_ref_own::<'cmp2, T>(right2_ref);
        //@ close <(&'cmp2 T, &'cmp2 T)>.own(t, std_tuple_2_::<&'cmp2 T, &'cmp2 T> {0: left2_ref, 1: right2_ref});
        //@ open_frac_borrow(cmp2_k, ref_initialized_(left2_ref), 1/4);
        //@ open [?left2_fraction]ref_initialized_::<T>(left2_ref)();
        //@ open_frac_borrow(cmp2_k, ref_initialized_(right2_ref), 1/4);
        //@ open [?right2_fraction]ref_initialized_::<T>(right2_ref)();
'''

DEBT_ARGS = b"t, cmp2_k, v_base, left2_ref, right2_ref, left2_fraction, right2_fraction"
MARKER = (b'''/*@ {
            __vf_callback_unwind_four(2);
            { close callback_four_debt::<T>(''' + DEBT_ARGS + b'''); }
            { recover_four_sources::<T>(v_base); }
        } @*/
''')
NORMAL = (b"        //@ close callback_four_debt::<T>(" + DEBT_ARGS + b");\n" +
          b"        //@ end_lft_binding::<'cmp2>();\n" +
          b"        //@ recover_four_sources::<T>(v_base);\n")


def need(ok: bool, reason: str) -> None:
    if not ok:
        raise RuntimeError("R17-C2-CONSTRUCTOR: " + reason)


def ghost_declaration(source: bytes, prefix: bytes) -> bytes:
    name = source.find(prefix)
    need(name >= 0, "missing checked declaration " + prefix.decode())
    start = source.rfind(b"/*@", 0, name)
    end = source.find(b"@*/", name)
    need(start >= 0 and end >= 0, "malformed checked declaration " + prefix.decode())
    return source[start:end + len(b"@*/")] + b"\n"


def _insert_before_target(source: bytes, declaration: bytes) -> bytes:
    need(source.count(TARGET) == 1, "one complete actual target")
    return source.replace(TARGET, declaration + TARGET, 1)


def _layer_c2(verified_c1: bytes, original: bytes, c1_meta: dict,
              ghost, four_recovery: bytes, lemma_metadata):
    need(verified_c1.count(C2_CALL) == 1,
         "one exact c2 call with source operand order (3,2)")
    need(c1_meta.get("actual_c1_recovery") is True,
         "c1 constructor result must retain checked c1 recovery")
    need(ghost.strip_ghost(verified_c1) == original,
         "c1 constructor source/runtime pair is immutable before c2")
    need(verified_c1.count(C1_HEADER_LIFETIME) == 1,
         "one parser-admitted c1 lifetime declaration at the unsafe body header")

    callback_debt = ghost_declaration(four_recovery, b"pred callback_four_debt<T>")
    recover_four = ghost_declaration(four_recovery, b"lem recover_four_sources<T>")
    need(four_recovery.count(b"lem join_four_owned_cells<T>") == 1,
         "pinned four-source dependency has one checked join declaration")
    need(verified_c1.count(b"lem join_four_owned_cells<T>") == 1,
         "reuse exactly one c1-provided join_four_owned_cells declaration")
    need(verified_c1.count(b"pred callback_four_debt<T>") == 0 and
         verified_c1.count(b"lem recover_four_sources<T>") == 0,
         "c1 input has no duplicate c2 recovery declarations")

    staged = verified_c1.replace(C1_HEADER_LIFETIME, C2_HEADER_LIFETIMES, 1)
    target_at = staged.index(TARGET)
    declarations = callback_debt + recover_four
    staged = staged[:target_at] + declarations + staged[target_at:]
    need(staged.count(C2_HEADER_LIFETIMES) == 1,
         "both lifetime declarations stay in one unsafe-header comment")
    need(staged.count(C2_CALL) == 1, "c2 call retained after helper insertion")
    call = staged.replace(C2_CALL, C2_TYPED_CALL, 1)
    need(call.count(C2_TYPED_CALL) == 1, "c2 receives its fresh cmp2 lifetime annotation")
    call = call.replace(C2_TYPED_CALL, C2_SETUP + MARKER + C2_TYPED_CALL + NORMAL, 1)
    need(call.count(C2_SCOPE_MARKER) == 1,
         "one c2 scope marker follows creation of the fresh lifetime token")
    need(call.count(b"__vf_callback_unwind_four(2);") == 1,
         "one exact indexed c2 direct-unwind marker")
    need(call.count(b"callback_four_debt::<T>(" + DEBT_ARGS + b")") == 2,
         "normal and direct-unwind paths close the same four-source debt")
    need(call.count(b"recover_four_sources::<T>(v_base);") == 2,
         "normal and direct-unwind paths recover the current four source owners")
    need(ghost.strip_ghost(call) == original,
         "c2 source annotations preserve the exact complete runtime body")

    all_lemmas = lemma_metadata(call)
    recover_rows = [row for row in all_lemmas if row["name"] == "recover_four_sources"]
    join_rows = [row for row in all_lemmas if row["name"] == "join_four_owned_cells"]
    need(len(recover_rows) == len(join_rows) == 1,
         "one generic four-source recovery and one reused join declaration")
    previous = c1_meta.get("required_lemmas")
    need(isinstance(previous, list), "c1 constructor supplies exact checked prerequisites")
    required_names = [row.get("name") for row in previous]
    need(required_names.count("join_four_owned_cells") == 1,
         "c1 prerequisite list carries one existing four-cell join")
    need("recover_four_sources" not in required_names,
         "c2 recovery is newly added once")

    generated_lines = call.splitlines()
    function_lines = [i for i, line in enumerate(generated_lines, 1)
                      if line.startswith(TARGET)]
    c2_lines = [i for i, line in enumerate(generated_lines, 1)
                if b"let c2 = is_less/*@" in line]
    need(len(function_lines) == len(c2_lines) == 1,
         "one actual body and one typed c2 call after construction")
    first_c1_lines = [i for i, line in enumerate(generated_lines, 1)
                      if b"let c1 = is_less/*@" in line]
    need(len(first_c1_lines) == 1,
         "one original c1 comparator coordinate after helper insertion")
    required = [row for row in all_lemmas
                if row["name"] in COMPARATOR_NAMES]
    need(tuple(row["name"] for row in required) == COMPARATOR_NAMES,
         "exact five required comparator dependencies in generated source")
    c2_meta = {
        **c1_meta,
        "focus_line": function_lines[0],
        "end_line": len(generated_lines),
        "required_lemmas": required,
        "body_annotation_stage": "c1-then-c2-four-source-recovery-v1",
        "actual_c2_recovery": True,
        "c2_call_index": 2,
        "c2_ordered_source_slots": [3, 2],
        "c2_marker": "__vf_callback_unwind_four(2)",
        "first_comparator_line": first_c1_lines[0],
        "c2_comparator_line": c2_lines[0],
        "c2_marker_callsite_attribution": "OPEN",
        "generated_source_sha256": hashlib.sha256(call).hexdigest(),
        "runtime_body_byteequal": True,
        "summary_eligible": False,
        "proof_credit": False,
    }
    return call, original, c2_meta


def construct(source: bytes, ghost, capture, pair_recovery: bytes,
              four_recovery: bytes, c1_constructor, base_constructor,
              lemma_metadata):
    """Build c1 first, then layer c2's source annotations without running tools."""
    need(hasattr(c1_constructor, "construct"),
         "caller must supply the separately pinned c1 constructor module")
    verified_c1, original, c1_meta = c1_constructor.construct(
        source, ghost, capture, pair_recovery, base_constructor, lemma_metadata)
    return _layer_c2(verified_c1, original, c1_meta, ghost,
                     four_recovery, lemma_metadata)


def resource_controls(verified: bytes, original: bytes, ghost,
                      four_recovery: bytes, meta: dict, lemma_metadata):
    """Return annotation-only c2 negative controls; no result is proof credit."""
    need(meta.get("actual_c2_recovery") is True,
         "resource controls require the exact c2 constructor output")
    need(ghost.strip_ghost(verified) == original,
         "positive c2 runtime source pair is byte-equal")
    need(verified.count(MARKER) == 1 and verified.count(C2_TYPED_CALL) == 1,
         "one exact c2 marker/call before making controls")

    wrong_ref = verified.replace(C2_LEFT_PRECREATE,
        b"        //@ let left2_ref = precreate_ref::<T>(v_base + 2);\n", 1)
    wrong_index = verified.replace(b"__vf_callback_unwind_four(2);",
                                   b"__vf_callback_unwind_four(1);", 1)
    missing_pred = ghost_declaration(
        four_recovery, b"pred callback_four_debt_without_fourth<T>")
    debt_marker = MARKER.replace(b"callback_four_debt::<T>(",
                                 b"callback_four_debt_without_fourth::<T>(", 1)
    missing_token = verified.replace(MARKER, debt_marker, 1)
    missing_token = _insert_before_target(missing_token, missing_pred)
    displaced = verified.replace(MARKER + C2_TYPED_CALL,
                                 C2_TYPED_CALL + MARKER, 1)
    unrelated_borrow = b"        //@ borrow(cmp2_k, <T>.full_borrow_content(t, v_base));\n"
    need(verified.count(unrelated_borrow) == 1, "one unrelated base0 end-token producer")
    missing_resource = verified.replace(unrelated_borrow, b"", 1)
    wrong_order = verified.replace(C2_LEFT_PRECREATE + C2_RIGHT_PRECREATE,
        b"        //@ let left2_ref = precreate_ref::<T>(v_base + 2);\n"
        b"        //@ let right2_ref = precreate_ref::<T>(v_base + 3);\n", 1)


    cases = (
        ("c2-missing-unrelated-end-token-negative", missing_resource,
         "no base0 borrow_end token exists to close normal or direct-unwind four-source debt"),
        ("c2-wrong-ordered-ref-pair-negative", wrong_order,
         "ghost precreated reference order (2,3) differs from actual ordered source operands (3,2)"),
        ("c2-wrong-ref-resource-negative", wrong_ref,
         "left2_ref precreation points to slot 2 while the actual first operand is slot 3"),
        ("c2-wrong-marker-index-negative", wrong_index,
         "indexed marker names call 1 while positioned at actual c2"),
        ("c2-missing-fourth-debt-token-negative", missing_token,
         "direct-unwind close supplies a predicate lacking the base+3 end token"),
        ("c2-displaced-marker-negative", displaced,
         "direct-unwind marker is after the call instead of immediately before it"),
    )
    output = []
    for name, candidate, expected in cases:
        need(ghost.strip_ghost(candidate) == original,
             name + " must preserve exact runtime bytes")
        candidate_lines = candidate.splitlines()
        focus_lines = [i for i, line in enumerate(candidate_lines, 1)
                       if line.startswith(TARGET)]
        first_c1_lines = [i for i, line in enumerate(candidate_lines, 1)
                          if b"let c1 = is_less/*@" in line]
        c2_lines = [i for i, line in enumerate(candidate_lines, 1)
                    if b"let c2 = is_less/*@" in line]
        candidate_lemmas = [row for row in lemma_metadata(candidate)
                            if row["name"] in COMPARATOR_NAMES]
        need(len(focus_lines) == len(first_c1_lines) == len(c2_lines) == 1,
             name + " has exact actual body and comparator coordinates")
        need(tuple(row["name"] for row in candidate_lemmas) == COMPARATOR_NAMES,
             name + " retains exact five required comparator dependencies")
        output.append((name, candidate, original, {
            **meta,
            "name": "sort4_stable",
            "focus_line": focus_lines[0],
            "end_line": len(candidate_lines),
            "first_comparator_line": first_c1_lines[0],
            "c2_comparator_line": c2_lines[0],
            "required_lemmas": candidate_lemmas,
            "c2_control": name,
            "expected_rejection": expected,
            "c2_marker_callsite_attribution": "OPEN",
            "generated_source_sha256": hashlib.sha256(candidate).hexdigest(),
            "summary_eligible": False,
            "proof_credit": False,
        }))
    return output
