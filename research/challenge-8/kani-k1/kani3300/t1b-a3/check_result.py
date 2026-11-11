"""Validate bounded A3 reader responses and derive source-reported observations only."""
import collections
import hashlib
import json
import subprocess
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE / 'evidence/35308c57'
BUILD = '35308c57-41d6-4057-943d-c55eb28642ad'
HEAD = 'f2990957c8199fea4600b6123ebaeb0a917df775'
REQUEST = '5b82ada544e8eced4e72a10e4e22c8b71eef892bde4aed34f9309d74e9a414bd'


def load(label):
    return json.loads((EVIDENCE / (label + '.stdout.txt')).read_text())


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    receipts = []
    for path in sorted(EVIDENCE.glob('*.receipt.json')):
        receipt = json.loads(path.read_text())
        for stream in ('stdout', 'stderr'):
            raw = (EVIDENCE / receipt[stream + '_file']).read_bytes()
            assert len(raw) == receipt[stream + '_bytes']
            assert sha(raw) == receipt[stream + '_sha256']
        assert receipt['exit'] == (1 if path.name == 'brief.receipt.json' else 0)
        receipts.append({'file': str(path.relative_to(HERE)), 'sha256': sha(path.read_bytes()),
                         **receipt})
    identity = load('identity')['value']
    assert (identity['build_id'], identity['head_sha'], identity['request_sha256']) == (BUILD, HEAD, REQUEST)
    expected = json.loads((HERE / 'EFFECTIVE-INVOCATION.json').read_text())
    assert identity['effective_argv'] == expected['runner_argv'] and identity['effective_env'] == expected['env']
    assert identity['applied_tree'] == identity['expected_applied_tree'] == '53927d9bc0ccbff8183aa91ffb6c29d1c8a74465'
    assert identity['actual_library_tree'] == identity['library_tree'] == '919cc3e2dc5fb19ea6e7f7be761914b949160a41'
    assert identity['base_pin'] == identity['kani_commit'] == 'f046b70644e113be0df9c22c2e6ea44a65a57566'
    assert identity['patch_sha256'] == '0e1dd370789a196cf7f7eadad4fe850910f83fd38cbf6e306394c6c247588298'
    for name, digest in identity['tooling_sha256'].items():
        assert sha(subprocess.check_output(['git', 'show', f'{HEAD}:{name}'])) == digest
    pages = sorted(EVIDENCE.glob('records-*.stdout.txt'), key=lambda p: int(p.name.split('-')[1].split('.')[0]))
    cursor = 0
    rows = []
    row_files = {}
    for index, path in enumerate(pages):
        page = json.loads(path.read_text())
        assert page['identity'] == identity and page['build_id'] == BUILD
        assert page['state'] == 'OVERSIZED' and page['trace_complete'] is False
        assert page['start'] == cursor and len(page['records']) <= 20 and path.stat().st_size <= 12000
        for row in page['records']:
            row_files[row['seq']] = path.name
        rows.extend(page['records'])
        cursor += len(page['records'])
        assert page['omitted'] == 374 - cursor
        if index < len(pages) - 1:
            assert page['next_start'] == cursor and page['complete'] is False
        else:
            assert page['next_start'] is None and page['complete'] is True
    assert len(rows) == 374 and [r['seq'] for r in rows] == list(range(1, 375))
    coverage = load('coverage')['records'][0]
    assert dict(collections.Counter(r['kind'] for r in rows)) == coverage['coverage']
    footer = load('footers')['records'][0]
    sidecar = load('sidecars')['records'][0]
    assert footer['sidecar_sha256'] == sidecar['sha256'] == 'd6046f88c19e54f9efdaf329648c6cdcc5da36045bd8bbb7be3caf910fbb46e4'
    assert footer['status'] == 'UNVALIDATED' and not footer['malformed_fields']
    assert footer['data']['state'] == coverage['state'] == 'OVERSIZED'
    for source, target in [('seen_records', 'seen'), ('emitted_records', 'emitted'), ('omitted_records', 'omitted'),
                           ('coverage', 'coverage'), ('omission_counts', 'omission_counts')]:
        assert footer['data'][source] == coverage[target]
    assert (coverage['seen'], coverage['emitted'], coverage['omitted']) == (929, 374, 555)
    assert load('omitted')['value'] == 555 and load('state')['value'] == 'OVERSIZED'
    assert load('errors')['records'] == []
    index_header = (EVIDENCE / 'rows.stdout.txt').read_text().splitlines()
    assert f'build_id={BUILD}' in index_header and f'head_sha={HEAD}' in index_header
    assert f'request_sha256={REQUEST}' in index_header and 'next_offset=done' in index_header
    roots = []
    for line in index_header[index_header.index('name\tstatus\ttime_s\tchecks\tcovers') + 1:]:
        if not line:
            continue
        name, status, seconds, checks, covers = line.split('\t')
        failed, total = map(int, checks.split('/')); satisfied, cover_total = map(int, covers.split('/'))
        roots.append(dict(name=name, status=status, time_s=float(seconds), checks_failed=failed,
                          checks_total=total, covers_satisfied=satisfied, covers_total=cover_total))
    old = json.loads((HERE.parent / 't1b-r/A2-OBSERVATIONS.json').read_text())['roots']
    assert len(roots) == len(old) == 9
    for a3, a2 in zip(roots, old):
        assert {k: v for k, v in a3.items() if k != 'time_s'} == {k: v for k, v in a2.items() if k != 'time_s'}
    key_roots = ['cmp3_index_range_len', 'cmp3_manually_drop_unsized_len',
                 'pincheck_calibration_init_read_u8', 'pincheck_calibration_uninit_read_u8']
    def ref(row):
        return {'seq': row['seq'], 'file': row_files[row['seq']], 'context': row['context'], 'data': row['data']}
    keys = {}
    for root in key_roots:
        selected = [r for r in rows if r['context']['root'].endswith('::' + root)]
        keys[root] = {
            'assurance': 'Retained source observations only; omitted events unknown',
            'cache': [ref(r) for r in selected if r['kind'] in ('body_cache', 'body_cache_writer')],
            'selected_ops': [ref(r) for r in selected if r['kind'] == 'memory_init_op'],
            'zero_ops': [{'seq': r['seq'], 'file': row_files[r['seq']], 'instance': r['data']['instance'],
                          'source': r['data']['source']} for r in selected if r['data'].get('decision') == 'zero_ops_selected'],
            'snapshot_hashes': [{'seq': r['seq'], 'file': row_files[r['seq']], 'instance': r['data']['instance'],
                                  'stage': r['data']['stage'], 'body_hash': r['data']['body_hash']}
                                 for r in selected if r['kind'] == 'mir_snapshot'],
            'per_root_codegen_records': sum(r['context']['stage'] == 'codegen' for r in selected),
            'per_root_codegen_comparison': 'UNKNOWN: no retained codegen records for this root; trace omitted555; not NOT_RUN',
        }
    assert all(v['per_root_codegen_records'] == 0 for v in keys.values())
    # The shared unit1 callee creator and observed subsequent writer are different contexts.
    by_seq = {r['seq']: r for r in rows}
    assert by_seq[120]['data']['event'] == 'miss_creator' and by_seq[241]['data']['event'] == 'hit'
    assert by_seq[121]['data']['body_hash'] == by_seq[242]['data']['body_hash'] == '8e83681b4d5b4436'
    assert by_seq[299]['data']['writer'] == 'DelayedUbPass'
    assert by_seq[298]['data']['body_hash'] == '9bae019701b64b9b'
    assert not any(r['kind'] == 'function_presence' for r in rows)
    budget = (EVIDENCE / 'budget.stdout.txt').read_text().split()
    assert budget == ['1', '0.1215', '0.0000']
    total = Decimal('.2025') + Decimal(budget[1])
    observations = {'build_id': BUILD, 'dispatch_head': HEAD, 'request_sha256': REQUEST,
                    'cloud_status': 'FAILURE', 'cloud_status_source': 'k1g watch terminal notification, delivery attempt1',
                    'classification': 'PROOF_EXECUTED_ORIGINAL_FAILURE_REPRODUCED_TRACE_OVERSIZED',
                    'kani_build': 'SUCCESS', 'kani_build_seconds': 245, 'kani_exit': 1, 'gate': False,
                    'roots': roots, 'A2_verdict_check_cover_counts_match': True,
                    'trace': {'state': 'OVERSIZED', 'complete': False, **coverage,
                              'sidecar': sidecar, 'footer_observation': footer, 'validator_errors': [],
                              'key_codegen_comparison': 'UNKNOWN; omitted555; no function_presence records retained'},
                    'cost': {'A3_usd': budget[1], 'terminal_reserved_usd': budget[2], 'initial_reserve_usd': '0.5265',
                             'cumulative_A_A2_A3_usd': str(total), 'cap_usd': '0.80',
                             'remaining_usd': str(Decimal('.80') - total), 'source': 'k1g.sh rounded pool ledger; not independent billing audit'},
                    'brief': {'exit': 1, 'reason': 'Reader report/query route unavailable HTTP404'},
                    'assurance': 'Bounded source-reported diagnostics; archive/index integrity and independent B1/B2 credit not established',
                    'runtime_causality': 'UNKNOWN', 'proof_credit': 'NONE', 'retry': False, 'B_run': False}
    (HERE / 'A3-OBSERVATIONS.json').write_text(json.dumps(observations, indent=2) + '\n')
    (HERE / 'TRACE-KEYS.json').write_text(json.dumps(keys, indent=2) + '\n')
    (HERE / 'EVIDENCE-INDEX.json').write_text(json.dumps({'build_id': BUILD, 'source_identity': identity,
        'archive_sha256': 'UNKNOWN: Brief unavailable; raw access prohibited',
        'index_sha256': 'UNKNOWN: K1 bounded summary routes only', 'receipts': receipts}, indent=2) + '\n')
    print(json.dumps({'result': 'PASS', 'bounded_pages': len(pages), 'retained_records': len(rows),
                       'A2_all9_match': True, 'state': coverage['state'], 'trace_complete': False,
                       'key_codegen_comparison': 'UNKNOWN', 'cost_usd': budget[1], 'cumulative_usd': str(total),
                       'remaining_usd': str(Decimal('.80') - total), 'proof_credit': 'NONE'}, indent=2))


if __name__ == '__main__':
    main()
