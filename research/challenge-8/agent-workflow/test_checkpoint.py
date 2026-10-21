import copy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest

import checkpoint


BUILD = "12345678-1234-4234-8234-123456789abc"
SHA = "a" * 64
SHA40 = "b" * 40


def sample(state="ACTIVE"):
    not_started = state == "NOT_STARTED"
    return {
        "schema": checkpoint.SCHEMA,
        "task_id": "select-sort4-current",
        "owner": "select-sort4",
        "phase": "caller-bridge",
        "state": state,
        "updated_utc": "2026-10-21T10:00:00Z",
        "assignment_sha256": SHA,
        "baseline": {"source_sha": None, "tool_sha": SHA40, "profile_sha256": None},
        "session": {
            "t0": None if not_started else "2026-10-21T08:00:00Z",
            "main_deadline_utc": None if not_started else "2026-10-21T10:00:00Z",
            "deadline_utc": None if not_started else "2026-10-21T10:30:00Z",
            "budget_seconds": 3600,
            "spent_seconds": 0 if not_started else 300,
            "retired_seconds": 0,
            "remaining_seconds": 3600 if not_started else 3300,
            "active_build_ids": [BUILD] if state == "HANDOFF" else [],
            "unresolved_ids": ["gate-origin"] if state == "HANDOFF" else [],
        },
        "confirmed": [{
            "claim": "The source reports bounded probe pass; independent credit remains separate.",
            "assurance": "SOURCE_REPORTED",
            "evidence": [{"path": "evidence/claim.json", "sha256": SHA, "build_id": BUILD}],
        }],
        "open": ["actual invocation remains UNKNOWN"],
        "blocker": {"summary": "caller admission is unresolved", "location": "select.rs:42", "build_id": None, "evidence": []},
        "rejected": [{"approach": "slice projection", "reason": "does not establish exact path correspondence", "evidence": []}],
        "next_step": "Inspect the admitted caller boundary.",
        "artifacts": [{"path": "checkpoint.json", "sha256": SHA}],
    }


class CheckpointTests(unittest.TestCase):
    def test_valid_and_explicit_unknowns(self):
        data = sample("NOT_STARTED")
        self.assertIs(checkpoint.validate(data), data)
        report = checkpoint.render(data, "report")
        self.assertIn("UNKNOWN", report)
        self.assertIn("T0 `NOT_SET`", report)
        self.assertIn("STATUS.md", report)
        status = checkpoint.render(data, "status")
        self.assertIn("[SOURCE_REPORTED]", status)
        self.assertNotIn("INDEPENDENTLY_ESTABLISHED", report)
        self.assertIn("actual invocation remains UNKNOWN", status)

    def test_source_claim_is_never_promoted(self):
        status = checkpoint.render(sample(), "status")
        self.assertIn("[SOURCE_REPORTED] The source reports", status)
        self.assertNotIn("[INDEPENDENTLY_ESTABLISHED]", status)

    def test_active_handoff_keeps_build_and_unresolved_ids_visible(self):
        report = checkpoint.render(sample("HANDOFF"), "status")
        self.assertIn(BUILD, report)
        self.assertIn("gate-origin", report)

    def test_rejects_identity_and_state_errors(self):
        for change in (
            lambda x: x.update(task_id=""),
            lambda x: x.update(assignment_sha256="abc"),
            lambda x: x["baseline"].update(tool_sha="abc"),
            lambda x: x["session"].update(active_build_ids=["not-a-build-uuid"]),
            lambda x: x.update(state="PASS"),
            lambda x: x["confirmed"][0].update(assurance="PASS"),
            lambda x: x["confirmed"][0].update(evidence=[]),
        ):
            data = copy.deepcopy(sample())
            change(data)
            with self.subTest(data=data), self.assertRaises(checkpoint.CheckpointError):
                checkpoint.validate(data)

    def test_rejects_window_math_budget_and_closed_invariants(self):
        data = sample()
        data["session"]["deadline_utc"] = "2026-10-21T11:00:00Z"
        with self.assertRaisesRegex(checkpoint.CheckpointError, "120 minutes"):
            checkpoint.validate(data)
        data = sample()
        data["session"]["remaining_seconds"] -= 1
        with self.assertRaisesRegex(checkpoint.CheckpointError, "budget arithmetic"):
            checkpoint.validate(data)
        data = sample("CLOSED")
        with self.assertRaisesRegex(checkpoint.CheckpointError, "CLOSED requires"):
            checkpoint.validate(data)

    def test_rejects_oversized_narrative_or_render(self):
        data = sample()
        data["next_step"] = "x" * (checkpoint.MAX_NARRATIVE + 1)
        with self.assertRaisesRegex(checkpoint.CheckpointError, "exceeds"):
            checkpoint.validate(data)
        data = sample()
        data["open"] = ["x" * 1000] * 32
        with self.assertRaisesRegex(checkpoint.CheckpointError, "exceeds 6144"):
            checkpoint.render(data, "status")

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / ".git").mkdir()
        self.flow = self.root / "research" / "challenge-8"
        self.flow.mkdir(parents=True)
        self.checkpoint_path = self.flow / "CHECKPOINT.json"
        self.status_path = self.flow / "STATUS.md"
        self.task_path = self.flow / "CURRENT-TASK.md"
        self.prefix = "# Assigned task\r\n\r\nKeep this assignment intact.\r\n\r\n"
        self.write_sample()
        self.status_path.write_text("old status\n", encoding="utf-8")
        self.task_path.write_bytes((self.prefix + checkpoint.REPORT_MARKER + "\r\nold report\r\n").encode())

    def tearDown(self):
        self.tmp.cleanup()

    def write_sample(self, data=None):
        data = copy.deepcopy(data or sample())
        data["assignment_sha256"] = hashlib.sha256(self.prefix.encode()).hexdigest()
        self.checkpoint_path.write_text(json.dumps(data), encoding="utf-8")

    def test_write_views_preserves_assignment_and_replaces_report_once(self):
        checkpoint.write_views(self.checkpoint_path, self.status_path, self.task_path)
        task = self.task_path.read_bytes()
        self.assertTrue(task.startswith(self.prefix.encode()))
        self.assertEqual(task.count(checkpoint.REPORT_MARKER.encode()), 1)
        self.assertIn(b"STATUS.md", task)
        self.assertIn("Agent checkpoint", self.status_path.read_text(encoding="utf-8"))
        self.assertIn("T0 `2026-10-21T08:00:00Z`", self.status_path.read_text(encoding="utf-8"))
        self.assertIn("evidence/claim.json", self.status_path.read_text(encoding="utf-8"))

    def test_stale_digest_and_duplicate_marker_fail_before_any_write(self):
        self.write_sample()
        task_original = self.prefix.encode() + (checkpoint.REPORT_MARKER + "\r\nold\r\n").encode()
        status_original = "old status\n"
        self.task_path.write_bytes(task_original)
        data = json.loads(self.checkpoint_path.read_text())
        data["assignment_sha256"] = "c" * 64
        self.checkpoint_path.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaisesRegex(checkpoint.CheckpointError, "does not match"):
            checkpoint.write_views(self.checkpoint_path, self.status_path, self.task_path)
        self.assertEqual(self.status_path.read_text(), status_original)
        self.assertEqual(self.task_path.read_bytes(), task_original)
        self.write_sample()
        self.task_path.write_bytes(self.prefix.encode() + (checkpoint.REPORT_MARKER + "\r\n" + checkpoint.REPORT_MARKER + "\r\n").encode())
        before = self.status_path.read_text()
        with self.assertRaisesRegex(checkpoint.CheckpointError, "exactly one"):
            checkpoint.write_views(self.checkpoint_path, self.status_path, self.task_path)
        self.assertEqual(self.status_path.read_text(), before)

    def test_symlinks_and_outside_targets_are_rejected(self):
        self.status_path.unlink()
        self.status_path.symlink_to(self.task_path)
        with self.assertRaisesRegex(checkpoint.CheckpointError, "symlink"):
            checkpoint.write_views(self.checkpoint_path, self.status_path, self.task_path)

    def test_rejects_arbitrary_same_worktree_targets(self):
        unsafe = self.flow / "source.rs"
        unsafe.write_text("keep", encoding="utf-8")
        with self.assertRaisesRegex(checkpoint.CheckpointError, "CURRENT-TASK.md"):
            checkpoint.write_views(self.checkpoint_path, self.status_path, unsafe)
        self.assertEqual(unsafe.read_text(), "keep")

    def test_current_total_size_limit_fails_before_any_write(self):
        prefix = "x" * (checkpoint.MAX_OUTPUT - 100)
        prefix = prefix + "\n"
        self.task_path.write_bytes((prefix + checkpoint.REPORT_MARKER + "\nold\n").encode())
        data = sample()
        self.prefix = prefix
        data["assignment_sha256"] = hashlib.sha256(prefix.encode()).hexdigest()
        self.write_sample(data)
        before_status = self.status_path.read_bytes()
        before_task = self.task_path.read_bytes()
        with self.assertRaisesRegex(checkpoint.CheckpointError, "CURRENT-TASK output exceeds"):
            checkpoint.write_views(self.checkpoint_path, self.status_path, self.task_path)
        self.assertEqual(self.status_path.read_bytes(), before_status)
        self.assertEqual(self.task_path.read_bytes(), before_task)


if __name__ == "__main__":
    unittest.main()
