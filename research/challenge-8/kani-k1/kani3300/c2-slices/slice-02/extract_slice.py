#!/usr/bin/env python3
"""Extract approved cumulative owners1/2 edits in memory, then write the assigned worktree.

No compiler, formatter, verifier, network or build invocation. Not a proof result.
"""
import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAP = HERE.parent / 'source-map'
REPO = Path('/root/kani-fix-3300-c2-slices-w14')
B1 = '6fe484b30043b3696b5f1ccc4bea0e42891ad012'
F = 'ad499e41dd2db9ccd432f89721638a1f3a0bbd44'


def git(*args):
    return subprocess.check_output(['git', '-C', str(REPO), *args])


def digest(data):
    return hashlib.sha256(data).hexdigest()


BASE = 'd82752c8bc878398e672bffaa631ca6a28430acc'


def extract(owners=('1', '2')):
    inventory = json.loads((MAP / 'B1--F.json').read_text())
    pre = json.loads((MAP / 'PRE-F7.json').read_text())
    outputs = {}
    for file in inventory['files']:
        if not any(set(owners).intersection(h['owners']) for h in file['hunks']):
            continue
        path = file['path']
        old = git('show', B1 + ':' + path).splitlines(keepends=True) if file['identities']['B1']['blob'] else []
        final = git('show', F + ':' + path).splitlines(keepends=True)
        result, cursor = [], 0
        for h in file['hunks']:
            pos = h['old'][0] - 1 if h['old'][1] else h['old'][0]
            result.extend(old[cursor:pos])
            # Preserve every baseline deletion assigned to a later owner.
            for line in range(h['old'][0], h['old'][0] + h['old'][1]):
                part = next(p for p in h['parts'] if p['side'] == '-' and p['start'] <= line < p['start'] + p['count'])
                if part['owner'] not in owners:
                    result.append(old[line - 1])
            for line in range(h['new'][0], h['new'][0] + h['new'][1]):
                part = next(p for p in h['parts'] if p['side'] == '+' and p['start'] <= line < p['start'] + p['count'])
                if part['owner'] in owners:
                    result.append(final[line - 1])
                elif path == pre['path'] and line == 212:
                    # The failed-root loop is1, while the final writer API is7.
                    assert part['owner'] == '7'
                    result.append(pre['snippets'][2]['text'].encode())
            cursor = pos + h['old'][1]
        result.extend(old[cursor:])
        data = b''.join(result)
        if path == pre['path']:
            # One baseline import line combines owner7's retained import and
            # owner1's expanded body imports. Split it at the existing seam.
            data = data.replace(
                b'        BodyTransformation, GlobalPass, TransformationResult, body::CheckType,\n',
                pre['snippets'][0]['text'].encode(),
            )
        if path.endswith('/ptr_uninit/uninit_visitor.rs'):
            # The zero-context diff moves the resolver into a hunk that removes
            # two baseline helper functions. Keep those functions at this head;
            # replace only the resolver at its original location, with its
            # existing closing brace. No later helper deletion is imported.
            body = b''.join(final[1178:1185])
            data = data.replace(body[:-2], b'')
            anchor = b'/// Try retrieving instance for the given function operand.\n'
            data = data.replace(anchor + b'\n', anchor + body + b'\n', 1)
        if path.endswith('/check_uninit/ty_layout.rs') and '2' in owners:
            # Owner4's adjacent methods leave a leading blank inside the impl.
            data = data.replace(b'impl PointeeInfo {\n\n', b'impl PointeeInfo {\n', 1)
        outputs[path] = data
    oracle = json.loads((HERE.parent / 'oracle-map/ORACLE-MAP.json').read_text())
    for row in oracle['paths']:
        if str(row['owner_slice']) in owners and row['earliest_runnable_head'] <= max(map(int, owners)) and row['delta_B1_F']:
            outputs[row['path']] = git('show', F + ':' + row['path'])
    if '2' in owners:
        docs = json.loads((HERE.parent / 'oracle-map/DOCS-MAP.json').read_text())
        for document in docs['documents']:
            segments = [r for r in document['added_segments'] if r['owner_slice'] == 2]
            if not segments:
                continue
            path = document['path']
            old = git('show', BASE + ':' + path)
            final = git('show', F + ':' + path).decode().splitlines()
            for row in segments:
                assert final[row['F_line'] - 1][row['start_column_0']:row['end_column_0']] == row['text']
            paragraph = ('\n'.join(row['text'] for row in segments) + '\n').encode()
            if path == 'docs/src/rust-feature-support.md':
                anchor = b'See [this issue](https://github.com/model-checking/kani/issues/3300) for more details.\n'
                assert old.count(anchor) == 1
                outputs[path] = old.replace(anchor, b'\n' + paragraph + b'\n' + anchor)
            elif path == 'docs/src/reference/experimental/contracts.md':
                # The final leading link/header is owned by6/4. Supply a complete
                # interim sentence with the same destination, reverted by6.
                paragraph = paragraph.replace(b'Whole\nimmutable', b'Whole immutable')
                paragraph = paragraph.replace(b'qualification described there;',
                    b'qualification described in the\n[uninitialized memory support](../../rust-feature-support.md#uninitialized-memory);')
                anchor = b'There is far more to learn about contracts.\n'
                assert old.count(anchor) == 1
                outputs[path] = old.replace(anchor, paragraph + b'\n' + anchor)
            else:
                raise AssertionError(path)
    return outputs


if __name__ == '__main__':
    assert git('rev-parse', 'HEAD').decode().strip() == BASE
    assert git('status', '--porcelain') == b''
    # Reproduce the accepted parent exactly before any write.
    for path, data in extract(('1',)).items():
        assert git('show', BASE + ':' + path) == data, path
    outputs = extract()
    for path, data in outputs.items():
        target = REPO / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    print(json.dumps({p: digest(b) for p, b in outputs.items()}, indent=2))
