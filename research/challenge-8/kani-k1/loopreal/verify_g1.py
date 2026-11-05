#!/usr/bin/env python3
"""Validate captured bounded G1 responses; no compiler, raw evidence or dispatch."""
import hashlib
import json
from decimal import Decimal
from pathlib import Path

PACKET = Path(__file__).resolve().parent
E = PACKET / 'evidence'
BUILD = '69ac5245-e83e-4d87-b8b6-68acd46b0e02'
SOURCE = '3a1a71036fc48708094c59e3b1c70252ce4fbf9b'
KANI = 'cd355b0bccd32300713bc2ce4f765dafa1510607'


def main():
    request_bytes = (E/'g1-request.json').read_bytes()
    request = json.loads(request_bytes)
    request_hash = hashlib.sha256(request_bytes).hexdigest()
    assert request_hash == '8af5df8cdad82e52c3851d4caab263beb11a291ef437319feea9e2e94d9a5081'
    status = json.loads((E/'status.json').read_text())
    assert status['id'] == BUILD and status['source_sha'] == SOURCE
    assert status['status'] == 'FAILURE' and status['timeout'] == '4680s'
    assert status['pool'].endswith('/workerPools/k1-standard4')
    summary = (E/'summary.md').read_text()
    assert all(s in summary for s in [BUILD, SOURCE, KANI, request_hash, request['request_id']])
    assert ': COMPILE_ERROR' in summary and 'gate: False; expectation met: False' in summary
    assert 'Kani exit 1' in summary and '5 previous errors' in summary
    assert summary.count('error[E0382]') == 5
    assert 'borrow of moved value' in summary
    rows_bytes = (E/'rows.txt').read_bytes()
    lines = rows_bytes.decode().splitlines()
    headers = dict(line.split('=', 1) for line in lines[:8])
    assert headers == {'request_id': request['request_id'], 'request_sha256': request_hash,
                       'build_id': BUILD, 'head_sha': SOURCE, 'total': '12',
                       'offset': '0', 'count': '12', 'next_offset': 'done'}
    assert lines[8] == 'name\tstatus\ttime_s\tchecks\tcovers'
    rows = {}
    for line in lines[9:]:
        name, outcome, seconds, checks, covers = line.split('\t')
        assert outcome == 'NOT_RUN' and seconds == checks == covers == ''
        assert name not in rows
        rows[name] = {'status': outcome, 'time_s': None, 'checks': None,
                      'covers': None, 'cbmc_peak_rss_kib': None}
    assert len(rows) == 12 and set(rows) == {h['name'] for h in request['harnesses']}
    tooling = (E/'tooling.txt').read_text().splitlines()
    assert len(tooling) == 8 and all(line.startswith('ok ') for line in tooling)
    assert SOURCE in tooling[1] and '59893bff1fbb2af1a0c08862afd7e3bb87c19cdd' in tooling[1]
    peaks = (E/'peaks0.txt').read_text()
    assert 'process_records=0 offset=0 count=0 next_offset=done' in peaks
    assert 'cmd=cbmc ' not in peaks
    assert 'cmd=kani-compiler peak_kb=1278800 ' in peaks
    assert 'dmesg_oom=none_seen' in peaks
    assert 'max RSS 1290476 KiB, wall 0:43.20' in summary
    n, spent, reserved = (E/'cost.txt').read_text().split()
    assert n == '1' and Decimal(spent) == Decimal('0.1080') and Decimal(reserved) == 0
    diagnostics = (E/'compile-diagnostics.txt').read_text()
    assert diagnostics.count('error[E0382]') == 5
    assert 'defaulting to `2015`' in diagnostics  # manifest warning, not proof evidence
    report = {
        'verdict': 'COMPILE_ERROR_NO_PROOF_CREDIT', 'build_id': BUILD, 'source_sha': SOURCE,
        'request_id': request['request_id'], 'request_sha256': request_hash, 'kani_commit': KANI,
        'cloud_status': 'FAILURE', 'summary_status': 'COMPILE_ERROR', 'kani_exit': 1,
        'tooling_bindings': 'PASS', 'rows': rows, 'not_run_count': 12,
        'compiler_error': 'Five E0382 diagnostics: loop_modifies moves &mut F is_less in the two real functions and the false cfg-copy.',
        'invariant_checks_observed': False, 'negative_control_established': False,
        'verification_wall_s': '43.20', 'time_v_max_rss_kib': 1290476,
        'sampled_compiler_peak_rss_kib': 1278800, 'per_harness_cbmc_records': 0,
        'spent_usd': spent, 'reserved_usd': reserved,
        'metadata_discrepancy': 'Summary run text says build success; bounded Cloud status says FAILURE. Preserve both; use Cloud FAILURE and summary COMPILE_ERROR, not successful verification.',
        'rows_capture_sha256': hashlib.sha256(rows_bytes).hexdigest(),
        'capture_note': 'rows.txt preserves empty TSV time/check/cover fields as trailing tabs; exempt this data capture alone from end-of-line whitespace checks.',
        'scope': 'Bounded response consistency only, not independent verifier execution. No invariant, length-cost, ZST, ordinary regression or arbitrary-length proof credit.',
    }
    (E/'verification-report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'rows'}, indent=2))


if __name__ == '__main__':
    main()
