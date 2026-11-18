import hashlib,json,os,subprocess,tempfile
from pathlib import Path
G0=Path('/root/verify-rust-std-kani3300-g0')
REL='research/challenge-8/kani-k1/kani3300/ch8-s3/'
OUT=G0/REL/'s3-1-review-r1';PKG=G0/REL/'s3-1-r1'
PACKAGE='0902ad2d84e5e5c4d9bb3b01d5c7f7671e84b38d'
OLD='e8a8e5328a941af8a07b778122604b0c9bf4579b';REVIEW='610dcd6858415792050a9aba7e0d7859afd7d727'
def git(repo,*args,env=None):return subprocess.check_output(['git','-C',str(repo),*args],env=env)
def sha(b):return hashlib.sha256(b).hexdigest()
def save(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():assert path.read_bytes()==data,path
    else:path.write_bytes(data)
def jfile(name):return json.loads((PKG/name).read_text())
record={'schema':'independent14-delta-input-audit-v1','package':PACKAGE,'checks':{}}
files=git(G0,'ls-tree','-r','--name-only',PACKAGE,'--',REL+'s3-1-r1/').decode().splitlines()
for name in files:
    data=git(G0,'show',PACKAGE+':'+name);assert (G0/name).read_bytes()==data,name
    save(OUT/'inputs/package'/Path(name).name,data)
manifest=(PKG/'MANIFEST.sha256').read_text().splitlines()
for line in manifest:
    h,name=line.split('  ',1);assert sha((PKG/name).read_bytes())==h,name
record['checks']['package_files_manifest']={'files':len(files),'manifest_entries':len(manifest),'status':'MATCH'}
for directory,commit in [('s3-1',OLD),('s3-1-review',REVIEW)]:
    names=git(G0,'ls-tree','-r','--name-only',commit,'--',REL+directory+'/').decode().splitlines()
    for name in names:assert (G0/name).read_bytes()==git(G0,'show',commit+':'+name),name
    record['checks'][directory+'_immutable']={'files':len(names),'commit':commit,'status':'MATCH'}
for name in ('REPORT.md','FINDINGS.json','tests/test_review14.py'):
    save(OUT/'inputs/frozen-review'/name,git(G0,'show',REVIEW+':'+REL+'s3-1-review/'+name))
save(OUT/'inputs/TASK-CH8-S3-1-CONTROL-DELTA-W14.md',(G0/'research/challenge-8/kani-k1/TASK-CH8-S3-1-CONTROL-DELTA-W14.md').read_bytes())
pins=jfile('PINS.json')
for role in ('source','control','tool'):
    pin=pins[role];repo=Path(pin['worktree'])
    assert git(repo,'rev-parse','HEAD').decode().strip()==pin['sha']
    assert git(repo,'rev-parse','HEAD^{tree}').decode().strip()==pin['tree']
    assert git(repo,'show','-s','--format=%P','HEAD').decode().strip()==pin['parent']
    assert not git(repo,'status','--porcelain=v1')
    record['checks'][role]={'sha':pin['sha'],'tree':pin['tree'],'parent':pin['parent'],'clean':True}
control=Path(pins['control']['worktree']);request=jfile('CI-REQUEST.json')
assert (PKG/'CI-REQUEST.json').read_bytes()==(control/'ch8-s1-control/CI-REQUEST.json').read_bytes()
assert sha((PKG/'CI-REQUEST.json').read_bytes())==pins['request_sha256']
assert (PKG/'WORKFLOW.yml').read_bytes()==(control/'.github/workflows/ch8-s2.yml').read_bytes()
assert sha((PKG/'WORKFLOW.yml').read_bytes())==pins['workflow_sha256']
assert git(control,'show','1dfc267b66abd83d536eb41a17052a4f3d767d2b:.github/workflows/ch8-s2.yml')==(PKG/'WORKFLOW.yml').read_bytes()
for key,repo in [('ci_payload_sha256',control),('changed_file_sha256',Path(pins['source']['worktree']))]:
    for name,h in request[key].items():assert sha((repo/name).read_bytes())==h,(key,name)
record['checks']['request_workflow_payloads']='MATCH'
for name in ('ROOT-BINDINGS.json','ROLE-COVER-MAP.json','DOMAIN-UNWIND.json','PROVIDER-DAG.json','U-SITE-PROPOSAL.json','FULL-OBLIGATIONS.md'):
    assert (PKG/name).read_bytes()==git(G0,'show',OLD+':'+REL+'s3-1/'+name),name
record['checks']['six_frozen_maps']='EXACT_BYTES_MATCH'
patches=[]
for patch in jfile('PATCHES.json'):
    assert sha((PKG/patch['patch']).read_bytes())==patch['sha256']
    with tempfile.TemporaryDirectory() as d:
        env=dict(os.environ,GIT_INDEX_FILE=d+'/index')
        git(control,'read-tree',patch['base'],env=env)
        git(control,'apply','--cached','--whitespace=nowarn',str(PKG/patch['patch']),env=env)
        actual=git(control,'write-tree',env=env).decode().strip();assert actual==patch['tree']
        patches.append({'patch':patch['patch'],'tree':actual,'status':'EXACT_TREE_MATCH'})
record['checks']['patches']=patches
for chain,role in zip(jfile('ANCESTRY.json'),('control','source','tool')):
    actual=git(pins[role]['worktree'],'rev-list','--first-parent','--max-count='+str(chain['depth']),chain['head']).decode().splitlines()
    assert actual==chain['chain'],role
record['checks']['ancestry']='7/5/2 MATCH'
final=jfile('FINAL-VALIDATE.json');validation=jfile('VALIDATION.json')
assert final==validation['final']
for name,key in [('run_final_validate.py','script_sha256'),('FINAL-VALIDATE.stdout.txt','stdout_sha256'),('FINAL-VALIDATE.stderr.txt','stderr_sha256')]:assert sha((PKG/name).read_bytes())==final[key]
assert final['control_sha']==pins['control']['sha'] and final['control_tree']==pins['control']['tree']
assert final['request_sha256']==pins['request_sha256'] and final['workflow_sha256']==pins['workflow_sha256']
assert (final['monotonic_end_ns']-final['monotonic_start_ns'])/1e9==final['elapsed_seconds']
assert final['margin']==1080/final['elapsed_seconds'] and final['margin']>=1.5
assert final['execution_count']==1 and all(x['exit_code']==0 for x in final['commands_executed'])
assert validation['test_summary']['legacy_tests']==136 and validation['test_summary']['s3_tests']==46
assert 'Ran 136 tests' in (PKG/'FINAL-VALIDATE.stderr.txt').read_text() and 'Ran 46 tests' in (PKG/'FINAL-VALIDATE.stderr.txt').read_text()
record['checks']['author_final_validate']={'tests':182,'elapsed_seconds':final['elapsed_seconds'],'margin':final['margin'],'receipt_and_transcript':'MATCH','independently_rerun':False}
record['checks']['delta_paths']=git(control,'diff','--name-only','1dfc267b66abd83d536eb41a17052a4f3d767d2b',pins['control']['sha']).decode().splitlines()
precursors=[]
for name in ('targeted.stdout.txt','targeted.stderr.txt'):
    path=OUT/'tests'/name;precursors.append({'path':'tests/'+name,'bytes':path.stat().st_size,'sha256':sha(path.read_bytes()),'classification':'INTERRUPTED PRECURSOR','final_evidence':False})
save(OUT/'PRECURSORS.json',(json.dumps({'state':'INTERRUPTED PRECURSOR','reason':'Owner00:33 /new14: prior attempt cancelled by root; background terminal stopped. Transcript may contain completed individual checks but is not final evidence.','files':precursors},indent=2)+'\n').encode())
save(OUT/'INPUT-AUDIT.json',(json.dumps(record,indent=2)+'\n').encode())
print(json.dumps(record,indent=2))
