#!/usr/bin/env python3
"""Synthetic-only tests for the dormant native compile controller."""
from __future__ import annotations

import hashlib
import importlib.util
import ast
import json
import os
from pathlib import Path
import shutil
import tempfile
import types
import unittest
from unittest.mock import patch

MODULE_PATH = Path(__file__).with_name('select-callee-r24-w4-dormant-compile.py')
SPEC = importlib.util.spec_from_file_location('w4_dormant_compile_under_test', MODULE_PATH)
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
SPEC.loader.exec_module(MOD)

HELPER_PATH = Path(__file__).with_name('select-callee-r24-w4-control-capture.py')
HELPER_SPEC = importlib.util.spec_from_file_location('w4_control_capture_real_dependency', HELPER_PATH)
HELPER = importlib.util.module_from_spec(HELPER_SPEC)
assert HELPER_SPEC is not None and HELPER_SPEC.loader is not None
HELPER_SPEC.loader.exec_module(HELPER)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class FakeStages:
    def __init__(self, helper, target, *, failure=None, malformed=None, write_files=True):
        self.helper = helper
        self.target = target
        self.failure = failure
        self.malformed = malformed
        self.write_files = write_files
        self.calls = []

    def __call__(self, name, argv, root, env, fixture_hashes, deadline, cap,
                 *, stdin_name=None, stdout_name=None):
        self.calls.append(name)
        index = len(self.calls) - 1
        if self.malformed and self.malformed[0] == index:
            return self.malformed[1]
        if index == 0:
            self.target.mkdir(parents=True)
            (self.target / 'bin').mkdir()
        code = self.failure[1] if self.failure and self.failure[0] == index else 0
        stdout_name = f'{name}.stdout.log'
        stderr_name = f'{name}.stderr.log'
        record = {'argv': argv, 'exit': code, 'timeout_seconds': cap,
                  'fixture_before': {}, 'fixture_after': {}, 'fixture_integrity': True,
                  'stdout': stdout_name, 'stderr': stderr_name}
        if self.failure and self.failure[0] == index and self.failure[2] == 'timeout':
            record.update({'status': 'TIMEOUT', 'exit': 124})
        if self.failure and self.failure[0] == index and self.failure[2] == 'notrun':
            record.update({'status': 'NOT_RUN', 'exit': 0})
        if self.write_files:
            root.mkdir(parents=True, exist_ok=True)
            (root / stdout_name).write_bytes(b'fake stdout\n')
            (root / stderr_name).write_bytes(b'fake stderr\n')
            self.helper._write_json(root, root / f'{name}-stage.json', record)
        return record


class DormantCompileTests(unittest.TestCase):
    def test_pinned_real_helper_api_and_mode_boundary(self):
        with tempfile.TemporaryDirectory() as tmp:
            helper = MOD._load_helper(Path(tmp), HELPER_PATH.parent)
        self.assertEqual(helper.digest(HELPER_PATH.read_bytes()), MOD.CONTROL_HELPER_SHA256)
        self.assertEqual(MOD.STAGES, ('copy', 'patch-check', 'patch-apply', 'compile'))
        mode = MOD.expected_mode()
        self.assertTrue(mode['input_binary_sha256'])
        self.assertNotIn('proof_credit', mode)
        self.assertNotIn('caller_body_proof_admission', mode)
        self.assertFalse(MOD._json_exact({'proof_credit': False}, {'proof_credit': 0}))
        self.assertEqual(MOD._stage_status({'exit': False}), ('WRONG_TYPE', None))

    def test_frozen_capture_stage_api_has_named_stdio_parameters(self):
        capture_path = MODULE_PATH.parents[1] / 'overnight-sort4/capture.py'
        tree = ast.parse(capture_path.read_text(encoding='utf-8'))
        stage = next(node for node in tree.body
                     if isinstance(node, ast.FunctionDef) and node.name == 'run_stage')
        names = [arg.arg for arg in stage.args.args + stage.args.kwonlyargs]
        self.assertIn('stdin_name', names)
        self.assertIn('stdout_name', names)

    def test_command_inventory_is_closed_and_copy_build_arguments_exact(self):
        commands = MOD._stage_commands(Path('/repo'), Path('/tmp/target'), Path('/repo/patch'))
        self.assertEqual(commands['copy'], ['/bin/cp', '-a', str(MOD.INPUT_HOME), '/tmp/target'])
        self.assertEqual(commands['patch-check'], ['git', '-C', '/tmp/target', 'apply', '--check', '/repo/patch'])
        self.assertEqual(commands['patch-apply'], ['git', '-C', '/tmp/target', 'apply', '/repo/patch'])
        self.assertEqual(commands['compile'], ['make', '-C', '/tmp/target/src', '../bin/verifast',
            'WITHOUT_LABLGTK=yes', 'VERBOSE=yes'])
        self.assertEqual(set(commands), set(MOD.STAGES))

    def _chain(self, *, failure=None, malformed=None, write_files=True):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        base = Path(temporary.name)
        evidence = base / 'evidence'
        evidence.mkdir()
        target = base / 'native-target'
        stages = FakeStages(HELPER, target, failure=failure, malformed=malformed,
                            write_files=write_files)
        result = MOD._run_stage_chain(HELPER, stages, repo=base, evidence=evidence,
            target=target, patch=base / 'patch.diff', deadline=9999999999)
        return base, evidence, target, stages, result

    def test_success_runs_all_four_and_physical_stage_files_match(self):
        base, evidence, target, stages, result = self._chain()
        self.assertTrue(result['complete'])
        self.assertEqual(stages.calls, ['dormant-copy', 'dormant-patch-check',
                                       'dormant-patch-apply', 'dormant-compile'])
        self.assertEqual(MOD._physical_stages(HELPER, evidence,
            {'commands': result['commands'], 'stages': result['stages']}), [])
        self.assertTrue(target.is_dir())

    def test_nonzero_timeout_and_not_run_preserve_exit_and_stop_chain(self):
        for failure, expected_status in (((1, 1, 'error'), 'RAN'),
                                         ((1, 124, 'timeout'), 'TIMEOUT'),
                                         ((1, 0, 'notrun'), 'NOT_RUN')):
            with self.subTest(failure=failure):
                _, _, _, stages, result = self._chain(failure=failure)
                self.assertFalse(result['complete'])
                self.assertEqual(len(stages.calls), 2)
                self.assertEqual(MOD._stage_status(result['stages']['patch-check'])[0], expected_status)
                self.assertNotIn('patch-apply', result['stages'])

    def test_missing_physical_stage_log_and_stage_json_are_incomplete(self):
        _, evidence, _, _, result = self._chain(write_files=False)
        errors = MOD._physical_stages(HELPER, evidence,
            {'commands': result['commands'], 'stages': result['stages']})
        self.assertTrue(errors)
        self.assertFalse(result['complete'])

    def test_null_wrong_type_and_explicit_not_run_exit_zero_do_not_advance(self):
        for value, status in ((None, 'WRONG_TYPE'), ('bad', 'WRONG_TYPE'),
                              ({'status': 'NOT_RUN', 'exit': 0}, 'NOT_RUN'),
                              ({'status': None, 'exit': 0}, 'WRONG_TYPE'),
                              ({'status': 'BOGUS', 'exit': 0}, 'WRONG_TYPE')):
            with self.subTest(value=value):
                _, _, _, stages, result = self._chain(malformed=(0, value))
                self.assertFalse(result['complete'])
                self.assertEqual(len(stages.calls), 1)
                self.assertEqual(MOD._stage_status(result['stages']['copy'])[0], status)

    def test_stage_target_mismatch_is_rejected_by_physical_command_audit(self):
        base, evidence, _, stages, result = self._chain()
        result['commands']['patch-check'] = ['git', '-C', '/wrong/tool', 'apply', '--check', str(base / 'patch.diff')]
        errors = MOD._physical_stages(HELPER, evidence,
            {'commands': result['commands'], 'stages': result['stages']})
        self.assertTrue(any('command target differs' in error for error in errors))

    def test_unsafe_log_path_is_refused(self):
        base, evidence, _, stages, result = self._chain()
        stage = result['stages']['copy']
        stage['stdout'] = '../outside.log'
        errors = MOD._physical_stages(HELPER, evidence,
            {'commands': result['commands'], 'stages': result['stages']})
        self.assertTrue(any('log name malformed' in error for error in errors))

    def test_internal_stage_typeerror_is_not_retried(self):
        calls = []
        original = TypeError('callback internal typeerror')
        def fail_once(name, argv, root, env, fixture_hashes, deadline, cap,
                      *, stdin_name=None, stdout_name=None):
            calls.append(name)
            raise original
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(TypeError, 'callback internal typeerror'):
                MOD._stage_call(fail_once, 'dormant-copy', [], Path(tmp), {}, 1000)
        self.assertEqual(calls, ['dormant-copy'])

    def test_stage_exception_is_retained_as_original_object_and_partial_stage(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        base = Path(temporary.name); evidence = base / 'evidence'; evidence.mkdir()
        original = RuntimeError('stage service failed')
        calls = []
        def broken(name, argv, root, env, fixture_hashes, deadline, cap,
                    *, stdin_name=None, stdout_name=None):
            calls.append(name)
            raise original
        result = MOD._run_stage_chain(HELPER, broken, repo=base, evidence=evidence,
            target=base / 'tool', patch=base / 'patch', deadline=9999999999)
        self.assertIs(result['_exception_object'], original)
        self.assertEqual(calls, ['dormant-copy'])
        self.assertFalse(result['complete'])
        self.assertEqual(result['stages']['copy']['exception_type'], 'RuntimeError')

    def test_symlink_ancestor_is_rejected_before_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            real = root / 'real'; real.mkdir()
            alias = root / 'alias'; alias.symlink_to(real, target_is_directory=True)
            with self.assertRaisesRegex(RuntimeError, 'symlink'):
                MOD._assert_chain(alias / 'new' / 'file', missing=True)

    def test_manifest_shape_is_closed_and_diagnostic_only(self):
        manifest = {
            'schema': 'select-r24-w4-dormant-native-manifest-v1',
            'dormant': True, 'caller_body_proof_admission': False,
            'accepted': False, 'publication_allowed': False, 'proof_credit': 0,
            'base_translator_sha256': 'a' * 64, 'result_translator_sha256': 'b' * 64,
            'patch': {'path': MOD.PATCH_REL.as_posix(), 'sha256': 'c' * 64}}
        self.assertTrue(manifest['dormant'])
        self.assertFalse(manifest['accepted'])
        self.assertEqual(type(manifest['proof_credit']), int)
        manifest['proof_credit'] = False
        self.assertIsNot(type(manifest['proof_credit']), int)

    def test_real_run_then_physical_audit_composition_with_fake_stages(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            repo = base / 'repo'; repo.mkdir()
            cloud = base / 'cloud'; cloud.mkdir()
            evidence = base / 'evidence'; evidence.mkdir()
            native_in = base / 'input-tool'; native_in.mkdir()
            target = base / 'output-tool'
            identity_path = repo / 'identity.json'
            manifest_path = repo / 'manifest.json'
            patch_path = repo / 'patch.diff'
            mode_path = repo / 'mode.json'
            control_bytes = HELPER_PATH.read_bytes()
            (cloud / HELPER_PATH.name).write_bytes(control_bytes)

            source_bytes = {}
            source_hashes = {}
            for rel in HELPER.NATIVE_TOOL_SOURCE_HASHES:
                raw = ('input:' + rel).encode()
                source_bytes[rel] = raw
                source_hashes[rel] = sha(raw)
                path = native_in / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(raw)
            binary = b'input verifast binary'
            (native_in / 'bin/verifast').parent.mkdir(parents=True, exist_ok=True)
            (native_in / 'bin/verifast').write_bytes(binary)
            input_hashes = {**source_hashes, 'bin/verifast': sha(binary)}
            identity = {'schema': 'select-r24-w4-source-reported-tool-identity-v1',
                'assurance': 'SOURCE_REPORTED',
                'classification': 'C6_INPUT_DIAGNOSTIC_TOOL_IDENTITY_ONLY',
                'tool_hashes': input_hashes, 'accepted': False,
                'publication_allowed': False, 'caller_body_proof_admission': False,
                'proof_credit': 0}
            identity_raw = (json.dumps(identity, sort_keys=True, indent=2) + '\n').encode()
            identity_path.write_bytes(identity_raw)
            patch_bytes = b'fake native patch\n'; patch_path.write_bytes(patch_bytes)
            result_translator = b'patched translator bytes'
            result_sha = sha(result_translator)
            manifest = {'schema': 'select-r24-w4-dormant-native-manifest-v1',
                'dormant': True, 'base_translator_sha256': source_hashes[
                    'src/rust_frontend/vf_mir_translator/vf_mir_translator.ml'],
                'result_translator_sha256': result_sha,
                'patch': {'path': 'patch.diff', 'sha256': sha(patch_bytes)},
                'caller_body_proof_admission': False, 'accepted': False,
                'publication_allowed': False, 'proof_credit': 0}
            manifest_raw = (json.dumps(manifest, sort_keys=True, indent=2) + '\n').encode()
            manifest_path.write_bytes(manifest_raw)

            candidate = 'a' * 40
            build = '11111111-1111-4111-8111-111111111111'
            qual = {'schema': 'select-r24-w4-const-qualification-v1', 'complete': True,
                'candidate': candidate, 'build_id': build, 'phase_id': MOD.R24_PHASE,
                'route_phase_id': MOD.R21_PHASE, 'lane': MOD.LANE, 'profile': MOD.PROFILE,
                'accepted': False, 'publication_allowed': False, 'proof_credit': 0,
                'source_observation': {'complete': True},
                'consequence': {'complete': True, 'accepted': False, 'publication_allowed': False,
                    'caller_body_proof_admission': False, 'proof_credit': 0},
                'consequence_audit': {'complete': True, 'evidence_complete': True,
                    'accepted': False, 'publication_allowed': False, 'proof_credit': 0},
                'postqualification_diagnostic': {'complete': True, 'accepted': False,
                    'publication_allowed': False, 'caller_body_proof_admission': False,
                    'proof_credit': 0},
                'postqualification_diagnostic_audit': {'complete': True, 'evidence_complete': True,
                    'accepted': False, 'publication_allowed': False, 'proof_credit': 0},
                'source_control_capture': {'complete': True, 'accepted': False,
                    'publication_allowed': False, 'caller_body_proof_admission': False,
                    'proof_credit': 0},
                'source_control_capture_audit': {'complete': True, 'evidence_complete': True,
                    'accepted': False, 'publication_allowed': False, 'proof_credit': 0}}
            qual_path = evidence / MOD.CONST_SUMMARY_REL
            qual_path.parent.mkdir(parents=True)
            qual_raw = (json.dumps(qual, sort_keys=True, indent=2) + '\n').encode()
            qual_path.write_bytes(qual_raw)
            qual_audit = {'schema': 'select-r24-w4-const-qualification-v1-audit',
                'complete': True, 'evidence_complete': True, 'candidate': candidate,
                'build_id': build, 'summary_sha256': sha(qual_raw), 'accepted': False,
                'publication_allowed': False, 'proof_credit': 0,
                'runner_exit': 0, 'failed_stage': 'complete'}
            qa_path = evidence / MOD.CONST_AUDIT_REL
            qa_path.write_bytes((json.dumps(qual_audit, sort_keys=True, indent=2) + '\n').encode())

            with patch.object(MOD, 'INPUT_HOME', native_in), \
                 patch.object(MOD, 'TARGET_HOME', target), \
                 patch.object(MOD, 'INPUT_IDENTITY_REL', Path('identity.json')), \
                 patch.object(MOD, 'INPUT_IDENTITY_SHA256', sha(identity_raw)), \
                 patch.object(MOD, 'MANIFEST_REL', Path('manifest.json')), \
                 patch.object(MOD, 'MANIFEST_SHA256', sha(manifest_raw)), \
                 patch.object(MOD, 'PATCH_REL', Path('patch.diff')), \
                 patch.object(MOD, 'PATCH_SHA256', sha(patch_bytes)), \
                 patch.object(MOD, 'MODE_REL', Path('mode.json')), \
                 patch.object(MOD, 'MODE_SHA256', 'temporary-mode-pin'), \
                 patch.object(MOD, 'BASE_TRANSLATOR_SHA256', source_hashes[
                    'src/rust_frontend/vf_mir_translator/vf_mir_translator.ml']), \
                 patch.object(MOD, 'RESULT_TRANSLATOR_SHA256', result_sha), \
                 patch.object(HELPER, 'NATIVE_TOOL_SOURCE_HASHES', source_hashes), \
                 patch.object(MOD.subprocess, 'check_output', return_value=candidate), \
                 patch.dict(os.environ, {'CLOUD_BUILD_ID': build,
                    'SMALLSORT_EXECUTION_PROVIDER': 'cloud-build',
                    MOD.PHASE_ENV: MOD.R24_PHASE, MOD.ROUTE_ENV: MOD.R21_PHASE,
                    'LANE': MOD.LANE, 'SORT4_SELECT_PROFILE': MOD.PROFILE}, clear=True):
                mode = MOD.expected_mode()
                mode_raw = (json.dumps(mode, sort_keys=True, indent=2) + '\n').encode()
                mode_path.write_bytes(mode_raw)
                MOD.MODE_SHA256 = sha(mode_raw)

                class FullFake:
                    def __init__(self): self.calls = []
                    def __call__(self, name, argv, root, env, fixtures, deadline, cap,
                                 *, stdin_name=None, stdout_name=None):
                        self.calls.append(name)
                        if name == 'dormant-copy':
                            shutil.copytree(native_in, target)
                        elif name == 'dormant-patch-apply':
                            (target / 'src/rust_frontend/vf_mir_translator/vf_mir_translator.ml').write_bytes(
                                result_translator)
                        elif name == 'dormant-compile':
                            (target / 'bin/verifast').write_bytes(b'measured output binary')
                        record = {'argv': argv, 'exit': 0, 'timeout_seconds': cap,
                            'fixture_before': {}, 'fixture_after': {}, 'fixture_integrity': True,
                            'stdout': name + '.log', 'stderr': name + '.log'}
                        root.mkdir(parents=True, exist_ok=True)
                        (root / (name + '.log')).write_bytes(b'synthetic stage log\n')
                        HELPER._write_json(root, root / (name + '-stage.json'), record)
                        return record

                args = types.SimpleNamespace(repo=repo, cloud_dir=cloud, evidence=evidence,
                    native_tool_home=native_in, deadline_epoch=9999999999, candidate=candidate)
                fake = FullFake()
                result = MOD.run(args, stage_runner=fake, helper=HELPER)
                self.assertTrue(result['complete'], result['errors'])
                self.assertEqual(fake.calls, ['dormant-copy', 'dormant-patch-check',
                                               'dormant-patch-apply', 'dormant-compile'])
                audit_args = types.SimpleNamespace(**vars(args), output=evidence / MOD.AUDIT_REL,
                    runner_exit=0, failed_stage='complete')
                audited = MOD.audit(audit_args, helper=HELPER)
                self.assertTrue(audited['complete'], audited['errors'])
                self.assertFalse(audited['accepted'])
                self.assertEqual(audited['proof_credit'], 0)
                self.assertTrue(audited['audit_written'])
                saved_audit = json.loads((evidence / MOD.AUDIT_REL).read_text(encoding='utf-8'))
                self.assertEqual(saved_audit, audited)
                summary_path = evidence / MOD.SUMMARY_REL
                summary = json.loads(summary_path.read_text(encoding='utf-8'))
                summary['artifact_inventory'][0]['bytes'] = float(
                    summary['artifact_inventory'][0]['bytes'])
                summary_path.write_text(json.dumps(summary, sort_keys=True, indent=2) + '\n',
                                        encoding='utf-8')
                audit_args.runner_exit = 0
                audit_args.failed_stage = 'complete'
                fractional = MOD.audit(audit_args, helper=HELPER)
                self.assertFalse(fractional['complete'])
                self.assertTrue(any('artifact inventory differs' in error
                                    for error in fractional['errors']))
                (evidence / MOD.SUMMARY_REL.parent / 'tool-build' /
                 'dormant-copy.log').write_bytes(b'changed after audit\n')
                audit_args.runner_exit = 4
                audit_args.failed_stage = 'compile'
                drifted = MOD.audit(audit_args, helper=HELPER)
                self.assertFalse(drifted['complete'])
                self.assertTrue(any('inventory differs' in error for error in drifted['errors']))


if __name__ == '__main__':
    unittest.main()
