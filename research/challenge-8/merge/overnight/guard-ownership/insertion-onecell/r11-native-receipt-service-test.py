#!/usr/bin/env python3
"""Synthetic tests for R11 current exporter/decode receipt provenance."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("r11_receipt_prove", HERE / "prove.py")
PROVE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PROVE)


class NativeReceiptTests(unittest.TestCase):
    def setUp(self):
        self.source = {"original/lib.rs": "a" * 64,
                       "verified/lib.rs": "b" * 64,
                       "small_sort_source": "c" * 64}
        self.identity = {"cloud_build_id": "build", "source_sha256": "c" * 64}
        self.stage = "exporter"
        self.receipt = {"stage": "exporter", "exit_code": 0,
                        "status": "SUCCESS", "error": None,
                        "source_unchanged": True, "source_before": dict(self.source),
                        "source_after": dict(self.source)}

    def test_success_stamps_exact_artifact_identity(self):
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "compiler-mir.bin"
            output.write_bytes(b"native bytes")
            result = PROVE._r11_stamp_native_receipt(
                dict(self.receipt), "exporter", 0, self.source, output, self.identity)
            self.assertEqual(result["output_path"], "compiler-mir.bin")
            self.assertEqual(result["output_size"], len(b"native bytes"))
            self.assertEqual(result["output_sha256"], PROVE.hashlib.sha256(b"native bytes").hexdigest())
            self.assertEqual(result["r11_run_identity"], self.identity)

    def test_decode_binds_input_snapshot_and_output(self):
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "decode.out"
            output.write_bytes(b"decoded")
            receipt = {**self.receipt, "stage": "decode"}
            result = PROVE._r11_stamp_native_receipt(
                receipt, "decode", 0, self.source, output, self.identity,
                decode_input_before=b"native")
            self.assertEqual(result["input_path"], "compiler-mir.bin")
            self.assertEqual(result["input_sha256"], PROVE.hashlib.sha256(b"native").hexdigest())

    def test_error_partial_timeout_and_not_run_are_never_stamped(self):
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "compiler-mir.bin"
            output.write_bytes(b"some bytes")
            variants = [
                (self.receipt, 1),
                ({**self.receipt, "status": "ERROR"}, 0),
                ({**self.receipt, "status": "NOT_RUN"}, 0),
                ({**self.receipt, "source_unchanged": False}, 0),
                ({**self.receipt, "source_after": {**self.source, "verified/lib.rs": "d" * 64}}, 0),
                (None, 0),
            ]
            for receipt, code in variants:
                self.assertIsNone(PROVE._r11_stamp_native_receipt(
                    receipt, "exporter", code, self.source, output, self.identity))

    def test_missing_or_empty_output_is_not_stamped(self):
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "compiler-mir.bin"
            self.assertIsNone(PROVE._r11_stamp_native_receipt(
                dict(self.receipt), "exporter", 0, self.source, output, self.identity))
            output.write_bytes(b"")
            self.assertIsNone(PROVE._r11_stamp_native_receipt(
                dict(self.receipt), "exporter", 0, self.source, output, self.identity))

    def test_decode_requires_input_snapshot(self):
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "decode.out"
            output.write_bytes(b"decoded")
            receipt = {**self.receipt, "stage": "decode"}
            self.assertIsNone(PROVE._r11_stamp_native_receipt(
                receipt, "decode", 0, self.source, output, self.identity))

    def test_existing_receipt_or_output_refuses_current_run(self):
        with tempfile.TemporaryDirectory() as td:
            case = Path(td)
            self.assertEqual(PROVE._r11_require_fresh_native_paths(case, "exporter"),
                             case / "compiler-mir.bin")
            (case / "compiler-mir.bin").write_bytes(b"old")
            with self.assertRaises(RuntimeError):
                PROVE._r11_require_fresh_native_paths(case, "exporter")
            (case / "compiler-mir.bin").unlink()
            (case / "decode-stage.json").write_text("{}")
            with self.assertRaises(RuntimeError):
                PROVE._r11_require_fresh_native_paths(case, "decode")


if __name__ == "__main__":
    unittest.main()
