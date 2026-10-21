#!/usr/bin/env python3
"""Synthetic authorization, time-window, and one-shot R11 retry checks."""
from __future__ import annotations

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
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent))
spec = importlib.util.spec_from_file_location("r11_retry_control", ROOT / "cloud-build" / "control.py")
if spec is None or spec.loader is None:
    raise RuntimeError("cloud build control module is unavailable")
control = importlib.util.module_from_spec(spec)
spec.loader.exec_module(control)

PHASE = "MERGE-R11-EVIDENCE-RETRY-2026-10-21"
LEDGER = HERE / "R11-RETRY-BUDGET-20261021.json"
START = "2026-10-21T09:02:57Z"
MAIN = "2026-10-21T09:32:57Z"
DEADLINE = "2026-10-21T09:47:57Z"
NOW = "2026-10-21T09:03:00+00:00"
OLD_LEDGER = HERE / "CURRENT-RECOVERY-R11-BUDGET-20261021.json"
OLD_LEDGER_SHA = "e8bc64434ee2bfc346b683d6a99599172575cea972ca359878c32bb19e317d88"


def account():
    return {
        "phase": PHASE, "owner": "merge", "authorization_model": "bounded-cloud-budget",
        "status": "AUTHORIZED", "allowed_lanes": ["merge"],
        "ceiling_build_seconds": 1060, "used_build_seconds": 0,
        "remaining_build_seconds": 1060, "max_builds": 1, "max_timeout_seconds": 1000,
        "builds": [], "active_build": None, "start_utc": START,
        "main_deadline_utc": MAIN, "deadline_utc": DEADLINE,
        "authorized_source_sha": "a" * 40,
        "authorization": "synthetic one-Build R11 retry authorization", "carryover_allowed": False,
    }


def args(**changes):
    values = dict(phase_id=PHASE, ledger=LEDGER, owner="merge", command="submit",
                  timeout=1000, lane="merge", source_mode="pinned-objects",
                  infra_sha="a" * 40, proof_sha="a" * 40)
    values.update(changes)
    return SimpleNamespace(**values)


def authorize(arguments, ledger, instant=NOW):
    real_datetime = control.datetime.datetime

    class FrozenDateTime(real_datetime):
        @classmethod
        def now(cls, tz=None):
            value = real_datetime.fromisoformat(instant)
            return value if tz is None else value.astimezone(tz)

    with patch.object(control.datetime, "datetime", FrozenDateTime):
        return control.authorized_phase(arguments, ledger)


class R11RetryPhaseTests(unittest.TestCase):
    def test_real_request_arguments_do_not_need_submit_fields(self):
        arguments = args(command="request")
        for name in ("timeout", "lane", "source_mode", "infra_sha", "proof_sha"):
            delattr(arguments, name)
        self.assertEqual(authorize(arguments, account()),
                         control.datetime.datetime.fromisoformat(DEADLINE))


    def test_registered_ledger_and_recipe_are_fresh_and_exact(self):
        registered = json.loads(LEDGER.read_text())
        synthetic = account()
        for key in ("phase", "owner", "authorization_model", "status", "allowed_lanes",
                    "ceiling_build_seconds", "max_builds", "max_timeout_seconds", "start_utc",
                    "main_deadline_utc", "deadline_utc", "carryover_allowed"):
            self.assertEqual(registered[key], synthetic[key], key)
        self.assertEqual(registered["used_build_seconds"], 0)
        self.assertEqual(registered["remaining_build_seconds"], 1060)
        self.assertEqual(registered["builds"], [])
        self.assertIsNone(registered["active_build"])
        self.assertIsNone(registered["authorized_source_sha"])
        self.assertEqual(authorize(args(), synthetic), control.datetime.datetime.fromisoformat(DEADLINE))
        recipe = json.loads((ROOT / "cloud-build" / "recipes" / "merge.json").read_text())
        paths = recipe["proof_paths"]
        for path in (
            "research/challenge-8/cloud-build/origin-layout/R11-RETRY-BUDGET-20261021.json",
            "research/challenge-8/cloud-build/origin-layout/R11-RETRY-INPUTS-20261021.json",
            "research/challenge-8/cloud-build/origin-layout/r11-retry-phase-service-test.py",
        ):
            self.assertIn(path, paths)
        self.assertEqual(control.digest(OLD_LEDGER.read_bytes()), OLD_LEDGER_SHA)

    def test_time_window_and_exact_dispatch_contract(self):
        for command in ("submit", "request"):
            with self.subTest(command=command, case="before start"), self.assertRaises(SystemExit):
                authorize(args(command=command), account(), "2026-10-21T09:02:56+00:00")
            with self.subTest(command=command, case="main cutoff"), self.assertRaises(SystemExit):
                authorize(args(command=command), account(), MAIN.replace("Z", "+00:00"))
        self.assertEqual(authorize(args(command="status"), account(), "2026-10-21T09:40:00+00:00"),
                         control.datetime.datetime.fromisoformat(DEADLINE))
        for changes in (
            {"phase_id": "MERGE-LABEL-STORAGE-INVARIANT-R11-2026-10-21"},
            {"owner": "select"}, {"lane": "stock"}, {"timeout": 999}, {"timeout": 1001},
            {"source_mode": "public-git"}, {"ledger": HERE / "CURRENT-RECOVERY-R11-BUDGET-20261021.json"},
        ):
            with self.subTest(args=changes), self.assertRaises(SystemExit):
                authorize(args(**changes), account())

    def test_submit_must_fit_build_and_queue_reserve_before_absolute_deadline(self):
        self.assertEqual(authorize(args(), account(), "2026-10-21T09:30:17+00:00"),
                         control.datetime.datetime.fromisoformat(DEADLINE))
        for instant in ("2026-10-21T09:30:18+00:00", "2026-10-21T09:31:00+00:00"):
            with self.subTest(instant=instant), self.assertRaises(SystemExit):
                authorize(args(), account(), instant)
        self.assertEqual(authorize(args(command="request"), account(), "2026-10-21T09:31:00+00:00"),
                         control.datetime.datetime.fromisoformat(DEADLINE))

    def test_missing_null_and_wrong_type_authorization_fields_fail_closed(self):
        required = ("status", "authorization", "authorization_model", "owner", "allowed_lanes",
                    "ceiling_build_seconds", "start_utc", "main_deadline_utc", "deadline_utc",
                    "max_builds", "max_timeout_seconds", "used_build_seconds",
                    "remaining_build_seconds", "builds", "carryover_allowed", "authorized_source_sha")
        for key in required:
            with self.subTest(missing=key), self.assertRaises(SystemExit):
                broken = account()
                del broken[key]
                authorize(args(), broken)
            with self.subTest(null=key), self.assertRaises(SystemExit):
                broken = account()
                broken[key] = None
                authorize(args(), broken)
        for key, value in (("max_builds", True), ("max_timeout_seconds", "1000"),
                           ("used_build_seconds", True), ("remaining_build_seconds", "1060"),
                           ("builds", {}), ("allowed_lanes", "merge"),
                           ("ceiling_build_seconds", True), ("carryover_allowed", 0)):
            with self.subTest(wrong_type=key), self.assertRaises(SystemExit):
                broken = account()
                broken[key] = value
                authorize(args(), broken)

    def test_source_sha_must_be_pinned_before_submit_but_not_request_or_status(self):
        unpinned = account()
        unpinned["authorized_source_sha"] = None
        self.assertEqual(authorize(args(command="request"), unpinned),
                         control.datetime.datetime.fromisoformat(DEADLINE))
        self.assertEqual(authorize(args(command="status"), unpinned),
                         control.datetime.datetime.fromisoformat(DEADLINE))
        with self.assertRaises(SystemExit):
            authorize(args(command="submit"), unpinned)
        for change in (
            {"authorized_source_sha": "not-a-sha"},
            {"infra_sha": "b" * 40}, {"proof_sha": "b" * 40},
        ):
            broken = account()
            if "authorized_source_sha" in change:
                broken["authorized_source_sha"] = change["authorized_source_sha"]
            callargs = {key: value for key, value in change.items() if key != "authorized_source_sha"}
            with self.subTest(change=change), self.assertRaises(SystemExit):
                authorize(args(**callargs), broken)

    def test_any_recorded_or_pending_build_consumes_the_only_attempt_but_status_remains_allowed(self):
        accounted_failure = account()
        accounted_failure.update(used_build_seconds=540, remaining_build_seconds=520,
                                 builds=[{"status": "FAILURE", "accounted": True, "build_seconds": 540}])
        for command in ("submit", "request"):
            with self.subTest(state="accounted failure", command=command), self.assertRaises(SystemExit):
                authorize(args(command=command), accounted_failure)
        self.assertEqual(authorize(args(command="status"), accounted_failure),
                         control.datetime.datetime.fromisoformat(DEADLINE))

        pending = account()
        pending.update(builds=[{"status": "WORKING", "accounted": False}], active_build="build-123")
        for command in ("submit", "request"):
            with self.subTest(state="pending", command=command), self.assertRaises(SystemExit):
                authorize(args(command=command), pending)
        self.assertEqual(authorize(args(command="status"), pending),
                         control.datetime.datetime.fromisoformat(DEADLINE))

        repeated = account()
        repeated["builds"] = [{"status": "FAILURE"}, {"status": "FAILURE"}]
        with self.assertRaises(SystemExit):
            authorize(args(command="status"), repeated)


if __name__ == "__main__":
    unittest.main(verbosity=2)
