#!/usr/bin/env python3
"""Synthetic R7 array-control service checks; no compiler or live state."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("r7_array_controls", HERE / "r7-array-controls.py")
if spec is None or spec.loader is None:
    raise RuntimeError("R7 array controls module is unavailable")
controls = importlib.util.module_from_spec(spec)
spec.loader.exec_module(controls)
first_spec = importlib.util.spec_from_file_location(
    "first_callback_for_r7_controls", HERE / "first-callback.py")
if first_spec is None or first_spec.loader is None:
    raise RuntimeError("first callback module is unavailable for inert helper binding")
first_callback = importlib.util.module_from_spec(first_spec)
first_spec.loader.exec_module(first_callback)
HELPER = first_callback.GUARD_EMPTY_TAIL_HELPER


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _callback(case, args, env, *, behavior="normal"):
    names = {
        "raise": "missing_physical_quarter", "null": "wrong_referent",
        "partial": "wrong_value", "missing-receipt": "wrong_referent",
        "missing-artifact": "wrong_value", "wrong-error-location": "missing_physical_quarter",
        "observed-wrong-value-prelude-error": "wrong_value",
    }
    name = case.name
    if behavior == "raise" and name == names[behavior]:
        raise RuntimeError("synthetic hosted execution failure")
    if behavior == "null" and name == names[behavior]:
        return None
    meta = json.loads((case.parent / "manifest.json").read_text())["cases"][name]
    before = {rel: _sha((case / rel).read_bytes())
              for rel in ("original/lib.rs", "verified/lib.rs")}
    stages = dict(meta["expected_stages"])
    if behavior == "partial" and name == names[behavior]:
        stages.pop("decode")
    for stage in controls.STAGES:
        if behavior == "missing-receipt" and name == names[behavior] and stage == "refinement":
            continue
        code = meta["expected_stages"][stage]
        receipt = {"stage": stage, "exit_code": code, "source_unchanged": True,
                   "source_before": before, "source_after": before}
        (case / f"{stage}-stage.json").write_text(json.dumps(receipt))

    target = meta["target"]["line"]
    log = ""
    if name == "positive":
        close_line = target + 1
        log += f"verified/lib.rs({target},4): Executing statement r7_guard_empty_tail\n"
        log += f"verified/lib.rs({close_line},4): Executing statement close array singleton\n"
        log += "Executing return statement\nLeak check.\n0 errors found\n"
    else:
        log += f"verified/lib.rs({target},4): Executing statement R7 target\n"
        if behavior == "observed-wrong-value-prelude-error" and name == names[behavior]:
            log += ("/workspace/bin/rust/prelude_core.rsspec(260,30-32): error: "
                    "Cannot prove condition. (Cannot prove pointer_within_limits(p) <==> true.)\n")
        else:
            error_line = meta["expected_error_line"]
            if behavior == "wrong-error-location" and name == names[behavior]:
                error_line = target
            if name == "wrong_value":
                log += f"verified/lib.rs({error_line},4): error: synthetic target-local diagnostic\n"
            else:
                log += f"verified/lib.rs({error_line},4): error: {meta['error_contains']}\n"
    if behavior == "missing-artifact" and name == names[behavior]:
        (case / "verifast.log").unlink(missing_ok=True)
    else:
        (case / "verifast.log").write_text(log)
    return {"stages": stages, "source_unchanged_at_every_stage": True}


class R7ArrayControlsTests(unittest.TestCase):
    def test_prepare_binds_exact_helper_sources_targets_and_false_credit(self):
        with tempfile.TemporaryDirectory() as temporary:
            evidence = Path(temporary) / "controls"
            self.assertEqual(HELPER, controls.EXPECTED_HELPER)
            rows = controls.prepare(evidence, helper=HELPER)
            self.assertEqual(set(rows), set(controls.CASES))
            manifest = json.loads((evidence / "manifest.json").read_text())
            self.assertFalse(manifest["accepted"])
            self.assertFalse(manifest["proof_credit"])
            self.assertEqual(manifest["helper_sha256"], _sha(HELPER))
            for name in controls.CASES:
                original = (evidence / name / "original/lib.rs").read_bytes()
                verified = (evidence / name / "verified/lib.rs").read_bytes()
                self.assertNotIn(HELPER, original)
                self.assertEqual(verified.count(HELPER), 1)
                self.assertIn(HELPER, verified)
                self.assertEqual(rows[name]["helper_sha256"], _sha(HELPER))
                self.assertEqual(original.splitlines()[-1], b"pub fn r7_runtime_empty() {}")
                self.assertEqual(verified.splitlines()[-1], b"pub fn r7_runtime_empty() {}")
            self.assertEqual(rows["positive"]["expected_stages"], {
                "exporter": 0, "decode": 0, "refinement": 0, "verifast": 0})
            self.assertEqual(rows["wrong_value"]["expected_error_line"],
                             rows["wrong_value"]["target"]["line"])

    def test_positive_and_observed_helper_negatives_classify_wrong_value_stays_open(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = controls.run(Path(temporary) / "controls", None, {},
                                  _callback, helper=HELPER)
            self.assertFalse(result["all_matched"])
            self.assertEqual(result["classification"], "INCONCLUSIVE")
            self.assertFalse(result["accepted"])
            self.assertFalse(result["proof_credit"])
            self.assertEqual(result["cases"]["positive"], "PASS_CONTROL")
            for name in ("missing_physical_quarter", "wrong_referent"):
                row = result["case_details"][name]
                self.assertEqual(row["classification"], "EXPECTED_REJECTION")
                self.assertTrue(row["error_at_expected_line"])
                self.assertTrue(row["error_match"])
                self.assertTrue(row["target_executed"])
                self.assertTrue(row["last_execution_is_target"])
            wrong_value = result["case_details"]["wrong_value"]
            self.assertEqual(wrong_value["classification"], "INCONCLUSIVE")
            self.assertTrue(wrong_value["error_at_expected_line"])
            self.assertFalse(wrong_value["error_match"])
            self.assertTrue(wrong_value["target_executed"])
            self.assertTrue(wrong_value["last_execution_is_target"])

    def test_execution_and_evidence_failures_are_inconclusive(self):
        scenarios = ("raise", "null", "partial", "missing-receipt", "missing-artifact",
                     "wrong-error-location", "observed-wrong-value-prelude-error")
        affected = {
            "raise": "missing_physical_quarter", "null": "wrong_referent",
            "partial": "wrong_value", "missing-receipt": "wrong_referent",
            "missing-artifact": "wrong_value", "wrong-error-location": "missing_physical_quarter",
            "observed-wrong-value-prelude-error": "wrong_value",
        }
        for scenario in scenarios:
            with self.subTest(scenario=scenario), tempfile.TemporaryDirectory() as temporary:
                result = controls.run(Path(temporary) / "controls", None,
                                      {"scenario": scenario},
                                      lambda case, args, env: _callback(
                                          case, args, env, behavior=scenario),
                                      helper=HELPER)
                self.assertEqual(result["case_details"][affected[scenario]]["classification"],
                                 "INCONCLUSIVE")
                self.assertFalse(result["accepted"])
                self.assertFalse(result["proof_credit"])

    def test_wrong_helper_and_absent_executor_fail_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = controls.run(Path(temporary) / "bad", None, {}, _callback,
                                  helper=b"different helper")
            self.assertEqual(result["classification"], "INCONCLUSIVE")
            self.assertFalse(result["accepted"])
            result = controls.run(Path(temporary) / "no-executor", None, {}, None,
                                  helper=HELPER)
            self.assertEqual(result["classification"], "INCONCLUSIVE")
            self.assertTrue(all(row["classification"] == "INCONCLUSIVE"
                                for row in result["cases"].values()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
