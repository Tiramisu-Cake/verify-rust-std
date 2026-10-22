#!/usr/bin/env python3
"""Synthetic R19 admission, source, budget and publisher checks; no Cloud calls."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0]))
spec = importlib.util.spec_from_file_location("r19_control", HERE.parents[0] / "control.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

START = "2026-10-22T16:08:18Z"
MAIN = "2026-10-22T18:08:18Z"
END = "2026-10-22T18:38:18Z"


def account():
    return {
        "phase": m.R19_PHASE, "phase_id": m.R19_PHASE, "owner": "merge",
        "authorization_model": "bounded-cloud-budget", "authorization": m.R19_AUTHORIZATION,
        "status": "AUTHORIZED", "allowed_lanes": ["merge"],
        "ceiling_build_seconds": 3600, "used_build_seconds": 0,
        "spent_build_seconds": 0, "retired_seconds": 0,
        "remaining_build_seconds": 3600, "max_builds": None,
        "max_timeout_seconds": 1200, "report_reserve_seconds": 420,
        "builds": [], "active_build": None, "start_utc": START,
        "main_deadline_utc": MAIN, "deadline_utc": END,
        "carryover_allowed": False, "carry_seconds": 0,
        "publication_gate_path": m.R14_GATE_PATH, "profile_path": m.R19_PROFILE_PATH,
        "baseline_profile_sha256": m.R19_BASELINE_PROFILE_SHA256,
        "starting_source_sha": m.R19_STARTING_SOURCE_SHA,
        "starting_tool_commit": m.R17_CANDIDATE_TOOL_SHA,
        "baseline_sha": m.R19_BASELINE_SHA,
    }


def args(**overrides):
    values = {
        "phase_id": m.R19_PHASE, "owner": "merge",
        "ledger": HERE / "CURRENT-RECOVERY-R19-BUDGET-20261022.json",
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


class R19PhaseTests(unittest.TestCase):
    def setUp(self):
        self.clock = clock("2026-10-22T16:30:00+00:00")
        self.clock.start()
        self.addCleanup(self.clock.stop)

    def test_authorized_phase_binds_r19_account_source_and_upload_guard(self):
        with patch.object(m, "r14_read_selected_gate") as gate, \
             patch.object(m, "r19_validate_sources") as source:
            m.authorized_phase(args(), account())
        gate.assert_called_once_with("a" * 40)
        source.assert_called_once_with(m.R19_PROBE_SOURCE, "a" * 40)
        for phase in ("MERGE-ARCHIVE-SIZE-UPLOAD-R13-2026-10-21", m.R14_PHASE, m.R15_PHASE,
                      m.R16_PHASE, m.R17_PHASE, m.R18_PHASE, m.R19_PHASE):
            self.assertIs(m.required_upload_guard(phase), True)

    def test_r18_account_and_window_are_not_reopened(self):
        r18 = account()
        r18.update(phase=m.R18_PHASE, phase_id=m.R18_PHASE)
        with self.assertRaises(SystemExit):
            m.authorized_phase(args(phase_id=m.R18_PHASE, command="request"), r18)
        with self.assertRaises(SystemExit):
            m.authorized_phase(args(command="request",
                                    ledger=HERE / "CURRENT-RECOVERY-R18-BUDGET-20261022.json"), account())

    def test_terminal_reconcile_syncs_r19_spent_alias_before_authorization(self):
        ledger = account()
        ledger["builds"] = [{
            "dispatch_token": "dispatch-r19-test", "owner": "merge",
            "phase_id": m.R19_PHASE, "build_id": "build-r19-test",
            "reserved_seconds": 1260, "accounted": False,
        }]
        completed = {
            "status": "FAILURE", "createTime": "2026-10-22T16:20:00Z",
            "startTime": "2026-10-22T16:20:01Z", "finishTime": "2026-10-22T16:35:00Z",
        }
        with tempfile.TemporaryDirectory(prefix="r19-terminal-reconcile-") as temporary:
            root = Path(temporary)
            with patch.object(m.coordination, "COORDINATION", root / "coordinator"), \
                 patch.object(m, "invoke", return_value=completed):
                m.reconcile(root / "state", ledger, root / "R19-ledger.json")
            self.assertEqual(ledger["used_build_seconds"], 900)
            self.assertEqual(ledger["remaining_build_seconds"], 2700)
            self.assertEqual(ledger["spent_build_seconds"], 900)
            m.authorized_phase(args(command="request"), ledger)
            ledger["spent_build_seconds"] = 899
            with self.assertRaises(SystemExit):
                m.authorized_phase(args(command="request"), ledger)

    def test_account_identity_budget_and_phase_inputs_fail_closed(self):
        for field, value in (
            ("phase", "MERGE-OTHER"), ("phase_id", "MERGE-OTHER"), ("owner", "select"),
            ("authorization", "draft"), ("status", "PREPARED_NOT_REGISTERED"),
            ("allowed_lanes", ["select"]), ("ceiling_build_seconds", 3601),
            ("max_timeout_seconds", 1201), ("start_utc", "2026-10-22T16:08:19Z"),
            ("main_deadline_utc", "2026-10-22T18:08:19Z"), ("deadline_utc", "2026-10-22T18:38:19Z"),
            ("report_reserve_seconds", 419), ("carryover_allowed", True), ("carry_seconds", 1),
            ("publication_gate_path", "other"), ("profile_path", "other"),
            ("baseline_profile_sha256", "0" * 64), ("starting_source_sha", "0" * 40),
            ("starting_tool_commit", "0" * 40), ("baseline_sha", "0" * 40),
            ("remaining_build_seconds", 3599), ("used_build_seconds", -1),
            ("used_build_seconds", "0"), ("spent_build_seconds", 1), ("retired_seconds", 1),
            ("active_build", "dispatch-x"), ("builds", None),
            ("builds", [{"owner": "select", "phase_id": m.R19_PHASE}]),
            ("max_builds", 3),
        ):
            value_account = account(); value_account[field] = value
            with self.subTest(field=field, value=value), self.assertRaises(SystemExit):
                m.authorized_phase(args(command="request"), value_account)
        missing = account(); del missing["active_build"]
        with self.assertRaises(SystemExit):
            m.authorized_phase(args(command="request"), missing)
        for value in (
            args(phase_id="MERGE-OTHER"), args(owner="select"), args(lane="select"),
            args(source_mode="public-git"), args(infra_sha="b" * 40),
            args(timeout=1201), args(timeout=509), args(timeout=True),
            args(ledger=HERE / "other.json"),
        ):
            with self.subTest(args=value.__dict__), self.assertRaises(SystemExit):
                m.authorized_phase(value, account())

    def test_windows_reject_early_and_late_work(self):
        for moment, command in (("2026-10-22T16:08:17+00:00", "request"),
                                ("2026-10-22T18:08:18+00:00", "request"),
                                ("2026-10-22T18:08:18+00:00", "submit")):
            with self.subTest(moment=moment), clock(moment), \
                 patch.object(m, "r14_read_selected_gate"), \
                 patch.object(m, "r19_validate_sources"), self.assertRaises(SystemExit):
                m.authorized_phase(args(command=command, timeout=1200), account())
        # main+timeout1200+queue60 still ends before the absolute cutoff.
        with clock("2026-10-22T18:08:17+00:00"), patch.object(m, "r14_read_selected_gate"), \
             patch.object(m, "r19_validate_sources"):
            m.authorized_phase(args(timeout=1200), account())

    def test_source_preflight_crossing_main_deadline_fails_final_recheck(self):
        real = m.datetime.datetime
        current = [real.fromisoformat("2026-10-22T17:08:16+00:00")]

        class MovingClock(real):
            @classmethod
            def now(cls, tz=None): return current[0]

        for after in ("2026-10-22T18:08:18+00:00", "2026-10-22T18:40:00+00:00"):
            current[0] = real.fromisoformat("2026-10-22T17:08:16+00:00")

            def slow_source(*_):
                current[0] = real.fromisoformat(after)

            with self.subTest(after=after), patch.object(m.datetime, "datetime", MovingClock), \
                 patch.object(m, "r14_read_selected_gate"), \
                 patch.object(m, "r19_validate_sources", side_effect=slow_source), \
                 self.assertRaises(SystemExit):
                m.authorized_phase(args(timeout=1200), account())

    def test_final_deadline_check_binds_exact_r19_main_and_cutoff(self):
        with clock("2026-10-22T17:00:00+00:00"):
            m.r19_final_deadline_check(args(timeout=1200), account())
            changed = account(); changed["main_deadline_utc"] = "2026-10-22T18:30:00Z"
            with self.assertRaises(SystemExit):
                m.r19_final_deadline_check(args(timeout=1200), changed)
        with clock("2026-10-22T18:08:18+00:00"), self.assertRaises(SystemExit):
            m.r19_final_deadline_check(args(timeout=510), account())
        with clock("2026-10-22T18:08:17+00:00"), self.assertRaises(SystemExit):
            m.r19_final_deadline_check(args(timeout=1800), account())

    def test_source_or_gate_refusal_propagates_before_reservation(self):
        for target in ("r14_read_selected_gate", "r19_validate_sources"):
            with self.subTest(target=target), \
                 patch.object(m, "r14_read_selected_gate"), \
                 patch.object(m, "r19_validate_sources"), \
                 patch.object(m, target, side_effect=SystemExit("refused")), \
                 self.assertRaises(SystemExit):
                m.authorized_phase(args(), account())

    def test_recipe_adds_ledger_and_controls_and_drops_only_r11_retry_inputs(self):
        removed = sorted(m.R19_REMOVED_PATHS)
        before = {"schema": "s", "lane": "merge", "infra_paths": ["i"], "proof_paths": sorted(["a", "b", *removed])}
        selected = dict(before, proof_paths=sorted(["a", "b", *m.R19_ADDED_PATHS]))
        m.r19_validate_recipe_delta(before, selected)
        for bad in (
            dict(selected, lane="select"),
            dict(selected, proof_paths=sorted(["a", *m.R19_ADDED_PATHS])),
            dict(selected, proof_paths=sorted(["a", "b", m.R19_LEDGER_PATH])),
            dict(selected, proof_paths=sorted(["a", "b", *m.R19_ADDED_PATHS, "c"])),
            dict(selected, proof_paths=sorted(["a", "b", *m.R19_ADDED_PATHS, removed[0]])),
            dict(selected, proof_paths=list(reversed(selected["proof_paths"]))),
            dict(selected, proof_paths="a"),
            before,
        ):
            with self.subTest(bad=bad), self.assertRaises(SystemExit):
                m.r19_validate_recipe_delta(before, bad)

    def test_historical_ledger_profile_and_guard_closure_is_immutable(self):
        paths = {m.R18_LEDGER_PATH, m.R17_LEDGER_PATH, m.R16_LEDGER_PATH, m.R13_MODE_PATH,
                 m.R14_GATE_PATH, m.R17_PROFILE_PATH}
        tree = {path: ("100644", "blob", hashlib.sha1(path.encode()).hexdigest()) for path in paths}
        m.r19_validate_historical_closure(paths, tree, dict(tree))
        changed = dict(tree); changed[m.R17_LEDGER_PATH] = ("100644", "blob", "0" * 40)
        executable = dict(tree); executable[m.R17_PROFILE_PATH] = ("100755", "blob", tree[m.R17_PROFILE_PATH][2])
        missing = dict(tree); del missing[m.R14_GATE_PATH]
        for before, selected, check in ((tree, changed, paths), (tree, executable, paths),
                                        (tree, missing, paths), (missing, missing, paths - {m.R14_GATE_PATH})):
            with self.assertRaises(SystemExit):
                m.r19_validate_historical_closure(check, before, selected)

    def test_committed_probe_matches_r18_profile_ledger_and_current_pins(self):
        probe = m.R19_PROBE_SOURCE
        root = HERE.parents[2]
        profile = subprocess_show(root, probe, m.R19_PROFILE_PATH)
        self.assertEqual(hashlib.sha256(profile).hexdigest(), m.R19_BASELINE_PROFILE_SHA256)
        recipe = json.loads(subprocess_show(root, probe, "research/challenge-8/cloud-build/recipes/merge.json"))
        self.assertIn(m.R18_LEDGER_PATH, recipe["proof_paths"])
        self.assertTrue(m.R19_REMOVED_PATHS.issubset(recipe["proof_paths"]))
        self.assertFalse(m.R19_ADDED_PATHS & set(recipe["proof_paths"]))
        r18 = json.loads(subprocess_show(root, probe, m.R18_LEDGER_PATH))
        self.assertIsNone(r18.get("active_build"))
        repo = root.parent
        current = (repo / m.R19_PROFILE_PATH).read_bytes()
        self.assertEqual(hashlib.sha256(current).hexdigest(), m.R19_PROFILE_SHA256)
        patch_bytes = (repo / m.R17_PATCH_PATH).read_bytes()
        self.assertEqual(hashlib.sha256(patch_bytes).hexdigest(), m.R19_PATCH_SHA256)
        provider = (repo / m.R17_PROVIDER_OVERLAYS_PATH).read_bytes()
        old_provider = subprocess_show(root, probe, m.R17_PROVIDER_OVERLAYS_PATH)
        self.assertEqual(provider, old_provider.replace(m.R19_PROVIDER_OLD_PROVE_SHA256.encode(),
                                                        m.R19_PROVIDER_NEW_PROVE_SHA256.encode(), 1))
        prove = (repo / "research/challenge-8/merge/overnight/guard-ownership/insertion-onecell/prove.py").read_bytes()
        self.assertEqual(hashlib.sha256(prove).hexdigest(), m.R19_PROVIDER_NEW_PROVE_SHA256)
        with self.assertRaises(SystemExit):
            m.r19_validate_sources("0" * 40, "a" * 40)
        with self.assertRaises(SystemExit):
            m.r19_validate_sources(probe, "not-a-sha")

    def test_timeout_execute_budget_keeps_420_second_reserve_and_780_cap(self):
        for timeout, execute in ((510, 90), (1200, 780)):
            cfg = m.config("a" * 40, "a" * 40, "merge", timeout, "r19-synthetic-token")
            self.assertEqual(m.r17_validate_execute_budget(cfg, timeout), execute)
        for timeout in (509, 1201, True, "1200"):
            with self.subTest(timeout=timeout), self.assertRaises(SystemExit):
                m.r17_validate_execute_budget({}, timeout)

    def test_publisher_guard_route_includes_r19_without_config_change(self):
        root = HERE.parents[2]
        before = subprocess_show(root, m.R14_PROBE_SOURCE,
                                 "research/challenge-8/cloud-build/control.py").decode()
        current = (HERE.parents[0] / "control.py").read_text()
        m.r14_validate_publisher_control(before, current)
        broken = current.replace(",'MERGE-UNWIND-CLEANUP-R19-2026-10-22','MERGE-UNWIND-ACCEPTANCE-R20-2026-10-23')\n\ndef config(", ")\n\ndef config(", 1)
        self.assertNotEqual(broken, current)
        with self.assertRaises(SystemExit):
            m.r14_validate_publisher_control(before, broken)


def subprocess_show(root, commit, path):
    import subprocess
    return subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=root)


if __name__ == "__main__":
    unittest.main()
