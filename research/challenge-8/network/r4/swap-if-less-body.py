#!/usr/bin/env python3
"""R4 candidate: annotated actual `swap_if_less` crate text (no proof tools).

Inert on import. `construct` takes the exact std file bytes and the Select
layer files (pinned by blob/SHA below), inserts ghost text only, and checks
that stripping ghost text restores the exact original function bytes.
Status: PREPARED / UNVERIFIED. See DESIGN.md for the dependency gates.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

SOURCE_SHA256 = '85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1'
STD_SPAN = (380, 412)  # 1-based inclusive lines of `unsafe fn swap_if_less` at blob 40939f92
# Select layer consumed verbatim (origin/research/night-select-sort4-cloud-2026-10-09):
SELECT_RECOVER_PAIR_BLOB = 'a29ad2542a4eb4c70686786c3426ab742672e761'  # a1-actual-recover-pair.rs
SELECT_CAPTURE_BLOB = 'a7775d9393222a123e23034102f11e24f7b4e99b'       # overnight-sort4/capture.py (strip_ghost)

GHOST_BLOCK = re.compile(rb"/\*@.*?@\*/(?:\r?\n)?", re.S)   # = capture.py:39
GHOST_LINE = re.compile(rb"(?m)^[ \t]*//@[^\r\n]*(?:\r?\n|$)")  # = capture.py:40

COUNTS = {
    b'is_less(': 1, b'hint::select_unpredictable(': 2, b'ptr::read(': 1,
    b'ManuallyDrop::new(': 1, b'ptr::copy(': 1, b'ptr::copy_nonoverlapping(': 1,
    b'.add(': 2,
}

PREFIX = (b'#![allow(internal_features)]\n'
          b'use std::{hint, ptr, mem::ManuallyDrop};\n\n')

# Distinct logical positions (all 25/45 sort9/sort13 call sites). Equal
# positions are OPEN (DESIGN.md D3). No ordering, Copy, Freeze or purity premise.
CONTRACT = b'''/*@
req thread_token(?t) &*& t == currentThread &*& type_interp::<T>() &*& type_interp::<F>() &*&
    a_pos != b_pos &*&
    *(v_base + a_pos) |-> ?a_before &*& <T>.own(t, a_before) &*&
    *(v_base + b_pos) |-> ?b_before &*& <T>.own(t, b_before) &*&
    *is_less |-> ?less_before &*& <F>.own(t, less_before);
@*/
/*@
ens thread_token(t) &*& type_interp::<T>() &*& type_interp::<F>() &*&
    *(v_base + a_pos) |-> ?a_after &*& <T>.own(t, a_after) &*&
    *(v_base + b_pos) |-> ?b_after &*& <T>.own(t, b_after) &*&
    *is_less |-> ?less_after &*& <F>.own(t, less_after);
@*/
/*@
on_unwind_ens thread_token(t) &*& type_interp::<T>() &*& type_interp::<F>() &*&
    *(v_base + a_pos) |-> ?a_after &*& <T>.own(t, a_after) &*&
    *(v_base + b_pos) |-> ?b_after &*& <T>.own(t, b_after) &*&
    *is_less |-> ?less_after &*& <F>.own(t, less_after);
@*/
'''

UNSAFE_ANCHOR = b'    unsafe {\n'
LIFETIME_SCOPE = (b'    //@ let cmp_k = begin_lifetime();\n'
                  b'    unsafe {\n'
                  b"/*@ let_lft 'cmp = cmp_k; @*/\n")

ADD_A = b'        let v_a = v_base.add(a_pos);\n'
ADD_LIMITS = (b'        //@ points_to_limits(v_base + a_pos);\n'
              b'        //@ points_to_limits(v_base + b_pos);\n')

CALL = b'        let should_swap = is_less(&*v_b, &*v_a);\n'
# Same protocol and names as Select c1 (capture.py BORROW_PREFIX_FIRST_CALL,
# a1-actual-body-c1.py MARKER/NORMAL); left = first argument = v_b.
CALL_PREFIX = b'''        //@ let left = v_b;
        //@ let right = v_a;
        //@ close_full_borrow_content::<T>(t, left);
        //@ close_full_borrow_content::<T>(t, right);
        //@ borrow(cmp_k, <T>.full_borrow_content(t, left));
        //@ borrow(cmp_k, <T>.full_borrow_content(t, right));
        //@ share_full_borrow::<T>(cmp_k, t, left);
        //@ share_full_borrow::<T>(cmp_k, t, right);
        //@ let left_ref = precreate_ref(left);
        //@ let right_ref = precreate_ref(right);
        //@ init_ref_share::<T>(cmp_k, t, left_ref);
        //@ init_ref_share::<T>(cmp_k, t, right_ref);
        //@ close_ref_own::<'cmp, T>(left_ref);
        //@ close_ref_own::<'cmp, T>(right_ref);
        //@ close <(&'cmp T, &'cmp T)>.own(t, std_tuple_2_::<&'cmp T, &'cmp T> { 0: left_ref, 1: right_ref });
        //@ open_frac_borrow(cmp_k, ref_initialized_(left_ref), 1/4);
        //@ open [?left_fraction]ref_initialized_::<T>(left_ref)();
        //@ open_frac_borrow(cmp_k, ref_initialized_(right_ref), 1/4);
        //@ open [?right_fraction]ref_initialized_::<T>(right_ref)();
/*@ {
            __vf_callback_unwind_pair();
            { close comparison_debt::<T>(t, cmp_k, left, right, left_ref, right_ref, left_fraction, right_fraction); }
            { recover_pair::<T>(left, right); }
        } @*/
'''
CALL_TYPED = (b"        let should_swap = is_less/*@::<F, (&'cmp T, &'cmp T), 'cmp>@*/"
              b'(&*v_b, &*v_a);\n')
CALL_NORMAL = b'''        //@ close comparison_debt::<T>(t, cmp_k, left, right, left_ref, right_ref, left_fraction, right_fraction);
        //@ end_lft_binding::<'cmp>();
        //@ recover_pair::<T>(left, right);
'''

# Tail (UNVERIFIED frontier, DESIGN.md D2/D4): select_unpredictable must branch
# on its condition (layer gate P2); byte view for the overlapping-permitted copy
# uses stock to_u8s_/from_u8s_ only. ManuallyDrop<T> erases to T in the
# translator; `&*v_b_swap_tmp` is create_ref(&tmp) + identity deref + reborrow.
COPY = b'        ptr::copy(v_a_swap, v_a, 1);\n'
COPY_PREFIX = b'''        //@ if should_swap { to_u8s_(v_b); to_u8s_(v_a); close exists::<option<isize>>(none); } else { to_u8s_(v_a); close exists::<option<isize>>(some(0)); }
'''
COPY_SUFFIX = b'''        //@ if should_swap { from_u8s_(v_b); from_u8s_(v_a); } else { from_u8s_(v_a); }
'''
LAST = b'        ptr::copy_nonoverlapping(&*v_b_swap_tmp, v_b, 1);\n'
LAST_PREFIX = b'''        //@ let tmp_ref = precreate_ref(&v_b_swap_tmp);
        //@ init_ref_readonly(tmp_ref, 1/2);
        //@ points_to_limits(tmp_ref);
        //@ close [1/2]array(tmp_ref + 1, 0, nil);
        //@ close [1/2]array(tmp_ref, 1, cons(*tmp_ref, nil));
        //@ points_to_limits(v_b);
        //@ open points_to(v_b, _);
        //@ close array_(v_b + 1, 0, nil);
        //@ close array_(v_b, 1, cons(some(*v_b), nil));
'''
LAST_SUFFIX = b'''        //@ open array(v_b, 1, _);
        //@ open array(v_b + 1, 0, _);
        //@ open [1/2]array(tmp_ref, 1, _);
        //@ open [1/2]array(tmp_ref + 1, 0, _);
        //@ end_ref_readonly(tmp_ref);
'''


def need(ok, why):
    if not ok:
        raise SystemExit('R4 CONSTRUCT REFUSED: ' + why)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def strip_ghost(source):
    return GHOST_LINE.sub(b'', GHOST_BLOCK.sub(b'', source))


def extract(std):
    need(sha(std) == SOURCE_SHA256, 'std smallsort.rs SHA256 differs from the pinned shared baseline')
    lines = std.split(b'\n')
    lo, hi = STD_SPAN
    need(lines[lo - 1].startswith(b'unsafe fn swap_if_less<T, F>(v_base: *mut T, a_pos: usize, b_pos: usize, is_less: &mut F)'),
         'swap_if_less signature moved')
    need(lines[hi - 1] == b'}' and lines[hi] == b'', 'swap_if_less closing brace moved')
    body = b'\n'.join(lines[lo - 1:hi]) + b'\n'
    for fragment, expected in COUNTS.items():
        need(body.count(fragment) == expected, 'call inventory changed: ' + fragment.decode())
    return body


def replace_once(text, old, new, why):
    need(text.count(old) == 1, why)
    return text.replace(old, new, 1)


def construct(std, recover_pair_rs, select_spec=b''):
    body = extract(std)
    need(hashlib.sha1(b'blob %d\0' % len(recover_pair_rs) + recover_pair_rs).hexdigest() == SELECT_RECOVER_PAIR_BLOB,
         'Select recover_pair layer blob differs from the pinned consumer input')
    layer = recover_pair_rs.replace(b'#![no_std]\n', b'', 1).replace(b'#![allow(dead_code)]\n', b'', 1)
    v = body
    v = replace_once(v, b'{\n    // SAFETY', CONTRACT + b'{\n    // SAFETY', 'body opening brace')
    v = replace_once(v, UNSAFE_ANCHOR, LIFETIME_SCOPE, 'unsafe block anchor')
    v = replace_once(v, ADD_A, ADD_LIMITS + ADD_A, 'first add anchor')
    v = replace_once(v, CALL, CALL_PREFIX + CALL_TYPED + CALL_NORMAL, 'comparator call anchor')
    v = replace_once(v, COPY, COPY_PREFIX + COPY + COPY_SUFFIX, 'ptr::copy anchor')
    v = replace_once(v, LAST, LAST_PREFIX + LAST + LAST_SUFFIX, 'copy_nonoverlapping anchor')
    need(strip_ghost(v) == body, 'ghost stripping does not restore the exact actual body')
    crate = PREFIX + layer + b'\n' + select_spec + v
    need(strip_ghost(crate).endswith(body), 'crate tail is not the exact actual body')
    meta = {
        'schema': 'network-r4-swap-if-less-candidate-v1', 'status': 'PREPARED_UNVERIFIED',
        'name': 'swap_if_less', 'std_source_sha256': SOURCE_SHA256, 'std_span': list(STD_SPAN),
        'std_body_sha256': sha(body), 'runtime_body_byteequal': True,
        'select_recover_pair_blob': SELECT_RECOVER_PAIR_BLOB,
        'select_pointer_spec_sha256': sha(select_spec) if select_spec else None,
        'domain': 'generic T/F; a_pos != b_pos (all sort9/sort13 sites); two separate owned cells; ZST admitted',
        'normal': 'both cells owned with current values; current F', 'unwind': 'both cells owned (callback recovery); current F',
        'equal_positions': 'OPEN (D3)', 'ordering_link': 'OPEN', 'proof_credit': False,
    }
    return crate, meta


def main():
    if len(sys.argv) not in (4, 5):
        raise SystemExit('usage: swap-if-less-body.py SMALLSORT_RS RECOVER_PAIR_RS OUT_DIR [SELECT_POINTER_SPEC]')
    std = Path(sys.argv[1]).read_bytes()
    recover = Path(sys.argv[2]).read_bytes()
    spec = Path(sys.argv[4]).read_bytes() if len(sys.argv) == 5 else b''
    crate, meta = construct(std, recover, spec)
    out = Path(sys.argv[3])
    out.mkdir(parents=True, exist_ok=True)
    (out / 'lib.rs').write_bytes(crate)
    meta['crate_sha256'] = sha(crate)
    (out / 'meta.json').write_text(json.dumps(meta, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'crate_sha256': meta['crate_sha256'], 'std_body_sha256': meta['std_body_sha256']}))


if __name__ == '__main__':
    main()
