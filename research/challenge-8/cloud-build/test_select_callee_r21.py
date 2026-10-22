"""Bounded synthetic proof-row identity and failure-preservation tests; no proof tools."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('r21_existing_fixtures', HERE / 'test_select_callee_r20.py')
FIX = importlib.util.module_from_spec(spec)
spec.loader.exec_module(FIX)
C = FIX.CALLEE
NAME = 'merged-optin'
ARGV = ['/synthetic/bin/verifast', '-rustc_args', '--edition 2021', '-verbose', '1', 'verified/lib.rs']
SOURCES = {'original/lib.rs': 'a' * 64, 'verified/lib.rs': 'b' * 64}


def stage(name=NAME, argv=ARGV, sources=SOURCES, exit_code=0):
    return {'status': 'RAN', 'exit': exit_code, 'argv': argv,
            'source_before': sources, 'source_after': sources,
            'source_unchanged': True, 'intrinsic_gate_active': True,
            'pointer_drop_gate_active': True,
            'stdout': 'r20-' + name + '.log', 'stderr': 'r20-' + name + '.log'}


def classify(value, *, name=NAME, log='fine', observed=SOURCES):
    return C.classify_bound_row(name, value, log, expected_argv=ARGV,
                               expected_sources=SOURCES, observed_sources=observed)


class BoundRow(unittest.TestCase):
    def test_success_error_and_certificate_control_preserve_distinctions(self):
        self.assertEqual(classify(stage()), 'POSITIVE_VERIFIED_SOURCE_REPORTED')
        self.assertEqual(classify(stage(exit_code=1), log='lib.rsspec(462): error: missing own'), 'POSITIVE_FAILED')
        name = 'merged-no-optin'
        self.assertEqual(classify(stage(name=name, exit_code=2), name=name,
                                  log='Fatal error: owner exact verified source SHA256'),
                         'INTENDED_CERTIFICATE_REFUSAL')
        self.assertEqual(classify(stage(), log='x: error: failure'), 'POSITIVE_FAILED')

    def test_timeout_partial_missing_null_wrong_type_and_explicit_not_run(self):
        for value in (None, [], 'RAN', {}, {'status': 'RAN'},
                      dict(stage(), status='TIMED_OUT', exit=124),
                      dict(stage(), status='NOT_RUN', exit=None),
                      dict(stage(), exit=None), dict(stage(), exit=True),
                      dict(stage(), exit='0')):
            with self.subTest(value=value):
                self.assertEqual(classify(value), 'NOT_RUN_OR_INCONCLUSIVE')

    def test_missing_empty_or_wrong_type_log_is_inconclusive(self):
        for log in (None, "", " ", []):
            with self.subTest(log=log):
                self.assertEqual(classify(stage(), log=log), 'NOT_RUN_OR_INCONCLUSIVE')

    def test_source_stage_target_and_gate_mismatches_fail_closed(self):
        for delta in ({'argv': ARGV[:-1] + ['other/lib.rs']}, {'argv': ['other-tool']},
                      {'stdout': 'other.log'}, {'stderr': None},
                      {'source_before': {}}, {'source_after': {'verified/lib.rs': 'c' * 64}},
                      {'source_unchanged': False}, {'intrinsic_gate_active': False},
                      {'pointer_drop_gate_active': None}):
            with self.subTest(delta=delta):
                self.assertEqual(classify(dict(stage(), **delta)), 'SOURCE_STAGE_TARGET_MISMATCH')
        self.assertEqual(classify(stage(), observed={}), 'SOURCE_STAGE_TARGET_MISMATCH')
        self.assertEqual(classify(stage(), name='other-row'), 'SOURCE_STAGE_TARGET_MISMATCH')


class ProofIntegration(unittest.TestCase):
    def run_rows(self, root, *, mutation=None, exception_on=None):
        FIX.make_case(root)
        args = FIX.Args(root, int(time.time()) + 3600)
        real_load = C.load
        class Fake:
            def proof_stage(self, repo, case, tool, schema, sysroot, deadline, name, label):
                if name == exception_on:
                    raise RuntimeError('original stage exception')
                short = name.removeprefix('r20-')
                positive = short == NAME
                sources = {p: C.sha((case / p).read_bytes()) for p in SOURCES}
                value = stage(short, [str(tool / 'bin/verifast'), *ARGV[1:]], sources,
                              0 if positive else 2)
                (case / (name + '.log')).write_text('fine' if positive else 'Fatal error: owner exact verified source SHA256')
                if mutation:
                    mutation(value)
                return value
        def load(path, name, expected=None):
            return Fake() if path.name == 'o26-recipe.py' else real_load(path, name, expected)
        env = {**FIX.ENV, 'SORT4_R20_CALLEE_PHASE_ID': 'SORT4-ACTUAL-SELECT-2026-10-23-R21'}
        with patch.dict(os.environ, env, clear=True), patch.object(C, 'load', load):
            try:
                return C.proof(args)
            finally:
                self.assertNotIn(C.R20_FLAG, os.environ)

    def test_bound_positive_and_controls_keep_original_snapshot_and_no_credit(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            record = self.run_rows(root)
            self.assertTrue(record['complete'])
            self.assertTrue(record['controls_intended'])
            self.assertFalse(record['proof_credit'])
            self.assertEqual(record['rows'][NAME]['stage']['exit'], 0)
            self.assertEqual(record['rows'][NAME]['verdict'], 'POSITIVE_VERIFIED_SOURCE_REPORTED')
            self.assertEqual((root / 'cases/candidate/capture' / C.CASE / 'verified/lib.rs').read_bytes(), FIX.UNIT)

    def test_mismatch_remains_incomplete_and_preserves_exit_and_snapshot(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with self.assertRaises(SystemExit) as raised:
                self.run_rows(root, mutation=lambda s: s.update(stdout='wrong.log'))
            self.assertEqual(raised.exception.code, 3)
            record = json.loads((root / 'cases/r20-proof/r20-proof.json').read_text())
            self.assertFalse(record['complete'])
            row = record['rows'][NAME]
            self.assertEqual(row['verdict'], 'SOURCE_STAGE_TARGET_MISMATCH')
            self.assertEqual(row['stage']['exit'], 0)
            self.assertEqual(row['stage']['source_before'], row['stage']['source_after'])

    def test_exception_propagates_with_partial_record_and_no_ambient_optin(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with self.assertRaisesRegex(RuntimeError, 'original stage exception'):
                self.run_rows(root, exception_on='r20-merged-no-optin')
            record = json.loads((root / 'cases/r20-proof/r20-proof.json').read_text())
            self.assertFalse(record['complete'])
            self.assertEqual(list(record['rows']), [NAME])
            self.assertEqual(record['rows'][NAME]['stage']['exit'], 0)


if __name__ == '__main__':
    unittest.main()
