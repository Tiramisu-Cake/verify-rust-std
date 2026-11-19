#!/usr/bin/env python3
"""Bounded offline intake with exact committed readers; no native execution.

Reuses the run-44439462279 and run-44416629057 intake contracts. Only this
directory is written; fresh temporary materialization is removed on exit.
"""
import base64,collections,copy,csv,gzip,hashlib,importlib,json,re,subprocess,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
G0=Path('/root/verify-rust-std-kani3300-g0')
TASK='0d36282d44664af05a69eb3ee47686952786a261'
ADDENDUM='7c2c6af9f538d43e5cce51d548bdd73633358241'
HEAD='c2bbdb972cfe0e6f7472cf8bd93f1fa7c5e87acd'
CTRL='d675ef70dc1ada13330efc0990c2e1d6b0d21a5a'
CONTROL=Path('/root/kani-ch8-s3s4-bridge1-r1-control-w13')
SOURCE=Path('/root/verify-rust-std-ch8-s3s4-bridge1-w13')
TOOL=Path('/root/kani-upstream-ch8-s1')
STD=Path('/home/runner/work/kani/kani/export')
BASE='research/challenge-8/kani-k1/'
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
def context(b,line):
    ls=b.decode().splitlines();return '\n'.join(f'{i+1}: {ls[i]}' for i in range(max(0,line-5),min(len(ls),line+4)))
def uargument(rid,p):
    f=p['file'];n=int(p['line'])
    if f.endswith('/sorting_model.rs'):
        length={'checker_order_corrupt':2,'checker_count_corrupt':32,'sort13_weak':13}.get(rid)
        args={100:'Order loop starts i=1 and increments only with i<L<=32; i+1<=32.',106:'Count outer i<L<=CAP32 bounds before.values[i].',111:'Inner j<L<=32 bounds before.values[j]; old_count starts0 and is at most j before one increment.',112:'Entry L=before.len=values.len<=32; j<L bounds values[j]; new_count<=j before one increment.',113:'Inner loop increments only with j<L<=32, hence j+1<=32.',118:'Outer loop increments only with i<L<=32, hence i+1<=32.'}
        if length is not None and n in args:return args[n],[f'Exact fixed fixture L={length}<=CAP32; valid snapshot and equal lengths checked at active_post entry.','Early false return can make later checks unreachable; bounds still imply defined arithmetic.']
    if f.endswith('/fmt/mod.rs') and n==820:return 'Literal shift count1 is below x86_64 usize width64; this is not a no-lost-bits claim.',['Exact expression s.len()<<1|1; target x86_64.']
    if f.endswith('/num/uint_macros.rs') and n in (3222,3224):return ('self<other branch gives other>=self for other-self.' if n==3222 else 'Else branch gives self>=other for self-other.'),['Exact usize::abs_diff unsigned subtraction branch, all usize values.']
    if f.endswith('/ptr/const_ptr.rs') and n==1479:return 'Normal continuation follows is_power_of_two(align); zero is not a power of two, so align>=1 and align-1 is defined.',['Pointer validity and panic properties remain separate.']
    if f.endswith('/ub_checks.rs') and n==148:return 'size==0 arm skips division; else divides only by size!=0. Concrete u8 size=1 independently.',['Allocation validity is not inferred.']
    if f.endswith('/sorting_s2_span.rs') and n in (36,37):return ('i starts1 and loop executes only with i<n<=32; i>=1 makes i-1 defined.' if n==36 else 'i<n<=32 before increment gives i+1<=32.'),['Exact u8/KeyLess Span::ordered source; n>32 returns false before loop.','No inference of ownership/readability from this arithmetic argument.']
    return None,[]

def main():
    pins=json.loads(blob(G0,TASK,BASE+'kani3300/ch8-s3-s4/postrun-bridge-1-r1/INPUTS.json'))
    add=json.loads(blob(G0,ADDENDUM,BASE+'kani3300/ch8-s3-s4/postrun-bridge-1-r1-terminal/INPUTS.json'))
    taskbytes=blob(G0,TASK,BASE+'TASK-CH8-S3S4-BRIDGE1-R1-INTAKE-W11.md')
    need(sha(taskbytes)==pins['task_sha256'],'exact task bytes/hash')
    write('INPUTS.json',{'task_commit':TASK,'terminal_addendum_commit':ADDENDUM,'base_inputs':pins,'terminal_addendum':add,'settings':'current high/FastOFF preserved; no subagents/model changes','authorization':'Owner08:25 /new11; terminal intake only; no review issued here'})
    run=json.loads((HERE/'github-run.json').read_bytes());jobs=json.loads((HERE/'github-jobs-detail.json').read_bytes())['jobs'];arts=json.loads((HERE/'github-artifacts.json').read_bytes())['artifacts']
    need(all(run[k]==v for k,v in add['native_metadata'].items()),'connected exact terminal metadata and timestamps')
    need(len(jobs)==1 and jobs[0]['head_sha']==HEAD and jobs[0]['run_attempt']==1 and jobs[0]['run_id']==pins['run_id'] and jobs[0]['conclusion']=='failure','connected exact job/run/attempt/head failure')
    need(len(arts)==1 and all(arts[0][k]==add['artifact'][p] for k,p in [('id','id'),('name','name'),('digest','transport_digest'),('size_in_bytes','size_bytes')]),'connected exact artifact metadata digest before acquisition')
    need(arts[0]['expired'] is False and arts[0]['workflow_run']['head_sha']==HEAD and arts[0]['workflow_run']['id']==pins['run_id'],'artifact not expired run/head binding')
    integ=json.loads((HERE/'artifact-integrity.json').read_bytes());gz=(HERE/'group-evidence.json.gz').read_bytes();raw=gzip.decompress(gz)
    need(sha(gz)==integ['payload_sha256'] and sha(raw)==integ['uncompressed_sha256'],'compact/payload hashes separate from transport')
    need(integ['bytes']==374679 and 'sha256:'+integ['sha256']==arts[0]['digest'] and integ['digest_checked_before_zip_open'] and not integ['transport_saved'],'transport digest checked before memory-only ZIP member access')
    packet=json.loads(raw);need(packet['state']=='PACKAGED' and packet['error'] is None and packet['schema']=='ch8-s1-05-artifact-v1','compact complete packaging schema/state')
    members={};data={}
    for n,e in packet['files'].items():
        p=Path(n);need(not p.is_absolute() and '..' not in p.parts and '\\' not in n and p.suffix=='.json','structured-only member '+n)
        b=decode(e);need(len(b)==e['bytes'] and sha(b)==e['sha256'],'member size/hash '+n);members[n]=b;data[n]=json.loads(b)
    need(len(data)==105,'exact105 compact structured members')
    trees={}
    for kind,repo,rev in [('source',SOURCE,pins['source']['sha']),('tool',TOOL,pins['tool']['sha']),('control',CONTROL,CTRL),('trigger',CONTROL,HEAD)]:
        v={'sha':rev,'tree':git(repo,'rev-parse',rev+'^{tree}').decode().strip(),'sole_parent':git(repo,'show','-s','--format=%P',rev).decode().strip()};trees[kind]=v
        expected=pins['head'] if kind=='trigger' else pins[kind]
        need(v['tree']==expected['tree'] and v['sole_parent']==(expected.get('sole_parent') or expected['parents'][0]),kind+' exact tree/sole parent')
    need(trees['control']['tree']==trees['trigger']['tree'],'trigger nonskip same-tree sibling of reviewed control')
    reqbytes=blob(CONTROL,HEAD,'ch8-s1-control/CI-REQUEST.json');req=json.loads(reqbytes);rh=sha(reqbytes);wf=blob(CONTROL,HEAD,'.github/workflows/ch8-s2.yml')
    need(rh==pins['request']['sha256'] and reqbytes==blob(CONTROL,CTRL,'ch8-s1-control/CI-REQUEST.json'),'executed exact reviewed request bytes')
    need(sha(wf)==pins['request']['workflow_sha256'] and wf==blob(CONTROL,CTRL,'.github/workflows/ch8-s2.yml'),'executed exact reviewed workflow/depths7/5/2')
    for p,h in req['ci_payload_sha256'].items():need(sha(blob(CONTROL,HEAD,p))==h and blob(CONTROL,HEAD,p)==blob(CONTROL,CTRL,p),'executed pinned control payload '+p)
    sourcefiles={}
    for key in ['changed_file_sha256','cfg_pfc_source_sha256','contract_stack_source_sha256','lexical_source_sha256','ordinary_contract_source_sha256']:
        for p,h in req[key].items():
            need(sha(blob(SOURCE,req['std_sha'],p))==h,'source hash '+key+' '+p);sourcefiles[p]=h
    need(req['s3']['caps']==pins['caps'] and req['flags']==pins['flags'],'all caps/flags unchanged')
    need([x['id'] for x in req['rows']]==pins['ordered_rows'],'seven exact ordered roots')
    need(data['campaign-start.json']['request_data']==req and data['receipt.json']['request_sha256']==rh,'actual campaign embedded exact request')
    need(data['baseline.json']['control']=={'sha':HEAD,'tree':pins['head']['tree'],'parent':pins['head']['sole_parent'],'dirty':''},'native actual checkout control head/tree/parent/clean')
    review_prefix=BASE+'kani3300/ch8-s3-s4/bridge-1-review-r1/'
    review_files={n:blob(G0,pins['review']['g0'],review_prefix+n) for n in ('CHECKPOINT.json','FINDINGS.json','VALIDATION.json')}
    prior=json.loads(review_files['FINDINGS.json']);priorcheck=json.loads(review_files['CHECKPOINT.json'])
    need(prior['disposition']=='APPROVE' and prior['candidate']==pins['package']['g0'] and prior['control']==CTRL and prior['control_tree']==pins['control']['tree'] and prior['source']==req['std_sha'] and prior['tool']==req['tool_sha'] and prior['request_sha256']==rh and prior['workflow_sha256']==sha(wf),'exact committed prior review identities')
    need(priorcheck['closed_independently']==['W14-B1-01','W14-B1-02'] and priorcheck['remaining_blockers']==[] and all(x['status']=='CLOSED_INDEPENDENTLY' for x in prior['closures']),'prior B01 B02 independent closures preserved')
    write('B01-B02.json',{'review_commit':pins['review']['g0'],'files':{n:{'path':review_prefix+n,'sha256':sha(b)} for n,b in review_files.items()},'closures':prior['closures'],'prior_validation':json.loads(review_files['VALIDATION.json']),'assurance':'Committed independently reviewed pre-run evidence; no new review issued. Native Validate step success is step-summary only, not an independently observed per-test inventory.','current_replay':'Actual int7 full completion plus bounded invalid-cardinality local/upload STOPPED/partial/zero-completion controls in VALIDATION.json; same-tree reviewed reader and writer hashes verified.','full_host_suite_rerun':False})
    gopath=BASE+'kani3300/ch8-s3-s4/bridge-1-go/ROOT-RECHECK.json';gobytes=blob(G0,pins['root_GO']['g0'],gopath);go=json.loads(gobytes)
    need(go['review_g0']==pins['review']['g0'] and go['candidate_g0']==pins['package']['g0'] and go['request_sha256']==rh and go['workflow_sha256']==sha(wf) and go['disposition']=='APPROVE','exact prior root recheck dependencies/request/workflow')
    domain_doc=json.loads(blob(G0,pins['package']['g0'],BASE+'kani3300/ch8-s3-s4/bridge-1-r1/DOMAIN-UNWIND.json'));domains={x['id']:x for x in domain_doc['roots']}
    need(domain_doc['std_sha']==req['std_sha'],'exact source domain/unwind package binding')
    planned_assertions=sum(role['class']=='assertion' for row in req['rows'] for role in row['roles']);planned_covers=sum(row['required_cover_count'] for row in req['rows'])
    need(planned_assertions==19 and planned_covers==46,'planned19 source assertion sites and46 cover labels are not native property counts')
    for rid,prefix,count in [('fallback_cell_b01_n00_16','B1_F_N',17),('network_u8_b01_n00_08','B1_N_N',9)]:
        row=next(x for x in req['rows'] if x['id']==rid)
        need(all(f'{prefix}{n:02}' in row['required_cover_messages'] for n in range(count)),rid+' every symbolic length cover required')
    frozen={};qual=[];roots=[];cost=[];us=[];gaps=[];epochs=[];properties={};tests=[]
    with tempfile.TemporaryDirectory(prefix='s34-intake-') as td:
        tmp=Path(td);reader=tmp/'reader';reader.mkdir()
        for n in git(CONTROL,'ls-tree','-r','--name-only',CTRL,'ch8-s1-control').decode().splitlines():
            rel=Path(n).relative_to('ch8-s1-control');b=blob(CONTROL,CTRL,n);p=reader/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);frozen[str(rel)]={'sha256':sha(b),'bytes':len(b)}
        sys.path.insert(0,str(reader));r=importlib.import_module('runner');c=importlib.import_module('s34_campaign');ev=importlib.import_module('s3_evidence');rich=importlib.import_module('rich_evidence');policy=importlib.import_module('s34_policy');public=importlib.import_module('collect')
        need(r.load_request()==req,'frozen request loader exact7')
        # Source-only checks; no runner main/full validator/native preparation.
        static=policy.validate_source(SOURCE,req)
        write('SOURCE-GATES.json',{'status':static['status'],'canonical_sha256':sha(canon(static)),'reports':{k:pick(v,['status','schema','source_sha','source_tree','source_files_sha256','proof_credit','limits']) for k,v in static['reports'].items()},'scope':'Pinned source-only policy validators; no expansion/compiler/full Validate','proof_credit':'NONE'})
        local=tmp/'materialized';upload=tmp/'upload';local.mkdir();upload.mkdir()
        for n,b in members.items():p=local/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
        (upload/'group-evidence.json.gz').write_bytes(gz)
        left=c.collect([local],req);right=public.collect([upload],req)
        need(left==right,'fresh materialized vs upload-only public collector equality')
        seals=c.sealed(local);need(list(seals)==pins['ordered_rows'],'all7 sealed ordered completion prefix')
        need(type(data['receipt.json']['s3_campaign']['selected_roots']) is int and data['receipt.json']['s3_campaign']['selected_roots']==7,'selected_roots exact genuine int7')
        need(not right['global_stop'] and not right['selected_missing_groups'] and data['receipt.json']['state']=='SELECTED_PARTIAL' and data['receipt.json']['stop_reason'] is None,'SELECTED_PARTIAL no global STOP no missing selected row')
        write('PREFIX.json',{'state':right['state'],'completed_prefix':list(seals),'selected_roots':7,'local_upload_equal':True,'all_seal_digests_verified':True,'global_stop':right['global_stop'],'global_stops':right['global_stops'],'selected_missing_groups':right['selected_missing_groups'],'collector':right,'completion_is_not_qualification':True})
        for rank,row in enumerate(req['rows'],1):
            rid=row['id'];selector=row['selector'];gp='groups/s3-'+rid+'/'
            g=data[gp+'receipt.json'];co=data[gp+'compile/receipt.json'];can=data[rid+'/receipt.json'];sup=data['workers/'+rid+'-supervision.json'];life=data['workers/'+rid+'-lifecycle.json'];launch=data['workers/'+rid+'-launch.json'];stock=data[gp+'export.json'];pr=data[gp+'properties.json'];bm=data[gp+'binding-metadata.json'];execution=g['execution'];hs=stock.get('harnesses',[]);h=hs[0] if hs else {};props=pr.get('harnesses',[{'properties':[]}])[0]['properties'];binding=req['source_bindings'][rid]
            need(ev.provenance(g,co,req,rid,rh),rid+' all-state source/compile provenance')
            prot=ev.protected(g,req,data['baseline.json'],sup,rh);need(not prot['observed_errors_ignored'],rid+' all-state protected reader')
            need(c.snapshots.validate_pair(data['baseline.json'],life['pre'],life['post'],life['context']),rid+' controller epochs source/control/binary identity')
            need(g['argv']==r.build_argv(STD,Path('/home/runner/work/kani/kani/tool'),[selector],row['unwind'],Path('/home/runner/work/_temp/ch8-s1-receipts')/(gp+'export.json')) and g['selectors']==[selector] and g['unwind']==row['unwind'],rid+' singleton argv/selector/unwind')
            mem=g['memory'];ceff=min(pins['caps']['local_rss_kib'],pins['caps']['outer_rss_kib'],mem['available_kib']-pins['caps']['headroom_kib'])
            need(g['timeout_seconds']==g['group_budget_seconds']==600 and g['compile_limit_seconds']==180 and g['phase_limited'] is False and mem['group_cap_kib']==ceff==6291456 and mem['reserve_kib']==2097152,rid+' actual child/compile/effective RSS caps/availability')
            need(launch['context']['root']==rid and launch['context']['rank']==rank and launch['context']['epoch']=='E'+str(rank),rid+' launch order/controller context')
            need(g['effective_cfg']==req['flags']['RUSTFLAGS'] and g['native_start_verified'] and [x['selector'] for x in g['native_start_events']]==[selector],rid+' actual cfg singleton native start')
            need(g['cargo_target_dir']==str(STD/'target/ch8-s1-cargo'/g['invocation_id']),rid+' fresh invocation namespace')
            need(bm['invocation_id']==g['invocation_id'] and bm['request_sha256']==rh and bm['std_sha']==req['std_sha'] and bm['tool_sha']==req['tool_sha'] and bm['argv']==g['argv'],rid+' binding metadata request/source/tool/invocation/argv')
            for a in bm['artifacts']:need(sha(members[gp+a['path']])==a['sha256'] and len(members[gp+a['path']])==a['bytes'],rid+' bound export member '+a['path'])
            stages={'E0':data['baseline.json']['binaries'],'pre':life['pre']['binaries'],'worker.BEFORE':g['tool_fingerprints_before'],'worker.AFTER':g['tool_fingerprints_after'],'controller.post':life['post']['binaries']}
            for label,snap in stages.items():need(r.fingerprints_match(data['baseline.json']['binaries'],snap),rid+' protected binary '+label)
            epochs.append({'id':rid,'context':life['context'],'stages':stages,'all_five_equal_E0':True,'protected':prot})
            need(execution['child_shutdown_verified'] and sup['worker_exit']==0 and sup['containment']['verified'] and not sup['cutoff'] and not sup['limit_initiated'] and sup['supervisor_error'] is None and not sup['orphan_survivors_at_worker_exit'],rid+' shutdown/ownership/reap/serial continuation')
            registrations=[];providers=[]
            for m in bm['native_metadata']:
                if m.get('state')!='CAPTURED':continue
                b=decode(m);need(len(b)==m['bytes'] and sha(b)==m['sha256'],rid+' native metadata hash '+m['path']);md=json.loads(b)
                registrations += [dict(x,metadata_path=m['path'],metadata_sha256=m['sha256']) for x in md.get('proof_harnesses',[]) if x['pretty_name']==selector]
                providers += [x for x in md.get('contracted_functions',[]) if selector in x.get('harnesses',[])]
            need(len(registrations)==1,rid+' unique native registration including partial')
            reg=registrations[0];kind=reg['attributes']['kind']
            need(reg['original_file']==str(STD/binding['file']) and reg['crate_name']=='core',rid+' native source/crate')
            need(reg['attributes']['stubs']==([{'original':'s2_swap_seam','replacement':'weak_swap'}] if rid=='sort13_weak' else []) and reg['attributes']['verified_stubs']==[],rid+' exact native stubs/seam')
            need(kind==({'ProofForContract':{'target_fn':'insert_tail'}} if row['mode']=='PFC' else 'Proof') and (binding['target']=='insert_tail' if row['mode']=='PFC' else binding['target'] is None and row['target'] is None),rid+' exact Original nulltarget/PFC actualtarget')
            need(stock['schema_version']=='0.1.0' and stock['kani_commit']==req['tool_sha'] and stock['kani_commit_dirty'] is False and stock['target']=='x86_64-unknown-linux-gnu',rid+' native schema/tool/target')
            need(stock['harness_selection']=={'requested_filters':[selector],'exact':True,'unmatched_filters':[],'matched_count':1} and stock['harness_timeout_s']==600,rid+' native exact singleton selection/cap')
            literal=[]
            for role in row['roles']:
                b=blob(SOURCE,req['std_sha'],role['file']);need(sha(b)==role['source_sha256'] and b.decode().splitlines()[role['line']-1]==role['source_line'],rid+' literal source '+role['description'])
                matches=[p for p in props if p['description']==role['description']]
                ok=bool(matches) and all(p['class']==role['class'] and p['status']==role['status'] and p['file']==str(STD/role['file']) and p['line']==str(role['line']) for p in matches)
                need(ok if hs else not matches,rid+' native literal role or explicit UNKNOWN '+role['description'])
                literal.append({'required':role,'native_matches':matches,'exact_match':ok,'assessment':'OBSERVED_EXACT' if ok else 'UNKNOWN_NO_COMPLETED_NATIVE_INVENTORY'})
            bad=[p for p in props if not located(p)];fail=[p for p in props if p['status']=='FAILURE'];u=[p for p in props if p['status']=='UNREACHABLE'];covers=[p for p in props if p['class']=='cover'];guards=[p for p in props if p['class']=='unsupported_construct'];rebound=None;pfc=None;reader_result=None
            if hs:
                need(len(hs)==1 and h['name']==selector,rid+' completed singleton export')
                rebound=r.validate_export_value(stock,row,source_binding=binding,std=STD,group_selectors=[selector]);need(rebound['outcome']=='RECORDED',rid+' frozen source/stage/target reader')
                dec=rich.RegularEvidence([selector],STD);dec.finished=True;dec.closed={selector};dec.records={selector:copy.deepcopy(props)};dec.validate(stock);reader_result='ACCEPT'
                need(h['n_properties']==len(props)==h['checks']['total']+h['covers']['total'],rid+' full native/rich count partitions')
                need(not bad and len(fail)==(1 if row['expected']=='DETECTED' else 0) and h['outcome']=={'kind':'COMPLETED','verdict':'FAILURE' if fail else 'SUCCESS'},rid+' all properties located exact native verdict')
                need(len(covers)==row['required_cover_count'] and set(p['description'] for p in covers)==set(row['required_cover_messages']) and all(p['status']=='SATISFIED' for p in covers),rid+' complete exact SAT covers')
                need(all(p['status'] in ('SUCCESS','FAILURE','UNREACHABLE','SATISFIED') for p in props),rid+' full statuses assessed no hidden ERROR/UNKNOWN')
                need(len(guards)==len(h['unsupported_constructs']) and all(p['status']=='SUCCESS' and located(p) for p in guards),rid+' all SUCCESS unsupported guards retained')
                if row['mode']=='PFC':
                    need(len(providers)==1,rid+' unique contracted provider')
                    symbol=reg['contract']['contracted_function_name'];decoded=subprocess.check_output(['c++filt','-i','-s','rust',symbol],text=True).strip();links=[p for p in props if p['id'].startswith(decoded+'.')]
                    need(decoded.startswith('core::slice::sort::shared::smallsort::insert_tail::<u8, core::slice::sort::shared::smallsort::verify::sorting_model::KeyLess<u8>>::'),rid+' concrete PFC actual function')
                    need(all(any(p['class']==cl and p['status']=='SUCCESS' and symbol in p['description'] for p in links) for cl in ('single_top_level_call','no_recursive_call')),rid+' DFCC actual body links')
                    ensures=[p for p in props if p['id'].startswith('slice::sort::shared::smallsort::insert_tail::<u8, slice::sort::shared::smallsort::verify::sorting_model::KeyLess<u8>>::') and p['class']=='assertion' and p['description'].startswith('|_|')]
                    need(len(ensures)==1 and ensures[0]['status']=='SUCCESS' and located(ensures[0]),rid+' checked source-reported ensures')
                    pfc={'raw_symbol':symbol,'demangled_symbol':decoded,'DFCC_links':links,'ensures':ensures,'assurance':'SOURCE_REPORTED native PFC registration/actual-body stack; independent MIR binding UNKNOWN'}
            else:
                need(stock['run_state']=='INCOMPLETE' and 'harnesses' not in stock and not props and pr['state']=='INCOMPLETE' and execution.get('termination_reason')=='timeout',rid+' partial native export unknown properties and wall timeout')
            strict=policy.expected_observation(row,rebound or {},{'name':selector,'properties':props})
            need(strict is False and can['s3_expected_match'] is False and seals[rid]['expected_match'] is False,rid+' immutable strict conclusion false')
            for p in u:
                rel=p['file'].split('/export/',1)[1];n=int(p['line']);b=blob(SOURCE,req['std_sha'],rel);arg,premises=uargument(rid,p)
                us.append({'root':rid,'selector':selector,'invocation_id':g['invocation_id'],'namespace':g['cargo_target_dir'],'property':p,'member':gp+'properties.json','member_sha256':sha(members[gp+'properties.json']),'source_sha':req['std_sha'],'source_file':rel,'source_sha256':sha(b),'source_line':n,'source_context':context(b,n),'effective_cfg':g['effective_cfg'],'provider_target':binding['target'],'domain':domains[rid],'source_binding':binding,'native_registration':reg,'source_local_argument':arg,'premises':premises,'assessment':'SOURCE_LOCAL_DEFINEDNESS_ARGUMENT' if arg else 'UNKNOWN','origin_assurance':'SOURCE_REPORTED site; independent AST/MIR/property/caller origin UNKNOWN','policy_status':'REJECT_ALL; proposal DISABLED; no admission'})
            gaps.append({'root':rid,'selector':selector,'invocation_id':g['invocation_id'],'namespace':g['cargo_target_dir'],'member':gp+'properties.json','member_sha256':sha(members[gp+'properties.json']),'export_member':gp+'export.json','export_sha256':sha(members[gp+'export.json']),'observed_offending_records':bad,'observed_count':len(bad) if hs else 'UNKNOWN_NO_COMPLETED_NATIVE_INVENTORY','class_unreachable_SUCCESS':[p for p in props if p['class']=='unreachable' and p['status']=='SUCCESS'],'status_U_count':len(u) if hs else 'UNKNOWN','rich_state':pr['state'],'rich_error':pr['error'],'missing_sites':pr['missing_sites'],'reader':reader_result,'protected_epochs':'PROTECTED.json','full_source_tool_request_export_binding':{'request':rh,'source':req['std_sha'],'tool':req['tool_sha'],'control':HEAD,'cfg':g['effective_cfg'],'argv':g['argv']},'location_exception_applied':False})
            q={'id':rid,'rank':rank,'selector':selector,'mode':row['mode'],'target':row['target'],'unwind':row['unwind'],'domain':domains[rid],'scope_classification':row['scope_classification'],'native_verdict':h.get('outcome',{}).get('verdict','UNKNOWN_INCOMPLETE_EXPORT'),'native_property_count':h.get('n_properties','UNKNOWN_NO_COMPLETED_NATIVE_INVENTORY'),'status_counts':dict(collections.Counter(p['status'] for p in props)) if hs else 'UNKNOWN','class_status_counts':{cl:dict(collections.Counter(p['status'] for p in props if p['class']==cl)) for cl in sorted({p['class'] for p in props})} if hs else 'UNKNOWN','literal_roles':literal,'covers':covers if hs else 'UNKNOWN','unsupported_guards':guards if hs else 'UNKNOWN','native_unsupported_constructs':h.get('unsupported_constructs','UNKNOWN'),'U_count':len(u) if hs else 'UNKNOWN','failed_properties':fail if hs else 'UNKNOWN','missing_location':bad if hs else 'UNKNOWN','actual_rich_reader':reader_result or 'NO_COMPLETED_NATIVE_INVENTORY','native_registration':reg,'providers':providers,'PFC':pfc,'binding':{'source_binding':binding,'native_metadata_state':bm['native_metadata_state'],'compiler_identity_status':bm['compiler_identity_status'],'gaps':bm['rows'],'flags':req['flags'],'effective_cfg':g['effective_cfg'],'init':'Source-written typed initialized values; no independent initialization-mask/dstinit theorem','caller':'Exact harness/backing/base/normal-return frame only; no generic caller lifting'},'producer':pick(can,['status','outcome','reason','s3_expected_match']),'strict_expected_match':False,'provisional_S1':('FIXED_NEGATIVE_EXACT_LABEL_OBSERVED' if row['expected']=='DETECTED' else 'BOUNDED_NATIVE_SUCCESS_ALL_LITERAL_ROLES_COVERS_LOCATED_PENDING_U_GUARD_REVIEW' if hs else 'INELIGIBLE_NO_COMPLETED_NATIVE_RESULT'),'source_reported_candidate_eligible_for_review':bool(hs and row['expected']=='SUCCESS'),'qualification_admitted':False,'eligible_as_init_leaf_or_provider_summary':False,'proof_credit':'NONE','members':{n:{'member':gp+n,'sha256':sha(members[gp+n])} for n in ('receipt.json','compile/receipt.json','binding-metadata.json','export.json','properties.json')}}
            qual.append(q);properties[rid]={'selector':selector,'state':pr['state'],'properties':props if hs else 'UNKNOWN_NO_COMPLETED_NATIVE_INVENTORY','member':gp+'properties.json','sha256':sha(members[gp+'properties.json'])}
            roots.append({'id':rid,'rank':rank,'selector':selector,'mode':row['mode'],'target':row['target'],'unwind':row['unwind'],'native_verdict':q['native_verdict'],'canonical_status':can['status'],'canonical_outcome':can['outcome'],'group_state':g['state'],'original_exception':g.get('original_exception'),'original_exit':execution['original_exit_code'],'signal':execution['signal'],'worker_exit':sup['worker_exit'],'sealed':True,'argv':g['argv'],'effective_cfg':g['effective_cfg'],'invocation_id':g['invocation_id'],'cargo_target_dir':g['cargo_target_dir'],'native_start_events':g['native_start_events'],'source_before':g['source_before'],'source_after':g['source_after'],'source_under_test':g['source_under_test'],'launch':launch,'native_export_state':stock['run_state']})
            timed=execution.get('termination_reason')=='timeout'
            if timed:need(co['state']=='COMPLETE' and co['elapsed_upper_bound_seconds']<180 and execution['rss_peak_kib']<ceff and execution['timed_out'] and execution['signal']==15 and execution['original_exit_code']==-15 and sup['elapsed_seconds']<sup['worker_wall_limit_seconds'],rid+' exact child600 wall timeout not compile/RSS/slot/global')
            cost.append({'id':rid,'compile':co,'compile_elapsed_upper_bound_seconds':co['elapsed_upper_bound_seconds'],'native_verification_time_s':h.get('resources',{}).get('verification_time_s','UNKNOWN_CENSORED_NO_COMPLETED_EXPORT'),'native_wall_time_s':stock.get('wall_time_s','UNKNOWN_INCOMPLETE_EXPORT'),'execution':pick(execution,['elapsed_seconds','original_exit_code','signal','timed_out','termination_reason','child_shutdown_verified','rss_peak_kib','rss_scope','rss_sample_period_seconds','component_group_peak_kib','component_rss_scope','cleanup_errors','process_identity']),'memory_admission':mem,'effective_cap_kib':ceff,'effective_cap_formula':'min(local6GiB, outer12GiB, available-2GiB)','limits':g['r5_limits'],'worker_supervision':pick(sup,['worker_exit','cutoff','elapsed_seconds','limit_initiated','outer_sampled_peak_kib','outer_rss_scope','supervisor_error','orphan_survivors_at_worker_exit','worker_wall_limit_seconds','lifecycle_events_omitted']),'containment':pick(sup['containment'],['verified','scope','elapsed_seconds','signals','reaped_adopted','worker_exit']),'lifecycle_diagnostics':{'events':sup['lifecycle_events'],'omitted':sup['lifecycle_events_omitted']},'cutoff_cause':'CHILD_600_WALL_TIMEOUT' if timed else 'NONE_COMPLETED','cutoff_phase':'AFTER_INITIAL_EXPORT_AND_NATIVE_START; exact symex/backend subphase UNKNOWN' if timed else 'COMPLETED','censoring':'UNFINISHED_NATIVE_RESULT_UNKNOWN' if timed else 'NONE','residual_budget_after_compile_marker_s':600-co['elapsed_upper_bound_seconds'],'symex_backend_steps_VCC':'UNKNOWN_NOT_EXPORTED','rss_at_signal_true_kernel_cgroup_peak':'UNKNOWN','next_root':pins['ordered_rows'][rank] if rank<7 else None,'continuation':'verified cleanup precedes next serial launch; final row campaign completed' if timed else 'verified cleanup'})
        need(len({x['invocation_id'] for x in roots})==7,'all7 fresh singleton namespaces')
        serial=[];prior_end=None
        for row in roots:
            rid=row['id'];sup=data['workers/'+rid+'-supervision.json'];launch=row['launch']['monotonic'];start=row['native_start_events'][0]['monotonic']
            need(launch<=sup['monotonic_start']<=start<=sup['monotonic_end'] and (prior_end is None or prior_end<=launch),rid+' observed monotonic serial launch/native-start/cleanup order')
            serial.append({'id':rid,'launch_monotonic':launch,'supervision_start':sup['monotonic_start'],'native_start':start,'supervision_end':sup['monotonic_end'],'prior_cleanup_end':prior_end});prior_end=sup['monotonic_end']
        write('SERIAL-ORDER.json',{'same_host_monotonic_order_verified':True,'rows':serial,'scope':'Observed launches/native start/worker supervision boundaries; exact inner signal timestamp UNKNOWN'})
        need(sum(q['native_property_count'] for q in qual if isinstance(q['native_property_count'],int))==602,'exact602 native properties across5 completed rows; incomplete counts UNKNOWN')
        need(len(us)==28 and all(x['source_local_argument'] for x in us),'all28 U invocation-specific source-local arguments')
        need(sum(len(q['unsupported_guards']) for q in qual if isinstance(q['unsupported_guards'],list))==7,'all7 observed SUCCESS unsupported guards retained; incomplete rows UNKNOWN')
        need(sum(q['native_verdict']=='SUCCESS' for q in qual)==2 and sum(q['native_verdict']=='FAILURE' for q in qual)==3,'native two successes three exact failures two censored')
        # Required portable-prefix/cardinality boundaries, using frozen actual readers.
        victim=local/'groups/s3-i_p01_b01_fullu8/export.json';original=victim.read_bytes()
        for name,replacement in [('missing_required_member',None),('changed_required_member',original+b' ')]:
            if replacement is None:victim.unlink()
            else:victim.write_bytes(replacement)
            try:c.sealed(local)
            except (c.GlobalFailure,ValueError,OSError):tests.append({'test':name,'result':'REJECT'})
            else:raise AssertionError(name+' accepted')
            victim.write_bytes(original)
        badg=copy.deepcopy(data['groups/s3-i_p01_b01_fullu8/receipt.json']);badg['tool_fingerprints_after']['binaries']['kani_driver']['sha256']='0'*64
        try:ev.protected(badg,req,data['baseline.json'],data['workers/i_p01_b01_fullu8-supervision.json'],rh)
        except ev.EvidenceError:tests.append({'test':'changed_protected_binary','result':'REJECT'})
        else:raise AssertionError('changed protected binary accepted')
        termpath=local/'receipt.json';termbytes=termpath.read_bytes()
        for state,completed in [('SELECTED_PARTIAL',pins['ordered_rows']),('STOPPED',pins['ordered_rows']),('STOPPED',[])]:
            for name,val in [('missing',None),('null',None),('bool',True),('string','7'),('zero',0),('six',6),('eight',8)]:
                bad=copy.deepcopy(data['receipt.json']);bad['state']=state;bad['stop_reason']='SYNTHETIC_GLOBAL_STOP' if state=='STOPPED' else None;bad['s3_campaign']['completed']=completed
                if name=='missing':del bad['s3_campaign']['selected_roots']
                else:bad['s3_campaign']['selected_roots']=val
                termpath.write_bytes(canon(bad))
                for route in ('local','upload'):
                    if route=='upload':
                        changed=copy.deepcopy(packet);b=canon(bad);changed['files']['receipt.json']={'encoding':'utf-8','text':b.decode(),'bytes':len(b),'sha256':sha(b)};(upload/'group-evidence.json.gz').write_bytes(gzip.compress(canon(changed),mtime=0))
                    try:public.collect([local if route=='local' else upload],req)
                    except c.GlobalFailure as exc:
                        need(str(exc)=='S3 terminal selected-root cardinality mismatch','exact cardinality rejection '+state+'/'+str(len(completed))+'/'+name+'/'+route)
                        tests.append({'test':'selected_roots_'+name,'state':state,'completed_count':len(completed),'route':route,'result':'REJECT_CARDINALITY'})
                    else:raise AssertionError('invalid selected_roots accepted')
        termpath.write_bytes(termbytes);(upload/'group-evidence.json.gz').write_bytes(gz)
        need(all((local/n).read_bytes()==b for n,b in members.items()),'all authentic evidence bytes restored after bounded adverse controls')
    write('ROOTS.json',{'rows':roots,'request':req,'deferred':req['s3']['deferred'],'deferred_state':'NOT_SELECTED_NO_PROMOTION','domain_unwind':domain_doc,'source_files':sourcefiles,'physical_inode_realpath_identity':'UNKNOWN_NOT_EXPORTED'})
    with (HERE/'ROOTS.csv').open('w',newline='') as f:
        fields=['id','rank','mode','target','unwind','native_verdict','canonical_status','canonical_outcome','group_state','original_exit','signal','worker_exit','sealed'];w=csv.DictWriter(f,fields,lineterminator='\n');w.writeheader();w.writerows({k:x[k] for k in fields} for x in roots)
    write('PROTECTED.json',{'baseline':data['baseline.json'],'epochs':epochs,'assurance':'SOURCE_REPORTED observed clean identities and exact hash/path snapshots; no independent compiler/MIR causal binding'})
    write('NATIVE-PROPERTIES.json',properties)
    write('QUALIFICATION.json',{'schema':'s34-terminal-qualification-v1','assurance':'S1 Profiles v4 SOURCE_REPORTED provisional; independent B1/B2 NONE','strict_policy':req['unreachable_admission'],'producer_expected_matches':0,'rows':qual,'U_count':len(us),'U_instances':us,'observed_SUCCESS_unsupported_guards':7,'incomplete_property_U_guard_counts':'UNKNOWN_NOT_ZERO','source_site_plan':{'assertions':planned_assertions,'covers':planned_covers,'note':'Source sites/labels only; observed native properties602 across5 completed roots, not19/46. All17 fallback and9 network length covers remain UNKNOWN.'},'qualification_admitted':False,'qualified_new_leaves':0,'qualified_init_provider_contexts':0,'proof_obligations_closed':0,'independent_credit':'NONE'})
    write('METADATA-GAP.json',{'schema':'s34-location-audit-v1','rows':gaps,'completed_rows':5,'observed_completed_location_defects':0,'incomplete_rows':2,'incomplete_location_defects':'UNKNOWN_NO_COMPLETED_NATIVE_INVENTORY','old_admissions':{'f74025e493a627962842e8f7bc6a2766d33dd300':'ORIGINAL_RUN_IDS_ONLY','ff193cc35690a5daabaa849d412c58d9f286d893':'ORIGINAL_RUN_IDS_ONLY'},'new_exact_case_proposal':'NONE_NEEDED_FOR_OBSERVED_COMPLETED_ROWS; NOT_APPLIED','shared_emitter_source_MIR_origin':'UNKNOWN_NOT_ESTABLISHED','status_U_vs_class_unreachable_SUCCESS':'Different partitions; every observed record preserved in NATIVE-PROPERTIES.json','policy_changed':False,'U_policy':'REJECT_ALL proposal DISABLED','original_producer_history_preserved':True})
    write('COST.json',{'campaign_elapsed_seconds':data['receipt.json']['phase_elapsed_seconds'],'caps':pins['caps'],'setup':pick(data['setup/receipt.json'],['setup_total_seconds','elapsed_seconds','rss_peak_kib','rss_status','rss_sample_period_seconds','component_group_peak_kib','component_rss_scope','original_exit_code','child_shutdown_verified']),'job':pick(jobs[0],['id','started_at','completed_at','steps']),'rows':cost,'compiler_metric':'Upper bound to initial stock export includes std compilation/link/observer delay; not exclusive CPU compilation.','native_verification_metric':'resources.verification_time_s as exported; not exclusive backend duration.','wholechild_campaign_setup_metrics':'Distinct scopes, not added to backend or used to invent symex timing.','rss_metric':'50ms nominal sampled non-atomic owned PGID VmRSS; component peaks not simultaneous; no kernel/cgroup/tree peak claim.','comparison':'NO_SPEEDUP_CLAIM. Fixed insert base1/p1 differs from earlier variable-base geometries; no universal cost-fit theorem.','accounting':'TRACKING_ONLY_NO_LEDGER_WRITES','signal_precision':'Signal15/originalexit-15 and verified reap exported; exact signal monotonic time/true RSS at signal UNKNOWN.'})
    write('PROVENANCE.json',{'task':TASK,'terminal_addendum':ADDENDUM,'source_tool_control_trigger':trees,'request_sha256':rh,'workflow_sha256':sha(wf),'checkout_depths':{'control':7,'source':5,'tool':2},'review':pins['review'],'package':pins['package'],'root_GO':pins['root_GO'],'root_recheck':{'path':gopath,'sha256':sha(gobytes),'identities_checked':True},'artifact_metadata':arts[0],'transport_integrity':'artifact-integrity.json','payload_sha256':sha(gz),'uncompressed_sha256':sha(raw),'frozen_reader_files':frozen,'source_file_hashes':sourcefiles,'actual_binary_snapshots':'PROTECTED.json','source_tool_binding_scope':'Observed native registration/exports/compile/argv/cfg/namespaces; independent AST/MIR/property and physical-inode causality UNKNOWN','connected_job_detail_recovery':'direct /actions/jobs/135346092818 rejected INVALID_ARGUMENT by connector; supported /actions/runs/44460583125/jobs succeeded; no logs read','base_helpers':['run-44416629057/acquire.py','run-44439462279/replay.py','exact executed s34_campaign/collect/s34_policy/s3_evidence/rich_evidence Python readers'],'restrictions':'Only new intake output; no native/compiler/CI/raw/full/GCS/ledger/policy changes, no review/subagents/model changes/push.'})
    write('VALIDATION.json',{'status':'PASS','checks_count':len(CHECKS),'checks':CHECKS,'adverse_tests':tests,'scope':'bounded offline static source/integrity/native export/protected epochs/prefix replay only; no full host suite/native runner','evidence_modified':False,'policy_modified':False})
    write('RESULT.json',{'schema':'s34-bridge1-r1-terminal-intake-v1','status':'READY','run':44460583125,'attempt':1,'native_run':'completed/failure','classification':'SELECTED_PARTIAL_NATIVE_2SUCCESS_3EXPECTED_FAILURE_2CHILD_WALL_TIMEOUT; STRICT0; NO_ADMISSION','campaign_elapsed_seconds':data['receipt.json']['phase_elapsed_seconds'],'global_stop':False,'completed_sealed_prefix':7,'native_success':2,'intended_native_negative_failures':3,'child_wall_timeout_unknown_results':2,'strict_expected_matches':0,'provisional_S1_positive_candidates_for_review':2,'provisional_S1_negative_label_observations':3,'observed_completed_missing_location_records':0,'incomplete_locations':'UNKNOWN','U_source_local_assessments':len(us),'observed_SUCCESS_unsupported_guards_retained':7,'qualified_new_leaves':0,'proof_obligations_closed':0,'proof_credit':'NONE','review':'Review14 follows root exact hash/pins/replay/completeness/cost check; NOT_ISSUED_HERE','policy_or_accounting_changed':False,'remaining_unknown':['Two incomplete native inventories, all symbolic-family roles and17/9 length covers unobserved','Exact symex/backend phase, censored verification time, signal timestamp/kernel peak','Independent AST/MIR/property/caller binding and shared emitter origin','Generic trait/callback/ownership/panic/init-mask theorem, full N16/N32, merge/provider/sort8 obligations'],'handoff':'Root checks immutable READY commit and manifest, then separately issues14; no automatic admission or next CI/S4 implementation.'})
    print(json.dumps({'status':'PASS','checks':len(CHECKS),'roots':7,'U':len(us),'guards':7,'observed_completed_location_gaps':0,'adverse_tests':len(tests)}))

if __name__=='__main__':main()
