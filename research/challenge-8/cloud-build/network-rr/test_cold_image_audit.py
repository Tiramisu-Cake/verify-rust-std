#!/usr/bin/env python3
"""Synthetic contract tests for cold-image receipt/error classification."""

import importlib.util
from pathlib import Path
import unittest
import json
import tempfile

MODULE_PATH = Path(__file__).with_name('cold-image-audit.py')
spec = importlib.util.spec_from_file_location('cold_image_audit', MODULE_PATH)
audit_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit_module)

BUILD_ID = '01234567-89ab-cdef-0123-456789abcdef'
DIGEST = audit_module.REGISTRY + '@sha256:' + ('a' * 64)
GOOD_STATUS = {'stage': 'cold-image', 'state': 'COMPLETE', 'build_id': BUILD_ID, 'exit_code': 0}
GOOD_RECEIPT = {
    'schema': 'refinedrust-g1-registry-image-receipt-v1',
    'stage': 'cold-image',
    'build_id': BUILD_ID,
    'image_digest': DIGEST,
    'internal_receipt_sha256': 'b' * 64,
    'cargo_lock_sha256': audit_module.RR_LOCK_SHA256,
}


class ColdImageAuditTests(unittest.TestCase):
    def test_api_override_matches_server_without_proof_credit(self):
        response = {'Client': {'ApiVersion': '1.41'},
                    'Server': {'ApiVersion': '1.41', 'MinAPIVersion': '1.12'}}
        result = audit_module.validate_docker_version(response, BUILD_ID)
        self.assertEqual(result['state'], 'COMPATIBLE_API')
        self.assertFalse(result['accepted'])
        self.assertFalse(result['proof_credit'])
        response['Server']['ApiVersion'] = '1.52'
        self.assertEqual(audit_module.validate_docker_version(response, BUILD_ID)['server_max_api'], '1.52')

    def test_api_preflight_refuses_partial_null_wrong_type_and_mismatch(self):
        good = {'Client': {'ApiVersion': '1.41'}, 'Server': {'ApiVersion': '1.41'}}
        cases = [None, [], 'NOT_RUN', {}, {'Client': None, 'Server': {}},
                 {'Client': {'ApiVersion': '1.52'}, 'Server': {'ApiVersion': '1.41'}},
                 {'Client': {'ApiVersion': None}, 'Server': {'ApiVersion': '1.41'}},
                 {'Client': {'ApiVersion': '1.41', 'APIVersion': '1.52'}, 'Server': {'ApiVersion': '1.41'}},
                 {'Client': {'ApiVersion': '1.41'}, 'Server': {'ApiVersion': '1.40'}},
                 {'Client': {'ApiVersion': '1.41'}, 'Server': {'ApiVersion': '1.52', 'MinAPIVersion': '1.44'}}]
        for value in cases:
            with self.subTest(value=value), self.assertRaises(ValueError):
                audit_module.validate_docker_version(value, BUILD_ID)
        with self.assertRaises(ValueError):
            audit_module.validate_docker_version(good, BUILD_ID, 'warm-g1')
        with self.assertRaises(ValueError):
            audit_module.validate_docker_version(good, None)

    def test_api_error_preserves_input_digest_and_exception_without_executing_tools(self):
        with tempfile.TemporaryDirectory() as directory:
            source, output = Path(directory) / 'version.json', Path(directory) / 'result.json'
            source.write_text('{malformed')
            code = audit_module.api_main(['--input', str(source), '--output', str(output), '--build-id', BUILD_ID])
            result = json.loads(output.read_text())
            self.assertEqual(code, 2)
            self.assertEqual(result['error_type'], 'JSONDecodeError')
            self.assertEqual(len(result['input_sha256']), 64)
            self.assertEqual(source.read_text(), '{malformed')
            self.assertFalse(result['accepted'])

    def test_success(self):
        result = audit_module.summarize(GOOD_STATUS, GOOD_RECEIPT, BUILD_ID)
        self.assertTrue(result['diagnostic_complete'])
        self.assertFalse(result['accepted'])
        self.assertFalse(result['proof_credit'])

    def test_stage_error(self):
        status = {**GOOD_STATUS, 'exit_code': 23, 'state': 'FAILED'}
        self.assertEqual(audit_module.summarize(status, GOOD_RECEIPT, BUILD_ID)['failure_class'], 'stage-error')

    def test_timeout(self):
        status = {**GOOD_STATUS, 'exit_code': 124, 'state': 'FAILED'}
        self.assertEqual(audit_module.summarize(status, None, BUILD_ID)['failure_class'], 'timeout')

    def test_partial_receipt(self):
        receipt = {**GOOD_RECEIPT, 'cargo_lock_sha256': None}
        self.assertEqual(audit_module.summarize(GOOD_STATUS, receipt, BUILD_ID)['failure_class'], 'partial-receipt')

    def test_missing_receipt(self):
        self.assertEqual(audit_module.summarize(GOOD_STATUS, audit_module.MISSING, BUILD_ID)['failure_class'], 'missing-receipt')

    def test_null_receipt(self):
        self.assertEqual(audit_module.summarize(GOOD_STATUS, None, BUILD_ID)['failure_class'], 'null-receipt')

    def test_wrong_type_receipt(self):
        self.assertEqual(audit_module.summarize(GOOD_STATUS, 'receipt', BUILD_ID)['failure_class'], 'wrong-type-receipt')

    def test_not_run(self):
        status = {**GOOD_STATUS, 'state': 'NOT_RUN', 'exit_code': 0}
        self.assertEqual(audit_module.summarize(status, GOOD_RECEIPT, BUILD_ID)['failure_class'], 'not-run')

    def test_source_stage_mismatch(self):
        receipt = {**GOOD_RECEIPT, 'stage': 'warm-g1'}
        self.assertEqual(audit_module.summarize(GOOD_STATUS, receipt, BUILD_ID)['failure_class'], 'source-stage-mismatch')

    def test_unknown_or_malformed_state(self):
        for state, expected in ((None, 'null-state'), (7, 'wrong-type-state'),
                                ('FAILED', 'unexpected-state')):
            status = {**GOOD_STATUS, 'state': state}
            self.assertEqual(audit_module.summarize(status, GOOD_RECEIPT, BUILD_ID)['failure_class'], expected)
        status = dict(GOOD_STATUS)
        del status['state']
        self.assertEqual(audit_module.summarize(status, GOOD_RECEIPT, BUILD_ID)['failure_class'], 'missing-state')

    def test_cargo_lock_hash_mismatch(self):
        receipt = {**GOOD_RECEIPT, 'cargo_lock_sha256': 'c' * 64}
        self.assertEqual(audit_module.summarize(GOOD_STATUS, receipt, BUILD_ID)['failure_class'], 'cargo-lock-mismatch')

    def test_missing_status_and_wrong_status_type(self):
        self.assertEqual(audit_module.summarize(None, None, BUILD_ID)['failure_class'], 'wrong-type-status')
        status = {**GOOD_STATUS, 'exit_code': True}
        self.assertEqual(audit_module.summarize(status, None, BUILD_ID)['failure_class'], 'wrong-type-exit-code')


if __name__ == '__main__':
    unittest.main()
