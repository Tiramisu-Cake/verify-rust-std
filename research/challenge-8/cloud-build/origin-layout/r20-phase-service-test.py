#!/usr/bin/env python3
"""Synthetic R20 phase admission checks; no Cloud calls or proof execution."""
from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0]))
spec = importlib.util.spec_from_file_location("r20_control", HERE.parents[0] / "control.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def account():
    return {
        "phase": m.R20_PHASE, "phase_id": m.R20_PHASE, "owner": "merge",
        "authorization_model": "bounded-cloud-budget", "authorization": m.R20_AUTHORIZATION,
        "schema": "smallsort-prepared-session-ledger-v1", "task_id": m.R20_TASK_ID,
        "status": "AUTHORIZED", "allowed_lanes": ["merge"],
        "ceiling_build_seconds": 3600, "used_build_seconds": 0, "spent_build_seconds": 0,
        "retired_seconds": 0, "remaining_build_seconds": 3600, "max_builds": None,
        "maximum_builds": None,
        "max_timeout_seconds": 1200, "maximum_build_timeout_seconds": 1200,
        "report_reserve_seconds": 420, "builds": [], "active_build": None,
        "start_utc": m.R20_START, "main_deadline_utc": m.R20_MAIN_DEADLINE,
        "deadline_utc": m.R20_DEADLINE, "carryover_allowed": False, "carry_seconds": 0,
        "publication_gate_path": m.R14_GATE_PATH, "profile_path": m.R20_PROFILE_PATH,
        "baseline_profile_sha256": m.R20_PROFILE_SHA256,
        "starting_source_sha": m.R20_STARTING_SOURCE_SHA,
        "starting_tool_commit": m.R20_STARTING_TOOL_COMMIT, "baseline_sha": m.R20_BASELINE_SHA,
    }


def args(**overrides):
    values = {
        "phase_id": m.R20_PHASE, "owner": "merge",
        "ledger": HERE / "CURRENT-RECOVERY-R20-BUDGET-20261023.json",
        "command": "submit", "infra_sha": "a" * 40, "proof_sha": "a" * 40,
        "lane": "merge", "timeout": 1200, "source_mode": "pinned-objects",
    }
    values.update(overrides)
    return type("Args", (), values)()


def clock(moment):
    real = m.datetime.datetime

    class Frozen(real):
        @classmethod
        def now(cls, tz=None):
            return real.fromisoformat(moment)

    return patch.object(m.datetime, "datetime", Frozen)


class R20PhaseTests(unittest.TestCase):
    def setUp(self):
        self.clock = clock("2026-10-22T20:30:00+00:00")
        self.clock.start()
        self.addCleanup(self.clock.stop)

    def test_exact_phase_account_source_gate_and_upload_routing(self):
        with patch.object(m, "r14_read_selected_gate") as gate, \
             patch.object(m, "r20_validate_sources") as source:
            m.authorized_phase(args(), account())
        gate.assert_called_once_with("a" * 40)
        source.assert_called_once_with(m.R20_PROBE_SOURCE, "a" * 40)
        self.assertTrue(m.required_upload_guard(m.R20_PHASE))
        for phase in (m.R17_PHASE, m.R18_PHASE, m.R19_PHASE):
            self.assertTrue(m.required_upload_guard(phase))

    def test_prepared_ledger_and_old_phase_cannot_dispatch(self):
        for status, phase in (("PREPARED_NOT_REGISTERED", m.R20_PHASE),
                              ("AUTHORIZED", m.R19_PHASE), ("AUTHORIZED", m.R18_PHASE)):
            ledger = account(); ledger.update(status=status, phase=phase, phase_id=phase)
            with self.subTest(status=status, phase=phase), self.assertRaises(SystemExit):
                m.authorized_phase(args(phase_id=phase, command="request"), ledger)

    def test_account_identity_pins_types_and_budget_fail_closed(self):
        bad = (
            ("owner", "select"), ("authorization", "draft"), ("allowed_lanes", ["select"]),
            ("task_id", "old-task"), ("maximum_builds", 3),
            ("ceiling_build_seconds", True), ("max_timeout_seconds", 1201),
            ("maximum_build_timeout_seconds", 1199), ("start_utc", "2026-10-22T20:08:01Z"),
            ("main_deadline_utc", "2026-10-22T22:08:01Z"),
            ("deadline_utc", "2026-10-22T22:38:01Z"), ("report_reserve_seconds", 419),
            ("carryover_allowed", True), ("carry_seconds", 1),
            ("publication_gate_path", "other"), ("profile_path", "other"),
            ("baseline_profile_sha256", "0" * 64), ("starting_source_sha", "0" * 40),
            ("starting_tool_commit", "0" * 40), ("baseline_sha", "0" * 40),
            ("remaining_build_seconds", 3599), ("used_build_seconds", -1),
            ("used_build_seconds", True), ("spent_build_seconds", 1),
            ("retired_seconds", 1), ("active_build", "dispatch-x"), ("builds", None),
            ("builds", [{"owner": "select", "phase_id": m.R20_PHASE}]), ("max_builds", 3),
        )
        for key, value in bad:
            ledger = account(); ledger[key] = value
            with self.subTest(key=key, value=value), self.assertRaises(SystemExit):
                m.authorized_phase(args(command="request"), ledger)
        missing = account(); del missing["active_build"]
        with self.assertRaises(SystemExit):
            m.authorized_phase(args(command="request"), missing)

    def test_submit_requires_same_full_pinned_source_merge_and_valid_timeout(self):
        for values in (
            {"owner": "select"}, {"lane": "select"}, {"source_mode": "public-git"},
            {"infra_sha": "b" * 40}, {"timeout": 1201}, {"timeout": 509},
            {"timeout": True}, {"ledger": HERE / "other.json"},
        ):
            with self.subTest(values=values), self.assertRaises(SystemExit):
                m.authorized_phase(args(**values), account())

    def test_window_edges_and_queue_reserve(self):
        cases = (("2026-10-22T20:07:59+00:00", "request"),
                 ("2026-10-22T22:08:00+00:00", "request"),
                 ("2026-10-22T22:08:00+00:00", "submit"))
        for moment, command in cases:
            with self.subTest(moment=moment), clock(moment), self.assertRaises(SystemExit):
                m.authorized_phase(args(command=command), account())
        # At the last main-window second, the maximum timeout and queue reserve
        # still fit before the absolute cutoff.
        with clock("2026-10-22T22:07:59+00:00"), patch.object(m, "r14_read_selected_gate"), \
             patch.object(m, "r20_validate_sources"):
            m.authorized_phase(args(timeout=1200), account())
        with clock("2026-10-22T22:07:59+00:00"), patch.object(m, "r14_read_selected_gate"), \
             patch.object(m, "r20_validate_sources"):
            m.authorized_phase(args(timeout=510), account())

    def test_final_recheck_rejects_main_crossing_and_absolute_deadline(self):
        real = m.datetime.datetime
        now = [real.fromisoformat("2026-10-22T21:00:00+00:00")]

        class MovingClock(real):
            @classmethod
            def now(cls, tz=None): return now[0]

        for later in ("2026-10-22T22:08:00+00:00", "2026-10-22T22:38:01+00:00"):
            now[0] = real.fromisoformat("2026-10-22T21:00:00+00:00")

            def slow(*_): now[0] = real.fromisoformat(later)

            with self.subTest(later=later), patch.object(m.datetime, "datetime", MovingClock), \
                 patch.object(m, "r14_read_selected_gate"), patch.object(m, "r20_validate_sources", side_effect=slow), \
                 self.assertRaises(SystemExit):
                m.authorized_phase(args(timeout=1200), account())
        with clock("2026-10-22T22:07:59+00:00"), self.assertRaises(SystemExit):
            m.r20_final_deadline_check(args(timeout=1800), account())

    def test_recipe_delta_and_historical_closure_are_exact(self):
        old = sorted({"a", "b", *m.R20_REMOVED_PATHS})
        before = {"schema": "smallsort-cloud-recipe-v1", "lane": "merge", "infra_paths": ["i"], "proof_paths": old}
        selected = dict(before, proof_paths=sorted(({"a", "b"} | m.R20_ADDED_PATHS)))
        m.r20_validate_recipe_delta(before, selected)
        for bad in (dict(selected, lane="select"), dict(selected, proof_paths=list(reversed(selected["proof_paths"]))),
                    dict(selected, proof_paths=sorted({"a", *m.R20_ADDED_PATHS})),
                    dict(selected, proof_paths=sorted({"a", "b", *m.R20_ADDED_PATHS, "extra"}))):
            with self.subTest(bad=bad), self.assertRaises(SystemExit):
                m.r20_validate_recipe_delta(before, bad)
        paths = {m.R19_LEDGER_PATH, m.R18_LEDGER_PATH, m.R17_LEDGER_PATH, m.R16_LEDGER_PATH,
                 m.R13_MODE_PATH, m.R14_GATE_PATH, m.R17_PROFILE_PATH, m.R20_PROFILE_PATH}
        tree = {p: ("100644", "blob", hashlib.sha1(p.encode()).hexdigest()) for p in paths}
        m.r20_validate_historical_closure(paths, tree, dict(tree))
        changed = dict(tree); changed[m.R19_LEDGER_PATH] = ("100644", "blob", "0" * 40)
        with self.assertRaises(SystemExit):
            m.r20_validate_historical_closure(paths, tree, changed)

    def test_wrong_source_and_candidate_pins_fail_closed(self):
        with self.assertRaises(SystemExit):
            m.r20_validate_sources("0" * 40, "a" * 40)
        with self.assertRaises(SystemExit):
            m.r20_validate_sources(m.R20_PROBE_SOURCE, "not-a-sha")
        good_profile = b"profile"; good_provider = m.R20_PROVIDER_PROVE_SHA256.encode()
        with self.assertRaises(SystemExit):
            m.r20_validate_candidate_pins(good_profile, good_profile, good_profile, b"patch",
                                          good_provider, b"changed", good_provider)
        with self.assertRaises(SystemExit):
            m.r20_validate_candidate_pins(good_profile, b"wrong", good_profile, b"patch",
                                          good_provider, good_provider, good_provider)

    def test_execute_budget_preserves_reserve_and_780_second_cap(self):
        for timeout, execute in ((510, 90), (1200, 780)):
            cfg = m.config("a" * 40, "a" * 40, "merge", timeout, "r20-synthetic-token")
            self.assertEqual(m.r17_validate_execute_budget(cfg, timeout), execute)
        for timeout in (509, 1201, True, "1200"):
            with self.subTest(timeout=timeout), self.assertRaises(SystemExit):
                m.r17_validate_execute_budget({}, timeout)

    def test_publisher_ast_keeps_config_fixed_and_routes_r20_guard(self):
        import subprocess
        root = HERE.parents[2]
        baseline = subprocess.check_output(["git", "show",
            m.R14_PROBE_SOURCE + ":research/challenge-8/cloud-build/control.py"], cwd=root).decode()
        current = (HERE.parents[0] / "control.py").read_text()
        m.r14_validate_publisher_control(baseline, current)
        broken = current.replace(",'MERGE-UNWIND-ACCEPTANCE-R20-2026-10-23','MERGE-CALLER-ACCEPTANCE-R21-2026-10-23','MERGE-CALLER-ACCEPTANCE-R22-2026-10-23',R23_PHASE)", ",'MERGE-CALLER-ACCEPTANCE-R21-2026-10-23','MERGE-CALLER-ACCEPTANCE-R22-2026-10-23',R23_PHASE)", 1)
        self.assertNotEqual(broken, current)
        with self.assertRaises(SystemExit):
            m.r14_validate_publisher_control(baseline, broken)

    def test_reconcile_syncs_r20_spent_seconds_alias(self):
        ledger = account()
        ledger["builds"] = [{"dispatch_token": "dispatch-r20-test", "owner": "merge",
            "phase_id": m.R20_PHASE, "build_id": "build-r20-test", "reserved_seconds": 1260,
            "accounted": False}]
        completed = {"status": "FAILURE", "createTime": "2026-10-22T20:20:00Z",
                     "startTime": "2026-10-22T20:20:01Z", "finishTime": "2026-10-22T20:35:00Z"}
        import tempfile
        with tempfile.TemporaryDirectory(prefix="r20-terminal-reconcile-") as temporary:
            root = Path(temporary)
            with patch.object(m.coordination, "COORDINATION", root / "coordinator"), \
                 patch.object(m, "invoke", return_value=completed):
                m.reconcile(root / "state", ledger, root / "R20-ledger.json")
        self.assertEqual(ledger["used_build_seconds"], 900)
        self.assertEqual(ledger["remaining_build_seconds"], 2700)
        self.assertEqual(ledger["spent_build_seconds"], 900)


if __name__ == "__main__":
    unittest.main()
