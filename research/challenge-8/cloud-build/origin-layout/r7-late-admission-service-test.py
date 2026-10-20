#!/usr/bin/env python3
"""Synthetic service tests for R7 late callback admission controls."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from types import SimpleNamespace


sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "r7_late_admission_controls", HERE / "r7-late-admission-controls.py")
if spec is None or spec.loader is None:
    raise RuntimeError("R7 late callback admission module is unavailable")
controls = importlib.util.module_from_spec(spec)
spec.loader.exec_module(controls)

SOURCE = b"""#![no_std]
//@ let r5_late_k = begin_lifetime();
//@ let r7_late_unwind = false;
//@ late_callback_scope_begin::<'late>();
//@ r6_close_u64_share(r5_late_k, t, r4_cmp_tmp_ref);
if !is_less/*@::<F, (&'late u64, &'late u64), 'late>@*/(&tmp, &*sift) {
}
/*@ { late_callback_close::<'late>(); merge_fractions lifetime_token(r5_late_k); assert [1/2]lifetime_token(r5_late_k); } @*/
//@ late_callback_scope_end::<'late>();
/*@ { late_callback_recover::<'late>(); assert lifetime_token(r5_late_k); end_lifetime(r5_late_k); borrow_end(r5_late_k, scaledp(r5_tmp_share, u64_full_borrow_content(t, r4_cmp_tmp_ref))); open scaledp(r5_tmp_share, u64_full_borrow_content(t, r4_cmp_tmp_ref))(); open [r5_tmp_share]u64_full_borrow_content(t, r4_cmp_tmp_ref)(); end_ref_readonly::<u64>(r4_cmp_tmp_ref); borrow_end(r5_late_k, scaledp(r5_sift_share, u64_full_borrow_content(t, r4_cmp_sift_ref))); open scaledp(r5_sift_share, u64_full_borrow_content(t, r4_cmp_sift_ref))(); open [r5_sift_share]u64_full_borrow_content(t, r4_cmp_sift_ref)(); end_ref_readonly::<u64>(r4_cmp_sift_ref); merge_fractions *sift |-> _; assert *sift |-> ?r7_sift_current; close array::<u64>(sift, 1, cons(r7_sift_current, nil)); } @*/
"""


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _source_case(root):
    case = root / "fullbody"
    (case / "original").mkdir(parents=True)
    (case / "verified").mkdir()
    original = b"#![no_std]\npub fn original() {}\n"
    verified = SOURCE
    (case / "original/lib.rs").write_bytes(original)
    (case / "verified/lib.rs").write_bytes(verified)
    source_record = {"profile": controls.R7_PROFILE, "prefix": False,
                     "late_callback_scope_recovery_requested": True,
                     "mutation": None, "original_sha256": _sha(original),
                     "verified_sha256": _sha(verified)}
    return case, source_record


def _receipt(case, stage, code, original_sha, verified_sha):
    pair = {"original/lib.rs": original_sha, "verified/lib.rs": verified_sha}
    (case / f"{stage}-stage.json").write_text(json.dumps({
        "stage": stage, "exit_code": code, "source_unchanged": True,
        "source_before": pair, "source_after": pair}))


def _baseline(case, record, *, diagnostic=True):
    for stage, code in (("exporter", 0), ("decode", 0),
                        ("refinement", 0), ("verifast", 1)):
        _receipt(case, stage, code, record["original_sha256"], record["verified_sha256"])
    line = controls.BASELINE_DIAGNOSTIC + " registered=1 source=actual\n" if diagnostic else ""
    (case / "verifast.log").write_text(line + "verified/lib.rs(7,4): error: expected baseline proof failure\n")


def _execute(case, args, env, behavior=None):
    meta = json.loads((case / "case.json").read_text())
    original_sha = _sha((case / "original/lib.rs").read_bytes())
    verified_sha = _sha((case / "verified/lib.rs").read_bytes())
    if behavior == "raise":
        raise RuntimeError("synthetic stage failure")
    if behavior == "null":
        return None
    stages = {"exporter": 0, "decode": 0, "refinement": 0, "verifast": 1}
    for stage, code in stages.items():
        if behavior == "missing_receipt" and stage == "decode":
            continue
        _receipt(case, stage, code, original_sha, verified_sha)
    source = (case / "verified/lib.rs").read_bytes()
    if behavior == "mutated_source":
        (case / "verified/lib.rs").write_bytes(source + b"// stage changed source\n")
    line = meta["expected_error_line"]
    if behavior == "wrong_line":
        line += 1
    (case / "verifast.log").write_text(
        f"verified/lib.rs({line},4): error: {meta['expected_error']}\n")
    if behavior == "missing_log":
        (case / "verifast.log").unlink()
    if behavior == "partial_stages":
        stages.pop("refinement")
    return {"stages": stages, "source_unchanged_at_every_stage": behavior != "mutated_source"}


class R7LateAdmissionTests(unittest.TestCase):
    def test_exact_baseline_gates_and_two_targeted_negatives(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_case, record = _source_case(root)
            _baseline(source_case, record)
            calls = []

            def execute(case, args, env):
                calls.append(case.name)
                return _execute(case, args, env)

            output = controls.run(root / "controls", SimpleNamespace(profile=controls.R7_PROFILE),
                                  {}, execute, source_case, record)
            self.assertTrue(output["baseline"]["admitted"])
            self.assertTrue(output["all_matched"])
            self.assertFalse(output["accepted"])
            self.assertFalse(output["proof_credit"])
            self.assertEqual(set(calls), set(controls.CASES))
            self.assertEqual(set(output["cases"]), set(controls.CASES))
            missing = root / "controls/missing_outer_unwind_flag"
            wrong_ref = root / "controls/wrong_recovery_ref"
            self.assertNotIn(b"let r7_late_unwind = false", (missing / "verified/lib.rs").read_bytes())
            self.assertIn(b"end_ref_readonly::<u64>(r4_cmp_sift_ref);",
                          (wrong_ref / "verified/lib.rs").read_bytes())
            self.assertEqual((missing / "original/lib.rs").read_bytes(),
                             (source_case / "original/lib.rs").read_bytes())
            self.assertEqual((wrong_ref / "original/lib.rs").read_bytes(),
                             (source_case / "original/lib.rs").read_bytes())

    def test_missing_baseline_frontend_admission_does_not_run_mutants(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_case, record = _source_case(root)
            _baseline(source_case, record, diagnostic=False)
            calls = []
            output = controls.run(root / "controls", SimpleNamespace(profile=controls.R7_PROFILE),
                                  {}, lambda *args: calls.append(args), source_case, record)
            self.assertFalse(output["baseline"]["admitted"])
            self.assertEqual(calls, [])
            self.assertTrue(all(row["classification"] == "NOT_RUN"
                                for row in output["cases"].values()))

    def test_bad_hash_profile_and_baseline_receipts_fail_closed(self):
        for defect in ("hash", "profile", "receipt"):
            with self.subTest(defect=defect), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                source_case, record = _source_case(root)
                _baseline(source_case, record)
                if defect == "hash":
                    record["verified_sha256"] = "0" * 64
                elif defect == "profile":
                    record["profile"] = "other"
                else:
                    (source_case / "decode-stage.json").unlink()
                calls = []
                output = controls.run(root / "controls", SimpleNamespace(profile=controls.R7_PROFILE),
                                      {}, lambda *args: calls.append(args), source_case, record)
                self.assertFalse(output["all_matched"])
                self.assertEqual(calls, [])
                self.assertFalse(output["accepted"])
                self.assertFalse(output["proof_credit"])

    def test_mutant_execution_failures_and_wrong_diagnostics_are_inconclusive(self):
        scenarios = ("raise", "null", "missing_receipt", "wrong_line", "missing_log",
                     "partial_stages", "mutated_source")
        for behavior in scenarios:
            with self.subTest(behavior=behavior), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                source_case, record = _source_case(root)
                _baseline(source_case, record)
                affected = "missing_outer_unwind_flag"
                output = controls.run(root / "controls", SimpleNamespace(profile=controls.R7_PROFILE),
                                      {}, lambda case, args, env: _execute(case, args, env,
                                                                           behavior if case.name == affected else None),
                                      source_case, record)
                self.assertEqual(output["cases"][affected]["classification"], "INCONCLUSIVE")
                self.assertFalse(output["accepted"])
                self.assertFalse(output["proof_credit"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
