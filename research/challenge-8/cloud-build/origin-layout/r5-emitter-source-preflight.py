#!/usr/bin/env python3
"""Static R5 emitter patch composition/pins; no extraction, compiler, proof or dispatch."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
TOOL=Path('/root/verifast-merge-actual-glue')
BASE='a42d50becbc84a45e33a58269358eee105f1fdcb'
def sha(b):return hashlib.sha256(b).hexdigest()
def git(*args):return subprocess.check_output(['git','-C',str(TOOL),*args])
def main():
 oldraw=(HERE/'R5-BASELINE-PROFILE-20261020.json').read_bytes()
 assert sha(oldraw)=='77164792cfca039fe8b2a993a198a545a74a074480371dba5f454a5e86709c66'
 old=json.loads(oldraw); raw=(HERE/'GLUE-PROFILE.json').read_bytes();new=json.loads(raw)
 assert new['profile']=='experimental-merge-guard-addressability-emitter-r5-v1' and new['accepted'] is False
 assert new['effective_tool_commit']=='45594fb821805f10c4e05f02912d1ea3bf920e62'
 assert new['ordered_patch_chain'][-1]['path']=='research/challenge-8/cloud-build/origin-layout/r5-deferred-local-emitter.patch'
 assert new['ordered_patch_chain'][-1]['sha256']==new['deferred_local_emitter_patch_sha256']
 assert new['ordered_patch_chain'][:-1]==old['ordered_patch_chain'] and len(new['ordered_patch_chain'])==16
 before=git('show',BASE+':src/verifast.ml');after=git('show',new['effective_tool_commit']+':src/verifast.ml')
 anchor=b'            if not (List.mem_assoc x !block) then block := (x, is_const_var) :: !block;\r\n            let env_tp = match t with StaticArrayType _ -> t | _ -> RefType t in\r\n'
 replacement=anchor.replace(b'            let env_tp',b'            rocq_print_local_addr_taken !address_taken;\r\n            let env_tp')
 assert before.count(anchor)==1 and after==before.replace(anchor,replacement,1)
 assert after.count(b'\r\n')==before.count(b'\r\n')+1 and after==(TOOL/'src/verifast.ml').read_bytes()
 assert git('diff','--name-only',BASE,new['effective_tool_commit']).decode().splitlines()==['src/verifast.ml']
 pins={'src/rust_frontend/vf_mir_exporter/src/lib.rs':'exporter_source_sha256','src/rust_frontend/vf_mir/vf_mir.capnp':'schema_sha256','src/refinement_checker/main.ml':'refiner_main_source_sha256','src/refinement_checker/refinement_checker.ml':'refiner_core_source_sha256','src/rust_frontend/vf_mir_translator/vf_mir_translator.ml':'translator_sha256','src/rust_frontend/vf_mir_translator/rust_parser.ml':'parser_sha256','src/frontend/ast.ml':'ast_sha256','src/frontend/ocaml_expr_of_ast.ml':'emitter_sha256','src/SExpressionEmitter.ml':'sexpression_sha256','src/verifast.ml':'kernel_sha256','src/verifast1.ml':'model_sha256','src/verify_expr.ml':'verify_expr_sha256','bin/rust/prelude_core.rsspec':'prelude_sha256','bin/rust/std/lib.rsspec':'stdlib_sha256'}
 for path,key in pins.items():
  assert sha(git('show',new['effective_tool_commit']+':'+path))==new[key],path
  if path!='src/verifast.ml':assert new[key]==old[key],path
 patches=[];paths=set()
 for row in new['ordered_patch_chain']:
  p=ROOT/row['path'];assert sha(p.read_bytes())==row['sha256'],p;patches.append(p)
  for line in subprocess.check_output(['git','apply','--numstat',str(p)],text=True).splitlines():paths.add(line.split('\t',2)[2])
 with tempfile.TemporaryDirectory(prefix='r4-static-composition-') as temp:
  temp=Path(temp);subprocess.run(['git','init','--quiet',str(temp)],check=True)
  tree=set(git('ls-tree','-r','--name-only',new['verifast_commit']).decode().splitlines())
  for path in paths & tree:
   p=temp/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(git('show',new['verifast_commit']+':'+path))
  for p in patches:
   subprocess.run(['git','-C',str(temp),'-c','core.whitespace=cr-at-eol','apply','--check',str(p)],check=True)
   subprocess.run(['git','-C',str(temp),'-c','core.whitespace=cr-at-eol','apply','--whitespace=error',str(p)],check=True)
  for path in paths:assert (temp/path).read_bytes()==git('show',new['effective_tool_commit']+':'+path),path
 adapter=ROOT/'research/challenge-8/merge/cloud-build/provider-overlays.py'
 fixed=next(ast.literal_eval(x.value) for x in ast.parse(adapter.read_bytes()).body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='FILES' for t in x.targets))
 assert len(fixed)==18
 for path,h in fixed.items():assert sha((ROOT/path).read_bytes())==h,path
 recipe=json.loads((ROOT/'research/challenge-8/cloud-build/recipes/merge.json').read_text())
 assert recipe['proof_paths']==sorted(set(recipe['proof_paths']))
 assert set(fixed)<=set(recipe['proof_paths'])
 for path in recipe['proof_paths']:assert (ROOT/path).is_file(),path
 for path in recipe['proof_paths']:
  if path.endswith('.py'):ast.parse((ROOT/path).read_bytes(),filename=path)
 for path in ['research/challenge-8/merge/overnight/guard-ownership/insertion-onecell/build-profile.sh','research/challenge-8/cloud-build/origin-layout/compile-preflight.sh']:
  subprocess.run(['bash','-n',str(ROOT/path)],check=True)
 # Only pure string overlays, never provider.main or proof preparation.
 spec=importlib.util.spec_from_file_location('r4_pure_overlay',adapter);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 net='research/challenge-8/networks/prove.py';network_sha=m.sha(m.transform(net,(ROOT/net).read_bytes()))
 run='research/challenge-8/merge/overnight/run.sh';staged=m.transform(run,(ROOT/run).read_bytes(),{'network_sha':network_sha},new['profile'])
 assert b'experimental-merge-guard-addressability-emitter-r5-v1' in staged and b'experimental-merge-first-callback-u64-v1' not in staged and b'experimental-merge-guard-addressability-v1' not in staged
 subprocess.run(['bash','-n'],input=staged,check=True)
 report={'schema':'merge-r5-emitter-static-source-preflight-v1','result':'PASS_STATIC_ONLY','tool':new['effective_tool_commit'],'profile_sha256':sha(raw),'verifast_ml_sha256':sha(after),'preserved_patch_count':15,'composed_patch_count':len(patches),'reconstructed_files':len(paths),'source_pin_count':len(pins),'strict_base_pins':len(fixed),'unchanged_run_sh_sha256':fixed[run],'staged_run_sha256':sha(staged),'compiler_or_extractor_or_proof_executed':False}
 (HERE/'R5-EMITTER-SOURCE-PREFLIGHT-20261020.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
