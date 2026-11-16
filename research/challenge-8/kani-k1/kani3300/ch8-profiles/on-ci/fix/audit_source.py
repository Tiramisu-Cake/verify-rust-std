#!/usr/bin/env python3
"""Pinned source-preservation checks, not compilation or formal verification."""
import collections
import hashlib
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
SOURCE = json.loads((HERE / 'SOURCE.json').read_bytes())
REPO = SOURCE['worktree']
OLD, NEW = SOURCE['parent'], SOURCE['source_sha']
DIR = 'library/core/src/slice/sort/shared/smallsort/verify/'


def git(*args):
    return subprocess.check_output(['git', '-C', REPO, *args], text=True)


def function(text, name):
    start = re.search(r'(?m)^(?:pub\([^\n]+\) )?(?:unsafe )?fn ' + re.escape(name) + r'[<(]', text).start()
    opening = text.index('{', start)
    depth = 1
    i = opening + 1
    while depth:
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
        i += 1
    return text[start:i]


def audit():
    assert git('rev-parse', NEW + '^').strip() == OLD
    assert git('rev-parse', NEW + '^{tree}').strip() == SOURCE['source_tree']
    subprocess.run(['git', '-C', REPO, 'diff', '--check', OLD, NEW], check=True)
    paths = git('diff', '--name-only', OLD, NEW).splitlines()
    assert set(paths) == {DIR + p for p in ['helper_contracts.rs', 'helper_contracts_wide.rs',
                                          'merge.rs', 'merge/profiles.rs', 'network.rs']}
    old = {p: git('show', OLD + ':' + p) for p in paths}
    new = {p: git('show', NEW + ':' + p) for p in paths}
    for p in paths:
        # Existing assumptions and executable assertions remain; new PFC adds no assumptions.
        for call in ('kani::assume', 'kani::assert'):
            pattern = r'^.*' + re.escape(call) + r'.*$'
            assert collections.Counter(re.findall(pattern, old[p], re.M)) == collections.Counter(re.findall(pattern, new[p], re.M)), (p, call)
    p = DIR + 'merge/profiles.rs'
    assert function(old[p], 'merge_profile') == function(new[p], 'merge_profile')
    old_contract = old[p][old[p].index('#[kani::requires(merge_regions'):old[p].index('// Matched summary')]
    assert old_contract.strip() in new[p]
    for p in (DIR + 'helper_contracts.rs', DIR + 'helper_contracts_wide.rs'):
        assert function(old[p], 'arbitrary_less') == function(new[p], 'arbitrary_less')
        assert '&mut arbitrary_less::<' not in new[p]
        assert new[p].count('|a, b| arbitrary_less::<T>(a, b)') == 1
    for path, fn in [(DIR + 'network.rs', 'swap_contract_fixed'),
                     (DIR + 'merge.rs', 'sort4_length_body'),
                     (DIR + 'merge/profiles.rs', 'sort4_consumer')]:
        assert function(old[path], fn).split('{', 1)[0] == function(new[path], fn).split('{', 1)[0]
    covers_old = collections.Counter(line.strip() for text in old.values() for line in text.splitlines() if 'kani::cover(' in line)
    covers_new = collections.Counter(line.strip() for text in new.values() for line in text.splitlines() if 'kani::cover(' in line)
    assert not (covers_old - covers_new)
    assert covers_new - covers_old == collections.Counter({'kani::cover(true, "four-element merge returns");': 1})
    for path in ['library/core/src/slice/sort/shared/smallsort.rs', DIR + 'forwarding_contracts.rs']:
        assert git('show', OLD + ':' + path) == git('show', NEW + ':' + path)
    return {'schema': 'prof-on-02-source-audit-v1', 'state': 'STATIC_PASS', 'source': NEW,
            'tree': SOURCE['source_tree'], 'checks': ['parent/tree/allowed paths', 'unchanged runtime/forwarders',
            'unchanged general merge contract/body', 'unchanged arbitrary_less reads/nondeterminism',
            'unchanged generic headers/assumptions/assertions', 'all original covers + one new return cover'],
            'qualification': 'NOT_RUN', 'proof_credit': 'NONE'}


if __name__ == '__main__':
    result = audit()
    (HERE / 'static-audit.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
