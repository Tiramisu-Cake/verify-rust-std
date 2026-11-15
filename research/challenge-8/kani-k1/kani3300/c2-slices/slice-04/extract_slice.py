#!/usr/bin/env python3
"""Compose only approved source owners1..4; Git/Python only, no native execution."""
import importlib.util
import json
import sys
from pathlib import Path
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('slice3', HERE.parent / 'slice-03/extract_slice.py')
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
git, digest, REPO, MAP, B1, F = prior.git, prior.digest, prior.REPO, prior.MAP, prior.B1, prior.F
BASE = '5ca51679e3f433718807a2e44add0d5abac128e7'


def fixture_sets():
    oracle = prior.effective_oracle()
    correction = HERE / 'ORACLE-MAP-CORRECTION.json'
    if correction.exists():
        for change in json.loads(correction.read_text())['changes']:
            row = next(r for r in oracle['fixtures'] if r['id'] == change['id'])
            assert row['earliest_runnable_head'] == change['old_head']
            row['earliest_runnable_head'] = row['planned_introduction_head'] = change['new_head']
            row['dependency_correction'] = 'slice-04/ORACLE-MAP-CORRECTION.json'
    selected = [r for r in oracle['fixtures'] if r['earliest_runnable_head'] == 4]
    deferred = [r for r in oracle['fixtures'] if r['earliest_runnable_head'] == 5]
    return selected, deferred


def compose_production():
    owners = {'1', '2', '3', '4'}
    inventory = prior.effective_inventory()
    pre = json.loads((MAP / 'PRE-F7.json').read_text())
    outputs = {}
    for file in inventory['files']:
        if not any(owners.intersection(h['owners']) for h in file['hunks']):
            continue
        path = file['path']
        old = git('show', B1 + ':' + path).splitlines(keepends=True) if file['identities']['B1']['blob'] else []
        final = git('show', F + ':' + path).splitlines(keepends=True)
        result, cursor = [], 0
        for h in file['hunks']:
            pos = h['old'][0] - 1 if h['old'][1] else h['old'][0]
            result.extend(old[cursor:pos])
            for line in range(h['old'][0], h['old'][0] + h['old'][1]):
                part = next(p for p in h['parts'] if p['side'] == '-' and p['start'] <= line < p['start'] + p['count'])
                if part['owner'] not in owners:
                    result.append(old[line - 1])
            for line in range(h['new'][0], h['new'][0] + h['new'][1]):
                part = next(p for p in h['parts'] if p['side'] == '+' and p['start'] <= line < p['start'] + p['count'])
                if part['owner'] in owners:
                    result.append(final[line - 1])
                elif path == pre['path'] and line == 212:
                    assert part['owner'] == '7'
                    result.append(pre['snippets'][2]['text'].encode())
            cursor = pos + h['old'][1]
        result.extend(old[cursor:])
        data = b''.join(result)
        if path == pre['path']:
            data = data.replace(b'        BodyTransformation, GlobalPass, TransformationResult, body::CheckType,\n', pre['snippets'][0]['text'].encode())
        # All owner4 helper deletions now land with the owner1 resolver: no early-head relocation.
        outputs[path] = data
    return outputs


def compose_docs():
    docs = json.loads((HERE.parent / 'oracle-map/DOCS-MAP.json').read_text())
    outputs = {}
    for document in docs['documents']:
        rows = [r for r in document['added_segments'] if r['owner_slice'] == 4]
        if not rows:
            continue
        path = document['path']
        final = git('show', F + ':' + path).decode().splitlines()
        for row in rows:
            assert final[row['F_line']-1][row['start_column_0']:row['end_column_0']] == row['text']
        old = git('show', BASE + ':' + path).decode()
        if path == 'docs/src/rust-feature-support.md':
            # Shared physical line184 belongs4/2. Retain immutable paragraph once.
            intro = '\n'.join(r['text'] for r in rows if 180 <= r['F_line'] <= 184).rstrip() + '\n'
            anchor = 'Qualified whole immutable promoted constants and named\n'
            assert old.count(anchor) == 1
            old = old.replace(anchor, intro + anchor)
            # Complete interim sentences omit only the not-yet-owned6 clause and link.
            limitations = '\n'.join(r['text'] for r in rows if 198 <= r['F_line'] <= 203)
            limitations = limitations.replace('Shadow transfer under\nnested', 'By-value aggregates containing\nnested')
            anchor = 'See [this issue](https://github.com/model-checking/kani/issues/3300) for more details.\n'
            assert old.count(anchor) == 1
            outputs[path] = old.replace(anchor, limitations + '\n\n' + anchor).encode()
        elif path == 'docs/src/reference/experimental/contracts.md':
            # Owner6 owns the final link prefix; retain the existing link target in an interim sentence.
            prefix = ('## Limitations\n\nThe limitations of\n'
                      '[uninitialized memory support](../../rust-feature-support.md#uninitialized-memory)\n')
            intro = '\n'.join(r['text'] for r in rows if 76 <= r['F_line'] <= 78)
            intro = intro.rstrip() + '\n'
            anchor = 'Whole immutable masks require the qualification described in the\n[uninitialized memory support](../../rust-feature-support.md#uninitialized-memory);'
            assert old.count(anchor) == 1
            old = old.replace(anchor, prefix + intro + 'Whole immutable masks require the qualification described there;')
            nested = '\n'.join(r['text'] for r in rows if 95 <= r['F_line'] <= 106) + '\n\n'
            anchor = 'There is far more to learn about contracts.\n'
            assert old.count(anchor) == 1
            outputs[path] = old.replace(anchor, nested + anchor).encode()
        else:
            raise AssertionError(path)
    return outputs


def extract():
    outputs = compose_production()
    for row in fixture_sets()[0]:
        for path in [row['input'], row['golden']]:
            outputs[path] = git('show', F + ':' + path)
    outputs.update(compose_docs())
    return outputs


def check_parent():
    prior.check_parent()
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
