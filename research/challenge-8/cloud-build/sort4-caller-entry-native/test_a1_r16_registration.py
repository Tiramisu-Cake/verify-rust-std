"""Synthetic R16 registration checks; no Cloud or proof dispatch."""
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
PROFILE = HERE / "A1-ACTUAL-LIFETIME-R16-PROFILE-2026-10-21.json"
R16 = json.loads(PROFILE.read_text())
S4 = json.loads(subprocess.check_output([
    "git", "show", "8bf480eac8273511137e8abc8dde8f4cb991ee6a:"
    + PREFIX + "A1-ACTUAL-BODY-R15-PROFILE-2026-10-21.json"], cwd=ROOT))
PHASE = "SORT4-ACTUAL-LIFETIME-2026-10-21-R16"
PROTOCOL = "SORT4-A1-CHECKED-TRAIT-CONTRACT-CLOUD-2026-10-17"
LANE = "o26-sort4-c1-current-recovery"

sys.path.insert(0, str(CLOUD))
spec = importlib.util.spec_from_file_location("r16_registration_control", CLOUD / "control.py")
CONTROL = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = CONTROL
spec.loader.exec_module(CONTROL)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def authorized_ledger():
    return {
        "phase": PHASE,
        "status": "AUTHORIZED",
        "authorization": "synthetic isolated registration test",
        "owner": "select-sort4",
        "ceiling_build_seconds": 3600,
        "allowed_lanes": [LANE],
        "start_utc": "2026-10-21T17:50:34Z",
        "main_deadline_utc": "2026-10-21T19:50:34Z",
        "deadline_utc": "2026-10-21T20:20:34Z",
        "maximum_builds": None,
        "maximum_build_timeout_seconds": 1200,
    }


class R16Registration(unittest.TestCase):
    def test_phase_profile_and_fresh_window(self):
        self.assertEqual(CONTROL.A1_R16_PHASE, PHASE)
        self.assertEqual(CONTROL.A1_R16_PROFILE, PREFIX + PROFILE.name)
        self.assertEqual((R16["phase"], R16["authorization_phase_id"]), (PHASE, PHASE))
        self.assertEqual((R16["phase_id"], R16["experiment_protocol_phase_id"]),
                         (PROTOCOL, PROTOCOL))
        self.assertEqual(R16["execution_mode"], "actual-sort4-body-v1")
        self.assertEqual(R16["body_action"], "full-body-c1-recovery")
        self.assertEqual(R16["account"], "BUDGET-A1-ACTUAL-LIFETIME-2026-10-21-R16.json")
        self.assertEqual((R16["start_utc"], R16["main_deadline_utc"], R16["deadline_utc"]),
                         (CONTROL.A1_R16_START, CONTROL.A1_R16_MAIN_DEADLINE,
                          CONTROL.A1_R16_DEADLINE))
        self.assertFalse(R16["profile_accepted"])
        self.assertFalse(R16["proof_credit"])
        self.assertEqual(R16["first_matrix_status"], "NOT_RUN")

    def test_exact_account_required(self):
        args = SimpleNamespace(phase_id=PHASE, owner="select-sort4")
        CONTROL.authorized_phase(args, authorized_ledger())
        mismatches = (
            {"owner": "other"}, {"start_utc": "2026-10-21T17:50:35Z"},
            {"main_deadline_utc": "2026-10-21T19:50:35Z"},
            {"deadline_utc": "2026-10-21T20:20:35Z"},
            {"maximum_build_timeout_seconds": 1201}, {"maximum_builds": 1},
            {"allowed_lanes": ["other-lane"]}, {"ceiling_build_seconds": 3601},
        )
        for delta in mismatches:
            with self.subTest(delta=delta), self.assertRaises(SystemExit):
                CONTROL.authorized_phase(args, dict(authorized_ledger(), **delta))

    def test_time_budget_has_r15_reserve_bounds(self):
        self.assertEqual(CONTROL.r16_time_budget(1200),
                         {"package_reserve": 240, "work_seconds": 960, "soft_margin": 60})
        self.assertEqual(CONTROL.r16_time_budget(270),
                         {"package_reserve": 240, "work_seconds": 30, "soft_margin": 15})
        for invalid in (89, 90, 269, 1201, True, 270.0):
            with self.subTest(seconds=invalid), self.assertRaises(ValueError):
                CONTROL.r16_time_budget(invalid)

    def test_environment_binds_exact_profile_bytes(self):
        raw = PROFILE.read_bytes()
        with patch.object(CONTROL.subprocess, "check_output", return_value=raw):
            env = CONTROL.envs("a" * 40, "b" * 40, LANE, PHASE)
        self.assertIn("SORT4_A1_AUTHORIZATION_PHASE_ID=" + PHASE, env)
        self.assertIn("SORT4_A1_PHASE_ID=" + PROTOCOL, env)
        self.assertIn("SORT4_A1_CHECKED_TRAIT_CONTRACT=1", env)
        self.assertIn("SORT4_A1_PROFILE_SHA256=" + sha(raw), env)

    def test_source_restore_uses_lossless_xz_transport(self):
        payload = b"synthetic R16 source payload\x00with bytes"
        encoded, command = CONTROL.source_restore_transport(payload, PHASE)
        import base64
        import lzma
        self.assertEqual(lzma.decompress(base64.b64decode(encoded)), payload)
        self.assertIn("lzma.decompress", command)
        self.assertIn("SOURCE_RESTORE_BYTES", command)

    def test_s4_semantic_and_full_body_dependency_pins_are_retained(self):
        mutable = {
            "account", "a1_entry_sha256", "a1_runner_sha256", "authorization_phase_id",
            "deadline_utc", "main_deadline_utc", "phase", "start_utc", "status",
            "previous_build_id", "candidate_version", "body_action", "registration_rationale",
            "cloud_build_enabled", "session_preparation", "a1_actual_body_sha256", "actual_body_dependencies_sha256",
            "a1_helper_sha256", "reference_own_probe_sha256",
        }
        for key, value in S4.items():
            if key not in mutable:
                with self.subTest(field=key):
                    self.assertEqual(R16.get(key), value)
        for field, filename in (
            ("a1_actual_body_sha256", "a1-actual-body-r16.py"),
            ("reference_own_probe_sha256", "a1-reference-own-probe.py"),
            ("a1_entry_sha256", "a1-entry-r16.py"),
            ("a1_runner_sha256", "a1-runner-r16.py"),
        ):
            self.assertEqual(R16[field], sha((HERE / filename).read_bytes()))
        for filename, digest in R16["a1_helper_sha256"].items():
            self.assertEqual(digest, sha((HERE / filename).read_bytes()))
            if filename not in ("a1-tool.py", "a1-focus-backend.py"):
                self.assertEqual(digest, S4["a1_helper_sha256"][filename])
        self.assertEqual(set(R16["actual_body_dependencies_sha256"]), {
            "a1-actual-body-c1.py", "a1-actual-copy-lemma.rs", "a1-actual-four-copy.rs",
            "a1-actual-recover-pair.rs", "a1-actual-selector-permutation.rs", "capture.py"})
        for name, digest in R16["actual_body_dependencies_sha256"].items():
            if name == "a1-actual-body-c1.py":
                self.assertEqual(digest, sha((HERE / name).read_bytes()))
            else:
                self.assertEqual(digest, S4["actual_body_dependencies_sha256"][name])

    def test_route_and_recipe_select_r16_full_body_inputs(self):
        lane = (CLOUD / "run-sort4-c1-current-recovery.sh").read_text()
        self.assertLess(lane.index(PHASE), lane.index("SORT4-ACTUAL-BODY-2026-10-21-R15"))
        self.assertIn("a1-entry-r16.py", lane)
        recipe = json.loads((CLOUD / "recipes/o26-sort4-c1-current-recovery.json").read_text())
        for path in ("A1-ACTUAL-LIFETIME-R16-PROFILE-2026-10-21.json",
                     "a1-actual-body-r16.py", "a1-actual-body-c1.py",
                     "a1-actual-four-copy.rs",
                     "a1-actual-recover-pair.rs", "a1-actual-selector-permutation.rs"):
            self.assertIn(PREFIX + path, recipe["proof_paths"])
        for path in ("a1-entry-r16.py", "a1-runner-r16.py"):
            self.assertIn(PREFIX + path, recipe["infra_paths"])
        self.assertNotIn(PREFIX + "a1-entry-r15.py", recipe["infra_paths"])
        self.assertNotIn(PREFIX + "a1-runner-r15.py", recipe["infra_paths"])

    def test_adapter_phase_and_profile_paths_are_r16_specific(self):
        entry = (HERE / "a1-entry-r16.py").read_text()
        runner = (HERE / "a1-runner-r16.py").read_text()
        self.assertIn("AUTHORIZATION_PHASE = '" + PHASE + "'", entry)
        self.assertIn("A1-ACTUAL-LIFETIME-R16-PROFILE-2026-10-21.json", entry)
        self.assertIn("a1-runner-r16.py", entry)
        self.assertIn("AUTHORIZATION_PHASE = \"" + PHASE + "\"", runner)
        self.assertIn("a1-actual-body-r16.py", runner)


if __name__ == "__main__":
    unittest.main()
