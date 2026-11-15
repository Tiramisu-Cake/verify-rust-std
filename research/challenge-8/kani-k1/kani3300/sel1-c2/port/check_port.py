#!/usr/bin/env python3
"""Exact Git/source-only port checks. No Rust tools, build, or verifier."""
import hashlib
import importlib.util
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = Path('/root/kani-fix-3300-sel1-c2-w14')
BASE = '8e299aa6243bc5f06a29c51e98aafa9564478220'
OLD_BASE = '69b13711e60a87458200833445d47488ab466344'
OLD = '39a6521bf1b042358801cf613fd340623f35f851'
HEAD = '14bc57fdb99960240c4944845a3d985c8af4dcf7'
PRODUCTION = [
    'kani-compiler/src/codegen_cprover_gotoc/codegen/statement.rs',
    'kani-compiler/src/kani_middle/mod.rs',
    'kani-compiler/src/kani_middle/points_to/points_to_analysis.rs',
    'kani-compiler/src/kani_middle/reachability.rs',
    'kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs',
]
DOC = 'docs/src/rust-feature-support.md'


def git(*args):
    return subprocess.check_output(['git', '-C', str(REPO), *args])


def source(ref, path):
    return git('show', f'{ref}:{path}')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def save(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2) + '\n')


def main():
    spec = importlib.util.spec_from_file_location(
        'seams', HERE.parents[1] / 'c2-slices/seam-audit/check_seams.py')
    seams = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(seams)
    assert git('rev-parse', 'HEAD').decode().strip() == HEAD
    assert git('status', '--porcelain') == b''
    assert git('rev-parse', HEAD + '^').decode().strip() == BASE
    assert git('rev-list', '--count', BASE + '..' + HEAD).strip() == b'1'
    assert git('rev-parse', BASE + '^{tree}').strip() == b'9829702c1aa0ecb73c860fc0ad5451757917d6cb'
    git('diff', '--check', BASE, HEAD)
    old_paths = git('diff', '--name-only', OLD_BASE, OLD).decode().splitlines()
    new_paths = git('diff', '--name-only', BASE, HEAD).decode().splitlines()
    fixture_paths = [p for p in old_paths if p.startswith('tests/')]
    assert len(fixture_paths) == 65
    assert set(old_paths) == set(PRODUCTION + fixture_paths)
    assert set(new_paths) == set(old_paths + [DOC])
    groups = sorted({Path(p).parts[3] for p in fixture_paths})
    assert len(groups) == 12
    assert all(g.startswith('select-unpredictable-') for g in groups)
    files = []
    for p in new_paths:
        data = source(HEAD, p)
        old_data = source(OLD, p) if p != DOC else None
        if p in fixture_paths:
            assert data == old_data, p
        files.append(dict(path=p, source_sha256=sha(data),
                          old_sel1_sha256=sha(old_data) if old_data is not None else None,
                          same_as_old_sel1=data == old_data))
    save('FILES.json', files)

    # Every file changed by F7 remains byte-identical to final C2.
    f7_paths = git('diff', '--name-only', '3f5242bb15', BASE).decode().splitlines()
    assert len(f7_paths) == 5
    f7 = []
    for p in f7_paths:
        assert source(BASE, p) == source(HEAD, p), p
        f7.append(dict(path=p, sha256=sha(source(HEAD, p))))

    def functions(ref, path):
        text = source(ref, path).decode()
        rows, ts, pairs = seams.inventory(text)
        out = {}
        for row in rows:
            if row['kind'] != 'fn':
                continue
            start, end = row['token_start'], row['token_end']
            if ts[end][0] == '{':
                end = pairs[end] + 1
            key = (tuple(row['container']), row['name'])
            out[key] = [v for v, _ in ts[start:end]]
        return out

    visitor = PRODUCTION[-1]
    before, after = functions(BASE, visitor), functions(HEAD, visitor)
    allowed_changes = {'find_all', 'visit_terminator', 'has_transfer_protocol'}
    preserved = []
    for key, tokens in before.items():
        assert key in after, key
        if key[1] not in allowed_changes:
            assert tokens == after[key], key
            preserved.append(key[1])
    assert {'needs_nested_call_reset', 'reset_nested_call', 'can_skip_intrinsic',
            'try_resolve_instance', 'visit_statement', 'visit_place'} <= set(preserved)

    manifest = json.loads((HERE.parents[1] / 'sel1/CONTROL-MANIFEST.json').read_text())
    selectors = manifest['selectors']
    assert len(selectors) == len({r['selector'] for r in selectors}) == 29
    assert sum(r['expected_result'] == 'SUCCESS' for r in selectors) == 12
    assert sum(r['expected_result'] == 'FAILURE' for r in selectors) == 17
    for row in selectors:
        assert row['file'] in fixture_paths
        assert row['expected_file'] in fixture_paths
        wrapper = source(HEAD, row['file']).decode()
        if row.get('shared_source'):
            assert row['shared_source'] in fixture_paths
            assert '--harness ' + row['selector'] + ' --exact' in wrapper
            executable = source(HEAD, row['shared_source']).decode()
        else:
            executable = wrapper
        assert re.search(r'\bfn\s+' + row['selector'] + r'\s*\(', executable)
        golden = source(HEAD, row['expected_file']).decode()
        assert 'Checking harness ' + row['selector'] + '...' in golden
        assert not re.search(r'(?m)^\s*//\s*(?:ignore|fixme)', wrapper)

    # The seam tool covers .rs; inventory the unchanged include files explicitly too.
    includes = []
    for path in fixture_paths:
        if path.endswith('.inc'):
            data = source(HEAD, path).decode()
            rows, _, _ = seams.inventory(data)
            includes.append(dict(path=path, declarations_impls_uses=rows))
    save('INCLUDE-INVENTORY.json', includes)
    save('VALIDATION.json', dict(
        status='PASS_BOUNDED_STATIC_PORT_CHECKS', source=HEAD,
        tree=git('rev-parse', HEAD + '^{tree}').decode().strip(), parent=BASE,
        changed_files=len(new_paths), production_files=len(PRODUCTION), docs_files=1,
        fixtures_exact_old_sel1=len(fixture_paths), groups=groups,
        intended_success=12, intended_failure=17, selectors=29,
        unchanged_F7_files=f7, preserved_visitor_functions=preserved,
        original_C2_tests='UNCHANGED', outside_scope_diff='EMPTY',
        source_clean=True, diff_check='PASS', native_build='NOT_RUN',
        new_runtime_outcomes='NOT_RUN', independent_worker15_review='PENDING',
        proof_credit='NONE'))
    (HERE / 'source.patch').write_bytes(git('diff', '--binary', BASE, HEAD))
    (HERE / 'DIFFSTAT.txt').write_bytes(git('diff', '--stat', BASE, HEAD))
    print('PASS_BOUNDED_STATIC_PORT_CHECKS: 5 production, 65 exact fixtures, 1 doc; 29 selectors; F7 unchanged')


if __name__ == '__main__':
    main()
