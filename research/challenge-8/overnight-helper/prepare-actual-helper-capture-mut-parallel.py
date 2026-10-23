#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Independent source-only `T = *mut Element` actual-helper fixture writer.

Unlike the earlier signature-swap writer, this path extracts the pinned std
body directly and never imports or invokes the const fixture writer. It is
still only source preparation: no Rust tools, MIR binding, translator
admission, proof, or publication.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
from pathlib import Path
import sys


HINT_SHA256 = "ce89716d46b8060db2c2da1aef1d4bcccf90e0804fc021d4470c55203501315f"
MAYBE_SHA256 = "1230d267542337ee2842c29d8227cf8a58fe75c53a2a70efaee3922c4e8e25c0"
CONTRACT_SHA256 = "dc985de2e2a0e1a95e6c12c4b9cb78c4042d9d45f949d78904a999e82262b870"
PROVIDER_ADAPTER_SHA256 = "04fd1ca82bdbfb7f837a49ed303199024208c85124cf1a45b7893f6d20ed1871"
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
MUT_SIGNATURE = (
    b"pub fn select_unpredictable<Element>(\n"
    b"    condition: bool,\n    true_val: *mut Element,\n"
    b"    false_val: *mut Element,\n) -> *mut Element\n"
)
CONTRACT = (
    b"/*@\nreq thread_token(?t) &*& t == currentThread;\n@*/\n"
    b"/*@\nens thread_token(t) &*& (result as pointer) ==\n"
    b"    (if condition { true_val as pointer } else { false_val as pointer });\n@*/\n"
    b"/*@\non_unwind_ens false;\n@*/\n"
)
PREFIX = (
    b"#![feature(core_intrinsics)]\n#![allow(internal_features)]\n\n"
    b"use std::mem::MaybeUninit;\nuse std::{intrinsics, mem};\n\n"
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)


def require_cloud_provider() -> dict:
    path = Path(__file__).with_name("mut_source_cloud_provider.py")
    raw = path.read_bytes()
    require(sha(raw) == PROVIDER_ADAPTER_SHA256,
            "pinned mutable Cloud provider adapter changed")
    spec = importlib.util.spec_from_file_location("p2_mut_cloud_provider", path)
    require(spec is not None and spec.loader is not None,
            "mutable Cloud provider adapter unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.require_cloud_provider()


def extract_select(source: bytes) -> bytes:
    require(source.count(SELECT_SIGNATURE) == 1,
            "actual std helper signature absent/ambiguous")
    opening = source.index(SELECT_SIGNATURE) + len(SELECT_SIGNATURE) - 1
    tail = source.find(SELECT_TAIL, opening)
    require(tail > opening and source[tail - 1] == ord("}"),
            "actual std helper closing anchor changed")
    body = source[opening:tail]
    require(body.startswith(b"{\n") and body.endswith(b"}"),
            "actual std helper body boundary changed")
    return body


def strip_ghost(source: bytes) -> bytes:
    return re.sub(rb"/\*@.*?@\*/(?:\r?\n)?", b"", source, flags=re.S)


def source_certificate(repo: Path) -> tuple[bytes, dict]:
    provider = require_cloud_provider()
    hint = (repo / "library/core/src/hint.rs").read_bytes()
    maybe = (repo / "library/core/src/mem/maybe_uninit.rs").read_bytes()
    require(sha(hint) == HINT_SHA256 and sha(maybe) == MAYBE_SHA256,
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
        "hint_sha256": HINT_SHA256,
        "maybe_uninit_sha256": MAYBE_SHA256,
        "exact_body_sha256": sha(body),
        "target_signature": SELECT_SIGNATURE.decode(),
        "target_specialization": "T = *mut Element; Element unrestricted",
        "runtime_body_exact": True,
        "guard_and_drop_body_retained": True,
        "actual_forget_redirect": False,
        "actual_assume_init_redirect": False,
        "fixture_writer_is_const_independent": True,
        "provider": provider,
        "helper_proof_status": "NOT_RUN",
    }


def build_pair_from_body(body: bytes, source: dict) -> tuple[bytes, bytes, dict]:
    require(isinstance(body, bytes) and body.startswith(b"{\n") and body.endswith(b"}"),
            "body must be one exact braced source body")
    require(source.get("target_specialization") ==
            "T = *mut Element; Element unrestricted" and
            source.get("runtime_body_exact") is True,
            "mutable source certificate is missing exact specialization")
    verified = PREFIX + MUT_SIGNATURE + CONTRACT + body + b"\n"
    original = strip_ghost(verified)
    require(original.count(body) == verified.count(body) == 1 and
            original.count(MUT_SIGNATURE) == 1 and
            original.count(b"*const Element") == 0 and
            original.count(b"*mut Element") == 3 and
            original.count(b"crate::mem::forget(guard);") == 1,
            "mutable fixture signature/body or runtime pair changed")
    record = {
        "classification": "MUTABLE_SOURCE_FIXTURE; CAPTURE ONLY",
        "source_certificate": source,
        "original_sha256": sha(original),
        "verified_sha256": sha(verified),
        "fixture_signature": MUT_SIGNATURE.decode(),
        "contract_text_sha256": sha(CONTRACT),
        "ghost_strip_identity": strip_ghost(verified) == original,
        "capture_only": True,
        "translator_admission": "NOT_IMPLEMENTED",
        "helper_proof_status": "NOT_RUN",
        "typed_mir_binding_established": False,
        "publication_status": "NOT_PUBLISHED",
        "proof_credit": 0,
    }
    require(record["contract_text_sha256"] == CONTRACT_SHA256,
            "planned P2 contract bytes changed")
    return original, verified, record


def write_fixture(repo: Path, out: Path) -> dict:
    require_cloud_provider()
    body, source = source_certificate(repo)
    original, verified, record = build_pair_from_body(body, source)
    require(not out.exists(), f"refusing to overwrite {out}")
    (out / "original").mkdir(parents=True)
    (out / "verified").mkdir()
    (out / "original/lib.rs").write_bytes(original)
    (out / "verified/lib.rs").write_bytes(verified)
    (out / "fixture.json").write_text(json.dumps(
        record, indent=2, sort_keys=True) + "\n")
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(write_fixture(args.repo, args.out),
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
