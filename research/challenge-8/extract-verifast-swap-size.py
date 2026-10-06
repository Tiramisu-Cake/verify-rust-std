#!/usr/bin/env python3
"""Extract the live generic SmallSort size heuristic for an Actions proof."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


SOURCE = Path("library/core/src/slice/sort/shared/smallsort.rs")
TARGET_START = "#[must_use]\npub(crate) const fn has_efficient_in_place_swap<T>() -> bool {"
TARGET_END = "    size_of::<T>() <= 8 // size_of::<u64>()\n}"
SPEC = "/*@ req true; @*/ /*@ ens result == (std::mem::size_of::<T>() <= 8); @*/ "
ROOT = "#![no_std]\n#![allow(dead_code)]\nmod smallsort;\n"
HEADER = "use core::mem::size_of;\n\n"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def unique_offset(text: str, marker: str) -> int:
    count = text.count(marker)
    if count != 1:
        raise ValueError(f"expected one exact source anchor, found {count}: {marker!r}")
    return text.index(marker)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: extract-verifast-swap-size.py OUTPUT_DIRECTORY")

    source_bytes = SOURCE.read_bytes()
    source = source_bytes.decode("utf-8")
    start = unique_offset(source, TARGET_START)
    end_start = unique_offset(source, TARGET_END)
    end = end_start + len(TARGET_END)
    if end_start < start:
        raise ValueError("target body end precedes its unique start")
    if source[end:].strip():
        raise ValueError("target is no longer the final source item; extraction boundary needs review")

    target = source[start:end]
    if target.count("has_efficient_in_place_swap<T>() -> bool") != 1:
        raise ValueError("generic helper signature changed")
    if target.count("size_of::<T>() <= 8 // size_of::<u64>()") != 1:
        raise ValueError("size threshold expression changed")
    if target.count("{") != target.count("}"):
        raise ValueError("target body is not a complete balanced item")

    original = HEADER + target + "\n"
    signature = "pub(crate) const fn has_efficient_in_place_swap<T>() -> bool {"
    if original.count(signature) != 1:
        raise ValueError("assembled target signature is not unique")
    verified = original.replace(signature, signature[:-1] + SPEC + "{", 1)
    if verified.count(SPEC) != 1:
        raise ValueError("expected exactly one result-equivalence contract")
    stripped = verified.replace(SPEC, "", 1)
    if stripped != original:
        raise ValueError("verified source differs from original beyond the ghost contract")

    out = Path(sys.argv[1])
    (out / "source-spans").mkdir(parents=True, exist_ok=True)
    (out / "source-spans/has_efficient_in_place_swap.rs").write_bytes(target.encode())
    for variant, body in (("original", original), ("verified", verified)):
        directory = out / variant
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "lib.rs").write_text(ROOT, encoding="utf-8")
        (directory / "smallsort.rs").write_text(body, encoding="utf-8")

    manifest = {
        "source": str(SOURCE),
        "source_sha256": sha256(source_bytes),
        "source_span_sha256": sha256(target.encode()),
        "source_span_bytes": len(target.encode()),
        "original_sha256": sha256(original.encode()),
        "verified_sha256": sha256(verified.encode()),
        "ghost_contract": SPEC,
        "ghost_comment_only": True,
        "specified_function": "has_efficient_in_place_swap<T>",
        "expected_specified_target_bodies": 1,
        "contract": "req true; ens result == (std::mem::size_of::<T>() <= 8); generic T unrestricted",
        "target_statement_lines": [6, 7],
    }
    (out / "extraction.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"extracted has_efficient_in_place_swap<T>: {len(target.encode())} bytes, sha256 {manifest['source_span_sha256']}")
    print("expected specified target bodies: 1")


if __name__ == "__main__":
    try:
        main()
    except (OSError, UnicodeError, ValueError) as error:
        raise SystemExit(f"source extraction failed closed: {error}") from error
