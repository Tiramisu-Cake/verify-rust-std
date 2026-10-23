import importlib.util
import json
import re
import shlex
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

MODULE_PATH = Path(__file__).with_name('select-callee-r24-p2-entailment.py')
SPEC = importlib.util.spec_from_file_location('r24_p2_entailment_testmod', MODULE_PATH)
entailment = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(entailment)

MODEL_BYTES = (b'pred_ctor raw_ptr_own<T>()(t: thread_id_t, v: *T;) = true;\n'
               b'type_pred_def for <T> <*T>.own = raw_ptr_own::<T>;\n')


class FakeDiagnostic:
    PROFILE_REL = Path('profile-hashes.json')

    def __init__(self):
        self.tool_generation = 0

    @staticmethod
    def load_library(_cloud):
        return object()

    @staticmethod
    def _validate_context(args, _env, _lib):
        if not Path(args.repo).is_absolute():
            raise RuntimeError('repo path is not absolute')
        return '11111111-2222-3333-4444-555555555555'

    @staticmethod
    def validate_mode(_repo, path, _lib):
        if not path.is_file():
            raise RuntimeError('matrix proof mode absent')

    @staticmethod
    def _positive_evidence(_repo):
        return {'schema': 'synthetic-positive'}

    def _tool_hashes(self, _tool, _profile, _positive):
        return {'synthetic-tool-generation': str(self.tool_generation)}

    @staticmethod
    def _regular_under(root, path):
        try:
            return (not root.is_symlink() and not path.is_symlink() and path.is_file() and
                    path.resolve().is_relative_to(root.resolve()))
        except OSError:
            return False

    @staticmethod
    def write_json(path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


class P2EntailmentTests(unittest.TestCase):
    def setUp(self):
        self.old_model_sha = entailment.MODEL_SHA
        entailment.MODEL_SHA = entailment.sha(MODEL_BYTES)

    def tearDown(self):
        entailment.MODEL_SHA = self.old_model_sha

    def fixture(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        repo, cloud, evidence, tool = root/'repo', root/'cloud', root/'evidence', root/'tool'
        for path in (repo, cloud, evidence, tool): path.mkdir()
        (repo/'matrix-mode.json').write_text('{}')
        model = tool/entailment.MODEL_REL
        model.parent.mkdir(parents=True)
        model.write_bytes(MODEL_BYTES)
        args = SimpleNamespace(repo=repo, cloud_dir=cloud, evidence=evidence, tool_home=tool,
            schema=root/'VfMir.capnp', compiler_sysroot=str(root/'sysroot'),
            matrix_proof_mode_file=repo/'matrix-mode.json', deadline_epoch=9999999999,
            candidate='a'*40, output=root/'audit.json', runner_exit=0, failed_stage='complete')
        diag = FakeDiagnostic()
        return args, diag, evidence

    def stage_service(self, args, diag, *, mutation=None, raise_error=None):
        def stage(case, name, argv, stage_args, *, input_name=None, output_name=None,
                  gates=None, pointer_drop=None, cap_seconds=None):
            self.assertEqual(gates, False)
            self.assertEqual(pointer_drop, False)
            self.assertEqual(cap_seconds, 1200)
            commands = entailment.commands_for(args)
            expected_argv, expected_input, expected_output = commands[name]
            self.assertEqual(argv, expected_argv)
            self.assertEqual(input_name, expected_input)
            self.assertEqual(output_name, expected_output)
            original = (case/'original/lib.rs').read_bytes()
            verified = (case/'verified/lib.rs').read_bytes()
            source = {'original/lib.rs': entailment.sha(original),
                      'verified/lib.rs': entailment.sha(verified)}
            stdout = output_name or name+'.log'
            stderr = name+'-stderr.log' if output_name else stdout
            log = b''
            if name == 'p2-entailment-proof':
                log = (b"3.2s: verified/lib.rs(4,1-10): Verifying function "
                       b"'select_p2_post_consequence'\n"
                       b'0 errors found (24 statements verified)\n')
            case.joinpath(stdout).write_bytes(log if name == 'p2-entailment-proof' else b'output\n')
            if stderr != stdout:
                case.joinpath(stderr).write_bytes(b'\n')
            result = {'status':'RAN','exit':0,'argv':list(argv),'stdout':stdout,'stderr':stderr,
                'source_before':source,'source_after':source,'source_unchanged':True,
                'intrinsic_gate_active':False,'pointer_drop_gate_active':False,
                'timeout':False}
            if mutation:
                mutation(case, name, result, diag)
            saved = result.pop('_persisted_stage_json', None)
            case.joinpath(name+'-stage.json').write_text(saved if saved is not None else json.dumps(result))
            if raise_error and name == raise_error[0]:
                raise raise_error[1]
            return result
        return stage

    def test_clean_ghost_lemma_entailment_passes_from_physical_stage_files(self):
        args, diag, evidence = self.fixture()
        report = entailment.run(args, diag=diag, stage=self.stage_service(args, diag))
        self.assertTrue(report['complete'])
        self.assertEqual(report['scope'], 'NORMAL_POST_ENTAILMENT_ONLY; NO_CALLEE_BODY_REPLACEMENT; FALSE_UNWIND_INHERITED_FROM_CALLEE')
        self.assertEqual(report['observation']['lemma_headers'], 1)
        self.assertFalse(report['accepted'])
        self.assertFalse(report['publication_allowed'])
        self.assertEqual(report['proof_credit'], 0)
        proof_log = evidence/entailment.SUMMARY_REL.parent/'p2-entailment-proof.log'
        self.assertTrue(proof_log.is_file())
        audited = entailment.audit(args, diag=diag)
        self.assertTrue(audited['evidence_complete'])

    def test_missing_sysroot_fails_before_run_or_audit_reconstructs_commands(self):
        args, diag, evidence = self.fixture()
        args.compiler_sysroot = None
        with self.assertRaisesRegex(RuntimeError, 'compiler sysroot is required'):
            entailment.run(args, diag=diag, stage=self.stage_service(args, diag))
        self.assertFalse((evidence/entailment.SUMMARY_REL).exists())

        # A local audit must write an incomplete record and reject before
        # validate_case reconstructs stage argv with a missing sysroot.
        args, diag, _ = self.fixture()
        entailment.run(args, diag=diag, stage=self.stage_service(args, diag))
        args.compiler_sysroot = ''
        audited = entailment.audit(args, diag=diag)
        self.assertFalse(audited['evidence_complete'])
        self.assertIn('compiler sysroot is required', audited['errors'][0])
        self.assertTrue(args.output.is_file())

    def test_audit_rejects_different_nonempty_sysroot_from_run(self):
        args, diag, _ = self.fixture()
        entailment.run(args, diag=diag, stage=self.stage_service(args, diag))
        args.compiler_sysroot = str(Path(args.compiler_sysroot).parent/'other-sysroot')
        audited = entailment.audit(args, diag=diag)
        self.assertFalse(audited['evidence_complete'])
        self.assertIn('stage command/outputs differ: normal-export', audited['errors'][0])

    def test_shell_consequence_audit_passes_compiler_sysroot_argument(self):
        shell = MODULE_PATH.with_name('run-o26-select-callee-r20.sh').read_text()
        match = re.search(
            r'python3 "\$cloud_dir/select-callee-r24-p2-entailment\.py" audit \\\n(.*?)\|\| consequence_audit_exit',
            shell, re.S)
        self.assertIsNotNone(match, 'shell consequence audit invocation absent')
        argv = shlex.split(match.group(1).replace('\\\n', ' '))
        self.assertIn('--compiler-sysroot', argv)
        index = argv.index('--compiler-sysroot')
        self.assertEqual(argv[index + 1], '${compiler_sysroot:-}')

    def test_bad_stage_status_exit_timeout_and_argv_refuse(self):
        mutations = (
            lambda _c,n,row,_d: row.update(status='NOT_RUN') if n=='p2-entailment-proof' else None,
            lambda _c,n,row,_d: row.update(exit=1) if n=='p2-entailment-proof' else None,
            lambda _c,n,row,_d: row.update(timeout=True) if n=='p2-entailment-proof' else None,
            lambda _c,n,row,_d: row.update(argv=['wrong']) if n=='p2-entailment-proof' else None,
        )
        for mutate in mutations:
            args, diag, _ = self.fixture()
            with self.assertRaises(RuntimeError):
                entailment.run(args, diag=diag, stage=self.stage_service(args, diag, mutation=mutate))
            saved=json.loads((args.evidence/entailment.SUMMARY_REL).read_text())
            self.assertFalse(saved['complete'])
            self.assertTrue(saved['exception'])

    def test_null_wrongtype_and_incomplete_stage_snapshot_refuse(self):
        for bad_json in ('null', '"not-an-object"'):
            args, diag, _ = self.fixture()
            def invalid(case,name,row,_diag,bad=bad_json):
                if name=='p2-entailment-proof':
                    # The native stage result is valid; only its saved observation is malformed.
                    row['_persisted_stage_json']=bad
            with self.assertRaises(Exception):
                entailment.run(args,diag=diag,stage=self.stage_service(args,diag,mutation=invalid))
        args,diag,_=self.fixture()
        def missing(case,name,row,_diag):
            if name=='normal-export': case.joinpath('normal-mir.bin').unlink()
        with self.assertRaises(RuntimeError):
            entailment.run(args,diag=diag,stage=self.stage_service(args,diag,mutation=missing))

    def test_source_drift_and_changed_lemma_refuse(self):
        for mutation in ('source','lemma'):
            args,diag,_=self.fixture()
            def change(case,name,_row,_diag,which=mutation):
                if name=='p2-entailment-proof':
                    target=case/'verified/lib.rs' if which=='lemma' else case/'original/lib.rs'
                    target.write_bytes(target.read_bytes()+b'changed\n')
            with self.assertRaises(RuntimeError):
                entailment.run(args,diag=diag,stage=self.stage_service(args,diag,mutation=change))

    def test_missing_header_extra_diagnostic_and_missing_success_summary_refuse(self):
        changes = (
            lambda log: log.replace(b"Verifying function 'select_p2_post_consequence'", b'Verifying function other'),
            lambda log: log+b'error: unexpected diagnostic\n',
            lambda log: log.replace(b'0 errors found (24 statements verified)\n', b''),
        )
        for change in changes:
            args,diag,_=self.fixture()
            def mutate(case,name,row,_diag,transform=change):
                if name=='p2-entailment-proof':
                    path=case/'p2-entailment-proof.log'; path.write_bytes(transform(path.read_bytes()))
            with self.assertRaises(RuntimeError):
                entailment.run(args,diag=diag,stage=self.stage_service(args,diag,mutation=mutate))

    def test_tool_change_after_stage_is_detected(self):
        args,diag,_=self.fixture()
        def mutate(_case,name,_row,current_diag):
            if name=='p2-entailment-proof': current_diag.tool_generation += 1
        with self.assertRaises(RuntimeError):
            entailment.run(args,diag=diag,stage=self.stage_service(args,diag,mutation=mutate))
        saved=json.loads((args.evidence/entailment.SUMMARY_REL).read_text())
        self.assertIn('tool/model changed', saved['errors'][0])

    def test_original_stage_exception_is_preserved_with_partial_snapshot(self):
        args,diag,evidence=self.fixture()
        error=ValueError('synthetic native stage callback failure')
        with self.assertRaisesRegex(ValueError,'synthetic native stage callback failure'):
            entailment.run(args,diag=diag,stage=self.stage_service(args,diag,
                raise_error=('normal-export',error)))
        saved=json.loads((evidence/entailment.SUMMARY_REL).read_text())
        self.assertEqual(saved['exception']['type'],'ValueError')
        self.assertFalse(saved['complete'])
        case=evidence/entailment.SUMMARY_REL.parent
        self.assertTrue((case/'original/lib.rs').is_file())
        self.assertTrue((case/'verified/lib.rs').is_file())

    def test_audit_reopens_stage_log_and_tool_model_evidence(self):
        args,diag,evidence=self.fixture()
        entailment.run(args,diag=diag,stage=self.stage_service(args,diag))
        log=evidence/entailment.SUMMARY_REL.parent/'p2-entailment-proof.log'
        log.write_text('changed log')
        result=entailment.audit(args,diag=diag)
        self.assertFalse(result['evidence_complete'])
        self.assertFalse(result['accepted'])
        self.assertTrue(args.output.is_file())


if __name__=='__main__':
    unittest.main()
