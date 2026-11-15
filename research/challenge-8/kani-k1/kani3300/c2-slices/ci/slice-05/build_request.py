#!/usr/bin/env python3
"""Create immutable coordinator request; Git/Python only, never dispatch CI."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
PACKET=HERE.parent.parent
REPO=Path('/root/kani-fix-3300-c2-slices-w15')

def git(*args):
    return subprocess.check_output(['git','-C',str(REPO),*args])

def load(path):
    return json.loads((PACKET/path).read_text())

def main():
    sys.path.insert(0,str(REPO/'.github/c2-slices'))
    spec=importlib.util.spec_from_file_location('slice_ci',REPO/'.github/c2-slices/slice05_ci.py')
    ci=importlib.util.module_from_spec(spec);sys.modules[spec.name]=ci;spec.loader.exec_module(ci)
    config,manifest=ci.inputs()
    source=config['source_sha'];overlay=git('rev-parse','HEAD').decode().strip()
    tree=git('rev-parse','HEAD^{tree}').decode().strip()
    with tempfile.TemporaryDirectory() as temp:
        ci.snapshot('static',Path(temp))
        snapshot=json.loads((Path(temp)/'source-static.json').read_text())
    suites=[]
    for (suite,mode),selectors in ci.suites(manifest).items():
        suites.append(dict(suite=suite,mode=mode,discovery=len(selectors),existing_ignored=sum(r['existing_path_ignore'] for r in selectors.values()),
            expected_passed_if_green=sum(not r['existing_path_ignore'] for r in selectors.values()),selectors=list(selectors),
            argv=['cargo','run','-p','compiletest','--quiet','--','--suite',suite,'--mode',mode,'--build-base','${C2_EVIDENCE_DIR}/build-tests/'+suite,
                '--logfile','${C2_EVIDENCE_DIR}/suite-'+suite+'.native.log','--color','never','--exact','--force-rerun','--no-fail-fast','--timeout','2400',*selectors]))
    units=[dict(action='units',filter='active_call_tests',native_names=['kani_middle::points_to::points_to_analysis::active_call_tests::'+n for n in manifest['active_call_units']]),
        dict(action='immutable-units',filter='immutable_allocations::tests',native_names=['codegen_cprover_gotoc::context::immutable_allocations::tests::'+n for n in manifest['immutable_unit_names']]),
        *[dict(action=action,**unit) for action,unit in config['additional_units'].items()]]
    for unit in units:
        unit.update(expected_passed=len(unit['native_names']),expected_failed=0,expected_ignored=0,argv=ci.COMMANDS[unit['action']])
    delta=load('slice-05/ORACLE-DELTA.json')
    rows=delta['selected_complete_fixtures']
    target=[]
    for row in rows:
        src,golden=[git('show',source+':'+row[k]) for k in ['input','golden']]
        target.append(dict(id=row['id'],input=row['input'],golden=row['golden'],selector='[expected] '+row['input'].removeprefix('tests/'),
            owner_slice=row['owner_slice'],earliest_runnable_head=5,source_sha256=hashlib.sha256(src).hexdigest(),golden_sha256=hashlib.sha256(golden).hexdigest(),
            source_harness_count=row['source_harness_count'],exact_failure_N=[int(n) for n in re.findall(rb'\*\* (\d+) of',golden)],
            golden_verdicts=re.findall(r'VERIFICATION:- (SUCCESSFUL|FAILED)',golden.decode()),native_result='NOT_RUN'))
    assert len(target)==47
    paths=git('diff','--name-only',source,'HEAD').decode().splitlines()
    assert all(ci.ci_path(p) for p in paths)
    request=dict(inputs=dict(config,overlay_sha=overlay,overlay_tree=tree,branch='uninit-ci/c2-slices-05-w15'),stage_commands=ci.COMMANDS,units=units,suites=suites,
        targeted_stage5_fixtures=target,integration_obligations=load('slice-05/CLOSURE-OBLIGATIONS.json'),
        historical_obligation_provenance='Owner1 integration-tested on head5 only after explicit CI receipts; accepted4 records remain unchanged.',
        sensitivity=dict(manifest=json.loads((REPO/'.github/c2-slices/sensitivity-manifest.json').read_text()),
            readiness=load('slice-05/S5-MUTATIONS-READINESS.json'),status='REQUIRED_4_OF_4_NATIVE_NOT_RUN',
            requirements=['clean expected suite must pass first','independent patches, restored source after every variant','input and patch SHA checked',
                'same built tools; no rebuild; unique --force-rerun --exact output dirs','compiletest exit1 + exact selected FAILED + completed native verdict/N + intended golden mismatch',
                'compile/setup/timeout/early Unsupported is not detection','negative-extra retains exact outside-assigns failure; golden inversion is sanity only']),
        recipe=dict(accepted_overlay=config['accepted_recipe_overlay'],accepted_run='43710024495',runner='ubuntu-24.04',job_timeout_minutes=120,per_fixture_timeout_seconds=2400,
            RUST_TEST_THREADS=2,auto_retries=0,delta='Stage5 manifest/count/names; full compiler68 units; sensitivity action/helper/4 test-only patches, source-restoring in CI only.'),
        qualification_review_required=['460 selectors:451 passes+9 existing ignores if green; all compiler68 units plus explicit9/9/1/1 groups',
            'Native fmt/build/clippy and compile seams, source before/after clean and source-identical',
            'Explicit all47 exact-head fixture outcomes, useful SUCCESS and exact intended failures; no substitute Unsupported/protocol/layout refusal',
            'Owner1 pending head5 obligations and generated-modifies-no-shadow close only by explicit native output on this cumulative source',
            'All8 strong oracles,7 modes,7 roots; recursive ordinary/check exact cycle boundary and simple-check legal',
            'Replace two local PFC companions remain present but only selected callers execute; separate simple-check runs',
            'S5 mutation4/4 independently detected through intended golden failures and actual retained verdict/N'],
        artifacts=dict(always_upload=True,path='${runner.temp}/c2-slices-05-evidence/',name='c2-slices-05-${github.run_id}-${github.run_attempt}',
            required=['inputs.json','test-manifest.json','source-before.json','source-after.json','per-stage original argv/exit/termination reason and stdout/stderr',
                'six suite native logs and actual build-tests per-fixture output','sensitivity summary,4 independent results, patches and mutated data, native .out, per-variant source snapshots','runner-errors when present'],
            not_started='NOT_RUN/null exit/NOT_STARTED',successful_runner='Requires per-fixture coordinator review, not proof credit'),
        static_validation_refs={n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in ['SOURCE-VALIDATION.json','SEAM-VALIDATION.json','FIXTURE-REVIEW.json','STATIC-VALIDATION.json','CALL-CONTRACTS.json','COMPILER-UNITS.json','check_source.py','check_overlay.py','prepare_overlay.py','sensitivity.py','check_sensitivity.py']},
        authorization='Local CI-only overlay and g0 commits only; no local Rust/Kani builds, no push/dispatch. Coordinator alone may publish or run CI.')
    (HERE/'CI-REQUEST.json').write_text(json.dumps(request,indent=2)+'\n')
    (HERE/'overlay.patch').write_bytes(git('diff','--binary',source,'HEAD'))
    print(json.dumps(dict(overlay_sha=overlay,overlay_tree=tree,protected_source_entries=len(snapshot['files']),selectors=sum(s['discovery'] for s in suites),target_pairs=len(target),compiler_units=68,sensitivity='NATIVE_NOT_RUN')))

if __name__=='__main__':
    main()
