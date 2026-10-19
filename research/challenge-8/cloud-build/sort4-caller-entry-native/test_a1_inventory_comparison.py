"""Synthetic-only controls for normal/readonly compiler inventory comparison."""
import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).parent

def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

fixture = load("a1_inventory_comparison_fixture", "test_a1_compiler_inventory.py")
m = load("a1_inventory_comparison_inventory", "a1-compiler-inventory.py")


def with_body_fields(text, body_id, fields):
    paths = {12: "crate::default16::small_sort",
             22: "crate::freeze32::small_sort",
             11: "crate::default16::small_sort_threshold",
             21: "crate::freeze32::small_sort_threshold"}
    if body_id == 12:
        raw = fixture.body(body_id, paths[body_id], 6, 7, 101, 201)
    elif body_id == 22:
        raw = fixture.body(body_id, paths[body_id], 12, 13, 102, 202)
    elif body_id == 11:
        raw = fixture.body(body_id, paths[body_id], 4, 5)
    else:
        raw = fixture.body(body_id, paths[body_id], 10, 11)
    assert raw in text
    return text.replace(raw, raw[:-1] + ", " + fields + ")", 1)


def observe(normal, readonly=None):
    source = fixture.valid_source()
    return m.observe("P0a", normal, normal if readonly is None else readonly,
                     fixture.certificate(source), source)


class InventoryComparisonTests(unittest.TestCase):
    def test_operational_lists_may_differ_and_raw_values_remain(self):
        normal = fixture.stream()
        readonly = fixture.stream()
        normal = with_body_fields(normal, 12,
            'localDecls = ["normal-local"], basicBlocks = ["normal-bb"], varDebugInfo = ["normal-debug"]')
        readonly = with_body_fields(readonly, 12,
            'localDecls = ["readonly-local", "extra"], basicBlocks = ["readonly-bb"], varDebugInfo = ["readonly-debug"]')

        normal_shape = m._parse_inventory_input(normal, "normal")
        before = normal_shape["impls"][0]["items"][1]["body"]["record"]
        before_fields = before.fields
        comparison = m._inventory_comparison(normal_shape)
        after = normal_shape["impls"][0]["items"][1]["body"]["record"]
        self.assertEqual(after.fields, before_fields)
        normalized_record = comparison["impls"][0]["items"][1]["body"]["record"]
        for key in ("localDecls", "basicBlocks", "varDebugInfo"):
            self.assertEqual(m._one(normalized_record, key), m._parser.ListValue(()))

        result = observe(normal, readonly)
        self.assertFalse(result["proof_credit"])
        raw = result["inventory"]["impls"][0]["items"][1]["body"]["record"]
        self.assertEqual(m._one(raw, "localDecls").values[0], m._parser.Text("normal-local"))
        self.assertEqual(m._one(raw, "basicBlocks").values, (m._parser.Text("normal-bb"),))

    def test_each_operational_field_is_ignored_independently_on_both_body_kinds(self):
        for body_id in (11, 12):
            for field in ("localDecls", "basicBlocks", "varDebugInfo"):
                with self.subTest(body_id=body_id, field=field):
                    normal = with_body_fields(fixture.stream(), body_id,
                                              f'{field} = ["normal"]')
                    readonly = with_body_fields(fixture.stream(), body_id,
                                                f'{field} = ["readonly", "other"]')
                    result = observe(normal, readonly)
                    raw = result["inventory"]["impls"][0]["items"][0 if body_id == 11 else 1]["body"]["record"]
                    self.assertEqual(m._one(raw, field).values[0], m._parser.Text("normal"))

    def test_operational_field_presence_must_match_between_modes(self):
        normal = with_body_fields(fixture.stream(), 12, 'basicBlocks = ["bb"]')
        with self.assertRaisesRegex(m.InventoryError, "differ at .*"):
            observe(normal, fixture.stream())

    def test_operational_fields_must_be_unique_explicit_lists(self):
        base = fixture.stream()
        invalid = (
            with_body_fields(base, 12, 'localDecls = [], localDecls = []'),
            with_body_fields(base, 12, 'localDecls = null'),
            with_body_fields(base, 12, 'basicBlocks = (some = [])'),
            with_body_fields(base, 12, 'varDebugInfo = void'),
        )
        for text in invalid:
            with self.subTest(text=text[-160:]), self.assertRaises(m.InventoryError):
                shape = m._parse_inventory_input(text, "normal")
                m._inventory_comparison(shape)

    def test_unknown_and_visibility_fields_are_retained(self):
        normal = fixture.stream()
        readonly_unknown = with_body_fields(normal, 12, 'futureSemanticField = "one"')
        with self.assertRaisesRegex(m.InventoryError, "differ at .*"):
            observe(normal, readonly_unknown)
        same_unknown_shape_left = with_body_fields(normal, 12,
            'futureSemanticField = (annotation = true)')
        same_unknown_shape_right = with_body_fields(normal, 12,
            'futureSemanticField = (annotation = false)')
        with self.assertRaisesRegex(m.InventoryError, r"differ at .*futureSemanticField.annotation"):
            observe(same_unknown_shape_left, same_unknown_shape_right)
        readonly_visibility = with_body_fields(normal, 12, 'visibility = public')
        with self.assertRaisesRegex(m.InventoryError, "differ at .*"):
            observe(normal, readonly_visibility)

    def test_contract_annotation_values_are_compared_for_same_field_shape(self):
        base = fixture.stream()
        cases = (
            ('contract = (annotation = true)', 'contract = (annotation = false)'),
            ('contract = (annotation = "normal")', 'contract = (annotation = "readonly")'),
        )
        for normal_field, readonly_field in cases:
            normal = with_body_fields(base, 12, normal_field)
            readonly = with_body_fields(base, 12, readonly_field)
            with self.subTest(normal_field=normal_field), self.assertRaisesRegex(
                    m.InventoryError, r"differ at .*contract.annotation"):
                observe(normal, readonly)

    def test_first_difference_is_stable_and_bounded(self):
        left = m._parse_inventory_input(fixture.stream(), "normal")
        right = m._parse_inventory_input(
            with_body_fields(fixture.stream(), 12, 'futureSemanticField = "value"'), "readonly")
        a, b = m._inventory_comparison(left), m._inventory_comparison(right)
        first = m._first_difference(a, b)
        self.assertEqual(first, m._first_difference(a, b))
        self.assertTrue(first.startswith("inventory.impls[0].items[1].body.record"))
        self.assertLessEqual(len(first), 240)
        long_name = "nested_field_" * 80
        deep_left = m._parser.Record(((long_name,
            m._parser.Record(((long_name, m._parser.Text("left")),))),))
        deep_right = m._parser.Record(((long_name,
            m._parser.Record(((long_name, m._parser.Text("right")),))),))
        long_path = m._first_difference(deep_left, deep_right)
        self.assertLessEqual(len(long_path), 240)

    def test_nonoperational_contract_identity_inputs_and_clauses_stay_strict(self):
        source = fixture.valid_source()
        base = fixture.stream()
        changes = (
            base.replace('selfTy = "T"', 'selfTy = "U"', 1),
            base.replace('defIndex = 12, defPath = "crate::default16::small_sort"',
                         'defIndex = 99, defPath = "crate::default16::small_sort"', 1),
            base.replace('param = "T"', 'param = "U"', 1),
            base.replace('defId = "core::ops::FnMut"', 'defId = "core::ops::FnOnce"', 1),
        )
        for changed in changes:
            with self.subTest(change=changed[-100:]), self.assertRaises(m.InventoryError):
                observe(base, changed)
        unknown_left = with_body_fields(base, 12, 'mystery = true')
        unknown_right = with_body_fields(base, 12, 'mystery = false')
        with self.assertRaisesRegex(m.InventoryError, r"differ at .*mystery"):
            observe(unknown_left, unknown_right)

    def test_missing_partial_and_null_whole_streams_fail_closed(self):
        source = fixture.valid_source()
        cert = fixture.certificate(source)
        for bad in ("", "(traits = [], traitImpls = [])",
                    "(traits = null, traitImpls = null, bodies = null)"):
            with self.subTest(bad=bad), self.assertRaises(m.InventoryError):
                m.observe("P0a", bad, bad, cert, source)


if __name__ == "__main__":
    unittest.main()
