#!/usr/bin/env python3
"""Prepare source-pinned one-cell insert_tail guard diagnostics; no tools run here."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
SOURCE = ROOT / "library/core/src/slice/sort/shared/smallsort.rs"
SOURCE_SHA = "85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1"
SOURCE_BLOB = "40939f922bcb6fdc7ee0d30427fa861827043827"
PROFILE = "insert-tail-onecell-mutable-fbc-held-recovery-v1"
READ = b"        let tmp = ManuallyDrop::new(tail.read());\n"
GUARD = b"        let mut gap_guard = CopyOnDrop { src: &*tmp, dst: tail, len: 1 };\n"
COPY = b"        ptr::copy_nonoverlapping(gap_guard.src, gap_guard.dst, 1);\n"
FBC_CLOSE = b"        //@ close CopyOnDrop_full_borrow_content::<T>(t, &gap_guard)();\n"
FBC_OPEN = b"        //@ open CopyOnDrop_full_borrow_content::<T>(t, &gap_guard)();\n"
OWN_CLOSE = b"        //@ close <CopyOnDrop<T>>.own(t, gap_guard);\n"
OWN_OPEN = b"        //@ open <CopyOnDrop<T>>.own(t, gap_guard);\n"
MISSING_OWNER_CLOSE = b"        //@ close <CopyOnDrop<T>>.own(t, gap_guard); // TARGET: missing held owner\n"
DOUBLE_FBC_CLOSE = b"        //@ close CopyOnDrop_full_borrow_content::<T>(t, &gap_guard)(); // TARGET: duplicate physical FBC\n"
FALSE = b"        //@ assert false; // TARGET: after one-cell recovery\n"
FBC_FALSE = b"        //@ assert false; // TARGET: after mutable canonical FBC open\n"
SOURCE_LIMITS = b"        //@ points_to_limits::<T>(gap_guard.src as *mut T);\n"

OWN = b"""/*@
pred<T> <CopyOnDrop<T>>.own(t, v) =
    type_interp::<T>() &*& v.len == 1 &*&
    [?f](*v.src |-> ?current) &*& *v.dst |-?-> ?old_gap &*&
    <T>.own(t, current);
@*/

"""

ALIGNMENT_LEMMA = b"""/*@
lem initialized_storage_alignment<T>(p: *T)
    req [?f](*p |-> ?v);
    ens [f](*p |-> v) &*& p as usize % std::mem::align_of::<T>() == 0;
{
    open [f]points_to::<T>(p, v);
    to_u8s_::<T>(p);
    from_u8s_::<T>(p);
    close [f]points_to::<T>(p, v);
}
@*/

"""
ALIGNMENT = b"        //@ initialized_storage_alignment::<T>(gap_guard.src as *mut T);\n"
SOURCE_IDENTITY = b"        //@ assert gap_guard.src == held_ref;\n"

CONTRACT = b"""/*@
req thread_token(?t) &*& t == currentThread &*& type_interp::<T>() &*&
    0 < std::mem::size_of::<T>() &*&
    std::mem::size_of::<T>() <= isize::MAX &*&
    tail as usize != 0 &*&
    tail as usize % std::mem::align_of::<T>() == 0 &*&
    object_pointer_within_limits(tail, std::mem::size_of::<T>()) == true &*&
    tail as usize <= usize::MAX - std::mem::size_of::<T>() &*&
    *tail |-> ?held &*& <T>.own(t, held);
@*//*@
ens thread_token(t) &*& type_interp::<T>() &*&
    *tail |-> held &*& <T>.own(t, held);
@*//*@
on_unwind_ens thread_token(t) &*& type_interp::<T>() &*&
    *tail |-> ?unwound &*& <T>.own(t, unwound);
@*/"""

PREFIX = b"#![no_std]\nuse core::{mem::ManuallyDrop, ptr};\n\n"
FN = (b"unsafe fn insertion_onecell<T>(tail: *mut T)" + CONTRACT + b" {\n"
      b"    unsafe {\n" + READ + GUARD + COPY + b"    }\n}\n")
ANNOTATIONS = (
    b"        //@ let held_k = begin_lifetime();\n"
    b"        //@ let held_ref = precreate_ref(&tmp);\n"
    b"        //@ merge_fractions lifetime_token(held_k);\n"
    b"        //@ init_ref_readonly(held_ref, 1/2);\n"
)
RECOVER = (
    b"        //@ end_ref_readonly(held_ref);\n"
    b"        //@ merge_fractions points_to::<T>(&tmp, _);\n"
    b"        //@ end_lifetime(held_k);\n"
    b"        //@ assert *tail |-> held &*& <T>.own(t, held);\n"
)
GEOMETRY = (
    b"        //@ assert gap_guard.src as usize != 0;\n",
    b"        //@ assert gap_guard.src as usize % std::mem::align_of::<T>() == 0;\n",
    b"        //@ assert object_pointer_within_limits(gap_guard.src, std::mem::size_of::<T>()) == true;\n",
    b"        //@ assert gap_guard.src as usize <= usize::MAX - std::mem::size_of::<T>();\n",
    b"        //@ assert (gap_guard.src as usize + std::mem::size_of::<T>() <= gap_guard.dst as usize || gap_guard.dst as usize + std::mem::size_of::<T>() <= gap_guard.src as usize);\n"
)
GEOMETRY_LABELS = ("source_nonnull", "source_alignment", "source_object_limits",
                   "source_address_no_overflow", "source_destination_disjoint")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def blob(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def line(data: bytes, needle: bytes) -> int:
    if data.count(needle) != 1:
        raise ValueError(f"expected one occurrence: {needle!r}")
    return data[:data.index(needle)].count(b"\n") + 1


def extract(output: Path, report: Path, source: Path = SOURCE) -> dict:
    raw = source.read_bytes()
    if sha(raw) != SOURCE_SHA or blob(raw) != SOURCE_BLOB:
        raise ValueError("SmallSort source identity changed")
    if raw.count(READ) != 1 or raw.count(GUARD) != 1 or \
            raw.index(GUARD) != raw.index(READ) + len(READ) or \
            line(raw, READ) != 550 or line(raw, GUARD) != 551:
        raise ValueError("actual insert_tail read/guard adjacency changed")
    spec = importlib.util.spec_from_file_location(
        "onecell_direct_drop_source", HERE.parents[1] / "copy-on-drop-prepare.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("direct Drop source pin unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if raw.count(module.BLOCK_START) != 1 or raw.count(module.BLOCK_END) != 1:
        raise ValueError("actual CopyOnDrop block anchors changed")
    start = raw.index(module.BLOCK_START)
    end = raw.index(module.BLOCK_END, start) + len(b"}\n\n")
    block = raw[start:end]
    if len(block) != module.BLOCK_BYTES or sha(block) != module.BLOCK_SHA256 or \
            block.count(module.COPY_CALL) != 1:
        raise ValueError("actual CopyOnDrop/Drop block changed")
    struct = block.split(b"}\n\nimpl<T> Drop", 1)[0] + b"}\n\n"
    if b"impl<T> Drop" in struct or struct.count(b"struct CopyOnDrop<T>") != 1:
        raise ValueError("isolated struct shape differs")
    original = PREFIX + struct + FN.replace(CONTRACT, b"", 1)
    if output.exists() or report.exists():
        raise FileExistsError("refusing to reuse one-cell evidence")
    rows = {}
    for name in ("positive", "after_fbc_false", "after_recovery_false", "missing_held_owner",
                 "double_physical_fbc"):
        case_contract = (CONTRACT.replace(
            b"*tail |-> ?held &*& <T>.own(t, held);", b"*tail |-> ?held;", 1)
            if name == "missing_held_owner" else CONTRACT)
        if name == "missing_held_owner" and case_contract == CONTRACT:
            raise ValueError("missing-owner negative did not remove supplied owner")
        verified = PREFIX + struct + OWN + ALIGNMENT_LEMMA + FN.replace(CONTRACT, case_contract, 1)
        # The exact runtime read and initializer remain adjacent after ghost strip.
        verified = verified.replace(READ, READ + ANNOTATIONS, 1)
        close = MISSING_OWNER_CLOSE if name == "missing_held_owner" else OWN_CLOSE
        middle = close + FBC_CLOSE
        if name == "double_physical_fbc":
            middle += DOUBLE_FBC_CLOSE
        middle += FBC_OPEN + OWN_OPEN
        if name == "after_fbc_false":
            middle += FBC_FALSE
        middle += SOURCE_IDENTITY + ALIGNMENT + SOURCE_LIMITS + b"".join(GEOMETRY)
        verified = verified.replace(GUARD, GUARD + middle, 1)
        verified = verified.replace(COPY, COPY + RECOVER +
                                    (FALSE if name == "after_recovery_false" else b""), 1)
        stripped = verified.replace(OWN, b"", 1).replace(ALIGNMENT_LEMMA, b"", 1).replace(case_contract, b"", 1)
        for ghost in (ANNOTATIONS, middle, RECOVER, FALSE):
            stripped = stripped.replace(ghost, b"", 1)
        if stripped != original:
            raise ValueError(f"{name}: runtime bytes differ after ghost strip")
        case = output / name
        (case / "original").mkdir(parents=True)
        (case / "verified").mkdir()
        (case / "original/lib.rs").write_bytes(original)
        (case / "verified/lib.rs").write_bytes(verified)
        target = (FBC_FALSE if name == "after_fbc_false" else
                  FALSE if name == "after_recovery_false" else
                  READ if name == "missing_held_owner" else
                  DOUBLE_FBC_CLOSE if name == "double_physical_fbc" else None)
        rows[name] = {
            "original_sha256": sha(original), "verified_sha256": sha(verified),
            "case_contract_sha256": sha(case_contract),
            "source_read_line": 550, "source_guard_line": 551,
            "read_line": line(verified, READ), "guard_line": line(verified, GUARD),
            "copy_line": line(verified, COPY),
            "fbc_close_line": line(verified, FBC_CLOSE),
            "fbc_open_line": line(verified, FBC_OPEN),
            "source_limits_line": line(verified, SOURCE_LIMITS),
            "alignment_lemma_line": line(verified, ALIGNMENT),
            "source_identity_line": line(verified, SOURCE_IDENTITY),
            "own_close_line": line(verified, close),
            "geometry_lines": [line(verified, item) for item in GEOMETRY],
            "geometry_labels": list(GEOMETRY_LABELS),
            "target": None if target is None else {
                "line": line(verified, target), "column_start": target.index(
                    b"false" if target in (FALSE, FBC_FALSE) else b"tail.read" if target == READ
                    else b"close") + 1,
                "predicate": "false" if target in (FALSE, FBC_FALSE) else
                "held owner" if target == READ else "physical FBC"},
            "runtime_ghost_strip_equal": True,
        }
    result = {
        "profile": PROFILE, "source_sha256": sha(raw), "source_git_blob": blob(raw),
        "source_block_sha256": sha(block), "source_struct_sha256": sha(struct),
        "actual_drop_copy_sha256": sha(module.COPY_CALL),
        "source_read_sha256": sha(READ), "source_guard_sha256": sha(GUARD),
        "own_sha256": sha(OWN), "contract_sha256": sha(CONTRACT),
        "recovery_sha256": sha(RECOVER), "no_drop_impl_in_fragment": True,
        "source_limits_sha256": sha(SOURCE_LIMITS),
        "alignment_lemma_sha256": sha(ALIGNMENT_LEMMA),
        "alignment_call_sha256": sha(ALIGNMENT),
        "geometry_assertions_sha256": [sha(item) for item in GEOMETRY],
        "supplied_entry_resources": True, "accepted": False, "cases": rows,
    }
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    extract(args.output, args.report, args.source)
