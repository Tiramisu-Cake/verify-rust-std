#!/usr/bin/env python3
"""Create CI-only patch with temporary Git index, without checkout/commit/dispatch."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

HERE=Path(__file__).resolve().parent
STD=Path('/root/verify-rust-std-ch8-s1-w13')
SOURCE='75a4d1ea6eb60c63c27c1b18e662740d93bafb08'

def run(*args,data=None,env=None):
    return subprocess.check_output(['git','-C',str(STD),*args],input=data,env=env)

def main():
    r=json.loads((HERE/'CI-REQUEST.json').read_text())
    assert r['status']=='READY' and r['std_sha']==SOURCE
    assert run('rev-parse','HEAD').decode().strip()==SOURCE
    payload={'.github/workflows/ch8-s1.yml':HERE/'ch8-s1.yml'}
    for name in ['runner.py','test_runner.py','check_package.py','activation-default.patch','activation-override.patch']:
        payload['scripts/ch8-s1/'+name]=HERE/name
    r['ci_payload_sha256']={dest:hashlib.sha256(path.read_bytes()).hexdigest() for dest,path in payload.items()}
    workflows=run('ls-tree','-r','--name-only',SOURCE,'.github/workflows').decode().splitlines()
    r['ci_changed_paths']=sorted(set(workflows)|set(payload)|{'scripts/ch8-s1/CI-REQUEST.json'})
    (HERE/'CI-REQUEST.json').write_text(json.dumps(r,indent=2)+'\n')
    payload['scripts/ch8-s1/CI-REQUEST.json']=HERE/'CI-REQUEST.json'
    with tempfile.TemporaryDirectory(prefix='ch8-s1-index-') as d:
        env=os.environ.copy();env['GIT_INDEX_FILE']=str(Path(d)/'index')
        run('read-tree',SOURCE,env=env)
        workflows=run('ls-tree','-r','--name-only',SOURCE,'.github/workflows').decode().splitlines()
        if workflows:run('update-index','--force-remove','--',*workflows,env=env)
        for dest,path in payload.items():
            blob=run('hash-object','-w','--stdin',data=path.read_bytes()).decode().strip()
            run('update-index','--add','--cacheinfo','100644',blob,dest,env=env)
        tree=run('write-tree',env=env).decode().strip()
        patch=run('diff','--binary',SOURCE,tree)
    (HERE/'ci-only.patch').write_bytes(patch)
    changed=run('diff','--name-only',SOURCE,tree).decode().splitlines()
    assert set(changed)==set(workflows)|set(payload)
    assert all(p.startswith(('scripts/ch8-s1/','.github/workflows/')) for p in changed)
    actual=run('ls-tree','-r','--name-only',tree,'.github/workflows').decode().splitlines()
    assert actual==['.github/workflows/ch8-s1.yml']
    # No worktree edits; this is solely a future coordinator overlay.
    run('apply','--check',str(HERE/'ci-only.patch'))
    run('diff','--check',SOURCE,tree)
    identity={'schema':'ch8-s1-ci-overlay-v1','status':'PREPARED_NOT_RUN','base_std_sha':SOURCE,
        'base_std_tree':r['std_tree'],'ci_control_sha':None,'ci_control_sha_note':'Coordinator creates sole-parent trigger commit after review; no local non-skip commit.',
        'ci_control_tree':tree,'patch_sha256':hashlib.sha256(patch).hexdigest(),
        'request_sha256':hashlib.sha256((HERE/'CI-REQUEST.json').read_bytes()).hexdigest(),
        'files':{dest:hashlib.sha256(path.read_bytes()).hexdigest() for dest,path in payload.items()},
        'removed_workflows_in_control_only':workflows,'changed_paths':changed,
        'source_export_preserves_workflows':True,'tool_source_preserves_workflows':True,
        'dispatches':0,'Cloud_dollars':0}
    (HERE/'CI-OVERLAY.json').write_text(json.dumps(identity,indent=2)+'\n')
    print(json.dumps({'tree':tree,'patch_sha256':identity['patch_sha256'],'request_sha256':identity['request_sha256']}))

if __name__=='__main__':main()
