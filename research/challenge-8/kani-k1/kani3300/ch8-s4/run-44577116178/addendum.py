#!/usr/bin/env python3
"""Planner addendum: exact U/domain reasoning and non-vacuity, offline only.

Preserves the original native evidence and original intake projections.
"""
import collections,copy,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
import replay as r
H=r.HERE
def read(n):return json.loads((H/n).read_text())
def main():
    checks=[]
    def need(x,label):
        if not x:raise AssertionError(label)
        checks.append(label)
    original='S4P2-r2 method and planner addendum, new run immutable input identities'
    preserved={}
    for n in ['group-evidence.json.gz','artifact-integrity.json','NATIVE-PROPERTIES.json','QUALIFICATION.json','U-ARGUMENTS.json','PROVENANCE.json','COST.json','PROTECTED.json','PREFIX.json','SERIAL-ORDER.json']:
        b=(H/n).read_bytes();preserved[n]={'bytes':len(b),'sha256':r.sha(b)}
    roots=read('ROOTS.json');req=roots['request'];qs=read('QUALIFICATION.json')['rows'];props=read('NATIVE-PROPERTIES.json');us=read('U-ARGUMENTS.json')['instances'];pv=read('PROVENANCE.json')
    source_cache={}
    def source(f):
        if f not in source_cache:source_cache[f]=r.blob(r.SOURCE,req['std_sha'],f)
        return source_cache[f]
    def source_block(f,a,b):
        raw=source(f);ls=raw.decode().splitlines();return {'source_sha':req['std_sha'],'file':f,'file_sha256':r.sha(raw),'lines':[a,b],'text':'\n'.join(f'{i+1}: {ls[i]}' for i in range(a-1,b))}
    helper='library/core/src/slice/sort/shared/smallsort.rs'
    ls=source(helper).decode().splitlines()
    anchors={339:'    let len = v.len();',340:'    if len < 2 {',341:'        return;',350:'    let len_div_2 = len / 2;',351:'    let no_merge = len < 18;',354:'    let initial_region_len = if no_merge { len } else { len_div_2 };',360:'        let presorted_len = if region.len() >= 13 {',363:'        } else if region.len() >= 9 {',370:'        insertion_sort_shift_left(region, presorted_len, is_less);',372:'        if no_merge {',373:'            return;',381:'        unsafe { region = slice::from_raw_parts_mut(v_base.add(len_div_2), len - len_div_2) };',389:'        bidirectional_merge(slice::from_raw_parts_mut(v_base, len), scratch_base, is_less);'}
    for n,line in anchors.items():need(ls[n-1]==line,'exact helper branch anchor '+str(n))
    branch_cases=[]
    for q in qs[4:]:
        rid=q['id'];domain=req['domains'][rid];lo,hi=domain['length_interval'];f=q['source_binding']['file'];lines=source(f).decode().splitlines()
        start=q['native_registration']['original_start_line'] if 'original_start_line' in q['native_registration'] else next(i+1 for i,l in enumerate(lines) if l=='fn '+rid+'() {')
        end=next(i+1 for i in range(start,len(lines)) if lines[i]=='}')
        calls=[{'line':i+1,'source':lines[i]} for i in range(start,end) if '    small_sort_network(' in lines[i]]
        expected=[f'[1..{hi+1}]']
        need(len(calls)==len(expected) and all(e in c['source'] for c,e in zip(calls,expected)),'literal actual helper calls '+rid)
        attrs=q['native_registration']['attributes']
        need(q['mode']=='Original' and q['target'] is None and attrs['kind']=='Proof' and attrs['stubs']==[] and attrs['verified_stubs']==[] and domain['summary_edges']==[],'actual Original helper instance no replacement '+rid)
        need((lo,hi) in [(8,8),(9,9),(13,13),(17,17)] and domain['type']=='u8' and domain['comparator']=='KeyLess<u8>' and domain['allocation']==34 and domain['base']==1,'exact helper call domain '+rid)
        path = {8:'region.len=8 fails both >=13 and >=9, hence presorted_len=1; insertion processes suffix indices1..7',9:'region.len=9 fails >=13 and takes >=9: actual sort9_optimal runs, presorted_len=9; insertion has no suffix',13:'region.len=13 takes >=13: actual sort13_optimal runs, presorted_len=13; insertion has no suffix',17:'region.len=17 takes >=13: actual sort13_optimal handles prefix13, presorted_len=13; insertion processes indices13..16'}[hi]
        argument=f'Literal slice length={hi}; len<2 at340 is false. At351 no_merge=({hi}<18)=true; initial_region_len at354 is exactly len. In the first region, '+path+'. At370 insertion_sort_shift_left is called. If it returns normally, unchanged no_merge forces return at372-373; otherwise no normal continuation reaches merge. Thus neither second-region update381 nor bidirectional_merge call389 is reachable. This argument uses exact caller branches, never the callee intrinsics::assume. For censored roots this is source branching only, not a successful native theorem.'
        branch_cases.append({'root':rid,'selector':q['selector'],'invocation_id':q['invocation_id'],'namespace':q['namespace'],'domain':domain,'harness_source':source_block(f,start,end),'literal_helper_calls':calls,'native_registration':q['native_registration'],'member_identities':q['members'],'source_branch_argument':argument,'merge_call_389_reachable':False,'source_origin_assurance':'Frozen Original source/registration context; no independent AST/MIR/emitter cause claimed'})
    helper_binding={'schema':'s4p3-helper-domain-branch-binding-v1','source_sha':req['std_sha'],'helper_source':source_block(helper,332,391),'exact_branch_anchors':anchors,'cases':branch_cases,'merge_properties_source':source_block(helper,971,1006),'insertion_source':source_block(helper,709,737),'assurance':'Bounded source-reported branch argument; not inferred from native UNREACHABLE status; no callee intrinsics::assume used as proof premise'}
    r.write('HELPER-BRANCH-BINDING.json',helper_binding)
    batch='library/core/src/slice/sort/shared/smallsort/verify/sorting_s2_batch.rs'
    checker='library/core/src/slice/sort/shared/smallsort/verify/sorting_model.rs'
    fixture_bindings={root:[source_block(checker,91,120),source_block(batch,130,149)] for root in ('checker_order_corrupt','checker_count_corrupt','sort13_weak')}
    fixture_bindings['sort13_weak'].append(source_block(batch,178,249))
    fixture_bindings['s4p_cell_count_corrupt']=[source_block(checker,91,120),source_block('library/core/src/slice/sort/shared/smallsort/verify/sorting_s4_partition.rs',21,30)]
    r.write('FIXTURE-PATH-BINDING.json',{'source_sha':req['std_sha'],'cases':fixture_bindings,'scope':'Exact fixed negative fixture inputs, checker early returns, and weak stub/copy source; no new native execution'})
    domain_us=[]
    for u in us:
        x=copy.deepcopy(u);root=u['root'];p=u['property'];ident=p['id'];f=u['source_file'];n=u['source_line'];raw=source(f)
        need(r.sha(raw)==u['source_sha256'] and p['line']==str(n) and p['status']=='UNREACHABLE','exact U site/source identity '+root+'/'+ident)
        kind=None;arg=None;premises=[]
        if root in ('checker_order_corrupt','sort13_weak') and f.endswith('/sorting_model.rs'):
            kind='SOURCE_SITE_EXCLUDED'
            if root=='checker_order_corrupt':arg='The frozen input snapshot is [1,2], output is [2,1]. At active_post i=1, values[1]=1 < values[0]=2, so line98 returns false before the order increment100 and every count-loop site106-118.'
            else:arg='The frozen negative starts descending [12,11,...,0]. Every copied-network comparator uses s2_swap_seam, replaced in this invocation by the empty weak_swap body; the 13 values therefore remain descending. At active_post i=1, values[1]=11 < values[0]=12, so line98 returns false before increment100 and every count-loop site106-118.'
        elif root=='checker_count_corrupt' and f.endswith('/sorting_model.rs'):
            kind='SOURCE_SITE_EXCLUDED';arg='The snapshot is 32 ones and output is 31 ones followed by2. The order loop does not return false. The first count query is1, old_count=32 and new_count=31. Line115 detects the mismatch and line116 returns false before outer increment118.'
        elif root=='s4p_cell_count_corrupt' and f.endswith('/sorting_model.rs'):
            kind='SOURCE_SITE_EXCLUDED';arg='Initialized logical Cell snapshot [0,1] is changed to sorted [0,0]. The first count query is0, old_count=1 and new_count=2. Line116 returns false before outer increment118; this is the intended checker-only count failure.'
        elif '::bidirectional_merge::<' in ident or ('::small_sort_network::<' in ident and n in (350,381)):
            kind='SOURCE_SITE_EXCLUDED';case=next(c for c in branch_cases if c['root']==root);arg=case['source_branch_argument']+' The exact reported site '+f+':'+str(n)+' is inside the excluded merge body.' if '::bidirectional_merge::<' in ident else case['source_branch_argument']+' The exact reported network site '+str(n)+' is after the applicable return.'
            premises.append({'helper_binding':'HELPER-BRANCH-BINDING.json','helper_binding_sha256':r.sha((H/'HELPER-BRANCH-BINDING.json').read_bytes()),'root':root,'invocation_id':u['invocation_id']})
        else:
            # S1 permits per-site definedness arguments for generated arithmetic/bounds
            # checks. Do not turn these into an invented check-site/MIR reachability trace.
            kind='GENERATED_FAILURE_EDGE_EXCLUDED';arg=u['source_local_argument']+' Hence the generated arithmetic/bounds error edge cannot be taken in this exact root domain. This is the S1 source-local definedness argument; why the producer reports this check site itself UNREACHABLE remains UNKNOWN, not inferred from SUCCESS roles or SAT covers.'
        if root in fixture_bindings:premises.append({'fixture_binding':'FIXTURE-PATH-BINDING.json','fixture_binding_sha256':r.sha((H/'FIXTURE-PATH-BINDING.json').read_bytes()),'root':root})
        x.update(domain_unreachability_argument=arg,argument_kind=kind,branch_binding=premises,exact_source_line=raw.decode().splitlines()[n-1],native_UNREACHABLE_cause='SOURCE_PATH_EXCLUDED_AT_APPROVED_SOURCE_REPORTED_LEVEL; compiler/emitter/MIR causality UNKNOWN' if kind=='SOURCE_SITE_EXCLUDED' else 'UNKNOWN_CHECK_SITE_OR_EMITTER_CAUSE; exact generated error edge excluded by source premises',assessment='S1_SOURCE_LOCAL_DOMAIN_CANDIDATE' if arg else 'BLOCKER')
        need(x['property']==u['property'] and x['invocation_id']==u['invocation_id'] and bool(arg),'U domain argument preserves exact identity '+root+'/'+ident);domain_us.append(x)
    expected={(rid,p['id']) for rid,v in props.items() for p in (v['properties'] or []) if p['status']=='UNREACHABLE'}
    need(len(domain_us)==len(expected)==40 and {(x['root'],x['property']['id']) for x in domain_us}==expected,'all40 exact U instances covered, no missing/additional/duplicate')
    need(sum('::bidirectional_merge::<' in x['property']['id'] for x in domain_us)==8,'all8 exact merge U instances bound to helper branching')
    r.write('U-DOMAIN-ARGUMENTS.json',{'schema':'s4p3-per-instance-domain-U-candidates-v1','run':44577116178,'attempt':1,'source':req['std_sha'],'tool':req['tool_sha'],'request_sha256':pv['request_sha256'],'artifact_payload':pv['compact_payload'],'instances':domain_us,'count':len(domain_us),'argument_kinds':dict(collections.Counter(x['argument_kind'] for x in domain_us)),'blockers':[x for x in domain_us if x['assessment']=='BLOCKER'],'method':'S1 per-site source-path exclusion or generated failure-edge exclusion; these are distinct. Literal check-site/emitter cause is not independently established for source-local definedness cases. No relabelling of native statuses.','admission':False})
    cases=[]
    for q in qs:
        rid=q['id'];native=q['members']['properties.json'];declared=next(row for row in req['rows'] if row['id']==rid);positive=rid in req['domains'];blockers=[]
        if props[rid]['properties'] is None:
            cases.append({'root':rid,'selector':q['selector'],'invocation_id':q['invocation_id'],'namespace':q['namespace'],'positive':True,'required_assertion_roles':q['roles'],'declared_covers':declared['required_cover_messages'],'native_covers':None,'native_properties_count':None,'safety_checks_count':None,'all_exported_unwind_properties':None,'requested_unwind':declared['unwind'],'resolved_unwind':None,'U_arguments':None,'inventory_scope':'INCOMPLETE; UNKNOWN, not zero/empty/vacuous success','blockers':['BLOCKER: no completed same-invocation native/rich inventory','BLOCKER: required SUCCESS roles and all six SAT covers unestablished','BLOCKER: safety/unwind/U/location inventories unknown'],'candidate_status':'BLOCKER','admission':False})
            need(q['native_verdict']=='UNKNOWN' and q['strict_expected_match'] is False,'incomplete root remains BLOCKER '+rid)
            continue
        ps=props[rid]['properties']
        roles=[copy.deepcopy(x) for x in q['roles'] if x['required']['class']=='assertion'];covers=[p for p in ps if p['class']=='cover'];safety=[p for p in ps if p['class']!='cover'];unwind=[p for p in ps if p['class']=='unwind'];root_us=[u for u in domain_us if u['root']==rid]
        if positive and (len(roles)!=4 or any(not x['native_matches'] or any(p['status']!='SUCCESS' for p in x['native_matches']) for x in roles)):blockers.append('BLOCKER: missing, failed or unreached required positive role')
        reachability=None
        if positive:
            role_lines=[x['required']['line'] for x in roles];cover_lines=[int(p['line']) for p in covers]
            if not cover_lines or max(role_lines)>=min(cover_lines):blockers.append('BLOCKER: post-role cover reachability is not source-bound')
            reachability='All declared covers occur after the active-model assertion, original-helper call, postcondition assertion, fixed 0..34 frame loop and arbitrary outside-canary assertion in the exact frozen harness body. Each SAT cover supplies a continuing path through those required roles; the frame loop has34 iterations and is not an empty loop. SUCCESS for all four exact labelled native roles supplies their retained verification results. SAT is used only for non-vacuity, never as a substitute for a U argument.'
            need(bool(cover_lines) and max(role_lines)<min(cover_lines),'SAT covers after all required assertion roles '+rid)
        if len(covers)!=declared['required_cover_count'] or {p['description'] for p in covers}!=set(declared['required_cover_messages']) or any(p['status']!='SATISFIED' for p in covers):blockers.append('BLOCKER: a declared cover is missing or not SAT')
        if any(u['assessment']=='BLOCKER' or not u['domain_unreachability_argument'] for u in root_us) or {u['property']['id'] for u in root_us}!={p['id'] for p in safety if p['status']=='UNREACHABLE'}:blockers.append('BLOCKER: unexplained U')
        if len({p['id'] for p in ps})!=len(ps) or len(ps)!=q['n_properties'] or len(safety)!=q['checks']['total'] or len(covers)!=q['covers_summary']['total']:blockers.append('BLOCKER: incomplete or inconsistent native inventory')
        if any(p['status'] not in ('SUCCESS','FAILURE','UNREACHABLE') for p in safety) or (positive and any(p['status']=='FAILURE' for p in safety)) or any(p['status']!='SUCCESS' for p in unwind):blockers.append('BLOCKER: unknown/failed safety or unwind property')
        cases.append({'root':rid,'selector':q['selector'],'invocation_id':q['invocation_id'],'namespace':q['namespace'],'positive':positive,'required_assertion_roles':roles,'required_role_reachability_argument':reachability,'declared_covers':declared['required_cover_messages'],'native_covers':covers,'native_properties_count':len(ps),'safety_checks_count':len(safety),'complete_safety_ids_by_status':{s:[p['id'] for p in safety if p['status']==s] for s in ('SUCCESS','FAILURE','UNREACHABLE')},'complete_class_status_counts':q['class_status_counts'],'full_native_dictionary_inventory':{'path':'NATIVE-PROPERTIES.json','file_sha256':r.sha((H/'NATIVE-PROPERTIES.json').read_bytes()),'root':rid,'authenticated_member':native},'unwind_value':q['resolved_unwind'],'all_exported_unwind_properties':unwind,'unwind_scope':'Exact exported inventory, including zero residual assertions where applicable; no unexported check or larger-length sufficiency claim.','U_arguments':{'path':'U-DOMAIN-ARGUMENTS.json','count':len(root_us),'ids':[u['property']['id'] for u in root_us]},'blockers':blockers,'candidate_status':'BLOCKER' if blockers else 'READY_FOR_SEPARATE_BOUNDED_SOURCE_REPORTED_REVIEW','producer_s3_expected_match':False,'admission':False})
        need(not blockers,'case non-vacuity/complete safety/U coverage '+rid)
    need([len(c['native_covers']) if c['native_covers'] is not None else None for c in cases[4:]]==[6,6,None,None],'N8/N9 six SAT each; N13/N17 covers UNKNOWN')
    need(req['unreachable_admission']=={'mode':'REJECT_ALL','proposal':'S3-U-SITE-REVIEW-v1','enabled':False,'unknown':'REJECT','role_unreachable':'REJECT'},'original REJECT_ALL/proposalDISABLED policy unchanged')
    need(all(q['strict_expected_match'] is False and q['canonical']['s3_expected_match'] is False for q in qs),'all8 original s3_expected_match=False preserved')
    need(read('RUN-METADATA.json')['conclusion']=='failure' and read('PREFIX.json')['terminal']['state']=='SELECTED_PARTIAL','workflow FAILURE/campaign SELECTED_PARTIAL history unchanged')
    r.write('NON-VACUITY.json',{'schema':'s4p3-same-invocation-non-vacuity-v1','run':44577116178,'attempt':1,'cases':cases,'blocker_rule':'Each unexplained U, unreached/nonSUCCESS required positive role, incomplete safety/unwind inventory or nonSAT required cover is a BLOCKER for that case. No waiver/admission applied.','native_history':{'workflow':'FAILURE','campaign':'SELECTED_PARTIAL','unreachable_policy':'ZERO_U/REJECT_ALL','proposal_enabled':False,'s3_expected_match_all_rows':False},'admission':False})
    cost=read('COST.json')
    # Bounded guard checks of the new review checklist itself; no policy activation.
    def blockers_for_case(roles,covers,arguments):
        return (['required role'] if len(roles)!=4 or any(not rs or any(p['status']!='SUCCESS' for p in rs) for rs in roles) else [])+(['cover'] if any(p['status']!='SATISFIED' for p in covers) else [])+(['unexplained U'] if any(not x for x in arguments) else [])
    base=cases[5];rr=[x['native_matches'] for x in base['required_assertion_roles']];cc=base['native_covers'];aa=[u['domain_unreachability_argument'] for u in domain_us if u['root']==base['root']]
    need(blockers_for_case(rr,cc,aa)==[],'actual N9 checklist non-vacuity')
    bad=copy.deepcopy(rr);bad[0][0]['status']='UNREACHABLE';need('required role' in blockers_for_case(bad,cc,aa),'unreached required role yields BLOCKER')
    need('required role' in blockers_for_case(rr[:-1],cc,aa),'missing required role yields BLOCKER')
    bad=copy.deepcopy(cc);bad[0]['status']='UNSATISFIABLE';need('cover' in blockers_for_case(rr,bad,aa),'nonSAT length cover yields BLOCKER')
    need('unexplained U' in blockers_for_case(rr,cc,aa[:-1]+[None]),'unexplained U yields BLOCKER')
    for n,entry in preserved.items():
        b=(H/n).read_bytes();need(len(b)==entry['bytes'] and r.sha(b)==entry['sha256'],'original evidence and projections byte-preserved '+n)
    r.write('ADDENDUM-VALIDATION.json',{'status':'PASS','checks_count':len(checks),'checks':checks,'method_reference':{'run':44548842328,'original_intake_commit':'5c52edd71ad20f3f5b89257ed54836b2f43e14c0','planner_addendum':'run-44548842328/addendum.py'},'preserved_original_files':preserved,'scope':'Source anchors and domain/instance reasoning, exact U bijection, full native inventory/non-vacuity; offline targeted checks only. No acquisition/native/full Validate/CI.','case_blockers':[{ 'root':c['root'],'blockers':c['blockers']} for c in cases if c['blockers']],'admission':False})
    print(json.dumps({'status':'PASS','checks':len(checks),'U':len(domain_us),'U_kinds':dict(collections.Counter(u['argument_kind'] for u in domain_us)),'merge_U_bound_to_helper':8,'complete_positive_cases':2,'blocked_positive_cases':2}))
if __name__=='__main__':main()
