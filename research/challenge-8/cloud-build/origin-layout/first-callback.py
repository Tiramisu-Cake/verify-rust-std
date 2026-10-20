#!/usr/bin/env python3
"""Cloud-only first actual comparator campaign. Import has no side effects.

The prefix is mechanically cut immediately before tail.read, and never stands
in for the complete actual insert_tail. Full-body final posts stay unchanged.
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
PROFILE = 'experimental-merge-guard-addressability-v1'
R5_PROFILE = 'experimental-merge-guard-addressability-emitter-r5-v1'
R7_PROFILE = 'experimental-merge-late-callback-recovery-r7-v1'
R8_PROFILE = 'experimental-merge-owned-array-allocation-r8-v1'
R9_PROFILE = 'experimental-merge-guard-current-return-r9-v1'
R9_GUARD_RETURN_RECOVERY_ENV = 'SMALLSORT_R9_GUARD_RETURN_RECOVERY'
SUPPORTED_PROFILES = (PROFILE, R5_PROFILE, R7_PROFILE, R8_PROFILE, R9_PROFILE)
R9_GUARD_TRACE_ENV = 'SMALLSORT_R9_GUARD_TRACE'
PREFIX_NAME = b'insert_tail_first_callback_prefix'
CUT = b'        // SAFETY: after this read'

# Pure entry facts, before the callback lifetime; no resources or value equality.
SINGLETON_FACTS = b"""    //@ length_drop(1, xs);
    //@ length_take(1, drop(1, xs));
    //@ length_drop(1, drop(1, xs));
    //@ note(length(take(1, drop(1, xs))) == 1);
    //@ note(length(drop(1, drop(1, xs))) == 1);
    //@ drop_length(drop(1, drop(1, xs)));
"""

# Exact inherited suffix and owner-authorized CURRENT replacement; ghost only.
ENTRY_OWNER_REJOIN = b"""        //@ close own::<u64>(t)(head(take(1, drop(1, xs))));
        //@ close own::<u64>(t)(head(drop(1, drop(1, xs))));
        //@ close foreach(take(1, drop(1, xs)), own::<u64>(t));
        //@ close foreach(drop(1, drop(1, xs)), own::<u64>(t));
        //@ close array::<u64>(sift, 1, take(1, drop(1, xs)));
        //@ close array::<u64>(tail, 1, drop(1, drop(1, xs)));
        //@ array_join::<u64>(begin + 1);
        //@ array_join::<u64>(begin);
        //@ foreach_join(drop(1, xs), own::<u64>(t), 1);
        //@ foreach_join(xs, own::<u64>(t), 1);
"""
CURRENT_OWNER_REJOIN = b"""        //@ close own::<u64>(t)(current_sift);
        //@ close own::<u64>(t)(current_tail);
        //@ close foreach(cons(current_sift, nil), own::<u64>(t));
        //@ close foreach(cons(current_tail, nil), own::<u64>(t));
        //@ close array::<u64>(sift, 1, cons(current_sift, nil));
        //@ close array::<u64>(tail, 1, cons(current_tail, nil));
        //@ array_join::<u64>(begin + 1);
        //@ array_join::<u64>(begin);
        //@ foreach_append(cons(current_sift, nil), cons(current_tail, nil));
        //@ foreach_append(take(1, xs), append(cons(current_sift, nil), cons(current_tail, nil)));
"""


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'missing pinned module: {path}')
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _one(data, old, new, label):
    if data.count(old) != 1:
        raise ValueError(f'{label}: expected one exact anchor')
    return data.replace(old, new, 1)


def _add_singleton_facts(source):
    anchor = b"    //@ let cmp_k = begin_lifetime();\n"
    return _one(source, anchor, SINGLETON_FACTS + anchor,
                'pure singleton length facts before callback lifetime')


# Fullbody only: expose the physically owned CURRENT tail from the rejoined array.
TAIL_READ_OPEN = b"""        //@ assert array::<u64>(begin, 3, ?read_current);
        //@ array_split::<u64>(begin, 2);
        //@ open array::<u64>(tail, 1, drop(2, read_current));
"""


def _open_tail_read(source):
    anchor = b'        let tmp = ManuallyDrop::new(tail.read());\n'
    return _one(source, anchor, TAIL_READ_OPEN + anchor,
                'open CURRENT tail singleton before original read')


# Checked primitives: precreation provides no points-to ownership; initialization
# consumes a fraction of the actual tmp cell. Its readonly-end obligation remains
# live and must be discharged by the unchanged full normal/unwind contracts.
TMP_REFERENCE_INIT = b"""        //@ let r4_tmp_ref = precreate_ref::<u64>(&tmp);
        //@ init_ref_readonly::<u64>(r4_tmp_ref, 1/2);
"""


# Empty-tail folding follows the existing array definition and checks geometry.
# This retains the actual physical fraction/value and returns no nonempty owner.
GUARD_EMPTY_TAIL_HELPER = b"""/*@
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


def _prepare_guard_empty_tail(source):
    anchor = b'        let mut gap_guard = CopyOnDrop { src: &*tmp, dst: tail, len: 1 };\n'
    return _one(source, anchor, anchor +
                b'        //@ r7_guard_empty_tail(gap_guard.src as *mut u64);\n'
                b'        //@ initialized_storage_alignment(gap_guard.src as *mut u64);\n'
                b'        //@ points_to_limits::<u64>(gap_guard.src as *mut u64);\n'
                b'        //@ assert gap_guard.src as usize != 0;\n'
                b'        //@ assert gap_guard.src as usize % std::mem::align_of::<u64>() == 0;\n'
                b'        //@ assert object_pointer_within_limits(gap_guard.src, std::mem::size_of::<u64>()) == true;\n'
                b'        //@ assert gap_guard.src as usize <= usize::MAX - std::mem::size_of::<u64>();\n',
                'checked empty array tail at original guard reference provenance')


def _prepare_tmp_reference(source):
    anchor = b'        let mut gap_guard = CopyOnDrop { src: &*tmp, dst: tail, len: 1 };\n'
    return _one(source, anchor, TMP_REFERENCE_INIT + anchor,
                'checked reference initialization before original guard')


# Initial iteration only. Later loop/resource restoration remains a proof
# obligation of the unchanged complete actual body and full final contracts.
FIRST_SHIFT_PREP = b"""        //@ note(sift == begin + 1);
        //@ array_split::<u64>(begin, 1);
        //@ assert array::<u64>(sift, 1, ?r4_shift_current);
        //@ open array::<u64>(sift, 1, r4_shift_current);
        //@ initialized_storage_alignment(sift);
        //@ points_to_limits::<u64>(sift);
        //@ uninitialized_storage_alignment(gap_guard.dst);
        //@ points_to__limits::<u64>(gap_guard.dst);
        //@ assert sift as usize != 0;
        //@ assert gap_guard.dst as usize != 0;
        //@ assert sift as usize % std::mem::align_of::<u64>() == 0;
        //@ assert gap_guard.dst as usize % std::mem::align_of::<u64>() == 0;
        //@ assert object_pointer_within_limits(sift, std::mem::size_of::<u64>()) == true;
        //@ assert object_pointer_within_limits(gap_guard.dst, std::mem::size_of::<u64>()) == true;
        //@ assert sift as usize <= usize::MAX - std::mem::size_of::<u64>();
        //@ assert gap_guard.dst as usize <= usize::MAX - std::mem::size_of::<u64>();
        //@ assert sift as usize + std::mem::size_of::<u64>() <= gap_guard.dst as usize;
"""


def _prepare_first_shift(source):
    anchor = b'        loop {\n'
    return _one(source, anchor, FIRST_SHIFT_PREP +
                b'        //@ let r5_late_k = begin_lifetime();\n' + anchor +
                b"            /*@ let_lft 'late = r5_late_k; @*/\n",
                'CURRENT first shift and block-start late lifetime binding')


# Concrete primitive representation missing from the pinned abstract .share.
# It is an explicit specification definition using the existing physical borrow;
# the body-checked bridge cannot establish share without that exact premise.
U64_SHARE_REPRESENTATION = b"""/*@
pred r6_u64_share(k: lifetime_t, t: thread_id_t, p: *u64) =
    frac_borrow(k, u64_full_borrow_content(t, p));
type_pred_def <u64>.share = r6_u64_share;

lem r6_close_u64_share(k: lifetime_t, t: thread_id_t, p: *u64)
    req [_]frac_borrow(k, u64_full_borrow_content(t, p));
    ens [_](<u64>.share)(k, t, p);
{
    assert [?r6_share_fraction]frac_borrow(k, u64_full_borrow_content(t, p));
    close [r6_share_fraction]r6_u64_share(k, t, p);
    leak [r6_share_fraction]r6_u64_share(k, t, p);
}

lem r6_u64_share_mono(k: lifetime_t, k1: lifetime_t, t: thread_id_t, p: *u64)
    req [_](<u64>.share)(k, t, p) &*& lifetime_inclusion(k1, k) == true;
    ens [_](<u64>.share)(k1, t, p);
{
    open [_]r6_u64_share(k, t, p);
    frac_borrow_mono(k, k1, u64_full_borrow_content(t, p));
    assert [?r6_mono_fraction]frac_borrow(k1, u64_full_borrow_content(t, p));
    close [r6_mono_fraction]r6_u64_share(k1, t, p);
    leak [r6_mono_fraction]r6_u64_share(k1, t, p);
}
@*/
"""


def _add_u64_share_representation(source):
    anchor = b'use core::{mem::ManuallyDrop, ptr};\n'
    return _one(source, anchor, anchor + U64_SHARE_REPRESENTATION,
                'checked concrete u64 canonical share representation')


LATE_REFERENCE_PREP = b"""            //@ let r4_cmp_tmp_ref = precreate_ref::<u64>(&tmp);
            //@ init_ref_readonly::<u64>(r4_cmp_tmp_ref, 1/2);
            //@ assert array::<u64>(sift, 1, ?r4_cmp_current);
            //@ open array::<u64>(sift, 1, r4_cmp_current);
            //@ let r4_cmp_sift_ref = precreate_ref::<u64>(sift);
            //@ init_ref_readonly::<u64>(r4_cmp_sift_ref, 1/2);
            //@ assert [?r5_tmp_share](*r4_cmp_tmp_ref |-> ?r5_tmp_value);
            //@ close [r5_tmp_share]u64_full_borrow_content(t, r4_cmp_tmp_ref)();
            //@ close scaledp(r5_tmp_share, u64_full_borrow_content(t, r4_cmp_tmp_ref))();
            //@ borrow(r5_late_k, scaledp(r5_tmp_share, u64_full_borrow_content(t, r4_cmp_tmp_ref)));
            //@ full_borrow_into_frac(r5_late_k, scaledp(r5_tmp_share, u64_full_borrow_content(t, r4_cmp_tmp_ref)));
            //@ frac_borrow_implies_scaled(r5_late_k, r5_tmp_share, u64_full_borrow_content(t, r4_cmp_tmp_ref));
            //@ assert [?r5_sift_share](*r4_cmp_sift_ref |-> ?r5_sift_value);
            //@ close [r5_sift_share]u64_full_borrow_content(t, r4_cmp_sift_ref)();
            //@ close scaledp(r5_sift_share, u64_full_borrow_content(t, r4_cmp_sift_ref))();
            //@ borrow(r5_late_k, scaledp(r5_sift_share, u64_full_borrow_content(t, r4_cmp_sift_ref)));
            //@ full_borrow_into_frac(r5_late_k, scaledp(r5_sift_share, u64_full_borrow_content(t, r4_cmp_sift_ref)));
            //@ frac_borrow_implies_scaled(r5_late_k, r5_sift_share, u64_full_borrow_content(t, r4_cmp_sift_ref));
            //@ r6_close_u64_share(r5_late_k, t, r4_cmp_tmp_ref);
            //@ close_ref_own::<'late, u64>(r4_cmp_tmp_ref);
            //@ r6_close_u64_share(r5_late_k, t, r4_cmp_sift_ref);
            //@ close_ref_own::<'late, u64>(r4_cmp_sift_ref);
            //@ close <(&'late u64, &'late u64)>.own(t, std_tuple_2_::<&'late u64, &'late u64> { 0: r4_cmp_tmp_ref, 1: r4_cmp_sift_ref });
"""
LATE_CALL = b"            if !is_less/*@::<F, (&'late u64, &'late u64), 'late>@*/(&tmp, &*sift) {\n"


def _prepare_late_references(source):
    anchor = b'            if !is_less(&tmp, &*sift) {\n'
    return _one(source, anchor, LATE_REFERENCE_PREP + LATE_CALL,
                'checked fractional share and Args ownership before late comparator')


# R7 explicit type-level scope starts after physical setup, so references,
# semantic lifetime and exact coefficients remain in the outer environment.
LATE_CLOSE = b"""            //@ merge_fractions lifetime_token(r5_late_k);
            //@ assert [1/2]lifetime_token(r5_late_k);
"""
LATE_RECOVER = b"""            //@ assert lifetime_token(r5_late_k);
            //@ end_lifetime(r5_late_k);
            //@ borrow_end(r5_late_k, scaledp(r5_tmp_share, u64_full_borrow_content(t, r4_cmp_tmp_ref)));
            //@ open scaledp(r5_tmp_share, u64_full_borrow_content(t, r4_cmp_tmp_ref))();
            //@ open [r5_tmp_share]u64_full_borrow_content(t, r4_cmp_tmp_ref)();
            //@ end_ref_readonly::<u64>(r4_cmp_tmp_ref);
            //@ borrow_end(r5_late_k, scaledp(r5_sift_share, u64_full_borrow_content(t, r4_cmp_sift_ref)));
            //@ open scaledp(r5_sift_share, u64_full_borrow_content(t, r4_cmp_sift_ref))();
            //@ open [r5_sift_share]u64_full_borrow_content(t, r4_cmp_sift_ref)();
            //@ end_ref_readonly::<u64>(r4_cmp_sift_ref);
            //@ merge_fractions points_to::<u64>(sift, _);
            //@ assert *sift |-> ?r7_sift_current;
            //@ close array::<u64>(sift, 1, cons(r7_sift_current, nil));
"""


# The enclosing source branch retires the original guard before this suffix.
# Recover only existing heap resources: the original readonly token selects its
# actual reference, and the returned Drop effect must match that same pointer.
# This is checked ghost code; no pointer, fraction or current value is assumed.
GUARD_POST_DROP_RECOVERY = b"""    //@ assert ref_readonly_end_token::<u64>(?r8_guard_ref, ?r8_tmp_origin, ?r8_tmp_share);
    //@ open CopyOnDrop_drop_effect(t, r8_guard_ref, ?r8_drop_dst, 1);
    //@ open [1/4]array::<u64>(r8_guard_ref, 1, ?r8_drop_current);
    //@ open [1/4]array::<u64>(r8_guard_ref + 1, 0, nil);
    //@ end_ref_readonly::<u64>(r8_guard_ref);
    //@ merge_fractions points_to::<u64>(r8_tmp_origin, _);
"""

R9_GUARD_RETURN_MARKER = b"""    /*@ {
        guard_current_return_recover();
        assert ref_readonly_end_token::<u64>(?r9_guard_ref, ?r9_tmp_origin, ?r9_tmp_share);
        open [1/4]array::<u64>(r9_guard_ref, 1, ?r9_drop_current);
        open [1/4]array::<u64>(r9_guard_ref + 1, 0, nil);
        end_ref_readonly::<u64>(r9_guard_ref);
        merge_fractions points_to::<u64>(r9_tmp_origin, _);
        assert [1/2](*r9_tmp_origin |-> ?r9_tmp_current);
    } @*/
"""


def _prepare_post_drop_recovery(source, old):
    # Bind the closing sequence to the unique following actual caller, rather
    # than matching identical nested braces in earlier checked helper bodies.
    anchor = b'        }\n    }\n}\n\n' + old.WRAPPER_SIGNATURE
    return _one(source, anchor, b'        }\n    }\n' +
                GUARD_POST_DROP_RECOVERY + b'}\n\n' + old.WRAPPER_SIGNATURE,
                'checked original guard debt after branch Drop before function free')


def _prepare_r9_guard_return_recovery(source, old):
    # This marker is parsed and moved by the R9-only checked MIR hook. It
    # remains ghost-only in Rust and is anchored to the one wrapper body.
    anchor = b'        }\n    }\n}\n\n' + old.WRAPPER_SIGNATURE
    return _one(source, anchor,
                b'        }\n    }\n' + R9_GUARD_RETURN_MARKER + b'}\n\n' +
                old.WRAPPER_SIGNATURE,
                'R9 checked guard-return recovery marker')


def _prepare_late_scope(source):
    source = _one(source, b'        //@ let r5_late_k = begin_lifetime();\n',
                  b'', 'move semantic lifetime begin to reached late preparation')
    anchor = b'            //@ let r4_cmp_tmp_ref = precreate_ref::<u64>(&tmp);\n'
    source = _one(source, anchor,
                  b'            //@ let r5_late_k = begin_lifetime();\n'
                  b'            //@ let r7_late_unwind = false;\n' + anchor,
                  'fresh semantic lifetime and outcome flag outside late type binding')
    anchor = b'            //@ r6_close_u64_share(r5_late_k, t, r4_cmp_tmp_ref);\n'
    source = _one(source, anchor,
                  b"            //@ late_callback_scope_begin::<'late>();\n" + anchor,
                  'late type scope starts after physical variables are captured')
    markers = (b"            /*@ { late_callback_close::<'late>(); " +
               _commands(LATE_CLOSE) + b" } @*/\n" +
               b"            //@ late_callback_scope_end::<'late>();\n" +
               b"            /*@ { late_callback_recover::<'late>(); " +
               _commands(LATE_RECOVER) + b" } @*/\n")
    return _one(source, LATE_CALL, LATE_CALL + markers,
                'actual late normal and Cleanup resource scope markers')


def _commands(fragment):
    lines = fragment.splitlines()
    if any(not line.lstrip().startswith(b'//@ ') for line in lines):
        raise ValueError('recovery must contain only explicit ghost commands')
    return b' '.join(line.lstrip()[4:] for line in lines)


def _markers(old, mutation=None):
    split = b"        //@ end_lft_binding::<'cmp>();\n"
    if old.B2_COMPARE_RECOVER.count(split) != 1:
        raise ValueError('callback lifetime split changed')
    close, recover = old.B2_COMPARE_RECOVER.split(split)
    recover = _one(recover, ENTRY_OWNER_REJOIN, CURRENT_OWNER_REJOIN,
                   'CURRENT owner and physical-cell rejoin')
    for pointer, value in (('tail', 'current_tail'), ('sift', 'current_sift')):
        opened = f'        //@ open_full_borrow_content::<u64>(t, {pointer});\n'.encode()
        bound = f'        //@ assert *{pointer} |-> ?{value};\n'.encode()
        recover = _one(recover, opened, opened + bound,
                       f'bind returned CURRENT {pointer} value')
    if mutation == 'lost_reference_fraction':
        close = _one(close, b'close_frac_borrow(tail_ref_frac,',
                     b'close_frac_borrow(tail_ref_frac + 1,', 'bad reference fraction')
    if mutation == 'lost_reference_token':
        close = _one(close, b'assert [1/2]lifetime_token(cmp_k);',
                     b'assert lifetime_token(cmp_k);', 'insufficient lifetime token')
    return (b"            /*@ { first_callback_close::<'cmp>(); " +
            _commands(close) + b" } @*/\n" +
            b"            //@ first_callback_scope_end::<'cmp>();\n" +
            b"            /*@ { first_callback_recover::<'cmp>(); " +
            _commands(recover) + b' } @*/\n')


def _cut_prefix(source):
    """Exact partial source relation: keep before CUT, close unsafe/function.

    Preserve all helper/Drop code preceding insert_tail and the actual local
    wrapper after it. No original source is extracted or run on the VPS.
    """
    wrapper = b'pub unsafe fn b2_three_from_local'
    if source.count(CUT) != 1 or source.count(wrapper) != 1:
        raise ValueError('prefix cut or wrapper boundary is not unique')
    cut = source.index(CUT)
    wrapper_at = source.index(wrapper, cut)
    # Wrapper contract precedes its signature and must remain attached to it.
    suffix = source[wrapper_at:]
    wrapper_contract = source.rfind(b'/*@\nreq thread_token', cut, wrapper_at)
    if wrapper_contract >= 0:
        suffix = source[wrapper_contract:]
    result = source[:cut] + b'    }\n}\n\n' + suffix
    result = _one(result, b'unsafe fn insert_tail<',
                  b'unsafe fn ' + PREFIX_NAME + b'<', 'prefix function name')
    result = _one(result, b'insert_tail(begin, begin.add(2), is_less);',
                  PREFIX_NAME + b'(begin, begin.add(2), is_less);', 'prefix wrapper')
    if b'tail.read()' in result or b'if !is_less(&tmp' in result:
        raise ValueError('prefix includes forbidden post-cut runtime')
    return result


def prepare(evidence, *, prefix=False, mutation=None, profile=PROFILE):
    old = _load('first_callback_original_preparation', HERE / 'actual-insert-tail-b2.py')
    record = old._prepare(evidence)  # Cloud-only inherited actual-source binding.
    case = evidence / 'cases' / old.CASE
    original = (case / 'original/lib.rs').read_bytes()
    verified = (case / 'verified/lib.rs').read_bytes()
    full_original = original
    verified = _add_u64_share_representation(verified)
    verified = _one(verified, U64_SHARE_REPRESENTATION,
                    U64_SHARE_REPRESENTATION + GUARD_EMPTY_TAIL_HELPER,
                    'checked guard empty-tail helper')
    verified = _add_singleton_facts(verified)
    verified = _one(verified,
                    old.B2_COMPARE_RECOVER.replace(b'        ', b'            '),
                    b'', 'remove old false recovery')
    verified = _one(verified, old.B2_COMPARE_RECOVER, b'',
                    'remove old true recovery')
    call = (b"        if !is_less/*@::<F, (&'cmp u64, &'cmp u64), 'cmp>@*/"
            b'(&*tail, &*sift) {\n')
    markers = _markers(old, mutation)
    verified = _one(verified, call, call + markers, 'first actual comparator markers')
    negative = b''
    if mutation == 'lost_current_f':
        negative = b'            //@ leak <F>.own(t, _);\n'
    elif mutation == 'lost_cell_owner':
        negative = (b'            //@ array_split::<u64>(begin, 1);\n'
                    b'            //@ leak array::<u64>(begin, 1, _);\n'
                    b'            //@ array_join::<u64>(begin); // TARGET: missing physical cell owner\n')
    if negative:
        verified = _one(verified, markers, markers + negative,
                        'explicit negative-only resource loss on false path')
    if mutation not in (None, 'lost_reference_fraction', 'lost_reference_token',
                         'lost_current_f', 'lost_cell_owner'):
        raise ValueError('unknown first-comparator mutation')
    if not prefix:
        verified = _prepare_late_references(_prepare_first_shift(_prepare_guard_empty_tail(
            _prepare_tmp_reference(_open_tail_read(verified)))))
        if profile in (R7_PROFILE, R8_PROFILE, R9_PROFILE):
            verified = _prepare_late_scope(verified)
        if profile in (R8_PROFILE, R9_PROFILE):
            if profile == R8_PROFILE:
                verified = _prepare_post_drop_recovery(verified, old)
            else:
                verified = _prepare_r9_guard_return_recovery(verified, old)
    # Strip the NEW ghost-only annotations and compare with inherited source.
    # Other original ghost commands were already checked by old._prepare.
    # Runtime comparison removes only comments and whitespace; the inherited
    # preparation already established exact actual-source extraction identities.
    def runtime(data):
        return re.sub(rb'/\*.*?\*/|//[^\n]*', b'', data, flags=re.S)
    if runtime(verified) != runtime(original):
        # Removing whole annotation lines leaves whitespace-only source lines.
        clean = lambda data: b'\n'.join(x.strip() for x in runtime(data).splitlines() if x.strip())
        if clean(verified) != clean(original):
            raise ValueError('new recovery changed runtime tokens')
    if prefix:
        original, verified = _cut_prefix(original), _cut_prefix(verified)
    if mutation is None and (b'//@ leak' in verified or b'//@ assume' in verified):
        raise ValueError('positive cannot discard or assume resources')
    if old.INSERT_CONTRACT not in verified:
        raise ValueError('full CURRENT normal/unwind final posts changed')
    (case / 'original/lib.rs').write_bytes(original)
    (case / 'verified/lib.rs').write_bytes(verified)
    record.update(schema='first-actual-callback-source-v1', profile=profile,
                  original_sha256=_sha(original), verified_sha256=_sha(verified),
                  full_specialized_original_sha256=_sha(full_original),
                  prefix=prefix, mutation=mutation,
                  cut='immediately before tail.read/ManuallyDrop/guard; true path returns at cut' if prefix else None,
                  source_relation='exact pre-cut runtime segment plus closing braces and renamed function/wrapper' if prefix else 'complete actual body; ghost-only annotation replacement',
                  final_posts_sha256=_sha(old.INSERT_CONTRACT),
                  callback_marker_sha256=_sha(markers),
                  late_callback_scope_recovery_requested=(profile in (R7_PROFILE, R8_PROFILE, R9_PROFILE) and not prefix),
                  guard_return_recovery_marker_sha256=(
                      _sha(R9_GUARD_RETURN_MARKER) if profile == R9_PROFILE and not prefix else None),
                  guard_return_recovery_requested=(profile == R9_PROFILE and not prefix),
                  first_callback_unwind_recovery_qualified=False,
                  first_callback_unwind_status='NOT_RUN', proof_credit=False)
    record['actual_first_call_line'] = old._line(verified, call.rstrip(b'\n'))
    for key, anchor in (
        ('actual_read_line', b'let tmp = ManuallyDrop::new(tail.read());'),
        ('actual_guard_line', b'let mut gap_guard = CopyOnDrop { src: &*tmp, dst: tail, len: 1 };'),
        ('actual_shift_line', b'ptr::copy_nonoverlapping(sift, gap_guard.dst, 1);'),
        ('actual_update_line', b'gap_guard.dst = sift;'),
        ('actual_late_call_line', LATE_CALL.strip())):
        record[key] = None if prefix else old._line(verified, anchor)
    record['false_return_line'] = old._line(verified, b'            return;')
    if prefix:
        record['true_cut_line'] = verified[:verified.index(b'    }\n}\n\n', verified.index(call))].count(b'\n') + 1
    else:
        record['true_frontier_line'] = old._line(verified, b'let tmp = ManuallyDrop::new(tail.read());')
    (evidence / 'preparation.json').write_text(json.dumps(record, indent=2, sort_keys=True)+'\n')
    return case, record


def _execute_case_with_r9_trace(execute_case, case, args, env, *, profile,
                                prefix=False, actual_callback_case=False):
    """Enable R9-only native guard diagnostics and checked recovery."""
    case_env = dict(env)
    case_env.pop(R9_GUARD_TRACE_ENV, None)
    case_env.pop(R9_GUARD_RETURN_RECOVERY_ENV, None)
    if profile == R9_PROFILE and not prefix and actual_callback_case:
        case_env[R9_GUARD_TRACE_ENV] = '1'
        case_env[R9_GUARD_RETURN_RECOVERY_ENV] = '1'
    return execute_case(case, args, case_env)


def classify(case, record, execution, *, baseline_positive=False):
    stages = execution.get('stages', {})
    text = (case / 'verifast.log').read_text(errors='replace') if (case / 'verifast.log').is_file() else ''
    refinement = ''.join((case / name).read_text(errors='replace')
                         for name in ('refinement.log', 'refinement.out') if (case / name).is_file())
    errors = [line for line in text.splitlines() if re.search(r'\berror:', line, re.I)]
    exact = (_sha((case/'original/lib.rs').read_bytes()) == record['original_sha256'] and
             _sha((case/'verified/lib.rs').read_bytes()) == record['verified_sha256'] and
             execution.get('source_unchanged_at_every_stage') is True and
             execution.get('stage_receipt_gate', {}).get('admitted') is True)
    # These are necessary admission observations, never sufficient by themselves.
    hrtb = bool(re.search(r'MERGE_HRTB_CALL registered=1 .*T=u64 .*', text))
    local = 'MERGE_FIRST_CALLBACK_LOCAL_CONTINUE' in text
    official = ('QUALIFIED_FIRST_FNMUT_CONTINUE_EDGE:' in refinement and stages.get('refinement') == 0)
    first_error = errors[0] if errors else None
    admitted = exact and hrtb and local and official and stages.get('exporter') == 0 and stages.get('decode') == 0
    mutation = record['mutation']
    negative_match = False
    if mutation:
        intended = {
            'lost_reference_fraction': ('ref_initialized', 'close_frac_borrow_token', 'Cannot prove condition'),
            'lost_reference_token': ('lifetime_token',),
            'lost_current_f': ('own',),
            'lost_cell_owner': ('array',),
        }[mutation]
        source = (case/'verified/lib.rs').read_bytes()
        if mutation in ('lost_reference_fraction', 'lost_reference_token'):
            anchor = b'first_callback_close::<'
            expected_line = source[:source.index(anchor)].count(b'\n')+1
        elif mutation == 'lost_current_f':
            contract_at = source.index(b'unsafe fn ' + PREFIX_NAME)
            normal_post_at = source.index(b'    *is_less |-> ?normal_f &*& <F>.own(t, normal_f);', contract_at)
            expected_line = source[:normal_post_at].count(b'\n')+1
        else:
            anchor = b'            //@ array_join::<u64>(begin); // TARGET: missing physical cell owner'
            expected_line = source[:source.index(anchor)].count(b'\n')+1
        target_executed = bool(re.search(
            rf'verified/lib\.rs\({expected_line},\d+[^\n]*Executing statement', text))
        error_at_target = bool(first_error and f'({expected_line},' in first_error)
        # An executed target alone does not locate a later proof error. Only
        # direct source errors, or the exact close/join specification with the
        # target as the LAST executed statement before that error, qualify.
        before_error = text.split(first_error, 1)[0] if first_error else ''
        executions = re.findall(r'verified/lib\.rs\((\d+),\d+[^\n]*Executing statement', before_error)
        last_at_target = bool(executions and int(executions[-1]) == expected_line)
        canonical_spec_error = bool(first_error and (
            mutation == 'lost_reference_fraction' and
            re.search(r'lifetime_logic\.rsspec\(282,', first_error) or
            mutation == 'lost_cell_owner' and
            re.search(r'prelude_core\.rsspec\(293,', first_error)))
        negative_match = bool(baseline_positive and admitted and
                              stages.get('verifast') not in (0,125,None) and first_error and
                              (error_at_target or (canonical_spec_error and last_at_target)) and
                              any(word in first_error for word in intended))
    prefix_proved = bool(admitted and record['prefix'] and mutation is None and
                         stages.get('verifast') == 0 and not errors and 'dead code' not in text.lower())
    runtime_frontiers = {}
    for key in ('actual_first_call_line', 'actual_read_line', 'actual_guard_line', 'actual_shift_line',
                'actual_update_line', 'actual_late_call_line', 'false_return_line'):
        line = record.get(key)
        runtime_frontiers[key] = bool(line and re.search(
            rf'verified/lib\.rs\({line},\d+[^\n]*(?:Executing statement|Executing return statement)', text))
    result = dict(schema='first-callback-result-v1', accepted=False,
                  classification='PREFIX_CURRENT_NORMAL_UNWIND_PROVED' if prefix_proved else
                  'INTENDED_RESOURCE_NEGATIVE' if negative_match else 'INCONCLUSIVE',
                  prefix=record['prefix'], cut=record['cut'], mutation=mutation,
                  stages=stages, source_exact=exact, runtime_frontiers=runtime_frontiers,
                  hrtb_registration_observed=hrtb, local_first_continue_observed=local,
                  official_first_continue_qualified=official,
                  current_false_true_panic_proved=prefix_proved,
                  intended_negative=negative_match,
                  full_insert_tail_proved=False, b2_achieved=False,
                  first_error=first_error, proof_credit=prefix_proved,
                  next_frontier='full body diagnostic required' if prefix_proved else first_error,
                  limitations='Prefix is partial. Registration/reached-call/refiner exit0 alone give no resource credit.')
    (case/'classification.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    return result


def run(evidence, args, env, execute_case, validated_receipt):
    if not callable(execute_case):
        raise TypeError('hosted execute_case required')
    campaign_env = dict(env)
    campaign_env.pop(R9_GUARD_TRACE_ENV, None)
    campaign_env.pop(R9_GUARD_RETURN_RECOVERY_ENV, None)
    selected_profile = getattr(args, 'profile', None)
    profile_path = os.environ.get('SMALLSORT_MERGE_PROFILE')
    if (selected_profile not in SUPPORTED_PROFILES or not profile_path or
            json.loads(Path(profile_path).read_text()).get('profile') != selected_profile):
        raise RuntimeError('first callback requires the exact supported experimental profile')
    proof = _load('first_callback_hosted_proof', HERE.parents[1] / 'merge/overnight/copy-on-drop-prove.py')
    proof.require_hosted_cloud()
    consumer = _load('first_callback_receipt', HERE/'concrete-consumer.py')
    provider, proof_sha = proof.require_hosted_cloud()
    consumer._validate_receipt(args, validated_receipt, provider, proof_sha)
    evidence.mkdir(parents=True, exist_ok=False)
    def dispatch(case, case_args, case_env=None, *, prefix=False, actual_callback_case=False):
        return _execute_case_with_r9_trace(
            execute_case, case, case_args, campaign_env if case_env is None else case_env,
            profile=selected_profile,
            prefix=prefix, actual_callback_case=actual_callback_case)
    share_controls = _load('r6_share_controls', HERE/'r6-share-controls.py')
    results = {'share_representation_controls': share_controls.run(
        evidence/'share-representation-controls', args, campaign_env,
        lambda case, case_args, case_env: dispatch(case, case_args, case_env),
        representation=U64_SHARE_REPRESENTATION)}
    array_controls = _load('r7_array_controls', HERE/'r7-array-controls.py')
    results['guard_array_controls'] = array_controls.run(
        evidence/'guard-array-controls', args, campaign_env,
        lambda case, case_args, case_env: dispatch(case, case_args, case_env),
        helper=GUARD_EMPTY_TAIL_HELPER)
    # Full-body case runs regardless of prefix failure, retaining the next real
    # resource frontier under unmodified final posts.
    cases = [('prefix', True, None), ('full_body', False, None)] + [
        (name, True, name) for name in ('lost_reference_fraction', 'lost_reference_token',
                                      'lost_current_f', 'lost_cell_owner')]
    previous_flag = getattr(args, 'first_fnmut_continue', False)
    previous_r8_flag = getattr(args, 'r8_owned_array_allocation', False)
    args.first_fnmut_continue = True
    args.r8_owned_array_allocation = False
    try:
        for name, prefix, mutation in cases:
            if mutation and not results['prefix']['current_false_true_panic_proved']:
                results[name] = dict(classification='NOT_RUN_PREFIX_PREREQUISITE_FAILED',
                                     intended_negative=False, proof_credit=False)
                continue
            case, record = prepare(evidence/name, prefix=prefix, mutation=mutation, profile=selected_profile)
            before = consumer._hashes(case)
            args.r8_owned_array_allocation = (selected_profile in (R8_PROFILE, R9_PROFILE) and not prefix)
            try:
                execution = dispatch(case, args, prefix=prefix,
                                     actual_callback_case=(name == 'full_body'))
            finally:
                args.r8_owned_array_allocation = False
            execution['stage_receipt_gate'] = consumer._stage_receipts(case, execution.get('stages', {}), before)
            execution['source_unchanged_at_every_stage'] = (before == consumer._hashes(case) and
                execution['stage_receipt_gate'].get('admitted') is True)
            results[name] = classify(case, record, execution,
                                     baseline_positive=results.get('prefix', {}).get('current_false_true_panic_proved', False))
        if selected_profile == R7_PROFILE:
            geometry_controls = _load('r8_geometry_controls', HERE/'r8-geometry-controls.py')
            results['allocation_geometry_controls'] = geometry_controls.run(
                evidence/'allocation-geometry-controls', args, campaign_env,
                lambda case, case_args, case_env: dispatch(case, case_args, case_env))
        if selected_profile in (R7_PROFILE, R8_PROFILE, R9_PROFILE):
            late_controls = _load('r7_late_admission', HERE/'r7-late-admission-controls.py')
            results['late_scope_admission_controls'] = late_controls.run(
                evidence/'late-scope-admission-controls', args, campaign_env,
                lambda case, case_args, case_env: dispatch(
                    case, case_args, case_env,
                    actual_callback_case=(selected_profile == R9_PROFILE)),
                evidence/'full_body/cases/actual_three_current_full_posts',
                json.loads((evidence/'full_body/preparation.json').read_text()))
        if selected_profile in (R8_PROFILE, R9_PROFILE):
            freshness = _load('r8_freshness_controls', HERE/'r8-freshness-controls.py')
            results['owned_array_allocation_freshness_controls'] = freshness.run(
                evidence/'owned-array-allocation-freshness-controls', args, campaign_env,
                lambda case, case_args, case_env: dispatch(case, case_args, case_env))
        if selected_profile == R9_PROFILE:
            guard_controls = _load('r9_guard_return_controls', HERE/'r9-guard-return-controls.py')
            args.r8_owned_array_allocation = True
            try:
                results['guard_return_recovery_controls'] = guard_controls.run(
                    evidence/'guard-return-recovery-controls', args, campaign_env,
                    lambda case, case_args, case_env: dispatch(
                        case, case_args, case_env, actual_callback_case=True),
                    evidence/'full_body/cases/actual_three_current_full_posts',
                    json.loads((evidence/'full_body/preparation.json').read_text()))
            finally:
                args.r8_owned_array_allocation = False
        if results['prefix']['current_false_true_panic_proved']:
            controls = _load('first_callback_admission', HERE/'first-callback-admission-controls.py')
            results['admission_controls'] = controls.run(
                evidence/'admission-controls', args, campaign_env,
                lambda case, case_args, case_env: dispatch(case, case_args, case_env),
                evidence/'prefix/cases/actual_three_current_full_posts',
                {**json.loads((evidence/'prefix/preparation.json').read_text()),
                 'full_body_case': str(evidence/'full_body/cases/actual_three_current_full_posts'),
                 'full_body_source_record': json.loads((evidence/'full_body/preparation.json').read_text())})
        else:
            results['admission_controls'] = dict(all_matched=False,
                classification='NOT_RUN_PREFIX_PREREQUISITE_FAILED', proof_credit=False)
    finally:
        args.first_fnmut_continue = previous_flag
        args.r8_owned_array_allocation = previous_r8_flag
    aggregate = dict(schema='first-callback-campaign-v1', profile=selected_profile, accepted=False,
                     results=results, b2_achieved=False,
                     prefix_current_normal_unwind_proved=results['prefix']['current_false_true_panic_proved'],
                     all_target_controls_matched=(
                         results['prefix']['current_false_true_panic_proved'] and
                         all(results[name].get('intended_negative') is True for name in
                             ('lost_reference_fraction', 'lost_reference_token', 'lost_current_f', 'lost_cell_owner')) and
                         results['admission_controls'].get('all_matched') is True),
                     classification='DIAGNOSTIC_ONLY_UNTIL_ALL_GATES_MATCH')
    (evidence/'aggregate.json').write_text(json.dumps(aggregate, indent=2, sort_keys=True)+'\n')
    return aggregate
