"""Synthetic service/parser tests only; no runner/tool/real evidence input."""
import copy
import importlib.util
from pathlib import Path
import unittest

SPEC = importlib.util.spec_from_file_location('a1_matrix_pure_test', Path(__file__).with_name('a1-matrix-classifier.py'))
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)
BUILD = '11111111-1111-4111-8111-111111111111'
EXPECTED = {'source_id': 'a' * 64, 'unit_id': 'b' * 64}
PINS = {'tool_id': 'c' * 64, 'profile_id': 'd' * 64, 'proof_id': 'e' * 40,
        'infra_id': 'f' * 40, 'target_id': 'A1-FIRST-MATRIX-THRESHOLD-INTERFACE'}
INVENTORY = {'default16': {'compiler_impl_id': '11', 'compiler_item_id': '12'},
             'freeze32': {'compiler_impl_id': '21', 'compiler_item_id': '22'}}


def source(case):
    return {'proof_credit': False, 'raw': {'case_id': case, 'build_id': BUILD, **EXPECTED,
        'paired_support': {'paired_support_passed': True}, 'focus_is_export_or_translation_filter': False,
        'focus': 'verified/lib.rs:0', 'artifacts': {'proof-ast.ml': {'sha256': '0' * 64}},
        'stages': {'verification': {'exit': 0}}, 'source_pair_sha256': {'verified': 'a' * 64, 'original': 'b' * 64}},
        'structure': {'threshold_posts': {'classification': 'STRUCTURE_ONLY_UNRUN_PROOF', 'common_checked': True},
        'caller_calls': {'ast': {'owner': 'a1_guard_observer', 'classification': 'CALL_AST_STRUCTURE_ONLY'}}},
        'proof_candidate': {'classification': 'FOCUSED_VF0_CANDIDATE', 'candidate_passed': True, 'body_verified': True},
        'execution_attestation': {'body_count': 1, 'focus_body_reached': True, 'focus_body_verified': True,
        'focus_conformance_verified': True, 'normal_posts_preserved': True, 'unwind_posts_preserved': True,
        'caller_body_reached': True, 'caller_body_verified': True}}


def body(case):
    obs = source(case)
    impl = m.BODY[case]
    obs['execution_attestation']['compiler_identity'] = {'impl': impl, **INVENTORY[impl]}
    if case.startswith('N-'):
        obs['raw']['stages']['verification']['exit'] = 1
        obs['proof_candidate'] = {'classification': 'INTENDED_FOCUSED_FAILURE_CANDIDATE',
            'predicate': 'result<=32', 'target_reached': True, 'error_context': {'stage': 'impl-body'}}
        obs['execution_attestation']['focus_body_verified'] = False
    return obs


class MatrixClassifier(unittest.TestCase):
    def classify(self, case, obs, expected=None):
        return m.classify_case(case, obs, expected_input=expected or EXPECTED,
                              run_pins=PINS, build_id=BUILD, expected_inventory=INVENTORY)

    def test_absent_remains_not_run(self):
        self.assertEqual(self.classify('P1', None)['status'], 'NOT_RUN')

    def test_pre_stage_deadline_refusal_remains_not_run(self):
        result = self.classify('P1', {'not_run': True, 'reason': 'shared deadline', 'proof_credit': False})
        self.assertEqual(result['status'], 'NOT_RUN')
        self.assertFalse(result['matrix_gate_passed'])

    def test_unclassified_raw_does_not_pass(self):
        for case in ('P0a', 'P0c', 'P1', 'P-dispatch', 'OFF', 'N-binding', 'R1'):
            with self.subTest(case=case):
                self.assertFalse(self.classify(case, {'proof_credit': False, 'raw': {'stages': {}}})['matrix_gate_passed'])

    def test_both_body_routes_require_identity_stage_and_conformance(self):
        for case in m.BODY:
            obs = body(case)
            self.assertTrue(self.classify(case, obs)['matrix_gate_passed'])
            for key in ('focus_conformance_verified', 'normal_posts_preserved', 'unwind_posts_preserved'):
                bad = copy.deepcopy(obs); bad['execution_attestation'][key] = False
                self.assertFalse(self.classify(case, bad)['matrix_gate_passed'])
            bad = copy.deepcopy(obs); bad['execution_attestation']['compiler_identity']['compiler_item_id'] = '99'
            self.assertFalse(self.classify(case, bad)['matrix_gate_passed'])

    def test_negative_body_header_failure_not_intended(self):
        obs = body('N-default-contract'); obs['proof_candidate']['error_context']['stage'] = 'prototype-conformance'
        self.assertEqual(self.classify('N-default-contract', obs)['status'], 'INCONCLUSIVE')

    def test_body_input_build_and_unit_continuity(self):
        for key in ('source_id', 'unit_id', 'build_id'):
            obs = body('P0a'); obs['raw'][key] = 'wrong'
            self.assertFalse(self.classify('P0a', obs)['matrix_gate_passed'])

    def test_caller_requires_actual_vf0(self):
        obs = source('P0c')
        self.assertTrue(self.classify('P0c', obs)['matrix_gate_passed'])
        obs['raw']['stages']['verification']['exit'] = 1
        self.assertFalse(self.classify('P0c', obs)['matrix_gate_passed'])

    def test_dispatch_requires_independent_trace_classifier(self):
        obs = source('P-dispatch')
        self.assertFalse(self.classify('P-dispatch', obs)['matrix_gate_passed'])
        obs['dispatch_classifier'] = {'classification': 'ORIGINAL_COMMON_TRAIT_DISPATCH_OBSERVED'}
        self.assertTrue(self.classify('P-dispatch', obs)['matrix_gate_passed'])

    def test_p1_requires_full_native_gate_without_body_credit(self):
        obs = source('P1')
        self.assertFalse(self.classify('P1', obs)['matrix_gate_passed'])
        obs['structure']['small_sort_interface'] = {'structural_pass': True, 'body_count': 0,
            'proof_credit': False, 'compiler_clauses_source_bound': True,
            'impls': {impl: {'native_matches_r_only_baseline': True} for impl in INVENTORY}}
        result = self.classify('P1', obs)
        self.assertTrue(result['matrix_gate_passed'])
        self.assertEqual(result['record']['body_count'], 0)
        self.assertFalse(result['record']['proof_credit'])

    def test_synthetic_routes_require_every_observed_input_classifier(self):
        for case, mutations in m.SYNTHETIC.items():
            messages = []
            for i, mutation in enumerate(mutations):
                messages.append({'mutation': mutation, 'transport': {'build_id': BUILD, 'synthetic': True, 'compiler_derived': False,
                    'refinement_derived': False, 'decoded_input_sha256': str(i) * 64,
                    'stages': {'synthetic-encode': {'exit': 0}, 'synthetic-translator': {'exit': 0 if case == 'N-alpha-valid' else 1}}},
                    'classifier': {'classification': 'SYNTHETIC_REPRESENTATION_ACCEPTED' if case == 'N-alpha-valid' else 'SYNTHETIC_REFUSAL_OBSERVED',
                    'proof_credit': False, 'compiler_derived': False, 'refinement_derived': False, 'summary_available': False}})
            expected = {**EXPECTED, 'synthetic_input_sha256': tuple(str(i) * 64 for i in range(len(messages)))}
            obs = {'proof_credit': False, 'messages': messages}
            result = self.classify(case, obs, expected)
            self.assertTrue(result['matrix_gate_passed'], (case, result))
            self.assertEqual(result['provenance'], 'synthetic-transport-control')
            messages[-1]['classifier']['classification'] = 'INCONCLUSIVE_SYNTHETIC_TRANSPORT'
            self.assertFalse(self.classify(case, obs, expected)['matrix_gate_passed'])

    def test_synthetic_provenance_and_hash_cannot_be_upgraded(self):
        obs = {'proof_credit': False, 'messages': [{'mutation': 'binder_collapse',
            'transport': {'compiler_derived': True}, 'classifier': {}}]}
        self.assertFalse(self.classify('N-binder-collapse', obs)['matrix_gate_passed'])

    def test_false31_requires_own_pair_body_proofs_receipt_and_boundary(self):
        caller = source('N-false31')
        caller['raw']['stages']['verification']['exit'] = 1
        caller['proof_candidate'] = {'classification': 'INTENDED_FOCUSED_FAILURE_CANDIDATE',
            'predicate': 'len<=31', 'target_reached': True, 'intended_failure_observed': True}
        caller['execution_attestation']['caller_body_verified'] = False
        pair = caller['raw']['source_pair_sha256']
        own = {case: body(case) for case in ('P0a', 'P0b')}
        for case, obs in own.items():
            obs['raw']['source_pair_sha256'] = copy.deepcopy(pair)
            obs['raw']['focus_case_id'] = case
            obs['raw']['case_id'] = 'N-false31'
        obs = {'proof_credit': False, 'classification': 'FALSE31_OWN_PAIR_REPROVED_AND_CALLER_OBSERVED',
            'receipt_issued_after_both_bodies': True, 'source_pair_sha256': pair,
            'caller_case': caller, 'body_cases': own,
            'boundary_observation': {'classification': 'LEN32_BOUNDARY_ADMISSIBLE_BY_CHECKED_INTERFACE_AND_GUARD',
                'source_pair_sha256': pair, 'threshold_upper_bound': 32, 'boundary_len': 32, 'guard_expression': 'len <= T::small_sort_threshold()',
                'boundary_satisfies_guard': True, 'proof_credit': False}}
        self.assertTrue(self.classify('N-false31', obs)['matrix_gate_passed'])
        bad = copy.deepcopy(obs); bad['body_cases']['P0a']['raw']['source_pair_sha256']['verified'] = 'positive-pair'
        self.assertFalse(self.classify('N-false31', bad)['matrix_gate_passed'])
        for key in ('receipt_issued_after_both_bodies', 'boundary_observation'):
            bad = copy.deepcopy(obs); del bad[key]
            self.assertFalse(self.classify('N-false31', bad)['matrix_gate_passed'])

    def test_admission_controls_need_actual_input_and_intended_refusal(self):
        for case, classified in (
                ('N-source', 'SOURCE_CERTIFICATE_REFUSAL_OBSERVED'),
                ('N-binding', 'CALL_BINDING_CLAIM_REFUSAL_OBSERVED'),
                ('N-region-swap', 'INPUT_REGION_ROLE_REFUSAL_OBSERVED'),
                ('N-clause-redirect', 'LEGACY_REDIRECT_REFUSAL_OBSERVED')):
            expected = {**EXPECTED, 'control_input_sha256': '9' * 64}
            obs = {'proof_credit': False, **EXPECTED, 'input_identity_verified': True,
                   'input_sha256': '9' * 64, 'classifier': {'classification': classified}}
            self.assertTrue(self.classify(case, obs, expected)['matrix_gate_passed'])
            obs['classifier']['classification'] = 'SYNTHETIC_REFUSAL_OBSERVED'
            self.assertFalse(self.classify(case, obs, expected)['matrix_gate_passed'])
            obs['classifier']['classification'] = classified
            obs['input_sha256'] = '8' * 64
            self.assertFalse(self.classify(case, obs, expected)['matrix_gate_passed'])

    def test_off_needs_exact_trait_diagnostic(self):
        obs = {'proof_credit': False, **EXPECTED, 'input_identity_verified': True,
            'classification': 'OFF_BASELINE_OBSERVATION_ONLY', 'source_pair_immutable': True,
            'first_diagnostic': "verified/lib.rs(13,1): error: Duplicate type parameter ''_'.",
            'duplicate_trait_parameter_at_source_declaration': True}
        self.assertTrue(self.classify('OFF', obs)['matrix_gate_passed'])
        obs['first_diagnostic'] = 'error: receipt unavailable'
        self.assertFalse(self.classify('OFF', obs)['matrix_gate_passed'])

    def test_all_26_records_satisfy_exact_admission_schema_without_proof_credit(self):
        import sys
        spec = importlib.util.spec_from_file_location('a1_matrix_admission_synthetic',
            Path(__file__).with_name('a1-contract-admission.py'))
        admission = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = admission
        spec.loader.exec_module(admission)
        expected, observations = {}, {}
        for case, values in admission.MATRIX.items():
            expected[case] = {**EXPECTED, **dict(zip(
                ('stage', 'predicate', 'location', 'outcome', 'classification'), values))}
            if case in m.BODY:
                expected[case]['focused_item_id'] = INVENTORY[m.BODY[case]]['compiler_item_id']
                obs = body(case)
            elif case == 'P0c':
                obs = source(case)
            elif case in ('P1', 'P-dispatch'):
                obs = source(case)
                obs['dispatch_classifier'] = {'classification': 'ORIGINAL_COMMON_TRAIT_DISPATCH_OBSERVED'}
                obs['structure']['small_sort_interface'] = {'structural_pass': True, 'body_count': 0,
                    'proof_credit': False, 'compiler_clauses_source_bound': True,
                    'impls': {impl: {'native_matches_r_only_baseline': True} for impl in INVENTORY}}
            elif case in m.SYNTHETIC:
                messages = []
                for i, mutation in enumerate(m.SYNTHETIC[case]):
                    messages.append({'mutation': mutation, 'transport': {'build_id': BUILD,
                        'synthetic': True, 'compiler_derived': False, 'refinement_derived': False,
                        'decoded_input_sha256': str(i) * 64,
                        'stages': {'synthetic-encode': {'exit': 0}, 'synthetic-translator': {'exit': 0 if case == 'N-alpha-valid' else 1}}},
                        'classifier': {'classification': 'SYNTHETIC_REPRESENTATION_ACCEPTED' if case == 'N-alpha-valid' else 'SYNTHETIC_REFUSAL_OBSERVED',
                        'proof_credit': False, 'compiler_derived': False, 'refinement_derived': False, 'summary_available': False}})
                expected[case]['synthetic_input_sha256'] = tuple(str(i) * 64 for i in range(len(messages)))
                obs = {'proof_credit': False, 'messages': messages}
            elif case in ('N-source', 'N-binding', 'N-region-swap', 'N-clause-redirect'):
                expected[case]['control_input_sha256'] = '9' * 64
                classes = {'N-source': 'SOURCE_CERTIFICATE_REFUSAL_OBSERVED',
                    'N-binding': 'CALL_BINDING_CLAIM_REFUSAL_OBSERVED',
                    'N-region-swap': 'INPUT_REGION_ROLE_REFUSAL_OBSERVED',
                    'N-clause-redirect': 'LEGACY_REDIRECT_REFUSAL_OBSERVED'}
                obs = {'proof_credit': False, **EXPECTED, 'input_identity_verified': True,
                    'input_sha256': '9' * 64, 'classifier': {'classification': classes[case]}}
            elif case == 'OFF':
                obs = {'proof_credit': False, **EXPECTED, 'input_identity_verified': True,
                    'classification': 'OFF_BASELINE_OBSERVATION_ONLY', 'source_pair_immutable': True,
                    'first_diagnostic': "verified/lib.rs(13,1): error: Duplicate type parameter ''_'.",
                    'duplicate_trait_parameter_at_source_declaration': True}
            elif case in m.REGRESSIONS:
                negative = m.REGRESSIONS[case][1] is not None
                obs = {'proof_credit': False, **EXPECTED, 'input_identity_verified': True,
                    'gate_passed': True, 'paired_support_passed': True, 'proof_ast_captured': True, 'source_pair_immutable': True,
                    'classification': 'INTENDED_ASSERTION_NEGATIVE_RAW_REVIEW_REQUIRED' if negative else 'FRESH_VF0_CANDIDATE_RAW_REVIEW_REQUIRED',
                    'first_causal_stage': 'verification' if negative else 'NONE_OBSERVED'}
            else:
                caller = source('N-false31')
                caller['raw']['stages']['verification']['exit'] = 1
                caller['proof_candidate'] = {'classification': 'INTENDED_FOCUSED_FAILURE_CANDIDATE',
                    'predicate': 'len<=31', 'target_reached': True, 'intended_failure_observed': True}
                caller['execution_attestation']['caller_body_verified'] = False
                pair = caller['raw']['source_pair_sha256']
                own = {k: body(k) for k in ('P0a', 'P0b')}
                for k, value in own.items():
                    value['raw']['case_id'] = 'N-false31'; value['raw']['focus_case_id'] = k
                obs = {'proof_credit': False, 'classification': 'FALSE31_OWN_PAIR_REPROVED_AND_CALLER_OBSERVED',
                    'receipt_issued_after_both_bodies': True, 'source_pair_sha256': pair,
                    'caller_case': caller, 'body_cases': own,
                    'boundary_observation': {'classification': 'LEN32_BOUNDARY_ADMISSIBLE_BY_CHECKED_INTERFACE_AND_GUARD',
                        'source_pair_sha256': pair, 'threshold_upper_bound': 32, 'boundary_len': 32,
                        'guard_expression': 'len <= T::small_sort_threshold()', 'boundary_satisfies_guard': True, 'proof_credit': False}}
            observations[case] = obs
        records = []
        for case, obs in observations.items():
            classified = self.classify(case, obs, expected[case])
            self.assertTrue(classified['matrix_gate_passed'], (case, classified))
            records.append(classified['record'])
        self.assertEqual(len(records), 26)
        gate = admission.A1Admission(expected_inventory=INVENTORY, expected_run_pins=PINS,
            expected_impl_inputs={impl: EXPECTED for impl in INVENTORY}, expected_cases=expected)
        gate.record_matrix(records)
        self.assertEqual(len(gate.matrix_records), 26)
        self.assertFalse(gate.common_summary_available)
        self.assertFalse(gate.first_matrix_accepted)
        self.assertTrue(all(row['proof_credit'] is False for row in gate.matrix_records.values()))

    def test_all_regressions_require_current_intended_gate(self):
        for case, (_, negative) in m.REGRESSIONS.items():
            obs = {'proof_credit': False, **EXPECTED, 'input_identity_verified': True,
                'gate_passed': True, 'paired_support_passed': True, 'proof_ast_captured': True, 'source_pair_immutable': True,
                'classification': 'INTENDED_ASSERTION_NEGATIVE_RAW_REVIEW_REQUIRED' if negative else 'FRESH_VF0_CANDIDATE_RAW_REVIEW_REQUIRED',
                'first_causal_stage': 'verification' if negative else 'NONE_OBSERVED'}
            self.assertTrue(self.classify(case, obs)['matrix_gate_passed'])
            obs['first_causal_stage'] = 'normal-export'
            self.assertFalse(self.classify(case, obs)['matrix_gate_passed'])


if __name__ == '__main__':
    unittest.main()
