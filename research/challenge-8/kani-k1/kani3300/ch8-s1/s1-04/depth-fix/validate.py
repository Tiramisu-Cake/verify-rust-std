#!/usr/bin/env python3
"""Offline depth-fix closure: Git/static checks only; never builds or dispatches."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

CONTROL=Path('/root/kani-ch8-s1-04-depth-w13')
STD=Path('/root/verify-rust-std-ch8-s1-04-w13')
TOOL=Path('/root/kani-upstream-ch8-s1')
OLD='2a532e5913173d6af4490c25d74c587f7bf1a749'
PARENT='40b5d9cf48900ff1e227e1fbba24cb5b2edbf8d5'
CANDIDATE='205b0e98c771a7e6c6b8ec28414494868bcca4e0'
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(CONTROL/'ch8-s1-control'))
import check_package
import runner


def git(*args):
    return subprocess.check_output(['git','-C',str(CONTROL),*args],text=True).strip()


def main():
    assert git('rev-parse','HEAD')==CANDIDATE
    assert git('rev-list','--parents','-n','1','HEAD').split()==[CANDIDATE,PARENT]
    request=runner.load_request()
    # Exact depth 3 is valid only with this two-edge frozen control/tool graph.
    assert git('rev-parse',PARENT+'^')==request['tool_sha']
    assert git('log','-1','--format=%an <%ae>')=='Tiramisu-Cake <igkharin@gmail.com>'
    assert '[skip ci]' not in git('log','-1','--format=%B').lower()
    assert not git('status','--porcelain','--untracked-files=no')
    paths=git('diff','--name-only',OLD,'HEAD').splitlines()
    assert paths==['.github/workflows/ch8-s1.yml','ch8-s1-control/CI-REQUEST.json',
                   'ch8-s1-control/check_package.py','ch8-s1-control/test_package.py']
    before=json.loads(git('show',OLD+':ch8-s1-control/CI-REQUEST.json'))
    assert {k:v for k,v in request.items() if k!='ci_payload_sha256'}=={
        k:v for k,v in before.items() if k!='ci_payload_sha256'}
    changed_hashes=sorted(k for k,v in request['ci_payload_sha256'].items()
                          if before['ci_payload_sha256'][k]!=v)
    assert changed_hashes==[paths[0],paths[2],paths[3]]
    current=check_package.load_yaml((CONTROL/paths[0]).read_text())
    prior=check_package.load_yaml(git('show',OLD+':'+paths[0]))
    checkout_rows=[]
    for job_name,job in prior['jobs'].items():
        count=0
        for step in job['steps']:
            if not step.get('uses','').startswith('actions/checkout@'):continue
            inputs=step['with'];checkout=inputs['path']
            assert inputs['fetch-depth']==2
            if checkout=='control':inputs['fetch-depth']=3;count+=1
            checkout_rows.append({'job':job_name,'path':checkout,'depth':inputs['fetch-depth']})
        assert count==1
    assert len(checkout_rows)==12
    assert current==prior, 'workflow changed beyond four control depths'
    request_path=CONTROL/'ch8-s1-control/CI-REQUEST.json'
    assert (HERE/'CI-REQUEST.json').read_bytes()==request_path.read_bytes()
    env={'GITHUB_REPOSITORY':'Tiramisu-Cake/kani','GITHUB_EVENT_NAME':'push',
         'GITHUB_REF':'refs/heads/uninit-ci/ch8-s1k-depth-static',
         'GITHUB_RUN_ATTEMPT':'1','GITHUB_SHA':CANDIDATE}
    with patch.dict(os.environ,env):
        control=check_package.control(CONTROL)
    identity=runner.verify_source(STD,TOOL,request)
    tests=json.loads((HERE/'TESTS.json').read_text())
    assert tests['control_sha']==CANDIDATE and tests['result']=='PASS'
    assert tests['tests_run']==38
    return {'offline_closure':'PASS','control_sha':CANDIDATE,'control_parent':PARENT,
            'control_tree':git('rev-parse','HEAD^{tree}'),'prior_control_sha':OLD,
            'delta_paths':paths,'updated_payload_hash_paths':changed_hashes,
            'request_sha256':hashlib.sha256(request_path.read_bytes()).hexdigest(),
            'std_sha':identity['std_sha'],'tool_sha':identity['tool_sha'],
            'checkout_rows':checkout_rows,'workflow_other_fields':'UNCHANGED_TYPED_DOCUMENT_EQUALITY',
            'control_preflight':control['status'],'source_identity_preflight':'PASS_LOCAL_READ_ONLY',
            'shallow_simulation':'12 real file:// synthetic clones, depths from each job; TESTS.json',
            'old_depth_2_regression':'diff against tool endpoint exits 128; HEAD^ still available',
            'synthetic_tests':tests['tests_run'],'scheduled_rows':len(request['rows']),
            'groups':len(request['execution_groups']),'unions':len(request['replacement_unions']),
            'production_shallow_clone':'NOT_RUN; synthetic graph simulation only',
            'github_server_acceptance':'NOT_RUN','proof_execution':'NOT_RUN',
            'proof_credit':'NONE','dispatch':'NOT_RUN'}


if __name__=='__main__':print(json.dumps(main(),indent=2))
