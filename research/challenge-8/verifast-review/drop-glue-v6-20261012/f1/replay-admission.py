#!/usr/bin/env python3
"""Rerun file-reading AST/source admission and scoped negative log gates.
Saved MIR/selected-body/canonical admissions are reused, never executed anew.
No preparation, compiler, exporter, refiner or verifier invocation.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
from types import SimpleNamespace


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--runner', required=True, type=Path)
    parser.add_argument('--parser', required=True, type=Path)
    parser.add_argument('--evidence', required=True, type=Path)
    parser.add_argument('--build-record', required=True, type=Path)
    a = parser.parse_args()
    runner = load('f1_replay_runner', a.runner)
    ast = load('f1_replay_ast', a.parser)
    here = Path(__file__).resolve().parent
    previous = json.loads((here.parent / 'NEGATIVE-GATE-REPLAY.json').read_text())
    extraction = json.loads((a.evidence / 'extraction.json').read_text())
    assert set(extraction['cases']) == set(previous['cases']) == set(runner.CASES)
    # These exact constants are only read by _source_gate. No prepare module or
    # extractor is imported or called; source bytes remain untouched.
    source_constants = SimpleNamespace(
        READ=b'        let tmp = ManuallyDrop::new(tail.read());\n',
        GUARD=b'        let mut gap_guard = CopyOnDrop { src: &*tmp, dst: tail, len: 1 };\n')
    result = {'kind': 'SAVED_ADMISSION_AND_SCOPED_NEGATIVE_REPLAY_NO_FRESH_PROOF',
        'build_id': '34485da0-911b-4c1e-9d8d-32922f154f82',
        'proof_infra_sha': 'f8c7cb7ed80fed845c0ad11155835da4a5803340',
        'tool_sha': 'e0a94e3eab17fcd69f7fad785f7a0fb316d27258',
        'profile_sha256': 'e97cce6325ad7f2874fccc963d43d1e9e1c0c795f813cc1bddc46a1ce9fa0081',
        'old_auditor_commit': '420188dd1732d53f3f515690ed2ff6f53a9026ab',
        'old_auditor_sha256': previous['auditor_source_sha256'],
        'auditor_source_sha256': sha(a.runner), 'parser_sha256': sha(a.parser),
        'fresh_gates': ['_source_gate', '_caller_ast_evidence', '_body_glue_ast_evidence',
            'refinement stage/marker/error-absence receipt', '_generated_glue_proof_gate',
            '_body_glue_negative_gate', 'source hashes and all four stage exit/immutability receipts'],
        'reused_gates': ['raw MIR identity/CFG admission', 'selected Drop body/effect AST admission',
            'canonical safety_proof compatibility', 'actual compiler/refiner/verifier results',
            'caller return/leak and natural scope execution markers from hash-bound raw classification'],
        'cases': {}}
    for name, row in extraction['cases'].items():
        case = a.evidence / 'cases' / name
        old = previous['cases'][name]
        for f, expected in old['sha256'].items():
            assert sha(case / f) == expected, (name, f)
        raw = json.loads((case / 'classification.json').read_text())
        for f, expected in [('original/lib.rs', row['original_sha256']),
                            ('verified/lib.rs', row['verified_sha256'])]:
            assert sha(case / f) == expected, (name, f)
        stages = raw['stages']
        for stage in ('exporter', 'decode', 'refinement', 'verifast'):
            receipt = json.loads((case / (stage + '-stage.json')).read_text())
            assert int((case / (stage + '-exit-code.txt')).read_text()) == receipt['exit_code'] == stages[stage]
            assert receipt['source_unchanged'] and receipt['source_before'] == receipt['source_after']
            assert receipt['source_before']['original/lib.rs'] == row['original_sha256']
            assert receipt['source_before']['verified/lib.rs'] == row['verified_sha256']
            assert receipt['source_before']['small_sort_source'] == '85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1'
        assert raw['source_unchanged_at_every_stage']
        mir = raw['mir_gate']
        assert mir['admitted'] and raw['drop_body_effect_ast_gate']['admitted']
        selected = mir['selected_normal_drop']['selected_path']
        source = runner._source_gate(case, row, source_constants)
        caller_ast = runner._caller_ast_evidence(case, ast)
        glue_ast = runner._body_glue_ast_evidence(case, ast, selected, mir)
        assert source['admitted'] and caller_ast['admitted'] and glue_ast['admitted'], name
        caller_ast['body_glue_evidence'] = glue_ast
        refinement = (case / 'refinement.out').read_text()
        assert stages['refinement'] == 0 and 'No refinement errors found' in refinement and 'Generated DropGlue:' not in refinement
        assert all(stages[s] == 0 for s in ('exporter', 'decode', 'refinement'))
        log = (case / 'verifast.log').read_text()
        errors = [line for line in log.splitlines() if re.search(r'\berror:', line, re.I)]
        dead = [line for line in log.splitlines() if re.search('dead code', line, re.I)]
        glue_proof = runner._generated_glue_proof_gate(log, glue_ast)
        assert glue_proof['admitted'], name
        negative = runner._body_glue_negative_gate(name, case, row, log, errors, dead,
            caller_ast, glue_proof, True, raw['natural_scope_end_executed'],
            raw['caller_return'], raw['caller_leak_check'])
        if name == 'positive':
            assert stages['verifast'] == 0 and not errors and not dead and '0 errors found' in log
            assert raw['body_copy_executed'] and raw['body_return_executed'] and raw['leak_check']
            assert raw['caller_return'] and raw['caller_leak_check']
            verdict = 'NATURAL_DROP_CALLER_AND_EFFECT_PASS_FRAGMENT_ONLY'
        else:
            assert stages['verifast'] == 1 and negative['admitted'], (name, negative)
            verdict = ('CALLER_READY_ENTRY_EXPECTED_REJECTION' if name == 'caller_ready_entry_false'
                       else 'EXPECTED_REJECTION')
        assert verdict == old['replay_verdict']
        result['cases'][name] = {'raw_verdict': raw['classification'],
            'old_scoped_replay_verdict': old['replay_verdict'], 'new_scoped_replay_verdict': verdict,
            'stages': stages, 'source_gate': source, 'caller_ast_evidence': caller_ast,
            'body_glue_evidence': glue_ast, 'generated_glue_proof_gate': glue_proof,
            'negative_gate': negative, 'unchanged_raw_sha256': old['sha256']}
    # Check immutable archived status inputs rather than hard-code FAILURE.
    prior_inputs = json.loads((here.parent / 'INPUTS.json').read_text())
    summary_path = a.evidence.parents[2] / 'summary.json'
    assert sha(summary_path) == prior_inputs['raw_metadata_sha256']['summary.json']
    summary = json.loads(summary_path.read_text())
    build_record = json.loads(a.build_record.read_text())
    assert summary['build_id'] == build_record['id'] == result['build_id']
    assert summary['run_exit_code'] == 1 and summary['failure_class'] == 'run-failed'
    assert summary['verification_accepted'] is False and build_record['status'] == 'FAILURE'
    result['cloud_failure_preserved'] = {
        'saved_status': build_record['status'], 'run_exit_code': summary['run_exit_code'],
        'verification_accepted': summary['verification_accepted'],
        'summary_sha256': sha(summary_path), 'build_record_sha256': sha(a.build_record)}
    result['six_raw_inconclusive_preserved'] = all(
        c['raw_verdict'] == 'INCONCLUSIVE' for n, c in result['cases'].items() if n != 'positive')
    assert result['six_raw_inconclusive_preserved']
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
