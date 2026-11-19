"""Review-only static preflight, targeted regressions and in-memory sensitivity."""
from pathlib import Path
import contextlib, importlib, io, json, sys, time, unittest
from unittest import mock
OUT=Path(__file__).resolve().parent
P=OUT.with_name('s4-next-impl')
H=Path('/root/kani-ch8-s4-next-control-w15/ch8-s1-control')
sys.path.insert(0,str(H))
def save(name,obj): (OUT/name).write_text(json.dumps(obj,indent=2)+'\n')
if sys.argv[1]=='preflight':
    import runner,check_package,s4p3_policy as policy
    req=runner.load_request();saved=[];original=policy.validate_source;start=time.monotonic()
    def observe(std,r):
        report=original(std,r);saved.append(report);return report
    with mock.patch.object(policy,'validate_source',side_effect=observe):
        source=runner.verify_source(Path('/root/verify-rust-std-ch8-s4-next-w15'),Path('/root/kani-upstream-ch8-s1'),req,prebuild=True)
    assert len(saved)==1 and saved[0]['status']=='STATIC_PASS'
    for name,report in saved[0]['reports'].items():
        assert json.loads((P/('MAP-'+name.upper()+'.json')).read_text())==json.loads(json.dumps(report))
    from s4p3_contract_stacks import ACTIVE
    rows=saved[0]['reports']['contract_stacks']['cfg_projection_invariance']
    keys={'kani'}|{x[6:] for x in req['flags']['RUSTFLAGS'].split()}
    assert len(rows)==len({tuple(x['effective_cfg']) for x in rows})==64
    legacy=sum(set(x['effective_cfg'])<=keys-{'kani_smallsort_controls'} for x in rows)
    active=sum(ACTIVE<=set(x['effective_cfg']) for x in rows)
    assert (legacy,active)==(32,8)
    result={'status':'STATIC_PASS','seconds':time.monotonic()-start,'request_sha256':runner.sha256(H/'CI-REQUEST.json'),
            'four_source_maps':'RECOMPUTED_EXACT_MATCH','uncached_validate_source_calls':1,'cfg_projections':64,
            'legacy_contexts':legacy,'ACTIVE_contexts':active,'domain':saved[0]['domain_correspondence'],
            'workflow':check_package.check_yaml(H.parent/'.github/workflows/ch8-s2.yml'),
            'native_compile_CI':'NOT_RUN','proof_credit':'NONE'}
    save('PREFLIGHT.json',result);print(json.dumps(result),flush=True)
elif sys.argv[1]=='tests':
    import s4p2r2_validate as r2,s4p3_validate as v
    start=time.monotonic()
    with (OUT/'OLD-TARGETED-TESTS.txt').open('w') as log,contextlib.redirect_stderr(log):
        a=r2.old_s4p2_suite(('test_s4p2.RoleTests','test_s4p2.WorkflowTests','test_s4p2.SingletonRunnerTests'))
        b=v.old_s4p2r2_suite()
    result={'status':'PASS' if a.wasSuccessful() and b.wasSuccessful() else 'FAIL',
            'tests':a.testsRun+b.testsRun,'failures':len(a.failures)+len(b.failures),'errors':len(a.errors)+len(b.errors),
            'seconds':time.monotonic()-start,'scope':'8 retained S4P2 routing and all22 network-r2 regressions',
            'final_Validate':'NOT_RUN','native_CI':'NOT_RUN'}
    save('OLD-TARGETED-TESTS.json',result);print(json.dumps(result),flush=True)
    assert result['status']=='PASS' and result['tests']==30
    import s3_validate,s32_validate,s34_validate,s4p_validate,s4p2_validate
    # Match the prepared runner's explicit suite names; discover without running.
    cases={'legacy':s3_validate.LEGACY,'s3':('test_s3','test_s3_repair','test_s3_paths'),
           's32':s32_validate.NEW,'bridge1':s34_validate.NEW,'s4p':s4p_validate.NEW,
           's4p2':s4p2_validate.NEW,'s4p2r2':r2.NEW,'s4p3':v.NEW}
    counts={k:unittest.defaultTestLoader.loadTestsFromNames(names).countTestCases() for k,names in cases.items()}
    assert counts==dict(zip(cases,(136,56,35,40,38,39,22,23))),counts
    assert sum(counts.values())==389
    save('DISCOVERY.json',{'status':'PASS_DISCOVERY_ONLY','counts':counts,'old_tests':366,'new_tests':23,'total':389,'final_Validate':'NOT_RUN'})
elif sys.argv[1]=='mutations':
    import runner,s4p3_domain as domain,s4p3_policy as policy,test_s4p3_domain as dt,test_s4p3 as tt
    mutants=[]
    def detect(name,test,patch):
        stream=io.StringIO()
        with patch:
            result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.TestSuite([test]))
        assert result.failures and not result.errors,(name,stream.getvalue())
        mutants.append({'mutant':name,'detected':True,'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors)})
    detect('domain_gate_accepts_wrong_call_snapshot_post_domain_frame',
           dt.DomainTests('test_adverse_call_snapshot_post_domain_frame_and_role_changes_reject'),
           mock.patch.object(domain,'check_text',return_value={}))
    detect('native_gate_accepts_nonSAT_covers_and_failed_assertions',
           dt.DomainTests('test_each_native_cover_required_sat_and_each_assertion_success'),
           mock.patch.object(policy,'expected_observation',return_value=True))
    original=runner.ci_env
    def lose_cfg(*args,**kwargs):
        env=original(*args,**kwargs);env['RUSTFLAGS']='';return env
    detect('runner_loses_new_profile_cfg',tt.SingletonRunnerTests('test_s3_singleton_uses_real_new_pins_cfg_bounds_fresh_target_and_after'),
           mock.patch.object(runner,'ci_env',side_effect=lose_cfg))
    save('MUTATION-CHECKS.json',{'status':'PASS_MUTANTS_DETECTED','mutants':mutants,
         'method':'in-memory monkeypatches; candidate bytes unchanged','native_CI':'NOT_RUN'})
    print('Mutation sensitivity PASS',flush=True)
else: raise SystemExit('unknown mode')
