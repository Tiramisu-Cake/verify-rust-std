"""Isolated R10 controls for the native reference source-pair gate."""
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
    def __init__(self, *, mutation=None, emit_ast=True):
        self.mutation = mutation
        self.emit_ast = emit_ast

    def clean_env(self, _a, _tool):
        return {}

    def stage(self, _a, root, _name, _command, _env, _timeout, *, cwd):
        if self.emit_ast:
            (root / "r-only-native-reference-ast.ml").write_text(
                "synthetic structural AST\n", encoding="utf-8")
        if self.mutation:
            (cwd / self.mutation).write_text("changed during stage\n",
                                            encoding="utf-8")
        # Nonzero is retained as an observation; it does not erase the AST.
        return {"exit": 1, "proof_credit": False}


class _AstGates:
    def small_sort_native_baseline(self, _text, _inventory, *, source_pair_id,
                                   reference_receipt):
        return {"schema": "a1-small-sort-native-baseline-v1",
                "provenance": "r-only-native-translation",
                "source_pair_id": source_pair_id,
                "actual_source_pair_sha256":
                    reference_receipt["actual_source_pair_sha256"],
                "proof_credit": False, "conformance_credit": False}


class ROnlySourcePairTests(unittest.TestCase):
    def _run(self, *, mutation=None, emit_ast=True):
        with tempfile.TemporaryDirectory() as temp:
            base = StdPath(temp)
            fixture = base / "fixtures" / "P1"
            (fixture / "verified").mkdir(parents=True)
            (fixture / "original").mkdir(parents=True)
            (fixture / "verified/lib.rs").write_text("verified input\n",
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
            helpers = {"a1-ast-gates.py": _AstGates()}
            with patch.dict(os.environ, {"CLOUD_BUILD_ID": "synthetic-build",
                                         "SORT4_A1_PROFILE_SHA256": "f" * 64}), \
                 patch.object(RUNNER, "Path", path_factory):
                return RUNNER.collect_native_reference_baseline(
                    args, _C4(mutation=mutation, emit_ast=emit_ast),
                    tool=base / "tool", tool_receipt=receipt,
                    profile=profile, fixture=fixture, p1_raw=p1_raw,
                    p1_structure=p1_structure, helpers=helpers)

    def test_unchanged_pair_and_ast_pass_even_when_stage_exit_is_nonzero(self):
        observation = self._run()
        self.assertEqual(observation["classification"],
                         "R_ONLY_NATIVE_INTERFACE_BASELINE_OBSERVED")
        self.assertEqual(observation["raw"]["stage"]["exit"], 1)
        self.assertEqual(set(observation["raw"]["source_pair_sha256"]),
                         {"verified", "original"})
        self.assertFalse(observation["proof_credit"])
        self.assertFalse(observation["baseline"]["conformance_credit"])

    def test_each_changed_source_file_fails_the_pair_gate(self):
        for path in ("verified/lib.rs", "original/lib.rs"):
            with self.subTest(path=path), self.assertRaisesRegex(
                    RuntimeError, "changed P1 source pair"):
                self._run(mutation=path)

    def test_missing_ast_has_a_distinct_fail_closed_error(self):
        with self.assertRaisesRegex(RuntimeError, "did not emit its pre-verification AST"):
            self._run(emit_ast=False)


if __name__ == "__main__":
    unittest.main()
