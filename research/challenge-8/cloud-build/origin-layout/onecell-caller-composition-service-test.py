#!/usr/bin/env python3
"""Isolated synthetic classifier checks; no proof tools or evidence access."""
import importlib.util
from pathlib import Path
import sys
import tempfile

HERE = Path(__file__).resolve().parent
TARGET = HERE / "onecell-caller-composition.py"

spec = importlib.util.spec_from_file_location("composition_service_test", TARGET)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

# The imported campaign module has only standard-library top-level imports.
# Replace all evidence gates so these cases exercise classification only.
module._source_gate = lambda case, row: {"admitted": True}
module._mir_gate = lambda case, row, mir: {"admitted": True}
module._ast_gate = lambda case, row, ast, body: {"admitted": True}

# Exercise the pinned AST shape directly with synthetic nodes. CallExpr args
# are LitPat-wrapped, matching the repository's admitted function-call ASTs.
ast = module._load("composition_ast_service_test", module.ROOT /
                   "research/challenge-8/merge/overnight/stack-proof-ast-admission.py")
row_ast = {"origin_line": 20, "origin_equality_column": 43}
assert_loc = ast.Node("loc", ["verified/lib.rs(20,13-55)"])
eq_loc = ast.Node("loc", ["verified/lib.rs(20,43-45)"])
guard_arg = ast.Node("LitPat", [ast.Node("Var", [assert_loc, "guard_ptr"])])
origin_call = ast.Node("CallExpr", [eq_loc, "ref_origin", [], [], [guard_arg], ast.Sym("Static")])
guard_rhs = ast.Node("Var", [eq_loc, "guard_ptr"])
origin_eq = ast.Node("Operation", [eq_loc, ast.Sym("Eq"), [origin_call, guard_rhs]])
origin_assert = ast.Node("Assert", [assert_loc, origin_eq])
assert module._origin_equality_matches(origin_eq, ast, row_ast)
assert ast.loc(origin_assert.args[0]) == "verified/lib.rs(20,13-55)"
wrong_call = ast.Node("CallExpr", [eq_loc, "ref_origin", [], [],
                                   [ast.Node("LitPat", [ast.Node("Var", [assert_loc, "other_ptr"])])],
                                   ast.Sym("Static")])
assert not module._origin_equality_matches(
    ast.Node("Operation", [eq_loc, ast.Sym("Eq"), [wrong_call, guard_rhs]]), ast, row_ast)
assert not module._origin_equality_matches(
    ast.Node("Operation", [eq_loc, ast.Sym("Eq"),
        [origin_call, ast.Node("Var", [eq_loc, "other_ptr"])] ]), ast, row_ast)
assert not module._origin_equality_matches(
    ast.Node("Operation", [ast.Node("loc", ["verified/lib.rs(20,44-46)"]),
        ast.Sym("Eq"), [origin_call, guard_rhs]]), ast, row_ast)

row = {
    "case": "receiver_origin_probe", "expected": "receiver_origin_probe",
    "origin_line": 20,
    "origin_assert_column": module.ORIGIN_ASSERT.splitlines()[0].index(b"assert ref_origin") + 1,
    "origin_equality_column": module.ORIGIN_ASSERT.splitlines()[0].index(b"==") + 1,
    "guard_fields_line": 19,
    "false_line": None,
    "helper_return_line": 70, "caller_return_line": 90,
    "helper_copy_line": 50, "call_line": 60, "effect_open_line": 65,
}
stages = {"exporter": 0, "decode": 0, "refinement": 0, "verifast": 1}
execution = {"stages": stages, "source_unchanged_at_every_stage": True}

with tempfile.TemporaryDirectory(prefix="onecell-origin-classifier-") as tmp:
    case = Path(tmp)
    (case / "original").mkdir()
    (case / "verified").mkdir()
    (case / "original/lib.rs").write_text("")
    (case / "verified/lib.rs").write_text("")
    (case / "verifast.log").write_text(
        "verified/lib.rs(19,12-48): note: Executing statement\n"
        f"verified/lib.rs(20,{row['origin_equality_column']}-54): error: Assertion might not hold. (Cannot prove equality.)\n")
    classified = module._classify(case, row, execution, None, None, None)
    assert classified["classification"] == "EXPECTED_RECEIVER_ORIGIN_REJECTION"
    assert classified["receiver_origin_probe_targeted_negative"] is True
    assert classified["receiver_origin_probe_exact_location_error"] is True

    # The same error at a different column is inconclusive.
    (case / "verifast.log").write_text(
        "verified/lib.rs(19,12-48): note: Executing statement\n"
        f"verified/lib.rs(20,{row['origin_equality_column'] + 1}-54): error: Assertion might not hold. (Cannot prove equality.)\n")
    classified = module._classify(case, row, execution, None, None, None)
    assert classified["classification"] == "INCONCLUSIVE"

    # If the fixedpoint verifies, report only the probe result, never method proof.
    successful_stages = dict(stages, verifast=0)
    successful_execution = dict(execution, stages=successful_stages)
    (case / "verifast.log").write_text(
        "verified/lib.rs(19,12-48): note: Executing statement\n"
        "verified/lib.rs(20,12-54): note: Executing statement\n"
        "verified/lib.rs(50,12-48): note: Executing statement\n"
        "verified/lib.rs(60,12-48): note: Executing statement\n"
        "verified/lib.rs(65,12-48): note: Executing statement\n"
        "verified/lib.rs(70,1-5): Executing return statement\n"
        "verified/lib.rs(70,1-5): Leak check.\n"
        "verified/lib.rs(90,1-5): Executing return statement\n"
        "verified/lib.rs(90,1-5): Leak check.\n"
        "0 errors found.\n")
    classified = module._classify(case, row, successful_execution, None, None, None)
    assert classified["classification"] == "PROBE_ORIGIN_ESTABLISHED"
    assert classified["accepted"] is False
    assert classified["actual_drop_glue_credit"] is False

print("PASS_SERVICE_ONLY: exact negative, wrong-column refusal, unexpected success")
