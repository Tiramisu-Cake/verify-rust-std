from pathlib import Path
import importlib.util,sys,shutil,tempfile,json,hashlib
repo=Path(sys.argv[1]);root=Path(sys.argv[2])
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
span=load('span_replay',repo/'research/challenge-8/cloud-build/incoming-span-lifetime/controls/run.py')
origin=load('origin_replay',repo/'research/challenge-8/cloud-build/incoming-origin/controls/run.py')
rows={}
with tempfile.TemporaryDirectory(prefix='origin-classifier-replay-') as tmp:
 for p in sorted((root/'controls').iterdir()):
  if not (p/'classification.json').exists():continue
  saved=json.loads((p/'classification.json').read_text());case=Path(tmp)/p.name;shutil.copytree(p,case)
  if p.name.startswith('span_'):got=span.classify(p.name,case,saved,saved)
  else:got=origin.classify(p.name,case,saved,saved)
  assert got['classification']==saved['classification'],p.name
  rows[p.name]=got['classification']
 case=Path(tmp)/'span_retired_local_reuse';ast=case/'proof-ast.ml';raw=ast.read_text();ast.write_text(raw.replace('RustStorageDeadStmt','CallExpr').replace('RustStorageLiveStmt','CallExpr'))
 rejected=span.retired_mir_ast_gate(case);assert rejected['admitted'] is False,rejected
out={'schema':'incoming-origin-saved-classifier-replay-v1','credit':'service classifier replay only; no compiler, extraction, verifier or fresh proof','cases':rows,'legacy_CallExpr_gate':rejected,'all_classifications_identical':True,'origin_gate_status':'OPEN: Rust extern cases stop before target and normal/unwind case lacks resource','tool_commit':'6cb7b6736c4ef7978d2f3a80737952ac7148cccb'}
print(json.dumps(out,indent=2))
