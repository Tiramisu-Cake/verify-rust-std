#!/usr/bin/env python3
"""Synthetic R5 phase authorization checks; no proof or live coordinator."""
from __future__ import annotations

import ast
import copy
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
spec = importlib.util.spec_from_file_location("r5_phase_control", HERE.parent / "control.py")
if spec is None or spec.loader is None:
    raise RuntimeError("cloud build control module is unavailable")
control = importlib.util.module_from_spec(spec)
spec.loader.exec_module(control)

LEDGER_PATH = HERE / "CURRENT-OWNERSHIP-R5-BUDGET-20261020.json"
PHASE_ID = "MERGE-CURRENT-OWNERSHIP-R5-2026-10-20"
START_UTC = "2026-10-20T07:28:45Z"
MAIN_DEADLINE_UTC = "2026-10-20T09:28:45Z"
DEADLINE_UTC = "2026-10-20T09:58:45Z"
IN_WINDOW_NOW = "2026-10-20T08:00:00+00:00"


def account():
    """Fresh synthetic authorized account; never depend on mutable ledger state."""
    return {
        "phase": PHASE_ID, "owner": "merge", "authorization_model": "bounded-cloud-budget",
        "status": "AUTHORIZED", "allowed_lanes": ["merge"],
        "ceiling_build_seconds": 3600, "used_build_seconds": 0,
        "remaining_build_seconds": 3600, "builds": [], "active_build": None,
        "start_utc": START_UTC, "main_deadline_utc": MAIN_DEADLINE_UTC,
        "deadline_utc": DEADLINE_UTC, "max_timeout_seconds": 900,
        "authorization": "synthetic authorized R5 account",
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


class R5PhaseTests(unittest.TestCase):
    def test_exact_registration_and_authorized_account(self):
        synthetic = account()
        for key in (
            "phase", "owner", "authorization_model", "allowed_lanes",
            "ceiling_build_seconds", "start_utc", "main_deadline_utc",
            "deadline_utc", "max_timeout_seconds",
        ):
            self.assertEqual(json.loads(LEDGER_PATH.read_text())[key], synthetic[key])
        authorize(args(), synthetic)

        tree = ast.parse((HERE.parent / "control.py").read_bytes())
        source = ast.unparse(tree)
        self.assertIn("MERGE-CURRENT-OWNERSHIP-R5-2026-10-20", source)
        self.assertIn("'MERGE-CURRENT-OWNERSHIP-R5-2026-10-20')", source)

    def test_missing_null_and_changed_authorization_fields_fail_closed(self):
        for key in (
            "owner", "authorization_model", "status", "allowed_lanes",
            "ceiling_build_seconds", "start_utc", "main_deadline_utc",
            "deadline_utc", "max_timeout_seconds", "authorization",
        ):
            invalid = {
                "owner": "other", "authorization_model": None, "status": "CLOSED",
                "allowed_lanes": ["stock"], "ceiling_build_seconds": 3601,
                "start_utc": None, "main_deadline_utc": "bad",
                "deadline_utc": "bad", "max_timeout_seconds": 901,
                "authorization": "",
            }[key]
            bad = account()
            bad[key] = invalid
            with self.subTest(key=key, value=invalid), self.assertRaises(SystemExit):
                authorize(args(), bad)
            missing = account()
            missing.pop(key)
            with self.subTest(key=key, missing=True), self.assertRaises(SystemExit):
                authorize(args(), missing)

        for key, value in (
            ("phase_id", "MERGE-GUARD-ADDRESSABILITY-R4-2026-10-20"),
            ("ledger", HERE / "GUARD-ADDRESSABILITY-R4-BUDGET-20261020.json"),
            ("owner", "select"), ("timeout", 89), ("timeout", 901),
            ("lane", "stock"), ("source_mode", "public-git"),
        ):
            with self.subTest(argument=key, value=value), self.assertRaises(SystemExit):
                authorize(args(**{key: value}), account())

    def test_evolving_budget_and_build_state_do_not_invalidate_phase(self):
        terminal = account()
        terminal.update(
            used_build_seconds=601,
            remaining_build_seconds=2999,
            builds=[{"status": "FAILURE", "build_seconds": 601, "accounted": True}],
        )
        authorize(args(), terminal)

        active = account()
        active.update(
            builds=[{"status": "WORKING", "build_id": "build-r5-active"}],
            active_build="build-r5-active",
        )
        authorize(args(command="status"), active)

    def test_start_main_and_absolute_clocks_are_enforced(self):
        for command in ("submit", "request"):
            with self.subTest(command=command, boundary="before-start"), self.assertRaises(SystemExit):
                authorize(args(command=command), account(), "2026-10-20T07:28:44+00:00")
            with self.subTest(command=command, boundary="main-deadline"), self.assertRaises(SystemExit):
                authorize(args(command=command), account(), "2026-10-20T09:28:45+00:00")

        with self.assertRaises(SystemExit):
            authorize(args(command="status"), account(), "2026-10-20T09:58:45+00:00")
        with self.assertRaises(SystemExit):
            authorize(args(command="status"), account(), "2026-10-20T10:00:00+00:00")
        with self.assertRaises(SystemExit):
            authorize(args(command="request"), account(), "2026-10-20T10:00:00+00:00")

    def test_status_is_permitted_during_finishing_window(self):
        active = account()
        active.update(
            builds=[{"status": "WORKING", "build_id": "build-r5-active"}],
            active_build="build-r5-active",
        )
        self.assertEqual(
            authorize(args(command="status"), active, "2026-10-20T09:40:00+00:00"),
            control.datetime.datetime.fromisoformat("2026-10-20T09:58:45+00:00"),
        )

    def test_pinned_merge_submission_rejects_invalid_envelope(self):
        for key, value in (
            ("timeout", 89), ("timeout", 901), ("lane", "stock"),
            ("source_mode", "public-git"),
        ):
            with self.subTest(argument=key, value=value), self.assertRaises(SystemExit):
                authorize(args(**{key: value}), account())


if __name__ == "__main__":
    unittest.main(verbosity=2)
