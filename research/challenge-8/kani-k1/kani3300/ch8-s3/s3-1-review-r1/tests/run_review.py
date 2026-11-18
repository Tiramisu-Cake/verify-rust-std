import datetime,hashlib,json,os,subprocess,sys,time
from pathlib import Path
OUT=Path(__file__).resolve().parent;CONTROL=Path('/root/kani-ch8-s3-1-r1-control-w13');HERE=CONTROL/'ch8-s1-control'
args=[sys.executable,'-m','unittest','-v','test_s3_repair','test_s3.CampaignTests','test_s3.SingletonRunnerTests','test_s3.PortableReplayTests','test_delta14']
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONPATH=str(HERE)+':'+str(OUT))
record={'schema':'independent14-delta-test-execution-v1','state':'RUNNING','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'argv':args,'cwd':str(HERE),'control_sha':subprocess.check_output(['git','-C',str(CONTROL),'rev-parse','HEAD'],text=True).strip(),'scope':'Python synthetic/static service tests only','native':'NOT_RUN','full_validate_rerun':False,'proof_credit':'NONE'}
path=OUT/'review-execution.json'
assert not path.exists();path.write_text(json.dumps(record,indent=2)+'\n')
start=time.monotonic_ns()
with (OUT/'review.stdout.txt').open('xb') as stdout,(OUT/'review.stderr.txt').open('xb') as stderr:
    done=subprocess.run(args,cwd=HERE,env=env,stdout=stdout,stderr=stderr,timeout=300)
end=time.monotonic_ns();record.update(state='PASS' if done.returncode==0 else 'FAIL',exit_code=done.returncode,monotonic_start_ns=start,monotonic_end_ns=end,elapsed_seconds=(end-start)/1e9,ended_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
record['artifacts']={name:hashlib.sha256((OUT/name).read_bytes()).hexdigest() for name in ('review.stdout.txt','review.stderr.txt','test_delta14.py','run_review.py')}
path.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2));raise SystemExit(done.returncode)
