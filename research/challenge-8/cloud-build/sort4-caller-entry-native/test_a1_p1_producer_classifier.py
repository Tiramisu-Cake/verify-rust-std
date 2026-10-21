"""P1 classifier tests with output from the current structural AST producer."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
from pathlib import Path
import unittest

BASE = Path(__file__).parent
spec = importlib.util.spec_from_file_location(
    'a1_matrix_p1_producer_classifier', BASE / 'a1-matrix-classifier.py')
classifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(classifier)

import test_a1_ast_gates as ast_fixtures

BUILD = '11111111-1111-4111-8111-111111111111'
_SOURCE = ast_fixtures.inventory_fixture.valid_source()
_CERTIFICATE = ast_fixtures.inventory_fixture.certificate(_SOURCE)
EXPECTED_INPUT = {
    'source_id': _CERTIFICATE['cases']['P0a']['source_id'],
    'unit_id': 'b' * 64,
}
RUN_PINS = {'tool_id': 'c' * 64, 'profile_id': 'd' * 64,
            'proof_id': 'e' * 40, 'infra_id': 'f' * 40,
            'target_id': 'A1-FIRST-MATRIX-THRESHOLD-INTERFACE'}


def producer_case():
    """Build a P1 observation from real synthetic compiler/AST fixture producers."""
    generated_source = _CERTIFICATE['cases']['P0a']['generated_source_sha256']
    raw_pair = {'verified': generated_source, 'original': 'b' * 64}
    ast, inventory, baseline, actual_pair = ast_fixtures.p1_fixture(
        source_pair_sha256=raw_pair)
    # The fixture must construct this pair into the capture receipt before
    # small_sort_native_baseline validates and extracts it.
    captured_pair = baseline['reference_receipt']['source_pair_sha256']
    if captured_pair != raw_pair:
        raise AssertionError('P1 fixture did not capture the requested source pair')
    gate = ast_fixtures.gate.small_sort_interface(
        ast, inventory, baseline=baseline,
        actual_source_pair_sha256=actual_pair)
    impl_rows = inventory['inventory']['impl_small_sort_identities']
    expected_inventory = {
        row['impl']: {'compiler_impl_id': str(row['impl_def_index']),
                      'compiler_item_id': str(row['item_def_index'])}
        for row in impl_rows
    }
    obs = {
        'proof_credit': False,
        'run_identity': dict(RUN_PINS),
        'raw': {
            'case_id': 'P1', 'build_id': BUILD, **EXPECTED_INPUT,
            'paired_support': {'paired_support_passed': True},
            'focus_is_export_or_translation_filter': False,
            'focus': 'verified/lib.rs:0',
            'artifacts': {'proof-ast.ml': {'sha256': '0' * 64}},
            'source_pair_sha256': raw_pair,
            'stages': {'verification': {'exit': 0}},
        },
        'structure': {
            'inventory': inventory,
            'small_sort_interface': gate,
            'threshold_posts': {'classification': 'STRUCTURE_ONLY_UNRUN_PROOF'},
        },
    }
    return obs, expected_inventory, ast, inventory, baseline, actual_pair


def classify(obs, expected_inventory):
    return classifier.classify_case(
        'P1', obs, expected_input=EXPECTED_INPUT, run_pins=RUN_PINS,
        build_id=BUILD, expected_inventory=expected_inventory)


class P1ProducerConsumerSchema(unittest.TestCase):
    def test_current_producer_record_is_accepted_without_body_credit(self):
        obs, expected, *_ = producer_case()
        result = classify(obs, expected)
        self.assertTrue(result['matrix_gate_passed'], result.get('reason'))
        self.assertEqual(result['record']['body_count'], 0)
        self.assertFalse(result['record']['proof_credit'])
        self.assertEqual(result['record']['tool_id'], RUN_PINS['tool_id'])
        self.assertEqual(result['record']['profile_id'], RUN_PINS['profile_id'])

    def test_missing_null_wrong_type_legacy_and_extra_schema_fail_closed(self):
        mutations = (
            lambda gate: gate.pop('schema'),
            lambda gate: gate.__setitem__('schema', None),
            lambda gate: gate.__setitem__('schema', 7),
            lambda gate: gate.__setitem__('native_matches_r_only_baseline', True),
            lambda gate: gate['impls']['default16'].__setitem__(
                'native_matches_r_only_baseline', True),
            lambda gate: gate['impls']['default16'].pop(
                'native_matches_r_only_original_impl'),
            lambda gate: gate['impls']['default16'].__setitem__(
                'native_matches_r_only_original_impl', None),
            lambda gate: gate['impls']['freeze32'].__setitem__(
                'native_matches_r_only_original_impl', False),
            lambda gate: gate['impls']['freeze32'].__setitem__(
                'native_matches_r_only_original_impl', 1),
            lambda gate: gate['impls'].pop('freeze32'),
            lambda gate: gate['impls'].__setitem__('extra', copy.deepcopy(gate['impls']['default16'])),
        )
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                obs, expected, *_ = producer_case()
                mutate(obs['structure']['small_sort_interface'])
                self.assertFalse(classify(obs, expected)['matrix_gate_passed'])

    def test_per_impl_source_compiler_and_component_identities_are_exact(self):
        mutations = (
            lambda gate: gate['impls']['default16'].__setitem__('compiler_impl_id', '99'),
            lambda gate: gate['impls']['freeze32'].__setitem__('compiler_item_id', '99'),
            lambda gate: gate['impls']['default16'].__setitem__('alias', '__a1_impl_2_item_22_small_sort'),
            lambda gate: gate['impls']['freeze32'].__setitem__('compiler_signature_digest', 'x' * 64),
            lambda gate: gate['impls']['default16'].__setitem__('actual_definition_bound_to_compiler_item', False),
            lambda gate: gate['impls']['default16']['native_sha256'].__setitem__('pre', '0' * 64),
            lambda gate: gate['impls']['freeze32']['native_sha256'].__setitem__('unwind', '0' * 64),
        )
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                obs, expected, *_ = producer_case()
                mutate(obs['structure']['small_sort_interface'])
                self.assertFalse(classify(obs, expected)['matrix_gate_passed'])

    def test_common_pre_normal_unwind_hashes_and_source_pair_are_bound(self):
        for component in ('pre', 'returning', 'unwind'):
            obs, expected, *_ = producer_case()
            obs['structure']['small_sort_interface']['normalized_native'][component] = ('mutated',)
            self.assertFalse(classify(obs, expected)['matrix_gate_passed'], component)
        for mutation in ('actual_hash', 'verified_hash', 'source_id', 'unit_id', 'build_id'):
            obs, expected, *_ = producer_case()
            if mutation == 'actual_hash':
                obs['structure']['small_sort_interface']['actual_source_pair_sha256'] = '9' * 64
            elif mutation == 'verified_hash':
                obs['raw']['source_pair_sha256']['verified'] = '9' * 64
            else:
                obs['raw'][mutation] = 'wrong'
            self.assertFalse(classify(obs, expected)['matrix_gate_passed'], mutation)
        obs, expected, *_ = producer_case()
        changed_verified = '9' * 64
        obs['raw']['source_pair_sha256']['verified'] = changed_verified
        obs['structure']['small_sort_interface']['actual_source_pair_sha256'] = hashlib.sha256(
            (changed_verified + ':' + obs['raw']['source_pair_sha256']['original']).encode('ascii')
        ).hexdigest()
        self.assertFalse(classify(obs, expected)['matrix_gate_passed'],
                         'coordinated raw/gate pair hash mutation')

    def test_observed_tool_and_profile_pins_match_this_run_exactly(self):
        for key, value in (('tool_id', '9' * 64), ('profile_id', '8' * 64),
                           ('proof_id', '7' * 40), ('infra_id', '6' * 40),
                           ('target_id', 'other-target')):
            obs, expected, *_ = producer_case()
            obs['run_identity'][key] = value
            self.assertFalse(classify(obs, expected)['matrix_gate_passed'], key)
        for key in ('tool_id', 'profile_id', 'proof_id', 'infra_id', 'target_id'):
            obs, expected, *_ = producer_case()
            altered = dict(RUN_PINS)
            altered[key] = ('9' * (40 if key in ('proof_id', 'infra_id') else 64)
                            if key != 'target_id' else 'other-target')
            result = classifier.classify_case(
                'P1', obs, expected_input=EXPECTED_INPUT, run_pins=altered,
                build_id=BUILD, expected_inventory=expected)
            self.assertFalse(result['matrix_gate_passed'], key)
        for bad in (None, {}, {'tool_id': 'c' * 64},
                    {**RUN_PINS, 'legacy_profile': 'd' * 64}):
            obs, expected, *_ = producer_case()
            obs['run_identity'] = bad
            self.assertFalse(classify(obs, expected)['matrix_gate_passed'])
        for key, bad in (('proof_id', 'e' * 64), ('infra_id', 'f' * 64)):
            obs, expected, *_ = producer_case()
            obs['run_identity'][key] = bad
            self.assertFalse(classify(obs, expected)['matrix_gate_passed'], key)

    def test_common_and_actual_impl_header_native_ast_controls_remain_active(self):
        controls = (
            {'candidate_scratch_name': 'wrong_scratch'},
            {'drop_resource': True},
            {'drop_unwind': True},
            {'drop_outcome': True},
            {'substitute': True},
            {'mix_region': True},
            {'lifetime_bound_mutant': True},
            {'mix_native_fraction': True},
            {'wrong_maybeuninit': True},
            {'candidate_default_prefixed_wrong_source': True},
        )
        for options in controls:
            with self.subTest(options=options):
                ast, inventory, baseline, actual_pair = ast_fixtures.p1_fixture(**options)
                with self.assertRaises(ast_fixtures.gate.AstGateError):
                    ast_fixtures.gate.small_sort_interface(
                        ast, inventory, baseline=baseline,
                        actual_source_pair_sha256=actual_pair)

    def test_required_header_and_compiler_body_spans_remain_bound(self):
        ast, inventory, baseline, actual_pair = ast_fixtures.p1_fixture()
        for mutant in (
                ast.replace('"Self"', '"OtherSelf"', 1),
                ast.replace('loc "verified/lib.rs(6,1-6,61)"',
                            'loc "verified/lib.rs(7,1-7,61)"', 1)):
            with self.subTest(mutant=mutant[:80]):
                with self.assertRaises(ast_fixtures.gate.AstGateError):
                    ast_fixtures.gate.small_sort_interface(
                        mutant, inventory, baseline=baseline,
                        actual_source_pair_sha256=actual_pair)
        for options in ({'r_only_default_bad_span': True},
                        {'r_only_default_wrong_source': True},
                        {'duplicate_r_only_span': True}):
            with self.subTest(options=options):
                with self.assertRaises(ast_fixtures.gate.AstGateError):
                    ast_fixtures.p1_fixture(**options)


if __name__ == '__main__':
    unittest.main()
