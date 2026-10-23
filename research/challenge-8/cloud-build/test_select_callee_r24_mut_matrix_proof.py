import importlib.util
import ast
import json
import shutil
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
from types import SimpleNamespace

MODULE_PATH = Path(__file__).with_name('select-callee-r24-mut-matrix-proof.py')
SPEC = importlib.util.spec_from_file_location('r24_mut_matrix_proof_testmod', MODULE_PATH)
wrapper = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(wrapper)
REPO = MODULE_PATH.parents[3]


class FakeLib:
    SCHEMA = 'select-r24-mut-proof-v1'
    VARIANTS = ('positive', 'omit-selected-own', 'omit-unselected-own', 'no-retained-half',
        'callee-false-normal', 'callee-owner-duplicate', 'callee-owner-loss', 'callee-thread-duplicate')
    SUMMARY_REL = Path('cases/r24-mut-proof/MUT-PROOF.json')
    LANE = 'o26-select-callee-r20'
    PROFILE = 'experimental-s6-26.10-v1'
    R24_PHASE_ENV = 'SORT4_R24_SESSION_PHASE_ID'
    R21_PHASE_ENV = 'SORT4_R20_CALLEE_PHASE_ID'
    R24_PHASE = 'SORT4-ACTUAL-SELECT-2026-10-24-R24'
    R21_PHASE = 'SORT4-ACTUAL-SELECT-2026-10-23-R21'
    PINS_REL = wrapper.PINS_REL
    PINS_SHA256 = wrapper.PINS_SHA

    @staticmethod
    def _validate_route(env, build, repo):
        if not Path(repo).is_absolute() or build != env.get('CLOUD_BUILD_ID'):
            raise RuntimeError('bad fake route')

    @staticmethod
    def _validate_capture(record, pins, native):
        if not isinstance(record, dict) or record.get('complete') is not True:
            return ['capture incomplete']
        if record.get('native_build_id') != native or set(record.get('rows', {})) != set(FakeLib.VARIANTS):
            return ['capture native identity/row inventory differs']
        return []

    @staticmethod
    def _load_pins(_repo):
        return pins_fixture()


def pins_fixture():
    original, verified = b'original pair\n', b'verified pair\n'
    return {'source': {'original_sha256': wrapper.digest(original)},
        'cases': {name: {'source': {'verified_sha256': wrapper.digest(verified)}}
                  for name in FakeLib.VARIANTS}}


def fixture(tmp):
    root = Path(tmp)
    repo, evidence, toolhome = root/'repo', root/'evidence', root/'tool'
    repo.mkdir(); evidence.mkdir(); toolhome.mkdir()
    # The pinned mode, source pins, and positive evidence are copied byte-for-byte.
    for rel in (wrapper.MODE_REL, wrapper.PINS_REL, wrapper.POSITIVE_REL):
        dest = repo/rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO/rel, dest)
    pins = pins_fixture()
    source_claim = {}
    profile_actual = {}
    for rel in ('bin/refinement-checker', 'bin/rust/std/lib.rsspec', 'bin/verifast',
                'bin/vf-rust-mir-exporter', *wrapper.SOURCE_TOOL_PATHS[1:]):
        file = toolhome/rel
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(('tool-' + rel).encode())
        h = wrapper.digest(file.read_bytes())
        profile_actual[rel] = h
        source_claim[rel] = h
    # Synthetic service fixtures use a local fake source image; production keeps the fixed translator pin.
    wrapper.TRANSLATOR_SHA = profile_actual[wrapper.TRANSLATOR_PATH]
    positive = {'actual_tool_hashes_source_claim': source_claim, 'source': pins['source']}
    (evidence/wrapper.PROFILE_REL).write_text(json.dumps({'actual': profile_actual}))
    (evidence/wrapper.CONST_AUDIT_REL).write_text(json.dumps({'evidence_complete': True, 'runner_exit': 0}))
    build = '11111111-2222-3333-4444-555555555555'
    candidate = 'a'*40
    env = {'SMALLSORT_EXECUTION_PROVIDER':'cloud-build', 'SORT4_R24_SESSION_PHASE_ID':wrapper.R24,
        'SORT4_R20_CALLEE_PHASE_ID':wrapper.R21, 'SORT4_SELECT_PROFILE':'experimental-s6-26.10-v1',
        'LANE':'o26-select-callee-r20', 'CLOUD_BUILD_ID':build, 'PROOF_SHA':candidate}
    args = SimpleNamespace(repo=repo, cloud_dir=root/'cloud', evidence=evidence, tool_home=toolhome,
        schema=root/'schema', compiler_sysroot=root/'sysroot', deadline_epoch=9999999999,
        candidate=candidate, matrix_proof_mode_file=repo/wrapper.MODE_REL, output=root/'audit.json',
        runner_exit=0, failed_stage='complete')
    capture_rows, proof_rows = {}, {}
    for variant in FakeLib.VARIANTS:
        original, verified = b'original pair\n', b'verified pair\n'
        case_rel = f'cases/{variant}'
        case = evidence/case_rel
        (case/'original').mkdir(parents=True); (case/'verified').mkdir()
        (case/'original/lib.rs').write_bytes(original); (case/'verified/lib.rs').write_bytes(verified)
        source_pair = {'original/lib.rs':wrapper.digest(original), 'verified/lib.rs':wrapper.digest(verified)}
        marker = wrapper.MARKER_PREFIX+variant+wrapper.MARKER_SUFFIX
        logname = f'r24-mut-proof-{variant}.log'
        (case/logname).write_text(marker+'\n')
        capture_rows[variant] = {'original_sha256': source_pair['original/lib.rs'],
            'verified_sha256': source_pair['verified/lib.rs'], 'case_path':case_rel}
        stage = {'status':'RAN','exit':0 if variant=='positive' else 1,
            'source_unchanged':True,'source_before':source_pair,'source_after':source_pair,
            'intrinsic_gate_active':False,'pointer_drop_gate_active':False,
            'argv':[str(toolhome/'bin/verifast'),'-rustc_args','--edition 2021','-verbose','1','verified/lib.rs'],
            'stdout':logname,'stderr':logname,'build_id':build}
        proof_rows[variant] = {'variant':variant,'case_path':case_rel,
            'stage_name':'r24-mut-proof-'+variant,'proof_stage':stage,
            'source_before':source_pair,'source_after':source_pair,'source_intact':True,
            'classification':'POSITIVE_PROOF_STAGE_RAN_SOURCE_INTACT' if variant=='positive' else 'UNKNOWN_UNCLASSIFIED',
            'native_marker_seen':1 if variant=='positive' else None,
            'errors':[] if variant=='positive' else [wrapper.NEGATIVE_SENTINEL]}
    capture = {'complete':True,'native_build_id':build,'r24_session_phase_id':wrapper.R24,
        'r21_route_phase_id':wrapper.R21,'provider_record':{'provider':'cloud-build','build_id':build,
        'project':'smallsort-ci','region':'global','os':'ubuntu-22.04','arch':'x86_64'},'rows':capture_rows}
    library_summary = {'schema':FakeLib.SCHEMA,'proof_mode':'all8','proof_variants':list(FakeLib.VARIANTS),
        'native_build_id':build,'candidate':candidate,'complete_source_observation':capture,'rows':proof_rows,
        'complete':False,'classification':'INCOMPLETE_MUTABLE_PROOF','body_proof_run':True,
        'accepted':False,'proof_credit':0,'publication_allowed':False,
        'typed_admission':False,
        'r24_session_phase_id':wrapper.R24,'r21_route_phase_id':wrapper.R21,
        'provider':'cloud-build','lane':FakeLib.LANE,'profile':FakeLib.PROFILE,
        'pins':{'path':wrapper.PINS_REL.as_posix(),'sha256':wrapper.PINS_SHA}}
    return args, env, pins, positive, library_summary, evidence


class MatrixProofWrapperTests(unittest.TestCase):
    def run_fake(self, mutate=None, exception=None):
        tmp = tempfile.TemporaryDirectory(); self.addCleanup(tmp.cleanup)
        args, env, pins, positive, summary, evidence = fixture(tmp.name)
        if mutate: mutate(summary, evidence)
        def library_runner(_args, _lib):
            if exception: raise exception
            path = evidence/FakeLib.SUMMARY_REL
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(summary))
            return summary
        result = wrapper.run(args, lib=FakeLib, library_runner=library_runner,
            pins_loader=lambda _repo:pins, positive_loader=lambda _repo:positive, env=env)
        return result, args, evidence

    def test_all8_clean_diagnostic_collection(self):
        report, _, _ = self.run_fake()
        self.assertTrue(report['complete'])
        self.assertFalse(report['targets_pinned'])
        self.assertEqual(report['proof_credit'], 0)
        self.assertEqual(set(report['rows']), set(FakeLib.VARIANTS))
        self.assertEqual(report['rows']['callee-owner-loss']['classification'], 'UNKNOWN_UNCLASSIFIED')

    def test_error_exit_and_timeout_fail_closed(self):
        def mutate(s, _e): s['rows']['positive']['proof_stage']['exit']=2
        report, _, _ = self.run_fake(mutate)
        self.assertFalse(report['complete'])
        self.assertTrue(any('positive stage exit' in x for x in report['errors']))
        def timeout(s, _e):
            st=s['rows']['positive']['proof_stage']; st.update(status='TIMEOUT', timeout=True)
        report, _, _ = self.run_fake(timeout)
        self.assertTrue(any('timed out' in x for x in report['errors']))

    def test_partial_missing_null_wrongtype_and_not_run(self):
        for mutate in (
            lambda s,e: s.update(rows={k:v for k,v in s['rows'].items() if k!='positive'}),
            lambda s,e: s['rows'].pop('positive'),
            lambda s,e: s['rows']['positive'].update(proof_stage=None),
            lambda s,e: s['rows']['positive'].update(proof_stage='wrong-type'),
            lambda s,e: s['rows']['positive']['proof_stage'].update(status='NOT_RUN'),
        ):
            report, _, _ = self.run_fake(mutate)
            self.assertFalse(report['complete'])

    def test_incomplete_capture_rejected_before_row_credit(self):
        def partial(summary, _evidence): summary['complete_source_observation']['complete'] = False
        report, _, _ = self.run_fake(partial)
        self.assertFalse(report['complete'])
        self.assertTrue(any('capture incomplete' in item for item in report['errors']))

    def test_null_or_missing_capture_rows_is_incomplete_not_exception(self):
        for mutate in (
            lambda summary, _evidence: summary.update(complete_source_observation=None),
            lambda summary, _evidence: summary['complete_source_observation'].pop('rows'),
            lambda summary, _evidence: summary['complete_source_observation']['rows'].pop('positive'),
        ):
            report, _, _ = self.run_fake(mutate)
            self.assertFalse(report['complete'])
            self.assertTrue(report['errors'])

    def test_case_path_must_match_capture_row_even_if_bytes_match(self):
        def wrong_case(summary, _evidence):
            summary['rows']['positive']['case_path'] = summary['rows']['omit-selected-own']['case_path']
        report, _, _ = self.run_fake(wrong_case)
        self.assertFalse(report['complete'])
        self.assertTrue(any('proof case path differs from current fingerprint row' in x
                            for x in report['errors']))

    def test_original_summary_boundaries_cannot_be_recast(self):
        for key, value in (
            ('accepted', True), ('publication_allowed', True), ('proof_credit', 1),
            ('complete', True), ('classification', 'COMPLETE'), ('body_proof_run', False),
            ('typed_admission', True), ('semantic_rule_enabled', True),
            ('r24_session_phase_id', 'wrong'), ('lane', 'wrong'),
            ('provider', 'wrong'), ('profile', 'wrong'),
            ('pins', {'path':'wrong','sha256':'0'*64}),
        ):
            def mutate(summary, _evidence, key=key, value=value): summary[key] = value
            report, _, _ = self.run_fake(mutate)
            self.assertFalse(report['complete'], key)

    def test_negative_exit_zero_wrong_marker_duplicate_and_fatal(self):
        def run_mutation(change):
            def mutate(s,e):
                variant='callee-owner-loss'; case=e/s['rows'][variant]['case_path']
                change(s['rows'][variant], case, variant)
            return self.run_fake(mutate)[0]
        report=run_mutation(lambda row,case,v:row['proof_stage'].update(exit=0))
        self.assertFalse(report['complete'])
        report=run_mutation(lambda row,case,v:(case/f'r24-mut-proof-{v}.log').write_text('wrong marker\n'))
        self.assertFalse(report['complete'])
        report=run_mutation(lambda row,case,v:(case/f'r24-mut-proof-{v}.log').write_text(
            wrapper.MARKER_PREFIX+v+wrapper.MARKER_SUFFIX+'\n'+wrapper.MARKER_PREFIX+v+wrapper.MARKER_SUFFIX+'\n'))
        self.assertFalse(report['complete'])
        report=run_mutation(lambda row,case,v:(case/f'r24-mut-proof-{v}.log').write_text(
            wrapper.MARKER_PREFIX+v+wrapper.MARKER_SUFFIX+'\nFatal error: synthetic\n'))
        self.assertFalse(report['complete'])

    def test_source_target_mismatch_unsafe_path_and_drift(self):
        def bad_stage(s,e): s['rows']['positive']['proof_stage']['source_after']={'wrong':'target'}
        self.assertFalse(self.run_fake(bad_stage)[0]['complete'])
        def unsafe(s,e): s['rows']['positive']['case_path']='../../outside'
        self.assertFalse(self.run_fake(unsafe)[0]['complete'])
        def drift(s,e):
            case=e/s['rows']['positive']['case_path']; (case/'verified/lib.rs').write_bytes(b'drift')
        self.assertFalse(self.run_fake(drift)[0]['complete'])

    def test_stage_log_identity_and_duplicate_marker_count(self):
        def bad(s,e):
            row=s['rows']['positive']; row['proof_stage']['stdout']='wrong.log'
        self.assertFalse(self.run_fake(bad)[0]['complete'])

    def test_exception_keeps_partial_and_reraises(self):
        tmp=tempfile.TemporaryDirectory(); self.addCleanup(tmp.cleanup)
        args,env,pins,positive,summary,evidence=fixture(tmp.name)
        def boom(_args,_lib): raise ValueError('synthetic matrix runner failure')
        with self.assertRaisesRegex(ValueError,'synthetic matrix runner failure'):
            wrapper.run(args,lib=FakeLib,library_runner=boom,pins_loader=lambda _repo:pins,
                positive_loader=lambda _repo:positive,env=env)
        partial=json.loads((evidence/wrapper.SUMMARY_REL).read_text())
        self.assertEqual(partial['exception']['type'],'ValueError')
        self.assertFalse(partial['complete'])

    def test_partial_write_failure_does_not_mask_library_exception(self):
        tmp=tempfile.TemporaryDirectory(); self.addCleanup(tmp.cleanup)
        args,env,pins,positive,summary,evidence=fixture(tmp.name)
        original_write=wrapper.write_json
        wrapper.write_json=lambda *_args: (_ for _ in ()).throw(OSError('synthetic summary write failure'))
        try:
            with self.assertRaisesRegex(ValueError,'original library exception'):
                wrapper.run(args,lib=FakeLib,
                    library_runner=lambda *_args: (_ for _ in ()).throw(ValueError('original library exception')),
                    pins_loader=lambda _repo:pins,positive_loader=lambda _repo:positive,env=env)
        finally:
            wrapper.write_json=original_write

    def test_audit_missing_tools_returns_incomplete_report(self):
        tmp=tempfile.TemporaryDirectory(); self.addCleanup(tmp.cleanup)
        args,env,pins,positive,summary,evidence=fixture(tmp.name)
        args.tool_home=None
        report=wrapper.audit(args,lib=FakeLib,env=env)
        self.assertFalse(report['evidence_complete'])
        self.assertFalse(report['verification_accepted'])
        self.assertTrue(args.output.is_file())

    def test_frozen_library_summary_shape_does_not_require_absent_field(self):
        source = (MODULE_PATH.parent/'select-callee-r24-mut-proof.py').read_text()
        tree = ast.parse(source)
        keys = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == 'summary':
                if isinstance(node.value, ast.Dict):
                    keys = {key.value for key in node.value.keys if isinstance(key, ast.Constant)}
                    break
        self.assertIn('typed_admission', keys)
        self.assertNotIn('semantic_rule_enabled', keys)
        report, _, _ = self.run_fake()
        self.assertTrue(report['complete'])

    def test_audit_bad_candidate_mode_or_pins_writes_incomplete_json(self):
        for change in ('candidate', 'mode', 'pins'):
            report, args, evidence = self.run_fake()
            if change == 'candidate': args.candidate = None
            elif change == 'mode': args.matrix_proof_mode_file = args.repo/'missing-mode.json'
            else: FakeLib._load_pins = staticmethod(lambda _repo: None)
            try:
                audited = wrapper.audit(args, lib=FakeLib, env={
                    'SMALLSORT_EXECUTION_PROVIDER':'cloud-build',
                    'SORT4_R24_SESSION_PHASE_ID':wrapper.R24,
                    'SORT4_R20_CALLEE_PHASE_ID':wrapper.R21,
                    'SORT4_SELECT_PROFILE':'experimental-s6-26.10-v1',
                    'LANE':'o26-select-callee-r20',
                    'CLOUD_BUILD_ID':'11111111-2222-3333-4444-555555555555',
                    'PROOF_SHA':'a'*40})
                self.assertFalse(audited['evidence_complete'])
                self.assertTrue(args.output.is_file())
                self.assertFalse(audited['verification_accepted'])
            finally:
                FakeLib._load_pins = staticmethod(lambda _repo: pins_fixture())

    def test_good_audit_recomputes_collection_and_detects_later_log_drift(self):
        report,args,evidence=self.run_fake()
        with patch.object(wrapper,'_positive_evidence',lambda _repo: {
            'actual_tool_hashes_source_claim':report['tool_hashes'], 'source':pins_fixture()['source']}):
            env={'SMALLSORT_EXECUTION_PROVIDER':'cloud-build',
                 'SORT4_R24_SESSION_PHASE_ID':wrapper.R24,'SORT4_R20_CALLEE_PHASE_ID':wrapper.R21,
                 'SORT4_SELECT_PROFILE':'experimental-s6-26.10-v1','LANE':'o26-select-callee-r20',
                 'CLOUD_BUILD_ID':'11111111-2222-3333-4444-555555555555','PROOF_SHA':'a'*40}
            result=wrapper.audit(args,lib=FakeLib,env=env)
            self.assertTrue(result['evidence_complete'],result['errors'])
            log=evidence/report['rows']['callee-owner-loss']['log']['path']
            log.write_text(log.read_text()+'synthetic late drift\n')
            result=wrapper.audit(args,lib=FakeLib,env=env)
            self.assertFalse(result['evidence_complete'])
            self.assertFalse(result['verification_accepted'])


if __name__=='__main__': unittest.main()
