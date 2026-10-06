#!/usr/bin/env python3
"""Make a disposable VeriFast crate from the live SmallSort insertion code.

This is source preparation only. The verifier and refinement checker run on
GitHub-hosted Actions, never on the editing machine.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


SOURCE = Path("library/core/src/slice/sort/shared/smallsort.rs")
GHOSTS = {
    "frontend": "/*@ req true; @*/ /*@ ens true; @*/ ",
    "range": (
        "/*@\n"
        "req thread_token(?t) &*&\n"
        "    exists::<usize>(?n) &*&\n"
        "    n >= 2 &*&\n"
        "    begin[..n] |-> ?xs &*&\n"
        "    tail == begin + (n - 1) &*&\n"
        "    type_interp::<T>() &*& type_interp::<F>() &*&\n"
        "    foreach(xs, own::<T>(t)) &*&\n"
        "    *is_less |-> ?f &*& <F>.own(t, f);\n"
        "@*/ /*@ ens true; @*/ "
    ),
}
GHOSTS["tuple_overlay"] = GHOSTS["range"]
# This is an explicit comparison-resource exit diagnostic, not a restored
# range contract. No heap wildcard, assumed bridge, or leaked chunk is used.
COMPARISON_DEBT_POST = """thread_token(t) &*&
    type_interp::<T>() &*& type_interp::<F>() &*&
    *is_less |-> ?cmp_f &*& <F>.own(t, cmp_f) &*&
    begin[..n - 2] |-> ?cmp_prefix &*& foreach(cmp_prefix, own::<T>(t)) &*&
    [1/2]lifetime_token(?cmp_lifetime) &*&
    borrow_end_token(cmp_lifetime, <T>.full_borrow_content(t, tail)) &*&
    borrow_end_token(cmp_lifetime, <T>.full_borrow_content(t, begin + (n - 2))) &*&
    [?cmp_tail_fraction]ref_initialized::<T>(?cmp_tail_id) &*&
    close_frac_borrow_token(cmp_tail_fraction, ref_initialized_::<T>(cmp_tail_id), 1/4, cmp_lifetime) &*&
    [?cmp_sift_fraction]ref_initialized::<T>(?cmp_sift_id) &*&
    close_frac_borrow_token(cmp_sift_fraction, ref_initialized_::<T>(cmp_sift_id), 1/4, cmp_lifetime) &*&
    foreach(?cmp_remainder0, own::<T>(t)) &*& foreach(?cmp_remainder1, own::<T>(t))"""
GHOSTS["tuple_parser"] = GHOSTS["range"].replace(
    "/*@ ens true; @*/",
    "/*@ ens " + COMPARISON_DEBT_POST + "; @*/ /*@ on_unwind_ens " + COMPARISON_DEBT_POST + "; @*/",
)
GHOSTS["tuple_hrtb"] = GHOSTS["tuple_parser"]
CONTRACTS = {
    "frontend": "req true; ens true; no pointer or ownership precondition",
    "range": (
        "arbitrary n >= 2, initialized writable begin[..n], tail at n-1, "
        "generic T values owned, comparator F owned; ens true (safety probe only)"
    ),
}
CONTRACTS["tuple_overlay"] = CONTRACTS["range"] + "; patched bundled tuple-2 ownership spec"
CONTRACTS["tuple_parser"] = CONTRACTS["range"].replace("ens true (safety probe only)", "normal/unwind post explicitly returns partial comparison borrow resources; final restored-range contract unproved") + "; experimental tuple-2 parser; unmodified prelude"
CONTRACTS["tuple_hrtb"] = CONTRACTS["tuple_parser"] + "; compiler-origin HRTB Output instantiation; normal comparison accesses closed before lifetime recovery"
INSERT_SIGNATURE = (
    "unsafe fn insert_tail<T, F: FnMut(&T, &T) -> bool>"
    "(begin: *mut T, tail: *mut T, is_less: &mut F) {"
)
SIFT_ANCHOR = "        let mut sift = tail.sub(1);"
RANGE_INTERIOR_LEMMA = """/*@
lem interior_pointer_limits<T>(base: *T, count: usize, index: usize)
    req [?f]base[..count] |-> ?xs &*& 1 <= count &*& 0 <= index &*& index <= count;
    ens [f]base[..count] |-> xs &*& pointer_within_limits(base + index) == true;
{
    open array(base, count, xs);
    points_to_limits(base);
    close [f]array(base, count, xs);
    note(0 <= std::mem::size_of::<T>());
    array_inv::<T>();
    mul_mono_l(0, index, std::mem::size_of::<T>());
    mul_mono_l(index, count, std::mem::size_of::<T>());
    note(pointer_within_limits(base));
    note(pointer_within_limits(base + count));
}
@*/

"""
RANGE_BOUND_GHOST = "        //@ interior_pointer_limits::<T>(begin, n, n - 2);\n"
RANGE_LIFETIME_BEGIN = (
    "    //@ let cmp_k = begin_lifetime();\n"
    "    //@ assert lifetime_token(cmp_k);\n"
)
RANGE_LIFETIME_BIND = (
    "        /*@ let_lft 'cmp = cmp_k; @*/\n"
    "        //@ assert [1/2]lifetime_token(cmp_k);\n"
)
RANGE_COMPARE_PREP = """        //@ array_inv::<T>();
        //@ array_split::<T>(begin, n - 2);
        //@ array_split::<T>(begin + (n - 2), 1);
        //@ foreach_split(xs, own::<T>(t), n - 2);
        //@ length_drop(n - 2, xs);
        //@ note(length(drop(n - 2, xs)) == 2);
        //@ foreach_split(drop(n - 2, xs), own::<T>(t), 1);
        //@ note(sift == begin + (n - 2));
        //@ note(tail == begin + (n - 1));
        //@ open array::<T>(sift, 1, take(1, drop(n - 2, xs)));
        //@ open array::<T>(tail, 1, drop(1, drop(n - 2, xs)));
        //@ open foreach(take(1, drop(n - 2, xs)), own::<T>(t));
        //@ open foreach(drop(1, drop(n - 2, xs)), own::<T>(t));
        //@ open own::<T>(t)(head(take(1, drop(n - 2, xs))));
        //@ open own::<T>(t)(head(drop(1, drop(n - 2, xs))));
        //@ close_full_borrow_content::<T>(t, sift);
        //@ close_full_borrow_content::<T>(t, tail);
        //@ assert [1/2]lifetime_token(cmp_k);
        //@ borrow(cmp_k, <T>.full_borrow_content(t, sift));
        //@ assert [1/2]lifetime_token(cmp_k);
        //@ borrow(cmp_k, <T>.full_borrow_content(t, tail));
        //@ assert [1/2]lifetime_token(cmp_k);
        //@ share_full_borrow::<T>(cmp_k, t, sift);
        //@ assert [1/2]lifetime_token(cmp_k);
        //@ share_full_borrow::<T>(cmp_k, t, tail);
        //@ assert [1/2]lifetime_token(cmp_k);
        //@ let cmp_tail_ref = precreate_ref(tail);
        //@ let cmp_sift_ref = precreate_ref(sift);
        //@ init_ref_share::<T>(cmp_k, t, cmp_tail_ref);
        //@ assert [1/2]lifetime_token(cmp_k);
        //@ init_ref_share::<T>(cmp_k, t, cmp_sift_ref);
        //@ assert [1/2]lifetime_token(cmp_k);
        //@ merge_fractions lifetime_token(cmp_k);
        //@ assert [1/2]lifetime_token(cmp_k);
        //@ open_frac_borrow(cmp_k, ref_initialized_(cmp_tail_ref), 1/4);
        //@ assert [1/4]lifetime_token(cmp_k);
        //@ open [?tail_ref_frac]ref_initialized_::<T>(cmp_tail_ref)();
        //@ assert [1/4]lifetime_token(cmp_k);
        //@ open_frac_borrow(cmp_k, ref_initialized_(cmp_sift_ref), 1/4);
        //@ open [?sift_ref_frac]ref_initialized_::<T>(cmp_sift_ref)();
        //@ close_ref_own::<'cmp, T>(cmp_tail_ref);
        //@ close_ref_own::<'cmp, T>(cmp_sift_ref);
        //@ close <(&'cmp T, &'cmp T)>.own(t, std_tuple_2_::<&'cmp T, &'cmp T> { 0: cmp_tail_ref, 1: cmp_sift_ref });
"""
# Normal true-comparison path only. Both callback accesses must return their
# genuine initialization fractions before lifetime/token ownership is recovered.
RANGE_COMPARE_RECOVER = """        //@ close [tail_ref_frac]ref_initialized_::<T>(cmp_tail_ref)();
        //@ close_frac_borrow(tail_ref_frac, ref_initialized_(cmp_tail_ref));
        //@ close [sift_ref_frac]ref_initialized_::<T>(cmp_sift_ref)();
        //@ close_frac_borrow(sift_ref_frac, ref_initialized_(cmp_sift_ref));
        //@ merge_fractions lifetime_token(cmp_k);
        //@ assert [1/2]lifetime_token(cmp_k);
        //@ end_lifetime(cmp_k);
"""
RANGE_READ_ANCHOR = "        let tmp = ManuallyDrop::new(tail.read());"
RANGE_BODY_ANCHOR = (
    "    // SAFETY: see individual comments.\n"
    "    unsafe {\n"
    "        // SAFETY: in-bounds as tail > begin.\n"
)
RANGE_COMPARE_ANCHOR = "        if !is_less(&*tail, &*sift) {"
RANGE_COMPARE_CALL = "        if !is_less/*@::<F, (&'cmp T, &'cmp T), 'cmp>@*/(&*tail, &*sift) {"
HEADER = "use core::mem::ManuallyDrop;\nuse core::{intrinsics, ptr};\n\n"
ROOT = (
    "#![no_std]\n"
    "#![allow(dead_code)]\n"
    "#![feature(core_intrinsics)]\n"
    "mod smallsort;\n"
)


def unique_offset(text: str, marker: str) -> int:
    if text.count(marker) != 1:
        raise ValueError(f"expected one exact anchor, found {text.count(marker)}: {marker!r}")
    return text.index(marker)


def bounded_block(text: str, start: str, end: str) -> str:
    i, j = unique_offset(text, start), unique_offset(text, end)
    if i >= j:
        raise ValueError(f"reordered anchors: {start!r}, {end!r}")
    return text[i:j]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    if len(sys.argv) == 2:
        profile = "frontend"
    elif len(sys.argv) == 4 and sys.argv[2] == "--profile" and sys.argv[3] in GHOSTS:
        profile = sys.argv[3]
    else:
        raise SystemExit(
            "usage: extract-verifast-insertion.py OUTPUT_DIRECTORY "
            "[--profile frontend|range|tuple_overlay|tuple_parser|tuple_hrtb]"
        )
    ghost = GHOSTS[profile]
    source_bytes = SOURCE.read_bytes()
    source = source_bytes.decode("utf-8")
    pieces = {
        "copy_on_drop": bounded_block(source, "struct CopyOnDrop<T> {", "fn small_sort_network<T, F>"),
        "insert_tail": bounded_block(
            source, "/// Sorts range [begin, tail] assuming", "/// Sort `v` assuming"
        ),
        "insertion_sort_shift_left": bounded_block(
            source,
            "/// Sort `v` assuming",
            "/// SAFETY: The caller MUST guarantee that `v_base` is valid for 4 reads and",
        ),
    }
    copy = pieces["copy_on_drop"]
    if copy.count("struct CopyOnDrop<T> {") != 1 or copy.count("impl<T> Drop for CopyOnDrop<T> {") != 1:
        raise ValueError("CopyOnDrop blocks changed")
    if "fn small_sort_network" in copy or "fn insert_tail" in copy:
        raise ValueError("CopyOnDrop selection contains unrelated code")
    tail = pieces["insert_tail"]
    if tail.count(INSERT_SIGNATURE) != 1 or tail.count("let tmp = ManuallyDrop::new(tail.read());") != 1:
        raise ValueError("insert_tail signature or body anchor changed")
    outer = pieces["insertion_sort_shift_left"]
    if outer.count("pub fn insertion_sort_shift_left<T, F: FnMut(&T, &T) -> bool>(") != 1:
        raise ValueError("outer function signature changed")
    if outer.count("insert_tail(v_base, tail, is_less);") != 1:
        raise ValueError("outer function body changed")
    if tail.count(SIFT_ANCHOR) != 1:
        raise ValueError("first insert_tail pointer step changed")
    if tail.count(RANGE_BODY_ANCHOR) != 1 or tail.count(RANGE_COMPARE_ANCHOR) != 1:
        raise ValueError("first insert_tail comparison anchor changed")
    for name, piece in pieces.items():
        if not piece.rstrip().endswith("}"):
            raise ValueError(f"{name} does not end in a complete Rust item")
        if piece.count("{") != piece.count("}"):
            raise ValueError(f"{name} has unbalanced braces")

    # Piece bytes are exact substrings of the source. Scaffolding only supplies
    # equivalent core imports; no sorting operation is reimplemented here.
    original = HEADER + "".join(pieces.values())
    if original.count(RANGE_BODY_ANCHOR) != 1 or original.count(RANGE_COMPARE_ANCHOR) != 1:
        raise ValueError("assembled first-comparison anchors are not unique")
    verified = original.replace(INSERT_SIGNATURE, INSERT_SIGNATURE[:-1] + ghost + "{")
    original_root = ROOT
    verified_root = ROOT
    module_injections = {"contract": ghost}
    root_injections = {}
    if profile in ("range", "tuple_overlay", "tuple_parser", "tuple_hrtb"):
        module_injections["interior_lemma"] = RANGE_INTERIOR_LEMMA
        module_injections["interior_call"] = RANGE_BOUND_GHOST
        module_injections["lifetime_begin"] = RANGE_LIFETIME_BEGIN
        module_injections["lifetime_bind"] = RANGE_LIFETIME_BIND
        module_injections["comparison_prep"] = RANGE_COMPARE_PREP
        verified = verified.replace(HEADER, HEADER + RANGE_INTERIOR_LEMMA, 1)
        verified = verified.replace(SIFT_ANCHOR, RANGE_BOUND_GHOST + SIFT_ANCHOR)
        verified = verified.replace(
            RANGE_BODY_ANCHOR,
            RANGE_LIFETIME_BEGIN + RANGE_BODY_ANCHOR.replace(
                "    unsafe {\n", "    unsafe {\n" + RANGE_LIFETIME_BIND, 1
            ),
            1,
        )
        verified = verified.replace(
            RANGE_COMPARE_ANCHOR,
            RANGE_COMPARE_PREP + RANGE_COMPARE_CALL,
            1,
        )
        module_injections["comparison_call_types"] = "/*@::<F, (&'cmp T, &'cmp T), 'cmp>@*/"
        if profile == "tuple_hrtb":
            unique_offset(verified, RANGE_READ_ANCHOR)
            verified = verified.replace(RANGE_READ_ANCHOR, RANGE_COMPARE_RECOVER + RANGE_READ_ANCHOR, 1)
            module_injections["comparison_recover"] = RANGE_COMPARE_RECOVER
    for filename, candidate, reference, insertions in (
        ("lib.rs", verified_root, original_root, root_injections),
        ("smallsort.rs", verified, original, module_injections),
    ):
        stripped = candidate
        for name, content in insertions.items():
            if stripped.count(content) != 1:
                raise ValueError(f"expected exactly one {filename} {name} ghost insertion")
            stripped = stripped.replace(content, "", 1)
        if stripped != reference:
            raise ValueError(f"verified {filename} is not ghost-comments-only")

    out = Path(sys.argv[1])
    spans = out / "source-spans"
    spans.mkdir(parents=True, exist_ok=True)
    for name, piece in pieces.items():
        (spans / f"{name}.rs").write_bytes(piece.encode("utf-8"))
    for variant, root_body, module_body in (
        ("original", original_root, original),
        ("verified", verified_root, verified),
    ):
        directory = out / variant
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "lib.rs").write_text(root_body, encoding="utf-8")
        (directory / "smallsort.rs").write_text(module_body, encoding="utf-8")
    manifest = {
        "source": str(SOURCE),
        "source_sha256": sha256(source_bytes),
        "pieces": {
            name: {"sha256": sha256(piece.encode()), "bytes": len(piece.encode())}
            for name, piece in pieces.items()
        },
        "original_sha256": sha256(original.encode()),
        "verified_sha256": sha256(verified.encode()),
        "files": {
            "lib.rs": {
                "original_sha256": sha256(original_root.encode()),
                "verified_sha256": sha256(verified_root.encode()),
            },
            "smallsort.rs": {
                "original_sha256": sha256(original.encode()),
                "verified_sha256": sha256(verified.encode()),
            },
        },
        "ghost_comment_only": True,
        "profile": profile,
        "specified_function": "insert_tail",
        "expected_specified_target_bodies": 1,
        "contract": CONTRACTS[profile],
        "ghost_insertions": {
            filename: {
                name: {"sha256": sha256(content.encode()), "bytes": len(content.encode())}
                for name, content in insertions.items()
            }
            for filename, insertions in (
                ("lib.rs", root_injections),
                ("smallsort.rs", module_injections),
            )
        },
    }
    (out / "extraction.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    for name, info in manifest["pieces"].items():
        print(f"extracted {name}: {info['bytes']} bytes, sha256 {info['sha256']}")
    print(f"profile: {profile}; {CONTRACTS[profile]}")
    print("expected specified target bodies: 1 (insert_tail)")


if __name__ == "__main__":
    try:
        main()
    except (OSError, UnicodeError, ValueError) as error:
        raise SystemExit(f"source extraction failed closed: {error}") from error
