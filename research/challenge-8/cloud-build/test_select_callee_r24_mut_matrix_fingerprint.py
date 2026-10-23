"""Synthetic tests for closed R24 mutable matrix fingerprint orchestration."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    'select_callee_r24_mut_matrix_fingerprint_test_target',
    HERE / 'select-callee-r24-mut-matrix-fingerprint.py')
assert SPEC and SPEC.loader
TARGET = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(TARGET)
OLD = TARGET.load_old_adapter(HERE)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


BUILD = 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'
ORDER = list(OLD.EXPECTED_ORDER)
ORIGINAL = b'pub fn select_unpredictable<Element>() { runtime }\n'
POSITIVE = ORIGINAL + b'/*@ positive ghost @*/\n'


class FakeOwner:
    @staticmethod
    def strip_ghost(data: bytes) -> bytes:
        return re.sub(rb'/\*@.*?@\*/\n?', b'', data, flags=re.S)


class FakeCapture:
    def __init__(self, failure=None):
        self.failure = failure
        self.GUARD = self
        self.LINK = type('LinkModule', (), {'LINK': type('NestedLink', (), {
            'ERR': re.compile(r'^(.+?)\((\d+),([^)]*)\): error: (.*)$', re.M)})()})()
        self.clear_count = 0

    def clear_semantic_opt_ins(self):
        self.clear_count += 1
        for name in list(__import__('os').environ):
            if name.startswith('SORT4_') and name not in (
                    TARGET.R24_PHASE_ENV, TARGET.R21_PHASE_ENV, 'SORT4_SELECT_PROFILE'):
                __import__('os').environ.pop(name, None)

    @staticmethod
    def _body_payload(mode, index, source):
        if index in (6, 7):
            return f'{mode}-{index}-{source["verified_sha256"]}'.encode()
        return f'{mode}-{index}-stable'.encode()

    def capture_case(self, case, source, _args):
        if self.failure == 'capture-exception':
            raise LookupError('synthetic capture exception')
        stages = {}
        for name in ('normal-export', 'normal-decode', 'readonly-export',
                     'readonly-decode', 'refinement'):
            code = 1 if self.failure == name else 0
            stages[name] = {'status': 'RAN', 'exit': code}
        if self.failure == 'timeout':
            stages['normal-export'] = {'status': 'TIMEOUT', 'exit': None}
        if self.failure == 'missing-stage':
            stages.pop('readonly-decode')
        for name, raw in (('normal-mir.bin', b'normal binary'),
                          ('readonly-mir.bin', b'readonly binary'),
                          ('normal-mir.txt', b'normal decoded'),
                          ('readonly-mir.txt', b'readonly decoded')):
            (case / name).write_bytes(raw)
        return {'stages': stages, 'frontend_refinement': self.failure != 'refinement',
                'source_unchanged': self.failure != 'guard-source-drift'}

    def full_body_capture(self, case, source, _stages):
        if self.failure == 'full-null':
            return None
        result = {}
        for mode in ('normal', 'readonly'):
            body_rows = []
            for index, defpath in enumerate(ORDER):
                raw = self._body_payload(mode, index, source)
                if self.failure == 'body-drift' and index == 5:
                    raw = raw + b'changed out-of-scope body'
                name = f'{mode}-body-{index}-full-mir.txt'
                (case / name).write_bytes(raw)
                body_rows.append({'index': index, 'defpath': defpath, 'file': name,
                                  'bytes': len(raw), 'sha256': digest(raw)})
            decoded_name = f'{mode}-mir.txt'
            decoded = (case / decoded_name).read_bytes()
            result[mode] = {'classification': 'COMPLETE_NINE_BODY_CAPTURE_ONLY',
                'whole_decoded_mir_file': decoded_name,
                'whole_decoded_mir_sha256': digest(decoded),
                'exact_body_count_and_order': True, 'bodies': body_rows}
        return result

    def refusal_fingerprint(self, case, source, _args):
        snapshots = {}
        for name in TARGET.SNAPSHOT_NAMES:
            if self.failure == 'missing-snapshot' and name == 'body-8':
                continue
            if name in ('body-6', 'body-7', 'unit'):
                raw = f'{name}:{source["verified_sha256"]}'.encode()
            else:
                raw = f'{name}:stable'.encode()
            filename = f'actual-nested-9-{name}.marshal'
            (case / filename).write_bytes(raw)
            snapshots[name] = {'file': filename, 'bytes': len(raw), 'sha256': digest(raw)}
        if self.failure == 'source-drift':
            (case / 'verified/lib.rs').write_bytes(b'late source mutation')
        stage = {'status': 'RAN', 'exit': 2, 'source_unchanged': True}
        if self.failure == 'fingerprint-timeout':
            stage = {'status': 'TIMEOUT', 'exit': None, 'source_unchanged': True}
        elif self.failure == 'fingerprint-not-run':
            stage = {'status': 'NOT_RUN', 'exit': None, 'source_unchanged': True}
        elif self.failure == 'fingerprint-null-source':
            stage['source_unchanged'] = None
        (case / OLD.CAPTURE_LOG).write_text(OLD.NATIVE_REFUSAL_LINE + '\n')
        return {'classification': 'INTENDED_DIAGNOSTIC_REFUSAL_NO_PROOF_RULE',
            'expected_refusal_seen': True, 'all_ten_snapshots': len(snapshots) == 10,
            'body_proof_run': False, 'stage': stage, 'snapshots': snapshots}


class FakeOld:
    def __init__(self, test, failure=None):
        self.test = test
        self.failure = failure
        self.capture = FakeCapture(failure)
        self.__name__ = 'FakeOld'

    def __getattr__(self, name):
        return getattr(OLD, name)

    def run(self, args):
        if self.failure == 'old-exception':
            raise LookupError('synthetic positive adapter exception')
        evidence = Path(args.evidence)
        root = evidence / 'cases/r24-mut-capture'
        case = root / 'source-preparation/nine-body/nine-body-mut'
        (case / 'original').mkdir(parents=True)
        (case / 'verified').mkdir()
        (case / 'original/lib.rs').write_bytes(ORIGINAL)
        (case / 'verified/lib.rs').write_bytes(POSITIVE)
        source_view = root / 'source-repository'
        source_view.mkdir(parents=True)
        source = {'source_order': ORDER,
            'original_sha256': digest(ORIGINAL), 'verified_sha256': digest(POSITIVE),
            'specialization': 'T = *mut Element; Element unrestricted',
            'contract_text_sha256': TARGET.CONTRACT_SHA256}
        snapshots = {}
        for name in TARGET.SNAPSHOT_NAMES:
            raw = (f'{name}:{digest(POSITIVE)}'.encode() if name in ('unit', 'body-6', 'body-7')
                   else f'{name}:stable'.encode())
            filename = f'actual-nested-9-{name}.marshal'
            (case / filename).write_bytes(raw)
            snapshots[name] = {'file': filename, 'bytes': len(raw), 'sha256': digest(raw)}
        for name, raw in (('normal-mir.bin', b'normal binary'),
                          ('readonly-mir.bin', b'readonly binary'),
                          ('normal-mir.txt', b'normal decoded'),
                          ('readonly-mir.txt', b'readonly decoded')):
            (case / name).write_bytes(raw)
        (case / OLD.CAPTURE_LOG).write_text(OLD.NATIVE_REFUSAL_LINE + '\n')
        full = {}
        for mode in ('normal', 'readonly'):
            bodies = []
            for index, defpath in enumerate(ORDER):
                raw = FakeCapture._body_payload(mode, index, source)
                bodies.append({'index': index, 'defpath': defpath,
                               'file': f'{mode}-body-{index}-full-mir.txt',
                               'bytes': len(raw), 'sha256': digest(raw)})
            full[mode] = {'classification': 'COMPLETE_NINE_BODY_CAPTURE_ONLY',
                'whole_decoded_mir_file': f'{mode}-mir.txt',
                'whole_decoded_mir_sha256': digest(f'{mode} decoded'.encode()),
                'exact_body_count_and_order': True, 'bodies': bodies}
            for body in bodies:
                raw = FakeCapture._body_payload(mode, body['index'], source)
                (case / body['file']).write_bytes(raw)
        stages = {name: {'status': 'RAN', 'exit': 0} for name in (
            'normal-export', 'normal-decode', 'readonly-export', 'readonly-decode', 'refinement')}
        fingerprint = {'classification': 'INTENDED_DIAGNOSTIC_REFUSAL_NO_PROOF_RULE',
            'expected_refusal_seen': True, 'all_ten_snapshots': True,
            'body_proof_run': False,
            'stage': {'status': 'RAN', 'exit': 2, 'source_unchanged': True},
            'snapshots': snapshots}
        provider_record = dict(self.test.provider_record)
        if self.failure == 'provider-mismatch':
            provider_record['build_id'] = 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb'
        return {'complete': True, 'classification': 'MUTABLE_SOURCE_MIR_CAPTURE_ONLY',
            'native_build_id': BUILD, 'provider_record': provider_record,
            'source_records': {'final_nine_body': source,
                'original': {'path': 'cases/r24-mut-capture/source-preparation/nine-body/nine-body-mut/original/lib.rs'},
                'verified': {'path': 'cases/r24-mut-capture/source-preparation/nine-body/nine-body-mut/verified/lib.rs'}},
            'full_body_capture': full, 'stages': stages,
            'guard_capture': {'stages': stages, 'frontend_refinement': True,
                              'source_unchanged': True},
            'fingerprint': fingerprint}

    def load_capture_runtime(self, *_args):
        return {'capture': self.capture}

    def load_source_writers(self, _source_view):
        return {'owner': FakeOwner()}


class MatrixFingerprintTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.repo = self.base / 'repo'
        self.repo.mkdir()
        self.cloud = self.repo / 'research/challenge-8/cloud-build'
        self.cloud.mkdir(parents=True)
        task = self.repo / 'research/challenge-8/task-history/select-callee-r24'
        task.mkdir(parents=True)
        for name in ('P2-MUT-MATRIX-FINGERPRINT-MODE.json', 'P2-MUT-CAPTURE-PINS.json',
                     'P2-MUT-CAPTURE-MODE.json'):
            shutil.copyfile(Path(__file__).parents[1] / 'task-history/select-callee-r24' / name,
                            task / name)
        self.evidence = self.base / 'evidence'
        self.evidence.mkdir()
        self.provider_record = {'provider': 'cloud-build', 'build_id': BUILD,
            'project': 'smallsort-ci', 'region': 'global', 'os': 'ubuntu-22.04', 'arch': 'x86_64'}
        self.env = {'SMALLSORT_EXECUTION_PROVIDER': 'cloud-build',
            TARGET.R24_PHASE_ENV: TARGET.R24_PHASE, TARGET.R21_PHASE_ENV: TARGET.R21_PHASE,
            'LANE': TARGET.LANE, 'CLOUD_BUILD_ID': BUILD,
            'CLOUD_BUILD_PROJECT_ID': 'smallsort-ci', 'CLOUD_BUILD_REGION': 'global',
            'SORT4_SELECT_PROFILE': 'experimental-s6-26.10-v1'}
        self.fake_pins = self.make_synthetic_pins()

    def tearDown(self):
        self.temp.cleanup()

    def make_synthetic_pins(self):
        snapshots = {}
        for name in TARGET.SNAPSHOT_NAMES:
            raw = (f'{name}:{digest(POSITIVE)}'.encode() if name in ('unit', 'body-6', 'body-7')
                   else f'{name}:stable'.encode())
            snapshots[name] = {'file': f'actual-nested-9-{name}.marshal',
                               'bytes': len(raw), 'sha256': digest(raw)}
        return {'schema': 'select-r24-mut-positive-capture-pins-v1', 'build_id': BUILD,
            'status': 'COMPLETE_SOURCE_REPORTED_CAPTURE_ONLY', 'accepted': False,
            'proof_credit': 0, 'body_proof_run': False, 'typed_admission': False,
            'publication_allowed': False,
            'source': {'original_sha256': digest(ORIGINAL), 'verified_sha256': digest(POSITIVE),
                'specialization': 'T = *mut Element; Element unrestricted',
                'contract_text_sha256': TARGET.CONTRACT_SHA256},
            'snapshots': snapshots,
            'normal': {'classification': 'COMPLETE_NINE_BODY_CAPTURE_ONLY',
                'exact_body_count_and_order': True,
                'decoded_sha256': digest(b'normal decoded')},
            'readonly': {'classification': 'COMPLETE_NINE_BODY_CAPTURE_ONLY',
                'exact_body_count_and_order': True,
                'decoded_sha256': digest(b'readonly decoded')}}

    def args(self):
        return SimpleNamespace(repo=self.repo, cloud_dir=self.cloud, evidence=self.evidence,
            tool_home=Path('/synthetic/tool'), schema=Path('/synthetic/schema'),
            compiler_sysroot=Path('/synthetic/sysroot'), deadline_epoch=123456,
            mode_file=self.repo / OLD.MODE_REL, mode_sha256=OLD.MODE_SHA256,
            matrix_mode_file=self.repo / TARGET.MODE_REL,
            matrix_mode_sha256=TARGET.MODE_SHA256)

    def run_matrix(self, failure=None, *, env=None, transform=None, pins=None):
        old = FakeOld(self, failure)
        if transform is None:
            def transform(source, variant):
                return source + b'/*@ ' + variant.encode() + b' @*/\n'
        with patch.dict('os.environ', self.env if env is None else env, clear=True):
            return TARGET.run(self.args(), old_adapter=old,
                positive_pins_loader=lambda _repo: self.fake_pins if pins is None else pins,
                capture_loader=old.load_capture_runtime,
                source_loader=old.load_source_writers,
                transform_loader=lambda _repo: transform,
                pins_validator=lambda _pins: None)

    def test_success_has_exact_eight_rows_location_control_and_zero_credit(self):
        summary = self.run_matrix()
        self.assertTrue(summary['complete'])
        self.assertEqual(summary['classification'], 'SOURCE_REPORTED_MUTABLE_MATRIX_FINGERPRINT_ONLY')
        self.assertEqual(list(summary['rows']), list(TARGET.VARIANTS))
        self.assertEqual(len({row['verified_sha256'] for row in summary['rows'].values()}), 8)
        self.assertTrue(summary['location_control']['complete'])
        self.assertTrue(summary['location_control']['reproduces_positive_pins'])
        self.assertTrue(all(row['source_unchanged'] and row['ghost_strip_identity']
                            and row['status'] == 'COMPLETE_SOURCE_REPORTED_FINGERPRINT'
                            and row['native_build_id'] == BUILD for row in summary['rows'].values()))
        self.assertFalse(summary['body_proof_run'])
        self.assertFalse(summary['typed_admission'])
        self.assertFalse(summary['semantic_rule_enabled'])
        self.assertFalse(summary['accepted'])
        self.assertEqual(summary['proof_credit'], 0)
        self.assertFalse(summary['publication_allowed'])
        self.assertEqual(json.loads((self.evidence / TARGET.SUMMARY_REL).read_text()), summary)

    def test_wrong_route_or_ambient_proof_optin_refuses_before_old_adapter(self):
        for env in (dict(self.env, **{TARGET.R24_PHASE_ENV: 'wrong'}),
                    dict(self.env, SORT4_R24_CHECKED_POINTER_OUTCOMES='1'),
                    dict(self.env, SORT4_A1_NINE_REPO_ROOT='/synthetic/repo'),
                    dict(self.env, SORT4_ACTUAL_NESTED_H2_REPO_ROOT='/synthetic/repo'),
                    dict(self.env, SORT4_ACTUAL_FORGET_OWN_REPO_ROOT='/synthetic/repo')):
            with self.subTest(env=env), patch.dict('os.environ', env, clear=True):
                old = FakeOld(self)
                with self.assertRaises(RuntimeError):
                    TARGET.run(self.args(), old_adapter=old,
                        positive_pins_loader=lambda _repo: self.fake_pins,
                        pins_validator=lambda _pins: None)
                self.assertFalse((self.evidence / 'cases/r24-mut-capture').exists())

    def test_wrong_matrix_manifest_hash_refuses_before_positive_adapter(self):
        args = self.args()
        args.matrix_mode_sha256 = '0' * 64
        old = FakeOld(self)
        with patch.dict('os.environ', self.env, clear=True):
            with self.assertRaisesRegex(RuntimeError, 'matrix mode hash'):
                TARGET.run(args, old_adapter=old,
                    positive_pins_loader=lambda _repo: self.fake_pins,
                    pins_validator=lambda _pins: None)
        self.assertFalse((self.evidence / 'cases/r24-mut-capture').exists())

    def test_positive_pin_mismatch_fails_before_matrix_capture(self):
        pins = self.make_synthetic_pins()
        pins['source']['verified_sha256'] = '0' * 64
        with patch.dict('os.environ', self.env, clear=True):
            result = TARGET.run(self.args(), old_adapter=FakeOld(self),
                    positive_pins_loader=lambda _repo: pins,
                    capture_loader=lambda *_: self.fail('capture must not start'),
                    source_loader=lambda *_: self.fail('source loader must not start'),
                    transform_loader=lambda *_: self.fail('transform must not start'),
                    pins_validator=lambda _pins: None)
        self.assertFalse(result['complete'])
        partial = json.loads((self.evidence / TARGET.SUMMARY_REL).read_text())
        self.assertFalse(partial['complete'])

    def test_capture_failures_timeout_missing_null_and_not_run_rows_are_incomplete(self):
        for failure in ('normal-export', 'timeout', 'missing-stage', 'refinement',
                        'full-null', 'missing-snapshot', 'fingerprint-timeout',
                        'fingerprint-not-run', 'fingerprint-null-source', 'guard-source-drift'):
            with self.subTest(failure=failure):
                self.evidence = self.base / ('evidence-' + failure)
                self.evidence.mkdir()
                summary = self.run_matrix(failure)
                self.assertFalse(summary['complete'])
                self.assertFalse(summary['body_proof_run'])
                self.assertTrue(any(not row['complete'] for row in summary['rows'].values()))

    def test_native_provider_and_out_of_scope_body_changes_refuse_matrix(self):
        pins = self.make_synthetic_pins()
        self.evidence = self.base / 'evidence-provider-mismatch'
        self.evidence.mkdir()
        old = FakeOld(self, 'provider-mismatch')
        with patch.dict('os.environ', self.env, clear=True):
            result = TARGET.run(self.args(), old_adapter=old,
                positive_pins_loader=lambda _repo: pins,
                pins_validator=lambda _pins: None)
        self.assertFalse(result['complete'])
        self.assertIn('native build', result['rows']['positive']['incomplete_reasons'][0])

        self.evidence = self.base / 'evidence-body-drift'
        self.evidence.mkdir()
        result = self.run_matrix('body-drift')
        self.assertFalse(result['complete'])
        self.assertFalse(result['location_control']['complete'])

    def test_source_drift_and_non_ghost_transform_refuse(self):
        def bad_transform(source, variant):
            if variant == 'omit-selected-own':
                return b'not ghost-only'
            return source + b'/*@ ' + variant.encode() + b' @*/\n'
        with patch.dict('os.environ', self.env, clear=True):
            with self.assertRaisesRegex(RuntimeError, 'ghost-strip identity'):
                TARGET.run(self.args(), old_adapter=FakeOld(self),
                    positive_pins_loader=lambda _repo: self.fake_pins,
                    capture_loader=FakeOld(self).load_capture_runtime,
                    source_loader=FakeOld(self).load_source_writers,
                    transform_loader=lambda _repo: bad_transform,
                    pins_validator=lambda _pins: None)
        self.evidence = self.base / 'evidence-drift'
        self.evidence.mkdir()
        summary = self.run_matrix('source-drift')
        self.assertFalse(summary['complete'])
        self.assertFalse(summary['location_control']['complete'])
        self.assertFalse(summary['rows']['omit-selected-own']['complete'])

    def test_original_adapter_or_capture_exceptions_are_saved_and_preserved(self):
        for failure, message in (('old-exception', 'synthetic positive adapter exception'),
                                 ('capture-exception', 'synthetic capture exception')):
            self.evidence = self.base / ('evidence-' + failure)
            self.evidence.mkdir()
            with self.subTest(failure=failure), self.assertRaisesRegex(LookupError, message):
                self.run_matrix(failure)
            partial = json.loads((self.evidence / TARGET.SUMMARY_REL).read_text())
            self.assertFalse(partial['complete'])
            self.assertEqual(partial['exception']['type'], 'LookupError')


if __name__ == '__main__':
    unittest.main()
