import copy
import unittest

from reclassify_v4 import bind, expected_instance, DIR, PROFILES


class BindingTests(unittest.TestCase):
    def setUp(self):
        self.row = {'id': 'leaf', 'mode': 'PFC:swap_profile', 'profile': 'LtU8', 'expected': 'SUCCESS'}
        self.mapping = {'binding': {'source_target': {'fully_qualified': PROFILES + '::swap_profile'}},
                        'covers': []}
        self.old = {'binding': {'export_contract_symbol': '_R_example'},
                    'cover_mapping': {'post_target_ids': ['return.cover.1']}}
        self.h = {'contract': {'contracted_function_name': '_R_example'}}
        instance = expected_instance(self.row, self.mapping)
        self.check = instance + '::{closure#3}'
        self.inner = self.check + '::{closure#2}'
        self.demangled = {'_R_example': self.inner}
        file = DIR + '/verify/merge/profiles.rs'
        lines = [''] * 207
        lines[203] = '#[kani::requires(geometry(v))]'
        lines[204] = '#[kani::modifies(v)]'
        lines[205] = '#[kani::ensures(|_| transfer(v))]'
        lines[206] = '#[kani::ensures(|_| ordered(v))]'
        self.sources = {file: '\n'.join(lines)}
        self.records = {}
        for cls, desc in [
            ('single_top_level_call', 'Only a single top-level call to function _R_example when checking contract _R_example'),
            ('no_recursive_call', 'No recursive call to function _R_example when checking contract _R_example'),
            ('no_alloc_dealloc_in_requires', 'Check that requires do not allocate or deallocate memory'),
            ('no_alloc_dealloc_in_ensures', 'Check that ensures do not allocate or deallocate memory'),
        ]:
            self.add(self.inner, cls, 1, desc, file, 205)
        from reclassify_v4 import relative
        self.add(relative(self.check), 'assertion', 1, '|_| transfer(v)', file, 206)
        self.add(relative(self.check), 'assertion', 2, '|_| ordered(v)', file, 207)
        self.add('memcpy', 'assigns', 1, 'write site', '<builtin>', 1)

    def add(self, fn, cls, n, desc, file, line):
        pid = fn + '.' + cls + '.' + str(n)
        self.records[pid] = dict(id=pid, function=fn, status='SUCCESS', description=desc, file=file, line=line)

    def run_bind(self):
        return bind(self.row, self.old, self.mapping, self.h, self.records, self.demangled, self.sources)

    def test_valid_binding_and_preconditions_assumed(self):
        b = self.run_bind()
        self.assertEqual(b['state'], 'BOUND')
        self.assertEqual(b['preconditions']['assertion_ids'], [])
        self.assertEqual(len(b['postconditions']), 2)
        self.assertEqual(b['assigns']['properties'][0]['function'], 'memcpy')

    def test_foreign_full_target_or_profile_rejected(self):
        for value in [self.inner.replace('::LtU8', '::LtU64'), self.inner.replace('::profiles::', '::foreign::')]:
            with self.subTest(value=value):
                self.demangled['_R_example'] = value
                with self.assertRaises(ValueError):
                    self.run_bind()

    def test_metadata_symbol_changed(self):
        self.h['contract']['contracted_function_name'] = '_R_foreign'
        with self.assertRaises(ValueError):
            self.run_bind()

    def test_foreign_contract_in_single_call_description(self):
        self.records[self.inner + '.single_top_level_call.1']['description'] += '_foreign'
        with self.assertRaises(ValueError):
            self.run_bind()

    def test_missing_check_unknown(self):
        del self.records[self.inner + '.no_recursive_call.1']
        with self.assertRaises(KeyError):
            self.run_bind()

    def test_failed_or_unreachable_post_blocks(self):
        from reclassify_v4 import relative
        for status in ['FAILURE', 'UNREACHABLE', None]:
            self.records[relative(self.check) + '.assertion.1']['status'] = status
            with self.subTest(status=status), self.assertRaises(ValueError):
                self.run_bind()

    def test_wrong_post_site_or_text_rejected(self):
        from reclassify_v4 import relative
        p = self.records[relative(self.check) + '.assertion.1']
        saved = copy.deepcopy(p)
        for key, value in [('line', 207), ('file', 'other.rs'), ('description', 'other post'), ('function', self.check)]:
            p.update(saved)
            p[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.run_bind()

    def test_no_assigns_inventory_rejected(self):
        del self.records['memcpy.assigns.1']
        with self.assertRaises(ValueError):
            self.run_bind()

    def test_foreign_assigns_failure_rejected(self):
        self.records['memcpy.assigns.1']['status'] = 'FAILURE'
        with self.assertRaises(ValueError):
            self.run_bind()

    def test_no_post_target_cover_rejected(self):
        self.old['cover_mapping']['post_target_ids'] = []
        with self.assertRaises(ValueError):
            self.run_bind()

    def test_assertion_ordinals_may_include_arithmetic(self):
        from reclassify_v4 import relative
        fn = relative(self.check)
        first = self.records.pop(fn + '.assertion.1')
        second = self.records.pop(fn + '.assertion.2')
        for n, p in [(2, first), (3, second)]:
            p['id'] = fn + '.assertion.' + str(n)
            self.records[p['id']] = p
        self.add(fn, 'assertion', 1, 'attempt to subtract with overflow', first['file'], 205)
        self.assertTrue(self.run_bind()['postconditions'][0]['id'].endswith('.assertion.2'))

    def test_duplicate_clause_site_rejected(self):
        from reclassify_v4 import relative
        p = copy.deepcopy(self.records[relative(self.check) + '.assertion.1'])
        p['id'] = relative(self.check) + '.assertion.99'
        self.records[p['id']] = p
        with self.assertRaises(ValueError):
            self.run_bind()

    def replace_fixture(self):
        from reclassify_v4 import relative
        self.row['mode'] = 'Replace:profile_wrapper'
        self.h = {'contract': None, 'attributes': {'verified_stubs': [PROFILES + '::swap_profile']}}
        self.replace = relative(expected_instance(self.row, self.mapping)) + '::{closure#2}'
        self.records = {}
        self.add(self.replace, 'assertion', 2, 'geometry(v)', DIR + '/verify/merge/profiles.rs', 204)

    def test_replace_asserted_precondition(self):
        self.replace_fixture()
        b = self.run_bind()
        self.assertEqual(b['replace_wrapper_function'], self.replace)
        self.assertEqual(b['preconditions']['properties'][0]['id'], self.replace + '.assertion.2')
        self.assertEqual(b['postconditions'], [])

    def test_replace_foreign_stub_or_contract_rejected(self):
        self.replace_fixture()
        self.h['attributes']['verified_stubs'] = ['other::swap_profile']
        with self.assertRaises(ValueError):
            self.run_bind()
        self.h['contract'] = {'contracted_function_name': '_R_example'}
        with self.assertRaises(ValueError):
            self.run_bind()

    def test_replace_missing_or_wrong_precondition_rejected(self):
        self.replace_fixture()
        self.records[self.replace + '.assertion.2']['description'] = 'foreign geometry'
        with self.assertRaises(ValueError):
            self.run_bind()

    def test_cover_function_and_site_must_match(self):
        self.mapping['covers'] = [{'id': 'after.cover.1', 'source_file': DIR + '/verify/merge/profiles.rs',
                                  'source_line': 200, 'source_expression': 'kani::cover(true)', 'role': 'POST_TARGET'}]
        self.add('after', 'cover', 1, 'after return', DIR + '/verify/merge/profiles.rs', 200)
        self.records['after.cover.1']['status'] = 'SATISFIED'
        self.assertEqual(len(self.run_bind()['covers']), 1)
        for key, value in [('function', 'before'), ('line', 199), ('status', 'UNREACHABLE')]:
            p = self.records['after.cover.1']
            saved = p[key]
            p[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.run_bind()
            p[key] = saved

    def frame_fixture(self):
        from reclassify_v4 import FRAME, ROOT, relative
        self.row = {'id': FRAME, 'mode': 'PFC:swap_if_less',
                    'profile': 'effectful captured-counter closure', 'expected': 'DETECTED'}
        self.mapping = {'binding': {'source_target': {'fully_qualified': ROOT + '::swap_if_less'}}, 'covers': []}
        instance = expected_instance(self.row, self.mapping)
        self.inner = instance + '::{closure#2}::{closure#2}'
        self.demangled['_R_example'] = self.inner
        self.records = {}
        file = DIR + '.rs'
        for cls, desc in [
            ('single_top_level_call', 'Only a single top-level call to function _R_example when checking contract _R_example'),
            ('no_recursive_call', 'No recursive call to function _R_example when checking contract _R_example'),
            ('no_alloc_dealloc_in_requires', 'Check that requires do not allocate or deallocate memory'),
            ('no_alloc_dealloc_in_ensures', 'Check that ensures do not allocate or deallocate memory'),
        ]:
            self.add(self.inner, cls, 1, desc, file, 413)
        lines = [''] * 413
        lines[412] = '#[cfg_attr(kani, crate::kani::modifies(v_base.wrapping_add(a_pos), v_base.wrapping_add(b_pos)))]'
        helper_lines = [''] * 276
        helper_lines[275] = '        comparisons = comparisons.wrapping_add(1);'
        self.sources = {file: '\n'.join(lines), DIR + '/verify/helper_contracts.rs': '\n'.join(helper_lines)}
        function = relative(ROOT) + '::verify::helper_contracts::' + FRAME + '::{closure#0}'
        self.add(function, 'assigns', 1, 'Check that *var_9 is assignable', DIR + '/verify/helper_contracts.rs', 276)
        self.failure = function + '.assigns.1'
        self.records[self.failure]['status'] = 'FAILURE'
        self.h['checks'] = {'failure': [self.failure]}
        self.h['failed_properties'] = [self.records[self.failure]]

    def test_frame_failure_source_criterion(self):
        self.frame_fixture()
        self.assertEqual(self.run_bind()['negative_oracle']['state'], 'BOUND')

    def test_frame_wrong_site_or_description_rejected(self):
        self.frame_fixture()
        for key, value in [('line', 277), ('description', 'unrelated failure'), ('status', 'SUCCESS')]:
            p = self.records[self.failure]
            saved = p[key]
            p[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.run_bind()
            p[key] = saved

    def test_frame_additional_failure_rejected(self):
        self.frame_fixture()
        self.h['checks']['failure'].append('other.assertion.1')
        with self.assertRaises(ValueError):
            self.run_bind()

    def test_frame_changed_write_set_rejected(self):
        self.frame_fixture()
        self.sources[DIR + '.rs'] += 'allow_counter'
        with self.assertRaises(ValueError):
            self.run_bind()


if __name__ == '__main__':
    unittest.main()
