#!/usr/bin/env python3
"""Bind a successful dispatch UUID to its published request and frozen library."""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
stage = sys.argv[1].lower()
uuid = (HERE / (stage + '.dispatch.txt')).read_text().strip()
assert re.fullmatch(r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}', uuid), uuid
preflight = json.loads((HERE / (stage + '.preflight.json')).read_text())
assert preflight['status'] == 'PASS'
ledger = json.loads((HERE / 'builds.json').read_text())
assert int(stage[1:]) == len(ledger['builds']) + 1 <= 3
assert not any(b['uuid'] == uuid for b in ledger['builds'])
entry = dict(label=stage,uuid=uuid,request_id=preflight['request_id'],
    source_sha=preflight['source_sha'],request_sha256=preflight['request_sha256'],
    library_tree=preflight['frozen_library_tree'],kind='measurement' if stage == 'g3' else 'inventory',
    controls=stage != 'g1',work_minutes=preflight['work_minutes'],
    total_envelope_minutes=preflight['full_envelope_minutes'],
    max_reserved_usd=preflight['next_reserve_usd'],status='SUBMITTED',
    submitted_recorded_at_utc=datetime.now(timezone.utc).isoformat())
if stage == 'g3':
    entry.update(kani_jobs=1,harness_count=3,harness_timeout_minutes=10)
ledger['builds'].append(entry)
ledger.update(status='SUBMITTED_AWAITING_RESULTS',spent_usd=preflight['own_spent_usd'],
    reserved_usd=round(preflight['own_reserved_usd']+preflight['next_reserve_usd'],4),
    reviewed_source=preflight['reviewed_source'],library_tree=preflight['frozen_library_tree'],
    accounting='Per-dispatch selected UUID budget snapshots; actual costs await terminal selected-UUID ledger')
(HERE / 'builds.json').write_text(json.dumps(ledger,indent=2)+'\n')
window=json.loads((HERE / 'window.json').read_text())
window['builds_submitted']=len(ledger['builds'])
(HERE / 'window.json').write_text(json.dumps(window,indent=2)+'\n')
print(json.dumps(entry,indent=2))
