#!/usr/bin/env python3
"""Synthetic R15 registration and publisher-preservation checks; no Cloud calls."""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE.parents[0]))
spec = importlib.util.spec_from_file_location("r15_control", HERE.parents[0] / "control.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def ledger():
    return {
        "phase": m.R15_PHASE, "owner": "merge", "authorization_model": "bounded-cloud-budget",
        "status": "AUTHORIZED", "allowed_lanes": ["merge"], "ceiling_build_seconds": 3600,
        "used_build_seconds": 0, "remaining_build_seconds": 3600, "max_builds": None,
        "max_timeout_seconds": 1200, "builds": [], "active_build": None,
        "start_utc": "2026-10-21T14:12:12Z", "main_deadline_utc": "2026-10-21T16:12:12Z",
        "deadline_utc": "2026-10-21T16:42:12Z", "carryover_allowed": False,
        "publication_gate_path": m.R14_GATE_PATH, "authorization": "R15 explicit task",
    }


def args(**overrides):
    values = {"phase_id": m.R15_PHASE, "owner": "merge", "ledger": HERE / ledger_name(),
              "command": "submit", "infra_sha": "a" * 40, "proof_sha": "a" * 40,
              "lane": "merge", "timeout": 1200, "source_mode": "pinned-objects"}
    values.update(overrides)
    return type("Args", (), values)()


def ledger_name():
    return m.R15_LEDGER_PATH.rsplit("/", 1)[-1]


class R15PhaseTests(unittest.TestCase):
    def setUp(self):
        real = m.datetime.datetime
        class Frozen(real):
            @classmethod
            def now(cls, tz=None): return real.fromisoformat("2026-10-21T15:00:00+00:00")
        self.clock = patch.object(m.datetime, "datetime", Frozen)
        self.clock.start()
        self.addCleanup(self.clock.stop)

    def authorize(self, account=None, command="submit", value=None):
        account = ledger() if account is None else account
        value = args(command=command) if value is None else value
        with patch.object(m, "r13_upload_mode", return_value="proof-r11"), \
             patch.object(m, "r14_read_selected_gate") as gate, \
             patch.object(m, "r15_validate_sources") as source:
            deadline = m.authorized_phase(value, account)
            if command == "submit":
                gate.assert_called_once_with("a" * 40)
                source.assert_called_once_with(m.R15_PROBE_SOURCE, "a" * 40)
            return deadline

    def test_authorized_submit_request_and_publisher_guard(self):
        self.authorize()
        self.authorize(command="request")
        self.assertIs(m.required_upload_guard(m.R15_PHASE), True)
        self.assertIs(m.required_upload_guard(m.R14_PHASE), True)
        self.assertIs(m.required_upload_guard("MERGE-LABEL-STORAGE-INVARIANT-R11-2026-10-21"), False)
        cfg = m.config("a" * 40, "a" * 40, "merge", 1200, "synthetic-test-token",
                       source_payload=None, r13_required=m.required_upload_guard(m.R15_PHASE))
        self.assertEqual(cfg["timeout"], "1200s")
        self.assertEqual(m.r15_set_execute_budget(cfg, 1200), 840)
        body = cfg["steps"][0]["args"][1]
        self.assertIn('"840s" bash', body)
        self.assertIn(" + 840 - 15 ", body)

    def test_account_registration_mismatches_refuse(self):
        for field, bad in (
            ("owner", "other"), ("authorization_model", "time-window"),
            ("ceiling_build_seconds", 3601), ("allowed_lanes", ["other"]),
            ("start_utc", "2026-10-21T14:12:13Z"),
            ("main_deadline_utc", "2026-10-21T16:12:13Z"),
            ("deadline_utc", "2026-10-21T16:42:13Z"), ("max_timeout_seconds", 1201),
            ("carryover_allowed", True), ("publication_gate_path", "other"),
            ("max_builds", 1), ("remaining_build_seconds", 3599), ("active_build", False),
            ("builds", [{"owner": "other", "phase_id": m.R15_PHASE}]),
        ):
            bad_ledger = ledger(); bad_ledger[field] = bad
            with self.subTest(field=field), self.assertRaises(SystemExit):
                self.authorize(bad_ledger)
        for field in ("publication_gate_path", "builds", "remaining_build_seconds", "used_build_seconds", "active_build"):
            bad_ledger = ledger(); bad_ledger.pop(field)
            with self.subTest(missing=field), self.assertRaises(SystemExit):
                self.authorize(bad_ledger)

    def test_submit_identity_deadline_mode_and_source_fail_closed(self):
        for changed in (args(infra_sha="b" * 40), args(source_mode="public-git"),
                        args(timeout=1201), args(timeout=449), args(lane="smoke-success")):
            with self.subTest(value=changed.__dict__), self.assertRaises(SystemExit):
                self.authorize(value=changed)
        with patch.object(m, "r13_upload_mode", return_value="synthetic-upload"), self.assertRaises(SystemExit):
            m.authorized_phase(args(), ledger())
        for field, value in (("r14_read_selected_gate", None), ("r15_validate_sources", None)):
            with patch.object(m, "r13_upload_mode", return_value="proof-r11"), \
                 patch.object(m, "r14_read_selected_gate") as gate, \
                 patch.object(m, "r15_validate_sources") as source:
                (gate if field == "r14_read_selected_gate" else source).side_effect = SystemExit("closed")
                with self.subTest(gate=field), self.assertRaises(SystemExit):
                    m.authorized_phase(args(), ledger())

    def test_window_and_absolute_deadline_are_enforced(self):
        real = m.datetime.datetime
        class Late(real):
            @classmethod
            def now(cls, tz=None): return real.fromisoformat("2026-10-21T16:12:12+00:00")
        with patch.object(m.datetime, "datetime", Late), self.assertRaises(SystemExit):
            m.authorized_phase(args(), ledger())
        class NearCutoff(real):
            @classmethod
            def now(cls, tz=None): return real.fromisoformat("2026-10-21T16:21:13+00:00")
        with patch.object(m.datetime, "datetime", NearCutoff), self.assertRaises(SystemExit):
            m.authorized_phase(args(timeout=1200), ledger())

    def test_recipe_allows_proof_input_changes_with_exact_registration_paths(self):
        before = {"schema": "smallsort-cloud-recipe-v1", "lane": "merge", "entrypoint": "run-merge.sh",
                  "infra_paths": ["run-merge.sh"],
                  "proof_paths": sorted(["a.py", *m.R15_RECIPE_REMOVALS, "z.py"])}
        after = copy.deepcopy(before)
        after["proof_paths"] += [m.R15_LEDGER_PATH]
        after["proof_paths"] = [path for path in after["proof_paths"]
                                 if path not in m.R15_RECIPE_REMOVALS]
        after["proof_paths"].sort()
        m.r15_validate_recipe_delta(before, after)
        for bad in (
            dict(after, baseline_sha="f" * 40),
            dict(after, proof_paths=[m.R15_LEDGER_PATH, m.R15_PREFLIGHT_PATH, "z.py"]),
            dict(after, proof_paths=after["proof_paths"] + ["unexpected.py"]),
        ):
            with self.subTest(recipe=bad), self.assertRaises(SystemExit):
                m.r15_validate_recipe_delta(before, bad)

    def test_r14_publisher_guards_remain_exact_under_r15_registration(self):
        probe = subprocess.check_output(
            ["git", "show", f"{m.R14_PROBE_SOURCE}:research/challenge-8/cloud-build/control.py"], cwd=ROOT
        ).decode()
        selected = (HERE.parents[0] / "control.py").read_text()
        m.r14_validate_publisher_control(probe, selected)
        mutated = selected.replace("CLOUDSDK_STORAGE_PARALLEL_COMPOSITE_UPLOAD_ENABLED=False",
                                   "CLOUDSDK_STORAGE_PARALLEL_COMPOSITE_UPLOAD_ENABLED=True", 1)
        with self.assertRaises(SystemExit):
            m.r14_validate_publisher_control(probe, mutated)

    def test_execute_budget_reserves_publication_and_refuses_bad_shapes(self):
        for bad_timeout in (449, 1201, True, "1200"):
            with self.subTest(timeout=bad_timeout), self.assertRaises(SystemExit):
                m.r15_set_execute_budget({}, bad_timeout)
        cfg = m.config("a" * 40, "a" * 40, "merge", 1200, "synthetic-test-token")
        cfg["steps"][0]["args"][1] = cfg["steps"][0]["args"][1].replace('"1130s" bash', '"1129s" bash')
        with self.assertRaises(SystemExit):
            m.r15_set_execute_budget(cfg, 1200)


if __name__ == "__main__":
    unittest.main()
