#!/usr/bin/env python3
"""Validate only bounded k1g outputs; never read raw logs or evidence archives."""
import csv
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
D = HERE / 'g1'
BUILD = '34500433-bd3d-4784-9a26-aaf0ba3f0492'
SOURCE = '1c99acce330d708961571bd593ecc322768f690f'
KANI = 'cd355b0bccd32300713bc2ce4f765dafa1510607'
HASH = 'ccc22fb30ac75edd682dee2aca2b175fcdc977c23c017a85802d8f0ff3037296'
request = json.loads((D / 'RUN-REQUEST.json').read_text())
assert hashlib.sha256((D / 'RUN-REQUEST.json').read_bytes()).hexdigest() == HASH
text = json.loads((D / 'rows-output.json').read_text())['text'].splitlines()
head = dict(line.split('=', 1) for line in text[:8])
assert head == dict(request_id=request['request_id'], request_sha256=HASH, build_id=BUILD,
                    head_sha=SOURCE, total='10', offset='0', count='10', next_offset='done')
rows = list(csv.DictReader(text[8:], delimiter='\t'))
assert [r['name'] for r in rows] == [r['name'] for r in request['harnesses']]
assert len(rows) == 10
records = []
for filename, position in [('peaks0.txt', 'offset=0 count=8 next_offset=8'),
                           ('peaks8.txt', 'offset=8 count=5 next_offset=done')]:
    lines = (D / filename).read_text().splitlines()
    assert f'process_records=13 {position}' in lines
    records += [json.loads(line) for line in lines if line.startswith('{')]
assert len(records) == 13 and len({r['pid'] for r in records}) == 13
for r in records:
    assert (r['build_id'], r['head_sha'], r['kani_commit']) == (BUILD, SOURCE, KANI)
    assert r['attribution'] == r['metadata_resolution'] == 'direct'
    assert r['metadata_match_count'] == 1 and r['harness'] == r['direct_harness']
    assert r['harness'] in {x['name'] for x in rows}
summary = (D / 'summary.md').read_text()
assert all(x in summary for x in [BUILD, SOURCE, HASH, KANI, 'gate: False', 'Kani exit 1'])
status = json.loads((D / 'status.json').read_text())
assert status['id'] == BUILD and status['source_sha'] == SOURCE and status['status'] == 'FAILURE'
assert status['pool'].endswith('/k1-standard4') and status['timeout'] == '4200s'
tooling = (D / 'tooling.txt').read_text().splitlines()
assert len(tooling) == 8 and all(line.startswith('ok ') for line in tooling)
assert SOURCE in tooling[1] and '59893bff1fbb2af1a0c08862afd7e3bb87c19cdd' in tooling[1]
assert (D / 'budget-own.txt').read_text().strip() == '1 0.4185 0.0000'
for r in rows:
    r['time_s'] = None if r['time_s'] == 'None' else float(r['time_s'])
    cbmc = [p for p in records if p['harness'] == r['name'] and p['cmd'] == 'cbmc']
    assert len(cbmc) == 1
    r['cbmc_peak_kib'] = cbmc[0]['peak_kb']
    if r['status'] == 'SUCCESS':
        assert r['checks'] == '0/229' and r['covers'] == '5/5' and r['time_s'] <= 200
    else:
        assert r['name'].endswith('tail1_to7_value_order') and r['status'] == 'TIMEOUT'
        assert r['time_s'] is None and not r['checks'] and not r['covers']
assert sum(r['status'] == 'SUCCESS' for r in rows) == 9
report = dict(validation='PASS', scope='Bounded K-1 evidence; no universal proof credit',
              build_id=BUILD, source_sha=SOURCE, request_sha256=HASH, kani_commit=KANI,
              cloud_status='FAILURE', summary_status='COMPLETE', gate=False,
              summary_build_outcome='success', build_outcome_discrepancy_preserved=True,
              successes=9, timeouts=1, covers_reached_successes=45, covers_expected_all=50,
              successful_time_sum_s=sum(r['time_s'] or 0 for r in rows),
              maximum_verification_s=max(r['time_s'] or 0 for r in rows),
              own_cost_usd=0.4185, own_reserved_usd=0, inventory='disabled; source-only counts',
              insert_tail_domain=dict(type='u64', allocation=17, start=0, tail=[1, 15],
                                      comparator='taildiag::arbitrary_less::<u64>'),
              insertion_consumer='not run; G2 proposed', rows=rows)
(D / 'verification-report.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({k: v for k, v in report.items() if k != 'rows'}, indent=2))
