"""Synthetic R19 exact registration checks with an injected clock; no Cloud or proof dispatch."""
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
PROFILE_SHA256 = "4dc903b89439f79d0e52d42480efb526ca97352728652aab688eb2987cf59c7a"
LEDGER = HERE / "BUDGET-A1-ACTUAL-C3-2026-10-22-R19.json"
PHASE = "SORT4-ACTUAL-C3-2026-10-22-R19"
INSIDE = "2026-10-22T14:30:00Z"
ROUTING = "SORT4-ACTUAL-C2-2026-10-21-R17"
PROTOCOL = "SORT4-A1-CHECKED-TRAIT-CONTRACT-CLOUD-2026-10-17"
LANE = "o26-sort4-c1-current-recovery"

sys.path.insert(0, str(CLOUD))
spec = importlib.util.spec_from_file_location("r19_registration_control", CLOUD / "control.py")
CONTROL = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = CONTROL
spec.loader.exec_module(CONTROL)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


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
        "authorization": "synthetic isolated registration test",
        "owner": "select-sort4",
        "task_id": "select-c3-callback-autonomous-2026-10-22-r19",
        "ceiling_build_seconds": 3600,
        "allowed_lanes": [LANE],
        "start_utc": "2026-10-22T13:50:26Z",
        "main_deadline_utc": "2026-10-22T15:50:26Z",
        "deadline_utc": "2026-10-22T16:20:26Z",
        "maximum_builds": None,
        "maximum_build_timeout_seconds": 1200,
        "report_reserve_seconds": 240,
    }


class R19Registration(unittest.TestCase):
    def test_phase_window_and_pinned_c3_profile(self):
        self.assertEqual(CONTROL.A1_R19_PHASE, PHASE)
        self.assertEqual((CONTROL.A1_R19_START, CONTROL.A1_R19_MAIN_DEADLINE,
                          CONTROL.A1_R19_DEADLINE, CONTROL.A1_R19_CEILING),
                         ("2026-10-22T13:50:26Z", "2026-10-22T15:50:26Z",
                          "2026-10-22T16:20:26Z", 3600))
        self.assertEqual(CONTROL.A1_R19_PROFILE, PREFIX + PROFILE.name)
        self.assertEqual(CONTROL.A1_R19_PROFILE_SHA256, PROFILE_SHA256)
        self.assertEqual(sha(PROFILE.read_bytes()), PROFILE_SHA256)
        profile = json.loads(PROFILE.read_text())
        self.assertEqual(profile["authorization_phase_id"], ROUTING)
        self.assertEqual(profile["actual_indexed_calls"], 3)
        self.assertIs(profile["actual_c2_recovery_enabled"], True)
        overlay = json.loads((HERE / "ACTUAL-SORT4-C2-RECOVERY-R17-MANIFEST.json").read_text())
        self.assertEqual(sha((HERE / "ACTUAL-SORT4-C2-RECOVERY-R17-MANIFEST.json").read_bytes()),
                         profile["actual_c2_recovery_overlay"]["manifest_sha256"])
        self.assertEqual(sha((HERE / overlay["patch"]).read_bytes()), overlay["patch_sha256"])
        for key in ("patch", "patch_sha256", "result_sha256"):
            self.assertEqual(overlay[key], profile["actual_c2_recovery_overlay"][key])
        self.assertEqual(sha((HERE / "a1-actual-body-r17.py").read_bytes()),
                         profile["a1_actual_body_sha256"])
        self.assertEqual(sha((HERE / "a1-actual-body-c2.py").read_bytes()),
                         profile["actual_body_dependencies_sha256"]["a1-actual-body-c2.py"])
        self.assertFalse(profile["profile_accepted"])
        self.assertFalse(profile["proof_credit"])

    def test_committed_ledger_is_exact_fresh_r19_account(self):
        ledger = json.loads(LEDGER.read_text())
        self.assertEqual((ledger["phase"], ledger["phase_id"], ledger["status"]),
                         (PHASE, PHASE, "AUTHORIZED"))
        self.assertEqual((ledger["ceiling_build_seconds"], ledger["carry_seconds"]), (3600, 0))
        used = sum(b["build_seconds"] for b in ledger["builds"] if b.get("accounted"))
        self.assertEqual(ledger["used_build_seconds"], used)
        self.assertEqual(ledger["remaining_build_seconds"] + used, 3600)
        self.assertTrue(all(b["phase_id"] == PHASE for b in ledger["builds"]))
        for key, value in authorized_ledger().items():
            if key not in ("authorization",):
                self.assertEqual(ledger[key], value, key)
        self.assertIn(ROUTING, ledger["authorization"])

    def test_exact_account_required(self):
        args = SimpleNamespace(phase_id=PHASE, owner="select-sort4")
        with at(INSIDE):
            CONTROL.authorized_phase(args, authorized_ledger())
        mismatches = (
            {"owner": "other"}, {"start_utc": "2026-10-22T13:50:27Z"},
            {"main_deadline_utc": "2026-10-22T15:50:27Z"},
            {"deadline_utc": "2026-10-22T16:20:27Z"},
            {"deadline_utc": "2026-10-22T16:20:25Z"},
            {"start_utc": "2026-10-22T12:12:06Z", "main_deadline_utc": "2026-10-22T14:12:06Z",
             "deadline_utc": "2026-10-22T14:42:06Z"},
            {"maximum_build_timeout_seconds": 1201}, {"maximum_builds": 1},
            {"allowed_lanes": ["other-lane"]}, {"ceiling_build_seconds": 3601},
            {"ceiling_build_seconds": 3599}, {"report_reserve_seconds": 239},
            {"status": "CLOSED"}, {"phase": ROUTING},
        )
        for delta in mismatches:
            with self.subTest(delta=delta), at(INSIDE), self.assertRaises(SystemExit):
                CONTROL.authorized_phase(args, dict(authorized_ledger(), **delta))
        with at(INSIDE), self.assertRaises(SystemExit):
            CONTROL.authorized_phase(SimpleNamespace(phase_id=PHASE, owner="merge"),
                                     authorized_ledger())
        with at("2026-10-22T16:20:27Z"), self.assertRaises(SystemExit):
            CONTROL.authorized_phase(args, authorized_ledger())

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
        variants = [raw + b"\n", raw.replace(b"R19-C3", b"R19-C4", 1)]
        for key, value in (("authorization_phase_id", PHASE), ("execution_mode", "other"),
                           ("body_action", "other"), ("experiment_protocol_phase_id", "other"),
                           ("actual_indexed_calls", 2), ("actual_indexed_calls", None),
                           ("actual_c2_recovery_enabled", False)):
            variants.append(json.dumps(dict(profile, **{key: value})).encode())
        for variant in variants:
            with self.subTest(sha=sha(variant)), self.assertRaises(SystemExit), \
                    patch.object(CONTROL.subprocess, "check_output", return_value=variant):
                CONTROL.envs("a" * 40, "b" * 40, LANE, PHASE)

    def test_source_restore_is_r19_enabled(self):
        payload = b"synthetic R19 source payload\x00with bytes"
        encoded, command = CONTROL.source_restore_transport(payload, PHASE)
        self.assertEqual(lzma.decompress(base64.b64decode(encoded)), payload)
        self.assertIn("SOURCE_RESTORE_BYTES", command)

    def test_r17_r18_registration_unchanged(self):
        self.assertEqual((CONTROL.A1_R17_START, CONTROL.A1_R17_MAIN_DEADLINE,
                          CONTROL.A1_R17_DEADLINE),
                         ("2026-10-21T20:06:19Z", "2026-10-21T22:06:19Z",
                          "2026-10-21T22:36:19Z"))
        self.assertEqual((CONTROL.A1_R18_START, CONTROL.A1_R18_MAIN_DEADLINE,
                          CONTROL.A1_R18_DEADLINE, CONTROL.A1_R18_PROFILE_SHA256),
                         ("2026-10-22T12:12:06Z", "2026-10-22T14:12:06Z",
                          "2026-10-22T14:42:06Z",
                          "87a0bfe586b40a33bdf840164aec8748872c8fdd11b3faad421d3860d1f2a091"))
        raw = PROFILE.read_bytes()
        with patch.object(CONTROL.subprocess, "check_output", return_value=raw), \
                self.assertRaises(SystemExit):
            CONTROL.envs("a" * 40, "b" * 40, LANE, CONTROL.A1_R18_PHASE)

    def test_submit_main_deadline_and_timeout_refuse_before_dispatch(self):
        import datetime as real

        def clock(text):
            fixed = real.datetime.fromisoformat(text.replace("Z", "+00:00"))

            class Fixed(real.datetime):
                @classmethod
                def now(cls, tz=None):
                    return fixed
            return SimpleNamespace(datetime=Fixed, timezone=real.timezone,
                                   timedelta=real.timedelta)

        def forbidden(*_args, **_kwargs):
            raise AssertionError("Cloud/coordinator reached")

        cases = (("2026-10-22T15:50:26Z", 1200, "main window ended"),
                 ("2026-10-22T16:00:00Z", 600, "main window ended"),
                 ("2026-10-22T14:30:00Z", 269, "timeout must be270..1200"),
                 ("2026-10-22T14:30:00Z", 1201, "timeout must be270..1200"))
        for now, timeout, reason in cases:
            args = SimpleNamespace(command="submit", phase_id=PHASE, owner="select-sort4",
                                   timeout=timeout, lane=LANE, source_mode="pinned-objects",
                                   infra_sha="a" * 40, proof_sha="a" * 40)
            with self.subTest(now=now, timeout=timeout), \
                    patch.object(CONTROL, "datetime", clock(now)), \
                    patch.object(CONTROL, "invoke", forbidden), \
                    patch.object(CONTROL.coordination, "request", forbidden), \
                    self.assertRaisesRegex(SystemExit, reason):
                CONTROL.run_command(args, None, authorized_ledger(), None)

    def test_lane_route_accepts_routing_key(self):
        lane = (CLOUD / "run-sort4-c1-current-recovery.sh").read_text()
        self.assertIn('"${SORT4_A1_AUTHORIZATION_PHASE_ID:-}" == ' + ROUTING, lane)
        self.assertNotIn(PHASE, lane)


if __name__ == "__main__":
    unittest.main()
