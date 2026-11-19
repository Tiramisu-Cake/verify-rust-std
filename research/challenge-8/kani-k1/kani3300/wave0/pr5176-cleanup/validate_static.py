#!/usr/bin/env python3
"""Static preservation/discovery audit; never launches a Rust or Kani tool."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import textwrap

ROOT = Path('/root/kani-pr5176-cleanup-w13')
OUT = Path(__file__).resolve().parent
HEAD = '3d9a1809388f74c62ea9fb7320e123db0b8b37fa'
PREFIX = 'tests/expected/'
MAIN = PREFIX + 'zst-union-arm/'
SHAPES = ['array-first', 'nested-unit-array', 'nested-empty-byte-array',
          'aligned-array', 'struct-array']
RECURSIVE = ['recursive-arm', 'recursive-zst-arm']
REPEATED = '// The ZST arm is deliberately first, including for the nested shapes.\n'


def original(path):
    return subprocess.check_output(['git', '-C', str(ROOT), 'show', f'{HEAD}:{path}'])


def digest(data):
    return hashlib.sha256(data).hexdigest()


def proof_functions(source):
    # These concrete fixtures have line comments, quoted strings and balanced blocks.
    functions = {}
    for match in re.finditer(r'#\[kani::proof\]\nfn (\w+)\(\) \{', source):
        end = match.end()
        depth = 1
        for token in re.finditer(r'//[^\n]*|"(?:\\.|[^"\\])*"|[{}]', source[end:]):
            if token.group() == '{':
                depth += 1
            elif token.group() == '}':
                depth -= 1
            if depth == 0:
                functions[match[1]] = source[match.start():end + token.end()]
                break
        assert depth == 0, match[1]
    return functions


def contains_lines(output, expected):
    # Transcribed from TestCx::contains_lines/contains, runtest.rs:564-598.
    output_lines = output.split('\n')
    group = []
    for line in expected.split('\n'):
        continued = line.endswith('\\')
        group.append(line[:-1] if continued else line)
        if not continued:
            if not any(all(e.strip() in o for e, o in zip(group, window))
                       for window in (output_lines[i:i + len(group)]
                                      for i in range(len(output_lines) - len(group) + 1))):
                return False
            group = []
    assert not group  # All audited goldens end with a newline, not a backslash.
    return True


assert subprocess.check_output(['git', '-C', str(ROOT), 'branch', '--show-current'],
                               text=True).strip() == 'cleanup/pr5176-20261119'
compiler = 'kani-compiler/src/codegen_cprover_gotoc/codegen/typ.rs'
compiler_bytes = (ROOT / compiler).read_bytes()
assert compiler_bytes == original(compiler)
main = (ROOT / MAIN / 'main.rs').read_text()
old_main = original(MAIN + 'main.rs').decode()
assert main.startswith(old_main)
assert len(proof_functions(old_main)) == 7
preservation = {}
old_cases = proof_functions(old_main)
new_cases = proof_functions(main[:len(old_main)])

for shape in SHAPES:
    old_path = PREFIX + 'zst-union-edge-' + shape + '/main.rs'
    old = original(old_path).decode()
    module = shape.replace('-', '_')
    match = re.search(r'\nmod ' + module + r' \{\n(.*?)\n\}\n', main, re.S)
    assert match, module
    moved = textwrap.dedent(match[1]) + '\n'
    expected_body = old.split('\n\n', 1)[1].replace(REPEATED, '')
    assert moved == expected_body, module  # Includes concrete types/imports/all code.
    old_cases.update(proof_functions(old))
    new_cases.update(proof_functions(moved))
    assert not (ROOT / old_path).parent.exists()

for name in RECURSIVE:
    old_path = PREFIX + 'zst-union-' + name + '/main.rs'
    old = original(old_path).decode()
    moved = (ROOT / MAIN / (name + '.rs')).read_text()
    assert moved == old.replace(
        '// Only the pointer graph should retain this union; reading it would change the root.',
        '// The pointer field reaches this union while the enclosing struct is incomplete.')
    old_cases.update(proof_functions(old))
    new_cases.update(proof_functions(moved))
    assert not (ROOT / old_path).parent.exists()

assert old_cases == new_cases
assert len(old_cases) == 14
assert main.count('#[kani::proof]') == 12
assert REPEATED not in main
for name, body in old_cases.items():
    preservation[name] = digest(body.encode())

discovery = []
cover_labels = []
negative_checks = 0
for source_path in sorted((ROOT / MAIN).glob('*.rs')):
    source = source_path.read_text()
    oracle = source_path.with_suffix('.expected')
    assert oracle.exists()
    assert not source_path.name.startswith(('.', '#', '~'))
    assert not re.search(r'(?m)^\s*//\s*(compile-flags|kani-flags|cbmc-flags|ignore-|edition:)', source)
    assert not re.search(r'(?m)^\s*(#\[cfg|mod \w+;|include!)', source)
    count = source.count('#[kani::proof]')
    assert count == (12 if source_path.name == 'main.rs' else 1)
    expected = oracle.read_text()
    summary = f'Complete - {count} successfully verified harnesses, 0 failures, {count} total.'
    assert summary in expected
    assert 'VERIFICATION:- SUCCESSFUL' in expected
    labels = re.findall(r'kani::cover!\([^;]*?"([^"]+)"\s*\)', source, re.S)
    assert len(labels) == (5 if count == 12 else 1)
    cover_labels.extend(labels)
    blocks = [f'Status: SATISFIED\nDescription: "{label}"' for label in labels]
    for block in blocks:
        assert block.replace('\n', '\\\n', 1) in expected
    # Independent blocks may appear in any harness order, but each cover's two
    # lines must be adjacent and all covers/full-success summary must be present.
    output = '\n\n'.join(reversed(blocks)) + '\nVERIFICATION:- SUCCESSFUL\n' + summary + '\n'
    assert contains_lines(output, expected)
    negatives = [output.replace(summary, ''),
                 output.replace(summary, f'Complete - {count - 1} successfully verified harnesses, 1 failures, {count} total.'),
                 output.replace(summary, 'Complete - 1 successfully verified harnesses, 0 failures, 1 total.')
                 if count > 1 else output.replace(summary, 'Complete - 0 successfully verified harnesses, 0 failures, 0 total.'),
                 output.replace('VERIFICATION:- SUCCESSFUL', 'VERIFICATION:- FAILED')]
    for block in blocks:
        negatives.extend([output.replace(block, ''),
                          output.replace(block, block.replace('SATISFIED', 'FAILED')),
                          output.replace(block, block.replace('\n', '\nintervening line\n'))])
    for bad in negatives:
        assert not contains_lines(bad, expected)
    negative_checks += len(negatives)
    discovery.append({'source': str(source_path.relative_to(ROOT)),
                      'expected': str(oracle.relative_to(ROOT)),
                      'harnesses': count, 'covers': labels})

assert len(discovery) == 3 and len(cover_labels) == 7
assert sum(len(re.findall('kani::cover!', body)) for body in old_cases.values()) == 7
assert not (ROOT / MAIN / 'expected').exists()
snapshot = json.loads((OUT / 'PR-SNAPSHOT.json').read_text())
assert snapshot['head_sha'] == HEAD and snapshot['state'] == 'open'
draft = (OUT / 'PR-BODY.md').read_text()
for prefix in ['By submitting this pull request,', '*Disclosure:']:
    before = [line for line in snapshot['body'].splitlines() if line.startswith(prefix)]
    after = [line for line in draft.splitlines() if line.startswith(prefix)]
    assert len(before) == 1 and before == after
assert 'Each new harness includes' not in draft
assert draft.count('https://github.com/Tiramisu-Cake/kani/actions/runs/') == 1
subprocess.run(['git', '-C', str(ROOT), 'diff', '--check'], check=True)
report = {'status': 'PASS_STATIC_ONLY', 'initial_head': HEAD,
          'compiler_file_sha256_unchanged': digest(compiler_bytes),
          'original_main_sha256_unchanged_prefix': digest(old_main.encode()),
          'all_14_harness_bodies_sha256_unchanged_after_deindent': preservation,
          'source_based_discovery': discovery, 'oracle_negative_controls_rejected': negative_checks,
          'license_and_disclosure_byte_identical': True,
          'native_compilation_discovery_verification_CI': 'NOT_RUN',
          'execution_evidence_credit': 'NONE'}
(OUT / 'STATIC-CHECK.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
