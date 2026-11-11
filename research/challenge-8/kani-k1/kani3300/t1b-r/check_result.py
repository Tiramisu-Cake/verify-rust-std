"""Validate bounded reader receipts and close the single authorized A2; no external operations."""
from pathlib import Path
import datetime
import hashlib
import json
import re
from decimal import Decimal

HERE = Path(__file__).resolve().parent
EV = HERE/'evidence/cbf4045a'
BUILD = 'cbf4045a-cf4b-4ac7-8495-dfafcf57f6fb'
HEAD = 'bddfa044cbb4e884f9140b51c0cc0b9dfc464e58'

def read(path):
    return json.loads(path.read_text())

def write(path, value):
    path.write_text(json.dumps(value, indent=2)+'\n')

def sha(data):
    return hashlib.sha256(data).hexdigest()

def main():
    request = read(HERE/'RUN-REQUEST-A2.json')
    summary = (EV/'summary.md').read_text()
    lines = (EV/'rows.txt').read_text().splitlines()
    rows = []
    for line in lines[9:]:
        name, status, seconds, checks, covers = line.split('\t')
        fail, total = map(int, checks.split('/'))
        cs, ct = map(int, covers.split('/'))
        rows.append(dict(name=name, status=status, time_s=float(seconds), checks_failed=fail,
                         checks_total=total, covers_satisfied=cs, covers_total=ct))
    assert len(rows) == 9
    assert [r['name'] for r in rows] == [r['name'] for r in request['harnesses']]
    request_sha = sha((HERE/'RUN-REQUEST-A2.json').read_bytes())
    assert 'request_sha256='+request_sha in lines and 'head_sha='+HEAD in lines
    assert 'build_id='+BUILD in lines and 'total=9' in lines and 'next_offset=done' in lines
    baseline = read(HERE.parent/'t1a/HARNESS-OUTCOMES.json')['roots']
    keys = ('name','status','checks_failed','checks_total','covers_satisfied','covers_total')
    assert all(all(a[k] == b[k] for k in keys) for a,b in zip(rows,baseline))
    binding = read(HERE/'PATCH-BINDING.json')
    assert binding['expected_applied_tree'] in summary and binding['combined_patch_sha256'] in summary
    expected_tools = read(HERE.parent/'t1b/TOOLING-FILES.json')
    expected_tools.update(read(HERE.parent/'t1b/TOOLING-BINDING.json')['recipe_files'])
    reported = re.findall(r'^- `([^`]+)` ([0-9a-f]{64})$', summary, re.M)
    checked_tools = {name: digest for name,digest in reported if name in expected_tools}
    assert len(checked_tools) == 7
    assert all(expected_tools[name] == digest for name,digest in checked_tools.items())
    assert (EV/'budget.txt').read_text().strip() == '1 0.1215 0.0000'
    cumulative = Decimal('0.0810') + Decimal('0.1215')
    remaining = Decimal('0.80') - cumulative
    withheld = 'page-trace-field: diagnostic trace state INVALID; pages withheld'
    assert (EV/'trace-state.txt').read_text().strip() == withheld
    for field in ('complete','omitted','records'):
        assert read(EV/f'trace-{field}.receipt.json')['exit'] == 2
        assert (EV/f'trace-{field}.stderr.txt').read_text().strip() == withheld
    assert len((HERE/'RESULT-KANI3300-T1B-A2.md').read_text().splitlines()) <= 40
    obs = dict(build_id=BUILD, cloud_status='FAILURE', cloud_status_source='k1g watch terminal event, wait exit0, delivery attempt1',
               dispatch_head=HEAD, request_sha256=request_sha, classification='PROOF_EXECUTED_ORIGINAL_FAILURE_REPRODUCED_TRACE_INVALID',
               kani_build='SUCCESS', kani_build_seconds=252, kani_exit=1, gate=False, roots=rows,
               baseline_T1a_verdict_check_cover_counts_match=True,
               diagnostic_trace=dict(state='INVALID', source='Official trace-field identity guard', complete=None, omitted=None,
                   key_records=None, key_roots=[request['harnesses'][i]['name'] for i in (0,7,8)], reader_exit=2, reader_error=withheld,
                   attempted_paths=['state','complete','omitted','records'], invalid_reason='UNKNOWN; all pages withheld; no guard bypass'),
               identities=dict(head_request_patch_applied_tree='MATCH via bounded summary and rows',
                   reported_tooling_hashes_match=checked_tools, actual_applied_tree=binding['expected_applied_tree'],
                   full_producer_identity='UNKNOWN due INVALID trace'),
               cost=dict(A2_spent_usd='0.1215', terminal_reserved_usd='0.0000', initial_reserve_usd='0.648', prior_A_spent_usd='0.0810',
                   cumulative_spent_usd=str(cumulative), stage_cap_usd='0.80', remaining_usd=str(remaining),
                   source='k1g.sh budget BUILD; coordinator rounded pool ledger, not independent billing audit'),
               brief=dict(exit=1, error='Reader report or query route is unavailable (HTTP 404)'),
               assurance='Bounded source-reported diagnostic evidence; no independent B1/B2 credit', B_run=False, retry=False,
               runtime_causality='UNKNOWN', proof_credit='NONE')
    write(HERE/'A2-OBSERVATIONS.json', obs)
    queries = [dict(command=['smallsort-brief',BUILD], exit=1, receipt='brief-error.txt'),
               dict(command=['k1g.sh','summary',BUILD], exit=0, receipt='summary.md'),
               dict(command=['k1g.sh','summary',BUILD,'0','9'], exit=0, receipt='rows.txt'),
               dict(command=['k1g.sh','budget',BUILD], exit=0, receipt='budget.txt'),
               dict(command=['k1g.sh','trace-field',BUILD,'state','0','1'], exit=2, receipt='trace-state.txt')]
    for field in ('complete','omitted','records'):
        queries.append(dict(read(EV/f'trace-{field}.receipt.json'), stdout=f'trace-{field}.stdout.txt', stderr=f'trace-{field}.stderr.txt'))
    files = [dict(path=str(p.relative_to(HERE)), bytes=p.stat().st_size, sha256=sha(p.read_bytes())) for p in sorted(EV.iterdir()) if p.is_file()]
    write(HERE/'A2-EVIDENCE-INDEX.json', dict(build_id=BUILD, captured_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
          assurance='Only bounded official reader outputs; Brief unavailable; no raw fallback', queries=queries, files=files))
    cp = read(HERE/'CHECKPOINT.json')
    cp.update(state='COMPLETE_A2_ORIGINAL_FAILURE_TRACE_INVALID', compilation='SUCCESS_CLOUD_SOURCE_REPORTED',
              D_warnings='NOT_INDEPENDENTLY_ESTABLISHED', cloud_this_stage_usd='0.1215', submitted_reserve_usd='0.0000',
              remaining_cap_usd=str(remaining), cumulative_A_A2_spend_usd=str(cumulative), proof_credit='NONE',
              result='RESULT-KANI3300-T1B-A2.md', observations='A2-OBSERVATIONS.json', evidence='A2-EVIDENCE-INDEX.json',
              stop_boundary='One authorized A2 completed and analyzed; original verdicts reproduced, trace INVALID; no B/retry/repair authorized.')
    cp['watcher'].update(state='TERMINAL_EVENT_RECEIVED_AND_HANDLED', reported_status='FAILURE', wait_exit=0, delivery_attempt=1)
    cp['open'] = ['diagnostic_trace INVALID; all trace-field pages withheld, complete/omitted/key records and INVALID cause UNKNOWN',
                  'KANI3300 mechanism/concrete object/offset/R/runtime causality UNKNOWN; no independent proof credit']
    write(HERE/'CHECKPOINT.json', cp)
    print('PASS: 9 roots/T1a counts, identities, 7 reported tooling hashes, cost, withheld receipts and <=40-line result')

if __name__ == '__main__':
    main()
