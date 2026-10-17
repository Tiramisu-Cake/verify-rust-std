"""Synthetic parser controls only; no compiler or proof artifact is read."""
import importlib.util
from pathlib import Path
import unittest


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


class SyntheticAstGates(unittest.TestCase):
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
