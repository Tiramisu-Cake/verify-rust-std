#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Exact-source actual pointer-specialized helper for hosted dependency capture.

No guard/forget redirect or semantic rule is installed. This fixture is not a
helper proof; its purpose is complete typed MIR/first-obligation evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
from pathlib import Path


HINT_SHA = "ce89716d46b8060db2c2da1aef1d4bcccf90e0804fc021d4470c55203501315f"
MAYBE_SHA = "1230d267542337ee2842c29d8227cf8a58fe75c53a2a70efaee3922c4e8e25c0"
SELECT_SIGNATURE = (
    b"pub const fn select_unpredictable<T>(condition: bool, true_val: T, false_val: T) -> T\n"
    b"where\n    T: [const] Destruct,\n{"
)
SELECT_TAIL = b"\n\n/// The expected temporal locality"
REQUIRED = (
    b"struct DropOnPanic<T> {",
    b"impl<T> Drop for DropOnPanic<T> {",
    b"unsafe { self.inner.drop_in_place() }",
    b"let guard = DropOnPanic { inner: guard };",
    b"drop.drop_in_place();",
    b"crate::mem::forget(guard);",
    b"crate::intrinsics::select_unpredictable(condition, true_val, false_val).assume_init()",
)


def require(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_a1():
    path = Path(__file__).with_name("prepare-assume-init-2610.py")
    spec = importlib.util.spec_from_file_location("overnight_assume_capture", path)
    require(spec is not None and spec.loader is not None,
            "A1 complete-MIR helper absent")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def extract_select(source: bytes) -> bytes:
    require(source.count(SELECT_SIGNATURE) == 1,
            "actual helper signature absent/ambiguous")
    opening = source.index(SELECT_SIGNATURE) + len(SELECT_SIGNATURE) - 1
    # The source is full-file pinned and the next-doc anchor pins the closing
    # boundary, avoiding assumptions about nested comment braces.
    tail = source.find(SELECT_TAIL, opening)
    require(tail > opening and source[tail - 1] == ord("}"),
            "actual helper closing anchor changed")
    body = source[opening:tail]
    require(body.startswith(b"{\n") and body.endswith(b"}"),
            "actual helper body boundary changed")
    return body


def strip_ghost(data: bytes) -> bytes:
    return re.sub(rb"/\*@.*?@\*/(?:\r?\n)?", b"", data, flags=re.S)


def source_certificate(repo: Path) -> tuple[bytes, dict]:
    hint = (repo / "library/core/src/hint.rs").read_bytes()
    maybe = (repo / "library/core/src/mem/maybe_uninit.rs").read_bytes()
    require(digest(hint) == HINT_SHA and digest(maybe) == MAYBE_SHA,
            "actual helper or MaybeUninit std source pin changed")
    body = extract_select(hint)
    for fragment in REQUIRED:
        require(body.count(fragment) == 1,
                f"actual helper operation absent/ambiguous: {fragment.decode()}")
    require(body.count(b"crate::intrinsics::select_unpredictable(") == 3 and
            body.count(b"MaybeUninit::new(") == 2 and
            body.count(b".as_mut_ptr()") == 2,
            "actual helper call inventory changed")
    return body, {
        "hint_sha256": HINT_SHA,
        "maybe_uninit_sha256": MAYBE_SHA,
        "exact_body_sha256": digest(body),
        "target_signature": SELECT_SIGNATURE.decode(),
        "target_specialization": "T = *const Element; Element unrestricted",
        "runtime_body_exact": True,
        "guard_and_drop_body_retained": True,
        "actual_forget_redirect": False,
        "actual_assume_init_redirect": False,
        "helper_proof_status": "NOT_RUN",
    }


def write_fixture(repo: Path, out: Path) -> dict:
    body, source = source_certificate(repo)
    prefix = (
        b"#![feature(core_intrinsics)]\n#![allow(internal_features)]\n\n"
        b"use std::mem::MaybeUninit;\nuse std::{intrinsics, mem};\n\n"
        b"pub fn select_unpredictable<Element>(\n"
        b"    condition: bool,\n    true_val: *const Element,\n"
        b"    false_val: *const Element,\n) -> *const Element\n"
    )
    contract = (
        b"/*@\nreq thread_token(?t) &*& t == currentThread;\n@*/\n"
        b"/*@\nens thread_token(t) &*& (result as pointer) ==\n"
        b"    (if condition { true_val as pointer } else { false_val as pointer });\n@*/\n"
        b"/*@\non_unwind_ens false;\n@*/\n"
    )
    verified = prefix + contract + body + b"\n"
    original = strip_ghost(verified)
    require(original.count(body) == verified.count(body) == 1 and
            original.count(b"crate::mem::forget(guard);") == 1,
            "actual source pair changed")
    require(not out.exists(), f"refusing to overwrite {out}")
    (out / "original").mkdir(parents=True)
    (out / "verified").mkdir()
    (out / "original/lib.rs").write_bytes(original)
    (out / "verified/lib.rs").write_bytes(verified)
    record = {"source_certificate": source,
              "original_sha256": digest(original),
              "verified_sha256": digest(verified),
              "ghost_strip_identity": strip_ghost(verified) == original,
              "capture_only": True}
    require(record["ghost_strip_identity"], "ghost stripping changed runtime body")
    (out / "fixture.json").write_text(json.dumps(record, indent=2,
                                                  sort_keys=True) + "\n")
    return record


def capture_mir(decoded_path: Path, out: Path) -> dict:
    a1 = load_a1()
    decoded = decoded_path.read_text(errors="strict")
    defpath, body = a1.complete_function_record(decoded, "select_unpredictable")
    require(defpath == "select_unpredictable" or
            defpath.endswith("::select_unpredictable"),
            "captured helper identity differs")
    require(not out.exists(), f"refusing to overwrite {out}")
    out.mkdir(parents=True)
    (out / "helper-full-mir.txt").write_text(body)
    record = {
        "classification": "UNREVIEWED_CAPTURE; NOT A HELPER CERTIFICATE",
        "helper_defpath": defpath,
        "helper_full_mir_sha256": digest(body.encode()),
        "helper_full_mir_bytes": len(body.encode()),
        "call_name_inventory": {name: body.count(name) for name in (
            "MaybeUninit", "select_unpredictable", "drop_in_place",
            "forget", "assume_init", "DropOnPanic")},
        "cleanup_edges_present": "cleanup =" in body,
        "guard_destructor_reachability_proved": False,
        "actual_forget_redirect": False,
        "helper_proof_status": "NOT_RUN",
    }
    (out / "capture.json").write_text(json.dumps(record, indent=2,
                                                sort_keys=True) + "\n")
    return record


def main() -> None:
    require(os.environ.get("GITHUB_ACTIONS") == "true" and
            os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted",
            "actual helper capture runs only on GitHub-hosted Actions")
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="mode", required=True)
    prepare = sub.add_parser("prepare")
    prepare.add_argument("--repo", type=Path, required=True)
    prepare.add_argument("--out", type=Path, required=True)
    capture = sub.add_parser("capture")
    capture.add_argument("--decoded-mir", type=Path, required=True)
    capture.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    record = (write_fixture(args.repo, args.out) if args.mode == "prepare" else
              capture_mir(args.decoded_mir, args.out))
    print(json.dumps(record, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
