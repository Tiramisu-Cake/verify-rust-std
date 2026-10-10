#!/usr/bin/env python3
"""Cloud-only source preparation for the bounded native-entry/c1 composition.

This script only writes source and certificates. Compiler, MIR, refinement and
verification belong to the Cloud runner. It deliberately never makes the
bounded actual sort4 AST a callable Rust callee.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re


HERE = Path(__file__).resolve().parent
STD = Path("library/core/src/slice/sort/shared/smallsort.rs")
STD_SHA = "85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1"
CALLER = Path("research/challenge-8/caller-entry/prepare.py")
CAPTURE = Path("research/challenge-8/overnight-sort4/capture.py")
CALLBACK = Path("research/challenge-8/overnight-callback/callback-cases.rs")
JOIN = Path("research/challenge-8/overnight-callback/join-four-owned-cells.rs")
FIRST = b"        let c1 = is_less(&*v_base.add(1), &*v_base);"
ANNOTATED = (b"        let c1 = is_less/*@::<F, (&'cmp T, &'cmp T), 'cmp>@*/"
             b"(&*v_base.add(1), &*v_base);")


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def strip_ghost(data: bytes) -> bytes:
    data = re.sub(rb"/\*@.*?@\*/(?:\r?\n)?", b"", data, flags=re.S)
    return re.sub(rb"(?m)^[ \t]*//@[^\r\n]*(?:\r?\n|$)", b"", data)


def exact_ghost_source(path: Path, start: bytes, end: bytes) -> bytes:
    data = path.read_bytes()
    need(data.count(start) == data.count(end) == 1,
         f"ghost source anchors ambiguous: {path}")
    part = data[data.index(start):data.index(end)]
    need(part.startswith(b"/*@") and part.count(b"/*@") == 2 and
         part.count(b"@*/") == 2, "callback ghost prefix shape")
    part = part.replace(b"@*/\n\n/*@", b"@*/\n/*@", 1)
    part = part.rstrip() + b"\n"
    need(strip_ghost(part) == b"", "callback ghost prefix leaves runtime bytes")
    return part


def source_lemmas(repo: Path) -> bytes:
    # The checked definitions are copied, never weakened or turned into axioms.
    callback = exact_ghost_source(
        repo / CALLBACK, b"/*@\npred comparison_debt<T>(",
        b"// CASE_BEGIN callback_positive\n")
    join = (repo / JOIN).read_bytes()
    need(join.startswith(b"/*@\nlem join_four_owned_cells<T>(") and
         join.rstrip().endswith(b"@*/"), "join lemma shape")
    capture = (repo / CAPTURE).read_bytes()
    interior_start = b"MEMORY_PRE_INTERIOR_LEMMA = b\"\"\""
    split_start = b"BORROW_PREFIX_SPLIT_LEMMA = b\"\"\""
    # Static source snippets are decoded as Python byte literals only; no
    # source-preparation module or proof entrypoint is executed here.
    def literal(anchor: bytes) -> bytes:
        need(capture.count(anchor) == 1, "capture lemma anchor")
        offset = capture.index(anchor) + len(anchor)
        finish = capture.index(b'\"\"\"', offset)
        return capture[offset:finish]
    interior = literal(interior_start)
    split = literal(split_start)
    need(interior.startswith(b"/*@\nlem interior_pointer_limits<T>(") and
         split.startswith(b"/*@\nlem split_four_owned_cells<T>("),
         "checked source helper identity")
    all_lemmas = interior + split + callback + join
    need(not any(word in all_lemmas for word in (b"assume(", b"admit(", b"unchecked")),
         "proof helper assumption/admission")
    return all_lemmas


PREFIX = b"""#![feature(freeze, rustc_attrs, core_intrinsics)]
#![allow(internal_features)]
#![allow(dead_code)]

use std::{intrinsics, mem::{MaybeUninit, size_of}};
use std::marker::Freeze;

"""

HELPER = b"""pub unsafe fn c1_source_prefix<T, F: FnMut(&T, &T) -> bool>(
    v_base: *const T,
    len: usize,
    is_less: &mut F,
) -> bool
/*@
req thread_token(?t) &*& t == currentThread &*&
    8 <= len &*&
    0 < std::mem::size_of::<T>() &*&
    v_base[..len] |-> ?source_before &*&
    foreach(source_before, own::<T>(t)) &*&
    *is_less |-> ?less_before &*& <F>.own(t, less_before);
@*/
/*@
ens thread_token(t) &*&
    v_base[..len] |-> ?source_after &*&
    foreach(source_after, own::<T>(t)) &*&
    *is_less |-> ?less_after &*& <F>.own(t, less_after);
@*/
/*@
on_unwind_ens thread_token(t) &*&
    v_base[..len] |-> ?source_after &*&
    foreach(source_after, own::<T>(t)) &*&
    *is_less |-> ?less_after &*& <F>.own(t, less_after);
@*/
{
    //@ produce_type_interp::<T>();
    //@ produce_type_interp::<F>();
    //@ let cmp_k = begin_lifetime();
    let mut result: bool;
    unsafe {
/*@ let_lft 'cmp = cmp_k; @*/
        //@ array_split::<T>(v_base, 4);
        //@ foreach_split(source_before, own::<T>(t), 4);
        //@ interior_pointer_limits::<T>(v_base, 4, 1);
        //@ split_four_owned_cells::<T>(v_base, t);
        //@ close_full_borrow_content::<T>(t, v_base + 1);
        //@ close_full_borrow_content::<T>(t, v_base);
        //@ borrow(cmp_k, <T>.full_borrow_content(t, v_base + 1));
        //@ borrow(cmp_k, <T>.full_borrow_content(t, v_base));
        //@ share_full_borrow::<T>(cmp_k, t, v_base + 1);
        //@ share_full_borrow::<T>(cmp_k, t, v_base);
        //@ let left_ref = precreate_ref(v_base + 1);
        //@ let right_ref = precreate_ref(v_base);
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
            __vf_c1_compose_unwind();
            { close comparison_debt::<T>(t, cmp_k, v_base + 1, v_base, left_ref, right_ref, left_fraction, right_fraction); }
            { recover_pair::<T>(v_base + 1, v_base); }
            { join_four_owned_cells::<T>(v_base, t); }
            { assert v_base[..4] |-> ?first_current;
              array_join::<T>(v_base);
              foreach_append(first_current, drop(4, source_before));
              leak type_interp::<T>();
              leak type_interp::<F>(); }
        } @*/
        let c1 = is_less/*@::<F, (&'cmp T, &'cmp T), 'cmp>@*/(&*v_base.add(1), &*v_base);
        //@ close comparison_debt::<T>(t, cmp_k, v_base + 1, v_base, left_ref, right_ref, left_fraction, right_fraction);
        result = c1;
        //@ end_lft_binding::<'cmp>();
    }
    //@ recover_pair::<T>(v_base + 1, v_base);
    //@ join_four_owned_cells::<T>(v_base, t);
    //@ assert v_base[..4] |-> ?first_current;
    //@ array_join::<T>(v_base);
    //@ foreach_append(first_current, drop(4, source_before));
    //@ leak type_interp::<T>();
    //@ leak type_interp::<F>();
    result
}
"""

NATIVE = b"""fn small_sort_general_with_scratch<T: FreezeMarker, F: FnMut(&T, &T) -> bool>(
    v: &mut [T],
    scratch: &mut [MaybeUninit<T>],
    is_less: &mut F,
) {
    let len = v.len();
    let v_base = v.as_mut_ptr();
    let len_div_2 = len / 2;
    unsafe {
        let scratch_base = scratch.as_mut_ptr() as *mut T;
        if len >= 8 && size_of::<T>() > 0 {
            /*@ assert thread_token(?t);
                assert t == currentThread;
                assert v_base[..len] |-> ?source_all;
                assert foreach(source_all, own::<T>(t));
                assert *is_less |-> ?less_before;
                assert <F>.own(t, less_before); @*/
            let _c1 = c1_source_prefix(v_base, len, is_less);
            /*@ assert v_base[..len] |-> ?source_current;
                assert foreach(source_current, own::<T>(t));
                assert *is_less |-> ?less_current;
                assert <F>.own(t, less_current); @*/
        }
    }
}
"""


def prepare(repo: Path, out: Path, case: str = "positive") -> dict:
    need(case in {"positive", "normal-false-post", "unwind-false-post",
                  "missing-debt", "missing-owner"}, "unknown composition case")
    need(os.environ.get("SMALLSORT_EXECUTION_PROVIDER") == "cloud-build" and
         os.environ.get("LANE") == "o26-sort4-caller-entry" and
         not os.environ.get("GITHUB_ACTIONS"), "Cloud-only composition lane")
    repo = repo.resolve()
    out = out.resolve()
    need(str(repo).startswith("/workspace/") and str(out).startswith("/workspace/"),
         "workspace paths required")
    need(not out.exists(), "fresh fixture required")
    std = (repo / STD).read_bytes()
    need(sha(std) == STD_SHA and std.count(FIRST) == 1, "pinned std first c1")
    caller_prep = (repo / CALLER).read_bytes()
    need(b"FUNCTION_NAME = b\"fn small_sort_general_with_scratch" in caller_prep,
         "source caller preparation pin missing")
    marker = (repo / "library/core/src/marker.rs").read_bytes()
    freeze = (b'#[lang = "freeze"]\n'
              b'#[unstable(feature = "freeze", issue = "121675")]\n'
              b'pub unsafe auto trait Freeze {}')
    need(marker.count(freeze) == 1, "Freeze source definition")
    shared = (repo / "library/core/src/slice/sort/shared/mod.rs").read_bytes()
    begin = b"/// SAFETY: this is safety relevant, how does this interact with the soundness holes in\n"
    end = b"impl<T: Freeze> FreezeMarker for T {}"
    need(shared.count(begin) == shared.count(end) == 1, "FreezeMarker source definition")
    freeze_marker = shared[shared.index(begin):shared.index(end) + len(end)] + b"\n"
    helper = HELPER
    native = NATIVE
    if case == "normal-false-post":
        old = b"*is_less |-> ?less_after &*& <F>.own(t, less_after);\n@*/"
        need(helper.count(old) == 2, "two outcome posts required")
        helper = helper.replace(old, old[:-len(b";\n@*/")] + b" &*& false;\n@*/", 1)
    elif case == "unwind-false-post":
        old = b"*is_less |-> ?less_after &*& <F>.own(t, less_after);\n@*/"
        need(helper.count(old) == 2, "two outcome posts required")
        at = helper.rindex(old)
        helper = helper[:at] + old[:-len(b";\n@*/")] + b" &*& false;\n@*/" + helper[at + len(old):]
    elif case == "missing-debt":
        line = b"            { close comparison_debt::<T>(t, cmp_k, v_base + 1, v_base, left_ref, right_ref, left_fraction, right_fraction); }\n"
        need(helper.count(line) == 1, "unwind debt control site")
        helper = helper.replace(line, b"", 1)
    elif case == "missing-owner":
        line = b"        //@ join_four_owned_cells::<T>(v_base, t);\n"
        need(helper.count(line) == 1, "normal join control site")
        helper = helper.replace(line, b"", 1)
    verified = PREFIX + freeze + b"\n" + freeze_marker + b"\n" + source_lemmas(repo) + helper + b"\n" + native
    original = strip_ghost(verified)
    need(original.count(FIRST) == 1 and ANNOTATED in verified and
         verified.count(b"fn small_sort_general_with_scratch<") == 1 and
         b"sort4_stable(" not in verified, "bounded source inventory")
    need(not any(token in verified for token in (b"assume(", b"admit(", b"unchecked")),
         "forbidden proof-source assumption")
    out.mkdir(parents=True)
    (out / "original").mkdir()
    (out / "verified").mkdir()
    (out / "original/lib.rs").write_bytes(original)
    (out / "verified/lib.rs").write_bytes(verified)
    cert = {
        "case": case,
        "classification": "BOUNDED_NATIVE_C1_COMPOSITION_DIAGNOSTIC_NOT_ACTUAL_CALLER_CFG",
        "accepted": False,
        "actual_sort4_proved": False,
        "full_actual_caller_proved": False,
        "std_source_sha256": STD_SHA,
        "original_sha256": sha(original),
        "verified_sha256": sha(verified),
        "first_c1_runtime_line_exact": original.count(FIRST) == 1,
        "first_c1_source_line": std[:std.index(FIRST)].count(b"\n") + 1,
        "helper_name": "c1_source_prefix",
        "helper_dst_precondition": "none",
        "helper_type_interpretation": "stock produced and leaked internally on normal and direct unwind",
        "native_scratch_frame": "opaque MaybeUninit array and owners",
        "normal_post": "CURRENT source4/T owners/F and full native normal post",
        "unwind_post": "CURRENT source4/T owners/F and full native direct-unwind post",
        "domain": "native entry arbitrary; c1 operation only len>=8 and positive-size T",
    }
    (out / "source-certificate.json").write_text(json.dumps(cert, indent=2, sort_keys=True) + "\n")
    return cert
