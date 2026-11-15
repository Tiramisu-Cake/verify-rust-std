# Copyright Kani Contributors
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Synthetic tests for the bounded B3 T1b dump analyzer."""

import importlib.util
import pathlib
import sys
import unittest


MODULE = pathlib.Path("/root/kani-b3-t1/.github/b3-t1b/analysis.py")
SPEC = importlib.util.spec_from_file_location("b3_t1b_analysis", MODULE)
analysis = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = analysis
SPEC.loader.exec_module(analysis)


WRAPPER = "tag-_ab12::zst_array"


def symbol_dump(payload: str, *, symbol: str = WRAPPER,
                pretty: str = "main::ArrayUnion::zst_array",
                padding: str = "unsigned long int zst_array_padding;",
                extra: str = "", prefix: str = "\nSymbols:\n\n",
                include_unit: bool = True,
                unit_type: str = "struct Unit { }") -> str:
    text = prefix + (
        f"Symbol......: {symbol}\n"
        f"Pretty name.: {pretty}\n"
        "Module......: demo\n"
        f"Base name...: {symbol.removeprefix('tag-')}\n"
        "Mode........: C\n"
        f"Type........: struct {symbol.removeprefix('tag-')} {{ {payload}; {padding} }}\n"
        "Value.......: \n"
        "Flags.......: type\n"
        "Location....: \n\n"
        + extra
    )
    if include_unit:
        text += ("Symbol......: tag-Unit\nPretty name.: ()\nModule......: demo\n"
                 f"Base name...: Unit\nMode........: C\nType........: {unit_type}\n"
                 "Flags.......: type\nLocation....: \n\n")
    return text


OLD = "struct Unit zst_array[2]"
NEW = "struct Unit zst_array"


class AnalysisTests(unittest.TestCase):
    def test_allocid_aliases_are_consistent_by_first_occurrence(self):
        text = "x AllocId(89, ThreadLocalIndex), y AllocId(4, ThreadLocalIndex), x AllocId(89, ThreadLocalIndex)"
        self.assertEqual(
            analysis.normalize(text),
            "x AllocId(0, ThreadLocalIndex), y AllocId(1, ThreadLocalIndex), x AllocId(0, ThreadLocalIndex)",
        )

    def test_normalizer_leaves_other_text_and_allocid_spellings_unchanged(self):
        text = "AllocId(3, ThreadLocalIndex) AllocId(3, Other) AllocId(3, ThreadLocalIndex )"
        self.assertEqual(
            analysis.normalize(text),
            "AllocId(0, ThreadLocalIndex) AllocId(3, Other) AllocId(3, ThreadLocalIndex )",
        )

    def test_meaningful_symbol_changes_survive_normalization(self):
        self.assertNotEqual(analysis.normalize("x AllocId(8, ThreadLocalIndex)"),
                            analysis.normalize("y AllocId(8, ThreadLocalIndex)"))

    def test_valid_control(self):
        result = analysis.control(symbol_dump(OLD), symbol_dump(NEW), "function f\n", "function f\n")
        self.assertTrue(result["valid"], result["reason"])

    def test_control_rejects_function_change(self):
        result = analysis.control(symbol_dump(OLD), symbol_dump(NEW), "function f\n", "function g\n")
        self.assertFalse(result["valid"])

    def test_control_pretty_name_must_match_exact_union_path(self):
        result = analysis.control(symbol_dump(OLD, pretty="main::OtherArrayUnion::zst_array"),
                                  symbol_dump(NEW, pretty="main::OtherArrayUnion::zst_array"), "f", "f")
        self.assertFalse(result["valid"])

    def test_control_rejects_change_outside_wrapper(self):
        changed = symbol_dump(NEW) + "Symbol......: unrelated\nType........: int\n"
        self.assertFalse(analysis.control(symbol_dump(OLD), changed, "f", "f")["valid"])

    def test_control_rejects_wrong_direction(self):
        self.assertFalse(analysis.control(symbol_dump(NEW), symbol_dump(OLD), "f", "f")["valid"])

    def test_control_rejects_padding_change(self):
        self.assertFalse(analysis.control(symbol_dump(OLD), symbol_dump(NEW, padding="unsigned int zst_array_padding;"), "f", "f")["valid"])

    def test_control_rejects_wrong_array_length(self):
        self.assertFalse(analysis.control(symbol_dump("struct Unit zst_array[3]"), symbol_dump(NEW), "f", "f")["valid"])

    def test_control_rejects_reordered_padding(self):
        reordered = symbol_dump(NEW).replace(
            "struct Unit zst_array; unsigned long int zst_array_padding;",
            "unsigned long int zst_array_padding; struct Unit zst_array;",
        )
        self.assertFalse(analysis.control(symbol_dump(OLD), reordered, "f", "f")["valid"])

    def test_control_rejects_whitespace_change_outside_payload(self):
        changed = symbol_dump(NEW).replace("; unsigned long int", ";  unsigned long int")
        self.assertFalse(analysis.control(symbol_dump(OLD), changed, "f", "f")["valid"])

    def test_control_rejects_missing_padding(self):
        self.assertFalse(analysis.control(symbol_dump(OLD), symbol_dump(NEW, padding=""), "f", "f")["valid"])

    def test_function_change_classification_wins_for_mixed_changes(self):
        result = analysis.classify(symbol_dump(OLD), symbol_dump(NEW), "f() { SKIP; }", "f() { ASSIGN x := 1; }")
        self.assertEqual(result["class"], "FUNCTION_CHANGES")
        self.assertEqual(result["symbol_class"], "WRAPPER_ONLY")

    def test_wrapper_only_classification_uses_control_gate(self):
        result = analysis.classify(symbol_dump(OLD), symbol_dump(NEW), "f", "f")
        self.assertEqual(result["class"], "WRAPPER_ONLY")

    def test_unknown_symbol_change_is_other(self):
        result = analysis.classify(symbol_dump("int zst_array"), symbol_dump("unsigned char zst_array"), "f", "f")
        self.assertEqual(result["class"], "OTHER_CHANGES")

    def test_equal(self):
        result = analysis.classify(symbol_dump(OLD), symbol_dump(OLD), "same", "same")
        self.assertEqual(result["class"], "EQUAL")

    def test_general_wrapper_census_accepts_multiple_mangled_symbols(self):
        a = symbol_dump(OLD) + symbol_dump("struct Unit other_arm[4]", symbol="tag-_cd34::other_arm", pretty="demo::Other::other_arm", padding="unsigned int other_arm_padding", include_unit=False)
        b = symbol_dump(NEW) + symbol_dump(NEW.replace("zst_array", "other_arm"), symbol="tag-_cd34::other_arm", pretty="demo::Other::other_arm", padding="unsigned int other_arm_padding", include_unit=False)
        result = analysis.classify(a, b, "functions", "functions")
        self.assertEqual(result["class"], "WRAPPER_ONLY")
        self.assertEqual(result["symbols"], [WRAPPER, "tag-_cd34::other_arm"])

    def test_prefix_and_suffix_are_preserved(self):
        a = symbol_dump(OLD, prefix="preamble A\n")
        b = symbol_dump(NEW, prefix="preamble B\n")
        self.assertEqual(analysis.classify(a, b, "f", "f")["class"], "OTHER_CHANGES")

    def test_pretty_name_changes_are_preserved(self):
        a, b = symbol_dump(OLD), symbol_dump(NEW, pretty="other::ArrayUnion::zst_array")
        self.assertEqual(analysis.classify(a, b, "f", "f")["class"], "OTHER_CHANGES")

    def test_duplicate_metadata_field_is_rejected(self):
        a = symbol_dump(OLD)
        b = symbol_dump(NEW).replace("Pretty name.: main::ArrayUnion::zst_array\n",
                                     "Pretty name.: main::ArrayUnion::zst_array\nPretty name.: altered\n")
        self.assertEqual(analysis.classify(a, b, "f", "f")["class"], "OTHER_CHANGES")

    def test_nested_empty_struct_proves_zero_width_payload(self):
        zst = "Symbol......: tag-Zst\nPretty name.: Zst\nModule......: demo\nBase name...: Zst\nMode........: C\nType........: struct Zst { }\nFlags.......: type\nLocation....: \n\n"
        old = symbol_dump("struct Zst zst_array", extra=zst)
        new = symbol_dump(NEW, extra=zst)
        self.assertEqual(analysis.classify(old, new, "f", "f")["class"], "WRAPPER_ONLY")

    def test_nonempty_unit_symbol_is_not_zero_width(self):
        old = symbol_dump(OLD)
        new = symbol_dump(NEW, unit_type="struct Unit { unsigned char byte; }")
        self.assertEqual(analysis.classify(old, new, "f", "f")["class"], "OTHER_CHANGES")


if __name__ == "__main__":
    unittest.main()
