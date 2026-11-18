#!/usr/bin/env python3
"""Timeout-only sibling control. Never imports unapproved gate backlog bytes."""
import hashlib,json,subprocess
from pathlib import Path
C=Path('/root/kani-ch8-s2-r4-r2-w13');Q=C/'ch8-s1-control'
F='0e8c836857344866564e1423ad5d8d28bbc4106b';P='9e14e033f9ee31522b571c127609dcdff76d230b'
def git(*args):return subprocess.check_output(['git','-C',str(C),*args])
assert git('rev-parse','HEAD').decode().strip()==P
for name in git('diff','--name-only',P,F).decode().splitlines():
    p=C/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(git('show',F+':'+name))
w=C/'.github/workflows/ch8-s2.yml'
s=w.read_text();old='- name: Validate control and synthetic wrapper\n      timeout-minutes: 1\n'
assert s.count(old)==1;w.write_text(s.replace(old,old.replace(': 1\n',': 10\n')))
p=Q/'check_package.py';s=p.read_text().replace("assert sum(s['timeout-minutes'] for s in steps)==177","assert sum(s['timeout-minutes'] for s in steps)==186")
s=s.replace("byname={s['name']:s for s in steps}","""byname={s['name']:s for s in steps}
    # Exact approved setup caps; aggregate setup clock remains independent.
    assert [(s['name'],s['timeout-minutes']) for s in steps] == [
        ('Begin setup budget',1),('Checkout CI control',2),
        ('Validate control and synthetic wrapper',10),('Read immutable export pins',1),
        ('Checkout production model export',5),('Checkout immutable upstream tool',2),
        ('Check all source identities',1),('Setup exact stock tool',15),
        ('Build exact stock tool once',15),('Run S2 batch3probes with bounded observations',126),
        ('Materialize bounded fallback',2),('Upload bounded evidence',6)]""")
s=s.replace("'step_timeout_sum_minutes':177","'step_timeout_sum_minutes':186")
p.write_text(s)
p=Q/'test_s2.py';s=p.read_text().replace("['step_timeout_sum_minutes'],177","['step_timeout_sum_minutes'],186")
s=s.replace('    def test_sampled_component_metrics_are_group_only(self):','''    def test_timeout_caps_and_order_reject_redistribution(self):
        import yaml
        original=cp.load_yaml((HERE.parent/'.github/workflows/ch8-s2.yml').read_text())
        for case in ('validate','source','redistribute','order'):
            doc=copy.deepcopy(original);steps=doc['jobs']['s2_batch']['steps']
            if case=='validate':steps[2]['timeout-minutes']=1
            if case=='source':steps[6]['timeout-minutes']=10
            if case=='redistribute':
                steps[2]['timeout-minutes']-=1;steps[6]['timeout-minutes']+=1
            if case=='order':steps[2],steps[6]=steps[6],steps[2]
            with self.subTest(case=case),tempfile.TemporaryDirectory() as d:
                path=Path(d)/'bad.yml';path.write_text(yaml.safe_dump(doc))
                with self.assertRaises(AssertionError):cp.check_yaml(path)

    def test_setup_aggregate_remaining_boundary_without_compiler(self):
        good={'original_exit_code':0,'timed_out':False,'termination_reason':None,
              'stdout_truncated':False,'stderr_truncated':False}
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);epoch=root/'epoch';epoch.write_text('1000')
            # elapsed setup includes earlier validation/source/checkout time.
            for elapsed,expected in ((0,900),(600,900),(900,900),(901,899),(1799,1)):
                with mock.patch.object(cp.time,'time',return_value=1000+elapsed),mock.patch.object(r,'execute',return_value=good.copy()) as call:
                    self.assertEqual(cp.build(root,epoch,root/str(elapsed))['setup'],'COMPLETE')
                    self.assertEqual(call.call_args.args[3],expected)
            for elapsed in (1800,1801):
                with mock.patch.object(cp.time,'time',return_value=1000+elapsed),mock.patch.object(r,'execute') as call:
                    with self.assertRaises(AssertionError):cp.build(root,epoch,root/'expired')
                    call.assert_not_called()
            with mock.patch.object(cp.time,'time',side_effect=[2799,2801]),mock.patch.object(r,'execute',return_value=good.copy()):
                with self.assertRaises(AssertionError):cp.build(root,epoch,root/'overrun')
                self.assertEqual(json.loads((root/'overrun/receipt.json').read_text())['setup_total_seconds'],1801)

    def test_sampled_component_metrics_are_group_only(self):''')
p.write_text(s)
r=json.loads((Q/'CI-REQUEST.json').read_text());r['entry_g0']='16a4f1d3e9ca438396d9226ea3d13ffaa88150fe';r['control_reference']=F
paths=git('diff','--name-only',r['tool_sha']).decode().splitlines()
paths+=git('ls-files','--others','--exclude-standard').decode().splitlines();paths=sorted(set(paths))
r['ci_changed_paths']=paths
r['ci_payload_sha256']={p:hashlib.sha256((C/p).read_bytes()).hexdigest() for p in paths if (C/p).is_file() and p!='ch8-s1-control/CI-REQUEST.json'}
(Q/'CI-REQUEST.json').write_text(json.dumps(r,indent=2)+'\n')
assert not (Q/'test_r1403_lexical.py').exists()
assert (Q/'lexical_bindings.py').read_bytes()==git('show',F+':ch8-s1-control/lexical_bindings.py')
print('Prepared timeout-only control: R14-03 OPEN, no backlog bytes')
