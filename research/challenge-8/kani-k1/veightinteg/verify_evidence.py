#!/usr/bin/env python3
"""Validate only saved bounded k1g reports; never reads cached/raw logs or runs proof tools."""
import hashlib
import json
import subprocess
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE / 'evidence'
PREFIX = 'slice::sort::shared::smallsort::verify::'
BUILD = '03d45e6a-0553-414e-83ea-6f6c9ce87778'
HEAD = '91aeee2c62c3fc1e665fa7a44a5787c8283e54ab'
KANI = 'cd355b0bccd32300713bc2ce4f765dafa1510607'


def read_page(name):
    fields, names = {}, []
    for line in (EVIDENCE / name).read_text().splitlines():
        if line.startswith(PREFIX):
            names.append(line)
        elif '=' in line:
            key, value = line.split('=', 1)
            fields[key] = value
    return fields, names


def main():
    request_path = HERE.parent / 'RUN-REQUEST.json'
    request = json.loads(request_path.read_text())
    request_sha = hashlib.sha256(request_path.read_bytes()).hexdigest()
    bindings = {'request_id': request['request_id'], 'request_sha256': request_sha,
                'build_id': BUILD, 'head_sha': HEAD}
    summary = (EVIDENCE / 'summary.md').read_text()
    row_header, raw_rows = read_page('rows.txt')
    rows = []
    for raw in raw_rows:
        name, status, seconds, checks, covers = raw.split('\t')
        failed, total = map(int, checks.split('/'))
        reached, cover_total = map(int, covers.split('/'))
        rows.append({'name': name, 'status': status, 'seconds': float(seconds),
                     'seconds_decimal': seconds, 'checks_failed': failed, 'checks_total': total,
                     'covers_satisfied': reached, 'covers_total': cover_total})
    names, page_headers, continuation_ok = [], [], True
    next_offset = '0'
    for file in ('inventory0.txt', 'inventory80.txt', 'inventory160.txt'):
        h, page = read_page(file)
        continuation_ok &= h['offset'] == next_offset and int(h['count']) == len(page)
        continuation_ok &= all(h.get(k) == v for k, v in {**bindings, 'kani_commit': KANI}.items())
        page_headers.append(h)
        names.extend(page)
        next_offset = h['next_offset']
    continuation_ok &= next_offset == 'done'
    continuation_ok &= all(h['total'] == '219' for h in page_headers)
    continuation_ok &= all(h['inventory_sha256'] == page_headers[0]['inventory_sha256']
                           and h['names_sha256'] == page_headers[0]['names_sha256']
                           for h in page_headers)
    expected_names = HERE.joinpath('ordinary-expected.txt').read_text().splitlines()
    old_names = (HERE.parent / 'codefix/ordinary-expected.txt').read_text().splitlines()
    new_names = HERE.joinpath('new-ordinary.txt').read_text().splitlines()
    opt_in = set(HERE.joinpath('opt-in-expected.txt').read_text().splitlines())
    expected_covers = json.loads(HERE.joinpath('expected-covers.json').read_text())
    static = json.loads(HERE.joinpath('check-report.json').read_text())
    status = json.loads(EVIDENCE.joinpath('status.json').read_text())
    tooling = EVIDENCE.joinpath('tooling.txt').read_text()
    budget_count, cost, reserved = EVIDENCE.joinpath('budget.txt').read_text().split()
    seconds_sum = sum(Decimal(row['seconds_decimal']) for row in rows)
    max_seconds = max(row['seconds'] for row in rows)
    covers_satisfied = sum(row['covers_satisfied'] for row in rows)
    covers_total = sum(row['covers_total'] for row in rows)
    checks = {
        'cloud_success_exact_source_pool': status['id'] == BUILD
            and status['source_sha'] == HEAD and status['status'] == 'SUCCESS'
            and status['pool'].endswith('/k1-standard4'),
        'row_bindings_and_complete_page': all(row_header.get(k) == v for k, v in bindings.items())
            and row_header['total'] == row_header['count'] == '15'
            and row_header['offset'] == '0' and row_header['next_offset'] == 'done',
        'all_15_new_roots_success_without_failed_checks': len(rows) == 15
            and {row['name'] for row in rows} == set(new_names)
            and all(row['status'] == 'SUCCESS' and row['checks_failed'] == 0 for row in rows),
        'all_55_covers_reached_exact_expected_totals': covers_satisfied == covers_total == 55
            and set(expected_covers) == set(new_names)
            and all(row['covers_satisfied'] == row['covers_total']
                    == expected_covers[row['name']]['covers_total'] for row in rows),
        'each_new_root_within_60_seconds': max_seconds <= 60,
        'gate_and_expectations_met_kani_exit_zero': summary.startswith(
            '# K-1 run `veightinteg-g1-20261105-02`: COMPLETE')
            and 'gate: True; expectation met: True;' in summary and 'Kani exit 0' in summary
            and HEAD in summary and KANI in summary and request_sha in summary,
        'inventory_bindings_and_continuations': continuation_ok,
        'inventory_names_hash': hashlib.sha256(('\n'.join(names) + '\n').encode()).hexdigest()
            == page_headers[0]['names_sha256'],
        'inventory_exact_219_ordinary': len(names) == len(set(names)) == 219
            and set(names) == set(expected_names),
        'inventory_delta_exact_15_and_no_opt_in': set(names) - set(old_names) == set(new_names)
            and not set(old_names) - set(names) and not set(names) & opt_in,
        'build_bound_tooling_all_eight_checks_pass': len(tooling.splitlines()) == 8
            and all(line.startswith('ok   ') for line in tooling.splitlines())
            and HEAD in tooling and static['tooling_base'] in tooling,
        'library_identical_to_build': not subprocess.check_output(
            ['git', 'diff', '--name-only', HEAD, '--', 'library'], text=True).strip(),
        'static_report_pass_and_request_coverage_bindings': static['status'] == 'PASS'
            and all(static['checks'].values()) and static['request_sha256'] == request_sha
            and static['expected_covers_sha256'] == hashlib.sha256(
                HERE.joinpath('expected-covers.json').read_bytes()).hexdigest(),
        'targeted_verify_unused_warning_scan_no_matches':
            EVIDENCE.joinpath('verify-warning-paths.txt').read_text().strip() == '(no match)',
        'single_build_cost_within_own_cap_no_reservation': budget_count == '1'
            and Decimal(cost) <= Decimal('3.00') and Decimal(reserved) == 0,
    }
    report = {
        'status': 'PASS' if all(checks.values()) else 'FAIL', 'checks': checks,
        'build_id': BUILD, 'source_sha': HEAD, 'request_id': request['request_id'],
        'request_sha256': request_sha, 'kani_commit': KANI,
        'inventory_sha256': page_headers[0]['inventory_sha256'],
        'inventory_names_sha256': page_headers[0]['names_sha256'],
        'inventory_count': len(names), 'ordinary_before': len(old_names),
        'added_vs_v8': sorted(set(names) - set(old_names)),
        'removed_vs_v8': sorted(set(old_names) - set(names)),
        'covers_satisfied': covers_satisfied, 'covers_total': covers_total,
        'unreached_covers': covers_total - covers_satisfied,
        'harness_seconds_sum': str(seconds_sum), 'max_harness_seconds': max_seconds,
        'prior_source_reported_ci_seconds_sum': static['prior_ci_seconds_sum'],
        'rows': rows, 'cost_usd': float(cost), 'reserved_usd': float(reserved),
        'builds': 1, 'repairs': 0, 'cloud_status': status,
        'proof_scope': 'Bounded diagnostic of 15 new ordinary roots, not a full-suite rerun. '
            'The previous 204 roots and 34 opt-in roots were not reverified here. '
            'All 55 covers were reached; summary unreachable check counts are other checks, '
            'not unreachable covers. Original callback/panic cover variants remain opt-in. '
            'Comparator/PFC domains, tag transfer assumption and panic cutoff limits unchanged.',
        'warning_scope': 'Targeted bounded scan found no SmallSort verify/unused-import/dead-code '
            'matches. General warning scan is a capped sample '
            '(manifest/unstable-feature warnings).',
    }
    EVIDENCE.joinpath('verification-report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ('status', 'checks', 'covers_satisfied', 'covers_total',
          'harness_seconds_sum', 'max_harness_seconds', 'inventory_count', 'cost_usd')}, indent=2))
    return int(report['status'] != 'PASS')


if __name__ == '__main__':
    raise SystemExit(main())
