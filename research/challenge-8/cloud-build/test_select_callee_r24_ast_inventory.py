"""Synthetic tests for the explicit R24 positive-only AST inventory."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

CLOUD = Path(__file__).resolve().parent
sys.path.insert(0, str(CLOUD))

def load(filename, name):
    spec = importlib.util.spec_from_file_location(name, CLOUD / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

AST = load("select-callee-r24-ast-inventory.py", "test_r24_ast_inventory")
ENTRY = load("select-callee-r21-fractional-proof-entry.py", "test_r24_proof_entry")
PHASE = "SORT4-ACTUAL-SELECT-2026-10-24-R24"
ROUTE = "SORT4-ACTUAL-SELECT-2026-10-23-R21"

def sha(data):
    return hashlib.sha256(data).hexdigest()

class FakeCapture:
    def __init__(self, stage):
        self.LINK = SimpleNamespace(stage=MagicMock(side_effect=stage))
    def clear_semantic_opt_ins(self):
        for key in AST.CONTROL_ENV:
            os.environ.pop(key, None)

class PositiveAstInventory(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.case = self.root / "evidence/cases/positive/nine-body-a1-owned-forget"
        self.tool = self.root / "tool"
        self.schema = self.root / "schema"
        self.repo.mkdir()
        (self.case / "original").mkdir(parents=True)
        (self.case / "verified").mkdir()
        self.tool.mkdir()
        self.schema.write_text("schema")
        self.original, self.verified = b"original source", b"verified source"
        (self.case / "original/lib.rs").write_bytes(self.original)
        (self.case / "verified/lib.rs").write_bytes(self.verified)
        self.source_pins = {"original/lib.rs": sha(self.original),
                            "verified/lib.rs": sha(self.verified)}
        self.snapshot_pins = {}
        for label in AST.SNAPSHOT_NAMES:
            filename = f"actual-nested-9-{label}.marshal"
            data = ("snapshot:" + label).encode()
            (self.case / filename).write_bytes(data)
            self.snapshot_pins[label] = {"file": filename, "bytes": len(data),
                                         "sha256": sha(data)}
        self.route_env = {"SMALLSORT_EXECUTION_PROVIDER": "cloud-build",
                          AST.ROUTE_ENV: ROUTE, AST.PHASE_ENV: PHASE}
        self.control_env = {"SORT4_ACTUAL_OWNER_REPO_ROOT": str(self.root / "old"),
            "SORT4_ACTUAL_OWNER_ADMISSION": "old", "SORT4_ACTUAL_NINE_ADMISSION": "old",
            "SORT4_ACTUAL_NESTED_H2_REPO_ROOT": "old",
            "SORT4_ACTUAL_FORGET_OWN_REPO_ROOT": "old",
            "SORT4_A1_NINE_REPO_ROOT": "old", "KEEP_ME": "exact"}

    def tearDown(self):
        self.temp.cleanup()

    def stage_result(self, *, exit_code=0, status="RAN", alter=None,
                     source_before=None, source_after=None, argv=None,
                     returned_argv=None,
                     ast_data=b'[PackageDecl (loc "verified/lib.rs(1,0-1,1)" (Identifier "x"))]',
                     intrinsic=True, pointer=True):
        expected_sources = dict(self.source_pins)
        expected_argv = [str(self.tool / "bin/verifast"), "-rustc_args",
            "--edition 2021", "-verbose", "1", "-dump_ast_with_locs",
            AST.AST_FILENAME, "verified/lib.rs"]
        def stage(case, name, command, args, **kwargs):
            self.assertEqual(name, AST.STAGE_NAME)
            self.assertEqual(command, expected_argv if argv is None else argv)
            self.assertEqual(kwargs, {"gates": True, "pointer_drop": True,
                                      "cap_seconds": 110})
            if callable(alter):
                alter(case)
            if isinstance(alter, dict) and callable(alter.get("before_stage")):
                alter["before_stage"](case)
            if not isinstance(alter, dict) or alter.get("write_ast", True):
                (case / AST.AST_FILENAME).write_bytes(ast_data)
            return {"status": status, "exit": exit_code,
                "argv": expected_argv if returned_argv is None else returned_argv,
                "source_before": expected_sources if source_before is None else source_before,
                "source_after": expected_sources if source_after is None else source_after,
                "source_unchanged": True, "intrinsic_gate_active": intrinsic,
                "pointer_drop_gate_active": pointer,
                "stdout": AST.STAGE_NAME + ".log", "stderr": AST.STAGE_NAME + ".log"}
        return stage

    def invoke(self, stage, *, variant="positive", env=None):
        cap = FakeCapture(stage)
        with patch.dict(os.environ, {**self.route_env, **self.control_env}, clear=True):
            record = AST.run_positive_ast_inventory(cap=cap, repo=self.repo,
                case=self.case, tool_home=self.tool, schema=self.schema,
                compiler_sysroot="/sysroot", deadline_epoch=42, variant=variant,
                expected_sources=self.source_pins, expected_snapshots=self.snapshot_pins,
                env=os.environ if env is None else env)
        return record, cap

    def clean_outputs(self):
        (self.case / AST.RECORD_FILENAME).unlink(missing_ok=True)
        (self.case / AST.AST_FILENAME).unlink(missing_ok=True)

    def test_exact_argv_gates_success_and_zero_credit(self):
        with patch.dict(os.environ, {**self.route_env, **self.control_env}, clear=True):
            before = dict(os.environ)
            record = AST.run_positive_ast_inventory(cap=FakeCapture(self.stage_result()),
                repo=self.repo, case=self.case, tool_home=self.tool, schema=self.schema,
                compiler_sysroot="/sysroot", deadline_epoch=42, variant="positive",
                expected_sources=self.source_pins, expected_snapshots=self.snapshot_pins)
            self.assertEqual(dict(os.environ), before)
        self.assertTrue(record["complete"])
        self.assertEqual(record["proof_credit"], 0)
        self.assertFalse(record["accepted"])
        self.assertEqual(record["body_proof_run"], "UNKNOWN")
        self.assertEqual(record["verifier_execution"], "REQUESTED_NOT_QUALIFIED")
        self.assertEqual(record["stage_name"], "r24-positive-ast")
        self.assertGreater(record["ast_artifact"]["bytes"], 0)
        self.assertEqual(record["ast_artifact"]["structural_validation"]["level"],
                         "STRUCTURAL_ENVELOPE_ONLY")

    def test_nonzero_one_is_diagnostic_data_not_proof(self):
        record, _ = self.invoke(self.stage_result(exit_code=1))
        self.assertTrue(record["complete"])
        self.assertEqual(record["stage"]["exit"], 1)
        self.assertEqual(record["proof_credit"], 0)

    def test_partial_missing_null_wrong_type_and_not_run_are_incomplete(self):
        cases = [
            ("empty", self.stage_result(alter={"write_ast": False,
                "before_stage": lambda c: (c / AST.AST_FILENAME).write_bytes(b"")}),
             "AST artifact"),
            ("missing", self.stage_result(alter={"write_ast": False}), "AST artifact"),
            ("not-run", self.stage_result(status="NOT_RUN"), "typed RAN"),
            ("timeout", self.stage_result(status="TIMEOUT"), "typed RAN"),
            ("error", self.stage_result(status="ERROR"), "typed RAN"),
            ("unexpected-exit", self.stage_result(exit_code=124), "neither success"),
            ("null", lambda *_a, **_k: None, "wrong type"),
            ("wrong-type", lambda *_a, **_k: ["bad"], "wrong type"),
            ("null-exit", self.stage_result(exit_code=None), "typed RAN")]
        for label, stage, expected in cases:
            with self.subTest(label=label):
                record, _ = self.invoke(stage)
                self.assertFalse(record["complete"])
                self.assertEqual(record["proof_credit"], 0)
                self.assertTrue(any(expected in error for error in record["errors"]))
                self.assertTrue((self.case / AST.RECORD_FILENAME).is_file())
                self.clean_outputs()

    def test_source_snapshot_and_stage_binding_drift_are_incomplete(self):
        def drift_source(case):
            (case / "verified/lib.rs").write_bytes(b"mutated source")
        record, _ = self.invoke(self.stage_result(alter=drift_source))
        self.assertFalse(record["source_pins_valid_after"])
        self.assertFalse(record["complete"])
        self.clean_outputs()
        (self.case / "verified/lib.rs").write_bytes(self.verified)
        def drift_snapshot(case):
            (case / "actual-nested-9-body-4.marshal").write_bytes(b"changed snapshot")
        record, _ = self.invoke(self.stage_result(alter=drift_snapshot))
        self.assertFalse(record["snapshots_match_pins_after"])
        self.assertFalse(record["complete"])
        self.clean_outputs()
        (self.case / "actual-nested-9-body-4.marshal").write_bytes(b"snapshot:body-4")
        wrong = dict(self.source_pins, **{"verified/lib.rs": "0" * 64})
        for stage in (self.stage_result(source_before=wrong),
                      self.stage_result(source_after=wrong),
                      self.stage_result(returned_argv=["wrong"]),
                      self.stage_result(intrinsic=False),
                      self.stage_result(pointer=False)):
            record, _ = self.invoke(stage)
            self.assertFalse(record["complete"])
            self.clean_outputs()

    def test_ast_envelope_accepts_quoted_delimiters_and_rejects_partial_outputs(self):
        quoted = b'[PackageDecl (loc "verified/(file[one]).rs(1,0-1,1)" (Identifier "x"))]'
        record, _ = self.invoke(self.stage_result(ast_data=quoted))
        self.assertTrue(record["complete"])
        self.assertTrue(record["ast_artifact"]["structural_validation"]["valid"])
        self.clean_outputs()
        malformed = (
            b'[PackageDecl (Identifier "unfinished)',
            b'[PackageDecl (Identifier "escaped ' + bytes([92]) + b'")',
            b'[PackageDecl (Identifier "x"]',
            b'[PackageDecl (Identifier "x"))]',
            b'\xff[PackageDecl (Identifier "x")]',
        )
        for data in malformed:
            with self.subTest(data=data):
                record, _ = self.invoke(self.stage_result(ast_data=data))
                self.assertFalse(record["complete"])
                self.assertFalse(record["ast_artifact"]["structural_validation"]["valid"])
                self.assertEqual(record["proof_credit"], 0)
                self.clean_outputs()

    def test_exception_observations_are_saved_then_original_error_reraised(self):
        def explode(case, *_args, **_kwargs):
            (case / "verified/lib.rs").write_bytes(b"changed before timeout")
            raise TimeoutError("diagnostic timeout")
        with patch.dict(os.environ, {**self.route_env, **self.control_env}, clear=True):
            before = dict(os.environ)
            with self.assertRaisesRegex(TimeoutError, "diagnostic timeout"):
                AST.run_positive_ast_inventory(cap=FakeCapture(explode), repo=self.repo,
                    case=self.case, tool_home=self.tool, schema=self.schema,
                    compiler_sysroot="/sysroot", deadline_epoch=42, variant="positive",
                    expected_sources=self.source_pins, expected_snapshots=self.snapshot_pins)
            self.assertEqual(dict(os.environ), before)
        saved = json.loads((self.case / AST.RECORD_FILENAME).read_text())
        self.assertEqual(saved["exception"]["type"], "TimeoutError")
        self.assertFalse(saved["source_pins_valid_after"])
        self.assertTrue(saved["snapshots_match_pins_after"])

    def test_wrong_route_provider_variant_and_symlink_ast_are_refused(self):
        def forbidden(*_a, **_k):
            raise AssertionError("stage should be refused")
        common = dict(cap=FakeCapture(forbidden), repo=self.repo, case=self.case,
            tool_home=self.tool, schema=self.schema, compiler_sysroot="/sysroot",
            deadline_epoch=42, expected_sources=self.source_pins,
            expected_snapshots=self.snapshot_pins)
        for env, variant in (({**self.route_env, AST.PHASE_ENV: "wrong"}, "positive"),
                             ({**self.route_env, AST.PROVIDER_ENV: "local"}, "positive"),
                             (self.route_env, "omit-selected-own")):
            with self.assertRaises(RuntimeError):
                AST.run_positive_ast_inventory(**common, env=env, variant=variant)
        outside = self.root / "outside.ast"
        outside.write_text("outside")
        (self.case / AST.AST_FILENAME).symlink_to(outside)
        with patch.dict(os.environ, self.route_env, clear=True), \
             self.assertRaisesRegex(RuntimeError, "AST output already exists"):
            AST.run_positive_ast_inventory(**common, variant="positive")
        self.assertFalse((self.case / AST.RECORD_FILENAME).exists())

    def test_counterfeit_environment_map_is_refused(self):
        stage = MagicMock(side_effect=AssertionError("stage should not run"))
        with patch.dict(os.environ, {**self.route_env, **self.control_env}, clear=True):
            counterfeit = dict(os.environ)
            counterfeit[AST.PHASE_ENV] = "SORT4-ACTUAL-SELECT-2026-10-23-R23"
            with self.assertRaisesRegex(RuntimeError, "must match the live process"):
                AST.run_positive_ast_inventory(cap=FakeCapture(stage), repo=self.repo,
                    case=self.case, tool_home=self.tool, schema=self.schema,
                    compiler_sysroot="/sysroot", deadline_epoch=42, variant="positive",
                    expected_sources=self.source_pins,
                    expected_snapshots=self.snapshot_pins, env=counterfeit)
        stage.assert_not_called()

    def test_bad_preflight_source_pin_skips_stage_and_records_incomplete(self):
        def forbidden(*_a, **_k):
            raise AssertionError("bad preflight must not launch stage")
        bad = dict(self.source_pins, **{"verified/lib.rs": "f" * 64})
        with patch.dict(os.environ, {**self.route_env, **self.control_env}, clear=True):
            record = AST.run_positive_ast_inventory(cap=FakeCapture(forbidden),
                repo=self.repo, case=self.case, tool_home=self.tool, schema=self.schema,
                compiler_sysroot="/sysroot", deadline_epoch=42, variant="positive",
                expected_sources=bad, expected_snapshots=self.snapshot_pins)
        self.assertFalse(record["complete"])
        self.assertEqual(record["status"], "INCOMPLETE")
        self.assertIsNone(record["stage"])
        self.assertTrue(record["snapshots_match_pins_before"])

    def test_symlink_source_target_is_recorded_incomplete_without_stage(self):
        def forbidden(*_a, **_k):
            raise AssertionError("symlink source must not launch stage")
        source = self.case / "verified/lib.rs"
        source.unlink()
        outside = self.root / "outside.rs"
        outside.write_bytes(self.verified)
        source.symlink_to(outside)
        with patch.dict(os.environ, {**self.route_env, **self.control_env}, clear=True):
            record = AST.run_positive_ast_inventory(cap=FakeCapture(forbidden),
                repo=self.repo, case=self.case, tool_home=self.tool, schema=self.schema,
                compiler_sysroot="/sysroot", deadline_epoch=42, variant="positive",
                expected_sources=self.source_pins, expected_snapshots=self.snapshot_pins)
        self.assertFalse(record["complete"])
        self.assertIsNone(record["stage"])
        self.assertIn("invalid", record["source_before"]["verified/lib.rs"])

    def test_callback_default_off_and_negative_preserve_standard_result(self):
        standard = {"status": "RAN", "exit": 1}
        o26 = SimpleNamespace(proof_stage=MagicMock(return_value=standard))
        inventory = SimpleNamespace(run_positive_ast_inventory=MagicMock(
            side_effect=AssertionError("unexpected diagnostic")))
        runtime = {"proof": SimpleNamespace(VARIANTS=("positive", "omit-selected-own")),
                   "o26": o26, "capture": FakeCapture(lambda *_a, **_k: None),
                   "ast_inventory": inventory}
        args = dict(runtime=runtime, repo=self.repo, case=self.case,
            name="r20-merged-optin", tool_home=self.tool, schema=self.schema,
            compiler_sysroot=self.root / "sysroot", deadline_epoch=42,
            expected_sources=self.source_pins, expected_snapshots=self.snapshot_pins)
        with patch.dict(os.environ, {**self.route_env, ENTRY.OPT_IN_KEY: "1"}, clear=True):
            before = dict(os.environ)
            self.assertIs(ENTRY.run_proof_stage(**args, variant="positive",
                                                positive_ast_inventory=False), standard)
            self.assertEqual(dict(os.environ), before)
            self.assertIs(ENTRY.run_proof_stage(**args, variant="omit-selected-own",
                                                positive_ast_inventory=True), standard)
            self.assertEqual(dict(os.environ), before)
        inventory.run_positive_ast_inventory.assert_not_called()
        self.assertEqual(o26.proof_stage.call_count, 2)

    def test_callback_attaches_diagnostic_and_preserves_standard_fields(self):
        standard = {"status": "RAN", "exit": 1, "source_unchanged": True}
        o26 = SimpleNamespace(proof_stage=MagicMock(return_value=standard))
        capture = FakeCapture(self.stage_result(exit_code=1))
        runtime = {"proof": SimpleNamespace(VARIANTS=("positive",)),
                   "o26": o26, "capture": capture, "ast_inventory": AST}
        args = dict(runtime=runtime, repo=self.repo, case=self.case,
            name="r20-merged-optin", tool_home=self.tool, schema=self.schema,
            compiler_sysroot=self.root / "sysroot", deadline_epoch=42,
            variant="positive", positive_ast_inventory=True,
            expected_sources=self.source_pins, expected_snapshots=self.snapshot_pins)
        with patch.dict(os.environ,
             {**self.route_env, ENTRY.OPT_IN_KEY: "1", **self.control_env}, clear=True):
            before = dict(os.environ)
            result = ENTRY.run_proof_stage(**args)
            self.assertEqual(dict(os.environ), before)
        self.assertEqual({key: result[key] for key in standard}, standard)
        self.assertTrue(result["r24_positive_ast_inventory"]["complete"])
        self.assertEqual(result["r24_positive_ast_inventory"]["proof_credit"], 0)
        self.assertEqual(o26.proof_stage.call_count, 1)
        self.assertEqual(capture.LINK.stage.call_count, 1)

    def test_entry_refuses_opt_in_under_wrong_session_before_runtime_load(self):
        loader = MagicMock(side_effect=AssertionError("runtime must not load"))
        args = SimpleNamespace(positive_ast_inventory=True)
        with patch.dict(os.environ,
             {**self.route_env, ENTRY.R24_SESSION_ENV: "wrong"}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "exact R24 Cloud session"):
                ENTRY.run(args, runtime_loader=loader)
        loader.assert_not_called()

    def test_recipe_and_runner_require_explicit_exact_r24_marker(self):
        recipe = json.loads((CLOUD / "recipes/o26-select-callee-r20.json").read_text())
        self.assertIn("research/challenge-8/cloud-build/select-callee-r24-ast-inventory.py",
                      recipe["infra_paths"])
        self.assertEqual(sha((CLOUD / "select-callee-r24-ast-inventory.py").read_bytes()),
                         ENTRY.AST_INVENTORY_SHA256)
        runner = (CLOUD / "run-o26-select-callee-r20.sh").read_text()
        marker = chr(36) + "{SORT4_R24_SESSION_PHASE_ID}"
        opt = chr(36) + "{positive_ast_args[@]}"
        self.assertIn("positive_ast_args=(--positive-ast-inventory --checked-pointer-outcomes)", runner)
        self.assertIn('[[ "' + marker + '" == ' + PHASE + ' ]] || exit 2', runner)
        self.assertIn('"' + opt + '"', runner)

if __name__ == "__main__":
    unittest.main()
