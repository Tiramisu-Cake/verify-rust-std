#!/usr/bin/env python3
"""Bounded reporting replay of sealed d29 intake; no native/full reader run."""
import ast, copy, gzip, hashlib, json, subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
BASE=HERE.with_name("run-44416629057")
G0=HERE.parents[5]
BASE_COMMIT="d29ab46dbbb45d7106fa30c3ac04bb419a2ac286"
REVIEW_COMMIT="a9fe0055aab3279e3f5bb71bde9667925da80e65"
TASK_COMMIT=ADMISSION_COMMIT="f74025e493a627962842e8f7bc6a2766d33dd300"
SOURCE_COMMIT="513341f41ce53833a279571401c924bdddddb6c8"
COMPACT_SHA="b9a02491bfb360eb17a13ab6f7fea78108d0371a7e8033f277674fb33213bed0"
POSITIVE_ROOTS=("s3_swap_u8_geometry","s3_sort4_u8_separate","s3_sort4_u8_same_alloc","s3_merge8_u8_separate")

def sha(b):return hashlib.sha256(b).hexdigest()
def read(n):return json.loads((BASE/n).read_bytes())
def write(n,v):(HERE/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+"\n")
def blob(rev,path):return subprocess.check_output(["git","-C",str(G0),"show",rev+":"+path])

def domain(rid):
    return {'checker_order_corrupt':'Fixed [1,2] -> [2,1]; length2 order corruption.','checker_count_corrupt':'Fixed [1;32], output[31]=2; length32 multiplicity corruption.','sort13_weak':'Fixed descending length13 [12u8,11,10,9,8,7,6,5,4,3,2,1,0] at sorting_s2_batch.rs:147; exact source-bound sort13_fault_network caller copy with ordinary s2_swap_seam -> weak_swap replacement; negative only, no actual sort13 proof.','s3_swap_u8_geometry':'Initialized arbitrary [u8;34], base0..20, a,b0..12 including equal/reversed; exact transfer and all outside frame.','s3_sort4_u8_separate':'Arbitrary initialized src[u8;6], src[1..5], separate MaybeUninit dst[6] output[1..5]; initialized canaries0/5, typed output loads, full source frame.','s3_sort4_u8_same_alloc':'Arbitrary before[u8;48]; src,dst0..44, length4 nonoverlap either order, all outside destination initialized; output initially MaybeUninit; full source/outside frame and symbolic canary, typed output loads.','s3_insert_tail_u8_rel16':'Initialized arbitrary [u8;34], begin1..16 tail1..16; sorted prefix, active length2..17, full outside frame.','s3_merge8_u8_separate':'Arbitrary src[u8;10], src[1..9] two sorted halves4+4; separate MaybeUninit dst[10], initialized canaries0/9 and typed output loads.','s3_merge8_u8_same_alloc':'Arbitrary before[u8;48]; src,dst0..40, nonoverlap length8 either order; sorted halves4+4; only source range borrowed, raw destination; initially uninitialized output, initialized outside; typed output loads and full source/outside frame.'}[rid]


def validate_guards(records, expected):
    """Reporting consistency only; this does not replace strict producer policy."""
    assert isinstance(records,list) and len(records)==4, 'four guard records required'
    assert len({x['id'] for x in records})==4, 'duplicate guard ID'
    assert all(x['class']=='unsupported_construct' and x['status']=='SUCCESS'
               for x in records), 'only exact SUCCESS guard records supported'
    assert all(all(k in x for k in ('id','description','class','status','file','line','trace_available'))
               for x in records), 'native guard fields missing'
    assert records==expected, 'native guard fields/order differ from sealed export'

def main():
    checks=[]
    def need(value,label):
        assert value,label
        checks.append(label)
    def rejects(fn,label):
        try:fn()
        except (AssertionError,KeyError,TypeError):checks.append(label)
        else:raise AssertionError('accepted adverse reporting case: '+label)

    # All base files must still be the exact committed intake. No broad review rerun.
    rel=str(BASE.relative_to(G0))
    manifest=read('MANIFEST.json')
    need((BASE/'MANIFEST.json').read_bytes()==blob(BASE_COMMIT,rel+'/MANIFEST.json'),
         'base manifest matches exact d29 commit')
    for name,meta in manifest['files'].items():
        b=(BASE/name).read_bytes()
        need(sha(b)==meta['sha256'] and len(b)==meta['bytes'],'sealed base file '+name)
    need((BASE/'MANIFEST.sha256').read_bytes()==blob(BASE_COMMIT,rel+'/MANIFEST.sha256'),
         'base hash manifest matches exact d29 commit')
    for name in ('group-evidence.json.gz','NATIVE.json','COST.json','COST.md','PREFIX-REPLAY.json',
                 'PREFIX-REPLAY.md','SOURCE-GATES.json','ROOTS.csv','artifact-integrity.json',
                 'compact-metadata.json','member-catalogue.json','github-run.json','github-jobs.json',
                 'github-job-collection.json','github-artifacts.json','CONNECTOR-LIMIT.json','acquire.py'):
        need((HERE/name).read_bytes()==(BASE/name).read_bytes(),'unchanged inherited '+name)
    gz=(HERE/'group-evidence.json.gz').read_bytes()
    need(sha(gz)==COMPACT_SHA,'same compact SHA256')
    packet=json.loads(gzip.decompress(gz))
    def member(name):
        e=packet['files'][name]
        need(e.get('encoding','utf-8')=='utf-8','structured UTF-8 '+name)
        b=e['text'].encode()
        need(len(b)==e['bytes'] and sha(b)==e['sha256'],'structured digest '+name)
        return json.loads(b)

    q=read('QUALIFICATION.json');inventory=read('INVENTORY.json');native=read('NATIVE.json')
    source_path='library/core/src/slice/sort/shared/smallsort/verify/sorting_s2_batch.rs'
    source=subprocess.check_output(['git','-C','/root/verify-rust-std-ch8-s3-1-final-w13',
                                    'show',SOURCE_COMMIT+':'+source_path])
    lines=source.decode().splitlines()
    need(lines[146].strip()=='let mut v = [12u8,11,10,9,8,7,6,5,4,3,2,1,0]; let before = v;',
         'W14-01 exact fixed descending fixture at source line147')
    need(lines[143]=='#[kani::stub(s2_swap_seam,weak_swap)]' and
         lines[147].strip()=='sort13_fault_network(&mut v,&mut KeyLess::<u8>::new());' and
         'S2_NEG_SORT13_WEAK' in lines[148], 'W14-01 exact ordinary weak_swap seam/caller/literal')
    need('unsafe fn weak_swap' in lines[141] and lines[141].endswith('{}'),
         'W14-01 ordinary weak_swap body retained')
    rows={r['id']:r for r in q['rows']}
    for rid,r in rows.items():
        if rid!='sort13_weak':need(domain(rid)==r['bindings']['source_domain'],rid+' domain unchanged')
    rows['sort13_weak']['bindings']['source_domain']=domain('sort13_weak')
    source_binding={'commit':SOURCE_COMMIT,'file':source_path,'sha256':sha(source),
                    'fixture_line':147,'fixture':list(range(12,-1,-1)),
                    'ordinary_stub':'s2_swap_seam -> weak_swap','stub_attribute_line':144,
                    'caller_line':148,'literal_failure_line':149,'negative_scope':'fixed fixture only'}
    rows['sort13_weak']['bindings']['negative_fixture']=source_binding
    fixture_text='['+','.join(str(x)+('u8' if i==0 else '') for i,x in enumerate(source_binding['fixture']))+']'
    need(fixture_text in domain('sort13_weak') and 'Fixed descending length13' in domain('sort13_weak')
         and 'arbitrary' not in domain('sort13_weak') and 's2_swap_seam -> weak_swap' in domain('sort13_weak'),
         'W14-01 generated domain matches source fixture and exact ordinary seam')

    guards={}
    for rid in POSITIVE_ROOTS:
        prefix='groups/s3-'+rid+'/'
        export=member(prefix+'export.json')['harnesses'][0]
        props=member(prefix+'properties.json')['harnesses'][0]['properties']
        exact=export['unsupported_constructs']
        validate_guards(exact,native[rid]['harness']['unsupported_constructs'])
        rich=[p for p in props if p['class']=='unsupported_construct']
        need(len(rich)==4 and all(all(p[k]==x[k] for k in ('id','description','class','status','file','line'))
             for x in exact for p in rich if p['id']==x['id']) and
             {p['id'] for p in rich}=={x['id'] for x in exact},rid+' exact export/rich guard agreement')
        rows[rid]['unsupported_constructs']=copy.deepcopy(exact)
        ir=next(r for r in inventory['selected'] if r['id']==rid)
        ir['unsupported_constructs']=copy.deepcopy(exact)
        validate_guards(rows[rid]['unsupported_constructs'],exact)
        validate_guards(ir['unsupported_constructs'],exact)
        guards[rid]=copy.deepcopy(exact)
        for status in ('FAILURE','FAILED','UNKNOWN','UNREACHABLE','UNDETERMINED',None):
            bad=copy.deepcopy(exact);bad[0]['status']=status
            rejects(lambda:validate_guards(bad,exact),rid+' reject guard status '+str(status))
        rejects(lambda:validate_guards(exact[:-1],exact),rid+' reject missing guard')
        rejects(lambda:validate_guards([],exact),rid+' reject inaccurate empty inventory')
        bad=copy.deepcopy(exact);del bad[0]['description']
        rejects(lambda:validate_guards(bad,exact),rid+' reject missing native field')
        for field in ('id','description','class','file','line','trace_available'):
            bad=copy.deepcopy(exact);bad[0][field]='altered'
            rejects(lambda:validate_guards(bad,exact),rid+' reject altered '+field)
        need(rows[rid]['native_check_counts']==next(r for r in read('QUALIFICATION.json')['rows'] if r['id']==rid)['native_check_counts'],
             rid+' native counts/status partitions unchanged')
    need(sum(map(len,guards.values()))==16,'W14-02 four SUCCESS guards per four roots/16 total')

    # Exercise only the existing small predicate, isolated from runner/import side effects.
    policy=subprocess.check_output(['git','-C','/root/kani-ch8-s3-1-r2-control-w13','show',
             'cb63033ffcde918f4341146e56373476b8eeb569:ch8-s1-control/s3_policy.py'])
    function=next(n for n in ast.parse(policy).body if isinstance(n,ast.FunctionDef) and n.name=='expected_observation')
    namespace={'Path':Path}
    exec(compile(ast.Module(body=[function],type_ignores=[]),'<pinned expected_observation>','exec'),namespace)
    predicate=namespace['expected_observation']
    synthetic_h={'unsupported_constructs':[],'outcome':{'kind':'COMPLETED','verdict':'SUCCESS'},
                 'checks':{'total':1,'success':1,'failure':[]},'covers':{'total':0,'satisfied':[]}}
    for key in ('unreachable','undetermined','error','unknown','other'):
        synthetic_h['checks'][key]=[]
        synthetic_h['covers'][key]=[]
    synthetic_h['covers']['unsatisfiable']=[]
    synthetic={'state':'RECORDED_OBSERVATION','outcome':'RECORDED','source_root':'/synthetic',
               'harness':synthetic_h}
    synthetic_row={'selector':'synthetic','expected':'SUCCESS','required_cover_messages':[],
                   'required_cover_count':0,'roles':[]}
    synthetic_properties={'name':'synthetic','properties':[{'id':'synthetic.assertion.1',
                          'class':'assertion','status':'SUCCESS'}]}
    need(predicate(synthetic_row,synthetic,synthetic_properties),'isolated strict-predicate synthetic baseline accepted')
    for rid,exact in guards.items():
        candidate=copy.deepcopy(synthetic);candidate['harness']['unsupported_constructs']=exact
        need(not predicate(synthetic_row,candidate,synthetic_properties),rid+' strict predicate rejects SUCCESS guard array independently of U')

    admission_path=str((HERE.parent/'admission-r2-location'/'ADMISSION.json').relative_to(G0))
    admission_bytes=blob(ADMISSION_COMMIT,admission_path);admission=json.loads(admission_bytes)
    need((G0/admission_path).read_bytes()==admission_bytes,'exact f740 admission bytes')
    need(admission['overall_qualification']=='PENDING_REPORTING_CORRECTIONS_AND_DELTA_REVIEW' and
         admission['producer_policy']=='REJECT_ALL; proposalDISABLED; strict0/9 unchanged',
         'accepted location gate does not grant overall qualification or producer PASS')
    same_props=member('groups/s3-s3_sort4_u8_same_alloc/properties.json')['harnesses'][0]['properties']
    prop=next(p for p in same_props if p['id']==admission['exact_property']['id'])
    need(prop==admission['exact_property'] and prop['file'] is None and prop['line'] is None,
         'full admitted exact tuple retained including present null coordinates')
    need(admission['protected_identity']['compact_sha256']==COMPACT_SHA and
         admission['independent_review_commit']==REVIEW_COMMIT and admission['intake_commit']==BASE_COMMIT,
         'admission full protected identity and exact review/base references')
    admission_ref={'commit':ADMISSION_COMMIT,'path':admission_path,'sha256':sha(admission_bytes),
                   'decision':admission,'scope':'Exact reversible location metadata gate only; no runtime application.'}
    write('ADMISSION-REFERENCE.json',admission_ref)
    rows['s3_sort4_u8_same_alloc']['S1_assessment']='PROVISIONALLY_ELIGIBLE_EXACT_LOCATION_GATE_ADMITTED_OVERALL_PENDING_DELTA'
    rows['s3_sort4_u8_same_alloc']['admission']='Exact location metadata gate admitted at f740; overall qualification pending SAME14 delta and root/coordinator assessment; independent proof NONE.'
    q['decision_required']=['W14-01/W14-02 correction awaits SAME14 exact delta and root/coordinator overall case assessment.',
                            'Exact location metadata gate already accepted at '+ADMISSION_COMMIT+'; runtime reader and producer UNKNOWN unchanged.',
                            'No leaf is an assumed summary for S3-2; caller domains/frame/init/locality must separately match.']
    q['successful_unsupported_guard_inventory']={'per_completed_positive':4,'total':16,'roots':guards,
        'meaning':'Successful native unsupported guards retained verbatim; no executed unsupported failure established. FAILED/UNKNOWN are never accepted as SUCCESS.',
        'strict_producer':'Nonempty arrays still rejected independently of U; REJECT_ALL/disabled proposal and 0/9 unchanged.'}
    q['location_metadata_admission_reference']='ADMISSION-REFERENCE.json'
    q['overall_qualification']='PENDING_SAME14_DELTA_AND_ROOT_COORDINATOR_CASE_ASSESSMENT'
    need(q['U_instances']==read('QUALIFICATION.json')['U_instances'],'all42 U records/arguments unchanged')
    need(all(r['strict_expected_match'] is False for r in q['rows']),'strict0/9 unchanged')
    write('QUALIFICATION.json',q);write('INVENTORY.json',inventory)
    gap=read('METADATA-GAP.json')
    gap['remaining']='Exact reversible location metadata gate accepted coordinator+planner at '+ADMISSION_COMMIT+'; overall qualification pending reporting delta and root/coordinator case assessment. Actual source origin remains UNKNOWN; runtime repair NOT_APPLIED.'
    gap['location_metadata_admission_reference']='ADMISSION-REFERENCE.json'
    write('METADATA-GAP.json',gap)
    result=read('RESULT.json');result.pop('S1_provisional_location_decision_pending')
    result.update(S1_provisional_exact_location_gate_admitted_overall_pending=1,
                  overall_qualification=q['overall_qualification'],successful_unsupported_guards=16,
                  correction_findings={'W14-01':'AUTHOR_REPAIRED_PENDING_SAME14_DELTA','W14-02':'AUTHOR_REPAIRED_PENDING_SAME14_DELTA'})
    result['handoff']='Immutable reporting repair for SAME14 exact delta; no whole-S3 qualification or execution GO.'
    write('RESULT.json',result)
    pins=read('INPUTS.json');pins['reporting_correction']={'task_commit':TASK_COMMIT,'base_intake':BASE_COMMIT,
        'review':REVIEW_COMMIT,'admission':ADMISSION_COMMIT,'settings':'high/FastOFF; no subagents',
        'scope':'Reporting/generator checks only; no source/parser/control/CI/accounting/policy changes.'}
    write('INPUTS.json',pins)
    prov=read('PROVENANCE.json');prov['reporting_correction']=pins['reporting_correction']
    prov['inherited_validation']={'commit':BASE_COMMIT,'path':rel+'/VALIDATION.json',
        'sha256':manifest['files']['VALIDATION.json']['sha256'],'scope':'Original checks inherited by exact bytes; not rerun.'}
    write('PROVENANCE.json',prov)
    write('CORRECTIONS.json',{
        'status':'READY_AUTHOR_CORRECTIONS_COMPLETE_PENDING_SAME14_DELTA',
        'task_commit':TASK_COMMIT,'base_commit':BASE_COMMIT,'review_commit':REVIEW_COMMIT,
        'admission_commit':ADMISSION_COMMIT,'overall_qualification':q['overall_qualification'],
        'findings':[
            {'id':'W14-01','author_disposition':'CLOSED_BY_AUTHOR_PENDING_SAME14_DELTA',
             'change':'Fixed descending length13 domain and exact ordinary weak_swap seam/caller copy in generator, binding and all summaries.',
             'source_binding':source_binding,'new_binding':'QUALIFICATION.json#/rows/8/bindings',
             'preserved':'One intended literal negative failure, all eight U arguments for exact fixture; full-byte positive domains unchanged.'},
            {'id':'W14-02','author_disposition':'CLOSED_BY_AUTHOR_PENDING_SAME14_DELTA',
             'change':'Four exact SUCCESS unsupported guards per completed positive/16 total, projected in qualification/inventory/report; native arrays unchanged.',
             'roots':list(POSITIVE_ROOTS),'native_records':'NATIVE.json',
             'new_inventory':'QUALIFICATION.json#/successful_unsupported_guard_inventory',
             'regressions':'Reject missing/empty/altered native inventory and every non-SUCCESS status; actual pinned strict predicate rejects nonempty arrays independently of U.'}],
        'validation':'VALIDATION.json; bounded reporting/generator checks only; broad exact prior audit inherited, not rerun.',
        'next':'Root supplies this exact committed correction to SAME14 CURRENT110 for short delta; no external message sent.',
        'unchanged':'Compact payload/digests/native counts and statuses/policy/42 U/roles/covers/PFC/context/provenance/prefix/cost; no source/control/CI/accounting actions.',
        'proof_credit':'NONE'})
    write('VALIDATION.json',{'status':'PASS','scope':'Bounded reporting replay; prior broad source/reader/U/PFC/prefix/cost audit inherited by exact bytes, not rerun.',
        'checks':checks,'checks_count':len(checks),'native_reexecuted':False,'policy_modified':False,
        'raw_logs_or_transport_zip_saved':False,'regression_controls':'Synthetic copies only; original evidence unmodified.',
        'inherited_validation':prov['inherited_validation'],'fixed_fixture_binding':source_binding,
        'successful_unsupported_guards':{'per_completed_positive':4,'total':16},'strict_expected_matches':0})
    print(json.dumps({'status':'PASS','bounded_checks':len(checks),'W14-01':'AUTHOR_REPAIRED','W14-02':'AUTHOR_REPAIRED',
                      'unsupported_SUCCESS_guards':16,'strict_expected_matches':0,'native_reexecuted':False}))

if __name__=='__main__':main()
