#!/usr/bin/env python3
"""Assemble combined margin and portable-prefix review delta; preserve prior-object evidence."""
import ast,datetime,hashlib,json,shutil,subprocess,sys
from decimal import Decimal,ROUND_CEILING
from pathlib import Path
H=Path(__file__).resolve().parent;OLD=H.with_name('batch-r5');G=Path('/root/verify-rust-std-kani3300-g0');C=Path('/root/kani-ch8-s2-r5-r1-final-w13');Q=C/'ch8-s1-control'
F='4e97d370aba4adc480fcc3701b111d02658aa94d';FP='53008fd4de6bb5719fd232b1ddb7e875b5112012';CP='9e14e033f9ee31522b571c127609dcdff76d230b';ENTRY='a9cc91d717751d2047e13bc7570a95305f546fa7'
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
 changed=text(C,'diff','--name-only',F,'HEAD').splitlines();allowed=['.github/workflows/ch8-s2.yml','ch8-s1-control/CI-REQUEST.json','ch8-s1-control/check_package.py','ch8-s1-control/r5_campaign.py','ch8-s1-control/r5_profile.py','ch8-s1-control/test_r5.py','ch8-s1-control/test_s2.py'];assert changed==allowed
 r=json.loads((Q/'CI-REQUEST.json').read_text());oldr=json.loads(git(C,'show',F+':ch8-s1-control/CI-REQUEST.json'))
 assert {k:v for k,v in r.items() if k not in ('entry_g0','control_reference','ci_payload_sha256')}=={k:v for k,v in oldr.items() if k not in ('entry_g0','control_reference','ci_payload_sha256')}
 pins={'schema':'ch8-s2-batch-r5-r1-pins-v1','task_id':'task'+ENTRY,'entry_g0':ENTRY,'source':s,'control':c,'tool':t,
   'checkout_depths':{'control':7,'source':5,'tool':2},'frozen_package':FP,'frozen_control':F,'profile':r['profile'],'r5':r['r5'],
   'review14':'022b9893c693f5908d3c9fa2ffe22961bbf8d30b CHANGES_REQUIRED; SAME14_COMBINED_DELTA_PENDING','dispatch_authority':'NONE','full_suite_new_head':'COMBINED-FINAL-VALIDATE-TIMING.json',
   'timing_classification':'ACTUAL_FINAL_OBJECT; prior130 separately INHERITED_PRIOR_OBJECT','native_compile':'NOT_RUN','proof_credit':'NONE','package_commit':'Containing ownpaths commit; self-reference excluded',
   'changed_test_pins':{'test_s2.py':sha(Q/'test_s2.py'),'test_r5.py':sha(Q/'test_r5.py'),'cap_checks.py':sha(H/'cap_checks.py'),'CAP-TESTS.json':sha(H/'CAP-TESTS.json'),'CAP-TESTS.txt':sha(H/'CAP-TESTS.txt')},
   'cap_assertion_pins':{'r5_profile.py':sha(Q/'r5_profile.py'),'check_package.py':sha(Q/'check_package.py')}}
 for n,v in [('PINS.json',pins),('IDENTITIES.json',pins),('SOURCE.json',s),('CONTROL.json',c),('PROFILE.json',{'profile':r['profile'],'r5':r['r5'],'validate_minutes':11,'legacy_validate_minutes':10})]:dump(n,v)
 shutil.copyfile(Q/'CI-REQUEST.json',H/'CI-REQUEST.json');shutil.copyfile(C/'.github/workflows/ch8-s2.yml',H/'WORKFLOW.yml')
 inherited={}
 for src,dst in [('RELEASE-FINAL-VALIDATE-TIMING.json','PRIOR-OBJECT-VALIDATE-TIMING.json'),('RELEASE-TEST-PROVENANCE.json','PRIOR-OBJECT-TEST-PROVENANCE.json'),('RELEASE-FINAL-VALIDATE.txt','PRIOR-OBJECT-VALIDATE.txt'),('RELEASE-CHECK-SOURCE-TIMING.json','PRIOR-OBJECT-CHECK-SOURCE-TIMING.json')]:
  assert (OLD/src).read_bytes()==git(G,'show',FP+':'+str((OLD/src).relative_to(G)))
  shutil.copyfile(OLD/src,H/dst);inherited[dst]={'source_file':src,'source_package':FP,'sha256':sha(H/dst),'classification':'INHERITED_PRIOR_OBJECT'}
 dump('INHERITED-HOST-EVIDENCE.json',{'classification':'INHERITED_PRIOR_OBJECT','original_control':oldpins['control'],'new_control':c,'prior130_suite_executions_new_head':0,'new134_suite':'COMBINED-FINAL-VALIDATE-TIMING.json','files':inherited,'reason':'Prior130 timing remains prior-object only. Portable seal/service/test behavior changed, so separate actual final-object134 timing is mandatory.'})
 evidence=json.loads((H/'PRIOR-OBJECT-VALIDATE-TIMING.json').read_text());proof=json.loads((H/'PRIOR-OBJECT-TEST-PROVENANCE.json').read_text());assert proof['test_count']==130 and evidence['provenance']['control']['sha']==F
 host=Decimal(evidence['monotonic_end_ns']-evidence['monotonic_start_ns'])/Decimal(1000000000);assert host==Decimal(str(evidence['elapsed_seconds']))
 minimum=host*Decimal('1.5');minutes=int((minimum/Decimal(60)).to_integral_value(rounding=ROUND_CEILING));assert minutes==11
 margin={'status':'COMBINED_MARGIN_AND_PORTABLE_REPAIR','measurement_classification':'INHERITED_PRIOR_OBJECT','prior_package':FP,'prior_control':oldpins['control'],
  'prior_host_seconds':str(host),'prior_tests':130,'required_multiplier':'1.5','minimum_seconds_exact':str(minimum),'minimum_whole_minutes':minutes,
  'old_cap_seconds':600,'old_ratio':str(Decimal(600)/host),'new_cap_seconds':660,'new_ratio':str(Decimal(660)/host),'rounding':'ceil((403.420022367 *1.5)/60)=11',
  'full_suite_new_head':'COMBINED-FINAL-VALIDATE-TIMING.json','targeted_tests':'CAP-TESTS.json','workflow_maxima_minutes':{'prior':186,'new':187},
  'setup_step_maxima_seconds':{'prior':3120,'new':3180},'setup_aggregate_seconds':1800,'job_minutes':180,'proof_step_seconds':7560,'campaign_seconds':6900,
  'extra_step_maximum_is_budget_grant':False,'future_GitHub_duration':'UNKNOWN','future_timeout_absence':'NOT_CLAIMED','source_tool_schedule_caps':'UNCHANGED','runtime_delta':'portable structured seal only',
  'coverage':{'selected_roots':9,'covers':16,'exact_negatives':5,'deferred':['general32_assumed','general32_weak'],'full_inventory':'11/20/6'},
  'current_budget_reference_only':{'item2_used':10,'item2_cap':14,'total_used':39,'total_cap':43,'requested_extra3':'NOT_APPROVED','reservation':False}}
 dump('TIMEOUT-MARGIN.json',margin)
 # All bytes outside the exact seven-path combined repair remain frozen.
 invariant=[]
 for rel in text(C,'ls-tree','-r','--name-only',F,'--','ch8-s1-control').splitlines():
  if rel in allowed:continue
  assert (C/rel).read_bytes()==git(C,'show',F+':'+rel),rel
  invariant.append({'path':rel,'sha256':sha(C/rel),'status':'BYTE_IDENTICAL'})
 for filename,exception in [('r5_profile.py','validate_yaml'),('check_package.py','check_yaml')]:
  before=ast.parse(git(C,'show',F+':ch8-s1-control/'+filename).decode());after=ast.parse((Q/filename).read_text())
  def remainder(m):return ast.dump(ast.Module(body=[n for n in m.body if not isinstance(n,ast.FunctionDef) or n.name!=exception],type_ignores=[]))
  assert remainder(before)==remainder(after),filename
 before=ast.parse(git(C,'show',F+':ch8-s1-control/test_s2.py').decode());after=ast.parse((Q/'test_s2.py').read_text())
 changes=0
 for n in ast.walk(after):
  if isinstance(n,ast.Constant) and type(n.value) is int and n.value==187:n.value=186;changes+=1
 assert changes==1 and ast.dump(before)==ast.dump(after)
 before=ast.parse(git(C,'show',F+':ch8-s1-control/r5_campaign.py').decode());after=ast.parse((Q/'r5_campaign.py').read_text())
 def service_rest(m):return ast.dump(ast.Module(body=[n for n in m.body if not isinstance(n,ast.FunctionDef) or n.name not in ('sealed','root_outcome')],type_ignores=[]))
 assert service_rest(before)==service_rest(after)
 before=ast.parse(git(C,'show',F+':ch8-s1-control/test_r5.py').decode());after=ast.parse((Q/'test_r5.py').read_text())
 after.body=[n for n in after.body if not isinstance(n,ast.ClassDef) or n.name!='PortablePrefixTests']
 assert ast.dump(before)==ast.dump(after)
 dump('INVARIANCE.json',{'reference':F,'candidate':c,'allowed_changed_paths':allowed,'unchanged_files':invariant,
  'AST_except_r5_validate_yaml_and_check_yaml':'IDENTICAL','legacy_check_legacy_yaml':'BYTE/AST_BODY_UNCHANGED:10min/186','test_s2_delta':'Sole numeric expectation186->187; all other test AST identical',
  'actual_commands':'ALL_WORKFLOW_RUN_STRINGS_BYTE_IDENTICAL','full_test_module_list':'UNCHANGED_MODULE_LIST;134 tests including4 new portable tests','runtime_caps':r['r5']['caps']})
 patches=[];records={}
 for label,repo,obj in [('source',S,s),('control',C,c)]:
  for kind,base in [('DELTA',obj['derivation_'+label]),('PARENT',obj['parent']),('CANDIDATE',obj['base'] if label=='source' else t['sha'])]:
   n=label.upper()+'-'+kind+'.patch';(H/n).write_bytes(git(repo,'diff','--binary','--full-index',base,obj['sha']))
   patches.append({'path':n,'base':base,'target':obj['sha'],'target_tree':obj['tree'],'sha256':sha(H/n)});records[label+'_'+kind.lower()]=inventory(repo,base,obj['sha'])
 dump('PATCHES.json',patches);dump('FULL-INVENTORIES.json',records);dump('CHANGED-FILES.json',[{'path':n,'sha256':sha(C/n)} for n in changed])
 dump('SOURCE-UNCHANGED.json',{'source':s,'tool':t,'source_delta':text(S,'diff','--name-only',oldpins['source']['sha'],'HEAD'),'source_dirty':text(S,'status','--porcelain=v1'),'tool_dirty':text(T,'status','--porcelain=v1'),'source_runtime_code':'UNCHANGED','native_r5_r1':'NOT_RUN'})
 maps=[]
 for n in ('SOURCE-MAP.json','ROOT-BINDINGS.json','SCHEDULE-MAP.json','QUALIFICATION-ASSUMPTIONS.json'):
  shutil.copyfile(OLD/n,H/n);maps.append({'file':n,'sha256':sha(H/n),'from_package':FP,'classification':'UNCHANGED_REFERENCE; source/schedule/obligations unchanged'})
 dump('MAP-PROVENANCE.json',maps)
 property_map=json.loads((OLD/'PROPERTY-COVER-MAP.json').read_text())
 old_request=property_map['request_sha256'];property_map['request_sha256']=c['request_sha256']
 dump('PROPERTY-COVER-MAP.json',property_map)
 dump('DERIVED-MAP-PROVENANCE.json',{'PROPERTY-COVER-MAP.json':{'base_package':FP,'base_sha256':sha(OLD/'PROPERTY-COVER-MAP.json'),'current_sha256':sha(H/'PROPERTY-COVER-MAP.json'),'old_request_sha256':old_request,'new_request_sha256':c['request_sha256'],'delta':'Request digest only; source/property/cover expectations and all rows unchanged'}})
 dump('INPUTS.json',{'task_id':'task'+ENTRY,'owner':'20:45 combined margin + R14-R5-02 repair','task_document_sha256':sha(G/'research/challenge-8/kani-k1/TASK-CH8-S2-R5-VALIDATE-MARGIN-W13.md'),'frozen_package':FP,'frozen_control':oldpins['control'],'prior_host_timing':inherited,'review14':'022b9893c693f5908d3c9fa2ffe22961bbf8d30b CHANGES_REQUIRED; exact-final delta pending','Fast':'OFF_NOT_TOGGLED','settings':'PRESERVED','subagents':0})
 print('Combined package prepared',c['sha'],'ratio',margin['new_ratio'])
if __name__=='__main__':
 if '--seal' in sys.argv:seal()
 else:main()
