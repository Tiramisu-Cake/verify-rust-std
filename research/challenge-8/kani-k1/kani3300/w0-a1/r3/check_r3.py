#!/usr/bin/env python3
"""Offline R3 identity, workflow and patch checks. No Rust or verifier execution."""
import ast
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import yaml

CI = Path('/root/kani-fix-ch8-w0-a1-r3-w15')
STD = Path('/root/verify-rust-std-ch8-w0-a1-r3-w15')
BASE = CI / 'scripts/ch8-w0-a1'
OLD = 'bf81a1f14f9468c5b25d3ee33f7dafbf2bca131e'
SOURCE = '14bc57fdb99960240c4944845a3d985c8af4dcf7'
ROWS = ['stable_freeze_u64_n32', 'unstable_general_nocopy_u64_n32',
        'unstable_network_u64_n32', 'stable_freeze_u64_n8', 'stable_freeze_u64_n16',
        'unstable_general_nocopy_u64_n8', 'unstable_general_nocopy_u64_n16',
        'unstable_network_u64_n18']


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])


def digest(b):
    return hashlib.sha256(b).hexdigest()


class Loader(yaml.SafeLoader):
    pass


def mapping(loader, node):
    out = {}
    for key, val in node.value:
        key = loader.construct_object(key)
        assert key not in out, f'duplicate YAML key {key}'
        out[key] = loader.construct_object(val)
    return out


Loader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)


def workflow(doc):
    assert doc['on'] == {'push': {'branches': ['uninit-ci/ch8-w0-a1-r3-*']}}
    assert doc['permissions'] == {'contents': 'read'}
    assert doc['concurrency'] == {'group': 'ch8-w0-a1', 'cancel-in-progress': False}
    assert set(doc['jobs']) == {'r1', 'r2'}
    for name, job in doc['jobs'].items():
        assert job['if'] == "${{ github.repository == 'Tiramisu-Cake/kani' && startsWith(github.ref, 'refs/heads/uninit-ci/ch8-w0-a1-r3-') }}"
        assert job['runs-on'] == 'ubuntu-24.04'
        assert job['timeout-minutes'] == (130 if name == 'r1' else 50)
        if name == 'r1':
            assert 'strategy' not in job, 'R1 must share one job for fail-fast state'
            assert 'matrix.' not in json.dumps(job)
        else:
            assert job['strategy'] == {'fail-fast': False, 'max-parallel': 1,
                                       'matrix': {'pin': ['baseline', 'sel1']}}
        steps = {s['name']: s for s in job['steps']}
        checkout = [s for s in job['steps'] if s.get('uses', '').startswith('actions/checkout@')]
        assert [s['with'] for s in checkout] == [
            {'ref': '${{ github.sha }}', 'path': 'control', 'fetch-depth': 2, 'persist-credentials': False},
            {'ref': '${{ steps.pin.outputs.sha }}', 'path': 'export', 'fetch-depth': 2, 'persist-credentials': False}]
        guard = steps['Require first attempt and same-tree trigger']['run']
        assert "os.environ['GITHUB_RUN_ATTEMPT'] == '1'" in guard
        assert "head == os.environ['GITHUB_SHA']" in guard
        assert 'HEAD^1^{tree}' in guard and "'HEAD^'" in guard and '[skip ci]' in guard
        assert steps['Setup this pin dependencies']['uses'] == './export/.github/actions/setup'
        assert steps['Setup this pin dependencies']['with']['kani_dir'] == 'export'
        assert steps['Build exact export']['working-directory'] == 'export'
        run = steps['Run exact cases once']['run']
        if name == 'r1':
            assert 'run-r1-sequence' in run and '<= 2340' in run
            assert '--std "$RUNNER_TEMP/ch8-a1-std"' in run
            assert '--binary "$GITHUB_WORKSPACE/export/scripts/kani"' in run
            assert '--out "$RUNNER_TEMP/ch8-a1-receipt"' in run
        else:
            assert "req['r3']['native_row_ids']" in run and '<= 1140' in run
            assert "'--stage', 'r2'" in run
        for stepname in ['Fallback NOT_RUN receipts', 'Bound receipt upload', 'Upload bounded receipts']:
            assert steps[stepname]['if'] == 'always()'
        upload = steps['Upload bounded receipts']
        assert '!${{ env.RECEIPT_ROOT }}/**/target/**' in upload['with']['path']
        assert upload['with']['retention-days'] == 7
        assert upload['with']['if-no-files-found'] == 'error'
        for step in job['steps']:
            if 'run' not in step:
                continue
            shell = re.sub(r'\$\{\{.*?\}\}', 'STATIC', step['run'], flags=re.S)
            subprocess.run(['bash', '-n'], input=shell.encode(), check=True, capture_output=True)
            for code in re.findall(r"python3 - <<'PYCODE'\n(.*?)\nPYCODE", shell, re.S):
                ast.parse(code)


def main():
    doc = yaml.load((CI / '.github/workflows/ch8-w0-a1.yml').read_text(), Loader=Loader)
    workflow(doc)
    mutations = []
    for label, mutate in [
        ('dispatch', lambda x: x.update({'on': {'workflow_dispatch': None}})),
        ('matrix-breaks-failfast', lambda x: x['jobs']['r1'].update(strategy={'matrix': {'root': ROWS}})),
        ('wrong-binary', lambda x: x['jobs']['r1']['steps'][9].update(run=x['jobs']['r1']['steps'][9]['run'].replace('$GITHUB_WORKSPACE/export/scripts/kani', '$GITHUB_WORKSPACE/control/export/scripts/kani'))),
        ('unexcluded-target', lambda x: x['jobs']['r1']['steps'][-1]['with'].update(path='${{ env.RECEIPT_ROOT }}/')),
    ]:
        bad = copy.deepcopy(doc); mutate(bad)
        try:
            workflow(bad)
        except AssertionError:
            mutations.append(label)
        else:
            raise AssertionError(f'accepted {label}')
    sys.path.insert(0, str(BASE))
    import a1
    req = a1.load_request()
    old = json.loads(git(CI, 'show', OLD + ':scripts/ch8-w0-a1/CI-REQUEST.json'))
    assert req['pins'] == old['pins']
    assert req['r1']['rows'] == old['r1']['rows'], 'proof flags, controls and N32 order unchanged'
    assert [r['id'] for r in req['r1']['rows']] == ROWS
    for row, before in zip(req['r2']['rows'], old['r2']['rows']):
        expected = copy.deepcopy(before)
        if '5151' in expected['id']:
            expected['environment']['RUSTFLAGS'] = '--edition=2021'
        assert row == expected
        assert digest((BASE / row['fixture']).read_bytes()) == row['fixture_sha256']
    assert req['r3']['native_row_ids'] == [r['id'] for r in req['r2']['rows'] if '5151' in r['id']]
    assert req['r3']['maximum_runner_minutes'] == 130 + 2 * 50
    assert digest((BASE / req['std']['patch']).read_bytes()) == req['std']['patch_sha256']
    assert git(STD, 'rev-parse', 'HEAD').decode().strip() == req['std']['package_sha']
    assert git(STD, 'rev-parse', 'HEAD^{tree}').decode().strip() == req['std']['package_tree']
    assert git(STD, 'rev-parse', 'HEAD:library').decode().strip() == req['std']['package_library_tree']
    for path, sha in req['std']['patched_files'].items():
        assert digest(git(STD, 'show', 'HEAD:' + path)) == sha
    assert git(STD, 'diff', '--name-only', 'HEAD^', 'HEAD').decode().splitlines() == [
        'library/core/src/slice/sort/shared/smallsort/verify/wave0_a1.rs']
    source_path = 'library/core/src/slice/sort/shared/smallsort/verify/wave0_a1.rs'
    before = git(STD, 'show', 'HEAD^:' + source_path)
    assert before.replace(b'use super::{StableSmallSortTypeImpl, UnstableSmallSortTypeImpl};',
                          b'use super::super::{StableSmallSortTypeImpl, UnstableSmallSortTypeImpl};') == git(STD, 'show', 'HEAD:' + source_path)
    patch = git(STD, 'diff', '--binary', req['std']['base_sha'], 'HEAD', '--', 'library')
    assert patch == (BASE / 'std-test-only.patch').read_bytes()
    with tempfile.TemporaryDirectory(prefix='a1-r3-static-index-') as td:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(td) / 'index'))
        def index_git(*args):
            return subprocess.check_output(['git', '-C', str(STD), *args], env=env)
        index_git('read-tree', req['std']['base_sha'])
        index_git('apply', '--cached', '--check', str(BASE / 'std-test-only.patch'))
        index_git('apply', '--cached', str(BASE / 'std-test-only.patch'))
        result_tree = index_git('write-tree').decode().strip()
        assert git(STD, 'rev-parse', result_tree + ':library').decode().strip() == req['std']['package_library_tree']
    changed = git(CI, 'diff', '--name-only', SOURCE).decode().splitlines()
    assert all(p.startswith(('.github/workflows/', 'scripts/ch8-w0-a1/')) for p in changed)
    git(CI, 'diff', '--check'); git(STD, 'diff', '--check')
    print(json.dumps({'status': 'PASS_STATIC_ONLY', 'workflow_mutations_rejected': mutations,
                      'std_package': req['std']['package_sha'], 'rows': {'r1': 8, 'r3_native_per_pin': 2},
                      'proof_profile_unchanged': True, 'runtime': 'NOT_RUN'}, indent=2))


if __name__ == '__main__':
    main()
