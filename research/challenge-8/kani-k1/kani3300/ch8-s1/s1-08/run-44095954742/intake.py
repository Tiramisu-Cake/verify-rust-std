#!/usr/bin/env python3
"""Replay structured S1-08 evidence only; no compiler, verifier or raw log reads."""
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
OLD = HERE.parent.parent / 's1-07/run-43923266772'
CONTROL = Path('/root/kani-ch8-s1-08-w13')
STD = Path('/root/verify-rust-std-ch8-s1-08-w13')
CANDIDATE = '7c41333f9bfcfd7eb4e0ede7bd316443090c9025'
EXECUTED = '21592884db439389364b416dea1515bfa9d8018e'
TREE = '7ba8030690596cb491d1ae4f44e32805aa25931e'
RUN = 44095954742
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
            'changed': [{'id': key, 'fields': {field: {'s107': a[key].get(field), 's108': b[key].get(field)}
                         for field in sorted(a[key].keys() | b[key].keys())
                         if a[key].get(field) != b[key].get(field)}}
                        for key in sorted(a.keys() & b.keys()) if a[key] != b[key]],
            'order_equal': [p['id'] for p in old] == [p['id'] for p in new]}


def union_domain(unions):
    # Reviewed role-label and offline qualification metadata do not change
    # executed member selectors/domain or required cover predicates.
    label_metadata = {'required_success_messages', 'required_success_roles', 'qualification'}
    return [{k: v for k, v in u.items() if k not in label_metadata} for u in unions]


def main():
    pins = read(HERE.parent.parent / 's1-08-postrun/INPUTS.json')
    require(git(CONTROL, 'rev-parse', EXECUTED + '^{tree}') ==
            git(CONTROL, 'rev-parse', CANDIDATE + '^{tree}') == TREE, 'reviewed/executed tree')
    request_bytes = (HERE / 'CI-REQUEST.json').read_bytes()
    require(sha(request_bytes) == pins['request']['embedded_sha256'], 'embedded request pin')
    request = json.loads(request_bytes)
    for rel, expected in request['ci_payload_sha256'].items():
        raw = subprocess.check_output(['git', '-C', str(CONTROL), 'show', EXECUTED + ':' + rel])
        require(sha(raw) == expected, 'executed control payload: ' + rel)
        if rel.startswith('ch8-s1-control/'):
            require((HERE / 'replay-control' / rel.removeprefix('ch8-s1-control/')).read_bytes() == raw,
                    'replay control pin: ' + rel)
    require((HERE / 'replay-control/CI-REQUEST.json').read_bytes() == request_bytes, 'collector request')
    sys.path.insert(0, str(HERE / 'replay-control'))
    r, collector = importlib.import_module('runner'), importlib.import_module('collect')
    require(r.load_request() == request, 'producer request validation')
    require(git(STD, 'rev-parse', request['std_sha'] + '^{tree}') == request['std_tree'] and
            git(CONTROL, 'rev-parse', request['tool_sha'] + '^{tree}') == request['tool_tree'], 'source/tool tree')
    for rel, expected in request['changed_file_sha256'].items():
        raw = subprocess.check_output(['git', '-C', str(STD), 'show', request['std_sha'] + ':' + rel])
        require(sha(raw) == expected, 'pinned std file: ' + rel)
    require(sha((HERE / 'ROLE-MAP.json').read_bytes()) == pins['request']['role_map_sha256'], 'role map pin')
    identity, artifacts, jobs = map(read, (HERE / 'run-identity.json', HERE / 'artifacts-metadata.json',
                                         HERE / 'jobs-metadata.json'))
    require(identity['id'] == RUN and identity['head_sha'] == EXECUTED and identity['run_attempt'] == 1
            and identity['status'] == 'completed' and identity['conclusion'] == 'failure'
            and identity['head_branch'] == 'uninit-ci/ch8-s1k-j' and identity['event'] == 'push'
            and identity['path'] == '.github/workflows/ch8-s1.yml'
            and identity['head_commit']['tree_id'] == TREE, 'terminal run identity')
    require(len(jobs['jobs']) == 14 and sum(j['conclusion'] == 'success' for j in jobs['jobs']) == 13,
            'terminal 13 success jobs')
    failed, = [j for j in jobs['jobs'] if j['conclusion'] != 'success']
    require(failed['name'].endswith('(cell-u34)') and failed['conclusion'] == 'failure', 'cell failed only')
    roots = sorted((HERE / 'artifacts').iterdir())
    require(len(roots) == 13 and len(artifacts['artifacts']) == 14 and
            {p.name for p in roots} == {a['name'] for a in artifacts['artifacts']
                                      if not a['name'].endswith('-cell-u34')}, '13 artifacts exclude cell')
    collected = collector.collect(roots, request)
    require(collected['missing_groups'] == ['cell-u34'] and len(collected['rows']) == 35, 'partial matrix')
    require(sum(x['outcome'] == 'RECORDED' and x['status'] == 'OBSERVED' for x in collected['rows']) == 33,
            '33 complete row observations')
    write('runner-collected.json', without_previews(collected))
    byid = {x['id']: x for x in collected['rows']}
    old_collected = read(OLD / 'collected.json')
    old_rows = {x['id']: x for x in old_collected['rows']}
    old_groups = {x['id']: x for x in old_collected['groups']}
    old_request = read(OLD / 'CI-REQUEST.json')
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
            harness_diff = {key: {'s107': h_old.get(key), 's108': harness.get(key)}
                            for key in sorted(h_old.keys() | harness.keys())
                            if key != 'resources' and h_old.get(key) != harness.get(key)}
            order_only = True
            for key, values in harness_diff.items():
                if key == 'checks':
                    def buckets(v):
                        return {k: sorted(x) if isinstance(x, list) else x for k, x in v.items()}
                    order_only &= buckets(values['s107']) == buckets(values['s108'])
                elif key == 'unsupported_constructs':
                    order_only &= sorted(values['s107'], key=lambda p: p['id']) == sorted(values['s108'], key=lambda p: p['id'])
                else:
                    order_only = False
            comparisons.append({'id': rid, 'group': gid,
                'verdict_equal': harness['outcome'] == old_rows[rid]['evidence']['raw_outcome'],
                'property_count_equal': harness['n_properties'] == h_old['n_properties'],
                'rich_inventory': inventory_diff, 'stock_harness_changes_except_resources': harness_diff,
                'stock_harness_differences_are_list_order_only': order_only,
                'verification_time_s': {'s107': h_old['resources']['verification_time_s'],
                                        's108': harness['resources']['verification_time_s']}})
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
        global_export_diff = {key: {'s107': old_export.get(key), 's108': stock.get(key)}
            for key in sorted(old_export.keys() | stock.keys()) if key != 'harnesses'
            and old_export.get(key) != stock.get(key)}
        group_config_diff = {key: {'s107': old_group_receipt.get(key), 's108': group.get(key)}
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
            's107_comparison': {'group_state': old_groups[gid]['group_state'],
                'global_export_changes': global_export_diff, 'group_config_changes': group_config_diff,
                'rich_state': old_groups[gid]['rich_state'],
                'binary_after_present': bool(old_group_receipt.get('tool_fingerprints_after')),
                'before_binary_hashes_equal': {k: v['sha256'] for k, v in before['binaries'].items()} ==
                    {k: v['sha256'] for k, v in old_group_receipt['tool_fingerprints_before']['binaries'].items()},
                's107_before_binaries': old_group_receipt['tool_fingerprints_before']['binaries'],
                's108_before_binaries': before['binaries'],
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
    finish(collected, groups, provenance, locations, comparisons, request, native_count, native_bytes)

def merge_diagnostic_row(observed, projection, harness):
    require(observed['id'] == projection['id'] and projection['group'] == 'cell-u34', 'diagnostic row identity')
    require(projection['selector'] == harness['name'], 'diagnostic harness identity')
    require(projection['status'] == projection['outcome'] == 'UNKNOWN', 'diagnostic cannot promote incomplete row')
    return {**observed, **projection, 'group_admitted': False, 'qualified_acceptance': 'PENDING_OFFLINE'}


def finish(collected, groups, provenance, locations, comparisons, request, native_count, native_bytes):
    from timing import measure, summarize
    diagnostic = HERE / 'cell-diagnostic'
    diag_commit = git(HERE, 'rev-parse', '929f21bb1f')
    diag_hashes = {}
    for line in (diagnostic / 'MANIFEST.sha256').read_text().splitlines():
        digest, rel = line.split('  ', 1)
        require('..' not in Path(rel).parts and not Path(rel).is_absolute(), 'diagnostic path')
        raw = (diagnostic / rel).read_bytes()
        require(sha(raw) == digest, 'diagnostic manifest: ' + rel)
        repo_rel = str((diagnostic / rel).relative_to(Path(git(HERE, 'rev-parse', '--show-toplevel'))))
        require(raw == subprocess.check_output(['git', '-C', str(HERE), 'show', diag_commit + ':' + repo_rel]),
                'immutable diagnostic commit: ' + rel)
        diag_hashes['cell-diagnostic/' + rel] = digest
    manifest_raw = (diagnostic / 'MANIFEST.sha256').read_bytes()
    manifest_rel = str((diagnostic / 'MANIFEST.sha256').relative_to(Path(git(HERE, 'rev-parse', '--show-toplevel'))))
    require(manifest_raw == subprocess.check_output(['git', '-C', str(HERE), 'show', diag_commit + ':' + manifest_rel]),
            'immutable diagnostic manifest')
    diag_hashes['cell-diagnostic/MANIFEST.sha256'] = sha(manifest_raw)
    diag_artifact = read(diagnostic / 'ARTIFACT-METADATA.json')
    artifact, = [a for a in read(HERE / 'artifacts-metadata.json')['artifacts'] if a['name'].endswith('-cell-u34')]
    require(all(artifact[k] == diag_artifact[k] for k in ('id', 'digest', 'size_in_bytes', 'workflow_run')),
            'same-run diagnostic artifact identity')
    cell = read(diagnostic / 'structured/receipt.json')
    cell_export = read(diagnostic / 'structured/export.json')
    cell_rich = read(diagnostic / 'RICH-PROJECTION.json')
    binding = read(diagnostic / 'BINDING-PROJECTION.json')
    require(cell['request_sha256'] == sha((HERE / 'CI-REQUEST.json').read_bytes()) and
            cell['state'] == 'FAILED' and cell_rich['metadata']['state'] == 'INCOMPLETE', 'cell partial identities')
    diagnostic_rows = read(diagnostic / 'ROW-PROJECTION.json')['rows']
    rows = collected['rows']
    byid = {x['id']: x for x in rows}
    for row in diagnostic_rows:
        native, = [n for n in binding['rows'] if n['row_id'] == row['id']]
        harness, = [h for h in cell_export['harnesses'] if h['name'] == row['selector']]
        byid[row['id']].update(merge_diagnostic_row(byid[row['id']], row, harness))
        byid[row['id']]['evidence'] = {
            'raw_outcome': harness['outcome'], 'verification_time_s': harness['resources']['verification_time_s'],
            'stock_property_count': harness['n_properties'],
            'retained_rich_property_count': None, 'rich_inventory_complete': False,
            'rich_inventory_ref': 'cell-diagnostic/RICH-PROJECTION.json',
            'rich_inventory_scope': 'PARTIAL_PROJECTION; stable absent, unstable 301 reported, 8 labels retained',
            'stock_checks': harness.get('checks'), 'stock_covers': harness.get('covers'),
            'failed_properties': harness.get('failed_properties'),
            'group_original_exit': cell['execution']['original_exit_code'],
            'group_original_exception': cell['original_exception'],
            'execution_exception': cell.get('execution_exception'),
            'group_elapsed_seconds': cell['execution']['elapsed_seconds'],
            'group_rss_peak_kib': cell['execution']['rss_peak_kib'],
            'per_root_original_exit': None, 'per_root_wall_seconds': None, 'per_root_rss_kib': None,
            'per_root_measurement_scope': 'UNKNOWN_NO_SEPARATE_PROCESS_ATTRIBUTION',
            'native_harness_records': native['native_harness_records'], 'binding_gaps': native['binding_gaps'],
            'native_metadata_container': 'cell-diagnostic/BINDING-PROJECTION.json',
            'stock_export_ref': 'cell-diagnostic/structured/export.json',
            'qualified_acceptance': 'PENDING_OFFLINE', 'group_admitted': False, 'proof_credit': 'NONE'}
    groups.append({'id': 'cell-u34', 'group_state': cell['state'], 'rich_state': 'INCOMPLETE',
                   'row_ids': [x['id'] for x in diagnostic_rows], 'job_conclusion': 'failure',
                   'job_id': read(diagnostic / 'JOB-METADATA.json')['id'],
                   'execution': without_previews(cell['execution']),
                   'original_exception': cell['original_exception'], 'execution_exception': cell.get('execution_exception'),
                   'invocation_id': cell['invocation_id'], 'group_admitted': False,
                   'source_ref': 'cell-diagnostic/structured/receipt.json', 'proof_credit': 'NONE'})
    require(len({g['invocation_id'] for g in groups}) == 14, 'unique invocation namespaces')
    complete_rows = [x for x in rows if x['status'] == 'OBSERVED' and x['outcome'] == 'RECORDED']
    require(len(complete_rows) == 33 and all(x['outcome'] == 'UNKNOWN' for x in diagnostic_rows), 'partial row preservation')
    collected.update(schema='s108-intake13-v1', run=RUN, attempt=1, control_sha=EXECUTED,
                     control_tree=TREE, groups=groups, state='PARTIAL_MATRIX_13_COMPLETE_GROUPS',
                     incomplete_groups=['cell-u34'], qualified_acceptance='PENDING_OFFLINE',
                     assurance='SOURCE_REPORTED; STRUCTURED_INTEGRITY_REPLAY; NO_INDEPENDENT_B1_OR_B2_CREDIT')
    totals = {'declared_groups': 14, 'complete_groups': 13, 'incomplete_groups': 1,
              'declared_rows': len(rows), 'complete_rows': len(complete_rows), 'diagnostic_unknown_rows': 2,
              'complete_source_success': sum(x['evidence']['raw_outcome'].get('verdict') == 'SUCCESS' for x in complete_rows),
              'complete_source_failure': sum(x['evidence']['raw_outcome'].get('verdict') == 'FAILURE' for x in complete_rows),
              'stock_properties_complete_groups': sum(x['evidence']['stock_property_count'] for x in complete_rows),
              'rich_properties_complete_groups': sum(x['evidence']['retained_rich_property_count'] for x in complete_rows),
              'cell_source_observations': {x['id']: x['evidence']['raw_outcome'] for x in rows if x['group'] == 'cell-u34'},
              'complete_groups_native_metadata_files': native_count, 'complete_groups_native_metadata_bytes': native_bytes,
              'location_exception_observations_complete_groups': len(locations),
              'checks_unreachable_complete_groups': sum(len(x['evidence']['stock_checks']['unreachable']) for x in complete_rows),
              'covers_satisfied_complete_groups': sum(len(x['evidence']['stock_covers']['satisfied']) for x in complete_rows),
              'covers_unreachable_complete_groups': sum(len(x['evidence']['stock_covers']['unreachable']) for x in complete_rows),
              'proof_credit': 'NONE'}
    require(totals['stock_properties_complete_groups'] == totals['rich_properties_complete_groups'], 'stock/rich reconciliation')
    # Diagnostic tuple comparison against already recorded approved S1-07 observations.
    # No quantity quota and no new exception policy or admission.
    approved = read(OLD / 'LOCATION-EXCEPTIONS.json')['records']
    fields = ('group', 'selector', 'id', 'class', 'description', 'status', 'location_display')
    def tuple_key(record):
        flat = {**record, **record['property']}
        return tuple(flat.get(k) for k in fields)
    permitted = {tuple_key(p) for p in approved}
    location_comparison = {'records': locations,
        'matches_prior_approved_tuple': [tuple_key(p) in permitted for p in locations],
        'policy': request['location_exception_policy'], 'admission': 'PENDING_OFFLINE_EXACT_TUPLE_POLICY'}
    # Fresh diagnostics only. No historical candidate IDs are consumed here.
    role_map = read(HERE / 'ROLE-MAP.json')
    coverage = []
    for role in role_map['required_success_bindings']:
        row = byid[role['row_id']]
        partial = row['group'] == 'cell-u34'
        if partial:
            props = [p for p in cell_rich['label_properties'] if p['id'].startswith(role['selector'] + '.')]
        else:
            rich = read(HERE / 'evidence' / row['group'] / 'properties.json')
            props, = [h['properties'] for h in rich['harnesses'] if h['name'] == role['selector']]
        allowed = {str(x) for x in role['source']['allowed_property_lines']}
        matches = [p for p in props if p['class'] == 'assertion' and p['description'] == role['expected_description']
                   and p.get('line') in allowed and isinstance(p.get('file'), str)
                   and p['file'].endswith('/' + role['source']['file'])]
        exact = role['binding_kind'] == 'EXACT_ROLE_LABEL'
        status = ('FOUND' if exact and len(matches) == 1 else 'DUPLICATE' if exact and len(matches) > 1
                  else 'MISSING' if exact and not partial else 'UNKNOWN_PARTIAL' if exact
                  else 'CANDIDATES_REQUIRE_FRESH_SEMANTIC_AUDIT')
        coverage.append({'row_id': role['row_id'], 'selector': role['selector'], 'root': role['root'],
                         'role': role['role'], 'binding_kind': role['binding_kind'],
                         'expected_description': role['expected_description'], 'diagnostic_status': status,
                         'inventory_complete': not partial, 'group_admitted': False,
                         'properties': matches, 'semantic_set_completeness': 'PENDING_OFFLINE' if not exact else None,
                         'qualification': 'PENDING_OFFLINE', 'proof_credit': 'NONE'})
    write('LABEL-COVERAGE.json', {'scope': 'DIAGNOSTIC_ONLY; no role admission or historical IDs reused',
                                'new_labels': [x for x in coverage if x['binding_kind'] == 'EXACT_ROLE_LABEL'],
                                'preserved_semantic_bindings': [x for x in coverage if x['binding_kind'] != 'EXACT_ROLE_LABEL']})
    # Compare every declared common logical row. Production and mutants join separately.
    old_request = read(OLD / 'CI-REQUEST.json')
    pins = read(HERE.parent.parent / 's1-08-postrun/INPUTS.json')
    require(old_request['std_sha'] == pins['timing_comparison']['baseline_source_sha'], 'timing baseline source pin')
    old_rows = {x['id']: x for x in old_request['rows']}
    join_fields = ('id', 'selector', 'source_qualified_selector', 'variant', 'mode', 'target', 'type', 'N',
                   'threshold', 'unwind', 'expected', 'failure_description', 'required_cover_count',
                   'required_cover_messages', 'timeout_seconds', 'companion')
    timings, unpaired = [], []
    timing_refs = {}
    for row in request['rows']:
        rid, gid = row['id'], byid[row['id']]['group']
        if rid not in old_rows:
            unpaired.append({'side': 's108', 'row_id': rid}); continue
        old_row = old_rows[rid]
        a_export_path = OLD / 'evidence' / gid / 'export.json'
        a_receipt_path = OLD / 'evidence' / gid / 'receipt.json'
        b_export_path = HERE / ('cell-diagnostic/structured/export.json' if gid == 'cell-u34' else 'evidence/' + gid + '/export.json')
        b_receipt_path = HERE / ('cell-diagnostic/structured/receipt.json' if gid == 'cell-u34' else 'evidence/' + gid + '/receipt.json')
        ae, be, ar, br = map(read, (a_export_path, b_export_path, a_receipt_path, b_receipt_path))
        ah, = [h for h in ae['harnesses'] if h['name'] == old_row['selector']]
        bh, = [h for h in be['harnesses'] if h['name'] == row['selector']]
        mismatches = {key: {'s107': old_row.get(key), 's108': row.get(key)} for key in join_fields
                      if old_row.get(key) != row.get(key)}
        # Check any additional row domain fields; only reviewed message/oracle
        # source-coordinate metadata and planning/state fields are excluded.
        for key in row.keys() | old_row.keys():
            if key not in set(join_fields) | {'required_success_messages', 'oracle', 'planned_seconds', 'state', 'oracle_status'}:
                if old_row.get(key) != row.get(key):
                    mismatches['row.' + key] = {'s107': old_row.get(key), 's108': row.get(key)}
        oracle_keys = ('selector', 'class', 'status', 'description', 'source_line', 'intended_message',
                       'require_only_this_failure', 'companion', 'companion_required_cover_messages',
                       'companion_required_status', 'mutant_return_cover_status')
        for key in oracle_keys:
            a, b = old_row.get('oracle', {}).get(key), row.get('oracle', {}).get(key)
            if a != b: mismatches['oracle.' + key] = {'s107': a, 's108': b}
        if union_domain(old_request['replacement_unions']) != union_domain(request['replacement_unions']):
            mismatches['request.replacement_unions'] = {'s107': union_domain(old_request['replacement_unions']),
                                                       's108': union_domain(request['replacement_unions'])}
        for key in ('flags', 'tool_sha', 'tool_tree', 'execution_groups', 'budgets', 'variants'):
            if old_request[key] != request[key]: mismatches['request.' + key] = {'s107': old_request[key], 's108': request[key]}
        for key in ('configuration', 'target', 'enabled_unstable_features', 'harness_timeout_s', 'tools', 'kani_commit', 'kani_commit_dirty'):
            if ae.get(key) != be.get(key): mismatches['export.' + key] = {'s107': ae.get(key), 's108': be.get(key)}
        for key in ('argv', 'effective_cfg', 'unwind', 'selectors', 'variant'):
            if ar.get(key) != br.get(key): mismatches['group.' + key] = {'s107': ar.get(key), 's108': br.get(key)}
        for phase in ('before', 'after'):
            snap = 'tool_fingerprints_' + phase
            a = {k: v['sha256'] for k, v in ar[snap]['binaries'].items()}
            b = {k: v['sha256'] for k, v in br[snap]['binaries'].items()}
            if a != b: mismatches[snap] = {'s107': a, 's108': b}
        for key in ('crate', 'file', 'mode', 'selector', 'target'):
            a, b = old_request['source_bindings'][rid].get(key), request['source_bindings'][rid].get(key)
            if a != b: mismatches['source_binding.' + key] = {'s107': a, 's108': b}
        compatible = not mismatches
        measured = measure(ah, bh, row['expected'], compatible, row['timeout_seconds'])
        paths = [a_export_path, b_export_path, a_receipt_path, b_receipt_path]
        refs = []
        for path in paths:
            rel = str(path.relative_to(HERE)) if path.is_relative_to(HERE) else '../../s1-07/run-43923266772/' + str(path.relative_to(OLD))
            timing_refs[rel] = sha(path.read_bytes()); refs.append(rel)
        timings.append({'row_id': rid, 'group': gid, 'join_key': {k: row.get(k) for k in join_fields},
                        'compatible': compatible, 'incompatible_dimensions': mismatches,
                        'expected_source_delta': {'s107': old_request['std_sha'], 's108': request['std_sha'],
                                                  'kind': 'REVIEWED_LABEL_ONLY_5be_TO_99e'},
                        's107_required_messages': old_row['required_success_messages'],
                        's108_required_messages': row['required_success_messages'],
                        'limits': {'s107_per_harness_s': old_row['timeout_seconds'],
                                   's108_per_harness_s': row['timeout_seconds'],
                                   's107_group_s': ar.get('group_budget_seconds'), 's108_group_s': br.get('group_budget_seconds')},
                        's108_evidence_scope': 'DIAGNOSTIC_FAILED_GROUP_NOT_ADMITTED' if gid == 'cell-u34' else 'COMPLETE_GROUP_PENDING_OFFLINE',
                        'evidence_refs': refs, **measured})
    unpaired.extend({'side': 's107', 'row_id': rid} for rid in old_rows if rid not in byid)
    summary = summarize(timings)
    timing_doc = {'schema': 's108-timing-comparison-v1', 's107_run': 43923266772, 's108_run': RUN,
                  'attempts': [1, 1], 'field': 'harness.resources.verification_time_s', 'rows': timings,
                  'unpaired': unpaired, 'cohorts': summary, 'evidence_sha256': timing_refs,
                  'interpretation': 'Descriptive stock producer measurements; not pure solver time; group/job/compile wall never substituted. No causal claim for kani::assert or labels.',
                  'future_retry': 'EXCLUDED; no retry evidence read', 'missing_values': 'UNKNOWN/null; never zero',
                  'source_delta': 'Reviewed assertion labels and source positions disclosed; all other domain/config dimensions checked separately'}
    write('TIMING-COMPARISON.json', timing_doc)
    table = ['# S1-07 → S1-08 timings', '',
             'Field: `harness.resources.verification_time_s`; source5be→99e is the reviewed label delta. '
             'All other domain/config, variant, flags, tool and measured binary dimensions are checked per pair. '
             'These are descriptive producer measurements, not pure solver time. No causal claim for labels/kani::assert. '
             'Cell values come only from immutable diagnostic refs; the failed group stays unadmitted. Retry1200s excluded.', '',
             '| Row / variant | Outcomes 07 → 08 | seconds 07 | seconds 08 | Δ s | completed ratio | cohort | compatible |',
             '|---|---|---:|---:|---:|---:|---|---|']
    def show(v): return 'UNKNOWN' if v is None else f'{v:.9g}'
    for t in timings:
        outcomes = [o.get('verdict', o.get('kind', 'UNKNOWN')) for o in (t['s107_outcome'], t['s108_outcome'])]
        table.append(f"| {t['row_id']} / {t['join_key']['variant']} | {' → '.join(outcomes)} | {show(t['s107_raw_verification_time_s'])} | {show(t['s108_raw_verification_time_s'])} | {show(t['delta_s'])} | {show(t['completed_ratio_s108_over_s107'])} | {t['cohort']} | {t['compatible']} |")
    table += ['', 'Cohorts (kept separate):', '', '```json', json.dumps(summary, indent=2), '```', '',
              'TIMEOUT is censored: stable_default_cell observed600.031112420s at600s cutoff. '
              'The JSON records the conditional completion-time lower bound relative to the completed baseline; '
              'it is excluded from completed ratios. Missing inventories and null durations are UNKNOWN, never zero.', '',
              f'Common pairs: {len(timings)}; incompatible: {sum(not x["compatible"] for x in timings)}; unpaired: {len(unpaired)}. '
              'Exact outcomes, limits, join dimensions, expected message differences and evidence hashes are in TIMING-COMPARISON.json.']
    (HERE / 'TIMING-COMPARISON.md').write_text('\n'.join(table) + '\n')
    write('collected.json', collected)
    write('TOTALS.json', totals)
    write('LOCATION-EXCEPTIONS.json', location_comparison)
    write('COMPARISON-S1-07.json', {'rows': comparisons,
          'request_differences': {k: {'s107': old_request.get(k), 's108': request.get(k)}
                                  for k in sorted(old_request.keys() | request.keys())
                                  if old_request.get(k) != request.get(k)},
          'expected_source_delta': 'REVIEWED_LABEL_ONLY_5be_TO_99e; no causal runtime attribution',
          'cell': 'SUCCESS/SUCCESS baseline → TIMEOUT/source SUCCESS; both collector statuses UNKNOWN in failed group',
          'note': 'All fresh rich property differences retained; no 9986/187/18 quota imposed'})
    write('PROVENANCE.json', {'success_artifacts': provenance, 'cell_diagnostic_commit': diag_commit,
                            'cell_read_only_refs_sha256': diag_hashes,
                            'metadata_transport': 'GitHub connector; compact artifacts only; no logs; ZIP digest before extraction',
                            'source_identity_assurance': 'Artifact-reported snapshots cross-checked against exact Git pins; AST/MIR provenance UNKNOWN',
                            'proof_credit': 'NONE'})
    write('INPUTS.json', {'task_commit': '9e94c809ad5781542da3c63efe6655084e5a9a4f',
                         'pins_path': '../../s1-08-postrun/INPUTS.json',
                         'pins_sha256': sha((HERE.parent.parent / 's1-08-postrun/INPUTS.json').read_bytes()),
                         'request_sha256': sha((HERE / 'CI-REQUEST.json').read_bytes()),
                         'role_map_sha256': sha((HERE / 'ROLE-MAP.json').read_bytes()),
                         'executed_control': EXECUTED, 'reviewed_control': CANDIDATE, 'control_tree': TREE,
                         'source_sha': request['std_sha'], 'tool_sha': request['tool_sha'],
                         'baseline_request_sha256': sha((OLD / 'CI-REQUEST.json').read_bytes()),
                         'baseline_collected_sha256': sha((OLD / 'collected.json').read_bytes()),
                         'diagnostic_commit': diag_commit, 'writes_exclude': ['cell-diagnostic/', 'accept/']})
    write('VALIDATION.json', {'state': 'PASS_INTAKE13_WITH_EXPLICIT_CELL_PARTIAL',
          'checks': ['13 GitHub ZIP digests matched before extraction; bounded embedded bytes/SHA256/schema/namespace checks',
                     'terminal exact run/head/tree/attempt/request/source/tool/config/variant identities',
                     'executed collector replay: 33 OBSERVED RECORDED rows, cell missing_groups preserved',
                     'complete stock/rich reconciliation, ID/status partitions, exact negative tuples and same-run companions',
                     'required before/after binary snapshots, shutdown/exits/exceptions and source invariance',
                     'native metadata member hashes, exact selector/crate refs and artifact links via exact producer collector',
                     'immutable diagnostic files match commit929f21bb1f and manifest; no cell artifact redownload',
                     'fresh 111 label diagnostics and 16 semantic candidate inventories, no historical ID transfer',
                     'all common logical rows timed with compatibility checks; censoring and cohorts separate'],
          'timing_common_pairs': len(timings), 'timing_incompatible_pairs': sum(not t['compatible'] for t in timings),
          'approved_location_tuple_matches': all(location_comparison['matches_prior_approved_tuple']),
          'qualified_acceptance': 'PENDING_OFFLINE', 'local_verifier_execution': 'NOT_RUN', 'proof_credit': 'NONE'})
    print(json.dumps({'totals': totals, 'timing_cohorts': summary,
                      'incompatible_pairs': sum(not t['compatible'] for t in timings),
                      'new_label_statuses': {s: sum(x['diagnostic_status'] == s for x in coverage if x['binding_kind'] == 'EXACT_ROLE_LABEL')
                                             for s in sorted({x['diagnostic_status'] for x in coverage if x['binding_kind'] == 'EXACT_ROLE_LABEL'})}}, sort_keys=True))


if __name__ == '__main__':
    main()
