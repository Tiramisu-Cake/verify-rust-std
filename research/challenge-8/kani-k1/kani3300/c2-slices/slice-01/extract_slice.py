#!/usr/bin/env python3
"""Extract only approved owner1 edits in memory, then write the assigned worktree.

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


def extract():
    inventory = json.loads((MAP / 'B1--F.json').read_text())
    pre = json.loads((MAP / 'PRE-F7.json').read_text())
    outputs = {}
    for file in inventory['files']:
        if not any('1' in h['owners'] for h in file['hunks']):
            continue
        path = file['path']
        old = git('show', B1 + ':' + path).splitlines(keepends=True)
        final = git('show', F + ':' + path).splitlines(keepends=True)
        result, cursor = [], 0
        for h in file['hunks']:
            pos = h['old'][0] - 1 if h['old'][1] else h['old'][0]
            result.extend(old[cursor:pos])
            # Preserve every baseline deletion assigned to a later owner.
            for line in range(h['old'][0], h['old'][0] + h['old'][1]):
                part = next(p for p in h['parts'] if p['side'] == '-' and p['start'] <= line < p['start'] + p['count'])
                if part['owner'] != '1':
                    result.append(old[line - 1])
            for line in range(h['new'][0], h['new'][0] + h['new'][1]):
                part = next(p for p in h['parts'] if p['side'] == '+' and p['start'] <= line < p['start'] + p['count'])
                if part['owner'] == '1':
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
        outputs[path] = data
    oracle = json.loads((HERE.parent / 'oracle-map/ORACLE-MAP.json').read_text())
    for row in oracle['paths']:
        if row['owner_slice'] == 1 and row['earliest_runnable_head'] == 1 and row['delta_B1_F']:
            outputs[row['path']] = git('show', F + ':' + row['path'])
    return outputs


if __name__ == '__main__':
    assert git('rev-parse', 'HEAD').decode().strip() == B1
    assert git('status', '--porcelain') == b''
    outputs = extract()
    for path, data in outputs.items():
        (REPO / path).write_bytes(data)
    print(json.dumps({p: digest(b) for p, b in outputs.items()}, indent=2))
