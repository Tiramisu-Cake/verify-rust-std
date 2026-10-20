"""Pure controls for the R10 bounded P1 target route and report view."""
from __future__ import annotations

import copy
import json
import unittest

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


HERE = Path(__file__).parent
SPEC = spec_from_file_location("a1_r10_target_test_runner", HERE / "a1-runner.py")
assert SPEC is not None and SPEC.loader is not None
RUNNER = module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)
R9 = "SORT4-NATIVE-INTERFACE-PROOF-2026-10-20-R9"
R10 = "SORT4-DELIVERABLE-NATIVE-PROOF-2026-10-20-R10"


class RecordingClassifier:
    def __init__(self, *, error=None):
        self.calls = []
        self.error = error

    def classify_case(self, case_id, observation, **kwargs):
        self.calls.append((case_id, observation, kwargs))
        if self.error is not None:
            raise self.error
        return {"case_id": case_id, "status": "INTENDED_CLASSIFIED",
                "matrix_gate_passed": True, "observed_classification": "synthetic",
                "record": {"case_id": case_id, "source_id": "source-id",
                           "unit_id": "unit-id", "stage": "test-stage"},
                "proof_credit": False}


class NativeTargetSequenceTests(unittest.TestCase):
    def test_partial_prerequisite_views_guard_nested_null_and_wrong_types(self):
        malformed = (
            None, [],
            {"positive_cases": None},
            {"positive_cases": []},
            {"positive_cases": {"P0a": None}},
            {"positive_cases": {"P0a": {"raw": None, "structure": []}}},
            {"positive_cases": {"P0a": {"raw": [], "structure": {
                "bound_impls": None, "inventory": {"inventory": {"impls": [None]}}}}}},
            {"positive_cases": {"P0a": {"raw": {"artifacts": []}, "structure": {
                "bound_impls": [], "inventory": []}}}},
        )
        for progress in malformed:
            with self.subTest(progress=progress):
                before = copy.deepcopy(progress)
                context = RUNNER._native_target_context(progress)
                self.assertIsInstance(context["p0a"], dict)
                self.assertIsInstance(context["p0a_raw"], dict)
                self.assertEqual(context["artifacts"], {})
                self.assertEqual(context["bound_impls"], {})
                self.assertEqual(context["impls"], [])
                self.assertEqual(progress, before)

    def test_partial_context_preserves_valid_raw_data_and_does_not_mutate_it(self):
        progress = {"positive_cases": {"P0a": {
            "raw": {"source_pair_sha256": {"verified": "v"},
                    "artifacts": {"normal-mir.txt": {"path": "/same-build/mir"}}},
            "structure": {"inventory": {"inventory": {"impls": [
                {"impl": "default16"}, None]}}, "bound_impls": {"default16": {"id": "x"}}}}}}
        before = copy.deepcopy(progress)
        context = RUNNER._native_target_context(progress)
        self.assertIs(context["p0a_raw"], progress["positive_cases"]["P0a"]["raw"])
        self.assertIn("normal-mir.txt", context["artifacts"])
        self.assertEqual(context["impls"], [{"impl": "default16"}])
        self.assertEqual(context["bound_impls"], {"default16": {"id": "x"}})
        self.assertEqual(progress, before)

    def test_exact_stage_order_and_timeout_partial_observations_are_preserved(self):
        calls = []
        timeout = {"not_run": True, "execution_started": False,
                   "reason": "shared deadline left no stage budget", "proof_credit": False}
        partial = {"adapter_error": "ValueError: primary collection error",
                   "partial_artifacts": {"path": None}, "proof_credit": False}

        def run_stage(case_id, callback):
            calls.append((case_id, callback()))
            return calls[-1][1]

        result = RUNNER._run_native_target_sequence(
            run_stage, p1_action=lambda: timeout,
            binding_actions={"N-binding": lambda: partial,
                             "N-region-swap": lambda: {"classification": "OK"}},
            alpha_action=lambda: {"classification": "PARTIAL_ALPHA"})
        self.assertEqual([case for case, _ in calls],
                         ["P1", "N-binding", "N-region-swap", "N-alpha-valid"])
        self.assertIs(result["P1"], timeout)
        self.assertIs(result["N-binding"], partial)
        self.assertEqual(result["N-binding"]["adapter_error"],
                         "ValueError: primary collection error")
        self.assertEqual(result["N-alpha-valid"]["classification"], "PARTIAL_ALPHA")

    def test_missing_prerequisites_are_explicit_not_run(self):
        calls = []
        result = RUNNER._run_native_target_sequence(
            lambda case, fn: (calls.append(case), fn())[1], p1_action=None,
            binding_actions={}, alpha_action=None)
        self.assertEqual(calls, [])
        self.assertEqual(result["P1"]["not_run"], True)
        self.assertEqual(result["N-binding"]["not_run"], True)
        self.assertEqual(result["N-region-swap"]["not_run"], True)
        self.assertEqual(result["N-alpha-valid"]["not_run"], True)
        self.assertTrue(all(row.get("reason") for row in result.values()))

    def test_only_target_rows_are_classified_and_all_26_rows_remain(self):
        classifier = RecordingClassifier()
        statuses = {case: {"status": "NOT_RUN", "proof_credit": False}
                    for case in RUNNER.CASE_ORDER}
        rows = []
        observations = {"P1": {"classification": "P1_FULL_INTERFACE_OBSERVED"},
                        "N-alpha-valid": {"messages": [], "proof_credit": False}}
        expected = {case: {"source_id": "expected-source", "unit_id": "expected-unit"}
                    for case in observations}
        records = RUNNER._classify_native_target_rows(
            statuses, rows, observations, set(observations), expected, classifier,
            {"tool_id": "tool"}, "build-id", {})
        self.assertEqual(len(statuses), 26)
        self.assertEqual([case for case, _, _ in classifier.calls], list(observations))
        self.assertEqual(len(records), 2)
        self.assertEqual(len(rows), 26)
        self.assertEqual(statuses["P1"]["status"], "INTENDED_CLASSIFIED")
        skipped = next(row for row in rows if row["case_id"] == "R7")
        self.assertEqual(skipped["status"]["status"], "NOT_RUN")
        self.assertIn("bounded native-p1-target", skipped["status"]["reason"])
        self.assertFalse(any(row["status"]["proof_credit"] for row in rows))

    def test_missing_null_wrong_type_and_classifier_error_fail_closed(self):
        target = {"P1", "N-alpha-valid"}
        cases = [
            ({}, {"P1": {"source_id": "s", "unit_id": "u"}}),
            ({"P1": None}, {"P1": {"source_id": "s", "unit_id": "u"}}),
            ({"P1": "bad-type"}, {"P1": "bad-type"}),
            ({"P1": {"not_run": True, "execution_started": False,
                     "reason": "deadline"}}, {"P1": {"source_id": "s", "unit_id": "u"}}),
        ]
        for observations, expected in cases:
            with self.subTest(observations=observations, expected=expected):
                statuses = {case: {} for case in RUNNER.CASE_ORDER}
                rows = []
                classifier = RecordingClassifier()
                RUNNER._classify_native_target_rows(
                    statuses, rows, observations, target, expected, classifier,
                    {"tool_id": "tool"}, "build-id", {})
                self.assertEqual(len(rows), 26)
                self.assertFalse(classifier.calls)
                self.assertIn(statuses["P1"]["status"], {"NOT_RUN", "INCONCLUSIVE"})
                self.assertFalse(statuses["P1"]["matrix_gate_passed"])
        statuses = {case: {} for case in RUNNER.CASE_ORDER}
        rows = []
        broken = RecordingClassifier(error=ValueError("classifier primary failure"))
        RUNNER._classify_native_target_rows(
            statuses, rows, {"P1": {"classification": "partial"}}, {"P1"},
            {"P1": {"source_id": "s", "unit_id": "u"}}, broken,
            {"tool_id": "tool"}, "build-id", {})
        self.assertEqual(statuses["P1"]["status"], "INCONCLUSIVE")
        self.assertIn("ValueError: classifier primary failure", statuses["P1"]["reason"])
        self.assertFalse(statuses["P1"]["matrix_gate_passed"])

        statuses = {case: {} for case in RUNNER.CASE_ORDER}
        rows = []
        RUNNER._classify_native_target_rows(
            statuses, rows, None, {"P1"}, None, RecordingClassifier(),
            ["wrong", "type"], "build-id", None)
        self.assertEqual(len(rows), 26)
        self.assertEqual(statuses["P1"]["status"], "NOT_RUN")

    def test_target_mode_is_r10_only_and_preserves_the_26_row_plan(self):
        base = {"phase_id": RUNNER.PHASE, "profile_accepted": False,
                "first_matrix_status": "NOT_RUN", "execution_mode": "native-p1-target",
                "authorization_phase_id": R10}
        plan = RUNNER.preflight_plan(base)
        self.assertEqual(plan["case_count"], 26)
        full = RUNNER.preflight_plan({**base, "execution_mode": "full-matrix"})
        self.assertEqual(full["case_count"], 26)
        self.assertEqual(full["planned_order"], list(RUNNER.CASE_ORDER))
        self.assertFalse(full["matrix_complete"])
        self.assertFalse(full["dispatch_ready"])
        self.assertFalse(full["proof_credit"])
        with self.assertRaisesRegex(RuntimeError, "R10/R11 authorization"):
            RUNNER.preflight_plan({**base, "authorization_phase_id": R9})


def _pointer_get(root, pointer):
    value = root
    for token in pointer.lstrip("/").split("/"):
        if not token:
            continue
        token = token.replace("~1", "/").replace("~0", "~")
        value = value[int(token)] if isinstance(value, list) else value[token]
    return value


class R10ReportSerializationTests(unittest.TestCase):
    def test_r10_exact_root_argument_roundtrip_all_rows_and_details(self):
        observation = {"partial": {"path": None}, "unicode": "α/β~γ",
                       "normal_unwind": {"observed": True}, "proof_credit": False}
        detail = {case: {**observation, "case_id": case} for case in RUNNER.CASE_ORDER}
        detail["P1-extra"] = {"status": "PARTIAL", "artifact": {}}
        original = {"authorization_phase_id": R10,
                    "observed_rows": [{"case_id": case,
                                       "observation": copy.deepcopy(detail[case])}
                                      for case in RUNNER.CASE_ORDER],
                    "observation_details": detail, "accepted": False,
                    "matrix_complete": False, "proof_credit": False}
        disk = RUNNER._report_value_for_disk(original, R10)
        disk = json.loads(json.dumps(disk, ensure_ascii=False))
        self.assertEqual(disk["report_serialization"]["lossless"], True)
        self.assertEqual(len(disk["observed_rows"]), 26)
        for row in disk["observed_rows"]:
            pointer = row["observation_ref"]["json_pointer"]
            self.assertEqual(_pointer_get(disk, pointer), detail[row["case_id"]])
        self.assertEqual(disk["observation_details"]["P1-extra"], detail["P1-extra"])
        self.assertFalse(disk["accepted"] or disk["matrix_complete"] or disk["proof_credit"])
        self.assertIs(RUNNER._report_value_for_disk(original, R9), original)

    def test_r9_keeps_its_exact_compaction_and_older_phase_is_noop(self):
        observation = {"status": "PARTIAL", "payload": "z" * 1024}
        report = {"authorization_phase_id": R9,
                  "observed_rows": [{"case_id": "P1",
                                     "observation": copy.deepcopy(observation)}],
                  "observation_details": {"P1": observation}}
        r9_disk = RUNNER._report_value_for_disk(report, R9)
        self.assertIn("observation_ref", r9_disk["observed_rows"][0])
        self.assertIs(RUNNER._report_value_for_disk(report, R10), report)
        old = {**report, "authorization_phase_id": "SORT4-POST-MIGRATION-NATIVE-PROOF-2026-10-20-R8"}
        self.assertIs(RUNNER._report_value_for_disk(old, old["authorization_phase_id"]), old)

    def test_null_missing_wrongtype_and_conflicting_values_stay_inline(self):
        rows = [
            {"case_id": "missing", "observation": {"status": "partial"}},
            {"case_id": "null", "observation": None},
            {"case_id": "wrong", "observation": "bad"},
            {"case_id": "valid", "observation": {"status": "same"}},
        ]
        report = {"authorization_phase_id": R10, "observed_rows": rows,
                  "observation_details": {"null": None,
                                          "wrong": {"status": "detail"},
                                          "valid": {"status": "same"}}}
        disk = RUNNER._report_value_for_disk(report, R10)
        self.assertEqual(disk["observed_rows"][:3], rows[:3])
        self.assertEqual(disk["observed_rows"][3]["observation_ref"]["json_pointer"],
                         "/observation_details/valid")
        conflict = {**report, "observed_rows": rows + [
            {"case_id": "conflict", "observation": {"status": "row"}}],
            "observation_details": {**report["observation_details"],
                                    "conflict": {"status": "detail"}}}
        self.assertIs(RUNNER._report_value_for_disk(conflict, R10), conflict)
        self.assertIs(RUNNER._report_value_for_disk(report, "wrong-phase"), report)
        malformed = {**report, "authorization_phase_id": "wrong-phase"}
        self.assertIs(RUNNER._report_value_for_disk(malformed, R10), malformed)


if __name__ == "__main__":
    unittest.main()
