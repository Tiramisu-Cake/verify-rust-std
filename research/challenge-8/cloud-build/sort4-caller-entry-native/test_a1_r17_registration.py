"""Synthetic R17 exact registration checks; no Cloud or proof dispatch."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
CLOUD = HERE.parent
ROOT = CLOUD.parents[2]
PREFIX = "research/challenge-8/cloud-build/sort4-caller-entry-native/"
PROFILE = HERE / "A1-ACTUAL-C2-R17-PROFILE-2026-10-21.json"
R17 = json.loads(PROFILE.read_text())
PHASE = "SORT4-ACTUAL-C2-2026-10-21-R17"
PROTOCOL = "SORT4-A1-CHECKED-TRAIT-CONTRACT-CLOUD-2026-10-17"
LANE = "o26-sort4-c1-current-recovery"

sys.path.insert(0, str(CLOUD))
spec = importlib.util.spec_from_file_location("r17_registration_control", CLOUD / "control.py")
CONTROL = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = CONTROL
spec.loader.exec_module(CONTROL)


def _fixed_window_clock():
    """Inject a fixed instant inside the R17 window instead of the wall clock."""
    import datetime as _real
    from types import SimpleNamespace as _NS
    start = _real.datetime.fromisoformat(CONTROL.A1_R17_START.replace("Z", "+00:00"))
    fixed = start + _real.timedelta(minutes=1)

    class _Fixed(_real.datetime):
        @classmethod
        def now(cls, tz=None):
            return fixed if tz is not None else fixed.replace(tzinfo=None)
    return _NS(datetime=_Fixed, timezone=_real.timezone, timedelta=_real.timedelta)


def _use_fixed_window_clock(test):
    from unittest.mock import patch as _patch
    clock = _patch.object(CONTROL, "datetime", _fixed_window_clock())
    clock.start()
    test.addCleanup(clock.stop)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def authorized_ledger():
    return {
        "phase": PHASE,
        "phase_id": PHASE,
        "status": "AUTHORIZED",
        "authorization": "synthetic isolated registration test",
        "owner": "select-sort4",
        "task_id": "select-actual-c2-autonomous-2026-10-21-r17",
        "ceiling_build_seconds": 3600,
        "allowed_lanes": [LANE],
        "start_utc": "2026-10-21T20:06:19Z",
        "main_deadline_utc": "2026-10-21T22:06:19Z",
        "deadline_utc": "2026-10-21T22:36:19Z",
        "maximum_builds": None,
        "maximum_build_timeout_seconds": 1200,
        "report_reserve_seconds": 240,
    }


class R17Registration(unittest.TestCase):
    def setUp(self):
        _use_fixed_window_clock(self)

    def test_phase_profile_and_fresh_window(self):
        self.assertEqual(CONTROL.A1_R17_PHASE, PHASE)
        self.assertEqual(CONTROL.A1_R17_PROFILE, PREFIX + PROFILE.name)
        self.assertEqual((R17["phase"], R17["authorization_phase_id"]), (PHASE, PHASE))
        self.assertEqual((R17["phase_id"], R17["experiment_protocol_phase_id"]),
                         (PROTOCOL, PROTOCOL))
        self.assertEqual(R17["execution_mode"], "actual-sort4-body-v1")
        self.assertEqual(R17["body_action"], "full-body-c1-recovery")
        self.assertEqual(R17["account"], "BUDGET-A1-ACTUAL-C2-2026-10-21-R17.json")
        self.assertEqual((R17["start_utc"], R17["main_deadline_utc"], R17["deadline_utc"]),
                         (CONTROL.A1_R17_START, CONTROL.A1_R17_MAIN_DEADLINE,
                          CONTROL.A1_R17_DEADLINE))
        self.assertFalse(R17["profile_accepted"])
        self.assertFalse(R17["proof_credit"])
        self.assertEqual(R17["first_matrix_status"], "NOT_RUN")

    def test_exact_account_required(self):
        args = SimpleNamespace(phase_id=PHASE, owner="select-sort4")
        CONTROL.authorized_phase(args, authorized_ledger())
        mismatches = (
            {"owner": "other"}, {"start_utc": "2026-10-21T20:06:20Z"},
            {"main_deadline_utc": "2026-10-21T22:06:20Z"},
            {"deadline_utc": "2026-10-21T22:36:20Z"},
            {"maximum_build_timeout_seconds": 1201}, {"maximum_builds": 1},
            {"allowed_lanes": ["other-lane"]}, {"ceiling_build_seconds": 3601},
            {"report_reserve_seconds": 239},
        )
        for delta in mismatches:
            with self.subTest(delta=delta), self.assertRaises(SystemExit):
                CONTROL.authorized_phase(args, dict(authorized_ledger(), **delta))

    def test_timeout_budget_keeps_report_reserve(self):
        self.assertEqual(CONTROL.r17_time_budget(1200),
                         {"package_reserve": 240, "work_seconds": 960, "soft_margin": 60})
        self.assertEqual(CONTROL.r17_time_budget(270),
                         {"package_reserve": 240, "work_seconds": 30, "soft_margin": 15})
        for invalid in (89, 90, 269, 1201, True, 270.0):
            with self.subTest(seconds=invalid), self.assertRaises(ValueError):
                CONTROL.r17_time_budget(invalid)

    def test_environment_binds_exact_profile_bytes(self):
        raw = PROFILE.read_bytes()
        with patch.object(CONTROL.subprocess, "check_output", return_value=raw):
            env = CONTROL.envs("a" * 40, "b" * 40, LANE, PHASE)
        self.assertIn("SORT4_A1_AUTHORIZATION_PHASE_ID=" + PHASE, env)
        self.assertIn("SORT4_A1_PHASE_ID=" + PROTOCOL, env)
        self.assertIn("SORT4_A1_CHECKED_TRAIT_CONTRACT=1", env)
        self.assertIn("SORT4_A1_PROFILE_SHA256=" + sha(raw), env)

    def test_source_restore_and_timeout_config_are_r17_specific(self):
        payload = b"synthetic R17 source payload\x00with bytes"
        encoded, command = CONTROL.source_restore_transport(payload, PHASE)
        import base64
        import lzma
        self.assertEqual(lzma.decompress(base64.b64decode(encoded)), payload)
        self.assertIn("lzma.decompress", command)
        self.assertIn("SOURCE_RESTORE_BYTES", command)
        with patch.object(CONTROL.subprocess, "check_output", return_value=PROFILE.read_bytes()):
            config = CONTROL.config("a" * 40, "b" * 40, LANE, 1200,
                                    "token", phase_id=PHASE)
        self.assertEqual(config["timeout"], "1200s")

    def test_route_and_recipe_select_r17_inputs(self):
        lane = (CLOUD / "run-sort4-c1-current-recovery.sh").read_text()
        self.assertLess(lane.index(PHASE), lane.index("SORT4-ACTUAL-LIFETIME-2026-10-21-R16"))
        self.assertIn("a1-entry-r17.py", lane)
        recipe = json.loads((CLOUD / "recipes/o26-sort4-c1-current-recovery.json").read_text())
        for kind in ("proof_paths", "infra_paths"):
            self.assertEqual(recipe[kind], sorted(set(recipe[kind])))
        for path in ("A1-ACTUAL-C2-R17-PROFILE-2026-10-21.json",
                     "a1-actual-body-r17.py", "a1-actual-body-c1.py",
                     "a1-actual-four-copy.rs", "a1-actual-recover-pair.rs",
                     "a1-actual-selector-permutation.rs", "a1-tool-r17.py"):
            self.assertIn(PREFIX + path, recipe["proof_paths"])
        for path in ("a1-entry-r17.py", "a1-runner-r17.py"):
            self.assertIn(PREFIX + path, recipe["infra_paths"])

    def test_adapter_phase_profile_and_body_paths_are_r17_specific(self):
        entry = (HERE / "a1-entry-r17.py").read_text()
        runner = (HERE / "a1-runner-r17.py").read_text()
        self.assertIn("AUTHORIZATION_PHASE = '" + PHASE + "'", entry)
        self.assertIn("A1-ACTUAL-C2-R17-PROFILE-2026-10-21.json", entry)
        self.assertIn("a1-runner-r17.py", entry)
        self.assertIn("AUTHORIZATION_PHASE = \"" + PHASE + "\"", runner)
        self.assertIn("a1-actual-body-r17.py", runner)


if __name__ == "__main__":
    unittest.main()
