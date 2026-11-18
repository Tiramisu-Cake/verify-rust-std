#!/usr/bin/env python3
"""Bounded real-writer regressions against candidate and frozen Git blobs."""
import datetime,hashlib,json,os,subprocess,tempfile,time
from pathlib import Path
OUT=Path(__file__).resolve().parent
CONTROL=Path('/root/kani-ch8-s3-1-r2-control-w13')
FROZEN='fc29b93b1e333b73e55e2872701c80d9927f3b02'
def sha(data):return hashlib.sha256(data).hexdigest()
def git(*args):return subprocess.check_output(['git','-C',str(CONTROL),*args])
def main():
    record=OUT/'TARGETED.json'
    if record.exists():raise RuntimeError('targeted record exists')
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');results=[]
    command=['python3','-m','unittest','-v','test_s3_paths','test_s3_repair'];start=time.monotonic()
    with (OUT/'TARGETED.stdout.txt').open('xb') as out,(OUT/'TARGETED.stderr.txt').open('xb') as err:
        result=subprocess.run(command,cwd=CONTROL/'ch8-s1-control',env=env,stdout=out,stderr=err,timeout=180)
    results.append({'argv':command,'exit':result.returncode,'elapsed_seconds':time.monotonic()-start})
    assert result.returncode==0
    names=git('ls-tree','-r','--name-only',FROZEN,'ch8-s1-control','.github/workflows/ch8-s2.yml').decode().splitlines();closure={}
    with tempfile.TemporaryDirectory() as d:
        root=Path(d)
        for name in names:
            data=git('show',FROZEN+':'+name);path=root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data);closure[name]=sha(data)
        test=(CONTROL/'ch8-s1-control/test_s3_paths.py').read_bytes();(root/'ch8-s1-control/test_s3_paths.py').write_bytes(test)
        command=['python3','-m','unittest','-v','test_s3_paths.RealPathWriterTests.test_workflow_relative_entry_real_writer_and_portable_replay'];start=time.monotonic()
        with (OUT/'FROZEN-DEFECT.stdout.txt').open('xb') as out,(OUT/'FROZEN-DEFECT.stderr.txt').open('xb') as err:
            result=subprocess.run(command,cwd=root/'ch8-s1-control',env=env,stdout=out,stderr=err,timeout=60)
        error=(OUT/'FROZEN-DEFECT.stderr.txt').read_text()
        assert result.returncode==1 and 'recorded worker binary drift: before' in error
        results.append({'argv':command,'exit':result.returncode,'expected':'workflow-shaped rejection: recorded worker binary drift: before','elapsed_seconds':time.monotonic()-start,'frozen_closure_sha256':closure})
    doc={'state':'PASS','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'commands':results,'frozen_control':FROZEN,'fixture_sha256':sha(test),'native':'NOT_RUN','proof_credit':0,'historical_artifact_transformed':False}
    record.write_text(json.dumps(doc,indent=2)+'\n');print(json.dumps({'state':'PASS','commands':[(x['exit'],x['elapsed_seconds']) for x in results]}))
if __name__=='__main__':main()
