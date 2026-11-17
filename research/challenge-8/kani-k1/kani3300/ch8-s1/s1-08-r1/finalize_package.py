#!/usr/bin/env python3
"""Materialize review identities and exact local patches, without CI or push."""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess

import prepare_package as p

HERE=Path(__file__).resolve().parent
CONTROL=Path('/root/kani-ch8-s1-08-fix-w13')
STD=Path('/root/verify-rust-std-ch8-s1-08-w13')
G0=HERE.parents[5]


def sha(data): return hashlib.sha256(data).hexdigest()

def pin(repo, ref): return p.git(repo,'rev-parse',ref).strip()


def main():
    control_sha=pin(CONTROL,'HEAD');control_tree=pin(CONTROL,'HEAD^{tree}')
    assert pin(CONTROL,'HEAD^')==p.CONTROL_BASE
    assert pin(STD,'HEAD')==p.STD
    for repo in (CONTROL,STD):
        assert not p.git(repo,'status','--porcelain')
        assert p.git(repo,'log','-1','--format=%an <%ae>').strip()=='Tiramisu-Cake <igkharin@gmail.com>'
        msg=p.git(repo,'log','-1','--format=%B')
        assert '[skip ci]' in msg and 'Co-Authored-By' not in msg
    request_bytes=(CONTROL/'ch8-s1-control/CI-REQUEST.json').read_bytes()
    request=json.loads(request_bytes)
    task_sha=pin(G0,'4ccfdcc024')
    identity={'schema':'ch8-s1-08-r1-identities-v1', 'status':'READY_FOR_REVIEW',
       'task_commit':task_sha,'entry_g0':task_sha,
       'source':{'worktree':str(STD),'sha':p.STD,'parent':p.STD_BASE,'tree':pin(STD,'HEAD^{tree}'),
                 'files':{rel:request['changed_file_sha256'][rel] for rel in [p.PREFIX+n for n in p.FILES]}},
       'control':{'worktree':str(CONTROL),'sha':control_sha,'parent':p.CONTROL_BASE,'tree':control_tree,
                  'embedded_request_sha256':sha(request_bytes),'role_map_sha256':request['role_map']['sha256']},
       'tool':{'sha':p.TOOL,'tree':request['tool_tree'],'change':'NONE'},
       'previous_frozen_candidate':{'source':p.STD,'control':'9ccd882ef2460fbc97400594e7e3dfc884a4a997','package':'8ea1c1d370f4076eb6ed4aeaa0a96898499ce580','immutable':True},
       'admission':'OFFLINE_PENDING','independent_review':'PENDING_DELTA_W14',
       'compiler_runtime':'NOT_RUN','ci_push_publication_ledger':'NOT_RUN'}
    p.write(HERE/'IDENTITIES.json',identity)
    (HERE/'EMBEDDED-CI-REQUEST.json').write_bytes(request_bytes)
    (HERE/'ROLE-MAP.json').write_bytes((CONTROL/'ch8-s1-control/ROLE-MAP.json').read_bytes())
    request['control_candidate']={'sha':control_sha,'tree':control_tree,'worktree':str(CONTROL),
        'parent':p.CONTROL_BASE,'embedded_request_sha256':sha(request_bytes),
        'entry_g0':task_sha,'publication':'LOCAL_ONLY','dispatch_authorized':False}
    p.write(HERE/'CI-REQUEST.json',request)
    patches=[]
    for name,repo,base,head in [('SOURCE-CANDIDATE.patch',STD,p.STD_BASE,p.STD),
                              ('CONTROL-CANDIDATE.patch',CONTROL,p.CONTROL_BASE,control_sha),
                              ('REVIEW-DELTA.patch',CONTROL,'9ccd882ef2460fbc97400594e7e3dfc884a4a997',control_sha)]:
        data=subprocess.check_output(['git','-C',str(repo),'diff','--binary',base,head])
        (HERE/name).write_bytes(data)
        patches.append({'path':name,'base':base,'candidate':head,'sha256':sha(data)})
    p.write(HERE/'PATCHES.json',{'patches':patches,'application':'Exact base Git tree; no history rewriting'})
    print(json.dumps({'std':p.STD,'control':control_sha,'request_sha256':sha(request_bytes)}))


if __name__=='__main__':main()
