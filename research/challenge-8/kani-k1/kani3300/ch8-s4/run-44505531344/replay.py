#!/usr/bin/env python3
"""Offline terminal reporting only; frozen reviewed readers, no native execution.
Reuses earlier intake helpers; never calls runner main or full Validate.
"""
import base64,collections,copy,gzip,hashlib,importlib,importlib.util,json,re,subprocess,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
G0=HERE.parents[5]
BASE='research/challenge-8/kani-k1/'
TASK='248cfebd4b3c6f433fd809656ea70041258fd69c'
BASE_TASK='be83c7b5b9a2e2110a7b3d9191b051ef487ca7cc'
HEAD='9c63491609f7d4c9dba9f9fbb4598b79625316d7'
CTRL='4059c900e50ba179d824a1e6f6bd7798cf343e36'
CONTROL=Path('/root/kani-ch8-s4p-2-r1-control-w13')
SOURCE=Path('/root/verify-rust-std-ch8-s4p-2-w13')
TOOL=Path('/root/kani-upstream-ch8-s1')
STD=Path('/home/runner/work/kani/kani/export')
CHECKS=[]
def sha(b):return hashlib.sha256(b).hexdigest()
def canon(v):return json.dumps(v,sort_keys=True,separators=(',',':')).encode()
def write(n,v):(HERE/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def git(repo,*args):return subprocess.check_output(['git','-C',str(repo),*args])
def blob(repo,rev,path):return git(repo,'show',rev+':'+path)
def need(v,label):
 if not v:raise AssertionError(label)
 CHECKS.append(label)
def pick(d,ks):return {k:d[k] for k in ks if k in d}
def decode(e):return e['text'].encode() if e.get('encoding','utf-8')=='utf-8' else base64.b64decode(e['text'],validate=True)
def located(p):return isinstance(p.get('file'),str) and bool(p['file']) and isinstance(p.get('line'),str) and re.fullmatch('[1-9][0-9]*',p['line']) is not None
def context(b,n):
 ls=b.decode().splitlines();return '\n'.join(f'{i+1}: {ls[i]}' for i in range(max(0,n-5),min(len(ls),n+4)))

def main():
 pins=json.loads(blob(G0,TASK,BASE+'kani3300/ch8-s4/postrun-s4p-2-terminal/INPUTS.json'))
 inherited=json.loads(blob(G0,BASE_TASK,BASE+'kani3300/ch8-s4/postrun-s4p-2/INPUTS.json'))
 need(inherited['expected_run']==pins['expected_run'],'base task exact native identity inherited')
 write('INPUTS.json',{'task_commit':TASK,'base_task':BASE_TASK,'terminal_inputs':pins,'base_inputs_sha256':sha(blob(G0,BASE_TASK,BASE+'kani3300/ch8-s4/postrun-s4p-2/INPUTS.json')),'authorization':'User14:23 explicitly/new14; one compact intake only; current high/FastOFF; no subagents/model changes','owned_path':str(HERE.relative_to(G0))})
 pins['package']={'g0':pins['author']['commit'],'path':pins['author']['path'],'manifest_sha256':pins['author']['manifest_sha256'],'source':dict(pins['source'],parents=[pins['source']['sole_parent']]),'tool':dict(pins['tool'],parents=[pins['tool']['sole_parent']]),'control':dict(pins['control_reviewed'],parents=[pins['control_reviewed']['sole_parent']])}
 pins['root_go']=dict(pins['rootGO'],g0=pins['rootGO']['commit'])
 pins['selection']={'ordered_rows':pins['ordered_rows']}
 run=json.loads((HERE/'github-run.json').read_bytes());jobs=json.loads((HERE/'github-jobs-detail.json').read_bytes())['jobs'];art=json.loads((HERE/'github-artifacts.json').read_bytes())['artifacts']
 for k in ['id','status','conclusion','head_sha','head_branch','event','run_attempt']:need(run[k]==pins['native_snapshot'][k],'connected native '+k)
 need(run['path']==pins['expected_run']['workflow_path'] and run['head_commit']['tree_id']==pins['expected_run']['tree'],'connected native workflow/tree')
 need(len(jobs)==1 and jobs[0]['head_sha']==HEAD and jobs[0]['run_attempt']==1 and jobs[0]['run_id']==run['id'] and jobs[0]['conclusion']=='failure','connected job/head/attempt failure')
 need(len(art)==1 and art[0]['digest']==pins['artifact']['metadata_digest'] and all(art[0][k]==pins['artifact'][k] for k in ['id','name','size_in_bytes','expired']),'connected artifact exact metadata digest first')
 integ=json.loads((HERE/'artifact-integrity.json').read_bytes());gz=(HERE/'group-evidence.json.gz').read_bytes();raw=gzip.decompress(gz);packet=json.loads(raw)
 need(integ['bytes']==art[0]['size_in_bytes'] and 'sha256:'+integ['sha256']==art[0]['digest'] and integ['digest_checked_before_zip_open'] and not integ['transport_saved'],'transport metadata digest checked before bounded memory-only member access')
 need(sha(gz)==integ['payload_sha256'] and sha(raw)==integ['uncompressed_sha256'],'separate transport/member/uncompressed digests')
 need(packet['state']=='PACKAGED' and packet['error'] is None and packet['schema']=='ch8-s1-05-artifact-v1','compact complete packaging')
 members={};data={}
 for n,e in packet['files'].items():
  p=Path(n);need(not p.is_absolute() and '..' not in p.parts and '\\' not in n and p.suffix=='.json','structured member path '+n)
  b=decode(e);need(len(b)==e['bytes'] and sha(b)==e['sha256'],'member hash/bytes '+n);members[n]=b;data[n]=json.loads(b)
 need(len(data)==119,'all119 structured members present')
 trees={}
 for kind,repo,rev,expected in [('source',SOURCE,pins['package']['source']['sha'],pins['package']['source']),('tool',TOOL,pins['package']['tool']['sha'],pins['package']['tool']),('control',CONTROL,CTRL,pins['package']['control']),('trigger',CONTROL,HEAD,pins['expected_run'])]:
  v={'sha':rev,'tree':git(repo,'rev-parse',rev+'^{tree}').decode().strip(),'sole_parent':git(repo,'show','-s','--format=%P',rev).decode().strip()};trees[kind]=v
  need(v['tree']==expected['tree'] and v['sole_parent']==expected['parents'][0],kind+' exact Git tree/sole parent')
 need(trees['control']['tree']==trees['trigger']['tree'] and CTRL!=HEAD,'same-tree nonskip sibling head, not reviewed control child')
 rb=blob(CONTROL,HEAD,'ch8-s1-control/CI-REQUEST.json');req=json.loads(rb);rh=sha(rb);wf=blob(CONTROL,HEAD,'.github/workflows/ch8-s2.yml')
 need(rh==pins['request']['sha256'] and rb==blob(CONTROL,CTRL,'ch8-s1-control/CI-REQUEST.json'),'exact executed reviewed request')
 need(sha(wf)==pins['request']['workflow_sha256'] and wf==blob(CONTROL,CTRL,'.github/workflows/ch8-s2.yml'),'exact executed reviewed workflow depths7/5/2')
 need(len(req['ci_payload_sha256'])==137,'all137 exact control payload hashes')
 for p,h in req['ci_payload_sha256'].items():need(sha(blob(CONTROL,HEAD,p))==h and blob(CONTROL,HEAD,p)==blob(CONTROL,CTRL,p),'control payload '+p)
 sourcefiles={}
 for key in ['changed_file_sha256','cfg_pfc_source_sha256','contract_stack_source_sha256','lexical_source_sha256','ordinary_contract_source_sha256']:
  for p,h in req[key].items():need(sha(blob(SOURCE,req['std_sha'],p))==h,'source hash '+key+' '+p);sourcefiles[p]=h
 need(req['s3']['caps']==pins['caps'],'all caps frozen; flags bound by exact request hash')
 order=pins['selection']['ordered_rows'];need([r['id'] for r in req['rows']]==order and all(r['mode']=='Original' and r['target'] is None for r in req['rows']),'all8 ordered Original/null targets')
 need(data['campaign-start.json']['request_data']==req and data['receipt.json']['request_sha256']==rh,'same-invocation embedded request')
 need(data['baseline.json']['control']=={'sha':HEAD,'tree':pins['expected_run']['tree'],'parent':pins['expected_run']['parents'][0],'dirty':''},'actual native checkout control head/tree/parent/clean')
 deps=[]
 for label,key in [('author','package'),('review','independent_review'),('GO','root_go')]:
  pin=pins[key];prefix=BASE+pin['path']+'/'
  names=git(G0,'ls-tree','-r','--name-only',pin['g0'],prefix).decode().splitlines()
  needed=[p for p in names if p.endswith(('/MANIFEST.sha256','/MANIFEST.json','/CHECKPOINT.json','/FINDINGS.json','/ROOT-RECHECK.json','/PINS.json'))]
  deps.append({'kind':label,'commit':pin['g0'],'pin':pin,'files':{p:sha(blob(G0,pin['g0'],p)) for p in needed}})
 domains=req['domains'];domain_doc=json.loads(blob(G0,pins['package']['g0'],BASE+pins['package']['path']+'/DOMAIN-UNWIND.json'))
 need(domain_doc['domains']==domains,'exact reviewed domain/unwind binding')
 planned_asserts=sum(x['class']=='assertion' for r in req['rows'] for x in r['roles']);planned_covers=sum(r['required_cover_count'] for r in req['rows'])
 need((planned_asserts,planned_covers)==(21,21),'21 source assertion /21 cover sites distinct from native counts')
 old_helper=G0/(BASE+'kani3300/ch8-s3-s4/run-44460583125/replay.py');need(old_helper.read_bytes()==blob(G0,TASK,str(old_helper.relative_to(G0))),'reused U helper exact task-commit bytes');spec=importlib.util.spec_from_file_location('prior_intake_helpers',old_helper);old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
 frozen={};roots=[];qual=[];cost=[];us=[];gaps=[];epochs=[];properties={};tests=[];cases=[]
 with tempfile.TemporaryDirectory(prefix='s4p-intake-') as td:
  tmp=Path(td);reader=tmp/'reader';reader.mkdir()
  for n in git(CONTROL,'ls-tree','-r','--name-only',CTRL,'ch8-s1-control').decode().splitlines():
   rel=Path(n).relative_to('ch8-s1-control');b=blob(CONTROL,CTRL,n);p=reader/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);frozen[str(rel)]={'sha256':sha(b),'bytes':len(b)}
  sys.path.insert(0,str(reader));r=importlib.import_module('runner');c=importlib.import_module('s4p2_campaign');ev=importlib.import_module('s3_evidence');rich=importlib.import_module('rich_evidence');policy=importlib.import_module('s4p2_policy');public=importlib.import_module('collect')
  need(r.load_request()==req,'frozen actual request loader')
  static=policy.validate_source(SOURCE,req);write('SOURCE-GATES.json',{'status':static['status'],'canonical_sha256':sha(canon(static)),'reports':static['reports'],'scope':'Source-only exact reviewed static gates; no compiler/full Validate','proof_credit':'NONE'})
  local=tmp/'materialized';upload=tmp/'upload';local.mkdir();upload.mkdir()
  for n,b in members.items():p=local/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
  (upload/'group-evidence.json.gz').write_bytes(gz)
  terminal=data['receipt.json'];need(type(terminal['schema']) is str and terminal['schema']=='ch8-s4p-2-campaign-v1' and type(terminal['s3_campaign']['selected_roots']) is int and terminal['s3_campaign']['selected_roots']==8,'exact realstr terminal schema/genuine int8 before collection')
  left=c.collect([local],req);right=public.collect([upload],req);need(left==right,'fresh local/public upload-only collectors agree')
  seals=c.sealed(local);need(list(seals)==order,'all8 ordered durable completion seals and member hashes')
  prefix_checks=[]
  for count in range(9):
   local_prefix=c.sealed(local,ids=order[:count]);uploaded_prefix=c.sealed(upload,reader=public.read_bytes,ids=order[:count])
   need(list(local_prefix)==order[:count] and local_prefix==uploaded_prefix,'authenticated prefix0..8 local/upload sealed replay '+str(count));prefix_checks.append({'count':count,'local_upload_equal':True,'scope':'Prefix seal reader on authentic same-run members; not invented shortened campaign terminal'})
  need(terminal['state']=='SELECTED_PARTIAL' and terminal['stop_reason'] is None and not right['global_stop'] and not right['selected_missing_groups'],'SELECTED_PARTIAL no global stop/no missing selected groups')
  write('PREFIX.json',{'state':terminal['state'],'selected_roots':8,'completed_prefix':list(seals),'local_upload_equal':True,'global_stop':False,'selected_missing_groups':[],'collector':right,'completion_is_not_qualification':True,'prefix0_to8_checks':prefix_checks,'unselected':terminal['s3_campaign']['unselected']})
  for rank,row in enumerate(req['rows'],1):
   rid=row['id'];selector=row['selector'];gp='groups/s3-'+rid+'/'
   g=data[gp+'receipt.json'];co=data[gp+'compile/receipt.json'];can=data[rid+'/receipt.json'];sup=data['workers/'+rid+'-supervision.json'];life=data['workers/'+rid+'-lifecycle.json'];launch=data['workers/'+rid+'-launch.json'];stock=data[gp+'export.json'];pr=data[gp+'properties.json'];bm=data[gp+'binding-metadata.json'];execution=g['execution'];hs=stock.get('harnesses',[]);h=hs[0] if hs else {};props=pr.get('harnesses',[{'properties':[]}])[0]['properties'];binding=req['source_bindings'][rid]
   need(ev.provenance(g,co,req,rid,rh),rid+' all-state source/compile provenance')
   prot=ev.protected(g,req,data['baseline.json'],sup,rh);need(not prot['observed_errors_ignored'],rid+' all-state protected reader')
   need(c.snapshots.validate_pair(data['baseline.json'],life['pre'],life['post'],life['context']),rid+' all-state controller epochs')
   need(g['argv']==r.build_argv(STD,Path('/home/runner/work/kani/kani/tool'),[selector],row['unwind'],Path('/home/runner/work/_temp/ch8-s1-receipts')/(gp+'export.json')) and g['selectors']==[selector] and g['unwind']==row['unwind'],rid+' exact fresh singleton argv/selector/unwind')
   mem=g['memory'];ceff=min(pins['caps']['local_rss_kib'],pins['caps']['outer_rss_kib'],mem['available_kib']-pins['caps']['headroom_kib'])
   need(g['timeout_seconds']==g['group_budget_seconds']==600 and g['compile_limit_seconds']==180 and g['phase_limited'] is False and mem['group_cap_kib']==ceff==6291456 and mem['reserve_kib']==2097152,rid+' observed effective cap/availability and600 child/180 compile')
   need(launch['context']['root']==rid and launch['context']['rank']==rank and launch['context']['epoch']=='E'+str(rank),rid+' launch order/context')
   need(g['effective_cfg']==req['flags']['RUSTFLAGS'] and g['native_start_verified'] and [x['selector'] for x in g['native_start_events']]==[selector],rid+' actual cfg/native singleton start')
   need(g['cargo_target_dir']==str(STD/'target/ch8-s1-cargo'/g['invocation_id']),rid+' fresh invocation namespace')
   need(bm['invocation_id']==g['invocation_id'] and bm['request_sha256']==rh and bm['std_sha']==req['std_sha'] and bm['tool_sha']==req['tool_sha'] and bm['argv']==g['argv'],rid+' actual metadata request/source/tool/invocation/argv')
   for a in bm['artifacts']:need(sha(members[gp+a['path']])==a['sha256'] and len(members[gp+a['path']])==a['bytes'],rid+' bound export '+a['path'])
   stages={'E0':data['baseline.json']['binaries'],'pre':life['pre']['binaries'],'worker.BEFORE':g['tool_fingerprints_before'],'worker.AFTER':g['tool_fingerprints_after'],'controller.post':life['post']['binaries']}
   for label,snap in stages.items():need(r.fingerprints_match(data['baseline.json']['binaries'],snap),rid+' binary '+label)
   epochs.append({'id':rid,'context':life['context'],'stages':stages,'all_five_equal_E0':True,'protected':prot,'lifecycle':life})
   need(execution['child_shutdown_verified'] and sup['worker_exit']==0 and sup['containment']['verified'] and not sup['cutoff'] and not sup['limit_initiated'] and sup['supervisor_error'] is None and not sup['orphan_survivors_at_worker_exit'],rid+' shutdown/owned-group/reap/safe serial continuation')
   regs=[];providers=[]
   for m in bm['native_metadata']:
    if m.get('state')!='CAPTURED':continue
    b=decode(m);need(len(b)==m['bytes'] and sha(b)==m['sha256'],rid+' native metadata hash '+m['path']);md=json.loads(b)
    regs.extend(dict(x,metadata_path=m['path'],metadata_sha256=m['sha256']) for x in md.get('proof_harnesses',[]) if x['pretty_name']==selector)
    providers.extend(x for x in md.get('contracted_functions',[]) if selector in x.get('harnesses',[]))
   need(len(regs)==1,rid+' native registration singleton including partial')
   reg=regs[0];need(reg['original_file']==str(STD/binding['file']) and reg['crate_name']=='core' and reg['attributes']['kind']=='Proof' and binding['target'] is None and not providers,rid+' actual Original source/crate/nulltarget no contracted provider')
   need(reg['attributes']['stubs']==([{'original':'s2_swap_seam','replacement':'weak_swap'}] if rid=='sort13_weak' else []) and not reg['attributes']['verified_stubs'],rid+' exact permitted negative seam/no positive stubs')
   need(stock['schema_version']=='0.1.0' and stock['kani_commit']==req['tool_sha'] and stock['kani_commit_dirty'] is False and stock['target']=='x86_64-unknown-linux-gnu',rid+' stock schema/tool/target')
   need(stock['harness_selection']=={'requested_filters':[selector],'exact':True,'unmatched_filters':[],'matched_count':1} and stock['harness_timeout_s']==600,rid+' stock singleton selection/cap')
   literal=[]
   for role in row['roles']:
    b=blob(SOURCE,req['std_sha'],role['file']);need(sha(b)==role['source_sha256'] and b.decode().splitlines()[role['line']-1]==role['source_line'],rid+' literal source '+role['description'])
    matches=[p for p in props if p['description']==role['description']]
    ok=bool(matches) and all(p['class']==role['class'] and p['status']==role['status'] and p['file']==str(STD/role['file']) and p['line']==str(role['line']) for p in matches)
    need(ok if hs else not matches,rid+' observed role or explicit UNKNOWN '+role['description'])
    literal.append({'required':role,'native_matches':matches,'exact_match':ok,'assessment':'OBSERVED_EXACT' if ok else 'UNKNOWN_CENSORED_NO_COMPLETED_INVENTORY'})
   bad=[p for p in props if not located(p)];fail=[p for p in props if p['status']=='FAILURE'];u=[p for p in props if p['status']=='UNREACHABLE'];covers=[p for p in props if p['class']=='cover'];guards=[p for p in props if p['class']=='unsupported_construct'];rebound=None;rr='NO_COMPLETED_NATIVE_INVENTORY'
   if hs:
    need(len(hs)==1 and h['name']==selector,rid+' completed native singleton')
    rebound=r.validate_export_value(stock,row,source_binding=binding,std=STD,group_selectors=[selector]);need(rebound['outcome']=='RECORDED',rid+' frozen native export source/stage/target binding')
    dec=rich.RegularEvidence([selector],STD);dec.finished=True;dec.closed={selector};dec.records={selector:copy.deepcopy(props)}
    try:dec.validate(stock);rr='ACCEPT'
    except ValueError as exc:rr='REJECT '+str(exc)
    need((rr=='ACCEPT') if not bad else (rr=='REJECT rich metadata incomplete: file/line missing'),rid+' actual strict location reader outcome')
    need(len({p['id'] for p in props})==len(props)==h['n_properties']==h['checks']['total']+h['covers']['total'],rid+' complete native count/unique IDs/check-cover partitions')
    need(len(fail)==(1 if row['expected']=='DETECTED' else 0) and h['outcome']=={'kind':'COMPLETED','verdict':'FAILURE' if fail else 'SUCCESS'},rid+' intended failures only/native verdict')
    need(len(covers)==row['required_cover_count'] and set(p['description'] for p in covers)==set(row['required_cover_messages']) and all(p['status']=='SATISFIED' and located(p) for p in covers),rid+' all exact required length/feasible SAT covers located')
    need(all(p['status'] in ('SUCCESS','FAILURE','UNREACHABLE','SATISFIED') for p in props),rid+' no hidden unknown/error/undetermined property')
    need(len(guards)==len(h['unsupported_constructs']) and all(p['status']=='SUCCESS' and located(p) for p in guards),rid+' every unsupported guard retained including SUCCESS')
    need(not bad if rank<=4 else len(bad)==1 and bad[0]['id']==selector+'.unreachable.1' and bad[0]['display_id']==bad[0]['id'] and bad[0]['class']=='unreachable' and bad[0]['status']=='SUCCESS' and bad[0]['description']=='unreachable code' and 'file' in bad[0] and 'line' in bad[0] and bad[0]['file'] is None and bad[0]['line'] is None and bad[0]['location_display']=='library/core/src/lib.rs:0:0 in function '+selector,rid+' exact location cardinality/null keys/display')
    if rank>4:need(all(p['status']=='SUCCESS' and located(p) for p in props if p['class']=='unwind'),rid+' native unwind checks SUCCESS separately from source36 bound')
   else:need(stock['run_state']=='INCOMPLETE' and 'harnesses' not in stock and not props and pr['state']=='INCOMPLETE' and execution.get('termination_reason')=='timeout',rid+' censored UNKNOWN inventory not NOT_RUN')
   strict=policy.expected_observation(row,rebound or {},{'name':selector,'properties':props})
   need(strict is False and can['s3_expected_match'] is False and seals[rid]['expected_match'] is False,rid+' original producer strict rejection unchanged')
   for p in u:
    rel=p['file'].split('/export/',1)[1];n=int(p['line']);b=blob(SOURCE,req['std_sha'],rel);arg,premises=old.uargument(rid,p)
    if rid=='s4p_cell_count_corrupt' and rel.endswith('sorting_model.rs') and n==118:arg='The snapshot is valid with L=2 from initialized logical Cell values [0,1]; post sees [0,0]. Outer i<L<=CAP32 increments at most32; i+1 is defined even after checker returns false.';premises=['Cell new/get/set logical u8 model enabled, no actual callee invoked. Count mismatch is the intended negative.']
    need(bool(arg) and located(p),rid+' U has individual source-local argument '+p['id'])
    us.append({'root':rid,'selector':selector,'invocation_id':g['invocation_id'],'namespace':g['cargo_target_dir'],'property':p,'member':gp+'properties.json','member_sha256':sha(members[gp+'properties.json']),'source_sha':req['std_sha'],'source_file':rel,'source_sha256':sha(b),'source_line':n,'source_context':context(b,n),'effective_cfg':g['effective_cfg'],'domain':domains.get(rid,'FIXED_NEGATIVE_FIXTURE'),'source_binding':binding,'native_registration':reg,'source_local_argument':arg,'premises':premises,'assessment':'SOURCE_LOCAL_DEFINEDNESS_ARGUMENT; not independent emitted-property proof','origin_assurance':'SOURCE_REPORTED site; AST/MIR/emitter/caller origin UNKNOWN','policy_status':'REJECT_ALL; proposal DISABLED; not admitted'})
   members_pin={n:{'member':gp+n,'sha256':sha(members[gp+n])} for n in ('receipt.json','compile/receipt.json','binding-metadata.json','export.json','properties.json')}
   gap={'root':rid,'selector':selector,'invocation_id':g['invocation_id'],'namespace':g['cargo_target_dir'],'observed_offending_records':bad if hs else 'UNKNOWN','observed_count':len(bad) if hs else 'UNKNOWN','class_unreachable_SUCCESS':[p for p in props if p['class']=='unreachable' and p['status']=='SUCCESS'] if hs else 'UNKNOWN','status_U_count':len(u) if hs else 'UNKNOWN','rich_state':pr['state'],'rich_error':pr['error'],'missing_sites':pr['missing_sites'],'actual_reader':rr,'location_exception_applied':False,'members':members_pin,'protected_epochs':'PROTECTED.json'};gaps.append(gap)
   q={'id':rid,'rank':rank,'selector':selector,'mode':row['mode'],'target':row['target'],'unwind':row['unwind'],'domain':domains.get(rid,'FIXED_NEGATIVE_FIXTURE'),'scope_classification':row['scope_classification'],'native_verdict':h.get('outcome',{}).get('verdict','UNKNOWN_INCOMPLETE_EXPORT'),'native_property_count':h.get('n_properties','UNKNOWN'),'status_counts':dict(collections.Counter(p['status'] for p in props)) if hs else 'UNKNOWN','class_status_counts':{cl:dict(collections.Counter(p['status'] for p in props if p['class']==cl)) for cl in sorted({p['class'] for p in props})} if hs else 'UNKNOWN','literal_roles':literal,'covers':covers if hs else 'UNKNOWN','unsupported_guards':guards if hs else 'UNKNOWN','native_unsupported_constructs':h.get('unsupported_constructs','UNKNOWN'),'U_count':len(u) if hs else 'UNKNOWN','failed_properties':fail if hs else 'UNKNOWN','missing_location':bad if hs else 'UNKNOWN','actual_rich_reader':rr,'native_registration':reg,'providers':providers,'binding':{'source_binding':binding,'native_metadata_state':bm['native_metadata_state'],'compiler_identity_status':bm['compiler_identity_status'],'gaps':bm['rows'],'flags':req['flags'],'effective_cfg':g['effective_cfg'],'init':'Source-written typed initialized values; no init-mask/dstinit theorem','caller':'Exact concrete family, backing34/base1/normal return frame only'},'producer':pick(can,['status','outcome','reason','s3_expected_match']),'strict_expected_match':False,'provisional_S1':'FIXED_NEGATIVE_EXACT_LABEL_OBSERVED' if rank<=4 else 'EXACT_BOUNDED_SOURCE_REPORTED_CANDIDATE_PENDING_LOCATION_AND_INDEPENDENT_REVIEW' if hs else 'INELIGIBLE_CENSORED_UNKNOWN','qualification_admitted':False,'eligible_as_init_leaf_or_provider_summary':False,'proof_credit':'NONE','members':members_pin}
   qual.append(q);properties[rid]={'selector':selector,'state':pr['state'],'properties':props if hs else 'UNKNOWN_CENSORED','member':gp+'properties.json','sha256':sha(members[gp+'properties.json'])}
   roots.append({'id':rid,'rank':rank,'selector':selector,'mode':row['mode'],'target':row['target'],'unwind':row['unwind'],'native_verdict':q['native_verdict'],'canonical_status':can['status'],'canonical_outcome':can['outcome'],'canonical_reason':can.get('reason'),'group_state':g['state'],'original_exception':g.get('original_exception'),'execution_exception':g.get('execution_exception'),'snapshot_errors':g.get('snapshot_errors'),'original_exit':execution['original_exit_code'],'signal':execution['signal'],'worker_exit':sup['worker_exit'],'sealed':True,'argv':g['argv'],'effective_cfg':g['effective_cfg'],'invocation_id':g['invocation_id'],'cargo_target_dir':g['cargo_target_dir'],'native_start_events':g['native_start_events'],'source_before':g['source_before'],'source_after':g['source_after'],'source_under_test':g['source_under_test'],'launch':launch,'native_export_state':stock['run_state']})
   timed=execution.get('termination_reason')=='timeout'
   if timed:need(co['state']=='COMPLETE' and co['elapsed_upper_bound_seconds']<180 and execution['rss_peak_kib']<ceff and execution['timed_out'] and execution['signal']==15 and execution['original_exit_code']==-15 and 600<=execution['elapsed_seconds']<610 and sup['elapsed_seconds']<sup['worker_wall_limit_seconds'],rid+'600 wholechild wall not RSS/compile/slot/global cap')
   cost.append({'id':rid,'compile':pick(co,['schema','boundary','scope','state','elapsed_upper_bound_seconds','limit_seconds','observed_run_state','marker_sha256','selectors']),'compile_elapsed_upper_bound_seconds':co['elapsed_upper_bound_seconds'],'native_verification_time_s':h.get('resources',{}).get('verification_time_s','UNKNOWN_CENSORED'),'native_wall_time_s':stock.get('wall_time_s','UNKNOWN'),'execution':pick(execution,['elapsed_seconds','original_exit_code','signal','timed_out','termination_reason','child_shutdown_verified','rss_peak_kib','rss_scope','rss_sample_period_seconds','component_group_peak_kib','component_rss_scope','cleanup_errors','process_identity']),'memory_admission':mem,'effective_cap_kib':ceff,'effective_cap_formula':'min(local6GiB,outer12GiB,available-2GiB)','limits':g['r5_limits'],'worker_supervision':pick(sup,['worker_exit','cutoff','elapsed_seconds','limit_initiated','outer_sampled_peak_kib','outer_rss_scope','supervisor_error','orphan_survivors_at_worker_exit','worker_wall_limit_seconds','lifecycle_events_omitted']),'containment':pick(sup['containment'],['verified','scope','elapsed_seconds','signals','reaped_adopted','worker_exit']),'lifecycle_diagnostics':{'events':sup['lifecycle_events'],'omitted':sup['lifecycle_events_omitted']},'cutoff_cause':'CHILD600_WALL_INCLUDING_COMPILE' if timed else 'NONE_COMPLETED','cutoff_phase':'AFTER_INITIAL_EXPORT_AND_NATIVE_START; exact subphase UNKNOWN' if timed else 'COMPLETED','censoring':'UNFINISHED_NATIVE_RESULT_UNKNOWN' if timed else 'NONE','residual_budget_after_compile_marker_s':600-co['elapsed_upper_bound_seconds'],'symex_backend_steps_VCC':'UNKNOWN_NOT_EXPORTED','rss_true_peak_at_signal':'UNKNOWN','next_root':order[rank] if rank<8 else None,'continuation':'verified shutdown/cleanup before next serial launch; final row seals campaign'})
   if bad:
    a=bad[0];parser=rich.RegularEvidence([selector],STD)
    stream=('Checking harness '+selector+'...\nRESULTS:\nCheck 1: '+a['display_id']+'\n\t - Status: '+a['status']+'\n\t - Description: "'+a['description']+'"\n\t - Location: '+a['location_display']+'\nSUMMARY:\n').encode()
    parser.feed(stream);parser.finish();need(parser.error is None and parser.records=={selector:bad} and len(parser.missing_sites)==1,rid+' actual-field frozen streaming parser zero sentinel to present-null coordinates')
    cases.append({'root':rid,'status':'NOT_APPLIED','recommendation':'RECOMMEND_EXACT_CASE_FOR_INDEPENDENT_REVIEW','exact_property':bad[0],'allowed_bad_location_cardinality':1,'run':run['id'],'attempt':1,'selector':selector,'invocation_id':g['invocation_id'],'namespace':g['cargo_target_dir'],'identity':{'run':run['id'],'attempt':1,'selector':selector,'invocation_id':g['invocation_id'],'namespace':g['cargo_target_dir'],'transport_sha256':integ['sha256'],'members':members_pin,'source':req['std_sha'],'tool':req['tool_sha'],'control':CTRL,'head':HEAD,'tree':trees['control']['tree'],'request':rh,'workflow':sha(wf),'cfg':g['effective_cfg'],'argv':g['argv'],'compact_sha256':sha(gz)},'members':members_pin,'native_counts':{'n_properties':h['n_properties'],'checks':h['checks'],'covers':h['covers']},'other_roles_covers_U_guards':'QUALIFICATION.json/NATIVE-PROPERTIES.json/U-ARGUMENTS.json exact same invocation; all other records located','all_other_records_located':all(located(p) for p in props if p!=bad[0]),'full_property_inventory_sha256':sha(canon(props)),'protected_epochs':'PROTECTED.json','shared_emitter_source_MIR_origin':'UNKNOWN','null_keys_present':True,'no_location_substitution':True,'producer_UNKNOWN_unchanged':True})
  need(len({x['invocation_id'] for x in roots})==8,'all8 fresh invocation namespaces')
  serial=[];prior_end=None
  for row in roots:
   rid=row['id'];sup=data['workers/'+rid+'-supervision.json'];launch=row['launch']['monotonic'];start=row['native_start_events'][0]['monotonic']
   need(launch<=sup['monotonic_start']<=start<=sup['monotonic_end'] and (prior_end is None or prior_end<=launch),rid+' serial launch/start/verified cleanup')
   serial.append({'id':rid,'launch':launch,'native_start':start,'cleanup_end':sup['monotonic_end'],'previous_cleanup_end':prior_end});prior_end=sup['monotonic_end']
  write('SERIAL-ORDER.json',{'same_host_monotonic_order_verified':True,'rows':serial})
  need(sum(q['native_property_count'] for q in qual if type(q['native_property_count']) is int)==139,'139 native properties across4 completed negatives; all4 network UNKNOWN')
  need(len(us)==18 and all(x['source_local_argument'] for x in us),'all18 U have invocation/source-local arguments')
  need(sum(len(q['unsupported_guards']) for q in qual if isinstance(q['unsupported_guards'],list))==1,'all1 SUCCESS unsupported guards retained; network UNKNOWN')
  need(sum(q['native_verdict']=='SUCCESS' for q in qual)==0 and sum(q['native_verdict']=='FAILURE' for q in qual)==4,'native0 SUCCESS/4 exact negatives/4 censored')
  # Bounded reader regressions at the exact actual terminal: no full synthetic suite.
  tp=local/'receipt.json';original=tp.read_bytes()
  # Present {} is malformed, never absence. No fallback/runner execution here.
  tp.write_text('{}');changed=copy.deepcopy(packet);empty=b'{}';changed['files']['receipt.json']={'encoding':'utf-8','text':'{}','bytes':2,'sha256':sha(empty)};(upload/'group-evidence.json.gz').write_bytes(gzip.compress(canon(changed),mtime=0))
  for route in [local,upload]:
   try:public.collect([route],req)
   except c.GlobalFailure as exc:
    need(str(exc)=='S4 terminal campaign schema mismatch','present {} rejected unchanged '+route.name);tests.append({'test':'present {} terminal','route':route.name,'result':'REJECT','reason':str(exc)})
   else:raise AssertionError('present {} terminal normalized')
  tp.write_bytes(original);(upload/'group-evidence.json.gz').write_bytes(gz)
  for field,variants in [('schema',[('missing',None),('null',None),('wrong','ch8-s3s4-bridge1-campaign-v1'),('bool',True),('container',{})]),('selected_roots',[('missing',None),('null',None),('bool',True),('string','8'),('float',8.0),('zero',0),('seven',7),('nine',9)])]:
   for name,value in variants:
    altered=copy.deepcopy(terminal);obj=altered if field=='schema' else altered['s3_campaign']
    if name=='missing':del obj[field]
    else:obj[field]=value
    tp.write_bytes(canon(altered));changed=copy.deepcopy(packet);b=canon(altered);changed['files']['receipt.json']={'encoding':'utf-8','text':b.decode(),'bytes':len(b),'sha256':sha(b)};(upload/'group-evidence.json.gz').write_bytes(gzip.compress(canon(changed),mtime=0))
    for route in [local,upload]:
     try:public.collect([route],req)
     except c.GlobalFailure as exc:
      expected='S4 terminal campaign schema mismatch' if field=='schema' else 'S3 terminal selected-root cardinality mismatch';need(str(exc)==expected,'exact rejection '+field+'/'+name+'/'+route.name);tests.append({'test':field+'/'+name,'route':route.name,'result':'REJECT','reason':str(exc)})
     else:raise AssertionError('invalid terminal accepted')
  tp.write_bytes(original);(upload/'group-evidence.json.gz').write_bytes(gz)
  victim=local/'groups/s3-s4p2_network_b01_n00_01_fullbyte/export.json';saved=victim.read_bytes()
  for name,replacement in [('missing sealed export',None),('changed sealed export',saved+b' ')]:
   if replacement is None:victim.unlink()
   else:victim.write_bytes(replacement)
   try:c.sealed(local)
   except (c.GlobalFailure,ValueError,OSError):tests.append({'test':name,'result':'REJECT'})
   else:raise AssertionError(name+' accepted')
   victim.write_bytes(saved)
  bg=copy.deepcopy(data['groups/s3-s4p2_network_b01_n00_01_fullbyte/receipt.json']);bg['tool_fingerprints_after']['binaries']['kani_driver']['sha256']='0'*64
  try:ev.protected(bg,req,data['baseline.json'],data['workers/s4p2_network_b01_n00_01_fullbyte-supervision.json'],rh)
  except ev.EvidenceError:tests.append({'test':'changed protected binary in UNKNOWN row','result':'REJECT'})
  else:raise AssertionError('protected binary mutation accepted')
  need(all((local/n).read_bytes()==b for n,b in members.items()) and c.collect([local],req)==public.collect([upload],req)==right,'authentic bytes and replay unchanged after adverse tests')
 # Exact metadata proposal model only; no active policy/parser/receipt changes.
 location_tests=[]
 for case in cases:
  props=properties[case['root']]['properties'];expected_prop=case['exact_property'];expected_identity=copy.deepcopy(case['identity'])
  def proposal_gate(records,identity):
   bad=[p for p in records if not located(p)]
   return identity==expected_identity and bad==[expected_prop] and all(k in bad[0] for k in ('file','line')) and len({p['id'] for p in records})==len(records) and sha(canon(records))==case['full_property_inventory_sha256']
  need(proposal_gate(props,case['identity']),case['root']+' authentic hypothetical exact packet accepts')
  mutations=[]
  for field,value in [('id',expected_prop['id']+'x'),('display_id','wrong'),('class','assertion'),('status','UNREACHABLE'),('description','other'),('file','library/core/src/lib.rs'),('line','0'),('location_display','library/core/src/lib.rs:0:0')]:
   pp=copy.deepcopy(props);next(p for p in pp if p['id']==expected_prop['id'])[field]=value;mutations.append((field,pp,case['identity']))
  for field in ['file','line']:
   pp=copy.deepcopy(props);del next(p for p in pp if p['id']==expected_prop['id'])[field];mutations.append(('missing_'+field,pp,case['identity']))
  for label,choose,field,value in [('guard_failure',lambda p:p['class']=='unsupported_construct','status','FAILURE'),('role_failure',lambda p:p['description'].endswith('SORTED_FULL_VALUE_COUNT'),'status','FAILURE'),('cover_unsat',lambda p:p['class']=='cover','status','UNSATISFIABLE'),('U_changed',lambda p:p['status']=='UNREACHABLE','status','SUCCESS'),('second_unlocated',lambda p:located(p),'file',None)]:
   pp=copy.deepcopy(props);next(p for p in pp if choose(p))[field]=value;mutations.append((label,pp,case['identity']))
  mutations.append(('duplicate_extra_record',props+[copy.deepcopy(expected_prop)],case['identity']))
  for field in expected_identity:
   ident=copy.deepcopy(expected_identity);ident[field]='ADVERSE_WRONG_IDENTITY';mutations.append(('identity_'+field,props,ident))
  for label,pp,ident in mutations:need(not proposal_gate(pp,ident),case['root']+' hypothetical exact proposal rejects '+label);location_tests.append({'root':case['root'],'mutation':label,'result':'REJECT'})
 old_cases=[]
 for rev,path in [('f74025e493a627962842e8f7bc6a2766d33dd300','ch8-s3/admission-r2-location/ADMISSION.json'),('ff193cc35690a5daabaa849d412c58d9f286d893','ch8-s3/admission-s3-2-r1-exact-location/ADMISSION.json')]:
  full=BASE+'kani3300/'+path;b=blob(G0,rev,full);d=json.loads(b)
  records=[{'root':d['harness'],'property':d['exact_property'],'counts':d['counts'],'identity':d['protected_identity']}] if 'exact_property' in d else [{'root':x['root'],'property':x['reviewed_packet']['exact_property'],'counts':x['reviewed_packet']['counts'],'identity':pick(x['reviewed_packet'],['invocation_id','namespace','bindings'])} for x in d['exact_metadata_cases']]
  old_cases.append({'commit':rev,'path':full,'sha256':sha(b),'review_commit':d.get('independent_review_commit',d.get('immutable_inputs',{}).get('review')),'records':records,'comparison':'Same class/status/description/null-key/display-zero shape; exact roots/IDs/invocations/source/control/request/member hashes differ. No transfer; common emitter/positive source or MIR origin UNKNOWN.'})
 write('ROOTS.json',{'rows':roots,'request':req,'domain_unwind':domain_doc,'source_files':sourcefiles,'physical_inode_realpath_identity':'UNKNOWN_NOT_EXPORTED','deferred':terminal['s3_campaign']['unselected']})
 write('PROTECTED.json',{'baseline':data['baseline.json'],'epochs':epochs,'assurance':'SOURCE_REPORTED snapshots and identity hashes; independent compiler/MIR causality UNKNOWN'})
 write('NATIVE-PROPERTIES.json',properties)
 write('U-ARGUMENTS.json',{'count':len(us),'instances':us,'producer_policy':req['unreachable_admission'],'admitted':False})
 write('QUALIFICATION.json',{'schema':'s4p-terminal-qualification-v1','assurance':'S1 Profiles v4 SOURCE_REPORTED provisional ONLY','rows':qual,'strict_policy':req['unreachable_admission'],'producer_expected_matches':0,'U_count':len(us),'U_arguments':'U-ARGUMENTS.json','observed_SUCCESS_unsupported_guards':1,'network_inventory_counts':'UNKNOWN_NOT_ZERO','source_site_plan':{'assertions':21,'covers':21,'native_properties_observed':139,'native_completed_rows':4},'qualified_new_leaves':0,'qualification_admitted':False,'init_provider_summary_credit':False,'proof_obligations_closed':0,'independent_B1_B2_credit':'NONE'})
 write('METADATA-GAP.json',{'schema':'s4p-location-audit-v1','rows':gaps,'completed_rows':4,'observed_bad_location_records':0,'incomplete_rows':4,'network_locations':'UNKNOWN_CENSORED','new_exact_case_proposal':'NONE_OBSERVED; four incomplete inventories UNKNOWN','class_unreachable_SUCCESS_vs_status_UNREACHABLE':'Distinct partitions, both fully retained','shared_emitter_source_MIR_origin':'UNKNOWN','original_producer_history_preserved':True})
 write('LOCATION-PROPOSAL.json',{'schema':'s4p-exact-location-proposal-v1','status':'NOT_APPLIED','recommendation':'NO_NEW_CASE_OBSERVED_NO_ADMISSION','cases':cases,'old_packets':old_cases,'adverse_tests':location_tests,'test_scope':'Hypothetical exact packet boundary only; does not make active rich reader accept or establish source origin','constraints':['Exact run/attempt/selector/invocation/namespace/protected identities and authenticated member bytes only','One exact full dictionary, both null keys present; no source coordinate substitution','All other properties including every role/cover/U/guard positively located; counts and full status partitions unchanged','U/guard treatment separate; existing producer REJECT_ALL and proposalDISABLED unchanged','No global/suffix/unreachable/stdlib/future-run waiver; shared emitter/source/MIR origin UNKNOWN'],'admission':False,'runtime_parser_policy_changed':False})
 write('COST.json',{'campaign_elapsed_seconds':terminal['phase_elapsed_seconds'],'caps':pins['caps'],'setup':pick(data['setup/receipt.json'],['setup_total_seconds','elapsed_seconds','rss_peak_kib','rss_status','rss_sample_period_seconds','component_group_peak_kib','component_rss_scope','original_exit_code','child_shutdown_verified']),'job':pick(jobs[0],['id','started_at','completed_at','steps']),'rows':cost,'residual_budget_metric':'600 minus initial-export observed upper-bound marker is arithmetic only, not measured backend/proof time or an uncensored budget guarantee','compiler_metric':'Observed initial export marker upper bound includes compilation/link and observation delay; not exclusive compile CPU','native_verification_metric':'Exported resources.verification_time_s; no exclusive backend claim','symex_backend_subphases':'UNKNOWN_NOT_EXPORTED','rss_metric':'Nominal50ms sampled nonatomic owned PGID VmRSS; outer12GiB owned census, reserve2GiB; component peaks not simultaneous; no kernel/cgroup/tree peak guarantee','network_conclusion':'ALL_FOUR child600 wholechild wall cutoffs including compilation; no observed RSS/compile180/outer/slot/global cap; native inventories UNKNOWN','accounting':'TRACKING_ONLY_NO_WRITES','no_resource_escalation':True})
 write('PROVENANCE.json',{'task':TASK,'base_task':BASE_TASK,'source_tool_control_trigger':trees,'request_sha256':rh,'workflow_sha256':sha(wf),'checkout_depths':pins['checkout_depths'],'dependencies':deps,'artifact_metadata':art[0],'transport_integrity':'artifact-integrity.json','member_sha256':sha(gz),'uncompressed_payload_sha256':sha(raw),'member_count':len(data),'frozen_reader_files':frozen,'source_file_hashes':sourcefiles,'reporter_reference':{'commit':TASK,'path':BASE+'kani3300/ch8-s4/run-44481580554/replay.py','sha256':sha(blob(G0,TASK,BASE+'kani3300/ch8-s4/run-44481580554/replay.py'))},'base_helper':{'path':str(old_helper.relative_to(G0)),'sha256':sha(old_helper.read_bytes())},'native_binding_scope':'Actual registration/exports/compile/argv/cfg/namespaces; independent AST/MIR/property/emitter/caller/physical-inode causality UNKNOWN','acquisition':'Existing acquire.py from run44481580554 with exact size/digest and bounded gh memory-transport adapter; ACQUISITION.json records attempts. Sole compact member acquired once; digest checked before ZIP opened, ZIP never saved; no raw/full/logs/GCS','restrictions':'Own directory only; no native/compiler/CI/push/ledger/policy/model changes/subagents'})
 write('VALIDATION.json',{'status':'PASS','checks_count':len(CHECKS),'checks':CHECKS,'adverse_tests':tests,'location_adverse_tests':location_tests,'scope':'Targeted offline hashes/source gates/native properties/protected epochs/portable prefix/terminal schema/cardinality only','full_host_suite_rerun':False,'native_rerun':False,'evidence_modified':False,'policy_modified':False})
 write('RESULT.json',{'schema':'s4p-terminal-intake-v1','status':'READY','run':run['id'],'attempt':1,'native_run':'completed/failure','classification':'SELECTED_PARTIAL; NATIVE0_SUCCESS_4_INTENDED_FAILURE_4_CHILD600_WALL_TIMEOUT; STRICT0; NO_ADMISSION','campaign_elapsed_seconds':terminal['phase_elapsed_seconds'],'global_stop':False,'completed_sealed_prefix':8,'native_success':0,'intended_native_negative_failures':4,'child_wall_timeout_unknown_results':4,'strict_expected_matches':0,'provisional_S1_network_candidates_for_review':0,'location_proposal':'NONE_OBSERVED_IN_COMPLETE_NEGATIVE_EXPORTS; NETWORK_UNKNOWN','U_source_local_arguments':18,'observed_SUCCESS_unsupported_guards':1,'observed_native_properties':139,'qualified_new_leaves':0,'proof_obligations_closed':0,'proof_credit':'NONE','review':'Root intake verification and separately issued offline plan; no admission by intake author','runtime_settings_actions':[],'subagents':0,'lifecycle_telemetry':'64 retained lifecycle events per row with nonzero omitted counts; details outside retention UNKNOWN, cleanup observations kept separately','policy_or_accounting_changed':False,'remaining_unknown':['All four network native inventories/roles/covers/U/guards/unwind outcomes censored; observed empty arrays are incomplete, not empty U inventories','Timestamped phase at signal, internal phase durations, solver start, uncensored peak/verification time, omitted lifecycle events; bounded tails do show symbolic loop unwinding','Positive source/emitter/AST/MIR/caller causal binding','Fallback5..16/network0..32/general/initmask/provider/summary/ownership/panic/generic trait/fullN16N32/B1B2'],'handoff':'Root verifies exact committed hash/manifest/pins/replay/cap facts, then separately issues an intake-bound offline simplification-or-defer plan; no implementation or CI authorized'})
 print(json.dumps({'status':'PASS','checks':len(CHECKS),'roots':len(roots),'U':len(us),'guards':1,'properties':139,'metadata_gaps':len(cases),'adverse_tests':len(tests),'location_adverse_tests':len(location_tests)}))
if __name__=='__main__':main()
