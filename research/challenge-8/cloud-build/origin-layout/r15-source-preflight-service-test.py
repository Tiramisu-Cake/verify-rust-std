#!/usr/bin/env python3
"""Synthetic source-registration and transport-boundary tests; no Cloud calls."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0]))
spec = importlib.util.spec_from_file_location("r15_preflight_control", HERE.parents[0] / "control.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class R15SourcePreflightTests(unittest.TestCase):
    def test_transport_limit_accepts_cap_and_refuses_overflow_and_bad_types(self):
        limit = 191 * 3990
        self.assertLessEqual(m.r15_validate_transport_size((limit // 4) * 3), limit)
        with self.assertRaises(SystemExit):
            m.r15_validate_transport_size((limit // 4) * 3 + 1)
        for invalid in (-1, True, "1200"):
            with self.subTest(invalid=invalid), self.assertRaises(SystemExit):
                m.r15_validate_transport_size(invalid)

    def test_source_transport_caps_are_unchanged(self):
        control = (HERE.parents[0] / "control.py").read_text()
        self.assertIn("source_parts=[encoded[i:i+3990]", control)
        self.assertIn("if len(source_parts)>191", control)

    def test_registration_uses_exact_recipe_additions_and_requires_existing_inputs(self):
        recipe = {"schema": "smallsort-cloud-recipe-v1", "lane": "merge",
                  "entrypoint": "run-merge.sh", "infra_paths": ["run-merge.sh"],
                  "proof_paths": sorted(["a.py", *m.R15_RECIPE_REMOVALS])}
        selected_paths = sorted([path for path in recipe["proof_paths"]
                                 if path not in m.R15_RECIPE_REMOVALS] + [m.R15_LEDGER_PATH])
        selected = dict(recipe, proof_paths=selected_paths)
        m.r15_validate_recipe_delta(recipe, selected)
        for bad in (
            dict(selected, proof_paths=sorted(selected["proof_paths"] + ["extra.py"])),
            dict(selected, infra_paths=["changed.sh"]),
            dict(selected, proof_paths=selected["proof_paths"] + [m.R14_PREFLIGHT_PATH]),
        ):
            with self.subTest(recipe=bad), self.assertRaises(SystemExit):
                m.r15_validate_recipe_delta(recipe, bad)


if __name__ == "__main__":
    unittest.main()
