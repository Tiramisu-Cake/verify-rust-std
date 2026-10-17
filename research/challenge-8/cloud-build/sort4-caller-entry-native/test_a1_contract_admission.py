"""Synthetic unit tests for the pure A1 admission state machine."""

import importlib.util
from pathlib import Path
import sys
import unittest


MODULE_PATH = Path(__file__).with_name("a1-contract-admission.py")
SPEC = importlib.util.spec_from_file_location("a1_contract_admission", MODULE_PATH)
admission = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = admission
assert SPEC.loader is not None
SPEC.loader.exec_module(admission)


RUN_PINS = {
    "tool_id": "tool:sha256-222",
    "profile_id": "profile:sha256-333",
    "proof_id": "proof:sha256-444",
    "infra_id": "infra:sha256-555",
    "target_id": "target:a1-first-matrix",
}
BUILD = "build:test-build-id"
IMPL_INPUTS = {
    "default16": {"source_id": "source:baseline-pair", "unit_id": "unit:default-threshold"},
    "freeze32": {"source_id": "source:baseline-pair", "unit_id": "unit:freeze-threshold"},
}
CASE_INPUTS = {
    case_id: {
        "source_id": (f"source:synthetic-{case_id}" if case_id.startswith("N-") else "source:baseline-pair"),
        "unit_id": f"unit:{case_id}",
    }
    for case_id in admission.MATRIX
}
CASE_INPUTS["P0a"] = dict(IMPL_INPUTS["default16"])
CASE_INPUTS["P0b"] = dict(IMPL_INPUTS["freeze32"])
INVENTORY = {
    "default16": {"compiler_impl_id": "impl-defid-default", "compiler_item_id": "item-defid-default-threshold"},
    "freeze32": {"compiler_impl_id": "impl-defid-freeze", "compiler_item_id": "item-defid-freeze-threshold"},
}


def inventory_rows():
    return [{"impl": name, **ident} for name, ident in INVENTORY.items()]


def implementation(impl):
    return {
        **RUN_PINS,
        **IMPL_INPUTS[impl],
        "build_id": BUILD,
        "record_kind": "runner_attestation",
        "skipped": False,
        "focus_only": True,
        "focus_mode": "actual-body-and-conformance",
        "focused_item_id": INVENTORY[impl]["compiler_item_id"],
        "body_count": 1,
        "focus_body_verified": True,
        "focus_conformance_verified": True,
        "proof_kind": "actual_body",
        "impl": impl,
        "inventory": inventory_rows(),
        "compiler_identity": {"impl": impl, **INVENTORY[impl]},
        "body": {
            "stage": "impl-body", "predicate": "16<=result<=32",
            "location": f"{impl} threshold item", "outcome": "pass",
            "classification": "proved-by-runner",
        },
        "native_envelope": {
            "stage": "native-envelope-conformance", "predicate": "16<=result<=32",
            "location": f"{impl} threshold item", "outcome": "pass",
            "classification": "proved-by-runner",
        },
    }


def matrix_records():
    records = []
    for case_id, (stage, predicate, location, outcome, classification) in admission.MATRIX.items():
        row = {
            **RUN_PINS, **CASE_INPUTS[case_id],
            "build_id": BUILD, "record_kind": "runner_attestation",
            "skipped": False, "focus_only": False, "focus_mode": "none",
            "case_id": case_id, "stage": stage, "predicate": predicate,
            "location": location, "outcome": outcome, "classification": classification,
        }
        if case_id in admission.THRESHOLD_BODY_CASES:
            impl = admission._focus_impl_for_case(case_id)
            negative = case_id.startswith("N-")
            gate_location = ("mutated default threshold body" if impl == "default16" else
                             "mutated Freeze threshold body") if negative else f"{impl} threshold item"
            body_gate = ({
                "stage": "impl-body-post", "predicate": "result<=32", "location": gate_location,
                "outcome": "fail", "classification": "runner-reported-intended-negative",
                "target_reached": True, "failure_observed": True, "verified": False,
            } if negative else {
                "stage": "impl-body", "predicate": "16<=result<=32", "location": gate_location,
                "outcome": "pass", "classification": "runner-reported-body-pass",
            })
            envelope_gate = ({
                "stage": "native-envelope-conformance", "predicate": "normal+unwind-posts-preserved",
                "location": gate_location, "outcome": "pass",
                "classification": "runner-reported-conformance-preserved",
                "normal_posts_preserved": True, "unwind_posts_preserved": True,
            } if negative else {
                "stage": "native-envelope-conformance", "predicate": "16<=result<=32", "location": gate_location,
                "outcome": "pass", "classification": "runner-reported-conformance-pass",
            })
            row.update({
                "focus_only": True, "focus_mode": "actual-body-and-conformance",
                "focused_item_id": INVENTORY[impl]["compiler_item_id"], "body_count": 1,
                "proof_kind": "actual_body", "focus_body_reached": True,
                "focus_body_verified": not negative, "focus_conformance_verified": True,
                "compiler_identity": {"impl": impl, **INVENTORY[impl]},
                "body": body_gate, "native_envelope": envelope_gate,
            })
        elif case_id in admission.CALLER_BODY_CASES:
            row.update({"focus_only": True, "focus_mode": "caller-body",
                        "focus_target": admission.CALLER_FOCUS_TARGET,
                        "body_count": 1, "caller_body_reached": True,
                        "caller_body_verified": case_id == "P0c"})
            if case_id == "P0c":
                row["assertions_reached"] = ["len<=32", "requirement<=48"]
            else:
                row["reached_predicate"] = "len<=31"
                row["assertion_failure_observed"] = True
        elif case_id in admission.INTERFACE_ONLY_CASES:
            row.update({"focus_only": True, "focus_mode": "interface-only",
                        "focus_target": admission.INTERFACE_FOCUS_TARGET,
                        "body_count": 0, "interface_verified": True,
                        "case_credit": classification, "proof_credit": False})
        records.append(row)
    return records


def expected_cases():
    return {
        case_id: {
            **CASE_INPUTS[case_id],
            "stage": stage, "predicate": predicate, "location": location,
            "outcome": outcome, "classification": classification,
            **({"focused_item_id": INVENTORY[admission._focus_impl_for_case(case_id)]["compiler_item_id"]}
               if case_id in admission.THRESHOLD_BODY_CASES else {}),
        }
        for case_id, (stage, predicate, location, outcome, classification) in admission.MATRIX.items()
    }


class AdmissionTests(unittest.TestCase):
    def fresh(self):
        return admission.A1Admission(INVENTORY, RUN_PINS, IMPL_INPUTS,
                                    {case: {**admission_fields, **CASE_INPUTS[case]}
                                     for case, admission_fields in expected_cases().items()})

    def test_impl_proofs_and_positive_matrix_cannot_use_different_source_pairs(self):
        from copy import deepcopy
        changed = deepcopy(IMPL_INPUTS)
        changed["freeze32"]["source_id"] = "source:another-pair"
        with self.assertRaises(admission.AdmissionError):
            admission.A1Admission(INVENTORY, RUN_PINS, changed, expected_cases())
        cases = expected_cases()
        cases["P0a"]["unit_id"] = "unit:unrelated-body"
        with self.assertRaises(admission.AdmissionError):
            admission.A1Admission(INVENTORY, RUN_PINS, IMPL_INPUTS, cases)
        cases = expected_cases()
        cases["P0c"]["source_id"] = "source:supplied-bound-caller"
        with self.assertRaises(admission.AdmissionError):
            admission.A1Admission(INVENTORY, RUN_PINS, IMPL_INPUTS, cases)

    def test_one_actual_impl_never_unlocks_the_common_summary(self):
        service = self.fresh()
        service.record_implementation(implementation("default16"))
        self.assertFalse(service.common_summary_available)
        service.record_matrix(matrix_records())
        service.report_build(terminal_success=True, collector_success=True)
        self.assertFalse(service.first_matrix_accepted)

    def test_both_actual_impls_and_envelopes_are_required(self):
        service = self.fresh()
        service.record_implementation(implementation("default16"))
        bad = implementation("freeze32")
        bad["native_envelope"]["outcome"] = "skip"
        with self.assertRaisesRegex(admission.AdmissionError, "did not pass"):
            service.record_implementation(bad)
        self.assertFalse(service.common_summary_available)

    def test_successful_build_and_collector_do_not_release_summary(self):
        service = self.fresh()
        service.report_build(terminal_success=True, collector_success=True)
        self.assertFalse(service.common_summary_available)
        self.assertFalse(service.first_matrix_accepted)

    def test_pass_at_wrong_stage_or_location_is_inconclusive_and_rejected(self):
        service = self.fresh()
        rows = matrix_records()
        target = next(row for row in rows if row["case_id"] == "N-false31")
        target["stage"] = "frontend"
        with self.assertRaisesRegex(admission.AdmissionError, "stage mismatch"):
            service.record_matrix(rows)
        rows = matrix_records()
        target = next(row for row in rows if row["case_id"] == "N-false31")
        target["location"] = "some earlier error"
        with self.assertRaisesRegex(admission.AdmissionError, "location mismatch"):
            service.record_matrix(rows)

    def test_mutated_case_source_identity_is_bound_to_external_manifest(self):
        service = self.fresh()
        rows = matrix_records()
        n_default = next(row for row in rows if row["case_id"] == "N-default-contract")
        self.assertNotEqual(n_default["source_id"], CASE_INPUTS["P0a"]["source_id"])
        service.record_matrix(rows)
        self.assertEqual(service.matrix_records["N-default-contract"]["source_id"],
                         CASE_INPUTS["N-default-contract"]["source_id"])

        rows = matrix_records()
        next(row for row in rows if row["case_id"] == "N-default-contract")["source_id"] = "source:wrong-mutation"
        with self.assertRaisesRegex(admission.AdmissionError, "source identity mismatch"):
            self.fresh().record_matrix(rows)

    def test_inconclusive_not_run_and_wrong_negative_classification_fail(self):
        for classification in ("INCONCLUSIVE", "NOT_RUN", "POSITIVE_INTENDED"):
            rows = matrix_records()
            next(row for row in rows if row["case_id"] == "R4")["classification"] = classification
            with self.subTest(classification=classification):
                with self.assertRaisesRegex(admission.AdmissionError, "classification mismatch"):
                    self.fresh().record_matrix(rows)

    def test_matrix_manifest_must_bind_all_cases(self):
        manifest = {case: {**data, **CASE_INPUTS[case]}
                    for case, data in expected_cases().items()}
        del manifest["R7"]
        with self.assertRaisesRegex(admission.AdmissionError, "exact complete case set"):
            admission.A1Admission(INVENTORY, RUN_PINS, IMPL_INPUTS, manifest)

    def test_duplicate_or_incomplete_compiler_inventory_fails_closed(self):
        service = self.fresh()
        rec = implementation("default16")
        rec["inventory"][1]["compiler_item_id"] = rec["inventory"][0]["compiler_item_id"]
        with self.assertRaises(admission.AdmissionError):
            service.record_implementation(rec)
        rec = implementation("default16")
        rec["inventory"] = rec["inventory"][:1]
        with self.assertRaises(admission.AdmissionError):
            service.record_implementation(rec)

    def test_duplicate_impl_record_fails(self):
        service = self.fresh()
        service.record_implementation(implementation("default16"))
        with self.assertRaisesRegex(admission.AdmissionError, "duplicate implementation"):
            service.record_implementation(implementation("default16"))

    def test_mismatched_proof_identity_fails(self):
        service = self.fresh()
        service.record_implementation(implementation("default16"))
        rec = implementation("freeze32")
        rec["proof_id"] = "proof:stale"
        with self.assertRaisesRegex(admission.AdmissionError, "run pins"):
            service.record_implementation(rec)

    def test_failed_record_does_not_bind_or_poison_service(self):
        service = self.fresh()
        bad = implementation("default16")
        bad["body"]["outcome"] = "INCONCLUSIVE"
        with self.assertRaises(admission.AdmissionError):
            service.record_implementation(bad)
        self.assertIsNone(service._run_pins)
        service.record_implementation(implementation("default16"))
        self.assertFalse(service.common_summary_available)

    def test_accepted_records_and_expected_pins_are_deep_immutable_copies(self):
        service = self.fresh()
        rec = implementation("default16")
        service.record_implementation(rec)
        rec["body"]["outcome"] = "fail"
        rec["inventory"][0]["compiler_item_id"] = "mutated-after-validation"
        self.assertEqual(service.implementations["default16"]["body"]["outcome"], "pass")
        self.assertEqual(service.implementations["default16"]["inventory"][0]["compiler_item_id"],
                         INVENTORY["default16"]["compiler_item_id"])
        with self.assertRaises(TypeError):
            service.implementations["default16"]["body"]["outcome"] = "fail"
        with self.assertRaises(TypeError):
            service.expected_inventory["default16"]["compiler_item_id"] = "changed"

        rows = matrix_records()
        service.record_matrix(rows)
        rows[0]["outcome"] = "NOT_RUN"
        self.assertNotEqual(service.matrix_records[rows[0]["case_id"]]["outcome"], "NOT_RUN")

    def test_fake_unproved_impl_and_fake_matrix_claim_fail(self):
        service = self.fresh()
        rec = implementation("default16")
        rec["body"]["classification"] = "unproved"
        with self.assertRaises(admission.AdmissionError):
            service.record_implementation(rec)
        rows = matrix_records()
        rows[0]["record_kind"] = "invented"
        with self.assertRaises(admission.AdmissionError):
            service.record_matrix(rows)
        rows = matrix_records()
        next(row for row in rows if row["case_id"] == "P0a")["proof_credit"] = True
        with self.assertRaisesRegex(admission.AdmissionError, "cannot claim independent proof"):
            self.fresh().record_matrix(rows)

    def test_skipped_or_frontend_only_focus_cannot_release_summary(self):
        rec = implementation("default16")
        rec["skipped"] = True
        with self.assertRaises(admission.AdmissionError):
            self.fresh().record_implementation(rec)

        rec = implementation("default16")
        rec["focus_only"] = True
        rec["focus_mode"] = "frontend-only"
        with self.assertRaises(admission.AdmissionError):
            self.fresh().record_implementation(rec)

    def test_verified_body_targeted_focus_is_allowed_for_each_impl(self):
        service = self.fresh()
        for impl in ("default16", "freeze32"):
            rec = implementation(impl)
            rec.update({
                "focus_only": True,
                "focus_mode": "actual-body-and-conformance",
                "focused_item_id": INVENTORY[impl]["compiler_item_id"],
                "focus_body_verified": True,
                "focus_conformance_verified": True,
            })
            service.record_implementation(rec)
        self.assertTrue(service.common_summary_available)

    def test_unfocused_implementation_body_is_rejected(self):
        rec = implementation("default16")
        rec.update({"focus_only": False, "focus_mode": "none"})
        with self.assertRaisesRegex(admission.AdmissionError, "focus mode mismatch"):
            self.fresh().record_implementation(rec)

    def test_threshold_matrix_focus_is_inventory_bound_and_checks_both_attestations(self):
        rows = matrix_records()
        positive = next(row for row in rows if row["case_id"] == "P0a")
        self.assertEqual(positive["focused_item_id"], INVENTORY["default16"]["compiler_item_id"])
        positive["focused_item_id"] = "caller-supplied-arbitrary-id"
        with self.assertRaisesRegex(admission.AdmissionError, "focus target"):
            self.fresh().record_matrix(rows)

        rows = matrix_records()
        negative = next(row for row in rows if row["case_id"] == "N-default-contract")
        negative["body"]["location"] = "earlier parser error"
        with self.assertRaisesRegex(admission.AdmissionError, "body failure was not observed"):
            self.fresh().record_matrix(rows)

        rows = matrix_records()
        positive = next(row for row in rows if row["case_id"] == "P0b")
        positive["focus_conformance_verified"] = False
        with self.assertRaisesRegex(admission.AdmissionError, "not both observed"):
            self.fresh().record_matrix(rows)

        rows = matrix_records()
        negative = next(row for row in rows if row["case_id"] == "N-freeze-contract")
        negative["focus_body_verified"] = True
        with self.assertRaisesRegex(admission.AdmissionError, "negative body must be reached"):
            self.fresh().record_matrix(rows)

        rows = matrix_records()
        negative = next(row for row in rows if row["case_id"] == "N-default-contract")
        negative["native_envelope"]["outcome"] = "fail"
        with self.assertRaisesRegex(admission.AdmissionError, "not independently preserved"):
            self.fresh().record_matrix(rows)

        rows = matrix_records()
        negative = next(row for row in rows if row["case_id"] == "N-default-contract")
        negative["body"]["stage"] = "frontend"
        negative["body"]["outcome"] = "INCONCLUSIVE"
        with self.assertRaisesRegex(admission.AdmissionError, "body failure was not observed"):
            self.fresh().record_matrix(rows)

    def test_caller_focus_requires_exact_observer_and_intended_assertions(self):
        rows = matrix_records()
        p0c = next(row for row in rows if row["case_id"] == "P0c")
        p0c["focus_target"] = "quicksort"
        with self.assertRaisesRegex(admission.AdmissionError, "exact source observer"):
            self.fresh().record_matrix(rows)

        rows = matrix_records()
        negative = next(row for row in rows if row["case_id"] == "N-false31")
        negative["assertion_failure_observed"] = False
        with self.assertRaisesRegex(admission.AdmissionError, "did not fail at its intended assertion"):
            self.fresh().record_matrix(rows)

    def test_interface_focus_is_zero_body_and_never_implementation_credit(self):
        rows = matrix_records()
        interface = next(row for row in rows if row["case_id"] == "P1")
        self.assertEqual(interface["focus_target"], admission.INTERFACE_FOCUS_TARGET)
        self.assertEqual(interface["body_count"], 0)
        interface["body_count"] = 1
        with self.assertRaisesRegex(admission.AdmissionError, "executed a body"):
            self.fresh().record_matrix(rows)

        rows = matrix_records()
        interface = next(row for row in rows if row["case_id"] == "N-alpha-valid")
        interface["proof_credit"] = True
        with self.assertRaisesRegex(admission.AdmissionError, "cannot claim independent proof credit"):
            self.fresh().record_matrix(rows)

    def test_manifest_focus_id_cannot_be_arbitrary(self):
        cases = expected_cases()
        cases["P0a"]["focused_item_id"] = "invented-item-id"
        with self.assertRaisesRegex(admission.AdmissionError, "bind to expected compiler inventory"):
            admission.A1Admission(INVENTORY, RUN_PINS, IMPL_INPUTS, cases)

    def test_exact_full_matrix_needed_for_final_gate_and_stays_source_reported(self):
        service = self.fresh()
        service.record_implementation(implementation("default16"))
        service.record_implementation(implementation("freeze32"))
        self.assertTrue(service.common_summary_available)
        service.report_build(terminal_success=True, collector_success=True)
        with self.assertRaises(admission.AdmissionError):
            service.record_matrix(matrix_records()[:-1])
        self.assertFalse(service.first_matrix_accepted)
        service.record_matrix(matrix_records())
        self.assertTrue(service.first_matrix_accepted)
        self.assertEqual(service.state(), "source-reported-first-matrix-gates-satisfied")
        self.assertNotIn("proof", service.state())

    def test_mixed_build_ids_fail(self):
        service = self.fresh()
        service.record_implementation(implementation("default16"))
        rec = implementation("freeze32")
        rec["build_id"] = "build:another"
        with self.assertRaises(admission.AdmissionError):
            service.record_implementation(rec)


if __name__ == "__main__":
    unittest.main()
