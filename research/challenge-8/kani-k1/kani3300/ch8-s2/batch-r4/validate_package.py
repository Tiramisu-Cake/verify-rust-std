#!/usr/bin/env python3
"""Exact-object, source and package preflight; no compiler or full runner."""
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def git(repo, *args, env=None):
    return subprocess.check_output(['git', '-C', str(repo), *args], env=env, text=True).strip()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2) + '\n')


def replay(repo, item):
    with tempfile.TemporaryDirectory(prefix='s2-r4-index-') as tmp:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(tmp) / 'index'))
        subprocess.run(['git', '-C', str(repo), 'read-tree', item['base']], env=env, check=True)
        subprocess.run(['git', '-C', str(repo), 'apply', '--cached', str(HERE / item['path'])],
                       env=env, check=True)
        tree = git(repo, 'write-tree', env=env)
        assert tree == item['target_tree']
        return {'patch': item['path'], 'base': item['base'], 'tree': tree, 'status': 'EXACT_TREE_MATCH'}


def shallow(repo, head, depth, endpoint):
    common = Path(git(repo, 'rev-parse', '--git-common-dir'))
    if not common.is_absolute():
        common = (repo / common).resolve()
    chain = git(repo, 'rev-list', '--first-parent', '--max-count=' + str(depth), head).splitlines()
    assert len(chain) == depth and endpoint in chain
    with tempfile.TemporaryDirectory(prefix='s2-r4-shallow-') as tmp:
        probe = Path(tmp)
        subprocess.run(['git', 'init', '-q', str(probe)], check=True)
        (probe / '.git/objects/info/alternates').write_text(str(common / 'objects') + '\n')
        subprocess.run(['git', '-C', str(probe), 'update-ref', 'refs/heads/probe', head], check=True)
        subprocess.run(['git', '-C', str(probe), 'symbolic-ref', 'HEAD', 'refs/heads/probe'], check=True)
        (probe / '.git/shallow').write_text(chain[-1] + '\n')
        assert git(probe, 'rev-parse', '--is-shallow-repository') == 'true'
        assert git(probe, 'rev-list', '--first-parent', 'HEAD').splitlines() == chain
        assert git(probe, 'cat-file', '-t', endpoint) == 'commit'
        paths = git(probe, 'diff', '--name-only', endpoint, 'HEAD').splitlines()
        assert git(probe, 'rev-parse', 'HEAD^{tree}') == git(repo, 'rev-parse', head + '^{tree}')
    return {'head': head, 'depth': depth, 'endpoint': endpoint, 'retained_chain': chain,
            'endpoint_diff_paths': paths, 'status': 'PASS_REAL_SHALLOW_GIT_METADATA_SHARED_OBJECTS'}


def main():
    from unittest import mock
    import re
    ids=json.loads((HERE/'PINS.json').read_text())
    S=Path(ids['source']['worktree']);C=Path(ids['control']['worktree']);T=Path(ids['tool']['worktree']);Q=C/'ch8-s1-control'
    sys.path.insert(0,str(Q))
    import runner,cfg_pfc,ordinary_contracts,contract_stacks,s2_correspondence,check_package
    r=runner.load_request()
    for label,repo in [('source',S),('control',C),('tool',T)]:
        assert git(repo,'rev-parse','HEAD')==ids[label]['sha']
        assert git(repo,'rev-parse','HEAD^{tree}')==ids[label]['tree']
        assert git(repo,'rev-parse','HEAD^')==ids[label]['parent']
        assert not git(repo,'status','--porcelain=v1')
    assert sha(Q/'CI-REQUEST.json')==ids['control']['request_sha256']
    assert sha(C/'.github/workflows/ch8-s2.yml')==ids['control']['workflow_sha256']
    assert (HERE/'CI-REQUEST.json').read_bytes()==(Q/'CI-REQUEST.json').read_bytes()
    assert (HERE/'WORKFLOW.yml').read_bytes()==(C/'.github/workflows/ch8-s2.yml').read_bytes()
    for p,digest in json.loads((HERE/'SOURCE-MAP.json').read_text())['files'].items():assert sha(S/p)==digest,p
    # Execute the actual final check-source subcommand; never build or full run.
    preflight=subprocess.run([sys.executable,str(Q/'runner.py'),'check-source','--std',str(S),'--tool',str(T)],
                             env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),capture_output=True,text=True)
    (HERE/'PREBUILD-SOURCE-PREFLIGHT.txt').write_text(preflight.stdout+preflight.stderr)
    assert preflight.returncode==0,preflight.stderr
    trace=[]
    def traced(label,fun):
        def call(*args,**kwargs):
            result=fun(*args,**kwargs);trace.append({'gate':label,'status':result['status'],
                      'contexts':len(result.get('contexts',result.get('rows',[])))})
            return result
        return call
    with mock.patch.object(ordinary_contracts,'check',side_effect=traced('ordinary_NO_ACTIVE_CONTRACT_ATTRS',ordinary_contracts.check)), \
         mock.patch.object(cfg_pfc,'check',side_effect=traced('verified_same_cfg_PFC',cfg_pfc.check)):
        source_result=runner.verify_source(S,T,r)
    assert [x['gate'] for x in trace]==['ordinary_NO_ACTIVE_CONTRACT_ATTRS','verified_same_cfg_PFC']
    assert all(x['contexts']==11 for x in trace)
    cfg=cfg_pfc.check(S,r);ordinary=ordinary_contracts.check(S,r);stacks=contract_stacks.check(S,r)
    for name,result in [('CFG-PFC-MAP.json',cfg),('ORDINARY-STUB-CONTRACT-MAP.json',ordinary),('CONTRACT-STACK-MAP.json',stacks)]:
        assert json.loads((HERE/name).read_text())==result
    assert len(stacks['contract_stacks'])==19 and len(stacks['contexts'])==11 and len(stacks['functions'])==326
    assert len(ordinary['checked_active_ordinary_uses'])==23
    assert not any(x['active_contract_attrs'] for x in ordinary['checked_active_ordinary_uses'])
    assert s2_correspondence.check((S/s2_correspondence.BATCH).read_text(),(S/s2_correspondence.SMALLSORT).read_text())==json.loads((HERE/'COPY-CORRESPONDENCE.json').read_text())
    assert git(S,'diff','--name-only',ids['source']['derivation_source'],'HEAD')==s2_correspondence.BATCH
    assert git(S,'diff',ids['source']['derivation_source'],'HEAD','--',s2_correspondence.SMALLSORT)==''
    os.environ.update(GITHUB_REPOSITORY='Tiramisu-Cake/kani',GITHUB_EVENT_NAME='push',
        GITHUB_REF='refs/heads/uninit-ci/ch8-s2-batch3probes-offline-r4',GITHUB_RUN_ATTEMPT='1',GITHUB_SHA=ids['control']['sha'])
    control_result=check_package.control(C);yaml_result=check_package.check_yaml(C/'.github/workflows/ch8-s2.yml')
    old=json.loads(git(C,'show',ids['control']['derivation_control']+':ch8-s1-control/CI-REQUEST.json'))
    for key in ('budgets','flags','execution_groups','variants','replacement_unions','formal_expected_inventory','diagnostic_assumed_inventory','qualification_inventory'):assert r[key]==old[key]
    assert [x['required_cover_messages'] for x in r['rows']]==[x['required_cover_messages'] for x in old['rows']]
    assert [x.get('failure_description') for x in r['rows']]==[x.get('failure_description') for x in old['rows']]
    assert sum(x['required_cover_count'] for x in r['rows'])==20 and sum('oracle' in x for x in r['rows'])==6
    fixtures=json.loads((Q/'S2-SOURCE.json').read_text())
    for rel,text in fixtures.items():assert (S/rel).read_text()==text
    paths=git(C,'diff','--name-only',ids['tool']['sha'],'HEAD').splitlines();assert paths==r['ci_changed_paths']
    existing={p for p in paths if (C/p).is_file()}-{'ch8-s1-control/CI-REQUEST.json'}
    assert existing==set(r['ci_payload_sha256'])
    for p,digest in r['ci_payload_sha256'].items():assert sha(C/p)==digest
    patches=[]
    for item in json.loads((HERE/'PATCHES.json').read_text()):
        assert sha(HERE/item['path'])==item['sha256']
        patches.append(replay(S if item['path'].startswith('SOURCE-') else C,item))
    ancestry=[shallow(C,ids['control']['sha'],7,ids['tool']['sha']),
              shallow(S,ids['source']['sha'],5,ids['source']['base']),shallow(T,ids['tool']['sha'],2,ids['tool']['sha'])]
    invariance=json.loads((HERE/'RUNNER-INVARIANCE.json').read_text())
    for rec in invariance['files']:
        assert sha(C/rec['path'])==rec['r4_sha256']
        data=subprocess.check_output(['git','-C',str(C),'show',invariance['reference']+':'+rec['path']])
        assert hashlib.sha256(data).hexdigest()==rec['r3_sha256']
        if rec['status']=='BYTE_IDENTICAL':assert data==(C/rec['path']).read_bytes()
    proof=json.loads((HERE/'TEST-PROVENANCE.json').read_text());transcript=(HERE/'TARGETED-TESTS.txt').read_text()
    assert proof['source_sha']==ids['source']['sha'] and proof['control_sha']==ids['control']['sha']
    assert proof['request_sha256']==ids['control']['request_sha256'] and proof['exit_code']==0
    match=re.search(r'Ran ([0-9]+) tests in',transcript);assert match and transcript.endswith('\nOK\n')
    assert int(match[1])==proof['test_count']
    parsed=[]
    for p in sorted(Q.glob('*.py')):ast.parse(p.read_text(),filename=str(p));parsed.append(p.name)
    for repo,base in [(S,ids['source']['base']),(C,ids['control']['base'])]:
        subprocess.run(['git','-C',str(repo),'diff','--check',base,'HEAD'],check=True)
    for row in r['rows']:
        argv=runner.build_argv(S,T,[row['selector']],34,Path('/synthetic/export.json'))
        assert argv.count('--harness')==1 and argv[argv.index('--harness-timeout')+1]=='600s'
        assert '--exact' in argv and '--no-assert-contracts' in argv and '--jobs=1' in argv
    write('VALIDATION.json',{'state':'STATIC_PASS','source':source_result,'control':control_result,'workflow':yaml_result,
          'actual_final_prebuild_subcommand_exit':preflight.returncode,'actual_source_preflight_gate_trace':trace,
          'patch_replays':patches,'checkout_depths':ancestry,'python_AST_files':parsed,
          'tests':proof,'ordinary_binding_records':23,'selected_roots':11,'covers':20,'negative_oracles':6,
          'original_contract_stacks':19,'original_function_bodies_and_contracts':'BYTE_IDENTICAL_TO_R3',
          'native_compile':'NOT_RUN','causal_repair':'NOT_RUN','actual_causal_CI_unit':'UNKNOWN','proof_credit':'NONE'})
    print('STATIC_PASS: actual final source/control preflight; both gates in11 contexts;6 exact patch replays;checkout7/5/2;'+str(proof['test_count'])+' final-object offline tests.')


if __name__=='__main__':main()
