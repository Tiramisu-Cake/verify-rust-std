"""Synthetic failure-preservation checks; no proof tools are executed."""
import argparse
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import hashlib

TEST_SPEC = importlib.util.spec_from_file_location('r21_fractional_proof_test_fixtures',
    Path(__file__).with_name('test_select_callee_r21_fractional_proof.py'))
FIXTURES = importlib.util.module_from_spec(TEST_SPEC)
TEST_SPEC.loader.exec_module(FIXTURES)


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()

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

    def test_exact_target_matrix_requires_all_source_and_observation_bindings(self):
        sources = {variant: FIXTURES.source_for(variant)
                   for variant in FIXTURES.TARGET_HELPER.VARIANTS}
        tool_spec = FIXTURES.tool_spec_fixture()
        target_map = FIXTURES.target_map_fixture()
        validation = FIXTURES.TARGET_HELPER.validate_target_map(
            target_map, sources, tool_spec,
            tool_spec_file=FIXTURES.TARGET_HELPER.TOOL_SPEC_FILE)
        original_sha = _sha(FIXTURES.ORIGINAL)
        snapshots = {name: {'file': name + '.marshal', 'bytes': 5,
                            'sha256': _sha(name.encode())}
                     for name in ('unit', *(f'body-{i}' for i in range(9)))}
        cases = {}
        rows = {}
        for variant in MODULE.VARIANTS:
            source_sha = _sha(sources.get(variant, FIXTURES.source_for(variant)))
            cases[variant] = {'verified_sha256': source_sha, 'snapshots': snapshots}
            expected_sources = {'original/lib.rs': original_sha,
                                'verified/lib.rs': source_sha}
            positive = variant == 'positive'
            row = {
                'variant': variant, 'status': 'COMPLETE',
                'verified_sha256': source_sha,
                'observed_sources_after_stage': expected_sources,
                'source_intact_after_stages': True,
                'normal_unwind_nested_drop_gates': True,
                'stage': {'status': 'RAN', 'exit': 0 if positive else 1,
                          'intrinsic_gate_active': True,
                          'pointer_drop_gate_active': True,
                          'source_unchanged': True,
                          'source_before': expected_sources,
                          'source_after': expected_sources},
                'preflight_capture_check': {'complete': True, 'snapshots': snapshots},
                'postflight_capture_check': {'complete': True, 'snapshots': snapshots},
                'classification': ('POSITIVE_VERIFIED_SOURCE_REPORTED' if positive else
                    'EXPECTED_CALLEE_CONTRACT_REJECTION'
                    if variant.startswith('callee-') else
                    'EXPECTED_SAME_SITE_TYPED_FAILURE'),
            }
            if not positive:
                target = validation['targets'][variant]
                row.update(expected_diagnostic_target=target,
                    log_sha256=target['log_sha256'],
                    diagnostic_target_observation={
                        'variant': variant, 'matches_first_and_only_error': True,
                        'accepted': False, 'proof_credit': False,
                        'provenance_status':
                            'CALLER_DECLARED_PRIOR_OBSERVATION_CONSISTENT_NOT_AUTHENTICATED',
                        'target': {key: target[key] for key in
                            ('file', 'line', 'start_column', 'end_column', 'message')},
                        'log_sha256': target['log_sha256']})
            rows[variant] = row
        raw_map_sha = _sha(json.dumps(target_map, sort_keys=True).encode())
        proof = {'schema': 'r21-fractional-classified-proof-v1',
            'complete': True, 'accepted': False, 'proof_credit': False,
            'body_proof_run': True, 'variant_order': list(MODULE.VARIANTS),
            'pins': {'base_original_sha256': original_sha, 'cases': cases},
            'rows': rows, 'diagnostic_target_validation': validation,
            'diagnostic_target_map_sha256': validation['target_map_sha256'],
            'target_map_unchanged': True, 'tool_spec_unchanged': True,
            'entry_dependencies': {'target_map_sha256': raw_map_sha,
                                   'target_map_canonical_sha256':
                                       validation['target_map_sha256'],
                                   'tool_spec_sha256': _sha(tool_spec),
                                   'target_helper_sha256': MODULE.TARGET_HELPER_SHA256}}
        self.assertTrue(MODULE.complete_matrix(proof))
        for mutate in (
            lambda p: p['rows']['no-retained-half']['observed_sources_after_stage'].__setitem__(
                'verified/lib.rs', '0' * 64),
            lambda p: p['rows']['callee-owner-loss']['diagnostic_target_observation'].__setitem__(
                'matches_first_and_only_error', False),
            lambda p: p['rows']['omit-selected-own']['postflight_capture_check']['snapshots'].pop(
                'body-8'),
            lambda p: p.__setitem__('target_map_unchanged', False),
        ):
            bad = json.loads(json.dumps(proof))
            mutate(bad)
            self.assertFalse(MODULE.complete_matrix(bad))


if __name__ == '__main__':
    unittest.main()
