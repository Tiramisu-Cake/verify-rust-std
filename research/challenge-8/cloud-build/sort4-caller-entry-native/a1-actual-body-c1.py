"""Source-only first-call recovery annotations for the complete actual body.

Inert on import. The authorized Cloud constructor supplies exact original body
bytes and checked recovery/join declarations.
"""
import hashlib

MARKER = b'''/*@ {
            __vf_callback_unwind_pair();
            { close comparison_debt::<T>(t, cmp_k, left, right, left_ref, right_ref, left_fraction, right_fraction); }
            { recover_pair::<T>(left, right); }
        } @*/
'''
NORMAL = b'''        //@ close comparison_debt::<T>(t, cmp_k, left, right, left_ref, right_ref, left_fraction, right_fraction);
        //@ end_lft_binding::<'cmp>();
        //@ recover_pair::<T>(left, right);
'''
EXTRA_BORROWS = b'''        //@ close_full_borrow_content::<T>(t, v_base + 2);
        //@ close_full_borrow_content::<T>(t, v_base + 3);
        //@ borrow(cmp_k, <T>.full_borrow_content(t, v_base + 2));
        //@ borrow(cmp_k, <T>.full_borrow_content(t, v_base + 3));
        //@ share_full_borrow::<T>(cmp_k, t, v_base + 2);
        //@ share_full_borrow::<T>(cmp_k, t, v_base + 3);
'''

RECOVER_PAIR = b'''/*@
lem recover_pair<T>(left: *T, right: *T)
    nonghost_callers_only
    req thread_token(?t) &*& type_interp::<T>() &*&
        left == right + 1 &*&
        comparison_debt::<T>(
            t, ?k, left, right, ?left_ref, ?right_ref,
            ?left_fraction, ?right_fraction) &*&
        [1/2]lifetime_token(k);
    ens thread_token(t) &*& type_interp::<T>() &*&
        right[..4] |-> ?current &*& foreach(current, own::<T>(t));
{
    open comparison_debt::<T>(
        t, k, left, right, left_ref, right_ref, left_fraction, right_fraction);
    close [left_fraction]ref_initialized_::<T>(left_ref)();
    close_frac_borrow(left_fraction, ref_initialized_::<T>(left_ref));
    close [right_fraction]ref_initialized_::<T>(right_ref)();
    close_frac_borrow(right_fraction, ref_initialized_::<T>(right_ref));
    merge_fractions lifetime_token(k);
    end_lifetime(k);
    borrow_end(k, <T>.full_borrow_content(t, left));
    open_full_borrow_content::<T>(t, left);
    borrow_end(k, <T>.full_borrow_content(t, right));
    open_full_borrow_content::<T>(t, right);
    borrow_end(k, <T>.full_borrow_content(t, right + 2));
    open_full_borrow_content::<T>(t, right + 2);
    borrow_end(k, <T>.full_borrow_content(t, right + 3));
    open_full_borrow_content::<T>(t, right + 3);
    join_four_owned_cells::<T>(right, t);
}
@*/
'''


def need(ok, reason):
    if not ok:
        raise RuntimeError('R15-C1-CONSTRUCTOR: ' + reason)


def ghost_declaration(source, prefix):
    name = source.find(prefix)
    need(name >= 0, 'missing checked declaration ' + prefix.decode())
    start = source.rfind(b'/*@', 0, name)
    end = source.find(b'@*/', name)
    need(start >= 0 and end >= 0, 'malformed checked declaration ' + prefix.decode())
    return source[start:end + len(b'@*/')] + b'\n'


def extend_comparison_debt(declaration):
    old = b'    borrow_end_token(k, <T>.full_borrow_content(t, right));'
    new = b'''    borrow_end_token(k, <T>.full_borrow_content(t, right)) &*&
    borrow_end_token(k, <T>.full_borrow_content(t, right + 2)) &*&
    borrow_end_token(k, <T>.full_borrow_content(t, right + 3));'''
    need(declaration.count(old) == 1, 'one exact pair debt tail')
    result = declaration.replace(old, new, 1)
    need(result.count(b'borrow_end_token(') == 4,
         'comparison debt must carry one end token for every source cell')
    return result


def annotate(base, recovery):
    """Pure annotation edit; caller gates actual construction to Cloud."""
    signature = b'pub unsafe fn sort4_stable<'
    need(base.count(signature) == 1, 'one complete actual target')
    prefix, body = base.split(signature, 1)
    # Keep the remaining comparator expressions byte-for-byte source-written.
    for name in (b'c2', b'c3', b'c4', b'c5'):
        body = body.replace(b'let ' + name + b" = is_less/*@::<F, (&'cmp T, &'cmp T), 'cmp>@*/(",
                            b'let ' + name + b' = is_less(')
    aliases = b'        //@ let left = v_base + 1;\n        //@ let right = v_base;\n'
    split = b'        //@ split_four_owned_cells::<T>(v_base, t);\n'
    need(body.count(split) == 1, 'checked split before actual c1')
    # Recovery is a sibling of the strict lifetime scope on both normal and
    # unwind paths, so aliases must dominate that scope at function root.
    bounds = b'        //@ interior_pointer_limits::<T>(v_base, 4, 1);\n'
    need(body.count(bounds) == 1, 'one checked source interior bounds step')
    body = body.replace(bounds, b'', 1)
    outer = b'    //@ let cmp_k = begin_lifetime();\n'
    need(body.count(outer) == 1, 'one outer lifetime creation anchor')
    outer_aliases = (b'    //@ interior_pointer_limits::<T>(v_base, 4, 1);\n' +
                     aliases.replace(b'        //@', b'    //@'))
    body = body.replace(outer, outer_aliases + outer, 1)
    share_anchor = b'        //@ share_full_borrow::<T>(cmp_k, t, v_base);\n'
    need(body.count(share_anchor) == 1, 'pair borrow/share setup before c1')
    body = body.replace(share_anchor, share_anchor + EXTRA_BORROWS, 1)
    first = b"        let c1 = is_less/*@::<F, (&'cmp T, &'cmp T), 'cmp>@*/(&*v_base.add(1), &*v_base);\n"
    need(body.count(first) == 1, 'unique original c1 expression/typed annotation')
    body = body.replace(first, MARKER + first + NORMAL, 1)

    debt = extend_comparison_debt(ghost_declaration(recovery, b'pred comparison_debt<T>'))
    join = ghost_declaration(recovery, b'lem join_four_owned_cells<T>')
    need(b'lem recover_pair<T>' in recovery,
         'source recovery fixture must retain the original independently checked pair lemma')
    declarations = debt + join + RECOVER_PAIR
    need(declarations.count(b'lem recover_pair<T>') == 1 and
         declarations.count(b'lem join_four_owned_cells<T>') == 1,
         'one generated all-four recovery and join definition')
    # The original two-cell recover_pair declaration in the dependency fixture
    # is deliberately excluded; only the generated all-four wrapper is emitted.
    return prefix + declarations + signature + body


def resource_controls(verified, ghost, meta, lemma_metadata):
    """Pure source-only negative controls for the two c1 recovery obligations."""
    target = b'pub unsafe fn sort4_stable<'
    need(verified.count(target) == 1, 'one target for resource controls')
    stripped = ghost.strip_ghost(verified)
    required = meta.get('required_lemmas')
    need(isinstance(required, list) and [row.get('name') for row in required] == [
        'interior_pointer_limits', 'split_four_owned_cells',
        'join_four_owned_cells', 'recover_pair'],
        'controls retain the exact four checked prerequisites')

    debt = ghost_declaration(verified, b'pred comparison_debt<T>')
    debt = debt.replace(b'pred comparison_debt<T>',
                        b'pred comparison_debt_without_fourth<T>', 1)
    full_tail = (b'    borrow_end_token(k, <T>.full_borrow_content(t, right + 2)) &*&\n'
                 b'    borrow_end_token(k, <T>.full_borrow_content(t, right + 3));')
    need(debt.count(full_tail) == 1, 'all-four debt tail for missing-token control')
    debt = debt.replace(
        full_tail,
        b'    borrow_end_token(k, <T>.full_borrow_content(t, right + 2));', 1)

    missing_fourth = b'''/*@
lem missing_fourth_end_token_negative<T>(left: *T, right: *T)
    nonghost_callers_only
    req thread_token(?t) &*& type_interp::<T>() &*& left == right + 1 &*&
        comparison_debt_without_fourth::<T>(
            t, ?k, left, right, ?left_ref, ?right_ref,
            ?left_fraction, ?right_fraction) &*&
        [1/2]lifetime_token(k);
    ens thread_token(t) &*& type_interp::<T>();
{
    open comparison_debt_without_fourth::<T>(
        t, k, left, right, left_ref, right_ref, left_fraction, right_fraction);
    close comparison_debt::<T>(
        t, k, left, right, left_ref, right_ref, left_fraction, right_fraction);
    recover_pair::<T>(left, right);
}
@*/
'''
    false_old_value = b'''/*@
lem false_old_value_array_post_negative<T>(
    left: *T, right: *T, old_values: list<T>)
    nonghost_callers_only
    req thread_token(?t) &*& type_interp::<T>() &*& left == right + 1 &*&
        comparison_debt::<T>(
            t, ?k, left, right, ?left_ref, ?right_ref,
            ?left_fraction, ?right_fraction) &*&
        [1/2]lifetime_token(k);
    ens thread_token(t) &*& type_interp::<T>() &*&
        right[..4] |-> old_values &*& foreach(old_values, own::<T>(t));
{
    recover_pair::<T>(left, right);
}
@*/
'''
    insertion = verified.index(target)
    cases = []
    for name, block, expected in (
        ('missing-fourth-end-token-negative', debt + missing_fourth,
         'comparison_debt close lacks right+3 borrow_end_token'),
        ('false-old-value-array-post-negative', false_old_value,
         'postcondition requires arbitrary old_values rather than recovered current values'),
    ):
        source = verified[:insertion] + block + verified[insertion:]
        need(ghost.strip_ghost(source) == stripped,
             'resource control must preserve exact actual runtime bytes')
        starts = [row for row in lemma_metadata(source)
                  if row['name'] in ('missing_fourth_end_token_negative',
                                     'false_old_value_array_post_negative')]
        wanted = ('missing_fourth_end_token_negative'
                  if name.startswith('missing-fourth')
                  else 'false_old_value_array_post_negative')
        selected = [row for row in starts if row['name'] == wanted]
        need(len(selected) == 1, 'one exact negative lemma interval: ' + wanted)
        row = selected[0]
        first = [i for i, line in enumerate(source.splitlines(), 1)
                 if b'let c1 = is_less/*@' in line]
        need(len(first) == 1, 'one actual c1 coordinate after control insertion')
        negative_meta = {**meta, **row, 'mir_target': 'sort4_stable',
                         'focus_line': row['focus_line'],
                         'end_line': row['end_line'],
                         'first_comparator_line': first[0],
                         'generated_source_sha256': hashlib.sha256(source).hexdigest(),
                         'required_lemmas': required,
                         'expected_rejection': expected,
                         'control_scope': ('generic arbitrary old_values list postcondition; '
                             'not evidence about concrete Cell mutation'
                             if name.startswith('false-old-value') else
                             'one missing right+3 borrow_end_token, rejected when closing full debt'),
                         'summary_eligible': False, 'proof_credit': False}
        cases.append((name, source, ghost.strip_ghost(source), negative_meta))
    return cases


def construct(source, ghost, capture, recovery, base_constructor, lemma_metadata):
    base, original, meta = base_constructor(source, ghost, capture)
    generated = annotate(base, recovery)
    need(ghost.strip_ghost(generated) == original,
         'full runtime unchanged after c1 borrow/recovery annotations')
    lines = generated.splitlines()
    lo = next(i for i, line in enumerate(lines, 1)
              if line.startswith(b'pub unsafe fn sort4_stable<'))
    first = [i for i, line in enumerate(lines, 1)
             if b'let c1 = is_less/*@' in line]
    need(len(first) == 1, 'one original first callback coordinate')
    required = lemma_metadata(generated)
    meta = {**meta, 'focus_line': lo, 'end_line': len(lines),
        'required_lemmas': required,
        'body_annotation_stage': 'c1-all-four-borrow-and-unwind-recovery-v2',
        'actual_c1_recovery': True, 'borrowed_source_cells': 4,
        'first_comparator_line': first[0],
        'generated_source_sha256': hashlib.sha256(generated).hexdigest(),
        'summary_eligible': False, 'proof_credit': False}
    need([x['name'] for x in required] == [
        'interior_pointer_limits', 'split_four_owned_cells',
        'join_four_owned_cells', 'recover_pair'],
        'exact checked dependency sequence')
    return generated, original, meta
