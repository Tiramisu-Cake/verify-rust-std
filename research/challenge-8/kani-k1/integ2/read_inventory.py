#!/usr/bin/env python3
"""Read approved bounded K-1 inventory pages, following each returned continuation."""
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ledger = json.loads((HERE / 'builds.json').read_text())
build = ledger['builds'][1]
reader = HERE.parent / 'tools/k1g.sh'
expected_path = HERE / 'scope/cfg-on.txt'
expected = expected_path.read_text().splitlines()
assert len(expected) == len(set(expected)) == 479
offset, names, pages, identities = 0, [], [], None
while True:
    output = subprocess.check_output([str(reader), 'inventory', build['uuid'], str(offset), '80'],
                                     text=True)
    filename = f'g2.inventory-{offset}.txt'
    (HERE / filename).write_text(output)
    lines = output.splitlines()
    fields = dict(line.split('=', 1) for line in lines[:11])
    part = lines[11:]
    for key, want in [('request_id', build['request_id']), ('request_sha256', build['request_sha256']),
                      ('build_id', build['uuid']), ('head_sha', build['source_sha']),
                      ('kani_commit', '9461e07af7ec929f050aa4192f29363c9be07779')]:
        assert fields[key] == want, (key, fields[key], want)
    assert int(fields['total']) == 479 and int(fields['offset']) == offset
    assert 0 < int(fields['count']) == len(part) <= 80
    identity = {k: v for k, v in fields.items() if k not in ('offset', 'count', 'next_offset')}
    if identities is None:
        identities = identity
    assert identities == identity, 'page identities changed'
    assert offset == len(names), 'noncontiguous coverage'
    names.extend(part)
    pages.append(dict(file=filename, offset=offset, count=len(part), next_offset=fields['next_offset']))
    print(json.dumps(pages[-1]), flush=True)
    if fields['next_offset'] == 'done':
        break
    next_offset = int(fields['next_offset'])
    assert next_offset == len(names) and next_offset > offset
    offset = next_offset
assert len(names) == 479
assert hashlib.sha256(('\n'.join(names) + '\n').encode()).hexdigest() == identities['names_sha256']
assert Counter(names) == Counter(expected), (set(expected)-set(names), set(names)-set(expected))
assert len(names) == len(set(names))
(HERE / 'g2.inventory-names.txt').write_text('\n'.join(names) + '\n')
report = dict(status='PASS_EXACT_479_NAME_SET', build=build['uuid'], source_sha=build['source_sha'],
    library_tree=build['library_tree'], controls=True, actual_count=len(names), expected_count=len(expected),
    duplicates=0, missing_names=[], unexpected_names=[], exact_name_set_equal=True, coverage_complete=True,
    pages=pages, bindings=identities, expected_file='scope/cfg-on.txt',
    expected_file_sha256=hashlib.sha256(expected_path.read_bytes()).hexdigest(),
    positive_verification_credit='None; enumeration only',
    memory_time_credit='Inventory summary fields MISSING; no performance claim',
    artifact_binding='K-1 reader checks inventory schema/count/hash against bound run summary on every page')
(HERE / 'g2.inventory-check.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(dict(status=report['status'], count=len(names), pages=len(pages))), flush=True)
