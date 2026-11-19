"""Read-only final packet identity/manifests check. Never native, CI, push or ledger."""
from pathlib import Path
import hashlib,json,subprocess,sys
OUT=Path(__file__).resolve().parent
D=lambda b:hashlib.sha256(b).hexdigest()
read=lambda name:json.loads((OUT/name).read_text())
def git(repo,*args):return subprocess.check_output(['git','-C',str(repo),*args],text=True).strip()
manifest=read('MANIFEST.json');files={str(p.relative_to(OUT)) for p in OUT.rglob('*') if p.is_file() and p.name!='MANIFEST.json'}
assert files==set(manifest['files'])
assert not any(p.is_symlink() for p in OUT.rglob('*'))
for name,rec in manifest['files'].items():
    path=OUT/name;raw=path.read_bytes();assert D(raw)==rec['sha256'] and len(raw)==rec['bytes'],name
pins=read('PINS.json');request=read('CI-REQUEST.json');control=Path(pins['control']['repo']);source=Path(pins['source']['repo'])
assert pins['status']=='READY_FOR_ROOT_FULLPIN_CHECK_AND_W14_EXACT_PACKAGE_REVIEW_NOT_GO'
for role in ('source','control','tool'):
    item=pins[role];repo=Path(item['repo'])
    assert git(repo,'rev-parse','HEAD')==item['sha']
    assert git(repo,'rev-parse','HEAD^{tree}')==item['tree']
    assert git(repo,'show','-s','--format=%P','HEAD')==item['sole_parent']
    assert not git(repo,'status','--porcelain=v1')
assert pins['request']['sha256']==D((OUT/'CI-REQUEST.json').read_bytes())
assert (OUT/'CI-REQUEST.json').read_bytes()==(control/'ch8-s1-control/CI-REQUEST.json').read_bytes()
assert (OUT/'WORKFLOW.yml').read_bytes()==(control/'.github/workflows/ch8-s2.yml').read_bytes()
assert pins['request']['workflow_sha256']==D((OUT/'WORKFLOW.yml').read_bytes())
assert git(control,'diff','--name-only',request['tool_sha'],'HEAD').splitlines()==request['ci_changed_paths']
assert git(control,'diff','--diff-filter=D','--name-only',request['tool_sha'],'HEAD').splitlines()==request['ci_deleted_paths']
assert set(request['ci_payload_sha256'])==set(request['ci_changed_paths'])-set(request['ci_deleted_paths'])-{'ch8-s1-control/CI-REQUEST.json'}
for rel,sha in request['ci_payload_sha256'].items():assert D((control/rel).read_bytes())==sha,rel
for key in ('changed_file_sha256','ordinary_contract_source_sha256','cfg_pfc_source_sha256','contract_stack_source_sha256','lexical_source_sha256'):
    for rel,sha in request[key].items():assert D((source/rel).read_bytes())==sha,rel
sys.path.insert(0,str(control/'ch8-s1-control'));import runner,s4p2_profile,s4p2_policy
s4p2_profile.validate(request);assert runner.load_request()==request
patches=read('PATCHES.json');assert len(patches)==6
for item in patches:
    assert D((OUT/item['file']).read_bytes())==item['sha256']
    assert item['expected_tree']==item['replayed_tree']==pins['source' if item['file'].startswith('SOURCE') else 'control']['tree']
final=read('FINAL-VALIDATE.json');summary=json.loads((OUT/'FINAL-VALIDATE.stdout').read_text().splitlines()[-1])
assert final['status']=='PASS' and final['exit_code']==0 and not final['timed_out'] and final['clean_after']
assert final['execution_count']==1 and final['control_sha']==pins['control']['sha'] and final['control_tree']==pins['control']['tree']
assert final['request_sha256']==pins['request']['sha256']==read('PREFLIGHT.json')['request_sha256']
assert final['limit_seconds']==1080 and final['margin_at_18_minutes']>=1.5
assert summary['success'] and summary['failures']==summary['errors']==0
assert summary['test_counts']=={'legacy':136,'s3':56,'s32':35,'bridge1':40,'s4p':38,'s4p2':39}
for suffix in ('stdout','stderr'):assert final[suffix]['sha256']==D((OUT/('FINAL-VALIDATE.'+suffix)).read_bytes())
assert pins['proof_credit']=='NONE' and pins['native_compile_proof_cost_fit']=='NOT_RUN' and pins['GO']=='NOT_GRANTED'
print(json.dumps({'status':'PACKET_HASH_AND_FULLPIN_PASS','files':len(files),'source':pins['source']['sha'],
    'control':pins['control']['sha'],'tool':pins['tool']['sha'],'tests':sum(summary['test_counts'].values()),
    'elapsed_seconds':final['elapsed_seconds'],'margin':final['margin_at_18_minutes'],'native_CI_push_GO':'NOT_RUN_NOT_GRANTED'}),flush=True)
