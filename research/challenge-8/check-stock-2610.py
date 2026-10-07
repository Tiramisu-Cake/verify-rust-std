#!/usr/bin/env python3
"""Isolated stock fixtures; preserve old harness and classification bytes."""
import argparse, hashlib, importlib.util, json, os, re, sys, time
from pathlib import Path

def load(path,name):
 s=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(s); sys.modules[name]=m; s.loader.exec_module(m); return m

def write(path,obj): path.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n")
def sha(b): return hashlib.sha256(b).hexdigest()

def main():
 assert os.environ.get('GITHUB_ACTIONS')=='true' and os.environ.get('RUNNER_ENVIRONMENT')=='github-hosted'
 p=argparse.ArgumentParser(); p.add_argument('--tool-home',type=Path,required=True); p.add_argument('--schema',type=Path,required=True); p.add_argument('--compiler-sysroot',required=True); p.add_argument('--evidence',type=Path,required=True); p.add_argument('--deadline-epoch',type=int,required=True); a=p.parse_args(); a.dump_ast_with_locs=True
 here=Path(__file__).parent; g=load(here/'check-forget-generic.py','old_run_helpers'); c=g.strict_classifier()
 # Reuse only process/stage recording. No old certificates, profile or summaries.
 base=['u32_sync','u32_share_mono','init_ref_readonly_points_to_shared']
 ghost=lambda x:'/*@\n'+x+'\n@*/\n'
 pre='req thread_token(?tid) &*& tid == currentThread;'; post='ens thread_token(tid);'; unw='on_unwind_ens false;'
 simple=lambda sig,pr,po,uw,body:sig+'\n'+ghost(pr)+ghost(po)+ghost(uw)+body+'\n'
 u32=simple('unsafe fn stock_u32(x: u32) -> u32',pre,post[:-1]+' &*& result == x;',unw,'{\n    x\n}')
 raw=simple('unsafe fn stock_raw(p: *const u32) -> u32',pre[:-1]+' &*& *p |-> ?v;',post[:-1]+' &*& *p |-> v &*& result == v;',unw,'{\n    unsafe { *p }\n}')
 panic=simple('unsafe fn potentially_panicking(b: bool)',pre,post,'on_unwind_ens thread_token(tid);','{\n    if b { panic!("stock unwind"); }\n}')
 call=lambda false,shared:panic+'\n'+simple('unsafe fn '+('checked_shared_cleanup<T>(b: bool, t: T)' if shared else 'checked_unwind_call(b: bool)'),pre,post,'on_unwind_ens false;' if false else 'on_unwind_ens thread_token(tid);','{\n'+('    let _ = std::mem::ManuallyDrop::new(t);\n' if shared else '')+'    unsafe { potentially_panicking(b); }\n}')
 cases=[('u32_positive',u32,['stock_u32'],None),('raw_positive',raw,['stock_raw'],None),('u32_false_post',u32.replace('result == x','false'),['stock_u32'],'false-post'),('raw_false_post',raw.replace('result == v','false'),['stock_raw'],'false-post'),('u32_contradictory_pre',u32.replace('tid == currentThread;','tid == currentThread &*& false;'),['stock_u32'],'dead'),('forget_positive',g.VERIFIED.decode(),['checked_forget_generic'],None),('forget_false_post',g.VERIFIED.decode().replace('ens thread_token(tid);','ens thread_token(tid) &*& false;'),['checked_forget_generic'],'false-post'),('forget_contradictory_pre',g.VERIFIED.decode().replace('tid == currentThread;','tid == currentThread &*& false;'),['checked_forget_generic'],'dead'),('ordinary_unwind',call(False,False),['potentially_panicking','checked_unwind_call'],None),('false_unwind',call(True,False),['potentially_panicking','checked_unwind_call'],'false-unwind'),('shared_cleanup',call(False,True),['potentially_panicking','checked_shared_cleanup'],None)]
 a.evidence.mkdir(parents=True); summaries={}
 mem=Path('library/core/src/mem/mod.rs').read_bytes()
 assert sha(mem)=='b86a596a58dcb21a45e8b29b33327ca8c7bde708aa6fca158d4366e51403daf2' and mem.count(g.FORGET_SOURCE)==1
 write(a.evidence/'source-certificate.json',{'mem_sha256':sha(mem),'forget_body_sha256':sha(g.FORGET_BODY),'body_exact':True,'adapter_contract':g.GHOST.decode(),'trusted_boundary':'stock ManuallyDrop representation/destructor/no-unwind identity lowering; no actual safe summary/linkage'})
 old_stage=g.run_stage
 def bounded(name,argv,root,env,fr,secs,stdin_name=None,stdout_name=None):
  return old_stage(name,argv,root,env,fr,min(secs,max(1,int(a.deadline_epoch-time.time()))),stdin_name,stdout_name)
 g.run_stage=bounded
 for name,source,functions,negative in cases:
  if time.time()+15>=a.deadline_epoch:
   summaries[name]={'classification':'NOT_RUN','reason':'artifact reserve'}; continue
  root=a.evidence/name; root.mkdir(); (root/'original').mkdir(); (root/'verified').mkdir()
  ver=source.encode(); orig=g.strip_ghost(ver)
  (root/'original/lib.rs').write_bytes(orig); (root/'verified/lib.rs').write_bytes(ver)
  fixture={'variant':name,'original_sha256':sha(orig),'verified_sha256':sha(ver),'functions':functions,'ghost_strip_exact':True}
  write(root/'fixture.json',fixture)
  st=g.run(root,a,fixture); log=(root/'full-verification.log').read_text(errors='replace'); expected=base+functions
  target_error=None
  if negative in ('false-post','false-unwind'):
   marker='on_unwind_ens false;' if negative=='false-unwind' else 'ens '
   line=next(i for i,x in enumerate(source.splitlines(),1) if marker in x and 'false' in x)
   target_error={'file':'verified/lib.rs','line':line,'message_contains':'Cannot prove false','function':functions[-1]}
  strict=c.classify_unit(log,st['full-verification']['exit'],expected,positive=negative is None,expected_error=target_error)
  frontend=all(st.get(k,{}).get('exit')==0 for k in ('normal-export','normal-decode','readonly-export','readonly-decode','refinement'))
  integrity=all(s['source_exact'] for s in st.values())
  cls=strict['classification'] if frontend and integrity else 'INCONCLUSIVE'
  dead=[x for x in log.splitlines() if re.search(r': dead code$',x)]
  if negative=='dead':
   start=next(i for i,x in enumerate(source.splitlines(),1) if 'unsafe fn '+functions[-1] in x); end=len(source.splitlines())
   exact_span=f'verified/lib.rs({start},1-{end},2): dead code'
   target=[x for x in strict['timed_functions'] if x['function']==functions[-1]]
   intended=frontend and integrity and st['full-verification']['exit']==1 and strict['function_list_exact'] and strict['error_count']==0 and dead and exact_span in dead and len(target)==1 and not target[0]['body_execution_seen'] and all(x.startswith('verified/lib.rs(') for x in dead)
   cls='INTENDED_DEAD_CODE_REJECTION' if intended else 'INCONCLUSIVE'
  ast=root/'verified-ast.txt'
  result={'classification':cls,'frontend_all_zero':frontend,'source_integrity':integrity,'strict_original_classification':strict,'negative_kind':negative,'expected_error':target_error,'dead_code_diagnostics':dead,'ast_sha256':sha(ast.read_bytes()) if ast.exists() else None,'stages':st}
  write(root/'summary.json',result); summaries[name]=result
  print(json.dumps({'case':name,'classification':cls,'exits':{k:v['exit'] for k,v in st.items()},'first_error':strict['first_error'],'dead_code':dead}),flush=True)
 write(a.evidence/'summary.json',summaries)
 # Diagnostic job succeeds when evidence collection completes; acceptance is per fixture.
if __name__=='__main__':main()
