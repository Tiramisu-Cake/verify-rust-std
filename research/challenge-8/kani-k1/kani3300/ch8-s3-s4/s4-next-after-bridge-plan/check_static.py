#!/usr/bin/env python3
"""Read-only document/source identity and finite-coverage checks; no native tools."""
import hashlib,json,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
DIGEST=lambda data:hashlib.sha256(data).hexdigest()
def read(name):return json.loads((HERE/name).read_text())
def blob(repo,commit,path):return subprocess.check_output(['git','-C',str(repo),'show',commit+':'+path])
def git(repo,*args):return subprocess.check_output(['git','-C',str(repo),*args],text=True).strip()
def check():
    checks=0
    def need(value,why):
        nonlocal checks
        checks+=1
        if not value:raise AssertionError(why)
    pins=read('PINS.json');review=read('REVIEW-BINDING.json');admission=read('ADMISSION-BINDING.json')
    need(pins['status']=='READY_PLANONLY_REVIEW_BOUND_NO_IMPLEMENTATION','ready plan scope')
    need(review['review_commit']==pins['review_commit']=='135c04791a779e949079db723bdbc0e636873b37','actual review')
    need(review['intake_commit']==pins['intake_commit']=='97eaff96cd28267e36af69fe98077dd08737eea6','exact intake')
    need(review['disposition']=='APPROVE' and not review['blocking_findings'] and not review['localized_findings'],'review verdict')
    need(not review['conditional_packet_sealed'] and not review['immutable_evidence_update_required'],'single final review-bound seal')
    need(admission['commit']==pins['new_admission']=='39606c431ba266a5dbab2163d0e5175428d38aec','actual separate admission')
    need(admission['intake']==pins['intake_commit'] and admission['review']==pins['review_commit'],'admission input binding')
    need(admission['qualified_bounded_cases']==2 and admission['new_provider_summary_contracts_admitted']==0,'admission bounded cases only')
    need([c['id'] for c in admission['cases']]==['i_p01_b01_fullu8','sort9_v34_b01_len09_real'],'case list')
    need([(c['mode'],c['target']) for c in admission['cases']]==[('PFC','insert_tail'),('Original',None)],'actual modes')
    need(all(not c['general_contract_provider_eligibility'] for c in admission['cases']),'not provider summaries')
    need(not admission['location_exception']['required'] and not admission['location_exception']['applied'],'no new location exception')
    for key in ('source','tool','reviewed_control'):
        item=pins[key];repo=Path(item['repo'])
        need(git(repo,'rev-parse','HEAD')==item['sha'],key+' exact head')
        need(git(repo,'rev-parse','HEAD^{tree}')==item['tree'],key+' exact tree')
        need(not git(repo,'status','--porcelain=v1'),key+' clean')
        if 'sole_parent' in item:need(git(repo,'rev-list','--parents','-n','1','HEAD').split()[1:]==[item['sole_parent']],key+' parent')
    for item in read('DEPENDENCIES.json')['entries']:
        need(DIGEST(blob(item['repo'],item['commit'],item['path']))==item['sha256'],'dependency '+item['path'])
    rootinputs=read('INPUTS.json');bad=rootinputs['exact_root_inputs']['existing_admissions']['s3_1_r2']
    need(len(bad)==41 and bad==pins['prior_admissions']['s3_1_supplied_invalid'],'supplied pin preserved')
    need(rootinputs['resolution_notes'][0]['resolved_commit']==pins['prior_admissions']['s3_1_actual'],'resolved exact actual admission')
    authority=next(x for x in read('DEPENDENCIES.json')['entries'] if x['role']=='EXPLICIT_PLANONLY_AUTHORITY')
    need(authority['sha256']==rootinputs['exact_root_inputs']['task_sha256'],'authority bytes match issued input')
    for item in read('SOURCE-CITATIONS.json')['ranges']:
        data=blob(item['repo'],item['commit'],item['file']);lines=data.decode().splitlines()
        need(DIGEST(data)==item['file_sha256'],'cited file')
        need(1<=item['start_line']<=item['end_line']<=len(lines),'source coordinates')
        need(DIGEST(('\n'.join(lines[item['start_line']-1:item['end_line']])+'\n').encode())==item['range_sha256'],'cited exact range')
    for item in read('SOURCE-PRESERVATION.json')['bindings']:
        old=blob(item['repo'],item['old_commit'],item['file']);new=blob(item['repo'],item['current_commit'],item['file'])
        need(old==new and DIGEST(new)==item['sha256'],'old/current source byte rebinding')
    parts=read('PARTITIONS.json')
    for fam,blocks in parts['length_partitions'].items():
        values=[n for low,high in blocks for n in range(low,high+1)]
        need(values==parts['full_domains'][fam] and len(values)==len(set(values)),fam+' exhaustive disjoint union')
    for fam in ('fallback','network'):
        values=parts['next_positive_union'][fam];rest=parts['remaining_after_next_if_all_admitted'][fam]
        need(values+rest==parts['full_domains'][fam],fam+' remaining exact domain')
    matrix=read('CALLER-MATRIX.json');rows=matrix['rows']
    need(len(rows)==83,'83 finite current source rows')
    for fam,limit in [('fallback',16),('network',32),('general',32)]:
        selected=[r for r in rows if r['family']==fam]
        need([r['n'] for r in selected]==list(range(limit+1)),fam+' no omitted/duplicate lengths')
        for row in selected:
            n=row['n'];h=n//2
            need(row['source_commit']==pins['source']['sha'] and row['admitted_assurance'].startswith('NONE'),'caller not promoted')
            calls=row['calls'];tails=row['insert_calls']
            if fam=='fallback':expected=[] if n<2 else [(0,p) for p in range(1,n)]
            elif fam=='network':
                expected=[]
                if n>=2:
                    for offset,length in ([(0,n)] if n<18 else [(0,h),(h,n-h)]):
                        seed=13 if length>=13 else 9 if length>=9 else 1
                        expected.extend((offset,p) for p in range(seed,length))
                if n<=8:need(not any(c['target'] in ('sort4_stable','sort9_optimal','bidirectional_merge') for c in calls),'no proposed leaves on network<=8')
                if n==25:need([c['target'] for c in calls if c['target'].startswith('sort')]==['sort9_optimal','sort13_optimal'],'mixed25 exact')
            else:
                seed=8 if n>=16 else 4 if n>=8 else 1
                expected=[] if n<2 else [(offset,p) for offset,length in [(0,h),(h,n-h)] for p in range(seed,length)]
            need([(t['begin_active_offset'],t['relative_tail']) for t in tails]==expected,f'{fam}{n} actual required tails')
            for tail in tails:
                need(2<=tail['span']<=17 and tail['span']==tail['relative_tail']+1,'span contract arithmetic')
                need(tail['input_initialized_REQUIRED']==[tail['begin_allocation_index'],tail['begin_allocation_index']+tail['span']],'exact initialized span coordinates')
                need(tail['input_initialized_REQUIRED'][1]<=(1+n if fam!='general' else n),'tail within actual caller')
    contexts=matrix['sort8_internal_merge_contexts']
    need(len(contexts)==34 and {(c['n'],c['side']) for c in contexts}=={(n,side) for n in range(16,33) for side in (0,1)},'34 distinct sort8 contexts')
    for c in contexts:
        n,side=c['n'],c['side'];src,dst=c['merge8_source_scratch'],c['merge8_dst_scratch'];h=n//2
        need(src==n+8*side and dst==(0 if side==0 else h),'exact source/dst offsets')
        need(0<=dst and dst+8<=n and src+8<=48 and dst+8<=src,'same-allocation disjoint8 ranges')
        need(not c['existing_allinit_case_applicable'] and not c['scratch_init_mask_is_all_outside_dst'],'no allinit-to-partial lift')
    leaves=read('LEAF-APPLICABILITY.json')['items'];byid={r['id']:r for r in leaves}
    need(len(byid)==len(leaves)==15,'leaf inventory')
    need(all(not r['usable_as_universal_summary'] and not r['qualified_init_provider'] for r in leaves),'no false provider/init lift')
    for id in ('L_INSERT_P1','L_SORT9'):need(byid[id]['case_admission_commit']==admission['commit'] and byid[id]['assurance']=='QUALIFIED_BOUNDED_SOURCE_REPORTED_EXACT_CASE','admitted case status')
    for id in ('L_MERGE8_PARTIAL_LEFT','L_MERGE8_PARTIAL_RIGHT'):need(byid[id]['assurance']=='DIAGNOSTIC_ONLY_INITIALIZATION_OPEN_NONPROVIDER','partial nonprovider')
    dag=read('DAG.json');nodes=dag['provider_and_caller_nodes'];nodeids={n['id'] for n in nodes}|set(byid)
    need(len(nodes)==13 and len(dag['edges'])==24 and not dag['enabled_summary_edges'],'open DAG only')
    need(all(n['assurance']=='OPEN_NO_SUMMARY_CREDIT' for n in nodes),'no provider claimed proved')
    for edge in dag['edges']:need(edge['from'] in nodeids and edge['to'] in nodeids and edge['status'] in ('EVIDENCE_STARTING_POINT_ONLY','OPEN_NOT_ENABLED'),'edge exact boundary')
    campaign=read('NEXT-CAMPAIGN.json');selectors=campaign['ordered_selectors'];need(len(selectors)==8 and len({s['id'] for s in selectors})==8,'8 unique prospective selectors')
    need([s['kind'] for s in selectors[:4]]==['NEGATIVE']*4,'four negative controls')
    positives=selectors[4:]
    for root in positives:
        low,high=root['length_interval'];need(root['mode']=='Original' and root['target'] is None,'Original positive targets')
        need(len(root['assertion_roles'])==4 and len(root['length_cover_labels'])==high-low+1,'four roles and every length cover')
        need(high>=2 and high<=4 and low>=0,'feasible next unsorted/duplicate/descending witnesses, no hidden large family')
    resource=read('RESOURCE.json');caps=resource['defaults']
    need(resource['all_caps_unchanged'] and resource['setup_seconds']==1800 and resource['job_minutes']==180,'defaults unchanged')
    need(caps=={'child_seconds':600,'compile_seconds':180,'slot_seconds':720,'controller_seconds':180,'cleanup_seconds':240,'campaign_seconds':6900,'outer_seconds':7500,'phase_seconds':8100,'step_seconds':7560,'local_rss_kib':6291456,'outer_rss_kib':12582912,'headroom_kib':2097152,'stdout_bytes':16777216,'stderr_bytes':1048576,'export_bytes':8388608,'artifact_bytes':268435456},'exact caps')
    need(len(selectors)*720+180+240==resource['envelopes']['eight_roots']==6180<=6900,'eight-slot arithmetic only')
    facts=read('EVIDENCE-FACTS.json')
    for row in facts['facts'][-2:]:need(row['cutoff_cause']=='CHILD_600_WALL_TIMEOUT' and row['effective_cap_kib']==6291456 and row['whole_child']['timed_out'],'correct cutoff cause')
    need(facts['U_count']==28 and facts['SUCCESS_unsupported_guards']==7 and facts['producer_strict_matches']=='0/7','retained producer history')
    checkpoint=read('CHECKPOINT.json')
    need(checkpoint['independent_review']==pins['review_commit'] and checkpoint['new_admission_input']==admission['commit'],'final checkpoint dependencies')
    need(checkpoint['plan_created_qualified_cases']==0 and checkpoint['summary_providers_or_caller_obligations_closed']==0,'plan creates no proof')
    manifest={}
    for line in (HERE/'MANIFEST.sha256').read_text().splitlines():
        digest,name=line.split('  ',1);need(name not in manifest,'unique manifest path');manifest[name]=digest
        need(DIGEST((HERE/name).read_bytes())==digest,'manifest '+name)
    actual={str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and p.name!='MANIFEST.sha256'}
    need(set(manifest)==actual,'all own packet files sealed')
    return {'status':'STATIC_PLAN_PASS','checks':checks,'source_ranges':len(read('SOURCE-CITATIONS.json')['ranges']),'leaf_cases':15,'caller_length_rows':83,'sort8_contexts':34,'DAG_nodes':13,'DAG_edges':24,'proposed_selectors':8,'native_tools_or_CI':'NOT_RUN','algorithm_or_provider_proof_credit':'NONE'}
if __name__=='__main__':print(json.dumps(check(),sort_keys=True))
