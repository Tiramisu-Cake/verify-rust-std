#!/usr/bin/env python3
"""Check captured bounded repair evidence; no raw logs, verifier or remote execution."""
import hashlib
import json
from collections import Counter
from decimal import Decimal
from pathlib import Path

PACKET = Path(__file__).resolve().parent
E = PACKET/'evidence/repair1'
BUILD = '8400bb9d-f0f3-43fe-b47e-df5b4a4aae67'
SOURCE = 'dc0d792f74c437966aff93c734d43fcedc4dc7a7'
KANI = 'cd355b0bccd32300713bc2ce4f765dafa1510607'
PREFIX = 'slice::sort::shared::smallsort::verify::'


def main():
    request_bytes = (E/'request.json').read_bytes()
    request = json.loads(request_bytes)
    request_hash = hashlib.sha256(request_bytes).hexdigest()
    assert request_hash == '92b07d04e7bf08dcfaba93c0b92601236e3ce9cf987b00b34e181797ffe0ff22'
    assert request_bytes == (PACKET/'request.json').read_bytes()
    status = json.loads((E/'status.json').read_text())
    assert status['id'] == BUILD and status['source_sha'] == SOURCE
    assert status['status'] == 'FAILURE' and status['timeout'] == '4680s'
    assert status['pool'].endswith('/workerPools/k1-standard4')
    summary = (E/'summary.md').read_text()
    assert all(s in summary for s in (BUILD, SOURCE, KANI, request_hash, request['request_id']))
    assert ': COMPLETE' in summary and 'gate: False; expectation met: False' in summary
    assert 'Kani exit 1' in summary and 'COMPILE_ERROR' not in summary
    rows_bytes = (E/'rows.txt').read_bytes()
    lines = rows_bytes.decode().splitlines()
    assert dict(line.split('=', 1) for line in lines[:8]) == {
        'request_id': request['request_id'], 'request_sha256': request_hash,
        'build_id': BUILD, 'head_sha': SOURCE, 'total': '12',
        'offset': '0', 'count': '12', 'next_offset': 'done'}
    assert lines[8] == 'name\tstatus\ttime_s\tchecks\tcovers'
    rows = {}
    for line in lines[9:]:
        name, outcome, seconds, checks, covers = line.split('\t')
        assert name not in rows
        rows[name] = {'status': outcome, 'time_s': None if seconds == 'None' else seconds,
                      'checks': checks or None, 'covers': covers or None}
    assert len(rows) == 12 and set(rows) == {r['name'] for r in request['harnesses']}
    expected = {
        'loopreal::insert_tail_u64_backing8': 'TIMEOUT',
        'loopreal::insert_tail_u64_backing32': 'TIMEOUT',
        'loopreal::insert_tail_u64_backing128': 'TIMEOUT',
        'loopreal::outer_loop_u64_backing8': 'SUCCESS',
        'loopreal::outer_loop_u64_backing32': 'TIMEOUT',
        'loopreal::outer_loop_u64_backing128': 'OUT_OF_MEMORY',
        'loopreal::outer_loop_false_invariant_backing8': 'FAILED',
        'realcontracts::insert_tail_safety_u64_tail1_to4_backing5': 'TIMEOUT',
        'network::unstable_freeze_noncopy_bytes86_fallback_n2': 'TIMEOUT',
        'realcontracts::unstable_network_safety_u8_n9_stubbed': 'SUCCESS',
        'assembly::safety_stable_unit_n16': 'SUCCESS',
        'assembly::safety_stable_unit_n32': 'SUCCESS',
    }
    expected_covers = json.loads((PACKET/'expected-covers.json').read_text())
    completed_covers = 0
    for short, outcome in expected.items():
        row = rows[PREFIX+short]
        assert row['status'] == outcome
        if outcome == 'SUCCESS':
            assert row['checks'].startswith('0/') and Decimal(row['time_s']) < 240
            n = expected_covers[PREFIX+short]
            assert row['covers'] == f'{n}/{n}'
            completed_covers += n
        elif outcome in ('TIMEOUT', 'OUT_OF_MEMORY'):
            assert row['time_s'] is row['checks'] is row['covers'] is None
    assert completed_covers == 7
    negative = PREFIX+'loopreal::outer_loop_false_invariant_backing8'
    assert rows[negative]['checks'] == '1/636'
    failed = [line for line in summary.splitlines() if line.startswith('- Check invariant after step')]
    assert len(failed) == 1
    description, location = failed[0][2:].split(' @ ')
    assert description.startswith('Check invariant after step for loop '+PREFIX+'loopreal::insertion_sort_shift_left_false::<u64,')
    assert location == '/workspace/src/library/core/src/slice/sort/shared/smallsort/verify/loopreal.rs:115'
    assert next(h for h in request['harnesses'] if h['name']==negative)['expect_check'] in description
    diagnostics = (E/'proof-diagnostics.txt').read_text()
    assert diagnostics.count('Checking harness ') == 12
    assert diagnostics.count('CBMC timed out.') == 6
    assert diagnostics.count('CBMC appears to have run out of memory.') == 1
    assert diagnostics.count('Failed Checks: Check invariant after step') == 1
    # Terse output identifies the negative step, but does not enumerate successful invariant checks.
    assert 'Check invariant before entry' not in diagnostics
    tooling = (E/'tooling.txt').read_text().splitlines()
    assert len(tooling) == 8 and all(s.startswith('ok ') for s in tooling)
    assert SOURCE in tooling[1] and '59893bff1fbb2af1a0c08862afd7e3bb87c19cdd' in tooling[1]
    seen = set()
    for filename, page in [('peaks0.txt', 'process_records=12 offset=0 count=8 next_offset=8'),
                           ('peaks8.txt', 'process_records=12 offset=8 count=4 next_offset=done')]:
        text = (E/filename).read_text()
        assert page in text
        processes = [json.loads(s) for s in text.splitlines() if s.startswith('{')]
        assert len(processes) == (8 if filename == 'peaks0.txt' else 4)
        for process in processes:
            assert process['build_id'] == BUILD and process['head_sha'] == SOURCE
            assert process['kani_commit'] == KANI and process['cmd'] == 'cbmc'
            assert process['attribution'] == process['metadata_resolution'] == 'direct'
            name = process['harness']
            assert name == process['direct_harness'] == process['pretty_name']
            assert name in rows and name not in seen
            assert process['metadata_match_count'] == 1
            assert process['peak_kb'] > 0
            rows[name]['cbmc_peak_rss_kib'] = process['peak_kb']
            seen.add(name)
    assert seen == set(rows)
    assert 'max RSS 15601676 KiB, wall 40:18.76' in summary
    assert 'Out of memory: Killed process' in (E/'peaks0.txt').read_text()
    n, spent, reserved = (E/'cost.txt').read_text().split()
    assert n == '1' and Decimal(spent) == Decimal('0.6480') and Decimal(reserved) == 0
    original = json.loads((PACKET/'evidence/verification-report.json').read_text())
    total_spent = Decimal(original['spent_usd']) + Decimal(spent)
    assert total_spent == Decimal('0.7560')
    baselines = json.loads((PACKET/'regression-baselines.json').read_text())
    comparisons = []
    for before in baselines:
        after = rows[before['name']]
        comparisons.append({'name': before['name'], 'baseline': before,
                            'after_status': after['status'], 'after_time_s': after['time_s'],
                            'qualification': 'Historical K-1 comparison with no isolated causal attribution.'
                            if before['evidence_kind']=='bounded_k1_rows' else
                            'Approximate Actions-v7 to GCB comparison; supplied timings are not independently verified.'})
    report = {
        'verdict': 'FAIL_SCALING_AND_REGRESSION_GATES',
        'build_id': BUILD, 'source_sha': SOURCE, 'request_id': request['request_id'],
        'request_sha256': request_hash, 'kani_commit': KANI,
        'cloud_status': 'FAILURE', 'summary_status': 'COMPLETE', 'gate': False, 'kani_exit': 1,
        'compiled': True, 'tooling_bindings': 'PASS', 'rows': rows,
        'status_counts': dict(Counter(r['status'] for r in rows.values())),
        'negative_control': {'established': True, 'failed_checks': 1,
                             'description': description, 'location': location},
        'successful_rows_covers_satisfied': 7, 'successful_rows_covers_total': 7,
        'expected_positive_covers': 34, 'full_positive_coverage_established': False,
        'positive_invariant_check_observability': 'Terse rows do not enumerate successful invariant base/step checks; only the negative step is located. No separate per-check listing was obtained.',
        'pfc_consumer_pairs': {str(size): {'pfc_status': rows[PREFIX+f'loopreal::insert_tail_u64_backing{size}']['status'],
                                          'consumer_status': rows[PREFIX+f'loopreal::outer_loop_u64_backing{size}']['status'],
                                          'composition_credit': False} for size in (8,32,128)},
        'length_cost_conclusion': 'No near-constant verification-cost evidence: no completed u64 PFC at any backing; outer 8 succeeds conditionally, 32 times out, 128 is OOM. Timeout/OOM rows have no verification time, only the configured four-minute budget.',
        'regression_comparisons': comparisons, 'verify_wall_with_compilation': '40:18.76',
        'time_v_max_rss_kib': 15601676, 'sampled_cbmc_peak_rss_kib': 15503184,
        'memory_note': 'All 12 per-root CBMC peaks have direct metadata attribution. Kani reports OOM for outer128 and bounded kernel scan records a cbmc kill; kernel and sampler PIDs are not claimed to be identical.',
        'spent_usd': spent, 'reserved_usd': reserved, 'own_total_spent_usd': str(total_spent),
        'own_remaining_usd': str(Decimal('2.00')-total_spent),
        'metadata_discrepancy': 'Summary run text says build success, bounded Cloud status FAILURE; retain both and use FAILURE / COMPLETE gate false.',
        'rows_capture_sha256': hashlib.sha256(rows_bytes).hexdigest(),
        'capture_note': 'Empty TSV check/cover fields are preserved as trailing tabs; whitelist this capture alone for whitespace checking.',
        'integration_note': 'Coordinator: smallsort.rs:695 is 108 characters; wrap loop_modifies arguments onto separate lines at integration. Source unchanged for this run.',
        'scope': 'Bounded-response consistency, not independent verifier execution. No arbitrary-length, generic T/F, merge, other-loop or termination proof; outer8 has no matched PFC credit. No G2 dispatched.',
    }
    (E/'verification-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k: v for k, v in report.items() if k not in ('rows','regression_comparisons')},indent=2))


if __name__=='__main__':
    main()
