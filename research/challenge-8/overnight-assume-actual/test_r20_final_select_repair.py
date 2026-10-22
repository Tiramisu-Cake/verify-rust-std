"""Synthetic service tests for the R20 final-select repair transform."""
import importlib.util
from pathlib import Path
import unittest

_spec = importlib.util.spec_from_file_location(
    "r20_final_select_repair", Path(__file__).with_name("r20_final_select_repair.py"))
REPAIR = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(REPAIR)

HINT = Path(__file__).resolve().parents[3] / "library/core/src/hint.rs"

UNIT = (b"pub const fn select_unpredictable<T>(condition: bool, true_val: T, false_val: T) -> T {\n"
        b"    let true_ptr = true_val.as_mut_ptr();\n"
        b"    let false_ptr = false_val.as_mut_ptr();\n"
        + REPAIR.PAYLOAD_ASSERTS[0] + REPAIR.PAYLOAD_ASSERTS[1] +
        b"    unsafe {\n"
        b"        crate::mem::forget(guard);\n"
        + REPAIR.FINAL_CALL +
        b"    }\n}\n")


class FinalSelectRepair(unittest.TestCase):
    def test_final_call_anchor_is_the_actual_std_line(self):
        self.assertEqual(HINT.read_bytes().count(REPAIR.FINAL_CALL), 1)

    def test_variants_insert_only_ghost_lines_before_the_final_select(self):
        expected = {"both": 2, "true-only": 1, "false-only": 1, "none": 0}
        for variant, count in expected.items():
            with self.subTest(variant=variant):
                out = REPAIR.repair(UNIT, variant)
                self.assertEqual(out.count(b"close_MaybeUninit_pointer_own"), count)
                self.assertLess(out.find(b"close_MaybeUninit_pointer_own") if count else 0,
                                out.index(REPAIR.FINAL_CALL))
                stripped = b"".join(l for l in out.splitlines(True)
                                    if not l.lstrip().startswith(b"/*@ std::mem::close_MaybeUninit_pointer_own"))
                self.assertEqual(stripped, UNIT)
        self.assertIn(b"(true_payload)", REPAIR.repair(UNIT, "true-only"))
        self.assertIn(b"(false_payload)", REPAIR.repair(UNIT, "false-only"))
        self.assertEqual(REPAIR.repair(UNIT, "none"), UNIT)

    def test_refusals(self):
        for bad in (UNIT.replace(REPAIR.FINAL_CALL, b""),
                    UNIT.replace(REPAIR.FINAL_CALL, REPAIR.FINAL_CALL * 2),
                    UNIT.replace(REPAIR.PAYLOAD_ASSERTS[0], b""),
                    UNIT.replace(REPAIR.PAYLOAD_ASSERTS[1], b"") ,
                    REPAIR.repair(UNIT, "both")):
            with self.subTest(size=len(bad)), self.assertRaises(RuntimeError):
                REPAIR.repair(bad, "both")
        moved = UNIT.replace(REPAIR.PAYLOAD_ASSERTS[1], b"").replace(
            REPAIR.FINAL_CALL, REPAIR.FINAL_CALL + REPAIR.PAYLOAD_ASSERTS[1])
        with self.assertRaises(RuntimeError):
            REPAIR.repair(moved, "both")
        with self.assertRaises(RuntimeError):
            REPAIR.repair(UNIT, "all")


if __name__ == "__main__":
    unittest.main()
