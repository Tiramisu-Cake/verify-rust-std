"""Predetermined repetitions and failure probes against exact final committed code."""
import hashlib, importlib.util, io, json, os, sys, time, unittest
from pathlib import Path
from unittest import mock
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent;B=H.with_name('batch-r5-r1-stable')
C=Path('/root/kani-ch8-s2-r5-r1-stable-final-w13');Q=C/'ch8-s1-control';sys.path.insert(0,str(Q))
import test_r5, r5_runtime as rt, r5_campaign as c, r5_profile as p, runner as r
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
caps=load('final_cap_checks',B/'final_cap_checks.py')
cases=[]
class FailureBoundary(unittest.TestCase):
 def test_ready_eof_wrong_identity_and_sigterm_escalation(self):
  original=rt.supervise
  for mode in ('eof','wrong_identity','missing_ignore_term'):
   with self.subTest(mode=mode):
    captured=[]
    def inject(argv,cwd,*args,**kw):
     argv=list(argv)
     script="""import json,os,signal,sys
from pathlib import Path
os.setsid();signal.alarm(15)
raw=Path('/proc/self/stat').read_text();tail=raw[raw.rfind(')')+2:].split()
identity={'pid':os.getpid(),'pgid':os.getpgrp(),'start_ticks':int(tail[19])}
Path('failure-child.json').write_text(json.dumps(identity))
MODE=__MODE__
if MODE=='missing_ignore_term':signal.signal(signal.SIGTERM,signal.SIG_IGN)
elif MODE=='eof':os.close(int(sys.argv[1]))
else:
    wrong=dict(identity,pid=identity['pid']+1)
    os.write(int(sys.argv[1]),json.dumps(wrong).encode());os.close(int(sys.argv[1]))
signal.pause()
""".replace('__MODE__',repr(mode))
     argv[-1]=script
     result=original(argv,cwd,*args,**kw)
     child=json.loads((cwd/'failure-child.json').read_text());stderr=(cwd/'worker.stderr').read_text()
     captured.append({'mode':mode,'supervision':result,'child':child,'stderr':stderr})
     self.assertNotIn(child['pid'],rt.census());self.assertTrue(result['containment']['verified'])
     self.assertIsNone(result['supervisor_error']);self.assertNotEqual(result['worker_exit'],0)
     expected={'eof':'JSONDecodeError','wrong_identity':'AssertionError','missing_ignore_term':'child-ready timeout'}[mode]
     self.assertIn(expected,stderr)
     return result
    with mock.patch.object(rt,'supervise',inject):test_r5.ProcessTests().escaped_case()
    self.assertEqual(len(captured),1);cases.extend(captured)
 def test_nonempty_early_orphan_rejects_real_controller(self):
  import tempfile
  helper=test_r5.CampaignTests();helper.req=r.load_request()
  with tempfile.TemporaryDirectory() as d:
   out=Path(d);sup=helper.emit(out,p.ORDER[0]);doc=c.read(out/'groups'/('r5-'+p.ORDER[0])/'receipt.json')
   c.validate_owned_groups(doc,sup)
   sup['orphan_survivors_at_worker_exit']=[sup['containment']['observed'][1]]
   c.validate_owned_groups(doc,sup)
   with self.assertRaisesRegex(c.GlobalFailure,'^global_supervisor_failure$'):c.root_outcome(out,helper.req,p.ORDER[0],sup)
def main():
 assert not (H/'TARGETED-TESTS.json').exists()
 started=time.monotonic_ns();records=[];outputs=[];good=True;count=0
 original=test_r5.ProcessTests.escaped_case
 for iteration in range(3):
  for name in ('test_escaped_setsid_child_found_and_reaped','test_escaped_child_adopted_after_early_snapshot'):
   evidence=[]
   def capture(self,*args,**kw):
    result=original(self,*args,**kw);evidence.append({'supervision':result[0],'child_ready':result[1]});return result
   stream=io.StringIO()
   with mock.patch.object(test_r5.ProcessTests,'escaped_case',capture):
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.TestSuite([test_r5.ProcessTests(name)]))
   records.append({'iteration':iteration+1,'test':name,'pass':result.wasSuccessful(),'real_case':evidence,'transcript':stream.getvalue()});outputs.append(stream.getvalue());good &= result.wasSuccessful();count+=result.testsRun
 names=['test_r5.ProcessTests','test_r5.PortablePrefixTests','test_r5.CampaignTests.test_identity_start_and_containment_abort','test_s2.S2Tests.test_workflow_caps_types_and_single_serial_job','test_s2.S2Tests.test_timeout_caps_and_order_reject_redistribution','test_s2.S2Tests.test_setup_aggregate_remaining_boundary_without_compiler']
 suite=unittest.defaultTestLoader.loadTestsFromNames(names)
 suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(caps.R5MarginTests));suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(FailureBoundary))
 stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
 good &= result.wasSuccessful();count+=result.testsRun;outputs.append(stream.getvalue());end=time.monotonic_ns()
 (H/'TARGETED-TESTS.txt').write_text('\n'.join(outputs))
 record={'status':'PASS' if good else 'FAIL','control':'63535098ab85c70c8707eee0afd65f53c9ef566a','test_r5_sha256':hashlib.sha256((Q/'test_r5.py').read_bytes()).hexdigest(),'test_count':count,'repeat_policy':'Exactly 3 normal and 3 forced-early-empty; predetermined; every result retained; no retry-until-pass','repetitions':records,'failure_probes':cases,'regressions':names+['final_cap_checks.R5MarginTests','FailureBoundary'],'monotonic_start_ns':started,'monotonic_end_ns':end,'elapsed_seconds':(end-started)/1e9,'transcript_sha256':hashlib.sha256((H/'TARGETED-TESTS.txt').read_bytes()).hexdigest(),'compiler_fullrunner_CI':'NOT_RUN','proof_credit':'NONE'}
 (H/'TARGETED-TESTS.json').write_text(json.dumps(record,indent=2)+'\n');print(record['status'],count,'tests',record['elapsed_seconds'],'seconds');assert good
if __name__=='__main__':main()
