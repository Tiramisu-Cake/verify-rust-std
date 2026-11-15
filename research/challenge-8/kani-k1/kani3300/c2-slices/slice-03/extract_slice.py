#!/usr/bin/env python3
"""Compose accepted owners1/2 + owner3 from pinned maps; no native execution."""
import importlib.util
import copy
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('accepted_slice2', HERE.parent / 'slice-02/extract_slice.py')
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
git, digest, REPO, MAP, B1, F = prior.git, prior.digest, prior.REPO, prior.MAP, prior.B1, prior.F
BASE = '932fb8395a58f8c86c0d702ba2cae835823b2962'


def effective_inventory():
    data = json.loads((MAP / 'B1--F.json').read_text())
    correction = json.loads((HERE / 'SOURCE-MAP-CORRECTION.json').read_text())
    assert correction['canonical_map_sha256'] == digest((MAP / 'B1--F.json').read_bytes())
    for change in correction['owner_changes']:
        file = next(r for r in data['files'] if r['path'] == change['path'])
        hunk = next(r for r in file['hunks'] if r['id'] == change['hunk_id'])
        part = hunk['parts'][change['part_index']]
        assert part == change['part'] and part['owner'] == change['old_owner']
        part['owner'] = change['new_owner']
        hunk['owners'] = sorted({p['owner'] for p in hunk['parts']})
    return data


def parts_for(owner):
    return [{'hunk_id': h['id'], 'part_index': i, 'path': f['path'], **copy.deepcopy(p)}
            for f in effective_inventory()['files'] for h in f['hunks']
            for i, p in enumerate(h['parts']) if p['owner'] == owner]


def extract():
    # Reuse the reviewed line-part composer and its explicit pre-F7 seams.
    # Parent reconstruction is checked separately before writing anything.
    outputs = prior.extract(('1', '2', '3'))
    # Exact one-line import correction from the compile-seam manual inventory.
    # Canonical stage0 map remains immutable; the stage3 ownership delta is explicit.
    changes = json.loads((HERE / 'SOURCE-MAP-CORRECTION.json').read_text())['owner_changes']
    assert len(changes) == 2 and {c['part']['side'] for c in changes} == {'-', '+'}
    path = changes[0]['path']
    texts = {}
    for change in changes:
        assert change['path'] == path
        part = change['part']
        assert part['count'] == 1
        ref = F if part['side'] == '+' else B1
        line = git('show', ref + ':' + path).splitlines(keepends=True)[part['start'] - 1]
        assert digest(line) == part['sha256']
        texts[part['side']] = line
    assert outputs[path].count(texts['-']) == 1
    outputs[path] = outputs[path].replace(texts['-'], texts['+'], 1)
    docs = json.loads((HERE.parent / 'oracle-map/DOCS-MAP.json').read_text())
    for document in docs['documents']:
        rows = [r for r in document['added_segments'] if r['owner_slice'] == 3]
        if not rows:
            continue
        path = document['path']
        assert path == 'docs/src/rust-feature-support/intrinsics.md' and len(rows) == 1
        row = rows[0]
        final = git('show', F + ':' + path).decode().splitlines()
        assert final[row['F_line'] - 1][row['start_column_0']:row['end_column_0']] == row['text']
        old = git('show', BASE + ':' + path)
        lines = old.decode().splitlines(keepends=True)
        indexes = [i for i, line in enumerate(lines) if line.startswith('raw_eq |')]
        assert len(indexes) == 1
        lines[indexes[0]] = row['text'] + '\n'
        outputs[path] = ''.join(lines).encode()
        # Only this row differs from baseline; whole-file equality is a check,
        # not the extraction method for this shared documentation file.
        assert outputs[path] == git('show', F + ':' + path)
    return outputs


def check_parent():
    for path, data in prior.extract().items():
        assert git('show', BASE + ':' + path) == data, path


if __name__ == '__main__':
    assert git('rev-parse', 'HEAD').decode().strip() == BASE
    assert not git('status', '--porcelain')
    check_parent()
    changed = []
    for path, data in extract().items():
        target = REPO / path
        if target.exists() and target.read_bytes() == data:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        changed.append(path)
    print(json.dumps({'base': BASE, 'changed_paths': changed}, indent=2))
