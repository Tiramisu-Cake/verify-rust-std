#!/usr/bin/env python3
"""Authorized bounded offline intake. Reuses frozen readers; never runs native tools.
Adapted from run-44416629057/{replay.py,review-w14/review.py} contracts.
"""
import base64,collections,copy,csv,gzip,hashlib,importlib,json,re,subprocess,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
G0=HERE.parents[5]
TASK='e5a9d8f40c82408abf033466e0d50e94d77fad31'
BASE='8ea5bbbf8872fdb9a3f4b207b390e79dea3fcff5'
OLD='f74025e493a627962842e8f7bc6a2766d33dd300'
OLDREVIEW='a9fe0055aab3279e3f5bb71bde9667925da80e65'
CTRL='775574eb2f361ef90eade30330ff0d608530287f'
HEAD='474a9d1617d77f34566e6992debc604c70a9e9ea'
CONTROL=Path('/root/kani-ch8-s3-2-r1-control-w13')
SOURCE=Path('/root/verify-rust-std-ch8-s3-2-r1-w13')
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
def located(p):return isinstance(p.get('file'),str) and bool(p['file']) and isinstance(p.get('line'),str) and re.fullmatch('[1-9][0-9]*',p['line']) is not None
def decode(e):return e['text'].encode() if e.get('encoding','utf-8')=='utf-8' else base64.b64decode(e['text'],validate=True)
def context(b,line):
    ls=b.decode().splitlines();return '\n'.join(f'{i+1}: {ls[i]}' for i in range(max(0,line-5),min(len(ls),line+4)))
def uargument(rid,p):
    f=p['file'];n=int(p['line'])
    if f.endswith('/sorting_model.rs'):
        length={'checker_order_corrupt':2,'checker_count_corrupt':32,'sort13_weak':13}.get(rid)
        if length is None:return None,'UNKNOWN',[]
        args={100:('Order loop starts i=1 and increments only with i<L<=32, so i+1<=32.','i<L<=32 implies i+1<=32'),106:('Count outer loop uses i<L<=CAP32; before.values[i] is in bounds.','i<L<=CAP32'),111:('Count inner loop uses j<L<=CAP32, bounding before.values[j]; old_count starts0 and is at most j before at most one increment.','j<L<=32 and old_count<=j'),112:('Entry L=before.len=values.len; inner j<L bounds values[j]; new_count starts0 and is at most j before at most one increment.','j<values.len<=32 and new_count<=j'),113:('Inner loop increments only with j<L<=32, so j+1<=32.','j<L<=32 implies j+1<=32'),118:('Outer loop increments only with i<L<=32, so i+1<=32.','i<L<=32 implies i+1<=32')}
        if n not in args:return None,'UNKNOWN',[]
        return (*args[n],[f'Exact active_post entry before.valid, L=before.len=values.len={length}<=CAP32; slice capacity32.','Normal loop continuation only; early false return may make later checks unreachable, but cannot violate these bounds.','Fixed fixtures; sort13 is descending[12..0], with ordinary weak_swap seam, never arbitrary13bytes.'])
    if f.endswith('/fmt/mod.rs') and n==820:return ('The literal shift count1 is below x86_64 usize width64, independently of string length. No lost-bit claim.','1 < usize::BITS64',['Exact from_str expression s.len()<<1|1; target x86_64.'])
    if f.endswith('/num/uint_macros.rs') and n==3222:return ('The self<other branch evaluates other-self with other>=self.','self<other implies other-self defined',['Exact usize::abs_diff branch; all usize values.'])
    if f.endswith('/ptr/const_ptr.rs') and n==1479:return ('Normal continuation follows is_power_of_two(align); zero is not a power of two, hence align>=1 and align-1 is defined.','is_power_of_two(align) implies align>=1',['Exact is_aligned_to guard; separate panic/pointer checks retained.'])
    if f.endswith('/ub_checks.rs') and n==148:return ('The size==0 arm skips division; the else arm divides only by size!=0. Concrete u8 size=1 independently.','else(size==0) implies size!=0',['Exact is_valid_allocation_size conditional; allocation validity remains separate.'])
    if f.endswith('/smallsort.rs') and n in (974,990,991,992) and rid.startswith('m8_'):
        a={974:('Divisor is literal2, hence nonzero for every length.','2 != 0'),990:('Exact source slice has length8, half4; half-1=3 is defined.','len8 implies len/2-1=3'),991:('Exact source slice has length8, so right_rev len-1=7 is defined.','len8 implies len-1=7'),992:('Exact source slice has length8, so dst_rev len-1=7 is defined; writability and initialization remain separate.','len8 implies len-1=7')}
        return (*a[n],[f'Exact {rid} source-bounded singleton PFC bidirectional_merge::<u8,KeyLess<u8>>; source slice length8 before merge loop.','Geometry, initialized intervals, frame and caller binding are per-root records, not transferred from old case.','Source/native registration assurance only; independent MIR origin UNKNOWN.'])
    return None,'UNKNOWN',[]

def main():
    pins=json.loads(blob(G0,TASK,'research/challenge-8/kani-k1/kani3300/ch8-s3/postrun-s3-2-r1-terminal/INPUTS.json'))
    pins.update(task_g0=TASK,base_task_g0=BASE,settings='current high/FastOFF preserved; no subagents/model changes',execution_scope='BOUNDED_OFFLINE_INTAKE_ONLY')
    write('INPUTS.json',pins)
    run=json.loads((HERE/'github-run.json').read_bytes());jobs=json.loads((HERE/'github-job-collection.json').read_bytes())['jobs'];arts=json.loads((HERE/'github-artifacts.json').read_bytes())['artifacts']
    need((run['id'],run['run_attempt'],run['event'],run['head_sha'],run['head_branch'],run['path'],run['status'],run['conclusion'])==(44439462279,1,'push',HEAD,pins['branch'],pins['request']['workflow_path'],'completed','failure'),'connected exact terminal run identities')
    need(len(jobs)==1 and jobs[0]['head_sha']==HEAD and jobs[0]['run_attempt']==1 and jobs[0]['run_id']==pins['run'] and jobs[0]['conclusion']=='failure','connected exact native job/attempt')
    need(len(arts)==1 and all(arts[0][k]==pins['artifact'][p] for k,p in [('id','id'),('name','name'),('digest','digest'),('size_in_bytes','transport_bytes'),('expired','expired')]),'one exact artifact metadata')
    need(arts[0]['workflow_run']['head_sha']==HEAD and arts[0]['workflow_run']['id']==pins['run'],'artifact run/head binding')
    integ=json.loads((HERE/'artifact-integrity.json').read_bytes());gz=(HERE/'group-evidence.json.gz').read_bytes();raw=gzip.decompress(gz)
    need(sha(gz)==integ['payload_sha256'] and sha(raw)==integ['uncompressed_sha256'],'compact and uncompressed hashes')
    need(integ['bytes']==422238 and 'sha256:'+integ['sha256']==pins['artifact']['digest'] and integ['digest_checked_before_zip_open'] and not integ['transport_saved'],'digest first; no saved transport ZIP')
    packet=json.loads(raw);need(packet['state']=='PACKAGED' and packet['error'] is None and packet['schema']=='ch8-s1-05-artifact-v1','compact schema/state')
    data={};members={}
    for name,e in packet['files'].items():
        p=Path(name);need(not p.is_absolute() and '..' not in p.parts and '\\' not in name and p.suffix=='.json','structured-only member '+name)
        b=decode(e);need(len(b)==e['bytes'] and sha(b)==e['sha256'],'member hash/size '+name);members[name]=b;data[name]=json.loads(b)
    need(len(data)==119,'exact119 structured members')
    trees={}
    for kind,repo,rev in [('source',SOURCE,pins['source']['sha']),('tool',TOOL,pins['tool']['sha']),('control',CONTROL,CTRL),('trigger',CONTROL,HEAD)]:
        v={'sha':rev,'tree':git(repo,'rev-parse',rev+'^{tree}').decode().strip(),'sole_parent':git(repo,'show','-s','--format=%P',rev).decode().strip()};trees[kind]=v
        expected=pins['trigger'] if kind=='trigger' else pins['control_candidate' if kind=='control' else kind]
        need(v['tree']==expected['tree'] and v['sole_parent']==expected['sole_parent'],kind+' exact tree/sole parent')
    need(trees['control']['tree']==trees['trigger']['tree'],'executed/reviewed same tree')
    reqbytes=blob(CONTROL,HEAD,pins['request']['path']);req=json.loads(reqbytes);rh=sha(reqbytes)
    need(rh==pins['request']['sha256'] and reqbytes==blob(CONTROL,CTRL,pins['request']['path']),'executed exact request bytes')
    wf=blob(CONTROL,HEAD,pins['request']['workflow_path']);need(sha(wf)==pins['request']['workflow_sha256'] and wf==blob(CONTROL,CTRL,pins['request']['workflow_path']),'executed exact workflow bytes/depths7/5/2')
    for path,h in req['ci_payload_sha256'].items():need(sha(blob(CONTROL,HEAD,path))==h and blob(CONTROL,HEAD,path)==blob(CONTROL,CTRL,path),'executed pinned control payload '+path)
    sourcefiles={}
    for key in ['changed_file_sha256','cfg_pfc_source_sha256','contract_stack_source_sha256','lexical_source_sha256','ordinary_contract_source_sha256']:
        for path,h in req[key].items():
            b=blob(SOURCE,pins['source']['sha'],path);need(sha(b)==h,'source hash '+key+' '+path);sourcefiles[path]=h
    need(req['s3']['caps']==pins['caps'],'exact requested caps unchanged')
    baseline_control=data['baseline.json']['control']
    need(baseline_control=={'sha':HEAD,'tree':pins['trigger']['tree'],'parent':pins['trigger']['sole_parent'],'dirty':''},'native actual checkout control head/tree/parent/clean')
    need(data['campaign-start.json']['request_data']==req and data['receipt.json']['request_sha256']==rh,'embedded exact request')
    need([x['id'] for x in req['rows']]==[x['id'] for x in pins['ordered_rows']],'eight exact ordered roots')
    need(req['unreachable_admission']==pins['policy']['unreachable_admission'] and not req['unreachable_admission']['enabled'],'U REJECT_ALL proposalDISABLED unchanged')
    domains=json.loads(blob(G0,pins['candidate_g0'],'research/challenge-8/kani-k1/kani3300/ch8-s3/s3-2-r1/DOMAIN-UNWIND.json'))
    domain={x['id']:x for x in domains['roots']}
    deps={}
    for key,rev in [('task',TASK),('base_task',BASE),('candidate',pins['candidate_g0']),('review',pins['review_g0']),('GO',pins['GO_g0']),('old_exact_location',OLD),('old_review',OLDREVIEW),('prior_bounded_admission',pins['prior_S3_1_bounded_admission']['g0']),('method_plan',pins['method_plan']['g0'])]:
        deps[key]={'commit':rev,'tree':git(G0,'rev-parse',rev+'^{tree}').decode().strip()}
    frozen={};inventory=[];qual=[];us=[];cost=[];gaps=[];epochs=[];native={};allprops={};tests=[]
    with tempfile.TemporaryDirectory(prefix='s32-intake-') as td:
        tmp=Path(td);reader=tmp/'reader';reader.mkdir()
        for name in git(CONTROL,'ls-tree','-r','--name-only',CTRL,'ch8-s1-control').decode().splitlines():
            rel=Path(name).relative_to('ch8-s1-control');b=blob(CONTROL,CTRL,name);p=reader/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);frozen[str(rel)]={'sha256':sha(b),'bytes':len(b)}
        sys.path.insert(0,str(reader))
        r=importlib.import_module('runner');c=importlib.import_module('s32_campaign');ev=importlib.import_module('s3_evidence');rich=importlib.import_module('rich_evidence');policy=importlib.import_module('s32_policy');public=importlib.import_module('collect')
        need(r.load_request()==req,'frozen request loader exact8')
        static=policy.validate_source(SOURCE,req)
        write('SOURCE-GATES.json',{'status':static['status'],'canonical_sha256':sha(canon(static)),'reports':{k:pick(v,['status','schema','source_sha','source_tree','source_files_sha256','compilation','native_compile','proof_credit','qualification_from_registration','limits']) for k,v in static['reports'].items()},'scope':'Pinned source-only validators; no expansion/native compiler/full Validate','proof_credit':'NONE'})
        local=tmp/'materialized';upload=tmp/'upload';local.mkdir();upload.mkdir()
        for n,b in members.items():p=local/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
        (upload/'group-evidence.json.gz').write_bytes(gz)
        left=c.collect([local],req);right=public.collect([upload],req)
        need(left==right,'exact materialized vs upload-only public collector equality')
        seals=c.sealed(local);need(list(seals)==req['s3']['selected'],'all8 sealed ordered completion prefix')
        need(not right['global_stop'] and not right['selected_missing_groups'],'no globalstop/no missing selected group')
        need(data['receipt.json']['state']=='SELECTED_PARTIAL' and data['receipt.json']['stop_reason'] is None,'original SELECTED_PARTIAL no globalstop')
        prefix={'control':CTRL,'collector_state':right['state'],'global_stop':right['global_stop'],'global_stops':right['global_stops'],'selected_missing_groups':right['selected_missing_groups'],'completed_prefix':list(seals),'local_upload_equal':True,'all_required_seal_digests_verified':True,'collector':right,'completion_is_not_qualification':True}
        write('PREFIX-REPLAY.json',prefix)
        for rank,row in enumerate(req['rows'],1):
            rid=row['id'];selector=row['selector'];gp='groups/s3-'+rid+'/'
            g=data[gp+'receipt.json'];co=data[gp+'compile/receipt.json'];can=data[rid+'/receipt.json'];sup=data['workers/'+rid+'-supervision.json'];life=data['workers/'+rid+'-lifecycle.json'];launch=data['workers/'+rid+'-launch.json'];stock=data[gp+'export.json'];pr=data[gp+'properties.json'];bm=data[gp+'binding-metadata.json'];execution=g['execution'];hs=stock.get('harnesses',[]);h=hs[0] if hs else {};props=pr.get('harnesses',[{'properties':[]}])[0]['properties']
            need(ev.provenance(g,co,req,rid,rh),rid+' all-state source/compile provenance')
            prot=ev.protected(g,req,data['baseline.json'],sup,rh);need(not prot['observed_errors_ignored'],rid+' all-state protected reader')
            need(c.snapshots.validate_pair(data['baseline.json'],life['pre'],life['post'],life['context']),rid+' controller epoch source/control/binary identity')
            argv=r.build_argv(STD,Path('/home/runner/work/kani/kani/tool'),[selector],row['unwind'],Path('/home/runner/work/_temp/ch8-s1-receipts')/(gp+'export.json'))
            need(g['argv']==argv and g['selectors']==[selector] and g['unwind']==row['unwind'],rid+' exact singleton argv/selector/unwind')
            need(g['timeout_seconds']==g['group_budget_seconds']==600 and g['compile_limit_seconds']==180 and g['phase_limited'] is False and g['memory']['group_cap_kib']==6291456 and g['memory']['reserve_kib']==2097152 and launch['limits'] and launch['context']['root']==rid and launch['context']['rank']==rank and launch['context']['epoch']=='E'+str(rank),rid+' actual child/compile/RSS caps and controller root/rank/epoch')
            need(g['effective_cfg']==req['flags']['RUSTFLAGS'] and g['native_start_verified'] and [x['selector'] for x in g['native_start_events']]==[selector],rid+' exact cfg/native start')
            need(g['cargo_target_dir']==str(STD/'target/ch8-s1-cargo'/g['invocation_id']),rid+' fresh namespace')
            need(bm['invocation_id']==g['invocation_id'] and bm['request_sha256']==rh and bm['std_sha']==req['std_sha'] and bm['tool_sha']==req['tool_sha'] and bm['argv']==g['argv'],rid+' binding metadata invocation/request/source/tool/argv')
            for a in bm['artifacts']:need(sha(members[gp+a['path']])==a['sha256'] and len(members[gp+a['path']])==a['bytes'],rid+' artifact/member binding '+a['path'])
            stages={'E0':data['baseline.json']['binaries'],'pre':life['pre']['binaries'],'worker.BEFORE':g['tool_fingerprints_before'],'worker.AFTER':g['tool_fingerprints_after'],'post':life['post']['binaries']}
            for label,snap in stages.items():need(r.fingerprints_match(data['baseline.json']['binaries'],snap),rid+' protected canonical binary '+label)
            epochs.append({'id':rid,'context':life['context'],'stages':stages,'all_five_equal_E0':True,'protected':prot})
            need(execution['child_shutdown_verified'] and sup['worker_exit']==0 and sup['containment']['verified'] and not sup['cutoff'] and not sup['limit_initiated'] and sup['supervisor_error'] is None and not sup['orphan_survivors_at_worker_exit'],rid+' child shutdown/worker cleanup/serial continuation')
            rootsmeta=[];providers=[]
            for m in bm['native_metadata']:
                if m.get('state')!='CAPTURED':continue
                b=decode(m);need(len(b)==m['bytes'] and sha(b)==m['sha256'],rid+' native metadata digest '+m['path']);md=json.loads(b)
                rootsmeta += [dict(x,metadata_path=m['path'],metadata_sha256=m['sha256']) for x in md.get('proof_harnesses',[]) if x['pretty_name']==selector]
                providers += [x for x in md.get('contracted_functions',[]) if selector in x.get('harnesses',[])]
            need(len(rootsmeta)==1,rid+' unique native registration')
            registration=rootsmeta[0];binding=req['source_bindings'][rid];kind=registration['attributes']['kind']
            need(registration['original_file']==str(STD/binding['file']) and registration['crate_name']=='core',rid+' native source/crate registration')
            expected_stubs=[{'original':'s2_swap_seam','replacement':'weak_swap'}] if rid=='sort13_weak' else []
            need(registration['attributes']['stubs']==expected_stubs and registration['attributes']['verified_stubs']==[],rid+' exact native stubs/seam')
            need(kind==({'ProofForContract':{'target_fn':binding['target']}} if row['mode']=='PFC' else 'Proof'),rid+' exact Original/PFC target')
            if row['mode']=='PFC':need(len(providers)==1,rid+' unique contracted provider registration')
            need(stock['schema_version']=='0.1.0' and stock['kani_commit']==req['tool_sha'] and stock['kani_commit_dirty'] is False and stock['target']=='x86_64-unknown-linux-gnu',rid+' native schema/tool/target')
            need(stock['harness_selection']=={'requested_filters':[selector],'exact':True,'unmatched_filters':[],'matched_count':1} and stock['harness_timeout_s']==600,rid+' native exact selection/cap')
            literal=[]
            for role in row['roles']:
                b=blob(SOURCE,req['std_sha'],role['file']);need(sha(b)==role['source_sha256'] and b.decode().splitlines()[role['line']-1]==role['source_line'],rid+' role source hash/line '+role['description'])
                matches=[p for p in props if p['description']==role['description']]
                ok=len(matches)==1 and all(p['class']==role['class'] and p['status']==role['status'] and p['file']==str(STD/role['file']) and p['line']==str(role['line']) for p in matches)
                if hs:need(ok,rid+' literal role native source/status '+role['description'])
                else:need(not matches,rid+' no fabricated native role '+role['description'])
                literal.append({'required':role,'native_matches':matches,'exact_match':ok,'state':'OBSERVED_EXACT' if ok else 'UNKNOWN_NO_COMPLETED_INVENTORY'})
            bad=[p for p in props if not located(p)];fail=[p for p in props if p['status']=='FAILURE'];u=[p for p in props if p['status']=='UNREACHABLE'];covers=[p for p in props if p['class']=='cover'];guards=[p for p in props if p['class']=='unsupported_construct'];rebound=None;pfc=None;reader_result=None
            if hs:
                need(len(hs)==1 and h['name']==selector,rid+' completed singleton export')
                rebound=r.validate_export_value(stock,row,source_binding=binding,std=STD,group_selectors=[selector]);need(rebound['outcome']=='RECORDED',rid+' frozen native source-stage-target reader')
                dec=rich.RegularEvidence([selector],STD);dec.finished=True;dec.closed={selector};dec.records={selector:copy.deepcopy(props)}
                try:dec.validate(stock);reader_result='ACCEPT'
                except ValueError as exc:reader_result=str(exc)
                need(reader_result==('rich metadata incomplete: file/line missing' if rid.startswith('m8_') else 'ACCEPT'),rid+' exact actual rich metadata verdict')
                need(h['n_properties']==len(props)==h['checks']['total']+h['covers']['total'],rid+' full observed count partitions')
                need(len(fail)==(1 if row['expected']=='DETECTED' else 0) and h['outcome']=={'kind':'COMPLETED','verdict':'FAILURE' if fail else 'SUCCESS'},rid+' exact native verdict/failure count')
                need(len(covers)==row['required_cover_count'] and set(p['description'] for p in covers)==set(row['required_cover_messages']) and all(p['status']=='SATISFIED' for p in covers),rid+' exact SAT covers/no extras')
                need(all(p['status'] in ('SUCCESS','FAILURE','UNREACHABLE','SATISFIED') for p in props),rid+' no unassessed error/unknown/undetermined status')
                need(len(guards)==len(h['unsupported_constructs']) and all(p['status']=='SUCCESS' and located(p) for p in guards),rid+' ALL unsupported guards explicitly retained SUCCESS')
                if rid.startswith('m8_'):
                    need(len(bad)==1 and bad[0]['class']=='unreachable' and bad[0]['status']=='SUCCESS' and len(guards)==4 and len(u)==8,rid+' exact one locationless systemSUCCESS/eight U/four guards')
                    a=bad[0];parser=rich.RegularEvidence([selector],STD)
                    stream=('Checking harness '+selector+'...\nRESULTS:\nCheck 1: '+a['display_id']+'\n\t - Status: '+a['status']+'\n\t - Description: "'+a['description']+'"\n\t - Location: '+a['location_display']+'\nSUMMARY:\n').encode()
                    parser.feed(stream);parser.finish();need(parser.error is None and parser.records=={selector:bad} and len(parser.missing_sites)==1,rid+' authentic-field streaming parser zero sentinel/nulls')
                    need(not rich.location_exception(selector,a),rid+' old runtime location map excludes new case')
                    gaps.append({'root':rid,'selector':selector,'invocation_id':g['invocation_id'],'namespace':g['cargo_target_dir'],'member':gp+'properties.json','member_sha256':sha(members[gp+'properties.json']),'export_member':gp+'export.json','export_sha256':sha(members[gp+'export.json']),'all_missing_null_wrong_type_location_records':bad,'count':len(bad),'missing_key_count':sum('file' not in p or 'line' not in p for p in props),'present_null_count':sum(p.get('file') is None or p.get('line') is None for p in props),'non_null_wrong_type_count':sum((p.get('file') is not None and not isinstance(p['file'],str)) or (p.get('line') is not None and not isinstance(p['line'],str)) for p in props),'invalid_positive_coordinate_count':len(bad),'raw_display_fields':bad,'stock_counts':pick(h,['n_properties','n_failed','checks','covers']),'literal_roles':literal,'all_roles_covers_U_guards_located':all(located(p) for p in props if p not in bad),'actual_reader':reader_result,'actual_producer':can,'original_exception':g.get('original_exception'),'stream_reconstruction':'PASS; ordinal1 isolated authentic fields, not original stream ordinal','positive_source_or_MIR_origin':'UNKNOWN','location_rule':'NOT_APPLIED'})
                else:need(not bad,rid+' all native properties located')
                if row['mode']=='PFC':
                    symbol=registration['contract']['contracted_function_name'];decoded=subprocess.check_output(['c++filt','-i','-s','rust',symbol],text=True).strip()
                    need(decoded.startswith('core::slice::sort::shared::smallsort::'+binding['target']+'::<u8, core::slice::sort::shared::smallsort::verify::sorting_model::KeyLess<u8>>::'),rid+' concrete PFC symbol')
                    links=[p for p in props if p['id'].startswith(decoded+'.')]
                    need(all(any(p['class']==cl and p['status']=='SUCCESS' and symbol in p['description'] for p in links) for cl in ('single_top_level_call','no_recursive_call')),rid+' exact DFCC actual-body symbol links')
                    base='slice::sort::shared::smallsort::'+binding['target']+'::<u8, slice::sort::shared::smallsort::verify::sorting_model::KeyLess<u8>>'
                    ensures=[p for p in props if p['id'].startswith(base+'::') and p['class']=='assertion' and p['description'].startswith('|_|')]
                    need(len(ensures)==1 and ensures[0]['status']=='SUCCESS' and located(ensures[0]),rid+' located source-reported checked ensures')
                    pfc={'raw_symbol':symbol,'demangled_symbol':decoded,'DFCC_links':links,'ensures':ensures,'assurance':'SOURCE_REPORTED stock PFC actual body/contract stack; no independent MIR binding'}
            else:
                need(stock['run_state']=='INCOMPLETE' and 'harnesses' not in stock and not props and pr['state']=='INCOMPLETE' and execution.get('termination_reason')=='rss_cap',rid+' actual partial export/no result, RSS cutoff')
            strict=policy.expected_observation(row,rebound or {},{'name':selector,'properties':props});need(strict is False and can.get('s3_expected_match') is False,rid+' immutable strict unqualified')
            urec=[]
            for p in u:
                rel=p['file'].split('/export/',1)[1];line=int(p['line']);b=blob(SOURCE,req['std_sha'],rel);arg,predicate,premises=uargument(rid,p)
                entry={'root':rid,'selector':selector,'invocation_id':g['invocation_id'],'namespace':g['cargo_target_dir'],'property':p,'member':gp+'properties.json','member_sha256':sha(members[gp+'properties.json']),'source_sha':req['std_sha'],'source_file':rel,'source_sha256':sha(b),'source_line':line,'source_context':context(b,line),'effective_cfg':g['effective_cfg'],'provider_target':binding['target'],'domain':domain[rid],'source_binding':binding,'native_registration':registration,'type_comparator':'u8, full byte KeyLess<u8>','predicate':predicate,'premises':premises,'source_local_argument':arg,'assessment':'SOURCE_LOCAL_DEFINEDNESS_ARGUMENT' if arg else 'UNKNOWN','origin_assurance':'SOURCE_REPORTED site/context; independent AST/MIR/property/caller edges UNKNOWN','policy_status':'REJECT_ALL; proposal DISABLED; no admission'}
                urec.append(entry);us.append(entry)
            scope=row['scope_classification'];need(scope==domain[rid]['scope_classification'],rid+' exact source domain/scope classification')
            assessment=('PROVISIONAL_S1_FIXED_NEGATIVE_LABEL_DETECTED' if row['expected']=='DETECTED' else 'NO_COMPLETED_NATIVE_RESULT' if not hs else 'DIAG_INIT_OPEN' if 'partial_diag' in rid else 'PROVISIONAL_S1_BOUNDED_PFC_PENDING_LOCATION_DECISION')
            q={'id':rid,'rank':rank,'selector':selector,'mode':row['mode'],'unwind':row['unwind'],'scope_classification':scope,'domain':domain[rid],'native_verdict':h.get('outcome',{}).get('verdict','UNKNOWN_INCOMPLETE_EXPORT'),'native_property_count':h.get('n_properties','UNKNOWN_NO_COMPLETED_NATIVE_INVENTORY'),'status_counts':dict(collections.Counter(p['status'] for p in props)) if hs else 'UNKNOWN','class_status_counts':{cl:dict(collections.Counter(p['status'] for p in props if p['class']==cl)) for cl in sorted({p['class'] for p in props})},'literal_roles':literal,'covers':covers,'unsupported_guards':guards,'native_unsupported_constructs':h.get('unsupported_constructs','UNKNOWN_NO_COMPLETED_NATIVE_INVENTORY'),'failed_properties':fail,'U_count':len(u) if hs else 'UNKNOWN_NO_COMPLETED_NATIVE_INVENTORY','U_properties':u,'missing_location':bad,'actual_rich_reader':reader_result or 'NO_COMPLETED_NATIVE_INVENTORY','native_registration':rootsmeta,'contracted_provider_registration':providers,'PFC':pfc,'binding':{'source_binding':binding,'native_metadata_state':bm['native_metadata_state'],'compiler_identity_status':bm['compiler_identity_status'],'gaps':bm['rows'],'effective_cfg':g['effective_cfg'],'flags':req['flags'],'type':'u8','comparator':'KeyLess<u8>, full0..255 with source order premises','init_assurance':'Source-written known values and typed output reads only; actual mask/dstinit not proved, initialization hook disabled/constanttrue; no ghost mask/spec read of uninitialized backing.','caller_assurance':'Exact harness/backing/offset/initialization/normal-return frame only; no generic caller lifting.'},'producer':pick(can,['status','outcome','reason','s3_expected_match']),'strict_expected_match':strict,'provisional_assessment':assessment,'qualification_admitted':False,'eligible_as_init_leaf_or_provider_summary':False,'proof_credit':'NONE','native_members':{k:{'member':gp+k,'sha256':sha(members[gp+k])} for k in ('receipt.json','compile/receipt.json','binding-metadata.json','export.json','properties.json')}}
            qual.append(q);native[rid]={'export':stock,'rich':pick(pr,['schema','state','error','missing_sites','location_exceptions','observed_stdout_bytes'])};allprops[rid]={'harness':selector,'state':pr['state'],'properties':props,'absent_inventory':'UNKNOWN_NOT_ZERO' if not hs else None,'member':gp+'properties.json','sha256':sha(members[gp+'properties.json'])}
            inventory.append({'id':rid,'rank':rank,'selector':selector,'mode':row['mode'],'unwind':row['unwind'],'native_verdict':q['native_verdict'],'canonical_status':can['status'],'canonical_outcome':can['outcome'],'canonical_reason':can.get('reason'),'group_state':g['state'],'original_exception':g.get('original_exception'),'original_exit':execution['original_exit_code'],'signal':execution['signal'],'worker_exit':sup['worker_exit'],'sealed':True,'argv':g['argv'],'effective_cfg':g['effective_cfg'],'invocation_id':g['invocation_id'],'cargo_target_dir':g['cargo_target_dir'],'native_start_events':g['native_start_events'],'source_before':g['source_before'],'source_after':g['source_after'],'source_under_test':g['source_under_test'],'protected':prot,'export':gp+'export.json','export_sha256':sha(members[gp+'export.json']),'native_export_state':stock['run_state'],'launch':launch})
            isrss=execution.get('termination_reason')=='rss_cap'
            cost.append({'id':rid,'compile_elapsed_upper_bound_seconds':co['elapsed_upper_bound_seconds'],'compile_scope':co['scope'],'compile_boundary':co['boundary'],'compile_state':co['state'],'native_verification_time_s':h.get('resources',{}).get('verification_time_s','UNKNOWN_CENSORED_NO_COMPLETED_EXPORT'),'native_wall_time_s':stock.get('wall_time_s','UNKNOWN_INCOMPLETE_EXPORT'),'execution':pick(execution,['elapsed_seconds','original_exit_code','signal','timed_out','termination_reason','child_shutdown_verified','rss_peak_kib','rss_scope','rss_sample_period_seconds','component_group_peak_kib','component_rss_scope','cleanup_errors','process_identity']),'worker_supervision':pick(sup,['worker_exit','cutoff','elapsed_seconds','limit_initiated','outer_sampled_peak_kib','outer_rss_scope','supervisor_error','orphan_survivors_at_worker_exit','worker_wall_limit_seconds','lifecycle_errors','lifecycle_events_omitted']),'containment':pick(sup['containment'],['verified','scope','elapsed_seconds','signals','reaped_adopted','worker_exit']),'supervisor_lifecycle_diagnostics':{'retained_count':len(sup['lifecycle_events']),'omitted_count':sup['lifecycle_events_omitted'],'classification_counts':dict(collections.Counter(x.get('classification',x.get('operation','UNKNOWN')) for x in sup['lifecycle_events'])),'retained_projection':[pick(x,['classification','operation','errno','message','monotonic','pid','start_ticks']) for x in sup['lifecycle_events']],'scope':'Bounded race/ownership diagnostic retention; compact retains full records; final containment independently verified.'},'censoring':'TERMINATED_UNFINISHED_RSS' if isrss else 'NONE_NATIVE_COMPLETED','trigger':{'cause':'LOCAL_SAMPLED_PGID_RSS_FIRST_OVER_CAP' if isrss else 'NONE','sample_kib':execution['rss_peak_kib'] if isrss else None,'cap_kib':6291456,'sample_inference':'runner updates max then breaks on first RSS>cap; every earlier group sample<=cap, so recorded max is trigger sample' if isrss else None,'phase':'AFTER_STOCK_INITIAL_EXPORT; precise symex/backend subphase UNKNOWN' if isrss else 'COMPLETED; no phase peak timestamps','rss_at_signal_or_kernel_peak':'UNKNOWN','compile180_child600_slot720_global':'LOCAL_RSS, NOT_TIME_CAP; all wall limits unhit, no global stop' if isrss else 'NO_CAP_HIT'},'residual_child_budget_after_compile_marker_s':600-co['elapsed_upper_bound_seconds'],'not_backend_duration':True,'symex_backend_steps_VCC':'UNKNOWN_NOT_EXPORTED','next_root':req['rows'][rank]['id'] if rank<len(req['rows']) else None})
        need(len({x['invocation_id'] for x in inventory})==8,'eight distinct fresh singleton namespaces')
        need(len(us)==41 and all(x['source_local_argument'] for x in us),'all41 U invocation/site arguments separately assessed')
        need(sum(len(x['unsupported_guards']) for x in qual)==12,'all12 SUCCESS unsupported guards retained, none waived')
        need(sum(x['native_verdict']=='SUCCESS' for x in qual)==3 and sum(x['native_verdict']=='FAILURE' for x in qual)==3,'three native positive successes/three exact negative failures/two censored')
        # Actual portable-seal adverse tests; restore bytes after every bounded mutation.
        victim='groups/s3-m8_s32_d00_allinit/export.json';path=local/victim;original=path.read_bytes()
        path.unlink()
        try:c.sealed(local)
        except (c.GlobalFailure,ValueError,OSError):tests.append({'test':'missing_required_member','result':'REJECT'})
        else:raise AssertionError('missing required seal member accepted')
        path.write_bytes(original+b' ')
        try:c.sealed(local)
        except (c.GlobalFailure,ValueError,OSError):tests.append({'test':'tampered_required_member','result':'REJECT'})
        else:raise AssertionError('tampered seal member accepted')
        path.write_bytes(original)
        badg=copy.deepcopy(data['groups/s3-m8_s32_d00_allinit/receipt.json']);badg['tool_fingerprints_after']['binaries']['kani_driver']['sha256']='0'*64
        try:ev.protected(badg,req,data['baseline.json'],data['workers/m8_s32_d00_allinit-supervision.json'],rh)
        except ev.EvidenceError:tests.append({'test':'changed_protected_binary','result':'REJECT'})
        else:raise AssertionError('changed binary accepted')
        location_proposal(pins,req,data,members,qual,gaps,rich,ev,tests)
        need(all((local/n).read_bytes()==b for n,b in members.items()),'all authentic structured evidence unchanged after bounded adverse tests')
    write('INVENTORY.json',{'selected':inventory,'deferred':req['s3']['deferred'],'deferred_state':'NOT_SELECTED_NO_PROMOTION','full_obligations':pins['policy']['open_obligations_path'],'request':req,'source_files':sourcefiles,'baseline':data['baseline.json'],'epoch_comparisons':epochs,'physical_inode_realpath_identity':'UNKNOWN_NOT_EXPORTED; canonical path/hash equality only'})
    write('NATIVE.json',native);write('NATIVE-PROPERTIES.json',allprops)
    write('QUALIFICATION.json',{'schema':'s32-provisional-qualification-v1','assurance':'S1 Profiles v4 SOURCE_REPORTED; independent B1/B2 NONE','strict_policy':req['unreachable_admission'],'producer_expected_matches':0,'rows':qual,'U_instances':us,'U_count':len(us),'decisions':'3 fixed negative label observations;1 bounded allinit candidate PENDING_LOCATION_DECISION;2 DIAG_INIT_OPEN;2 insertion results censored. No admission.','qualified_new_leaves':0,'qualified_partial_provider_contexts':0,'sort8_init_caller_contexts_open':34,'proof_obligations_closed':0,'independent_credit':'NONE'})
    oldcost=json.loads(blob(G0,OLD,'research/challenge-8/kani-k1/kani3300/ch8-s3/run-44416629057/COST.json'))
    write('COST.json',{'campaign_elapsed_seconds':data['receipt.json']['phase_elapsed_seconds'],'caps':pins['caps'],'setup':pick(data['setup/receipt.json'],['setup_total_seconds','elapsed_seconds','rss_peak_kib','rss_status','rss_sample_period_seconds','component_group_peak_kib','component_rss_scope','original_exit_code','child_shutdown_verified']),'job_steps':jobs[0]['steps'],'job_started_at':jobs[0]['started_at'],'job_completed_at':jobs[0]['completed_at'],'rows':cost,'compiler_metric':'Upper bound to initial stock export includes std_project compilation/link/observer delay; not CPU/exclusive compilation.','native_verification_metric':'Native resources.verification_time_s scope as exported by tool; not a measured exclusive backend phase.','symex_backend_steps_VCC':'UNKNOWN_NOT_EXPORTED','rss_metric':'50ms nominal polled non-atomic owned PGID VmRSS; possible overshoot, not kernel/cgroup/tree peak. Component maxima not simultaneous.','old_cutoff_reference':{'commit':OLD,'rows':[x for x in oldcost['rows'] if x['id'] in ('s3_insert_tail_u8_rel16','s3_merge8_u8_same_alloc')],'comparison':'CHANGED_GEOMETRY_NOT_MATCHED; old insertion begin1..16/tail1..16 vs new fixedtail1 or16; old merge symbolic src/dst vs new fixed. No speedup, no full-domain fit600 theorem.'}})
    tracepaths=['kani-compiler/src/codegen_cprover_gotoc/codegen/span.rs','kani-compiler/src/codegen_cprover_gotoc/codegen/statement.rs','kani-compiler/src/codegen_cprover_gotoc/codegen/assert.rs','kani-compiler/src/codegen_cprover_gotoc/codegen/span.rs','kani-driver/src/cbmc_output_parser.rs','kani-driver/src/cbmc_property_renderer.rs','kani-driver/src/frontend/schema_utils.rs']
    write('PROVENANCE.json',{'task':TASK,'base_task':BASE,'source_tool_control_trigger':trees,'dependencies':deps,'checkout_depths':pins['checkout_depths'],'request_sha256':rh,'workflow_sha256':sha(wf),'artifact':pins['artifact'],'payload_sha256':sha(gz),'compact_uncompressed_sha256':sha(raw),'frozen_reader_source_files':frozen,'tool_source_trace_sha256':{p:sha(blob(TOOL,req['tool_sha'],p)) for p in tracepaths},'base_helpers':['run-44416629057/acquire.py','run-44416629057/replay.py','run-44416629057-review-w14/review.py','exact executed s32_campaign/collect/s32_policy/s3_evidence/rich_evidence Python readers'],'restrictions':'No source/control/policy/ledger/accounting/CI/native tool edits or execution; no subagents/model changes; no push/raw logs/GCS/full archives.'})
    write('VALIDATION.json',{'status':'PASS','checks':CHECKS,'checks_count':len(CHECKS),'adverse_tests':tests,'scope':'Offline bounded source/integrity/frozen-reader/proposal tests only; no full Validate/native execution','proposal_runtime_applied':False,'evidence_modified':False})
    with (HERE/'ROOTS.csv').open('w',newline='') as f:
        fields=['id','rank','mode','unwind','native_verdict','canonical_status','canonical_outcome','group_state','original_exit','signal','worker_exit','sealed'];w=csv.DictWriter(f,fields,lineterminator='\n');w.writeheader();w.writerows({k:x[k] for k in fields} for x in inventory)
    write('RESULT.json',{'schema':'s32-r1-terminal-intake-v1','status':'READY','task':TASK,'run':pins['run'],'native_run':'completed/failure','campaign':'SELECTED_PARTIAL','campaign_elapsed_seconds':data['receipt.json']['phase_elapsed_seconds'],'global_stop':False,'completed_sealed_prefix':8,'native_success':3,'intended_native_negative_failures':3,'censored_insertions':2,'strict_expected_matches':0,'provisional_S1_fixed_negative_observations':3,'provisional_S1_bounded_candidate_pending_location':1,'DIAG_INIT_OPEN':2,'missing_location_records':3,'all_U_occurrences_assessed':len(us),'SUCCESS_unsupported_guards_retained':12,'location_proposal':'NOT_APPLIED_EXACT_ENUMERATED_ONLY; shared actual emitter identity UNKNOWN','qualified_new_leaves':0,'qualified_init_provider_contexts':0,'proof_obligations_closed':0,'proof_credit':'NONE','independent_review':'W14 FOLLOWS ONLY AFTER SEALED_COMMIT; not performed here','policy_or_accounting_changed':False,'remaining_unknown':['Actual positive source/MIR origin and shared emitter identity of the3 zero-location system records','Independent AST/MIR/property/caller edges not exported','Exact backend/symex/steps/VCC, RSS at signal/kernel/tree peak, censored verification durations','Initialization mask/dstinit/provider summaries and34 sort8 contexts; generic caller/fullN16N32 proof'],'handoff':'Root verifies exact fullg0/manifests/completeness/replay/cost, then separately issued independent14. No automatic stage/admission.'})
    print(json.dumps({'status':'PASS','checks':len(CHECKS),'roots':8,'U':len(us),'guards':12,'missing_locations':3,'negative_tests':len(tests)}))


def location_proposal(pins,req,data,members,qual,gaps,rich,ev,tests):
    old=json.loads(blob(G0,OLD,'research/challenge-8/kani-k1/kani3300/ch8-s3/admission-r2-location/ADMISSION.json'))
    oldreview=json.loads(blob(G0,OLDREVIEW,'research/challenge-8/kani-k1/kani3300/ch8-s3/run-44416629057-review-w14/LOCATION-DECISION.json'))
    need(old['exact_property']==oldreview['exact_property'] and old['run']==oldreview['run']==44416629057,'old exact coordinator admission/review agree on authentic property')
    oldreader='cb63033ffcde918f4341146e56373476b8eeb569'
    parserpath='ch8-s1-control/rich_evidence.py'
    need(blob(CONTROL,oldreader,parserpath)==blob(CONTROL,CTRL,parserpath),'old/new frozen rich parser bytes identical')
    comparisons=[]
    for g in gaps:
        p=g['all_missing_null_wrong_type_location_records'][0];oldp=old['exact_property']
        comparisons.append({'root':g['root'],'same_tool':pins['tool']['sha']==oldreview['protected_identity']['tool']['sha'],'same_parser_bytes':True,'same_schema':'0.1.0/ch8-s1-05-rich-v1','same_class_status_description_null_keys':all(p[k]==oldp[k] for k in ('class','status','description','file','line')),'same_display_shape':'library/core/src/lib.rs:0:0 in function EXACT_HARNESS','same_native_id':p['id']==oldp['id'],'same_root':g['selector']==old['harness'],'same_source':pins['source']['sha']==oldreview['protected_identity']['source']['sha'],'same_control':CTRL==oldreview['protected_identity']['control']['sha'],'same_invocation':g['invocation_id']==oldreview['protected_identity']['invocation_id'],'same_request':pins['request']['sha256']==oldreview['protected_identity']['request_sha256'],'old_counts':oldreview['counts'],'new_counts':g['stock_counts'],'independent_U_source_local_arguments':8,'all_literal_roles_covers_U_located':g['all_roles_covers_U_guards_located'],'actual_shared_emitter_identity':'UNKNOWN_NOT_BOUND_BY_COMPACT','actual_lowering_cause':'UNKNOWN','new_case_uses_old_exception':False})
    trace=[{'file':'kani-compiler/src/codegen_cprover_gotoc/codegen/statement.rs','lines':'468-469,512-516','claim':'A supported stock source route: MIR TerminatorKind::Unreachable calls codegen_assert_assume_false(PropertyClass::Unreachable, unreachable code, loc); loc comes from term.source_info.span. No retained MIR binds these actual records to this route.'},
           {'file':'kani-compiler/src/codegen_cprover_gotoc/codegen/assert.rs','lines':'214-221','claim':'Helper emits assert-assume(false) with supplied property class/message/location.'},
           {'file':'kani-compiler/src/codegen_cprover_gotoc/codegen/span.rs','lines':'40-65,92-109','claim':'Span conversion takes stable filename/start_line/start_col and current function; cache adjusts current function/pragmas. Which concrete span/route produced actual0:0 is UNKNOWN.'},
           {'file':'kani-driver/src/cbmc_output_parser.rs','lines':'261-310','claim':'SourceLocation optional fields preserve strings; Display prints file, supplied line/column, and demangled function. This explains display formatting, not original positive source origin.'},
           {'file':'kani-driver/src/cbmc_property_renderer.rs','lines':'274-347','claim':'format_result prints Check/status/description and nonmissing display location under show_checks.'},
           {'file':'kani-driver/src/frontend/schema_utils.rs','lines':'485-510,516-550,750-790','claim':'Successful system check is only counted in checks.success; success ID/location not retained individually in stock JSON. Unsupported guards exported at every status. Rich streaming record supplies actual SUCCESS ID/display, checked against same invocation counts/partitions.'}]
    for t in trace:t.update(tool=pins['tool']['sha'],sha256=sha(blob(TOOL,pins['tool']['sha'],t['file'])))
    write('METADATA-GAP.json',{'schema':'s32-exact-location-comparison-v1','rows':gaps,'total_bad_location_records':sum(g['count'] for g in gaps),'old_admission':{'commit':OLD,'document_sha256':sha(blob(G0,OLD,'research/challenge-8/kani-k1/kani3300/ch8-s3/admission-r2-location/ADMISSION.json')),'case':old},'old_review':{'commit':OLDREVIEW,'document_sha256':sha(blob(G0,OLDREVIEW,'research/challenge-8/kani-k1/kani3300/ch8-s3/run-44416629057-review-w14/LOCATION-DECISION.json')),'case':oldreview},'comparisons':comparisons,'normalization':'Authentic field streaming reconstruction with frozen RegularEvidence._record: positive decimal line regex rejects0, preserving raw display and setting both normalized file/line present-null. validate rejects only at final positive-location gate, after counts/status/guard partitions. No coordinate invented.','tool_source_trace':trace,'reader_source':{'commit':CTRL,'path':parserpath,'sha256':sha(blob(CONTROL,CTRL,parserpath)),'record_lines':'148-173','validate_lines':'177-217'},'actual_shared_emitter_identity':'UNKNOWN; same text/class/suffix/display and parser bytes do not prove same emitter or cause.','originating_positive_source_or_MIR_coordinate':'UNKNOWN','classification':'class unreachable + statusSUCCESS system check; distinct from statusUNREACHABLE U. Retain intact, not role/cover/panic failure.','old_exception_transferred':False,'recommendation':'NOT_APPLIED exact enumerated3 cases; general rule PENDING independent emitter evidence.'})
    candidates=[];outtests=[]
    for gap in gaps:
        rid=gap['root'];gp='groups/s3-'+rid+'/';selector=gap['selector'];exact=gap['all_missing_null_wrong_type_location_records'][0];q=next(x for x in qual if x['id']==rid)
        original={'selector':selector,'stock':data[gp+'export.json'],'rich':data[gp+'properties.json'],'group':data[gp+'receipt.json'],'binding':data[gp+'binding-metadata.json'],'compile':data[gp+'compile/receipt.json'],'supervision':data['workers/'+rid+'-supervision.json'],'properties_member':gp+'properties.json','export_member':gp+'export.json','source':req['std_sha'],'control':CTRL,'head':HEAD,'request':pins['request']['sha256'],'workflow':pins['request']['workflow_sha256'],'run':pins['run'],'attempt':1}
        def hypothetical(case):
            """CASE-ONLY immutable-fingerprint test model. Never patches real reader/policy."""
            try:
                for k in ('selector','source','control','head','request','workflow','run','attempt','properties_member','export_member'):
                    if case[k]!=original[k]:return False
                g=case['group'];bm=case['binding'];stock=case['stock'];pr=case['rich'];ps=pr['harnesses'][0]['properties']
                if len(pr['harnesses'])!=1 or pr['harnesses'][0]['name']!=selector:return False
                # Exact observed packet identity, not a class/prefix/zero wildcard.
                if any(case[k]!=original[k] for k in ('stock','group','binding','compile','supervision')):return False
                if g['invocation_id']!=bm['invocation_id'] or bm['request_sha256']!=case['request']:return False
                ev.protected(g,req,data['baseline.json'],case['supervision'],case['request']);ev.provenance(g,case['compile'],req,rid,case['request'])
                decoder=rich.RegularEvidence([selector],STD);decoder.finished=True;decoder.closed={selector};decoder.records={selector:copy.deepcopy(ps)}
                try:decoder.validate(stock)
                except ValueError as exc:
                    if str(exc)!='rich metadata incomplete: file/line missing':return False
                else:return False
                if [p for p in ps if not located(p)]!=[exact]:return False
                if sha(canon(pr))!=sha(canon(original['rich'])):return False
                if len(ps)!=386 or len({p['id'] for p in ps})!=386:return False
                if any(p['status'] not in ('SUCCESS','UNREACHABLE','SATISFIED') for p in ps):return False
                for role in next(x for x in req['rows'] if x['id']==rid)['roles']:
                    ms=[p for p in ps if p['description']==role['description']]
                    if len(ms)!=1 or any(ms[0][k]!=role[k] for k in ('class','status')) or ms[0]['file']!=str(STD/role['file']) or ms[0]['line']!=str(role['line']):return False
                return True
            except (ValueError,KeyError,TypeError,IndexError):return False
        need(hypothetical(original),rid+' exact NOT_APPLIED proposal accepts authentic record only')
        mutations=['wrong_id','wrong_display_id','wrong_class','status_FAILURE','status_UNREACHABLE','status_UNKNOWN','wrong_description','wrong_raw_display','wrong_root','record_missing','record_duplicate','second_unknown_location','role_location_missing','cover_location_missing','U_location_missing','file_key_missing','line_key_missing','file_wrong_type','line_wrong_type','mixed_invocation','mixed_member','wrong_request','wrong_source','wrong_tool','wrong_cfg','wrong_namespace','wrong_export_schema','changed_protected_identity','changed_guard_status','changed_control','changed_head','changed_workflow','changed_run']
        for mutation in mutations:
            bad=copy.deepcopy(original);ps=bad['rich']['harnesses'][0]['properties'];p=next(x for x in ps if x['id']==exact['id'])
            if mutation=='wrong_id':p['id']+='x'
            elif mutation=='wrong_display_id':p['display_id']+='x'
            elif mutation=='wrong_class':p['class']='assertion'
            elif mutation.startswith('status_'):p['status']=mutation[7:]
            elif mutation=='wrong_description':p['description']+='x'
            elif mutation=='wrong_raw_display':p['location_display']+='x'
            elif mutation=='wrong_root':bad['selector']+='x'
            elif mutation=='record_missing':ps.remove(p)
            elif mutation=='record_duplicate':ps.append(copy.deepcopy(p))
            elif mutation=='second_unknown_location':next(x for x in ps if x is not p and x['class'] not in ('assertion','cover'))['file']=None
            elif mutation=='role_location_missing':next(x for x in ps if x['description']==q['literal_roles'][0]['required']['description'])['line']=None
            elif mutation=='cover_location_missing':next(x for x in ps if x['class']=='cover')['file']=None
            elif mutation=='U_location_missing':next(x for x in ps if x['status']=='UNREACHABLE')['line']=None
            elif mutation=='file_key_missing':del p['file']
            elif mutation=='line_key_missing':del p['line']
            elif mutation=='file_wrong_type':p['file']=7
            elif mutation=='line_wrong_type':p['line']=0
            elif mutation=='mixed_invocation':bad['binding']['invocation_id']='mixed'
            elif mutation=='mixed_member':bad['properties_member']='groups/s3-other/properties.json'
            elif mutation=='wrong_request':bad['binding']['request_sha256']='0'*64
            elif mutation=='wrong_source':bad['source']='0'*40
            elif mutation=='wrong_tool':bad['binding']['tool_sha']='0'*40
            elif mutation=='wrong_cfg':bad['group']['effective_cfg']=''
            elif mutation=='wrong_namespace':bad['group']['cargo_target_dir']+='/other'
            elif mutation=='wrong_export_schema':bad['stock']['schema_version']='changed'
            elif mutation=='changed_protected_identity':bad['group']['tool_fingerprints_after']['binaries']['kani_driver']['sha256']='0'*64
            elif mutation=='changed_guard_status':next(x for x in ps if x['class']=='unsupported_construct')['status']='UNKNOWN'
            elif mutation=='changed_control':bad['control']='0'*40
            elif mutation=='changed_head':bad['head']='0'*40
            elif mutation=='changed_workflow':bad['workflow']='0'*64
            elif mutation=='changed_run':bad['run']+=1
            need(not hypothetical(bad),rid+' NOT_APPLIED exact-case rejects '+mutation)
            t={'root':rid,'mutation':mutation,'expected':'REJECT','observed':'REJECT'};tests.append(t);outtests.append(t)
        semantic={'class':'unreachable','status':'SUCCESS','description':'unreachable code','file':None,'line':None,'keys_present':['file','line'],'cardinality':1,'id_and_display_id':exact['id'],'location_display':exact['location_display'],'status_UNREACHABLE_U':False,'literal_role_or_cover':False,'positive_origin':'UNKNOWN'}
        candidates.append({'root':rid,'status':'PROPOSED_NOT_APPLIED_PENDING_INDEPENDENT14_AND_ROOT_COORDINATOR','scope':'METADATA_GATE_ONLY_EXACT_ENUMERATED_CASE','fingerprint':semantic,'semantic_fingerprint_sha256':sha(canon(semantic)),'structural_packet_fingerprint_sha256':sha(canon(original)),'bindings':pick(original,['selector','source','control','head','request','workflow','run','attempt','properties_member','export_member']),'invocation_id':original['group']['invocation_id'],'namespace':original['group']['cargo_target_dir'],'argv':original['group']['argv'],'cfg':original['group']['effective_cfg'],'schema':{'stock':'0.1.0','rich':'ch8-s1-05-rich-v1','compact':'ch8-s1-05-artifact-v1'},'member_digests':{n:sha(members[gp+n]) for n in ('export.json','properties.json','receipt.json','binding-metadata.json','compile/receipt.json')},'stock_counts':gap['stock_counts'],'all_U':q['U_properties'],'all_guards':q['unsupported_guards'],'all_literal_roles_and_covers':q['literal_roles'],'allowed_missing_location_records':[exact],'allowed_missing_location_cardinality':1,'policy':'U REJECT_ALL proposalDISABLED; all role/cover/U/guard locations mandatory; no other statuses allowed than SUCCESS/UNREACHABLE/SATISFIED with exact partitions','qualification_effect':'DIAG_INIT_OPEN permanently remains diagnostic/init-provider eligibility false' if 'partial_diag' in rid else 'Only location decision proposed; bounded PFC S1 qualification remains separate root/coordinator decision','authentic_case_test':'ACCEPT_HYPOTHETICAL_ONLY','negative_tests':len(mutations)})
    samekeys=['class','status','description','file','line']
    oldp=old['exact_property']
    comparison={'old_commit':OLD,'old_review_commit':OLDREVIEW,'old_admission':old,'old_review_location_decision':oldreview,'new_record_count':3,'new_vs_old':[{ 'root':g['root'],'equal_fields':{k:g['all_missing_null_wrong_type_location_records'][0][k]==oldp[k] for k in samekeys},'same_suffix':g['all_missing_null_wrong_type_location_records'][0]['id'].endswith('.unreachable.1'),'same_zero_display_shape':g['all_missing_null_wrong_type_location_records'][0]['location_display'].startswith('library/core/src/lib.rs:0:0 in function '),'different_full_id_harness_invocation_source_request_control':True} for g in gaps],'actual_shared_emitter_or_lowering_identity':'UNKNOWN_NOT_ESTABLISHED; matching description/class/suffix/zero sentinel is structural similarity only','same_parser_normalization':'ESTABLISHED exact rich_evidence.py byte identity and authentic-field streaming replay','tool_trace':'Stock statement.rs:468-469 maps terminator source_info.span,512-516 emits assert-assume false PropertyClass::Unreachable,unreachable code. assert.rs:214-220 preserves supplied Location. cbmc_output_parser.rs:261-310 deserializes optional source fields and renders zero strings verbatim; cbmc_property_renderer.rs:333-345 prints Location; schema_utils.rs retains only failed/unsupported detail, successful system origin absent. This is a compatible emission route, NOT an actual per-record MIR/positive source binding.','actual_positive_source_origin':'UNKNOWN; lib.rs:0:0 is not a valid coordinate; no registration-line replacement','recommendation':'EXACT_ENUMERATED_CASES_PENDING_REVIEW; no prefix/lib.rs0 wildcard or transfer of old originalrun-only decision'}
    write('METADATA-GAP.json',{**json.loads((HERE/'METADATA-GAP.json').read_bytes()),'comparison':comparison,'actual_producer_history':'UNKNOWN immutable for3merge rows','runtime_location_rule_changed':False})
    write('LOCATION-PROPOSAL.json',{'schema':'s32-location-proposal-v1','status':'NOT_APPLIED','recommendation':'EXACT_ENUMERATED_CASES_PENDING; shared actual system-check identity UNKNOWN','candidates':candidates,'pinned_parser':{'control':CTRL,'path':'ch8-s1-control/rich_evidence.py','sha256':sha(blob(CONTROL,CTRL,'ch8-s1-control/rich_evidence.py')),'tool':req['tool_sha'],'stock_schema':'0.1.0','rich_schema':'ch8-s1-05-rich-v1'},'optional_general_metadata_rule':{'status':'PENDING_NOT_RECOMMENDED_FOR_ACTIVATION','requires':'Authentic shared emission/normalization identity tied to MIR/property origin, reviewed exact structural fingerprint + explicit root/source/request/invocation/export bindings, cardinality1 and complete status/count partitions. Current compact does not bind the emitter; general lib.rs0/prefix wildcard rejected.','reason':'Text/class/suffix cannot establish same emitter or cause.'},'remaining_gates':['Complete stock/schema/config/selector/unwind partitions and full property inventory; exactly1 enumerated metadata gap','All exact positive assertions SUCCESS, literal negative FAILs, covers SATISFIED; every role/cover/U/guard positively located','Every U source-local argument reviewed individually; strict producer policy remains REJECT_ALL/proposalDISABLED','Retain every unsupported guard; unknown/error/undetermined/failure/extra gap reject','Protected snapshots/native start/source/compile/PFC/contract/frame/caller bindings, cleanup and seals mandatory','No global safety/location/U/role waiver; no actual producer/history rewrite','Partial rows remain DIAGNOSTIC_ONLY_INITIALIZATION_OPEN; no init/provider qualification even after location decision','Independent14 then root/coordinator decision required for any admission'],'mutation_tests':'LOCATION-TESTS.json','runtime_or_policy_applied':False,'admission':False})
    write('LOCATION-TESTS.json',{'status':'PASS','authentic_cases':3,'negative_controls':outtests,'scope':'Bounded authentic-record mutations with existing frozen streaming parser/stock inventory/protected readers and separate exact-case model. NOT runtime policy activation.','frozen_reader':'All3 unchanged REJECT rich metadata incomplete: file/line missing','hypothetical_cases':'All3 exact authentic ACCEPT; all mutations REJECT','proposal_applied':False})

if __name__=='__main__':main()
