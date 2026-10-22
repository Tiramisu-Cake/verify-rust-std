"""Synthetic R20 callee-lane registration checks with an injected clock; no Cloud dispatch."""
from __future__ import annotations

import base64
import hashlib
import importlib.util
import json
import lzma
from pathlib import Path
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
CLOUD = HERE.parent
PREFIX = "research/challenge-8/cloud-build/sort4-caller-entry-native/"
LEDGER = HERE / "BUDGET-A1-ACTUAL-SELECT-2026-10-22-R20.json"
PHASE = "SORT4-ACTUAL-SELECT-2026-10-22-R20"
INSIDE = "2026-10-22T16:30:00Z"
LANE = "o26-select-callee-r20"
RECOVERY_LANE = "o26-sort4-c1-current-recovery"

sys.path.insert(0, str(CLOUD))
spec = importlib.util.spec_from_file_location("r20_registration_control", CLOUD / "control.py")
CONTROL = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = CONTROL
spec.loader.exec_module(CONTROL)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def clock(text):
    import datetime as real
    fixed = real.datetime.fromisoformat(text.replace("Z", "+00:00"))

    class Fixed(real.datetime):
        @classmethod
        def now(cls, tz=None):
            return fixed if tz is not None else fixed.replace(tzinfo=None)

        @classmethod
        def utcnow(cls):
            return fixed.replace(tzinfo=None)
    return SimpleNamespace(datetime=Fixed, timezone=real.timezone,
                           timedelta=real.timedelta)


def at(text):
    return patch.object(CONTROL, "datetime", clock(text))


def authorized_ledger():
    return {
        "phase": PHASE,
        "phase_id": PHASE,
        "status": "AUTHORIZED",
        "authorization": "synthetic isolated registration test",
        "owner": "select-sort4",
        "task_id": "select-actual-callee-autonomous-2026-10-22-r20",
        "ceiling_build_seconds": 3600,
        "allowed_lanes": [LANE],
        "start_utc": "2026-10-22T15:41:28Z",
        "main_deadline_utc": "2026-10-22T17:41:28Z",
        "deadline_utc": "2026-10-22T18:11:28Z",
        "maximum_builds": None,
        "maximum_build_timeout_seconds": 1200,
        "report_reserve_seconds": 240,
    }


class R20CalleeRegistration(unittest.TestCase):
    def test_phase_window_and_lane(self):
        self.assertEqual(CONTROL.A1_R20_PHASE, PHASE)
        self.assertEqual((CONTROL.A1_R20_START, CONTROL.A1_R20_MAIN_DEADLINE,
                          CONTROL.A1_R20_DEADLINE, CONTROL.A1_R20_CEILING),
                         ("2026-10-22T15:41:28Z", "2026-10-22T17:41:28Z",
                          "2026-10-22T18:11:28Z", 3600))
        self.assertEqual(CONTROL.A1_R20_LANES, {LANE})
        recipe = json.loads((CLOUD / "recipes" / (LANE + ".json")).read_text())
        self.assertEqual(recipe["lane"], LANE)

    def test_committed_ledger_is_exact_fresh_r20_account(self):
        ledger = json.loads(LEDGER.read_text())
        self.assertEqual((ledger["phase"], ledger["phase_id"], ledger["status"]),
                         (PHASE, PHASE, "AUTHORIZED"))
        self.assertEqual((ledger["ceiling_build_seconds"], ledger["carry_seconds"]), (3600, 0))
        used = sum(b["build_seconds"] for b in ledger["builds"] if b.get("accounted"))
        self.assertEqual(ledger["used_build_seconds"], used)
        self.assertEqual(ledger["remaining_build_seconds"] + used, 3600)
        for key, value in authorized_ledger().items():
            if key not in ("authorization",):
                self.assertEqual(ledger[key], value, key)

    def test_exact_account_required(self):
        args = SimpleNamespace(phase_id=PHASE, owner="select-sort4")
        with at(INSIDE):
            CONTROL.authorized_phase(args, authorized_ledger())
        mismatches = (
            {"owner": "other"}, {"start_utc": "2026-10-22T15:41:29Z"},
            {"main_deadline_utc": "2026-10-22T17:41:29Z"},
            {"deadline_utc": "2026-10-22T18:11:29Z"},
            {"deadline_utc": "2026-10-22T18:11:27Z"},
            {"maximum_build_timeout_seconds": 1201}, {"maximum_builds": 1},
            {"allowed_lanes": [RECOVERY_LANE]}, {"allowed_lanes": [LANE, RECOVERY_LANE]},
            {"ceiling_build_seconds": 3601}, {"report_reserve_seconds": 239},
            {"status": "CLOSED"}, {"phase": "SORT4-ACTUAL-C3-2026-10-22-R19"},
        )
        for delta in mismatches:
            with self.subTest(delta=delta), at(INSIDE), self.assertRaises(SystemExit):
                CONTROL.authorized_phase(args, dict(authorized_ledger(), **delta))
        with at("2026-10-22T18:11:29Z"), self.assertRaises(SystemExit):
            CONTROL.authorized_phase(args, authorized_ledger())

    def test_environment_is_phase_marker_on_callee_lane_only(self):
        def forbidden(*_a, **_k):
            raise AssertionError("profile read for callee lane")
        with patch.object(CONTROL.subprocess, "check_output", forbidden):
            env = CONTROL.envs("a" * 40, "b" * 40, LANE, PHASE)
        self.assertIn("SORT4_R20_CALLEE_PHASE_ID=" + PHASE, env)
        self.assertIn("LANE=" + LANE, env)
        self.assertFalse(any(x.startswith("SORT4_A1_") for x in env))
        with self.assertRaises(SystemExit):
            CONTROL.envs("a" * 40, "b" * 40, RECOVERY_LANE, PHASE)

    def test_timeout_budget_and_source_restore(self):
        config = CONTROL.config("a" * 40, "b" * 40, LANE, 1200, "token", phase_id=PHASE)
        self.assertEqual(config["timeout"], "1200s")
        for invalid in (269, 1201):
            with self.subTest(seconds=invalid), self.assertRaises(ValueError):
                CONTROL.config("a" * 40, "b" * 40, LANE, invalid, "token", phase_id=PHASE)
        payload = b"synthetic R20 source payload\x00"
        encoded, command = CONTROL.source_restore_transport(payload, PHASE)
        self.assertEqual(lzma.decompress(base64.b64decode(encoded)), payload)

    def test_submit_main_deadline_and_timeout_refuse_before_dispatch(self):
        def forbidden(*_args, **_kwargs):
            raise AssertionError("Cloud/coordinator reached")
        cases = (("2026-10-22T17:41:28Z", 1200, "main window ended"),
                 ("2026-10-22T16:30:00Z", 269, "timeout must be270..1200"),
                 ("2026-10-22T16:30:00Z", 1201, "timeout must be270..1200"))
        for now, timeout, reason in cases:
            args = SimpleNamespace(command="submit", phase_id=PHASE, owner="select-sort4",
                                   timeout=timeout, lane=LANE, source_mode="pinned-objects",
                                   infra_sha="a" * 40, proof_sha="a" * 40)
            with self.subTest(now=now, timeout=timeout), at(now), \
                    patch.object(CONTROL, "invoke", forbidden), \
                    patch.object(CONTROL.coordination, "request", forbidden), \
                    self.assertRaisesRegex(SystemExit, reason):
                CONTROL.run_command(args, None, authorized_ledger(), None)

    def test_r19_registration_unchanged(self):
        self.assertEqual((CONTROL.A1_R19_START, CONTROL.A1_R19_DEADLINE),
                         ("2026-10-22T13:50:26Z", "2026-10-22T16:20:26Z"))


if __name__ == "__main__":
    unittest.main()
