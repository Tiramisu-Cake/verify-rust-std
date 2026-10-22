"""Synthetic R18 exact registration checks; no Cloud or proof dispatch."""
from __future__ import annotations

import base64
import hashlib
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
PREFIX = "research/challenge-8/cloud-build/sort4-caller-entry-native/"
PROFILE = HERE / "A1-ACTUAL-C2-R17-PROFILE-2026-10-21.json"
PROFILE_SHA256 = "87a0bfe586b40a33bdf840164aec8748872c8fdd11b3faad421d3860d1f2a091"
LEDGER = HERE / "BUDGET-A1-ACTUAL-C2-2026-10-22-R18.json"
PHASE = "SORT4-ACTUAL-C2-2026-10-22-R18"
ROUTING = "SORT4-ACTUAL-C2-2026-10-21-R17"
PROTOCOL = "SORT4-A1-CHECKED-TRAIT-CONTRACT-CLOUD-2026-10-17"
LANE = "o26-sort4-c1-current-recovery"

sys.path.insert(0, str(CLOUD))
spec = importlib.util.spec_from_file_location("r18_registration_control", CLOUD / "control.py")
CONTROL = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = CONTROL
spec.loader.exec_module(CONTROL)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def authorized_ledger():
    return {
        "phase": PHASE,
        "phase_id": PHASE,
        "status": "AUTHORIZED",
        "authorization": "synthetic isolated registration test",
        "owner": "select-sort4",
        "task_id": "select-s5-unselected-borrow-autonomous-2026-10-22-r18",
        "ceiling_build_seconds": 3600,
        "allowed_lanes": [LANE],
        "start_utc": "2026-10-22T12:12:06Z",
        "main_deadline_utc": "2026-10-22T14:12:06Z",
        "deadline_utc": "2026-10-22T14:42:06Z",
        "maximum_builds": None,
        "maximum_build_timeout_seconds": 1200,
        "report_reserve_seconds": 240,
    }


class R18Registration(unittest.TestCase):
    def test_phase_window_and_pinned_r17_profile(self):
        self.assertEqual(CONTROL.A1_R18_PHASE, PHASE)
        self.assertEqual((CONTROL.A1_R18_START, CONTROL.A1_R18_MAIN_DEADLINE,
                          CONTROL.A1_R18_DEADLINE, CONTROL.A1_R18_CEILING),
                         ("2026-10-22T12:12:06Z", "2026-10-22T14:12:06Z",
                          "2026-10-22T14:42:06Z", 3600))
        self.assertEqual(CONTROL.A1_R18_PROFILE, PREFIX + PROFILE.name)
        self.assertEqual(CONTROL.A1_R18_PROFILE_SHA256, PROFILE_SHA256)
        self.assertEqual(sha(PROFILE.read_bytes()), PROFILE_SHA256)
        profile = json.loads(PROFILE.read_text())
        self.assertEqual(profile["authorization_phase_id"], ROUTING)
        self.assertFalse(profile["profile_accepted"])
        self.assertFalse(profile["proof_credit"])

    def test_committed_ledger_is_exact_fresh_r18_account(self):
        ledger = json.loads(LEDGER.read_text())
        self.assertEqual((ledger["phase"], ledger["phase_id"], ledger["status"]),
                         (PHASE, PHASE, "AUTHORIZED"))
        self.assertEqual((ledger["remaining_build_seconds"], ledger["spent_build_seconds"],
                          ledger["carry_seconds"], ledger["builds"], ledger["active_build"]),
                         (3600, 0, 0, [], None))
        for key, value in authorized_ledger().items():
            if key not in ("authorization",):
                self.assertEqual(ledger[key], value, key)
        self.assertIn(ROUTING, ledger["authorization"])
        self.assertIn(PROFILE_SHA256, ledger["authorization"])

    def test_exact_account_required(self):
        args = SimpleNamespace(phase_id=PHASE, owner="select-sort4")
        CONTROL.authorized_phase(args, authorized_ledger())
        mismatches = (
            {"owner": "other"}, {"start_utc": "2026-10-22T12:12:07Z"},
            {"main_deadline_utc": "2026-10-22T14:12:07Z"},
            {"deadline_utc": "2026-10-22T14:42:07Z"},
            {"deadline_utc": "2026-10-22T14:42:05Z"},
            {"start_utc": "2026-10-21T20:06:19Z", "main_deadline_utc": "2026-10-21T22:06:19Z",
             "deadline_utc": "2026-10-21T22:36:19Z"},
            {"maximum_build_timeout_seconds": 1201}, {"maximum_builds": 1},
            {"allowed_lanes": ["other-lane"]}, {"ceiling_build_seconds": 3601},
            {"ceiling_build_seconds": 3599}, {"report_reserve_seconds": 239},
            {"status": "CLOSED"}, {"phase": ROUTING},
        )
        for delta in mismatches:
            with self.subTest(delta=delta), self.assertRaises(SystemExit):
                CONTROL.authorized_phase(args, dict(authorized_ledger(), **delta))
        with self.assertRaises(SystemExit):
            CONTROL.authorized_phase(SimpleNamespace(phase_id=PHASE, owner="merge"),
                                     authorized_ledger())

    def test_timeout_budget_keeps_report_reserve(self):
        with patch.object(CONTROL.subprocess, "check_output", return_value=PROFILE.read_bytes()):
            config = CONTROL.config("a" * 40, "b" * 40, LANE, 1200, "token", phase_id=PHASE)
        self.assertEqual(config["timeout"], "1200s")
        for invalid in (269, 1201):
            with self.subTest(seconds=invalid), self.assertRaises(ValueError), \
                    patch.object(CONTROL.subprocess, "check_output",
                                 return_value=PROFILE.read_bytes()):
                CONTROL.config("a" * 40, "b" * 40, LANE, invalid, "token", phase_id=PHASE)

    def test_environment_routes_r17_key_over_exact_profile_bytes(self):
        raw = PROFILE.read_bytes()
        with patch.object(CONTROL.subprocess, "check_output", return_value=raw):
            env = CONTROL.envs("a" * 40, "b" * 40, LANE, PHASE)
        self.assertIn("SORT4_A1_AUTHORIZATION_PHASE_ID=" + ROUTING, env)
        self.assertNotIn("SORT4_A1_AUTHORIZATION_PHASE_ID=" + PHASE, env)
        self.assertIn("SORT4_A1_PHASE_ID=" + PROTOCOL, env)
        self.assertIn("SORT4_A1_CHECKED_TRAIT_CONTRACT=1", env)
        self.assertIn("SORT4_A1_PROFILE_SHA256=" + PROFILE_SHA256, env)

    def test_environment_rejects_changed_profile(self):
        raw = PROFILE.read_bytes()
        profile = json.loads(raw)
        variants = [raw + b"\n", raw.replace(b"R17-S5", b"R17-S6", 1)]
        for key, value in (("authorization_phase_id", PHASE), ("execution_mode", "other"),
                           ("body_action", "other"), ("experiment_protocol_phase_id", "other")):
            variants.append(json.dumps(dict(profile, **{key: value})).encode())
        for variant in variants:
            with self.subTest(sha=sha(variant)), self.assertRaises(SystemExit), \
                    patch.object(CONTROL.subprocess, "check_output", return_value=variant):
                CONTROL.envs("a" * 40, "b" * 40, LANE, PHASE)

    def test_source_restore_is_r18_enabled(self):
        payload = b"synthetic R18 source payload\x00with bytes"
        encoded, command = CONTROL.source_restore_transport(payload, PHASE)
        self.assertEqual(lzma.decompress(base64.b64decode(encoded)), payload)
        self.assertIn("SOURCE_RESTORE_BYTES", command)

    def test_r17_registration_unchanged(self):
        self.assertEqual((CONTROL.A1_R17_START, CONTROL.A1_R17_MAIN_DEADLINE,
                          CONTROL.A1_R17_DEADLINE),
                         ("2026-10-21T20:06:19Z", "2026-10-21T22:06:19Z",
                          "2026-10-21T22:36:19Z"))
        raw = PROFILE.read_bytes()
        with patch.object(CONTROL.subprocess, "check_output", return_value=raw):
            env = CONTROL.envs("a" * 40, "b" * 40, LANE, ROUTING)
        self.assertIn("SORT4_A1_AUTHORIZATION_PHASE_ID=" + ROUTING, env)

    def test_lane_route_accepts_routing_key(self):
        lane = (CLOUD / "run-sort4-c1-current-recovery.sh").read_text()
        self.assertIn('"${SORT4_A1_AUTHORIZATION_PHASE_ID:-}" == ' + ROUTING, lane)
        self.assertNotIn(PHASE, lane)


if __name__ == "__main__":
    unittest.main()
