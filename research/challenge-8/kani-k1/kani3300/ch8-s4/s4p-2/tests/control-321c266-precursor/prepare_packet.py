"""Prepare exact offline package, six full-tree patch replays and shallow identities."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,tempfile
MAIN=Path('/root/verify-rust-std-kani3300-g0');BASE=MAIN/'research/challenge-8/kani-k1'
OUT=Path(__file__).resolve().parent
SOURCE=Path('/root/verify-rust-std-ch8-s4p-2-w13');CONTROL=Path('/root/kani-ch8-s4p-2-control-w13');TOOL=Path('/root/kani-upstream-ch8-s1')
TASK='bf3aba53618b759a11d3ff277e88ba66530ec708';PLAN='7253272c427eb9b564c79350ef73b231fa124298';REVIEW='e287943e116a102d5950295b2629d80a62d1f922'
SREF='985062ebad90cee1e2846b1648cd6a8624d146f6';CREF='2db5d2c08804036d283cb36450647cd584ee9e10'
SP='97ac4d39d7f959ea70b1f57785ffd1fd66ecd22a';CP='9e14e033f9ee31522b571c127609dcdff76d230b'
D=lambda b:hashlib.sha256(b).hexdigest()
def git(repo,*args):return subprocess.check_output(['git','-C',str(repo),*args])
def text(repo,*args):return git(repo,*args).decode().strip()
def put(name,data):(OUT/name).write_text(json.dumps(data,indent=2)+'\n')
def read(path):return json.loads(path.read_text())
request=read(CONTROL/'ch8-s1-control/CI-REQUEST.json');std=request['std_sha'];ctrl=text(CONTROL,'rev-parse','HEAD');tool=request['tool_sha']
identities={};shallow=[]
for label,repo,tip,parent,depth,required in [
 ('source',SOURCE,std,SP,5,[std,SP,request['base_std_sha']]),
 ('control',CONTROL,ctrl,CP,7,[ctrl,CP,tool]),
 ('tool',TOOL,tool,'3e095c22a231de1d7acd2410b71f0fc8e6970c19',2,[tool,'3e095c22a231de1d7acd2410b71f0fc8e6970c19'])]:
    assert text(repo,'rev-parse','HEAD')==tip and not text(repo,'status','--porcelain=v1')
    assert text(repo,'show','-s','--format=%P',tip)==parent
    tree=text(repo,'rev-parse',tip+'^{tree}')
    with tempfile.TemporaryDirectory(prefix='s4p2-shallow-') as d:
        dest=Path(d)/'clone'
        subprocess.run(['git','clone','--quiet','--no-checkout','--single-branch','--depth='+str(depth),'file://'+str(repo),str(dest)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
        assert text(dest,'rev-parse','HEAD')==tip and text(dest,'rev-parse','HEAD^{tree}')==tree
        for commit in required:assert text(dest,'cat-file','-t',commit)=='commit'
        assert text(dest,'show','-s','--format=%P','HEAD')==parent
    identities[label]={'repo':str(repo),'sha':tip,'tree':tree,'sole_parent':parent,'clean':True,'depth':depth,
        'author_committer':text(repo,'show','-s','--format=%an <%ae>%n%cn <%ce>',tip)}
    shallow.append({'role':label,'depth':depth,'sha':tip,'tree':tree,'required_commits_available':required,'status':'SHALLOW_IDENTITY_PASS'})
assert identities['source']['tree']==request['std_tree'] and identities['tool']['tree']==request['tool_tree']
patches=[]
for role,repo,tip,parent,ref,stock in [('SOURCE',SOURCE,std,SP,SREF,request['base_std_sha']),('CONTROL',CONTROL,ctrl,CP,CREF,tool)]:
    for tag,base in [('PARENT',parent),('DELTA',ref),('STOCK',stock)]:
        data=git(repo,'diff','--binary','--full-index',base,tip);path=OUT/(role+'-'+tag+'.patch');path.write_bytes(data)
        expected=text(repo,'rev-parse',tip+'^{tree}')
        with tempfile.TemporaryDirectory(prefix='s4p2-replay-') as d:
            env={**os.environ,'GIT_INDEX_FILE':d+'/index'}
            subprocess.run(['git','-C',str(repo),'read-tree',base],env=env,check=True)
            subprocess.run(['git','-C',str(repo),'apply','--cached','--whitespace=nowarn',str(path)],env=env,check=True)
            actual=subprocess.check_output(['git','-C',str(repo),'write-tree'],env=env,text=True).strip()
        assert actual==expected
        patches.append({'file':path.name,'base':base,'tip':tip,'sha256':D(data),'expected_tree':expected,'replayed_tree':actual,'status':'EXACT_TREE_PASS','native_compile':'NOT_RUN'})
put('PATCHES.json',patches);put('ANCESTRY.json',{'shallow':shallow,'patch_trees':6,'future_trigger':'NONSKIP SAME-TREE SIBLING of final control, sole9e14; not created or published'})
leaf='library/core/src/slice/sort/shared/smallsort/verify/sorting_s4_network_partition.rs';verify='library/core/src/slice/sort/shared/smallsort/verify.rs'
sdelta=text(SOURCE,'diff','--name-only',SREF,std).splitlines();assert sdelta==sorted([leaf,verify])
oldverify=git(SOURCE,'show',SREF+':'+verify);newverify=(SOURCE/verify).read_bytes();assert newverify.startswith(oldverify)
assert newverify[len(oldverify):]==b'\n// S4P2 exact network singletons and N0..1; no assumed replacements.\n#[cfg(all(kani, kani_smallsort_sorting, kani_smallsort_s2_assumed, kani_smallsort_s3_leaf, kani_smallsort_s4_partition))]\npub(super) mod sorting_s4_network_partition;\n'
oldrequest=read(Path('/root/kani-ch8-s4p-1-r1-control-w13/ch8-s1-control/CI-REQUEST.json'))
protected_source={}
for rel in oldrequest['changed_file_sha256']:
    if rel==verify:continue
    before=git(SOURCE,'show',SREF+':'+rel);assert (SOURCE/rel).read_bytes()==before;protected_source[rel]=D(before)
put('SOURCE-PRESERVATION.json',{'reference':SREF,'reference_tree':text(SOURCE,'rev-parse',SREF+'^{tree}'),'current':identities['source'],
    'sole_parent':SP,'delta_paths':sdelta,'all_other_baseline_tree_entries_identical':True,'old_verify_prefix_exact':True,
    'protected_source_sha256':protected_source,'new_leaf_sha256':D((SOURCE/leaf).read_bytes()),
    'kernel_contracts_models_and_all_old_harness_bytes':'EXACT_BYTE_PRESERVED','proof_credit':'NONE'})
cdelta=text(CONTROL,'diff','--name-only',CREF,ctrl).splitlines()
allowed={'ch8-s1-control/CI-REQUEST.json','ch8-s1-control/runner.py','ch8-s1-control/check_package.py','ch8-s1-control/collect.py','.github/workflows/ch8-s2.yml'}
oldfiles=set(text(CONTROL,'ls-tree','-r','--name-only',CREF).splitlines());newfiles=set(text(CONTROL,'ls-tree','-r','--name-only',ctrl).splitlines())
assert not oldfiles-newfiles
assert set(cdelta)&oldfiles==allowed
assert all(x.startswith('ch8-s1-control/s4p2_') or x.startswith('ch8-s1-control/test_s4p2') or x.startswith('ch8-s1-control/S4P2-') or x in ('ch8-s1-control/fixtures/s4p-request.json','ch8-s1-control/fixtures/s4p-workflow.yml') for x in newfiles-oldfiles)
unchanged={}
for rel in sorted(oldfiles-allowed):
    assert git(CONTROL,'rev-parse',CREF+':'+rel)==git(CONTROL,'rev-parse',ctrl+':'+rel)
    if rel.startswith('ch8-s1-control/'):
        unchanged[rel]=D((CONTROL/rel).read_bytes())
for rel in ('ch8-s1-control/runner.py','ch8-s1-control/check_package.py','ch8-s1-control/collect.py'):
    (OUT/(Path(rel).stem.upper()+'-DISPATCH.patch')).write_bytes(git(CONTROL,'diff','--full-index',CREF,ctrl,'--',rel))
put('CONTROL-PRESERVATION.json',{'reference':CREF,'reference_tree':text(CONTROL,'rev-parse',CREF+'^{tree}'),'current':identities['control'],
    'delta_paths':cdelta,'modified_existing_paths':sorted(allowed),'new_paths':sorted(newfiles-oldfiles),
    'protected_old_payload_sha256':unchanged,'all_other_baseline_tree_entries_identical':True,
    'old_profiles_gates_tests_fixtures_lexer_cache_runtime':'BYTE_IDENTICAL; only runner/check_package/collect schema dispatch additions and new explicit-target emission',
    'shared_runtime_dispatch_audit':['RUNNER-DISPATCH.patch','CHECK_PACKAGE-DISPATCH.patch','COLLECT-DISPATCH.patch']})
deps=[]
def dependency(commit,relative,expected=None):
    rel=str((BASE/relative).relative_to(MAIN));raw=git(MAIN,'show',commit+':'+rel)
    assert (MAIN/rel).read_bytes()==raw
    if expected:assert D(raw)==expected
    deps.append({'commit':commit,'path':rel,'bytes':len(raw),'sha256':D(raw),'status':'MATCH'})
im=read(BASE/'kani3300/ch8-s4/s4p-2-inputs/MANIFEST.json')
for rel,sha in im['files'].items():dependency(TASK,rel,sha)
dependency(TASK,'kani3300/ch8-s4/s4p-2-inputs/MANIFEST.json')
rd='kani3300/ch8-s4/network-after-s4p1-plan-review-w14/'
manifest=read(BASE/(rd+'MANIFEST.json'));review_count=0
for name,rec in manifest['files'].items():dependency(REVIEW,rd+name,rec['sha256']);review_count+=1
dependency(REVIEW,rd+'MANIFEST.json')
prior=read(BASE/(rd+'DEPENDENCIES.json'))
assert len(prior['items'])==31
for item in prior['items']:
    raw=git(MAIN,'show',item['commit']+':'+item['path']);assert D(raw)==item['sha256'] and raw==(MAIN/item['path']).read_bytes()
assert review_count==14
for name in text(MAIN,'ls-tree','-r','--name-only',PLAN,'research/challenge-8/kani-k1/kani3300/ch8-s4/network-after-s4p1-plan-r1').splitlines():
    dependency(PLAN,str(Path(name).relative_to('research/challenge-8/kani-k1')))
put('DEPENDENCIES.json',{'task':TASK,'plan':PLAN,'plan_review':REVIEW,'review_files':15,'review_hashes':14,'review_dependency_refs_verified':31,
    'entries':deps,'review_prior_dependencies':prior['items'],'proof_credit':'NONE','execution_GO':'NOT_GRANTED'})
for name in ('INPUTS.json','ROLE-SAT-CONTRACT.json','IMPLEMENTATION-GATES.json','ROOT-PLAN-RECHECK.json'):
    shutil.copyfile(BASE/'kani3300/ch8-s4/s4p-2-inputs'/name,OUT/name)
shutil.copyfile(CONTROL/'ch8-s1-control/CI-REQUEST.json',OUT/'CI-REQUEST.json')
shutil.copyfile(CONTROL/'.github/workflows/ch8-s2.yml',OUT/'WORKFLOW.yml')
put('ROOTS.json',{'ordered_roots':request['rows'],'source_bindings':request['source_bindings'],'design_id_to_selector':{x['design_id']:x['selector'] for x in request['rows'][4:]},'native_counts':'UNKNOWN','source_assertions':21,'source_covers':21})
put('ROLE-ORACLE-COVER.json',{'profile':request['profile'],'rows':[{k:row[k] for k in ('id','selector','mode','target','roles','required_success_messages','required_cover_messages','required_cover_count')} for row in request['rows']],
    'structural_na':[{k:row[k] for k in ('id','structurally_not_applicable_roles','structural_na_binding')} for row in request['rows'][4:]],
    'oracle':'unchanged sorting_model::post exact full-value sorted/count; full outside frame and arbitrary outside canary',
    'source_assertions':21,'source_covers':21,'native_counts':'UNKNOWN; loop instances retained, never inferred from source-site count'})
put('DOMAIN-UNWIND.json',{'domains':request['domains'],'unwind':{x['id']:x['unwind'] for x in request['rows']},'flags':request['flags'],
    'source_unwind36':'PROPOSED_NATIVE_EXHAUSTION_NOT_RUN','actual_network_path':'N0/1 immediate return; N2/3/4 no_merge insertion prefix1 with 1/2/3 insert_tail steps; no sort4/swap replacement',
    'normal_return_scope':'stateless u8/KeyLess; initialized V34/base1, all34 independent fullu8; no generic/panic/init/mask/provider theorem'})
sys.path.insert(0,str(CONTROL/'ch8-s1-control'))
import s4p2_profile as profile,s4p2_validate,s4p_validate,s34_validate,s32_validate,s3_validate,unittest
def ids(suite):
    for item in suite:
        if isinstance(item,unittest.TestSuite):yield from ids(item)
        else:yield item.id()
selected=list(ids(unittest.defaultTestLoader.loadTestsFromNames(s4p2_validate.NEW)))
assert not any('unittest.loader._FailedTest' in x for x in selected)
put('TEST-LIST.json',{'suites':{'legacy':s3_validate.LEGACY,'s3':('test_s3','test_s3_repair','test_s3_paths'),'s32':s32_validate.NEW,'bridge1':s34_validate.NEW,'s4p':s4p_validate.NEW,'s4p2':s4p2_validate.NEW},
    'expanded_new_tests':selected,'new_test_count':len(selected),'all_prior_305_tests_selected':True,'new_tests_actually_selected_by_workflow':'s4p2_validate.py NEW, not merely standalone or test discovery'})
put('RESOURCE.json',{'caps':profile.CAPS,'setup_seconds':1800,'job_minutes':180,'validate_minutes':18,'validate_margin_required':1.5,
    'memory_effective':'Ceff=min(6GiB,12GiB,A-2GiB); local sampled ownedPGID, outer owned census; not cgroup/kernelpeak',
    'eight_slot_envelope_seconds':6180,'envelope_scope':'ARITHMETIC_ONLY_NOT_MEASURED_FIT','native_cost_fit':'NOT_RUN','retries_escalation':'NONE'})
citations=[]
for rel,names in [(leaf,list(profile.CANDIDATES)),('library/core/src/slice/sort/shared/smallsort.rs',['small_sort_network','insertion_sort_shift_left','insert_tail']),('library/core/src/slice/sort/shared/smallsort/verify/sorting_model.rs',['active_post']),('library/core/src/slice/sort/shared/smallsort/verify/sorting_s2_batch.rs',list(profile.ORDER[:3])),('library/core/src/slice/sort/shared/smallsort/verify/sorting_s4_partition.rs',[profile.ORDER[3]])]:
    lines=(SOURCE/rel).read_text().splitlines()
    for name in names:
        matches=[i+1 for i,line in enumerate(lines) if 'fn '+name+'(' in line or 'fn '+name+'<' in line]
        assert len(matches)==1,(rel,name,matches)
        citations.append({'source_sha':std,'file':rel,'sha256':D((SOURCE/rel).read_bytes()),'symbol':name,'line':matches[0],'assurance':'SOURCE_LOCATION_ONLY_NOT_MIR_CAUSAL_BINDING'})
put('SOURCE-CITATIONS.json',citations)
put('PROVENANCE.json',{**identities,'task':TASK,'request_sha256':D((OUT/'CI-REQUEST.json').read_bytes()),
    'workflow_sha256':D((OUT/'WORKFLOW.yml').read_bytes()),'workflow_path':'.github/workflows/ch8-s2.yml','branch_filter':'uninit-ci/ch8-s4p-*',
    'artifact_prefix':'ch8-s3-2-${{ github.run_id }}-${{ github.run_attempt }}; intentional historical portable artifact prefix',
    'payload':request['ci_payload_sha256'],'changed_paths':request['ci_changed_paths'],'deleted_paths':request['ci_deleted_paths'],
    'selfhash_excluded':'ch8-s1-control/CI-REQUEST.json','native_start':'NOT_RUN','g0_delivery_commit':'Returned externally, containing commit binds packet manifest'})
put('OPEN-OBLIGATIONS.json',{'native_inventory_roles_SAT_U_guard_location_unwind_cost_fit':'NOT_RUN',
    'open':['Exact package W14 independent review and root fullpin check/GO','Published exact source and NONSKIP SAME-TREE control sibling sole9e14/head/ref/run binding by coordinator',
    'Actual Kani compilation and same-invocation native property inventory/counts/status/SAT/unwind/fit',
    'All insertion-prefix provider/caller edges; initialized-input harness is not initialization theorem','Generic traits/type/ownership/panic/unwind/universal contracts, summary/model qualification and MIR/B1/B2',
    'N>=5/9/13/16/32/general and capped historical network remain UNKNOWN'],
    'new_proof_obligations_closed':0,'new_qualified_leaves':0,'proof_credit':'NONE','old_exact_location_admissions':'Only historical exact runs/IDs, never transferred','unreachable':'REJECT_ALL; proposal disabled'})
put('PRECURSORS.json',{'targeted_receipts':sorted(p.name for p in (OUT/'tests').glob('targeted-*.json')),
    'initial_construction_failure':{'tool_transcript_only':True,'exit':1,'exception':'ValueError: substring not found','scope':'Offline helper template extraction before source commit; fixed extraction; not native or final Validate'},
    'targeted_02_failure':'Retained exact stdout/stderr/receipt; relative python -c sys.path and distinguishing ordinary replacement check corrected',
    'targeted_03':'Passing pre-tightening imported object; subsequent explicit worker-null/canonical source/replay additions validated by targeted-04; never relabelled final',
    'other_read_only_diagnostics':['Pinned notification nonobject corrected by root to actual bf3aba; no pin substitution without authorization','One test-count import used repository cwd instead of ch8-s1-control; rerun at correct cwd, no candidate effect','One git diff queried baseline control object in stock-tool-only clone; nonobject, corrected repo; no mutation'],
    'historical_final_validate':'S4P1 2db5d2c08804036d283cb36450647cd584ee9e10 only:305 PASS 550.6377290091477s; not S4P2 evidence',
    'actual_final_validate_runs_so_far':0,'native_compile_proof':'NOT_RUN','failures_discarded':False})
pins={**identities,'schema':'ch8-s4p-2-offline-pins-v1','status':'PREPARED_PENDING_ACTUAL_FINAL_VALIDATE','task':TASK,'plan':PLAN,'plan_review':REVIEW,
    'runtime':'SolHigh/FastOFF; no subagents/model changes','request':{'schema':request['schema'],'profile':request['profile'],'sha256':D((OUT/'CI-REQUEST.json').read_bytes()),
       'workflow_sha256':D((OUT/'WORKFLOW.yml').read_bytes()),'payload_files':len(request['ci_payload_sha256']),'selfhash_excluded':True},
    'terminal_schema':profile.TERMINAL_SCHEMA,'seal_schema':profile.SEAL_SCHEMA,'ordered_rows':list(profile.ORDER),'caps':profile.CAPS,
    'cfg_power_set':{'actual_independent_keys':6,'projections':64,'legacy_contexts_retained':32,'sorting_enabled':32,'ACTIVE_contexts':8},
    'offline_validation':'PENDING actual final Validate once','native_compile_proof_cost_fit':'NOT_RUN','proof_credit':'NONE','GO':'NOT_GRANTED',
    'independent14':'EXACT_PACKAGE_REVIEW_REQUIRED; plan approval is insufficient','future_head_ref_run':'UNKNOWN','publication':'NOT_PERFORMED','accounting':'TRACKING_ONLY_NO_WRITES',
    'g0_delivery_commit':'Reported externally; manifest bound by containing commit'}
put('PINS.json',pins)
print(json.dumps({'status':pins['status'],'source':std,'control':ctrl,'control_tree':identities['control']['tree'],'six_patch_trees':'PASS','shallow_depths':[5,7,2],'new_tests_selected':len(selected),'payload_files':len(request['ci_payload_sha256'])}),flush=True)
