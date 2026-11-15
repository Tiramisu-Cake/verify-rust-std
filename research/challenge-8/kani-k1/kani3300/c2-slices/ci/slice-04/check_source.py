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
SOURCE = '345cedfd67df679e326474385308349d609fc43d'
BASE = '5ca51679e3f433718807a2e44add0d5abac128e7'
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
    source = load('slice-04/SLICE.json')
    assert source['source_sha'] == SOURCE and source['base_sha'] == BASE
    assert git('show', '-s', '--format=%P', SOURCE).decode().strip() == BASE
    assert git('rev-parse', SOURCE + '^{tree}').decode().strip() == source['source_tree']
    spec = importlib.util.spec_from_file_location('extract4', PACKET / 'slice-04/extract_slice.py')
    extraction = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(extraction)
    extraction.check_parent()
    expected = extraction.extract()  # Pure composition; never invoke writer main.
    for path, data in expected.items():
        assert git('show', SOURCE + ':' + path) == data, path
    inventory = extraction.prior.effective_inventory()
    parts = [(f['path'], p) for f in inventory['files'] for h in f['hunks'] for p in h['parts'] if p['owner'] == '4']
    assert len(parts) == 180
    for path, p in parts:
        revision = F if p['side'] == '+' else extraction.B1
        lines = git('show', revision + ':' + path).splitlines(keepends=True)
        assert hashlib.sha256(b''.join(lines[p['start']-1:p['start']-1+p['count']])).hexdigest() == p['sha256'], (path,p)
    selected, deferred = extraction.fixture_sets()
    assert len(selected) == 99 and len(deferred) == 47
    all_fixture_paths = {r[k] for r in selected for k in ['input','golden']}
    for row in selected:
        for k in ['input','golden']:
            assert git('show', SOURCE + ':' + row[k]) == git('show', F + ':' + row[k]), row[k]
    for row in deferred:
        assert not git('ls-tree', SOURCE, '--', row['input'])
        assert not git('ls-tree', SOURCE, '--', row['golden'])
    delta = dict(line.split('\t',1)[::-1] for line in git('diff','--name-status',BASE,SOURCE).decode().splitlines())
    production = {p for p in delta if p.startswith(('kani-compiler/','library/'))}
    docs = {p for p in delta if p.startswith('docs/')}
    tests = {p for p in delta if p.startswith('tests/')}
    assert len(delta) == 204 and len(production) == 8 and len(docs) == 2
    assert set(delta) == production | docs | tests
    assert tests <= all_fixture_paths
    changed_existing = {p for p in tests if delta[p] == 'M'}
    assert changed_existing == {'tests/expected/uninit/unresolved-calls/entry-' + kind + '-' + mode + '.rs' for kind in ['initialized','partial'] for mode in ['plain','seeded']}
    assert sum(delta[p] == 'A' for p in tests) == 190
    for p in production:
        if p.endswith('ty_layout.rs') or p.endswith('delayed_ub/mod.rs'):
            continue
        assert git('show',SOURCE+':'+p) == git('show',F+':'+p), p
    manifest = load('slice-04/TEST-MANIFEST.json')
    previous, current = grouped(load('slice-03/TEST-MANIFEST.json')), grouped(manifest)
    assert manifest['source_sha'] == SOURCE
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
    assert len(inherited_updates) == 4
    additions = {s for key,rows in current.items() for s in rows if s not in previous[key]}
    assert len(additions) == 95
    assert {'[expected] ' + r['input'].removeprefix('tests/') for r in selected} <= set(current[('expected','expected')])
    # Full present uninit discovery: .rs files excluding auxiliary dirs, no hidden omissions.
    tracked = git('ls-tree','-r','--name-only',SOURCE,'--','tests/expected/uninit').decode().splitlines()
    discovered = {'[expected] '+p.removeprefix('tests/') for p in tracked if p.endswith('.rs') and '/auxiliary/' not in p}
    assert discovered == {s for s in current[('expected','expected')] if s.startswith('[expected] expected/uninit/')}
    files = {f['path']: f['identity'] for rows in current.values() for row in rows.values() for f in row['files']}
    for path, identity in files.items():
        assert hashlib.sha256(git('show',SOURCE+':'+path)).hexdigest() == identity['sha256'], path
    counts = {key[0]: [len(rows),sum(r['existing_path_ignore'] for r in rows.values())] for key,rows in current.items()}
    assert counts == {'kani':[53,3], 'expected':[321,6], 'ui':[17,0], 'script-based-pre':[3,0], 'json-handler':[17,0], 'std-checks':[2,0]}
    subprocess.run(['git','-C',str(REPO),'diff','--check',BASE,SOURCE],check=True)
    report = dict(status='PASS_STATIC_ONLY',source_sha=SOURCE,source_tree=source['source_tree'],base_sha=BASE,
        changed_files=len(delta), production_files=len(production), owner4_parts=len(parts), exact_F_fixture_pairs=len(selected),
        new_fixture_pairs=95, existing_source_updates=sorted(changed_existing), manifest_file_identities=len(files),
        cumulative_selectors=413, preexisting_ignores=9, suite_counts=counts, present_uninit_selectors=len(discovered),
        all_head5_pairs_absent=47, effective_targeted_units=20, packet_stale_unit_scalar=manifest['unit_expected_count'],
        checks=['read-only owner1..4 line composition and accepted parent reconstruction','180 owner4 part hashes',
                '8 production/2 docs/190 added fixture paths/4 source-only updates; no golden changes',
                '99 exact-F pairs; inherited selectors preserved;47 head5 pairs absent',
                'all manifest hashes and full present expected/uninit discovery','git diff --check'],
        native_checks='NOT_RUN', formal_proof_credit='NOT_ESTABLISHED')
    (HERE/'SOURCE-VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
