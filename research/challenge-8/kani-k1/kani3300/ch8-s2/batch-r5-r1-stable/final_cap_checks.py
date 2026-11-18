"""Cap-only regressions; never invokes the full Validate command or a compiler."""
import copy,json,subprocess,sys,tempfile,unittest
from pathlib import Path
C=Path('/root/kani-ch8-s2-r5-r1-stable-final-w13');Q=C/'ch8-s1-control'
sys.dont_write_bytecode=True;sys.path.insert(0,str(Q))
import check_package as cp
import r5_profile
class R5MarginTests(unittest.TestCase):
    def check(self,doc):
        import yaml
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'workflow.yml';path.write_text(yaml.safe_dump(doc,sort_keys=False));return cp.check_yaml(path)
    def workflow(self):return cp.load_yaml((C/'.github/workflows/ch8-s2.yml').read_text())
    def test_r5_requires_exact_native_integer_twelve(self):
        for cap in (10,11,12,13,'12',True,12.0):
            with self.subTest(cap=cap):
                doc=self.workflow();doc['jobs']['s2_batch']['steps'][2]['timeout-minutes']=cap
                if type(cap) is int and cap==12:self.assertEqual(self.check(doc)['step_timeout_sum_minutes'],188)
                else:
                    with self.assertRaises(AssertionError):self.check(doc)
    def test_legacy_remains_exact_ten_and_maxima186(self):
        raw=subprocess.check_output(['git','-C',str(C),'show','d33a0900da19d865f20ccaa76e1ee27065c5a671:.github/workflows/ch8-s2.yml'],text=True)
        doc=cp.load_yaml(raw);self.assertEqual(self.check(doc)['step_timeout_sum_minutes'],186)
        doc['jobs']['s2_batch']['steps'][2]['timeout-minutes']=11
        with self.assertRaises(AssertionError):self.check(doc)
    def test_other_caps_and_order_cannot_absorb_extra_minute(self):
        for case in ('source','job','proof','redistribution','order'):
            with self.subTest(case=case):
                doc=self.workflow();job=doc['jobs']['s2_batch'];steps=job['steps']
                if case=='source':steps[6]['timeout-minutes']=2
                if case=='job':job['timeout-minutes']=181
                if case=='proof':steps[9]['timeout-minutes']=127
                if case=='redistribution':steps[2]['timeout-minutes']=10;steps[6]['timeout-minutes']=2
                if case=='order':steps[2],steps[6]=steps[6],steps[2]
                with self.assertRaises(AssertionError):self.check(doc)
    def test_runtime_and_aggregate_caps_unchanged(self):
        r=json.loads((Q/'CI-REQUEST.json').read_text());r5_profile.validate(r)
        old=json.loads(subprocess.check_output(['git','-C',str(C),'show','4e97d370aba4adc480fcc3701b111d02658aa94d:ch8-s1-control/CI-REQUEST.json']))
        self.assertEqual(r['r5'],old['r5']);self.assertEqual(r['budgets'],old['budgets'])
        self.assertEqual(r['budgets']['setup_seconds'],1800);self.assertEqual(r['budgets']['workflow_minutes'],180)
        self.assertEqual(r['r5']['caps']['campaign_seconds'],6900)
