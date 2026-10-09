#!/usr/bin/env python3
"""Classify one exact-source Linux make test and its five native controls."""
import argparse, hashlib, importlib.util, json, re, subprocess
from pathlib import Path

BASE="0a83dba42db7ce0b445034ece5298afe980e57dc"
HEAD="bf63b7dff2e053eea8541996d856fac4be11f6f1"
TREE="687ae7dab447c94c4b87362d3d880d959c89e3de"
REF="refs/heads/upstream/manuallydrop-new-final-20261009"
RUSTC="f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f"
COMPONENTS=("verifast","vf-rust-mir-exporter","refinement-checker","vf-cxx-ast-exporter")
COMMANDS=("verifast forget.rs","verifast shared_cleanup.rs",
          "verifast -allow_should_fail false_normal_post.rs",
          "verifast -allow_should_fail shared_false_unwind.rs")
class Failure(Exception):
 def __init__(self,message,kind="INCOMPLETE_EVIDENCE"):
  super().__init__(message);self.kind=kind
def need(ok,message,kind="INCOMPLETE_EVIDENCE"):
 if not ok:raise Failure(message,kind)
def read(path):
 need(path.is_file(),f"missing evidence {path}")
 return path.read_bytes()
def j(path):return json.loads(read(path))
def h(data):return hashlib.sha256(data).hexdigest()
def oid(repo,*args):return subprocess.check_output(["git","-C",str(repo),*args],text=True).strip()
def stage(root,name):
 code=int(read(root/f"{name}-exit-code.txt").strip())
 stdout=read(root/f"{name}.stdout.log")
 stderr=read(root/f"{name}.stderr.log")
 resources=read(root/f"{name}-resources.txt")
 need(b'Elapsed (wall clock) time' in resources,f"{name} resource report incomplete")
 return code,stdout.decode(errors="replace"),stderr.decode(errors="replace")
def verify_make_completion(make_out):
 need(re.search(r'(?m)^\s+MYSH\s+testsuite\s*$',make_out) is not None and
      re.search(r'(?m)^\s+MYSH\s+assignments/run_model_solutions\s*$',make_out) is not None,
      'normal root and assignments make targets are not visible')
 need(re.search(r'(?m)^0 failed processes$',make_out) is not None,
      'full suite lacked a zero-failed mysh summary')
def verify_registration(registration):
 lines=registration.splitlines()
 starts=[i for i,line in enumerate(lines) if line.strip()=='cd manuallydrop_new_cfg']
 need(len(starts)==1,'ManuallyDrop native registration block absent or duplicated')
 end=next((i for i in range(starts[0]+1,len(lines)) if lines[i].strip()=='cd ..'),None)
 need(end is not None,'ManuallyDrop native registration block unterminated')
 block='\n'.join(lines[starts[0]:end+1])
 for command in COMMANDS:
  need(sum(line.strip()==command for line in lines[starts[0]:end+1])==1,
       f'ManuallyDrop native command absent or duplicated: {command}')
 need('dead_code_pre.rs(1,1-7,2): dead code' in block and
      'EXIT:1' in block and 'verifast dead_code_pre.rs 2>&1' in block and
      '-allow_dead_code' not in block and '-ignore_unwind_paths' not in block,
      'selected native block lacks exact dead diagnostic or disables a checker')
 return block
def affected(root):
 helper_path=Path(__file__).with_name('mdnew-audit.py')
 spec=importlib.util.spec_from_file_location('mdnew_structural_helpers',helper_path)
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 findings={}
 for case in ('forget','shared_cleanup'):
  folder=root/'affected'/case
  for op in ('verifast','exporter','decode'):
   code,_,_=stage(root,f'affected-{case}-{op}')
   need(code==0,f'{case} fresh {op} stage failed','AFFECTED_GATE_FAILED')
  mir=read(folder/'normal-mir.txt').decode(errors='replace')
  ast=read(folder/'verified-ast.txt').decode(errors='replace')
  body=module.mir_body(mir,case)
  cleanup,target,term=module.call_record(body,'std::mem::ManuallyDrop::<T>::new')
  blocks=module.mir_blocks(body)
  need(cleanup is not None and cleanup in blocks and target in blocks and
       'isCleanup = true' in blocks[cleanup] and 'unwindResume = void' in blocks[cleanup],
       f'{case} typed ManuallyDrop call lacks original cleanup block','AFFECTED_GATE_FAILED')
  need(re.search(r'substs = \[.*?param = "T"',term,re.S) is not None,
       f'{case} MIR call lacks generic T substitution','AFFECTED_GATE_FAILED')
  caller=module.ast_body(ast,case)
  if case=='forget':
   need('"returning"' in caller and
        re.search(r'ReturnStmt .*?"unwinding"',caller) is None and
        re.search(r'LabelStmt \([^\n]*"'+str(cleanup)+r'"',caller) is None,
        'forget AST contains orphan cleanup or lacks normal successor','AFFECTED_GATE_FAILED')
  else:
   ordinary_cleanup,ordinary_target=module.call_edge(body,'new')
   need(cleanup==ordinary_cleanup and ordinary_target in blocks,
        'shared cleanup call edges differ','AFFECTED_GATE_FAILED')
   label=str(cleanup)
   match=re.search(r'SwitchStmt \(loc "([^"]+)", CallExpr \(loc "[^"]+", "new"',caller)
   loc=re.escape(match.group(1)) if match else '<missing>'
   need(match is not None and
        re.search(r'SwitchStmtClause \(loc "'+loc+r'"[^\n]*"unwinding"[^\n]*GotoStmt \([^\n]*"'+label+r'"',caller) is not None and
        re.search(r'LabelStmt \([^\n]*"'+label+r'"\);\s*ReturnStmt \([^\n]*"unwinding"',caller) is not None,
        'shared cleanup AST lacks concrete unwind arm/return','AFFECTED_GATE_FAILED')
   ordinary_body=module.mir_body(mir,'ordinary_caller')
   ordinary_cont,_=module.call_edge(ordinary_body,'new')
   ordinary_ast=module.ast_body(ast,'ordinary_caller')
   ordinary_switch=re.search(r'SwitchStmt \(loc "([^"]+)", CallExpr \(loc "[^"]+", "new"',ordinary_ast)
   ordinary_loc=re.escape(ordinary_switch.group(1)) if ordinary_switch else '<missing>'
   need(ordinary_cont is None and ordinary_switch is not None and
        re.search(r'SwitchStmtClause \(loc "'+ordinary_loc+r'"[^\n]*"unwinding"[^\n]*ReturnStmt \([^\n]*"unwinding"',ordinary_ast) is not None,
        'ordinary caller AST lacks real unwind return','AFFECTED_GATE_FAILED')
  findings[case]={'cleanup_block':cleanup,'normal_target':target,
                  'mir_sha256':h(mir.encode()),'ast_sha256':h(ast.encode())}
 return findings
def audit(repo,root):
 out={"schema":"verifast-mdnew-fullmake-audit-v1","classification":"INCOMPLETE_EVIDENCE",
      "accepted":False,"base":BASE,"head":HEAD,"tree":TREE}
 try:
  identity=j(root/'source-identity.json'); cert=j(root.parent/'source-input-certificate.json')
  need(cert.get('lane')=='verifast-mdnew-fullmake','source lane differs')
  need(identity['infra_sha']==identity['proof_sha']==cert['infra']['commit']==cert['proof']['commit'],
       'infra/proof source commit differs')
  need(identity['source_input_archive_sha256']==cert['archive_sha256'],'source archive differs')
  infra_paths=cert['infra']['restored_paths'];proof_paths=cert['proof']['restored_paths']
  def bound(rows,rel,expected):
   matches=[r for r in rows if r.get('path')==rel]
   need(len(matches)==1 and matches[0].get('sha256')==expected,
        f'certificate lacks exact restored input {rel}')
  prefix=f'research/challenge-8/verifast-input/{HEAD}/'
  bound(proof_paths,prefix+'bundle',h(read(root/'tool-input.bundle')))
  bound(proof_paths,prefix+'manifest',h(read(root/'tool-input.manifest')))
  rel='research/challenge-8/cloud-build/mdnew-fullmake-audit.py'
  bound(infra_paths,rel,h(read(Path(__file__))))
  manifest=j(root/'tool-input.manifest');restore=j(root/'restore.json')
  need(manifest.get('base_commit')==BASE and manifest.get('candidate_commit')==HEAD and
       manifest.get('candidate_tree')==TREE and manifest.get('candidate_ref')==REF,
       'manifest source identity differs')
  need(h(read(root/'tool-input.bundle'))==manifest['bundle_sha256'],'bundle hash differs')
  need(restore.get('classification')=='RESTORED_GIT_INPUT' and
       restore.get('base_commit')==BASE and restore.get('candidate_commit')==HEAD and
       restore.get('candidate_tree')==TREE and restore.get('candidate_ref')==REF and
       restore.get('bundle_sha256')==manifest['bundle_sha256'] and
       restore.get('manifest_sha256')==h(read(root/'tool-input.manifest')) and
       restore.get('git_identity_preserved') is True,
       'restore receipt differs')
  need(oid(repo,'rev-parse','HEAD')==HEAD and oid(repo,'rev-parse','HEAD^{tree}')==TREE,
       'restored Git head/tree differs')
  for rel,record in manifest['selected_files'].items():
   blob=read(repo/rel)
   need(h(blob)==record['sha256'] and len(blob)==record['bytes'] and
        oid(repo,'rev-parse',f'HEAD:{rel}')==record['git_blob'],
        f'selected source bytes differ: {rel}')
  version=read(root/'rustc.verbose.txt').decode()
  need(f'commit-hash: {RUSTC}' in version,'Rust compiler pin differs')
  need(read(root/'rustc.sysroot.txt').strip(),'Rust compiler sysroot absent')
  for dep in ('vfdeps','stock','rustup','llvm'):
   need(b': OK' in read(root/f'{dep}-sha256.txt'),f'{dep} archive checksum missing')
  pre=j(root/'pre-build-components.json')
  need(pre.get('all_absent_before_build') is True and set(pre.get('removed_stock_binaries',[]))==set(COMPONENTS),
       'old executable may have survived before source build')
  conditional=j(root/'conditional-components.json')
  need(conditional.get('schema')=='verifast-fullmake-conditional-components-v1' and
       conditional.get('assignment_models_directory_present')==(repo/'assignments').is_dir() and
       conditional.get('assignment_models_script_present')==(repo/'assignments/run_model_solutions.mysh').is_file() and
       isinstance(conditional.get('java_ast_server_enabled'),bool) and
       isinstance(conditional.get('rocq_coqc_available'),bool) and
       isinstance(conditional.get('z3_in_path'),bool) and
       isinstance(conditional.get('z3v45_in_path'),bool),
       'conditional dependency receipt incomplete')
  make_code,make_out,make_err=stage(root,'make-test')
  out['make_test']={'exit_status':make_code,'stdout_sha256':h(make_out.encode()),
                    'stderr_sha256':h(make_err.encode()),
                    'failed_process_lines':re.findall(r'(?m)^\d+ failed processes$',make_out),
                    'conditional_skip_lines':re.findall(r'(?m)^SKIP:.*$',make_out),
                    'assignment_models': 'ENABLED' if conditional['assignment_models_directory_present'] else 'SKIPPED_DIRECTORY_ABSENT',
                    'java_frontend': 'ENABLED' if conditional['java_ast_server_enabled'] else 'SKIPPED_ENV_NOT_SET',
                    'rocq': 'AVAILABLE_OPTIONAL_NOT_PART_OF_MAKE_TEST' if conditional['rocq_coqc_available'] else 'NOT_RUN_COMPONENT_ABSENT',
                    'z3_in_path':conditional['z3_in_path']}
  if make_code in (124,137):raise Failure('full make test reached its bounded deadline','INCOMPLETE_TIMEOUT')
  need(make_code==0,f'full make test exited {make_code}','TEST_FAILURE')
  verify_make_completion(make_out)
  post=j(root/'build-components.json')
  need(post.get('make_exit_code')==0 and set(post.get('components',{}))==set(COMPONENTS),
       'source-built component receipt incomplete')
  for name,expected in post['components'].items():
   need(isinstance(expected,str) and re.fullmatch('[0-9a-f]{64}',expected) and
        h(read(repo/'bin'/name))==expected,f'{name} component digest differs')
  reg='tests/rust/testsuite.mysh'; reg_bytes=read(repo/reg)
  need(h(reg_bytes)==manifest['selected_files'][reg]['sha256'],
       'native registration differs from pinned source')
  registration_block=verify_registration(reg_bytes.decode())
  root_suite=read(repo/'testsuite.mysh').decode()
  need(re.search(r'cd rust\s*\n\s*call testsuite\.mysh',root_suite) is not None,
       'root suite does not invoke native Rust tests')
  diagnostic_code,diagnostic_stdout,diagnostic_stderr=stage(root,'dead-diagnostic')
  need(diagnostic_code==1,'dead code control did not exit exactly 1','WRONG_DIAGNOSTIC')
  need('dead_code_pre.rs(1,1-7,2): dead code' in diagnostic_stdout+diagnostic_stderr,
       'negative control lacks exact whole-function dead-code diagnostic','WRONG_DIAGNOSTIC')
  changed=affected(root)
  out.update(classification='FULL_LINUX_MAKE_TEST_PASS',accepted=True,
             provenance={'infra_sha':identity['infra_sha'],'proof_sha':identity['proof_sha'],
                         'bundle_sha256':manifest['bundle_sha256'],
                         'manifest_sha256':h(read(root/'tool-input.manifest')),
                         'rustc_commit':RUSTC,'components':post['components']},
             selected_native={'positive_and_expected_failure_commands':list(COMMANDS),
                              'exact_dead_code_diagnostic':True,
                              'dead_code_exit_status':diagnostic_code,
                              'registration_block_sha256':h(registration_block.encode())},
             affected_structural=changed)
 except Failure as exc:
  out.update(classification=exc.kind,reason=str(exc),accepted=False)
 except Exception as exc:
  out.update(classification='INCOMPLETE_EVIDENCE',reason=f'{type(exc).__name__}: {exc}',accepted=False)
 return out
def main():
 p=argparse.ArgumentParser()
 p.add_argument('repo',type=Path);p.add_argument('root',type=Path)
 p.add_argument('--output',required=True,type=Path)
 p.add_argument('--runner-status',type=int,required=True)
 p.add_argument('--failed-stage',required=True)
 a=p.parse_args(); result=audit(a.repo,a.root)
 result['runner_status']=a.runner_status;result['failed_stage']=a.failed_stage
 if a.runner_status not in (0,):
  result['accepted']=False
  if a.runner_status in (124,137):result['classification']='INCOMPLETE_TIMEOUT'
 a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print(json.dumps(result,sort_keys=True))
 return 0 if result['accepted'] else 2
if __name__=='__main__':raise SystemExit(main())
