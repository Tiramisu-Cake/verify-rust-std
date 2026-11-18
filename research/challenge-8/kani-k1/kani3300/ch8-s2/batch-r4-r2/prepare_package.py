#!/usr/bin/env python3
"""Assemble exact integrated object package without dispatch or re-running suites."""
import ast,hashlib,json,os,shutil,subprocess,sys
from pathlib import Path
H=Path(__file__).resolve().parent;OLD=H.with_name('batch-r4-r1');C=Path('/root/kani-ch8-s2-r4-r2-final-w13');S=Path('/root/verify-rust-std-ch8-s2-r4-r1-w13');T=Path('/root/kani-upstream-ch8-s1');Q=C/'ch8-s1-control'
F='0e8c836857344866564e1423ad5d8d28bbc4106b';CP='9e14e033f9ee31522b571c127609dcdff76d230b';ENTRY='16a4f1d3e9ca438396d9226ea3d13ffaa88150fe'
def git(repo,*args,env=None):return subprocess.check_output(['git','-C',str(repo),*args],env=env)
def txt(repo,*args):return git(repo,*args).decode().strip()
def sha(data):return hashlib.sha256(data).hexdigest()
def dump(name,data): (H/name).write_text(json.dumps(data,indent=2)+'\n')
def identity(repo):
 assert not txt(repo,'status','--porcelain=v1')
 return {'worktree':str(repo),'sha':txt(repo,'rev-parse','HEAD'),'tree':txt(repo,'rev-parse','HEAD^{tree}'),'parent':txt(repo,'rev-parse','HEAD^')}
def inventory(repo,base,head):
 rows=[]
 for line in txt(repo,'diff','--name-status',base,head).splitlines():
  status,path=line.split('\t');rec={'status':status,'path':path}
  for label,rev in [('base',base),('target',head)]:
   exists=subprocess.run(['git','-C',str(repo),'cat-file','-e',rev+':'+path],capture_output=True).returncode==0
   rec[label]={'blob':txt(repo,'rev-parse',rev+':'+path),'sha256':sha(git(repo,'show',rev+':'+path))} if exists else None
  rows.append(rec)
 return {'base':base,'target':head,'paths':rows}
def seal():
 names=sorted(p.name for p in H.iterdir() if p.is_file() and p.name not in ('MANIFEST.sha256','PACKAGE-CONTENTS.json'))
 dump('PACKAGE-CONTENTS.json',{'files':{n:sha((H/n).read_bytes()) for n in names},'self_reference':'contents excludes itself and manifest; manifest includes contents'})
 (H/'MANIFEST.sha256').write_text(''.join(sha((H/n).read_bytes())+'  '+n+'\n' for n in sorted(names+['PACKAGE-CONTENTS.json'])))
def main():
 s=identity(S);c=identity(C);t=identity(T);oldpins=json.loads((OLD/'PINS.json').read_text());r=json.loads((Q/'CI-REQUEST.json').read_text());oldr=json.loads(git(C,'show',F+':ch8-s1-control/CI-REQUEST.json'))
 assert s['sha']=='bd62e54df1b4749154790aa3db3cc7978f547f75' and s['tree']=='dc2e7a7f258719a05c65bbb9b1e2c7f1e8271ac8' and c['parent']==CP
 s.update(base=oldpins['source']['base'],derivation_source=s['sha']);c.update(base=CP,derivation_control=F,request_sha256=sha((Q/'CI-REQUEST.json').read_bytes()),workflow_sha256=sha((C/'.github/workflows/ch8-s2.yml').read_bytes()))
 pins={'schema':'ch8-s2-batch-r4-r2-pins-v1','task_id':'task'+ENTRY,'entry_g0':ENTRY,'source':s,'control':c,'tool':t,'checkout_depths':{'control':7,'source':5,'tool':2},'frozen_package':'474e0b4209554bdd69c4303410192d2d472af4a2','frozen_control':F,'spent_GO':'6db728b62b62d6d98d683f3d2cf6fb824dd6cc68','gate_dependency':{'status':'APPROVED_EXACT_GATE_BYTES_INTEGRATED','R14-03':'CLOSED_GATE_ONLY','candidate_package':'4eccefc670602b58f25f9c55a27da2d844cdcf18','candidate_control':'0e97a487d8b7f8e8cbced5dbe2b6909c7150c695','patch_sha256':'1dfaf5a1fa2d748e81bea4093018eb65972d7cfc807e47c0d1f7ad39565f8cba','review':'ccb6a60731866bcc8fc6dd6e6cbdf4c2a9fd4653 APPROVE/CLOSED exact gate-only','review_commit':'ccb6a60731866bcc8fc6dd6e6cbdf4c2a9fd4653','integrated':True},'review14':'PENDING_SAME14_FINAL_DELTA_REVIEW','dispatch_authority':'NONE','native_compile':'NOT_RUN','causal_repair':'NOT_RUN','actual_causal_CI_unit':'UNKNOWN','proof_credit':'NONE','package_commit':'commit containing this file; self-reference excluded'}
 for n,v in [('PINS.json',pins),('IDENTITIES.json',pins),('SOURCE.json',s),('CONTROL.json',c)]:dump(n,v)
 shutil.copyfile(Q/'CI-REQUEST.json',H/'CI-REQUEST.json');shutil.copyfile(C/'.github/workflows/ch8-s2.yml',H/'WORKFLOW.yml')
 assert {k:r[k] for k in r if k not in ('entry_g0','control_reference','ci_payload_sha256','ci_changed_paths')}=={k:oldr[k] for k in oldr if k not in ('entry_g0','control_reference','ci_payload_sha256','ci_changed_paths')}
 for k in ('cfg_pfc_source_sha256','contract_stack_source_sha256','ordinary_contract_source_sha256','lexical_source_sha256','source_bindings','rows','variants','flags','budgets'):assert r[k]==oldr[k]
 inherited=[]
 for n in ('CFG-PFC-MAP.json','ORDINARY-STUB-CONTRACT-MAP.json','CONTRACT-STACK-MAP.json','NAME-RESOLUTION-MAP.json','COPY-CORRESPONDENCE.json','ROOT-BINDINGS.json','SOURCE-MAP.json','MODEL-MAP.json','QUALIFICATION-ASSUMPTIONS.json','ENVELOPE.json','SOURCE-DIAGNOSTIC-REFERENCE.json'):
  shutil.copyfile(OLD/n,H/n);inherited.append({'file':n,'sha256':sha((H/n).read_bytes()),'from_package':pins['frozen_package'],'basis':'Same source/tree and request source/row/policy/fixture fields; approved gate review ccb6 establishes baseline map EXACT unchanged77/8/11; inherited static maps, no new proof'})
 dump('MAP-PROVENANCE.json',inherited)
 invariant=[]
 for p in txt(C,'ls-tree','-r','--name-only',F,'--','ch8-s1-control').splitlines():
  before=git(C,'show',F+':'+p);after=(C/p).read_bytes()
  invariant.append({'path':p,'frozen_sha256':sha(before),'candidate_sha256':sha(after),'status':'BYTE_IDENTICAL' if before==after else 'REVIEWED_GATE_OR_TIMEOUT_POLICY_OR_TEST_OR_REQUEST_REBIND'})
 changed=txt(C,'diff','--name-only',F,'HEAD').splitlines()
 assert changed==['.github/workflows/ch8-s2.yml','ch8-s1-control/CI-REQUEST.json','ch8-s1-control/check_package.py','ch8-s1-control/lexical_bindings.py','ch8-s1-control/test_r1403_lexical.py','ch8-s1-control/test_s2.py']
 # All build/fallback/collector and diagnostic controls preserve exact bytes/AST.
 a=ast.parse(git(C,'show',F+':ch8-s1-control/check_package.py').decode());b=ast.parse((Q/'check_package.py').read_text())
 for name in ('build','fallback','control','check_scalar_types'):
  one=next(x for x in a.body if isinstance(x,ast.FunctionDef) and x.name==name);two=next(x for x in b.body if isinstance(x,ast.FunctionDef) and x.name==name)
  assert ast.dump(one)==ast.dump(two),name
 dump('RUNNER-INVARIANCE.json',{'reference':F,'candidate':c['sha'],'files':invariant,'check_package_exceptions':'check_yaml only; exact approved timeout caps/order/sum return186 plus exact integrated explicit Validate command; build/fallback/control/type checks AST-identical','B01_B02':'UNCHANGED','protected_runner_collector_packer_decoder':'BYTE_IDENTICAL','source':'UNCHANGED','gate':'R14-03 gate-only CLOSED ccb6; exact approved lexical/test bytes inherited; integration review PENDING'})
 records={}
 patches=[]
 for label,repo,obj in [('source',S,s),('control',C,c)]:
  for kind,base in [('DELTA',obj['derivation_'+label]),('PARENT',obj['parent']),('CANDIDATE',obj['base'] if label=='source' else t['sha'])]:
   name=label.upper()+'-'+kind+'.patch';data=git(repo,'diff','--binary','--full-index',base,obj['sha']);(H/name).write_bytes(data)
   patches.append({'path':name,'base':base,'target':obj['sha'],'target_tree':obj['tree'],'sha256':sha(data)})
   records[label+'_'+kind.lower()]=inventory(repo,base,obj['sha'])
 dump('PATCHES.json',patches);dump('FULL-INVENTORIES.json',records)
 dump('CHANGED-FILES.json',{'source':[],'control':[{'path':p,'sha256':sha((C/p).read_bytes())} for p in changed]})
 dump('SOURCE-UNCHANGED.json',{'source':s,'frozen_source_sha':oldpins['source']['sha'],'frozen_source_tree':oldpins['source']['tree'],'delta_paths':txt(S,'diff','--name-only',s['sha'],s['sha']).splitlines(),'dirty':txt(S,'status','--porcelain=v1'),'tool':t,'source_compilation':'NOT_RUN'})
 fixtures={}
 for p in sorted(Q.rglob('*')):
  if p.is_file() and (p.suffix=='.json' or 'fixtures' in p.parts):fixtures[str(p.relative_to(C))]=sha(p.read_bytes())
 dump('FIXTURE-INVENTORY.json',fixtures)
 dump('CONTROL-DELTA.json',{'reference':F,'target':c,'paths':changed,'gate_patch_integrated':True,'workflow_delta':'Validate timeout1 ->10min; explicit CI unittest list appends approved test_r1403_lexical.py','check_yaml_delta':'Exact timeout/order and final actual Validate command enforcement; sum177 ->186; no aggregate cap change','tests_delta':'test_s2: updated sum, redistribution/order/caps and mocked aggregate clock boundaries','request_delta':['entry_g0','control_reference','ci_changed_paths appends new approved regression module','ci_payload_sha256 for workflow/check_package/test_s2/lexical_bindings/test_r1403_lexical'],'CI_module_list':'explicit test_r1403_lexical.py included; actual integrated final Validate measured ONCE after final commit'})
 print(json.dumps(pins,indent=2))
if __name__=='__main__':
 if '--seal' in sys.argv:seal()
 else:main()
