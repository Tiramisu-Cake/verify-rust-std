"""Narrow synthetic mutations at the retry selection/origin/timeout/partial boundary."""
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest import mock
sys.dont_write_bytecode = True
import replay as p
sys.path.insert(0,str(p.HERE/'replay-control'))
import collect
import runner


class RetryBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root, = (p.HERE/'artifacts').iterdir()
        _, cls.files, cls.data, _ = p.h.compact(cls.root)
        cls.request = p.read(p.HERE/'CI-REQUEST.json')
        cls.result = p.read(p.HERE/'collector-exact.json')

    def test_exact_selected_pair_and_reference_scope(self):
        self.assertEqual([r['id'] for r in p.validate_selection(self.result)],p.PAIR)
        self.assertEqual(collect.collect([self.root],self.request),self.result)

    def test_foreign_request_rejected_by_exact_collector(self):
        with mock.patch.object(runner,'sha256',return_value='0'*64):
            with self.assertRaisesRegex(runner.RunnerError,'terminal identity mismatch'):
                collect.collect([self.root],self.request)

    def test_duplicate_group_rejected_by_exact_collector(self):
        with self.assertRaisesRegex(runner.RunnerError,'duplicate or invalid matrix partition'):
            collect.collect([self.root,self.root],self.request)

    def test_one_row_splice_and_timeout_not_promoted(self):
        for status,outcome in [('NOT_RUN','UNKNOWN'),('OBSERVED','UNKNOWN')]:
            result=copy.deepcopy(self.result)
            result['rows'][0].update(status=status,outcome=outcome)
            with self.assertRaisesRegex(ValueError,'atomic complete observed pair'):
                p.validate_selection(result)

    def test_incomplete_group_is_unknown_in_exact_collector(self):
        def partial(path):
            rel=str(path.relative_to(self.root))
            if rel=='groups/cell-u34/receipt.json':
                doc=copy.deepcopy(self.files[rel]);doc['state']='FAILED'
                return json.dumps(doc).encode()
            return self.data[rel]
        with mock.patch.object(collect,'read_bytes',side_effect=partial):
            result=collect.collect([self.root],self.request)
        self.assertTrue(all(r['outcome']=='UNKNOWN' for r in result['rows'][:2]))
        with self.assertRaisesRegex(ValueError,'atomic complete observed pair'):
            p.validate_selection(result)

    def test_wrong_timeout_or_origin_rejected(self):
        terminal=self.files['receipt.json'];group=self.files['groups/cell-u34/receipt.json']
        request_hash=p.sha((p.HERE/'CI-REQUEST.json').read_bytes())
        for mutation,reason in [('timeout','exact timeout profile'),('request','origin request mismatch'),('partial','atomic complete group/terminal')]:
            changed=copy.deepcopy(group)
            if mutation=='timeout': changed['argv'][changed['argv'].index('--harness-timeout')+1]='600s'
            if mutation=='request': changed['request_sha256']='0'*64
            if mutation=='partial': changed['state']='FAILED'
            with self.assertRaisesRegex(ValueError,reason):
                p.validate_origin(terminal,changed,self.request,request_hash)

    def test_missing_results_and_timeout_never_become_success(self):
        rich=self.files['groups/cell-u34/properties.json']
        for outcome in [{'kind':'TIMEOUT'},{'kind':'UNKNOWN'}]:
            stock=copy.deepcopy(self.files['groups/cell-u34/export.json'])
            stock['harnesses'][0]['outcome']=outcome
            with self.assertRaisesRegex(ValueError,'source outcome remains exact'):
                p.inventories(stock,rich)

    def test_truncated_inventory_rejected(self):
        rich=copy.deepcopy(self.files['groups/cell-u34/properties.json'])
        rich['harnesses'][0]['properties'].pop()
        with self.assertRaisesRegex(ValueError,'stock/rich inventory count/uniqueness'):
            p.inventories(self.files['groups/cell-u34/export.json'],rich)


if __name__=='__main__':
    unittest.main(verbosity=2)
