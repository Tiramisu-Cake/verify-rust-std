"""Read-only packet hashes, exact Git identities and prepared gates; never Validate."""
from pathlib import Path
import hashlib,json,subprocess,sys
OUT=Path(__file__).resolve().parent
D=lambda b:hashlib.sha256(b).hexdigest()
def read(name):return json.loads((OUT/name).read_text())
def git(repo,*args):return subprocess.check_output(['git','-C',str(repo),*args],text=True).strip()
manifest=read('MANIFEST.json');files={str(p.relative_to(OUT)) for p in OUT.rglob('*') if p.is_file() and p.name!='MANIFEST.json'}
assert files==set(manifest['files']) and not any(p.is_symlink() for p in OUT.rglob('*'))
for name,rec in manifest['files'].items():
    data=(OUT/name).read_bytes();assert D(data)==rec['sha256'] and len(data)==rec['bytes'],name
pins=read('PINS.json');r=read('CI-REQUEST.json');C=Path(pins['control']['repo']);H=C/'ch8-s1-control';S=Path(pins['source']['repo'])
for label in ('source','control','tool'):
    p=pins[label];repo=Path(p['repo'])
    assert git(repo,'rev-parse','HEAD')==p['sha'] and git(repo,'rev-parse','HEAD^{tree}')==p['tree']
    assert git(repo,'show','-s','--format=%P','HEAD')==p['sole_parent']
    assert not git(repo,'status','--porcelain=v1')
assert (H/'CI-REQUEST.json').read_bytes()==(OUT/'CI-REQUEST.json').read_bytes()
assert pins['request_sha256']==D((OUT/'CI-REQUEST.json').read_bytes())
assert (C/'.github/workflows/ch8-s2.yml').read_bytes()==(OUT/'WORKFLOW.yml').read_bytes()
assert pins['workflow_sha256']==D((OUT/'WORKFLOW.yml').read_bytes())
assert git(C,'diff','--name-only',r['tool_sha'],'HEAD').splitlines()==r['ci_changed_paths']
assert git(C,'diff','--diff-filter=D','--name-only',r['tool_sha'],'HEAD').splitlines()==r['ci_deleted_paths']
assert set(r['ci_payload_sha256'])==set(r['ci_changed_paths'])-set(r['ci_deleted_paths'])-{'ch8-s1-control/CI-REQUEST.json'}
for rel,sha in r['ci_payload_sha256'].items():assert D((C/rel).read_bytes())==sha,rel
for key in ('changed_file_sha256','cfg_pfc_source_sha256','ordinary_contract_source_sha256','contract_stack_source_sha256','lexical_source_sha256'):
    for rel,sha in r[key].items():assert D((S/rel).read_bytes())==sha,rel
for item in read('PATCHES.json'):
    assert D((OUT/item['file']).read_bytes())==item['sha256']
    assert item['expected_tree']==item['replayed_tree']==pins['source' if item['file'].startswith('SOURCE') else 'control']['tree']
for item in read('DEPENDENCIES.json'):
    data=subprocess.check_output(['git','-C','/root/verify-rust-std-kani3300-g0','show',item['commit']+':'+item['path']])
    assert D(data)==item['sha256'] and len(data)==item['bytes']
sys.path.insert(0,str(H));import runner,s4p3_profile as profile,s4p3_policy as policy,s4p3_domain as domain,check_package
assert runner.load_request()==r;profile.validate(r);assert policy.validate_roles(S,r);domain.check(S)
workflow=check_package.check_yaml(C/'.github/workflows/ch8-s2.yml');assert workflow['checkout_depths']=={'control':9,'export':7,'tool':2}
for name,control in [('tests/targeted-final.json',True),('tests/old-targeted-final.json',False)]:
    result=read(name);assert result['exit_code']==0 and result['control_sha']==pins['control']['sha']
    if control:assert result['control_tree']==pins['control']['tree'] and result['request_sha256']==pins['request_sha256']
preflight=read('PREFLIGHT.json');assert preflight['status']=='STATIC_PASS' and preflight['request_sha256']==pins['request_sha256']
assert preflight['cfg_projections']==64 and preflight['legacy_contexts']==32 and preflight['ACTIVE_contexts']==8
assert read('CONTROL-GATE.json')['report']['control_sha']==pins['control']['sha']
prepared=read('FINAL-VALIDATE-PREPARED.json')
assert prepared['status']=='PREPARED_NOT_RUN' and prepared['execution_count']==0
assert prepared['control_sha']==pins['control']['sha'] and prepared['control_tree']==pins['control']['tree']
assert prepared['request_sha256']==pins['request_sha256'] and prepared['workflow_sha256']==pins['workflow_sha256']
assert prepared['deadline_seconds']==1080 and prepared['margin_required']==1.5 and prepared['maximum_elapsed_seconds_for_margin']==720
assert prepared['measured_elapsed_seconds'] is None and prepared['measured_margin'] is None
assert read('TEST-LIST.json')['prepared_total']==389 and read('CHECKPOINT.json')['status']=='HANDOFF'
assert pins['GO']=='NOT_GRANTED' and pins['native_CI']=='NOT_RUN' and pins['proof_credit']=='NONE'
print(json.dumps({'status':'PACKET_HASH_PIN_PASS','files':len(files),'payload_hashes':len(r['ci_payload_sha256']),
    'source':pins['source']['sha'],'control':pins['control']['sha'],'tests':'23 new +30 existing targeted PASS;389 final PREPARED_NOT_RUN',
    'patch_trees':4,'shallow_depths':[7,9,2],'final_validate_execution_count':0,'proof_credit':'NONE'}),flush=True)
