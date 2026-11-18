#!/usr/bin/env python3
"""Narrow deterministic controller boundary; retains real-child tests separately."""
import hashlib,io,json,subprocess,sys,tempfile,unittest
from pathlib import Path
H=Path(__file__).resolve().parent;C=Path('/root/kani-ch8-s2-r5-r1-stable-w13');Q=C/'ch8-s1-control'
sys.dont_write_bytecode=True;sys.path.insert(0,str(Q))
import r5_campaign as c,r5_profile as p,runner as r
from test_r5 import CampaignTests
class EarlyOrphanBoundary(unittest.TestCase):
 def test_valid_owned_identity_then_nonempty_early_orphan_rejected(self):
  request=r.load_request();helper=CampaignTests();helper.req=request
  with tempfile.TemporaryDirectory() as d:
   out=Path(d);sup=helper.emit(out,p.ORDER[0]);doc=c.read(out/'groups'/('r5-'+p.ORDER[0])/'receipt.json')
   c.validate_owned_groups(doc,sup) # prove rejection does not come from invalid identity fixture
   sup['orphan_survivors_at_worker_exit']=[sup['containment']['observed'][1]]
   c.validate_owned_groups(doc,sup)
   with self.assertRaisesRegex(c.GlobalFailure,'^global_supervisor_failure$'):
    c.root_outcome(out,request,p.ORDER[0],sup)
if __name__=='__main__':
 assert not (H/'EARLY-ORPHAN-BOUNDARY.json').exists()
 stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(EarlyOrphanBoundary))
 (H/'EARLY-ORPHAN-BOUNDARY.txt').write_text(stream.getvalue())
 sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 record={'status':'PASS' if result.wasSuccessful() else 'FAIL','control_sha':subprocess.check_output(['git','-C',str(C),'rev-parse','HEAD'],text=True).strip(),'test_count':result.testsRun,'script_sha256':sha(Path(__file__).resolve()),'transcript_sha256':sha(H/'EARLY-ORPHAN-BOUNDARY.txt'),'scope':'SYNTHETIC_VALID_OWNED_IDS_AND_REAL_CONTROLLER; no production/runtime mutation','command':[sys.executable,str(Path(__file__).resolve())],'test_r5_sha256':sha(Q/'test_r5.py')}
 (H/'EARLY-ORPHAN-BOUNDARY.json').write_text(json.dumps(record,indent=2)+'\n');print(record['status']);assert result.wasSuccessful()
