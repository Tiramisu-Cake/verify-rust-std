#!/usr/bin/env python3
"""Offline exact delta, Git/shallow and synthetic checks. Never dispatches."""
import argparse
import ast
import copy
import hashlib
import importlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
CONTROL=Path('/root/kani-ch8-s1-08-cell-retry-w13')
SOURCE=Path('/root/verify-rust-std-ch8-s1-08-w13')
BASE='7c41333f9bfcfd7eb4e0ede7bd316443090c9025'
PARENT='9208b373c0a08a265fa0d7493a6529e331065271'
STD='99e8456d200fff1299ee5756279cddb23921dc65'
TOOL='0aac16ef62da9e9d5645782d458593e5d78143ba'
TASK='49f2363e09b63b433ef84cb2b6cbaf1a05112386'
WHITELIST=['.github/workflows/ch8-s1.yml','ch8-s1-control/CI-REQUEST.json',
 'ch8-s1-control/cell_retry_profile.py','ch8-s1-control/check_package.py',
 'ch8-s1-control/runner.py','ch8-s1-control/test_cell_retry.py']
H=CONTROL/'ch8-s1-control'
sys.path.insert(0,str(H))
import runner as r
import check_package as c
import cell_retry_profile as p


def git(repo,*args,env=None):
    return subprocess.check_output(['git','-C',str(repo),*args],env=env,stderr=subprocess.PIPE)
def textgit(repo,*args):return git(repo,*args).decode().strip()
def sha(data):return hashlib.sha256(data).hexdigest()
def write(path,value):path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
def blob(repo,commit,path):return git(repo,'show',commit+':'+path)
def functions(data):
    return {node.name:ast.dump(node,include_attributes=False) for node in ast.parse(data).body
            if isinstance(node,(ast.FunctionDef,ast.ClassDef))}
def differences(old,new,path=''):
    if type(old)!=type(new):return [{'pointer':path,'before':old,'after':new}]
    if isinstance(old,dict):
        out=[]
        for key in sorted(set(old)|set(new)):
            ptr=path+'/'+key.replace('~','~0').replace('/','~1')
            if key not in old:out.append({'pointer':ptr,'added':new[key]})
            elif key not in new:out.append({'pointer':ptr,'removed':old[key]})
            else:out.extend(differences(old[key],new[key],ptr))
        return out
    if isinstance(old,list) and len(old)==len(new):
        return [d for i,(a,b) in enumerate(zip(old,new)) for d in differences(a,b,path+'/'+str(i))]
    return [] if old==new else [{'pointer':path,'before':old,'after':new}]


def static_checks():
    candidate=textgit(CONTROL,'rev-parse','HEAD')
    assert textgit(CONTROL,'rev-parse','HEAD^')==PARENT
    assert textgit(CONTROL,'rev-list','--parents','-n','1','HEAD').split()==[candidate,PARENT]
    assert not textgit(CONTROL,'status','--porcelain=v1','--untracked-files=no')
    assert textgit(CONTROL,'log','-1','--format=%an <%ae>')=='Tiramisu-Cake <igkharin@gmail.com>'
    assert '[skip ci]' in textgit(CONTROL,'log','-1','--format=%B')
    paths=textgit(CONTROL,'diff','--name-only',BASE,candidate).splitlines()
    assert paths==WHITELIST
    request=r.load_request();base=json.loads(blob(CONTROL,BASE,'ch8-s1-control/CI-REQUEST.json'))
    changes=differences(base,request)
    allowed={'schema','budgets','reservations','batch_policy','ci_changed_paths','workflow_stages',
             'artifact_policy','execution_scope','ci_payload_sha256'}
    for item in changes:
        ptr=item['pointer'];head=ptr.split('/')[1]
        if head=='rows':
            _,_,index,field=ptr.split('/')
            assert field=='timeout_seconds' and base['rows'][int(index)]['id'] in p.ROW_IDS
            assert item['before']==600 and item['after']==1200
        else:assert head in allowed,ptr
    assert sum(x['pointer'].startswith('/rows/') for x in changes)==2
    # All declared reference rows/ROLE-MAP/source/oracles remain canonical7c.
    assert len(request['rows'])==35 and len(request['execution_groups'])==14
    assert (H/'ROLE-MAP.json').read_bytes()==blob(CONTROL,BASE,'ch8-s1-control/ROLE-MAP.json')
    assert request['flags']==base['flags']
    unchanged={}
    treepaths=textgit(CONTROL,'ls-tree','-r','--name-only',BASE,'ch8-s1-control').splitlines()
    for rel in treepaths:
        if rel not in paths:
            value=blob(CONTROL,BASE,rel);assert (CONTROL/rel).read_bytes()==value
            unchanged[rel]=sha(value)
    changed_functions={}
    for rel,expected in {'ch8-s1-control/runner.py':['load_request','select_groups','build_argv','_selection_matches','_run_group'],
                         'ch8-s1-control/check_package.py':['check_yaml','fallback']}.items():
        before=functions(blob(CONTROL,BASE,rel));after=functions((CONTROL/rel).read_bytes())
        changed=sorted(k for k in set(before)|set(after) if before.get(k)!=after.get(k))
        assert changed==sorted(expected);changed_functions[rel]=changed
    old=c.load_yaml(blob(CONTROL,BASE,'.github/workflows/ch8-s1.yml').decode())
    new=c.load_yaml((CONTROL/'.github/workflows/ch8-s1.yml').read_text())
    expected=copy.deepcopy(old);expected['name']='CH8 S1-08 cell retry1200'
    job=expected['jobs']['s1_cell'];job.pop('needs');job['if']="${{ github.repository == 'Tiramisu-Cake/kani' && github.event_name == 'push' }}"
    job['steps'][2]['run']='python3 check_package.py control --repo ..\npython3 -m unittest -v test_cell_retry.py test_s108.py test_s108r1.py\n'
    expected['jobs']={'s1_cell':job};assert new==expected
    assert c.check_yaml(CONTROL/'.github/workflows/ch8-s1.yml')['yaml']=='PASS'
    for rel,digest in request['ci_payload_sha256'].items():assert sha((CONTROL/rel).read_bytes())==digest
    assert textgit(CONTROL,'diff','--name-only',TOOL,candidate).splitlines()==request['ci_changed_paths']
    assert textgit(SOURCE,'rev-parse','HEAD')==STD and not textgit(SOURCE,'status','--porcelain=v1')
    assert textgit(SOURCE,'rev-parse','HEAD^{tree}')==request['std_tree']
    assert textgit(CONTROL,'rev-parse',TOOL+'^{tree}')==request['tool_tree']
    for rel,digest in request['changed_file_sha256'].items():assert sha(blob(SOURCE,STD,rel))==digest
    write(HERE/'SEMANTIC-DIFF.json',{'status':'PASS','base':BASE,'candidate':candidate,'whitelist':WHITELIST,
        'json_changes':changes,'changed_functions':changed_functions,'unchanged_payload_sha256':unchanged,
        'yaml':'EXACT_BASE_CELL_JOB_MINUS_NEEDS_PLUS_TARGETED_TESTS_AND_NAME',
        'source_and_tool':'EXACT_UNCHANGED_COMMITS_AND_TREES','proof_runtime_delta':'TWO_CELL_TIMEOUTS600_TO1200_ONLY',
        'decoder_missing_RESULTS':'UNCHANGED_FAIL_CLOSED','proof_credit':'NONE'})
    return {'status':'PASS','whitelist':WHITELIST,'request_delta_count':len(changes),
            'immutable_payload_files':len(unchanged),'functions':changed_functions,'yaml':'PASS','payload':'PASS'}


def shallow_checks():
    candidate=textgit(CONTROL,'rev-parse','HEAD');request=r.load_request();report={}
    with tempfile.TemporaryDirectory(prefix='w13-cell-shallow-') as tmp:
        root=Path(tmp)
        for label,origin,commit,depth,paths in [('control',CONTROL,candidate,5,['.github/workflows','ch8-s1-control']),
                ('export',SOURCE,STD,2,['library/core','tool_config']),
                ('tool',CONTROL,TOOL,2,['.github/actions/setup'])]:
            dest=root/label
            subprocess.run(['git','init','-q',str(dest)],check=True)
            git(dest,'fetch','--quiet','--no-tags','--depth',str(depth),origin.as_uri(),commit)
            git(dest,'sparse-checkout','init','--cone');git(dest,'sparse-checkout','set',*paths)
            git(dest,'checkout','--quiet','--detach','FETCH_HEAD')
            assert textgit(dest,'rev-parse','--is-shallow-repository')=='true'
            assert not (dest/'.git/objects/info/alternates').exists()
            report[label]={'sha':textgit(dest,'rev-parse','HEAD'),'tree':textgit(dest,'rev-parse','HEAD^{tree}'),
                           'depth':depth,'actual_commits':int(textgit(dest,'rev-list','--count','HEAD')),
                           'shallow':True,'alternates':False}
        env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','GITHUB_REPOSITORY':'Tiramisu-Cake/kani',
             'GITHUB_EVENT_NAME':'push','GITHUB_REF':'refs/heads/uninit-ci/ch8-s1k-cell-retry-w13',
             'GITHUB_RUN_ATTEMPT':'1','GITHUB_SHA':candidate}
        result=subprocess.run([sys.executable,'check_package.py','control','--repo','..'],
                   cwd=root/'control/ch8-s1-control',env=env,capture_output=True,text=True)
        assert result.returncode==0,result.stderr;report['control_preflight']=json.loads(result.stdout)
        result=subprocess.run([sys.executable,str(root/'control/ch8-s1-control/runner.py'),'check-source',
                    '--std',str(root/'export'),'--tool',str(root/'tool')],env=env,capture_output=True,text=True)
        assert result.returncode==0,result.stderr;report['source_preflight']=json.loads(result.stdout)
        assert textgit(root/'control','rev-parse','HEAD^')==PARENT
        assert textgit(root/'control','cat-file','-t',TOOL)=='commit'
        report['tool_endpoint_diff_paths']=len(textgit(root/'control','diff','--name-only',TOOL,'HEAD').splitlines())
        # Reproduce old fetch-depth error against the actual candidate graph.
        bad=root/'too-shallow';subprocess.run(['git','init','-q',str(bad)],check=True)
        git(bad,'fetch','--quiet','--no-tags','--depth','2',CONTROL.as_uri(),candidate)
        git(bad,'checkout','--quiet','--detach','FETCH_HEAD')
        assert textgit(bad,'rev-parse','HEAD^')==PARENT
        result=subprocess.run(['git','-C',str(bad),'diff','--name-only',TOOL,'HEAD'],capture_output=True,text=True)
        assert result.returncode==128
        report['negative_depth2']={'exit':128,'HEAD_parent_present':True,'tool_endpoint_unavailable':True}
    write(HERE/'SHALLOW-VALIDATION.json',{'status':'PASS','transport':'file:// actual pinned repositories; no alternates',**report})
    return {'status':'PASS','depths':c.CHECKOUT_DEPTHS,'actual_preflight':'PASS','negative_depth2_exit':128}


def artifact_checks():
    ids=json.loads((HERE/'IDENTITIES.json').read_text());candidate=ids['control']['sha']
    embedded=(H/'CI-REQUEST.json').read_bytes()
    assert (HERE/'EMBEDDED-CI-REQUEST.json').read_bytes()==embedded
    req=json.loads((HERE/'CI-REQUEST.json').read_text())
    assert {k:v for k,v in req.items() if k!='control_candidate'}==json.loads(embedded)
    assert req['control_candidate']==ids['control']
    assert ids['control']['embedded_request_sha256']==sha(embedded)
    assert (HERE/'ROLE-MAP.json').read_bytes()==(H/'ROLE-MAP.json').read_bytes()
    report=[]
    with tempfile.TemporaryDirectory(prefix='w13-cell-patches-') as tmp:
        for item in json.loads((HERE/'PATCHES.json').read_text())['patches']:
            path=HERE/item['file'];assert sha(path.read_bytes())==item['sha256']
            env={**os.environ,'GIT_INDEX_FILE':str(Path(tmp)/item['file'])}
            git(CONTROL,'read-tree',item['base'],env=env)
            git(CONTROL,'apply','--cached','--check',str(path),env=env)
            git(CONTROL,'apply','--cached',str(path),env=env)
            tree=git(CONTROL,'write-tree',env=env).decode().strip()
            assert tree==ids['control']['tree']
            report.append({**item,'reconstructed_tree':tree,'result':'EXACT_TREE_MATCH'})
    write(HERE/'ARTIFACT-VALIDATION.json',{'status':'PASS','patches':report,'mirrored_payloads':'EXACT_BYTES'})
    return {'status':'PASS','patches':'EXACT_TREE_MATCH','mirrors':'EXACT_BYTES'}


def run_tests():
    result=subprocess.run([sys.executable,'-m','unittest','-v','test_cell_retry.py','test_s108.py','test_s108r1.py'],
                          cwd=H,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},capture_output=True,text=True)
    assert result.returncode==0,result.stderr
    count=int(re.search(r'Ran (\d+) tests',result.stderr)[1])
    report={'status':'PASS','candidate':textgit(CONTROL,'rev-parse','HEAD'),'exit':0,'top_level_tests':count,
      'command':'PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_cell_retry.py test_s108.py test_s108r1.py',
      'test_payload_sha256':{rel:sha((CONTROL/rel).read_bytes()) for rel in r.load_request()['ci_payload_sha256'] if Path(rel).name.startswith('test')},
      'scope':'small static and isolated synthetic subprocess/service tests; no compiler/verifier/full runner',
      'initial_development_failures':'fixture path error; no-op mutation; matrix-wide reused fixture; missing synthetic finish. Fixed before frozen candidate; no gate weakened.'}
    write(HERE/'TEST-RESULT.json',report)
    return report


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--tests',action='store_true');a=parser.parse_args()
    result={'status':'PASS','candidate':textgit(CONTROL,'rev-parse','HEAD'),'static':static_checks(),
            'shallow':shallow_checks(),'artifacts':artifact_checks()}
    tests=run_tests() if a.tests else json.loads((HERE/'TEST-RESULT.json').read_text())
    assert tests['candidate']==result['candidate'] and tests['status']=='PASS'
    for rel,digest in tests['test_payload_sha256'].items():assert sha((CONTROL/rel).read_bytes())==digest
    result['tests']=tests
    result.update(review='PENDING_W14',dispatch='NOT_RUN',reservation='NOT_RESERVED',proof_credit='NONE',
       missing_RESULTS_parser='UNCHANGED',runtime_compiler_solver='NOT_RUN',historical_ledgers='UNTOUCHED')
    write(HERE/'VALIDATION.json',result)
    print(json.dumps({'status':'PASS','candidate':result['candidate'],'top_level_tests':tests['top_level_tests'],
                      'shallow':'ACTUAL_PINNED_GIT_FIXTURES_PASS','dispatch':'NOT_RUN'}))

if __name__=='__main__':main()
