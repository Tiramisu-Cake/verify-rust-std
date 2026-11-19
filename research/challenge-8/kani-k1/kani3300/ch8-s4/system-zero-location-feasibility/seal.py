#!/usr/bin/env python3
"""Seal/check only this source-only investigation packet."""
import hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 assert all(p.is_file() and not p.is_symlink() for p in HERE.iterdir())
 files={p.name:{'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in sorted(HERE.iterdir()) if p.name!='MANIFEST.json'}
 m={'schema':'system-zero-feasibility-manifest-v1','status':'READY','files':files,'excluded':['MANIFEST.json'],'identity':'Exact containing Git commit covers the manifest; full SHA returned to root','scope':'Source-only5-case investigation; no common rule applied'}
 if '--check' in sys.argv:assert json.loads((HERE/'MANIFEST.json').read_text())==m
 else:(HERE/'MANIFEST.json').write_text(json.dumps(m,indent=2)+'\n')
 print(json.dumps({'manifest':'PASS','files':len(files),'mode':'check' if '--check' in sys.argv else 'seal'}))
if __name__=='__main__':main()
