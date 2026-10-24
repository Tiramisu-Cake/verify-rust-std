#!/usr/bin/env python3
"""Synthetic service tests for the W4 source/control capture adapter.

No constructor is run and no compiler/exporter/verifier process is invoked.
"""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch


MODULE_PATH = Path(__file__).with_name('select-callee-r24-w4-control-capture.py')
SPEC = importlib.util.spec_from_file_location('w4_control_capture_under_test', MODULE_PATH)
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
SPEC.loader.exec_module(MOD)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def scrub_ghost(raw: bytes) -> bytes:
    out = []
    in_block = False
    for line in raw.splitlines(keepends=True):
        if b'/*@' in line:
            in_block = True
        if not in_block and not line.lstrip().startswith(b'//@'):
            out.append(line)
        if b'@*/' in line:
            in_block = False
    return b''.join(out)


def make_count5_source():
    source = bytearray(b'pub unsafe fn sort4_stable() {\n')
    for index in range(1, 6):
        source.extend(f'let c{index} = is_less(a, b);\n'.encode())
    for index in range(1, 8):
        source.extend(f'let s{index} = hint::select_unpredictable(a, b, c);\n'.encode())
    selector = b'        let lo = hint::select_unpredictable(c5, unknown_right, unknown_left);\n'
    source.extend(b"        //@ let cmp5_k: lifetime 'cmp5;\n")
    source.extend(b'        //@ __vf_callback_scope5();\n')
    source.extend(b'        //@ let left5_ref = precreate_ref::<T>(c);\n')
    source.extend(b'        //@ NORMAL5 recovery\n')
    source.extend(selector)
    for _ in range(4):
        source.extend(b'ptr::copy_nonoverlapping(a, b, n);\n')
    source.extend(b'}\n')
    return bytes(source), selector


class ControlCaptureTests(unittest.TestCase):
    def test_pinned_indexed_module_exposes_every_attribute_the_adapter_reads(self):
        repo = MODULE_PATH.resolve().parents[3]
        relative, expected = MOD.HELPER_PINS['c2_c5']
        indexed = MOD._load(repo / relative, 'r24_static_indexed_api', expected)
        tree = ast.parse(MODULE_PATH.read_text())
        attributes = {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)
                      and isinstance(node.value, ast.Name) and node.value.id == 'indexed'}
        self.assertTrue(attributes)
        self.assertEqual(sorted(name for name in attributes if not hasattr(indexed, name)), [])
        self.assertFalse(hasattr(indexed, 'C4_EXPECTED'))

    def test_c4_reason_labels_match_the_pinned_inline_api_tuple(self):
        repo = MODULE_PATH.resolve().parents[3]
        relative, expected = MOD.HELPER_PINS['c2_c5']
        path = repo / relative
        self.assertEqual(sha(path.read_bytes()), expected)
        tree = ast.parse(path.read_text())
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef)
                        and node.name == 'resource_controls_c4')
        call = next(node.value for node in ast.walk(function) if isinstance(node, ast.Return))
        self.assertIsInstance(call, ast.Call)
        self.assertEqual(MOD.C4_EXPECTED_REASON_LABELS, ast.literal_eval(call.args[-1]))
        self.assertEqual(len(MOD.C4_EXPECTED_REASON_LABELS), 8)

    def test_indexed_adapters_exercise_real_pinned_constants_on_tiny_fake_source(self):
        repo = MODULE_PATH.resolve().parents[3]
        relative, expected = MOD.HELPER_PINS['c2_c5']
        real = MOD._load(repo / relative, 'r24_tiny_indexed_constants', expected)
        strip_rel, strip_sha = MOD.HELPER_PINS['ghost_strip']
        ghost = MOD._load(repo / strip_rel, 'r24_tiny_ghost_parser', strip_sha)
        # These are dummy runtime calls, not an extracted/constructed std body.
        # Only the pinned API's marker/share byte forms are real constants.
        indexed = types.SimpleNamespace(**{
            name: getattr(real, name) for name in dir(real) if not name.startswith('__')})
        indexed.ghost_declaration = lambda *a: b'/*@\npred synthetic_missing_token;\n@*/\n'
        indexed._insert_before_target = lambda source, declaration: declaration + source
        for k, slots, token in ((3, (1, 3), 0), (4, (0, 2), 3)):
            with self.subTest(k=k):
                typed = getattr(real, f'C{k}_TYPED_CALL')
                marker = getattr(real, f'MARKER{k}')
                normal = getattr(real, f'NORMAL{k}')
                pre = getattr(real, f'C{k}_LEFT_PRECREATE') + getattr(real, f'C{k}_RIGHT_PRECREATE')
                share = lambda slot: (b'        //@ share_full_borrow::<T>(cmp%d_k, t, ' % k +
                                      real._slot(slot) + b');\n')
                borrow = (b'        //@ borrow(cmp%d_k, <T>.full_borrow_content(t, ' % k +
                          real._slot(token) + b'));\n')
                source = (b'pub unsafe fn sort4_stable<Synthetic>() {\n' +
                    b'let synthetic = is_less(a, b);\n' * 4 +
                    b'hint::select_unpredictable(a, b, c);\n' * 7 +
                    b'ptr::copy_nonoverlapping(a, b, n);\n' * 4 +
                    borrow + b''.join(share(slot) for slot in (*slots, token)) +
                    pre + marker + typed + normal + real.LO_SELECT + b'}\n')
                original = ghost.strip_ghost(source)
                rows = MOD._indexed_controls_at_count5(
                    k, source, original, ghost, b'synthetic recovery input',
                    {'actual_indexed_calls': 5}, indexed, lambda *a: [])
                self.assertEqual(len(rows), 8)
                self.assertTrue(all(row[3]['actual_indexed_calls'] == 5 for row in rows))
                self.assertTrue(all(ghost.strip_ghost(row[1]) == original for row in rows))
                self.assertIn(b'__vf_callback_unwind_four(6);', rows[-1][1])

    def test_closed_remaining_batch_covers_29_uncaptured_variants(self):
        self.assertEqual(len(MOD.BODY_NAMES), 37)
        self.assertEqual(MOD.BATCH_INDICES, tuple(range(8, 37)))
        self.assertEqual(set(range(8)) | set(MOD.BATCH_INDICES), set(range(37)))
        self.assertFalse(set(range(8)) & set(MOD.BATCH_INDICES))
        self.assertEqual(MOD.BODY_NAMES[0], 'positive')
        self.assertTrue(MOD.BODY_NAMES[1].startswith('c1-'))
        self.assertEqual(MOD.BODY_NAMES[3], 'c2-missing-unselected-share-negative')
        self.assertIn('c5-cross-scope-read-negative', MOD.BODY_NAMES)
        self.assertEqual(MOD.expected_mode()['universe_count'], 37)
        self.assertEqual(MOD.expected_mode()['batch_complete_is_universe_complete'], False)
        self.assertEqual(MOD.expected_mode()['native_output_binary_sha256'],
                         MOD.NATIVE_OUTPUT_BINARY_SHA256)

    def test_measured_output_identity_stays_data_only_and_has_nine_exact_pins(self):
        repo = MODULE_PATH.resolve().parents[3]
        pins = MOD._native_output_identity(repo)
        self.assertEqual(len(pins), 9)
        self.assertEqual(pins['bin/verifast'], MOD.NATIVE_OUTPUT_BINARY_SHA256)
        self.assertEqual(pins['src/rust_frontend/vf_mir_translator/vf_mir_translator.ml'],
                         MOD.NATIVE_TRANSLATOR_SHA256)

    def test_changed_output_binary_is_refused_before_data_capture(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            source = home / 'src/translator.ml'
            source.parent.mkdir()
            source.write_bytes(b'synthetic source')
            binary = home / 'bin/verifast'
            binary.parent.mkdir()
            binary.write_bytes(b'synthetic measured binary')
            pins = {'src/translator.ml': sha(source.read_bytes())}
            expected_binary = sha(binary.read_bytes())
            self.assertEqual(MOD._tool_sources(home, expected_sources=pins,
                                              expected_binary=expected_binary)['bin/verifast'],
                             expected_binary)
            binary.write_bytes(b'changed synthetic binary')
            with self.assertRaisesRegex(RuntimeError, 'binary pin differs'):
                MOD._tool_sources(home, expected_sources=pins, expected_binary=expected_binary)

    def test_frozen_constructor_api_shapes_are_pinned_without_running_constructors(self):
        files = {
            'c1': Path(__file__).parent / 'sort4-caller-entry-native/a1-actual-body-c1.py',
            'c2': Path(__file__).parent / 'sort4-caller-entry-native/a1-actual-body-c2.py',
            'body': Path(__file__).parent / 'sort4-caller-entry-native/a1-actual-body-r21.py',
        }
        trees = {key: ast.parse(path.read_text(encoding='utf-8')) for key, path in files.items()}
        funcs = {key: {node.name: node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
                 for key, tree in trees.items()}
        self.assertIn('resource_controls', funcs['c1'])
        self.assertIn('construct_c5', funcs['c2'])
        self.assertIn('resource_controls_c5', funcs['c2'])
        self.assertIn('refresh_callback_coordinates', funcs['body'])
        self.assertIn('construct_actual', funcs['body'])
        c5_args = [arg.arg for arg in funcs['c2']['construct_c5'].args.args]
        self.assertEqual(c5_args, ['source', 'ghost', 'capture', 'pair_recovery', 'four_recovery',
                                   'c1_constructor', 'base_constructor', 'lemma_metadata'])

    def test_status_inference_and_explicit_not_run_are_preserved(self):
        self.assertEqual(MOD._status({'exit': 0}), 'RAN')
        self.assertEqual(MOD._status({'status': 'NOT_RUN', 'exit': 0}), 'NOT_RUN')
        self.assertEqual(MOD._status({'status': 'TIMEOUT', 'exit': 124}), 'TIMEOUT')
        self.assertEqual(MOD._status({'status': 'ERROR', 'exit': 1}), 'ERROR')

    def test_malformed_explicit_status_and_wrong_types_fail_closed(self):
        self.assertEqual(MOD._status({'status': None, 'exit': 0}), 'WRONG_TYPE')
        self.assertEqual(MOD._status({'status': False, 'exit': 0}), 'WRONG_TYPE')
        self.assertEqual(MOD._status({'status': 'BOGUS', 'exit': 0}), 'WRONG_TYPE')
        self.assertEqual(MOD._status({'exit': '0'}), 'WRONG_TYPE')
        self.assertEqual(MOD._status(None), 'WRONG_TYPE')
        self.assertEqual(MOD._status('not a stage'), 'WRONG_TYPE')

    def test_json_boundary_rejects_integer_boolean_coercion(self):
        expected = {'accepted': False, 'proof_credit': 0, 'complete': True}
        self.assertTrue(MOD._exact_boundary(expected, expected))
        self.assertFalse(MOD._exact_boundary(
            {'accepted': 0, 'proof_credit': 0, 'complete': True}, expected))
        self.assertFalse(MOD._exact_boundary(
            {'accepted': False, 'proof_credit': False, 'complete': True}, expected))
        self.assertFalse(MOD._exact_boundary(
            {'accepted': False, 'proof_credit': 0, 'complete': 1}, expected))

    def test_stage_exit_timeout_notrun_and_source_mismatch(self):
        source = {'verified/lib.rs': 'a' * 64}
        argv = ['/bin/tool', 'verified/lib.rs']
        good = {'exit': 0, 'argv': argv, 'fixture_integrity': True,
                'fixture_before': source, 'fixture_after': source}
        self.assertEqual(MOD._stage_errors(good, 'ok', expected_argv=argv,
                                           expected_fixture=source), [])
        self.assertTrue(MOD._stage_errors({'exit': 124, 'argv': argv,
            'fixture_integrity': True, 'fixture_before': source, 'fixture_after': source},
            'timeout', expected_argv=argv, expected_fixture=source))
        self.assertTrue(MOD._stage_errors({'status': 'NOT_RUN', 'exit': 0,
            'argv': argv, 'fixture_integrity': True, 'fixture_before': source,
            'fixture_after': source}, 'notrun', expected_argv=argv,
            expected_fixture=source))
        changed = {'exit': 0, 'argv': argv, 'fixture_integrity': False,
                   'fixture_before': source, 'fixture_after': {'verified/lib.rs': 'b' * 64}}
        self.assertTrue(MOD._stage_errors(changed, 'changed', expected_argv=argv,
                                           expected_fixture=source))
        wrong_target = dict(good, argv=['/bin/other'])
        self.assertTrue(MOD._stage_errors(wrong_target, 'wrong-target', expected_argv=argv,
                                           expected_fixture=source))

    def test_native_marker_accepts_exact_wrapped_ocaml_refusal(self):
        source_sha = 'a' * 64
        unit = {'bytes': 3, 'sha256': 'b' * 64}
        body = {'bytes': 4, 'sha256': 'c' * 64}
        stdout = (f'SORT4-R24-W4-DATA: source_sha256={source_sha} unit_bytes=3 '
                  f'unit_sha256={unit["sha256"]} body_bytes=4 body_sha256={body["sha256"]} '
                  'body_name=sort4_stable\n')
        stderr = MOD.NATIVE_REFUSAL_STDERR + '\nRaised at Verifier.translate in file "x.ml"\n'
        self.assertEqual(MOD._parse_native_marker(stdout, stderr, source_sha, unit, body), [])

    def test_native_marker_rejects_wrong_source_duplicate_and_plain_refusal(self):
        source_sha = 'a' * 64
        unit = {'bytes': 3, 'sha256': 'b' * 64}
        body = {'bytes': 4, 'sha256': 'c' * 64}
        marker = (f'SORT4-R24-W4-DATA: source_sha256={source_sha} unit_bytes=3 '
                  f'unit_sha256={unit["sha256"]} body_bytes=4 body_sha256={body["sha256"]} '
                  'body_name=sort4_stable\n')
        self.assertTrue(MOD._parse_native_marker(marker, MOD.NATIVE_REFUSAL_STDERR,
                                                 'd' * 64, unit, body))
        self.assertTrue(MOD._parse_native_marker(marker + marker,
            MOD.NATIVE_REFUSAL_STDERR, source_sha, unit, body))
        self.assertTrue(MOD._parse_native_marker(marker,
            MOD.NATIVE_REFUSAL + '\n', source_sha, unit, body))

    def test_c5_scope_source_mutations_preserve_ghost_stripped_runtime(self):
        verified, _ = make_count5_source()
        original = scrub_ghost(verified)
        fake = types.SimpleNamespace(
            C5_SCOPE_MARKER=b'        //@ __vf_callback_scope5();\n',
            C5_LEFT_PRECREATE=b'        //@ let left5_ref = precreate_ref::<T>(c);\n',
            NORMAL5=b'        //@ NORMAL5 recovery\n',
            LO_SELECT=b'        let lo = hint::select_unpredictable(c5, unknown_right, unknown_left);\n')
        rows = MOD._c5_scope_controls(verified, original,
            types.SimpleNamespace(strip_ghost=scrub_ghost),
            {'actual_indexed_calls': 5}, fake)
        self.assertEqual([row[0] for row in rows], [
            'c5-scope-escape-negative', 'c5-missing-scope-marker-negative',
            'c5-cross-scope-read-negative'])
        for _, candidate, stripped, meta in rows:
            self.assertEqual(scrub_ghost(candidate), original)
            self.assertEqual(stripped, original)
            self.assertFalse(meta['native_scope_validator_executed'])
            self.assertIn('OPEN', meta['source_observation_note'])

    def test_c3_c4_adapter_refuses_prefix_metadata_spoof(self):
        with self.assertRaisesRegex(RuntimeError, 'actual count-five constructor output'):
            MOD._indexed_controls_at_count5(3, b'', b'', types.SimpleNamespace(strip_ghost=lambda raw: raw),
                b'', {'actual_indexed_calls': 3}, types.SimpleNamespace(), lambda _: [])

    def test_stage_service_internal_typeerror_is_not_retried(self):
        calls = []
        def broken(name, argv, root, env, fixture_hashes, deadline, cap,
                   *, stdin_name=None, stdout_name=None):
            calls.append(name)
            raise TypeError('original stage typeerror')
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(TypeError, 'original stage typeerror'):
                MOD._stage_call(broken, 'one', [], Path(tmp), {}, {}, 123, 1)
        self.assertEqual(calls, ['one'])

    def test_safe_paths_reject_symlink_ancestors_and_output_aliases(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            real = base / 'real'
            real.mkdir()
            alias = base / 'alias'
            alias.symlink_to(real, target_is_directory=True)
            with self.assertRaisesRegex(RuntimeError, 'symlink'):
                MOD._assert_path_chain(alias / 'child', allow_missing=True)
            with self.assertRaisesRegex(RuntimeError, 'symlink'):
                MOD._safe_path(alias, alias / 'child', allow_missing=True)

    def test_native_tool_build_fake_service_keeps_pinned_cloud_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / 'repo'; repo.mkdir()
            cloud = root / 'cloud'; cloud.mkdir()
            work = root / 'evidence' / 'tool-build'; work.mkdir(parents=True)
            native = root / 'input-tool'; native.mkdir()
            target = root / 'copied-tool'
            patch_path = repo / MOD.NATIVE_PATCH_REL
            patch_path.parent.mkdir(parents=True)
            patch_path.write_bytes((Path(__file__).parent /
                'sort4-caller-entry-native/w4-control-fingerprint-r24.patch').read_bytes())
            manifest_path = repo / MOD.NATIVE_MANIFEST_REL
            manifest_path.parent.mkdir(parents=True)
            manifest_path.write_bytes((Path(__file__).parents[1] /
                'task-history/select-callee-r24/W4-CONTROL-FINGERPRINT-MANIFEST.json').read_bytes())
            args = types.SimpleNamespace(repo=repo, deadline_epoch=9999999999)
            base_hashes = {**MOD.NATIVE_TOOL_SOURCE_HASHES, 'bin/verifast': MOD.NATIVE_BINARY_SHA256}
            built_sources = dict(MOD.NATIVE_TOOL_SOURCE_HASHES)
            built_sources['src/rust_frontend/vf_mir_translator/vf_mir_translator.ml'] = MOD.NATIVE_TRANSLATOR_SHA256
            built_hashes = {**built_sources, 'bin/verifast': 'd' * 64}
            seen_env = {}

            def fake_hashes(home, *, expected_sources=None, expected_binary='INPUT'):
                return built_hashes if expected_sources is not None and expected_sources.get(
                    'src/rust_frontend/vf_mir_translator/vf_mir_translator.ml') == MOD.NATIVE_TRANSLATOR_SHA256 else base_hashes

            def fake_stage(name, argv, stage_root, env, fixture_hashes, deadline, cap,
                           *, stdin_name=None, stdout_name=None):
                if name == 'native-tool-copy':
                    target.mkdir()
                    (target / 'src').mkdir()
                if name == 'native-tool-build':
                    seen_env.update(env)
                return {'exit': 0, 'argv': argv, 'fixture_integrity': True,
                        'fixture_before': {}, 'fixture_after': {}}

            env_path = '/pinned/cloud-vfdeps:/usr/bin'
            with patch.object(MOD, 'NATIVE_OUTPUT_HOME', target), \
                 patch.object(MOD, '_tool_sources', side_effect=fake_hashes), \
                 patch.object(MOD, '_native_output_identity', return_value=built_hashes), \
                 patch.dict(os.environ, {'PATH': env_path, 'CAPNP_INC_DIR': '/pinned/capnp',
                                        'LD_LIBRARY_PATH': '/pinned/lib'}):
                result = MOD._prepare_native_tool(args, work_root=work,
                    cloud_dir=cloud, native_home=native, stage_runner=fake_stage)
            self.assertEqual(result['errors'], [])
            self.assertEqual(seen_env['PATH'], env_path)
            self.assertEqual(seen_env['CAPNP_INC_DIR'], '/pinned/capnp')
            self.assertEqual(seen_env['LD_LIBRARY_PATH'], '/pinned/lib')

    def test_c6_prerequisite_schema_is_current_contract_input_boundary(self):
        summary = {'schema': 'select-r24-w4-contract-inputs-v1', 'complete': True,
            'phase_id': MOD.R24_PHASE, 'route_phase_id': MOD.R21_PHASE,
            'owner': 'select-sort4', 'lane': MOD.LANE, 'profile': MOD.PROFILE,
            'build_id': '11111111-1111-4111-8111-111111111111', 'candidate': 'a' * 40,
            'caller_body_proof_admission': False, 'accepted': False,
            'publication_allowed': False, 'typed_call_linkage': 'UNKNOWN',
            'call_linkage': 'UNKNOWN', 'caller_body_proof_status': 'UNKNOWN', 'proof_credit': 0,
            'cases': []}
        audit = {'schema': 'select-r24-w4-contract-inputs-v1-audit', 'complete': True,
            'evidence_complete': True, 'candidate': 'a' * 40,
            'build_id': '11111111-1111-4111-8111-111111111111',
            'accepted': False, 'publication_allowed': False, 'proof_credit': 0}
        with patch.dict(os.environ, {'CLOUD_BUILD_ID': summary['build_id']}):
            self.assertTrue(MOD._prerequisite_errors(summary, audit, 'a' * 40))
            summary['cases'] = [{'case': name, 'expected_classification': cls,
                'errors': [], 'facts': {'complete': True, 'classification': cls}}
                for name, cls in zip(('positive', 'false-normal', 'false-unwind',
                    'duplicate-thread', 'mut-pointer', 'extra-declaration'),
                    ('INPUTS_MATCH',) + ('EXPECTED_INPUT_REFUSAL',) * 5)]
            self.assertEqual(MOD._prerequisite_errors(summary, audit, 'a' * 40), [])


if __name__ == '__main__':
    unittest.main()
