#!/usr/bin/env python3
"""Hash the exact owned packet; check mode is read-only."""
import hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 files={p.name:{'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in sorted(HERE.iterdir()) if p.is_file() and p.name!='MANIFEST.json'}
 assert not any(p.is_dir() or p.is_symlink() for p in HERE.iterdir()),'unexpected nested directory/symlink'
 m={'schema':'s4p-terminal-immutable-manifest-v1','status':'READY','files':files,'excluded':['MANIFEST.json'],'identity':'Exact containing Git commit covers this manifest; full SHA returned to root','scope':'Own run44481580554 directory only; no evidence/admission/policy changes'}
 if '--check' in sys.argv:assert json.loads((HERE/'MANIFEST.json').read_text())==m
 else:(HERE/'MANIFEST.json').write_text(json.dumps(m,indent=2)+'\n')
 print(json.dumps({'manifest':'PASS','files':len(files),'mode':'check' if '--check' in sys.argv else 'seal'}))
if __name__=='__main__':main()
