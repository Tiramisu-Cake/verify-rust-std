#!/usr/bin/env python3
"""Isolated generated-glue evidence gate tests; no proof tools or evidence access."""
import importlib.util
from pathlib import Path
import sys

TARGET = Path(__file__).with_name("onecell-selected-drop.py")
spec = importlib.util.spec_from_file_location("selected_drop_service_test", TARGET)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

# The restricted parser import is inert; use the exact constructor shape
# emitted by dump_ast_with_locs: False (loc "verified/lib.rs(...)").
parser_path = TARGET.parents[2] / "merge/overnight/stack-proof-ast-admission.py"
parser_spec = importlib.util.spec_from_file_location("selected_drop_ast_parser_test", parser_path)
ast = importlib.util.module_from_spec(parser_spec)
sys.modules[parser_spec.name] = ast
parser_spec.loader.exec_module(ast)
ast_parser = ast
emitted_false = ast.OcamlAstText(
    'False(loc "verified/lib.rs(42,17-22)")').parse()
assert module._literal_false_with_loc(emitted_false, ast)
for malformed in (
    'False',
    'False()',
    'False(loc "verified/lib.rs(42,17-22)", True)',
    'False(Var(loc "verified/lib.rs(42,17-22)", "x"))',
    'False(loc "other.rs(42,17-22)")',
    'True(loc "verified/lib.rs(42,17-22)")',
    'assume(loc "verified/lib.rs(42,17-22)", False)',
):
    assert not module._literal_false_with_loc(ast.OcamlAstText(malformed).parse(), ast), malformed

call_loc = "verified/lib.rs(10,5-19)"
copy_loc = "verified/lib.rs(9,5-13)"
ast = {"glue_selected_method_call_loc": call_loc,
       "glue_receiver_copy_loc": copy_loc}
success = (
    "verified/lib.rs(4,1-10): Verifying function 'core::__vf_generated_drop_glue'\n"
    f"  0.101s: {copy_loc}: Executing statement\n"
    f"  0.153s: {call_loc}: Executing statement\n"
    f"  0.153s: {call_loc}: Verifying call\n"
    "verified/lib.rs(12,1-5): Executing return statement\n"
    "verified/lib.rs(12,1-5): Leak check.\n"
    "verified/lib.rs(20,1-5): Verifying function 'natural_onecell'\n")
assert module._generated_glue_proof_gate(success, ast)["admitted"]

cases = (
    # No marker elsewhere in a caller or selected-method segment can stand in.
    success.replace(f"  0.153s: {call_loc}: Executing statement\n", ""),
    success.replace(f"  0.153s: {call_loc}: Verifying call\n", ""),
    success.replace(f"{copy_loc}: Executing statement\n", ""),
    success.replace(call_loc, "verified/lib.rs(10,6-20)"),
    success.replace("Executing return statement", "Returning"),
    success.replace("Leak check.", ""),
    success.replace("Leak check.\n", "Leak check.\n"
                     "verified/lib.rs(11,1-5): error: failure\n"),
    success.replace("Leak check.\n", "Leak check.\n"
                     "verified/lib.rs(11,1-5): dead code\n"),
    success.replace("core::__vf_generated_drop_glue", "fake__vf_generated_drop_glue"),
    success + "Verifying function '__vf_generated_drop_glue'\n",
    (success.replace(f"  0.101s: {copy_loc}: Executing statement\n", "")
     .replace(f"  0.153s: {call_loc}: Executing statement\n", "")
     .replace(f"  0.153s: {call_loc}: Verifying call\n", "")
     .replace("verified/lib.rs(12,1-5): Executing return statement\n", "")
     .replace("verified/lib.rs(12,1-5): Leak check.\n", "")
     .replace("verified/lib.rs(20,1-5): Verifying function 'natural_onecell'\n",
              "verified/lib.rs(20,1-5): Verifying function 'natural_onecell'\n"
              f"  0.200s: {call_loc}: Executing statement\n"
              f"  0.200s: {call_loc}: Verifying call\n"
              "  0.201s: Executing return statement\n"
              "  0.201s: Leak check.\n")),
)
for log in cases:
    assert not module._generated_glue_proof_gate(log, ast)["admitted"], log

assert module._is_generated_glue_name("__vf_generated_drop_glue")
assert module._is_generated_glue_name("core::__vf_generated_drop_glue")
assert not module._is_generated_glue_name("fake__vf_generated_drop_glue")

# Each body-route negative is matched at its declared source obligation. A
# matching verifier result still cannot be admitted when the full setup gate
# (including successful refinement) is false.
import tempfile

def run_negative(name, row, source_line, log, error_lines=(), dead_lines=(),
                 natural_exit=True, caller_return=False, caller_leak=False):
    with tempfile.TemporaryDirectory(prefix="selected-drop-negative-") as tmp:
        case = Path(tmp)
        (case / "verified").mkdir()
        source = [b"" for _ in range(max(25, source_line + 1))]
        if source_line:
            source[source_line - 1] = source_line_bytes
        (case / "verified/lib.rs").write_bytes(b"\n".join(source) + b"\n")
        calls = [{"callee": module.GENERATED_GLUE_NAME, "loc": negative_call_loc},
                 {"callee": "create_ref_mut", "loc": negative_call_loc}]
        result = module._body_glue_negative_gate(
            name, case, row, log, list(error_lines), list(dead_lines),
            {"call_nodes": calls}, {"admitted": True}, True, natural_exit,
            caller_return, caller_leak)
        assert result["matched"], (name, result)
        assert result["admitted"]
        result_no_setup = module._body_glue_negative_gate(
            name, case, row, log, list(error_lines), list(dead_lines),
            {"call_nodes": calls}, {"admitted": True}, False, natural_exit,
            caller_return, caller_leak)
        assert result_no_setup["matched"] and not result_no_setup["admitted"]

def markers(loc, *items):
    return "".join(f"  0.123s: {loc}: {item}\n" for item in items)

source_line_bytes = b" " * 19 + b"false"
negative_call_loc = "verified/lib.rs(18,9-10)"
false_loc = "verified/lib.rs(20,20-25)"
false_log = markers(negative_call_loc, "Executing statement", "Verifying call")
false_error = false_loc + ": error: Assertion might not hold. (Cannot prove false.)"
run_negative("after_natural_drop_false",
             {"false_line": 20, "natural_scope_end_line": 19,
              "target_stage": "after_natural_drop"}, 20,
             false_log, [false_error])
negative_call_loc = "verified/lib.rs(21,9-10)"
run_negative("caller_ready_entry_false",
             {"false_line": 20, "natural_scope_end_line": 22,
              "target_stage": "caller_ready_entry_before_scope_exit"}, 20,
             "", [false_error], natural_exit=False)

source_line_bytes = b"receiver precondition"
negative_call_loc = "verified/lib.rs(20,9-10)"
receiver_error = (negative_call_loc +
                  ": error: No matching heap chunks: CopyOnDrop_len(gap_guard_addr, _)")
run_negative("missing_receiver_frame", {"expected_missing": "receiver_frame"}, 20,
             markers(negative_call_loc, "Executing statement", "Consuming object"),
             [receiver_error], natural_exit=False)

source_line_bytes = b"    [1/4]src[..1] |-> cons(?current, nil) &*& dst[..1] |-> _ &*&"
negative_call_loc = "verified/lib.rs(9,5-10)"
source_permission_error = (
    "/bin/rust/prelude_core.rsspec(264,12-15): error: No matching heap chunks: "
    "[1/4]points_to<u64>(get_CopyOnDrop_src(mk_CopyOnDrop(fn_outcome_result(outcome0), tail0, 1)), _)")
source_log = (
    "verified/lib.rs(7,13-18): Producing predicate chunk\n"
    "verified/lib.rs(8,1-2): Executing statement\n"
    "verified/lib.rs(8,13-19): Verifying call\n"
    "verified/lib.rs(9,1-2): Executing statement\n"
    "verified/lib.rs(9,5-10): Verifying call\n"
    "verified/lib.rs(9,5-10): Executing statement\n"
    "verified/lib.rs(9,5-10): Verifying call\n"
    "verified/lib.rs(9,5-10): note: Verifying call\n"
    "verified/lib.rs(5,5-6): note: Consuming assertion\n"
    "prelude_core.rsspec(259,6-11): Auto-closing predicate with coefficient 1/4\n"
    + source_permission_error + "\n")
run_negative("missing_source_permission",
             {"expected_missing": "source_permission", "natural_scope_end_line": 10},
             5, source_log, [source_permission_error], natural_exit=False)

source_token = b"CopyOnDrop_drop_effect"
source_line_bytes = b"  " + source_token + b" &*& " + source_token
second_start = source_line_bytes.find(source_token, source_line_bytes.find(source_token) + 1) + 1
negative_call_loc = "verified/lib.rs(18,9-10)"
effect_error = (f"verified/lib.rs(20,{second_start}-{second_start + len(source_token)}): error: "
                "No matching heap chunks: CopyOnDrop_drop_effect(t, held_ref, tail0, 1)")
run_negative("duplicate_effect_simultaneous", {"double_effect_line": 20}, 20,
             markers(negative_call_loc, "Executing statement", "Verifying call"),
             [effect_error])

source_line_bytes = b" " * 25 + b"assert true"
negative_call_loc = "verified/lib.rs(18,9-10)"
run_negative("caller_dead_code", {"dead_control_line": 20}, 20,
             markers(negative_call_loc, "Executing statement", "Verifying call"),
             dead_lines=["verified/lib.rs(20,26-32): dead code"],
             caller_return=True, caller_leak=True)

def receiver_function(name, lifetime, guard="CopyOnDrop"):
    loc = ast_parser.Node("loc", ["verified/lib.rs(1,1-2)"])
    region = ast_parser.Node("IdentTypeExpr", [loc, ast_parser.Sym("None"), lifetime])
    referent = ast_parser.Node("StructTypeExpr", [loc, ast_parser.Node("Some", [guard]),
                                                   ast_parser.Sym("None"), [], []])
    ref = ast_parser.Node("RustRefTypeExpr", [loc, region, ast_parser.Sym("Mutable"), referent])
    const_ref = ast_parser.Node("ConstTypeExpr", [loc, ref])
    return ast_parser.Node("Func", [loc, ast_parser.Sym("Regular"), [(lifetime, ast_parser.Sym("None"))],
                                    ast_parser.Sym("None"), name, [(const_ref, "self")],
                                    ast_parser.Sym("false"), (ast_parser.Sym("None"), ast_parser.Sym("None")),
                                    ast_parser.Sym("None"), ast_parser.Sym("false"), ast_parser.Sym("None"),
                                    ast_parser.Sym("false"), []])

selected = receiver_function("<CopyOnDrop as core::ops::Drop>::drop", "'a")
glue = receiver_function("__vf_generated_drop_glue", "'a")
assert module._receiver_lifetime_signature(glue, selected, ast_parser, "CopyOnDrop")["admitted"]
assert not module._receiver_lifetime_signature(
    receiver_function("__vf_generated_drop_glue", "'b"), selected, ast_parser,
    "CopyOnDrop")["admitted"]
assert not module._receiver_lifetime_signature(
    receiver_function("__vf_generated_drop_glue", "'a", "Other"), selected, ast_parser,
    "CopyOnDrop")["admitted"]
print("PASS_SERVICE_ONLY: generated glue requires unique local runtime proof evidence")
