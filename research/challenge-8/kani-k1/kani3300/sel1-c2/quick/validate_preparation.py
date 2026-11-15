#!/usr/bin/env python3
"""Unbound A/B/Q checks (aa9074c6f5); for finalized Q use validate_bound.py."""
from pathlib import Path
import ast,hashlib,json,subprocess
import yaml
ROOT=Path(__file__).resolve().parent.parent
BASE='8e299aa6243bc5f06a29c51e98aafa9564478220'
W='/root/kani-fix-3300-sel1-c2-w15'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(repo,*args):return subprocess.check_output(['git','-C',str(repo),*args])
def load(p):return json.loads(p.read_text())
summary={}
for stage in ['quick','gatea','replay']:
    root=ROOT/stage;full=root/'full-export';inv=load(root/'TEMPLATE-INVENTORY.json');meta=load(root/'LOCAL-CI.json')
    assert inv['source_binding_finalized'] is False
    assert sha(root/'ci-only-template.patch')==inv['ci_patch_sha256']
    for rel,digest in inv['files'].items():assert sha(root/rel)==digest,rel
    for p in full.rglob('*.py'):ast.parse(p.read_text(),filename=str(p))
    for p in full.rglob('*.json'):load(p)
    workflows=list((full/'.github/workflows').glob('*.yml'));assert len(workflows)==1
    workflow=yaml.load(workflows[0].read_text(),Loader=yaml.BaseLoader)
    assert set(workflow['on'])=={'workflow_dispatch'}
    assert all('false &&' in job['if'] for job in workflow['jobs'].values())
    changed=git(W,'diff','--name-only',BASE,meta['commit']).decode().splitlines()
    assert all(p.startswith(('.github/workflows/','.github/c2-slices/','scripts/kani3300-gate/','scripts/kani3300-replay/')) for p in changed)
    assert git(W,'merge-base',BASE,meta['commit']).decode().strip()==BASE
    subprocess.run(['git','-C',W,'diff','--check',BASE,meta['commit'],'--','.',':(glob,exclude)**/*.patch'],check=True)
    for p in full.rglob('*'):
        if p.is_file():assert git(W,'show',meta['commit']+':'+str(p.relative_to(full)))==p.read_bytes(),str(p)
    live=git(W,'ls-tree','-r','--name-only',meta['commit'],'--','.github/workflows').decode().splitlines()
    assert live==[str(workflows[0].relative_to(full))]
    summary[stage]={'template_files':len(inv['files']),'ci_sha':meta['commit'],'binding_finalized':False,'workflow':'manual, fork-only, disabled','status':'PASS_STATIC_ONLY'}
# Gate A uses accepted receipt observer with only identity/state edits.
a=ROOT/'gatea/full-export';bind=load(a/'scripts/kani3300-gate/binding.json')
assert len(bind['stages'])==33 and bind['state']=='PENDING_FREEZE'
assert all(x=='PENDING_SOURCE_SHA256' for x in bind['files'].values())
assert all(x=='PENDING_SOURCE_OBJECT' for x in bind['subtrees'].values())
y=(a/'.github/workflows/kani3300-sel1-c2-gatea.yml').read_text()
for text in ['path: control','path: export','working-directory: export','--source-dir ../export','max-parallel: 3','timeout-minutes: 360','fail-fast: false','os: [ubuntu-24.04, ubuntu-24.04-arm, macos-15]']:assert text in y,text
ref='/root/kani-fix-3300-c2-gatea';ac='39bcdd7ad51dc169f75a9974e43717205553bad0'
for name in ['receipt.py','lifecycle.py','test_receipt.py','test_lifecycle.py']:
    old=git(ref,'show',ac+':scripts/kani3300-gate/'+name).decode()
    expected=old.replace('ad499e41dd2db9ccd432f89721638a1f3a0bbd44','PENDING_SEL1_FREEZE_SHA').replace('9829702c1aa0ecb73c860fc0ad5451757917d6cb','PENDING_SEL1_FREEZE_TREE').replace('C2_FROZEN','SEL1_C2_FROZEN')
    assert (a/'scripts/kani3300-gate'/name).read_text()==expected
# Replay: std patch and all five files are independently tied to the exact std test commit.
b=ROOT/'replay/full-export/scripts/kani3300-replay';req=load(b/'CI-REQUEST.json')
std=load(ROOT.parent/'sel1/STD-OVERLAY.json')
assert sha(b/'sel1-test-only.patch')==std['patches_sha256']['std-test-only.patch']==req['test_patch_sha256']
repo='/root/verify-rust-std-kani3300-sel1-swap'
assert git(repo,'rev-parse',std['commit']+'^{tree}').decode().strip()==std['tree']
changed=set(git(repo,'diff','--name-only',std['frozen_std'],std['commit'],'--','library').decode().splitlines())
assert changed==set(std['files_sha256'])
for p,digest in std['files_sha256'].items():assert hashlib.sha256(git(repo,'show',std['commit']+':'+p)).hexdigest()==digest
assert req['patched_file_sha256']==std['files_sha256']
rows=req['roots'];assert len(rows)==len({r['selector'] for r in rows})==6
assert [r['id'] for r in rows]==['merge-raw-closure-on','merge-profile-closure-on','sort4-closure-on','swap-if-less-closure-on','raw-legal-on','raw-negative-on']
assert [r['source_unwind'] for r in rows]==[34,34,16,8,16,16]
assert [r['expected_failed_checks'] for r in rows]==[0,0,0,0,0,1]
assert [r['required_covers'] for r in rows]==[5,2,3,6,2,None]
assert req['run_budget']['aggregate_job_envelope_seconds']==21600
for r in rows:
    argv=r['argv'];assert argv[argv.index('--harness')+1]==r['selector'] and '--exact' in argv
    assert '--no-assert-contracts' in argv and 'uninit-checks' in argv
    assert r['environment']['RUSTFLAGS']=='--cfg kani_smallsort_controls'
# Quick: retain all inherited selectors/directives/ignores, then add 29.
q=ROOT/'quick/full-export/.github/c2-slices';manifest=load(q/'test-manifest.json')
old= json.loads(git('/root/kani-fix-3300-c2-slices-w15','show','8288537e7c57b04d2462ff0c5bf1af38ab9d4451:.github/c2-slices/test-manifest.json'))
def inventory(d):return {(g['suite'],g['mode'],r['selector']):r for g in d['groups'] for r in g['selectors']}
previous=inventory(old);current=inventory(manifest);assert len(previous)==471 and len(current)==500
for k,r in previous.items():
    now=current[k];assert now['existing_path_ignore']==r['existing_path_ignore']
    assert [(f['path'],f['original_directives']) for f in now['files']]==[(f['path'],f['original_directives']) for f in r['files']]
for p in ['structural-manifest.json','structural-mixed.rs','structural_compare.py']:
    assert (q/p).read_bytes()==git('/root/kani-fix-3300-c2-slices-w15','show','8288537e7c57b04d2462ff0c5bf1af38ab9d4451:.github/c2-slices/'+p)
config=load(q/'inputs.json');assert sha(q/'test-manifest.json')==config['test_manifest_sha256']
assert sha(q/'sensitivity-manifest.json')==config['sensitivity']['manifest_sha256']
assert config['source_sha']=='PENDING_SEL1_FREEZE_SHA' and config['source_parent']==BASE
summary['std_test_only_identity']='PASS_EXACT_GIT_OBJECTS_5_TEST_FILES_PRODUCTION_UNCHANGED'
print(json.dumps(summary,indent=2,sort_keys=True))
