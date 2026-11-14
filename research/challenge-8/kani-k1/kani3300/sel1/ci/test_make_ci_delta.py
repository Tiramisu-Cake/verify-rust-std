#!/usr/bin/env python3
"""Local packaging tests: Python plus temporary Git only; no builds/network/CI."""
import contextlib
import importlib.util
import io
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("make_ci_delta", HERE / "make-ci-delta.py")
delta = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(delta)
REPO = Path("/root/kani-fix-3300-replay-c1-w15")


class DeltaTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="sel1-delta-test-")
        self.addCleanup(self.temp.cleanup)
        self.package = Path(self.temp.name) / "package"
        shutil.copytree(HERE / "full-export", self.package / "full-export")
        self.output = self.package / "ci-overlay-delta.patch"
        self.original_head = delta.run(["git", "-C", str(REPO), "rev-parse", "HEAD"])
        self.original_status = delta.run(["git", "-C", str(REPO), "status", "--porcelain"])

    def tearDown(self):
        self.assertEqual(self.original_head, delta.run(["git", "-C", str(REPO), "rev-parse", "HEAD"]))
        self.assertEqual(self.original_status, delta.run(["git", "-C", str(REPO), "status", "--porcelain"]))

    def generate(self, check=False):
        argv = ["make-ci-delta.py", "--repo", str(REPO), "--package", str(self.package),
                "--output", str(self.output)] + (["--check"] if check else [])
        with mock.patch("sys.argv", argv), contextlib.redirect_stdout(io.StringIO()):
            return delta.main()

    def test_round_trip_matches_published_package_bytes(self):
        self.assertEqual(self.generate(), 0)
        self.assertEqual(self.output.read_bytes(), (HERE / self.output.name).read_bytes())
        before = self.output.read_bytes()
        self.assertEqual(self.generate(check=True), 0)
        self.assertEqual(self.output.read_bytes(), before)

    def test_check_rejects_changed_patch_without_overwriting(self):
        self.generate()
        self.output.write_bytes(self.output.read_bytes() + b"\nchanged\n")
        bad = self.output.read_bytes()
        with self.assertRaisesRegex(ValueError, "existing overlay delta differs"):
            self.generate(check=True)
        self.assertEqual(self.output.read_bytes(), bad)

    def test_check_rejects_wrong_checksum_without_overwriting(self):
        self.generate()
        path = self.output.with_suffix(".patch.sha256")
        path.write_text("wrong checksum\n")
        with self.assertRaisesRegex(ValueError, "checksum mismatch"):
            self.generate(check=True)
        self.assertEqual(path.read_text(), "wrong checksum\n")

    def test_missing_export_is_rejected_before_output(self):
        (self.package / "full-export/scripts/kani3300-replay/test_replay.py").unlink()
        with self.assertRaisesRegex(ValueError, "file inventory mismatch"):
            self.generate()
        self.assertFalse(self.output.exists())

    def test_extra_export_is_rejected_before_output(self):
        (self.package / "full-export/unexpected").write_text("unexpected")
        with self.assertRaisesRegex(ValueError, "file inventory mismatch"):
            self.generate()
        self.assertFalse(self.output.exists())

    def test_wrong_base_tree_is_rejected(self):
        with mock.patch.object(delta, "BASE_TREE", "0" * 40):
            with self.assertRaisesRegex(ValueError, "base tree mismatch"):
                self.generate()
        self.assertFalse(self.output.exists())

    def test_check_rejects_changed_export_without_overwriting(self):
        self.generate()
        before = self.output.read_bytes()
        path = self.package / "full-export/scripts/kani3300-replay/replay.py"
        path.write_text(path.read_text() + "\n# changed\n")
        with self.assertRaisesRegex(ValueError, "existing overlay delta differs"):
            self.generate(check=True)
        self.assertEqual(self.output.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
