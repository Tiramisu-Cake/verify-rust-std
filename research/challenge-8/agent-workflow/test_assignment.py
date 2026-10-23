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
        (self.canonical / "CLAUDE-COMPACT.md").write_text("# claude entry\n")
        (self.canonical / "RUNTIME-CODEX.md").write_text("# codex runtime\n")
        (self.canonical / "RUNTIME-CLAUDE.md").write_text("# claude runtime\n")

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
        self.assertEqual((self.repo / "CLAUDE.md").read_text(), (self.canonical / "CLAUDE-COMPACT.md").read_text())
        for name in ("RUNTIME-CODEX.md", "RUNTIME-CLAUDE.md"):
            self.assertEqual((self.base / "agent-workflow" / name).read_text(), (self.canonical / name).read_text())
        self.assertNotIn("ROOT-CLAUDE.md", manifest["files"])

    def test_install_archives_prior_claude_entry_and_runtime_profiles(self):
        (self.repo / "CLAUDE.md").write_bytes(b"old claude entry\n")
        (self.base / "agent-workflow").mkdir(exist_ok=True)
        (self.base / "agent-workflow/RUNTIME-CLAUDE.md").write_bytes(b"old claude runtime\n")
        self.spec["runtime"] = "claude"
        self.write_spec()
        with patch.object(assignment, "CORE_DIR", self.canonical):
            assignment.install(self.spec_path, self.coordination)
        history = self.base / "task-history" / PREVIOUS
        manifest = json.loads((history / "manifest.json").read_text())
        self.assertEqual((history / f"ROOT-CLAUDE.md.{manifest['files']['ROOT-CLAUDE.md']}").read_bytes(), b"old claude entry\n")
        archived = history / f"agent-workflow-RUNTIME-CLAUDE.md.{manifest['files']['agent-workflow-RUNTIME-CLAUDE.md']}"
        self.assertEqual(archived.read_bytes(), b"old claude runtime\n")
        self.assertEqual((self.repo / "CLAUDE.md").read_text(), "# claude entry\n")
        self.assertIn(b"Runtime: Claude Code.", (self.base / "CURRENT-TASK.md").read_bytes())

    def test_install_refuses_symlinked_claude_entry_without_writes(self):
        (self.repo / "CLAUDE.md").symlink_to(self.repo / "AGENTS.md")
        self.write_spec()
        before = self.snapshot()
        with patch.object(assignment, "CORE_DIR", self.canonical), self.assertRaisesRegex(assignment.AssignmentError, "symlink"):
            assignment.install(self.spec_path, self.coordination)
        self.assertEqual(self.snapshot(), before)
        self.assertFalse((self.base / "task-history").exists())

    def test_install_refuses_unsafe_runtime_profile_or_missing_canonical_without_writes(self):
        (self.base / "agent-workflow").mkdir(exist_ok=True)
        cases = []
        def link_profile():
            (self.base / "agent-workflow/RUNTIME-CODEX.md").symlink_to(self.repo / "AGENTS.md")
        def dangling_profile():
            (self.base / "agent-workflow/RUNTIME-CLAUDE.md").symlink_to(self.repo / "missing.md")
        def claude_dir():
            (self.repo / "CLAUDE.md").mkdir()
        def missing_canonical():
            (self.canonical / "CLAUDE-COMPACT.md").unlink()
        for name, change, message in (("link", link_profile, "symlink"), ("dangling", dangling_profile, "symlink"),
                                      ("dir", claude_dir, "regular file"), ("canonical", missing_canonical, "canonical CLAUDE-COMPACT.md")):
            with self.subTest(case=name):
                self.tearDown()
                self.setUp()
                (self.base / "agent-workflow").mkdir(exist_ok=True)
                change()
                self.write_spec()
                before = self.snapshot()
                with patch.object(assignment, "CORE_DIR", self.canonical), self.assertRaisesRegex(assignment.AssignmentError, message):
                    assignment.install(self.spec_path, self.coordination)
                self.assertEqual(self.snapshot(), before)
                self.assertFalse((self.base / "task-history").exists())

    def test_runtime_selects_entry_profile_and_absent_keeps_legacy_text(self):
        legacy, _ = assignment.render_task(self.spec)
        self.assertIn(b"the compact root [AGENTS.md](../../AGENTS.md), and the persistent", legacy)
        self.assertNotIn(b"Runtime:", legacy)
        for runtime, entry, profile in (("codex", b"[AGENTS.md]", b"RUNTIME-CODEX.md"),
                                        ("claude", b"[CLAUDE.md]", b"RUNTIME-CLAUDE.md")):
            with self.subTest(runtime=runtime):
                task, cpdata = assignment.render_task(dict(self.spec, runtime=runtime))
                prefix = task.split(checkpoint.REPORT_MARKER.encode(), 1)[0]
                self.assertIn(entry, prefix)
                self.assertIn(profile, prefix)
                self.assertEqual(hashlib.sha256(prefix).hexdigest(), cpdata["assignment_sha256"])
        for bad in ("Claude", "", None, 1, ["claude"]):
            with self.subTest(bad=bad), self.assertRaisesRegex(assignment.AssignmentError, "runtime must be"):
                assignment.render_task(dict(self.spec, runtime=bad))
        with self.assertRaisesRegex(assignment.AssignmentError, "unknown spec fields: runtimes"):
            assignment.render_task(dict(self.spec, runtimes="claude"))

    def test_legacy_relative_ledger_and_protocol_owner_keep_exact_binding(self):
        (self.base / "CHECKPOINT.json").unlink()
        task = self.base / "CURRENT-TASK.md"
        relative = Path(self.previous_ledger_rel).relative_to("research/challenge-8").as_posix()
        prefix = f"# Legacy task\nID {PREVIOUS}; owner {OWNER}; phase {OLD_PHASE}; ledger "
        task.write_text(prefix + "other/BUDGET.json\n" + checkpoint.REPORT_MARKER + "\nCLOSED\n")
        before = self.snapshot()
        with self.assertRaisesRegex(assignment.AssignmentError, "exact prior ledger"):
            assignment.install(self.spec_path, self.coordination)
        self.assertEqual(self.snapshot(), before)
        task.write_text(prefix + relative + "\n" + checkpoint.REPORT_MARKER + "\nCLOSED\n")
        with patch.object(assignment, "CORE_DIR", self.canonical):
            assignment.install(self.spec_path, self.coordination)
        self.assertEqual(self.ledger.read_bytes(), self.ledger_bytes)
        current = json.loads((self.base / "CHECKPOINT.json").read_text())
        self.assertEqual(current["state"], "NOT_STARTED")
        self.assertIsNone(current["session"]["t0"])

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

    def test_closed_cloud_ledger_uses_primary_counter_without_rewriting_aliases(self):
        ledger = json.loads(self.ledger_bytes)
        ledger.update(spent_build_seconds=0, retired_seconds=1708)
        raw = (json.dumps(ledger, sort_keys=True) + "\n").encode()
        self.ledger.write_bytes(raw)
        git(self.repo, "add", self.previous_ledger_rel)
        git(self.repo, "commit", "-m", "closed coordinator ledger with stale alias")
        self.assertEqual(assignment._ledger_closed(self.repo, self.spec), OLD_PHASE)
        self.assertEqual(self.ledger.read_bytes(), raw)
        # Installation and a new phase still require all ordinary gates.
        with patch.object(assignment, "CORE_DIR", self.canonical):
            assignment.install(self.spec_path, self.coordination)
        self.assertEqual(self.ledger.read_bytes(), raw)
        newcp = json.loads((self.base / "CHECKPOINT.json").read_text())
        self.assertEqual(newcp["state"], "NOT_STARTED")
        self.assertEqual(newcp["session"]["spent_seconds"], 0)
        self.assertIsNone(newcp["session"]["t0"])

    def test_invalid_primary_counter_never_falls_back_to_valid_alias(self):
        for value in (None, True, -1, 1893):
            ledger = json.loads(self.ledger_bytes)
            ledger.update(used_build_seconds=value, spent_build_seconds=1892)
            self.ledger.write_text(json.dumps(ledger))
            git(self.repo, "add", self.previous_ledger_rel)
            git(self.repo, "commit", "-m", "invalid primary counter fixture")
            before = self.snapshot()
            with self.subTest(value=value), self.assertRaises(assignment.AssignmentError):
                assignment._ledger_closed(self.repo, self.spec)
            self.assertEqual(self.snapshot(), before)

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
        history = self.base / "task-history" / PREVIOUS
        history.mkdir(parents=True)
        (history / "manifest.json").write_text("{}", encoding="utf-8")
        before = self.snapshot()
        with self.assertRaisesRegex(assignment.AssignmentError, "already exists"):
            assignment.install(self.spec_path, self.coordination)
        self.assertEqual(self.snapshot(), before)

    def test_window_timeout_must_fit_budget(self):
        spec = copy.deepcopy(self.spec)
        spec.update({"cloud_budget_seconds": 1200, "window": {"main_minutes": 120, "finish_minutes": 30, "max_timeout_seconds": 1500}})
        with self.assertRaisesRegex(assignment.AssignmentError, "must not exceed cloud_budget_seconds"):
            assignment.validate_spec(spec)

    def test_install_refuses_prior_checkpoint_window_that_differs_from_prior_task_text(self):
        prefix = (f"# Prior mission\n\nTask ID: `{PREVIOUS}`; Owner: **Select/sort4**. Phase: `{OLD_PHASE}`. Ledger: `{self.previous_ledger_rel}`.\n"
                  "Cloud budget: 3600 seconds. Wall window: 120 minutes main + 30 minutes closeout.\n\n").encode()
        oldcp = self.closed_checkpoint(hashlib.sha256(prefix).hexdigest())
        oldcp["session"].update({"main_minutes": 240, "main_deadline_utc": "2026-10-08T12:00:00Z", "deadline_utc": "2026-10-08T12:30:00Z"})
        checkpoint.validate(oldcp)
        (self.base / "CURRENT-TASK.md").write_bytes(prefix + checkpoint.REPORT_MARKER.encode() + b"\nold closeout\n")
        (self.base / "CHECKPOINT.json").write_text(json.dumps(oldcp), encoding="utf-8")
        git(self.repo, "add", "research"); git(self.repo, "commit", "-q", "-m", "self-declared window")
        before = self.snapshot()
        with patch.object(assignment, "CORE_DIR", self.canonical):
            with self.assertRaisesRegex(assignment.AssignmentError, "does not match the prior assignment: session window 240"):
                assignment.install(self.spec_path, self.coordination)
        self.assertEqual(self.snapshot(), before)

    def test_history_target_symlink_file_or_archive_collision_fail_without_writes(self):
        history = self.base / "task-history" / PREVIOUS
        history.parent.mkdir(parents=True, exist_ok=True)
        outside = self.tmp_root / "outside"; outside.mkdir()
        history.symlink_to(outside, target_is_directory=True)
        before = self.snapshot()
        with patch.object(assignment, "CORE_DIR", self.canonical):
            with self.assertRaisesRegex(assignment.AssignmentError, "symlink"):
                assignment.install(self.spec_path, self.coordination)
        self.assertEqual(self.snapshot(), before)
        history.unlink(); history.write_text("not a directory\n", encoding="utf-8")
        with patch.object(assignment, "CORE_DIR", self.canonical):
            with self.assertRaisesRegex(assignment.AssignmentError, "not a directory"):
                assignment.install(self.spec_path, self.coordination)
        history.unlink(); history.mkdir()
        status_digest = hashlib.sha256(b"old status\n").hexdigest()
        (history / f"STATUS.md.{status_digest}").write_text("stale partial archive\n", encoding="utf-8")
        before = self.snapshot()
        with patch.object(assignment, "CORE_DIR", self.canonical):
            with self.assertRaisesRegex(assignment.AssignmentError, "archive file already exists"):
                assignment.install(self.spec_path, self.coordination)
        self.assertEqual(self.snapshot(), before)
        self.assertFalse((history / "manifest.json").exists())

    def test_install_archives_into_existing_agent_history_dir_without_manifest(self):
        history = self.base / "task-history" / PREVIOUS
        history.mkdir(parents=True)
        (history / "ENTRY-CONFIRMED.json").write_text("{}", encoding="utf-8")
        git(self.repo, "add", "research"); git(self.repo, "commit", "-q", "-m", "agent artifacts in task-history")
        with patch.object(assignment, "CORE_DIR", self.canonical):
            assignment.install(self.spec_path, self.coordination)
        manifest = json.loads((history / "manifest.json").read_text())
        self.assertIn("CURRENT-TASK.md", manifest["files"])
        self.assertEqual((history / "ENTRY-CONFIRMED.json").read_text(), "{}")

    def test_closed_ledger_accepts_fully_retired_closeout_with_unused_retired(self):
        ledger = json.loads(self.ledger_bytes)
        # CORE closeout: remaining 0, unused seconds retired (Select R23 convention).
        ledger.update(remaining_build_seconds=0, retired_seconds=1708, unused_retired_seconds=1708)
        self.ledger.write_bytes((json.dumps(ledger, sort_keys=True) + "\n").encode())
        git(self.repo, "add", self.previous_ledger_rel); git(self.repo, "commit", "-q", "-m", "fully retired ledger")
        self.assertEqual(assignment._ledger_closed(self.repo, self.spec), OLD_PHASE)
        ledger.update(retired_seconds=1700)
        self.ledger.write_bytes((json.dumps(ledger, sort_keys=True) + "\n").encode())
        git(self.repo, "add", self.previous_ledger_rel); git(self.repo, "commit", "-q", "-m", "inconsistent retirement")
        with self.assertRaisesRegex(assignment.AssignmentError, "inconsistent"):
            assignment._ledger_closed(self.repo, self.spec)

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

    def network_bootstrap_spec(self):
        spec = copy.deepcopy(self.spec)
        spec.update({"task_id": "network-first", "previous_task_id": "networks-iteration-2026-10-07",
                     "owner": "network", "lane": "network", "phase": "NETWORK-BOOTSTRAP",
                     "runtime": "claude", "bootstrap": True, "cloud_budget_seconds": 0,
                     "profile_path": None, "profile_sha256": None,
                     "ledger_path": None, "previous_ledger_path": None})
        return spec

    def make_bootstrap_worktree(self):
        for name in ("CURRENT-TASK.md", "CHECKPOINT.json"):
            git(self.repo, "rm", "-q", f"research/challenge-8/{name}")
        git(self.repo, "commit", "-q", "-m", "worktree without prior assignment")

    def test_default_budget_rendering_is_unchanged_by_explicit_defaults(self):
        explicit = copy.deepcopy(self.spec)
        explicit.update({"cloud_budget_seconds": 3600, "bootstrap": False})
        default_task, default_cp = assignment.render_task(copy.deepcopy(self.spec))
        explicit_task, explicit_cp = assignment.render_task(explicit)
        self.assertEqual(default_task, explicit_task)
        self.assertEqual(default_cp["session"], explicit_cp["session"])
        self.assertIn(b"Cloud budget: 3600 seconds.", default_task)

    def test_bootstrap_zero_budget_installs_new_owner_and_archives_prior_files(self):
        self.make_bootstrap_worktree()
        self.spec = self.network_bootstrap_spec()
        self.write_spec()
        with patch.object(assignment, "CORE_DIR", self.canonical):
            assignment.install(self.spec_path, self.coordination)
        current = (self.base / "CURRENT-TASK.md").read_bytes()
        self.assertIn(b"Owner: **Network**", current)
        self.assertIn(b"first task of a newly established owner", current)
        self.assertIn(b"Cloud budget: 0 seconds (no Cloud lane)", current)
        self.assertIn(b"no coordinator request, phase registration, Build submission", current)
        self.assertIn(b"Profile: none (no Cloud lane). New ledger path: none; previous closed ledger: none (bootstrap).", current)
        self.assertNotIn(b"register the exact phase", current)
        cpdata = checkpoint.validate(json.loads((self.base / "CHECKPOINT.json").read_text()))
        self.assertEqual(cpdata["owner"], "network")
        self.assertEqual((cpdata["session"]["budget_seconds"], cpdata["session"]["remaining_seconds"]), (0, 0))
        self.assertIsNone(cpdata["baseline"]["profile_sha256"])
        history = self.base / "task-history" / "networks-iteration-2026-10-07"
        manifest = json.loads((history / "manifest.json").read_text())
        self.assertEqual(set(manifest["files"]), {"STATUS.md", "AGENTS-COMPACT.md", "ROOT-AGENTS.md"})
        self.assertEqual((history / f"STATUS.md.{manifest['files']['STATUS.md']}").read_bytes(), b"old status\n")
        self.assertEqual((self.repo / "CLAUDE.md").read_text(), (self.canonical / "CLAUDE-COMPACT.md").read_text())
        self.assertEqual(self.ledger.read_bytes(), self.ledger_bytes)

    def test_bootstrap_refuses_worktree_with_prior_assignment_without_writes(self):
        self.spec = self.network_bootstrap_spec()
        self.write_spec()
        before = self.snapshot()
        with patch.object(assignment, "CORE_DIR", self.canonical):
            with self.assertRaisesRegex(assignment.AssignmentError, "bootstrap requires a worktree without CURRENT-TASK.md"):
                assignment.install(self.spec_path, self.coordination)
        self.assertEqual(self.snapshot(), before)

    def test_bootstrap_and_null_fields_require_zero_budget(self):
        for update, message in (
            ({"cloud_budget_seconds": 3600}, "bootstrap requires cloud_budget_seconds 0"),
            ({"owner": "merge", "cloud_budget_seconds": 3600}, "bootstrap requires cloud_budget_seconds 0"),
            ({"previous_ledger_path": self.previous_ledger_rel}, "bootstrap requires cloud_budget_seconds 0"),
            ({"owner": "merge"}, "bootstrap is only for owners without Cloud history"),
            ({"owner": "select-sort4"}, "bootstrap is only for owners without Cloud history"),
            ({"owner": "merge", "bootstrap": False, "cloud_budget_seconds": 3600}, "may be null only when cloud_budget_seconds is 0"),
            ({"profile_sha256": SHA256}, "both be set or both be null"),
            ({"cloud_budget_seconds": -1}, "must be 0 or a positive integer up to 86400"),
            ({"cloud_budget_seconds": 86401}, "must be 0 or a positive integer up to 86400"),
            ({"cloud_budget_seconds": True}, "must be 0 or a positive integer up to 86400"),
            ({"window": {"main_minutes": 120, "finish_minutes": 30, "max_timeout_seconds": 1200}}, "requires a Cloud budget"),
            ({"bootstrap": "yes"}, "bootstrap must be true or false"),
        ):
            spec = self.network_bootstrap_spec()
            spec.update(update)
            with self.subTest(update=update):
                with self.assertRaisesRegex(assignment.AssignmentError, message):
                    assignment.validate_spec(spec)

    def test_explicit_window_and_budget_render_and_bind_checkpoint(self):
        spec = copy.deepcopy(self.spec)
        spec.update({"cloud_budget_seconds": 21600, "window": {"main_minutes": 4320, "finish_minutes": 60}})
        task, cpdata = assignment.render_task(copy.deepcopy(spec))
        self.assertIn(("Cloud budget: 21600 seconds. Wall window: 4320 minutes main + 60 minutes closeout "
                       "(explicit window authorized by this task only; CORE main/closeout rules apply to these deadlines). "
                       "Per-Build timeout ≤1200 seconds; report reserve ≥240 seconds.").encode("utf-8"), task)
        self.assertEqual((cpdata["session"]["budget_seconds"], cpdata["session"]["remaining_seconds"]), (21600, 21600))
        self.assertEqual((cpdata["session"]["main_minutes"], cpdata["session"]["finish_minutes"]), (4320, 60))
        # A later ACTIVE checkpoint must use the explicit window, not the default one.
        active = copy.deepcopy(cpdata)
        active.update({"state": "ACTIVE"})
        active["session"].update({"t0": "2026-10-24T00:00:00Z", "main_deadline_utc": "2026-10-27T00:00:00Z",
                                  "deadline_utc": "2026-10-27T01:00:00Z"})
        checkpoint.validate(copy.deepcopy(active))
        active["session"]["main_deadline_utc"] = "2026-10-24T02:00:00Z"
        with self.assertRaisesRegex(checkpoint.CheckpointError, "4320 minutes"):
            checkpoint.validate(active)
        spec["window"]["max_timeout_seconds"] = 1500
        task, _ = assignment.render_task(copy.deepcopy(spec))
        self.assertIn("Per-Build timeout ≤1500 seconds".encode("utf-8"), task)
        # Default rendering stays byte-identical when no window is given; 1800 s budgets are plain values.
        plain = copy.deepcopy(self.spec)
        plain["cloud_budget_seconds"] = 1800
        plain_task, plain_cp = assignment.render_task(plain)
        self.assertIn(b"Cloud budget: 1800 seconds. Wall window: 120 minutes main + 30 minutes closeout. Per-Build timeout", plain_task)
        self.assertNotIn("main_minutes", plain_cp["session"])
        for bad in ({}, {"main_minutes": 240}, {"finish_minutes": 60}, {"main_minutes": 0, "finish_minutes": 30},
                    {"main_minutes": 10081, "finish_minutes": 30}, {"main_minutes": 120, "finish_minutes": 241},
                    {"main_minutes": 120, "finish_minutes": 30, "max_timeout_seconds": 1741},
                    {"main_minutes": 120, "finish_minutes": 30, "max_timeout_seconds": 59}, {"hours": 1}, "4320"):
            spec = copy.deepcopy(self.spec)
            spec["window"] = bad
            with self.subTest(window=bad), self.assertRaises(assignment.AssignmentError):
                assignment.validate_spec(spec)

    def test_network_cloud_lane_and_owner_without_lane(self):
        spec = self.network_bootstrap_spec()
        spec.update({"bootstrap": False, "cloud_budget_seconds": 3600, "profile_path": self.spec["profile_path"],
                     "profile_sha256": self.spec["profile_sha256"], "ledger_path": self.spec["ledger_path"]})
        self.assertEqual(assignment.validate_spec(copy.deepcopy(spec))["cloud_budget_seconds"], 3600)
        with patch.object(assignment, "CLOUD_OWNERS", {"merge", "select-sort4"}):
            with self.assertRaisesRegex(assignment.AssignmentError, "owner network has no Cloud lane"):
                assignment.validate_spec(copy.deepcopy(spec))

    def test_coordinator_envelopes_v2_v3_v4(self):
        self.write_spec()
        active = self.coordination / "active.json"
        for version, cap, accepted in ((4, 3, True), (3, 3, True), (2, 2, True), (4, 4, False), (3, 2, False), (5, 3, False)):
            active.write_text(json.dumps({"schema_version": version, "max_active": cap, "reservations": []}), encoding="utf-8")
            with self.subTest(version=version, cap=cap):
                if accepted:
                    with assignment._coordination_guard(OWNER, self.coordination):
                        pass
                else:
                    with self.assertRaisesRegex(assignment.AssignmentError, "unsupported coordinator envelope"):
                        with assignment._coordination_guard(OWNER, self.coordination):
                            pass
        active.write_text(json.dumps({"schema_version": 4, "max_active": 3, "reservations": [
            {"owner": OWNER, "ledger": "/tmp/old", "dispatch_token": "x"}]}), encoding="utf-8")
        with self.assertRaisesRegex(assignment.AssignmentError, "occupied or unresolved"):
            with assignment._coordination_guard(OWNER, self.coordination):
                pass

    def zero_budget_closed_task(self, budget_line=assignment.NO_CLOUD_BUDGET_LINE, commit=True):
        prefix = (f"# Prior zero-budget task\n\nTask ID: `{PREVIOUS}`; Owner: **Select/sort4**. Phase: `{OLD_PHASE}`.\n"
                  f"{budget_line} Wall window: 120 minutes main + 30 minutes closeout.\n\n").encode()
        oldcp = self.closed_checkpoint(hashlib.sha256(prefix).hexdigest())
        oldcp["session"].update({"budget_seconds": 0, "spent_seconds": 0, "retired_seconds": 0})
        (self.base / "CURRENT-TASK.md").write_bytes(prefix + checkpoint.REPORT_MARKER.encode() + b"\nclosed\n")
        (self.base / "CHECKPOINT.json").write_text(json.dumps(checkpoint.validate(oldcp)), encoding="utf-8")
        if commit:
            git(self.repo, "add", "research")
            git(self.repo, "commit", "-q", "-m", "closed zero-budget task")
        self.spec["previous_ledger_path"] = None
        self.write_spec()

    def test_followup_after_closed_zero_budget_task_needs_no_ledger(self):
        self.zero_budget_closed_task()
        with patch.object(assignment, "CORE_DIR", self.canonical):
            assignment.install(self.spec_path, self.coordination)
        current = (self.base / "CURRENT-TASK.md").read_bytes()
        self.assertIn(b"previous closed ledger: none (closed zero-budget task).", current)
        self.assertIn(b"Cloud budget: 3600 seconds.", current)

    def test_null_previous_ledger_refuses_prior_task_with_cloud_budget(self):
        self.zero_budget_closed_task()
        oldcp = json.loads((self.base / "CHECKPOINT.json").read_text())
        oldcp["session"].update({"budget_seconds": 3600, "retired_seconds": 3600})
        (self.base / "CHECKPOINT.json").write_text(json.dumps(oldcp), encoding="utf-8")
        git(self.repo, "commit", "-q", "-am", "checkpoint claims a Cloud budget")
        before = self.snapshot()
        with patch.object(assignment, "CORE_DIR", self.canonical):
            with self.assertRaisesRegex(assignment.AssignmentError, "closed zero-budget checkpoint"):
                assignment.install(self.spec_path, self.coordination)
        self.assertEqual(self.snapshot(), before)
        git(self.repo, "rm", "-q", "research/challenge-8/CHECKPOINT.json")
        git(self.repo, "commit", "-q", "-m", "no checkpoint")
        with self.assertRaisesRegex(assignment.AssignmentError, "closed zero-budget checkpoint"):
            assignment.install(self.spec_path, self.coordination)

    def test_null_previous_ledger_binds_zero_budget_to_granted_task_text(self):
        # A self-written zero-budget checkpoint cannot hide a task that granted Cloud seconds.
        self.zero_budget_closed_task(budget_line="Cloud budget: 3600 seconds.")
        before = self.snapshot()
        with patch.object(assignment, "CORE_DIR", self.canonical):
            with self.assertRaisesRegex(assignment.AssignmentError, "closed zero-budget checkpoint"):
                assignment.install(self.spec_path, self.coordination)
        self.assertEqual(self.snapshot(), before)

    def test_null_previous_ledger_refuses_smuggled_second_budget_line(self):
        self.zero_budget_closed_task(budget_line="Cloud budget: 3600 seconds.\n" + assignment.NO_CLOUD_BUDGET_LINE)
        with patch.object(assignment, "CORE_DIR", self.canonical):
            with self.assertRaisesRegex(assignment.AssignmentError, "closed zero-budget checkpoint"):
                assignment.install(self.spec_path, self.coordination)

    def test_null_previous_ledger_requires_committed_task_and_checkpoint(self):
        self.zero_budget_closed_task(commit=False)
        before = self.snapshot()
        with patch.object(assignment, "CORE_DIR", self.canonical):
            with self.assertRaisesRegex(assignment.AssignmentError, "match the assigned branch HEAD"):
                assignment.install(self.spec_path, self.coordination)
        self.assertEqual(self.snapshot(), before)

    def test_default_rendering_matches_pre_change_renderer_digest(self):
        # Digest of the CURRENT-TASK prefix produced by the renderer before zero-budget support. Re-derive:
        # `git show e6d9536a:research/challenge-8/agent-workflow/{assignment,checkpoint}.py` into a scratch
        # directory and call its render_task on this spec.
        spec = {"schema": assignment.SCHEMA, "task_id": "select4-next", "previous_task_id": "select4-closed-2026",
                "title": "Continue sort4 caller admission", "owner": "select-sort4", "runtime": "claude",
                "worktree": "/fixture/worktree", "branch": "select4-next",
                "baseline_sha": "a" * 40, "source_sha": "a" * 40, "tool_sha": "c" * 40,
                "tool_worktree": "/fixture/tool", "tool_branch": "verifast-review",
                "profile_path": "research/challenge-8/profiles/select.json", "profile_sha256": "b" * 64,
                "phase": "SORT4-ACTUAL-CALLER", "lane": "select-sort4",
                "ledger_path": "research/challenge-8/new/BUDGET.json",
                "previous_ledger_path": "research/challenge-8/old/BUDGET.json",
                "goal": "Establish the exact admitted caller path.", "steps": ["Inspect caller admission"],
                "special_bounds": [], "references": [{"title": "Plan", "path": "research/challenge-8/PLAN.md"}],
                "handoff": {"confirmed": [], "open": ["actual invocation remains NOT_RUN"],
                            "blocker": {"summary": "caller admission remains open", "evidence": []},
                            "rejected": [], "next_step": "Inspect.", "artifacts": []}}
        _task, generated = assignment.render_task(spec)
        self.assertEqual(generated["assignment_sha256"], "33bd33df4251ff22f0e3edb485a54fbe711d78b2d6fff0b8719957122d982c71")


if __name__ == "__main__":
    unittest.main()
