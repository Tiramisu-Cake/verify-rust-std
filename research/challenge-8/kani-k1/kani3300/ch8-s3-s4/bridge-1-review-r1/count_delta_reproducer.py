#!/usr/bin/env python3
"""Independent count matrix, exact separate baseline/repaired module processes.

Uses existing real Python controller/writer/packer; native and Git telemetry are
synthetic fixture data. No compiler, solver or dummy binary is executed.
"""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from unittest import mock

sys.dont_write_bytecode=True
KIND=sys.argv[1]
assert KIND in ('baseline','repaired')
CONTROL=Path('/root/kani-ch8-s3s4-bridge1-'+('control-w13' if KIND=='baseline' else 'r1-control-w13'))
EXPECTED='b9e57f09775ed9db249e0b1b6f8e7e53bde5e60f' if KIND=='baseline' else 'd675ef70dc1ada13330efc0990c2e1d6b0d21a5a'
def git(*args): return subprocess.check_output(['git','-C',str(CONTROL),*args])
assert git('rev-parse','HEAD').decode().strip()==EXPECTED
assert not git('status','--porcelain=v1').strip()
sys.path.insert(0,str(CONTROL/'ch8-s1-control'))
import test_s34_paths as fixtures
import s34_campaign as c
import collect as public
import pack_evidence
for module in (fixtures,c,public,pack_evidence):
    assert Path(module.__file__).resolve().parent==CONTROL/'ch8-s1-control'
test=fixtures.RealPathWriterTests('test_workflow_relative_entry_real_writer_and_portable_replay')
CASES=[('int7',7),('missing',None),('null',None),('bool',True),('string','7'),('float',7.0),('zero',0),('six',6),('eight',8)]
observations=[]

def snapshot(out):
    return {str(p.relative_to(out)):hashlib.sha256(p.read_bytes()).hexdigest() for p in out.rglob('*.json') if p!=out/'receipt.json'}

def matrix(fix,terminal,label):
    out,req=fix[3:5];c.p.validate(req)
    selected=terminal['s3_campaign']['selected_roots'];done=terminal['s3_campaign']['completed']
    assert type(selected) is int and selected==(8 if KIND=='baseline' else 7)
    path=out/'receipt.json';authentic=path.read_bytes();frozen=snapshot(out)
    upload=fix[0]/'independent-upload';upload.mkdir(exist_ok=True)
    initial=public.collect([out],req)
    assert len(initial['rows'])==7 and initial['proof_credit']=='NONE'
    rows=[]
    try:
        for name,value in CASES:
            doc=json.loads(authentic)
            if name=='missing': del doc['s3_campaign']['selected_roots']
            else: doc['s3_campaign']['selected_roots']=value
            c.atomic(path,doc);pack_evidence.pack(out)
            (upload/pack_evidence.NAME).write_bytes((out/pack_evidence.NAME).read_bytes())
            assert [p.name for p in upload.iterdir()]==[pack_evidence.NAME]
            results=[];accepted=[]
            for route in (out,upload):
                try:
                    result=public.collect([route],req);results.append('ACCEPT');accepted.append(result)
                except c.GlobalFailure as exc:
                    assert 'selected-root cardinality' in str(exc);results.append('REJECT')
            expectation='ACCEPT' if KIND=='baseline' or name=='int7' else 'REJECT'
            assert results==[expectation]*2,(label,name,results)
            if accepted: assert accepted==[initial,initial]
            rows.append({'case':name,'local':results[0],'upload_only':results[1]})
    finally: path.write_bytes(authentic)
    assert snapshot(out)==frozen
    observations.append({'scenario':label,'state':terminal['state'],'launched':len(fix[6]),'completed':len(done),'writer_type':type(selected).__name__,'writer_selected':selected,'remaining_statuses':[r['status'] for r in terminal['rows'][len(done):]],'collector_outcomes':[r['outcome'] for r in initial['rows']],'public_routes':rows,'nonterminal_structured_bytes_preserved':True})

with test.fixture() as fix:
    code,terminal=test.run_fixture(fix)
    assert code==0 and fix[6]==terminal['s3_campaign']['completed']==list(c.p.ORDER)
    matrix(fix,terminal,'full7')

if KIND=='repaired':
    def stop_after_two(root,out,rid,tool,sup):
        if rid==c.p.ORDER[2]: raise c.GlobalFailure('independent stop after two seals')
    with test.fixture(fault=stop_after_two) as fix:
        code,terminal=test.run_fixture(fix)
        assert code==1 and terminal['state']=='STOPPED';test.prefix(fix,terminal)
        matrix(fix,terminal,'stopped2')
        frozen=snapshot(fix[3]);terminal=c.finalize(fix[3],fix[4])
        assert terminal['state']=='SELECTED_PARTIAL';test.prefix(fix,terminal)
        assert public.collect([fix[3]],fix[4])['rows'][2]['outcome']=='UNKNOWN'
        assert all(row['status']=='NOT_RUN' for row in terminal['rows'][3:])
        # Re-finalization may add unfinished records, but sealed prefix is immutable.
        assert all(snapshot(fix[3])[k]==v for k,v in frozen.items() if k.startswith(('completed/','groups/s3-'+c.p.ORDER[0]+'/','groups/s3-'+c.p.ORDER[1]+'/')))
        matrix(fix,terminal,'partial2')
    with test.fixture() as fix:
        with mock.patch.object(c,'check_usage',side_effect=c.GlobalFailure('independent prelaunch stop')):
            code,terminal=test.run_fixture(fix)
        assert code==1 and fix[6]==[] and terminal['s3_campaign']['completed']==[]
        assert all(row['status']=='NOT_RUN' for row in terminal['rows'])
        assert all(row['outcome']=='UNKNOWN' for row in public.collect([fix[3]],fix[4])['rows'])
        matrix(fix,terminal,'stopped0')
        terminal=c.finalize(fix[3],fix[4]);assert terminal['state']=='SELECTED_PARTIAL'
        matrix(fix,terminal,'partial0')
    with test.fixture() as fix:
        assert test.run_fixture(fix)[0]==0
        before=(fix[3]/'receipt.json').read_bytes()
        for rows in (fix[4]['rows'][:-1],fix[4]['rows'][::-1]):
            bad=copy.deepcopy(fix[4]);bad['rows']=rows
            for operation in (c.finalize,c.collect,public.collect):
                try: operation(fix[3] if operation is c.finalize else [fix[3]],bad)
                except AssertionError: pass
                else: raise AssertionError('unvalidated inventory accepted')
            assert (fix[3]/'receipt.json').read_bytes()==before
assert git('rev-parse','HEAD').decode().strip()==EXPECTED and not git('status','--porcelain=v1').strip()
print(json.dumps({'status':'PASS','kind':KIND,'control':EXPECTED,'module_origins':{m.__name__:m.__file__ for m in (fixtures,c,public,pack_evidence)},'observations':observations,'invalid_inventory_checks':6 if KIND=='repaired' else 0,'native_execution':'SYNTHETIC_ONLY','proof_credit':'NONE'},indent=2))
