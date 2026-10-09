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
    if os.environ.get('LANE') in ('o26-strict-cut-controls','o26-sort4-scope-tests'):
        matched=matched and result.get('classification')=='FIXTURE_FULL_VF0_DIAGNOSTIC_ONLY'
    return {'requested':True,'classification':result.get('classification','INCONCLUSIVE'),
            'diagnostic_match':matched,'helper_exit':code,'test_only':True,'accepted':False}

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
                  (row.get('first_error') is None if key[1] and key[0] in positives else
                   isinstance(row.get('first_error'),str) and
                   bool(row.get('first_error_source_location')))
                  for key,row in keyed.items()) and
              isinstance(open_gates,list) and len(open_gates)>=8 and
              all(isinstance(gate,str) and gate for gate in open_gates))
    return {'requested':True,'complete':complete,
            'classification':result.get('classification','INCONCLUSIVE'),
            'helper_exit':code,'test_only':True,'accepted':False,
            'matrix_cases':len(rows),'distinct_f_bound_full_vf0':
            pre.get('distinct_f_bound_full_vf0') is True,
            'normal_unwind_negative_gates_open':
            any('false normal-post and false unwind-post' in gate for gate in open_gates),
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
    rebase_profile=wrapper_profile(ev)
    independent=os.environ.get('LANE')=='o26-independent-tests'
    recovery=os.environ.get('LANE')=='o26-recovery-tests'
    strict_cut_lane=os.environ.get('LANE')=='o26-strict-cut-controls'
    input_relation_lane=os.environ.get('LANE')=='o26-input-relation-capture'
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
    input_relation_requested=(input_relation['requested'] and
                              not cut['requested'] and not strict_cut['requested'] and
                              not false_posts['requested'] and
                              not ast_probe['requested'] and
                              not owner['requested'] and not sort4['requested'] and
                              not a1['requested'] and not coordination['requested'] and
                              not nested_order['requested'] and not wrapper_rebase['requested'] and
                              not rebase_profile['requested'])
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
                         (not rebase_profile['requested'] or rebase_profile['complete']) and
                         (not independent or independent_requested) and
                         (not recovery or recovery_requested) and
                         (not strict_cut_lane or strict_cut_requested) and
                         (not input_relation_lane or input_relation_requested))
    proof_zero=proof_ran and stage.get('exit')==0
    # Source/MIR mutation negatives for component 17 and independently reached
    # component 20 A1 negatives are still pending. These cannot be inferred from
    # a positive full proof or an earlier owner-certificate rejection.
    controls={'owner_source_mir_isolated':owner['complete'],'a1_isolated':False}
    test_only_requested=(coordination['requested'] or nested_order['requested'] or
                         strict_cut['requested'] or
                         false_posts['requested'] or
                         ast_probe['requested'] or wrapper_rebase['requested'] or
                         input_relation['requested'] or rebase_profile['requested'])
    verified=(diagnostic_complete and proof_zero and callees_before_outer and nested_visible and
              all(controls.values()) and not test_only_requested and not independent and
              not recovery and not strict_cut_lane and not input_relation_lane)
    result={'lane':os.environ.get('LANE','o26-refresh'),
      'classification':('ACTUAL_PROOF_ACCEPTED' if verified else
         'INDEPENDENT_TESTS_DIAGNOSTIC_COMPLETE' if independent and diagnostic_complete else
         'RECOVERY_TESTS_DIAGNOSTIC_COMPLETE' if recovery and diagnostic_complete else
         'STRICT_CUT_CONTROLS_DISCOVERY_COMPLETE' if strict_cut_lane and diagnostic_complete else
         'WRAPPER_INPUT_RELATION_SOURCE_CAPTURE_COMPLETE' if input_relation_lane and diagnostic_complete else
         'WRAPPER_REBASE_PROFILE_DIAGNOSTIC_COMPLETE' if rebase_profile['requested'] and diagnostic_complete else
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
      'wrapper_input_relation_source_capture_diagnostic':input_relation,
      'wrapper_rebase_profile_diagnostic':rebase_profile,
      'independent_test_scope_complete':independent_requested if independent else False,
      'recovery_test_scope_complete':recovery_requested if recovery else False,
      'input_relation_source_scope_complete':input_relation_requested if input_relation_lane else False,
      'strict_cut_controls_scope_complete':strict_cut_requested if strict_cut_lane else False,
      'strict_cut_controls_diagnostic':strict_cut,
      'strict_cut_false_posts_diagnostic':false_posts,
      'cut_relocation_test_diagnostic':cut,'runner_exit':a.runner_exit,
      'failed_stage':a.failed_stage,'evidence_root':'allprooflogs'}
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:result[k] for k in ('classification','diagnostic_complete','verification_accepted')}),flush=True)
if __name__=='__main__':main()
