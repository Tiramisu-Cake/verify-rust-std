"""Synthetic R14 phase/adapter registration checks; no proof execution."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
CLOUD = HERE.parent
sys.path.insert(0, str(CLOUD))
spec = importlib.util.spec_from_file_location("r14_control", CLOUD / "control.py")
CONTROL = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = CONTROL
spec.loader.exec_module(CONTROL)


def _fixed_window_clock():
    """Inject a fixed instant inside the R14 window instead of the wall clock."""
    import datetime as _real
    from types import SimpleNamespace as _NS
    start = _real.datetime.fromisoformat(CONTROL.A1_R14_START.replace("Z", "+00:00"))
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

PHASE = "SORT4-NATIVE-P1-MATRIX-2026-10-21-R14"
PROFILE = "A1-NATIVE-MATRIX-R14-PROFILE-2026-10-21.json"
LEDGER = "BUDGET-A1-NATIVE-MATRIX-2026-10-21-R14.json"
LANE = "o26-sort4-c1-current-recovery"
PROTOCOL = "SORT4-A1-CHECKED-TRAIT-CONTRACT-CLOUD-2026-10-17"


class R14Registration(unittest.TestCase):
    def setUp(self):
        _use_fixed_window_clock(self)

    @classmethod
    def setUpClass(cls):
        cls.profile = json.loads((HERE / PROFILE).read_text())
        cls.ledger = json.loads((HERE / LEDGER).read_text())

    def test_fresh_phase_account_and_nonadmitting_profile(self):
        p, ledger = self.profile, self.ledger
        self.assertEqual(CONTROL.A1_R14_PHASE, PHASE)
        self.assertEqual(CONTROL.A1_R14_PROFILE,
                         "research/challenge-8/cloud-build/sort4-caller-entry-native/" + PROFILE)
        self.assertEqual(p["phase"], PHASE)
        self.assertEqual(p["authorization_phase_id"], PHASE)
        self.assertEqual(p["experiment_protocol_phase_id"], PROTOCOL)
        self.assertEqual(p["phase_id"], PROTOCOL)
        self.assertEqual(p["account"], LEDGER)
        self.assertEqual((p["start_utc"], p["main_deadline_utc"], p["deadline_utc"]),
                         (CONTROL.A1_R14_START, CONTROL.A1_R14_MAIN_DEADLINE,
                          CONTROL.A1_R14_DEADLINE))
        self.assertIn(p["execution_mode"], ("native-p1-target", "full-matrix"))
        self.assertFalse(p["profile_accepted"])
        self.assertFalse(p["proof_credit"])
        self.assertEqual(p["first_matrix_status"], "NOT_RUN")
        self.assertTrue(all(value == "NOT_RUN" for value in p["first_matrix_cases"].values()))
        self.assertEqual(ledger["phase"], PHASE)
        self.assertEqual(ledger["owner"], "select-sort4")
        self.assertEqual(ledger["allowed_lanes"], [LANE])
        self.assertEqual(ledger["ceiling_build_seconds"], 3600)
        self.assertEqual(ledger["maximum_build_timeout_seconds"], 1200)
        self.assertIsNone(ledger["maximum_builds"])
        self.assertEqual((ledger["start_utc"], ledger["main_deadline_utc"],
                          ledger["deadline_utc"]), (CONTROL.A1_R14_START,
                          CONTROL.A1_R14_MAIN_DEADLINE, CONTROL.A1_R14_DEADLINE))
        self.assertEqual(ledger["status"], "AUTHORIZED")
        self.assertEqual(ledger["used_build_seconds"], 0)
        self.assertEqual(ledger["carry_forward_seconds"], 0)

    def test_control_accepts_exact_fresh_account_only(self):
        args = SimpleNamespace(phase_id=PHASE, owner="select-sort4")
        CONTROL.authorized_phase(args, self.ledger)
        for key, bad in (("owner", "other"),
                         ("maximum_build_timeout_seconds", 1201),
                         ("deadline_utc", "2026-10-21T14:59:31Z"),
                         ("start_utc", "2026-10-21T12:29:31Z")):
            mutated = dict(self.ledger, **{key: bad})
            with self.subTest(key=key), self.assertRaises(SystemExit):
                CONTROL.authorized_phase(args, mutated)

    def test_environment_binds_r14_profile_and_preserves_protocol(self):
        raw = (HERE / PROFILE).read_bytes()
        with patch.object(CONTROL.subprocess, "check_output", return_value=raw):
            env = CONTROL.envs("a" * 40, "b" * 40, LANE, PHASE)
        self.assertIn("SORT4_A1_AUTHORIZATION_PHASE_ID=" + PHASE, env)
        self.assertIn("SORT4_A1_PHASE_ID=" + PROTOCOL, env)
        self.assertIn("SORT4_A1_PROFILE_SHA256=" + hashlib.sha256(raw).hexdigest(), env)
        self.assertIn("SORT4_A1_CHECKED_TRAIT_CONTRACT=1", env)

    def test_r14_budget_and_historical_route_are_separate(self):
        budget = CONTROL.r14_time_budget(1200)
        self.assertEqual(budget["package_reserve"], 240)
        self.assertEqual(budget["work_seconds"], 960)
        self.assertEqual(CONTROL.legacy_a1_occupied_limit(PHASE), None)
        self.assertEqual(CONTROL.A1_R13_PHASE,
                         "SORT4-REFERENCE-OWN-CALLER-2026-10-21-R13")
        with self.assertRaises(ValueError):
            CONTROL.r14_time_budget(1201)

    def test_route_and_adapter_pins(self):
        lane = (CLOUD / "run-sort4-c1-current-recovery.sh").read_text()
        r14_at = lane.index(PHASE)
        self.assertIn("a1-entry-r14.py", lane[r14_at:r14_at + 800])
        self.assertLess(r14_at, lane.index("SORT4-REFERENCE-OWN-CALLER-2026-10-21-R13"))
        entry = (HERE / "a1-entry-r14.py").read_text()
        runner = (HERE / "a1-runner-r14.py").read_text()
        self.assertIn("AUTHORIZATION_PHASE = '" + PHASE + "'", entry)
        self.assertIn("a1-runner-r14.py", entry)
        self.assertIn("AUTHORIZATION_PHASE = \"" + PHASE + "\"", runner)
        self.assertIn(PROFILE, runner)
        self.assertIn('"a1-runner.py"', runner)
        recipe = json.loads((CLOUD / "recipes/o26-sort4-c1-current-recovery.json").read_text())
        prefix = "research/challenge-8/cloud-build/sort4-caller-entry-native/"
        self.assertIn(prefix + PROFILE, recipe["proof_paths"])
        for name in ("a1-entry-r14.py", "a1-runner-r14.py"):
            self.assertIn(prefix + name, recipe["infra_paths"])

    def test_profile_adapter_hashes_match_files(self):
        h = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
        self.assertEqual(self.profile["a1_entry_sha256"], h(HERE / "a1-entry-r14.py"))
        self.assertEqual(self.profile["a1_runner_sha256"], h(HERE / "a1-runner-r14.py"))
        self.assertEqual(self.profile["a1_source_runner_sha256"], h(HERE / "a1-runner.py"))


if __name__ == "__main__":
    unittest.main()
