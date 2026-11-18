#!/usr/bin/env python3
"""Exact r5 review package, static object reads only. No compiler/network/CI."""
import ast,hashlib,json,shutil,subprocess,sys
from pathlib import Path
H=Path(__file__).resolve().parent;OLD=H.with_name('batch-r4-r2');C=Path('/root/kani-ch8-s2-r5-package-w13');Q=C/'ch8-s1-control';S=Path('/root/verify-rust-std-ch8-s2-r4-r1-w13');T=Path('/root/kani-upstream-ch8-s1')
F='d33a0900da19d865f20ccaa76e1ee27065c5a671';CP='9e14e033f9ee31522b571c127609dcdff76d230b';G=Path('/root/verify-rust-std-kani3300-g0')
def git(repo,*a):return subprocess.check_output(['git','-C',str(repo),*a])
def text(repo,*a):return git(repo,*a).decode().strip()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,v):(H/n).write_text(json.dumps(v,indent=2)+'\n')
def ids(repo):
 assert not text(repo,'status','--porcelain=v1')
 return {'worktree':str(repo),'sha':text(repo,'rev-parse','HEAD'),'tree':text(repo,'rev-parse','HEAD^{tree}'),'parent':text(repo,'rev-parse','HEAD^')}
def inventory(repo,base,head):
 rows=[]
 for line in text(repo,'diff','--name-status',base,head).splitlines():
  status,path=line.split('\t');rec={'status':status,'path':path}
  for label,rev in [('base',base),('target',head)]:
   exists=subprocess.run(['git','-C',str(repo),'cat-file','-e',rev+':'+path],capture_output=True).returncode==0
   rec[label]={'blob':text(repo,'rev-parse',rev+':'+path),'sha256':hashlib.sha256(git(repo,'show',rev+':'+path)).hexdigest()} if exists else None
  rows.append(rec)
 return {'base':base,'target':head,'paths':rows}
def seal():
 files=sorted(p.name for p in H.iterdir() if p.is_file() and p.name not in ('PACKAGE-CONTENTS.json','MANIFEST.sha256'))
 dump('PACKAGE-CONTENTS.json',{'files':{n:sha(H/n) for n in files},'self_reference':'contents and manifest excluded; manifest covers contents'})
 (H/'MANIFEST.sha256').write_text(''.join(sha(H/n)+'  '+n+'\n' for n in sorted(files+['PACKAGE-CONTENTS.json'])))
def main():
 s=ids(S);c=ids(C);t=ids(T);oldpins=json.loads((OLD/'PINS.json').read_text());r=json.loads((Q/'CI-REQUEST.json').read_text());oldr=json.loads(git(C,'show',F+':ch8-s1-control/CI-REQUEST.json'))
 assert s['sha']==oldpins['source']['sha'] and s['tree']==oldpins['source']['tree'] and t['sha']==oldpins['tool']['sha'] and c['parent']==CP
 s.update(base=oldpins['source']['base'],derivation_source=s['sha']);c.update(base=CP,derivation_control=F,request_sha256=sha(Q/'CI-REQUEST.json'),workflow_sha256=sha(C/'.github/workflows/ch8-s2.yml'))
 inputs=json.loads((H/'INPUTS.json').read_text())
 pins={'schema':'ch8-s2-batch-r5-pins-v1','task_id':inputs['task'],'entry_g0':'cd5da9a56e145dfef0e14a78a5379659d1c77cd6','source':s,'control':c,'tool':t,
       'checkout_depths':{'control':7,'source':5,'tool':2},'frozen_package':'3cdec7455c52d93903a31e005c7e42204fa502e1','frozen_control':F,
       'plan_commit':'07d891b23ba65405920090de87ed7eec9730fec4','intake_commit':'5ca0641af6c5b588ae2a4257ccc0fe52df6a827a','W11_dependency':'RESOLVED_EXACT_INTAKE',
       'profile':r['profile'],'r5':r['r5'],'review14':'PENDING_NEW_R5_INDEPENDENT_REVIEW','dispatch_authority':'NONE',
       'gate_dependency':oldpins['gate_dependency'],'inherited_combined_review':'7c0a05d5bd85aeed14ea8579dd1f498152e04398',
       'native_compile':'NOT_RUN','actual_r5_roots':'NOT_RUN','proof_credit':'NONE','package_commit':'Containing ownpaths commit; self-reference excluded'}
 for n,v in [('PINS.json',pins),('IDENTITIES.json',pins),('SOURCE.json',s),('CONTROL.json',c),('PROFILE.json',{'profile':r['profile'],'r5':r['r5']})]:dump(n,v)
 shutil.copyfile(Q/'CI-REQUEST.json',H/'CI-REQUEST.json');shutil.copyfile(C/'.github/workflows/ch8-s2.yml',H/'WORKFLOW.yml')
 unchanged_keys=[k for k in oldr if k not in ('ci_payload_sha256','ci_changed_paths','control_reference','entry_g0','accounting_reference')]
 for k in unchanged_keys:assert r[k]==oldr[k],k
 maps=[]
 for n in ('SOURCE-MAP.json','ROOT-BINDINGS.json','CFG-PFC-MAP.json','CONTRACT-STACK-MAP.json','ORDINARY-STUB-CONTRACT-MAP.json','NAME-RESOLUTION-MAP.json','COPY-CORRESPONDENCE.json','MODEL-MAP.json'):
  shutil.copyfile(OLD/n,H/n);maps.append({'file':n,'sha256':sha(H/n),'from_package':pins['frozen_package'],'basis':'Same source/tool and unchanged canonical source/stub/PFC/model/oracle/cover fields; gate provider bytes identical; scheduling profile changes no source claim'})
 dump('MAP-PROVENANCE.json',maps)
 qualification=json.loads((OLD/'QUALIFICATION-ASSUMPTIONS.json').read_text())
 qualification['canonical_obligation_roots']=qualification['selected_roots']
 qualification['canonical_covers']=qualification['selected_covers']
 qualification['canonical_negative_oracles']=qualification['negative_oracles']
 qualification['selected_roots']=r['r5']['selected'];qualification['selected_covers']=16
 qualification['negative_oracles']={rid:value for rid,value in qualification['negative_oracles'].items() if rid in r['r5']['selected']}
 qualification['deferred_roots']={rid:'DEFERRED_NOT_SELECTED_TO_S3; UNKNOWN' for rid in r['r5']['deferred']}
 qualification['selected_assumed_roots']=['sort13_assumed']
 qualification['execution']='R5_NOT_RUN; source expectations and inherited model limits only'
 dump('QUALIFICATION-ASSUMPTIONS.json',qualification)
 dump('DERIVED-MAP-PROVENANCE.json',{'QUALIFICATION-ASSUMPTIONS.json':{'base_package':pins['frozen_package'],'base_sha256':sha(OLD/'QUALIFICATION-ASSUMPTIONS.json'),'current_sha256':sha(H/'QUALIFICATION-ASSUMPTIONS.json'),'delta':'Explicit selected9/16/5 vs canonical11/20/6 and deferred general32; no changed source/model/oracle claim'}})
 schedule=[]
 for rank,rid in enumerate(r['r5']['selected'],1):
  row=next(x for x in r['rows'] if x['id']==rid);schedule.append({'rank':rank,'id':rid,'selector':row['selector'],'mode':row['mode'],'assurance':row['assurance'],'expected':row['expected'],'covers':row['required_cover_count'],'source_binding':r['source_bindings'][rid],'oracle':row.get('oracle'),'group':'r5-'+rid,'child_seconds':600,'compile_inside_child_seconds':180,'worker_seconds':710,'slot_seconds':720,'publication_reserve_seconds':10,'rss_target_kib':6291456})
 dump('SCHEDULE-MAP.json',{'profile':r['profile'],'launch_order':schedule,'deferred':[{'id':rid,'reason':'DEFERRED_TO_S3_PROVED_LEAVES','outcome':'UNKNOWN','selected':False} for rid in r['r5']['deferred']],'selected':{'roots':9,'covers':16,'negatives':5,'positives':4},'full':{'roots':11,'covers':20,'negatives':6}})
 dump('CAP-MAP.json',{'r5':r['r5']['caps'],'canonical_legacy_budgets':r['budgets'],'setup_seconds':1800,'job_seconds':10800,'schedule_arithmetic':'9*720+180+240=6900 <7500 <7560 <8100','job_arithmetic':'1800+7560+900=10260 <=10800','RSS_scope':'LOCAL: non-atomic sampled PGID VmRSS, effective min6GiB/available-2GiB/outer12GiB; outer: sampled observed-owned PIDs, no strict tree/kernel/cgroup claim','clock':'Single monotonic campaign clock, cleanup alarm6660 and hard6900; no retries/resets; stock600 inner not full child extra budget'})
 files=[]
 for rel in text(C,'ls-tree','-r','--name-only',F,'--','ch8-s1-control').splitlines():
  before=git(C,'show',F+':'+rel);after=(C/rel).read_bytes();files.append({'path':rel,'frozen_sha256':hashlib.sha256(before).hexdigest(),'candidate_sha256':sha(C/rel),'status':'BYTE_IDENTICAL' if before==after else 'R5_CONTROL_OR_TEST_DELTA'})
 protected=['pack_evidence.py','rustc_diagnostics.py','test_rustc_diagnostics.py','rich_evidence.py','negative_oracle.py','binding_metadata.py','cfg_pfc.py','contract_stacks.py','ordinary_contracts.py','lexical_bindings.py','s2_correspondence.py','oracle_source.py','S2-SOURCE.json','ORACLE-SOURCES.json','test_r1403_lexical.py']
 for n in protected:assert (Q/n).read_bytes()==git(C,'show',F+':ch8-s1-control/'+n),n
 invariants=[]
 for file,oldname,newname in [('s2_policy.py','validate_request','validate_legacy_request'),('collect.py','collect','legacy_collect'),('check_package.py','fallback','legacy_fallback'),('check_package.py','build','build')]:
  a=ast.parse(git(C,'show',F+':ch8-s1-control/'+file).decode());b=ast.parse((Q/file).read_text());one=next(n for n in a.body if isinstance(n,ast.FunctionDef) and n.name==oldname);two=next(n for n in b.body if isinstance(n,ast.FunctionDef) and n.name==newname);two.name=oldname;assert ast.dump(one)==ast.dump(two),(file,oldname)
  invariants.append({'file':file,'legacy_function':oldname,'new_name':newname,'AST':'IDENTICAL_EXCEPT_NAME'})
 dump('RUNNER-INVARIANCE.json',{'reference':F,'candidate':c['sha'],'files':files,'protected_exact_bytes':protected,'legacy_functions':invariants,'legacy_yaml':'All former assertions retained in check_legacy_yaml, after explicit exact r5 normalization; no weakened scalar/cap/checkout guards','source_tool':'UNCHANGED','B01_B02':'UNCHANGED_PROTECTED_DECODER_DIAGNOSTIC_PACKER_CONTROLS'})
 records={};patches=[]
 for label,repo,obj in [('source',S,s),('control',C,c)]:
  for kind,base in [('DELTA',obj['derivation_'+label]),('PARENT',obj['parent']),('CANDIDATE',obj['base'] if label=='source' else t['sha'])]:
   name=label.upper()+'-'+kind+'.patch';(H/name).write_bytes(git(repo,'diff','--binary','--full-index',base,obj['sha']))
   patches.append({'path':name,'base':base,'target':obj['sha'],'target_tree':obj['tree'],'sha256':sha(H/name)})
   records[label+'_'+kind.lower()]=inventory(repo,base,obj['sha'])
 dump('PATCHES.json',patches);dump('FULL-INVENTORIES.json',records)
 changed=text(C,'diff','--name-only',F,'HEAD').splitlines();dump('CHANGED-FILES.json',{'source':[],'control':[{'path':path,'sha256':sha(C/path)} for path in changed]})
 dump('SOURCE-UNCHANGED.json',{'source':s,'tool':t,'dirty_source':text(S,'status','--porcelain=v1'),'delta_to_frozen':text(S,'diff','--name-only',oldpins['source']['sha'],'HEAD'),'source_compile':'NOT_RUN','runtime_model_domains_frames_oracles':'UNCHANGED'})
 dump('FIXTURE-INVENTORY.json',{str(f.relative_to(C)):sha(f) for f in sorted(Q.rglob('*')) if f.is_file() and (f.suffix=='.json' or 'fixtures' in f.parts)})
 print(json.dumps(pins,indent=2))
if __name__=='__main__':
 if '--seal' in sys.argv:seal()
 else:main()
