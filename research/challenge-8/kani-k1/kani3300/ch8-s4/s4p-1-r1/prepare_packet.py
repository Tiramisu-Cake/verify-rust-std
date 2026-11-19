"""Prepare current repair packet and independently replay complete patch trees."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,tempfile
MAIN=Path('/root/verify-rust-std-kani3300-g0')
BASE=MAIN/'research/challenge-8/kani-k1'
OLD=BASE/'kani3300/ch8-s4/s4p-1'
OUT=BASE/'kani3300/ch8-s4/s4p-1-r1'
CONTROL=Path('/root/kani-ch8-s4p-1-r1-control-w13')
SOURCE=Path('/root/verify-rust-std-ch8-s4p-1-w13');TOOL=Path('/root/kani-upstream-ch8-s1')
TASK='989b0dbd020bc9bb500c0a18f3220d21537fbc44'
AUTHOR='590dd6360f5b4c92eab9fff30aa0d2e7d8d942ce'
REVIEW='4856a87f39d2606adbbed747d3cae9a73fb80d52'
E941='e941155517a02f67ea9bac1adb81c1d5f6f85638'
D=lambda b:hashlib.sha256(b).hexdigest()
def git(repo,*args):return subprocess.check_output(['git','-C',str(repo),*args])
def text(repo,*args):return git(repo,*args).decode().strip()
def put(name,data):
    (OUT/name).parent.mkdir(parents=True,exist_ok=True)
    (OUT/name).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
def read(name):return json.loads((OLD/name).read_text())
r=json.loads((CONTROL/'ch8-s1-control/CI-REQUEST.json').read_text())
assert text(CONTROL,'show','-s','--format=%P','HEAD')==r['control_parent']
assert not text(CONTROL,'status','--porcelain=v1')
ctrl=text(CONTROL,'rev-parse','HEAD');ctree=text(CONTROL,'rev-parse','HEAD^{tree}')
assert ctrl=='2db5d2c08804036d283cb36450647cd584ee9e10'
for name in ('SOURCE-PRESERVATION.json','SOURCE-CITATIONS.json','ROOTS.json','ROLE-ORACLE-COVER.json','DOMAIN-UNWIND.json','RESOURCE.json','OPEN-OBLIGATIONS.json'):
    shutil.copyfile(OLD/name,OUT/name)
shutil.copyfile(BASE/'kani3300/ch8-s4/s4p-1-gate-repair-inputs/INPUTS.json',OUT/'INPUTS.json')
shutil.copyfile(CONTROL/'ch8-s1-control/CI-REQUEST.json',OUT/'CI-REQUEST.json')
shutil.copyfile(CONTROL/'.github/workflows/ch8-s2.yml',OUT/'WORKFLOW.yml')
shutil.copyfile('/tmp/s4p1_r1_targeted.py',OUT/'tests/run_targeted.py')
shutil.copyfile('/tmp/s4p1_r1_preflight.py',OUT/'run_preflight.py')
shutil.copyfile('/tmp/s4p1_r1_final.py',OUT/'execute_final_validate.py')
patches=[]
for item in read('PATCHES.json'):
    repo=SOURCE if item['file'].startswith('SOURCE-') else CONTROL
    tip=r['std_sha'] if repo==SOURCE else ctrl
    tree=r['std_tree'] if repo==SOURCE else ctree
    data=git(repo,'diff','--binary','--full-index',item['base'],tip)
    path=OUT/item['file'];path.write_bytes(data)
    with tempfile.TemporaryDirectory(prefix='s4p1-r1-replay-') as directory:
        env={**os.environ,'GIT_INDEX_FILE':directory+'/index'}
        subprocess.run(['git','-C',str(repo),'read-tree',item['base']],env=env,check=True)
        subprocess.run(['git','-C',str(repo),'apply','--cached','--whitespace=nowarn',str(path)],env=env,check=True)
        replay=subprocess.check_output(['git','-C',str(repo),'write-tree'],env=env,text=True).strip()
        assert replay==tree
    patches.append({'file':path.name,'sha256':D(data),'base':item['base'],'tip':tip,'expected_tree':tree,'replayed_tree':replay,'status':'EXACT_TREE_PASS','native_compile':'NOT_RUN'})
put('PATCHES.json',patches)
(OUT/'CONTROL-REPAIR.patch').write_bytes(git(CONTROL,'diff','--binary','--full-index',E941,ctrl))
identities={};shallow=[]
for label,repo,tip,depth,required in [('source',SOURCE,r['std_sha'],5,[r['std_sha'],r['source_parent'],r['base_std_sha']]),
        ('control',CONTROL,ctrl,7,[ctrl,r['control_parent'],r['tool_sha']]),
        ('tool',TOOL,r['tool_sha'],2,[r['tool_sha'],'3e095c22a231de1d7acd2410b71f0fc8e6970c19'])]:
    assert text(repo,'rev-parse','HEAD')==tip and not text(repo,'status','--porcelain=v1')
    tree=text(repo,'rev-parse',tip+'^{tree}')
    with tempfile.TemporaryDirectory(prefix='s4p1-r1-shallow-') as directory:
        dest=Path(directory)/'clone'
        subprocess.run(['git','clone','--quiet','--no-checkout','--single-branch','--depth='+str(depth),'file://'+str(repo),str(dest)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
        assert text(dest,'rev-parse','HEAD')==tip and text(dest,'rev-parse','HEAD^{tree}')==tree
        for commit in required:assert text(dest,'cat-file','-t',commit)=='commit'
        assert text(dest,'show','-s','--format=%P','HEAD').split()==text(repo,'show','-s','--format=%P',tip).split()
    identity={'repo':str(repo),'sha':tip,'tree':tree,'parents':text(repo,'show','-s','--format=%P',tip).split(),
        'clean':True,'depth':depth,'author_committer':text(repo,'show','-s','--format=%an <%ae>%n%cn <%ce>',tip)}
    if label!='tool':
        identity.update(reference='f1bdf11902252ad1178f42403c253ae710fecbaf' if label=='source' else 'd675ef70dc1ada13330efc0990c2e1d6b0d21a5a',sole_parent=r[label+'_parent'])
    identities[label]=identity
    shallow.append({'repo':str(repo),'depth':depth,'sha':tip,'tree':tree,'required_commits_available':required,'status':'SHALLOW_IDENTITY_PASS'})
put('ANCESTRY.json',{'shallow':shallow,'patch_trees':6,'future_trigger':'NONSKIP SAME-TREE SIBLING finalcontrol sole9e14; coordinator only, not created or published'})
delta=text(CONTROL,'diff','--name-only',E941,ctrl).splitlines()
allowed=['ch8-s1-control/'+name for name in ('CI-REQUEST.json','s4p_campaign.py','s4p_contract_stacks.py','s4p_validate.py','test_s4p_gate_repair.py')]
assert delta==sorted(allowed),delta
oldrequest=json.loads(git(CONTROL,'show',E941+':ch8-s1-control/CI-REQUEST.json'))
assert set(k for k in r if r[k]!=oldrequest[k])=={'ci_payload_sha256','ci_changed_paths'}
def entries(commit):
    result={}
    for line in git(CONTROL,'ls-tree','-r','-z',commit).split(b'\0'):
        if not line:continue
        meta,path=line.split(b'\t',1);result[path.decode()]=meta.decode()
    return result
before_entries,after_entries=entries(E941),entries(ctrl)
assert set(after_entries)-set(before_entries)=={'ch8-s1-control/test_s4p_gate_repair.py'}
assert not set(before_entries)-set(after_entries)
protected={}
for path,meta in before_entries.items():
    if path in delta:continue
    assert after_entries[path]==meta
    if path.startswith(('ch8-s1-control/','.github/workflows/')):
        assert meta.split()[1]=='blob'
        protected[path]=D(git(CONTROL,'show',ctrl+':'+path))
preserve=read('CONTROL-PRESERVATION.json');preserve.update(current=ctrl,changed_paths=text(CONTROL,'diff','--name-only',preserve['reference'],ctrl).splitlines())
preserve.update(repair_reference=E941,repair_delta_paths=delta,all_other_e941_tree_entries_byte_identical=True,
    protected_e941_payload_bytes=protected,request_changed_fields=['ci_changed_paths','ci_payload_sha256'],
    old_profile_gates_readers_runtime_suites_fixtures_and_lexer_cache='EXACT_BYTE_IDENTICAL_TO_E941',
    new_validate_selection='test_s4p_gate_repair added; all existing selections byte-preserved')
put('CONTROL-PRESERVATION.json',preserve)
deps=read('DEPENDENCIES.json')
for commit,relative in [(TASK,'TASK-CH8-S4P1-GATE-FIX-W13.md'),(TASK,'TASK-CH8-S4P1-GATE-DELTA-W14.md'),
        (TASK,'kani3300/ch8-s4/s4p-1-gate-repair-inputs/INPUTS.json'),
        (AUTHOR,'kani3300/ch8-s4/s4p-1/MANIFEST.sha256'),
        (REVIEW,'kani3300/ch8-s4/s4p-1-review/MANIFEST.sha256'),(REVIEW,'kani3300/ch8-s4/s4p-1-review/REVIEW.md'),
        (REVIEW,'kani3300/ch8-s4/s4p-1-review/FINDINGS.json'),(REVIEW,'kani3300/ch8-s4/s4p-1-review/reproduce_schema.py')]:
    path='research/challenge-8/kani-k1/'+relative
    raw=git(MAIN,'show',commit+':'+path)
    assert (MAIN/path).read_bytes()==raw
    deps['entries'].append({'repo':str(MAIN),'commit':commit,'path':path,'sha256':D(raw)})
deps['repair_task']=TASK;deps['independent_review']=REVIEW
put('DEPENDENCIES.json',deps)
history=[]
for commit,directory in [(AUTHOR,OLD),(REVIEW,BASE/'kani3300/ch8-s4/s4p-1-review')]:
    relative=str(directory.relative_to(MAIN));files=text(MAIN,'ls-tree','-r','--name-only',commit,relative).splitlines()
    bindings={}
    for path in files:
        raw=git(MAIN,'show',commit+':'+path);assert raw==(MAIN/path).read_bytes();bindings[path]=D(raw)
    for line in (directory/'MANIFEST.sha256').read_text().splitlines():
        sha,name=line.split('  ',1);assert D((directory/name).read_bytes())==sha
    history.append({'commit':commit,'path':relative,'files':len(files),'manifest_sha256':D((directory/'MANIFEST.sha256').read_bytes()),'all_committed_bytes_unchanged':True,'bindings':bindings})
frozen=read('PINS.json')
assert text(Path(frozen['control']['repo']),'rev-parse','HEAD')==E941
assert not text(Path(frozen['control']['repo']),'status','--porcelain=v1')
assert identities['source']==frozen['source'] and identities['tool']==frozen['tool']
put('HISTORY-PRESERVATION.json',{'frozen_packets':history,'old_control':frozen['control'],
    'old_final_validate':frozen['offline_validation'],'historical_precursors':'Old PRECURSORS.json and all stdout/stderr byte-preserved in original immutable packet; reviewer harness failures also retained unchanged',
    'new_repair_targeted_01':{'exit_code':0,'tests':3,'unittest_reported_seconds':20.972,'wall_timing':'NOT_MEASURED','request_at_execution':frozen['request']['sha256'],'scope':'uncommitted repair code before payload refresh; not final Validate'},
    'expected_nonzero_reviewer_reproducer':'tests/review-reproducer.json; expected first missing-schema rejection, not an omitted failure',
    'historical_records_relabelled':False,'download_verified_changed':False})
put('PRECURSORS.json',{'historical':'HISTORY-PRESERVATION.json; immutable old packets retained with all old failures',
    'repair_targeted':['tests/targeted-01.stderr','tests/targeted-02.json','tests/targeted-02.stderr'],
    'expected_rejection_reproducer':'tests/review-reproducer.json','repair_full_validate_before_final':0,'failures_discarded':False})
provenance=read('PROVENANCE.json');provenance.update(identities)
provenance.update(request_sha256=D((OUT/'CI-REQUEST.json').read_bytes()),workflow_sha256=D((OUT/'WORKFLOW.yml').read_bytes()),
    payload=r['ci_payload_sha256'],changed_paths=r['ci_changed_paths'],deleted_paths=r['ci_deleted_paths'],
    frozen_author=AUTHOR,independent_review=REVIEW,repair_task=TASK,repair_reference=E941,repair_delta_paths=delta,
    repair_patch_sha256=D((OUT/'CONTROL-REPAIR.patch').read_bytes()),native_start='NOT_RUN; native tools never invoked')
put('PROVENANCE.json',provenance)
sys.path.insert(0,str(CONTROL/'ch8-s1-control'))
import s4p_validate,s3_validate,s32_validate,s34_validate
loader=__import__('unittest').defaultTestLoader
def ids(suite):
    for item in suite:
        if isinstance(item,__import__('unittest').TestSuite):yield from ids(item)
        else:yield item.id()
selected=list(ids(loader.loadTestsFromNames(s4p_validate.NEW)));assert len(selected)==38
# Preserve the original driver lists exactly; only S4 NEW receives this module.
lists=read('TEST-LIST.json');lists['suites']['s4p']=list(s4p_validate.NEW)
lists['new_expanded_tests']=selected;lists['total_new_tests']=38
lists['repair_tests']=[x for x in selected if x.startswith('test_s4p_gate_repair.')]
lists['all_new_test_modules_wired']=True
put('TEST-LIST.json',lists)
pins=frozen.copy();pins.update(identities)
pins.update(schema='ch8-s4p-1-repair-pins-v1',status='FINAL_VALIDATE_RUNNING',repair_task=TASK,
    frozen_author=AUTHOR,independent_review=REVIEW,repair_reference=E941,
    request={**frozen['request'],'sha256':D((OUT/'CI-REQUEST.json').read_bytes()),'workflow_sha256':D((OUT/'WORKFLOW.yml').read_bytes()),'payload_files':len(r['ci_payload_sha256'])},
    offline_validation='FINAL-VALIDATE.json RUNNING; do not treat as PASS',
    independent14='SAME14_DELTA_PENDING; separate existing CURRENT14 session, no subagent',
    GO='NOT_AUTHORIZED',g0_delivery_commit='REPORTED_EXTERNALLY; excluded from selfhash loop')
put('PINS.json',pins)
put('CHECKPOINT.json',{'status':'FINAL_VALIDATE_RUNNING','repair_task':TASK,**identities,
    'request_sha256':pins['request']['sha256'],'new_proof_credit':'NONE','next':'Wait for exact final Validate; seal packet, root check, SAME14 delta, rootGO request only',
    'open':['SAME14 independent closure of R14-01/02','Root recheck and GO request','All native/proof/fit/MIR/B1/B2 obligations'],'actual_future_head_ref_run':'UNKNOWN'})
(OUT/'CURRENT-TASK.md').write_text('# W13 S4P1 gate repair\n\nExact task '+TASK+'. High/FastOFF/no subagents or model changes.\nOriginal implementation constraints retained. Repair only R14-01/02; source/tool unchanged.\nFinal Validate is running; final disposition will be sealed in CHECKPOINT/HANDOFF.\n')
print(json.dumps({'status':'PACKET_PREPARED_PENDING_FINAL_VALIDATE','source':r['std_sha'],'control':ctrl,'control_tree':ctree,'tool':r['tool_sha'],'six_patch_trees':'PASS','shallow_depths':[5,7,2],'repair_delta_paths':delta,'selected_s4p_tests':len(selected)}),flush=True)
