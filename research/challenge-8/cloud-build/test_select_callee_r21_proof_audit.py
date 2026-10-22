"""Synthetic failure-preservation checks; no proof tools are executed."""
import argparse
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location('r21_proof_audit',
    Path(__file__).with_name('select-callee-r21-proof-audit.py'))
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class AuditTests(unittest.TestCase):
    def test_missing_malformed_partial_and_not_run_stay_incomplete(self):
        cases = [None, 'null', '[]', '{', '{}',
                 '{"complete":false,"rows":{"positive":{"status":"NOT_RUN"}}}']
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / 'cases/r21-fractional-proof/r21-fractional-proof.json'
            path.parent.mkdir(parents=True)
            args = argparse.Namespace(evidence=root, output=root/'audit.json',
                                      runner_exit=124, failed_stage='exact-stage')
            def base(a):
                return {'schema': 'base', 'evidence_complete': True,
                        'runner_exit': a.runner_exit, 'failed_stage': a.failed_stage}
            for raw in cases:
                with self.subTest(raw=raw):
                    if raw is None:
                        path.unlink(missing_ok=True)
                    else:
                        path.write_text(raw)
                    result = MODULE.audit(args, base_audit=base)
                    self.assertIs(result['evidence_complete'], False)
                    self.assertEqual(result['runner_exit'], 124)
                    self.assertEqual(result['failed_stage'], 'exact-stage')
                    self.assertIs(result['accepted'], False)
                    self.assertIs(result['proof_credit'], False)

    def test_complete_matrix_preserves_rows_and_base_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / 'cases/r21-fractional-proof/r21-fractional-proof.json'
            path.parent.mkdir(parents=True)
            proof = {'schema': 'r21-fractional-classified-proof-v1',
                     'complete': True, 'accepted': False, 'proof_credit': False,
                     'body_proof_run': True, 'variant_order': list(MODULE.VARIANTS),
                     'rows': {'positive': {'stage': {'status': 'RAN', 'exit': 0}}}}
            path.write_text(json.dumps(proof))
            args = argparse.Namespace(evidence=root, output=root/'audit.json')
            for complete in (False, True):
                result = MODULE.audit(args, base_audit=lambda _: {
                    'schema': 'base', 'evidence_complete': complete})
                self.assertIs(result['evidence_complete'], False)
                self.assertEqual(result['fractional_proof'], proof)
                self.assertIs(result['verification_accepted'], False)
            for variant in MODULE.VARIANTS:
                proof['rows'][variant] = {
                    'status': 'COMPLETE', 'source_intact_after_stages': True,
                    'normal_unwind_nested_drop_gates': True,
                    'stage': {'status': 'RAN', 'exit': 0 if variant == 'positive' else 1,
                              'intrinsic_gate_active': True, 'pointer_drop_gate_active': True,
                              'source_unchanged': True},
                    'preflight_capture_check': {'complete': True},
                    'postflight_capture_check': {'complete': True},
                    'classification': ('POSITIVE_VERIFIED_SOURCE_REPORTED'
                        if variant == 'positive' else
                        'EXPECTED_CALLEE_CONTRACT_REJECTION'
                        if variant.startswith('callee-') else
                        'EXPECTED_SAME_SITE_FINAL_SELECT_FAILURE')}
            self.assertFalse(MODULE.complete_matrix(proof))  # callee targets remain unpinned
            for variant in MODULE.VARIANTS:
                proof['rows'][variant]['status'] = 'NOT_RUN'
                self.assertFalse(MODULE.complete_matrix(proof))
                proof['rows'][variant]['status'] = 'COMPLETE'
            proof['rows']['callee-owner-loss']['classification'] = 'TARGET_UNPINNED'
            self.assertFalse(MODULE.complete_matrix(proof))


if __name__ == '__main__':
    unittest.main()
