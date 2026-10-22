#!/usr/bin/env python3
"""W7 candidate: annotated actual sort9_optimal / sort13_optimal (no proof tools).

Inert on import. Builds on the R4 generator (same std pin, same Select layer
blob): crate = R4 helper crate + generated checked split/join lemmas + one
actual network body with ghost text only. strip_ghost restores the exact body.
Status: PREPARED / UNVERIFIED. Safety/ownership only; no sorting claim.
"""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location('r4', HERE.parent / 'r4' / 'swap-if-less-body.py')
r4 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(r4)
need, sha, strip_ghost, replace_once = r4.need, r4.sha, r4.strip_ghost, r4.replace_once

# 1-based inclusive spans at blob 40939f92 (SOURCE-MAP re-pin 2026-10-22).
NETWORKS = {9: ('sort9_optimal', (420, 461), 25), 13: ('sort13_optimal', (469, 530), 45)}


# Crate header: R4 prefix plus the std-internal `intrinsics` path used by the
# actual bodies, in the form of Select's caller fixtures (a1-fixtures.py blob
# 797e3d11 @10e13a41: `core_intrinsics` feature + `use std::intrinsics;`).
W7_PREFIX = (b'#![feature(core_intrinsics)]\n'
             b'#![allow(internal_features)]\n'
             b'use std::{hint, ptr, mem::ManuallyDrop};\n'
             b'use std::intrinsics;\n\n')


def split_lemma(n):
    """Select's split_four_owned_cells pattern for the first n cells of base[..len]."""
    ens = ''.join(f'        *(base + {k}) |-> ?x{k} &*& <T>.own(t, x{k}) &*&\n' for k in range(n))
    cons = 'rest' + ''.join(')' for _ in range(n))
    cons = ''.join(f'cons(x{k}, ' for k in range(n)) + cons
    body = ''
    for k in range(n):
        cur = 'xs' if k == 0 else f'r{k}'
        target = 'base, len' if k == 0 else f'base + {k}, len - {k}'
        body += (f'    open array({target}, {cur});\n'
                 f'    assert {cur} == cons(?y{k}, ?r{k + 1});\n'
                 f'    open foreach({cur}, own::<T>(t));\n'
                 f'    open own::<T>(t)(y{k});\n')
    return (f'/*@\nlem split_owned_cells{n}<T>(base: *T, len: usize, t: thread_id_t)\n'
            f'    req base[..len] |-> ?xs &*& foreach(xs, own::<T>(t)) &*& {n} <= len;\n'
            f'    ens {ens.strip()}\n'
            f'        (base + {n})[..len - {n}] |-> ?rest &*& foreach(rest, own::<T>(t)) &*&\n'
            f'        xs == {cons};\n{{\n{body}}}\n@*/\n')


def join_lemma(n):
    req = ''.join(f'        *(base + {k}) |-> ?x{k} &*& <T>.own(t, x{k}) &*&\n' for k in range(n))
    body = ''
    for k in range(n):
        body += f'    points_to_limits(base + {k});\n    note(pointer_within_limits(base + {k}));\n'
    # One-past limit of the last cell, from the suffix chunk (Select's join notes base + 4).
    body += (f'    open array(base + {n}, len - {n}, rest);\n'
             f'    close array(base + {n}, len - {n}, rest);\n'
             f'    note(pointer_within_limits(base + {n}));\n')
    tail = 'rest'
    for k in reversed(range(n)):
        tail = f'cons(x{k}, {tail})'
        body += (f'    close own::<T>(t)(x{k});\n'
                 f'    close foreach({tail}, own::<T>(t));\n'
                 f'    close array(base + {k}, len - {k}, {tail});\n')
    return (f'/*@\nlem join_owned_cells{n}<T>(base: *T, len: usize, t: thread_id_t)\n'
            f'    req {req.strip()}\n'
            f'        (base + {n})[..len - {n}] |-> ?rest &*& foreach(rest, own::<T>(t)) &*& {n} <= len;\n'
            f'    ens base[..len] |-> {tail} &*& foreach({tail}, own::<T>(t));\n{{\n{body}}}\n@*/\n')


def contract(n):
    cells = ''.join(f'    *(v_base0 + {k}) |-> ?c{k} &*& <T>.own(t, c{k}) &*&\n' for k in range(n))
    return (b'/*@\nreq thread_token(?t) &*& t == currentThread &*& type_interp::<T>() &*& type_interp::<F>() &*&\n'
            b'    (v as *T)[..v.len()] |-> ?vs &*& foreach(vs, own::<T>(t)) &*&\n'
            b'    *is_less |-> ?less_before &*& <F>.own(t, less_before);\n@*/\n'
            b'/*@\nens thread_token(t) &*& type_interp::<T>() &*& type_interp::<F>() &*&\n'
            b'    (v as *T)[..v.len()] |-> ?vs1 &*& foreach(vs1, own::<T>(t)) &*&\n'
            b'    *is_less |-> ?less_after &*& <F>.own(t, less_after);\n@*/\n'
            b'/*@\non_unwind_ens thread_token(t) &*& type_interp::<T>() &*& type_interp::<F>() &*&\n'
            b'    v.len() >= ' + str(n).encode() + b' &*& v as *T == ?v_base0 &*&\n' + cells.encode() +
            b'    (v_base0 + ' + str(n).encode() + b')[..v.len() - ' + str(n).encode() +
            b'] |-> ?rest1 &*& foreach(rest1, own::<T>(t)) &*&\n'
            b'    *is_less |-> ?less_after &*& <F>.own(t, less_after);\n@*/\n')


def extract(std, n):
    name, (lo, hi), calls = NETWORKS[n]
    need(sha(std) == r4.SOURCE_SHA256, 'std smallsort.rs SHA256 differs from the pinned shared baseline')
    lines = std.split(b'\n')
    need(lines[lo - 1] == b'fn ' + name.encode() + b'<T, F>(v: &mut [T], is_less: &mut F)', name + ' signature moved')
    need(lines[hi - 1] == b'}' and lines[hi] == b'', name + ' closing brace moved')
    body = b'\n'.join(lines[lo - 1:hi]) + b'\n'
    need(body.count(b'swap_if_less(v_base, ') == calls, name + ' call count changed')
    need(body.count(b'let v_base = v.as_mut_ptr();\n') == 1 and body.count(b'intrinsics::abort();') == 1,
         name + ' prefix changed')
    return body


def construct(std, recover_pair_rs, n):
    helper, _ = r4.construct(std, recover_pair_rs)
    body = extract(std, n)
    name = NETWORKS[n][0]
    v = replace_once(body, b'{\n    if v.len() < ', contract(n) + b'{\n    if v.len() < ', name + ' opening brace')
    v = replace_once(v, b'    let v_base = v.as_mut_ptr();\n',
                     b'    let v_base = v.as_mut_ptr();\n'
                     b'    //@ split_owned_cells' + str(n).encode() + b'::<T>(v_base, v.len(), t);\n',
                     name + ' as_mut_ptr anchor')
    last = body[:body.rindex(b'swap_if_less(v_base, ')]
    close = body.index(b'\n    }\n}\n', len(last))
    v = replace_once(v, body[len(last):close + 1] + b'    }\n}\n',
                     body[len(last):close + 1] +
                     b'        //@ join_owned_cells' + str(n).encode() + b'::<T>(v_base, v.len(), t);\n    }\n}\n',
                     name + ' last-call anchor')
    need(strip_ghost(v) == body, 'ghost stripping does not restore the exact ' + name + ' body')
    need(helper.startswith(r4.PREFIX), 'R4 crate prefix changed')
    crate = W7_PREFIX + helper[len(r4.PREFIX):] + (split_lemma(n) + join_lemma(n)).encode() + v
    need(strip_ghost(crate).endswith(body), 'crate tail is not the exact actual body')
    call_lines = [i + 1 for i, line in enumerate(crate.split(b'\n'))
                  if line.startswith(b'        let should_swap = is_less/*@')]
    need(len(call_lines) == 1, 'comparator call line in the W7 crate')
    meta = {'schema': 'network-w7-candidate-v1', 'status': 'PREPARED_UNVERIFIED', 'name': name,
            'crate_call_line': call_lines[0],  # NETWORK_SWAP_IF_LESS_CALL_LINE for this crate
            'std_source_sha256': r4.SOURCE_SHA256, 'std_span': list(NETWORKS[n][1]),
            'std_body_sha256': sha(body), 'helper': 'R4 swap_if_less in the same crate (verified there, not assumed)',
            'calls': NETWORKS[n][2], 'domain': 'generic T/F; v.len() >= n normal path; v.len() < n aborts',
            'gates': ['P1/P2 (R4)', 'slice as_mut_ptr projection (Select caller-entry overlay)',
                      'intrinsics::abort spec', 'safe-fn spec vs type-derived spec'],
            'sorting': False, 'proof_credit': False}
    return crate, meta


def matrix(std, recover_pair_rs, n):
    """positive + ghost-only controls; std bodies exact in every variant."""
    crate, meta = construct(std, recover_pair_rs, n)
    name = NETWORKS[n][0]
    split = b'    //@ split_owned_cells%d::<T>(v_base, v.len(), t);\n' % n
    join = b'        //@ join_owned_cells%d::<T>(v_base, v.len(), t);\n' % n
    false_ = b'        //@ assert false;\n'
    mutations = {'split-off': (split, b''), 'join-off': (join, b''),
                 'reach-before-first': (split, split + b'    //@ assert false;\n'),
                 'reach-after-last': (join, false_ + join)}
    out = {'positive': crate}
    body_start = crate.index(b'fn ' + name.encode())
    for label, (old, new) in mutations.items():
        head, body = crate[:body_start], crate[body_start:]
        variant = head + replace_once(body, old, new, 'control anchor ' + label)
        need(strip_ghost(variant) == strip_ghost(crate), 'control is not ghost-only: ' + label)
        out[label] = variant
    return out, meta


EXPECTED = {'positive': 'PASS (helper + lemmas + network body)',
            'split-off': 'missing cell chunk at the first swap_if_less call',
            'join-off': 'postcondition failure (array/foreach not rejoined) or leak at return',
            'reach-before-first': 'assertion failure (PASS: state inconsistent after split; positive is not evidence)',
            'reach-after-last': 'assertion failure (PASS: state inconsistent after the calls; positive is not evidence)'}


def main():
    if len(sys.argv) != 4:
        raise SystemExit('usage: network-body.py SMALLSORT_RS RECOVER_PAIR_RS OUT_DIR')
    std, recover = Path(sys.argv[1]).read_bytes(), Path(sys.argv[2]).read_bytes()
    out = Path(sys.argv[3])
    need(not out.exists(), 'output directory must not exist')
    out.mkdir(parents=True)
    metas = {}
    for n in NETWORKS:
        variants, meta = matrix(std, recover, n)
        meta['controls'] = {}
        for label, crate in sorted(variants.items()):
            (out / f'sort{n}-{label}.rs').write_bytes(crate)
            lines = [i + 1 for i, line in enumerate(crate.split(b'\n'))
                     if line.startswith(b'        let should_swap = is_less/*@')]
            need(lines == [meta['crate_call_line']], 'control shifts the comparator call line: ' + label)
            # P1 opt-in per variant: NETWORK_SWAP_IF_LESS_SOURCE_SHA256 = crate_sha256, CALL_LINE = crate_call_line.
            meta['controls'][label] = {'crate_sha256': sha(crate), 'crate_call_line': lines[0],
                                       'expected': EXPECTED[label]}
        meta['crate_sha256'] = meta['controls']['positive']['crate_sha256']
        metas[f'sort{n}'] = meta
    (out / 'meta.json').write_text(json.dumps(metas, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: m['crate_sha256'] for k, m in metas.items()}))


if __name__ == '__main__':
    main()
