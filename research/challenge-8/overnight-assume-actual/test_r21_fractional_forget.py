"""Synthetic source-transform checks; no preparation or proof tools are run."""
from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
import sys
import unittest


HERE = Path(__file__).resolve().parent


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load isolated module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


TRANSFORM = load("r21_fractional_forget_test", HERE / "r21_fractional_forget.py")
REPAIR = load("r21_fractional_repair_source_pin", HERE / "r20_final_select_repair.py")
CONTROLS = load("r21_fractional_controls_source_pin", HERE / "r21_final_select_controls.py")
GHOST = load("r21_fractional_ghost_strip", HERE.parent / "cloud-build" /
             "sort4-native-c1-bound" / "ghost-strip.py")


def source() -> bytes:
    """Small input with the exact source anchors required by the transform."""
    return (
        b"pub unsafe fn checked_forget_owned<T>(t: T)\n" +
        TRANSFORM.FORGET_OLD_CONTRACT + TRANSFORM.FORGET_BODY + b"\n\n" +
        b"pub unsafe fn select_unpredictable(condition: bool) {\n"
        b"    let true_payload = true_val;\n"
        b"    let false_payload = false_val;\n"
        b"    let guard = DropOnPanic { inner: guard };\n"
        + TRANSFORM.CLOSE_OWNER_FULL +
        b"        drop.drop_in_place();\n"
        + TRANSFORM.SAVED_GUARD_FULL +
        b"        crate::mem::forget(guard);\n"
        + TRANSFORM.RETURNED_GUARD_FULL +
        REPAIR.PAYLOAD_ASSERTS[0] + REPAIR.PAYLOAD_ASSERTS[1]
        + REPAIR.SELECTED_BLOCK + REPAIR.FINAL_CALL + b"}\n")


class FractionalForgetTransform(unittest.TestCase):
    def setUp(self):
        self.input = source()

    def test_pinned_source_transform_dependencies(self):
        self.assertEqual(hashlib.sha256((HERE / "r20_final_select_repair.py").read_bytes()).hexdigest(),
                         TRANSFORM.PINNED_REPAIR_SHA256)
        self.assertEqual(hashlib.sha256((HERE / "r21_final_select_controls.py").read_bytes()).hexdigest(),
                         TRANSFORM.PINNED_CONTROLS_SHA256)
        self.assertEqual(TRANSFORM.PINNED_REPAIR_SHA256,
                         "3646b05602b7dce35cd4b2ab8f74d8cfe280d65df2637ac4f6cc0a128dd7e2a3")
        self.assertEqual(TRANSFORM.BASELINE_SHA256_PREFIX, "1798132f")

    def test_positive_has_exact_fractional_ownership_and_selected_repair(self):
        out = TRANSFORM.transform(self.input)
        self.assertEqual(out.count(TRANSFORM.CLOSE_OWNER_HALF), 1)
        self.assertEqual(out.count(TRANSFORM.SAVED_GUARD_HALF), 1)
        self.assertEqual(out.count(TRANSFORM.RETURNED_GUARD_HALF), 1)
        self.assertEqual(out.count(TRANSFORM.FORGET_HALF_CONTRACT), 1)
        self.assertEqual(out.count(REPAIR.SELECTED_BRANCH_BLOCK), 1)
        self.assertEqual(out.count(b"close [1/2] raw_ptr_own::<Element>()"), 2)
        self.assertEqual(out.count(b"[1/2] <select_unpredictable::DropOnPanic<*Element>>.own"), 4)
        self.assertEqual(out.count(b"merge_fractions *saved_guard.inner |-> _;"), 1)
        self.assertEqual(out.count(b"/*@"), self.input.count(b"/*@"))
        self.assertEqual(out.count(b"@*/"), self.input.count(b"@*/"))
        self.assertEqual(GHOST.strip_ghost(out), GHOST.strip_ghost(self.input))
        self.assertIn(TRANSFORM.FORGET_BODY, out)
        self.assertIn(b"on_unwind_ens false;", out)
        self.assertEqual(out.count(b"pub unsafe fn checked_forget_owned<T>(t: T)"), 1)

    def test_control_variants_keep_runtime_and_expected_failure_site(self):
        positive = TRANSFORM.transform(self.input, "positive")
        expected = {
            "omit-selected-own": 2,
            "omit-unselected-own": 2,
            "no-retained-half": 4,
            "callee-false-normal": 4,
            "callee-owner-duplicate": 4,
            "callee-owner-loss": 4,
            "callee-thread-duplicate": 4,
        }
        for variant, closes in expected.items():
            with self.subTest(variant=variant):
                out = TRANSFORM.transform(self.input, variant)
                self.assertEqual(out.count(b"close_MaybeUninit_pointer_own"), closes)
                self.assertEqual(GHOST.strip_ghost(out), GHOST.strip_ghost(self.input))
                self.assertEqual(out.count(REPAIR.FINAL_CALL), 1)
                self.assertEqual(out.count(b"if (condition)"), 2)
                self.assertEqual(out.count(b"crate::mem::forget(guard);"), 1)
                self.assertIn(TRANSFORM.FORGET_BODY, out)
                with self.assertRaises(RuntimeError):
                    TRANSFORM.transform(out, variant)
        selected = TRANSFORM.transform(self.input, "omit-selected-own")
        self.assertEqual(selected.count(b"(selected_payload))"), 0)
        unselected = TRANSFORM.transform(self.input, "omit-unselected-own")
        self.assertEqual(unselected.count(b"(selected_payload))"), 2)
        self.assertNotIn(b"close [1/2] raw_ptr_own::<Element>()",
                         TRANSFORM.transform(self.input, "no-retained-half"))
        self.assertIn(b"&*& false;", TRANSFORM.transform(self.input, "callee-false-normal"))
        duplicate = TRANSFORM.transform(self.input, "callee-owner-duplicate")
        self.assertIn(TRANSFORM.FORGET_DUPLICATE_OWNER_CONTRACT, duplicate)
        self.assertNotIn(b"ens thread_token(tid) &*& [1/2]", 
                         TRANSFORM.transform(self.input, "callee-owner-loss"))
        self.assertEqual(TRANSFORM.transform(self.input, "callee-thread-duplicate").count(
            b"ens thread_token(tid) &*& thread_token(tid)"), 1)
        self.assertEqual(GHOST.strip_ghost(positive), GHOST.strip_ghost(self.input))

    def test_refuses_missing_duplicate_or_malformed_source_anchors(self):
        bad = [
            ("missing owner close", self.input.replace(TRANSFORM.CLOSE_OWNER_FULL, b"", 1)),
            ("duplicate owner close", self.input.replace(
                TRANSFORM.CLOSE_OWNER_FULL, TRANSFORM.CLOSE_OWNER_FULL * 2, 1)),
            ("already fractional", self.input.replace(
                TRANSFORM.CLOSE_OWNER_FULL, TRANSFORM.CLOSE_OWNER_HALF, 1)),
            ("wrong saved guard", self.input.replace(
                TRANSFORM.SAVED_GUARD_FULL, TRANSFORM.SAVED_GUARD_HALF, 1)),
            ("changed forget body", self.input.replace(
                TRANSFORM.FORGET_BODY, b"{\n    different();\n}", 1)),
            ("duplicate contract", self.input.replace(
                TRANSFORM.FORGET_OLD_CONTRACT,
                TRANSFORM.FORGET_OLD_CONTRACT * 2, 1)),
            ("duplicate final call", self.input.replace(
                REPAIR.FINAL_CALL, REPAIR.FINAL_CALL * 2, 1)),
        ]
        for label, candidate in bad:
            with self.subTest(refusal=label), self.assertRaises(RuntimeError):
                TRANSFORM.transform(candidate)
        with self.assertRaises(RuntimeError):
            TRANSFORM.transform(self.input, "not-a-variant")
        with self.assertRaises(RuntimeError):
            TRANSFORM.transform(bytearray(self.input))

    def test_source_change_is_ghost_only_and_candidate_inverts(self):
        out = TRANSFORM.transform(self.input)
        fractional = out.replace(REPAIR.SELECTED_BRANCH_BLOCK, REPAIR.SELECTED_BLOCK, 1)
        fractional = fractional.replace(TRANSFORM.FORGET_HALF_CONTRACT,
                                        TRANSFORM.FORGET_OLD_CONTRACT, 1)
        fractional = fractional.replace(TRANSFORM.RETURNED_GUARD_HALF,
                                        TRANSFORM.RETURNED_GUARD_FULL, 1)
        fractional = fractional.replace(TRANSFORM.SAVED_GUARD_HALF,
                                        TRANSFORM.SAVED_GUARD_FULL, 1)
        fractional = fractional.replace(TRANSFORM.CLOSE_OWNER_HALF,
                                        TRANSFORM.CLOSE_OWNER_FULL, 1)
        self.assertEqual(fractional, self.input)
        self.assertEqual(GHOST.strip_ghost(out), GHOST.strip_ghost(self.input))


if __name__ == "__main__":
    unittest.main()
