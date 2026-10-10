#!/usr/bin/env python3
"""Lightweight Git/text replay of the exact Cloud source chain; no compiler/proof."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[4]
ONE = ROOT / 'research/challenge-8/merge/overnight/guard-ownership/insertion-onecell'
LAYOUT = Path(__file__).resolve().parent
BASE = 'f76012fb518703b1d98e243ac4f487f16877cfcb'
SOURCES = {
 'src/rust_frontend/vf_mir_translator/vf_mir_translator.ml':'translator_sha256',
 'src/frontend/ocaml_expr_of_ast.ml':'emitter_sha256',
 'src/verifast.ml':'kernel_sha256', 'src/verifast1.ml':'model_sha256',
 'src/frontend/ast.ml':'ast_sha256', 'src/SExpressionEmitter.ml':'sexpression_sha256',
 'src/verify_expr.ml':'verify_expr_sha256',
 'src/rust_frontend/vf_mir_exporter/src/lib.rs':'exporter_source_sha256',
 'src/rust_frontend/vf_mir/vf_mir.capnp':'schema_sha256',
 'src/rust_frontend/vf_mir_translator/rust_parser.ml':'parser_sha256',
 'bin/rust/prelude_core.rsspec':'prelude_sha256', 'bin/rust/std/lib.rsspec':'stdlib_sha256',
}

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--git-source',type=Path,required=True)
 p.add_argument('--output',type=Path,required=True)
 a=p.parse_args()
 if a.output.exists():raise SystemExit('refusing to reuse source replay directory')
 pins=json.loads((ONE/'PROFILE.json').read_text())
 assert pins['verifast_commit']==BASE and pins['accepted'] is False
 overnight=ONE.parents[1]
 patches=[overnight/(name+'.patch') for name in
          ('wrapping','callback','copy','cleanup','usize-multiple','stack-address')]
 patches += [ONE/'tracked-md.patch',ONE/'allocation-span.patch',LAYOUT/'unit-layout.patch',LAYOUT/'guard-layout.patch']
 patch_pins={'tracked-md.patch':'patch_sha256','allocation-span.patch':'allocation_span_patch_sha256',
             'unit-layout.patch':'unit_layout_patch_sha256','guard-layout.patch':'guard_layout_patch_sha256'}
 paths=set(SOURCES)
 for patch in patches:
  for line in patch.read_text().splitlines():
   if line.startswith('--- a/'):paths.add(line[6:])
  if patch.name in patch_pins:assert hashlib.sha256(patch.read_bytes()).hexdigest()==pins[patch_pins[patch.name]]
 a.output.mkdir(parents=True)
 for rel in paths:
  assert not Path(rel).is_absolute() and '..' not in Path(rel).parts
  r=subprocess.run(['git','-C',str(a.git_source),'show',BASE+':'+rel],capture_output=True)
  if r.returncode==0:
   target=a.output/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(r.stdout)
 subprocess.run(['git','init','-q',str(a.output)],check=True)
 patch_receipts=[]
 for i,patch in enumerate(patches):
  subprocess.run(['git','-C',str(a.output),'-c','core.whitespace=cr-at-eol','apply','--whitespace=error',str(patch)],check=True)
  patch_receipts.append({'path':str(patch.relative_to(ROOT)),'sha256':hashlib.sha256(patch.read_bytes()).hexdigest()})
  if i==5:
   for rel,key in [('src/rust_frontend/vf_mir_translator/vf_mir_translator.ml','baseline_translator_sha256'),
                   ('src/verifast.ml','baseline_kernel_sha256'),('src/verifast1.ml','model_baseline_sha256'),
                   ('src/frontend/ocaml_expr_of_ast.ml','baseline_emitter_sha256')]:
    assert hashlib.sha256((a.output/rel).read_bytes()).hexdigest()==pins[key],(rel,key)
 sources={rel:hashlib.sha256((a.output/rel).read_bytes()).hexdigest() for rel in SOURCES}
 mismatches={rel:{'actual':sources[rel],'expected':pins[key]} for rel,key in SOURCES.items() if sources[rel]!=pins[key]}
 receipt={'schema':'merge-effective-source-replay-v1','base_commit':BASE,'component_commit':pins['guard_layout_tool_commit'],
          'profile_sha256':hashlib.sha256((ONE/'PROFILE.json').read_bytes()).hexdigest(),
          'ordered_patches':patch_receipts,'source_sha256':sources,'mismatches':mismatches,
          'compiler_attempted':False,'proof_attempted':False,'accepted':False,
          'classification':'PASS_TEXT_REPLAY_ONLY' if not mismatches else 'PIN_MISMATCH'}
 (a.output/'source-replay.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print(json.dumps({'classification':receipt['classification'],'mismatches':mismatches}))
 return int(bool(mismatches))

if __name__=='__main__':raise SystemExit(main())
