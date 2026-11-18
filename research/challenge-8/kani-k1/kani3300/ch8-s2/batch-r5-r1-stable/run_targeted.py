#!/usr/bin/env python3
"""Predetermined bounded real-child repetitions, then relevant process/portable/cap regressions."""
import datetime,hashlib,io,json,os,subprocess,sys,time,unittest
from pathlib import Path
from unittest import mock
H=Path(__file__).resolve().parent;C=Path('/root/kani-ch8-s2-r5-r1-stable-w13');Q=C/'ch8-s1-control'
sys.dont_write_bytecode=True;sys.path[:0]=[str(H),str(Q)]
from test_r5 import ProcessTests
import test_r5,cap_checks

def git(*a):return subprocess.check_output(['git','-C',str(C),*a],text=True).strip()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not (H/'TARGETED-TESTS.json').exists()
assert not git('status','--porcelain=v1')
start=time.monotonic_ns();records=[];outputs=[];success=True;count=0
original=ProcessTests.escaped_case
for i in range(3):
 for name in ('test_escaped_setsid_child_found_and_reaped','test_escaped_child_adopted_after_early_snapshot'):
  captured=[]
  def capture(self,*args,**kw):
   result=original(self,*args,**kw);captured.append({'supervision':result[0],'child_ready':result[1]});return result
  stream=io.StringIO()
  with mock.patch.object(ProcessTests,'escaped_case',capture):
   result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.TestSuite([ProcessTests(name)]))
  records.append({'iteration':i+1,'test':name,'success':result.wasSuccessful(),'real_case':captured,'transcript':stream.getvalue()})
  outputs.append(stream.getvalue());success=success and result.wasSuccessful();count+=result.testsRun
names=['test_r5.ProcessTests','test_r5.PortablePrefixTests','test_r5.CampaignTests.test_identity_start_and_containment_abort','cap_checks.R5MarginTests','test_s2.S2Tests.test_workflow_caps_types_and_single_serial_job','test_s2.S2Tests.test_timeout_caps_and_order_reject_redistribution','test_s2.S2Tests.test_setup_aggregate_remaining_boundary_without_compiler']
stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(names));success=success and result.wasSuccessful();count+=result.testsRun;outputs.append(stream.getvalue())
end=time.monotonic_ns();(H/'TARGETED-TESTS.txt').write_text('\n'.join(outputs))
record={'status':'PASS' if success else 'FAIL','control_sha':git('rev-parse','HEAD'),'control_tree':git('rev-parse','HEAD^{tree}'),'request_sha256':sha(Q/'CI-REQUEST.json'),'workflow_sha256':sha(C/'.github/workflows/ch8-s2.yml'),'test_r5_sha256':sha(Q/'test_r5.py'),'cap_checks_sha256':sha(H/'cap_checks.py'),'command':[sys.executable,str(Path(__file__).resolve())],'cwd':str(Path.cwd()),'environment':{'PYTHONDONTWRITEBYTECODE':os.environ.get('PYTHONDONTWRITEBYTECODE')},'test_count':count,'repeat_policy':'EXACTLY3 normal +3 forced-delayed, predetermined; every outcome retained; no retry-until-pass','repeat_attempts':records,'relevant_suite':names,'suite_success':result.wasSuccessful(),'suite_transcript':stream.getvalue(),'monotonic_start_ns':start,'monotonic_end_ns':end,'elapsed_seconds':(end-start)/1e9,'transcript_sha256':sha(H/'TARGETED-TESTS.txt'),'compiler_CI':'NOT_RUN','proof_credit':'NONE'}
(H/'TARGETED-TESTS.json').write_text(json.dumps(record,indent=2)+'\n');print(record['status'],count,'tests',record['elapsed_seconds'],'seconds');assert success
