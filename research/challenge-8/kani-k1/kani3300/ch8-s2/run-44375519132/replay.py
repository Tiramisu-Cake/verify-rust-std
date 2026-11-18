#!/usr/bin/env python3
"""Offline structured intake. No compiler, native runner, CI, logs or mutation of inputs."""
import ast, base64, gzip, hashlib, importlib, json, subprocess, sys
from datetime import datetime
from pathlib import Path
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
CONTROL = Path('/root/kani-ch8-s2-r5-r1-stable-final-w13')
STD = Path('/root/verify-rust-std-ch8-s2-r4-r1-w13')
CTRL = '63535098ab85c70c8707eee0afd65f53c9ef566a'
HEAD = '33c687e43de170d4b936ed3e9c29f6b35c192419'
checks = []
def sha(b): return hashlib.sha256(b).hexdigest()
def read(n): return json.loads((HERE/n).read_bytes())
def write(n, v): (HERE/n).write_text(json.dumps(v, indent=2, ensure_ascii=False)+'\n')
def need(v, label):
    if not v: raise AssertionError(label)
    checks.append(label)
def git(repo, *args): return subprocess.check_output(['git','-C',str(repo),*args])
def blob(repo, commit, path): return git(repo, 'show', commit+':'+path)
def seconds(a,b): return (datetime.fromisoformat(b.replace('Z','+00:00'))-datetime.fromisoformat(a.replace('Z','+00:00'))).total_seconds()

def main():
    pins=json.loads((HERE.parent/'postrun-r5/INPUTS.json').read_bytes())
    pins.update(status='ISSUED_OWNER2240_NEW11_SUPERSEDES_PREPARED_INTAKE13',task='TASK-CH8-S2-R5-INTAKE-SNAPSHOT-W11.md',task_g0='a6b52a0aa3c145cfabb5989b2e1e49780275c6bb')
    pins['budget_reference']={'ledger_g0':'1085e94c8c1b6df072721c47abd8632b1600ecb2','item1':[30,30],'item2':[11,17],'total':[41,47],'authority':'OWNER_REPORTED_REFERENCE_ONLY; no worker accounting authority'}
    write('INPUTS.json',pins)
    run=read('github-run.json'); arts=read('github-artifacts.json')['artifacts']; jobs=read('github-jobs.json')['jobs']; integrity=read('artifact-integrity.json')
    need((run['id'],run['run_attempt'],run['status'],run['conclusion'],run['event'])==(44375519132,1,'completed','failure','push'),'native terminal run identity')
    need(run['head_sha']==HEAD and run['head_branch']==pins['branch'] and run['head_commit']['tree_id']==pins['tree'],'actual trigger/ref/tree identity')
    need(len(arts)==1 and arts[0]['id']==14463098208 and arts[0]['name']==pins['artifact'] and not arts[0]['expired'],'one authorized compact artifact')
    a=arts[0]
    need(a['digest']=='sha256:'+integrity['sha256'] and a['size_in_bytes']==integrity['bytes'] and integrity['digest_checked_before_zip_open'] and not integrity['transport_saved'],'digest first; no saved ZIP')
    need(a['workflow_run']['id']==run['id'] and a['workflow_run']['head_sha']==HEAD and a['workflow_run']['head_branch']==pins['branch'],'artifact execution binding')
    need(len(jobs)==1 and jobs[0]['head_sha']==HEAD and jobs[0]['run_attempt']==1 and jobs[0]['conclusion']=='failure','native job binding')
    need(git(CONTROL,'rev-parse',HEAD+'^{tree}').decode().strip()==pins['tree']==git(CONTROL,'rev-parse',CTRL+'^{tree}').decode().strip(),'actual/reviewed same tree')
    for commit in [CTRL,HEAD]: need(git(CONTROL,'show','-s','--format=%P',commit).decode().strip()==pins['parent'],'same sole parent '+commit)
    for kind,repo in [('source',STD),('tool',CONTROL)]:
        need(git(repo,'rev-parse',pins[kind]['sha']+'^{tree}').decode().strip()==pins[kind]['tree'],'pinned '+kind+' tree')
    request_raw=blob(CONTROL,HEAD,'ch8-s1-control/CI-REQUEST.json'); request=json.loads(request_raw)
    need(sha(request_raw)==pins['request_sha256'] and request_raw==blob(CONTROL,CTRL,'ch8-s1-control/CI-REQUEST.json'),'actual/reviewed request bytes')
    workflow=blob(CONTROL,HEAD,'.github/workflows/ch8-s2.yml')
    need(sha(workflow)==pins['workflow_sha256'] and workflow==blob(CONTROL,CTRL,'.github/workflows/ch8-s2.yml'),'actual/reviewed workflow bytes')
    payloads={}
    for path,h in request['ci_payload_sha256'].items():
        raw=blob(CONTROL,HEAD,path)
        need(sha(raw)==h and raw==blob(CONTROL,CTRL,path),'reviewed/executed payload '+path)
        payloads[path]={'bytes':len(raw),'sha256':h}
    source_hashes={}
    for key in ['changed_file_sha256','cfg_pfc_source_sha256','contract_stack_source_sha256','lexical_source_sha256','ordinary_contract_source_sha256']:
        for path,h in request[key].items():
            need(sha(blob(STD,pins['source']['sha'],path))==h,'source '+key+' '+path); source_hashes[path]=h
    replay=HERE/'replay-control'; replay.mkdir(exist_ok=True)
    names={Path(p).stem for p in request['ci_payload_sha256'] if p.startswith('ch8-s1-control/') and p.endswith('.py')}
    todo=['collect','r5_campaign','negative_oracle']; done=set()
    while todo:
        name=todo.pop()
        if name in done: continue
        done.add(name); raw=blob(CONTROL,HEAD,'ch8-s1-control/'+name+'.py');(replay/(name+'.py')).write_bytes(raw)
        for node in ast.walk(ast.parse(raw)):
            deps=[x.name.split('.')[0] for x in node.names] if isinstance(node,ast.Import) else [node.module.split('.')[0]] if isinstance(node,ast.ImportFrom) and node.module else []
            todo.extend(n for n in deps if n in names and n not in done)
    (replay/'CI-REQUEST.json').write_bytes(request_raw)
    sys.path.insert(0,str(replay)); r=importlib.import_module('runner'); c=importlib.import_module('collect'); campaign=importlib.import_module('r5_campaign'); policy=importlib.import_module('s2_policy'); neg=importlib.import_module('negative_oracle')
    need(r.load_request()==request,'exact request validation; no runner main called')
    gz=(HERE/'group-evidence.json.gz').read_bytes(); need(sha(gz)==integrity['payload_sha256'] and len(gz)==integrity['payload_bytes'],'retained compact digest')
    raw=gzip.decompress(gz);need(len(raw)<=32*1024*1024 and sha(raw)==integrity['uncompressed_sha256'],'compact uncompressed bound/hash')
    doc=json.loads(raw);need(doc['state']=='PACKAGED' and doc['error'] is None,'packaged structured evidence')
    d={}; b={}
    for name,item in doc['files'].items():
        data=item['text'].encode() if item.get('encoding','utf-8')=='utf-8' else base64.b64decode(item['text'],validate=True)
        need(len(data)==item['bytes'] and sha(data)==item['sha256'],'structured member '+name)
        b[name]=data;d[name]=json.loads(data)
    need(d==read('embedded-projection.json') and len(d)==99,'exact 99-member structured projection')
    need(d['campaign-start.json']['request_data']==request and d['receipt.json']['request_sha256']==sha(request_raw),'campaign frozen request binding')
    collected=c.collect([HERE],request);write('collected.json',collected)
    need(len(collected['rows'])==11 and not collected['selected_missing_groups'],'exact reviewed collector replay all11')
    seals=campaign.sealed(HERE,c.read_bytes,d['receipt.json']['r5_campaign']['completed'])
    need(list(seals)==request['r5']['selected'][:6],'portable six-row completed prefix')
    need(all(name in b for s in seals.values() for name in s['files']),'every required sealed member retained; local raw logs unnecessary')
    # One bounded error-path replay of the exact initial guard on the actual interrupted receipt.
    original_read,original_record=campaign.read,campaign.record_supervision
    campaign.read=lambda path:d['groups/r5-merge_count_corrupt/receipt.json']
    campaign.record_supervision=lambda *args:None
    try:
        try: campaign.root_outcome(HERE,request,'merge_count_corrupt',d['workers/merge_count_corrupt-supervision.json'])
        except campaign.GlobalFailure as exc: need(str(exc)=='source_tool_request_binary_snapshot_drift_or_unavailable','actual missing-after guard reproduces generic GlobalFailure without native execution')
        else: raise AssertionError('missing snapshot guard did not stop')
    finally: campaign.read, campaign.record_supervision=original_read,original_record
    # Portable seal rejection is checked using in-memory reads only.
    victim=next(iter(seals['swap_pfc']['files']))
    for case in ['missing','tampered']:
        def corrupt(path):
            name=str(path.relative_to(HERE))
            if name==victim:
                if case=='missing': raise FileNotFoundError(name)
                return b[name]+b' '
            return b[name]
        try: campaign.sealed(HERE,corrupt,['swap_pfc'])
        except (FileNotFoundError,campaign.GlobalFailure): need(True,'portable seal rejects '+case+' required structured member')
        else: raise AssertionError('seal accepted '+case)
    expected={k:request[k] for k in ['std_sha','std_tree','tool_sha','tool_tree','changed_file_sha256']}
    inventories=[]; costs=[]; rows=[]; identities=[]; order=[]
    for decl in request['rows']:
        rid=decl['id']; selected=rid in request['r5']['selected']; prefix='groups/r5-'+rid+'/'
        g=d.get(prefix+'receipt.json',{}); row=d[rid+'/receipt.json'];comp=d.get(prefix+'compile/receipt.json',{});sup=d.get('workers/'+rid+'-supervision.json',{})
        stock=d.get(prefix+'export.json',{}); harnesses=stock.get('harnesses',[]);h=harnesses[0] if harnesses else {};rich=d.get(prefix+'properties.json',{});rh=next((x for x in rich.get('harnesses',[]) if x['name']==decl['selector']),{});props=rh.get('properties',[])
        if selected and g.get('invocation_id'):
            need(g['argv']==r.build_argv(Path('/home/runner/work/kani/kani/export'),Path('/home/runner/work/kani/kani/tool'),[decl['selector']],34,Path('/home/runner/work/_temp/ch8-s1-receipts')/prefix/'export.json'),'exact singleton argv '+rid)
            need(g['effective_cfg']==request['flags']['RUSTFLAGS'] and g['cargo_target_dir'].endswith('/target/ch8-s1-cargo/'+g['invocation_id']),'cfg and fresh target '+rid)
            need(g['source_before']==expected and g['request_sha256']==sha(request_raw),'before source/request '+rid)
            if rid in seals:
                need(g['source_after']==expected and g['binary_identity']=='MATCH' and r.fingerprints_match(g['tool_fingerprints_before'],g['tool_fingerprints_after']) and not g['snapshot_errors'],'protected after/binary snapshots '+rid)
            order.append({'id':rid,'rank':request['r5']['selected'].index(rid)+1,'launch':d['workers/'+rid+'-launch.json'],'native_start_events':g.get('native_start_events','UNKNOWN_NOT_PUBLISHED'),'sealed':rid in seals,'worker_exit':sup.get('worker_exit'),'next_launched':None})
        if h:
            actual=policy.expected_observation(decl,row['export'],rh)
            need(actual==row['r5_expected_match']==False,'unchanged expected-observation oracle rejects '+rid)
            need(h['name']==decl['selector'] and h['attributes']['unwind_value']==34,'native selector/unwind '+rid)
        successful={x['description'] for x in props if x['class']!='cover' and x['status']=='SUCCESS'}
        inventories.append({'id':rid,'selected':selected,'assurance':decl['assurance'],'selector':decl['selector'],'expected':decl['expected'],'required_covers':decl['required_cover_messages'],'required_success_messages':decl.get('required_success_messages',[]),'expected_negative_oracle':decl.get('oracle'),'native':h or 'UNKNOWN_NO_FINAL_EXPORT','rich_state':rich.get('state','NOT_RETAINED'),'property_count':len(props) if props else None,'properties_by_class_status':{cl:{st:sum(x['class']==cl and x['status']==st for x in props) for st in sorted({x['status'] for x in props if x['class']==cl})} for cl in sorted({x['class'] for x in props})},'covers':[x for x in props if x['class']=='cover'],'non_success_checks':[x for x in props if x['class']!='cover' and x['status']!='SUCCESS'],'required_success_labels_absent':sorted(set(decl.get('required_success_messages',[]))-successful),'negative_identity_only_match':neg.matches(h,decl['oracle']) if decl.get('oracle') and h else None,'negative_policy_match':actual if decl.get('oracle') and h else None,'native_start_events':g.get('native_start_events','UNKNOWN_NOT_PUBLISHED' if sup else 'NOT_STARTED_OR_NOT_SELECTED')})
        ex=g.get('execution',comp.get('group_execution',{}));using_compile='execution' not in g and bool(ex)
        costs.append({'id':rid,'selected':selected,'cost_status':'RECORDED_SCOPED' if ex else 'UNKNOWN_NOT_ZERO','compile_state':comp.get('state','NOT_STARTED' if not sup else 'UNKNOWN'),'compile_elapsed_upper_bound_seconds':comp.get('elapsed_upper_bound_seconds'),'native_cargo_finished_dev_seconds':None,'verification_time_s':h.get('resources',{}).get('verification_time_s'),'execution_scope':'COMPILE_RECEIPT_PARTIAL_CHILD_EXECUTION' if using_compile else 'SINGLETON_DRIVER_COMPILE_PLUS_NATIVE_VERIFICATION' if ex else 'NO_EXECUTION_COST_RECORDED','execution':{k:v for k,v in ex.items() if k not in ['rustc_diagnostics']},'worker_supervision':{k:v for k,v in sup.items() if k!='containment'},'containment':{k:v for k,v in sup.get('containment',{}).items() if k!='observed'},'phases':{key:'UNKNOWN_NOT_EXPOSED_IN_STRUCTURED_EXPORT' for key in ['instrumentation_seconds','symex_seconds','solver_seconds','body_seconds','model_seconds','checker_seconds','summary_seconds','VCC','steps','true_tree_peak_RSS','exact_root_RSS']},'compile_receipt':prefix+'compile/receipt.json' if comp else None})
        # Only parse the explicitly retained bounded preview, never open raw logs.
        import re
        hits=re.findall(r'Finished `dev` profile .*? in ([0-9.]+)s',comp.get('stderr',{}).get('tail',''))
        if hits:costs[-1]['native_cargo_finished_dev_seconds']=float(hits[-1])
        fragments=[]
        for capture_name,capture in [('group',g),('compile',comp)]:
            for stream in ['stdout','stderr']:
                for edge in ['head','tail']:
                    text=capture.get(stream,{}).get(edge,'')
                    matched=[{'preview_line':i,'text':line} for i,line in enumerate(text.splitlines(),1) if re.search(r'Runtime (?:Symex|Solver|decision procedure|Postprocess Equation|Convert SSA|Post-process)|size of program expression:|Generated .* VCC|slicing removed|instrumentation|Finished `dev`',line)]
                    if matched:fragments.append({'member':prefix+'receipt.json' if capture_name=='group' else prefix+'compile/receipt.json','pointer':'/'+stream+'/'+edge,'metrics':matched})
        costs[-1]['bounded_native_metric_fragments']=fragments
        costs[-1]['fragment_scope']='Exact source-reported lines retained in bounded previews; head/tail may overlap. Individual Runtime Solver/decision procedure values can describe repeated property-solving iterations. No sum or aggregate phase duration inferred; omitted intervals and final backend outcome UNKNOWN for cutoffs.'
        if not h: inventories[-1]['required_success_labels_absent']='UNKNOWN_NO_FINAL_INVENTORY'
        rows.append({'id':rid,'selection':'SELECTED' if selected else 'DEFERRED_NOT_SELECTED','assurance':decl['assurance'],'worker_started':bool(sup),'native_start':'OBSERVED_SINGLETON' if g.get('native_start_events') else 'UNKNOWN_NOT_PUBLISHED' if sup else 'NOT_STARTED' if selected else 'NOT_SELECTED','sealed':rid in seals,'compile':comp.get('state','NOT_STARTED'),'status':row['status'],'collector_outcome':next(x['outcome'] for x in collected['rows'] if x['id']==rid),'native_outcome':h.get('outcome','UNKNOWN_NO_FINAL_EXPORT'),'r5_expected_match':row.get('r5_expected_match','NOT_RECORDED'),'reason':row.get('reason'),'proof_credit':'NONE'})
        if g.get('invocation_id'):
            meta=d.get(prefix+'binding-metadata.json')
            identities.append({'id':rid,'invocation_id':g['invocation_id'],'cargo_target_dir':g['cargo_target_dir'],'argv':g['argv'],'effective_cfg':g['effective_cfg'],'source_under_test':g['source_under_test'],'before':g.get('tool_fingerprints_before'),'after':g.get('tool_fingerprints_after','UNKNOWN_NOT_RECORDED'),'source_before':g.get('source_before'),'source_after':g.get('source_after','UNKNOWN_NOT_RECORDED'),'binding_metadata':g.get('binding_metadata','UNKNOWN_NOT_RECORDED'),'native_binding':{k:meta[k] for k in ['compilation_id','compiler_identity_status','identity_scope','rows','configuration_sha256']} if meta else 'UNKNOWN_NOT_RECORDED'})
    order.sort(key=lambda x:x['rank'])
    for i,x in enumerate(order):x['next_launched']=order[i+1]['id'] if i+1<len(order) else 'NONE_GLOBAL_STOP'
    need(len({x['invocation_id'] for x in identities})==7,'seven unique invocation namespaces')
    need(sum(x['required_cover_count'] for x in request['rows'])==20 and sum(x['required_cover_count'] for x in request['rows'] if x['id'] in request['r5']['selected'])==16,'full20/selected16 cover inventory')
    need(len(order)==7 and sum(bool(x.get('native_start_events') and isinstance(x['native_start_events'],list)) for x in order)==6,'seven worker launches, six retained exact native starts, interrupted root native start UNKNOWN')
    write('VERDICTS.json',{'rows':rows,'inventory':inventories,'full_inventory':request['r5']['full_inventory'],'selected_inventory':request['r5']['selected_inventory'],'deferred':request['r5']['deferred'],'native_successes':1,'native_failures':3,'accepted_exact_negative_roles':0,'r5_expected_matches':0,'qualification':'NOT_GRANTED','B1':'NOT_ESTABLISHED','B2':'NOT_ESTABLISHED','closed_proof_obligations':0,'proof_credit':'NONE'})
    steps=jobs[0]['steps'];step_cost=[{'name':s['name'],'conclusion':s['conclusion'],'started_at':s.get('started_at'),'completed_at':s.get('completed_at'),'wall_seconds':seconds(s['started_at'],s['completed_at']) if s.get('started_at') and s.get('completed_at') else None} for s in steps]
    write('COST.json',{'rows':costs,'limits':request['r5']['caps'],'additional_limits':{'setup_seconds':1800,'job_minutes':180,'checkout_depths':[7,5,2],'worker_wall_seconds':710,'durable_publication_reserve_seconds':10,'inner_CBMC_ceiling_seconds':600},'campaign_elapsed_seconds':d['receipt.json']['phase_elapsed_seconds'],'campaign_start_monotonic':d['campaign-start.json']['start_monotonic'],'setup':d['setup/receipt.json'],'job_wall_seconds':seconds(jobs[0]['started_at'],jobs[0]['completed_at']),'github_step_costs':step_cost,'scope':'Native source-reported cost observations. Child600 includes compile180. No subtraction into missing phases. PGID/owned RSS samples are not strict tree peaks; components are non-simultaneous. NOT_RUN costs UNKNOWN, no general32 extrapolation.'})
    write('ORDER.json',{'observed_order':order,'planned_order':request['r5']['selected'],'completed_prefix':list(seals),'completed_means':'DURABLY_SEALED_OBSERVATIONS; includes two UNKNOWN cutoffs, not six successful proofs','deferred':request['r5']['deferred']})
    write('PROVENANCE.json',{'actual_trigger':HEAD,'reviewed_control':CTRL,'same_tree':pins['tree'],'same_parent':pins['parent'],'source':pins['source'],'tool':pins['tool'],'request_sha256':sha(request_raw),'workflow_sha256':sha(workflow),'payloads':payloads,'source_file_hashes':source_hashes,'identities':identities,'compact':{'file_reference':'file_0000000009d48211ae0bf0cd22226ea7','artifact_id':a['id'],'digest':a['digest'],'transport_saved':False,'members':99},'settings':'PRESERVED','Fast':'OFF_PRESERVED','subagents':0,'review_assurance':'Pinned committed package/review/GO references from issued task; not fresh review or proof credit'})
    write('COMPLETENESS.json',{'packaging':doc['state'],'packaging_error':doc['error'],'diagnostic_retention':doc['diagnostic_retention'],'rustc_diagnostics':doc['rustc_diagnostics'],'all11_rows':True,'selected9':True,'deferred2':True,'seals_validated':list(seals),'sealed_members':{rid:s['files'] for rid,s in seals.items()},'local_only_digests_not_replayed':{rid:s.get('local_only_file_digests') for rid,s in seals.items()},'compiler_identity':'UNKNOWN_NOT_EXPORTED_BY_PINNED_PRODUCER','parser_binding':'reviewed collector exact structured digest/selector/crate/native metadata/rich-export checks; no AST/MIR/ADT or compiler-instance proof','proof_credit':'NONE'})
    trace=[]
    ranges={'r5_campaign.py':[(165,180),(245,268),(274,325)],'r5_runtime.py':[(99,160)],'runner.py':[(194,211),(874,939),(1047,1058),(1095,1110),(1150,1177)],'s2_policy.py':[(114,145)]}
    for name,spans in ranges.items():
        raw=blob(CONTROL,HEAD,'ch8-s1-control/'+name);lines=raw.decode().splitlines()
        trace.append({'path':'ch8-s1-control/'+name,'commit':HEAD,'sha256':sha(raw),'excerpts':[{'first':a,'last':z,'text':'\n'.join(str(i)+': '+lines[i-1] for i in range(a,min(z,len(lines))+1))} for a,z in spans]})
    write('SOURCE-TRACE.json',trace)
    write('VALIDATION.json',{'state':'PASS_READ_ONLY_INTAKE','checks':checks,'count':len(checks),'collector':'EXACT_REVIEWED_ACTUAL_TRIGGER_TREE_BYTES','portable_prefix':'6_VALID; REQUIRED_MISSING/TAMPERED_REJECTED','bounded_guard_replay':'ACTUAL_INTERRUPTED_GROUP_GENERIC_FAILURE_REPRODUCED','native_compiler_verifier_fullrunner_CI_invocations':0,'proof_credit':'NONE'})
    print(json.dumps({'checks':len(checks),'prefix':list(seals),'rows':[(x['id'],x['native_outcome'],x['r5_expected_match']) for x in rows]}))

if __name__=='__main__': main()
