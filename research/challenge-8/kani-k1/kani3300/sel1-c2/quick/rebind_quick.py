#!/usr/bin/env python3
"""Rebuild reviewed Q input identities from exact Git objects. No toolchain/write to source."""
from pathlib import Path
from collections import Counter
import hashlib
import importlib.util
import json
import re
import subprocess

HERE = Path(__file__).resolve().parent
REPO = Path('/root/kani-fix-3300-sel1-c2-w15')
SOURCE = '14bc57fdb99960240c4944845a3d985c8af4dcf7'
TREE = '1efb6e4dfa69d346df8e23741d11839b1932403d'
BASE = '8e299aa6243bc5f06a29c51e98aafa9564478220'
RECIPE = '8288537e7c57b04d2462ff0c5bf1af38ab9d4451'
G0_INPUT = 'aa9074c6f5'
FULL = HERE / 'full-export'
PAYLOAD = FULL / '.github/c2-slices'


def git(*args):
    return subprocess.check_output(['git', '-C', str(REPO), *args])


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads(path.read_text())


def save(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def rows(manifest):
    return {(g['suite'], g['mode'], r['selector']): r
            for g in manifest['groups'] for r in g['selectors']}


def main():
    assert git('rev-parse', SOURCE + '^').decode().strip() == BASE
    assert git('rev-parse', SOURCE + '^{tree}').decode().strip() == TREE
    assert '— PASS' in (HERE.parent / 'review/REVIEW.md').read_text()
    tree = {}
    for row in git('ls-tree', '-rz', SOURCE).split(b'\0'):
        if row:
            info, path = row.split(b'\t', 1)
            mode, kind, blob = info.decode().split()
            tree[path.decode()] = dict(mode=mode, kind=kind, blob=blob)
    manifest = read(PAYLOAD / 'test-manifest.json')
    previous = json.loads(git('show', RECIPE + ':.github/c2-slices/test-manifest.json'))
    inherited = rows(previous)
    current = rows(manifest)
    assert len(inherited) == 471 and len(current) == 500
    controls = read(PAYLOAD / 'sel1-controls.json')
    required = {f['path'] for r in current.values() for f in r['files']}
    changed = set(git('diff', '--name-only', BASE, SOURCE).decode().splitlines())
    compiler_paths = {p for p in tree if p.startswith('kani-compiler/') and p.endswith('.rs')}
    required |= compiler_paths | changed | {
        'Cargo.toml', 'Cargo.lock', 'rust-toolchain.toml', 'scripts/kani-regression.sh',
        '.github/actions/setup/action.yml',
        'kani-compiler/src/kani_middle/transform/check_uninit/ty_layout.rs'}
    # Setup helper names are source-owned; inventory the actual setup subtree too.
    required |= {p for p in tree if p.startswith(('.github/actions/setup/', 'scripts/setup/'))}
    assert required <= tree.keys()
    objects = sorted({tree[p]['blob'] for p in required if tree[p]['kind'] == 'blob'})
    raw = subprocess.check_output(
        ['git', '-C', str(REPO), 'cat-file', '--batch'],
        input=('\n'.join(objects) + '\n').encode())
    cache = {}
    offset = 0
    for obj in objects:
        end = raw.index(b'\n', offset)
        actual, kind, size = raw[offset:end].decode().split()
        assert actual == obj and kind == 'blob'
        offset = end + 1
        cache[obj] = raw[offset:offset + int(size)]
        offset += int(size) + 1

    def source(path):
        return cache[tree[path]['blob']]

    def identity(path):
        return dict(mode=tree[path]['mode'], blob=tree[path]['blob'], sha256=sha(source(path)))

    for group in manifest['groups']:
        for row in group['selectors']:
            key = (group['suite'], group['mode'], row['selector'])
            assert row['selector'] == '[' + group['mode'] + '] ' + row['input'].removeprefix('tests/')
            ignored = 'fixme' in row['input'] or 'ignore' in row['input']
            assert row['existing_path_ignore'] == ignored
            if key in inherited:
                old = inherited[key]
                assert row['existing_path_ignore'] == old['existing_path_ignore']
                assert [f['path'] for f in row['files']] == [f['path'] for f in old['files']]
            for f in row['files']:
                path = f['path']
                assert path in tree and tree[path]['kind'] == 'blob'
                directives = [ln for ln in source(path).decode().splitlines()
                              if ln.startswith(('// kani-flags:', '// compile-flags:'))]
                if key in inherited:
                    old_f = next(x for x in inherited[key]['files'] if x['path'] == path)
                    assert identity(path) == old_f['identity'], path
                    assert directives == old_f['original_directives'], path
                f.update(identity=identity(path), original_directives=directives)
    select_files = {p for p in tree if p.startswith('tests/expected/uninit/select-unpredictable-')}
    discovered = {p for p in select_files if p.endswith('.rs') and 'auxiliary' not in Path(p).parts
                  and not Path(p).name.startswith(('.', '#', '~'))}
    assert len(discovered) == 29 and discovered == {r['file'] for r in controls['selectors']}
    assert select_files == {f['path'] for r in current.values()
                            if 'select-unpredictable-' in r['input'] for f in r['files']}
    assert len({Path(p).parent.name for p in select_files}) == 12
    assert Counter(r['expected_result'] for r in controls['selectors']) == {'SUCCESS': 12, 'FAILURE': 17}
    for row in controls['selectors']:
        row['source_identity'] = identity(row['file'])
        row['expected_identity'] = identity(row['expected_file'])
        if row.get('shared_source'):
            row['shared_identity'] = identity(row['shared_source'])
    controls.update(candidate=SOURCE, candidate_tree=TREE, state='BOUND_REVIEWED_CANDIDATE_NOT_RUN')
    save(PAYLOAD / 'sel1-controls.json', controls)
    counts = {}
    for (suite, mode, _), row in current.items():
        c = counts.setdefault(suite, dict(selectors=0, existing_path_ignored=0, expected_passed_if_all_succeed=0))
        c['selectors'] += 1
        c['existing_path_ignored'] += int(row['existing_path_ignore'])
        c['expected_passed_if_all_succeed'] += int(not row['existing_path_ignore'])
    manifest.update(source_sha=SOURCE, source_tree=TREE, source_parent=BASE,
                    deduplicated_selector_count=500, deduplicated_suite_counts=counts,
                    qualification_kind='SEL1_C2_QUICK_WITH_S5_AND_F7',
                    discovery='Static reconstruction of native compiletest naming/selection from exact candidate Git objects: inherited471 + all29 new wrappers. Native discovery/execution NOT_RUN.')
    save(PAYLOAD / 'test-manifest.json', manifest)
    config = read(PAYLOAD / 'inputs.json')
    # Confirm the inherited native compiler-unit inventory against actual candidate sources.
    spec = importlib.util.spec_from_file_location('seams', HERE.parent / 'review/check_seams.py')
    seams = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(seams)
    native = []
    unit_files = []
    for path in sorted(compiler_paths):
        text = source(path).decode()
        masked = seams.mask(text)
        matches = list(re.finditer(r'#\[test\](?:\s*#\[[^\n]*\])*\s*fn\s+(\w+)\s*\(', masked))
        if matches:
            declarations, _, _ = seams.inventory(text)
            for m in matches:
                line = text.count('\n', 0, m.start(1)) + 1
                decl = next(r for r in declarations if r['kind'] == 'fn' and r['name'] == m[1] and r['line'] == line)
                prefix = path.removeprefix('kani-compiler/src/').removesuffix('.rs').split('/')
                if prefix[-1] == 'mod':
                    prefix.pop()
                modules = [r.removeprefix('mod ').strip() for r in decl['container'] if r.startswith('mod ')]
                native.append('::'.join(prefix + modules + [m[1]]))
            unit_files.append(path)
    expected_units = config['additional_units']['compiler-all-units']['native_names']
    assert len(native) == len(set(native)) == 76 and set(native) == set(expected_units)
    sensitivity = read(PAYLOAD / 'sensitivity-manifest.json')
    sensitivity.update(source_candidate=SOURCE, source_tree=TREE, base=BASE)
    for variant in sensitivity['variants']:
        assert sha(source(variant['mutated_path'])) == variant['input_sha256']
        assert sha((PAYLOAD / variant['patch']).read_bytes()) == variant['patch_sha256']
    save(PAYLOAD / 'sensitivity-manifest.json', sensitivity)
    p = PAYLOAD / 'sensitivity.py'
    p.write_text(re.sub(r'^SOURCE_SHA = "[^"]+"', 'SOURCE_SHA = "' + SOURCE + '"', p.read_text(), flags=re.M))
    workflow = FULL / '.github/workflows/uninit-quick.yml'
    content = workflow.read_text().replace('SEL1-C2 Quick (UNBOUND TEMPLATE)', 'SEL1-C2 Quick (reviewed candidate)')
    content = content.replace('false && ', '').replace('ref: PENDING_SEL1_FREEZE_SHA', 'ref: ' + SOURCE)
    workflow.write_text(content)
    g0 = subprocess.check_output(
        ['git', '-C', str(HERE), 'rev-parse', G0_INPUT]).decode().strip()
    config.update(source_sha=SOURCE, source_tree=TREE, source_parent=BASE, g0_input=g0,
                  integration_status='P_STATIC_REVIEW_PASS_Q_NOT_RUN',
                  recipe_commit=RECIPE,
                  recipe_commit_role='Accepted recipe ancestor; actual Q overlay SHA is recorded externally and in source snapshots.',
                  recipe_sha256=sha(workflow.read_bytes()),
                  test_manifest_sha256=sha((PAYLOAD / 'test-manifest.json').read_bytes()),
                  sel1_controls_sha256=sha((PAYLOAD / 'sel1-controls.json').read_bytes()))
    config['sensitivity']['manifest_sha256'] = sha((PAYLOAD / 'sensitivity-manifest.json').read_bytes())
    assert config['structural']['manifest_sha256'] == sha((PAYLOAD / 'structural-manifest.json').read_bytes())
    save(PAYLOAD / 'inputs.json', config)
    binding = dict(source_sha=SOURCE, source_tree=TREE, source_parent=BASE, runtime='NOT_RUN',
                   assurance='Git object binding and static native naming reconstruction, no compiler/verifier',
                   files={p: identity(p) for p in sorted(required) if tree[p]['kind'] == 'blob'},
                   selectors=500, inherited_selectors=471, new_selectors=29,
                   compiler_unit_names=sorted(native), compiler_unit_sources=unit_files,
                   suite_counts=counts, selective_bindings=True,
                   runtime_snapshot='Runner checks ALL non-CI source entries before/after; candidate tree pins complete source.')
    save(HERE / 'SOURCE-BINDING.json', binding)
    print(json.dumps(dict(status='BOUND_STATIC_ONLY', files=len(binding['files']), selectors=500,
                          units=len(native), source_sha=SOURCE, source_tree=TREE)))


if __name__ == '__main__':
    main()
