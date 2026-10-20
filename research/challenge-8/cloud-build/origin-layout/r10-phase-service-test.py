#!/usr/bin/env python3
"""Synthetic R10 phase authorization and profile registration checks."""
from __future__ import annotations

import ast
import hashlib
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
spec = importlib.util.spec_from_file_location("r10_phase_control", HERE.parent / "control.py")
if spec is None or spec.loader is None:
    raise RuntimeError("cloud build control module is unavailable")
control = importlib.util.module_from_spec(spec)
spec.loader.exec_module(control)

LEDGER_PATH = HERE / "CURRENT-RECOVERY-R10-BUDGET-20261021.json"
PHASE_ID = "MERGE-MOVING-GAP-INVARIANT-R10-2026-10-21"
PROFILE_NAME = "experimental-merge-moving-gap-r10-v1"
START_UTC = "2026-10-20T21:48:01Z"
MAIN_DEADLINE_UTC = "2026-10-20T23:48:01Z"
DEADLINE_UTC = "2026-10-21T00:18:01Z"
IN_WINDOW_NOW = "2026-10-20T22:00:00+00:00"


def account():
    return {
        "phase": PHASE_ID, "owner": "merge", "authorization_model": "bounded-cloud-budget",
        "status": "AUTHORIZED", "allowed_lanes": ["merge"],
        "ceiling_build_seconds": 3600, "used_build_seconds": 0,
        "remaining_build_seconds": 3600, "builds": [], "active_build": None,
        "start_utc": START_UTC, "main_deadline_utc": MAIN_DEADLINE_UTC,
        "deadline_utc": DEADLINE_UTC, "max_timeout_seconds": 1200,
        "authorization": "synthetic authorized R10 account", "carryover_allowed": False,
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


class R10PhaseTests(unittest.TestCase):
    def test_exact_registration_and_authorized_timeout(self):
        registered = json.loads(LEDGER_PATH.read_text())
        synthetic = account()
        for key in (
            "phase", "owner", "authorization_model", "allowed_lanes",
            "ceiling_build_seconds", "start_utc", "main_deadline_utc", "deadline_utc",
            "max_timeout_seconds", "status", "carryover_allowed",
        ):
            self.assertEqual(registered[key], synthetic[key])
        self.assertEqual(registered["used_build_seconds"] + registered["remaining_build_seconds"], 3600)
        # The live coordinator ledger evolves after the initial admission;
        # validate conservation without treating a legitimate Build as a defect.
        self.assertIsInstance(registered["builds"], list)
        self.assertEqual(registered["used_build_seconds"] + registered["remaining_build_seconds"],
                         registered["ceiling_build_seconds"])
        self.assertTrue(registered["active_build"] is None or any(
            row.get("build_id") == registered["active_build"] for row in registered["builds"]))
        self.assertEqual(authorize(args(), synthetic), control.datetime.datetime.fromisoformat(DEADLINE_UTC))
        self.assertEqual(authorize(args(timeout=90), synthetic), control.datetime.datetime.fromisoformat(DEADLINE_UTC))
        source = ast.unparse(ast.parse((HERE.parent / "control.py").read_bytes()))
        self.assertIn(PHASE_ID, source)
        self.assertIn("CURRENT-RECOVERY-R10-BUDGET-20261021.json", source)
        self.assertIn(PHASE_ID + "')", source)

    def test_window_and_dispatch_boundaries(self):
        for command in ("submit", "request"):
            with self.subTest(command=command, boundary="before-start"), self.assertRaises(SystemExit):
                authorize(args(command=command), account(), "2026-10-20T21:48:00+00:00")
            with self.subTest(command=command, boundary="main-deadline"), self.assertRaises(SystemExit):
                authorize(args(command=command), account(), MAIN_DEADLINE_UTC.replace("Z", "+00:00"))
        for instant in (DEADLINE_UTC.replace("Z", "+00:00"), "2026-10-21T00:19:00+00:00"):
            with self.subTest(command="status", instant=instant), self.assertRaises(SystemExit):
                authorize(args(command="status"), account(), instant)
        self.assertEqual(
            authorize(args(command="status"), account(), "2026-10-21T00:00:00+00:00"),
            control.datetime.datetime.fromisoformat(DEADLINE_UTC),
        )

    def test_wrong_phase_path_owner_lane_mode_and_timeout_fail_closed(self):
        for key, value in (
            ("phase_id", "MERGE-GUARD-CURRENT-RETURN-R9-2026-10-20"),
            ("owner", "select"), ("lane", "stock"),
            ("ledger", HERE / "CURRENT-RECOVERY-R9-BUDGET-20261020.json"),
            ("timeout", 89), ("timeout", 1201), ("source_mode", "public-git"),
        ):
            with self.subTest(argument=key, value=value), self.assertRaises(SystemExit):
                authorize(args(**{key: value}), account())
        wrong_lane = account()
        wrong_lane["allowed_lanes"] = ["stock"]
        with self.assertRaises(SystemExit):
            authorize(args(), wrong_lane)

    def test_profile_snapshot_has_new_identity_and_unqualified_status(self):
        profile_path = HERE / "GLUE-PROFILE.json"
        profile = json.loads(profile_path.read_bytes())
        baseline = json.loads((HERE / "R10-BASELINE-PROFILE-20261021.json").read_bytes())
        recipe = json.loads((HERE.parent / "recipes" / "merge.json").read_bytes())
        self.assertEqual(profile["profile"], PROFILE_NAME)
        self.assertEqual(profile["previous_profile_sha256"], hashlib.sha256(
            (HERE / "R10-BASELINE-PROFILE-20261021.json").read_bytes()).hexdigest())
        self.assertEqual(baseline["profile"], "experimental-merge-guard-current-return-r9-v1")
        self.assertFalse(profile["accepted"])
        self.assertEqual(profile["qualification"], "OPEN")
        self.assertEqual(profile["r10_registration"]["starting_tool_commit"],
                         "706e7c89fdf69dbe11e05ef275300b20d30a27cb")
        required = {
            "research/challenge-8/cloud-build/origin-layout/CURRENT-RECOVERY-R10-BUDGET-20261021.json",
            "research/challenge-8/cloud-build/origin-layout/R10-BASELINE-PROFILE-20261021.json",
            "research/challenge-8/cloud-build/origin-layout/R10-START-20261021.json",
            "research/challenge-8/cloud-build/origin-layout/r10-phase-service-test.py",
        }
        self.assertTrue(required <= set(recipe["proof_paths"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
