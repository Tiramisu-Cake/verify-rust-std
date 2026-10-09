#!/usr/bin/env python3
"""Prepare exact-source CopyOnDrop callee cases for hosted VeriFast stages."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


SOURCE_SHA256 = "85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1"
SOURCE_GIT_BLOB = "40939f922bcb6fdc7ee0d30427fa861827043827"
BLOCK_SHA256 = "caff1edbfa3a8d9fd29459e49c43abd0f8f987f9061c75e7bf6ecedbbba26a6a"
BLOCK_BYTES = 364
BLOCK_START = b"struct CopyOnDrop<T> {\n"
BLOCK_END = b"}\n\nfn small_sort_network"
DROP_SIGNATURE = b"    fn drop(&mut self)"
COPY_CALL = b"            ptr::copy_nonoverlapping(self.src, self.dst, self.len);"
TARGET = "<CopyOnDrop<T> as core::ops::Drop>::drop"
CRATE_PREFIX = b"#![no_std]\nuse core::ptr;\n\n"
FALSE_LINE = b"        //@ assert false; // TARGET: matched first-body entry control\n"

# Keep the source contract identical to the accepted extractor, adding only
# explicit nonempty-object, span, alignment, overflow, and guard separation facts.
CONTRACT = b"""/*@
req thread_token(?t) &*& t == currentThread &*& type_interp::<T>() &*&
    (*self).src |-> ?src &*& (*self).dst |-> ?dst &*& (*self).len |-> ?len &*&
    struct_CopyOnDrop_padding(self) &*&
    0 <= len &*& len <= usize::MAX &*&
    0 < std::mem::size_of::<T>() &*&
    std::mem::size_of::<T>() <= isize::MAX &*&
    len * std::mem::size_of::<T>() <= isize::MAX &*&
    0 < std::mem::size_of::<CopyOnDrop<T>>() &*&
    0 < std::mem::align_of::<CopyOnDrop<T>>() &*&
    self as usize != 0 &*&
    self as usize % std::mem::align_of::<CopyOnDrop<T>>() == 0 &*&
    object_pointer_within_limits(self, std::mem::size_of::<CopyOnDrop<T>>()) == true &*&
    self as usize <= usize::MAX - std::mem::size_of::<CopyOnDrop<T>>() &*&
    src as usize != 0 &*& dst as usize != 0 &*&
    src as usize % std::mem::align_of::<T>() == 0 &*&
    dst as usize % std::mem::align_of::<T>() == 0 &*&
    object_pointer_within_limits(src, len * std::mem::size_of::<T>()) == true &*&
    object_pointer_within_limits(dst, len * std::mem::size_of::<T>()) == true &*&
    src as usize <= usize::MAX - len * std::mem::size_of::<T>() &*&
    dst as usize <= usize::MAX - len * std::mem::size_of::<T>() &*&
    pointer_within_limits(src) == true &*& pointer_within_limits(src + len) == true &*&
    pointer_within_limits(dst) == true &*& pointer_within_limits(dst + len) == true &*&
    (len == 0 ||
        src as usize + len * std::mem::size_of::<T>() <= dst as usize ||
        dst as usize + len * std::mem::size_of::<T>() <= src as usize) &*&
    (len == 0 ||
        self as usize + std::mem::size_of::<CopyOnDrop<T>>() <= src as usize ||
        src as usize + len * std::mem::size_of::<T>() <= self as usize) &*&
    (len == 0 ||
        self as usize + std::mem::size_of::<CopyOnDrop<T>>() <= dst as usize ||
        dst as usize + len * std::mem::size_of::<T>() <= self as usize) &*&
    [?f]src[..len] |-> ?src_values &*& dst[..len] |-> _ &*&
    foreach(src_values, own::<T>(t));
@*//*@
ens thread_token(t) &*& type_interp::<T>() &*&
    (*self).src |-> src &*& (*self).dst |-> dst &*& (*self).len |-> len &*&
    struct_CopyOnDrop_padding(self) &*&
    0 <= len &*& len <= usize::MAX &*&
    0 < std::mem::size_of::<T>() &*&
    std::mem::size_of::<T>() <= isize::MAX &*&
    len * std::mem::size_of::<T>() <= isize::MAX &*&
    0 < std::mem::size_of::<CopyOnDrop<T>>() &*&
    0 < std::mem::align_of::<CopyOnDrop<T>>() &*&
    self as usize != 0 &*&
    self as usize % std::mem::align_of::<CopyOnDrop<T>>() == 0 &*&
    object_pointer_within_limits(self, std::mem::size_of::<CopyOnDrop<T>>()) == true &*&
    self as usize <= usize::MAX - std::mem::size_of::<CopyOnDrop<T>>() &*&
    src as usize != 0 &*& dst as usize != 0 &*&
    src as usize % std::mem::align_of::<T>() == 0 &*&
    dst as usize % std::mem::align_of::<T>() == 0 &*&
    object_pointer_within_limits(src, len * std::mem::size_of::<T>()) == true &*&
    object_pointer_within_limits(dst, len * std::mem::size_of::<T>()) == true &*&
    src as usize <= usize::MAX - len * std::mem::size_of::<T>() &*&
    dst as usize <= usize::MAX - len * std::mem::size_of::<T>() &*&
    pointer_within_limits(src) == true &*& pointer_within_limits(src + len) == true &*&
    pointer_within_limits(dst) == true &*& pointer_within_limits(dst + len) == true &*&
    (len == 0 ||
        src as usize + len * std::mem::size_of::<T>() <= dst as usize ||
        dst as usize + len * std::mem::size_of::<T>() <= src as usize) &*&
    (len == 0 ||
        self as usize + std::mem::size_of::<CopyOnDrop<T>>() <= src as usize ||
        src as usize + len * std::mem::size_of::<T>() <= self as usize) &*&
    (len == 0 ||
        self as usize + std::mem::size_of::<CopyOnDrop<T>>() <= dst as usize ||
        dst as usize + len * std::mem::size_of::<T>() <= self as usize) &*&
    [f]src[..len] |-> src_values &*& dst[..len] |-> src_values &*&
    foreach(src_values, own::<T>(t));
@*//*@ on_unwind_ens false; @*//*@
safety_proof {
    open CopyOnDrop_full_borrow_content::<T>(_t, self)();
    open <CopyOnDrop<T>>.own(_t, *self);
}
@*/"""


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode()
    return hashlib.sha1(header + data).hexdigest()


def extract(source: Path, output: Path, report_path: Path) -> dict:
    source_data = source.read_bytes()
    source_sha = sha(source_data)
    if source_sha != SOURCE_SHA256:
        raise ValueError(f"SmallSort source SHA-256 mismatch: {source_sha}")
    if git_blob(source_data) != SOURCE_GIT_BLOB:
        raise ValueError("SmallSort source Git blob mismatch")
    if source_data.count(BLOCK_START) != 1 or source_data.count(BLOCK_END) != 1:
        raise ValueError("CopyOnDrop source anchors are not unique")
    start = source_data.index(BLOCK_START)
    end = source_data.index(BLOCK_END, start) + len(b"}\n\n")
    block = source_data[start:end]
    if len(block) != BLOCK_BYTES or sha(block) != BLOCK_SHA256:
        raise ValueError("exact CopyOnDrop source block changed")
    if block.count(DROP_SIGNATURE) != 1 or block.count(COPY_CALL) != 1:
        raise ValueError("Drop signature or dynamic copy call is not unique")
    if b"self.len" not in COPY_CALL:
        raise ValueError("copy call lost its dynamic self.len argument")
    original = CRATE_PREFIX + block
    verified = original.replace(DROP_SIGNATURE, DROP_SIGNATURE + CONTRACT, 1)
    if verified.count(CONTRACT) != 1 or verified.replace(CONTRACT, b"") != original:
        raise ValueError("positive verified source differs beyond ghost contract")
    # The negative control adds one ghost assertion at the first method-body
    # statement; its runtime source strips exactly back to the same original.
    original_drop = original.index(DROP_SIGNATURE)
    original_open_brace = original.index(b"{", original_drop + len(DROP_SIGNATURE))
    # Translate the original method-body location across the inserted contract;
    # never scan verified bytes for the next brace, since safety_proof has one.
    method_body_offset = original_open_brace + len(CONTRACT)
    if verified[method_body_offset] != ord("{"):
        raise ValueError("contract insertion no longer maps to the actual Drop body")
    line_end = verified.index(b"\n", method_body_offset) + 1
    negative = verified[:line_end] + FALSE_LINE + verified[line_end:]
    if negative.replace(FALSE_LINE, b"").replace(CONTRACT, b"") != original:
        raise ValueError("negative control changes runtime source beyond ghost assertion")
    false_token_offset = FALSE_LINE.index(b"false")
    negative_line = negative[:negative.index(FALSE_LINE) + false_token_offset].count(b"\n") + 1
    negative_column_start = false_token_offset + 1
    negative_column_end = negative_column_start + len(b"false")
    if negative_line < 1:
        raise ValueError("invalid source target coordinates")
    if output.exists() or report_path.exists():
        raise FileExistsError("refusing to reuse Drop preparation paths")
    cases = {}
    for name, verified_bytes in (("positive", verified), ("first_body_false", negative)):
        case = output / name
        (case / "original").mkdir(parents=True)
        (case / "verified").mkdir()
        (case / "original/lib.rs").write_bytes(original)
        (case / "verified/lib.rs").write_bytes(verified_bytes)
        copy_call_line = verified_bytes[:verified_bytes.index(COPY_CALL)].count(b"\n") + 1
        cases[name] = {
            "original_sha256": sha(original),
            "verified_sha256": sha(verified_bytes),
            "copy_call_line": copy_call_line,
            "expected_target_name": TARGET,
            "runtime_source_identical_after_ghost_strip": True,
        }
        if name == "first_body_false":
            cases[name].update({"negative_target_line": negative_line,
                                "negative_column_start": negative_column_start,
                                "negative_column_end": negative_column_end,
                                "negative_predicate": "false"})
    report = {
        "selection": "copy_on_drop_actual_count_n_diagnostic",
        "source_sha256": source_sha,
        "source_git_blob": SOURCE_GIT_BLOB,
        "block_offset": start,
        "block_bytes": len(block),
        "block_sha256": sha(block),
        "contract_sha256": sha(CONTRACT),
        "target": TARGET,
        "dynamic_copy_call": COPY_CALL.decode().strip(),
        "copy_call_uses_self_len": True,
        "guard_span_disjointness_rationale": "prevents destination writes from aliasing Drop guard fields; same-allocation disjoint ranges remain allowed",
        "guard_safe_drop_compatibility": "historically observed as private own=false and vacuous; this run must separately record the generated compatibility path before making that claim",
        "partial_diagnostic": True,
        "cases": cases,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    extract(args.source, args.output, args.report)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        raise SystemExit(f"CopyOnDrop source preparation refused: {error}")
