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


if __name__ == "__main__":
    unittest.main()
