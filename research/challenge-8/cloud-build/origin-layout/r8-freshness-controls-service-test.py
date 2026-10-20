#!/usr/bin/env python3
"""Synthetic service checks for the R8 owned-array freshness controls."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest
from types import SimpleNamespace


sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
MODULE_SPEC = importlib.util.spec_from_file_location(
    "r8_freshness_controls", HERE / "r8-freshness-controls.py")
if MODULE_SPEC is None or MODULE_SPEC.loader is None:
    raise RuntimeError("R8 freshness controls module is unavailable")
controls = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(controls)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _erase_ghost(source: bytes) -> bytes:
    text = re.sub(r"/\*@.*?@\*/", "", source.decode(), flags=re.S)
    lines = [line.rstrip() for line in text.splitlines()
             if not line.lstrip().startswith("//@")]
    return ("\n".join(lines) + "\n").encode()


def _receipt(case: Path, meta: dict, stage: str, code: int, *, status=None) -> None:
    pair = {relative: _sha((case / relative).read_bytes())
            for relative in ("original/lib.rs", "verified/lib.rs")}
    receipt = {"stage": stage, "exit_code": code, "source_unchanged": True,
               "source_before": pair, "source_after": pair}
    if status is not None:
        receipt["status"] = status
    (case / f"{stage}-stage.json").write_text(json.dumps(receipt))


def _executor(case: Path, args, env: dict, *, behavior="normal"):
    if behavior == "raise" and case.name == "wrong_entry_count":
        raise RuntimeError("synthetic hosted stage exception")
    if behavior == "null" and case.name == "wrong_entry_count":
        return None
    manifest = json.loads((case.parent / "manifest.json").read_text())
    meta = manifest["cases"][case.name]
    if behavior == "wrong-literal" and case.name == "wholearray3":
        source = case / "verified/lib.rs"
        source.write_bytes(source.read_bytes().replace(b"+ 8 <= (p + 1)", b"+ 9 <= (p + 1)", 1))
    if behavior == "wrong-shape" and case.name == "wrong_entry_count":
        source = case / "verified/lib.rs"
        source.write_bytes(source.read_bytes().replace(b"(p,2,?xs)", b"(p,3,?xs)", 1))
    if behavior == "source-mismatch" and case.name == "wrong_entry_count":
        source = case / "verified/lib.rs"
        source.write_bytes(source.read_bytes() + b"// changed after preparation\n")
    if behavior == "flag-mismatch" and case.name == "currentprefix2":
        flag_receipt = not meta["expected_flag"]
    else:
        flag_receipt = args.r8_owned_array_allocation
    stages = dict(meta["expected_stages"])
    if case.name == "wrong_entry_count" and behavior == "partial":
        stages.pop("decode")
    if case.name == "wrong_entry_count" and behavior == "notrun":
        stages["verifast"] = "NOT_RUN"
    if case.name == "wrong_entry_count" and behavior == "wrong-refusal-stage":
        stages["verifast"] = 2
    for stage in controls.STAGES:
        if case.name == "wrong_entry_count" and behavior == "missing-receipt" and stage == "decode":
            continue
        status = {"bad": "type"} if (
            case.name == "wrong_entry_count" and behavior == "malformed-status" and
            stage == "verifast") else "SUCCESS"
        code = (2 if stage == "verifast" and case.name == "wrong_entry_count" and
                behavior == "wrong-refusal-stage" else meta["expected_stages"][stage])
        _receipt(case, meta, stage, code, status=status)
    if meta["expected_class"] == "positive":
        target = meta["target"]["line"]
        log = (f"verified/lib.rs({target},4): Executing statement span assertion\n"
               "Executing return statement\nLeak check.\n0 errors found\n")
    else:
        target = meta["target"]["line"]
        if meta["expected_class"] == "missing_owner_refusal":
            diagnostic = "No matching heap chunks: [_]points_to<u64>(p, _)"
        else:
            if case.name == "wrong_root":
                right_side = "get_pointer_address(q)"
            else:
                element_type = ("int64_t_typeid" if case.name == "wrong_element"
                                else "uint64_t_typeid")
                right_side = f"get_pointer_address(ptr_add_(p, 1, {element_type}))"
            diagnostic = ("Assertion might not hold. (Cannot prove "
                          "(get_pointer_address(local_addr) + 8) <= "
                          f"{right_side} || "
                          f"({right_side} + 8) <= "
                          "get_pointer_address(local_addr).)")
        log = (f"verified/lib.rs({target},4): Executing statement intended target\n"
               f"verified/lib.rs({target},4): error: {diagnostic}\n")
    if behavior == "wrong-location" and case.name == "wrong_entry_count":
        log = log.replace(f"verified/lib.rs({target},4): error:",
                          f"verified/lib.rs({target + 1},4): error:")
    if behavior == "wrong-predicate" and case.name == "wrong_entry_count":
        log = log.replace(" || ", " && ", 1)
    if behavior == "multiple-errors" and case.name == "wrong_entry_count":
        log += f"verified/lib.rs({target},4): error: second diagnostic\n"
    if behavior == "missing-artifact" and case.name == "wrong_entry_count":
        pass
    else:
        (case / "verifast.log").write_text(log)
    result = {"stages": stages, "source_unchanged_at_every_stage": True,
              "r8_owned_array_allocation": flag_receipt}
    if behavior == "service-error" and case.name == "wrong_entry_count":
        result["error"] = "hosted service failed after a partial run"
    return result


class R8FreshnessControlsServiceTests(unittest.TestCase):
    def _binding(self, root: Path):
        profile_path = root / "experimental-profile.json"
        profile_path.write_text(json.dumps({
            "schema": "smallsort-tracked-md-profile-v2",
            "profile": controls.PROFILE,
            "accepted": False,
            "effective_tool_commit": "a" * 40,
        }))
        return (SimpleNamespace(profile=controls.PROFILE),
                {"SMALLSORT_MERGE_PROFILE": str(profile_path)})

    def test_source_shapes_contracts_posts_and_ghost_free_originals(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            rows = controls.prepare(root / "controls")
            manifest = json.loads((root / "controls/manifest.json").read_text())
            self.assertFalse(manifest["accepted"])
            self.assertFalse(manifest["proof_credit"])
            self.assertEqual(len(rows), 8)
            for name, meta in rows.items():
                original = (root / "controls" / name / "original/lib.rs").read_bytes()
                verified = (root / "controls" / name / "verified/lib.rs").read_bytes()
                self.assertEqual(_erase_ghost(verified), original)
                self.assertNotIn(b"/*@", original)
                self.assertNotIn(b"//@", original)
                self.assertEqual(verified.count(("TARGET: " + meta["target"]["marker"]).encode()), 1)
                self.assertIn(b"let mut local = 19u64;", verified)
                self.assertIn(b"let _address = &mut local as *mut u64;", verified)
                self.assertNotIn(b"&raw mut local", verified)
                self.assertIn(b"on_unwind_ens", verified)
                clauses = re.findall(rb"/\*@\s*(.*?)\s*@\*/", verified, re.S)
                self.assertEqual(len(clauses), 3)
                self.assertTrue(clauses[0].startswith(b"req "))
                self.assertTrue(clauses[1].startswith(b"ens "))
                self.assertTrue(clauses[2].startswith(b"on_unwind_ens "))
            whole = (root / "controls/wholearray3/verified/lib.rs").read_bytes()
            default_off = (root / "controls/default_off/verified/lib.rs").read_bytes()
            self.assertEqual(whole, default_off)
            self.assertIn(b"req [1/4]array::<u64>(p,3,?xs);", whole)
            prefix = (root / "controls/currentprefix2/verified/lib.rs").read_bytes()
            self.assertLess(prefix.index(b"array_split::<u64>(p, 2)"),
                            prefix.index(b"let mut local"))
            self.assertLess(prefix.index(b"TARGET: current prefix2"),
                            prefix.index(b"array_join::<u64>(p)"))
            opened = (root / "controls/missing_current_owner/verified/lib.rs").read_bytes()
            self.assertEqual(opened.count(b"//@ open [1/4]array::<u64>"), 3)
            self.assertEqual(opened.count(b"//@ close [1/4]array::<u64>"), 3)
            self.assertLess(opened.index(b"open [1/4]array::<u64>(p + 2"),
                            opened.index(b"let mut local"))
            self.assertGreater(opened.index(b"close [1/4]array::<u64>(p, 3"),
                                opened.index(b"TARGET:"))
            wrong_root = (root / "controls/wrong_root/verified/lib.rs").read_bytes()
            self.assertIn(b"array::<u64>(q,1,?ys)", wrong_root)
            self.assertIn(b"(q as usize) + 8", wrong_root)
            wrong_root_clauses = re.findall(rb"/\*@\s*(.*?)\s*@\*/", wrong_root, re.S)
            self.assertEqual(len(wrong_root_clauses), 3)
            for clause in wrong_root_clauses:
                self.assertIn(b"array::<u64>(p,3", clause)
                self.assertIn(b"array::<u64>(q,1", clause)
                self.assertIn(b"&*&", clause)
            missing = (root / "controls/numeric_same_address_no_owner/verified/lib.rs").read_bytes()
            self.assertIn(b"p as usize == _address as usize", missing)
            self.assertIn(b"assert *p |-> _", missing)
            self.assertEqual(rows["default_off"]["expected_flag"], False)
            for name in controls.CASES:
                self.assertFalse(rows[name]["accepted"])
                self.assertFalse(rows[name]["proof_credit"])

    def test_all_positive_and_intended_negative_controls_classify(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            args, env = self._binding(root)
            args.first_fnmut_continue = True
            child_values = []

            def executor(case, child_args, child_env):
                child_values.append(child_args.first_fnmut_continue)
                return _executor(case, child_args, child_env)

            result = controls.run(root / "controls", args, env, executor)
            self.assertEqual(child_values, [False] * len(controls.CASES))
            self.assertTrue(args.first_fnmut_continue)
            self.assertEqual(result["classification"], "DIAGNOSTIC_CONTROLS_CLASSIFIED")
            self.assertEqual(result["profile"], controls.PROFILE)
            self.assertEqual(result["profile_schema"], "smallsort-tracked-md-profile-v2")
            self.assertFalse(result["profile_accepted"])
            self.assertEqual(result["effective_tool_commit"], "a" * 40)
            self.assertFalse(result["accepted"])
            self.assertFalse(result["proof_credit"])
            manifest = json.loads((root / "controls/manifest.json").read_text())
            self.assertEqual(manifest["profile_schema"], "smallsort-tracked-md-profile-v2")
            self.assertFalse(manifest["profile_accepted"])
            self.assertEqual(manifest["effective_tool_commit"], "a" * 40)
            for name in ("wholearray3", "currentprefix2"):
                self.assertEqual(result["cases"][name], "PASS_CONTROL")
            for name in ("default_off", "wrong_entry_count", "wrong_element",
                         "missing_current_owner", "wrong_root",
                         "numeric_same_address_no_owner"):
                row = result["case_details"][name]
                self.assertEqual(row["classification"], "EXPECTED_REJECTION_DIAGNOSTIC")
                self.assertTrue(row["flag_receipt_matches"])
                self.assertEqual(row["source_binding"]["profile"], controls.PROFILE)
                self.assertTrue(row["target_executed"])
                self.assertTrue(row["last_execution_is_target"])
                self.assertTrue(row["error_at_target"])
                self.assertTrue(row["diagnostic_matches"])
                self.assertFalse(row["accepted"])
                self.assertFalse(row["proof_credit"])
            self.assertEqual(controls._expected_error("default_off")["contains"],
                             "Assertion might not hold.")
            self.assertFalse(result["case_details"]["default_off"]["expected_flag"])

    def test_tampered_source_wrong_predicate_location_and_flag_receipt_are_inconclusive(self):
        for behavior, case_name in (("wrong-literal", "wholearray3"),
                                    ("wrong-shape", "wrong_entry_count"),
                                    ("source-mismatch", "wrong_entry_count"),
                                    ("wrong-predicate", "wrong_entry_count"),
                                    ("wrong-refusal-stage", "wrong_entry_count"),
                                    ("wrong-location", "wrong_entry_count"),
                                    ("flag-mismatch", "currentprefix2")):
            with self.subTest(behavior=behavior), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                args, env = self._binding(root)
                result = controls.run(root / "controls", args, env,
                                      lambda case, a, e: _executor(case, a, e,
                                                                   behavior=behavior))
                self.assertEqual(result["case_details"][case_name]["classification"],
                                 "INCONCLUSIVE")
                self.assertFalse(result["accepted"])
                self.assertFalse(result["proof_credit"])

    def test_partial_notrun_errors_null_missing_receipt_and_artifact_are_inconclusive(self):
        scenarios = ("raise", "null", "partial", "notrun", "multiple-errors",
                     "service-error", "missing-receipt", "missing-artifact",
                     "malformed-status")
        for behavior in scenarios:
            with self.subTest(behavior=behavior), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                args, env = self._binding(root)
                result = controls.run(root / "controls", args, env,
                                      lambda case, a, e: _executor(case, a, e,
                                                                   behavior=behavior))
                row = result["case_details"]["wrong_entry_count"]
                self.assertEqual(row["classification"], "INCONCLUSIVE")
                self.assertFalse(row["accepted"])
                self.assertFalse(row["proof_credit"])
                if behavior == "malformed-status":
                    self.assertTrue(row["stage_gate"]["stages"]["exporter"]["admitted"])
                    self.assertFalse(row["stage_gate"]["stages"]["verifast"]["admitted"])

    def test_wrong_profile_schema_acceptance_or_tool_binding_fails_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            args, env = self._binding(root)
            for field, value in (("profile", "other"), ("schema", None),
                                 ("accepted", True), ("effective_tool_commit", "bad")):
                with self.subTest(field=field):
                    profile_path = Path(env["SMALLSORT_MERGE_PROFILE"])
                    profile = json.loads(profile_path.read_text())
                    profile[field] = value
                    profile_path.write_text(json.dumps(profile))
                    output = controls.run(root / f"bad-{field}", args, env, _executor)
                    self.assertEqual(output["classification"], "INCONCLUSIVE")
                    self.assertFalse(output["accepted"])
                    self.assertFalse(output["proof_credit"])
                    profile[field] = {"profile": controls.PROFILE,
                                      "schema": "smallsort-tracked-md-profile-v2",
                                      "accepted": False,
                                      "effective_tool_commit": "a" * 40}[field]
                    profile_path.write_text(json.dumps(profile))


if __name__ == "__main__":
    unittest.main(verbosity=2)
