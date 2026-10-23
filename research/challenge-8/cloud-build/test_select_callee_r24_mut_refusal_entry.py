"""Synthetic checks for the closed R24 refusal-control entry."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "select_callee_r24_mut_refusal_entry_test",
    HERE / "select-callee-r24-mut-refusal-entry.py")
assert SPEC is not None and SPEC.loader is not None
ENTRY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ENTRY)

BUILD_ID = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
SOURCE = {
    "classification": "SOURCE_ONLY_MUTABLE_NINE_BODY_A1_FRACTIONAL_CAPTURE",
    "original_sha256": ENTRY.POSITIVE_ORIGINAL_SHA256,
    "verified_sha256": ENTRY.POSITIVE_VERIFIED_SHA256,
    "specialization": "T = *mut Element; Element unrestricted",
    "source_order": ["select_unpredictable"],
    "ghost_strip_identity": True,
    "typed_mir_binding_established": False,
    "helper_proof_status": "NOT_RUN",
    "publication_status": "NOT_PUBLISHED",
    "proof_credit": 0,
}
PROVIDER = {
    "provider": "cloud-build", "build_id": BUILD_ID, "project": "smallsort-ci",
    "region": "global", "os": "ubuntu-22.04", "arch": "x86_64",
}


class _Collector:
    POSITIVE_ORIGINAL_SHA256 = ENTRY.POSITIVE_ORIGINAL_SHA256
    POSITIVE_VERIFIED_SHA256 = ENTRY.POSITIVE_VERIFIED_SHA256
    @staticmethod
    def _validate_provider_record(record, build):
        ENTRY._need(isinstance(record, dict) and
                    record == {**PROVIDER, "build_id": build},
                    "synthetic provider mismatch")
        return record


class RefusalEntryTests(unittest.TestCase):
    def test_mode_file_is_raw_pinned_and_exact(self):
        repo = HERE.parents[2]
        mode_path = repo / ENTRY.MODE_REL
        self.assertEqual(ENTRY.validate_mode(repo, mode_path), ENTRY._expected_mode())
        self.assertEqual(hashlib.sha256(mode_path.read_bytes()).hexdigest(),
                         ENTRY.MODE_SHA256)
        with patch.object(ENTRY, "MODE_SHA256", "0" * 64):
            with self.assertRaises(ENTRY.EntryError):
                ENTRY.validate_mode(repo, mode_path)

    def test_capture_summary_accepts_only_complete_same_build_source_only_record(self):
        with tempfile.TemporaryDirectory() as temp:
            evidence = Path(temp)
            path = evidence / ENTRY.CAPTURE_SUMMARY_REL
            path.parent.mkdir(parents=True)
            summary = {
                "schema": "select-r24-mut-capture-summary-v1",
                "complete": True, "classification": "MUTABLE_SOURCE_MIR_CAPTURE_ONLY",
                "native_build_id": BUILD_ID,
                "provider_record": PROVIDER,
                "body_proof_run": False, "typed_admission": False,
                "semantic_rule_enabled": False, "accepted": False,
                "publication_allowed": False, "proof_credit": 0,
                "source_records": {
                    "contract_text_sha256": ENTRY.CONTRACT_SHA256,
                    "final_nine_body": SOURCE,
                },
            }
            path.write_text(json.dumps(summary), encoding="utf-8")
            self.assertEqual(ENTRY._read_capture_summary(
                evidence, BUILD_ID, _Collector)[1], SOURCE)

            refusals = (
                None,
                {**summary, "complete": False},
                {**summary, "typed_admission": True},
                {**summary, "provider_record": {**PROVIDER, "build_id": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"}},
                {**summary, "source_records": {**summary["source_records"],
                    "final_nine_body": {**SOURCE, "verified_sha256": "0" * 64}}},
                {**summary, "source_records": {**summary["source_records"],
                    "final_nine_body": {**SOURCE, "helper_proof_status": "RAN"}}},
            )
            for changed in refusals:
                with self.subTest(changed=changed):
                    if changed is None:
                        path.write_text("null", encoding="utf-8")
                    else:
                        path.write_text(json.dumps(changed), encoding="utf-8")
                    with self.assertRaises(ENTRY.EntryError):
                        ENTRY._read_capture_summary(evidence, BUILD_ID, _Collector)

    def test_provider_reload_uses_frozen_capture_provider_api_and_matches_capture(self):
        services = ENTRY.load_services(HERE)
        self.assertTrue(callable(getattr(services["old"], "load_provider", None)))
        actual_provider_module = services["old"].load_provider(HERE)
        self.assertTrue(callable(getattr(actual_provider_module,
                                         "require_supported_provider", None)))

        class Provider:
            @staticmethod
            def require_supported_provider():
                return PROVIDER
        class Old:
            @staticmethod
            def load_provider(_cloud_dir):
                return Provider
        self.assertEqual(ENTRY._load_current_provider(Old, HERE, BUILD_ID, _Collector),
                         PROVIDER)
        with self.assertRaises(ENTRY.EntryError):
            ENTRY._load_current_provider(Old, HERE,
                "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb", _Collector)

    def test_context_requires_exact_modes_current_candidate_and_nonempty_sysroot(self):
        repo = HERE.parents[2]
        env = {
            "PROOF_SHA": "1" * 40, "CLOUD_BUILD_ID": BUILD_ID,
            "SMALLSORT_EXECUTION_PROVIDER": "cloud-build",
            "SORT4_R24_SESSION_PHASE_ID": ENTRY.R24,
            "SORT4_R20_CALLEE_PHASE_ID": ENTRY.R21,
            "SORT4_SELECT_PROFILE": ENTRY.PROFILE,
            "LANE": ENTRY.LANE,
        }

        class Diag:
            @staticmethod
            def _validate_context(args, actual_env, lib):
                self.assertIs(lib, "lib")
                self.assertEqual(actual_env, env)
                return BUILD_ID

            @staticmethod
            def validate_mode(path_repo, path, lib):
                self.assertEqual(path_repo, repo)
                self.assertEqual(path, repo / ENTRY.MATRIX_MODE_REL)
                self.assertIs(lib, "lib")

        class Classified:
            @staticmethod
            def validate_classified_mode(path_repo, path, lib, targets):
                self.assertEqual(path_repo, repo)
                self.assertEqual(path, repo / ENTRY.CLASSIFIED_MODE_REL)
                self.assertIs(lib, "lib")
                self.assertIs(targets, "targets")

        services = {"diag": Diag, "lib": "lib", "classified": Classified,
                    "targets": "targets"}
        args = SimpleNamespace(
            repo=repo, cloud_dir=repo / "cloud", evidence=repo / "evidence",
            refusal_mode_file=repo / ENTRY.MODE_REL,
            matrix_proof_mode_file=repo / ENTRY.MATRIX_MODE_REL,
            classified_mode_file=repo / ENTRY.CLASSIFIED_MODE_REL,
            candidate="1" * 40, tool_home=Path("/tool"), schema=Path("/schema"),
            compiler_sysroot=Path("/sysroot"), deadline_epoch=123,
        )
        result = ENTRY._validate_context(args, env, services)
        self.assertEqual(result["build_id"], BUILD_ID)
        for changes in ({"compiler_sysroot": None}, {"compiler_sysroot": ""},
                        {"candidate": "2" * 40}, {"deadline_epoch": True}):
            changed = copy.copy(args)
            for key, value in changes.items():
                setattr(changed, key, value)
            with self.subTest(changes=changes):
                with self.assertRaises((ENTRY.EntryError, TypeError)):
                    ENTRY._validate_context(changed, env, services)

    def test_precondition_audits_preserve_sysroot_and_reject_incomplete_status(self):
        args = SimpleNamespace(compiler_sysroot=Path("/actual/sysroot"), candidate="1" * 40)

        class Classified:
            @staticmethod
            def audit(received, *, diag, targets, env):
                self.assertEqual(received.compiler_sysroot, Path("/actual/sysroot"))
                self.assertEqual(received.runner_exit, 0)
                self.assertEqual(received.failed_stage, "complete")
                self.assertTrue(received.output.parent.is_dir())
                return {"evidence_complete": True, "accepted": False,
                        "publication_allowed": False, "proof_credit": 0}

        class Consequence:
            @staticmethod
            def audit(received, *, diag):
                self.assertEqual(received.compiler_sysroot, "/actual/sysroot")
                return {"evidence_complete": True, "accepted": False,
                        "publication_allowed": False, "proof_credit": 0}

        services = {"classified": Classified, "entailment": Consequence,
                    "diag": object(), "targets": object()}
        with tempfile.TemporaryDirectory() as temp:
            result = ENTRY._precondition_audits(
                args, services, {}, 0, "complete", Path(temp), persist=True)
            self.assertTrue((Path(temp) / ENTRY.CLASSIFIED_AUDIT_REL).is_file())
            self.assertTrue((Path(temp) / ENTRY.CONSEQUENCE_AUDIT_REL).is_file())
        self.assertTrue(result["classified_audit"]["evidence_complete"])

        class Incomplete(Classified):
            @staticmethod
            def audit(*_args, **_kwargs):
                return {"evidence_complete": False, "accepted": False,
                        "publication_allowed": False, "proof_credit": 0}
        services["classified"] = Incomplete
        with self.assertRaises(ENTRY.EntryError):
            with tempfile.TemporaryDirectory() as temp:
                ENTRY._precondition_audits(
                    args, services, {}, 0, "complete", Path(temp), persist=False)

        class Exploding(Classified):
            @staticmethod
            def audit(*_args, **_kwargs):
                raise ValueError("original audit exception")
        services["classified"] = Exploding
        with tempfile.TemporaryDirectory() as temp:
            evidence = Path(temp)
            with self.assertRaisesRegex(ValueError, "original audit exception"):
                ENTRY._precondition_audits(
                    args, services, {}, 0, "complete", evidence, persist=True)
            exception_receipt = json.loads(
                (evidence / ENTRY.CLASSIFIED_AUDIT_REL).read_text(encoding="utf-8"))
            self.assertFalse(exception_receipt["complete"])
            self.assertEqual(exception_receipt["exception"]["message"],
                             "original audit exception")

    def test_real_entailment_audit_receives_string_sysroot_and_persists_failure(self):
        services = ENTRY.load_services(HERE)
        entailment = services["entailment"]
        args = SimpleNamespace(
            compiler_sysroot=Path("/actual/sysroot"),
            repo=HERE.parents[2], cloud_dir=HERE, evidence=Path("/absent/evidence"),
            tool_home=Path("/tool"), schema=Path("/schema"),
            matrix_proof_mode_file=HERE.parents[2] / ENTRY.MATRIX_MODE_REL,
            candidate="1" * 40,
        )
        class Classified:
            @staticmethod
            def audit(received, *, diag, targets, env):
                self.assertIsInstance(received.compiler_sysroot, Path)
                return {"evidence_complete": True, "accepted": False,
                        "publication_allowed": False, "proof_credit": 0}
        class Diagnostic:
            @staticmethod
            def load_library(_cloud): return object()
            @staticmethod
            def _validate_context(_args, _env, _lib): return BUILD_ID
            @staticmethod
            def validate_mode(_repo, _path, _lib): return {}
            @staticmethod
            def _regular_under(_root, _path): return False
            @staticmethod
            def write_json(path, value):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(value), encoding="utf-8")
        services["classified"] = Classified
        services["diag"] = Diagnostic
        services["targets"] = object()
        with tempfile.TemporaryDirectory() as temp:
            evidence = Path(temp)
            with self.assertRaisesRegex(ENTRY.EntryError, "P2 consequence audit is incomplete"):
                ENTRY._precondition_audits(
                    args, services, {}, 0, "complete", evidence, persist=True)
            receipt_path = evidence / ENTRY.CONSEQUENCE_AUDIT_REL
            self.assertTrue(receipt_path.is_file())
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            self.assertFalse(receipt["evidence_complete"])
            self.assertIn("P2-ENTAILMENT:", " ".join(receipt["errors"]))
            self.assertNotIn("compiler sysroot is required",
                             " ".join(receipt["errors"]))

    def test_entry_run_then_audit_composes_capture_and_collector_contracts(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo, cloud, evidence = root / "repo", root / "cloud", root / "evidence"
            repo.mkdir(); cloud.mkdir(); evidence.mkdir()
            source_view = evidence / ENTRY.SOURCE_VIEW_REL
            source_view.mkdir(parents=True)
            positive = evidence / ENTRY.POSITIVE_SOURCE_REL
            (positive / "original").mkdir(parents=True)
            (positive / "verified").mkdir()
            tool_home = root / "tool"
            tool_home.mkdir()
            tool_spec_path = tool_home / "bin/rust/std/lib.rsspec"
            tool_spec_path.parent.mkdir(parents=True)
            tool_spec_path.write_bytes(b"synthetic pinned spec")
            provider = {**PROVIDER, "build_id": BUILD_ID}
            capture_summary = {"provider_record": provider}

            class Old:
                TOOL_SPEC_RELATIVE = Path("bin/rust/std/lib.rsspec")
                _capture_errors = staticmethod(lambda *_a, **_k: [])
                _final_source_pair_errors = staticmethod(lambda *_a, **_k: [])
                @staticmethod
                def load_source_writers(path):
                    self.assertEqual(path, source_view)
                    return {"owner": object()}
                @staticmethod
                def load_capture_runtime(_repo, _cloud, _evidence):
                    return {"capture": SimpleNamespace(LINK=object())}

            class Collector:
                TOOL_SPEC_RELATIVE = Path("bin/rust/std/lib.rsspec")
                @staticmethod
                def make_frontend_capture_runner(capture, args, capture_errors):
                    self.assertIsNotNone(capture)
                    self.assertIs(args, run_args)
                    self.assertTrue(callable(capture_errors))
                    return object()
                @staticmethod
                def make_link_stage_runner(link, args):
                    self.assertIs(args, run_args)
                    return object()
                @staticmethod
                def collect_controls(**kwargs):
                    self.assertEqual(kwargs["positive_case"], positive)
                    self.assertEqual(kwargs["provider_record"], provider)
                    self.assertEqual(kwargs["source_record"], SOURCE)
                    return {"complete": True,
                            "classification": "COMPLETE_SOURCE_REPORTED_REFUSAL_COLLECTOR_NO_PROOF_CREDIT",
                            "accepted": False, "publication_allowed": False,
                            "proof_credit": 0, "controls": {key: {} for key in ENTRY.CONTROLS}}
                @staticmethod
                def audit_controls(**kwargs):
                    self.assertEqual(kwargs["provider_record"], provider)
                    self.assertEqual(kwargs["source_record"] if "source_record" in kwargs else SOURCE,
                                     SOURCE)
                    return {"complete": True,
                            "classification": "COMPLETE_SOURCE_REPORTED_REFUSALS_NO_PROOF_CREDIT",
                            "accepted": False, "publication_allowed": False,
                            "proof_credit": 0}

            services = {"old": Old, "collector": Collector}
            env = {"PROOF_SHA": "1" * 40, "CLOUD_BUILD_ID": BUILD_ID}
            run_args = SimpleNamespace(
                repo=repo, cloud_dir=cloud, evidence=evidence,
                tool_home=tool_home, schema=root / "schema.capnp",
                compiler_sysroot=root / "sysroot", deadline_epoch=123,
                candidate="1" * 40, refusal_mode_file=repo / ENTRY.MODE_REL,
                classified_mode_file=repo / ENTRY.CLASSIFIED_MODE_REL,
                matrix_proof_mode_file=repo / ENTRY.MATRIX_MODE_REL,
            )
            with patch.object(ENTRY, "_validate_context", return_value={
                    "mode": {}, "build_id": BUILD_ID, "repo": repo, "cloud_dir": cloud}), \
                 patch.object(ENTRY, "_precondition_audits", return_value={"ok": True}), \
                 patch.object(ENTRY, "_read_capture_summary", return_value=(capture_summary, SOURCE)), \
                 patch.object(ENTRY, "_load_current_provider", return_value=provider), \
                 patch.object(ENTRY, "_validate_positive_capture_artifacts"), \
                 patch.dict(os.environ, env, clear=False):
                run_result = ENTRY.run(run_args, env=env, services=services)
            self.assertTrue(run_result["complete"])
            self.assertFalse(run_result["accepted"])

            audit_args = copy.copy(run_args)
            audit_args.output = evidence / "entry-audit.json"
            audit_args.runner_exit = 0
            audit_args.failed_stage = "complete"
            with patch.object(ENTRY, "_validate_context", return_value={
                    "mode": {}, "build_id": BUILD_ID, "repo": repo, "cloud_dir": cloud}), \
                 patch.object(ENTRY, "_precondition_audits", return_value={"ok": True}), \
                 patch.object(ENTRY, "_read_capture_summary", return_value=(capture_summary, SOURCE)), \
                 patch.object(ENTRY, "_load_current_provider", return_value=provider), \
                 patch.object(ENTRY, "_validate_positive_capture_artifacts"), \
                 patch.dict(os.environ, env, clear=False):
                audit_result = ENTRY.audit(audit_args, env=env, services=services)
            self.assertTrue(audit_result["evidence_complete"], audit_result["errors"])
            self.assertFalse(audit_result["accepted"])
            self.assertTrue(audit_args.output.is_file())


if __name__ == "__main__":
    unittest.main()
