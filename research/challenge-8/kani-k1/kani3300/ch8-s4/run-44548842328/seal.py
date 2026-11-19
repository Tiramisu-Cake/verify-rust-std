#!/usr/bin/env python3
"""Seal/check only this immutable intake directory."""
import hashlib,json,sys
from pathlib import Path
H=Path(__file__).resolve().parent
def entries():
    return {str(p.relative_to(H)):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(H.rglob('*')) if p.is_file() and p.name!='MANIFEST.json' and '__pycache__' not in p.parts}
current=entries()
if '--check' in sys.argv:
    assert json.loads((H/'MANIFEST.json').read_text())['files']==current,'manifest mismatch'
    print(json.dumps({'status':'PASS','files':len(current)}))
else:
    (H/'MANIFEST.json').write_text(json.dumps({'schema':'ch8-postrun-intake-manifest-v1','files':current},indent=2)+'\n')
    print(json.dumps({'status':'SEALED','files':len(current)}))
