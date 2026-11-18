#!/usr/bin/env python3
"""Run only bounded R5/cap service tests, retaining exact provenance."""
import datetime, hashlib, json, os, subprocess, sys, time
from pathlib import Path
HERE=Path(__file__).resolve().parent
PACKET=HERE.with_name('batch-r5-r1')
P=json.loads((PACKET/'PINS.json').read_text())
Q=Path(P['control']['worktree'])/'ch8-s1-control'
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONPATH=str(Q)+os.pathsep+str(PACKET))
argv=[sys.executable,'-m','unittest','-v','test_r5','cap_checks.R5MarginTests',
    'test_s2.S2Tests.test_workflow_caps_types_and_single_serial_job',
    'test_s2.S2Tests.test_timeout_caps_and_order_reject_redistribution',
    'test_s2.S2Tests.test_setup_aggregate_remaining_boundary_without_compiler']
assert not (HERE/'TARGETED-TESTS.json').exists()
start=time.monotonic_ns();utc=datetime.datetime.now(datetime.timezone.utc).isoformat()
proc=subprocess.run(argv,cwd=Q,env=env,capture_output=True)
end=time.monotonic_ns();log=proc.stdout+proc.stderr
(HERE/'TARGETED-TESTS.txt').write_bytes(log)
result={'argv':argv,'cwd':str(Q),'environment':{'PYTHONDONTWRITEBYTECODE':'1','PYTHONPATH':env['PYTHONPATH']},
    'started_utc':utc,'elapsed_seconds':(end-start)/1e9,'exit_code':proc.returncode,
    'transcript_sha256':hashlib.sha256(log).hexdigest(),'control':P['control'],
    'test_r5_sha256':hashlib.sha256((Q/'test_r5.py').read_bytes()).hexdigest(),
    'cap_checks_sha256':hashlib.sha256((PACKET/'cap_checks.py').read_bytes()).hexdigest(),
    'scope':'BOUNDED_SYNTHETIC_SERVICE_TESTS; no compiler/verifier/full runner/CI',
    'full_Validate_reexecutions':0,'proof_credit':'NONE'}
(HERE/'TARGETED-TESTS.json').write_text(json.dumps(result,indent=2)+'\n')
print(log.decode(),end='');assert proc.returncode==0
