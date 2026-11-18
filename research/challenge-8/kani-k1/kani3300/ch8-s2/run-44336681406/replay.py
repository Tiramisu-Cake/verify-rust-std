#!/usr/bin/env python3
"""Offline intake: Git object reads and exact collector/oracle replay only."""
import ast,base64,gzip,hashlib,importlib,json,re,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
G0=HERE.parents[5]
CONTROL=Path('/root/kani-ch8-s2-r4-r2-final-w13')
STD=Path('/root/verify-rust-std-ch8-s2-r4-r1-w13')
CTRL='d33a0900da19d865f20ccaa76e1ee27065c5a671'
HEAD='6157554df88fa810496fa6ba10a16a8acc805687'
SOURCE='bd62e54df1b4749154790aa3db3cc7978f547f75'
TOOL='0aac16ef62da9e9d5645782d458593e5d78143ba'
GID='s2-batch3probes-u34'
BATCH='library/core/src/slice/sort/shared/smallsort/verify/sorting_s2_batch.rs'
U='UNKNOWN'
checks=[]
def need(ok,msg):
 if not ok: raise ValueError(msg)
 checks.append(msg)
def sha(b): return hashlib.sha256(b).hexdigest()
def read(n): return json.loads((HERE/n).read_bytes())
def write(n,v): (HERE/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def git(repo,*args): return subprocess.check_output(['git','-C',str(repo),*args])
def blob(repo,commit,path): return git(repo,'show',commit+':'+path)
def clean(v):
 if isinstance(v,dict): return {k:clean(x) for k,x in v.items() if k not in ('stdout','stderr')}
 if isinstance(v,list): return [clean(x) for x in v]
 return v
def compact():
 integrity=read('artifact-integrity.json')
 gz=(HERE/'group-evidence.json.gz').read_bytes()
 need(len(gz)==integrity['payload_bytes'] and sha(gz)==integrity['payload_sha256'],'retained compact digest')
 need(len(gz)<=8*1024*1024,'compressed cap')
 with gzip.open(HERE/'group-evidence.json.gz','rb') as f: raw=f.read(32*1024*1024+1)
 need(len(raw)<=32*1024*1024 and sha(raw)==integrity['uncompressed_sha256'],'decompression cap and hash')
 doc=json.loads(raw); d={}; b={}
 need(doc['schema']=='ch8-s1-05-artifact-v1' and doc['state']=='PACKAGED' and doc['error'] is None,'packaging complete only')
 for n,e in doc['files'].items():
  need(not Path(n).is_absolute() and '..' not in Path(n).parts and n.endswith('.json'),'structured namespace '+n)
  raw=e['text'].encode() if e.get('encoding','utf-8')=='utf-8' else base64.b64decode(e['text'],validate=True)
  need(len(raw)==e['bytes'] and sha(raw)==e['sha256'],'embedded hash '+n)
  b[n]=raw;d[n]=json.loads(raw)
 need(d==read('embedded-projection.json'),'bounded projection exact')
 return doc,d,b
def excerpt(repo,commit,path,ranges):
 raw=blob(repo,commit,path); lines=raw.decode().splitlines()
 return {'commit':commit,'path':path,'file_sha256':sha(raw),'ranges':[{'first':lo,'last':hi,'text':'\n'.join(f'{i}: {lines[i-1]}' for i in range(lo,min(hi,len(lines))+1))} for lo,hi in ranges]}
def main():
 pins=json.loads((HERE.parent/'postrun-r4-r2/INPUTS.json').read_bytes())
 write('INPUTS.json',pins)
 run=read('github-run.json');arts=read('github-artifacts.json')['artifacts'];jobs=read('github-jobs.json')['jobs']
 need(run['id']==44336681406 and run['run_attempt']==1 and run['event']=='push' and run['status']=='completed' and run['conclusion']=='failure','connected terminal run failure/push/attempt1')
 need(run['head_sha']==HEAD and run['head_branch']==pins['run']['branch'] and run['head_commit']['tree_id']==pins['run']['tree'],'connected trigger/ref/tree')
 need(len(arts)==1 and arts[0]['name']==pins['artifact']['name'] and arts[0]['id']==14443915305 and not arts[0]['expired'],'sole allowed compact artifact')
 need(arts[0]['digest']=='sha256:'+read('artifact-integrity.json')['sha256'] and arts[0]['size_in_bytes']==read('artifact-integrity.json')['bytes'],'connected transport digest/size')
 need(arts[0]['workflow_run']['id']==run['id'] and arts[0]['workflow_run']['head_sha']==HEAD and arts[0]['workflow_run']['head_branch']==run['head_branch'],'artifact workflow identity')
 need(len(jobs)==1 and jobs[0]['run_id']==run['id'] and jobs[0]['run_attempt']==1 and jobs[0]['head_sha']==HEAD and jobs[0]['conclusion']=='failure','connected job identity')
 need(git(CONTROL,'rev-parse',HEAD+'^{tree}').decode().strip()==pins['run']['tree']==git(CONTROL,'rev-parse',CTRL+'^{tree}').decode().strip(),'trigger equals reviewed control tree')
 need(git(CONTROL,'show','-s','--format=%P',HEAD).decode().strip()==pins['run']['parent'],'trigger sole parent')
 for repo,commit,tree in [(STD,SOURCE,pins['source']['tree']),(CONTROL,TOOL,pins['tool']['tree'])]:
  need(git(repo,'rev-parse',commit+'^{tree}').decode().strip()==tree,'exact tree '+commit)
 need(git(STD,'show','-s','--format=%P',SOURCE).decode().strip()==pins['source']['parent'],'source sole parent')
 need(git(CONTROL,'show','-s','--format=%P',CTRL).decode().strip()==pins['run']['parent'],'reviewed control sole parent')
 request_raw=blob(CONTROL,HEAD,'ch8-s1-control/CI-REQUEST.json');request=json.loads(request_raw)
 need(sha(request_raw)==pins['request']['sha256'],'executed request hash')
 need(request_raw==blob(CONTROL,CTRL,'ch8-s1-control/CI-REQUEST.json'),'reviewed/executed request bytes')
 payloads={}
 for p,h in request['ci_payload_sha256'].items():
  raw=blob(CONTROL,HEAD,p)
  need(sha(raw)==h and raw==blob(CONTROL,CTRL,p),'reviewed/executed payload '+p)
  payloads[p]={'sha256':h,'bytes':len(raw)}
 source_hashes={}
 for mapping in [request['changed_file_sha256'],pins['request']['cfg_pfc_source_sha256'],pins['request']['contract_stack_source_sha256'],pins['request']['lexical_source_sha256']]:
  for p,h in mapping.items():
   need(sha(blob(STD,SOURCE,p))==h,'pinned source '+p);source_hashes[p]=h
 # Copy only the exact collector's local import closure, plus existing oracle.
 replay=HERE/'replay-control';replay.mkdir(exist_ok=True)
 todo=['collect','negative_oracle','oracle_source'];done=set()
 names={Path(p).stem for p in request['ci_payload_sha256'] if p.startswith('ch8-s1-control/') and p.endswith('.py')}
 while todo:
  name=todo.pop()
  if name in done: continue
  done.add(name);raw=blob(CONTROL,HEAD,'ch8-s1-control/'+name+'.py')
  (replay/(name+'.py')).write_bytes(raw)
  tree=ast.parse(raw)
  for node in ast.walk(tree):
   deps=[x.name.split('.')[0] for x in node.names] if isinstance(node,ast.Import) else [node.module.split('.')[0]] if isinstance(node,ast.ImportFrom) and node.module else []
   todo.extend(n for n in deps if n in names and n not in done)
 (replay/'CI-REQUEST.json').write_bytes(request_raw)
 sys.path.insert(0,str(replay));r=importlib.import_module('runner');collector=importlib.import_module('collect');neg=importlib.import_module('negative_oracle');osrc=importlib.import_module('oracle_source')
 need(r.load_request()==request,'exact read-only request validator')
 doc,d,b=compact();p='groups/'+GID+'/'
 group,comp,stock,rich,meta,terminal=(d[x] for x in (p+'receipt.json',p+'compile/receipt.json',p+'export.json',p+'properties.json',p+'binding-metadata.json','receipt.json'))
 expected={k:request[k] for k in ('std_sha','std_tree','tool_sha','tool_tree','changed_file_sha256')}
 need(group['source_before']==group['source_after']==meta['source_before']==meta['source_after']==expected,'same-invocation source snapshots')
 need(all(v['request_sha256']==sha(request_raw) for v in [group,comp,meta,terminal]),'receipt request bindings')
 need(group['source_under_test']['file_sha256']==request['changed_file_sha256'] and group['source_under_test']['patch_sha256'] is None and group['variant']=='production','production source no variant')
 need(group['binary_identity']=='MATCH' and r.fingerprints_match(group['tool_fingerprints_before'],group['tool_fingerprints_after']) and not group['snapshot_errors'],'protected binary before/after match')
 need(group['execution']['child_shutdown_verified'] is True,'child shutdown precedes protected after snapshot')
 need(meta['binaries_before']==group['tool_fingerprints_before'] and meta['binaries_after']==group['tool_fingerprints_after'] and meta['invocation_id']==group['invocation_id'],'metadata binaries and fresh invocation')
 need(len(b[p+'binding-metadata.json'])==group['binding_metadata']['bytes'] and sha(b[p+'binding-metadata.json'])==group['binding_metadata']['sha256'],'binding metadata digest')
 selectors=[x['selector'] for x in request['rows']]
 need(group['selectors']==selectors==stock['harness_selection']['requested_filters'] and stock['harness_selection']['matched_count']==11 and stock['harness_selection']['exact'] and not stock['harness_selection']['unmatched_filters'],'all 11 exact selected filters')
 need(meta['argv']==group['argv'] and meta['effective_cfg']==group['effective_cfg']==request['flags']['RUSTFLAGS'],'actual argv/cfg')
 argv=r.build_argv(Path('/home/runner/work/kani/kani/export'),Path('/home/runner/work/kani/kani/tool'),selectors,34,Path('/home/runner/work/_temp/ch8-s1-receipts/groups/'+GID+'/export.json'))
 need(argv==group['argv'] and '--jobs=1' in argv and argv[argv.index('--harness-timeout')+1]=='600s','exact producer argv serial1/backend600')
 need(sha(json.dumps({'flags':request['flags'],'cfg':group['effective_cfg'],'argv':argv},sort_keys=True).encode())==meta['configuration_sha256'],'configuration digest')
 for e in meta['artifacts']:
  raw=b[p+e['path']];need(len(raw)==e['bytes'] and sha(raw)==e['sha256'],'metadata artifact digest '+e['path'])
 native=[];native_man=[];native_refs=[]
 for entry in meta['native_metadata']:
  raw=entry['text'].encode()
  need(entry['state']=='CAPTURED' and len(raw)==entry['bytes'] and sha(raw)==entry['sha256'],'native metadata '+entry['path'])
  o=json.loads(raw);native_man.append({k:v for k,v in entry.items() if k!='text'})
  native.extend(o.get('proof_harnesses',[]))
  for key in ['proof_harnesses','test_harnesses']:
   for index,harness in enumerate(o.get(key,[])):
    native_refs.append({'metadata_path':entry['path'],'pointer':'/'+key+'/'+str(index),'name':harness['pretty_name'],'crate':harness['crate_name']})
 need(len(meta['native_metadata'])==23 and sum(x['bytes'] for x in native_man)==184322,'native metadata 23 files/184322 bytes')
 need(len(native)==11 and {x['pretty_name'] for x in native}==set(selectors),'fresh native compilation inventory exactly11')
 need(all(h['crate_name']=='core' and group['invocation_id'] in h['goto_file'] for h in native),'native core/fresh target namespace')
 need(all(h['original_file']=='/home/runner/work/kani/kani/export/'+BATCH for h in native),'one actual root file')
 need(meta['source_under_test']==group['source_under_test'],'metadata source variant binding')
 need(len(meta['rows'])==11,'metadata row count')
 for row,declared in zip(meta['rows'],request['rows']):
  need((row['row_id'],row['harness'],row['crate'],row['mode'],row['group_id'],row['variant'])==(declared['id'],declared['selector'],'core',declared['mode'],GID,'production'),'metadata row identity '+declared['id'])
  matches=[x for x in native_refs if x['name']==row['harness'] and x['crate']==row['crate']]
  need(len(matches)==1 and row['native_harness_records']==matches,'native exact selector/crate pointer '+declared['id'])
 sort=sorted(native,key=lambda h:(h['original_file'],-h['original_start_line']))
 need(sort[0]['pretty_name']==selectors[-1] and sort[0]['original_start_line']==160,'stock source-line scheduler puts general32_weak first')
 need(comp['state']=='COMPLETE' and comp['boundary']=='STOCK_INITIAL_EXPORT_OBSERVED' and comp['elapsed_upper_bound_seconds']==35.5,'compile complete boundary upper bound35.5s')
 need(comp['marker_sha256']==sha(b[p+'export.json']) and stock['run_state']=='INCOMPLETE' and 'harnesses' not in stock,'initial marker retained; no terminal stock inventory')
 need(group['state']=='FAILED' and terminal['state']=='STOPPED' and group['execution']['termination_reason']=='rss_cap' and not group['execution']['timed_out'],'RSS interruption not backend timeout')
 need(rich['state']=='INCOMPLETE' and rich['error']=='missing regular harness RESULTS' and rich['harnesses']==[{'name':selectors[-1],'properties':[]}],'first root start only; no RESULTS')
 need(rich['observed_stdout_bytes']==group['execution']['stdout_bytes'] and not group['execution']['output_truncated'],'streaming parser received all observed stdout within cap')
 need(group['execution']['stdout_bytes']<r.STDOUT_CAP_BYTES and group['execution']['stderr_bytes']<r.STDERR_CAP_BYTES,'no output cap trigger')
 need(not any(k in group['execution'] for k in ['runner_exception','diagnostic_errors','cleanup_errors']),'no reader/runner/cleanup exception recorded')
 need(all(d[p+'rustc-'+s+'-receipt.json']['pipe_eof'] and d[p+'rustc-'+s+'-receipt.json']['incomplete_reasons']==['rss_cap'] for s in ['stdout','stderr']),'both pipes EOF; no reader failure reason')
 # Pinned collector intentionally preserves UNKNOWN for a failed group.
 collected=collector.collect([HERE],request);write('collected.json',collected)
 need(len(collected['rows'])==11 and not collected['missing_groups'] and all(x['outcome']=='UNKNOWN' for x in collected['rows']),'exact collector all11 UNKNOWN; no missing group')
 batch=blob(STD,SOURCE,BATCH).decode();source_lines=batch.splitlines()
 oracles=[]
 for row in request['rows']:
  binding=request['source_bindings'][row['id']]
  need(meta['source_bindings'][row['id']]==binding,'source binding '+row['id'])
  for loc in binding['locations']:need(source_lines[loc['line']-1].strip()==loc['source'].strip(),'source coordinate '+row['id']+':'+str(loc['line']))
  oracle=row.get('oracle')
  if oracle:
   need(source_lines[oracle['line']-1]==oracle['source_line'] and sha(batch.encode())==oracle['source_sha256'],'negative oracle source '+row['id'])
   osrc.assertion_at(batch,oracle['line'])
   need(not neg.matches(None,oracle),'missing final negative inventory rejected '+row['id'])
  messages=row['required_success_messages']+row['required_cover_messages']+([row['failure_description']] if row['failure_description'] else [])
  sites={}
  for msg in messages:
   hits=[{'line':i,'source':s} for i,s in enumerate(source_lines,1) if '"'+msg+'"' in s]
   need(len(hits)==1,'unique expected source tag '+msg);sites[msg]=hits[0]
  oracles.append({'id':row['id'],'expected':row['expected'],'required_success_messages':row['required_success_messages'],'required_cover_messages':row['required_cover_messages'],'failure_description':row['failure_description'],'oracle':oracle,'source_sites':sites,'observed_final_properties':None,'binding_status':'SOURCE_EXPECTATIONS_MATCH; NATIVE_PROPERTY_BINDING_UNKNOWN','outcome':'UNKNOWN'})
 need(sum(len(x['required_cover_messages']) for x in oracles)==20,'all20 required covers mapped')
 write('ORACLE-BINDINGS.json',oracles)
 tail=group['stdout']['tail']
 metrics={}
 for key,pattern in [('symex_s',r'Runtime Symex: ([0-9.]+)s'),('steps',r'size of program expression: (\d+) steps'),('sliced_assignments',r'slicing removed (\d+) assignments'),('vcc_generated',r'Generated (\d+) VCC'),('vcc_simplified',r'VCC\(s\), (\d+) remaining after simplification'),('postprocess_equation_s',r'Runtime Postprocess Equation: ([0-9.]+)s')]:
  match=re.search(pattern,tail);need(match is not None,'bounded tail metric '+key)
  metrics[key]=float(match[1]) if key.endswith('_s') else int(match[1])
 need(metrics=={'symex_s':488.498,'steps':4175569,'sliced_assignments':2842455,'vcc_generated':376543,'vcc_simplified':155645,'postprocess_equation_s':25.0517},'exact observed native progress metrics')
 need('sorting_s2_batch::general32_weak thread 0' in tail,'tail attribution to first caller-copy root')
 write('NATIVE-INVENTORY.json',{'members':native_man,'harnesses_in_compilation_metadata_order':native,'stock_terminal_harness_inventory':None,'rich':rich,'not_proof_credit':True})
 order={'request_order':[x['id'] for x in request['rows']],'native_compilation_order':[h['pretty_name'].split('::')[-1] for h in native],'stock_scheduled_order':[{'id':h['pretty_name'].split('::')[-1],'line':h['original_start_line'],'file':h['original_file']} for h in sort],'observed_started':['general32_weak'],'remaining_not_started':[h['pretty_name'].split('::')[-1] for h in sort[1:]],'basis':'Exact stock file ASC/line DESC sort plus one-worker pool; full observed-stream parser records only general32_weak and no final RESULTS; interrupted before next callback','future_order_guarantee':'Do not depend on request JSON/selector order or HashMap codegen/export order; more workers can change scheduling. Stock-internal future ordering beyond first unobserved.'}
 write('ORDER.json',order)
 execution=group['execution'];memory=group['memory']
 rows=[]
 for expected_row in request['rows']:
  rid=expected_row['id']
  rows.append({'id':rid,'role':'primary_probe' if rid in ['merge32_real','sort13_assumed','general32_assumed'] else 'qualification' if rid=='swap_pfc' else 'witness' if rid=='summary_witness' else 'negative_control','expected':expected_row['expected'],'execution_status':'STARTED_INTERRUPTED_RSS' if rid=='general32_weak' else 'NOT_STARTED','execution_basis':'STREAM_MARKER_AND_SOURCE_SCHEDULER' if rid=='general32_weak' else 'SERIAL_FIRST_ROOT_STILL_INCOMPLETE_AND_FULL_OBSERVED_STREAM_START_INVENTORY','native_outcome':None,'outcome':'UNKNOWN','verification_time_s':None,'verification_time_status':'MISSING_TERMINAL_EXPORT','root_wall_s':None,'root_timeout_s':600,'timeout_observed':False,'censoring':'RSS_INTERRUPTED_BEFORE_FINAL_VERDICT' if rid=='general32_weak' else 'UNSTARTED_UNMEASURED_NOT_ZERO','required_covers':expected_row['required_cover_messages'],'per_root_rss_kib':None,'progress':metrics if rid=='general32_weak' else None})
 cost={'run':44336681406,'compile':{'state':'COMPLETE','elapsed_upper_bound_seconds':35.5,'exact_compile_wall_s':None,'native_cargo_finished_profile_s':30.49,'scope':comp['scope'],'marker_sha256':comp['marker_sha256'],'not_additive_to_group':True},'observed_progress':{'general32_weak':metrics,'scope':'Native CBMC-reported runtime/counts from bounded shared stdout tail, attributed via active first root; clock implementation not independently audited','symex_completed':True,'postprocess_equation_completed':True,'solver_phase_s':None,'solver_phase_completion':'UNKNOWN','root_total_elapsed_s':None,'verification_time_s':None,'unmeasured_gaps':'UNKNOWN; no subtraction-based phase estimates'},'group':{'elapsed_seconds':execution['elapsed_seconds'],'phase_elapsed_seconds':terminal['phase_elapsed_seconds'],'execution':execution,'memory':memory,'rss_peak_scope':'MAXIMUM_OF_SAMPLED_SUM_OF_VmRSS_FOR_SAME_PGID; NOT_VIRTUAL_MEMORY; NOT_TRUE_PEAK; NOT_EXACT_ROOT','rss_peak_GiB':execution['rss_peak_kib']/1048576,'component_group_peak_GiB':{k:v/1048576 for k,v in execution['component_group_peak_kib'].items()},'components_scope':execution['component_rss_scope'],'per_root_6GiB_target_measurement':None,'monitor_trigger':'_group_rss_kib(proc.pid) > memory[group_cap_kib]','kill_path':'Popen start_new_session=True => PGID=child PID. _kill_group(SIGTERM,5s grace) then SIGKILL if live; finally wait/reap/readers/snapshot. Actual parent exit -15/SIGTERM; individual descendant signals/escalation UNKNOWN. Numeric PGID not exported. No kernel-OOM claim.'},'setup':d['setup/receipt.json'],'github_steps':jobs[0]['steps'],'job_wall_s':981,'rows':rows,'prior_runs':'No prior evidence splice/cost speedup inference; historical compilefail or validation zero charges are coordinator-specific references only. Real setup/CI cost preserved.','accounting_reference_only':{'ledger':'943d67bd487ea3ab33e5e77a0d0dfe8453a83532','source':'Owner/task/coordinator report, not independently replayed or edited','item1':'29/29','item2':'10/14','total':'39/43','boundary':'First root/backend executed; this is not confirmed pre-root compile failure; no refund inferred from missing RESULTS.'}}
 write('COST.json',cost)
 diagnostics={k:v for k,v in d.items() if Path(k).name.startswith('rustc-')}
 previews={s:group[s] for s in ['stdout','stderr']}
 need(sha((previews['stderr']['head']+previews['stderr']['tail']).encode())==previews['stderr']['sha256'],'complete inline stderr capture hash replay')
 windows={}
 for s,x in previews.items():
  windows[s]={'head_original_byte_range':[0,len(x['head'].encode())],'tail_original_byte_range':[x['original_bytes']-len(x['tail'].encode()),x['original_bytes']],'coordinate_basis':'Reconstructed from exact runner HEAD_THEN_TAIL layout, byte counts, and ASCII preview text; half-open original pipe bytes','head_sha256':sha(x['head'].encode()),'tail_sha256':sha(x['tail'].encode()),'capture_sha256_scope':'PRODUCER_HASH_OF_STORED_CAPTURE; NOT_FULL_ORIGINAL_PIPE_IF_CAPTURE_OMITTED','capture_hash_replay':'VERIFIED_INLINE' if s=='stderr' else 'UNKNOWN_65536_BYTE_CAPTURE_NOT_FULLY_INLINE'}
 write('DIAGNOSTICS.json',{'streams':diagnostics,'artifact_retention':doc['diagnostic_retention'],'group_summary':group['rustc_diagnostics'],'setup_summary':d['setup/receipt.json']['rustc_diagnostics'],'scope':'Shared group captures; no per-root attribution. Original byte coordinates/hashes for retained blocks only; blocks are empty. Group completeness false/rss_cap; producer unknown even where stream capture complete.','bounded_previews':previews,'preview_windows':windows})
 trace=[
  excerpt(CONTROL,TOOL,'kani-driver/src/main.rs',[(149,156),(186,198),(219,222)]),
  excerpt(CONTROL,TOOL,'kani-driver/src/metadata.rs',[(91,127),(155,169)]),
  excerpt(CONTROL,TOOL,'kani-driver/src/harness_runner.rs',[(58,89),(113,163),(249,280)]),
  excerpt(CONTROL,TOOL,'kani-driver/src/args/mod.rs',[(433,461)]),
  excerpt(CONTROL,TOOL,'kani-driver/src/frontend/schema_utils.rs',[(54,87)]),
  excerpt(CONTROL,TOOL,'kani-compiler/src/kani_middle/codegen_units.rs',[(82,99),(223,233),(244,294)]),
  excerpt(CONTROL,TOOL,'kani-driver/src/call_cbmc.rs',[(170,245)]),
  excerpt(STD,SOURCE,BATCH,[(27,88),(98,175)])]
 write('SOURCE-TRACE.json',trace)
 provenance={'entry_g0':'33d6df20ddc2276439be3aae5862104c976edc2a','frozen_base_g0':'e462f0e327801eecee9598a6f5f8af4d9279992d','trigger':pins['run'],'source':pins['source'],'tool':pins['tool'],'request_sha256':sha(request_raw),'reviewed_control':CTRL,'package_g0':pins['package_g0'],'review_g0':pins['package_review_g0'],'GO_g0':pins['GO_request_g0'],'review_assurance':'Inherited committed APPROVE/CLOSED R14-01/02/03 verified as exact report and payload references; not a new review or proof','source_files_verified':source_hashes,'payloads_verified':payloads,'invocation_id':group['invocation_id'],'configuration_sha256':meta['configuration_sha256'],'native_identity_limits':{'compilation_id':meta['compilation_id'],'compiler_identity_status':meta['compiler_identity_status'],'rows':meta['rows']},'binary_snapshots':{'before':group['tool_fingerprints_before'],'after':group['tool_fingerprints_after']},'no_external_mutation':True,'no_subagents':True,'Fast':'OFF_PRESERVED_NOT_TOGGLED','settings':'PRESERVED','transport_file_ref':'file_000000007c1c8211a8db2039cd20929f','transport_zip_saved':False}
 review_path='research/challenge-8/kani-k1/kani3300/ch8-s2/review-batch-r4-r2/REPORT.md'
 review=git(G0,'show',pins['package_review_g0']+':'+review_path)
 need(b'**APPROVE.**' in review and CTRL.encode() in review,'exact combined review report APPROVE')
 provenance['review_report_sha256']=sha(review)
 write('PROVENANCE.json',provenance)
 result={'state':'READY_INTAKE_PARTIAL_PROOF_EVIDENCE','run':44336681406,'attempt':1,'terminal':'FAILURE','artifact_integrity':'VERIFIED_ALLOWED_COMPACT_ONLY','packaging':'PACKAGED','compile':'COMPLETE_UPPER_BOUND35.5S','stock_terminal_export':'INCOMPLETE_INITIAL_MARKER_ONLY','rich':'INCOMPLETE_ONE_STARTED_ROOT_NO_RESULTS','diagnostic_retention':'INCOMPLETE_RSS_CAP','native_compilation_harness_inventory':'11_EXACT_SELECTED; NOT_VERDICT_INVENTORY','rows':rows,'closed_proof_obligations':0,'proof_credit':'NONE','B1':'NOT_ESTABLISHED','B2':'NOT_ESTABLISHED','admission':'NOT_GRANTED','qualification':'NOT_GRANTED','negative_detections':0,'successful_roots':0,'required_covers_observed_satisfied':None,'remaining_unknown':['final outcomes/assertions/covers for all11','exact root wall and verification_time_s','solver progress/time/completion','root RSS and 6GiB target','true peak and per-process signals/numeric PGID','compiler-instance/MIR/type/contract/property-origin binding','historical R3 unit/cause and r1 diagnostics'],'limits':['general32_weak tests a source-bound caller copy with weak merge seam; cannot detect control without final property inventory','sort13/general32 remain DIAGNOSTIC_ASSUMED; sort8 registration only, unproved/unselected','swap PFC separate admission; merge domain exact u8/32/sorted halves/allocation only','nonvacuity/witness/controls/qualification remain separate UNKNOWN claims','native compile now observed, supports repair without uniquely establishing old failure cause']}
 write('RESULT.json',result)
 write('VALIDATION.json',{'state':'PASS_READ_ONLY_INTAKE_CHECKS','checks':checks,'count':len(checks),'collector':'EXACT_EXECUTED_BYTES_REPLAYED;11_UNKNOWN','compiler_or_CI_invocations':0,'source_control_ledger_mutations':0,'validation_scope':'Integrity, identity, expected source tags/coordinates, inventories, scheduler/kill-path tracing and exact collector. No proof acceptance.'})
 print(json.dumps({'validation':'PASS','checks':len(checks),'first':'general32_weak','outcomes':'11 UNKNOWN','compile_upper_bound_s':35.5,'metrics':metrics,'group_s':execution['elapsed_seconds']}))
if __name__=='__main__': main()
