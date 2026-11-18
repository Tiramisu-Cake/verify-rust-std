# Copyright Kani Contributors
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Read-only preflight and alternate-index patch replay; never dispatches."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def git(repo, *args, env=None):
    return subprocess.check_output(['git', '-C', str(repo), *args], env=env, text=True).strip()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replay(repo, patch):
    with tempfile.TemporaryDirectory(prefix='w11-patch-index-') as tmp:
        env = {**os.environ, 'GIT_INDEX_FILE': str(Path(tmp)/'index')}
        subprocess.run(['git', '-C', str(repo), 'read-tree', patch['base']], env=env, check=True)
        subprocess.run(['git', '-C', str(repo), 'apply', '--cached', '--check', str(HERE/patch['path'])], env=env, check=True)
        subprocess.run(['git', '-C', str(repo), 'apply', '--cached', str(HERE/patch['path'])], env=env, check=True)
        tree = git(repo, 'write-tree', env=env)
        assert tree == patch['target_tree']
        assert sha(HERE/patch['path']) == patch['sha256']
        return {**patch, 'replayed_tree': tree, 'result': 'EXACT_TREE_MATCH'}


def main():
    ids = json.loads((HERE/'IDENTITIES.json').read_text())
    control = Path(ids['control']['worktree'])
    source = Path(ids['source']['worktree'])
    tool = Path('/root/kani-upstream-ch8-s1')
    for role, repo in [('control', control), ('source', source), ('tool', tool)]:
        assert git(repo, 'rev-parse', 'HEAD') == ids[role]['sha'], role
        assert git(repo, 'rev-parse', 'HEAD^{tree}') == ids[role]['tree'], role
        assert not git(repo, 'status', '--porcelain=v1'), role
    assert git(control, 'rev-parse', 'HEAD^') == ids['control']['parent'] == '9e14e033f9ee31522b571c127609dcdff76d230b'
    baseline = Path('/root/kani-ch8-s2-diagnostics-w11')
    assert git(baseline, 'rev-parse', 'HEAD') == ids['control']['baseline']
    assert not git(baseline, 'status', '--porcelain=v1')
    assert sha(control/'ch8-s1-control/CI-REQUEST.json') == ids['control']['request_sha256']
    assert sha(control/'.github/workflows/ch8-s2.yml') == ids['control']['workflow_sha256']
    assert (HERE/'CI-REQUEST.json').read_bytes() == (control/'ch8-s1-control/CI-REQUEST.json').read_bytes()
    assert (HERE/'WORKFLOW.yml').read_bytes() == (control/'.github/workflows/ch8-s2.yml').read_bytes()
    for name in ('rustc_diagnostics.py', 'test_rustc_diagnostics.py'):
        assert (HERE/name).read_bytes() == (control/'ch8-s1-control'/name).read_bytes()
    old = json.loads(git(control, 'show', ids['control']['baseline']+':ch8-s1-control/CI-REQUEST.json'))
    request = json.loads((HERE/'CI-REQUEST.json').read_text())
    assert [k for k in old if old[k] != request[k]] == ['ci_payload_sha256']
    assert old.keys() == request.keys()
    for rel in ('ch8-s1-control/runner.py', '.github/workflows/ch8-s2.yml'):
        assert subprocess.check_output(['git', '-C', str(control), 'show', ids['control']['baseline']+':'+rel]) == (control/rel).read_bytes()
    assert len(request['rows']) == 11
    assert sum(r['required_cover_count'] for r in request['rows']) == 20
    assert sum(r['expected'] == 'DETECTED' for r in request['rows']) == 6
    for rel, digest in request['ci_payload_sha256'].items():
        assert sha(control/rel) == digest, rel
    for rel, digest in ids['source']['files'].items():
        assert sha(source/rel) == digest, rel
    changed = json.loads((HERE/'CHANGED-FILES.json').read_text())
    assert git(control, 'diff', '--name-only', ids['control']['baseline'], 'HEAD').splitlines() == changed['delta_paths']
    for item in changed['files']:
        assert sha(control/item['path']) == item['candidate_sha256']
    sys.path.insert(0, str(control/'ch8-s1-control'))
    import runner
    import cfg_pfc
    import check_package
    validated_request = runner.load_request()
    source_check = runner.verify_source(source, tool, validated_request)
    cfg = cfg_pfc.check(source, validated_request)
    assert len(cfg['rows']) == 11
    # Synthetic environment only for the existing read-only local preflight.
    os.environ.update(GITHUB_REPOSITORY='Tiramisu-Cake/kani', GITHUB_EVENT_NAME='push',
        GITHUB_REF='refs/heads/uninit-ci/ch8-s2-batch3probes-offline-diagnostics',
        GITHUB_RUN_ATTEMPT='1', GITHUB_SHA=ids['control']['sha'])
    preflight = check_package.control(control)
    patches = [replay(control, p) for p in json.loads((HERE/'PATCHES.json').read_text())]
    print(json.dumps({'state': 'PASS', 'control': ids['control'], 'source': source_check,
        'source_unchanged': True, 'baseline_worktree_untouched': True,
        'immutable_request_fields': 'UNCHANGED', 'roots': 11, 'covers': 20, 'negative_oracles': 6,
        'cfg_pfc_rows': len(cfg['rows']), 'preflight': preflight, 'patches': patches,
        'runtime_CI_retention': 'NOT_RUN', 'proof_credit': 'NONE'}, indent=2))


if __name__ == '__main__':
    main()
