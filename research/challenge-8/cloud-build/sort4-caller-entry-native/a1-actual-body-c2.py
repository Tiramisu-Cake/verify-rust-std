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
C2_UNSELECTED_SHARES = (b"        //@ share_full_borrow::<T>(cmp2_k, t, v_base);\n"
                        b"        //@ share_full_borrow::<T>(cmp2_k, t, v_base + 1);\n")
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
        //@ share_full_borrow::<T>(cmp2_k, t, v_base);
        //@ share_full_borrow::<T>(cmp2_k, t, v_base + 1);
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


# R19 c3 layer: the operands are the selected pointers `c` and `a` (symbolic
# offsets from c1/c2). All four borrows are shared so none remains at the
# leak check; only the two selected pointers get precreated references.
C3_CALL = b"        let c3 = is_less(&*c, &*a);\n"
C3_TYPED_CALL = b"        let c3 = is_less/*@::<F, (&'cmp3 T, &'cmp3 T), 'cmp3>@*/(&*c, &*a);\n"
C3_HEADER_LIFETIMES = (
    b"/*@ let_lft 'cmp = cmp_k;\n"
    b"    let_lft 'cmp2 = cmp2_k;\n"
    b"    let_lft 'cmp3 = cmp3_k; @*/"
)
C3_SCOPE_MARKER = b"        //@ __vf_callback_scope3();\n"
C3_LEFT_PRECREATE = b"        //@ let left3_ref = precreate_ref::<T>(c);\n"
C3_RIGHT_PRECREATE = b"        //@ let right3_ref = precreate_ref::<T>(a);\n"
C3_SHARES = (b"        //@ share_full_borrow::<T>(cmp3_k, t, v_base);\n"
             b"        //@ share_full_borrow::<T>(cmp3_k, t, v_base + 1);\n"
             b"        //@ share_full_borrow::<T>(cmp3_k, t, v_base + 2);\n"
             b"        //@ share_full_borrow::<T>(cmp3_k, t, v_base + 3);\n")
C3_SETUP = (b'''        //@ let cmp3_k = begin_lifetime();
        //@ __vf_callback_scope3();
        //@ split_four_owned_cells::<T>(v_base, t);
        //@ close_full_borrow_content::<T>(t, v_base);
        //@ close_full_borrow_content::<T>(t, v_base + 1);
        //@ close_full_borrow_content::<T>(t, v_base + 2);
        //@ close_full_borrow_content::<T>(t, v_base + 3);
        //@ borrow(cmp3_k, <T>.full_borrow_content(t, v_base));
        //@ borrow(cmp3_k, <T>.full_borrow_content(t, v_base + 1));
        //@ borrow(cmp3_k, <T>.full_borrow_content(t, v_base + 2));
        //@ borrow(cmp3_k, <T>.full_borrow_content(t, v_base + 3));
''' + C3_SHARES + C3_LEFT_PRECREATE + C3_RIGHT_PRECREATE + b'''        //@ init_ref_share::<T>(cmp3_k, t, left3_ref);
        //@ init_ref_share::<T>(cmp3_k, t, right3_ref);
        //@ close_ref_own::<'cmp3, T>(left3_ref);
        //@ close_ref_own::<'cmp3, T>(right3_ref);
        //@ close <(&'cmp3 T, &'cmp3 T)>.own(t, std_tuple_2_::<&'cmp3 T, &'cmp3 T> {0: left3_ref, 1: right3_ref});
        //@ open_frac_borrow(cmp3_k, ref_initialized_(left3_ref), 1/4);
        //@ open [?left3_fraction]ref_initialized_::<T>(left3_ref)();
        //@ open_frac_borrow(cmp3_k, ref_initialized_(right3_ref), 1/4);
        //@ open [?right3_fraction]ref_initialized_::<T>(right3_ref)();
''')
DEBT3_ARGS = b"t, cmp3_k, v_base, left3_ref, right3_ref, left3_fraction, right3_fraction"
MARKER3 = (b'''/*@ {
            __vf_callback_unwind_four(3);
            { close callback_four_debt::<T>(''' + DEBT3_ARGS + b'''); }
            { recover_four_sources::<T>(v_base); }
        } @*/
''')
NORMAL3 = (b"        //@ close callback_four_debt::<T>(" + DEBT3_ARGS + b");\n" +
           b"        //@ end_lft_binding::<'cmp3>();\n" +
           b"        //@ recover_four_sources::<T>(v_base);\n")
C4_CALL = b"        let c4 = is_less(&*d, &*b);\n"


def _layer_c3(verified_c2: bytes, original: bytes, c2_meta: dict, ghost, lemma_metadata):
    need(c2_meta.get("actual_c2_recovery") is True,
         "c3 requires the exact checked c2 constructor output")
    need(ghost.strip_ghost(verified_c2) == original,
         "c2 constructor source/runtime pair is immutable before c3")
    need(verified_c2.count(C3_CALL) == 1,
         "one exact c3 call with selected source operands (c, a)")
    need(verified_c2.count(C2_HEADER_LIFETIMES) == 1,
         "one c1/c2 lifetime declaration comment at the unsafe body header")
    need(verified_c2.count(MARKER) == 1 and verified_c2.count(NORMAL) == 1,
         "c2 recovery precedes c3 exactly once")
    need(verified_c2.index(NORMAL) < verified_c2.index(C3_CALL),
         "c2 recovery restores the four owners before c3")
    staged = verified_c2.replace(C2_HEADER_LIFETIMES, C3_HEADER_LIFETIMES, 1)
    call = staged.replace(C3_CALL, C3_SETUP + MARKER3 + C3_TYPED_CALL + NORMAL3, 1)
    need(call.count(C3_SCOPE_MARKER) == 1,
         "one c3 scope marker follows creation of the fresh lifetime token")
    need(call.count(b"__vf_callback_unwind_four(3);") == 1,
         "one exact indexed c3 direct-unwind marker")
    need(call.count(b"callback_four_debt::<T>(" + DEBT3_ARGS + b")") == 2,
         "normal and direct-unwind c3 paths close the same four-source debt")
    need(call.count(b"recover_four_sources::<T>(v_base);") == 4,
         "c2 and c3 each recover the current four source owners on both paths")
    need(call.count(C3_SHARES) == 1,
         "all four c3 full-borrow capabilities are converted by checked sharing")
    need(call.index(NORMAL3) < call.index(C4_CALL),
         "c3 recovery precedes the untouched c4 call")
    need(ghost.strip_ghost(call) == original,
         "c3 source annotations preserve the exact complete runtime body")
    generated_lines = call.splitlines()
    function_lines = [i for i, line in enumerate(generated_lines, 1)
                      if line.startswith(TARGET)]
    c3_lines = [i for i, line in enumerate(generated_lines, 1)
                if b"let c3 = is_less/*@" in line]
    need(len(function_lines) == len(c3_lines) == 1,
         "one actual body and one typed c3 call after construction")
    required = [row for row in lemma_metadata(call) if row["name"] in COMPARATOR_NAMES]
    need(tuple(row["name"] for row in required) == COMPARATOR_NAMES,
         "exact five required comparator dependencies in generated source")
    c3_meta = {
        **c2_meta,
        "focus_line": function_lines[0],
        "end_line": len(generated_lines),
        "required_lemmas": required,
        "body_annotation_stage": "c1-c2-c3-four-source-recovery-v1",
        "actual_indexed_calls": 3,
        "c3_call_index": 3,
        "c3_ordered_source_operands": ["c", "a"],
        "c3_marker": "__vf_callback_unwind_four(3)",
        "c3_comparator_line": c3_lines[0],
        "c3_marker_callsite_attribution": "OPEN",
        "generated_source_sha256": hashlib.sha256(call).hexdigest(),
        "runtime_body_byteequal": True,
        "summary_eligible": False,
        "proof_credit": False,
    }
    return call, original, c3_meta


def construct_c3(source: bytes, ghost, capture, pair_recovery: bytes,
                 four_recovery: bytes, c1_constructor, base_constructor,
                 lemma_metadata):
    """Build c1 and c2, then layer c3's source annotations without running tools."""
    verified_c2, original, c2_meta = construct(
        source, ghost, capture, pair_recovery, four_recovery, c1_constructor,
        base_constructor, lemma_metadata)
    return _layer_c3(verified_c2, original, c2_meta, ghost, lemma_metadata)


def _indexed_control_rows(cases, verified, original, ghost, meta, lemma_metadata, index):
    """Shared c3/c4 control metadata; every case keeps exact runtime bytes."""
    output = []
    for name, candidate, expected in cases:
        need(candidate != verified, name + " changes the annotations")
        need(ghost.strip_ghost(candidate) == original,
             name + " must preserve exact runtime bytes")
        candidate_lines = candidate.splitlines()
        focus_lines = [i for i, line in enumerate(candidate_lines, 1)
                       if line.startswith(TARGET)]
        candidate_lemmas = [row for row in lemma_metadata(candidate)
                            if row["name"] in COMPARATOR_NAMES]
        need(len(focus_lines) == 1, name + " has one exact actual body")
        need(tuple(row["name"] for row in candidate_lemmas) == COMPARATOR_NAMES,
             name + " retains exact five required comparator dependencies")
        output.append((name, candidate, original, {
            **meta,
            "name": "sort4_stable",
            "focus_line": focus_lines[0],
            "end_line": len(candidate_lines),
            "required_lemmas": candidate_lemmas,
            index + "_control": name,
            "expected_rejection": expected,
            index + "_marker_callsite_attribution": "OPEN",
            "generated_source_sha256": hashlib.sha256(candidate).hexdigest(),
            "summary_eligible": False,
            "proof_credit": False,
        }))
    return output


def _slot(n: int) -> bytes:
    return b"v_base" if n == 0 else b"v_base + %d" % n


def _indexed_resource_controls(k, verified, original, ghost, four_recovery, meta,
                               lemma_metadata, marker, typed_call, normal, left_pre,
                               right_pre, operands, drop_slots, token_slot, wrong_left,
                               next_call, expected):
    """Annotation-only negatives for indexed call k; no result is proof credit."""
    need(meta.get("actual_indexed_calls") == k, "controls require the exact constructor output")
    need(ghost.strip_ghost(verified) == original, "positive runtime source pair is byte-equal")
    need(verified.count(marker) == 1 and verified.count(typed_call) == 1 and
         verified.count(normal) == 1, "one exact marker/call/recovery before controls")
    lifetime = b"cmp%d_k" % k
    share = lambda n: b"        //@ share_full_borrow::<T>(" + lifetime + b", t, " + _slot(n) + b");\n"
    missing_shares = verified
    for n in drop_slots:
        need(missing_shares.count(share(n)) == 1, "one share line per slot")
        missing_shares = missing_shares.replace(share(n), b"", 1)
    borrow = (b"        //@ borrow(" + lifetime + b", <T>.full_borrow_content(t, " +
              _slot(token_slot) + b"));\n")
    need(verified.count(borrow) == 1 and verified.count(share(token_slot)) == 1,
         "one end-token producer")
    missing_resource = verified.replace(borrow, b"", 1).replace(share(token_slot), b"", 1)
    pre = lambda side, operand: b"        //@ let %s%d_ref = precreate_ref::<T>(%s);\n" % (side, k, operand)
    wrong_order = verified.replace(left_pre + right_pre,
                                   pre(b"left", operands[1]) + pre(b"right", operands[0]), 1)
    wrong_ref = verified.replace(left_pre, pre(b"left", wrong_left), 1)
    wrong_index = verified.replace(b"__vf_callback_unwind_four(%d);" % k,
                                   b"__vf_callback_unwind_four(%d);" % (k - 1), 1)
    missing_pred = ghost_declaration(four_recovery, b"pred callback_four_debt_without_fourth<T>")
    debt_marker = marker.replace(b"callback_four_debt::<T>(",
                                 b"callback_four_debt_without_fourth::<T>(", 1)
    missing_token = _insert_before_target(verified.replace(marker, debt_marker, 1), missing_pred)
    displaced = verified.replace(marker + typed_call, typed_call + marker, 1)
    j = k + 1
    overflow_marker = (b"/*@ {\n"
                       b"            __vf_callback_unwind_four(%d);\n" % j +
                       b"            { close callback_four_debt::<T>(t, cmp%d_k, v_base, left%d_ref, "
                       b"right%d_ref, left%d_fraction, right%d_fraction); }\n" % (j, j, j, j, j) +
                       b"            { recover_four_sources::<T>(v_base); }\n"
                       b"        } @*/\n")
    need(verified.count(next_call) == 1, "one untouched next call")
    overflow = verified.replace(next_call, overflow_marker + next_call, 1)
    names = ("missing-unselected-share", "missing-unrelated-end-token", "wrong-ordered-ref-pair",
             "wrong-ref-resource", "wrong-marker-index", "missing-fourth-debt-token",
             "displaced-marker", "index-overflow-marker")
    candidates = (missing_shares, missing_resource, wrong_order, wrong_ref, wrong_index,
                  missing_token, displaced, overflow)
    cases = tuple(("c%d-%s-negative" % (k, name), candidate, why)
                  for name, candidate, why in zip(names, candidates, expected))
    return _indexed_control_rows(cases, verified, original, ghost, meta, lemma_metadata, "c%d" % k)


C3_EXPECTED = ('base+1/base+3 full_borrow capabilities leak on the (c1,c2)=(0,0) path or a selected share is missing', 'no base0 borrow_end token for the c3 four-source debt, or no base0 share when a selects slot 0', 'ghost precreated reference order (a,c) differs from actual ordered operands (c,a)', 'left3_ref precreation points to b while the actual first operand is c', 'indexed marker names call 2 while positioned at actual c3', 'direct-unwind close supplies a predicate lacking the base+3 end token', 'direct-unwind marker is after the call instead of immediately before it', 'index-4 marker with no matching indexed call when the explicit count is 3')


def resource_controls_c3(verified: bytes, original: bytes, ghost,
                         four_recovery: bytes, meta: dict, lemma_metadata):
    """c3 negatives; base+1/+3 shares are unselected on the (c1,c2)=(0,0) path."""
    return _indexed_resource_controls(3, verified, original, ghost, four_recovery, meta,
        lemma_metadata, MARKER3, C3_TYPED_CALL, NORMAL3, C3_LEFT_PRECREATE,
        C3_RIGHT_PRECREATE, (b"c", b"a"), (1, 3), 0, b"b", C4_CALL, C3_EXPECTED)


# R19 c4 layer: c3 templates renamed for call 4 with operands `d` and `b`.
def _rename_c3_to_c4(raw: bytes) -> bytes:
    for old, new in ((b"cmp3_k", b"cmp4_k"), (b"'cmp3", b"'cmp4"),
                     (b"__vf_callback_scope3", b"__vf_callback_scope4"),
                     (b"left3_", b"left4_"), (b"right3_", b"right4_"),
                     (b"precreate_ref::<T>(c)", b"precreate_ref::<T>(d)"),
                     (b"precreate_ref::<T>(a)", b"precreate_ref::<T>(b)"),
                     (b"__vf_callback_unwind_four(3)", b"__vf_callback_unwind_four(4)")):
        raw = raw.replace(old, new)
    return raw


C4_TYPED_CALL = b"        let c4 = is_less/*@::<F, (&'cmp4 T, &'cmp4 T), 'cmp4>@*/(&*d, &*b);\n"
C4_HEADER_LIFETIMES = C3_HEADER_LIFETIMES.replace(
    b"    let_lft 'cmp3 = cmp3_k; @*/", b"    let_lft 'cmp3 = cmp3_k;\n    let_lft 'cmp4 = cmp4_k; @*/")
C4_SCOPE_MARKER = b"        //@ __vf_callback_scope4();\n"
C4_LEFT_PRECREATE = _rename_c3_to_c4(C3_LEFT_PRECREATE)
C4_RIGHT_PRECREATE = _rename_c3_to_c4(C3_RIGHT_PRECREATE)
C4_SHARES = _rename_c3_to_c4(C3_SHARES)
C4_SETUP = _rename_c3_to_c4(C3_SETUP)
DEBT4_ARGS = _rename_c3_to_c4(DEBT3_ARGS)
MARKER4 = _rename_c3_to_c4(MARKER3)
NORMAL4 = _rename_c3_to_c4(NORMAL3)
MIN_SELECT = b"        let min = hint::select_unpredictable(c3, c, a);\n"


def _layer_c4(verified_c3: bytes, original: bytes, c3_meta: dict, ghost, lemma_metadata):
    need(c3_meta.get("actual_indexed_calls") == 3,
         "c4 requires the exact checked c3 constructor output")
    need(ghost.strip_ghost(verified_c3) == original,
         "c3 constructor source/runtime pair is immutable before c4")
    need(verified_c3.count(C4_CALL) == 1 and verified_c3.count(C3_HEADER_LIFETIMES) == 1 and
         verified_c3.count(NORMAL3) == 1 and verified_c3.count(MIN_SELECT) == 1,
         "one exact c4 call after one c3 recovery and one c1..c3 header")
    need(verified_c3.index(NORMAL3) < verified_c3.index(C4_CALL) < verified_c3.index(MIN_SELECT),
         "c3 recovery precedes c4, which precedes the selectors")
    staged = verified_c3.replace(C3_HEADER_LIFETIMES, C4_HEADER_LIFETIMES, 1)
    call = staged.replace(C4_CALL, C4_SETUP + MARKER4 + C4_TYPED_CALL + NORMAL4, 1)
    need(call.count(C4_SCOPE_MARKER) == 1 and
         call.count(b"__vf_callback_unwind_four(4);") == 1 and
         call.count(b"callback_four_debt::<T>(" + DEBT4_ARGS + b")") == 2 and
         call.count(b"recover_four_sources::<T>(v_base);") == 6 and
         call.count(C4_SHARES) == 1 and call.count(b"__vf_callback_unwind_") == 4,
         "one exact c4 scope/marker/debt/recovery/share layer")
    need(call.index(NORMAL4) < call.index(MIN_SELECT), "c4 recovery precedes the selectors")
    need(ghost.strip_ghost(call) == original,
         "c4 source annotations preserve the exact complete runtime body")
    generated_lines = call.splitlines()
    function_lines = [i for i, line in enumerate(generated_lines, 1) if line.startswith(TARGET)]
    c4_lines = [i for i, line in enumerate(generated_lines, 1) if b"let c4 = is_less/*@" in line]
    need(len(function_lines) == len(c4_lines) == 1, "one actual body and one typed c4 call")
    required = [row for row in lemma_metadata(call) if row["name"] in COMPARATOR_NAMES]
    need(tuple(row["name"] for row in required) == COMPARATOR_NAMES,
         "exact five required comparator dependencies in generated source")
    return call, original, {
        **c3_meta,
        "focus_line": function_lines[0],
        "end_line": len(generated_lines),
        "required_lemmas": required,
        "body_annotation_stage": "c1-c4-four-source-recovery-v1",
        "actual_indexed_calls": 4,
        "c4_call_index": 4,
        "c4_ordered_source_operands": ["d", "b"],
        "c4_marker": "__vf_callback_unwind_four(4)",
        "c4_comparator_line": c4_lines[0],
        "c4_marker_callsite_attribution": "OPEN",
        "generated_source_sha256": hashlib.sha256(call).hexdigest(),
        "runtime_body_byteequal": True,
        "summary_eligible": False,
        "proof_credit": False,
    }


def construct_c4(source: bytes, ghost, capture, pair_recovery: bytes,
                 four_recovery: bytes, c1_constructor, base_constructor,
                 lemma_metadata):
    """Build c1..c3, then layer c4's source annotations without running tools."""
    verified_c3, original, c3_meta = construct_c3(
        source, ghost, capture, pair_recovery, four_recovery, c1_constructor,
        base_constructor, lemma_metadata)
    return _layer_c4(verified_c3, original, c3_meta, ghost, lemma_metadata)


def resource_controls_c4(verified: bytes, original: bytes, ghost,
                         four_recovery: bytes, meta: dict, lemma_metadata):
    """c4 negatives; base+0/+2 shares are unselected on the (b,d)=(1,3) path."""
    return _indexed_resource_controls(4, verified, original, ghost, four_recovery, meta,
        lemma_metadata, MARKER4, C4_TYPED_CALL, NORMAL4, C4_LEFT_PRECREATE,
        C4_RIGHT_PRECREATE, (b"d", b"b"), (0, 2), 3, b"a",
        b"        let c5 = is_less(&*unknown_right, &*unknown_left);\n",
        ("resource: share", "resource: end token", "resource: ordered pair",
         "resource: ref token", "frontend: marker inventory", "frontend: marker inventory",
         "frontend: marker binding", "frontend: marker inventory"))


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
    need(verified.count(C2_UNSELECTED_SHARES) == 1,
         "one checked conversion for both unselected full-borrow capabilities")
    missing_shares = verified.replace(C2_UNSELECTED_SHARES, b"", 1)
    missing_resource = verified.replace(unrelated_borrow, b"", 1).replace(
        b"        //@ share_full_borrow::<T>(cmp2_k, t, v_base);\n", b"", 1)
    wrong_order = verified.replace(C2_LEFT_PRECREATE + C2_RIGHT_PRECREATE,
        b"        //@ let left2_ref = precreate_ref::<T>(v_base + 2);\n"
        b"        //@ let right2_ref = precreate_ref::<T>(v_base + 3);\n", 1)


    cases = (
        ("c2-missing-unselected-share-negative", missing_shares,
         "unused full_borrow capabilities for base0/1 remain at the leak check"),
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
