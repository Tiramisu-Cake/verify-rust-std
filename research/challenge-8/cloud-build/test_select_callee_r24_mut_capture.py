"""Isolated synthetic tests for the R24 mutable source/MIR capture adapter."""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    'select_callee_r24_mut_capture_test_target',
    HERE / 'select-callee-r24-mut-capture.py')
assert SPEC and SPEC.loader
TARGET = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(TARGET)


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


class FakeProvider:
    def __init__(self, record=None):
        self.record = record or {'provider': 'cloud-build', 'build_id': BUILD_ID,
            'project': 'smallsort-ci', 'region': 'global', 'os': 'ubuntu-22.04',
            'arch': 'x86_64'}
        self.calls = 0

    def require_supported_provider(self):
        self.calls += 1
        return self.record


BUILD_ID = 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'
GHOST = b'/*@ synthetic ghost @*/\n'
SOURCE_ORDER = list(TARGET.EXPECTED_ORDER)
ORIGINAL = (TARGET.MUT_PREFIX + TARGET.MUT_SIGNATURE + b'{\n'
            b'struct DropOnPanic<T> {\nimpl<T> Drop for DropOnPanic<T> {\n'
            b'unsafe { self.inner.drop_in_place() }\n'
            b'let guard = DropOnPanic { inner: guard };\n'
            b'drop.drop_in_place();\ncrate::mem::forget(guard);\n'
            b'crate::intrinsics::select_unpredictable(condition, true_val, false_val).assume_init()\n}\n')
VERIFIED = ORIGINAL.replace(b'{\n', b'{\n' + GHOST * 3, 1)


class FakeOwner:
    @staticmethod
    def strip_ghost(data):
        return data.replace(GHOST, b'')


class FakeSourceWriters:
    def __init__(self, mode='ok'):
        self.mode = mode
        self.owner = FakeOwner()

    def write_case_owner(self, repo, out):
        out.mkdir(parents=True)
        base = out / 'mutable-actual-baseline'
        (base / 'original').mkdir(parents=True)
        (base / 'verified').mkdir()
        (base / 'original/lib.rs').write_bytes(ORIGINAL)
        (base / 'verified/lib.rs').write_bytes(VERIFIED)
        base_record = {
            'fixture_signature': TARGET.MUT_SIGNATURE.decode(),
            'contract_text_sha256': TARGET.CONTRACT_SHA256, 'capture_only': True,
            'typed_mir_binding_established': False, 'helper_proof_status': 'NOT_RUN',
            'translator_admission': 'NOT_IMPLEMENTED',
            'publication_status': 'NOT_PUBLISHED', 'proof_credit': 0,
            'ghost_strip_identity': True, 'original_sha256': digest(ORIGINAL),
            'verified_sha256': digest(VERIFIED),
            'source_certificate': {
                **TARGET.BASELINE_SOURCE_PINS,
                'target_specialization': 'T = *mut Element; Element unrestricted',
                'runtime_body_exact': True, 'guard_and_drop_body_retained': True,
                'actual_forget_redirect': False, 'actual_assume_init_redirect': False,
                'fixture_writer_is_const_independent': True, 'helper_proof_status': 'NOT_RUN',
                'exact_body_sha256': digest(ORIGINAL[len(TARGET.MUT_PREFIX + TARGET.MUT_SIGNATURE):-1]),
                'provider': FakeProvider().record,
            },
        }
        if self.mode == 'bad-baseline-hash':
            base_record['original_sha256'] = '0' * 64
        if self.mode == 'bad-source-cert':
            base_record['source_certificate'].pop('hint_sha256')
        if self.mode == 'bad-source-sentinel':
            original = ORIGINAL.replace(b'crate::mem::forget(guard);', b'')
            verified = VERIFIED.replace(b'crate::mem::forget(guard);', b'')
            (base / 'original/lib.rs').write_bytes(original)
            (base / 'verified/lib.rs').write_bytes(verified)
            base_record['original_sha256'] = digest(original)
            base_record['verified_sha256'] = digest(verified)
        (base / 'fixture.json').write_text(json.dumps(base_record))
        final = out / 'owner-linked-mut'
        (final / 'original').mkdir(parents=True)
        (final / 'verified').mkdir()
        (final / 'original/lib.rs').write_bytes(ORIGINAL)
        (final / 'verified/lib.rs').write_bytes(VERIFIED)
        (final / 'fixture.json').write_text(json.dumps({
            'classification': 'SOURCE_ONLY_MUTABLE_OWNER_LINKED_CANDIDATE',
            'typed_mir_binding_established': False, 'helper_proof_status': 'NOT_RUN',
            'publication_status': 'NOT_PUBLISHED', 'proof_credit': 0,
            'original_sha256': digest(ORIGINAL), 'verified_sha256': digest(VERIFIED),
        }))
        return {'source_only': True}

    def write_nested(self, owner_dir, out, repo):
        out.mkdir(parents=True)
        seven = out / 'seven-body-owned-forget-mut'
        (seven / 'original').mkdir(parents=True)
        (seven / 'verified').mkdir()
        (seven / 'original/lib.rs').write_bytes(ORIGINAL)
        (seven / 'verified/lib.rs').write_bytes(VERIFIED)
        (seven / 'fixture.json').write_text(json.dumps({
            'classification': 'SOURCE_ONLY_MUTABLE_OWNED_FORGET_SEVEN_BODY',
            'typed_mir_binding_established': False, 'helper_proof_status': 'NOT_RUN'}))
        return {'source_only': True}

    def write_nine(self, seven, out, repo):
        out.mkdir(parents=True)
        case = out / 'nine-body-mut'
        (case / 'original').mkdir(parents=True)
        (case / 'verified').mkdir()
        original = ORIGINAL
        verified = VERIFIED
        record_original = '0' * 64 if self.mode == 'source-drift' else digest(original)
        (case / 'original/lib.rs').write_bytes(original)
        (case / 'verified/lib.rs').write_bytes(verified)
        (case / 'fixture.json').write_text(json.dumps({
            'classification': 'SOURCE_ONLY_MUTABLE_NINE_BODY_A1_FRACTIONAL_CAPTURE',
            'specialization': 'T = *mut Element; Element unrestricted',
            'source_order': SOURCE_ORDER,
            'original_sha256': record_original,
            'verified_sha256': digest(verified),
            'ghost_strip_identity': True,
            'typed_mir_binding_established': False,
            'translator_admission': 'NOT_IMPLEMENTED', 'helper_proof_status': 'NOT_RUN',
            'publication_status': 'NOT_PUBLISHED', 'proof_credit': 0,
        }))
        return {'source_only': True}

    def mapping(self):
        return {'owner_writer': type('OwnerWriter', (), {
                    'build_linked_pair': self.write_case_owner})(),
                'nested_drop_writer': type('NestedWriter', (), {
                    'write_case': self.write_nested})(),
                'nine_body_writer': type('NineWriter', (), {
                    'write_case': self.write_nine})(),
                'owner': self.owner}


def production_error_matcher():
    # Parse the production regex literal without importing actual source drivers.
    tree = ast.parse((HERE.parent / 'overnight-helper/check-helper.py').read_text())
    assignment = next(node for node in tree.body if isinstance(node, ast.Assign)
                      and any(isinstance(target, ast.Name) and target.id == 'ERR'
                              for target in node.targets))
    call = assignment.value
    assert isinstance(call, ast.Call) and len(call.args) == 1 and not call.keywords
    return re.compile(ast.literal_eval(call.args[0]))


class FakeCapture:
    def __init__(self, mode='ok'):
        self.mode = mode
        self.GUARD = self
        self.proof_calls = 0
        self.LINK = type('LinkModule', (), {'LINK': type('NestedLink', (), {
            'ERR': production_error_matcher()})()})()

    def clear_semantic_opt_ins(self):
        for key in TARGET.BLOCKED_OPT_INS:
            __import__('os').environ.pop(key, None)
        for key in list(__import__('os').environ):
            if key.startswith('SORT4_R21_FRACTIONAL_'):
                __import__('os').environ.pop(key, None)

    def capture_case(self, case, source, args):
        if self.mode == 'exception':
            raise LookupError('original capture exception')
        stages = {}
        for name in ('normal-export', 'normal-decode', 'readonly-export',
                     'readonly-decode', 'refinement'):
            exit_code = 1 if name == self.mode else 0
            stages[name] = {'status': 'RAN', 'exit': exit_code}
        if self.mode == 'missing-stage':
            stages.pop('readonly-decode')
        if self.mode == 'missing-refinement':
            stages['refinement']['exit'] = 1
        (case / 'normal-mir.bin').write_bytes(b'normal export')
        (case / 'readonly-mir.bin').write_bytes(b'readonly export')
        (case / 'normal-mir.txt').write_text('normal decoded MIR')
        (case / 'readonly-mir.txt').write_text('readonly decoded MIR')
        return {'stages': stages, 'frontend_refinement': self.mode != 'missing-refinement',
                'source_unchanged': True}

    def full_body_capture(self, case, source, stages):
        if self.mode == 'bad-order':
            order = list(reversed(SOURCE_ORDER))
        else:
            order = SOURCE_ORDER
        result = {}
        for mode in ('normal', 'readonly'):
            rows = []
            for index, name in enumerate(order):
                raw = f'{mode} body {index}: {name}'.encode()
                filename = f'{mode}-body-{index}-full-mir.txt'
                (case / filename).write_bytes(raw)
                rows.append({'index': index, 'defpath': name, 'file': filename,
                             'bytes': len(raw), 'sha256': digest(raw)})
            decoded = (case / f'{mode}-mir.txt').read_bytes()
            result[mode] = {'classification': 'COMPLETE_NINE_BODY_CAPTURE_ONLY',
                'whole_decoded_mir_file': f'{mode}-mir.txt',
                'whole_decoded_mir_sha256': digest(decoded),
                'exact_body_count_and_order': True, 'bodies': rows}
        if self.mode == 'missing-order':
            result['normal']['bodies'][0]['defpath'] = 'wrong body'
        return result

    def refusal_fingerprint(self, case, source, args):
        env = __import__('os').environ
        env['SORT4_NESTED_FINGERPRINT_MODE'] = '9'
        for name in TARGET.SNAPSHOT_NAMES:
            if name == 'body-8' and self.mode == 'missing-snapshot':
                continue
            data = ('marshal:' + name).encode()
            (case / f'actual-nested-9-{name}.marshal').write_bytes(data)
        marker = TARGET.NATIVE_REFUSAL_LINE
        if self.mode == 'wrong-marker':
            marker = 'wrong refusal marker'
        if self.mode == 'duplicate-marker':
            marker += '\n' + TARGET.NATIVE_REFUSAL_LINE
        if self.mode == 'bare-marker':
            marker = TARGET.REFUSAL_MARKER
        if self.mode == 'alternate-exception':
            marker = TARGET.NATIVE_REFUSAL_LINE.replace('Failure(', 'Invalid_argument(')
        if self.mode == 'suffix-marker':
            marker += ' appended text'
        if self.mode == 'embedded-marker':
            marker = 'debug: ' + marker
        if self.mode == 'mixed-markers':
            marker += '\n' + TARGET.REFUSAL_MARKER
        log_text = marker + '\n'
        if self.mode == 'fatal-with-refusal':
            log_text += 'Fatal error: exception Failure("synthetic fatal")\n'
        if self.mode == 'error-with-refusal':
            log_text += 'verified/lib.rs(1,1-2): error: synthetic verifier error\n'
        (case / TARGET.CAPTURE_LOG).write_text(log_text)
        snapshots = {}
        for name in TARGET.SNAPSHOT_NAMES:
            path = case / f'actual-nested-9-{name}.marshal'
            if path.is_file():
                data = path.read_bytes()
                snapshots[name] = {'file': path.name, 'bytes': len(data), 'sha256': digest(data)}
        stage = {'status': 'RAN', 'exit': 1 if self.mode == 'wrong-probe' else 2}
        if self.mode == 'fingerprint-source-false':
            stage['source_unchanged'] = False
        elif self.mode == 'fingerprint-source-null':
            stage['source_unchanged'] = None
        elif self.mode != 'fingerprint-source-absent':
            stage['source_unchanged'] = True
        if self.mode == 'post-source-drift':
            (case / 'verified/lib.rs').write_bytes(b'drift after mode-9 capture')
        return {'classification': ('BAD' if self.mode == 'wrong-probe' else
                                   'INTENDED_DIAGNOSTIC_REFUSAL_NO_PROOF_RULE'),
            'expected_refusal_seen': self.mode != 'wrong-marker',
            'all_ten_snapshots': len(snapshots) == 10,
            'body_proof_run': False,
            'stage': stage, 'snapshots': snapshots}


class CaptureAdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.repo = self.root / 'repo'
        self.repo.mkdir()
        self.cloud = self.root / 'cloud'
        self.cloud.mkdir()
        self.evidence = self.root / 'allprooflogs'
        self.evidence.mkdir()
        self.mode_path = self.repo / TARGET.MODE_REL
        self.mode_path.parent.mkdir(parents=True)
        source_mode = Path(__file__).parents[1] / 'task-history/select-callee-r24/P2-MUT-CAPTURE-MODE.json'
        self.mode_path.write_bytes(source_mode.read_bytes())
        self.env = {'SMALLSORT_EXECUTION_PROVIDER': 'cloud-build',
            TARGET.R24_PHASE_ENV: TARGET.R24_PHASE,
            TARGET.R21_PHASE_ENV: TARGET.R21_PHASE, 'LANE': TARGET.LANE,
            'CLOUD_BUILD_ID': BUILD_ID, 'CLOUD_BUILD_PROJECT_ID': 'smallsort-ci',
            'CLOUD_BUILD_REGION': 'global'}
        self.fake_capture = FakeCapture()
        self.fake_provider = FakeProvider()
        self.fake_source = FakeSourceWriters()
        self.provider_calls = 0
        self.capture_calls = 0
        self.source_calls = 0

    def tearDown(self):
        self.temp.cleanup()

    def args(self):
        return type('Args', (), {'repo': self.repo, 'cloud_dir': self.cloud,
            'evidence': self.evidence, 'tool_home': Path('/synthetic/tool'),
            'schema': Path('/synthetic/schema'),
            'compiler_sysroot': Path('/synthetic/sysroot'), 'deadline_epoch': 999999,
            'mode_file': self.mode_path, 'mode_sha256': TARGET.MODE_SHA256})()

    def provider_loader(self, _cloud):
        self.provider_calls += 1
        return self.fake_provider

    def capture_loader(self, *_args):
        self.capture_calls += 1
        return {'capture': self.fake_capture}

    def source_loader(self, *_args):
        self.source_calls += 1
        return self.fake_source.mapping()

    @staticmethod
    def source_view_builder(_repo, _cloud_dir, capture_root):
        view = capture_root / 'source-repository'
        view.mkdir()
        return view, [{'path': 'source-repository/synthetic.py', 'bytes': 1,
                       'sha256': digest(b'x')}]

    def run_adapter(self, *, mode='ok'):
        self.fake_capture = FakeCapture(mode)
        self.fake_source = FakeSourceWriters(mode)
        with patch.dict('os.environ', self.env, clear=True):
            return TARGET.run(self.args(), provider_loader=self.provider_loader,
                capture_loader=self.capture_loader, source_loader=self.source_loader,
                source_view_builder=self.source_view_builder)

    def test_nested_writer_resolves_existing_owner_module_interface(self):
        path = HERE.parent / 'overnight-guard-actual/prepare-actual-nested-drop-mut.py'
        tree = ast.parse(path.read_text())
        helper = next(node for node in tree.body if isinstance(node, ast.FunctionDef)
                      and node.name == 'owner_projection')
        def require(ok, message):
            if not ok:
                raise ValueError(message)
        namespace = {'require': require}
        exec(compile(ast.Module(body=[helper], type_ignores=[]), str(path), 'exec'), namespace)
        owner = FakeOwner()
        linked = type('PinnedOwnerLinked', (), {'load_modules': lambda self: (owner,)})()
        self.assertFalse(hasattr(linked, 'OWNER'))
        self.assertIs(namespace['owner_projection'](linked), owner)
        bad = type('BadOwnerLinked', (), {'load_modules': lambda self: (object(),)})()
        with self.assertRaisesRegex(ValueError, 'ghost-strip service'):
            namespace['owner_projection'](bad)
        # No whole source builder/preparation is invoked by this isolated test.

    def test_wrong_route_mode_hash_or_provider_refuses_before_source_services(self):
        wrong_envs = [dict(self.env, **{TARGET.R24_PHASE_ENV: 'wrong'}),
                      dict(self.env, SMALLSORT_EXECUTION_PROVIDER='github')]
        for env in wrong_envs:
            with self.subTest(env=env), patch.dict('os.environ', env, clear=True):
                with self.assertRaises(RuntimeError):
                    TARGET.run(self.args(), provider_loader=self.provider_loader,
                        capture_loader=self.capture_loader, source_loader=self.source_loader,
                        source_view_builder=self.source_view_builder)
        self.assertEqual(self.provider_calls, 0)
        self.assertEqual(self.capture_calls, 0)
        self.assertEqual(self.source_calls, 0)

        self.mode_path.write_bytes(self.mode_path.read_bytes() + b' ')
        with patch.dict('os.environ', self.env, clear=True):
            with self.assertRaisesRegex(RuntimeError, 'mode hash'):
                TARGET.run(self.args(), provider_loader=self.provider_loader,
                    capture_loader=self.capture_loader, source_loader=self.source_loader,
                    source_view_builder=self.source_view_builder)
        self.assertEqual(self.provider_calls, 0)
        self.assertEqual(self.source_calls, 0)

    def test_provider_record_mismatch_stops_before_capture_or_preparation(self):
        self.fake_provider = FakeProvider(dict(FakeProvider().record,
                                                build_id='bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb'))
        with patch.dict('os.environ', self.env, clear=True):
            with self.assertRaisesRegex(RuntimeError, 'native Cloud provider'):
                TARGET.run(self.args(), provider_loader=self.provider_loader,
                    capture_loader=self.capture_loader, source_loader=self.source_loader,
                    source_view_builder=self.source_view_builder)
        self.assertEqual(self.capture_calls, 0)
        self.assertEqual(self.source_calls, 0)

        self.fake_provider = FakeProvider(dict(FakeProvider().record, build_id='not-a-uuid'))
        with patch.dict('os.environ', dict(self.env, CLOUD_BUILD_ID='not-a-uuid'), clear=True):
            with self.assertRaisesRegex(RuntimeError, 'canonical UUID'):
                TARGET.run(self.args(), provider_loader=self.provider_loader,
                    capture_loader=self.capture_loader, source_loader=self.source_loader,
                    source_view_builder=self.source_view_builder)
        self.assertEqual(self.capture_calls, 0)
        self.assertEqual(self.source_calls, 0)

    def test_source_view_uses_exact_committed_recipe_blobs_and_pinned_infra_provider(self):
        proof = self.root / 'proof-repo'
        infra = self.root / 'infra-repo'
        proof.mkdir()
        infra.mkdir()
        rels = [rel for rel, _ in TARGET.MUTABLE_SOURCE_FILES.values()]
        for rel in rels:
            path = proof / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(('committed:' + rel).encode())
        subprocess.run(['git', '-C', str(proof), 'init', '-q'], check=True)
        subprocess.run(['git', '-C', str(proof), 'config', 'user.email', 'test@example.invalid'],
                       check=True)
        subprocess.run(['git', '-C', str(proof), 'config', 'user.name', 'Synthetic Test'],
                       check=True)
        subprocess.run(['git', '-C', str(proof), 'add', '.'], check=True)
        subprocess.run(['git', '-C', str(proof), 'commit', '-qm', 'proof blobs'], check=True)
        recipe_rel = infra / 'research/challenge-8/cloud-build/recipes/o26-select-callee-r20.json'
        recipe_rel.parent.mkdir(parents=True)
        recipe_rel.write_text(json.dumps({'proof_paths': rels}))
        cloud = infra / 'research/challenge-8/cloud-build'
        cloud.mkdir(parents=True, exist_ok=True)
        provider = Path(__file__).with_name('provider.py').read_bytes()
        (cloud / 'provider.py').write_bytes(provider)
        subprocess.run(['git', '-C', str(infra), 'init', '-q'], check=True)
        subprocess.run(['git', '-C', str(infra), 'config', 'user.email', 'test@example.invalid'],
                       check=True)
        subprocess.run(['git', '-C', str(infra), 'config', 'user.name', 'Synthetic Test'],
                       check=True)
        subprocess.run(['git', '-C', str(infra), 'add', '.'], check=True)
        subprocess.run(['git', '-C', str(infra), 'commit', '-qm', 'infra recipe/provider'],
                       check=True)
        capture_root = self.root / 'capture'
        capture_root.mkdir()
        view, rows = TARGET._prepare_source_view(proof, cloud, capture_root)
        self.assertEqual(len(rows), len(rels) + 1)
        for rel in rels:
            self.assertEqual((view / rel).read_bytes(),
                             subprocess.check_output(['git', '-C', str(proof), 'show', 'HEAD:' + rel]))
        self.assertEqual((view / 'research/challenge-8/cloud-build/provider.py').read_bytes(),
                         provider)

    def test_inventory_failure_downgrades_success_to_incomplete(self):
        with patch.object(TARGET, '_artifact_inventory', side_effect=OSError('inventory failure')):
            result = self.run_adapter()
        self.assertFalse(result['complete'])
        self.assertEqual(result['classification'], 'INCOMPLETE_MUTABLE_SOURCE_MIR_CAPTURE')
        self.assertIn('artifact inventory failed', result['incomplete_reasons'][0])

    def test_success_inventories_source_mir_and_refusal_without_proof_credit(self):
        result = self.run_adapter()
        self.assertTrue(result['complete'])
        self.assertEqual(result['classification'], 'MUTABLE_SOURCE_MIR_CAPTURE_ONLY')
        self.assertEqual(result['provider_record']['build_id'], BUILD_ID)
        self.assertTrue(result['source_records']['original_sha256'])
        self.assertTrue(result['source_records']['verified_sha256'])
        self.assertEqual(result['source_records']['specialization'],
                         'T = *mut Element; Element unrestricted')
        request = result['source_records']['static_fingerprint_request']
        self.assertEqual(request['schema'], 'select-r24-mut-capture-request-v1')
        self.assertEqual(request['source_generation'], 'CONST_INDEPENDENT_MUTABLE_PARALLEL')
        self.assertEqual(request['legacy_request_status'],
                         'NOT_USED_UNSUPPORTED_CONST_PAIR_INPUT')
        self.assertNotIn('const_pair_identity_modulo_signature', request['fixture'])
        self.assertEqual(len(result['artifact_inventory']),
                         len(result['artifact_inventory']))
        inventory_paths = {row['path'] for row in result['artifact_inventory']}
        self.assertIn('cases/r24-mut-capture/source-preparation/R24-MUT-CAPTURE-REQUEST.json',
                      inventory_paths)
        self.assertIn('cases/r24-mut-capture/source-preparation/nine-body/nine-body-mut/normal-mir.txt',
                      inventory_paths)
        self.assertIn('cases/r24-mut-capture/source-preparation/nine-body/nine-body-mut/actual-nested-9-unit.marshal',
                      inventory_paths)
        self.assertIs(result['body_proof_run'], False)
        self.assertIs(result['typed_admission'], False)
        self.assertIs(result['semantic_rule_enabled'], False)
        self.assertIs(result['accepted'], False)
        self.assertEqual(result['proof_credit'], 0)
        self.assertIs(result['publication_allowed'], False)
        self.assertEqual(self.fake_capture.proof_calls, 0)
        self.assertNotIn('SORT4_NESTED_FINGERPRINT_MODE', __import__('os').environ)
        saved = self.evidence / TARGET.SUMMARY_REL
        self.assertEqual(json.loads(saved.read_text()), result)

    def test_capture_prerequisite_failures_remain_incomplete(self):
        for mode in ('normal-export', 'missing-stage', 'missing-refinement',
                     'bad-order', 'missing-order'):
            self.evidence = self.root / ('ev-' + mode)
            self.evidence.mkdir()
            with self.subTest(mode=mode):
                result = self.run_adapter(mode=mode)
                self.assertFalse(result['complete'])
                self.assertFalse(result['fingerprint'])
                self.assertTrue(result['incomplete_reasons'])

    def test_fingerprint_refusal_and_snapshot_failures_remain_incomplete(self):
        for mode in ('missing-snapshot', 'wrong-marker', 'duplicate-marker', 'wrong-probe',
                     'fingerprint-source-false', 'fingerprint-source-null',
                     'fingerprint-source-absent', 'fatal-with-refusal',
                     'error-with-refusal', 'post-source-drift', 'bare-marker',
                     'alternate-exception', 'suffix-marker', 'embedded-marker', 'mixed-markers'):
            self.evidence = self.root / ('ev-' + mode)
            self.evidence.mkdir()
            with self.subTest(mode=mode):
                result = self.run_adapter(mode=mode)
                self.assertFalse(result['complete'])
                self.assertTrue(result['incomplete_reasons'])

    def test_source_drift_writes_incomplete_partial_summary_then_preserves_exception(self):
        with self.assertRaisesRegex(RuntimeError, 'final mutable source pair hash'):
            self.run_adapter(mode='source-drift')
        saved = self.evidence / TARGET.SUMMARY_REL
        partial = json.loads(saved.read_text())
        self.assertFalse(partial['complete'])
        self.assertEqual(partial['exception']['type'], 'RuntimeError')
        self.assertFalse(partial['body_proof_run'])

    def test_mutable_baseline_requires_physical_hashes_source_certificate_and_sentinels(self):
        for mode in ('bad-baseline-hash', 'bad-source-cert', 'bad-source-sentinel'):
            self.evidence = self.root / ('ev-' + mode)
            self.evidence.mkdir()
            with self.subTest(mode=mode), self.assertRaisesRegex(RuntimeError, 'baseline'):
                self.run_adapter(mode=mode)
            partial = json.loads((self.evidence / TARGET.SUMMARY_REL).read_text())
            self.assertFalse(partial['complete'])
            self.assertFalse(partial['body_proof_run'])

    def test_original_capture_exception_is_saved_and_rethrown(self):
        with self.assertRaisesRegex(LookupError, 'original capture exception'):
            self.run_adapter(mode='exception')
        partial = json.loads((self.evidence / TARGET.SUMMARY_REL).read_text())
        self.assertEqual(partial['exception']['type'], 'LookupError')
        self.assertEqual(partial['exception']['message'], 'original capture exception')
        self.assertFalse(partial['complete'])

    def test_ambient_proof_opt_in_refuses_before_provider_or_capture(self):
        env = dict(self.env, SORT4_R24_CHECKED_POINTER_OUTCOMES='1')
        with patch.dict('os.environ', env, clear=True):
            with self.assertRaisesRegex(RuntimeError, 'ambient proof opt-ins'):
                TARGET.run(self.args(), provider_loader=self.provider_loader,
                    capture_loader=self.capture_loader, source_loader=self.source_loader,
                    source_view_builder=self.source_view_builder)
        self.assertEqual(self.provider_calls, 0)
        self.assertEqual(self.capture_calls, 0)
        self.assertEqual(self.source_calls, 0)

    def test_provider_overlay_requires_exact_known_guard_rewrite_of_committed_capture(self):
        repo = self.root / 'overlay-repo'
        evidence = self.root / 'overlay-evidence'
        cloud = self.root / 'overlay-cloud'
        source = repo / 'research/challenge-8/synthetic-capture.py'
        source.parent.mkdir(parents=True)
        evidence.mkdir()
        cloud.mkdir()
        provider_bytes = b'# synthetic pinned provider\n'
        (cloud / 'provider.py').write_bytes(provider_bytes)
        guard = ('os.environ.get("GITHUB_ACTIONS") == "true" and\n'
                 '            os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted" and\n'
                 '            os.environ.get("RUNNER_OS") == "Linux"')
        committed = ('from pathlib import Path\nimport importlib.util\n'
                     'allowed = (' + guard + ')\n').encode()
        source.write_bytes(committed)
        subprocess.run(['git', '-C', str(repo), 'init', '-q'], check=True)
        subprocess.run(['git', '-C', str(repo), 'config', 'user.email', 'test@example.invalid'],
                       check=True)
        subprocess.run(['git', '-C', str(repo), 'config', 'user.name', 'Synthetic Test'],
                       check=True)
        subprocess.run(['git', '-C', str(repo), 'add', str(source.relative_to(repo))], check=True)
        subprocess.run(['git', '-C', str(repo), 'commit', '-qm', 'synthetic committed guard'],
                       check=True)
        rel = Path('research/challenge-8/synthetic-capture.py')
        helper = '\n\ndef _o26_cloud_provider_ok():\n    return True\n'
        expected_overlay = committed.decode().replace(guard, '_o26_cloud_provider_ok()', 1)
        expected_overlay = expected_overlay.replace('from pathlib import Path\n',
            'from pathlib import Path\n' + helper, 1).encode()
        source.write_bytes(expected_overlay)
        proof_sha = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'],
                                            text=True).strip()
        import difflib
        diff = ''.join(difflib.unified_diff(committed.decode().splitlines(True),
            expected_overlay.decode().splitlines(True),
            fromfile=rel.as_posix() + '.committed', tofile=rel.as_posix() + '.cloud-guard'))
        receipt = {'proof_sha': proof_sha, 'provider_sha256': digest(provider_bytes),
            'files': [{'path': rel.as_posix(), 'original_sha256': digest(committed),
                'cloud_overlay_sha256': digest(expected_overlay), 'guard_only': True,
                'diff': diff}]}
        (evidence / 'candidate-provider-overlay.json').write_text(json.dumps(receipt))
        o26 = type('O26', (), {'PROVIDER_SHA': digest(provider_bytes),
            'OVERLAYS': [rel], 'GUARD_VARIANTS': (guard,), 'HELPER': helper,
            'git_sha': staticmethod(lambda _repo: proof_sha)})()

        def derive(raw, _rel, _o26):
            text = raw.decode()
            text = text.replace(guard, '_o26_cloud_provider_ok()', 1)
            text = text.replace('from pathlib import Path\n',
                'from pathlib import Path\n' + helper, 1)
            return text.encode()
        fractional = type('Fractional', (), {'_derive_o26_guard_overlay': staticmethod(derive)})()
        result = TARGET._validate_overlay_receipt(repo, cloud, evidence, fractional, o26)
        self.assertEqual(result['files'][0]['original_sha256'], digest(committed))
        self.assertEqual(result['files'][0]['cloud_overlay_sha256'], digest(expected_overlay))
        self.assertNotEqual(result['files'][0]['original_sha256'],
                            result['files'][0]['cloud_overlay_sha256'])
        source.write_bytes(committed)
        with self.assertRaisesRegex(RuntimeError, 'exact committed O26 guard-only overlay'):
            TARGET._validate_overlay_receipt(repo, cloud, evidence, fractional, o26)


if __name__ == '__main__':
    unittest.main()
