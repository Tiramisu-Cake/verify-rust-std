#!/usr/bin/env python3
"""One-shot actual final Validate and check-source; offline/static/synthetic only."""
import datetime,hashlib,json,os,platform,re,subprocess,sys,tempfile,time
from pathlib import Path
H=Path(__file__).resolve().parent;C=Path('/root/kani-ch8-s2-r5-r1-final-w13');S=Path('/root/verify-rust-std-ch8-s2-r4-r1-w13');T=Path('/root/kani-upstream-ch8-s1');Q=C/'ch8-s1-control'
sys.dont_write_bytecode=True;sys.path.insert(0,str(Q));import check_package

def git(repo,*args):return subprocess.check_output(['git','-C',str(repo),*args],text=True).strip()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ids():
    result={}
    for key,repo in [('source',S),('control',C),('tool',T)]:
        assert not git(repo,'status','--porcelain=v1')
        result[key]={'worktree':str(repo),'sha':git(repo,'rev-parse','HEAD'),'tree':git(repo,'rev-parse','HEAD^{tree}'),'parent':git(repo,'rev-parse','HEAD^')}
    result['request_sha256']=sha(Q/'CI-REQUEST.json');result['workflow_sha256']=sha(C/'.github/workflows/ch8-s2.yml')
    return result

def measure(name,command,cwd,env):
    dest=H/(name+'-TIMING.json');assert not dest.exists(), 'One-shot receipt exists; do not rerun'
    provenance=ids();start=time.monotonic_ns();utc=datetime.datetime.now(datetime.timezone.utc).isoformat()
    receipt={'status':'STARTED','command':command,'shell':['bash','--noprofile','--norc','-e','-o','pipefail','-c'], 'cwd':str(cwd),'provenance':provenance,'started_utc':utc,'monotonic_start_ns':start,'environment':{k:env[k] for k in ('PYTHONDONTWRITEBYTECODE','GITHUB_REPOSITORY','GITHUB_EVENT_NAME','GITHUB_REF','GITHUB_RUN_ATTEMPT','GITHUB_SHA','S2_PROFILE')},'host':platform.platform(),'machine_duration_scope':'THIS_MACHINE_ONLY; GitHub future duration UNKNOWN','proof_credit':'NONE'}
    dest.write_text(json.dumps(receipt,indent=2)+'\n')
    proc=subprocess.run(receipt['shell']+[command],cwd=cwd,env=env,capture_output=True,text=True)
    end=time.monotonic_ns();log=H/(name+'.txt');log.write_text(proc.stdout+proc.stderr)
    assert ids()==provenance
    receipt.update(status='PASS' if proc.returncode==0 else 'FAIL',exit_code=proc.returncode,ended_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),monotonic_end_ns=end,elapsed_seconds=(end-start)/1e9,transcript_sha256=sha(log))
    dest.write_text(json.dumps(receipt,indent=2)+'\n')
    print(name,receipt['status'],receipt['elapsed_seconds'],flush=True)
    assert proc.returncode==0,log
    return receipt

identity=ids();env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',GITHUB_REPOSITORY='Tiramisu-Cake/kani',GITHUB_EVENT_NAME='push',GITHUB_REF='refs/heads/uninit-ci/ch8-s2-batch3probes-r5-r1-final-w13',GITHUB_RUN_ATTEMPT='1',GITHUB_SHA=identity['control']['sha'],S2_PROFILE='ch8-s2-r5-isolated-v1')
doc=check_package.load_yaml((C/'.github/workflows/ch8-s2.yml').read_text());steps={s['name']:s for s in doc['jobs']['s2_batch']['steps']}
with tempfile.TemporaryDirectory(prefix='r4-r2-check-source-layout-') as d:
    root=Path(d)
    for name,repo in [('control',C),('export',S),('tool',T)]: (root/name).symlink_to(repo,target_is_directory=True)
    source=measure('COMBINED-CHECK-SOURCE',steps['Check all source identities']['run'],root,env)
validate=measure('COMBINED-FINAL-VALIDATE',steps['Validate control and synthetic wrapper']['run'],Q,env)
transcript=(H/'COMBINED-FINAL-VALIDATE.txt').read_text();match=re.search(r'Ran ([0-9]+) tests in ([0-9.]+)s',transcript);assert match and transcript.endswith('\nOK\n')
(H/'COMBINED-TEST-PROVENANCE.json').write_text(json.dumps({**validate,'test_count':int(match[1]),'unittest_reported_seconds':float(match[2]),'execution_count':1,'check_source_execution_count':1,'native_compile':'NOT_RUN','full_runner':'NOT_RUN','CI':'NOT_RUN','actual_causal_CI_unit':'UNKNOWN'},indent=2)+'\n')
