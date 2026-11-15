#!/usr/bin/env python3
"""Extract the two approved closure parts and all whole head5 fixtures; Git/Python only."""
import importlib.util
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('slice4', HERE.parent/'slice-04/extract_slice.py')
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
git, digest, REPO, MAP, B1, F = prior.git, prior.digest, prior.REPO, prior.MAP, prior.B1, prior.F
BASE = '345cedfd67df679e326474385308349d609fc43d'
LAYOUT = 'kani-compiler/src/kani_middle/transform/check_uninit/ty_layout.rs'


def fixtures():
    rows = prior.fixture_sets()[1]
    assert len(rows) == 47
    return rows


def parts():
    rows = prior.prior.parts_for('5')
    assert len(rows) == 2 and {p['path'] for p in rows} == {LAYOUT}
    return rows


def extract():
    parent = git('show', BASE+':'+LAYOUT)
    final = git('show', F+':'+LAYOUT)
    plus, minus = [next(p for p in parts() if p['side'] == side) for side in ['+', '-']]
    added = b''.join(final.splitlines(keepends=True)[plus['start']-1:plus['start']-1+plus['count']])
    deleted = b''.join(git('show', B1+':'+LAYOUT).splitlines(keepends=True)[minus['start']-1:minus['start']-1+minus['count']])
    assert digest(added) == plus['sha256'] and digest(deleted) == minus['sha256']
    anchor = b'                RigidTy::FnDef(_, _)\n'
    assert parent.count(anchor) == parent.count(deleted) == 1
    layout = parent.replace(anchor, added+anchor, 1).replace(deleted, b'', 1)
    # Whole-file identity is a validation result, not a whole-file extraction shortcut.
    assert layout == final
    outputs = {LAYOUT: layout}
    for row in fixtures():
        for path in [row['input'], row['golden']]:
            assert not git('ls-tree', BASE, '--', path), path
            outputs[path] = git('show', F+':'+path)
    return outputs


def check_parent():
    prior.check_parent()
    for path, data in prior.extract().items():
        assert git('show', BASE+':'+path) == data, path
    assert git('merge-base', B1, BASE).decode().strip() == B1


if __name__ == '__main__':
    assert git('rev-parse', 'HEAD').decode().strip() == BASE
    assert not git('status', '--porcelain')
    check_parent()
    outputs = extract()
    for path, data in outputs.items():
        target = REPO/path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    print(json.dumps({'base': BASE, 'changed_paths': len(outputs), 'whole_fixtures': len(fixtures())}))
