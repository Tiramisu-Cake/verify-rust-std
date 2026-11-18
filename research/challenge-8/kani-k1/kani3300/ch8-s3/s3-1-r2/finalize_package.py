#!/usr/bin/env python3
"""Seal local validation views/manifest after exactly one final Validate."""
import hashlib,json,subprocess
from pathlib import Path
OUT=Path(__file__).resolve().parent
CONTROL=Path('/root/kani-ch8-s3-1-r2-control-w13')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(name):return json.loads((OUT/name).read_text())
def write(name,value):(OUT/name).write_text(json.dumps(value,indent=2)+'\n')
def git(*args):return subprocess.check_output(['git','-C',str(CONTROL),*args],text=True).strip()
def main():
    pins=read('PINS.json');v=read('FINAL-VALIDATE.json');s=read('SOURCE-GATES.json');t=read('TARGETED.json');inputs=read('INPUTS.json')
    assert v['state']=='PASS' and v['execution_count']==1 and v['margin_pass'] and v['margin']>=1.5
    assert v['control_sha']==s['control_sha']==pins['control']['sha']==git('rev-parse','HEAD')
    assert v['control_tree']==s['control_tree']==pins['control']['tree']==git('rev-parse','HEAD^{tree}')
    assert v['source_sha']==s['source']['std_sha']==pins['source']['sha']
    assert v['request_sha256']==s['request_sha256']==pins['request_sha256']==sha(OUT/'CI-REQUEST.json')
    assert v['workflow_sha256']==s['workflow_sha256']==pins['workflow_sha256']==sha(OUT/'WORKFLOW.yml')
    assert t['fixture_sha256']==pins['fixture_sha256']==sha(OUT/'FIXTURE-REGRESSION.py')==sha(CONTROL/'ch8-s1-control/test_s3_paths.py')
    assert not git('status','--porcelain=v1')
    assert v['tracked_worktree_sha256']=={name:sha(CONTROL/name) for name in v['tracked_worktree_sha256']}
    for record in inputs['immutable_source_scope_maps']:assert sha(OUT/record['file'])==record['sha256']
    for record in inputs['dependencies']:assert sha(OUT/record['copy'])==record['sha256']
    for key in ('stdout','stderr'):assert sha(OUT/('FINAL-VALIDATE.'+key+'.txt'))==v[key+'_sha256']
    summaries=[json.loads(line) for line in (OUT/'FINAL-VALIDATE.stdout.txt').read_text().splitlines() if line.startswith('{')]
    suite=next(x for x in summaries if x.get('schema')=='ch8-s3-validate-v1')
    assert suite['success'] and suite['legacy_tests']==136 and suite['s3_tests']==56 and suite['failures']==suite['errors']==0
    validation={'state':'OFFLINE_FINAL_PASS_NOT_NATIVE','final_record':'FINAL-VALIDATE.json','final_record_sha256':sha(OUT/'FINAL-VALIDATE.json'),
        'test_summary':suite,'tests':192,'actual_final_elapsed_seconds':v['elapsed_seconds'],'step_cap_seconds':1080,'margin':v['margin'],
        'execution_count':1,'source_preflight':'SOURCE-GATES.json','targeted':'TARGETED.json','frozen_defect':'FROZEN-DEFECT.stderr.txt',
        'native_compile_proof_fit':'NOT_RUN','historical_status':'UNCHANGED_STOPPED_PREFIX0','qualification':0,'proof_credit':0}
    write('VALIDATION.json',validation)
    provenance={'task':pins['task'],'intake':pins['intake'],'control':pins['control'],'source':pins['source'],'tool':pins['tool'],
        'request_sha256':pins['request_sha256'],'workflow_sha256':pins['workflow_sha256'],'fixture_sha256':pins['fixture_sha256'],
        'final_validation':validation,'patches':read('PATCHES.json'),'ancestry':read('ANCESTRY.json'),
        'assurance':'Local static/synthetic service checks against frozen bytes; no native compile, proof, campaign fit, B1 or B2 acceptance.',
        'historical':{'control':pins['frozen_control'],'package':pins['frozen_package'],'review':pins['frozen_review'],'GO_spent':pins['spent_GO'],
            'trigger':'d92581141b86e0f3b695cb37acc15c265478c9b4','state':'STOPPED','completed_prefix':0,'first_row':'INTERRUPTED/UNKNOWN',
            'later_selected_roots':'8 NOT_RUN','deferred':'8 NOT_SELECTED','native_literal_observation':'S2_NEG_CHECKER_ORDER FAILURE; source-reported only',
            'driver_exit':1,'worker_exit':0,'U':8,'physical_identity':'UNKNOWN','admitted_negative':False,'qualification':0,'proof_credit':0,
            'rewritten':False,'counterfactual_admitted':False},
        'same14_delta':'PENDING','root_GO':'NEW_REQUIRED_AFTER_APPROVAL','ledger_action':'NONE; coordinator charge0 case unchanged;31/31+11/17=42/48'}
    write('PROVENANCE.json',provenance)
    write('CLOSURE.json',{'status':'READY_FOR_SAME14_DELTA','control':pins['control'],'source':pins['source'],'tool':pins['tool'],
        'request_sha256':pins['request_sha256'],'workflow_sha256':pins['workflow_sha256'],'final_validation':validation,
        'scope_preserved':[x['file'] for x in inputs['immutable_source_scope_maps']],
        'immutable_historical_inputs':[pins[k] for k in ('intake','frozen_control','frozen_package','frozen_review','spent_GO')],
        'proof_obligations_closed':0,'qualification':0,'proof_credit':0,'native_compile_proof_fit':'NOT_RUN','CI':'NOT_RUN',
        'push_PR_issues_comments_ledger_budget_reservation':'NOT_PERFORMED','same14_delta':'PENDING','new_root_GO':'REQUIRED_AFTER_APPROVE',
        'closure_reason':'Authorized offline path repair, exact real-writer regression, frozen reproduction, patch/identity closure and once-only final validation completed. Required next independent SAME14 delta and root GO belong to separate roles; no source/tool or optional feature work authorized.'})
    checkpoint={'status':'READY_FOR_SAME14_DELTA','runtime':'Codex original13; high/FastOFF; no subagents/model/settings changes',
        'task':pins['task'],'intake':pins['intake'],'control':pins['control'],'source':pins['source'],'tool':pins['tool'],
        'claims':[{'claim':'Future S3 entry canonical path fixes observed string mismatch; strict readers/legacy unchanged','assurance':'Exact four-path delta plus real-file synthetic service regression','evidence':['CONTROL-DELTA.patch','TARGETED.json','REGRESSION.md']},
                  {'claim':'Final offline checks pass on exact committed bytes','assurance':'Static/synthetic only','evidence':['FINAL-VALIDATE.json','SOURCE-GATES.json','VALIDATION.json']}],
        'validation':validation,'decisions':[{'choice':'Canonicalize only S3 tool input before E0; reuse without resolving again in invoke','reason':'Observed path serialization is only tool fingerprints; std controller records pinned hashes rather than directory path','rejected':['hash-only/basename comparisons','retrospective normalization','rebaseline after drift','legacy writer change']}],
        'blocker':None,'open':['SAME14 independent exact delta disposition','new root GO after APPROVE','native future compile/proof/fit NOT_RUN; no launch authorized'],
        'next':'SAME14 uses REVIEW14-DELTA-REQUEST.md and TASK-W14 input; new immutable s3-1-review-r2. Coordinator owns prospective12/17.',
        'historical_status':'STOPPED/prefix0/firstrowINTERRUPTED-UNKNOWN/later8NOT_RUN/deferred8NOT_SELECTED/8U; physical identityUNKNOWN',
        'accounting_reference':'31/31+11/17=42/48; coordinator charge0 case decision; no agent action','proof_credit':0,'proof_obligations_closed':0,
        'closure_reason':read('CLOSURE.json')['closure_reason']}
    write('CHECKPOINT.json',checkpoint)
    short=f"192PASS ({suite['legacy_tests']} legacy + {suite['s3_tests']} S3); final Validate ONCE {v['elapsed_seconds']:.9f}s; margin {v['margin']:.9f}x>=1.5. Source preflight STATIC_PASS."
    (OUT/'CURRENT-TASK.md').write_text('# S3-1-r2 / original13\n\nTask '+pins['task']+'; runtime Codex high/FastOFF; no subagents/model changes.\n\nREADY_FOR_SAME14_DELTA. CONTROL '+pins['control']['sha']+'; tree '+pins['control']['tree']+'; sole parent '+pins['control']['parent']+'.\n\n'+short+'\n\nSource513341/tool0aac exact. Historical STOPPED/UNKNOWN classifications unchanged; physical identity UNKNOWN, qualification/proofcredit0. Native compile/proof/fit and CI NOT_RUN.\n\nNext SAME14 independent delta then new root GO only. No push/CI/ledger/budget action. Accounting31/31+11/17=42/48 unchanged.\n')
    (OUT/'HANDOFF.md').write_text('# READY — original13 path repair to SAME14\n\nCONTROL `'+pins['control']['sha']+'`, tree `'+pins['control']['tree']+'`, sole parent `'+pins['control']['parent']+'`. This package is identified by the immutable G0 commit containing its manifest; full commit SHA is supplied in the completion response.\n\n'+short+'\n\nStart PINS.json, REPAIR.md, REGRESSION.md and REVIEW14-DELTA-REQUEST.md. INPUTS/PROVENANCE/PATCHES/ANCESTRY bind source, stock tool, request, workflow, maps, exact fixture and preserved failures. CONTROL-DELTA is four paths; shared runner/readers/policies/legacy unchanged.\n\nFrozen fc29 workflow test fails with recorded worker binary drift: before; repaired future writer passes real filesystem hashing and worker argv checks. Historical artifact remains STOPPED, qualification0, physical identityUNKNOWN; no transformed copy admitted.\n\nRequired next: SAME14 independent path delta under copied TASK-W14.md, immutable s3-1-review-r2; exact APPROVE permits root to consider a new GO. User coordinator separately launches/counts prospective12/17. Old GO spent. Source513/tool0aac, all9 roots, maps/domains/full-byte premises, unwinds,44 covers/71 literals/deferred8/rejectALLU and resource caps unchanged.\n\nNo native compiler/Kani/CBMC, CI, push, PR/issues/comments, ledger/budget action or subagents. Future compile/proof/fit NOT_RUN; proofcredit0.\n')
    files=sorted(p for p in OUT.rglob('*') if p.is_file() and p!=OUT/'MANIFEST.sha256')
    (OUT/'MANIFEST.sha256').write_text(''.join(sha(p)+'  '+p.relative_to(OUT).as_posix()+'\n' for p in files))
    for line in (OUT/'MANIFEST.sha256').read_text().splitlines():
        digest,name=line.split('  ',1);assert sha(OUT/name)==digest
    print(json.dumps({'status':'READY_FOR_SAME14_DELTA','tests':192,'elapsed_seconds':v['elapsed_seconds'],'margin':v['margin'],'manifest_files':len(files),'manifest_sha256':sha(OUT/'MANIFEST.sha256')}))
if __name__=='__main__':main()
