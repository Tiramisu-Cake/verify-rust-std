"""Isolated tests for exact same-Build paired-support reuse identity."""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

PATH = Path(__file__).with_name("a1-runner.py")
SPEC = importlib.util.spec_from_file_location("a1_runner_lifecycle_test", PATH)
assert SPEC is not None and SPEC.loader is not None
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)
FOCUS_PATH = PATH.with_name("a1-focus-backend.py")
FOCUS_SPEC = importlib.util.spec_from_file_location("a1_focus_cache_test", FOCUS_PATH)
assert FOCUS_SPEC is not None and FOCUS_SPEC.loader is not None
FOCUS = importlib.util.module_from_spec(FOCUS_SPEC)
FOCUS_SPEC.loader.exec_module(FOCUS)


class PairedSupportReuseIdentity(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.fixture = self.root / "fixture"
        self.fixture.mkdir()
        (self.fixture / "verified/lib.rs").parent.mkdir(parents=True)
        (self.fixture / "original").mkdir()
        (self.fixture / "verified/lib.rs").write_bytes(b"verified source")
        (self.fixture / "original/lib.rs").write_bytes(b"original source")
        self.tool = self.root / "tool"
        for relative in (
                "bin/verifast", "bin/vf-rust-mir-exporter",
                "bin/refinement-checker", "src/rust_frontend/vf_mir/vf_mir.capnp"):
            path = self.tool / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(relative.encode("ascii"))
        self.args = type("Args", (), {"compiler_sysroot": self.root / "sysroot"})()
        self.env = {"SORT4_A1_STAGE": "bodies",
                    "SORT4_A1_PHASE_ID": RUNNER.PHASE,
                    "SORT4_A1_CHECKED_TRAIT_CONTRACT": "1",
                    "SORT4_A1_PROFILE_SHA256": "a" * 64}
        self.receipt = {
            "final_translator_sha256": "b" * 64,
            "final_schema_sha256": "c" * 64,
            "final_exporter_sha256": "d" * 64,
            "console_binary_sha256": "e" * 64,
            "exporter_binary_sha256": "f" * 64,
        }
        self.cloud_env = patch.dict(os.environ, {
            "CLOUD_BUILD_ID": "11111111-1111-4111-8111-111111111111",
            "RUSTUP_TOOLCHAIN": "nightly-2026-09-25",
            "CARGO_BUILD_TARGET": "x86_64-unknown-linux-gnu",
        })
        self.cloud_env.start()

    def tearDown(self):
        self.cloud_env.stop()
        self.tmp.cleanup()

    def key(self):
        return FOCUS._support_cache_key(
            self.args, self.tool, self.fixture, self.env, self.receipt)

    def test_identical_pair_tool_build_and_config_reuse_same_key(self):
        first = self.key()
        self.assertEqual(first, self.key())

    def test_source_or_stage_mutation_invalidates_cache_key(self):
        first = self.key()
        (self.fixture / "verified/lib.rs").write_bytes(b"changed verified source")
        self.assertNotEqual(first, self.key())
        (self.fixture / "verified/lib.rs").write_bytes(b"verified source")
        self.env["SORT4_A1_STAGE"] = "caller"
        self.assertNotEqual(first, self.key())

    def test_tool_or_build_mutation_invalidates_cache_key(self):
        first = self.key()
        (self.tool / "bin/verifast").write_bytes(b"changed console")
        self.assertNotEqual(first, self.key())
        (self.tool / "bin/verifast").write_bytes(b"bin/verifast")
        os.environ["CLOUD_BUILD_ID"] = "22222222-2222-4222-8222-222222222222"
        self.assertNotEqual(first, self.key())

    def test_remembered_pair_can_be_reused_after_identity_validation(self):
        names = ("normal-mir.bin", "normal-mir.txt", "readonly-mir.bin",
                 "readonly-mir.txt", "normal-a1_guard_observer-full-mir.txt",
                 "readonly-a1_guard_observer-full-mir.txt")
        source_root = self.root / "source-support"
        source_root.mkdir()
        for name in names:
            (source_root / name).write_bytes(("artifact:" + name).encode())
        source_pair = {"verified/lib.rs": RUNNER._sha(self.fixture / "verified/lib.rs"),
                       "original/lib.rs": RUNNER._sha(self.fixture / "original/lib.rs")}
        stages = {name: {"exit": 0, "log_sha256": "a" * 64} for name in
                  ("normal-export", "normal-decode", "readonly-export",
                   "readonly-decode", "refinement")}
        support = {"paired_support_passed": True, "proof_credit": False}
        cache = {}
        key = self.key()
        FOCUS._remember_support(self.args, source_root, source_pair, stages,
                                support, cache, key)
        target = self.root / "target-support"
        reused = FOCUS._cached_support(
            self.args, target, self.fixture, key=key, support_cache=cache)
        self.assertIsNotNone(reused)
        copied_stages, copied_support = reused
        self.assertTrue(copied_support["same_build_identity_validated"])
        self.assertTrue(all(row["reused_support"] for row in copied_stages.values()))
        self.assertEqual(set(path.name for path in target.iterdir()), set(names))


if __name__ == "__main__":
    unittest.main()
