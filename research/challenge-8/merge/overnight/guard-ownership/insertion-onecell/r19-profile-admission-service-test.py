#!/usr/bin/env python3
"""Pure R19 profile-admission tests; no compiler, verifier, or hosted services."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
ORIGIN = HERE.parents[3] / "cloud-build/origin-layout"
R17_BASELINE_BYTES = (ORIGIN / "R17-BASELINE-PROFILE-20261021.json").read_bytes()
R19_BASELINE_BYTES = (ORIGIN / "R19-BASELINE-PROFILE-20261022.json").read_bytes()
PROFILE = json.loads((ORIGIN / "GLUE-PROFILE.json").read_text())


def load_prove():
    path = HERE / "prove.py"
    spec = importlib.util.spec_from_file_location("r19_prove_profile_test", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


prove = load_prove()


class R19ProfileAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.profile = copy.deepcopy(PROFILE)

    def admit(self, profile=None, r17=R17_BASELINE_BYTES, r19=R19_BASELINE_BYTES):
        return prove.admit_r17_profile_extension_if_present(
            self.profile if profile is None else profile, r17, r19)

    def test_selected_profile_is_the_exact_r19_extension(self):
        self.assertTrue(self.admit())

    def test_r19_baseline_alone_keeps_the_r17_route(self):
        baseline = json.loads(R19_BASELINE_BYTES)
        self.assertTrue(prove.admit_r17_profile_extension_if_present(baseline, R17_BASELINE_BYTES))

    def test_missing_r19_baseline_is_rejected(self):
        with self.assertRaises(ValueError):
            self.admit(r19=None)

    def test_missing_r17_baseline_is_rejected(self):
        with self.assertRaises(ValueError):
            self.admit(r17=None)

    def test_r19_baseline_hash_mismatch_is_rejected(self):
        with self.assertRaises(ValueError):
            self.admit(r19=R19_BASELINE_BYTES + b" ")

    def test_unknown_candidate_is_rejected(self):
        self.profile["r19_registration"]["candidate_tool_commit"] = "1" * 40
        with self.assertRaises(ValueError):
            self.admit()

    def test_effective_commit_mismatch_is_rejected(self):
        self.profile["effective_tool_commit"] = prove.R17_TOOL_COMMIT
        with self.assertRaises(ValueError):
            self.admit()

    def test_translator_hash_mismatch_is_rejected(self):
        self.profile["translator_sha256"] = "3" * 64
        with self.assertRaises(ValueError):
            self.admit()

    def test_unregistered_field_change_is_rejected(self):
        self.profile["kernel_sha256"] = "4" * 64
        with self.assertRaises(ValueError):
            self.admit()

    def test_refiner_change_is_rejected(self):
        self.profile["refiner_core_source_sha256"] = "5" * 64
        with self.assertRaises(ValueError):
            self.admit()

    def test_extra_top_level_field_is_rejected(self):
        self.profile["r20_registration"] = {}
        with self.assertRaises(ValueError):
            self.admit()

    def test_patch_chain_prefix_change_is_rejected(self):
        self.profile["ordered_patch_chain"][0]["sha256"] = "6" * 64
        with self.assertRaises(ValueError):
            self.admit()

    def test_final_patch_row_hash_mismatch_is_rejected(self):
        self.profile["ordered_patch_chain"][-1]["sha256"] = "7" * 64
        with self.assertRaises(ValueError):
            self.admit()

    def test_partial_registration_is_rejected(self):
        self.profile["r19_registration"].pop("tool_source_paths")
        with self.assertRaises(ValueError):
            self.admit()

    def test_wrong_registration_type_is_rejected(self):
        self.profile["r19_registration"] = "registered"
        with self.assertRaises(ValueError):
            self.admit()

    def test_patch_file_and_profile_pins_agree(self):
        patch = (ORIGIN / "r9-guard-return-trace.patch").read_bytes()
        self.assertEqual(prove.hashlib.sha256(patch).hexdigest(), prove.R19_PATCH_SHA256)
        self.assertEqual(self.profile["guard_return_trace_patch_sha256"], prove.R19_PATCH_SHA256)


if __name__ == "__main__":
    unittest.main()
