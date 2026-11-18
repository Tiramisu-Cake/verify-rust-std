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
 C=Path(P['control']['worktree']);S=Path(P['source']['worktree']);T=Path(P['tool']['worktree']);Q=C/'ch8-s1-control';old=H.with_name('batch-r5')
 for key,repo in [('source',S),('control',C),('tool',T)]:
  for field,rev in [('sha','HEAD'),('tree','HEAD^{tree}'),('parent','HEAD^')]:assert git(repo,'rev-parse',rev)==P[key][field]
  assert not git(repo,'status','--porcelain=v1')
 r=json.loads((Q/'CI-REQUEST.json').read_text())
 assert sha(Q/'CI-REQUEST.json')==P['control']['request_sha256'] and sha(C/'.github/workflows/ch8-s2.yml')==P['control']['workflow_sha256']
 assert (H/'CI-REQUEST.json').read_bytes()==(Q/'CI-REQUEST.json').read_bytes()
 assert (H/'WORKFLOW.yml').read_bytes()==(C/'.github/workflows/ch8-s2.yml').read_bytes()
 paths=git(C,'diff','--name-only',P['tool']['sha'],'HEAD').splitlines();assert paths==r['ci_changed_paths']
 assert set(r['ci_payload_sha256'])=={n for n in paths if (C/n).is_file()}-{'ch8-s1-control/CI-REQUEST.json'}
 for path,h in r['ci_payload_sha256'].items():assert sha(C/path)==h,path
 for key in ('changed_file_sha256','cfg_pfc_source_sha256','ordinary_contract_source_sha256','contract_stack_source_sha256','lexical_source_sha256'):
  for path,h in r[key].items():assert sha(S/path)==h
 sys.path.insert(0,str(Q));import check_package,r5_profile
 result=check_package.check_yaml(C/'.github/workflows/ch8-s2.yml');assert result['step_timeout_sum_minutes']==187
 newdoc=check_package.load_yaml((H/'WORKFLOW.yml').read_text());olddoc=check_package.load_yaml((old/'WORKFLOW.yml').read_text())
 assert [x.get('run') for x in newdoc['jobs']['s2_batch']['steps']]==[x.get('run') for x in olddoc['jobs']['s2_batch']['steps']]
 normalized=json.loads(json.dumps(newdoc));normalized['jobs']['s2_batch']['steps'][2]['timeout-minutes']=10;assert normalized==olddoc
 assert sum(x['timeout-minutes'] for x in newdoc['jobs']['s2_batch']['steps'])==187
 assert r['r5']==json.loads((old/'CI-REQUEST.json').read_text())['r5'];r5_profile.validate(r)
 tests=json.loads((H/'CAP-TESTS.json').read_text());log=(H/'CAP-TESTS.txt').read_text()
 assert tests['exit_code']==0 and tests['control_sha']==P['control']['sha'] and tests['control_tree']==P['control']['tree']
 assert tests['request_sha256']==P['control']['request_sha256'] and tests['workflow_sha256']==P['control']['workflow_sha256']
 assert sha(H/'CAP-TESTS.txt')==tests['transcript_sha256'] and 'Ran 7 tests in' in log and log.endswith('\nOK\n')
 assert sha(Q/'test_s2.py')==tests['test_files_sha256']['test_s2.py'] and sha(H/'cap_checks.py')==tests['test_files_sha256']['cap_checks.py']
 inherited=json.loads((H/'INHERITED-HOST-EVIDENCE.json').read_text())
 assert inherited['classification']=='INHERITED_PRIOR_OBJECT' and inherited['prior130_suite_executions_new_head']==0
 for name,rec in inherited['files'].items():
  assert sha(H/name)==rec['sha256'] and (H/name).read_bytes()==(old/rec['source_file']).read_bytes()
 timing=json.loads((H/'PRIOR-OBJECT-VALIDATE-TIMING.json').read_text())
 assert timing['provenance']['control']['sha']==P['frozen_control'] and timing['provenance']['control']['sha']!=P['control']['sha']
 assert timing['elapsed_seconds']==403.420022367 and timing['status']=='PASS'
 for rec in json.loads((H/'MAP-PROVENANCE.json').read_text()):assert sha(H/rec['file'])==rec['sha256'] and (H/rec['file']).read_bytes()==(old/rec['file']).read_bytes()
 property_map=json.loads((H/'PROPERTY-COVER-MAP.json').read_text());prior_property=json.loads((old/'PROPERTY-COVER-MAP.json').read_text())
 assert property_map['request_sha256']==P['control']['request_sha256']
 property_map['request_sha256']=prior_property['request_sha256'];assert property_map==prior_property
 changed=git(C,'diff','--name-only',P['frozen_control'],'HEAD').splitlines()
 assert changed==json.loads((H/'INVARIANCE.json').read_text())['allowed_changed_paths']
 for rec in json.loads((H/'INVARIANCE.json').read_text())['unchanged_files']:assert sha(C/rec['path'])==rec['sha256']
 actual=json.loads((H/'COMBINED-TEST-PROVENANCE.json').read_text())
 assert actual['status']=='PASS' and actual['test_count']==134 and actual['execution_count']==1
 assert actual['provenance']['control']['sha']==P['control']['sha'] and actual['provenance']['request_sha256']==P['control']['request_sha256']
 assert actual['transcript_sha256']==sha(H/'COMBINED-FINAL-VALIDATE.txt')
 final_log=(H/'COMBINED-FINAL-VALIDATE.txt').read_text()
 assert 'Ran 134 tests in' in final_log and final_log.endswith('\nOK\n')
 for name in ('test_archive_only_prefix_exact_seal_and_collect_after_later_failure','test_compact_cap_omission_is_explicit_and_never_qualified','test_missing_required_structured_member_rejects_archive','test_mutated_structured_member_with_updated_entry_hash_still_rejects'):
  assert re.search(name+r'.* \.\.\. ok',final_log),name
 assert 660/actual['elapsed_seconds']>=1.5
 check=json.loads((H/'COMBINED-CHECK-SOURCE-TIMING.json').read_text());assert check['status']=='PASS' and check['provenance']==actual['provenance']
 assert check['transcript_sha256']==sha(H/'COMBINED-CHECK-SOURCE.txt')
 inv=json.loads((H/'INVARIANCE.json').read_text())
 before=ast.parse(subprocess.check_output(['git','-C',str(C),'show',P['frozen_control']+':ch8-s1-control/r5_campaign.py'],text=True));after=ast.parse((Q/'r5_campaign.py').read_text())
 def remainder(m):return ast.dump(ast.Module(body=[n for n in m.body if not isinstance(n,ast.FunctionDef) or n.name not in ('sealed','root_outcome')],type_ignores=[]))
 assert remainder(before)==remainder(after)
 for path in ('research/challenge-8/kani-k1/kani3300/ch8-s2/review-batch-r5',):
  subprocess.run(['git','-C','/root/verify-rust-std-kani3300-g0','diff','--exit-code','022b9893c693f5908d3c9fa2ffe22961bbf8d30b','--',path],check=True,capture_output=True)
 patches=[]
 for item in json.loads((H/'PATCHES.json').read_text()):
  assert sha(H/item['path'])==item['sha256'];patches.append(replay(S if item['path'].startswith('SOURCE') else C,item))
 ancestry=[shallow(C,P['control']['sha'],7,P['tool']['sha']),shallow(S,P['source']['sha'],5,P['source']['base']),shallow(T,P['tool']['sha'],2,P['tool']['sha'])]
 root=Path('/root/verify-rust-std-kani3300-g0');rel=str(old.relative_to(root))
 subprocess.run(['git','-C',str(root),'diff','--exit-code',P['frozen_package'],'--',rel],check=True,capture_output=True)
 subprocess.run(['git','-C',str(C),'diff','--check',P['frozen_control'],'HEAD'],check=True)
 dump('VALIDATION.json',{'state':'STATIC_COMBINED_DELTA_PASS','control':P['control'],'targeted_tests':tests,'targeted_test_count':7,'patch_replays':patches,'checkout_depths':ancestry,'workflow':result,'actual_commands':'BYTE_IDENTICAL','full130_timing':'INHERITED_PRIOR_OBJECT4e97; NOT_EXECUTED_ON_NEW_HEAD','actual134_final':actual,'prior_host_seconds':timing['elapsed_seconds'],'frozen530_packet':'UNCHANGED_GIT_OBJECT_DIFF','source_tool_campaign_caps':'UNCHANGED','runtime_delta':'portable structured seal functions only','native_compiler_CI':'NOT_RUN','proof_credit':'NONE'})
 print('STATIC_COMBINED_DELTA_PASS: 7 cap tests; actual134 final PASS; six exact replays; shallow7/5/2; frozen530/review022b unchanged')
if __name__=='__main__':main()
