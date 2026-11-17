"""Adversarial U-only tests. No compiler, network, or raw evidence.

In-memory rehashing is deliberately test-only: it exercises semantic gates
beyond the production file/manifest SHA gate. No historical file is modified.
"""
import copy
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import replay as u


class ReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = u.load()
        cls.result = u.analyze(cls.base)
        cls.props = []
        for r in cls.result['records']:
            h = next(h for h in cls.base['groups'][r['group']]['properties']['harnesses']
                     if h['name'] == r['harness'])
            cls.props.append(next(p for p in h['properties'] if p['id'] == r['property_id']))

    def rejected(self, fn, reason=None):
        with self.assertRaises((ValueError, KeyError, TypeError, IndexError)) as error:
            fn()
        if reason:
            self.assertIn(reason, str(error.exception))

    @staticmethod
    def rehash_group(b, gid):
        for name in ('properties', 'export', 'receipt'):
            b['manifest']['group_canonical_sha256'][gid][name] = u.sha(u.encoded(b['groups'][gid][name]))

    @staticmethod
    def rehash_request(b):
        b['manifest']['request_canonical_sha256'] = u.sha(u.encoded(b['request']))

    def first(self, b):
        r = self.result['records'][0]
        g = b['groups'][r['group']]
        h = next(h for h in g['properties']['harnesses'] if h['name'] == r['harness'])
        p = next(p for p in h['properties'] if p['id'] == r['property_id'])
        return r['group'], g, h, p

    def test_exact_repeat_and_record_partition(self):
        data = u.encoded(self.result)
        self.assertEqual(data, (u.HERE/'U.json').read_bytes())
        self.assertEqual(data, u.encoded(u.analyze(self.base)))
        self.assertEqual(self.result['summary']['processed'], 187)
        self.assertEqual(self.result['summary']['UNKNOWN'], 0)
        original = self.base['accept']['unreachable_analysis']['records']
        expected = {(r['group'], r['row_id'], r['selector'], r['property_id']) for r in original
                    if r['decision'].startswith('UNKNOWN')}
        actual = {(r['group'], r['row_id'], r['harness'], r['property_id']) for r in self.result['records']}
        self.assertEqual(actual, expected)
        self.assertTrue(all(r['status'] == 'UNREACHABLE' for r in self.result['records']))
        self.assertEqual(len([r for r in original if r['decision'].startswith('ALLOWED_')]), 228)

    def test_every_record_rejects_metadata_mutations(self):
        # All 187 observations, including repeated same-ID different-harness
        # records, exercise exact function/site/class/description/status gates.
        mutations = {
            'status': 'SUCCESS', 'class': 'cover', 'description': 'sorting relation',
            'file': 'library/core/src/fmt/mod.rs', 'line': '999999',
            'location_display': 'library/core/src/lib.rs:1:1 in function foreign',
            'id': 'foreign.assertion.1', 'display_id': 'foreign.assertion.1',
        }
        for p in self.props:
            u.classify(p)
            for field, value in mutations.items():
                with self.subTest(property=p['id'], field=field):
                    q = dict(p); q[field] = value
                    self.rejected(lambda: u.classify(q))

    def test_coherent_foreign_function_and_site(self):
        p = copy.deepcopy(self.props[0])
        p['id'] = p['display_id'] = 'fmt::Arguments::foreign.assertion.1'
        p['location_display'] = p['location_display'].split(' in function ')[0] + ' in function fmt::Arguments::foreign'
        self.rejected(lambda: u.classify(p), 'unknown function/site')
        p = dict(self.props[0]); p['line'] = '821'
        p['location_display'] = p['location_display'].replace(':820:', ':821:')
        self.rejected(lambda: u.classify(p), 'unknown function/site')

    def test_original_namespace_and_structural_mutations_after_rehash(self):
        for mutation in ('missing_property', 'duplicate_property', 'foreign_property', 'extra_foreign_property',
                         'missing_harness', 'duplicate_harness', 'foreign_harness',
                         'missing_row', 'duplicate_row', 'foreign_row', 'swapped_row_harness',
                         'missing_group', 'foreign_group', 'duplicate_group_membership',
                         'foreign_request', 'foreign_receipt_group', 'producer_sha',
                         'source_snapshot', 'duplicate_bucket', 'missing_bucket',
                         'wrong_status', 'wrong_description', 'wrong_class', 'wrong_site',
                         'wrong_function', 'wrong_property_id'):
            with self.subTest(mutation=mutation):
                b = copy.deepcopy(self.base)
                gid, g, h, p = self.first(b)
                if mutation == 'missing_property': h['properties'].remove(p)
                elif mutation == 'duplicate_property': h['properties'].append(copy.deepcopy(p))
                elif mutation == 'foreign_property':
                    p['id'] = p['display_id'] = 'foreign.assertion.1'
                elif mutation == 'extra_foreign_property':
                    extra = copy.deepcopy(p);extra['id'] = extra['display_id'] = 'foreign.assertion.1'
                    h['properties'].append(extra)
                elif mutation == 'missing_harness': g['properties']['harnesses'].remove(h)
                elif mutation == 'duplicate_harness': g['properties']['harnesses'].append(copy.deepcopy(h))
                elif mutation == 'foreign_harness': h['name'] = 'foreign::harness'
                elif mutation == 'missing_row': b['request']['rows'].pop()
                elif mutation == 'duplicate_row': b['request']['rows'].append(copy.deepcopy(b['request']['rows'][0]))
                elif mutation == 'foreign_row': b['request']['rows'][0]['id'] = 'foreign'
                elif mutation == 'swapped_row_harness':
                    row = next(x for x in b['request']['rows'] if x['id'] == self.result['records'][0]['row_id'])
                    row['selector'] = 'foreign::harness'
                elif mutation == 'missing_group': b['groups'].pop(gid)
                elif mutation == 'foreign_group': b['groups']['foreign'] = copy.deepcopy(g)
                elif mutation == 'duplicate_group_membership': b['request']['execution_groups'][0]['row_ids'].append(b['request']['rows'][0]['id'])
                elif mutation == 'foreign_request': g['receipt']['request_sha256'] = '0'*64
                elif mutation == 'foreign_receipt_group': g['receipt']['group'] = 'foreign'
                elif mutation == 'producer_sha': g['export']['kani_commit'] = '0'*40
                elif mutation == 'source_snapshot': g['receipt']['source_after']['std_sha'] = '0'*40
                elif mutation in ('duplicate_bucket', 'missing_bucket'):
                    e = next(e for e in g['export']['harnesses'] if e['name'] == h['name'])
                    if mutation == 'duplicate_bucket': e['checks']['unreachable'].append(p['id'])
                    else: e['checks']['unreachable'].remove(p['id'])
                elif mutation == 'wrong_status': p['status'] = 'SUCCESS'
                elif mutation == 'wrong_description': p['description'] = 'attempt to add with overflow'
                elif mutation == 'wrong_class': p['class'] = 'cover'
                elif mutation == 'wrong_site':
                    p['line'] = '821'; p['location_display'] = p['location_display'].replace(':820:', ':821:')
                elif mutation == 'wrong_function': p['location_display'] += '_foreign'
                elif mutation == 'wrong_property_id':
                    # A plausible same-function ID still cannot replace the original.
                    p['id'] = p['display_id'] = p['id'].rsplit('.',1)[0] + '.999'
                if gid in b['groups']: self.rehash_group(b, gid)
                self.rehash_request(b)
                self.rejected(lambda: u.analyze(b))

    def test_file_sha_fail_closed(self):
        original = Path.read_bytes
        def altered(path):
            data = original(path)
            return data+b' ' if path == u.HERE/'../CI-REQUEST.json' else data
        with patch.object(Path, 'read_bytes', altered):
            self.rejected(u.load, 'input SHA:../CI-REQUEST.json')

    def test_manifest_sha_fail_closed(self):
        with patch.object(u, 'MANIFEST_SHA', '0'*64):
            self.rejected(u.load, 'input manifest SHA')

    def test_source_sha_fail_closed(self):
        b = copy.deepcopy(self.base)
        b['sources']['std',u.NUM] += '\n'
        self.rejected(lambda:u.analyze(b), 'source SHA')

    def test_exact_source_anchor_after_rehash(self):
        b = copy.deepcopy(self.base)
        b['sources']['std',u.FMT] = b['sources']['std',u.FMT].replace('s.len() << 1 | 1', 's.len() << 2 | 1')
        for entry in b['manifest']['sources']:
            if entry['repo'] == 'std' and entry['path'] == u.FMT:
                entry['sha256'] = u.sha(b['sources']['std',u.FMT].encode())
        self.rejected(lambda:u.analyze(b), 'exact source anchor:fmt')

    def test_six_families_broken_premises_without_digest_gate(self):
        # Each case changes the actual guard/operation, not the explanation.
        cases = [
            ('abs_diff', 'std', u.NUM, 'if self < other {', 'if self > other {'),
            ('abs_diff', 'std', u.NUM, 'other - self', 'self - other'),
            ('alignment', 'std', u.PTR, 'if !align.is_power_of_two() {', 'if align.is_power_of_two() {'),
            ('alignment', 'std', u.NUM, 'self.count_ones() == 1', 'self.count_ones() == 0'),
            ('alignment', 'std', u.PTR, 'align - 1', 'align - 2'),
            ('multiple', 'std', u.NUM, '0 => self == 0,', '1 => self == 0,'),
            ('multiple', 'std', u.NUM, '_ => self % rhs == 0,', '_ => self % 0 == 0,'),
            ('allocation', 'std', u.UB, 'if size == 0 {', 'if size != 0 {'),
            ('allocation', 'std', u.UB, 'isize::MAX as usize / size', 'isize::MAX as usize / 0'),
            ('fmt', 'std', u.FMT, 's.len() << 1 | 1', 's.len() << 64 | 1'),
            ('fmt', 'tool', u.CODEGEN, 'ce1.shl(ce2.clone())', 'ce2.shl(ce1.clone())'),
            ('fmt', 'tool', u.CODEGEN, 'ce2.cast_to(self.codegen_ty_stable(t1)).gt(max)', 'ce1.cast_to(self.codegen_ty_stable(t1)).gt(max)'),
            ('fmt', 'tool', u.CODEGEN, 'UintTy::Usize => Expr::int_constant(mm.pointer_width - 1', 'UintTy::Usize => Expr::int_constant(0'),
            ('active_post', 'std', u.MODEL, 'const CAP: usize = 32;', 'const CAP: usize = 0;'),
            ('active_post', 'std', u.MODEL, 'before.len > CAP', 'before.len > CAP + 1'),
            ('active_post', 'std', u.MODEL, 'before.len != values.len()', 'before.len == values.len()'),
            ('active_post', 'std', u.MODEL, 'let mut i = 1;', 'let mut i = 0;'),
            ('active_post', 'std', u.MODEL, 'while i < before.len {', 'while i <= before.len {'),
            ('active_post', 'std', u.MODEL, 'while j < before.len {', 'while j <= before.len {'),
            ('active_post', 'std', u.MODEL, 'values[i - 1]', 'values[i - 2]'),
            ('active_post', 'std', u.MODEL, 'old_count += 1;', 'old_count += 2;'),
            ('active_post', 'std', u.MODEL, 'let mut new_count: usize = 0;', 'let mut new_count: usize = 32;'),
            ('active_post', 'std', u.MODEL, 'j += 1;', 'j += 2;'),
            ('active_post', 'std', u.MODEL, 'values: [u8; CAP]', 'values: [u8; 1]'),
        ]
        self.assertEqual({x[0] for x in cases}, set(u.FAMILY_ANCHORS))
        for family,repo,path,old,new in cases:
            with self.subTest(family=family, mutation=old):
                sources = dict(self.base['sources'])
                self.assertIn(old, sources[repo,path])
                sources[repo,path] = sources[repo,path].replace(old,new)
                self.rejected(lambda:u.check_premises(family,sources))

    def test_all_rules_accept_only_pinned_width(self):
        for family in u.FAMILY_ANCHORS:
            u.check_premises(family,self.base['sources'])
            with self.subTest(family=family):
                self.rejected(lambda:u.check_premises(family,self.base['sources'],bits=1))

    def test_active_post_induction_and_origin_independence(self):
        facts = u.check_premises('active_post',self.base['sources'])['facts']
        self.assertEqual(facts['accepted_lengths'],[0,32])
        self.assertEqual(facts['counter_induction_transitions'],11968)
        self.assertFalse(facts['caller_or_origin_required'])
        # The rule consumes just property and source. Every actual origin/variant
        # shares its certificate; neither requested target nor ensures is read.
        records = [r for r in self.result['records'] if r['rule']=='active_post']
        self.assertEqual(len(records),54)
        self.assertGreater(len({r['harness'] for r in records}),1)
        self.assertTrue(all(r['premises']['facts']==facts for r in records))

    def test_fmt_unbounded_lhs(self):
        facts = u.check_premises('fmt',self.base['sources'])['facts']
        self.assertFalse(facts['length_bound_required'])
        self.assertFalse(facts['overflow_flag_value'])
        self.assertEqual(facts['rhs'],1)
        for lhs in (0,1,1<<63,(1<<64)-1):
            self.assertFalse(facts['rhs'] > facts['word_bits']-1)
            self.assertEqual((lhs << 1) & ((1<<64)-1), (2*lhs) % (1<<64))

    def test_output_tampering_is_rejected(self):
        original = Path.read_bytes
        # Preserve status and mutate a plausible-looking operation/result field.
        for field in ('operation','source_sha256','property_id','harness','row_id','group','status'):
            with self.subTest(field=field):
                result=copy.deepcopy(self.result);result['records'][0][field]='foreign'
                def altered(path):
                    return u.encoded(result) if path == u.HERE/'U.json' else original(path)
                with patch.object(Path,'read_bytes',altered),patch.object(sys,'argv',['replay.py']), contextlib.redirect_stderr(io.StringIO()) as err:
                    self.assertEqual(u.main(),1)
                    self.assertIn('U.json replay mismatch',err.getvalue())


if __name__=='__main__':
    unittest.main(verbosity=2)
