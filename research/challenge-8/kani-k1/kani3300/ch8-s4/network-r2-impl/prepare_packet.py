"""Exact Git/hash/static packet, isolated patch replay and shallow local clones."""
from pathlib import Path
import ast,hashlib,json,os,shutil,subprocess,sys,tempfile,unittest
OUT=Path(__file__).resolve().parent;MAIN=Path('/root/verify-rust-std-kani3300-g0')
S=Path('/root/verify-rust-std-ch8-s4p-2-w13');C=Path('/root/kani-ch8-s4p-2-r1-control-w13');T=Path('/root/kani-upstream-ch8-s1');H=C/'ch8-s1-control'
SP='c12867b1e651a3927cbd9f169fe2c3d3728a44c3';CP='4059c900e50ba179d824a1e6f6bd7798cf343e36'
D=lambda b:hashlib.sha256(b).hexdigest()
def git(repo,*args):return subprocess.check_output(['git','-C',str(repo),*args])
def text(repo,*args):return git(repo,*args).decode().strip()
def put(name,v):(OUT/name).write_text(json.dumps(v,indent=2)+'\n')
r=json.loads((H/'CI-REQUEST.json').read_text());pins={}
for label,repo,parent,depth,required in [('source',S,SP,6,[SP,r['base_std_sha']]),('control',C,CP,8,[CP,r['tool_sha']]),('tool',T,'3e095c22a231de1d7acd2410b71f0fc8e6970c19',2,['3e095c22a231de1d7acd2410b71f0fc8e6970c19'])]:
    sha=text(repo,'rev-parse','HEAD');tree=text(repo,'rev-parse','HEAD^{tree}')
    assert not text(repo,'status','--porcelain=v1') and text(repo,'show','-s','--format=%P','HEAD')==parent
    with tempfile.TemporaryDirectory(prefix='network-r2-shallow-') as d:
        dest=Path(d)/'clone'
        subprocess.run(['git','clone','--quiet','--no-checkout','--single-branch','--depth='+str(depth),'file://'+str(repo),str(dest)],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        assert text(dest,'rev-parse','HEAD')==sha and text(dest,'rev-parse','HEAD^{tree}')==tree
        assert text(dest,'show','-s','--format=%P','HEAD')==parent
        for item in required:assert text(dest,'cat-file','-t',item)=='commit'
    pins[label]={'repo':str(repo),'sha':sha,'tree':tree,'sole_parent':parent,'clean':True,'checkout_depth':depth,'required_commits_available':required,
        'shallow':'PASS','author_committer':text(repo,'show','-s','--format=%an <%ae>%n%cn <%ce>','HEAD')}
assert r['std_sha']==pins['source']['sha'] and r['std_tree']==pins['source']['tree']
assert r['tool_sha']==pins['tool']['sha'] and r['tool_tree']==pins['tool']['tree']
patches=[]
for label,repo,parent,stock in [('SOURCE',S,SP,r['base_std_sha']),('CONTROL',C,CP,r['tool_sha'])]:
    for tag,base in [('PARENT',parent),('STOCK',stock)]:
        data=git(repo,'diff','--binary','--full-index',base,'HEAD');name=label+'-'+tag+'.patch';(OUT/name).write_bytes(data)
        with tempfile.TemporaryDirectory(prefix='network-r2-index-') as d:
            env={**os.environ,'GIT_INDEX_FILE':d+'/index'}
            subprocess.run(['git','-C',str(repo),'read-tree',base],check=True,env=env)
            subprocess.run(['git','-C',str(repo),'apply','--cached','--whitespace=nowarn',str(OUT/name)],check=True,env=env)
            actual=subprocess.check_output(['git','-C',str(repo),'write-tree'],env=env,text=True).strip()
        assert actual==pins[label.lower()]['tree']
        patches.append({'file':name,'base':base,'tip':pins[label.lower()]['sha'],'sha256':D(data),'expected_tree':actual,'replayed_tree':actual,'status':'EXACT_TREE_PASS'})
put('PATCHES.json',patches)
leaf='library/core/src/slice/sort/shared/smallsort/verify/sorting_s4_network_r2.rs';verify='library/core/src/slice/sort/shared/smallsort/verify.rs'
assert text(S,'diff','--name-only',SP,'HEAD').splitlines()==sorted([leaf,verify])
oldverify=git(S,'show',SP+':'+verify);newverify=(S/verify).read_bytes()
assert newverify==oldverify+b'\n// S4P2 r2 concrete actual-call slices; old partitions remain unchanged.\n#[cfg(all(kani, kani_smallsort_sorting, kani_smallsort_s2_assumed, kani_smallsort_s3_leaf, kani_smallsort_s4_partition))]\npub(super) mod sorting_s4_network_r2;\n'
oldfiles=set(text(C,'ls-tree','-r','--name-only',CP).splitlines());files=set(text(C,'ls-tree','-r','--name-only','HEAD').splitlines());changed=set(text(C,'diff','--name-only',CP,'HEAD').splitlines())
allowed={'ch8-s1-control/CI-REQUEST.json','ch8-s1-control/runner.py','ch8-s1-control/check_package.py','ch8-s1-control/collect.py','.github/workflows/ch8-s2.yml'}
assert not oldfiles-files and changed&oldfiles==allowed
added=files-oldfiles
assert all(x.startswith(('ch8-s1-control/s4p2r2_','ch8-s1-control/test_s4p2r2','ch8-s1-control/S4P2R2-')) or x in ('ch8-s1-control/fixtures/s4p2-request.json','ch8-s1-control/fixtures/s4p2-workflow.yml') for x in added)
# Independently invert only new dispatch branches/tuple membership and require
# byte equality with the original shared runtime. No execution logic may differ.
def invert_dispatch(data,filename):
    lines=data.splitlines(True);out=[];i=0
    while i<len(lines):
        line=lines[i];strip=line.strip()
        if filename=='collect.py' and strip=='import s4p2r2_profile':i+=4;continue
        if "if request.get('profile')=='ch8-s4p-2r2-" in line:i+=2;continue
        if filename=='check_package.py' and '=="ch8-s4p-2r2-network' in line:i+=1;continue
        if strip=="if request.get('schema')=='ch8-s4p-2r2-v1':":i+=3;continue
        if strip.startswith('if request.get("schema")=="ch8-s4p-2r2-v1":'):
            i+=1 if ':import' in line else 3 if 'import s4p2r2_profile' in lines[i+1] else 2;continue
        out.append(line.replace(', "ch8-s4p-2r2-v1"','').replace(",'ch8-s4p-2r2-v1'",''));i+=1
    return ''.join(out)
for filename in ('runner.py','check_package.py','collect.py'):
    rel='ch8-s1-control/'+filename
    assert invert_dispatch((C/rel).read_text(),filename).encode()==git(C,'show',CP+':'+rel),filename
    (OUT/(Path(filename).stem.upper()+'-DISPATCH.patch')).write_bytes(git(C,'diff','--full-index',CP,'HEAD','--',rel))
oldreq=json.loads(git(C,'show',CP+':ch8-s1-control/CI-REQUEST.json'))
assert r['rows'][:4]==oldreq['rows'][:4] and r['flags']==oldreq['flags'] and r['budgets']==oldreq['budgets']
assert (H/'fixtures/s4p2-request.json').read_bytes()==git(C,'show',CP+':ch8-s1-control/CI-REQUEST.json')
assert (H/'fixtures/s4p2-workflow.yml').read_bytes()==git(C,'show',CP+':.github/workflows/ch8-s2.yml')
# Native campaign/acceptance code is copied only by namespace; no new semantics.
def namespace(s):return s.replace('s4p2_','s4p2r2_').replace('ch8-s4p-2','ch8-s4p-2r2').replace('S4P2-','S4P2R2-').replace('S4P2_N_','S4P2R2_N_')
assert (H/'s4p2r2_campaign.py').read_text()==namespace((H/'s4p2_campaign.py').read_text())
for name in ('expected_observation','validate_roles'):
    def body(path):
        source=path.read_text();tree=ast.parse(source);item=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name==name);return ast.dump(item,include_attributes=False)
    assert body(H/'s4p2r2_policy.py')==body(H/'s4p2_policy.py'),name
unchanged={rel:D((C/rel).read_bytes()) for rel in sorted(oldfiles-allowed) if rel.startswith('ch8-s1-control/')}
put('PRESERVATION.json',{'source_parent':SP,'source_delta':[verify,leaf],'all_other_source_tree_entries_identical':True,
    'kernel_model_contract_old_harness':'BYTE_IDENTICAL','control_parent':CP,'modified_existing_control':sorted(allowed),'new_control_paths':sorted(added),
    'protected_old_control_sha256':unchanged,'all_other_control_entries_identical':True,'shared_runtime_inverse_dispatch':'EXACT_BYTE_PASS',
    'new_campaign':'EXACT_NAMESPACE_COPY','native_acceptance_and_role_matcher_AST':'UNCHANGED',
    'negative_rows_bindings_expectations':'BYTE_EQUAL','flags_resource_caps':'UNCHANGED',
    'checkout_depth':'new control8 required to retain stock-tool ancestor after one additional generation; old profiles stay7; new source6 likewise retains historical patch-base ancestor; tool2 unchanged'})
for name,src in [('CI-REQUEST.json',H/'CI-REQUEST.json'),('WORKFLOW.yml',C/'.github/workflows/ch8-s2.yml')]:shutil.copyfile(src,OUT/name)
deps=[]
plan=r['s4p2r2_inputs']['plan'];review=r['s4p2r2_inputs']['plan_review']
for commit,root in [(plan,'research/challenge-8/kani-k1/kani3300/ch8-s4/network-r2-offline-plan'),(review,'research/challenge-8/kani-k1/kani3300/ch8-s4/network-r2-offline-plan-review'),(r['entry_g0'],'research/challenge-8/kani-k1/kani3300/ch8-s4/network-r2-impl/CURRENT-TASK.md')]:
    for rel in text(MAIN,'ls-tree','-r','--name-only',commit,root).splitlines():
        data=git(MAIN,'show',commit+':'+rel);assert (MAIN/rel).read_bytes()==data
        deps.append({'commit':commit,'path':rel,'sha256':D(data),'bytes':len(data),'git_blob':text(MAIN,'rev-parse',commit+':'+rel)})
put('DEPENDENCIES.json',deps)
sys.path.insert(0,str(H));import runner,s4p2r2_validate as v,s4p2r2_profile as p,s3_validate,s32_validate,s34_validate,s4p_validate,s4p2_validate
request=runner.load_request();assert request==r
for key in ('changed_file_sha256','cfg_pfc_source_sha256','ordinary_contract_source_sha256','contract_stack_source_sha256','lexical_source_sha256'):
    for rel,sha in r[key].items():assert D((S/rel).read_bytes())==sha
assert text(C,'diff','--name-only',r['tool_sha'],'HEAD').splitlines()==r['ci_changed_paths']
assert text(C,'diff','--diff-filter=D','--name-only',r['tool_sha'],'HEAD').splitlines()==r['ci_deleted_paths']
assert set(r['ci_payload_sha256'])==set(r['ci_changed_paths'])-set(r['ci_deleted_paths'])-{'ch8-s1-control/CI-REQUEST.json'}
for rel,sha in r['ci_payload_sha256'].items():assert D((C/rel).read_bytes())==sha
for label in ('source','control'):
    assert pins[label]['author_committer']=='Tiramisu-Cake <igkharin@gmail.com>\nTiramisu-Cake <igkharin@gmail.com>'
    assert '[skip ci]' in text(S if label=='source' else C,'show','-s','--format=%B','HEAD')
def testids(suite):
    for item in suite:
        if isinstance(item,unittest.TestSuite):yield from testids(item)
        else:yield item.id()
selected=list(testids(unittest.defaultTestLoader.loadTestsFromNames(v.NEW)));assert len(selected)==22 and not any('_FailedTest' in t for t in selected)
put('TEST-LIST.json',{'old_suites':{'legacy':s3_validate.LEGACY,'s3':('test_s3','test_s3_repair','test_s3_paths'),'s32':s32_validate.NEW,'bridge1':s34_validate.NEW,'s4p':s4p_validate.NEW,'s4p2':s4p2_validate.NEW},
    'old_test_counts':{'legacy':136,'s3':56,'s32':35,'bridge1':40,'s4p':38,'s4p2':39},'all344_old_tests_selected':True,
    'new_suites':v.NEW,'new_tests':selected,'new_test_count':22,'prepared_total':366,'entry':'s4p2r2_validate.py; workflow executes this exact entry after control gate',
    'full_final_validate':'NOT_RUN'})
put('ROOTS.json',{'rows':r['rows'],'source_bindings':r['source_bindings'],'domains':r['domains'],'unwind':p.BOUNDS,
    'source_positive_assertions':16,'source_positive_covers':[6,6,6,3],'native_property_counts':'UNKNOWN','producer_ids':'UNKNOWN_UNTIL_SAME_INVOCATION_INVENTORY','proof_credit':'NONE'})
put('RESOURCE.json',{'caps':p.CAPS,'budgets':r['budgets'],'flags':r['flags'],'slot_envelope_seconds':6180,'campaign_reserve_seconds':720,
    'cost_fit':'UNKNOWN_NOT_RUN','validate_deadline_seconds':1080,'validate_margin_required':1.5,'validate_maximum_elapsed_for_margin_seconds':720,
    'strict_peak_memory_assurance':'NOT_ESTABLISHED; unchanged sampled-PGID/owned-census semantics'})
pins.update(schema='network-r2-impl-pins-v1',status='READY_FOR_EXACT_PACKAGE_REVIEW_FINAL_VALIDATE_PREPARED_NOT_RUN',
    plan=plan,plan_review=review,authority=r['entry_g0'],request_sha256=D((H/'CI-REQUEST.json').read_bytes()),workflow_sha256=D((OUT/'WORKFLOW.yml').read_bytes()),
    profile=r['profile'],schema_request=r['schema'],payload_files=len(r['ci_payload_sha256']),GO='NOT_GRANTED',publication='NOT_PERFORMED',native_CI='NOT_RUN',proof_credit='NONE')
put('PINS.json',pins)
put('FINAL-VALIDATE-PREPARED.json',{'status':'PREPARED_NOT_RUN','execution_count':0,'control_sha':pins['control']['sha'],'control_tree':pins['control']['tree'],
    'request_sha256':pins['request_sha256'],'workflow_sha256':pins['workflow_sha256'],'cwd':str(H),'deadline_seconds':1080,'margin_required':1.5,
    'maximum_elapsed_seconds_for_margin':720,'command':['timeout','--signal=TERM','--kill-after=10s','1080s','env','PYTHONDONTWRITEBYTECODE=1','python3','s4p2r2_validate.py'],
    'checks_before_execution':['Exact control HEAD/tree/request/payload/workflow hashes and clean checkout must equal PINS.json','Separate coordinator authorization required; this file is preparation only'],
    'success_requires':['All366 selected tests pass','No timeout; exit0','margin_at_18_minutes>=1.5 on these exact committed bytes'],
    'measured_elapsed_seconds':None,'measured_margin':None,'result':'NOT_RUN; no historical timing transferred; do not run as part of this stage'})
print(json.dumps({'status':pins['status'],'source':pins['source']['sha'],'control':pins['control']['sha'],'patch_trees':len(patches),'shallow_depths':[6,8,2],'selected_tests':366}),flush=True)
