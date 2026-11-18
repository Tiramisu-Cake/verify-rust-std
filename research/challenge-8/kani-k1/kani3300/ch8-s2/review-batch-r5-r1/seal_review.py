#!/usr/bin/env python3
"""Seal reviewer-only metadata and manifest. No candidate mutation or dispatch."""
import ast,datetime,hashlib,json,re,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=Path('/root/verify-rust-std-kani3300-g0')
PACKET=HERE.with_name('batch-r5-r1')
PACKAGE='dc8d28b0117737e95ccc9b91eb470c1a3c42a635'
PRIOR_REVIEW='022b9893c693f5908d3c9fa2ffe22961bbf8d30b'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(name):return json.loads((HERE/name).read_text())
def dump(name,value):(HERE/name).write_text(json.dumps(value,indent=2)+'\n')
def git(repo,*args):return subprocess.check_output(['git','-C',str(repo),*args],text=True).strip()

def main():
    inputs=read('INPUTS.json');p=json.loads((PACKET/'PINS.json').read_text())
    assert inputs['package']==PACKAGE and inputs['pins_sha256']==sha(PACKET/'PINS.json')
    for name in ('source','control','tool'):
        repo=Path(p[name]['worktree'])
        assert not git(repo,'status','--porcelain=v1')
        assert git(repo,'rev-parse','HEAD')==p[name]['sha']
        assert git(repo,'rev-parse','HEAD^{tree}')==p[name]['tree']
        assert git(repo,'rev-list','--parents','-n','1','HEAD').split()==[p[name]['sha'],p[name]['parent']]
    immutable=[(PACKAGE,PACKET),(p['frozen_package'],HERE.with_name('batch-r5')),
               (PRIOR_REVIEW,HERE.with_name('review-batch-r5'))]
    for rev,path in immutable:assert not git(ROOT,'diff',rev,'--',str(path.relative_to(ROOT)))
    # No input drift since initial static verification.
    for line in (PACKET/'MANIFEST.sha256').read_text().splitlines():
        expected,name=line.split(None,1);assert sha(PACKET/name.lstrip('*'))==expected
    static=read('REEXECUTED-VALIDATION.json');inv=read('INVARIANCE.json')
    assert static['state']=='STATIC_COMBINED_DELTA_PASS'
    assert len(static['patch_replays'])==6
    assert [r['depth'] for r in static['checkout_depths']]==[7,5,2]
    assert inv['package_files']==70 and inv['manifest_hashes']==69
    portable=read('PORTABLE-PROBE.json');prior=read('UPLOADED-PREFIX-REPRO.json')
    assert portable['status']=='PASS' and portable['prefix_byte_exact']
    assert portable['member_negative_count']==16 and portable['malformed_seal_count']==15
    assert prior['control_sha']==p['frozen_control'] and prior['archive_only_seal_verification']['type']=='KeyError'
    targeted=read('TARGETED-TESTS.json');log=(HERE/'TARGETED-TESTS.txt').read_text()
    assert sha(HERE/'TARGETED-TESTS.txt')==targeted['transcript_sha256']
    assert targeted['exit_code']==1 and 'Ran 34 tests in' in log and 'FAILED (failures=1)' in log
    assert len(re.findall(r'^test_.* \.\.\. ok$',log,re.M))==33
    assert len(re.findall(r'^test_.* \.\.\. FAIL$',log,re.M))==1
    assert re.search(r'^test_escaped_setsid_child_found_and_reaped .* \.\.\. FAIL$',log,re.M)
    portable_cases=['test_archive_only_prefix_exact_seal_and_collect_after_later_failure',
        'test_compact_cap_omission_is_explicit_and_never_qualified',
        'test_missing_required_structured_member_rejects_archive',
        'test_mutated_structured_member_with_updated_entry_hash_still_rejects']
    for case in portable_cases:assert re.search(r'^'+case+r' .* \.\.\. ok$',log,re.M)
    process=read('PROCESS-DIAGNOSTIC.json')
    assert process['runtime_byte_identical_to_prior']
    for case in process['instrumented_cases']:
        assert case['result']['containment']['verified'] and case['result']['containment']['reaped_adopted']
        assert case['controller_owned_group_check']['rejected']
    assert not process['instrumented_cases'][-1]['result']['orphan_survivors_at_worker_exit']
    closures=[{'id':'R14-R5-01','status':'CLOSED','blocking':False,
        'control':p['control']['sha'],'evidence':['VALIDATE-MARGIN.json','INVARIANCE.json','REEXECUTED-VALIDATION.json','TARGETED-TESTS.txt'],
        'reason':'Exact R5 cap11, legacy10; actual final134/409.026897886s, margin1.613585814; caps/invariants/rebinding verified. Prior130 remains inherited4e97.'},
        {'id':'R14-R5-02','status':'CLOSED','blocking':False,'control':p['control']['sha'],
        'evidence':['PORTABLE-PROBE.json','TARGETED-TESTS.txt','UPLOADED-PREFIX-REPRO.json','INVARIANCE.json'],
        'reason':'Old upload-only seal and collect failure reproduced; exact final real pipeline archive-only replay passes with byte-exact completed prefix after later failure/fallback. Missing/tampered/malformed/cap-omitted cases fail closed. Raw logs remain local; protected bindings and production caps unchanged.'}]
    dump('CLOSURES.json',{'verdict':'APPROVE','reviewed_package':PACKAGE,'prior_review':PRIOR_REVIEW,'closures':closures,'blockers':[]})
    observation={'id':'R14-R5-R1-O01','severity':'LOW','blocking':False,
        'title':'Unchanged fast-exit process fixture has a timing-dependent early orphan list',
        'evidence':['TARGETED-TESTS.txt','PROCESS-DIAGNOSTIC.json'],
        'initial_targeted':'34 tests:33 PASS/1 FAIL','isolated_repeat':'1 FAIL',
        'diagnostic':'All three instrumented cases verified cleanup/reaping and controller rejection of escaped PGID; delayed sampling recreates empty early orphan list.',
        'scope':'Nonblocking inherited test stability observation; no candidate change requested in this localized repair. Possible future CI flakiness remains.'}
    dump('REPORT.json',{'schema':'ch8-s2-r5-r1-independent-delta-review-v1','verdict':'APPROVE',
        'reviewed_package':PACKAGE,'task':inputs['task'],'control':p['control'],'source':p['source'],'tool':p['tool'],
        'prior_review':PRIOR_REVIEW,'closures':closures,'blockers':[],'observations':[observation],
        'inherited_fullreview':'VERIFIED_INVARIANCE; exact seven control delta paths,3874 unchanged entries, unchanged source/tool and protected bytes',
        'package_files':70,'manifest_hashes':69,'patch_replays':6,'checkout_depths':[7,5,2],
        'validation':{'reviewer_targeted':{'tests':34,'passed':33,'failed':1,'exit_code':1,'seconds':targeted['elapsed_seconds']},
            'portable_cases':{name:'PASS' for name in portable_cases},'additional_portable_member_negatives':16,
            'additional_malformed_seals':15,'cap_setup_tests':{'tests':7,'passed':7},
            'author_final':{'tests':134,'seconds':'409.026897886','classification':'ACTUAL_FINAL_OBJECT; INSPECTED_AUTHOR_EVIDENCE'},
            'author_check_source_seconds':'13.409119839','author_prior':{'tests':130,'seconds':'403.420022367','classification':'INHERITED_PRIOR_OBJECT4e97'},
            'reviewer_full_Validate_executions':0,'static':'PASS'},
        'scope':{'selected':'9/16/5','full':'11/20/6','general32':'DEFERRED_NOT_SELECTED; UNKNOWN',
            'native_R5':'NOT_RUN','future_GitHub_timing':'UNKNOWN','proof_credit':'NONE','independent_B1_B2':'NONE','proof_obligations_closed':0,
            'assumed_caller_copy_source_reported_restrictions':'PRESERVED','compiler_instance_assertion_origin':'UNKNOWN'},
        'actions':{name:0 for name in ['candidate_edit','source_edit','compiler','verifier','full_runner','CI','push','PR','issue','raw_real_archive_read','GCS','ledger','budget','reservation','subagent']},
        'Fast':'OFF_NOT_TOGGLED','settings':'PRESERVED','dispatch_authority':'NONE',
        'next':'Coordinator GO-request preparation only; dispatch/publication separate owner/coordinator decisions.'})
    refs=[]
    for file in ['PINS.json','CI-REQUEST.json','WORKFLOW.yml','MANIFEST.sha256','INVARIANCE.json','AUDIT.json','TIMEOUT-MARGIN.json',
                 'COMBINED-FINAL-VALIDATE-TIMING.json','COMBINED-TEST-PROVENANCE.json','COMBINED-FINAL-VALIDATE.txt',
                 'COMBINED-CHECK-SOURCE-TIMING.json','COMBINED-CHECK-SOURCE.txt','PRIOR-OBJECT-VALIDATE-TIMING.json',
                 'CAP-TESTS.json','CAP-TESTS.txt','PATCHES.json','validate_package.py']:
        refs.append({'package':PACKAGE,'path':str((PACKET/file).relative_to(ROOT)),'sha256':sha(PACKET/file)})
    for file in ['REPORT.md','REPORT.json','reproduce_uploaded_prefix.py','UPLOADED-PREFIX-REPRO.json']:
        path=HERE.with_name('review-batch-r5')/file
        refs.append({'package':PRIOR_REVIEW,'path':str(path.relative_to(ROOT)),'sha256':sha(path)})
    dump('EVIDENCE.json',{'schema':'review-evidence-index-v1','reviewed_input_refs':refs,
        'local_reviewer_evidence':['INPUTS.json','INVARIANCE.json','VALIDATE-MARGIN.json','REEXECUTED-VALIDATION.json',
            'TARGETED-TESTS.json','TARGETED-TESTS.txt','PORTABLE-PROBE.json','UPLOADED-PREFIX-REPRO.json','PROCESS-DIAGNOSTIC.json'],
        'scope':'local bounded synthetic/static evidence; no native outcome or proof credit'})
    for path in HERE.glob('*.py'):ast.parse(path.read_text(),filename=str(path))
    dump('FINAL-CHECKS.json',{'status':'PASS','at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'g0_head_before_review_commit':git(ROOT,'rev-parse','HEAD'),'reviewed_package':PACKAGE,
        'candidate_source_tool_clean':True,'immutable_inputs_unchanged':True,
        'closures':'BOTH_CLOSED','blockers':[],'preserved_failure':'TARGETED-TESTS.txt/PROCESS-DIAGNOSTIC.json',
        'report_consistency':'CHECKED','python_AST':'PASS','ownpaths_commit':'REQUIRED [skip ci]'})
    files=sorted(p for p in HERE.rglob('*') if p.is_file() and p.name!='MANIFEST.sha256')
    assert all(not p.is_symlink() for p in files)
    (HERE/'MANIFEST.sha256').write_text(''.join(sha(p)+'  '+str(p.relative_to(HERE))+'\n' for p in files))
    print('REVIEW_SEALED APPROVE; both CLOSED; '+str(len(files))+' hashes; initial test failure retained')

if __name__=='__main__':main()
