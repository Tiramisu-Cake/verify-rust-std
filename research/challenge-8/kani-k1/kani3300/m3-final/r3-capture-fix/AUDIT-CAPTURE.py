#!/usr/bin/env python3
# Copyright Kani Contributors
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Validate retained capture files without invoking a verifier or changing evidence."""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--clone', type=Path, default=Path('/root/kani-fix-3300-m3r3'))
parser.add_argument('--artifacts', type=Path, default=Path(
    '/root/kani3300-h1-ci/m3r3-capture/kani-uninit-part1-composition-iygr48dk'))
parser.add_argument('--job-log', type=Path, default=Path('/root/kani3300-h1-ci/m3r3-capture.log'))
args = parser.parse_args()
suite = args.clone / 'tests/json-handler/uninit-part1-composition'
sys.path.insert(0, str(suite))
spec = importlib.util.spec_from_file_location('capture_runner_audit', suite / 'run.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
manifest = json.loads((suite / 'roots.json').read_text())
cases = {case['name']: case for case in manifest['roots']}
expected_runs = ['isolated-' + case['name'] for case in manifest['roots']]
expected_runs += [order['id'] for order in manifest['orders']]
source_hash = runner.sha256(args.clone / manifest['source'])
assert source_hash == manifest['source_sha256']
rows = []
for receipt_path in sorted(args.artifacts.glob('*/receipt.json')):
    directory = receipt_path.parent
    receipt = json.loads(receipt_path.read_text())
    assert receipt['run_id'] == directory.name
    assert directory.name in expected_runs
    assert receipt['source_sha256'] == receipt['input_sha256_after'] == source_hash
    assert receipt['snapshot_errors'] == {}
    assert receipt['timed_out'] is False
    expected_selectors = ([directory.name.removeprefix('isolated-')]
                          if directory.name.startswith('isolated-') else
                          next(order['selectors'] for order in manifest['orders']
                               if order['id'] == directory.name))
    assert receipt['selectors'] == expected_selectors
    expected_exit = int(any(cases[name]['expected_verdict'] == 'FAILURE'
                            for name in expected_selectors))
    runner.validate_process_result(receipt['original_exit'], expected_exit)
    files = {}
    for field, filename in (('export_sha256', 'export.json'), ('regular_sha256', 'regular.out')):
        actual_hash = runner.sha256(directory / filename)
        assert actual_hash == receipt[field]
        files[filename] = actual_hash
    files['receipt.json'] = runner.sha256(receipt_path)
    data = runner.CHECKER.load_export(directory / 'export.json')
    observation = runner.observation(data, (directory / 'regular.out').read_text(),
                                     expected_selectors, cases, receipt)
    runner.compare_selection(observation, cases)
    roots = []
    for root in observation['roots']:
        roots.append({'name': root['actual_root'], 'checks': len(root['checks']),
                      'n_failed': root['n_failed'], 'verdict': root['verdict'],
                      'failure_kind': root['failure_kind'],
                      'unsupported_count': len(root['unsupported_constructs'])})
    rows.append({'run_id': directory.name, 'files_sha256': files,
                 'original_exit': receipt['original_exit'], 'expected_exit': expected_exit,
                 'original_receipt_error': receipt['error'],
                 'revalidation': 'COMPLETE_INVENTORY_VALIDATED', 'roots': roots})

failure_lines = [(index, line) for index, line in enumerate(
    args.job_log.read_text().splitlines(), 1) if line.startswith('Composition observation: ')]
assert len(failure_lines) == 1
line_number, failure_line = failure_lines[0]
original_failure = json.loads(failure_line.removeprefix('Composition observation: '))
assert original_failure['status'] == 'FAIL'
assert original_failure['error'] == "Rejected('wrong PFC target: pfc_legal')"
pfc = json.loads((args.artifacts / 'isolated-pfc_legal/export.json').read_text())['harnesses'][0]
target = pfc['attributes']['kind']['ProofForContract']['target_fn']
assert target == cases['pfc_legal']['target']
assert not target.endswith('::' + cases['pfc_legal']['target'])
present = {row['run_id'] for row in rows}
missing = [run_id for run_id in expected_runs if run_id not in present]
assert len(present) == len(rows)
report = {
    'schema': 'kani3300-m3-r3-capture-revalidation/v1',
    'source_commit': subprocess.check_output(['git', '-C', str(args.clone), 'rev-parse', 'HEAD'],
                                            text=True).strip(),
    'source_sha256': source_hash, 'artifact_directory': str(args.artifacts),
    'capture_run': '43501001052', 'job_log': str(args.job_log),
    'job_log_sha256': runner.sha256(args.job_log),
    'original_failure': {'step': 'isolated-pfc_legal', 'phase': 'observation',
                         'job_log_line': line_number, 'error': original_failure['error'],
                         'actual_target': target, 'legacy_predicate_accepted': False},
    'revalidated_runs': rows, 'missing_runs': missing,
    'capture_status': 'INCOMPLETE' if missing else 'READY_FOR_FULL_COMPARISON',
    'binding_status': 'BINDING_PENDING', 'order_credit': 'NOT_ESTABLISHED',
    'proof_credit': 'NONE', 'verifier_invocations': 0,
    'note': 'Offline file integrity and runner validation only. Original artifacts and receipts unchanged.'}
print(json.dumps(report, indent=2, sort_keys=True))
