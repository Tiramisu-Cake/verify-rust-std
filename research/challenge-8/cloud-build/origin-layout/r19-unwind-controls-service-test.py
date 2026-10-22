#!/usr/bin/env python3
"""Synthetic R19 unwind cleanup control tests; no compiler or Cloud service runs."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("r19_unwind_controls", HERE / "r19-unwind-controls.py")
controls = importlib.util.module_from_spec(spec)
spec.loader.exec_module(controls)
callback_spec = importlib.util.spec_from_file_location("r19_first_callback", HERE / "first-callback.py")
callback = importlib.util.module_from_spec(callback_spec)
callback_spec.loader.exec_module(callback)
SOURCE_SHA = "a" * 64


def sha(data):
    return hashlib.sha256(data).hexdigest()


def raw_pair():
    old = callback._load("r19_raw_source", HERE / "actual-insert-tail-b2.py")
    original, verified = callback._raw_local_caller_suffixes(old)
    body = b"#![no_std]\nunsafe fn insert_tail() {}\n"
    return body + original, body + verified


def synthetic_pair():
    old = callback._load("r19_synthetic_b2", HERE / "actual-insert-tail-b2.py")
    original, verified, lines = controls._synthetic_unwind_pair(callback, old)
    return original, verified, lines


class Consumer:
    def _hashes(self, case):
        return {"original/lib.rs": sha((case / "original/lib.rs").read_bytes()),
                "verified/lib.rs": sha((case / "verified/lib.rs").read_bytes()),
                "small_sort_source": SOURCE_SHA}

    def _stage_receipts(self, case, stages, baseline):
        return {"admitted": type(stages) is dict and all(
            type(stages.get(stage)) is int for stage in controls.STAGES)}


def diagnostic_log(name, line):
    return f"verified/lib.rs({line},5-6): error: {controls.DIAGNOSTICS[name]}\n"


class R19UnwindControlsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.raw = self.root / "raw_local_caller" / "cases" / callback.RAW_LOCAL_CALLER_NAME
        (self.raw / "original").mkdir(parents=True)
        (self.raw / "verified").mkdir()
        self.original, self.verified = raw_pair()
        (self.raw / "original/lib.rs").write_bytes(self.original)
        (self.raw / "verified/lib.rs").write_bytes(self.verified)
        prep = {"case": callback.RAW_LOCAL_CALLER_NAME,
                "original_sha256": sha(self.original), "verified_sha256": sha(self.verified)}
        (self.raw.parents[1] / "preparation.json").write_text(
            json.dumps(prep, sort_keys=True) + "\n")

    def tearDown(self):
        self.temp.cleanup()

    def run_controls(self, executor, name="evidence"):
        evidence = self.root / name
        evidence.mkdir()
        args = SimpleNamespace(r8_owned_array_allocation=False, first_fnmut_continue=True)
        result = controls.run(evidence, self.raw, args, executor, Consumer(), "profile",
                              source_sha256=SOURCE_SHA)
        self.assertFalse(args.r8_owned_array_allocation)
        return result

    def matching_executor(self, stages=None, log=None):
        def execute(case, args, *, actual_callback_case, body_isolation_native):
            self.assertTrue(actual_callback_case and body_isolation_native)
            self.assertTrue(args.r8_owned_array_allocation)
            record = json.loads((case / "case.json").read_text())
            if record.get("control_kind") == "synthetic_always_panicking_callee_resource_negative":
                text = (
                    "  1.000s: verified/lib.rs(2,1-2): Verifying function 'insert_tail'\n"
                    f"  1.010s: verified/lib.rs({record['panic_line']},5-24): Executing statement\n"
                    "  1.020s: verified/lib.rs(20,1-2): Verifying function 'b2_three_from_local'\n"
                    f"  1.030s: verified/lib.rs({record['call_line']},5-52): Verifying function call\n"
                    f"  1.040s: verified/lib.rs({record['marker_line']},9-71): Executing statement\n"
                    f"verified/lib.rs({record['marker_line']},9-71): error: "
                    "No matching heap chunks: array<u64>(values_addr, 4, _)\n"
                ) if log is None else log
            else:
                text = diagnostic_log(record["case"], record["expected_line"]) if log is None else log
            (case / "verifast.log").write_text(text)
            return {"status": "FAILURE", "stages": dict(
                {"exporter": 0, "decode": 0, "refinement": 0, "verifast": 1}, **(stages or {}))}
        return execute

    def test_raw_caller_carries_the_marked_cleanup_after_the_call(self):
        self.assertEqual(self.verified.count(controls.CALL + controls.R19_AFTER), 1)
        self.assertEqual(self.original.count(controls.CALL), 1)
        self.assertNotIn(b"r19_", self.original)

    def test_variants_change_only_their_target_and_bind_exact_lines(self):
        variants = controls._variants(self.original, self.verified)
        self.assertEqual(set(variants), set(controls.CASES))
        for name, (original, verified, line) in variants.items():
            lines = verified.splitlines()
            with self.subTest(name=name):
                self.assertGreater(line, 0)
                if name == "missing_marker":
                    self.assertEqual(lines[line - 1], b"}")
                    self.assertNotIn(b"r19_insert_tail_unwind_cleanup", verified)
                elif name == "cleanup_edge":
                    self.assertEqual(lines[line - 1], controls.CALL.rstrip(b"\n"))
                    self.assertIn(controls.KEEP_LOCAL, original)
                else:
                    self.assertIn(b"r19_insert_tail_unwind_cleanup();", lines[line - 1])
                if name not in ("cleanup_edge", "other_function"):
                    self.assertEqual(original, self.original)

    def test_variants_refuse_an_unmarked_or_duplicated_raw_caller(self):
        unmarked = self.verified.replace(controls.R19_AFTER, controls.R18_AFTER)
        for verified in (unmarked, self.verified + controls.CALL + controls.R19_AFTER,
                         self.verified + controls.KEEP_TYPE):
            with self.subTest(size=len(verified)), self.assertRaises(ValueError):
                controls._variants(self.original, verified)

    def test_all_exact_refusals_match(self):
        result = self.run_controls(self.matching_executor())
        self.assertTrue(result["all_matched"])
        self.assertEqual(result["classification"], "ALL_R19_UNWIND_CONTROLS_MATCHED")
        self.assertFalse(result["proof_credit"])
        self.assertEqual(result["synthetic_unwind_resource"]["classification"],
                         "EXPECTED_SYNTHETIC_RESOURCE_REFUSAL")
        self.assertFalse(result["synthetic_unwind_resource"]["proof_credit"])
        for name in controls.CASES:
            self.assertEqual(result["cases"][name]["classification"], "EXPECTED_VERIFAST_REFUSAL")

    def test_synthetic_callee_is_paired_and_failure_is_at_unwind_copy(self):
        original, verified, lines = synthetic_pair()
        self.assertTrue(callback._body_runtime_equal(original, verified))
        self.assertIn(b"ens false;", verified)
        self.assertIn(b"on_unwind_ens thread_token(t)", verified)
        self.assertEqual(verified.count(controls.CALL), 1)
        self.assertEqual(verified.count(b"r19_insert_tail_unwind_cleanup();"), 1)
        self.assertIn(b"assert array::<u64>(begin, 4, ?r16_normal_current);", verified)
        self.assertIn(b"core::panic!();", verified)
        self.assertGreater(lines["marker_line"], lines["call_line"])
        self.assertFalse(any(token in verified for token in (b"assume", b"leak")))

    def test_synthetic_negative_requires_callee_pass_and_exact_caller_resource_error(self):
        scenarios = {
            "missing callee header": lambda log: log.replace(
                "Verifying function 'insert_tail'", "Verifying function 'other'"),
            "dead code": lambda log: log + "verified/lib.rs(99,1-2): dead code\n",
            "wrong target": lambda log: log.replace(
                "array<u64>(values_addr, 4, _)", "array<u64>(values_addr, 3, _)"),
            "normal or additional failure": lambda log: log +
                "verified/lib.rs(3,1-2): error: No matching heap chunks before caller\n",
            "target not executed": lambda log: log.replace("Executing statement\n", "Statement\n", 1),
            "out of order function traces": lambda log: log.replace(
                "Verifying function 'insert_tail'", "Verifying function 'later_insert_tail'"),
        }
        for label, alter in scenarios.items():
            def executor(case, args, **kwargs):
                result = self.matching_executor()(case, args, **kwargs)
                if json.loads((case / "case.json").read_text()).get("control_kind") == \
                        "synthetic_always_panicking_callee_resource_negative":
                    (case / "verifast.log").write_text(alter((case / "verifast.log").read_text()))
                return result
            with self.subTest(label=label):
                result = self.run_controls(executor, name="synthetic-" + label.replace(" ", "-"))
                self.assertEqual(result["synthetic_unwind_resource"]["classification"], "INCONCLUSIVE")
                self.assertTrue(result["all_matched"], "the five existing R19 controls must remain independent")
        def wrong_target_line(case, args, **kwargs):
            result = self.matching_executor()(case, args, **kwargs)
            record = json.loads((case / "case.json").read_text())
            if record.get("control_kind") == "synthetic_always_panicking_callee_resource_negative":
                log_path = case / "verifast.log"
                log = log_path.read_text()
                target = f"verified/lib.rs({record['marker_line']},"
                self.assertEqual(log.count(target), 2)
                log_path.write_text(log.replace(target,
                                                f"verified/lib.rs({record['marker_line'] + 1},"))
            return result
        result = self.run_controls(wrong_target_line, name="synthetic-wrong-target-line")
        self.assertEqual(result["synthetic_unwind_resource"]["classification"], "INCONCLUSIVE")
        self.assertTrue(result["all_matched"])
        def repeated_target(case, args, **kwargs):
            result = self.matching_executor()(case, args, **kwargs)
            record = json.loads((case / "case.json").read_text())
            if record.get("control_kind") == "synthetic_always_panicking_callee_resource_negative":
                log_path = case / "verifast.log"
                log = log_path.read_text()
                target = (f"verified/lib.rs({record['marker_line']},9-71): "
                          "Executing statement\n")
                self.assertEqual(log.count(target), 1)
                log_path.write_text(log.replace(target, target + target))
            return result
        result = self.run_controls(repeated_target, name="synthetic-repeated-target-trace")
        synthetic = result["synthetic_unwind_resource"]
        self.assertEqual(synthetic["classification"], "EXPECTED_SYNTHETIC_RESOURCE_REFUSAL")
        self.assertEqual(synthetic["target_trace_count"], 2)
        self.assertTrue(result["all_matched"])

    def test_synthetic_requires_zero_source_stages_and_stable_parent_preparation(self):
        def refinement_failure(case, args, **kwargs):
            result = self.matching_executor()(case, args, **kwargs)
            if json.loads((case / "case.json").read_text()).get("control_kind") == \
                    "synthetic_always_panicking_callee_resource_negative":
                result["stages"]["refinement"] = 1
            return result
        result = self.run_controls(refinement_failure, name="synthetic-refinement-failure")
        self.assertEqual(result["synthetic_unwind_resource"]["classification"], "INCONCLUSIVE")
        self.assertTrue(result["all_matched"])

        inner = self.matching_executor()
        prep_path = self.raw.parents[1] / "preparation.json"
        def changed_parent(case, args, **kwargs):
            result = inner(case, args, **kwargs)
            if json.loads((case / "case.json").read_text()).get("control_kind") == \
                    "synthetic_always_panicking_callee_resource_negative":
                prep_path.write_text("{}\n")
            return result
        result = self.run_controls(changed_parent, name="synthetic-parent-changed")
        self.assertEqual(result["synthetic_unwind_resource"]["classification"], "INCONCLUSIVE")
        self.assertTrue(result["all_matched"])

        original_loader = controls._load_module
        def fail_synthetic_import(*args, **kwargs):
            raise ImportError("synthetic setup import sentinel")
        controls._load_module = fail_synthetic_import
        try:
            result = self.run_controls(self.matching_executor(), name="synthetic-import-failure")
        finally:
            controls._load_module = original_loader
        synthetic = result["synthetic_unwind_resource"]
        self.assertEqual(synthetic["classification"], "INCONCLUSIVE")
        self.assertEqual(synthetic["setup_exception"], {
            "type": "ImportError", "message": "synthetic setup import sentinel"})
        self.assertTrue(result["all_matched"])
        result_path = self.root / "synthetic-import-failure" / "r19-unwind-controls" / "result.json"
        self.assertTrue(result_path.is_file())
        self.assertEqual(json.loads(result_path.read_text())["cases"], result["cases"])
        classification_path = (self.root / "synthetic-import-failure" / "r19-unwind-controls" /
                               controls.SYNTHETIC_CASE / "cases" / controls.SYNTHETIC_CASE /
                               "classification.json")
        self.assertEqual(json.loads(classification_path.read_text())["setup_exception"]["type"],
                         "ImportError")

    def test_success_wrong_line_or_duplicate_diagnostic_is_inconclusive(self):
        for label, executor in (
            ("verifier exit0", self.matching_executor(stages={"verifast": 0})),
            ("exporter failure", self.matching_executor(stages={"exporter": 1})),
            ("wrong line", self.matching_executor(log="verified/lib.rs(1,1-2): error: " +
                                                  controls.DIAGNOSTICS["missing_marker"])),
            ("missing log", self.matching_executor(log="")),
        ):
            with self.subTest(label=label):
                result = self.run_controls(executor, name=label.replace(" ", "-"))
                self.assertFalse(result["all_matched"])
        def duplicate(case, args, **kwargs):
            record = json.loads((case / "case.json").read_text())
            line = diagnostic_log(record["case"], record["expected_line"])
            (case / "verifast.log").write_text(line + line.replace("5-6", "9-10"))
            return {"stages": {"exporter": 0, "decode": 0, "refinement": 0, "verifast": 1}}
        result = self.run_controls(duplicate, name="duplicate")
        self.assertEqual({r["classification"] for r in result["cases"].values()}, {"INCONCLUSIVE"})
        def repeated(case, args, **kwargs):
            record = json.loads((case / "case.json").read_text())
            line = diagnostic_log(record["case"], record["expected_line"])
            trace = "Trace: " + controls.DIAGNOSTICS[record["case"]] + "\n"
            (case / "verifast.log").write_text(line + trace + line)
            return {"stages": {"exporter": 0, "decode": 0, "refinement": 0, "verifast": 1}}
        result = self.run_controls(repeated, name="repeated")
        self.assertTrue(result["all_matched"])

    def test_timeout_setup_null_wrong_type_not_run_and_exception_fail_closed(self):
        cases = {
            "timeout": lambda *a, **k: {"stages": {"exporter": 0, "decode": 0, "refinement": 0, "verifast": 124}},
            "partial": lambda *a, **k: {"stages": {"exporter": 0, "decode": 0}},
            "null": lambda *a, **k: {"stages": {"exporter": 0, "decode": 0, "refinement": None, "verifast": 1}},
            "bool": lambda *a, **k: {"stages": {"exporter": 0, "decode": 0, "refinement": 0, "verifast": True}},
            "wrong-type": lambda *a, **k: ["not", "a", "dict"],
            "not-run": lambda *a, **k: {"status": "NOT_RUN", "stages": None},
        }
        def raises(*a, **k):
            raise RuntimeError("dispatch failed")
        cases["exception"] = raises
        for label, executor in cases.items():
            with self.subTest(label=label):
                result = self.run_controls(executor, name=label)
                self.assertFalse(result["all_matched"])
                expected = "NOT_RUN" if label == "not-run" else "INCONCLUSIVE"
                self.assertEqual({r["classification"] for r in result["cases"].values()}, {expected})

    def test_source_change_during_dispatch_is_inconclusive(self):
        inner = self.matching_executor()
        def mutate(case, args, **kwargs):
            result = inner(case, args, **kwargs)
            (case / "verified/lib.rs").write_bytes(b"changed")
            return result
        result = self.run_controls(mutate, name="mutated")
        self.assertEqual({r["classification"] for r in result["cases"].values()}, {"INCONCLUSIVE"})

    def test_controls_require_the_prepared_raw_caller_record(self):
        evidence = self.root / "ev"
        case = evidence / "raw_local_caller" / "cases" / callback.RAW_LOCAL_CALLER_NAME
        (case / "original").mkdir(parents=True)
        (case / "verified").mkdir()
        (case / "original/lib.rs").write_bytes(self.original)
        (case / "verified/lib.rs").write_bytes(self.verified)
        prep = evidence / "raw_local_caller" / "preparation.json"
        self.assertFalse(callback._r19_raw_case_matches(evidence, case))
        record = {"case": callback.RAW_LOCAL_CALLER_NAME, "verified_sha256": sha(self.verified),
                  "original_sha256": sha(self.original)}
        prep.write_text(json.dumps(record))
        self.assertTrue(callback._r19_raw_case_matches(evidence, case))
        (case / "verified/lib.rs").write_bytes(self.verified + b"\n")
        self.assertFalse(callback._r19_raw_case_matches(evidence, case))
        prep.write_text("[]")
        self.assertFalse(callback._r19_raw_case_matches(evidence, case))

    def test_registration_gate_requires_exact_r19_profile(self):
        profile_path = HERE / "GLUE-PROFILE.json"
        self.assertTrue(callback._r19_registration_matches(profile_path, callback.R11_PROFILE))
        self.assertFalse(callback._r19_registration_matches(profile_path, callback.R10_PROFILE))
        changed = json.loads(profile_path.read_text())
        changed["r19_registration"]["candidate_tool_commit"] = "0" * 40
        other = self.root / "profile.json"
        other.write_text(json.dumps(changed))
        self.assertFalse(callback._r19_registration_matches(other, callback.R11_PROFILE))
        self.assertFalse(callback._r19_registration_matches(self.root / "absent.json", callback.R11_PROFILE))
        receipt = {"profile": callback.R11_PROFILE}
        self.assertTrue(callback._r17_registration_matches(profile_path, callback.R11_PROFILE, receipt))
        self.assertFalse(callback._r17_registration_matches(other, callback.R11_PROFILE, receipt))


if __name__ == "__main__":
    unittest.main()
