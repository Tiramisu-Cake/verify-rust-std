"""Run the exact committed workflow Validate command ONCE, never native tooling."""
import datetime,hashlib,json,os,subprocess,time
from pathlib import Path
CONTROL=Path('/root/kani-ch8-s4p-1-r1-control-w13');HERE=CONTROL/'ch8-s1-control'
OUT=Path('/root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/kani3300/ch8-s4/s4p-1-r1')
def git(*args):return subprocess.check_output(['git','-C',str(CONTROL),*args],text=True).strip()
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
assert not (OUT/'FINAL-VALIDATE.json').exists(), 'No repeated final Validate'
assert not git('status','--porcelain=v1')
sha=git('rev-parse','HEAD');tree=git('rev-parse','HEAD^{tree}')
assert git('show','-s','--format=%P','HEAD')=='9e14e033f9ee31522b571c127609dcdff76d230b'
import sys
sys.path.insert(0,str(HERE));import check_package
workflow=check_package.load_yaml((CONTROL/'.github/workflows/ch8-s2.yml').read_text())
step=next(x for x in workflow['jobs']['s3_leaf']['steps'] if x['name']=='Validate control and synthetic wrapper')
assert step['timeout-minutes']==18
command=step['run'];assert command=='python3 check_package.py control --repo ..\npython3 s4p_validate.py\n'
env={'PYTHONDONTWRITEBYTECODE':'1','GITHUB_REPOSITORY':'Tiramisu-Cake/kani','GITHUB_EVENT_NAME':'push',
    'GITHUB_REF':'refs/heads/uninit-ci/ch8-s4p-offline-validation-r1','GITHUB_RUN_ATTEMPT':'1','GITHUB_SHA':sha}
record={'command':command,'cwd':str(HERE),'argv':['bash','-e','-c',command],
    'control_sha':sha,'control_tree':tree,'request_sha256':digest(HERE/'CI-REQUEST.json'),
    'workflow_sha256':digest(CONTROL/'.github/workflows/ch8-s2.yml'),'script_sha256':digest(HERE/'s4p_validate.py'),
    'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'limit_seconds':1080,'required_margin':1.5,
    'execution_count':1,'environment_kind':'OFFLINE_SYNTHETIC_GITHUB_STATIC_GATE_CONTEXT; no CI event or run','environment':env,
    'native_compile_proof_cost_fit':'NOT_RUN','proof_credit':'NONE'}
(OUT/'FINAL-VALIDATE.json').write_text(json.dumps({**record,'status':'RUNNING'},indent=2)+'\n')
started=time.monotonic();timed_out=False
with (OUT/'FINAL-VALIDATE.stdout').open('wb') as stdout,(OUT/'FINAL-VALIDATE.stderr').open('wb') as stderr:
    try:result=subprocess.run(record['argv'],cwd=HERE,env={**os.environ,**env},stdout=stdout,stderr=stderr,timeout=1080);code=result.returncode
    except subprocess.TimeoutExpired:timed_out=True;code=124
record.update(exit_code=code,timed_out=timed_out,elapsed_seconds=time.monotonic()-started,
    finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),clean_after=not git('status','--porcelain=v1'))
record['margin_at_18_minutes']=1080/record['elapsed_seconds']
for label in ('stdout','stderr'):
    path=OUT/('FINAL-VALIDATE.'+label);record[label]={'file':path.name,'bytes':path.stat().st_size,'sha256':digest(path)}
assert git('rev-parse','HEAD')==sha and git('rev-parse','HEAD^{tree}')==tree
(OUT/'FINAL-VALIDATE.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record),flush=True)
raise SystemExit(code if code else 0 if record['margin_at_18_minutes']>=1.5 else 1)
