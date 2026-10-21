"""Isolated controls for fail-closed R-only AST capture and source-pair binding."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path as StdPath
import tempfile
import types
import unittest
from unittest.mock import patch

from importlib.util import module_from_spec, spec_from_file_location


HERE = StdPath(__file__).parent
SPEC = spec_from_file_location("a1_r10_r_only_source_pair_runner",
                               HERE / "a1-runner.py")
assert SPEC is not None and SPEC.loader is not None
RUNNER = module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


class _ConsoleAlias:
    """Map a test console to /workspace for the collector's path guard."""

    def __init__(self, actual: StdPath, display: str):
        self.actual = actual
        self.display = display

    def resolve(self):
        return self

    def is_file(self):
        return self.actual.is_file()

    def read_bytes(self):
        return self.actual.read_bytes()

    def __str__(self):
        return self.display


class _C4:
    def __init__(self, *, exit_code=1, log_text=None, emit_ast=True,
                 emit_log=True, classification="TERMINAL", bad_log_sha=False,
                 mutation=None, raise_stage=False):
        self.exit_code = exit_code
        self.log_text = log_text
        self.emit_ast = emit_ast
        self.emit_log = emit_log
        self.classification = classification
        self.bad_log_sha = bad_log_sha
        self.mutation = mutation
        self.raise_stage = raise_stage

    def clean_env(self, _a, _tool):
        return {}

    def stage(self, _a, root, _name, _command, _env, _timeout, *, cwd):
        if self.raise_stage:
            raise RuntimeError("synthetic stage exception")
        source = (cwd / "verified/lib.rs").read_text(encoding="utf-8")
        matches = [(n, line) for n, line in enumerate(source.splitlines(), 1)
                   if line.strip() == "fn small_sort_threshold() -> usize;"]
        assert len(matches) == 1
        line_number, line = matches[0]
        start = line.index("small_sort_threshold") + 1
        end = start + len("small_sort_threshold")
        expected = (f"verified/lib.rs({line_number},{start}-{end}): "
                    "error: Duplicate function prototype.\n")
        log_text = self.log_text
        if log_text is None:
            log_text = expected if self.exit_code == 1 else "synthetic verifier completed\n"
        log_bytes = log_text.encode("utf-8")
        if self.emit_ast:
            (root / "r-only-native-reference-ast.ml").write_text(
                "synthetic structural AST\n", encoding="utf-8")
        if self.emit_log:
            (root / "r-only-native-reference.log").write_bytes(log_bytes)
        if self.mutation:
            (cwd / self.mutation).write_text("changed during stage\n",
                                            encoding="utf-8")
        digest = hashlib.sha256(log_bytes).hexdigest()
        return {"exit": self.exit_code, "classification": self.classification,
                "log_sha256": "f" * 64 if self.bad_log_sha else digest,
                "proof_verdict": None}


class _AstGates:
    def small_sort_native_baseline(self, _text, _inventory, *, source_pair_id,
                                   reference_receipt, reference_source_text):
        return {"schema": "a1-small-sort-native-baseline-v1",
                "provenance": "r-only-native-translation",
                "source_pair_id": source_pair_id,
                "actual_source_pair_sha256":
                    reference_receipt["actual_source_pair_sha256"],
                "reference_receipt": dict(reference_receipt),
                "proof_credit": False, "conformance_credit": False}


class ROnlySourcePairTests(unittest.TestCase):
    def _run(self, *, mutation=None, emit_ast=True, emit_log=True,
             exit_code=1, log_text=None, classification="TERMINAL",
             bad_log_sha=False, raise_stage=False, stale_root=False):
        with tempfile.TemporaryDirectory() as temp:
            base = StdPath(temp)
            fixture = base / "fixtures" / "P1"
            (fixture / "verified").mkdir(parents=True)
            (fixture / "original").mkdir(parents=True)
            (fixture / "verified/lib.rs").write_text(
                "trait StableSmallSortTypeImpl {\n"
                "    fn small_sort_threshold() -> usize;\n}\n",
                encoding="utf-8")
            (fixture / "original/lib.rs").write_text("original input\n",
                                                       encoding="utf-8")
            console_file = base / "console"
            console_file.write_bytes(b"synthetic console")
            visible_console = "/workspace/synthetic-r10/console"
            console_alias = _ConsoleAlias(console_file, visible_console)
            real_path = RUNNER.Path

            def path_factory(value):
                if isinstance(value, _ConsoleAlias):
                    return value
                if str(value) == visible_console:
                    return console_alias
                return real_path(value)

            identity = {
                "translator": "a" * 64,
                "schema": "b" * 64,
                "exporter": "c" * 64,
            }
            profile = {"r_patch_sha256": "d" * 64,
                       "r_after": {
                           "src/rust_frontend/vf_mir_translator/vf_mir_translator.ml": identity["translator"],
                           "src/rust_frontend/vf_mir/vf_mir.capnp": identity["schema"],
                           "src/rust_frontend/vf_mir_exporter/src/lib.rs": identity["exporter"],
                       }}
            receipt = {
                "native_reference": {
                    "kind": "separately-built-R-only-native-reference",
                    "proof_credit": False,
                    "build_id": "synthetic-build",
                    "build_exit": 0,
                    "c_patch_applied": False,
                    "r_patch_sha256": profile["r_patch_sha256"],
                    "translator_sha256": identity["translator"],
                    "schema_sha256": identity["schema"],
                    "exporter_source_sha256": identity["exporter"],
                    "console_path": visible_console,
                    "console_binary_sha256": hashlib.sha256(
                        console_file.read_bytes()).hexdigest(),
                    "exporter_binary_sha256": "e" * 64,
                },
                "final_schema_sha256": identity["schema"],
                "exporter_binary_sha256": "e" * 64,
            }
            source_pair = {
                "verified": RUNNER._sha(fixture / "verified/lib.rs"),
                "original": RUNNER._sha(fixture / "original/lib.rs"),
            }
            p1_raw = {"case_id": "P1", "focus_stage": "interface",
                      "paired_support": {"paired_support_passed": True},
                      "source_pair_sha256": source_pair}
            p1_structure = {"inventory": {"case_binding": {
                "source_pair_id": "synthetic-source-pair"}}}
            args = types.SimpleNamespace(
                evidence=str(base / "evidence"),
                deadline_epoch=9_999_999_999)
            if stale_root:
                (base / "evidence/a1-native-reference/P1").mkdir(parents=True)
            helpers = {"a1-ast-gates.py": _AstGates()}
            with patch.dict(os.environ, {"CLOUD_BUILD_ID": "synthetic-build",
                                         "SORT4_A1_PROFILE_SHA256": "f" * 64}), \
                 patch.object(RUNNER, "Path", path_factory):
                return RUNNER.collect_native_reference_baseline(
                    args, _C4(mutation=mutation, emit_ast=emit_ast,
                              emit_log=emit_log, exit_code=exit_code,
                              log_text=log_text, classification=classification,
                              bad_log_sha=bad_log_sha, raise_stage=raise_stage),
                    tool=base / "tool", tool_receipt=receipt,
                    profile=profile, fixture=fixture, p1_raw=p1_raw,
                    p1_structure=p1_structure, helpers=helpers)

    def test_zero_exit_and_exact_source_anchored_expected_error_are_structural_only(self):
        success = self._run(exit_code=0)
        self.assertEqual(success["classification"],
                         "R_ONLY_NATIVE_INTERFACE_BASELINE_OBSERVED")
        self.assertEqual(success["baseline"]["reference_receipt"]["capture_status"],
                         "COMPLETE_NO_ERROR_EXIT0")
        expected_error = self._run(exit_code=1)
        receipt = expected_error["baseline"]["reference_receipt"]
        self.assertEqual(receipt["observed_exit"], 1)
        self.assertEqual(receipt["capture_status"],
                         "COMPLETE_EXPECTED_DUPLICATE_PROTOTYPE_EXIT1")
        self.assertEqual(receipt["diagnostic"]["line"], 2)
        self.assertFalse(expected_error["proof_credit"])
        self.assertFalse(expected_error["baseline"]["conformance_credit"])

    def test_only_unique_source_anchored_expected_error_is_accepted_for_exit_one(self):
        for log in (
            "unrelated verifier error\n",
            "verified/lib.rs(1,1-2): error: Duplicate function prototype.\n",
            "verified/lib.rs(2,8-28): error: Duplicate function prototype.\n"
            "verified/lib.rs(2,8-28): error: Duplicate function prototype.\n",
            "verified/lib.rs(2,8-28): error: Other verifier failure.\n",
        ):
            with self.subTest(log=log), self.assertRaisesRegex(
                    RuntimeError, "source-anchored duplicate-prototype"):
                self._run(exit_code=1, log_text=log)

    def test_nonadmitted_exit_types_and_nonterminal_stages_fail_closed(self):
        for exit_code in (124, None, True, "1", 2):
            with self.subTest(exit_code=exit_code), self.assertRaisesRegex(
                    RuntimeError, "terminal integer|not an admitted"):
                self._run(exit_code=exit_code)
        with self.assertRaisesRegex(RuntimeError, "terminal integer"):
            self._run(exit_code=1, classification="RUNNING")

    def test_exit_zero_with_error_diagnostic_is_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "exit 0 contains an error"):
            self._run(exit_code=0,
                      log_text="verified/lib.rs(2,8-28): error: Duplicate function prototype.\n")

    def test_stage_log_is_required_and_hash_verified(self):
        with self.assertRaisesRegex(RuntimeError, "stage log missing"):
            self._run(emit_log=False)
        with self.assertRaisesRegex(RuntimeError, "stage log missing or changed"):
            self._run(bad_log_sha=True)

    def test_stage_exception_missing_ast_stale_root_and_source_mutation_fail(self):
        with self.assertRaisesRegex(RuntimeError, "synthetic stage exception"):
            self._run(raise_stage=True)
        with self.assertRaisesRegex(RuntimeError, "did not emit its pre-verification AST"):
            self._run(emit_ast=False)
        with self.assertRaisesRegex(RuntimeError, "fresh R-only baseline destination"):
            self._run(stale_root=True)
        for path in ("verified/lib.rs", "original/lib.rs"):
            with self.subTest(path=path), self.assertRaisesRegex(
                    RuntimeError, "changed P1 source pair"):
                self._run(mutation=path)


if __name__ == "__main__":
    unittest.main()
