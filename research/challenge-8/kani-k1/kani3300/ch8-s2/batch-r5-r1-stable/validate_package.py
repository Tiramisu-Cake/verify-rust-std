#!/usr/bin/env python3
"""Static package validation. Does NOT rerun final Validate or check-source."""
import ast,hashlib,importlib.util,json,os,re,subprocess,sys,tempfile
from pathlib import Path
H=Path(__file__).resolve().parent
P=json.loads((H/'PINS.json').read_text())
def git(repo,*args,env=None):return subprocess.check_output(['git','-C',str(repo),*args],text=True,env=env).strip()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,v):(H/n).write_text(json.dumps(v,indent=2)+'\n')
def replay(repo,item):
 with tempfile.TemporaryDirectory(prefix='r4-r2-replay-') as d:
  env=dict(os.environ,GIT_INDEX_FILE=str(Path(d)/'index'))
  subprocess.run(['git','-C',str(repo),'read-tree',item['base']],env=env,check=True)
  if (H/item['path']).stat().st_size:
   subprocess.run(['git','-C',str(repo),'apply','--cached',str(H/item['path'])],env=env,check=True)
  tree=git(repo,'write-tree',env=env);assert tree==item['target_tree']
  return {'patch':item['path'],'base':item['base'],'tree':tree,'status':'EXACT_TREE_MATCH','empty_patch':not (H/item['path']).stat().st_size}
def shallow(repo,head,depth,endpoint):
 common=Path(git(repo,'rev-parse','--git-common-dir'))
 if not common.is_absolute():common=(repo/common).resolve()
 chain=git(repo,'rev-list','--first-parent','--max-count='+str(depth),head).splitlines();assert len(chain)==depth and endpoint in chain
 with tempfile.TemporaryDirectory(prefix='r4-r2-shallow-') as d:
  probe=Path(d);subprocess.run(['git','init','-q',str(probe)],check=True)
  (probe/'.git/objects/info/alternates').write_text(str(common/'objects')+'\n')
  subprocess.run(['git','-C',str(probe),'update-ref','refs/heads/probe',head],check=True)
  subprocess.run(['git','-C',str(probe),'symbolic-ref','HEAD','refs/heads/probe'],check=True)
  (probe/'.git/shallow').write_text(chain[-1]+'\n')
  assert git(probe,'rev-parse','--is-shallow-repository')=='true' and git(probe,'rev-list','--first-parent','HEAD').splitlines()==chain
  assert git(probe,'cat-file','-t',endpoint)=='commit'
  paths=git(probe,'diff','--name-only',endpoint,'HEAD').splitlines()
  assert git(probe,'rev-parse','HEAD^{tree}')==git(repo,'rev-parse',head+'^{tree}')
 return {'head':head,'depth':depth,'endpoint':endpoint,'retained_chain':chain,'endpoint_diff_paths':paths,'status':'PASS_REAL_SHALLOW_METADATA_SHARED_OBJECTS'}
def main():
 C=Path(P['control']['worktree']);S=Path(P['source']['worktree']);T=Path(P['tool']['worktree']);Q=C/'ch8-s1-control';old=H.with_name('batch-r5-r1');G=Path('/root/verify-rust-std-kani3300-g0')
 for key,repo in [('source',S),('control',C),('tool',T)]:
  for field,rev in [('sha','HEAD'),('tree','HEAD^{tree}'),('parent','HEAD^')]:assert git(repo,'rev-parse',rev)==P[key][field]
  assert not git(repo,'status','--porcelain=v1')
 r=json.loads((Q/'CI-REQUEST.json').read_text());prior=json.loads((old/'CI-REQUEST.json').read_text())
 assert sha(Q/'CI-REQUEST.json')==P['control']['request_sha256'] and sha(C/'.github/workflows/ch8-s2.yml')==P['control']['workflow_sha256']
 assert (H/'CI-REQUEST.json').read_bytes()==(Q/'CI-REQUEST.json').read_bytes() and (H/'WORKFLOW.yml').read_bytes()==(C/'.github/workflows/ch8-s2.yml').read_bytes()
 assert git(C,'diff','--name-only',P['tool']['sha'],'HEAD').splitlines()==r['ci_changed_paths']
 assert set(r['ci_payload_sha256'])=={n for n in r['ci_changed_paths'] if (C/n).is_file()}-{'ch8-s1-control/CI-REQUEST.json'}
 for path,h in r['ci_payload_sha256'].items():assert sha(C/path)==h,path
 for key in ('changed_file_sha256','cfg_pfc_source_sha256','ordinary_contract_source_sha256','contract_stack_source_sha256','lexical_source_sha256'):
  for path,h in r[key].items():assert sha(S/path)==h
 assert {k:v for k,v in r.items() if k not in ('entry_g0','control_reference','ci_payload_sha256')}=={k:v for k,v in prior.items() if k not in ('entry_g0','control_reference','ci_payload_sha256')}
 assert set(k for k in r['ci_payload_sha256'] if r['ci_payload_sha256'][k]!=prior['ci_payload_sha256'][k])=={'.github/workflows/ch8-s2.yml','ch8-s1-control/check_package.py','ch8-s1-control/r5_profile.py','ch8-s1-control/test_s2.py','ch8-s1-control/test_r5.py'}
 sys.path.insert(0,str(Q));import check_package,r5_profile
 caps=check_package.check_yaml(C/'.github/workflows/ch8-s2.yml');assert caps['step_timeout_sum_minutes']==188;r5_profile.validate(r)
 tests=json.loads((H/'TARGETED-TESTS.json').read_text());log=(H/'TARGETED-TESTS.txt').read_text()
 assert tests['status']=='PASS' and tests['test_count']==26 and tests['suite_success']
 assert tests['control_sha']=='5d7b8cadedc2f7627e5d28432701b8ea6823e188' # prior fixture object; same test bytes
 assert sha(Q/'test_r5.py')==tests['test_r5_sha256'] and sha(H/'cap_checks.py')==tests['cap_checks_sha256'] and sha(H/'TARGETED-TESTS.txt')==tests['transcript_sha256']
 assert len(tests['repeat_attempts'])==6 and all(x['success'] for x in tests['repeat_attempts'])
 for attempt in tests['repeat_attempts']:
  assert len(attempt['real_case'])==1;case=attempt['real_case'][0];sup=case['supervision'];child=case['child_ready'];cleanup=sup['containment']
  assert cleanup['verified'] and sup['worker_exit']==0 and child['pid']==child['pgid']!=sup['worker_pid']
  assert any(all(rec[k]==child[k] for k in ('pid','pgid','start_ticks')) for rec in cleanup['observed'])
  assert any(rec['pid']==child['pid'] and rec['start_ticks']==child['start_ticks'] for rec in cleanup['signals']) and any(rec['pid']==child['pid'] for rec in cleanup['reaped_adopted'])
  if 'after_early' in attempt['test']:assert sup['orphan_survivors_at_worker_exit']==[]
 boundary=json.loads((H/'EARLY-ORPHAN-BOUNDARY.json').read_text());assert boundary['status']=='PASS' and boundary['control_sha']==tests['control_sha'] and boundary['transcript_sha256']==sha(H/'EARLY-ORPHAN-BOUNDARY.txt') and boundary['script_sha256']==sha(H/'check_early_orphan.py')
 inherited=json.loads((H/'INHERITED-HOST-EVIDENCE.json').read_text())
 for rec in inherited['files']:assert sha(H/rec['file'])==rec['sha256'] and (H/rec['file']).read_bytes()==(old/rec['source_file']).read_bytes()
 timing=json.loads((H/'PRIOR-OBJECT-COMBINED-FINAL-VALIDATE-TIMING.json').read_text());assert timing['provenance']['control']['sha']==P['frozen_control'] and timing['elapsed_seconds']==409.026897886
 actual=json.loads((H/'STABLE-TEST-PROVENANCE.json').read_text());check=json.loads((H/'STABLE-CHECK-SOURCE-TIMING.json').read_text())
 assert actual['status']=='PASS' and actual['test_count']==136 and actual['execution_count']==1 and actual['provenance']['control']['sha']==P['control']['sha']
 assert actual['provenance']['request_sha256']==P['control']['request_sha256'] and actual['provenance']['workflow_sha256']==P['control']['workflow_sha256']
 assert actual['transcript_sha256']==sha(H/'STABLE-FINAL-VALIDATE.txt') and 720/actual['elapsed_seconds']>=1.5
 doc=check_package.load_yaml((H/'WORKFLOW.yml').read_text());steps={x['name']:x for x in doc['jobs']['s2_batch']['steps']}
 assert actual['command']==steps['Validate control and synthetic wrapper']['run'] and check['command']==steps['Check all source identities']['run']
 final=(H/'STABLE-FINAL-VALIDATE.txt').read_text();assert 'Ran 136 tests in' in final and final.endswith('\nOK\n')
 for name in ('test_escaped_setsid_child_found_and_reaped','test_escaped_child_adopted_after_early_snapshot','test_escaped_fixture_missing_ready_cleans_child','test_archive_only_prefix_exact_seal_and_collect_after_later_failure'):
  assert re.search(name+r'.* \.\.\. ok',final),name
 assert check['status']=='PASS' and check['provenance']==actual['provenance'] and check['transcript_sha256']==sha(H/'STABLE-CHECK-SOURCE.txt')
 for rec in json.loads((H/'MAP-PROVENANCE.json').read_text()):assert sha(H/rec['file'])==rec['sha256'] and (H/rec['file']).read_bytes()==(old/rec['file']).read_bytes()
 prop=json.loads((H/'PROPERTY-COVER-MAP.json').read_text());oldprop=json.loads((old/'PROPERTY-COVER-MAP.json').read_text());assert prop['request_sha256']==P['control']['request_sha256'];prop['request_sha256']=oldprop['request_sha256'];assert prop==oldprop
 inv=json.loads((H/'INVARIANCE.json').read_text());assert git(C,'diff','--name-only',P['frozen_control'],'HEAD').splitlines()==inv['allowed_changed_paths']==['.github/workflows/ch8-s2.yml','ch8-s1-control/CI-REQUEST.json','ch8-s1-control/check_package.py','ch8-s1-control/r5_profile.py','ch8-s1-control/test_r5.py','ch8-s1-control/test_s2.py']
 for rec in inv['unchanged_files']:assert sha(C/rec['path'])==rec['sha256']
 finalcaps=json.loads((H/'FINAL-CAP-TESTS.json').read_text());assert finalcaps['exit_code']==0 and finalcaps['control_sha']==P['control']['sha'] and finalcaps['control_tree']==P['control']['tree'] and finalcaps['transcript_sha256']==sha(H/'FINAL-CAP-TESTS.txt')
 assert 'Ran 7 tests in' in (H/'FINAL-CAP-TESTS.txt').read_text()
 olddoc=check_package.load_yaml((old/'WORKFLOW.yml').read_text());doc['jobs']['s2_batch']['steps'][2]['timeout-minutes']=11;assert doc==olddoc
 precursor=json.loads((H/'PRECURSOR-STABLE-TEST-PROVENANCE.json').read_text());assert precursor['status']=='PASS' and precursor['test_count']==136 and precursor['elapsed_seconds']==440.727425928 and precursor['provenance']['control']['sha']==tests['control_sha']
 assert 660/precursor['elapsed_seconds']<1.5 and sha(H/'PRECURSOR-STABLE-FINAL-VALIDATE.txt')==precursor['transcript_sha256']
 patches=[]
 for item in json.loads((H/'PATCHES.json').read_text()):
  assert sha(H/item['path'])==item['sha256'];patches.append(replay(S if item['path'].startswith('SOURCE') else C,item))
 ancestry=[shallow(C,P['control']['sha'],7,P['tool']['sha']),shallow(S,P['source']['sha'],5,P['source']['base']),shallow(T,P['tool']['sha'],2,P['tool']['sha'])]
 for commit,directory in [(P['frozen_package'],old),('2ed2c8ef2f6b9d6460494b85594e3a5f08387a7f',H.with_name('review-batch-r5-r1'))]:
  subprocess.run(['git','-C',str(G),'diff','--exit-code',commit,'--',str(directory.relative_to(G))],check=True,capture_output=True)
 subprocess.run(['git','-C',str(C),'diff','--check',P['frozen_control'],'HEAD'],check=True)
 dump('VALIDATION.json',{'state':'STATIC_TEST_ONLY_DELTA_PASS','control':P['control'],'targeted_tests':26,'early_orphan_boundary':boundary,'real_child_repetitions':6,'patch_replays':patches,'checkout_depths':ancestry,'workflow':caps,'full136_final':actual,'check_source':check,'prior134':'INHERITED_PRIOR_OBJECTd67_409.026897886s','frozen_dc8_review2ed':'UNCHANGED_GIT_OBJECT_DIFF','production_service_source_tool_campaign_caps':'BYTE_IDENTICAL','cap_exception':'measured precursor440.727s requires12min; exact-cap-only assertions','native_compiler_CI':'NOT_RUN','proof_credit':'NONE'})
 print('STATIC_TEST_ONLY_DELTA_PASS:26 targeted+1 boundary;136 final;6 exact replays;shallow7/5/2;production/frozen objects unchanged')
if __name__=='__main__':main()
