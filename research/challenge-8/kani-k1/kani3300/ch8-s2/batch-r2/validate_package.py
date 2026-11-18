#!/usr/bin/env python3
# Copyright Kani Contributors
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Offline static/package preflight only; never compiles, runs the full runner or dispatches."""
import ast
import hashlib
import json
import os
from pathlib import Path
import re
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
    assert len(chain)==depth and endpoint in chain
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
    S=Path(ids['source']['worktree']);C=Path(ids['control']['worktree']);T=Path('/root/kani-upstream-ch8-s1');Q=C/'ch8-s1-control'
    W=Path('/root/kani-ch8-s2-diagnostics-w11')
    for label,repo in [('source',S),('control',C),('tool',T)]:
        assert git(repo,'rev-parse','HEAD')==ids[label]['sha']
        assert git(repo,'rev-parse','HEAD^{tree}')==ids[label]['tree']
        assert not git(repo,'status','--porcelain=v1'),label
    assert git(S,'rev-parse','HEAD^')==ids['source']['parent']
    assert git(C,'rev-parse','HEAD^')==ids['control']['parent']=='9e14e033f9ee31522b571c127609dcdff76d230b'
    assert git(W,'rev-parse','HEAD')==ids['control']['diagnostics_reference']=='b678fb6cdd5edf69a4e952167422f36a45a3d6cb'
    assert not git(W,'status','--porcelain=v1')
    assert git(G,'merge-base','--is-ancestor',ids['entry_g0'],'HEAD')==''
    sys.path.insert(0,str(Q))
    import runner,cfg_pfc,s2_policy,check_package
    request=runner.load_request()
    for name,rel in [('CI-REQUEST.json','ch8-s1-control/CI-REQUEST.json'),('WORKFLOW.yml','.github/workflows/ch8-s2.yml')]:
        assert (HERE/name).read_bytes()==(C/rel).read_bytes()
    assert sha(HERE/'CI-REQUEST.json')==ids['control']['request_sha256']
    assert sha(HERE/'WORKFLOW.yml')==ids['control']['workflow_sha256']
    for name in ('cfg_pfc.py','test_cfg_pfc.py','rustc_diagnostics.py','test_rustc_diagnostics.py','s2_policy.py'):
        assert (HERE/name).read_bytes()==(Q/name).read_bytes()
    for rel,digest in ids['source']['files'].items():assert sha(S/rel)==digest,rel
    source=runner.verify_source(S,T,request)
    assert s2_policy.validate_source(S,request)
    matrix=cfg_pfc.check(S,request)
    assert matrix==json.loads((HERE/'CFG-PFC-MAP.json').read_text())
    assert len(matrix['rows'])==11
    assert not any(x['target'].endswith('::sort8_stable') for x in matrix['checked_active_slice_uses'])
    assert sum(x['required_cover_count'] for x in request['rows'])==20
    assert sum(x['expected']=='DETECTED' for x in request['rows'])==6
    assert request['rows'][4]['assurance']=='DIAGNOSTIC_ASSUMED'
    assert json.loads((HERE/'MODEL-MAP.json').read_text())['consumers']==['general32_assumed','general32_weak']
    old=json.loads(git(W,'show','HEAD:ch8-s1-control/CI-REQUEST.json'))
    allowed={'entry_g0','std_sha','std_tree','source_bindings','rows','changed_file_sha256','cfg_pfc_source_sha256','ci_changed_paths','ci_payload_sha256'}
    assert request.keys()==old.keys()
    changed=[k for k in request if old[k]!=request[k]]
    assert set(changed)<=allowed,changed
    for a,b in zip(old['rows'],request['rows']):
        a=json.loads(json.dumps(a));b=json.loads(json.dumps(b))
        if 'oracle' in a:
            assert a['oracle'].pop('source_sha256')=='207f05964330722a66a98212fa8801b6baf9d2c55ba7cd608ae73d80d69fd5e2'
            b['oracle'].pop('source_sha256')
        assert a==b
    for name,a in old['source_bindings'].items():
        b=request['source_bindings'][name]
        assert {k:v for k,v in a.items() if k!='sha256'}=={k:v for k,v in b.items() if k!='sha256'}
    old_source=Path('/root/verify-rust-std-ch8-s2-cfg-r1-w13')
    assert (Q/'fixtures/s2-r1-batch.rs.txt').read_bytes()==(old_source/s2_policy.BATCH).read_bytes()
    assert sha(Q/'fixtures/s2-r1-batch.rs.txt')=='207f05964330722a66a98212fa8801b6baf9d2c55ba7cd608ae73d80d69fd5e2'
    assert git(S,'diff','--name-only',ids['source']['derivation_source'],'HEAD')==s2_policy.BATCH
    # Every original root body/signature is exactly retained. Replacements live outside roots.
    def roots(text):
        _,items=cfg_pfc.items(text)
        return {x['head'][cfg_pfc.kind(x,'fn')][0]:x for x in items if cfg_pfc.kind(x,'fn') is not None}
    a=roots((old_source/s2_policy.BATCH).read_text());b=roots((S/s2_policy.BATCH).read_text())
    bound=json.loads((HERE/'ROOT-BINDINGS.json').read_text())
    for row in bound:
        name=row['id']
        assert a[name]['body']==b[name]['body'] and a[name]['head']==b[name]['head']
        assert hashlib.sha256(cfg_pfc.spelling(b[name]['body']).encode()).hexdigest()==row['body_tokens_sha256']
    invariance=json.loads((HERE/'RUNNER-INVARIANCE.json').read_text())
    for item in invariance['files']:
        rel=item['file'];assert sha(W/rel)==item['reference_sha256'] and sha(C/rel)==item['candidate_sha256']
        if rel.endswith('/runner.py'):
            assert (W/rel).read_text().replace(ids['source']['derivation_source'],ids['source']['sha']).replace('64d96010b0b4b896322e26d700c253f834ba9fd6',ids['source']['tree'])==(C/rel).read_text()
        else:assert (W/rel).read_bytes()==(C/rel).read_bytes()
    diffs=json.loads((HERE/'CHANGED-FILES.json').read_text())
    assert git(C,'diff','--name-only',ids['control']['diagnostics_reference'],'HEAD').splitlines()==[x['path'] for x in diffs['control_vs_W11']]
    for item in diffs['control_vs_W11']:assert sha(C/item['path'])==item['sha256']
    fixture=json.loads((Q/'S2-SOURCE.json').read_text())
    for rel,text in fixture.items():assert (S/rel).read_text()==text,rel
    extra=json.loads((HERE/'COMPILED-ITEMS-MAP.json').read_text())
    actual=[]
    V=S/'library/core/src/slice/sort/shared/smallsort/verify'
    for path in sorted(V.rglob('*.rs')):
        rel=str(path.relative_to(S));assert sha(path)==extra['source_sha256'][rel]
        toks=cfg_pfc.tokens(path.read_text())
        if any(t=='stub_verified' for t,_ in toks):actual.append(rel)
        assert 'stub_verified(sort8_stable)' not in cfg_pfc.spelling(toks)
        if rel!=s2_policy.BATCH:assert path.read_bytes()==(old_source/rel).read_bytes()
    assert actual==extra['all_verified_use_files']
    assert len(extra['outside_primary_gate'])==6
    for item in extra['outside_primary_gate']:
        proof=item['matching_pfc'];text=(S/proof['file']).read_text()
        assert 'proof_for_contract' in text.splitlines()[proof['attribute_line']-1]
        if 'macro' in proof:
            assert proof['macro']+'!(\n    '+proof['invocation']+',' in text
    os.environ.update(GITHUB_REPOSITORY='Tiramisu-Cake/kani',GITHUB_EVENT_NAME='push',
        GITHUB_REF='refs/heads/uninit-ci/ch8-s2-batch3probes-offline-r2',GITHUB_RUN_ATTEMPT='1',GITHUB_SHA=ids['control']['sha'])
    preflight=check_package.control(C)
    patches=[]
    for item in json.loads((HERE/'PATCHES.json').read_text()):
        repo=S if item['path'].startswith('SOURCE-') else C
        assert sha(HERE/item['path'])==item['sha256']
        patches.append(replay(repo,item['base'],HERE/item['path'],item['target_tree']))
    ancestry=[shallow(C,ids['control']['sha'],7,ids['tool']['sha']),shallow(S,ids['source']['sha'],5,ids['source']['base']),shallow(T,ids['tool']['sha'],2,ids['tool']['sha'])]
    provenance=json.loads((HERE/'TEST-PROVENANCE.json').read_text())
    assert git(S,'rev-parse',provenance['execution_source_sha']+'^{tree}')==ids['source']['tree']
    stage=provenance['execution_control_sha']
    stage_paths=git(C,'diff','--name-only',stage,'HEAD').splitlines()
    assert stage_paths==provenance['stage_to_final_control_changes']
    stage_runner=git(C,'show',stage+':ch8-s1-control/runner.py')+'\n'
    assert stage_runner.replace(provenance['execution_source_sha'],ids['source']['sha'])==(Q/'runner.py').read_text()
    stage_request=json.loads(git(C,'show',stage+':ch8-s1-control/CI-REQUEST.json'))
    assert [k for k in request if request[k]!=stage_request[k]]==['std_sha','ci_payload_sha256']
    assert ids['package_readiness']=='DRAFT_AWAITING_APPROVED_W11_CORRECTION'
    assert ids['known_runner_review']['verdict']=='CHANGES_REQUIRED'
    parsed=[]
    for path in sorted(Q.glob('*.py')):ast.parse(path.read_text(),filename=str(path));parsed.append(path.name)
    for repo,base in [(S,ids['source']['base']),(C,ids['control']['base'])]:subprocess.run(['git','-C',str(repo),'diff','--check',base,'HEAD'],check=True)
    for row in request['rows']:
        argv=runner.build_argv(S,T,[row['selector']],34,Path('/synthetic/export.json'))
        assert argv.count('--harness')==1 and argv[argv.index('--harness-timeout')+1]=='600s'
        assert '--exact' in argv and '--no-assert-contracts' in argv and '--jobs=1' in argv
    envelope=json.loads((HERE/'ENVELOPE.json').read_text())
    assert envelope['group_s']==900+11*600==7500
    assert envelope['group_s']+envelope['internal_cleanup_margin_s']<=envelope['workflow_phase_step_s']<=8100
    assert envelope['sum_literal_step_caps_s']==177*60<10800
    assert json.loads((HERE/'QUALIFICATION-ASSUMPTIONS.json').read_text())['source_sha']==ids['source']['sha']
    tests=(HERE/'TARGETED-TESTS.txt').read_text();fallback=(HERE/'FALLBACK-TESTS.txt').read_text()
    assert 'Ran 72 tests' in tests and tests.endswith('\nOK\n')
    assert 'Ran 3 tests' in fallback and fallback.endswith('\nOK\n')
    names=lambda text:set(re.findall(r'^(test_\S+ \([^\n]+\)) \.\.\. ok$',text,re.M))
    w11=(HERE.with_name('runner-diagnostics-r2')/'TARGETED-TESTS.txt').read_text()
    assert len(names(w11))==29 and names(w11)<=names(tests+fallback)
    # Frozen old candidates and task inputs are never rewritten.
    frozen=[('/root/verify-rust-std-ch8-s2-cfg-r1-w13',ids['source']['derivation_source']),('/root/kani-ch8-s2-cfg-r1-w13',ids['control']['baseline']),('/root/verify-rust-std-ch8-s2-batch-w13','97ac4d39d7f959ea70b1f57785ffd1fd66ecd22a')]
    for repo,head in frozen:
        assert git(repo,'rev-parse','HEAD')==head and not git(repo,'status','--porcelain=v1')
    if (HERE/'MANIFEST.sha256').exists():
        listed=[]
        for line in (HERE/'MANIFEST.sha256').read_text().splitlines():
            digest,rel=line.split('  ',1);assert sha(HERE/rel)==digest,rel;listed.append(rel)
        assert set(listed)=={str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and p.name!='MANIFEST.sha256'}
    return {'schema':'ch8-s2-combined-r2-static-validation-v1','state':'STATIC_PASS_DRAFT_NOT_READY','identities':ids,
        'roots':11,'covers':20,'exact_negatives':6,'root_bodies_signatures_assertions_covers':'EXACT_RETAINED',
        'request_changed_fields_vs_W11':changed,'cfg_pfc_map':matrix,'supplemental_compiled_uses':6,
        'runner_invariance':'EXACT_W11_IMPLEMENTATION_PLUS_TWO_SOURCE_LITERAL_REBINDS',
        'preflight':preflight,'patch_replay':patches,'actual_shallow_ancestry':ancestry,
        'targeted_tests':72,'fallback_tests':3,'original_W11_tests_included':29,'test_execution_provenance':provenance,'GO':'BLOCKED_W11_B01_B02_AND_COMBINED_REVIEW14','python_ast_files':parsed,
        'source_check':source,'old_candidates':'PRESERVED_CLEAN','native_compile_model_production_retention':'NOT_RUN',
        'historical_actual_cause':'UNKNOWN','independent_review14':'PENDING_EXACT_COMMITTED_COMBINED_PACKAGE',
        'closed_proof_obligations':0,'proof_credit':'NONE','external_actions':'NO_CI_PUSH_PR_CANCEL_LEDGER_RESERVATION_OR_BUDGET_CHANGE'}
if __name__=='__main__':print(json.dumps(main(),indent=2))
