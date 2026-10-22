"""Synthetic byte-transform checks; no preparation or proof tools are run."""
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


R20 = load("r20_final_select_source_pin", HERE / "r20_final_select_repair.py")
CONTROLS = load("r21_final_select_controls_test", HERE / "r21_final_select_controls.py")
GHOST = load("r21_final_select_ghost_strip", HERE.parent / "cloud-build" /
             "sort4-native-c1-bound" / "ghost-strip.py")


def unit() -> bytes:
    return (b"pub const fn select_unpredictable<T>(condition: bool, true_val: T, false_val: T) -> T {\n"
            b"    let true_ptr = true_val.as_mut_ptr();\n"
            b"    let false_ptr = false_val.as_mut_ptr();\n"
            + R20.PAYLOAD_ASSERTS[0] + R20.PAYLOAD_ASSERTS[1] +
            CONTROLS.SELECTED_PAYLOAD_ASSERT +
            b"    unsafe {\n"
            b"        crate::mem::forget(guard);\n"
            + CONTROLS.SELECTED_BRANCH_BLOCK + CONTROLS.FINAL_CALL +
            b"    }\n}\n")


def close(payload: bytes) -> bytes:
    return (b"                 std::mem::close_MaybeUninit_pointer_own::<Element>(t, "
            b"std::mem::MaybeUninit::new::<*Element>(" + payload + b"));\n")


class FinalSelectControls(unittest.TestCase):
    def setUp(self):
        self.source = unit()

    def expected_block(self, variant: str) -> bytes:
        block = CONTROLS.SELECTED_BRANCH_BLOCK
        if variant == "omit-selected-own":
            return block.replace(close(b"selected_payload"), b"", 2)
        block = block.replace(close(b"false_payload"), b"", 1)
        return block.replace(close(b"true_payload"), b"", 1)

    def test_source_pin_and_selected_block_match_pinned_repair(self):
        path = HERE / "r20_final_select_repair.py"
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),
                         CONTROLS.PINNED_REPAIR_SOURCE_SHA256)
        self.assertEqual(CONTROLS.PINNED_REPAIR_SOURCE_SHA256,
                         "3646b05602b7dce35cd4b2ab8f74d8cfe280d65df2637ac4f6cc0a128dd7e2a3")
        self.assertEqual(CONTROLS.SELECTED_BRANCH_BLOCK,
                         R20.SELECTED_BRANCH_BLOCK)
        self.assertEqual(hashlib.sha256(CONTROLS.SELECTED_BRANCH_BLOCK).hexdigest(),
                         CONTROLS.SELECTED_BRANCH_BLOCK_SHA256)

    def test_each_control_removes_only_its_two_branch_close_lines(self):
        for variant in CONTROLS.VARIANTS:
            with self.subTest(variant=variant):
                result = CONTROLS.transform(self.source, variant)
                expected = self.expected_block(variant)
                self.assertEqual(result,
                                 self.source.replace(CONTROLS.SELECTED_BRANCH_BLOCK,
                                                     expected, 1))
                self.assertEqual(result.count(b"close_MaybeUninit::<*Element>"), 2)
                self.assertEqual(result.count(b"close_MaybeUninit_pointer_own"), 2)
                self.assertEqual(result.count(b"if (condition)"), 1)
                self.assertEqual(result.count(b"} else {"), 1)
                self.assertEqual(GHOST.strip_ghost(result),
                                 GHOST.strip_ghost(self.source))
                with self.assertRaises(RuntimeError):
                    CONTROLS.transform(result, variant)

    def test_omission_semantics_are_branch_specific(self):
        selected_omitted = CONTROLS.transform(self.source, "omit-selected-own")
        selected_block = selected_omitted[
            selected_omitted.index(b"        /*@ if (condition) {"):]
        selected_block = selected_block[:selected_block.index(b"} @*/")]
        self.assertNotIn(b"selected_payload))", selected_block)
        self.assertIn(b"(false_payload))", selected_block)
        self.assertIn(b"(true_payload))", selected_block)

        unselected_omitted = CONTROLS.transform(self.source, "omit-unselected-own")
        unselected_block = unselected_omitted[
            unselected_omitted.index(b"        /*@ if (condition) {"):]
        unselected_block = unselected_block[:unselected_block.index(b"} @*/")]
        self.assertEqual(unselected_block.count(b"(selected_payload))"), 2)
        self.assertNotIn(b"(false_payload))", unselected_block)
        self.assertNotIn(b"(true_payload))", unselected_block)

    def test_refuses_malformed_duplicate_and_pre_repaired_blocks(self):
        malformed = self.source.replace(
            close(b"selected_payload"), close(b"true_payload"), 1)
        duplicate = self.source.replace(
            CONTROLS.SELECTED_BRANCH_BLOCK,
            CONTROLS.SELECTED_BRANCH_BLOCK * 2, 1)
        pre_repaired = self.source.replace(close(b"selected_payload"), b"", 1)
        wrong_r20_branch = self.source.replace(
            CONTROLS.SELECTED_BRANCH_BLOCK, R20.BRANCH_BLOCK, 1)
        extra_close = self.source.replace(
            b"        crate::mem::forget(guard);\n",
            b"        crate::mem::forget(guard);\n" + close(b"true_payload"), 1)
        for label, candidate in (
                ("wrong-branch-payload", malformed),
                ("duplicate-block", duplicate),
                ("pre-repaired", pre_repaired),
                ("wrong-r20-branch", wrong_r20_branch),
                ("close-outside-block", extra_close)):
            with self.subTest(refusal=label), self.assertRaises(RuntimeError):
                CONTROLS.transform(candidate, "omit-selected-own")

    def test_refuses_missing_duplicate_moved_payloads_and_bad_gap(self):
        missing_selected = self.source.replace(
            CONTROLS.SELECTED_PAYLOAD_ASSERT, b"", 1)
        duplicate_selected = self.source.replace(
            CONTROLS.SELECTED_PAYLOAD_ASSERT,
            CONTROLS.SELECTED_PAYLOAD_ASSERT * 2, 1)
        missing_true = self.source.replace(R20.PAYLOAD_ASSERTS[0], b"", 1)
        moved_false = self.source.replace(R20.PAYLOAD_ASSERTS[1], b"", 1).replace(
            CONTROLS.FINAL_CALL, R20.PAYLOAD_ASSERTS[1] + CONTROLS.FINAL_CALL, 1)
        bad_gap = self.source.replace(
            CONTROLS.SELECTED_BRANCH_BLOCK + CONTROLS.FINAL_CALL,
            CONTROLS.SELECTED_BRANCH_BLOCK + b"        unsafe { }\n" +
            CONTROLS.FINAL_CALL, 1)
        no_final = self.source.replace(CONTROLS.FINAL_CALL, b"", 1)
        duplicate_final = self.source.replace(
            CONTROLS.FINAL_CALL, CONTROLS.FINAL_CALL * 2, 1)
        for label, candidate in (
                ("missing-selected-binding", missing_selected),
                ("duplicate-selected-binding", duplicate_selected),
                ("missing-payload", missing_true),
                ("moved-payload", moved_false),
                ("statement-in-gap", bad_gap),
                ("missing-final", no_final),
                ("duplicate-final", duplicate_final)):
            with self.subTest(refusal=label), self.assertRaises(RuntimeError):
                CONTROLS.transform(candidate, "omit-unselected-own")

    def test_refuses_unknown_variant_and_non_bytes(self):
        with self.assertRaisesRegex(RuntimeError, "unknown control variant"):
            CONTROLS.transform(self.source, "all")
        with self.assertRaisesRegex(RuntimeError, "must be bytes"):
            CONTROLS.transform("not bytes", "omit-selected-own")


if __name__ == "__main__":
    unittest.main()
