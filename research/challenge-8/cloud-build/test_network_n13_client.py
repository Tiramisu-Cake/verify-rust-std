"""Synthetic client checks for the bounded Network N13 Cloud phase."""
import json
from pathlib import Path
import subprocess
import sys
import unittest
from types import SimpleNamespace
from unittest import mock


CLOUD_BUILD = Path(__file__).resolve().parent
sys.path.insert(0, str(CLOUD_BUILD))
import control


CANDIDATE = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=CLOUD_BUILD).decode().strip()
PHASE = control.NETWORK_N3_PHASE


class NetworkN13ClientTests(unittest.TestCase):
    def args(self, *, stage="exact", timeout=795, infra_sha=CANDIDATE):
        values = {"phase_id": PHASE, "timeout": timeout, "infra_sha": infra_sha}
        if stage is not None:
            values["stage"] = stage
        return SimpleNamespace(**values)

    def test_registered_stage_and_exact_build_timeouts_are_required(self):
        expected = {
            "preflight": 735,
            "exact": 795,
            "controls": 975,
            "controls-order": 795,
            "regressions": 915,
        }
        for stage, timeout in expected.items():
            with self.subTest(stage=stage):
                control.network_submit_gate(self.args(stage=stage, timeout=timeout))
        for bad in (
            self.args(stage=None),
            self.args(stage="unregistered"),
            self.args(timeout=794),
            self.args(stage="controls-order", timeout=794),
        ):
            with self.subTest(args=vars(bad)), self.assertRaises(SystemExit):
                control.network_submit_gate(bad)

    def test_profile_stage_limits_must_match_client_envelope(self):
        profile_path = CLOUD_BUILD / "network-n13" / "N13-EXECUTION-PROFILE-20261023-N3.json"
        profile = json.loads(profile_path.read_text())
        control.network_profile_stage_gate(profile, "controls-order", 795, 420)
        for changed in ("timeout_seconds", "build_timeout_seconds"):
            bad = json.loads(json.dumps(profile))
            bad["stages"]["controls-order"][changed] -= 1
            with self.subTest(changed=changed), self.assertRaises(SystemExit):
                control.network_profile_stage_gate(bad, "controls-order", 795, 420)

    def test_selected_recipe_must_bind_network_stages(self):
        profile_path = CLOUD_BUILD / "network-n13" / "N13-EXECUTION-PROFILE-20261023-N3.json"
        old_recipe = subprocess.check_output([
            "git", "show", "010127f1a6fb125097dcbec4ef84818b8f7adb8f:research/challenge-8/cloud-build/recipes/network-n13.json"
        ])
        with mock.patch.object(
            control.subprocess, "check_output",
            side_effect=[profile_path.read_bytes(), old_recipe],
        ), self.assertRaises(SystemExit):
            control.network_submit_gate(self.args(stage="controls-order"))

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
            CANDIDATE, CANDIDATE, "network-n13", 795, "synthetic-token",
            phase_id=PHASE, stage="controls-order",
        )
        self.assertIn("NETWORK_STAGE=controls-order", config["steps"][0]["env"])
        self.assertEqual(config["timeout"], "795s")
        self.assertEqual(config["queueTtl"], "60s")

    def test_network_build_reservation_keeps_setup_and_report_margins(self):
        budget = control.network_time_budget(735)
        self.assertEqual(budget, {
            "package_reserve": 240, "work_seconds": 495, "soft_margin": 15,
        })


if __name__ == "__main__":
    unittest.main()
