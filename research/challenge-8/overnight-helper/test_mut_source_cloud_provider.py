"""Synthetic controls for Cloud-only mutable source preparation gate."""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "mut_source_cloud_provider_test", HERE / "mut_source_cloud_provider.py")
GATE = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = GATE
spec.loader.exec_module(GATE)
CLOUD_ENV = {
    "SMALLSORT_EXECUTION_PROVIDER": "cloud-build",
    "CLOUD_BUILD_ID": "12345678-1234-4234-8234-123456789abc",
    "CLOUD_BUILD_PROJECT_ID": "smallsort-ci",
    "CLOUD_BUILD_REGION": "global",
}
IDENTITY = {
    "provider": "cloud-build", "build_id": "12345678-1234-4234-8234-123456789abc",
    "project": "smallsort-ci", "region": "global",
    "os": "ubuntu-22.04", "arch": "x86_64",
}


class MutableCloudProviderGate(unittest.TestCase):
    def test_missing_provider_record_refused(self):
        with self.assertRaisesRegex(RuntimeError, "identified Cloud Build"):
            GATE.validate_provider_record({}, CLOUD_ENV)

    def test_wrong_provider_record_refused(self):
        with self.assertRaisesRegex(RuntimeError, "identified Cloud Build"):
            GATE.validate_provider_record(dict(IDENTITY, provider="github-hosted"), CLOUD_ENV)

    def test_github_identity_refused_even_with_cloud_shaped_record(self):
        with self.assertRaisesRegex(RuntimeError, "GitHub identity is forbidden"):
            GATE.validate_provider_record(IDENTITY, {"GITHUB_ACTIONS": "true"})

    def test_valid_cloud_identity_accepted(self):
        self.assertEqual(GATE.validate_provider_record(IDENTITY, CLOUD_ENV), IDENTITY)

    def test_runtime_gate_uses_pinned_provider_module_with_mock_record(self):
        env = dict(CLOUD_ENV)
        self.assertEqual(GATE.require_cloud_provider(
            env, provider_loader=lambda: dict(IDENTITY)), IDENTITY)
        with self.assertRaisesRegex(RuntimeError, "GitHub identity is forbidden"):
            GATE.require_cloud_provider(
                dict(env, GITHUB_ACTIONS="true"),
                provider_loader=lambda: dict(IDENTITY))
        with self.assertRaisesRegex(RuntimeError, "environment identity is missing"):
            GATE.require_cloud_provider({}, provider_loader=lambda: dict(IDENTITY))

    def test_runtime_gate_rejects_missing_cloud_build_id(self):
        env = dict(CLOUD_ENV)
        env.pop("CLOUD_BUILD_ID")
        with self.assertRaisesRegex(RuntimeError, "environment identity is missing"):
            GATE.require_cloud_provider(env, provider_loader=lambda: dict(IDENTITY))


if __name__ == "__main__":
    unittest.main()
