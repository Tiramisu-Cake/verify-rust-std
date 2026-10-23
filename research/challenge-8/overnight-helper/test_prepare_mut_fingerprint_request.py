"""Synthetic source-binding checks; no Rust or verification tools are run."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
spec = importlib.util.spec_from_file_location(
    "p2_mut_fingerprint_request", HERE / "prepare-mut-fingerprint-request.py")
TARGET = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = TARGET
spec.loader.exec_module(TARGET)
writer_spec = importlib.util.spec_from_file_location(
    "p2_mut_capture", HERE / "prepare-actual-helper-capture-mut.py")
WRITER = importlib.util.module_from_spec(writer_spec)
sys.modules[writer_spec.name] = WRITER
writer_spec.loader.exec_module(WRITER)


def synthetic_fixture(path: Path) -> None:
    """Build a byte-only fixture; never open repository std source."""
    body = (
        b"{\n"
        b"struct DropOnPanic<T> { inner: T }\n"
        b"impl<T> Drop for DropOnPanic<T> {\n"
        b"    fn drop(&mut self) { unsafe { self.inner.drop_in_place() } }\n"
        b"}\n"
        b"let guard = DropOnPanic { inner: guard };\n"
        b"drop.drop_in_place();\n"
        b"crate::mem::forget(guard);\n"
        b"crate::intrinsics::select_unpredictable(condition, true_val, false_val).assume_init()\n"
        b"}")
    prefix = (b"#![feature(core_intrinsics)]\n#![allow(internal_features)]\n\n"
              b"use std::mem::MaybeUninit;\nuse std::{intrinsics, mem};\n\n")
    contract = (
        b"/*@\nreq thread_token(?t) &*& t == currentThread;\n@*/\n"
        b"/*@\nens thread_token(t) &*& (result as pointer) ==\n"
        b"    (if condition { true_val as pointer } else { false_val as pointer });\n@*/\n"
        b"/*@\non_unwind_ens false;\n@*/\n")
    verified = prefix + WRITER.MUT_SIGNATURE + contract + body + b"\n"
    original = re.sub(rb"/\*@.*?@\*/(?:\r?\n)?", b"", verified, flags=re.S)
    digest = lambda data: hashlib.sha256(data).hexdigest()
    record = {
        "source_certificate": {
            "hint_sha256": digest(b"synthetic hint source"),
            "maybe_uninit_sha256": digest(b"synthetic MaybeUninit source"),
            "exact_body_sha256": digest(body),
            "target_specialization": "T = *mut Element; Element unrestricted",
            "runtime_body_exact": True,
            "guard_and_drop_body_retained": True,
            "actual_forget_redirect": False,
            "actual_assume_init_redirect": False,
        },
        "const_preparer_sha256": WRITER.CONST_PREPARER_SHA256,
        "original_sha256": digest(original),
        "verified_sha256": digest(verified),
        "contract_text_sha256": digest(contract),
        "fixture_signature": WRITER.MUT_SIGNATURE.decode(),
        "const_pair_identity_modulo_signature": True,
        "capture_only": True,
        "translator_admission": "NOT_IMPLEMENTED",
        "helper_proof_status": "NOT_RUN",
    }
    (path / "original").mkdir(parents=True)
    (path / "verified").mkdir()
    (path / "original/lib.rs").write_bytes(original)
    (path / "verified/lib.rs").write_bytes(verified)
    (path / "fixture.json").write_text(json.dumps(record))


class MutableFingerprintRequest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.fixture = self.tmp / "fixture"
        synthetic_fixture(self.fixture)

    def test_emits_request_with_fresh_capture_outputs_pending(self):
        request = TARGET.prepare_request(self.fixture)
        self.assertEqual(request["schema"], "select-p2-mut-fingerprint-request-v1")
        self.assertEqual(request["classification"], "STATIC_REQUEST_ONLY; NOT CLOUD EVIDENCE")
        self.assertEqual(request["fixture"]["signature"], TARGET.MUT_SIGNATURE)
        self.assertEqual(request["fixture"]["contract_text_sha256"], TARGET.CONTRACT_SHA256)
        self.assertTrue(all(row["status"] == "PENDING_CLOUD_CAPTURE"
                            for row in request["required_cloud_outputs"]))
        self.assertEqual(request["proof_status"], "NOT_RUN")
        self.assertEqual(request["publication_status"], "NOT_PUBLISHED")
        self.assertEqual(request["proof_credit"], 0)
        self.assertIn("changed cleanup/unwind successor",
                      request["required_refusal_controls"])

    def test_write_request_is_write_once_and_json_round_trips(self):
        path = self.tmp / "request.json"
        TARGET.write_request(self.fixture, path)
        self.assertEqual(json.loads(path.read_text()), TARGET.prepare_request(self.fixture))
        with self.assertRaisesRegex(ValueError, "refusing to overwrite"):
            TARGET.write_request(self.fixture, path)

    def test_rejects_changed_source_bytes_and_record_hash(self):
        path = self.fixture / "original/lib.rs"
        path.write_bytes(path.read_bytes() + b"\n")
        with self.assertRaisesRegex(ValueError, "fixture bytes differ"):
            TARGET.prepare_request(self.fixture)

    def test_rejects_mutable_source_with_const_or_wrong_depth(self):
        for replacement in (b"*const Element", b"**mut Element"):
            with self.subTest(replacement=replacement):
                self.setUp()
                path = self.fixture / "verified/lib.rs"
                data = path.read_bytes().replace(b"*mut Element", replacement, 1)
                path.write_bytes(data)
                record_path = self.fixture / "fixture.json"
                record = json.loads(record_path.read_text())
                import hashlib
                record["verified_sha256"] = hashlib.sha256(data).hexdigest()
                record_path.write_text(json.dumps(record))
                with self.assertRaises(ValueError):
                    TARGET.prepare_request(self.fixture)

    def test_rejects_drifted_runtime_cleanup_and_publication_state(self):
        original = self.fixture / "original/lib.rs"
        data = original.read_bytes().replace(b"crate::mem::forget(guard);",
                                             b"core::mem::forget(guard);", 1)
        original.write_bytes(data)
        verified = self.fixture / "verified/lib.rs"
        verified_data = verified.read_bytes().replace(b"crate::mem::forget(guard);",
                                                        b"core::mem::forget(guard);", 1)
        verified.write_bytes(verified_data)
        record_path = self.fixture / "fixture.json"
        record = json.loads(record_path.read_text())
        import hashlib
        record["original_sha256"] = hashlib.sha256(data).hexdigest()
        record["verified_sha256"] = hashlib.sha256(verified_data).hexdigest()
        record_path.write_text(json.dumps(record))
        with self.assertRaisesRegex(ValueError, "runtime body operation"):
            TARGET.prepare_request(self.fixture)
        # Even a valid source pair must not make this preparer a publisher.
        self.setUp()
        record = json.loads((self.fixture / "fixture.json").read_text())
        record["helper_proof_status"] = "PASS"
        (self.fixture / "fixture.json").write_text(json.dumps(record))
        with self.assertRaisesRegex(ValueError, "status must remain"):
            TARGET.prepare_request(self.fixture)


if __name__ == "__main__":
    unittest.main()
