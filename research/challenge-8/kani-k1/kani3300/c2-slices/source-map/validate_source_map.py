#!/usr/bin/env python3
"""Independent static audit of saved source ranges, identities and owner coverage."""
import hashlib
import json
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = '/root/kani-fix-3300-c2-s6'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def git(*args):
    return subprocess.check_output(['git', '-C', REPO, *args])


def read(name):
    return json.loads((ROOT / name).read_text())


def main():
    inputs = read('INPUTS.json')
    deps = read('DEPENDENCIES.json')
    expected_parts = []
    totals = Counter()
    for label in ['U--B1', 'B1--F']:
        doc = read(label + '.json')
        raw = (ROOT / (label + '.patch')).read_bytes()
        assert digest(raw) == doc['patch_sha256']
        assert raw == git('diff', '--no-ext-diff', '--no-renames', '--full-index', '--binary', '--unified=0', doc['base'], doc['target'], '--', 'kani-compiler', 'library')
        chunks = re.split(rb'(?=^diff --git )', raw, flags=re.M)[1:]
        assert len(chunks) == len(doc['files'])
        for file, chunk in zip(doc['files'], chunks):
            path = file['path']
            assert chunk.splitlines()[0].decode().endswith(' b/' + path)
            blocks = re.split(rb'(?=^@@ )', chunk, flags=re.M)[1:]
            assert len(blocks) == len(file['hunks'])
            seen = set()
            for hunk, block in zip(file['hunks'], blocks):
                assert hunk['header'] == block.splitlines()[0].decode()
                assert digest(block) == hunk['sha256']
                edited = {'+': [], '-': []}
                for line in block.splitlines(keepends=True)[1:]:
                    assert line[0] in (43, 45)
                    edited[chr(line[0])].append(line[1:])
                covered = {'+': set(), '-': set()}
                for index, part in enumerate(hunk['parts']):
                    side = part['side']
                    base = hunk['new' if side == '+' else 'old'][0]
                    start, count = part['start'], part['count']
                    contents = b''.join(edited[side][start - base:start - base + count])
                    assert contents.count(b'\n') == count
                    assert digest(contents) == part['sha256']
                    assert part['owner'] in (['B1'] if label == 'U--B1' else list('1234567'))
                    for n in range(start, start + count):
                        identity = (side, n)
                        assert identity not in seen, (label, path, identity)
                        seen.add(identity)
                        covered[side].add(n - base)
                    totals[label + ':' + side] += count
                    if label == 'B1--F':
                        expected_parts.append({'hunk_id': hunk['id'], 'part_index': index, 'path': path, **part})
                for side in ['+', '-']:
                    assert covered[side] == set(range(len(edited[side])))
            for name, info in file['identities'].items():
                tree = git('ls-tree', inputs['refs'][name]['sha'], '--', path).decode().strip()
                if not info['blob']:
                    assert not tree
                    continue
                mode, kind, blob = tree.split('\t')[0].split()
                assert (mode, blob) == (info['mode'], info['blob']) and kind == 'blob'
                data = git('cat-file', 'blob', blob)
                assert digest(data) == info['sha256']
                assert hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == blob
    actual_parts = [p for s in deps['slices'].values() for p in s['source_parts']]
    canonical = lambda p: (p['hunk_id'], p['part_index'])
    assert sorted(actual_parts, key=canonical) == sorted(expected_parts, key=canonical)
    assert len({canonical(p) for p in actual_parts}) == len(expected_parts)
    assert deps['head6_residual']['exact_F_parts'] == deps['slices']['7']['source_parts']
    pre = read('PRE-F7.json')
    pre_data = git('show', pre['commit'] + ':' + pre['path']).decode().splitlines(keepends=True)
    for snip in pre['snippets']:
        text = ''.join(pre_data[snip['start'] - 1:snip['start'] - 1 + snip['count']])
        assert text == snip['text'] and digest(text.encode()) == snip['sha256']
    assert git('diff', '--name-only', inputs['refs']['U']['sha'], inputs['refs']['B1']['sha'], '--',
               'library/kani_core/src/mem_init.rs', 'kani-compiler/src/kani_middle/kani_functions.rs') == b''
    snap = read('UPSTREAM-SNAPSHOT.json')
    assert snap['main']['sha'] == snap['pr']['base']['sha'] == inputs['refs']['U']['sha']
    assert snap['pr']['head']['sha'] == inputs['refs']['B1']['sha']
    assert snap['pr']['state'] == 'open' and snap['pr']['merged'] is False
    assert all(r['object']['sha'] == inputs['refs']['F']['sha'] for r in snap['fork_refs'])
    for name, expected in [('resolve_call', '1'), ('constant_init_mask', '4'), ('has_transfer_protocol', '4'),
                           ('wrapper_inner', '2'), ('maybe_uninit_storage', '2'), ('for_storage', '2'),
                           ('argument_size', '4'), ('delayed_scope', '7')]:
        uses = read('SEAM-USES.json')['symbols'][name]
        definitions = [u for u in uses if re.search(r'\bfn\s+' + name + r'\b', u['text'])]
        assert definitions, name
        for definition in definitions:
            hits = [p for p in expected_parts if p['path'] == definition['path'] and p['side'] == '+' and p['start'] <= definition['line'] < p['start'] + p['count']]
            if hits:
                assert all(p['owner'] == expected for p in hits), (name, hits)
    for path, head in [(REPO, inputs['refs']['F']['sha']), ('/root/kani-fix-b1-upstream', inputs['refs']['B1']['sha']),
                       (inputs['worker14_worktree'], inputs['refs']['B1']['sha'])]:
        assert subprocess.check_output(['git', '-C', path, 'rev-parse', 'HEAD']).decode().strip() == head
        assert subprocess.check_output(['git', '-C', path, 'status', '--porcelain']) == b'', path
    excluded = {'MANIFEST.json', 'RESEARCH-VALIDATION.json'}
    manifest = {p.name: digest(p.read_bytes()) for p in sorted(ROOT.iterdir()) if p.is_file() and p.name not in excluded}
    (ROOT / 'MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n')
    report = {'checked_at_utc': datetime.now(timezone.utc).isoformat(), 'status': 'PASS_STATIC_RESEARCH_CONSISTENCY',
              'checks': ['exact saved Git patches', 'hunk and part hashes/ranges', 'complete unique changed-line ownership',
                         'all original U/B1/F blobs/modes/digests', 'dependency owner-part bijection', 'exact head6 F7 residual list',
                         'historical pre-F7 snippets', 'B1 excludes runtime/marker delta', 'remote snapshot identity/no-drift',
                         'key seam definition owners', 'all three source worktrees clean/pinned'],
              'line_counts': dict(totals), 'manifest_sha256': digest((ROOT / 'MANIFEST.json').read_bytes()),
              'build_CI_push': 'NOT_RUN', 'oracle_docs_map': 'worker15 separate; not accepted by this validation',
              'intermediate_heads': 'NOT_CREATED_NOT_QUALIFIED', 'full_recompose': 'NOT_RUN'}
    (ROOT / 'RESEARCH-VALIDATION.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
