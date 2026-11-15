#!/usr/bin/env python3
"""Read-only exact rebase and batch checks; no compiler/verifier invocation."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import yaml

HERE = Path(__file__).resolve().parent
STD = Path('/root/verify-rust-std-ch8-s1-pprime-w13')
CONTROL = Path('/root/kani-ch8-s1k-pprime-w13')
BASE = 'c5ff36ff433692140605891f646043f991db05de'
OLD_STD = '75a4d1ea6eb60c63c27c1b18e662740d93bafb08'
OLD_CONTROL = '36db70978a16144624abf94d480a593dae684451'
TOOL = '0aac16ef62da9e9d5645782d458593e5d78143ba'
FIX = 'library/core/src/slice/sort/shared/smallsort/verify/sorting_entry_controls.rs'

def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])

def sha(data):
    return hashlib.sha256(data).hexdigest()

def main():
    source = git(STD, 'rev-parse', 'HEAD').decode().strip()
    source_tree = git(STD, 'rev-parse', 'HEAD^{tree}').decode().strip()
    control = git(CONTROL, 'rev-parse', 'HEAD').decode().strip()
    assert git(STD, 'rev-list', '--count', BASE+'..HEAD').strip() == b'3'
    paths = git(STD, 'diff', '--name-only', BASE, 'HEAD').decode().splitlines()
    for path in paths:
        old = git(STD, 'show', OLD_STD+':'+path)
        expected = old.replace(b'post::<u8, KeyLess<u8>>>(before, &v)',
                               b'post::<u8, KeyLess<u8>>(before, &v)') if path == FIX else old
        assert (STD/path).read_bytes() == expected, path
    assert git(CONTROL, 'rev-list', '--parents', '-n', '1', 'HEAD').decode().split() == [control, TOOL]
    assert not git(STD, 'status', '--porcelain').strip()
    assert not git(CONTROL, 'status', '--porcelain').strip()
    previous = json.loads(git(CONTROL, 'show', OLD_CONTROL+':ch8-s1-control/CI-REQUEST.json'))
    current = json.loads((CONTROL/'ch8-s1-control/CI-REQUEST.json').read_text())
    changed_keys = sorted(k for k in set(previous)|set(current) if previous.get(k) != current.get(k))
    assert changed_keys == ['changed_file_sha256', 'ci_payload_sha256', 'std_sha', 'std_tree'], changed_keys
    assert current['std_sha'] == source and current['std_tree'] == source_tree
    changed_hashes = sorted(k for k in current['changed_file_sha256']
                            if current['changed_file_sha256'][k] != previous['changed_file_sha256'][k])
    assert changed_hashes == [FIX], changed_hashes
    assert len(current['rows']) == 23 and all(r['state'] == 'NOT_RUN' for r in current['rows'])
    old_request = git(CONTROL, 'show', OLD_CONTROL+':ch8-s1-control/CI-REQUEST.json')
    new_request = (CONTROL/'ch8-s1-control/CI-REQUEST.json').read_bytes()
    def literal_rows(data):
        return data.split(b'  "rows": [', 1)[1].split(b'  "ci_payload_sha256": {', 1)[0]
    assert literal_rows(old_request) == literal_rows(new_request)
    expected_delta = ['.github/workflows/ch8-s1.yml', 'ch8-s1-control/CI-REQUEST.json', 'ch8-s1-control/runner.py']
    assert git(CONTROL, 'diff', '--name-only', OLD_CONTROL, 'HEAD').decode().splitlines() == expected_delta
    old_runner = git(CONTROL, 'show', OLD_CONTROL+':ch8-s1-control/runner.py')
    expected_runner = old_runner.replace(previous['std_sha'].encode(), source.encode()).replace(previous['std_tree'].encode(), source_tree.encode())
    assert (CONTROL/'ch8-s1-control/runner.py').read_bytes() == expected_runner
    workflow = CONTROL/'.github/workflows/ch8-s1.yml'
    old_workflow = git(CONTROL, 'show', OLD_CONTROL+':.github/workflows/ch8-s1.yml')
    expected_workflow = old_workflow.replace(b'          path: ${{ env.RECEIPT_ROOT }}/\n', b'          path: |\n            ${{ env.RECEIPT_ROOT }}/\n            !${{ env.RECEIPT_ROOT }}/**/target/**\n')
    assert workflow.read_bytes() == expected_workflow
    upload = yaml.load(workflow.read_text(), Loader=yaml.BaseLoader)['jobs']['s1']['steps'][-1]
    assert upload['with']['path'].splitlines() == ['${{ env.RECEIPT_ROOT }}/', '!${{ env.RECEIPT_ROOT }}/**/target/**']
    for rel, digest in current['ci_payload_sha256'].items():
        assert sha((CONTROL/rel).read_bytes()) == digest, rel
    for rel, digest in current['changed_file_sha256'].items():
        assert sha((STD/rel).read_bytes()) == digest, rel
    # Apply only the tiny activation source patches to isolated initialized files.
    for variant in current['variants'].values():
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for rel in variant['changed_file_sha256']:
                dst = root/rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes((STD/rel).read_bytes())
            patch = CONTROL/'ch8-s1-control'/variant['patch']
            assert sha(patch.read_bytes()) == variant['sha256']
            subprocess.run(['git', 'apply', str(patch)], cwd=root, check=True)
            for rel, digest in variant['changed_file_sha256'].items():
                assert sha((root/rel).read_bytes()) == digest
    for repo, base in [(STD, BASE), (CONTROL, TOOL)]:
        subprocess.run(['git', '-C', str(repo), 'diff', '--check', base, 'HEAD'], check=True)
    env = {**os.environ, 'PYTHONDONTWRITEBYTECODE':'1', 'GITHUB_REPOSITORY':'Tiramisu-Cake/kani',
           'GITHUB_EVENT_NAME':'push', 'GITHUB_REF':'refs/heads/uninit-ci/ch8-s1k-pprime-w13',
           'GITHUB_RUN_ATTEMPT':'1', 'GITHUB_SHA':control}
    subprocess.run(['python3', str(CONTROL/'ch8-s1-control/check_package.py'), 'control', '--repo', str(CONTROL)], env=env, check=True, stdout=subprocess.PIPE)
    result = {'state':'PASS_STATIC_ONLY', 'source_sha':source, 'source_tree':source_tree,
              'control_sha':control, 'control_tree':git(CONTROL,'rev-parse','HEAD^{tree}').decode().strip(),
              'changed_request_keys':changed_keys, 'changed_source_hashes':changed_hashes,
              'literal_rows_byte_equal':True, 'row_count':23,
              'literal_rows_sha256':sha(literal_rows(new_request)),
              'runner_delta':'STD_SHA_AND_STD_TREE_ONLY', 'upload_delta':'EXCLUDE_ALL_TARGET_SUBTREES',
              'variants':'PATCHES_AND_RESULT_HASHES_PASS', 'control_identity':'PASS',
              'proof_status':'NOT_RUN', 'proof_credit':'NONE'}
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
