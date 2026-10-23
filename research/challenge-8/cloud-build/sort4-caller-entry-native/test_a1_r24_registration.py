"""Synthetic R24 callee-lane admission checks; no Cloud dispatch."""
from __future__ import annotations

import base64
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
LEDGER = HERE / "BUDGET-A1-ACTUAL-SELECT-2026-10-24-R24.json"
PROFILE = HERE / "A1-ACTUAL-SELECT-R24-PROFILE-2026-10-24.json"
PHASE = "SORT4-ACTUAL-SELECT-2026-10-24-R24"
ROUTE_MARKER = "SORT4-ACTUAL-SELECT-2026-10-23-R21"
TASK_ID = "select-callee-acceptance-autonomous-2026-10-24-r24"
T0 = "2026-10-23T10:48:18Z"
MAIN = "2026-10-26T10:48:18Z"
DEADLINE = "2026-10-26T11:48:18Z"
INSIDE = "2026-10-23T10:49:00Z"
LANE = "o26-select-callee-r20"
OTHER_LANE = "o26-sort4-c1-current-recovery"

sys.path.insert(0, str(CLOUD))
spec = importlib.util.spec_from_file_location("r24_registration_control", CLOUD / "control.py")
CONTROL = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = CONTROL
spec.loader.exec_module(CONTROL)


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
        "authorization": "synthetic isolated R24 registration test",
        "owner": "select-sort4",
        "task_id": TASK_ID,
        "ceiling_build_seconds": 21600,
        "allowed_lanes": [LANE],
        "start_utc": T0,
        "main_deadline_utc": MAIN,
        "deadline_utc": DEADLINE,
        "maximum_builds": None,
        "maximum_build_timeout_seconds": 1200,
        "report_reserve_seconds": 240,
    }


class R24CalleeRegistration(unittest.TestCase):
    def test_exact_window_and_lane(self):
        self.assertEqual(CONTROL.A1_R24_PHASE, PHASE)
        self.assertEqual((CONTROL.A1_R24_START, CONTROL.A1_R24_MAIN_DEADLINE,
                          CONTROL.A1_R24_DEADLINE, CONTROL.A1_R24_CEILING),
                         (T0, MAIN, DEADLINE, 21600))
        self.assertEqual(CONTROL.A1_R24_LANES, {LANE})
        recipe = json.loads((CLOUD / "recipes" / (LANE + ".json")).read_text())
        self.assertEqual(recipe["lane"], LANE)
        with at(INSIDE):
            deadline = CONTROL.authorized_phase(
                SimpleNamespace(phase_id=PHASE, owner="select-sort4"), authorized_ledger())
        self.assertEqual(deadline.isoformat(), "2026-10-26T11:48:18+00:00")

    def test_generated_artifacts_are_fresh_drafts(self):
        ledger = json.loads(LEDGER.read_text())
        profile = json.loads(PROFILE.read_text())
        self.assertEqual((ledger["phase"], ledger["phase_id"], ledger["owner"],
                          ledger["status"], ledger["ceiling_build_seconds"],
                          ledger["carry_seconds"], ledger["remaining_build_seconds"]),
                         (PHASE, PHASE, "select-sort4", "PREPARED_NOT_REGISTERED", 21600, 0, 21600))
        self.assertEqual((ledger["start_utc"], ledger["main_deadline_utc"],
                          ledger["deadline_utc"], ledger["allowed_lanes"]),
                         (T0, MAIN, DEADLINE, [LANE]))
        self.assertFalse(profile["accepted"])
        self.assertEqual(profile["account"], "BUDGET-A1-ACTUAL-C3-2026-10-22-R19.json")
        self.assertEqual(profile["session_preparation"], {
            "cloud_build_enabled": False, "owner": "select-sort4", "phase": PHASE,
            "schema": "smallsort-session-preparation-v1", "status": "DRAFT",
            "task_id": TASK_ID,
        })
        self.assertEqual((profile["stage_budget_estimate"]["build_timeout_seconds"],
                          profile["stage_budget_estimate"]["queue_reserve_seconds"],
                          profile["stage_budget_estimate"]["package_upload_verdict_reserve_seconds"]),
                         (1200, 60, 240))

    def test_wrong_account_values_and_deadline_are_refused(self):
        args = SimpleNamespace(phase_id=PHASE, owner="select-sort4")
        mismatches = (
            {"owner": "other"}, {"start_utc": "2026-10-23T10:48:19Z"},
            {"main_deadline_utc": "2026-10-26T10:48:19Z"},
            {"deadline_utc": "2026-10-26T11:48:19Z"},
            {"ceiling_build_seconds": 21599}, {"allowed_lanes": [OTHER_LANE]},
            {"allowed_lanes": [LANE, OTHER_LANE]}, {"maximum_build_timeout_seconds": 1201},
            {"maximum_builds": 1}, {"report_reserve_seconds": 239},
            {"status": "CLOSED"}, {"phase": "SORT4-ACTUAL-SELECT-2026-10-23-R23"},
        )
        for delta in mismatches:
            with self.subTest(delta=delta), at(INSIDE), self.assertRaises(SystemExit):
                CONTROL.authorized_phase(args, dict(authorized_ledger(), **delta))
        self.assertEqual(CONTROL.authorized_phase(
            args, dict(authorized_ledger(), report_reserve_seconds=300)),
            CONTROL.datetime.datetime.fromisoformat(DEADLINE.replace("Z", "+00:00")))
        with at(DEADLINE), self.assertRaisesRegex(SystemExit, "deadline has passed"):
            CONTROL.authorized_phase(args, authorized_ledger())

    def test_runner_preserves_r21_route_marker_and_exports_r24_phase(self):
        def forbidden(*_args, **_kwargs):
            raise AssertionError("callee lane must not read the A1 profile")
        with patch.object(CONTROL.subprocess, "check_output", forbidden):
            env = CONTROL.envs("a" * 40, "b" * 40, LANE, PHASE)
        self.assertIn("SORT4_R20_CALLEE_PHASE_ID=" + ROUTE_MARKER, env)
        self.assertIn("SORT4_R24_SESSION_PHASE_ID=" + PHASE, env)
        self.assertNotIn("SORT4_R20_CALLEE_PHASE_ID=" + PHASE, env)
        self.assertNotIn("SORT4_R23_SESSION_PHASE_ID=" + PHASE, env)
        self.assertFalse(any(item.startswith("SORT4_A1_") for item in env))
        with self.assertRaises(SystemExit):
            CONTROL.envs("a" * 40, "b" * 40, OTHER_LANE, PHASE)

    def test_timeout_config_and_source_transport(self):
        config = CONTROL.config("a" * 40, "b" * 40, LANE, 1200, "token", phase_id=PHASE)
        self.assertEqual(config["timeout"], "1200s")
        execute_script = config["steps"][0]["args"][1]
        self.assertIn(" + 960 - 60 ", execute_script)
        self.assertIn('"960s"', execute_script)
        for invalid in (269, 1201):
            with self.subTest(seconds=invalid), self.assertRaises(ValueError):
                CONTROL.config("a" * 40, "b" * 40, LANE, invalid, "token", phase_id=PHASE)
        payload = b"synthetic R24 source payload\x00"
        encoded, command = CONTROL.source_restore_transport(payload, PHASE)
        self.assertEqual(lzma.decompress(base64.b64decode(encoded)), payload)
        self.assertIn("lzma.decompress", command)

    def test_submit_requires_full_timeout_and_reserve_before_any_service_call(self):
        def forbidden(*_args, **_kwargs):
            raise AssertionError("Cloud/coordinator reached")
        ledger = authorized_ledger()
        cases = ((MAIN, 1200, 240, "main window ended"),
                 (INSIDE, 1199, 240, "full timeout 1200"),
                 (INSIDE, 1200, 239, "reserve"),
                 ("2026-10-26T10:27:00Z", 1200, 240, "do not fit main window"))
        for now, timeout, reserve, reason in cases:
            row = dict(ledger, report_reserve_seconds=reserve)
            args = SimpleNamespace(command="submit", phase_id=PHASE, owner="select-sort4",
                                   timeout=timeout, lane=LANE, source_mode="pinned-objects",
                                   infra_sha="a" * 40, proof_sha="b" * 40)
            with self.subTest(now=now, timeout=timeout, reserve=reserve), at(now), \
                    patch.object(CONTROL, "invoke", forbidden), \
                    patch.object(CONTROL.coordination, "request", forbidden), \
                    self.assertRaisesRegex(SystemExit, reason):
                CONTROL.run_command(args, None, row, None)

    def test_route_marker_matches_pinned_consumer(self):
        env = CONTROL.envs("a" * 40, "b" * 40, LANE, PHASE)
        self.assertEqual([item.split("=", 1)[1] for item in env
                          if item.startswith("SORT4_R20_CALLEE_PHASE_ID=")], [ROUTE_MARKER])
        runner = (CLOUD / "run-o26-select-callee-r20.sh").read_text()
        self.assertIn('"${SORT4_R20_CALLEE_PHASE_ID:-}" == ' + ROUTE_MARKER, runner)
        for name in ("select-callee-r21-fractional.py",
                     "select-callee-r21-fractional-proof-entry.py"):
            consumer = (CLOUD / name).read_text()
            self.assertIn("PHASE = '" + ROUTE_MARKER + "'", consumer)
        route_patch = (CLOUD.parents[0] / "overnight-assume-actual" /
                       "verifast-r22-fractional-forget-26.10.patch")
        self.assertTrue(route_patch.is_file())
        self.assertNotIn(PHASE, route_patch.read_text())

    def test_r23_account_and_route_values_are_unchanged(self):
        self.assertEqual((CONTROL.A1_R23_PHASE, CONTROL.A1_R23_START,
                          CONTROL.A1_R23_MAIN_DEADLINE, CONTROL.A1_R23_DEADLINE,
                          CONTROL.A1_R23_CEILING),
                         ("SORT4-ACTUAL-SELECT-2026-10-23-R23",
                          "2026-10-23T07:37:19Z", "2026-10-23T09:37:19Z",
                          "2026-10-23T10:07:19Z", 3600))
        self.assertEqual(CONTROL.A1_R24_ROUTE_MARKER, CONTROL.A1_R21_PHASE)
        prior = dict(authorized_ledger(), phase=CONTROL.A1_R23_PHASE,
                     phase_id=CONTROL.A1_R23_PHASE,
                     task_id="select-callee-acceptance-autonomous-2026-10-23-r23",
                     ceiling_build_seconds=3600,
                     start_utc=CONTROL.A1_R23_START,
                     main_deadline_utc=CONTROL.A1_R23_MAIN_DEADLINE,
                     deadline_utc=CONTROL.A1_R23_DEADLINE,
                     report_reserve_seconds=240)
        with at("2026-10-23T08:00:00Z"):
            result = CONTROL.authorized_phase(
                SimpleNamespace(phase_id=CONTROL.A1_R23_PHASE, owner="select-sort4"), prior)
        self.assertEqual(result.isoformat(), "2026-10-23T10:07:19+00:00")

    def test_full_envelope_is_checked_at_both_preflight_points(self):
        source = (CLOUD / "control.py").read_text()
        check = "a.timeout+60+ledger['report_reserve_seconds']"
        self.assertEqual(source.count(check), 4)
        self.assertIn("A1 R24 full timeout, queue envelope and report reserve do not fit main window", source)
        self.assertIn("A1 R24 full timeout, queue envelope and report reserve do not fit main window during preflight", source)


if __name__ == "__main__":
    unittest.main()
