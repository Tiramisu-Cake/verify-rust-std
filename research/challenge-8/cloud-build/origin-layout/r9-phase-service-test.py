#!/usr/bin/env python3
"""Synthetic R9 phase authorization checks; no proof or live coordinator."""
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
spec = importlib.util.spec_from_file_location("r9_phase_control", HERE.parent / "control.py")
if spec is None or spec.loader is None:
    raise RuntimeError("cloud build control module is unavailable")
control = importlib.util.module_from_spec(spec)
spec.loader.exec_module(control)

LEDGER_PATH = HERE / "CURRENT-RECOVERY-R9-BUDGET-20261020.json"
PHASE_ID = "MERGE-GUARD-CURRENT-RETURN-R9-2026-10-20"
START_UTC = "2026-10-20T19:30:15Z"
MAIN_DEADLINE_UTC = "2026-10-20T21:30:15Z"
DEADLINE_UTC = "2026-10-20T22:00:15Z"
IN_WINDOW_NOW = "2026-10-20T20:00:00+00:00"


def account():
    return {
        "phase": PHASE_ID, "owner": "merge", "authorization_model": "bounded-cloud-budget",
        "status": "AUTHORIZED", "allowed_lanes": ["merge"],
        "ceiling_build_seconds": 3600, "used_build_seconds": 0,
        "remaining_build_seconds": 3600, "builds": [], "active_build": None,
        "start_utc": START_UTC, "main_deadline_utc": MAIN_DEADLINE_UTC,
        "deadline_utc": DEADLINE_UTC, "max_timeout_seconds": 1200,
        "authorization": "synthetic authorized R9 account",
        "carryover_allowed": False,
    }


def args(**changes):
    values = dict(
        phase_id=PHASE_ID, ledger=LEDGER_PATH, owner="merge",
        command="submit", timeout=1200, lane="merge", source_mode="pinned-objects",
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


class R9PhaseTests(unittest.TestCase):
    def test_exact_registration_and_authorized_1200_second_timeout(self):
        synthetic = account()
        registered = json.loads(LEDGER_PATH.read_text())
        for key in (
            "phase", "owner", "authorization_model", "allowed_lanes",
            "ceiling_build_seconds", "start_utc", "main_deadline_utc", "deadline_utc",
            "max_timeout_seconds", "status", "carryover_allowed",
        ):
            self.assertEqual(registered[key], synthetic[key])
        self.assertEqual(registered["used_build_seconds"] + registered["remaining_build_seconds"],
                         registered["ceiling_build_seconds"])
        self.assertIsInstance(registered["builds"], list)
        self.assertEqual(authorize(args(), synthetic), control.datetime.datetime.fromisoformat(DEADLINE_UTC))
        self.assertEqual(authorize(args(timeout=999), synthetic), control.datetime.datetime.fromisoformat(DEADLINE_UTC))
        self.assertLessEqual(1200 + 60, 1800)
        source = ast.unparse(ast.parse((HERE.parent / "control.py").read_bytes()))
        self.assertIn(PHASE_ID, source)
        self.assertIn("CURRENT-RECOVERY-R9-BUDGET-20261020.json", source)
        self.assertIn(PHASE_ID + "')", source)

    def test_missing_null_and_wrong_type_fields_fail_closed(self):
        invalid_values = {
            "phase": None, "owner": "select", "authorization_model": None,
            "status": "CLOSED", "allowed_lanes": None,
            "ceiling_build_seconds": "3600", "start_utc": None,
            "main_deadline_utc": "not-a-time", "deadline_utc": None,
            "max_timeout_seconds": "1200", "authorization": "",
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

    def test_wrong_identity_path_lane_owner_mode_and_timeout_fail_closed(self):
        for key, value in (
            ("phase_id", "MERGE-LATE-RECOVERY-REJOIN-R8-2026-10-20"),
            ("owner", "select"), ("lane", "stock"),
            ("ledger", HERE / "CURRENT-RECOVERY-R8-BUDGET-20261020.json"),
            ("timeout", 89), ("timeout", 1201), ("source_mode", "public-git"),
        ):
            with self.subTest(argument=key, value=value), self.assertRaises(SystemExit):
                authorize(args(**{key: value}), account())
        wrong_lane = account()
        wrong_lane["allowed_lanes"] = ["stock"]
        with self.assertRaises(SystemExit):
            authorize(args(), wrong_lane)

    def test_start_main_and_absolute_deadline_boundaries(self):
        for command in ("submit", "request"):
            with self.subTest(command=command, boundary="before-start"), self.assertRaises(SystemExit):
                authorize(args(command=command), account(), "2026-10-20T19:30:14+00:00")
            with self.subTest(command=command, boundary="main-deadline"), self.assertRaises(SystemExit):
                authorize(args(command=command), account(), MAIN_DEADLINE_UTC.replace("Z", "+00:00"))
        for instant in (DEADLINE_UTC.replace("Z", "+00:00"), "2026-10-20T22:01:00+00:00"):
            with self.subTest(command="status", instant=instant), self.assertRaises(SystemExit):
                authorize(args(command="status"), account(), instant)

    def test_finishing_window_allows_status_but_blocks_new_dispatch(self):
        self.assertEqual(
            authorize(args(command="status"), account(), "2026-10-20T21:45:00+00:00"),
            control.datetime.datetime.fromisoformat(DEADLINE_UTC),
        )
        for command in ("submit", "request"):
            with self.subTest(command=command), self.assertRaises(SystemExit):
                authorize(args(command=command), account(), "2026-10-20T21:45:00+00:00")

    def test_evolving_budget_does_not_change_authorized_phase_identity(self):
        spent = account()
        spent.update(used_build_seconds=1260, remaining_build_seconds=2340,
                     builds=[{"status": "FAILURE", "build_seconds": 1260}], active_build=None)
        self.assertEqual(authorize(args(timeout=1200), spent),
                         control.datetime.datetime.fromisoformat(DEADLINE_UTC))
        no_envelope_budget = account()
        no_envelope_budget["remaining_build_seconds"] = 1259
        self.assertEqual(authorize(args(), no_envelope_budget),
                         control.datetime.datetime.fromisoformat(DEADLINE_UTC))
        self.assertGreater(1200 + 60, no_envelope_budget["remaining_build_seconds"])
        source = ast.unparse(ast.parse((HERE.parent / "control.py").read_bytes()))
        self.assertIn("a.timeout + 60 > ledger['remaining_build_seconds']", source)
        self.assertIn("a.timeout + 60 > 1800", source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
