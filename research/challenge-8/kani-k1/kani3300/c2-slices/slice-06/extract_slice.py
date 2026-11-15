#!/usr/bin/env python3
"""Extract only the approved head6 edge pairs and remaining docs; Git/Python only."""
import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPO = Path('/root/kani-fix-3300-c2-slices-w14')
BASE = '96f5d5dc8dedd369c6986a4f1dd5e698b6167f0f'
F = 'ad499e41dd2db9ccd432f89721638a1f3a0bbd44'
B1 = '6fe484b30043b3696b5f1ccc4bea0e42891ad012'
DOCS = ['docs/src/rust-feature-support.md',
        'docs/src/reference/experimental/contracts.md',
        'tests/expected/uninit/part1-edges/README.md']


def git(*args):
    return subprocess.check_output(['git', '-C', str(REPO), *args])


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text())


def fixtures():
    rows = [r for r in load(ROOT/'oracle-map/ORACLE-MAP.json')['fixtures']
            if r['earliest_runnable_head'] == 6]
    assert len(rows) == 11 and all(r['owner_slice'] == 6 for r in rows)
    assert {r['id'].split('/')[1].rsplit('-', 1)[0] for r in rows} == {
        'union-constant', 'union-variable', 'raw-field', 'raw-field-neighbor',
        'raw-field-padding', 'dst-by-reference', 'dst-by-value'}
    return rows


def paths():
    return sorted(DOCS + [r[k] for r in fixtures() for k in ['input', 'golden']])


def extract():
    assert git('rev-parse', 'HEAD').decode().strip() == BASE
    assert not git('status', '--porcelain')
    assert git('merge-base', B1, BASE).decode().strip() == B1
    assert not load(ROOT/'source-map/DEPENDENCIES.json')['slices']['6']['source_parts']
    f7 = {r['path'] for r in load(ROOT/'f7/F7-RESIDUAL.json')['files']}
    remaining = set(git('diff', '--name-only', BASE, F).decode().splitlines())
    assert remaining == set(paths()) | f7
    # Shared docs: apply only the outstanding parent->F hunks. Earlier owners stay present.
    tracked_docs = DOCS[:2]
    patch = git('diff', '--binary', '--full-index', BASE, F, '--', *tracked_docs)
    (HERE/'docs-remainder.patch').write_bytes(patch)
    subprocess.run(['git', '-C', str(REPO), 'apply', '--check', str(HERE/'docs-remainder.patch')], check=True)
    subprocess.run(['git', '-C', str(REPO), 'apply', str(HERE/'docs-remainder.patch')], check=True)
    for path in paths():
        if path not in tracked_docs:
            assert not git('ls-tree', BASE, '--', path), path
            dest = REPO/path
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(git('show', F+':'+path))
        assert (REPO/path).read_bytes() == git('show', F+':'+path), path
    print(json.dumps(dict(base=BASE, files=len(paths()), fixture_pairs=11, production_delta=0)))


if __name__ == '__main__':
    extract()
