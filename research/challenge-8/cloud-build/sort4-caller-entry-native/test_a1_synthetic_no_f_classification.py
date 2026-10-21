"""Synthetic controls for the exact R12 no_F translator refusal classifier."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "a1_synthetic_no_f_test_backend", HERE / "a1-synthetic-backend.py")
assert SPEC is not None and SPEC.loader is not None
BACKEND = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BACKEND)

IDENTITY_GUARD = "A1 type parameter identity table mismatch"
GENERIC_GUARD = "A1 HIR/compiler method generic mismatch"


def observation(*, exit_code=1, classification="TERMINAL"):
    with tempfile.TemporaryDirectory() as tmp:
        ast = Path(tmp) / "synthetic-ast.ml"
        ast.write_text("synthetic AST placeholder\n", encoding="utf-8")
        return {"stages": {"synthetic-translator": {
            "classification": classification, "exit": exit_code}},
            "ast_path": str(ast), "synthetic": True,
            "compiler_derived": False, "refinement_derived": False,
            "proof_credit": False}


class NoFClassifierTests(unittest.TestCase):
    def classify(self, diagnostic, *, exit_code=1, classification="TERMINAL",
                 mutation="no_F"):
        return BACKEND.classify(observation(exit_code=exit_code,
                                            classification=classification),
                                mutation=mutation, verifier_log=diagnostic)

    def test_terminal_exact_identity_guard_refusal_is_classified(self):
        log = ("verified/lib.rs(35,8-18): error: "
               + IDENTITY_GUARD + "\n")
        result = self.classify(log)
        self.assertEqual(result["classification"], "SYNTHETIC_REFUSAL_OBSERVED")
        self.assertEqual(result["stage"], "interface")
        self.assertEqual(result["exit"], 1)
        self.assertEqual(result["first_diagnostic"], log.strip())
        self.assertEqual(result["diagnostic_match"], IDENTITY_GUARD)
        self.assertFalse(result["summary_available"])
        self.assertFalse(result["proof_credit"])
        self.assertFalse(result["compiler_derived"])
        self.assertFalse(result["refinement_derived"])

    def test_previous_exact_generic_refusal_remains_classified(self):
        result = self.classify(
            f"verified/lib.rs(35,8-18): error: {GENERIC_GUARD}\n")
        self.assertEqual(result["classification"], "SYNTHETIC_REFUSAL_OBSERVED")
        self.assertEqual(result["diagnostic_match"], GENERIC_GUARD)

    def test_arbitrary_embedded_wrong_source_or_other_mutation_refuse(self):
        cases = (
            f"verified/lib.rs(35,8-18): error: unrelated; {IDENTITY_GUARD}\n",
            f"verified/lib.rs(35,8-18): error: {IDENTITY_GUARD} plus unrelated\n",
            f"other.rs(35,8-18): error: {IDENTITY_GUARD}\n",
            f"verified/lib.rs(35,8-18): error: unrelated identity mismatch\n",
        )
        for log in cases:
            with self.subTest(log=log):
                self.assertEqual(self.classify(log)["classification"],
                                 "INCONCLUSIVE_SYNTHETIC_TRANSLATOR")
        self.assertEqual(self.classify(
            f"verified/lib.rs(35,8-18): error: {IDENTITY_GUARD}\n",
            mutation="binder_collapse")["classification"],
            "INCONCLUSIVE_SYNTHETIC_TRANSLATOR")

    def test_wrong_stage_exit_or_multiple_diagnostics_refuse(self):
        log = f"verified/lib.rs(35,8-18): error: {IDENTITY_GUARD}\n"
        self.assertEqual(self.classify(log, classification="RUNNING")["classification"],
                         "INCONCLUSIVE_SYNTHETIC_TRANSLATOR")
        self.assertEqual(self.classify(log, exit_code=0)["classification"],
                         "INCONCLUSIVE_SYNTHETIC_TRANSLATOR")
        self.assertEqual(self.classify(log, exit_code=True)["classification"],
                         "INCONCLUSIVE_SYNTHETIC_TRANSLATOR")
        self.assertEqual(self.classify(
            log + "verified/lib.rs(36,1): error: later unrelated error\n")["classification"],
            "INCONCLUSIVE_SYNTHETIC_TRANSLATOR")
        result = self.classify(log, classification="NOT_RUN")
        self.assertEqual(result["classification"], "INCONCLUSIVE_SYNTHETIC_TRANSLATOR")

    def test_wrong_missing_or_nonterminal_stage_refuses(self):
        log = f"verified/lib.rs(35,8-18): error: {IDENTITY_GUARD}\n"
        for stages in ({}, {"other-stage": {"classification": "TERMINAL", "exit": 1}},
                       {"synthetic-translator": {"classification": "RUNNING", "exit": 1}}):
            with self.subTest(stages=stages):
                result = BACKEND.classify({"stages": stages, "synthetic": True,
                                           "proof_credit": False},
                                          mutation="no_F", verifier_log=log)
                self.assertEqual(result["classification"],
                                 "INCONCLUSIVE_SYNTHETIC_TRANSLATOR")


if __name__ == "__main__":
    unittest.main()
