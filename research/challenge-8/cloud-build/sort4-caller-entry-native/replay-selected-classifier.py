#!/usr/bin/env python3
"""Isolated synthetic classifier controls; no compiler/verifier or live evidence."""
import copy
import hashlib
import importlib.util
import json
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('selected_classifier', HERE / 'selected-proof.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
results = {}
with tempfile.TemporaryDirectory(prefix='selected-classifier-replay-') as tmp:
    root = Path(tmp)
    fixture = root / 'fixture'
    (fixture / 'verified').mkdir(parents=True)
    for case, source, error in (
        ('selected-branch-false-bound-31', '//@ assert len <= 31;\n',
         'verified/lib.rs(1,1-3): error: Cannot prove assertion.'),
        ('selected-branch-missing-source-array', 'T::small_sort(v, scratch, is_less);\n',
         'verified/lib.rs(1,1-3): error: No matching heap chunks: array<T>(v, _, _)')):
        (fixture / 'verified/lib.rs').write_text(source)
        baseline = {'support': {'paired_support_passed': True}, 'source_pair_immutable': True,
                    'proof_ast_sha256': 'synthetic-hash-classifier-only',
                    'stages': {'proof-ast-diagnostic': 1, 'verification': 1},
                    'first_causal_stage': 'verification', 'first_error': error}
        (root / 'proof-ast-diagnostic.log').write_text(error + '\n')
        assert module.classify_selected(case, baseline, fixture)['gate_passed']
        rows = {'matching-first-error': True}
        changes = {
            'diagnostic-exit2': lambda r: r['stages'].update({'proof-ast-diagnostic': 2}),
            'diagnostic-exit0': lambda r: r['stages'].update({'proof-ast-diagnostic': 0}),
            'missing-ast-hash': lambda r: r.update(proof_ast_sha256=None),
            'wrong-causal-stage': lambda r: r.update(first_causal_stage='refinement'),
            'wrong-location': lambda r: r.update(first_error=error.replace('(1,', '(2,')),
            'wrong-proof-error': lambda r: r.update(first_error='verified/lib.rs(1,1-3): error: unrelated'),
            'no-source-pair': lambda r: r.update(source_pair_immutable=False),
            'support-refused': lambda r: r['support'].update(paired_support_passed=False),
            'verifier-exit2': lambda r: r['stages'].update(verification=2),
        }
        for name, mutate in changes.items():
            row = copy.deepcopy(baseline); mutate(row)
            rows[name] = not module.classify_selected(case, row, fixture)['gate_passed']
            assert rows[name], name
        for name, text in [('different-first-diagnostic', 'verified/lib.rs(1,1-3): error: earlier\n' + error),
                           ('missing-diagnostic-error', '')]:
            (root / 'proof-ast-diagnostic.log').write_text(text)
            rows[name] = not module.classify_selected(case, baseline, fixture)['gate_passed']
            assert rows[name], name
        results[case] = rows
report = {'auditor_sha256': hashlib.sha256((HERE/'selected-proof.py').read_bytes()).hexdigest(),
          'synthetic_classifier_controls': results, 'mandatory_full_post_ast_audit_unchanged': True,
          'compiler_or_verifier_executed': False, 'proof_credit': False}
(HERE/'REPLAY-SELECTED-CLASSIFIER.json').write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')
print(json.dumps({'all_controls_passed': True, 'negative_controls_per_case': 11, 'proof_credit': False}))
