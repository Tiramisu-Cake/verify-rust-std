"""Synthetic controls for the bounded P-dispatch diagnostic receipt."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).parent
SPEC = importlib.util.spec_from_file_location("a1_dispatch_diagnostic_test", HERE / "a1-runner.py")
m = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = m
SPEC.loader.exec_module(m)


def inputs(root, classification="ORIGINAL_COMMON_TRAIT_DISPATCH_OBSERVED"):
    raw = {
        "case_id": "P-dispatch", "build_id": "build-test",
        "profile_sha256": "not-read-from-raw",
        "source_id": "source-test", "unit_id": "unit-test",
        "source_pair_sha256": {"verified": "a" * 64, "original": "b" * 64},
        "paired_support": {"paired_support_passed": True},
        "evidence_root": str(root),
        "stages": {"verification": {"exit": 0, "log_sha256": "c" * 64}},
        "artifacts": {"proof-ast.ml": {"sha256": "d" * 64,
                                       "path": "/excluded/full/ast/path"}},
        "normal-mir.txt": "must not be copied", "verification_log": "must not be copied"}
    classifier = {"classification": classification, "source_sha256": "a" * 64,
                  "trace_lines": [{"owner": "quicksort", "callee": "threshold"}],
                  "proof_credit": False}
    return raw, classifier


class DispatchDiagnostic(unittest.TestCase):
    def test_persists_small_identity_and_result_without_mir_or_log_copy(self):
        with tempfile.TemporaryDirectory() as tmp:
            raw, classifier = inputs(Path(tmp))
            result = m.persist_dispatch_join_diagnostic(raw, classifier,
                                                        profile_sha256="e" * 64)
            self.assertEqual(result["classification"], classifier["classification"])
            self.assertTrue(result["diagnostic_artifact"]["persisted"])
            saved = json.loads((Path(tmp) / "dispatch-join-observation.json").read_text())
            self.assertEqual(saved["build_id"], "build-test")
            self.assertEqual(saved["profile_sha256"], "e" * 64)
            self.assertEqual(saved["source_pair_sha256"], raw["source_pair_sha256"])
            self.assertEqual(saved["verification"]["log_sha256"], "c" * 64)
            self.assertEqual(saved["proof_ast_sha256"], "d" * 64)
            self.assertFalse(saved["proof_credit"])
            self.assertFalse(saved["matrix_admission"])
            self.assertFalse(saved["caller_receipt"])
            self.assertNotIn("normal-mir.txt", saved)
            self.assertNotIn("verification_log", saved)
            self.assertNotIn("/excluded/full/ast/path", json.dumps(saved))

    def test_io_failure_preserves_observation_but_forces_inconclusive(self):
        with tempfile.TemporaryDirectory() as tmp:
            raw, classifier = inputs(Path(tmp))
            def fail_write(_path, _content):
                raise OSError("synthetic filesystem failure")
            result = m.persist_dispatch_join_diagnostic(
                raw, classifier, profile_sha256="e" * 64, writer=fail_write)
            self.assertEqual(result["classification"], "INCONCLUSIVE_DISPATCH_OBSERVATION")
            self.assertEqual(result["observed_classification"], classifier["classification"])
            self.assertEqual(result["diagnostic_artifact"]["error_type"], "OSError")
            self.assertFalse(result["proof_credit"])

    def test_path_resolution_failure_preserves_observation_as_inconclusive(self):
        with tempfile.TemporaryDirectory() as tmp:
            raw, classifier = inputs(Path(tmp))
            with patch.object(Path, "resolve", side_effect=OSError("synthetic resolve failure")):
                result = m.persist_dispatch_join_diagnostic(
                    raw, classifier, profile_sha256="e" * 64)
            self.assertEqual(result["classification"], "INCONCLUSIVE_DISPATCH_OBSERVATION")
            self.assertEqual(result["observed_classification"], classifier["classification"])
            self.assertEqual(result["diagnostic_artifact"]["error_type"], "OSError")

    def test_existing_symlink_is_refused_without_changing_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "verification.log"
            target.write_text("keep this exact content")
            artifact = root / "dispatch-join-observation.json"
            artifact.symlink_to(target.name)
            raw, classifier = inputs(root)
            result = m.persist_dispatch_join_diagnostic(
                raw, classifier, profile_sha256="e" * 64)
            self.assertEqual(result["classification"], "INCONCLUSIVE_DISPATCH_OBSERVATION")
            self.assertEqual(result["diagnostic_artifact"]["error_type"], "OSError")
            self.assertTrue(artifact.is_symlink())
            self.assertEqual(target.read_text(), "keep this exact content")

    def test_preexisting_inconclusive_status_stays_nonaccepting(self):
        with tempfile.TemporaryDirectory() as tmp:
            raw, classifier = inputs(Path(tmp), "INCONCLUSIVE_DISPATCH_OBSERVATION")
            result = m.persist_dispatch_join_diagnostic(raw, classifier,
                                                        profile_sha256="e" * 64)
            self.assertEqual(result["classification"], "INCONCLUSIVE_DISPATCH_OBSERVATION")
            self.assertTrue(result["diagnostic_artifact"]["persisted"])
            saved = json.loads((Path(tmp) / "dispatch-join-observation.json").read_text())
            self.assertEqual(saved["dispatch_classifier"]["classification"],
                             "INCONCLUSIVE_DISPATCH_OBSERVATION")
            self.assertFalse(saved["proof_credit"])


if __name__ == "__main__":
    unittest.main()
