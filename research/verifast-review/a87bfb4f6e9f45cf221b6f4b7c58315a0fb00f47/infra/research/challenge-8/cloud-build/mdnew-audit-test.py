#!/usr/bin/env python3
"""Small parser/classifier controls; no compiler, verifier, or source extractor."""
from __future__ import annotations

import importlib.util
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

MODULE = Path(__file__).with_name("mdnew-audit.py")
spec = importlib.util.spec_from_file_location("mdnew_audit", MODULE)
assert spec and spec.loader
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class ClassifierControls(unittest.TestCase):
    def test_first_diagnostic_cannot_be_hidden_by_later_expected_error(self):
        log = ("forget.rs(2,1): error: earlier frontend failure\n"
               "forget.rs(3,9): error: Cannot prove condition. (Cannot prove false.)\n")
        self.assertEqual(m.first_diagnostic(log)[1],
                         "forget.rs(2,1): error: earlier frontend failure")
        self.assertFalse(m.target_location(m.first_diagnostic(log)[1], "forget", 3))

    def test_exact_annotated_location(self):
        msg = "shared_false_unwind.rs(14,19-24): error: Cannot prove condition. (Cannot prove false.)"
        self.assertTrue(m.target_location(msg, "shared_false_unwind", 14))
        self.assertFalse(m.target_location(msg, "shared_false_unwind", 15))
        self.assertFalse(m.target_location(msg, "false_normal_post", 14))

    def test_mir_call_edges_are_scoped_to_named_body(self):
        mir = '''  bodies = [
    (
      defPath = "new",
      basicBlocks = [
        ( id = (index = 0),
          terminator = (kind = (call = (func = (constant = (val = (fnDef = (id = (name = "wrong"))))),
            unwindAction = (continue = void), target = (something = (index = 1))))), isCleanup = false ) ] ),
    (
      defPath = "shared_cleanup",
      basicBlocks = [
        ( id = (index = 0),
          terminator = (kind = (call = (func = (constant = (val = (fnDef = (id = (name = "std::mem::ManuallyDrop::<T>::new"))))),
            args = [( move = (local = (name = "_4")))], unwindAction = (cleanup = (index = 3)),
            target = (something = (index = 1))))), isCleanup = false ),
        ( id = (index = 1),
          terminator = (kind = (call = (func = (constant = (val = (fnDef = (id = (name = "new"))))),
            unwindAction = (cleanup = (index = 3)), target = (something = (index = 2))))), isCleanup = false ),
        ( id = (index = 2), terminator = (kind = (return = void)), isCleanup = false ),
        ( id = (index = 3), terminator = (kind = (unwindResume = void)), isCleanup = true ) ] ) ]
'''
        body = m.mir_body(mir, "shared_cleanup")
        self.assertEqual(m.call_edge(body, "std::mem::ManuallyDrop::<T>::new"), (3, 1))
        self.assertEqual(m.call_edge(body, "new"), (3, 2))
        with self.assertRaises(m.AuditIssue):
            m.call_edge(m.mir_body(mir, "new"), "new")

    def test_ast_function_scope_excludes_callee_marker(self):
        ast = '''    Func (loc "x.rs(1,1-2)", Regular, "new", false, Some (([
      ReturnStmt (loc "x.rs(2,1)", Some (CallExpr (loc "x.rs(2,1)", "unwinding", [], [], [], Static)))
    ], loc "x.rs(2,1)")), false, []);
    Func (loc "x.rs(4,1-5)", Regular, "shared_cleanup", false, Some (([
      ReturnStmt (loc "x.rs(5,1)", Some (CallExpr (loc "x.rs(5,1)", "returning", [], [], [], Static)))
    ], loc "x.rs(5,1)")), false, [])
'''
        self.assertIn('"unwinding"', m.ast_body(ast, "new"))
        self.assertNotIn('"unwinding"', m.ast_body(ast, "shared_cleanup"))

    def test_missing_evidence_is_inconclusive(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(m.AuditIssue) as ctx:
                m.audit(Path(temp))
            self.assertEqual(ctx.exception.classification, "INCONCLUSIVE")

    def test_negative_diagnostic_copy_only_removes_marker(self):
        original = (b"pub unsafe fn forget_false_normal_post<T>(t: T)\n"
                    b"//@ req thread_token(?tid) &*& tid == currentThread;\n"
                    b"//@ ens false; //~should_fail\n"
                    b"//@ on_unwind_ens false;\n"
                    b"{\n    let _ = std::mem::ManuallyDrop::new(t);\n}\n")
        self.assertEqual(hashlib.sha256(original).hexdigest(), m.FIXTURES["false_normal_post"][0])
        derived = original.replace(b" //~should_fail", b"", 1)
        sha = hashlib.sha256(derived).hexdigest()
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp) / "candidate/false_normal_post"
            folder.mkdir(parents=True)
            (folder / "source.rs").write_bytes(original)
            (folder / "diagnostic-source.rs").write_bytes(derived)
            (folder / "diagnostic-source-sha256.txt").write_text(sha + "\n")
            (folder / "fixture.json").write_text(json.dumps({
                "diagnostic_source_sha256": sha, "diagnostic_source_path": "diagnostic-source.rs",
                "diagnostic_line_count_preserved": True, "should_fail_marker_count_removed": 1}))
            (folder / "diagnostic-source.json").write_text(json.dumps({
                "original_sha256": m.FIXTURES["false_normal_post"][0],
                "diagnostic_sha256": sha, "marker_count_removed": 1,
                "line_count_preserved": True}))
            m.verify_diagnostic_derivative(Path(temp), "candidate", "false_normal_post")
            (folder / "diagnostic-source.rs").write_bytes(derived.replace(b"ens false", b"ens true"))
            with self.assertRaises(m.AuditIssue):
                m.verify_diagnostic_derivative(Path(temp), "candidate", "false_normal_post")

    def test_failed_or_tampered_capture_cannot_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp) / "captures/forget"
            folder.mkdir(parents=True)
            files = {"normal-export": "normal-mir.bin", "normal-decode": "normal-mir.txt",
                     "readonly-export": "readonly-mir.bin", "readonly-decode": "readonly-mir.txt",
                     "refinement": "refinement.log"}
            stages = {}
            for name, filename in files.items():
                data = (name + "-data").encode()
                (folder / filename).write_bytes(data)
                stages[name] = {"exit_status": 0, "output_sha256": hashlib.sha256(data).hexdigest()}
            ast = b"ast-data"
            (folder / "verified-ast.txt").write_bytes(ast)
            record = {"schema": "verifast-mdnew-capture-v1", "case": "forget",
                      "side": "candidate", "tool_source_sha": m.CANDIDATE,
                      "source_sha256": m.FIXTURES["forget"][0],
                      "infra_sha": "a" * 40, "proof_sha": "a" * 40,
                      "stages": stages,
                      "verified_ast_sha256": hashlib.sha256(ast).hexdigest()}
            status = folder / "capture-status.json"
            status.write_text(json.dumps(record))
            provenance = {"infra_sha": "a" * 40, "proof_sha": "a" * 40}
            m.verify_capture_status(Path(temp), "forget", "candidate", provenance)
            stages["refinement"]["exit_status"] = 1
            status.write_text(json.dumps(record))
            with self.assertRaises(m.AuditIssue):
                m.verify_capture_status(Path(temp), "forget", "candidate", provenance)
            stages["refinement"]["exit_status"] = 0
            status.write_text(json.dumps(record))
            (folder / "normal-mir.txt").write_text("tampered")
            with self.assertRaises(m.AuditIssue):
                m.verify_capture_status(Path(temp), "forget", "candidate", provenance)


if __name__ == "__main__":
    unittest.main()
