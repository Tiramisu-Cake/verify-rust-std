#!/usr/bin/env python3
"""Pure profile-admission tests; no compiler, verifier, or hosted services."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
ORIGIN = HERE.parents[3] / "cloud-build/origin-layout"
BASELINE_BYTES = (ORIGIN / "R17-BASELINE-PROFILE-20261021.json").read_bytes()
PROFILE = json.loads((ORIGIN / "GLUE-PROFILE.json").read_text())


def load_prove():
    path = HERE / "prove.py"
    spec = importlib.util.spec_from_file_location("r17_prove_profile_test", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


prove = load_prove()


class R17ProfileAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.profile = copy.deepcopy(PROFILE)

    def test_legacy_profile_keeps_the_r11_route(self):
        legacy = copy.deepcopy(self.profile)
        legacy.pop("r17_registration")
        self.assertFalse(prove.admit_r17_profile_extension_if_present(legacy, None))

    def test_exact_registered_r17_extension_is_admitted(self):
        self.assertTrue(prove.admit_r17_profile_extension_if_present(
            self.profile, BASELINE_BYTES))

    def test_unknown_candidate_is_rejected(self):
        self.profile["r17_registration"]["candidate_tool_commit"] = "1" * 40
        with self.assertRaises(ValueError):
            prove.admit_r17_profile_extension_if_present(self.profile, BASELINE_BYTES)

    def test_mutated_registration_key_is_rejected(self):
        self.profile["r17_registration"]["phase_id"] = "wrong-phase"
        with self.assertRaises(ValueError):
            prove.admit_r17_profile_extension_if_present(self.profile, BASELINE_BYTES)

    def test_unregistered_profile_field_mutation_is_rejected(self):
        self.profile["accepted"] = True
        with self.assertRaises(ValueError):
            prove.admit_r17_profile_extension_if_present(self.profile, BASELINE_BYTES)

    def test_missing_baseline_is_rejected(self):
        with self.assertRaises(ValueError):
            prove.admit_r17_profile_extension_if_present(self.profile, None)

    def test_malformed_baseline_type_is_rejected(self):
        with self.assertRaises(ValueError):
            prove.admit_r17_profile_extension_if_present(self.profile, {"bad": "type"})

    def test_partial_registration_is_rejected(self):
        self.profile["r17_registration"].pop("source_applicability")
        with self.assertRaises(ValueError):
            prove.admit_r17_profile_extension_if_present(self.profile, BASELINE_BYTES)

    def test_patch_hash_mismatch_is_rejected(self):
        self.profile["guard_return_trace_patch_sha256"] = "2" * 64
        with self.assertRaises(ValueError):
            prove.admit_r17_profile_extension_if_present(self.profile, BASELINE_BYTES)

    def test_baseline_bytes_hash_mismatch_is_rejected(self):
        with self.assertRaises(ValueError):
            prove.admit_r17_profile_extension_if_present(self.profile, BASELINE_BYTES + b" ")


if __name__ == "__main__":
    unittest.main()
