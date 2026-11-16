#!/usr/bin/env python3
"""Offline E-02 closure: Git identities, frozen payload and patch reconstruction."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile


def audit(repo, bundle):
    request = json.loads((bundle/'CI-REQUEST.json').read_text())
    control = request['control_sha']
    candidate = request['review']['candidate']
    previous = request['previous_control']
    tool = request['pins']['upstream']['sha']
    tree = request['control_tree']
    def git(*argv, **kwargs):
        return subprocess.check_output(['git','-C',str(repo),*argv], **kwargs)
    def sha(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()
    assert git('rev-parse','HEAD').decode().strip() == control
    assert git('rev-list','--parents','-n','1',control).decode().split() == [control,tool]
    assert git('rev-parse',control+'^{tree}').decode().strip() == tree
    assert git('rev-parse',candidate+'^{tree}').decode().strip() == tree
    assert '[skip ci]' in git('show','-s','--format=%B',control).decode()
    assert not git('status','--porcelain=v1').strip()
    delta = git('diff','--name-only',previous,control).decode().splitlines()
    packet = json.loads((bundle/request['review']['packet']/'metadata.json').read_text())
    assert sorted(delta) == sorted(x['path'] for x in packet['changed_files'])
    scope = git('diff','--name-only',tool,control).decode().splitlines()
    assert scope and all(x.startswith(('ch8-e-control/','.github/workflows/')) for x in scope)
    assert git('ls-tree','-r','--name-only',control,'.github/workflows').decode().splitlines() == ['.github/workflows/ch8-e.yml']
    payload = json.loads((repo/'ch8-e-control/CI-REQUEST.json').read_text())
    assert sha(repo/'ch8-e-control/CI-REQUEST.json') == request['control_request_sha256']
    assert payload['pins'] == request['pins']
    assert payload['payload_sha256'] == request['payload_sha256']
    for path, digest in request['payload_sha256'].items():
        assert sha(repo/path) == digest, path
    assert sha(repo/'ch8-e-control/rows.json') == request['rows_sha256']
    rows = json.loads((repo/'ch8-e-control/rows.json').read_text())
    assert len(rows) == 6 and sum(len(r['checks']) for r in rows) == 12
    assert all(r['checks'] == ['ON','OFF'] for r in rows)
    # The issue root is the exact original fixture; E-S positive only fixes namespace.
    prefix = 'ch8-e-control/fixtures/'
    assert git('show',previous+':'+prefix+'e_h_write_then_read.rs') == (repo/prefix/'e_h_issue_mre.rs').read_bytes()
    before = git('show',previous+':'+prefix+'e_s_unbounded_slice.rs').decode()
    assert before.replace('kani::any_slice_mut_unbounded','kani::arbitrary::any_slice_mut_unbounded') == (repo/prefix/'e_s_unbounded_slice.rs').read_text()
    for patch, base in [('control-delta.patch',previous),('CONTROL.patch',tool)]:
        assert sha(bundle/patch) == request['patches'][patch]
        with tempfile.TemporaryDirectory(prefix='ch8-e02-index-') as directory:
            env = dict(os.environ, GIT_INDEX_FILE=str(Path(directory)/'index'))
            git('read-tree',base,env=env)
            git('apply','--cached','--whitespace=error',str(bundle/patch),env=env)
            assert git('write-tree',env=env).decode().strip() == tree
    return dict(state='PASS_STATIC_ONLY',control=control,tree=tree,sole_parent=tool,
                review_candidate=candidate,same_reviewed_tree=True,
                delta_paths=delta,rows=6,invocations_per_pin=12,total_invocations=24,
                patch_reconstruction='BOTH_EXACT_TREE',mre_source='BYTE_IDENTICAL_E01',
                namespace_fix='EXACT_ONLY_POSITIVE_DELTA',qualification='ALL_NOT_RUN',
                proof_credit='NONE')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo',type=Path,required=True)
    parser.add_argument('--bundle',type=Path,default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    print(json.dumps(audit(args.repo.resolve(),args.bundle.resolve()),indent=2))
