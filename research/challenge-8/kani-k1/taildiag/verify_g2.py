#!/usr/bin/env python3
"""Validate bounded G2 response identities and acceptance; no raw evidence or proof tools."""
import csv
import hashlib
import json
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
D = HERE / 'g2'
BUILD = 'a5a16595-8c2e-4bf8-80bd-b7627d775ca6'
SOURCE = '49420dda0b505d38d9bed8568ce602a4026b4ae4'
KANI = 'cd355b0bccd32300713bc2ce4f765dafa1510607'
HASH = 'c7652b3bf9c2b8abc8896b894c80c228b619a3087917d55131cdcf19d261fdf7'
request = json.loads((D / 'RUN-REQUEST.json').read_text())
assert hashlib.sha256((D / 'RUN-REQUEST.json').read_bytes()).hexdigest() == HASH
text = json.loads((D / 'rows-output.json').read_text())['text'].splitlines()
head = dict(line.split('=', 1) for line in text[:8])
assert head == dict(request_id=request['request_id'], request_sha256=HASH, build_id=BUILD,
                    head_sha=SOURCE, total='5', offset='0', count='5', next_offset='done')
rows = list(csv.DictReader(text[8:], delimiter='\t'))
assert [r['name'] for r in rows] == [r['name'] for r in request['harnesses']]
assert len(rows) == 5
lines = (D / 'peaks0.txt').read_text().splitlines()
assert 'process_records=5 offset=0 count=5 next_offset=done' in lines
assert 'dmesg_oom=none_seen' in lines and 'swap_total_bytes=0' in lines
records = [json.loads(line) for line in lines if line.startswith('{')]
assert len(records) == 5 and len({r['pid'] for r in records}) == 5
for r in records:
    assert (r['build_id'], r['head_sha'], r['kani_commit']) == (BUILD, SOURCE, KANI)
    assert r['attribution'] == r['metadata_resolution'] == 'direct'
    assert r['metadata_match_count'] == 1 and r['harness'] == r['direct_harness']
    assert r['harness'] in {x['name'] for x in rows} and r['cmd'] == 'cbmc'
summary = (D / 'summary.md').read_text()
assert all(x in summary for x in [BUILD, SOURCE, HASH, KANI, 'gate: False', 'Kani exit 1'])
status = json.loads((D / 'status.json').read_text())
assert status['id'] == BUILD and status['source_sha'] == SOURCE and status['status'] == 'FAILURE'
assert status['pool'].endswith('/k1-standard4') and status['timeout'] == '3000s'
tooling = (D / 'tooling.txt').read_text().splitlines()
assert len(tooling) == 8 and all(line.startswith('ok ') for line in tooling)
assert SOURCE in tooling[1] and '59893bff1fbb2af1a0c08862afd7e3bb87c19cdd' in tooling[1]
assert (D / 'budget-own-total.txt').read_text().strip() == '2 0.7695 0.0000'
for r in rows:
    r['time_s'] = None if r['time_s'] == 'None' else float(r['time_s'])
    cbmc = [p for p in records if p['harness'] == r['name']]
    assert len(cbmc) == 1
    r['cbmc_peak_kib'] = cbmc[0]['peak_kb']
    if r['status'] == 'SUCCESS':
        assert r['checks'] == '0/229' and r['covers'] == '5/5' and r['time_s'] <= 200
        assert r['name'].endswith('u64_backing17_tail8_to15_no_explicit_frame')
    else:
        assert 'insertion_stubbed_' in r['name'] and r['status'] == 'TIMEOUT'
        assert r['time_s'] is None and not r['checks'] and not r['covers']
consumers = [r for r in rows if 'insertion_stubbed_' in r['name']]
assert len(consumers) == 4
consumer_credit = all(r['status'] == 'SUCCESS' for r in consumers)
assert not consumer_credit and sum(r['status'] == 'SUCCESS' for r in rows) == 1
own_total = Decimal('0.7695')
g1_cost = Decimal('0.4185')
report = dict(validation='PASS', scope='Bounded evidence consistency; partial proof result',
              build_id=BUILD, source_sha=SOURCE, request_sha256=HASH, kani_commit=KANI,
              cloud_status='FAILURE', summary_status='COMPLETE', gate=False,
              summary_build_outcome='success', build_outcome_discrepancy_preserved=True,
              successes=1, timeouts=4, covers_reached_successes=5, covers_expected_all=25,
              successful_time_sum_s=sum(r['time_s'] or 0 for r in rows),
              own_build_cost_usd=float(own_total - g1_cost), own_total_cost_usd=float(own_total),
              own_reserved_usd=0, inventory='disabled; source-only counts',
              insert_tail_domain=dict(type='u64', allocation=17, start=0, tail=[1, 15],
                                      comparator='taildiag::arbitrary_less::<u64>'),
              insertion_len1_to16_credited=consumer_credit, insertion_consumers_successful=0,
              insertion_reason='All four matched consumers TIMEOUT; no new composition credit',
              rows=rows)
(D / 'verification-report.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({k: v for k, v in report.items() if k != 'rows'}, indent=2))
