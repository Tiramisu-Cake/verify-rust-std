"""Run explicitly selected static/service tests; preserve truthful precursor receipts."""
from pathlib import Path
import datetime,hashlib,json,os,subprocess,sys,time
CONTROL=Path('/root/kani-ch8-s4p-2-r1-control-w13');HERE=CONTROL/'ch8-s1-control'
OUT=Path(__file__).resolve().parent/'tests';OUT.mkdir(exist_ok=True)
tag=sys.argv[1];names=sys.argv[2:];assert names
assert not (OUT/(tag+'.json')).exists()
script='''import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from validate_tokens import cached_tokens
with cached_tokens(('cfg_pfc','s3_cfg_pfc','s32_cfg_pfc','s34_cfg_pfc','s4p_cfg_pfc','s4p2_cfg_pfc')):
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(sys.argv[1:]))
 raise SystemExit(0 if result.wasSuccessful() else 1)
'''
record={'tests':names,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'request_sha256':hashlib.sha256((HERE/'CI-REQUEST.json').read_bytes()).hexdigest(),
 'native_CI':'NOT_RUN','validation_kind':'TARGETED_UNCOMMITTED_PRECURSOR_NOT_FINAL_VALIDATE',
 'working_files_sha256':{str(p.relative_to(CONTROL)):hashlib.sha256(p.read_bytes()).hexdigest() for p in HERE.glob('*.py')}}
start=time.monotonic()
with (OUT/(tag+'.stdout')).open('wb') as stdout,(OUT/(tag+'.stderr')).open('wb') as stderr:
 result=subprocess.run(['python3','-c',script,*names],cwd=HERE,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},stdout=stdout,stderr=stderr)
record.update(exit_code=result.returncode,elapsed_seconds=time.monotonic()-start)
for suffix in ('stdout','stderr'):
 path=OUT/(tag+'.'+suffix);record[suffix]={'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
(OUT/(tag+'.json')).write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({k:v for k,v in record.items() if k!='working_files_sha256'}),flush=True)
raise SystemExit(result.returncode)
