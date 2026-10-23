"""Synthetic source-binding checks; no Rust or verification tools are run."""
from __future__ import annotations

import importlib.util
import json
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


class MutableFingerprintRequest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.fixture = self.tmp / "fixture"
        WRITER.write_fixture(REPO, self.fixture)

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
