#!/usr/bin/env python3
"""Frozen-source preflight through the actual static reader; no native tools."""
import hashlib,json,subprocess,sys,time
from pathlib import Path
OUT=Path(__file__).resolve().parent
CONTROL=Path('/root/kani-ch8-s3-1-r2-control-w13');HERE=CONTROL/'ch8-s1-control'
SOURCE=Path('/root/verify-rust-std-ch8-s3-1-final-w13');TOOL=Path('/root/kani-upstream-ch8-s1')
sys.path.insert(0,str(HERE))
import runner as r

def main():
    target=OUT/'SOURCE-GATES.json'
    if target.exists():raise RuntimeError('source preflight already recorded')
    sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
    assert r.git(CONTROL,'rev-parse','HEAD')=='cb63033ffcde918f4341146e56373476b8eeb569'
    assert not r.git(CONTROL,'status','--porcelain=v1')
    request=r.load_request();start=time.monotonic();source=r.verify_source(SOURCE,TOOL,request,prebuild=True)
    doc={'state':'STATIC_PASS','method':'actual runner.verify_source(prebuild=True); no compiler/expansion','elapsed_seconds':time.monotonic()-start,
         'source':source,'control_sha':r.git(CONTROL,'rev-parse','HEAD'),'control_tree':r.git(CONTROL,'rev-parse','HEAD^{tree}'),
         'request_sha256':sha(r.REQUEST_PATH),'workflow_sha256':sha(CONTROL/'.github/workflows/ch8-s2.yml'),
         'source_gate_files':{p.name:sha(p) for p in sorted(HERE.glob('s3_*.py'))},'native':'NOT_RUN','proof_credit':'NONE'}
    target.write_text(json.dumps(doc,indent=2)+'\n');print(json.dumps({'state':doc['state'],'elapsed_seconds':doc['elapsed_seconds']}))
if __name__=='__main__':main()
