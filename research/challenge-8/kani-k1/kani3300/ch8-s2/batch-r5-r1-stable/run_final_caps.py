#!/usr/bin/env python3
"""Record narrow final-object cap tests, not a full-suite timing claim."""
import datetime,hashlib,json,os,subprocess,sys,time
from pathlib import Path
H=Path(__file__).resolve().parent;C=Path('/root/kani-ch8-s2-r5-r1-stable-final-w13');Q=C/'ch8-s1-control'
def git(*a):return subprocess.check_output(['git','-C',str(C),*a],text=True).strip()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not (H/'FINAL-CAP-TESTS.json').exists(), 'one targeted final-object run already recorded'
assert not git('status','--porcelain=v1')
argv=[sys.executable,'-m','unittest','-v','final_cap_checks.R5MarginTests',
 'test_s2.S2Tests.test_workflow_caps_types_and_single_serial_job',
 'test_s2.S2Tests.test_timeout_caps_and_order_reject_redistribution',
 'test_s2.S2Tests.test_setup_aggregate_remaining_boundary_without_compiler']
start=time.monotonic_ns();utc=datetime.datetime.now(datetime.timezone.utc).isoformat()
proc=subprocess.run(argv,cwd=H,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),capture_output=True,text=True)
end=time.monotonic_ns();(H/'FINAL-CAP-TESTS.txt').write_text(proc.stdout+proc.stderr)
record={'execution':'TARGETED_CAP_TESTS_ONLY_NEW_OBJECT','control_sha':git('rev-parse','HEAD'),'control_tree':git('rev-parse','HEAD^{tree}'),
 'request_sha256':sha(Q/'CI-REQUEST.json'),'workflow_sha256':sha(C/'.github/workflows/ch8-s2.yml'),
 'argv':argv,'cwd':str(H),'environment':{'PYTHONDONTWRITEBYTECODE':'1'},'started_utc':utc,
 'monotonic_start_ns':start,'monotonic_end_ns':end,'elapsed_seconds':(end-start)/1e9,'exit_code':proc.returncode,
 'test_files_sha256':{'final_cap_checks.py':sha(H/'final_cap_checks.py'),'test_s2.py':sha(Q/'test_s2.py')},
 'transcript_sha256':sha(H/'FINAL-CAP-TESTS.txt'),'full130_suite_on_new_object':'SEPARATELY_MEASURED_COMBINED_FINAL','compiler_CI':'NOT_RUN'}
(H/'FINAL-CAP-TESTS.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2));assert proc.returncode==0
