#!/usr/bin/env python3
"""Static source/identity checks only; does not invoke a compiler or verifier."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
M = json.loads((HERE / 'manifest.json').read_text())


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def digest(data):
    return hashlib.sha256(data).hexdigest()


network = M['changed_library_paths'][0]
old = git('show', M['base_sha'] + ':' + network)
new = (ROOT / network).read_bytes()
added = new[len(old):].decode()
assert new.startswith(old)
assert added.startswith('\n#[cfg(kani_smallsort_controls)]\nmod perm12 {\n')
assert git('diff', '--name-only', M['base_sha'], '--', 'library').decode().splitlines() == [network]
assert git('rev-parse', M['base_sha'] + ':library').decode().strip() == M['base_library_tree']
assert git('rev-parse', M['source_sha'] + ':library').decode().strip() == M['source_library_tree']
assert git('show', M['source_sha'] + ':' + network) == new
assert len(new.splitlines()) == 1565
assert all(len(line) <= 100 for line in added.splitlines())
assert not re.search(r'\b(?:assume|any_where|stub|stub_verified)\b', added)
assert added.count('kani::any::<bool>()') == 1
assert added.count('insertion_sort_shift_left(') == 1
assert added.count('#[kani::unwind(25)]') == 1
assert added.count('assert!(') == 2
assert added.index('read_volatile(a)') < added.index('match self.phase')
assert added.index('read_volatile(b)') < added.index('match self.phase')
assert '_ => kani::any::<bool>()' in added
assert 'phase: if PARTITIONED { 0 } else { 2 }' in added
assert 'count_matching_values(pre, probe) == count_matching_values(v, probe)' in added
assert added.index('!prefix_unchanged') < added.index('v[0] ^= 1')
assert added.index('v[0] ^= 1') < added.index('kani::cover(true, "insertion value corruption')
assert added.index('kani::cover(true, "insertion value corruption') < added.index('check_permutation(&pre')
rows = re.findall(r'trace_case!\((\w+), (true|false), (true|false), (true|false), (true|false)\);', added)
assert len(rows) == 6
assert {(a, b) for _, part, a, b, corrupt in rows if part == 'true' and corrupt == 'false'} == {
    ('false', 'false'), ('false', 'true'), ('true', 'false'), ('true', 'true')}
expected = [(r['name'].rsplit('::', 1)[1]) for r in M['g1_entries'][1:]]
assert [row[0] for row in rows] == expected
for path, sha in M['bound_files'].items():
    data = (ROOT / path).read_bytes()
    assert digest(data) == sha, path
    assert data == git('show', M['cap_sha'] + ':' + path), path
for path, sha in M['request_sha256'].items():
    assert digest((HERE / path).read_bytes()) == sha, path
assert (HERE.parent / 'RUN-REQUEST.json').read_bytes() == (HERE / 'g1.request.json').read_bytes()
for label in ('g1', 'g2'):
    req = json.loads((HERE / (label + '.request.json')).read_text())
    assert req['harnesses'] == M[label + '_entries']
    assert req['harness_timeout_minutes'] == 10 and req['controls'] is True
    assert req['uninit_checks'] is False
assert json.loads((HERE / 'g1.request.json').read_text())['kani_jobs'] == 1
assert json.loads((HERE / 'g2.request.json').read_text())['kani_jobs'] == 3
lines = new.decode().splitlines()
assert lines[M['count_failure']['line'] - 1].strip().startswith('assert!(count_matching_values')
assert lines[M['phase_assert_line'] - 1].strip() == 'assert!(trace.phase == 2);'
assert lines[M['corruption_line'] - 1].strip() == 'v[0] ^= 1;'
print(json.dumps({
    'status': 'STATIC_PASS', 'source_sha': M['source_sha'],
    'library_tree': M['source_library_tree'], 'old_network_sha256': digest(old),
    'new_network_sha256': digest(new), 'old_items_byte_identical': True,
    'ordinary_projection_byte_identical_after_removing_new_cfg_module': True,
    'existing_dependency_sources_unchanged': True, 'bound_files_match_cap': True,
    'request_files_match_manifest': True, 'new_harnesses': len(rows),
    'limitations': 'Source/identity checks only; no compiler, AST/MIR binding or machine proof credit.'
}, indent=2))
