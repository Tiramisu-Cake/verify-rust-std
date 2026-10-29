"""Derive VALID-B metrics exclusively from bounded exported views."""
import csv
import hashlib
import json
import re
import statistics
from collections import Counter
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
SCOPE = BASE.parent / 'scope'
PREFIX = 'slice::sort::shared::smallsort::verify::'


def names(file):
    return file.read_text().splitlines()


def inventory(label):
    result = []
    pages = sorted((BASE / 'evidence').glob(label + '.*.inventory.page'))
    for p in pages:
        lines = p.read_text().splitlines()
        result.extend(x for x in lines if x.startswith(PREFIX))
    if not pages:
        return None
    metadata = dict(x.split('=', 1) for x in pages[0].read_text().splitlines() if '=' in x)
    assert len(result) == int(metadata['total'])
    assert hashlib.sha256(('\n'.join(result) + '\n').encode()).hexdigest() == metadata['names_sha256']
    expected = names(SCOPE / 'ordinary.txt')
    if label == 'controls':
        for f in ('extended-positive.txt', 'controls-failed.txt', 'deferred-unsupported.txt'):
            expected += names(SCOPE / f)
    a, b = Counter(result), Counter(expected)
    return dict(count=len(result), unique=len(a), missing=list((b-a).elements()),
                extra=list((a-b).elements()), names_sha256=metadata['names_sha256'])


def result_rows(label, directory=None):
    result = []
    for p in sorted((directory or BASE / 'evidence').glob(label + '.*.rows.tsv')):
        lines = p.read_text().splitlines()
        at = lines.index('name\tstatus\ttime_s\tchecks\tcovers')
        result += list(csv.DictReader(lines[at:], delimiter='\t'))
    return result


def aggregate(rows):
    vt = [float(r['time_s']) for r in rows if r['time_s'] not in ('', 'None')]
    return dict(rows=len(rows), counts=dict(Counter(r['status'] for r in rows)),
                sum_vt_s=sum(vt), vt_count=len(vt), max_vt_s=max(vt, default=None))


def main():
    data = {label: inventory(label) for label in ('ordinary', 'controls')}
    costs = []
    for p in sorted((BASE / 'evidence').glob('*.status.json')):
        s = json.loads(p.read_text())
        wall = (datetime.fromisoformat(s['finishTime'].replace('Z', '+00:00')) -
                datetime.fromisoformat(s['startTime'].replace('Z', '+00:00'))).total_seconds()
        import math
        costs.append(dict(label=p.name.split('.')[0], build_id=s['id'], sha=s['source_sha'],
                          wall_s=wall, usd=math.ceil(wall/60)*0.0135))
    data['builds'] = costs
    rows = result_rows('autoharness')
    if rows:
        ours = [r for r in rows if r['name'].startswith(PREFIX)]
        seen = Counter(r['name'] for r in ours)
        expected = names(SCOPE / 'ordinary.txt')
        per_name = {r['name']: r for r in ours}
        scope = {r['name']: r for r in csv.DictReader((SCOPE / 'scope.tsv').open(), delimiter='\t')}
        table = []
        ratios = []
        for n in expected:
            row = per_name.get(n, dict(name=n, status='NO_RESULT_ROW', time_s='', checks='', covers=''))
            mac = scope[n]['mac_vt_s']
            ratio = ''
            if row['status'] == 'SUCCESS' and row['time_s'] not in ('', 'None') and mac != 'UNKNOWN':
                ratio = float(mac) / float(row['time_s'])
                ratios.append(ratio)
            table.append(dict(row, mac_vt_s=mac, mac_over_gcb=ratio))
        with (BASE / 'per-harness.tsv').open('w') as f:
            w = csv.DictWriter(f, fieldnames=table[0].keys(), delimiter='\t', lineterminator='\n')
            w.writeheader(); w.writerows(table)
        data['autoharness'] = dict(all=aggregate(rows), smallsort=aggregate(ours),
            missing=[n for n in expected if n not in seen], extra=list((seen-Counter(expected)).elements()),
            duplicates={n:c for n,c in seen.items() if c > 1},
            c3a=[r for r in table if r['mac_vt_s'] == 'UNKNOWN'],
            matched_mac_ratio=dict(n=len(ratios), median=statistics.median(ratios) if ratios else None,
                                   min=min(ratios, default=None), max=max(ratios, default=None)))
        known = [r for r in table if r['mac_vt_s'] != 'UNKNOWN']
        data['autoharness']['matched_mac_ratio']['sum_mac_over_sum_gcb'] = (
            sum(float(r['mac_vt_s']) for r in known) / sum(float(r['time_s']) for r in known))
        data['autoharness']['over_120'] = sum(float(r['time_s']) > 120 for r in table)
        data['autoharness']['over_300'] = [r['name'] for r in table if float(r['time_s']) > 300]
        function_summary = (BASE / 'evidence/autoharness.function-summary.txt').read_text()
        m = re.search(r'Complete - (\d+) successfully verified functions, (\d+) failures, (\d+) total\.', function_summary)
        assert m
        success, failures, total = map(int, m.groups())
        assert success + failures == total
        data['autoharness']['automatic_functions_source_summary'] = dict(success=success, failures=failures, total=total,
            source='evidence/autoharness.function-summary.txt', verification_time='NOT_EXPORTED_BY_LANE_PARSER')
        data['autoharness']['non_success'] = [r for r in rows if r['status'] != 'SUCCESS']
        data['c3c_historical'] = aggregate(result_rows('autoharness', BASE.parent / 'c3c/evidence'))
    (BASE / 'metrics.json').write_text(json.dumps(data, indent=2) + '\n')
    print(json.dumps(data, indent=2))


if __name__ == '__main__':
    main()
