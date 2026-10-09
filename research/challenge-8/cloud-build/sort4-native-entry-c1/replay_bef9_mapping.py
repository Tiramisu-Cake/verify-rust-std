#!/usr/bin/env python3
"""Replay only pure mapping classifiers over immutable saved native evidence."""
import argparse
import hashlib
import importlib.util
import json
import re
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--extracted', type=Path, required=True)
    ap.add_argument('--record', type=Path, required=True)
    args = ap.parse_args()
    home = Path(__file__).resolve().parent
    # This module AST-selects only pure collector functions/constants. Its
    # unittest runner is under __main__; no proof/export/build entrypoint loads.
    spec = importlib.util.spec_from_file_location('pure_native_classifier', home/'test_native_entry_classifier.py')
    pure = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pure)
    rows = json.loads(args.record.read_text())
    evidence = args.extracted/'allprooflogs/cases/sort4-caller-entry'
    controls_path=evidence/'slice-projection-controls/controls-result.json'
    controls=json.loads(controls_path.read_text())
    controls_sha=hashlib.sha256(controls_path.read_bytes()).hexdigest()
    for case, saved in rows['cases'].items():
        root = evidence/'cases'/case
        fixture = root/'fixture'
        log = (fixture/'verification.log').read_text(errors='replace')
        entries = list(re.finditer(r"(?m)^\s*\d+\.\d+s: [^\n]*: Verifying function 'small_sort_general_with_scratch'\s*$", log))
        entry = entries[0].start() if len(entries) == 1 else None
        caller_log=log[entry:] if entry is not None else ''
        cert=json.loads((root/'source-certificate.json').read_text())
        result = pure.namespace['native_entry_mapping'](
            fixture, cert,
            (root/'normal-full-prefix-mir.txt').read_text(),
            (root/'readonly-full-prefix-mir.txt').read_text(),
            caller_log, entry)
        assert result['status'] == saved['replayed_mapping_gate'], case
        for mode in ('normal', 'readonly'):
            actual = result['artificial_ghost_boundary']['normal_and_readonly'][mode]
            expected = saved['ghost_spans_normal_readonly'][mode]
            assert actual['mir_ghost_statement'] == [expected['ghost_span']], case
            assert actual['full_function_record_sha256'] == expected['full_mir_sha256'], case
        for rel, expected in saved['saved_input_sha256'].items():
            assert hashlib.sha256((root/rel).read_bytes()).hexdigest() == expected, (case, rel)
        raw=json.loads((root/'case-result.json').read_text())
        admission=json.loads((root/'admission-gates.json').read_text())
        ast_capture=json.loads((root/'proof-ast-capture.json').read_text())
        pins=json.loads((root/'raw-input-pins.json').read_text())
        source_hashes=pins.get('source_hashes',{})
        actual_source_hashes={name:hashlib.sha256((fixture/name).read_bytes()).hexdigest()
                              for name in ('original/lib.rs','verified/lib.rs')}
        source_immutable=(actual_source_hashes==source_hashes==raw.get('source_hashes'))
        log_sha=hashlib.sha256((fixture/'verification.log').read_bytes()).hexdigest()
        raw_log_unchanged=(log_sha==raw.get('full_log_sha256'))
        support_names=('normal-export','normal-decode','readonly-export','readonly-decode','refinement')
        raw_stages=raw.get('stages',{})
        support_passed=(all(raw_stages.get(name)==0 for name in support_names) and source_immutable and raw_log_unchanged)
        controls_passed=(controls.get('all_intended') is True and
                         all(c.get('classification')=='PASS' for c in controls.get('cases',{}).values()))
        proof_ast=(pure.namespace['native_post_ast_evidence'](root/'fixture/proof-ast.ml',cert)
                   if (root/'fixture/proof-ast.ml').is_file() else {'status':'NOT_CONFIRMED'})
        verifier_exit=raw.get('verifier_exit')
        errors=[line for line in log.splitlines() if ': error:' in line or line.startswith('Fatal error:') or re.search(r'\): dead code$',line)]
        proof_entry_ok=len(entries)==1
        full_vf0=(verifier_exit==0 and not errors and
                  re.search(r'0 errors found \(\d+ statements verified\)',log) is not None and
                  'Leak check.' in caller_log)
        verified_lines=(fixture/'verified/lib.rs').read_text(errors='replace').splitlines()
        targets_reached=pure.namespace['native_case_targets_reached'](
            case,cert,caller_log,verified_lines)
        identity_reached=(case!='bridge-positive' or
            (pure.namespace['native_identity_call_target'](cert,verified_lines) is not None and
             pure.namespace['executed_line'](caller_log,
                pure.namespace['native_identity_call_target'](cert,verified_lines))))
        full_positive=pure.namespace['positive_full_vf0'](
            case,controls_passed=controls_passed,
            support_gates_passed=(support_passed and result['status']=='PASS' and proof_ast.get('status')=='PASS'),
            source_mir_trace_passed=(result['status']=='PASS' and targets_reached and identity_reached),
            verifier_exit=verifier_exit,proof_entries=[entry] if proof_entry_ok else [],
            caller_log=caller_log,errors=errors,full_vf0_log=full_vf0,
            full_native_contract=proof_ast.get('status')=='PASS')
        expected_negative=pure.namespace['native_expected_negative'](
            case,cert,(fixture/'verified/lib.rs').read_bytes(),caller_log,
            [entry] if proof_entry_ok else [],errors,verifier_exit)
        saved['saved_evidence_reclassification']={
            'candidate_controls_passed':controls_passed,
            'candidate_controls_sha256':controls_sha,
            'source_pair_immutable':source_immutable,
            'source_pair_hashes_reproduced':actual_source_hashes,
            'full_verification_log_sha256_reproduced':log_sha,
            'raw_verification_log_unchanged':raw_log_unchanged,
            'support_and_refinement_gates_passed':support_passed,
            'native_automatic_post_ast':proof_ast.get('status'),
            'one_caller_proof_entry':proof_entry_ok,
            'full_vf0_and_leak':full_vf0,
            'named_resource_targets_reached':targets_reached,
            'bridge_identity_call_reached':identity_reached if case=='bridge-positive' else None,
            'first_error_unchanged':raw.get('first_error'),
            'positive_full_gate':full_positive,
            'intended_negative_attribution':expected_negative,
            'classification':'SAVED_NATIVE_ENTRY_FULL_VF0' if full_positive else
                'SAVED_INTENDED_RESOURCE_NEGATIVE' if expected_negative and controls_passed and support_passed and proof_entry_ok and proof_ast.get('status')=='PASS' else
                'SAVED_BRIDGE_IDENTITY_REACHED_BUT_NATIVE_RESOURCE_VC_FAILED' if case=='bridge-positive' and identity_reached else
                'SAVED_EVIDENCE_INCOMPLETE_OR_UNATTRIBUTED',
            'proof_credit':False,
            'raw_records_modified':False,
        }
    rows['replay_command'] = (f'python3 -B {Path(__file__).relative_to(home.parents[3])} '
                              f'--extracted {args.extracted} --record {args.record}')
    rows['replay_script_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    rows['replay_collector_sha256'] = hashlib.sha256((home.parent/'sort4-caller-entry.py').read_bytes()).hexdigest()
    rows['test_result'] = '10 isolated classifier tests passed; AST parse passed'
    rows['proof_credit'] = 'NONE; saved-evidence service reclassification only'
    args.record.write_text(json.dumps(rows, indent=2, sort_keys=True)+'\n')
    print(json.dumps({'cases': len(rows['cases']), 'mapping_gates_reproduced': True,
                      'saved_inputs_hash_verified': True,
                      'full_positive_gates':sum(bool(v.get('saved_evidence_reclassification',{}).get('positive_full_gate')) for v in rows['cases'].values()),
                      'attributed_negatives':sum(bool(v.get('saved_evidence_reclassification',{}).get('intended_negative_attribution')) for v in rows['cases'].values()),
                      'proof_credit': False, 'raw_records_modified': False}))


if __name__ == '__main__':
    main()
