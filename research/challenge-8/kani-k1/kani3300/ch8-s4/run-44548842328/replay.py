#!/usr/bin/env python3
"""Offline intake using exact frozen producer readers. Never runs CI/native/Validate."""
import base64, collections, copy, gzip, hashlib, importlib, json, re, subprocess, sys, tempfile
from pathlib import Path
sys.dont_write_bytecode=True
from arguments import argument
HERE=Path(__file__).resolve().parent
G0=HERE.parents[5]
BASE='research/challenge-8/kani-k1/kani3300/'
SOURCE=Path('/root/verify-rust-std-ch8-s4p-2-w13')
CONTROL=Path('/root/kani-ch8-s4p-2-r1-control-w13')
TOOL=Path('/root/kani-upstream-ch8-s1')
HEAD='d88fac48cf50a742f9f00026ba66e5e4353e1019'
CTRL='3d3fb715271e3b195c6e0eee3557d5b0a6aad00d'
STD=Path('/home/runner/work/kani/kani/export')
CHECKS=[]
def sha(b): return hashlib.sha256(b).hexdigest()
def canon(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def write(n,x): (HERE/n).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def git(repo,*args): return subprocess.check_output(['git','-C',str(repo),*args])
def blob(repo,rev,p): return git(repo,'show',rev+':'+p)
def need(x,label):
    if not x: raise AssertionError(label)
    CHECKS.append(label)
def pick(d,ks): return {k:d[k] for k in ks if k in d}
def located(p): return isinstance(p.get('file'),str) and bool(p['file']) and isinstance(p.get('line'),str) and re.fullmatch('[1-9][0-9]*',p['line']) is not None
def decode(e): return e['text'].encode() if e.get('encoding','utf-8')=='utf-8' else base64.b64decode(e['text'],validate=True)
def context(b,n,radius=5):
    ls=b.decode().splitlines(); return '\n'.join(f'{i+1}: {ls[i]}' for i in range(max(0,n-radius-1),min(len(ls),n+radius)))
def main():
    go=json.loads(blob(G0,'fef8170d86',BASE+'ch8-s4/network-r2-go/GO-REQUEST.json'))
    run=json.loads((HERE/'RUN-METADATA.json').read_text()); hm=json.loads((HERE/'HEAD-METADATA.json').read_text()); jobs=json.loads((HERE/'JOBS-METADATA.json').read_text())['jobs']
    connected=json.loads((HERE/'CONNECTED-METADATA.json').read_text()); a,=connected['artifacts']['artifacts']; integ=json.loads((HERE/'artifact-integrity.json').read_text())
    need(all(run[k]==v for k,v in {'id':44548842328,'run_attempt':1,'head_sha':HEAD,'head_branch':'uninit-ci/ch8-s4p-2-r2-20261119','event':'push','status':'completed','conclusion':'failure','path':'.github/workflows/ch8-s2.yml'}.items()),'connected run exact head/attempt/workflow/event/failure')
    need(len(jobs)==1 and jobs[0]['id']==135646722748 and jobs[0]['head_sha']==HEAD and jobs[0]['run_attempt']==1 and jobs[0]['conclusion']=='failure','attempt1 job exact identity/failure')
    need(hm['sha']==HEAD and hm['tree']==go['pins']['control']['tree'] and hm['parents']==[go['pins']['control']['sole_parent']],'connected head same reviewed tree/sole parent')
    need(a['workflow_run']['head_sha']==HEAD and a['workflow_run']['id']==run['id'] and a['name']=='ch8-s3-2-44548842328-1' and not a['expired'],'connected artifact run/head/name/notexpired')
    need(a['size_in_bytes']==integ['bytes'] and a['digest']=='sha256:'+integ['sha256'] and integ['metadata_first'] and integ['digest_checked_before_zip_open'] and not integ['transport_saved'],'metadata-first transport digest')
    gz=(HERE/'group-evidence.json.gz').read_bytes(); raw=gzip.decompress(gz); packet=json.loads(raw)
    need(sha(gz)==integ['payload_sha256'] and sha(raw)==integ['uncompressed_sha256'],'compact member/payload identities')
    need(packet['schema']=='ch8-s1-05-artifact-v1' and packet['state']=='PACKAGED' and packet['error'] is None,'complete compact packaging')
    data={};members={}
    for n,e in packet['files'].items():
        b=decode(e); need(len(b)==e['bytes'] and sha(b)==e['sha256'], 'structured member identity '+n);members[n]=b;data[n]=json.loads(b)
    need(len(data)==119,'all119 structured members')
    trees={}
    for name,repo,rev in [('source',SOURCE,go['pins']['source']['sha']),('tool',TOOL,go['pins']['tool']['sha']),('control',CONTROL,CTRL),('trigger',CONTROL,HEAD)]:
        tree=git(repo,'rev-parse',rev+'^{tree}').decode().strip();parent=git(repo,'show','-s','--format=%P',rev).decode().strip()
        expected=go['pins']['control' if name=='trigger' else name]
        need(tree==expected['tree'] and parent==expected['sole_parent'], name+' actual Git tree/sole parent')
        trees[name]={'sha':rev,'tree':tree,'sole_parent':parent}
    rb=blob(CONTROL,HEAD,'ch8-s1-control/CI-REQUEST.json');req=json.loads(rb);rh=sha(rb);wf=blob(CONTROL,HEAD,'.github/workflows/ch8-s2.yml')
    need(rh==go['request']['sha256'] and sha(wf)==go['workflow']['sha256'],'actual request/workflow GO hashes')
    need(rb==blob(CONTROL,CTRL,'ch8-s1-control/CI-REQUEST.json') and wf==blob(CONTROL,CTRL,'.github/workflows/ch8-s2.yml'),'reviewed vs executed same-tree request/workflow')
    for p,h in req['ci_payload_sha256'].items(): need(sha(blob(CONTROL,HEAD,p))==h,'frozen control payload '+p)
    sourcefiles={}
    for key in ['changed_file_sha256','cfg_pfc_source_sha256','contract_stack_source_sha256','lexical_source_sha256','ordinary_contract_source_sha256']:
        for p,h in req[key].items():
            need(sha(blob(SOURCE,req['std_sha'],p))==h,'source hash '+key+' '+p); sourcefiles[p]=h
    need(data['campaign-start.json']['request_data']==req and data['receipt.json']['request_sha256']==rh,'same-invocation embedded request')
    need(data['baseline.json']['control']=={'sha':HEAD,'tree':hm['tree'],'parent':hm['parents'][0],'dirty':''},'actual baseline control clean head/tree/parent')
    order=[row['id'] for row in req['rows']];need(order==go['selection']['ordered_rows'] and req['s3']['caps']==go['caps'],'frozen selection/order/caps')
    terminal=data['receipt.json']; need(type(terminal['schema']) is str and terminal['schema']=='ch8-s4p-2r2-campaign-v1' and type(terminal['s3_campaign']['selected_roots']) is int and terminal['s3_campaign']['selected_roots']==8,'exact terminal schema and genuine int8 before collection')
    roots=[];qual=[];cost=[];us=[];guards=[];gaps=[];epochs=[];properties={};serial=[];prior_end=None
    with tempfile.TemporaryDirectory(prefix='network-r2-intake-') as td:
        tmp=Path(td);reader=tmp/'reader';reader.mkdir(); frozen={}
        for n in git(CONTROL,'ls-tree','-r','--name-only',HEAD,'ch8-s1-control').decode().splitlines():
            rel=Path(n).relative_to('ch8-s1-control');b=blob(CONTROL,HEAD,n);p=reader/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);frozen[str(rel)]={'sha256':sha(b),'bytes':len(b)}
        sys.path.insert(0,str(reader));r=importlib.import_module('runner');c=importlib.import_module('s4p2r2_campaign');ev=importlib.import_module('s3_evidence');rich=importlib.import_module('rich_evidence');policy=importlib.import_module('s4p2r2_policy');public=importlib.import_module('collect')
        need(r.load_request()==req,'frozen actual request loader')
        static=policy.validate_source(SOURCE,req); need(static['status']=='STATIC_PASS','frozen source-only static gates')
        write('SOURCE-GATES.json',dict(static,scope='Exact frozen static source gates only; no compiler/native/full Validate'))
        local=tmp/'local';upload=tmp/'upload';local.mkdir();upload.mkdir()
        for n,b in members.items(): p=local/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
        (upload/'group-evidence.json.gz').write_bytes(gz)
        left=c.collect([local],req);right=public.collect([upload],req);need(left==right,'fresh local/upload-only collectors agree')
        seals=c.sealed(local);need(list(seals)==order,'all8 ordered sealed completions')
        prefixes=[]
        for count in range(9):
            lp=c.sealed(local,ids=order[:count]);up=c.sealed(upload,reader=public.read_bytes,ids=order[:count]);need(list(lp)==order[:count] and lp==up,'local/upload authenticated prefix '+str(count));prefixes.append({'count':count,'equal':True})
        need(terminal['state']=='SELECTED_PARTIAL' and terminal['stop_reason'] is None and not right['global_stop'] and not right['selected_missing_groups'],'all selected complete; no global stop; partial qualification')
        write('PREFIX.json',{'terminal':{k:v for k,v in terminal.items() if k!='rows'},'collector':right,'prefix0_to8':prefixes,'completion_is_not_qualification':True})
        for rank,row in enumerate(req['rows'],1):
            rid=row['id'];selector=row['selector'];gp='groups/s3-'+rid+'/'
            g=data[gp+'receipt.json'];co=data[gp+'compile/receipt.json'];can=data[rid+'/receipt.json'];sup=data['workers/'+rid+'-supervision.json'];life=data['workers/'+rid+'-lifecycle.json'];launch=data['workers/'+rid+'-launch.json'];stock=data[gp+'export.json'];pr=data[gp+'properties.json'];bm=data[gp+'binding-metadata.json'];ex=g['execution'];h,=stock['harnesses'];ph,=pr['harnesses'];ps=ph['properties'];binding=req['source_bindings'][rid]
            need(ev.provenance(g,co,req,rid,rh),rid+' provenance');prot=ev.protected(g,req,data['baseline.json'],sup,rh);need(not prot['observed_errors_ignored'],rid+' protected reader')
            need(c.snapshots.validate_pair(data['baseline.json'],life['pre'],life['post'],life['context']),rid+' controller epochs')
            need(g['argv']==r.build_argv(STD,Path('/home/runner/work/kani/kani/tool'),[selector],row['unwind'],Path('/home/runner/work/_temp/ch8-s1-receipts')/(gp+'export.json')) and g['selectors']==[selector] and g['unwind']==row['unwind'],rid+' exact singleton argv/selector/unwind')
            need(row['mode']=='Original' and row['target'] is None and g['effective_cfg']==req['flags']['RUSTFLAGS'] and g['native_start_verified'] and [x['selector'] for x in g['native_start_events']]==[selector],rid+' Original/null/cfg/native start')
            need(g['cargo_target_dir']==str(STD/'target/ch8-s1-cargo'/g['invocation_id']),rid+' fresh invocation namespace')
            need(all(bm[k]==v for k,v in {'invocation_id':g['invocation_id'],'request_sha256':rh,'std_sha':req['std_sha'],'tool_sha':req['tool_sha'],'argv':g['argv']}.items()),rid+' metadata identity')
            for a0 in bm['artifacts']: need(sha(members[gp+a0['path']])==a0['sha256'] and len(members[gp+a0['path']])==a0['bytes'],rid+' bound export '+a0['path'])
            stages={'E0':data['baseline.json']['binaries'],'pre':life['pre']['binaries'],'worker.BEFORE':g['tool_fingerprints_before'],'worker.AFTER':g['tool_fingerprints_after'],'controller.post':life['post']['binaries']}
            for label,snap in stages.items():need(r.fingerprints_match(data['baseline.json']['binaries'],snap),rid+' binary '+label)
            epochs.append({'id':rid,'context':life['context'],'stages':stages,'protected':prot,'lifecycle':life})
            need(ex['child_shutdown_verified'] and sup['worker_exit']==0 and sup['containment']['verified'] and not sup['cutoff'] and not sup['limit_initiated'] and sup['supervisor_error'] is None and not sup['orphan_survivors_at_worker_exit'],rid+' shutdown/containment/reap')
            need(launch['context']['rank']==rank and launch['context']['epoch']=='E'+str(rank) and launch['context']['root']==rid,rid+' serial launch context')
            start=g['native_start_events'][0]['monotonic'];end=sup['monotonic_end'];lt=launch['monotonic'];need(lt<=sup['monotonic_start']<=start<=end and (prior_end is None or prior_end<=lt),rid+' serial cleanup before next launch');serial.append({'id':rid,'launch':lt,'native_start':start,'cleanup_end':end,'previous_cleanup_end':prior_end});prior_end=end
            regs=[];providers=[]
            for m in bm['native_metadata']:
                if m.get('state')!='CAPTURED':continue
                b=decode(m);need(sha(b)==m['sha256'] and len(b)==m['bytes'],rid+' native metadata hash');md=json.loads(b)
                regs.extend(dict(x,metadata_path=m['path'],metadata_sha256=m['sha256']) for x in md.get('proof_harnesses',[]) if x['pretty_name']==selector);providers.extend(x for x in md.get('contracted_functions',[]) if selector in x.get('harnesses',[]))
            reg,=regs;need(reg['original_file']==str(STD/binding['file']) and reg['crate_name']=='core' and reg['attributes']['kind']=='Proof' and not providers,rid+' native registration/source/Original no provider')
            need(reg['attributes']['stubs']==([{'original':'s2_swap_seam','replacement':'weak_swap'}] if rid=='sort13_weak' else []) and not reg['attributes']['verified_stubs'],rid+' exact negative seam/no positive stubs')
            rebound=r.validate_export_value(stock,row,source_binding=binding,std=STD,group_selectors=[selector]);need(rebound['outcome']=='RECORDED' and rebound==can['export'],rid+' native source/stage/target rebound')
            need(stock['schema_version']=='0.1.0' and stock['kani_commit']==req['tool_sha'] and stock['kani_commit_dirty'] is False and stock['target']=='x86_64-unknown-linux-gnu',rid+' stock tool/target')
            need(stock['harness_selection']=={'requested_filters':[selector],'exact':True,'unmatched_filters':[],'matched_count':1} and stock['harness_timeout_s']==600,rid+' exact native selection/cap')
            need(pr['state']=='COMPLETE' and pr['error'] is None and pr['missing_sites']==[] and h['name']==ph['name']==selector,rid+' complete rich/native singleton')
            dec=rich.RegularEvidence([selector],STD);dec.finished=True;dec.closed={selector};dec.records={selector:copy.deepcopy(ps)};dec.validate(stock)
            bad=[p for p in ps if not located(p)];u=[p for p in ps if p['status']=='UNREACHABLE'];fail=[p for p in ps if p['status']=='FAILURE'];covers=[p for p in ps if p['class']=='cover'];gs=[p for p in ps if p['class']=='unsupported_construct'];unwinds=[p for p in ps if p['class']=='unwind']
            need(not bad,rid+' all exact property locations present and positive')
            need(len({p['id'] for p in ps})==len(ps)==h['n_properties']==h['checks']['total']+h['covers']['total'],rid+' unique complete native property counts')
            need(all(p['status'] in ('SUCCESS','FAILURE','UNREACHABLE','SATISFIED') for p in ps),rid+' no unknown/error status')
            targetfail=row['expected']=='DETECTED';need(len(fail)==(1 if targetfail else 0) and h['outcome']=={'kind':'COMPLETED','verdict':'FAILURE' if targetfail else 'SUCCESS'} and ex['original_exit_code']==(1 if targetfail else 0) and ex['signal'] is None and not ex['timed_out'],rid+' native verdict/original exit/intended failure cardinality')
            need(h['checks']['success']==sum(p['status']=='SUCCESS' for p in ps) and set(h['checks']['unreachable'])=={p['id'] for p in u} and set(h['checks']['failure'])=={p['id'] for p in fail},rid+' full native check partition')
            need(len(covers)==row['required_cover_count'] and {p['description'] for p in covers}==set(row['required_cover_messages']) and all(p['status']=='SATISFIED' for p in covers) and set(h['covers']['satisfied'])=={p['id'] for p in covers},rid+' exact required covers all SAT')
            need(all(not h['checks'][k] for k in ['unknown','error','undetermined','other']) and all(not h['covers'][k] for k in ['unknown','error','undetermined','other','unreachable','unsatisfiable']),rid+' no hidden unknown/error/UNSAT')
            need(len(gs)==len(h['unsupported_constructs']) and all(p['status']=='SUCCESS' for p in gs),rid+' successful guards retained')
            need(all(p['status']=='SUCCESS' for p in unwinds),rid+' all exported unwind properties SUCCESS')
            roles=[]
            for role in row['roles']:
                b=blob(SOURCE,req['std_sha'],role['file']);need(sha(b)==role['source_sha256'] and b.decode().splitlines()[role['line']-1]==role['source_line'],rid+' exact labelled source '+role['description'])
                matches=[p for p in ps if p['description']==role['description']];need(bool(matches) and all(p['class']==role['class'] and p['status']==role['status'] and p['file']==str(STD/role['file']) and p['line']==str(role['line']) for p in matches),rid+' exact native role '+role['description']);roles.append({'required':role,'native_matches':matches})
            strict=policy.expected_observation(row,rebound,ph);need(strict is False and can['s3_expected_match'] is False and seals[rid]['expected_match'] is False,rid+' original strict rejection reproduced')
            reasons=[]
            if gs:reasons.append('unsupported_constructs must be [] (first failing expected_observation gate); SUCCESS status does not satisfy this strict empty-array rule')
            if u:reasons.append('check statuses must be SUCCESS/FAILURE and checks.unreachable must be []; exact UNREACHABLE inventory violates ZERO_U/REJECT_ALL')
            for p in u:
                rel=p['file'].split('/export/',1)[1];n=int(p['line']);b=blob(SOURCE,req['std_sha'],rel);arg,premises=argument(rid,p)
                us.append({'root':rid,'selector':selector,'invocation_id':g['invocation_id'],'namespace':g['cargo_target_dir'],'property':p,'member':gp+'properties.json','member_sha256':sha(members[gp+'properties.json']),'source_sha':req['std_sha'],'source_file':rel,'source_sha256':sha(b),'source_line':n,'source_context':context(b,n),'effective_cfg':g['effective_cfg'],'domain':req['domains'].get(rid,'FIXED_NEGATIVE_FIXTURE'),'source_binding':binding,'native_registration':reg,'source_local_argument':arg,'premises':premises,'assessment':'S1_SOURCE_LOCAL_CANDIDATE' if arg else 'BLOCKER','origin_assurance':'Source-reported exact site; independent AST/MIR/emitter/caller provenance UNKNOWN','policy_status':'REJECT_ALL/proposal DISABLED; no admission'})
            for p in gs:
                rel=p['file'].split('/export/',1)[1];b=blob(SOURCE,req['std_sha'],rel)
                guards.append({'root':rid,'selector':selector,'invocation_id':g['invocation_id'],'property':p,'member':gp+'properties.json','member_sha256':sha(members[gp+'properties.json']),'source_sha':req['std_sha'],'source_file':rel,'source_sha256':sha(b),'source_context':context(b,int(p['line'])),'assessment':'SOURCE_REPORTED_SUCCESS_GUARD_RETAINED; strict empty-array gate rejects','argument':'This exact same-invocation unsupported guard is SUCCESS, not an executed unsupported operation accepted by waiver. Stock producer emits a false assertion plus assume for unsupported operations; success therefore reports no reachable violation in this bounded run. Keep original guard and all safety/unwind results. This does not establish generic support, allocation semantics or unwind behavior.','independent_guard_MIR_causality':'UNKNOWN','admitted':False})
            mp={n:{'member':gp+n,'bytes':len(members[gp+n]),'sha256':sha(members[gp+n])} for n in ['receipt.json','compile/receipt.json','binding-metadata.json','export.json','properties.json']}
            gaps.append({'root':rid,'invocation_id':g['invocation_id'],'state':pr['state'],'error':pr['error'],'missing_sites':pr['missing_sites'],'unlocated_records':bad,'actual_frozen_rich_reader':'ACCEPT','class_unreachable_SUCCESS_count':sum(p['class']=='unreachable' and p['status']=='SUCCESS' for p in ps),'all_properties_located':True,'new_location_exception':'NONE_REQUIRED','members':mp})
            qual.append({'id':rid,'rank':rank,'selector':selector,'mode':row['mode'],'target':row['target'],'scope_classification':row['scope_classification'],'domain':req['domains'].get(rid,'FIXED_NEGATIVE_FIXTURE'),'invocation_id':g['invocation_id'],'namespace':g['cargo_target_dir'],'native_verdict':h['outcome']['verdict'],'n_properties':h['n_properties'],'checks':h['checks'],'covers_summary':h['covers'],'status_counts':dict(collections.Counter(p['status'] for p in ps)),'class_status_counts':{cl:dict(collections.Counter(p['status'] for p in ps if p['class']==cl)) for cl in sorted({p['class'] for p in ps})},'roles':roles,'covers':covers,'failed_properties':fail,'unsupported_guards':gs,'native_unwinds':unwinds,'resolved_unwind':h['resolved_unwind'],'native_registration':reg,'providers':providers,'source_binding':binding,'strict_expected_match':False,'strict_rejection_reasons':reasons,'canonical':pick(can,['status','outcome','reason','s3_expected_match']),'members':mp,'assessment':'EXACT_NEGATIVE_LABEL_OBSERVED' if targetfail else 'BOUNDED_SOURCE_REPORTED_S1_CANDIDATE_PENDING_REVIEW_AND_COORDINATOR_DECISION','admission':False,'proof_credit':'NONE'})
            properties[rid]={'selector':selector,'invocation_id':g['invocation_id'],'member':mp['properties.json'],'state':pr['state'],'properties':ps}
            roots.append({'id':rid,'rank':rank,'selector':selector,'invocation_id':g['invocation_id'],'cargo_target_dir':g['cargo_target_dir'],'argv':g['argv'],'effective_cfg':g['effective_cfg'],'native_start_events':g['native_start_events'],'source_before':g['source_before'],'source_after':g['source_after'],'source_under_test':g['source_under_test'],'native_registration':reg,'binding_metadata':bm,'native_export_state':stock['run_state'],'canonical':pick(can,['status','outcome','reason','s3_expected_match'])})
            mem=g['memory'];ceff=min(go['caps']['local_rss_kib'],go['caps']['outer_rss_kib'],mem['available_kib']-go['caps']['headroom_kib'])
            need(ceff==mem['group_cap_kib']==6291456 and g['timeout_seconds']==g['group_budget_seconds']==600 and g['compile_limit_seconds']==180 and g['phase_limited'] is False,rid+' effective cap formula and frozen child/compile')
            need(co['state']=='COMPLETE' and co['elapsed_upper_bound_seconds']<180 and ex['elapsed_seconds']<600 and ex['rss_peak_kib']<ceff,rid+' completed below compile/wall/sampledRSS limits')
            cost.append({'id':rid,'compile':pick(co,['schema','boundary','scope','state','elapsed_upper_bound_seconds','limit_seconds','observed_run_state','marker_sha256','selectors']),'native_verification_time_s':h['resources']['verification_time_s'],'native_wall_time_s':stock.get('wall_time_s','UNKNOWN_NOT_EXPORTED'),'execution':pick(ex,['elapsed_seconds','original_exit_code','signal','timed_out','child_shutdown_verified','rss_peak_kib','rss_peak_gib','rss_scope','rss_sample_period_seconds','component_group_peak_kib','component_rss_scope','output_truncated','stdout_truncated','stderr_truncated']),'memory_admission':mem,'effective_cap_kib':ceff,'limits':g['r5_limits'],'supervision':pick(sup,['worker_exit','cutoff','elapsed_seconds','limit_initiated','outer_sampled_peak_kib','outer_rss_scope','worker_wall_limit_seconds','supervisor_error','orphan_survivors_at_worker_exit','lifecycle_events_omitted']),'containment':sup['containment'],'cutoff':'NONE_COMPLETED'})
        need(len({x['invocation_id'] for x in roots})==8,'all8 distinct fresh invocation namespaces')
    total=collections.Counter(p['status'] for root in properties.values() for p in root['properties'])
    need(dict(total)=={'SUCCESS':1051,'UNREACHABLE':67,'FAILURE':4,'SATISFIED':21},'complete1143 native partition')
    need(len(us)==67 and all(x['assessment']!='BLOCKER' for x in us),'all67 exact U instances have source-local candidate arguments')
    need(len(guards)==13 and all(x['property']['status']=='SUCCESS' for x in guards),'all13 successful unsupported guards retained')
    need([len(q['covers']) for q in qual]==[0,0,0,0,6,6,6,3],'all21 SAT covers including N0/N1')
    provenance={'source_tool_control_trigger':trees,'GO_commit':git(G0,'rev-parse','fef8170d86').decode().strip(),'GO_path':BASE+'ch8-s4/network-r2-go/GO-REQUEST.json','GO_sha256':sha(blob(G0,'fef8170d86',BASE+'ch8-s4/network-r2-go/GO-REQUEST.json')),'request_sha256':rh,'workflow_sha256':sha(wf),'artifact':a,'compact_payload':pick(integ,['payload_bytes','payload_sha256','uncompressed_bytes','uncompressed_sha256']),'frozen_reader_files':frozen,'source_files':sourcefiles,'binding_scope':'Exact stock registration/source/argv/cfg/export/namespace plus protected hashes; independent AST/MIR/emitter provenance UNKNOWN','checkout_depths':go['checkout_depths']}
    write('PROVENANCE.json',provenance);write('ROOTS.json',{'rows':roots,'request':req,'physical_inode_binding':'UNKNOWN_NOT_EXPORTED'})
    write('NATIVE-PROPERTIES.json',properties);write('QUALIFICATION.json',{'rows':qual,'status_partition':dict(total),'native_properties':sum(total.values()),'strict_expected_matches':0,'admission':False,'qualified_new_leaves':0,'independent_B1_B2_credit':'NONE'})
    write('U-ARGUMENTS.json',{'instances':us,'count':len(us),'producer_policy':req['unreachable_admission'],'policy':'S1-ACCEPTANCE-DECISION-2026-11-17; source-local candidate only, not admission','blockers':[x for x in us if x['assessment']=='BLOCKER'],'admitted':False})
    write('GUARD-ARGUMENTS.json',{'instances':guards,'count':len(guards),'admitted':False,'policy':'Retained SUCCESS guards; producer requires empty array and therefore rejects.'})
    write('METADATA-GAP.json',{'rows':gaps,'observed_missing_locations':0,'all8_complete_rich_readers_accept':True,'new_location_cases':[],'old_location_admissions_transferred':False,'class_unreachable_SUCCESS_is_not_status_UNREACHABLE':True,'compiler_MIR_origin':'UNKNOWN'})
    write('PROTECTED.json',{'baseline':data['baseline.json'],'epochs':epochs,'assurance':'Source-reported snapshots/identity hashes; independent compiler provenance UNKNOWN'})
    write('SERIAL-ORDER.json',{'rows':serial,'verified':True})
    write('COST.json',{'campaign_elapsed_seconds':terminal['phase_elapsed_seconds'],'caps':go['caps'],'setup':{k:v for k,v in data['setup/receipt.json'].items() if k!='rustc_diagnostics'},'job':pick(jobs[0],['id','started_at','completed_at']),'rows':cost,'compiler_metric':'Initial-export marker upper bound includes compilation/link and observation delay, not exclusive compile CPU','native_metric':'Stock resources.verification_time_s, not exclusive backend time','RSS_metric':'50ms sampled non-atomic owned PGID VmRSS; component peaks not simultaneous, not kernel/cgroup/full-tree peaks','internal_symex_solver_phases':'UNKNOWN_NOT_EXPORTED','accounting_changed':False})
    write('VALIDATION.json',{'status':'PASS','checks_count':len(CHECKS),'checks':CHECKS,'scope':'Frozen pure readers/static source gates/identity hashes/protected epochs/complete inventories/portable prefix; no native/compiler/CI/full Validate','evidence_modified':False,'admission':False})
    write('RESULT.json',{'status':'HANDOFF','run':44548842328,'attempt':1,'classification':'SELECTED_PARTIAL; 4_NATIVE_POSITIVE_SUCCESS; 4_INTENDED_NEGATIVE_FAILURE; STRICT0; NO_ADMISSION','campaign_elapsed_seconds':terminal['phase_elapsed_seconds'],'roots_started_and_sealed':8,'global_stop':False,'native_properties':1143,'status_partition':dict(total),'U_source_local_candidate_arguments':67,'location_blockers':0,'U_blockers':0,'successful_unsupported_guards':13,'provisional_positive_candidates_for_review':4,'qualified_new_leaves':0,'admission':False,'proof_credit':'NONE','proof_obligations_closed':0,'next':'Independent review of this exact intake/S1 candidates, then separate coordinator admission decision; no automatic CI/push/ledger action'})
    print(json.dumps({'status':'PASS','checks':len(CHECKS),'properties':1143,'U':67,'guards':13,'missing_locations':0,'strict_matches':0,'admission':False}))
if __name__=='__main__':main()
