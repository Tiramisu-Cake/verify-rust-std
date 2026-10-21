"""Pure routing/isolation checks; never starts Codex or a model turn."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from experiments import queue_wakeup_probe as probe


class QueueWakeupProbeTests(unittest.TestCase):
    def setUp(self):
        self.expected = {"thread_id": "test-thread", "phase": "TEST-ONLY", "build_id": "synthetic-build", "main": 100, "absolute": 130}
        self.event = {"thread_id": "test-thread", "phase": "TEST-ONLY", "build_id": "synthetic-build", "event_id": "event-1"}

    def test_current_event_preserves_window(self):
        before = copy.deepcopy(self.expected)
        self.assertEqual(probe.event_guard(self.event, self.expected, set(), 99), "CONTINUE_EXISTING_WINDOW")
        self.assertEqual(self.expected, before)

    def test_duplicate_does_not_authorize_second_delivery(self):
        self.assertEqual(probe.event_guard(self.event, self.expected, {"event-1"}, 99), "DUPLICATE")

    def test_each_identity_mismatch_is_stale(self):
        for name in ("thread_id", "phase", "build_id"):
            with self.subTest(name=name):
                self.assertEqual(probe.event_guard({**self.event, name: "other"}, self.expected, set(), 99), "STALE_IDENTITY")

    def test_deadline_boundaries_do_not_open_new_window(self):
        self.assertEqual(probe.event_guard(self.event, self.expected, set(), 100), "CLOSEOUT_ONLY")
        self.assertEqual(probe.event_guard(self.event, self.expected, set(), 129), "CLOSEOUT_ONLY")
        self.assertEqual(probe.event_guard(self.event, self.expected, set(), 130), "EXPIRED")
        self.assertEqual(probe.event_guard(self.event, self.expected, set(), 131), "EXPIRED")

    def test_existing_or_symlink_output_refused_before_connection(self):
        with tempfile.TemporaryDirectory() as name, patch.object(probe, "Rpc") as rpc:
            root = Path(name)
            with self.assertRaises(probe.ProbeError):
                probe.run(root, 10)
            (root / "alias").symlink_to(root, target_is_directory=True)
            with self.assertRaises(probe.ProbeError):
                probe.run(root / "alias" / "new-output", 10)
            rpc.assert_not_called()

    def test_startup_failure_saved_without_model_or_other_session(self):
        with tempfile.TemporaryDirectory() as name:
            output = Path(name) / "new-output"
            with patch.object(probe, "Rpc", side_effect=probe.ProbeError("synthetic connection failure")), patch("builtins.print"):
                self.assertEqual(probe.run(output, 10), 2)
            result = json.loads((output / "result.json").read_text())
            self.assertEqual(result["result"], "ERROR")
            self.assertNotIn("thread_id", result)
            self.assertFalse(result["production_watcher_deployed"])

    def test_real_probe_requires_explicit_opt_in(self):
        result = subprocess.run([sys.executable, "-B", str(Path(probe.__file__)), "--out", "/tmp/not-created-by-help-test"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("--run-real-probe", result.stderr)


if __name__ == "__main__":
    unittest.main()
