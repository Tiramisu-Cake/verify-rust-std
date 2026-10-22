"""Isolated synthetic authority/accounting tests; never invoke Cloud/Codex."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import checkpoint as cp
import watch_bindings as wb


BUILD = "12345678-1234-4234-8234-123456789abc"
THREAD = "12345678-1234-4234-8234-123456789def"
TOKEN = "dispatch-" + "c" * 32


class BindingFixture:
    """Temporary committed repo + fake coordinator, also used by integration tests."""
    def __init__(self, base):
        self.root = Path(base) / "worktree"
        self.root.mkdir()
        self.coord = Path(base) / "coordinator"
        self.coord.mkdir()
        (self.coord / "receipts").mkdir()
        (self.coord / "lock").touch()
        self.ledger_relative = "research/challenge-8/cloud-build/budget.json"
        self.ledger_path = self.root / self.ledger_relative
        self.ledger_path.parent.mkdir(parents=True)
        for file in (wb.CLIENT, wb.COORD):
            (self.root / file).write_text("# synthetic metadata client\n")
        self.git("init", "-q", "-b", "test-owner")
        self.git("config", "user.email", "synthetic@example.invalid")
        self.git("config", "user.name", "Synthetic test")
        self.git("remote", "add", "origin", "https://github.com/Tiramisu-Cake/verify-rust-std.git")
        self.git("add", wb.CLIENT, wb.COORD)
        self.git("commit", "-qm", "synthetic clients")
        sha = self.git("rev-parse", "HEAD").strip()
        prefix = b"# Synthetic task\n\nOriginal authority only.\n\n"
        (self.root / wb.TASK).write_bytes(prefix + cp.REPORT_MARKER.encode() + b"\nWAITING\n")
        self.checkpoint = {
            "schema": cp.SCHEMA, "task_id": "synthetic-select", "owner": "select-sort4",
            "phase": "synthetic-phase", "state": "HANDOFF", "updated_utc": "2026-10-21T10:00:00Z",
            "assignment_sha256": hashlib.sha256(prefix).hexdigest(),
            "baseline": {"source_sha": sha, "tool_sha": sha, "profile_sha256": None},
            "session": {"t0": "2026-10-21T09:00:00Z", "main_deadline_utc": "2026-10-21T11:00:00Z",
                        "deadline_utc": "2026-10-21T11:30:00Z", "budget_seconds": 3600,
                        "spent_seconds": 0, "retired_seconds": 0, "remaining_seconds": 3600,
                        "active_build_ids": [BUILD], "unresolved_ids": []},
            "confirmed": [], "open": ["Proof remains UNKNOWN"],
            "blocker": {"summary": "Waiting", "evidence": []}, "rejected": [],
            "next_step": "Read Brief after terminal", "artifacts": [],
        }
        self.item = {
            "build_id": BUILD, "dispatch_token": TOKEN, "owner": "select-sort4", "phase_id": "synthetic-phase",
            "infra_sha": sha, "proof_sha": sha, "lane": "sort4", "submitted_config_sha256": "a" * 64,
            "source_mode": "git", "source_input_sha256": None,
            "timeout_seconds": 600, "reserved_seconds": 600, "status": "WORKING", "accounted": False,
        }
        self.ledger = {
            "status": "AUTHORIZED", "owner": "select-sort4", "phase": "synthetic-phase",
            "phase_id": "synthetic-phase", "task_id": "synthetic-select",
            "start_utc": self.checkpoint["session"]["t0"],
            "main_deadline_utc": self.checkpoint["session"]["main_deadline_utc"],
            "deadline_utc": self.checkpoint["session"]["deadline_utc"],
            "ceiling_build_seconds": 3600, "used_build_seconds": 0, "spent_build_seconds": 0,
            "remaining_build_seconds": 3600, "retired_seconds": 0, "allowed_lanes": ["sort4"],
            "active_build": BUILD, "builds": [self.item],
        }
        self.reservation = {"owner": "select-sort4", "ledger": str(self.ledger_path), "phase_id": "synthetic-phase",
                            "dispatch_token": TOKEN, "build_id": BUILD}
        self.write(self.root / wb.CHECKPOINT, self.checkpoint)
        self.save()
        self.spec = {"worktree": str(self.root), "ledger_path": self.ledger_relative,
                     "thread_id": THREAD, "build_id": BUILD}

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.root), "-c", "core.hooksPath=/dev/null", *args], text=True, stderr=subprocess.PIPE)

    @staticmethod
    def write(path, value):
        Path(path).write_text(json.dumps(value, sort_keys=True))

    def save(self, reservation=True):
        self.write(self.ledger_path, self.ledger)
        self.write(self.coord / "active.json", {"schema_version": 3, "max_active": 3,
                                               "reservations": [self.reservation] if reservation else []})

    def terminal(self, accounted=True):
        self.item.update(status="SUCCESS", accounted=accounted)
        self.item["duration_seconds"] = 123
        if accounted:
            self.ledger.update(active_build=None, used_build_seconds=123, remaining_build_seconds=3477)
        self.write(self.coord / "receipts" / (TOKEN + ".json"), dict(self.reservation, status="SUCCESS"))
        self.save(reservation=False)

    def patches(self):
        return (patch.object(wb, "OWNER_REPOS", {"select-sort4": (self.root, "test-owner")}),
                patch.object(wb, "COORDINATION", self.coord))


class BindingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.f = BindingFixture(self.tmp.name)
        for mock in self.f.patches():
            mock.start()
            self.addCleanup(mock.stop)
        self.addCleanup(self.tmp.cleanup)
        self.binding = wb.capture(self.f.spec)

    def test_capture_exact_handoff_and_status_only_no_writes(self):
        before = {p: p.read_bytes() for p in (self.f.ledger_path, self.f.root / wb.CHECKPOINT, self.f.coord / "active.json")}
        self.assertEqual(wb.validate(self.binding), {"terminal": False, "status": "WORKING", "accounted": False})
        self.assertEqual(self.binding["build_id"], BUILD)
        self.assertEqual(self.binding["thread_id"], THREAD)
        for path, data in before.items():
            self.assertEqual(path.read_bytes(), data)

    def test_ordinary_terminal_accounting_does_not_invalidate(self):
        self.f.terminal()
        result = wb.validate(self.binding)
        self.assertEqual(result, {"terminal": True, "status": "SUCCESS", "accounted": True})
        self.assertNotIn("verification_accepted", result)
        self.assertEqual(self.f.ledger["spent_build_seconds"], 0)  # Historical alias is preserved.

    def test_terminal_receipt_before_own_accounting_is_not_accepted(self):
        self.f.terminal(accounted=False)
        self.assertEqual(wb.validate(self.binding), {"terminal": True, "status": "SUCCESS", "accounted": False})

    def test_freezes_checkpoint_and_assignment_bytes(self):
        path = self.f.root / wb.CHECKPOINT
        original = path.read_bytes()
        path.write_bytes(original + b"\n")
        with self.assertRaises(wb.BindingError):
            wb.validate(self.binding)
        path.write_bytes(original)
        task = self.f.root / wb.TASK
        task.write_bytes(task.read_bytes().replace(b"Original", b"Replaced"))
        with self.assertRaises(wb.BindingError):
            wb.validate(self.binding)

    def test_envelope_v3_or_v4_with_three_slots_only(self):
        active = self.f.coord / "active.json"
        envelope = json.loads(active.read_text())
        for version, cap, accepted in ((4, 3, True), (3, 3, True), (4, 4, False), (2, 2, False), (5, 3, False),
                                       ([4], 3, False), (4.0, 3, False), (True, 3, False), (4, {}, False)):
            active.write_text(json.dumps(dict(envelope, schema_version=version, max_active=cap)))
            with self.subTest(version=version, cap=cap):
                if accepted:
                    self.assertEqual(wb.validate(self.binding)["status"], "WORKING")
                else:
                    with self.assertRaises(wb.BindingError):
                        wb.validate(self.binding)
        active.write_text(json.dumps(envelope))

    def test_closed_or_moved_account_refuses(self):
        for mutation in ({"status": "CLOSED"}, {"phase": "another"}, {"task_id": "another"},
                         {"ceiling_build_seconds": 4000, "remaining_build_seconds": 4000}, {"owner": "merge"},
                         {"start_utc": "2026-10-21T08:00:00Z"}):
            original = copy.deepcopy(self.f.ledger)
            self.f.ledger.update(mutation)
            self.f.save()
            with self.subTest(mutation=mutation), self.assertRaises(wb.BindingError):
                wb.validate(self.binding)
            self.f.ledger = original
        self.f.save()

    def test_config_source_dispatch_and_reservation_mismatch_refuse(self):
        for key, value in (("submitted_config_sha256", "b" * 64), ("infra_sha", "d" * 40),
                           ("dispatch_token", "dispatch-" + "d" * 32), ("owner", "merge")):
            old = self.f.item[key]
            self.f.item[key] = value
            self.f.save()
            with self.subTest(key=key), self.assertRaises(wb.BindingError):
                wb.validate(self.binding)
            self.f.item[key] = old
        self.f.reservation["ledger"] = "/tmp/foreign.json"
        self.f.save()
        with self.assertRaises(wb.BindingError):
            wb.validate(self.binding)

    def test_unknown_build_and_second_pending_refuse(self):
        self.f.ledger["builds"].append(dict(self.f.item, build_id=THREAD))
        self.f.save()
        with self.assertRaises(wb.BindingError):
            wb.validate(self.binding)
        self.f.ledger["builds"] = []
        self.f.save()
        with self.assertRaises(wb.BindingError):
            wb.validate(self.binding)

    def test_pinned_committed_status_client_and_branch(self):
        client = self.f.root / wb.CLIENT
        original = client.read_bytes()
        client.write_bytes(original + b"# dirty\n")
        with self.assertRaises(wb.BindingError):
            wb.validate(self.binding)
        self.f.git("add", wb.CLIENT)
        self.f.git("commit", "-qm", "changed client")
        with self.assertRaises(wb.BindingError):
            wb.validate(self.binding)
        client.write_bytes(original)
        self.f.git("checkout", "-qb", "foreign")
        with self.assertRaises(wb.BindingError):
            wb.validate(self.binding)

    def test_paths_symlinks_caps_and_invalid_json_refuse(self):
        for ledger in ("../budget.json", self.f.ledger_relative + "/../budget.json", "research/challenge-8/cloud-build//budget.json"):
            with self.subTest(ledger=ledger), self.assertRaises(wb.BindingError):
                wb.capture(dict(self.f.spec, ledger_path=ledger))
        original = self.f.ledger_path.read_bytes()
        self.f.ledger_path.unlink()
        outside = Path(self.tmp.name) / "outside.json"
        outside.write_bytes(original)
        self.f.ledger_path.symlink_to(outside)
        with self.assertRaises(wb.BindingError):
            wb.validate(self.binding)
        self.f.ledger_path.unlink()
        self.f.ledger_path.write_bytes(b"null")
        with self.assertRaises(wb.BindingError):
            wb.validate(self.binding)
        self.f.ledger_path.write_bytes(b"x" * (128 * 1024 + 1))
        with self.assertRaises(wb.BindingError):
            wb.validate(self.binding)

    def test_missing_or_foreign_receipt_refuses(self):
        self.f.save(reservation=False)
        with self.assertRaises(wb.BindingError):
            wb.validate(self.binding)
        self.f.write(self.f.coord / "receipts" / (TOKEN + ".json"), dict(self.f.reservation, owner="merge", status="SUCCESS"))
        with self.assertRaises(wb.BindingError):
            wb.validate(self.binding)

    def test_poll_runs_only_existing_status_and_accepts_its_accounting(self):
        original_run = wb._run
        seen = []
        def run(argv, **kwargs):
            if argv[0] == "git":
                return original_run(argv, **kwargs)
            seen.append(argv)
            self.f.terminal()
            return json.dumps({"id": BUILD, "status": "SUCCESS"}).encode()
        state = Path(self.tmp.name) / "private-client-state"
        with patch.object(wb, "_run", side_effect=run):
            result = wb.poll(self.binding, state)
        self.assertTrue(result["accounted"])
        self.assertEqual(seen, [[sys.executable, str(self.f.root / wb.CLIENT), "--owner", "select-sort4", "--phase-id", "synthetic-phase", "--ledger", str(self.f.ledger_path), "--state-dir", str(state), "status", BUILD]])
        self.assertEqual(state.stat().st_mode & 0o777, 0o700)

    def test_poll_missing_null_wrongtype_mismatch_and_timeout(self):
        original_run = wb._run
        for response in (b"{}", b"null", b"[]", b'{"id":null,"status":"SUCCESS"}',
                         json.dumps({"id": THREAD, "status": "SUCCESS"}).encode(),
                         json.dumps({"id": BUILD, "status": "SUCCESS"}).encode(), b"invalid"):
            def run(argv, **kwargs):
                return original_run(argv, **kwargs) if argv[0] == "git" else response
            with self.subTest(response=response), patch.object(wb, "_run", side_effect=run), self.assertRaises(wb.PollError):
                wb.poll(self.binding, Path(self.tmp.name) / "private-state")
        def timeout(argv, **kwargs):
            if argv[0] == "git":
                return original_run(argv, **kwargs)
            raise wb.PollError("synthetic timeout")
        with patch.object(wb, "_run", side_effect=timeout), self.assertRaises(wb.PollError):
            wb.poll(self.binding, Path(self.tmp.name) / "private-state")

    def test_output_cap_and_process_timeout_are_bounded(self):
        with self.assertRaises(wb.PollError):
            wb._run([sys.executable, "-c", "print('x'*10000)"], cap=128)
        with self.assertRaises(wb.PollError):
            wb._run([sys.executable, "-c", "import time; time.sleep(2)"], timeout=.05)


class OwnerRepositoryTests(unittest.TestCase):
    def test_owner_repositories(self):
        self.assertEqual(wb.OWNER_REPOS, {
            "merge": (Path("/root/verify-rust-std-merge-origin"), "merge/incoming-origin-20261009"),
            "select-sort4": (Path("/root/verify-rust-std-select-night"), "research/night-select-sort4-cloud-2026-10-09"),
            "network": (Path("/root/verify-rust-std-networks"), "challenge-8/networks"),
        })


if __name__ == "__main__":
    unittest.main()
