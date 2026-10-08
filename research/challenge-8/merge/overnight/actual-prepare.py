#!/usr/bin/env python3
"""Hosted-only exact-source merge callee preparation; no local invocation."""
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

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def strip(data: str) -> str:
    return re.sub(r"(?m)^[ \t]*//@[^\r\n]*(?:\r?\n|$)", "",
                  re.sub(r"/\*@.*?@\*/", "", data, flags=re.S))

def contract(name: str) -> str:
    result_posts = (
        "((result.0 == left_src + 1 && result.1 == right_src && copied == lv1) || "
        "(result.0 == left_src && result.1 == right_src + 1 && copied == rv1)) &*& result.2 == dst + 1"
        if name == "merge_up" else
        "((result.0 as pointer == wrapping_pointer_offset(left_src as pointer, -std::mem::size_of::<T>()) && result.1 == right_src && copied == lv1) || "
        "(result.0 == left_src && result.1 as pointer == wrapping_pointer_offset(right_src as pointer, -std::mem::size_of::<T>()) && copied == rv1)) &*& result.2 == dst - 1"
    )
    common = """thread_token(t) &*& type_interp::<T>() &*& type_interp::<F>() &*&
    *left_src |-> ?lv1 &*& <T>.own(t, lv1) &*&
    *right_src |-> ?rv1 &*& <T>.own(t, rv1) &*&
    *is_less |-> ?f1 &*& <F>.own(t, f1)"""
    return """/*@
req thread_token(?t) &*& t == currentThread &*& type_interp::<T>() &*& type_interp::<F>() &*&
    0 < std::mem::size_of::<T>() &*& std::mem::size_of::<T>() <= isize::MAX &*&
    left_src as pointer != right_src as pointer &*&
    0 < left_src as usize &*& 0 < right_src as usize &*& 0 < dst as usize &*&
    left_src as usize % std::mem::align_of::<T>() == 0 &*&
    right_src as usize % std::mem::align_of::<T>() == 0 &*&
    dst as usize % std::mem::align_of::<T>() == 0 &*&
    left_src as usize <= usize::MAX - std::mem::size_of::<T>() &*&
    right_src as usize <= usize::MAX - std::mem::size_of::<T>() &*&
    dst as usize <= usize::MAX - std::mem::size_of::<T>() &*&
    object_pointer_within_limits(left_src, std::mem::size_of::<T>()) == true &*&
    object_pointer_within_limits(right_src, std::mem::size_of::<T>()) == true &*&
    object_pointer_within_limits(dst, std::mem::size_of::<T>()) == true &*&
    (left_src as usize + std::mem::size_of::<T>() <= dst as usize ||
     dst as usize + std::mem::size_of::<T>() <= left_src as usize) &*&
    (right_src as usize + std::mem::size_of::<T>() <= dst as usize ||
     dst as usize + std::mem::size_of::<T>() <= right_src as usize) &*&
    *left_src |-> ?lv &*& <T>.own(t, lv) &*&
    *right_src |-> ?rv &*& <T>.own(t, rv) &*&
    *dst |-?-> ?dst0 &*& *is_less |-> ?f0 &*& <F>.own(t, f0) &*&
    pointer_within_limits(left_src + 1) == true &*&
    pointer_within_limits(right_src + 1) == true &*&
    pointer_within_limits(dst + 1) == true &*& pointer_within_limits(dst - 1) == true;
@*//*@
ens """ + common + " &*& *dst |-> ?copied &*&\n    " + result_posts + ";\n@*//*@\non_unwind_ens " + common + " &*& *dst |-?-> dst0;\n@*/"

def main() -> None:
    if (os.environ.get("GITHUB_ACTIONS") != "true" or
        os.environ.get("RUNNER_ENVIRONMENT") != "github-hosted" or
        os.environ.get("GITHUB_REF") != "refs/heads/overnight/merge-26.10"):
        raise RuntimeError("actual preparation requires own GitHub-hosted Actions branch")
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise RuntimeError("refusing existing source fixture")
    spec = importlib.util.spec_from_file_location("merge_actual_admission", HERE.parent / "stock-26.10/prove.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    admission = module.admit_source()
    source = SOURCE.read_text()
    header = "#![feature(unboxed_closures)]\nuse core::ptr;\n"
    fixture = header
    record = {"source_admission": admission, "source_sha256": sha(SOURCE.read_bytes()),
              "scope": "distinct-source positive-stride writable option destination with explicit C1 pointer domain conditional actual callee; generic safety/callback effects and both full posts remain targets",
              "cases": {}}
    for name in ("merge_up", "merge_down"):
        marker = f"unsafe fn {name}<T, F: FnMut(&T, &T) -> bool>("
        if source.count(marker) != 1:
            raise RuntimeError(f"changed exact signature: {name}")
        start = source.index(marker)
        end_match = re.search(r"(?m)^}\n", source[start:])
        if end_match is None:
            raise RuntimeError(f"missing exact body end: {name}")
        original = source[start:start + end_match.end()]
        brace = original.index("{")
        verified = original[:brace] + contract(name) + original[brace:]
        # Ghost type instantiation is an annotation on the unchanged actual call.
        anchor = "let is_l = !is_less(&*right_src, &*left_src);"
        if verified.count(anchor) != 1:
            raise RuntimeError(f"changed exact callback statement: {name}")
        verified = verified.replace(anchor,
            "let is_l = !is_less/*@::<F, (&'cmp T, &'cmp T), 'cmp>@*/(&*right_src, &*left_src);")
        # Establish the actual two shared-reference arguments from distinct
        # initialized source cells. The opt-in three-marker cleanup profile
        # checks the exact callback/normal/Continue-unwind scope mapping.
        verified = verified.replace("    unsafe {\n",
            "    //@ let cmp_k = begin_lifetime();\n    unsafe {\n"
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
            "        //@ close <(&'cmp T, &'cmp T)>.own(t, std_tuple_2_::<&'cmp T, &'cmp T> { 0: right_ref, 1: left_ref });\n", 1)
        cleanup = (
            "        //@ { callback_close::<'cmp>(); close [left_ref_frac]ref_initialized_::<T>(left_ref)(); close_frac_borrow(left_ref_frac, ref_initialized_(left_ref)); close [right_ref_frac]ref_initialized_::<T>(right_ref)(); close_frac_borrow(right_ref_frac, ref_initialized_(right_ref)); }\n"
            "        //@ callback_scope_end::<'cmp>();\n"
            "        //@ { callback_recover::<'cmp>(); end_lifetime(cmp_k); borrow_end(cmp_k, <T>.full_borrow_content(t, left_src as *T)); open_full_borrow_content::<T>(t, left_src as *T); borrow_end(cmp_k, <T>.full_borrow_content(t, right_src as *T)); open_full_borrow_content::<T>(t, right_src as *T); }\n"
        )
        after_call = "(&*right_src, &*left_src);\n"
        if verified.count(after_call) != 1:
            raise RuntimeError(f"changed exact callback end: {name}")
        verified = verified.replace(after_call, after_call + cleanup, 1)
        if strip(verified) != original:
            raise RuntimeError(f"ghost stripping changes actual runtime source: {name}")
        record["cases"][name] = {"source_line": source[:start].count("\n") + 1,
            "exact_function_sha256": sha(original.encode()), "verified_sha256": sha(verified.encode()),
            "ghost_strip_exact": True, "target_posts": "updated valid source ownership/callback state; selected copy and exact cursor advances normal; untouched destination on callback unwind",
            "excluded": "ZST, coincident source, arbitrary invalid destination bytes, caller derivation of C1 domain; not a generic whole-callee acceptance"}
        fixture += f"// CASE_BEGIN {name}\n" + verified + f"// CASE_END {name}\n"
    args.output.write_text(fixture)
    args.output.with_suffix(".admission.json").write_text(json.dumps(record, indent=2) + "\n")

if __name__ == "__main__":
    main()
