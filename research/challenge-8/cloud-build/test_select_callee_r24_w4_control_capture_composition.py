"""Tiny fake-service run/audit composition; no actual Rust preparation or tools."""
import argparse
from contextlib import ExitStack
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import types
import unittest
from unittest import mock

PATH = Path(__file__).with_name('select-callee-r24-w4-control-capture.py')
SPEC = importlib.util.spec_from_file_location('r24_capture_composition_tested', PATH)
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)
BUILD = '11111111-1111-4111-8111-111111111111'
OLD_BUILD = '22222222-2222-4222-8222-222222222222'


class CompositionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo, self.cloud, self.ev, self.frozen, self.native = [
            self.root / name for name in ('repo', 'cloud', 'evidence', 'frozen', 'native')]
        for p in (self.repo, self.cloud, self.ev, self.frozen, self.native):
            p.mkdir()
        self.source = b'synthetic repository source, not Rust\n'
        p = self.repo / M.SOURCE_REL
        p.parent.mkdir(parents=True)
        p.write_bytes(self.source)
        self.args = argparse.Namespace(repo=self.repo, cloud_dir=self.cloud, evidence=self.ev,
            tool_home=self.frozen, native_tool_home=self.native,
            schema=self.native / 'src/rust_frontend/vf_mir/vf_mir.capnp',
            compiler_sysroot=self.root / 'synthetic-sysroot',
            candidate='a' * 40, deadline_epoch=4_000_000_000,
            mode_file=self.repo / M.MODE_REL, capture_mode_file=self.repo / M.CAPTURE_MODE_REL,
            output=self.ev / M.AUDIT_REL, runner_exit=0, failed_stage='complete')
        self.input_pins = {**M.NATIVE_TOOL_SOURCE_HASHES, 'bin/verifast': M.NATIVE_BINARY_SHA256}
        self.output_pins = {**self.input_pins, 'bin/verifast': 'b' * 64,
            'src/rust_frontend/vf_mir_translator/vf_mir_translator.ml': M.NATIVE_TRANSLATOR_SHA256}
        self.profile = {'actual_indexed_calls': 5, 'body_action': 'full-body-c1-recovery',
                        'cloud_build_enabled': False}
        self.rows = [dict(name=name, kind='positive' if i == 0 else 'source-control',
            verified=b'synthetic verified ' + str(i).encode() + b'\n',
            original=b'synthetic runtime\n', metadata={'actual_indexed_calls': 5})
            for i, name in enumerate(M.BODY_NAMES)]
        self.summary = dict(schema='select-r24-w4-contract-inputs-v1', complete=True,
            phase_id=M.R24_PHASE, route_phase_id=M.R21_PHASE, owner='select-sort4',
            lane=M.LANE, profile=M.PROFILE, candidate=self.args.candidate, build_id=BUILD,
            accepted=False, publication_allowed=False, proof_credit=0,
            caller_body_proof_admission=False, typed_call_linkage='UNKNOWN',
            call_linkage='UNKNOWN', caller_body_proof_status='UNKNOWN',
            cases=[dict(case=name, expected_classification=classification, errors=[],
                        facts=dict(complete=True, classification=classification))
                for name, classification in zip(
                    ('positive', 'false-normal', 'false-unwind', 'duplicate-thread',
                     'mut-pointer', 'extra-declaration'),
                    ('INPUTS_MATCH',) + ('EXPECTED_INPUT_REFUSAL',) * 5)],
            diagnostic_tool_hashes_after_build={
                rel: dict(regular=True, matches=True, bytes=9, sha256=value,
                    expected_sha256='DIAGNOSTIC_BUILD_OUTPUT_RECORDED'
                    if rel == 'bin/verifast' else value)
                for rel, value in self.input_pins.items()})
        self.prereq_audit = dict(schema='select-r24-w4-contract-inputs-v1-audit',
            complete=True, evidence_complete=True, candidate=self.args.candidate, build_id=BUILD,
            accepted=False, publication_allowed=False, proof_credit=0)
        self.failure_stage = None
        self.failure_status = None
        self.raise_error = None
        self.native_override = {}
        self.calls = []
        self.env = {k: v for k, v in os.environ.items() if not k.startswith('SORT4_')}
        self.env.update(CLOUD_BUILD_ID=BUILD, SMALLSORT_EXECUTION_PROVIDER='cloud-build',
                        LANE=M.LANE, SORT4_SELECT_PROFILE=M.PROFILE)
        self.env[M.R24_PHASE_ENV] = M.R24_PHASE
        self.env[M.R21_PHASE_ENV] = M.R21_PHASE
        self.env.pop('GITHUB_ACTIONS', None)

    def stage(self, name, argv, root, env, fixture_hashes, deadline, cap,
              stdin_name=None, stdout_name=None):
        self.calls.append(name)
        if self.raise_error is not None and name == self.failure_stage:
            raise self.raise_error
        root = Path(root)
        out = stdout_name or name + '.stdout.log'
        err = name + '.stderr.log'
        stdout = b'synthetic service output\n'
        stderr = b''
        code = 0
        if name == 'native-fingerprint':
            fp = Path(env['SORT4_R24_W4_DATA_FINGERPRINT_EVIDENCE_DIR'])
            source = (root / 'verified/lib.rs').read_bytes()
            unit, body = b'synthetic unit bytes', b'synthetic body bytes'
            (fp / 'caller-native-unit.marshal').write_bytes(unit)
            (fp / 'caller-native-body-0.marshal').write_bytes(body)
            facts = dict(schema='select-r24-w4-native-data-fingerprint-v1',
                classification='SOURCE_ONLY_NATIVE_DATA_CAPTURE', complete=True,
                build_id=BUILD, body_name='sort4_stable', body_index=0,
                body_inventory=['sort4_stable'], expected_refusal='snapshot complete; no proof rule admitted',
                body_proof_run=False, accepted=False, publication_allowed=False,
                caller_body_proof_admission=False, typed_call_linkage='UNKNOWN', proof_credit=0,
                source=dict(path=str((root / 'verified/lib.rs').resolve()), bytes=len(source),
                            sha256=M.digest(source)),
                unit=dict(path='caller-native-unit.marshal', bytes=len(unit), sha256=M.digest(unit)),
                body=dict(path='caller-native-body-0.marshal', bytes=len(body), sha256=M.digest(body)))
            facts.update(self.native_override)
            (fp / 'native-data.json').write_text(json.dumps(facts))
            stdout = ('SORT4-R24-W4-DATA: source_sha256=%s unit_bytes=%s unit_sha256=%s '
                'body_bytes=%s body_sha256=%s body_name=sort4_stable\n' %
                (M.digest(source), len(unit), M.digest(unit), len(body), M.digest(body))).encode()
            stderr = (M.NATIVE_REFUSAL_STDERR + '\n').encode()
            code = 2
        (root / out).write_bytes(stdout)
        (root / err).write_bytes(stderr)
        stage = dict(status='RAN', exit=code, argv=argv, fixture_integrity=True,
            fixture_before=dict(fixture_hashes), fixture_after=dict(fixture_hashes),
            stdout=out, stderr=err)
        if name == self.failure_stage:
            stage.update(exit=124 if self.failure_status == 'TIMEOUT' else 7,
                         status=self.failure_status or 'RAN')
        (root / (name + '-stage.json')).write_text(json.dumps(stage))
        return stage

    def context(self, args, *, fresh=False):
        if fresh:
            M.need(not (self.ev / M.SUMMARY_REL.parent).exists(),
                   'fake service observed fresh validation after output creation')
        return self.repo, self.cloud, self.ev, self.frozen, self.native

    def build(self, args, *, work_root, cloud_dir, native_home, stage_runner):
        target = self.root / 'synthetic-new-tool'
        target.mkdir()
        patch_path = self.repo / M.NATIVE_PATCH_REL
        commands = {
            'native-tool-copy': ['/bin/cp', '-a', str(native_home), str(target)],
            'native-patch-check': ['git', '-C', str(target), 'apply', '--check', str(patch_path)],
            'native-patch-apply': ['git', '-C', str(target), 'apply', str(patch_path)],
            'native-tool-build': ['make', '-C', str(target / 'src'),
                                 '../bin/verifast', 'WITHOUT_LABLGTK=yes', 'VERBOSE=yes'],
        }
        stages = {name: M._stage_call(stage_runner, name, argv, work_root, self.env, {},
                                     args.deadline_epoch, 1)
                  for name, argv in commands.items()}
        return dict(target=str(target), errors=[], source_before=self.input_pins,
                    source_copied=self.input_pins, source_after_build=self.output_pins,
                    copy_stage=stages['native-tool-copy'], patch_check_stage=stages['native-patch-check'],
                    patch_apply_stage=stages['native-patch-apply'], build_stage=stages['native-tool-build'])

    def graph_inventory(self, decoded_path, out, mode):
        record = decoded_path.read_text()
        (out / (mode + '-sort4-full-mir.txt')).write_text(record)
        graph = {'synthetic': True, 'mode': mode}
        (out / (mode + '-graph-inventory.json')).write_text(
            json.dumps(graph, indent=2, sort_keys=True) + '\n')
        return graph

    def patches(self):
        stack = ExitStack()
        stack.enter_context(mock.patch.dict(os.environ, self.env, clear=True))
        replacements = {
            'BATCH_INDICES': (0,), 'MODE_SHA256': 'd' * 64,
            'NATIVE_TOOL_HOME_NAME': str(self.root / 'synthetic-new-tool'),
            'SOURCE_SHA256': M.digest(self.source),
            '_validate_context': self.context,
            '_check_mode': lambda *a: M.expected_mode(),
            '_provider_record': lambda *a: {'build_id': BUILD},
            '_validate_native_schema': lambda *a: 'e' * 64,
            '_validate_capture_inputs': lambda *a: (
                {'frozen-tool': 'pinned'},
                types.SimpleNamespace(complete_function_record=lambda text, name: (name, text),
                                      graph_inventory=self.graph_inventory)),
            '_validate_native_input_identity': lambda *a: self.input_pins,
            '_native_input_identity_record': lambda *a: {'build_id': OLD_BUILD, 'assurance': 'SOURCE_REPORTED'},
            '_load_constructor_inputs': lambda *a: (self.profile, {}),
            '_construct_sources': lambda *a: self.rows,
            '_prepare_native_tool': self.build,
            '_tool_hashes': lambda *a: {'frozen-tool': 'pinned'},
            '_tool_sources': lambda home, **kw: self.input_pins if home == self.native else self.output_pins,
        }
        for name, value in replacements.items():
            stack.enter_context(mock.patch.object(M, name, value))
        stack.enter_context(mock.patch.object(M.subprocess, 'check_output', return_value=self.args.candidate + '\n'))
        return stack

    def run_fake(self):
        return M.run(self.args, prerequisite_summary=self.summary,
                     prerequisite_audit=self.prereq_audit, stage_runner=self.stage)

    def audit_fake(self):
        return M.audit(self.args, prerequisite_summary=self.summary,
                       prerequisite_audit=self.prereq_audit)

    def test_selected_batch_run_and_physical_audit_keep_historical_and_live_builds_distinct(self):
        with self.patches():
            result = self.run_fake()
            self.assertTrue(result['complete'], result['errors'])
            self.assertFalse(result['universe_complete'])
            audit = self.audit_fake()
        self.assertTrue(audit['complete'], audit['errors'])
        self.assertEqual(audit, json.loads((self.ev / M.AUDIT_REL).read_text()))
        self.assertFalse(audit['body_proof_run'])
        self.assertFalse(audit['universe_complete'])

    def test_explicit_notrun_timeout_and_error_never_complete(self):
        for status in ('NOT_RUN', 'TIMEOUT', 'RAN'):
            with self.subTest(status=status):
                # Separate fresh subtree per service attempt.
                self.ev = self.root / ('evidence-' + status)
                self.ev.mkdir()
                self.args.evidence = self.ev
                self.args.output = self.ev / M.AUDIT_REL
                self.failure_stage, self.failure_status = 'refinement', status
                with self.patches(), mock.patch.object(self, 'build', wraps=self.build):
                    # Build target is a fake reusable directory, not an executable.
                    (self.root / 'synthetic-new-tool').rmdir() if (self.root / 'synthetic-new-tool').exists() else None
                    result = self.run_fake()
                    self.assertFalse(result['complete'])
                    self.args.runner_exit = 4
                    self.args.failed_stage = 'refinement'
                    audited = self.audit_fake()
                self.assertFalse(audited['complete'])

    def test_original_stage_exception_is_preserved_once_with_partial_snapshot(self):
        self.failure_stage = 'normal-export'
        original = TypeError('original synthetic callback failure')
        self.raise_error = original
        with self.patches():
            with self.assertRaises(TypeError) as caught:
                self.run_fake()
        self.assertIs(caught.exception, original)
        self.assertEqual(self.calls.count('normal-export'), 1)
        partial = json.loads((self.ev / M.SUMMARY_REL).read_text())
        self.assertFalse(partial['complete'])
        self.assertTrue(any('original synthetic callback failure' in e for e in partial['errors']))

    def test_source_or_native_snapshot_change_is_rejected_by_readonly_audit(self):
        with self.patches():
            result = self.run_fake()
            self.assertTrue(result['complete'], result['errors'])
            snapshot = self.ev / result['rows'][0]['native']['snapshots']['body']['path']
            snapshot.write_bytes(snapshot.read_bytes() + b'changed')
            audit = self.audit_fake()
        self.assertFalse(audit['complete'])
        self.assertTrue(any('body' in error or 'inventory' in error for error in audit['errors']))

    def test_native_numeric_boolean_does_not_substitute_for_complete(self):
        self.native_override = {'complete': 1}
        with self.patches():
            result = self.run_fake()
        self.assertFalse(result['complete'])
        self.assertTrue(any('complete' in e for e in result['rows'][0]['errors']))

    def test_audit_write_error_cannot_return_complete(self):
        with self.patches():
            self.assertTrue(self.run_fake()['complete'])
            with mock.patch.object(M, '_write_json', side_effect=OSError('synthetic disk failure')):
                audit = self.audit_fake()
        self.assertFalse(audit['complete'])
        self.assertFalse(audit['evidence_complete'])
        self.assertFalse(audit['audit_written'])
        self.assertFalse((self.ev / M.AUDIT_REL).exists())

    def test_every_persisted_mir_fact_is_bound_to_unchanged_physical_inputs(self):
        with self.patches():
            self.assertTrue(self.run_fake()['complete'])
            path = self.ev / M.SUMMARY_REL
            original = path.read_bytes()
            physical = M._summary_root_inventory(path.parent, self.ev)
            mutations = {
                'decoded_sha256': '0' * 64,
                'full_function_record': 'other/report.txt',
                'full_function_record_sha256': 'f' * 64,
                'function_name': 'different_function',
                'graph_inventory': {'synthetic': False, 'mode': 'normal'},
            }
            for mode in ('normal', 'readonly'):
                for field, value in mutations.items():
                    with self.subTest(mode=mode, field=field):
                        report = json.loads(original)
                        report['rows'][0]['mir'][mode][field] = value
                        path.write_text(json.dumps(report))
                        audit = self.audit_fake()
                        self.assertFalse(audit['complete'])
                        self.assertTrue(any('MIR' in e for e in audit['errors']))
                        self.assertEqual(M._summary_root_inventory(path.parent, self.ev), physical)
            for missing_or_extra in ('missing', 'extra'):
                report = json.loads(original)
                if missing_or_extra == 'missing':
                    del report['rows'][0]['mir']['readonly']
                else:
                    report['rows'][0]['mir']['extra'] = {}
                path.write_text(json.dumps(report))
                self.assertFalse(self.audit_fake()['complete'])

    def test_row_and_universe_metadata_are_reconstructed_not_trusted(self):
        with self.patches():
            self.assertTrue(self.run_fake()['complete'])
            path = self.ev / M.SUMMARY_REL
            original = path.read_bytes()
            physical = M._summary_root_inventory(path.parent, self.ev)
            for branch in ('rows', 'constructor_inventory'):
                with self.subTest(branch=branch):
                    report = json.loads(original)
                    report[branch][0]['source_metadata']['actual_indexed_calls'] = 2
                    path.write_text(json.dumps(report))
                    audit = self.audit_fake()
                    self.assertFalse(audit['complete'])
                    self.assertTrue(any('metadata' in e or 'constructor source inventory' in e
                                        for e in audit['errors']))
                    self.assertEqual(M._summary_root_inventory(path.parent, self.ev), physical)

    def test_successful_graph_recheck_does_not_write_captured_artifacts(self):
        with self.patches():
            self.assertTrue(self.run_fake()['complete'])
            root = self.ev / M.SUMMARY_REL.parent
            before = M._summary_root_inventory(root, self.ev)
            self.assertTrue(self.audit_fake()['complete'])
            self.assertEqual(M._summary_root_inventory(root, self.ev), before)

    def test_compare_only_adapter_uses_real_pinned_graph_parser_on_tiny_text(self):
        repo = PATH.resolve().parents[3]
        logical, pinned = M.HELPER_PINS['capture']
        capture = M._load(repo / logical, 'r24_tiny_graph_parser', pinned)
        case = self.ev / 'tiny-parser-service'
        fixture = case / 'fixture'
        fixture.mkdir(parents=True)
        calls = '\n'.join(
            '( id = (index = %d), fnDef = (id = (name = "std::ops::FnMut::call_mut")), '
            'unwindAction = continue )' % i for i in range(5))
        decoded = ('    ( defKind = function, defPath = "sort4_stable", '
                   'inputs = [], localDecls = [], basicBlocks = [\n' + calls + '\n])')
        path = fixture / 'normal-mir.txt'
        path.write_text(decoded)
        expected = capture.graph_inventory(path, case, 'normal')
        before = {str(p): p.read_bytes() for p in case.rglob('*') if p.is_file()}
        with mock.patch.object(Path, 'write_text', side_effect=AssertionError('read-only parser attempted write')):
            result = M._recompute_mir_observation(self.ev, case, 'normal', capture)
        self.assertEqual(result['graph_inventory'], expected)
        self.assertEqual(result['function_name'], 'sort4_stable')
        self.assertEqual({str(p): p.read_bytes() for p in case.rglob('*') if p.is_file()}, before)

    def test_row_and_batch_indices_reject_false_float_string_and_null(self):
        with self.patches():
            self.assertTrue(self.run_fake()['complete'])
            path = self.ev / M.SUMMARY_REL
            original = path.read_bytes()
            for value in (False, 0.0, '0', None):
                for field in ('row', 'batch'):
                    with self.subTest(field=field, value=value):
                        report = json.loads(original)
                        if field == 'row':
                            report['rows'][0]['index'] = value
                        else:
                            report['batch_indices'] = [value]
                        path.write_text(json.dumps(report))
                        self.assertFalse(self.audit_fake()['complete'])
            for value in (None, '0', {'0': 0}):
                report = json.loads(original)
                report['batch_indices'] = value
                path.write_text(json.dumps(report))
                self.assertFalse(self.audit_fake()['complete'])

    def test_adjacent_numeric_context_and_size_records_are_exact(self):
        with self.patches():
            self.assertTrue(self.run_fake()['complete'])
            path = self.ev / M.SUMMARY_REL
            original = path.read_bytes()
            mutations = (
                lambda r: r.update(universe_count=37.0),
                lambda r: r.update(runner_exit=False),
                lambda r: r['source_after'].update(bytes=float(r['source_after']['bytes'])),
                lambda r: r['constructor_profile'].update(actual_indexed_calls=5.0),
                lambda r: r['artifact_inventory'][0].update(bytes=float(r['artifact_inventory'][0]['bytes'])),
                lambda r: r['rows'][0]['fixture']['verified'].update(
                    bytes=float(r['rows'][0]['fixture']['verified']['bytes'])),
                lambda r: r['rows'][0]['native']['snapshots']['body'].update(
                    bytes=float(r['rows'][0]['native']['snapshots']['body']['bytes'])),
                lambda r: r['provider_record'].update(build_id=OLD_BUILD),
                lambda r: r['tool_build']['stages'].pop('native-tool-build'),
                lambda r: r['tool_build']['copy_stage'].update(exit=False),
            )
            for i, mutate in enumerate(mutations):
                with self.subTest(mutation=i):
                    report = json.loads(original)
                    mutate(report)
                    path.write_text(json.dumps(report))
                    self.assertFalse(self.audit_fake()['complete'])

    def test_outer_runner_boolean_is_not_integer_exit_zero(self):
        with self.patches():
            self.assertTrue(self.run_fake()['complete'])
            self.args.runner_exit = False
            self.assertFalse(self.audit_fake()['complete'])


if __name__ == '__main__':
    unittest.main()
