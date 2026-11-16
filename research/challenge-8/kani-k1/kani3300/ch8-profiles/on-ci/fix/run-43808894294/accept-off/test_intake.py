"""Targeted malformed evidence, binding and dependency regression tests; no verifier."""
import copy
import json
from pathlib import Path
import unittest
import intake as i

class IntakeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runner=i.module('test_off_runner',i.CONTROL/'ch8-prof-on-control/off/runner.py')
        cls.rows=cls.runner.load_request()['rows']
        cls.row=next(r for r in cls.rows if r['id']=='profile_merge4_contract_u8_len4')
        cls.gp=i.ART/'groups/group-00'
        cls.group=i.read(cls.gp/'receipt.json')
        cls.export=i.read(cls.gp/'export.json')
        cls.h=next(h for h in cls.export['harnesses'] if h['name']==cls.row['selector'])
        cls.group_rows=[r for r in cls.rows if r['id'] in cls.group['rows']]
        cls.sources={p:i.git(i.ROOT,'show',i.SOURCE+':'+p).decode() for p in i.binding.SPEC['source_files_sha256']}
        cls.accept=i.read(i.HERE/'ACCEPT.json')

    def test_legacy_target_recheck_keeps_complete_inventory_state(self):
        row=next(r for r in self.rows if r['id']=='swap_contract_u8_n2')
        old,new=i.checked_preflight(self.runner,self.gp/'export.json',row,self.group_rows)
        self.assertEqual(old['state'],'SOURCE_STAGE_TARGET_MISMATCH')
        self.assertEqual(new['state'],'INCOMPLETE_CHECK_INVENTORY')

    def preflight_mutation(self,mutate):
        # Patch only structured export read. Preserve the actual pinned path and cap.
        from unittest.mock import patch
        e=copy.deepcopy(self.export);mutate(e)
        with patch.object(Path,'read_bytes',return_value=json.dumps(e).encode()):
            with self.assertRaises(i.v3.EvidenceError):
                i.checked_preflight(self.runner,self.gp/'export.json',self.row,self.group_rows)

    def test_wrong_config_not_hidden_by_legacy_gate(self):
        self.preflight_mutation(lambda e:e['configuration']['checks'].update(unwinding=False))

    def test_wrong_tool_fails_closed(self):
        self.preflight_mutation(lambda e:e.update(kani_commit='bad'))

    def test_not_run_fails_closed(self):
        self.preflight_mutation(lambda e:e.update(run_state='NOT_RUN'))

    def test_partial_selection_fails_closed(self):
        self.preflight_mutation(lambda e:e['harness_selection'].update(matched_count=0))

    def test_wrong_unwind_fails_closed(self):
        self.preflight_mutation(lambda e:next(h for h in e['harnesses'] if h['name']==self.row['selector']).update(resolved_unwind=1))

    def test_source_attribute_uses_exact_path(self):
        m=i.mapping_for(self.row,self.h,self.sources)
        self.assertEqual(m['binding']['source_target_expression'],'profiles::merge4_profile')
        e=copy.deepcopy(self.h);e['attributes']['kind']['ProofForContract']['target_fn']='other::merge4_profile'
        result=i.policy.classify(self.row,e,m,{}, {},'INCOMPLETE_CHECK_INVENTORY')
        self.assertIn('FULL_SOURCE_ATTRIBUTE_TARGET_MISMATCH',result['unknown_reasons'])

    def test_source_attribute_absence_blocks(self):
        sources=copy.deepcopy(self.sources)
        sources[self.row['source_file']]=sources[self.row['source_file']].replace('#[kani::proof_for_contract(profiles::merge4_profile)]','')
        with self.assertRaises(i.v3.EvidenceError):i.mapping_for(self.row,self.h,sources)

    def test_required_cover_missing_blocks(self):
        row=next(r for r in self.rows if r['id']=='profile_relation_lt_u8')
        h=copy.deepcopy(next(h for h in self.export['harnesses'] if h['name']==row['selector']))
        m=i.mapping_for(row,h,self.sources);h['covers']['satisfied']=[];h['covers']['total']=0
        r=i.policy.classify(row,h,m,{}, {},'INCOMPLETE_CHECK_INVENTORY')
        self.assertIn('REQUIRED_COVER_MISSING_OR_NOT_SATISFIED',r['pending_reasons'])

    def test_unsupported_wrong_class_blocks(self):
        h=copy.deepcopy(self.h);h['unsupported_constructs'][0]['class']='assertion'
        with self.assertRaises(i.v3.EvidenceError):
            i.helpers.fresh_unsupported_links(h,{u['id']:dict(id=u['id'],status=u['status'],description=u['description'],file=u['file'].split('/export/')[-1],line=int(u['line'])) for u in h['unsupported_constructs']})

    def test_role_site_translation_requires_identical_function(self):
        rules=i.fresh_roles(i.read(i.OFF/'accept-v3/ROLE-RULES.json')['rules'],self.sources)
        self.assertEqual(next(r for r in rules if r['id'].startswith('prof02-region'))['lines'],[114])
        sources=copy.deepcopy(self.sources);p=i.binding.DIR+'/verify/merge.rs'
        sources[p]=sources[p].replace('d >= n as isize || -d >= m as isize','d >= 0 || -d >= m as isize')
        with self.assertRaises(i.v3.EvidenceError):i.fresh_roles(i.read(i.OFF/'accept-v3/ROLE-RULES.json')['rules'],sources)

    def consumer_fixture(self):
        row=copy.deepcopy(next(r for r in self.rows if r['id']=='profile_merge_consumer_u8_len4'))
        accepted={r['id']:r for r in self.accept['rows']}
        values=copy.deepcopy([accepted[row['id']],accepted[row['leaf_companion']]])
        return row,values

    def test_new_leaf_is_required(self):
        row,values=self.consumer_fixture();values[1]['status']='PENDING'
        i.consumers_after_leaves([row],values)
        self.assertEqual(values[0]['status'],'PENDING')
        self.assertIn('MATCHING_LEAF_NOT_ACCEPTED',values[0]['pending_reasons'])

    def test_consumer_instance_mismatch_blocks(self):
        row,values=self.consumer_fixture();values[1]['exact_instance_identity']='old merge_profile'
        i.consumers_after_leaves([row],values)
        self.assertEqual(values[0]['status'],'PENDING')

    def test_consumer_export_config_mismatch_blocks(self):
        row,values=self.consumer_fixture();values[1]['evidence']['export_sha256']='other'
        i.consumers_after_leaves([row],values)
        self.assertEqual(values[0]['status'],'PENDING')

    def test_negative_foreign_site_blocks(self):
        row=next(r for r in self.rows if r['id']=='rejects_payload_corruption')
        r=next(r for r in self.accept['rows'] if r['id']==row['id'])
        records={p['id']:copy.deepcopy(p) for p in r['negative_oracle_records']}
        h={'checks':{'failure':list(records)}}
        next(iter(records.values()))['line']+=1
        with self.assertRaises(i.v3.EvidenceError):i.bind_negative(row,h,records,self.sources)

    def test_negative_cover_literal_remap_and_wrong_site_rejected(self):
        row=next(r for r in self.rows if r['id']=='rejects_always_true')
        r=next(r for r in self.accept['rows'] if r['id']==row['id'])
        records={c['property']['id']:copy.deepcopy(c['property']) for c in r['exact_binding_v4']['covers']}
        m=i.mapping_for(row,next(h for h in i.read(i.ART/'groups/group-01/export.json')['harnesses'] if h['name']==row['selector']),self.sources)
        bound=i.bind_covers(row,m,records,self.sources)
        self.assertEqual([c['property']['line'] for c in bound['covers']],[229,220,211])
        next(iter(records.values()))['line']=220
        with self.assertRaises(i.v3.EvidenceError):i.bind_covers(row,m,records,self.sources)

    def test_final_all_rows_bound_with_fresh_merge_leaf(self):
        d=self.accept;self.assertEqual(d['prior_admissions_reused'],0)
        self.assertEqual(d['summary']['statuses'],dict(ACCEPTED=63,BLOCKED_TOOL=0,REJECTED=0,PENDING=0))
        self.assertTrue(all(r['binding_state']=='BOUND' and not r['unknown_reasons'] and not r['pending_reasons'] for r in d['rows']))
        r=next(r for r in d['rows'] if r['id']=='profile_merge_consumer_u8_len4')
        self.assertEqual(r['consumer_leaf']['id'],'profile_merge4_contract_u8_len4')
        self.assertEqual(d['summary']['covers'],{'satisfied':190})

if __name__=='__main__':unittest.main()
