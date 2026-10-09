#!/usr/bin/env python3
"""Classify fresh O26 Cloud evidence; never promote pending controls to acceptance."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re

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

def a1_test(ev):
    requested=(ev/'cases/a1-isolated-test-request.json').exists()
    if not requested:return {'requested':False,'complete':False,'classification':'NOT_RUN','accepted':False}
    result=read(ev/'cases/a1-isolated-test/diagnostic-audit.json') or {}
    try:code=int((ev/'cases/a1-isolated-test-helper-exit-code.txt').read_text().strip())
    except (OSError,ValueError):code=None
    complete=(code==0 and result.get('classification')=='ISOLATED_A1_MOVE_NEGATIVE_MATCH' and
              result.get('diagnostic_complete') is True and
              result.get('verification_accepted') is False and
              result.get('production_unchanged') is True and
              result.get('test_profile_only') is True)
    return {'requested':True,'complete':complete,'classification':result.get('classification','INCONCLUSIVE'),
            'helper_exit':code,'test_only':True,'accepted':False}

def helper_exit(ev,name):
    try:return int((ev/'cases'/f'{name}-helper-exit-code.txt').read_text().strip())
    except (OSError,ValueError):return None

def coordination_regression(ev):
    name='coordination-regression'
    if not (ev/'cases'/f'{name}-request.json').exists():
        return {'requested':False,'complete':False,'classification':'NOT_RUN','test_only':True}
    result=read(ev/'cases'/name/'summary.json') or {}
    if not isinstance(result,dict):result={}
    code=helper_exit(ev,name)
    cases=result.get('cases') if isinstance(result.get('cases'),list) else []
    complete=(code==0 and result.get('classification')=='COORDINATION_REGRESSION_COMPLETE' and
              result.get('diagnostic_complete') is True and
              result.get('verification_accepted') is False and
              result.get('provider',{}).get('provider')=='cloud-build' and
              result.get('case_count')==10 and result.get('passed_count')==10 and
              isinstance(cases,list) and len(cases)==10 and
              all(isinstance(row,dict) and row.get('passed') is True for row in cases))
    return {'requested':True,'complete':complete,'classification':result.get('classification','INCONCLUSIVE'),
            'helper_exit':code,'test_only':True,'accepted':False,'case_count':len(cases)}

def nested_proof_order(ev):
    name='nested-proof-order-test'
    if not (ev/'cases'/f'{name}-request.json').exists():
        return {'requested':False,'complete':False,'classification':'NOT_RUN','test_only':True}
    result=read(ev/'cases'/name/'diagnostic-audit.json') or {}
    if not isinstance(result,dict):result={}
    code=helper_exit(ev,name)
    complete=(code==0 and result.get('classification')=='NESTED_PROOF_ORDER_TEST_DIAGNOSTIC_COMPLETE' and
              result.get('diagnostic_complete') is True and
              result.get('test_profile_only') is True and
              result.get('verification_accepted') is False and
              result.get('production_and_test_source_integrity') is True and
              result.get('nested_prefix_complete_diagnostic') is True)
    return {'requested':True,'complete':complete,'classification':result.get('classification','INCONCLUSIVE'),
            'helper_exit':code,'test_only':True,'accepted':False,
            'nested_before_outer':result.get('seven_prefix_headers_then_nested_then_outer')}

def sort4_ast_probe(ev):
    name='sort4-ast-probe'
    if not (ev/'cases'/f'{name}-request.json').exists():
        return {'requested':False,'complete':False,'classification':'NOT_RUN','test_only':True}
    result=read(ev/'cases'/name/'sort4-ast-result.json') or {}
    if not isinstance(result,dict):result={}
    code=helper_exit(ev,name)
    hash_ok=lambda key:isinstance(result.get(key),str) and re.fullmatch('[0-9a-f]{64}',result[key]) is not None
    error=result.get('probe_first_error')
    same_refusal=(isinstance(error,str) and error==result.get('probe_off_first_error')==
                  result.get('baseline_refusal') and
                  'No such function: __vf_sort4_first_unwind' in error)
    observation=result.get('scope_observation')
    complete=(code==0 and result.get('classification')=='PRINT_ONLY_AST_SCOPE_DIAGNOSTIC' and
              result.get('source_sha256')=='fddb6f1a0a90948042c99fd1037b7e939586c9e7b9e46a63367a7d876e04ccc9' and
              result.get('original_sha256')=='3602050e45025745d80b308802be9e552310959abcee4b95bfe8c24f8ca04b72' and
              isinstance(observation,str) and observation.startswith('AST_') and
              same_refusal and isinstance(result.get('snapshot_bytes'),int) and
              result['snapshot_bytes']>0 and
              hash_ok('snapshot_sha256') and hash_ok('trace_sha256') and
              result.get('probe_off_ast_output_empty') is True and
              result.get('frontend_semantics_accepted') is False and
              result.get('actual_sort4_proved') is False)
    return {'requested':True,'complete':complete,'classification':result.get('classification','INCONCLUSIVE'),
            'helper_exit':code,'test_only':True,'accepted':False,
            'scope_observation':observation,
            'scope_resolved':observation in ('AST_FIRST_CALL_INSIDE_UNIQUE_CMP_BLOCK',
                                             'AST_FIRST_CALL_OUTSIDE_CMP_BLOCK')}

def wrapper_rebase_capture(ev,canonical):
    name='wrapper-rebase-capture'
    if not (ev/'cases'/f'{name}-request.json').exists():
        return {'requested':False,'complete':False,'classification':'NOT_RUN','source_only':True}
    result=read(ev/'cases'/name/'summary.json') or {}
    if not isinstance(result,dict):result={}
    code=helper_exit(ev,name)
    case=ev/'cases'/name/'nine-body-wrapper-rebase'
    source=result.get('source',{})
    fingerprint=result.get('fingerprint') or {}
    if not isinstance(source,dict):source={}
    if not isinstance(fingerprint,dict):fingerprint={}
    current=fingerprint.get('snapshots') or {}
    prior_fingerprint=canonical.get('fingerprint') or {}
    if not isinstance(prior_fingerprint,dict):prior_fingerprint={}
    previous=prior_fingerprint.get('snapshots') or {}
    if not isinstance(current,dict):current={}
    if not isinstance(previous,dict):previous={}
    labels={'unit',*(f'body-{i}' for i in range(9))}
    old_labels={f'body-{i}' for i in range(9) if i!=7}
    current_hashes={label:row.get('sha256') for label,row in current.items()
                    if isinstance(row,dict)}
    prior_hashes={label:row.get('sha256') for label,row in previous.items()
                  if isinstance(row,dict)}
    recorded=(set(current)==labels and set(previous)==labels and
              all(isinstance(current.get(label),dict) and
                  isinstance(current[label].get('bytes'),int) and current[label]['bytes']>0 and
                  isinstance(current[label].get('sha256'),str) and
                  re.fullmatch('[0-9a-f]{64}',current[label]['sha256']) and
                  current[label].get('file')==f'actual-nested-9-{label}.marshal' and
                  (case/f'actual-nested-9-{label}.marshal').is_file() and
                  (case/f'actual-nested-9-{label}.marshal').stat().st_size==current[label]['bytes'] and
                  digest(case/f'actual-nested-9-{label}.marshal')==current[label]['sha256']
                  for label in labels))
    unchanged=(recorded and all(current_hashes[label]==prior_hashes[label]
                                for label in old_labels))
    changed=(recorded and all(current_hashes[label]!=prior_hashes[label]
                              for label in ('unit','body-7')))
    verified=case/'verified/lib.rs';original=case/'original/lib.rs'
    source_pair=(verified.is_file() and original.is_file() and
                 source.get('verified_sha256')==digest(verified) and
                 source.get('verified_sha256')!=SOURCE and
                 source.get('original_sha256')==ORIGINAL==digest(original) and
                 source.get('ghost_strip_identity') is True and
                 source.get('verified_source_reversible_two_insertions') is True and
                 source.get('actual_runtime_unchanged') is True and
                 source.get('full_mir_refinement_and_proof')=='NOT_RUN')
    complete=(code==0 and result.get('source_mode')=='wrapper-rebase-source-only' and
              result.get('frontend_refinement_and_full_body_capture') is True and
              fingerprint.get('classification')=='INTENDED_DIAGNOSTIC_REFUSAL_NO_PROOF_RULE' and
              fingerprint.get('all_ten_snapshots') is True and
              source_pair and unchanged and changed)
    return {'requested':True,'complete':complete,
            'classification':'WRAPPER_REBASE_SOURCE_CAPTURE_COMPLETE' if complete else 'INCONCLUSIVE',
            'helper_exit':code,'source_only':True,'accepted':False,
            'source_pair_exact':source_pair,'ten_snapshots_independently_hashed':recorded,
            'eight_canonical_bodies_unchanged':unchanged,'unit_and_body7_changed':changed,
            'observed_verified_sha256':source.get('verified_sha256'),
            'observed_unit_sha256':current_hashes.get('unit'),
            'observed_body7_sha256':current_hashes.get('body-7')}

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
        '0862e635075edd06a827c567710a3e1125ac03aa122e95149db755a1fddce48a' and
      (ev/'refreshed-applied.patch').is_file() and
      (ev/'frozen20-applied.patch').is_file() and
      digest(ev/'frozen20-applied.patch')==frozen['applied_diff_sha256'])
    cut=relocation(ev)
    owner=owner_controls(ev)
    sort4=sort4_capture(ev)
    a1=a1_test(ev)
    coordination=coordination_regression(ev)
    nested_order=nested_proof_order(ev)
    ast_probe=sort4_ast_probe(ev)
    wrapper_rebase=wrapper_rebase_capture(ev,cap)
    independent=os.environ.get('LANE')=='o26-independent-tests'
    independent_requested=(coordination['requested'] and nested_order['requested'] and ast_probe['requested'] and
                           wrapper_rebase['requested'] and
                           not owner['requested'] and not sort4['requested'] and
                           not a1['requested'] and not cut['requested'])
    diagnostic_complete=(a.runner_exit==0 and pair and proof_ran and profile_ok and
                         (not owner['requested'] or owner['complete']) and
                         (not sort4['requested'] or sort4['complete']) and
                         (not a1['requested'] or a1['complete']) and
                         (not cut['requested'] or cut.get('diagnostic_match') is True) and
                         (not coordination['requested'] or coordination['complete']) and
                         (not nested_order['requested'] or nested_order['complete']) and
                         (not ast_probe['requested'] or ast_probe['complete']) and
                         (not wrapper_rebase['requested'] or wrapper_rebase['complete']) and
                         (not independent or independent_requested))
    proof_zero=proof_ran and stage.get('exit')==0
    # Source/MIR mutation negatives for component 17 and independently reached
    # component 20 A1 negatives are still pending. These cannot be inferred from
    # a positive full proof or an earlier owner-certificate rejection.
    controls={'owner_source_mir_isolated':owner['complete'],'a1_isolated':False}
    test_only_requested=(coordination['requested'] or nested_order['requested'] or
                         ast_probe['requested'] or wrapper_rebase['requested'])
    verified=(diagnostic_complete and proof_zero and callees_before_outer and nested_visible and
              all(controls.values()) and not test_only_requested and not independent)
    result={'lane':os.environ.get('LANE','o26-refresh'),
      'classification':('ACTUAL_PROOF_ACCEPTED' if verified else
         'INDEPENDENT_TESTS_DIAGNOSTIC_COMPLETE' if independent and diagnostic_complete else
         'REFRESH_DIAGNOSTIC_COMPLETE' if diagnostic_complete else 'INCONCLUSIVE'),
      'diagnostic_complete':diagnostic_complete,'verification_accepted':verified,
      'accepted':verified,'actual_helper_proved':proof_zero and callees_before_outer and nested_visible,
      'source_mir_refinement_complete':pair,'profile_pins_complete':profile_ok,
      'full_proof_exit':stage.get('exit'),'prefix_callees_before_outer':callees_before_outer,
      'nested_drop_header_visible':nested_visible,
      'controls':controls,'pending_gates':profile.get('acceptance_pending',[]),
      'owner17_control_diagnostic':owner,
      'actual_sort4_capture_diagnostic':sort4,
      'a1_isolated_test_diagnostic':a1,
      'coordination_regression_diagnostic':coordination,
      'nested_proof_order_test_diagnostic':nested_order,
      'sort4_ast_probe_diagnostic':ast_probe,
      'wrapper_rebase_source_capture_diagnostic':wrapper_rebase,
      'independent_test_scope_complete':independent_requested if independent else False,
      'cut_relocation_test_diagnostic':cut,'runner_exit':a.runner_exit,
      'failed_stage':a.failed_stage,'evidence_root':'allprooflogs'}
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:result[k] for k in ('classification','diagnostic_complete','verification_accepted')}),flush=True)
if __name__=='__main__':main()
