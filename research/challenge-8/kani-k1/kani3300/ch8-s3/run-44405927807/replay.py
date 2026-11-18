#!/usr/bin/env python3
"""Bounded offline intake using frozen readers and authenticated compact members.

Adapted from ch8-s2/run-44375519132/replay.py. No compiler, runner main,
native process, CI, historical evidence write, or candidate repair is invoked.
"""
import ast, base64, copy, csv, gzip, hashlib, importlib, io, json, subprocess, sys, tempfile
from pathlib import Path
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
BASE = HERE.parent
CONTROL = Path('/root/kani-ch8-s3-1-r1-control-w13')
CTRL = 'fc29b93b1e333b73e55e2872701c80d9927f3b02'
HEAD = 'd92581141b86e0f3b695cb37acc15c265478c9b4'
TASK = 'f4c2a494bb6a00f4174fb957b1e2d08feabea07d'
RID = 'checker_order_corrupt'
GP = 'groups/s3-'+RID+'/'
checks = []
def sha(b): return hashlib.sha256(b).hexdigest()
def write(n,v): (HERE/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def read(n): return json.loads((HERE/n).read_bytes())
def need(ok,label):
    if not ok: raise AssertionError(label)
    checks.append(label)
def git(repo,*args): return subprocess.check_output(['git','-C',str(repo),*args])
def blob(repo,commit,path): return git(repo,'show',commit+':'+path)
def project(d,keys): return {k:d[k] for k in keys if k in d}
def main():
    pins=json.loads((BASE/'before-snapshot-postrun/INPUTS.json').read_bytes())
    old=json.loads((BASE/'postrun-s3-1/INPUTS.json').read_bytes())
    pins.update(status='EXECUTED_OWNER0106_NEW11',task_g0=TASK,task='TASK-CH8-S3-1-BEFORE-INTAKE-W11.md',
                inherited_intake='6967b2db974efff371efbbf45a7eeb0c1b065666',settings='high / Fast OFF preserved; no setting change',
                prior_intake_pins=old)
    write('INPUTS.json',pins)
    run=read('github-run.json');jobs=read('github-jobs.json')['jobs'];arts=read('github-artifacts.json')['artifacts']
    need((run['id'],run['run_attempt'],run['event'],run['status'],run['conclusion'])==(44405927807,1,'push','completed','failure'),'native terminal identity')
    need(run['head_sha']==HEAD and run['head_branch']==pins['branch'],'native ref/head')
    need(len(arts)==1 and arts[0]['id']==pins['artifact']['id'] and arts[0]['name']==pins['artifact']['name'] and not arts[0]['expired'],'one authorized artifact metadata')
    integ=read('artifact-integrity.json')
    need(arts[0]['digest']==pins['artifact']['archive_digest']=='sha256:'+integ['sha256'] and arts[0]['size_in_bytes']==integ['bytes']==60016 and integ['digest_checked_before_zip_open'] and not integ['transport_saved'],'transport digest first; no saved ZIP')
    need(arts[0]['workflow_run']['head_sha']==HEAD and arts[0]['workflow_run']['id']==44405927807,'artifact/run binding')
    need(len(jobs)==1 and jobs[0]['head_sha']==HEAD and jobs[0]['run_attempt']==1 and jobs[0]['conclusion']=='failure','job binding')
    trees={commit:git(CONTROL,'rev-parse',commit+'^{tree}').decode().strip() for commit in (CTRL,HEAD)}
    need(len(set(trees.values()))==1 and trees[CTRL]==old['trigger']['tree'],'executed/reviewed exact tree')
    for commit in (CTRL,HEAD): need(git(CONTROL,'show','-s','--format=%P',commit).decode().strip()==old['trigger']['sole_parent'],'same sole parent '+commit)
    request_raw=blob(CONTROL,CTRL,'ch8-s1-control/CI-REQUEST.json');req=json.loads(request_raw)
    need(sha(request_raw)==old['request_sha256'] and request_raw==blob(CONTROL,HEAD,'ch8-s1-control/CI-REQUEST.json'),'request exact bytes')
    workflow=blob(CONTROL,CTRL,'.github/workflows/ch8-s2.yml')
    need(sha(workflow)==old['workflow_sha256'] and workflow==blob(CONTROL,HEAD,'.github/workflows/ch8-s2.yml'),'workflow exact bytes')
    payloads={}
    for path,h in req['ci_payload_sha256'].items():
        data=blob(CONTROL,CTRL,path)
        need(sha(data)==h and data==blob(CONTROL,HEAD,path),'executed/reviewed payload '+path)
        payloads[path]={'sha256':h,'bytes':len(data)}
    source=Path(old['source']['worktree'])
    for kind,repo in [('source',source),('tool',CONTROL)]:
        need(git(repo,'rev-parse',old[kind]['sha']+'^{tree}').decode().strip()==old[kind]['tree'],'pinned '+kind+' tree')
    for key in ['changed_file_sha256','cfg_pfc_source_sha256','contract_stack_source_sha256','lexical_source_sha256','ordinary_contract_source_sha256']:
        for path,h in req[key].items():need(sha(blob(source,pins['source'],path))==h,'source '+key+' '+path)
    gz=(HERE/'group-evidence.json.gz').read_bytes();raw=gzip.decompress(gz)
    need(sha(gz)==integ['payload_sha256'] and sha(raw)==integ['uncompressed_sha256'] and len(raw)<=32*1024*1024,'compact payload integrity/bound')
    packet=json.loads(raw);need(packet['state']=='PACKAGED' and packet['error'] is None,'compact packaged without error')
    data={};members={}
    for name,entry in packet['files'].items():
        rel=Path(name);need(not rel.is_absolute() and '..' not in rel.parts and rel.suffix=='.json','structured member boundary '+name)
        b=entry['text'].encode() if entry.get('encoding','utf-8')=='utf-8' else base64.b64decode(entry['text'],validate=True)
        need(len(b)==entry['bytes'] and sha(b)==entry['sha256'],'member digest '+name)
        data[name]=json.loads(b);members[name]=b
    need(len(data)==36,'36 structured members')
    g=data[GP+'receipt.json'];base=data['baseline.json'];life=data['workers/'+RID+'-lifecycle.json'];sup=data['workers/'+RID+'-supervision.json'];top=data['receipt.json']
    need(data['campaign-start.json']['request_data']==req and top['request_sha256']==sha(request_raw),'compact frozen request')
    observed={'E0':('baseline.json','/binaries',base['binaries']),
              'E1.pre':('workers/'+RID+'-lifecycle.json','/pre/binaries',life['pre']['binaries']),
              'worker.BEFORE':(GP+'receipt.json','/tool_fingerprints_before',g['tool_fingerprints_before']),
              'worker.AFTER':(GP+'receipt.json','/tool_fingerprints_after',g['tool_fingerprints_after']),
              'E1.post':('workers/'+RID+'-lifecycle.json','/post/binaries',life['post']['binaries'])}
    observations={};comparisons=[]
    missing=['size','resolved_realpath','symlink','mtime','inode','existence_stat','device']
    for label,(name,pointer,snap) in observed.items():
        observations[label]={'member':name,'member_sha256':sha(members[name]),'pointer':pointer,'value':snap,
                            'unknown_not_recorded':missing,'error_field_presence':'PRESENT' if 'error' in snap else 'MISSING',
                            'reported_versions_presence':'PRESENT_NULL' if snap.get('reported_versions','MISSING') is None else 'OTHER'}
    for name in ('kani_driver','kani_compiler','cbmc'):
        b=base['binaries']['binaries'][name];w=g['tool_fingerprints_before']['binaries'][name]
        fields=sorted(set(b)|set(w));diff=[{'field':k,'expected_present':k in b,'actual_present':k in w,'expected':b.get(k),'actual':w.get(k)} for k in fields if b.get(k)!=w.get(k) or (k in b)!=(k in w)]
        comparisons.append({'binary':name,'expected':b,'actual':w,'sha256_equal':b['sha256']==w['sha256'],'path_equal':b['path']==w['path'],'entry_equal':b==w,'differing_fields':diff,'unknown_not_recorded':missing})
    need([x['binary'] for x in comparisons if not x['entry_equal']]==['kani_driver','kani_compiler'] and all(x['sha256_equal'] for x in comparisons),'only driver/compiler path strings differ; all three recorded hashes match')
    need(all(x['differing_fields']==[] or [y['field'] for y in x['differing_fields']]==['path'] for x in comparisons),'exact differing field path')
    # Freeze import closure in a temporary directory. Imported code is never modified.
    names={Path(x).stem for x in git(CONTROL,'ls-tree','-r','--name-only',CTRL,'ch8-s1-control').decode().splitlines() if x.endswith('.py')}
    frozen={};todo=['collect','s3_campaign']
    with tempfile.TemporaryDirectory(prefix='s3-before-intake-') as tmp:
        temp=Path(tmp);scripts=temp/'reader';scripts.mkdir()
        while todo:
            name=todo.pop()
            if name in frozen:continue
            b=blob(CONTROL,CTRL,'ch8-s1-control/'+name+'.py');frozen[name]=b;(scripts/(name+'.py')).write_bytes(b)
            for node in ast.walk(ast.parse(b)):
                deps=[x.name.split('.')[0] for x in node.names] if isinstance(node,ast.Import) else [node.module.split('.')[0]] if isinstance(node,ast.ImportFrom) and node.module else []
                todo.extend(x for x in deps if x in names and x not in frozen)
        (scripts/'CI-REQUEST.json').write_bytes(request_raw);sys.path.insert(0,str(scripts))
        r=importlib.import_module('runner');c=importlib.import_module('s3_campaign');ev=importlib.import_module('s3_evidence');collector=importlib.import_module('collect')
        need(r.load_request()==req,'frozen request reader')
        local=temp/'local';upload=temp/'upload';local.mkdir();upload.mkdir()
        for name,b in members.items():p=local/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
        (upload/'group-evidence.json.gz').write_bytes(gz)
        need(c.snapshots.validate_pair(base,life['pre'],life['post'],life['context']),'authentic E0/pre/post pair passes frozen guard')
        matrix={a:{b:r.fingerprints_match(x[2],y[2]) for b,y in observed.items()} for a,x in observed.items()}
        try:c.root_outcome(local,req,RID,sup)
        except c.GlobalFailure as exc: local_error=str(exc)
        else:raise AssertionError('authentic BEFORE unexpectedly accepted')
        need(local_error=='worker protected/provenance evidence rejected: recorded worker binary drift: before','authentic frozen local rejection reproduced')
        def guarded(doc):
            try:return {'accepted_by_protected':True,'return':ev.protected(doc,req,base,sup,sha(request_raw))}
            except ev.EvidenceError as exc:return {'accepted_by_protected':False,'error':str(exc)}
        original=guarded(g)
        aligned=copy.deepcopy(g)
        # Counterfactual isolation only: two path strings per stage, no hash changes.
        for stage in ('before','after'):
            for name in ('kani_driver','kani_compiler'):
                aligned['tool_fingerprints_'+stage]['binaries'][name]['path']=base['binaries']['binaries'][name]['path']
        aligned_result=guarded(aligned);drift=copy.deepcopy(aligned)
        h=drift['tool_fingerprints_before']['binaries']['kani_driver']['sha256'];drift['tool_fingerprints_before']['binaries']['kani_driver']['sha256']=('0' if h[0]!='0' else '1')+h[1:]
        drift_result=guarded(drift);absent=copy.deepcopy(aligned);del absent['tool_fingerprints_before'];absent_result=guarded(absent)
        need(not original['accepted_by_protected'] and aligned_result['accepted_by_protected'] and not drift_result['accepted_by_protected'] and not absent_result['accepted_by_protected'],'diagnostic isolation and true recorded-hash drift/missing controls')
        need(r.fingerprints_match(g['tool_fingerprints_before'],g['tool_fingerprints_after']),'worker internal before/after MATCH independently replayed')
        need(ev.provenance(g,data[GP+'compile/receipt.json'],req,RID,sha(request_raw)),'authentic request-derived source/tool provenance independently passes')
        need(g['argv']==r.build_argv(Path('/home/runner/work/kani/kani/export'),Path('/home/runner/work/kani/kani/tool'),[g['selectors'][0]],34,Path('/home/runner/work/_temp/ch8-s1-receipts')/(GP+'export.json')),'authentic singleton argv')
        left=c.collect([local],req);right=c.collect([upload],req)
        need(left==right,'exact collector local/upload-only equality')
        need(left['global_stop'] and left['state']=='GLOBAL_STOPPED_PENDING_REVIEW' and not c.sealed(local),'empty completed prefix remains global STOP')
        need(all((local/n).read_bytes()==b for n,b in members.items()),'reader replay did not change authentic evidence')
        replay={'control':CTRL,'local_root_outcome_error':local_error,'protected_original':original,
                'diagnostic_counterfactual_paths_only':aligned_result,'recorded_hash_drift_control':drift_result,'missing_before_control':absent_result,
                'counterfactual_is_not_repair_or_identity_proof':True,'local_upload_equal':True,'completed_prefix':[],
                'collector_state':left['state'],'global_stop':left['global_stop'],'selected_missing_groups':left['selected_missing_groups'],
                'global_stops':left['global_stops'],'rows':[{k:x[k] for k in ('id','status','outcome','reason') if k in x} for x in left['rows']],
                'portable_scope':'No sealed roots; collector preserves STOP and worker observations. The unsealed worker is diagnosed by direct protected/root_outcome replay, not admitted by collect.'}
    write('PREFIX-REPLAY.json',replay)
    diff={'schema':'s3-before-comparison-v1','control':CTRL,'cause':'PATH_STRING_REPRESENTATION_MISMATCH_WITH_EQUAL_RECORDED_HASHES',
          'failing_expression':"fingerprints_match(baseline['binaries'],doc['tool_fingerprints_before']) -> before['binaries'] == after['binaries']",
          'failing_key':'binaries.{kani_driver,kani_compiler}.path','order_note':'dict equality returns false; guard does not report a first binary. Both mismatched entries are enumerated here.',
          'comparisons':comparisons,'observations':observations,'match_matrix':matrix,
          'unknowns':{'physical_identity':'UNKNOWN: no recorded realpath/readlink/stat/device/inode/size/mtime; equal recorded hashes do not bind a filesystem object.',
                      'setup_build_fingerprints':'NOT_RECORDED: setup receipt has execution metrics, no binary snapshots. E0 is first available post-build fingerprint.',
                      'byte_change':'NO_RECORDED_HASH_CHANGE across all five observations; unobserved intermediate changes UNKNOWN.',
                      'worker_snapshot_epoch':'before/after phase fields recorded; separate worker capture timestamp/epoch MISSING.',
                      'installer_rebuild_symlink_cause':'UNKNOWN_NOT_NEEDED_FOR_REPRODUCED_READER_REJECTION'}}
    write('BEFORE-DIFF.json',diff)
    exp=data[GP+'export.json'];h=exp['harnesses'][0];rich=data[GP+'properties.json'];rh=rich['harnesses'][0]
    native={'source_reported_only':True,'campaign_row':project(data[RID+'/receipt.json'],['id','status','outcome','native_root_start','original_exit','signal','reason','proof_credit']),
            'worker_group_state':g['state'],'worker_exit':sup['worker_exit'],'driver_exit':g['execution']['original_exit_code'],
            'native_start_events':g['native_start_events'],'native_start_scope':g['native_start_scope'],
            'export':project(exp,['run_state','outcome','started_at','wall_time_s','harness_selection','tools','summary']),
            'harness':project(h,['name','file','line','outcome','resolved_unwind','resolved_solver','resources','n_properties','n_failed','failure_kind','failed_properties','checks','covers']),
            'rich_state':rich['state'],'rich_failed_or_unreachable':[x for x in rh['properties'] if x['status'] in ('FAILURE','UNREACHABLE')],
            'admission':'NOT_ACCEPTED: no seal; STOP; reject-ALL-U unchanged; eight UNREACHABLE checks retained',
            'coordinator_report_reconciliation':'NONE native verdicts is superseded by authenticated compact export FAILURE. Zero completed campaign roots remains accurate.'}
    write('NATIVE.json',native)
    rows=[]
    for rank,rid in enumerate(req['s3']['selected'],1):
        row=next(x for x in req['rows'] if x['id']==rid);actual=data[rid+'/receipt.json']
        rows.append({'id':rid,'selected':True,'rank':rank,'mode':row['mode'],'assurance':row['assurance'],'selector':row['selector'],'unwind':row['unwind'],
            'campaign_status':actual['status'],'campaign_outcome':actual['outcome'],'sealed':False,
            'worker_launched':rid==RID,'native_start':'OBSERVED_STOCK_HEADER' if rid==RID else 'NOT_RUN',
            'native_verdict':'FAILURE_SOURCE_REPORTED' if rid==RID else 'NOT_RUN','accepted':False,'proof_credit':'NONE'})
    for rid in req['s3']['deferred']:rows.append({'id':rid,'selected':False,'campaign_status':'NOT_SELECTED','worker_launched':False,'native_verdict':'NOT_SELECTED','accepted':False,'proof_credit':'NONE'})
    write('ROOTS.json',rows)
    with (HERE/'ROOTS.csv').open('w',newline='') as f:
        fields=list(dict.fromkeys(k for row in rows for k in row));w=csv.DictWriter(f,fields,lineterminator='\n');w.writeheader();w.writerows(rows)
    compile_doc=data[GP+'compile/receipt.json'];setup=data['setup/receipt.json']
    cost={'native_job_steps':jobs[0]['steps'],'setup_build':project(setup,['elapsed_seconds','setup_total_seconds','original_exit_code','signal','timed_out','rss_peak_kib','rss_status','rss_sample_period_seconds','child_shutdown_verified']),
          'campaign_phase_elapsed_seconds':top['phase_elapsed_seconds'],
          'first_root':{'id':RID,'compile':project(compile_doc,['state','boundary','scope','elapsed_upper_bound_seconds','observed_run_state','limit_seconds','marker_sha256']),
                        'driver_execution':project(g['execution'],['elapsed_seconds','original_exit_code','signal','timed_out','child_shutdown_verified','rss_peak_kib','rss_scope','rss_sample_period_seconds','component_group_peak_kib','component_rss_scope']),
                        'worker_supervision':project(sup,['elapsed_seconds','monotonic_start','monotonic_end','worker_exit','cutoff','outer_sampled_peak_kib','outer_rss_scope','worker_wall_limit_seconds','limit_initiated','supervisor_error','orphan_survivors_at_worker_exit']),
                        'cleanup':project(sup['containment'],['verified','scope','elapsed_seconds','signals','reaped_adopted','worker_exit']),
                        'native_verification_time_s':h['resources']['verification_time_s'],'native_export_wall_time_s':exp['wall_time_s'],
                        'symex_time_s':'UNKNOWN_NOT_EXPORTED','backend_phase_time_s':'UNKNOWN_NOT_EXPORTED','symex_steps':'UNKNOWN_NOT_EXPORTED','VCC':'UNKNOWN_NOT_EXPORTED','true_peak_rss':'UNKNOWN_NOT_MEASURED'},
          'other_selected':[{'id':rid,'status':'NOT_RUN','compile_time':'NOT_RUN','verification_time':'NOT_RUN'} for rid in req['s3']['selected'][1:]],
          'limits':req['s3']['caps'],'interpretation':'phase elapsed includes controller and worker. Compile marker is an upper bound, not precise compiler time; verification excludes compilation. RSS is sampled PGID/owned-process scope, not true kernel/tree peak. No matched historical timing pair established.'}
    write('COST.json',cost)
    chronology={'campaign_start':data['campaign-start.json']['start_monotonic'],'E0':base['monotonic'],'launch':data['workers/'+RID+'-launch.json']['monotonic'],
                'E1.pre':life['pre']['monotonic'],'worker_start':sup['monotonic_start'],'native_start_events':g['native_start_events'],'worker_end':sup['monotonic_end'],'E1.post':life['post']['monotonic']}
    write('PROVENANCE.json',{'control_tree':trees,'payloads':payloads,'request_sha256':sha(request_raw),'workflow_sha256':sha(workflow),
          'temporary_frozen_reader_modules':{k:sha(v) for k,v in frozen.items()},'chronology':chronology,
          'protected_source':{'expected':g['source_before'],'worker_before_equals_after':g['source_before']==g['source_after'],
               'controller_source_all_equal':base['source']==life['pre']['source']==life['post']['source']==g['source_before'],
               'controller_control_all_equal':base['control']==life['pre']['control']==life['post']['control'],'actual_control':base['control'],
               'request_derived_provenance_pass':True,'source_under_test':g['source_under_test']},
          'invocation':project(g,['invocation_id','argv','selectors','unwind','effective_cfg','cargo_target_dir','timeout_seconds','compile_limit_seconds','variant']),
          'provenance_limit':'source-reported structured identities/binding, no independent compiler-origin/proof binding credit',
          'setup_fingerprints':'MISSING_NOT_NULL; no build binary inventory emitted by check_package.build',
          'metadata_exception':{'tool':'github_fetch','url':'https://api.github.com/repos/Tiramisu-Cake/kani/actions/jobs/135160999072','error_code':'INVALID_ARGUMENT','reason':'endpoint unsupported; succeeded via /actions/runs/44405927807/jobs, metadata only'}})
    spans={'runner.py':[(902,965),(1096,1107),(1152,1159)],
           's3_evidence.py':[(20,58)],'s3_snapshots.py':[(9,24)],
           's3_campaign.py':[(171,191),(258,263),(265,299),(319,326),(359,365)],
           'test_s3.py':[(40,49),(197,208),(343,347),(371,372),(420,426)],
           'test_s3_repair.py':[(78,101),(105,121)],'check_package.py':[(163,177)]}
    trace=[]
    for name,ranges in spans.items():
        path='ch8-s1-control/'+name;b=blob(CONTROL,CTRL,path);lines=b.decode().splitlines()
        for start,end in ranges:trace.append({'commit':CTRL,'path':path,'file_sha256':sha(b),'start_line':start,'end_line':end,'lines':lines[start-1:end]})
    precursor='1dfc267b66abd83d536eb41a17052a4f3d767d2b'
    old_runner=blob(CONTROL,precursor,'ch8-s1-control/runner.py')
    def function_bytes(b,name):
        node=next(x for x in ast.parse(b).body if isinstance(x,ast.FunctionDef) and x.name==name)
        return ast.get_source_segment(b.decode(),node)
    for name in ('binary_fingerprints','snapshot_binaries','fingerprints_match'):
        need(function_bytes(old_runner,name)==function_bytes(frozen['runner'],name),'unchanged precursor/final function '+name)
    old_campaign=blob(CONTROL,precursor,'ch8-s1-control/s3_campaign.py')
    trace.append({'commit':precursor,'path':'ch8-s1-control/s3_campaign.py','file_sha256':sha(old_campaign),'start_line':171,'end_line':198,'lines':old_campaign.decode().splitlines()[170:198]})
    trace.append({'commit':CTRL,'path':'.github/workflows/ch8-s2.yml','file_sha256':sha(workflow),'start_line':89,'end_line':106,'lines':workflow.decode().splitlines()[88:106]})
    write('SOURCE-TRACE.json',{'assurance':'EXACT_PINNED_SOURCE_SPANS; static code is not runtime proof','spans':trace,'unchanged_functions':['binary_fingerprints','snapshot_binaries','fingerprints_match']})
    result={'schema':'s3-before-intake-result-v1','task_g0':TASK,'run':44405927807,'status':'READY_EXACT_READER_CAUSE_WITH_BOUNDED_PHYSICAL_IDENTITY_UNKNOWNS',
            'cause':diff['cause'],'failed_fields':['kani_driver.path','kani_compiler.path'],'all_recorded_binary_sha256_equal':True,
            'authentic_rejection_reproduced':True,'native_job':'completed/failure','campaign_state':'STOPPED','sealed_roots':0,
            'selected_launched':1,'selected_not_run':8,'deferred_not_selected':8,'native_first_verdict':'FAILURE_SOURCE_REPORTED_S2_NEG_CHECKER_ORDER',
            'qualification':0,'closed_obligations':0,'independent_B1_B2_credit':'NONE','proposal':'NOT_APPLIED',
            'budget_reference':pins['budget'],'accounting_note':'case-specific coordinator charge0 retained; no blanket refund rule or accounting recomputation from new native observation',
            'next':'root reviews committed intake -> original13 localized repair/regression -> same14 delta -> newGO; no automatic rerun',
            'constraints':'No source/control/test edits, compiler/native runner/CI/push/ledger/subagents/model/settings changes; only owned intake outputs'}
    write('RESULT.json',result)
    write('VALIDATION.json',{'status':'PASS','checks_count':len(checks),'checks':checks,'reader_controls':replay,'verification_scope':'offline pure-reader/root-finalizer rejection and compact collector only; no native execution'})
    print(json.dumps({'status':result['status'],'checks':len(checks),'native_first_verdict':result['native_first_verdict'],'failed_fields':result['failed_fields'],'replay':replay['collector_state']}))
if __name__=='__main__':main()
