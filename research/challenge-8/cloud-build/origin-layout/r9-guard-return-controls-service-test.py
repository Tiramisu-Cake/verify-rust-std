#!/usr/bin/env python3
"""Synthetic tests for the source-bound R9 guard-return control runner."""
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
    "r9_guard_return_controls", HERE / "r9-guard-return-controls.py")
if spec is None or spec.loader is None:
    raise RuntimeError("R9 guard-return controls module is unavailable")
controls = importlib.util.module_from_spec(spec)
spec.loader.exec_module(controls)


SOURCE = b"""#![no_std]
unsafe fn insert_tail() {
    /*@ {
        guard_current_return_recover();
        assert ref_readonly_end_token::<u64>(?r9_guard_ref, ?r9_tmp_origin, ?r9_tmp_share);
        open [1/4]array::<u64>(r9_guard_ref, 1, ?r9_drop_current);
        open [1/4]array::<u64>(r9_guard_ref + 1, 0, _);
        end_ref_readonly::<u64>(r9_guard_ref);
        merge_fractions points_to::<u64>(r9_tmp_origin, _);
        assert [1/2](*r9_tmp_origin |-> ?r9_tmp_current);
    } @*/
}
"""


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _source_case(root):
    case = root / "fullbody"
    (case / "original").mkdir(parents=True)
    (case / "verified").mkdir()
    original = b"#![no_std]\npub fn untouched() {}\n"
    verified = SOURCE
    (case / "original/lib.rs").write_bytes(original)
    (case / "verified/lib.rs").write_bytes(verified)
    record = {"schema": "first-actual-callback-source-v1",
              "profile": controls.R9_PROFILE, "prefix": False,
              "late_callback_scope_recovery_requested": True,
              "mutation": None, "original_sha256": _sha(original),
              "verified_sha256": _sha(verified),
              "source_sha256": "85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1"}
    return case, record


def _write_stage(case, stage, code, original_sha, verified_sha,
                 *, status=None, exit_override=None, source_sha=None):
    pair = {"original/lib.rs": original_sha, "verified/lib.rs": verified_sha,
            "small_sort_source": (source_sha or
                "85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1")}
    receipt = {"stage": stage,
               "exit_code": code if exit_override is None else exit_override,
               "source_unchanged": True,
               "source_before": pair, "source_after": pair}
    if status is not None:
        receipt["status"] = status
    (case / f"{stage}-stage.json").write_text(json.dumps(receipt))


def _event(recovery, *, cleanup="true", outcome="returning", block="143",
           selected_hash="DefPathHash(Fingerprint(12908149020305531562, 11549365108250137374))"):
    return ("R9_GUARD_EVENT at=verified/lib.rs(9,5) "
            "function=insert_tail def_hash=def123 mir_fingerprint=mir456 "
            "mir_phase=Runtime(Optimized) body_span=verified/lib.rs(1,1) "
            f"block={block} cleanup={cleanup} at=verified/lib.rs(9,5) "
            f"kind=selected_drop outcome={outcome} key=__vf_generated_drop_glue "
            "selected=core::slice::sort::CopyOnDrop::drop (selected lang item) "
            f"selected_hash={selected_hash} guard=core::slice::sort::CopyOnDrop "
            "normal_target=144 unwind=cleanup:144 receiver=__vf_drop_receiver_143 "
            f"recovery={recovery} tmp=stack$tmp storage_live=true heap_total=8 "
            "selected_total=3 shown=3")


def _baseline(case, record, *, events=True, bad_status=None, missing_stage=None):
    codes = {"exporter": 0, "decode": 0, "refinement": 0, "verifast": 1}
    for stage, code in codes.items():
        if stage == missing_stage:
            continue
        status = "SUCCESS"
        if bad_status and stage == bad_status[0]:
            status = bad_status[1]
        _write_stage(case, stage, code, record["original_sha256"],
                     record["verified_sha256"], status=status,
                     source_sha=record["source_sha256"])
    log = ""
    if events:
        log += _event("before") + "\n" + _event("complete") + "\n"
    log += "verified/lib.rs(100,1): error: post-recovery full CURRENT owner remains pending\n"
    (case / "verifast.log").write_text(log)


def _execute(case, args, env, behavior=None):
    meta = json.loads((case / "case.json").read_text())
    original_sha = _sha((case / "original/lib.rs").read_bytes())
    verified_sha = _sha((case / "verified/lib.rs").read_bytes())
    if behavior == "raise":
        raise RuntimeError("synthetic executor exception")
    if behavior == "null":
        return None
    if behavior == "bool":
        return False
    if behavior == "wrong_type":
        return ["not", "an", "execution receipt"]

    stages = dict(meta["expected_stages"])
    for stage, code in stages.items():
        if behavior == "missing_receipt" and stage == "decode":
            continue
        status = "SUCCESS"
        if behavior == "wrong_status" and stage == "verifast":
            status = "FAILED"
        exit_override = True if behavior == "bool_exit" and stage == "verifast" else None
        _write_stage(case, stage, code, original_sha, verified_sha,
                     status=status, exit_override=exit_override,
                     source_sha=meta["expected_source_hashes"]["small_sort_source"])

    line = meta["expected_error_line"]
    if meta["case_name"] == "duplicate_marker":
        expected_span = meta["expected_error_span"]
        line = expected_span[0]
    elif meta["case_name"] == "missing_marker":
        source = (case / "verified/lib.rs").read_bytes()
        line = next(index for index, row in enumerate(source.splitlines(), 1)
                    if b"unsafe fn insert_tail" in row)
    if behavior == "ambiguous_line":
        line += 1
    execution_line = line
    if behavior == "loop_refusal":
        execution_line = max(2, line - 2)
    target_line = f"verified/lib.rs({execution_line},4): Executing statement\n"
    before = _event("before") + "\n"
    if behavior == "no_binding":
        before = ""
    elif behavior == "wrong_binding":
        before = _event("before", selected_hash="different-selected-hash") + "\n"
    elif behavior == "different_mir_binding":
        before = before.replace("mir_fingerprint=mir456", "mir_fingerprint=mutant-mir")
    if behavior == "complete_before_error":
        before += _event("complete") + "\n"
    if meta.get("expected_diagnostic"):
        error = meta["expected_diagnostic"]
        error_line = line
        if meta["case_name"] == "duplicate_marker":
            start_line, start_col, end_line, end_col = meta["expected_error_span"]
            if behavior == "wrong_span":
                start_col += 1
            log = (f"verified/lib.rs({start_line},{start_col}-{end_line},{end_col}): "
                   f"error: {error}\n")
        else:
            log = f"verified/lib.rs({error_line},4): error: {error}\n"
    else:
        case_name = meta["case_name"]
        if case_name == "omit_end":
            message = "No matching heap chunks: points_to(r9_tmp_origin,_)"
        elif case_name == "duplicate_end":
            message = "No matching heap chunks: ref_readonly_end_token"
            if behavior == "canonical_spec":
                message = ("/workspace/merge-work/runner-temp/challenge8-merge-overnight/"
                           "verifast-tracked-md-source/bin/rust/aliasing.rsspec(50,9-31): "
                           "error: No matching heap chunks: ref_readonly_end_token")
        elif (case_name == "wrongorigin" and
              meta.get("mutant_version") == "wrongorigin-v2-end-token-origin"):
            message = "No matching heap chunks: ref_readonly_end_token(begin,_,_)"
            if behavior == "canonical_spec":
                message = ("/workspace/merge-work/runner-temp/challenge8-merge-overnight/"
                           "verifast-tracked-md-source/bin/rust/aliasing.rsspec(50,9-31): "
                           "error: No matching heap chunks: ref_readonly_end_token(begin,_,_)")
            elif behavior == "wrong_spec":
                message = ("bin/rust/aliasing.rsspec(51,1): No matching heap chunks: "
                           "ref_readonly_end_token(begin,_,_)")
        else:
            message = "Cannot prove condition points_to(begin,_)"
        if behavior == "wrong_predicate":
            message = "No matching heap chunks: unrelated_predicate"
        error_location = (execution_line - 1 if behavior == "loop_refusal" else
                          error_line if 'error_line' in locals() else line)
        if behavior == "loop_refusal":
            message = "Loop invariant required."
        if behavior == "canonical_spec":
            log = f"{message}\n"
        elif behavior == "wrong_spec":
            log = f"{message}: error: diagnostic at the wrong spec location\n"
        else:
            log = f"verified/lib.rs({error_location},4): error: {message}\n"
        if behavior == "ambiguous_line":
            log += f"verified/lib.rs({line + 1},4): error: {message}\n"
    if behavior == "timeout":
        stages["verifast"] = 124
        _write_stage(case, "verifast", 124, original_sha, verified_sha, status="FAILED",
                     source_sha=meta["expected_source_hashes"]["small_sort_source"])
        log = "executor timed out\n"
    elif behavior == "wrong_exit":
        stages["verifast"] = 2
        _write_stage(case, "verifast", 2, original_sha, verified_sha, status="FAILED",
                     source_sha=meta["expected_source_hashes"]["small_sort_source"])
    elif behavior == "partial_stages":
        stages.pop("decode")
    (case / "verifast.log").write_text(before + target_line + log)
    if behavior == "mutated_source":
        with (case / "verified/lib.rs").open("ab") as stream:
            stream.write(b"// changed by synthetic stage\n")
    return {"stages": stages,
            "source_unchanged_at_every_stage": behavior != "mutated_source"}


class R9GuardReturnControlsTests(unittest.TestCase):
    def _run(self, root, *, behavior=None, baseline_events=True, baseline_status=None,
             missing_baseline_stage=None, profile=None, source_profile=None, callback=None):
        source_case, record = _source_case(root)
        if source_profile is not None:
            record["profile"] = source_profile
        _baseline(source_case, record, events=baseline_events,
                  bad_status=baseline_status, missing_stage=missing_baseline_stage)
        calls = []
        parent_env = {controls.TRACE_ENV: "parent-trace", "KEEP": "parent"}

        def execute(case, args, env):
            calls.append(case.name)
            self.assertEqual(env[controls.TRACE_ENV], "1")
            self.assertEqual(env[controls.RECOVERY_ENV], "1")
            if callback:
                return callback(case, args, env)
            result = _execute(case, args, env,
                              behavior if case.name == "omit_end" else None)
            # This is the child environment handed to the callback, never the
            # caller's environment object.
            env["CALLBACK_MUTATION"] = "private"
            return result

        output = controls.run(root / "controls", SimpleNamespace(
            profile=profile or controls.R9_PROFILE), parent_env, execute,
            source_case, record)
        self.assertEqual(parent_env, {controls.TRACE_ENV: "parent-trace", "KEEP": "parent"})
        return output, calls

    def test_r10_profile_alias_and_cross_profile_refusal(self):
        with tempfile.TemporaryDirectory() as temporary:
            output, calls = self._run(Path(temporary), profile=controls.R10_PROFILE,
                                      source_profile=controls.R10_PROFILE)
            self.assertTrue(output["all_matched"])
            self.assertEqual(output["classification"],
                             "ALL_INTENDED_R10_GUARD_RETURN_CONTROLS_MATCHED")
            self.assertFalse(output["proof_credit"])
            self.assertEqual(set(calls), set(output["cases"]))
        for active, source in ((controls.R9_PROFILE, controls.R10_PROFILE),
                               (controls.R10_PROFILE, controls.R9_PROFILE)):
            with self.subTest(active=active), tempfile.TemporaryDirectory() as temporary:
                output, calls = self._run(Path(temporary), profile=active, source_profile=source)
                self.assertEqual(calls, [])
                self.assertTrue(all(row["classification"] == "NOT_RUN"
                                    for row in output["cases"].values()))

    def test_r11_profile_has_distinct_classification_without_proof_credit(self):
        with tempfile.TemporaryDirectory() as temporary:
            output, calls = self._run(Path(temporary), profile=controls.R11_PROFILE,
                                      source_profile=controls.R11_PROFILE)
            self.assertTrue(output["all_matched"])
            self.assertEqual(output["classification"],
                             "ALL_INTENDED_R11_GUARD_RETURN_CONTROLS_MATCHED")
            self.assertFalse(output["accepted"])
            self.assertFalse(output["proof_credit"])
            self.assertEqual(set(calls), set(output["cases"]))

    def test_exact_baseline_and_all_five_narrow_controls(self):
        with tempfile.TemporaryDirectory() as temporary:
            output, calls = self._run(Path(temporary))
            self.assertTrue(output["baseline"]["admitted"])
            self.assertTrue(output["all_matched"])
            self.assertEqual(output["classification"],
                             "ALL_INTENDED_R9_GUARD_RETURN_CONTROLS_MATCHED")
            self.assertFalse(output["accepted"])
            self.assertFalse(output["proof_credit"])
            self.assertEqual(set(calls), set(controls.CASES))
            self.assertEqual(set(output["cases"]), set(controls.CASES))
            self.assertTrue(all(row["matched"] for row in output["cases"].values()))
            for name in ("omit_end", "duplicate_end", "wrongorigin"):
                self.assertEqual(output["cases"][name]["classification"],
                                 "EXPECTED_RESOURCE_REFUSAL")
            self.assertEqual(output["cases"]["duplicate_marker"]["classification"],
                             "EXPECTED_ADMISSION_REJECTION")
            self.assertEqual(output["cases"]["missing_marker"]["classification"],
                             "EXPECTED_ADMISSION_REJECTION")

    def test_r10_wrongorigin_v2_is_exact_resource_control(self):
        with tempfile.TemporaryDirectory() as temporary:
            mutants = {}

            def execute(case, args, env):
                mutants[case.name] = (case / "verified/lib.rs").read_bytes()
                return _execute(case, args, env)

            output, calls = self._run(Path(temporary), profile=controls.R10_PROFILE,
                                      source_profile=controls.R10_PROFILE,
                                      callback=execute)
            self.assertTrue(output["all_matched"])
            self.assertEqual(set(calls), set(controls.CASES))
            self.assertEqual(set(output["cases"]), set(controls.CASES))
            control = output["cases"]["wrongorigin"]
            self.assertEqual(mutants["wrongorigin"].count(
                controls.WRONG_END_TOKEN_ORIGIN_V2), 1)
            self.assertEqual(mutants["wrongorigin"].count(
                controls.END_READONLY), 0)
            self.assertEqual(control["classification"], "EXPECTED_RESOURCE_REFUSAL")
            self.assertTrue(control["error_at_target"])
            self.assertTrue(control["target_line_executed"])
            self.assertEqual(control["last_executed_line_before_error"],
                             control["expected_error_line"])
            self.assertEqual(control["expected_predicates"], ["ref_readonly_end_token"])

    def test_r10_wrongorigin_v2_accepts_canonical_spec_at_last_target(self):
        with tempfile.TemporaryDirectory() as temporary:
            output, _ = self._run(
                Path(temporary), profile=controls.R10_PROFILE,
                source_profile=controls.R10_PROFILE,
                callback=lambda case, args, env: _execute(
                    case, args, env,
                    "canonical_spec" if case.name == "wrongorigin" else None))
            row = output["cases"]["wrongorigin"]
            self.assertTrue(row["matched"])
            self.assertTrue(row["canonical_spec_error_last_at_target"])
            self.assertFalse(row["error_at_target"])
            self.assertTrue(row["native_pre_recovery_binding"]["admitted"])
            self.assertTrue(row["target_line_executed"])
            self.assertEqual(row["last_executed_line_before_error"],
                             row["expected_error_line"])
            self.assertTrue(row["recovery_completion_absent"])

    def test_r10_wrongorigin_canonical_spec_still_requires_binding_and_stage_receipts(self):
        for defect in ("missing_binding", "missing_stage_receipt"):
            with self.subTest(defect=defect), tempfile.TemporaryDirectory() as temporary:
                def execute(case, args, env):
                    result = _execute(case, args, env,
                                      "canonical_spec" if case.name == "wrongorigin" else None)
                    if case.name == "wrongorigin":
                        if defect == "missing_binding":
                            log = case / "verifast.log"
                            log.write_text(log.read_text().replace(_event("before") + "\n", "", 1))
                        else:
                            (case / "decode-stage.json").unlink()
                    return result

                output, _ = self._run(Path(temporary), profile=controls.R10_PROFILE,
                                      source_profile=controls.R10_PROFILE, callback=execute)
                row = output["cases"]["wrongorigin"]
                self.assertFalse(row["matched"])
                self.assertEqual(row["classification"], "INCONCLUSIVE")
                if defect == "missing_binding":
                    self.assertTrue(row["canonical_spec_error_last_at_target"])
                    self.assertFalse(row["native_pre_recovery_binding"]["admitted"])
                else:
                    self.assertFalse(row["stage_receipt_gate"]["admitted"])

    def test_r10_wrongorigin_v2_rejects_bad_receipt_binding_and_spec_location(self):
        for behavior in ("wrong_spec", "missing_receipt", "wrong_status",
                         "partial_stages", "mutated_source", "no_binding",
                         "wrong_binding", "loop_refusal", "complete_before_error"):
            with self.subTest(behavior=behavior), tempfile.TemporaryDirectory() as temporary:
                output, _ = self._run(
                    Path(temporary), profile=controls.R10_PROFILE,
                    source_profile=controls.R10_PROFILE,
                    callback=lambda case, args, env: _execute(
                        case, args, env,
                        behavior if case.name == "wrongorigin" else None))
                row = output["cases"]["wrongorigin"]
                self.assertFalse(row["matched"])
                self.assertEqual(row["classification"], "INCONCLUSIVE")

    def test_r10_wrongorigin_v2_rejects_unrelated_or_early_diagnostics(self):
        for behavior in ("wrong_predicate", "wrong_binding", "loop_refusal",
                         "complete_before_error"):
            with self.subTest(behavior=behavior), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)

                def execute(case, args, env):
                    return _execute(case, args, env,
                                    behavior if case.name == "wrongorigin" else None)

                output, _ = self._run(root, profile=controls.R10_PROFILE,
                                      source_profile=controls.R10_PROFILE, callback=execute)
                row = output["cases"]["wrongorigin"]
                self.assertFalse(row["matched"])
                self.assertEqual(row["classification"], "INCONCLUSIVE")

    def test_duplicate_marker_binds_first_outer_statement_span(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_case, record = _source_case(root)
            _baseline(source_case, record)
            calls = []
            output = controls.run(root / "controls", SimpleNamespace(profile=controls.R9_PROFILE),
                                  {}, lambda case, args, env: _execute(case, args, env),
                                  source_case, record)
            row = output["cases"]["duplicate_marker"]
            self.assertTrue(row["matched"])
            self.assertEqual(row["expected_error_span"], (3, 5, 11, 10))
            with tempfile.TemporaryDirectory() as mismatch_temp:
                mismatch_root = Path(mismatch_temp)
                mismatch_source, mismatch_record = _source_case(mismatch_root)
                _baseline(mismatch_source, mismatch_record)

                def mismatch_execute(case, args, env):
                    return _execute(case, args, env,
                                    "wrong_span" if case.name == "duplicate_marker" else None)

                mismatch = controls.run(
                    mismatch_root / "controls", SimpleNamespace(profile=controls.R9_PROFILE),
                    {}, mismatch_execute, mismatch_source, mismatch_record)
                self.assertFalse(mismatch["cases"]["duplicate_marker"]["matched"])
                self.assertEqual(mismatch["cases"]["duplicate_marker"]["classification"],
                                 "INCONCLUSIVE")

    def test_baseline_requires_cleanup_return_and_completion_pair(self):
        for bad in ("missing", "wrong_cleanup", "wrong_outcome", "duplicate"):
            with self.subTest(bad=bad), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                source_case, record = _source_case(root)
                _baseline(source_case, record, events=False)
                log = source_case / "verifast.log"
                before, complete = _event("before"), _event("complete")
                if bad == "missing":
                    before = ""
                elif bad == "wrong_cleanup":
                    before = _event("before", cleanup="false")
                    complete = _event("complete", cleanup="false")
                elif bad == "wrong_outcome":
                    before = _event("before", outcome="unwinding")
                    complete = _event("complete", outcome="unwinding")
                elif bad == "duplicate":
                    before += "\n" + before
                log.write_text(before + "\n" + complete +
                                "\nverified/lib.rs(100,1): error: expected later proof failure\n")
                calls = []
                output = controls.run(root / "controls", SimpleNamespace(profile=controls.R9_PROFILE),
                                      {}, lambda *args: calls.append(args), source_case, record)
                self.assertFalse(output["baseline"]["admitted"])
                self.assertEqual(calls, [])
                self.assertTrue(all(row["classification"] == "NOT_RUN"
                                    for row in output["cases"].values()))

    def test_baseline_drop_pair_requires_same_dynamic_binding(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_case, record = _source_case(root)
            _baseline(source_case, record, events=False)
            (source_case / "verifast.log").write_text(
                _event("before") + "\n" +
                _event("complete", selected_hash="different-selected-hash") + "\n" +
                "verified/lib.rs(100,1): error: later failure\n")
            output = controls.run(root / "controls", SimpleNamespace(profile=controls.R9_PROFILE),
                                  {}, lambda *args: self.fail("mutants must not run"),
                                  source_case, record)
            self.assertFalse(output["baseline"]["admitted"])

    def test_mutant_binding_uses_stable_drop_identity_not_mir_position(self):
        with tempfile.TemporaryDirectory() as temporary:
            output, _ = self._run(Path(temporary), callback=lambda case, args, env:
                                  _execute(case, args, env,
                                           "different_mir_binding" if case.name == "omit_end" else None))
            self.assertEqual(output["cases"]["omit_end"]["classification"],
                             "EXPECTED_RESOURCE_REFUSAL")

    def test_strict_baseline_receipts_reject_missing_wrongstatus_bool_and_setup_exit(self):
        scenarios = (("missing", None, None),
                     ("wrongstatus", ("verifast", "FAILED"), None),
                     ("setup_exit", None, 124),
                     ("bool_exit", None, True),
                     ("wrong_source_pin", None, None))
        for label, status, override in scenarios:
            with self.subTest(label=label), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                source_case, record = _source_case(root)
                _baseline(source_case, record)
                if label == "missing":
                    (source_case / "decode-stage.json").unlink()
                elif label == "wrongstatus":
                    path = source_case / "verifast-stage.json"
                    data = json.loads(path.read_text())
                    data["status"] = status[1]
                    path.write_text(json.dumps(data))
                elif label in ("setup_exit", "bool_exit"):
                    path = source_case / "verifast-stage.json"
                    data = json.loads(path.read_text())
                    data["exit_code"] = override
                    path.write_text(json.dumps(data))
                else:
                    path = source_case / "verifast-stage.json"
                    data = json.loads(path.read_text())
                    data["source_before"]["small_sort_source"] = "0" * 64
                    data["source_after"]["small_sort_source"] = "0" * 64
                    path.write_text(json.dumps(data))
                output = controls.run(root / "controls", SimpleNamespace(profile=controls.R9_PROFILE),
                                      {}, lambda *args: self.fail("mutants must not run"),
                                      source_case, record)
                self.assertFalse(output["baseline"]["admitted"])
                self.assertFalse(output["all_matched"])

    def test_missing_null_and_invalid_preparation_source_pin_are_not_run(self):
        for bad in ("missing", None, True, 7, [], {}, "bad-sha"):
            with self.subTest(pin=bad), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                source_case, record = _source_case(root)
                if bad == "missing":
                    record.pop("source_sha256")
                else:
                    record["source_sha256"] = bad
                output = controls.run(root / "controls", SimpleNamespace(profile=controls.R9_PROFILE),
                                      {}, lambda *args: self.fail("invalid setup must not execute"),
                                      source_case, record)
                self.assertFalse(output["all_matched"])
                self.assertNotIn("baseline", output)
                self.assertTrue(all(row["classification"] == "NOT_RUN"
                                    for row in output["cases"].values()))
                self.assertTrue((root / "controls/aggregate.json").is_file())

    def test_baseline_rejects_nonproof_verifier_exit_codes(self):
        for code in (2, -9):
            with self.subTest(code=code), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                source_case, record = _source_case(root)
                _baseline(source_case, record)
                path = source_case / "verifast-stage.json"
                data = json.loads(path.read_text())
                data["exit_code"] = code
                path.write_text(json.dumps(data))
                output = controls.run(root / "controls", SimpleNamespace(profile=controls.R9_PROFILE),
                                      {}, lambda *args: self.fail("mutants must not run"),
                                      source_case, record)
                self.assertFalse(output["baseline"]["admitted"])

    def test_runner_success_status_can_carry_expected_verifier_failure_exit(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_case, record = _source_case(root)
            _baseline(source_case, record)
            path = source_case / "verifast-stage.json"
            data = json.loads(path.read_text())
            data["status"] = "SUCCESS"
            path.write_text(json.dumps(data))
            output = controls.run(root / "controls", SimpleNamespace(profile=controls.R9_PROFILE),
                                  {}, lambda *args: self.fail("mutants must not run"),
                                  source_case, record)
            self.assertTrue(output["baseline"]["admitted"])

    def test_resource_classifier_rejects_execution_receipt_failures_and_wrong_diagnostics(self):
        scenarios = ("raise", "null", "bool", "wrong_type", "missing_receipt",
                     "wrong_status", "bool_exit", "partial_stages", "wrong_predicate",
                     "wrong_exit", "timeout", "ambiguous_line", "no_binding", "wrong_binding",
                     "complete_before_error", "mutated_source")
        for behavior in scenarios:
            with self.subTest(behavior=behavior), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                def callback(case, args, env):
                    if case.name != "omit_end":
                        return _execute(case, args, env)
                    if behavior == "raise":
                        raise RuntimeError("stage crashed")
                    return _execute(case, args, env, behavior)
                output, _ = self._run(root, callback=callback)
                self.assertFalse(output["cases"]["omit_end"]["matched"])
                self.assertFalse(output["accepted"])
                self.assertFalse(output["proof_credit"])
                if behavior in ("null", "bool", "wrong_type", "raise"):
                    self.assertEqual(output["cases"]["omit_end"]["classification"],
                                     "INCONCLUSIVE")

    def test_wrong_profile_and_preexisting_directory_are_not_run(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_case, record = _source_case(root)
            _baseline(source_case, record)
            calls = []
            wrong = controls.run(root / "wrong", SimpleNamespace(profile="R8"), {},
                                 lambda *args: calls.append(args), source_case, record)
            self.assertFalse(wrong["all_matched"])
            self.assertEqual(calls, [])
            existing = root / "existing"
            existing.mkdir()
            again = controls.run(existing, SimpleNamespace(profile=controls.R9_PROFILE), {},
                                 lambda *args: calls.append(args), source_case, record)
            self.assertEqual(calls, [])
            self.assertTrue(all(row["classification"] == "NOT_RUN"
                                for row in again["cases"].values()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
