#!/usr/bin/env python3
"""Read-only candidate/ownership/manifest checks. No native tools or source writes."""
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
SOURCE = 'd0345ddf4f70d10caf5ee34ddca402867264379e'
BASE = '932fb8395a58f8c86c0d702ba2cae835823b2962'
F = 'ad499e41dd2db9ccd432f89721638a1f3a0bbd44'


def git(*args):
    return subprocess.check_output(['git', '-C', str(REPO), *args])


def load(name):
    return json.loads((PACKET / name).read_text())


def grouped(manifest):
    result = {}
    for group in manifest['groups']:
        key = (group['suite'], group['mode'])
        rows = result.setdefault(key, {})
        for row in group['selectors']:
            assert rows.setdefault(row['selector'], row) == row
    return result


def main():
    source = load('slice-03/SLICE.json')
    assert source['source_sha'] == SOURCE and source['base_sha'] == BASE
    assert git('show', '-s', '--format=%P', SOURCE).decode().strip() == BASE
    assert git('rev-parse', SOURCE + '^{tree}').decode().strip() == source['source_tree']
    changed = set(git('diff', '--name-only', BASE, SOURCE).decode().splitlines())
    prefix = 'kani-compiler/src/kani_middle/transform/check_uninit/'
    production = {prefix + n for n in ['delayed_ub/initial_target_visitor.rs', 'mod.rs',
        'ptr_uninit/uninit_visitor.rs', 'relevant_instruction.rs', 'ty_layout.rs']}
    assert {p for p in changed if p.startswith('kani-compiler/')} == production
    # Re-execute the line-part composer read-only, comparing Git objects rather than
    # trusting the author's validation report or altering the worker14 checkout.
    spec = importlib.util.spec_from_file_location('extract3', PACKET / 'slice-03/extract_slice.py')
    extraction = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(extraction)
    extraction.check_parent()
    expected = extraction.extract()
    for path, data in expected.items():
        assert git('show', SOURCE + ':' + path) == data, path
    for part in extraction.parts_for('3'):
        ref = F if part['side'] == '+' else extraction.B1
        lines = git('show', ref + ':' + part['path']).splitlines(keepends=True)
        raw = b''.join(lines[part['start'] - 1:part['start'] - 1 + part['count']])
        assert hashlib.sha256(raw).hexdigest() == part['sha256']
    assert len(extraction.parts_for('3')) == 22
    quick = load('ci/QUICK-PLAN.json')
    head3 = next(h for h in quick['heads'] if h['head'] == 3)
    selected = head3['new_or_changed_final_fixture_pairs']
    assert len(selected) == 19
    fixtures = {r[k] for r in selected for k in ['input', 'golden']}
    assert changed == production | fixtures | {'docs/src/rust-feature-support/intrinsics.md'}
    verdicts = {'SUCCESSFUL': 0, 'FAILED': 0}
    for path in fixtures:
        assert git('show', SOURCE + ':' + path) == git('show', F + ':' + path), path
        if path.endswith('.expected'):
            data = git('show', SOURCE + ':' + path).decode()
            verdicts['SUCCESSFUL' if 'VERIFICATION:- SUCCESSFUL' in data else 'FAILED'] += 1
    assert verdicts == {'SUCCESSFUL': 10, 'FAILED': 9}
    assert not git('diff', '--name-only', '--diff-filter=CDMRTUXB', BASE, SOURCE, '--', 'tests')
    for row in source['deferred_owner3_fixtures']:
        for key in ['input', 'golden']:
            assert not git('ls-tree', SOURCE, '--', row[key])
    assert len(source['deferred_owner3_fixtures']) == 9
    manifest = load('slice-03/TEST-MANIFEST.json')
    previous = grouped(load('slice-02/TEST-MANIFEST.json'))
    current = grouped(manifest)
    assert manifest['source_sha'] == SOURCE
    for key, rows in previous.items():
        for selector, row in rows.items():
            assert current[key][selector] == row, selector
    added = {s for key, rows in current.items() for s in rows if s not in previous[key]}
    assert added == {r['selector'] for r in selected}
    files = {f['path']: f['identity'] for rows in current.values() for row in rows.values() for f in row['files']}
    for path, identity in files.items():
        assert hashlib.sha256(git('show', SOURCE + ':' + path)).hexdigest() == identity['sha256'], path
    counts = {key[0]: [len(rows), sum(r['existing_path_ignore'] for r in rows.values())]
              for key, rows in current.items()}
    assert counts == {'kani': [53, 3], 'expected': [244, 6], 'ui': [17, 0],
                      'script-based-pre': [3, 0], 'json-handler': [17, 0], 'std-checks': [2, 0]}
    subprocess.run(['git', '-C', str(REPO), 'diff', '--check', BASE, SOURCE], check=True)
    report = dict(status='PASS_STATIC_ONLY', source_sha=SOURCE, source_tree=source['source_tree'],
        base_sha=BASE, changed_files=len(changed), production_files=len(production), owner3_parts=22,
        selected_whole_fixture_pairs=19, deferred_whole_fixture_pairs=9,
        golden_verdicts=verdicts, cumulative_selectors=336, preexisting_ignores=9,
        manifest_file_identities=len(files), suite_counts=counts,
        checks=['read-only line-part recomposition', 'effective part hashes with neutral import correction',
                'exact changed-path boundary', 'all existing tests unchanged', '19 pairs exact F',
                'all inherited selectors/identities unchanged', 'Quick head3 additions exact',
                'all manifest file hashes', 'deferred9 absent', 'git diff --check'],
        native_compile_tests='NOT_RUN', formal_proof_credit='NOT_ESTABLISHED')
    (HERE / 'SOURCE-VALIDATION.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
