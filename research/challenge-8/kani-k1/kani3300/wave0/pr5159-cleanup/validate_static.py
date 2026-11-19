"""Bounded static audit; invokes only Git and Python, never native verification."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

OUT = Path(__file__).resolve().parent
SOURCE = Path('/root/kani-pr5159-cleanup-w13')
HEAD = '78f745bb696c85095a9582f959d4854ec494c4f5'
COMPILER = 'kani-compiler/src/codegen_cprover_gotoc/codegen/intrinsic.rs'
NEGATIVE = 'tests/expected/intrinsics/volatile_load/'
POSITIVE = 'tests/kani/Intrinsics/Volatile/load_zst.rs'
SUMMARY = 'Complete - 0 successfully verified harnesses, 1 failures, 1 total.'


def git(*args):
    return subprocess.check_output(['git', '-C', str(SOURCE), *args])


def original(path):
    return git('show', HEAD + ':' + path)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


# Port of TestCx::contains_lines/contains, runtest.rs:564-597. Independent
# blocks have no ordering constraint; a trailing backslash joins adjacent lines.
def accepts(output, expected):
    lines = output.split('\n')
    pending = []

    def contains(parts):
        return any(all(part.strip() in line for part, line in zip(parts, lines[i:]))
                   for i in range(len(lines) - len(parts) + 1))

    for line in expected.split('\n'):
        if line.endswith('\\'):
            pending.append(line[:-1])
        else:
            pending.append(line)
            if not contains(pending):
                return False
            pending = []
    return not pending or contains(pending)


assert git('branch', '--show-current').decode().strip() == 'cleanup/pr5159-20261119'
assert git('merge-base', HEAD, 'HEAD').decode().strip() == HEAD
assert digest((OUT / 'FINDINGS.md').read_bytes()) == (
    '54bfa7b449d4f5fcf256f3ebdd4a5866db705e9ed45c5352b892581ec393d525')
compiler = (SOURCE / COMPILER).read_bytes()
assert compiler == original(COMPILER)
assert digest(compiler) == '09a6e3f017471549fc5c7a45471a321157339409c42a29471f0bd3f8f035bed7'
replacements = {
    POSITIVE: (
        '// Regression for #5072: volatile ZST reads must not access memory.',
        '// Volatile loads of inhabited ZSTs accept aligned reference, dangling and null pointers (#5072).'),
    NEGATIVE + 'zst_unaligned.rs': (
        '// An over-aligned ZST still requires alignment even though no memory is read.',
        '// An over-aligned ZST requires an aligned source address.'),
    NEGATIVE + 'zst_uninhabited.rs': (
        '// Preserve the diagnostic for a load that cannot return an inhabited value.',
        '// Loading an uninhabited ZST requires a safety diagnostic.'),
}
harnesses = {}
for path, (old, new) in replacements.items():
    before = original(path)
    after = (SOURCE / path).read_bytes()
    assert before.count(old.encode()) == 1
    assert after == before.replace(old.encode(), new.encode())
    # All three sources have only these simple top-level functions; an exact
    # function slice includes its proof attribute, comments and all whitespace.
    pattern = rb'(?m)^#\[kani::proof\]\nfn (\w+)\(\) \{.*?^\}'
    old_functions = list(re.finditer(pattern, before, re.S))
    new_functions = list(re.finditer(pattern, after, re.S))
    assert len(old_functions) == len(new_functions)
    for a, b in zip(old_functions, new_functions):
        assert a.group() == b.group()
        harnesses[a.group(1).decode()] = {'path': path, 'sha256': digest(a.group())}
assert len(harnesses) == 8
assert sum(x['path'] == POSITIVE for x in harnesses.values()) == 6

oracle_results = []
for stem, name in [('zst_unaligned', 'misaligned_zst'),
                   ('zst_uninhabited', 'uninhabited_zst')]:
    path = NEGATIVE + stem + '.expected'
    before = original(path).decode()
    expected = (SOURCE / path).read_text()
    header = 'Checking harness ' + name + '...'
    assert expected == header + '\n' + before + SUMMARY + '\n'
    reason = before.splitlines()[1]
    assert reason in compiler.decode()
    # Representative transcript assembled from the source emitters cited in
    # FINDINGS.md. Synthetic output is never labeled as an observed Kani run.
    status = '\t - Status: FAILURE'
    description = '\t - Description: "' + reason + '"'
    failed = 'Failed Checks: ' + reason
    verdict = 'VERIFICATION:- FAILED'
    blocks = [header, status + '\n' + description, failed, verdict, SUMMARY]
    complete = '\n'.join(blocks) + '\n'
    incomplete = '\n'.join(blocks[:-1]) + '\ninternal compiler error: synthetic tail\n'
    assert accepts(incomplete, before)
    assert not accepts(incomplete, expected)
    accepted = [complete, '\n'.join(reversed(blocks)) + '\n',
                '\n'.join('Thread 0: ' + line for line in complete.split('\n')),
                complete + 'internal compiler error: synthetic tail\n']
    rejected = {
        'setup_only': 'error: compiler setup failed\n',
        'incomplete_error_tail': incomplete,
        'missing_header': complete.replace(header, ''),
        'wrong_header': complete.replace(name, 'unrelated_harness'),
        'missing_completion': complete.replace(SUMMARY, ''),
        'wrong_completion_counts': complete.replace(SUMMARY, 'Complete - 1 successfully verified harnesses, 0 failures, 1 total.'),
        'wrong_reason': complete.replace(reason, 'some unrelated failure'),
        'missing_failed_checks': complete.replace(failed, ''),
        'wrong_verdict': complete.replace(verdict, 'VERIFICATION:- SUCCESSFUL'),
        'wrong_property_status': complete.replace(status, '\t - Status: SUCCESS'),
        'broken_status_reason_adjacency': complete.replace(status + '\n', status + '\nunrelated intervening line\n'),
    }
    assert all(accepts(output, expected) for output in accepted)
    assert all(not accepts(output, expected) for output in rejected.values())
    oracle_results.append({'path': path, 'reason': reason,
                           'preserved_original_body_sha256': digest(before.encode()),
                           'synthetic_accepts': len(accepted),
                           'synthetic_rejects': list(rejected),
                           'complete_output_plus_error_tail_still_matches': True})

expected_changes = set(replacements) | {item['path'] for item in oracle_results}
assert set(git('diff', '--name-only', HEAD).decode().splitlines()) == expected_changes
git('diff', '--check', HEAD)
snapshot = json.loads((OUT / 'PR-SNAPSHOT.json').read_text())
draft = (OUT / 'PR-BODY.md').read_text()
for line in snapshot['body'].splitlines():
    if line.startswith('By submitting this pull request,') or line.startswith('*Disclosure:'):
        assert line in draft.splitlines()
assert 'Resolves #5072' in draft
receipt = {
    'status': 'PASS', 'assurance': 'Static source/byte and synthetic matcher audit only',
    'base_head': HEAD, 'worktree': str(SOURCE),
    'compiler_sha256': digest(compiler), 'compiler_byte_identical': True,
    'findings_sha256_before_edits': digest((OUT / 'FINDINGS.md').read_bytes()),
    'changed_paths': sorted(expected_changes), 'file_level_comment_edits_only': 3,
    'byte_identical_proof_functions': harnesses, 'proof_count': 8,
    'positive_proofs': 6, 'negative_proofs': 2, 'oracle_checks': oracle_results,
    'source_and_output_limits': 'No native execution, MIR-route evidence, exit-code enforcement or proof credit',
    'native_tests': 'NOT_RUN', 'CI': 'NOT_RUN',
}
(OUT / 'STATIC-CHECK.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({'status': 'PASS', 'compiler_byte_identical': True,
                  'proof_functions_byte_identical': len(harnesses),
                  'synthetic_accepts': 8, 'synthetic_rejects': 22}))
