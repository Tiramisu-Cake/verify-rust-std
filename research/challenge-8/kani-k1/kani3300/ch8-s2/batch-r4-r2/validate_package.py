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
 repos={k:Path(P[k]['worktree']) for k in ('source','control','tool')};S,C,T=(repos[k] for k in ('source','control','tool'));Q=C/'ch8-s1-control'
 for key,repo in repos.items():
  for field,rev in [('sha','HEAD'),('tree','HEAD^{tree}'),('parent','HEAD^')]:assert git(repo,'rev-parse',rev)==P[key][field]
  assert not git(repo,'status','--porcelain=v1')
  subprocess.run(['git','-C',str(repo),'diff','--check',P[key]['parent'],'HEAD'],check=True)
 r=json.loads((Q/'CI-REQUEST.json').read_text());assert sha(Q/'CI-REQUEST.json')==P['control']['request_sha256']
 assert sha(C/'.github/workflows/ch8-s2.yml')==P['control']['workflow_sha256']
 assert (H/'CI-REQUEST.json').read_bytes()==(Q/'CI-REQUEST.json').read_bytes()
 assert (H/'WORKFLOW.yml').read_bytes()==(C/'.github/workflows/ch8-s2.yml').read_bytes()
 paths=git(C,'diff','--name-only',P['tool']['sha'],'HEAD').splitlines();assert paths==r['ci_changed_paths']
 assert set(r['ci_payload_sha256'])=={p for p in paths if (C/p).is_file()}-{'ch8-s1-control/CI-REQUEST.json'}
 for p,digest in r['ci_payload_sha256'].items():assert sha(C/p)==digest,p
 for field in ('changed_file_sha256','cfg_pfc_source_sha256','contract_stack_source_sha256','ordinary_contract_source_sha256','lexical_source_sha256'):
  for p,digest in r[field].items():assert sha(S/p)==digest,p
 for n in ('S2-SOURCE.json','ORACLE-SOURCES.json'):
  assert (Q/n).read_bytes()==subprocess.check_output(['git','-C',str(C),'show',P['frozen_control']+':ch8-s1-control/'+n])
 fixtures=json.loads((Q/'S2-SOURCE.json').read_text())
 for p,data in fixtures.items():assert (S/p).read_text()==data,p
 for p,digest in json.loads((H/'FIXTURE-INVENTORY.json').read_text()).items():assert sha(C/p)==digest
 integration=json.loads((H/'GATE-INTEGRATION.json').read_text())
 assert integration['review_commit']==P['gate_dependency']['review_commit']
 for p,digest in integration['exact_inherited_files'].items():
  assert sha(C/p)==digest
  data=subprocess.check_output(['git','-C',str(C),'show',P['gate_dependency']['candidate_control']+':'+p])
  assert (C/p).read_bytes()==data
 review=H.with_name('r14-03-gate-backlog-review');root=Path('/root/verify-rust-std-kani3300-g0')
 data=subprocess.check_output(['git','-C',str(root),'show',integration['review_commit']+':'+str((review/'REPORT.json').relative_to(root))])
 report=json.loads(data);assert report['verdict']=='APPROVE' and report['finding']['status']=='CLOSED'
 assert report['patch']['sha256']==integration['patch_sha256']
 for record in json.loads((H/'MAP-PROVENANCE.json').read_text()):
  assert sha(H/record['file'])==record['sha256']
  assert (H/record['file']).read_bytes()==(H.with_name('batch-r4-r1')/record['file']).read_bytes()
 for n in ('CFG-PFC-MAP.json','NAME-RESOLUTION-MAP.json','ORDINARY-STUB-CONTRACT-MAP.json','CONTRACT-STACK-MAP.json'):
  x=json.loads((H/n).read_text());assert x['source_sha']==P['source']['sha'] and x['source_tree']==P['source']['tree']
  for p,digest in x['source_files_sha256'].items():assert sha(S/p)==digest
 for p,digest in json.loads((H/'SOURCE-MAP.json').read_text())['files'].items():assert sha(S/p)==digest
 assert len(r['rows'])==11 and sum(x['required_cover_count'] for x in r['rows'])==20 and sum('oracle' in x for x in r['rows'])==6
 assert P['gate_dependency']['integrated'] is True and P['gate_dependency']['R14-03']=='CLOSED_GATE_ONLY'
 assert (Q/'test_r1403_lexical.py').exists()
 assert (Q/'lexical_bindings.py').read_bytes()==subprocess.check_output(['git','-C',str(C),'show',P['gate_dependency']['candidate_control']+':ch8-s1-control/lexical_bindings.py'])
 timing={}
 for name in ('ACTUAL-CHECK-SOURCE','ACTUAL-FINAL-VALIDATE'):
  x=json.loads((H/(name+'-TIMING.json')).read_text());assert x['status']=='PASS' and x['exit_code']==0
  for k in repos:assert x['provenance'][k]['sha']==P[k]['sha'] and x['provenance'][k]['tree']==P[k]['tree']
  assert x['provenance']['request_sha256']==P['control']['request_sha256'] and x['provenance']['workflow_sha256']==P['control']['workflow_sha256']
  assert x['monotonic_end_ns']>x['monotonic_start_ns'] and x['elapsed_seconds']==(x['monotonic_end_ns']-x['monotonic_start_ns'])/1e9
  assert sha(H/(name+'.txt'))==x['transcript_sha256'];timing[name]=x
 proof=json.loads((H/'FINAL-TEST-PROVENANCE.json').read_text());assert proof['execution_count']==proof['check_source_execution_count']==1
 log=(H/'ACTUAL-FINAL-VALIDATE.txt').read_text();m=re.search(r'Ran ([0-9]+) tests in',log);assert m and int(m[1])==proof['test_count'] and log.endswith('\nOK\n')
 sys.path.insert(0,str(Q));import check_package
 wf=check_package.check_yaml(C/'.github/workflows/ch8-s2.yml')
 doc=check_package.load_yaml((C/'.github/workflows/ch8-s2.yml').read_text());steps={s['name']:s for s in doc['jobs']['s2_batch']['steps']}
 assert timing['ACTUAL-FINAL-VALIDATE']['command']==steps['Validate control and synthetic wrapper']['run']
 assert timing['ACTUAL-CHECK-SOURCE']['command']==steps['Check all source identities']['run']
 patches=[]
 for item in json.loads((H/'PATCHES.json').read_text()):
  assert sha(H/item['path'])==item['sha256'];patches.append(replay(S if item['path'].startswith('SOURCE') else C,item))
 ancestry=[shallow(C,P['control']['sha'],7,P['tool']['sha']),shallow(S,P['source']['sha'],5,P['source']['base']),shallow(T,P['tool']['sha'],2,P['tool']['sha'])]
 parsed=[]
 for p in sorted(Q.glob('*.py')):ast.parse(p.read_text());parsed.append(p.name)
 # Old packets are immutable; concurrent new reviewer directory is intentionally outside this scope.
 frozen=[]
 for name,rev in [('batch-r4-r1',P['frozen_package']),('r14-03-gate-backlog',P['gate_dependency']['candidate_package'])]:
  directory=H.with_name(name);root=Path('/root/verify-rust-std-kani3300-g0');rel=str(directory.relative_to(root));paths=git(root,'ls-tree','-r','--name-only',rev,'--',rel).splitlines()
  for path in paths:assert (root/path).read_bytes()==subprocess.check_output(['git','-C',str(root),'show',rev+':'+path]),path
  frozen.append({'directory':name,'commit':rev,'files':len(paths),'status':'UNCHANGED_COMMITTED_BYTES'})
 dump('VALIDATION.json',{'state':'STATIC_OFFLINE_PASS_INTEGRATED_REVIEW_PENDING','workflow':wf,'patch_replays':patches,'checkout_depths':ancestry,'frozen_packets':frozen,'python_AST_files':parsed,'rows':11,'covers':20,'exact_negatives':6,'actual_final_validate':timing['ACTUAL-FINAL-VALIDATE'],'check_source':timing['ACTUAL-CHECK-SOURCE'],'test_count':proof['test_count'],'gate_dependency':P['gate_dependency'],'native_compile':'NOT_RUN','CI':'NOT_RUN','actual_causal_CI_unit':'UNKNOWN','proof_credit':'NONE'})
 print('PASS: final-object timings, request/payload/maps/fixtures, six patch replays, real shallow 7/5/2, frozen packets; no suite/source rerun')
if __name__=='__main__':main()
