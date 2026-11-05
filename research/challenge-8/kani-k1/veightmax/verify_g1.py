#!/usr/bin/env python3
"""Reconcile saved bounded helper outputs; consistency PASS is not proof acceptance."""
import hashlib
import json
import subprocess
from collections import Counter
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
E = HERE / 'evidence'
BUILD = 'daf1045c-5454-4662-93a7-df16cfd23e00'
HEAD = '7df3f7d3d68c458185c2f42f72483c13fbe9c161'
KANI = 'cd355b0bccd32300713bc2ce4f765dafa1510607'
PREFIX = 'slice::sort::shared::smallsort::verify::'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def fields(text):
    return dict(line.split('=', 1) for line in text.splitlines()
                if '=' in line and not line.startswith(PREFIX))


def main():
    request_bytes = (HERE / 'RUN-REQUEST.json').read_bytes()
    source_request = subprocess.check_output(
        ['git', 'show', HEAD + ':research/challenge-8/kani-k1/RUN-REQUEST.json'])
    assert source_request == request_bytes
    request = json.loads(request_bytes)
    request_hash = sha(request_bytes)
    assert request_hash == '5e6e812216996d281d57aa8bb2626c27b32fed1be71329b2c7cc96261e6161fc'
    identity = {'request_id': request['request_id'], 'request_sha256': request_hash,
                'build_id': BUILD, 'head_sha': HEAD}
    assert request['inventory'] is True and request['controls'] is False
    assert request['agent'] == 'k1-merge' and request['kani_jobs'] == 1
    assert request['runner'] == 'gcb-e2-standard-4' and request['harness_timeout_minutes'] == 4
    text = (E / 'rows.txt').read_text()
    assert fields(text) == identity | {'total': '7', 'offset': '0', 'count': '7', 'next_offset': 'done'}
    rows = []
    for line in text.splitlines():
        if not line.startswith(PREFIX):
            continue
        name, status, seconds, checks, covers = line.split('\t')
        failed, total = map(int, checks.split('/')) if checks else (None, None)
        reached, cover_total = map(int, covers.split('/')) if covers else (None, None)
        rows.append({'name': name, 'status': status,
                     'seconds': seconds if seconds not in ('', 'None') else None,
                     'checks_failed': failed, 'checks_total': total,
                     'covers_satisfied': reached, 'covers_total': cover_total})
    assert len(rows) == 7 and len({r['name'] for r in rows}) == 7
    assert {r['name'] for r in rows} == {r['name'] for r in request['harnesses']}
    assert Counter(r['status'] for r in rows) == {'SUCCESS': 2, 'UNKNOWN': 1, 'NOT_RUN': 4}
    expected_covers = json.loads((HERE / 'expected-covers.json').read_text())
    completed = [r for r in rows if r['status'] == 'SUCCESS']
    assert {r['name'][len(PREFIX):] for r in completed} == {
        'allocationcontracts::merge_safety_u64_len8_scratch48_src32_dst0',
        'allocationcontracts::sort8_safety_u64_scratch48_src32_dst0_merge_stubbed'}
    assert all(r['checks_failed'] == 0 and r['checks_total'] > 0 and
               r['covers_satisfied'] == r['covers_total'] == expected_covers[r['name']]
               for r in completed)
    assert all(r['seconds'] is r['checks_failed'] is r['covers_total'] is None
               for r in rows if r['status'] != 'SUCCESS')

    # Preserve the helper's inventory order for its hash; compare canonical sorted names separately.
    names, next_offset, page_identity = [], '0', None
    for filename in ('inventory-000.txt', 'inventory-080.txt', 'inventory-160.txt'):
        page = (E / filename).read_text()
        f = fields(page)
        assert all(f[k] == v for k, v in identity.items()) and f['kani_commit'] == KANI
        assert f['total'] == '233' and f['offset'] == next_offset
        binding = {k: v for k, v in f.items() if k not in ('offset', 'count', 'next_offset')}
        assert page_identity is None or binding == page_identity
        page_identity = binding
        batch = [line for line in page.splitlines() if line.startswith(PREFIX)]
        assert len(batch) == int(f['count']) and int(f['offset']) == len(names)
        names.extend(batch)
        next_offset = f['next_offset']
        assert next_offset == ('done' if len(names) == 233 else str(len(names)))
    assert next_offset == 'done' and len(names) == len(set(names)) == 233
    assert sha(('\n'.join(names) + '\n').encode()) == page_identity['names_sha256']
    canonical = ('\n'.join(sorted(names)) + '\n').encode()
    expected_names = (HERE / 'ordinary-expected.txt').read_bytes()
    assert canonical == expected_names
    assert sha(canonical) == 'a73e3c308728c7e7e560665547f79775ddffef2676d4ddee1cecd1b572bdd374'
    assert {r['name'] for r in rows} <= set(names)

    summary = (E / 'summary.md').read_text()
    assert summary.startswith('# K-1 run `veightmax-g1-20261105-02`: PARTIAL')
    assert all(value in summary for value in (HEAD, KANI, request_hash, BUILD))
    assert 'gate: False; expectation met: False;' in summary and 'Kani exit 124' in summary
    assert "final 'Complete - …' line missing" in summary
    assert 'build success' in summary
    cloud = json.loads((E / 'status.json').read_text())
    assert cloud['id'] == BUILD and cloud['source_sha'] == HEAD and cloud['status'] == 'FAILURE'
    assert cloud['pool'].endswith('/k1-standard4') and cloud['timeout'] == '3480s'
    tooling = (E / 'tooling.txt').read_text().splitlines()
    assert len(tooling) == 8 and all(line.startswith('ok   ') for line in tooling)
    assert HEAD in '\n'.join(tooling) and '59893bff1fbb2af1a0c08862afd7e3bb87c19cdd' in '\n'.join(tooling)
    machine = fields((E / 'peaks.txt').read_text())
    assert machine['verify_start_after_validate_s'] == '2851' and machine['verify_budget_s'] == '269'
    assert machine['dmesg_oom'] == 'none_seen' and machine['swap_total_bytes'] == '0'
    count, cost, reserve = (E / 'budget.txt').read_text().split()
    assert count == '1' and Decimal(cost) == Decimal('0.7290') and Decimal(reserve) == 0
    seconds = sum(Decimal(r['seconds']) for r in completed)
    assert seconds == Decimal('94.568953')
    report = {'evidence_consistency': 'PASS', 'task_acceptance': 'FAIL_PARTIAL_VERIFICATION',
              'build_id': BUILD, 'source_sha': HEAD, 'request_id': request['request_id'],
              'request_sha256': request_hash, 'kani_commit': KANI,
              'cloud_status': cloud['status'], 'summary_status': 'PARTIAL', 'gate': False,
              'summary_build_outcome': 'success', 'build_outcome_discrepancy_preserved': True,
              'kani_exit': 124, 'rows': rows, 'successful_rows': 2, 'unknown_rows': 1,
              'not_run_rows': 4, 'completed_covers_satisfied': 9, 'completed_covers_total': 9,
              'expected_all_covers': sum(expected_covers.values()),
              'completed_root_seconds_sum': str(seconds), 'all_seven_root_seconds_sum': None,
              'inventory': {'count': 233, 'unique_count': 233, 'expected_names_match': True,
                            'missing': [], 'extra': [], 'pages': 3,
                            'inventory_artifact_sha256': page_identity['inventory_sha256'],
                            'names_in_artifact_order_sha256': page_identity['names_sha256'],
                            'sorted_names_sha256': sha(canonical),
                            'note': 'Artifact order groups standard/contract harnesses; sorted canonical names match exactly.'},
              'tooling': 'PASS: source, pool, lane paths and six bound files',
              'verify_start_after_validate_s': 2851, 'verify_budget_s': 269,
              'cause': 'Runner-wide selected verification cut at the remaining 269-second budget '
                       '(exit 124, missing final Complete). Preparation including inventory consumes '
                       'the same 52-minute validate-to-verify deadline in the unchanged runner. '
                       'No per-root timeout or failed obligation is established for UNKNOWN.',
              'cost_usd': cost, 'reserved_usd': reserve, 'builds': 1, 'retries': 0, 'repairs': 0,
              'limits': 'Only the two completed bounded rows have integrated SUCCESS. '
                        'NOT_RUN/UNKNOWN do not inherit integrated proof or time credit from prior sources. '
                        'Nine reached covers are not 42/42. No universal T/F or unwinding theorem.'}
    report['bounded_outputs_sha256'] = {
        f.name: sha(f.read_bytes()) for f in sorted(E.iterdir())
        if f.is_file() and f.name != 'verification-report.json'}
    (E / 'verification-report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ('evidence_consistency', 'task_acceptance',
          'successful_rows', 'unknown_rows', 'not_run_rows', 'completed_covers_satisfied',
          'expected_all_covers', 'completed_root_seconds_sum', 'cost_usd')}, indent=2))


if __name__ == '__main__':
    main()
