#!/usr/bin/env python3
"""Package worker15 review/request metadata from immutable objects. No CI invocation."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
PACKET = HERE.parent.parent
ROOT = PACKET.parent
REPO = Path('/root/kani-fix-3300-c2-slices-w15')


def git(*args):
    return subprocess.check_output(['git', '-C', str(REPO), *args])


def save(name, data):
    (HERE / name).write_text(json.dumps(data, indent=2) + '\n')


def load(name):
    return json.loads((PACKET / name).read_text())


def main():
    spec = importlib.util.spec_from_file_location('ci', REPO / '.github/c2-slices/slice04_ci.py')
    ci = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ci)
    config, manifest = ci.inputs()
    source = config['source_sha']
    overlay = git('rev-parse', 'HEAD').decode().strip()
    tree = git('rev-parse', 'HEAD^{tree}').decode().strip()
    with tempfile.TemporaryDirectory() as tmp:
        ci.snapshot('static', Path(tmp))
        snap = json.loads((Path(tmp) / 'source-static.json').read_text())
    prior = git('show', config['accepted_recipe_overlay'] + ':.github/c2-slices/slice03_ci.py').decode()
    current = (REPO / '.github/c2-slices/slice04_ci.py').read_text()
    for action, unit in config['additional_units'].items():
        line = '    ' + repr(action) + ': ' + repr(ci.COMMANDS[action]) + ',\n'
        assert current.count(line) == 1
        current = current.replace(line, '')
    extra = '        elif action in config["additional_units"]:\n            expected = {n: False for n in config["additional_units"][action]["native_names"]}\n'
    assert current.count(extra) == 1 and current.replace(extra, '') == prior
    save('STATIC-VALIDATION.json', dict(status='PASS_STATIC_AND_SYNTHETIC_ONLY', overlay_sha=overlay, overlay_tree=tree,
        source_sha=source, accepted_recipe=config['accepted_recipe_overlay'], accepted_run='43706759714',
        runner_synthetic_checks=21, seam_checker_synthetic_checks=10, source_manifest_byte_identical=True,
        protected_source_entries=len(snap['files']), source_snapshot_problems=snap['problems'],
        runner_delta='Only2 command entries and exact-name branch for2 new unit filters; prior execution/output/source-guard logic byte-identical.',
        sensitivity='DEFERRED_HEAD5_FULL_STRONG_SET_ABSENT', native_checks='NOT_RUN', push_dispatch='NOT_RUN', cloud_spend=0))
    sources = sorted(x for x in git('diff', '--name-only', config['source_parent'], source, '--', 'tests').decode().splitlines() if x.endswith('.rs'))
    rows = []
    for path in sources:
        text = git('show', source + ':' + path).decode()
        assert not any('#[kani::' + kind in text for kind in ['requires', 'ensures', 'modifies'])
        hits = [{'line': i, 'text': line.strip()} for i, line in enumerate(text.splitlines(), 1) if '|' in line and not line.strip().startswith('//')]
        if hits:
            rows.append({'path': path, 'closure_syntax': hits})
    assert len(rows) == 7
    strong = [r['proposed_selector'] for r in json.loads((ROOT / 'c2-s5/ORACLE-MAP.json').read_text())['rows'][:8]]
    assert len(set(strong)) == 8
    for path in strong:
        assert not git('ls-tree', source, '--', path), path
    save('FIXTURE-REVIEW.json', dict(status='PASS_BOUNDED_STATIC_DEPENDENCY_REVIEW', source_sha=source,
        reviewers=['worker15', 'independent Luna HIGH read-only fixture helper'], changed_fixture_sources=sources,
        source_list_sha256=hashlib.sha256(('\n'.join(sources) + '\n').encode()).hexdigest(),
        fixture_pairs=99, new_pairs=95, modified_sources_unchanged_goldens=4, closure_syntax_sources=rows,
        closure_syntax_source_count=7,
        guard_trace={'carrier': 'transfers_shadow only union or maybe_uninit_storage, not Closure',
            'assignment_and_nested_reset': 'Only Err(UnionAsField) triggers boundary; Closure fallback is UnsupportedType',
            'delayed_entry': 'Requires Ok(PointeeLayout::Sized); UnsupportedType closure does not seed setter',
            'item_return': 'Four capture-free Item bodies transfer MU return via stage4; closure env is not tracked byte payload',
            'intended_shim_negatives': 'pairing-unsupported and2 tuple cases retain exact-F conservative golden; no closure masks needed',
            'contracts': 'No changed fixture has requires/ensures/modifies; no contract macro capture-layout obligation'},
        helper_count_correction='Helper enumerated7 paths but called them6; main independent recount confirms7. Substantive conclusion unchanged.',
        missing_strong_oracles=strong, sensitivity_status='DEFERRED_HEAD5', native_lowering_typecheck='NOT_RUN',
        limits='Static dependency review, not runtime qualification. Unexpected closure/layout Unsupported in CI is STOP, never a golden change.'))
    suites = []
    for (suite, mode), selectors in ci.suites(manifest).items():
        suites.append(dict(suite=suite, mode=mode, discovery=len(selectors), existing_ignored=sum(r['existing_path_ignore'] for r in selectors.values()),
            expected_passed_if_green=sum(not r['existing_path_ignore'] for r in selectors.values()), selectors=list(selectors),
            argv=['cargo', 'run', '-p', 'compiletest', '--quiet', '--', '--suite', suite, '--mode', mode,
                '--build-base', '${C2_EVIDENCE_DIR}/build-tests/' + suite, '--logfile', '${C2_EVIDENCE_DIR}/suite-' + suite + '.native.log',
                '--color', 'never', '--exact', '--force-rerun', '--no-fail-fast', '--timeout', '2400', *selectors]))
    units = [dict(action='units', filter='active_call_tests', native_names=['kani_middle::points_to::points_to_analysis::active_call_tests::' + n for n in manifest['active_call_units']]),
             dict(action='immutable-units', filter='immutable_allocations::tests', native_names=['codegen_cprover_gotoc::context::immutable_allocations::tests::' + n for n in manifest['immutable_unit_names']]),
             *[dict(action=action, **unit) for action, unit in config['additional_units'].items()]]
    for unit in units:
        unit.update(expected_passed=len(unit['native_names']), expected_failed=0, expected_ignored=0)
    selected = load('slice-04/ORACLE-DELTA.json')['selected_complete_fixtures']
    target = []
    for row in selected:
        src, golden = (git('show', source + ':' + row[k]) for k in ['input', 'golden'])
        target.append(dict(input=row['input'], golden=row['golden'], selector='[expected] ' + row['input'].removeprefix('tests/'),
            owner_slice=row['owner_slice'], earliest_runnable_head=4, source_sha256=hashlib.sha256(src).hexdigest(), golden_sha256=hashlib.sha256(golden).hexdigest(),
            source_harness_count=row['source_harness_count'], exact_failure_N=[int(n) for n in re.findall(rb'\*\* (\d+) of', golden)],
            golden_verdicts=re.findall(r'VERIFICATION:- (SUCCESSFUL|FAILED)', golden.decode()), native_result='NOT_RUN'))
    assert len(target) == 99
    save('CI-REQUEST.json', dict(inputs=dict(config, overlay_sha=overlay, overlay_tree=tree, branch='uninit-ci/c2-slices-04-w15'),
        stage_commands=ci.COMMANDS, units=units, suites=suites, targeted_stage4_fixtures=target,
        integration_obligations=load('slice-04/DEFERRED-OBLIGATIONS.json'),
        sensitivity=dict(status='DEFERRED_HEAD5', missing_strong_oracles=strong, mutations_required=4, force_rerun_required=True, reason='No full strong set on4; no substitute checks qualify4/4.'),
        recipe=dict(accepted_overlay=config['accepted_recipe_overlay'], accepted_run='43706759714', runner_delta='2 unit commands/expected branches only', workflow_delta='stage4 names/count/artifacts and2 unit steps', runner='ubuntu-24.04', job_timeout_minutes=120, per_fixture_timeout_seconds=2400, RUST_TEST_THREADS=2, auto_retries=0),
        qualification_review_required=['413 selectors;404 passes+9 existing ignores if green;20 units exact full names',
            'Native fmt/build/clippy and compile-seams; source before/after identical',
            'All99 target pairs: useful SUCCESS and exact intended failures, no unrelated Unsupported/layout/protocol substitutes',
            'Owner1 seven and owner3 nine plus18 moved pairs only close through explicit per-fixture exact-head receipts',
            'F6 two read negatives+reinit; Copy false preservation; padding/stride; mandatory return0; Hook-only refusal vs marked model',
            'Any unexpected closure5 prerequisite is STOP;47 absent head5 pairs remain pending'],
        artifacts=dict(always_upload=True, path='${runner.temp}/c2-slices-04-evidence/', name='c2-slices-04-${github.run_id}-${github.run_attempt}',
            required=['inputs.json', 'test-manifest.json', 'source-before.json', 'source-after.json', 'per-stage result.json with original argv/exit/termination reason', 'stdout.txt and stderr.txt', 'suite native logs', 'actual build-tests per-fixture outputs', 'runner-errors when present'], not_started='NOT_RUN/null exit/NOT_STARTED', successful_runner='EXIT_ZERO_COUNTS_MATCH_REQUIRES_REVIEW'),
        static_validation_refs={n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in ['SOURCE-VALIDATION.json','SEAM-VALIDATION.json','STATIC-VALIDATION.json','FIXTURE-REVIEW.json','check_source.py','check_overlay.py','prepare_overlay.py']},
        authorization='Local overlay and g0 commits only; coordinator alone may push/dispatch. No local native build, push or CI run performed.'))
    (HERE / 'overlay.patch').write_bytes(git('diff', '--binary', source, 'HEAD'))
    print(json.dumps(dict(overlay_sha=overlay, overlay_tree=tree, protected_source_entries=len(snap['files']), selectors=sum(s['discovery'] for s in suites), units=sum(u['expected_passed'] for u in units), fixture_pairs=len(target), sensitivity='DEFERRED_HEAD5')))


if __name__ == '__main__':
    main()
