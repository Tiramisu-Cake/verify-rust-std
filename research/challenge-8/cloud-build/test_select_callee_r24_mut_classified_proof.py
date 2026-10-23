import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

MODULE_PATH = Path(__file__).with_name('select-callee-r24-mut-classified-proof.py')
SPEC = importlib.util.spec_from_file_location('r24_mut_classified_proof_testmod', MODULE_PATH)
classified = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(classified)
REPO = MODULE_PATH.parents[3]


class FakeProofLibrary:
    SCHEMA = 'select-r24-mut-proof-v1'
    VARIANTS = ('positive', 'omit-selected-own', 'omit-unselected-own', 'no-retained-half',
        'callee-false-normal', 'callee-owner-duplicate', 'callee-owner-loss', 'callee-thread-duplicate')
    LANE = 'o26-select-callee-r20'
    PROFILE = 'experimental-s6-26.10-v1'
    PINS_REL = Path('research/challenge-8/task-history/select-callee-r24/P2-MUT-MATRIX-PINS.json')
    PINS_SHA256 = '5aee793196c2e0ab5960f1c0ea4aab8880ca68e61d74876363e2ccf3febadbed'
    NEGATIVE_SENTINEL = 'negative diagnostic acceptance is not pinned'

    @staticmethod
    def _validate_route(env, build, repo):
        if build != env.get('CLOUD_BUILD_ID') or not Path(repo).is_absolute():
            raise RuntimeError('bad fake route')

    @staticmethod
    def _load_pins(_repo):
        return pins_fixture()


class FakeDiagnostic:
    SUMMARY_REL = Path('cases/r24-mut-matrix-proof/MUT-MATRIX-PROOF.json')
    ORIGINAL_PROOF_REL = Path('cases/r24-mut-proof/MUT-PROOF.json')
    POSITIVE_REL = Path('research/challenge-8/task-history/select-callee-r24/P2-MUT-POSITIVE-EVIDENCE.json')
    POSITIVE_SHA = '5b6f58485534622f66c246d37e17bd2f43cd2d2e2b020cc5c4c020d30374ee2a'

    @staticmethod
    def load_library(_cloud):
        return FakeProofLibrary

    @staticmethod
    def _validate_context(args, env, lib):
        lib._validate_route(env, env.get('CLOUD_BUILD_ID'), args.repo)
        if args.candidate != env.get('PROOF_SHA'):
            raise RuntimeError('bad fake candidate')
        return env['CLOUD_BUILD_ID']

    @staticmethod
    def validate_mode(repo, path, _lib):
        if not path.is_file() or path.resolve() != (repo/classified.DIAGNOSTIC_MODE_REL).resolve():
            raise RuntimeError('bad diagnostic mode')
        return {}

    @staticmethod
    def audit(*_args, **_kwargs):
        return {'evidence_complete': True, 'verification_accepted': False}


class FakeTargets:
    VARIANTS = ('callee-false-normal', 'callee-owner-duplicate', 'callee-owner-loss',
        'callee-thread-duplicate', 'no-retained-half', 'omit-selected-own', 'omit-unselected-own')
    CURRENT_LOG_RELATIVE = 'cases/r24-mut-matrix-fingerprint/variants/{variant}/r24-mut-proof-{variant}.log'
    TOOL_SPEC_FILE = 'bin/rust/std/lib.rsspec'

    @staticmethod
    def validate_target_map(target_map, sources, tool_spec, **_kwargs):
        if not isinstance(target_map, dict) or set(sources) != set(FakeTargets.VARIANTS) or not tool_spec:
            raise ValueError('bad synthetic target map inputs')
        return {'schema':'select-r24-mut-control-target-validation-v1',
            'status':'TARGET_MAP_VALIDATED_NOT_ACCEPTED','classification':'SOURCE_REPORTED',
            'targets':{key:{'variant':key,'observed':True} for key in FakeTargets.VARIANTS},
            'accepted':False,'publication_allowed':False,'proof_credit':0}

    @staticmethod
    def match_first_and_only_error(variant, _map, sources, _spec, text, *, log_bytes,
            log_observation, expected_build_id, **_kwargs):
        expected_marker = (f'SORT4-R24-MUTABLE-CERTIFICATES: case={variant} bodies=9 '
            'pointer_drop=1 assume_init=1; raw MIR cleanup retained')
        if (not isinstance(sources.get(variant), bytes) or
            log_observation.get('build_id') != expected_build_id or
            log_observation.get('variant') != variant or
            log_observation.get('stage', {}).get('status') != 'RAN' or
            log_observation.get('stage', {}).get('exit') != 1 or
            text.splitlines().count(expected_marker) != 1 or
            len(log_bytes) == 0):
            raise ValueError('synthetic exact diagnostic mismatch')
        if 'error:' not in text:
            raise ValueError('synthetic diagnostic missing')
        return {'schema':'select-r24-mut-control-diagnostic-observation-v1',
            'current_build_id':expected_build_id,'variant':variant,
            'matches_first_and_only_error':True,'classification':'SOURCE_REPORTED',
            'accepted':False,'publication_allowed':False,'proof_credit':0}


def pins_fixture():
    original = b'original mutable source\n'
    verified = b'verified mutable source\n'
    return {'source':{'original_sha256':classified.digest(original)},
        'cases':{variant:{'source':{'verified_sha256':classified.digest(verified)}}
                 for variant in FakeProofLibrary.VARIANTS}}


def fixture(tmp):
    root=Path(tmp); repo=root/'repo'; evidence=root/'evidence'; toolhome=root/'tool'
    repo.mkdir(); evidence.mkdir(); toolhome.mkdir()
    for rel in (classified.CLASSIFIED_MODE_REL, classified.DIAGNOSTIC_MODE_REL, classified.TARGET_MAP_REL):
        dest=repo/rel; dest.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(REPO/rel,dest)
    spec=toolhome/'bin/rust/std/lib.rsspec'; spec.parent.mkdir(parents=True); spec.write_bytes(b'// synthetic spec\n')
    build='11111111-2222-3333-4444-555555555555'; candidate='c'*40
    env={'SMALLSORT_EXECUTION_PROVIDER':'cloud-build','SORT4_R24_SESSION_PHASE_ID':classified.R24,
        'SORT4_R20_CALLEE_PHASE_ID':classified.R21,'SORT4_SELECT_PROFILE':'experimental-s6-26.10-v1',
        'LANE':'o26-select-callee-r20','CLOUD_BUILD_ID':build,'PROOF_SHA':candidate}
    args=SimpleNamespace(repo=repo,cloud_dir=root/'cloud',evidence=evidence,tool_home=toolhome,
        schema=root/'schema',compiler_sysroot=root/'sysroot',deadline_epoch=9999999999,
        candidate=candidate,classified_mode_file=repo/classified.CLASSIFIED_MODE_REL,
        matrix_proof_mode_file=repo/classified.DIAGNOSTIC_MODE_REL,
        mode_file=root/'capture-mode',mode_sha256='0'*64,matrix_mode_file=root/'matrix-mode',
        matrix_mode_sha256='1'*64,runner_exit=0,failed_stage='complete',output=root/'audit.json')
    pins=pins_fixture(); rows={}; variant_rows={}
    original=b'original mutable source\n'; verified=b'verified mutable source\n'
    for variant in FakeProofLibrary.VARIANTS:
        case_rel=f'cases/r24-mut-matrix-fingerprint/variants/{variant}'
        case=evidence/case_rel
        (case/'original').mkdir(parents=True); (case/'verified').mkdir()
        (case/'original/lib.rs').write_bytes(original); (case/'verified/lib.rs').write_bytes(verified)
        pair={'original/lib.rs':classified.digest(original),'verified/lib.rs':classified.digest(verified)}
        logname=f'r24-mut-proof-{variant}.log'
        marker=(f'SORT4-R24-MUTABLE-CERTIFICATES: case={variant} bodies=9 '
            'pointer_drop=1 assume_init=1; raw MIR cleanup retained')
        (case/logname).write_text(marker+'\nverified/lib.rs(1,1-2): error: expected diagnostic\n')
        raw=(case/logname).read_bytes()
        stage={'status':'RAN','exit':0 if variant=='positive' else 1,'argv':[
            str(toolhome/'bin/verifast'),'-rustc_args','--edition 2021','-verbose','1','verified/lib.rs'],
            'stdout':logname,'stderr':logname,'source_before':pair,'source_after':pair,
            'source_unchanged':True,'intrinsic_gate_active':False,'pointer_drop_gate_active':False}
        variant_rows[variant]={'case_path':case_rel,'source_before':pair,'source_after':pair,
            'source_intact':True,'original_stage_record':stage,'stage_status':'RAN',
            'stage_exit':stage['exit'],'log':{'path':case_rel+'/'+logname,'sha256':classified.digest(raw),
            'bytes':len(raw)},'native_marker_count':1,'errors':[],
            'classification':'POSITIVE_STAGE_RAN_SOURCE_REPORTED' if variant=='positive' else 'UNKNOWN_UNCLASSIFIED'}
        rows[variant]={'case_path':case_rel,'original_sha256':pair['original/lib.rs'],
            'verified_sha256':pair['verified/lib.rs']}
    diag_report={'schema':'select-r24-mut-matrix-proof-v1','classification':
        'COMPLETE_DIAGNOSTIC_COLLECTION_TARGETS_UNPINNED','complete':True,'candidate':candidate,
        'native_build_id':build,'r24_session_phase_id':classified.R24,'r21_route_phase_id':classified.R21,
        'provider':'cloud-build','lane':'o26-select-callee-r20','profile':'experimental-s6-26.10-v1',
        'matrix_pins_ref':{'path':FakeProofLibrary.PINS_REL.as_posix(),'sha256':FakeProofLibrary.PINS_SHA256},
        'positive_evidence_ref':{'path':FakeDiagnostic.POSITIVE_REL.as_posix(),'sha256':FakeDiagnostic.POSITIVE_SHA},
        'targets_pinned':False,'accepted':False,'publication_allowed':False,'proof_credit':0,
        'tool_hashes':{'bin/rust/std/lib.rsspec':classified.digest(spec.read_bytes())},
        'rows':variant_rows}
    return args,env,pins,diag_report,rows,evidence


class ClassifiedProofTests(unittest.TestCase):
    def run_fixture(self, mutate=None, raise_error=None):
        temp=tempfile.TemporaryDirectory(); self.addCleanup(temp.cleanup)
        args,env,pins,diag_report,rows,evidence=fixture(temp.name)
        if mutate: mutate(diag_report,evidence)
        def runner(_args,_diag,_lib):
            if raise_error: raise raise_error
            dpath=evidence/FakeDiagnostic.SUMMARY_REL; dpath.parent.mkdir(parents=True,exist_ok=True)
            dpath.write_text(json.dumps(diag_report))
            opath=evidence/FakeDiagnostic.ORIGINAL_PROOF_REL; opath.parent.mkdir(parents=True,exist_ok=True)
            opath.write_text('{"synthetic":true}')
            return diag_report
        record=classified.run(args,diag=FakeDiagnostic,targets=FakeTargets,
            diagnostic_runner=runner,env=env)
        return record,args,env,evidence,diag_report

    def test_seven_exact_refusals_remain_source_reported_only(self):
        report,_,_,_,_=self.run_fixture()
        self.assertTrue(report['complete'])
        self.assertTrue(report['targets_pinned'])
        self.assertEqual(set(report['rows']),set(FakeProofLibrary.VARIANTS))
        for variant in classified.NEGATIVES:
            self.assertEqual(report['rows'][variant]['classification'],
                'NEGATIVE_SOLE_TARGET_MATCHED_SOURCE_REPORTED')
            self.assertFalse(report['rows'][variant]['accepted'])
            self.assertEqual(report['rows'][variant]['proof_credit'],0)
        self.assertFalse(report['accepted'])
        self.assertFalse(report['publication_allowed'])

    def test_real_frozen_module_boundary_keeps_route_api_on_loaded_library(self):
        cloud = REPO/'research/challenge-8/cloud-build'
        diagnostic, targets = classified.load_services(cloud)
        prooflib = diagnostic.load_library(cloud)
        self.assertTrue(callable(diagnostic.run))
        self.assertTrue(callable(diagnostic.audit))
        for name in ('LANE','PROFILE','VARIANTS','_load_pins','_validate_route'):
            self.assertFalse(hasattr(diagnostic,name), name)
            self.assertTrue(hasattr(prooflib,name), name)
        self.assertTrue(callable(targets.validate_target_map))
        self.assertTrue(callable(targets.match_first_and_only_error))

    def test_wrong_marker_and_fatal_or_diagnostic_mismatch_refused(self):
        def wrong_marker(_summary,evidence):
            path=evidence/'cases/r24-mut-matrix-fingerprint/variants/callee-owner-loss/r24-mut-proof-callee-owner-loss.log'
            path.write_text('wrong marker\nverified/lib.rs(1,1-2): error: expected diagnostic\n')
        self.assertFalse(self.run_fixture(wrong_marker)[0]['complete'])
        def fatal(_summary,evidence):
            path=evidence/'cases/r24-mut-matrix-fingerprint/variants/callee-owner-loss/r24-mut-proof-callee-owner-loss.log'
            path.write_text('SORT4-R24-MUTABLE-CERTIFICATES: case=callee-owner-loss bodies=9 pointer_drop=1 assume_init=1; raw MIR cleanup retained\nFatal error: native exception\nerror: expected diagnostic\n')
        self.assertFalse(self.run_fixture(fatal)[0]['complete'])

    def test_changed_source_wrong_stage_timeout_and_unexpected_exit_refused(self):
        def source(_summary,evidence):
            (evidence/'cases/r24-mut-matrix-fingerprint/variants/callee-owner-loss/verified/lib.rs').write_bytes(b'drift')
        self.assertFalse(self.run_fixture(source)[0]['complete'])
        def wrong_stage(summary,_evidence): summary['rows']['callee-owner-loss']['original_stage_record']['source_after']={'x':'y'}
        self.assertFalse(self.run_fixture(wrong_stage)[0]['complete'])
        def timeout(summary,_evidence): summary['rows']['callee-owner-loss']['original_stage_record']['status']='TIMEOUT'
        self.assertFalse(self.run_fixture(timeout)[0]['complete'])
        def exit0(summary,_evidence): summary['rows']['callee-owner-loss']['original_stage_record']['exit']=0
        self.assertFalse(self.run_fixture(exit0)[0]['complete'])
        def null_stage(summary,_evidence): summary['rows']['callee-owner-loss']['original_stage_record']=None
        self.assertFalse(self.run_fixture(null_stage)[0]['complete'])

    def test_incomplete_diagnostic_matrix_remains_incomplete(self):
        def partial(summary,_evidence): summary['complete']=False
        self.assertFalse(self.run_fixture(partial)[0]['complete'])
        def null_row(summary,_evidence): summary['rows']['callee-owner-loss']=None
        self.assertFalse(self.run_fixture(null_row)[0]['complete'])
        def missing_row(summary,_evidence): summary['rows'].pop('callee-owner-loss')
        self.assertFalse(self.run_fixture(missing_row)[0]['complete'])
        def null_result(summary,_evidence): summary.update(rows=None)
        self.assertFalse(self.run_fixture(null_result)[0]['complete'])

    def test_exception_preserved_with_partial_classified_summary(self):
        temp=tempfile.TemporaryDirectory(); self.addCleanup(temp.cleanup)
        args,env,_,_,_,evidence=fixture(temp.name)
        with self.assertRaisesRegex(ValueError,'synthetic diagnostic service error'):
            classified.run(args,diag=FakeDiagnostic,targets=FakeTargets,
                diagnostic_runner=lambda *_:(_ for _ in ()).throw(ValueError('synthetic diagnostic service error')),
                env=env)
        saved=json.loads((evidence/classified.SUMMARY_REL).read_text())
        self.assertEqual(saved['exception']['type'],'ValueError')

    def test_root_audit_reopens_and_rejects_changed_log(self):
        report,args,env,evidence,_=self.run_fixture()
        path=evidence/'cases/r24-mut-matrix-fingerprint/variants/callee-owner-loss/r24-mut-proof-callee-owner-loss.log'
        path.write_text('changed after classification')
        audited=classified.audit(args,diag=FakeDiagnostic,targets=FakeTargets,env=env)
        self.assertFalse(audited['evidence_complete'])
        self.assertFalse(audited['verification_accepted'])
        self.assertTrue(args.output.is_file())


if __name__=='__main__': unittest.main()
