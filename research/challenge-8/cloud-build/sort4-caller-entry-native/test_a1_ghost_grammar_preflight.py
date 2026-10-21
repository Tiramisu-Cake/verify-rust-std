"""Synthetic service tests for the isolated grammar preflight (no compiler)."""
from __future__ import annotations

import hashlib
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import time
import types
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


GRAMMAR = load("a1_ghost_grammar_test", HERE / "a1-ghost-grammar.py")
FIXTURES = load("a1_ghost_fixture_source_test", HERE / "a1-fixtures.py")
GHOST = load("a1_ghost_strip_source_test",
             HERE.parent / "sort4-native-c1-bound" / "ghost-strip.py")


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


class FakeArgs:
    deadline_epoch = int(time.time()) + 1000


class FakeC4:
    def __init__(self, scenario="pass"):
        self.scenario = scenario
        self.calls = []
        self.provider_path = None

    def clean_env(self, _a, _tool):
        return {"RUSTUP_TOOLCHAIN": "nightly-2026-09-25", "PATH": "/bin",
                "SMALLSORT_CLOUD_PROVIDER_PATH": str(self.provider_path)}

    def stage(self, _a, root, name, argv, env, _cap, *, cwd):
        variant = root.parent.name
        self.calls.append((variant, dict(env), Path(cwd)))
        if self.scenario == "exception" and variant == "positive":
            raise OSError("synthetic stage transport exception")
        if self.scenario == "partial" and variant == "positive":
            return {"classification": "RUNNING", "exit": None}
        if self.scenario == "not_run" and variant == "positive":
            return {"classification": "NOT_RUN_DEADLINE", "timeout_seconds": 0}
        if self.scenario == "missing_metadata" and variant == "positive":
            return {"classification": "TERMINAL"}
        if self.scenario == "null_exit" and variant == "positive":
            return {"classification": "TERMINAL", "exit": None}
        if self.scenario == "wrong_type_exit" and variant == "positive":
            return {"classification": "TERMINAL", "exit": "0"}
        if self.scenario == "unexpected_negative_pass" and variant.startswith("negative"):
            code, log_text = 0, ""
        elif variant == "positive":
            code, log_text = 0, ""
        elif variant == "negative_fully_qualified":
            source = (Path(cwd) / "verified/lib.rs").read_text()
            line = next(i for i, row in enumerate(source.splitlines(), 1)
                        if "std::option::Option::None" in row)
            code = 1
            log_text = (f"verified/lib.rs({line},9): error: "
                        "Not a constructor of type std::option::Option\n")
        else:
            source = (Path(cwd) / "verified/lib.rs").read_text()
            anchor = ("use std::option::{Option, Option::None, Option::Some};"
                      if self.scenario == "parse_at_use_line" else
                      "lem a1_cleanup_option_ref")
            line = next(i for i, row in enumerate(source.splitlines(), 1)
                        if anchor in row)
            code = 1
            log_text = f"verified/lib.rs({line},1): Parse error\n"
        if self.scenario == "wrong_diagnostic" and variant.startswith("negative"):
            log_text = "verified/lib.rs(999,1): Parse error: unrelated\n"
        log = root / f"{name}.log"
        log.write_text(log_text)
        ast_path = Path(argv[argv.index("-dump_ast_with_locs") + 1])
        if variant == "positive" and code == 0:
            ast_path.write_text("synthetic AST")
        row = {"classification": "TERMINAL", "exit": code,
               "log_sha256": sha(log.read_bytes())}
        if self.scenario == "wrong_log_hash" and variant == "positive":
            row["log_sha256"] = "0" * 64
        return row


class FakeSelector:
    def __init__(self, malformed=False):
        self.malformed = malformed
        self.calls = []

    def __call__(self, ast_text, ast_gates, source, metadata):
        self.calls.append((ast_text, source, dict(metadata)))
        if self.malformed:
            return {"classification": "ONE_SOURCE_INTERVAL_SELECTED_CHECKED_LEMMA",
                    "body_count_from_intervals": 2,
                    "selected": {"name": "a1_cleanup_option_ref", "kind": "lemma"},
                    "proof_credit": False}
        return {"classification": "ONE_SOURCE_INTERVAL_SELECTED_CHECKED_LEMMA",
                "body_count_from_intervals": 1,
                "selected": {"name": "a1_cleanup_option_ref", "kind": "lemma"},
                "proof_credit": False}


class GhostGrammarPreflightTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.tool = self.root / "tool"
        for rel in ("bin", "src/rust_frontend/vf_mir_translator",
                    "src/rust_frontend/vf_mir", "src/rust_frontend/vf_mir_exporter",
                    "src"):
            (self.tool / rel).mkdir(parents=True, exist_ok=True)
        self.files = {
            "bin/verifast": b"console",
            "src/rust_frontend/vf_mir_translator/vf_mir_translator.ml": b"translator",
            "src/rust_frontend/vf_mir/vf_mir.capnp": b"schema",
            "src/rust_frontend/vf_mir_exporter/src/lib.rs": b"exporter",
            "src/verifast.ml": b"kernel",
        }
        self.tool_shas = {}
        for rel, raw in self.files.items():
            path = self.tool / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
            self.tool_shas[rel] = sha(raw)
        self.profile = {
            "ghost_grammar_preflight_enabled": True,
            "a1_checked_cleanup_import_sha256": sha(FIXTURES.OPTION_CLEANUP_IMPORT),
            "profile_pin_source": "coordinator-environment",
            "cloud_build_enabled": True,
            "profile_accepted": False,
            "authorization_phase_id": "SORT4-CHECKED-HELPER-CALLER-2026-10-21-R12",
            "experiment_protocol_phase_id": "SORT4-A1-CHECKED-TRAIT-CONTRACT-CLOUD-2026-10-17",
            "phase_id": "SORT4-A1-CHECKED-TRAIT-CONTRACT-CLOUD-2026-10-17",
            "compiler_toolchain": "nightly-2026-09-25",
            "tool_head": "f" * 40,
        }
        self.receipt = {
            "classification": "A1_TOOL_BUILT_UNRUN_PROOF", "proof_credit": False,
            "build_exit": 0, "tool_head": self.profile["tool_head"],
            "phase_id": self.profile["phase_id"],
            "console_binary_sha256": self.tool_shas["bin/verifast"],
            "final_translator_sha256": self.tool_shas[
                "src/rust_frontend/vf_mir_translator/vf_mir_translator.ml"],
            "final_schema_sha256": self.tool_shas["src/rust_frontend/vf_mir/vf_mir.capnp"],
            "final_exporter_sha256": self.tool_shas[
                "src/rust_frontend/vf_mir_exporter/src/lib.rs"],
            "final_kernel_sha256": self.tool_shas["src/verifast.ml"],
        }
        self.args = FakeArgs()
        self.args.evidence = self.root / "evidence"
        self.provider_path = self.root / "provider.py"
        self.provider_path.write_text("# synthetic provider identity\n")
        self.c4 = FakeC4()
        self.c4.provider_path = self.provider_path
        self.selector = FakeSelector()
        self.env_patch = patch.dict(os.environ, {
            "SMALLSORT_EXECUTION_PROVIDER": "cloud-build",
            "CLOUD_BUILD_ID": "01234567-89ab-cdef-0123-456789abcdef",
            "CLOUD_BUILD_PROJECT_ID": "small-sort-project",
            "SORT4_A1_AUTHORIZATION_PHASE_ID": self.profile["authorization_phase_id"],
            "SORT4_A1_PHASE_ID": self.profile["phase_id"],
            "SORT4_A1_PROFILE_SHA256": "a" * 64,
        })
        self.env_patch.start()
        self.workspace_patch = patch.object(GRAMMAR, "_workspace_path",
                                            lambda path, _label: Path(path))
        self.workspace_patch.start()

    def tearDown(self):
        self.workspace_patch.stop()
        self.env_patch.stop()
        self.tmp.cleanup()

    def run_preflight(self, *, scenario="pass", profile=None, receipt=None,
                      selector=None):
        self.args.evidence = self.root / f"evidence-{scenario}-{len(getattr(self, '_runs', []))}"
        self._runs = [*getattr(self, "_runs", []), scenario]
        c4 = FakeC4(scenario)
        c4.provider_path = self.provider_path
        result = GRAMMAR.run(self.args, c4, self.tool,
                             self.receipt if receipt is None else receipt,
                             self.profile if profile is None else profile,
                             FIXTURES, GHOST, object(),
                             self.selector if selector is None else selector)
        return result, c4

    def test_three_controls_pass_with_exact_hashes_and_no_credit(self):
        result, c4 = self.run_preflight()
        self.assertEqual(result["status"], "GRAMMAR_PREFLIGHT_PASS")
        self.assertEqual(set(result["variants"]), set(GRAMMAR.VARIANTS))
        self.assertEqual(result["variants"]["positive"]["status"],
                         "GRAMMAR_POSITIVE_PASS")
        self.assertEqual(result["variants"]["positive"]["ast_selection"]["body_count_from_intervals"], 1)
        self.assertEqual(result["variants"]["negative_fully_qualified"]["status"],
                         "EXPECTED_GRAMMAR_REJECTION")
        self.assertEqual(result["variants"]["negative_import_inside_block"]["status"],
                         "EXPECTED_GRAMMAR_REJECTION")
        self.assertFalse(result["proof_credit"])
        self.assertFalse(result["caller_receipt"])
        self.assertEqual(len(self.selector.calls), 1)
        self.assertEqual(len(c4.calls), 3)
        self.assertTrue(all(not any(k.startswith(("SORT4_A1_", "O26_WITH_"))
                                for k in env) for _, env, _ in c4.calls))
        for case in result["variants"].values():
            self.assertEqual(case["source_pair_sha256"]["verified/lib.rs"],
                             case["source_sha256"])
            self.assertEqual(case["source_pair_sha256"]["original/lib.rs"],
                             case["original_sha256"])
            self.assertTrue(case["same_active_binary_after_stage"])

    def test_expected_negative_diagnostics_must_be_at_exact_source_line(self):
        result, _ = self.run_preflight(scenario="wrong_diagnostic")
        self.assertEqual(result["status"], "GRAMMAR_PREFLIGHT_INCONCLUSIVE")
        self.assertEqual(result["variants"]["negative_fully_qualified"]["status"],
                         "GRAMMAR_NEGATIVE_UNEXPECTED_FAILURE")

    def test_s5_control_is_bare_use_and_parse_error_is_anchored_to_lemma(self):
        variants = GRAMMAR._source_variants(FIXTURES, GHOST)
        source = variants["negative_import_inside_block"]["verified"]
        self.assertIn(b"/*@\nuse std::option::{Option, Option::None, Option::Some};\nlem ",
                      source)
        self.assertNotIn(b"/*@\n//@ use std::option::", source)
        self.assertNotIn(FIXTURES.OPTION_CLEANUP_IMPORT, source)
        result, _ = self.run_preflight(scenario="parse_at_use_line")
        case = result["variants"]["negative_import_inside_block"]
        self.assertEqual(case["status"], "GRAMMAR_NEGATIVE_UNEXPECTED_FAILURE")
        expected_line = next(i for i, row in enumerate(source.splitlines(), 1)
                             if b"lem a1_cleanup_option_ref" in row)
        self.assertEqual(case["diagnostic_match"]["expected_source_line"], expected_line)

    def test_positive_does_not_accept_bad_ast_selector_metadata(self):
        result, _ = self.run_preflight(selector=FakeSelector(malformed=True))
        self.assertEqual(result["variants"]["positive"]["status"],
                         "INCONCLUSIVE_EXCEPTION")
        self.assertEqual(result["status"], "GRAMMAR_PREFLIGHT_INCONCLUSIVE")

    def test_nonzero_expected_negative_pass_is_not_accepted(self):
        result, _ = self.run_preflight(scenario="unexpected_negative_pass")
        self.assertEqual(result["variants"]["negative_fully_qualified"]["status"],
                         "GRAMMAR_NEGATIVE_UNEXPECTED_PASS")

    def test_stage_exception_is_preserved(self):
        result, _ = self.run_preflight(scenario="exception")
        positive = result["variants"]["positive"]
        self.assertEqual(positive["status"], "INCONCLUSIVE_EXCEPTION")
        self.assertEqual(positive["exception_type"], "OSError")
        self.assertIn("synthetic stage transport exception", positive["exception"])

    def test_partial_stage_is_not_terminal_or_proof(self):
        result, _ = self.run_preflight(scenario="partial")
        self.assertEqual(result["variants"]["positive"]["status"],
                         "NOT_RUN_OR_PARTIAL")
        self.assertEqual(result["status"], "GRAMMAR_PREFLIGHT_INCONCLUSIVE")

    def test_not_run_stage_remains_not_run(self):
        result, _ = self.run_preflight(scenario="not_run")
        self.assertEqual(result["variants"]["positive"]["status"],
                         "NOT_RUN_OR_PARTIAL")
        self.assertEqual(result["variants"]["positive"]["stage_classification"],
                         "NOT_RUN_DEADLINE")

    def test_missing_null_and_wrong_type_exit_fail_closed(self):
        for scenario in ("missing_metadata", "null_exit", "wrong_type_exit"):
            with self.subTest(scenario=scenario):
                result, _ = self.run_preflight(scenario=scenario)
                positive = result["variants"]["positive"]
                self.assertIn(positive["status"], {
                    "INCONCLUSIVE_MALFORMED_STAGE", "INCONCLUSIVE_MALFORMED_EXIT"})

    def test_log_hash_mismatch_fails_closed(self):
        result, _ = self.run_preflight(scenario="wrong_log_hash")
        self.assertEqual(result["variants"]["positive"]["status"],
                         "INCONCLUSIVE_MISSING_OR_MISMATCHED_LOG")

    def test_profile_and_tool_identity_guards_run_before_any_stage(self):
        profile = dict(self.profile, ghost_grammar_preflight_enabled=False)
        result, c4 = self.run_preflight(profile=profile)
        self.assertEqual(result["status"], "GRAMMAR_PREFLIGHT_BLOCKED")
        self.assertEqual(c4.calls, [])
        profile = dict(self.profile, a1_checked_cleanup_import_sha256="0" * 64)
        result, c4 = self.run_preflight(profile=profile)
        self.assertEqual(result["status"], "GRAMMAR_PREFLIGHT_BLOCKED")
        self.assertEqual(c4.calls, [])
        bad_receipt = dict(self.receipt, console_binary_sha256="0" * 64)
        result, c4 = self.run_preflight(receipt=bad_receipt)
        self.assertEqual(result["status"], "GRAMMAR_PREFLIGHT_BLOCKED")
        self.assertEqual(c4.calls, [])


if __name__ == "__main__":
    unittest.main()
