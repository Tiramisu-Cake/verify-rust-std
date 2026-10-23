"""Synthetic controls for the isolated R24 mutable refusal collector."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "select_callee_r24_mut_refusals_test",
    HERE / "select-callee-r24-mut-refusals.py")
assert SPEC is not None and SPEC.loader is not None
REFUSALS = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = REFUSALS
SPEC.loader.exec_module(REFUSALS)

BUILD_ID = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
TOOL_HOME = Path("/synthetic/tool")


def _fixture() -> bytes:
    return (
        b"pub unsafe fn sort4_checked_pointer_drop<Element>(slot: *mut *mut Element) {}\n"
        + REFUSALS.MUTABLE_SIGNATURE
        + b"/*@ synthetic contract; @*/\n"
        + b"{\n"
        + b"    let true_val = MaybeUninit::<*mut Element>::uninit();\n"
        + b"    let false_val = MaybeUninit::<*mut Element>::uninit();\n"
        + b"    unsafe { " + REFUSALS.RUNTIME_SENTINEL + b" }\n"
        + b"}\n"
    )


class _IdentityGhostStripper:
    @staticmethod
    def strip_ghost(raw: bytes) -> bytes:
        return raw


def _hashes(case: Path) -> dict[str, str]:
    return {
        "original/lib.rs": hashlib.sha256(
            (case / "original/lib.rs").read_bytes()).hexdigest(),
        "verified/lib.rs": hashlib.sha256(
            (case / "verified/lib.rs").read_bytes()).hexdigest(),
    }


class R24MutRefusalTests(unittest.TestCase):
    def _collection_fixture(self, root: Path):
        repo = root / "repo"
        repo.mkdir()
        evidence = root / "evidence"
        evidence.mkdir()
        positive = evidence / "cases/r24-mut-capture/source-preparation/nine-body/nine-body-mut"
        (positive / "original").mkdir(parents=True)
        (positive / "verified").mkdir()
        tool_home = root / "tool"
        (tool_home / "bin/rust/std").mkdir(parents=True)
        (tool_home / "bin/verifast").write_bytes(b"synthetic native binary")
        tool_spec = b"synthetic exact tool spec\n"
        (tool_home / "bin/rust/std/lib.rsspec").write_bytes(tool_spec)
        source = _fixture()
        (positive / "original/lib.rs").write_bytes(source)
        (positive / "verified/lib.rs").write_bytes(source)
        digest = hashlib.sha256(source).hexdigest()
        source_record = {
            "classification": "SOURCE_ONLY_MUTABLE_NINE_BODY_A1_FRACTIONAL_CAPTURE",
            "original_sha256": digest, "verified_sha256": digest,
            "specialization": "T = *mut Element; Element unrestricted",
            "source_order": ["select_unpredictable"],
            "ghost_strip_identity": True, "typed_mir_binding_established": False,
            "helper_proof_status": "NOT_RUN", "publication_status": "NOT_PUBLISHED",
            "proof_credit": 0,
        }
        env = {
            "CLOUD_BUILD_ID": BUILD_ID,
            "CLOUD_BUILD_PROJECT_ID": "smallsort-ci",
            "CLOUD_BUILD_REGION": "global",
            "SMALLSORT_EXECUTION_PROVIDER": "cloud-build",
            REFUSALS.R24_PHASE_ENV: REFUSALS.R24_PHASE,
            REFUSALS.R21_PHASE_ENV: REFUSALS.R21_PHASE,
            REFUSALS.PROFILE_ENV: REFUSALS.PROFILE,
            "LANE": REFUSALS.LANE,
        }
        pins = {"schema": "select-r24-mut-positive-capture-pins-v1",
                "accepted": False, "proof_credit": 0, "publication_allowed": False,
                "source": {"original_sha256": digest, "verified_sha256": digest,
                           "contract_text_sha256": "dc985de2e2a0e1a95e6c12c4b9cb78c4042d9d45f949d78904a999e82262b870",
                           "specialization": "T = *mut Element; Element unrestricted"}}
        provider = {**REFUSALS.SUPPORTED_PROVIDER, "build_id": BUILD_ID}
        return repo, evidence, positive, tool_home, tool_spec, source_record, env, digest, pins, provider

    def test_all_seven_source_controls_are_unique_valid_byte_mutations(self):
        source = _fixture()
        for control in REFUSALS.SOURCE_CONTROLS:
            with self.subTest(control=control):
                changed = REFUSALS.mutate_verified_source(control, source)
                self.assertNotEqual(changed, source)
                self.assertEqual(source.count(REFUSALS.MUTABLE_SIGNATURE), 1)
                if control == "const-substitution":
                    self.assertIn(b"slot: *mut *const Element", changed)
                    self.assertNotIn(b"slot: *const *const Element", changed)
                elif control == "extra-pointer-depth":
                    self.assertIn(b"slot: *mut *mut *mut Element", changed)
                elif control == "swapped-selected-pointer-operand":
                    self.assertIn(b"select_unpredictable(condition, false_val, true_val)", changed)
                elif control == "swapped-final-branch-result":
                    self.assertIn(b"select_unpredictable(!condition, true_val, false_val)", changed)
                elif control == "changed-runtime-body":
                    self.assertIn(b"{ " + REFUSALS.RUNTIME_SENTINEL + b" }", changed)
                elif control == "renamed-generic-element":
                    self.assertIsNone(REFUSALS.ELEMENT_TOKEN.search(changed))
                    self.assertIn(b"R24MutatedElement", changed)
                elif control == "changed-cleanup-graph":
                    self.assertIn(b"let _r24_cleanup_box: Box<u8> = Box::new(0u8);", changed)

    def test_source_hash_controls_refuse_only_on_exact_native_gate_line(self):
        for control in REFUSALS.SOURCE_CONTROLS:
            with self.subTest(control=control):
                line = REFUSALS.REFUSAL_PREFIX + REFUSALS.SOURCE_HASH_REFUSAL + \
                    REFUSALS.REFUSAL_SUFFIX
                matched, gate, reason = REFUSALS._classify_log(control, line + "\n")
                self.assertTrue(matched)
                self.assertEqual(gate, REFUSALS.SOURCE_HASH_REFUSAL)
                self.assertEqual(reason, "exact source-envelope refusal observed")

    def test_context_controls_have_closed_expected_gate_messages(self):
        self.assertEqual(REFUSALS.EXPECTED_REFUSALS["wrong-phase"],
                         REFUSALS.ROUTE_REFUSAL)
        self.assertEqual(REFUSALS.EXPECTED_REFUSALS["partial-case-root"],
                         REFUSALS.PARTIAL_SELECTOR_REFUSAL)
        self.assertEqual(REFUSALS.EXPECTED_REFUSALS["unknown-case"],
                         REFUSALS.UNKNOWN_CASE_REFUSAL)
        self.assertEqual(REFUSALS.EXPECTED_REFUSALS["legacy-selector"],
                         REFUSALS.LEGACY_REFUSAL)

    def test_provider_record_requires_current_canonical_native_build(self):
        provider = {**REFUSALS.SUPPORTED_PROVIDER, "build_id": BUILD_ID}
        self.assertEqual(REFUSALS._validate_provider_record(provider, BUILD_ID), provider)
        for changed in (
                {**provider, "build_id": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"},
                {**provider, "project": "other-project"},
                {key: value for key, value in provider.items() if key != "arch"},
        ):
            with self.subTest(changed=changed):
                with self.assertRaises(REFUSALS.RefusalError):
                    REFUSALS._validate_provider_record(changed, BUILD_ID)

    def test_unexpected_diagnostic_success_marker_or_multiple_errors_are_unknown(self):
        control = "const-substitution"
        expected = REFUSALS.REFUSAL_PREFIX + REFUSALS.SOURCE_HASH_REFUSAL + \
            REFUSALS.REFUSAL_SUFFIX
        cases = (
            "Fatal error: exception Failure(\"compiler setup failed\")\n",
            expected + "\nerror: second diagnostic\n",
            expected.replace(REFUSALS.SOURCE_HASH_REFUSAL, "different gate") + "\n",
            expected + "\n" + REFUSALS.MARKER_PREFIX + " accepted\n",
            "error: cannot compile fixture\n",
        )
        for log in cases:
            with self.subTest(log=log):
                try:
                    matched, _, _ = REFUSALS._classify_log(control, log)
                except REFUSALS.RefusalError:
                    matched = False
                self.assertFalse(matched)
        with self.assertRaises(REFUSALS.RefusalError):
            REFUSALS._classify_log(control, expected + "\n" +
                                   REFUSALS.MARKER_PREFIX + " proof\n")

    def test_integrated_fake_stage_collects_without_acceptance_or_env_leaks(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            evidence = root / "evidence"
            evidence.mkdir()
            positive = evidence / "cases/r24-mut-capture/source-preparation/nine-body/nine-body-mut"
            (positive / "original").mkdir(parents=True)
            (positive / "verified").mkdir()
            tool_home = root / "tool"
            (tool_home / "bin/rust/std").mkdir(parents=True)
            (tool_home / "bin/verifast").write_bytes(b"synthetic native binary")
            tool_spec = b"synthetic exact tool spec\n"
            (tool_home / "bin/rust/std/lib.rsspec").write_bytes(tool_spec)
            source = _fixture()
            (positive / "original/lib.rs").write_bytes(source)
            (positive / "verified/lib.rs").write_bytes(source)
            original_hash = hashlib.sha256(source).hexdigest()
            verified_hash = original_hash
            REFUSALS.POSITIVE_ORIGINAL_SHA256 = original_hash
            REFUSALS.POSITIVE_VERIFIED_SHA256 = verified_hash
            REFUSALS._load_capture_pins = lambda _repo: {
                "accepted": False, "proof_credit": 0,
                "publication_allowed": False,
                "source": {"original_sha256": original_hash,
                           "verified_sha256": verified_hash},
            }
            env = {
                "CLOUD_BUILD_ID": BUILD_ID,
                "CLOUD_BUILD_PROJECT_ID": "smallsort-ci",
                "CLOUD_BUILD_REGION": "global",
                "SMALLSORT_EXECUTION_PROVIDER": "cloud-build",
                REFUSALS.R24_PHASE_ENV: REFUSALS.R24_PHASE,
                REFUSALS.R21_PHASE_ENV: REFUSALS.R21_PHASE,
                REFUSALS.PROFILE_ENV: REFUSALS.PROFILE,
                "LANE": REFUSALS.LANE,
            }
            prior = {key: os.environ.get(key) for key in (
                REFUSALS.CASE_ENV, REFUSALS.ROOT_ENV, REFUSALS.LEGACY_SELECTOR,
                REFUSALS.R24_PHASE_ENV)}

            def fake_stage_runner(*, case: Path, variant: str, name: str,
                                  build_id: str, child_environment_delta: dict):
                self.assertEqual(os.environ.get(REFUSALS.CASE_ENV),
                                 child_environment_delta.get(REFUSALS.CASE_ENV))
                expected = REFUSALS.EXPECTED_REFUSALS[variant]
                diagnostic = REFUSALS.REFUSAL_PREFIX + expected + REFUSALS.REFUSAL_SUFFIX
                log_name = name + ".log"
                (case / log_name).write_text(diagnostic + "\n", encoding="utf-8")
                return {
                    "name": name, "status": "RAN", "exit": 2,
                    "build_id": build_id,
                    "argv": [str(tool_home / "bin/verifast"), "-rustc_args",
                             "--edition 2021", "-verbose", "1", "verified/lib.rs"],
                    "stdout": log_name, "stderr": log_name,
                    "source_before": _hashes(case), "source_after": _hashes(case),
                    "source_unchanged": True,
                    "intrinsic_gate_active": False,
                    "pointer_drop_gate_active": False,
                }

            source_record = {
                "classification": "SOURCE_ONLY_MUTABLE_NINE_BODY_A1_FRACTIONAL_CAPTURE",
                "original_sha256": original_hash,
                "verified_sha256": verified_hash,
                "specialization": "T = *mut Element; Element unrestricted",
                "source_order": ["select_unpredictable"],
                "ghost_strip_identity": True,
                "typed_mir_binding_established": False,
                "helper_proof_status": "NOT_RUN",
                "publication_status": "NOT_PUBLISHED",
                "proof_credit": 0,
            }
            provider_record = {**REFUSALS.SUPPORTED_PROVIDER, "build_id": BUILD_ID}
            def fake_frontend_runner(*, case: Path, source_record: dict):
                return {"errors": [], "case": str(case),
                        "source_record": source_record,
                        "guard_capture": {"stages": {}},
                        "full_body_capture": {"normal": {}, "readonly": {}}}

            with patch.dict(os.environ, env, clear=False):
                summary = REFUSALS.collect_controls(
                    evidence=evidence, positive_case=positive, repo=repo,
                    owner=_IdentityGhostStripper, source_record=source_record,
                    frontend_runner=fake_frontend_runner, tool_home=tool_home,
                    tool_spec=tool_spec, build_id=BUILD_ID,
                    provider_record=provider_record,
                    stage_runner=fake_stage_runner, env=env)
                audit = REFUSALS.audit_controls(
                    evidence=evidence, positive_case=positive, repo=repo,
                    owner=_IdentityGhostStripper, capture=object(),
                    capture_errors=lambda *_args, **_kwargs: [],
                    tool_home=tool_home, tool_spec=tool_spec,
                    build_id=BUILD_ID, provider_record=provider_record, env=env)
            self.assertTrue(summary["complete"])
            self.assertTrue(audit["complete"], audit["errors"])
            self.assertEqual(set(summary["controls"]), set(REFUSALS.ALL_CONTROLS))
            self.assertEqual(summary["classification"],
                "COMPLETE_SOURCE_REPORTED_REFUSAL_COLLECTOR_NO_PROOF_CREDIT")
            self.assertIs(summary["accepted"], False)
            self.assertIs(summary["publication_allowed"], False)
            self.assertEqual(summary["proof_credit"], 0)
            for row in summary["controls"].values():
                self.assertEqual(row["classification"],
                    "NATIVE_SOURCE_ENVELOPE_REFUSAL_SOURCE_REPORTED")
                self.assertTrue(row["source_unchanged"])
                self.assertTrue(row["ghost_strip_identity"])
            for key, value in prior.items():
                self.assertEqual(os.environ.get(key), value)
            self.assertTrue((evidence / REFUSALS.SUMMARY_RELATIVE).is_file())
            summary_path = evidence / REFUSALS.SUMMARY_RELATIVE
            physical_summary = json.loads(summary_path.read_text(encoding="utf-8"))
            control = REFUSALS.ALL_CONTROLS[0]
            row = physical_summary["controls"][control]
            case = evidence / row["case_path"]
            alternate_verified = REFUSALS.mutate_verified_source(
                "extra-pointer-depth", (positive / "verified/lib.rs").read_bytes())
            (case / "original/lib.rs").write_bytes(alternate_verified)
            (case / "verified/lib.rs").write_bytes(alternate_verified)
            changed_pair = _hashes(case)
            row["source_before"] = changed_pair
            row["source_after"] = changed_pair
            row["frontend_capture"]["source_record"]["original_sha256"] = changed_pair["original/lib.rs"]
            row["frontend_capture"]["source_record"]["verified_sha256"] = changed_pair["verified/lib.rs"]
            for item in physical_summary["artifact_inventory"]:
                if item["path"] in {
                    row["case_path"] + "/original/lib.rs",
                    row["case_path"] + "/verified/lib.rs",
                }:
                    artifact = evidence / item["path"]
                    item["bytes"] = artifact.stat().st_size
                    item["sha256"] = hashlib.sha256(artifact.read_bytes()).hexdigest()
            summary_path.write_text(json.dumps(physical_summary), encoding="utf-8")
            with patch.dict(os.environ, env, clear=False):
                tampered_source_audit = REFUSALS.audit_controls(
                    evidence=evidence, positive_case=positive, repo=repo,
                    owner=_IdentityGhostStripper, capture=object(),
                    capture_errors=lambda *_args, **_kwargs: [],
                    tool_home=tool_home, tool_spec=tool_spec,
                    build_id=BUILD_ID, provider_record=provider_record, env=env)
            self.assertFalse(tampered_source_audit["complete"])
            first_log = evidence / summary["controls"][REFUSALS.ALL_CONTROLS[0]]["case_path"] / \
                summary["controls"][REFUSALS.ALL_CONTROLS[0]]["log"]["path"]
            first_log.write_bytes(first_log.read_bytes() + b"\nerror: tampered\n")
            with patch.dict(os.environ, env, clear=False):
                tampered_audit = REFUSALS.audit_controls(
                    evidence=evidence, positive_case=positive, repo=repo,
                    owner=_IdentityGhostStripper, capture=object(),
                    capture_errors=lambda *_args, **_kwargs: [],
                    tool_home=tool_home, tool_spec=tool_spec,
                    build_id=BUILD_ID, provider_record=provider_record, env=env)
            self.assertFalse(tampered_audit["complete"])

    def test_frontend_failure_blocks_native_stage_and_exception_keeps_partial_summary(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (repo, evidence, positive, tool_home, tool_spec, source_record,
             env, digest, pins, provider_record) = self._collection_fixture(root)
            frontend_calls = []
            def failed_frontend(*, case, source_record):
                frontend_calls.append(case)
                return {"errors": ["normal-decode did not complete"],
                        "source_record": source_record}
            def should_not_run(**_kwargs):
                self.fail("native refusal stage ran after frontend failure")
            with patch.object(REFUSALS, "POSITIVE_ORIGINAL_SHA256", digest), \
                 patch.object(REFUSALS, "POSITIVE_VERIFIED_SHA256", digest), \
                 patch.object(REFUSALS, "_load_capture_pins", return_value=pins), \
                 patch.dict(os.environ, env, clear=False):
                summary = REFUSALS.collect_controls(
                    evidence=evidence, positive_case=positive, repo=repo,
                    owner=_IdentityGhostStripper, source_record=source_record,
                    frontend_runner=failed_frontend, tool_home=tool_home,
                    tool_spec=tool_spec, build_id=BUILD_ID,
                    provider_record=provider_record,
                    stage_runner=should_not_run, env=env,
                    source_controls=("const-substitution",), context_controls=())
            self.assertFalse(summary["complete"])
            self.assertEqual(len(frontend_calls), 1)
            self.assertEqual(summary["controls"]["const-substitution"]["classification"],
                             "UNKNOWN_UNCLASSIFIED")

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (repo, evidence, positive, tool_home, tool_spec, source_record,
             env, digest, pins, provider_record) = self._collection_fixture(root)
            def good_frontend(*, case, source_record):
                return {"errors": [], "source_record": source_record,
                        "guard_capture": {"stages": {}},
                        "full_body_capture": {"normal": {}, "readonly": {}}}
            def interrupted_stage(**_kwargs):
                raise KeyboardInterrupt("synthetic stage interruption")
            with patch.object(REFUSALS, "POSITIVE_ORIGINAL_SHA256", digest), \
                 patch.object(REFUSALS, "POSITIVE_VERIFIED_SHA256", digest), \
                 patch.object(REFUSALS, "_load_capture_pins", return_value=pins), \
                 patch.dict(os.environ, env, clear=False):
                with self.assertRaisesRegex(KeyboardInterrupt, "synthetic stage interruption"):
                    REFUSALS.collect_controls(
                        evidence=evidence, positive_case=positive, repo=repo,
                        owner=_IdentityGhostStripper, source_record=source_record,
                        frontend_runner=good_frontend, tool_home=tool_home,
                        tool_spec=tool_spec, build_id=BUILD_ID,
                        provider_record=provider_record,
                        stage_runner=interrupted_stage, env=env,
                        source_controls=(), context_controls=("legacy-selector",))
            summary_path = evidence / REFUSALS.SUMMARY_RELATIVE
            self.assertTrue(summary_path.is_file())
            partial = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertFalse(partial["complete"])
            self.assertEqual(partial["controls"]["legacy-selector"]["exception"]["type"],
                             "KeyboardInterrupt")
            self.assertTrue(partial["artifact_inventory"])

    def test_stage_exit_timeout_source_drift_and_invalid_utf8_refuse_classification(self):
        before = {"original/lib.rs": "a" * 64, "verified/lib.rs": "b" * 64}
        home = Path("/synthetic/tool")
        stage = {
            "status": "RAN", "exit": 2,
            "argv": [str(home / "bin/verifast"), "-rustc_args",
                     "--edition 2021", "-verbose", "1", "verified/lib.rs"],
            "source_before": before, "source_after": before,
            "source_unchanged": True, "intrinsic_gate_active": False,
            "pointer_drop_gate_active": False,
        }
        self.assertEqual(REFUSALS._stage_errors(
            stage, Path("/case"), "r24-mut-refusal-test", before,
            before, home, BUILD_ID), [])
        mutations = (
            {"exit": 1}, {"timeout": True}, {"status": "TIMEOUT"},
            {"source_after": {**before, "verified/lib.rs": "c" * 64}},
            {"intrinsic_gate_active": True}, {"pointer_drop_gate_active": True},
            {"argv": ["wrong"]},
        )
        for update in mutations:
            changed = {**stage, **update}
            with self.subTest(update=update):
                self.assertTrue(REFUSALS._stage_errors(
                    changed, Path("/case"), "r24-mut-refusal-test", before,
                    changed.get("source_after", before), home, BUILD_ID))
        with tempfile.TemporaryDirectory() as temp:
            case = Path(temp)
            bad_name = "r24-mut-refusal-invalid.log"
            (case / bad_name).write_bytes(b"\xff")
            with self.assertRaises(REFUSALS.RefusalError):
                REFUSALS._read_log(case, {"stdout": bad_name, "stderr": bad_name},
                                   "r24-mut-refusal-invalid")

    def test_frozen_link_stage_adapter_uses_proof_callback_contract(self):
        calls = []

        class Link:
            @staticmethod
            def stage(*args, **kwargs):
                calls.append((args, kwargs))
                return {"status": "RAN", "exit": 1}

        class Args:
            tool_home = "/synthetic/tool"
            schema = "/synthetic/schema.json"
            compiler_sysroot = "/synthetic/sysroot"
            deadline_epoch = 1234567890

        adapter = REFUSALS.make_link_stage_runner(Link, Args)
        case = Path("/synthetic/case")
        result = adapter(case=case, variant="const-substitution",
                         name="r24-mut-refusal-const-substitution",
                         build_id=BUILD_ID, child_environment_delta={})
        self.assertEqual(result, {"status": "RAN", "exit": 1})
        self.assertEqual(len(calls), 1)
        stage_args, stage_kwargs = calls[0]
        self.assertEqual(stage_args[0:2],
                         (case, "r24-mut-refusal-const-substitution"))
        self.assertEqual(stage_args[2], ["/synthetic/tool/bin/verifast",
                         "-rustc_args", "--edition 2021", "-verbose", "1",
                         "verified/lib.rs"])
        self.assertEqual(stage_args[3].tool_home, Path("/synthetic/tool"))
        self.assertEqual(stage_args[3].schema, Path("/synthetic/schema.json"))
        self.assertEqual(stage_args[3].compiler_sysroot, "/synthetic/sysroot")
        self.assertEqual(stage_args[3].deadline_epoch, 1234567890)
        self.assertEqual(stage_kwargs, {
            "gates": False, "pointer_drop": False, "cap_seconds": 1200})

    def test_frozen_frontend_capture_adapter_disables_semantic_barriers(self):
        calls = []
        class Guard:
            @staticmethod
            def capture_case(case, source_record, args):
                calls.append((case, source_record, args))
                return {"stages": {"normal-export": {"status": "RAN", "exit": 0}}}
        class Capture:
            GUARD = Guard
            @staticmethod
            def clear_semantic_opt_ins():
                calls.append("clear")
            @staticmethod
            def full_body_capture(case, source_record, stages):
                calls.append(("full", case, source_record, stages))
                return {"normal": {}, "readonly": {}}
        class Args:
            tool_home = "/synthetic/tool"
            schema = "/synthetic/schema.json"
            compiler_sysroot = "/synthetic/sysroot"
            deadline_epoch = 1234567890
        with tempfile.TemporaryDirectory() as temp:
            case = Path(temp)
            (case / "original").mkdir()
            (case / "verified").mkdir()
            (case / "original/lib.rs").write_bytes(b"original")
            (case / "verified/lib.rs").write_bytes(b"verified")
            source_record = {"original_sha256": "old", "verified_sha256": "old"}
            runner = REFUSALS.make_frontend_capture_runner(
                Capture, Args, lambda *_args, **_kwargs: [])
            result = runner(case=case, source_record=source_record)
            self.assertEqual(result["errors"], [])
            self.assertNotEqual(result["source_record"]["original_sha256"], "old")
            self.assertNotEqual(result["source_record"]["verified_sha256"], "old")
            self.assertIs(calls[0], "clear")
            capture_args = calls[1][2]
            self.assertIs(capture_args.first_barrier, False)
            self.assertIs(capture_args.fingerprint_probe, False)
            self.assertEqual(calls[-1][0], "full")


if __name__ == "__main__":
    unittest.main()
