"""Checks for policy-significant failures; no compiler or verifier invocation."""
import copy
import json
from pathlib import Path
import sys
import unittest

sys.dont_write_bytecode = True
import intake as a


class PolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0,str(a.CONTROL/'ch8-s1-control'))
        cls.report = a.read(a.HERE/'ACCEPT.json')
        cls.request = a.read(a.CONTROL/'ch8-s1-control/CI-REQUEST.json')
        cls.h = a.read(a.BASE/'evidence/light-model-u5/export.json')['harnesses'][0]

    def test_inventory_rejects_loss_status_and_wrong_shapes(self):
        a.inventory(self.h)
        mutations = [lambda h: h['checks'].update(total=h['checks']['total']+1),
                     lambda h: h['covers'].update(total=h['covers']['total']+1),
                     lambda h: h['checks'].update(success=None),
                     lambda h: h['checks'].update(success=True),
                     lambda h: h['checks'].update(unreachable=None),
                     lambda h: h['covers'].update(satisfied=None),
                     lambda h: h['checks'].update(unknown=['lost-property']),
                     lambda h: h['covers'].update(other=[{'id':'x','status':'NEW'}]),
                     lambda h: h['checks']['unreachable'].append(h['checks']['unreachable'][0]),
                     lambda h: h.update(n_failed=1)]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                h = copy.deepcopy(self.h)
                mutate(h)
                with self.assertRaises((ValueError, TypeError)):
                    a.inventory(h)

    def test_unsupported_rejects_mismatched_class_status_id_site(self):
        p = self.h['unsupported_constructs'][0]
        self.assertEqual(a.unsupported_link(p, self.h)['semantics'], 'assert(false); assume(false)')
        for key, value in [('status','FAILURE'),('status','UNREACHABLE'),('status','UNKNOWN'),
                           ('class','assertion'),('id','x.assertion.1'),('file',None),('line',None),('description','')]:
            q = dict(p, **{key:value})
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                a.unsupported_link(q, self.h)
        h = copy.deepcopy(self.h)
        h['checks']['unreachable'].append(p['id'])
        with self.assertRaises(ValueError):
            a.unsupported_link(p,h)

    def test_mandatory_unreachable_never_exempted(self):
        for role in a.REQUIRED_ROLES:
            self.assertEqual(a.role_decision({'exact_source_site_bound':True,'role':role,'reason':'helper'}),
                             'BLOCKED_MANDATORY_OBLIGATION_UNREACHABLE')
            self.assertEqual(a.role_decision({'exact_source_site_bound':False,'role':role}), 'UNKNOWN')
        self.assertEqual(a.role_decision(None), 'UNKNOWN')
        self.assertEqual(a.role_decision({'exact_source_site_bound':True,'role':'helper'}), 'UNKNOWN')

    def test_cover_counts_and_order_do_not_bind_messages(self):
        row = next(r for r in self.request['rows'] if r['selector'] == self.h['name'])
        for ids in [self.h['covers']['satisfied'],list(reversed(self.h['covers']['satisfied']))]:
            h = copy.deepcopy(self.h)
            h['covers']['satisfied'] = ids
            table = a.cover_message_table(row,h,[])
            self.assertTrue(all(x['property_id'] is None for x in table))

    def test_macro_retains_both_exact_anchors(self):
        fixed = a.binding_fixed(self.request)
        for rid, invocation in zip(a.MACRO_ROWS,(66,67,68)):
            self.assertEqual([x['line'] for x in fixed['source_bindings'][rid]['locations']], [invocation,29])
        self.assertEqual(len(self.request['source_bindings'][a.MACRO_ROWS[0]]['locations']),1)
        for key, value in [('sha256','wrong'),('locations',[{'line':30,'source':'wrong'}])]:
            request = copy.deepcopy(self.request)
            request['source_bindings'][a.MACRO_ROWS[0]][key] = value
            with self.assertRaises(ValueError):
                a.binding_fixed(request)

    def test_preflight_binding_mutations_rejected(self):
        sys.path.insert(0,str(a.CONTROL/'ch8-s1-control'))
        runner = a.load('s104_test_runner',a.CONTROL/'ch8-s1-control/runner.py')
        fixed = a.binding_fixed(self.request)
        for rid in a.MACRO_ROWS:
            row = next(r for r in self.request['rows'] if r['id']==rid)
            path = a.BASE/'evidence/light-model-u5/export.json'
            selectors = a.read(path)['harness_selection']['requested_filters']
            binding = fixed['source_bindings'][rid]
            for key, value in [('selector','wrong'),('crate','wrong'),('mode','PFC'),
                               ('file','wrong.rs'),('locations',[{'line':30,'source':'wrong'}])]:
                bad = copy.deepcopy(binding)
                bad[key] = value
                result = runner.parse_export(path,row,source_binding=bad,
                    std=Path('/home/runner/work/kani/kani/export'),group_selectors=selectors)
                self.assertEqual(result['state'],'WRONG_SOURCE_BINDING')

    def test_six_frozen_oracles_reject_changed_id_and_site(self):
        import negative_oracle
        n = 0
        for ep in (a.BASE/'evidence').glob('*/export.json'):
            for h in a.read(ep)['harnesses']:
                rows = [r for r in self.request['rows'] if r['selector']==h['name'] and r.get('oracle')]
                if not rows:
                    continue
                oracle = rows[0]['oracle']
                self.assertTrue(negative_oracle.matches(h,oracle))
                for field, value in [('property_id','wrong.assertion.1'),('line',oracle['line']+1),
                                     ('export_file','wrong.rs'),('class','cover')]:
                    self.assertFalse(negative_oracle.matches(h,dict(oracle,**{field:value})))
                n += 1
        self.assertEqual(n,6)

    def test_no_admission_or_retroactive_attachment_oracles(self):
        rows = self.report['rows']
        self.assertFalse(any(r['status']=='ACCEPTED' for r in rows))
        self.assertEqual({r['id'] for r in rows if r['status']=='ACCEPTED_NEGATIVE_OBSERVATION'},
                         {'activation_descending_rejected','activation_effectful_rejected','activation_unsupported_type_rejected'})
        self.assertEqual(sum(len(r['unreachable']) for r in rows),413)
        self.assertTrue(all(p['decision']=='UNKNOWN' for r in rows for p in r['unreachable']))
        for row in rows:
            if row['variant'] != 'production':
                self.assertEqual(row['status'],'OBSERVED_UNQUALIFIED')
                self.assertIsNone(row['predeclared_oracle'])
                self.assertTrue(row['future_oracle_proposal']['status'].startswith('PROPOSED_NEXT_PACKAGE_ONLY'))
        self.assertTrue(all(u['eligible_for_review'] is False for u in self.report['replacement_unions']))


if __name__ == '__main__':
    unittest.main()
