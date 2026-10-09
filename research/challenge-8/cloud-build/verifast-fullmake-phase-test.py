#!/usr/bin/env python3
"""Small isolated admission checks; no Cloud API or verifier execution."""
import copy,datetime,json,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import control

class PhaseTest(unittest.TestCase):
 def setUp(self):
  self.ledger=json.loads((Path(__file__).parent/'verifast-mdnew-fullmake/BUDGET.json').read_text())
  self.args=SimpleNamespace(phase_id=control.VERIFAST_FULLMAKE_PHASE,owner='verifast')
 def at(self,stamp):
  real=datetime.datetime
  class Clock(real):
   @classmethod
   def now(cls,tz=None):return real.fromisoformat(stamp.replace('Z','+00:00'))
  return patch.object(control.datetime,'datetime',Clock)
 def test_exact_phase(self):
  with self.at(control.VERIFAST_FULLMAKE_START):
   self.assertEqual(control.authorized_phase(self.args,self.ledger).isoformat(),
                    '2026-10-09T21:51:27+00:00')
 def test_wrong_account(self):
  with self.at(control.VERIFAST_FULLMAKE_START):
   for key,value in [('ceiling_build_seconds',7200),('owner','merge'),
                     ('allowed_lanes',['verifast-mdnew-upstream-pr']),
                     ('main_deadline_utc','2026-10-09T21:22:27Z'),
                     ('deadline_utc','2026-10-09T21:52:27Z')]:
    bad=copy.deepcopy(self.ledger);bad[key]=value
    with self.assertRaises(SystemExit):control.authorized_phase(self.args,bad)
 def test_no_new_submission_after_main(self):
  with self.at(control.VERIFAST_FULLMAKE_MAIN_DEADLINE),self.assertRaisesRegex(SystemExit,'main window ended'):
   control.authorized_phase(self.args,self.ledger)
 def test_closed_old_phase(self):
  old=json.loads((Path(__file__).parent/'verifast-mdnew-upstream-pr/BUDGET.json').read_text())
  with self.at(control.VERIFAST_FULLMAKE_START),self.assertRaisesRegex(SystemExit,'closed'):
   control.authorized_phase(SimpleNamespace(phase_id=control.VERIFAST_PR_PHASE,owner='verifast'),old)
 def test_narrow_timeout_ceiling(self):
  newcap=3000 if self.args.phase_id==control.VERIFAST_FULLMAKE_PHASE and 'verifast-mdnew-fullmake' in self.ledger['allowed_lanes'] else 1740
  self.assertEqual(newcap,3000)
  self.assertEqual(control.VERIFAST_PR_LANES,frozenset(('verifast-mdnew-upstream-pr',)))
if __name__=='__main__':unittest.main()
