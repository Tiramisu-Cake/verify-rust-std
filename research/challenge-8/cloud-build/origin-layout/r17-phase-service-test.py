#!/usr/bin/env python3
"""Synthetic R17 admission, source-profile, budget and publisher checks; no Cloud calls."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0]))
spec = importlib.util.spec_from_file_location("r17_control", HERE.parents[0] / "control.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

START = "2026-10-21T18:33:50Z"
MAIN = "2026-10-21T20:33:50Z"
END = "2026-10-21T21:03:50Z"
PROFILE_HASH = "eb61e49397cd9973ec12d1675bd8bd4867c7374de22e7c1c6a8a58e991266375"
SOURCE = "6fd50c699500cbac5c65912174d4aa49b49db19f"
TOOL = "660b576b6b1608db913c51e0785b443a8733396f"
SOURCE_APPLICABILITY = (
    "paired RawPtr bare local only; exact mutability/full MIR and decoded local type/place; "
    "existing equal-state allocation reconciliation; no borrow or memory authority"
)


def account():
    return {
        "phase": m.R17_PHASE, "phase_id": m.R17_PHASE, "owner": "merge",
        "authorization_model": "bounded-cloud-budget", "authorization": m.R17_AUTHORIZATION,
        "status": "AUTHORIZED", "allowed_lanes": ["merge"],
        "ceiling_build_seconds": 3600, "used_build_seconds": 0,
        "spent_build_seconds": 0, "retired_seconds": 0,
        "remaining_build_seconds": 3600, "max_builds": None,
        "max_timeout_seconds": 1200, "report_reserve_seconds": 420,
        "builds": [], "active_build": None, "start_utc": START,
        "main_deadline_utc": MAIN, "deadline_utc": END,
        "carryover_allowed": False, "carry_seconds": 0,
        "publication_gate_path": m.R14_GATE_PATH, "profile_path": m.R17_PROFILE_PATH,
        "baseline_profile_sha256": PROFILE_HASH, "starting_source_sha": SOURCE,
        "starting_tool_commit": TOOL, "baseline_sha": "137cbf8ed13653c83a56975449c544ed7b348365",
    }


def args(**overrides):
    values = {
        "phase_id": m.R17_PHASE, "owner": "merge",
        "ledger": HERE / "CURRENT-RECOVERY-R17-BUDGET-20261021.json",
        "command": "submit", "infra_sha": "a" * 40, "proof_sha": "a" * 40,
        "lane": "merge", "timeout": 1200, "source_mode": "pinned-objects",
    }
    values.update(overrides)
    return type("Args", (), values)()


def profile_pair():
    old = {
        "effective_tool_commit": TOOL, "refiner_core_source_sha256": "1" * 64,
        "guard_return_trace_patch_sha256": "2" * 64,
        "ordered_patch_chain": [{"path": f"p{i}.patch", "sha256": f"{i % 16:x}" * 64} for i in range(18)] +
            [{"path": m.R17_PATCH_PATH, "sha256": "2" * 64}],
    }
    new = copy.deepcopy(old)
    candidate = m.R17_CANDIDATE_TOOL_SHA
    source_hash = m.R17_REFINER_CORE_SOURCE_SHA256
    patch_hash = m.R17_PATCH_SHA256
    new["effective_tool_commit"] = candidate
    new["refiner_core_source_sha256"] = source_hash
    new["guard_return_trace_patch_sha256"] = patch_hash
    new["ordered_patch_chain"][-1]["sha256"] = patch_hash
    new[m.R17_PROFILE_REGISTRATION] = {
        "schema": "merge-r17-profile-registration-v1", "phase_id": m.R17_PHASE,
        "baseline_profile_path": m.R17_PROFILE_PATH, "starting_tool_commit": TOOL,
        "starting_source_sha": SOURCE, "owner": "merge", "lane": "merge",
        "candidate_tool_commit": candidate,
        "tool_source_paths": ["src/refinement_checker/refinement_checker.ml"],
        "source_applicability": SOURCE_APPLICABILITY,
    }
    return old, new


class R17PhaseTests(unittest.TestCase):
    def setUp(self):
        real = m.datetime.datetime

        class Frozen(real):
            @classmethod
            def now(cls, tz=None):
                return real.fromisoformat("2026-10-21T18:34:00+00:00")

        self.clock = patch.object(m.datetime, "datetime", Frozen)
        self.clock.start()
        self.addCleanup(self.clock.stop)

    def test_authorized_phase_binds_r17_account_source_and_upload_guard(self):
        with patch.object(m, "r14_read_selected_gate") as gate, \
             patch.object(m, "r17_validate_sources") as source:
            m.authorized_phase(args(), account())
        gate.assert_called_once_with("a" * 40)
        source.assert_called_once_with(m.R17_PROBE_SOURCE, "a" * 40)
        self.assertIs(m.required_upload_guard(m.R17_PHASE), True)
        for phase in (m.R13_PHASE if hasattr(m, "R13_PHASE") else "MERGE-ARCHIVE-SIZE-UPLOAD-R13-2026-10-21",
                      m.R14_PHASE, m.R15_PHASE, m.R16_PHASE):
            self.assertIs(m.required_upload_guard(phase), True)

    def test_account_identity_budget_and_phase_inputs_fail_closed(self):
        for field, value in (
            ("phase", "MERGE-OTHER"), ("owner", "select"), ("authorization", "draft"),
            ("status", "PREPARED_NOT_REGISTERED"), ("allowed_lanes", ["select"]),
            ("ceiling_build_seconds", 3601), ("max_timeout_seconds", 1201),
            ("start_utc", "2026-10-21T18:33:51Z"), ("main_deadline_utc", "2026-10-21T20:33:51Z"),
            ("deadline_utc", "2026-10-21T21:03:51Z"), ("report_reserve_seconds", 419),
            ("carryover_allowed", True), ("carry_seconds", 1),
            ("publication_gate_path", "other"), ("profile_path", "other"),
            ("baseline_profile_sha256", "0" * 64), ("starting_source_sha", "0" * 40),
            ("starting_tool_commit", "0" * 40), ("remaining_build_seconds", 3599),
            ("spent_build_seconds", 1), ("retired_seconds", 1),
            ("active_build", False), ("builds", [{"owner": "select", "phase_id": m.R17_PHASE}]),
        ):
            value_account = account(); value_account[field] = value
            with self.subTest(field=field), self.assertRaises(SystemExit):
                m.authorized_phase(args(command="request"), value_account)
        for value in (
            args(phase_id="MERGE-OTHER"), args(owner="select"), args(lane="select"),
            args(source_mode="public-git"), args(infra_sha="b" * 40),
            args(timeout=1201), args(timeout=509),
        ):
            with self.subTest(args=value.__dict__), self.assertRaises(SystemExit):
                m.authorized_phase(value, account())

    def test_main_and_absolute_windows_reject_late_work(self):
        real = m.datetime.datetime

        class MainExpired(real):
            @classmethod
            def now(cls, tz=None): return real.fromisoformat("2026-10-21T20:33:50+00:00")

        with patch.object(m.datetime, "datetime", MainExpired), self.assertRaises(SystemExit):
            m.authorized_phase(args(command="request"), account())

        class InsufficientAbsolute(real):
            @classmethod
            def now(cls, tz=None): return real.fromisoformat("2026-10-21T20:43:51+00:00")

        with patch.object(m.datetime, "datetime", InsufficientAbsolute), self.assertRaises(SystemExit):
            m.authorized_phase(args(timeout=1200), account())

    def test_source_preflight_crossing_main_deadline_fails_final_recheck(self):
        real = m.datetime.datetime
        current = [real.fromisoformat("2026-10-21T20:33:49+00:00")]

        class MovingClock(real):
            @classmethod
            def now(cls, tz=None): return current[0]

        def slow_source(*_):
            current[0] = real.fromisoformat("2026-10-21T20:33:50+00:00")

        with patch.object(m.datetime, "datetime", MovingClock), \
             patch.object(m, "r14_read_selected_gate"), \
             patch.object(m, "r17_validate_sources", side_effect=slow_source):
            with self.assertRaises(SystemExit):
                m.authorized_phase(args(timeout=510), account())

    def test_timeout_execute_budget_keeps_420_second_reserve_and_780_cap(self):
        for timeout, execute in ((510, 90), (1200, 780)):
            cfg = m.config("a" * 40, "a" * 40, "merge", timeout, "r17-synthetic-token")
            self.assertEqual(m.r17_validate_execute_budget(cfg, timeout), execute)
            body = cfg["steps"][0]["args"][1]
            self.assertIn(f'"{execute}s" bash', body)
            self.assertIn(f" + {execute} - 15 ", body)
        for timeout in (89, 419, 509, 1201, True, "1200"):
            with self.subTest(timeout=timeout), self.assertRaises(SystemExit):
                m.r17_validate_execute_budget({}, timeout)
        cfg = m.config("a" * 40, "a" * 40, "merge", 1200, "r17-synthetic-token")
        cfg["steps"][0]["args"][1] = cfg["steps"][0]["args"][1].replace('"1130s" bash', '"1129s" bash')
        with self.assertRaises(SystemExit):
            m.r17_validate_execute_budget(cfg, 1200)

    def test_recipe_adds_only_r17_ledger_and_baseline_profile(self):
        before = {"schema": "smallsort-cloud-recipe-v1", "lane": "merge",
                  "entrypoint": "run-merge.sh", "infra_paths": ["run-merge.sh"],
                  "proof_paths": [m.R16_LEDGER_PATH,
                      "research/challenge-8/cloud-build/origin-layout/GLUE-PROFILE.json"]}
        selected = copy.deepcopy(before)
        selected["proof_paths"] += [m.R17_LEDGER_PATH, m.R17_PROFILE_PATH, m.R17_CONTROLS_PATH]
        selected["proof_paths"].sort()
        m.r17_validate_recipe_delta(before, selected)
        bad = copy.deepcopy(selected); bad["proof_paths"].remove(m.R16_LEDGER_PATH)
        with self.assertRaises(SystemExit): m.r17_validate_recipe_delta(before, bad)
        bad = copy.deepcopy(selected); bad["infra_paths"] = ["changed.sh"]
        with self.assertRaises(SystemExit): m.r17_validate_recipe_delta(before, bad)

    def test_profile_delta_accepts_only_candidate_refiner_pin_and_registration(self):
        old, new = profile_pair()
        m.r17_validate_profile_delta(json.dumps(old), json.dumps(new))
        for mutate in (
            lambda item: item.update(semantic_delta="broadened"),
            lambda item: item["ordered_patch_chain"].__setitem__(0, {"path": "changed", "sha256": "f" * 64}),
            lambda item: item[m.R17_PROFILE_REGISTRATION].update(source_applicability="address only"),
            lambda item: item[m.R17_PROFILE_REGISTRATION].update(candidate_tool_commit="bad"),
        ):
            bad = copy.deepcopy(new); mutate(bad)
            with self.subTest(bad=bad), self.assertRaises(SystemExit):
                m.r17_validate_profile_delta(json.dumps(old), json.dumps(bad))

    def test_worktree_profile_matches_the_exact_candidate_pins(self):
        baseline_path = HERE / "R17-BASELINE-PROFILE-20261021.json"
        selected_path = HERE / "GLUE-PROFILE.json"
        baseline = baseline_path.read_bytes()
        selected = selected_path.read_bytes()
        self.assertEqual(hashlib.sha256(baseline).hexdigest(), PROFILE_HASH)
        if selected == baseline:
            self.assertEqual(hashlib.sha256(selected).hexdigest(), PROFILE_HASH)
        else:
            m.r17_validate_profile_delta(baseline, selected)

    def test_historical_ledger_and_publication_guard_are_immutable(self):
        paths = {m.R16_LEDGER_PATH, m.R13_MODE_PATH, m.R14_GATE_PATH}
        baseline = {path: ("100644", "blob", str(i) * 40) for i, path in enumerate(sorted(paths), 1)}
        m.r17_validate_historical_closure(paths, baseline, copy.deepcopy(baseline))
        changed = copy.deepcopy(baseline); changed[m.R16_LEDGER_PATH] = ("100644", "blob", "f" * 40)
        with self.assertRaises(SystemExit): m.r17_validate_historical_closure(paths, baseline, changed)
        self.assertEqual(m.R14_UPLOAD_SHELL_SHA256,
                         "677740c98b0389c77c40804a825037b598c46c095fc0fecd9a30b80c5922ef64")

    def test_wrong_probe_source_and_worktree_blob_or_mode_refuse(self):
        with self.assertRaises(SystemExit): m.r17_validate_sources("f" * 40, "a" * 40)
        with self.assertRaises(SystemExit): m.r17_validate_profile_baseline(b"old", b"changed")


if __name__ == "__main__":
    unittest.main()
