#!/usr/bin/env python3
"""Synthetic-only tests for the R21 fractional fingerprint recorder."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import time
import unittest
from types import SimpleNamespace
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    'select_callee_r21_fractional_test_target',
    HERE / 'select-callee-r21-fractional.py')
assert SPEC and SPEC.loader
TARGET = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(TARGET)

ORIGINAL = b'// synthetic original\n'
BASE = b'// synthetic verified owner projection\n'
UNIT_BYTES = b'synthetic default unit snapshot'
BODY_BYTES = [f'synthetic default body {i}'.encode() for i in range(9)]


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


class FakeRefresh:
    UNIT = digest(UNIT_BYTES)
    BODIES = tuple(digest(data) for data in BODY_BYTES)


class FakeTransform:
    def transform(self, verified: bytes, variant: str) -> bytes:
        return verified + f'// variant={variant}\n'.encode()


class FakeR20:
    def __init__(self, failure: str | None = None):
        self.failure = failure

    def export_decode(self, case: Path, out: Path, args):
        out.mkdir(parents=True)
        if self.failure == 'exception':
            raise RuntimeError('synthetic exporter exception')
        export = b'normal mir binary'
        decoded = b'normal mir decoded text'
        (out / 'normal-mir.bin').write_bytes(export)
        (out / 'normal-mir.txt').write_bytes(decoded)
        if self.failure == 'partial':
            return {'export': {'status': 'RAN', 'exit': 0,
                               'output': 'normal-mir.bin',
                               'output_sha256': digest(export)},
                    'decode': {'status': 'NOT_RUN'}}
        return {'export': {'status': 'RAN', 'exit': 0,
                           'output': 'normal-mir.bin',
                           'output_sha256': digest(export)},
                'decode': {'status': 'RAN', 'exit': 0,
                           'output': 'normal-mir.txt',
                           'output_sha256': digest(decoded)}}


class FakeCapture:
    def __init__(self, mode: str | None = None):
        self.mode = mode
        self.calls = 0
        self.clears = 0

    def clear_semantic_opt_ins(self):
        self.clears += 1

    def refusal_fingerprint(self, case: Path, source: dict, args):
        self.calls += 1
        for label, data in [('unit', UNIT_BYTES),
                            *((f'body-{i}', b) for i, b in enumerate(BODY_BYTES))]:
            (case / f'actual-nested-9-{label}.marshal').write_bytes(data)
        verified = (case / 'verified/lib.rs').read_bytes()
        original = (case / 'original/lib.rs').read_bytes()
        stage = {
            'status': 'RAN', 'exit': 2,
            'argv': TARGET.fingerprint_argv(Path('/synthetic/tool')),
            'source_before': {'original/lib.rs': digest(original),
                              'verified/lib.rs': digest(verified)},
            'source_after': {'original/lib.rs': digest(original),
                             'verified/lib.rs': digest(verified)},
            'source_unchanged': True,
            'intrinsic_gate_active': False,
            'pointer_drop_gate_active': False,
            'stdout': 'nine-body-fingerprint-refusal.log',
            'stderr': 'nine-body-fingerprint-refusal.log',
        }
        if self.mode == 'source-mismatch' and self.calls == 2:
            stage['source_after']['verified/lib.rs'] = '0' * 64
        if self.mode == 'null' and self.calls == 2:
            return None
        if self.mode == 'wrong-type' and self.calls == 2:
            return {'stage': [], 'body_proof_run': False}
        if self.mode == 'not-run' and self.calls == 2:
            stage['status'] = 'NOT_RUN'
        if self.mode == 'partial' and self.calls == 2:
            snapshots = {'unit': {'file': 'actual-nested-9-unit.marshal',
                                  'bytes': len(UNIT_BYTES), 'sha256': digest(UNIT_BYTES)}}
        else:
            snapshots = {}
            for label, data in [('unit', UNIT_BYTES),
                                *((f'body-{i}', b) for i, b in enumerate(BODY_BYTES))]:
                snapshots[label] = {'file': f'actual-nested-9-{label}.marshal',
                                    'bytes': len(data), 'sha256': digest(data)}
        return {'classification': TARGET.EXPECTED_REFUSAL,
                'expected_refusal_seen': True, 'all_ten_snapshots': True,
                'body_proof_run': False, 'stage': stage, 'snapshots': snapshots}


class FractionalFingerprintTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.evidence = self.root / 'evidence'
        base_case = self.evidence / 'cases/candidate/capture' / TARGET.CASE
        (base_case / 'original').mkdir(parents=True)
        (base_case / 'verified').mkdir()
        (base_case / 'original/lib.rs').write_bytes(ORIGINAL)
        (base_case / 'verified/lib.rs').write_bytes(BASE)
        self.args = SimpleNamespace(evidence=self.evidence,
                                    deadline_epoch=int(time.time()) + 3600,
                                    tool_home=Path('/synthetic/tool'),
                                    schema=Path('/synthetic/schema'),
                                    compiler_sysroot=Path('/synthetic/sysroot'),
                                    repo=self.root, cloud_dir=self.root,
                                    proof_root=self.root)
        self.hash_patches = patch.multiple(TARGET,
            ORIGINAL_SHA256=digest(ORIGINAL), BASE_VERIFIED_SHA256=digest(BASE))
        self.hash_patches.start()
        self.addCleanup(self.hash_patches.stop)
        self.env = {'SMALLSORT_EXECUTION_PROVIDER': 'cloud-build',
                    TARGET.PHASE_ENV: TARGET.PHASE}

    def tearDown(self):
        self.temp.cleanup()

    def run_batch(self, *, cap=None, r20=None, deadline=None):
        self.args.evidence = self.evidence
        if deadline is not None:
            self.args.deadline_epoch = deadline
        cap = cap or FakeCapture()
        r20 = r20 or FakeR20()
        record = TARGET.fingerprint_batch(self.args,
            transform=FakeTransform().transform,
            export_decode=r20.export_decode, cap=cap, refresh=FakeRefresh,
            env=self.env)
        return record, cap, r20

    def record_after_exit(self):
        return json.loads((self.evidence / 'cases/r21-fractional-fingerprint' /
                           'r21-fractional-fingerprint.json').read_text())

    def test_success_records_all_eight_variants_and_no_proof_credit(self):
        record, cap, _ = self.run_batch()
        self.assertTrue(record['complete'], json.dumps(record, indent=2, sort_keys=True))
        self.assertEqual(set(record['variants']), set(TARGET.VARIANTS))
        self.assertEqual(cap.calls, len(TARGET.VARIANTS) + 1)
        self.assertEqual(cap.clears, 2 * len(TARGET.VARIANTS) + 2)
        for key in ('accepted', 'proof_credit', 'body_proof_run'):
            self.assertIs(record[key], False)
        self.assertTrue(all(row['status'] == 'COMPLETE'
                            for row in record['variants'].values()))

    def test_short_deadline_preserves_explicit_not_run_and_nonzero(self):
        with self.assertRaises(SystemExit) as caught:
            self.run_batch(deadline=int(time.time()) + 2)
        self.assertEqual(caught.exception.code, 3)
        record = self.record_after_exit()
        self.assertFalse(record['complete'])
        self.assertEqual(record['location_control']['status'], 'NOT_RUN')
        self.assertIs(record['accepted'], False)

    def test_partial_and_exception_records_do_not_become_complete(self):
        with self.assertRaisesRegex(RuntimeError, 'synthetic exporter exception'):
            self.run_batch(r20=FakeR20('exception'))
        record = self.record_after_exit()
        row = record['variants']['positive']
        self.assertEqual(row['normal_mir']['status'], 'EXCEPTION')
        self.assertEqual(row['normal_mir_exception_type'], 'RuntimeError')
        self.assertIn('synthetic exporter exception', row['normal_mir_exception'])
        self.assertIn('Traceback', row['normal_mir_traceback'])

        # Isolate the pure stage validator's partial, missing, null, wrong-type,
        # and timeout handling without any repository tools.
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            self.assertFalse(TARGET.validate_export_decode(None, out)['complete'])
            self.assertFalse(TARGET.validate_export_decode({}, out)['complete'])
            self.assertFalse(TARGET.validate_export_decode(
                {'export': None, 'decode': {'status': 'TIMED_OUT', 'exit': 124}},
                out)['complete'])

    def test_empty_mir_outputs_cannot_complete_even_with_matching_hashes(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            rows = {}
            for stage, name in (("export", "normal-mir.bin"),
                                ("decode", "normal-mir.txt")):
                (out / name).write_bytes(b"")
                rows[stage] = {"status": "RAN", "exit": 0, "output": name,
                               "output_sha256": hashlib.sha256(b"").hexdigest()}
            self.assertFalse(TARGET.validate_export_decode(rows, out)["complete"])

    def test_capture_null_wrong_type_not_run_partial_and_source_mismatch_fail_closed(self):
        for mode in ('null', 'wrong-type', 'not-run', 'partial', 'source-mismatch'):
            with self.subTest(mode=mode):
                # Existing output root is deliberately fresh per test.
                self.evidence = self.root / ('evidence-' + mode)
                self.args.evidence = self.evidence
                base_case = self.evidence / 'cases/candidate/capture' / TARGET.CASE
                (base_case / 'original').mkdir(parents=True)
                (base_case / 'verified').mkdir()
                (base_case / 'original/lib.rs').write_bytes(ORIGINAL)
                (base_case / 'verified/lib.rs').write_bytes(BASE)
                with self.assertRaises(SystemExit) as caught:
                    self.run_batch(cap=FakeCapture(mode))
                self.assertEqual(caught.exception.code, 4)
                record = self.record_after_exit()
                self.assertFalse(record['complete'])
                row = record['variants']['positive']
                self.assertNotEqual(row.get('status'), 'COMPLETE')
                self.assertIs(record['proof_credit'], False)

    def test_provider_phase_and_ambient_flags_are_refused(self):
        cases = [({'SMALLSORT_EXECUTION_PROVIDER': 'github-actions',
                   TARGET.PHASE_ENV: TARGET.PHASE}, 'provider'),
                 ({'SMALLSORT_EXECUTION_PROVIDER': 'cloud-build',
                   TARGET.PHASE_ENV: 'old'}, 'phase'),
                 ({**self.env, TARGET.R20_OPT_IN: '1'}, 'R20 ambient'),
                 ({**self.env, 'SORT4_R21_FRACTIONAL_ANYTHING': '1'}, 'R21 ambient')]
        for env, label in cases:
            with self.subTest(label=label), self.assertRaises(RuntimeError):
                TARGET.require_cloud(env)

    def test_fingerprint_public_entry_preserves_full_namespace(self):
        args = SimpleNamespace(repo=self.root, cloud_dir=self.root,
            evidence=self.evidence, tool_home=Path('/synthetic/tool'),
            schema=Path('/synthetic/schema'),
            compiler_sysroot=Path('/synthetic/sysroot'),
            deadline_epoch=int(time.time()) + 3600, proof_root=self.root)
        cap = FakeCapture()
        fake_o26 = SimpleNamespace(load_capture=lambda *_args: cap)
        fake_r20 = FakeR20()
        with patch.dict(os.environ, self.env, clear=True), \
             patch.object(TARGET, 'pinned_dependencies',
                return_value=(FakeTransform(), fake_r20, fake_o26, FakeRefresh)):
            record = TARGET.fingerprint(args)
        self.assertTrue(record['complete'])
        self.assertEqual(record['dependencies']['transform_sha256'],
                         TARGET.TRANSFORM_SHA256)
        self.assertEqual(args.compiler_sysroot, Path('/synthetic/sysroot'))

    def test_fingerprint_requires_exact_exit_argv_and_log_targets(self):
        case = self.evidence / 'case'
        (case / 'original').mkdir(parents=True)
        (case / 'verified').mkdir()
        (case / 'original/lib.rs').write_bytes(ORIGINAL)
        (case / 'verified/lib.rs').write_bytes(BASE)
        cap = FakeCapture()
        result = cap.refusal_fingerprint(case, {}, self.args)
        hashes = {'original/lib.rs': digest(ORIGINAL),
                  'verified/lib.rs': digest(BASE)}
        pins = TARGET.snapshot_pins(FakeRefresh)
        argv = TARGET.fingerprint_argv(self.args.tool_home)
        self.assertTrue(TARGET.validate_fingerprint(
            result, case, hashes, pins, argv)['complete'])
        for field, bad in (('exit', 0), ('argv', argv[:-1] + ['original/lib.rs']),
                           ('stdout', 'wrong.log'), ('stderr', 'wrong.log')):
            with self.subTest(field=field):
                broken = json.loads(json.dumps(result))
                broken['stage'][field] = bad
                self.assertFalse(TARGET.validate_fingerprint(
                    broken, case, hashes, pins, argv)['complete'])

    def test_audit_delegates_and_preserves_incremental_status_without_cloud_guard(self):
        base = {'schema': 'r20-select-callee-audit-v1',
                'runner_exit': 23, 'failed_stage': 'fingerprint',
                'stage_exits': {'setup': 0},
                'baseline_proof_ran': True, 'evidence_complete': True,
                'accepted': False, 'verification_accepted': False,
                'proof_credit': False}
        fake_helper = SimpleNamespace(audit=lambda _args: dict(base))
        with tempfile.TemporaryDirectory() as tmp:
            ev = Path(tmp) / 'evidence'
            fp_path = ev / 'cases/r21-fractional-fingerprint/r21-fractional-fingerprint.json'
            output = Path(tmp) / 'audit.json'
            args = SimpleNamespace(evidence=ev, output=output,
                                   runner_exit=23, failed_stage='fingerprint')
            states = [('missing', None, False),
                      ('null', None, False),
                      ('wrong-type', [], False),
                      ('partial', {'complete': False, 'variants': {}}, False),
                      ('complete', {'complete': True}, True)]
            for name, payload, expected_complete in states:
                with self.subTest(name=name):
                    if name == 'missing':
                        fp_path.unlink(missing_ok=True)
                    else:
                        fp_path.parent.mkdir(parents=True, exist_ok=True)
                        fp_path.write_text(json.dumps(payload))
                    with patch.object(TARGET, 'load', return_value=fake_helper):
                        record = TARGET.audit(args)
                    self.assertEqual(record['evidence_complete'], expected_complete)
                    self.assertEqual(record['runner_exit'], 23)
                    self.assertEqual(record['failed_stage'], 'fingerprint')
                    self.assertIs(record['accepted'], False)
                    self.assertIs(record['proof_credit'], False)
                    self.assertEqual(record['fractional_fingerprint'], payload)
                    self.assertEqual(json.loads(output.read_text()), record)
            base['evidence_complete'] = False
            fp_path.write_text(json.dumps({'complete': True}))
            with patch.object(TARGET, 'load', return_value=fake_helper):
                record = TARGET.audit(args)
            self.assertFalse(record['evidence_complete'])


if __name__ == '__main__':
    unittest.main()
