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


def loc(line):
    return f'loc "verified/lib.rs({line},1-1)"'


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
                    drop_resource=False, drop_unwind=False, substitute=False,
                    mix_region=False, drop_outcome=False, return_substitute=False,
                    lifetime_bound_mutant=False, mix_native_fraction=False,
                    wrong_maybeuninit=False):
    binders = (impl_self, "F", "'a", "'b", "'c")
    params = "; ".join(f'("{x}", ({"true" if lifetime_bound_mutant and x.startswith(chr(39)) else ("false" if x.startswith(chr(39)) else "true")}))'
                        for x in binders)
    def ident(value):
        return f'IdentTypeExpr ({loc(line)}, None, "{value}")'
    def region(value):
        return f'Var ({loc(line)}, "{value}")'
    def ref(lifetime, inner):
        return f'RustRefTypeExpr ({loc(line)}, {region(lifetime)}, Mutable, {inner})'
    slice_self = f'SliceTypeExpr ({loc(line)}, {ident(impl_self)})'
    maybe_name = "evil::mem::MaybeUninit" if wrong_maybeuninit else "std::mem::MaybeUninit"
    maybe = (f'StructTypeExpr ({loc(line)}, Some ("{maybe_name}"), '
             f'None, [], [{ident(impl_self)}])')
    scratch_ty = f'SliceTypeExpr ({loc(line)}, {maybe})'
    comparator = ident("T" if substitute else "F")
    region_scratch = "'a" if mix_region else "'b"
    region_v, region_cmp = "'a", "'c"
    declarations = "; ".join((
        f'({ref(region_v, slice_self)}, "v")',
        f'({ref(region_scratch, scratch_ty)}, "scratch")',
        f'({ref(region_cmp, comparator)}, "is_less")'))
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
    return (f'Func ({loc(line)}, Regular, [{params}], {return_ty}, "{name}", '
            f'[{declarations}], false, (None, None), {spec}, false, {body_field}, false, [])')


def p1_fixture(*, candidate_extra=True, **changes):
    pair_hashes = {"verified": "a" * 64, "original": "b" * 64}
    actual_pair = hashlib.sha256(
        (pair_hashes["verified"] + ":" + pair_hashes["original"]).encode("ascii")
    ).hexdigest()
    source = inventory_fixture.valid_source()
    cert = inventory_fixture.certificate(source)
    observation = inventory_fixture.m.observe("P0a", inventory_fixture.stream(),
                                               inventory_fixture.stream(), cert, source)
    r_only_default_drop_resource = changes.pop("r_only_default_drop_resource", False)
    r_only_freeze_drop_outcome = changes.pop("r_only_freeze_drop_outcome", False)
    native_ast = "\n".join((
        small_sort_func("StableSmallSortTypeImpl::small_sort", 2),
        small_sort_func("crate::default16::small_sort", 6, body=True, impl_self="T",
                        drop_resource=r_only_default_drop_resource),
        small_sort_func("crate::freeze32::small_sort", 12, body=True, impl_self="T",
                        drop_outcome=r_only_freeze_drop_outcome)))
    global_return = changes.pop("all_return_substitute", False)
    candidate_first = small_sort_func("__a1_impl_1_item_12_small_sort", 6,
                                      body=True, impl_self="T",
                                      return_substitute=global_return, **changes)
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
    def test_module_owned_short_function_name_is_qualified_structurally(self):
        common = func(20, gate.COMMON, False)
        short = common.replace(f'"{gate.COMMON}"', '"small_sort_threshold"')
        module = f'ModuleDecl ({loc(20)}, "StableSmallSortTypeImpl", [], [{short}])'
        ast = all_functions().replace(common, module, 1)
        rows = gate.functions(ast)
        selected = [row for row in rows if row["name"] == gate.COMMON]
        self.assertEqual(len(selected), 1)
        params = gate.items(selected[0]["fields"][2])
        self.assertEqual(gate.atom(gate.node(params[0], "tuple", 2)[0]), "Self")
        result = gate.threshold_posts(ast, INVENTORY, stage="bodies", common_line=20)
        self.assertFalse(result["proof_credit"])

    def test_nested_module_paths_and_unscoped_functions_remain_distinct(self):
        nested_func = func(75, "guard", True)
        nested = (f'ModuleDecl ({loc(70)}, "Outer", [], '
                  f'[ModuleDecl ({loc(71)}, "Inner", [], [{nested_func}])])')
        # The byte-identical top-level record must not be mistaken for the
        # nested record just because its text occurs inside the module.
        bare = nested_func
        rows = gate.functions(nested + "\n" + bare)
        self.assertEqual({row["name"] for row in rows}, {"Outer::Inner::guard", "guard"})
        self.assertEqual(sum(row["raw"] == nested_func for row in rows), 1)

    def test_malformed_or_ambiguous_module_ownership_is_rejected(self):
        f = func(20, "small_sort_threshold", False)
        bad_modules = (
            f'ModuleDecl ({loc(20)}, "", [], [{f}])',
            f'ModuleDecl ({loc(20)}, 12, [], [{f}])',
            f'ModuleDecl ({loc(20)}, "M", [{f}])',
            f'ModuleDecl ({loc(20)}, "M", [], [{f}])\n'
            f'ModuleDecl ({loc(21)}, "M", [], [{f.replace("20", "21")}])',
        )
        for ast in bad_modules:
            with self.subTest(ast=ast[:100]), self.assertRaises(gate.AstGateError):
                gate.functions(ast)
        common = func(20, gate.COMMON, False)
        short = common.replace(f'"{gate.COMMON}"', '"small_sort_threshold"')
        duplicate = (f'ModuleDecl ({loc(20)}, "StableSmallSortTypeImpl", [], [{short}])\n'
                     + common)
        with self.assertRaises(gate.AstGateError):
            gate.threshold_posts(duplicate, INVENTORY, stage="bodies", common_line=20)

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

    def test_p1_rejects_lost_native_resource(self):
        ast, inventory, baseline, actual_pair = p1_fixture(drop_resource=True)
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
