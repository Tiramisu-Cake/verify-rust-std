#!/usr/bin/env python3
"""E2 read-only identity/scope/fixture audit. No Rust compiler/verifier execution."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

SOURCE = Path(sys.argv[1] if len(sys.argv) > 1 else '/root/kani-fix-3300-e2')
BASE = '478aad601fc5a45b142d6a8a2ae85594add9a0e6'
CANDIDATE = '19588e0afa9994a0e892f7f93a72534bdc061452'


def git(*args):
    return subprocess.check_output(['git', '-C', str(SOURCE), *args], text=True).strip()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


assert git('rev-parse', 'HEAD') == CANDIDATE
assert git('rev-parse', 'HEAD^') == BASE
assert not git('status', '--porcelain')
changed = git('diff', '--name-only', BASE, 'HEAD').splitlines()
expected = sorted([
    'kani-compiler/src/codegen_cprover_gotoc/codegen/static_var.rs',
    'kani-compiler/src/codegen_cprover_gotoc/context/immutable_allocations.rs',
    *[f'tests/expected/uninit/part1-edges/immutable-{edge}-{kind}.rs'
      for edge in ['subrange', 'relocation'] for kind in ['legal', 'hole']],
])
assert changed == expected
critical = [
    'library', 'kani-driver', 'kani-compiler/src/kani_middle',
    'tests/json-handler', 'scripts', 'tests/expected/uninit/immutable-masks',
    'tests/expected/uninit/promoted-allocations',
    'tests/expected/uninit/maybe-uninit-reset-alias',
    'tests/expected/uninit/maybe-uninit-reset-zst',
]
for path in critical:
    assert git('rev-parse', f'{BASE}:{path}') == git('rev-parse', f'HEAD:{path}')
fixtures = []
for edge in ['subrange', 'relocation', 'static']:
    for kind in ['legal', 'hole']:
        rel = f'tests/expected/uninit/part1-edges/immutable-{edge}-{kind}.rs'
        path = SOURCE / rel
        text = path.read_text()
        golden = path.with_suffix('.expected')
        golden_rel = str(golden.relative_to(SOURCE))
        assert git('rev-parse', f'{BASE}:{golden_rel}') == git('rev-parse', f'HEAD:{golden_rel}')
        root = f'immutable_{edge}_{kind}'
        assert text.count('#[kani::proof]') == 1 and f'fn {root}()' in text
        assert f'Checking harness {root}...' in golden.read_text()
        assert ('VERIFICATION:- SUCCESSFUL' in golden.read_text()) == (kind == 'legal')
        assert text.count('MaybeUninit::uninit()') == (kind == 'hole')
        if edge == 'subrange':
            assert 'ALLOCATION: &[MaybeUninit<u8>; 4]' in text
            assert 'SUBRANGE: &[MaybeUninit<u8>; 3]' in text
            assert '.add(1).cast::<[MaybeUninit<u8>; 3]>()' in text
        if edge == 'relocation':
            assert text.count('[MaybeUninit<&u8>; 3]') == 2
            assert 'MaybeUninit::new(&0u8)' in text
        fixtures.append({'path': rel, 'root': root, 'sha256': sha(path),
                         'expected_sha256': sha(golden), 'actual_mir': 'NOT_RUN',
                         'actual_full_failure_set': 'NOT_RUN'})
for field in ['%an <%ae>', '%cn <%ce>']:
    assert git('show', '-s', f'--format={field}', 'HEAD') == 'Tiramisu-Cake <igkharin@gmail.com>'
subprocess.run(['git', '-C', str(SOURCE), 'diff', '--check', BASE, 'HEAD'], check=True)
print(json.dumps({'base': BASE, 'candidate': CANDIDATE,
                  'tree': git('rev-parse', 'HEAD^{tree}'), 'scope': 'PASS',
                  'critical_subtree_identities': 'PASS', 'six_fixture_maps': fixtures,
                  'changed_paths': {path: sha(SOURCE / path) for path in changed},
                  'expected_files': 'UNCHANGED', 'diff_check': 'PASS',
                  'compiler_verifier_execution': 'NOT_RUN', 'proof_credit': 'NONE'}, indent=2))
