#!/usr/bin/env python3
"""Synthetic/static checks for the R23 source-array-borrow runner adapter."""
from __future__ import annotations
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import shutil
import types
import unittest

HERE = Path(__file__).resolve().parent
RUNNER_PATH = HERE / 'first-callback.py'
OLD_PATH = HERE / 'actual-insert-tail-b2.py'

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

runner = load('r23_source_borrow_runner_tested', RUNNER_PATH)
old = load('r23_source_borrow_old_source_tested', OLD_PATH)

class SourceBorrowRunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.evidence = Path(self.temp.name) / 'evidence'
        self.parent_case = self.evidence / 'full_body' / 'cases' / 'actual_three_current_full_posts'
        (self.parent_case / 'original').mkdir(parents=True)
        (self.parent_case / 'verified').mkdir()
        self.parent_record = {
            'profile': runner.R11_PROFILE, 'prefix': False, 'mutation': None,
            'source_sha256': 'source-sha', 'source_git_blob': 'git-blob',
            'actual_drop_sha256': 'drop-sha', 'actual_insert_tail_sha256': 'insert-sha',
            'actual_insert_tail_bytes': 321, 'mechanically_specialized_insert_sha256': 'spec-insert-sha',
            'final_posts_sha256': runner._sha(old.INSERT_CONTRACT),
        }
        (self.parent_case / 'original/lib.rs').write_bytes(b'parent original')
        (self.parent_case / 'verified/lib.rs').write_bytes(b'parent verified')
        self.parent_record['original_sha256'] = runner._sha((self.parent_case / 'original/lib.rs').read_bytes())
        self.parent_record['verified_sha256'] = runner._sha((self.parent_case / 'verified/lib.rs').read_bytes())
        gate_rows = {}
        for name in ('exporter', 'decode', 'verifast', 'refinement'):
            receipt = {
                'stage': name, 'exit_code': 0, 'status': 'SUCCESS', 'source_unchanged': True,
                'source_before': {'original/lib.rs': self.parent_record['original_sha256'],
                                  'verified/lib.rs': self.parent_record['verified_sha256'],
                                  'small_sort_source': self.parent_record['source_sha256']},
            }
            receipt['source_after'] = dict(receipt['source_before'])
            (self.parent_case / f'{name}-stage.json').write_text(json.dumps(receipt))
            gate_rows[name] = {'present': True, 'admitted': True, 'exit_code': 0,
                               'callback_exit_code': 0, 'source_unchanged': True, 'status': 'SUCCESS'}
        (self.evidence / 'full_body/preparation.json').write_text(
            json.dumps(self.parent_record, sort_keys=True))
        self.prep_sha = runner._sha((self.evidence / 'full_body/preparation.json').read_bytes())
        self.parent_gate = {'admitted': True, 'stages': gate_rows}
        self.canonical = {
            'original_body': b'pub unsafe fn insert_tail() {}\n',
            'source_sha256': self.parent_record['source_sha256'],
            'source_git_blob': self.parent_record['source_git_blob'],
            'actual_drop_sha256': self.parent_record['actual_drop_sha256'],
            'actual_insert_tail_sha256': self.parent_record['actual_insert_tail_sha256'],
            'actual_insert_tail_bytes': self.parent_record['actual_insert_tail_bytes'],
            'mechanically_specialized_insert_sha256': self.parent_record['mechanically_specialized_insert_sha256'],
        }
        self.original_body = b'pub unsafe fn insert_tail() {}\n'
        self.verified_body = b'pub unsafe fn insert_tail() {}\n'
        self._original_raw_parent_body = runner._raw_parent_body
        runner._raw_parent_body = lambda *args: (self.canonical, self.original_body, self.verified_body)

    def tearDown(self):
        runner._raw_parent_body = self._original_raw_parent_body
        self.temp.cleanup()

    def prepare(self, control=None):
        return runner._prepare_r23_source_borrow(
            self.evidence, self.parent_case, self.parent_record, old, self.prep_sha,
            True, self.parent_gate, control=control)

    def source_gate(self, case, record, control=None):
        return runner._r23_source_borrow_source_gate(
            case, self.parent_case, self.parent_record, record, old, self.prep_sha,
            self.parent_gate, control)

    def test_positive_pair_is_exact_and_runtime_preserving(self):
        case, record = self.prepare()
        self.assertTrue(self.source_gate(case, record))
        original = (case / 'original/lib.rs').read_bytes()
        verified = (case / 'verified/lib.rs').read_bytes()
        self.assertTrue(runner._body_runtime_equal(original, verified))
        self.assertEqual(1, verified.count(b'let mut values = [10_u64, 20_u64, 5_u64];'))
        self.assertEqual(1, verified.count(b'let begin = values.as_mut_ptr();'))
        self.assertEqual(1, verified.count(b'insert_tail(begin, begin.add(2), is_less);'))
        self.assertEqual(1, original.count(b'pub unsafe fn r23_checked_slice_as_mut_ptr'))
        self.assertEqual(1, verified.count(b'pub unsafe fn r23_checked_slice_as_mut_ptr'))
        self.assertIn(b'full_borrow(k, r23_u64_array3_fbc(t, p))', verified)
        self.assertIn(b'r19_insert_tail_unwind_cleanup();', verified)
        begin_at = verified.index(b'let begin = values.as_mut_ptr();')
        post_marker_at = verified.index(b'r23_source_array_borrow_adapter_end(')
        lifetime_end_at = verified.index(b'end_lifetime(r23_borrow_k);')
        array_recovery_at = verified.index(b'Array_to_array(r23_array_p);')
        raw_prep_at = verified.index(b'r18_u64_array_inv(begin, 3);')
        insert_call_at = verified.index(b'insert_tail(begin, begin.add(2), is_less);')
        raw_cleanup_at = verified.index(b'r19_insert_tail_unwind_cleanup();')
        self.assertLess(begin_at, post_marker_at)
        self.assertLess(post_marker_at, lifetime_end_at)
        self.assertLess(lifetime_end_at, array_recovery_at)
        self.assertLess(array_recovery_at, raw_prep_at)
        self.assertLess(raw_prep_at, insert_call_at)
        self.assertLess(insert_call_at, raw_cleanup_at)
        self.assertEqual(json.loads((case / 'preparation.json').read_text()), record)
        self.assertFalse(record['proof_credit'])
        self.assertFalse(record['accepted'])
        verified_path = case / 'verified/lib.rs'
        before = verified_path.read_bytes()
        verified_path.write_bytes(before + b'\n// tampered\n')
        self.assertFalse(self.source_gate(case, record))
        verified_path.write_bytes(before)

    def test_three_source_pair_controls_reach_only_exact_refusal(self):
        for name, refusal in runner.R23_SOURCE_BORROW_CONTROLS.items():
            with self.subTest(control=name):
                case, record = self.prepare(name)
                self.assertTrue(self.source_gate(case, record, name))
                original = (case / 'original/lib.rs').read_bytes()
                verified = (case / 'verified/lib.rs').read_bytes()
                self.assertTrue(runner._body_runtime_equal(original, verified))
                verified_source = verified.decode()
                if name == 'missing_end_marker':
                    self.assertNotIn('r23_source_array_borrow_adapter_end(', verified_source)
                elif name == 'duplicate_begin_marker':
                    self.assertEqual(2, verified_source.count('r23_source_array_borrow_adapter(r23_borrow_k, values);'))
                else:
                    self.assertIn("let_lft 'r23_wrong_borrow = r23_borrow_k;", verified_source)
                    self.assertNotIn("let_lft 'r23_borrow = r23_borrow_k;", verified_source)
                log = f'verified/lib.rs(100,1): error: {refusal}'
                (case / 'verifast.log').write_text(log + '\n')
                execution = {
                    'stages': {'exporter': 0, 'decode': 0, 'verifast': 1, 'refinement': 0},
                    'source_unchanged_at_every_stage': True,
                    'stage_receipt_gate': {'admitted': True},
                }
                result = runner._classify_r23_source_borrow(
                    case, self.parent_case, self.parent_record, record, execution, old,
                    self.prep_sha, name, self.parent_gate)
                self.assertEqual('SOURCE_ADAPTER_INTENDED_REFUSAL', result['classification'])
                self.assertTrue(result['intended_negative'])
                self.assertEqual(refusal, result['expected_refusal'])
                self.assertFalse(result['proof_credit'])
                wrong_stage = {**execution, 'stages': {'exporter': 0, 'decode': 0,
                    'verifast': 0, 'refinement': 1}}
                result = runner._classify_r23_source_borrow(
                    case, self.parent_case, self.parent_record, record, wrong_stage, old,
                    self.prep_sha, name, self.parent_gate)
                self.assertEqual('INCONCLUSIVE', result['classification'])
                (case / 'verifast.log').write_text(
                    f'error: {refusal}\nerror: unrelated verifier failure\n')
                result = runner._classify_r23_source_borrow(
                    case, self.parent_case, self.parent_record, record, execution, old,
                    self.prep_sha, name, self.parent_gate)
                self.assertEqual('INCONCLUSIVE', result['classification'])

    def test_classifier_fails_closed_on_service_shapes_and_receipts(self):
        case, record = self.prepare()
        (case / 'verifast.log').write_text("Verifying function 'insert_tail'\n")
        good = {'stages': {'exporter': 0, 'decode': 0, 'verifast': 0, 'refinement': 0},
                'source_unchanged_at_every_stage': True,
                'stage_receipt_gate': {'admitted': True}}
        cases = [
            ('wrong execution type', [], 'INCONCLUSIVE'),
            ('NOT_RUN', {'status': 'NOT_RUN'}, 'NOT_RUN'),
            ('missing stage map', {'stages': None}, 'INCONCLUSIVE'),
            ('partial stage map', {'stages': {'exporter': 0}}, 'INCONCLUSIVE'),
            ('null stage exit', {'stages': {**good['stages'], 'decode': None}}, 'INCONCLUSIVE'),
            ('wrong stage exit type', {'stages': {**good['stages'], 'decode': '0'}}, 'INCONCLUSIVE'),
            ('exception', {**good, 'exception': 'synthetic'}, 'INCONCLUSIVE'),
            ('timeout', {**good, 'stages': {**good['stages'], 'exporter': 124}}, 'INCONCLUSIVE'),
            ('partial failure', {**good, 'stages': {**good['stages'], 'exporter': 1}}, 'INCONCLUSIVE'),
            ('source mismatch', {**good, 'source_unchanged_at_every_stage': False}, 'INCONCLUSIVE'),
            ('receipt mismatch', {**good, 'stage_receipt_gate': {'admitted': False}}, 'INCONCLUSIVE'),
        ]
        for label, execution, expected in cases:
            with self.subTest(label=label):
                result = runner._classify_r23_source_borrow(
                    case, self.parent_case, self.parent_record, record, execution,
                    old, self.prep_sha, parent_stage_receipt_gate=self.parent_gate)
                self.assertEqual(expected, result['classification'])
                self.assertFalse(result['proof_credit'])
        (case / 'verifast.log').unlink()
        mismatch = copy.deepcopy(record)
        mismatch['actual_insert_tail_sha256'] = 'other'
        result = runner._classify_r23_source_borrow(
            case, self.parent_case, self.parent_record, mismatch, good, old,
            self.prep_sha, parent_stage_receipt_gate=self.parent_gate)
        self.assertEqual('INCONCLUSIVE', result['classification'])

    def test_runner_success_and_dispatch_exception_paths(self):
        class Consumer:
            @staticmethod
            def _hashes(case):
                return {name: hashlib.sha256((case / name / 'lib.rs').read_bytes()).hexdigest()
                        for name in ('original', 'verified')}

            @staticmethod
            def _stage_receipts(case, stages, before):
                return {'admitted': True, 'source_hashes': before}

        def exercise(raise_dispatch=False):
            base_env = {runner.R23_SOURCE_BORROW_ENV: '1'}

            def execute(case, args, child_env):
                if raise_dispatch:
                    raise RuntimeError('synthetic dispatch fault')
                self.assertEqual('1', child_env[runner.R23_SOURCE_BORROW_ENV])
                (case / 'verifast.log').write_text('\n'.join(
                    f"Verifying function '{name}'" for name in
                    ('insert_tail', 'b2_three_from_local', 'r23_checked_slice_as_mut_ptr')))
                return {'stages': {'exporter': 0, 'decode': 0, 'verifast': 0, 'refinement': 0}}

            def dispatch(case, args, **kwargs):
                return runner._execute_case_with_r9_trace(
                    execute, case, args, base_env, profile=runner.R11_PROFILE,
                    actual_callback_case=kwargs.get('actual_callback_case', False),
                    source_adapter_eligible=kwargs.get('source_adapter_eligible', False))

            shutil.rmtree(self.evidence / 'r23_source_borrow', ignore_errors=True)
            return runner._run_r23_source_borrow_diagnostic(
                self.evidence, self.parent_case, self.parent_record, old, Consumer,
                types.SimpleNamespace(r8_owned_array_allocation=False), runner.R11_PROFILE,
                dispatch, parent_preparation_sha=self.prep_sha,
                parent_source_unchanged=True, parent_stage_receipt_gate=self.parent_gate)

        result = exercise()
        self.assertEqual('SOURCE_ARRAY_BORROW_ALL_TARGETS_EXIT0', result['classification'])
        self.assertFalse(result['proof_credit'])
        self.assertFalse(result['b2_achieved'])
        result = exercise(raise_dispatch=True)
        self.assertEqual('INCONCLUSIVE', result['classification'])
        self.assertIn('dispatch raised', result['reason'])

    def test_dispatch_flag_is_exact_case_scoped_and_caller_env_is_unchanged(self):
        calls = []
        inherited = {runner.R23_SOURCE_BORROW_ENV: '1', runner.VF_EXPORT_OWNED_NLL_FACTS: '1'}
        env_before = dict(inherited)
        source_case = Path('/tmp') / runner.R23_SOURCE_BORROW_NAME
        runner._execute_case_with_r9_trace(
            lambda case, args, child_env: calls.append((case, child_env.copy())) or {},
            source_case, object(), inherited, profile=runner.R11_PROFILE,
            actual_callback_case=True, source_adapter_eligible=True)
        self.assertEqual(env_before, inherited)
        self.assertEqual('1', calls[-1][1][runner.R23_SOURCE_BORROW_ENV])
        self.assertNotIn(runner.VF_EXPORT_OWNED_NLL_FACTS, calls[-1][1])
        for control in runner.R23_SOURCE_BORROW_CONTROLS:
            control_case = Path('/tmp') / f'{runner.R23_SOURCE_BORROW_NAME}_{control}'
            runner._execute_case_with_r9_trace(
                lambda case, args, child_env: calls.append((case, child_env.copy())) or {},
                control_case, object(), inherited, profile=runner.R11_PROFILE,
                actual_callback_case=True, source_adapter_eligible=True)
            self.assertEqual('1', calls[-1][1][runner.R23_SOURCE_BORROW_ENV])
        self.assertNotIn(runner.R23_SOURCE_BORROW_ENV,
                         runner._campaign_environment(inherited))
        self.assertNotIn(runner.R23_SOURCE_BORROW_ENV,
                         runner._r11_storage_placement_env(inherited))
        runner._execute_case_with_r9_trace(
            lambda case, args, child_env: calls.append((case, child_env.copy())) or {},
            Path('/tmp/body_isolation'), object(), inherited, profile=runner.R11_PROFILE,
            actual_callback_case=True, source_adapter_eligible=False)
        self.assertNotIn(runner.R23_SOURCE_BORROW_ENV, calls[-1][1])
        with self.assertRaises(RuntimeError):
            runner._execute_case_with_r9_trace(
                lambda *args: {}, Path('/tmp/wrong'), object(), inherited,
                profile=runner.R11_PROFILE, actual_callback_case=True,
                source_adapter_eligible=True)

    def test_registration_presence_only_schedules_r23_case_and_never_capture(self):
        source = RUNNER_PATH.read_text()
        self.assertIn("source_borrow_registered = 'r23_source_borrow_registration' in profile_card", source)
        self.assertIn("if not source_borrow_registered:", source)
        self.assertIn('source_adapter_eligible=source_adapter_eligible', source)
        self.assertIn("owned_nll_capture=False", source)
        self.assertIn("'proof_credit': False", source)

if __name__ == '__main__':
    unittest.main(verbosity=2)
