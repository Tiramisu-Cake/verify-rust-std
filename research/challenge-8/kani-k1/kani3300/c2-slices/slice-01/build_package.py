#!/usr/bin/env python3
"""Build a static, exact-head handoff; never execute the listed CI commands."""
import importlib.util
import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('extract', HERE / 'extract_slice.py')
extract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(extract)
git, digest = extract.git, extract.digest
U = '0aac16ef62da9e9d5645782d458593e5d78143ba'
G0 = '4fef62ad67'


def dump(name, data):
    (HERE / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')


def identity(ref, path):
    row = git('ls-tree', ref, '--', path).decode().strip()
    if not row:
        return None
    mode, _, blob = row.split('\t')[0].split()
    return {'mode': mode, 'blob': blob, 'sha256': digest(git('cat-file', 'blob', blob))}


def main():
    head = git('rev-parse', 'HEAD').decode().strip()
    assert head != extract.B1 and git('show', '-s', '--format=%P', head).decode().strip() == extract.B1
    assert not git('status', '--porcelain')
    deps = json.loads((extract.MAP / 'DEPENDENCIES.json').read_text())
    parts = deps['slices']['1']['source_parts']
    source_map_hash = digest((extract.MAP / 'B1--F.json').read_bytes())
    dump('SOURCE-PARTS.json', {'canonical_map': '../source-map/B1--F.json', 'canonical_map_sha256': source_map_hash,
                              'parts': parts, 'semantics': 'owner1 only; see REVIEW-notes.md for syntax seams/pre-F7 writers'})
    oracle_path = HERE.parent / 'oracle-map/ORACLE-MAP.json'
    oracle = json.loads(oracle_path.read_text())
    paths = git('ls-tree', '-r', '--name-only', head, '--', 'tests').decode().splitlines()
    paths_set = set(paths)
    rs = [p for p in paths if p.endswith('.rs') and 'auxiliary' not in p.split('/')
          and p.split('/')[-1][0] not in '.#~']
    quick = json.loads((HERE.parent / 'ci/QUICK-PLAN.json').read_text())
    groups = []
    for row in quick['common']:
        suite, mode = row['suite'], row['mode']
        if mode == 'exec':
            candidates = ['/'.join(p.split('/')[:3]) for p in paths if p.startswith('tests/' + suite + '/')
                          and p.endswith('/config.yml') and len(p.split('/')) == 4]
        else:
            candidates = [p for p in rs if p.startswith('tests/' + suite + '/')]
        selected = sorted({p for p in candidates if any(f in p for f in row['filters'])}) if row['filters'] else sorted(set(candidates))
        groups.append({'name': 'common_' + suite, 'suite': suite, 'mode': mode, 'paths': selected})
    groups.extend([
        {'name': 'full_FunctionContracts', 'suite': 'kani', 'mode': 'kani',
         'paths': sorted(p for p in rs if p.startswith('tests/kani/FunctionContracts/'))},
        {'name': 'full_function_contract', 'suite': 'expected', 'mode': 'expected',
         'paths': sorted(p for p in rs if p.startswith('tests/expected/function-contract/'))},
    ])
    # Cover every upstream uninit/delayed-UB path and every explicit uninit flag,
    # including exec/cargo selectors outside the common Quick substrings.
    upstream = git('ls-tree', '-r', '--name-only', U, '--', 'tests').decode().splitlines()
    flagged = git('grep', '-l', '-e', 'uninit-checks', '-e', 'delayed_ub', '-e', 'delayed-ub', U, '--', 'tests').decode().splitlines()
    relevant = {p.split(':', 1)[1] for p in flagged}
    relevant.update(p for p in upstream if re.search(r'uninit|delayed[-_]ub', p, re.I))
    upstream_selectors = set()
    for path in relevant:
        pieces = path.split('/')
        if pieces[1] in ('script-based-pre', 'json-handler'):
            upstream_selectors.add(('exec', '/'.join(pieces[:3])))
        elif pieces[1] == 'std-checks':
            for p in upstream:
                if p.startswith('tests/std-checks/std/') and p.endswith('.expected'):
                    upstream_selectors.add(('cargo-kani', p))
        elif path in rs:
            suite = pieces[1]
            upstream_selectors.add(('expected' if suite in ('expected', 'ui') else 'kani', path))
        elif path.endswith('.expected') and path[:-9] + '.rs' in rs:
            source = path[:-9] + '.rs'
            upstream_selectors.add(('expected', source))
    by_suite = {}
    for mode, path in sorted(upstream_selectors):
        suite = path.split('/')[1]
        by_suite.setdefault((suite, mode), []).append(path)
    for (suite, mode), selected in sorted(by_suite.items()):
        groups.append({'name': 'upstream_uninit_delayed_' + suite, 'suite': suite, 'mode': mode, 'paths': selected})
    manifests = []
    for group in groups:
        rows = []
        for path in group.pop('paths'):
            mode = group['mode']
            selector = f'[{mode}] ' + path.removeprefix('tests/')
            files = [p for p in paths if p.startswith(path + '/')] if mode == 'exec' else [path]
            if mode == 'cargo-kani':
                files += [p for p in paths if p.startswith(str(Path(path).parent) + '/') and p != path]
            if mode == 'expected':
                own = str(Path(path).with_suffix('.expected'))
                fallback = str(Path(path).parent / 'expected')
                files += [p for p in (own, fallback) if p in paths_set][:1]
            records = []
            for file in sorted(set(files)):
                data = git('show', head + ':' + file)
                directives = [x for x in data.decode(errors='replace').splitlines()
                              if re.match(r'\s*//\s*(kani-flags|compile-flags|ignore|xfail)', x)]
                records.append({'path': file, 'identity': identity(head, file), 'original_directives': directives})
            ignored = 'fixme' in path or 'ignore' in path
            rows.append({'selector': selector, 'input': path, 'files': records,
                         'existing_path_ignore': ignored, 'result': 'NOT_RUN'})
        group.update(static_discovery_count=len(rows), existing_path_ignored=sum(r['existing_path_ignore'] for r in rows), selectors=rows)
        manifests.append(group)
    dump('TEST-MANIFEST.json', {'source_sha': head, 'discovery': 'Static tracked-path expansion following compiletest main.rs; native discovery NOT_RUN. Counts are selectors, not harness/property counts.',
                                'flag_policy': 'Original flags and goldens; no extra uninit flags, no new ignores or weakened checks. --force-rerun prevents cached ignores.',
                                'groups': manifests, 'active_call_units': json.loads((HERE / 'STATIC-VALIDATION.json').read_text())['active_call_unit_names'],
                                'upstream_uninit_delayed_inputs': sorted(relevant), 'unit_expected_count': 9,
                                'qualification_kind': 'NO_REGRESSION', 'runtime': 'NOT_RUN'})
    obligation_prefixes = ('ordinary-slots/', 'points-to-cycles/', 'contract-immutable-masks/', 'contract-modes/',
                           'root-composition/', 'private-transfer-frame/', 'maybe-uninit-contract-', 'closure-upvars/', 'closure-zst/')
    obligation_exact = {'transfer-qualification/legal-ordinary', 'transfer-qualification/legal-pfc',
                        'transfer-qualification/postcondition-hole', 'marker-hook-calls/generated-modifies-no-shadow'}
    obligations = []
    for row in oracle['fixtures']:
        if not (row['id'].startswith(obligation_prefixes) or row['id'] in obligation_exact):
            continue
        required_head = row['earliest_runnable_head']
        assert required_head in (4, 5), row['id']
        source, golden = row['input'], row['golden']
        assert source not in paths_set and golden not in paths_set, row['id']
        obligations.append({
            'id': row['id'], 'owner_slice': row['owner_slice'], 'integration_head': required_head,
            'status': 'PENDING', 'source': {'path': source, **identity(extract.F, source)},
            'golden': {'path': golden, **identity(extract.F, golden)}, 'flags': row['flags'],
            'useful_assertions': row['source_assertions'], 'contracts_and_covers': row['source_contracts_and_covers'],
            'oracle': row['oracle'], 'special_requirements': row['special_requirements'],
            'source_parts': {'file': 'SOURCE-PARTS.json', 'sha256': digest((HERE / 'SOURCE-PARTS.json').read_bytes()),
                             'owner': '1', 'binding': 'Static feature/dependency link, not AST/MIR binding'},
            'closure_receipt': None,
        })
    assert len([r for r in obligations if r['integration_head'] == 4]) == 7
    dump('DEFERRED-OBLIGATIONS.json', {'status': 'PENDING', 'integration_heads': [4, 5],
                                    'source_sha': head, 'reference_F': extract.F, 'obligations': obligations,
                                    'closure_requires': 'Exact cumulative head4/5 and run receipt; useful SUCCESS and exact intended negatives; unchanged slice1 part hashes. Aggregate exit0 and synthetic units do not close an obligation.'})
    static = json.loads((HERE / 'STATIC-VALIDATION.json').read_text())
    changed = git('diff', '--name-only', extract.B1, head).decode().splitlines()
    dump('SLICE.json', {
        'slice': 1, 'name': 'ANALYSIS S3+CC1/2/4', 'source_sha': head, 'source_tree': static['source_tree'],
        'base_sha': extract.B1, 'parents': [extract.B1], 'reference_F': extract.F,
        'reference_F_tree': '9829702c1aa0ecb73c860fc0ad5451757917d6cb',
        'g0_input': G0, 'source_map_input': 'bf455494e449c8c60c23a9e6db1e19bc809c0458',
        'oracle_map_input': 'd1dbc70afd797457ada49fb651ac98d5d338d2de', 'dependency_decision': 'TASK variant C @4fef62ad67',
        'dependents': [2, 3, 4, 5, 6, 7], 'changed_files': changed, 'changed_hunks': 'SOURCE-PARTS.json',
        'tests': 'TEST-MANIFEST.json', 'docs': [], 'borrowed_prerequisite': [],
        'syntax_adaptations': ['Split combined baseline CheckType import with exact pre-F7 import',
                               'Keep baseline shim/diagnostic helpers and replace resolver in its original location',
                               'Failed-root write uses real historical cache insertion until F7; ordinary writer unchanged'],
        'qualification_kind': 'NO_REGRESSION', 'qualification_status': 'NOT_RUN', 'integration_status': 'PENDING',
        'integration_heads': [4, 5], 'deferred_obligations': obligations,
        'tested_selectors': [], 'tested_selectors_note': 'No native tests executed; exact required selectors and input/golden hashes are in TEST-MANIFEST.json.',
        'required_test_selectors_manifest': {'path': 'TEST-MANIFEST.json', 'sha256': digest((HERE / 'TEST-MANIFEST.json').read_bytes())},
        'source_patch': {'path': 'source.patch', 'sha256': static['source.patch_sha256']},
        'residual_to_F': {'path': 'residual-to-F.patch', 'direction': 'slice1 -> F', 'sha256': static['residual-to-F.patch_sha256'],
                          'remaining_owners': [2, 3, 4, 5, 6, 7], 'full_recomposition': 'NOT_RUN'},
        'static_validation': 'PASS_STATIC_ONLY', 'independent_review': 'PENDING_WORKER15',
        'CI': 'NOT_RUN', 'push': 'NOT_RUN', 'builds': 'NOT_RUN_PROHIBITED', 'formal_proof_credit': 'NOT_ESTABLISHED',
    })
    corrections = {
        'input_oracle_map_sha256': digest(oracle_path.read_bytes()), 'input_commit': 'd1dbc70afd',
        'decision': 'TASK variant C @4fef62ad67', 'authoritative_map_area': 'worker15; not edited by worker14',
        'updates_required': ['head1 full FunctionContracts/function-contract rather than old 25/12 smoke',
                             'head1 NO_REGRESSION; actual MIR integration deferred to4/5',
                             'head3 nested Pat/enum/raw-eq-uninit pending until4',
                             'marked-model initialized/hole earliest head4, not old6; V420-424 prerequisite belongs4',
                             'generated-modifies-no-shadow stays5',
                             'source feature hunk hashes must refresh against corrected canonical map; F7 failed-root writer is F212, not213'],
        'complete_slice1_deferred_manifest': 'DEFERRED-OBLIGATIONS.json',
        'complete_required_slice1_selectors': 'TEST-MANIFEST.json', 'new_runtime_observations': 'NONE',
    }
    dump('ORACLE-DELTA.json', corrections)
    counts = [(r['name'], r['static_discovery_count'], r['existing_path_ignored']) for r in manifests]
    lines = ['# Slice1 exact-head CI request (coordinator / worker15 only)', '',
             f'Source `{head}`, tree `{static["source_tree"]}`, parent existing B1 `{extract.B1}`.',
             'Prepared request only: no CI overlay, push, dispatch, local build or native execution in this session.', '',
             'Qualification: **NO_REGRESSION**. Integration **PENDING on heads4/5**; exact source/golden/part hashes and closure conditions are in SLICE.json and DEFERRED-OBLIGATIONS.json.', '',
             'Use accepted recipe `.github/workflows/uninit-quick.yml` @0998b98867 with an exact-parent CI-only overlay. Stock workflows remain in source. ubuntu-24.04; RUST_TEST_THREADS=2; job cap120min; per-test2400s; no auto retries. fmt -> build-dev -> clippy workspace/tests -D warnings -> ActiveCalls9 -> all manifest selectors. Preserve solver/checks, original per-test flags/object-bits; no extra uninit flag on contract tests.', '',
             'TEST-MANIFEST.json supersedes the stage0 bounded smoke list for this source head. Every listed selector is required; groups overlap and can be deduplicated by exact suite/mode/selector. Static counts are discovery expectations, not observed passes. Native ignored counts must match existing directives/paths; zero selected units is failure.', '',
             '| Group | Static selectors | Existing path ignores |', '|---|---:|---:|']
    lines.extend(f'| {name} | {count} | {ignored} |' for name, count, ignored in counts)
    lines += ['', 'Compiler unit request: `cargo test -p kani-compiler active_call_tests` -> exactly9 tests, 9 passed/0 failed/0 ignored required. This does not exercise compiler MIR integration.', '',
              'For each group invoke compiletest with its manifest suite/mode, `--exact --force-rerun --no-fail-fast --timeout 2400`, and the exact full selector strings in `selectors[].selector`. Retain all original flags/goldens. Run full kani FunctionContracts and full expected/function-contract; the old12 expected smoke list is insufficient. The upstream uninit inventory also reaches verify_std_cmd and std-checks/std expected selectors via their existing uninit settings; preserve their native cargo/exec modes.', '',
              'Upload original argv, exit, termination reason, native discovery/counts, unit and fixture output, and source/tree/manifest/dirty identities before and after with always. Preserve actual compiletest output/build-base paths; no stale Part1 JSON-only artifacts. Missing/partial/timeout output is NOT_RUN/UNKNOWN, not PASS. A reached ordinary regression, new false SUCCESS, extra Unsupported or lost assertion is STOP; no new ignore/filter/golden updates.', '',
              'Worker15 owns independent review and CI-only overlay. ORACLE-DELTA.json supplies pending stage0-map refresh items without editing its research area. No new Gate A, SmallSort proof or structural F7 credit is claimed.']
    (HERE / 'CI-REQUEST.md').write_text('\n'.join(lines) + '\n')
    print(json.dumps({'source': head, 'groups': counts, 'deferred_by_head': dict(Counter(r['integration_head'] for r in obligations)),
                      'upstream_uninit_unique_selectors': len(upstream_selectors)}, indent=2))


if __name__ == '__main__':
    main()
