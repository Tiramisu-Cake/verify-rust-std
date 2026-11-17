#!/usr/bin/env python3
"""Review artifact integrity/patch reconstruction only; never dispatches."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

import prepare_package as p

HERE=Path(__file__).resolve().parent


def sha(data): return hashlib.sha256(data).hexdigest()


def check():
    ids=json.loads((HERE/'IDENTITIES.json').read_bytes())
    request=json.loads((HERE/'CI-REQUEST.json').read_bytes())
    embedded=(HERE/'EMBEDDED-CI-REQUEST.json').read_bytes()
    control=Path(ids['control']['worktree']);std=Path(ids['source']['worktree'])
    assert embedded==(control/'ch8-s1-control/CI-REQUEST.json').read_bytes()
    assert sha(embedded)==ids['control']['embedded_request_sha256']==request['control_candidate']['embedded_request_sha256']
    assert (HERE/'ROLE-MAP.json').read_bytes()==(control/'ch8-s1-control/ROLE-MAP.json').read_bytes()
    assert sha((HERE/'ROLE-MAP.json').read_bytes())==request['role_map']['sha256']
    assert {k:v for k,v in request.items() if k!='control_candidate'}==json.loads(embedded)
    assert request['control_candidate']['sha']==ids['control']['sha']
    assert request['control_candidate']['tree']==ids['control']['tree']
    assert request['control_candidate']['dispatch_authorized'] is False
    result=[]
    with tempfile.TemporaryDirectory() as tmp:
        for item in json.loads((HERE/'PATCHES.json').read_bytes())['patches']:
            repo=std if item['path'].startswith('SOURCE') else control
            patch=HERE/item['path']
            assert sha(patch.read_bytes())==item['sha256']
            env={**os.environ,'GIT_INDEX_FILE':str(Path(tmp)/(item['path']+'.index'))}
            def git(*args):
                return subprocess.check_output(['git','-C',str(repo),*args],env=env).decode().strip()
            git('read-tree',item['base']);git('apply','--cached','--check',str(patch));git('apply','--cached',str(patch))
            tree=git('write-tree')
            assert tree==git('rev-parse',item['candidate']+'^{tree}')
            result.append({'patch':item['path'],'base':item['base'],'candidate':item['candidate'],
                           'tree':tree,'sha256':item['sha256'],'reconstruction':'EXACT_TREE_MATCH'})
    return {'status':'PASS','patch_reconstruction':result,'mirrored_payloads':'EXACT_BYTES',
            'dispatch':'NOT_RUN','proof_credit':'NONE'}


if __name__=='__main__':
    result=check();p.write(HERE/'ARTIFACT-VALIDATION.json',result);print(json.dumps(result))
