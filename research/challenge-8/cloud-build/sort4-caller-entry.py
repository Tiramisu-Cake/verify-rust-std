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
        rows={}
        for mode in ('normal','readonly'):
            argv=[exporter,'verified/lib.rs','--sysroot='+str(a.compiler_sysroot),'--edition','2021']
            if mode=='readonly': argv.append('--vf-rust-mir-exporter:preprocess-readonly')
            rows[mode+'-export']=stage(a,fixture,mode+'-export',argv,env,100,stdout=mode+'-mir.bin')
            if rows[mode+'-export']['exit']==0:
                rows[mode+'-decode']=stage(a,fixture,mode+'-decode',['capnp','decode',str(schema),'VfMir'],env,60,stdin=mode+'-mir.bin',stdout=mode+'-mir.txt')
                if rows[mode+'-decode']['exit']==0:
                    defpath,record=capture.complete_function_record((fixture/(mode+'-mir.txt')).read_text(),'small_sort_general_with_scratch')
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
        complete=(gates and caller_ok and helper_ok and identity_reached and rows['verification'].get('exit')==0 and not errors and re.search(r'0 errors found \(\d+ statements verified\)',log) is not None)
        intended=False
        if gates and caller_ok and len(errors)==1 and rows['verification'].get('exit')==1 and entries[0]<log.index(errors[0]):
            if case=='range-negative': intended=('Cannot prove condition' in errors[0] and 'array_split' in log[entries[0]:] and 'len + 1' in log[log.index(errors[0]):])
            if case=='duplicate-negative': intended=('No matching heap chunks: array<T>' in errors[0] and 'DUPLICATE_AUTHORITY_CONTROL' in log[log.index(errors[0]):])
        first=errors[0] if errors else next((line for line in log.splitlines() if line.startswith('error[') or line.startswith('error:')),None)
        result.update(classification=('NATIVE_PREFIX_FULL_VF0_CONDITIONAL_MODEL' if complete and case=='prefix-native' else 'C1_ENTRY_ENTAILMENT_AND_NATIVE_FRAME_RETURN_CONDITIONAL' if complete and case=='bridge-positive' else 'INTENDED_RESOURCE_CONTROL' if intended else 'NATIVE_ENTRY_OR_PREFIX_ADMISSION_BLOCKER' if not gates or not caller_ok else 'FIRST_BRIDGE_RESOURCE_OR_CONTRACT_BLOCKER' if case=='bridge-positive' else 'INCONCLUSIVE_WRONG_FIRST_OBLIGATION'),support_gates_passed=gates,verifier_exit=rows['verification'].get('exit'),first_error=first,proof_entries=len(entries),identity_helper_verified_before_caller=helper_ok,native_prefix_complete=complete if case=='prefix-native' else False,bridge_premises_derived=complete and case=='bridge-positive',positive_size_condition='EXISTING_C1_PREMISE_NOT_DERIVED_FROM_FULL_ACTUAL_BRANCH',full_actual_caller_proved=False,actual_sort4_run=False,intended_resource_negative=intended,leak_seen='Leak check.' in log[entries[0]:] if caller_ok else False,full_log_sha256=sha(fixture/'verification.log'),source_hashes=before,stages={n:r.get('exit') for n,r in rows.items()})
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
    result={'classification':'C1_CALLER_ENTRY_DIAGNOSTIC_COMPLETE','accepted':False,'diagnostic_complete':all('verifier_exit' in r for r in rows.values()),'bridge_premises_derived':rows['bridge-positive']['bridge_premises_derived'],'full_actual_caller_proved':False,'actual_sort4_proved':False,'c1_branch_proof_new':'NOT_RUN','positive_size_supplied_or_conditional':True,'cases':rows,'profile_status':'EXPERIMENTAL_O26_NATIVE_PREFIX_NOT_ACCEPTED','source_linkage':'Exact common actual prefix/conditions, explicit callsite boundaries, fragment refiner only','proof_sha':os.environ['PROOF_SHA'],'tool_snapshot_sha256':sha(a.evidence/'tool-snapshot.json')}
    write(a.evidence/'diagnostic-audit.json',result);print(json.dumps(result,sort_keys=True),flush=True)

if __name__=='__main__': main()
