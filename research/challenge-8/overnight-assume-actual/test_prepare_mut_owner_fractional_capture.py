"""Synthetic integration checks for the inactive mutable source chain."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
import shutil
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "p2_mut_owner_fractional_capture",
    HERE / "prepare-mut-owner-fractional-capture.py")
TARGET = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = TARGET
spec.loader.exec_module(TARGET)
OWNER, FRACTIONAL, WRITER = TARGET.load_dependencies()
REPAIR = FRACTIONAL._load_pinned("r20_final_select_repair.py",
                                  "mut_chain_test_r20",
                                  FRACTIONAL.PINNED_REPAIR_SHA256)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def synthetic_pair(mut: bool = True) -> tuple[bytes, bytes, dict]:
    signature = WRITER.MUT_SIGNATURE if mut else WRITER.CONST_SIGNATURE
    source = (
        b"use std::mem::ManuallyDrop;\n"
        b"pub unsafe fn checked_forget_owned<T>(t: T)\n" +
        FRACTIONAL.FORGET_OLD_CONTRACT + FRACTIONAL.FORGET_BODY + b"\n\n"
        b"struct DropOnPanic<T> { inner: T }\n"
        b"impl<T> Drop for DropOnPanic<T> {\n"
        b"    fn drop(&mut self) {\n" + OWNER.NESTED_DROP_CALL +
        b"    }\n}\n"
        b"pub fn select_unpredictable<Element>(\n"
        b"    condition: bool,\n    true_val: *mut Element,\n"
        b"    false_val: *mut Element,\n) -> *mut Element\n"
        b"/*@\nreq thread_token(?t) &*& t == currentThread;\n@*/\n"
        b"/*@\nens thread_token(t) &*& (result as pointer) ==\n"
        b"    (if condition { true_val as pointer } else { false_val as pointer });\n@*/\n"
        b"/*@\non_unwind_ens false;\n@*/\n{\n"
        b"    crate::intrinsics::select_unpredictable(a, b, c);\n"
        b"    let true_ptr = true_val.as_mut_ptr();\n"
        b"    let false_ptr = false_val.as_mut_ptr();\n"
        b"        let guard = DropOnPanic { inner: guard };\n"
        b"    crate::intrinsics::select_unpredictable(a, b, c);\n"
        b"        drop.drop_in_place();\n"
        b"        crate::mem::forget(guard);\n"
        b"        crate::intrinsics::select_unpredictable(condition, true_val, false_val).assume_init()\n"
        b"}\n")
    # The helper signature is a single specialization point. Keep the body
    # representative but replace exactly the signature's three type sites.
    signature_start = source.index(WRITER.MUT_SIGNATURE)
    source = (source[:signature_start] + WRITER.MUT_SIGNATURE +
              source[signature_start + len(WRITER.MUT_SIGNATURE):]) if mut else source
    if not mut:
        mutable_sig = WRITER.MUT_SIGNATURE
        const_sig = WRITER.CONST_SIGNATURE
        source = source.replace(mutable_sig, const_sig, 1)
    original = OWNER.strip_ghost(source)
    record = {
        "classification": "MUTABLE_OWNER_INPUT_CAPTURE_ONLY",
        "input_stage": "PRE_OWNER_PROJECTION_FULL_UNIT",
        "synthetic_fixture": True,
        "actual_helper_proved": False,
        "semantic_frontend_enabled": False,
        "contract_text_sha256": TARGET.CONTRACT_SHA256,
        "original_sha256": digest(original),
        "verified_sha256": digest(source),
    }
    return original, source, record


class MutableOwnerFractionalChain(unittest.TestCase):
    def test_mutable_pair_flows_through_owner_saved_guard_and_r20_r21(self):
        original, verified, record = synthetic_pair(mut=True)
        output, stages = TARGET.transform_pair(original, verified, record)
        self.assertEqual(OWNER.strip_ghost(output), original)
        self.assertEqual(output.count(WRITER.MUT_SIGNATURE), 1)
        self.assertNotIn(b"*const Element", output)
        self.assertEqual(output.count(REPAIR.SELECTED_BRANCH_BLOCK), 1)
        self.assertEqual(output.count(FRACTIONAL.FORGET_HALF_CONTRACT), 1)
        self.assertEqual(output.count(FRACTIONAL.CONSTRUCTOR_OWN_RELEASE), 1)
        self.assertTrue(stages["runtime_source_preserved"])

    def test_transform_stages_are_pointer_kind_neutral_and_const_bytes_restore(self):
        mut_original, mut_verified, mut_record = synthetic_pair(mut=True)
        const_original, const_verified, _ = synthetic_pair(mut=False)
        mut_output, _ = TARGET.transform_pair(mut_original, mut_verified, mut_record)
        # Exercise the pinned const transforms directly on the synthetic const
        # fixture to assert identical annotations modulo its signature.
        const_owner = OWNER.candidate(const_verified, const_original,
                                      owner_literal=True)
        const_owner = TARGET._add_saved_guard_transfer(OWNER, const_owner)
        const_output = FRACTIONAL.transform(const_owner, "positive")
        self.assertEqual(
            mut_output.replace(WRITER.MUT_SIGNATURE, WRITER.CONST_SIGNATURE, 1),
            const_output)
        self.assertEqual(OWNER.strip_ghost(const_output), const_original)

    def test_rejects_const_mut_depth_and_source_mismatch(self):
        original, verified, record = synthetic_pair(mut=True)
        const_verified = verified.replace(WRITER.MUT_SIGNATURE,
                                          WRITER.CONST_SIGNATURE, 1)
        const_original = OWNER.strip_ghost(const_verified)
        const_record = dict(record, original_sha256=digest(const_original),
                            verified_sha256=digest(const_verified))
        with self.assertRaisesRegex(ValueError, "exact mutable specialization"):
            TARGET.transform_pair(const_original, const_verified, const_record)
        wrong_depth = verified.replace(b"*mut Element", b"**mut Element", 1)
        wrong_original = OWNER.strip_ghost(wrong_depth)
        wrong_record = dict(record, original_sha256=digest(wrong_original),
                            verified_sha256=digest(wrong_depth))
        with self.assertRaisesRegex(ValueError, "exact mutable specialization"):
            TARGET.transform_pair(wrong_original, wrong_depth, wrong_record)
        changed_original = original + b"\n"
        with self.assertRaisesRegex(ValueError, "does not match its recorded hashes"):
            TARGET.transform_pair(changed_original, verified, record)

    def test_refuses_missing_nine_body_transfer_anchors(self):
        original, verified, record = synthetic_pair(mut=True)
        bad = verified.replace(b"crate::mem::forget(guard);\n", b"", 1)
        bad_original = OWNER.strip_ghost(bad)
        bad_record = dict(record, original_sha256=digest(bad_original),
                          verified_sha256=digest(bad))
        with self.assertRaisesRegex(ValueError, "call/forget inventory"):
            TARGET.transform_pair(bad_original, bad, bad_record)

    def test_write_candidate_preserves_capture_only_status(self):
        original, verified, record = synthetic_pair(mut=True)
        with tempfile.TemporaryDirectory() as tmp:
            input_dir = Path(tmp) / "input"
            output_dir = Path(tmp) / "output"
            (input_dir / "original").mkdir(parents=True)
            (input_dir / "verified").mkdir()
            (input_dir / "original/lib.rs").write_bytes(original)
            (input_dir / "verified/lib.rs").write_bytes(verified)
            (input_dir / "fixture.json").write_text(json.dumps(record))
            result = TARGET.write_candidate(input_dir, output_dir)
            self.assertEqual(result["classification"],
                             "MUTABLE_SOURCE_CANDIDATE; CAPTURE ONLY")
            self.assertEqual(result["helper_proof_status"], "NOT_RUN")
            self.assertEqual(result["translator_admission"], "NOT_IMPLEMENTED")
            self.assertEqual(result["publication_status"], "NOT_PUBLISHED")
            self.assertEqual(OWNER.strip_ghost(
                (output_dir / "verified/lib.rs").read_bytes()), original)


if __name__ == "__main__":
    unittest.main()
