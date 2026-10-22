#!/usr/bin/env python3
"""Synthetic adapter tests; no preparation, compiler, verifier, or Cloud."""
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
    'select_callee_r21_fractional_proof_entry_target',
    HERE / 'select-callee-r21-fractional-proof-entry.py')
assert SPEC and SPEC.loader
TARGET = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(TARGET)

ORIGINAL = b'// synthetic original\n'
BASE = b'// synthetic candidate base\n'
UNIT = b'synthetic unit default'
BODIES = [f'synthetic body {index}'.encode() for index in range(9)]
PHASE_KEY = 'SORT4_R20_CALLEE_PHASE_ID'
PHASE_VALUE = 'SORT4-ACTUAL-SELECT-2026-10-23-R22'


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class FakeProof:
    VARIANTS = ('positive', 'omit-selected-own', 'omit-unselected-own',
        'no-retained-half', 'callee-false-normal', 'callee-owner-duplicate',
        'callee-owner-loss', 'callee-thread-duplicate')

    def __init__(self, failure=False):
        self.failure = failure

    def require_route(self, env, phase_key, phase_value, opt_in_key):
        if (env.get('SMALLSORT_EXECUTION_PROVIDER') != 'cloud-build' or
                env.get(phase_key) != phase_value or 'GITHUB_ACTIONS' in env or
                opt_in_key in env or TARGET.R20_OPT_IN_KEY in env or
                TARGET.VARIANT_KEY in env):
            raise RuntimeError('bad synthetic route')

    def fingerprint_to_pins(self, record):
        if record.get('complete') is not True:
            raise RuntimeError('partial synthetic fingerprint')
        return {'schema': 'synthetic-pins-v1',
                'base_original_sha256': digest(ORIGINAL),
                'base_verified_sha256': digest(BASE),
                'snapshot_pins': {'unit': digest(UNIT),
                    **{f'body-{index}': digest(data)
                       for index, data in enumerate(BODIES)}}}

    def validate_pins(self, pins):
        return pins

    def proof_batch(self, **kw):
        case = kw['evidence'] / 'cases/r21-fractional-proof/variants/positive/nine-body-a1-owned-forget'
        (case / 'original').mkdir(parents=True)
        (case / 'verified').mkdir()
        (case / 'original/lib.rs').write_bytes(ORIGINAL)
        (case / 'verified/lib.rs').write_bytes(BASE)
        capture = kw['refusal_fingerprint']
        first = capture(case, {'verified_sha256': digest(BASE)}, SimpleNamespace())
        second = capture(case, {'verified_sha256': digest(BASE)}, SimpleNamespace())
        self.assert_archive = (first, second)
        self.assert_no_stale = not (case / 'actual-nested-9-body-1.marshal').exists()
        os.environ[TARGET.OPT_IN_KEY] = '1'
        try:
            stage = kw['proof_stage'](case=case, name='r20-merged-optin',
                tool_home=kw['tool_home'], schema=kw['schema'],
                compiler_sysroot=kw['compiler_sysroot'],
                deadline_epoch=kw['deadline_epoch'], variant='positive')
            self.stage_env = (os.environ.get(TARGET.OPT_IN_KEY),
                              os.environ.get(TARGET.R20_OPT_IN_KEY),
                              os.environ.get(TARGET.VARIANT_KEY))
        finally:
            os.environ.pop(TARGET.OPT_IN_KEY, None)
        proof_path = kw['evidence'] / 'cases/r21-fractional-proof/r21-fractional-proof.json'
        proof_path.parent.mkdir(parents=True, exist_ok=True)
        partial = {'classification': 'R21_FRACTIONAL_CLASSIFIED_PROOF_INCOMPLETE',
                   'complete': False, 'accepted': True, 'proof_credit': True,
                   'rows': {'positive': {'stage': stage}}}
        proof_path.write_text(json.dumps(partial))
        if self.failure:
            raise LookupError('synthetic original proof failure')
        return partial


class FakeCapture:
    def __init__(self):
        self.calls = 0
        self.clears = 0

    def clear_semantic_opt_ins(self):
        self.clears += 1

    def refusal_fingerprint(self, case, source, args):
        self.calls += 1
        expected = {}
        names = TARGET.SNAPSHOT_NAMES if self.calls == 1 else ('unit',)
        for label in names:
            data = ('synthetic-' + label).encode()
            path = case / f'actual-nested-9-{label}.marshal'
            path.write_bytes(data)
            expected[label] = {'file': path.name, 'bytes': len(data),
                               'sha256': digest(data)}
        (case / TARGET.CAPTURE_LOG).write_text(f'capture {self.calls}\n')
        return {'snapshots': expected, 'stage': {'status': 'RAN'},
                'body_proof_run': False}


class FakeO26:
    def __init__(self):
        self.calls = []
        self.seen_env = None

    def proof_stage(self, repo, case, tool_home, schema, sysroot,
                    deadline, name, label):
        self.calls.append((repo, case, name, label))
        self.seen_env = (os.environ.get(TARGET.OPT_IN_KEY),
                         os.environ.get(TARGET.R20_OPT_IN_KEY),
                         os.environ.get(TARGET.VARIANT_KEY))
        return {'status': 'RAN', 'exit': 2}


class FakeProvider:
    def __init__(self, provider='cloud-build'):
        self.calls = 0
        self.provider = provider

    def require_supported_provider(self):
        self.calls += 1
        return {'provider': self.provider}


class EntryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.evidence = self.root / 'evidence'
        self.base = self.evidence / 'cases/candidate/capture' / TARGET.CASE
        (self.base / 'original').mkdir(parents=True)
        (self.base / 'verified').mkdir()
        (self.base / 'original/lib.rs').write_bytes(ORIGINAL)
        (self.base / 'verified/lib.rs').write_bytes(BASE)
        self.pins = self.root / 'fingerprint.json'
        self.pins.write_text(json.dumps({'complete': True}))
        self.args = SimpleNamespace(repo=self.root, cloud_dir=self.root,
            evidence=self.evidence, tool_home=Path('/fake/tool'),
            schema=Path('/fake/schema'), compiler_sysroot=Path('/fake/sysroot'),
            deadline_epoch=int(time.time()) + 3600, pins_json=self.pins)
        self.env = {'SMALLSORT_EXECUTION_PROVIDER': 'cloud-build',
                    PHASE_KEY: PHASE_VALUE}
        self.capture = FakeCapture()
        self.o26 = FakeO26()
        self.proof = FakeProof()
        self.provider = FakeProvider()
        self.runtime = {'fractional': SimpleNamespace(
                require_cloud=lambda env: TARGET.need(
                    env.get('SMALLSORT_EXECUTION_PROVIDER') == 'cloud-build' and
                    env.get(PHASE_KEY) == PHASE_VALUE and 'GITHUB_ACTIONS' not in env,
                    'synthetic Cloud route'),
                PHASE_ENV=PHASE_KEY, PHASE=PHASE_VALUE,
                TRANSFORM_REL=Path('transform.py'),
                TRANSFORM_REPAIR_SHA256='repair',
                TRANSFORM_CONTROLS_SHA256='controls', R20_HELPER_SHA256='r20',
                O26_RECIPE_SHA256='o26', O26_REFRESH_SHA256='refresh',
                CAPTURE_SHA256='capture'),
            'proof': self.proof,
            'transform': SimpleNamespace(transform=lambda source, variant: source),
            'r20': SimpleNamespace(), 'o26': self.o26,
            'refresh': SimpleNamespace(UNIT=digest(UNIT),
                BODIES=tuple(digest(data) for data in BODIES)),
            'capture': self.capture, 'provider': self.provider}

    def tearDown(self):
        self.temp.cleanup()

    def run_entry(self, *, failure=False, env=None):
        if failure:
            self.proof.failure = True
        with patch.dict(os.environ, self.env if env is None else env, clear=True):
            return TARGET.run(self.args, runtime_loader=lambda *_: self.runtime,
                              env=self.env if env is None else env)

    def test_adapter_sets_per_call_optins_and_archives_fresh_capture_outputs(self):
        record = self.run_entry()
        self.assertEqual(self.provider.calls, 1)
        self.assertFalse(record['complete'])
        self.assertIs(record['accepted'], False)
        self.assertIs(record['proof_credit'], False)
        row = record['rows']['positive']['stage']
        self.assertEqual(row['exit'], 2)
        first, second = self.proof.assert_archive
        self.assertIn('capture_archive', first)
        self.assertIn('capture_archive', second)
        self.assertIsNone(second['snapshots'].get('body-1'))
        self.assertTrue(self.proof.assert_no_stale)
        self.assertEqual(self.o26.seen_env, ('1', '1', 'positive'))
        self.assertNotIn(TARGET.R20_OPT_IN_KEY, os.environ)
        self.assertNotIn(TARGET.VARIANT_KEY, os.environ)
        self.assertEqual(len(record['capture_archive_records']), 2)
        archived = record['capture_archive_records'][0]
        self.assertEqual(archived['files']['unit']['sha256'], digest(b'synthetic-unit'))
        self.assertIsNone(record['capture_archive_records'][1]['files']['body-1']['sha256'])

    def test_non_cloud_provider_is_rejected_before_capture_or_proof(self):
        self.provider = FakeProvider('github-hosted')
        self.runtime['provider'] = self.provider
        with self.assertRaisesRegex(RuntimeError, 'actual supported Cloud Build provider'):
            self.run_entry()
        self.assertEqual(self.provider.calls, 1)
        self.assertEqual(self.capture.calls, 0)
        self.assertEqual(self.o26.calls, [])

    def test_original_proof_exception_is_preserved_and_record_remains_unaccepted(self):
        with self.assertRaisesRegex(LookupError, 'synthetic original proof failure'):
            self.run_entry(failure=True)
        path = self.evidence / 'cases/r21-fractional-proof/r21-fractional-proof.json'
        record = json.loads(path.read_text())
        self.assertIs(record['complete'], False)
        self.assertIs(record['accepted'], False)
        self.assertIs(record['proof_credit'], False)
        self.assertIn('entry_dependencies', record)
        self.assertEqual(len(record['capture_archive_records']), 2)

    def test_bad_route_and_base_source_fail_before_proof(self):
        bad = {**self.env, PHASE_KEY: 'wrong'}
        with self.assertRaisesRegex(RuntimeError, 'fresh R22 Cloud proof phase'):
            self.run_entry(env=bad)
        ambient = {**self.env, TARGET.OPT_IN_KEY: '1'}
        with self.assertRaisesRegex(RuntimeError, 'must not be ambient'):
            self.run_entry(env=ambient)
        self.base.joinpath('verified/lib.rs').write_bytes(b'different source')
        with self.assertRaisesRegex(RuntimeError, 'differs from pinned fingerprint'):
            self.run_entry()

    def test_incomplete_pins_fail_before_proof(self):
        self.pins.write_text(json.dumps({'complete': False}))
        with self.assertRaisesRegex(RuntimeError, 'partial synthetic fingerprint'):
            self.run_entry()

    def test_pinned_module_loader_rejects_source_hash_mismatch(self):
        path = self.root / 'module.py'
        path.write_text('VALUE = 1\n')
        with self.assertRaisesRegex(RuntimeError, 'pinned module differs'):
            TARGET.load(path, 'synthetic_bad_pin', '0' * 64)

    def test_entry_pin_matches_reviewed_proof_helper_bytes(self):
        helper = HERE / 'select-callee-r21-fractional-proof.py'
        self.assertEqual(TARGET.sha(helper.read_bytes()), TARGET.PROOF_HELPER_SHA256)


if __name__ == '__main__':
    unittest.main()
