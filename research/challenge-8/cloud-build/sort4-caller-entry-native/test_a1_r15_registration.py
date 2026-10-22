"""Isolated R15 registration tests; mocks Git profile reads and never dispatches Cloud."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
CLOUD = HERE.parent
PREFIX = "research/challenge-8/cloud-build/sort4-caller-entry-native/"
R13_PROFILE = HERE / "A1-REFERENCE-OWN-R13-PROFILE-2026-10-21.json"
R14_PROFILE = HERE / "A1-NATIVE-MATRIX-R14-PROFILE-2026-10-21.json"
R15_PROFILE = HERE / "A1-ACTUAL-BODY-R15-PROFILE-2026-10-21.json"
R13 = json.loads(R13_PROFILE.read_text())
R14 = json.loads(R14_PROFILE.read_text())
R15 = json.loads(R15_PROFILE.read_text())
PHASE = "SORT4-ACTUAL-BODY-2026-10-21-R15"
PROTOCOL = "SORT4-A1-CHECKED-TRAIT-CONTRACT-CLOUD-2026-10-17"
LANE = "o26-sort4-c1-current-recovery"

sys.path.insert(0, str(CLOUD))
spec = importlib.util.spec_from_file_location("r15_registration_control", CLOUD / "control.py")
CONTROL = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = CONTROL
spec.loader.exec_module(CONTROL)


def _fixed_window_clock():
    """Inject a fixed instant inside the R15 window instead of the wall clock."""
    import datetime as _real
    from types import SimpleNamespace as _NS
    start = _real.datetime.fromisoformat(CONTROL.A1_R15_START.replace("Z", "+00:00"))
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
        "status": "AUTHORIZED",
        "authorization": "synthetic isolated registration test",
        "owner": "select-sort4",
        "ceiling_build_seconds": 3600,
        "allowed_lanes": [LANE],
        "start_utc": "2026-10-21T14:54:00Z",
        "main_deadline_utc": "2026-10-21T16:54:00Z",
        "deadline_utc": "2026-10-21T17:24:00Z",
        "maximum_builds": None,
        "maximum_build_timeout_seconds": 1200,
    }


class R15Registration(unittest.TestCase):
    def setUp(self):
        _use_fixed_window_clock(self)

    def test_phase_profile_window_and_nonadmitting_body_mode(self):
        p = R15
        self.assertEqual(CONTROL.A1_R15_PHASE, PHASE)
        self.assertEqual(CONTROL.A1_R15_PROFILE, PREFIX + R15_PROFILE.name)
        self.assertEqual((p["phase"], p["authorization_phase_id"]), (PHASE, PHASE))
        self.assertEqual((p["phase_id"], p["experiment_protocol_phase_id"]),
                         (PROTOCOL, PROTOCOL))
        self.assertEqual(p["execution_mode"], "actual-sort4-body-v1")
        self.assertEqual(p["account"], "BUDGET-A1-ACTUAL-BODY-2026-10-21-R15.json")
        self.assertEqual((p["start_utc"], p["main_deadline_utc"], p["deadline_utc"]),
                         (CONTROL.A1_R15_START, CONTROL.A1_R15_MAIN_DEADLINE,
                          CONTROL.A1_R15_DEADLINE))
        self.assertFalse(p["profile_accepted"])
        self.assertFalse(p["proof_credit"])
        self.assertEqual(p["first_matrix_status"], "NOT_RUN")
        self.assertTrue(all(value == "NOT_RUN" for value in p["first_matrix_cases"].values()))
        self.assertIn("complete source-bound sort4_stable body", p["registration_rationale"])

    def test_synthetic_authorized_ledger_is_accepted_and_mismatches_rejected(self):
        ledger = authorized_ledger()
        args = SimpleNamespace(phase_id=PHASE, owner="select-sort4")
        CONTROL.authorized_phase(args, ledger)
        mismatches = (
            (dict(ledger, owner="different-owner"), args),
            (ledger, SimpleNamespace(phase_id=PHASE, owner="different-owner")),
            (dict(ledger, start_utc="2026-10-21T14:54:01Z"), args),
            (dict(ledger, main_deadline_utc="2026-10-21T16:54:01Z"), args),
            (dict(ledger, deadline_utc="2026-10-21T17:24:01Z"), args),
            (dict(ledger, maximum_build_timeout_seconds=1201), args),
            (dict(ledger, maximum_builds=1), args),
        )
        for changed, changed_args in mismatches:
            with self.subTest(ledger=changed, args=changed_args), self.assertRaises(SystemExit):
                CONTROL.authorized_phase(changed_args, changed)

    def test_r15_build_time_budget_bounds_and_reserves_package_time(self):
        self.assertEqual(CONTROL.r15_time_budget(1200),
                         {"package_reserve": 240, "work_seconds": 960, "soft_margin": 60})
        self.assertEqual(CONTROL.r15_time_budget(90),
                         {"package_reserve": 60, "work_seconds": 30, "soft_margin": 15})
        for invalid in (89, 1201, True, 90.0):
            with self.subTest(seconds=invalid), self.assertRaises(ValueError):
                CONTROL.r15_time_budget(invalid)

    def test_r15_environment_uses_mocked_published_profile_bytes(self):
        raw = R15_PROFILE.read_bytes()
        with patch.object(CONTROL.subprocess, "check_output", return_value=raw):
            env = CONTROL.envs("a" * 40, "b" * 40, LANE, PHASE)
        self.assertIn("SORT4_A1_AUTHORIZATION_PHASE_ID=" + PHASE, env)
        self.assertIn("SORT4_A1_PHASE_ID=" + PROTOCOL, env)
        self.assertIn("SORT4_A1_PROFILE_SHA256=" + sha(raw), env)
        self.assertIn("SORT4_A1_CHECKED_TRAIT_CONTRACT=1", env)

    def test_r13_environment_registration_remains_separate(self):
        raw = R13_PROFILE.read_bytes()
        with patch.object(CONTROL.subprocess, "check_output", return_value=raw):
            env = CONTROL.envs("c" * 40, "d" * 40, LANE, CONTROL.A1_R13_PHASE)
        self.assertIn("SORT4_A1_AUTHORIZATION_PHASE_ID=" + CONTROL.A1_R13_PHASE, env)
        self.assertIn("SORT4_A1_PHASE_ID=" + PROTOCOL, env)
        self.assertIn("SORT4_A1_PROFILE_SHA256=" + sha(raw), env)
        self.assertNotIn("SORT4_A1_AUTHORIZATION_PHASE_ID=" + PHASE, env)
        self.assertEqual(CONTROL.A1_R13_START, "2026-10-21T09:26:36Z")
        self.assertEqual(CONTROL.A1_R13_DEADLINE, "2026-10-21T11:56:36Z")

    def test_r15_source_restore_uses_lossless_lzma_transport(self):
        payload = b"synthetic R15 transport payload\x00with bytes"
        encoded, command = CONTROL.source_restore_transport(payload, PHASE)
        import base64
        import lzma
        self.assertEqual(lzma.decompress(base64.b64decode(encoded)), payload)
        self.assertIn("lzma.decompress", command)
        self.assertIn("SOURCE_RESTORE_BYTES", command)

    def test_r15_route_adapters_and_recipe_closure(self):
        lane = (CLOUD / "run-sort4-c1-current-recovery.sh").read_text()
        r15_at = lane.index(PHASE)
        r14_at = lane.index("SORT4-NATIVE-P1-MATRIX-2026-10-21-R14")
        self.assertLess(r15_at, r14_at)
        self.assertIn("a1-entry-r15.py", lane[r15_at:r15_at + 900])
        entry = (HERE / "a1-entry-r15.py").read_text()
        runner = (HERE / "a1-runner-r15.py").read_text()
        actual = (HERE / "a1-actual-body.py").read_text()
        self.assertIn("AUTHORIZATION_PHASE = '" + PHASE + "'", entry)
        self.assertIn("actual-sort4-body-v1", entry)
        self.assertIn("a1-runner-r15.py", entry)
        self.assertIn("a1_actual_body_sha256", runner)
        self.assertIn("a1-actual-body.py", runner)
        self.assertIn("return module.run(a, c4=c4, audit=audit, driver=driver,", runner)
        self.assertIn("def run(a, *, c4, audit, driver, manifest, ghost):", actual)

        recipe = json.loads((CLOUD / "recipes/o26-sort4-c1-current-recovery.json").read_text())
        self.assertIn(PREFIX + R15_PROFILE.name, recipe["proof_paths"])
        self.assertIn(PREFIX + "a1-actual-body.py", recipe["proof_paths"])
        self.assertIn(PREFIX + "a1-entry-r15.py", recipe["infra_paths"])
        self.assertIn(PREFIX + "a1-runner-r15.py", recipe["infra_paths"])
        self.assertNotIn(PREFIX + R14_PROFILE.name, recipe["proof_paths"])

    def test_profile_body_pin_is_present_and_updated_helper_pins_are_well_formed(self):
        body_pin = R15.get("a1_actual_body_sha256")
        self.assertIsInstance(body_pin, str)
        self.assertRegex(body_pin, re.compile(r"^[0-9a-f]{64}$"))
        self.assertNotIn("PLACEHOLDER", body_pin.upper())
        for pin in (R15.get("a1_runner_sha256"), R15.get("a1_entry_sha256"),
                    R15.get("reference_own_probe_sha256"),
                    *R15.get("a1_helper_sha256", {}).values()):
            with self.subTest(pin=pin):
                self.assertIsInstance(pin, str)
                self.assertRegex(pin, re.compile(r"^[0-9a-f]{64}$"))

    def test_r15_retains_r14_effective_chain_except_explicit_phase_and_byte_pins(self):
        mutable = {
            "account", "a1_entry_sha256", "a1_helper_sha256", "a1_runner_sha256",
            "reference_own_probe_sha256", "authorization_phase_id", "deadline_utc",
            "execution_mode", "main_deadline_utc", "phase", "start_utc", "status", "previous_build_id",
        }
        for key, value in R14.items():
            if key in mutable:
                continue
            with self.subTest(profile_field=key):
                self.assertIn(key, R15)
                self.assertEqual(R15[key], value)
        self.assertEqual(set(R15) - set(R14), {
            "a1_actual_body_sha256", "actual_body_dependencies_sha256",
            "registration_rationale", "body_action", "candidate_version", "baseline_r15_profile_sha256",
            "actual_c1_recovery_overlay", "merge_fractions_ast_dump_overlay"})
        self.assertEqual(R15["a1_source_runner_sha256"], R14["a1_source_runner_sha256"])

    def test_r13_semantic_tool_and_ownership_chain_is_retained(self):
        retained = (
            "base_translator_sha256", "selected_base_translator_sha256",
            "c_before", "c_after", "c_patch_sha256", "ghost_call_lifetime_inference",
            "focus_dead_code_scope_manifest_sha256", "focus_dead_code_scope_patch_sha256",
            "focus_dead_code_scope_result_sha256", "native_signature_manifest_sha256",
            "native_signature_patch_sha256", "r_before", "r_after", "r_patch_path",
            "r_patch_sha256", "r_representation_after", "shared_reference_own_normalization",
            "stable_threshold_pins_sha256", "std_source_sha256", "tool_head",
        )
        for key in retained:
            with self.subTest(chain_field=key):
                self.assertEqual(R13[key], R14[key])
                self.assertEqual(R14[key], R15[key])
        self.assertTrue(R15["shared_reference_own_normalization"]["shared_only"])
        self.assertEqual(R15["shared_reference_own_normalization"]["representation"],
                         "persistent-pointee-share")
        self.assertIn("unresolved lifetime cells only",
                      R15["ghost_call_lifetime_inference"]["scope"])


if __name__ == "__main__":
    unittest.main()
