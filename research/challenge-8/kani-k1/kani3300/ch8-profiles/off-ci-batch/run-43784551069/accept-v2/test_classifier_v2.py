# Copyright Kani Contributors
# SPDX-License-Identifier: Apache-2.0 OR MIT
import copy
import unittest

from classifier_v2 import classify, consumers_after_leaves, tokens


class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.row = {'id': 'leaf', 'selector': 'm::leaf', 'mode': 'Original',
                    'expected': 'SUCCESS', 'allowed_failure_descriptions': [], 'profile': 'P'}
        self.h = {'name': 'm::leaf', 'crate_name': 'core',
                  'outcome': {'kind': 'COMPLETED', 'verdict': 'SUCCESS'},
                  'n_properties': 3, 'n_failed': 0, 'failed_properties': [],
                  'checks': {'total': 2, 'success': 2, 'failure': [], 'unreachable': [],
                             'undetermined': [], 'error': [], 'unknown': [], 'other': []},
                  'covers': {'total': 1, 'satisfied': ['m::leaf.cover.1'], 'unsatisfiable': [],
                             'unreachable': [], 'undetermined': [], 'error': [], 'unknown': [], 'other': []},
                  'unsupported_constructs': [], 'attributes': {'stubs': [], 'verified_stubs': []}}
        self.mapping = {'binding': {'target_status': 'BOUND', 'wrapper_status': 'NOT_APPLICABLE',
                                    'verified_stubs': []},
                        'coverage': {'required_ids': ['m::leaf.cover.1'],
                                     'post_target_ids': ['m::leaf.cover.1'], 'missing_obligations': []}}
        self.links, self.roles = {}, {}
        self.preflight = 'VALIDATED_OBSERVATION'

    def run_policy(self):
        return classify(self.row, self.h, self.mapping, self.links, self.roles, self.preflight)

    def unreachable(self):
        self.h['checks']['unreachable'] = ['m::target.assertion.1']
        self.h['checks']['success'] = 1

    def unsupported(self):
        u = {'id': 'm::target.unsupported_construct.1', 'class': 'unsupported_construct',
             'description': 'unsupported fixture', 'status': 'SUCCESS',
             'file': '/checkout/src.rs', 'line': '17'}
        self.h['unsupported_constructs'] = [u]
        self.links[u['id']] = {'semantics': 'assert(false); assume(false)',
                               'description': u['description'], 'file_suffix': 'src.rs', 'line': '17'}
        return u

    def test_complete_positive(self):
        self.assertEqual(self.run_policy()['status'], 'ACCEPTED')

    def test_unsupported_success_exact_id(self):
        self.unsupported()
        self.assertEqual(self.run_policy()['status'], 'ACCEPTED')

    def test_unsupported_missing_link(self):
        self.unsupported(); self.links.clear()
        self.assertEqual(self.run_policy()['status'], 'UNKNOWN')

    def test_unsupported_wrong_id(self):
        self.unsupported()['id'] = 'other.unsupported_construct.1'
        self.assertEqual(self.run_policy()['status'], 'UNKNOWN')

    def test_unsupported_wrong_source_or_class(self):
        for field, value in [('class', 'assertion'), ('line', '18'), ('file', '/wrong.rs'),
                             ('description', 'other')]:
            self.setUp(); self.unsupported()[field] = value
            self.assertEqual(self.run_policy()['status'], 'UNKNOWN')

    def test_unsupported_non_success(self):
        for status in ['FAILURE', 'UNREACHABLE']:
            self.setUp(); self.unsupported()['status'] = status
            self.assertEqual(self.run_policy()['status'], 'PENDING')

    def test_unsupported_unknown_status(self):
        for status in ['UNKNOWN', 'UNDETERMINED', 'ERROR', None, 7]:
            self.setUp(); self.unsupported()['status'] = status
            self.assertEqual(self.run_policy()['status'], 'UNKNOWN')

    def test_unsupported_success_conflict(self):
        u = self.unsupported()
        self.h['checks']['unreachable'] = [u['id']]; self.h['checks']['success'] = 1
        self.assertIn('UNSUPPORTED_STATUS_CONFLICT:' + u['id'], self.run_policy()['unknown_reasons'])

    def test_helper_name_is_not_exemption(self):
        self.unreachable()
        self.assertEqual(self.run_policy()['status'], 'UNKNOWN')

    def test_required_unreachable_roles(self):
        self.unreachable()
        for role in ['postcondition', 'frame', 'relation', 'required_section']:
            self.roles['m::target.assertion.1'] = {'role': role, 'property_location': 'src.rs:17',
                'target_wrapper_relation': 'inside_target', 'reason': 'required by scenario'}
            self.assertEqual(self.run_policy()['status'], 'PENDING')

    def test_defensive_inside_target_allowed(self):
        self.unreachable()
        self.roles['m::target.assertion.1'] = {'role': 'defensive_branch',
            'property_location': 'src.rs:17', 'target_wrapper_relation': 'inside_target',
            'reason': 'guard rejects out-of-domain input excluded by source precondition'}
        r = self.run_policy()
        self.assertEqual(r['status'], 'ACCEPTED')
        self.assertEqual(r['unreachable'][0]['decision'], 'ALLOWED_DEFENSIVE_BRANCH')

    def test_defensive_without_location_unknown(self):
        self.unreachable()
        self.roles['m::target.assertion.1'] = {'role': 'defensive_branch'}
        self.assertEqual(self.run_policy()['status'], 'UNKNOWN')

    def test_missing_required_cover_even_zero_count(self):
        self.h['covers']['satisfied'] = []; self.h['covers']['total'] = 0
        self.h['n_properties'] = 2
        self.assertEqual(self.run_policy()['status'], 'PENDING')

    def test_precall_cover_insufficient(self):
        self.mapping['coverage']['post_target_ids'] = []
        self.assertEqual(self.run_policy()['status'], 'PENDING')

    def test_precall_cover_cannot_be_postcover(self):
        self.mapping['coverage']['pre_call_only_ids'] = ['m::leaf.cover.1']
        self.assertEqual(self.run_policy()['status'], 'UNKNOWN')

    def test_unmapped_extra_cover(self):
        self.h['covers']['satisfied'].append('m::extra.cover.1')
        self.h['covers']['total'] = 2; self.h['n_properties'] = 4
        self.assertEqual(self.run_policy()['status'], 'UNKNOWN')

    def test_postcover_not_in_required_mapping(self):
        self.mapping['coverage']['post_target_ids'] = ['m::invented.cover.1']
        self.assertEqual(self.run_policy()['status'], 'UNKNOWN')

    def test_missing_obligation(self):
        self.mapping['coverage']['missing_obligations'] = ['postchecks']
        self.assertEqual(self.run_policy()['status'], 'PENDING')

    def test_unsatisfied_cover(self):
        self.h['covers']['satisfied'] = []
        self.h['covers']['unsatisfiable'] = ['m::leaf.cover.1']
        self.assertEqual(self.run_policy()['status'], 'PENDING')

    def test_unknown_check_buckets(self):
        for field in ['undetermined', 'error', 'unknown', 'other']:
            self.setUp(); self.h['checks'][field] = ['bad']; self.h['checks']['success'] = 1
            self.assertEqual(self.run_policy()['status'], 'UNKNOWN')

    def test_missing_null_wrong_type_fields(self):
        for value in [None, 7, {}, 'SUCCESS']:
            self.setUp(); self.h['checks']['unreachable'] = value
            self.assertEqual(self.run_policy()['status'], 'UNKNOWN')

    def test_lost_properties(self):
        self.h['checks']['success'] = 0
        self.assertEqual(self.run_policy()['status'], 'UNKNOWN')

    def test_duplicate_property(self):
        self.h['covers']['satisfied'] *= 2
        self.h['covers']['total'] = 2; self.h['n_properties'] = 4
        self.assertEqual(self.run_policy()['status'], 'UNKNOWN')

    def test_preflight_not_bypassed(self):
        for state in ['NOT_RUN', 'MISSING', 'INVALID_OR_PARTIAL', 'WRONG_TOOL_BINDING',
                      'WRONG_CONFIGURATION', 'WRONG_UNWIND', 'WRONG_SOURCE_FILE',
                      'SOURCE_STAGE_TARGET_MISMATCH', 'HARNESS_NOT_COMPLETED']:
            self.preflight = state
            self.assertEqual(self.run_policy()['status'], 'UNKNOWN')

    def test_full_target_same_terminal_rejected(self):
        self.row['mode'] = 'PFC'
        self.h['attributes']['kind'] = {'ProofForContract': {'target_fn': 'other :: target'}}
        self.h['contract'] = {'contracted_function_name': '_symbol'}
        self.mapping['binding'].update(source_target_expression='super::module::target',
            wrapper_status='PENDING', export_contract_symbol='_symbol')
        self.assertEqual(self.run_policy()['status'], 'UNKNOWN')
        self.h['attributes']['kind']['ProofForContract']['target_fn'] = 'super :: module :: target'
        self.assertEqual(self.run_policy()['status'], 'PENDING')

    def test_verified_stub_full_path(self):
        self.h['attributes']['verified_stubs'] = ['wrong::target']
        self.assertEqual(self.run_policy()['status'], 'UNKNOWN')

    def test_negative_named_oracle(self):
        self.row.update(expected='DETECTED', allowed_failure_descriptions=['predeclared named check'])
        self.h['outcome']['verdict'] = 'FAILURE'
        self.h['checks'].update(success=1, failure=['m::check.assertion.1'])
        self.h.update(n_failed=1, failed_properties=[{'id': 'm::check.assertion.1',
                                                    'description': 'predeclared named check',
                                                    'status': 'FAILURE'}])
        self.assertEqual(self.run_policy()['status'], 'ACCEPTED')
        self.h['failed_properties'][0]['description'] = 'unrelated'
        self.assertEqual(self.run_policy()['status'], 'PENDING')

    def test_frame_oracle_not_learned(self):
        self.row.update(expected='DETECTED', allowed_failure_descriptions=['<generated modifies placeholder>'])
        self.assertEqual(self.run_policy()['status'], 'PENDING')

    def test_consumers_evaluated_after_leaf(self):
        leaf = self.run_policy()
        consumer_row = dict(self.row, id='consumer', profile_mode='Replace:profile_wrapper',
                            leaf_companion='leaf')
        consumer = copy.deepcopy(leaf); consumer['id'] = 'consumer'
        results = {'consumer': consumer, 'leaf': leaf}
        consumers_after_leaves([consumer_row, self.row], results)
        self.assertEqual(consumer['status'], 'ACCEPTED')
        leaf['unknown_reasons'].append('unresolved role'); leaf['status'] = 'UNKNOWN'
        consumers_after_leaves([consumer_row, self.row], results)
        self.assertEqual(consumer['status'], 'PENDING')

    def test_consumer_missing_self_or_wrong_profile(self):
        for leaf_id, profile in [('missing', 'P'), ('consumer', 'P'), ('leaf', 'wrong')]:
            leaf = self.run_policy(); consumer = copy.deepcopy(leaf); consumer['id'] = 'consumer'
            r = dict(self.row, id='consumer', profile_mode='Replace:profile_wrapper',
                     leaf_companion=leaf_id, profile=profile)
            consumers_after_leaves([r, self.row], {'consumer': consumer, 'leaf': leaf})
            self.assertNotEqual(consumer['status'], 'ACCEPTED')

    def test_path_tokens_preserve_identifiers(self):
        self.assertEqual(tokens('super :: foo :: bar'), tokens('super::foo::bar'))
        for value in [None, 7, 'foo bar', 'foo:::bar', 'foo::', 'foo::<P>']:
            self.assertIsNone(tokens(value))


if __name__ == '__main__':
    unittest.main()
