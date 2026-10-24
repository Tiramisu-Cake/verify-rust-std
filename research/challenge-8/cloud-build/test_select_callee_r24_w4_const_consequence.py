from __future__ import annotations

import importlib.util
import json
import copy
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace


MODULE_PATH = Path(__file__).with_name('select-callee-r24-w4-const-consequence.py')
SPEC = importlib.util.spec_from_file_location('r24_w4_const_consequence_tested', MODULE_PATH)
CONSEQ = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(CONSEQ)

BUILD = '12345678-1234-4234-8234-123456789abc'
MODEL_BYTES = (b'pred_ctor raw_ptr_own<T>()(t: thread_id_t, v: *T;) = true;\n'
               b'type_pred_def for <T> <*T>.own = raw_ptr_own::<T>;\n')


class FakeDiagnostic:
    def __init__(self, schema_sha):
        self.TOOL_HASHES = {'src/rust_frontend/vf_mir/vf_mir.capnp': schema_sha}
        self.CAPTURE_PINS_REL = Path('pins.json')
        self.MIR_CALLS_REL = Path('mir-calls.py')
        self.generation = 0

    def _validate_context(self, args):
        return tuple(Path(getattr(args, name)).resolve() for name in
                     ('repo', 'cloud_dir', 'evidence', 'tool_home', 'native_tool_home'))

    @staticmethod
    def _validate_route():
        return {'provider': 'cloud-build', 'phase_id': CONSEQ.R24_PHASE,
                'route_phase_id': CONSEQ.R21_PHASE, 'lane': CONSEQ.LANE,
                'profile': CONSEQ.PROFILE}

    @staticmethod
    def _validate_mode(*_args):
        return {'enabled': True}

    @staticmethod
    def _regular_under(root, path):
        root, path = Path(root), Path(path)
        try:
            if root.is_symlink() or path.is_symlink() or not path.is_file():
                return False
            return path.resolve().is_relative_to(root.resolve())
        except OSError:
            return False

    def _tool_hashes(self, _tool_home):
        return {'frozen-generation': self.generation}

    def _native_tool_identity(self, _tool_home):
        return {'binary_sha256': f'{self.generation:064x}', 'source_sha256': 'a' * 64}


class ConstConsequenceTests(unittest.TestCase):
    def setUp(self):
        self.old_model_sha = CONSEQ.MODEL_SHA256
        CONSEQ.MODEL_SHA256 = CONSEQ.sha(MODEL_BYTES)
        self.old_build = __import__('os').environ.get('CLOUD_BUILD_ID')
        __import__('os').environ['CLOUD_BUILD_ID'] = BUILD

    def tearDown(self):
        CONSEQ.MODEL_SHA256 = self.old_model_sha
        if self.old_build is None:
            __import__('os').environ.pop('CLOUD_BUILD_ID', None)
        else:
            __import__('os').environ['CLOUD_BUILD_ID'] = self.old_build

    def fixture(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        base = Path(tmp.name)
        repo, cloud, evidence, tool, native = [base / n for n in
                                                ('repo', 'cloud', 'evidence', 'tool', 'native')]
        for path in (repo, cloud, evidence, tool, native):
            path.mkdir()
        (repo / 'capture-mode.json').write_text('{}')
        (repo / 'mode.json').write_text('{}')
        (repo / 'pins.json').write_text('{}')
        (cloud / 'mir-calls.py').write_text('# fake pinned module\n')
        (base / 'VfMir.capnp').write_text('schema')
        (native / CONSEQ.MODEL_REL).parent.mkdir(parents=True)
        (native / CONSEQ.MODEL_REL).write_bytes(MODEL_BYTES)
        for tool_name in ('verifast', 'vf-rust-mir-exporter', 'refinement-checker'):
            path = native / 'bin' / tool_name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'synthetic tool')
        diag = FakeDiagnostic(CONSEQ.sha((base / 'VfMir.capnp').read_bytes()))
        args = SimpleNamespace(repo=repo, cloud_dir=cloud, evidence=evidence,
            tool_home=tool, native_tool_home=native, schema=base/'VfMir.capnp',
            capture_mode_file=repo/'capture-mode.json', mode_file=repo/'mode.json',
            compiler_sysroot=str(base/'sysroot'), deadline_epoch=4_000_000_000,
            candidate='a' * 40, output=evidence/'audit.json', runner_exit=0,
            failed_stage='complete')
        summary, audit = self.matrix_fixture(args)
        return args, diag, summary, audit

    def matrix_fixture(self, args):
        rows = {}
        for variant in CONSEQ.VARIANTS:
            rows[variant] = {
                'status': 'COMPLETE', 'source_intact_after_stages': True,
                'stage': {'argv': [str(Path(args.native_tool_home).resolve()/'bin/verifast')]}}
        summary = {'schema': 'r21-fractional-classified-proof-v1', 'complete': True,
            'body_proof_run': True, 'accepted': False, 'proof_credit': False,
            'current_build_id': BUILD, 'r24_session_phase_id': CONSEQ.R24_PHASE,
            'tool_home': str(Path(args.native_tool_home).resolve()),
            'variant_order': list(CONSEQ.VARIANTS), 'rows': rows}
        audit = {'schema': 'r21-fractional-proof-audit-v1', 'evidence_complete': True,
            'fractional_proof_status': 'object', 'fractional_proof': summary,
            'accepted': False, 'verification_accepted': False, 'proof_credit': False}
        summary_path = args.evidence / CONSEQ.MATRIX_SUMMARY_REL
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(json.dumps(summary, sort_keys=True))
        audit_path = args.evidence / CONSEQ.MATRIX_AUDIT_REL
        audit_path.write_text(json.dumps(audit, sort_keys=True))
        return summary, audit

    def stage_service(self, args, *, mutate=None, exception=None):
        def stage(name, argv, root, _env, fixture_hashes, deadline, cap,
                  stdin_name=None, stdout_name=None):
            self.assertGreater(deadline, 0)
            self.assertEqual(cap, 1200)
            negative = name == 'omit-result-relation-proof'
            expected = CONSEQ.commands_for(args, negative=negative)
            self.assertIn(name, expected)
            exp_argv, exp_stdin, exp_stdout = expected[name]
            self.assertEqual(argv, exp_argv)
            self.assertEqual(stdin_name, exp_stdin)
            self.assertEqual(stdout_name, exp_stdout)
            before = {'original/lib.rs': CONSEQ.sha((root/'original/lib.rs').read_bytes()),
                      'verified/lib.rs': CONSEQ.sha((root/'verified/lib.rs').read_bytes())}
            stderr = name + '-stderr.log'
            stdout_path = root / stdout_name
            if name in ('normal-export', 'readonly-export'):
                stdout_path.write_bytes(b'MIR binary\n')
            elif name in ('normal-decode', 'readonly-decode'):
                stdout_path.write_text('struct VfMir { synthetic: true }\n')
            elif name == 'refinement':
                stdout_path.write_text('refinement succeeded\n')
            else:
                function = CONSEQ.NEGATIVE_FUNCTION if negative else CONSEQ.FUNCTION
                header = f"1.0s: verified/lib.rs(1,1-2): Verifying function '{function}'\n"
                if negative:
                    verified = (root/'verified/lib.rs').read_bytes()
                    line = CONSEQ._normal_post_line(verified)
                    text = (header +
                        f'verified/lib.rs({line},1-2): error: Cannot prove condition.\n'
                        '1 errors found (20 statements verified)\n')
                    (root/'omit-result-relation.ast.ml').write_text('(FunctionDecl ())\n')
                else:
                    text = header + '0 errors found (20 statements verified)\n'
                    (root/'consequence.ast.ml').write_text('(FunctionDecl ())\n')
                stdout_path.write_text(text)
            (root / stderr).write_text('')
            row = {'argv': argv, 'exit': 1 if negative else 0, 'timeout_seconds': 1200,
                   'fixture_before': before, 'fixture_after': before,
                   'fixture_integrity': True, 'stdout': stdout_name, 'stderr': stderr}
            if mutate:
                mutate(name, root, row)
            (root / (name + '-stage.json')).write_text(json.dumps(row, sort_keys=True))
            if exception and name == exception[0]:
                raise exception[1]
            return row
        return stage

    def test_positive_and_omit_relation_control_are_physically_audited(self):
        args, diag, matrix, matrix_audit = self.fixture()
        report = CONSEQ.run(args, diag=diag, stage=self.stage_service(args),
                            const_matrix_summary=matrix, const_matrix_audit=matrix_audit)
        self.assertTrue(report['complete'])
        self.assertEqual(report['classification'], 'COMPLETE_W4_CONST_CONSEQUENCE_SOURCE_REPORTED')
        self.assertEqual(report['cases']['positive']['classification'],
                         'CHECKED_CONSEQUENCE_SOURCE_REPORTED')
        self.assertEqual(report['cases']['omit-result-relation']['classification'],
                         'EXPECTED_NORMAL_POST_FAILURE')
        self.assertTrue(report['body_proof_run'])
        self.assertEqual(report['call_linkage'], 'UNKNOWN')
        self.assertFalse(report['accepted'])
        self.assertFalse(report['publication_allowed'])
        self.assertEqual(report['proof_credit'], 0)
        audit = CONSEQ.audit(args, diag=diag, const_matrix_summary=matrix,
                             const_matrix_audit=matrix_audit)
        self.assertTrue(audit['evidence_complete'], audit['errors'])
        self.assertEqual(audit['proof_credit'], 0)
        again = CONSEQ.audit(args, diag=diag, const_matrix_summary=matrix,
                             const_matrix_audit=matrix_audit)
        self.assertTrue(again['evidence_complete'], again['errors'])

    def test_source_contract_uses_actual_pointer_view_and_changes_only_control_premise(self):
        positive = CONSEQ._source(CONSEQ.FUNCTION, include_relation=True)
        negative = CONSEQ._source(CONSEQ.NEGATIVE_FUNCTION, include_relation=False)
        self.assertIn(b'(selected as pointer) ==', positive)
        self.assertIn(b'raw_ptr_own::<Element>()(t, selected)', positive)
        self.assertIn(b'selected == (if condition { true_val } else { false_val })', positive)
        self.assertNotIn(b'(selected as pointer) ==', negative)
        self.assertIn(b'raw_ptr_own::<Element>()(t, selected)', negative)
        self.assertIn(b'selected == (if condition { true_val } else { false_val })', negative)
        positive_runtime = CONSEQ._strip_ghost(positive)
        negative_runtime = CONSEQ._strip_ghost(negative)
        self.assertEqual(CONSEQ._strip_ghost(positive), positive_runtime)
        self.assertEqual(CONSEQ._strip_ghost(negative), negative_runtime)
        self.assertEqual([line for line in positive_runtime.splitlines() if line.strip()],
                         [line for line in negative_runtime.splitlines() if line.strip()])
        self.assertNotIn(b'/*@', positive_runtime)
        self.assertNotIn(b'//@', positive_runtime)
        self.assertNotIn(b'open raw_ptr_own', positive_runtime)
        self.assertIn(b'fn select_w4_const_post_consequence<Element>', positive_runtime)

    def test_ghost_stripping_removes_block_and_line_directives_preserving_lines(self):
        source = (b'fn f() {\n'
                  b'    /*@ open p(); @*/\n'
                  b'    //@ close q();\n'
                  b'    run();\n'
                  b'}\n')
        stripped = CONSEQ._strip_ghost(source)
        self.assertEqual(stripped.count(b'\n'), source.count(b'\n'))
        self.assertEqual(stripped, b'fn f() {\n\n\n    run();\n}\n')
        self.assertNotIn(b'//@', stripped)
        self.assertNotIn(b'/*@', stripped)
        self.assertNotIn(b'open p', stripped)
        self.assertNotIn(b'close q', stripped)

    def test_generated_original_is_clean_runtime_projection(self):
        for name, include_relation in ((CONSEQ.FUNCTION, True),
                                       (CONSEQ.NEGATIVE_FUNCTION, False)):
            verified = CONSEQ._source(name, include_relation=include_relation)
            original = CONSEQ._strip_ghost(verified)
            self.assertEqual(original, CONSEQ._strip_ghost(verified))
            self.assertNotIn(b'/*@', original)
            self.assertNotIn(b'//@', original)
            self.assertNotIn(b'open raw_ptr_own', original)
            self.assertIn(b'fn ' + name.encode() + b'<Element>', original)
            self.assertTrue(original.rstrip().endswith(b'}'))

    def test_missing_or_incomplete_matrix_fails_before_any_stage(self):
        args, diag, matrix, matrix_audit = self.fixture()
        matrix['complete'] = False
        matrix_path = args.evidence/CONSEQ.MATRIX_SUMMARY_REL
        matrix_path.write_text(json.dumps(matrix, sort_keys=True))
        matrix_audit['fractional_proof'] = matrix
        (args.evidence/CONSEQ.MATRIX_AUDIT_REL).write_text(json.dumps(matrix_audit, sort_keys=True))
        called = []
        with self.assertRaisesRegex(RuntimeError, 'const eight-row proof matrix'):
            CONSEQ.run(args, diag=diag, stage=lambda *a, **k: called.append((a,k)),
                       const_matrix_summary=matrix, const_matrix_audit=matrix_audit)
        self.assertEqual(called, [])
        report = json.loads((args.evidence/CONSEQ.SUMMARY_REL).read_text())
        self.assertFalse(report['complete'])
        self.assertIn('RuntimeError', report['exception']['type'])

    def test_supplied_matrix_must_match_physical_audit_and_rows(self):
        args, diag, matrix, matrix_audit = self.fixture()
        matrix_audit = copy.deepcopy(matrix_audit)
        matrix_audit['fractional_proof']['rows']['positive']['status'] = 'FAILED'
        with self.assertRaisesRegex(RuntimeError, 'supplied const matrix audit differs'):
            CONSEQ.run(args, diag=diag, stage=self.stage_service(args),
                       const_matrix_summary=matrix, const_matrix_audit=matrix_audit)

    def test_timeout_wrong_stage_result_and_source_drift_preserve_incomplete_summary(self):
        for mutation in (
                lambda name, _root, row: row.update(exit=124) if name == 'normal-export' else None,
                lambda name, _root, row: row.update(timeout_seconds=1201) if name == 'normal-export' else None,
                lambda name, _root, row: row.update(fixture_integrity=False) if name == 'normal-export' else None,
        ):
            args, diag, matrix, matrix_audit = self.fixture()
            with self.assertRaises(RuntimeError):
                CONSEQ.run(args, diag=diag, stage=self.stage_service(args, mutate=mutation),
                           const_matrix_summary=matrix, const_matrix_audit=matrix_audit)
            report = json.loads((args.evidence/CONSEQ.SUMMARY_REL).read_text())
            self.assertFalse(report['complete'])
            self.assertEqual(report['accepted'], False)
        args, diag, matrix, matrix_audit = self.fixture()
        def drift(name, root, row):
            if name == 'normal-export':
                (root/'verified/lib.rs').write_bytes((root/'verified/lib.rs').read_bytes()+b'// drift\n')
        with self.assertRaisesRegex(RuntimeError, 'stage failed|source snapshot differs'):
            CONSEQ.run(args, diag=diag, stage=self.stage_service(args, mutate=drift),
                       const_matrix_summary=matrix, const_matrix_audit=matrix_audit)
        report = json.loads((args.evidence/CONSEQ.SUMMARY_REL).read_text())
        self.assertFalse(report['complete'])

    def test_negative_must_fail_at_post_not_elsewhere_or_succeed(self):
        args, diag, matrix, matrix_audit = self.fixture()
        def wrong(name, _root, row):
            if name == 'omit-result-relation-proof':
                row['exit'] = 0
        with self.assertRaisesRegex(RuntimeError, 'stage failed|normal post'):
            CONSEQ.run(args, diag=diag, stage=self.stage_service(args, mutate=wrong),
                       const_matrix_summary=matrix, const_matrix_audit=matrix_audit)
        args, diag, matrix, matrix_audit = self.fixture()
        def wrong_line(name, root, row):
            if name == 'omit-result-relation-proof':
                expected = CONSEQ._normal_post_line((root/'verified/lib.rs').read_bytes())
                (root/row['stdout']).write_text(
                    f"1.0s: verified/lib.rs(1,1-2): Verifying function '{CONSEQ.NEGATIVE_FUNCTION}'\n"
                    f'verified/lib.rs({expected+1},1-2): error: Cannot prove condition.\n'
                    '1 errors found (20 statements verified)\n')
        with self.assertRaisesRegex(RuntimeError, 'stage failed|normal post'):
            CONSEQ.run(args, diag=diag, stage=self.stage_service(args, mutate=wrong_line),
                       const_matrix_summary=matrix, const_matrix_audit=matrix_audit)

    def test_wrong_stage_command_and_missing_ast_refuse(self):
        args, diag, matrix, matrix_audit = self.fixture()
        def wrong_argv(name, _root, row):
            if name == 'consequence-proof':
                row['argv'] = ['verifast', 'different-source.rs']
        with self.assertRaisesRegex(RuntimeError, 'stage command/output differs'):
            CONSEQ.run(args, diag=diag, stage=self.stage_service(args, mutate=wrong_argv),
                       const_matrix_summary=matrix, const_matrix_audit=matrix_audit)

        args, diag, matrix, matrix_audit = self.fixture()
        original_stage = self.stage_service(args)
        def missing_ast(name, *call_args):
            row = original_stage(name, *call_args)
            if name == 'consequence-proof':
                (call_args[1]/'consequence.ast.ml').unlink()
            return row
        with self.assertRaisesRegex(RuntimeError, 'AST artifact missing'):
            CONSEQ.run(args, diag=diag, stage=missing_ast,
                       const_matrix_summary=matrix, const_matrix_audit=matrix_audit)

    def test_original_stage_exception_is_rethrown_with_partial_artifact_inventory(self):
        args, diag, matrix, matrix_audit = self.fixture()
        failure = KeyboardInterrupt('synthetic stage interruption')
        with self.assertRaises(KeyboardInterrupt) as caught:
            CONSEQ.run(args, diag=diag,
                       stage=self.stage_service(args, exception=('readonly-export', failure)),
                       const_matrix_summary=matrix, const_matrix_audit=matrix_audit)
        self.assertIs(caught.exception, failure)
        report = json.loads((args.evidence/CONSEQ.SUMMARY_REL).read_text())
        self.assertFalse(report['complete'])
        self.assertEqual(report['exception']['type'], 'KeyboardInterrupt')
        self.assertGreater(len(report['artifact_inventory']), 0)

    def test_physical_source_log_ast_matrix_and_tool_drift_are_audited(self):
        args, diag, matrix, matrix_audit = self.fixture()
        report = CONSEQ.run(args, diag=diag, stage=self.stage_service(args),
                            const_matrix_summary=matrix, const_matrix_audit=matrix_audit)
        source = args.evidence/CONSEQ.SUMMARY_REL.parent/'positive'/'verified/lib.rs'
        source.write_bytes(source.read_bytes()+b'// tampered\n')
        audit = CONSEQ.audit(args, diag=diag, const_matrix_summary=matrix,
                             const_matrix_audit=matrix_audit)
        self.assertFalse(audit['evidence_complete'])
        self.assertTrue(any('exact source/ghost-strip' in error for error in audit['errors']))

        args, diag, matrix, matrix_audit = self.fixture()
        CONSEQ.run(args, diag=diag, stage=self.stage_service(args),
                   const_matrix_summary=matrix, const_matrix_audit=matrix_audit)
        diag.generation += 1
        audit = CONSEQ.audit(args, diag=diag, const_matrix_summary=matrix,
                             const_matrix_audit=matrix_audit)
        self.assertFalse(audit['evidence_complete'])
        self.assertTrue(any('tool identities differ' in error for error in audit['errors']))

    def test_null_wrong_type_and_missing_stage_are_incomplete(self):
        for bad in (None, 'bad', 7):
            args, diag, matrix, matrix_audit = self.fixture()
            with self.assertRaises(Exception):
                CONSEQ.run(args, diag=diag, stage=lambda *a, **k: bad,
                           const_matrix_summary=matrix, const_matrix_audit=matrix_audit)
        args, diag, matrix, matrix_audit = self.fixture()
        def missing(name, argv, root, env, hashes, deadline, cap, stdin_name=None, stdout_name=None):
            if name == 'normal-export':
                return {'exit': None, 'skipped': 'not run'}
            return self.stage_service(args)(name, argv, root, env, hashes, deadline, cap,
                                            stdin_name, stdout_name)
        with self.assertRaises(Exception):
            CONSEQ.run(args, diag=diag, stage=missing,
                       const_matrix_summary=matrix, const_matrix_audit=matrix_audit)


if __name__ == '__main__':
    unittest.main()
