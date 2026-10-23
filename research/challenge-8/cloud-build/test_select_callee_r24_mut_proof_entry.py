import copy
import importlib.util
import json
from pathlib import Path
import unittest

HERE=Path(__file__).parent

def load(name,file):
    spec=importlib.util.spec_from_file_location(name,HERE/file)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
entry=load('r24_mut_entry_tests','select-callee-r24-mut-proof-entry.py')
lib=load('r24_mut_proof_tests','select-callee-r24-mut-proof.py')

class AuditTests(unittest.TestCase):
    def setUp(self):
        self.native='11111111-2222-3333-4444-555555555555'
        self.env={'CLOUD_BUILD_ID':self.native,'SMALLSORT_EXECUTION_PROVIDER':'cloud-build',
                  lib.R24_PHASE_ENV:lib.R24_PHASE,lib.R21_PHASE_ENV:lib.R21_PHASE,
                  'LANE':lib.LANE,'SORT4_SELECT_PROFILE':lib.PROFILE}
        self.pins=lib._load_pins(HERE.parents[2].resolve())
        rows={}
        for v in lib.VARIANTS:
            pin=self.pins['cases'][v]
            rows[v]={'variant':v,'complete':True,'status':'COMPLETE_SOURCE_REPORTED_FINGERPRINT',
                     'native_build_id':self.native,'source_unchanged':True,'ghost_strip_identity':True,
                     'original_sha256':self.pins['source']['original_sha256'],
                     'verified_sha256':pin['source']['verified_sha256'],
                     'fingerprint':{'snapshots':pin['snapshots']}}
        captured={'complete':True,'native_build_id':self.native,'variant_order':list(lib.VARIANTS),
                  'rows':rows,'location_control':{'complete':True,'native_build_id':self.native,
                   'reproduces_positive_pins':True,'fingerprint':{'snapshots':self.pins['cases']['positive']['snapshots']}}}
        pair={'original/lib.rs':self.pins['source']['original_sha256'],
              'verified/lib.rs':self.pins['source']['verified_sha256']}
        stage={'status':'RAN','exit':0,'source_before':pair,'source_after':pair,
               'source_unchanged':True,'intrinsic_gate_active':False,'pointer_drop_gate_active':False}
        row={'variant':'positive','stage_name':'r24-mut-proof-positive',
             'classification':'POSITIVE_PROOF_STAGE_RAN_SOURCE_INTACT','source_intact':True,
             'source_before':pair,'source_after':pair,'errors':[],'native_marker_seen':1,'proof_stage':stage}
        self.summary={'schema':lib.SCHEMA,'complete':True,'proof_mode':'positive','proof_variants':['positive'],
                      'native_build_id':self.native,'provider':'cloud-build','lane':lib.LANE,'profile':lib.PROFILE,
                      'r24_session_phase_id':lib.R24_PHASE,'r21_route_phase_id':lib.R21_PHASE,
                      'pins':{'path':lib.PINS_REL.as_posix(),'sha256':lib.PINS_SHA256},
                      'complete_source_observation':captured,'rows':{'positive':row},
                      'accepted':False,'publication_allowed':False,'proof_credit':0}
    def audit(self,s=None,const=None,exit=0,env=None):
        return entry.audit_record(self.summary if s is None else s,
           {'evidence_complete':True} if const is None else const,exit,'synthetic',
           self.env if env is None else env,lib,self.pins)
    def test_source_complete_has_no_credit(self):
        a=self.audit();self.assertTrue(a['evidence_complete']);self.assertFalse(a['verification_accepted']);self.assertEqual(a['proof_credit'],0)
    def test_absent_wrongtype_and_partial(self):
        for s in [[],False,{'complete':True},dict(self.summary,rows=None),dict(self.summary,complete=False)]:
            with self.subTest(summary=s):self.assertFalse(self.audit(s=s)['evidence_complete'])
    def test_all_stage_failures(self):
        for field,value in [('status','NOT_RUN'),('status','TIMED_OUT'),('exit',None),('exit',True),('exit',1),('source_after',{}),('intrinsic_gate_active',True),('source_unchanged',None)]:
            s=copy.deepcopy(self.summary);s['rows']['positive']['proof_stage'][field]=value
            with self.subTest(field=field,value=value):self.assertFalse(self.audit(s=s)['evidence_complete'])
    def test_wrong_source_row_marker_and_build(self):
        for key,value in [('native_marker_seen',0),('native_marker_seen',2),('source_before',{}),('errors',['synthetic']),('variant','omit-selected-own')]:
            s=copy.deepcopy(self.summary);s['rows']['positive'][key]=value
            self.assertFalse(self.audit(s=s)['evidence_complete'])
        self.assertFalse(self.audit(s=dict(self.summary,native_build_id='wrong'))['evidence_complete'])
    def test_fingerprint_and_location_drift(self):
        for name in lib.SNAPSHOTS:
            s=copy.deepcopy(self.summary);s['complete_source_observation']['rows']['positive']['fingerprint']['snapshots'][name]['sha256']='0'*64
            self.assertFalse(self.audit(s=s)['evidence_complete'])
        s=copy.deepcopy(self.summary);s['complete_source_observation']['location_control']['complete']=False
        self.assertFalse(self.audit(s=s)['evidence_complete'])
    def test_const_regression_and_context_and_exit_required(self):
        for const in [{},{'evidence_complete':None},{'evidence_complete':False}]:self.assertFalse(self.audit(const=const)['evidence_complete'])
        self.assertFalse(self.audit(exit=4)['evidence_complete'])
        self.assertFalse(self.audit(env=dict(self.env,LANE='wrong'))['evidence_complete'])
        self.assertFalse(self.audit(env=dict(self.env,SORT4_R24_MUTABLE_CASE='positive'))['evidence_complete'])
    def test_no_earned_credit_or_publication(self):
        for key in ['accepted','publication_allowed','proof_credit']:
            self.assertFalse(self.audit(s=dict(self.summary,**{key:True}))['evidence_complete'])

if __name__=='__main__':unittest.main()
