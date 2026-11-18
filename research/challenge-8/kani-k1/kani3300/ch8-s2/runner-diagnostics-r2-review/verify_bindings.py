"""Offline identities/hash/alternate-index checks; no compiler or dispatch."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent / 'runner-diagnostics-r2'
G0 = Path('/root/verify-rust-std-kani3300-g0')
CONTROL = Path('/root/kani-ch8-s2-diagnostics-w11')
AUTHOR = 'ac956bdf4db98a95e2da988ccd2c527582d3d32f'
CANDIDATE = 'b678fb6cdd5edf69a4e952167422f36a45a3d6cb'
TREE = 'beb2346615ffbb7027b2f1ea8ea33a149952aa0b'
BASE = '2ecf5e839f898f6bb1cd96edd6cc6bf677acb4c8'
PARENT = '9e14e033f9ee31522b571c127609dcdff76d230b'


def git(repo, *args, env=None):
    return subprocess.check_output(['git', '-C', str(repo), *args], env=env)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    relative = PACKAGE.relative_to(G0).as_posix()
    names = git(G0, 'ls-tree', '-r', '--name-only', AUTHOR, '--', relative).decode().splitlines()
    assert len(names) == 26
    package_files = []
    for name in names:
        pinned = git(G0, 'show', AUTHOR + ':' + name)
        assert (G0 / name).read_bytes() == pinned, name
        package_files.append({'path': str(Path(name).relative_to(relative)), 'sha256': sha(pinned)})
    ids = json.loads((PACKAGE / 'IDENTITIES.json').read_text())
    for role, repo in [('control', CONTROL), ('source', Path(ids['source']['worktree'])),
                      ('tool', Path('/root/kani-upstream-ch8-s1')),
                      ('baseline', Path('/root/kani-ch8-s2-cfg-r1-w13'))]:
        expected = BASE if role == 'baseline' else ids[role]['sha']
        assert git(repo, 'rev-parse', 'HEAD').decode().strip() == expected, role
        assert not git(repo, 'status', '--porcelain=v1').strip(), role
        if role != 'baseline':
            assert git(repo, 'rev-parse', 'HEAD^{tree}').decode().strip() == ids[role]['tree']
    assert git(CONTROL, 'rev-parse', 'HEAD^').decode().strip() == PARENT
    assert ids['control']['sha'] == CANDIDATE and ids['control']['tree'] == TREE
    assert git(CONTROL, 'rev-parse', BASE+'^{tree}').decode().strip() == ids['control']['baseline_tree']
    task = G0 / 'research/challenge-8/kani-k1/TASK-CH8-S2-DIAGNOSTICS-REVIEW-W14.md'
    assert task.read_bytes() == git(G0, 'show', '90b7e5bd7f7dcecc00e7009196a466a7422f179d:'+str(task.relative_to(G0)))
    changed = json.loads((PACKAGE / 'CHANGED-FILES.json').read_text())
    delta_names = git(CONTROL, 'diff', '--name-only', BASE, CANDIDATE).decode().splitlines()
    assert delta_names == changed['delta_paths']
    for item in changed['files']:
        assert sha(git(CONTROL, 'show', CANDIDATE+':'+item['path'])) == item['candidate_sha256']
        assert sha((CONTROL/item['path']).read_bytes()) == item['candidate_sha256']
        if item['baseline_sha256'] is not None:
            assert sha(git(CONTROL, 'show', BASE+':'+item['path'])) == item['baseline_sha256']
    for packaged, control in [('CI-REQUEST.json', 'ch8-s1-control/CI-REQUEST.json'),
                              ('WORKFLOW.yml', '.github/workflows/ch8-s2.yml'),
                              ('rustc_diagnostics.py', 'ch8-s1-control/rustc_diagnostics.py'),
                              ('test_rustc_diagnostics.py', 'ch8-s1-control/test_rustc_diagnostics.py')]:
        assert (PACKAGE/packaged).read_bytes() == git(CONTROL, 'show', CANDIDATE+':'+control)
    old = json.loads(git(CONTROL, 'show', BASE+':ch8-s1-control/CI-REQUEST.json'))
    new = json.loads((PACKAGE/'CI-REQUEST.json').read_text())
    assert old.keys() == new.keys()
    fields = [k for k in old if old[k] != new[k]]
    assert fields == ['ci_changed_paths', 'ci_payload_sha256']
    assert len(new['rows']) == 11
    assert sum(r['required_cover_count'] for r in new['rows']) == 20
    assert sum(r['expected'] == 'DETECTED' for r in new['rows']) == 6
    for name, digest in new['ci_payload_sha256'].items():
        assert sha(git(CONTROL, 'show', CANDIDATE+':'+name)) == digest
    replayed = []
    for patch in json.loads((PACKAGE/'PATCHES.json').read_text()):
        data = (PACKAGE/patch['path']).read_bytes()
        assert sha(data) == patch['sha256']
        # Also verify exact committed diff bytes, independently of replay.
        assert data == git(CONTROL, 'diff', '--binary', patch['base'], CANDIDATE)
        with tempfile.TemporaryDirectory(prefix='w14-review-index-') as temporary:
            env = {**os.environ, 'GIT_INDEX_FILE': str(Path(temporary)/'index')}
            git(CONTROL, 'read-tree', patch['base'], env=env)
            git(CONTROL, 'apply', '--cached', str(PACKAGE/patch['path']), env=env)
            tree = git(CONTROL, 'write-tree', env=env).decode().strip()
            assert tree == TREE == patch['target_tree']
        replayed.append({**patch, 'replayed_tree': tree})
    for line in (PACKAGE/'MANIFEST.sha256').read_text().splitlines():
        digest, name = line.split(None, 1)
        assert sha((PACKAGE/name.strip()).read_bytes()) == digest, name
    print(json.dumps({'state': 'PASS', 'package_commit': AUTHOR, 'package_files': package_files,
        'task_file_sha256': sha(task.read_bytes()), 'control': ids['control'],
        'source': {k: ids['source'][k] for k in ('sha', 'tree')}, 'tool': ids['tool'],
        'clean_worktrees': ['control', 'source', 'tool', 'baseline'],
        'changed_files': changed['files'], 'only_changed_request_fields': fields,
        'roots': 11, 'covers': 20, 'negative_oracles': 6, 'patches': replayed,
        'scope_A_review': 'NOT_RERUN', 'proof_credit': 'NONE'}, indent=2))


if __name__ == '__main__':
    main()
