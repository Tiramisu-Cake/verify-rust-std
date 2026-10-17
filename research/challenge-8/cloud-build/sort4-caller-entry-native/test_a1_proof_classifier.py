"""Synthetic diagnostic controls; no compiler, verifier, or proof imports."""
import importlib.util
from pathlib import Path
import unittest

SPEC = importlib.util.spec_from_file_location(
    "a1_proof_classifier_test", Path(__file__).with_name("a1-proof-classifier.py"))
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


def observation(case="N-default-contract", code=1):
    return {"case_id": case, "focus_is_export_or_translation_filter": False,
            "paired_support": {"paired_support_passed": True},
            "stages": {**{key: {"exit": 0} for key in m.SUPPORT_STAGES},
                       "verification": {"exit": code}},
            "artifacts": {"proof-ast.ml": {"sha256": "synthetic-ast"}},
            "focus_source_line": 30, "focus": "verified/lib.rs:30",
            "focus_stage": "bodies"}


GATES = {"threshold": {"classification": "STRUCTURE_ONLY_UNRUN_PROOF",
                       "stage": "bodies", "impls": {"default16": {"source_line": 30, "diagnostic_post_line": 30, "alias": "__a1_impl_11_item_12_small_sort_threshold"}}}}


class ClassifierControls(unittest.TestCase):
    def classify(self, obs=None, log=None):
        if log is None:
            log = ("verified/lib.rs(30,1): error: Cannot prove 33 <= 32.\n"
                   "verified/lib.rs(30,1-32,1): note: Verifying function '__a1_impl_11_item_12_small_sort_threshold'")
        obs = obs or observation()
        return m.classify_focus(obs["case_id"], obs, GATES, "", log)

    def test_intended_failure_keeps_body_unverified_and_no_conformance_claim(self):
        row = self.classify()
        self.assertTrue(row["intended_failure_observed"])
        self.assertFalse(row["body_verified"])
        self.assertIsNone(row["native_conformance_verified"])
        self.assertIsNone(row["body_count"])
        self.assertFalse(row["proof_credit"])

    def test_first_error_wins_over_later_matching_failure(self):
        row = self.classify(log=("verified/lib.rs(12,1): error: Cannot prove 0 <= 1.\n"
                                 "verified/lib.rs(30,1): error: Cannot prove 33 <= 32."))
        self.assertFalse(row["candidate_passed"])

    def test_wrong_predicate_or_location_is_inconclusive(self):
        for log in ("verified/lib.rs(31,1): error: Cannot prove 33 <= 32.",
                    "verified/lib.rs(30,1): error: Cannot prove 33 <= 31.",
                    "verified/lib.rs(30,1): error: No matching heap chunks:"):
            self.assertFalse(self.classify(log=log)["candidate_passed"])

    def test_earlier_failed_export_cannot_count_as_negative(self):
        obs = observation()
        obs["stages"]["normal-export"] = {"exit": 1}
        row = self.classify(obs)
        self.assertFalse(row["candidate_passed"])
        self.assertEqual(row["first_causal_stage"], "normal-export")

    def test_missing_ast_cannot_count_as_negative(self):
        obs = observation()
        obs["artifacts"] = {}
        self.assertFalse(self.classify(obs)["candidate_passed"])

    def test_vf0_is_candidate_without_body_count_or_conformance_attestation(self):
        row = self.classify(observation("P0a", 0), "0 errors found")
        self.assertTrue(row["candidate_passed"])
        self.assertTrue(row["body_verified"])
        self.assertIsNone(row["body_count"])
        self.assertIsNone(row["native_conformance_verified"])
        self.assertFalse(row["proof_credit"])

    def test_vf0_does_not_satisfy_negative(self):
        self.assertFalse(self.classify(observation(code=0), "0 errors found")["candidate_passed"])

    def test_native_post_location_is_separate_from_mir_focus_line(self):
        gates = {"threshold": {**GATES["threshold"], "impls": {
            "default16": {"source_line": 30, "diagnostic_post_line": 26,
                          "alias": "__a1_impl_11_item_12_small_sort_threshold"}}}}
        for line, expected in ((26, True), (30, False)):
            row = m.classify_focus("N-default-contract", observation(), gates, "",
                f"verified/lib.rs({line},1): error: Cannot prove 33 <= 32.\n"
                "verified/lib.rs(30,1-32,1): note: Verifying function '__a1_impl_11_item_12_small_sort_threshold'")
            self.assertEqual(row["candidate_passed"], expected)

    def test_header_failure_cannot_be_reported_as_body_failure(self):
        log = ("verified/lib.rs(30,1): error: Cannot prove 33 <= 32.\n"
               "verified/lib.rs(30,1-32,1): note: Function '__a1_impl_11_item_12_small_sort_threshold': Function prototype implementation check")
        row = self.classify(log=log)
        self.assertFalse(row["candidate_passed"])
        self.assertEqual(row["error_context"]["stage"], "prototype-conformance")

    def test_missing_wrong_alias_wrong_line_and_duplicate_body_frames_refuse(self):
        error = "verified/lib.rs(30,1): error: Cannot prove 33 <= 32.\n"
        frame = "verified/lib.rs(30,1-32,1): note: Verifying function '__a1_impl_11_item_12_small_sort_threshold'"
        for suffix in ("", frame.replace("item_12", "item_13"),
                       frame.replace("(30,", "(31,"), frame + "\n" + frame):
            self.assertFalse(self.classify(log=error + suffix)["candidate_passed"])

    def test_body_frame_from_another_error_cannot_repair_first_failure(self):
        log = ("verified/lib.rs(30,1): error: Cannot prove 33 <= 32.\n"
               "verified/lib.rs(50,1): error: second diagnostic\n"
               "verified/lib.rs(30,1-32,1): note: Verifying function '__a1_impl_11_item_12_small_sort_threshold'")
        self.assertFalse(self.classify(log=log)["candidate_passed"])


if __name__ == "__main__":
    unittest.main()
