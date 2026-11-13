#!/usr/bin/env python3
"""Static identities and M3-R3 scope; never invokes Rust tools or CI."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent


def check():
    inputs = json.loads((HERE / 'INPUTS.json').read_text())
    repo = Path(inputs['source_clone'])

    def git(*args):
        return subprocess.check_output(['git', '-C', str(repo), *args], text=True).strip()

    base, head = inputs['baseline_sha'], inputs['source_sha']
    assert git('rev-parse', 'HEAD') == head
    assert git('rev-parse', 'HEAD^{tree}') == inputs['source_tree']
    assert git('rev-parse', base + '^{tree}') == inputs['baseline_tree']
    assert git('branch', '--show-current') == inputs['source_branch']
    assert git('status', '--porcelain') == ''
    commits = git('rev-list', base + '..HEAD').splitlines()
    assert git('rev-parse', commits[-1] + '^') == base
    assert all(commit not in git('rev-list', 'HEAD').splitlines()
               for commit in inputs['excluded_guard_commits'])
    expected_paths = {
        'docs/src/reference/experimental/contracts.md',
        'tests/expected/uninit/part1-composition/move-return-reinit.rs',
        'tests/expected/uninit/part1-composition/move-return-reinit.expected',
        'tests/expected/uninit/part1-composition/move-return-top-level.rs',
        'tests/expected/uninit/part1-composition/move-return-top-level.expected',
    }
    assert set(git('diff', '--name-only', base, head).splitlines()) == expected_paths
    assert {row['path'] for row in inputs['files']} == expected_paths
    for row in inputs['files']:
        assert hashlib.sha256((repo / row['path']).read_bytes()).hexdigest() == row['sha256']
    for path, tree in inputs['unchanged_trees'].items():
        assert git('rev-parse', base + ':' + path) == tree
        assert git('rev-parse', head + ':' + path) == tree
    assert not (repo / 'tests/expected/uninit/aggregate-transfer-boundary').exists()
    assert not (repo / 'docs/dev/kani3300-m3-final-r1-research.md').exists()
    prefix = 'tests/expected/uninit/part1-composition/'
    original_tuple = subprocess.check_output(
        ['git', '-C', str(repo), 'show', base + ':' + prefix + 'move-return-reinit.rs'],
        text=True,
    )
    tuple_source = (repo / prefix / 'move-return-reinit.rs').read_text()
    comment = ('// Known false positive: semantically this must be SUCCESS. Nested aggregate\n'
               '// shadow transfer is not implemented for the tuple returned by handoff.\n'
               '// The pinned failure is a regression observation, not detection of UB here.\n')
    assert tuple_source.replace(comment, '', 1) == original_tuple
    source = (repo / prefix / 'move-return-top-level.rs').read_text()
    roots = re.findall(r'#\[kani::proof\]\s*fn (\w+)\(', source)
    assert roots == ['top_level_move_return_reinit_legal', 'top_level_move_return_source_hole']
    for retained in [
        'type RET = MaybeUninit<u8>;',
        'relay(Move(source))',
        'match reinit { true => do_repair, _ => do_read }',
        '(*pointer).write(23);',
        'read_source(pointer)',
        '*observed_out = observed;',
        'RET = Move(returned);',
        'handoff(MaybeUninit::new(42), true, &raw mut source)',
        'handoff(MaybeUninit::new(42), false, &raw mut source)',
        'assert_eq!(source, 23);',
    ]:
        assert retained in source, retained
    assert source.count('assert_eq!(unsafe { returned.assume_init() }, 42);') == 2
    assert 'kani::assume' not in source and '#[kani::should_panic]' not in source
    observation = (repo / prefix / 'move-return-reinit.expected').read_text()
    assert ('std::mem::transmute_neo::<std::mem::MaybeUninit<u8>, u8>.safety_check.1\\\n'
            ' - Status: FAILURE\\\n'
            ' - Description: "Undefined Behavior: Reading from an uninitialized pointer of type `u8`"') in observation
    for root in ['move_return_reinit_legal', 'move_return_source_hole']:
        assert f'Verification failed for - {root}' in observation
    assert 'Complete - 0 successfully verified harnesses, 2 failures, 2 total.' in observation
    golden = (repo / prefix / 'move-return-top-level.expected').read_text()
    assert 'Checking harness top_level_move_return_reinit_legal...\nVERIFICATION:- SUCCESSFUL' in golden
    assert 'Verification failed for - top_level_move_return_source_hole' in golden
    assert 'Complete - 1 successfully verified harnesses, 1 failures, 2 total.' in golden
    git('diff', '--check', base, head)
    return {
        'source_sha': head, 'source_tree': inputs['source_tree'],
        'identities': 'PASS', 'direct_baseline_branch': 'PASS',
        'guard_commits_excluded': 'PASS', 'source_diff_paths': len(expected_paths),
        'unchanged_subtrees': len(inputs['unchanged_trees']),
        'tuple_source_body_unchanged': 'PASS', 'top_level_static_obligations': 'PASS',
        'diff_check': 'PASS', 'Rust_typecheck': 'NOT_RUN',
        'Kani_CBMC_CI': 'NOT_RUN', 'proof_credit': 'NONE',
    }


if __name__ == '__main__':
    print(json.dumps(check(), indent=2))
