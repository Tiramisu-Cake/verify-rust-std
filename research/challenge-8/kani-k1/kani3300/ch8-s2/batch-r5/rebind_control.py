#!/usr/bin/env python3
"""Exact payload rebind; no source edits, compiler, publication or dispatch."""
import hashlib,json,subprocess
from pathlib import Path
C=Path('/root/kani-ch8-s2-r5-package-w13');Q=C/'ch8-s1-control'
def git(*args):return subprocess.check_output(['git','-C',str(C),*args],text=True).strip()
r=json.loads((Q/'CI-REQUEST.json').read_text())
paths=sorted(set(git('diff','--name-only',r['tool_sha']).splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines()))
r['ci_changed_paths']=paths
r['ci_payload_sha256']={p:hashlib.sha256((C/p).read_bytes()).hexdigest() for p in paths if (C/p).is_file() and p!='ch8-s1-control/CI-REQUEST.json'}
(Q/'CI-REQUEST.json').write_text(json.dumps(r,indent=2)+'\n')
print('Rebound',len(paths),'stock-relative paths;',len(r['ci_payload_sha256']),'payload hashes')
