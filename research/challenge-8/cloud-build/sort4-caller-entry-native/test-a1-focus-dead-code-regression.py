#!/usr/bin/env python3
"""Isolated controls for focus dead-code stage classification and source pins."""
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("a1_tool_focus_test", HERE / "a1-tool.py")
A1 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(A1)


class FocusDeadCodeRegressionTests(unittest.TestCase):
    def stage(self, code, classification="TERMINAL", log_bytes=b"", log_sha=None):
        digest = hashlib.sha256(log_bytes).hexdigest() if log_sha is None else log_sha
        return {"classification": classification, "exit": code,
                "log_sha256": digest}

    def test_three_intended_controls(self):
        expected = "fixture.c(7,"
        dead_log = b"fixture.c(7,5-8): dead code\n"
        selected = A1.classify_focus_dead_code_stage(
            self.stage(1, log_bytes=dead_log), expected, dead_log)
        excluded = A1.classify_focus_dead_code_stage(
            self.stage(0), expected, b"")
        nofocus = A1.classify_focus_dead_code_stage(
            self.stage(1, log_bytes=dead_log), expected, dead_log)
        self.assertEqual(selected["classification"], "EXPECTED_DEAD_CODE_REJECTION")
        self.assertEqual(excluded["classification"], "PASS_NO_IN_SCOPE_DEAD_CODE")
        self.assertEqual(nofocus["classification"], "EXPECTED_DEAD_CODE_REJECTION")
        self.assertFalse(any(row["proof_credit"] for row in
                             (selected, excluded, nofocus)))

    def test_wrong_failure_is_not_intended_negative(self):
        row = A1.classify_focus_dead_code_stage(
            self.stage(1, log_bytes=b"fixture.c(2,1-3): assertion failed\n"),
            "fixture.c(7,", b"fixture.c(2,1-3): assertion failed\n")
        self.assertEqual(row["classification"],
                         "INCONCLUSIVE_WRONG_PREDICATE_OR_EXIT")

    def test_wrong_line_and_timeout_with_dead_code_are_inconclusive(self):
        wrong_line = b"fixture.c(8,5-8): dead code\n"
        row = A1.classify_focus_dead_code_stage(
            self.stage(1, log_bytes=wrong_line), "fixture.c(7,", wrong_line)
        self.assertEqual(row["classification"],
                         "INCONCLUSIVE_WRONG_PREDICATE_OR_EXIT")
        timeout_log = b"fixture.c(7,5-8): dead code\n"
        timeout = A1.classify_focus_dead_code_stage(
            self.stage(124, log_bytes=timeout_log), "fixture.c(7,", timeout_log)
        self.assertEqual(timeout["classification"],
                         "INCONCLUSIVE_WRONG_PREDICATE_OR_EXIT")
        excluded_dead = b"fixture.c(8,5-8): dead code\n"
        positive = A1.classify_focus_dead_code_stage(
            self.stage(0, log_bytes=excluded_dead), "fixture.c(7,", excluded_dead)
        self.assertEqual(positive["classification"],
                         "INCONCLUSIVE_WRONG_PREDICATE_OR_EXIT")

    def test_error_not_run_and_partial_stages_do_not_pass(self):
        cases = [
            (self.stage(1, "ERROR", b"fixture.c(7,5): dead code\n"),
             b"fixture.c(7,5): dead code\n"),
            (self.stage(None, "NOT_RUN"), None),
            ({"classification": "TERMINAL", "log_sha256": "a" * 64}, b""),
            ({"classification": "TERMINAL", "exit": None,
              "log_sha256": "a" * 64}, b""),
            ({"classification": "TERMINAL", "exit": True,
              "log_sha256": "a" * 64}, b""),
            (self.stage(0, log_sha=None), None),
            (None, b""),
        ]
        for stage, log in cases:
            with self.subTest(stage=stage, log=log):
                row = A1.classify_focus_dead_code_stage(stage, "fixture.c(", log)
                self.assertNotIn("PASS", row["classification"])
                self.assertNotIn("dead_code_diagnostics", row)

    def test_mismatched_log_sha_is_inconclusive(self):
        data = b"fixture.c(7,5-8): dead code\n"
        row = A1.classify_focus_dead_code_stage(
            self.stage(1, log_sha="0" * 64), "fixture.c(7,", data)
        self.assertEqual(row["classification"], "INCONCLUSIVE_LOG_IDENTITY_MISMATCH")
        self.assertNotIn("dead_code_diagnostics", row)

    def test_static_patch_and_core_pin_transition(self):
        manifest_path = HERE.parent / "sort4-native-c1-bound" / \
            "NATIVE-RUST-FOCUS-DEAD-CODE-SCOPE-MANIFEST.json"
        patch_path = HERE.parent / "sort4-native-c1-bound" / \
            "native-rust-focus-dead-code-scope.patch"
        diagnostic_manifest_path = HERE.parent / "sort4-native-c1-bound" / \
            "NATIVE-DEAD-CODE-IDENTITY-DIAGNOSTIC-MANIFEST.json"
        diagnostic_patch_path = HERE.parent / "sort4-native-c1-bound" / \
            "native-dead-code-identity-diagnostic.patch"
        profile_path = HERE / "A1-POST-MIGRATION-R8-PROFILE-2026-10-20.json"
        manifest = json.loads(manifest_path.read_text())
        diagnostic = json.loads(diagnostic_manifest_path.read_text())
        profile = json.loads(profile_path.read_text())
        self.assertEqual(hashlib.sha256(diagnostic_patch_path.read_bytes()).hexdigest(),
                         diagnostic["patch_sha256"])
        self.assertEqual(diagnostic["files"]["src/verify_expr.ml"]["base_sha256"],
                         "f2a2a32c990219392cff3b1dbc13992567cf9cdc37d29ae3214e4353d81f8150")
        self.assertEqual(diagnostic["files"]["src/verify_expr.ml"]["result_sha256"],
                         manifest["files"]["src/verify_expr.ml"]["base_sha256"])
        self.assertEqual(hashlib.sha256(patch_path.read_bytes()).hexdigest(),
                         manifest["patch_sha256"])
        self.assertEqual(manifest["files"]["src/verify_expr.ml"]["base_sha256"],
                         "c2246e54f06fe099b5ddb6ba500aba4f6186498b1a44cb8a51b3389b18fe8ca9")
        self.assertEqual(manifest["files"]["src/verify_expr.ml"]["result_sha256"],
                         "2d17c36005d6727cb5ff6d831bf905f513065bb591d5d9768ee70778872a6d20")
        self.assertEqual(manifest["kernel_sha256"], diagnostic["kernel_sha256"])
        self.assertEqual(profile["focus_dead_code_scope_manifest_sha256"],
                         hashlib.sha256(manifest_path.read_bytes()).hexdigest())
        self.assertEqual(profile["focus_dead_code_scope_patch_sha256"],
                         manifest["patch_sha256"])
        self.assertEqual(profile["a1_focus_semantics_sha256"]["src/verify_expr.ml"],
                         manifest["files"]["src/verify_expr.ml"]["result_sha256"])
        self.assertEqual(profile["a1_helper_sha256"]["a1-tool.py"],
                         hashlib.sha256((HERE / "a1-tool.py").read_bytes()).hexdigest())
        self.assertEqual(profile["a1_source_runner_sha256"],
                         hashlib.sha256((HERE / "a1-runner.py").read_bytes()).hexdigest())
        runner = (HERE / "a1-runner.py").read_text()
        self.assertIn('"src/verify_expr.ml": "2d17c36005d6727cb5ff6d831bf905f513065bb591d5d9768ee70778872a6d20"',
                      runner)
        self.assertIn('"src/verifast.ml": "37ed2550d276abccbbe0a9ced678137ef587f80782bcff763062df394c2a440c"',
                      runner)
        tool = (HERE / "a1-tool.py").read_text()
        self.assertIn('apply("a1-rust-focus-dead-code-scope", FOCUS_SCOPE_PATCH,', tool)
        self.assertNotIn('chain.append(apply("a1-rust-focus-dead-code-scope"', tool)
        self.assertLess(tool.index("driver.compare_source_snapshot(pre_slice"),
                        tool.index('apply("a1-rust-focus-dead-code-scope"'))


if __name__ == "__main__":
    unittest.main()
