#!/usr/bin/env python3
"""Check saved bounded G2 helper outputs; no cache/raw evidence or proof tools."""
import hashlib
import json
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
E = HERE / 'g2-evidence'
PREFIX = 'slice::sort::shared::smallsort::verify::'
BUILD = 'bd623a0c-935a-4bcd-a5c1-5d6f148c6bec'
HEAD = '9cc449ccce74c6b3b8f96554b86308ff39a2b71f'
KANI = 'cd355b0bccd32300713bc2ce4f765dafa1510607'


def main():
    request = json.loads((E / 'RUN-REQUEST.json').read_text())
    request_hash = hashlib.sha256((E / 'RUN-REQUEST.json').read_bytes()).hexdigest()
    fields, rows = {}, []
    for line in (E / 'rows.txt').read_text().splitlines():
        if line.startswith(PREFIX):
            name, status, time, checks, covers = line.split('\t')
            failed, total = (map(int, checks.split('/')) if checks else (None, None))
            reached, cover_total = (map(int, covers.split('/')) if covers else (None, None))
            rows.append({'name': name, 'status': status,
                         'seconds': None if time == 'None' else float(time),
                         'seconds_decimal': None if time == 'None' else time,
                         'checks_failed': failed, 'checks_total': total,
                         'covers_satisfied': reached, 'covers_total': cover_total})
        elif '=' in line:
            k, v = line.split('=', 1)
            fields[k] = v
    summary = (E / 'summary.md').read_text()
    status = json.loads((E / 'status.json').read_text())
    expected = json.loads((E / 'expected-g2-covers.json').read_text())
    completed = [r for r in rows if r['status'] == 'SUCCESS']
    timed_out = [r['name'] for r in rows if r['status'] == 'TIMEOUT']
    quick = [r['name'] for r in completed if r['seconds'] <= 120]
    slow = [r['name'] for r in completed if r['seconds'] > 120]
    tooling = (E / 'tooling.txt').read_text().splitlines()
    n, cost, reserve = (E / 'budget-total.txt').read_text().split()
    checks = {
        'row_identity_page_and_exact_requested_names':
            fields == {'request_id': request['request_id'], 'request_sha256': request_hash,
                       'build_id': BUILD, 'head_sha': HEAD, 'total': '15', 'offset': '0',
                       'count': '15', 'next_offset': 'done'}
            and len(rows) == 15 and len({r['name'] for r in rows}) == 15
            and {r['name'] for r in rows} == {r['name'] for r in request['harnesses']},
        'summary_complete_exact_identity_failed_gate':
            summary.startswith('# K-1 run `citrim-g2-20261105-02`: COMPLETE')
            and HEAD in summary and KANI in summary and request_hash in summary
            and 'gate: False; expectation met: False;' in summary and 'Kani exit 1' in summary,
        'cloud_failure_on_approved_source_standard4': status['id'] == BUILD
            and status['source_sha'] == HEAD and status['status'] == 'FAILURE'
            and status['pool'].endswith('/k1-standard4'),
        'tooling_exactly_eight_ok_bindings': len(tooling) == 8
            and all(line.startswith('ok   ') for line in tooling)
            and HEAD in '\n'.join(tooling),
        '2_success_13_timeout_no_other_result': len(completed) == 2 and len(timed_out) == 13,
        'completed_checks_success_and_exact_covers':
            all(r['checks_failed'] == 0 and r['covers_satisfied'] == r['covers_total']
                == expected[r['name']] for r in completed),
        'timeouts_not_misreported_as_complete_evidence':
            all(r['seconds'] is r['checks_failed'] is r['covers_total'] is None
                for r in rows if r['status'] == 'TIMEOUT'),
        'targeted_verify_warning_scan_no_matches':
            (E / 'verify-warning-paths.txt').read_text().strip() == '(no match)',
        'cost_two_completed_builds': n == '2' and Decimal(cost) == Decimal('2.2815')
            and Decimal(reserve) == 0,
    }
    assert all(checks.values()), checks
    report = {'evidence_consistency': 'PASS', 'task_acceptance': 'FAIL', 'checks': checks,
              'build_id': BUILD, 'source_sha': HEAD, 'request_id': request['request_id'],
              'request_sha256': request_hash, 'kani_commit': KANI, 'rows': rows,
              'success': len(completed), 'timeouts': timed_out,
              'within_120s': quick, 'success_over_120s': slow,
              'completed_covers_satisfied': sum(r['covers_satisfied'] for r in completed),
              'completed_covers_total': sum(r['covers_total'] for r in completed),
              'expected_all_covers': sum(expected.values()),
              'timeout_covers_unknown': sum(expected[n] for n in timed_out),
              'completed_verification_seconds_sum': str(sum(
                  Decimal(r['seconds_decimal']) for r in completed)),
              'whole_suite_seconds': None, 'cost_usd': str(Decimal(cost) - Decimal('1.1880')), 'two_builds_cost_usd': cost, 'reserved_usd': str(reserve),
              'inventory': 'NOT_REQUESTED',
              'limitations': '13 timeouts have no proof/cover/time completion evidence; '
                  'unreachable non-cover checks are not unreachable covers. No GCB/Actions '
                  'paired original-root timings available in inherited own reports. '
                  'Library still covers all original domains at source level, not proof acceptance.'}
    (E / 'verification-report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ('evidence_consistency', 'task_acceptance',
        'success', 'completed_covers_satisfied', 'expected_all_covers',
        'completed_verification_seconds_sum', 'cost_usd')}, indent=2))


if __name__ == '__main__':
    main()
