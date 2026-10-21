#!/usr/bin/env python3
"""Synthetic R11 profile/source applicability, alias and recipe closure checks."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PROFILE_NAME = "experimental-merge-label-storage-r11-v1"
TOOL_COMMIT = "bb557d43c4196694c7af50ff2150ce56a269e17d"
PHASE_ID = "MERGE-LABEL-STORAGE-INVARIANT-R11-2026-10-21"
BASELINE_PATH = HERE / "R11-BASELINE-PROFILE-20261021.json"
BASELINE_SHA = "c3f5d286777ffd388e1eb0894ad0ff9e8f1f87f72424291041cb800385f7c979"
CANDIDATE_TOOL_COMMIT = "a3a22f98e0e48f25af6741f3291c31a6d96e5119"


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"missing module {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


preflight = load("r11_source_preflight", HERE / "r11-source-preflight.py")


class R11RegistrationTests(unittest.TestCase):
    def setUp(self):
        self.baseline_raw = BASELINE_PATH.read_bytes()
        self.baseline = json.loads(self.baseline_raw)
        self.profile = copy.deepcopy(self.baseline)
        self.profile["profile"] = PROFILE_NAME
        self.profile["previous_profile_sha256"] = BASELINE_SHA
        candidate = CANDIDATE_TOOL_COMMIT
        self.profile["effective_tool_commit"] = candidate
        self.profile["guard_return_trace_tool_commit"] = candidate
        self.profile["translator_sha256"] = "b" * 64
        self.profile["kernel_sha256"] = "c" * 64
        self.profile["guard_return_trace_patch_sha256"] = "d" * 64
        self.profile["ordered_patch_chain"][-1]["sha256"] = "d" * 64
        self.profile["r11_registration"] = {
            "schema": "merge-r11-profile-registration-v1",
            "phase_id": PHASE_ID,
            "baseline_profile_path": "research/challenge-8/cloud-build/origin-layout/R11-BASELINE-PROFILE-20261021.json",
            "baseline_profile_sha256": BASELINE_SHA,
            "starting_tool_commit": TOOL_COMMIT,
            "candidate_tool_commit": candidate,
            "tool_source_paths": ["src/rust_frontend/vf_mir_translator/vf_mir_translator.ml", "src/verifast.ml"],
            "source_applicability": "label-storage-invariant annotation temporary; exact body/local/Live/ghost-call/Dead and label-invariant binding; unchanged R10 resource model",
        }

    def test_immutable_r10_baseline_and_new_unqualified_profile_identity(self):
        self.assertEqual(hashlib.sha256(self.baseline_raw).hexdigest(), BASELINE_SHA)
        self.assertEqual(self.baseline["profile"], "experimental-merge-moving-gap-r10-v1")
        self.assertFalse(self.baseline["accepted"])
        self.assertEqual(self.baseline["effective_tool_commit"], TOOL_COMMIT)
        preflight.validate_profile(self.profile, self.baseline, BASELINE_SHA,
                                   self.profile["effective_tool_commit"])

    def test_profile_source_tool_and_registration_mismatches_fail_closed(self):
        mutants = (
            ("profile", "experimental-merge-moving-gap-r10-v1"),
            ("accepted", True),
            ("qualification", "QUALIFIED"),
            ("previous_profile_sha256", "0" * 64),
            ("effective_tool_commit", "1" * 40),
            ("ordered_patch_chain", []),
            ("kernel_sha256", "2" * 64),
        )
        for key, value in mutants:
            bad = copy.deepcopy(self.profile)
            bad[key] = value
            with self.subTest(field=key), self.assertRaises(ValueError):
                preflight.validate_profile(bad, self.baseline, BASELINE_SHA, TOOL_COMMIT)
        bad_registration = copy.deepcopy(self.profile)
        bad_registration["r11_registration"]["phase_id"] = "wrong"
        with self.assertRaises(ValueError):
            preflight.validate_profile(bad_registration, self.baseline, BASELINE_SHA,
                                       self.profile["effective_tool_commit"])
        with self.assertRaises(ValueError):
            preflight.validate_profile(self.profile, self.baseline, "0" * 64,
                                       self.profile["effective_tool_commit"])
        with self.assertRaises(ValueError):
            preflight.validate_profile(self.profile, self.baseline, BASELINE_SHA, "1" * 40)

    def test_r11_profile_aliases_reach_existing_external_consumers(self):
        modules = (
            ("r5-addressability-controls.py", "SUPPORTED_PROFILES"),
            ("r7-late-admission-controls.py", "SUPPORTED_PROFILES"),
            ("r8-freshness-controls.py", "SUPPORTED_PROFILES"),
            ("r9-guard-return-controls.py", "SUPPORTED_PROFILES"),
        )
        for filename, attr in modules:
            module = load("r11_" + filename.replace("-", "_").replace(".", "_"), HERE / filename)
            with self.subTest(consumer=filename):
                supported = getattr(module, attr)
                self.assertIn(PROFILE_NAME, supported)
        overlays = load("r11_provider_overlays", ROOT / "research/challenge-8/merge/cloud-build/provider-overlays.py")
        self.assertIn(PROFILE_NAME, overlays.SUPPORTED_PROFILES)
        prove_path = ROOT / "research/challenge-8/merge/overnight/guard-ownership/insertion-onecell/prove.py"
        prove = prove_path.read_text()
        self.assertIn("R11_PROFILE = \"" + PROFILE_NAME + "\"", prove)
        for relative in (
            "research/challenge-8/cloud-build/origin-layout/compile-preflight.sh",
            "research/challenge-8/cloud-build/origin-layout/generated-glue-compatibility-controls.py",
            "research/challenge-8/cloud-build/origin-layout/generated-glue-receiver-controls.py",
            "research/challenge-8/cloud-build/origin-layout/onecell-selected-drop.py",
            "research/challenge-8/cloud-build/origin-layout/onecell-caller-composition.py",
            "research/challenge-8/cloud-build/origin-layout/concrete-consumer.py",
            "research/challenge-8/merge/overnight/guard-ownership/insertion-onecell/build-profile.sh",
        ):
            self.assertIn(PROFILE_NAME, (ROOT / relative).read_text(), relative)

    def test_recipe_closes_only_existing_registration_artifacts(self):
        recipe = json.loads((ROOT / "research/challenge-8/cloud-build/recipes/merge.json").read_bytes())
        paths = recipe["proof_paths"]
        required = preflight.REQUIRED_PROOF_PATHS | {
            "research/challenge-8/cloud-build/origin-layout/r11-phase-service-test.py",
            "research/challenge-8/cloud-build/origin-layout/R11-INPUTS-20261021.json",
            "research/challenge-8/cloud-build/origin-layout/R11-LABEL-STORAGE-DESIGN-20261021.md",
            "research/challenge-8/cloud-build/origin-layout/r11-trace-service-test.py",
        }
        self.assertTrue(required <= set(paths))
        self.assertEqual(paths, sorted(set(paths)))
        for path in required:
            self.assertTrue((ROOT / path).is_file(), path)

    def test_r11_freshness_requires_run_identity_without_running_stages(self):
        freshness = load("r11_freshness_controls", HERE / "r8-freshness-controls.py")
        with tempfile.TemporaryDirectory(prefix="r11-freshness-identity-") as temporary:
            profile = Path(temporary) / "profile.json"
            profile.write_text(json.dumps({
                "schema": "smallsort-tracked-md-profile-v2",
                "profile": PROFILE_NAME, "accepted": False,
                "effective_tool_commit": TOOL_COMMIT,
            }))
            args = SimpleNamespace(profile=PROFILE_NAME, tool_home=Path(temporary) / "tool")
            result = freshness.run(Path(temporary) / "evidence", args,
                                   {"SMALLSORT_MERGE_PROFILE": str(profile)},
                                   lambda *a, **k: 0, validated_run=None)
            self.assertIn("r11_run_identity_error", result)
            self.assertFalse(result["accepted"])
            self.assertFalse(result["proof_credit"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
