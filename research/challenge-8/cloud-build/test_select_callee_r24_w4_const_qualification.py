import argparse
from contextlib import ExitStack
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest import mock


HERE = Path(__file__).resolve().parent
SCRIPT = HERE / 'select-callee-r24-w4-const-qualification.py'
SPEC = importlib.util.spec_from_file_location('r24_w4_const_qualification_tested', SCRIPT)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


class ConsequenceFake:
    SUMMARY_REL = Path('cases/r24-w4-const-consequence/W4-CONST-CONSEQUENCE.json')

    def run(self, args, *, const_matrix_summary=None, const_matrix_audit=None, **kwargs):
        return {'complete': True, 'accepted': False,
                'body_proof_run': True, 'call_linkage': 'UNKNOWN',
                'publication_allowed': False, 'proof_credit': 0,
                'matrix_summary': const_matrix_summary is not None,
                'matrix_audit': const_matrix_audit is not None}

    def audit(self, args, *, const_matrix_summary=None, const_matrix_audit=None,
              runner_exit=0, failed_stage='complete', **kwargs):
        return {'complete': True, 'evidence_complete': True,
                'accepted': False, 'proof_credit': 0}


def matrix_record(native_home=None):
    variants = {}
    for variant in MOD.VARIANTS:
        same_site = variant in {'omit-selected-own', 'omit-unselected-own', 'no-retained-half'}
        variants[variant] = {
            'variant': variant, 'status': 'COMPLETE',
            'classification': ('POSITIVE_VERIFIED_SOURCE_REPORTED' if variant == 'positive' else
                               'EXPECTED_SAME_SITE_TYPED_FAILURE' if same_site else
                               'EXPECTED_CALLEE_CONTRACT_REJECTION'),
            'normal_unwind_nested_drop_gates': True,
            'current_stage_observation': {'status': 'RAN', 'exit': 0 if variant == 'positive' else 1,
                                          'source_unchanged': True,
                                          'argv': ([str(native_home / 'bin/verifast'), '-rustc_args',
                                                    '--edition 2021', '-verbose', '1', 'verified/lib.rs']
                                                   if native_home else [])},
        }
    return {'schema': 'r21-fractional-classified-proof-v1',
            'complete': True, 'variant_order': list(MOD.VARIANTS),
            'body_proof_run': True,
            'rows': variants, 'pins': {'base_original_sha256': MOD.CONST_ORIGINAL_SHA256,
                                       'base_verified_sha256': MOD.CONST_BASE_VERIFIED_SHA256},
            'tool_home': str(native_home) if native_home else None,
            'current_build_id': 'build-uuid', 'checked_pointer_outcomes_requested': True,
            'accepted': False, 'proof_credit': False}


class FakeCommandRunner:
    def __init__(self, fail=None, result=None, throw=None, native_home=None,
                 omit_output=None, dirty_after=None):
        self.fail = fail
        self.result = result
        self.throw = throw
        self.native_home = native_home
        self.omit_output = omit_output
        self.dirty_after = dirty_after
        self.calls = []

    def __call__(self, name, argv, *, cwd, env, deadline):
        self.calls.append((name, argv))
        if name == self.throw:
            raise RuntimeError('injected stage exception')
        if name == self.omit_output:
            return {'status': 'RAN', 'exit': 0, 'stdout': '', 'stderr': ''}
        if name == self.fail:
            return self.result or {'status': 'RAN', 'exit': 1, 'stdout': 'stage out', 'stderr': 'stage err'}
        work = Path(argv[argv.index('--evidence') + 1]) if '--evidence' in argv else None
        if name == 'source-preflight':
            work.mkdir(parents=True, exist_ok=True)
            data = {'source_generation_complete': True,
                    'source': {'original_sha256': MOD.CONST_ORIGINAL_SHA256,
                               'verified_sha256': MOD.CONST_BASE_VERIFIED_SHA256,
                               'ghost_strip_identity': True}}
            (work / 'source-preflight.json').write_text(json.dumps(data))
        elif name == 'candidate-capture':
            root = work / 'nine-body-a1-owned-forget'
            source = {'original_sha256': MOD.CONST_ORIGINAL_SHA256,
                      'verified_sha256': MOD.CONST_BASE_VERIFIED_SHA256,
                      'ghost_strip_identity': True}
            for variant, content in (('original', b'orig'), ('verified', b'verified')):
                raw = content
                source[variant + '_sha256'] = sha(raw)
                p = root / variant / 'lib.rs'
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(raw)
            data = {'frontend_refinement_and_full_body_capture': True,
                    'actual_helper_proved': False, 'source': source}
            (work / 'summary.json').write_text(json.dumps(data))
        elif name == 'candidate-source-compare':
            (work / 'cases/candidate/capture-compare.json').write_text(
                json.dumps({'capture_complete': True}))
        elif name == 'candidate-proof':
            case = work / 'cases/candidate/capture/nine-body-a1-owned-forget'
            (case / 'refreshed-proof.log').write_text('baseline verifier result')
            (work / 'cases/candidate/proof-stage.json').write_text(json.dumps({
                'stage': {'status': 'RAN', 'exit': 1, 'source_unchanged': True,
                          'argv': [str(self.native_home / 'bin/verifast'), '-rustc_args',
                                   '--edition 2021', '-verbose', '1', 'verified/lib.rs'],
                          'stdout': 'refreshed-proof.log', 'stderr': 'refreshed-proof.log',
                          'source_before': {'original/lib.rs': MOD.CONST_ORIGINAL_SHA256,
                                            'verified/lib.rs': MOD.CONST_BASE_VERIFIED_SHA256},
                          'source_after': {'original/lib.rs': MOD.CONST_ORIGINAL_SHA256,
                                           'verified/lib.rs': MOD.CONST_BASE_VERIFIED_SHA256}},
                'actual_verification_accepted': False}))
            if self.dirty_after == name:
                (work / 'cases/candidate/capture/nine-body-a1-owned-forget/verified/lib.rs').write_bytes(b'dirty')
        elif name == 'r21-fractional-proof':
            path = work / MOD.CONST_MATRIX_REPORT_REL
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(matrix_record(self.native_home)))
        elif name == 'const-regression-audit':
            path = work / MOD.CONST_MATRIX_AUDIT_REL
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps({'evidence_complete': True, 'accepted': False,
                                        'verification_accepted': False, 'proof_credit': False}))
        return {'status': 'RAN', 'exit': 0, 'stdout': 'synthetic stdout', 'stderr': ''}


class FrozenAuditFake:
    def compare(self, evidence):
        return None

    def audit(self, args):
        value = json.loads((args.evidence / MOD.CONST_MATRIX_AUDIT_REL).read_text())
        args.output.write_text(json.dumps(value))
        return value


class QualificationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.args = argparse.Namespace(
            repo=self.root / 'repo', cloud_dir=self.root / 'cloud',
            evidence=self.root / 'evidence', tool_home=self.root / 'tool8a',
            native_tool_home=self.root / 'tool5170',
            schema=self.root / 'tool5170/src/rust_frontend/vf_mir/vf_mir.capnp',
            compiler_sysroot=self.root / 'sysroot', deadline_epoch=4_000_000_000,
            candidate='a' * 40, capture_mode_file=self.root / 'mode-capture.json',
            mode_file=self.root / 'mode-new.json')
        self.args.evidence.mkdir(parents=True)
        self.args.repo.mkdir()
        self.args.cloud_dir.mkdir()
        self.args.tool_home.mkdir()
        self.args.native_tool_home.mkdir()
        self.env = dict(os.environ)
        self.env.update({MOD.R24_PHASE_ENV: MOD.R24_PHASE, MOD.R21_PHASE_ENV: MOD.R21_PHASE,
                         'SMALLSORT_EXECUTION_PROVIDER': 'cloud-build',
                         'SORT4_SELECT_PROFILE': MOD.PROFILE, 'LANE': MOD.LANE,
                         'CLOUD_BUILD_ID': 'build-uuid'})
        self.original = b'orig'
        self.verified = b'verified'
        self.old_digest = {'old-tool': 'old'}
        self.native_digest = {'bin/verifast': {'regular': True, 'sha256': 'native',
                                               'bytes': 1, 'expected_sha256': 'native',
                                               'matches': True}}

    def tearDown(self):
        self.tmp.cleanup()

    def patched(self):
        patches = [
            mock.patch.object(MOD, '_context'),
            mock.patch.object(MOD, '_mode', return_value={}),
            mock.patch.object(MOD, '_validate_pins', return_value={}),
            mock.patch.object(MOD, '_tool_identity', return_value=self.old_digest),
            mock.patch.object(MOD, '_read_native_files', return_value=self.native_digest),
            mock.patch.object(MOD, 'TOOL_HASHES_8A', {'old-tool': 'old'}),
            mock.patch.object(MOD, 'NATIVE_TOOL_HASHES', {'bin/verifast': 'native'}),
            mock.patch.object(MOD, 'CONST_ORIGINAL_SHA256', sha(self.original)),
            mock.patch.object(MOD, 'CONST_BASE_VERIFIED_SHA256', sha(self.verified)),
        ]
        stack = ExitStack()
        for patcher in patches: stack.enter_context(patcher)
        return stack

    def test_unmocked_canonical_mode_and_pinned_inputs_accept_synthetic_overlay(self):
        repo = self.root / 'pinned-repo'
        evidence = self.root / 'pinned-evidence'
        repo.mkdir()
        evidence.mkdir()
        source_repo = HERE.parents[2]
        json_inputs = (MOD.CAPTURE_MODE_REL, MOD.CAPTURE_PINS_REL,
                       MOD.NATIVE_FINGERPRINT_PINS_REL, MOD.W4_INPUTS_REL,
                       MOD.CONST_QUALIFICATION_REL, MOD.P2_INTERFACE_REL,
                       MOD.FRACTIONAL_PINS_REL, MOD.TARGET_MAP_REL, MOD.MODE_REL,
                       MOD.O26_PROVIDER_REL)
        for rel in json_inputs:
            destination = repo / rel
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source_repo / rel, destination)
        recipe_path = source_repo / MOD.O26_BASE_REL
        spec = importlib.util.spec_from_file_location('test_o26_base_recipe', recipe_path)
        o26 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(o26)
        overlay_rows = []
        for relative, (original_sha, overlaid_sha) in MOD.O26_OVERLAY_FILES.items():
            relative_path = Path(relative)
            raw = (source_repo / relative_path).read_text()
            self.assertEqual(sha(raw.encode()), original_sha)
            matches = [guard for guard in o26.GUARD_VARIANTS if raw.count(guard) == 1]
            self.assertEqual(len(matches), 1)
            overlaid = raw.replace(matches[0], '_o26_cloud_provider_ok()', 1)
            overlaid = overlaid.replace('from pathlib import Path\n',
                                        'from pathlib import Path\n' + o26.HELPER, 1)
            self.assertEqual(sha(overlaid.encode()), overlaid_sha)
            destination = repo / relative_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(overlaid)
            overlay_rows.append({'path': relative, 'original_sha256': original_sha,
                                 'cloud_overlay_sha256': overlaid_sha, 'guard_only': True})
        (evidence / 'candidate-provider-overlay.json').write_text(json.dumps({
            'proof_sha': 'a' * 40, 'provider_sha256': MOD.O26_PROVIDER_SHA256,
            'files': overlay_rows}))
        args = argparse.Namespace(
            repo=repo, cloud_dir=HERE, evidence=evidence,
            tool_home=self.root / 'frozen8a', native_tool_home=self.root / 'native5170',
            schema=self.root / 'native5170/src/rust_frontend/vf_mir/vf_mir.capnp',
            compiler_sysroot=self.root / 'sysroot', deadline_epoch=4_000_000_000,
            candidate='a' * 40, capture_mode_file=repo / MOD.CAPTURE_MODE_REL,
            mode_file=repo / MOD.MODE_REL)
        self.assertEqual(MOD._mode(args), MOD.expected_mode())
        pins = MOD._validate_pins(args)
        self.assertEqual(pins['w4_inputs']['native_body_inventory'], ['sort4_stable'])
        self.assertEqual(pins['cloud_overlay']['proof_sha'], args.candidate)

    def test_service_composition_success_records_all_routes_false(self):
        with self.patched(), mock.patch.dict(os.environ, self.env, clear=True):
            runner = FakeCommandRunner(native_home=self.args.native_tool_home)
            record = MOD.run(self.args, command_runner=runner,
                             consequence_module=ConsequenceFake())
        self.assertTrue(record['complete'])
        self.assertEqual(len(runner.calls), 6)
        self.assertEqual(record['accepted'], False)
        self.assertEqual(record['publication_allowed'], False)
        self.assertEqual(record['proof_credit'], 0)
        self.assertEqual(record['native_tool_hashes_before'], record['native_tool_hashes_after'])
        for _, argv in runner.calls:
            if 'select-callee-r21-fractional-proof-entry.py' in argv[1]:
                self.assertIn(str(self.args.native_tool_home), argv)

    def test_audit_reopens_summary_matrix_logs_source_and_tool_identity(self):
        with self.patched(), mock.patch.dict(os.environ, self.env, clear=True):
            runner = FakeCommandRunner(native_home=self.args.native_tool_home)
            MOD.run(self.args, command_runner=runner,
                    consequence_module=ConsequenceFake())
            self.args.output = self.args.evidence / MOD.AUDIT_REL
            self.args.runner_exit = 0
            self.args.failed_stage = 'complete'
            with mock.patch.object(MOD, '_load', return_value=FrozenAuditFake()):
                result = MOD.audit(self.args, consequence_module=ConsequenceFake())
        self.assertTrue(result['complete'], result['errors'])
        self.assertFalse(result['accepted'])
        self.assertEqual(result['proof_credit'], 0)

    def test_error_exit_is_preserved_and_stops_following_stages(self):
        with self.patched(), mock.patch.dict(os.environ, self.env, clear=True):
            runner = FakeCommandRunner(fail='candidate-source-compare')
            record = MOD.run(self.args, command_runner=runner,
                             consequence_module=ConsequenceFake())
        self.assertFalse(record['complete'])
        self.assertEqual(record['stages'][-1]['exit'], 1)
        self.assertEqual(record['stages'][-1]['name'], 'candidate-source-compare')
        self.assertEqual(len(runner.calls), 3)

    def test_timeout_status_and_exit_are_not_recast(self):
        runner = FakeCommandRunner(fail='source-preflight', result={
            'status': 'TIMEOUT', 'exit': 124, 'stdout': 'partial', 'stderr': 'timeout'})
        with self.patched(), mock.patch.dict(os.environ, self.env, clear=True):
            record = MOD.run(self.args, command_runner=runner,
                             consequence_module=ConsequenceFake())
        self.assertEqual(record['stages'][0]['status'], 'TIMEOUT')
        self.assertEqual(record['stages'][0]['exit'], 124)
        self.assertFalse(record['complete'])

    def test_missing_success_artifact_stays_incomplete(self):
        with self.patched(), mock.patch.dict(os.environ, self.env, clear=True):
            runner = FakeCommandRunner(omit_output='candidate-capture')
            record = MOD.run(self.args, command_runner=runner,
                             consequence_module=ConsequenceFake())
        self.assertFalse(record['complete'])
        self.assertEqual(record['stages'][-1]['status'], 'RAN')
        self.assertTrue(any('capture' in error for error in record['errors']))

    def test_missing_null_and_wrong_type_stage_results_fail_closed(self):
        for malformed in (None, 'not-a-stage', {'status': 'NOT_RUN', 'exit': None,
                                                'stdout': None, 'stderr': None}):
            row = MOD._stage_record('stage', ['cmd'], malformed)
            self.assertNotEqual(row['status'], 'RAN')
            self.assertTrue(row['errors'])

    def test_matrix_requires_all_exact_rows_and_source_bound_ran_stages(self):
        data = matrix_record()
        self.assertEqual(MOD._validate_matrix_rows(data), [])
        del data['rows']['omit-selected-own']
        self.assertTrue(MOD._validate_matrix_rows(data))

    def test_source_stage_target_mismatch_is_rejected(self):
        data = matrix_record()
        data['rows']['positive']['current_stage_observation']['source_unchanged'] = False
        self.assertIn('proof stage missing/partial/source-dirty: positive',
                      MOD._validate_matrix_rows(data))
        with mock.patch.object(MOD, 'CONST_ORIGINAL_SHA256', 'a' * 64):
            self.assertIn('matrix source-stage-target command differs: positive',
                          MOD._validate_matrix_rows(data, native_home=Path('/native')))

    def test_dirty_source_after_baseline_stage_is_captured(self):
        with self.patched(), mock.patch.dict(os.environ, self.env, clear=True):
            runner = FakeCommandRunner(native_home=self.args.native_tool_home,
                                       dirty_after='candidate-proof')
            record = MOD.run(self.args, command_runner=runner,
                             consequence_module=ConsequenceFake())
        self.assertFalse(record['complete'])
        self.assertTrue(any('source changed' in error for error in record['errors']))

    def test_tool_identity_drift_is_detected(self):
        before = {'bin/verifast': {'regular': True, 'sha256': 'native', 'bytes': 1}}
        after = {'bin/verifast': {'regular': True, 'sha256': 'changed', 'bytes': 1}}
        with mock.patch.object(MOD, 'NATIVE_TOOL_HASHES', {'bin/verifast': 'native'}):
            self.assertTrue(MOD._validate_native_identities(before, after))

    def test_exception_writes_partial_snapshot_then_rethrows_same_type(self):
        with self.patched(), mock.patch.dict(os.environ, self.env, clear=True):
            runner = FakeCommandRunner(throw='source-preflight')
            with self.assertRaisesRegex(RuntimeError, 'injected stage exception'):
                MOD.run(self.args, command_runner=runner,
                        consequence_module=ConsequenceFake())
        partial = json.loads((self.args.evidence / MOD.SUMMARY_REL).read_text())
        self.assertFalse(partial['complete'])
        self.assertIn('exception: RuntimeError', partial['errors'][0])


if __name__ == '__main__':
    unittest.main()
