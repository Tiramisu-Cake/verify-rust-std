#!/usr/bin/env python3
"""Read-only exact-commit review checks. No author validator or compiler execution."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
PACKET = HERE.parent.parent
REPO = Path('/root/kani-fix-3300-c2-slices-w15')
SOURCE = '932fb8395a58f8c86c0d702ba2cae835823b2962'
PARENT = 'd82752c8bc878398e672bffaa631ca6a28430acc'
F = 'ad499e41dd2db9ccd432f89721638a1f3a0bbd44'
B1 = '6fe484b30043b3696b5f1ccc4bea0e42891ad012'


def git(*args):
    return subprocess.check_output(['git', '-C', str(REPO), *args])


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads((PACKET / path).read_text())


def blob(ref, path):
    return git('show', ref + ':' + path)


def main():
    source_slice = read('slice-02/SLICE.json')
    assert git('rev-parse', SOURCE + '^').decode().strip() == PARENT
    assert git('rev-parse', PARENT + '^').decode().strip() == B1
    assert git('rev-parse', SOURCE + '^{tree}').decode().strip() == source_slice['source_tree']
    for path, digest in source_slice['maps'].items():
        assert sha((PACKET / path).read_bytes()) == digest, path
    inventory = read('source-map/B1--F.json')
    expected_parts = [dict(hunk_id=h['id'], part_index=i, path=f['path'], **p)
                      for f in inventory['files'] for h in f['hunks']
                      for i, p in enumerate(h['parts']) if p['owner'] == '2']
    parts = read('slice-02/SOURCE-PARTS.json')['parts']
    assert parts == expected_parts and len(parts) == 54
    for p in parts:
        data = blob(F if p['side'] == '+' else B1, p['path']).splitlines(keepends=True)
        assert sha(b''.join(data[p['start'] - 1:p['start'] - 1 + p['count']])) == p['sha256']
    # Reconstruct allowed parts without executing author main()/write paths.
    spec = importlib.util.spec_from_file_location('extract_static', PACKET / 'slice-02/extract_slice.py')
    extractor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(extractor)
    extractor.REPO = REPO
    expected = extractor.extract()
    for path, data in extractor.extract(('1',)).items():
        assert blob(PARENT, path) == data, path
    for path, data in expected.items():
        assert blob(SOURCE, path) == data, path
    changed = git('diff', '--name-only', PARENT, SOURCE).decode().splitlines()
    assert set(changed) == {r['path'] for r in source_slice['changed_files']}
    assert len(changed) == 29
    assert not git('diff', '--name-only', '--diff-filter=CDMRTUXB', PARENT, SOURCE, '--', 'tests')
    protected = ['library', '.github', 'scripts', 'Cargo.toml', 'Cargo.lock', 'rust-toolchain.toml',
                 'kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit',
                 'kani-compiler/src/kani_middle/transform/check_uninit/relevant_instruction.rs',
                 'kani-compiler/src/kani_middle/kani_functions.rs',
                 'kani-compiler/src/kani_middle/transform/delayed_cache.rs',
                 'kani-compiler/src/codegen_aeneas_llbc', 'docs/src/rust-feature-support/intrinsics.md']
    assert not git('diff', '--name-only', PARENT, SOURCE, '--', *protected)
    layout = 'kani-compiler/src/kani_middle/transform/check_uninit/ty_layout.rs'
    start = b'fn data_bytes_for_ty'
    assert blob(SOURCE, layout).split(start, 1)[1] == blob(PARENT, layout).split(start, 1)[1]
    delayed = 'kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/mod.rs'
    for item in read('source-map/PRE-F7.json')['snippets']:
        assert blob(SOURCE, delayed).count(item['text'].encode()) == 1
    interface = blob(SOURCE, 'kani-compiler/src/codegen_cprover_gotoc/compiler_interface.rs')
    assert b'delayed_scope' not in interface
    assert b'replace_delayed_body' not in blob(SOURCE, delayed)
    lifecycle = [b'gcx.prepare_immutable_allocations(&items)', b'gcx.handle_quantifiers()',
                 b'gcx.finalize_immutable_allocations()', b'let pretty_name_map:', b'gcx.split()']
    assert [interface.index(s) for s in lifecycle] == sorted(interface.index(s) for s in lifecycle)
    oracle = read('oracle-map/ORACLE-MAP.json')
    fixtures = [r for r in oracle['fixtures'] if r['owner_slice'] == 2 and r['earliest_runnable_head'] == 2]
    assert len(fixtures) == 6
    assert {r['id'] for r in fixtures} == set(source_slice['selected_complete_fixture_ids'])
    for row in fixtures:
        for path in (row['input'], row['golden']):
            assert blob(SOURCE, path) == blob(F, path), path
    for row in source_slice['deferred_owner2_fixtures'] + source_slice['later_owner_immutable_consumers']:
        canonical = next(r for r in oracle['fixtures'] if r['id'] == row['id'])
        for k, v in canonical.items():
            assert row[k] == v, (row['id'], k)
        assert row['integration_status'] == 'PENDING' and row['result'] == 'NOT_RUN'
        for path in (row['input'], row['golden']):
            assert not git('ls-tree', SOURCE, '--', path)
        assert sha(blob(F, row['input'])) == row['source']['sha256']
        assert sha(blob(F, row['golden'])) == row['golden_identity']['sha256']
    manifest = read('slice-02/TEST-MANIFEST.json')
    previous = read('slice-01/TEST-MANIFEST.json')
    unique = {s['selector']: s for g in manifest['groups'] for s in g['selectors']}
    inherited = {s['selector']: s for g in previous['groups'] for s in g['selectors']}
    assert all(unique[k] == v for k, v in inherited.items())
    assert len(unique) == 317 and len(inherited) == 311
    assert {unique[k]['input'] for k in unique.keys() - inherited.keys()} == {r['input'] for r in fixtures}
    all_uninit = {p for p in git('ls-tree', '-r', '--name-only', SOURCE, '--', 'tests/expected/uninit').decode().splitlines() if p.endswith('.rs')}
    assert all_uninit == {s['input'] for s in unique.values() if s['input'].startswith('tests/expected/uninit/')}
    unit_source = blob(SOURCE, 'kani-compiler/src/codegen_cprover_gotoc/context/immutable_allocations.rs').decode()
    assert re.findall(r'#\[test\]\s+fn (\w+)', unit_source) == manifest['immutable_unit_names']
    assert len(manifest['immutable_unit_names']) == 9
    for name, base, target in [('source.patch', PARENT, SOURCE), ('residual-to-F.patch', SOURCE, F)]:
        assert (PACKET / 'slice-02' / name).read_bytes() == git('diff', '--no-ext-diff', '--no-renames', '--full-index', '--binary', '--unified=0', base, target)
    subprocess.run(['git', '-C', str(REPO), 'diff', '--check', PARENT, SOURCE], check=True)
    print(json.dumps({'status': 'PASS_STATIC_ONLY', 'source_sha': SOURCE,
                      'source_tree': source_slice['source_tree'], 'parent': PARENT,
                      'owner2_parts': len(parts), 'changed_files': len(changed),
                      'selected_fixtures': len(fixtures), 'deferred_owner2': 16, 'later_consumers': 11,
                      'inherited_selectors': len(inherited), 'cumulative_selectors': len(unique),
                      'source_mutations': 'NONE', 'native_build_units_verifier_CI': 'NOT_RUN'}, indent=2))


if __name__ == '__main__':
    main()
