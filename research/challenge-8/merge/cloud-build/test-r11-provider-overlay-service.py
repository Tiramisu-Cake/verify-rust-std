#!/usr/bin/env python3
"""Synthetic applicability checks for the two R11 identity overlays."""
import importlib.util
from pathlib import Path
import subprocess
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("r11_provider_overlay", HERE / "provider-overlays.py")
provider = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(provider)
PROOF_COMMIT = "4c14e05f009a87a0b64ea17d27246dad5d16ad58"
PROVE_PATH = "research/challenge-8/merge/overnight/guard-ownership/insertion-onecell/prove.py"
COMPAT_PATH = "research/challenge-8/cloud-build/origin-layout/generated-glue-compatibility-controls.py"


class R11OverlayTests(unittest.TestCase):
    def test_selected_r11_prove_pin_matches_selected_source(self):
        source = subprocess.check_output(["git", "show", f"{PROOF_COMMIT}:{PROVE_PATH}"], cwd=HERE.parents[3])
        self.assertEqual(provider.sha(source), provider.R11_FILES[PROVE_PATH])
        self.assertEqual((HERE.parents[3] / PROVE_PATH).read_bytes(), source)

    def test_r17_compatibility_source_pin_matches_selected_source(self):
        source = (HERE.parents[3] / COMPAT_PATH).read_bytes()
        self.assertEqual(provider.sha(source), provider.R11_FILES[COMPAT_PATH])
        self.assertEqual(provider.R11_FILES[COMPAT_PATH],
                         "2cedb29c2c0194e8e7f4eb254c9a5e27c8eb8b5faa864bc4bd60f3a37065b2c3")

    def test_only_exact_r11_inputs_are_identity_overlays(self):
        self.assertEqual(len(provider.FILES), 18)
        self.assertEqual(len(provider.R11_FILES), 3)
        self.assertEqual(set(provider.files_for_profile(provider.R11_PROFILE)),
                         set(provider.FILES) | set(provider.R11_FILES))
        for path in provider.R11_FILES:
            with self.subTest(path=path):
                original = b"synthetic exact R11 source\n"
                self.assertIs(provider.transform(path, original,
                    profile=provider.R11_PROFILE), original)
                with self.assertRaisesRegex(SystemExit, "only valid for the selected R11"):
                    provider.transform(path, original, profile=provider.R10_PROFILE)

    def test_legacy_profile_retains_exact_old_pin_set(self):
        self.assertEqual(provider.files_for_profile(provider.R10_PROFILE), provider.FILES)
        self.assertEqual(provider.files_for_profile(provider.R9_PROFILE), provider.FILES)

    def test_unknown_python_source_still_fails_closed(self):
        with self.assertRaisesRegex(SystemExit, "unhandled provider overlay"):
            provider.transform("research/challenge-8/cloud-build/origin-layout/not-known.py",
                               b"synthetic", profile=provider.R11_PROFILE)


if __name__ == "__main__":
    unittest.main(verbosity=2)
