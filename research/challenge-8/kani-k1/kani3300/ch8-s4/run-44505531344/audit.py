#!/usr/bin/env python3
"""Targeted offline dependency, inventory and observed/source phase audit only."""
import collections,gzip,hashlib,json,re,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
G0=HERE.parents[5]
BASE='research/challenge-8/kani-k1/'
checks=[]
def sha(b):return hashlib.sha256(b).hexdigest()
def read(n):return json.loads((HERE/n).read_bytes())
def write(n,v):(HERE/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def blob(repo,rev,path):return subprocess.check_output(['git','-C',str(repo),'show',rev+':'+path])
def need(v,label):
    if not v:raise AssertionError(label)
    checks.append(label)
def context(b,n,radius=4):
    ls=b.decode().splitlines()
    return '\n'.join(f'{i+1}: {ls[i]}' for i in range(max(0,n-1-radius),min(len(ls),n+radius)))
def main():
    pins=read('INPUTS.json')['terminal_inputs'];roots=read('ROOTS.json');req=roots['request']
    q=read('QUALIFICATION.json');props=read('NATIVE-PROPERTIES.json');cost=read('COST.json')
    packet=json.loads(gzip.decompress((HERE/'group-evidence.json.gz').read_bytes()))
    data={n:json.loads(e['text']) for n,e in packet['files'].items()}
    deps=[]
    for kind,pin,rev in [('author',pins['author'],pins['author']['commit']),('review',pins['independent_review'],pins['independent_review']['g0'])]:
        prefix=BASE+pin['path']+'/'
        b=blob(G0,rev,prefix+'MANIFEST.json');m=json.loads(b)
        need(sha(b)==pin['manifest_sha256'],kind+' exact manifest digest')
        for name,entry in m['files'].items():
            need(not Path(name).is_absolute() and '..' not in Path(name).parts,kind+' safe manifest path '+name)
            member=blob(G0,rev,prefix+name)
            need(len(member)==entry['bytes'] and sha(member)==entry['sha256'],kind+' exact immutable file '+name)
        deps.append({'kind':kind,'commit':rev,'manifest_sha256':sha(b),'validated_files':len(m['files'])})
    review=json.loads(blob(G0,pins['independent_review']['g0'],BASE+pins['independent_review']['path']+'/FINDINGS.json'))
    rin=json.loads(blob(G0,pins['independent_review']['g0'],BASE+pins['independent_review']['path']+'/INPUTS.json'))
    need(review['decision']=='APPROVE' and review['blocking_findings']==[] and review['new_nonblocking_findings']==[], 'independent exact-package APPROVE without blockers')
    need(rin['author_commit']==pins['author']['commit'] and rin['pins']['control']==pins['control_reviewed'] and rin['pins']['source']==pins['source'], 'review exact author/source/control pins')
    closed=review['closed_author_findings']
    need(len(closed)==1 and closed[0]['id']=='AUTHOR-FALLBACK-EMPTY-OBJECT' and closed[0]['final']==pins['control_reviewed']['sha'] and closed[0]['status']=='INDEPENDENTLY_CLOSED_ON_EXACT_FINAL_OBJECT','present-empty-object finding closed on actual control object only')
    go=json.loads(blob(G0,pins['rootGO']['commit'],BASE+pins['rootGO']['path']+'/ROOT-RECHECK.json'))
    need(go['author']==pins['author']['commit'] and go['review']==pins['independent_review']['g0'] and go['verdict']=='APPROVE' and go['findings']==[], 'rootGO exact approved author/review')
    for kind,key in [('source','source'),('control','control_reviewed'),('tool','tool')]:
        need(go['gitpins'][kind]==pins[key],'rootGO '+kind+' exact pins')
    need(go['prior_root_author_check']['request_sha256']==pins['request']['sha256'] and go['prior_root_author_check']['workflow_sha256']==pins['request']['workflow_sha256'],'rootGO request/workflow hashes')
    baseline=data['baseline.json']
    for kind in ['source','tool']:
        pin=pins[kind]
        prefix='std' if kind=='source' else 'tool'
        need(baseline['source'][prefix+'_sha']==pin['sha'] and baseline['source'][prefix+'_tree']==pin['tree'],'actual native '+kind+' checkout observed SHA/tree')
    write('DEPENDENCIES.json',{'validated_manifests':deps,'independent_review':review,'rootGO_commit':pins['rootGO']['commit'],'consumed_one_run':True,'request_sha256':go['prior_root_author_check']['request_sha256'],'workflow_sha256':go['prior_root_author_check']['workflow_sha256'],'source_control_tool_actual_checkout':'MATCH actual source/tool SHA/tree/file hashes and control SHA/tree/parent/clean; baseline and per-row protected/provenance readers. Native source/tool Git dirty/parent not separately exported; pinned local parents/clean and controller context remain source-reported context, not a new native cleanliness proof.','host344':'Historical regression result only: 679.1141679468565s, margin1.5903069777871495 at1080s. No rerun, proof or native fit credit.','accounting':'No ledger read for accounting, mutation, reservation or charge; historical GO fields are dependency data only'})
    guards=[]
    for row in q['rows']:
        if not isinstance(row['unsupported_guards'],list):continue
        for p in row['unsupported_guards']:
            rel=p['file'].split('/export/',1)[1];b=blob(pins['source']['repo'],req['std_sha'],rel)
            need(p['id']=='kani::mem::cbmc::same_allocation.unsupported_construct.1' and p['status']=='SUCCESS','retain exact observed SUCCESS unsupported guard')
            guards.append({'root':row['id'],'selector':row['selector'],'invocation_id':row['native_registration'].get('mangled_name'),'property':p,'member':props[row['id']]['member'],'member_sha256':props[row['id']]['sha256'],'source_sha':req['std_sha'],'source_file':rel,'source_sha256':sha(b),'source_context':context(b,int(p['line'])),'assessment':'SOURCE_REPORTED_GUARD_SUCCESS_ONLY','source_local_context':'Fixed initialized live Cell [0,1] -> [0,0] checker fixture. The pointer guard status remains recorded; it neither establishes generic allocation semantics nor licenses unsupported operations.','independent_MIR_or_guard_reachability':'UNKNOWN','admission':False})
    need(len(guards)==1,'one actual guard in complete negative inventory; positive inventory UNKNOWN')
    guards[0]['invocation_id']=next(x['invocation_id'] for x in roots['rows'] if x['id']==guards[0]['root'])
    write('GUARD-ARGUMENTS.json',{'count':1,'instances':guards,'positive_inventory':'UNKNOWN_CENSORED_NOT_EMPTY','general_support_or_admission':False})
    blocks=[]
    for row in q['rows'][4:]:
        planned=next(x for x in req['rows'] if x['id']==row['id'])
        lo,hi=row['domain']['length_interval']
        roles=[x for x in row['literal_roles'] if x['required']['class']=='assertion']
        covers=[x for x in row['literal_roles'] if x['required']['class']=='cover']
        labels=[x['required']['description'] for x in covers]
        need(len(roles)==4 and all(x['required']['status']=='SUCCESS' and not x['exact_match'] for x in roles),'four required literal roles UNKNOWN '+row['id'])
        need(len(covers)==planned['required_cover_count'] and all(x['required']['status']=='SATISFIED' and not x['exact_match'] for x in covers),'all declared covers UNKNOWN '+row['id'])
        need(all(any(label.endswith(f'_N{n:02}') for label in labels) for n in range(lo,hi+1)),'exact length cover sites '+row['id'])
        need(row['U_count']=='UNKNOWN' and row['unsupported_guards']=='UNKNOWN' and row['native_property_count']=='UNKNOWN','no empty inventory inferred from censored row '+row['id'])
        if hi<=1:
            need(len(covers)==3 and all(not any(s in label for s in ['UNSORTED','DUPLICATE','NONCONSTANT','MAX_DESCENDING']) for label in labels),'N01 structural omission only at source sites')
        else:
            need(len(covers)==6 and all(any(label.endswith(s) for label in labels) for s in ['UNSORTED','DUPLICATE','NONCONSTANT','MAX_DESCENDING','USEFUL_RETURN']),'all five feasible witnesses remain required '+row['id'])
        blocks.append({'root':row['id'],'domain':row['domain'],'four_assertion_roles':roles,'declared_covers':covers,'observed_native_SAT':'UNKNOWN_CENSORED','native_unwind_outcomes':'UNKNOWN_CENSORED','source_unwind':36,'structural_NA':'Only omitted impossible pair/max-descending source sites in N01; no exported UNSAT/UNREACHABLE acceptance' if hi<=1 else 'NONE; every site must export located SAT','assumed_summary_edges':[],'eligible':False,'admitted':False})
    need([len(x['declared_covers']) for x in blocks]==[6,6,6,3],'exact21 required covers partition6/6/6/3')
    write('LENGTH-ROLES-SAT.json',{'blocks':blocks,'required_source_assertion_sites_all8':21,'required_source_cover_sites_all8':21,'positive_native_inventories':'All4 incomplete; native role/cover/U/guard/unwind counts UNKNOWN, not source site counts','summary_provider_init_MIR_credit':'NONE'})
    phases=[]
    for row in roots['rows']:
        rid=row['id'];gp='groups/s3-'+rid+'/'
        g=data[gp+'receipt.json'];co=data[gp+'compile/receipt.json'];stock=data[gp+'export.json'];supervision=data['workers/'+rid+'-supervision.json']
        c=next(x for x in cost['rows'] if x['id']==rid)
        # Read only already authorized compact bounded previews; no raw stream recovery.
        excerpts=[]
        for stream in ['stdout','stderr']:
            for part in ['head','tail']:
                for i,line in enumerate(g.get(stream,{}).get(part,'').splitlines(),1):
                    if re.search(r'Unwinding loop|Not unwinding loop|aborting path on assume\(false\)|Finished `dev`',line):
                        excerpts.append({'pointer':'/'+stream+'/'+part,'line_in_preview':i,'text':line})
        retention={s:{k:g[s].get(k) for k in ['original_bytes','captured_bytes','capture_layout','capture_omitted_bytes','preview_omitted_bytes','sha256']} for s in ['stdout','stderr']}
        positive=row['rank']>4
        if positive:
            need(any('Unwinding loop' in x['text'] and 'insert_tail' in x['text'] for x in excerpts),'bounded tail records actual symbolic loop exploration '+rid)
            need(stock['run_state']=='INCOMPLETE' and 'harnesses' not in stock and 'wall_time_s' not in stock,'no completed verification resources or wall fields '+rid)
            need(all(v=='UNKNOWN_NOT_EXPORTED_BY_STOCK' for v in data[rid+'/receipt.json']['cost_phases'].values()),'actual perphase producer fields explicitly UNKNOWN '+rid)
        events=supervision['lifecycle_events']
        need(type(supervision['lifecycle_events_omitted']) is int and supervision['lifecycle_events_omitted']>=0,'preserve bounded lifecycle omission count '+rid)
        p={'root':rid,'group_receipt_member':gp+'receipt.json','group_receipt_member_sha256':packet['files'][gp+'receipt.json']['sha256'],'compile_member':gp+'compile/receipt.json','compile_member_sha256':packet['files'][gp+'compile/receipt.json']['sha256'],'export_member':gp+'export.json','export_member_sha256':packet['files'][gp+'export.json']['sha256'],'invocation_id':g['invocation_id'],'native_started_at':stock['started_at'],'native_start_event':g['native_start_events'],'native_start_scope':g['native_start_scope'],'compile_initial_export_upper_s':co['elapsed_upper_bound_seconds'],'compile_marker_sha256':co['marker_sha256'],'stock_configuration':stock['configuration'],'stock_tools':stock['tools'],'exported_cost_phases':data[rid+'/receipt.json']['cost_phases'],'bounded_preview_progress_excerpts':excerpts,'preview_retention':retention,'actual_last_retained_activity':'SYMBOLIC_LOOP_UNWINDING_AND_ASSUME_FALSE_MESSAGES; timestamp within tail UNKNOWN' if positive else 'COMPLETED_NATIVE_PROPERTY_INVENTORY','phase_at_exact_signal':'UNKNOWN; final buffered progress text is not a timestamped phase sample' if positive else 'NO_SIGNAL_NORMAL_COMPLETION','internal_profile_fields_absent':['symex_wall_s','solver_wall_s','solver_start_timestamp','symex_steps','VCC_count','helper_entry_timestamp','helper_return_timestamp','initialization_wall_s','oracle_wall_s'] if positive else [],'lifecycle_diagnostic_count':len(events),'lifecycle_events_omitted':supervision['lifecycle_events_omitted'],'lifecycle_diagnostic_completeness':'INCOMPLETE_BOUNDED_RETENTION; omitted event details UNKNOWN','lifecycle_classifications':dict(collections.Counter(x.get('classification','UNCLASSIFIED') for x in events)),'errno_counts':dict(collections.Counter(str(x.get('errno')) for x in events)),'original_exception':g.get('original_exception'),'execution_exception':g.get('execution_exception'),'snapshot_errors':g.get('snapshot_errors'),'semantic_helper_entry_return':'UNKNOWN_NOT_EXPORTED; native header is harness start only','causal_hotspot':'UNKNOWN','censoring':'Whole child wall600 including compilation; completion time exceeds observed budget, actual solver start/completion UNKNOWN' if positive else 'NONE'}
        phases.append(p)
        c['actual_progress_observations']=p
        c['cutoff_phase']='AFTER_INITIAL_EXPORT_AND_NATIVE_START; bounded tail symbolic unwinding; exact signal subphase UNKNOWN' if positive else 'COMPLETED'
    write('PHASE-OBSERVATIONS.json',{'rows':phases,'assurance':'Authenticated compact fields and bounded retained preview excerpts only; observations are not compiler/MIR causal proof','no_raw_stream_or_full_log_read':True,'no_phase_duration_inference':True})
    cost['network_conclusion']='ALL_FOUR child600 whole-child wall cutoffs including compilation. Compile markers <180s, sampled local RSS below observed6GiB cap; no supervisor slot/outer/global cutoff. Bounded tails record symbolic loop exploration, not complete proof or exclusive solver time.'
    cost['network_N_independence']='NOT_ESTABLISHED; four right-censored runs cannot rank or equate uncensored costs. Old two600s union contexts are incomparable.'
    write('COST.json',cost)
    prot=read('PROTECTED.json');epochs=[]
    need(prot['baseline']['errors']==[],'baseline snapshot has no observed errors')
    for e in prot['epochs']:
        life=e['lifecycle'];need(life['pre']['errors']==life['post']['errors']==[],'all-state pre/post no ignored snapshot errors '+e['id'])
        epochs.append({'root':e['id'],'context':life['context'],'E0':prot['baseline']['epoch'],'pre_epoch':life['pre']['epoch'],'post_epoch':life['post']['epoch'],'inner_after_absent':e['protected']['inner_after_absent'],'controller_recovery_used':e['protected']['controller_recovery_used'],'all_five_fingerprints_match':e['all_five_equal_E0'],'observed_errors_ignored':False,'diagnostics':'COST.json exact original supervision/lifecycle diagnostics, errno preserved'})
    write('EPOCH-AUDIT.json',{'rows':epochs,'all_state_validation':'Actual frozen provenance/protected/controller pair readers replayed for all8 including UNKNOWN','B01_B02':'All-state gates retained; B01/B02 identity diagnostics not reclassified into proof. No interrupted missing-AFTER recovery needed in this run.','canonical_paths':'Exported canonical path identities and reviewed snapshot source; independent physical inode/origin proof UNKNOWN','global_stop':False,'no_protected_snapshot_errors_ignored':True,'lifecycle_telemetry':'64 retained events per row; omitted counts preserved in PHASE-OBSERVATIONS and COST; omitted diagnostics UNKNOWN. Cleanup verified is a separate producer observation, not a complete syscall transcript.'})
    citations=[]
    specs=[('source',pins['source']['repo'],req['std_sha'],'library/core/src/slice/sort/shared/smallsort/verify/sorting_s4_network_partition.rs',[8,98,102,104,106,108,112,115]),('source',pins['source']['repo'],req['std_sha'],'library/core/src/slice/sort/shared/smallsort/verify/sorting_model.rs',[48,80,95,104,139,153]),('source',pins['source']['repo'],req['std_sha'],'library/core/src/slice/sort/shared/smallsort.rs',[332,339,358,372,665,671,709,728]),('source',pins['source']['repo'],req['std_sha'],'library/core/src/slice/sort/shared/smallsort/verify/sorting_s2_span.rs',[20,41]),('source',pins['source']['repo'],req['std_sha'],'library/core/src/slice/sort/shared/smallsort/verify/sorting_s2_swap.rs',[38,55]),('control',pins['control_reviewed']['repo'],pins['control_reviewed']['sha'],'ch8-s1-control/runner.py',[469,525,549,1093,1264]),('tool',pins['tool']['repo'],req['tool_sha'],'kani-driver/src/call_cbmc.rs',[172,215,232,267])]
    for kind,repo,rev,path,lines in specs:
        b=blob(repo,rev,path);citations.append({'kind':kind,'commit':rev,'path':path,'sha256':sha(b),'contexts':[{'line':n,'source':context(b,n)} for n in lines]})
    write('SOURCE-COST-PATH.json',{'citations':citations,'classification':'Frozen source context and candidate hypotheses only; no compiler expansion/native/MIR experiment','measured_hotspots':'UNKNOWN','hypotheses':['Path exploration may retain branches excluded by the source assume until later reasoning; bounded N01 tail contains insertion loops despite early-return source semantics. Exact mechanism not established.','Symbolic usize n/canary, dynamic slice bounds, oracle and frame loops may create intermediate verification work before simplification. No measured causal allocation.','Contract/builtin handling on the insertion path, including same_allocation assume(false) messages, is an investigation candidate; messages do not prove a bad premise, a model bug, common emitter or successful proof.'],'no_enabled_summary_edges':req['enabled_summary_edges']})
    write('QUALIFICATION-CHECKLIST.json',{'all8_requirements':[{'item':1,'assessment':'MATCH_NATIVE_TERMINAL_AND_IDENTITIES','evidence':['github-run.json','github-jobs-detail.json','github-artifacts.json','artifact-integrity.json','DEPENDENCIES.json','PROVENANCE.json']},{'item':2,'assessment':'ALL8_STARTED_ORDERED_FRESH_ORIGINAL_NULL_SEALED; PREFIX8; NO_GLOBALSTOP','evidence':['ROOTS.json','SERIAL-ORDER.json','PREFIX.json','PROTECTED.json','EPOCH-AUDIT.json']},{'item':3,'assessment':'FOUR_EXACT_LABELLED_NATIVE_FAILURES; STRICT_PRODUCER_FALSE','evidence':['QUALIFICATION.json','NATIVE-PROPERTIES.json','U-ARGUMENTS.json','GUARD-ARGUMENTS.json']},{'item':4,'assessment':'SOURCE21ASSERT21COVER; FOUR_POSITIVE_NATIVE_INVENTORIES_INCOMPLETE_UNKNOWN','evidence':['LENGTH-ROLES-SAT.json','SOURCE-GATES.json']},{'item':5,'assessment':'NATIVE_VS_PRODUCER_VS_S1_VS_ADMISSION_SEPARATE;18U_ARGUMENTS;1SUCCESSGUARD;NO_CREDIT','evidence':['QUALIFICATION.json','U-ARGUMENTS.json','GUARD-ARGUMENTS.json']},{'item':6,'assessment':'NO_LOCATION_GAP_IN139_COMPLETE_NEGATIVE_PROPERTIES;4POSITIVE_INVENTORIES_UNKNOWN;NO_NEW_PROPOSAL_OR_WAIVER','evidence':['METADATA-GAP.json','LOCATION-PROPOSAL.json']},{'item':7,'assessment':'ALL8_COST_ACCOUNTED;4WHOLECHILD600_WALL;COMPILE180_RSS_SLOT_GLOBAL_NOT_TRIGGERED;PHASE_TIMINGS_UNKNOWN','evidence':['COST.json','PHASE-OBSERVATIONS.json','N01-COST-PATH.md']},{'item':8,'assessment':'EXACT_FROZEN_READERS_LOCAL_UPLOAD_REPLAY_AND_TARGETED_ADVERSES;NO_ADMISSION','evidence':['VALIDATION.json','AUDIT-VALIDATION.json','PROVENANCE.json']}],'qualified_new_leaves':0,'independent_B1_B2_credit':'NONE','next':'Root verifies exact committed READY then separately issues intake-bound offline plan; intake grants no implementation or run'})
    write('AUDIT-VALIDATION.json',{'status':'PASS','checks_count':len(checks),'checks':checks,'scope':'Dependency manifests, actual native checkout, guard retention, role/cover omissions, all-state epochs, bounded preview observations and source-only diagnosis','native_rerun':False,'full_Validate_or_host_suite':False,'policy_changed':False})
    print(json.dumps({'audit':'PASS','checks':len(checks),'rows':len(phases),'guards':len(guards),'complete_native_properties':139,'positive_inventory':'UNKNOWN'}))
if __name__=='__main__':main()
