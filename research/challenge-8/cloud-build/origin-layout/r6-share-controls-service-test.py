#!/usr/bin/env python3
"""Synthetic R6 representation-control tests; no compiler or live state."""
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
spec = importlib.util.spec_from_file_location("r6_share_controls", HERE / "r6-share-controls.py")
if spec is None or spec.loader is None:
    raise RuntimeError("R6 controls module is unavailable")
controls = importlib.util.module_from_spec(spec)
spec.loader.exec_module(controls)

REPRESENTATION = b"""/*@
pred r6_u64_share(k: lifetime_t, t: thread_id_t, p: *u64) =
    frac_borrow(k, u64_full_borrow_content(t, p));
type_pred_def <u64>.share = r6_u64_share;

lem r6_close_u64_share(k: lifetime_t, t: thread_id_t, p: *u64)
    req [_]frac_borrow(k, u64_full_borrow_content(t, p));
    ens [_](<u64>.share)(k, t, p);
{
    assert [?r6_share_fraction]frac_borrow(k, u64_full_borrow_content(t, p));
    close [r6_share_fraction]r6_u64_share(k, t, p);
}

lem r6_u64_share_mono(k: lifetime_t, k1: lifetime_t, t: thread_id_t, p: *u64)
    req [_](<u64>.share)(k, t, p) &*& lifetime_inclusion(k1, k) == true;
    ens [_](<u64>.share)(k1, t, p);
{
    open [_]r6_u64_share(k, t, p);
    frac_borrow_mono(k, k1, u64_full_borrow_content(t, p));
    assert [?r6_mono_fraction]frac_borrow(k1, u64_full_borrow_content(t, p));
    close [r6_mono_fraction]r6_u64_share(k1, t, p);
}
@*/
"""


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _callback(case, args, env, *, behavior="normal"):
    name = case.name
    if behavior == "raise" and name == "missing_resource":
        raise RuntimeError("synthetic setup failure")
    if behavior == "null" and name == "wrong_referent":
        return None
    meta = json.loads((case.parent / "manifest.json").read_text())["cases"][name]
    before = {rel: _sha((case / rel).read_bytes())
              for rel in ("original/lib.rs", "verified/lib.rs")}
    stages = dict(meta["expected_stages"])
    if behavior == "partial" and name == "wrong_lifetime":
        stages.pop("refinement")
    for stage in controls.STAGES:
        if behavior == "missing-stage" and name == "wrong_thread" and stage == "refinement":
            continue
        code = meta["expected_stages"][stage]
        if behavior == "wrong-stage-field" and name == "positive" and stage == "refinement":
            code = 1
        receipt = {"stage": stage, "exit_code": code, "source_unchanged": True,
                   "source_before": before, "source_after": before}
        if behavior == "wrong-stage-field" and name == "positive" and stage == "refinement":
            receipt["status"] = "FAILURE"
        (case / f"{stage}-stage.json").write_text(json.dumps(receipt))
    line = meta["target"]["line"]
    if behavior == "wrong-target" and name == "missing_resource":
        line += 1
    log = "verified/lib.rs(19,4): Executing return statement\n"
    log += f"verified/lib.rs({line},4): note: Executing statement r6_close_u64_share\n"
    if meta["expected_class"] == "positive":
        log += "Executing return statement\nLeak check.\n0 errors found\n"
    elif behavior != "no-log":
        error_line = meta["bridge_req_line"]
        if behavior == "wrong-error-location" and name == "missing_resource":
            error_line = line
        log += f"verified/lib.rs({error_line},4): error: No matching heap chunks: {meta['error_contains']}\n"
    (case / "verifast.log").write_text(log)
    return {"stages": stages, "source_unchanged_at_every_stage": True}


class R6ShareControlsTests(unittest.TestCase):
    def test_prepare_embeds_the_exact_representation_and_only_empty_runtime(self):
        with tempfile.TemporaryDirectory() as temporary:
            evidence = Path(temporary) / "controls"
            rows = controls.prepare(evidence, representation=REPRESENTATION)
            self.assertEqual(set(rows), set(controls.CASES))
            for name in controls.CASES:
                original = (evidence / name / "original/lib.rs").read_bytes()
                verified = (evidence / name / "verified/lib.rs").read_bytes()
                self.assertNotIn(REPRESENTATION, original)
                bridge = controls._bridge_representation(REPRESENTATION)
                self.assertIn(bridge, verified)
                self.assertNotIn(b"lem r6_u64_share_mono(", verified)
                self.assertEqual(original.splitlines()[-1], b"pub fn r6_runtime_empty() {}")
                self.assertEqual(verified.splitlines()[-1], b"pub fn r6_runtime_empty() {}")
                self.assertEqual(rows[name]["representation_sha256"], _sha(REPRESENTATION))
            self.assertEqual(rows["positive"]["expected_stages"], {
                "exporter": 0, "decode": 0, "refinement": 0, "verifast": 0})
            self.assertEqual(rows["missing_resource"]["expected_stages"], {
                "exporter": 0, "decode": 0, "refinement": 0, "verifast": 1})

    def test_positive_and_all_intended_negative_controls_classify(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = controls.run(Path(temporary) / "controls", None, {},
                                  _callback, representation=REPRESENTATION)
            self.assertTrue(result["all_matched"])
            self.assertFalse(result["accepted"])
            self.assertFalse(result["proof_credit"])
            self.assertEqual(result["cases"]["positive"], "PASS_CONTROL")
            for name in ("missing_resource", "wrong_referent", "wrong_lifetime", "wrong_thread"):
                row = result["case_details"][name]
                self.assertEqual(row["classification"], "EXPECTED_REJECTION")
                self.assertTrue(row["bridge_req_error"])
                self.assertTrue(row["last_execution_is_target"])
                self.assertTrue(row["return_before_error"])

    def test_callback_errors_null_partial_receipts_missing_artifacts_and_wrong_target_are_inconclusive(self):
        scenarios = ("raise", "null", "partial", "missing-stage", "no-log", "wrong-target",
                     "wrong-error-location", "wrong-stage-field")
        for scenario in scenarios:
            with self.subTest(scenario=scenario), tempfile.TemporaryDirectory() as temporary:
                result = controls.run(Path(temporary) / "controls", None,
                                      {"scenario": scenario},
                                      lambda case, args, env: _callback(
                                          case, args, env, behavior=scenario),
                                      representation=REPRESENTATION)
                affected = {
                    "raise": "missing_resource", "null": "wrong_referent",
                    "partial": "wrong_lifetime", "missing-stage": "wrong_thread",
                    "no-log": "missing_resource", "wrong-target": "missing_resource",
                    "wrong-error-location": "missing_resource",
                    "wrong-stage-field": "positive",
                }[scenario]
                self.assertEqual(result["case_details"][affected]["classification"], "INCONCLUSIVE")
                self.assertFalse(result["accepted"])
                self.assertFalse(result["proof_credit"])

    def test_bad_representation_and_absent_executor_fail_closed_without_throwing(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = controls.run(Path(temporary) / "bad", None, {}, _callback,
                                  representation=b"no bridge")
            self.assertEqual(result["classification"], "INCONCLUSIVE")
            self.assertFalse(result["accepted"])
            result = controls.run(Path(temporary) / "no-executor", None, {}, None,
                                  representation=REPRESENTATION)
            self.assertEqual(result["classification"], "INCONCLUSIVE")
            self.assertTrue(all(row["classification"] == "INCONCLUSIVE"
                                for row in result["cases"].values()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
