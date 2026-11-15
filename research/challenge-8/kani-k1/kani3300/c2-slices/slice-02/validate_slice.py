#!/usr/bin/env python3
"""Static slice integrity; never Rust parsing, building or verification."""
import importlib.util
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent

def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

extract = module('extract2', HERE / 'extract_slice.py')
previous = module('validate1', HERE.parent / 'slice-01/validate_slice.py')
git, digest = extract.git, extract.digest


def main():
    expected = extract.extract()
    # Parent was accepted independently; reproduce it without borrowing later source.
    for path, data in extract.extract(('1',)).items():
        assert git('show', extract.BASE + ':' + path) == data, path
    for path, data in expected.items():
        assert (extract.REPO / path).read_bytes() == data, path
        if path.endswith('.rs'):
            previous.delimiters(data)
    changed = set(git('diff', '--name-only', extract.BASE).decode().splitlines())
    changed.update(git('ls-files', '--others', '--exclude-standard').decode().splitlines())
    intended = {p for p, data in expected.items() if not git('ls-tree', extract.BASE, '--', p) or git('show', extract.BASE + ':' + p) != data}
    assert changed == intended, (changed - intended, intended - changed)
    inventory = json.loads((extract.MAP / 'B1--F.json').read_text())
    count = 0
    for file in inventory['files']:
        for h in file['hunks']:
            for part in h['parts']:
                if part['owner'] != '2':
                    continue
                ref = extract.F if part['side'] == '+' else extract.B1
                lines = git('show', ref + ':' + file['path']).splitlines(keepends=True)
                data = b''.join(lines[part['start'] - 1:part['start'] - 1 + part['count']])
                assert digest(data) == part['sha256'], (file['path'], h['id'], part)
                count += 1
    exact_f = [
        'kani-compiler/src/codegen_cprover_gotoc/context/immutable_allocations.rs',
        'kani-compiler/src/kani_middle/anonymous_allocations.rs',
        'kani-compiler/src/kani_middle/points_to/points_to_graph.rs',
        'kani-compiler/src/kani_middle/points_to/points_to_analysis.rs',
    ]
    for p in exact_f:
        assert expected[p] == git('show', extract.F + ':' + p), p
    prefix = 'kani-compiler/src/'
    registry = expected[prefix + 'codegen_cprover_gotoc/context/immutable_allocations.rs']
    unit_names = re.findall(rb'#\[test\]\s+fn (\w+)', registry)
    assert len(unit_names) == 9
    lifecycle = expected[prefix + 'codegen_cprover_gotoc/compiler_interface.rs']
    tokens = [b'gcx.prepare_immutable_allocations(&items)', b'gcx.handle_quantifiers()', b'gcx.finalize_immutable_allocations()', b'let pretty_name_map:', b'gcx.split()']
    positions = [lifecycle.index(t) for t in tokens]
    assert positions == sorted(positions)
    assert b'with_delayed_scope' not in lifecycle and b'delayed_scope' not in lifecycle
    delayed = expected[prefix + 'kani_middle/transform/check_uninit/delayed_ub/mod.rs']
    for item in json.loads((extract.MAP / 'PRE-F7.json').read_text())['snippets']:
        assert delayed.count(item['text'].encode()) == 1
    assert b'replace_delayed_body' not in delayed
    layout = expected[prefix + 'kani_middle/transform/check_uninit/ty_layout.rs']
    assert b'for_typed_storage' not in layout and b'for_deinit' not in layout and b'argument_size' not in layout
    assert b'impl PointeeInfo {\n\n' not in layout
    # Baseline storage/protocol/runtime, raw_eq, closure, F7, workflows and pins stay parent.
    protected = ['library', '.github', 'scripts', 'Cargo.toml', 'Cargo.lock', 'rust-toolchain.toml',
                 prefix + 'kani_middle/transform/check_uninit/ptr_uninit',
                 prefix + 'kani_middle/transform/check_uninit/relevant_instruction.rs',
                 prefix + 'kani_middle/kani_functions.rs',
                 prefix + 'kani_middle/transform/delayed_cache.rs',
                 prefix + 'codegen_aeneas_llbc', 'docs/src/rust-feature-support/intrinsics.md']
    assert not git('diff', '--name-only', extract.BASE, '--', *protected)
    oracle = json.loads((HERE.parent / 'oracle-map/ORACLE-MAP.json').read_text())
    selected = [r for r in oracle['fixtures'] if r['owner_slice'] == 2 and r['earliest_runnable_head'] == 2]
    deferred = [r for r in oracle['fixtures'] if r['owner_slice'] == 2 and r['earliest_runnable_head'] > 2]
    assert len(selected) == 6 and len(deferred) == 16
    for row in selected:
        for p in (row['input'], row['golden']):
            assert expected[p] == git('show', extract.F + ':' + p)
    for row in deferred:
        for p in (row['input'], row['golden']):
            assert not (extract.REPO / p).exists(), p
    # Every existing parent test, B1 control, directive and golden is byte-identical.
    assert not git('diff', '--name-only', '--diff-filter=CDMRTUXB', extract.BASE, '--', 'tests')
    subprocess.run(['git', '-C', str(extract.REPO), 'diff', '--check', extract.BASE], check=True)
    report = {
        'status': 'PASS_STATIC_ONLY', 'base_sha': extract.BASE,
        'owner2_part_hashes_checked': count, 'changed_paths': sorted(intended),
        'exact_F_production_blobs': exact_f,
        'immutable_unit_count': 9, 'immutable_unit_names': [n.decode() for n in unit_names],
        'selected_whole_fixtures': len(selected), 'deferred_owner2_whole_fixtures': len(deferred),
        'checks': ['accepted parent independently reconstructed', 'deterministic owner1+2 extraction with explicit seams',
                   'all owner2 original hunk-part hashes', 'lexical delimiter balance (not Rust parser)',
                   'exact F registry/anonymous/graph/analysis blobs and all new fixtures',
                   'prepare -> quantifier postpass -> finalize -> metadata -> split ordering',
                   'both pre-F7 writers preserved, no F7 scope API', 'no typed/protocol/runtime/layout-offset/raw_eq/closure feature delta',
                   'all existing tests/flags/goldens unchanged', 'deferred fixtures absent', 'git diff --check'],
        'native_fmt_build_clippy_units_tests_verifier_CI_push': 'NOT_RUN',
        'worker15_review': 'PENDING', 'formal_proof_credit': 'NOT_ESTABLISHED',
    }
    head = git('rev-parse', 'HEAD').decode().strip()
    if head != extract.BASE:
        assert git('show', '-s', '--format=%P', head).decode().strip() == extract.BASE
        assert not git('status', '--porcelain')
        report.update(source_sha=head, source_tree=git('rev-parse', 'HEAD^{tree}').decode().strip())
        for name, base, target in [('source.patch', extract.BASE, head), ('residual-to-F.patch', head, extract.F)]:
            patch = git('diff', '--no-ext-diff', '--no-renames', '--full-index', '--binary', '--unified=0', base, target)
            (HERE / name).write_bytes(patch)
            with tempfile.TemporaryDirectory(prefix='c2-slice02-index-') as tmp:
                env = dict(os.environ, GIT_INDEX_FILE=str(Path(tmp) / 'index'))
                def index_git(*args):
                    return subprocess.check_output(['git', '-C', str(extract.REPO), *args], env=env)
                index_git('read-tree', base)
                index_git('apply', '--cached', '--unidiff-zero', '--whitespace=nowarn', str(HERE / name))
                tree = index_git('write-tree').decode().strip()
                assert tree == git('rev-parse', target + '^{tree}').decode().strip()
            report[name] = {'sha256': digest(patch), 'alternate_index_target_tree': tree}
    (HERE / 'STATIC-VALIDATION.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
