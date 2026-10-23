import importlib.util
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

MODULE_PATH = Path(__file__).with_name('select-callee-r24-mut-proof.py')
SPEC = importlib.util.spec_from_file_location('select_callee_r24_mut_proof_testmod', MODULE_PATH)
proof = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(proof)


class Owner:
    @staticmethod
    def strip_ghost(data):
        return data


class Engine:
    def __init__(self, record):
        self.record = record
        self.calls = 0

    def run(self, args):
        self.calls += 1
        return self.record

    @staticmethod
    def load_old_adapter(_cloud):
        return SimpleNamespace(load_source_writers=lambda _root: {'owner': Owner()})


def fixture(tmp):
    root = Path(tmp)
    repo = root / 'repo'
    evidence = root / 'evidence'
    cloud = root / 'cloud'
    for path in (repo, evidence, cloud): path.mkdir()
    original, verified = b'source-pair\n', b'source-pair\n'
    oh, vh = proof.sha(original), proof.sha(verified)
    snapshots = {name: {'file': f'actual-nested-9-{name}.marshal', 'bytes': 1,
                        'sha256': proof.sha(name.encode())} for name in proof.SNAPSHOTS}
    pins = {'cases': {}, 'source': {'original_sha256': oh,
             'specialization': 'T = *mut Element; Element unrestricted'}}
    rows = {}
    for variant in proof.VARIANTS:
        pins['cases'][variant] = {'source': {'verified_sha256': vh}, 'snapshots': snapshots}
        case_rel = f'cases/{variant}'
        case = evidence / case_rel
        (case / 'original').mkdir(parents=True)
        (case / 'verified').mkdir()
        (case / 'original/lib.rs').write_bytes(original)
        (case / 'verified/lib.rs').write_bytes(verified)
        rows[variant] = {'complete': True, 'status': 'COMPLETE_SOURCE_REPORTED_FINGERPRINT',
            'native_build_id': '11111111-2222-3333-4444-555555555555',
            'source_unchanged': True, 'ghost_strip_identity': True,
            'original_sha256': oh, 'verified_sha256': vh, 'case_path': case_rel,
            'fingerprint': {'snapshots': snapshots}}
    location = {'complete': True, 'native_build_id': '11111111-2222-3333-4444-555555555555',
        'reproduces_positive_pins': True, 'fingerprint': {'snapshots': snapshots}}
    record = {'complete': True, 'native_build_id': '11111111-2222-3333-4444-555555555555',
              'variant_order': list(proof.VARIANTS), 'rows': rows, 'location_control': location}
    args = SimpleNamespace(repo=repo, evidence=evidence, cloud_dir=cloud, tool_home=root/'tool',
        schema=root/'schema', compiler_sysroot=root/'sysroot', deadline_epoch=9999999999,
        proof_mode='positive', proof_variants=['positive'], candidate='fake')
    env = {'SMALLSORT_EXECUTION_PROVIDER': 'cloud-build', proof.R24_PHASE_ENV: proof.R24_PHASE,
        proof.R21_PHASE_ENV: proof.R21_PHASE, 'LANE': proof.LANE,
        'SORT4_SELECT_PROFILE': proof.PROFILE, 'CLOUD_BUILD_ID': record['native_build_id']}
    return args, env, pins, record, evidence


def stage_result(variant='positive', **overrides):
    marker = proof.MARKER_PREFIX + variant + proof.MARKER_SUFFIX
    result = {'status': 'RAN', 'exit': 0, 'name': 'r24-mut-proof-' + variant,
              'source_before': {'original/lib.rs': 'source-original', 'verified/lib.rs': 'source-verified'},
              'source_after': {'original/lib.rs': 'source-original', 'verified/lib.rs': 'source-verified'},
              'log_text': marker}
    result.update(overrides)
    return result


class MutableProofRunnerTests(unittest.TestCase):
    def run_fixture(self, *, proof_cb=None, mutate=None, capture_change=None):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        args, env, pins, record, evidence = fixture(tmp.name)
        if capture_change:
            capture_change(record)
        engine = Engine(record)
        def callback(**kw):
            if mutate: mutate(kw['case'])
            value = proof_cb(**kw) if proof_cb else stage_result()
            if isinstance(value, dict):
                pair = {'original/lib.rs': proof.sha((kw['case']/'original/lib.rs').read_bytes()),
                        'verified/lib.rs': proof.sha((kw['case']/'verified/lib.rs').read_bytes())}
                if value.get('source_before', {}).get('original/lib.rs') == 'source-original':
                    value['source_before'] = pair
                if value.get('source_after', {}).get('original/lib.rs') == 'source-original':
                    value['source_after'] = pair
            return value
        result = proof.run(args, engine=engine, pins_loader=lambda _repo: pins,
                           proof_runner=callback, runtime_loader=lambda _args: {}, env=env)
        return result, engine, evidence

    def test_positive_marker_stage_success(self):
        result, engine, _ = self.run_fixture()
        self.assertEqual(engine.calls, 1)
        self.assertEqual(result['rows']['positive']['classification'], 'POSITIVE_PROOF_STAGE_RAN_SOURCE_INTACT')
        self.assertFalse(result['accepted'])
        self.assertEqual(result['proof_credit'], 0)

    def test_original_error_exit_preserved(self):
        result, _, _ = self.run_fixture(proof_cb=lambda **kw: stage_result(exit=1))
        self.assertEqual(result['rows']['positive']['proof_stage']['exit'], 1)
        self.assertIn('positive proof did not exit 0', result['rows']['positive']['errors'])

    def test_timeout_preserved(self):
        result, _, _ = self.run_fixture(proof_cb=lambda **kw: stage_result(status='TIMEOUT', timeout=True))
        self.assertEqual(result['rows']['positive']['proof_stage']['status'], 'TIMEOUT')
        self.assertIn('proof stage timed out', result['rows']['positive']['errors'])

    def test_partial_capture_stops_before_proof(self):
        def partial(record): record['rows']['callee-owner-loss']['complete'] = False
        result, _, _ = self.run_fixture(capture_change=partial)
        self.assertEqual(result['rows'], {})
        self.assertTrue(any('callee-owner-loss' in x for x in result['incomplete_reasons']))

    def test_missing_capture_row_stops_before_proof(self):
        def missing(record): del record['rows']['callee-owner-loss']
        result, _, _ = self.run_fixture(capture_change=missing)
        self.assertEqual(result['rows'], {})
        self.assertIn('fingerprint producer does not contain exactly all eight rows', result['incomplete_reasons'])

    def test_null_stage_preserved(self):
        result, _, _ = self.run_fixture(proof_cb=lambda **kw: None)
        self.assertIsNone(result['rows']['positive']['proof_stage'])
        self.assertIn('proof stage result is not an object', result['rows']['positive']['errors'])

    def test_wrong_type_stage_preserved(self):
        result, _, _ = self.run_fixture(proof_cb=lambda **kw: ['bad'])
        self.assertEqual(result['rows']['positive']['proof_stage'], ['bad'])
        self.assertIn('proof stage result is not an object', result['rows']['positive']['errors'])

    def test_explicit_not_run_preserved(self):
        result, _, _ = self.run_fixture(proof_cb=lambda **kw: stage_result(status='NOT_RUN'))
        self.assertEqual(result['rows']['positive']['proof_stage']['status'], 'NOT_RUN')
        self.assertIn('proof stage status is not RAN', result['rows']['positive']['errors'])

    def test_source_stage_target_mismatch(self):
        result, _, _ = self.run_fixture(proof_cb=lambda **kw: stage_result(source_after={'wrong': 'target'}))
        self.assertIn('proof stage source target mismatch or drift', result['rows']['positive']['errors'])

    def test_wrong_case_marker_refused(self):
        result, _, _ = self.run_fixture(proof_cb=lambda **kw: stage_result('omit-selected-own'))
        self.assertIn('positive native certificate marker missing/duplicated/wrong-case',
                      result['rows']['positive']['errors'])

    def test_duplicate_marker_refused(self):
        def duplicate(**kw):
            value = stage_result()
            value['log_text'] += '\n' + proof.MARKER_PREFIX + 'positive' + proof.MARKER_SUFFIX
            return value
        result, _, _ = self.run_fixture(proof_cb=duplicate)
        self.assertIn('positive native certificate marker missing/duplicated/wrong-case',
                      result['rows']['positive']['errors'])

    def test_dirty_source_detected_after_stage(self):
        def dirty(case): (case/'verified/lib.rs').write_bytes(b'dirty')
        result, _, _ = self.run_fixture(mutate=dirty)
        self.assertFalse(result['rows']['positive']['source_intact'])
        self.assertIn('source target hash differs: verified/lib.rs', result['rows']['positive']['errors'])

    def test_exception_partially_written_and_rethrown(self):
        with tempfile.TemporaryDirectory() as tmp:
            args, env, pins, record, evidence = fixture(tmp)
            with self.assertRaisesRegex(ValueError, 'synthetic stage exception'):
                proof.run(args, engine=Engine(record), pins_loader=lambda _repo: pins,
                          proof_runner=lambda **kw: (_ for _ in ()).throw(ValueError('synthetic stage exception')),
                          runtime_loader=lambda _args: {}, env=env)
            saved = __import__('json').loads((evidence/proof.SUMMARY_REL).read_text())
            self.assertEqual(saved['rows']['positive']['proof_stage']['status'], 'EXCEPTION')
            self.assertEqual(saved['exception']['type'], 'ValueError')

    def test_production_stage_callback_uses_intrinsic_link_interface(self):
        calls=[]
        def stage(case,name,argv,args,**kw):
            calls.append((case,name,argv,args,kw));return {'exit':0}
        cap=SimpleNamespace(LINK=SimpleNamespace(stage=stage))
        args=SimpleNamespace(tool_home=Path('/synthetic/tool'),schema=Path('/synthetic/schema'),
                             compiler_sysroot='/synthetic/sysroot',deadline_epoch=10)
        callback=proof._proof_callback({'capture':cap},args)
        result=callback(case=Path('/synthetic/case'),variant='positive',
                        name='r24-mut-proof-positive',build_id='synthetic')
        self.assertEqual(result['exit'],0)
        self.assertEqual(calls[0][-1],dict(gates=False,pointer_drop=False,cap_seconds=1200))
        self.assertEqual(calls[0][2][-1],'verified/lib.rs')

    def test_substring_marker_and_hidden_error_refused(self):
        marker=proof.MARKER_PREFIX+'positive'+proof.MARKER_SUFFIX
        result,_,_=self.run_fixture(proof_cb=lambda **kw: stage_result(log_text='prefix '+marker+' suffix'))
        self.assertIn('positive native certificate marker missing/duplicated/wrong-case',result['rows']['positive']['errors'])
        result,_,_=self.run_fixture(proof_cb=lambda **kw: stage_result(log_text=marker+'\nverified/lib.rs(1,1): error: synthetic'))
        self.assertIn('positive proof log contains diagnostic error',result['rows']['positive']['errors'])


if __name__ == '__main__':
    unittest.main()
