"""Static R11 closure/account binding checks; no preparation or proof execution."""
import hashlib
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
CLOUD = HERE.parent
ROOT = CLOUD.parents[2]
PHASE = "SORT4-CHECKED-CALLER-NATIVE-PROOF-2026-10-21-R11"
PROFILE_NAME = "A1-CHECKED-CALLER-R11-PROFILE-2026-10-21.json"
LEDGER_NAME = "BUDGET-A1-CHECKED-CALLER-2026-10-21-R11.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class R11Registration(unittest.TestCase):
    def test_new_profile_and_empty_budget_are_independently_bound(self):
        profile = json.loads((HERE / PROFILE_NAME).read_text())
        ledger = json.loads((HERE / LEDGER_NAME).read_text())
        self.assertEqual(profile["authorization_phase_id"], PHASE)
        self.assertEqual(profile["phase"], PHASE)
        self.assertEqual(profile["experiment_protocol_phase_id"],
                         "SORT4-A1-CHECKED-TRAIT-CONTRACT-CLOUD-2026-10-17")
        self.assertEqual(profile["account"], LEDGER_NAME)
        self.assertEqual(profile["start_utc"], "2026-10-20T21:41:43Z")
        self.assertEqual(profile["main_deadline_utc"], "2026-10-20T23:41:43Z")
        self.assertEqual(profile["deadline_utc"], "2026-10-21T00:11:43Z")
        self.assertFalse(profile["proof_credit"])
        self.assertEqual(profile["status"], "R11_AUTHORIZED_NOT_RUN")
        self.assertEqual(ledger["phase"], PHASE)
        self.assertEqual(ledger["owner"], "select-sort4")
        self.assertEqual(ledger["allowed_lanes"], ["o26-sort4-c1-current-recovery"])
        self.assertEqual(ledger["ceiling_build_seconds"], 3600)
        self.assertEqual(ledger["remaining_build_seconds"], 3600)
        self.assertEqual(ledger["builds"], [])
        self.assertIsNone(ledger["active_build"])
        for key, filename in (("a1_entry_sha256", "a1-entry-r11.py"),
                              ("a1_runner_sha256", "a1-runner-r11.py"),
                              ("a1_source_runner_sha256", "a1-runner.py")):
            self.assertEqual(profile[key], sha(HERE / filename), key)

    def test_recipe_and_lane_select_the_r11_adapter_without_replacing_history(self):
        recipe = json.loads((CLOUD / "recipes/o26-sort4-c1-current-recovery.json").read_text())
        self.assertIn("research/challenge-8/cloud-build/sort4-caller-entry-native/" + PROFILE_NAME,
                      recipe["proof_paths"])
        for filename in (PROFILE_NAME, "a1-entry-r11.py", "a1-runner-r11.py"):
            self.assertIn("research/challenge-8/cloud-build/sort4-caller-entry-native/" + filename,
                          recipe["infra_paths"])
        lane = (CLOUD / "run-sort4-c1-current-recovery.sh").read_text()
        self.assertIn(PHASE, lane)
        self.assertIn("a1-entry-r11.py", lane)
        self.assertIn("SORT4-DELIVERABLE-NATIVE-PROOF-2026-10-20-R10", lane)
        self.assertIn("a1-entry-r10.py", lane)


if __name__ == "__main__":
    unittest.main()
