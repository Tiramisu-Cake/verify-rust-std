#!/usr/bin/env python3
"""Offline compact intake; adapts run-44405927807 replay. No native execution.
Reads exact Git blobs and authenticated structured members. Frozen collector only.
"""
import ast,base64,collections,copy,csv,gzip,hashlib,importlib,json,re,subprocess,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
G0=HERE.parents[5]
CONTROL=Path('/root/kani-ch8-s3-1-r2-control-w13')
CTRL='cb63033ffcde918f4341146e56373476b8eeb569'
HEAD='7497ecdb3934585634f5f04e4ff7c6cc42450c0b'
TASK='03ad6ec5bba2085c5a46419f77a4ec0ee6f3d294'
SOURCE=Path('/root/verify-rust-std-ch8-s3-1-final-w13')
checks=[]
def sha(b):return hashlib.sha256(b).hexdigest()
def write(n,v): (HERE/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def need(v,label):
    if not v:raise AssertionError(label)
    checks.append(label)
def git(repo,*args):return subprocess.check_output(['git','-C',str(repo),*args])
def blob(repo,rev,path):return git(repo,'show',rev+':'+path)
def pick(d,keys):return {k:d[k] for k in keys if k in d}
def main():
    pins=json.loads((HERE.parent/'postrun-s3-1-r2-terminal/INPUTS.json').read_bytes());pins.update(task_g0=TASK,settings='high/FastOFF preserved; no subagents',execution_scope='OFFLINE_INTAKE_ONLY')
    write('INPUTS.json',pins)
    run=json.loads((HERE/'github-run.json').read_bytes());jobs=json.loads((HERE/'github-job-collection.json').read_bytes())['jobs'];art=json.loads((HERE/'github-artifacts.json').read_bytes())['artifacts']
    need((run['id'],run['run_attempt'],run['event'],run['head_sha'],run['head_branch'],run['status'],run['conclusion'])==(pins['run'],1,'push',HEAD,pins['branch'],'completed','failure'),'connected terminal run identity')
    need(len(jobs)==1 and jobs[0]['head_sha']==HEAD and jobs[0]['run_attempt']==1 and jobs[0]['conclusion']=='failure','connected job identity')
    need(len(art)==1 and art[0]['id']==14482022386 and art[0]['size_in_bytes']==481904 and art[0]['digest']==pins['artifact']['digest'] and not art[0]['expired'],'one exact authorized compact artifact metadata')
    need(art[0]['workflow_run']['head_sha']==HEAD and art[0]['workflow_run']['id']==pins['run'],'artifact run binding')
    integ=json.loads((HERE/'artifact-integrity.json').read_bytes());gz=(HERE/'group-evidence.json.gz').read_bytes();raw=gzip.decompress(gz)
    need(sha(gz)==integ['payload_sha256'] and sha(raw)==integ['uncompressed_sha256'],'compact payload integrity')
    need(integ['sha256']==pins['artifact']['digest'].removeprefix('sha256:') and integ['bytes']==481904 and integ['digest_checked_before_zip_open'] and not integ['transport_saved'],'transport digest checked before extraction; transport never saved')
    packet=json.loads(raw);need(packet['state']=='PACKAGED' and packet['error'] is None,'compact packaged')
    data={};members={}
    for name,e in packet['files'].items():
        p=Path(name);need(not p.is_absolute() and '..' not in p.parts and p.suffix=='.json','structured boundary '+name)
        b=e['text'].encode() if e.get('encoding','utf-8')=='utf-8' else base64.b64decode(e['text'],validate=True)
        need(len(b)==e['bytes'] and sha(b)==e['sha256'],'member integrity '+name);members[name]=b;data[name]=json.loads(b)
    need(len(data)==133,'133 structured members')
    trees={}
    for kind,repo,rev in [('source',SOURCE,pins['source']['sha']),('tool',CONTROL,pins['tool']['sha']),('control',CONTROL,CTRL),('trigger',CONTROL,HEAD)]:
        tree=git(repo,'rev-parse',rev+'^{tree}').decode().strip();trees[kind]={'sha':rev,'tree':tree,'parent':git(repo,'show','-s','--format=%P',rev).decode().strip()}
        expected=pins['trigger']['tree'] if kind=='trigger' else pins['control_candidate' if kind=='control' else kind]['tree'];need(tree==expected,kind+' exact tree')
    need(trees['control']['tree']==trees['trigger']['tree'] and trees['control']['parent']==trees['trigger']['parent']==pins['trigger']['sole_parent'],'reviewed and executed same-tree siblings')
    reqbytes=blob(CONTROL,CTRL,'ch8-s1-control/CI-REQUEST.json');req=json.loads(reqbytes)
    need(sha(reqbytes)==pins['request_sha256'] and reqbytes==blob(CONTROL,HEAD,'ch8-s1-control/CI-REQUEST.json'),'request hash and executed bytes')
    wf=blob(CONTROL,CTRL,'.github/workflows/ch8-s2.yml');need(sha(wf)==pins['workflow_sha256'] and wf==blob(CONTROL,HEAD,'.github/workflows/ch8-s2.yml'),'workflow hash and executed bytes')
    for path,h in req['ci_payload_sha256'].items():need(sha(blob(CONTROL,CTRL,path))==h and blob(CONTROL,CTRL,path)==blob(CONTROL,HEAD,path),'executed payload '+path)
    sourcefiles={}
    for key in ['changed_file_sha256','cfg_pfc_source_sha256','contract_stack_source_sha256','lexical_source_sha256','ordinary_contract_source_sha256']:
        for path,h in req[key].items():
            b=blob(SOURCE,pins['source']['sha'],path);need(sha(b)==h,'source '+key+' '+path);sourcefiles[path]=h
    need(data['campaign-start.json']['request_data']==req and data['receipt.json']['request_sha256']==pins['request_sha256'],'native embedded exact request')
    deps={}
    for key,rev in [('candidate',pins['candidate_g0']),('review',pins['review_g0']),('GO',pins['GO_g0']),('task',TASK),('U_proposal',pins['offline_U_proposal']['g0'])]:
        deps[key]={'commit':rev,'tree':git(G0,'rev-parse',rev+'^{tree}').decode().strip()}
    uproposal=json.loads(blob(G0,pins['offline_U_proposal']['g0'],'research/challenge-8/kani-k1/kani3300/ch8-s3/s3-1-r2/U-SITE-PROPOSAL.json'))
    # Full exact control directory is a small source closure, not evidence logs.
    frozen={}
    with tempfile.TemporaryDirectory(prefix='s3-r2-intake-') as td:
        tmp=Path(td);scripts=tmp/'reader';scripts.mkdir()
        for name in git(CONTROL,'ls-tree','-r','--name-only',CTRL,'ch8-s1-control').decode().splitlines():
            rel=Path(name).relative_to('ch8-s1-control');b=blob(CONTROL,CTRL,name);f=scripts/rel;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b);frozen[str(rel)]={'sha256':sha(b),'bytes':len(b)}
        sys.path.insert(0,str(scripts))
        r=importlib.import_module('runner');c=importlib.import_module('s3_campaign');ev=importlib.import_module('s3_evidence');richmod=importlib.import_module('rich_evidence');policy=importlib.import_module('s3_policy')
        need(r.load_request()==req,'frozen request loader')
        # Existing source-only helpers. No compiler/expansion/full runner.
        static=policy.validate_source(SOURCE,req)
        write('SOURCE-GATES.json',{'status':static['status'],'full_report_canonical_sha256':sha(json.dumps(static,sort_keys=True,separators=(',',':')).encode()),'reports':{k:pick(v,['status','schema','source_sha','source_tree','source_files_sha256','compilation','native_compile','proof_credit','qualification_from_registration','limits']) for k,v in static['reports'].items()},'scope':'Existing source-only validators; complete reports reproducible via exact pinned helpers; compact projection only.','proof_credit':'NONE'})
        local=tmp/'local';upload=tmp/'upload';local.mkdir();upload.mkdir()
        for name,b in members.items():p=local/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
        (upload/'group-evidence.json.gz').write_bytes(gz)
        left=c.collect([local],req);right=c.collect([upload],req)
        need(left==right,'exact frozen collector materialized/upload-only equality')
        done=c.sealed(local);need(list(done)==req['s3']['selected'],'all nine sealed in selected prefix order')
        need(not left['global_stop'] and left['selected_missing_groups']==[],'no global STOP; no selected group missing')
        need(data['receipt.json']['state']=='SELECTED_PARTIAL' and data['receipt.json']['stop_reason'] is None,'native SELECTED_PARTIAL without global stop')
        write('PREFIX-REPLAY.json',{'control':CTRL,'collector_state':left['state'],'global_stop':left['global_stop'],'global_stops':left['global_stops'],'selected_missing_groups':left['selected_missing_groups'],'completed_prefix':list(done),'local_upload_equal':True,'all_seal_digests_verified_by_frozen_reader':True,'rows':[{k:x[k] for k in ('id','status','outcome','reason') if k in x} for x in left['rows']],'scope':'Completion seals preserve observations and UNKNOWNs; not qualification/admission.'})
        baseline=data['baseline.json'];inventory=[];cost=[];qual=[];ugaps=[];gap=None;epoch=[];nativeprojections={}
        for rank,row in enumerate(req['rows'],1):
            rid=row['id'];gp='groups/s3-'+rid+'/';g=data[gp+'receipt.json'];co=data[gp+'compile/receipt.json'];can=data[rid+'/receipt.json'];sup=data['workers/'+rid+'-supervision.json'];life=data['workers/'+rid+'-lifecycle.json'];launch=data['workers/'+rid+'-launch.json'];e=data[gp+'export.json'];pr=data[gp+'properties.json'];hs=e.get('harnesses',[]);h=hs[0] if hs else {};props=pr.get('harnesses',[{'properties':[]}])[0]['properties'];execution=g['execution'];bm=data[gp+'binding-metadata.json']
            need(g['request_sha256']==pins['request_sha256'] and g['std_sha']==pins['source']['sha'] and g['tool_sha']==pins['tool']['sha'],rid+' source/tool/request')
            need(ev.provenance(g,co,req,rid,pins['request_sha256']),rid+' source/compile provenance')
            protected=ev.protected(g,req,baseline,sup,pins['request_sha256']);need(not protected['observed_errors_ignored'],rid+' all-state protected evidence')
            need(c.snapshots.validate_pair(baseline,life['pre'],life['post'],life['context']),rid+' controller epochs')
            actual_argv=g['argv'];std=Path('/home/runner/work/kani/kani/export');tool=Path('/home/runner/work/kani/kani/tool');export=Path('/home/runner/work/_temp/ch8-s1-receipts')/(gp+'export.json')
            need(actual_argv==r.build_argv(std,tool,[row['selector']],row['unwind'],export),rid+' singleton exact argv')
            need(g['effective_cfg']==req['flags']['RUSTFLAGS'] and g['native_start_verified'] and [x['selector'] for x in g['native_start_events']]==[row['selector']],rid+' effective cfg and native start')
            need(g['cargo_target_dir']==str(std/'target/ch8-s1-cargo'/g['invocation_id']),rid+' fresh namespace')
            stages={'E0':baseline['binaries'],'pre':life['pre']['binaries'],'worker.BEFORE':g['tool_fingerprints_before'],'worker.AFTER':g['tool_fingerprints_after'],'post':life['post']['binaries']}
            for label,snap in stages.items():need(r.fingerprints_match(baseline['binaries'],snap),rid+' canonical binaries '+label)
            epoch.append({'id':rid,'context':life['context'],'all_five_equal_to_E0':True,'stages':{k:v['binaries'] for k,v in stages.items()},'protected':protected})
            rootsmeta=[];registrations=[]
            for m in bm['native_metadata']:
                if m.get('state')!='CAPTURED':continue
                b=m['text'].encode() if m.get('encoding','utf-8')=='utf-8' else base64.b64decode(m['text'],validate=True)
                need(len(b)==m['bytes'] and sha(b)==m['sha256'],rid+' native metadata digest '+m['path'])
                md=json.loads(b)
                rootsmeta += [dict(x,metadata_path=m['path'],metadata_sha256=m['sha256']) for x in md.get('proof_harnesses',[]) if x['pretty_name']==row['selector']]
                registrations += [x for x in md.get('contracted_functions',[]) if row['selector'] in x.get('harnesses',[])]
            need(len(rootsmeta)==1,rid+' unique native registration')
            rm=rootsmeta[0];need(rm['original_file']==str(std/req['source_bindings'][rid]['file']),rid+' native source file')
            kind=rm['attributes']['kind'];need((kind=={'ProofForContract':{'target_fn':req['source_bindings'][rid]['target']}} if row['mode']=='PFC' else kind=='Proof'),rid+' native PFC/Original kind')
            if row['mode']=='PFC':need(len(registrations)==1 and rm['attributes']['stubs']==[] and rm['attributes']['verified_stubs']==[],rid+' PFC provider without assumed summary')
            rebound=r.validate_export_value(e,row,source_binding=req['source_bindings'][rid],std=std,group_selectors=[row['selector']]) if h else None
            literal=[]
            for role in row['roles']:
                matches=[p for p in props if p['description']==role['description']]
                ok=bool(matches) and all(p['class']==role['class'] and p['status']==role['status'] and p['file']==str(std/role['file']) and str(p['line'])==str(role['line']) for p in matches)
                literal.append({'description':role['description'],'class':role['class'],'required_status':role['status'],'source_file':role['file'],'source_line':role['line'],'source_sha256':role['source_sha256'],'source_text':role['source_line'],'native_matches':matches,'exact_match':ok})
            if h:need(all(x['exact_match'] for x in literal),rid+' all literal roles same invocation exact site/status')
            failed=[x for x in props if x['status']=='FAILURE'];unreachable=[x for x in props if x['status']=='UNREACHABLE'];covers=[x for x in props if x['class']=='cover']
            if h:
                need(h['n_properties']==len(props) and h['checks']['total']+h['covers']['total']==len(props),rid+' full count inventory')
                need(len(failed)==(1 if row['expected']=='DETECTED' else 0),rid+' intended failure count')
                need(len(covers)==row['required_cover_count'] and all(x['status']=='SATISFIED' for x in covers),rid+' exact SAT covers')
            urecords=[]
            for p in unreachable:
                rel=p['file'].split('/export/',1)[1];line=int(p['line']);sb=blob(SOURCE,pins['source']['sha'],rel);lines=sb.decode().splitlines();context='\n'.join(f'{i+1}: {lines[i]}' for i in range(max(0,line-5),min(len(lines),line+4)))
                arg,predicate,premises=uargument(rid,p,req)
                proposal=[x for x in uproposal['sites'] if x['file']==rel and x['line']==line and x['sha256']==sha(sb) and all(x['historical_exact_instance'].get(k)==p.get(k) for k in ['id','class','description','file','line'])]
                u={'root':rid,'selector':row['selector'],'invocation_id':g['invocation_id'],'property':p,'member':gp+'properties.json','member_sha256':sha(members[gp+'properties.json']),'source_file':rel,'source_sha':pins['source']['sha'],'source_sha256':sha(sb),'source_line':line,'source_context':context,'effective_cfg':g['effective_cfg'],'provider_target':req['source_bindings'][rid]['target'],'predicate':predicate,'premises':premises,'source_local_argument':arg,'assessment':'SOURCE_LOCAL_DEFINEDNESS_ARGUMENT' if arg else 'UNKNOWN','origin_assurance':'SOURCE_REPORTED_SITE_CONTEXT; no independent AST/MIR/caller binding','frozen_proposal_exact_site_matches':len(proposal),'proposal_argument_reused':False,'policy_status':'REJECT_ALL_UNCHANGED; proposal DISABLED'}
                # Same site may be used as a reference, but every root instance is independently contextualized here.
                urecords.append(u)
            ugaps.extend(urecords)
            strict=policy.expected_observation(row,rebound or {},{'name':row['selector'],'properties':props})
            need(not strict,rid+' strict policy remains unqualified')
            cs=collections.Counter(x['status'] for x in props if x['class']!='cover');classes={k:dict(collections.Counter(x['status'] for x in props if x['class']==k)) for k in sorted({x['class'] for x in props})}
            bindings={'assurance':'Profiles v4 SOURCE_REPORTED; not independent MIR proof','source_binding':req['source_bindings'][rid],'native_registration':rootsmeta,'registered_provider_context':registrations,'native_kind':kind,'effective_cfg':g['effective_cfg'],'request_flags':req['flags'],'type':'u8','comparator':'KeyLess<u8>; stateless full byte a<b','source_domain':domain(rid),'caller_scope':'Only exact harness, backing, offsets, initialization, frame and normal-return conditions; no generic T/F, allocation lifting, unwind theorem or caller summary.','compiler_identity_status':bm['compiler_identity_status'],'native_metadata_state':bm['native_metadata_state'],'independent_binding':'UNKNOWN_NOT_EXPORTED_BY_PINNED_PRODUCER','initialization_assurance':'Source initializes outside/output canaries, leaves intended destination MaybeUninit, then typed loads after actual call; stock exported checks retained. No separate experimental uninit-checks/valid-value-checks flags enabled, no independent initialization theorem claimed.'}
            entry={'id':rid,'selector':row['selector'],'mode':row['mode'],'native_verdict':h.get('outcome'),'native_check_counts':dict(cs),'native_checks':h.get('checks'),'native_covers':h.get('covers'),'n_properties':h.get('n_properties'),'rich_state':pr['state'],'canonical_status':can['status'],'canonical_outcome':can['outcome'],'strict_expected_match':strict,'immutable_policy':req['unreachable_admission'],'literal_roles':literal,'failed_properties':failed,'unwinding_panic_safety_by_class':classes,'U_instances':len(urecords),'U_arguments_complete':bool(h) and all(x['assessment']=='SOURCE_LOCAL_DEFINEDNESS_ARGUMENT' for x in urecords),'bindings':bindings,'S1_assessment':('PROVISIONALLY_ELIGIBLE_LOCATION_DECISION_PENDING' if rid=='s3_sort4_u8_same_alloc' else 'PROVISIONALLY_ELIGIBLE_SOURCE_REPORTED' if h else 'NO_COMPLETED_NATIVE_RESULT'),'admission':'NOT_GRANTED; root/coordinator decision; no B1/B2 promotion','native_links':{k:{'member':gp+k,'sha256':sha(members[gp+k])} for k in ['export.json','properties.json','binding-metadata.json','receipt.json']}}
            qual.append(entry)
            execution_cost=pick(execution,['elapsed_seconds','original_exit_code','signal','timed_out','termination_reason','child_shutdown_verified','rss_peak_kib','rss_scope','rss_sample_period_seconds','component_group_peak_kib','component_rss_scope','cleanup_errors'])
            cost.append({'id':rid,'compile_elapsed_upper_bound_seconds':co['elapsed_upper_bound_seconds'],'compile_scope':co['scope'],'compile_boundary':co['boundary'],'compile_state':co['state'],'native_verification_time_s':h.get('resources',{}).get('verification_time_s','UNKNOWN_NO_COMPLETED_NATIVE_RESOURCE'),'native_wall_time_s':e.get('wall_time_s','UNKNOWN'),'execution':execution_cost,'worker_supervision':pick(sup,['worker_exit','cutoff','elapsed_seconds','limit_initiated','outer_sampled_peak_kib','outer_rss_scope','supervisor_error','orphan_survivors_at_worker_exit']),'containment':pick(sup['containment'],['verified','scope','elapsed_seconds','signals','reaped_adopted','worker_exit']),'censoring':'TERMINATED_UNFINISHED' if execution.get('termination_reason') else 'NONE_NATIVE_COMPLETED','symex_backend_steps_VCC':'UNKNOWN_NOT_EXPORTED','RSS_at_kill_and_phase':('Trigger sample6326988KiB reconstructed from recorded peak and exact runner first-overcap break; each previous PGID sample<=6291456KiB. RSS at subsequent signal/kill UNKNOWN. Post-compilation; precise symex/backend phase UNKNOWN.' if rid=='s3_insert_tail_u8_rel16' else 'UNKNOWN_NO_TRIGGER_SAMPLE_OR_PHASE_TELEMETRY; recorded PGID and component maxima are separate samples'),'verification_budget_after_compile_upper_bound_seconds':600-co['elapsed_upper_bound_seconds'],'not_backend_duration':True,'next_root':req['rows'][rank]['id'] if rank<len(req['rows']) else None})
            inventory.append({'id':rid,'rank':rank,'selector':row['selector'],'mode':row['mode'],'assurance':row['assurance'],'unwind':row['unwind'],'native_verdict':h.get('outcome',{}).get('verdict','UNKNOWN'),'canonical_status':can['status'],'canonical_outcome':can['outcome'],'group_state':g['state'],'native_start_events':g['native_start_events'],'native_start_verified':g['native_start_verified'],'argv':g['argv'],'effective_cfg':g['effective_cfg'],'invocation_id':g['invocation_id'],'cargo_target_dir':g['cargo_target_dir'],'export':gp+'export.json','export_sha256':sha(members[gp+'export.json']),'native_export_state':e.get('run_state'),'native_outcome':e.get('outcome'),'source_before':g['source_before'],'source_after':g['source_after'],'source_under_test':g['source_under_test'],'snapshot_errors':g['snapshot_errors'],'binary_identity':g['binary_identity'],'protected':protected,'compile':co,'binding_metadata':g['binding_metadata'],'canonical_reason':can.get('reason'),'original_exit':execution.get('original_exit_code'),'signal':execution.get('signal'),'worker_exit':sup['worker_exit'],'sealed':True})
            nativeprojections[rid]={'export':pick(e,['run_state','outcome','configuration','harness_selection','enabled_unstable_features','kani_commit','kani_commit_dirty','summary']),'harness':pick(h,['name','file','line','contract','attributes','outcome','resources','resolved_unwind','resolved_solver','n_properties','n_failed','failure_kind','failed_properties','checks','covers','unsupported_constructs','warnings'])}
            if rid=='s3_sort4_u8_same_alloc':
                bad=[p for p in props if not isinstance(p.get('file'),str) or not p['file'] or not isinstance(p.get('line'),str) or not re.fullmatch(r'[1-9][0-9]*',p['line'])]
                need(len(bad)==1 and bad[0]['class']=='unreachable' and bad[0]['status']=='SUCCESS','one authentic offending successful system property')
                decoder=richmod.RegularEvidence([row['selector']],std)
                decoder.records={row['selector']:copy.deepcopy(props)};decoder.finished=True;decoder.closed={row['selector']}
                try:decoder.validate(e)
                except ValueError as exc:metadata_error=str(exc)
                else:raise AssertionError('authentic sort4same must retain current metadata rejection')
                need(metadata_error=='rich metadata incomplete: file/line missing','authentic sort4same full inventory passes until exact location gate')
                one=richmod.RegularEvidence([row['selector']],std);a=bad[0]
                reconstruction=('Checking harness '+row['selector']+'...\nRESULTS:\nCheck 1: '+a['display_id']+'\n\t - Status: '+a['status']+'\n\t - Description: "'+a['description']+'"\n\t - Location: '+a['location_display']+'\nSUMMARY:\n').encode()
                one.feed(reconstruction);one.finish()
                need(one.error is None and one.records[row['selector']]==bad,'authentic field reconstruction retains display sentinel and normalized nulls')
                gap={'id':rid,'offending_records':bad,'count':len(bad),'rich_missing_sites':pr.get('missing_sites'),'rich_error':pr.get('error'),'stock_export_representation':'Successful property details are omitted; success count and non-success ID buckets only. No per-property SourceLocation in stock JSON.','rich_fields':{'file':'PRESENT_NULL','line':'PRESENT_NULL','location_display':'PRESENT lib.rs:0:0 plus exact harness function'},'cause':'Display preserves a file with zero line/column; rich _record positive-line regex rejects :0:0 and sets both normalized file/line to null. validate requires positive line or exact preexisting location_exception; this harness is absent from that map.','source_trace':{'control_commit':CTRL,'tool_commit':pins['tool']['sha'],'reader':'ch8-s1-control/rich_evidence.py:148-173,213-217','producer_display':'kani-driver/src/cbmc_output_parser.rs:261-310; cbmc_property_renderer.rs:274 onward'},'native_location_recovery':'Display file library/core/src/lib.rs, line token 0 and column token 0 recovered; zero is a sentinel, not a valid source coordinate. Real originating source line UNKNOWN. No raw CBMC per-check sourceLocation retained in compact export.','classification':{'role':False,'cover':False,'class':'unreachable','status':'SUCCESS','description':'unreachable code','failed':False,'unwinding':False,'panic':'No failure; successful absence-of-unreachable-code system check; compiler lowering origin UNKNOWN','safety':'system reachability/UB check, retain intact'},'actual_reader_condition':"all(valid nonempty file and positive decimal line OR location_exception(harness,p))",'call_chain':['runner._run_group:1178 rich.validate(raw)','rich_evidence.RegularEvidence.validate:213-217 positive coordinates OR exact exception','runner._run_group except:1236 properties.json persisted INCOMPLETE','s3_campaign.root_outcome records UNKNOWN, seals and continues'],'original_exception':g['original_exception'],'all_literal_roles_bound':all(x['exact_match'] for x in literal),'all_native_inventory_counts_and_statuses_match':True,'offline_reader_rejection_reproduced':metadata_error,'reconstruction_scope':'One record reconstructed only from authentic structured fields; ordinal1 for isolated parser test, not original stream ordinal.','policy_location_exception_matches':richmod.location_exception(row['selector'],bad[0]),'repair_proposal':'NOT_APPLIED: original worker/reviewer can add a narrowly reviewed location-only exception for this exact harness/id/display_id/class=unreachable/status=SUCCESS/description/display tuple, preserving null coordinates, same-invocation totals/status validation, strict U and role gates; alternatively producer provides authentic positive origin. Never global missing-location allowance.','regression_proposal':'Feed authentic compact offending display record to existing RichParser; require normalized nulls and current rejection. Any reviewed exception must reject changed harness/id/class/status/description/display, locationless literal roles and extra missing-site records; valid role bindings remain unchanged.','remaining':'Root/coordinator must decide whether source-reported S1 location-only eligibility suffices; producer rejection remains immutable.'}
                write('METADATA-GAP.json',gap)
        need(len(ugaps)==42 and all(x['assessment']=='SOURCE_LOCAL_DEFINEDNESS_ARGUMENT' for x in ugaps),'42 distinct invocation/site U arguments without waiver')
        need(len({x['invocation_id'] for x in inventory})==9,'nine distinct fresh namespaces')
        need(sum(x['native_verdict']=='SUCCESS' for x in inventory)==4 and sum(x['native_verdict']=='FAILURE' for x in inventory)==3,'four native successes and three literal negative failures')
        # Bounded reader controls: mutate only temp copies, never evidence or policy.
        r0=req['rows'][0]['id'];g0=data['groups/s3-'+r0+'/receipt.json'];bad=copy.deepcopy(g0);bad['tool_fingerprints_before']['binaries']['kani_driver']['sha256']='0'*64
        try:ev.protected(bad,req,baseline,data['workers/'+r0+'-supervision.json'],pins['request_sha256'])
        except ev.EvidenceError:drift_rejected=True
        else:drift_rejected=False
        need(drift_rejected,'frozen protected reader rejects changed hash')
        need(all((local/n).read_bytes()==b for n,b in members.items()),'all authentic structured evidence unchanged by replay')
    write('INVENTORY.json',{'selected':inventory,'deferred':req['s3']['deferred'],'deferred_state':'NOT_SELECTED; no promotion','source_files':sourcefiles,'baseline':data['baseline.json'],'epoch_comparisons':epoch,'physical_file_identity':'UNKNOWN stat/inode/realpath not recorded; canonical strings and recorded hashes match','request':req,'workflow_sha256':sha(wf)})
    write('NATIVE.json',nativeprojections)
    write('QUALIFICATION.json',{'schema':'S3-S1-criteria-provisional-v1','assurance':'SOURCE_REPORTED Profiles v4; independent proof credit NONE','strict_policy':req['unreachable_admission'],'producer_policy_outcome':'0/9 expected matches; native SUCCESS is not admission','rows':qual,'U_instances':ugaps,'decision_required':['Root/coordinator assesses site-local arguments under S1; producer proposal remains disabled.','sort4same location-only exception/admission decision; fix NOT_APPLIED.','No leaf is an assumed summary for S3-2; caller domains/frame/init/locality must separately match.'],'generic_B1_B2_credit':'NONE'})
    write('COST.json',{'campaign_elapsed_seconds':data['receipt.json']['phase_elapsed_seconds'],'caps':pins['caps'],'rows':cost,'job_steps':jobs[0]['steps'],'job_started_at':jobs[0]['started_at'],'job_completed_at':jobs[0]['completed_at'],'compiler_metric':'compile receipt elapsed_upper_bound_seconds is observation to first stock initial export, not exact compiler CPU or separately measured exclusive compile time.','RSS_limits':'Local PGID polled 6GiB; outer sampled census12GiB+2GiB headroom. Neither is true kernel/cgroup/tree peak. Component maxima are non-simultaneous; trigger RSS and kill phase not separately exported.','no_speedup_claim':'No matched problem/binary/control comparison.'})
    provenance={'task':TASK,'source_tool_control_trigger':trees,'dependencies':deps,'artifact':pins['artifact'],'payload_sha256':sha(gz),'compact_uncompressed_sha256':sha(raw),'frozen_reader_source_files':frozen,'base_helpers':['run-44405927807/acquire.py','run-44405927807/replay.py','exact cb6303 collect/s3_campaign/s3_evidence/rich_evidence/s3_policy helpers'],'restricted_actions':'No source/policy/control/CI/accounting edits; no push; no compiler/solver/native execution; no subagents','metadata_access_note':'Direct jobs/{id} GET rejected by connector allowlist INVALID_ARGUMENT; full run jobs collection provided equivalent job identity/step metadata.'}
    write('PROVENANCE.json',provenance)
    write('VALIDATION.json',{'status':'PASS','checks':checks,'checks_count':len(checks),'raw_logs_or_transport_zip_saved':False,'native_reexecuted':False,'policy_modified':False})
    with (HERE/'ROOTS.csv').open('w',newline='') as f:
        fields=['id','rank','mode','unwind','native_verdict','canonical_status','canonical_outcome','group_state','original_exit','signal','worker_exit','sealed'];w=csv.DictWriter(f,fields,lineterminator="\n");w.writeheader();w.writerows({k:x[k] for k in fields} for x in inventory)
    write('RESULT.json',{'schema':'S3-r2-terminal-intake-v1','status':'READY','run':pins['run'],'native_run':'completed/failure','campaign':'SELECTED_PARTIAL','campaign_elapsed_seconds':data['receipt.json']['phase_elapsed_seconds'],'global_stop':False,'completed_sealed_prefix':9,'native_success':4,'native_literal_negative_failure':3,'no_completed_native_result':2,'strict_expected_matches':0,'S1_provisional_source_reported':6,'S1_provisional_location_decision_pending':1,'metadata_offending_records':1,'cutoffs':{'s3_insert_tail_u8_rel16':'local sampled PGID RSS cap;112.349s;SIGTERM15','s3_merge8_u8_same_alloc':'whole-child timeout;600.205s includes compilation;SIGTERM15'},'proof_credit':'NONE','policy_changes':False,'remaining_unknown':['actual positive originating source coordinate for sort4same system property','AST/MIR/caller binding not exported by producer','exact kill-time RSS/phase, symex/backend/steps/VCC and censored verification duration','completed insert_tail/merge8same proofs and any S3-2 caller proof/admission'],'handoff':'Exact committed intake for root and original planner13; no offline DAG redesign.'})
    print(json.dumps({'status':'PASS','checks':len(checks),'native_success':4,'negative_failures':3,'U_instances':len(ugaps),'sealed_prefix':9}))

def domain(rid):
    return {'checker_order_corrupt':'Fixed [1,2] -> [2,1]; length2 order corruption.','checker_count_corrupt':'Fixed [1;32], output[31]=2; length32 multiplicity corruption.','sort13_weak':'13 arbitrary independent full bytes; weak s2_swap_seam ordinary stub; negative only, no actual sort13 proof.','s3_swap_u8_geometry':'Initialized arbitrary [u8;34], base0..20, a,b0..12 including equal/reversed; exact transfer and all outside frame.','s3_sort4_u8_separate':'Arbitrary initialized src[u8;6], src[1..5], separate MaybeUninit dst[6] output[1..5]; initialized canaries0/5, typed output loads, full source frame.','s3_sort4_u8_same_alloc':'Arbitrary before[u8;48]; src,dst0..44, length4 nonoverlap either order, all outside destination initialized; output initially MaybeUninit; full source/outside frame and symbolic canary, typed output loads.','s3_insert_tail_u8_rel16':'Initialized arbitrary [u8;34], begin1..16 tail1..16; sorted prefix, active length2..17, full outside frame.','s3_merge8_u8_separate':'Arbitrary src[u8;10], src[1..9] two sorted halves4+4; separate MaybeUninit dst[10], initialized canaries0/9 and typed output loads.','s3_merge8_u8_same_alloc':'Arbitrary before[u8;48]; src,dst0..40, nonoverlap length8 either order; sorted halves4+4; only source range borrowed, raw destination; initially uninitialized output, initialized outside; typed output loads and full source/outside frame.'}[rid]

def uargument(rid,p,req):
    pid=p['id'];line=int(p['line']);site=p['file'].split('/export/')[1]
    if site.endswith('/fmt/mod.rs') and line==820:
        return ('The source expression shifts by literal1; x86_64 usize has64 bits, so the checked shift-count condition 1<64 holds for every s.len(). No claim of lost-bit absence or formatting caller purity is needed.','shift_count(1) < usize::BITS(64)',['Exact from_str site; target x86_64; source shift is s.len() << 1 | 1.'])
    if site.endswith('/num/uint_macros.rs') and line in (3222,3224):
        return (('In the self<other branch, other-self is defined for all usize operands.' if line==3222 else 'In the else branch, self>=other and self-other is defined for all usize operands.'),('self < other implies other >= self' if line==3222 else '!(self < other) implies self >= other'),['Exact usize::abs_diff branch; all usize operands allowed; no caller range assumption.'])
    if site.endswith('/ptr/const_ptr.rs') and line==1479:
        return ('Execution reaches align-1 only after the non-power-of-two branch panics. A power of two is nonzero, so align>=1; subtraction cannot underflow. The separate alignment/pointer/panic properties are retained.','is_power_of_two(align) implies align>=1',['Exact is_aligned_to guard and continuation; no ownership inferred from addresses.'])
    if site.endswith('/ub_checks.rs') and line==148:
        return ('The source if size==0 selects usize::MAX and skips division; the division arm is reached only with size!=0. For u8 the concrete size is1 as well.','else(size==0) implies divisor size!=0',['Exact is_valid_allocation_size conditional; Rust conditional branch evaluation; no removal of allocation validity checks.'])
    if site.endswith('/smallsort.rs') and line in (782,783):
        return ('c2 is the bool result of the concrete KeyLess<u8> comparison. Both c2 as usize and (!c2 as usize) are0 or1; 2+operand<=3, far below usize::MAX. This is the arithmetic condition only; source/output provenance, writes and initialization remain separately checked.','2 + bool_as_usize <=3 <=usize::MAX',['Exact sort4_stable::<u8,KeyLess<u8>> site; '+domain(rid)])
    if site.endswith('/smallsort.rs') and line in (974,990,991,992):
        expr={974:'len/2',990:'len_div_2-1',991:'len-1',992:'len-1'}[line]
        return ({974:'The divisor is the integer literal2, hence nonzero, independently of v length.',990:'This singleton harness passes src[1..9], length8; len_div_2=4. Thus4-1=3 is defined. Keep the source length and source-reported PFC actual-body context; no generic length claim.',991:'This singleton harness passes a length8 slice, so len-1=7 is defined for right_rev.',992:'This singleton harness passes a length8 slice, so len-1=7 is defined for dst_rev; destination writability remains separate.'}[line],expr+' defined',['Exact bidirectional_merge::<u8,KeyLess<u8>>; '+domain(rid),'Native registration matches target; independent MIR origin UNKNOWN.'])
    if site.endswith('/sorting_model.rs'):
        n={'checker_order_corrupt':2,'checker_count_corrupt':32,'sort13_weak':13}.get(rid)
        if n is None:return (None,'UNKNOWN',['Unexpected caller context'])
        args={100:'The order loop begins i=1 and runs only while i<before.len<=32; i+1<=32 at the increment, so no usize overflow.',106:'The outer count loop runs with i<before.len<=CAP32; before.values has fixed capacity32, so before.values[i] is in bounds.',111:'The inner loop guard j<before.len<=CAP32 makes before.values[j] in bounds; old_count starts0 and increments at most once per j iteration.',112:'The entry guard requires before.len==values.len(); inner j<before.len therefore bounds values[j]. new_count starts0 and increments at most once per j iteration.',113:'At inner-loop increment, j<before.len<=32, so j+1<=32 and cannot overflow.',118:'At outer-loop increment, i<before.len<=32, so i+1<=32 and cannot overflow.'}
        text=args.get(line)
        if line==111 and 'overflow' in p['description']:text='old_count starts0 for each query and counts at most one equality per inner iteration. With j<before.len<=32, old_count+1<=32; no usize overflow.'
        if line==112 and 'overflow' in p['description']:text='new_count starts0 for each query and counts at most one equality per inner iteration. With j<before.len<=32, new_count+1<=32; no usize overflow.'
        return (text,'entry guards plus loop index/count bounds0..32; exact '+p['description'],['active_post exact early validity/length/CAP guards; fixed Snapshot.values[32]',f'{rid} invokes post with source/output length{n}; CAP32','Short-circuit negative results may render later sites UNREACHABLE; that status is not the argument.'])
    return (None,'UNKNOWN',['No source-local argument established'])
if __name__=='__main__':main()
