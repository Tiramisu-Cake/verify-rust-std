"""Synthetic strict owner/span dispatch-trace join controls."""
import hashlib
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).parent
SPEC = importlib.util.spec_from_file_location("a1_dispatch_trace_test", HERE / "a1-runner.py")
m = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = m
SPEC.loader.exec_module(m)

SRC = "a" * 64
CALLEES = {
    "quicksort": ("StableSmallSortTypeImpl::small_sort_threshold",
                  "StableSmallSortTypeImpl::small_sort"),
    "a1_guard_observer": ("StableSmallSortTypeImpl::small_sort_threshold",),
}


def sample():
    expected, rows = {}, []
    per_owner = {}
    line = 11
    for owner, callees in CALLEES.items():
        mir_calls, ast_calls = [], []
        for callee in callees:
            loc = f"verified/lib.rs({line},1-8)"
            bounds = (("verified/lib.rs", line, 1), ("verified/lib.rs", line, 8))
            mir_bounds = (("verified/lib.rs", line, 2), ("verified/lib.rs", line, 9))
            mir = {"callee": callee, "call_line": line,
                   "mir_call_span_ast": mir_bounds, "expected_ast_arguments": ()}
            ast = {"callee": callee, "ast_call_span": loc,
                   "ast_call_span_bounds": bounds}
            mir_calls.append(mir); ast_calls.append(ast)
            mir_loc = f"verified/lib.rs({line},2-9)"
            rows.append(f"SORT4-A1-DISPATCH: owner={owner} ast_call={loc} mir_call={mir_loc} "
                        f"original={callee} translated={callee} redirect=false")
            expected[(owner, callee)] = (loc, mir_loc, line, bounds)
            line += 1
        binding = {"caller": owner,
                   "case_binding": {"case_id": "P-dispatch",
                                    "generated_source_sha256": SRC},
                   "proof_credit": False, "calls": mir_calls}
        per_owner[owner] = {"mir": {"binding": binding},
                            "ast": {"owner": owner,
                                    "classification": "CALL_AST_STRUCTURE_ONLY",
                                    "proof_credit": False, "calls": ast_calls}}
    return rows, {"caller_calls": {"dispatch_pair": per_owner}}


class DispatchTraceJoin(unittest.TestCase):
    def classify(self, rows, structure):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "verification.log"
            log.write_text("\n".join(rows) + "\n")
            digest = hashlib.sha256(log.read_bytes()).hexdigest()
            raw = {"case_id": "P-dispatch", "source_pair_sha256": {"verified": SRC},
                   "paired_support": {"paired_support_passed": True},
                   "stages": {"verification": {"exit": 0, "log_sha256": digest}},
                   "evidence_root": tmp,
                   "artifacts": {"proof-ast.ml": {"sha256": "b" * 64}}}
            return m.classify_dispatch_observation(raw, expected_source_sha256=SRC,
                                                   structure=structure)

    def test_exact_three_owner_span_bijection(self):
        rows, structure = sample()
        result = self.classify(rows, structure)
        self.assertEqual(result["classification"], "ORIGINAL_COMMON_TRAIT_DISPATCH_OBSERVED")
        self.assertFalse(result["proof_credit"])
        self.assertEqual(len(result["trace_lines"]), 3)

    def test_missing_duplicate_unknown_owner_redirect_and_wrong_span_fail_closed(self):
        rows, structure = sample()
        mutations = [[], rows[:-1], rows + [rows[0]],
                     [rows[0].replace("owner=quicksort", "owner=other"), *rows[1:]],
                     [rows[0].replace("redirect=false", "redirect=true"), *rows[1:]],
                     [rows[0].replace("(11,1-8)", "(11,2-8)"), *rows[1:]],
                     [rows[0].replace("mir_call=verified/lib.rs(11,2-9)",
                                      "mir_call=verified/lib.rs(11,3-9)"), *rows[1:]]]
        for changed in mutations:
            with self.subTest(changed=changed[0] if changed else "zero rows"):
                self.assertEqual(self.classify(changed, structure)["classification"],
                                 "INCONCLUSIVE_DISPATCH_OBSERVATION")

    def test_missing_or_mismatched_caller_binding_fails_closed(self):
        rows, structure = sample()
        self.assertEqual(self.classify(rows, {})["classification"],
                         "INCONCLUSIVE_DISPATCH_OBSERVATION")
        structure["caller_calls"]["dispatch_pair"]["quicksort"]["mir"]["binding"]["calls"][0]["mir_call_span_ast"] = (("verified/lib.rs", 99, 1), ("verified/lib.rs", 99, 8))
        self.assertEqual(self.classify(rows, structure)["classification"],
                         "INCONCLUSIVE_DISPATCH_OBSERVATION")

    def test_stale_source_and_log_digest_fail_closed(self):
        rows, structure = sample()
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "verification.log"
            log.write_text("\n".join(rows) + "\n")
            raw = {"case_id": "P-dispatch", "source_pair_sha256": {"verified": "c" * 64},
                   "paired_support": {"paired_support_passed": True},
                   "stages": {"verification": {"exit": 0,
                                "log_sha256": hashlib.sha256(log.read_bytes()).hexdigest()}},
                   "evidence_root": tmp,
                   "artifacts": {"proof-ast.ml": {"sha256": "b" * 64}}}
            self.assertEqual(m.classify_dispatch_observation(
                raw, expected_source_sha256=SRC, structure=structure)["classification"],
                "INCONCLUSIVE_DISPATCH_OBSERVATION")
            raw["source_pair_sha256"]["verified"] = SRC
            raw["stages"]["verification"]["log_sha256"] = "0" * 64
            self.assertEqual(m.classify_dispatch_observation(
                raw, expected_source_sha256=SRC, structure=structure)["classification"],
                "INCONCLUSIVE_DISPATCH_OBSERVATION")

    def test_malformed_span_leaf_fails_closed_without_exception(self):
        rows, structure = sample()
        structure["caller_calls"]["dispatch_pair"]["quicksort"]["ast"]["calls"][0]["ast_call_span_bounds"] = ((), ())
        result = self.classify(rows, structure)
        self.assertEqual(result["classification"], "INCONCLUSIVE_DISPATCH_OBSERVATION")


if __name__ == "__main__":
    unittest.main()
