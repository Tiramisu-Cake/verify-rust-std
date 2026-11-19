#!/usr/bin/env python3
"""Read-only exact packet checks. No native tools, CI or ledger operations."""
import hashlib,json,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
D=lambda b:hashlib.sha256(b).hexdigest()
def read(name):return json.loads((HERE/name).read_text())
def git(repo,*args):return subprocess.check_output(['git','-C',str(repo),*args],text=True).strip()
def blob(repo,sha,path):return subprocess.check_output(['git','-C',str(repo),'show',sha+':'+path])
def check():
    count=0
    def need(ok,why):
        nonlocal count
        count+=1
        if not ok:raise AssertionError(why)
    pins=read('PINS.json');r=read('CI-REQUEST.json');final=read('FINAL-VALIDATE.json')
    need(pins['status']=='READY_FOR_ROOT_CHECK_AND_SAME14_DELTA_NOT_GO','READY scope')
    need(pins['implementation_task']=='c049f3c7f44d111db45baf36a5de24dc19209ee5','task')
    need(pins['frozen_plan']=='a931835b4af8dc8b2ad60e9a115bc0a4903b0b5e','plan')
    for name in ('source','control','tool'):
        item=pins[name];repo=Path(item['repo'])
        need(git(repo,'rev-parse','HEAD')==item['sha'],name+' HEAD')
        need(git(repo,'rev-parse','HEAD^{tree}')==item['tree'],name+' tree')
        need(git(repo,'show','-s','--format=%P','HEAD').split()==item['parents'],name+' parents')
        need(not git(repo,'status','--porcelain=v1'),name+' clean')
    need(pins['source']['parents']==['97ac4d39d7f959ea70b1f57785ffd1fd66ecd22a'],'source soleparent')
    need(pins['control']['parents']==['9e14e033f9ee31522b571c127609dcdff76d230b'],'control soleparent')
    need(pins['tool']['sha']=='0aac16ef62da9e9d5645782d458593e5d78143ba','stocktool')
    h=Path(pins['control']['repo'])/'ch8-s1-control';sys.path.insert(0,str(h))
    import runner,s4p_profile as p,s4p_policy as policy,check_package
    need(runner.load_request()==r,'actual strict request loader')
    need(p.validate(r),'new profile')
    need((h/'CI-REQUEST.json').read_bytes()==(HERE/'CI-REQUEST.json').read_bytes(),'request byte binding')
    need(D((HERE/'CI-REQUEST.json').read_bytes())==pins['request']['sha256']==final['request_sha256'],'request hash')
    need(D((HERE/'WORKFLOW.yml').read_bytes())==pins['request']['workflow_sha256']==final['workflow_sha256'],'workflow hash')
    need((Path(pins['control']['repo'])/'.github/workflows/ch8-s2.yml').read_bytes()==(HERE/'WORKFLOW.yml').read_bytes(),'workflow current bytes')
    need(check_package.check_yaml(HERE/'WORKFLOW.yml')['campaign_envelope_seconds']==6180,'workflow strict schema/depths/caps')
    changed=git(pins['control']['repo'],'diff','--name-only',r['tool_sha'],pins['control']['sha']).splitlines()
    need(changed==r['ci_changed_paths'],'committed full payload path inventory')
    for rel,digest in r['ci_payload_sha256'].items():need(D(blob(pins['control']['repo'],pins['control']['sha'],rel))==digest,'payload '+rel)
    need(r['std_sha']==pins['source']['sha'] and r['std_tree']==pins['source']['tree'],'source request')
    need(r['tool_sha']==pins['tool']['sha'] and r['tool_tree']==pins['tool']['tree'],'tool request')
    need(final['control_sha']==pins['control']['sha'] and final['control_tree']==pins['control']['tree'],'actual final Validate commit')
    need(final['execution_count']==1 and final['exit_code']==0 and not final['timed_out'] and final['clean_after'],'single final Validate success')
    need(final['elapsed_seconds']<=720 and final['margin_at_18_minutes']>=1.5 and final['limit_seconds']==1080,'18 minute actual margin')
    for name in ('stdout','stderr'):
        spec=final[name];raw=(HERE/spec['file']).read_bytes()
        need(D(raw)==spec['sha256'] and len(raw)==spec['bytes'],'final '+name+' bytes')
    summary=json.loads((HERE/'FINAL-VALIDATE.stdout').read_text().splitlines()[-1])
    need(summary['success'] and summary['errors']==summary['failures']==0,'all final test suites')
    need(summary['control_sha']==pins['control']['sha'] and summary['request_sha256']==pins['request']['sha256'],'summary identities')
    need(summary['test_counts']['s4p']==38,'all necessary new tests in CI command')
    need(r['flags']['RUSTFLAGS']==p.CFG,'effective cfg')
    need(len(r['rows'])==8 and all(row['mode']=='Original' and row['target'] is None for row in r['rows']),'all eight modes/targets')
    need([row['id'] for row in r['rows']]==list(p.ORDER),'exact order')
    need([row['required_cover_count'] for row in r['rows']]==[0,0,0,0,8,7,8,7],'covers plus every length')
    need(sum(x['class']=='assertion' for row in r['rows'] for x in row['roles'])==21,'actual literal assertion source sites only')
    need(sum(row['required_cover_count'] for row in r['rows'])==30,'actual literal cover source sites only')
    need(policy.validate_roles(Path(pins['source']['repo']),r),'source roles full binding')
    for name,key in [('ORDINARY','ordinary_contract_source_sha256'),('CFG_PFC','cfg_pfc_source_sha256'),('CONTRACT_STACKS','contract_stack_source_sha256'),('LEXICAL','lexical_source_sha256')]:
        report=read('MAP-'+name+'.json')
        need(report['status']=='STATIC_PASS','preflight '+name)
        need(report['source_files_sha256']==r[key],'dependency inventory '+name)
        for rel,digest in r[key].items():need(D(blob(pins['source']['repo'],pins['source']['sha'],rel))==digest,'actual gated source '+rel)
    need(pins['repair_task']=='989b0dbd020bc9bb500c0a18f3220d21537fbc44','exact repair task')
    need(pins['frozen_author']=='590dd6360f5b4c92eab9fff30aa0d2e7d8d942ce','frozen author')
    need(pins['independent_review']=='4856a87f39d2606adbbed747d3cae9a73fb80d52','same review')
    need(final['command']=="python3 check_package.py control --repo ..\npython3 s4p_validate.py\n",'actual workflow command')
    need(final['script_sha256']==D((h/'s4p_validate.py').read_bytes()),'exact actual Validate script')
    need(summary['test_counts']=={'legacy':136,'s3':56,'s32':35,'bridge1':40,'s4p':38},'305 tests and old protected counts')
    need(sum(summary['test_counts'].values())==305,'all tests')
    import itertools,unittest,s4p_validate,s4p_contract_stacks
    keys={'kani','kani_smallsort_sorting','kani_smallsort_s2_assumed','kani_smallsort_s3_leaf','kani_smallsort_s4_partition'}
    expected={frozenset(part) for size in range(6) for part in itertools.combinations(keys,size)}
    projections=read('MAP-CONTRACT_STACKS.json')['cfg_projection_invariance']
    actual=[frozenset(x['effective_cfg']) for x in projections]
    need(len(actual)==len(set(actual))==32 and set(actual)==expected,'full exact unique power set')
    need(sum('kani_smallsort_sorting' in x for x in actual)==16,'sorting-enabled contexts')
    need(sum(s4p_contract_stacks.ACTIVE<=x for x in actual)==4,'ACTIVE contexts')
    need(all(x['functions']>0 and x['semantics']=='EXACT_TOKEN_MATCH' for x in projections),'real comparisons')
    need(all(x['outside_s2_attrs']==('NORMALIZED' if s4p_contract_stacks.ACTIVE<=set(x['effective_cfg']) else 'EXACT_TOKEN_MATCH') for x in projections),'normalization contexts')
    testlist=read('TEST-LIST.json')
    need(testlist['suites']['s4p']==list(s4p_validate.NEW),'actual CI selection')
    need(unittest.defaultTestLoader.loadTestsFromNames(s4p_validate.NEW).countTestCases()==38,'actual new selection count')
    need('test_s4p_gate_repair' in s4p_validate.NEW,'regressions selected')
    stderr=(HERE/'FINAL-VALIDATE.stderr').read_text()
    for name in testlist['repair_tests']:need(name.split('.')[-1] in stderr,'new regression actually executed '+name)
    matrix=read('tests/TERMINAL-SCHEMA-MATRIX.json')['records']
    bad=[x for x in matrix if not x['accepted']];good=[x for x in matrix if x['accepted']]
    need(len(matrix)==84 and len(bad)==78 and len(good)==6,'schema mutation matrix')
    need(all(not x['legacy_collection_entered'] and x['error']=='S4 terminal campaign schema mismatch' for x in bad),'no malformed schema collection')
    need(all(x['legacy_collection_entered'] and x['recorded_observations']==x['completed'] for x in good),'genuine full/partial/STOPPED accepted')
    states={'STOPPED','SELECTED_PARTIAL','SELECTED_RECORDED_FULL_INVENTORY_INCOMPLETE'}
    need({(x['writer_state'],x['route']) for x in good}=={(s,r) for s in states for r in ('LOCAL','UPLOAD_ONLY')},'both routes all valid states')
    def original_variant(x):
        if not x['schema_present']:return 'missing'
        if x['schema'] is None:return 'null'
        if x['schema']=='ch8-s3s4-bridge1-campaign-v1':return 'old'
        if type(x['schema']) is int and x['schema']==123:return 'int'
    old24={(x['writer_state'],x['route'],original_variant(x)) for x in bad if original_variant(x)}
    need(old24=={(s,r,v) for s in states for r in ('LOCAL','UPLOAD_ONLY') for v in ('missing','null','old','int')},'all original24 rejected')
    preserve=read('CONTROL-PRESERVATION.json')
    delta=git(pins['control']['repo'],'diff','--name-only',pins['repair_reference'],pins['control']['sha']).splitlines()
    need(delta==preserve['repair_delta_paths']==sorted('ch8-s1-control/'+x for x in ('CI-REQUEST.json','s4p_campaign.py','s4p_contract_stacks.py','s4p_validate.py','test_s4p_gate_repair.py')),'localized exact delta')
    for rel,digest in preserve['protected_e941_payload_bytes'].items():
        need(D(blob(pins['control']['repo'],pins['control']['sha'],rel))==digest==D(blob(pins['control']['repo'],pins['repair_reference'],rel)),'protected E941 '+rel)
    oldrequest=json.loads(blob(pins['control']['repo'],pins['repair_reference'],'ch8-s1-control/CI-REQUEST.json'))
    need(set(k for k in r if r[k]!=oldrequest[k])=={'ci_changed_paths','ci_payload_sha256'},'request semantics unchanged')
    history=read('HISTORY-PRESERVATION.json')
    for frozen in history['frozen_packets']:
        for rel,digest in frozen['bindings'].items():
            need(D(blob('/root/verify-rust-std-kani3300-g0',frozen['commit'],rel))==digest==D((Path('/root/verify-rust-std-kani3300-g0')/rel).read_bytes()),'immutable historical '+rel)
    need(history['old_final_validate']['tests']==302 and history['old_final_validate']['control_sha']==pins['repair_reference'],'old302 preserved separate')
    oldcontrol=history['old_control']
    need(git(oldcontrol['repo'],'rev-parse','HEAD')==oldcontrol['sha']==pins['repair_reference'],'E941 old HEAD preserved')
    need(git(oldcontrol['repo'],'rev-parse','HEAD^{tree}')==oldcontrol['tree'] and not git(oldcontrol['repo'],'status','--porcelain=v1'),'E941 old tree/clean preserved')
    need(read('tests/targeted-02.json')['request_sha256']==pins['request']['sha256'],'targeted candidate payload binding')
    reproduced=read('tests/review-reproducer.json');original_reproducer=(HERE/'tests/reproduce_schema.review.py').read_bytes()
    need(D(original_reproducer)==reproduced['original_sha256'],'sealed reproducer identity')
    need(D(original_reproducer.replace(b'/root/kani-ch8-s4p-1-control-w13/ch8-s1-control',b'/root/kani-ch8-s4p-1-r1-control-w13/ch8-s1-control'))==reproduced['execution_copy_sha256'],'only disposable CONTROL replacement')
    need(reproduced['exit_code']==1 and reproduced['expected_nonzero'] and reproduced['observed_rejection']=='S4 terminal campaign schema mismatch','preserved expected rejection')
    need(read('FINDING-CLOSURES.json')['independent_closure']=='PENDING_SAME14','author does not claim independent closure')
    patches=read('PATCHES.json');need(len(patches)==6,'six patches')
    for patch in patches:
        need(patch['expected_tree']==patch['replayed_tree'],'patch exact replay')
        need(D((HERE/patch['file']).read_bytes())==patch['sha256'],'patch digest')
    for item in read('ANCESTRY.json')['shallow']:need(item['status']=='SHALLOW_IDENTITY_PASS','shallow '+str(item['depth']))
    for item in read('SOURCE-CITATIONS.json')['ranges']:
        raw=blob(item['repo'],item['commit'],item['file']);lines=raw.decode().splitlines()
        need(D(raw)==item['file_sha256'],'cited file')
        need(1<=item['start_line']<=item['end_line']<=len(lines),'cited coordinates')
        need(D(('\n'.join(lines[item['start_line']-1:item['end_line']])+'\n').encode())==item['range_sha256'],'cited bytes')
    for item in read('DEPENDENCIES.json')['entries']:need(D(blob(item['repo'],item['commit'],item['path']))==item['sha256'],'authority/plan bytes')
    preservation=read('SOURCE-PRESERVATION.json')
    need(preservation['verify_prefix_preserved'],'old verify wiring retained')
    for item in preservation['bindings']:
        need(blob(pins['source']['repo'],preservation['reference'],item['file'])==blob(pins['source']['repo'],pins['source']['sha'],item['file']),'preserved source '+item['file'])
    resources=read('RESOURCE.json');need(resources['defaults']==p.CAPS and resources['all_caps_unchanged'],'caps')
    need(resources['setup_seconds']==1800 and resources['job_minutes']==180 and resources['validate_minutes']==18,'setup/job/Validate caps')
    need(r['enabled_summary_edges']==[] and r['replacement_unions']==[] and r['variants']=={},'no summaries/stub variants')
    need(r['unreachable_admission']['mode']=='REJECT_ALL' and not r['unreachable_admission']['enabled'],'no inherited U waiver')
    manifest={}
    for line in (HERE/'MANIFEST.sha256').read_text().splitlines():
        digest,name=line.split('  ',1);need(name not in manifest,'unique manifest entry');manifest[name]=digest
        need(D((HERE/name).read_bytes())==digest,'manifest '+name)
    actual={str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and p.name!='MANIFEST.sha256'}
    need(set(manifest)==actual,'complete immutable packet file set')
    return {'status':'STATIC_READY_PACKET_PASS','checks':count,'selected_source_literal_assertions':21,'selected_source_literal_covers':30,'required_rows':8,'proof_credit':'NONE','native_compile_verifier_CI':'NOT_RUN','GO':'NOT_AUTHORIZED'}
if __name__=='__main__':print(json.dumps(check(),sort_keys=True))
