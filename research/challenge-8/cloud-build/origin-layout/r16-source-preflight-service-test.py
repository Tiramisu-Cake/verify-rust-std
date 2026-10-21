#!/usr/bin/env python3
"""Synthetic R16 recipe/source-preflight checks; no Cloud calls."""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0]))
spec = importlib.util.spec_from_file_location("r16_source_control", HERE.parents[0] / "control.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
preflight_spec = importlib.util.spec_from_file_location("r16_preflight", HERE / "r16-source-preflight.py")
preflight = importlib.util.module_from_spec(preflight_spec)
preflight_spec.loader.exec_module(preflight)


def account():
    return {
        "phase": m.R16_PHASE, "owner": "merge", "authorization_model": "bounded-cloud-budget",
        "status": "AUTHORIZED", "allowed_lanes": ["merge"], "ceiling_build_seconds": 3600,
        "used_build_seconds": 0, "remaining_build_seconds": 3600, "max_builds": None,
        "max_timeout_seconds": 1200, "builds": [], "active_build": None,
        "start_utc": "2026-10-21T16:08:24Z", "main_deadline_utc": "2026-10-21T18:08:24Z",
        "deadline_utc": "2026-10-21T18:38:24Z", "carryover_allowed": False,
        "publication_gate_path": m.R14_GATE_PATH,
        "authorization": "CURRENT-TASK R16: autonomous source-preserving caller unsize/lifetime and actual insert_tail/CURRENT proof; independent Luna HIGH review and Cloud regressions; fresh3600 no carry.",
    }


class R16SourcePreflightTests(unittest.TestCase):
    def test_recipe_allows_only_the_new_r16_ledger(self):
        before = {"schema": "smallsort-cloud-recipe-v1", "lane": "merge",
                  "entrypoint": "run-merge.sh", "infra_paths": ["run-merge.sh"],
                  "proof_paths": ["a.py", "z.py"]}
        selected = copy.deepcopy(before)
        selected["proof_paths"].append(m.R16_LEDGER_PATH)
        selected["proof_paths"].sort()
        m.r16_validate_recipe_delta(before, selected)
        for bad in (
            dict(selected, proof_paths=selected["proof_paths"] + [m.R15_LEDGER_PATH]),
            dict(selected, infra_paths=["changed.sh"]),
            dict(selected, baseline_sha="f" * 40),
        ):
            with self.subTest(recipe=bad), self.assertRaises(SystemExit):
                m.r16_validate_recipe_delta(before, bad)

    def test_source_baseline_and_transport_caps_are_fixed(self):
        self.assertEqual(m.R16_PROBE_SOURCE, "a89d091c95e50d3aab961654f54668e0f631e3be")
        self.assertEqual(m.r15_validate_transport_size(0), 0)
        with self.assertRaises(SystemExit):
            m.r16_validate_sources("f" * 40, "a" * 40)
        with self.assertRaises(SystemExit):
            m.r15_validate_transport_size(571568)

    def test_historical_r13_mode_and_r14_gate_are_byte_identical(self):
        paths = {m.R13_MODE_PATH, m.R14_GATE_PATH, m.R15_LEDGER_PATH}
        baseline = {
            m.R13_MODE_PATH: ("100644", "blob", "1" * 40),
            m.R14_GATE_PATH: ("100644", "blob", "2" * 40),
            m.R15_LEDGER_PATH: ("100644", "blob", "3" * 40),
        }
        m.r16_validate_historical_closure(paths, baseline, copy.deepcopy(baseline))
        for changed in (
            dict(baseline, **{m.R13_MODE_PATH: ("100644", "blob", "f" * 40)}),
            {path: value for path, value in baseline.items() if path != m.R13_MODE_PATH},
        ):
            with self.subTest(changed=changed), self.assertRaises(SystemExit):
                m.r16_validate_historical_closure(paths, baseline, changed)

    def test_phase_account_accepts_fully_accounted_terminal_build(self):
        value = account()
        value.update(used_build_seconds=815, remaining_build_seconds=2785)
        value["builds"] = [{
            "owner": "merge", "phase_id": m.R16_PHASE,
            "build_id": "9487d6d1-14aa-4370-bc0b-7ac57279fb7b",
            "status": "FAILURE", "accounted": True, "build_seconds": 815,
        }]
        preflight.validate_phase_account(value, m)

    def test_phase_account_rejects_malformed_budget_or_unresolved_build(self):
        for update, mutate in (
            ({"authorization": "different authorized task"}, None),
            ({"used_build_seconds": True}, None),
            ({"remaining_build_seconds": 2784, "used_build_seconds": 815}, None),
            ({"used_build_seconds": 815, "remaining_build_seconds": 2785},
             {"status": "QUEUED", "accounted": True, "build_seconds": 815}),
            ({"used_build_seconds": 815, "remaining_build_seconds": 2785},
             {"status": "FAILURE", "accounted": False, "build_seconds": 815}),
            ({"used_build_seconds": 815, "remaining_build_seconds": 2785},
             {"status": "FAILURE", "accounted": True, "build_seconds": 814}),
        ):
            value = account()
            value.update(update)
            if mutate is not None:
                entry = {"owner": "merge", "phase_id": m.R16_PHASE,
                         "build_id": "synthetic-build-id", "status": "FAILURE",
                         "accounted": True, "build_seconds": 815}
                entry.update(mutate)
                value["builds"] = [entry]
            with self.subTest(update=update, mutate=mutate), self.assertRaises(ValueError):
                preflight.validate_phase_account(value, m)
        missing_active = account()
        missing_active.pop("active_build")
        with self.assertRaises(ValueError):
            preflight.validate_phase_account(missing_active, m)


if __name__ == "__main__":
    unittest.main()
