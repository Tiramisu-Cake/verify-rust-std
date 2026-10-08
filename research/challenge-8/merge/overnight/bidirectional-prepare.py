#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted-only exact-source extractor for the len-2 bidirectional merge profile."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCE = ROOT / "library/core/src/slice/sort/shared/smallsort.rs"
FREEZE_SOURCE = ROOT / "library/core/src/slice/sort/shared/mod.rs"
FREEZE_TRAIT = (
    "/// SAFETY: this is safety relevant, how does this interact with the soundness holes in\n"
    "/// specialization?\n"
    "#[unsafe(rustc_allow_lifetime_dependent_specialization)]\n"
    "pub(crate) trait FreezeMarker {}\n\n"
)
FREEZE_TRAIT_SHA256 = "9c2029134f74cc3d2d29d14932e5bd01c65c52c78f461b933666491b6f61003f"
PANIC_SIGNATURE = "fn panic_on_ord_violation() -> ! {"
PANIC_BODY_SHA256 = "2732f3532a1d8796efc7d9b16221bdc1820d1a9e42a4e0de92d426a33a583e5f"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def strip_ghost(data: str) -> str:
    data = re.sub(r"(?m)^[ \t]*//@[^\r\n]*(?:\r?\n|$)", "", data)
    return re.sub(r"/\*@.*?@\*/", "", data, flags=re.S)


def extract(source: str, signature: str, name: str) -> str:
    if source.count(signature) != 1:
        raise RuntimeError(f"missing or ambiguous exact signature: {name}")
    start = source.index(signature)
    end = source.find("\n}\n", start)
    if end < 0:
        raise RuntimeError(f"missing exact body end: {name}")
    return source[start:end + 2]


def actual_helper(name: str, source: str, signature: str, helper: object) -> tuple[str, dict]:
    original = extract(source, signature, name)
    verified = original[:original.index("{")] + helper.contract(name) + original[original.index("{"):]

    call = "let is_l = !is_less(&*right_src, &*left_src);"
    if verified.count(call) != 1:
        raise RuntimeError(f"callback anchor changed: {name}")
    verified = verified.replace(
        call,
        "let is_l = !is_less/*@::<F, (&'cmp T, &'cmp T), 'cmp>@*/(&*right_src, &*left_src);",
    )
    unsafe_anchor = "    unsafe {\n"
    setup = (
        "    //@ let cmp_k = begin_lifetime();\n"
        "    unsafe {\n"
        "        //@ let_lft 'cmp = cmp_k;\n"
        "        //@ close_full_borrow_content::<T>(t, left_src as *T);\n"
        "        //@ borrow(cmp_k, <T>.full_borrow_content(t, left_src as *T));\n"
        "        //@ share_full_borrow::<T>(cmp_k, t, left_src as *T);\n"
        "        //@ close_full_borrow_content::<T>(t, right_src as *T);\n"
        "        //@ borrow(cmp_k, <T>.full_borrow_content(t, right_src as *T));\n"
        "        //@ share_full_borrow::<T>(cmp_k, t, right_src as *T);\n"
        "        //@ let left_ref = precreate_ref(left_src as *T);\n"
        "        //@ init_ref_share::<T>(cmp_k, t, left_ref);\n"
        "        //@ let right_ref = precreate_ref(right_src as *T);\n"
        "        //@ init_ref_share::<T>(cmp_k, t, right_ref);\n"
        "        //@ open_frac_borrow(cmp_k, ref_initialized_(left_ref), 1/4);\n"
        "        //@ open [?left_ref_frac]ref_initialized_::<T>(left_ref)();\n"
        "        //@ close_ref_own::<'cmp, T>(left_ref);\n"
        "        //@ open_frac_borrow(cmp_k, ref_initialized_(right_ref), 1/4);\n"
        "        //@ open [?right_ref_frac]ref_initialized_::<T>(right_ref)();\n"
        "        //@ close_ref_own::<'cmp, T>(right_ref);\n"
        "        //@ close <(&'cmp T, &'cmp T)>.own(t, std_tuple_2_::<&'cmp T, &'cmp T> { 0: right_ref, 1: left_ref });\n"
    )
    if verified.count(unsafe_anchor) != 1:
        raise RuntimeError(f"callback scope anchor changed: {name}")
    verified = verified.replace(unsafe_anchor, setup, 1)
    cleanup = (
        "        //@ { callback_close::<'cmp>(); close [left_ref_frac]ref_initialized_::<T>(left_ref)(); close_frac_borrow(left_ref_frac, ref_initialized_(left_ref)); close [right_ref_frac]ref_initialized_::<T>(right_ref)(); close_frac_borrow(right_ref_frac, ref_initialized_(right_ref)); }\n"
        "        //@ callback_scope_end::<'cmp>();\n"
        "        //@ { callback_recover::<'cmp>(); end_lifetime(cmp_k); borrow_end(cmp_k, <T>.full_borrow_content(t, left_src as *T)); open_full_borrow_content::<T>(t, left_src as *T); borrow_end(cmp_k, <T>.full_borrow_content(t, right_src as *T)); open_full_borrow_content::<T>(t, right_src as *T); }\n"
    )
    call_end = "(&*right_src, &*left_src);\n"
    if verified.count(call_end) != 1:
        raise RuntimeError(f"callback end anchor changed: {name}")
    verified = verified.replace(call_end, call_end + cleanup, 1)
    if strip_ghost(verified) != original:
        raise RuntimeError(f"ghost stripping changes actual runtime source: {name}")
    return verified, {
        "exact_source_sha256": sha(original.encode()),
        "fixture_body_sha256": sha(verified.encode()),
        "ghost_strip_exact": True,
        "body_present": True,
        "call_target": "actual extracted callee body, with previously admitted bounded contract",
    }


def bidirectional_contract() -> str:
    # The unsafe projection contract states source cells and T owners
    # explicitly. It does not claim that an arbitrary SAFE caller can realize
    # those premises from an &[T] borrow.
    return """/*@
req thread_token(?t) &*& t == currentThread &*&
    type_interp::<T>() &*& type_interp::<F>() &*&
    ptr_len(v) == 2 &*&
    0 < std::mem::size_of::<T>() &*&
    std::mem::size_of::<T>() <= isize::MAX &*&
    0 < std::mem::align_of::<T>() &*&
    2 * std::mem::size_of::<T>() <= isize::MAX &*&
    0 < (v as *T) as usize &*& 0 < dst as usize &*&
    (v as *T) as usize % std::mem::align_of::<T>() == 0 &*&
    dst as usize % std::mem::align_of::<T>() == 0 &*&
    (v as *T) as usize <= usize::MAX - 2 * std::mem::size_of::<T>() &*&
    dst as usize <= usize::MAX - 2 * std::mem::size_of::<T>() &*&
    object_pointer_within_limits(v as *T, 2 * std::mem::size_of::<T>()) == true &*&
    object_pointer_within_limits(dst, 2 * std::mem::size_of::<T>()) == true &*&
    pointer_within_limits((v as *T) + 1) == true &*&
    pointer_within_limits((v as *T) + 2) == true &*&
    pointer_within_limits(dst + 1) == true &*&
    pointer_within_limits(dst + 2) == true &*&
    ((v as *T) as usize + 2 * std::mem::size_of::<T>() <= dst as usize ||
     dst as usize + 2 * std::mem::size_of::<T>() <= (v as *T) as usize) &*&
    *(v as *T) |-> ?source0 &*& <T>.own(t, source0) &*&
    *((v as *T) + 1) |-> ?source1 &*& <T>.own(t, source1) &*&
    *dst |-?-> ?dst0 &*& *(dst + 1) |-?-> ?dst1 &*&
    *is_less |-> ?f0 &*& <F>.own(t, f0);
@*//*@
ens thread_token(t) &*& type_interp::<T>() &*& type_interp::<F>() &*&
    *(v as *T) |-> ?source0_after &*& <T>.own(t, source0_after) &*&
    *((v as *T) + 1) |-> ?source1_after &*& <T>.own(t, source1_after) &*&
    *dst |-> ?out0 &*& *(dst + 1) |-> ?out1 &*&
    *is_less |-> ?f1 &*& <F>.own(t, f1);
@*//*@
on_unwind_ens thread_token(t) &*& type_interp::<T>() &*& type_interp::<F>() &*&
    *(v as *T) |-> ?source0_unwind &*& <T>.own(t, source0_unwind) &*&
    *((v as *T) + 1) |-> ?source1_unwind &*& <T>.own(t, source1_unwind) &*&
    *dst |-?-> ?partial0 &*& *(dst + 1) |-?-> ?partial1 &*&
    ((partial0 == dst0 && partial1 == dst1) ||
     (partial0 == some(?written0) && partial1 == dst1) ||
     (partial0 == some(?written1) && partial1 == some(?written2))) &*&
    *is_less |-> ?f_unwind &*& <F>.own(t, f_unwind);
    @*/"""


def panic_contract() -> str:
    return """/*@
req true;
@*//*@
ens false;
@*//*@
on_unwind_ens true;
@*/"""


def insert_one_iteration_invariant(body: str) -> str:
    dst_init = "        let mut dst = dst;\n"
    loop = "        for _ in 0..len_div_2 {\n"
    src_init = "    let src = v.as_ptr();\n"
    if body.count(dst_init) != 1 or body.count(loop) != 1 or body.count(src_init) != 1:
        raise RuntimeError("bidirectional cursor/loop anchors changed")
    body = body.replace(src_init, src_init + "    //@ size_align::<T>();\n", 1)
    body = body.replace(dst_init, "        //@ let dst_base = dst;\n" + dst_init, 1)
    invariant = """        /*@
        inv thread_token(t) &*& type_interp::<T>() &*& type_interp::<F>() &*&
            len == 2 &*& len_div_2 == 1 &*&
            *src |-> ?inv_source0 &*& <T>.own(t, inv_source0) &*&
            *(src + 1) |-> ?inv_source1 &*& <T>.own(t, inv_source1) &*&
            *is_less |-> ?inv_f &*& <F>.own(t, inv_f) &*&
            *dst_base |-?-> ?inv_dst0 &*& *(dst_base + 1) |-?-> ?inv_dst1 &*&
            ((left == src && right == src + 1 && left_rev == src &&
              right_rev == src + 1 && dst == dst_base && dst_rev == dst_base + 1) ||
             ((left == src + 1 && right == src + 1 ||
               left == src && right == src + 2) &&
              ((left_rev == src && right_rev == src) ||
               ((left_rev as pointer) == wrapping_pointer_offset(src as pointer,
                 -std::mem::size_of::<T>()) && right_rev == src + 1)) &&
              dst == dst_base + 1 && dst_rev == dst_base));
        @*/
"""
    return body.replace(loop, invariant + loop, 1)


def main() -> None:
    if (os.environ.get("GITHUB_ACTIONS") != "true" or
            os.environ.get("RUNNER_ENVIRONMENT") != "github-hosted" or
            os.environ.get("GITHUB_REF") != "refs/heads/overnight/merge-26.10"):
        raise RuntimeError("bidirectional preparation requires own GitHub-hosted Actions branch")
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise RuntimeError("refusing existing generated fixture")

    spec = importlib.util.spec_from_file_location(
        "merge_stock_source_gate", HERE.parent / "stock-26.10/prove.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen actual-source gate")
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)
    admission = gate.admit_source()
    source = SOURCE.read_text()
    freeze_source = FREEZE_SOURCE.read_text()
    if freeze_source.count(FREEZE_TRAIT) != 1 or sha(FREEZE_TRAIT.encode()) != FREEZE_TRAIT_SHA256:
        raise RuntimeError("exact repository FreezeMarker declaration changed")

    helper_spec = importlib.util.spec_from_file_location("merge_actual_prepare", HERE / "actual-prepare.py")
    if helper_spec is None or helper_spec.loader is None:
        raise RuntimeError("cannot load accepted helper preparation functions")
    helper = importlib.util.module_from_spec(helper_spec)
    helper_spec.loader.exec_module(helper)

    out = "#![feature(unboxed_closures, core_intrinsics)]\n#![allow(dead_code)]\nuse core::ptr;\nuse core::intrinsics;\ntrait FreezeMarker {}\n"
    out += "// CASE_BEGIN bidirectional_merge_len2\n"
    records: dict[str, object] = {}
    for name in ("merge_up", "merge_down"):
        prepared, record = actual_helper(name, source, gate.SIGNATURES[name], helper)
        out += prepared + "\n"
        records[name] = record

    panic = extract(source, PANIC_SIGNATURE, "panic_on_ord_violation")
    if sha(panic.encode()) != PANIC_BODY_SHA256:
        raise RuntimeError("panic_on_ord_violation exact repository body changed")
    prepared_panic = panic[:panic.index("{")] + panic_contract() + panic[panic.index("{"):]
    if strip_ghost(prepared_panic) != panic:
        raise RuntimeError("panic contract changed actual runtime body")
    out += prepared_panic + "\n"
    records["panic_on_ord_violation"] = {
        "exact_source_sha256": sha(panic.encode()),
        "accepted_source_body_sha256": PANIC_BODY_SHA256,
        "fixture_body_sha256": sha(prepared_panic.encode()),
        "body_present": True,
        "normal_post": "false",
        "unwind_post": "true (caller frame preserved)",
        "contract_basis": "actual body is the unconditional panic path; ens false rules out normal return; no extra semantic summary or termination assumption",
    }

    bidir = extract(source, gate.SIGNATURES["bidirectional_merge"], "bidirectional_merge")
    verified = bidir[:bidir.index("{")] + bidirectional_contract() + bidir[bidir.index("{"):]
    verified = insert_one_iteration_invariant(verified)
    if strip_ghost(verified) != bidir:
        raise RuntimeError("bidirectional contract changed actual runtime body")
    out += verified + "\n// CASE_END bidirectional_merge_len2\n"
    records["bidirectional_merge"] = {
        "exact_source_sha256": sha(bidir.encode()),
        "fixture_body_sha256": sha(verified.encode()),
        "ghost_strip_exact": True,
        "body_present": True,
        "domain": "len=2; positive-sized/positive-aligned T; bounded separate source and destination spans",
        "source_resource": "two explicit source points-to and T.own chunks in the unsafe projection contract; no implicit &[T].own premise",
        "source_pointer_projection": "stock translator lowers slice as_ptr by fat-to-thin cast (v as *T) and len to ptr_len(v); SAFE caller realization from &[T] remains open",
        "normal_target": "current source values/owners and F owner; both option destinations initialized; no destination T.own",
        "unwind_target": "current source values/owners and F owner; destinations unchanged if first callback panics, first initialized only if reverse callback panics, both initialized if guard panics",
        "loop_invariant_status": "candidate source annotation only; iterator-state/cursor linkage is unvalidated",
        "restricted_domain_dead_branch": "len=2 proves the odd branch unreachable; preserve and report strict dead-code finding, do not count as an accepted full positive",
        "scope_warning": "diagnostic until hosted proof establishes source-pointer projection, C1 caller premises, exact partial destination behavior, and every actual body gate",
    }
    args.output.write_text(out)
    args.output.with_suffix(".admission.json").write_text(json.dumps({
        "source_admission": admission,
        "panic_on_ord_violation_body_sha256": PANIC_BODY_SHA256,
        "freeze_marker_declaration_sha256": FREEZE_TRAIT_SHA256,
        "freeze_marker_adapter": "empty local declaration only; no blanket impl or Freeze/purity theorem",
        "scope": "exact unchanged bidirectional_merge len=2 with actual merge_up/down bodies; experimental and unaccepted pending hosted matrix",
        "cases": records,
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()
