#!/usr/bin/env python3
"""Synthetic R17 RawPtr control tests; no compiler or Cloud service runs."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "r17_rawptr_controls", HERE / "r17-rawptr-controls.py")
if spec is None or spec.loader is None:
    raise RuntimeError("R17 RawPtr controls module is unavailable")
controls = importlib.util.module_from_spec(spec)
spec.loader.exec_module(controls)
callback_spec = importlib.util.spec_from_file_location(
    "r17_first_callback", HERE / "first-callback.py")
if callback_spec is None or callback_spec.loader is None:
    raise RuntimeError("first-callback module is unavailable")
callback = importlib.util.module_from_spec(callback_spec)
callback_spec.loader.exec_module(callback)
SOURCE_SHA = "a" * 64


def sha(data):
    return hashlib.sha256(data).hexdigest()


class Consumer:
    def _hashes(self, case):
        return {"original/lib.rs": sha((case / "original/lib.rs").read_bytes()),
                "verified/lib.rs": sha((case / "verified/lib.rs").read_bytes()),
                "small_sort_source": SOURCE_SHA}

    def _stage_receipts(self, case, stages, baseline):
        valid = type(stages) is dict
        for stage in controls.STAGES:
            path = case / f"{stage}-stage.json"
            try:
                receipt = json.loads(path.read_text())
                valid = valid and (receipt.get("stage") == stage and
                    type(stages.get(stage)) is int and type(stages.get(stage)) is not bool and
                    receipt.get("exit_code") == stages.get(stage) and
                    receipt.get("source_before") == baseline == receipt.get("source_after") and
                    receipt.get("source_unchanged") is True and
                    receipt.get("status") in {"SUCCESS", "SUCCEEDED", "COMPLETED"})
            except (OSError, json.JSONDecodeError, AttributeError, TypeError):
                valid = False
        return {"admitted": valid}


class RawPtrControlsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.consumer = Consumer()
        self.counter = 0

    def tearDown(self):
        self.temp.cleanup()

    def make_case(self, name, source=None):
        self.counter += 1
        case = self.root / f"{name}-{self.counter}"
        (case / "original").mkdir(parents=True)
        (case / "verified").mkdir()
        verified = controls.BASE if source is None else source
        (case / "original/lib.rs").write_bytes(controls.BASE)
        (case / "verified/lib.rs").write_bytes(verified)
        return case, verified

    def write_stages(self, case, name, overrides=None, status_overrides=None,
                     missing=()):
        stages = {"exporter": 0, "decode": 0, "refinement": 0, "verifast": 0}
        if name != "identical_local_rawmut":
            stages.update(refinement=1, verifast=1)
        stages.update(overrides or {})
        statuses = {stage: "SUCCESS" for stage in controls.STAGES}
        statuses.update(status_overrides or {})
        hashes = self.consumer._hashes(case)
        for stage in controls.STAGES:
            if stage in missing:
                continue
            pair = dict(hashes)
            (case / f"{stage}-stage.json").write_text(json.dumps({
                "stage": stage, "exit_code": stages[stage], "status": statuses[stage],
                "source_unchanged": True, "source_before": pair, "source_after": pair}))
        return stages, hashes

    def classify(self, name, diagnostic=None, *, stages=None, statuses=None,
                 missing=(), target_context=True, source_mutation=False,
                 overrides=None):
        variants = controls._variants()
        source, anchor = variants[name]
        case, source = self.make_case(name, source)
        stage_map, hashes = self.write_stages(case, name, stages, statuses, missing)
        if diagnostic is not None:
            if name == "changed_local_contents":
                line = f"ERROR: {diagnostic}\n"
            else:
                detail = ("While checking that the command at bb0:0 in the original program refines "
                          "the command at bb1:0 in the verified program: " + diagnostic)
                if target_context:
                    detail += (f"\nfunction={controls.CONTROL_FUNCTION}\n"
                               "======== Commands of basic block bb0 of original program ========\n"
                               "0: RawPtr(place=values)\n"
                               "======== Commands of basic block bb1 of verified program ========\n"
                               "0: RawPtr(place=values)\n")
                    if name == "raw_ref_cross_kind":
                        detail += "1: Ref(place=values)\n"
                line = "ERROR: " + detail + "\n"
            (case / "refinement.out1").write_text(line)
        if source_mutation:
            with (case / "verified/lib.rs").open("ab") as stream:
                stream.write(b"// changed after stage receipts\n")
        execution = {"stages": stage_map, "status": "SUCCESS",
                    "source_unchanged_at_every_stage": not source_mutation}
        execution.update(overrides or {})
        expected = {"original/lib.rs": hashes["original/lib.rs"],
                    "verified/lib.rs": hashes["verified/lib.rs"],
                    "small_sort_source": SOURCE_SHA}
        result = controls._classify(case, name, expected, execution, anchor, self.consumer)
        return result

    def test_control_sources_keep_same_pointer_interface_and_distinct_origins(self):
        variants = controls._variants()
        self.assertEqual(tuple(variants), controls.CASES)
        self.assertIn(b"&raw mut values", variants["identical_local_rawmut"][0])
        self.assertIn(b"&raw const values as *const [u64; 3] as *mut [u64; 3]",
                      variants["mutability_mismatch"][0])
        self.assertIn(b"[11_u64, 20_u64, 5_u64]", variants["changed_local_contents"][0])
        self.assertIn(b"values[0]", variants["unsupported_index_projection"][0])
        self.assertIn(b"&mut values", variants["raw_ref_cross_kind"][0])
        for source, _ in variants.values():
            self.assertIn(b"-> *mut [u64; 3]", source)

    def test_identical_local_rawmut_positive_is_refinement_only(self):
        result = self.classify("identical_local_rawmut")
        self.assertEqual(result["classification"], "RAW_LOCAL_RAWMUT_MATCHED")
        self.assertTrue(result["matched"])
        self.assertFalse(result["accepted"])
        self.assertFalse(result["proof_credit"])
        failed_refinement = self.classify("identical_local_rawmut",
            stages={"refinement": 1})
        self.assertFalse(failed_refinement["matched"])

    def test_exact_refusals_require_function_and_command_target_context(self):
        diagnostics = {
            "mutability_mismatch": controls.DIAGNOSTICS["mutability_mismatch"],
            "changed_local_contents": controls.DIAGNOSTICS["changed_local_contents"],
            "unsupported_index_projection": controls.DIAGNOSTICS["unsupported_index_projection"],
            "raw_ref_cross_kind": controls.DIAGNOSTICS["raw_ref_cross_kind"],
        }
        for name, diagnostic in diagnostics.items():
            with self.subTest(case=name):
                result = self.classify(name, diagnostic)
                self.assertEqual(result["classification"], "EXPECTED_REFINER_REFUSAL")
                self.assertTrue(result["matched"])
                self.assertFalse(result["accepted"])
                self.assertFalse(result["proof_credit"])
        generic = self.classify("mutability_mismatch", "generic nonzero exit")
        self.assertFalse(generic["matched"])
        unbound = self.classify("mutability_mismatch",
            controls.DIAGNOSTICS["mutability_mismatch"], target_context=False)
        self.assertFalse(unbound["matched"])
        wrong_local_pair = self.classify("changed_local_contents",
            "The states of the two locals values and begin whose address is taken are not equal")
        self.assertFalse(wrong_local_pair["matched"])

    def test_timeout_partial_missing_null_and_wrong_type_fail_closed(self):
        timeout = self.classify("mutability_mismatch",
            controls.DIAGNOSTICS["mutability_mismatch"],
            stages={"refinement": 124})
        self.assertFalse(timeout["matched"])
        partial = self.classify("mutability_mismatch",
            controls.DIAGNOSTICS["mutability_mismatch"],
            overrides={"stages": {"exporter": 0, "decode": 0}})
        self.assertEqual(partial["classification"], "INCONCLUSIVE")
        missing = self.classify("mutability_mismatch",
            controls.DIAGNOSTICS["mutability_mismatch"], missing=("decode",))
        self.assertFalse(missing["matched"])
        null = self.classify("mutability_mismatch",
            controls.DIAGNOSTICS["mutability_mismatch"], overrides={"stages": None})
        self.assertEqual(null["classification"], "INCONCLUSIVE")
        wrong_type = self.classify("mutability_mismatch",
            controls.DIAGNOSTICS["mutability_mismatch"], stages={"refinement": True})
        self.assertFalse(wrong_type["matched"])
        null_execution = controls._classify(self.root, "mutability_mismatch", {},
                                             None, b"target", self.consumer)
        wrong_execution = controls._classify(self.root, "mutability_mismatch", {},
                                              ["wrong", "type"], b"target", self.consumer)
        self.assertEqual(null_execution["execution_type"], "NoneType")
        self.assertEqual(wrong_execution["execution_type"], "list")

    def test_not_run_source_stage_and_target_mismatches_are_preserved(self):
        not_run = self.classify("mutability_mismatch",
            overrides={"status": "NOT_RUN"})
        self.assertEqual(not_run["classification"], "NOT_RUN")
        self.assertEqual(not_run["execution_status"], "NOT_RUN")
        source = self.classify("mutability_mismatch",
            controls.DIAGNOSTICS["mutability_mismatch"], source_mutation=True)
        self.assertFalse(source["matched"])
        stage = self.classify("mutability_mismatch",
            controls.DIAGNOSTICS["mutability_mismatch"], stages={"decode": 1})
        self.assertFalse(stage["matched"])

    def test_executor_exception_and_status_are_retained(self):
        case, _ = self.make_case("exception")
        result = controls._classify(case, "mutability_mismatch", {}, {
            "exception": {"type": "RuntimeError", "message": "original failure"},
            "status": "FAILED", "stages": None}, b"target", self.consumer)
        self.assertEqual(result["classification"], "INCONCLUSIVE")
        self.assertEqual(result["execution_exception"],
                         {"type": "RuntimeError", "message": "original failure"})
        self.assertEqual(result["execution_status"], "FAILED")

    def test_run_uses_campaign_receipts_and_keeps_controls_separate(self):
        evidence = self.root / "evidence"
        evidence.mkdir()

        def dispatch(case, args, env):
            name = json.loads((case / "case.json").read_text())["case"]
            stages = {"exporter": 0, "decode": 0, "refinement": 0, "verifast": 0}
            if name != "identical_local_rawmut":
                stages.update(refinement=1, verifast=1)
                diagnostic = controls.DIAGNOSTICS.get(name)
                body = (f"ERROR: While checking that command: {diagnostic}\n"
                        f"function={controls.CONTROL_FUNCTION}\n"
                        "======== Commands of basic block ========\nRawPtr\nRef\n")
                if name == "changed_local_contents":
                    body = "ERROR: " + diagnostic + "\n"
                (case / "refinement.out1").write_text(body)
            hashes = self.consumer._hashes(case)
            for stage in controls.STAGES:
                (case / f"{stage}-stage.json").write_text(json.dumps({
                    "stage": stage, "exit_code": stages[stage], "status": "SUCCESS",
                    "source_unchanged": True,
                    "source_before": hashes, "source_after": hashes}))
            return {"status": "SUCCESS", "stages": stages,
                    "source_unchanged_at_every_stage": True}

        result = controls.run(evidence, object(), {}, dispatch, self.consumer,
                              "synthetic-profile", source_sha256=SOURCE_SHA)
        self.assertTrue(result["all_matched"])
        self.assertFalse(result["accepted"])
        self.assertFalse(result["proof_credit"])
        self.assertEqual(set(result["cases"]), set(controls.CASES))

    def test_run_preserves_dispatch_exception_and_status(self):
        evidence = self.root / "exception-evidence"
        evidence.mkdir()

        def raising_dispatch(case, args, env):
            raise RuntimeError("dispatch sentinel")

        result = controls.run(evidence, object(), {}, raising_dispatch, self.consumer,
                              "synthetic-profile", source_sha256=SOURCE_SHA)
        first = result["cases"]["identical_local_rawmut"]
        self.assertEqual(first["classification"], "INCONCLUSIVE")
        self.assertEqual(first["execution_exception"],
                         {"type": "RuntimeError", "message": "dispatch sentinel"})
        self.assertEqual(first["execution_status"], "FAILED")
        self.assertFalse(result["all_matched"])

    def test_first_callback_requires_exact_r17_registration_and_keeps_raw_frontier(self):
        profile = {"profile": callback.R11_PROFILE,
                   "effective_tool_commit": callback.R17_CANDIDATE_TOOL_COMMIT,
                   "r17_registration": callback.R17_PROFILE_REGISTRATION}
        path = self.root / "GLUE-PROFILE.json"
        path.write_text(json.dumps(profile))
        receipt = {"profile": callback.R11_PROFILE}
        self.assertTrue(callback._r17_registration_matches(path, callback.R11_PROFILE, receipt))
        del profile["r17_registration"]
        path.write_text(json.dumps(profile))
        self.assertFalse(callback._r17_registration_matches(path, callback.R11_PROFILE, receipt))
        profile["r17_registration"] = dict(callback.R17_PROFILE_REGISTRATION,
                                            candidate_tool_commit="0" * 40)
        profile["effective_tool_commit"] = "0" * 40
        path.write_text(json.dumps(profile))
        self.assertFalse(callback._r17_registration_matches(path, callback.R11_PROFILE, receipt))
        called_controls = []
        skipped = callback._run_r17_controls_if_registered(
            False, {"preparation_sha256": "b" * 64,
                    "full_body_execution_observation": {},
                    "record": {"source_sha256": SOURCE_SHA}},
            lambda: (called_controls.append(True) or {}))
        self.assertEqual(called_controls, [])
        self.assertEqual(skipped["classification"], "NOT_APPLICABLE_R17_REGISTRATION_ABSENT")

        called = []
        raw = callback._run_raw_local_caller_after_controls(
            {"classification": "INCONCLUSIVE", "all_matched": False},
            lambda: (called.append(True) or {"classification": "RAW_CALLER_FRONTIER_REACHED"}))
        self.assertEqual(called, [True])
        self.assertEqual(raw["classification"], "RAW_CALLER_FRONTIER_REACHED")
        self.assertFalse(raw["rawptr_controls"]["all_matched"])


if __name__ == "__main__":
    unittest.main()
