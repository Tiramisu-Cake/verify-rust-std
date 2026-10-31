#!/usr/bin/env python3
"""Fail closed on INTEG2's approved identities, own budget and full time envelope."""
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
TREE = 'c522edd42ae67c385e1ee42a1c4d1bffb611c90b'
GO = 'e0ff82577dc58950621dadc9c141d88a5821987f'
BRANCH = 'experiment/kani-k1-integtwo-20261031'


def git(*args):
    return subprocess.check_output(['git', *args], text=True).strip()


def main():
    stage = sys.argv[1].lower()
    window = json.loads((HERE / 'window.json').read_text())
    ledger = json.loads((HERE / 'builds.json').read_text())
    go = json.loads((HERE / 'go.json').read_text())
    plan = next(p for p in ledger['planned'] if p['stage'].lower() == stage)
    assert int(stage[1:]) == len(ledger['builds']) + 1 <= 3
    assert go['reviewed_source'] == GO and go['frozen_library_tree'] == TREE
    assert window['go'] == 'COORDINATOR_GO_RECEIVED'
    sha = git('rev-parse', 'HEAD')
    assert git('branch', '--show-current') == BRANCH
    assert git('rev-parse', 'origin/' + BRANCH) == sha
    assert git('rev-parse', 'HEAD:library') == TREE
    assert not git('diff', GO, '--', 'library')
    raw = (HERE.parent / 'RUN-REQUEST.json').read_bytes()
    request = json.loads(raw)
    assert request['request_id'] == plan['request_id']
    assert raw == subprocess.check_output(['git', 'show', sha + ':research/challenge-8/kani-k1/RUN-REQUEST.json'])
    assert request['runner'] == 'gcb-e2-standard-4'
    if stage == 'g3':
        assert request['kind'] == 'measurement' and request['kani_jobs'] == 1
        assert request['controls'] and request['harness_timeout_minutes'] == 10
        expected = {
            'merge::general_stable_direct_value_corruption_control_u64_n2',
            'network::insert_tail_contract_u64_start1_prefix_frame_control',
            'network::insert_tail_contract_u64_start1_suffix_frame_control',
        }
        assert len(request['harnesses']) == 3
        assert {r['name'].split('::verify::')[1] for r in request['harnesses']} == expected
        assert all(r['expect'] == 'FAILED' and r['expect_check'] == 'This is a placeholder message'
                   for r in request['harnesses'])
        work = len(request['harnesses']) * request['harness_timeout_minutes']
    else:
        assert request['kind'] == 'inventory' and request['inventory']
        assert request['controls'] == (stage == 'g2') and not request['harnesses']
        assert request['harness_timeout_minutes'] == (30 if stage == 'g1' else 60)
        work = request['harness_timeout_minutes']
    envelope = work + 30
    reserve = Decimal(envelope) * Decimal('0.0135')
    assert envelope == plan['envelope_minutes'] and reserve == Decimal(str(plan['reserve_usd']))
    own_text = (HERE / ('own-budget-before-' + stage + '.txt')).read_text().split()
    assert len(own_text) == 3 and int(own_text[0]) == len(ledger['builds'])
    spent, reserved = map(Decimal, own_text[1:])
    assert all(v.is_finite() and v >= 0 for v in (spent, reserved))
    assert spent + reserved + reserve <= Decimal('2.90')
    global_text = (HERE / ('budget-before-' + stage + '.txt')).read_text()
    match = re.search(r'used \$([0-9.]+), reserved by unfinished builds \$([0-9.]+), cap \$([0-9.]+)', global_text)
    assert match, global_text
    global_used, global_reserved, cap = map(Decimal, match.groups())
    assert cap == Decimal('73.96') and global_used + global_reserved + reserve <= cap
    now = datetime.now(timezone.utc)
    remaining = (datetime.fromisoformat(window['deadline_utc']) - now).total_seconds() / 60
    closing = window['closing_reserve_minutes']
    assert closing == 30 and remaining >= envelope + closing
    report = dict(status='PASS',checked_at_utc=now.isoformat(),source_sha=sha,
        reviewed_source=GO,frozen_library_tree=TREE,stage=stage,request_id=request['request_id'],
        request_sha256=hashlib.sha256(raw).hexdigest(),own_previous_uuids=[b['uuid'] for b in ledger['builds']],
        own_spent_usd=float(spent),own_reserved_usd=float(reserved),next_reserve_usd=float(reserve),
        own_including_next_usd=float(spent+reserved+reserve),own_cap_usd=2.9,
        global_used_usd=float(global_used),global_reserved_usd=float(global_reserved),global_cap_usd=float(cap),
        remaining_window_minutes=round(remaining,3),work_minutes=work,setup_minutes=30,
        full_envelope_minutes=envelope,closing_reserve_minutes=closing)
    (HERE / (stage + '.preflight.json')).write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
