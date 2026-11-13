#!/usr/bin/env python3
"""Tiny hand-authored cases test losses that would change the proxy conclusion."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
import analyze_offline as a

FIXTURES = json.loads(Path(__file__).with_name('synthetic-fixtures.json').read_text())


def run_case(name):
    rows, issues = a.parse(FIXTURES[name].encode())
    return rows, a.summarize(rows, issues, '', '')


class Synthetic(unittest.TestCase):
    def test_multiline_key_and_provenance(self):
        rows, c = run_case('multiline')
        self.assertEqual(c['status'], 'COMPLETE_TEXT_ONLY')
        self.assertEqual(c['aggregate']['candidate_occurrences'], 2)
        self.assertEqual(c['aggregate']['candidate_distinct_raw'], 2)
        self.assertEqual(c['aggregate']['candidate_distinct_canonical'], 1)
        self.assertEqual(c['aggregate']['C_constant_confirmed'], 0)
        self.assertTrue(any(e['occurrences'][0]['period']=='after_last_ASSERT' for e in c['reads']))
        raw = FIXTURES['multiline'].encode()
        for r in rows:
            span=raw[r['byte_offset']:r['byte_offset']+r['byte_length']].decode()
            self.assertTrue(span.startswith('('+r['printed_id']+') '))
            self.assertIn(r['term'], span)

    def test_unknown_kind_is_incomplete(self):
        _, c = run_case('unknown_kind')
        self.assertEqual(c['status'], 'INCOMPLETE')
        self.assertTrue(any('UNKNOWN_KIND' in s for s in c['issues']))

    def test_ambiguous_index_is_incomplete(self):
        _, c = run_case('ambiguous_index')
        self.assertEqual(c['status'], 'INCOMPLETE')
        self.assertTrue(any('ambiguous' in s for s in c['issues']))

    def test_duplicate_prefix(self):
        raw=FIXTURES['unknown_kind'].replace('(1) NEW_KIND(foo)\n','').encode()
        _, issues=a.parse(raw+raw)
        self.assertTrue(any('prefixes=2' in s for s in issues))

    def test_missing_definition_never_becomes_free(self):
        _, c = run_case('missing_definition')
        self.assertEqual(c['reads'][0]['definition_class'],'UNKNOWN_MISSING_DEFINITION')
        self.assertEqual(c['aggregate']['D_free_version_read_candidates'],0)
        self.assertEqual(c['status'],'INCOMPLETE')

    def test_cap_never_returns_complete_prefix(self):
        rows, issues=a.parse(FIXTURES['multiline'].encode(),cap=32)
        self.assertEqual(rows,[])
        self.assertEqual(issues,['INCOMPLETE byte cap'])
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'large';p.write_bytes(b'abcd')
            with self.assertRaisesRegex(ValueError,'INCOMPLETE file cap'):
                a.checked(p,dict(sha256=a.sha(b'abcd'),bytes=4),cap=3)

    def test_wrong_hash_and_wrong_pin(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'identity';p.write_bytes(b'{}')
            with self.assertRaisesRegex(ValueError,'STOP identity'):
                a.checked(p,dict(sha256='0'*64,bytes=2))
        pin=dict(source_tree='tree',ci_commit='ci',ci_tree='ct')
        identity=dict(source_sha=a.PINS['r1-skip'],source_tree='tree',ci_sha='ci',ci_tree='ct',
                      run_id='43314208878',run_attempt='1',job='r1-skip')
        a.validate_identity(identity,pin,'r1-skip')
        identity['source_sha']=a.PINS['r6b']
        with self.assertRaisesRegex(ValueError,'source_sha'):
            a.validate_identity(identity,pin,'r1-skip')

    def test_coverage_receipt(self):
        good=dict(collector_status='COMPLETE',stream_complete=True,original_rc=0,
                  executable_sha256='pin',streams=dict(stdout=dict(truncated=False,
                      dropped_bytes=0,emitted_bytes=4,total_bytes=4)))
        a.validate_receipt(good,b'data','pin')
        bad=copy.deepcopy(good);bad['streams']['stdout']['truncated']=True
        with self.assertRaisesRegex(ValueError,'INCOMPLETE'):
            a.validate_receipt(bad,b'data','pin')
        with self.assertRaisesRegex(ValueError,'STOP wrong receipt'):
            a.validate_receipt(good,b'data','wrong')

    def test_lhs_with_byte_and_read_are_distinct(self):
        _,c=run_case('separate_uses')
        self.assertEqual(c['aggregate']['candidate_occurrences'],1)
        counts={p['use_kind']:p['count'] for p in c['table_use_counts']}
        self.assertEqual(counts,dict(index_read=1,lhs_store=1))
        self.assertEqual(len(c['other_operators']),2)
        reads,issues=a.indexed('dynamic_object$12#2[arr#1[i]]')
        self.assertEqual(reads[0][1],'arr#1[i]');self.assertFalse(issues)

    def test_call_suffixes_casts_fields_and_versions_stay_distinct(self):
        indices=['(long int)PO(&x!0@1.field)','(long int)PO(&x!0@2.field)',
                 '(long int)PO(&x!0@1)','(unsigned int)PO(&x!0@1.field)']
        self.assertEqual(len({a.norm(x) for x in indices}),4)
        self.assertEqual(a.definition_class(None),'UNKNOWN_MISSING_DEFINITION')
        self.assertEqual(a.definition_class(dict(ignore=False,rhs='ARRAY_OF(NULL)',guard=None)),
                         'RETAINED_NULL_CONSTANT')
        self.assertNotEqual(a.definition_class(dict(ignore=False,rhs='ARRAY_OF(NULL)',guard='g')),
                            'RETAINED_NULL_CONSTANT')


if __name__=='__main__':
    unittest.main()
