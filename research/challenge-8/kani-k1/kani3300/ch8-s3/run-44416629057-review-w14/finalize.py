#!/usr/bin/env python3
"""Render review decisions/manifests from independently checked compact outputs."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

HERE = Path(__file__).resolve().parent


def read(n):
    return json.loads((HERE/n).read_bytes())


def write(n, d):
    (HERE/n).write_text(json.dumps(d, indent=2, ensure_ascii=False)+'\n')


def main():
    audit, cases, validation = read('INPUT-AUDIT.json'), read('CASE-ASSESSMENT.json'), read('VALIDATION.json')
    root=HERE.parents[5]
    policy_paths=[
        'research/challenge-8/kani-k1/S1-ACCEPTANCE-DECISION-2026-11-17.md',
        'research/challenge-8/kani-k1/kani3300/ch8-s1/s1-08/composite-44095954742-44128268928/accept/replay.py',
        'research/challenge-8/kani-k1/kani3300/ch8-profiles/off-ci-batch/run-43784551069/accept-v4/BINDING.md']
    refs={}
    for path in policy_paths:
        b=subprocess.check_output(['git','-C',str(root),'show',audit['intake']+':'+path])
        refs[path]={'reference_commit':audit['intake'],'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),
                    'scope':'S1 source-reported criteria/earlier exact successful-guard precedent; no automatic S3 admission'}
    demangler=Path(shutil.which('c++filt')).resolve()
    write('REFERENCE-IDENTITIES.json', {'policy_references':refs,'demangler':{'path':str(demangler),
        'sha256':hashlib.sha256(demangler.read_bytes()).hexdigest(),
        'version':subprocess.check_output([str(demangler),'--version'],text=True).splitlines()[0],
        'scope':'Rust symbol demangling only; not a Rust compiler or verifier'}})
    case = next(x for x in cases['rows'] if x['id']=='s3_sort4_u8_same_alloc')
    findings = [
        {'id':'W14-01','severity':'MEDIUM','owner':'original11/CURRENT102','category':'REPORTING_DOMAIN',
         'locations':['../run-44416629057/QUALIFICATION.json#/rows/8/bindings/source_domain','../run-44416629057/replay.py:176'],
         'observed':'13 arbitrary independent full bytes claimed for sort13_weak',
         'evidence':'source513341f41ce53833a279571401c924bdddddb6c8:library/core/src/slice/sort/shared/smallsort/verify/sorting_s2_batch.rs:147 initializes fixed [12u8,11,10,9,8,7,6,5,4,3,2,1,0]',
         'required_correction':'Report fixed descending length13 fixture and exact ordinary weak_swap seam in new immutable correction; no arbitrary-byte negative claim.',
         'impact':'Negative role failure and all8 U arguments remain valid for fixed fixture; inaccurate domain blocks unqualified intake approval.'},
        {'id':'W14-02','severity':'MEDIUM','owner':'original11/CURRENT102','category':'REPORTING_INVENTORY',
         'locations':['../run-44416629057/QUALIFICATION.md:20','../run-44416629057/render.py:20'],
         'observed':'exported unsupported_constructs arrays described as empty',
         'evidence':[{'id':x['id'],'unsupported_constructs':x['unsupported_constructs']} for x in cases['rows'] if x.get('unsupported_constructs')],
         'required_correction':'Retain and accurately report four SUCCESS unsupported-guard records per completed positive root, sixteen total; no artifact or status changes.',
         'impact':'No extra failure established. Strict S3 expected_observation rejects nonempty arrays too. Source-reported case assessment may retain exact successful guards as in S1 composite method.'}
    ]
    write('FINDINGS.json', {'schema':'W14-independent-intake-review-v1','status':'READY','task':audit['task'],'intake':audit['intake'],
                            'disposition':'REQUEST_CHANGES','blockers_to_unqualified_intake_approval':2,'findings':findings,
                            'integrity':'PASS','six_provisional_cases':'SOUND within corrected domains at SOURCE_REPORTED assurance',
                            'sort4same':'SOUND conditional exact location-only decision; NOT_ADMITTED',
                            'location_recommendation':'RECOMMEND_ADMIT_EXACT_LOCATION_ONLY_CASE','final_admission':'ROOT_COORDINATOR_NOT_GRANTED_BY_REVIEW',
                            'strict_producer_expected_matches':'0/9_UNCHANGED','proof_credit':'NONE',
                            'followup':'New immutable author correction; preserve old intake/artifact; SAME14 exact delta. No reviewer source edits.'})
    selector = case['selector']
    prop = {'id':selector+'.unreachable.1','display_id':selector+'.unreachable.1','class':'unreachable','status':'SUCCESS',
            'description':'unreachable code','file':None,'line':None,
            'location_display':'library/core/src/lib.rs:0:0 in function '+selector}
    write('LOCATION-DECISION.json', {
        'schema':'W14-exact-location-only-case-recommendation-v1','recommendation':'RECOMMEND_ADMIT_EXACT_LOCATION_ONLY_CASE',
        'status':'NOT_APPLIED_ROOT_COORDINATOR_ADMISSION_PENDING','assurance':'S1 Profiles v4 SOURCE_REPORTED; independent proof NONE',
        'task':audit['task'],'intake':audit['intake'],'run':44416629057,'attempt':1,'harness':selector,'exact_property':prop,
        'require_present_keys':['file','line'],'originating_positive_source_coordinate':'UNKNOWN','zero_normalization':'ESTABLISHED by actual frozen streaming parser replay',
        'lowering_cause':'UNKNOWN; no original per-success CBMC SourceLocation retained',
        'protected_identity':{
            'source':audit['identities']['source'],'tool':audit['identities']['tool'],'control':audit['identities']['control'],
            'executed_head':audit['identities']['trigger'],'request_sha256':audit['request_sha256'],'workflow_sha256':audit['workflow_sha256'],
            'compact_sha256':audit['compact_sha256'],'invocation_id':case['invocation_id'],'namespace':case['namespace'],
            'members_sha256':case['members']},
        'counts':{'properties':363,'checks':356,'SUCCESS':351,'UNREACHABLE':5,'FAILURE':0,'covers':7,'SATISFIED':7,'missing_location_records':1,
                  'required_SUCCESS_literal_assertions':5,'required_located_covers':7},
        'constraints':[
            'Exact property dict plus exact harness; same original invocation/run/source/tool/control/request/workflow/namespace and authenticated member identity.',
            'Null coordinates preserved, both keys present; no registration line substitution or invented positive line.',
            'All counts and exact stock status partitions/IDs reconcile; no extra missing record, duplicate or error/unknown/undetermined.',
            'All five literal positive assertions SUCCESS and seven exact required covers SATISFIED at positive source sites; no extra/wrong-root covers.',
            'All five U remain separately source-locally justified with exact source hashes/premises/cfg/provider/domain/init/frame binding.',
            'Retain successful system record and unsupported guards; every actual role/source check/cover/failed check/U remains positively located.',
            'Protected binary snapshots, source/compile metadata, native singleton start, original exits, containment and durable seal validations remain mandatory.',
            'No global missing-location, stdlib, prefix, future-ID or future-run allowance; no policy/reader patch by reviewer.'
        ],
        'reason':'Only one SUCCESS system record has zero-sentinel location; full same-invocation inventory and all literal roles/covers/U are independently checked. Exact prior S1 exception structure is comparable; existing map does not admit this pair.',
        'risk':'Actual positive source origin/lowering explanation unresolved. Decision yields no source provenance or independent correctness credit for that system check.',
        'actual_frozen_reader':'REJECT rich metadata incomplete: file/line missing',
        'hypothetical_model':{'applied':False,'authentic_case':'ACCEPT','negative_controls':len(validation['negative_controls']),'all_mutations':'REJECT'},
        'raw_observed_S1_assessment_despite_producer_UNKNOWN':'YES as separate explicitly bounded case assessment; producer receipt/history unchanged',
        'producer_policy':'REJECT_ALL; proposalDISABLED; strict0/9 unchanged','final_admission':'Root/coordinator explicit decision required; not granted',
        'further_evidence_for_independent_origin':'Authentic producer positive-origin and lowering trace would be required for a stronger provenance claim; not invented or reacquired here.'})
    # Manifest covers all review files except its own two representations.
    records = {}
    for p in sorted(HERE.iterdir()):
        if p.is_file() and p.name not in ('MANIFEST.json','MANIFEST.sha256'):
            b=p.read_bytes();records[p.name]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
    write('MANIFEST.json', {'schema':'W14-review-manifest-v1','task':audit['task'],'intake':audit['intake'],
                           'files':records,'excluded':['MANIFEST.json','MANIFEST.sha256'],'original_intake_modified':False})
    (HERE/'MANIFEST.sha256').write_text(''.join(f"{r['sha256']}  {n}\n" for n,r in records.items()))
    print(json.dumps({'status':'READY','disposition':'REQUEST_CHANGES','findings':2,'manifest_files':len(records),
                      'location':'RECOMMEND_ADMIT_EXACT_LOCATION_ONLY_CASE; NOT_APPLIED'}))


if __name__=='__main__':
    main()
