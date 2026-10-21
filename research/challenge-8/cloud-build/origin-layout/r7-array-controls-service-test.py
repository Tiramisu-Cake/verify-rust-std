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
        "error": "missing_physical_quarter", "timeout": "wrong_referent",
        "partial": "wrong_value", "missing-receipt": "wrong_referent",
        "missing-artifact": "wrong_value", "wrong-error-location": "missing_physical_quarter",
        "observed-wrong-value-geometry-error": "wrong_value",
        "wrong-value-spec-location": "wrong_value",
        "wrong-value-source-position": "wrong_value",
        "wrong-value-error-text": "wrong_value",
        "wrong-length-spec-location": "wrong_length_fold",
        "wrong-length-error-text": "wrong_length_fold",
        "explicit-not-run": "wrong_length_fold", "wrong-type-stage": "fractional_singleton_roundtrip",
        "source-mismatch": "adjacent_nonempty_rejoin", "stage-mismatch": "nonempty_zero_witness",
    }
    name = case.name
    if behavior in {"raise", "error", "timeout"} and name == names[behavior]:
        error_type = TimeoutError if behavior == "timeout" else RuntimeError
        error = error_type("synthetic hosted execution failure")
        error.exit_code = 124 if behavior == "timeout" else 23
        error.last_snapshot = {"stage": "decode", "exit_code": 0,
                               "source_unchanged": True, "case": name}
        raise error
    if behavior == "null" and name == names[behavior]:
        return None
    meta = json.loads((case.parent / "manifest.json").read_text())["cases"][name]
    before = {rel: _sha((case / rel).read_bytes())
              for rel in ("original/lib.rs", "verified/lib.rs")}
    stages = dict(meta["expected_stages"])
    if behavior == "partial" and name == names[behavior]:
        stages.pop("decode")
    if behavior == "explicit-not-run" and name == names[behavior]:
        stages["verifast"] = None
    for stage in controls.STAGES:
        if behavior == "missing-receipt" and name == names[behavior] and stage == "refinement":
            continue
        code = meta["expected_stages"][stage]
        receipt_stage = stage
        receipt_code = code
        status = "SUCCESS"
        if behavior == "explicit-not-run" and name == names[behavior] and stage == "verifast":
            status = "NOT_RUN"
            receipt_code = None
        if behavior == "wrong-type-stage" and name == names[behavior] and stage == "decode":
            receipt_code = str(code)
        if behavior == "stage-mismatch" and name == names[behavior] and stage == "verifast":
            receipt_stage = "decode"
        receipt = {"stage": receipt_stage, "exit_code": receipt_code, "status": status,
                   "source_unchanged": True,
                   "source_before": before, "source_after": before}
        if behavior == "source-mismatch" and name == names[behavior] and stage == "refinement":
            receipt["source_after"] = dict(before)
            receipt["source_after"]["verified/lib.rs"] = "0" * 64
        (case / f"{stage}-stage.json").write_text(json.dumps(receipt))

    target = meta["target"]["line"]
    log = ""
    if behavior == "explicit-not-run" and name == names[behavior]:
        log += "verifier target NOT_RUN after explicit stage skip\n"
    elif meta["expected_class"] == "positive":
        close_line = target + 1
        log += f"verified/lib.rs({target},4): Executing statement {meta['target']['marker']}\n"
        log += f"verified/lib.rs({close_line},4): Executing statement close array singleton\n"
        log += "Executing return statement\nLeak check.\n0 errors found\n"
    else:
        executed_target = target + 1 if behavior == "wrong-value-source-position" and name == "wrong_value" else target
        log += f"verified/lib.rs({executed_target},4): Executing statement R7 target\n"
        if behavior == "observed-wrong-value-geometry-error" and name == names[behavior]:
            log += ("/workspace/bin/rust/prelude_core.rsspec(260,30-32): error: "
                    "Cannot prove condition. (Cannot prove pointer_within_limits(p) <==> true.)\n")
        elif name == "wrong_value":
            spec_line = 265 if behavior == "wrong-value-spec-location" else 264
            if behavior == "wrong-value-error-text":
                diagnostic = "Cannot prove condition. (different condition.)"
            else:
                diagnostic = "Cannot prove condition. (Cannot prove cons(w, nil) = cons(v, nil).)"
            log += f"/workspace/bin/rust/prelude_core.rsspec({spec_line},72-74): error: {diagnostic}\n"
        elif name == "wrong_length_fold":
            loc = meta["expected_error_location"]
            spec_line = loc["line"] + 1 if behavior == "wrong-length-spec-location" else loc["line"]
            diagnostic = ("No matching heap chunks: different recursive tail"
                          if behavior == "wrong-length-error-text" else meta["error_contains"])
            log += (f"/workspace/bin/rust/{loc['file']}({spec_line},{loc['columns']}): "
                    f"error: {diagnostic}\n")
        elif meta.get("expected_error_location") is not None:
            loc = meta["expected_error_location"]
            log += f"/workspace/bin/rust/{loc['file']}({loc['line']},{loc['columns']}): error: {meta['error_contains']}\n"
        else:
            error_line = meta["expected_error_line"]
            if behavior == "wrong-error-location" and name == names[behavior]:
                error_line = target
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
            self.assertEqual(sum(meta["class"] == "positive" for meta in controls.CASES.values()), 6)
            self.assertEqual(sum(meta["class"] == "negative" for meta in controls.CASES.values()), 6)
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
            lifecycle = controls.CASES["array3_borrow_lifecycle"]["runtime"]
            original = (evidence / "array3_borrow_lifecycle/original/lib.rs").read_bytes()
            verified = (evidence / "array3_borrow_lifecycle/verified/lib.rs").read_bytes()
            target = b"let slice = core::ptr::slice_from_raw_parts_mut::<u64>(p as *mut u64, 3); // TARGET: construct exact mutable slice metadata"
            self.assertEqual(original.count(target), 1)
            self.assertEqual(verified.count(target), 1)
            self.assertIn(b"//@ let k = begin_lifetime();", lifecycle)
            self.assertIn(b"//@ borrow(k, r16_array3_content(default_tid(), p));", lifecycle)
            self.assertIn(b"//@ end_lifetime(k);", lifecycle)
            self.assertIn(b"//@ borrow_end(k, r16_array3_content(default_tid(), p));", lifecycle)
            self.assertIn(b"full_borrow(?k, r16_array3_content(default_tid(), p))", lifecycle)
            self.assertIn(b"ens *p |-> ?restored_current", lifecycle)
            self.assertIn(b"default_tid())); @*/\n/*@ ens *p |-> ?restored_current", lifecycle)
            self.assertNotIn(b"ens *p |-> current", lifecycle)
            self.assertNotIn(b"create_ref_mut", lifecycle)
            self.assertNotIn(b"assume", lifecycle)
            self.assertEqual(rows["positive"]["expected_stages"], {
                "exporter": 0, "decode": 0, "refinement": 0, "verifast": 0})
            self.assertEqual(rows["wrong_value"]["expected_error_location"], {
                "file": "prelude_core.rsspec", "line": 264, "columns": "72-74"})
            self.assertEqual(rows["nonempty_zero_witness"]["expected_error_location"], {
                "file": "prelude_core.rsspec", "line": 262, "columns": "16-18"})
            self.assertEqual(rows["wrong_length_fold"]["expected_error_location"], {
                "file": "prelude_core.rsspec", "line": 264, "columns": "27-32"})
            post_drop = controls.CASES["post_drop_array3_reconstruction"]["lemma"]
            self.assertIn(b"array::<u64>(p + 2,1,?last)", post_drop)
            self.assertIn(b"assert [1/4](*(p + 2) |-> ?r15_tail_current);", post_drop)
            self.assertIn(b"assert [1/4](*(p + 1) |-> ?r15_middle_current);", post_drop)
            self.assertIn(b"assert [1/4](*p |-> ?r15_first_current);", post_drop)
            self.assertIn(b"array::<u64>(p,3,append(first,append(current,last)))", post_drop)
            self.assertNotIn(b"cons(first,", post_drop)
            self.assertNotIn(b"cons(current,", post_drop)
            self.assertIn(b"array::<u64>(p + 3,0,nil)", post_drop)
            self.assertNotIn(b"assume", post_drop)
            adjacent = controls.CASES["adjacent_nonempty_rejoin"]["lemma"]
            self.assertIn(b"array_split::<u64>(p,1);", adjacent)
            self.assertIn(b"open [1/4]array::<u64>(p + 1,0,_);", adjacent)
            self.assertIn(b"close [1/4]array::<u64>(p,1,take(1,vs));", adjacent)
            self.assertNotIn(b"assert *p |->", adjacent)
            wrong_length = controls.CASES["wrong_length_fold"]["lemma"]
            self.assertLess(wrong_length.index(b"points_to_limits::<u64>(p);"),
                            wrong_length.index(b"TARGET: reject singleton folded at length two"))

    def test_all_positive_and_expected_negative_controls_classify_by_metadata(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = controls.run(Path(temporary) / "controls", None, {},
                                  _callback, helper=HELPER)
            self.assertTrue(result["all_matched"])
            self.assertEqual(result["classification"], "DIAGNOSTIC_CONTROLS_CLASSIFIED")
            self.assertFalse(result["accepted"])
            self.assertFalse(result["proof_credit"])
            for name, meta in controls.CASES.items():
                row = result["case_details"][name]
                expected = "PASS_CONTROL" if meta["class"] == "positive" else "EXPECTED_REJECTION"
                self.assertEqual(row["classification"], expected)
                if meta["class"] == "negative":
                    self.assertTrue(row["error_at_expected_line"])
                    self.assertTrue(row["error_match"])
                    self.assertTrue(row["target_executed"])
                    self.assertTrue(row["last_execution_is_target"])

    def test_execution_and_evidence_failures_are_inconclusive(self):
        scenarios = ("raise", "error", "timeout", "null", "partial", "explicit-not-run",
                     "missing-receipt", "missing-artifact", "wrong-type-stage",
                     "source-mismatch", "stage-mismatch",
                     "wrong-error-location", "observed-wrong-value-geometry-error",
                     "wrong-value-spec-location", "wrong-value-source-position",
                     "wrong-value-error-text", "wrong-length-spec-location",
                     "wrong-length-error-text")
        affected = {
            "raise": "missing_physical_quarter", "null": "wrong_referent",
            "error": "missing_physical_quarter", "timeout": "wrong_referent",
            "partial": "wrong_value", "missing-receipt": "wrong_referent",
            "explicit-not-run": "wrong_length_fold",
            "missing-artifact": "wrong_value", "wrong-error-location": "missing_physical_quarter",
            "wrong-type-stage": "fractional_singleton_roundtrip",
            "source-mismatch": "adjacent_nonempty_rejoin", "stage-mismatch": "nonempty_zero_witness",
            "observed-wrong-value-geometry-error": "wrong_value",
            "wrong-value-spec-location": "wrong_value",
            "wrong-value-source-position": "wrong_value",
            "wrong-value-error-text": "wrong_value",
            "wrong-length-spec-location": "wrong_length_fold",
            "wrong-length-error-text": "wrong_length_fold",
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
                self.assertFalse(result["all_matched"])
                if scenario in {"error", "timeout"}:
                    failure = result["case_details"][affected[scenario]]["execution_failure"]
                    self.assertEqual(failure["exit_code"], 124 if scenario == "timeout" else 23)
                    self.assertEqual(failure["last_snapshot"]["stage"], "decode")
                    self.assertIn("synthetic hosted execution failure", failure["repr"])

    def test_source_stage_and_target_mismatches_cannot_match(self):
        for scenario, case_name in (("source-mismatch", "adjacent_nonempty_rejoin"),
                                    ("stage-mismatch", "nonempty_zero_witness"),
                                    ("wrong-value-source-position", "wrong_value")):
            with self.subTest(scenario=scenario), tempfile.TemporaryDirectory() as temporary:
                result = controls.run(Path(temporary) / "controls", None,
                                      {"scenario": scenario},
                                      lambda case, args, env: _callback(
                                          case, args, env, behavior=scenario),
                                      helper=HELPER)
                row = result["case_details"][case_name]
                self.assertEqual(row["classification"], "INCONCLUSIVE")
                self.assertFalse(result["all_matched"])

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
