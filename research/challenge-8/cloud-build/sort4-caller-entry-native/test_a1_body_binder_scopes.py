"""Focused synthetic controls for impl small_sort Body binder scoping."""
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

# Reuse the established synthetic body text fixture, but parse it with the
# inventory's parser so Record class identity is exactly the one _ty expects.
fixture = load("a1_body_binder_inventory_fixture", "test_a1_compiler_inventory.py")
m = load("a1_body_binder_inventory", "a1-compiler-inventory.py")


def body_record(text=None):
    text = text or fixture.body(112, "crate::default16::small_sort", 6, 7, 101, 201)
    record = m._parser.parse_records(text)[0]
    return {"record": record, "def_path": "crate::default16::small_sort",
            "fn_sig_span": m._span(m._one(record, "fnSigSpan")),
            "mir_span": m._span(m._one(record, "span"))}


def canonical(text=None, impl_name="default16", expected_id=101):
    return m._impl_body_small_sort(body_record(text), impl_name, expected_id)


class BodyBinderScopeTests(unittest.TestCase):
    def test_baseline_body_contract_is_canonicalized(self):
        result = canonical()
        self.assertEqual(result["impl_generic_names"], ("T",))
        self.assertEqual(result["impl_generic_ids"], (101,))
        self.assertEqual(result["generic_names"], ("F",))
        self.assertEqual(result["generic_ids"], (201,))
        self.assertEqual(result["input_regions"], ("@input_0", "@input_1", "@input_2"))
        self.assertEqual(len(result["clauses"]), 3)
        self.assertEqual(len(result["digest"]), 64)

    def test_alpha_renaming_preserves_canonical_clauses_and_digest(self):
        original = fixture.body(112, "crate::default16::small_sort", 6, 7, 101, 201)
        renamed = original
        for old, new in (("ia", "input_left"), ("ib", "input_mid"),
                         ("ic", "input_right"), ("ha", "call_a"),
                         ("hb", "call_b"), ("oa", "out_a"), ("ob", "out_b")):
            renamed = renamed.replace(f'"{old}"', f'"{new}"')
        left, right = canonical(original), canonical(renamed)
        self.assertEqual(left["clauses"], right["clauses"])
        self.assertEqual(left["inputs"], right["inputs"])
        self.assertEqual(left["digest"], right["digest"])

    def test_reused_binder_spelling_has_distinct_clause_keys(self):
        text = fixture.body(112, "crate::default16::small_sort", 6, 7, 101, 201)
        text = text.replace('"ha"', '"same"').replace('"hb"', '"other"')
        text = text.replace('"oa"', '"same"').replace('"ob"', '"other"')
        # The same wire spelling denotes distinct binders because each clause
        # has its own binder scope and local slot.
        result, baseline = canonical(text), canonical()
        self.assertEqual(result["clauses"], baseline["clauses"])
        self.assertEqual(result["digest"], baseline["digest"])
        fn_regions = result["clauses"][1][3]
        output_regions = result["clauses"][2][3]
        self.assertEqual(fn_regions, (("body-clause", 112, 1, 0),
                                     ("body-clause", 112, 1, 1)))
        self.assertEqual(output_regions, (("body-clause", 112, 2, 0),
                                          ("body-clause", 112, 2, 1)))
        self.assertTrue(set(fn_regions).isdisjoint(output_regions))

    def test_wrong_impl_identity_or_generic_tables_rejected(self):
        text = fixture.body(112, "crate::default16::small_sort", 6, 7, 101, 201)
        with self.assertRaises(m.InventoryError):
            canonical(text, expected_id=102)
        with self.assertRaises(m.InventoryError):
            canonical(text.replace('defIndex = 201', 'defIndex = 101'))
        with self.assertRaises(m.InventoryError):
            canonical(text.replace('name = "F", index = 1', 'name = "G", index = 1'))
        with self.assertRaises(m.InventoryError):
            canonical(text.replace('defIndex = 112, defPath', 'defPath', 1))

    def test_wrong_input_or_clause_F_parameter_rejected(self):
        text = fixture.body(112, "crate::default16::small_sort", 6, 7, 101, 201)
        with self.assertRaises(m.InventoryError):
            canonical(text.replace('"F"', '"G"', 1))
        with self.assertRaises(m.InventoryError):
            canonical(text.replace('param = "F"', 'param = "T"', 1))
        with self.assertRaises(m.InventoryError):
            canonical(text.replace('param = "T"', 'param = "U"', 1))

    def test_input_region_collapse_and_capture_rejected(self):
        text = fixture.body(112, "crate::default16::small_sort", 6, 7, 101, 201)
        with self.assertRaises(m.InventoryError):
            canonical(text.replace('"ib"', '"ia"', 1))
        # Make a callable binder reference an input lifetime instead of its
        # clause-local binder while leaving boundRegions unchanged.
        with self.assertRaises(m.InventoryError):
            canonical(text.replace('"ha"', '"ia"', 1))
        with self.assertRaises(m.InventoryError):
            canonical(text.replace('"ha"', '"unbound"', 1))
        # Rename both the FnMut binder and its reference to an input region;
        # name-to-name resolution alone would accept this capture.
        fnmut = text.index('defId = "core::ops::FnMut"')
        output_clause = text.index('defId = "core::ops::FnOnce::Output"')
        captured_fnmut = text[:fnmut] + text[fnmut:output_clause].replace('"ha"', '"ia"') + text[output_clause:]
        with self.assertRaises(m.InventoryError):
            canonical(captured_fnmut)

    def test_missing_malformed_or_duplicate_callable_binders_rejected(self):
        text = fixture.body(112, "crate::default16::small_sort", 6, 7, 101, 201)
        mutations = (
            text.replace('boundRegions = ["ha", "hb"]', 'boundRegions = ["ha"]'),
            text.replace('boundRegions = ["ha", "hb"]', 'boundRegions = ["ha", "ha"]'),
            text.replace('boundRegions = ["ha", "hb"]', 'boundRegions = void'),
            text.replace(', boundRegions = ["ha", "hb"]', ''),
            text.replace('boundRegions = ["oa", "ob"]', 'boundRegions = ["oa", "oa"]'),
        )
        for malformed in mutations:
            with self.subTest(malformed=malformed[-100:]), self.assertRaises(m.InventoryError):
                canonical(malformed)

    def test_binder_position_must_match_reference_position(self):
        text = fixture.body(112, "crate::default16::small_sort", 6, 7, 101, 201)
        text = text.replace('boundRegions = ["ha", "hb"]',
                            'boundRegions = ["hb", "ha"]', 1)
        with self.assertRaises(m.InventoryError):
            canonical(text)

    def test_input_mutability_and_tuple_arity_are_exact(self):
        text = fixture.body(112, "crate::default16::small_sort", 6, 7, 101, 201)
        with self.assertRaises(m.InventoryError):
            canonical(text.replace('mutability = (mut = void)',
                                   'mutability = (not = void)', 1))
        second_binder_ref = ('(kind = (ref = (region = (id = "hb"), '
                             'ty = (kind = (param = "T")), mutability = (not = void))))')
        overlong = text.replace(second_binder_ref,
                                second_binder_ref + ', ' + second_binder_ref, 1)
        with self.assertRaises(m.InventoryError):
            canonical(overlong)

    def test_projection_output_type_and_presence_are_exact(self):
        text = fixture.body(112, "crate::default16::small_sort", 6, 7, 101, 201)
        with self.assertRaises(m.InventoryError):
            canonical(text.replace('(bool = void)', '(unit = void)', 1))
        with self.assertRaises(m.InventoryError):
            canonical(text.replace('projection = (projectionTerm = ',
                                   'trait = (defId = "core::marker::Send", args = [], boundRegions = []), projection = (projectionTerm = ', 1))


if __name__ == "__main__":
    unittest.main()
