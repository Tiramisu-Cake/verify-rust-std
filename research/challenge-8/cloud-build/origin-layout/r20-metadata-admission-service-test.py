#!/usr/bin/env python3
"""Synthetic R20 metadata admission regressions; no compiler, verifier, or Cloud calls."""
from __future__ import annotations

import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TOOL = ROOT / "research/challenge-8/merge/overnight/guard-ownership/insertion-onecell/prove.py"
CALLBACK = HERE / "first-callback.py"
CONTROL = HERE.parent / "control.py"
PROFILE_PATH = HERE / "GLUE-PROFILE.json"
R17_BASELINE = (HERE / "R17-BASELINE-PROFILE-20261021.json").read_bytes()
PROFILE = json.loads(PROFILE_PATH.read_bytes())
sys.path.insert(0, str(CONTROL.parent))


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


prove = load("r20_profile_admission_prove", TOOL)
callback = load("r20_profile_admission_callback", CALLBACK)
control = load("r20_profile_admission_control", CONTROL)


def git_bytes(commit: str, path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=ROOT)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def provider_maps(data: bytes):
    tree = ast.parse(data)
    maps = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in ("FILES", "R11_FILES"):
                    maps[target.id] = ast.literal_eval(node.value)
    return maps


class R20MetadataAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.profile = copy.deepcopy(PROFILE)
        self.old_profile = prove.r20_r19_baseline_profile(self.profile)
        self.old_profile_bytes = (json.dumps(self.old_profile, indent=2) + "\n").encode()
        self.selected_profile_bytes = PROFILE_PATH.read_bytes()
        self.probe = control.R20_PROBE_SOURCE
        self.old_patch = git_bytes(self.probe, control.R17_PATCH_PATH)
        self.new_patch = (HERE / "r9-guard-return-trace.patch").read_bytes()
        self.old_provider = git_bytes(self.probe, control.R17_PROVIDER_OVERLAYS_PATH)
        self.new_provider = (ROOT / control.R17_PROVIDER_OVERLAYS_PATH).read_bytes()

    def test_r20_profile_reverts_exactly_to_r19_and_runs_unchanged_r19_validation(self):
        self.assertEqual(sha(self.old_profile_bytes), prove.R19_SELECTED_PROFILE_SHA256)
        self.assertTrue(prove.admit_r17_profile_extension_if_present(self.profile, R17_BASELINE))
        prove.validate_r20_profile_extension(self.profile, R17_BASELINE)
        prove.validate_r19_profile_extension(self.old_profile, R17_BASELINE)
        self.assertNotIn("r20_metadata_registration", self.old_profile)

    def test_profile_changes_only_registered_pins_and_registration(self):
        for key in ("effective_tool_commit", "refiner_core_source_sha256", "exporter_source_sha256",
                    "schema_sha256", "guard_return_trace_patch_sha256"):
            bad = copy.deepcopy(self.profile)
            bad[key] = "0" * (40 if key == "effective_tool_commit" else 64)
            with self.subTest(key=key), self.assertRaises(ValueError):
                prove.validate_r20_profile_extension(bad, R17_BASELINE)
        bad = copy.deepcopy(self.profile)
        bad["r20_metadata_registration"]["candidate_tool_commit"] = "0" * 40
        with self.assertRaises(ValueError):
            prove.validate_r20_profile_extension(bad, R17_BASELINE)
        bad = copy.deepcopy(self.profile)
        bad["kernel_sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            prove.validate_r20_profile_extension(bad, R17_BASELINE)

    def test_callback_accepts_legacy_r19_and_exact_r20_registration_only(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "profile.json"
            path.write_bytes(self.old_profile_bytes)
            self.assertTrue(callback._r19_registration_matches(path, callback.R11_PROFILE))
            old_receipt = {"profile": callback.R11_PROFILE}
            self.assertTrue(callback._r17_registration_matches(path, callback.R11_PROFILE, old_receipt))
            path.write_bytes(self.selected_profile_bytes)
            self.assertTrue(callback._r19_registration_matches(path, callback.R11_PROFILE))
            self.assertTrue(callback._r17_registration_matches(path, callback.R11_PROFILE, old_receipt))
            bad = copy.deepcopy(self.profile)
            bad["schema_sha256"] = "1" * 64
            path.write_text(json.dumps(bad, indent=2) + "\n")
            self.assertFalse(callback._r19_registration_matches(path, callback.R11_PROFILE))

    def test_provider_changes_only_the_exact_onecell_prove_pin(self):
        old = provider_maps(self.old_provider)
        new = provider_maps(self.new_provider)
        target = "research/challenge-8/merge/overnight/guard-ownership/insertion-onecell/prove.py"
        self.assertEqual(old["FILES"], new["FILES"])
        self.assertEqual(set(old["R11_FILES"]), set(new["R11_FILES"]))
        self.assertEqual({key for key in old["R11_FILES"] if old["R11_FILES"][key] != new["R11_FILES"][key]}, {target})
        self.assertEqual(new["R11_FILES"][target], sha(TOOL.read_bytes()))
        self.assertEqual(new["R11_FILES"][target], control.R20_METADATA_PROVIDER_PROVE_SHA256)

    def test_candidate_pin_gate_accepts_only_exact_r19_or_r20_tuple(self):
        self.assertFalse(control.r20_validate_candidate_pins(
            self.old_profile_bytes, self.old_profile_bytes, self.old_profile_bytes,
            self.old_patch, self.old_provider, self.old_provider, self.old_provider))
        self.assertTrue(control.r20_validate_candidate_pins(
            self.old_profile_bytes, self.selected_profile_bytes, self.selected_profile_bytes,
            self.new_patch, self.old_provider, self.new_provider, self.new_provider))
        with self.assertRaises(SystemExit):
            control.r20_validate_candidate_pins(
                self.old_profile_bytes, self.selected_profile_bytes, self.selected_profile_bytes,
                self.new_patch, self.old_provider, self.old_provider, self.old_provider)
        with self.assertRaises(SystemExit):
            control.r20_validate_candidate_pins(
                self.old_profile_bytes, self.selected_profile_bytes, self.selected_profile_bytes,
                self.old_patch, self.old_provider, self.new_provider, self.new_provider)

    def test_historical_closure_allows_only_checked_profile_extension(self):
        paths = {control.R19_LEDGER_PATH, control.R18_LEDGER_PATH, control.R17_LEDGER_PATH,
                 control.R16_LEDGER_PATH, control.R13_MODE_PATH, control.R14_GATE_PATH,
                 control.R17_PROFILE_PATH, control.R20_PROFILE_PATH}
        before = {path: ("100644", "blob", "a" * 40) for path in paths}
        unchanged = dict(before)
        control.r20_validate_historical_closure(paths, before, unchanged, False)
        changed_profile = dict(before)
        changed_profile[control.R20_PROFILE_PATH] = ("100644", "blob", "b" * 40)
        control.r20_validate_historical_closure(paths, before, changed_profile, True)
        changed_ledger = dict(changed_profile)
        changed_ledger[control.R19_LEDGER_PATH] = ("100644", "blob", "c" * 40)
        with self.assertRaises(SystemExit):
            control.r20_validate_historical_closure(paths, before, changed_ledger, True)
        with self.assertRaises(SystemExit):
            control.r20_validate_historical_closure(paths, before, changed_profile, False)

    def test_recipe_delta_has_only_registration_and_unused_service_test_pruning(self):
        before = json.loads(git_bytes(self.probe, "research/challenge-8/cloud-build/recipes/merge.json"))
        selected = json.loads(git_bytes(control.R21_PROBE_SOURCE, "research/challenge-8/cloud-build/recipes/merge.json"))
        control.r20_validate_recipe_delta(before, selected)
        bad = copy.deepcopy(selected)
        bad["proof_paths"].append("research/challenge-8/cloud-build/origin-layout/R11-INPUTS-20261021.json")
        bad["proof_paths"].sort()
        with self.assertRaises(SystemExit):
            control.r20_validate_recipe_delta(before, bad)


if __name__ == "__main__":
    unittest.main()
