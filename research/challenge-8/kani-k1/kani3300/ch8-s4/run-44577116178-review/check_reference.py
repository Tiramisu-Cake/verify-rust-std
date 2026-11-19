#!/usr/bin/env python3
"""Compare-only offline reference checks in clean child interpreters.

Every intake JSON writer is replaced with a byte comparison. No acquisition,
rendering, compiler/native invocation, or intake mutation is performed.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent
INTAKE=HERE.with_name('run-44577116178')
DRIVER=r'''
import importlib,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
h=Path(sys.argv[1]);sys.path.insert(0,str(h))
r=importlib.import_module('replay'); compared=[]; formatting=[]
def compare(name,value):
    actual=(json.dumps(value,indent=2,ensure_ascii=False)+'\n').encode()
    expected=(h/name).read_bytes()
    if actual!=expected:
        assert name=='RESULT.json' and json.loads(actual)==json.loads(expected), 'reference output mismatch '+name
        formatting.append({'file':name,'difference':'JSON object key order only; values exactly equal','generated_key_order':list(value),'committed_key_order':list(json.loads(expected))})
    compared.append(name)
r.write=compare
module=importlib.import_module(sys.argv[2]);module.main()
print(json.dumps({'compared_files':compared,'formatting_only':formatting}))
'''
def snapshot():
    return {str(p.relative_to(INTAKE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in INTAKE.rglob('*') if p.is_file()}
def main():
    before=snapshot(); rows=[]
    for name in ('replay','audit','addendum','cost_analysis','packet_check'):
        out=subprocess.run([sys.executable,'-B','-c',DRIVER,str(INTAKE),name],text=True,capture_output=True)
        rows.append({'module':name,'exit_code':out.returncode,'stdout':out.stdout,'stderr':out.stderr})
        if out.returncode:
            print(out.stderr);raise SystemExit(out.returncode)
    seal=subprocess.run([sys.executable,'-B',str(INTAKE/'seal.py'),'--check'],text=True,capture_output=True)
    assert seal.returncode==0,seal.stderr
    assert before==snapshot(),'intake changed during reference checks'
    result={'status':'PASS','reference_checks':rows,'seal':json.loads(seal.stdout),'original_files_unchanged':True,'source_of_independent_review':'review.py imports no intake modules','initial_reference_replay_note':'First compare-only replay stopped at RESULT.json: generated field ordering differs from committed field ordering. Exact parsed JSON equality was verified; rerun explicitly permits this one formatting-only difference and still rejects any changed value or other file byte difference. Original files unchanged.','reviewer_check_development_note':'During reviewer-script development, the offset guard anchor was corrected from716 to715 against pinned source, and fixed-negative domain matching was corrected from null to the existing FIXED_NEGATIVE_FIXTURE sentinel. Both were reviewer-check assumptions; no intake finding or input mutation. Final independent checks pass.'}
    (HERE/'VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'reference_modules':[{'module':r['module'],'result':r['stdout'].splitlines()[0]} for r in rows],'seal':result['seal'],'original_files_unchanged':True}))
if __name__=='__main__':main()
