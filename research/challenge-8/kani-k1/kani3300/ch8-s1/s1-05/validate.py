#!/usr/bin/env python3
"""Offline package closure only. No proof tools, CI, network or publication."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
CONTROL=Path('/root/kani-ch8-s1-05-w13')
STD=Path('/root/verify-rust-std-ch8-s1-04-w13')
TOOL=Path('/root/kani-upstream-ch8-s1')
sys.dont_write_bytecode=True
sys.path.insert(0,str(CONTROL/'ch8-s1-control'))
import runner
import check_package


def git(repo,*args):
    return subprocess.check_output(['git','-C',str(repo),*args],text=True).strip()


def main():
    request=runner.load_request()
    assert (HERE/'CI-REQUEST.json').read_bytes()==runner.REQUEST_PATH.read_bytes()
    old=json.loads(git(CONTROL,'show','205b0e98c771a7e6c6b8ec28414494868bcca4e0:ch8-s1-control/CI-REQUEST.json'))
    assert request['execution_groups']==old['execution_groups']
    assert request['workflow_stages']==old['workflow_stages']
    assert len(request['rows'])==35 and len(request['execution_groups'])==14
    for row,prior in zip(request['rows'],old['rows']):
        # Only prospective mutant oracle metadata changed; all proof parameters stay frozen.
        for key in set(row)|set(prior):
            if key not in ('oracle','oracle_status'):assert row.get(key)==prior.get(key),(row['id'],key)
        if row['variant']=='production':assert row.get('oracle')==prior.get('oracle')
    assert request['std_sha']==old['std_sha'] and request['tool_sha']==old['tool_sha']
    source=runner.verify_source(STD,TOOL,request)
    for row in request['rows']:
        if row['variant']=='production':continue
        oracle=row['oracle'];proposal=oracle['proposal'];prop=proposal['property']
        assert oracle['property_id']==prop['id'] and oracle['description']==prop['description']
        assert oracle['require_only_this_failure'] and oracle['companion_required_cover_messages']
        variant=request['variants'][row['variant']]
        assert variant==proposal['variant_spec']
        rel=oracle['file']
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);path=root/rel;path.parent.mkdir(parents=True)
            path.write_bytes((STD/rel).read_bytes())
            patch=CONTROL/'ch8-s1-control'/variant['patch']
            subprocess.run(['git','apply','--unsafe-paths',str(patch)],cwd=root,check=True)
            assert hashlib.sha256(path.read_bytes()).hexdigest()==oracle['source_sha256']
            assert path.read_text().splitlines()[oracle['line']-1]==oracle['source_line']
    for rid,anchor in zip(('model_u8_n0_3','model_cell_n0_3','model_noncopy_n0_3'),(66,67,68)):
        assert [p['line'] for p in request['source_bindings'][rid]['locations']]==[anchor,29]
    sha=git(CONTROL,'rev-parse','HEAD')
    os.environ.update(GITHUB_REPOSITORY='Tiramisu-Cake/kani',GITHUB_EVENT_NAME='push',
        GITHUB_REF='refs/heads/uninit-ci/ch8-s1k-s1-05-review-only',GITHUB_RUN_ATTEMPT='1',GITHUB_SHA=sha)
    control=check_package.control(CONTROL)
    assert not git(STD,'status','--porcelain','--untracked-files=no')
    return {'offline_closure':'PASS','control':control,'source':source,'rows':35,'groups':14,
            'artifact_policy':request['artifact_policy'],'local_verifier_execution':'NOT_RUN',
            'preflight_context':'SYNTHETIC_GITHUB_ENV_ONLY; no dispatch',
            'qualified_acceptance':'PENDING_OFFLINE_ACCEPTANCE','proof_credit':'NONE'}


if __name__=='__main__':print(json.dumps(main(),indent=2))
