#!/usr/bin/env python3
"""Independent pinned byte/oracle audit. Runs Python and read-only Git only."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path('/root/kani-pr5159-cleanup-w13')
BASE = '78f745bb696c85095a9582f959d4854ec494c4f5'
CANDIDATE = '282d007d06a2fc45ca6e6dc719a305f333b63a7c'
HERE = Path(__file__).resolve().parent


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args])


def blob(rev, path):
    return git('show', f'{rev}:{path}')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def matches(output, expected):
    # Port of TestCx::contains_lines/contains, runtest.rs:564-597.
    actual = output.split('\n')
    block = []

    def present():
        return any(all(want.strip() in got for got, want in zip(
            actual[i:i + len(block)], block))
            for i in range(len(actual) - len(block) + 1))

    for line in expected.split('\n'):
        if line.endswith('\\'):
            block.append(line[:-1])
        else:
            block.append(line)
            if not present():
                return False
            block = []
    return not block or present()


assert git('rev-parse', 'HEAD').decode().strip() == CANDIDATE
assert git('rev-parse', 'HEAD^').decode().strip() == BASE
assert git('branch', '--show-current').decode().strip() == 'cleanup/pr5159-20261119'
assert not git('status', '--porcelain=v1')
assert git('rev-list', '--count', f'{BASE}..{CANDIDATE}').strip() == b'1'
git('diff', '--check', BASE, CANDIDATE)

positive = 'tests/kani/Intrinsics/Volatile/load_zst.rs'
negative = 'tests/expected/intrinsics/volatile_load/'
sources = [positive, negative + 'zst_unaligned.rs', negative + 'zst_uninhabited.rs']
expected_paths = [negative + 'zst_unaligned.expected', negative + 'zst_uninhabited.expected']
assert set(git('diff', '--name-only', BASE, CANDIDATE).decode().splitlines()) == set(sources + expected_paths)
proofs = {}
for path in sources:
    before, after = blob(BASE, path), blob(CANDIDATE, path)
    old_lines, new_lines = before.splitlines(keepends=True), after.splitlines(keepends=True)
    assert len(old_lines) == len(new_lines)
    assert old_lines[4].startswith(b'// ') and new_lines[4].startswith(b'// ')
    assert old_lines[4] != new_lines[4]
    new_lines[4] = old_lines[4]
    assert b''.join(new_lines) == before  # Every byte except the one header comment.
    old_proofs = before.split(b'#[kani::proof]\n')[1:]
    new_proofs = after.split(b'#[kani::proof]\n')[1:]
    assert old_proofs == new_proofs
    for chunk in new_proofs:
        name = re.match(rb'fn (\w+)\(\)', chunk).group(1).decode()
        proofs[name] = {'path': path, 'sha256_from_fn_to_next_proof_or_eof': digest(chunk)}
assert len(proofs) == 8
compiler_path = 'kani-compiler/src/codegen_cprover_gotoc/codegen/intrinsic.rs'
compiler = blob(CANDIDATE, compiler_path)
assert blob(BASE, compiler_path) == compiler

# Derive strings from the emitting sources, independently of expected files.
runner = blob(CANDIDATE, 'kani-driver/src/harness_runner.rs').decode()
header_template = re.search(r'format!\("(Checking harness \{\}\.\.\.)", harness.pretty_name\)', runner).group(1)
summary_template = re.search(r'"(Complete - \{succeeding\}[^"\n]+)"', runner).group(1)
summary = summary_template.format(succeeding=0, failing=1, total=1)
intrinsic = compiler.decode()
load = intrinsic[intrinsic.index('    fn codegen_volatile_load('):intrinsic.index('    /// A volatile write')]
reasons = [re.search(r'PropertyClass::SafetyCheck,\s+"([^"]+)"', load).group(1)]
reasons.append(re.search(r'let validity_check =.*?PropertyClass::SafetyCheck,\s+"([^"]+)"', load, re.S).group(1))
assert intrinsic[:intrinsic.index('    /// c.f.')].count('"' + reasons[1] + '"') == 1
oracles = []
for path, name, reason in zip(expected_paths, ['misaligned_zst', 'uninhabited_zst'], reasons):
    old = blob(BASE, path).decode()
    expected = blob(CANDIDATE, path).decode()
    header = header_template.format(name)
    assert expected == header + '\n' + old + summary + '\n'
    assert old == f'FAILURE\\\n{reason}\nFailed Checks: {reason}\nVERIFICATION:- FAILED\n'
    output = (f'{header}\n\nRESULTS:\nCheck 1: synthetic.safety_check.1\n'
              f'\t - Status: FAILURE\n\t - Description: "{reason}"\n'
              f'\t - Location: synthetic.rs:1\n\nFailed Checks: {reason}\n'
              f' File: "synthetic.rs", line 1, in {name}\n\nVERIFICATION:- FAILED\n'
              f'Manual Harness Summary:\nVerification failed for - {name}\n{summary}\n')
    assert matches(output, expected)
    assert matches('\n'.join('Thread 2: ' + line for line in output.split('\n')), expected)
    rejected = {
        'wrong_reason_both_sites': output.replace(reason, 'dereference failure'),
        'wrong_failed_checks_reason': output.replace('Failed Checks: ' + reason, 'Failed Checks: dereference failure'),
        'wrong_property_reason': output.replace('Description: "' + reason, 'Description: "dereference failure'),
        'reason_only_on_successful_property': output.replace('Status: FAILURE', 'Status: SUCCESS'),
        'broken_status_reason_adjacency': output.replace('\n\t - Description:', '\nintervening line\n\t - Description:'),
        'wrong_verdict': output.replace('VERIFICATION:- FAILED', 'VERIFICATION:- SUCCESSFUL'),
        'wrong_harness': output.replace(header, 'Checking harness wrong_name...'),
        'missing_header': output.replace(header + '\n', ''),
        'header_punctuation': output.replace(header, header[:-1]),
        'missing_completion': output.replace(summary + '\n', ''),
        'wrong_counts': output.replace(summary, summary_template.format(succeeding=1, failing=0, total=1)),
        'internal_spacing': output.replace(summary, summary.replace(' - ', '  - ')),
        'completion_punctuation': output.replace(summary, summary[:-1]),
    }
    for label, text in rejected.items():
        assert not matches(text, expected), (path, label)
    for label in ['missing_header', 'missing_completion', 'wrong_harness', 'wrong_counts']:
        assert matches(rejected[label], old), (path, label, 'old oracle unexpectedly failed')
    assert matches(output + 'INTERNAL ERROR: synthetic extra tail\n', expected)
    oracles.append({'path': path, 'header': header, 'reason': reason, 'summary': summary,
                    'preserved_old_body_sha256': digest(old.encode()), 'accepted_synthetic_variants': 2,
                    'rejected_synthetic_variants': list(rejected), 'complete_plus_error_tail_matches': True})

draft = (HERE.parent / 'pr5159-cleanup/PR-BODY.md').read_bytes()
snapshot = json.loads((HERE.parent / 'pr5159-cleanup/PR-SNAPSHOT.json').read_text())
protected = [line for line in snapshot['body'].splitlines()
             if line.startswith('By submitting') or line.startswith('*Disclosure:')]
assert len(protected) == 2
assert all(draft.decode().splitlines().count(line) == 1 for line in protected)
result = {'status': 'PASS', 'assurance': 'Independent static bytes/source and synthetic matcher checks only',
          'candidate': CANDIDATE, 'parent': BASE, 'tree': git('rev-parse', 'HEAD^{tree}').decode().strip(),
          'compiler_byte_identical_sha256': digest(compiler), 'proof_count': len(proofs), 'proofs': proofs,
          'only_rs_changes': 'One file-level comment at line 5 in each of three files; every other byte identical',
          'oracles': oracles, 'pr_draft_sha256': digest(draft), 'license_and_ai_disclosure_exact': True,
          'native_and_CI': 'NOT_RUN', 'review_script_sha256': digest(Path(__file__).read_bytes())}
print(json.dumps(result, indent=2))
