#!/usr/bin/env python3
"""Synthetic hosted-service contract checks for R8 geometry controls."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import re
from types import SimpleNamespace
import sys
import tempfile
import unittest


sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
MODULE_SPEC = importlib.util.spec_from_file_location(
    "r8_geometry_controls", HERE / "r8-geometry-controls.py")
if MODULE_SPEC is None or MODULE_SPEC.loader is None:
    raise RuntimeError("R8 geometry controls module is unavailable")
controls = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(controls)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _erase_ghost(source: bytes) -> bytes:
    text = re.sub(r"/\*@.*?@\*/", "", source.decode(), flags=re.S)
    lines = [line.rstrip() for line in text.splitlines()
             if not line.lstrip().startswith("//@")]
    return ("\n".join(lines) + "\n").encode()


def _callback(case: Path, args, env, *, behavior="normal"):
    manifest = json.loads((case.parent / "manifest.json").read_text())
    name = case.name
    meta = manifest["cases"][name]
    if behavior == "null" and name == "incoming_array":
        return None
    before = {relative: _sha((case / relative).read_bytes())
              for relative in ("original/lib.rs", "verified/lib.rs")}
    stages = dict(meta["expected_stages"])
    affected = {
        "partial": "incoming_array",
        "notrun": "incoming_array",
        "errors": "incoming_array",
        "missing-receipt": "incoming_array",
        "missing-artifact": "incoming_array",
        "wrong-location": "incoming_array",
        "wrong-predicate": "incoming_array",
        "malformed-status": "incoming_array",
        "source-mismatch": "opened_entry_array",
    }.get(behavior)
    if name == affected and behavior == "partial":
        stages.pop("decode")
    if name == affected and behavior == "notrun":
        stages["verifast"] = "NOT_RUN"
    for stage in controls.STAGES:
        if name == affected and behavior == "missing-receipt" and stage == "decode":
            continue
        code = meta["expected_stages"][stage]
        receipt_before = dict(before)
        receipt_after = dict(before)
        if name == affected and behavior == "source-mismatch" and stage == "verifast":
            receipt_after["verified/lib.rs"] = "0" * 64
        receipt = {
            "stage": stage, "exit_code": code, "source_unchanged": True,
            "source_before": receipt_before, "source_after": receipt_after,
        }
        if name == affected and behavior == "malformed-status" and stage == "verifast":
            receipt["status"] = {"unexpected": "object"}
        (case / f"{stage}-stage.json").write_text(json.dumps(receipt))
    target = meta["target"]["line"]
    if meta["expected_class"] == "positive":
        log = (f"verified/lib.rs({target},4): Executing statement span assertion\n"
               "Executing return statement\nLeak check.\n0 errors found\n")
    elif name == affected and behavior == "errors":
        log = (f"verified/lib.rs({target},4): Executing statement span assertion\n"
               f"verified/lib.rs({target},4): error: Cannot prove condition. (synthetic)\n"
               f"verified/lib.rs({target},4): error: second diagnostic\n")
    else:
        error_line = target + 1 if name == affected and behavior == "wrong-location" else target
        message = ("Cannot prove condition. ((uintptr(_address) + 8 <= uintptr(p)) || "
                   "(uintptr(p) + 8 <= uintptr(_address)))")
        if name == affected and behavior == "wrong-predicate":
            message = "Cannot prove condition. (p <= usize::MAX)"
        log = (f"verified/lib.rs({target},4): Executing statement span assertion\n"
               f"verified/lib.rs({error_line},4): error: {message}\n")
    if not (name == affected and behavior in {"missing-artifact", "null"}):
        (case / "verifast.log").write_text(log)
    return {"stages": stages, "source_unchanged_at_every_stage": True}


class R8GeometryControlsServiceTests(unittest.TestCase):
    def _profile(self, root: Path) -> tuple[SimpleNamespace, dict]:
        profile_path = root / "profile.json"
        profile_path.write_text(json.dumps({
            "profile": controls.PROFILE,
            "effective_tool_commit": controls.TOOL_COMMIT,
        }))
        return (SimpleNamespace(profile=controls.PROFILE),
                {"SMALLSORT_MERGE_PROFILE": str(profile_path)})

    def test_sources_encode_three_distinct_entry_geometries_and_false_credit(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            rows = controls.prepare(root / "controls")
            manifest = json.loads((root / "controls/manifest.json").read_text())
            self.assertFalse(manifest["accepted"])
            self.assertFalse(manifest["proof_credit"])
            self.assertEqual(set(rows), {"incoming_cells", "incoming_array", "opened_entry_array"})
            cell = (root / "controls/incoming_cells/verified/lib.rs").read_text()
            array = (root / "controls/incoming_array/verified/lib.rs").read_text()
            opened = (root / "controls/opened_entry_array/verified/lib.rs").read_text()
            self.assertIn("req [1/4](*p |-> ?v);", cell)
            self.assertIn("req [1/4]array::<u64>(p,1,cons(?v,nil));", array)
            self.assertNotIn("//@ open", array)
            self.assertLess(opened.index("//@ open"), opened.index("let mut local"))
            self.assertLess(opened.index("//@ assert"), opened.index("//@ close"))
            for name, row in rows.items():
                source = (root / "controls" / name / "verified/lib.rs").read_bytes()
                original = (root / "controls" / name / "original/lib.rs").read_bytes()
                self.assertEqual(source.count(("TARGET: " + row["target"]["marker"]).encode()), 1)
                self.assertEqual(_erase_ghost(source), original)
                self.assertNotIn(b"/*@", original)
                self.assertNotIn(b"//@", original)
                self.assertFalse(row["accepted"])
                self.assertFalse(row["proof_credit"])
                self.assertEqual(row["expected_stages"]["exporter"], 0)
                self.assertEqual(row["expected_stages"]["decode"], 0)
                self.assertEqual(row["expected_stages"]["refinement"], 0)

    def test_positive_and_exact_target_refusals_classify_with_bound_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            args, env = self._profile(root)
            args.first_fnmut_continue = True
            child_values = []

            def callback(case, child_args, child_env):
                child_values.append(child_args.first_fnmut_continue)
                return _callback(case, child_args, child_env)

            result = controls.run(root / "controls", args, env, callback)
            self.assertEqual(child_values, [False] * len(controls.CASES))
            self.assertTrue(args.first_fnmut_continue)
            self.assertEqual(result["classification"], "DIAGNOSTIC_CONTROLS_CLASSIFIED")
            self.assertEqual(result["profile"], controls.PROFILE)
            self.assertEqual(result["tool_commit"], controls.TOOL_COMMIT)
            self.assertEqual(len(result["profile_sha256"]), 64)
            self.assertFalse(result["accepted"])
            self.assertFalse(result["proof_credit"])
            self.assertEqual(result["cases"]["incoming_cells"], "PASS_CONTROL")
            for name in ("incoming_array", "opened_entry_array"):
                row = result["case_details"][name]
                self.assertEqual(row["classification"], "OBSERVED_GEOMETRY_REFUSAL")
                self.assertTrue(row["target_executed"])
                self.assertTrue(row["last_execution_is_target"])
                self.assertTrue(row["error_at_target"])
                self.assertTrue(row["diagnostic_matches"])
                self.assertFalse(row["accepted"])
                self.assertFalse(row["proof_credit"])

    def test_wrong_location_missing_receipt_null_partial_notrun_errors_and_missing_artifact_fail_closed(self):
        scenarios = ("wrong-location", "wrong-predicate", "malformed-status",
                     "missing-receipt", "null", "partial", "notrun", "errors",
                     "missing-artifact")
        for scenario in scenarios:
            with self.subTest(scenario=scenario), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                args, env = self._profile(root)
                result = controls.run(root / "controls", args, env,
                                      lambda case, a, e: _callback(case, a, e,
                                                                   behavior=scenario))
                row = result["case_details"]["incoming_array"]
                self.assertEqual(row["classification"], "INCONCLUSIVE")
                self.assertFalse(row["accepted"])
                self.assertFalse(row["proof_credit"])
                self.assertEqual(result["classification"], "INCONCLUSIVE")
                if scenario == "malformed-status":
                    details = row["stage_gate"]["stages"]
                    self.assertTrue(details["exporter"]["admitted"])
                    self.assertFalse(details["verifast"]["admitted"])

    def test_source_identity_failure_and_invalid_profile_binding_are_inconclusive(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            args, env = self._profile(root)
            result = controls.run(root / "controls", args, env,
                                  lambda case, a, e: _callback(case, a, e,
                                                               behavior="source-mismatch"))
            self.assertEqual(result["case_details"]["opened_entry_array"]["classification"],
                             "INCONCLUSIVE")
            bad_args = SimpleNamespace(profile="different-profile")
            other = controls.run(root / "bad-profile", bad_args, env, _callback)
            self.assertEqual(other["classification"], "INCONCLUSIVE")
            self.assertFalse(other["accepted"])
            self.assertFalse(other["proof_credit"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
