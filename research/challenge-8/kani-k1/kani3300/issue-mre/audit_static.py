#!/usr/bin/env python3
"""Audit the prepared control, its patch, and candidate source reductions."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

HERE=Path(__file__).resolve().parent
G0=HERE.parents[0]
UP='0aac16ef62da9e9d5645782d458593e5d78143ba'
CONTROL=Path('/root/kani-ch8-issue-mre-w14')

def git(*args,env=None):
    return subprocess.check_output(['git','-C',str(CONTROL),*args],env=env,text=True).strip()

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def audit():
    req=json.loads((HERE/'CI-REQUEST.json').read_text())
    review=json.loads((HERE/'REVIEW.json').read_text())
    assert review['state']=='GO_STATIC_REVIEW_ONLY'
    assert review['candidate_commit']==req['control_sha'] and review['candidate_tree']==req['control_tree']
    assert review['qualification']=='ALL_NOT_RUN' and review['proof_credit']=='NONE'
    assert sha(HERE/'REVIEW.json')==req['review']['sha256']
    assert git('rev-parse','HEAD')==req['control_sha']
    assert git('rev-parse','HEAD^{tree}')==req['control_tree']
    assert git('show','-s','--format=%P','HEAD')==UP
    assert git('show','-s','--format=%an <%ae>','HEAD')=='Tiramisu-Cake <igkharin@gmail.com>'
    assert '[skip ci]' in git('show','-s','--format=%s','HEAD')
    assert not git('status','--porcelain=v1')
    changed=git('diff','--name-only',UP,'HEAD').splitlines()
    assert all(p.startswith(('.github/workflows/','ch8-issue-mre-control/')) for p in changed)
    assert git('ls-tree','--name-only','HEAD:.github/workflows')=='ch8-issue-mre.yml'
    assert sha(HERE/'CONTROL.patch')==req['patch_sha256']
    with tempfile.TemporaryDirectory() as d:
        env=dict(os.environ,GIT_INDEX_FILE=str(Path(d)/'index'))
        git('read-tree',UP,env=env)
        git('apply','--cached',str(HERE/'CONTROL.patch'),env=env)
        assert git('write-tree',env=env)==req['control_tree']
    fx=CONTROL/'ch8-issue-mre-control/fixtures'
    drafts={
        'copy':G0/'ch8-b/pprime-batch/run-43788110361/ISSUE-DRAFT.md',
        'slice':G0/'ch8-profiles/on-ci/gaps/ISSUE-DRAFT-B.md',
        'slice_source':G0/'ch8-profiles/on-ci/gaps/MRE-B-slice-havoc.rs'}
    assert {k:sha(v) for k,v in drafts.items()}==req['input_sha256']
    assert (fx/'slice_uninit.rs').read_bytes()==drafts['slice_source'].read_bytes()
    blocks=re.findall(r'```rust\n(.*?)```',drafts['copy'].read_text(),re.S)
    license='// Copyright Kani Contributors\n// SPDX-License-Identifier: Apache-2.0 OR MIT\n'
    assert (fx/'copy_integer.rs').read_text()==license+blocks[0]
    b=blocks[1]; second=b.index('// Paired invalid-value')
    assert (fx/'raw_bool_overwrite.rs').read_text()==license+b[b.index('#[kani::proof]'):second].rstrip()+'\n'
    assert (fx/'raw_bool_read.rs').read_text()==license+b[b.index('#[kani::proof]',second):].rstrip()+'\n'
    return dict(status='PASS',control=req['control_sha'],tree=req['control_tree'],sole_parent=UP,
                patch_reconstruction='PASS',drafts_unchanged=True,copy_mres='EXACT_RUST_BLOCKS',slice_mre='BYTE_EXACT',
                runtime='ALL_NOT_RUN',proof_credit='NONE')

if __name__=='__main__': print(json.dumps(audit(),indent=2))
