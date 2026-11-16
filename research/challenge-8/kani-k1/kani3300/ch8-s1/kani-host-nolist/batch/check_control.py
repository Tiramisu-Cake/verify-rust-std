#!/usr/bin/env python3
"""Read-only static checks. Never starts a compiler, verifier, or CI job."""
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess

CONTROL=Path('/root/kani-ch8-s1k-batch-w13')
STD=Path('/root/verify-rust-std-ch8-s1-pprime-w13')
TOOL=Path('/root/kani-upstream-ch8-s1')
CANDIDATE='40b5d9cf48900ff1e227e1fbba24cb5b2edbf8d5'
OLD='801c2634cee3f3f39cb20146a1080e016a59e048'
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
    assert sorted(set(current)-set(old))==['batch_policy']
    assert current['source_bindings']==old['source_bindings']
    assert sorted(k for k in old if old[k]!=current[k])==['budgets','ci_payload_sha256','selector_binding']
    budget={k:v for k,v in old['budgets'].items() if k not in ('warmup_seconds','planned_warmup_seconds')}
    budget.update(compile_seconds=900,planned_compile_seconds_per_group=330,group_rss_max_kib=12582912,memory_reserve_kib=2097152)
    assert current['budgets']==budget
    assert current['variants']==old['variants']
    unchanged=['verify_source','ci_env','_run_variant','_variant_info','_source_root',
               '_row_base','_artifact_size','binary_fingerprints','_target_tokens','_bounded_log']
    def functions(text):
        return {n.name:ast.get_source_segment(text,n) for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)}
    a=functions(git('show',OLD+':ch8-s1-control/runner.py').decode())
    b=functions((CONTROL/'ch8-s1-control/runner.py').read_text())
    for name in unchanged:assert a[name]==b[name],name
    assert not {'list_inventory','_freeze_inventory','warmup','build_warmup_argv'} & set(b)
    assert a['parse_export'].split('    binding = source_binding or {}',1)[1]==b['parse_export'].split('    binding = source_binding or {}',1)[1]
    expected_workflow=git('show',OLD+':.github/workflows/ch8-s1.yml').decode().replace('Compile first exact root and run fixed S1 batch','Run grouped S1 batch with per-harness timeout').replace('          python3 control/ch8-s1-control/runner.py warmup --std export --tool tool --out "$RECEIPT_ROOT"\n','')
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
         'GITHUB_EVENT_NAME':'push','GITHUB_REF':'refs/heads/uninit-ci/ch8-s1k-batch-w13',
         'GITHUB_RUN_ATTEMPT':'1','GITHUB_SHA':CANDIDATE}
    for argv in ([str(CONTROL/'ch8-s1-control/check_package.py'),'control','--repo',str(CONTROL)],
                 [str(CONTROL/'ch8-s1-control/runner.py'),'check-source','--std',str(STD),'--tool',str(TOOL)]):
        subprocess.run(['python3',*argv],env=env,check=True,stdout=subprocess.PIPE)
    subprocess.run(['git','-C',str(CONTROL),'diff','--check',STOCK,CANDIDATE],check=True)
    import sys
    sys.path.insert(0,str(CONTROL/'ch8-s1-control'))
    import runner
    groups=runner.group_rows(current['rows'])
    assert [(g['variant'],g['unwind'],len(g['rows'])) for g in groups]==[('production',34,15),('production',5,3),('production',4,3),('activation-default',34,1),('activation-override',34,1)]
    # Evaluate only the prior pure argv constructor, never a compiler or runner command.
    namespace={'Path':Path,'UNSTABLE':runner.UNSTABLE}
    exec(a['build_argv'],namespace)
    for group in groups:
        selectors=[row['selector'] for row in group['rows']]
        export=Path('/synthetic/export.json')
        argv=runner.build_argv(STD,TOOL,selectors,group['unwind'],export)
        for row in group['rows']:
            projected=[];i=0
            while i<len(argv):
                if argv[i]=='--harness-timeout':i+=2;continue
                if argv[i]=='--harness' and argv[i+1]!=row['selector']:i+=2;continue
                projected.append(argv[i]);i+=1
            assert projected==namespace['build_argv'](STD,TOOL,row['selector'],row['unwind'],export)
    assert 5*330+current['budgets']['planned_rows_seconds']==4410<4500

    print(json.dumps({'state':'PASS_STATIC_ONLY','candidate':CANDIDATE,
        'tree':git('rev-parse','HEAD^{tree}').decode().strip(),'parent':STOCK,
        'delta_vs_previous':paths,'row_count':23,'literal_rows_sha256':digest(literal_rows(after)),
        'unchanged_functions':unchanged,'source_and_payload_identity':'PASS','budgets':budget,
        'source_bindings':len(current['source_bindings']),'global_list':'REMOVED','separate_warmup':'REMOVED','groups':[{k:g[k] for k in ('id','variant','unwind')} | {'rows':len(g['rows'])} for g in groups],
        'per_row_argv_flags':'IDENTICAL_AFTER_PROJECTING_BATCH_SELECTORS_AND_ADDED_HARNESS_TIMEOUT',
        'binding_oracle_tail':'BYTE_IDENTICAL','planned_compile_plus_rows_seconds':4410,
        'per_root_rss_status':'UNKNOWN_NO_EXACT_HARNESS_ATTRIBUTION',
        'proof_rows':'ALL_23_NOT_RUN','proof_credit':'NONE'},indent=2))


if __name__=='__main__':main()
