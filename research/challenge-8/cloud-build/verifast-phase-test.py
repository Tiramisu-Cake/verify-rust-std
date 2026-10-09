#!/usr/bin/env python3
"""Isolated authorization checks; no Cloud API or proof execution."""
import copy
import datetime
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import unittest
import control

class PhaseTest(unittest.TestCase):
 def setUp(self):
  self.ledger=json.loads((Path(__file__).parent/'verifast-mdnew/BUDGET.json').read_text())
  self.args=SimpleNamespace(phase_id=control.VERIFAST_PHASE,owner='verifast')
 def at(self,stamp):
  real=datetime.datetime
  class Clock(real):
   @classmethod
   def now(cls,tz=None):return real.fromisoformat(stamp.replace('Z','+00:00'))
  return patch.object(control.datetime,'datetime',Clock)
 def test_authorized_exact_account(self):
  with self.at(control.VERIFAST_START):
   self.assertEqual(control.authorized_phase(self.args,self.ledger).isoformat(),'2026-10-09T16:57:32+00:00')
 def test_account_identity_budget_and_allowlist(self):
  with self.at(control.VERIFAST_START):
   for key,value in [('ceiling_build_seconds',7200),('owner','merge'),('allowed_lanes',['merge']),('start_utc','2026-10-09T15:00:00Z'),('deadline_utc','2026-10-09T17:00:00Z')]:
    account=copy.deepcopy(self.ledger);account[key]=value
    with self.assertRaises(SystemExit):control.authorized_phase(self.args,account)
   with self.assertRaises(SystemExit):control.authorized_phase(SimpleNamespace(phase_id=control.VERIFAST_PHASE,owner='alias'),self.ledger)
 def test_main_window_no_new_submission(self):
  for stamp in [control.VERIFAST_MAIN_DEADLINE,'2026-10-09T16:40:00Z',control.VERIFAST_DEADLINE]:
   with self.at(stamp),self.assertRaisesRegex(SystemExit,'main window ended'):control.authorized_phase(self.args,self.ledger)

if __name__=='__main__':unittest.main()
