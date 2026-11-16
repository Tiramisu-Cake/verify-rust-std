#!/usr/bin/env python3
"""Offline preparation closure. No compiler, proof tool, network or dispatch."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

CONTROL=Path('/root/kani-ch8-s1-04-w13')
STD=Path('/root/verify-rust-std-ch8-s1-04-w13')
sys.path.insert(0,str(CONTROL/'ch8-s1-control'))
import runner
import check_package

def git(root,*args):return subprocess.check_output(['git','-C',str(root),*args],text=True).strip()
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    request=runner.load_request()
    assert git(STD,'rev-parse','HEAD')==request['std_sha']
    assert git(STD,'rev-parse','HEAD^{tree}')==request['std_tree']
    changes=git(STD,'diff','--name-only','f22f84f316ad8ef6f3fccce86424bad927b09f78','HEAD').splitlines()
    assert changes and all('/smallsort/verify/' in p for p in changes)
    assert not git(STD,'status','--porcelain','--untracked-files=no')
    for rel,digest in request['changed_file_sha256'].items():assert sha(STD/rel)==digest,rel
    for binding in request['source_bindings'].values():
        path=STD/binding['file'];assert sha(path)==binding['sha256']
        lines=path.read_text().splitlines()
        for loc in binding['locations']:assert lines[loc['line']-1]==loc['source']
    for rel,digest in request['ci_payload_sha256'].items():assert sha(CONTROL/rel)==digest,rel
    assert len(request['rows'])==35 and len(request['execution_groups'])==14
    rows={r['id']:r for r in request['rows']}
    for union in request['replacement_unions']:
        members=[rows[rid] for rid in union['member_row_ids']]
        assert {r['N'] for r in members}=={0,1,2,3}
        assert len({(r['target'],r['type'],r['unwind']) for r in members})==1
        assert set.union(*(set(r['required_cover_messages']) for r in members))==set(union['required_cover_messages'])
        assert len(set(union['required_cover_messages']))==11
    for r in request['rows']:
        oracle=r.get('oracle')
        if oracle:
            assert sha(STD/oracle['file'])==oracle['source_sha256']
            assert (STD/oracle['file']).read_text().splitlines()[oracle['line']-1]==oracle['source_line']
    check_package.check_yaml(CONTROL/'.github/workflows/ch8-s1.yml')
    return {'offline_closure':'PASS','std_sha':request['std_sha'],'control_sha':git(CONTROL,'rev-parse','HEAD'),
            'request_sha256':sha(CONTROL/'ch8-s1-control/CI-REQUEST.json'),'scheduled_rows':35,'groups':14,
            'unions':4,'proof_execution':'NOT_RUN','proof_credit':'NONE','dispatch':'NOT_RUN'}

if __name__=='__main__':print(json.dumps(main(),indent=2))
