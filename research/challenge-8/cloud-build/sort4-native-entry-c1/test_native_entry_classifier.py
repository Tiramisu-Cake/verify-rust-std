"""Synthetic tests over AST-selected pure definitions from the production collector."""
from __future__ import annotations

import ast
import hashlib
import re
import tempfile
import unittest
from pathlib import Path


COLLECTOR = Path(__file__).resolve().parents[1] / "sort4-caller-entry.py"
TREE = ast.parse(COLLECTOR.read_text())
SELECTED = {
    "mir_basic_blocks", "matching_bracket", "mir_ghost_statement", "mir_line_blocks",
    "executed_line", "source_line", "native_entry_source_operations",
    "native_entry_mapping", "native_post_ast_evidence", "native_expected_negative", "positive_full_vf0",
    "native_case_targets_reached", "legacy_dead_code_vf1",
}
NAMES = {"NATIVE_ENTRY_CERT_CLASS", "NATIVE_ENTRY_OPERATIONS"}
DEFS = [node for node in TREE.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in SELECTED]
CONSTANTS = [node for node in TREE.body if isinstance(node, (ast.Assign, ast.AnnAssign)) and
             any(isinstance(target, ast.Name) and target.id in NAMES
                 for target in (node.targets if isinstance(node, ast.Assign) else [node.target]))]
MODULE = ast.Module(body=CONSTANTS + DEFS, type_ignores=[])
namespace = {"hashlib": hashlib, "re": re, "Path": Path, "sha": lambda p: hashlib.sha256(p.read_bytes()).hexdigest()}
exec(compile(ast.fix_missing_locations(MODULE), str(COLLECTOR), "exec"), namespace)


def operation_rows(source: bytes) -> dict:
    result = {}
    for name, statement in namespace["NATIVE_ENTRY_OPERATIONS"]:
        content_offset = source.index(statement)
        line_start = source.rfind(b"\n", 0, content_offset) + 1
        line_end = source.find(b"\n", content_offset)
        exact = source[line_start:line_end + 1]
        result[name] = {
            "source_byte_start": line_start,
            "caller_relative_byte_start": line_start,
            "source_line": source.count(b"\n", 0, line_start) + 1,
            "verified_source_line": source.count(b"\n", 0, line_start) + 1,
            "lemma_byte_start": line_start,
            "statement_sha256": hashlib.sha256(exact).hexdigest(),
            "exact_statement_bytes": exact.decode(),
        }
    return result


class NativeSourceTests(unittest.TestCase):
    def test_exact_source_spans_pass(self):
        statements = [value for _, value in namespace["NATIVE_ENTRY_OPERATIONS"]]
        source = b"fn small_sort_general_with_scratch<T>() {\n" + b"\n".join(b"    " + x for x in statements) + b"\n}\n"
        rows = operation_rows(source)
        cert = {"source_certificate": {"caller_byte_start": 0,
                                        "caller_start_line": 1,
                                        "full_original_caller_sha256": hashlib.sha256(source[:-1]).hexdigest()},
                "source_mapped_condition_bytes": {"operation_map": rows}}
        result = namespace["native_entry_source_operations"](source, source, cert)
        self.assertEqual(result["status"], "PASS")

    def test_modified_operation_bytes_fail_closed(self):
        statements = [value for _, value in namespace["NATIVE_ENTRY_OPERATIONS"]]
        source = b"fn small_sort_general_with_scratch<T>() {\n" + b"\n".join(b"    " + x for x in statements) + b"\n}\n"
        rows = operation_rows(source)
        rows["scratch_base"]["statement_sha256"] = "0" * 64
        cert = {"source_certificate": {"caller_byte_start": 0,
                                        "caller_start_line": 1,
                                        "full_original_caller_sha256": hashlib.sha256(source[:-1]).hexdigest()},
                "source_mapped_condition_bytes": {"operation_map": rows}}
        result = namespace["native_entry_source_operations"](source, source, cert)
        self.assertEqual(result["status"], "NOT_CONFIRMED")

    def test_certificate_to_mir_ghost_and_trace_mapping(self):
        signature = b"fn small_sort_general_with_scratch<T>() "
        statements = [value for _, value in namespace["NATIVE_ENTRY_OPERATIONS"]]
        lines = [signature + b"{\n"] + [b"    " + x + b"\n" for x in statements]
        lines.append(b"    //@ assert len >= 8; // FIRST_SORT4_CALLSITE_BOUNDARY\n")
        lines.append(b"}\n")
        source = b"".join(lines)
        rows = operation_rows(source)
        cert = {
            "classification": namespace["NATIVE_ENTRY_CERT_CLASS"],
            "source_certificate": {
                "caller_byte_start": 0, "caller_start_line": 25,
                "full_original_caller_sha256": hashlib.sha256(source[:-1]).hexdigest(),
                "native_entry_signature_exact": True,
                "native_entry_is_separate_resource_lemma": True,
                "native_entry_signature": signature.decode(),
                "caller_signature_sha256": hashlib.sha256(signature).hexdigest(),
            },
            "native_entry_contract": {
                "signature_is_exact_actual_caller_signature": True,
                "full_native_precondition_from_generated_mutable_reference_contract": True,
                "automatic_native_normal_post_checked": True,
                "automatic_native_unwind_post_checked": True,
                "automatic_native_leak_check_required": True,
                "all_lengths_admitted": True, "all_scratch_lengths_admitted": True,
                "zst_admitted": True, "no_runtime_guard_or_caller_cfg_projection": True,
            },
            "source_mapped_condition_bytes": {
                "operation_map": rows, "source_runtime_identity_claim": False,
                "caller_cfg_projection_claim": False, "ghost_boundary_marker": "FIRST_SORT4_CALLSITE_BOUNDARY",
                "ghost_boundary_is_artificial": True,
            },
            "ghost_boundary_is_artificial": True,
        }
        actual = source
        basic_lines = ", ".join(f"line = {i}," for i in range(1, len(lines)))
        record = ("basicBlocks = [\n  ( id = (index = 0), " + basic_lines + " )\n]\n" +
                  "ghostStmts = [\n  ( raw = \"assert len >= 8; // FIRST_SORT4_CALLSITE_BOUNDARY\", startLine = 7, endLine = 7, span = 0 )\n]\n")
        log = "".join(f"1.0s: verified/lib.rs({i},1-8): Executing statement\n" for i in (2, 3, 4, 6, 7))
        with tempfile.TemporaryDirectory() as temp:
            fixture = Path(temp)
            (fixture / "verified").mkdir()
            (fixture / "verified/lib.rs").write_bytes(source)
            (fixture / "actual-caller.rs").write_bytes(actual)
            # Rebuild offsets against the exact caller payload saved above.
            cert["source_certificate"]["full_original_caller_sha256"] = hashlib.sha256(actual[:-1]).hexdigest()
            for row in rows.values():
                row["source_byte_start"] = row["caller_relative_byte_start"]
            mapping = namespace["native_entry_mapping"](fixture, cert, record, record, log, 0)
        self.assertEqual(mapping["status"], "PASS", mapping)


class ClassifierTests(unittest.TestCase):
    def test_positive_targets_are_case_specific(self):
        cert = {"targeted_ghost_statement_lines": {"native_scratch_array": 8},
                "targeted_ghost_statement_line_lists": {"native_scratch_owners": [9, 10]}}
        log = "".join(f"1.0s: verified/lib.rs({line},1-8): Executing statement\n" for line in (8, 9, 10))
        self.assertTrue(namespace["native_case_targets_reached"]("native-scratch-frame", cert, log))
        self.assertFalse(namespace["native_case_targets_reached"]("native-scratch-frame", cert, log.replace("(10,", "(11,")))

    def test_post_capture_requires_both_return_arms_and_native_contract(self):
        cert = {"native_entry_contract": {
            "automatic_native_normal_post_checked": True,
            "automatic_native_unwind_post_checked": True,
            "automatic_native_leak_check_required": True,
            "all_lengths_admitted": True, "all_scratch_lengths_admitted": True,
            "zst_admitted": True, "no_runtime_guard_or_caller_cfg_projection": True,
            "native_post_source": "stock generated contract for the exact signature; not hand-written or strengthened",
        }}
        ast_text = ('[\n Func (loc "verified/lib.rs(1,1-8,2)", Regular, [], '
                    'Some (ConstructedTypeExpr ("fn_outcome")), "small_sort_general_with_scratch", [\n'
                    ' SwitchExpr (loc, "outcome", Var (loc, "outcome"), [\n'
                    ' SwitchExprClause (loc, "returning", [], true),\n'
                    ' SwitchExprClause (loc, "unwinding", [], true)\n ])\n]\n')
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "proof-ast.ml"
            path.write_text(ast_text)
            self.assertEqual(namespace["native_post_ast_evidence"](path, cert)["status"], "PASS")
            path.write_text(ast_text.replace('"unwinding"', '"other"'))
            self.assertEqual(namespace["native_post_ast_evidence"](path, cert)["status"], "NOT_CONFIRMED")

    def test_trace_qualifier_and_dead_code_vf1_are_retained(self):
        trace = "1.0s: verified/lib.rs(4,1-10): Executing statement\n"
        self.assertTrue(namespace["executed_line"](trace, 4))
        self.assertFalse(namespace["executed_line"](trace.replace("Executing statement", "Executing declaration"), 4))
        self.assertTrue(namespace["legacy_dead_code_vf1"](["verified/lib.rs(7,1-8): dead code"]))
        self.assertFalse(namespace["legacy_dead_code_vf1"](["verified/lib.rs(7,1-8): error: Cannot prove condition"]))

    def test_positive_needs_controls_support_mapping_and_full_vf0(self):
        good = dict(controls_passed=True, support_gates_passed=True,
                    source_mir_trace_passed=True, verifier_exit=0,
                    proof_entries=[20], caller_log="Leak check.", errors=[],
                    full_vf0_log=True, full_native_contract=True)
        self.assertTrue(namespace["positive_full_vf0"]("native-scratch-frame", **good))
        good["source_mir_trace_passed"] = False
        self.assertFalse(namespace["positive_full_vf0"]("native-scratch-frame", **good))

    def test_negative_requires_single_marker_pinned_error(self):
        verified = b"fn entry() {\n    array_split::<T>(v_base, 9); // RANGE_AUTHORITY_CONTROL\n}\n"
        cert = {"expected_negative_first_error": {
            "marker": "RANGE_AUTHORITY_CONTROL",
            "obligation": "array_split at 9 with len==8",
        }}
        log = "1.0s: verified/lib.rs(2,5-10): Executing statement\n"
        self.assertTrue(namespace["native_expected_negative"](
            "range-negative", cert, verified, log, [0],
            ["verified/lib.rs(2,5-10): error: Cannot prove condition."], 1))
        self.assertFalse(namespace["native_expected_negative"](
            "range-negative", cert, verified, log, [0],
            ["verified/lib.rs(2,5-10): error: unrelated failure"], 1))


if __name__ == "__main__":
    unittest.main()
