#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Prepare a static Cloud fingerprint request for P2 at T = *mut Element.

This adapter only validates and pins the source fixture already produced by
prepare-actual-helper-capture-mut.py. It does not run Rust, export/decode MIR,
admit a translator certificate, or prove the helper. The emitted request is
an input checklist for a later authorized capture, not evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


SCHEMA = "select-p2-mut-fingerprint-request-v1"
CONTRACT_SHA256 = "dc985de2e2a0e1a95e6c12c4b9cb78c4042d9d45f949d78904a999e82262b870"
MUT_SIGNATURE = (
    "pub fn select_unpredictable<Element>(\n"
    "    condition: bool,\n    true_val: *mut Element,\n"
    "    false_val: *mut Element,\n) -> *mut Element\n"
)
CONST_SIGNATURE = MUT_SIGNATURE.replace("*mut Element", "*const Element")
RUNTIME_SENTINELS = (
    b"struct DropOnPanic<T> {",
    b"impl<T> Drop for DropOnPanic<T> {",
    b"unsafe { self.inner.drop_in_place() }",
    b"let guard = DropOnPanic { inner: guard };",
    b"drop.drop_in_place();",
    b"crate::mem::forget(guard);",
    b"crate::intrinsics::select_unpredictable(condition, true_val, false_val).assume_init()",
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)


def load_fixture(fixture_dir: Path) -> dict:
    record = json.loads((fixture_dir / "fixture.json").read_text())
    original = (fixture_dir / "original/lib.rs").read_bytes()
    verified = (fixture_dir / "verified/lib.rs").read_bytes()
    require(record.get("capture_only") is True,
            "fixture is not marked capture-only")
    require(record.get("translator_admission") == "NOT_IMPLEMENTED" and
            record.get("helper_proof_status") == "NOT_RUN",
            "fixture status must remain unadmitted and unproved")
    require(record.get("original_sha256") == digest(original) and
            record.get("verified_sha256") == digest(verified),
            "fixture bytes differ from their recorded hashes")
    require(record.get("fixture_signature") == MUT_SIGNATURE,
            "fixture signature is not the exact *mut Element specialization")
    require(record.get("contract_text_sha256") == CONTRACT_SHA256,
            "fixture contract differs from planned P2 contract")
    require(record.get("const_pair_identity_modulo_signature") is True,
            "fixture lacks const-pair identity certificate")
    require(verified.count(MUT_SIGNATURE.encode()) == 1 and
            CONST_SIGNATURE.encode() not in verified,
            "verified source has a missing/ambiguous/mixed pointer signature")
    require(b"*const" not in original and original.count(b"*mut Element") == 3,
            "original source has an unexpected pointer kind or depth")
    require(verified.count(b"/*@") == 3,
            "expected req, ens and unwind ghost blocks are not present")
    require(verified.replace(
        b"/*@\nreq thread_token(?t) &*& t == currentThread;\n@*/\n"
        b"/*@\nens thread_token(t) &*& (result as pointer) ==\n"
        b"    (if condition { true_val as pointer } else { false_val as pointer });\n@*/\n"
        b"/*@\non_unwind_ens false;\n@*/\n", b"") == original,
        "ghost-stripped runtime source does not equal original source")
    for sentinel in RUNTIME_SENTINELS:
        require(original.count(sentinel) == 1,
                f"runtime body operation absent/ambiguous: {sentinel.decode()}")
    source = record.get("source_certificate", {})
    require(source.get("runtime_body_exact") is True and
            source.get("guard_and_drop_body_retained") is True and
            source.get("actual_forget_redirect") is False and
            source.get("actual_assume_init_redirect") is False,
            "source certificate does not preserve the actual runtime body")
    return {"record": record, "original": original, "verified": verified}


def prepare_request(fixture_dir: Path) -> dict:
    fixture = load_fixture(fixture_dir)
    record = fixture["record"]
    src = record["source_certificate"]
    return {
        "schema": SCHEMA,
        "classification": "STATIC_REQUEST_ONLY; NOT CLOUD EVIDENCE",
        "specialization": "T = *mut Element; Element unrestricted",
        "callee": "core::hint::select_unpredictable",
        "fixture": {
            "original_sha256": record["original_sha256"],
            "verified_sha256": record["verified_sha256"],
            "const_preparer_sha256": record["const_preparer_sha256"],
            "hint_source_sha256": src["hint_sha256"],
            "maybe_uninit_source_sha256": src["maybe_uninit_sha256"],
            "exact_body_sha256": src["exact_body_sha256"],
            "contract_text_sha256": record["contract_text_sha256"],
            "signature": MUT_SIGNATURE,
            "ghost_strip_identity": True,
            "runtime_body_exact": True,
        },
        "required_cloud_outputs": [
            {"name": "verified_source_identity", "status": "PENDING_CLOUD_CAPTURE"},
            {"name": "original_source_identity", "status": "PENDING_CLOUD_CAPTURE"},
            {"name": "normal_decoded_unit_and_body", "status": "PENDING_CLOUD_CAPTURE"},
            {"name": "readonly_decoded_unit_and_body", "status": "PENDING_CLOUD_CAPTURE"},
            {"name": "snapshot_inventory_and_hashes", "status": "PENDING_CLOUD_CAPTURE"},
        ],
        "typed_binding_obligations": [
            "public wrapper FnDef generic substitution is *mut Element",
            "true_val, false_val and result are exactly one mutable raw-pointer layer over Element",
            "constructor/as_mut_ptr/pointer-drop wrapper types preserve mutable pointer kind and depth",
            "both select operands and branch result bind to the same *mut Element specialization",
            "assume_init/transmute, checked forget and nested Drop bindings use fresh typed MIR pins",
            "cleanup/unwind successors are captured and graph-reviewed; no edge is inferred from source text",
        ],
        "required_refusal_controls": [
            "const/mut substitution", "wrong pointer depth", "wrong select operand or branch result",
            "changed source/signature/runtime bytes", "mismatched generic substitution",
            "changed cleanup/unwind successor",
        ],
        "proof_status": "NOT_RUN",
        "translator_admission": "NOT_IMPLEMENTED",
        "publication_status": "NOT_PUBLISHED",
        "proof_credit": 0,
    }


def write_request(fixture_dir: Path, output: Path) -> dict:
    request = prepare_request(fixture_dir)
    require(not output.exists(), f"refusing to overwrite {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(request, indent=2, sort_keys=True) + "\n")
    return request


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(write_request(args.fixture, args.out), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
