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
    if os.environ.get('LANE') in ('o26-recovery-tests','o26-strict-cut-controls',
                                  'o26-strict-cut-false-posts',
                                  'o26-strict-cut-reuse-false-posts',
                                  'o26-sort4-scope-tests'):
        checks=result.get('checks') or {}
        required={'translated_ids_patch_pin','support','exact_source_pair',
                  'complete_target_mir_pins','direct_unwind_continue',
                  'baseline_boundary','ast_six_removed_one_inserted',
                  'relocated_proof_entry','diagnostic_outcome'}
        matched=(matched and result.get('classification') in
                 ('FIXTURE_FULL_VF0_DIAGNOSTIC_ONLY',
                  'NEXT_PROOF_BLOCKER_DIAGNOSTIC_ONLY') and
                 set(checks)==required and all(value is True for value in checks.values()) and
                 result.get('raw_capture_exit')==0 and
                 result.get('unwind_storage_dead_assumed') is False)
    if os.environ.get('LANE') in ('o26-strict-cut-controls',
                                  'o26-strict-cut-false-posts',
                                  'o26-strict-cut-reuse-false-posts',
                                  'o26-sort4-scope-tests'):
        matched=matched and result.get('classification')=='FIXTURE_FULL_VF0_DIAGNOSTIC_ONLY'
    return {'requested':True,'classification':result.get('classification','INCONCLUSIVE'),
            'diagnostic_match':matched,'helper_exit':code,'test_only':True,'accepted':False}

def strict_cut_error_attribution(key,row):
    if row.get('first_error') is None:
        return key[1] and key[0] in {'positive_basic','ordinary_unmarked',
                                      'positive_early_return','positive_direct_unwind'}
    if key == ('negative_end_lifetime_twice',True):
        location=row.get('first_error_location')
        return (row.get('first_error_source_location') is None and
                isinstance(location,str) and
                location.endswith('/bin/rust/rust_belt/lifetime_logic.rsspec(78,9-23)') and
                row.get('first_error')==location+
                ': error: No matching heap chunks: lifetime_token(cmp_k)' and
                row.get('first_error_caller_note_location')==
                'verified/lib.rs(15,13-25)')
    return bool(row.get('first_error_source_location'))

def strict_cut_reuse_provenance(ev):
    root=ev/'cases/strict-cut-controls'
    report=read(root/'reuse-provenance.json') or {}
    old=read(root/'historical-diagnostic-audit.json') or {}
    receipt=read(root/'historical-upload-complete.json') or {}
    current=root/'diagnostic-audit.json'
    prior=root/'historical-diagnostic-audit.json'
    complete=(prior.is_file() and
              report.get('classification')=='HISTORICAL_STRICT_CUT_MATRIX_REAUDITED' and
              report.get('accepted') is False and
              report.get('historical_build_id')==
              '673526ac-6556-40bc-9ebe-7792e257bfcd' and
              report.get('historical_case_count')==17 and
              report.get('historical_cases_executed_in_this_build')==0 and
              report.get('new_false_post_cases_executed_here')==0 and
              report.get('archive_sha256')==
              '11ebebd82f74b42b4fd1a66cfa9959dc58bc4793629569545d35a2447c20e861' and
              report.get('infra_sha')=='9f22416ac13ac006f505605b57b50f37629caef1' and
              report.get('proof_sha')=='d253128ac42f5788cc322201bdfcc6c1e2e36f76' and
              report.get('config_sha256')==
              '0d3bdf60f461b0fb6eff7c55664ccd7ab094ac179f59be611c66294989e28e25' and
              report.get('verified_inventory') is True and
              report.get('fresh_tool_identity_equal') is True and
              report.get('historical_audit_sha256')==digest(prior))
    complete=(complete and current.is_file() and
              report.get('current_audit_sha256')==digest(current) and
              old.get('classification')=='INCONCLUSIVE' and
              old.get('accepted') is False and
              old.get('reason')==
              'negative_end_lifetime_twice: first error has no source location' and
              receipt.get('uploaded') is True and
              receipt.get('build_id')=='673526ac-6556-40bc-9ebe-7792e257bfcd' and
              receipt.get('archive_sha256')==report.get('archive_sha256'))
    return {'requested':True,'complete':complete,'accepted':False,
            'historical_matrix_cases':17 if complete else 0,
            'historical_cases_executed_in_this_build':0 if complete else None,
            'new_false_posts_expected_in_this_build':2}

def strict_cut_controls(ev):
    name='strict-cut-controls'
    if not (ev/'cases'/f'{name}-request.json').exists():
        return {'requested':False,'complete':False,'classification':'NOT_RUN',
                'test_only':True,'accepted':False}
    result=read(ev/'cases'/name/'diagnostic-audit.json') or {}
    if not isinstance(result,dict):result={}
    code=helper_exit(ev,name)
    rows=result.get('cases') or []
    if not isinstance(rows,list):rows=[]
    positives={'positive_basic','ordinary_unmarked','positive_early_return',
               'positive_direct_unwind'}
    negatives={'negative_wrong_marker','negative_duplicate_marker',
               'negative_marker_outside_binding','negative_unknown_binding',
               'negative_nested_marker','negative_malformed_marker',
               'negative_type_name_after_cut','negative_type_argument_after_cut',
               'negative_typed_chunk_survives_cut','negative_unclosed_fractional_access',
               'negative_reserved_half_after_lifetime_end','negative_end_lifetime_twice'}
    keyed={(row.get('case'),row.get('strict_lifetime_opt_in')):row
           for row in rows if isinstance(row,dict)}
    expected={(case,True) for case in positives|negatives}|{('positive_basic',False)}
    pre=result.get('preflight') or {}
    if not isinstance(pre,dict):pre={}
    open_gates=result.get('open_gates') or []
    reuse=os.environ.get('LANE')=='o26-strict-cut-reuse-false-posts'
    provenance=strict_cut_reuse_provenance(ev) if reuse else None
    complete=(code==0 and result.get('classification')==
              'CONTROLS_DISCOVERY_REVIEW_REQUIRED' and
              result.get('accepted') is False and
              result.get('strictcut_accepted') is False and
              result.get('actual_sort4_accepted') is False and
              result.get('source_and_mir_pin_status')==
              'recorded for fresh manual review, not pre-approved' and
              pre.get('production_unchanged') is True and
              pre.get('isolated_tool_unchanged') is True and
              pre.get('patch_chain_pinned') is True and
              pre.get('distinct_f_bound_full_vf0') is True and
              pre.get('prior_relocation_classification')==
              'FIXTURE_FULL_VF0_DIAGNOSTIC_ONLY' and
              len(rows)==17 and set(keyed)==expected and
              all(row.get('accepted') is False and
                  isinstance(row.get('source_hashes'),dict) and
                  set(row['source_hashes'])=={'verified/lib.rs','original/lib.rs'} and
                  isinstance(row.get('mir'),dict) and
                  set(row['mir'])=={'normal','readonly'} and
                  all(isinstance(row['mir'][mode],dict) and
                      isinstance(row['mir'][mode].get('full_text_sha256'),str) and
                      re.fullmatch('[0-9a-f]{64}',row['mir'][mode]['full_text_sha256']) and
                      isinstance(row['mir'][mode].get('bin_sha256'),str) and
                      re.fullmatch('[0-9a-f]{64}',row['mir'][mode]['bin_sha256'])
                      for mode in ('normal','readonly')) and
                  isinstance(row.get('stage_exits'),dict) and
                  all(row['stage_exits'].get(stage)==0 for stage in
                      ('normal-export','normal-decode','readonly-export',
                       'readonly-decode','refinement')) and
                  (row['stage_exits'].get('full-verification')==0
                   if key[1] and key[0] in positives else
                   row['stage_exits'].get('full-verification') in (1,2)) and
                  row.get('classification')==(
                      'POSITIVE_CANDIDATE_REVIEW_REQUIRED' if key[1] and key[0] in positives else
                      'INTENDED_NEGATIVE_CANDIDATE_REVIEW_REQUIRED' if key[1] else
                      'OPT_IN_ABSENT_INTENDED_REJECTION_CANDIDATE') and
                  strict_cut_error_attribution(key,row)
                  for key,row in keyed.items()) and
              isinstance(open_gates,list) and len(open_gates)>=8 and
              all(isinstance(gate,str) and gate for gate in open_gates) and
              (not reuse or provenance['complete']))
    return {'requested':True,'complete':complete,
            'classification':result.get('classification','INCONCLUSIVE'),
            'helper_exit':code,'test_only':True,'accepted':False,
            'matrix_cases':len(rows),'distinct_f_bound_full_vf0':
            pre.get('distinct_f_bound_full_vf0') is True,
            'normal_unwind_negative_gates_open':
            any('false normal-post and false unwind-post' in gate for gate in open_gates),
            'historical_reuse':provenance,
            'actual_sort4_accepted':False}

def strict_cut_false_posts(ev):
    name='strict-cut-false-posts'
    if not (ev/'cases'/f'{name}-request.json').exists():
        return {'requested':False,'complete':False,'classification':'NOT_RUN',
                'test_only':True,'accepted':False}
    result=read(ev/'cases'/name/'diagnostic-audit.json') or {}
    if not isinstance(result,dict):result={}
    code=helper_exit(ev,name)
    rows=result.get('cases') or []
    if not isinstance(rows,list):rows=[]
    keyed={row.get('case'):row for row in rows if isinstance(row,dict)}
    expected={'normal-false':'positive_basic',
              'unwind-false':'positive_direct_unwind'}
    complete=(code==0 and result.get('classification')==
              'FALSE_POST_CONTROLS_DISCOVERY_REVIEW_REQUIRED' and
              result.get('accepted') is False and
              result.get('strictcut_accepted') is False and
              result.get('actual_sort4_accepted') is False and
              len(rows)==2 and set(keyed)==set(expected) and
              all(row.get('parent_case')==parent and
                  row.get('classification')==
                  'FALSE_POST_FIRST_BOUNDARY_CANDIDATE_REVIEW_REQUIRED' and
                  row.get('accepted') is False and
                  isinstance(row.get('first_error'),str) and
                  row['first_error'].endswith(
                      'Cannot prove condition. (Cannot prove false.)') and
                  row.get('first_error_source_line') in
                  (row.get('target_post_line'),row.get('target_end_line')) and
                  isinstance(row.get('source_hashes'),dict) and
                  set(row['source_hashes'])=={'verified/lib.rs','original/lib.rs'} and
                  isinstance(row.get('stage_exits'),dict) and
                  all(row['stage_exits'].get(stage)==0 for stage in
                      ('normal-export','normal-decode','readonly-export',
                       'readonly-decode','refinement')) and
                  row['stage_exits'].get('full-verification') in (1,2) and
                  isinstance(row.get('mir'),dict) and
                  set(row['mir'])=={'normal','readonly'} and
                  all(isinstance(row['mir'][mode],dict) and
                      row['mir'][mode].get(
                          'complete_graph_equal_after_source_coordinate_and_contract_raw_redaction') is True and
                      row['mir'][mode].get('reviewed_contract_raw_change_only') is True and
                      isinstance(row['mir'][mode].get('normalized_full_mir_sha256'),str) and
                      re.fullmatch('[0-9a-f]{64}',row['mir'][mode]['normalized_full_mir_sha256']) and
                      row['mir'][mode].get('baseline_normalized_full_mir_sha256')==
                      row['mir'][mode]['normalized_full_mir_sha256']
                      for mode in ('normal','readonly')) and
                  (row.get('callee_before_target') is True
                   if key=='unwind-false' else True)
                  for key,parent in expected.items() for row in (keyed[key],)) and
              isinstance(result.get('open_gates'),list) and
              len(result['open_gates'])>=5)
    return {'requested':True,'complete':complete,
            'classification':result.get('classification','INCONCLUSIVE'),
            'helper_exit':code,'test_only':True,'accepted':False,
            'normal_first_false_post':
            keyed.get('normal-false',{}).get('first_error'),
            'unwind_first_false_post':
            keyed.get('unwind-false',{}).get('first_error'),
            'source_mir_gates_complete':complete}

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

def generic_new_capture(ev):
    name='generic-new-capture'
    if not (ev/'cases'/f'{name}-request.json').exists():
        return {'requested':False,'complete':False,'classification':'NOT_RUN',
                'accepted':False,'actual_callee_proved':False}
    root=ev/'cases'/name
    cert=read(root/'source-certificate.json') or {}
    result=read(root/'capture-result.json') or {}
    code=helper_exit(ev,name)
    expected_std={
      'library/core/src/hint.rs':'ce89716d46b8060db2c2da1aef1d4bcccf90e0804fc021d4470c55203501315f',
      'library/core/src/mem/manually_drop.rs':'f9cce798828cc852c00feeea9a6218c225b68d92727a5edbddc7c08a731a4f25',
      'library/core/src/mem/maybe_uninit.rs':'1230d267542337ee2842c29d8227cf8a58fe75c53a2a70efaee3922c4e8e25c0'}
    def exact_file(path,expected):
        return (isinstance(expected,str) and re.fullmatch('[0-9a-f]{64}',expected) is not None
                and path.is_file() and digest(path)==expected)
    source_sha=cert.get('generated_source_sha256')
    source_ok=(cert.get('classification')=='GENERIC_NEW_SOURCE_EQUIVALENCE_CAPTURE_ONLY' and
      cert.get('accepted') is False and cert.get('actual_callee_proved') is False and
      cert.get('pinned_complete_source_sha256')==expected_std and
      cert.get('source_pin_manifest_sha256')==
        '58aae37c02eec204b3837cee653485632549b6ab221245618fa32e702ce05811' and
      cert.get('union_signature')=='pub union MaybeUninit<T>' and
      cert.get('union_fields_sha256')==
        '330e4fa2bb6a58c95cdcc8155c0e3ff306f4b1e4da1d94df37a4d09d7bf6f54d' and
      cert.get('constructor_signature')=='pub const fn new(val: T) -> MaybeUninit<T>' and
      cert.get('constructor_body_sha256')==
        '26a6c87090e954dea0b4a43f081516f00d2e4ba5103ac6ea1b846c4fe3f2e261' and
      cert.get('actual_select_external_new_calls')==2 and
      cert.get('local_copy_defid_differs_from_core') is True and
      cert.get('local_constructor_runtime_body_exact_from_std') is True and
      cert.get('local_union_fields_exact_from_std') is True and
      cert.get('external_wrapper_call_unchanged') is True and
      cert.get('ghost_strip_identity') is True and
      cert.get('normal_unwind_contract_or_summary')=='NOT_PROVIDED' and
      cert.get('generic_ownership_model')=='OPAQUE_UNCHANGED' and
      cert.get('added_local_crate_attributes')==['#![feature(transparent_unions)]'] and
      exact_file(root/'verified/lib.rs',source_sha) and
      exact_file(root/'original/lib.rs',source_sha) and
      exact_file(root/'source-certificate.json',result.get('source_certificate_sha256')) and
      result.get('source_sha256')==source_sha)
    stages=result.get('stages') or {}
    stage_ok=(all(isinstance(stages.get(s),dict) and stages[s].get('exit')==0 and
                  stages[s].get('source_exact') is True for s in
                  ('normal-export','normal-decode','readonly-export',
                   'readonly-decode','refinement')) and
              result.get('complete_capture') is True and
              result.get('classification')=='SOURCE_MIR_CAPTURE_CANDIDATE_REVIEW_REQUIRED')
    mir=result.get('mir') or {}
    artifacts=result.get('raw_artifact_sha256') or {}
    body_counts={'new':1,'local_new_call':1,'external_new_call':1}
    modes_ok=True
    observed_details=True
    retained_local_mir=True
    for mode in ('normal','readonly'):
        row=mir.get(mode) or {}
        bin_path=root/f'{mode}-mir.bin'
        text_path=root/f'{mode}-mir.txt'
        modes_ok=(modes_ok and row.get('observation')=='OBSERVED' and
                  row.get('selected_body_counts')==body_counts and
                  all(row.get('selected_body_observation',{}).get(n)=='OBSERVED_UNIQUE'
                      for n in body_counts) and
                  isinstance(row.get('all_bodies'),list) and
                  len(row['all_bodies'])==len(row.get('all_def_paths',[])) and
                  exact_file(bin_path,artifacts.get(bin_path.name)) and
                  exact_file(text_path,artifacts.get(text_path.name)) and
                  artifacts.get(text_path.name)==row.get('full_decoded_sha256') and
                  text_path.stat().st_size==row.get('full_decoded_bytes')
                  if bin_path.is_file() and text_path.is_file() else False)
        targets=row.get('external_wrapper_nested_target_def_paths') or []
        call_lines=row.get('external_wrapper_call_substitution_lines') or []
        union_lines=row.get('union_declaration_lines') or []
        field_move=row.get('local_constructor_field_and_move_lines') or []
        normal_unwind=row.get('local_constructor_normal_unwind_lines') or []
        observed_details=(observed_details and isinstance(targets,list) and
          any('MaybeUninit' in path and path.endswith('new') and
              'source_copy' not in path for path in targets if isinstance(path,str)) and
          isinstance(call_lines,list) and
          any('genericArgs' in line or 'substs' in line for line in call_lines) and
          isinstance(union_lines,list) and
          any('union' in line.lower() for line in union_lines) and
          any('MaybeUninit' in line for line in union_lines))
        retained_local_mir=(retained_local_mir and isinstance(field_move,list) and
          any('field' in line.lower() for line in field_move if isinstance(line,str)) and
          any('move' in line.lower() for line in field_move if isinstance(line,str)) and
          isinstance(normal_unwind,list) and
          any(any(token in line for token in ('target =','goto =','return ='))
              for line in normal_unwind if isinstance(line,str)) and
          any('unwindAction' in line for line in normal_unwind if isinstance(line,str)))
    complete=(code==0 and source_ok and stage_ok and modes_ok and
              observed_details and retained_local_mir and
              result.get('local_constructor_retained_mir_observed') is True and
              result.get('accepted') is False and
              result.get('actual_callee_proved') is False and
              result.get('actual_callee_linkage')=='OPEN' and
              result.get('verifast_body_proof')=='NOT_RUN_SOURCE_MIR_DIAGNOSTIC_ONLY' and
              result.get('verifast_dead_code_check')=='UNOBSERVED_NOT_RUN_NOT_DISABLED')
    return {'requested':True,'complete':complete,
      'classification':'GENERIC_NEW_SOURCE_MIR_CAPTURE_COMPLETE' if complete else 'INCONCLUSIVE',
      'helper_exit':code,'source_certificate_complete':source_ok,
      'full_normal_readonly_mir_refinement_complete':stage_ok and modes_ok,
      'external_call_union_inventory_observed':observed_details,
      'local_constructor_field_move_normal_unwind_observed':retained_local_mir,
      'accepted':False,'actual_callee_proved':False,
      'generic_helper_closure_credited':False,
      'verifast_dead_code_check':'UNOBSERVED_NOT_RUN_NOT_DISABLED'}

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
    if os.environ.get('LANE')=='o26-recovery-tests':
        detail=result.get('r2_detail_observation') or {}
        required={'root_local_declarations','cmp_typeid_declaration',
                  'cmp_block_free_metadata','first_fnmut_operands',
                  'normal_debt_close','normal_recovery_call',
                  'local_assignment_descriptors'}
        complete=(complete and set(detail)==required and
                  all(value in ('OBSERVED','UNOBSERVED') for value in detail.values()) and
                  isinstance(result.get('first_call_returning_arm_zero'),bool) and
                  isinstance(result.get('first_call_unwinding_arm_one'),bool))
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

def wrapper_input_relation_capture(ev,canonical):
    name='wrapper-input-relation-capture'
    if not (ev/'cases'/f'{name}-request.json').exists():
        return {'requested':False,'complete':False,'classification':'NOT_RUN',
                'source_only':True,'accepted':False}
    result=read(ev/'cases'/name/'summary.json') or {}
    if not isinstance(result,dict):result={}
    code=helper_exit(ev,name)
    case=ev/'cases'/name/'nine-body-wrapper-input-relation'
    source=result.get('source') or {}
    fingerprint=result.get('fingerprint') or {}
    if not isinstance(source,dict):source={}
    if not isinstance(fingerprint,dict):fingerprint={}
    canonical_source=canonical.get('source') or {}
    if not isinstance(canonical_source,dict):canonical_source={}
    current=fingerprint.get('snapshots') or {}
    prior=canonical.get('fingerprint') or {}
    if not isinstance(prior,dict):prior={}
    previous=prior.get('snapshots') or {}
    if not isinstance(current,dict):current={}
    if not isinstance(previous,dict):previous={}
    current_hashes={label:row.get('sha256') for label,row in current.items()
                    if isinstance(row,dict)}
    labels={'unit',*(f'body-{i}' for i in range(9))}
    recorded=(set(current)==labels and set(previous)==labels and
              all(isinstance(current.get(label),dict) and
                  isinstance(previous.get(label),dict) and
                  isinstance(previous[label].get('sha256'),str) and
                  isinstance(current[label].get('bytes'),int) and
                  current[label]['bytes']>0 and
                  isinstance(current[label].get('sha256'),str) and
                  re.fullmatch('[0-9a-f]{64}',current[label]['sha256']) and
                  current[label].get('file')==f'actual-nested-9-{label}.marshal' and
                  (case/current[label]['file']).is_file() and
                  (case/current[label]['file']).stat().st_size==current[label]['bytes'] and
                  digest(case/current[label]['file'])==current[label]['sha256']
                  for label in labels))
    unchanged=(recorded and all(current[label]['sha256']==previous[label]['sha256']
                                for label in labels-{'unit','body-7'}))
    changed=(recorded and all(current[label]['sha256']!=previous[label]['sha256']
                              for label in ('unit','body-7')))
    body_records=result.get('full_body_capture') or {}
    bodies=(isinstance(body_records,dict) and set(body_records)=={'normal','readonly'} and
            all(isinstance(body_records[mode],dict) and
                body_records[mode].get('exact_body_count_and_order') is True and
                body_records[mode].get('whole_decoded_mir_file')==f'{mode}-mir.txt' and
                (case/f'{mode}-mir.txt').is_file() and
                digest(case/f'{mode}-mir.txt')==body_records[mode].get('whole_decoded_mir_sha256') and
                isinstance(body_records[mode].get('bodies'),list) and
                len(body_records[mode]['bodies'])==9 and
                all(isinstance(row,dict) and row.get('index')==index and
                    row.get('file')==f'{mode}-body-{index}-full-mir.txt' and
                    isinstance(row.get('bytes'),int) and row['bytes']>0 and
                    (case/row['file']).is_file() and
                    (case/row['file']).stat().st_size==row['bytes'] and
                    digest(case/row['file'])==row.get('sha256')
                    for index,row in enumerate(body_records[mode]['bodies']))
                for mode in ('normal','readonly')))
    verified=case/'verified/lib.rs'; original=case/'original/lib.rs'
    parent=ev/'cases'/name/'r2-source'/'nine-body-wrapper-rebase'/'verified/lib.rs'
    comments=source.get('inserted_ghost_comments') or []
    regions=source.get('inserted_ghost_regions') or []
    region_names=('before_rust_shadow','after_opened_payloads',
                  'after_rebased_wrapper_closes')
    comment_names=('save_true_input','save_false_input',
                   'true_payload_matches_input','false_payload_matches_input',
                   'current_true_wrapper_matches_input',
                   'current_false_wrapper_matches_input',
                   'shadow_true_wrapper_matches_input',
                   'shadow_false_wrapper_matches_input',
                   'conditional_wrapper_matches_input')
    data=verified.read_bytes() if verified.is_file() else b''
    def span_ok(row, text_required):
        if not isinstance(row,dict):return False
        start=row.get('byte_start'); end=row.get('byte_end_exclusive')
        if not isinstance(start,int) or not isinstance(end,int) or not 0<=start<end<=len(data):
            return False
        fragment=data[start:end]
        line_start=data.rfind(b'\n',0,start)+1
        line_end=data.rfind(b'\n',0,end)+1
        return (row.get('bytes')==len(fragment) and
                row.get('sha256')==hashlib.sha256(fragment).hexdigest() and
                row.get('line_start_one_based')==data.count(b'\n',0,start)+1 and
                row.get('column_start_zero_based')==start-line_start and
                row.get('line_end_one_based')==data.count(b'\n',0,end)+1 and
                row.get('column_end_zero_based')==end-line_end and
                (not text_required or row.get('utf8')==fragment.decode('utf-8',errors='replace')))
    metadata=(len(comments)==9 and len(regions)==3 and
              all(isinstance(row,dict) and row.get('index')==index and
                  row.get('name')==comment_names[index] and
                  row.get('region')==region_names[0 if index<2 else 1 if index<4 else 2] and
                  span_ok(row,True) for index,row in enumerate(comments)) and
              all(isinstance(row,dict) and row.get('index')==index and
                  row.get('name')==region_names[index] and
                  span_ok(row,False) for index,row in enumerate(regions)) and
              all(regions[index]['byte_start']==comments[first]['byte_start'] and
                  regions[index]['byte_end_exclusive']==comments[last]['byte_end_exclusive'] and
                  all(comments[j]['byte_end_exclusive']==comments[j+1]['byte_start']
                      for j in range(first,last))
                  for index,(first,last) in enumerate(((0,1),(2,3),(4,8)))) and
              all(comments[j]['byte_start']<comments[j+1]['byte_start'] for j in range(8)))
    parent_exact=(source.get('parent_case')=='r2-source/nine-body-wrapper-rebase' and
                  parent.is_file() and digest(parent)==source.get('parent_verified_sha256') and
                  metadata and verified.is_file() and
                  all(region['byte_start']<region['byte_end_exclusive'] for region in regions) and
                  all(regions[j]['byte_end_exclusive']<=regions[j+1]['byte_start']
                      for j in range(2)) and
                  b''.join(data[regions[j-1]['byte_end_exclusive'] if j else 0:
                                region['byte_start']] for j,region in enumerate(regions))+
                  data[regions[-1]['byte_end_exclusive']:] == parent.read_bytes())
    source_pair=(source.get('classification')==
                   'SOURCE_ONLY_WRAPPER_INPUT_RELATION_DIAGNOSTIC_NOT_ACCEPTED' and
                 source.get('case_name')=='nine-body-wrapper-input-relation' and
                 source.get('parent_verified_sha256')==
                   '11067f06ba7c745cfb221a559fb29778eba8d7b6e65f6db1a814ff7ce72bdfd4' and
                 source.get('verified_sha256')!=source.get('parent_verified_sha256') and
                 source.get('verified_sha256')!=SOURCE and
                 verified.is_file() and original.is_file() and
                 source.get('verified_sha256')==digest(verified) and
                 source.get('original_sha256')==ORIGINAL==digest(original) and
                 source.get('ghost_strip_identity') is True and
                 source.get('verified_source_reversible_three_input_relation_insertions') is True and
                 source.get('actual_runtime_unchanged') is True and
                 source.get('old_certificate_expected_to_refuse') is True and
                 source.get('verification_accepted') is False and
                 source.get('full_mir_refinement_and_proof')=='NOT_RUN' and
                 source.get('source_order')==canonical_source.get('source_order') and
                 parent_exact)
    guard=result.get('guard_capture') or {}
    if not isinstance(guard,dict):guard={}
    stages=guard.get('stages') or {}
    if not isinstance(stages,dict):stages={}
    paired=(result.get('frontend_refinement_and_full_body_capture') is True and
            guard.get('frontend_refinement') is True and
            all(isinstance(stages.get(label),dict) and stages[label].get('exit')==0 and
                stages[label].get('source_unchanged') is True for label in
                ('normal-export','normal-decode','readonly-export','readonly-decode','refinement')))
    refusal=(fingerprint.get('classification')=='INTENDED_DIAGNOSTIC_REFUSAL_NO_PROOF_RULE' and
             fingerprint.get('all_ten_snapshots') is True and
             fingerprint.get('expected_refusal_seen') is True and
             fingerprint.get('body_proof_run') is False and
             result.get('semantic_rule_enabled') is False and
             (fingerprint.get('stage') or {}).get('exit')==2)
    complete=(code==0 and result.get('source_mode')=='wrapper-input-relation-source-only' and
              source_pair and metadata and paired and bodies and recorded and unchanged and
              changed and refusal)
    return {'requested':True,'complete':complete,
            'classification':'WRAPPER_INPUT_RELATION_SOURCE_CAPTURE_COMPLETE' if complete else 'INCONCLUSIVE',
            'helper_exit':code,'source_only':True,'accepted':False,
            'source_pair_exact':source_pair,'paired_mir_refinement_complete':paired,
            'nine_ghost_comments_three_regions_exact':metadata,
            'full_nine_bodies_hashed':bodies,'ten_snapshots_independently_hashed':recorded,
            'eight_canonical_bodies_unchanged':unchanged,'unit_and_body7_changed':changed,
            'fingerprint_no_proof_rule_refusal':refusal,
            'historical_owner17_refusal_observed':False,
            'historical_owner17_refusal_expected':source.get('old_certificate_expected_to_refuse') is True,
            'exact_reversible_parent_source':parent_exact,
            'observed_verified_sha256':source.get('verified_sha256'),
            'observed_unit_sha256':current_hashes.get('unit'),
            'observed_body7_sha256':current_hashes.get('body-7')}

def wrapper_input_relation_frame_capture(ev,canonical):
    name='wrapper-input-relation-frame-capture'
    if not (ev/'cases'/f'{name}-request.json').exists():
        return {'requested':False,'complete':False,'classification':'NOT_RUN',
                'source_only':True,'accepted':False}
    root=ev/'cases'/name
    result=read(root/'summary.json') or {}
    if not isinstance(result,dict):result={}
    code=helper_exit(ev,name)
    case=root/'nine-body-wrapper-input-relation-frame'
    source=result.get('source') or {}
    if not isinstance(source,dict):source={}
    canonical_source=canonical.get('source') or {}
    if not isinstance(canonical_source,dict):canonical_source={}
    fingerprint=result.get('fingerprint') or {}
    if not isinstance(fingerprint,dict):fingerprint={}
    snapshots=fingerprint.get('snapshots') or {}
    canonical_fingerprint=canonical.get('fingerprint') or {}
    if not isinstance(canonical_fingerprint,dict):canonical_fingerprint={}
    prior=canonical_fingerprint.get('snapshots') or {}
    if not isinstance(snapshots,dict):snapshots={}
    if not isinstance(prior,dict):prior={}
    labels={'unit',*(f'body-{i}' for i in range(9))}
    verified=case/'verified/lib.rs'; original=case/'original/lib.rs'
    parent=root/'r2-source/nine-body-wrapper-input-relation/verified/lib.rs'
    parent_original=root/'r2-source/nine-body-wrapper-input-relation/original/lib.rs'
    parent_summary=read(root/'r2-source/source-summary.json') or {}
    if not isinstance(parent_summary,dict):parent_summary={}
    data=verified.read_bytes() if verified.is_file() else b''
    parent_data=parent.read_bytes() if parent.is_file() else b''
    old_contract=(b'/*@\nreq thread_token(?tid) &*& tid == currentThread &*& <T>.own(tid, t);\n@*/\n'
                  b'/*@\nens thread_token(tid) &*& <T>.own(tid, t);\n@*/\n'
                  b'/*@\non_unwind_ens false;\n@*/\n')
    new_contract=(b'/*@\nreq thread_token(?tid) &*& tid == currentThread;\n@*/\n'
                  b'/*@\nens thread_token(tid);\n@*/\n'
                  b'/*@\non_unwind_ens false;\n@*/\n')
    helper_signature=b'pub unsafe fn checked_forget_owned<T>(t: T)\n'
    helper_body=b'{\n    let _ = ManuallyDrop::new(t);\n}'
    blocks=(
      ('outer_guard_owner_branch_fold',
       b'        /*@ if (condition) {\n                 close raw_ptr_own::<Element>()(t, true_payload);\n'
       b'                 close <select_unpredictable::DropOnPanic<*Element>>.own(t, select_unpredictable::DropOnPanic::<*Element> { inner: guard });\n'
       b'             } else {\n                 close raw_ptr_own::<Element>()(t, false_payload);\n'
       b'                 close <select_unpredictable::DropOnPanic<*Element>>.own(t, select_unpredictable::DropOnPanic::<*Element> { inner: guard });\n'
       b'             } @*/\n', b'        drop.drop_in_place();\n', 'before'),
      ('saved_guard_owner_assertion',
       b'        /*@ assert <select_unpredictable::DropOnPanic<*Element>>.own(t, ?saved_guard); @*/\n',
       b'        crate::mem::forget(guard);\n', 'before'),
      ('post_forget_guard_owner_payload_projection',
       b'        /*@ open <select_unpredictable::DropOnPanic<*Element>>.own(t, saved_guard); @*/\n'
       b'        /*@ assert *saved_guard.inner |-> ?selected_payload; @*/\n'
       b'        /*@ open raw_ptr_own::<Element>()(t, selected_payload); @*/\n',
       b'        crate::mem::forget(guard);\n', 'after'),
    )
    removed=source.get('removed_owner_ghost_blocks') or []
    def removal_record_ok(index, spec, row):
        expected_name,expected,anchor,side=spec
        if not isinstance(row,dict) or expected not in parent_data or anchor not in parent_data:
            return False
        ordered=(parent_data.index(expected)<parent_data.index(anchor)
                 if side=='before' else parent_data.index(expected)>parent_data.index(anchor))
        return (row.get('index')==index and row.get('name')==expected_name and
            row.get('utf8')==expected.decode() and row.get('bytes')==len(expected) and
            row.get('sha256')==hashlib.sha256(expected).hexdigest() and
            row.get('byte_start')==parent_data.index(expected) and
            row.get('byte_end_exclusive')==row.get('byte_start')+len(expected) and
            row.get('anchor')==anchor.decode() and row.get('anchor_side')==side and ordered)
    removal_ok=(len(removed)==len(blocks) and all(
        removal_record_ok(index,spec,row)
        for index,(spec,row) in enumerate(zip(blocks,removed))))
    transformed=parent_data
    for _,block,_,_ in blocks:
        if transformed.count(block)!=1:
            transformed=b''; break
        transformed=transformed.replace(block,b'',1)
    if transformed and transformed.count(old_contract)==1:
        transformed=transformed.replace(old_contract,new_contract,1)
    else:
        transformed=b''
    runtime_source=re.sub(rb'(?m)^[ \t]*/\*@.*?@\*/(?:\r?\n)?',b'',data,flags=re.S)
    runtime_source=re.sub(rb'/\*@.*?@\*/(?:\r?\n)?',b'',runtime_source,flags=re.S)
    runtime_source=re.sub(rb'(?m)^[ \t]*//@[^\r\n]*(?:\r?\n|$)',b'',runtime_source)
    original_data=original.read_bytes() if original.is_file() else b''
    runtime_tokens=(b'crate::intrinsics::select_unpredictable(',
                    b'drop.drop_in_place();',b'crate::mem::forget(guard);',
                    b'.assume_init()')
    runtime_unchanged=(original.is_file() and runtime_source==original_data and
        hashlib.sha256(original_data).hexdigest()=='466882d74de217766ed8d5c583596c173df47f0e6bd40da7cb1a4c931d7265a5' and
        all(data.count(token)==parent_data.count(token) for token in runtime_tokens) and
        data.count(b'crate::intrinsics::select_unpredictable(')==3 and
        data.count(b'crate::mem::forget(guard);')==1 and
        data.count(b'drop.drop_in_place();')==1)
    final_assertion_markers=(
        b'/*@ assert true_payload == saved_true_input; @*/',
        b'/*@ assert false_payload == saved_false_input; @*/',
        b'/*@ assert std::mem::MaybeUninit::inner(current_true_wrapper) == some(saved_true_input); @*/',
        b'/*@ assert std::mem::MaybeUninit::inner(current_false_wrapper) == some(saved_false_input); @*/',
        b'/*@ assert std::mem::MaybeUninit::inner(true_val) == some(saved_true_input); @*/',
        b'/*@ assert std::mem::MaybeUninit::inner(false_val) == some(saved_false_input); @*/',
        b'/*@ assert std::mem::MaybeUninit::inner(if condition { true_val } else { false_val }) == some(if condition { saved_true_input } else { saved_false_input }); @*/')
    final_assertions_preserved=(transformed==data and all(
        parent_data.count(marker)==data.count(marker)>0 for marker in final_assertion_markers))
    parent_exact=(source.get('parent_case')=='r2-source/nine-body-wrapper-input-relation' and
        source.get('parent_verified_sha256')=='a95aff14592b167c62c53c7ed726128ee86c7c19768cfe613504cdec841f8463' and
        source.get('parent_parent_verified_sha256')=='11067f06ba7c745cfb221a559fb29778eba8d7b6e65f6db1a814ff7ce72bdfd4' and
        parent.is_file() and parent_original.is_file() and
        hashlib.sha256(parent_data).hexdigest()==source.get('parent_verified_sha256') and
        parent_summary.get('verified_sha256')==source.get('parent_verified_sha256') and
        parent_summary.get('parent_verified_sha256')==source.get('parent_parent_verified_sha256') and
        parent_original.read_bytes()==original.read_bytes() if original.is_file() else False)
    helper=source.get('forget_helper') or {}
    helper_exact=(isinstance(helper,dict) and
        helper.get('signature')=='pub unsafe fn checked_forget_owned<T>(t: T)' and
        helper.get('old_contract_utf8')==old_contract.decode() and
        helper.get('new_thread_only_contract_utf8')==new_contract.decode() and
        helper.get('runtime_body_same_as_std_forget') is True and
        helper.get('own_requirement_removed') is True and
        helper.get('own_ens_removed') is True and
        helper.get('unwind_false_preserved') is True and
        helper.get('same_public_generic_signature') is True and
        helper.get('runtime_body_sha256')=='8c7142c595a5e2d93986c1d1d7acbaf9a7e577f9736d2a705d5339c9280f18d8' and
        parent_data.count(old_contract)==1 and parent_data.count(new_contract)==0 and
        parent_data.count(helper_signature+old_contract+helper_body+b'\n')==1 and
        data.count(helper_signature+new_contract+helper_body+b'\n')==1 and
        data.count(old_contract)==0 and data.count(new_contract)==1 and
        data.count(helper_signature)==1 and data.count(helper_body)==1)
    source_ok=(source.get('classification')=='SOURCE_ONLY_THREADONLY_FRAME_CAPTURE_NOT_ACCEPTED' and
        source.get('case_name')=='nine-body-wrapper-input-relation-frame' and
        source.get('source_order')==canonical_source.get('source_order') and
        source.get('verified_sha256')==hashlib.sha256(data).hexdigest() and
        source.get('original_sha256')=='466882d74de217766ed8d5c583596c173df47f0e6bd40da7cb1a4c931d7265a5' and
        original.is_file() and hashlib.sha256(original.read_bytes()).hexdigest()==source.get('original_sha256') and
        source.get('ghost_strip_identity') is True and
        runtime_unchanged and final_assertions_preserved and
        source.get('verified_source_reversible_frame_transform') is True and
        source.get('actual_runtime_unchanged') is True and
        source.get('actual_calls_and_selected_cell_ghosts_retained') is True and
        source.get('selected_cell_never_folded_into_guard_owner') is True and
        source.get('full_mir_refinement_and_proof')=='NOT_RUN' and
        source.get('old_r3_certificate_expected_to_refuse') is True and
        source.get('semantic_frontend_enabled') is False and
        source.get('actual_helper_proved') is False and
        source.get('actual_safe_forget_linked') is False and
        source.get('verification_accepted') is False and source.get('accepted') is False and
        source.get('verified_sha256')!=canonical_source.get('verified_sha256') and
        parent_exact and removal_ok and helper_exact and transformed==data)
    current={label:row.get('sha256') for label,row in snapshots.items() if isinstance(row,dict)}
    recorded=(set(snapshots)==labels and set(prior)==labels and all(
        isinstance(snapshots.get(label),dict) and isinstance(prior.get(label),dict) and
        isinstance(snapshots[label].get('bytes'),int) and snapshots[label]['bytes']>0 and
        isinstance(current.get(label),str) and re.fullmatch('[0-9a-f]{64}',current[label]) and
        snapshots[label].get('file')==f'actual-nested-9-{label}.marshal' and
        (case/snapshots[label]['file']).is_file() and
        (case/snapshots[label]['file']).stat().st_size==snapshots[label]['bytes'] and
        digest(case/snapshots[label]['file'])==current[label]
        for label in labels))
    unchanged=(recorded and all(current[label]==prior[label].get('sha256')
                                for label in labels-{'unit','body-6','body-7'}))
    changed=(recorded and all(current[label]!=prior[label].get('sha256')
                              for label in ('unit','body-6','body-7')))
    full=result.get('full_body_capture') or {}
    source_order=source.get('source_order')
    if not isinstance(source_order,list) or len(source_order)!=9:source_order=[None]*9
    bodies=(isinstance(full,dict) and set(full)=={'normal','readonly'} and
        all(isinstance(full[mode],dict) and full[mode].get('exact_body_count_and_order') is True and
            full[mode].get('whole_decoded_mir_file')==f'{mode}-mir.txt' and
            (case/f'{mode}-mir.txt').is_file() and
            digest(case/f'{mode}-mir.txt')==full[mode].get('whole_decoded_mir_sha256') and
            isinstance(full[mode].get('bodies'),list) and len(full[mode]['bodies'])==9 and
            all(isinstance(row,dict) and row.get('index')==index and
                row.get('defpath')==source_order[index] and
                row.get('file')==f'{mode}-body-{index}-full-mir.txt' and
                isinstance(row.get('bytes'),int) and row['bytes']>0 and
                (case/row['file']).is_file() and
                (case/row['file']).stat().st_size==row['bytes'] and
                digest(case/row['file'])==row.get('sha256')
                for index,row in enumerate(full[mode]['bodies']))
            for mode in ('normal','readonly')))
    guard=result.get('guard_capture') or {}
    stages=guard.get('stages') or {}
    paired=(result.get('frontend_refinement_and_full_body_capture') is True and
        guard.get('frontend_refinement') is True and isinstance(stages,dict) and
        all(isinstance(stages.get(label),dict) and stages[label].get('exit')==0 and
            stages[label].get('source_unchanged') is True for label in
            ('normal-export','normal-decode','readonly-export','readonly-decode','refinement')))
    refusal=(fingerprint.get('classification')=='INTENDED_DIAGNOSTIC_REFUSAL_NO_PROOF_RULE' and
        fingerprint.get('all_ten_snapshots') is True and fingerprint.get('expected_refusal_seen') is True and
        fingerprint.get('body_proof_run') is False and
        isinstance(fingerprint.get('stage'),dict) and fingerprint['stage'].get('exit')==2)
    complete=(code==0 and result.get('source_mode')=='wrapper-input-relation-frame-source-only' and
        source_ok and paired and bodies and recorded and unchanged and changed and refusal and
        result.get('actual_helper_proved') is False and result.get('actual_safe_forget_linked') is False and
        result.get('semantic_rule_enabled') is False)
    return {'requested':True,'complete':complete,
        'classification':'THREADONLY_FRAME_SOURCE_CAPTURE_COMPLETE' if complete else 'INCONCLUSIVE',
        'helper_exit':code,'source_only':True,'accepted':False,
        'source_pair_exact':source_ok,'reversible_owner_frame_transform':parent_exact and removal_ok and transformed==data,
        'runtime_ghost_strip_exact':runtime_unchanged,
        'final_assertions_preserved':final_assertions_preserved,
        'thread_only_forget_contract_exact':helper_exact,
        'paired_normal_readonly_refinement_complete':paired,'full_nine_bodies_hashed':bodies,
        'ten_snapshots_independently_hashed':recorded,'unchanged_body_snapshots_exact':unchanged,
        'unit_helper_outer_snapshots_changed':changed,'fingerprint_no_proof_rule_refusal':refusal,
        'old_r3_certificate_expected_to_refuse':source.get('old_r3_certificate_expected_to_refuse') is True,
        'observed_verified_sha256':source.get('verified_sha256'),
        'accepted_actual_source':False,'actual_helper_proved':False,'actual_safe_forget_linked':False,
        'full_actual_proof_run':False}

def r3_frame_test_diagnostic(ev):
    name='r3-frame-test'
    requested=(ev/'cases/r3-frame-test-request.json').is_file()
    if not requested:
        return {'requested':False,'complete':False,'classification':'NOT_RUN',
                'accepted':False,'verification_accepted':False,
                'target_contract_proved':False}
    root=ev/'cases'/name
    result=read(root/'diagnostic-audit.json') or {}
    if not isinstance(result,dict):result={}
    code=helper_exit(ev,name)
    stages=result.get('stages') or {}
    if not isinstance(stages,dict):stages={}
    frame=result.get('source_capture_frame') or {}
    old=result.get('source_capture_old_r3') or {}
    outcome=result.get('classification')
    nested_regression=(outcome=='R3_FRAME_TEST_NESTED_REGRESSION_OUTER_NOT_REACHED')
    required={'old-r3-source-off','frame-source-off','frame-source-partial','frame-source-on'}
    classification_ok=((outcome=='R3_FRAME_TEST_DIAGNOSTIC_COMPLETE' and
                        result.get('nested_actual_failure') is False) or nested_regression)
    nested_regression_ok=(not nested_regression or (
        result.get('nested_actual_failure') is True and
        result.get('frame_on_outer_reached') is False and
        (stages.get('frame-source-on') or {}).get('outer_header_seen') is False and
        (stages.get('frame-source-on') or {}).get('outer_prototype_seen') is False and
        (stages.get('frame-source-on') or {}).get('first_error_in_nested') is True and
        (stages.get('frame-source-on') or {}).get('nested_full_normal_unwind_observed') is False and
        (stages.get('frame-source-on') or {}).get('proof_exit') in (1,2)))
    complete=(code==0 and classification_ok and
        result.get('diagnostic_complete') is True and result.get('accepted') is False and
        result.get('verification_accepted') is False and
        result.get('actual_source_accepted') is False and
        result.get('target_contract_proved') is False and
        result.get('actual_helper_proved') is False and
        result.get('actual_safe_forget_linked') is False and set(stages)==required and
        result.get('outer_credit') is False and
        result.get('actual_outer_240_progress') is False and nested_regression_ok and
        result.get('wrong_helper_contract_negative_complete') is False and
        result.get('wrong_typed_move_edge_negative_complete') is False and
        frame.get('source_pair_exact') is True and frame.get('ten_fingerprints_exact') is True and
        frame.get('full_normal_readonly_nine_body_capture') is True and
        frame.get('normal_readonly_refinement') is True and
        old.get('source_pair_exact') is True and old.get('ten_fingerprints_exact') is True and
        old.get('full_normal_readonly_nine_body_capture') is True and
        old.get('normal_readonly_refinement') is True and
        stages['old-r3-source-off'].get('reached_outer_240') is True and
        stages['frame-source-off'].get('preheader_refusal') is True and
        stages['frame-source-partial'].get('preheader_refusal') is True and
        stages['frame-source-on'].get('prefix7_ordered') is True and
        stages['frame-source-on'].get('nested_before_outer') is True and
        stages['frame-source-on'].get('errors_before_nested') is False and
        stages['frame-source-on'].get('helper_full_normal_unwind_observed') is True and
        stages['frame-source-on'].get('first_causal_error_attributed') is True)
    return {'requested':True,'complete':complete,
        'classification':result.get('classification','INCONCLUSIVE'),
        'helper_exit':code,'accepted':False,'verification_accepted':False,
        'target_contract_proved':False,'actual_source_accepted':False,
        'nested_actual_failure':result.get('nested_actual_failure') is True,
        'frame_on_outer_reached':result.get('frame_on_outer_reached') is True,
        'outer_credit':False,'actual_outer_240_progress':False,
        'source_capture_and_stage_gates_complete':complete,
        'first_frame_error':result.get('frame_on_first_error'),
        'nested_full_normal_unwind':result.get('frame_on_nested_full_normal_unwind') is True,
        'outer_full_normal_unwind':result.get('frame_on_outer_full_normal_unwind') is True,
        'first_causal_error_attributed':(stages.get('frame-source-on') or {}).get('first_causal_error_attributed') is True,
        'wrong_helper_contract_negative_complete':False,
        'wrong_typed_move_edge_negative_complete':False}

def wrapper_input_relation_shadow_capture(ev):
    name='wrapper-input-relation-shadow-capture'
    if not (ev/'cases'/f'{name}-request.json').exists():
        return {'requested':False,'complete':False,'classification':'NOT_RUN',
                'source_only':True,'accepted':False}
    result=read(ev/'cases'/name/'summary.json') or {}
    if not isinstance(result,dict):result={}
    code=helper_exit(ev,name)
    case=ev/'cases'/name/'nine-body-wrapper-input-relation-shadow'
    source=result.get('source') or {}
    fingerprint=result.get('fingerprint') or {}
    if not isinstance(source,dict):source={}
    if not isinstance(fingerprint,dict):fingerprint={}
    parent=ev/'cases'/name/'parent-r3-source'/'nine-body-wrapper-input-relation'
    parent_source=read(parent/'fixture.json') or {}
    if not isinstance(parent_source,dict):parent_source={}
    verified=case/'verified/lib.rs'; original=case/'original/lib.rs'
    data=verified.read_bytes() if verified.is_file() else b''
    old=parent/'verified/lib.rs'
    old_bytes=old.read_bytes() if old.is_file() else b''
    profile=read(Path('/workspace/proof/research/challenge-8/overnight-assume-actual/O26-WRAPPER-INPUT-RELATION-PROFILE.json')) or {}
    draft=read(Path('/workspace/proof/research/challenge-8/overnight-assume-actual/O26-WRAPPER-INPUT-RELATION-SHADOW-DRAFT.json')) or {}
    if not isinstance(profile,dict):profile={}
    if not isinstance(draft,dict):draft={}
    expected_source=profile.get('source') or {}
    if not isinstance(expected_source,dict):expected_source={}
    comments=source.get('inserted_ghost_comments') or []
    regions=source.get('inserted_ghost_regions') or []
    old_comments=parent_source.get('inserted_ghost_comments') or []
    names=('save_true_input','save_false_input','true_payload_matches_input',
           'false_payload_matches_input','current_true_wrapper_matches_input',
           'current_false_wrapper_matches_input','shadow_true_wrapper_matches_input',
           'shadow_false_wrapper_matches_input','conditional_wrapper_matches_input')
    region_names=('before_rust_shadow','after_opened_payloads',
                  'after_rebased_wrapper_closes')
    def span_ok(row,require_text):
        if not isinstance(row,dict):return False
        start=row.get('byte_start'); end=row.get('byte_end_exclusive')
        if not isinstance(start,int) or not isinstance(end,int) or not 0<=start<end<=len(data):
            return False
        fragment=data[start:end]
        return (row.get('bytes')==len(fragment) and
                row.get('sha256')==hashlib.sha256(fragment).hexdigest() and
                row.get('line_start_one_based')==data.count(b'\n',0,start)+1 and
                row.get('column_start_zero_based')==start-(data.rfind(b'\n',0,start)+1) and
                row.get('line_end_one_based')==data.count(b'\n',0,end)+1 and
                row.get('column_end_zero_based')==end-(data.rfind(b'\n',0,end)+1) and
                (not require_text or row.get('utf8')==fragment.decode('utf-8',errors='replace')))
    metadata=(isinstance(comments,list) and len(comments)==9 and
              isinstance(regions,list) and len(regions)==3 and
              all(isinstance(row,dict) and row.get('index')==i and
                  row.get('name')==names[i] and
                  row.get('region')==region_names[0 if i<2 else 1 if i<4 else 2] and
                  span_ok(row,True) for i,row in enumerate(comments)) and
              all(isinstance(row,dict) and row.get('index')==i and
                  row.get('name')==region_names[i] and span_ok(row,False)
                  for i,row in enumerate(regions)) and
              all(regions[i]['byte_start']==comments[first]['byte_start'] and
                  regions[i]['byte_end_exclusive']==comments[last]['byte_end_exclusive'] and
                  all(comments[j]['byte_end_exclusive']==comments[j+1]['byte_start']
                      for j in range(first,last))
                  for i,(first,last) in enumerate(((0,1),(2,3),(4,8)))) and
              all(comments[i]['byte_start']<comments[i+1]['byte_start'] for i in range(8)))
    parent_pin=(draft.get('status')=='REVIEWED_SOURCE_ONLY_SHADOW_BINDING' and
                draft.get('verification_accepted') is False and
                draft.get('parent_verified_sha256')==expected_source.get('verified_sha256') and
                source.get('parent_verified_sha256')==expected_source.get('verified_sha256') and
                old.is_file() and digest(old)==source.get('parent_verified_sha256') and
                parent_source.get('classification')==
                  'SOURCE_ONLY_WRAPPER_INPUT_RELATION_DIAGNOSTIC_NOT_ACCEPTED' and
                parent_source.get('verified_sha256')==source.get('parent_verified_sha256') and
                source.get('parent_case')=='parent-r3-source/nine-body-wrapper-input-relation')
    names_normal=draft.get('reviewed_normal_shadow_internal_names')
    names_readonly=draft.get('reviewed_readonly_shadow_internal_names')
    shadow_names=(isinstance(names_normal,dict) and names_normal==names_readonly and
                  set(names_normal)=={'true_val','false_val'} and
                  all(isinstance(names_normal[key],str) and
                      re.fullmatch(key+r'_[1-9][0-9]*',names_normal[key])
                      for key in ('true_val','false_val')))
    reversible=False
    if metadata and parent_pin and shadow_names and isinstance(old_comments,list) and len(old_comments)==9:
        try:
            old_text=[row['utf8'].encode() for row in old_comments]
            new_text=[row['utf8'].encode() for row in comments]
            stable=all(new_text[i]==old_text[i] for i in range(9) if i not in (6,7,8))
            restored=data
            for i in (6,7,8):
                if restored.count(new_text[i])!=1 or old_bytes.count(old_text[i])!=1:
                    stable=False
                    break
                restored=restored.replace(new_text[i],old_text[i],1)
            reversible=(stable and restored==old_bytes and
                        source.get('changed_late_comment_names')==sorted(names[6:9]) and
                        source.get('shadow_internal_names')==names_normal)
        except (KeyError,AttributeError,TypeError,ValueError,UnicodeEncodeError):
            reversible=False
    pair=(parent_pin and metadata and reversible and
          source.get('classification')=='SOURCE_ONLY_SHADOW_BINDING_REVISION_NOT_ACCEPTED' and
          source.get('case_name')=='nine-body-wrapper-input-relation-shadow' and
          source.get('verified_sha256')!=source.get('parent_verified_sha256') and
          verified.is_file() and digest(verified)==source.get('verified_sha256') and
          original.is_file() and digest(original)==ORIGINAL==source.get('original_sha256') and
          source.get('ghost_strip_identity') is True and
          source.get('verified_source_reversible_three_late_comment_substitutions') is True and
          source.get('actual_runtime_unchanged') is True and
          source.get('verification_accepted') is False and
          source.get('full_mir_refinement_and_proof')=='NOT_RUN' and
          source.get('source_order')==parent_source.get('source_order'))
    guard=result.get('guard_capture') or {}
    if not isinstance(guard,dict):guard={}
    stages=guard.get('stages') or {}
    if not isinstance(stages,dict):stages={}
    paired=(result.get('frontend_refinement_and_full_body_capture') is True and
            guard.get('frontend_refinement') is True and
            all(isinstance(stages.get(label),dict) and stages[label].get('exit')==0 and
                stages[label].get('source_unchanged') is True for label in
                ('normal-export','normal-decode','readonly-export','readonly-decode','refinement')))
    bodies=result.get('full_body_capture') or {}
    full_bodies=(isinstance(bodies,dict) and set(bodies)=={'normal','readonly'} and
                 all(isinstance(bodies[mode],dict) and
                     bodies[mode].get('exact_body_count_and_order') is True and
                     isinstance(bodies[mode].get('bodies'),list) and
                     len(bodies[mode]['bodies'])==9 and
                     all(isinstance(row,dict) and row.get('index')==i and
                         row.get('file')==f'{mode}-body-{i}-full-mir.txt' and
                         (case/row['file']).is_file() and
                         digest(case/row['file'])==row.get('sha256') and
                         (case/row['file']).stat().st_size==row.get('bytes')
                         for i,row in enumerate(bodies[mode]['bodies'])) and
                     (case/f'{mode}-mir.txt').is_file() and
                     digest(case/f'{mode}-mir.txt')==bodies[mode].get('whole_decoded_mir_sha256')
                     for mode in ('normal','readonly')))
    snaps=fingerprint.get('snapshots') or {}
    if not isinstance(snaps,dict):snaps={}
    expected_bodies=expected_source.get('body_sha256') or []
    ten=(set(snaps)=={'unit',*(f'body-{i}' for i in range(9))} and
         all(isinstance(row,dict) and row.get('file')==f'actual-nested-9-{key}.marshal' and
             isinstance(row.get('bytes'),int) and row['bytes']>0 and
             (case/row['file']).is_file() and
             (case/row['file']).stat().st_size==row['bytes'] and
             digest(case/row['file'])==row.get('sha256')
             for key,row in snaps.items()))
    unchanged=(ten and isinstance(expected_bodies,list) and len(expected_bodies)==9 and
               all(snaps[f'body-{i}']['sha256']==expected_bodies[i]
                   for i in range(9) if i!=7))
    changed=(ten and snaps['unit'].get('sha256')!=expected_source.get('unit_sha256') and
             snaps['body-7'].get('sha256')!=expected_bodies[7]) if len(expected_bodies)==9 else False
    refusal=(fingerprint.get('classification')=='INTENDED_DIAGNOSTIC_REFUSAL_NO_PROOF_RULE' and
             fingerprint.get('all_ten_snapshots') is True and
             fingerprint.get('expected_refusal_seen') is True and
             fingerprint.get('body_proof_run') is False and
             result.get('semantic_rule_enabled') is False and
             (fingerprint.get('stage') or {}).get('exit')==2)
    complete=(code==0 and result.get('source_mode')=='wrapper-input-relation-shadow-source-only' and
              pair and paired and full_bodies and ten and unchanged and changed and refusal)
    return {'requested':True,'complete':complete,'accepted':False,'source_only':True,
            'classification':'SHADOW_BINDING_SOURCE_CAPTURE_COMPLETE' if complete else 'INCONCLUSIVE',
            'helper_exit':code,'exact_parent_and_three_late_substitutions':pair,
            'paired_mir_refinement_complete':paired,'full_nine_bodies_hashed':full_bodies,
            'ten_snapshots_independently_hashed':ten,'eight_r3_bodies_unchanged':unchanged,
            'unit_and_body7_changed':changed,'fingerprint_no_proof_rule_refusal':refusal,
            'historical_owner17_refusal_observed':False,
            'observed_verified_sha256':source.get('verified_sha256'),
            'observed_unit_sha256':(snaps.get('unit') or {}).get('sha256')
                if isinstance(snaps.get('unit'),dict) else None,
            'observed_body7_sha256':(snaps.get('body-7') or {}).get('sha256')
                if isinstance(snaps.get('body-7'),dict) else None}

def sort4_postmark_print(ev):
    requested=(ev/'cases/sort4-postmark-print-test-request.json').exists()
    if not requested:
        return {'requested':False,'complete':False}
    inner=ev/'cases/sort4-postmark-print-test'
    report=read(inner/'sort4-postmark-result.json') or {}
    code=helper_exit(ev,'sort4-postmark-print-test')
    complete=(code==0 and report.get('classification')=='PRINT_ONLY_POSTMARK_LOCAL_TYPES_DIAGNOSTIC' and
              report.get('diagnostic_complete') is True and report.get('verification_accepted') is False)
    return {'requested':True,'complete':complete,'helper_exit':code,'accepted':False,
            'actual_sort4_proved':False,'storage_cleanup_proved':False,'report':report,
            'report_sha256':digest(inner/'sort4-postmark-result.json') if (inner/'sort4-postmark-result.json').is_file() else None}


def r3_nested_order(ev):
    requested=(ev/'cases/r3-nested-order-test-request.json').exists()
    if not requested:return {'requested':False,'complete':False}
    report=read(ev/'cases/r3-nested-order-test/diagnostic-audit.json') or {}
    code=helper_exit(ev,'r3-nested-order-test')
    complete=(code==0 and report.get('classification')=='R3_NESTED_ORDER_TEST_DIAGNOSTIC_COMPLETE' and
              report.get('diagnostic_complete') is True and
              report.get('nested_normal_unwind_return_leak_log_observed') is True and
              report.get('seven_prefix_then_nested_then_outer') is True and
              report.get('verification_accepted') is False and report.get('accepted') is False and
              report.get('actual_nested_drop_credit') is False)
    return {'requested':True,'complete':complete,'helper_exit':code,'accepted':False,
            'actual_helper_proved':False,'report':report}

def r3_ghost_scope_test(ev):
    requested=(ev/'cases/r3-ghost-scope-test-request.json').exists()
    if not requested:return {'requested':False,'complete':False,'accepted':False}
    root=ev/'cases/r3-ghost-scope-test'
    report=read(root/'diagnostic-audit.json') or {}
    code=helper_exit(ev,'r3-ghost-scope-test')
    parent=ev/'cases/wrapper-r3-profile'
    capture=read(parent/'capture-check.json') or {}
    positive=read(parent/'r3-positive-stage.json') or {}
    identity=read(parent/'tool-identity.json') or {}
    after=read(parent/'tool-identity-after.json') or {}
    parent_code=helper_exit(ev,'wrapper-r3-profile')
    complete=(code==0 and parent_code==0 and
              capture.get('classification')=='R3_SOURCE_MIR_GRAPH_PINNED_DIAGNOSTIC' and
              capture.get('all_nine_body_records_and_ten_marshal_files_hashed') is True and
              capture.get('typed_outer_mir_exact') is True and
              identity==after and bool(identity) and
              positive.get('status')=='RAN' and
              positive.get('source_unchanged') is True and
              report.get('classification')=='R3_GHOST_SCOPE_TEST_DIAGNOSTIC_COMPLETE' and
              report.get('diagnostic_complete') is True and
              all(report.get(key) is True for key in
                  ('r3_capture_rechecked','tool_identity_rechecked',
                   'default_off_refusal','partial_pair_refusal','enabled_scope_marker')) and
              report.get('accepted') is False and
              report.get('verification_accepted') is False and
              report.get('actual_nested_drop_credit') is False and
              report.get('actual_helper_proved') is False)
    receiver_requested=os.environ.get('O26_WITH_R3_RECEIVER_TEST','0')=='1'
    receiver=report.get('receiver_test') or {}
    if receiver_requested:
        complete=(complete and report.get('receiver_test_requested') is True and
                  receiver.get('classification')=='R3_RECEIVER_TEST_DIAGNOSTIC_COMPLETE' and
                  receiver.get('diagnostic_complete') is True and
                  all(receiver.get(k) is True for k in
                      ('exact_scope_parent','default_off_refusal','partial_pair_refusal',
                       'receiver_on_markers','wrong_first_receiver_negative','wrong_second_receiver_negative')) and
                  all(receiver.get(k) is False for k in
                      ('accepted','verification_accepted','actual_source_accepted','target_contract_proved',
                       'malformed_place_admissibility_complete')))
    column_requested=os.environ.get('O26_WITH_R3_GHOST_COLUMN_TEST','0')=='1'
    nested_requested=os.environ.get('O26_WITH_R3_COLUMN_NESTED_TEST','0')=='1'
    column=report.get('ghost_column_test') or {}
    if column_requested:
        complete=(complete and report.get('ghost_column_test_requested') is True and
                  column.get('classification')=='R3_GHOST_COLUMN_TEST_DIAGNOSTIC_COMPLETE' and
                  column.get('diagnostic_complete') is True and
                  all(column.get(k) is False for k in
                      ('accepted','verification_accepted','actual_source_accepted','target_contract_proved',
                       'source_unit_span_negative_gates_complete')))
    nested=column.get('nested_scheduler_test') or {}
    if nested_requested:
        complete=(complete and column_requested and
                  column.get('nested_scheduler_test_requested') is True and
                  nested.get('classification')=='R3_COLUMN_NESTED_SCHEDULER_DIAGNOSTIC_COMPLETE' and
                  nested.get('diagnostic_complete') is True and
                  all(nested.get(k) is False for k in
                      ('accepted','verification_accepted','actual_nested_drop_credit','actual_helper_proved')) and
                  isinstance(nested.get('actual_nested_drop_full_normal_unwind_observed'),bool))
    return {'requested':True,'complete':complete,'helper_exit':code,
            'parent_helper_exit':parent_code,'accepted':False,
            'actual_nested_drop_credit':False,'actual_helper_proved':False,
            'report':report}


def wrapper_r3_profile(ev):
    requested=(ev/'cases/wrapper-r3-profile-request.json').exists()
    if not requested:
        return {'requested':False,'complete':False}
    inner=ev/'cases/wrapper-r3-profile'
    report=read(inner/'diagnostic-audit.json') or {}
    code=helper_exit(ev,'wrapper-r3-profile')
    complete=(code==0 and
              report.get('classification')=='WRAPPER_R3_PROFILE_DIAGNOSTIC_COMPLETE' and
              report.get('diagnostic_complete') is True and
              report.get('verification_accepted') is False and
              report.get('accepted') is False)
    return {'requested':True,'complete':complete,'helper_exit':code,
            'classification':'WRAPPER_R3_PROFILE_DIAGNOSTIC_COMPLETE' if complete else 'INCONCLUSIVE',
            'accepted':False,'actual_helper_proved':False,
            'report_sha256':digest(inner/'diagnostic-audit.json') if (inner/'diagnostic-audit.json').is_file() else None,
            'report':report}


def wrapper_profile(ev):
    name='wrapper-profile'
    if not (ev/'cases'/f'{name}-request.json').exists():
        return {'requested':False,'complete':False,'classification':'NOT_RUN',
                'verification_accepted':False}
    root=ev/'cases'/name
    code=helper_exit(ev,name)
    manifest=read(root/'profile-manifest.json') or {}
    identity=read(root/'tool-identity.json') or {}
    identity_after=read(root/'tool-identity-after.json') or {}
    baseline=read(root/'production-tool-baseline.json') or {}
    capture=read(root/'capture-check.json') or {}
    positive=read(root/'profile-proof-stage.json') or {}
    off_canonical=read(root/'profile-off-canonical-stage.json') or {}
    off_rebase=read(root/'profile-off-rebase-stage.json') or {}
    controls=read(root/'owner17-controls/summary.json') or {}
    a1capture=read(root/'a1-isolated-test/capture-summary.json') or {}
    a1test=read(root/'a1-isolated-test/test-result.json') or {}
    case=root/'capture/nine-body-wrapper-rebase'
    positive_log=case/'profile-proof.log'
    off_log=case/'profile-off-rebase.log'
    canonical_case=ev/'cases/candidate/capture/nine-body-a1-owned-forget'
    canonical_log=canonical_case/'refreshed-proof.log'
    off_canonical_log=canonical_case/'profile-off-canonical.log'
    body=positive_log.read_text(errors='replace') if positive_log.is_file() else ''
    off_body=off_log.read_text(errors='replace') if off_log.is_file() else ''
    source=(manifest.get('source') or {}).get('verified_sha256')
    marks=[body.find("Verifying function '"+item+"'") for item in PREFIX_CALLEES]
    nested=body.find("Verifying function '<select_unpredictable::DropOnPanic<T> as std::ops::Drop>::drop'")
    outer=body.find("Verifying function 'select_unpredictable'")
    same_version_callees=(all(at>=0 for at in marks) and marks==sorted(marks) and
                          outer>max(marks) and
                          positive.get('source_before',{}).get('verified/lib.rs')==source)
    proof_ran=(positive.get('status')=='RAN' and
               positive.get('exit') not in (None,124,137) and
               positive.get('source_unchanged') is True and
               positive.get('source_before')==positive.get('source_after') and
               positive.get('intrinsic_gate_active') is True and
               positive.get('pointer_drop_gate_active') is True and
               same_version_callees)
    off_fatal='Fatal error: exception Failure("SORT4-SELECT-INTRINSIC: certificate mismatch: owner exact verified source SHA256")'
    off_lines=[x for x in off_body.splitlines() if x.startswith('Fatal error:')]
    off_rebase_complete=(off_rebase.get('status')=='RAN' and off_rebase.get('exit')==2 and
                  off_rebase.get('source_unchanged') is True and
                  off_rebase.get('source_before')==off_rebase.get('source_after') and
                  off_rebase.get('source_before',{}).get('verified/lib.rs')==source and
                  off_rebase.get('intrinsic_gate_active') is True and
                  off_rebase.get('pointer_drop_gate_active') is True and
                  off_lines==[off_fatal] and
                  "Verifying function '" not in off_body)
    original_body=canonical_log.read_text(errors='replace') if canonical_log.is_file() else ''
    canonical_off_body=off_canonical_log.read_text(errors='replace') if off_canonical_log.is_file() else ''
    error_pattern=re.compile(r'^(.+?)\((\d+),([^)]*)\): error: (.*)$',re.MULTILINE)
    original_error=error_pattern.findall(original_body)
    off_error=error_pattern.findall(canonical_off_body)
    base_stage=(read(ev/'cases/candidate/proof-stage.json') or {}).get('stage',{})
    off_canonical_complete=(off_canonical.get('status')=='RAN' and
                            off_canonical.get('exit')==base_stage.get('exit') and
                            off_canonical.get('source_unchanged') is True and
                            off_canonical.get('source_before')==off_canonical.get('source_after') and
                            off_canonical.get('source_before')==base_stage.get('source_before') and
                            off_canonical.get('intrinsic_gate_active') is True and
                            off_canonical.get('pointer_drop_gate_active') is True and
                            bool(original_error) and bool(off_error) and
                            original_error[0][0].endswith('lib.rsspec') and
                            off_error[0][0].endswith('lib.rsspec') and
                            original_error[0][1:]==off_error[0][1:] and
                            original_error[0][1:3]==('462','47-48'))
    controls_complete=(controls.get('classification')=='COMPONENT17_REBASE_CONTROLS_COMPLETE' and
                       controls.get('diagnostic_complete') is True and
                       controls.get('verification_accepted') is False and
                       len(controls.get('negative_cases',[]))==4 and
                       all(r.get('intended_component17_refusal') is True
                           for r in controls['negative_cases']))
    a1_complete=(a1capture.get('owner_hash_only_refusal') is True and
                 a1capture.get('normal_readonly_refinement_complete') is True and
                 a1test.get('classification')=='REBASE_A1_MOVE_COPY_NEGATIVE' and
                 a1test.get('intended_a1_refusal') is True and
                 a1test.get('verification_accepted') is False)
    complete=(code==0 and
              manifest.get('classification')=='EXPERIMENTAL_O26_WRAPPER_REBASE_COMPONENT23_R2_NOT_ACCEPTED' and
              identity.get('stock_binaries_unchanged') is True and
              identity.get('kernel_schema_parser_unchanged') is True and
              identity.get('all_other_tracked_sources_and_rsspec_unchanged') is True and
              bool(baseline) and identity.get('production_snapshot')==baseline and
              identity_after==identity and
              capture.get('classification')=='WRAPPER_REBASE_CAPTURE_PINNED' and
              capture.get('normal_readonly_refinement_complete') is True and
              capture.get('ten_snapshots_independently_hashed') is True and
              capture.get('eight_canonical_bodies_unchanged') is True and
              proof_ran and off_canonical_complete and off_rebase_complete and
              controls_complete and a1_complete)
    return {'requested':True,'complete':complete,
            'classification':'WRAPPER_REBASE_PROFILE_DIAGNOSTIC_COMPLETE' if complete else 'INCONCLUSIVE',
            'helper_exit':code,'source_sha256':source,
            'positive_six_gate_full_proof_ran':proof_ran,
            'positive_full_proof_exit_zero':proof_ran and positive.get('exit')==0,
            'positive_full_proof_exit':positive.get('exit'),
            'same_version_callees_before_outer':same_version_callees,
            'nested_drop_proof_header_visible':nested>=0,
            'component23_off_canonical_first462_unchanged':off_canonical_complete,
            'component23_off_rebase_old_source_pin_refusal':off_rebase_complete,
            'owner17_controls_complete':controls_complete,
            'a1_move_copy_negative_complete':a1_complete,
            'verification_accepted':False}

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
    strict_cut=strict_cut_controls(ev)
    false_posts=strict_cut_false_posts(ev)
    owner=owner_controls(ev)
    sort4=sort4_capture(ev)
    a1=a1_test(ev)
    coordination=coordination_regression(ev)
    nested_order=nested_proof_order(ev)
    ast_probe=sort4_ast_probe(ev)
    wrapper_rebase=wrapper_rebase_capture(ev,cap)
    input_relation=wrapper_input_relation_capture(ev,cap)
    input_relation_frame=wrapper_input_relation_frame_capture(ev,cap)
    frame_test=r3_frame_test_diagnostic(ev)
    input_relation_shadow=wrapper_input_relation_shadow_capture(ev)
    generic_new=generic_new_capture(ev)
    rebase_profile=wrapper_profile(ev)
    r3_profile=wrapper_r3_profile(ev)
    ghost_scope=r3_ghost_scope_test(ev)
    postmark=sort4_postmark_print(ev)
    postmark_lane=os.environ.get('LANE')=='o26-generic-sort4-postmark-diagnostics'
    r3_lane=os.environ.get('LANE') in ('o26-wrapper-input-relation-r3','o26-wrapper-r3-nested-diagnostics')
    r3_nested=r3_nested_order(ev)
    r3_nested_lane=os.environ.get('LANE')=='o26-wrapper-r3-nested-diagnostics'
    ghost_scope_lane=os.environ.get('LANE')=='o26-r3-ghost-scope-test'
    independent=os.environ.get('LANE')=='o26-independent-tests'
    recovery=os.environ.get('LANE')=='o26-recovery-tests'
    strict_cut_lane=os.environ.get('LANE')=='o26-strict-cut-controls'
    strict_false_posts_lane=os.environ.get('LANE')=='o26-strict-cut-false-posts'
    strict_reuse_lane=os.environ.get('LANE')=='o26-strict-cut-reuse-false-posts'
    input_relation_lane=os.environ.get('LANE')=='o26-input-relation-capture'
    input_relation_frame_lane=os.environ.get('LANE')=='o26-input-relation-frame-capture'
    frame_test_lane=os.environ.get('LANE')=='o26-input-relation-frame-test'
    input_relation_shadow_lane=os.environ.get('LANE')=='o26-input-relation-shadow-capture'
    shadow_generic_lane=os.environ.get('LANE')=='o26-shadow-generic-sort4-diagnostics'
    generic_new_lane=os.environ.get('LANE')=='o26-generic-new-capture'
    independent_requested=(coordination['requested'] and nested_order['requested'] and ast_probe['requested'] and
                           wrapper_rebase['requested'] and
                           not owner['requested'] and not sort4['requested'] and
                           not a1['requested'] and not cut['requested'])
    recovery_requested=(cut['requested'] and ast_probe['requested'] and
                        not owner['requested'] and not sort4['requested'] and
                        not a1['requested'] and not coordination['requested'] and
                        not nested_order['requested'] and not wrapper_rebase['requested'] and
                        not rebase_profile['requested'])
    strict_cut_requested=(cut['requested'] and strict_cut['requested'] and
                          not false_posts['requested'] and
                          not owner['requested'] and not sort4['requested'] and
                          not a1['requested'] and not coordination['requested'] and
                          not nested_order['requested'] and not ast_probe['requested'] and
                          not wrapper_rebase['requested'] and
                          not input_relation['requested'] and
                          not rebase_profile['requested'])
    strict_false_posts_requested=(cut['requested'] and strict_cut['requested'] and
                                  false_posts['requested'] and
                                  not owner['requested'] and not sort4['requested'] and
                                  not a1['requested'] and not coordination['requested'] and
                                  not nested_order['requested'] and not ast_probe['requested'] and
                                  not wrapper_rebase['requested'] and
                                  not input_relation['requested'] and
                                  not rebase_profile['requested'])
    input_relation_requested=(input_relation['requested'] and
                              not cut['requested'] and not strict_cut['requested'] and
                              not false_posts['requested'] and
                              not ast_probe['requested'] and
                              not owner['requested'] and not sort4['requested'] and
                              not a1['requested'] and not coordination['requested'] and
                              not nested_order['requested'] and not wrapper_rebase['requested'] and
                              not rebase_profile['requested'])
    input_relation_frame_requested=(input_relation_frame['requested'] and
                              not cut['requested'] and not strict_cut['requested'] and
                              not false_posts['requested'] and not ast_probe['requested'] and
                              not owner['requested'] and not sort4['requested'] and
                              not a1['requested'] and not coordination['requested'] and
                              not nested_order['requested'] and not wrapper_rebase['requested'] and
                              not input_relation['requested'] and
                              not input_relation_shadow['requested'] and
                              not generic_new['requested'] and not rebase_profile['requested'] and
                              not r3_profile['requested'] and not ghost_scope['requested'] and
                              not r3_nested['requested'] and not postmark['requested'])
    frame_test_requested=(frame_test['requested'] and
                              not cut['requested'] and not strict_cut['requested'] and
                              not false_posts['requested'] and not ast_probe['requested'] and
                              not owner['requested'] and not sort4['requested'] and
                              not a1['requested'] and not coordination['requested'] and
                              not nested_order['requested'] and not wrapper_rebase['requested'] and
                              not input_relation['requested'] and
                              not input_relation_frame['requested'] and
                              not input_relation_shadow['requested'] and
                              not generic_new['requested'] and not rebase_profile['requested'] and
                              not r3_profile['requested'] and not ghost_scope['requested'] and
                              not r3_nested['requested'] and not postmark['requested'])
    input_relation_shadow_requested=(input_relation_shadow['requested'] and
                                     not any(x['requested'] for x in
                                     (cut,strict_cut,false_posts,ast_probe,owner,sort4,a1,
                                      coordination,nested_order,wrapper_rebase,input_relation,
                                      generic_new,rebase_profile,r3_profile,postmark,r3_nested)))
    generic_new_requested=(generic_new['requested'] and
                           not cut['requested'] and not strict_cut['requested'] and
                           not false_posts['requested'] and not input_relation['requested'] and
                           not ast_probe['requested'] and not owner['requested'] and
                           not sort4['requested'] and not a1['requested'] and
                           not coordination['requested'] and not nested_order['requested'] and
                           not wrapper_rebase['requested'] and not rebase_profile['requested'])
    postmark_requested=(postmark['requested'] and generic_new['requested'] and
                  not any(x['requested'] for x in
                  (cut,strict_cut,false_posts,owner,sort4,a1,coordination,nested_order,
                   ast_probe,wrapper_rebase,input_relation,rebase_profile,r3_profile)))
    shadow_generic_requested=(input_relation_shadow['requested'] and
                              generic_new['requested'] and postmark['requested'] and
                              not any(x['requested'] for x in
                              (cut,strict_cut,false_posts,owner,sort4,a1,coordination,
                               nested_order,ast_probe,wrapper_rebase,input_relation,
                               rebase_profile,r3_profile,r3_nested)))
    r3_requested=(r3_profile['requested'] and not any(x['requested'] for x in
                  (cut,strict_cut,false_posts,owner,sort4,a1,coordination,nested_order,
                   ast_probe,wrapper_rebase,input_relation,generic_new,rebase_profile)))
    ghost_scope_requested=(r3_profile['requested'] and ghost_scope['requested'] and
                           not r3_nested['requested'] and not any(x['requested'] for x in
                           (cut,strict_cut,false_posts,owner,sort4,a1,coordination,
                            nested_order,ast_probe,wrapper_rebase,input_relation,
                            input_relation_shadow,generic_new,rebase_profile,postmark)))
    diagnostic_complete=(a.runner_exit==0 and pair and proof_ran and profile_ok and
                         (not owner['requested'] or owner['complete']) and
                         (not sort4['requested'] or sort4['complete']) and
                         (not a1['requested'] or a1['complete']) and
                         (not cut['requested'] or cut.get('diagnostic_match') is True) and
                         (not strict_cut['requested'] or strict_cut['complete']) and
                         (not false_posts['requested'] or false_posts['complete']) and
                         (not coordination['requested'] or coordination['complete']) and
                         (not nested_order['requested'] or nested_order['complete']) and
                         (not ast_probe['requested'] or ast_probe['complete']) and
                         (not wrapper_rebase['requested'] or wrapper_rebase['complete']) and
                         (not input_relation['requested'] or input_relation['complete']) and
                         (not input_relation_frame['requested'] or input_relation_frame['complete']) and
                         (not frame_test['requested'] or frame_test['complete']) and
                         (not input_relation_shadow['requested'] or input_relation_shadow['complete']) and
                         (not generic_new['requested'] or generic_new['complete']) and
                         (not rebase_profile['requested'] or rebase_profile['complete']) and
                         (not r3_profile['requested'] or r3_profile['complete'] or
                          (ghost_scope_lane and ghost_scope['complete'])) and
                         (not r3_lane or r3_requested) and
                         (not r3_nested['requested'] or r3_nested['complete']) and
                         (not r3_nested_lane or r3_nested['requested']) and
                         (not ghost_scope['requested'] or ghost_scope['complete']) and
                         (not ghost_scope_lane or ghost_scope_requested) and
                         (not postmark['requested'] or postmark['complete']) and
                         (not postmark_lane or postmark_requested) and
                         (not independent or independent_requested) and
                         (not recovery or recovery_requested) and
                         (not strict_cut_lane or strict_cut_requested) and
                         (not strict_false_posts_lane or strict_false_posts_requested) and
                         (not strict_reuse_lane or
                          (strict_false_posts_requested and
                           (strict_cut.get('historical_reuse') or {}).get('complete') is True)) and
                         (not input_relation_lane or input_relation_requested) and
                         (not input_relation_frame_lane or input_relation_frame_requested) and
                         (not frame_test_lane or frame_test_requested) and
                         (not input_relation_shadow_lane or input_relation_shadow_requested) and
                         (not shadow_generic_lane or shadow_generic_requested) and
                         (not generic_new_lane or generic_new_requested))
    proof_zero=proof_ran and stage.get('exit')==0
    # Source/MIR mutation negatives for component 17 and independently reached
    # component 20 A1 negatives are still pending. These cannot be inferred from
    # a positive full proof or an earlier owner-certificate rejection.
    controls={'owner_source_mir_isolated':owner['complete'],'a1_isolated':False}
    test_only_requested=(coordination['requested'] or nested_order['requested'] or
                         strict_cut['requested'] or
                         false_posts['requested'] or
                         ast_probe['requested'] or wrapper_rebase['requested'] or
                         input_relation['requested'] or input_relation_frame['requested'] or
                         frame_test['requested'] or
                         input_relation_shadow['requested'] or
                         generic_new['requested'] or
                         rebase_profile['requested'] or r3_profile['requested'] or
                         postmark['requested'] or r3_nested['requested'] or ghost_scope['requested'])
    verified=(diagnostic_complete and proof_zero and callees_before_outer and nested_visible and
              all(controls.values()) and not test_only_requested and not independent and
              not recovery and not strict_cut_lane and
              not strict_false_posts_lane and not strict_reuse_lane and
              not input_relation_lane and not input_relation_frame_lane and
              not frame_test_lane and
              not input_relation_shadow_lane and
              not shadow_generic_lane and
              not generic_new_lane and not r3_lane and not ghost_scope_lane and not postmark_lane)
    result={'lane':os.environ.get('LANE','o26-refresh'),
      'classification':('ACTUAL_PROOF_ACCEPTED' if verified else
         'INDEPENDENT_TESTS_DIAGNOSTIC_COMPLETE' if independent and diagnostic_complete else
         'RECOVERY_TESTS_DIAGNOSTIC_COMPLETE' if recovery and diagnostic_complete else
         'STRICT_CUT_CONTROLS_DISCOVERY_COMPLETE' if strict_cut_lane and diagnostic_complete else
         'STRICT_CUT_FALSE_POSTS_DISCOVERY_COMPLETE' if strict_false_posts_lane and diagnostic_complete else
         'STRICT_CUT_REUSED_MATRIX_FALSE_POSTS_DISCOVERY_COMPLETE' if strict_reuse_lane and diagnostic_complete else
         'WRAPPER_INPUT_RELATION_SOURCE_CAPTURE_COMPLETE' if input_relation_lane and diagnostic_complete else
         'THREADONLY_FRAME_SOURCE_CAPTURE_COMPLETE' if input_relation_frame_lane and diagnostic_complete else
         'R3_FRAME_TEST_DIAGNOSTIC_COMPLETE' if frame_test_lane and diagnostic_complete else
         'SHADOW_BINDING_SOURCE_CAPTURE_COMPLETE' if input_relation_shadow_lane and diagnostic_complete else
         'SHADOW_GENERIC_SORT4_DIAGNOSTICS_COMPLETE' if shadow_generic_lane and diagnostic_complete else
         'GENERIC_NEW_SOURCE_MIR_CAPTURE_COMPLETE' if generic_new_lane and diagnostic_complete else
         'GENERIC_SORT4_POSTMARK_DIAGNOSTICS_COMPLETE' if postmark_lane and diagnostic_complete else
         'R3_GHOST_SCOPE_TEST_DIAGNOSTIC_COMPLETE' if ghost_scope_lane and diagnostic_complete else
         'WRAPPER_R3_NESTED_DIAGNOSTICS_COMPLETE' if r3_nested_lane and diagnostic_complete else
         'WRAPPER_R3_PROFILE_DIAGNOSTIC_COMPLETE' if r3_lane and diagnostic_complete else
         'WRAPPER_REBASE_PROFILE_DIAGNOSTIC_COMPLETE' if rebase_profile['requested'] and diagnostic_complete else
         'REFRESH_DIAGNOSTIC_COMPLETE' if diagnostic_complete else 'INCONCLUSIVE'),
      'diagnostic_complete':diagnostic_complete,'verification_accepted':verified,
              'accepted':verified,'actual_helper_proved':proof_zero and callees_before_outer and nested_visible and not r3_nested_lane and not ghost_scope_lane and not input_relation_frame_lane and not frame_test_lane,
      'actual_safe_forget_linked':False if input_relation_frame_lane or frame_test_lane else None,
      'generic_constructor_helper_proved':False,
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
      'wrapper_input_relation_source_capture_diagnostic':input_relation,
      'threadonly_frame_source_capture_diagnostic':input_relation_frame,
      'r3_frame_test_diagnostic':frame_test,
      'wrapper_input_relation_shadow_source_capture_diagnostic':input_relation_shadow,
      'generic_new_source_mir_capture_diagnostic':generic_new,
      'wrapper_rebase_profile_diagnostic':rebase_profile,
      'wrapper_r3_profile_diagnostic':r3_profile,
      'r3_nested_order_test_diagnostic':r3_nested,
      'r3_ghost_scope_test_diagnostic':ghost_scope,
      'r3_ghost_scope_test_scope_complete':ghost_scope_requested if ghost_scope_lane else False,
      'sort4_postmark_print_diagnostic':postmark,
      'generic_sort4_postmark_scope_complete':postmark_requested if postmark_lane else False,
      'wrapper_r3_scope_complete':r3_requested if r3_lane else False,
      'independent_test_scope_complete':independent_requested if independent else False,
      'recovery_test_scope_complete':recovery_requested if recovery else False,
      'input_relation_source_scope_complete':input_relation_requested if input_relation_lane else False,
      'threadonly_frame_source_scope_complete':input_relation_frame_requested if input_relation_frame_lane else False,
      'r3_frame_test_scope_complete':frame_test_requested if frame_test_lane else False,
      'input_relation_shadow_source_scope_complete':input_relation_shadow_requested if input_relation_shadow_lane else False,
      'shadow_generic_sort4_scope_complete':shadow_generic_requested if shadow_generic_lane else False,
      'shadow_generic_sort4_three_independent_results':{
          'shadow_source_capture_complete':input_relation_shadow['complete'],
          'generic_constructor_capture_complete':generic_new['complete'],
          'sort4_postmark_diagnostic_complete':postmark['complete'],
          'accepted':False} if shadow_generic_lane else None,
      'generic_new_source_scope_complete':generic_new_requested if generic_new_lane else False,
      'strict_cut_controls_scope_complete':strict_cut_requested if strict_cut_lane else False,
      'strict_cut_false_posts_scope_complete':strict_false_posts_requested if strict_false_posts_lane else False,
      'strict_cut_reuse_scope_complete':(
          strict_false_posts_requested and
          (strict_cut.get('historical_reuse') or {}).get('complete') is True)
          if strict_reuse_lane else False,
      'strict_cut_controls_diagnostic':strict_cut,
      'strict_cut_false_posts_diagnostic':false_posts,
      'cut_relocation_test_diagnostic':cut,'runner_exit':a.runner_exit,
      'failed_stage':a.failed_stage,'evidence_root':'allprooflogs'}
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:result[k] for k in ('classification','diagnostic_complete','verification_accepted')}),flush=True)
if __name__=='__main__':main()
