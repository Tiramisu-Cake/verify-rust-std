"""Small synthetic binding tests. No compiler, verifier or artifact reads."""
import copy
import json
from pathlib import Path
import subprocess
import unittest

import binding_v02 as b


class FreshBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        repo = '/root/verify-rust-std-ch8-profiles-w11'
        cls.sources = {p: subprocess.check_output(
            ['git', '-C', repo, 'show', b.SPEC['source_commit'] + ':' + p], text=True)
            for p in b.SPEC['source_files_sha256']}

    def fixture(self, rid='profile_merge4_contract_u8_len4'):
        mapping = b.SPEC['rows'][rid]
        self.row = {'id': rid, 'mode': mapping['mode'], 'profile': mapping['profile'],
                    'leaf_companion': mapping['leaf_companion'], **mapping['oracle']}
        fn = mapping['binding']['source_target']['fully_qualified'].rsplit('::', 1)[-1]
        instance = b.expected_instance(self.row, mapping)
        self.check = instance + '::{closure#7}'
        inner = self.check + '::{closure#11}'
        self.demangled = {'_R_synthetic': inner}
        self.h = {'contract': {'contracted_function_name': '_R_synthetic'}}
        file = b.DIR + b.SITES[fn][0]
        self.records = {}
        for kind, description in (
            ('single_top_level_call', 'Only a single top-level call to function _R_synthetic when checking contract _R_synthetic'),
            ('no_recursive_call', 'No recursive call to function _R_synthetic when checking contract _R_synthetic'),
            ('no_alloc_dealloc_in_requires', 'Check that requires do not allocate or deallocate memory'),
            ('no_alloc_dealloc_in_ensures', 'Check that ensures do not allocate or deallocate memory'),
        ):
            self.add(inner + '.' + kind + '.1', inner, 'SUCCESS', file, b.SITES[fn][2][0], description)
        for n, line in enumerate(b.SITES[fn][3], 1):
            self.add(b.relative(self.check) + '.assertion.' + str(n), b.relative(self.check),
                     'SUCCESS', file, line, b.clause(self.sources[file], line, 'ensures'))
        self.add('memcpy.assigns.1', 'memcpy', 'SUCCESS', '<builtin>', 1, 'write site')
        for c in mapping['covers']:
            self.add(c['id'], c['id'].rsplit('.cover.', 1)[0], 'SATISFIED',
                     c['source_file'], c['source_line'], 'synthetic cover')

    def add(self, pid, function, status, file, line, description):
        self.records[pid] = dict(id=pid, function=function, status=status,
                                 file=file, line=line, description=description)

    def run_bind(self, sources=None):
        return b.bind_fresh(self.row, self.h, self.records, self.demangled,
                            self.sources if sources is None else sources)

    def test_new_leaf_thin_targets_posts_and_cover_bind(self):
        self.fixture()
        result = self.run_bind()
        self.assertEqual(result['state'], 'BOUND')
        self.assertEqual(len(result['postconditions']), 2)
        self.assertEqual(len(result['covers']), 1)
        self.assertEqual(result['proof_credit'], 'NONE')
        line = b.SITES['merge4_profile'][2][0]
        clause = b.compact(b.clause(self.sources[b.DIR + '/verify/merge/profiles.rs'], line, 'modifies'))
        self.assertEqual(clause, 'dst,dst.wrapping_add(1),dst.wrapping_add(2),dst.wrapping_add(3)')

    def test_sort4_has_same_four_thin_targets(self):
        self.fixture('sort4_contract_bytes16_n4')
        self.assertEqual(self.run_bind()['state'], 'BOUND')
        line = b.SITES['sort4_profile'][2][0]
        self.assertNotIn('slice_from_raw_parts', b.clause(self.sources[b.DIR + '/verify/merge/profiles.rs'], line, 'modifies'))

    def test_closure_factory_instance_binds_and_function_item_does_not(self):
        self.fixture('swap_safety_u8_backing4')
        self.assertIn('reading_comparator<u8>::{closure#0}', self.demangled['_R_synthetic'])
        self.assertEqual(self.run_bind()['state'], 'BOUND')
        self.demangled['_R_synthetic'] = self.demangled['_R_synthetic'].replace(
            'reading_comparator<u8>::{closure#0}', 'arbitrary_less<u8>')
        with self.assertRaises(ValueError):
            self.run_bind()

    def test_changed_source_row_profile_and_leaf_fail_closed(self):
        self.fixture()
        bad = dict(self.sources)
        path = b.DIR + '/verify/merge/profiles.rs'
        bad[path] += '\n'
        with self.assertRaisesRegex(ValueError, 'SOURCE_HASH'):
            self.run_bind(bad)
        for key, value in [('mode', 'Original'), ('profile', 'LtU64'), ('leaf_companion', 'other')]:
            old = self.row[key]
            self.row[key] = value
            with self.assertRaisesRegex(ValueError, 'ROW_SPEC'):
                self.run_bind()
            self.row[key] = old

    def test_no_historical_oracle_or_foreign_wrapper(self):
        self.fixture()
        self.row['allowed_failure_descriptions'] = ['ignored uninit']
        with self.assertRaisesRegex(ValueError, 'ORACLE_SPEC'):
            self.run_bind()
        self.row['allowed_failure_descriptions'] = []
        for field in ['merge4_profile', '::LtU8']:
            saved = self.demangled['_R_synthetic']
            self.demangled['_R_synthetic'] = saved.replace(field, 'foreign')
            with self.assertRaises(ValueError):
                self.run_bind()
            self.demangled['_R_synthetic'] = saved

    def test_missing_failed_unknown_or_unreachable_post_rejected(self):
        self.fixture()
        key = b.relative(self.check) + '.assertion.1'
        for status in ['FAILURE', 'UNREACHABLE', 'UNKNOWN', None]:
            self.records[key]['status'] = status
            with self.assertRaises(ValueError):
                self.run_bind()
        self.records.pop(key)
        with self.assertRaises(ValueError):
            self.run_bind()

    def test_cover_wrong_site_function_or_unsat_rejected(self):
        self.fixture()
        c = b.SPEC['rows'][self.row['id']]['covers'][0]
        for key, value in [('line', 1), ('function', 'foreign'), ('status', 'UNSATISFIABLE')]:
            saved = self.records[c['id']][key]
            self.records[c['id']][key] = value
            with self.assertRaises(ValueError):
                self.run_bind()
            self.records[c['id']][key] = saved

    def test_consumer_requires_exact_new_stub_and_matching_leaf(self):
        self.fixture('profile_merge_consumer_u8_len4')
        mapping = b.SPEC['rows'][self.row['id']]
        instance = b.expected_instance(self.row, mapping)
        fn = b.relative(instance) + '::{closure#3}'
        file = b.DIR + '/verify/merge/profiles.rs'
        line = b.SITES['merge4_profile'][1][0]
        self.h = {'contract': None, 'attributes': {'verified_stubs': [b.PROFILES + '::merge4_profile']}}
        self.add(fn + '.assertion.1', fn, 'SUCCESS', file, line, b.clause(self.sources[file], line, 'requires'))
        result = self.run_bind()
        self.assertEqual(result['replacement_postconditions'], 'ASSUMED; matching accepted PFC leaf required separately')
        self.assertEqual(mapping['leaf_companion'], 'profile_merge4_contract_u8_len4')
        self.h['attributes']['verified_stubs'] = [b.PROFILES + '::merge_profile']
        with self.assertRaises(ValueError):
            self.run_bind()

    def test_frame_relocated_write_site_keeps_exact_failure(self):
        self.fixture(b.FRAME)
        pid = b.relative(b.ROOT) + '::verify::helper_contracts::' + b.FRAME + '::{closure#0}.assigns.1'
        file = b.DIR + '/verify/helper_contracts.rs'
        self.add(pid, pid.rsplit('.assigns.', 1)[0], 'FAILURE', file,
                 b.FRAME_WRITE_LINE, 'Check that *var_9 is assignable')
        self.h['checks'] = {'failure': [pid]}
        self.h['failed_properties'] = [self.records[pid]]
        self.assertEqual(self.run_bind()['negative_oracle']['state'], 'BOUND')
        self.records[pid]['line'] -= 1
        with self.assertRaises(ValueError):
            self.run_bind()

    def test_all_rows_fresh_and_original_oracles_retained(self):
        old = json.loads((b.BASE / 'accept-v2/SOURCE-MAP.json').read_bytes())
        manifest = json.loads(Path('/root/kani-ch8-prof-on-w15/ch8-prof-on-control/manifest.json').read_bytes())
        self.assertEqual(len(b.SPEC['rows']), 63)
        for row in manifest:
            new = b.SPEC['rows'][row['id']]
            self.assertEqual(new['oracle']['expected'], row['expected'])
            self.assertEqual(new['oracle']['allowed_failure_descriptions'], row['allowed_failure_descriptions'])
            self.assertEqual(new['historical_admissions_reused'], 0)
            self.assertEqual(new['state'], 'PREDECLARED_STATIC_NOT_RUN')
            self.assertEqual(len(new['covers']), len(old['rows'][row['id']]['covers']))


if __name__ == '__main__':
    unittest.main()
