"""Synthetic false31 lifecycle test; no compiler or full runner invocation."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch


HERE = Path(__file__).resolve().parent


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


RUNNER = load("a1_false31_partial_runner_test", HERE / "a1-runner.py")
CLASSIFIER = load("a1_false31_partial_matrix_classifier_test",
                 HERE / "a1-matrix-classifier.py")


class False31PartialLifecycleTests(unittest.TestCase):
    def test_helper_blocked_caller_keeps_receipt_and_own_body_pair_inconclusive(self):
        native = {"classification": "STRUCTURE_ONLY_UNRUN_PROOF",
                  "normalized_posts": ["post-a", "post-b"]}
        pair_hashes = {"verified": "a" * 64, "original": "b" * 64}
        bodies = {}
        for focus, impl in (("P0a", "default16"), ("P0b", "freeze32")):
            bodies[focus] = {
                "case_id": "N-false31", "focus_case_id": focus,
                "raw": {"build_id": "build-r12",
                        "source_id": "false31-source", "unit_id": "false31-unit",
                        "source_pair_sha256": pair_hashes},
                "structure": {"threshold_posts": {"native": native}},
                "execution_attestation": {
                    "compiler_identity": {"impl": impl},
                    "body_count": 1, "focus_body_verified": True,
                    "focus_conformance_verified": True},
                "proof_candidate": {"classification": "FOCUSED_VF0_CANDIDATE",
                                    "candidate_passed": True, "body_verified": True},
                "proof_credit": False,
            }
        blocked_caller = {
            "classification": "BLOCKED_CHECKED_HELPER_PREREQUISITE",
            "case_id": "N-false31", "focus_case_id": "N-false31",
            "raw": {"build_id": "build-r12", "source_id": "false31-source",
                    "unit_id": "false31-unit", "source_pair_sha256": pair_hashes,
                    "checked_helper_proof": {"classification": "BLOCKED"}},
            "checked_helper_proof": {"classification": "BLOCKED"},
            "caller_verification_status": "NOT_RUN_CHECKED_HELPER_PREREQUISITE",
            "proof_attempted": False, "proof_credit": False,
        }

        def collect(*_args, focus_case_id, **_kwargs):
            return blocked_caller if focus_case_id == "N-false31" else bodies[focus_case_id]

        manifest = {case_id: {"source_id": f"{case_id}-source",
                              "unit_id": f"{case_id}-unit"}
                    for case_id in RUNNER.CASE_ORDER}
        progress = {}
        with patch.object(RUNNER, "collect_source_case", side_effect=collect), \
             patch.object(RUNNER, "publish_positive_threshold_receipt",
                          return_value=(object(), Path("/synthetic/false31-receipt.json"))) as publish, \
             patch.object(RUNNER, "observe_false31_boundary") as boundary:
            observed = RUNNER.draft_false31_pair_stage(
                object(), object(), object(), tool=Path("/unused/tool"),
                tool_receipt={}, profile={}, manifest={},
                certificate_path=Path("/unused/certificate.json"),
                certificate={"cases": {"N-false31": {
                    "source_id": "false31-source", "unit_id": "false31-unit"}}},
                source_package=Path("/unused/source"),
                positive_native_baseline=native, expected_cases=manifest,
                helpers={}, profile_sha256="c" * 64,
                support_cache={}, progress=progress)

        publish.assert_called_once()
        boundary.assert_not_called()
        self.assertEqual(observed["classification"],
                         "FALSE31_OWN_PAIR_RECEIPT_ISSUED_CALLER_BLOCKED")
        self.assertIs(observed["not_run"], False)
        self.assertIs(observed["execution_started"], True)
        self.assertEqual(observed["body_cases"], bodies)
        self.assertEqual(observed["caller_case"], blocked_caller)
        self.assertEqual(observed["source_pair_sha256"], pair_hashes)
        self.assertEqual(observed["receipt_path"], Path("/synthetic/false31-receipt.json"))
        self.assertIs(observed["receipt_issued_after_both_bodies"], True)
        self.assertEqual(observed["caller_stage"]["status"],
                         "NOT_RUN_CHECKED_HELPER_PREREQUISITE")
        self.assertIs(observed["caller_stage"]["caller_verification_started"], False)
        self.assertIs(observed["caller_stage"]["proof_attempted"], False)
        self.assertEqual(observed["boundary_stage"]["status"], "NOT_RUN")
        self.assertIs(observed["proof_credit"], False)
        self.assertEqual(progress["receipt_path"], str(observed["receipt_path"]))
        self.assertEqual(progress["caller_case"], blocked_caller)
        self.assertEqual(progress["caller_stage"], observed["caller_stage"])

        classified = CLASSIFIER.classify_case(
            "N-false31", observed,
            expected_input={"source_id": "false31-source", "unit_id": "false31-unit"},
            run_pins={"tool_id": "tool", "profile_id": "profile",
                      "proof_id": "proof", "infra_id": "infra",
                      "target_id": "target"},
            build_id="build-r12", expected_inventory={})
        self.assertEqual(classified["status"], "INCONCLUSIVE")
        self.assertIs(classified["matrix_gate_passed"], False)
        self.assertIsNone(classified["record"])
        expected_reason = "false31 caller/checked-helper prerequisite incomplete"
        self.assertEqual(classified["reason"], expected_reason)
        case_status = {}
        records = RUNNER._classify_native_target_rows(
            case_status, [], {"N-false31": observed}, {"N-false31"},
            {"N-false31": {"source_id": "false31-source",
                            "unit_id": "false31-unit"}},
            CLASSIFIER, {"tool_id": "tool"}, "build-r12", {})
        self.assertEqual(case_status["N-false31"]["status"], "INCONCLUSIVE")
        self.assertIs(case_status["N-false31"]["matrix_gate_passed"], False)
        self.assertEqual(case_status["N-false31"]["reason"], expected_reason)
        self.assertEqual(records, [])

    def test_missing_caller_structure_uses_separate_inconclusive_reason(self):
        native = {"classification": "STRUCTURE_ONLY_UNRUN_PROOF",
                  "normalized_posts": ["post-a", "post-b"]}
        pair_hashes = {"verified": "d" * 64, "original": "e" * 64}
        bodies = {}
        for focus, impl in (("P0a", "default16"), ("P0b", "freeze32")):
            bodies[focus] = {
                "raw": {"build_id": "build-r12", "source_id": "false31-source",
                        "unit_id": "false31-unit", "source_pair_sha256": pair_hashes},
                "structure": {"threshold_posts": {"native": native}},
                "execution_attestation": {
                    "compiler_identity": {"impl": impl}, "body_count": 1,
                    "focus_body_verified": True, "focus_conformance_verified": True},
                "proof_candidate": {"classification": "FOCUSED_VF0_CANDIDATE",
                                    "candidate_passed": True, "body_verified": True},
                "proof_credit": False,
            }
        incomplete_caller = {"classification": "INCONCLUSIVE_CURRENT_STAGE",
                             "raw": {"source_pair_sha256": pair_hashes},
                             "structure": None, "proof_credit": False}

        def collect(*_args, focus_case_id, **_kwargs):
            return incomplete_caller if focus_case_id == "N-false31" else bodies[focus_case_id]

        expected_cases = {case_id: {} for case_id in RUNNER.CASE_ORDER}
        with patch.object(RUNNER, "collect_source_case", side_effect=collect), \
             patch.object(RUNNER, "publish_positive_threshold_receipt",
                          return_value=(object(), Path("/synthetic/false31-receipt.json"))), \
             patch.object(RUNNER, "observe_false31_boundary") as boundary:
            observed = RUNNER.draft_false31_pair_stage(
                object(), object(), object(), tool=Path("/unused/tool"),
                tool_receipt={}, profile={}, manifest={},
                certificate_path=Path("/unused/certificate.json"),
                certificate={"cases": {"N-false31": {
                    "source_id": "false31-source", "unit_id": "false31-unit"}}},
                source_package=Path("/unused/source"),
                positive_native_baseline=native, expected_cases=expected_cases,
                helpers={}, profile_sha256="f" * 64, support_cache={}, progress={})

        boundary.assert_not_called()
        self.assertEqual(observed["classification"],
                         "FALSE31_OWN_PAIR_RECEIPT_ISSUED_CALLER_STRUCTURE_UNAVAILABLE")
        self.assertEqual(observed["caller_stage"]["status"],
                         "INCONCLUSIVE_CALLER_STRUCTURE_UNAVAILABLE")
        self.assertIsNone(observed["caller_stage"]["caller_verification_started"])
        self.assertIsNone(observed["caller_stage"]["proof_attempted"])
        self.assertIs(observed["proof_credit"], False)
        expected_reason = "false31 caller structure unavailable after own-pair receipt"
        classified = CLASSIFIER.classify_case(
            "N-false31", observed,
            expected_input={"source_id": "false31-source", "unit_id": "false31-unit"},
            run_pins={"tool_id": "tool", "profile_id": "profile",
                      "proof_id": "proof", "infra_id": "infra",
                      "target_id": "target"},
            build_id="build-r12", expected_inventory={})
        self.assertEqual(classified["status"], "INCONCLUSIVE")
        self.assertEqual(classified["reason"], expected_reason)
        self.assertIs(classified["matrix_gate_passed"], False)
        self.assertIsNone(classified["record"])
        case_status = {}
        records = RUNNER._classify_native_target_rows(
            case_status, [], {"N-false31": observed}, {"N-false31"},
            {"N-false31": {"source_id": "false31-source",
                            "unit_id": "false31-unit"}},
            CLASSIFIER, {"tool_id": "tool"}, "build-r12", {})
        self.assertEqual(case_status["N-false31"]["status"], "INCONCLUSIVE")
        self.assertEqual(case_status["N-false31"]["reason"], expected_reason)
        self.assertIs(case_status["N-false31"]["matrix_gate_passed"], False)
        self.assertEqual(records, [])

    def test_own_pair_exception_remains_an_exception_with_prior_attempt(self):
        native = {"classification": "STRUCTURE_ONLY_UNRUN_PROOF"}
        first = {"case_id": "N-false31", "focus_case_id": "P0a",
                 "raw": {"source_pair_sha256": {"verified": "a" * 64,
                                                "original": "b" * 64}},
                 "structure": {"threshold_posts": {"native": native}},
                 "execution_attestation": {"focus_body_verified": True,
                                            "focus_conformance_verified": True},
                 "proof_candidate": {"classification": "FOCUSED_VF0_CANDIDATE"},
                 "proof_credit": False}

        def collect(*_args, focus_case_id, **_kwargs):
            if focus_case_id == "P0b":
                raise RuntimeError("synthetic own Freeze body-stage failure")
            return first

        progress = {}
        with patch.object(RUNNER, "collect_source_case", side_effect=collect):
            with self.assertRaisesRegex(RuntimeError, "synthetic own Freeze body-stage failure"):
                RUNNER.draft_false31_pair_stage(
                    object(), object(), object(), tool=Path("/unused/tool"),
                    tool_receipt={}, profile={}, manifest={},
                    certificate_path=Path("/unused/certificate.json"),
                    certificate={"cases": {"N-false31": {}}},
                    source_package=Path("/unused/source"),
                    positive_native_baseline=native, expected_cases=None,
                    helpers={}, profile_sha256="c" * 64,
                    support_cache={}, progress=progress)
        self.assertEqual(progress["body_cases"]["P0a"], first)
        self.assertNotIn("receipt_path", progress)
        self.assertNotIn("caller_stage", progress)

    def test_body_pair_attempts_survive_missing_manifest_without_receipt(self):
        native = {"classification": "STRUCTURE_ONLY_UNRUN_PROOF",
                  "normalized_posts": ["post-a", "post-b"]}
        pair_hashes = {"verified": "a" * 64, "original": "b" * 64}
        bodies = {}
        for focus, impl in (("P0a", "default16"), ("P0b", "freeze32")):
            bodies[focus] = {
                "case_id": "N-false31", "focus_case_id": focus,
                "raw": {"build_id": "build-r12",
                        "source_id": "false31-source", "unit_id": "false31-unit",
                        "source_pair_sha256": pair_hashes},
                "structure": {"threshold_posts": {"native": native}},
                "execution_attestation": {
                    "compiler_identity": {"impl": impl},
                    "body_count": 1, "focus_body_verified": True,
                    "focus_conformance_verified": True},
                "proof_candidate": {"classification": "FOCUSED_VF0_CANDIDATE",
                                    "candidate_passed": True, "body_verified": True},
                "proof_credit": False,
            }

        def collect(*_args, focus_case_id, **_kwargs):
            return bodies[focus_case_id]

        malformed_rows = {case_id: {} for case_id in RUNNER.CASE_ORDER}
        malformed_rows["P0a"] = None
        extra_rows = {case_id: {} for case_id in RUNNER.CASE_ORDER}
        extra_rows["unexpected"] = {}
        extra_rows = {case_id: {} for case_id in RUNNER.CASE_ORDER}
        extra_rows["unexpected"] = {}
        caller_default = {}.get("expected_case_ids", {})
        manifest_inputs = (
            ("runner-default-empty", caller_default, "INCOMPLETE_OR_MALFORMED_CASE_MANIFEST"),
            ("incomplete", {"P0a": {}}, "INCOMPLETE_OR_MALFORMED_CASE_MANIFEST"),
            ("null", None, "EXPECTED_CASES_NOT_MAPPING"),
            ("wrong-type", [], "EXPECTED_CASES_NOT_MAPPING"),
            ("malformed-row", malformed_rows, "INCOMPLETE_OR_MALFORMED_CASE_MANIFEST"),
            ("extra-case", extra_rows, "INCOMPLETE_OR_MALFORMED_CASE_MANIFEST"),
            ("extra-case", extra_rows, "INCOMPLETE_OR_MALFORMED_CASE_MANIFEST"),
        )
        for label, expected_cases, manifest_classification in manifest_inputs:
            with self.subTest(manifest=label):
                progress = {}
                with patch.object(RUNNER, "collect_source_case", side_effect=collect):
                    observed = RUNNER.draft_false31_pair_stage(
                        object(), object(), object(), tool=Path("/unused/tool"),
                        tool_receipt={}, profile={}, manifest={},
                        certificate_path=Path("/unused/certificate.json"),
                        certificate={"cases": {"N-false31": {
                            "source_id": "false31-source", "unit_id": "false31-unit"}}},
                        source_package=Path("/unused/source"),
                        positive_native_baseline=native, expected_cases=expected_cases,
                        helpers={}, profile_sha256="c" * 64,
                        support_cache={}, progress=progress)

                self.assertEqual(observed["classification"],
                                 "FALSE31_BODY_PAIR_OBSERVED_CALLER_RECEIPT_NOT_RUN")
                self.assertIs(observed["not_run"], False)
                self.assertIs(observed["execution_started"], True)
                self.assertIs(observed["body_pair_attempted"], True)
                self.assertEqual(observed["body_cases"], bodies)
                self.assertEqual(observed["body_cases"]["P0a"]["raw"]["source_pair_sha256"],
                                 pair_hashes)
                self.assertEqual(observed["body_cases"]["P0b"]["raw"]["source_pair_sha256"],
                                 pair_hashes)
                self.assertEqual(observed["expected_case_manifest"]["classification"],
                                 manifest_classification)
                self.assertIs(observed["proof_credit"], False)
                self.assertIs(observed["receipt_issued_after_both_bodies"], False)
                self.assertEqual(observed["receipt_stage"]["status"], "NOT_RUN")
                self.assertEqual(observed["caller_stage"]["status"], "NOT_RUN")
                self.assertNotIn("receipt_path", observed)
                self.assertNotIn("caller_case", observed)
                self.assertIsNone(progress["receipt_path"])
                self.assertEqual(progress["receipt_stage"]["status"], "NOT_RUN")
                self.assertEqual(progress["caller_stage"]["status"], "NOT_RUN")

                # The actual matrix classifier must not consume the row's
                # not-run shortcut; incomplete receipt/caller evidence stays
                # inconclusive, never an accepted case.
                classified = CLASSIFIER.classify_case(
                    "N-false31", observed,
                    expected_input={"source_id": "false31-source",
                                    "unit_id": "false31-unit"},
                    run_pins={"tool_id": "tool", "profile_id": "profile",
                              "proof_id": "proof", "infra_id": "infra",
                              "target_id": "target"},
                    build_id="build-r12", expected_inventory={})
                self.assertEqual(classified["status"], "INCONCLUSIVE")
                self.assertIs(classified["matrix_gate_passed"], False)
                self.assertIsNone(classified["record"])

                case_status = {}
                rows = RUNNER._classify_native_target_rows(
                    case_status, [], {"N-false31": observed}, {"N-false31"},
                    {"N-false31": {"source_id": "false31-source",
                                    "unit_id": "false31-unit"}},
                    CLASSIFIER, {"tool_id": "tool"}, "build-r12", {})
                self.assertEqual(case_status["N-false31"]["status"], "INCONCLUSIVE")
                self.assertIs(case_status["N-false31"]["matrix_gate_passed"], False)
                self.assertEqual(rows, [])


if __name__ == "__main__":
    unittest.main()
