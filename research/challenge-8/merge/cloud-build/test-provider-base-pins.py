#!/usr/bin/env python3
"""Static Git pin check and synthetic hash-gate tests; no real overlays/toolchain."""

import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve()
REPO = HERE.parents[4]
# Source contract of the failed Build, not a claim that this revision passed CI.
PROOF_COMMIT = "4c14e05f009a87a0b64ea17d27246dad5d16ad58"
spec = importlib.util.spec_from_file_location("provider_base_pins", HERE.with_name("provider-overlays.py"))
provider = importlib.util.module_from_spec(spec)
spec.loader.exec_module(provider)  # stdlib imports/constants/functions; main guarded


class TransformBoundary(Exception):
    """Stop immediately after successful validation, before any transformation."""


class BasePins(unittest.TestCase):
    def test_selected_proof_commit(self):
        self.assertEqual(len(provider.FILES), 18)
        for path, expected in provider.FILES.items():
            with self.subTest(path=path):
                original = subprocess.check_output(
                    ["git", "-C", str(REPO), "show", f"{PROOF_COMMIT}:{path}"]
                )
                self.assertEqual(provider.sha(original), expected)
                self.assertEqual((REPO / path).read_bytes(), original)

    def check_synthetic_gate(self, corrupt=None):
        with tempfile.TemporaryDirectory(prefix="provider-base-pins-") as temp:
            root = Path(temp)
            originals = {path: f"synthetic base {index}\n".encode()
                         for index, path in enumerate(provider.FILES)}
            pins = {path: provider.sha(data) for path, data in originals.items()}
            for path, data in originals.items():
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
            profile_path = root / "research/challenge-8/cloud-build/origin-layout/GLUE-PROFILE.json"
            profile_path.parent.mkdir(parents=True, exist_ok=True)
            profile_path.write_text(
                '{"profile":"' + provider.BASELINE_PROFILE + '","accepted":false}\n')
            if corrupt is not None:
                data = originals[corrupt]
                changed = bytes([data[0] ^ 1]) + data[1:]
                (root / corrupt).write_bytes(changed)
            before = {path: (root / path).read_bytes() for path in originals}
            evidence = root / "overlay-evidence"
            argv = ["provider-overlays.py", "--proof-root", str(root), "--evidence", str(evidence)]
            with patch.object(provider, "FILES", pins), patch.object(sys, "argv", argv), \
                 patch.object(provider, "transform", side_effect=TransformBoundary) as transform:
                if corrupt is None:
                    with self.assertRaises(TransformBoundary):
                        provider.main()
                    transform.assert_called_once()
                else:
                    with self.assertRaises(SystemExit) as error:
                        provider.main()
                    self.assertEqual(str(error.exception),
                        f"base source hash mismatch for {corrupt}: {provider.sha(before[corrupt])}")
                    transform.assert_not_called()
            self.assertEqual(before, {path: (root / path).read_bytes() for path in originals})
            self.assertFalse((evidence / "provider-overlay-manifest.json").exists())

    def test_all_synthetic_inputs_reach_transform_boundary(self):
        self.check_synthetic_gate()

    def test_one_byte_change_in_each_input_refuses_before_transform(self):
        self.assertEqual(len(provider.FILES), 18)
        for path in provider.FILES:
            with self.subTest(path=path):
                self.check_synthetic_gate(corrupt=path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
