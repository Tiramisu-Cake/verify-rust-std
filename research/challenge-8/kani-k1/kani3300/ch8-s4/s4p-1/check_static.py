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
    need(pins['status']=='READY_FOR_ROOT_CHECK_AND_INDEPENDENT14_NOT_GO','READY scope')
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
    need(summary['test_counts']['s4p']==35,'all necessary new tests in CI command')
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
