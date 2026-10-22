"""Synthetic client checks for the bounded Network N13 Cloud phase."""
from pathlib import Path
import subprocess
import sys
import unittest
from types import SimpleNamespace
from unittest import mock


CLOUD_BUILD = Path(__file__).resolve().parent
sys.path.insert(0, str(CLOUD_BUILD))
import control


CANDIDATE = "d9805342e29bc375e7ab87760fb6b79fe12948b8"
PHASE = control.NETWORK_N3_PHASE


class NetworkN13ClientTests(unittest.TestCase):
    def args(self, *, stage="exact", timeout=675, infra_sha=CANDIDATE):
        values = {"phase_id": PHASE, "timeout": timeout, "infra_sha": infra_sha}
        if stage is not None:
            values["stage"] = stage
        return SimpleNamespace(**values)

    def test_registered_stage_and_timeout_are_required(self):
        control.network_submit_gate(self.args())
        for bad in (
            self.args(stage=None),
            self.args(stage="unregistered"),
            self.args(timeout=674),
        ):
            with self.subTest(args=vars(bad)), self.assertRaises(SystemExit):
                control.network_submit_gate(bad)

    def test_selected_recipe_must_bind_network_stages(self):
        with self.assertRaises(SystemExit):
            control.network_submit_gate(self.args(infra_sha="ef6ded63541496b076cd135bde6ab9909c711ece"))

    def test_profile_bytes_must_match_registration_pin(self):
        self.assertEqual(
            control.network_env(CANDIDATE, PHASE),
            ["NETWORK_PHASE_ID=" + PHASE,
             "NETWORK_PROFILE_SHA256=" + control.NETWORK_N3_PROFILE_SHA256],
        )
        with mock.patch.object(control.subprocess, "check_output", return_value=b"wrong profile"):
            with self.assertRaises(SystemExit):
                control.network_env(CANDIDATE, PHASE)

    def test_generated_config_carries_the_admitted_stage(self):
        config = control.config(
            CANDIDATE, CANDIDATE, "network-n13", 675, "synthetic-token",
            phase_id=PHASE, stage="exact",
        )
        self.assertIn("NETWORK_STAGE=exact", config["steps"][0]["env"])
        self.assertEqual(config["timeout"], "675s")
        self.assertEqual(config["queueTtl"], "60s")

    def test_network_build_reservation_keeps_setup_and_report_margins(self):
        budget = control.network_time_budget(735)
        self.assertEqual(budget, {
            "package_reserve": 240, "work_seconds": 495, "soft_margin": 15,
        })


if __name__ == "__main__":
    unittest.main()
