"""Isolated static/synthetic controls for the R24 translator overlay."""

import hashlib
import json
import pathlib
import shutil
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
HISTORY = ROOT / "task-history" / "select-callee-r24"
PATCH = HISTORY / "checked-pointer-outcomes-r24.patch"
PINS = HISTORY / "CHECKED-OUTCOMES-PINS.json"






class CheckedPointerOutcomeTests(unittest.TestCase):
    def test_pins_and_patch_hash(self):
        pins = json.loads(PINS.read_text())
        self.assertEqual(hashlib.sha256(PATCH.read_bytes()).hexdigest(), pins["patch_sha256"])
        self.assertEqual(pins["base_translator_sha256"], "103a34afa6b403760454ab42462040805f34f0cf42576b8179bc5ff368505e44")
        self.assertEqual(len(pins["projects"]), 2)

    def test_patch_reproduces_pinned_translator(self):
        base = pathlib.Path("/tmp/r24-translator103.ml")
        if not base.exists():
            self.skipTest("pinned external translator baseline unavailable")
        pins = json.loads(PINS.read_text())
        self.assertEqual(hashlib.sha256(base.read_bytes()).hexdigest(), pins["base_translator_sha256"])
        with tempfile.TemporaryDirectory(prefix="r24-translator-patch-") as temp:
            root = pathlib.Path(temp)
            target = root / "src/rust_frontend/vf_mir_translator/vf_mir_translator.ml"
            target.parent.mkdir(parents=True)
            shutil.copyfile(base, target)
            subprocess.run(["git", "apply", str(PATCH)], cwd=root, check=True)
            self.assertEqual(hashlib.sha256(target.read_bytes()).hexdigest(), pins["result_translator_sha256"])
            fix = json.loads((HISTORY / "CHECKED-OUTCOMES-COMPILE-FIX-PINS.json").read_text())
            fix_patch = ROOT.parents[1] / fix["patch"]
            self.assertEqual(hashlib.sha256(fix_patch.read_bytes()).hexdigest(), fix["patch_sha256"])
            self.assertEqual(fix["base_translator_sha256"], pins["result_translator_sha256"])
            subprocess.run(["git", "apply", "--check", str(fix_patch)], cwd=root, check=True)
            subprocess.run(["git", "apply", str(fix_patch)], cwd=root, check=True)
            self.assertEqual(hashlib.sha256(target.read_bytes()).hexdigest(), fix["result_translator_sha256"])







if __name__ == "__main__":
    unittest.main()
