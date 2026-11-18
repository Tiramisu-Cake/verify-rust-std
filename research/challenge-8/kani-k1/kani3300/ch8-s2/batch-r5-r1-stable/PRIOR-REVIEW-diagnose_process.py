#!/usr/bin/env python3
"""Bounded investigation of the unchanged fast-exit process fixture race."""
import contextlib,hashlib,json,os,subprocess,sys,tempfile,time,unittest
from unittest import mock
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
P=json.loads((HERE.with_name('batch-r5-r1')/'PINS.json').read_text())
C=Path(P['control']['worktree']);Q=C/'ch8-s1-control'
sys.path.insert(0,str(Q))
import r5_runtime as rt
import r5_campaign as c
from test_r5 import ProcessTests

def main():
    old=subprocess.check_output(['git','-C',str(C),'show',P['frozen_control']+':ch8-s1-control/r5_runtime.py'])
    assert old==(Q/'r5_runtime.py').read_bytes()
    # Keep every result, including a possible repeat failure. No candidate edits.
    log=[]
    import io
    for i in range(1):
        stream=io.StringIO()
        result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.TestSuite([
            ProcessTests('test_escaped_setsid_child_found_and_reaped')]))
        log.append({'attempt':i+1,'success':result.wasSuccessful(),'transcript':stream.getvalue()})
    cases=[]
    fast="import subprocess,sys;subprocess.Popen([sys.executable,'-c','import os,time;os.setsid();time.sleep(30)']);"
    for label,script in [('exact_fast_exit_fixture',fast),('synchronized_setsid_before_parent_exit',
        "import subprocess,sys,time,pathlib;subprocess.Popen([sys.executable,'-c',\"import os,time,pathlib;os.setsid();pathlib.Path('ready').write_text('ready');time.sleep(30)\"]);"+
        "\nwhile not pathlib.Path('ready').exists():time.sleep(.005)\n"),('delayed_after_first_observation',fast)]:
        with tempfile.TemporaryDirectory(prefix='review14-process-') as temp:
            root=Path(temp)
            original_observe=rt.Owned.observe;calls=[]
            def delayed_observe(owned,*args):
                value=original_observe(owned,*args)
                if not calls:time.sleep(.15)
                calls.append(True)
                return value
            ctx=mock.patch.object(rt.Owned,'observe',delayed_observe) if label.startswith('delayed') else contextlib.nullcontext()
            with ctx:
                result=rt.supervise([sys.executable,'-c',script],root,dict(os.environ),2,12*1024*1024,root/'worker.stderr')
            assert result['containment']['verified'] and result['containment']['reaped_adopted']
            doc={'state':'COMPLETE','execution':{'process_identity':result['worker_initial_identity']}}
            try:c.validate_owned_groups(doc,result)
            except c.GlobalFailure as error:gate={'rejected':True,'message':str(error)}
            else:gate={'rejected':False}
            if label.startswith('synchronized'):
                assert result['orphan_survivors_at_worker_exit']
                assert gate['rejected'] and 'unexpected_process_group_containment_gap' in gate['message']
            if label.startswith('delayed'):
                assert not result['orphan_survivors_at_worker_exit']
                assert gate['rejected'] and 'unexpected_process_group_containment_gap' in gate['message']
            cases.append({'case':label,'result':result,'controller_owned_group_check':gate})
    report={'status':'DIAGNOSED_UNCHANGED_FIXTURE_RACE',
        'initial_failure':'TARGETED-TESTS.txt: orphan_survivors_at_worker_exit [] assertion; containment verified assertion passed',
        'runtime_byte_identical_to_prior':True,'runtime_sha256':hashlib.sha256(old).hexdigest(),
        'exact_test_repeats':log,'instrumented_cases':cases,
        'analysis':'The original fixture lets its parent exit immediately after Popen, without synchronizing child setsid. The supervisor samples live before poll; adoption/child startup can occur between that sample and parent exit. The early survivors list is timing-dependent. cleanup resamples owned descendants, signals and reaps them; its observed inventory feeds the unchanged controller PGID escape check. The synchronized fixture guarantees setsid before exit and independently tests that check.',
        'classification':'UNCHANGED_NONDETERMINISTIC_TEST_SNAPSHOT; not a portable-seal regression',
        'limitation':'No general process-containment proof; scoped diagnostic only. Initial failed assertion retained; no all34PASS claim.',
        'candidate_edit':0,'full_Validate_reexecutions':0,'proof_credit':'NONE'}
    (HERE/'PROCESS-DIAGNOSTIC.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'exact_test_repeat_passes':sum(x['success'] for x in log),'synchronized_escape_rejected':True,'cleanup_verified':True}))

if __name__=='__main__':main()
