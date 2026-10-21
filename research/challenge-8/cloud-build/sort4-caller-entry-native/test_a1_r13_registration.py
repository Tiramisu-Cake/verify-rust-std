"""Synthetic R13 phase and route registration checks; no proof execution."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
CLOUD = HERE.parent
sys.path.insert(0, str(CLOUD))
spec = importlib.util.spec_from_file_location("r13_control", CLOUD / "control.py")
CONTROL = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = CONTROL
spec.loader.exec_module(CONTROL)

PHASE = "SORT4-REFERENCE-OWN-CALLER-2026-10-21-R13"
PROFILE = "A1-REFERENCE-OWN-R13-PROFILE-2026-10-21.json"
LEDGER = "BUDGET-A1-REFERENCE-OWN-2026-10-21-R13.json"
LANE = "o26-sort4-c1-current-recovery"


class R13Registration(unittest.TestCase):
    def test_fresh_phase_account_and_non_admitting_profile(self):
        profile = json.loads((HERE / PROFILE).read_text())
        ledger = json.loads((HERE / LEDGER).read_text())
        self.assertEqual(CONTROL.A1_R13_PHASE, PHASE)
        self.assertEqual(CONTROL.A1_R13_PROFILE,
                         "research/challenge-8/cloud-build/sort4-caller-entry-native/" + PROFILE)
        self.assertEqual(profile["phase"], PHASE)
        self.assertEqual(profile["authorization_phase_id"], PHASE)
        self.assertEqual(profile["experiment_protocol_phase_id"], CONTROL.A1_PHASE)
        self.assertEqual(profile["account"], LEDGER)
        self.assertEqual((profile["start_utc"], profile["main_deadline_utc"],
                          profile["deadline_utc"]), (CONTROL.A1_R13_START,
                          CONTROL.A1_R13_MAIN_DEADLINE, CONTROL.A1_R13_DEADLINE))
        self.assertIn(profile["execution_mode"], ("full-matrix", "reference-own-probe"))
        self.assertFalse(profile["profile_accepted"])
        self.assertFalse(profile["proof_credit"])
        self.assertEqual(profile["first_matrix_status"], "NOT_RUN")
        self.assertTrue(all(value == "NOT_RUN"
                            for value in profile["first_matrix_cases"].values()))
        self.assertEqual(ledger["phase"], PHASE)
        self.assertEqual(ledger["owner"], "select-sort4")
        self.assertEqual(ledger["allowed_lanes"], [LANE])
        self.assertEqual(ledger["ceiling_build_seconds"], 3600)
        self.assertEqual(ledger["maximum_build_timeout_seconds"], 1200)
        self.assertEqual((ledger["start_utc"], ledger["main_deadline_utc"],
                          ledger["deadline_utc"]), (CONTROL.A1_R13_START,
                          CONTROL.A1_R13_MAIN_DEADLINE, CONTROL.A1_R13_DEADLINE))
        self.assertEqual(ledger["status"], "AUTHORIZED")
        self.assertIsNone(ledger["active_build"])
        self.assertEqual(ledger["builds"], [])
        self.assertEqual(ledger["used_build_seconds"], 0)
        self.assertEqual(ledger["carry_forward_seconds"], 0)

    def test_coordinator_accepts_only_exact_r13_account_shape(self):
        ledger = json.loads((HERE / LEDGER).read_text())
        args = SimpleNamespace(phase_id=PHASE, owner="select-sort4")
        CONTROL.authorized_phase(args, ledger)
        for key, bad in (("owner", "other"), ("maximum_build_timeout_seconds", 1201),
                         ("deadline_utc", "2026-10-21T11:56:37Z")):
            mutated = dict(ledger)
            mutated[key] = bad
            with self.subTest(key=key), self.assertRaises(SystemExit):
                CONTROL.authorized_phase(args, mutated)

    def test_route_and_recipe_bind_r13_without_rewriting_history(self):
        lane = (CLOUD / "run-sort4-c1-current-recovery.sh").read_text()
        self.assertIn(PHASE, lane)
        self.assertIn("a1-entry-r13.py", lane)
        self.assertLess(lane.index(PHASE), lane.index("SORT4-CHECKED-HELPER-CALLER-2026-10-21-R12"))
        recipe = json.loads((CLOUD / "recipes/o26-sort4-c1-current-recovery.json").read_text())
        prefix = "research/challenge-8/cloud-build/sort4-caller-entry-native/"
        self.assertIn(prefix + PROFILE, recipe["proof_paths"])
        for name in (PROFILE, "a1-entry-r13.py", "a1-runner-r13.py"):
            self.assertIn(prefix + name, recipe["infra_paths"])
        for phase in (CONTROL.A1_R12_PHASE, CONTROL.A1_R13_PHASE):
            self.assertIn(phase, (CLOUD / "sort4-caller-entry-native/a1-focus-backend.py").read_text())
        self.assertEqual(CONTROL.legacy_a1_occupied_limit(PHASE), None)
        self.assertEqual(CONTROL.legacy_a1_occupied_limit(CONTROL.A1_R12_PHASE), None)
        self.assertEqual(CONTROL.r13_time_budget(1200)["package_reserve"], 240)
        with self.assertRaises(ValueError):
            CONTROL.r13_time_budget(1201)

    def test_adapter_pins_match_profile_snapshot(self):
        profile = json.loads((HERE / PROFILE).read_text())
        sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
        self.assertEqual(profile["a1_entry_sha256"], sha(HERE / "a1-entry-r13.py"))
        self.assertEqual(profile["a1_runner_sha256"], sha(HERE / "a1-runner-r13.py"))
        self.assertEqual(profile["a1_source_runner_sha256"], sha(HERE / "a1-runner.py"))
        self.assertEqual(profile["a1_helper_sha256"]["a1-focus-backend.py"],
                         sha(HERE / "a1-focus-backend.py"))


if __name__ == "__main__":
    unittest.main()
