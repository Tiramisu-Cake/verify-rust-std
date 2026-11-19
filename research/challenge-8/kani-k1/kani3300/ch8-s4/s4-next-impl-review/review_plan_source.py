"""Independent plan-to-actual-source/role inventory cross-check; static only."""
from pathlib import Path
import json,re,sys
OUT=Path(__file__).resolve().parent
P=OUT.with_name('s4-next-impl')
S=Path('/root/verify-rust-std-ch8-s4-next-w15')
H=Path('/root/kani-ch8-s4-next-control-w15/ch8-s1-control')
sys.path.insert(0,str(H))
import runner,s4p3_profile
read=lambda p:json.loads(p.read_text())
plan=read(OUT.with_name('s4-full-lengths-next-plan')/'NEXT-PACKAGE.json')
r=runner.load_request();source=(S/'library/core/src/slice/sort/shared/smallsort/verify/sorting_s4_full_lengths_next.rs').read_text()
assert plan['positive_lengths']==[8,9,13,17]
assert read(P/'RESOURCE.json')==plan['resource_snapshot_unchanged']
assert [x['id'] for x in r['rows']]==[x['id'] for x in plan['rows']]
rows=[]
for wanted,row in zip(plan['rows'][4:],r['rows'][4:]):
    n=wanted['domain']['n'];prefix=f'S4P3_N_{n:02}_'
    for key in ('id','selector','mode','target','unwind','timeout_seconds'):assert row[key]==wanted[key]
    start=source.index('fn '+row['id']+'() {');end=source.index('\n}',start)
    body=source[start:end]
    required=[f'let n: usize = {n};',f'let before = snapshot::<u8, KeyLess<u8>>(&v[1..{n+1}]);',
              wanted['literal_call']+';',f'post::<u8, KeyLess<u8>>(before, &v[1..{n+1}])',
              'let mut v: [u8; 34] = kani::any();','let bytes = v;','for i in 0..34 {',
              '(1 <= i && i < 1 + n) || v[i] == bytes[i]',
              'let canary: usize = kani::any();','kani::assume(canary < 34 && (canary < 1 || canary >= 1 + n));',
              'kani::assert(v[canary] == bytes[canary],', 'kani::assert(active_u8(),']
    for fragment in required:assert fragment in body,(n,fragment)
    assert body.count('small_sort_network(')==1 and body.count('kani::assume(')==1 and body.count('kani::any()')==2
    assert body.count('kani::assert(')==4 and body.count('kani::cover(')==6
    expected=[{k:x[k] for k in ('class','status','description')} for x in wanted['roles']+wanted['covers']]
    assert [{k:x[k] for k in ('class','status','description')} for x in row['roles']]==expected
    for role in row['roles']:
        assert source.splitlines()[role['line']-1]==role['source_line']
    for cover in wanted['covers'][:-1]:assert cover['expression'] in body
    assert 'kani::cover(true, "'+prefix+'USEFUL_RETURN");' in body
    argv=runner.build_argv(S,Path('/root/kani-upstream-ch8-s1'),[row['selector']],row['unwind'],Path('/tmp/not-created-review-export.json'))
    assert argv[argv.index('--default-unwind')+1]=='36'
    assert not any(x in argv for x in ('--unwind','--unwindset','--no-unwinding-assertions','--no-memory-safety-checks'))
    assert r['domains'][row['id']]['length_interval']==[n,n]
    rows.append({'n':n,'literal_slice':f'[1..{n+1}]','assertions':4,'covers':6,'default_unwind_argv':36,
                 'original_null':True,'full34_frame_canary':True,'merge_reached':False})
assert source.count('#[kani::unwind(36)]')==4
assert source.count('kani::assume(')==4
assert r['replacement_unions']==r['enabled_summary_edges']==[] and r['variants']=={}
assert r['unreachable_admission']['mode']=='REJECT_ALL' and r['unreachable_admission']['enabled'] is False
assert r['s3']['u_policy'].startswith('ZERO_U_FAIL_CLOSED;')
prepared=read(P/'FINAL-VALIDATE-PREPARED.json')
assert prepared['execution_count']==0 and prepared['status']=='PREPARED_NOT_RUN'
assert (prepared['deadline_seconds'],prepared['margin_required'],prepared['maximum_elapsed_seconds_for_margin'])==(1080,1.5,720)
result={'status':'PASS','scope':'source-level finite normal-return candidates only','rows':rows,
        'resource_snapshot':'EXACT_PLAN_MATCH','negative_unwinds':[x['unwind'] for x in r['rows'][:4]],
        'native_argv_resolution':'NOT_OBSERVED; source builder only','final_Validate':'PREPARED_NOT_RUN',
        '600_second_fit':'UNKNOWN','lowered_unwind_sufficiency':'UNKNOWN','proof_credit':'NONE'}
assert result['negative_unwinds']==[34,34,34,36]
(OUT/'PLAN-SOURCE-CHECKS.json').write_text(json.dumps(result,indent=2)+'\n')
log=(OUT/'TARGETED-TESTS.txt').read_text()
assert re.search(r'Ran 23 tests in ([0-9.]+)s\n\nOK',log)
(OUT/'TARGETED-TESTS.json').write_text(json.dumps({'status':'PASS','tests':23,'failures':0,'errors':0,
    'unittest_seconds':float(re.search(r'Ran 23 tests in ([0-9.]+)s',log)[1]),'control_sha':'65a9ea656a4b5f1e66f7b31eceffb5eefeba7541',
    'request_sha256':runner.sha256(H/'CI-REQUEST.json'),'scope':'new targeted synthetic regression suites only','final_Validate':'NOT_RUN','native_CI':'NOT_RUN'},indent=2)+'\n')
print('Plan/source/role cross-check PASS')
