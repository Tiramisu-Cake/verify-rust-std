#!/usr/bin/env python3
"""Isolated new-phase admission controls; no API, build, or compiler."""
import copy,datetime,json,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import control

class PhaseTest(unittest.TestCase):
    def setUp(self):
        self.ledger=json.loads((Path(__file__).parent/'verifast-mdnew-upstream-pr/BUDGET.json').read_text())
        self.args=SimpleNamespace(phase_id=control.VERIFAST_PR_PHASE,owner='verifast')
    def at(self,stamp):
        real=datetime.datetime
        class Clock(real):
            @classmethod
            def now(cls,tz=None): return real.fromisoformat(stamp.replace('Z','+00:00'))
        return patch.object(control.datetime,'datetime',Clock)
    def test_exact_phase(self):
        with self.at(control.VERIFAST_PR_START):
            self.assertEqual(control.authorized_phase(self.args,self.ledger).isoformat(),'2026-10-09T20:04:08+00:00')
    def test_wrong_account_or_window(self):
        with self.at(control.VERIFAST_PR_START):
            for key,value in [('ceiling_build_seconds',7200),('owner','merge'),('allowed_lanes',['verifast-mdnew-cfg']),
                              ('start_utc',control.VERIFAST_VALIDATION_START),('main_deadline_utc','2026-10-09T19:30:00Z'),
                              ('deadline_utc','2026-10-09T20:04:09Z')]:
                account=copy.deepcopy(self.ledger);account[key]=value
                with self.assertRaises(SystemExit): control.authorized_phase(self.args,account)
    def test_no_new_work_after_main_cutoff(self):
        for stamp in (control.VERIFAST_PR_MAIN_DEADLINE,control.VERIFAST_PR_DEADLINE):
            with self.at(stamp),self.assertRaisesRegex(SystemExit,'main window ended'):
                control.authorized_phase(self.args,self.ledger)
    def test_old_phase_and_lanes_preserved(self):
        old=json.loads((Path(__file__).parent/'verifast-mdnew-validation/BUDGET.json').read_text())
        with self.at(control.VERIFAST_PR_START),self.assertRaisesRegex(SystemExit,'closed'):
            control.authorized_phase(SimpleNamespace(phase_id=control.VERIFAST_VALIDATION_PHASE,owner='verifast'),old)
        self.assertEqual(control.VERIFAST_VALIDATION_LANES,frozenset(('verifast-mdnew-cfg','verifast-mdnew-regressions')))
        self.assertEqual(control.VERIFAST_PR_LANES,frozenset(('verifast-mdnew-upstream-pr',)))

if __name__=='__main__': unittest.main()
