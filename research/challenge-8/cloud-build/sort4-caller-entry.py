#!/usr/bin/env python3
"""Cloud-only native mutable-slice caller prefix / c1 entry entailment diagnostic."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, os, re, subprocess, sys, time
from pathlib import Path


def sha(p: Path) -> str: return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p: Path, x): p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(x, indent=2, sort_keys=True)+'\n')
def need(b, why):
    if not b: raise RuntimeError(why)
def load_module(p, name):
    spec=importlib.util.spec_from_file_location(name,p); m=importlib.util.module_from_spec(spec); sys.modules[name]=m; spec.loader.exec_module(m); return m

def mir_basic_blocks(record):
    """Read top-level basic block slices from a complete captured Cap'n Proto record."""
    marker='basicBlocks = ['
    at=record.find(marker)
    if at<0 or record.find(marker,at+len(marker))>=0:return None
    open_at=at+len(marker)-1
    close_at=matching_bracket(record,open_at)
    if close_at is None:return None
    tail=record[open_at+1:close_at]
    starts=list(re.finditer(r'(?m)^\s*\( id = \(index = (\d+)\),',tail))
    if not starts:return None
    blocks=[]
    for i,m in enumerate(starts):
        end=starts[i+1].start() if i+1<len(starts) else len(tail)
        blocks.append((int(m.group(1)),tail[m.start():end]))
    if [n for n,_ in blocks]!=list(range(len(blocks))):return None
    return blocks

def matching_bracket(text, opening):
    if opening<0 or opening>=len(text) or text[opening]!='[':return None
    depth=0; quoted=False; escaped=False
    for i in range(opening,len(text)):
        ch=text[i]
        if quoted:
            if escaped:escaped=False
            elif ch=='\\':escaped=True
            elif ch=='"':quoted=False
        elif ch=='"':quoted=True
        elif ch=='[':depth+=1
        elif ch==']':
            depth-=1
            if depth==0:return i
    return None

def mir_ghost_statement(record, line, marker_text):
    """Find a MIR ghostStmts raw item spanning a source marker line."""
    fields=list(re.finditer(r'(?m)^\s*ghostStmts = \[',record))
    if len(fields)!=1 or not isinstance(line,int):return None
    opening=record.find('[',fields[0].start())
    closing=matching_bracket(record,opening)
    if closing is None:return None
    section=record[opening+1:closing]
    starts=list(re.finditer(r'(?m)^\s*\( raw = "',section))
    matches=[]
    for i,m in enumerate(starts):
        end=starts[i+1].start() if i+1<len(starts) else len(section)
        item=section[m.start():end]
        start_match=re.search(r'\bstartLine = (\d+),',item)
        end_match=re.search(r'\bendLine = (\d+),',item)
        if not start_match or not end_match:continue
        lo,hi=int(start_match.group(1)),int(end_match.group(1))
        if lo<=line<=hi and marker_text in item:
            matches.append({'index':i,'start_line':lo,'end_line':hi})
    return matches if matches else None

def mir_line_blocks(blocks, line):
    if blocks is None or not isinstance(line,int):return None
    hits=[]
    for block_id,block in blocks:
        if re.search(r'\bline = '+str(line)+r',',block):hits.append(block_id)
    return hits or None

def executed_line(log, line):
    if not isinstance(line,int):return False
    return re.search(r'^\s*\d+(?:\.\d+)?s: verified/lib\.rs\('+str(line)+r',[^\n]*\): Executing statement\s*$',log,re.M) is not None

def source_line(lines, line):
    return lines[line-1] if isinstance(line,int) and 1<=line<=len(lines) else None

def resource_evidence(root):
    p=root/'verification-resources.txt'
    if not p.is_file():return {'status':'NOT_CONFIRMED','path':str(p)}
    data=p.read_bytes(); text=data.decode(errors='replace')
    fields={}
    for label,pattern in (
        ('elapsed_wall_seconds',r'Elapsed \(wall clock\) time \(h:mm:ss or m:ss\): ([^\n]+)'),
        ('maximum_resident_set_kb',r'Maximum resident set size \(kbytes\): (\d+)'),
        ('user_seconds',r'User time \(seconds\): ([^\n]+)'),
        ('system_seconds',r'System time \(seconds\): ([^\n]+)'),
    ):
        m=re.search(pattern,text); fields[label]=m.group(1).strip() if m else None
    return {'status':'CAPTURED','path':str(p),'sha256':hashlib.sha256(data).hexdigest(),**fields}

def caller_mapping(root, fixture, cert, normal_record, readonly_record, log, entry):
    """Bind selected source lines to complete MIR blocks and trace locations.

    The last edge is a verifier execution-trace location, not a complete proof
    AST dump. Missing or ambiguous mappings stay NOT_CONFIRMED.
    """
    targets=cert.get('targeted_ghost_statement_lines',{})
    if not isinstance(targets,dict):targets={}
    filter_line=targets.get('scratch_success_path_filter')
    original_line=targets.get('original_scratch_len_plus_16_check')
    boundary_line=targets.get('first_sort4_callsite_boundary')
    source=(fixture/'verified/lib.rs').read_text(errors='replace').splitlines()
    actual_path=fixture/'actual-caller.rs'
    actual=actual_path.read_text(errors='replace').splitlines() if actual_path.is_file() else []
    caller_cert=cert.get('source_certificate',{})
    if not isinstance(caller_cert,dict):caller_cert={}
    actual_sha=hashlib.sha256(actual_path.read_bytes()).hexdigest() if actual_path.is_file() else None
    source_cert=cert.get('source_mapped_condition_bytes',{})
    if not isinstance(source_cert,dict):source_cert={}
    expected=source_cert.get('scratch_success_filter_condition')
    expected=expected.strip() if isinstance(expected,str) else None
    filter_text=source_line(source,filter_line)
    original_text=source_line(source,original_line)
    boundary_text=source_line(source,boundary_line)
    line_targets_ok=all(type(line) is int for line in (filter_line,original_line,boundary_line))
    source_ok=(expected is not None and line_targets_ok and filter_line<original_line and
               filter_text is not None and original_text is not None and
               filter_text.strip()==expected and original_text.strip()==expected and
               source_line(source,filter_line+1) is not None and source_line(source,filter_line+1).strip()=='return;' and
               'FIRST_SORT4_CALLSITE_BOUNDARY' in (boundary_text or '') and
               caller_cert.get('caller_runtime_source_exact') is True and
               actual_sha==caller_cert.get('full_original_caller_sha256') and
               sum(1 for line in actual if line.strip()==expected)==1 and
               source_cert.get('scratch_success_filter_matches_original_condition') is True and
               source_cert.get('original_abort_check_retained_verbatim') is True)
    pointer_lines={}
    for name,needle in (('v_as_mut_ptr','let v_base = v.as_mut_ptr();'),
                        ('scratch_as_mut_ptr','let scratch_base = scratch.as_mut_ptr() as *mut T;')):
        hits=[i+1 for i,text in enumerate(source) if needle in text]
        pointer_lines[name]=hits[0] if len(hits)==1 else None
    abort_hits=[i+1 for i,text in enumerate(source) if 'intrinsics::abort();' in text]
    abort_line=abort_hits[0] if len(abort_hits)==1 else None
    source_ok=bool(source_ok and isinstance(original_line,int) and abort_line==original_line+1 and
                   source_line(source,abort_line)=='        intrinsics::abort();')
    order_ok=(source_ok and pointer_lines['v_as_mut_ptr'] is not None and
              pointer_lines['scratch_as_mut_ptr'] is not None and
              original_line<pointer_lines['v_as_mut_ptr']<pointer_lines['scratch_as_mut_ptr'])
    modes={}
    for mode,record in (('normal',normal_record),('readonly',readonly_record)):
        blocks=mir_basic_blocks(record)
        mapped={
            'scratch_success_path_filter':mir_line_blocks(blocks,filter_line),
            'original_scratch_len_plus_16_check':mir_line_blocks(blocks,original_line),
            'v_as_mut_ptr':mir_line_blocks(blocks,pointer_lines['v_as_mut_ptr']),
            'scratch_as_mut_ptr':mir_line_blocks(blocks,pointer_lines['scratch_as_mut_ptr']),
            'original_abort_statement':mir_line_blocks(blocks,abort_line),
        }
        boundary_ghost=mir_ghost_statement(record,boundary_line,'FIRST_SORT4_CALLSITE_BOUNDARY')
        abort_target_blocks=[block_id for block_id,block in (blocks or [])
                             if 'name = "std::intrinsics::abort"' in block]
        abort_target_linked=bool(abort_target_blocks and mapped['original_abort_statement'] and
                                 set(abort_target_blocks).intersection(mapped['original_abort_statement']))
        mir_complete=blocks is not None and all(mapped[k] for k in (
            'scratch_success_path_filter','original_scratch_len_plus_16_check',
            'v_as_mut_ptr','scratch_as_mut_ptr')) and boundary_ghost is not None
        modes[mode]={
            'status':'PASS' if source_ok and order_ok and mir_complete and abort_target_linked else 'NOT_CONFIRMED',
            'full_function_record_sha256':hashlib.sha256(record.encode()).hexdigest() if record else None,
            'complete_basic_block_inventory':len(blocks) if blocks is not None else None,
            'source_line_to_basic_blocks':mapped,
            'callsite_boundary_mir_ghost_statement':boundary_ghost,
            'abort_target_blocks':abort_target_blocks,
            'abort_target_linked_to_original_abort_span':abort_target_linked,
            'source_ordered_lines_all_present_in_mir':bool(order_ok and mir_complete),
            'control_flow_precedence_proved':False,
        }
    trace={
        'scratch_success_path_filter':executed_line(log,filter_line),
        'original_scratch_len_plus_16_check':executed_line(log,original_line),
        'first_sort4_callsite_boundary':executed_line(log,boundary_line),
        'original_abort_statement_executed':executed_line(log,abort_line),
    }
    trace_ok=all(trace[k] for k in ('scratch_success_path_filter',
                                    'original_scratch_len_plus_16_check',
                                    'first_sort4_callsite_boundary')) and not trace['original_abort_statement_executed']
    return {
        'status':'PASS' if source_ok and order_ok and all(m['status']=='PASS' for m in modes.values()) and trace_ok else 'NOT_CONFIRMED',
        'source':{
            'status':'PASS' if source_ok and order_ok else 'NOT_CONFIRMED',
            'scratch_filter_line':filter_line,'scratch_filter_text':filter_text,
            'original_check_line':original_line,'original_check_text':original_text,
            'condition_text_equal':bool(source_ok),'boundary_marker_line':boundary_line,
            'boundary_marker_text':boundary_text,'pointer_operation_lines':pointer_lines,
            'actual_caller_sha256':actual_sha,
            'actual_caller_sha_matches_certificate':actual_sha==caller_cert.get('full_original_caller_sha256'),
            'source_order_places_guards_before_pointer_operations':bool(order_ok),
            'original_abort_line':abort_line,
        },
        'mir':modes,
        'proof_execution_trace':{
            'status':'PASS' if trace_ok else 'NOT_CONFIRMED',
            'statement_hits':trace,
            'evidence_kind':'verifier execution trace locations; no complete proof AST dump claimed',
        },
        'proof_entry_log_offset':entry,
        'verification_resources':resource_evidence(fixture),
    }

def snapshot(a):
    root=a.production_source
    paths=['src/verifast.ml','src/rust_frontend/vf_mir_translator/vf_mir_translator.ml','src/rust_frontend/vf_mir_translator/rust_parser.ml','src/rust_frontend/vf_mir/vf_mir.capnp','bin/verifast','bin/vf-rust-mir-exporter','bin/refinement-checker']
    return {'critical':{p:sha(root/p) for p in paths},'effective_rsspec':{str(p.relative_to(root)):sha(p) for p in sorted((root/'bin/rust').rglob('*.rsspec'))},'base_commit':subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip(),'production_applied_patch_sha256':sha(a.production_applied_patch),'proof_sha':os.environ['PROOF_SHA'],'infra_sha':os.environ['INFRA_SHA'],'new_semantic_patch':False,'c1_overlay_active':False,'profile_accepted':False}

def stage(a, root, name, argv, env, cap, stdin=None, stdout=None):
    seconds=min(cap,a.deadline_epoch-int(time.time())-15)
    status={'name':name,'state':'RUNNING','argv':argv,'started_epoch':int(time.time()),'proof_verdict':None}
    write(root/(name+'-stage.json'),status); write(a.evidence/'stage-progress.json',{'case':root.name,**status})
    if seconds<=0:
        status.update(state='NOT_RUN',exit=None,reason='deadline/evidence reserve'); write(root/(name+'-stage.json'),status); return status
    output=root/(stdout or name+'.log'); errors=root/(name+'-stderr.log') if stdout else output
    with output.open('wb') as out:
        err=errors.open('wb') if errors!=output else subprocess.STDOUT
        inp=(root/stdin).open('rb') if stdin else open(os.devnull,'rb')
        try:
            code=subprocess.run(['/usr/bin/time','-v','-o',str(root/(name+'-resources.txt')),'timeout','--signal=TERM','--kill-after=10s',str(seconds)+'s',*argv],cwd=root,env=env,stdin=inp,stdout=out,stderr=err,check=False).returncode
        finally:
            inp.close()
            if errors!=output: err.close()
    status.update(state='TERMINAL',exit=code,finished_epoch=int(time.time()),stdout=output.name,stderr=errors.name,stdout_sha256=sha(output),stderr_sha256=sha(errors))
    (root/(name+'-exit-code.txt')).write_text(str(code)+'\n');write(root/(name+'-stage.json'),status);write(a.evidence/'stage-progress.json',{'case':root.name,**status})
    if stdout is None: print(output.read_text(errors='replace'),flush=True)
    return status

def run_case(a, prep, capture, parser, case, env):
    root=a.evidence/'cases'/case
    root.mkdir(parents=True)
    result={'case':case,'classification':'NOT_RUN_PREPARE','accepted':False,'bridge_premises_derived':False}
    write(root/'case-result.json',result)
    try:
        fixture=root/'fixture'; cert=prep.prepare(a.proof_root,fixture,case)
        write(root/'source-certificate.json',cert)
        before={name:sha(fixture/name) for name in ('original/lib.rs','verified/lib.rs')}
        write(root/'raw-input-pins.json',{'proof_sha':os.environ['PROOF_SHA'],'source_hashes':before,'source_linked_fragment_only':True,'caller_full_body_proved':False,'sort4_summary_used':False})
        exporter=str(a.production_source/'bin/vf-rust-mir-exporter'); vf=str(a.production_source/'bin/verifast'); refiner=str(a.production_source/'bin/refinement-checker'); schema=a.production_source/'src/rust_frontend/vf_mir/vf_mir.capnp'
        rows={}; records={}
        for mode in ('normal','readonly'):
            argv=[exporter,'verified/lib.rs','--sysroot='+str(a.compiler_sysroot),'--edition','2021']
            if mode=='readonly': argv.append('--vf-rust-mir-exporter:preprocess-readonly')
            rows[mode+'-export']=stage(a,fixture,mode+'-export',argv,env,100,stdout=mode+'-mir.bin')
            if rows[mode+'-export']['exit']==0:
                rows[mode+'-decode']=stage(a,fixture,mode+'-decode',['capnp','decode',str(schema),'VfMir'],env,60,stdin=mode+'-mir.bin',stdout=mode+'-mir.txt')
                if rows[mode+'-decode']['exit']==0:
                    defpath,record=capture.complete_function_record((fixture/(mode+'-mir.txt')).read_text(),'small_sort_general_with_scratch')
                    records[mode]=record
                    (root/(mode+'-full-prefix-mir.txt')).write_text(record)
                    write(root/(mode+'-graph.json'),{'def_path':defpath,'full_record_sha256':sha(root/(mode+'-full-prefix-mir.txt')),'full_record_bytes':len(record.encode()),'complete_fields':['inputs','localDecls','basicBlocks'],'source_linked_prefix_only':True,'actual_full_caller':False,'no_comparator_or_copy':not ('FnMut::call_mut' in record or 'copy_nonoverlapping' in record),'call_targets':re.findall(r'fnDef = \(\s*id = \(\s*name = "([^"]+)"',record)})
        rows['refinement']=stage(a,fixture,'refinement',[refiner,'--rustc-args','--edition 2021','original/lib.rs','verified/lib.rs'],env,120)
        gates=all(rows.get(name,{}).get('exit')==0 for name in ('normal-export','normal-decode','readonly-export','readonly-decode','refinement')) and all(sha(fixture/n)==h for n,h in before.items())
        write(root/'admission-gates.json',{'gates_passed':gates,'source_pair_immutable':all(sha(fixture/n)==h for n,h in before.items()),'fragment_only':True,'all_support_exits':{n:r.get('exit') for n,r in rows.items()},'skipped_prerequisites':False})
        # Diagnostic verifier invocation is an independent admission probe if support failed.
        # It cannot receive resource proof credit unless every gate passed.
        rows['verification']=stage(a,fixture,'verification',[vf,'-rustc_args','--edition 2021','-verbose','2','verified/lib.rs'],env,240)
        log=(fixture/'verification.log').read_text(errors='replace') if (fixture/'verification.log').exists() else ''
        errors=[line for line in log.splitlines() if ': error:' in line or line.startswith('Fatal error:')]
        entries=parser.proof_entries(log,'small_sort_general_with_scratch')
        helpers=parser.proof_entries(log,'c1_entry_identity')
        caller_ok=len(entries)==1
        helper_ok=(case!='bridge-positive') or (len(helpers)==1 and caller_ok and helpers[0]<entries[0] and 'Leak check.' in log[helpers[0]:entries[0]] and ': error:' not in log[helpers[0]:entries[0]])
        identity_line=cert.get('targeted_ghost_statement_lines',{}).get('positive_identity_lemma')
        identity_reached=(case!='bridge-positive') or (caller_ok and identity_line is not None and re.search(r'^\s*\d+\.\d+s: verified/lib\.rs\('+str(identity_line)+r',[^\n]*\): Executing ',log[entries[0]:],re.M) is not None)
        subset_line=cert.get('targeted_ghost_statement_lines',{}).get('source_subset_four')
        subset_reached=(case!='source-frame-positive') or (caller_ok and subset_line is not None and re.search(r'^\s*\d+\.\d+s: verified/lib\.rs\('+str(subset_line)+r',[^\n]*\): Executing ',log[entries[0]:],re.M) is not None)
        caller_log=log[entries[0]:] if caller_ok else ''
        mapping=caller_mapping(root,fixture,cert,records.get('normal',''),records.get('readonly',''),caller_log,entries[0] if caller_ok else None)
        mapping_passed=mapping['status']=='PASS'
        gates=gates and mapping_passed
        write(root/'admission-gates.json',{
            'gates_passed':gates,
            'source_pair_immutable':all(sha(fixture/n)==h for n,h in before.items()),
            'fragment_only':True,
            'all_support_exits':{n:r.get('exit') for n,r in rows.items()},
            'source_mir_proof_mapping_status':mapping['status'],
            'source_mir_proof_mapping':mapping,
            'skipped_prerequisites':False,
        })
        leak_seen=caller_ok and 'Leak check.' in caller_log
        complete=(gates and caller_ok and helper_ok and identity_reached and subset_reached and leak_seen and rows['verification'].get('exit')==0 and not errors and re.search(r'0 errors found \(\d+ statements verified\)',log) is not None)
        intended=False
        if gates and caller_ok and len(errors)==1 and rows['verification'].get('exit')==1 and entries[0]<log.index(errors[0]):
            if case=='range-negative': intended=('Cannot prove condition' in errors[0] and 'array_split' in log[entries[0]:] and 'len + 1' in log[log.index(errors[0]):])
            if case=='duplicate-negative': intended=('No matching heap chunks: array<T>' in errors[0] and 'DUPLICATE_AUTHORITY_CONTROL' in log[log.index(errors[0]):])
        first=errors[0] if errors else next((line for line in log.splitlines() if line.startswith('error[') or line.startswith('error:')),None)
        first_location=re.match(r'verified/lib\.rs\((\d+),',first or '')
        prefix_blocker=(gates and caller_ok and first_location is not None and int(first_location.group(1)) < cert['targeted_ghost_statement_lines']['source_sort8_condition'])
        observed={name:[n for n in numbers if caller_ok and re.search(r'^\s*\d+\.\d+s: verified/lib\.rs\('+str(n)+r',[^\n]*\): Executing ',log[entries[0]:],re.M)] for name,numbers in cert.get('targeted_ghost_statement_line_lists',{}).items()}
        size_status=('C1_PREMISE_CONDITIONAL_ONLY; NOT_DERIVED_FROM_FULL_ACTUAL_BRANCH' if case=='bridge-positive' else 'NOT_REQUIRED_FOR_SOURCE_F_THREAD_SUBSET' if case=='source-frame-positive' else 'NOT_APPLICABLE_TO_CASE')
        result.update(classification=('NATIVE_PREFIX_FULL_VF0_CONDITIONAL_MODEL' if complete and case=='prefix-native' else 'C1_ENTRY_ENTAILMENT_AND_NATIVE_FRAME_RETURN_CONDITIONAL' if complete and case=='bridge-positive' else 'SOURCE4_CURRENT_OWNERS_F_THREAD_AND_NATIVE_FRAME_RETURN_CONDITIONAL' if complete and case=='source-frame-positive' else 'INTENDED_RESOURCE_CONTROL' if intended else 'NATIVE_ENTRY_OR_PREFIX_ADMISSION_BLOCKER' if not gates or not caller_ok else 'FIRST_BRIDGE_RESOURCE_OR_CONTRACT_BLOCKER' if case=='bridge-positive' else 'INCONCLUSIVE_WRONG_FIRST_OBLIGATION'),support_gates_passed=gates,verifier_exit=rows['verification'].get('exit'),first_error=first,proof_entries=len(entries),identity_helper_verified_before_caller=helper_ok,native_prefix_complete=complete if case=='prefix-native' else False,bridge_premises_derived=complete and case=='bridge-positive',positive_size_condition=size_status,full_actual_caller_proved=False,actual_sort4_run=False,intended_resource_negative=intended,leak_seen=leak_seen,full_log_sha256=sha(fixture/'verification.log'),source_hashes=before,stages={n:r.get('exit') for n,r in rows.items()})
        result.update(identity_call_reached=identity_reached if case=='bridge-positive' else None,observed_target_statement_lines=observed,representation_and_fragment_refinement_passed=all(rows.get(n,{}).get('exit')==0 for n in ('normal-export','normal-decode','readonly-export','readonly-decode','refinement')) and all(sha(fixture/n)==h for n,h in before.items()),source_mir_proof_mapping=mapping,caller_mapping_gate_passed=mapping_passed,first_prefix_proof_obligation=prefix_blocker)
        result['source_frame_subset_derived']=complete and case=='source-frame-positive'
        result['source_subset_assertion_reached']=subset_reached if case=='source-frame-positive' else None
        if prefix_blocker and case in ('prefix-native','source-frame-positive','bridge-positive'):result['classification']='NATIVE_PREFIX_PROOF_OBLIGATION_BLOCKER'
        need(all(sha(fixture/n)==h for n,h in before.items()),'source pair changed')
    except Exception as exc:
        result.update(classification='SETUP_OR_COLLECTOR_ERROR_NOT_PROOF_VERDICT',collector_error=str(exc))
        write(root/'collector-error.json',{'reason':str(exc),'raw_preserved':True,'proof_verdict':None})
    write(root/'case-result.json',result)
    return result

def main():
    p=argparse.ArgumentParser()
    for name in ('production-source','production-applied-patch','stock-home','compiler-sysroot','evidence','proof-root','work-root','cloud-dir'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--deadline-epoch',type=int,required=True);a=p.parse_args()
    need(os.environ.get('SMALLSORT_EXECUTION_PROVIDER')=='cloud-build' and not os.environ.get('GITHUB_ACTIONS') and os.environ.get('LANE')=='o26-sort4-caller-entry','Cloud-only exact lane')
    need(all(str(getattr(a,n)).startswith('/workspace/') for n in ('production_source','evidence','proof_root','work_root','cloud_dir')),'workspace isolation')
    a.evidence.mkdir(parents=True,exist_ok=False)
    before=snapshot(a);write(a.evidence/'tool-snapshot.json',before)
    for rel in ('prelude_core.rsspec','prelude_core_core.rsspec','aliasing.rsspec','list.rsspec','std/lib.rsspec'):
        target=a.evidence/'model'/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((a.production_source/'bin/rust'/rel).read_bytes())
    (a.evidence/'model/vf_mir_translator.ml').write_bytes((a.production_source/'src/rust_frontend/vf_mir_translator/vf_mir_translator.ml').read_bytes())
    env=os.environ.copy();deps=a.work_root/'vfdeps-adf88dc';env['PATH']=str(a.production_source/'bin')+':'+str(deps/'bin')+':'+env.get('PATH','');env['LD_LIBRARY_PATH']=str(a.compiler_sysroot/'lib')+':'+str(a.production_source/'bin')+':'+str(deps/'lib');env['CAPNP_INC_DIR']=str(deps/'include');env['RUSTUP_TOOLCHAIN']='nightly-2026-09-25'
    prep=load_module(a.proof_root/'research/challenge-8/caller-entry/prepare.py','caller_prepare');capture=load_module(a.proof_root/'research/challenge-8/overnight-sort4/capture.py','caller_mir_static');parser=load_module(a.cloud_dir/'strict-cut-false-posts-audit.py','caller_proof_parser')
    rows={}
    for case in prep.CASES:
        rows[case]=run_case(a,prep,capture,parser,case,env)
        write(a.evidence/'case-results-so-far.json',rows)
    need(snapshot(a)==before,'production tool changed during bridge')
    result={'classification':'C1_CALLER_ENTRY_DIAGNOSTIC_COMPLETE','accepted':False,'diagnostic_complete':all('verifier_exit' in r for r in rows.values()),'source_frame_subset_derived':rows['source-frame-positive']['source_frame_subset_derived'],'bridge_premises_derived':rows['bridge-positive']['bridge_premises_derived'],'full_actual_caller_proved':False,'actual_sort4_proved':False,'c1_branch_proof_new':'NOT_RUN','c1_positive_size_premise_is_conditional':True,'source_frame_positive_size_premise_required':False,'positive_size_status_by_case':{name:row.get('positive_size_condition','NOT_CONFIRMED') for name,row in rows.items()},'cases':rows,'profile_status':'EXPERIMENTAL_O26_NATIVE_PREFIX_NOT_ACCEPTED','source_linkage':'Exact common actual prefix/conditions, explicit callsite boundaries, fragment refiner only','proof_sha':os.environ['PROOF_SHA'],'tool_snapshot_sha256':sha(a.evidence/'tool-snapshot.json')}
    write(a.evidence/'diagnostic-audit.json',result);print(json.dumps(result,sort_keys=True),flush=True)

if __name__=='__main__': main()
