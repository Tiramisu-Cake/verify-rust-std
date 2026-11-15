#!/usr/bin/env python3
"""Offline SEL1-C2 replay YAML/context/path and nested-binding qualification."""
import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

import yaml

HERE = Path(__file__).resolve().parent
# Reuse the same duplicate-key/YAML1.2 loader and context scanner qualified for A.
spec = importlib.util.spec_from_file_location('gatea_checks', HERE.parent / 'gatea/check_workflow.py')
gatea = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gatea)
SOURCE = '14bc57fdb99960240c4944845a3d985c8af4dcf7'
TREE = '1efb6e4dfa69d346df8e23741d11839b1932403d'
REPO = Path('/root/kani-fix-3300-sel1-c2-w15')
STD = Path('/root/verify-rust-std-kani3300-sel1-swap')
WORKFLOW = '.github/workflows/kani3300-replay.yml'
ROWS = ['merge-raw-closure-on', 'merge-profile-closure-on', 'sort4-closure-on',
        'swap-if-less-closure-on', 'raw-legal-on', 'raw-negative-on']


def validate(doc):
    assert set(doc) <= {'name', 'on', 'permissions', 'concurrency', 'env', 'jobs'}
    assert doc['on'] == {'push': {'branches': ['uninit-ci/sel1-c2-replay-*']}}
    assert doc['permissions'] == {'contents': 'read'}
    assert doc['concurrency'] == {'group': 'kani3300-sel1-c2-replay', 'cancel-in-progress': False}
    gatea.check_contexts(doc.get('env', {}), {'github', 'vars', 'secrets', 'inputs'})
    assert set(doc['jobs']) == {'replay'}
    job = doc['jobs']['replay']
    assert job['if'] == "${{ github.repository == 'Tiramisu-Cake/kani' }}"
    assert job['runs-on'] == 'ubuntu-24.04' and job['timeout-minutes'] == 60
    assert job['strategy'] == {'fail-fast': False, 'max-parallel': 1, 'matrix': {'root': ROWS}}
    gatea.check_contexts(job['if'], {'github', 'needs', 'vars', 'inputs'})
    gatea.check_contexts(job.get('env', {}), {'github', 'needs', 'strategy', 'matrix', 'vars', 'secrets', 'inputs'})
    ids = {s['id'] for s in job['steps'] if 'id' in s}
    assert len(ids) == sum('id' in s for s in job['steps'])
    for step in job['steps']:
        assert ('uses' in step) != ('run' in step)
        assert set(step) <= {'name', 'id', 'uses', 'with', 'env', 'if', 'run', 'working-directory', 'shell'}
        contexts = {'github', 'needs', 'strategy', 'matrix', 'vars', 'secrets', 'inputs', 'env', 'steps', 'job'}
        gatea.check_contexts({k: v for k, v in step.items() if k != 'env'}, contexts)
        gatea.check_contexts(step.get('env', {}), contexts | {'runner'})
        for ident in re.findall(r'steps\.([\w-]+)\.', json.dumps(step)):
            assert ident in ids, ('unknown step', ident)
        if step.get('uses', '').startswith('actions/checkout@'):
            assert step['with']['fetch-depth'] >= 2
            assert step['with']['persist-credentials'] is False
        if 'run' in step:
            shell = re.sub(r'\$\{\{.*?\}\}', 'STATIC', step['run'], flags=re.S)
            subprocess.run(['bash', '-n'], input=shell.encode(), check=True, capture_output=True)
            for python in re.findall(r"python3 - <<'PY'\n(.*?)\nPY", shell, re.S):
                ast.parse(python)
    steps = job['steps']
    named = {s['name']: s for s in steps}
    checkout = [s for s in steps if s.get('uses', '').startswith('actions/checkout@')]
    assert len(checkout) == 2
    assert checkout[0]['with']['path'] == 'control' and checkout[0]['with']['ref'] == '${{ github.sha }}'
    assert checkout[1]['with']['path'] == 'export' and checkout[1]['with']['ref'] == '${{ steps.export.outputs.sha }}'
    attempt = named['Require single attempt and exact control head']
    assert attempt['working-directory'] == 'control'
    assert 'os.environ["GITHUB_RUN_ATTEMPT"] == "1"' in attempt['run']
    assert 'head == os.environ["GITHUB_SHA"]' in attempt['run']
    assert named['Python-only wrapper preflight']['working-directory'] == 'control/scripts/kani3300-replay'
    read = named['Read exact export revision']['run']
    assert "control/scripts/kani3300-replay/CI-REQUEST.json" in read and "req['tool_export_sha']" in read
    assert named['Verify immutable SEL1-C2 source bindings']['run'] == 'python3 control/scripts/kani3300-replay/replay.py verify-source --repo export'
    setup = named['Setup pinned Kani dependencies']
    assert setup['uses'] == './export/.github/actions/setup' and setup['with'] == {'os': 'ubuntu-24.04', 'kani_dir': 'export'}
    build = named['Build this exact SEL1-C2 checkout']
    assert build['working-directory'] == 'export' and build['run'] == 'cargo build-dev -- --release'
    prepare = named['Prepare isolated selected std snapshot']
    assert '--destination "$RUNNER_TEMP/kani3300-std"' in prepare['run']
    execute = named['Execute one exact replay row']
    assert '--repo "$GITHUB_WORKSPACE/export"' in execute['run']
    assert '--std "$RUNNER_TEMP/kani3300-std"' in execute['run']
    assert '--binary "$GITHUB_WORKSPACE/export/scripts/kani"' in execute['run']
    assert '--out "$RUNNER_TEMP/kani3300-receipt/${{ matrix.root }}"' in execute['run']
    for step in (prepare, execute):
        assert step.get('working-directory', '.') == '.'
        assert step['run'].startswith('python3 control/scripts/kani3300-replay/replay.py ')
    fallback = named['Materialize NOT_RUN fallback receipt']
    assert fallback['if'] == 'always()' and 'if not receipt.exists():' in fallback['run']
    upload = named['Upload bounded receipts and retained failure artifacts']
    assert upload['if'] == 'always()'
    assert upload['env']['RECEIPT_ROOT'] == '${{ runner.temp }}/kani3300-receipt'
    assert upload['with']['path'] == '${{ env.RECEIPT_ROOT }}/${{ matrix.root }}/'
    assert upload['with']['if-no-files-found'] == 'error' and upload['with']['retention-days'] == 7


def main():
    def git(repo, *argv):
        return subprocess.check_output(['git', '-C', str(repo), *argv])
    full = HERE / 'full-export'
    for path in full.rglob('*'):
        if path.is_file():
            assert path.read_bytes() == (REPO / path.relative_to(full)).read_bytes(), str(path)
    assert list((REPO / '.github/workflows').iterdir()) == [REPO / WORKFLOW]
    doc = yaml.load((full / WORKFLOW).read_text(), Loader=gatea.Loader)
    validate(doc)
    scripts = full / 'scripts/kani3300-replay'
    sys.path.insert(0, str(scripts))
    import replay
    req = replay.load_request()
    assert (replay.SEL1_C2_SHA, replay.SEL1_C2_TREE) == (SOURCE, TREE)
    assert (HERE / 'CI-REQUEST.json').read_bytes() == replay.REQUEST.read_bytes()
    assert [r['id'] for r in req['roots']] == ROWS
    assert [r['source_unwind'] for r in req['roots']] == [34, 34, 16, 8, 16, 16]
    assert [r['required_covers'] for r in req['roots']] == [5, 2, 3, 6, 2, None]
    for row in req['roots']:
        argv = row['argv']
        assert argv[0] == '<EXACT_SEL1_C2_KANI_BINARY>' and argv[1:5] == ['verify-std', '-Z', 'unstable-options', './library']
        assert argv[argv.index('--harness') + 1] == row['selector'] and '--exact' in argv
        assert argv[argv.index('--jobs') + 1] == '1'
        assert argv[argv.index('--harness-timeout') + 1] == '2400s'
        assert argv[-3:] == ['--cbmc-args', '--object-bits', '12']
        assert '--no-assert-contracts' in argv and 'uninit-checks' in argv
        assert not any('valid-value' in x or 'disable' in x or 'arrays-uf' in x for x in argv)
        assert row['environment'] == {'NO_COLOR': '1', 'RUSTFLAGS': '--cfg kani_smallsort_controls'}
    binding = json.loads(replay.SOURCE_BINDING.read_text())
    assert binding['state'] == 'SEL1_C2_FROZEN'
    assert (binding['export_sha'], binding['export_tree']) == (SOURCE, TREE)
    assert git(REPO, 'rev-parse', SOURCE + '^{tree}').decode().strip() == TREE
    for path, digest in binding['files'].items():
        assert hashlib.sha256(git(REPO, 'show', SOURCE + ':' + path)).hexdigest() == digest, path
    for path, oid in binding['subtrees'].items():
        assert git(REPO, 'rev-parse', SOURCE + ':' + path).decode().strip() == oid, path
    actual_tests = set(git(REPO, 'ls-tree', '-r', '--name-only', SOURCE, '--', 'tests/expected/uninit', 'tests/json-handler').decode().splitlines())
    listed_tests = {p for p in binding['files'] if p.startswith(('tests/expected/uninit/', 'tests/json-handler/'))}
    assert listed_tests == actual_tests and len(actual_tests) == 548
    assert set(git(REPO, 'diff', '--name-only', '8e299aa624', SOURCE).decode().splitlines()) <= set(binding['files'])
    assert git(STD, 'rev-parse', replay.STD_SHA + '^{tree}').decode().strip() == replay.STD_COMMIT_TREE
    assert git(STD, 'rev-parse', req['test_overlay_commit'] + ':library').decode().strip() == req['test_only_library_tree']
    patch = git(STD, 'diff', '--binary', replay.STD_SHA, req['test_overlay_commit'], '--', 'library')
    assert patch == replay.PATCH.read_bytes()
    for path, digest in req['patched_file_sha256'].items():
        assert hashlib.sha256(git(STD, 'show', req['test_overlay_commit'] + ':' + path)).hexdigest() == digest
    manifest = json.loads((scripts / 'REPLAY-CI-OVERLAY.json').read_text())
    for path, digest in manifest['files_sha256'].items():
        assert hashlib.sha256((full / path).read_bytes()).hexdigest() == digest, path
    assert manifest['request_sha256'] == replay.REQUEST_SHA
    changed = git(REPO, 'diff', '--name-only', SOURCE).decode().splitlines()
    assert all(p.startswith(('.github/workflows/', 'scripts/kani3300-replay/')) for p in changed)
    rejected = []
    mutations = [
        ('dispatch-only', lambda d: d.update(on={'workflow_dispatch': None})),
        ('runner-job-env', lambda d: d['jobs']['replay'].update(env={'BAD': '${{ runner.temp }}'})),
        ('shallow-export', lambda d: next(s for s in d['jobs']['replay']['steps'] if s.get('name') == 'Checkout exact frozen SEL1-C2 export')['with'].update({'fetch-depth': 1})),
        ('nested-export', lambda d: next(s for s in d['jobs']['replay']['steps'] if s.get('name') == 'Checkout exact frozen SEL1-C2 export')['with'].update(path='control/export')),
    ]
    for label, mutate in mutations:
        bad = copy.deepcopy(doc)
        mutate(bad)
        try:
            validate(bad)
        except AssertionError:
            rejected.append(label)
        else:
            raise AssertionError(('known-error mutation accepted', label))
    print(json.dumps({'status': 'PASS', 'source_files': len(binding['files']),
                      'source_subtrees': len(binding['subtrees']), 'rediscovered_tests': len(actual_tests),
                      'unique_rows': 6, 'std_patch_and_five_files': 'EXACT_IMMUTABLE_OBJECTS',
                      'known_error_mutations_rejected': rejected,
                      'limitation': 'offline targeted checker; no native build, runtime proof or full actionlint'}, indent=2))


if __name__ == '__main__':
    main()
