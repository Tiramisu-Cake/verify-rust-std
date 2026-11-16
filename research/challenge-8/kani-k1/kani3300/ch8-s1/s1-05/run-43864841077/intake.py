#!/usr/bin/env python3
"""Replay structured intake only; never executes a proof tool or reads raw logs."""
import gzip
import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
CONTROL = Path('/root/kani-ch8-s1-05-w13')
CONTROL_SHA = '8860d38558651f7cf2e292d57b06b378c6ad3b94'
RUN = 43864841077
sys.dont_write_bytecode = True


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def write(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def main():
    assert subprocess.check_output(['git', '-C', str(CONTROL), 'rev-parse', 'HEAD'], text=True).strip() == CONTROL_SHA
    sys.path.insert(0, str(CONTROL / 'ch8-s1-control'))
    r = importlib.import_module('runner')
    collector = importlib.import_module('collect')
    req = r.load_request()
    for rel, expected in req['ci_payload_sha256'].items():
        assert sha((CONTROL / rel).read_bytes()) == expected
    run, metadata = read(HERE / 'run-metadata.json'), read(HERE / 'artifacts-metadata.json')
    identity = read(HERE / 'run-identity.json')
    assert identity['id'] == RUN and identity['run_attempt'] == 1 and identity['head_sha'] == CONTROL_SHA
    assert identity['event'] == 'push' and identity['path'] == '.github/workflows/ch8-s1.yml'
    assert run['databaseId'] == RUN and run['headSha'] == CONTROL_SHA and run['status'] == 'completed'
    assert len(run['jobs']) == len(metadata['artifacts']) == metadata['total_count'] == 14
    roots = sorted((HERE / 'artifacts').iterdir())
    assert {p.name for p in roots} == {a['name'] for a in metadata['artifacts']}
    collected = collector.collect(roots, req)
    assert collected['missing_groups'] == [] and len(collected['rows']) == 35
    write('runner-collected.json', collected)
    byid = {p['id']: p for p in collected['rows']}
    source = {k: req[k] for k in ('std_sha', 'std_tree', 'tool_sha', 'tool_tree', 'changed_file_sha256')}
    groups, provenance = [], []
    for root in roots:
        archive = root / 'group-evidence.json.gz'
        assert archive.stat().st_size <= 8 * 1024 * 1024
        with gzip.open(archive, 'rb') as stream:
            raw = stream.read(32 * 1024 * 1024 + 1)
        assert len(raw) <= 32 * 1024 * 1024
        doc = json.loads(raw)
        assert doc['schema'] == 'ch8-s1-05-artifact-v1' and doc['state'] == 'PACKAGED'
        files = {}
        for rel, entry in doc['files'].items():
            data = entry['text'].encode()
            assert len(data) == entry['bytes'] and sha(data) == entry['sha256']
            files[rel] = json.loads(data)
        terminal = files['receipt.json']
        gid, = terminal['selected_groups']
        group = files[f'groups/{gid}/receipt.json']
        stock = files[f'groups/{gid}/export.json']
        rich = files[f'groups/{gid}/properties.json']
        compile_receipt = files[f'groups/{gid}/compile/receipt.json']
        job, = [j for j in run['jobs'] if j['name'].endswith('(' + gid + ')')]
        artifact, = [a for a in metadata['artifacts'] if a['name'] == root.name]
        assert not artifact['expired'] and artifact['workflow_run']['head_sha'] == CONTROL_SHA
        assert group['source_before'] == group['source_after'] == source
        expected_files = dict(req['changed_file_sha256'])
        if group['variant'] != 'production':
            variant = req['variants'][group['variant']]
            expected_files.update(variant['changed_file_sha256'])
            assert group['source_under_test']['patch_sha256'] == variant['sha256']
        assert group['source_under_test']['file_sha256'] == expected_files
        assert group['request_sha256'] == collected['request_sha256']
        assert stock['run_state'] == 'COMPLETE' and stock['kani_commit'] == req['tool_sha'] and stock['kani_commit_dirty'] is False
        assert {h['name'] for h in stock['harnesses']} == set(group['selectors'])
        assert compile_receipt['state'] == 'COMPLETE'
        before = group['tool_fingerprints_before']
        assert before['required_hashes_present']
        if group.get('tool_fingerprints_after'):
            after = group['tool_fingerprints_after']
            assert after['required_hashes_present']
            assert {k: v['sha256'] for k, v in before['binaries'].items()} == {k: v['sha256'] for k, v in after['binaries'].items()}
        execution = group['execution']
        assert not execution['timed_out'] and execution['signal'] is None and not execution.get('termination_reason')
        assert all(execution[k] is False for k in ('stdout_truncated', 'stderr_truncated', 'output_truncated'))
        assert execution['original_exit_code'] == (0 if all(h['outcome']['verdict'] == 'SUCCESS' for h in stock['harnesses']) else 1)
        rich_byname = {h['name']: h['properties'] for h in rich['harnesses']}
        observed_rows = []
        for harness in stock['harnesses']:
            row, = [q for q in req['rows'] if q['selector'] == harness['name'] and q['variant'] == group['variant']]
            rid = row['id']; observed_rows.append(rid)
            r.rich_evidence.validate_stock_inventory(harness)
            props = rich_byname.get(harness['name'], [])
            sites = sum(bool(p.get('description')) and bool(p.get('file')) and bool(p.get('line')) for p in props)
            # parse_export reads only structured export bytes and checks frozen
            # source/selection/config identities. It is not an execution runner.
            parsed = r.parse_export(HERE / 'evidence' / gid / 'export.json', row,
                                   source_binding=req['source_bindings'][rid],
                                   std=Path('/home/runner/work/kani/kani/export'), group_selectors=group['selectors'])
            byid[rid]['evidence'] = {
                'raw_outcome': harness['outcome'], 'structured_preflight': parsed,
                'stock_checks': harness['checks'], 'stock_covers': harness['covers'],
                'failed_properties': harness['failed_properties'],
                'unsupported_constructs': harness['unsupported_constructs'],
                'rich_state': rich['state'], 'rich_error': rich['error'],
                'stock_property_count': harness['n_properties'], 'retained_rich_property_count': len(props),
                'retained_with_description_and_site': sites,
                'rich_inventory_complete': rich['state'] == 'COMPLETE' and len(props) == sites == harness['n_properties'],
                'verification_time_s': harness['resources']['verification_time_s'],
                'group_original_exit': execution['original_exit_code'],
                'per_root_original_exit': None, 'per_root_wall_seconds': None, 'per_root_rss_kib': None,
                'per_root_measurement_scope': 'UNKNOWN_NO_SEPARATE_PROCESS_ATTRIBUTION',
                'group_elapsed_seconds': execution['elapsed_seconds'],
                'group_rss_peak_kib': execution['rss_peak_kib'], 'rss_scope': execution['rss_status'],
                'same_run_binary_after_snapshot': 'RECORDED' if group.get('tool_fingerprints_after') else 'NOT_REACHED_DECODER_FAILED',
                'qualified_acceptance': 'PENDING_OFFLINE_REVIEW' if rich['state'] == 'COMPLETE' else 'UNKNOWN_INCOMPLETE_RICH_EVIDENCE',
                'evidence': f'evidence/{gid}/', 'proof_credit': 'NONE'}
        groups.append({'id': gid, 'row_ids': observed_rows, 'job_id': job['databaseId'],
                       'job_conclusion': job['conclusion'], 'terminal_state': terminal['state'],
                       'stop_reason': terminal['stop_reason'], 'group_state': group['state'],
                       'execution': execution, 'compile_elapsed_upper_bound_seconds': compile_receipt['elapsed_upper_bound_seconds'],
                       'compile_exit_code': None, 'rich_state': rich['state'], 'rich_error': rich['error'],
                       'source_before_after': 'MATCHED_REQUEST', 'proof_credit': 'NONE'})
        provenance.append({'artifact': root.name, 'github_id': artifact['id'],
                           'github_zip_digest': artifact.get('digest'),
                           'github_zip_digest_verification': 'NOT_VERIFIED_GH_DOWNLOAD_EXTRACTS_ZIP',
                           'payload_sha256': sha(archive.read_bytes()), 'payload_bytes': archive.stat().st_size,
                           'uncompressed_bytes': len(raw),
                           'saved_projection': {str(p.relative_to(HERE)): sha(p.read_bytes())
                                                for p in sorted((HERE / 'evidence' / gid).rglob('*.json'))},
                           'projection_note': 'export/properties exact; receipt head/tail previews removed; originals preserved in compact artifact',
                           'entries': {k: {a: v[a] for a in ('sha256', 'bytes')} for k, v in doc['files'].items()}})
    collected.update(schema='s105-intake-v1', run=RUN, control_sha=CONTROL_SHA,
                     groups=groups, assurance='SOURCE_REPORTED_VERDICTS; STRUCTURED_INVENTORY_RECONCILIATION; NO_INDEPENDENT_PROOF_CREDIT')
    write('collected.json', collected)
    write('PROVENANCE.json', provenance)
    totals = {'groups': len(groups), 'rows': len(collected['rows']),
              'complete_rich_groups': sum(g['rich_state'] == 'COMPLETE' for g in groups),
              'complete_rich_rows': sum(q['evidence']['rich_inventory_complete'] for q in collected['rows']),
              'source_success': sum(q['evidence']['raw_outcome']['verdict'] == 'SUCCESS' for q in collected['rows']),
              'source_failure': sum(q['evidence']['raw_outcome']['verdict'] == 'FAILURE' for q in collected['rows']),
              'stock_properties': sum(q['evidence']['stock_property_count'] for q in collected['rows']),
              'retained_rich_properties': sum(q['evidence']['retained_rich_property_count'] for q in collected['rows']),
              'checks_unreachable': sum(len(q['evidence']['stock_checks']['unreachable']) for q in collected['rows']),
              'covers_satisfied': sum(len(q['evidence']['stock_covers']['satisfied']) for q in collected['rows']),
              'covers_unreachable': sum(len(q['evidence']['stock_covers']['unreachable']) for q in collected['rows']),
              'proof_credit': 'NONE'}
    write('TOTALS.json', totals)
    print(json.dumps(totals))


if __name__ == '__main__':
    main()
