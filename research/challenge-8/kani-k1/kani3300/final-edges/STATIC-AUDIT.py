#!/usr/bin/env python3
"""Read-only E1 source identity/fixture audit. Does not compile or verify Rust."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

SOURCE = Path(sys.argv[1] if len(sys.argv) > 1 else '/root/kani-fix-3300-e1')
HERE = Path(__file__).resolve().parent
BASE = '94c00a8859bc9e4f0f1b7db73a95dbee88f6213a'
CANDIDATE = 'dc24745c68951effb702a4302e84481ca74bc51a'
TREE = '4e17cba9a9ae0bbc625f5fc6c147ff1cca17dc04'


def git(*args):
    return subprocess.check_output(['git', '-C', str(SOURCE), *args], text=True).strip()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


assert git('rev-parse', 'HEAD') == CANDIDATE
assert git('rev-parse', 'HEAD^') == BASE
assert git('rev-parse', 'HEAD^{tree}') == TREE
assert not git('status', '--porcelain')
checks = json.loads((HERE / 'STATIC-CHECKS.json').read_text())
manifest = json.loads((HERE / 'CONTROL-MAP.json').read_text())
changed = git('diff', '--name-only', BASE, 'HEAD').splitlines()
assert changed == checks['all_changed_paths']
compiler = checks['changed_compiler_files']
assert len(compiler) == 3
for path, expected in compiler.items():
    assert path.startswith('kani-compiler/src/kani_middle/transform/check_uninit/')
    assert sha(SOURCE / path) == expected
for path in changed:
    if path not in compiler:
        assert path.startswith('tests/expected/uninit/part1-edges/')
        previous = subprocess.run(
            ['git', '-C', str(SOURCE), 'cat-file', '-e', f'{BASE}:{path}'],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        assert previous.returncode != 0, 'existing test/golden changed'
for path in checks['critical_paths']:
    assert (SOURCE / path).exists()
    assert git('rev-parse', f'{BASE}:{path}') == git('rev-parse', f'HEAD:{path}')
for record in checks['existing_reuse']:
    assert record['exists'] and (SOURCE / 'tests/expected/uninit' / record['path']).exists()
files = list((SOURCE / 'tests/expected/uninit/part1-edges').glob('*.rs'))
cases = manifest['cases']
assert len(files) == len(cases) == 17
assert len({c['root'] for c in cases}) == 17
assert len({c['input'] for c in cases}) == 17
legal_stems = {p.stem for p in files}
for case in cases:
    path = SOURCE / case['input']
    expected_path = path.with_suffix('.expected')
    assert sha(path) == case['sha256']
    assert sha(expected_path) == case['expected_sha256']
    text = path.read_text()
    expected = expected_path.read_text()
    assert text.count('#[kani::proof]') == 1
    assert f'fn {case["root"]}()' in text
    assert f'Checking harness {case["root"]}...' in expected
    assert case['matched_legal'] in legal_stems
    assert ('VERIFICATION:- SUCCESSFUL' in expected) == (case['required_outcome'] == 'SUCCESS')
    assert case['actual_mir'] == case['actual_properties'] == case['actual_full_failure_set'] == 'NOT_RUN'
    if path.stem.startswith('immutable-') and path.stem.endswith('-legal'):
        assert case['required_outcome'] == 'SUCCESS'
        assert not case['required_failures']
    if case['required_outcome'] == 'UNSUPPORTED':
        assert 'Kani does not support unsized by-value shadow argument/return transfers.' in expected
subprocess.run(['git', '-C', str(SOURCE), 'diff', '--check', BASE, 'HEAD'], check=True)
print(json.dumps({'source': CANDIDATE, 'tree': TREE, 'scope': 'PASS',
                  'critical_tree_identities': 'PASS', 'fixture_map_17': 'PASS',
                  'diff_check': 'PASS', 'compiler_verifier_execution': 'NOT_RUN'}))
