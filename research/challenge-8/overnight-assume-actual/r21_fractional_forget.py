#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Inactive source-only fractional-owner candidate and negative controls.

This module transforms bytes only.  It does not prepare, extract, compile, or
verify the Rust source.  The caller remains responsible for binding its input
to the Cloud-established source fingerprint before using this transform.
"""
from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
PINNED_REPAIR_SHA256 = (
    "3646b05602b7dce35cd4b2ab8f74d8cfe280d65df2637ac4f6cc0a128dd7e2a3")
PINNED_CONTROLS_SHA256 = (
    "533c3d9be5249a40b2f0ad701cfaff6e95e688ecfb5b9c024c5dd2a56dc5124d")
BASELINE_SHA256_PREFIX = "1798132f"
VARIANTS = ("positive", "omit-selected-own", "omit-unselected-own",
            "no-retained-half", "callee-false-normal",
            "callee-owner-duplicate", "callee-owner-loss",
            "callee-thread-duplicate")


def _load_pinned(filename: str, name: str, expected: str):
    path = HERE / filename
    raw = path.read_bytes()
    _need(hashlib.sha256(raw).hexdigest() == expected,
          f"pinned transform source changed: {filename}")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"R21-FRACTIONAL-FORGET: cannot load {filename}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _need(ok: bool, why: str) -> None:
    if not ok:
        raise RuntimeError("R21-FRACTIONAL-FORGET: " + why)


# Exact owner-projection source anchor from prepare-actual-owner-projection.py.
CLOSE_OWNER_FULL = (
    b"        /*@ if (condition) {\n"
    b"                 close raw_ptr_own::<Element>()(t, true_payload);\n"
    b"                 close <select_unpredictable::DropOnPanic<*Element>>.own(t, select_unpredictable::DropOnPanic::<*Element> { inner: guard });\n"
    b"             } else {\n"
    b"                 close raw_ptr_own::<Element>()(t, false_payload);\n"
    b"                 close <select_unpredictable::DropOnPanic<*Element>>.own(t, select_unpredictable::DropOnPanic::<*Element> { inner: guard });\n"
    b"             } @*/\n")
CLOSE_OWNER_HALF = (
    b"        /*@ if (condition) {\n"
    b"                 close [1/2] raw_ptr_own::<Element>()(t, true_payload);\n"
    b"                 close [1/2] <select_unpredictable::DropOnPanic<*Element>>.own(t, select_unpredictable::DropOnPanic::<*Element> { inner: guard });\n"
    b"             } else {\n"
    b"                 close [1/2] raw_ptr_own::<Element>()(t, false_payload);\n"
    b"                 close [1/2] <select_unpredictable::DropOnPanic<*Element>>.own(t, select_unpredictable::DropOnPanic::<*Element> { inner: guard });\n"
    b"             } @*/\n")
SAVED_GUARD_FULL = (
    b"        /*@ assert <select_unpredictable::DropOnPanic<*Element>>.own(t, ?saved_guard); @*/\n")
SAVED_GUARD_HALF = (
    b"        /*@ assert [1/2] <select_unpredictable::DropOnPanic<*Element>>.own(t, ?saved_guard); @*/\n")
RETURNED_GUARD_FULL = (
    b"        /*@ open <select_unpredictable::DropOnPanic<*Element>>.own(t, saved_guard); @*/\n"
    b"        /*@ assert *saved_guard.inner |-> ?selected_payload; @*/\n"
    b"        /*@ open raw_ptr_own::<Element>()(t, selected_payload); @*/\n")
RETURNED_GUARD_HALF = (
    b"        /*@ { open [1/2] <select_unpredictable::DropOnPanic<*Element>>.own(t, saved_guard);\n"
    # R22: merge_fractions accepts only predicate/field points-to; in the Rust
    # dialect `*p |-> v` is the precise chunk points_to::<T>(p, v).
    b"             merge_fractions points_to::<*Element>(saved_guard.inner, _); } @*/\n"
    b"        /*@ assert *saved_guard.inner |-> ?selected_payload; @*/\n"
    b"        /*@ open [1/2] raw_ptr_own::<Element>()(t, selected_payload); @*/\n")

FORGET_SIGNATURE = b"pub unsafe fn checked_forget_owned<T>(t: T)\n"
FORGET_BODY = b"{\n    let _ = ManuallyDrop::new(t);\n}"
FORGET_OLD_CONTRACT = (
    b"/*@\nreq thread_token(?tid) &*& tid == currentThread &*& <T>.own(tid, t);\n@*/\n"
    b"/*@\nens thread_token(tid) &*& <T>.own(tid, t);\n@*/\n"
    b"/*@\non_unwind_ens false;\n@*/\n")
FORGET_HALF_CONTRACT = (
    b"/*@\nreq thread_token(?tid) &*& tid == currentThread &*& [1/2] <T>.own(tid, t);\n@*/\n"
    b"/*@\nens thread_token(tid) &*& [1/2] <T>.own(tid, t);\n@*/\n"
    b"/*@\non_unwind_ens false;\n@*/\n")
FORGET_FALSE_CONTRACT = FORGET_HALF_CONTRACT.replace(
    b"ens thread_token(tid) &*& [1/2] <T>.own(tid, t);",
    b"ens thread_token(tid) &*& [1/2] <T>.own(tid, t) &*& false;")
FORGET_DUPLICATE_OWNER_CONTRACT = FORGET_HALF_CONTRACT.replace(
    b"[1/2] <T>.own(tid, t);\n@*/\n/*@\non_unwind_ens",
    b"[1/2] <T>.own(tid, t) &*& [1/2] <T>.own(tid, t);\n@*/\n/*@\non_unwind_ens")
FORGET_OWNER_LOSS_CONTRACT = FORGET_HALF_CONTRACT.replace(
    b"ens thread_token(tid) &*& [1/2] <T>.own(tid, t);",
    b"ens thread_token(tid);")
FORGET_THREAD_DUPLICATE_CONTRACT = FORGET_HALF_CONTRACT.replace(
    b"ens thread_token(tid) &*& [1/2] <T>.own(tid, t);",
    b"ens thread_token(tid) &*& thread_token(tid) &*& [1/2] <T>.own(tid, t);")


def _replace_once(source: bytes, old: bytes, new: bytes, why: str) -> bytes:
    _need(source.count(old) == 1, f"one exact {why} anchor")
    return source.replace(old, new, 1)


def _fractional_positive(source: bytes) -> bytes:
    _need(isinstance(source, bytes), "source must be bytes")
    _need(source.count(FORGET_SIGNATURE) == 1 and source.count(FORGET_BODY) == 1,
          "one exact generic checked_forget_owned function")
    _need(source.count(FORGET_OLD_CONTRACT) == 1,
          "one original checked_forget_owned contract")
    out = _replace_once(source, CLOSE_OWNER_FULL, CLOSE_OWNER_HALF,
                        "full owner-close branch")
    out = _replace_once(out, SAVED_GUARD_FULL, SAVED_GUARD_HALF,
                        "saved full guard assertion")
    out = _replace_once(out, RETURNED_GUARD_FULL, RETURNED_GUARD_HALF,
                        "returned full guard open sequence")
    out = _replace_once(out, FORGET_OLD_CONTRACT, FORGET_HALF_CONTRACT,
                        "original forget contract")
    _need(out.count(CLOSE_OWNER_HALF) == 1 and
          out.count(SAVED_GUARD_HALF) == 1 and
          out.count(RETURNED_GUARD_HALF) == 1 and
          out.count(FORGET_HALF_CONTRACT) == 1,
          "fractional ownership edits are unique")
    return out


def _negative_from_positive(source: bytes, variant: str) -> bytes:
    if variant in ("omit-selected-own", "omit-unselected-own"):
        controls = _load_pinned("r21_final_select_controls.py",
                                "r21_fractional_pinned_controls",
                                PINNED_CONTROLS_SHA256)
        return controls.transform(source, variant)
    if variant == "no-retained-half":
        return _replace_once(source, CLOSE_OWNER_HALF, CLOSE_OWNER_FULL,
                             "fractional owner-close branch")
    contracts = {
        "callee-false-normal": FORGET_FALSE_CONTRACT,
        "callee-owner-duplicate": FORGET_DUPLICATE_OWNER_CONTRACT,
        "callee-owner-loss": FORGET_OWNER_LOSS_CONTRACT,
        "callee-thread-duplicate": FORGET_THREAD_DUPLICATE_CONTRACT,
    }
    if variant in contracts:
        return _replace_once(source, FORGET_HALF_CONTRACT, contracts[variant],
                             "fractional forget contract")
    _need(False, "unknown control variant")
    raise AssertionError("unreachable")


def transform(verified: bytes, variant: str = "positive") -> bytes:
    """Return one reversible ghost-only candidate/control source.

    `verified` is the source after the owner-projection insertion stage, before
    the R20 branch-selected final-select repair.  Production callers must
    independently enforce the complete Cloud source fingerprint; the short
    baseline prefix here documents that required upstream identity.
    """
    _need(variant in VARIANTS, "unknown variant")
    _need(isinstance(verified, bytes), "source must be bytes")
    repair = _load_pinned("r20_final_select_repair.py",
                          "r21_fractional_pinned_repair",
                          PINNED_REPAIR_SHA256)
    fractional = _fractional_positive(verified)
    positive = repair.repair(fractional, "branch-selected")
    _need(positive.replace(repair.SELECTED_BRANCH_BLOCK,
                           repair.SELECTED_BLOCK, 1) == fractional,
          "branch-selected repair changed bytes beyond its exact ghost block")
    if variant == "positive":
        return positive
    return _negative_from_positive(positive, variant)
