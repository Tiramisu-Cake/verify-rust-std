#!/usr/bin/env python3
"""Replay structured S1-07 evidence only; no compiler, verifier or raw log reads."""
import base64
import gzip
import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
OLD = HERE.parent.parent / 's1-06/run-43889560779'
CONTROL = Path('/root/kani-ch8-s1-07-w13')
STD = Path('/root/verify-rust-std-ch8-s1-04-w13')
CANDIDATE = '9208b373c0a08a265fa0d7493a6529e331065271'
EXECUTED = 'b37f6f75c5b7b77e84297cd7104f9c0868502fd4'
TREE = 'b6354b703d67f7aac03742b10d8c175a8eb43d24'
RUN = 43923266772
REQUIRED = ['kani_driver', 'kani_compiler', 'cbmc']
UNKNOWN = 'UNKNOWN_NOT_EXPORTED_BY_PINNED_PRODUCER'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def write(name, value):
    path = HERE / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + '\n')


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args]).decode().strip()


def without_previews(value):
    if isinstance(value, dict):
        return {k: without_previews(v) for k, v in value.items() if k not in ('stdout', 'stderr')}
    if isinstance(value, list):
        return [without_previews(v) for v in value]
    return value


def compact(root):
    path = root / 'group-evidence.json.gz'
    require(path.stat().st_size <= 8 * 1024 * 1024, 'compressed cap')
    with gzip.open(path, 'rb') as stream:
        raw = stream.read(32 * 1024 * 1024 + 1)
    require(len(raw) <= 32 * 1024 * 1024, 'uncompressed cap')
    doc = json.loads(raw)
    require(doc['schema'] == 'ch8-s1-05-artifact-v1' and doc['state'] == 'PACKAGED'
            and doc['error'] is None, 'compact completeness')
    values, data = {}, {}
    for rel, entry in doc['files'].items():
        require(not Path(rel).is_absolute() and '..' not in Path(rel).parts
                and rel.endswith('.json'), 'unsafe structured member')
        payload = (entry['text'].encode() if entry.get('encoding', 'utf-8') == 'utf-8'
                   else base64.b64decode(entry['text'], validate=True))
        require(len(payload) == entry['bytes'] and sha(payload) == entry['sha256'], 'member digest: ' + rel)
        data[rel], values[rel] = payload, json.loads(payload)
    return doc, values, data, len(raw)


def compare_inventory(old, new):
    a, b = ({p['id']: p for p in props} for props in (old, new))
    return {'removed': sorted(a.keys() - b.keys()), 'added': sorted(b.keys() - a.keys()),
            'changed': [{'id': key, 'fields': {field: {'s106': a[key].get(field), 's107': b[key].get(field)}
                         for field in sorted(a[key].keys() | b[key].keys())
                         if a[key].get(field) != b[key].get(field)}}
                        for key in sorted(a.keys() & b.keys()) if a[key] != b[key]],
            'order_equal': [p['id'] for p in old] == [p['id'] for p in new]}


def main():
    require(git(CONTROL, 'rev-parse', 'HEAD') == CANDIDATE and
            not git(CONTROL, 'status', '--porcelain'), 'control pin/dirty')
    require(git(CONTROL, 'rev-parse', CANDIDATE + '^{tree}') ==
            git(CONTROL, 'rev-parse', EXECUTED + '^{tree}') == TREE, 'sibling tree')
    sys.path.insert(0, str(CONTROL / 'ch8-s1-control'))
    r, collector = importlib.import_module('runner'), importlib.import_module('collect')
    request = r.load_request()
    request_bytes = r.REQUEST_PATH.read_bytes()
    package = read(HERE.parent / 'CI-REQUEST.json')
    require(sha(request_bytes) == package['control_candidate']['embedded_request_sha256'], 'embedded request')
    require(git(STD, 'rev-parse', 'HEAD') == request['std_sha'] and
            not git(STD, 'status', '--porcelain'), 'std pin/dirty')
    require(git(STD, 'rev-parse', 'HEAD^{tree}') == request['std_tree'] and
            git(CONTROL, 'rev-parse', request['tool_sha'] + '^{tree}') == request['tool_tree'], 'source/tool tree')
    for rel, expected in request['changed_file_sha256'].items():
        require(sha((STD / rel).read_bytes()) == expected, 'std file: ' + rel)
    for rel, expected in request['ci_payload_sha256'].items():
        require(sha((CONTROL / rel).read_bytes()) == expected, 'control payload: ' + rel)
    require(sha((HERE.parent / 'W11-MISSING-FOR-S1-07.md').read_bytes()) ==
            request['binding_metadata_requirements_sha256'], 'w11 requirements pin')
    (HERE / 'CI-REQUEST.json').write_bytes(request_bytes)
    identity, artifacts, jobs = map(read, (HERE / 'run-identity.json', HERE / 'artifacts-metadata.json',
                                         HERE / 'jobs-metadata.json'))
    require(identity['id'] == RUN and identity['head_sha'] == EXECUTED and identity['run_attempt'] == 1
            and identity['status'] == 'completed' and identity['conclusion'] == 'success'
            and identity['head_branch'] == 'uninit-ci/ch8-s1k-i' and identity['event'] == 'push'
            and identity['path'] == '.github/workflows/ch8-s1.yml', 'run identity')
    roots = sorted((HERE / 'artifacts').iterdir())
    require(len(roots) == len(artifacts['artifacts']) == len(jobs['jobs']) == 14, '14 groups/jobs/artifacts')
    require({p.name for p in roots} == {a['name'] for a in artifacts['artifacts']}, 'artifact set')
    collected = collector.collect(roots, request)
    require(not collected['missing_groups'] and len(collected['rows']) == 35, 'complete matrix')
    require(all(x['outcome'] == 'RECORDED' and x['status'] == 'OBSERVED' for x in collected['rows']),
            'collector fail-closed result')
    write('runner-collected.json', without_previews(collected))
    byid = {x['id']: x for x in collected['rows']}
    old_collected = read(OLD / 'collected.json')
    old_rows = {x['id']: x for x in old_collected['rows']}
    old_groups = {x['id']: x for x in old_collected['groups']}
    old_request = read(OLD / 'CI-REQUEST.json')
    proof_keys = ['rows', 'execution_groups', 'replacement_unions', 'source_bindings', 'flags',
                  'std_sha', 'std_tree', 'tool_sha', 'tool_tree', 'variants', 'changed_file_sha256']
    request_diffs = {key: {'s106': old_request[key], 's107': request[key]}
                     for key in proof_keys if old_request[key] != request[key]}
    nonproof_request_diffs = {key: {'s106': old_request.get(key), 's107': request.get(key)}
        for key in sorted(old_request.keys() | request.keys()) if key not in proof_keys
        and old_request.get(key) != request.get(key)}
    source = {k: request[k] for k in ('std_sha', 'std_tree', 'tool_sha', 'tool_tree', 'changed_file_sha256')}
    groups, provenance, locations, comparisons = [], [], [], []
    native_count = native_bytes = 0
    for root in roots:
        doc, files, data, raw_size = compact(root)
        terminal = files['receipt.json']
        gid, = terminal['selected_groups']
        prefix = f'groups/{gid}/'
        group, stock, rich, comp, meta = (files[prefix + name] for name in
            ('receipt.json', 'export.json', 'properties.json', 'compile/receipt.json', 'binding-metadata.json'))
        job, = [j for j in jobs['jobs'] if j['name'].endswith('(' + gid + ')')]
        artifact, = [a for a in artifacts['artifacts'] if a['name'] == root.name]
        zipinfo = read(root / 'zip-integrity.json')
        require(zipinfo['github_digest_match'] and artifact['digest'] == 'sha256:' + zipinfo['sha256']
                and zipinfo['bytes'] == artifact['size_in_bytes'], 'ZIP download attestation')
        require(sha((root / 'group-evidence.json.gz').read_bytes()) == zipinfo['payload_sha256'], 'payload digest')
        require(not artifact['expired'] and artifact['workflow_run']['id'] == RUN and
                artifact['workflow_run']['head_sha'] == EXECUTED and
                artifact['workflow_run']['head_branch'] == identity['head_branch'], 'artifact identity')
        require(job['run_id'] == RUN and job['status'] == 'completed' and job['conclusion'] == 'success'
                and all(step['conclusion'] == 'success' for step in job['steps']), 'job state/steps')
        require(group['source_before'] == group['source_after'] == source, 'source snapshots')
        require(group['request_sha256'] == comp['request_sha256'] == sha(request_bytes), 'group request')
        require(group['state'] == terminal['state'] == comp['state'] == 'COMPLETE', 'completion state')
        expected_files = dict(request['changed_file_sha256'])
        patch_hash = None
        if group['variant'] != 'production':
            variant = request['variants'][group['variant']]
            expected_files.update(variant['changed_file_sha256'])
            patch_hash = variant['sha256']
        require(group['source_under_test']['file_sha256'] == expected_files and
                group['source_under_test']['patch_sha256'] == patch_hash, 'variant source')
        before, after = group['tool_fingerprints_before'], group['tool_fingerprints_after']
        require(r.fingerprints_match(before, after) and not group['snapshot_errors'], 'fixed binary match')
        for phase, snap in [('BEFORE_CHILD', before), ('AFTER_CHILD_SHUTDOWN', after)]:
            require(snap['required_binaries'] == REQUIRED and snap['missing_binaries'] == [] and
                    snap['phase'] == phase and snap['snapshot_completed'] is True and snap['state'] == 'COMPLETE',
                    'snapshot phase/completion')
        execution = group['execution']
        require(execution['child_shutdown_verified'] is True and execution['signal'] is None and
                not execution['timed_out'] and not execution.get('termination_reason') and
                all(execution[k] is False for k in ('stdout_truncated', 'stderr_truncated', 'output_truncated')),
                'execution interruption/truncation')
        require(not group.get('original_exception') and not group.get('execution_exception') and
                not meta.get('original_exception') and not meta.get('execution_exception'), 'original exception')
        require(execution['original_exit_code'] ==
                (0 if all(h['outcome']['verdict'] == 'SUCCESS' for h in stock['harnesses']) else 1), 'group exit')
        require(rich['state'] == 'COMPLETE' and rich['error'] is None, 'rich completion')
        require(sorted((x['harness'], x['display_id'], x['location_display']) for x in rich['missing_sites']) ==
                sorted((x['harness'], x['property']['display_id'], x['property']['location_display'])
                       for x in rich['location_exceptions']), 'streaming missing sites equal exact exceptions')
        require(meta['compiler_identity_status'] == UNKNOWN and meta['compilation_id'] is None and
                meta['requirements_sha256'] == request['binding_metadata_requirements_sha256'], 'metadata gap identity')
        require(meta['source_before'] == meta['source_after'] == source and
                meta['execution'] == execution and meta['unwind'] == group['unwind'], 'metadata context')
        require(meta['configuration_sha256'] == sha(json.dumps({'flags': request['flags'],
                'cfg': group['effective_cfg'], 'argv': group['argv']}, sort_keys=True).encode()), 'configuration hash')
        native_count += len(meta['native_metadata'])
        native_bytes += sum(e['bytes'] for e in meta['native_metadata'])
        dest = HERE / 'evidence' / gid
        for name in ('export.json', 'properties.json', 'binding-metadata.json', 'receipt.json', 'compile/receipt.json'):
            out = dest / name
            out.parent.mkdir(parents=True, exist_ok=True)
            if name.endswith('receipt.json'):
                out.write_text(json.dumps(without_previews(files[prefix + name]), indent=2, sort_keys=True) + '\n')
            else:
                out.write_bytes(data[prefix + name])
        rich_byname = {h['name']: h['properties'] for h in rich['harnesses']}
        old_rich = {h['name']: h['properties'] for h in read(OLD / 'evidence' / gid / 'properties.json')['harnesses']}
        old_stock = {h['name']: h for h in read(OLD / 'evidence' / gid / 'export.json')['harnesses']}
        for harness in stock['harnesses']:
            row, = [x for x in request['rows'] if x['selector'] == harness['name'] and x['variant'] == group['variant']]
            rid = row['id']
            props = rich_byname[harness['name']]
            exceptions = [x for x in rich['location_exceptions'] if x['harness'] == harness['name']]
            nullable = [p for p in props if p['file'] is None or p['line'] is None]
            require(nullable == [e['property'] for e in exceptions], 'nullable set equals location exception set')
            require(all(p['file'] is None and p['line'] is None and p['class'] == 'unreachable'
                        and p['status'] == 'SUCCESS' and p['description'] == 'unreachable code' for p in nullable),
                    'location exception fields')
            locations.extend({'group': gid, 'row_id': rid, 'selector': harness['name'],
                              'variant': group['variant'], **e} for e in exceptions)
            parsed = r.parse_export(dest / 'export.json', row, source_binding=request['source_bindings'][rid],
                                    std=STD, group_selectors=group['selectors'])
            require(parsed['state'] == 'RECORDED_OBSERVATION', 'export parse: ' + rid)
            expected_verdict = 'FAILURE' if row['expected'] == 'DETECTED' else 'SUCCESS'
            require(harness['outcome']['verdict'] == expected_verdict, 'expected verdict: ' + rid)
            negative_observation = None
            if row['expected'] == 'DETECTED':
                oracle = row['oracle']
                failed, = harness['failed_properties']
                require(harness['checks']['failure'] == [oracle['property_id']] and harness['n_failed'] == 1
                        and failed['id'] == oracle['property_id'] and failed['file'] == oracle['export_file']
                        and failed['line'] == str(oracle['line']) and failed['class'] == oracle['class'] == 'assertion'
                        and failed['status'] == 'FAILURE', 'exact sole failure oracle: ' + rid)
                companion = next(x for x in request['rows'] if x['id'] == row['companion'])
                companion_observation = byid[companion['id']]['export']['harness']
                require(companion_observation['outcome']['verdict'] == 'SUCCESS' and
                        companion['variant'] == 'production', 'same-run production companion: ' + rid)
                negative_observation = {'exact_sole_failure_match': True, 'oracle': oracle,
                    'companion_row_id': companion['id'], 'companion_source_verdict': 'SUCCESS',
                    'qualified_acceptance': 'PENDING_OFFLINE_W11', 'proof_credit': 'NONE'}
            require(len(props) == harness['n_properties'], 'retained row count')
            native_row, = [x for x in meta['rows'] if x['row_id'] == rid]
            require(all(value == UNKNOWN for value in native_row['binding_gaps'].values()), 'producer binding gaps')
            inventory_diff = compare_inventory(old_rich[harness['name']], props)
            h_old = old_stock[harness['name']]
            harness_diff = {key: {'s106': h_old.get(key), 's107': harness.get(key)}
                            for key in sorted(h_old.keys() | harness.keys())
                            if key != 'resources' and h_old.get(key) != harness.get(key)}
            order_only = True
            for key, values in harness_diff.items():
                if key == 'checks':
                    def buckets(v):
                        return {k: sorted(x) if isinstance(x, list) else x for k, x in v.items()}
                    order_only &= buckets(values['s106']) == buckets(values['s107'])
                elif key == 'unsupported_constructs':
                    order_only &= sorted(values['s106'], key=lambda p: p['id']) == sorted(values['s107'], key=lambda p: p['id'])
                else:
                    order_only = False
            comparisons.append({'id': rid, 'group': gid,
                'verdict_equal': harness['outcome'] == old_rows[rid]['evidence']['raw_outcome'],
                'property_count_equal': harness['n_properties'] == h_old['n_properties'],
                'rich_inventory': inventory_diff, 'stock_harness_changes_except_resources': harness_diff,
                'stock_harness_differences_are_list_order_only': order_only,
                'verification_time_s': {'s106': h_old['resources']['verification_time_s'],
                                        's107': harness['resources']['verification_time_s']}})
            byid[rid]['evidence'] = {
                'raw_outcome': harness['outcome'], 'expected': row['expected'],
                'expected_verdict': expected_verdict, 'verdict_expectation_match': True,
                'stock_checks': harness['checks'], 'stock_covers': harness['covers'],
                'failed_properties': harness['failed_properties'], 'unsupported_constructs': harness['unsupported_constructs'],
                'negative_observation': negative_observation,
                'stock_property_count': harness['n_properties'], 'retained_rich_property_count': len(props),
                'rich_inventory_complete': True, 'row_locations_complete': not nullable,
                'location_exceptions': exceptions, 'original_nullable_sites': nullable,
                'group_original_exit': execution['original_exit_code'], 'group_original_exception': None,
                'group_elapsed_seconds': execution['elapsed_seconds'], 'group_rss_peak_kib': execution['rss_peak_kib'],
                'rss_scope': execution['rss_status'], 'verification_time_s': harness['resources']['verification_time_s'],
                'per_root_original_exit': None, 'per_root_wall_seconds': None, 'per_root_rss_kib': None,
                'per_root_measurement_scope': 'UNKNOWN_NO_SEPARATE_PROCESS_ATTRIBUTION',
                'same_run_binary_after_snapshot': 'RECORDED_MATCH',
                'tool_fingerprints_before': before, 'tool_fingerprints_after': after,
                'native_harness_records': native_row['native_harness_records'], 'binding_gaps': native_row['binding_gaps'],
                'invocation_id': meta['invocation_id'], 'compiler_compilation_id': None,
                'evidence': f'evidence/{gid}/', 'inventory_pointer': '/harnesses/' + str(next(
                    i for i, h in enumerate(rich['harnesses']) if h['name'] == harness['name'])) + '/properties',
                'native_metadata_container': f'evidence/{gid}/binding-metadata.json',
                'native_metadata_pointer': '/native_metadata',
                'qualified_acceptance': 'PENDING_OFFLINE_W11', 'proof_credit': 'NONE'}
        old_group_receipt = read(OLD / 'evidence' / gid / 'receipt.json')
        old_export = read(OLD / 'evidence' / gid / 'export.json')
        global_export_diff = {key: {'s106': old_export.get(key), 's107': stock.get(key)}
            for key in sorted(old_export.keys() | stock.keys()) if key != 'harnesses'
            and old_export.get(key) != stock.get(key)}
        group_config_diff = {key: {'s106': old_group_receipt.get(key), 's107': group.get(key)}
            for key in ('argv', 'effective_cfg', 'unwind', 'selectors', 'variant')
            if old_group_receipt.get(key) != group.get(key)}
        groups.append({'id': gid, 'row_ids': [x['row_id'] for x in meta['rows']],
            'job_id': job['id'], 'job_conclusion': job['conclusion'],
            'runner_exit': 0, 'runner_exit_assurance': 'INFERRED_FROM_RUNNER_MAIN_AND_SUCCESSFUL_JOB_STEP',
            'terminal_state': terminal['state'], 'group_state': group['state'], 'rich_state': rich['state'],
            'location_exceptions': len(rich['location_exceptions']), 'execution': without_previews(execution),
            'compile_elapsed_upper_bound_seconds': comp['elapsed_upper_bound_seconds'], 'compile_exit_code': None,
            'snapshot_errors': group['snapshot_errors'], 'source_before_after': 'MATCHED_REQUEST',
            'same_run_binary_after_snapshot': 'RECORDED_MATCH', 'invocation_id': meta['invocation_id'],
            'native_metadata_files': len(meta['native_metadata']), 'native_metadata_bytes': sum(e['bytes'] for e in meta['native_metadata']),
            'metadata_state': meta['state'], 'binding_gaps': UNKNOWN,
            's106_comparison': {'group_state': old_groups[gid]['group_state'],
                'global_export_changes': global_export_diff, 'group_config_changes': group_config_diff,
                'rich_state': old_groups[gid]['rich_state'],
                'binary_after_present': bool(old_group_receipt.get('tool_fingerprints_after')),
                'before_binary_hashes_equal': {k: v['sha256'] for k, v in before['binaries'].items()} ==
                    {k: v['sha256'] for k, v in old_group_receipt['tool_fingerprints_before']['binaries'].items()},
                's106_before_binaries': old_group_receipt['tool_fingerprints_before']['binaries'],
                's107_before_binaries': before['binaries'],
                'elapsed_seconds': old_groups[gid]['execution']['elapsed_seconds'],
                'compile_elapsed_upper_bound_seconds': old_groups[gid]['compile_elapsed_upper_bound_seconds'],
                'rss_peak_kib': old_groups[gid]['execution']['rss_peak_kib']}, 'proof_credit': 'NONE'})
        provenance.append({'artifact': root.name, 'github_id': artifact['id'],
            'github_zip_digest': artifact['digest'], 'zip_bytes': zipinfo['bytes'],
            'zip_digest_verification': 'DOWNLOAD_ATTESTATION_MATCHED_ZIP_BYTES_BEFORE_EXTRACTION; ZIP_NOT_RETAINED',
            'payload_sha256': sha((root / 'group-evidence.json.gz').read_bytes()), 'uncompressed_bytes': raw_size,
            'entries': {k: {a: v[a] for a in ('sha256', 'bytes')} for k, v in doc['files'].items()},
            'projections': {str(p.relative_to(HERE)): sha(p.read_bytes()) for p in sorted(dest.rglob('*.json'))},
            'projection_note': 'export/rich/binding metadata exact bytes; receipt projections remove stdout/stderr previews'})
    old_policy = read(OLD / 'accept-v2/LOCATION-POLICY.json')
    fields = ('group', 'selector', 'id', 'class', 'description', 'status', 'location_display')
    expected_locations = sorted(tuple(p[k] for k in fields) for p in old_policy['records'])
    actual_locations = sorted(tuple(({**p, **p['property']})[k] for k in fields) for p in locations)
    require(expected_locations == actual_locations and len(locations) == 18 and
            len({p['property']['id'] for p in locations}) == 2, 'exact S1-06 location tuples')
    require(len({g['invocation_id'] for g in groups}) == 14, 'distinct invocation namespaces')
    collected = without_previews(collected)
    collected.update(schema='s107-intake-v1', run=RUN, control_sha=EXECUTED, fix_control_sha=CANDIDATE,
                     control_tree=TREE, groups=groups, qualified_acceptance='PENDING_OFFLINE_W11',
                     assurance='SOURCE_REPORTED_VERDICTS; EXACT_STRUCTURED_INVENTORY_REPLAY; NO_INDEPENDENT_B1_OR_B2_CREDIT')
    rows = collected['rows']
    totals = {'groups': len(groups), 'rows': len(rows), 'source_success': sum(x['evidence']['raw_outcome']['verdict'] == 'SUCCESS' for x in rows),
        'source_failure': sum(x['evidence']['raw_outcome']['verdict'] == 'FAILURE' for x in rows),
        'stock_properties': sum(x['evidence']['stock_property_count'] for x in rows),
        'retained_rich_properties': sum(x['evidence']['retained_rich_property_count'] for x in rows),
        'rich_complete_groups': sum(x['rich_state'] == 'COMPLETE' for x in groups),
        'binary_before_after_match_groups': len(groups), 'location_exception_observations': len(locations),
        'location_exception_unique_ids': len({p['property']['id'] for p in locations}),
        'native_metadata_files': native_count, 'native_metadata_bytes': native_bytes,
        'checks_unreachable': sum(len(x['evidence']['stock_checks']['unreachable']) for x in rows),
        'covers_satisfied': sum(len(x['evidence']['stock_covers']['satisfied']) for x in rows),
        'covers_unreachable': sum(len(x['evidence']['stock_covers']['unreachable']) for x in rows),
        'group_elapsed_seconds_sum': round(sum(x['execution']['elapsed_seconds'] for x in groups), 3),
        'group_peak_rss_kib_max': max(x['execution']['rss_peak_kib'] for x in groups),
        'compile_elapsed_upper_bound_seconds_sum': round(sum(x['compile_elapsed_upper_bound_seconds'] for x in groups), 3),
        'proof_credit': 'NONE'}
    require(totals['stock_properties'] == totals['retained_rich_properties'] == 9986, 'expected property total')
    comparison = {'s106_run': 43889560779, 's107_run': RUN, 'proof_request_changes': request_diffs,
        'nonproof_request_changes': nonproof_request_diffs,
        'all_verdicts_equal': all(x['verdict_equal'] for x in comparisons),
        'all_property_counts_equal': all(x['property_count_equal'] for x in comparisons),
        'all_rich_records_equal': all(not any(x['rich_inventory'][k] for k in ('added', 'removed', 'changed')) for x in comparisons),
        'rich_record_order_changed_rows': sum(not x['rich_inventory']['order_equal'] for x in comparisons),
        'stock_harness_list_order_changed_rows': sum(bool(x['stock_harness_changes_except_resources']) for x in comparisons),
        'all_nonresource_stock_differences_are_list_order_only': all(x['stock_harness_differences_are_list_order_only'] for x in comparisons),
        'rows': comparisons, 'note': 'All differing rich fields and non-resource stock harness fields retained; measurement changes reported separately.'}
    write('collected.json', collected)
    write('TOTALS.json', totals)
    write('COMPARISON-S1-06.json', comparison)
    write('LOCATION-EXCEPTIONS.json', {'policy': request['location_exception_policy'], 'matches_s106_exact_tuples': True, 'records': locations})
    write('PROVENANCE.json', provenance)
    write('VALIDATION.json', {'state': 'PASS_STRUCTURED_INTAKE', 'run': RUN,
        'checks': ['14 ZIP download digest attestations; saved payload/member SHA256 and byte lengths',
                   'run/job/artifact/control sibling tree/std/tool/request/variant/config identities',
                   'pinned unchanged S1-07 collector replay; 35 rows OBSERVED/RECORDED',
                   '9986 exact stock/rich properties reconciled; 18 exceptions / 2 IDs equal S1-06 tuples',
                   'fixed three before/after hashes; protected phase/completion/child shutdown; original exits',
                   'native JSON bytes/digests and unique exact selector/crate refs; manifests checked',
                   'source expected verdicts; full S1-06 rich-record and stock-harness comparison'],
        'qualified_acceptance': 'PENDING_OFFLINE_W11', 'local_verifier_execution': 'NOT_RUN', 'proof_credit': 'NONE'})
    print(json.dumps({'totals': totals, 'comparison': {k: v for k, v in comparison.items()
                      if k not in ('rows', 'proof_request_changes', 'nonproof_request_changes')},
                      'proof_request_changed_keys': list(request_diffs)}, sort_keys=True))


if __name__ == '__main__':
    main()
