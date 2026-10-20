#!/usr/bin/env python3
"""Isolated tests for the R10 runner adapter; never load the real runner core."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
ADAPTER_PATH = HERE / "a1-runner-r10.py"
PHASE = "SORT4-A1-CHECKED-TRAIT-CONTRACT-CLOUD-2026-10-17"
AUTHORIZATION_PHASE = "SORT4-DELIVERABLE-NATIVE-PROOF-2026-10-20-R10"

STUB_CORE = b'''PHASE = "SORT4-A1-CHECKED-TRAIT-CONTRACT-CLOUD-2026-10-17"
AUTHORIZATION_PHASE = "OLD-R6-PHASE"
PROFILE = "old-profile.json"

def run(a, *, c4, audit, driver, manifest, ghost):
    result = getattr(a, "core_result", {
        "phase": PHASE,
        "authorization_phase": AUTHORIZATION_PHASE,
        "profile": str(PROFILE),
    })
    return {
        "phase": PHASE,
        "authorization_phase": AUTHORIZATION_PHASE,
        "profile": str(PROFILE),
        "result": result,
        "args": (a, c4, audit, driver, manifest, ghost),
    }
'''


def load_adapter():
    spec = importlib.util.spec_from_file_location("isolated_a1_runner_r10", ADAPTER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load R10 adapter")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class R10ActivationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="a1-r10-activation-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.adapter = load_adapter()
        self.profile_path = self.root / self.adapter.PROFILE
        self.core_path = self.root / self.adapter.HERE / "a1-runner.py"
        self.profile_path.parent.mkdir(parents=True)
        self.core_path.parent.mkdir(parents=True, exist_ok=True)
        self.core_path.write_bytes(STUB_CORE)
        self.profile = {
            "authorization_phase_id": AUTHORIZATION_PHASE,
            "experiment_protocol_phase_id": PHASE,
            "a1_source_runner_sha256": hashlib.sha256(STUB_CORE).hexdigest(),
        }
        self.write_profile()
        self.env = {"SORT4_A1_PROFILE_SHA256": self.sha(self.profile_path)}
        self.args = SimpleNamespace(proof_root=self.root)
        self.passthrough = {
            "c4": object(), "audit": object(), "driver": object(),
            "manifest": {"case": "fixture"}, "ghost": object(),
        }

    @staticmethod
    def sha(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def write_profile(self):
        self.profile_path.write_text(json.dumps(self.profile, sort_keys=True) + "\n")

    def call_adapter(self):
        with patch.dict(os.environ, self.env, clear=True):
            return self.adapter.run(self.args, **self.passthrough)

    def test_delegates_to_hash_pinned_core_with_only_r10_bindings(self):
        result = self.call_adapter()
        self.assertEqual(result["phase"], PHASE)
        self.assertEqual(result["authorization_phase"], AUTHORIZATION_PHASE)
        self.assertEqual(result["profile"], str(self.adapter.PROFILE))
        expected = (self.args, *self.passthrough.values())
        self.assertEqual(len(result["args"]), len(expected))
        for actual, value in zip(result["args"], expected):
            self.assertIs(actual, value)

    def test_preserves_success_error_not_run_and_partial_core_observations(self):
        results = (
            {"status": "PASS", "stage": "proof"},
            {"status": "ERROR", "error": "synthetic service failure"},
            {"status": "NOT_RUN", "reason": "synthetic setup failure"},
            {"status": "PARTIAL", "completed": ["compile"],
             "pending": ["extract", "verify"]},
            {"status": "ERROR", "artifact": {"path": None}},
        )
        for result in results:
            with self.subTest(result=result):
                self.args.core_result = result
                self.assertEqual(self.call_adapter()["result"], result)

    def test_rejects_null_or_wrong_type_profile(self):
        for raw in (b"null\n", b"[]\n", b"\"profile\"\n"):
            with self.subTest(raw=raw):
                self.profile_path.write_bytes(raw)
                self.env["SORT4_A1_PROFILE_SHA256"] = self.sha(self.profile_path)
                with self.assertRaisesRegex(RuntimeError, "profile must be an object"):
                    self.call_adapter()
                self.write_profile()
                self.env["SORT4_A1_PROFILE_SHA256"] = self.sha(self.profile_path)

    def test_rejects_bad_or_missing_profile_sha(self):
        for value in (None, "", "0" * 64, "not-a-sha"):
            with self.subTest(profile_sha=value):
                if value is None:
                    self.env.pop("SORT4_A1_PROFILE_SHA256", None)
                else:
                    self.env["SORT4_A1_PROFILE_SHA256"] = value
                with self.assertRaisesRegex(RuntimeError, "profile pin differs"):
                    self.call_adapter()

    def test_rejects_missing_profile_file(self):
        self.profile_path.unlink()
        with self.assertRaisesRegex(RuntimeError, "profile pin differs"):
            self.call_adapter()

    def test_rejects_wrong_missing_or_null_authorization_metadata(self):
        for value in (None, "", "SORT4-PACKAGE-SCOPE-NATIVE-PROOF-2026-10-20-R6"):
            with self.subTest(authorization=value):
                self.profile["authorization_phase_id"] = value
                self.write_profile()
                self.env["SORT4_A1_PROFILE_SHA256"] = self.sha(self.profile_path)
                with self.assertRaisesRegex(RuntimeError, "authorization/protocol binding differs"):
                    self.call_adapter()
        self.profile.pop("authorization_phase_id")
        self.write_profile()
        self.env["SORT4_A1_PROFILE_SHA256"] = self.sha(self.profile_path)
        with self.assertRaisesRegex(RuntimeError, "authorization/protocol binding differs"):
            self.call_adapter()

    def test_rejects_wrong_missing_or_null_protocol_metadata(self):
        for value in (None, "", "SORT4-OTHER-PHASE"):
            with self.subTest(protocol=value):
                self.profile["experiment_protocol_phase_id"] = value
                self.write_profile()
                self.env["SORT4_A1_PROFILE_SHA256"] = self.sha(self.profile_path)
                with self.assertRaisesRegex(RuntimeError, "authorization/protocol binding differs"):
                    self.call_adapter()
        self.profile.pop("experiment_protocol_phase_id")
        self.write_profile()
        self.env["SORT4_A1_PROFILE_SHA256"] = self.sha(self.profile_path)
        with self.assertRaisesRegex(RuntimeError, "authorization/protocol binding differs"):
            self.call_adapter()

    def test_rejects_missing_null_or_corrupt_core_hash(self):
        for value in (None, "", "0" * 64):
            with self.subTest(core_sha=value):
                self.profile["a1_source_runner_sha256"] = value
                self.write_profile()
                self.env["SORT4_A1_PROFILE_SHA256"] = self.sha(self.profile_path)
                with self.assertRaisesRegex(RuntimeError, "pinned S3 runner source differs"):
                    self.call_adapter()
        self.profile["a1_source_runner_sha256"] = hashlib.sha256(STUB_CORE).hexdigest()
        self.write_profile()
        self.env["SORT4_A1_PROFILE_SHA256"] = self.sha(self.profile_path)
        self.core_path.write_bytes(STUB_CORE + b"# altered after pin\n")
        with self.assertRaisesRegex(RuntimeError, "pinned S3 runner source differs"):
            self.call_adapter()


if __name__ == "__main__":
    unittest.main(verbosity=2)
