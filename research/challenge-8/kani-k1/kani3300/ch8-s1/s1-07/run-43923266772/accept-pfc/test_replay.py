#!/usr/bin/env python3
"""Synthetic relation mutations, including tests below the outer hash gates.

All mutations are in memory. No source/evidence files are edited. Contract
mutations call the binding checker directly, bypassing inventory/digest checks,
so a pass proves semantic rejection rather than just a changed file hash.
"""
import copy
import json
import sys
import unittest

sys.dont_write_bytecode = True
import replay as p

BUNDLE = None
REPORT = None


def setUpModule():
    global BUNDLE, REPORT
    BUNDLE = p.load_bundle()
    REPORT = p.analyze(BUNDLE)


def row_input(b, rid):
    row = next(r for r in b['request']['rows'] if r['id'] == rid)
    group = next(g for g in b['request']['execution_groups'] if rid in g['row_ids'])
    g = b['groups'][group['id']]
    h = next(h for h in g['export.json']['harnesses'] if h['name'] == row['selector'])
    props = next(h['properties'] for h in g['properties.json']['harnesses'] if h['name'] == row['selector'])
    return row, group, h, props, g


def binding(rid):
    return next(r for r in REPORT['bindings'] if r['id'] == rid)


def mutate_native(meta, row, operation):
    mr = next(r for r in meta['rows'] if r['row_id'] == row['id'])
    ref = mr['native_harness_records'][0]
    entry = next(e for e in meta['native_metadata'] if e['path'] == ref['metadata_path'])
    doc = json.loads(entry['text'])
    record = p.helpers()[1]._pointer(doc, ref['pointer'])
    operation(doc, record)
    entry['text'] = json.dumps(doc)
    # Deliberately repair the container digest to exercise the relation checks.
    entry['bytes'] = len(entry['text'].encode())
    entry['sha256'] = p.digest(entry['text'].encode())


class Positive(unittest.TestCase):
    def test_all_exact_22_and_component_scope(self):
        self.assertEqual(REPORT['totals'], dict(chains=22, bound=22, pending=0))
        self.assertTrue(REPORT['component_only'])
        self.assertFalse(REPORT['admission_root_recomputed'])
        self.assertEqual(REPORT['independent_proof_credit'], 'NONE')
        self.assertEqual(REPORT['B1_credit'], 'NONE')
        self.assertEqual(REPORT['B2_credit'], 'NONE')
        self.assertEqual(len([r for r in REPORT['bindings'] if r['negative_oracle']]), 2)

    def test_repeat_replay_is_byte_identical(self):
        self.assertEqual(p.encoded(p.analyze(BUNDLE)), p.encoded(REPORT))
        self.assertEqual((p.HERE / 'PFC.json').read_bytes(), p.encoded(REPORT))

    def test_requires_are_assumed_ensures_asserted_and_frame_enforced(self):
        for r in REPORT['bindings']:
            with self.subTest(row=r['id']):
                c = r['contract']
                self.assertTrue(c['requires'])
                self.assertTrue(all(q['assertion_ids'] == [] and q['semantics'] == 'ASSUMED_BY_PFC_CHECK; NOT_ASSERTED' for q in c['requires']))
                self.assertEqual(len(c['ensures']), 1)
                self.assertEqual(c['ensures'][0]['property']['status'], 'FAILURE' if r['negative_oracle'] else 'SUCCESS')
                self.assertEqual(c['modifies']['semantics'], 'ENFORCED_BY_SOLE_DFCC_CONTRACT')
                self.assertTrue(all(x['status'] == 'SUCCESS' for x in c['modifies']['write_site_properties']))

    def test_six_distinct_selected_impls(self):
        impls = {r['selected_impl']['header'] for r in REPORT['bindings']}
        self.assertEqual(len(impls), 6)

    def test_closure_numbers_do_not_assign_roles(self):
        # Renumber both nested closures coherently in an isolated semantic
        # fixture. Role comes from producer+symbol; no hard-coded #2/#1 gate.
        b = copy.deepcopy(BUNDLE)
        row, _, h, props, _ = row_input(b, 'stable_default_cell')
        r = binding(row['id'])
        raw = h['contract']['contracted_function_name']
        b['dictionary'][raw] = b['dictionary'][raw].replace('{closure#2}', '{closure#17}').replace('{closure#1}', '{closure#9}')
        for prop in props:
            for field in ['id', 'location_display']:
                prop[field] = prop[field].replace('{closure#2}', '{closure#17}').replace('{closure#1}', '{closure#9}')
        c = p.contract_properties(b, row, h, props, r['selected_impl'], r['type'], r['trait'])
        self.assertTrue(c['check_wrapper'].endswith('::{closure#17}'))
        self.assertTrue(c['decoded_modifies_wrapper'].endswith('::{closure#17}::{closure#9}'))

    def test_only_local_core_prefix_is_normalized(self):
        self.assertEqual(p.fullpath('<core::cell::Cell<u8> as core::slice::A>::f::<core::slice::B>'), '<cell::Cell<u8> as slice::A>::f::<slice::B>')
        self.assertNotEqual(p.fullpath('other::core::slice::A'), p.fullpath('core::slice::A'))
        self.assertNotEqual(p.fullpath('wrong::path::f::<u8>'), p.fullpath('right::path::f::<u8>'))

    def test_variants_effective_source_and_legal_companions(self):
        for rid, line in [('activation-default', 41), ('activation-override', 63)]:
            r = binding(rid)
            effective, patch = p.effective_source(BUNDLE, rid)
            self.assertNotEqual(effective, BUNDLE['sources'][p.SMALL])
            self.assertEqual(p.digest(effective.encode()), r['source']['effective_target_sha256'])
            self.assertIn(patch['marker'], effective.splitlines()[line-1])
            companion = binding(r['negative_oracle']['legal_companion_binding'])
            self.assertEqual(r['contract']['target_instance'], companion['contract']['target_instance'])
            self.assertEqual(companion['contract']['ensures'][0]['property']['status'], 'SUCCESS')
            self.assertEqual(r['contract']['ensures'][0]['property']['status'], 'FAILURE')

    def test_patch_application_never_touches_worktree(self):
        source = p.git_bytes(p.STD, p.SOURCE, p.SMALL)
        for variant in BUNDLE['request']['variants']:
            p.effective_source(BUNDLE, variant)
        self.assertEqual(p.git_bytes(p.STD, p.SOURCE, p.SMALL), source)


class ContractMutations(unittest.TestCase):
    def reject(self, rid, mutation, reason):
        row, _, h0, ps0, _ = row_input(BUNDLE, rid)
        b = {'dictionary': dict(BUNDLE['dictionary'])}
        h, props, impl = copy.deepcopy((h0, ps0, binding(rid)['selected_impl']))
        mutation(b, h, props, impl)
        with self.assertRaisesRegex(ValueError, reason):
            p.contract_properties(b, row, h, props, impl, binding(rid)['type'], binding(rid)['trait'])


def diag(props, cls='single_top_level_call'):
    return next(x for x in props if x['class'] == cls)


def ensure(props):
    return next(x for x in props if x['class'] == 'assertion' and ('sorting_model::post' in x['description'] or 'S1_ATTACHMENT' in x['description']))


def map_symbol(b, h, fn):
    raw = h['contract']['contracted_function_name']
    b['dictionary'][raw] = fn(b['dictionary'][raw])


CONTRACT_MUTATIONS = {
    'raw_symbol': (lambda b,h,ps,i: h['contract'].__setitem__('contracted_function_name', h['contract']['contracted_function_name'] + '_bad'), 'raw symbol dictionary'),
    'decoded_full_module_same_suffix': (lambda b,h,ps,i: map_symbol(b,h,lambda s:s.replace('core::slice::sort::shared', 'core::wrong::sort::shared')), 'decoded full target'),
    'decoded_trait': (lambda b,h,ps,i: map_symbol(b,h,lambda s:s.replace('SmallSort', 'WrongSort')), 'decoded full target'),
    'decoded_type': (lambda b,h,ps,i: map_symbol(b,h,lambda s:s.replace('u8', 'u16').replace('NonCopyByte', 'OtherByte')), 'decoded full target'),
    'decoded_comparator': (lambda b,h,ps,i: map_symbol(b,h,lambda s:s.replace('KeyLess', 'OtherLess')), 'decoded full target'),
    'diagnostic_raw_once': (lambda b,h,ps,i: diag(ps).__setitem__('description', diag(ps)['description'].replace(h['contract']['contracted_function_name'], 'other', 1)), 'diagnostic raw symbol/status'),
    'diagnostic_status': (lambda b,h,ps,i: diag(ps).__setitem__('status', 'FAILURE'), 'diagnostic raw symbol/status'),
    'diagnostic_full_stem_same_suffix': (lambda b,h,ps,i: diag(ps).__setitem__('id', diag(ps)['id'].replace('slice::sort', 'wrong::sort')), 'property full function'),
    'diagnostic_location_stem': (lambda b,h,ps,i: diag(ps).__setitem__('location_display', diag(ps)['location_display'].replace('slice::sort', 'wrong::sort')), 'property full function'),
    'diagnostic_source_site': (lambda b,h,ps,i: diag(ps).__setitem__('line', '999'), 'contract property source site'),
    'diagnostic_missing': (lambda b,h,ps,i: ps.remove(diag(ps)), 'one exact diagnostic'),
    'diagnostic_duplicate': (lambda b,h,ps,i: ps.append(copy.deepcopy(diag(ps))), 'one exact diagnostic'),
    'recursive_diagnostic_missing': (lambda b,h,ps,i: ps.remove(diag(ps,'no_recursive_call')), 'one exact diagnostic'),
    'ensures_missing': (lambda b,h,ps,i: ps.remove(ensure(ps)), 'exact check ensures'),
    'ensures_duplicate': (lambda b,h,ps,i: ps.append(copy.deepcopy(ensure(ps))), 'exact check ensures'),
    'ensures_clause': (lambda b,h,ps,i: ensure(ps).__setitem__('description', ensure(ps)['description'].replace('||', '&&')), 'exact check ensures'),
    'ensures_site': (lambda b,h,ps,i: ensure(ps).__setitem__('line','999'), 'exact check ensures'),
    'ensures_status': (lambda b,h,ps,i: ensure(ps).__setitem__('status', 'UNREACHABLE'), 'ensures clause status'),
    'ensures_caller_substitution': (lambda b,h,ps,i: ensure(ps).__setitem__('id', 'caller_same_terminal_suffix.assertion.1'), 'exact check ensures'),
    'frame_failure': (lambda b,h,ps,i: next(x for x in ps if x['class']=='assigns').__setitem__('status','FAILURE'), 'enforced frame statuses'),
    'frame_missing': (lambda b,h,ps,i: ps.__setitem__(slice(None), [x for x in ps if x['class'] not in {'assigns','frees'}]), 'enforced frame statuses'),
    'allocation_status': (lambda b,h,ps,i: next(x for x in ps if x['class']=='no_alloc_dealloc_in_requires').__setitem__('status','UNREACHABLE'), 'clause allocation status'),
}


# Run every semantic mutation for a positive row, both activation variants, and
# the non-Copy specialization. Separate methods make counts/results explicit.
for rid in ['stable_default_cell', 'stable_freeze_u8_n2', 'freeze_copy_u8_n2',
            'freeze_default_noncopy_n2', 'unstable_default_cell', 'unstable_freeze_u8_n2',
            'activation-default', 'activation-override']:
    for name, (mutation, reason) in CONTRACT_MUTATIONS.items():
        def case(self, rid=rid, mutation=mutation, reason=reason):
            self.reject(rid, mutation, reason)
        setattr(ContractMutations, 'test_' + rid.replace('-', '_') + '_' + name, case)


class RelationMutations(unittest.TestCase):
    def setUp(self):
        self.b = copy.deepcopy(BUNDLE)
        self.row, self.group, self.h, self.props, self.g = row_input(self.b, 'stable_default_cell')
        self.source = self.b['request']['source_bindings'][self.row['id']]
        self.meta = self.g['binding-metadata.json']

    def reject_row(self, reason):
        with self.assertRaisesRegex((ValueError, KeyError), reason):
            p.analyze_row(self.b, self.row, self.group)

    def test_request_group_mismatch(self):
        self.group['row_ids'].remove(self.row['id'])
        self.reject_row('row/group/variant')

    def test_request_harness_mismatch(self):
        self.row['selector'] += '_other'
        self.reject_row('argv/unwind|exact export selection')

    def test_request_target_mismatch(self):
        self.row['target'] = '<u8 as StableSmallSortTypeImpl>::small_sort'
        self.reject_row('request row target')

    def test_request_type_mismatch(self):
        self.row['type'] = 'u8'
        self.reject_row('request type')

    def test_export_crate_mismatch(self):
        self.h['crate_name'] = 'other'
        self.reject_row('source harness/crate/mode')

    def test_export_trait_mismatch(self):
        self.h['attributes']['kind']['ProofForContract']['target_fn'] = self.h['attributes']['kind']['ProofForContract']['target_fn'].replace('StableSmallSortTypeImpl','UnstableSmallSortTypeImpl')
        self.reject_row('PFC source/export target')

    def test_source_site_mismatch(self):
        self.source['locations'][0]['line'] += 1
        self.meta['source_bindings'][self.row['id']] = self.source
        self.reject_row('harness source site')

    def test_source_sha_mismatch(self):
        self.source['sha256'] = '0'*64
        self.meta['source_bindings'][self.row['id']] = self.source
        self.reject_row('harness source SHA')

    def test_group_request_mismatch(self):
        self.meta['request_sha256'] = '0'*64
        self.reject_row('group request identity')

    def test_cfg_mismatch_even_with_rehashed_configuration(self):
        for obj in [self.meta, self.g['receipt.json']]:
            obj['effective_cfg'] = '--cfg=kani_smallsort_sorting'
        self.meta['configuration_sha256'] = p.digest(json.dumps({'flags':self.b['request']['flags'], 'cfg':self.meta['effective_cfg'], 'argv':self.meta['argv']},sort_keys=True).encode())
        self.reject_row('effective cfg')

    def test_native_pointer_mismatch(self):
        next(r for r in self.meta['rows'] if r['row_id']==self.row['id'])['native_harness_records'][0]['pointer'] = '/proof_harnesses/9999'
        self.reject_row('native exact harness')

    def test_native_reference_missing(self):
        next(r for r in self.meta['rows'] if r['row_id']==self.row['id'])['native_harness_records'] = []
        self.reject_row('native ref uniqueness')

    def test_native_reference_duplicate(self):
        refs = next(r for r in self.meta['rows'] if r['row_id']==self.row['id'])['native_harness_records']
        refs.append(copy.deepcopy(refs[0]))
        self.reject_row('native ref uniqueness')

    def test_native_metadata_hash_mismatch(self):
        ref = next(r for r in self.meta['rows'] if r['row_id']==self.row['id'])['native_harness_records'][0]
        next(e for e in self.meta['native_metadata'] if e['path']==ref['metadata_path'])['sha256'] = '0'*64
        self.reject_row('native embedded content integrity')

    def test_native_manual_definition_wrong_trait(self):
        def mutate(doc, rec):
            target = next(d for d in doc['contracted_functions'] if self.row['selector'] in d['harnesses'])
            target['function'] = target['function'].replace('StableSmallSortTypeImpl','UnstableSmallSortTypeImpl')
        mutate_native(self.meta, self.row, mutate)
        self.reject_row('native target definition type/trait/file')

    def test_native_manual_definition_missing(self):
        mutate_native(self.meta,self.row,lambda d,r:d.__setitem__('contracted_functions',[t for t in d['contracted_functions'] if self.row['selector'] not in t['harnesses']]))
        self.reject_row('manual target-definition link')

    def test_native_manual_definition_duplicate(self):
        def mutate(doc, rec):
            doc['contracted_functions'].append(copy.deepcopy(next(d for d in doc['contracted_functions'] if self.row['selector'] in d['harnesses'])))
        mutate_native(self.meta,self.row,mutate)
        self.reject_row('manual target-definition link')

    def test_native_raw_symbol_mismatch_with_valid_container_digest(self):
        mutate_native(self.meta,self.row,lambda d,r:r['contract'].__setitem__('contracted_function_name','different_raw_symbol'))
        self.reject_row('native/export attrs and raw symbol')

    def test_property_duplicate(self):
        self.props.append(copy.deepcopy(self.props[0]))
        self.reject_row('missing/duplicate ID')

    def test_property_missing(self):
        self.props.pop()
        self.reject_row('property total')

    def test_property_wrong_status(self):
        self.props[0]['status'] = 'ERROR'
        self.reject_row('unknown|mismatch|count')

    def test_not_run_export(self):
        self.g['export.json']['run_state'] = 'NOT_RUN'
        self.reject_row('complete export')

    def test_partial_export(self):
        self.g['export.json']['harnesses'].pop()
        self.reject_row('complete exact group harness inventories')

    def test_timeout(self):
        self.meta['execution']['timed_out'] = True
        self.g['receipt.json']['execution']['timed_out'] = True
        self.reject_row('complete execution')

    def test_binary_drift(self):
        self.meta['binaries_after']['binaries']['cbmc']['sha256'] = '0'*64
        self.g['receipt.json']['tool_fingerprints_after']['binaries']['cbmc']['sha256'] = '0'*64
        self.reject_row('same-run binary snapshots')

    def test_source_mutation_not_accepted_by_hash(self):
        self.b['sources'][p.SMALL] = self.b['sources'][p.SMALL].replace('kani::modifies(v)', 'kani::modifies(scratch)', 1)
        with self.assertRaisesRegex(ValueError,'source SHA'):
            p.source_identity(self.b)

    def test_source_impl_not_inferred_by_terminal_method_name(self):
        text = self.b['sources'][p.SMALL].replace('impl<T> StableSmallSortTypeImpl for T {','impl<T: WrongBound> StableSmallSortTypeImpl for T {',1)
        with self.assertRaisesRegex(ValueError,'unique applicable impl header'):
            p.selected_impl(self.b,'Cell<u8>','StableSmallSortTypeImpl',text)

    def test_unknown_type_pending_instead_of_silent_binding(self):
        with self.assertRaisesRegex(ValueError,'supported type/trait'):
            p.selected_impl(self.b,'UnknownType','StableSmallSortTypeImpl',self.b['sources'][p.SMALL])

    def test_producer_edge_mutation(self):
        self.b['producer']['check_semantics']['lines'][0] = 'wrong producer semantics'
        with self.assertRaisesRegex(ValueError,'producer edge'):
            p.source_identity(self.b)

    def test_pending_keeps_specific_missing_edge(self):
        self.h['crate_name'] = 'other'
        result = p.analyze(self.b)
        r = next(r for r in result['bindings'] if r['id']==self.row['id'])
        self.assertEqual(r['status'],'PENDING')
        self.assertIn('source harness/crate/mode',r['gaps'][0])
        self.assertFalse(any('compiler-resolved' in g for r in result['bindings'] for g in r['gaps']))


class VariantMutations(unittest.TestCase):
    def setUp(self):
        self.b = copy.deepcopy(BUNDLE)
        self.row, self.group, self.h, self.props, self.g = row_input(self.b,'activation-override')
        self.r = binding(self.row['id'])
        self.effective, self.patch = p.effective_source(self.b,self.row['variant'])

    def reject_oracle(self, reason):
        with self.assertRaisesRegex(ValueError,reason):
            p.oracle(self.row,self.h,self.props,self.r['contract'],self.effective,self.patch)

    def test_patch_sha(self):
        self.b['patches']['activation-override'] += '\n'
        with self.assertRaisesRegex(ValueError,'variant patch SHA'):
            p.effective_source(self.b,'activation-override')

    def test_variant_patch_swap(self):
        self.b['patches']['activation-override'] = self.b['patches']['activation-default']
        with self.assertRaisesRegex(ValueError,'variant patch SHA'):
            p.effective_source(self.b,'activation-override')

    def test_wrong_effective_source_hash(self):
        self.b['request']['variants']['activation-override']['changed_file_sha256'][p.SMALL] = '0'*64
        with self.assertRaisesRegex(ValueError,'effective variant source SHA'):
            p.effective_source(self.b,'activation-override')

    def test_patch_context_mismatch_even_with_rehashed_patch(self):
        patch = self.b['patches']['activation-override'].replace('scratch.len() >= v.len() + 16','scratch.len() >= v.len() + 17')
        self.b['patches']['activation-override'] = patch
        self.b['request']['variants']['activation-override']['sha256'] = p.digest(patch.encode())
        with self.assertRaisesRegex(ValueError,'patch exact old context'):
            p.effective_source(self.b,'activation-override')

    def test_production_source_for_mutant(self):
        self.effective = self.b['sources'][p.SMALL]
        self.reject_oracle('oracle effective source')

    def test_oracle_id_mismatch(self):
        self.row['oracle']['property_id'] += '_other'
        self.reject_oracle('predeclared exact sole-failure oracle')

    def test_oracle_clause_mismatch(self):
        self.row['oracle']['description'] = 'false'
        self.reject_oracle('predeclared exact sole-failure oracle')

    def test_oracle_site_mismatch(self):
        self.row['oracle']['line'] += 1
        self.reject_oracle('predeclared exact sole-failure oracle')

    def test_oracle_status_mismatch(self):
        self.row['oracle']['status'] = 'SUCCESS'
        self.reject_oracle('predeclared oracle selector/status')

    def test_oracle_selector_mismatch(self):
        self.row['oracle']['selector'] += '_wrong'
        self.reject_oracle('predeclared oracle selector/status')

    def test_second_failure(self):
        self.props.append(dict(self.props[0],id='extra.assertion.1',status='FAILURE'))
        self.reject_oracle('activation sole failure')

    def test_marker_mismatch(self):
        self.patch['marker'] = 'DIFFERENT_ATTACHMENT'
        self.reject_oracle('oracle variant marker')

    def test_variant_changed_to_production(self):
        self.row['variant'] = 'production'
        with self.assertRaisesRegex(ValueError,'row/group/variant'):
            p.analyze_row(self.b,self.row,self.group)

    def test_companion_wrong_instance(self):
        self.row['companion'] = 'stable_default_activation-legal'
        result = p.analyze(self.b)
        bad = next(r for r in result['bindings'] if r['id']==self.row['id'])
        self.assertEqual(bad['status'],'PENDING')
        self.assertEqual(bad['gaps'],['legal companion same target instance'])


if __name__ == '__main__':
    unittest.main()
