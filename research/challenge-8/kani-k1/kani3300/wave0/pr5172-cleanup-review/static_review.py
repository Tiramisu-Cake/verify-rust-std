#!/usr/bin/env python3
"""Independent offline preservation checks; never invokes Rust or verification tools."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

REPO = Path('/root/kani-pr5172-cleanup-w11')
PARENT = '80e5d6fabc0103b0b3117440007ad2d9475f9a9c'
CANDIDATE = 'fef46d2d9d65bf3eb91a282da004043ecd26a208'
PREFIX = 'tests/expected/uninit/unresolved-calls/'
COMPILER = 'kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs'


def git(*args):
    return subprocess.check_output(['git', *args], cwd=REPO)


def blob(revision, path):
    return git('show', f'{revision}:{path}')


def paths(revision):
    return set(git('ls-tree', '-r', '--name-only', revision).decode().splitlines())


def sha(data):
    return hashlib.sha256(data).hexdigest()


def harnesses(data):
    text = data.decode()
    result = {}
    for match in re.finditer(r'#\[kani::proof\]\s*fn\s+(\w+)\s*\(\)\s*\{', text):
        start = match.end()
        depth, end = 1, start
        while depth:
            depth += (text[end] == '{') - (text[end] == '}')
            end += 1
        result[match[1]] = text[start:end - 1]
    assert len(result) == text.count('#[kani::proof]')
    return result


assert git('rev-parse', 'HEAD').decode().strip() == CANDIDATE
assert git('branch', '--show-current').decode().strip() == 'cleanup/pr5172-20261119'
assert git('show', '-s', '--format=%P', CANDIDATE).decode().strip() == PARENT
assert git('rev-list', '--count', f'{PARENT}..{CANDIDATE}').strip() == b'1'
assert not git('status', '--porcelain=v1')
git('diff', '--check', PARENT, CANDIDATE)
old_paths, new_paths = paths(PARENT), paths(CANDIDATE)
old_roots = sorted(p for p in old_paths if p.startswith(PREFIX)
                   and '/' not in p[len(PREFIX):] and p.endswith('.rs'))
new_roots = sorted(p for p in new_paths if p.startswith(PREFIX)
                   and '/' not in p[len(PREFIX):] and p.endswith('.rs'))
assert old_roots == new_roots and len(old_roots) == 22
helper_path = PREFIX + 'auxiliary/analysis_target.rs'
helper = blob(CANDIDATE, helper_path)
seed = helper.replace(b'pub fn check_byte_copy()', b'fn seed()')
seed = seed.removeprefix(b'// Copyright Kani Contributors\n// SPDX-License-Identifier: Apache-2.0 OR MIT\n\n')
assert b'#[inline(never)]\nfn seed()' in seed
assert b'#[kani::proof]' not in helper
module = b'#[path = "auxiliary/analysis_target.rs"]\nmod analysis_target;\n'
rows = []
total, seeded, call_sites = 0, 0, 0
fallback_names = {f'{family}-{mode}.rs' for family in
                  ('erased-pointer', 'fn-pointer', 'global-escaped', 'wrapped-pointer')
                  for mode in ('plain', 'seeded')}
for path in old_roots:
    before, after = blob(PARENT, path), blob(CANDIDATE, path)
    is_seeded = path.endswith('-seeded.rs')
    if is_seeded:
        seeded += 1
        assert before.count(seed) == 1
        assert after.count(module) == 1
        restored = after.replace(module, seed).replace(
            b'analysis_target::check_byte_copy();', b'seed();')
        assert restored == before, path
    else:
        assert before == after and b'analysis_target' not in after
    old_harnesses, new_harnesses = harnesses(before), harnesses(after)
    assert old_harnesses.keys() == new_harnesses.keys()
    body_rows = []
    for name, old_body in old_harnesses.items():
        new_body = new_harnesses[name]
        assert new_body.replace('analysis_target::check_byte_copy();', 'seed();') == old_body
        calls = new_body.count('analysis_target::check_byte_copy();')
        assert calls == int(is_seeded)
        call_sites += calls
        body_rows.append({'name': name, 'old_body_sha256': sha(old_body.encode()),
                          'new_body_sha256': sha(new_body.encode()),
                          'equal_after_only_call_qualification': True})
    total += len(old_harnesses)
    old_expected = path[:-3] + '.expected'
    new_expected = old_expected if old_expected in new_paths else PREFIX + 'expected'
    expected = blob(CANDIDATE, new_expected)
    assert expected == blob(PARENT, old_expected), path
    assert (new_expected == PREFIX + 'expected') == (Path(path).name in fallback_names)
    rows.append({'source': path, 'harnesses': body_rows,
                 'restores_entire_source_exactly': True,
                 'effective_expected': new_expected, 'expected_sha256': sha(expected),
                 'expected_identical_to_parent': True})
assert (total, seeded, call_sites) == (24, 11, 12)
assert len([p for p in new_paths if p.startswith(PREFIX) and p.endswith('.expected')]) == 14
old_comment = (b'// The resolver accepts MIR bodies and foreign items. Foreign items use\n'
               b'                        // the models below; other calls transfer union argument and return state.')
new_comment = (b'// Foreign allocation calls use the models below; other calls store\n'
               b'                        // initialization state for union arguments.')
compiler = blob(CANDIDATE, COMPILER)
assert compiler.count(new_comment) == 1
assert compiler.replace(new_comment, old_comment) == blob(PARENT, COMPILER)
changed = set(git('diff', '--no-renames', '--name-only', PARENT, CANDIDATE).decode().splitlines())
expected_changed = {COMPILER, helper_path, PREFIX + 'expected'}
expected_changed |= {p for p in old_roots if p.endswith('-seeded.rs')}
expected_changed |= {PREFIX + name[:-3] + '.expected' for name in fallback_names}
assert changed == expected_changed
assert len(changed) == 22  # Both endpoints of the displayed rename are counted.
assert all((REPO / p).read_bytes() == blob(CANDIDATE, p) for p in new_paths if p.startswith(PREFIX))
print(json.dumps({'status': 'PASS', 'assurance': 'STATIC_SOURCE_AND_BYTE_PRESERVATION_ONLY',
                  'parent': PARENT, 'candidate': CANDIDATE,
                  'candidate_tree': git('rev-parse', CANDIDATE + '^{tree}').decode().strip(),
                  'source_roots': 22, 'proof_harnesses': total, 'seeded_roots': seeded,
                  'helper_call_sites': call_sites, 'fallback_users': len(fallback_names),
                  'named_expected_files': 14, 'compiler_comment_only': True,
                  'exact_change_scope': sorted(changed), 'fixtures': rows}, indent=2))
