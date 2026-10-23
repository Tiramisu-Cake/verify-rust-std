from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock


HELPER = Path(__file__).with_name('select-callee-r24-w4-capture.py')
SPEC = importlib.util.spec_from_file_location('r24_w4_capture_tested', HELPER)
CAP = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(CAP)


def _hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class FakeCapture:
    @staticmethod
    def graph_inventory(decoded_path, out, mode):
        raw = decoded_path.read_bytes()
        row = {'classification': 'SYNTHETIC_GRAPH', 'mode': mode,
               'decoded_sha256': _hash(raw), 'proof_credit': False}
        (out / f'{mode}-graph-inventory.json').write_text(json.dumps(row))
        return row

    @staticmethod
    def complete_function_record(decoded, basename):
        return ('crate::sort4_stable', 'synthetic record: select_unpredictable\n')


class FakeGhostStrip:
    @staticmethod
    def strip_ghost(raw):
        return raw


def _base_source(root: Path) -> bytes:
    path = root / CAP.SOURCE_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (b'fn sort4_stable<T, F>() {\n'
           b' let c1 = is_less(a, b);\n let c2 = is_less(a, b);\n'
           b' let c3 = is_less(a, b);\n let c4 = is_less(a, b);\n'
           b' let c5 = is_less(a, b);\n}\n')
    path.write_bytes(raw)
    return raw


def _source_record(evidence: Path) -> dict:
    original = b'fn sort4_stable<T, F>() { }\n'
    pair = original
    root = evidence / CAP.SUMMARY_REL.parent / 'fixture'
    (root / 'original').mkdir(parents=True)
    (root / 'verified').mkdir(parents=True)
    (root / 'original/lib.rs').write_bytes(original)
    (root / 'verified/lib.rs').write_bytes(pair)
    return {
        'source_path': CAP.SOURCE_REL.as_posix(), 'source_sha256': CAP.SOURCE_SHA256,
        'source_git_blob': CAP.SOURCE_BLOB, 'original_sha256': _hash(original),
        'verified_sha256': _hash(pair), 'ghost_strip_identity': True,
        'runtime_source_sha256': _hash(original),
        'source_call_counts': {key.decode(): value for key, value in CAP.COUNTS.items()},
        'signature': 'generic signature', 'target': 'sort4_stable',
        'body_annotation_stage': 'c1-c5-four-source-recovery-v1',
        'source_comparator_lines': [2, 3, 4, 5, 6],
        'c1_c5_comparator_lines': [10, 20, 30, 40, 50],
        'c1_c5_coordinates_source_reported': True,
        'c5_metadata': {'actual_indexed_calls': 5},
        'fixture_paths': {
            'original': 'cases/r24-w4-capture/fixture/original/lib.rs',
            'verified': 'cases/r24-w4-capture/fixture/verified/lib.rs',
        },
    }


class W4CaptureTests(unittest.TestCase):
    def test_expected_closed_mode_is_capture_only_and_hash_stable(self):
        mode = CAP.expected_mode()
        self.assertEqual(mode['phase_id'], CAP.R24_PHASE)
        self.assertEqual(mode['route_phase_id'], CAP.R21_PHASE)
        self.assertEqual(mode['lane'], CAP.LANE)
        self.assertTrue(mode['source_only'])
        self.assertFalse(mode['body_proof_run'])
        self.assertFalse(mode['call_linkage'])
        self.assertFalse(mode['proof_admission'])
        self.assertFalse(mode['publication_allowed'])
        self.assertEqual(mode['independent_proof_credit'], 0)
        self.assertEqual(_hash((json.dumps(mode, indent=2, sort_keys=True) + '\n').encode()),
                         CAP.MODE_SHA256)

    def test_route_accepts_only_exact_r24_r21_profile_and_lane(self):
        env = {'SMALLSORT_EXECUTION_PROVIDER': 'cloud-build',
               CAP.R24_PHASE_ENV: CAP.R24_PHASE, CAP.R21_PHASE_ENV: CAP.R21_PHASE,
               'LANE': CAP.LANE, 'SORT4_SELECT_PROFILE': CAP.PROFILE_LABEL}
        self.assertEqual(CAP._validate_route(env)['phase_id'], CAP.R24_PHASE)
        for key, value in ((CAP.R24_PHASE_ENV, 'wrong'),
                           (CAP.R21_PHASE_ENV, 'wrong'),
                           ('LANE', 'o26-sort4-body-r21'),
                           ('SORT4_SELECT_PROFILE', 'wrong'),
                           ('SORT4_R24_CHECKED_POINTER_OUTCOMES', '1')):
            changed = dict(env); changed[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                CAP._validate_route(changed)

    def test_stage_classifier_keeps_not_run_null_wrong_type_and_timeout_incomplete(self):
        good = {'exit': 0, 'fixture_integrity': True}
        self.assertEqual(CAP._check_stage(good, 'export'), [])
        cases = [None, {'exit': None}, {'exit': '0', 'fixture_integrity': True},
                 {'exit': 124, 'fixture_integrity': True},
                 {'exit': 0, 'fixture_integrity': False},
                 {'exit': None, 'skipped': 'deadline'}]
        for row in cases:
            with self.subTest(row=row):
                self.assertTrue(CAP._check_stage(row, 'export'))

    def test_raw_selector_mir_is_observation_only(self):
        observation = CAP._selector_observation(
            'call target select_unpredictable::<*const T>\n')
        self.assertEqual(observation['source_call_count'], 8)
        self.assertEqual(observation['typed_call_linkage'], 'UNKNOWN')
        self.assertEqual(observation['raw_occurrences'], 1)

    def test_refresh_coordinates_accepts_actual_four_tuple_and_rejects_bad_shapes(self):
        case = ('sort4_stable', b'verified', b'original', {'actual_indexed_calls': 5})
        self.assertEqual(CAP._refresh_coordinates(lambda _case: case, ('input',)),
                         (b'verified', b'original', {'actual_indexed_calls': 5}))
        for malformed in (None, 'sort4_stable', ('sort4_stable', b'v', b'o'),
                          ('wrong-target', b'v', b'o', {}),
                          ('sort4_stable', None, b'o', {}),
                          ('sort4_stable', b'v', None, {}),
                          ('sort4_stable', b'v', b'o', None),
                          ['sort4_stable', b'v', b'o', {}]):
            with self.subTest(malformed=malformed), self.assertRaises(ValueError):
                CAP._refresh_coordinates(lambda _case: malformed, ('input',))
        class OriginalFailure(Exception):
            pass
        def explode(_case):
            raise OriginalFailure('refresh callback failure')
        with self.assertRaisesRegex(OriginalFailure, 'refresh callback failure'):
            CAP._refresh_coordinates(explode, ('input',))

    def test_pinned_refresh_api_returns_case_name_and_four_values(self):
        repo = HELPER.resolve().parents[3]
        _, modules = CAP._load_constructor_inputs(repo, CAP.expected_mode())
        verified = (b'let c1 = is_less(a, b);\nlet c2 = is_less(a, b);\n'
                    b'let c3 = is_less(a, b);\nlet c4 = is_less(a, b);\n'
                    b'let c5 = is_less(a, b);\n')
        metadata = {'actual_c1_recovery': True, 'actual_indexed_calls': 5}
        result = modules['sort4_body'].refresh_callback_coordinates(
            ('sort4_stable', verified, b'original', metadata))
        self.assertEqual(len(result), 4)
        self.assertEqual(result[0], 'sort4_stable')
        self.assertEqual(CAP._refresh_coordinates(
            modules['sort4_body'].refresh_callback_coordinates,
            ('sort4_stable', verified, b'original', metadata))[0], verified)

    def _install_fake_runtime(self, root: Path, evidence: Path, *, failing_stage=None,
                              exception=None, source_exception=None):
        repo = root / 'repo'; repo.mkdir()
        source_raw = _base_source(repo)
        mode_path = repo / CAP.MODE_REL
        mode_path.parent.mkdir(parents=True, exist_ok=True)
        mode_path.write_text(json.dumps(CAP.expected_mode(), indent=2, sort_keys=True) + '\n')
        tool = root / 'tool'; tool.mkdir()
        schema = tool / 'src/rust_frontend/vf_mir/vf_mir.capnp'
        schema.parent.mkdir(parents=True)
        schema.write_text('schema')
        tool_hashes = dict(CAP.TOOL_HASHES)
        tool_hashes['src/rust_frontend/vf_mir/vf_mir.capnp'] = _hash(b'schema')
        tool_hashes['bin/rust/std/lib.rsspec'] = _hash(b'spec')
        (tool / 'bin/rust/std').mkdir(parents=True)
        (tool / 'bin/rust/std/lib.rsspec').write_bytes(b'spec')
        args = argparse.Namespace(repo=repo, cloud_dir=root, evidence=evidence,
            tool_home=tool, schema=schema, compiler_sysroot='/sysroot',
            deadline_epoch=9999999999, mode_file=mode_path,
            candidate='candidate-sha', mode_sha256=CAP.MODE_SHA256)
        def fake_construct(_repo, _evidence, _modules, _profile):
            if source_exception is not None:
                raise source_exception
            return _source_record(_evidence)

        def fake_stage(name, argv, fixture_root, env, hashes, deadline, cap,
                       stdin_name=None, stdout=None):
            if exception is not None:
                raise exception
            if name == failing_stage:
                return {'exit': None, 'skipped': 'deadline/artifact reserve',
                        'fixture_integrity': True}
            if stdout:
                target = fixture_root / stdout
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(b'synthetic MIR\n')
            return {'argv': argv, 'exit': 0, 'fixture_integrity': True,
                    'timeout_seconds': cap}

        patches = [
            mock.patch.object(CAP, '_validate_route', return_value={}),
            mock.patch.object(CAP, '_require_workspace_paths', return_value=None),
            mock.patch.object(CAP, '_read_mode', return_value=CAP.expected_mode()),
            mock.patch.object(CAP, '_validate_published_inputs', return_value=({}, {})),
            mock.patch.object(CAP, '_provider', return_value={'provider': 'cloud-build', 'build_id': 'b'}),
            mock.patch.object(CAP, '_tool_hashes', return_value=tool_hashes),
            mock.patch.object(CAP, 'TOOL_HASHES', tool_hashes),
            mock.patch.object(CAP, '_load_constructor_inputs', return_value=({}, {
                'capture': FakeCapture, 'ghost_strip': FakeGhostStrip})),
            mock.patch.object(CAP, '_construct', side_effect=fake_construct),
            mock.patch.object(CAP.subprocess, 'check_output', return_value='candidate-sha\n'),
            mock.patch.object(CAP, 'SOURCE_SHA256', _hash(source_raw)),
            mock.patch.object(CAP, 'SOURCE_REL', CAP.SOURCE_REL),
        ]
        for patcher in patches: patcher.start()
        self.addCleanup(lambda: [patcher.stop() for patcher in reversed(patches)])
        return args, fake_stage

    def test_complete_fake_capture_never_runs_verifier_and_audit_rechecks_artifacts(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); evidence = root / 'evidence'; evidence.mkdir()
            args, stage = self._install_fake_runtime(root, evidence)
            report = CAP.collect(args, stage_runner=stage)
            self.assertTrue(report['complete'])
            self.assertFalse(report['body_proof_run'])
            self.assertFalse(report['call_linkage'])
            self.assertEqual(report['call_linkage_status'], 'UNKNOWN')
            self.assertEqual(report['proof_credit'], 0)
            self.assertEqual(report['source']['source_call_counts']['hint::select_unpredictable('], 8)
            self.assertEqual(set(report['stages']), {
                'normal-export', 'normal-decode', 'readonly-export',
                'readonly-decode', 'refinement'})
            self.assertFalse(any('verifast' in str(stage.get('argv', []))
                                 for stage in report['stages'].values()))
            audit_args = argparse.Namespace(repo=args.repo, cloud_dir=args.cloud_dir,
                evidence=evidence, mode_file=args.mode_file, candidate=args.candidate,
                runner_exit=0, failed_stage='complete', output=None)
            audited = CAP.audit(audit_args)
            self.assertTrue(audited['evidence_complete'], audited['audit'])

    def test_not_run_stage_cannot_complete(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); evidence = root / 'evidence'; evidence.mkdir()
            args, stage = self._install_fake_runtime(root, evidence, failing_stage='readonly-export')
            report = CAP.collect(args, stage_runner=stage)
            self.assertFalse(report['complete'])
            self.assertIn('readonly-export stage is NOT_RUN', report['errors'])
            self.assertEqual(report['proof_credit'], 0)

    def test_baseexception_writes_partial_snapshot_then_preserves_original(self):
        class Injected(BaseException):
            pass
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); evidence = root / 'evidence'; evidence.mkdir()
            args, stage = self._install_fake_runtime(root, evidence, exception=Injected('transport'))
            with self.assertRaisesRegex(Injected, 'transport'):
                CAP.collect(args, stage_runner=stage)
            summary = json.loads((evidence / CAP.SUMMARY_REL).read_text())
            self.assertFalse(summary['complete'])
            self.assertEqual(summary['exception']['type'], 'Injected')
            self.assertFalse(summary['body_proof_run'])
            self.assertEqual(summary['proof_credit'], 0)

    def test_source_preparation_exception_preserves_partial_summary_and_stage(self):
        class SourceFailure(BaseException):
            pass
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); evidence = root / 'evidence'; evidence.mkdir()
            args, stage = self._install_fake_runtime(
                root, evidence, source_exception=SourceFailure('constructor failure'))
            with self.assertRaisesRegex(SourceFailure, 'constructor failure'):
                CAP.collect(args, stage_runner=stage)
            summary = json.loads((evidence / CAP.SUMMARY_REL).read_text())
            self.assertFalse(summary['complete'])
            self.assertEqual(summary['failed_stage'], 'source-preparation')
            self.assertEqual(summary['exception']['type'], 'SourceFailure')
            self.assertEqual(summary['runner_exit'], 4)
            self.assertEqual(summary['proof_credit'], 0)


if __name__ == '__main__':
    unittest.main()
