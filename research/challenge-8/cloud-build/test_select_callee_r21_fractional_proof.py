#!/usr/bin/env python3
"""Synthetic-only tests for the inactive fractional proof classifier."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    'select_callee_r21_fractional_proof_target',
    HERE / 'select-callee-r21-fractional-proof.py')
assert SPEC and SPEC.loader
TARGET = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(TARGET)
R20_SPEC = importlib.util.spec_from_file_location(
    'select_callee_r20_fractional_test', HERE / 'select-callee-r20.py')
assert R20_SPEC and R20_SPEC.loader
R20 = importlib.util.module_from_spec(R20_SPEC)
R20_SPEC.loader.exec_module(R20)

ORIGINAL = b'// original synthetic Rust source\n'
BASE = (b'// verified synthetic owner-projection source\n'
        b'pub unsafe fn checked_forget_owned<T>(t: T)\n'
        b'{\n    let _ = ManuallyDrop::new(t);\n}')
FINAL_SELECT_CALL = TARGET.FINAL_SELECT_CALL
UNIT = b'synthetic unit mode9 bytes'
BODIES = [f'synthetic mode9 body {i}'.encode() for i in range(9)]
OPT_IN = 'SORT4_R21_FRACTIONAL_TEST'
PHASE_KEY = 'SORT4_R20_CALLEE_PHASE_ID'
PHASE_VALUE = 'SORT4-ACTUAL-SELECT-2026-10-23-R21'


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def source_for(variant: str) -> bytes:
    return BASE + f'// {variant}\n'.encode() + FINAL_SELECT_CALL


def snapshot_rows(case: Path) -> dict:
    result = {}
    for name, data in [('unit', UNIT), *((f'body-{i}', b) for i, b in enumerate(BODIES))]:
        filename = f'actual-nested-9-{name}.marshal'
        (case / filename).write_bytes(data)
        result[name] = {'file': filename, 'bytes': len(data), 'sha256': digest(data)}
    return result


def fingerprint_fixture() -> dict:
    default = {'unit': digest(UNIT),
               **{f'body-{i}': digest(data) for i, data in enumerate(BODIES)}}
    rows = {}
    for variant in TARGET.VARIANTS:
        variant_snapshots = {name: {'file': f'actual-nested-9-{name}.marshal',
            'bytes': len(data), 'sha256': digest(data)}
            for name, data in [('unit', UNIT),
                *((f'body-{i}', b) for i, b in enumerate(BODIES))]}
        rows[variant] = {
            'status': 'COMPLETE', 'source_intact_after_stages': True,
            'original_preserved': True, 'original_sha256': digest(ORIGINAL),
            'verified_sha256': digest(source_for(variant)),
            'fingerprint': {'body_proof_run': False,
                'stage': {'status': 'RAN', 'exit': 2,
                    'source_before': {'original/lib.rs': digest(ORIGINAL),
                                      'verified/lib.rs': digest(source_for(variant))},
                    'source_after': {'original/lib.rs': digest(ORIGINAL),
                                     'verified/lib.rs': digest(source_for(variant))},
                    'source_unchanged': True,
                    'intrinsic_gate_active': False,
                    'pointer_drop_gate_active': False,
                    'stdout': 'nine-body-fingerprint-refusal.log',
                    'stderr': 'nine-body-fingerprint-refusal.log'},
                'expected_refusal_seen': True, 'all_ten_snapshots': True,
                'snapshots': variant_snapshots},
            'fingerprint_check': {'complete': True,
                                  'snapshots_match_default_pins': True},
            'normal_mir_check': {'complete': True},
        }
    location_snapshots = {name: {'file': f'actual-nested-9-{name}.marshal',
        'bytes': len(data), 'sha256': digest(data)}
        for name, data in [('unit', UNIT),
            *((f'body-{i}', b) for i, b in enumerate(BODIES))]}
    return {'schema': 'r21-fractional-forget-fingerprint-v1', 'complete': True,
        'accepted': False, 'proof_credit': False, 'body_proof_run': False,
        'variant_order': list(TARGET.VARIANTS),
        'base_source': {'original_sha256': digest(ORIGINAL),
                        'verified_sha256': digest(BASE)},
        'snapshot_pins': default, 'variants': rows,
        'location_control': {'reproduces_pinned': True,
            'source_intact_after_stages': True,
            'fingerprint_check': {'complete': True,
                                  'snapshots_match_default_pins': True},
            'fingerprint': {'classification': TARGET.EXPECTED_REFUSAL,
                'expected_refusal_seen': True, 'all_ten_snapshots': True,
                'body_proof_run': False, 'snapshots': location_snapshots}}}


class FakeCapture:
    def refusal_fingerprint(self, case: Path, source: dict, args):
        snapshots = snapshot_rows(case)
        original = (case / 'original/lib.rs').read_bytes()
        verified = (case / 'verified/lib.rs').read_bytes()
        return {'classification': TARGET.EXPECTED_REFUSAL,
            'expected_refusal_seen': True, 'all_ten_snapshots': True,
            'body_proof_run': False, 'snapshots': snapshots,
            'stage': {'status': 'RAN', 'exit': 2,
                'argv': [str(args.tool_home / 'bin/verifast'), '-rustc_args',
                         '--edition 2021', '-verbose', '1', 'verified/lib.rs'],
                'source_before': {'original/lib.rs': digest(original),
                                  'verified/lib.rs': digest(verified)},
                'source_after': {'original/lib.rs': digest(original),
                                 'verified/lib.rs': digest(verified)},
                'source_unchanged': True,
                'intrinsic_gate_active': False,
                'pointer_drop_gate_active': False,
                'stdout': 'nine-body-fingerprint-refusal.log',
                'stderr': 'nine-body-fingerprint-refusal.log'}}


class FractionalProofTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.evidence = self.root / 'evidence'
        self.tool_home = Path('/synthetic/tool')
        self.env = {'SMALLSORT_EXECUTION_PROVIDER': 'cloud-build',
                    PHASE_KEY: PHASE_VALUE}

    def tearDown(self):
        self.tmp.cleanup()

    def run_batch(self, *, proof_stage=None, capture=None, deadline=None,
                  env=None):
        with patch.dict('os.environ', env or self.env, clear=True):
            return TARGET.proof_batch(evidence=self.evidence,
            original=ORIGINAL, base_verified=BASE,
            fingerprint_record=fingerprint_fixture(),
            transform=lambda _base, variant: source_for(variant), r20=R20,
            proof_stage=proof_stage or self.good_proof_stage,
            refusal_fingerprint=capture or FakeCapture().refusal_fingerprint,
            tool_home=self.tool_home, schema=Path('/synthetic/schema'),
            compiler_sysroot=Path('/synthetic/sysroot'),
            deadline_epoch=deadline or int(time.time()) + 3600,
            phase_key=PHASE_KEY, phase_value=PHASE_VALUE,
            opt_in_key=OPT_IN, env=env or self.env)

    def good_proof_stage(self, *, case: Path, name: str, tool_home: Path,
                         schema: Path, compiler_sysroot: Path,
                         deadline_epoch: int, variant: str):
        self.assertEqual(__import__('os').environ.get(OPT_IN), '1')
        if variant == 'positive':
            exit_code = 0
            log = 'verified: all normal, unwind, and nested Drop obligations discharged\n'
        elif variant in TARGET.SAME_SITE_NEGATIVES:
            exit_code = 1
            source = (case / 'verified/lib.rs').read_bytes()
            target = TARGET._final_select_target(source)
            log = (f"{target['file']}({target['line']},"
                   f"{target['start_column']}-{target['end_column']}): "
                   f"{target['message']}\n")
        else:
            exit_code = 1
            log = ('verified/lib.rs(5,1-2): error: unrelated failure\n'
                   'checked_forget_owned appears in context only\n')
        (case / 'r20-merged-optin.log').write_text(log)
        original = (case / 'original/lib.rs').read_bytes()
        verified = (case / 'verified/lib.rs').read_bytes()
        return {'status': 'RAN', 'exit': exit_code,
            'argv': [str(tool_home / 'bin/verifast'), '-rustc_args',
                     '--edition 2021', '-verbose', '1', 'verified/lib.rs'],
            'source_before': {'original/lib.rs': digest(original),
                              'verified/lib.rs': digest(verified)},
            'source_after': {'original/lib.rs': digest(original),
                             'verified/lib.rs': digest(verified)},
            'source_unchanged': True, 'intrinsic_gate_active': True,
            'pointer_drop_gate_active': True, 'stdout': 'r20-merged-optin.log',
            'stderr': 'r20-merged-optin.log'}

    def test_positive_and_same_site_controls_classify_but_callee_targets_stay_unpinned(self):
        self.assertEqual(TARGET.FINAL_SELECT_MESSAGE,
            'error: Cannot prove condition. '
            '(Cannot prove result6 = (condition ? true_val : false_val).)')
        record = self.run_batch()
        self.assertFalse(record['complete'])
        self.assertIs(record['accepted'], False)
        self.assertIs(record['proof_credit'], False)
        self.assertIs(record['body_proof_run'], True)
        self.assertEqual(record['rows']['positive']['classification'],
                         'POSITIVE_VERIFIED_SOURCE_REPORTED')
        for variant in TARGET.SAME_SITE_NEGATIVES:
            self.assertEqual(record['rows'][variant]['classification'],
                             'EXPECTED_SAME_SITE_FINAL_SELECT_FAILURE')
            target = record['rows'][variant]['expected_diagnostic_target']
            self.assertEqual(target['file'], 'verified/lib.rs')
            self.assertEqual(target['line'],
                source_for(variant)[:source_for(variant).index(FINAL_SELECT_CALL)].count(b'\n') + 1)
        for variant in TARGET.CALLEE_NEGATIVES:
            self.assertEqual(record['rows'][variant]['classification'],
                             'TARGET_UNPINNED')
            self.assertEqual(record['rows'][variant]['status'], 'INCOMPLETE')

    def test_fingerprint_to_pins_rejects_partial_and_malformed_per_case_data(self):
        record = fingerprint_fixture()
        self.assertEqual(TARGET.fingerprint_to_pins(record)['schema'], TARGET.SCHEMA)
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'fingerprint.json'
            source.write_text(json.dumps(record))
            self.assertEqual(TARGET.load_fingerprint_pins(source),
                             TARGET.fingerprint_to_pins(record))
        bad_cases = []
        partial = json.loads(json.dumps(record))
        partial['variants']['positive']['status'] = 'INCOMPLETE'
        bad_cases.append(partial)
        malformed = json.loads(json.dumps(record))
        malformed['variants']['positive']['fingerprint']['snapshots'].pop('body-8')
        bad_cases.append(malformed)
        for malformed_row in (None, [], {'file': None, 'bytes': 0, 'sha256': None},
                              {'file': 'actual-nested-9-unit.marshal',
                               'bytes': 'wrong', 'sha256': 'x'}):
            malformed = json.loads(json.dumps(record))
            malformed['variants']['positive']['fingerprint']['snapshots']['unit'] = malformed_row
            bad_cases.append(malformed)
        wrong_location = json.loads(json.dumps(record))
        wrong_location['location_control']['fingerprint']['snapshots']['body-0']['sha256'] = '0' * 64
        bad_cases.append(wrong_location)
        mismatch = json.loads(json.dumps(record))
        mismatch['variants']['positive']['verified_sha256'] = '0' * 64
        bad_cases.append(mismatch)
        for item in bad_cases:
            with self.subTest(item=item['variants']['positive']['status']), \
                    self.assertRaises(RuntimeError):
                TARGET.fingerprint_to_pins(item)

    def test_case_snapshot_maps_are_distinct_but_baseline_control_matches_defaults(self):
        record = fingerprint_fixture()
        expected = record['snapshot_pins']
        for index, variant in enumerate(TARGET.VARIANTS):
            snapshots = record['variants'][variant]['fingerprint']['snapshots']
            for changed in ('unit', 'body-6', 'body-7'):
                snapshots[changed]['sha256'] = digest(f'{variant}-{changed}'.encode())
            record['variants'][variant]['fingerprint_check'][
                'snapshots_match_default_pins'] = False
        pins = TARGET.fingerprint_to_pins(record)
        self.assertEqual(pins['snapshot_pins'], expected)
        for variant in TARGET.VARIANTS:
            snapshots = pins['cases'][variant]['snapshots']
            self.assertNotEqual(snapshots['body-6']['sha256'], expected['body-6'])
            self.assertNotEqual(snapshots['body-7']['sha256'], expected['body-7'])
            self.assertEqual(snapshots['body-0']['sha256'], expected['body-0'])
            self.assertEqual(snapshots['body-8']['sha256'], expected['body-8'])
        self.assertEqual(TARGET.validate_pins(pins), pins)

        # The location control remains the baseline anchor and cannot silently
        # inherit variant-specific unit/body snapshots.
        record['location_control']['fingerprint']['snapshots']['body-6']['sha256'] = '0' * 64
        with self.assertRaisesRegex(RuntimeError, 'location-control unit/body hashes'):
            TARGET.fingerprint_to_pins(record)

    def test_capture_partial_null_wrongtype_and_not_run_stay_inconclusive(self):
        pins = TARGET.fingerprint_to_pins(fingerprint_fixture())['cases']['positive']['snapshots']
        tool = self.tool_home
        with tempfile.TemporaryDirectory() as tmp:
            case = Path(tmp)
            (case / 'original').mkdir()
            (case / 'verified').mkdir()
            (case / 'original/lib.rs').write_bytes(ORIGINAL)
            (case / 'verified/lib.rs').write_bytes(source_for('positive'))
            for name, payload in (('null', None), ('wrong-type', []),
                ('not-run', {'stage': {'status': 'NOT_RUN_DEADLINE'},
                             'snapshots': {}, 'body_proof_run': False}),
                ('partial', {'stage': {'status': 'RAN'}, 'snapshots': {'unit': {}},
                             'body_proof_run': False})):
                with self.subTest(name=name):
                    check = TARGET._validate_capture(payload, case, digest(ORIGINAL),
                        digest(source_for('positive')), pins, tool)
                    self.assertFalse(check['complete'])

    def test_stage_target_mismatch_and_not_run_are_incomplete(self):
        def bad_stage(**kw):
            row = self.good_proof_stage(**kw)
            row['argv'][-1] = 'original/lib.rs'
            (kw['case'] / 'r20-merged-optin.log').write_text(
                'verified: no error\n')
            return row
        record = self.run_batch(proof_stage=bad_stage)
        self.assertFalse(record['complete'])
        self.assertEqual(record['rows']['positive']['bound_verdict'],
                         'SOURCE_STAGE_TARGET_MISMATCH')

        def not_run(**kw):
            row = self.good_proof_stage(**kw)
            row.update(status='NOT_RUN_DEADLINE', exit=None)
            return row
        # Use a fresh evidence root while retaining a valid phase/source fixture.
        self.evidence = self.root / 'not-run-evidence'
        record = self.run_batch(proof_stage=not_run)
        self.assertFalse(record['complete'])
        self.assertEqual(record['rows']['positive']['bound_verdict'],
                         'NOT_RUN_OR_INCONCLUSIVE')

    def test_deadline_before_any_stage_keeps_body_proof_run_false(self):
        record = self.run_batch(deadline=int(time.time()) + 2)
        self.assertFalse(record['complete'])
        self.assertIs(record['body_proof_run'], False)
        self.assertTrue(all(row['status'] == 'NOT_RUN'
                            for row in record['rows'].values()))

    def test_decoy_logs_cannot_confirm_control_target(self):
        variant = 'omit-selected-own'
        case = self.evidence / 'decoy' / 'nine-body-a1-owned-forget'
        (case / 'original').mkdir(parents=True)
        (case / 'verified').mkdir()
        candidate = source_for(variant)
        (case / 'original/lib.rs').write_bytes(ORIGINAL)
        (case / 'verified/lib.rs').write_bytes(candidate)
        target = TARGET._final_select_target(candidate)
        expected = (f"{target['file']}({target['line']},"
                    f"{target['start_column']}-{target['end_column']}): "
                    f"{target['message']}")
        source_hashes = {'original/lib.rs': digest(ORIGINAL),
                         'verified/lib.rs': digest(candidate)}
        with patch.dict('os.environ', {**self.env, OPT_IN: '1'}, clear=True):
            stage = self.good_proof_stage(case=case, name='r20-merged-optin',
                tool_home=self.tool_home, schema=Path('/synthetic/schema'),
                compiler_sysroot=Path('/synthetic/sysroot'),
                deadline_epoch=int(time.time()) + 3600, variant=variant)
        decoy_logs = (
            expected + '\nverified/lib.rs(999,1-2): error: unrelated failure\n',
            expected + '\n' + expected + '\n',
            expected.replace(f"({target['line']},", '(999,') + '\n',
        )
        for log in decoy_logs:
            with self.subTest(log=log):
                self.assertEqual(TARGET._classify(R20, variant, stage, log,
                    source_hashes, source_hashes, self.tool_home, candidate)[1],
                    'CONTROL_FAILURE_TARGET_MISMATCH')

        callee_variant = 'callee-false-normal'
        callee_stage = dict(stage, exit=1)
        callee_log = ('verified/lib.rs(5,1-2): error: unrelated failure\n'
                      'checked_forget_owned appears in a note\n')
        self.assertEqual(TARGET._classify(R20, callee_variant, callee_stage,
            callee_log, source_hashes, source_hashes, self.tool_home,
            candidate)[1], 'TARGET_UNPINNED')

    def test_postflight_snapshot_mismatch_is_saved_as_incomplete(self):
        capture = FakeCapture()
        counts = {}

        def mutate_second_capture(case, source, args):
            result = capture.refusal_fingerprint(case, source, args)
            counts[case] = counts.get(case, 0) + 1
            if case.parent.name == 'positive' and counts[case] == 2:
                (case / 'actual-nested-9-body-8.marshal').write_bytes(b'changed bytes')
            return result

        record = self.run_batch(capture=mutate_second_capture)
        self.assertFalse(record['complete'])
        positive = record['rows']['positive']
        self.assertEqual(positive['status'], 'INCOMPLETE')
        self.assertFalse(positive['postflight_capture_check']['complete'])
        self.assertIn('body-8: snapshot pin or physical bytes mismatch',
                      positive['postflight_capture_check']['errors'])

    def test_original_exception_is_saved_then_propagated(self):
        def broken(**_kw):
            raise LookupError('synthetic proof-stage failure')
        with self.assertRaisesRegex(LookupError, 'synthetic proof-stage failure'):
            self.run_batch(proof_stage=broken)
        record = json.loads((self.evidence / 'cases/r21-fractional-proof' /
                             'r21-fractional-proof.json').read_text())
        self.assertEqual(record['rows']['positive']['exception_type'], 'LookupError')
        self.assertIn('synthetic proof-stage failure',
                      record['rows']['positive']['exception'])
        self.assertEqual(record['terminal_exception']['type'], 'LookupError')
        self.assertIs(record['proof_credit'], False)

    def test_provider_phase_and_ambient_optins_refuse(self):
        for env in ({**self.env, 'SMALLSORT_EXECUTION_PROVIDER': 'github-actions'},
                    {**self.env, PHASE_KEY: 'old'},
                    {**self.env, R20.R20_FLAG: '1'},
                    {**self.env, 'SORT4_R21_FRACTIONAL_OTHER': '1'}):
            with self.subTest(env=env), self.assertRaises(RuntimeError):
                TARGET.require_route(env, PHASE_KEY, PHASE_VALUE, OPT_IN)


if __name__ == '__main__':
    unittest.main()
