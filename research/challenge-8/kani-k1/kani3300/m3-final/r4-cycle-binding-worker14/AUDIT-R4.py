#!/usr/bin/env python3
# Copyright Kani Contributors
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Revalidate supplied r4 capture and reviewed bindings offline; never invoke Kani or edit evidence."""
import argparse
import contextlib
import io
import tempfile
from unittest import mock
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--clone', type=Path, default=Path('/root/kani-fix-3300-worker14'))
parser.add_argument('--artifacts', type=Path, default=Path(
    '/root/kani3300-h1-ci/m3r3-capture-r4/kani-uninit-part1-composition-clpox3px'))
parser.add_argument('--job-log', type=Path, default=Path('/root/kani3300-h1-ci/m3r3-capture-r4.log'))
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
base_commit = '3912b8e0319754f43bbcd7f2b363ad5cbf0a80c9'
ci_commit = '8b2bca3bed4c643d4a0126de5dedfb2a723b9214'
ci_changes = subprocess.check_output(['git', '-C', str(args.clone), 'diff', '--name-only',
                                      base_commit, ci_commit], text=True).splitlines()
assert ci_changes and all(p.startswith('.github/workflows/') for p in ci_changes)
log_text = args.job_log.read_text()
assert ci_commit in log_text and '/actions/runs/43506774865/artifacts/' in log_text
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
    assert receipt['error'] is None and receipt['expected_exit'] == expected_exit
    assert receipt['input'] == manifest['source']
    argv = receipt['argv']
    original_directory = Path(argv[argv.index('--export-json') + 1]).parent
    expected_argv = runner.command('kani', manifest, expected[run_id], original_directory)
    expected_argv[1] = str(Path(receipt['build_prefix']) / manifest['source'])
    assert argv == expected_argv and original_directory.name == run_id
    data = runner.CHECKER.load_export(directory / 'export.json')
    assert data['kani_commit'] == ci_commit
    observed = runner.observation(data,
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
assert original['mixed_root_oracle'] == 'MATCH_WITH_T1B'
assert {r['run_id']: r for r in original['runs']} == {
    r['run_id']: json.loads((args.artifacts / r['run_id'] / 'receipt.json').read_text())
    for r in rows}
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
assert rejected == []
reviewed = []
for name, case in cases.items():
    assert case['binding'] == 'REGRESSION_BOUND'
    runner.check_single(observations['isolated-' + name][name], {
        'binding': case['binding'], 'expected_verdict': case['expected_verdict'],
        'checks': case['expected_inventory'], 'failure_kind': case['expected_failure_kind'],
        'failed_properties': case['expected_failures'],
        'unsupported_constructs': case['expected_unsupported_inventory'],
        'covers': case.get('expected_covers', [])})
    assert all(row['accepted'] for row in comparisons if row['root'] == name)
    reviewed.append(name)
cycle = observations['isolated-cycle_root']['cycle_root']
assert len(cycle['checks']) == 384 and cycle['n_failed'] == 1
assert cycle['failure_kind'] == 'OTHER' and cycle['verdict'] == 'FAILURE'
assert cycle['failed_properties'] == cycle['unsupported_constructs']
message = cycle['failed_properties'][0]['description']
assert message.startswith('Kani delayed uninitialized-memory analysis detected an interprocedural cycle')
assert 'root/active path: cycle_root [provenance=source]' in message
assert 'provenance=registration-override' in message and 'mixed.rs:75]' in message
assert not any(token in message for token in ('AnalysisKey', 'Instance {', 'DefId('))
assert all(row['exact_match'] for row in comparisons if row['root'] == 'cycle_root')
cycle_evidence = cases['cycle_root']['binding_evidence']
assert cycle_evidence['capture_source_commit'] == base_commit
assert cycle_evidence['capture_ci_commit'] == ci_commit
assert cycle_evidence['capture_sha256'] == runner.sha256(args.artifacts / 'capture.json')
assert cycle_evidence['capture_run'] == '43506774865'

# Replay the ordinary runner using only reconstructed saved observations. This
# exercises preflight, exact isolated binding checks and mixed-root oracle paths.
# A hard subprocess guard prevents this replay from launching any verifier.
def replay_execute(_kani, _manifest, selectors, _cases, _base, run_id):
    assert selectors == expected[run_id]
    receipt = json.loads((args.artifacts / run_id / 'receipt.json').read_text())
    return reconstructed[run_id], receipt

with tempfile.TemporaryDirectory() as replay_directory:
    with mock.patch.object(runner.tempfile, 'mkdtemp', return_value=replay_directory), \
            mock.patch.object(runner, 'execute', side_effect=replay_execute) as calls, \
            mock.patch.object(runner.subprocess, 'run', side_effect=AssertionError('offline only')), \
            contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        replay_exit = runner.capture(argparse.Namespace(kani='must-not-run',
                                     collect_unbound=False, keep_output=True))
    replay = json.loads((Path(replay_directory) / 'capture.json').read_text())
    assert calls.call_count == 11 and replay_exit == 0
    assert replay['status'] == 'PASS' and replay['binding_status'] == 'REGRESSION_BOUND'
    assert replay['mixed_root_comparisons'] == comparisons
    assert replay['mixed_root_oracle'] == 'MATCH_WITH_T1B'

report = {
    'schema': 'kani3300-worker14-r4-binding-audit/v1',
    'status': 'PASS', 'offline_replay_exit': replay_exit,
    'binding_status': replay['binding_status'],
    'capture_source_commit': base_commit, 'capture_ci_commit': ci_commit,
    'ci_wrapper_changed_paths': ci_changes,
    'source_clone': str(args.clone),
    'source_commit': subprocess.check_output(['git', '-C', str(args.clone), 'rev-parse', 'HEAD'],
                                            text=True).strip(),
    'capture_run': '43506774865', 'artifact_directory': str(args.artifacts),
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
    'reviewed_roots': reviewed, 'pending_roots': [],
    'order_credit': 'NOT_ESTABLISHED', 'proof_credit': 'NONE',
    'verifier_invocations': 0,
    'note': 'Offline validation of explicitly supplied local capture files only; '
            'r4 diagnostic validated against saved exports and regular output; no normalization of cycle text; '
            'offline replay PASS is not a fresh CI or C1 qualification.'}
print(json.dumps(report, indent=2, sort_keys=True))
