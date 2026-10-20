"""Synthetic tests for required-method early type/Fresh HIR partitioning."""
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

fixture = load("a1_required_hir_fixture", "test_a1_compiler_inventory.py")
m = load("a1_required_hir_inventory", "a1-compiler-inventory.py")


def _span_field(span):
    if span == "missing":
        return ""
    value = fixture.span(line=2) if span == "regular" else span
    return f", span = {value}"


def plain_type(name="F", kind="type", *, pure="false", bounds="void", span="regular"):
    return (f'(kind = ({kind} = void), name = (plain = (name = (name = "{name}"))), '
            f'pureWrtDrop = {pure}, bounds = {bounds}{_span_field(span)})')


def fresh_lifetime(l, *, h=0, kind="lifetime", pure="false", bounds="void", span="regular"):
    return (f'(kind = ({kind} = void), name = (fresh = (h = {h}, l = {l})), '
            f'pureWrtDrop = {pure}, bounds = {bounds}{_span_field(span)})')


def method_record(params=None, *, hir_value=None, duplicate_hir=False):
    text = fixture.required("small_sort", 71)
    if params is not None:
        hir_value = '(params = [' + ', '.join(params) + '])'
    if hir_value is not None:
        text = text[:-1] + ', hirGenerics = ' + hir_value + ')'
        if duplicate_hir:
            text = text[:-1] + ', hirGenerics = ' + hir_value + ')'
    return m._parser.parse_records(text)[0]


def validate(params=None, **kwargs):
    return m._required_small_sort([method_record(params, **kwargs)])


class RequiredHirPartitionTests(unittest.TestCase):
    def test_optional_absent_and_valid_fresh_alpha_metadata_do_not_change_semantics(self):
        absent = validate()
        self.assertEqual(absent["ast_type_param_names"], ("Self", "F"))
        first = validate([plain_type(), fresh_lifetime(101), fresh_lifetime(102), fresh_lifetime(103)])
        second = validate([plain_type(), fresh_lifetime(701), fresh_lifetime(702), fresh_lifetime(703)])
        for key in ("inputs", "clauses", "parent_clauses", "signature_regions",
                    "hrtb_regions", "scoped_regions", "alpha_roles"):
            self.assertEqual(first[key], second[key])
        self.assertEqual(first["inputs"], absent["inputs"])
        self.assertEqual(first["clauses"], absent["clauses"])

    def test_type_and_fresh_partition_must_be_ordered_exactly(self):
        valid = [plain_type(), fresh_lifetime(101), fresh_lifetime(102), fresh_lifetime(103)]
        malformed = (
            [plain_type(kind="const"), *valid[1:]],
            [fresh_lifetime(101), plain_type(), fresh_lifetime(102), fresh_lifetime(103)],
            [plain_type(), plain_type("G"), *valid[1:]],
            [plain_type(), *valid[1:3]],
            [plain_type(), *valid[1:], fresh_lifetime(104)],
            [plain_type(), fresh_lifetime(101), plain_type(), fresh_lifetime(103)],
            [plain_type(), plain_type("F"), fresh_lifetime(102), fresh_lifetime(103)],
        )
        for params in malformed:
            with self.subTest(params=params), self.assertRaises(m.InventoryError):
                validate(params)

    def test_fresh_metadata_shape_flags_and_identities_fail_closed(self):
        valid = [plain_type(), fresh_lifetime(101), fresh_lifetime(102), fresh_lifetime(103)]
        malformed = (
            [*valid[:3], '(kind = (lifetime = void), name = (fresh = (h = 0, l = 103)))'],
            [plain_type(), fresh_lifetime(101), fresh_lifetime(101), fresh_lifetime(103)],
            [plain_type(), fresh_lifetime(0), fresh_lifetime(102), fresh_lifetime(103)],
            [plain_type(), fresh_lifetime(101, h=1), fresh_lifetime(102), fresh_lifetime(103)],
            [plain_type(), fresh_lifetime(101), fresh_lifetime(102, pure="true"), fresh_lifetime(103)],
            [plain_type(), fresh_lifetime(101), fresh_lifetime(102), fresh_lifetime(103, bounds="[]")],
            [plain_type(), fresh_lifetime(101), fresh_lifetime(102), fresh_lifetime(1 << 64)],
            [plain_type(), fresh_lifetime(101), fresh_lifetime('"102"'), fresh_lifetime(103)],
            [plain_type(), fresh_lifetime(101), fresh_lifetime(102, kind="const"), fresh_lifetime(103)],
            [plain_type(), plain_type("F"), fresh_lifetime(102), fresh_lifetime(103)],
        )
        for params in malformed:
            with self.subTest(params=params), self.assertRaises(m.InventoryError):
                validate(params)

    def test_missing_null_duplicate_and_partial_hir_metadata_rejected(self):
        for kwargs in (
            {"hir_value": "null"},
            {"hir_value": "(params = null)"},
            {"hir_value": "(params = [(kind = (type = void))])"},
            {"params": [plain_type(), fresh_lifetime(101), fresh_lifetime(102), fresh_lifetime(103)],
             "duplicate_hir": True},
        ):
            with self.subTest(kwargs=kwargs), self.assertRaises(m.InventoryError):
                validate(**kwargs)

    def test_each_present_hir_parameter_requires_a_regular_span(self):
        bad_span_values = ("missing", "(dummy = void)", "null")
        for bad_span in bad_span_values:
            for position in range(4):
                params = [plain_type(), fresh_lifetime(101), fresh_lifetime(102), fresh_lifetime(103)]
                params[position] = (plain_type(span=bad_span) if position == 0 else
                                    fresh_lifetime(100 + position, span=bad_span))
                with self.subTest(span=bad_span, position=position), self.assertRaises(m.InventoryError):
                    validate(params)

    def test_threshold_hir_partition_has_no_type_or_fresh_parameters(self):
        text = fixture.required("small_sort_threshold", 70)
        empty_hir = m._parser.parse_records(text[:-1] + ', hirGenerics = (params = []))')[0]
        self.assertIsNone(m._required_hir_partition(empty_hir, (), 0))
        for params in ([plain_type()], [fresh_lifetime(101)]):
            malformed = m._parser.parse_records(
                text[:-1] + ', hirGenerics = (params = [' + ', '.join(params) + ']))')[0]
            with self.subTest(params=params), self.assertRaises(m.InventoryError):
                m._required_hir_partition(malformed, (), 0)

    def test_valid_hir_metadata_does_not_weaken_signature_or_fnmut_clause_checks(self):
        valid_hir = [plain_type(), fresh_lifetime(101), fresh_lifetime(102), fresh_lifetime(103)]
        text = fixture.required("small_sort", 71)
        with_hir = text[:-1] + ', hirGenerics = (params = [' + ', '.join(valid_hir) + ']))'
        wrong_input = with_hir.replace('param = "tp_f"', 'param = "tp_self"', 1)
        with self.assertRaises(m.InventoryError):
            m._required_small_sort([m._parser.parse_records(wrong_input)[0]])

        fnmut = with_hir.index('defId = "core::ops::FnMut"')
        output = with_hir.index('defId = "core::ops::FnOnce::Output"', fnmut)
        wrong_clause = (with_hir[:fnmut] +
                        with_hir[fnmut:output].replace('param = "tp_f"', 'param = "tp_self"', 1) +
                        with_hir[output:])
        with self.assertRaises(m.InventoryError):
            m._required_small_sort([m._parser.parse_records(wrong_clause)[0]])


if __name__ == "__main__":
    unittest.main()
