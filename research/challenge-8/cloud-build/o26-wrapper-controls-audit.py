#!/usr/bin/env python3
"""Compound R2 profile and component-19 Cloud diagnostic."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

FATAL='Fatal error: exception Failure("SORT4-ACTUAL-FORGET-OWN: certificate mismatch: forget argument plain Move")'
ERROR=re.compile(r'^.+\(\d+,[^)]*\): error: ',re.MULTILINE)

def read(path):
    try:return json.loads(Path(path).read_text())
    except (OSError,ValueError):return None

def code(path):
    try:return int(Path(path).read_text().strip())
    except (OSError,ValueError):return None

def digest(path):
    try:return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    except OSError:return None

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('evidence','base','output'):
        p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args()
    ev=a.evidence
    base=read(a.base) or {}
    profile=ev/'cases/wrapper-profile'
    comp=profile/'comp19-isolated-test'
    result=read(comp/'test-result.json') or {}
    record=read(comp/'test-case/mutation-record.json') or {}
    identity=read(comp/'test-case/mutation-profile.json') or {}
    source=read(profile/'profile-manifest.json') or {}
    source_sha=(source.get('source') or {}).get('verified_sha256')
    original_sha=(source.get('source') or {}).get('original_sha256')
    stage=result.get('proof_stage') or {}
    log_path=comp/'test-case/test-forget-refusal.log'
    log=log_path.read_text(errors='replace') if log_path.is_file() else ''
    fatals=[x for x in log.splitlines() if x.startswith('Fatal error:')]
    provider=read(comp/'provider.json') or {}
    base_profile=base.get('wrapper_rebase_profile_diagnostic') or {}
    base_ok=(base.get('lane')=='o26-wrapper-controls' and
             base.get('diagnostic_complete') is True and
             base.get('verification_accepted') is False and
             base.get('runner_exit')==0 and
             base_profile.get('requested') is True and
             base_profile.get('complete') is True and
             base_profile.get('verification_accepted') is False and
             base_profile.get('same_version_callees_before_outer') is True and
             base_profile.get('owner17_controls_complete') is True and
             base_profile.get('a1_move_copy_negative_complete') is True and
             source.get('classification')==
               'EXPERIMENTAL_O26_WRAPPER_REBASE_COMPONENT23_R2_NOT_ACCEPTED' and
             all((base.get(key) or {}).get('requested') is False for key in
                 ('nested_proof_order_test_diagnostic',
                  'coordination_regression_diagnostic',
                  'wrapper_rebase_source_capture_diagnostic',
                  'actual_sort4_capture_diagnostic',
                  'cut_relocation_test_diagnostic',
                  'sort4_ast_probe_diagnostic')))
    stage_ok=(stage.get('status')=='RAN' and stage.get('exit')==2 and
              stage.get('source_unchanged') is True and
              stage.get('source_before')==stage.get('source_after') and
              stage.get('source_before',{}).get('verified/lib.rs')==source_sha and
              stage.get('source_before',{}).get('original/lib.rs')==original_sha and
              stage.get('intrinsic_gate_active') is True and
              stage.get('pointer_drop_gate_active') is True and
              fatals==[FATAL] and ERROR.search(log) is None and
              'SORT4-ACTUAL-OWNER-NINE:' in log and
              'SORT4-A1-NINE:' not in log and
              "Verifying function '" not in log)
    mutation_ok=(record.get('matched') is True and
                 record.get('mutation')=='forget_move_to_copy' and
                 record.get('selected_source_sha256')==source_sha and
                 all(record.get(k)==0 for k in
                     ('exporter_exit','decode_exit','encode_exit')) and
                 record.get('canonical_sha256')==digest(comp/'test-case/canonical-mir.bin') and
                 record.get('mutated_sha256')==digest(comp/'test-case/mutated-mir.bin') and
                 record.get('canonical_sha256')!=record.get('mutated_sha256') and
                 identity.get('wrapper_sha256')==digest(comp/'test-case/mir-exporter-wrapper.py')==
                     digest(comp/'test-case/mutation-profile/bin/vf-rust-mir-exporter') and
                 identity.get('base_console_sha256')==identity.get('shadow_console_sha256'))
    case_ok=(source_sha==digest(comp/'test-case/verified/lib.rs') and
             original_sha==digest(comp/'test-case/original/lib.rs'))
    exit_ok=(code(profile/'comp19-helper-exit-code.txt')==0 and
             code(profile/'comp19-isolated-test-exit-code.txt')==0)
    complete=(base_ok and stage_ok and mutation_ok and case_ok and exit_ok and
              provider.get('provider')=='cloud-build' and
              result.get('classification')=='REBASE_COMP19_MOVE_COPY_NEGATIVE' and
              result.get('diagnostic_complete') is True and
              result.get('verification_accepted') is False and
              result.get('intended_component19_refusal') is True and
              result.get('owner_hash_only_test') is True and
              result.get('production_unchanged') is True)
    report={'lane':'o26-wrapper-controls',
            'classification':'WRAPPER_CONTROLS_DIAGNOSTIC_COMPLETE' if complete else 'INCONCLUSIVE',
            'diagnostic_complete':complete,'verification_accepted':False,
            'accepted':False,'actual_helper_proved':False,
            'base_profile_diagnostic_complete':base_ok,
            'component19_intended_negative':stage_ok and mutation_ok and case_ok,
            'component19_helper_exit':code(profile/'comp19-helper-exit-code.txt'),
            'component19_stage_exit':stage.get('exit'),
            'component19_production_unchanged':result.get('production_unchanged'),
            'positive_full_proof_exit':base_profile.get('positive_full_proof_exit'),
            'nested_drop_proof_header_visible':base_profile.get('nested_drop_proof_header_visible'),
            'full_normal_unwind_posts_accepted':False,
            'base_audit_file':a.base.name,
            'evidence_root':'allprooflogs'}
    a.output.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:report[k] for k in
          ('classification','diagnostic_complete','verification_accepted')}),flush=True)

if __name__=='__main__':main()
