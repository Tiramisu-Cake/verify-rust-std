from pathlib import Path
import tempfile
import unittest
import intake


class IntakeTests(unittest.TestCase):
    def test_tool_blocker_preserves_unknown_as_blocked(self):
        r={'unknown_reasons':['unreachable role unresolved'],'pending_reasons':['required post unreachable']}
        self.assertEqual(intake.decision({'expected':'SUCCESS'},{'checks':{'failure':['tool']}},r,[{'id':'tool'}]),'BLOCKED_TOOL')
        self.assertEqual(intake.decision({'expected':'SUCCESS'},{'checks':{'failure':['tool','target']}},r,[{'id':'tool'}]),'REJECTED')

    def test_foreign_positive_failure_rejected(self):
        self.assertEqual(intake.decision({'expected':'SUCCESS'},{'checks':{'failure':['foreign']}},
            {'unknown_reasons':[],'pending_reasons':['POSITIVE_NOT_SUCCESS']},[]),'REJECTED')

    def test_foreign_negative_failure_rejected(self):
        self.assertEqual(intake.decision({'expected':'DETECTED'},{},
            {'unknown_reasons':[],'pending_reasons':['PREDECLARED_NEGATIVE_ORACLE_MISMATCH']},[]),'REJECTED')

    def test_unknown_cannot_be_accepted(self):
        self.assertEqual(intake.decision({'expected':'SUCCESS'},{},
            {'unknown_reasons':['missing input'],'pending_reasons':[]},[]),'PENDING')

    def test_exact_instrumentation_role_and_wrong_site(self):
        fn='kani::mem_init::MemoryInitializationState::get::<8>'
        p=dict(id=fn+'.assertion.1',function=fn,file='library/kani_core/src/mem_init.rs',line=93,
               column=46,description='attempt to add with overflow',status='UNREACHABLE')
        self.assertEqual(intake.instrumentation_role(p)['role'],'instrumentation_defensive_branch')
        for changes in [{'line':118},{'column':45},{'description':'actual initialization predicate'},
                        {'file':'library/core/src/lib.rs'},{'function':'kani::mem_init::unreviewed::<8>'}]:
            self.assertIsNone(intake.instrumentation_role(dict(p,**changes)))

    def test_literal_required_post_never_instrumentation(self):
        p=dict(id='f.assertion.1',function='f',file='x.rs',line=1,column=1,
               description='|_| sorted(v)',status='UNREACHABLE')
        self.assertEqual(intake.required_role(p,{'x.rs':'#[kani::ensures(|_| sorted(v))]'})['role'],'postcondition')
        self.assertIsNone(intake.instrumentation_role(p))

    def test_duplicate_terminal_marker_is_rejected_even_after_expected_markers(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'stdout.log'
            valid='Checking harness exact...\nRESULTS:\nSUMMARY:\nVERIFICATION:- SUCCESSFUL\nVerification Time: 0.1s\n'
            row={'selector':'exact'};h={'outcome':{'verdict':'SUCCESS'}}
            intake.validate_markers(valid,row,h)
            for extra in ['VERIFICATION:- SUCCESSFUL\n','SUMMARY:\n','Verification Time: 0.1s\n']:
                path.write_text(valid+extra)
                markers=intake.rg(path,r'^Checking harness |^VERIFICATION:|^Verification Time:|^RESULTS:|^SUMMARY:',6)
                with self.assertRaises(ValueError):intake.validate_markers(markers,row,h)

    def test_selected_multiline_record_and_missing(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'stdout.log'
            p.write_text('noise\nCheck 1: f.assertion.1\n - Status: SUCCESS\n - Description: "line one\nline two"\n - Location: x.rs:1:2 in function f\n\nCheck 2: g.assertion.1\n - Status: SUCCESS\n - Description: "other"\n - Location: x.rs:3:4 in function g\n')
            self.assertEqual(intake.select_records(p,{'f.assertion.1'})['f.assertion.1']['description'],'line one\nline two')
            with self.assertRaises(ValueError): intake.select_records(p,{'absent.assertion.1'})

    def test_unsupported_requires_exact_class_site_and_status(self):
        pid='f.unsupported_construct.1'
        u=dict(id=pid,status='SUCCESS',description='unsupported',file='/export/x.rs',line='3',
               **{'class':'unsupported_construct'})
        p=dict(id=pid,status='SUCCESS',description='unsupported',file='x.rs',line=3)
        self.assertEqual(intake.fresh_unsupported_links({'unsupported_constructs':[u]},{pid:p})[pid]['semantics'],
                         'assert(false); assume(false)')
        for changes in [{'status':'FAILURE'},{'line':4},{'description':'other'}]:
            with self.assertRaises(ValueError):
                intake.fresh_unsupported_links({'unsupported_constructs':[u]},{pid:dict(p,**changes)})


class FreshBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import json
        cls.report=json.loads((intake.HERE/'ACCEPT.json').read_text())
        cls.results={r['id']:r for r in cls.report['rows']}
        cls.request=json.loads((intake.HERE/'runner-input/CI-REQUEST.json').read_text())
        cls.rows={r['id']:r for r in cls.request['rows']}
        cls.sources={p:intake.git(intake.ROOT,'show',intake.SOURCE+':'+p).decode()
                     for p in intake.fresh.SPEC['source_files_sha256']}
        cls.harnesses={h['name']:h for gp in (intake.ART/'groups').iterdir()
                       for h in json.loads((gp/'export.json').read_text())['harnesses']}

    def fixture(self,rid):
        import copy
        result=self.results[rid]
        h=copy.deepcopy(self.harnesses[self.rows[rid]['selector']])
        bound=result['exact_binding_v4']
        # All bound properties were freshly selected from this row by replay.
        def collect(v):
            if isinstance(v,dict):
                if {'id','status','description','function'}<=v.keys():yield v
                for x in v.values():yield from collect(x)
            elif isinstance(v,list):
                for x in v:yield from collect(x)
        records={p['id']:copy.deepcopy(p) for p in collect(bound)}
        demangled={bound['contract_symbol']:bound['modifies_wrapper_fully_qualified']} if h['contract'] else {}
        return copy.deepcopy(self.rows[rid]),h,records,demangled,copy.deepcopy(self.sources)

    def test_merge4_same_lane_fresh_leaf_and_delta(self):
        leaf=self.results['profile_merge4_contract_u8_len4']
        consumer=self.results['profile_merge_consumer_u8_len4']
        self.assertEqual(leaf['status'],'ACCEPTED')
        self.assertEqual(leaf['previous_on_comparison']['status'],'NEW_ROW')
        self.assertEqual(consumer['consumer_leaf']['id'],leaf['id'])
        self.assertTrue(consumer['consumer_leaf']['identical_source_tool_config'])
        self.assertEqual(consumer['exact_instance_identity'],leaf['exact_instance_identity'])
        self.assertIn('merge4_profile',leaf['exact_instance_identity'])

    def test_failed_required_postcondition_blocks_fresh_binding(self):
        row,h,records,names,sources=self.fixture('profile_merge4_contract_u8_len4')
        pid=self.results[row['id']]['exact_binding_v4']['postconditions'][0]['id']
        records[pid]['status']='FAILURE'
        with self.assertRaises(ValueError):intake.fresh.bind_fresh(row,h,records,names,sources)

    def test_wrong_full_instance_blocks_fresh_binding(self):
        row,h,records,names,sources=self.fixture('profile_merge4_contract_u8_len4')
        names={k:v.replace('merge4_profile','merge_profile') for k,v in names.items()}
        with self.assertRaises(ValueError):intake.fresh.bind_fresh(row,h,records,names,sources)

    def test_missing_or_non_sat_cover_blocks_fresh_binding(self):
        row,h,records,names,sources=self.fixture('profile_merge4_contract_u8_len4')
        pid=self.results[row['id']]['exact_binding_v4']['covers'][0]['property']['id']
        records[pid]['status']='UNREACHABLE'
        with self.assertRaises(ValueError):intake.fresh.bind_fresh(row,h,records,names,sources)
        del records[pid]
        with self.assertRaises(KeyError):intake.fresh.bind_fresh(row,h,records,names,sources)

    def test_source_or_oracle_drift_blocks_fresh_binding(self):
        row,h,records,names,sources=self.fixture('profile_merge4_contract_u8_len4')
        path=next(iter(sources));sources[path]+='\n'
        with self.assertRaises(ValueError):intake.fresh.bind_fresh(row,h,records,names,sources)
        row['allowed_failure_descriptions']=['unplanned']
        with self.assertRaises(ValueError):intake.fresh.bind_fresh(row,h,records,names,self.sources)

    def test_negative_oracle_needs_exact_source_function_site(self):
        import copy
        rid='rejects_payload_corruption';result=self.results[rid]
        row=self.rows[rid];h=self.harnesses[row['selector']]
        p=result['negative_oracle_records'][0];records={p['id']:copy.deepcopy(p)}
        self.assertEqual(len(intake.negative_oracles(row,h,records,self.sources)),1)
        for change in [{'function':'foreign::helper'},{'line':1},{'file':'foreign.rs'},
                       {'description':'prefix '+p['description']}]:
            altered={p['id']:dict(p,**change)}
            with self.assertRaises(ValueError):intake.negative_oracles(row,h,altered,self.sources)

    def test_all_admissions_keep_complete_fresh_gates(self):
        self.assertEqual(len(self.results),63)
        for r in self.results.values():
            if r['status']!='ACCEPTED':continue
            self.assertEqual(r['unknown_reasons'],[])
            self.assertEqual(r['pending_reasons'],[])
            self.assertEqual(r['binding_state'],'BOUND')
            self.assertEqual(r['proof_credit'],'NONE')
            self.assertTrue(r['stdout_binding']['parsed_id_status_pairs']>0)
        self.assertEqual(self.report['summary']['statuses'],dict(ACCEPTED=61,BLOCKED_TOOL=2,REJECTED=0,PENDING=0))


if __name__=='__main__': unittest.main()
