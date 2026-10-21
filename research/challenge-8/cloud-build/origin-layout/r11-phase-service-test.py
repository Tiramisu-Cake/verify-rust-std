#!/usr/bin/env python3
"""Synthetic R11 phase authorization and fresh-ledger boundary checks."""
from __future__ import annotations

import ast
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parents[0]))
spec = importlib.util.spec_from_file_location("r11_phase_control", ROOT / "cloud-build" / "control.py")
if spec is None or spec.loader is None:
    raise RuntimeError("cloud build control module is unavailable")
control = importlib.util.module_from_spec(spec)
spec.loader.exec_module(control)

LEDGER_PATH = HERE / "CURRENT-RECOVERY-R11-BUDGET-20261021.json"
PHASE_ID = "MERGE-LABEL-STORAGE-INVARIANT-R11-2026-10-21"
START_UTC = "2026-10-21T06:14:39Z"
MAIN_DEADLINE_UTC = "2026-10-21T08:14:39Z"
DEADLINE_UTC = "2026-10-21T08:44:39Z"
IN_WINDOW_NOW = "2026-10-21T06:30:00+00:00"


def account():
    return {
        "phase": PHASE_ID, "owner": "merge", "authorization_model": "bounded-cloud-budget",
        "status": "AUTHORIZED", "allowed_lanes": ["merge"],
        "ceiling_build_seconds": 3600, "used_build_seconds": 0,
        "remaining_build_seconds": 3600, "builds": [], "active_build": None,
        "start_utc": START_UTC, "main_deadline_utc": MAIN_DEADLINE_UTC,
        "deadline_utc": DEADLINE_UTC, "max_timeout_seconds": 1200,
        "authorization": "synthetic authorized R11 account", "carryover_allowed": False,
    }


def args(**changes):
    values = dict(phase_id=PHASE_ID, ledger=LEDGER_PATH, owner="merge",
                  command="submit", timeout=1200, lane="merge", source_mode="pinned-objects")
    values.update(changes)
    return SimpleNamespace(**values)


def authorize(arguments, ledger, instant=IN_WINDOW_NOW):
    real_datetime = control.datetime.datetime

    class FrozenDateTime(real_datetime):
        @classmethod
        def now(cls, tz=None):
            value = real_datetime.fromisoformat(instant)
            return value if tz is None else value.astimezone(tz)

    with patch.object(control.datetime, "datetime", FrozenDateTime):
        return control.authorized_phase(arguments, ledger)


class R11PhaseTests(unittest.TestCase):
    def test_exact_fresh_phase_account_and_authorized_timeout(self):
        registered = json.loads(LEDGER_PATH.read_text())
        synthetic = account()
        for key in ("phase", "owner", "authorization_model", "allowed_lanes",
                    "ceiling_build_seconds", "start_utc", "main_deadline_utc",
                    "deadline_utc", "max_timeout_seconds", "status", "carryover_allowed"):
            self.assertEqual(registered[key], synthetic[key])
        self.assertEqual(registered["used_build_seconds"], 0)
        self.assertEqual(registered["remaining_build_seconds"], 3600)
        self.assertEqual(registered["builds"], [])
        self.assertIsNone(registered["active_build"])
        self.assertEqual(authorize(args(), synthetic),
                         control.datetime.datetime.fromisoformat(DEADLINE_UTC))
        self.assertEqual(authorize(args(timeout=90), synthetic),
                         control.datetime.datetime.fromisoformat(DEADLINE_UTC))
        source = ast.unparse(ast.parse((ROOT / "cloud-build" / "control.py").read_bytes()))
        self.assertIn(PHASE_ID, source)
        self.assertIn("CURRENT-RECOVERY-R11-BUDGET-20261021.json", source)

    def test_window_and_dispatch_boundaries(self):
        for command in ("submit", "request"):
            with self.subTest(command=command, boundary="before-start"), self.assertRaises(SystemExit):
                authorize(args(command=command), account(), "2026-10-21T06:14:38+00:00")
            with self.subTest(command=command, boundary="main-deadline"), self.assertRaises(SystemExit):
                authorize(args(command=command), account(), MAIN_DEADLINE_UTC.replace("Z", "+00:00"))
        with self.assertRaises(SystemExit):
            authorize(args(command="status"), account(), DEADLINE_UTC.replace("Z", "+00:00"))
        self.assertEqual(authorize(args(command="status"), account(), "2026-10-21T08:40:00+00:00"),
                         control.datetime.datetime.fromisoformat(DEADLINE_UTC))

    def test_wrong_phase_account_lane_owner_timeout_and_mode_fail_closed(self):
        for key, value in (
            ("phase_id", "MERGE-MOVING-GAP-INVARIANT-R10-2026-10-21"),
            ("owner", "select"), ("lane", "stock"),
            ("ledger", HERE / "CURRENT-RECOVERY-R10-BUDGET-20261021.json"),
            ("timeout", 89), ("timeout", 1201), ("source_mode", "public-git"),
        ):
            with self.subTest(argument=key, value=value), self.assertRaises(SystemExit):
                authorize(args(**{key: value}), account())
        for key, value in (("start_utc", "2026-10-21T06:14:40Z"),
                           ("deadline_utc", "2026-10-21T08:44:40Z"),
                           ("max_timeout_seconds", 1201),
                           ("ceiling_build_seconds", 3601)):
            ledger = account()
            ledger[key] = value
            with self.subTest(ledger_field=key), self.assertRaises(SystemExit):
                authorize(args(), ledger)
        wrong_lane = account()
        wrong_lane["allowed_lanes"] = ["stock"]
        with self.assertRaises(SystemExit):
            authorize(args(), wrong_lane)


if __name__ == "__main__":
    unittest.main(verbosity=2)
