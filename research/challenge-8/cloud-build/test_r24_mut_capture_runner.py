"""Execute only the runner's pure metadata guards with isolated fake records."""
import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

CLOUD=Path(__file__).resolve().parent
PHASE='SORT4-ACTUAL-SELECT-2026-10-24-R24'
ROUTE='SORT4-ACTUAL-SELECT-2026-10-23-R21'
BUILD='12345678-1234-4234-8234-123456789abc'

def block(marker):
    lines=(CLOUD/'run-o26-select-callee-r20.sh').read_text().splitlines()
    start=next(i for i,x in enumerate(lines) if "<<'"+marker+"'" in x)
    end=lines.index(marker,start+1)
    return compile('\n'.join(lines[start+1:end]),'runner:'+marker,'exec')

class MetadataGuards(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.env={'CLOUD_BUILD_ID':BUILD,'SORT4_R24_SESSION_PHASE_ID':PHASE,'SORT4_R20_CALLEE_PHASE_ID':ROUTE}
        self.mode=json.loads((CLOUD.parent/'task-history/select-callee-r24/P2-MUT-CAPTURE-MODE.json').read_text())
        self.summary={'schema':'select-r24-mut-capture-summary-v1','complete':True,'body_proof_run':False,
            'typed_admission':False,'semantic_rule_enabled':False,'publication_allowed':False,
            'accepted':False,'proof_credit':0,'r24_session_phase_id':PHASE,
            'provider_record':{'provider':'cloud-build','build_id':BUILD,'project':'smallsort-ci',
                               'region':'global','os':'ubuntu-22.04','arch':'x86_64'}}
    def tearDown(self):self.tmp.cleanup()
    def run_mode(self,mode,env):
        p=self.root/'mode.json';p.write_text(json.dumps(mode))
        with patch.dict(os.environ,env,clear=True),patch.object(sys,'argv',['guard',str(p)]):exec(block('MUT_MODE'),{})
    def audit(self,summary=None,env=None,code=0):
        p=self.root/'summary.json';out=self.root/'audit.json'
        if summary is not None:p.write_text(json.dumps(summary))
        else:p.unlink(missing_ok=True)
        with patch.dict(os.environ,self.env if env is None else env,clear=True),patch.object(sys,'argv',['audit',str(p),str(out),str(code),'capture']):exec(block('MUT_AUDIT'),{})
        return json.loads(out.read_text())
    def test_mode_rejects_wrong_or_missing_phase_and_unsafe_flags(self):
        self.run_mode(self.mode,self.env)
        for key in ('SORT4_R24_SESSION_PHASE_ID','SORT4_R20_CALLEE_PHASE_ID'):
            env=dict(self.env);env.pop(key)
            with self.subTest(key=key),self.assertRaises(AssertionError):self.run_mode(self.mode,env)
        for key,value in [('enabled',False),('source_only',False),('proof_admission',True),('publication_allowed',True),('owner','other')]:
            mode=dict(self.mode);mode[key]=value
            with self.subTest(key=key),self.assertRaises(AssertionError):self.run_mode(mode,self.env)
    def test_capture_audit_accepts_only_complete_no_proof_native_record(self):
        result=self.audit(self.summary);self.assertTrue(result['evidence_complete'])
        for key in ('accepted','verification_accepted','proof_credit','body_proof_run','typed_admission','publication_allowed'):self.assertIs(result[key],False)
        for key in ('complete','body_proof_run','typed_admission','semantic_rule_enabled','publication_allowed','accepted','proof_credit'):
            bad=copy.deepcopy(self.summary);bad[key]=not bad[key]
            with self.subTest(key=key):self.assertFalse(self.audit(bad)['evidence_complete'])
        self.assertFalse(self.audit(self.summary,code=2)['evidence_complete'])
        self.assertFalse(self.audit()['evidence_complete'])
    def test_capture_audit_incomplete_records_never_gain_credit(self):
        for value in ({}, [], 'wrong-type', 0):
            with self.subTest(value=value):
                result=self.audit(value)
                self.assertFalse(result['evidence_complete'])
                self.assertIs(result['proof_credit'],False)
        for key in ('complete','body_proof_run','typed_admission','semantic_rule_enabled',
                    'publication_allowed','accepted','proof_credit','provider_record'):
            for value in (None, 'NOT_RUN', '0'):
                bad=copy.deepcopy(self.summary);bad[key]=value
                with self.subTest(key=key,value=value):self.assertFalse(self.audit(bad)['evidence_complete'])
        for code in (4, 124, 137):
            with self.subTest(code=code):self.assertFalse(self.audit(self.summary,code=code)['evidence_complete'])
    def test_capture_audit_refuses_provider_or_native_context_drift(self):
        for key,value in [('build_id','87654321-1234-4234-8234-123456789abc'),('project','other'),('os','other'),('provider','local')]:
            bad=copy.deepcopy(self.summary);bad['provider_record'][key]=value
            with self.subTest(key=key):self.assertFalse(self.audit(bad)['evidence_complete'])
        for key,value in [('CLOUD_BUILD_ID','bad-id'),('SORT4_R24_SESSION_PHASE_ID','wrong')]:
            env=dict(self.env);env[key]=value
            with self.subTest(key=key):self.assertFalse(self.audit(self.summary,env=env)['evidence_complete'])

if __name__=='__main__':unittest.main()
