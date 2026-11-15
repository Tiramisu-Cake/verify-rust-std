#!/usr/bin/env python3
"""Worker15 read-only source/composition/manifest validation. Git/Python only."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
PACKET = HERE.parent.parent
REPO = Path('/root/kani-fix-3300-c2-slices-w15')
SOURCE = '96f5d5dc8dedd369c6986a4f1dd5e698b6167f0f'
BASE = '345cedfd67df679e326474385308349d609fc43d'
F = 'ad499e41dd2db9ccd432f89721638a1f3a0bbd44'


def git(*args):
    return subprocess.check_output(['git', '-C', str(REPO), *args])


def load(name):
    return json.loads((PACKET / name).read_text())


def grouped(manifest):
    result = {}
    for group in manifest['groups']:
        rows = result.setdefault((group['suite'], group['mode']), {})
        for row in group['selectors']:
            assert rows.setdefault(row['selector'], row) == row
    return result


def main():
    source = load('slice-05/SLICE.json')
    assert source['source_sha'] == SOURCE and source['base_sha'] == BASE
    assert git('show', '-s', '--format=%P', SOURCE).decode().strip() == BASE
    assert git('rev-parse', SOURCE + '^{tree}').decode().strip() == source['source_tree']
    spec = importlib.util.spec_from_file_location('extract4', PACKET / 'slice-05/extract_slice.py')
    extraction = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(extraction)
    extraction.check_parent()
    expected = extraction.extract()  # Pure composition; never invoke writer main.
    for path, data in expected.items():
        assert git('show', SOURCE + ':' + path) == data, path
    parts = extraction.parts()
    assert len(parts) == 2
    selected = extraction.fixtures()
    assert len(selected) == 47
    all_fixture_paths = {r[k] for r in selected for k in ['input','golden']}
    for row in selected:
        for k in ['input','golden']:
            assert git('show', SOURCE + ':' + row[k]) == git('show', F + ':' + row[k]), row[k]
    delta = dict(line.split('\t',1)[::-1] for line in git('diff','--name-status',BASE,SOURCE).decode().splitlines())
    production = {p for p in delta if p.startswith(('kani-compiler/','library/'))}
    assert production == {extraction.LAYOUT}
    assert len(delta) == 95 and set(delta) == production | all_fixture_paths
    assert all(delta[p] == 'A' for p in all_fixture_paths)
    assert git('show',SOURCE+':'+extraction.LAYOUT) == git('show',F+':'+extraction.LAYOUT)
    d1 = load('slice-01/DEFERRED-OBLIGATIONS.json')
    ids = {r['id'] for r in selected}
    assert ids == {r['id'] for r in d1['obligations'] if r['integration_head'] == 5}
    assert ids == set(load('slice-04/SLICE.json')['stage5_deferred_fixture_ids'])
    assert 'marker-hook-calls/generated-modifies-no-shadow' in ids
    features = extraction.prior.prior.effective_oracle()['source_features']
    for row in selected:
        assert not {'E1','F7'}.intersection(row['prerequisites'])
        assert all(int(features[f]['slice']) <= 5 for f in row['prerequisites'])
    docs = load('oracle-map/DOCS-MAP.json')
    assert not [s for d in docs['documents'] for s in d['added_segments'] if s['owner_slice'] == 5]
    manifest = load('slice-05/TEST-MANIFEST.json')
    previous, current = grouped(load('slice-04/TEST-MANIFEST.json')), grouped(manifest)
    assert manifest['source_sha'] == SOURCE
    changed_existing = set()
    inherited_updates = []
    for key, rows in previous.items():
        for selector, old in rows.items():
            new = current[key][selector]
            if old != new:
                a,b = dict(old),dict(new)
                af,bf = a.pop('files'),b.pop('files')
                assert a == b, selector
                assert len(af) == len(bf)
                for x,y in zip(af,bf):
                    if x != y:
                        assert x['path'] == y['path'] and y['path'] in changed_existing, (x,y)
                inherited_updates.append(selector)
    assert not inherited_updates
    additions = {s for key,rows in current.items() for s in rows if s not in previous[key]}
    assert len(additions) == 47
    assert {'[expected] ' + r['input'].removeprefix('tests/') for r in selected} <= set(current[('expected','expected')])
    # Full present uninit discovery: .rs files excluding auxiliary dirs, no hidden omissions.
    tracked = git('ls-tree','-r','--name-only',SOURCE,'--','tests/expected/uninit').decode().splitlines()
    discovered = {'[expected] '+p.removeprefix('tests/') for p in tracked if p.endswith('.rs') and '/auxiliary/' not in p}
    assert discovered == {s for s in current[('expected','expected')] if s.startswith('[expected] expected/uninit/')}
    files = {f['path']: f['identity'] for rows in current.values() for row in rows.values() for f in row['files']}
    for path, identity in files.items():
        assert hashlib.sha256(git('show',SOURCE+':'+path)).hexdigest() == identity['sha256'], path
    counts = {key[0]: [len(rows),sum(r['existing_path_ignore'] for r in rows.values())] for key,rows in current.items()}
    assert counts == {'kani':[53,3], 'expected':[368,6], 'ui':[17,0], 'script-based-pre':[3,0], 'json-handler':[17,0], 'std-checks':[2,0]}
    subprocess.run(['git','-C',str(REPO),'diff','--check',BASE,SOURCE],check=True)
    report = dict(status='PASS_STATIC_ONLY',source_sha=SOURCE,source_tree=source['source_tree'],base_sha=BASE,
        changed_files=len(delta), production_files=len(production), owner5_parts=parts, exact_F_fixture_pairs=len(selected),
        new_fixture_pairs=47, inherited_selectors_unchanged=413, manifest_file_identities=len(files),
        cumulative_selectors=460, preexisting_ignores=9, suite_counts=counts, present_uninit_selectors=len(discovered),
        all_head5_pairs_present=True, E1_F7_imported=False, effective_targeted_units=20,
        historical_obligations='PENDING_NATIVE_EXACT_HEAD5; history unchanged',
        checks=['read-only owner1..5 composition and accepted4 reconstruction', '2 owner5 source parts; only layout production delta',
                '47 exact-F pairs; all413 inherited selectors unchanged; all deferred5 fixture IDs present',
                'all manifest hashes and full present expected/uninit discovery', 'git diff --check'],
        native_checks='NOT_RUN', formal_proof_credit='NOT_ESTABLISHED')
    (HERE/'SOURCE-VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
