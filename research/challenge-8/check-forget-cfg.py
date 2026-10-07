#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted acceptance for the narrow S7c ManuallyDrop::new CFG repair."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, os, re, subprocess, sys, time
from pathlib import Path
from types import SimpleNamespace

PROFILE = "experimental-manuallydrop-new-cfg-v1"
PATCH_SHA = "c7cc08a995bac5879901f4fe08030f09d23bdfefb1a3ab5893be12a8dd1f8fc1"

def ast_return_line(ast: str, name: str, function_name: str) -> str | None:
    # The return loc is either the function's closing brace or a call/cleanup
    # span. Bind the AST function first instead of guessing its return loc.
    functions = re.split(r'(?=^\s*Func \()', ast, flags=re.M)
    selected = [part for part in functions if f', "{function_name}", [' in part]
    if len(selected) != 1:
        return None
    return next((line for line in selected[0].splitlines()
                 if 'ReturnStmt' in line and f'"{name}"' in line), None)

def source_function_lines(source: bytes, name: bytes) -> tuple[int, int]:
    lines=source.splitlines(); start=next(i for i,x in enumerate(lines,1) if x.startswith(b'unsafe fn '+name))
    text=b'\n'.join(lines[start-1:]); op=text.index(b'{'); depth=0
    for offset,ch in enumerate(text[op:],op):
        if ch==123: depth+=1
        elif ch==125:
            depth-=1
            if depth==0: return start, start+text[:offset].count(b'\n')
    raise ValueError(f"function body unclosed: {name.decode()}")

def ast_return_executed(ast_line: str | None, log: str) -> bool:
    if ast_line is None: return False
    loc=re.search(r'loc "([^"]+)"',ast_line)
    return bool(loc and f'{loc.group(1)}: Executing return statement' in log)

def sha(b): return hashlib.sha256(b).hexdigest()
def need(ok, why):
    if not ok: raise ValueError(why)
def write(p, v):
    p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(v, indent=2, sort_keys=True)+"\n")
def load(p, name):
    s=importlib.util.spec_from_file_location(name,p); need(s and s.loader, f"missing {p}")
    m=importlib.util.module_from_spec(s); sys.modules[name]=m; s.loader.exec_module(m); return m

def card():
    return {"profile":PROFILE,"base_patch_sha256":PATCH_SHA,"actual_linkage":"NOT_RUN",
      "cases":[
       ["old_frozen_profile_reproducer","exit1 sole `verified/lib.rs(3,1-16,2): dead code`; exact S7b source and MIR"],
       ["autonomous_forget","readonly/normal export+decode, refinement, full verifier all 0; body/return/leak; dead-code gate"],
       ["ordinary_potential_unwind","local unsafe panic callee; verified normal and reachable unwind posts; actual unwind MIR (Continue or Cleanup)"],
       ["false_unwind_post","reject only caller's false unwind post at its source line"],
       ["shared_cleanup","caller MIR has ManuallyDrop and panicking calls to one cleanup target; AST retains unwind ReturnStmt"],
       ["false_normal_post","same generic body executes and fails exact normal post"],
       ["contradictory_precondition_nonempty_body","same nonempty body fails mandatory dead-code gate"],
       ["constructor/as_mut_ptr/intrinsics/pointer_drop","invoke existing full drivers/classifiers with unchanged expectations"]]}

def baseline(path, hashes):
    s=json.loads((path/'summary.json').read_text()); log=(path/'full-verification.log').read_text(errors='replace')
    ds=[x for x in log.splitlines() if re.search(r"verified/lib\.rs\(\d+,\d+-\d+,\d+\): dead code$",x)]
    need(ds==["verified/lib.rs(3,1-16,2): dead code"] and
         s.get("stages",{}).get("full-verification",{}).get("exit")==1 and
         s.get("source_integrity") is True and s.get("target_body_execution") and
         s.get("target_return") and s.get("target_leak_check"),"old profile is not exact intended dead-code failure")
    f=json.loads((path/'fixture.json').read_text())
    need(f.get('original_sha256')==hashes[0] and f.get('verified_sha256')==hashes[1],"old S7b source/contract differs")
    need(all(s.get('stages',{}).get(k,{}).get('exit')==0 for k in ('normal-export','readonly-export','refinement')),"old profile failed before verifier obligation")
    for fn, key in (('normal-mir.txt','normal_mir_sha256'),('readonly-mir.txt','readonly_mir_sha256')):
        need((path/fn).is_file() and sha((path/fn).read_bytes())==s.get(key),f"baseline {fn} hash differs")
    return {"classification":"SOLE_DEAD_CODE_REPRODUCED","diagnostic":ds[0],"normal_mir_sha256":s.get('normal_mir_sha256'),"readonly_mir_sha256":s.get('readonly_mir_sha256'),"summary_sha256":sha((path/'summary.json').read_bytes())}

def bounded_run(g, root, args, fixture, deadline):
    old=g.run_stage
    def stage(name, argv, root, env, fr, secs, stdin_name=None, stdout_name=None):
        return old(name,argv,root,env,fr,min(secs,max(1,int(deadline-time.monotonic()))),stdin_name,stdout_name)
    g.run_stage=stage
    try:return g.run(root,args,fixture)
    finally:g.run_stage=old

def basic(g, root, args, fixture, deadline, neg=None):
    stages=bounded_run(g,root,args,fixture,deadline); log=(root/'full-verification.log').read_text(errors='replace')
    errors=[x for x in log.splitlines() if ': error:' in x]
    res=g.classify(root,stages,False)
    front=all(stages.get(k,{}).get('exit')==0 for k in ('readonly-export','readonly-decode','normal-export','normal-decode','refinement'))
    if neg=='false_post':
        lines=(root/'verified/lib.rs').read_text().splitlines(); n=next(i for i,x in enumerate(lines,1) if 'ens thread_token(tid) &*& false' in x)
        ok=front and stages['full-verification']['exit']==1 and len(errors)==1 and 'Cannot prove false' in errors[0] and re.search(rf'verified/lib\.rs\({n},\d+(?:-|\))',errors[0]) and res.get('target_body_execution') and res.get('target_return') and res.get('source_integrity') and res.get('exact_predeclared_header_set')
        res['classification']='INTENDED_PROOF_REJECTION' if ok else 'INCONCLUSIVE'
    elif neg=='dead':
        ok=(front and stages['full-verification']['exit']==1 and
            log.splitlines().count('verified/lib.rs(3,1-16,2): dead code')==1 and not errors and
            res.get('source_integrity') is True and res.get('exact_predeclared_header_set') is True and
            res.get('target_header_count')==1)
        res['classification']='INTENDED_PROOF_REJECTION' if ok else 'INCONCLUSIVE'
    write(root/'summary.json',res); return res

def build_generic(g, root, variant):
    root.mkdir(parents=True); (root/'original').mkdir(); (root/'verified').mkdir()
    orig=g.ORIGINAL; ver=g.VERIFIED
    if variant=='false_post': ver=ver.replace(b'ens thread_token(tid);',b'ens thread_token(tid) &*& false;')
    elif variant=='dead': ver=ver.replace(b'req thread_token(?tid) &*& tid == currentThread;',b'req thread_token(?tid) &*& tid == currentThread &*& false;')
    need(g.strip_ghost(ver)==orig,'control changed runtime body')
    (root/'original/lib.rs').write_bytes(orig); (root/'verified/lib.rs').write_bytes(ver)
    f={'variant':variant,'original_sha256':sha(orig),'verified_sha256':sha(ver),'predeclared_functions':['checked_forget_generic']}
    write(root/'fixture.json',f); return f

def mir_body(d, name, ctor):
    marker=f'defPath = "{name}"'; need(d.count(marker)==1,f"MIR body identity not unique: {name}")
    at=d.index(marker); lead=d.rfind('    ( defKind =',0,at); need(lead>=0,'MIR body opener missing')
    op=d.index('(',lead); body=ctor.mir_balanced_item(d,op); need(marker in body,'MIR body mismatch'); return body

def unwind_case(g,ctor,root,args,deadline,false=False,shared=False):
    root.mkdir(); (root/'original').mkdir(); (root/'verified').mkdir()
    pre=b'req thread_token(?tid) &*& tid == currentThread;'; post=b'ens thread_token(tid);'
    ghost=lambda clause: b'/*@\n'+clause+b'\n@*/\n'
    cg=ghost(pre)+ghost(post)+ghost(b'on_unwind_ens thread_token(tid);')
    cn=b'on_unwind_ens false;' if false else b'on_unwind_ens thread_token(tid);'
    caller=b'checked_shared_cleanup' if shared else b'checked_unwind_call'
    callghost=ghost(pre)+ghost(post)+ghost(cn)
    prefix=b'unsafe fn potentially_panicking(b: bool)\n'+cg+b'{\n    if b { panic!("cfg unwind"); }\n}\n\n'
    body=b'{\n    let _ = std::mem::ManuallyDrop::new(t);\n' if shared else b'{\n'
    signature=b'<T>(b: bool, t: T)' if shared else b'(b: bool)'
    src=prefix+b'unsafe fn '+caller+signature+b'\n'+callghost+body+b'    unsafe { potentially_panicking(b); }\n}\n'
    orig=g.strip_ghost(src); (root/'original/lib.rs').write_bytes(orig); (root/'verified/lib.rs').write_bytes(src)
    marker=b'on_unwind_ens false;' if false else b'potentially_panicking(b)'; line=next(i for i,x in enumerate(src.splitlines(),1) if marker in x)
    f={'variant':'false_unwind' if false else ('shared_cleanup' if shared else 'ordinary_unwind'),'original_sha256':sha(orig),'verified_sha256':sha(src),'predeclared_functions':['potentially_panicking',caller.decode()],'focus_line':line}
    caller_line,caller_end=source_function_lines(src,caller)
    f['caller_line']=caller_line; f['caller_end_line']=caller_end
    write(root/'fixture.json',f); st=bounded_run(g,root,args,f,deadline); log=(root/'full-verification.log').read_text(errors='replace')
    expected=list(g.EXPECTED_TIMED_FUNCTIONS[:-1])+f['predeclared_functions']; err=None
    if false: err={'file':'verified/lib.rs','line':line,'message_contains':'Cannot prove false','function':caller.decode()}
    strict=g.strict_classifier().classify_unit(log,st['full-verification']['exit'],expected,positive=not false,expected_error=err)
    ok= strict.get('classification')==('INTENDED_NEGATIVE' if false else 'POSITIVE')
    ok=ok and all(x.get('source_exact') is True for x in st.values())
    mir=(root/'normal-mir.txt').read_text(errors='replace') if (root/'normal-mir.txt').exists() else ''
    body=mir_body(mir,caller.decode(),ctor) if mir else ''
    caller_evidence=next((x for x in strict.get('timed_functions',[]) if x.get('function')==caller.decode()),{})
    ast=(root/'verified-ast.txt').read_text(errors='replace') if (root/'verified-ast.txt').exists() else ''
    unwind_return=ast_return_line(ast,'unwinding',caller.decode())
    normal_return=ast_return_line(ast,'returning',caller.decode())
    cfg={'caller_mir_sha256':sha(body.encode()),'cleanup_targets':re.findall(r'unwindAction\s*=\s*\(cleanup\s*=\s*\(index\s*=\s*(\d+)\)',body),
         'caller_body_executed':caller_evidence.get('body_execution_seen') is True,
         'caller_normal_return_and_leak':caller_evidence.get('return_seen') is True and caller_evidence.get('leak_check_seen') is True,
         'caller_unwind_return_ast':unwind_return,'caller_normal_return_ast':normal_return,
         'caller_unwind_return_executed':ast_return_executed(unwind_return,log),
         'caller_normal_return_executed':ast_return_executed(normal_return,log)}
    if false:
        ok=ok and cfg['caller_unwind_return_ast'] is not None and cfg['caller_unwind_return_executed']
    if shared:
        md_name='name = "std::mem::ManuallyDrop::<T>::new"'
        md_at=body.find(md_name); fn_def=None
        if md_at>=0:
            fd=body.rfind('fnDef = (',0,md_at)
            if fd>=0:
                opening=body.index('(',fd+len('fnDef = ')); fn_def=ctor.mir_balanced_item(body,opening)
        cfg.update({'manuallydrop': md_name in body,
                    'typed_generic_substitution_T': bool(fn_def and ('param' in fn_def) and ('T' in fn_def)),
                    'panicking_call':'potentially_panicking' in body})
        ok=ok and cfg['manuallydrop'] and cfg['typed_generic_substitution_T'] and cfg['panicking_call'] and len(cfg['cleanup_targets'])>=2 and len(set(cfg['cleanup_targets']))<len(cfg['cleanup_targets']) and unwind_return and normal_return and cfg['caller_normal_return_and_leak'] and cfg['caller_body_executed'] and cfg['caller_unwind_return_executed'] and cfg['caller_normal_return_executed']
    elif not false: ok=ok and 'potentially_panicking' in body and bool(cfg['cleanup_targets'] or re.search(r'unwindAction\s*=\s*\(continue',body)) and unwind_return and normal_return and cfg['caller_normal_return_and_leak'] and cfg['caller_body_executed'] and cfg['caller_unwind_return_executed'] and cfg['caller_normal_return_executed']
    if not front_ok(st): ok=False
    result={'classification':('INTENDED_PROOF_REJECTION' if false else 'DIAGNOSTIC_POSITIVE') if ok else 'INCONCLUSIVE','exact_classifier':strict,'cfg_evidence':cfg,'stages':st}
    write(root/'summary.json',result); return result

def front_ok(s): return all(s.get(k,{}).get('exit')==0 for k in ('readonly-export','readonly-decode','normal-export','normal-decode','refinement'))

def command(name,argv,root,env,deadline,records):
    out=root/f'{name}.log'; remaining=max(1,int(deadline-time.monotonic()))
    try:
        with out.open('wb') as f: code=subprocess.run(argv,stdout=f,stderr=subprocess.STDOUT,env=env,timeout=remaining,check=False).returncode
        timed=False
    except subprocess.TimeoutExpired: code=124; timed=True
    r={'id':name,'exit':code,'timeout':timed,'log':out.name,'log_sha256':sha(out.read_bytes()) if out.exists() else None}; records.append(r); write(root/f'{name}-stage.json',r); return r

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for x in ('tool-home','stock-home','schema','evidence','baseline-evidence'): p.add_argument('--'+x,type=Path,required=True)
    p.add_argument('--focused-controls',action='store_true'); p.add_argument('--compiler-sysroot',required=True); p.add_argument('--budget-seconds',type=int,default=330); a=p.parse_args()
    need(os.environ.get('GITHUB_ACTIONS')=='true' and os.environ.get('RUNNER_ENVIRONMENT')=='github-hosted' and os.environ.get('RUNNER_OS')=='Linux','GitHub hosted Linux required')
    need(os.environ.get('SORT4_SELECT_PROFILE')==PROFILE,'experimental CFG profile required'); need(15<=a.budget_seconds<=648,'budget exceeds S7c allowance')
    repo=Path(__file__).resolve().parents[2]; scripts=repo/'research/challenge-8'; ev=a.evidence.resolve(); ev.mkdir(parents=True,exist_ok=False)
    c=card(); write(ev/'predeclared-cases.json',c)
    g=load(scripts/'check-forget-generic.py','s7c_generic'); need(g.strict_classifier().self_test()['pass'],'classifier self test failed')
    hashes=(sha(g.ORIGINAL),sha(g.VERIFIED)); c['source_hashes']={'original':hashes[0],'verified':hashes[1]}; write(ev/'predeclared-cases.json',c)
    write(ev/'profile.json',{'profile':PROFILE,'base_profile':'experimental-source-linked-select-pointer-drop-v4','base_patch_sha256':PATCH_SHA,'tool_home':str(a.tool_home.resolve()),'stock_home':str(a.stock_home.resolve()),'overlay_authentication':'provided by caller'})
    old=baseline(a.baseline_evidence.resolve(),hashes)
    env=os.environ.copy(); env['PATH']=str(a.tool_home/'bin')+os.pathsep+env.get('PATH','')
    for k in ('SORT4_MAYBEUNINIT_REPO_ROOT','SORT4_SELECT_INTRINSIC_REPO_ROOT','SORT4_POINTER_DROP_REPO_ROOT'): env.pop(k,None)
    start=time.monotonic(); deadline=start+a.budget_seconds-10; args=SimpleNamespace(tool_home=a.tool_home,schema=a.schema,compiler_sysroot=a.compiler_sysroot,dump_ast_with_locs=True)
    results={}; base=ev/'autonomous-forget'; f=g.fixture(base,g.certificate(repo)); results['autonomous_forget']=basic(g,base,args,f,deadline)
    ast=(base/'verified-ast.txt').read_text(errors='replace') if (base/'verified-ast.txt').exists() else ''
    positive=results['autonomous_forget']; positive['mir_same_old_profile']=positive.get('normal_mir_sha256')==old.get('normal_mir_sha256') and positive.get('readonly_mir_sha256')==old.get('readonly_mir_sha256')
    positive['ast_cfg']= {'normal_return': bool(re.search(r'ReturnStmt[^\n]*"returning"',ast)),
                          'orphan_unwind_return_absent': not bool(re.search(r'ReturnStmt[^\n]*"unwinding"',ast))}
    positive['classification']='ACCEPTED_AUTONOMOUS_BODY' if positive.get('classification')=='DIAGNOSTIC_POSITIVE' and positive.get('all_required_stage_exits_zero') and positive.get('target_body_execution') and positive.get('target_return') and positive.get('target_leak_check') and positive.get('dead_code_gate_complete') and positive['mir_same_old_profile'] and all(positive['ast_cfg'].values()) else 'INCONCLUSIVE'
    write(base/'summary.json',positive)
    ctor=load(scripts/'check-maybeuninit-new-pointer.py','s7c_ctor')
    if positive['classification']=='ACCEPTED_AUTONOMOUS_BODY':
        for nm,kw in [('ordinary_unwind',{}),('false_unwind',{'false':True}),('shared_cleanup',{'shared':True})]:
            if time.monotonic()>=deadline: break
            try:
                results[nm]=unwind_case(g,ctor,ev/nm,args,deadline,**kw)
            except Exception as exc:
                d=ev/nm; d.mkdir(parents=True,exist_ok=True)
                results[nm]={'classification':'INCONCLUSIVE','harness_exception':f'{type(exc).__name__}: {exc}'}
                write(d/'summary.json',results[nm])
        for nm,variant in [('false_normal_post','false_post'),('contradictory_precondition_nonempty_body','dead')]:
            if time.monotonic()>=deadline: break
            root=ev/nm; f=build_generic(g,root,variant); results[nm]=basic(g,root,args,f,deadline,variant)
    controls=(results.get('ordinary_unwind',{}).get('classification')=='DIAGNOSTIC_POSITIVE' and results.get('false_unwind',{}).get('classification')=='INTENDED_PROOF_REJECTION' and results.get('shared_cleanup',{}).get('classification')=='DIAGNOSTIC_POSITIVE' and results.get('false_normal_post',{}).get('classification')=='INTENDED_PROOF_REJECTION' and results.get('contradictory_precondition_nonempty_body',{}).get('classification')=='INTENDED_PROOF_REJECTION')
    regression=[('constructor-classifier',[sys.executable,str(scripts/'test-sort4-maybeuninit-classifier.py')]),('constructor-matrix',[sys.executable,str(scripts/'check-maybeuninit-new-pointer.py'),'--stock-home',str(a.stock_home),'--tool-home',str(a.tool_home),'--schema',str(a.schema),'--compiler-sysroot',a.compiler_sysroot,'--evidence',str(ev/'constructor-regressions'),'--components-only']),('as-mut-ptr-classifier',[sys.executable,str(scripts/'test-select-pointer-classifier.py'),'--evidence',str(ev/'as-mut-ptr-classifier.json')]),('as-mut-ptr-matrix',[sys.executable,str(scripts/'check-select-pointer.py'),'--stock-home',str(a.stock_home),'--tool-home',str(a.tool_home),'--schema',str(a.schema),'--compiler-sysroot',a.compiler_sysroot,'--evidence',str(ev/'as-mut-ptr-matrix'),'--constructor-summary',str(ev/'constructor-regressions/summary.json'),'--classifier-summary',str(ev/'as-mut-ptr-classifier.json')]),('intrinsics-classifier',[sys.executable,str(scripts/'test-select-pointer-intrinsics-classifier.py'),'--evidence',str(ev/'intrinsics-classifier.json')]),('intrinsics-matrix',[sys.executable,str(scripts/'check-select-pointer-intrinsics.py'),'--stock-home',str(a.stock_home),'--tool-home',str(a.tool_home),'--schema',str(a.schema),'--compiler-sysroot',a.compiler_sysroot,'--evidence',str(ev/'intrinsics-matrix'),'--constructor-summary',str(ev/'constructor-regressions/summary.json'),'--as-mut-ptr-summary',str(ev/'as-mut-ptr-matrix/summary.json'),'--classifier-summary',str(ev/'intrinsics-classifier.json')]),('pointer-drop-classifier',[sys.executable,str(scripts/'test-pointer-drop-classifier.py'),'--evidence',str(ev/'pointer-drop-classifier.json')]),('pointer-drop-matrix',[sys.executable,str(scripts/'check-pointer-drop.py'),'--tool-home',str(a.tool_home),'--schema',str(a.schema),'--compiler-sysroot',a.compiler_sysroot,'--evidence',str(ev/'pointer-drop-matrix'),'--constructor-summary',str(ev/'constructor-regressions/summary.json'),'--as-mut-ptr-summary',str(ev/'as-mut-ptr-matrix/summary.json'),'--intrinsic-summary',str(ev/'intrinsics-matrix/summary.json'),'--classifier-summary',str(ev/'pointer-drop-classifier.json')])]
    records=[]
    if not a.focused_controls and positive['classification']=='ACCEPTED_AUTONOMOUS_BODY' and time.monotonic()<deadline:
        env['SORT4_MAYBEUNINIT_REPO_ROOT']=str(repo)
        for nm,argv in regression:
            if time.monotonic()>=deadline: break
            r=command(nm,argv,ev,env,deadline,records)
            if r['exit']: break
    for nm,_ in regression[len(records):]: write(ev/f'{nm}-not-run.json',{'status':'NOT_RUN','reason':'focused continuation excludes repeated matrices' if a.focused_controls else 'previous gate failed or budget reserve reached'})
    for nm in ('ordinary_unwind','false_unwind','shared_cleanup','false_normal_post','contradictory_precondition_nonempty_body'):
        if nm not in results: write(ev/f'{nm}-not-run.json',{'status':'NOT_RUN','reason':'positive gate failed or S7c time reserve reached'})
    regok=len(records)==len(regression) and all(x['exit']==0 for x in records)
    accepted=positive['classification']=='ACCEPTED_AUTONOMOUS_BODY' and controls and regok
    summary={'classification':'ACCEPTED_AUTONOMOUS_BODY_ONLY' if accepted else 'INCONCLUSIVE','profile_status':'ACCEPTED_AUTONOMOUS_BODY_ONLY' if accepted else 'UNACCEPTED','accepted_autonomous_body':positive['classification']=='ACCEPTED_AUTONOMOUS_BODY','old_profile_dead_code_reproduced':old['classification']=='SOLE_DEAD_CODE_REPRODUCED','mandatory_controls_complete':controls,'regression_records':records,'regressions_all_pass':regok,'actual_linkage':'NOT_RUN','stages':results,'old_profile':old,'unrun':[nm for nm in ('ordinary_unwind','false_unwind','shared_cleanup','false_normal_post','contradictory_precondition_nonempty_body') if nm not in results]+[nm for nm,_ in regression[len(records):]]}
    write(ev/'summary.json',summary); print(json.dumps({k:summary[k] for k in ('classification','mandatory_controls_complete','regressions_all_pass','unrun')},sort_keys=True)); raise SystemExit(0 if accepted else 1)
if __name__=='__main__': main()
