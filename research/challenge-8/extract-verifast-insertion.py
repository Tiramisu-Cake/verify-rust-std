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
GHOST = "/*@\nreq true;\nens true;\n@*/ "
INSERT_SIGNATURE = (
    "unsafe fn insert_tail<T, F: FnMut(&T, &T) -> bool>"
    "(begin: *mut T, tail: *mut T, is_less: &mut F) {"
)
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
    if len(sys.argv) != 2:
        raise SystemExit("usage: extract-verifast-insertion.py OUTPUT_DIRECTORY")
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
    for name, piece in pieces.items():
        if not piece.rstrip().endswith("}"):
            raise ValueError(f"{name} does not end in a complete Rust item")
        if piece.count("{") != piece.count("}"):
            raise ValueError(f"{name} has unbalanced braces")

    # Piece bytes are exact substrings of the source. Scaffolding only supplies
    # equivalent core imports; no sorting operation is reimplemented here.
    original = HEADER + "".join(pieces.values())
    verified = original.replace(INSERT_SIGNATURE, INSERT_SIGNATURE[:-1] + GHOST + "{")
    if verified.count(GHOST) != 1 or verified.replace(GHOST, "") != original:
        raise ValueError("verified copy is not ghost-comments-only")

    out = Path(sys.argv[1])
    spans = out / "source-spans"
    spans.mkdir(parents=True, exist_ok=True)
    for name, piece in pieces.items():
        (spans / f"{name}.rs").write_bytes(piece.encode("utf-8"))
    for variant, body in (("original", original), ("verified", verified)):
        directory = out / variant
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "lib.rs").write_text(ROOT, encoding="utf-8")
        (directory / "smallsort.rs").write_text(body, encoding="utf-8")
    manifest = {
        "source": str(SOURCE),
        "source_sha256": sha256(source_bytes),
        "pieces": {
            name: {"sha256": sha256(piece.encode()), "bytes": len(piece.encode())}
            for name, piece in pieces.items()
        },
        "original_sha256": sha256(original.encode()),
        "verified_sha256": sha256(verified.encode()),
        "ghost_comment_only": True,
        "specified_function": "insert_tail",
        "expected_specified_target_bodies": 1,
        "contract": "req true; ens true; (no ownership or functional claim)",
    }
    (out / "extraction.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    for name, info in manifest["pieces"].items():
        print(f"extracted {name}: {info['bytes']} bytes, sha256 {info['sha256']}")
    print("expected specified target bodies: 1 (insert_tail)")


if __name__ == "__main__":
    try:
        main()
    except (OSError, UnicodeError, ValueError) as error:
        raise SystemExit(f"source extraction failed closed: {error}") from error
