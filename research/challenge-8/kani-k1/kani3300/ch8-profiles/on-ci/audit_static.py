#!/usr/bin/env python3
"""Git/Python-only package audit. Never builds, runs or downloads proof evidence."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

OLD = '112fcc9ada67ee2bb8e1712d47983d6717487b78'
TOOL = '14bc57fdb99960240c4944845a3d985c8af4dcf7'
TOOL_TREE = '1efb6e4dfa69d346df8e23741d11839b1932403d'
SOURCE = '9fa2f7f97760584f38738909625c064006d8a936'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def audit(repo, old_repo, source):
    def git(root, *args):
        return subprocess.check_output(['git', '-C', str(root), *args])
    candidate = git(repo, 'rev-parse', 'HEAD').decode().strip()
    assert git(repo, 'rev-list', '--parents', '-n', '1', 'HEAD').decode().split() == [candidate, TOOL]
    assert git(repo, 'rev-parse', TOOL+'^{tree}').decode().strip() == TOOL_TREE
    assert not git(repo, 'status', '--porcelain=v1').strip()
    request = json.loads((repo/'ch8-prof-on-control/CI-REQUEST.json').read_bytes())
    old_request = json.loads(git(old_repo, 'show', OLD+':ch8-prof-off-control/CI-REQUEST.json'))
    changed = git(repo, 'diff', '--name-only', TOOL, 'HEAD').decode().splitlines()
    assert changed == request['ci_changed_paths']
    assert all(p.startswith(('ch8-prof-on-control/', '.github/workflows/')) for p in changed)
    assert git(repo, 'ls-tree', '-r', '--name-only', 'HEAD', '.github/workflows').decode().splitlines() == ['.github/workflows/ch8-prof-on.yml']
    for rel, digest in request['ci_payload_sha256'].items():
        assert sha((repo/rel).read_bytes()) == digest, rel
    payload = set(request['ci_payload_sha256'])
    assert payload == {p for p in changed if (repo/p).is_file() and not p.endswith('CI-REQUEST.json')}
    for key in ('std_repository', 'std_sha', 'std_tree', 'caps', 'dispatch_cap', 'dispatches',
                'rows', 'changed_file_sha256', 'variants', 'budgets', 'source_request_sha256',
                'source_review_sha256', 'manifest_sha256', 'batching'):
        assert request[key] == old_request[key], key
    manifest = (repo/'ch8-prof-on-control/manifest.json').read_bytes()
    assert manifest == git(old_repo, 'show', OLD+':ch8-prof-off-control/manifest.json')
    assert sha(manifest) == request['manifest_sha256']
    assert len(request['rows']) == 62
    assert request['on_flags'] == {**old_request['off_flags'], 'uninit': True}
    argv = request['on_argv'].copy()
    pos = argv.index('uninit-checks')
    assert argv[pos-1] == '-Z'
    del argv[pos-1:pos+1]
    assert argv == old_request['off_argv']
    # Mechanical renaming leaves the mature execution and error paths intact.
    for name in ('workflow_repo.py', 'test_batch.py', 'test_runner.py', 'test_workflow_repo.py'):
        before = git(old_repo, 'show', OLD+':ch8-prof-off-control/'+name).decode()
        if name == 'test_runner.py':
            before = before.replace('set(runner.UNSTABLE) | {"export-json"}',
                                    'set(runner.UNSTABLE) | {"export-json", "unstable-options"}')
        assert (repo/'ch8-prof-on-control'/name).read_text() == before.replace('ch8-prof-off', 'ch8-prof-on')
    assert git(source, 'rev-parse', SOURCE+'^{tree}').decode().strip() == request['std_tree']
    for path, digest in request['changed_file_sha256'].items():
        assert sha(git(source, 'show', SOURCE+':'+path)) == digest
    assert 'nightly-2026-10-23' in git(repo, 'show', TOOL+':rust-toolchain.toml').decode()
    g0 = Path(__file__).resolve().parent
    # Locate by source directory rather than depending on worktree's HEAD.
    while not (g0/'research').is_dir():
        assert g0.parent != g0
        g0 = g0.parent
    for path, digest in request['classification']['sources_sha256'].items():
        assert sha((g0/path).read_bytes()) == digest, path
    compat = json.loads((Path(__file__).parent/'TOOL-CLASSIFIER-COMPAT.json').read_bytes())
    for path, record in compat['files'].items():
        data = git(repo, 'show', TOOL+':'+path)
        assert sha(data) == record['sel1_sha256'] == record['stock_sha256']
        assert data == git(old_repo, 'show', '0aac16ef62da9e9d5645782d458593e5d78143ba:'+path)
    sys.path.insert(0, str(repo/'ch8-prof-on-control'))
    spec = importlib.util.spec_from_file_location('on_check_package', repo/'ch8-prof-on-control/check_package.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    yaml_result = module.check_yaml(repo/'.github/workflows/ch8-prof-on.yml')
    return {'state': 'PASS_STATIC_ONLY', 'control': candidate,
            'control_tree': git(repo, 'rev-parse', 'HEAD^{tree}').decode().strip(),
            'control_parent': TOOL, 'source': SOURCE,
            'baseline_control': OLD, 'manifest_rows': 62, 'manifest_sha256': sha(manifest),
            'row_oracle_cfg_bounds_caps_budgets': 'IDENTICAL_TO_OFF',
            'classification_source_chain_files_identical': len(compat['files']),
            'yaml': yaml_result, 'qualification': 'NOT_RUN', 'proof_credit': 'NONE'}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    for name in ('repo', 'old-repo', 'source'):
        p.add_argument('--'+name, type=Path, required=True)
    args = p.parse_args()
    print(json.dumps(audit(args.repo.resolve(), args.old_repo.resolve(), args.source.resolve()), indent=2))
