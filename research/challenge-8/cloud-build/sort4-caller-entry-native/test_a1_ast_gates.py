"""Synthetic parser controls only; no compiler or proof artifact is read."""
import importlib.util
from pathlib import Path
import unittest
import hashlib
import json


path = Path(__file__).with_name("a1-ast-gates.py")
spec = importlib.util.spec_from_file_location("a1_ast_gates", path)
assert spec is not None and spec.loader is not None
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
runner_spec = importlib.util.spec_from_file_location(
    "a1_runner_parser_controls", path.with_name("a1-runner.py"))
assert runner_spec is not None and runner_spec.loader is not None
runner = importlib.util.module_from_spec(runner_spec)
runner_spec.loader.exec_module(runner)
import test_a1_compiler_inventory as inventory_fixture


def loc(line, *, endline=None, startcol=1, endcol=61):
    endline = endline or line
    return f'loc "verified/lib.rs({line},{startcol}-{endline},{endcol})"'


def variable(line, name):
    return f'Var ({loc(line)}, "{name}")'


def literal(line, number):
    return f'IntLit ({loc(line)}, big_int_of_string "{number}", true, false, NoLSuffix)'


def checked_range(line, result="r"):
    low = f'Operation ({loc(line)}, Le, [{literal(line, 16)}; {variable(line, result)}])'
    high = f'Operation ({loc(line)}, Le, [{variable(line, result)}; {literal(line, 32)}])'
    return f'Operation ({loc(line)}, And, [{low}; {high}])'


def post(line, checked, *, extra_arm=False, bad_unwind=False):
    token = f'CallExpr ({loc(line)}, "thread_token", [], [], [], Static)'
    rights = f'CallExpr ({loc(line)}, "raw_rights", [], [], [], Static)'
    native = f'Sep ({loc(line)}, {token}, {rights})'
    returning = f'Sep ({loc(line)}, {native}, {checked_range(line)})' if checked else native
    unwind = checked_range(line) if bad_unwind else native
    arms = (f'SwitchExprClause ({loc(line)}, "returning", ["r"], {returning}); '
            f'SwitchExprClause ({loc(line)}, "unwinding", [], {unwind})')
    if extra_arm:
        arms += f'; SwitchExprClause ({loc(line)}, "other", [], {native})'
    return (f'SwitchExpr ({loc(line)}, {variable(line, "out")}, '
            f'[{arms}], None)')


def func(line, name, checked, *, body=False, extra_arm=False, bad_unwind=False):
    spec = (f'Some ((True ({loc(line)}), '
            f'("out", {post(line, checked, extra_arm=extra_arm, bad_unwind=bad_unwind)})))')
    body_field = f'Some (([], {loc(line)}))' if body else 'None'
    tparam = 'Self' if name == gate.COMMON else 'T'
    return (f'Func ({loc(line)}, Regular, [("{tparam}", (true))], '
            f'Some (ConstructedTypeExpr ({loc(line)}, "fn_outcome", '
            f'[ManifestTypeExpr ({loc(line)}, Int (Unsigned, PtrRank))])), '
            f'"{name}", [], false, (None, None), {spec}, false, '
            f'{body_field}, false, [])')


INVENTORY = {
    "default16": {"compiler_impl_id": "11", "compiler_item_id": "12", "source_line": 30,
                  "diagnostic_post_line": 29},
    "freeze32": {"compiler_impl_id": "21", "compiler_item_id": "22", "source_line": 40,
                 "diagnostic_post_line": 39},
}


def all_functions(common_checked=False, **changes):
    common = func(20, gate.COMMON, common_checked)
    default = "__a1_impl_11_item_12_small_sort_threshold"
    freeze = "__a1_impl_21_item_22_small_sort_threshold"
    rows = [common,
            func(30, default, True, **changes), func(30, default, True, body=True),
            func(40, freeze, True), func(40, freeze, True, body=True),
            # The complete source also translates the two original small_sort
            # implementation bodies. They are independently inventoried.
            func(50, "__a1_impl_11_item_13_small_sort", False, body=True),
            func(60, "__a1_impl_21_item_23_small_sort", False, body=True)]
    return "\n".join(rows)


def caller_func(name, line, call_line, *, small_sort=False, alias=False):
    t = f'IdentTypeExpr ({loc(call_line)}, None, "T")'
    f = f'IdentTypeExpr ({loc(call_line)}, None, "F")'
    lifetime = f'IdentTypeExpr ({loc(call_line)}, None, "erased")'
    callee = "__a1_impl_11_item_12_small_sort_threshold" if alias else gate.COMMON
    calls = [f'CallExpr ({loc(call_line)}, "{callee}", [{t}], [], [], Static)']
    if small_sort:
        args = '; '.join(f'LitPat ({variable(call_line, name)})'
                         for name in ("$tmp_v", "$tmp_scratch", "$tmp_cmp"))
        calls.append(f'CallExpr ({loc(call_line + 1)}, "{gate.SMALL_SORT}", '
                     f'[{t}; {f}; {lifetime}; {lifetime}; {lifetime}], [], [{args}], Static)')
    body = '; '.join(calls)
    return (f'Func ({loc(line)}, Regular, [], None, "{name}", [], false, '
            f'(None, None), None, false, Some (([{body}], {loc(line)})), false, [])')


def small_sort_func(name, line, *, body=False, impl_self="Self",
                    scratch_name="scratch",
                    drop_resource=False, drop_unwind=False, substitute=False,
                    mix_region=False, drop_outcome=False, return_substitute=False,
                    lifetime_bound_mutant=False, mix_native_fraction=False,
                    wrong_maybeuninit=False, source_location=None):
    binders = (impl_self, "F", "'a", "'b", "'c")
    params = "; ".join(f'("{x}", ({"true" if lifetime_bound_mutant and x.startswith(chr(39)) else ("false" if x.startswith(chr(39)) else "true")}))'
                        for x in binders)
    def ident(value):
        return f'IdentTypeExpr ({loc(line)}, None, "{value}")'
    def region(value):
        return f'Var ({loc(line)}, "{value}")'
    def ref(lifetime, inner):
        return f'RustRefTypeExpr ({loc(line)}, {region(lifetime)}, Mutable, {inner})'
    def const(inner):
        return f'ConstTypeExpr ({loc(line)}, {inner})'
    slice_self = f'SliceTypeExpr ({loc(line)}, {ident(impl_self)})'
    maybe_name = "evil::mem::MaybeUninit" if wrong_maybeuninit else "std::mem::MaybeUninit"
    maybe = (f'StructTypeExpr ({loc(line)}, Some ("{maybe_name}"), '
             f'None, [], [{ident(impl_self)}])')
    scratch_ty = f'SliceTypeExpr ({loc(line)}, {maybe})'
    comparator = ident("T" if substitute else "F")
    region_scratch = "'a" if mix_region else "'b"
    region_v, region_cmp = "'a", "'c"
    declarations = "; ".join((
        f'({const(ref(region_v, slice_self))}, "v")',
        f'({const(ref(region_scratch, scratch_ty))}, "{scratch_name}")',
        f'({const(ref(region_cmp, comparator))}, "is_less")'))
    token = f'CallExpr ({loc(line)}, "thread_token", [], [], [], Static)'
    rights = f'CallExpr ({loc(line)}, "raw_rights", [], [], [], Static)'
    native = rights if drop_resource else f'Sep ({loc(line)}, {token}, {rights})'
    fraction_names = ("_q_b", "_q_b", "_q_c") if mix_native_fraction else ("_q_a", "_q_b", "_q_c")
    for fraction in fraction_names:
        native = (f'Sep ({loc(line)}, CoefAsn ({loc(line)}, VarPat ({loc(line)}, "{fraction}"), '
                  f'Var ({loc(line)}, "{fraction[3:]}")), {native})')
    unwind = rights if drop_unwind else native
    arms = f'SwitchExprClause ({loc(line)}, "returning", ["r"], {native})'
    if not drop_outcome:
        arms += f'; SwitchExprClause ({loc(line)}, "unwinding", [], {unwind})'
    result_post = (f'SwitchExpr ({loc(line)}, Var ({loc(line)}, "out"), '
                   f'[{arms}], None)')
    pre = f'Sep ({loc(line)}, CallExpr ({loc(line)}, "input_owners", [], [], [], Static), {token})'
    spec = f'Some (({pre}, ("out", {result_post})))'
    unit_name = "std_tuple_1_" if return_substitute else "std_tuple_0_"
    return_ty = (f'Some (ConstructedTypeExpr ({loc(line)}, "fn_outcome", '
                 f'[ManifestTypeExpr ({loc(line)}, StructType ("{unit_name}", []))]))')
    body_field = f'Some (([], {loc(line)}))' if body else 'None'
    return (f'Func ({source_location or loc(line)}, Regular, [{params}], {return_ty}, "{name}", '
            f'[{declarations}], false, (None, None), {spec}, false, {body_field}, false, [])')


def _thaw(value):
    from collections.abc import Mapping
    if isinstance(value, Mapping):
        return {key: _thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return tuple(_thaw(item) for item in value)
    if isinstance(value, list):
        return [_thaw(item) for item in value]
    return value


def p1_fixture(*, candidate_extra=True, shared_r_only_defpath=False,
               duplicate_r_only_ast=False, duplicate_r_only_numeric=False,
               duplicate_r_only_impl_numeric=False,
               duplicate_r_only_span=False, r_only_default_bad_span=False,
               r_only_default_zero_based_span=False,
               r_only_default_compact_span=False,
               r_only_default_wrong_source=False,
               r_only_ast_wrong_source=False,
               r_only_default_prefixed_wrong_source=False,
               candidate_default_prefixed_wrong_source=False,
               candidate_scratch_name="_scratch",
               candidate_default_compact_span=False, **changes):
    pair_hashes = {"verified": "a" * 64, "original": "b" * 64}
    actual_pair = hashlib.sha256(
        (pair_hashes["verified"] + ":" + pair_hashes["original"]).encode("ascii")
    ).hexdigest()
    source = inventory_fixture.valid_source()
    cert = inventory_fixture.certificate(source)
    compiler_dump = inventory_fixture.stream()
    if shared_r_only_defpath:
        compiler_dump = compiler_dump.replace(
            "crate::freeze32::small_sort", "crate::default16::small_sort")
    observation = inventory_fixture.m.observe("P0a", compiler_dump,
                                               compiler_dump, cert, source)
    if (duplicate_r_only_numeric or duplicate_r_only_impl_numeric or
            duplicate_r_only_span or
            r_only_default_wrong_source):
        observation = _thaw(observation)
        identities = list(observation["inventory"]["impl_small_sort_identities"])
        observation["inventory"]["impl_small_sort_identities"] = identities
        if duplicate_r_only_numeric:
            identities[1]["item_def_index"] = identities[0]["item_def_index"]
        if duplicate_r_only_impl_numeric:
            identities[1]["impl_def_index"] = identities[0]["impl_def_index"]
        if duplicate_r_only_span:
            identities[1]["source_body_span"] = identities[0]["source_body_span"]
        if r_only_default_wrong_source:
            identities[0]["source_body_span"] = (("other.rs", 6, 0),
                                                   identities[0]["source_body_span"][1])
    r_only_default_drop_resource = changes.pop("r_only_default_drop_resource", False)
    r_only_freeze_drop_outcome = changes.pop("r_only_freeze_drop_outcome", False)
    default_path = "crate::default16::small_sort"
    freeze_path = default_path if shared_r_only_defpath else "crate::freeze32::small_sort"
    default_location = (loc(6, endcol=60) if r_only_default_bad_span else
                        loc(6, startcol=0, endcol=60)
                        if r_only_default_zero_based_span else
                        'loc "verified/lib.rs(6,1-61)"'
                        if r_only_default_compact_span else
                        'loc "prefix/verified/lib.rs(6,1-6,61)"'
                        if r_only_default_prefixed_wrong_source else
                        'loc "other.rs(6,0-6,60)"'
                        if r_only_default_wrong_source or r_only_ast_wrong_source else None)
    native_rows = [
        small_sort_func("StableSmallSortTypeImpl::small_sort", 2),
        small_sort_func(default_path, 6, body=True, impl_self="T",
                        scratch_name="_scratch",
                        drop_resource=r_only_default_drop_resource,
                        source_location=default_location),
        small_sort_func(freeze_path, 12, body=True, impl_self="T",
                        drop_outcome=r_only_freeze_drop_outcome)]
    if duplicate_r_only_ast:
        native_rows.append(small_sort_func(default_path, 6, body=True, impl_self="T"))
    native_ast = "\n".join(native_rows)
    global_return = changes.pop("all_return_substitute", False)
    candidate_first = small_sort_func("__a1_impl_1_item_12_small_sort", 6,
                                      body=True, impl_self="T",
                                      scratch_name=candidate_scratch_name,
                                      return_substitute=global_return,
                                      source_location=('loc "prefix/verified/lib.rs(6,1-6,61)"'
                                          if candidate_default_prefixed_wrong_source else
                                          'loc "verified/lib.rs(6,1-61)"'
                                          if candidate_default_compact_span else None),
                                      **changes)
    candidate_ast = "\n".join((small_sort_func("StableSmallSortTypeImpl::small_sort", 2,
                                                return_substitute=global_return),
                                candidate_first,
                                small_sort_func("__a1_impl_2_item_22_small_sort", 12,
                                                body=True, impl_self="T",
                                                return_substitute=global_return)))
    if candidate_extra:
        candidate_ast += "\n" + func(70, "r_only_extra", True)
    pair = observation["case_binding"]["source_pair_id"]
    receipt = {"schema": "a1-r-only-native-reference-receipt-v1",
               "mode": "r-only-native-reference", "source_pair_id": pair,
               "reference_binary_sha256": "1" * 64,
               "reference_translator_sha256": "2" * 64,
               "source_pair_sha256": pair_hashes,
               "actual_source_pair_sha256": actual_pair,
               "build_id": "synthetic-r-only-build", "observed_exit": 1,
               "proof_credit": False,
               "ast_sha256": hashlib.sha256(native_ast.encode()).hexdigest()}
    baseline = gate.small_sort_native_baseline(native_ast, observation,
                                                source_pair_id=pair,
                                                reference_receipt=receipt)
    return candidate_ast, observation, baseline, actual_pair


class SyntheticAstGates(unittest.TestCase):
    @staticmethod
    def package(owner, *decls, location=None):
        return f'PackageDecl ({location or loc(20)}, {json.dumps(owner)}, [], [' + ";\n".join(decls) + '])'

    def packaged_threshold(self, *, owner="StableSmallSortTypeImpl", common=None):
        original = func(20, gate.COMMON, False)
        short = (common or original).replace(f'"{gate.COMMON}"', '"small_sort_threshold"')
        aliases = all_functions().replace(original + "\n", "", 1).splitlines()
        return '[\n' + ';\n'.join((self.package(""), self.package(owner, short),
                                     self.package("", *aliases))) + '\n]'

    def test_final_package_qualifies_common_and_preserves_aliases(self):
        ast = self.packaged_threshold()
        rows = gate.functions(ast)
        selected = [row for row in rows if row["name"] == gate.COMMON]
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0]["package_name"], "StableSmallSortTypeImpl")
        self.assertEqual(selected[0]["package_location"], gate.tree(loc(20)))
        self.assertEqual(selected[0]["fields"], gate.node(gate.tree(
            func(20, gate.COMMON, False).replace(f'"{gate.COMMON}"',
                                                 '"small_sort_threshold"')), "Func", 13))
        result = gate.threshold_posts(ast, INVENTORY, stage="bodies", common_line=20)
        self.assertFalse(result["proof_credit"])
        self.assertEqual(len(rows), 7)

    def test_empty_multisegment_repeated_packages_and_distinct_leaves(self):
        f = func(75, "guard", True)
        ast = '[' + ';'.join((self.package("", f), self.package("A::B", f),
                             self.package("Other", f), self.package("A::B"),
                             self.package("A::B", func(76, "other", False)))) + ']'
        rows = gate.functions(ast)
        self.assertEqual([row["name"] for row in rows],
                         ["guard", "A::B::guard", "Other::guard", "A::B::other"])
        self.assertEqual(sum(row["raw"] == f for row in rows), 3)

    def test_canonical_generic_impl_owner_preserves_duplicate_small_sort_functions(self):
        owner = "<T as StableSmallSortTypeImpl>"
        default = small_sort_func("small_sort", 6, body=True, impl_self="T")
        freeze = small_sort_func("small_sort", 12, body=True, impl_self="T")
        # R-only baseline has duplicate actual DefPaths, distinguished later
        # by compiler IDs and full source spans; the candidate dump has the
        # two compiler-generated local aliases under that same owner.
        baseline = gate.functions("[" + self.package(owner, default, freeze) + "]")
        rows = [row for row in baseline if row["name"] == owner + "::small_sort"]
        self.assertEqual(len(rows), 2)
        self.assertEqual([row["kind"] for row in rows], ["definition", "definition"])
        self.assertEqual([row["package_name"] for row in rows], [owner, owner])
        self.assertEqual([gate._source_span(row["fields"][0]) for row in rows],
                         [gate._source_span(gate.node(gate.tree(default), "Func", 13)[0]),
                          gate._source_span(gate.node(gate.tree(freeze), "Func", 13)[0])])
        _, inventory_observation, _, _ = p1_fixture()
        inventory_observation = _thaw(inventory_observation)
        pair = inventory_observation["case_binding"]["source_pair_id"]
        for identity in inventory_observation["inventory"]["impl_small_sort_identities"]:
            identity["item_def_id"] = owner + "::small_sort"
        common = small_sort_func("small_sort", 2, impl_self="Self")
        native_ast = "[" + ";".join((
            self.package("StableSmallSortTypeImpl", common),
            self.package(owner, default, freeze))) + "]"
        pair_hashes = {"verified": "a" * 64, "original": "b" * 64}
        actual_pair = hashlib.sha256((pair_hashes["verified"] + ":" +
                                      pair_hashes["original"]).encode()).hexdigest()
        receipt = {"schema": "a1-r-only-native-reference-receipt-v1",
                   "mode": "r-only-native-reference", "source_pair_id": pair,
                   "reference_binary_sha256": "1" * 64,
                   "reference_translator_sha256": "2" * 64,
                   "source_pair_sha256": pair_hashes,
                   "actual_source_pair_sha256": actual_pair,
                   "build_id": "synthetic-package-owner-build", "observed_exit": 1,
                   "proof_credit": False,
                   "ast_sha256": hashlib.sha256(native_ast.encode()).hexdigest()}
        native_baseline = gate.small_sort_native_baseline(
            native_ast, inventory_observation, source_pair_id=pair,
            reference_receipt=receipt)
        self.assertFalse(native_baseline["proof_credit"])
        self.assertEqual({row["item_def_id"] for row in
                          native_baseline["normalized_impls"].values()},
                         {owner + "::small_sort"})
        self.assertEqual(len({row["source_body_span"] for row in
                              native_baseline["normalized_impls"].values()}), 2)
        # The source compiler may also emit those same canonical DefPaths as
        # root-package Func locals. Keep that full identity intact so the
        # existing inventory IDs and source-span joins still select each body.
        root_native_ast = "[" + ";".join((
            self.package("StableSmallSortTypeImpl",
                         small_sort_func("small_sort", 2, impl_self="Self")),
            self.package("",
                         small_sort_func(owner + "::small_sort", 6,
                                         body=True, impl_self="T"),
                         small_sort_func(owner + "::small_sort", 12,
                                         body=True, impl_self="T")))) + "]"
        root_receipt = dict(receipt)
        root_receipt["ast_sha256"] = hashlib.sha256(root_native_ast.encode()).hexdigest()
        root_baseline = gate.small_sort_native_baseline(
            root_native_ast, inventory_observation, source_pair_id=pair,
            reference_receipt=root_receipt)
        self.assertFalse(root_baseline["proof_credit"])
        self.assertEqual({row["item_def_id"] for row in
                          root_baseline["normalized_impls"].values()},
                         {owner + "::small_sort"})
        self.assertEqual(len({row["source_body_span"] for row in
                              root_baseline["normalized_impls"].values()}), 2)
        candidate_ast = "[" + self.package(
            owner,
            small_sort_func("__a1_impl_11_item_13_small_sort", 6,
                            body=True, impl_self="T"),
            small_sort_func("__a1_impl_21_item_23_small_sort", 12,
                            body=True, impl_self="T")) + "]"
        candidate = [row for row in gate.functions(candidate_ast)
                     if row["kind"] == "definition"]
        self.assertEqual([row["name"] for row in candidate],
                         [owner + "::__a1_impl_11_item_13_small_sort",
                          owner + "::__a1_impl_21_item_23_small_sort"])
        for invalid in ("<U as StableSmallSortTypeImpl>",
                        "<T as OtherTrait>", "prefix/<T as StableSmallSortTypeImpl>",
                        "<T as StableSmallSortTypeImpl>::nested"):
            with self.subTest(invalid=invalid), self.assertRaises(gate.AstGateError):
                gate.functions("[" + self.package(invalid, default) + "]")

    def test_root_qualified_generic_impl_locals_keep_full_identity_and_duplicate_bodies(self):
        threshold = "<T as StableSmallSortTypeImpl>::small_sort_threshold"
        small_sort = "<T as StableSmallSortTypeImpl>::small_sort"
        owner = ""
        rows = gate.functions("[" + self.package(
            owner,
            small_sort_func(threshold, 44, body=True, impl_self="T"),
            small_sort_func(small_sort, 50, body=True, impl_self="T"),
            small_sort_func(small_sort, 68, body=True, impl_self="T")) + "]")
        self.assertEqual([row["name"] for row in rows],
                         [threshold, small_sort, small_sort])
        self.assertEqual([row["fields"][4][1] for row in rows],
                         [threshold, small_sort, small_sort])
        self.assertEqual([gate._source_span(row["fields"][0]) for row in rows[1:]],
                         [(('verified/lib.rs', 50, 1), ('verified/lib.rs', 50, 61)),
                          (('verified/lib.rs', 68, 1), ('verified/lib.rs', 68, 61))])
        for invalid_owner, invalid_local in (
                ("<T as StableSmallSortTypeImpl>", small_sort),
                ("Other", threshold),
                ("", "OtherTrait::small_sort"),
                ("", "<U as StableSmallSortTypeImpl>::small_sort")):
            with self.subTest(owner=invalid_owner, local=invalid_local), \
                    self.assertRaises(gate.AstGateError):
                gate.functions("[" + self.package(
                    invalid_owner,
                    small_sort_func(invalid_local, 50, body=True, impl_self="T")) + "]")

    def test_rejected_package_local_reports_bounded_exact_identity_context(self):
        owner = "<T as StableSmallSortTypeImpl>"
        local = "StableSmallSortTypeImpl::small_sort_threshold" + ("x" * 512)
        source = "[" + self.package(
            owner, func(32, local, False), location=loc(32)) + "]"
        with self.assertRaises(gate.AstGateError) as raised:
            gate.functions(source)
        message = str(raised.exception)
        self.assertIn("package Func local name", message)
        self.assertIn("<T as StableSmallSortTypeImpl>", message)
        self.assertIn("verified/lib.rs(32,1-32,61)", message)
        self.assertIn("verified/lib.rs(32,1-32,61)", message)
        self.assertIn("leaf_complete=False", message)
        self.assertIn("leaf_chars=", message)
        self.assertIn(hashlib.sha256(local.encode("utf-8")).hexdigest(), message)
        self.assertLess(len(message), 1200)
        self.assertNotIn("x" * 200, message)

    def test_wrong_owner_source_duplicate_and_missing_impl_identity_refused(self):
        common = func(20, gate.COMMON, False)
        short = common.replace(f'"{gate.COMMON}"', '"small_sort_threshold"')
        ast = self.packaged_threshold()
        alias = "__a1_impl_11_item_12_small_sort_threshold"
        mutants = [self.packaged_threshold(owner="Wrong"),
                   self.packaged_threshold(common=common.replace('lib.rs(20,', 'lib.rs(21,')),
                   ast[:-1] + ';' + self.package("StableSmallSortTypeImpl", short) + ']',
                   ast.replace('"' + alias + '"', '"wrong_alias"', 1),
                   ast.replace(self.package(""), self.package("", func(30, alias, True)), 1),
                   ast.replace('"' + alias + '"', '"Other::' + alias + '"', 1)]
        for mutant in mutants:
            with self.subTest(mutant=mutant[:120]), self.assertRaises(gate.AstGateError):
                gate.threshold_posts(mutant, INVENTORY, stage="bodies", common_line=20)
        # Equal leaf in another owner cannot shadow the real common prototype.
        ast = ast[:-1] + ';' + self.package("Other", short) + ']'
        gate.threshold_posts(ast, INVENTORY, stage="bodies", common_line=20)

    def test_package_normalization_does_not_hide_header_or_native_changes(self):
        ast = self.packaged_threshold()
        mutants = [ast.replace('Regular', 'Lemma', 1),
                   ast.replace('True (' + loc(20) + ')', 'False (' + loc(20) + ')', 1),
                   ast.replace('"raw_rights"', '"lost_native_resource"', 1),
                   ast.replace('"unwinding"', '"wrong_unwinding"', 1)]
        for mutant in mutants:
            with self.subTest(mutant=mutant[:120]), self.assertRaises(gate.AstGateError):
                gate.threshold_posts(mutant, INVENTORY, stage="bodies", common_line=20)

    def test_malformed_truncated_null_or_upstream_scope_refused(self):
        f = func(20, "small_sort_threshold", False)
        valid = '[' + self.package("Owner", f) + ']'
        bad = [valid[:-2], valid + 'junk',
               '[' + self.package("A::::B", f) + ']',
               '[' + self.package("::A", f) + ']',
               '[' + self.package("A::", f) + ']',
               '[' + self.package('A"B', f) + ']',
               valid.replace('"Owner"', 'null', 1),
               valid.replace('"Owner"', '12', 1),
               valid.replace(loc(20), 'None', 1),
               valid.replace(', [], [', ', None, [', 1),
               valid.replace(', [], [', ', [], None, [', 1),
               '[PackageDecl null]', '[PackageDecl]',
               'PackageDecl (' + loc(20) + ', "Owner", [], [' + f + '])',
               '[ModuleDecl (' + loc(20) + ', "Owner", [], [' + f + '])]',
               '[' + self.package("Owner", self.package("Inner", f)) + ']',
               valid[:-1] + ';' + f + ']']
        for mutant in bad:
            with self.subTest(mutant=mutant[:120]), self.assertRaises(gate.AstGateError):
                gate.functions(mutant)

    def test_package_strings_cannot_create_functions_or_scopes(self):
        f = func(20, "quoted", False)
        decoy = json.dumps('escaped " quote\nFunc (bad)\nPackageDecl (bad)')
        f = f.replace('"thread_token"', decoy)
        ast = '[' + self.package("Owner", f) + ']'
        rows = gate.functions(ast)
        self.assertEqual([row["name"] for row in rows], ["Owner::quoted"])
        self.assertIn('PackageDecl (bad)', rows[0]["raw"])

    def test_p1_binds_full_interface_and_native_triplet(self):
        ast, inventory, baseline, actual_pair = p1_fixture()
        result = gate.small_sort_interface(ast, inventory, baseline=baseline,
                                            actual_source_pair_sha256=actual_pair)
        self.assertTrue(result["structural_pass"])
        self.assertEqual(result["classification"], "INTERFACE_STRUCTURE_ONLY_UNRUN_PROOF")
        self.assertEqual(set(result["impls"]), {"default16", "freeze32"})
        self.assertEqual(
            {name: row["item_def_id"]
             for name, row in baseline["normalized_impls"].items()},
            {"default16": "crate::default16::small_sort",
             "freeze32": "crate::freeze32::small_sort"})
        self.assertTrue(all(result["impls"][name]["native_matches_r_only_original_impl"]
                            for name in ("default16", "freeze32")))
        self.assertTrue(result["compiler_clauses_source_bound"])
        self.assertEqual(result["ast_clause_representation"],
                         "none; compiler-required interface is separately validated")
        self.assertEqual(result["body_count"], 0)
        self.assertFalse(result["proof_credit"])

    def test_p1_signature_unwraps_one_outer_const_binding_marker_only(self):
        source = small_sort_func("crate::default16::small_sort", 6,
                                 body=True, impl_self="T")
        record, = gate.functions(source)
        alpha = gate._small_sort_alpha(record, self_name="T")
        normalized = gate._small_sort_ast_signature(record, "T", alpha)
        self.assertEqual(normalized[0],
                         ("ref", "@input_0", True,
                          ("slice", ("param", "@Self"))))

        fields = list(record["fields"])
        parameter_rows = list(gate.items(fields[5]))
        first_type, first_name = gate.node(parameter_rows[0], "tuple", 2)
        const_loc, inner = gate.node(first_type, "ConstTypeExpr", 2)
        malformed_types = {
            "nested binding marker": ("ConstTypeExpr", (const_loc, first_type)),
            "empty binding location": ("ConstTypeExpr", ((), inner)),
            "over-arity binding location":
                ("ConstTypeExpr", (("loc", "x", "extra"), inner)),
            "non-string binding location":
                ("ConstTypeExpr", (("loc", 7), inner)),
            "unlocated binding marker": ("ConstTypeExpr", (("atom", "None"), inner)),
        }
        # The already supported bare-type representation remains valid.
        bare_rows = list(parameter_rows)
        bare_rows[0] = ("tuple", (inner, first_name))
        bare_fields = list(fields)
        bare_fields[5] = ("list", tuple(bare_rows))
        bare_record = dict(record, fields=tuple(bare_fields))
        self.assertEqual(gate._small_sort_ast_signature(
            bare_record, "T", gate._small_sort_alpha(bare_record, self_name="T")),
            normalized)
        # Header comparison still retains the raw AST binding marker.
        self.assertNotEqual(gate._small_sort_ast_header(record, alpha),
                            gate._small_sort_ast_header(bare_record, alpha))
        self.assertEqual(gate._small_sort_ast_header_for_common_comparison(
            gate._small_sort_ast_header(record, alpha)),
            gate._small_sort_ast_header_for_common_comparison(
                gate._small_sort_ast_header(bare_record, alpha)))
        for label, bad_type in malformed_types.items():
            with self.subTest(mutant=label), self.assertRaises(gate.AstGateError):
                bad_rows = list(parameter_rows)
                bad_rows[0] = ("tuple", (bad_type, first_name))
                bad_fields = list(fields)
                bad_fields[5] = ("list", tuple(bad_rows))
                bad_record = dict(record, fields=tuple(bad_fields))
                gate._small_sort_ast_signature(
                    bad_record, "T", gate._small_sort_alpha(bad_record, self_name="T"))
            # Source location values are deliberately erased by normalize;
            # the preceding signature gate rejects the non-string source loc.
            if label != "non-string binding location":
                with self.subTest(header_mutant=label), self.assertRaises(gate.AstGateError):
                    gate._small_sort_ast_header_for_common_comparison(
                        gate._small_sort_ast_header(bad_record, alpha))

    def test_p1_signature_accepts_source_scratch_name_variants_without_header_erasure(self):
        records = []
        for scratch_name in ("scratch", "_scratch"):
            source = small_sort_func("crate::default16::small_sort", 6,
                                     body=True, impl_self="T",
                                     scratch_name=scratch_name)
            record, = gate.functions(source)
            alpha = gate._small_sort_alpha(record, self_name="T")
            records.append((record, alpha, gate._small_sort_ast_signature(
                record, "T", alpha)))
        self.assertEqual(records[0][2], records[1][2])
        self.assertNotEqual(gate._small_sort_ast_header(records[0][0], records[0][1]),
                            gate._small_sort_ast_header(records[1][0], records[1][1]))
        self.assertEqual(
            gate._small_sort_ast_header_for_common_comparison(
                gate._small_sort_ast_header(records[0][0], records[0][1])),
            gate._small_sort_ast_header_for_common_comparison(
                gate._small_sort_ast_header(records[1][0], records[1][1])))

        record = records[1][0]
        fields = list(record["fields"])
        parameter_rows = list(gate.items(fields[5]))
        for names in (("v", "is_less", "scratch"),
                      ("v", "scratch", "comparator")):
            with self.subTest(names=names), self.assertRaises(gate.AstGateError):
                bad_rows = [gate.node(row, "tuple", 2)[0] for row in parameter_rows]
                bad_rows = [(bad_rows[index], ("str", names[index]))
                            for index in range(len(names))]
                bad_fields = list(fields)
                bad_fields[5] = ("list", tuple(("tuple", row) for row in bad_rows))
                bad_record = dict(record, fields=tuple(bad_fields))
                gate._small_sort_ast_signature(
                    bad_record, "T", gate._small_sort_alpha(bad_record, self_name="T"))

    def test_p1_native_comparison_alpha_renames_only_bound_scratch_vars(self):
        def native(scratch_name, *, resource="array", item_type="T", region="'a",
                   unrelated_name=None,
                   fold_indexes=(0, 1), fold_patterns=True, fold_uses=True):
            fold_rows = []
            for index in fold_indexes:
                binder = f"_v{index}_{scratch_name}"
                if fold_patterns:
                    fold_rows.append(f'VarPat ({loc(1)}, "{binder}")')
                if fold_uses:
                    fold_rows.append(f'Var ({loc(1)}, "{binder}")')
            args = [f'Var ({loc(1)}, "{scratch_name}")', *fold_rows,
                    f'IdentTypeExpr ({loc(1)}, None, "{item_type}")',
                    f'IdentTypeExpr ({loc(1)}, None, "{region}")']
            if unrelated_name is not None:
                args.append(f'IdentTypeExpr ({loc(1)}, None, "{unrelated_name}")')
            args = "; ".join(args)
            term = gate.normalize(gate.tree(
                f'CallExpr ({loc(1)}, "{resource}", [], [], [{args}], Static)'))
            return {key: term for key in ("pre", "returning", "unwind")}

        default = native("_scratch")
        canonical = native("scratch")
        projected_default = gate._small_sort_native_for_common_comparison(
            default, "_scratch")
        projected_canonical = gate._small_sort_native_for_common_comparison(
            canonical, "scratch")
        self.assertEqual(projected_default, projected_canonical)
        self.assertNotEqual(default, projected_default)
        unrelated = gate._small_sort_native_for_common_comparison(
            native("scratch", unrelated_name="scratch"), "scratch")
        self.assertIn("('str', 'scratch')", repr(unrelated))
        self.assertNotEqual(
            projected_canonical,
            gate._small_sort_native_for_common_comparison(
                native("scratch", fold_indexes=(0,)), "scratch"))
        for changed in (native("scratch", resource="different_resource"),
                        native("scratch", item_type="U"),
                        native("scratch", region="'b")):
            with self.subTest(changed=changed):
                self.assertNotEqual(
                    projected_canonical,
                    gate._small_sort_native_for_common_comparison(changed, "scratch"))
        for malformed in (native("_scratch", fold_indexes=(2,)),
                          native("_scratch", fold_patterns=True, fold_uses=False),
                          native("_scratch", fold_patterns=False, fold_uses=True)):
            with self.subTest(malformed=malformed), self.assertRaises(gate.AstGateError):
                gate._small_sort_native_for_common_comparison(malformed, "_scratch")

    def test_p1_rejects_lost_native_resource(self):
        ast, inventory, baseline, actual_pair = p1_fixture(drop_resource=True)
        with self.assertRaises(gate.AstGateError):
            gate.small_sort_interface(ast, inventory, baseline=baseline,
                                      actual_source_pair_sha256=actual_pair)

    def test_p1_rejects_candidate_scratch_name_drift_from_same_r_only_body(self):
        ast, inventory, baseline, actual_pair = p1_fixture(
            candidate_scratch_name="scratch")
        with self.assertRaises(gate.AstGateError):
            gate.small_sort_interface(ast, inventory, baseline=baseline,
                                      actual_source_pair_sha256=actual_pair)

    def test_p1_rejects_lost_unwind_outcome(self):
        ast, inventory, baseline, actual_pair = p1_fixture(drop_outcome=True)
        with self.assertRaises(gate.AstGateError):
            gate.small_sort_interface(ast, inventory, baseline=baseline,
                                      actual_source_pair_sha256=actual_pair)

    def test_r_only_baseline_binds_original_impl_bodies_by_defpath_and_span(self):
        for mutation in ("r_only_default_drop_resource", "r_only_freeze_drop_outcome"):
            with self.subTest(mutation=mutation):
                with self.assertRaises(gate.AstGateError):
                    p1_fixture(**{mutation: True})

    def test_r_only_shared_printed_defpath_binds_by_numeric_ids_and_full_spans(self):
        ast, inventory, baseline, actual_pair = p1_fixture(
            shared_r_only_defpath=True, r_only_default_compact_span=True,
            candidate_default_compact_span=True)
        self.assertEqual({row["item_def_id"] for row in
                          baseline["normalized_impls"].values()},
                         {"crate::default16::small_sort"})
        self.assertNotEqual(
            baseline["normalized_impls"]["default16"]["source_body_span"],
            baseline["normalized_impls"]["freeze32"]["source_body_span"])
        self.assertEqual(
            baseline["normalized_impls"]["default16"]["source_body_span"],
            (("verified/lib.rs", 6, 0), ("verified/lib.rs", 6, 60)),
            "baseline preserves raw zero-based compiler source span")
        result = gate.small_sort_interface(ast, inventory, baseline=baseline,
                                           actual_source_pair_sha256=actual_pair)
        self.assertTrue(result["structural_pass"])
        self.assertEqual(set(result["impls"]), {"default16", "freeze32"})
        self.assertTrue(all(result["impls"][name]["actual_definition_bound_to_compiler_item"]
                            for name in ("default16", "freeze32")))

    def test_r_only_rejects_duplicate_numeric_identity_or_body_span(self):
        for mutation in ("duplicate_r_only_numeric", "duplicate_r_only_impl_numeric",
                         "duplicate_r_only_span"):
            with self.subTest(mutation=mutation), self.assertRaises(gate.AstGateError):
                p1_fixture(shared_r_only_defpath=True, **{mutation: True})

    def test_r_only_rejects_ambiguous_ast_and_full_span_mismatch(self):
        for mutation in ("duplicate_r_only_ast", "r_only_default_bad_span",
                         "r_only_default_zero_based_span"):
            with self.subTest(mutation=mutation), self.assertRaises(gate.AstGateError):
                p1_fixture(shared_r_only_defpath=True, **{mutation: True})

    def test_r_only_rejects_wrong_compiler_or_ast_source_path(self):
        for mutation in ("r_only_default_wrong_source", "r_only_ast_wrong_source",
                         "r_only_default_prefixed_wrong_source"):
            with self.subTest(mutation=mutation), self.assertRaises(gate.AstGateError):
                p1_fixture(shared_r_only_defpath=True, **{mutation: True})

    def test_candidate_rejects_prefixed_path_with_canonical_suffix(self):
        ast, inventory, baseline, actual_pair = p1_fixture(
            candidate_default_prefixed_wrong_source=True)
        with self.assertRaises(gate.AstGateError):
            gate.small_sort_interface(ast, inventory, baseline=baseline,
                                      actual_source_pair_sha256=actual_pair)

    def test_ast_location_parser_accepts_compact_same_line_range_only(self):
        self.assertEqual(gate._source_span(
            gate.tree('loc "verified/lib.rs(32,8-28)"')),
            (("verified/lib.rs", 32, 8), ("verified/lib.rs", 32, 28)))
        self.assertEqual(gate._source_span(
            gate.tree('loc "verified/lib.rs(32,8-34,28)"')),
            (("verified/lib.rs", 32, 8), ("verified/lib.rs", 34, 28)))
        for value in ('verified/lib.rs(32,8)',
                      'prefix/verified/lib.rs(32,8-28)'):
            with self.subTest(value=value), self.assertRaises(gate.AstGateError):
                gate._source_span(gate.tree(f'loc "{value}"'))

    def test_p1_rejects_self_or_unprovenanced_baseline(self):
        ast, inventory, baseline, actual_pair = p1_fixture()
        self_baseline = dict(baseline)
        candidate_sha = hashlib.sha256(ast.encode()).hexdigest()
        self_baseline["ast_sha256"] = candidate_sha
        self_baseline["reference_receipt"] = {**baseline["reference_receipt"],
                                               "ast_sha256": candidate_sha}
        with self.assertRaises(gate.AstGateError):
            gate.small_sort_interface(ast, inventory, baseline=self_baseline,
                                      actual_source_pair_sha256=actual_pair)
        wrong_source = {**baseline, "source_pair_id": "0" * 64}
        with self.assertRaises(gate.AstGateError):
            gate.small_sort_interface(ast, inventory, baseline=wrong_source,
                                      actual_source_pair_sha256=actual_pair)
        with self.assertRaises(gate.AstGateError):
            gate.small_sort_interface(ast, inventory, baseline=baseline,
                                      actual_source_pair_sha256="4" * 64)
        bad_pair_receipt = {**baseline, "reference_receipt": {
            **baseline["reference_receipt"],
            "source_pair_sha256": {"verified": "c" * 64, "original": "b" * 64}}}
        with self.assertRaises(gate.AstGateError):
            gate.small_sort_interface(ast, inventory, baseline=bad_pair_receipt,
                                      actual_source_pair_sha256=actual_pair)

    def test_p1_rejects_type_substitution_and_region_mixing(self):
        for changes in ({"substitute": True}, {"mix_region": True},
                        {"mix_native_fraction": True}, {"wrong_maybeuninit": True}):
            ast, inventory, baseline, actual_pair = p1_fixture(**changes)
            with self.assertRaises(gate.AstGateError):
                gate.small_sort_interface(ast, inventory, baseline=baseline,
                                          actual_source_pair_sha256=actual_pair)

    def test_p1_rejects_uniform_return_header_substitution(self):
        # Changing common and both impl headers together must still fail the
        # compiler-derived unit return check and independent R-only header.
        ast, inventory, baseline, actual_pair = p1_fixture(all_return_substitute=True)
        with self.assertRaises(gate.AstGateError):
            gate.small_sort_interface(ast, inventory, baseline=baseline,
                                      actual_source_pair_sha256=actual_pair)

    def test_p1_rejects_lifetime_sized_marker_mutation(self):
        ast, inventory, baseline, actual_pair = p1_fixture(lifetime_bound_mutant=True)
        with self.assertRaises(gate.AstGateError):
            gate.small_sort_interface(ast, inventory, baseline=baseline,
                                      actual_source_pair_sha256=actual_pair)

    def test_body_contracts_preserve_native(self):
        result = gate.threshold_posts(all_functions(), INVENTORY,
                                      stage="bodies", common_line=20)
        self.assertFalse(result["common_checked"])
        self.assertEqual(set(result["impls"]), {"default16", "freeze32"})
        self.assertFalse(result["proof_credit"])

    def test_caller_common_requires_prior_native(self):
        body = gate.threshold_posts(all_functions(), INVENTORY,
                                    stage="bodies", common_line=20)
        caller = gate.threshold_posts(all_functions(True), INVENTORY,
                                      stage="caller", common_line=20,
                                      baseline=body["native"])
        self.assertTrue(caller["common_checked"])

    def test_extra_outcome_arm_refused(self):
        with self.assertRaises(gate.AstGateError):
            gate.threshold_posts(all_functions(extra_arm=True), INVENTORY,
                                 stage="bodies", common_line=20)

    def test_unwind_range_refused(self):
        with self.assertRaises(gate.AstGateError):
            gate.threshold_posts(all_functions(bad_unwind=True), INVENTORY,
                                 stage="bodies", common_line=20)

    def test_duplicate_compiler_ids_refused(self):
        inventory = {**INVENTORY,
                     "freeze32": {**INVENTORY["freeze32"], "compiler_item_id": "12"}}
        with self.assertRaises(gate.AstGateError):
            gate.threshold_posts(all_functions(), inventory,
                                 stage="bodies", common_line=20)

    def test_string_aware_fields_and_unknown_syntax(self):
        self.assertEqual(gate.fields('"a,b", (x, [a; b]), c'),
                         ['"a,b"', '(x, [a; b])', 'c'])
        with self.assertRaises(gate.AstGateError):
            gate.tree('eval ("x") + unsafe')
        quoted_decoy = 'let s = "\\nFunc (loc \\"wrong\\", Regular)"\n'
        self.assertEqual(gate._segments(quoted_decoy + all_functions(), "Func")
                         .__len__(), 7)

    def test_observer_common_call_only(self):
        text = caller_func("a1_guard_observer", 70, 75)
        result = gate.caller_calls(text, owner="a1_guard_observer",
                                   expected=(gate.COMMON,), source_line=70,
                                   call_lines={gate.COMMON: 75},
                                   expected_arguments={gate.COMMON: ()})
        self.assertFalse(result["compiler_mir_binding_checked"])

    def test_impl_alias_call_refused(self):
        text = caller_func("a1_guard_observer", 70, 75, alias=True)
        with self.assertRaises(gate.AstGateError):
            gate.caller_calls(text, owner="a1_guard_observer",
                              expected=(gate.COMMON,), source_line=70,
                              call_lines={gate.COMMON: 75},
                              expected_arguments={gate.COMMON: ()})

    def test_p1_both_original_calls(self):
        text = caller_func("quicksort", 70, 75, small_sort=True)
        result = gate.caller_calls(text, owner="quicksort",
                                   expected=(gate.COMMON, gate.SMALL_SORT),
                                   source_line=70,
                                   call_lines={gate.COMMON: 75,
                                               gate.SMALL_SORT: 76},
                                   expected_arguments={
                                       gate.COMMON: (),
                                       gate.SMALL_SORT: ("$tmp_v", "$tmp_scratch", "$tmp_cmp")})
        self.assertEqual(len(result["calls"]), 2)

    def test_p1_argument_origin_change_refused(self):
        text = caller_func("quicksort", 70, 75, small_sort=True)
        with self.assertRaises(gate.AstGateError):
            gate.caller_calls(text, owner="quicksort",
                              expected=(gate.COMMON, gate.SMALL_SORT),
                              source_line=70,
                              call_lines={gate.COMMON: 75, gate.SMALL_SORT: 76},
                              expected_arguments={gate.COMMON: (),
                                                  gate.SMALL_SORT: ("$tmp_v", "$tmp_scratch", "$wrong")})

    def test_unique_focused_ast_body_interval(self):
        alias = "__a1_impl_11_item_12_small_sort_threshold"
        text = all_functions()
        selected = runner.select_focused_body(
            text, gate, focus_line=30, expected_name=alias,
            compiler_span=(30, 30))
        self.assertEqual(selected["body_count_from_intervals"], 1)
        with self.assertRaises(RuntimeError):
            runner.select_focused_body(
                text + "\n" + func(30, "unrelated", True, body=True),
                gate, focus_line=30, expected_name=alias,
                compiler_span=(30, 30))


if __name__ == "__main__":
    unittest.main()
