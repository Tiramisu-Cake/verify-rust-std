#!/usr/bin/env python3
"""Read-only static checks. Never starts a compiler, verifier, or CI job."""
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess

CONTROL=Path('/root/kani-ch8-s1k-nolist-w13')
STD=Path('/root/verify-rust-std-ch8-s1-pprime-w13')
TOOL=Path('/root/kani-upstream-ch8-s1')
CANDIDATE='801c2634cee3f3f39cb20146a1080e016a59e048'
OLD='c03363b3b0a83fa9e78c4841720cb48ee7638c6a'
STOCK='0aac16ef62da9e9d5645782d458593e5d78143ba'


def git(*args):
    return subprocess.check_output(['git','-C',str(CONTROL),*args])


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    assert git('rev-parse','HEAD').decode().strip()==CANDIDATE
    assert git('rev-list','--parents','-n','1','HEAD').decode().split()==[CANDIDATE,STOCK]
    assert not git('status','--porcelain').strip()
    paths=git('diff','--name-only',OLD,CANDIDATE).decode().splitlines()
    assert paths==['.github/workflows/ch8-s1.yml']+['ch8-s1-control/'+s for s in ['CI-REQUEST.json','check_package.py','runner.py','test_package.py','test_runner.py']],paths
    before=git('show',OLD+':ch8-s1-control/CI-REQUEST.json')
    after=(CONTROL/'ch8-s1-control/CI-REQUEST.json').read_bytes()
    old,current=json.loads(before),json.loads(after)
    def literal_rows(value):
        return value.split(b'  "rows": [',1)[1].split(b'  "ci_payload_sha256": {',1)[0]
    assert literal_rows(before)==literal_rows(after)
    assert current['rows']==old['rows'] and len(current['rows'])==23
    assert sorted(set(current)-set(old))==['source_bindings']
    assert sorted(k for k in old if old[k]!=current[k])==['budgets','ci_payload_sha256','selector_binding']
    budget={k:v for k,v in old['budgets'].items() if k not in ('list_seconds','planned_list_seconds')}
    budget.update(warmup_seconds=900,planned_warmup_seconds=600)
    assert current['budgets']==budget
    assert current['variants']==old['variants']
    unchanged=['build_argv','execute','_run_variant','_variant_info','_source_root',
               '_row_base','_artifact_size','binary_fingerprints','_read_pipe']
    def functions(text):
        return {n.name:ast.get_source_segment(text,n) for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)}
    a=functions(git('show',OLD+':ch8-s1-control/runner.py').decode())
    b=functions((CONTROL/'ch8-s1-control/runner.py').read_text())
    for name in unchanged:assert a[name]==b[name],name
    assert 'list_inventory' not in b and '_freeze_inventory' not in b
    expected_workflow=git('show',OLD+':.github/workflows/ch8-s1.yml').decode().replace('List once and run fixed S1 batch','Compile first exact root and run fixed S1 batch').replace('runner.py list --std','runner.py warmup --std')
    assert (CONTROL/'.github/workflows/ch8-s1.yml').read_text()==expected_workflow
    for rel,sha in current['ci_payload_sha256'].items():assert digest((CONTROL/rel).read_bytes())==sha,rel
    for rel,sha in current['changed_file_sha256'].items():assert digest((STD/rel).read_bytes())==sha,rel
    assert set(current['source_bindings'])=={r['id'] for r in current['rows']}
    for row in current['rows']:
        binding=current['source_bindings'][row['id']]
        assert (binding['selector'],binding['mode'],binding['crate'])==(row['selector'],row['mode'],'core')
        path=STD/binding['file'];assert digest(path.read_bytes())==binding['sha256']
        lines=path.read_text().splitlines()
        for loc in binding['locations']:assert lines[loc['line']-1]==loc['source']
        if row['mode']=='PFC':
            target=row.get('target') or ('<Cell<u8> as StableSmallSortTypeImpl>::small_sort' if 'default' in row['id'] else '<u8 as StableSmallSortTypeImpl>::small_sort')
            assert binding['target']==target
        else:assert binding['target'] is None
    env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','GITHUB_REPOSITORY':'Tiramisu-Cake/kani',
         'GITHUB_EVENT_NAME':'push','GITHUB_REF':'refs/heads/uninit-ci/ch8-s1k-nolist-w13',
         'GITHUB_RUN_ATTEMPT':'1','GITHUB_SHA':CANDIDATE}
    for argv in ([str(CONTROL/'ch8-s1-control/check_package.py'),'control','--repo',str(CONTROL)],
                 [str(CONTROL/'ch8-s1-control/runner.py'),'check-source','--std',str(STD),'--tool',str(TOOL)]):
        subprocess.run(['python3',*argv],env=env,check=True,stdout=subprocess.PIPE)
    subprocess.run(['git','-C',str(CONTROL),'diff','--check',STOCK,CANDIDATE],check=True)
    print(json.dumps({'state':'PASS_STATIC_ONLY','candidate':CANDIDATE,
        'tree':git('rev-parse','HEAD^{tree}').decode().strip(),'parent':STOCK,
        'delta_vs_previous':paths,'row_count':23,'literal_rows_sha256':digest(literal_rows(after)),
        'unchanged_functions':unchanged,'source_and_payload_identity':'PASS','budgets':budget,
        'source_bindings':len(current['source_bindings']),'global_list':'REMOVED',
        'proof_rows':'ALL_23_NOT_RUN','proof_credit':'NONE'},indent=2))


if __name__=='__main__':main()
