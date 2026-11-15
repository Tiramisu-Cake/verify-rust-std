#!/usr/bin/env python3
"""Write an exact-head coordinator request; no native execution or dispatch."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
PACKET=HERE.parent.parent
REPO=Path('/root/kani-fix-3300-c2-slices-w15')
sys.path.insert(0,str(REPO/'.github/c2-slices'))
import slice07_ci as ci
import structural


def main():
    config,manifest=ci.inputs()
    overlay=subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD']).decode().strip()
    parent=subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD^']).decode().strip()
    assert parent==config['source_sha']
    suites=[]
    for (suite,mode),rows in ci.suites(manifest).items():
        suites.append(dict(suite=suite,mode=mode,selectors=list(rows),expected_passed=sum(not r['existing_path_ignore'] for r in rows.values()),existing_ignored=sum(r['existing_path_ignore'] for r in rows.values()),argv=['cargo','run','-p','compiletest','--quiet','--','--suite',suite,'--mode',mode,'--build-base','${C2_EVIDENCE_DIR}/build-tests/'+suite,'--logfile','${C2_EVIDENCE_DIR}/suite-'+suite+'.native.log','--color','never','--exact','--force-rerun','--no-fail-fast','--timeout','2400',*rows]))
    units=[dict(action='units',filter='active_call_tests',native_names=['kani_middle::points_to::points_to_analysis::active_call_tests::'+n for n in manifest['active_call_units']]),dict(action='immutable-units',filter='immutable_allocations::tests',native_names=['codegen_cprover_gotoc::context::immutable_allocations::tests::'+n for n in manifest['immutable_unit_names']]),*[dict(action=key,**v) for key,v in config['additional_units'].items()]]
    for unit in units:
        unit.update(expected_passed=len(unit['native_names']),expected_failed=0,expected_ignored=0,native_result='NOT_RUN',argv=ci.COMMANDS[unit['action']])
    sm=json.loads((HERE/'structural-manifest.json').read_text());calls=structural.invocations(sm)
    for row in calls:
        row.update(argv=structural.command(Path('${CHECKOUT}'),sm,row,Path('${C2_EVIDENCE_DIR}')/('structural-'+row['id'])),timeout_seconds=180,native_result='NOT_RUN')
    request=dict(status='READY_LOCAL_ONLY_NATIVE_NOT_RUN',source_sha=config['source_sha'],source_tree=config['source_tree'],source_parent=config['source_parent'],overlay_sha=overlay,overlay_tree=subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD^{tree}']).decode().strip(),overlay_parent=parent,branch='uninit-ci/c2-slices-07-w15',g0_input=config['g0_input'],recipe=dict(overlay=config['accepted_recipe_overlay'],run='43720042056',runner='ci/slice-07/slice07_ci.py',delta='F7 units6+2/compiler76, should-panic display parsing, structural adapter, LLBC build after default checks, evidence env fields'),suites=suites,units=units,total_unique_selectors=471,expected_passed_if_green=462,existing_ignored=9,targeted_units=28,compiler_units=76,structural=dict(manifest=sm,invocations=calls,required_comparisons=18,acceptance='All11 original Kani exits match, schema/selection/counters/modes complete;18 accepted=true/exact_match=true/differences={}; no additions or removals',order_credit='NOT_ESTABLISHED',golden_binding='NOT_CHECKED_CAPTURE',fresh_native_result='NOT_RUN'),llbc=dict(argv=ci.COMMANDS['llbc-build'],position='After default-backend suites/sensitivity/structural; no default tests use LLBC replacement',native_result='NOT_RUN'),sensitivity=dict(variants=4,manifest_sha256=config['sensitivity']['manifest_sha256'],required_result='4/4 DETECTED_EXPECTED_MISMATCH',native_result='NOT_RUN'),environment=dict(runner='ubuntu-24.04',RUST_TEST_THREADS=2,job_timeout_minutes=120,fixture_timeout_seconds=2400,retries=0,structural_env=dict(RUSTFLAGS='--edition 2021 -D warnings',NO_COLOR='1',KANI_LOG='kani_compiler::kani_middle::codegen_units=debug')),always_artifacts='source before/after snapshots, full native argv/env/exits/termination/stdout/stderr, suite per-fixture logs, mutations with restore receipts, structural exports/regular inventories/receipts/summary/tool hashes, LLBC output',not_run=['fmt','build-dev','clippy','native units','Quick','sensitivity4/4','structural11/18','LLBC compile','push','dispatch'],proof_credit='NOT_ESTABLISHED',publication_authority='COORDINATOR_ONLY')
    (HERE/'CI-REQUEST.json').write_text(json.dumps(request,indent=2)+'\n')
    print('CI request pinned:',overlay)


if __name__=='__main__':main()
