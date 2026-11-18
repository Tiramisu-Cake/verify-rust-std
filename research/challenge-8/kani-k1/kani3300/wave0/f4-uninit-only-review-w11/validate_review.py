#!/usr/bin/env python3
"""Independent static review replay. Native tool execution is forbidden."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import runpy
import subprocess
import sys
from unittest.mock import patch

OUT = Path(__file__).resolve().parent
G0 = OUT.parents[5]
PACKET = OUT.parent / 'f4-uninit-only'
SOURCE = Path('/root/kani-f4-uninit-only-w15')
TASK = 'fd388552f401d9f72cea6e4b17d0678bdb7e54c1'
PACKAGE = 'a16ef717e18ca8263e360c24058b13a3ef4d4605'
HEAD = 'ca1452227d6ad319f1b9bc1ad33bf618120733eb'
TREE = 'baedd51d92073ecb2b96991bae7dc562ee8f58a2'
BASE = 'b5a9678fd7c2a0f67c3fcafd90057fc2afaf9b5d'
MAIN = 'faffcee3bca2770c03bd21c3bde89cc8f6f7a14e'
checks = []


def git(root, *args):
    return subprocess.check_output(['git', *args], cwd=root)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def snapshot():
    return {p.name: sha(p.read_bytes()) for p in sorted(PACKET.iterdir()) if p.is_file()}


def record(name):
    checks.append(name)


packet_rel = str(PACKET.relative_to(G0))
files = git(G0, 'ls-tree', '-r', '--name-only', PACKAGE, '--', packet_rel).decode().splitlines()
assert len(files) == 17
for name in files:
    assert (G0 / name).read_bytes() == git(G0, 'show', PACKAGE + ':' + name), name
task_rel = 'research/challenge-8/kani-k1/TASK-CH8-F4-UNINIT-ONLY-REVIEW-W11.md'
assert (G0 / task_rel).read_bytes() == git(G0, 'show', TASK + ':' + task_rel)
before = snapshot()
manifest = json.loads((PACKET / 'MANIFEST.json').read_text())
assert manifest['files_sha256'] == {k: v for k, v in before.items() if k != 'MANIFEST.json'}
record('Exact issued task and all 17 committed package files; author manifest matches')

assert git(SOURCE, 'rev-parse', 'HEAD').decode().strip() == HEAD
assert git(SOURCE, 'rev-parse', HEAD + '^{tree}').decode().strip() == TREE
assert git(SOURCE, 'show', '-s', '--format=%P', HEAD).decode().strip() == BASE
assert git(SOURCE, 'status', '--porcelain') == b''
index_path = Path(git(SOURCE, 'rev-parse', '--git-path', 'index').decode().strip())
if not index_path.is_absolute():
    index_path = SOURCE / index_path
index_before = sha(index_path.read_bytes())
pins = json.loads((PACKET / 'SOURCE-PINS.json').read_text())
assert (pins['source'], pins['tree'], pins['parent']) == (HEAD, TREE, BASE)
for group in ('changed_file_sha256', 'full_main_changed_file_sha256', 'workflow_sha256'):
    for name, expected in pins[group].items():
        committed = git(SOURCE, 'show', HEAD + ':' + name)
        assert sha(committed) == expected == sha((SOURCE / name).read_bytes())
assert len(pins['workflow_sha256']) == 16
assert git(SOURCE, 'diff', MAIN, HEAD, '--', '.github', 'scripts', 'library',
           'Cargo.toml', 'Cargo.lock', 'rust-toolchain.toml') == b''
for name in pins['workflow_sha256']:
    assert git(SOURCE, 'show', MAIN + ':' + name) == git(SOURCE, 'show', HEAD + ':' + name)
for name, expected in pins['patch_sha256'].items():
    assert before[name] == expected
record('Clean source SHA/tree/direct parent; committed file/workflow/patch hashes; all 16 workflows invariant from main')

prior = json.loads((OUT.parent / 'f4-fix-review/REVIEW.json').read_text())
provenance = json.loads((PACKET / 'PROVENANCE.json').read_text())
for name, expected in provenance['reference_sha256'].items():
    assert sha((G0 / name).read_bytes()) == expected, name
for commit, name in (
        ('cbfd888f274a0666f09af79d98ef4b8b8061f497', 'f4-fix-review/REVIEW.json'),
        ('4d79ed98f46d3d89feb25509cffa0704a0398cad', 'f4-fix-plan-r1-review/REVIEW.json')):
    path = OUT.parent / name
    assert path.read_bytes() == git(G0, 'show', commit + ':' + str(path.relative_to(G0)))
assert prior['source_static_assessment'].startswith('No blocking source-code finding;')
assert prior['tree'] == git(SOURCE, 'rev-parse', BASE + '^{tree}').decode().strip()
assert git(SOURCE, 'diff', BASE, HEAD, '--', 'kani-compiler/src/kani_middle') == b''
record('Inherited source assessment bound to identical b5 tree and invariant transformation module')

# Execute the exact author validator with its one package write intercepted.
# All native probes inside it were inspected and are mocked; subprocesses are Git/bash -n.
# Temporary isolated indexes reproduce patches; the real source index stays intact.
original_write = Path.write_text
captured = {}


def intercepted_write(path, text, *args, **kwargs):
    if path.resolve() == (PACKET / 'VALIDATION.json').resolve():
        captured['validation'] = text
        return len(text)
    if path.resolve().is_relative_to(PACKET.resolve()) or path.resolve().is_relative_to(SOURCE.resolve()):
        raise AssertionError('unexpected attempted author write: ' + str(path))
    return original_write(path, text, *args, **kwargs)


stdout = io.StringIO()
with patch.object(sys, 'argv', [str(PACKET / 'validate.py'), str(SOURCE)]), \
        patch.object(Path, 'write_text', intercepted_write), contextlib.redirect_stdout(stdout):
    runpy.run_path(str(PACKET / 'validate.py'), run_name='__main__')
replayed = json.loads(captured['validation'])
assert replayed == json.loads((PACKET / 'VALIDATION.json').read_text())
assert replayed['status'] == 'PASS'
(OUT / 'AUTHOR-REPLAY.json').write_text(captured['validation'])
record('Exact author static/synthetic replay reproduced recorded validation; package write intercepted')

# Independently exercise the whole final-head identity gate through mocked Git data.
# No commit or trigger is created, including for the positive same-tree sibling case.
gate = runpy.run_path(str(PACKET / 'check_push_head.py'), run_name='review_gate')
FINAL = 'd' * 40


def gate_case(changes=None, final=FINAL):
    data = {
        ('rev-parse', '--verify', final + '^{commit}'): final,
        ('rev-parse', HEAD + '^{tree}'): TREE,
        ('show', '-s', '--format=%P', HEAD): BASE,
        ('rev-parse', final + '^{tree}'): TREE,
        ('show', '-s', '--format=%P', final): BASE,
        ('rev-list', BASE + '..' + final): final,
        ('show', '-s', '--format=%B', final): 'Keep delayed checks specific to each harness',
    }
    data.update(changes or {})

    def fake_git(argv, **kwargs):
        assert argv[0] == 'git' and kwargs['cwd'] == SOURCE
        return (data[tuple(argv[1:])] + '\n').encode()

    with patch.object(gate['subprocess'], 'check_output', side_effect=fake_git):
        return gate['check'](SOURCE, final)


assert gate_case()['trigger_sha'] == FINAL
negative_cases = [
    {('rev-parse', HEAD + '^{tree}'): 'e' * 40},
    {('show', '-s', '--format=%P', HEAD): MAIN},
    {('rev-parse', FINAL + '^{tree}'): 'e' * 40},
    {('show', '-s', '--format=%P', FINAL): HEAD},
    {('show', '-s', '--format=%P', FINAL): BASE + ' ' + MAIN},
    {('rev-list', BASE + '..' + FINAL): FINAL + '\n' + HEAD},
]
for message in ('[skip ci]', '[ci skip]', '[no ci]', '[skip actions]', '[actions skip]',
                'subject\n\nskip-checks: true', 'subject\n\nskip-checks:true', '[SKIP CI]'):
    negative_cases.append({('show', '-s', '--format=%B', FINAL): message})
for mutation in negative_cases:
    try:
        gate_case(mutation)
    except AssertionError:
        pass
    else:
        raise AssertionError('invalid final-head identity accepted')
try:
    gate_case(final=HEAD)
except AssertionError:
    pass
else:
    raise AssertionError('candidate accepted as final sibling')
record('Independent mocked final-head gate: positive sibling and 15 invalid identity/range/skip cases')

request = json.loads((PACKET / 'CI-REQUEST.json').read_text())
assert request['old_ci']['head'] == BASE and request['old_ci']['coverage_of_new_head'] is False
assert request['future_final_head']['sha'] == 'NOT_CREATED'
assert request['authorization']['dispatch'] is False
assert set(request['deferred_to_owner_upstream_pr']) == {
    'release.yml', 'verify-std-check.yml', 'bench-pr.yml', 'extra_jobs.yml'}
assert not any(request['actions'].values())
record('Old-head evidence excluded; full push bundle and deferred PR checks retain separate owner gates')

assert snapshot() == before
assert sha(index_path.read_bytes()) == index_before
assert git(SOURCE, 'status', '--porcelain') == b''
assert git(SOURCE, 'rev-parse', 'HEAD').decode().strip() == HEAD
record('Author package/source/real index unchanged after review validation')

result = dict(status='PASS', assurance='STATIC_AND_SYNTHETIC_ONLY', reviewer='independent11',
              task_commit=TASK, package_commit=PACKAGE, source=HEAD, tree=TREE, parent=BASE,
              checks=checks, author_replay_checks=len(replayed['checks']),
              author_mocked_cases=len(replayed['mock_case_matrix']),
              independent_gate_positive_cases=1, independent_gate_rejections=len(negative_cases) + 1,
              source_index_sha256=index_before, package_sha256=before,
              author_stdout=stdout.getvalue().strip(), compiler='NOT_RUN', native_runtime='NOT_RUN',
              performance='NOT_RUN', ci='NOT_RUN', actual_future_head='NOT_CREATED', proof_credit='NONE')
(OUT / 'VALIDATION.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({k: result[k] for k in ('status', 'author_replay_checks', 'author_mocked_cases',
                                      'independent_gate_rejections', 'native_runtime')}))
