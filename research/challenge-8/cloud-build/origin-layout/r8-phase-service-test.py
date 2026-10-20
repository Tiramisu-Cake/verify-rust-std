#!/usr/bin/env python3
"""Synthetic R8 phase authorization checks; no proof or live coordinator."""
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
sys.path.insert(0, str(HERE.parent))
spec = importlib.util.spec_from_file_location("r8_phase_control", HERE.parent / "control.py")
if spec is None or spec.loader is None:
    raise RuntimeError("cloud build control module is unavailable")
control = importlib.util.module_from_spec(spec)
spec.loader.exec_module(control)

LEDGER_PATH = HERE / "CURRENT-RECOVERY-R8-BUDGET-20261020.json"
PHASE_ID = "MERGE-LATE-RECOVERY-REJOIN-R8-2026-10-20"
START_UTC = "2026-10-20T17:11:30Z"
MAIN_DEADLINE_UTC = "2026-10-20T19:11:30Z"
DEADLINE_UTC = "2026-10-20T19:41:30Z"
IN_WINDOW_NOW = "2026-10-20T18:00:00+00:00"


def account():
    """Fresh synthetic account independent of mutable ledger state."""
    return {
        "phase": PHASE_ID, "owner": "merge", "authorization_model": "bounded-cloud-budget",
        "status": "AUTHORIZED", "allowed_lanes": ["merge"],
        "ceiling_build_seconds": 3600, "used_build_seconds": 0,
        "remaining_build_seconds": 3600, "builds": [], "active_build": None,
        "start_utc": START_UTC, "main_deadline_utc": MAIN_DEADLINE_UTC,
        "deadline_utc": DEADLINE_UTC, "max_timeout_seconds": 900,
        "authorization": "synthetic authorized R8 account",
    }


def args(**changes):
    values = dict(
        phase_id=PHASE_ID, ledger=LEDGER_PATH, owner="merge",
        command="submit", timeout=900, lane="merge", source_mode="pinned-objects",
    )
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


class R8PhaseTests(unittest.TestCase):
    def test_exact_registration_and_authorized_account(self):
        synthetic = account()
        registered = json.loads(LEDGER_PATH.read_text())
        for key in (
            "phase", "owner", "authorization_model", "allowed_lanes",
            "ceiling_build_seconds", "start_utc", "main_deadline_utc",
            "deadline_utc", "max_timeout_seconds", "status", "used_build_seconds",
            "remaining_build_seconds", "builds", "active_build", "carryover_allowed",
        ):
            expected = False if key == "carryover_allowed" else synthetic.get(key)
            self.assertEqual(registered[key], expected)
        self.assertEqual(authorize(args(), synthetic), control.datetime.datetime.fromisoformat(DEADLINE_UTC))

        source = ast.unparse(ast.parse((HERE.parent / "control.py").read_bytes()))
        self.assertIn(PHASE_ID, source)
        self.assertIn("CURRENT-RECOVERY-R8-BUDGET-20261020.json", source)
        self.assertIn(PHASE_ID + "')", source)

    def test_missing_null_and_malformed_authorization_fields_fail_closed(self):
        invalid_values = {
            "phase": None, "owner": "select", "authorization_model": None,
            "status": "CLOSED", "allowed_lanes": None,
            "ceiling_build_seconds": 3601, "start_utc": None,
            "main_deadline_utc": "not-a-time", "deadline_utc": None,
            "max_timeout_seconds": 901, "authorization": "",
        }
        for key, invalid in invalid_values.items():
            bad = account()
            bad[key] = invalid
            with self.subTest(key=key, value=invalid), self.assertRaises(SystemExit):
                authorize(args(), bad)
            missing = account()
            missing.pop(key)
            with self.subTest(key=key, missing=True), self.assertRaises(SystemExit):
                authorize(args(), missing)

    def test_wrong_owner_lane_path_timeout_and_source_mode_fail_closed(self):
        for key, value in (
            ("owner", "select"), ("lane", "stock"),
            ("ledger", HERE / "CANONICAL-SHARE-R6-BUDGET-20261020.json"),
            ("timeout", 89), ("timeout", 901), ("source_mode", "public-git"),
        ):
            with self.subTest(argument=key, value=value), self.assertRaises(SystemExit):
                authorize(args(**{key: value}), account())
        wrong_lane_account = account()
        wrong_lane_account["allowed_lanes"] = ["stock"]
        with self.assertRaises(SystemExit):
            authorize(args(), wrong_lane_account)

    def test_start_main_and_absolute_window_boundaries(self):
        for command in ("submit", "request"):
            with self.subTest(command=command, boundary="before-start"), self.assertRaises(SystemExit):
                authorize(args(command=command), account(), "2026-10-20T17:11:29+00:00")
            with self.subTest(command=command, boundary="main-deadline"), self.assertRaises(SystemExit):
                authorize(args(command=command), account(), MAIN_DEADLINE_UTC.replace("Z", "+00:00"))

        for instant in (DEADLINE_UTC.replace("Z", "+00:00"), "2026-10-20T19:50:00+00:00"):
            with self.subTest(command="status", instant=instant), self.assertRaises(SystemExit):
                authorize(args(command="status"), account(), instant)

    def test_finishing_window_allows_status_but_no_new_request(self):
        active = account()
        active.update(builds=[{"status": "WORKING", "build_id": "build-r8-active"}], active_build="build-r8-active")
        self.assertEqual(
            authorize(args(command="status"), active, "2026-10-20T19:20:00+00:00"),
            control.datetime.datetime.fromisoformat(DEADLINE_UTC),
        )
        for command in ("submit", "request"):
            with self.subTest(command=command), self.assertRaises(SystemExit):
                authorize(args(command=command), active, "2026-10-20T19:20:00+00:00")

    def test_evolving_budget_state_does_not_change_phase_identity(self):
        terminal = account()
        terminal.update(used_build_seconds=601, remaining_build_seconds=2999,
                        builds=[{"status": "FAILURE", "build_seconds": 601, "accounted": True}])
        authorize(args(), terminal)


if __name__ == "__main__":
    unittest.main(verbosity=2)
