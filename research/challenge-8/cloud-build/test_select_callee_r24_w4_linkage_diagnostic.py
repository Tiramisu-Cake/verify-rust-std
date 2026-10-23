"""Synthetic service tests for the W4 linkage diagnostic wrapper."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import inspect
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SCRIPT = HERE / 'select-callee-r24-w4-linkage-diagnostic.py'
SPEC = importlib.util.spec_from_file_location('w4_linkage_diagnostic_under_test', SCRIPT)
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MOD)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def typed_observation():
    calls = [{'site': i} for i in range(8)]
    return {'schema': 'select-r24-w4-mir-calls-v1', 'complete': True,
            'status': 'COMPLETE_TYPED_MIR_OBSERVATION', 'typed_call_linkage': 'UNKNOWN',
            'typed_callee_family_observation': 'OBSERVED_STRUCTURAL_MIR_CALLS',
            'source_site_mapping': 'EQUAL_EMITTED_COORDINATES_ONLY',
            'normal': {'calls': calls}, 'readonly': {'calls': calls},
            'proof_claim': False, 'accepted': False, 'proof_credit': 0,
            'publication_allowed': False}


class FakeCapture:
    def __init__(self):
        self.collect_result = None
        self.collect_exception = None
        self.audit_result = {'evidence_complete': True}

    def _safe_file(self, evidence: Path, rel: str):
        path = evidence / rel
        if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(evidence.resolve()):
            raise ValueError('unsafe fake file')
        raw = path.read_bytes()
        return raw, {'path': rel, 'bytes': len(raw), 'sha256': sha(raw)}

    def collect(self, args, *, stage_runner=None):
        if self.collect_exception:
            raise self.collect_exception
        report = self.collect_result
        if report is not None:
            root = Path(args.evidence)
            (root / 'cases/r24-w4-capture').mkdir(parents=True, exist_ok=True)
            if report.get('complete') is not True:
                (root / 'cases/r24-w4-capture/W4-CAPTURE.json').write_text(
                    json.dumps(report), encoding='utf-8')
                return report
            fixtures = report.pop('_fixture_bytes')
            (root / 'cases/r24-w4-capture/W4-CAPTURE.json').write_text(
                json.dumps(report), encoding='utf-8')
            for key, text in (('normal', 'normal-func'), ('readonly', 'readonly-func')):
                (root / f'cases/r24-w4-capture/{key}-sort4-full-mir.txt').write_text(text, encoding='utf-8')
            for rel, payload in fixtures.items():
                path = root / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(payload)
        return report

    def audit(self, args):
        path = Path(args.output)
        path.write_text(json.dumps(self.audit_result), encoding='utf-8')
        return self.audit_result

    def run_stage(self, *args, **kwargs):
        raise AssertionError('default native stage must not run in synthetic tests')


class FakeAnalyzer:
    def __init__(self, result=None):
        self.result = result or typed_observation()

    def analyze_pair(self, normal, readonly):
        return self.result


class W4LinkageDiagnosticTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.repo = self.root / 'repo'
        self.cloud = self.root / 'cloud'
        self.evidence = self.root / 'evidence'
        self.tools = self.root / 'tools'
        for p in (self.repo, self.cloud, self.evidence, self.tools):
            p.mkdir()
        self.args = argparse.Namespace(repo=str(self.repo), cloud_dir=str(self.cloud),
                                       evidence=str(self.evidence), tool_home=str(self.tools),
                                       schema=str(self.tools / 'schema'),
                                       compiler_sysroot=str(self.tools / 'sysroot'),
                                       capture_mode_file=str(self.repo / MOD.CAPTURE_MODE_REL),
                                       mode_file=str(self.repo / MOD.MODE_REL),
                                       candidate='a' * 40, deadline_epoch=9999999999,
                                       output=None, runner_exit=0, failed_stage='complete')
        self.capture = FakeCapture()
        self.analyzer = FakeAnalyzer()
        self.original = b'original source fixture\n'
        self.verified = b'verified source fixture\n'
        self.normal = 'normal-func'
        self.readonly = 'readonly-func'
        self.pin = {'schema': 'select-r24-w4-capture-pins-v1',
                    'source': {'source_sha256': MOD.SOURCE_SHA256,
                               'source_git_blob': '40939f922bcb6fdc7ee0d30427fa861827043827',
                               'target': 'sort4_stable', 'original_sha256': sha(self.original),
                               'verified_sha256': sha(self.verified)},
                    'mir': {m: {'full_function_record': f'cases/r24-w4-capture/{m}-sort4-full-mir.txt',
                                'full_function_record_sha256': sha(text.encode())}
                            for m, text in (('normal', self.normal), ('readonly', self.readonly))},
                    'tool_hashes': MOD.TOOL_HASHES}
        self.capture_report = {
            'schema': 'select-r24-w4-capture-v1', 'complete': True,
            'candidate': 'a' * 40,
            'tool_hashes': MOD.TOOL_HASHES,
            'source': {'source_sha256': MOD.SOURCE_SHA256,
                       'source_git_blob': '40939f922bcb6fdc7ee0d30427fa861827043827',
                       'target': 'sort4_stable', 'original_sha256': sha(self.original),
                       'verified_sha256': sha(self.verified),
                       'repository_source_unchanged': True,
                       'fixture_paths': {'original': 'cases/r24-w4-capture/fixture/original/lib.rs',
                                         'verified': 'cases/r24-w4-capture/fixture/verified/lib.rs'}},
            'mir': {m: {'full_function_record': f'cases/r24-w4-capture/{m}-sort4-full-mir.txt',
                        'full_function_record_sha256': sha(text.encode())}
                    for m, text in (('normal', self.normal), ('readonly', self.readonly))},
            '_fixture_bytes': {'cases/r24-w4-capture/fixture/original/lib.rs': self.original,
                               'cases/r24-w4-capture/fixture/verified/lib.rs': self.verified}}
        self.capture.collect_result = self.capture_report
        self.native_result = None

    def tearDown(self):
        self.temp.cleanup()

    def services(self):
        return {'capture': self.capture, 'analyzer': self.analyzer,
                'native_stage_runner': self.native_stage}

    def guard(self):
        stack = mock.patch.multiple(
            MOD,
            _validate_context=mock.DEFAULT,
            _validate_route=mock.DEFAULT,
            _validate_mode=mock.DEFAULT,
            _load_json_pin=mock.DEFAULT,
            _tool_hashes=mock.DEFAULT,
            _source_state=mock.DEFAULT,
        )
        values = stack.start()
        values['_validate_context'].return_value = (self.repo, self.cloud, self.evidence, self.tools)
        values['_validate_route'].return_value = {'provider': 'cloud-build'}
        values['_validate_mode'].return_value = {'enabled': True}
        values['_load_json_pin'].return_value = self.pin
        values['_tool_hashes'].return_value = MOD.TOOL_HASHES
        values['_source_state'].return_value = {'path': MOD.SOURCE_REL.as_posix(),
                                                 'sha256': MOD.SOURCE_SHA256,
                                                 'expected_sha256': MOD.SOURCE_SHA256, 'intact': True}
        self.addCleanup(stack.stop)
        self.patchers = values

    def native_stage(self, name, argv, root, env, hashes, deadline, cap,
                     stdin_name=None, stdout_name=None):
        self.native_call = (name, list(argv), dict(env), dict(hashes), cap, stdout_name)
        if isinstance(self.native_result, BaseException):
            raise self.native_result
        result = self.native_result
        if result is None:
            out = root / stdout_name
            out.write_text('raw diagnostic only\n', encoding='utf-8')
            (root / 'first-barrier-stderr.log').write_text('raw stderr\n', encoding='utf-8')
            result = {'argv': list(argv), 'exit': 0, 'timeout_seconds': cap,
                      'fixture_before': dict(hashes), 'fixture_after': dict(hashes),
                      'fixture_integrity': True, 'stdout': stdout_name,
                      'stderr': 'first-barrier-stderr.log'}
        (root / 'first-barrier-stage.json').write_text(json.dumps(result), encoding='utf-8')
        return result

    def run_wrapper(self):
        self.guard()
        return MOD.run(self.args, services=self.services())

    def test_success_is_typed_diagnostic_only_with_exact_native_argv_and_isolated_copy(self):
        with mock.patch.dict(os.environ, {'LD_LIBRARY_PATH': '/synthetic/lib',
                                          'RUSTUP_HOME': '/synthetic/rustup',
                                          'CARGO_HOME': '/synthetic/cargo',
                                          'RUSTUP_TOOLCHAIN': 'synthetic-toolchain',
                                          'PATH': '/synthetic/base-path'}):
            report = self.run_wrapper()
        self.assertTrue(report['complete'], report['errors'])
        self.assertTrue(report['typed_call_inventory_complete'])
        self.assertTrue(report['verifier_invoked'])
        self.assertEqual(report['actual_body_proof_status'], 'UNKNOWN')
        self.assertFalse(report['call_linkage'])
        self.assertFalse(report['accepted'])
        self.assertEqual(report['proof_credit'], 0)
        self.assertEqual(self.native_call[0], 'first-barrier')
        self.assertEqual(self.native_call[1], [str(self.tools / 'bin/verifast'), *MOD.NATIVE_ARGV[1:]])
        self.assertEqual(set(k for k in self.native_call[2] if k.startswith('SORT4_')),
                         {MOD.R24_PHASE_ENV, MOD.R21_PHASE_ENV, 'SORT4_SELECT_PROFILE'})
        self.assertIn('PATH', self.native_call[2])
        self.assertEqual(self.native_call[2]['LD_LIBRARY_PATH'], '/synthetic/lib')
        self.assertEqual(self.native_call[2]['RUSTUP_HOME'], '/synthetic/rustup')
        self.assertTrue(self.native_call[2]['PATH'].startswith(str(self.tools / 'bin') + os.pathsep))
        copied = self.evidence / MOD.CASE_REL / 'verified/lib.rs'
        self.assertEqual(copied.read_bytes(), self.verified)
        self.assertEqual(report['native']['logs']['stdout']['sha256'], sha(b'raw diagnostic only\n'))
        self.assertEqual(report['native']['logs']['stderr']['sha256'], sha(b'raw stderr\n'))

    def test_pinned_production_stage_runner_exports_actual_keyword_api(self):
        module = MOD._load(REPO / MOD.NATIVE_STAGE_RUNNER_REL,
                           'w4_pinned_actual_stage_module_test', MOD.NATIVE_STAGE_RUNNER_SHA256)
        self.assertTrue(callable(getattr(module, 'run_stage', None)))
        signature = inspect.signature(module.run_stage)
        bound = signature.bind('first-barrier', ['/tool/bin/verifast', 'verified/lib.rs'],
                               self.root / 'case', {'PATH': '/tool/bin'},
                               {'verified/lib.rs': 'a' * 64}, 9999999999, 1200,
                               stdout_name='w4-first-barrier.log')
        bound.apply_defaults()
        self.assertEqual(bound.arguments['stdout_name'], 'w4-first-barrier.log')
        self.assertIsNone(bound.arguments['stdin_name'])
        self.assertNotIn('stderr_name', signature.parameters)

    def test_exit_zero_one_two_are_raw_diagnostics_and_nonzero_is_not_success_claim(self):
        for index, exit_code in enumerate((0, 1, 2)):
            with self.subTest(exit=exit_code):
                if index:
                    self.temp.cleanup()
                    self.setUp()
                self.native_result = {'argv': [str(self.tools / 'bin/verifast'), *MOD.NATIVE_ARGV[1:]],
                                      'exit': exit_code, 'timeout_seconds': 1200,
                                      'fixture_before': {'original/lib.rs': sha(self.original),
                                                         'verified/lib.rs': sha(self.verified)},
                                      'fixture_after': {'original/lib.rs': sha(self.original),
                                                        'verified/lib.rs': sha(self.verified)},
                                      'fixture_integrity': True, 'stdout': 'w4-first-barrier.log',
                                      'stderr': 'first-barrier-stderr.log'}
                # Write expected stage output in its independent native tree.
                def stage(*args, **kwargs):
                    root = args[2]
                    (root / 'w4-first-barrier.log').write_text(f'exit={exit_code}\n', encoding='utf-8')
                    (root / 'first-barrier-stderr.log').write_text(f'stderr={exit_code}\n', encoding='utf-8')
                    (root / 'first-barrier-stage.json').write_text(
                        json.dumps(self.native_result), encoding='utf-8')
                    return self.native_result
                self.guard()
                report = MOD.run(self.args, services={**self.services(), 'native_stage_runner': stage})
                self.assertTrue(report['complete'], report['errors'])
                self.assertEqual(report['native']['stage']['exit'], exit_code)
                self.assertEqual(report['actual_body_proof_status'], 'UNKNOWN')

    def test_timeout_missing_null_wrongtype_and_partial_are_incomplete(self):
        cases = [
            {'argv': [str(self.tools / 'bin/verifast'), *MOD.NATIVE_ARGV[1:]], 'exit': 124,
             'fixture_before': {}, 'fixture_after': {}, 'fixture_integrity': False,
             'stdout': 'w4-first-barrier.log', 'stderr': 'first-barrier-stderr.log'},
            None,
            {},
            'bad stage',
        ]
        for index, stage in enumerate(cases):
            with self.subTest(stage=stage):
                if index:
                    self.temp.cleanup()
                    self.setUp()
                self.native_result = stage
                if isinstance(stage, dict):
                    def stage_runner(*args, **kwargs):
                        root = args[2]
                        (root / 'w4-first-barrier.log').write_text('partial\n', encoding='utf-8')
                        (root / 'first-barrier-stderr.log').write_text('partial stderr\n', encoding='utf-8')
                        (root / 'first-barrier-stderr.log').write_text('partial stderr\n', encoding='utf-8')
                        (root / 'first-barrier-stage.json').write_text(json.dumps(stage), encoding='utf-8')
                        return stage
                    services = {**self.services(), 'native_stage_runner': stage_runner}
                elif stage is None:
                    services = {**self.services(), 'native_stage_runner': lambda *a, **k: None}
                else:
                    services = self.services()
                    if stage == 'bad stage':
                        self.native_result = 'bad stage'
                self.guard()
                report = MOD.run(self.args, services=services)
                self.assertFalse(report['complete'])
                self.assertFalse(report['accepted'])
                self.assertEqual(report['proof_credit'], 0)
                self.assertTrue((self.evidence / MOD.SUMMARY_REL).is_file())

    def test_incomplete_capture_stops_before_parser_and_verifier(self):
        self.capture.collect_result = {'schema': 'select-r24-w4-capture-v1', 'complete': False,
                                       'errors': ['synthetic partial capture']}
        self.analyzer.analyze_pair = mock.Mock(side_effect=AssertionError('parser must not run'))
        report = self.run_wrapper()
        self.assertFalse(report['complete'])
        self.assertFalse(report['verifier_invoked'])
        self.analyzer.analyze_pair.assert_not_called()

    def test_analyzer_unknown_incomplete_preserves_observation_and_still_runs_native_barrier(self):
        self.analyzer.result = {'complete': False, 'status': 'INCOMPLETE_UNKNOWN',
                                'typed_call_linkage': 'UNKNOWN', 'errors': ['truncated']}
        report = self.run_wrapper()
        self.assertFalse(report['complete'])
        self.assertFalse(report['typed_call_inventory_complete'])
        self.assertTrue(report['verifier_invoked'])
        self.assertIn('native', report)
        self.assertEqual(report['native']['stage']['exit'], 0)
        self.assertEqual(report['actual_body_proof_status'], 'UNKNOWN')

    def test_source_stage_target_mismatch_is_refused(self):
        def wrong_target(*args, **kwargs):
            root, stdout = args[2], kwargs['stdout_name']
            (root / stdout).write_text('diagnostic\n', encoding='utf-8')
            (root / 'first-barrier-stderr.log').write_text('diagnostic stderr\n', encoding='utf-8')
            stage = {'argv': [str(self.tools / 'bin/verifast'), *MOD.NATIVE_ARGV[1:]],
                     'exit': 0, 'fixture_before': {'verified/lib.rs': 'wrong'},
                     'fixture_after': {'verified/lib.rs': 'wrong'}, 'fixture_integrity': True,
                     'stdout': stdout, 'stderr': 'first-barrier-stderr.log'}
            (root / 'first-barrier-stage.json').write_text(json.dumps(stage), encoding='utf-8')
            return stage
        self.guard()
        report = MOD.run(self.args, services={**self.services(), 'native_stage_runner': wrong_target})
        self.assertFalse(report['complete'])
        self.assertTrue(any('source-stage-target' in error for error in report['errors']))

    def test_dirty_repository_source_during_native_diagnostic_is_refused(self):
        self.guard()
        good = {'path': MOD.SOURCE_REL.as_posix(), 'sha256': MOD.SOURCE_SHA256,
                'expected_sha256': MOD.SOURCE_SHA256, 'intact': True}
        dirty = {**good, 'sha256': 'f' * 64, 'intact': False}
        self.patchers['_source_state'].side_effect = [good, dirty]
        report = MOD.run(self.args, services=self.services())
        self.assertFalse(report['complete'])
        self.assertFalse(report['source_intact'])
        self.assertTrue(report['verifier_invoked'])
        self.assertTrue(any('repository source changed' in error for error in report['errors']))

    def test_native_exception_propagates_and_partial_snapshot_survives(self):
        original = RuntimeError('native callback exploded')
        self.native_result = original
        with self.assertRaisesRegex(RuntimeError, 'native callback exploded'):
            self.run_wrapper()
        saved = json.loads((self.evidence / MOD.SUMMARY_REL).read_text())
        self.assertFalse(saved['complete'])
        self.assertEqual(saved['exception']['message'], 'native callback exploded')
        self.assertFalse(saved['accepted'])
        self.assertEqual(saved['proof_credit'], 0)

    def test_capture_exception_propagates_with_partial_wrapper_record(self):
        original = ValueError('capture failed after partial')
        self.capture.collect_exception = original
        with self.assertRaisesRegex(ValueError, 'capture failed after partial'):
            self.run_wrapper()
        saved = json.loads((self.evidence / MOD.SUMMARY_REL).read_text())
        self.assertFalse(saved['complete'])
        self.assertEqual(saved['exception']['type'], 'ValueError')

    def test_audit_reopens_capture_and_rechecks_physical_log_without_rerunning_verifier(self):
        report = self.run_wrapper()
        self.assertTrue(report['complete'], report['errors'])
        self.capture.audit_result = {'evidence_complete': True}
        self.guard()
        audit = MOD.audit(self.args, services=self.services())
        self.assertTrue(audit['evidence_complete'], audit['errors'])
        log = self.evidence / MOD.CASE_REL / 'w4-first-barrier.log'
        log.write_text('changed diagnostic\n', encoding='utf-8')
        self.guard()
        audit = MOD.audit(self.args, services=self.services())
        self.assertFalse(audit['evidence_complete'])
        self.assertTrue(any('stage/log inventory changed' in error for error in audit['errors']))


if __name__ == '__main__':
    unittest.main()
