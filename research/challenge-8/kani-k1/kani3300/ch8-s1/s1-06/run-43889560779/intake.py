#!/usr/bin/env python3
"""Replay compact structured evidence; never execute tools or open raw logs."""
import copy
import gzip
import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
CONTROL = Path('/root/kani-ch8-s1-06-intake-w13')
CONTROL_SHA = 'a14a513eb7a77297a0cc10ff6eefa7577c2c383c'
FIX_SHA = 'b25dd39a46ba90b167500997d546a5f2f5bd8f3b'
STD = Path('/root/verify-rust-std-ch8-s1-04-w13')
RUN = 43889560779
SITE_ERROR = 'rich metadata incomplete: file/line missing'
sys.dont_write_bytecode = True


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def write(name, value):
    dest = HERE / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + '\n')


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args]).decode().strip()


def without_previews(value):
    if isinstance(value, dict):
        return {k: without_previews(v) for k, v in value.items() if k not in ('stdout', 'stderr')}
    if isinstance(value, list):
        return [without_previews(v) for v in value]
    return value


def reconcile(rich_module, stock, rich):
    """Use unchanged decoder; expected final coordinate rejection is not a PASS."""
    parser = rich_module.RegularEvidence([h['name'] for h in stock['harnesses']], Path('/'))
    parser.records = {h['name']: copy.deepcopy(h['properties']) for h in rich['harnesses']}
    parser.finished = True
    missing = [p for h in rich['harnesses'] for p in h['properties']
               if not p.get('file') or not p.get('line')]
    error = None
    try:
        parser.validate(stock)
    except ValueError as exc:
        error = str(exc)
        require(error == SITE_ERROR and bool(missing), 'unexpected inventory error: ' + error)
    require(parser.complete == (not missing), 'decoder completeness mismatch')
    require((rich['state'] == 'COMPLETE') == parser.complete, 'saved completeness mismatch')
    # The coordinate gate is the last check, after exact IDs, buckets, statuses,
    # classes and named failure/unsupported links have all been reconciled.
    return {'inventory_reconciliation': 'ALL_ROWS_EXACT_STOCK_BUCKETS_AND_RICH_RECORDS_RECONCILED',
            'metadata_gate': 'FAIL_CLOSED_MISSING_COORDINATES' if error else 'PASS',
            'metadata_gate_error': error, 'qualified_acceptance': 'PENDING', 'proof_credit': 'NONE'}


def main():
    require(git(CONTROL, 'rev-parse', 'HEAD') == CONTROL_SHA, 'control HEAD')
    require(not git(CONTROL, 'status', '--porcelain'), 'dirty control')
    require(git(CONTROL, 'rev-parse', CONTROL_SHA + '^{tree}') ==
            git(CONTROL, 'rev-parse', FIX_SHA + '^{tree}'), 'sibling tree differs')
    sys.path.insert(0, str(CONTROL / 'ch8-s1-control'))
    r = importlib.import_module('runner')
    collector = importlib.import_module('collect')
    request = r.load_request()
    request_bytes = r.REQUEST_PATH.read_bytes()
    require(git(STD, 'rev-parse', 'HEAD') == request['std_sha'], 'std HEAD')
    require(not git(STD, 'status', '--porcelain'), 'dirty std')
    require(git(STD, 'rev-parse', request['std_sha'] + '^{tree}') == request['std_tree'], 'std tree')
    require(git(CONTROL, 'rev-parse', request['tool_sha'] + '^{tree}') == request['tool_tree'], 'tool tree')
    for rel, expected in request['ci_payload_sha256'].items():
        require(sha((CONTROL / rel).read_bytes()) == expected, 'payload hash: ' + rel)
    for rel, expected in request['changed_file_sha256'].items():
        require(sha((STD / rel).read_bytes()) == expected, 'std file hash: ' + rel)
    (HERE / 'CI-REQUEST.json').write_bytes(request_bytes)
    identity, artifacts, jobs = map(read, (HERE / 'run-identity.json', HERE / 'artifacts-metadata.json', HERE / 'jobs-metadata.json'))
    require(identity['id'] == RUN and identity['head_sha'] == CONTROL_SHA and identity['run_attempt'] == 1,
            'run identity')
    require(identity['status'] == 'completed' and identity['event'] == 'push' and
            identity['path'] == '.github/workflows/ch8-s1.yml', 'run state/event/path')
    roots = sorted((HERE / 'artifacts').iterdir())
    require(len(roots) == len(artifacts['artifacts']) == len(jobs['jobs']) == 14, '14 groups')
    require({p.name for p in roots} == {a['name'] for a in artifacts['artifacts']}, 'artifact set')
    collected = collector.collect(roots, request)
    require(not collected['missing_groups'] and len(collected['rows']) == 35, 'collected rows')
    write('runner-collected.json', without_previews(collected))
    byid = {p['id']: p for p in collected['rows']}
    source = {k: request[k] for k in ('std_sha', 'std_tree', 'tool_sha', 'tool_tree', 'changed_file_sha256')}
    groups, provenance, missing_sites = [], [], []
    for root in roots:
        archive = root / 'group-evidence.json.gz'
        require(archive.stat().st_size <= 8 * 1024 * 1024, 'compressed size cap')
        with gzip.open(archive, 'rb') as stream:
            raw = stream.read(32 * 1024 * 1024 + 1)
        require(len(raw) <= 32 * 1024 * 1024, 'uncompressed size cap')
        doc = json.loads(raw)
        require(doc['schema'] == 'ch8-s1-05-artifact-v1' and doc['state'] == 'PACKAGED', 'artifact schema/state')
        files = {}
        for rel, entry in doc['files'].items():
            require(not Path(rel).is_absolute() and '..' not in Path(rel).parts and rel.endswith('.json'), 'entry path')
            data = entry['text'].encode()
            require(len(data) == entry['bytes'] and sha(data) == entry['sha256'], 'entry integrity: ' + rel)
            files[rel] = json.loads(data)
        terminal = files['receipt.json']
        gid, = terminal['selected_groups']
        group = files[f'groups/{gid}/receipt.json']
        stock = files[f'groups/{gid}/export.json']
        rich = files[f'groups/{gid}/properties.json']
        comp = files[f'groups/{gid}/compile/receipt.json']
        job, = [j for j in jobs['jobs'] if j['name'].endswith('(' + gid + ')')]
        artifact, = [a for a in artifacts['artifacts'] if a['name'] == root.name]
        zipinfo = read(root / 'zip-integrity.json')
        require(zipinfo['github_digest_match'] and artifact['digest'] == 'sha256:' + zipinfo['sha256'], 'ZIP digest')
        require(not artifact['expired'] and artifact['workflow_run']['id'] == RUN and
                artifact['workflow_run']['head_sha'] == CONTROL_SHA and job['run_id'] == RUN, 'artifact/job identity')
        require(group['source_before'] == group['source_after'] == source, 'source snapshot')
        expected_files = dict(request['changed_file_sha256'])
        if group['variant'] != 'production':
            variant = request['variants'][group['variant']]
            expected_files.update(variant['changed_file_sha256'])
            require(group['source_under_test']['patch_sha256'] == variant['sha256'], 'variant patch')
        require(group['source_under_test']['file_sha256'] == expected_files, 'variant files')
        require(group['request_sha256'] == comp['request_sha256'] == sha(request_bytes), 'request hash')
        require(stock['run_state'] == 'COMPLETE' and stock['kani_commit'] == request['tool_sha'] and
                stock['kani_commit_dirty'] is False and comp['state'] == 'COMPLETE', 'stock/compile complete')
        require({h['name'] for h in stock['harnesses']} == set(group['selectors']), 'harness set')
        require({h['name'] for h in rich['harnesses']} == set(group['selectors']), 'rich harness set')
        reconciliation = reconcile(r.rich_evidence, stock, rich)
        before, after = group['tool_fingerprints_before'], group.get('tool_fingerprints_after')
        require(before['required_hashes_present'], 'missing before fingerprints')
        if after:
            require(after['required_hashes_present'] and
                    {k: v['sha256'] for k, v in before['binaries'].items()} ==
                    {k: v['sha256'] for k, v in after['binaries'].items()}, 'binary drift')
        execution = group['execution']
        require(not execution['timed_out'] and execution['signal'] is None and
                not execution.get('termination_reason'), 'interrupted execution')
        require(all(execution[k] is False for k in ('stdout_truncated', 'stderr_truncated', 'output_truncated')), 'truncated execution')
        require(execution['original_exit_code'] == (0 if all(h['outcome']['verdict'] == 'SUCCESS' for h in stock['harnesses']) else 1), 'exit/export mismatch')
        # Export and rich projections retain exact original bytes. Receipt
        # projections remove only bounded stdout/stderr previews, recursively.
        dest = HERE / 'evidence' / gid
        for suffix in ('export.json', 'properties.json', 'receipt.json', 'compile/receipt.json'):
            rel = f'groups/{gid}/{suffix}'
            p = dest / suffix
            p.parent.mkdir(parents=True, exist_ok=True)
            if suffix in ('export.json', 'properties.json'):
                p.write_bytes(doc['files'][rel]['text'].encode())
            else:
                p.write_text(json.dumps(without_previews(files[rel]), indent=2, sort_keys=True) + '\n')
        props_byname = {h['name']: h['properties'] for h in rich['harnesses']}
        observed_rows = []
        for harness in stock['harnesses']:
            row, = [q for q in request['rows'] if q['selector'] == harness['name'] and q['variant'] == group['variant']]
            rid = row['id']
            observed_rows.append(rid)
            props = props_byname[harness['name']]
            require(all(p.get('description') for p in props), 'missing description')
            missing = [p for p in props if not p.get('file') or not p.get('line')]
            for p in missing:
                require(p['class'] == 'unreachable' and p['description'] == 'unreachable code' and
                        p['status'] == 'SUCCESS', 'unexpected missing-site role/status')
                missing_sites.append({'row_id': rid, 'group': gid, 'selector': harness['name'], **p,
                                      'role': 'STOCK_MIR_UNREACHABLE_ASSERT_ASSUME_FALSE',
                                      'required_post_frame_relation_cover': False,
                                      'location_policy_exception': 'NOT_AUTHORIZED_NOT_APPLIED',
                                      'precise_MIR_source_block_binding': 'UNKNOWN'})
            parsed = r.parse_export(dest / 'export.json', row, source_binding=request['source_bindings'][rid],
                                    std=Path('/home/runner/work/kani/kani/export'), group_selectors=group['selectors'])
            byid[rid]['evidence'] = {
                'raw_outcome': harness['outcome'], 'structured_preflight': parsed,
                'stock_checks': harness['checks'], 'stock_covers': harness['covers'],
                'failed_properties': harness['failed_properties'], 'unsupported_constructs': harness['unsupported_constructs'],
                'stock_property_count': harness['n_properties'], 'retained_rich_property_count': len(props),
                'retained_with_description_and_site': len(props)-len(missing), 'missing_sites': missing,
                'row_inventory_retained': len(props) == harness['n_properties'],
                'row_locations_complete': not missing, 'rich_state': rich['state'],
                'rich_error': rich['error'], 'rich_inventory_complete': rich['state'] == 'COMPLETE' and not missing,
                'inventory_reconciliation': reconciliation,
                'verification_time_s': harness['resources']['verification_time_s'],
                'group_original_exit': execution['original_exit_code'],
                'per_root_original_exit': None, 'per_root_wall_seconds': None, 'per_root_rss_kib': None,
                'per_root_measurement_scope': 'UNKNOWN_NO_SEPARATE_PROCESS_ATTRIBUTION',
                'group_elapsed_seconds': execution['elapsed_seconds'], 'group_rss_peak_kib': execution['rss_peak_kib'],
                'rss_scope': execution['rss_status'],
                'same_run_binary_after_snapshot': 'RECORDED_MATCH' if after else 'NOT_REACHED_METADATA_GATE_FAILED',
                'qualified_acceptance': 'PENDING_OFFLINE_POLICY_AND_BINDING_REVIEW',
                'evidence': f'evidence/{gid}/', 'proof_credit': 'NONE'}
        groups.append({'id': gid, 'row_ids': observed_rows, 'job_id': job['id'], 'job_conclusion': job['conclusion'],
                       'runner_exit': 0 if group['state'] == 'COMPLETE' else 1,
                       'runner_exit_assurance': 'INFERRED_FROM_RUNNER_MAIN_AND_JOB_STEP_CONCLUSION',
                       'terminal_state': terminal['state'], 'stop_reason': terminal['stop_reason'],
                       'group_state': group['state'], 'reason': group.get('reason'), 'execution': execution,
                       'compile_elapsed_upper_bound_seconds': comp['elapsed_upper_bound_seconds'], 'compile_exit_code': None,
                       'rich_state': rich['state'], 'rich_error': rich['error'],
                       'missing_sites': len(rich['missing_sites']), 'reconciliation': reconciliation,
                       'same_run_binary_after_snapshot': 'RECORDED_MATCH' if after else 'NOT_REACHED_METADATA_GATE_FAILED',
                       'source_before_after': 'MATCHED_REQUEST', 'proof_credit': 'NONE'})
        provenance.append({'artifact': root.name, 'github_id': artifact['id'], 'github_zip_digest': artifact['digest'],
                           'github_zip_digest_verification': 'MATCHED_DOWNLOADED_ZIP_BYTES_BEFORE_EXTRACTION',
                           'zip_bytes': zipinfo['bytes'], 'payload_sha256': sha(archive.read_bytes()),
                           'payload_bytes': archive.stat().st_size, 'uncompressed_bytes': len(raw),
                           'projection_note': 'export/properties exact; receipt stdout/stderr previews removed; compact original retained',
                           'saved_projection': {str(p.relative_to(HERE)): sha(p.read_bytes()) for p in sorted(dest.rglob('*.json'))},
                           'entries': {k: {a: v[a] for a in ('sha256', 'bytes')} for k, v in doc['files'].items()}})
    collected = without_previews(collected)
    collected.update(schema='s106-intake-v1', run=RUN, control_sha=CONTROL_SHA, fix_control_sha=FIX_SHA,
                     groups=groups, assurance='SOURCE_REPORTED_VERDICTS; EXACT_INVENTORY_RECONCILIATION; NO_INDEPENDENT_PROOF_CREDIT')
    write('collected.json', collected)
    write('PROVENANCE.json', provenance)
    write('missing-sites.json', {'schema': 's106-missing-sites-v1', 'policy_exception_applied': False, 'records': missing_sites})
    rows = collected['rows']
    totals = {'groups': len(groups), 'rows': len(rows),
              'complete_rich_groups': sum(g['rich_state'] == 'COMPLETE' for g in groups),
              'complete_rich_rows_in_complete_groups': sum(q['evidence']['rich_inventory_complete'] for q in rows),
              'individually_location_complete_rows': sum(q['evidence']['row_locations_complete'] for q in rows),
              'source_success': sum(q['evidence']['raw_outcome']['verdict'] == 'SUCCESS' for q in rows),
              'source_failure': sum(q['evidence']['raw_outcome']['verdict'] == 'FAILURE' for q in rows),
              'stock_properties': sum(q['evidence']['stock_property_count'] for q in rows),
              'retained_rich_properties': sum(q['evidence']['retained_rich_property_count'] for q in rows),
              'missing_site_properties': len(missing_sites), 'missing_site_unique_ids': len({p['id'] for p in missing_sites}),
              'heavy_missing_sites': sum('freeze' in p['group'] for p in missing_sites),
              'checks_unreachable': sum(len(q['evidence']['stock_checks']['unreachable']) for q in rows),
              'covers_satisfied': sum(len(q['evidence']['stock_covers']['satisfied']) for q in rows),
              'covers_unreachable': sum(len(q['evidence']['stock_covers']['unreachable']) for q in rows),
              'group_elapsed_seconds_sum': round(sum(g['execution']['elapsed_seconds'] for g in groups), 3),
              'compile_elapsed_upper_bound_seconds_sum': round(sum(g['compile_elapsed_upper_bound_seconds'] for g in groups), 3),
              'proof_credit': 'NONE'}
    require(totals['stock_properties'] == totals['retained_rich_properties'] == 9986, 'full inventory retention')
    require(totals['missing_site_properties'] == 18 and totals['heavy_missing_sites'] == 16, 'missing site set')
    write('TOTALS.json', totals)
    write('VALIDATION.json', {'state': 'PASS_STRUCTURED_INTAKE', 'run': RUN, 'groups': 14, 'rows': 35,
                             'checks': ['exact run/artifact/job/control/source/tool/request identities',
                                        '14 ZIP SHA256 digests matched before extraction', 'all compact member bytes and SHA256 match',
                                        '9986 records reconciled against unchanged decoder stock inventory validation',
                                        '10 expected final coordinate gate failures remain fail-closed',
                                        'source and binary snapshots preserved; absent after snapshots remain UNKNOWN',
                                        '35 source verdicts and measurements retained separately from runner UNKNOWN'],
                             'policy_exception_applied': False, 'local_verifier_execution': 'NOT_RUN', 'proof_credit': 'NONE'})
    print(json.dumps(totals, sort_keys=True))


if __name__ == '__main__':
    main()
