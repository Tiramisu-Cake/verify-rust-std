#!/usr/bin/env python3
# Copyright Kani Contributors
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Revalidate supplied r2 capture files offline; never invoke Kani or edit evidence."""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--clone', type=Path, default=Path('/root/kani-fix-3300-m3r3'))
parser.add_argument('--artifacts', type=Path, default=Path(
    '/root/kani3300-h1-ci/m3r3-capture-r2/kani-uninit-part1-composition-pyn9bnsb'))
parser.add_argument('--job-log', type=Path, default=Path('/root/kani3300-h1-ci/m3r3-capture-r2.log'))
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
observations, rows = {}, []
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

comparisons = []
for order in manifest['orders']:
    if order['id'] not in observations:
        continue
    for name in order['selectors']:
        comparison = runner.compare_root(observations['isolated-' + name][name],
                                         observations[order['id']][name])
        comparisons.append({'order': order['id'], **comparison})
original_capture = json.loads((args.artifacts / 'capture.json').read_text())
assert original_capture['status'] == 'FAIL'
assert original_capture['error'] == (
    "Rejected('mixed-root inventory changed: immutable_legal in all_A_then_B')")
missing = [run_id for run_id in expected if run_id not in observations]
report = {
    'schema': 'kani3300-m3-r3-capture-t1b-revalidation/v1',
    'source_commit': subprocess.check_output(['git', '-C', str(args.clone), 'rev-parse', 'HEAD'],
                                            text=True).strip(),
    'implementation_sha256': {name: runner.sha256(suite / name) for name in
                              ('compare.py', 'run.py', 'test_compare.py', 'README.md')},
    'source_sha256': source_hash, 'artifact_directory': str(args.artifacts),
    'capture_run': '43502450916', 'original_capture_status': 'FAIL',
    'original_capture_error': original_capture['error'],
    'original_capture_sha256': runner.sha256(args.artifacts / 'capture.json'),
    'job_log': str(args.job_log), 'job_log_sha256': runner.sha256(args.job_log),
    'revalidated_runs': rows, 'comparisons': comparisons, 'missing_runs': missing,
    'available_mixed_root_oracle': 'MISMATCH' if any(not row['accepted'] for row in comparisons)
        else 'MATCH_WITH_T1B' if any(not row['exact_match'] for row in comparisons)
        else 'EXACT_MATCH',
    'capture_status': 'INCOMPLETE' if missing else 'COMPLETE',
    'binding_status': 'BINDING_PENDING', 'order_credit': 'NOT_ESTABLISHED',
    'proof_credit': 'NONE', 'verifier_invocations': 0,
    'note': 'Offline file integrity and runner validation only; original files unchanged.'}
print(json.dumps(report, indent=2, sort_keys=True))
