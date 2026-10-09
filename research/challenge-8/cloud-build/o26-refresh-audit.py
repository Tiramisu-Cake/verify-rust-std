#!/usr/bin/env python3
"""Classify fresh O26 Cloud evidence; never promote pending controls to acceptance."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path

SOURCE='1798132ff7a1585db7367779365c88e5ef5f417adcff0bf82779bf6a674945e6'
ORIGINAL='466882d74de217766ed8d5c583596c173df47f0e6bd40da7cb1a4c931d7265a5'
PREFIX_CALLEES=(
 'sort4_certified_maybeuninit::sort4_checked_maybeuninit_new',
 'sort4_checked_as_mut_ptr','sort4_checked_pointer_drop',
 'sort4_checked_generic_drop','checked_transmute_neo_pointer',
 'checked_assume_init_pointer','checked_forget_owned',
)

def read(path):
    try:return json.loads(path.read_text())
    except (OSError,ValueError):return None

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def relocation(ev):
    requested=(ev/'cases/cut-relocate-request.json').exists()
    if not requested:return {'requested':False,'classification':'NOT_RUN','test_only':True}
    result=read(ev/'cases/cut-relocate/diagnostic-audit.json') or {}
    try: code=int((ev/'cases/cut-relocate-helper-exit-code.txt').read_text().strip())
    except (OSError,ValueError):code=None
    matched=code==0 and result.get('classification') not in (None,'INCONCLUSIVE') and result.get('accepted') is False
    return {'requested':True,'classification':result.get('classification','INCONCLUSIVE'),
            'diagnostic_match':matched,'helper_exit':code,'test_only':True,'accepted':False}

def owner_controls(ev):
    requested=(ev/'cases/owner17-controls-request.json').exists()
    if not requested:return {'requested':False,'complete':False,'classification':'NOT_RUN'}
    result=read(ev/'cases/owner17-controls/summary.json') or {}
    try:code=int((ev/'cases/owner17-controls-helper-exit-code.txt').read_text().strip())
    except (OSError,ValueError):code=None
    complete=(code==0 and result.get('classification')=='COMPONENT17_CONTROLS_COMPLETE' and
              result.get('diagnostic_complete') is True and
              len(result.get('negative_cases',[]))==4 and
              all(r.get('intended_component17_refusal') is True for r in result['negative_cases']))
    return {'requested':True,'complete':complete,'classification':result.get('classification','INCONCLUSIVE'),
            'helper_exit':code,'a1_isolated_negative':False}

def sort4_capture(ev):
    requested=(ev/'cases/actual-sort4-request.json').exists()
    if not requested:return {'requested':False,'complete':False,'classification':'NOT_RUN'}
    result=read(ev/'cases/actual-sort4/actual-sort4-result.json') or {}
    try:code=int((ev/'cases/actual-sort4-helper-exit-code.txt').read_text().strip())
    except (OSError,ValueError):code=None
    complete=(code==0 and result.get('classification')=='O24_EXACT_GRAPH_RESERVED_MARKER_DIAGNOSTIC' and
              result.get('support_stages_complete') is True and
              result.get('complete_graph_matches_O24') is True and
              result.get('semantic_handler_enabled') is False)
    return {'requested':True,'complete':complete,'classification':result.get('classification','INCONCLUSIVE'),
            'helper_exit':code,'actual_sort4_proved':False,'first_error':result.get('first_verifier_error')}

def main():
    p=argparse.ArgumentParser()
    for name in ('evidence','output'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--runner-exit',type=int,required=True)
    p.add_argument('--failed-stage',required=True)
    a=p.parse_args();ev=a.evidence
    pre=read(ev/'source-preflight.json') or {}
    cmp=read(ev/'cases/candidate/capture-compare.json') or {}
    cap=read(ev/'cases/candidate/capture/summary.json') or {}
    proof=read(ev/'cases/candidate/proof-stage.json') or {}
    profile=read(ev/'refresh-profile.json') or {}
    frozen=read(ev/'frozen-profile.json') or {}
    tools=read(ev/'profile-hashes.json') or {}
    stage=proof.get('stage',{})
    case=ev/'cases/candidate/capture/nine-body-a1-owned-forget'
    log=case/'refreshed-proof.log'
    text=log.read_text(errors='replace') if log.is_file() else ''
    source=cap.get('source',{})
    pair=(source.get('verified_sha256')==SOURCE and source.get('original_sha256')==ORIGINAL and
          pre.get('source_generation_complete') is True and
          pre.get('compiler_or_verifier_invoked') is False and
          cmp.get('capture_complete') is True and
          cmp.get('fresh_certificate_snapshots_match') is True and
          cmp.get('full_normal_readonly_mir_match') is True)
    proof_ran=(stage.get('status')=='RAN' and stage.get('exit') is not None and
               stage.get('exit') not in (124,137) and stage.get('source_unchanged') is True and
               stage.get('source_before')==stage.get('source_after') and
               stage.get('source_before',{}).get('verified/lib.rs')==SOURCE and
               stage.get('intrinsic_gate_active') is True and
               stage.get('pointer_drop_gate_active') is True and log.is_file())
    marks=[text.find("Verifying function '"+x+"'") for x in PREFIX_CALLEES]
    outer=text.find("Verifying function 'select_unpredictable'")
    nested=text.find("Verifying function '<select_unpredictable::DropOnPanic<T> as std::ops::Drop>::drop'")
    callees_before_outer=(all(n>=0 for n in marks) and
                          marks==sorted(marks) and outer>marks[-1])
    nested_visible=nested>=0
    profile_ok=(profile.get('classification')=='EXPERIMENTAL_O26_REFRESH_17_20' and
      frozen.get('applied_diff_sha256')=='6c4c5a7708af3bdec585abd308d37383a7de522a1aaecf2c01e1f94181324c25' and
      profile.get('kernel_modified') is False and len(profile.get('refresh_patches',[]))==2 and
      tools.get('actual',{}).get('src/rust_frontend/vf_mir_translator/vf_mir_translator.ml')==
        '595f4db4574b3f9b946c7f28024f9e8a3c2af70bbe4765368b581f6d2345c87a' and
      (ev/'refreshed-applied.patch').is_file() and
      (ev/'frozen20-applied.patch').is_file() and
      digest(ev/'frozen20-applied.patch')==frozen['applied_diff_sha256'])
    cut=relocation(ev)
    owner=owner_controls(ev)
    sort4=sort4_capture(ev)
    diagnostic_complete=(a.runner_exit==0 and pair and proof_ran and profile_ok and
                         (not owner['requested'] or owner['complete']) and
                         (not sort4['requested'] or sort4['complete']) and
                         (not cut['requested'] or cut.get('diagnostic_match') is True))
    proof_zero=proof_ran and stage.get('exit')==0
    # Source/MIR mutation negatives for component 17 and independently reached
    # component 20 A1 negatives are still pending. These cannot be inferred from
    # a positive full proof or an earlier owner-certificate rejection.
    controls={'owner_source_mir_isolated':owner['complete'],'a1_isolated':False}
    verified=(diagnostic_complete and proof_zero and callees_before_outer and nested_visible and
              all(controls.values()))
    result={'lane':os.environ.get('LANE','o26-refresh'),
      'classification':('ACTUAL_PROOF_ACCEPTED' if verified else
         'REFRESH_DIAGNOSTIC_COMPLETE' if diagnostic_complete else 'INCONCLUSIVE'),
      'diagnostic_complete':diagnostic_complete,'verification_accepted':verified,
      'accepted':verified,'actual_helper_proved':proof_zero and callees_before_outer and nested_visible,
      'source_mir_refinement_complete':pair,'profile_pins_complete':profile_ok,
      'full_proof_exit':stage.get('exit'),'prefix_callees_before_outer':callees_before_outer,
      'nested_drop_header_visible':nested_visible,
      'controls':controls,'pending_gates':profile.get('acceptance_pending',[]),
      'owner17_control_diagnostic':owner,
      'actual_sort4_capture_diagnostic':sort4,
      'cut_relocation_test_diagnostic':cut,'runner_exit':a.runner_exit,
      'failed_stage':a.failed_stage,'evidence_root':'allprooflogs'}
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:result[k] for k in ('classification','diagnostic_complete','verification_accepted')}),flush=True)
if __name__=='__main__':main()
