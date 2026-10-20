"""Regression for immutable, source-bound caller Body.span focus extraction."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import unittest
from collections.abc import Mapping


HERE = Path(__file__).resolve().parent


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load isolated module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


CALL_BINDING = load("a1_immutable_span_call_binding_test",
                    HERE / "a1-call-binding.py")
FOCUS = load("a1_immutable_span_focus_test", HERE / "a1-focus-backend.py")
ERROR = "A1-FOCUS: source-bound caller MIR Body.span required before focus"


def binding(span):
    return {"binding": {"mir_body_span": span}}


class ImmutableCallerSpanTests(unittest.TestCase):
    def test_actual_frozen_observer_shape_is_accepted(self):
        observed = CALL_BINDING._freeze(binding({
            "lo": {"source_path": "verified/lib.rs", "line": 27, "column": 3},
            "hi": {"source_path": "verified/lib.rs", "line": 31, "column": 1},
        }))
        span = observed["binding"]["mir_body_span"]
        self.assertIsInstance(observed, Mapping)
        self.assertNotIsInstance(span, dict)
        self.assertIsInstance(span, Mapping)
        raw_observation = {"case_id": "P0c", "classification": "UNCLASSIFIED"}
        line = FOCUS._record_caller_focus_span(raw_observation, observed)
        self.assertEqual(line, 27)
        self.assertEqual(raw_observation["focus"], "verified/lib.rs:27")
        self.assertEqual(raw_observation["focus_source_line"], 27)
        copied = raw_observation["compiler_caller_span_observed"]
        self.assertIsInstance(copied, dict)
        self.assertEqual(copied, {
            "lo": {"source_path": "verified/lib.rs", "line": 27, "column": 3},
            "hi": {"source_path": "verified/lib.rs", "line": 31, "column": 1},
        })
        encoded = json.dumps(raw_observation, sort_keys=True)
        self.assertEqual(json.loads(encoded), raw_observation)
        self.assertEqual(span["lo"]["line"], 27, "copy must not mutate observer data")

    def test_mutable_mapping_shape_is_also_accepted(self):
        self.assertEqual(FOCUS._source_bound_caller_focus_span(binding({
            "lo": {"source_path": "verified/lib.rs", "line": 8},
            "hi": {"source_path": "verified/lib.rs", "line": 8},
        })), (8, {"lo": {"source_path": "verified/lib.rs", "line": 8},
                 "hi": {"source_path": "verified/lib.rs", "line": 8}}))

    def test_missing_null_and_wrong_mapping_layers_fail_closed(self):
        bad = (
            {},
            {"binding": None},
            {"binding": []},
            {"binding": {}},
            binding(None),
            binding([]),
            binding({"lo": None, "hi": {"source_path": "verified/lib.rs", "line": 2}}),
            binding({"lo": {"source_path": "verified/lib.rs", "line": 1}, "hi": "bad"}),
        )
        for value in bad:
            with self.subTest(value=value), self.assertRaisesRegex(RuntimeError, ERROR):
                FOCUS._source_bound_caller_focus_span(value)

    def test_wrong_path_and_invalid_bounds_fail_closed(self):
        pairs = (
            ({"source_path": "other.rs", "line": 2},
             {"source_path": "verified/lib.rs", "line": 3}),
            ({"source_path": "verified/lib.rs", "line": 2},
             {"source_path": "other.rs", "line": 3}),
            ({"source_path": "verified/lib.rs", "line": 0},
             {"source_path": "verified/lib.rs", "line": 3}),
            ({"source_path": "verified/lib.rs", "line": 4},
             {"source_path": "verified/lib.rs", "line": 3}),
            ({"source_path": "verified/lib.rs", "line": True},
             {"source_path": "verified/lib.rs", "line": 3}),
        )
        for lo, hi in pairs:
            with self.subTest(lo=lo, hi=hi), self.assertRaisesRegex(RuntimeError, ERROR):
                FOCUS._source_bound_caller_focus_span(binding({"lo": lo, "hi": hi}))


if __name__ == "__main__":
    unittest.main()
