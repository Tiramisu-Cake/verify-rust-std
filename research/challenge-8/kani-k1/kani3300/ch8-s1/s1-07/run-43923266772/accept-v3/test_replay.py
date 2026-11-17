#!/usr/bin/env python3
"""In-memory composer mutations below digest gates plus immutable-input checks.

setUpModule performs all three full read-only replays once. Mutation cases call
compose/qualify directly, deliberately bypassing file-digest rejection. No input
file, source worktree, historical receipt or component is edited.
"""
import copy
import json
import sys
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
import replay as p

INPUT = None
REPORT = None


def setUpModule():
    global INPUT, REPORT
    INPUT = p.load()
    REPORT = p.compose(*INPUT)


def rows(report):
    return {r['id']: r for r in report['rows']}


class Composition(unittest.TestCase):
    def test_exact_byte_replay(self):
        self.assertEqual(p.encoded(REPORT), (p.HERE / 'ACCEPT.json').read_bytes())
        self.assertEqual(p.encoded(p.compose(*INPUT)), p.encoded(REPORT))

    def test_counts_are_derived(self):
        rs = rows(REPORT)
        self.assertEqual(REPORT['totals']['rows_qualified'], sum(r['qualification'] == 'QUALIFIED' for r in rs.values()))
        self.assertEqual(REPORT['totals']['rows_qualified'], 14)
        self.assertEqual(REPORT['totals']['U_consumed'], 187)
        self.assertEqual(REPORT['totals']['profiles_v4_pfc_bound'], 22)
        self.assertEqual(REPORT['totals']['companions_qualified'], 8)
        self.assertEqual(REPORT['totals']['pending_gate_rows'], {p.SG: 21})
        self.assertEqual(REPORT['totals']['unions_qualified'], 0)

    def test_historical_evidence_is_preserved(self):
        old = INPUT[1]
        for field in ('groups', 'location_exceptions', 'unsupported_records', 'native_analysis',
                      'semantic_binding_gaps', 'cover_source_case_audit', 'producer_source'):
            self.assertEqual(REPORT[field], old[field], field)
        for rid, row in rows(REPORT).items():
            before = rows(old)[rid]
            for field in ('required_success', 'required_covers', 'negative_oracle', 'properties',
                          'inventory', 'locations', 'binary_after', 'source_reported_verdict',
                          'same_run_companion', 'successful_mir_unreachable_guard_checks'):
                self.assertEqual(row.get(field), before.get(field), (rid, field))
        original_u = {(r['row_id'], r['property_id']): r for r in old['unreachable_analysis']['records']}
        allowed = covers = 0
        for record in REPORT['unreachable_analysis']['records']:
            before = original_u[record['row_id'], record['property_id']]
            for field, value in before.items():
                if field not in {'decision', 'decision_basis'}:
                    self.assertEqual(record[field], value)
            if not before['decision'].startswith('UNKNOWN'):
                self.assertEqual(record, before)
                allowed += before['status_kind'] == 'check'
                covers += before['status_kind'] == 'cover'
            else:
                self.assertEqual(record['historical_decision_basis'], before['decision_basis'])
                self.assertTrue(record['consumed_U_record'])
        self.assertEqual((allowed, covers), (226, 2))

    def test_row_and_global_U_decisions_match_effective_records(self):
        from collections import Counter
        global_counts = Counter()
        for rid, row in rows(REPORT).items():
            expected = Counter(r['decision'] for r in REPORT['unreachable_analysis']['records'] if r['row_id'] == rid)
            self.assertEqual(row['unreachable_decisions'], dict(expected))
            self.assertEqual(row['historical_unreachable_decisions'], rows(INPUT[1])[rid]['unreachable_decisions'])
            global_counts.update(expected)
        self.assertEqual(REPORT['totals']['unreachable_decisions'], dict(global_counts))

    def test_111_roles_16_exact_and_113_covers_unchanged(self):
        success = [s for r in REPORT['rows'] for s in r['required_success']]
        covers = [c for r in REPORT['rows'] for c in r['required_covers']]
        self.assertEqual(sum(s['binding'] not in p.EXACT_SUCCESS for s in success), 111)
        self.assertEqual(sum(s['binding'] in p.EXACT_SUCCESS for s in success), 16)
        self.assertEqual(len(covers), 113)
        self.assertTrue(all(c['binding'] == 'EXACT_SAT_COVER_SEMANTIC' for c in covers))

    def test_negative_verdicts_remain_failure(self):
        negatives = [r for r in REPORT['rows'] if r['negative_oracle']]
        self.assertEqual(len(negatives), 8)
        self.assertTrue(all(r['expected'] == 'DETECTED' and r['source_reported_verdict'] == 'FAILURE'
                            and r['negative_oracle']['property']['status'] == 'FAILURE' for r in negatives))

    def test_no_independent_credit_or_review_go(self):
        self.assertEqual(REPORT['source_reported_assurance'], p.PFC_ASSURANCE)
        for field in ('independent_proof_credit', 'B1_credit', 'B2_credit'):
            self.assertEqual(REPORT[field], 'NONE')
        self.assertEqual(REPORT['review'], {'W14_input_components': 'PENDING', 'W14_composer': 'PENDING', 'CI_GO': False})
        self.assertTrue(all(r['independent_proof_credit'] == 'NONE' for r in REPORT['rows']))
        self.assertEqual(REPORT['qualified_acceptance'], 'PENDING')

    def test_stop_marker_is_only_upstream_integrity_snapshot(self):
        manifest = json.loads((p.HERE / 'INPUTS.json').read_bytes())
        self.assertEqual(manifest['admission_inputs'], ['accept/ACCEPT.json', 'accept-u/U.json', 'accept-pfc/PFC.json'])
        inherited = [rel for rel in manifest['files'] if '/s1-07/run-43923266772/accept-v2/' in rel]
        self.assertEqual(sorted(inherited), manifest['upstream_U_integrity_only_stop_marker_files'])
        self.assertFalse(any('/s1-08' in rel or 'ROLE-MAP' in rel for rel in manifest['files']))
        self.assertEqual(set(REPORT['components']), {'accept', 'accept-u', 'accept-pfc'})

    def test_every_transition_has_record_or_dependency_reason(self):
        for row in REPORT['rows']:
            t, consumed = row['transition'], row['component_consumption']
            for gate in t['removed_gates']:
                if gate == p.UG:
                    self.assertEqual(consumed['U_remaining'], [])
                    self.assertEqual(consumed['U_required'], len(consumed['U']))
                elif gate == p.PG:
                    self.assertTrue(consumed['PFC']['edges'])
                elif gate == p.CG:
                    self.assertEqual(t['companion_edge']['qualification'], 'QUALIFIED')
                else:
                    self.fail('Unexplained removal ' + gate)

    def test_summaries_cannot_seed_qualification(self):
        data = copy.deepcopy(INPUT)
        data[2]['summary'] = {'justified': 999999}
        data[3]['totals'] = {'bound': 999999}
        report = p.compose(*data)
        self.assertEqual(report['totals'], REPORT['totals'])


class Mutations(unittest.TestCase):
    def test_partial_and_missing_U_coverage(self):
        for count in (1, len(INPUT[2]['records'])):
            with self.subTest(removed=count):
                data = copy.deepcopy(INPUT)
                lost = data[2]['records'][:count]
                data[2]['records'] = data[2]['records'][count:]
                report = p.compose(*data)
                for rid in {r['row_id'] for r in lost}:
                    self.assertIn(p.UG, rows(report)[rid]['pending_gates'])
                    self.assertEqual(rows(report)[rid]['qualification'], 'PENDING')

    def test_U_status_assurance_and_hashes_below_outer_digest(self):
        cases = [('status', 'SUCCESS'), ('status', 'FAILURE'), ('request_sha256', '0'*64),
                 ('source_commit', '0'*40), ('source_sha256', '0'*64), ('variant', 'foreign'),
                 ('assurance', 'INDEPENDENT'), ('independent_sorting_proof_credit', 'B2'),
                 ('decision', 'UNKNOWN')]
        for field, value in cases:
            with self.subTest(field=field, value=value):
                data = copy.deepcopy(INPUT)
                record = data[2]['records'][0]
                rid = record['row_id']
                record[field] = value
                report = p.compose(*data)
                self.assertIn(p.UG, rows(report)[rid]['pending_gates'])
        data = copy.deepcopy(INPUT)
        data[2]['records'][0]['evidence']['properties']['sha256'] = '0'*64
        self.assertIn(p.UG, rows(p.compose(*data))[data[2]['records'][0]['row_id']]['pending_gates'])

    def test_U_foreign_duplicate_and_harness_namespaces(self):
        for field in ('row_id', 'property_id', 'group', 'harness'):
            with self.subTest(field=field):
                data = copy.deepcopy(INPUT)
                data[2]['records'][0][field] = 'foreign'
                with self.assertRaises(ValueError):
                    p.compose(*data)
        data = copy.deepcopy(INPUT)
        data[2]['records'].append(copy.deepcopy(data[2]['records'][0]))
        with self.assertRaisesRegex(ValueError, 'duplicate U'):
            p.compose(*data)

    def test_missing_PFC_chain(self):
        for count in (1, len(INPUT[3]['bindings'])):
            data = copy.deepcopy(INPUT)
            lost = data[3]['bindings'][:count]
            data[3]['bindings'] = data[3]['bindings'][count:]
            report = p.compose(*data)
            for b in lost:
                self.assertIn(p.PG, rows(report)[b['id']]['pending_gates'])

    def test_incomplete_PFC_edges_below_digest(self):
        for section in ('source', 'native', 'selected_impl', 'contract'):
            with self.subTest(section=section):
                data = copy.deepcopy(INPUT)
                b = data[3]['bindings'][0]
                b[section] = {}
                self.assertIn(p.PG, rows(p.compose(*data))[b['id']]['pending_gates'])
        for section in ('diagnostics', 'ensures', 'requires', 'modifies', 'clause_allocation_checks',
                        'target_instance', 'raw_symbol', 'decoded_modifies_wrapper', 'check_wrapper'):
            with self.subTest(contract=section):
                data = copy.deepcopy(INPUT)
                b = data[3]['bindings'][0]
                b['contract'].pop(section)
                self.assertIn(p.PG, rows(p.compose(*data))[b['id']]['pending_gates'])

    def test_PFC_status_namespace_and_source_hash(self):
        for field, value in (('status', 'PENDING'), ('gaps', ['missing']), ('group', 'foreign'),
                             ('harness', 'foreign'), ('variant', 'foreign'), ('property_count', 0)):
            with self.subTest(field=field):
                data = copy.deepcopy(INPUT)
                b = data[3]['bindings'][0]
                b[field] = value
                self.assertIn(p.PG, rows(p.compose(*data))[b['id']]['pending_gates'])
        for field in ('sha256', 'effective_target_sha256'):
            data = copy.deepcopy(INPUT)
            b = data[3]['bindings'][0]
            b['source'][field] = '0'*64
            self.assertIn(p.PG, rows(p.compose(*data))[b['id']]['pending_gates'])

    def test_PFC_foreign_and_duplicate_rows(self):
        data = copy.deepcopy(INPUT)
        data[3]['bindings'][0]['id'] = 'foreign'
        with self.assertRaisesRegex(ValueError, 'foreign PFC'):
            p.compose(*data)
        data = copy.deepcopy(INPUT)
        data[3]['bindings'].append(copy.deepcopy(data[3]['bindings'][0]))
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            p.compose(*data)

    def test_global_namespaces_versions_and_assurance(self):
        for slot, field, value in ((1, 'run', 43923266773), (2, 'run', 43923266773),
              (3, 'run', '43923266773'), (1, 'request_sha256', '0'*64),
              (2, 'source_commit', '0'*40), (3, 'tool_sha', '0'*40),
              (3, 'control_sha', '0'*40), (2, 'schema', 'future'),
              (3, 'assurance', 'INDEPENDENT'), (3, 'B2_credit', 'B2')):
            with self.subTest(slot=slot, field=field):
                data = copy.deepcopy(INPUT)
                data[slot][field] = value
                with self.assertRaises(ValueError):
                    p.compose(*data)

    def test_source_success_does_not_close_message_gate(self):
        # Even removal of the saved pending flag cannot bypass actual messages.
        data = copy.deepcopy(INPUT)
        candidate = next(r for r in data[1]['rows'] if p.SG in r['pending_gates'])
        candidate['pending_gates'].remove(p.SG)
        candidate['qualification'] = 'QUALIFIED'
        self.assertEqual(candidate['source_reported_verdict'], 'SUCCESS')
        result = rows(p.compose(*data))[candidate['id']]
        self.assertEqual(result['qualification'], 'PENDING')
        self.assertIn(p.SG, result['pending_gates'])

    def test_positive_success_cannot_replace_expected_failure(self):
        data = copy.deepcopy(INPUT)
        next(r for r in data[1]['rows'] if r['negative_oracle'])['source_reported_verdict'] = 'SUCCESS'
        with self.assertRaisesRegex(ValueError, 'verdict'):
            p.compose(*data)

    def test_actual_companion_gate_propagates_transitively(self):
        data = copy.deepcopy(INPUT)
        rr = rows(data[1])
        rr['inactive_pairs_read_free']['pending_gates'].append('SYNTHETIC_LOCAL_GATE')
        report = p.compose(*data)
        for rid in ('activation_descending_rejected', 'activation_effectful_rejected', 'activation_unsupported_type_rejected'):
            self.assertIn(p.CG, rows(report)[rid]['pending_gates'])
        self.assertEqual(rows(report)['ordinary-bridge']['qualification'], 'QUALIFIED')

    def test_foreign_run_pin_and_missing_companion(self):
        for field, value in (('run', 43923266773), ('group', 'foreign'),
                             ('source_tool_request_pins', 'FOREIGN'), ('binary_after', 'UNKNOWN')):
            data = copy.deepcopy(INPUT)
            row = rows(data[1])['order_corruption_rejected']
            row['same_run_companion'][field] = value
            self.assertIn(p.CG, rows(p.compose(*data))[row['id']]['pending_gates'])
        data = copy.deepcopy(INPUT)
        spec = next(r for r in data[0]['rows'] if r['id'] == 'order_corruption_rejected')
        spec['companion'] = 'missing'
        self.assertIn(p.CG, rows(p.compose(*data))[spec['id']]['pending_gates'])

    def test_pending_member_keeps_union_pending(self):
        for union in REPORT['replacement_unions']:
            self.assertTrue(any(rows(REPORT)[rid]['qualification'] == 'PENDING' for rid in union['members']))
            self.assertEqual(union['qualification'], 'PENDING')
            self.assertEqual(union['domain_limit'], next(u for u in INPUT[1]['replacement_unions'] if u['id'] == union['id'])['domain_limit'])
        data = copy.deepcopy(INPUT)
        data[0]['replacement_unions'][0]['member_row_ids'][0] = 'ordinary-bridge'
        with self.assertRaisesRegex(ValueError, 'exact union'):
            p.compose(*data)

    def test_file_hash_and_committed_identity_checks(self):
        manifest = json.loads((p.HERE / 'INPUTS.json').read_bytes())
        rel = next(iter(manifest['files']))
        manifest['files'] = {rel: manifest['files'][rel]}
        manifest['files'][rel]['sha256'] = '0'*64
        with self.assertRaisesRegex(ValueError, 'input SHA'):
            p.verify_files(manifest)
        manifest['files'][rel]['sha256'] = p.sha((p.ROOT / rel).read_bytes())
        with patch.object(p.subprocess, 'check_output', return_value=b'foreign committed bytes'):
            with self.assertRaisesRegex(ValueError, 'uncommitted/foreign'):
                p.verify_files(manifest)


class DependencyGraph(unittest.TestCase):
    def graph(self, names, edges):
        rr = {name: {'group': 'g', 'source_reported_verdict': 'SUCCESS', 'binary_after': 'MATCH',
                     'local_pending_gates': []} for name in names}
        specs = {name: {} for name in names}
        for name, target in edges.items():
            specs[name]['companion'] = target
            rr[name]['same_run_companion'] = {'id': target, 'group': 'g', 'source_verdict': 'SUCCESS',
                'binary_after': 'MATCH', 'source_tool_request_pins': 'MATCH', 'run': 43923266772}
        return rr, specs

    def test_chain_is_order_independent(self):
        rr, ss = self.graph(['a', 'b', 'c'], {'a': 'b', 'b': 'c'})
        p.qualify(rr, ss, 43923266772)
        self.assertTrue(all(r['qualification'] == 'QUALIFIED' for r in rr.values()))
        rr['c']['local_pending_gates'] = ['OPEN']
        p.qualify(rr, ss, 43923266772)
        self.assertTrue(all(r['qualification'] == 'PENDING' for r in rr.values()))
        self.assertIn(p.CG, rr['a']['pending_gates'])

    def test_cycle_self_cycle_and_dependents_stay_pending(self):
        for edges in ({'a': 'b', 'b': 'a', 'c': 'b'}, {'a': 'a', 'b': 'a', 'c': 'b'}):
            rr, ss = self.graph(['a', 'b', 'c'], edges)
            p.qualify(rr, ss, 43923266772)
            self.assertTrue(all(r['qualification'] == 'PENDING' for r in rr.values()))
            self.assertTrue(all(p.CG in r['pending_gates'] for r in rr.values()))

    def test_missing_and_foreign_run_block_transitive_dependents(self):
        rr, ss = self.graph(['a', 'b'], {'a': 'b', 'b': 'missing'})
        p.qualify(rr, ss, 43923266772)
        self.assertTrue(all(r['qualification'] == 'PENDING' for r in rr.values()))
        rr, ss = self.graph(['a', 'b', 'c'], {'a': 'b', 'b': 'c'})
        rr['b']['same_run_companion']['run'] += 1
        p.qualify(rr, ss, 43923266772)
        self.assertEqual(rr['a']['qualification'], 'PENDING')
        self.assertEqual(rr['b']['qualification'], 'PENDING')
        self.assertEqual(rr['c']['qualification'], 'QUALIFIED')


if __name__ == '__main__':
    unittest.main()
