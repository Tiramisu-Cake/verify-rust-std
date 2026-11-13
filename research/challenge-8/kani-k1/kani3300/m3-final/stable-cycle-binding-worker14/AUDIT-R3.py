#!/usr/bin/env python3
# Copyright Kani Contributors
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Revalidate supplied r3 capture and reviewed bindings offline; never invoke Kani or edit evidence."""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--clone', type=Path, default=Path('/root/kani-fix-3300-worker14'))
parser.add_argument('--artifacts', type=Path, default=Path(
    '/root/kani3300-h1-ci/m3r3-capture-r3/kani-uninit-part1-composition-kx3sg2st'))
parser.add_argument('--job-log', type=Path, default=Path('/root/kani3300-h1-ci/m3r3-capture-r3.log'))
args = parser.parse_args()
suite = args.clone / 'tests/json-handler/uninit-part1-composition'
sys.path.insert(0, str(suite))
spec = importlib.util.spec_from_file_location('capture_runner_audit', suite / 'run.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
manifest = json.loads((suite / 'roots.json').read_text())
cases = {case['name']: case for case in manifest['roots']}
expected = {'isolated-' + name: [name] for name in cases}
expected.update({order['id']: order['selectors'] for order in manifest['orders']})
source_hash = runner.sha256(args.clone / manifest['source'])
assert source_hash == manifest['source_sha256']
observations, reconstructed, rows = {}, {}, []
for receipt_path in sorted(args.artifacts.glob('*/receipt.json')):
    directory = receipt_path.parent
    receipt = json.loads(receipt_path.read_text())
    run_id = directory.name
    assert receipt['run_id'] == run_id
    assert receipt['selectors'] == expected[run_id]
    assert receipt['source_sha256'] == receipt['input_sha256_after'] == source_hash
    assert receipt['snapshot_errors'] == {} and receipt['timed_out'] is False
    expected_exit = int(any(cases[name]['expected_verdict'] == 'FAILURE'
                            for name in expected[run_id]))
    runner.validate_process_result(receipt['original_exit'], expected_exit)
    hashes = {'receipt.json': runner.sha256(receipt_path)}
    for filename, field in (('export.json', 'export_sha256'), ('regular.out', 'regular_sha256')):
        hashes[filename] = runner.sha256(directory / filename)
        assert hashes[filename] == receipt[field]
    observed = runner.observation(runner.CHECKER.load_export(directory / 'export.json'),
                                  (directory / 'regular.out').read_text(),
                                  expected[run_id], cases, receipt)
    reconstructed[run_id] = observed
    observations[run_id] = runner.compare_selection(observed, cases)
    rows.append({'run_id': run_id, 'files_sha256': hashes,
                 'original_exit': receipt['original_exit'], 'expected_exit': expected_exit,
                 'original_receipt_error': receipt['error'],
                 'revalidation': 'COMPLETE_INVENTORY_VALIDATED',
                 'roots': [{'name': name, 'verdict': root['verdict'],
                            'checks': len(root['checks']), 'covers': len(root['covers']),
                            'n_failed': root['n_failed'], 'failure_kind': root['failure_kind'],
                            'unsupported_count': len(root['unsupported_constructs'])}
                           for name, root in observations[run_id].items()]})

original = json.loads((args.artifacts / 'capture.json').read_text())
assert original['status'] == 'UNBOUND_CAPTURE'
assert original['binding_status'] == 'BINDING_PENDING'
assert original['mixed_root_oracle'] == 'MISMATCH'
assert set(observations) == set(expected), 'missing or extra invocations'
for name in cases:
    assert original['root_inventory_observations'][name] == reconstructed['isolated-' + name]
combined = {row['order']: row['observation'] for row in original['combined_inventory_observations']}
comparisons = []
for order in manifest['orders']:
    assert combined[order['id']] == reconstructed[order['id']]
    for name in order['selectors']:
        comparison = runner.compare_root(observations['isolated-' + name][name],
                                         observations[order['id']][name])
        comparisons.append({'order': order['id'], **comparison})
assert comparisons == original['mixed_root_comparisons']
assert len(comparisons) == 18
rejected = [row for row in comparisons if not row['accepted']]
assert [(r['root'], r['order']) for r in rejected] == [('cycle_root', 'all_A_then_B')]
reviewed = []
for name, case in cases.items():
    if name == 'cycle_root':
        assert case['binding'] == 'BINDING_PENDING'
        assert all(case[field] is None for field in ('expected_inventory', 'expected_failure_kind',
                   'expected_failures', 'expected_unsupported_inventory'))
        continue
    assert case['binding'] == 'REGRESSION_BOUND'
    runner.check_single(observations['isolated-' + name][name], {
        'binding': case['binding'], 'expected_verdict': case['expected_verdict'],
        'checks': case['expected_inventory'], 'failure_kind': case['expected_failure_kind'],
        'failed_properties': case['expected_failures'],
        'unsupported_constructs': case['expected_unsupported_inventory'],
        'covers': case.get('expected_covers', [])})
    assert all(row['accepted'] for row in comparisons if row['root'] == name)
    reviewed.append(name)
report = {
    'schema': 'kani3300-worker14-r3-binding-audit/v1',
    'source_clone': str(args.clone),
    'source_commit': subprocess.check_output(['git', '-C', str(args.clone), 'rev-parse', 'HEAD'],
                                            text=True).strip(),
    'capture_run': '43504302188', 'artifact_directory': str(args.artifacts),
    'capture_sha256': runner.sha256(args.artifacts / 'capture.json'),
    'job_log': str(args.job_log), 'job_log_sha256': runner.sha256(args.job_log),
    'source_sha256': source_hash,
    'manifest_sha256': runner.sha256(suite / 'roots.json'),
    'original_status': original['status'], 'original_oracle': original['mixed_root_oracle'],
    'revalidated_runs': rows,
    'comparison_counts': {'total': len(comparisons),
        'accepted': sum(row['accepted'] for row in comparisons),
        'exact': sum(row['exact_match'] for row in comparisons),
        'accepted_t1b': sum(row['accepted'] and not row['exact_match'] for row in comparisons)},
    'comparisons': [{'order': row['order'], 'root': row['root'],
                     'accepted': row['accepted'], 'exact_match': row['exact_match'],
                     'difference_fields': sorted(row['differences'])} for row in comparisons],
    'reviewed_roots': reviewed, 'pending_roots': ['cycle_root'],
    'order_credit': 'NOT_ESTABLISHED', 'proof_credit': 'NONE',
    'verifier_invocations': 0,
    'note': 'Offline validation of explicitly supplied local capture files only; '
            'no runtime validation of the new compiler diagnostic; no normalization of cycle text.'}
print(json.dumps(report, indent=2, sort_keys=True))
