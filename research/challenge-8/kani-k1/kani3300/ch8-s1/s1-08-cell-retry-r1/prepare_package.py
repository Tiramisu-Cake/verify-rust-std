#!/usr/bin/env python3
"""Materialize the frozen review packet, offline; no source publication/dispatch."""
from pathlib import Path
import json
import verify_package as v

H=v.HERE;C=v.CONTROL

def main():
    candidate=v.textgit(C,'rev-parse','HEAD');request=json.loads((v.H/'CI-REQUEST.json').read_bytes())
    ids={'schema':'ch8-s1-08-cell-retry-r1-identities-v1','status':'READY_FOR_W14_REVIEW',
      'task_commit':v.TASK,'entry_g0':v.TASK,'previous_package_g0':v.PREVIOUS_G0,'review_g0':v.REVIEW,
      'workspace_g0_before_packet':v.textgit(H,'rev-parse','HEAD'),
      'source':{'worktree':str(v.SOURCE),'sha':v.STD,'tree':request['std_tree'],
                'changed_file_sha256':request['changed_file_sha256'],'publication':'ALREADY_PUBLISHED_UNCHANGED_NO_REPUBLISH'},
      'control':{'worktree':str(C),'sha':candidate,'tree':v.textgit(C,'rev-parse','HEAD^{tree}'),
        'parent':v.PARENT,'review_base':v.BASE,'repair_base':v.PREVIOUS,'repair_base_tree':v.textgit(C,'rev-parse',v.PREVIOUS+'^{tree}'),'review_base_tree':v.textgit(C,'rev-parse',v.BASE+'^{tree}'),
        'embedded_request_sha256':v.sha((v.H/'CI-REQUEST.json').read_bytes()),
        'role_map_sha256':v.sha((v.H/'ROLE-MAP.json').read_bytes()),'dispatch_authorized':False,'published':False},
      'tool':{'sha':v.TOOL,'tree':request['tool_tree'],'change':'NONE_STOCK'},
      'review':'PENDING_W14','runtime':'NOT_RUN','reservation':'NOT_RESERVED','current_charge':'8/14',
      'conditional_future_charge':'item2 9/14 only after separately authorized accepted run',
      'proof_credit':'NONE'}
    v.write(H/'IDENTITIES.json',ids)
    embedded=(v.H/'CI-REQUEST.json').read_bytes();(H/'EMBEDDED-CI-REQUEST.json').write_bytes(embedded)
    v.write(H/'CI-REQUEST.json',{**request,'control_candidate':ids['control']})
    (H/'ROLE-MAP.json').write_bytes((v.H/'ROLE-MAP.json').read_bytes())
    patches=[]
    for name,base in [('REVIEW-DELTA.patch',v.BASE),('REPAIR-DELTA.patch',v.PREVIOUS),('CONTROL-CANDIDATE.patch',v.PARENT)]:
        data=v.git(C,'diff','--binary',base,candidate);(H/name).write_bytes(data)
        patches.append({'file':name,'base':base,'candidate':candidate,'sha256':v.sha(data)})
    v.write(H/'PATCHES.json',{'patches':patches,'source_patch':'NONE; existing published99e immutable'})
    v.write(H/'PAYLOADS.json',{'control':candidate,'tree':ids['control']['tree'],
          'embedded_request_sha256':ids['control']['embedded_request_sha256'],
          'payload_sha256':request['ci_payload_sha256'],'changed_paths_from_tool':request['ci_changed_paths'],
          'changed_paths_from7c':v.WHITELIST})
    v.write(H/'ENVELOPE.json',{'setup_seconds':1800,'compile_child_seconds':900,'root_seconds':[1200,1200],
      'group_child_seconds':3300,'group_cleanup_seconds':10,'group_with_cleanup_seconds':3310,
      'phase_seconds':8100,'phase_slack_after_group_and_cleanup_seconds':4790,'job_seconds':10800,
      'job_reserve_seconds':900,'setup_plus_phase_plus_reserve_seconds':10800,
      'workflow_step_caps_minutes':{'build':15,'runner':135,'fallback':2,'upload':13},
      'setup_budget':'absolute30min; existing build wrapper uses min900s, remaining setup budget; overlapping step caps',
      'rss':'min12GiB, available-2GiB; unchanged; group peak is not per-root attribution',
      'phase_and_job_increase':'NONE_NEEDED','row_seconds600':'reference-only legacy default for33 nonselected rows',
      'cell_row_seconds':1200,'proof_time_reduced_for_window':False,
      'inherited_phase_deadline_guard':'unchanged; full3300 child+10 cleanup fits8100 phase from start'})
    v.write(H/'PREFLIGHT-COVERAGE.json',{'status':'PRESERVED_WITH_CELL_PROFILE_ADAPTATIONS',
      'tests':['test_cell_retry.py','test_s108.py','test_s108r1.py'],
      'reused':['test_runner.ExportTests','test_runner.ExecutionTests','test_runner.CompileTests','test_runner.NoListBindingTests',
        'test_runner.RequestTests source/flags checks','test_runner.GroupTests memory budget',
        'test_package.PackageTests control guards/build errors and both adapted cell fallback controls','test_s105.RichTests except full matrix fixture',
        'test_s107.FinalizationTests standalone pack/hash/monitor/snapshot checks','test_s107.LocationTests exact exceptions/mutations'],
      'adapted_full_matrix_cases':'exact cell pair run_rows/_run_group synthetic service; all other33 NOT_SELECTED; fallback only2',
      'preserved_cases':['success','error42','exception','timeout','TIMEOUT','partial','missing','null','wrong-type','NOT_RUN',
        'source/target/stage mismatch','post-source drift','snapshot error/missing/drift','native partial/null/wrong-type/missing/unmatched/duplicate/invalidUTF8',
        'metadata capture exception','wrong600','missing RESULTS','actual file:// shallow depth5 plus negative2'],
      'unchanged_runtime_checks':'original exit/exception; protected after-shutdown snapshot; cfg/source/inventory/timeout/mode gates; native and rich evidence retained',
      'broad_unchanged_proof_audits':'NOT_REPEATED; only2 original fallback methods adapted; original runtime unchanged'})
    print(json.dumps({'control':candidate,'tree':ids['control']['tree'],'packet':str(H)}))

if __name__=='__main__':main()
