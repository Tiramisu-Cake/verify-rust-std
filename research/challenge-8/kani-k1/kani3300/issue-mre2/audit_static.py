#!/usr/bin/env python3
"""Offline frozen-candidate, source immutability and patch reconstruction audit."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
CONTROL = Path('/root/kani-ch8-issue-mre2-w14')
UPSTREAM = '0aac16ef62da9e9d5645782d458593e5d78143ba'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args, env=None):
    return subprocess.check_output(['git','-C',str(CONTROL),*args],text=True,env=env).strip()

def audit():
    req = json.loads((HERE/'CI-REQUEST.json').read_text())
    assert req['control_sha'] == git('rev-parse','HEAD')
    assert req['control_tree'] == git('rev-parse','HEAD^{tree}')
    assert git('show','-s','--format=%P','HEAD') == UPSTREAM
    assert git('show','-s','--format=%an <%ae>','HEAD') == 'Tiramisu-Cake <igkharin@gmail.com>'
    assert '[skip ci]' in git('show','-s','--format=%s','HEAD')
    assert not git('status','--porcelain=v1')
    assert all(p.startswith(('.github/workflows/','ch8-issue-mre2-control/'))
               for p in git('diff','--name-only',UPSTREAM,'HEAD').splitlines())
    assert git('ls-tree','--name-only','HEAD:.github/workflows') == 'ch8-issue-mre2.yml'
    assert sha(HERE/'CONTROL.patch') == req['patch_sha256']
    with tempfile.TemporaryDirectory() as d:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(d)/'index'))
        git('read-tree', UPSTREAM, env=env)
        git('apply','--cached',str(HERE/'CONTROL.patch'), env=env)
        assert git('write-tree', env=env) == req['control_tree']
    inputs = json.loads((HERE/'INPUTS.json').read_text())
    for record in inputs['inputs'].values():
        assert sha(Path(record['path'])) == record['sha256']
    old = json.loads((HERE.parent/'issue-mre/CI-REQUEST.json').read_text())['input_sha256']
    assert inputs['inputs']['original_slice_source']['sha256'] == old['slice_source']
    assert inputs['inputs']['slice_issue_text']['sha256'] == old['slice']
    assert inputs['inputs']['copy_issue_text']['sha256'] == old['copy']
    source = HERE.parent/'ch8-profiles/on-ci/gaps/MRE-B-slice-havoc-v2.rs'
    assert source.read_bytes() == (CONTROL/'ch8-issue-mre2-control/fixtures/slice_uninit.rs').read_bytes()
    assert sha(source) == req['v2_source_sha256']
    for key in ('review', 'validation'):
        assert sha(HERE/req[key]['path']) == req[key]['sha256']
    assert req['review']['state'] == 'GO_STATIC_REVIEW_ONLY'
    assert req['review']['candidate'] == req['control_sha']
    assert sha(CONTROL/'ch8-issue-mre2-control/CI-REQUEST.json') == req['control_request_sha256']
    return {'status':'PASS','assurance':'STATIC_GIT_AND_SOURCE_ONLY',
            'control':req['control_sha'],'tree':req['control_tree'],'sole_parent':UPSTREAM,
            'patch_reconstruction':'PASS','v1_and_issue_texts_unchanged':True,
            'v2_source':'BYTE_EXACT_CONTROL_FIXTURE','runtime':'ALL_NOT_RUN',
            'proof_credit':'NONE','runtime_obligations_closed':0}

if __name__ == '__main__': print(json.dumps(audit(),indent=2))
