#!/usr/bin/env python3
"""Synthetic R16 phase and publisher-boundary checks; no Cloud calls."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import tempfile
import hashlib
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0]))
spec = importlib.util.spec_from_file_location("r16_control", HERE.parents[0] / "control.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def ledger():
    return {
        "phase": m.R16_PHASE, "owner": "merge", "authorization_model": "bounded-cloud-budget",
        "status": "AUTHORIZED", "allowed_lanes": ["merge"], "ceiling_build_seconds": 3600,
        "used_build_seconds": 0, "remaining_build_seconds": 3600, "max_builds": None,
        "max_timeout_seconds": 1200, "builds": [], "active_build": None,
        "start_utc": "2026-10-21T16:08:24Z", "main_deadline_utc": "2026-10-21T18:08:24Z",
        "deadline_utc": "2026-10-21T18:38:24Z", "carryover_allowed": False,
        "publication_gate_path": m.R14_GATE_PATH, "authorization": "CURRENT-TASK R16",
    }


def args(**overrides):
    values = {"phase_id": m.R16_PHASE, "owner": "merge", "ledger": HERE / ledger_name(),
              "command": "submit", "infra_sha": "a" * 40, "proof_sha": "a" * 40,
              "lane": "merge", "timeout": 1200, "source_mode": "pinned-objects"}
    values.update(overrides)
    return type("Args", (), values)()


def ledger_name():
    return m.R16_LEDGER_PATH.rsplit("/", 1)[-1]


class R16PhaseTests(unittest.TestCase):
    def setUp(self):
        real = m.datetime.datetime
        class Frozen(real):
            @classmethod
            def now(cls, tz=None): return real.fromisoformat("2026-10-21T17:00:00+00:00")
        self.clock = patch.object(m.datetime, "datetime", Frozen)
        self.clock.start()
        self.addCleanup(self.clock.stop)

    def authorize(self, account=None, value=None):
        with patch.object(m, "r14_read_selected_gate") as gate, \
             patch.object(m, "r16_validate_sources") as source:
            deadline = m.authorized_phase(args() if value is None else value,
                                          ledger() if account is None else account)
            if (args() if value is None else value).command == "submit":
                gate.assert_called_once_with("a" * 40)
                source.assert_called_once_with(m.R16_PROBE_SOURCE, "a" * 40)
            return deadline

    def test_authorized_phase_keeps_r13_upload_guard(self):
        self.authorize()
        self.authorize(value=args(command="request"))
        self.assertIs(m.required_upload_guard(m.R16_PHASE), True)
        self.assertIs(m.required_upload_guard(m.R15_PHASE), True)
        self.assertIs(m.required_upload_guard(m.R14_PHASE), True)
        cfg = m.config("a" * 40, "a" * 40, "merge", 1200, "synthetic-r16-token",
                       source_payload=None, r13_required=m.required_upload_guard(m.R16_PHASE))
        self.assertEqual(cfg["timeout"], "1200s")
        self.assertIn("R13_UPLOAD_REQUIRED=true", cfg["steps"][0]["env"])

    def test_phase_owner_deadline_budget_and_ledger_fields_fail_closed(self):
        for field, bad in (
            ("phase", "MERGE-OTHER"), ("owner", "select"), ("authorization_model", "time-window"),
            ("ceiling_build_seconds", 3601), ("allowed_lanes", ["select"]),
            ("start_utc", "2026-10-21T16:08:25Z"),
            ("main_deadline_utc", "2026-10-21T18:08:25Z"),
            ("deadline_utc", "2026-10-21T18:38:25Z"), ("max_timeout_seconds", 1201),
            ("carryover_allowed", True), ("publication_gate_path", "other"),
            ("max_builds", 1), ("remaining_build_seconds", 3599), ("active_build", False),
            ("builds", [{"owner": "select", "phase_id": m.R16_PHASE}]),
        ):
            account = ledger(); account[field] = bad
            with self.subTest(field=field), self.assertRaises(SystemExit): self.authorize(account)
        for missing in ("publication_gate_path", "builds", "remaining_build_seconds", "used_build_seconds", "active_build"):
            account = ledger(); account.pop(missing)
            with self.subTest(missing=missing), self.assertRaises(SystemExit): self.authorize(account)

    def test_phase_identity_source_mode_and_absolute_deadline_fail_closed(self):
        for value in (args(phase_id="MERGE-OTHER"), args(owner="select"),
                      args(source_mode="public-git"), args(infra_sha="b" * 40),
                      args(timeout=1201), args(timeout=509), args(lane="smoke-success")):
            with self.subTest(value=value.__dict__), self.assertRaises(SystemExit): self.authorize(value=value)
        for field in ("r14_read_selected_gate", "r16_validate_sources"):
            with patch.object(m, field, side_effect=SystemExit("closed")), self.assertRaises(SystemExit):
                m.authorized_phase(args(), ledger())
        real = m.datetime.datetime
        class Late(real):
            @classmethod
            def now(cls, tz=None): return real.fromisoformat("2026-10-21T18:08:24+00:00")
        with patch.object(m.datetime, "datetime", Late), self.assertRaises(SystemExit):
            self.authorize()
        class NearCutoff(real):
            @classmethod
            def now(cls, tz=None): return real.fromisoformat("2026-10-21T18:17:25+00:00")
        with patch.object(m.datetime, "datetime", NearCutoff), self.assertRaises(SystemExit):
            self.authorize()

    def test_preparation_crossing_main_deadline_fails_final_reservation_recheck(self):
        source = (HERE.parents[0] / "control.py").read_text()
        final_check = source.rfind("R14_PHASE,R15_PHASE,R16_PHASE")
        reservation = source.rfind("coordination.reserve(reservation)")
        self.assertGreater(final_check, 0)
        self.assertLess(final_check, reservation)
        real = m.datetime.datetime
        current = [real.fromisoformat("2026-10-21T18:08:23+00:00")]

        class MovingClock(real):
            @classmethod
            def now(cls, tz=None): return current[0]

        with patch.object(m.datetime, "datetime", MovingClock):
            self.authorize()  # authorization succeeds when preparation starts
            current[0] = real.fromisoformat("2026-10-21T18:08:24+00:00")
            with self.assertRaises(SystemExit):
                self.authorize()  # final pre-reservation recheck rejects the expired main window

    def test_source_validators_crossing_deadlines_fail_inside_final_authorization(self):
        real = m.datetime.datetime
        before, during = "2026-10-21T18:07:00+00:00", "2026-10-21T18:08:24+00:00"
        current = [real.fromisoformat(before)]

        class ValidatorClock(real):
            @classmethod
            def now(cls, tz=None): return current[0]

        def slow_source(*_args):
            current[0] = real.fromisoformat(during)

        with patch.object(m.datetime, "datetime", ValidatorClock), \
             patch.object(m, "r14_read_selected_gate") as gate, \
             patch.object(m, "r16_validate_sources", side_effect=slow_source) as source:
            with self.assertRaises(SystemExit):
                m.authorized_phase(args(), ledger())
            gate.assert_called_once_with("a" * 40)
            source.assert_called_once_with(m.R16_PROBE_SOURCE, "a" * 40)

    def test_final_deadline_check_includes_absolute_timeout_and_queue_reserve(self):
        real = m.datetime.datetime
        class NearAbsolute(real):
            @classmethod
            def now(cls, tz=None): return real.fromisoformat("2026-10-21T18:17:25+00:00")
        synthetic = ledger()
        synthetic["main_deadline_utc"] = "2026-10-21T18:30:00Z"
        with patch.object(m.datetime, "datetime", NearAbsolute), self.assertRaises(SystemExit):
            m.r16_final_deadline_check(args(timeout=1200), synthetic)

    def test_execute_budget_has_420_second_reserve_and_780_second_cap(self):
        source = (HERE.parents[0] / "control.py").read_text()
        self.assertIn("if a.phase_id==R16_PHASE:r16_validate_execute_budget(cfg,a.timeout)", source)
        for timeout, expected in ((510, 90), (1200, 780)):
            cfg = m.config("a" * 40, "a" * 40, "merge", timeout, "synthetic-budget-token")
            self.assertEqual(m.r16_validate_execute_budget(cfg, timeout), expected)
            body = cfg["steps"][0]["args"][1]
            self.assertIn(f'"{expected}s" bash', body)
            self.assertIn(f" + {expected} - 15 ", body)
        for timeout in (90, 419, 509, 1201, True, "1200"):
            with self.subTest(timeout=timeout), self.assertRaises(SystemExit):
                m.r16_validate_execute_budget({}, timeout)
        cfg = m.config("a" * 40, "a" * 40, "merge", 1200, "synthetic-budget-token")
        cfg["steps"][0]["args"][1] = cfg["steps"][0]["args"][1].replace('"1130s" bash', '"1129s" bash')
        with self.assertRaises(SystemExit): m.r16_validate_execute_budget(cfg, 1200)

    def test_selected_blob_and_mode_mismatch_refuse(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); target = root / "input.py"; target.write_bytes(b"selected")
            oid = hashlib.sha1(b"blob 8\0selected").hexdigest()
            with patch.object(m, "ROOT", root):
                m.r16_validate_worktree_entry("input.py", "100644", oid)
                with self.assertRaises(SystemExit): m.r16_validate_worktree_entry("input.py", "100644", "0" * 40)
                with self.assertRaises(SystemExit): m.r16_validate_worktree_entry("input.py", "100755", oid)

    def test_r14_publisher_config_and_upload_shell_are_preserved(self):
        probe = __import__("subprocess").check_output(
            ["git", "show", f"{m.R14_PROBE_SOURCE}:research/challenge-8/cloud-build/control.py"]
        ).decode()
        selected = (HERE.parents[0] / "control.py").read_text()
        m.r14_validate_publisher_control(probe, selected)
        mutated = selected.replace("CLOUDSDK_STORAGE_PARALLEL_COMPOSITE_UPLOAD_ENABLED=False",
                                   "CLOUDSDK_STORAGE_PARALLEL_COMPOSITE_UPLOAD_ENABLED=True", 1)
        with self.assertRaises(SystemExit): m.r14_validate_publisher_control(probe, mutated)
        gate = __import__("json").loads((HERE / "R14-PUBLICATION-GATE-20261021.json").read_bytes())
        m.r14_validate_gate_record(gate)
        self.assertEqual(m.R14_UPLOAD_SHELL_SHA256,
                         "677740c98b0389c77c40804a825037b598c46c095fc0fecd9a30b80c5922ef64")


if __name__ == "__main__":
    unittest.main()
