# Copyright Kani Contributors
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Replay only JSON evidence from the exact ZIP; never execute evidence argv."""
import argparse
import collections
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import zipfile

BASELINE = '741b7183b4d6e9d752c0b7951206d7257f69f951'
CONTROL = '112fcc9ada67ee2bb8e1712d47983d6717487b78'
ZIP_SHA = '6b1f8ed210d93aae32b3e512565df7d6726d43660c19cb3c614f612f6b1a15e9'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--zip', required=True, type=Path)
    p.add_argument('--control', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    args = p.parse_args()
    assert digest(args.zip.read_bytes()) == ZIP_SHA
    assert git(args.control, 'rev-parse', 'HEAD').decode().strip() == CONTROL
    assert not git(args.control, 'status', '--porcelain')
    runner_path = args.control / 'ch8-prof-off-control/runner.py'
    fixed = module('fixed', runner_path)
    request_path = args.control / 'ch8-prof-off-control/CI-REQUEST.json'
    request = fixed.load_request(request_path)
    raw_request = json.loads(request_path.read_bytes())
    baseline_request = git(args.control, 'show', BASELINE + ':ch8-prof-off-control/CI-REQUEST.json')
    assert raw_request['rows'] == json.loads(baseline_request)['rows']
    assert git(args.control, 'show', BASELINE + ':ch8-prof-off-control/manifest.json') == (
        args.control / 'ch8-prof-off-control/manifest.json').read_bytes()
    groups = fixed.batch_groups(request['rows'])
    result = {
        'schema': 'ch8-prof-off-offline-reclassification-v1',
        'run': 43784551069, 'artifact_id': 14190662926,
        'sibling': '075750ca90a65792e2489041d071ba9dbb5cebdb',
        'baseline_control': BASELINE, 'fixed_control': CONTROL,
        'artifact_zip_sha256': ZIP_SHA,
        'baseline_request_sha256': digest(baseline_request),
        'fixed_classifier_sha256': digest(runner_path.read_bytes()),
        'method': 'Same parse_export and _consumer_gates; only profile target binding fixed; oracles unchanged.',
        'proof_credit': 'NONE',
        'assurance': 'Exact source-reported Kani JSON and receipt replay, not independent compiler execution or symbol-resolution proof.',
        'groups': [], 'rows': [],
    }
    with zipfile.ZipFile(args.zip) as archive, tempfile.TemporaryDirectory(prefix='prof-off-replay-') as temp:
        temp = Path(temp)
        old_path = temp / 'baseline.py'
        old_path.write_bytes(git(args.control, 'show', BASELINE + ':ch8-prof-off-control/runner.py'))
        old = module('baseline', old_path)
        original = json.loads(archive.read('receipt.json'))
        original_rows = {r['id']: r for r in original['rows']}
        assert len(original_rows) == 62 and original['stop_reason'] is None
        job = json.loads(archive.read('job-status.json'))
        assert job['request_sha256'] == digest(baseline_request)
        observations = {}
        for n, rows in enumerate(groups):
            group = f'group-{n:02d}'
            member = f'groups/{group}/export.json'
            data = archive.read(member)
            path = temp / (group + '.json'); path.write_bytes(data)
            export = json.loads(data)
            receipt = json.loads(archive.read(f'groups/{group}/receipt.json'))
            assert digest(data) == receipt['export_sha256']
            assert receipt['source_before'] == receipt['source_after']
            assert receipt['source_before']['std_sha'] == fixed.STD_SHA
            assert receipt['source_before']['tool_sha'] == fixed.TOOL_SHA
            before, after = receipt['tool_fingerprints_before'], receipt['tool_fingerprints_after']
            assert before['required_hashes_present'] and after['required_hashes_present']
            assert {k: v['sha256'] for k, v in before['binaries'].items()} == {
                k: v['sha256'] for k, v in after['binaries'].items()}
            execution = receipt['execution']
            assert not any(execution.get(k) for k in ['termination_reason', 'signal', 'timed_out', 'output_truncated'])
            assert execution['original_exit_code'] == n
            assert execution['compilation']['state'] == 'PRE_HARNESS_COMPLETE'
            assert sorted(execution['compilation']['harness_marker_order']) == sorted(r['id'] for r in rows)
            assert receipt['cfg'] == rows[0]['cfg']
            checks = {k: sum(h['checks'][k] if type(h['checks'][k]) is int else len(h['checks'][k])
                             for h in export['harnesses']) for k in export['harnesses'][0]['checks']}
            assert checks['total'] == sum(v for k, v in checks.items() if k != 'total')
            result['groups'].append({
                'id': group, 'export_member': member, 'export_sha256': digest(data),
                'receipt_sha256': digest(archive.read(f'groups/{group}/receipt.json')),
                'summary': export['summary'], 'checks': checks,
                'unsupported_status_counts': dict(collections.Counter(
                    u['status'] for h in export['harnesses'] for u in h['unsupported_constructs'])),
                'original_exit': execution['original_exit_code'], 'exit_scope': 'GROUP_NOT_ROW',
                'compile_seconds': execution['compilation']['elapsed_seconds'],
                'group_elapsed_seconds': execution['elapsed_seconds'],
                'rss_peak_kib': execution['rss_peak_kib'], 'per_row_rss': 'UNKNOWN',
                'source_and_binary_snapshot_consistency': True,
            })
            for row in rows:
                historical = json.loads(archive.read(row['id'] + '/receipt.json'))
                assert historical == original_rows[row['id']]
                assert historical['group_export_sha256'] == digest(data)
                baseline = old.parse_export(path, row, max_bytes=receipt['export_cap_bytes'], group_rows=rows)
                assert baseline == historical['export'], row['id']
                parsed = fixed.parse_export(path, row, max_bytes=receipt['export_cap_bytes'], group_rows=rows)
                h = next(h for h in export['harnesses'] if h['name'] == row['selector'])
                kind = h['attributes']['kind']
                target = kind['ProofForContract']['target_fn'] if row['mode'] == 'PFC' else None
                expected_target = row['profile_mode'].split(':', 1)[1] if row['mode'] == 'PFC' else None
                if expected_target == 'concrete_forwarder':
                    expected_target = {'stable_cell_n2': 'stable_cell', 'unstable_byte_n2': 'unstable_byte',
                                       'freeze_noncopy_n2': 'freeze_noncopy'}[row['id']]
                normalized_file = h['file'].replace('\\', '/')
                binding = {
                    'harness_selector_expected': row['selector'], 'harness_selector_actual': h['name'],
                    'source_selector_expected': row['source_selector'],
                    'source_file_expected': row['source_file'], 'source_file_actual': h['file'],
                    'source_file_normalized': normalized_file,
                    'file_matches': normalized_file == row['source_file'] or normalized_file.endswith('/' + row['source_file']),
                    'source_line_reported': h['line'],
                    'target_triple_expected': fixed.TARGET, 'target_triple_actual': export['target'],
                    'profile_mode_expected': row['profile_mode'], 'mode_actual': kind,
                    'contract_actual': h.get('contract'),
                    'profile_target_expected': expected_target, 'profile_target_actual': target,
                    'profile_stage_matches': fixed._profile_target_matches(target, expected_target) if target is not None else row['mode'] == 'Original',
                    'unwind_expected': row['unwind'], 'unwind_actual': h['resolved_unwind'],
                    'cfg_expected': row['cfg'], 'cfg_receipt': receipt['cfg'],
                    'exact_group_selection_validated_by_classifier': True,
                    'contract_wrapper_resolution': 'PENDING_INDEPENDENT_REVIEW',
                    'binding_scope': 'Selected export entry and frozen manifest stage; no AST/MIR/ADT independent binding claimed.',
                }
                assert binding['file_matches'] and binding['profile_stage_matches']
                assert row['unwind'] == h['resolved_unwind'] and export['target'] == fixed.TARGET
                verdict = h['outcome']['verdict']
                descriptions = row['allowed_failure_descriptions']
                named = h['failed_properties']
                generated = any(d.startswith('<generated modifies') for d in descriptions)
                matches = ([sum(d in prop['description'] for prop in named) for d in descriptions])
                named_match = ('REVIEW_REQUIRED_GENERATED_FRAME_PROPERTY' if generated else
                               len(named) == len(descriptions) and matches == [1] * len(descriptions) and
                               all(sum(d in prop['description'] for d in descriptions) == 1 for prop in named))
                entry = {
                    'id': row['id'], 'group': group, 'export_member': member, 'export_sha256': digest(data),
                    'harness_index': export['harnesses'].index(h), 'binding': binding,
                    'oracle': {'expected': row['expected'], 'allowed_failure_descriptions': descriptions,
                               'required_cover_count': row['required_cover_count'], 'covers_policy': row['covers']},
                    'kani_outcome': h['outcome'],
                    'kani_verdict_matches_oracle': verdict == ('SUCCESS' if row['expected'] == 'SUCCESS' else 'FAILURE'),
                    'named_failures_match_oracle': named_match,
                    'checks': h['checks'], 'unsupported_constructs': h['unsupported_constructs'],
                    'covers': h['covers'], 'named_failures': named,
                    'all_emitted_covers_satisfied': len(h['covers']['satisfied']) == h['covers']['total'] and
                        all(h['covers'][k] == [] for k in ['unsatisfiable','unreachable','undetermined','error','unknown','other']),
                    'baseline_classifier': {'state': baseline['state'], 'outcome': baseline['outcome']},
                    'historical_receipt_outcome': historical['outcome'],
                    'fixed_classifier': {'state': parsed['state'], 'outcome': parsed['outcome']},
                    'proof_credit': 'NONE',
                }
                result['rows'].append(entry)
                observations[row['id']] = {**fixed._row_base(row), 'outcome': parsed['outcome'], 'export': parsed}
        fixed._consumer_gates(request['rows'], observations, temp / 'reclassified-receipts')
        for entry in result['rows']:
            observation = observations[entry['id']]
            entry['acceptance'] = {
                'row_observation': observation['outcome'],
                'independent_acceptance': 'PENDING', 'proof_credit': 'NONE',
                'consumer_reason': observation.get('reason'), 'consumer_gate': observation.get('consumer_gate'),
            }
        result['summary'] = {
            'rows': len(result['rows']), 'historical_snapshots_reproduced': 62,
            'baseline_classifier_states': dict(collections.Counter(r['baseline_classifier']['state'] for r in result['rows'])),
            'fixed_classifier_states': dict(collections.Counter(r['fixed_classifier']['state'] for r in result['rows'])),
            'row_observation_outcomes': dict(collections.Counter(r['acceptance']['row_observation'] for r in result['rows'])),
            'kani_verdicts': dict(collections.Counter(r['kani_outcome']['verdict'] for r in result['rows'])),
            'kani_verdict_oracle_matches': sum(r['kani_verdict_matches_oracle'] for r in result['rows']),
            'blocked_consumers': [r['id'] for r in result['rows'] if r['acceptance']['consumer_reason']],
            'phase_elapsed_seconds': original['phase_elapsed_seconds'],
        }
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
        print(json.dumps(result['summary'], indent=2))


if __name__ == '__main__':
    main()
