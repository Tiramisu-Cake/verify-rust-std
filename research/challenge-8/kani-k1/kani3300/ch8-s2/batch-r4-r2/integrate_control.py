#!/usr/bin/env python3
"""Exact committed SAME14-approved patch inheritance and explicit CI module wiring."""
import hashlib,json,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent;G=Path('/root/verify-rust-std-kani3300-g0');B=H.with_name('r14-03-gate-backlog');R=H.with_name('r14-03-gate-backlog-review');C=Path('/root/kani-ch8-s2-r4-r2-final-w13');Q=C/'ch8-s1-control'
REVIEW=subprocess.check_output(['git','-C',str(G),'rev-parse','ccb6a60731'],text=True).strip()
def git(*args):return subprocess.check_output(['git','-C',str(C),*args])
def sha(b):return hashlib.sha256(b).hexdigest()
report=json.loads((R/'REPORT.json').read_text());assert report['verdict']=='APPROVE' and report['finding']['status']=='CLOSED'
assert report['local_control']['sha']=='0e97a487d8b7f8e8cbced5dbe2b6909c7150c695' and report['patch']['sha256']=='1dfaf5a1fa2d748e81bea4093018eb65972d7cfc807e47c0d1f7ad39565f8cba'
for name in ('REPORT.json','INPUTS.json','FINDING-CLOSURE.json','MANIFEST.sha256'):
 rel=str((R/name).relative_to(G));assert (R/name).read_bytes()==subprocess.check_output(['git','-C',str(G),'show',REVIEW+':'+rel])
assert sha((B/'PATCH.patch').read_bytes())==report['patch']['sha256']
assert git('rev-parse','HEAD').decode().strip()=='9e14e033f9ee31522b571c127609dcdff76d230b'
PRE='64c1d0bbfee90b3fac0a13f5bd0545703daa4d18'
for name in git('diff','--name-only','HEAD',PRE).decode().splitlines():
 p=C/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(git('show',PRE+':'+name))
subprocess.run(['git','-C',str(C),'apply',str(B/'PATCH.patch')],check=True)
exact={}
for name in ('lexical_bindings.py','test_r1403_lexical.py'):
 p='ch8-s1-control/'+name;approved=git('show',report['local_control']['sha']+':'+p);assert (C/p).read_bytes()==approved;exact[p]=sha(approved)
p=C/'.github/workflows/ch8-s2.yml';s=p.read_text();old='test_rustc_diagnostics.py test_contract_stacks.py';assert s.count(old)==1;p.write_text(s.replace(old,old+' test_r1403_lexical.py'))
p=Q/'check_package.py';s=p.read_text();line="    assert 'test_runner.py test_s107.FinalizationTests test_s2.py test_cfg_pfc.py' in byname['Validate control and synthetic wrapper']['run']"
assert s.count(line)==1
s=s.replace(line,line+"\n    assert byname['Validate control and synthetic wrapper']['run'].splitlines() == [\n        'python3 check_package.py control --repo ..',\n        'python3 -m unittest -v test_runner.py test_s107.FinalizationTests test_s2.py test_cfg_pfc.py test_rustc_diagnostics.py test_contract_stacks.py test_r1403_lexical.py']")
p.write_text(s)
r=json.loads((Q/'CI-REQUEST.json').read_text());paths=git('diff','--name-only',r['tool_sha']).decode().splitlines()+git('ls-files','--others','--exclude-standard').decode().splitlines();paths=sorted(set(paths));r['ci_changed_paths']=paths
r['ci_payload_sha256']={p:sha((C/p).read_bytes()) for p in paths if (C/p).is_file() and p!='ch8-s1-control/CI-REQUEST.json'}
(Q/'CI-REQUEST.json').write_text(json.dumps(r,indent=2)+'\n')
(H/'GATE-INTEGRATION.json').write_text(json.dumps({'review_commit':REVIEW,'verdict':'APPROVE','R14-03':'CLOSED','package':report['package_commit'],'approved_control':report['local_control'],'patch_sha256':report['patch']['sha256'],'exact_inherited_files':exact,'integration_delta':['workflow actual explicit validation list appends test_r1403_lexical.py','check_yaml enforces exact final two-command validation list','ci_changed_paths and ci_payload_sha256 rebound for exact integrated candidate'],'source':'UNCHANGED','gate_review_does_not_approve_integration':True,'final_delta_review':'PENDING','GO':'PENDING'},indent=2)+'\n')
print('APPROVED_EXACT_GATE_BYTES_INHERITED; explicit regression CI module wired; final review pending')
