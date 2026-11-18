#!/usr/bin/env python3
"""One local execution of the exact final workflow Validate commands; no CI."""
import datetime,hashlib,json,os,subprocess,sys,time
from pathlib import Path
OUT=Path(__file__).resolve().parent/'validation-final'
OUT.mkdir(exist_ok=True)
CONTROL=Path('/root/kani-ch8-s3-1-final-control-w13');HERE=CONTROL/'ch8-s1-control'
SOURCE=Path('/root/verify-rust-std-ch8-s3-1-final-w13')

def git(repo,*args):return subprocess.check_output(['git','-C',str(repo),*args],text=True).strip()
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()

def main():
    record=OUT/'FINAL-VALIDATE.json'
    if record.exists():raise RuntimeError('final Validate already invoked; no automatic reexecution')
    req=json.loads((HERE/'CI-REQUEST.json').read_text())
    control_sha=git(CONTROL,'rev-parse','HEAD');source_sha=git(SOURCE,'rev-parse','HEAD')
    assert control_sha=='1dfc267b66abd83d536eb41a17052a4f3d767d2b' and source_sha==req['std_sha']
    assert not git(CONTROL,'status','--porcelain=v1') and not git(SOURCE,'status','--porcelain=v1')
    steps=[['python3','check_package.py','control','--repo','..'],['python3','s3_validate.py']]
    doc={'schema':'ch8-s3-final-validate-provenance-v1','state':'IN_PROGRESS','execution_count':1,
        'started_utc':utc(),'control_sha':control_sha,'control_tree':git(CONTROL,'rev-parse','HEAD^{tree}'),
        'source_sha':source_sha,'source_tree':git(SOURCE,'rev-parse','HEAD^{tree}'),
        'request_sha256':sha(HERE/'CI-REQUEST.json'),'workflow_sha256':sha(CONTROL/'.github/workflows/ch8-s2.yml'),
        'script_sha256':sha(Path(__file__)),'commands':steps,'cwd':str(HERE),'step_cap_seconds':1080,
        'scope':'EXACT_FINAL_LOCAL_STATIC_VALIDATE_WITH_SYNTHETIC_CI_METADATA; not a CI run',
        'native_compile':'NOT_RUN','Kani_CBMC':'NOT_RUN','full_native_runner':'NOT_RUN','CI':'NOT_RUN','proof_credit':'NONE'}
    record.write_text(json.dumps(doc,indent=2)+'\n')
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',GITHUB_REPOSITORY='Tiramisu-Cake/kani',GITHUB_EVENT_NAME='push',
        GITHUB_REF='refs/heads/uninit-ci/ch8-s3-1-LOCAL_STATIC_ONLY',GITHUB_RUN_ATTEMPT='1',GITHUB_SHA=control_sha)
    start=time.monotonic_ns();doc['monotonic_start_ns']=start;results=[]
    with (OUT/'FINAL-VALIDATE.stdout.txt').open('xb') as stdout,(OUT/'FINAL-VALIDATE.stderr.txt').open('xb') as stderr:
        for command in steps:
            child_start=time.monotonic();remaining=1080-(time.monotonic_ns()-start)/1e9
            try:
                result=subprocess.run(command,cwd=HERE,env=env,stdout=stdout,stderr=stderr,timeout=remaining)
                code=result.returncode
            except subprocess.TimeoutExpired:code=124
            results.append({'argv':command,'exit_code':code,'elapsed_seconds':time.monotonic()-child_start})
            if code:break
    end=time.monotonic_ns();elapsed=(end-start)/1e9
    doc.update(ended_utc=utc(),monotonic_end_ns=end,elapsed_seconds=elapsed,commands_executed=results,
        state='PASS' if len(results)==2 and all(x['exit_code']==0 for x in results) else 'FAIL',
        margin=1080/elapsed,required_margin=1.5,margin_pass=1080/elapsed>=1.5,
        stdout_sha256=sha(OUT/'FINAL-VALIDATE.stdout.txt'),stderr_sha256=sha(OUT/'FINAL-VALIDATE.stderr.txt'))
    assert git(CONTROL,'rev-parse','HEAD')==control_sha and sha(HERE/'CI-REQUEST.json')==doc['request_sha256']
    record.write_text(json.dumps(doc,indent=2)+'\n')
    print(json.dumps({'state':doc['state'],'elapsed_seconds':elapsed,'margin':doc['margin']}))
    return 0 if doc['state']=='PASS' and doc['margin_pass'] else 1
if __name__=='__main__':raise SystemExit(main())
