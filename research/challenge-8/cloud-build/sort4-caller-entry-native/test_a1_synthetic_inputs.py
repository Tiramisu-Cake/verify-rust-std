"""Synthetic-only controls for a1-synthetic-inputs.py; no proof imports."""
import importlib.util
from pathlib import Path
import sys
import unittest

PATH = Path(__file__).with_name("a1-synthetic-inputs.py")
SPEC = importlib.util.spec_from_file_location("a1_synthetic_inputs", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

BASE = r'''
(
  name = "StableSmallSortTypeImpl",
  requiredFns = (cons = (h = (
      name = "small_sort_threshold", scopedRepresentation = true,
      inputs = [], output = (uint = u64), typeParams = [], scopedRegions = [],
      clauses = [], unknownEnum = RetainMe
    ), t = (cons = (h = (
      name = "small_sort", scopedRepresentation = true,
      defId = "crate::StableSmallSortTypeImpl::small_sort", defIndex = 42,
      parentDefId = "StableSmallSortTypeImpl", parentDefIndex = 7,
      inputs = [
        (ref = (region = (id = "r1"), mutable = true, pointee = SelfSlice)),
        (ref = (region = (id = "r2"), mutable = true, pointee = ScratchSelf)),
        (ref = (region = (id = "r3"), mutable = true, pointee = F))
      ],
      lifetimeParams = ["r1", "r2", "r3"],
      output = (tuple = []),
      typeParams = [
        (alias = "__type_self", index = 0, defIndex = 100, name = "Self"),
        (alias = "__type_f", index = 1, defIndex = 101, name = "F")
      ],
      hirGenerics = (params = [(name = "F", kind = type, index = 1, defIndex = 101)]),
      generics = [(name = "F", kind = type, index = 1, defIndex = 101)],
      scopedRegions = [
        (alias = "r1", scope = "sig", depth = 0, index = 0, kind = "anon", elidedRole = true),
        (alias = "r2", scope = "sig", depth = 0, index = 1, kind = "anon", elidedRole = true),
        (alias = "r3", scope = "sig", depth = 0, index = 2, kind = "anon", elidedRole = true),
        (alias = "c0", scope = "clause_0", depth = 0, index = 0, kind = "named", elidedRole = false),
        (alias = "c1", scope = "clause_0", depth = 0, index = 1, kind = "named", elidedRole = false),
        (alias = "c2", scope = "clause_1", depth = 0, index = 0, kind = "named", elidedRole = false),
        (alias = "c3", scope = "clause_1", depth = 0, index = 1, kind = "named", elidedRole = false)
      ],
      clauses = [
        (trait = (defId = "std::ops::FnMut", boundRegions = ["c0", "c1"], args = [F])),
        (projection = (projectionTerm = (defId = "std::ops::FnOnce::Output", args = [F]),
                       boundRegions = ["c2", "c3"], term = Bool))
      ],
      parentClauses = [],
      unknownField = "quoted enum-looking value: safe"
    ), t = (nil = void))))),
  futureField = [futureEnum, "futureEnum"]
)
(
  ofTrait = "StableSmallSortTypeImpl", defIndex = 900, selfTy = "Vec<T>",
  items = [
    (name = "small_sort", defId = "impl::small_sort", defIndex = 900),
    (name = "small_sort_threshold", defId = "impl::threshold", defIndex = 901)
  ]
)
(
  ofTrait = "StableSmallSortTypeImpl", defIndex = 901, selfTy = "[T]",
  items = [
    (name = "small_sort", defId = "freeze_impl::small_sort", defIndex = 910),
    (name = "small_sort_threshold", defId = "freeze_impl::threshold", defIndex = 911)
  ]
)
(
  consumerUses = ["small_sort", "StableSmallSortTypeImpl::small_sort"]
)
'''
_raw_records = MODULE.parse_records(BASE)
BASE = MODULE.render_records((MODULE.Record((
    ("traits", MODULE._render_indlist((_raw_records[0],))),
    ("traitImpls", MODULE.ListValue(_raw_records[1:3])),
    ("consumer", _raw_records[3]),
)),))


def target(records):
    return MODULE._find_target(records, "StableSmallSortTypeImpl", "small_sort")[5]


def inputs(method):
    return MODULE._one(method, "inputs")


class CapnpTextParserTests(unittest.TestCase):
    def test_roundtrip_all_records_and_scalar_kinds(self):
        records = MODULE.parse_records(BASE)
        rendered = MODULE.render_records(records)
        self.assertEqual(MODULE.parse_records(rendered), records)
        self.assertEqual(len(records), 1)
        method = target(records)
        self.assertIsInstance(MODULE._one(method, "scopedRepresentation"), MODULE.Atom)
        self.assertIsInstance(MODULE._one(method, "unknownField"), MODULE.Text)
        self.assertEqual(MODULE._one(method, "unknownField").value, "quoted enum-looking value: safe")
        self.assertIn("futureEnum", rendered)

    def test_duplicate_fields_are_retained_then_rejected_by_shape_access(self):
        records = MODULE.parse_records('(name = "a", name = enumA, unknown = mystery)')
        self.assertEqual(len(records[0].fields), 3)
        with self.assertRaises(MODULE.ShapeError):
            MODULE._one(records[0], "name")

    def test_bad_top_level_and_ambiguous_records_fail_closed(self):
        with self.assertRaises(MODULE.ParseError):
            MODULE.parse_records('[ (name = "not-a-top-level-record") ]')
        duplicate = BASE.replace('name = "small_sort", scopedRepresentation',
                                 'name = "small_sort", name = "small_sort", scopedRepresentation', 1)
        with self.assertRaises(MODULE.ShapeError):
            MODULE.mutate_required_fn(duplicate, "alpha_valid")
        records = MODULE.parse_records(BASE)
        ri, root, root_path, methods, fi, method, method_path = MODULE._find_target(
            records, "StableSmallSortTypeImpl", "small_sort")
        duplicate_methods = (*methods, method)
        new_root = MODULE._replace_field(root, "requiredFns",
                                         MODULE._render_indlist(duplicate_methods))
        two_methods = MODULE.render_records(MODULE._replace_at_path(records, ri, root_path, new_root))
        with self.assertRaises(MODULE.ShapeError):
            MODULE.mutate_required_fn(two_methods, "alpha_valid")

    def test_wrong_target_is_not_fuzzily_retargeted(self):
        with self.assertRaises(MODULE.ShapeError):
            MODULE.mutate_required_fn(BASE, "alpha_valid", target_fn="small_sort_threshold")
        with self.assertRaises(MODULE.ShapeError):
            MODULE.mutate_required_fn(BASE.replace('name = "StableSmallSortTypeImpl"',
                                                   'name = "OtherTrait"', 1), "alpha_valid")

    def test_nested_root_record_can_be_mutated_without_touching_siblings(self):
        records = MODULE.parse_records(BASE)
        wrapped = (MODULE.Record((("payload", records[0]),)),)
        text = MODULE.render_records(wrapped)
        mutated, _ = MODULE.mutate_required_fn(text, "alpha_valid")
        result = MODULE.parse_records(mutated)
        self.assertEqual(len(result), 1)
        root = MODULE._one(result[0], "payload")
        self.assertIsInstance(root, MODULE.Record)
        self.assertEqual(MODULE._text(target((root,)), "name"), "small_sort")


class SyntheticMutationsTests(unittest.TestCase):
    def mutate(self, case):
        text, metadata = MODULE.mutate_required_fn(BASE, case)
        self.assertTrue(metadata["synthetic"])
        self.assertEqual(metadata["provenance"], "none")
        self.assertFalse(metadata["compiler_derived"])
        self.assertFalse(metadata["translator_derived"])
        self.assertFalse(metadata["refinement_derived"])
        self.assertFalse(metadata["proof_credit"])
        return MODULE.parse_records(text), metadata

    def test_binder_collapse_duplicates_semantic_scope_index(self):
        records, _ = self.mutate("binder_collapse")
        rows = MODULE._alias_rows(target(records))
        sig = [index for _, scope, depth, index in rows if scope == "sig" and depth == 0]
        self.assertLess(len(set(sig)), len(sig))

    def test_alpha_valid_renames_binders_and_all_method_references_bijectively(self):
        original_records = MODULE.parse_records(BASE)
        before = target(MODULE.parse_records(BASE))
        after_records, metadata = self.mutate("alpha_valid")
        after = target(after_records)
        old = {alias for alias, _, _, _ in MODULE._alias_rows(before)}
        new = {alias for alias, _, _, _ in MODULE._alias_rows(after)}
        self.assertEqual(len(old), len(new))
        self.assertTrue(all(alias.startswith("'__a1_alpha_") for alias in new))
        self.assertFalse(old.intersection(new))
        self.assertIn("semantic_provenance", metadata)
        self.assertTrue(metadata["semantic_metadata_unchanged"])
        self.assertEqual(set(metadata["alpha_alias_bijection"]), old)
        self.assertEqual(metadata["scoped_region_rows_before"], len(old))
        old_lifetimes = MODULE._one(before, "lifetimeParams")
        new_lifetimes = MODULE._one(after, "lifetimeParams")
        mapping = metadata["alpha_alias_bijection"]
        self.assertEqual(new_lifetimes, MODULE.ListValue(
            tuple(MODULE.Text(mapping[value.value]) for value in old_lifetimes.values)))
        self.assertEqual(MODULE._one(after, "unknownField"),
                         MODULE._one(before, "unknownField"))
        self.assertEqual(MODULE.parse_records(BASE), original_records)

    def test_free_input_region_is_unbound(self):
        records, _ = self.mutate("free_region_input")
        method = target(records)
        refs = MODULE._region_refs(inputs(method), {a for a, _, _, _ in MODULE._alias_rows(method)})
        self.assertNotIn("__a1_free_region", refs)
        rendered_method = MODULE.render_value(method)
        self.assertIn("__a1_free_region", rendered_method)

    def test_input_region_swap_changes_refs_but_not_binding_table(self):
        old = target(MODULE.parse_records(BASE))
        rows, _ = self.mutate("input_region_swap")
        new = target(rows)
        old_inputs = MODULE._region_refs(inputs(old), {"r1", "r2", "r3"})
        new_inputs = MODULE._region_refs(inputs(new), {"r1", "r2", "r3"})
        self.assertEqual(old_inputs, ["r1", "r2", "r3"])
        self.assertEqual(new_inputs, ["r2", "r1", "r3"])
        self.assertEqual(MODULE._one(old, "scopedRegions"), MODULE._one(new, "scopedRegions"))

    def test_missing_F_declaration_keeps_trait_impl_and_uses(self):
        rows, metadata = self.mutate("no_F")
        trait_rows = MODULE._records(MODULE._one(rows[0], "traits"), "traits")
        self.assertEqual(len(trait_rows), 1)
        root = trait_rows[0]
        retained = next(row for row in MODULE._records(MODULE._one(root, "requiredFns"), "requiredFns")
                        if MODULE._text(row, "name") == "small_sort")
        self.assertFalse(any(MODULE._text(row, "name") == "F"
                             for row in MODULE._records(MODULE._one(retained, "generics"), "generics")))
        self.assertFalse(any(MODULE._text(row, "name") == "F"
                             for row in MODULE._records(MODULE._one(MODULE._one(retained, "hirGenerics"), "params"),
                                                        "hirGenerics.params")))
        self.assertTrue(any(MODULE._text(row, "name") == "F"
                            for row in MODULE._records(MODULE._one(retained, "typeParams"), "typeParams")))
        self.assertTrue(metadata["required_method_retained"])
        self.assertEqual(metadata["removed_generic"], "F")
        self.assertEqual(len(MODULE._records(MODULE._one(rows[0], "traitImpls"), "traitImpls")), 2)
        self.assertIn('"StableSmallSortTypeImpl::small_sort"', MODULE.render_records(rows))

    def test_fnmut_and_output_clauses_can_be_removed_or_changed(self):
        for mutation, omitted in (("remove_fnmut", "std::ops::FnMut"),
                                  ("remove_output", "std::ops::FnOnce::Output")):
            with self.subTest(mutation=mutation):
                rows, _ = self.mutate(mutation)
                clauses = MODULE._records(MODULE._one(target(rows), "clauses"), "clauses")
                ids = [MODULE._clause_kind(row)[1] for row in clauses]
                self.assertFalse(any(value.endswith(omitted) for value in ids))
                method = target(rows)
                scoped = MODULE._alias_rows(method)
                self.assertEqual({scope for _, scope, _, _ in scoped}, {"sig", "clause_0"})
                remaining_clause = clauses[0]
                remaining_aliases = {alias for alias, scope, _, _ in scoped
                                     if scope == "clause_0"}
                self.assertTrue(MODULE._region_refs(remaining_clause, remaining_aliases))
                all_refs = set()
                all_aliases = {alias for alias, _, _, _ in scoped}
                for field in ("inputs", "output", "clauses", "parentClauses",
                              "hirGenerics", "generics", "typeParams", "lifetimeParams", "contract"):
                    value = MODULE._one(method, field, required=False)
                    if value is not None:
                        all_refs.update(MODULE._region_refs(value, all_aliases))
                self.assertTrue(remaining_aliases.issubset(all_refs))
        for mutation in ("change_fnmut", "change_output"):
            with self.subTest(mutation=mutation):
                rows, _ = self.mutate(mutation)
                clauses = MODULE._records(MODULE._one(target(rows), "clauses"), "clauses")
                self.assertTrue(any("A1SyntheticChanged" in MODULE.render_value(row) for row in clauses))

    def test_duplicate_impl_method_record_is_preserved_as_duplicate(self):
        text, metadata = MODULE.mutate_required_fn(BASE, "duplicate_impl_method", impl_def_index=900)
        rows = MODULE.parse_records(text)
        impls = MODULE._records(MODULE._one(rows[0], "traitImpls"), "traitImpls")
        counts = [sum(MODULE._text(item, "name") == "small_sort"
                      for item in MODULE._records(MODULE._one(impl, "items"), "items"))
                  for impl in impls]
        self.assertEqual(counts, [2, 1])
        self.assertEqual(len(impls), 2)
        self.assertTrue(metadata["both_impls_present"])
        with self.assertRaises(MODULE.ShapeError):
            MODULE.mutate_required_fn(BASE, "duplicate_impl_method")

    def test_unknown_missing_and_ambiguous_shapes_fail_closed(self):
        records = MODULE.parse_records(BASE)
        ri, _, _, _, _, method, method_path = MODULE._find_target(
            records, "StableSmallSortTypeImpl", "small_sort")
        malformed = MODULE._replace_field(method, "scopedRegions", None)
        missing_regions = MODULE.render_records(
            MODULE._replace_at_path(records, ri, method_path, malformed))
        with self.assertRaises((MODULE.ShapeError, MODULE.ParseError)):
            MODULE.mutate_required_fn(missing_regions, "binder_collapse")
        with self.assertRaises(MODULE.ShapeError):
            MODULE.mutate_required_fn(BASE, "unknown_mutation")


if __name__ == "__main__":
    unittest.main()
