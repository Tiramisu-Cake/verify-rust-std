#!/usr/bin/env python3
"""Exact extraction, ownership and fixture prerequisite audit; no Rust tools."""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('extract5', HERE/'extract_slice.py')
e = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e)


def dump(name, data):
    (HERE/name).write_text(json.dumps(data, indent=2, ensure_ascii=False)+'\n')


def main():
    e.check_parent()
    outputs = e.extract()
    for p, data in outputs.items():
        assert (e.REPO/p).read_bytes() == data, p
    changed = set(e.git('diff', '--name-only', e.BASE).decode().splitlines())
    changed.update(e.git('ls-files', '--others', '--exclude-standard').decode().splitlines())
    assert changed == set(outputs), (changed-set(outputs), set(outputs)-changed)
    prod = {p for p in changed if p.startswith(('kani-compiler/', 'library/'))}
    assert prod == {e.LAYOUT}
    assert not e.git('diff', '--name-only', e.BASE, '--', 'docs', '.github', 'scripts', 'Cargo.toml', 'Cargo.lock', 'rust-toolchain.toml')
    assert not e.git('diff', '--name-only', '--diff-filter=CDMRTUXB', e.BASE, '--', 'tests')
    rows = e.fixtures()
    ids = {r['id'] for r in rows}
    d1 = json.loads((HERE.parent/'slice-01/DEFERRED-OBLIGATIONS.json').read_text())
    d4 = json.loads((HERE.parent/'slice-04/SLICE.json').read_text())
    assert ids == {r['id'] for r in d1['obligations'] if r['integration_head'] == 5}
    assert ids == set(d4['stage5_deferred_fixture_ids'])
    features = e.prior.prior.effective_oracle()['source_features']
    for row in rows:
        for feature in row['prerequisites']:
            assert int(features[feature]['slice']) <= 5, (row['id'], feature)
        assert not {'E1', 'F7'}.intersection(row['prerequisites'])
        for p in [row['input'], row['golden']]:
            assert (e.REPO/p).read_bytes() == e.git('show', e.F+':'+p), p
    for group in ['contract-modes/', 'root-composition/']:
        assert sum(r['id'].startswith(group) for r in rows) == 7
    # Every residual test path belongs to E1; F7 changes no exported fixtures here.
    test_residual = set(e.git('diff', '--name-only', e.F, '--', 'tests').decode().splitlines())
    # Before the single source commit, Git diff does not enumerate untracked added pairs.
    test_residual.difference_update(p for p in outputs if p.startswith('tests/'))
    all_rows = e.prior.prior.effective_oracle()['fixtures']
    expected6 = {p for r in all_rows if r['earliest_runnable_head'] == 6 for p in [r['input'], r['golden']]}
    assert test_residual == expected6 | {'tests/expected/uninit/part1-edges/README.md'}, test_residual ^ expected6
    # No imported E1 fixture or F7 API/writer/wrapper. All other production files equal parent.
    assert not (e.REPO/'kani-compiler/src/kani_middle/transform/delayed_cache.rs').exists()
    for p in ['kani-compiler/src/kani_middle/transform/mod.rs',
              'kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/mod.rs',
              'kani-compiler/src/codegen_cprover_gotoc/compiler_interface.rs',
              'kani-compiler/src/codegen_aeneas_llbc/compiler_interface.rs']:
        assert (e.REPO/p).read_bytes() == e.git('show', e.BASE+':'+p), p
    docs = json.loads((HERE.parent/'oracle-map/DOCS-MAP.json').read_text())
    assert not [s for d in docs['documents'] for s in d['added_segments'] if s['owner_slice'] == 5]
    subprocess.run(['git', '-C', str(e.REPO), 'diff', '--check', e.BASE], check=True)
    report = dict(status='PASS_STATIC_ONLY', base_sha=e.BASE, validator_sha256=e.digest(Path(__file__).read_bytes()),
                  changed_paths=len(changed), owner5_parts=e.parts(), complete_exact_F_fixtures=len(rows),
                  all_owner1_head5_and_owner4_pending_present=True, E1_F7_imported=False,
                  native_fmt_build_clippy_units_tests_verifier_CI_push='NOT_RUN', formal_proof_credit='NOT_ESTABLISHED')
    head = e.git('rev-parse', 'HEAD').decode().strip()
    if head != e.BASE:
        assert e.git('show', '-s', '--format=%P', head).decode().strip() == e.BASE
        assert not e.git('status', '--porcelain')
        report.update(source_sha=head, source_tree=e.git('rev-parse', head+'^{tree}').decode().strip())
        for name, start, end in [('source.patch', e.BASE, head), ('residual-to-F.patch', head, e.F)]:
            patch = e.git('diff', '--binary', '--full-index', start, end)
            (HERE/name).write_bytes(patch)
            with tempfile.TemporaryDirectory(prefix='slice05-index-') as tmp:
                env = dict(os.environ, GIT_INDEX_FILE=str(Path(tmp)/'index'))
                def run(*args):
                    return subprocess.check_output(['git', '-C', str(e.REPO), *args], env=env)
                run('read-tree', start)
                subprocess.run(['git', '-C', str(e.REPO), 'apply', '--cached', str(HERE/name)], env=env, check=True)
                tree = run('write-tree').decode().strip()
                assert tree == e.git('rev-parse', end+'^{tree}').decode().strip()
            report[name] = dict(sha256=e.digest(patch), alternate_index_target_tree=tree)
    dump('STATIC-VALIDATION.json', report)
    print(json.dumps({k:v for k,v in report.items() if k != 'owner5_parts'}))


if __name__ == '__main__':
    main()
