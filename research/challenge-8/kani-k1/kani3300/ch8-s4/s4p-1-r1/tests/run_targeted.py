import datetime, hashlib, json, os, sys, time, unittest
from pathlib import Path
from unittest import mock
CONTROL=Path('/root/kani-ch8-s4p-1-r1-control-w13')
HERE=CONTROL/'ch8-s1-control'
OUT=Path('/root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/kani3300/ch8-s4/s4p-1-r1')
sys.path.insert(0,str(HERE));os.chdir(HERE)
import collect as public, s4p_campaign as campaign, runner
records=[];original=public.collect
def observe(roots,request):
    terminal=public.read(roots[0]/'receipt.json')
    record={'route':'LOCAL' if (roots[0]/'receipt.json').is_file() else 'UPLOAD_ONLY',
        'writer_state':terminal['state'],'completed':len(terminal['s3_campaign']['completed']),
        'schema_present':'schema' in terminal,'schema':terminal.get('schema')}
    with mock.patch.object(public,'legacy_collect',wraps=public.legacy_collect) as spy:
        try:result=original(roots,request)
        except campaign.GlobalFailure as exc:
            record.update(accepted=False,error=str(exc),legacy_collection_entered=spy.called)
            records.append(record);raise
        else:
            record.update(accepted=True,recorded_observations=sum(row['outcome']=='RECORDED' for row in result['rows']),legacy_collection_entered=spy.called)
            records.append(record);return result
start=time.monotonic();started=datetime.datetime.now(datetime.timezone.utc).isoformat()
with (OUT/'tests/targeted-02.stderr').open('w') as stream, mock.patch.object(public,'collect',side_effect=observe):
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromName('test_s4p_gate_repair'))
elapsed=time.monotonic()-start
bad=[x for x in records if not x['accepted']];good=[x for x in records if x['accepted']]
assert result.wasSuccessful() and result.testsRun==3
assert len(records)==84 and len(bad)==78 and len(good)==6
assert all(not x['legacy_collection_entered'] and x['error']=='S4 terminal campaign schema mismatch' for x in bad)
assert all(x['legacy_collection_entered'] and x['recorded_observations']==x['completed'] for x in good)
receipt={'schema':'s4p1-repair-targeted-v1','started_utc':started,'elapsed_seconds':elapsed,'tests':result.testsRun,'exit_code':0,
    'request_sha256':runner.sha256(runner.REQUEST_PATH),'test_file_sha256':runner.sha256(HERE/'test_s4p_gate_repair.py'),
    'working_candidate_not_final_commit':True,'authentic_old_24_all_reject':True,'malformed_rejections':len(bad),'genuine_acceptances':len(good),
    'no_malformed_schema_collection':True,'matrix':'TERMINAL-SCHEMA-MATRIX.json','native_compile_proof_CI':'NOT_RUN'}
(OUT/'tests/TERMINAL-SCHEMA-MATRIX.json').write_text(json.dumps({'records':records,**receipt},indent=2)+'\n')
(OUT/'tests/targeted-02.json').write_text(json.dumps(receipt,indent=2)+'\n')
(OUT/'tests/targeted-02.stdout').write_text(json.dumps(receipt,sort_keys=True)+'\n')
print(json.dumps(receipt),flush=True)
