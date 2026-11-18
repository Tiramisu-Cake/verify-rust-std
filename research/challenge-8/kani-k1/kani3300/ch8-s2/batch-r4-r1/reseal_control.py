#!/usr/bin/env python3
"""Rebind candidate metadata; no compilation, network or dispatch."""
import hashlib,json,subprocess,sys
from pathlib import Path
S=Path('/root/verify-rust-std-ch8-s2-r4-r1-w13')
C=Path('/root/kani-ch8-s2-r4-r1-w13');Q=C/'ch8-s1-control'
sys.dont_write_bytecode=True;sys.path.insert(0,str(Q))
import lexical_bindings as l

def git(repo,*args):return subprocess.check_output(['git','-C',str(repo),*args],text=True).strip()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
source=git(S,'rev-parse','HEAD');tree=git(S,'rev-parse','HEAD^{tree}')
previous=json.loads((Q/'CI-REQUEST.json').read_text())
p=Q/'runner.py';text=p.read_text().replace(previous['std_sha'],source).replace(previous['std_tree'],tree).replace('16aa3557742e1b8a8b64b3b3d49da23d988027f8',source).replace('135f4549d1e8d6f69f1935c817f4c42bb917b756',tree);p.write_text(text)
p=Q/'CI-REQUEST.json';r=json.loads(p.read_text());oldhash=r['changed_file_sha256'][l.BATCH]
text=p.read_text().replace(r['std_sha'],source).replace(r['std_tree'],tree).replace(oldhash,sha(S/l.BATCH));r=json.loads(text)
r['entry_g0']='cf40e805eb47a5f11efdf27a62b06caf2bc2adff'
r['control_reference']='db81e62d76cfa193b1d7fe8e8ebbecead7e20ef8'
r.pop('lexical_source_sha256',None)
doc=l.check(S,r);r['lexical_source_sha256']=doc['source_files_sha256']
p=Q/'S2-SOURCE.json';sources=json.loads(p.read_text())
for rel in set(sources)|set(doc['source_files_sha256']):sources[rel]=(S/rel).read_text()
dump(p,sources)
paths=set(git(C,'diff','--name-only',r['tool_sha']).splitlines())
paths.update(git(C,'ls-files','--others','--exclude-standard').splitlines())
r['ci_changed_paths']=sorted(paths)
r['ci_payload_sha256']={p:sha(C/p) for p in sorted(paths) if (C/p).is_file() and p!='ch8-s1-control/CI-REQUEST.json'}
dump(Q/'CI-REQUEST.json',r)
print(json.dumps({'source':source,'tree':tree,'request_sha256':sha(Q/'CI-REQUEST.json'),'lexical_provider_files':len(doc['source_files_sha256'])}))
