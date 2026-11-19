"""Root-authorized single execution of the exact prepared offline Validate."""
from pathlib import Path
import datetime,hashlib,json,os,re,subprocess,time
OUT=Path(__file__).resolve().parent
PREP=json.loads((OUT/'FROZEN-VALIDATE.json').read_text())
ROOT=json.loads((OUT/'ROOT-RECHECK.json').read_text());PINS=ROOT['pins']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def identities():
 out={}
 for name in ('source','control','tool'):
  p=PINS[name];r=Path(p['repo'])
  fields=subprocess.check_output(['git','show','-s','--format=%H%n%T%n%P','HEAD'],cwd=r,text=True).splitlines()
  assert fields==[p['sha'],p['tree'],p['sole_parent']],name
  assert not subprocess.check_output(['git','status','--porcelain'],cwd=r,text=True).strip(),name
  out[name]={'head':fields[0],'tree':fields[1],'sole_parent':fields[2],'clean':True}
 c=Path(PINS['control']['repo'])
 assert sha(c/'ch8-s1-control/CI-REQUEST.json')==PREP['request_sha256']
 assert sha(c/'.github/workflows/ch8-s2.yml')==PREP['workflow_sha256']
 return out
before=identities()
assert PREP['execution_count']==0 and PREP['status']=='PREPARED_NOT_RUN'
assert PREP['deadline_seconds']==1080 and PREP['margin_required']==1.5
with (OUT/'EXECUTION-COUNT.json').open('x') as f:json.dump({'execution_count':1,'frozen_prepared_count':0,'authority':'Coordinator explicitly authorized root host final Validate after exact review0c2784fabe; one execution only'},f,indent=2)
start_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()
(OUT/'FINAL-VALIDATE-RUNNING.json').write_text(json.dumps({'status':'RUNNING','execution_count':1,'pid':os.getpid(),'started_at':start_utc,'command':PREP['command'],'cwd':PREP['cwd'],'control':PINS['control'],'script_sha256':sha(Path(PREP['cwd'])/'s4p2r2_validate.py')},indent=2)+'\n')
start=time.monotonic()
with (OUT/'final-validate.stdout').open('wb') as stdout,(OUT/'final-validate.stderr').open('wb') as stderr:
 result=subprocess.run(PREP['command'],cwd=PREP['cwd'],stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr)
elapsed=time.monotonic()-start
finished=datetime.datetime.now(datetime.timezone.utc).isoformat()
records=[]
for line in (OUT/'final-validate.stdout').read_text(errors='replace').splitlines():
 try:
  value=json.loads(line)
  if value.get('schema')=='ch8-s4p-2r2-validate-v1':records.append(value)
 except (ValueError,AttributeError):pass
problems=[]
try:after=identities()
except Exception as e:after={'identity_error':str(e)};problems.append('Post-execution identity/clean gate failed')
if len(records)!=1:problems.append('Expected one final structured Validate result')
summary=records[0] if len(records)==1 else {}
expected={'legacy':136,'s3':56,'s32':35,'bridge1':40,'s4p':38,'s4p2':39,'s4p2r2':22}
for key,value in [('control_sha',PINS['control']['sha']),('control_tree',PINS['control']['tree']),('request_sha256',PREP['request_sha256']),('test_counts',expected),('failures',0),('errors',0),('success',True)]:
 if summary.get(key)!=value:problems.append('Final result mismatch: '+key)
if result.returncode!=0:problems.append('Frozen command exit '+str(result.returncode))
if elapsed>720:problems.append('Outer elapsed margin below1.5')
receipt={'schema':'root-network-r2-final-validate-receipt-v1','status':'PASS' if not problems else 'FAILED_GATE','execution_count':1,'prepared_execution_count_retained':0,'package_commit':ROOT['package'],'review_commit':ROOT['exact_review'],'started_at':start_utc,'finished_at':finished,'command':PREP['command'],'cwd':PREP['cwd'],'exit_code':result.returncode,'outer_elapsed_seconds':elapsed,'deadline_seconds':1080,'margin_required':1.5,'outer_margin':1080/elapsed,'internal_result':summary,'before':before,'after':after,'stdout':{'sha256':sha(OUT/'final-validate.stdout'),'bytes':(OUT/'final-validate.stdout').stat().st_size},'stderr':{'sha256':sha(OUT/'final-validate.stderr'),'bytes':(OUT/'final-validate.stderr').stat().st_size},'frozen_descriptor_sha256':sha(OUT/'FROZEN-VALIDATE.json'),'validate_script_sha256':sha(Path(PREP['cwd'])/'s4p2r2_validate.py'),'problems':problems,'native_compile_proof_cost_fit':'NOT_RUN','CI_push_accounting':False}
(OUT/'FINAL-VALIDATE-RESULT.json').write_text(json.dumps(receipt,indent=2)+'\n')
(OUT/'FINAL-VALIDATE-RUNNING.json').unlink()
print(json.dumps({k:receipt[k] for k in ['status','exit_code','outer_elapsed_seconds','outer_margin','problems']},sort_keys=True),flush=True)
raise SystemExit(0 if not problems else 1)
