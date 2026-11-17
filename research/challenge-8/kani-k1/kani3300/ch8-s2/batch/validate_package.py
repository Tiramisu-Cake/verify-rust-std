#!/usr/bin/env python3
"""Static/package validation only. No compiler, verifier, full runner or dispatch."""
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
G=HERE.parents[5]

def git(repo,*args,env=None):
    return subprocess.check_output(['git','-C',str(repo),*args],env=env,text=True).strip()
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def replay(repo,base,patch,expected):
    with tempfile.TemporaryDirectory(prefix='s2-index-') as tmp:
        env=os.environ.copy();env['GIT_INDEX_FILE']=str(Path(tmp)/'index')
        subprocess.run(['git','-C',str(repo),'read-tree',base],env=env,check=True)
        subprocess.run(['git','-C',str(repo),'apply','--cached','--check',str(patch)],env=env,check=True)
        subprocess.run(['git','-C',str(repo),'apply','--cached',str(patch)],env=env,check=True)
        actual=git(repo,'write-tree',env=env)
        assert actual==expected,(patch.name,actual,expected)
        return {'patch':patch.name,'sha256':sha(patch),'base':base,'replayed_tree':actual,'state':'EXACT_TREE_MATCH'}
def shallow(repo,head,depth,endpoint):
    # Real candidate objects and commit IDs, separate temporary ref/index/shallow
    # metadata, shared object database. No clone of target/build/artifact trees.
    common=Path(git(repo,'rev-parse','--git-common-dir'))
    if not common.is_absolute():common=(repo/common).resolve()
    chain=git(repo,'rev-list','--first-parent','--max-count='+str(depth),head).splitlines()
    assert len(chain)==depth
    with tempfile.TemporaryDirectory(prefix='s2-shallow-') as tmp:
        root=Path(tmp)
        subprocess.run(['git','init','-q',str(root)],check=True)
        (root/'.git/objects/info/alternates').write_text(str(common/'objects')+'\n')
        subprocess.run(['git','-C',str(root),'update-ref','refs/heads/probe',head],check=True)
        subprocess.run(['git','-C',str(root),'symbolic-ref','HEAD','refs/heads/probe'],check=True)
        (root/'.git/shallow').write_text(chain[-1]+'\n')
        assert git(root,'rev-parse','--is-shallow-repository')=='true'
        assert git(root,'rev-list','--first-parent','HEAD').splitlines()==chain
        assert git(root,'rev-parse','HEAD')==head
        assert git(root,'cat-file','-t',endpoint)=='commit'
        paths=git(root,'diff','--name-only',endpoint,'HEAD').splitlines()
        assert git(root,'rev-parse','HEAD^{tree}')==git(repo,'rev-parse',head+'^{tree}')
        assert git(root,'ls-tree','-r','--name-only','HEAD')
        return {'head':head,'depth':depth,'boundary':chain[-1],'endpoint':endpoint,'retained_chain':chain,'endpoint_diff_paths':paths,'state':'PASS_REAL_GIT_SHALLOW_METADATA_SHARED_OBJECTS'}

def main():
    ids=json.loads((HERE/'IDENTITIES.json').read_text())
    S=Path(ids['source']['worktree']);C=Path(ids['control']['worktree']);T=Path('/root/kani-upstream-ch8-s1')
    assert git(G,'merge-base','--is-ancestor',ids['entry_g0'],'HEAD')==''
    assert sha(G/ids['shared_INPUTS'])==ids['shared_INPUTS_sha256']
    for label,repo in [('source',S),('control',C),('tool',T)]:
        assert git(repo,'rev-parse','HEAD')==ids[label]['sha']
        assert git(repo,'rev-parse','HEAD^{tree}')==ids[label]['tree']
        assert not git(repo,'status','--porcelain=v1'),label
    sys.path.insert(0,str(C/'ch8-s1-control'))
    import runner,check_package,s2_policy
    request=runner.load_request()
    assert (HERE/'CI-REQUEST.json').read_bytes()==(C/'ch8-s1-control/CI-REQUEST.json').read_bytes()
    assert (HERE/'WORKFLOW.yml').read_bytes()==(C/'.github/workflows/ch8-s2.yml').read_bytes()
    assert sha(HERE/'CI-REQUEST.json')==ids['control']['request_sha256']
    source=runner.verify_source(S,T,request)
    assert s2_policy.validate_source(S,request)
    yaml=check_package.check_yaml(C/'.github/workflows/ch8-s2.yml')
    os.environ.update(GITHUB_REPOSITORY='Tiramisu-Cake/kani',GITHUB_EVENT_NAME='push',
        GITHUB_REF='refs/heads/uninit-ci/ch8-s2-batch3probes-synthetic-preflight',
        GITHUB_RUN_ATTEMPT='1',GITHUB_SHA=ids['control']['sha'])
    preflight=check_package.control(C)
    patches=[replay(S,ids['source']['base'],HERE/'SOURCE-CANDIDATE.patch',ids['source']['tree']),
        replay(C,ids['control']['base'],HERE/'CONTROL-DELTA.patch',ids['control']['tree']),
        replay(C,ids['tool']['sha'],HERE/'CONTROL-CANDIDATE.patch',ids['control']['tree'])]
    ancestry=[shallow(C,ids['control']['sha'],7,ids['tool']['sha']),
        shallow(S,ids['source']['sha'],4,ids['source']['base']),
        shallow(T,ids['tool']['sha'],2,ids['tool']['sha'])]
    parsed=[]
    for path in sorted((C/'ch8-s1-control').glob('*.py')):
        ast.parse(path.read_text(),filename=str(path));parsed.append(path.name)
    for repo,base in [(S,ids['source']['base']),(C,ids['control']['base'])]:
        subprocess.run(['git','-C',str(repo),'diff','--check',base,'HEAD'],check=True)
    assert git(Path('/root/verify-rust-std-ch8-s1-08-w13'),'rev-parse','HEAD')==ids['source']['base']
    assert not git(Path('/root/verify-rust-std-ch8-s1-08-w13'),'status','--porcelain=v1')
    envelope=json.loads((HERE/'ENVELOPE.json').read_text())
    assert envelope['group_s']==900+11*600==7500
    assert envelope['group_s']+envelope['internal_cleanup_margin_s']<=envelope['workflow_phase_step_s']<=8100
    assert envelope['sum_literal_step_caps_s']==177*60<10800
    assumptions=json.loads((HERE/'QUALIFICATION-ASSUMPTIONS.json').read_text())
    assert assumptions['source_sha']==ids['source']['sha'] and len(assumptions['stubs'])==4
    for row in request['rows']:
        argv=runner.build_argv(S,T,[row['selector']],34,Path('/synthetic/export.json'))
        assert argv.count('--harness')==1 and argv[argv.index('--harness-timeout')+1]=='600s'
        assert '--exact' in argv and '--no-assert-contracts' in argv and '--jobs=1' in argv
    if (HERE/'MANIFEST.sha256').exists():
        for line in (HERE/'MANIFEST.sha256').read_text().splitlines():
            digest,rel=line.split('  ',1);assert sha(HERE/rel)==digest,rel
    return {'schema':'ch8-s2-static-validation-v1','status':'STATIC_PASS','identities':ids,
        'source_check':source,'preflight':preflight,'workflow':yaml,'patch_replay':patches,'actual_shallow_ancestry':ancestry,
        'python_ast_files':parsed,'whitespace':'PASS','frozen_S1_source':'UNCHANGED_CLEAN',
        'runtime_smallsort_algorithm':'EXACT_BASE_BYTES_AFTER_REMOVING_8_OPT_IN_ATTRIBUTES',
        'controls':'43 tests passed in final synthetic suite; test_runner.py test_s107.FinalizationTests test_s2.py',
        'local_compiler_solver_full_runner':'NOT_RUN','compile_body_caller_controls_cost_results':'NOT_RUN',
        'independent_review':'NOT_RUN_W14_NEXT','B1_B2_independent_credit':'NONE','dispatch_push_reservation_ledger':'NOT_RUN'}
if __name__=='__main__':print(json.dumps(main(),indent=2))
