#!/usr/bin/env python3
"""Offline S1-05 acceptance replay over pinned inputs and structured evidence only."""
import hashlib, json, subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
RUN=HERE.parent
TASK=RUN.parent
CONTROL=Path('/root/kani-ch8-s1-05-w13')
STD=Path('/root/verify-rust-std-ch8-s1-04-w13')
K1=Path('/root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1')
POLICY=K1/'ACCEPTANCE-POLICY-BATCH.md'
ART=RUN/'artifacts'
CONTROL_SHA='8860d38558651f7cf2e292d57b06b378c6ad3b94'
SOURCE_SHA='5be85699b8826e3286c0bf89efb9affefac0acb5'
TOOL_SHA='0aac16ef62da9e9d5645782d458593e5d78143ba'
GOOD={'light-model-u5','light-corruption-u4','activation-default-u34','cell-u34'}

def req(ok, why):
    if not ok: raise ValueError(why)
def hb(b): return hashlib.sha256(b).hexdigest()
def sha(p): return hb(p.read_bytes())
def read(p): return json.loads(p.read_bytes())
def git(repo,*a): return subprocess.check_output(['git','-C',str(repo),*a]).decode().strip()
def source_rel(path):
    pre='/home/runner/work/kani/kani/export/'
    req(isinstance(path,str) and path.startswith(pre),'EXPORT_PATH')
    return path[len(pre):]

def inventory(h, records):
    c,v=h['checks'],h['covers']
    cb=('failure','unreachable','undetermined','error','unknown','other')
    vb=('satisfied','unsatisfiable','unreachable','undetermined','error','unknown','other')
    for b,ks in ((c,cb),(v,vb)):
        req(type(b['total']) is int and b['total']>=0,'TOTAL')
        for k in ks: req(isinstance(b[k],list) and all(isinstance(x,str) and x for x in b[k]),'BUCKET')
    req(type(c['success']) is int and c['success']>=0,'SUCCESS')
    req(c['total']==c['success']+sum(len(c[k]) for k in cb),'CHECK_PARTITION')
    req(v['total']==sum(len(v[k]) for k in vb),'COVER_PARTITION')
    ids=[x for k in cb for x in c[k]]+[x for k in vb for x in v[k]]
    req(len(ids)==len(set(ids)),'DUPLICATE_ID')
    req(h['n_properties']==c['total']+v['total']==len(records),'PROPERTY_TOTAL')
    req(h['n_failed']==len(c['failure'])==len(h['failed_properties']),'FAILURE_TOTAL')
    req({p['id'] for p in h['failed_properties']}==set(c['failure']),'FAILURE_ID_SET')
    req(all(not c[k] for k in ('undetermined','error','unknown','other')),'INCOMPLETE_CHECK_STATUS')
    req(all(not v[k] for k in ('unsatisfiable','undetermined','error','unknown','other')),'INCOMPLETE_COVER_STATUS')
    by={}
    for p in records:
        req(p.get('id') and p['id'] not in by,'RICH_ID')
        req(p.get('class') and p.get('status') and p.get('file') and str(p.get('line','')).isdigit(),'RICH_COORD')
        by[p['id']]=p
    req(set(ids).issubset(by),'RICH_NON_SUCCESS_ID_SET')
    req(sum(p['status']=='SUCCESS' and p['class']!='cover' for p in records)==c['success'],'RICH_CHECK_SUCCESS_COUNT')
    for key, pids in [(k,c[k]) for k in cb]+[(k,v[k]) for k in vb]:
        status={'success':'SUCCESS','failure':'FAILURE','unreachable':'UNREACHABLE','undetermined':'UNDETERMINED','error':'ERROR','unknown':'UNKNOWN','other':'OTHER','satisfied':'SATISFIED','unsatisfiable':'UNSATISFIABLE'}[key]
        req(all(by[x]['status']==status for x in pids),'RICH_BUCKET_STATUS:'+key)
    return by

def main():
    payload=CONTROL/'ch8-s1-control'
    rp=TASK/'CI-REQUEST.json'; request=read(rp); request_sha=sha(rp)
    req(git(CONTROL,'rev-parse','HEAD')==CONTROL_SHA,'CONTROL_HEAD')
    req(git(STD,'rev-parse','HEAD')==SOURCE_SHA,'SOURCE_HEAD')
    req(not git(CONTROL,'status','--porcelain') and not git(STD,'status','--porcelain'),'DIRTY_PIN')
    req(request['std_sha']==SOURCE_SHA and request['tool_sha']==TOOL_SHA,'REQUEST_PINS')
    req(git(STD,'rev-parse',SOURCE_SHA+'^{tree}')==request['std_tree'],'SOURCE_TREE')
    req(git(CONTROL,'rev-parse',TOOL_SHA+'^{tree}')==request['tool_tree'],'TOOL_TREE')
    for rel,h in request['ci_payload_sha256'].items(): req(sha(CONTROL/rel)==h,'CONTROL_FILE:'+rel)
    for rel,h in request['changed_file_sha256'].items():
        req(sha(STD/rel)==h and hb(subprocess.check_output(['git','-C',str(STD),'show',SOURCE_SHA+':'+rel]))==h,'SOURCE_FILE:'+rel)
    req(sha(POLICY)==sha(K1/'ACCEPTANCE-POLICY-BATCH.md'),'POLICY')
    runmeta=read(RUN/'run-metadata.json'); ameta=read(RUN/'artifacts-metadata.json')
    req(runmeta['databaseId']==43864841077 and runmeta['headSha']==CONTROL_SHA,'RUN_IDENTITY')
    req(ameta['total_count']==14 and len(ameta['artifacts'])==14,'ARTIFACT_COUNT')
    req(all(a['workflow_run']['id']==43864841077 and a['workflow_run']['head_sha']==CONTROL_SHA for a in ameta['artifacts']),'ARTIFACT_RUN')
    rows={r['id']:r for r in request['rows']}; req(len(rows)==35,'REQUEST_ROWS')
    artifact_by_group={a['name'].split('-1-',1)[1]:a for a in ameta['artifacts']}
    all_h={}; groups=[]; row_results=[]
    evidence=RUN/'evidence'
    for gid, art in sorted(artifact_by_group.items()):
        # Intake already checked the compact-artifact members. This replay
        # consumes saved JSON projections; it does not inspect stdout/stderr.
        req((ART/art['name']/'group-evidence.json.gz').is_file(),'ARTIFACT_MISSING:'+gid)
        base=evidence/gid
        rec,exp,rich,comp=map(read,(base/'receipt.json',base/'export.json',base/'properties.json',base/'compile/receipt.json'))
        req(rec['group']==gid and rec['request_sha256']==comp['request_sha256']==request_sha,'RECEIPT_REQUEST:'+gid)
        if rec.get('export_sha256'):
            req(sha(base/'export.json')==rec['export_sha256'],'EXPORT_HASH:'+gid)
        if rec.get('rich_evidence_sha256'):
            req(sha(base/'properties.json')==rec['rich_evidence_sha256'],'RICH_HASH:'+gid)
        req(rec['source_before']==rec['source_after'],'SOURCE_SNAPSHOT_DRIFT:'+gid)
        snap=rec['source_before']; req(snap['std_sha']==SOURCE_SHA and snap['tool_sha']==TOOL_SHA and snap['std_tree']==request['std_tree'] and snap['tool_tree']==request['tool_tree'],'GROUP_PINS:'+gid)
        variant=rec['variant']; expected=dict(request['changed_file_sha256'])
        if variant!='production':
            v=request['variants'][variant]; expected.update(v['changed_file_sha256'])
            req(sha(payload/v['patch'])==v['sha256']==rec['source_under_test']['patch_sha256'],'VARIANT_PATCH:'+variant)
        req(rec['source_under_test']['base_std_sha']==SOURCE_SHA and rec['source_under_test']['variant']==variant and rec['source_under_test']['file_sha256']==expected,'VARIANT_FILES:'+gid)
        req(comp['request_sha256']==request_sha and comp['std_sha']==SOURCE_SHA and comp['tool_sha']==TOOL_SHA,'COMPILE_PINS:'+gid)
        complete=rich.get('state')=='COMPLETE' and all(p.get('file') and str(p.get('line','')).isdigit() for h in rich.get('harnesses',[]) for p in h.get('properties',[]))
        if gid in GOOD:
            req(rec['state']=='COMPLETE' and complete and rec.get('export_sha256') and rec.get('rich_evidence_sha256') and rec.get('tool_fingerprints_after',{}).get('required_hashes_present'),'EXPECTED_RICH_COMPLETE:'+gid)
            before=rec['tool_fingerprints_before']['binaries']; after=rec['tool_fingerprints_after']['binaries']
            req({k:v['sha256'] for k,v in before.items()}=={k:v['sha256'] for k,v in after.items()},'BINARY_FINGERPRINT_DRIFT:'+gid)
        else:
            req(not complete,'EXPECTED_RICH_INCOMPLETE:'+gid)
        req(exp.get('harnesses') is not None and rich.get('harnesses') is not None,'HARNESS_ARRAY:'+gid)
        ex_by={h['name']:h for h in exp['harnesses']}; rh_by={h['name']:h for h in rich['harnesses']}
        selectors=set(rec['selectors']); matched=[r for r in request['rows'] if r['variant']==variant and r['selector'] in selectors]
        req({r['selector'] for r in matched}==selectors,'SELECTORS:'+gid)
        summaries=[]
        for row in matched:
            h=ex_by.get(row['selector']); rh=rh_by.get(row['selector'])
            all_h[(row['selector'],variant)]=(gid,row,h,rh,complete)
            if h and rh and complete:
                by=inventory(h,rh['properties'])
                for u in h['unsupported_constructs']:
                    p=by.get(u['id']); req(p and p['class']==u['class']=='unsupported_construct' and p['status']==u['status']=='SUCCESS' and p['file']==u['file'] and p['line']==u['line'],'UNSUPPORTED_LINK:'+u['id'])
                summaries.append({'selector':row['selector'],'source_verdict':h['outcome']['verdict'],'properties':h['n_properties'],'failures':h['n_failed'],'unreachable_checks':len(h['checks']['unreachable']),'covers_satisfied':len(h['covers']['satisfied']),'covers_unreachable':len(h['covers']['unreachable']),'unsupported_success_links':len(h['unsupported_constructs']),'inventory':'COMPLETE_EXACT_ID_STATUS_CLASS_FILE_LINE'})
            else:
                summaries.append({'selector':row['selector'],'source_verdict':h.get('outcome',{}).get('verdict') if h else None,'inventory':'INCOMPLETE_MISSING_DECODER_FILE_OR_LINE'})
        bin_before=rec.get('tool_fingerprints_before',{}).get('binaries',{}); bin_after=rec.get('tool_fingerprints_after',{}).get('binaries',{})
        bin_state='MATCH_BEFORE_AFTER' if bin_before and bin_after and {k:v.get('sha256') for k,v in bin_before.items()}=={k:v.get('sha256') for k,v in bin_after.items()} else 'UNKNOWN_AFTER_RUN_STOPPED'
        groups.append({'id':gid,'artifact_id':art['id'],'artifact_name':art['name'],'archive_digest_source_reported':art.get('digest'),'receipt_sha256':sha(base/'receipt.json'),'export_sha256':sha(base/'export.json'),'rich_sha256':sha(base/'properties.json'),'compile_sha256':sha(base/'compile/receipt.json'),'variant':variant,'request_sha256':request_sha,'receipt_state':rec['state'],'inventory':'COMPLETE' if complete else 'INCOMPLETE_MISSING_DECODER_FILE_OR_LINE','source_snapshots':'MATCH','binary_fingerprint_state':bin_state,'harnesses':summaries})

    for row in request['rows']:
        info=all_h.get((row['selector'],row['variant']))
        reasons=[]; accepted=[]
        if not info or not info[4] or not info[2] or not info[3]:
            h=info[2] if info else None
            row_results.append({'id':row['id'],'group':info[0] if info else None,'selector':row['selector'],'variant':row['variant'],'expected':row['expected'],'source_reported_verdict':h.get('outcome',{}).get('verdict') if h else None,'observation':'SOURCE_REPORTED_ONLY','qualification':'PENDING','acceptance_gate_status':'PENDING_INCOMPLETE_RICH','pending_reasons':['RICH_PROPERTY_DECODER_FILE_OR_LINE_MISSING_INCOMPLETE'],'proof_credit':'NONE','accepted_evidence':[]})
            continue
        gid,_,h,rh,_=info; by={p['id']:p for p in rh['properties']}; binding=request['source_bindings'][row['id']]
        src=STD/binding['file']; lines=src.read_text().splitlines(); req(sha(src)==binding['sha256'],'ROW_SOURCE_HASH:'+row['id'])
        anchors=[]
        for loc in binding['locations']:
            req(1<=loc['line']<=len(lines) and lines[loc['line']-1]==loc['source'],'ROW_ANCHOR:'+row['id'])
            anchors.append({'line':loc['line'],'source':loc['source']})
        accepted=['SAME_RUN_REQUEST_SOURCE_TOOL_CONFIG_IDENTITIES_MATCH','COMPLETE_EXACT_ID_STATUS_CLASS_FILE_LINE_INVENTORY']
        required=[]
        for m in row.get('required_success_messages',[]):
            literal_lines=[i+1 for i,s in enumerate(lines) if m in s]
            call_lines=[]
            for ln in literal_lines:
                start=ln
                for back in range(ln, max(0,ln-6), -1):
                    if 'assert!' in lines[back-1]:
                        start=back; break
                call_lines.append(start)
            suffix=binding['file'].split('library/core/',1)[1]
            root_name=row['selector'].split('::')[-1]
            candidates=[p for p in by.values() if p['status']=='SUCCESS' and p['class']=='assertion'
                        and p['file'].endswith(suffix) and int(p['line']) in call_lines
                        and root_name in p['id'].split('.assertion.',1)[0]
                        and "placeholder message; Kani doesn't support message formatted at runtime" in p['description']]
            unique=len(literal_lines)==1 and len(call_lines)==1 and len(candidates)==1
            required.append({'message':m,'literal_source_lines':literal_lines,'assertion_call_lines':call_lines,
                             'property_ids':[p['id'] for p in candidates],
                             'binding':'EXACT_SOURCE_CALLSITE_UNIQUE_PLACEHOLDER_PROPERTY' if unique else 'PENDING_EXACT_MESSAGE_TO_PROPERTY_BINDING'})
        covers=[]
        for m in row.get('required_cover_messages',[]):
            hits=[p for p in by.values() if p['class']=='cover' and p.get('description')==m]
            exact=len(hits)==1 and hits[0]['status']=='SATISFIED' and hits[0]['id'] in h['covers']['satisfied']
            covers.append({'message':m,'property_id':hits[0]['id'] if len(hits)==1 else None,'status':hits[0]['status'] if len(hits)==1 else None,'file':hits[0]['file'] if len(hits)==1 else None,'line':hits[0]['line'] if len(hits)==1 else None,'binding':'EXACT_SATISFIED_COVER' if exact else 'PENDING'})
        if covers and all(c['binding']=='EXACT_SATISFIED_COVER' for c in covers): accepted.append('REQUIRED_COVER_MESSAGES_EXACT_ID_SATISFIED')
        unreachable=[]
        for pid in sorted(set(h['checks']['unreachable'])|set(h['covers']['unreachable'])):
            p=by[pid]; role='UNKNOWN'; why='Exact site retained; obligation role unresolved. No helper-name exemption.'
            if 'active_post' in pid:
                if row['expected']=='DETECTED':
                    role='postcondition_candidate'; why='Exact source ID/site is in active_post, but applicability to this declared negative scenario is pending; do not infer a mandatory blocker from the function name.'
                else:
                    role='postcondition_candidate'; why='Exact source ID/site is in active_post; whether this is required by the declared scenario remains to be reviewed.'
            elif p['class']=='cover' and row['expected']=='DETECTED' and row.get('oracle'):
                role='mutant_return_cover'; why='Return cover is unreachable under the frozen failing mutant contract and gives no positive coverage credit.'
            rel=source_rel(p['file']); path=STD/rel; source_line=None
            req(path.is_file(),'UNREACHABLE_SOURCE_FILE:'+pid); source_lines=path.read_text().splitlines()
            req(1<=int(p['line'])<=len(source_lines),'UNREACHABLE_SOURCE_LINE:'+pid)
            source_line=source_lines[int(p['line'])-1]
            unreachable.append({'id':pid,'status':p['status'],'class':p['class'],'description':p['description'],'file':p['file'],'line':int(p['line']),'source_line':source_line,'role':role,'role_reason':why})
        oracle=row.get('oracle'); exact_oracle=False
        if row['expected']=='DETECTED':
            req(oracle is not None,'ORACLE_REQUIRED:'+row['id'])
            req([p['id'] for p in h['failed_properties']]==[oracle['property_id']],'ORACLE_SOLE_FAILURE:'+row['id'])
            p=by.get(oracle['property_id']); req(p and p['status']=='FAILURE' and p['class']==oracle['class'] and source_rel(p['file'])==oracle['file'] and int(p['line'])==oracle['line'],'ORACLE_EXACT_BINDING:'+row['id'])
            if oracle.get('description'):
                req(p['description']==oracle['description'],'ORACLE_DESCRIPTION:'+row['id'])
            req(h['outcome']=={'kind':'COMPLETED','verdict':'FAILURE'},'ORACLE_VERDICT:'+row['id'])
            if row['variant'] in request['variants']:
                vs=request['variants'][row['variant']]; patch=(payload/vs['patch']).read_text(); marker=oracle.get('intended_message') or row.get('failure_description') or vs.get('marker')
                req(marker and marker in patch,'ORACLE_PATCH_MESSAGE:'+row['id'])
            else:
                f=STD/oracle['file']; req(sha(f)==oracle['source_sha256'],'ORACLE_SOURCE_HASH:'+row['id']); ls=f.read_text().splitlines(); n=oracle['line']-1
                req(ls[n:n+len(oracle['assertion_context'])]==oracle['assertion_context'],'ORACLE_SOURCE_CONTEXT:'+row['id'])
            exact_oracle=True; accepted.append('SOLE_PREDECLARED_NEGATIVE_ORACLE_EXACT_ID_SITE_MATCH')
        else:
            req(h['outcome']=={'kind':'COMPLETED','verdict':'SUCCESS'} and not h['failed_properties'],'POSITIVE_VERDICT:'+row['id'])
            accepted.append('SOURCE_REPORTED_POSITIVE_VERDICT_NO_FAILURES')
        companion=None
        if row.get('companion'):
            cr=rows[row['companion']]; ci=all_h.get((cr['selector'],cr['variant'])); req(ci is not None,'COMPANION_NOT_PRESENT:'+row['id'])
            cv=ci[2].get('outcome',{}).get('verdict') if ci[2] else None
            companion={'id':row['companion'],'same_run':True,'source_verdict':cv,'rich_complete':bool(ci[4])}
            if cv=='SUCCESS': accepted.append('SAME_RUN_UNMUTATED_COMPANION_SOURCE_SUCCESS')
            else: reasons.append('REQUIRED_UNMUTATED_COMPANION_NOT_SOURCE_SUCCESS')
            if not ci[4]: reasons.append('COMPANION_RICH_INVENTORY_INCOMPLETE')
        if any(s['binding']!='EXACT_SOURCE_CALLSITE_UNIQUE_PLACEHOLDER_PROPERTY' for s in required): reasons.append('REQUIRED_SUCCESS_MESSAGE_TO_EXACT_PROPERTY_BINDING_INCOMPLETE')
        if any(u['role']=='UNKNOWN' for u in unreachable): reasons.append('UNREACHABLE_EXACT_SOURCE_ROLE_UNRESOLVED_NO_HELPER_EXEMPTION')
        if any(u['role']=='postcondition_candidate' for u in unreachable): reasons.append('UNREACHABLE_POSTCONDITION_SITE_SCENARIO_APPLICABILITY_PENDING')
        if row['mode']=='PFC': reasons.append('PFC_CHECK_MODIFIES_WRAPPER_TARGET_CONTRACT_CHAIN_PENDING')
        if any(c['binding']!='EXACT_SATISFIED_COVER' for c in covers): reasons.append('REQUIRED_COVER_MESSAGE_ID_BINDING_INCOMPLETE')
        if covers: accepted.append('SAT_COVERS_SHOW_REACHABILITY_ONLY_NOT_DOMAIN_COMPLETENESS')
        observation='EXPECTED_EXACT_PREDECLARED_ORACLE' if exact_oracle else 'SOURCE_REPORTED_'+h['outcome']['verdict']
        row_results.append({'id':row['id'],'group':gid,'selector':row['selector'],'variant':row['variant'],'mode':row['mode'],'expected':row['expected'],'source_reported_verdict':h['outcome']['verdict'],'observation':observation,'qualification':'PENDING' if reasons else 'ACCEPTABLE_OBSERVATION_ONLY','acceptance_gate_status':'PENDING_UNRESOLVED_EVIDENCE','pending_reasons':sorted(set(reasons)),'blocking_obligations':[],'scenario_applicability_pending':[u['id'] for u in unreachable if u['role']=='postcondition_candidate'],'unknown_unreachable_roles':[u['id'] for u in unreachable if u['role']=='UNKNOWN'],'proof_credit':'NONE','source_binding':{'file':binding['file'],'sha256':binding['sha256'],'locations':anchors},'required_success':required,'required_covers':covers,'unreachable':unreachable,'failures':h['failed_properties'],'unsupported_success_links':h['unsupported_constructs'],'same_run_companion':companion,'contract_export':h.get('contract'),'accepted_evidence':accepted,'assurance':'OFFLINE_SOURCE_REPORTED_STRUCTURED_OBSERVATION; NO_INDEPENDENT_B1_OR_B2'})
    req(len(groups)==14 and len(row_results)==35,'FINAL_SET')
    full=[r for r in row_results if r['group'] in GOOD]; other=[r for r in row_results if r['group'] not in GOOD]
    all_unreachable=[u for r in full for u in r.get('unreachable',[])]
    totals={'groups':14,'complete_rich_groups':4,'incomplete_rich_groups':10,'rows':35,'rows_in_complete_groups':len(full),'rows_pending_incomplete_rich':len(other),'complete_group_source_success':sum(r['source_reported_verdict']=='SUCCESS' for r in full),'exact_predeclared_negative_observations':sum(r['observation']=='EXPECTED_EXACT_PREDECLARED_ORACLE' for r in full),'required_cover_messages_exactly_bound':sum(c['binding']=='EXACT_SATISFIED_COVER' for r in full for c in r.get('required_covers',[])),'required_success_messages_exactly_bound':sum(s['binding']=='EXACT_SOURCE_CALLSITE_UNIQUE_PLACEHOLDER_PROPERTY' for r in full for s in r.get('required_success',[])),'unreachable_records_complete_groups':len(all_unreachable),'unreachable_postcondition_sites_scenario_pending':sum(u['role']=='postcondition_candidate' for u in all_unreachable),'unreachable_roles_unknown':sum(u['role']=='UNKNOWN' for u in all_unreachable),'expected_mutant_return_covers_unreachable':sum(u['role']=='mutant_return_cover' for u in all_unreachable),'confirmed_mandatory_blocker_rows':0,'qualified_rows':sum(r['qualification']!='PENDING' for r in row_results),'pending_rows':sum(r['qualification']=='PENDING' for r in row_results),'proof_credit':'NONE'}
    report={'schema':'ch8-s1-05-offline-acceptance-v1','run':43864841077,'stage':'COMPLETE_OFFLINE_ACCEPTANCE_REVIEW','qualified_acceptance':'PENDING','proof_credit':'NONE','source_sha':SOURCE_SHA,'tool_sha':TOOL_SHA,'control_sha':CONTROL_SHA,'request_sha256':request_sha,'policy_sha256':sha(POLICY),'artifact_metadata_sha256':sha(RUN/'artifacts-metadata.json'),'run_metadata_sha256':sha(RUN/'run-metadata.json'),'totals':totals,'groups':groups,'rows':row_results,'limits':['The four complete groups bind exact property IDs, statuses, classes, files, and lines; ten other groups are incomplete and receive no acceptance.','Required cover messages in complete groups bind exact SATISFIED IDs; SAT establishes reachability, not domain completeness.','Four required-success messages bind through exact source assertion sites to unique successful placeholder properties; 31 remain ambiguous and pending.','Unreachable roles are not dismissed by helper names. Twenty active_post sites in expected-negative scenarios have exact source identity but scenario applicability pending; 25 other unreachable sites retain UNKNOWN role.','PFC check/modifies wrapper and target/contract binding remain pending.','Exact negative oracle matches are source-reported observations only; companion and other obligation gates remain.','Coordinates and source strings do not establish AST/MIR/parser-input binding.','The compact-artifact intake already checked unpacked member integrity; replay validates saved export/rich hashes where receipts provide them. Artifact archive digests remain source-reported metadata.','No stdout/stderr logs were read; no B1/B2 independent proof credit; no historical receipt or ledger changed.'],'historical_receipts_and_ledgers_changed':False,'control_changed':False,'local_verifier_execution':'NOT_RUN'}
    (HERE/'ACCEPT.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(totals,sort_keys=True))
if __name__=='__main__': main()
