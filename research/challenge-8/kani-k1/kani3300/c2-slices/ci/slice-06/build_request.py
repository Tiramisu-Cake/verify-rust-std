#!/usr/bin/env python3
"""Build exact immutable coordinator CI request; never build or dispatch."""
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


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    sys.path.insert(0,str(REPO/'.github/c2-slices'))
    spec=importlib.util.spec_from_file_location('slice_ci',REPO/'.github/c2-slices/slice06_ci.py')
    ci=importlib.util.module_from_spec(spec);sys.modules[spec.name]=ci;spec.loader.exec_module(ci)
    config,manifest=ci.inputs()
    source=config['source_sha'];overlay=git('rev-parse','HEAD').decode().strip();tree=git('rev-parse','HEAD^{tree}').decode().strip()
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
    canonical=load('oracle-map/ORACLE-MAP.json')
    rows=load('slice-06/ORACLE-DELTA.json')['selected_complete_fixtures']
    assert {r['id'] for r in rows}=={r['id'] for r in canonical['fixtures'] if r['owner_slice']==6}
    # Explicit edge outcomes plus all inherited strong/mode/composition oracles.
    selected={r['id']:r for r in rows}
    inherited_ids={r['id'] for r in load('slice-05/ORACLE-DELTA.json')['selected_complete_fixtures']}
    selected.update({r['id']:r for r in canonical['fixtures']
                     if r['id'] in inherited_ids or '/part1-composition/' in r['input']})
    assert inherited_ids <= set(selected)
    target=[]
    for row in selected.values():
        src,golden=[git('show',source+':'+row[k]) for k in ['input','golden']]
        target.append(dict(id=row['id'],input=row['input'],golden=row['golden'],selector='[expected] '+row['input'].removeprefix('tests/'),
            owner_slice=row['owner_slice'],source_sha256=digest(src),golden_sha256=digest(golden),
            source_harness_count=row['source_harness_count'],required_golden=golden.decode().splitlines(),
            exact_failure_N=[int(n) for n in re.findall(rb'\*\* (\d+) of',golden)],
            golden_precision='F_LITERAL_ONLY_NO_EXACT_PROPERTY_COUNT' if row['owner_slice']==6 else 'EXACT_F_LITERAL_GOLDEN',
            golden_verdicts=re.findall(r'VERIFICATION:- (SUCCESSFUL|FAILED)',golden.decode()),native_result='NOT_RUN'))
    assert sum(r['owner_slice']==6 for r in target)==11
    assert all(ci.ci_path(p) for p in git('diff','--name-only',source,'HEAD').decode().splitlines())
    assert git('show',config['accepted_recipe_overlay']+':.github/c2-slices/slice05_ci.py')==(REPO/'.github/c2-slices/slice06_ci.py').read_bytes()
    assert (REPO/'.github/c2-slices/test-manifest.json').read_bytes()==(PACKET/'slice-06/TEST-MANIFEST.json').read_bytes()
    assert (REPO/'.github/c2-slices/sensitivity.py').read_bytes()==(HERE/'sensitivity.py').read_bytes()
    report=dict(status='PASS_STATIC_AND_SYNTHETIC_ONLY',source_sha=source,source_tree=config['source_tree'],overlay_sha=overlay,overlay_tree=tree,
        accepted_recipe=config['accepted_recipe_overlay'],accepted_run='43715788377',runner_byte_identical_to_accepted5=True,
        runner_synthetic_checks=23,sensitivity_synthetic_checks=13,seam_checker_synthetic_checks=10,
        generator_reproduction='PASS byte-identical CI overlay files',protected_source_entries=len(snapshot['files']),
        source_snapshot_problems=snapshot['problems'],manifest_byte_identical=True,cumulative_selectors=471,existing_ignores=9,
        all_compiler_units=68,explicit_relevant_units=20,sensitivity_status='REQUIRED4_OF4_NATIVE_NOT_RUN',
        native_checks='NOT_RUN',push_dispatch='NOT_RUN',cloud_spend=0,formal_proof_credit='NOT_ESTABLISHED',
        notes=['Python/Git synthetic tests only; original argv/exits/termination and exceptions retained.',
               'negative-repair-user-write requires completed native SUCCESS/N0 and exact intended golden failure mismatch; permitted write success accepts renumbered locals.',
               'Source inputs/goldens and all four patches are unchanged from accepted5; no historical acceptance rewritten.',
               'Nested saved overlay and mutation patch preserve original trailing whitespace as data; source/runner whitespace checks have no exemption.'])
    (HERE/'STATIC-VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n')
    refs=['SOURCE-VALIDATION.json','SEAM-VALIDATION.json','SEAM-VALIDATION-CUMULATIVE.json','FIXTURE-REVIEW.json','STATIC-VALIDATION.json',
          'CALL-CONTRACTS.json','COMPILER-UNITS.json','check_source.py','check_overlay.py','prepare_overlay.py','sensitivity.py','check_sensitivity.py','build_request.py']
    request=dict(inputs=dict(config,overlay_sha=overlay,overlay_tree=tree,branch='uninit-ci/c2-slices-06-w15'),stage_commands=ci.COMMANDS,units=units,suites=suites,
        targeted_E1_and_inherited_oracles=target,edge_fixture_count=11,
        inherited_acceptance=dict(source_sha=config['source_parent'],run='43715788377',receipt='../../slice-05/ci-43715788377/ACCEPTANCE.md',
            assurance='Coordinator-reported acceptance; no new runtime observation. Head1/3 deferred integration provenance remains on accepted4/5.',
            source_and_previous_fixtures='BYTE_IDENTICAL_TO_ACCEPTED5'),
        sensitivity=dict(manifest=json.loads((REPO/'.github/c2-slices/sensitivity-manifest.json').read_text()),status='REQUIRED_4_OF_4_NATIVE_NOT_RUN',
            requirements=['clean expected suite pass first','same built tools; no rebuild; each patch independent with input/patch hashes checked',
                'per-variant original bytes/modes restored including exception paths; before/after snapshots',
                'unique --exact --force-rerun --no-fail-fast --timeout2400 outputs',
                'compiletest exit1 + exact selected FAILED + completed native verdict/N + intended golden mismatch',
                'repaired write: SUCCESS/N0, intended outside-assigns FAILURE absent, permitted write SUCCESS independent of local var_N renumbering',
                'extra failure retains original outside-assigns failure and reached added failure; golden inversion sanity only',
                'no compile/setup/timeout/early Unsupported or arbitrary exit accepted']),
        recipe=dict(accepted_overlay=config['accepted_recipe_overlay'],accepted_run='43715788377',runner='ubuntu-24.04',job_timeout_minutes=120,per_fixture_timeout_seconds=2400,
            RUST_TEST_THREADS=2,auto_retries=0,delta='Stage6 source/manifest/count/names plus repaired-write classifier correction. Runner bytes identical; source untouched.'),
        qualification_review_required=['471 selectors:462 passes+9 existing ignores if green; compiler68 plus explicit9/9/1/1 filters, zero selection fails',
            'All eleven E1 outcomes:4 SUCCESS,5 uninitialized-read negatives,2 explicit unsized by-value boundary negatives',
            'Useful payload/layout assertions remain; extra Unsupported cannot replace an intended uninitialized read',
            'F edge golden precision retained: no exact failed-property-count claim for E1; inspect retained native outputs',
            'All inherited composition/mode/strong fixtures; exact counts and useful SUCCESS/required failures per unchanged F goldens',
            'Replace local PFC companion presence is not execution credit; only selected caller runs; simple-check separate',
            'Four independent native sensitivity detections on exact head6; accepted5 does not replace this requested rerun',
            'Source before/after clean and identical; native compile seams verified by fmt/build/clippy; no F7 isolation claim'],
        artifacts=dict(always_upload=True,path='${runner.temp}/c2-slices-06-evidence/',name='c2-slices-06-${github.run_id}-${github.run_attempt}',
            required=['inputs.json','test-manifest.json','source-before.json','source-after.json',
                'all stages original argv/exit/termination reason/environment/stdout/stderr','six native suite logs and per-fixture build-tests outputs',
                'sensitivity summary and4 variant records, patches/mutated bytes/native .out/.err/restoration snapshots','runner-errors when present'],
            not_started='NOT_RUN/null exit/NOT_STARTED',successful_runner='Requires coordinator per-fixture review; not proof credit'),
        static_validation_refs={name:digest((HERE/name).read_bytes()) for name in refs},
        authorization='Local CI-only overlay and g0 commits only. No local Rust/Kani builds or push/dispatch. Coordinator alone may publish/run CI.')
    (HERE/'CI-REQUEST.json').write_text(json.dumps(request,indent=2)+'\n')
    (HERE/'overlay.patch').write_bytes(git('diff','--binary',source,'HEAD'))
    print(json.dumps(dict(overlay_sha=overlay,overlay_tree=tree,protected_source_entries=len(snapshot['files']),selectors=471,target_pairs=len(target),compiler_units=68,sensitivity='NATIVE_NOT_RUN')))


if __name__=='__main__':
    main()
