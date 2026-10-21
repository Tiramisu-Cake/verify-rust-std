#!/usr/bin/env python3
"""Synthetic R14 authorization and publication-gate tests; no Cloud calls."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
CONTROL = HERE.parent / "control.py"
spec = importlib.util.spec_from_file_location("r14_control", CONTROL)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def gate():
    return {
        "schema": "merge-r14-publication-gate-v1",
        "status": "ACCEPTED",
        **m.R14_GATE_IDENTITIES,
        "archive_size_bytes": None,
        "exact_archive_size_observed": False,
        "sidecar_verified": False,
        "archive_limit_bytes": 536870912,
        "threshold_bytes": 157286400,
        "parallel_composite_upload_enabled": False,
        "proof_attempted": False,
        "verification_accepted": False,
        "archive_inventory_verified": True,
        "publication_verified": True,
        "independent_proof_credit": 0,
        "cloud_steps_success": {"execute": True, "package-upload": True, "verdict": True},
        "mandatory_guard_path_verified": True,
        "brief_request_id": m.R14_BRIEF_REQUEST_ID,
        "size_bounds_basis": "EXACT_PINNED_FAIL_CLOSED_PATH_AND_SUCCESSFUL_CLOUD_STEPS",
        "coverage": {
            "observed_utc": "2026-10-21T12:56:33.017365Z",
            "fresh_brief": "VERIFIED_ARCHIVE_AND_INVENTORY",
            "catalogue_complete": True,
            "catalogue_members": 15,
            "policy_file_id": m.R14_POLICY_FILE_ID,
            "policy_file_sha256": m.R14_POLICY_FILE_SHA256,
            "policy_selector": "pointer root",
            "policy_exact": True,
            "policy_complete": True,
            "policy_next_offset": None,
            "effective_enabled": "False",
            "effective_threshold": "150M",
            "policy_source_and_build_match": True,
            "archived_submitted_config_sha256_matches": True,
            "submitted_config_file_id": "8a44769e28c1a68c618ab62b28eb20f29e1e29f8c2d06a136824a973717e1c9a",
            "submitted_config_catalogue_verification": "SHA256_VERIFIED_ARCHIVE_MEMBER",
            "actual_dispatch_config_audit": "R14-CONFIG-AUDIT-20261021.json",
            "upload_shell_sha256": m.R14_UPLOAD_SHELL_SHA256,
            "bounded_archive_statement": "157286400 < actual compressed archive bytes <= 536870912; bounds from mandatory pinned guard execution and successful publication, not direct size receipt observation",
            "sidecar_limitation": "Post-package receipts outside archive catalogue; exact size and upload-only timing unavailable via Reader. No raw audit requested or used.",
            "historical_R13_records_modified": False,
            "old_probe_charged_to_R14": False,
        },
    }


def ledger():
    return {
        "phase": m.R14_PHASE,
        "owner": "merge",
        "authorization_model": "bounded-cloud-budget",
        "status": "AUTHORIZED",
        "allowed_lanes": ["merge"],
        "ceiling_build_seconds": 3600,
        "used_build_seconds": 0,
        "remaining_build_seconds": 3600,
        "max_builds": None,
        "max_timeout_seconds": 1200,
        "builds": [],
        "active_build": None,
        "start_utc": "2026-10-21T12:52:50Z",
        "main_deadline_utc": "2026-10-21T14:52:50Z",
        "deadline_utc": "2026-10-21T15:22:50Z",
        "carryover_allowed": False,
        "publication_gate_path": m.R14_GATE_PATH,
        "authorization": "R14 explicitly authorized by CURRENT-TASK",
    }


def args(command="submit"):
    values = dict(phase_id=m.R14_PHASE, owner="merge", ledger=HERE / m.R14_LEDGER_PATH.rsplit("/", 1)[-1], command=command)
    if command == "submit":
        values.update(infra_sha="a" * 40, proof_sha="a" * 40, lane="merge", timeout=1200, source_mode="pinned-objects")
    return type("Args", (), values)()


class R14GateTests(unittest.TestCase):
    def test_exact_unknown_size_gate_accepts_without_claiming_receipt_or_proof(self):
        value = gate()
        m.r14_validate_gate_record(value)
        self.assertIsNone(value["archive_size_bytes"])
        self.assertIs(value["sidecar_verified"], False)
        self.assertEqual(value["independent_proof_credit"], 0)

    def test_missing_wrong_and_wrongly_typed_gate_fields_fail_closed(self):
        for field, bad in (
            ("build_id", None), ("proof_source_sha", "d" * 40),
            ("submitted_config_sha256", "e" * 64), ("archive_sha256", "f" * 64),
            ("index_sha256", "e" * 64), ("archive_size_bytes", 1),
            ("archive_limit_bytes", 536870913), ("threshold_bytes", 1),
            ("parallel_composite_upload_enabled", True), ("proof_attempted", True),
            ("verification_accepted", True), ("archive_inventory_verified", False),
            ("mandatory_guard_path_verified", False), ("publication_verified", False),
            ("sidecar_verified", True), ("exact_archive_size_observed", True),
            ("independent_proof_credit", False), ("brief_request_id", "different-but-nonempty-request"),
        ):
            bad_gate = gate(); bad_gate[field] = bad
            with self.subTest(field=field, bad=bad), self.assertRaises(SystemExit):
                m.r14_validate_gate_record(bad_gate)
        for field in ("archive_size_bytes", "archive_sha256", "index_sha256", "proof_source_sha", "cloud_steps_success"):
            bad_gate = gate(); bad_gate.pop(field)
            with self.subTest(missing=field), self.assertRaises(SystemExit):
                m.r14_validate_gate_record(bad_gate)

    def test_config_catalogue_identity_is_required_and_exact(self):
        for field, value in (
            ("submitted_config_file_id", "wrong-file"),
            ("submitted_config_catalogue_verification", "NOT_VERIFIED"),
        ):
            bad = gate(); bad["coverage"][field] = value
            with self.subTest(field=field), self.assertRaises(SystemExit):
                m.r14_validate_gate_record(bad)
        for field in ("submitted_config_file_id", "submitted_config_catalogue_verification"):
            bad = gate(); bad["coverage"].pop(field)
            with self.subTest(missing=field), self.assertRaises(SystemExit):
                m.r14_validate_gate_record(bad)

    def test_step_matrix_and_policy_false_are_required(self):
        bad = gate(); bad["cloud_steps_success"]["package-upload"] = False
        with self.assertRaises(SystemExit): m.r14_validate_gate_record(bad)
        bad = gate(); bad["cloud_steps_success"]["extra"] = True
        with self.assertRaises(SystemExit): m.r14_validate_gate_record(bad)
        bad = gate(); bad["parallel_composite_upload_enabled"] = True
        with self.assertRaises(SystemExit): m.r14_validate_gate_record(bad)
        for field, value in (("effective_enabled", "True"), ("effective_threshold", "1"),
                             ("policy_file_sha256", "0"*64), ("policy_complete", False),
                             ("policy_source_and_build_match", False), ("catalogue_complete", False),
                             ("catalogue_members", True), ("observed_utc", "not-a-time")):
            bad = gate(); bad["coverage"][field] = value
            with self.subTest(coverage=field), self.assertRaises(SystemExit):
                m.r14_validate_gate_record(bad)
        bad = gate(); bad["coverage"]["observed_utc"] = "2099-10-21T12:56:33Z"
        with self.assertRaises(SystemExit): m.r14_validate_gate_record(bad)


class R14PhaseTests(unittest.TestCase):
    def setUp(self):
        real = m.datetime.datetime
        class Frozen(real):
            @classmethod
            def now(cls, tz=None): return real.fromisoformat("2026-10-21T13:00:00+00:00")
        self.clock = patch.object(m.datetime, "datetime", Frozen)
        self.clock.start()
        self.addCleanup(self.clock.stop)

    def authorize(self, account=None, command="submit"):
        account = ledger() if account is None else account
        with patch.object(m, "r13_upload_mode", return_value="proof-r11"), \
             patch.object(m, "r14_read_selected_gate", return_value=gate()), \
             patch.object(m, "r14_validate_retry_sources") as sources:
            m.authorized_phase(args(command), account)
            if command == "submit": sources.assert_called_once_with(m.R14_PROBE_SOURCE, "a" * 40)

    def test_valid_phase_submit_and_request(self):
        self.authorize()
        self.authorize(command="request")

    def test_r14_submit_selects_the_required_upload_marker_in_generated_config(self):
        selected = m.required_upload_guard(m.R14_PHASE)
        self.assertIs(selected, True)
        self.assertIs(m.required_upload_guard("MERGE-ARCHIVE-SIZE-UPLOAD-R13-2026-10-21"), True)
        self.assertIs(m.required_upload_guard("MERGE-LABEL-STORAGE-INVARIANT-R11-2026-10-21"), False)
        config = m.config("a" * 40, "a" * 40, "merge", 1200, "synthetic-test-token",
                          source_payload=None, r13_required=selected)
        self.assertIn("R13_UPLOAD_REQUIRED=true", config["steps"][1]["env"])

    def test_missing_or_mismatched_ledger_authority_refused(self):
        for key, value in (
            ("owner", "other"), ("authorization_model", "time-window"),
            ("ceiling_build_seconds", 3601), ("allowed_lanes", ["other"]),
            ("start_utc", None), ("main_deadline_utc", "2026-10-21T14:52:51Z"),
            ("deadline_utc", "2026-10-21T15:22:51Z"), ("max_timeout_seconds", 1201),
            ("carryover_allowed", True), ("publication_gate_path", "elsewhere.json"),
            ("max_builds", 1), ("remaining_build_seconds", 3599), ("active_build", False),
        ):
            bad = ledger(); bad[key] = value
            with self.subTest(field=key), self.assertRaises(SystemExit):
                self.authorize(bad)
        for key in ("publication_gate_path", "builds", "remaining_build_seconds", "used_build_seconds", "active_build"):
            bad = ledger(); bad.pop(key)
            with self.subTest(missing=key), self.assertRaises(SystemExit):
                self.authorize(bad)

    def test_prior_probe_is_not_charged_to_new_account(self):
        account = ledger()
        self.assertEqual(account["builds"], [])
        self.assertEqual(account["used_build_seconds"], 0)
        self.authorize(account)
        for record in (
            {"build_id": m.R14_GATE_IDENTITIES["build_id"], "owner": "merge", "phase_id": m.R14_PHASE},
            {"build_id": "another", "owner": "merge", "phase_id": "MERGE-ARCHIVE-SIZE-UPLOAD-R13-2026-10-21"},
        ):
            bad = ledger(); bad["builds"] = [record]
            with self.subTest(record=record), self.assertRaises(SystemExit): self.authorize(bad)

    def test_wrong_mode_identity_and_deadline_fail(self):
        with patch.object(m, "r13_upload_mode", return_value="synthetic-upload"), self.assertRaises(SystemExit):
            m.authorized_phase(args(), ledger())
        bad = args(); bad.infra_sha = "b" * 40
        with patch.object(m, "r13_upload_mode", return_value="proof-r11"), self.assertRaises(SystemExit):
            m.authorized_phase(bad, ledger())
        real = m.datetime.datetime
        class Late(real):
            @classmethod
            def now(cls, tz=None): return real.fromisoformat("2026-10-21T14:53:00+00:00")
        with patch.object(m.datetime, "datetime", Late), self.assertRaises(SystemExit):
            m.authorized_phase(args(), ledger())

    def test_actual_gate_and_source_calls_are_mandatory_for_submit(self):
        with patch.object(m, "r13_upload_mode", return_value="proof-r11"), \
             patch.object(m, "r14_read_selected_gate", side_effect=SystemExit("missing gate")), \
             self.assertRaises(SystemExit):
            m.authorized_phase(args(), ledger())
        with patch.object(m, "r13_upload_mode", return_value="proof-r11"), \
             patch.object(m, "r14_read_selected_gate", return_value=gate()), \
             patch.object(m, "r14_validate_retry_sources", side_effect=SystemExit("changed closure")), \
             self.assertRaises(SystemExit):
            m.authorized_phase(args(), ledger())


if __name__ == "__main__":
    unittest.main()
