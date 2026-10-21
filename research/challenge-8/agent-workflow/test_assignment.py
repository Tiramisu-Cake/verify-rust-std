import copy
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import assignment
import checkpoint


SHA40 = "a" * 40
SHA256 = "b" * 64
PREVIOUS = "select4-closed-2026"
OLD_PHASE = "SORT4-CALLER-BRIDGE"
OWNER = "select-sort4"


def git(path, *args):
    return subprocess.run(["git", "-C", str(path), *args], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).stdout.strip()


class AssignmentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.tmp_root = Path(self.tmp.name)
        self.repo = self.tmp_root / "worktree"
        self.repo.mkdir()
        git(self.repo, "init", "-b", "select4-next")
        git(self.repo, "config", "user.email", "agent@example.invalid")
        git(self.repo, "config", "user.name", "Fixture Agent")
        git(self.repo, "remote", "add", "origin", "https://github.com/Tiramisu-Cake/verify-rust-std.git")
        self.base = self.repo / "research/challenge-8"
        self.base.mkdir(parents=True)
        (self.base / "profiles").mkdir()
        (self.base / "new").mkdir()
        self.profile_rel = "research/challenge-8/profiles/select.json"
        self.profile = self.repo / self.profile_rel
        self.profile_bytes = b'{"lane":"select-sort4","profile_accepted":false}\n'
        self.profile.write_bytes(self.profile_bytes)
        self.previous_ledger_rel = "research/challenge-8/old/BUDGET.json"
        (self.repo / "research/challenge-8/old").mkdir()
        self.ledger = self.repo / self.previous_ledger_rel
        self.ledger_bytes = json.dumps({
            "schema": "old-ledger", "phase": OLD_PHASE, "owner": OWNER, "status": "CLOSED",
            "ceiling_build_seconds": 3600, "used_build_seconds": 1892,
            "retired_seconds": 0, "unused_retired_seconds": 1708,
            "remaining_build_seconds": 1708, "carry_forward_seconds": 0,
            "active_build": None, "builds": [], "unresolved": [],
        }, sort_keys=True).encode() + b"\n"
        self.ledger.write_bytes(self.ledger_bytes)
        prefix = f"# Prior mission\n\nTask ID: `{PREVIOUS}`; Owner: **Select/sort4**. Phase: `{OLD_PHASE}`. Ledger: `{self.previous_ledger_rel}`.\n\n".encode()
        oldcp = self.closed_checkpoint(hashlib.sha256(prefix).hexdigest())
        (self.base / "CURRENT-TASK.md").write_bytes(prefix + checkpoint.REPORT_MARKER.encode() + b"\nold closeout\n")
        (self.base / "STATUS.md").write_bytes(b"old status\n")
        (self.base / "AGENTS-COMPACT.md").write_bytes(b"old task compact agents\n")
        (self.repo / "AGENTS.md").write_bytes(b"old root agents\n")
        (self.base / "CHECKPOINT.json").write_text(json.dumps(oldcp), encoding="utf-8")
        git(self.repo, "add", "research")
        git(self.repo, "commit", "-m", "closed task fixture")
        self.baseline = git(self.repo, "rev-parse", "HEAD")

        self.toolrepo = self.tmp_root / "tool"
        self.toolrepo.mkdir()
        git(self.toolrepo, "init", "-b", "verifast-review")
        git(self.toolrepo, "config", "user.email", "agent@example.invalid")
        git(self.toolrepo, "config", "user.name", "Fixture Agent")
        (self.toolrepo / "tool.txt").write_text("tool\n")
        git(self.toolrepo, "add", "tool.txt")
        git(self.toolrepo, "commit", "-m", "tool")
        self.tool_sha = git(self.toolrepo, "rev-parse", "HEAD")
        self.spec = self.make_spec()
        self.spec_path = self.tmp_root / "spec.json"
        self.write_spec()
        self.coordination = self.tmp_root / "coordination"
        self.coordination.mkdir()
        (self.coordination / "lock").touch()
        (self.coordination / "active.json").write_text(json.dumps({"schema_version": 3, "max_active": 3, "reservations": []}), encoding="utf-8")
        self.canonical = self.tmp_root / "canonical"
        self.canonical.mkdir()
        (self.canonical / "CORE.md").write_text("# permanent core\n")
        (self.canonical / "AGENTS-COMPACT.md").write_text("# compact instructions\n")

    def tearDown(self):
        self.tmp.cleanup()

    def closed_checkpoint(self, digest):
        data = {
            "schema": checkpoint.SCHEMA, "task_id": PREVIOUS, "owner": OWNER,
            "phase": OLD_PHASE, "state": "CLOSED", "updated_utc": "2026-10-10T00:00:00Z",
            "assignment_sha256": digest,
            "baseline": {"source_sha": SHA40, "tool_sha": SHA40, "profile_sha256": SHA256},
            "session": {"t0": "2026-10-08T08:00:00Z", "main_deadline_utc": "2026-10-08T10:00:00Z",
                        "deadline_utc": "2026-10-08T10:30:00Z", "budget_seconds": 3600,
                        "spent_seconds": 934, "retired_seconds": 2666, "remaining_seconds": 0,
                        "active_build_ids": [], "unresolved_ids": []},
            "confirmed": [], "open": [],
            "blocker": {"summary": "resolved at closeout", "evidence": []},
            "rejected": [], "next_step": "closed", "artifacts": [],
        }
        return checkpoint.validate(data)

    def make_spec(self):
        return {
            "schema": assignment.SCHEMA,
            "task_id": "select4-next", "previous_task_id": PREVIOUS,
            "title": "Continue sort4 caller admission", "owner": OWNER,
            "worktree": str(self.repo), "branch": "select4-next",
            "baseline_sha": self.baseline, "source_sha": self.baseline,
            "tool_sha": self.tool_sha, "tool_worktree": str(self.toolrepo), "tool_branch": "verifast-review",
            "profile_path": self.profile_rel, "profile_sha256": hashlib.sha256(self.profile_bytes).hexdigest(),
            "phase": "SORT4-ACTUAL-CALLER", "lane": "select-sort4",
            "ledger_path": "research/challenge-8/new/BUDGET.json",
            "previous_ledger_path": self.previous_ledger_rel,
            "goal": "Establish the exact admitted caller path before the full sort4 invocation.",
            "steps": ["Inspect caller admission", "Record bounded evidence"],
            "special_bounds": ["Preserve UNKNOWN and separate source claims from independent credit."],
            "references": [{"title": "Plan", "path": "research/challenge-8/PLAN.md"}],
            "handoff": {"confirmed": [], "open": ["actual invocation remains NOT_RUN"],
                        "blocker": {"summary": "caller admission remains open", "evidence": []},
                        "rejected": [], "next_step": "Inspect the admitted caller boundary.", "artifacts": []},
        }

    def write_spec(self):
        self.spec_path.write_text(json.dumps(self.spec), encoding="utf-8")

    def snapshot(self):
        return {p.relative_to(self.repo).as_posix(): p.read_bytes()
                for p in self.repo.rglob("*") if p.is_file() and ".git" not in p.parts}

    def test_create_is_compact_fresh_and_checkpoint_digest_matches(self):
        out = self.tmp_root / "CURRENT-TASK-draft.md"
        assignment.create(self.spec_path, out)
        raw = out.read_bytes()
        self.assertLessEqual(len(raw), assignment.MAX_TASK_BYTES)
        self.assertEqual(raw.count(checkpoint.REPORT_MARKER.encode()), 1)
        prefix = raw.split(checkpoint.REPORT_MARKER.encode(), 1)[0]
        _, generated = assignment.render_task(self.spec)
        self.assertEqual(hashlib.sha256(prefix).hexdigest(), generated["assignment_sha256"])
        self.assertIn(b"T0 NOT_SET", raw)
        self.assertIn(b"CORE.md", raw)
        self.assertIn(b"register the exact phase through the assigned branch client", raw)
        with self.assertRaises(assignment.AssignmentError):
            assignment.create(self.spec_path, out)

    def test_oversized_task_refuses_output(self):
        self.spec["title"] = "T" * 1000
        self.spec["goal"] = "G" * 1000
        self.spec["steps"] = ["S" * 700] * 3
        self.spec["special_bounds"] = ["B" * 700] * 3
        self.write_spec()
        out = self.tmp_root / "too-large.md"
        with self.assertRaisesRegex(assignment.AssignmentError, "limit is 6144"):
            assignment.create(self.spec_path, out)
        self.assertFalse(out.exists())

    def test_task_cannot_smuggle_duplicate_report_marker(self):
        self.spec["goal"] += "\n" + checkpoint.REPORT_MARKER
        self.write_spec()
        out = self.tmp_root / "duplicate-marker.md"
        with self.assertRaisesRegex(assignment.AssignmentError, "exactly one generated report marker"):
            assignment.create(self.spec_path, out)
        self.assertFalse(out.exists())

    def test_active_same_owner_reservation_refuses_without_writes(self):
        self.write_spec()
        (self.coordination / "active.json").write_text(json.dumps({
            "schema_version": 3, "max_active": 3,
            "reservations": [{"owner": OWNER, "ledger": "/tmp/old", "dispatch_token": "x"}],
        }), encoding="utf-8")
        before = self.snapshot()
        with self.assertRaisesRegex(assignment.AssignmentError, "occupied or unresolved"):
            assignment.install(self.spec_path, self.coordination)
        self.assertEqual(self.snapshot(), before)
        with (self.coordination / "lock").open("rb") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)

    def test_install_archives_exact_bytes_and_syncs_checkpoint_views(self):
        self.write_spec()
        with patch.object(assignment, "CORE_DIR", self.canonical):
            assignment.install(self.spec_path, self.coordination)
        history = self.base / "task-history" / PREVIOUS
        self.assertTrue(history.is_dir())
        manifest = json.loads((history / "manifest.json").read_text())
        for name, digest in manifest["files"].items():
            archived = history / f"{name}.{digest}"
            self.assertEqual(hashlib.sha256(archived.read_bytes()).hexdigest(), digest)
        self.assertEqual(self.ledger.read_bytes(), self.ledger_bytes)
        self.assertFalse((self.repo / self.spec["ledger_path"]).exists())
        current = (self.base / "CURRENT-TASK.md").read_bytes()
        marker = checkpoint.REPORT_MARKER.encode()
        prefix = current.split(marker, 1)[0]
        cpdata = checkpoint.validate(json.loads((self.base / "CHECKPOINT.json").read_text()))
        self.assertEqual(cpdata["state"], "NOT_STARTED")
        self.assertIsNone(cpdata["session"]["t0"])
        self.assertEqual(cpdata["assignment_sha256"], hashlib.sha256(prefix).hexdigest())
        self.assertEqual((self.base / "STATUS.md").read_text(), checkpoint.render(cpdata, "status"))
        self.assertIn(b"Dates: T0 `NOT_SET`", current)
        self.assertEqual((self.base / "agent-workflow/CORE.md").read_text(), (self.canonical / "CORE.md").read_text())
        self.assertEqual((self.repo / "AGENTS.md").read_text(), (self.canonical / "AGENTS-COMPACT.md").read_text())
        self.assertEqual((history / f"ROOT-AGENTS.md.{manifest['files']['ROOT-AGENTS.md']}").read_bytes(), b"old root agents\n")

    def test_legacy_first_install_allows_absent_checkpoint(self):
        (self.base / "CHECKPOINT.json").unlink()
        self.write_spec()
        with patch.object(assignment, "CORE_DIR", self.canonical):
            assignment.install(self.spec_path, self.coordination)
        history = self.base / "task-history" / PREVIOUS
        manifest = json.loads((history / "manifest.json").read_text())
        self.assertNotIn("CHECKPOINT.json", manifest["files"])
        self.assertTrue((self.base / "CHECKPOINT.json").is_file())

    def test_accepts_merge_r15_ledger_and_rejects_unaccounted_build(self):
        spec = copy.deepcopy(self.spec)
        spec["owner"] = "merge"
        ledger = {"phase": "MERGE-R15", "owner": "merge", "status": "CLOSED",
                  "ceiling_build_seconds": 3600, "used_build_seconds": 2690,
                  "retired_build_seconds": 910, "remaining_build_seconds": 0,
                  "active_build": None, "builds": [{"result": "SUCCESS", "accounted": True}]}
        self.ledger.write_text(json.dumps(ledger), encoding="utf-8")
        git(self.repo, "add", self.previous_ledger_rel)
        git(self.repo, "commit", "-m", "merge R15 ledger fixture")
        self.assertEqual(assignment._ledger_closed(self.repo, spec), "MERGE-R15")
        ledger["builds"][0]["accounted"] = False
        self.ledger.write_text(json.dumps(ledger), encoding="utf-8")
        git(self.repo, "add", self.previous_ledger_rel)
        git(self.repo, "commit", "-m", "unaccounted merge build fixture")
        with self.assertRaisesRegex(assignment.AssignmentError, "terminal accounting"):
            assignment._ledger_closed(self.repo, spec)

    def test_stale_profile_branch_and_history_conflict_fail_without_repo_writes(self):
        cases = []
        stale = copy.deepcopy(self.spec)
        stale["baseline_sha"] = git(self.repo, "commit-tree", "HEAD^{tree}", "-m", "unrelated root")
        cases.append((stale, None, "not an ancestor"))
        wrong_branch = copy.deepcopy(self.spec); wrong_branch["branch"] = "wrong"; cases.append((wrong_branch, None, "branch mismatch"))
        wrong_profile = copy.deepcopy(self.spec); wrong_profile["profile_sha256"] = "f" * 64; cases.append((wrong_profile, None, "profile SHA-256 mismatch"))
        for spec, _, expected in cases:
            with self.subTest(expected=expected):
                self.spec = spec; self.write_spec(); before = self.snapshot()
                with self.assertRaisesRegex(assignment.AssignmentError, expected):
                    assignment.install(self.spec_path, self.coordination)
                self.assertEqual(self.snapshot(), before)
        self.spec = self.make_spec(); self.write_spec()
        (self.base / "task-history" / PREVIOUS).mkdir(parents=True)
        before = self.snapshot()
        with self.assertRaisesRegex(assignment.AssignmentError, "already exists"):
            assignment.install(self.spec_path, self.coordination)
        self.assertEqual(self.snapshot(), before)

    def test_symlink_profile_fails_before_mutation(self):
        self.profile.unlink()
        self.profile.symlink_to(self.ledger)
        before = self.snapshot()
        with self.assertRaisesRegex(assignment.AssignmentError, "symlink"):
            assignment.install(self.spec_path, self.coordination)
        self.assertEqual(self.snapshot(), before)

    def test_worktree_closed_ledger_must_match_committed_head(self):
        active = json.loads(self.ledger_bytes)
        active["status"] = "ACTIVE"
        active_bytes = json.dumps(active, sort_keys=True).encode() + b"\n"
        self.ledger.write_bytes(active_bytes)
        git(self.repo, "add", self.previous_ledger_rel)
        git(self.repo, "commit", "-m", "active ledger fixture")
        self.ledger.write_bytes(self.ledger_bytes)
        self.write_spec()
        before = self.snapshot()
        with self.assertRaisesRegex(assignment.AssignmentError, "differ from the assigned branch HEAD"):
            assignment.install(self.spec_path, self.coordination)
        self.assertEqual(self.snapshot(), before)
        self.assertFalse((self.base / "task-history" / PREVIOUS).exists())

    def test_task_history_parent_symlink_to_outside_fails_without_writes(self):
        outside = self.tmp_root / "outside-history"
        outside.mkdir()
        (self.base / "task-history").symlink_to(outside, target_is_directory=True)
        self.write_spec()
        before = self.snapshot()
        with patch.object(assignment, "CORE_DIR", self.canonical):
            with self.assertRaisesRegex(assignment.AssignmentError, "task-history parent contains a symlink"):
                assignment.install(self.spec_path, self.coordination)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(list(outside.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
