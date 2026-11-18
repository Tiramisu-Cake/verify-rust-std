#!/usr/bin/env python3
"""Assemble test-only deterministic process-fixture repair; never runs tests."""
import ast,datetime,hashlib,json,shutil,subprocess,sys
from decimal import Decimal,ROUND_CEILING
from pathlib import Path
H=Path(__file__).resolve().parent;OLD=H.with_name('batch-r5-r1');G=Path('/root/verify-rust-std-kani3300-g0');C=Path('/root/kani-ch8-s2-r5-r1-stable-final-w13');Q=C/'ch8-s1-control'
F='d67bd1ecd555030c46a06b8462d0313ea416711a';FP='dc8d28b0117737e95ccc9b91eb470c1a3c42a635';CP='9e14e033f9ee31522b571c127609dcdff76d230b';ENTRY='6d7c4739def196654459faf05b7e1c36ace03e93'
def git(repo,*a):return subprocess.check_output(['git','-C',str(repo),*a])
def text(repo,*a):return git(repo,*a).decode().strip()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,v):(H/n).write_text(json.dumps(v,indent=2)+'\n')
def identity(repo):
 assert not text(repo,'status','--porcelain=v1')
 return {'worktree':str(repo),'sha':text(repo,'rev-parse','HEAD'),'tree':text(repo,'rev-parse','HEAD^{tree}'),'parent':text(repo,'rev-parse','HEAD^')}
def inventory(repo,base,head):
 records=[]
 for line in text(repo,'diff','--name-status',base,head).splitlines():
  status,path=line.split('\t');rec={'status':status,'path':path}
  for label,rev in [('base',base),('target',head)]:
   exists=subprocess.run(['git','-C',str(repo),'cat-file','-e',rev+':'+path],capture_output=True).returncode==0
   rec[label]={'blob':text(repo,'rev-parse',rev+':'+path),'sha256':hashlib.sha256(git(repo,'show',rev+':'+path)).hexdigest()} if exists else None
  records.append(rec)
 return {'base':base,'target':head,'paths':records}
def seal():
 names=sorted(p.name for p in H.iterdir() if p.is_file() and p.name not in ('PACKAGE-CONTENTS.json','MANIFEST.sha256'))
 dump('PACKAGE-CONTENTS.json',{'files':{n:sha(H/n) for n in names},'self_reference':'contents and manifest excluded; manifest covers contents'})
 (H/'MANIFEST.sha256').write_text(''.join(sha(H/n)+'  '+n+'\n' for n in sorted(names+['PACKAGE-CONTENTS.json'])))
def main():
 oldpins=json.loads((OLD/'PINS.json').read_text());S=Path(oldpins['source']['worktree']);T=Path(oldpins['tool']['worktree']);s=identity(S);c=identity(C);t=identity(T)
 assert s['sha']==oldpins['source']['sha'] and s['tree']==oldpins['source']['tree'] and t['sha']==oldpins['tool']['sha'] and c['parent']==CP
 s.update(base=oldpins['source']['base'],derivation_source=s['sha']);c.update(base=CP,derivation_control=F,request_sha256=sha(Q/'CI-REQUEST.json'),workflow_sha256=sha(C/'.github/workflows/ch8-s2.yml'))
 changed=text(C,'diff','--name-only',F,'HEAD').splitlines();allowed=['.github/workflows/ch8-s2.yml','ch8-s1-control/CI-REQUEST.json','ch8-s1-control/check_package.py','ch8-s1-control/r5_profile.py','ch8-s1-control/test_r5.py','ch8-s1-control/test_s2.py'];assert changed==allowed
 oldr=json.loads(git(C,'show',F+':ch8-s1-control/CI-REQUEST.json'));r=json.loads((Q/'CI-REQUEST.json').read_text())
 assert {k:v for k,v in r.items() if k not in ('entry_g0','control_reference','ci_payload_sha256')}=={k:v for k,v in oldr.items() if k not in ('entry_g0','control_reference','ci_payload_sha256')}
 assert r['entry_g0']==ENTRY and r['control_reference']==F
 payload_changes=[n for n in r['ci_payload_sha256'] if r['ci_payload_sha256'][n]!=oldr['ci_payload_sha256'][n]];assert payload_changes==['.github/workflows/ch8-s2.yml','ch8-s1-control/check_package.py','ch8-s1-control/r5_profile.py','ch8-s1-control/test_s2.py','ch8-s1-control/test_r5.py'] or set(payload_changes)==set(allowed)-{'ch8-s1-control/CI-REQUEST.json'}
 # R5 cap12 is required by measured precursor440.727s; all run strings unchanged.
 # Whole-tree exactness: only the test and its request binding changed.
 invariant=[]
 for rel in text(C,'ls-tree','-r','--name-only',F,'--','ch8-s1-control').splitlines():
  if rel in allowed:continue
  assert (C/rel).read_bytes()==git(C,'show',F+':'+rel),rel
  invariant.append({'path':rel,'sha256':sha(C/rel),'status':'BYTE_IDENTICAL'})
 before=ast.parse(git(C,'show',F+':ch8-s1-control/test_r5.py').decode());after=ast.parse((Q/'test_r5.py').read_text())
 new_names={'escaped_case','assert_escaped_cleanup','test_escaped_child_adopted_after_early_snapshot','test_escaped_fixture_missing_ready_cleans_child'}
 for node in after.body:
  if isinstance(node,ast.ClassDef) and node.name=='ProcessTests':
   node.body=[x for x in node.body if not isinstance(x,ast.FunctionDef) or x.name not in new_names]
   prior=next(x for x in before.body if isinstance(x,ast.ClassDef) and x.name=='ProcessTests')
   original=next(x for x in prior.body if isinstance(x,ast.FunctionDef) and x.name=='test_escaped_setsid_child_found_and_reaped')
   node.body=[original if isinstance(x,ast.FunctionDef) and x.name==original.name else x for x in node.body]
 assert ast.dump(before)==ast.dump(after)
 for filename,func in [('r5_profile.py','validate_yaml'),('check_package.py','check_yaml')]:
  beforecap=ast.parse(git(C,'show',F+':ch8-s1-control/'+filename).decode());aftercap=ast.parse((Q/filename).read_text())
  def rest(m):return ast.dump(ast.Module(body=[n for n in m.body if not isinstance(n,ast.FunctionDef) or n.name!=func],type_ignores=[]))
  assert rest(beforecap)==rest(aftercap)
 beforecap=ast.parse(git(C,'show',F+':ch8-s1-control/test_s2.py').decode());aftercap=ast.parse((Q/'test_s2.py').read_text())
 for n in ast.walk(aftercap):
  if isinstance(n,ast.Constant) and type(n.value) is int and n.value==188:n.value=187
 assert ast.dump(beforecap)==ast.dump(aftercap)
 pins={'schema':'ch8-s2-r5-r1-stable-pins-v1','task_id':'task'+ENTRY,'entry_g0':ENTRY,'source':s,'control':c,'tool':t,'checkout_depths':{'control':7,'source':5,'tool':2},'frozen_package':FP,'frozen_control':F,'review14_prior':'2ed2c8ef2f6b9d6460494b85594e3a5f08387a7f APPROVE01/02; known test race recorded','review14_stable':'PENDING_SAME14_NARROW_DELTA','profile':r['profile'],'logical_GO_profile':'r5-r1','r5':r['r5'],'dispatch_authority':'NONE','native_compile':'NOT_RUN','proof_credit':'NONE','package_commit':'Containing ownpaths commit; self-reference excluded','test_pins':{'test_r5.py':sha(Q/'test_r5.py'),'cap_checks.py':sha(H/'cap_checks.py'),'TARGETED-TESTS.json':sha(H/'TARGETED-TESTS.json'),'TARGETED-TESTS.txt':sha(H/'TARGETED-TESTS.txt')}}
 for n,v in [('PINS.json',pins),('IDENTITIES.json',pins),('SOURCE.json',s),('CONTROL.json',c),('PROFILE.json',{'profile':r['profile'],'r5':r['r5'],'validate_minutes':12,'legacy_validate_minutes':10})]:dump(n,v)
 shutil.copyfile(Q/'CI-REQUEST.json',H/'CI-REQUEST.json');shutil.copyfile(C/'.github/workflows/ch8-s2.yml',H/'WORKFLOW.yml')
 dump('INVARIANCE.json',{'reference':F,'candidate':c,'allowed_changed_paths':allowed,'unchanged_files':invariant,'request_delta':'entry, control_reference and exact changed payload digests','all_production_service_runtime':'BYTE_IDENTICAL; exact-cap checker exception11->12/maxima187->188','workflow_command_module_list':'BYTE_IDENTICAL; only Validate cap11->12','test_AST_delta':'ProcessTests one fixture replaced;2 helpers/2 tests added; all other AST identical','runtime_caps':r['r5']['caps']})
 patches=[];records={}
 for label,repo,obj in [('source',S,s),('control',C,c)]:
  for kind,base in [('DELTA',obj['derivation_'+label]),('PARENT',obj['parent']),('CANDIDATE',obj['base'] if label=='source' else t['sha'])]:
   n=label.upper()+'-'+kind+'.patch';(H/n).write_bytes(git(repo,'diff','--binary','--full-index',base,obj['sha']))
   patches.append({'path':n,'base':base,'target':obj['sha'],'target_tree':obj['tree'],'sha256':sha(H/n)});records[label+'_'+kind.lower()]=inventory(repo,base,obj['sha'])
 dump('PATCHES.json',patches);dump('FULL-INVENTORIES.json',records);dump('CHANGED-FILES.json',[{'path':n,'sha256':sha(C/n)} for n in changed])
 dump('SOURCE-UNCHANGED.json',{'source':s,'tool':t,'source_delta':text(S,'diff','--name-only',s['sha'],'HEAD'),'source_dirty':text(S,'status','--porcelain=v1'),'tool_dirty':text(T,'status','--porcelain=v1'),'native_r5_r1_stable':'NOT_RUN'})
 maps=[]
 for n in ('SOURCE-MAP.json','ROOT-BINDINGS.json','SCHEDULE-MAP.json','QUALIFICATION-ASSUMPTIONS.json'):
  shutil.copyfile(OLD/n,H/n);maps.append({'file':n,'sha256':sha(H/n),'from_package':FP,'classification':'UNCHANGED_REFERENCE; source/schedule/obligations unchanged'})
 dump('MAP-PROVENANCE.json',maps)
 prop=json.loads((OLD/'PROPERTY-COVER-MAP.json').read_text());old_request=prop['request_sha256'];prop['request_sha256']=c['request_sha256'];dump('PROPERTY-COVER-MAP.json',prop)
 dump('DERIVED-MAP-PROVENANCE.json',{'base_package':FP,'old_request_sha256':old_request,'new_request_sha256':c['request_sha256'],'PROPERTY-COVER-MAP.json':{'base_sha256':sha(OLD/'PROPERTY-COVER-MAP.json'),'current_sha256':sha(H/'PROPERTY-COVER-MAP.json'),'delta':'Request digest only; all rows and source/property/cover expectations unchanged'}})
 inherited=[]
 for n in ('COMBINED-FINAL-VALIDATE-TIMING.json','COMBINED-TEST-PROVENANCE.json','COMBINED-FINAL-VALIDATE.txt','COMBINED-CHECK-SOURCE-TIMING.json'):
  assert (OLD/n).read_bytes()==git(G,'show',FP+':'+str((OLD/n).relative_to(G)))
  dst='PRIOR-OBJECT-'+n;shutil.copyfile(OLD/n,H/dst);inherited.append({'file':dst,'source_file':n,'sha256':sha(H/dst),'classification':'INHERITED_PRIOR_OBJECTd67_134PASS409.026897886s; not execution on stable head'})
 dump('INHERITED-HOST-EVIDENCE.json',{'prior_package':FP,'prior_control':oldpins['control'],'files':inherited,'prior_full_tests':134,'prior_host_seconds':409.026897886,'new_final_measurement':'STABLE-FINAL-VALIDATE-TIMING.json','inheritance_limit':'test behavior changed; stable actual timing required'})
 review=H.with_name('review-batch-r5-r1');reviewcommit='2ed2c8ef2f6b9d6460494b85594e3a5f08387a7f';reviews=[]
 for n in ('REPORT.md','PROCESS-DIAGNOSTIC.json','diagnose_process.py','TARGETED-TESTS.json','TARGETED-TESTS.txt'):
  assert (review/n).read_bytes()==git(G,'show',reviewcommit+':'+str((review/n).relative_to(G)))
  dst='PRIOR-REVIEW-'+n;shutil.copyfile(review/n,H/dst);reviews.append({'file':dst,'source_file':n,'sha256':sha(H/dst)})
 dump('REVIEW-INPUTS.json',{'commit':reviewcommit,'verdict':'APPROVE_R14-R5-01+02_CLOSED_ONd67','targeted':'34tests33PASS1FAIL','isolated_repeat':'1FAIL; early orphan[] assertion','files':reviews,'stable_review':'PENDING_SAME14_NARROW_DELTA'})
 dump('INPUTS.json',{'task':'task'+ENTRY,'task_document_sha256':sha(G/'research/challenge-8/kani-k1/TASK-CH8-S2-R5-TEST-STABILITY-W13.md'),'owner':'21:22 option(b) test deterministic and retain CI','frozen_package':FP,'frozen_control':F,'review_commit':reviewcommit,'prior_failures':'PRESERVED_IN_PRIOR-REVIEW_FILES','Fast':'OFF_NOT_TOGGLED','settings':'PRESERVED','subagents':0,'current_budget_reference_only':'item1 29/30,item2 10/17,total39/47; no accounting writes'})
 dump('AUDIT.json',{'control':c,'workflow_step_sum_minutes':188,'setup_step_maxima_seconds':3240,'binding_setup_aggregate_seconds':1800,'job_minutes':180,'proof_step_seconds':7560,'campaign_seconds':6900,'validate_minutes':12,'legacy_validate_minutes':10,'runtime_resource_caps':r['r5']['caps'],'RSS_scope':'sampled PGID; not strict root/tree/kernel/cgroup','selected_roots_covers_negatives':'9/16/5','deferred':'general32 pair toS3','full_inventory':'11/20/6','native_compiler_CI':'NOT_RUN','proof_credit':'NONE','dispatch':'NONE'})
 print('Stable package with necessary margin exception assembled',c['sha'])
if __name__=='__main__':
 if '--seal' in sys.argv:seal()
 else:main()
