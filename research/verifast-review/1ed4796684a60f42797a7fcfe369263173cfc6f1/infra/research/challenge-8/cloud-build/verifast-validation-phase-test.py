#!/usr/bin/env python3
"""Isolated current-phase admission controls; no API or compiler."""
import copy,datetime,json,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import control
class PhaseTest(unittest.TestCase):
 def setUp(self):
  self.ledger=json.loads((Path(__file__).parent/'verifast-mdnew-validation/BUDGET.json').read_text())
  self.args=SimpleNamespace(phase_id=control.VERIFAST_VALIDATION_PHASE,owner='verifast')
 def at(self,stamp):
  real=datetime.datetime
  class Clock(real):
   @classmethod
   def now(cls,tz=None):return real.fromisoformat(stamp.replace('Z','+00:00'))
  return patch.object(control.datetime,'datetime',Clock)
 def test_exact_new_phase(self):
  with self.at(control.VERIFAST_VALIDATION_START):
   self.assertEqual(control.authorized_phase(self.args,self.ledger).isoformat(),'2026-10-09T18:26:51+00:00')
 def test_wrong_account(self):
  with self.at(control.VERIFAST_VALIDATION_START):
   for key,value in [('ceiling_build_seconds',7200),('owner','merge'),('allowed_lanes',['merge']),('start_utc',control.VERIFAST_START),('deadline_utc','2026-10-09T18:27:51Z'),('main_deadline_utc','2026-10-09T18:00:00Z')]:
    account=copy.deepcopy(self.ledger);account[key]=value
    with self.assertRaises(SystemExit):control.authorized_phase(self.args,account)
 def test_main_cutoff(self):
  for stamp in [control.VERIFAST_VALIDATION_MAIN_DEADLINE,control.VERIFAST_VALIDATION_DEADLINE]:
   with self.at(stamp),self.assertRaisesRegex(SystemExit,'main window ended'):control.authorized_phase(self.args,self.ledger)
 def test_old_phase_stays_closed(self):
  old=json.loads((Path(__file__).parent/'verifast-mdnew/BUDGET.json').read_text())
  with self.at(control.VERIFAST_VALIDATION_START),self.assertRaisesRegex(SystemExit,'closed'):
   control.authorized_phase(SimpleNamespace(phase_id=control.VERIFAST_PHASE,owner='verifast'),old)
if __name__=='__main__':unittest.main()
