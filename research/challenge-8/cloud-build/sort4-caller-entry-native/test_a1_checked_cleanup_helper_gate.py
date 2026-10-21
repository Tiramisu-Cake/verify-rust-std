"""Synthetic same-Build checked-helper gate controls; no compiler is run."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch


HERE = Path(__file__).resolve().parent


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load isolated module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


FOCUS = load("a1_checked_helper_focus_test", HERE / "a1-focus-backend.py")
AST = load("a1_checked_helper_ast_test", HERE / "a1-ast-gates.py")
RUNNER = load("a1_checked_helper_runner_test", HERE / "a1-runner.py")
BUILD_ID = "01234567-89ab-cdef-0123-456789abcdef"
PROFILE_SHA = "a" * 64
MISSING = object()
TR = "src/rust_frontend/vf_mir_translator/vf_mir_translator.ml"
SCHEMA = "src/rust_frontend/vf_mir/vf_mir.capnp"
EXPORTER = "src/rust_frontend/vf_mir_exporter/src/lib.rs"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def fixture_source() -> bytes:
    return (b"// fixture prefix\n"
            b"//@ use std::option::{Option, Option::None, Option::Some};\n"
            b"/*@\n"
            b"lem a1_cleanup_option_ref<'a, T>(value: std::option::Option<&'a T>)\n"
            b"    req thread_token(?t) &*& std::option::Option_own::<&'a T>(t, value);\n"
            b"    ens thread_token(t);\n"
            b"{\n"
            b"    open std::option::Option_own::<&'a T>(t, value);\n"
            b"    match value {\n"
            b"        Option::None => {}\n"
            b"        Option::Some(r) => {}\n"
            b"    }\n"
            b"}\n"
            b"@*/\n"
            b"fn caller() {}\n")


def metadata(source: bytes) -> dict:
    lines = source.splitlines(keepends=True)
    start, end, body_start, body_end = 3, 14, 4, 13
    block = b"".join(lines[start - 1:end])
    return {"name": "a1_cleanup_option_ref", "kind": "lemma",
            "source_start_line": start, "source_end_line": end,
            "source_sha256": sha(block), "body_start_line": body_start,
            "body_end_line": body_end}


def ast_text(*, duplicate=False, ambiguous=False, external=False,
             kind="manual_lemma", span=(4, 13)) -> str:
    kind_node = {
        "manual_lemma": "Lemma (false, None)",
        "lemma_atom": "Lemma",
        "auto_lemma": "Lemma (true, None)",
        "triggered_lemma": 'Lemma (false, Some ("trigger"))',
        "malformed_lemma": "Lemma (false)",
        "regular": "Regular",
        "legacy_full_span": "Lemma (false, None)",
    }[kind]
    def func():
        header_loc = (f'loc "verified/lib.rs({span[0]},1-{span[1]},1)"'
                      if kind == "legacy_full_span" else
                      f'loc "verified/lib.rs({span[0]},5-26)"')
        return (f'Func ({header_loc}, '
                f'{kind_node}, [], None, "a1_cleanup_option_ref", [], false, '
                f'(None, None), None, false, Some (([], '
                f'loc "verified/lib.rs({span[1]},1)")), false, [])')
    declaration = func()
    if duplicate:
        declaration += "; " + func()
    if ambiguous:
        declaration += ('; Func (loc "verified/lib.rs(2,5-10)", Regular, [], '
                        'None, "other_body", [], false, (None, None), None, '
                        'false, Some (([], loc "verified/lib.rs(4,1)")), false, [])')
    if external:
        declaration += ('; Func (loc "external/lib.rs(2,5-10)", Regular, [], '
                        'None, "external_body", [], false, (None, None), None, '
                        'false, Some (([], loc "external/lib.rs(4,1)")), false, [])')
    return (f'[PackageDecl (loc "verified/lib.rs(1,1)", "", [], '
            f'[{declaration}])]')


def runtime_func(name="caller", header=(20, 1, 30, 1), close=30) -> str:
    return (f'Func (loc "verified/lib.rs({header[0]},{header[1]}-'
            f'{header[2]},{header[3]})", Regular, [], None, "{name}", [], '
            f'false, (None, None), None, false, Some (([], '
            f'loc "verified/lib.rs({close},1)")), false, [])')


def focused_ast(*, caller_span=(20, 30), ghost_span=(4, 13),
                external=False) -> str:
    ghost = ('Func (loc "verified/lib.rs('
             f'{ghost_span[0]},5-26)", Lemma (false, None), [], None, '
             '"a1_cleanup_option_ref", [], false, (None, None), None, false, '
             f'Some (([], loc "verified/lib.rs({ghost_span[1]},1)")), false, [])')
    rows = [runtime_func(header=(caller_span[0], 1, caller_span[1], 1),
                         close=caller_span[1]), ghost]
    if external:
        rows.append('Func (loc "external/lib.rs(2,5-10)", Regular, [], None, '
                    '"external_body", [], false, (None, None), None, false, '
                    'Some (([], loc "external/lib.rs(4,1)")), false, [])')
    return ('[PackageDecl (loc "verified/lib.rs(1,1)", "", [], [' +
            '; '.join(rows) + '])]')


class FakeArgs:
    deadline_epoch = int(time.time()) + 1000


class FakeStage:
    def __init__(self, ast: str | None, exit_code: int = 0, after_stage=None):
        self.ast = ast
        self.exit_code = exit_code
        self.after_stage = after_stage
        self.calls = 0
        self.environments = []

    def stage(self, _args, root, name, argv, env, _cap, *, cwd):
        self.calls += 1
        self.environments.append(dict(env))
        root.mkdir(parents=True, exist_ok=True)
        ast_path = Path(argv[argv.index("-dump_ast_with_locs") + 1])
        if self.ast is not None:
            ast_path.write_text(self.ast)
        log = root / f"{name}.log"
        log.write_bytes(b"synthetic focused helper stage\n")
        if self.after_stage is not None:
            self.after_stage()
        return {"argv": argv, "cwd": str(cwd), "timeout_seconds": 180,
                "classification": "TERMINAL", "exit": self.exit_code,
                "log_sha256": sha(log.read_bytes())}


class CheckedCleanupHelperGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.fixture = self.root / "fixture"
        self.fixture.mkdir()
        self.source = fixture_source()
        (self.fixture / "verified").mkdir()
        (self.fixture / "original").mkdir()
        (self.fixture / "verified/lib.rs").write_bytes(self.source)
        (self.fixture / "original/lib.rs").write_bytes(self.source)
        self.profile_path = self.root / "profile.json"
        self.profile_path.write_text("{}\n")
        self.profile_sha = PROFILE_SHA
        self.profile = {"a1_checked_cleanup_helper_sha256": metadata(self.source)["source_sha256"]}
        self.case = {"case_id": "P0c", "source_id": "source-id", "unit_id": "unit-id",
                     "generated_source_sha256": sha(self.source),
                     "checked_cleanup_helper": metadata(self.source)}
        self.certificate_path = self.root / "source-certificate.json"
        self.certificate_path.write_text(json.dumps({"cases": {"P0c": self.case}}))
        self.tool = self.root / "tool"
        for rel in (TR, SCHEMA, EXPORTER, "bin/verifast",
                    "bin/vf-rust-mir-exporter"):
            path = self.tool / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(("synthetic " + rel).encode())
        self.receipt = {"classification": "A1_TOOL_BUILT_UNRUN_PROOF",
                        "phase_id": RUNNER.PHASE, "proof_credit": False,
                        "final_translator_sha256": sha((self.tool / TR).read_bytes()),
                        "final_schema_sha256": sha((self.tool / SCHEMA).read_bytes()),
                        "final_exporter_sha256": sha((self.tool / EXPORTER).read_bytes()),
                        "console_binary_sha256": sha((self.tool / "bin/verifast").read_bytes()),
                        "exporter_binary_sha256": sha((self.tool / "bin/vf-rust-mir-exporter").read_bytes())}
        self.args = FakeArgs()
        self.stage = FakeStage(ast_text())
        self.env = {"SMALLSORT_EXECUTION_PROVIDER": "cloud-build",
                    "SORT4_A1_PHASE_ID": FOCUS.PHASE,
                    "SORT4_A1_CHECKED_TRAIT_CONTRACT": "1",
                    "SORT4_A1_STAGE": "caller",
                    "SORT4_A1_PROFILE_SHA256": PROFILE_SHA,
                    "CLOUD_BUILD_ID": BUILD_ID}
        self.root_evidence = self.root / "focus" / "P0c"
        self.root_evidence.mkdir(parents=True)
        self._env_patch = patch.dict(os.environ, {"CLOUD_BUILD_ID": BUILD_ID,
                                                  "SORT4_A1_PROFILE_SHA256": PROFILE_SHA})
        self._env_patch.start()

    def tearDown(self):
        self._env_patch.stop()
        self.temp.cleanup()

    def collect(self, *, metadata_value=MISSING, profile=None, receipt="default",
                stage=None, deadline=None, env=None):
        case = dict(self.case)
        if metadata_value is not MISSING:
            case["checked_cleanup_helper"] = metadata_value
        prof = dict(self.profile if profile is None else profile)
        actual_receipt = self.receipt if receipt == "default" else receipt
        fake = self.stage if stage is None else stage
        args = self.args if deadline is None else type("Args", (), {"deadline_epoch": deadline})()
        return FOCUS._checked_cleanup_helper_proof(
            args, fake, self.tool, actual_receipt, prof, self.fixture,
            self.root_evidence, self.env if env is None else env, self.source, case,
            self.certificate_path, AST, RUNNER.select_checked_cleanup_helper_lemma)

    def test_success_produces_same_build_noncredit_record_and_core_accepts_it(self):
        record = self.collect()
        self.assertEqual(record["status"], "HELPER_BODY_VERIFIED_SAME_BUILD")
        self.assertEqual(record["build_id"], BUILD_ID)
        self.assertEqual(record["source_pair_sha256"], {
            "verified/lib.rs": sha(self.source), "original/lib.rs": sha(self.source)})
        self.assertEqual(record["ast_selection"]["selected"]["kind"], "lemma")
        self.assertFalse(record["proof_credit"])
        raw = {"checked_helper_required": True, "checked_helper_proof": record,
               "checked_helper_proof_path": str(self.root_evidence / "checked-cleanup-helper-proof.json"),
               "evidence_root": str(self.root_evidence), "build_id": BUILD_ID,
               "focus_stage": "caller",
               "source_pair_sha256": {"verified": sha(self.source), "original": sha(self.source)}}
        (self.root_evidence / "checked-cleanup-helper-proof.json").write_text(
            json.dumps(record, indent=2, sort_keys=True) + "\n")
        self.assertTrue(RUNNER.checked_helper_record_valid(
            raw, profile=self.profile, certificate_case=self.case,
            certificate_path=self.certificate_path, fixture=self.fixture,
            tool=self.tool, tool_receipt=self.receipt,
            ast_gates=AST, expected_caller_env=self.env))
        actual_pair = dict(raw["source_pair_sha256"])
        for malformed in (None, {}, record["source_pair_sha256"],
                          {"verified": sha(self.source)},
                          dict(actual_pair, extra=sha(self.source)),
                          dict(actual_pair, verified="0" * 64),
                          dict(actual_pair, verified=None),
                          dict(actual_pair, original="wrong")):
            raw["source_pair_sha256"] = malformed
            self.assertFalse(RUNNER.checked_helper_record_valid(
                raw, profile=self.profile, certificate_case=self.case,
                certificate_path=self.certificate_path, fixture=self.fixture,
                tool=self.tool, tool_receipt=self.receipt,
                ast_gates=AST, expected_caller_env=self.env), malformed)
        raw["source_pair_sha256"] = actual_pair
        for field, value in (("build_id", "other-build"),
                             ("profile_sha256", "b" * 64),
                             ("source_pair_sha256", {"verified/lib.rs": "0" * 64,
                                                      "original/lib.rs": sha(self.source)}),
                             ("helper_source_sha256", "c" * 64),
                             ("ast_sha256", "d" * 64)):
            bad = dict(record, **{field: value})
            raw["checked_helper_proof"] = bad
            (self.root_evidence / "checked-cleanup-helper-proof.json").write_text(
                json.dumps(bad, indent=2, sort_keys=True) + "\n")
            self.assertFalse(RUNNER.checked_helper_record_valid(
                raw, profile=self.profile, certificate_case=self.case,
                certificate_path=self.certificate_path, fixture=self.fixture,
                tool=self.tool, tool_receipt=self.receipt,
                ast_gates=AST, expected_caller_env=self.env), field)
        raw["checked_helper_proof"] = record
        (self.root_evidence / "checked-cleanup-helper-proof.json").write_text(
            json.dumps(record, indent=2, sort_keys=True) + "\n")
        ast_path = Path(record["ast_artifact"]["path"])
        ast_contents = ast_path.read_text()
        ast_path.write_text(ast_contents + "\n")
        self.assertFalse(RUNNER.checked_helper_record_valid(
            raw, profile=self.profile, certificate_case=self.case,
            certificate_path=self.certificate_path, fixture=self.fixture,
            tool=self.tool, tool_receipt=self.receipt,
            ast_gates=AST, expected_caller_env=self.env), "mutated AST bytes")
        ast_path.write_text(ast_contents)
        source_path = self.fixture / "verified/lib.rs"
        original_source = source_path.read_bytes()
        source_path.write_bytes(original_source + b"// changed after proof\n")
        self.assertFalse(RUNNER.checked_helper_record_valid(
            raw, profile=self.profile, certificate_case=self.case,
            certificate_path=self.certificate_path, fixture=self.fixture,
            tool=self.tool, tool_receipt=self.receipt,
            ast_gates=AST, expected_caller_env=self.env), "mutated source pair")

    def test_core_binds_receipt_to_active_tool_and_exact_stage_cwd(self):
        record = self.collect()
        raw = {"checked_helper_required": True, "checked_helper_proof": record,
               "checked_helper_proof_path": str(self.root_evidence / "checked-cleanup-helper-proof.json"),
               "evidence_root": str(self.root_evidence), "build_id": BUILD_ID,
               "focus_stage": "caller",
               "source_pair_sha256": {"verified": sha(self.source), "original": sha(self.source)}}
        record_path = self.root_evidence / "checked-cleanup-helper-proof.json"
        record_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
        def valid():
            return RUNNER.checked_helper_record_valid(
                raw, profile=self.profile, certificate_case=self.case,
                certificate_path=self.certificate_path, fixture=self.fixture,
                tool=self.tool, tool_receipt=self.receipt, ast_gates=AST,
                expected_caller_env=self.env)
        self.assertTrue(valid())

        copied_tool = self.root / "copied-tool"
        copied_binary = copied_tool / "bin/verifast"
        copied_binary.parent.mkdir(parents=True)
        copied_binary.write_bytes((self.tool / "bin/verifast").read_bytes())
        alternate = json.loads(json.dumps(record))
        alternate["tool_binary_path"] = str(copied_binary)
        alternate["stage"]["argv"][0] = str(copied_binary)
        raw["checked_helper_proof"] = alternate
        record_path.write_text(json.dumps(alternate, indent=2, sort_keys=True) + "\n")
        self.assertFalse(valid(), "same bytes at another tool path")

        changed_binary = self.root / "unrelated-verifast"
        changed_binary.write_bytes(b"different verifier bytes")
        alternate["tool_binary_path"] = str(changed_binary)
        alternate["tool_binary_sha256"] = sha(changed_binary.read_bytes())
        alternate["stage"]["argv"][0] = str(changed_binary)
        raw["checked_helper_proof"] = alternate
        record_path.write_text(json.dumps(alternate, indent=2, sort_keys=True) + "\n")
        self.assertFalse(valid(), "different binary at an arbitrary path/hash")

        raw["checked_helper_proof"] = record
        record_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
        wrong_cwd = json.loads(json.dumps(record))
        wrong_cwd["stage"]["cwd"] = str(self.root)
        raw["checked_helper_proof"] = wrong_cwd
        record_path.write_text(json.dumps(wrong_cwd, indent=2, sort_keys=True) + "\n")
        self.assertFalse(valid(), "wrong helper stage cwd")

        raw["checked_helper_proof"] = record
        record_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
        wrong_receipt = dict(self.receipt, console_binary_sha256="0" * 64)
        self.assertFalse(RUNNER.checked_helper_record_valid(
            raw, profile=self.profile, certificate_case=self.case,
            certificate_path=self.certificate_path, fixture=self.fixture,
            tool=self.tool, tool_receipt=wrong_receipt, ast_gates=AST,
            expected_caller_env=self.env),
            "active tool receipt hash mismatch")

        bad_environment = json.loads(json.dumps(record))
        bad_environment["environment_identity"]["helper_a1"]["SORT4_A1_STAGE"] = "caller"
        raw["checked_helper_proof"] = bad_environment
        record_path.write_text(json.dumps(bad_environment, indent=2, sort_keys=True) + "\n")
        self.assertFalse(valid(), "caller-only stage leaked into helper environment receipt")

        bad_environment = json.loads(json.dumps(record))
        bad_environment["environment_identity"]["caller_sha256"] = "f" * 64
        raw["checked_helper_proof"] = bad_environment
        record_path.write_text(json.dumps(bad_environment, indent=2, sort_keys=True) + "\n")
        self.assertFalse(valid(), "substituted caller full-environment digest is rejected")

        bad_environment = json.loads(json.dumps(record))
        bad_environment["environment_identity"]["helper_sha256"] = "f" * 64
        raw["checked_helper_proof"] = bad_environment
        record_path.write_text(json.dumps(bad_environment, indent=2, sort_keys=True) + "\n")
        self.assertFalse(valid(), "substituted helper full-environment digest is rejected")

    def test_source_pair_changed_during_helper_stage_is_blocked(self):
        source_path = self.fixture / "verified/lib.rs"
        fake = FakeStage(ast_text(), after_stage=lambda: source_path.write_bytes(
            self.source + b"// changed during stage\n"))
        record = self.collect(stage=fake)
        self.assertEqual(record["status"], "BLOCKED_CHECKED_HELPER_PREREQUISITE")
        self.assertIn("source pair changed", record["error"])

    def test_tool_changed_during_helper_stage_is_blocked(self):
        tool_path = self.tool / "bin/verifast"
        fake = FakeStage(ast_text(), after_stage=lambda: tool_path.write_bytes(
            b"changed pinned console"))
        record = self.collect(stage=fake)
        self.assertEqual(record["status"], "BLOCKED_CHECKED_HELPER_PREREQUISITE")
        self.assertIn("final A1 tool file differs", record["error"])

    def test_nonzero_verifier_preserves_failure_and_never_reports_success(self):
        fake = FakeStage(ast_text(), exit_code=1)
        record = self.collect(stage=fake)
        self.assertEqual(record["status"], "HELPER_VERIFIER_FAILED")
        self.assertEqual(record["stage"]["exit"], 1)
        self.assertEqual(fake.calls, 1)
        self.assertEqual(fake.environments[0]["SORT4_A1_STAGE"], "checked-helper")
        self.assertFalse(record["proof_credit"])

    def test_success_exit_without_ast_is_blocked(self):
        record = self.collect(stage=FakeStage(None))
        self.assertEqual(record["status"], "BLOCKED_CHECKED_HELPER_PREREQUISITE")
        self.assertEqual(record["ast_artifact"]["sha256"], None)

    def test_null_receipt_and_wrong_metadata_type_fail_before_stage(self):
        fake = FakeStage(ast_text())
        record = self.collect(receipt=None, stage=fake)
        self.assertEqual(record["status"], "BLOCKED_CHECKED_HELPER_PREREQUISITE")
        self.assertEqual(fake.calls, 0)
        fake = FakeStage(ast_text())
        record = self.collect(metadata_value=[], stage=fake)
        self.assertEqual(record["status"], "BLOCKED_INVALID_SOURCE_CERTIFICATE_OR_PROFILE")
        self.assertEqual(fake.calls, 0)

    def test_one_sided_profile_or_certificate_declaration_fails_closed(self):
        record = self.collect(profile={})
        self.assertEqual(record["status"], "BLOCKED_INVALID_SOURCE_CERTIFICATE_OR_PROFILE")
        record = self.collect(metadata_value=None, profile=self.profile)
        self.assertEqual(record["status"], "BLOCKED_INVALID_SOURCE_CERTIFICATE_OR_PROFILE")

    def test_helper_environment_isolated_and_original_caller_environment_restored(self):
        caller_env = dict(self.env, SORT4_A1_FORCE_LEGACY_REDIRECT="1")
        original = dict(caller_env)
        fake = FakeStage(ast_text())
        record = self.collect(stage=fake, env=caller_env)
        self.assertEqual(record["status"], "HELPER_BODY_VERIFIED_SAME_BUILD")
        helper_env = fake.environments[0]
        self.assertEqual(helper_env["SORT4_A1_CHECKED_TRAIT_CONTRACT"], "1")
        self.assertEqual(helper_env["SORT4_A1_STAGE"], "checked-helper")
        self.assertNotIn("SORT4_A1_FORCE_LEGACY_REDIRECT", helper_env)
        self.assertEqual(helper_env["SORT4_A1_CHECKED_HELPER_NAME"],
                         "a1_cleanup_option_ref")
        self.assertEqual(helper_env["SORT4_A1_CHECKED_HELPER_SOURCE_SHA256"],
                         sha(self.source))
        self.assertEqual(helper_env["SORT4_A1_CHECKED_HELPER_BLOCK_SHA256"],
                         metadata(self.source)["source_sha256"])
        self.assertEqual(caller_env, original)
        identity = record["environment_identity"]
        self.assertEqual(identity["caller_sha256"],
                         FOCUS._stage_environment_sha256(original))
        self.assertEqual(identity["helper_sha256"],
                         FOCUS._stage_environment_sha256(helper_env))
        self.assertEqual(identity["caller_a1"]["SORT4_A1_STAGE"], "caller")
        self.assertEqual(identity["helper_a1"]["SORT4_A1_STAGE"], "checked-helper")
        self.assertEqual(identity["helper_a1"]["SORT4_A1_CHECKED_TRAIT_CONTRACT"], "1")

    def test_missing_or_wrong_caller_environment_blocks_before_stage(self):
        for change in ({"SORT4_A1_CHECKED_TRAIT_CONTRACT": None},
                       {"SORT4_A1_STAGE": "bodies"}):
            with self.subTest(change=change):
                caller_env = dict(self.env)
                caller_env.update(change)
                fake = FakeStage(ast_text())
                record = self.collect(stage=fake, env=caller_env)
                self.assertEqual(record["status"], "BLOCKED_CHECKED_HELPER_PREREQUISITE")
                self.assertEqual(fake.calls, 0)

    def test_interface_caller_environment_is_not_reused_for_helper_stage(self):
        caller_env = dict(self.env, SORT4_A1_STAGE="interface")
        fake = FakeStage(ast_text())
        record = self.collect(stage=fake, env=caller_env)
        self.assertEqual(record["status"], "HELPER_BODY_VERIFIED_SAME_BUILD")
        self.assertEqual(record["environment_identity"]["caller_mode"], "interface")
        self.assertEqual(fake.environments[0]["SORT4_A1_STAGE"], "checked-helper")
        self.assertEqual(caller_env["SORT4_A1_STAGE"], "interface")
    def test_deadline_and_ambiguous_ast_skip_the_caller(self):
        record = self.collect(deadline=int(time.time()) + 100)
        self.assertEqual(record["status"], "NOT_RUN_DEADLINE")
        self.assertEqual(self.stage.calls, 0)
        record = self.collect(stage=FakeStage(ast_text(duplicate=True)))
        self.assertEqual(record["status"], "BLOCKED_CHECKED_HELPER_PREREQUISITE")
        self.assertIn("one exact checked cleanup helper AST function", record["error"])
        with self.assertRaisesRegex(RuntimeError, "ambiguous AST function interval"):
            RUNNER.select_checked_cleanup_helper_lemma(
                ast_text(ambiguous=True), AST, self.source,
                metadata(self.source) | {"source_bytes_sha256":
                                         metadata(self.source)["source_sha256"]})

    def test_helper_selector_skips_unrelated_external_definition(self):
        selected = RUNNER.select_checked_cleanup_helper_lemma(
            ast_text(external=True), AST, self.source,
            metadata(self.source) | {"source_bytes_sha256":
                                     metadata(self.source)["source_sha256"]})
        self.assertEqual(selected["body_count_from_intervals"], 1)

    def test_caller_focus_counts_nonoverlap_ghost_and_skips_external_body(self):
        selected = RUNNER.select_focused_body(
            focused_ast(external=True), AST, focus_line=20,
            expected_name="caller", compiler_span=(20, 30))
        self.assertEqual(selected["selected"]["name"], "caller")
        self.assertEqual(selected["selected"]["effective_span"], (20, 30))

    def test_caller_focus_rejects_overlapping_ghost_and_runtime_span_mismatch(self):
        with self.assertRaisesRegex(RuntimeError, "exactly one compiler-bound"):
            RUNNER.select_focused_body(
                focused_ast(ghost_span=(20, 22)), AST, focus_line=20,
                expected_name="caller", compiler_span=(20, 30))
        with self.assertRaisesRegex(RuntimeError, "close brace differs"):
            RUNNER.select_focused_body(
                '[PackageDecl (loc "verified/lib.rs(1,1)", "", [], [' +
                runtime_func(header=(20, 1, 30, 1), close=29) + '])]',
                AST, focus_line=20, expected_name="caller",
                compiler_span=(20, 30))

    def test_wrong_ast_kind_or_interval_is_rejected(self):
        for kind in ("regular", "lemma_atom", "auto_lemma", "triggered_lemma",
                     "malformed_lemma", "legacy_full_span"):
            with self.subTest(kind=kind):
                record = self.collect(stage=FakeStage(ast_text(kind=kind)))
                self.assertEqual(record["status"],
                                 "BLOCKED_CHECKED_HELPER_PREREQUISITE")
        record = self.collect(stage=FakeStage(ast_text(span=(4, 12))))
        self.assertEqual(record["status"], "BLOCKED_CHECKED_HELPER_PREREQUISITE")
        record = self.collect(stage=FakeStage(ast_text(span=(4, 3))))
        self.assertEqual(record["status"], "BLOCKED_CHECKED_HELPER_PREREQUISITE")

    def test_duplicate_source_helper_is_rejected_before_verification(self):
        block = b"".join(self.source.splitlines(keepends=True)[2:14])
        duplicate = self.source + block
        (self.fixture / "verified/lib.rs").write_bytes(duplicate)
        fake = FakeStage(ast_text())
        case = dict(self.case, generated_source_sha256=sha(duplicate))
        record = FOCUS._checked_cleanup_helper_proof(
            self.args, fake, self.tool, self.receipt, self.profile,
            self.fixture, self.root_evidence, self.env, duplicate, case,
            self.certificate_path, AST, RUNNER.select_checked_cleanup_helper_lemma)
        self.assertEqual(record["status"], "BLOCKED_INVALID_SOURCE_CERTIFICATE_OR_PROFILE")
        self.assertEqual(fake.calls, 0)


if __name__ == "__main__":
    unittest.main()
