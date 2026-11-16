#!/usr/bin/env python3
"""Offline S1-07 policy receipt. No compiler, verifier, network or raw-log input.

Reads immutable structured projections, reconciles exact inventories, then adds
the coordinator's location exception and semantic binding analyses. Git is used
only to read pinned objects. Default mode compares the receipt; --write creates
only this directory's ACCEPT.json.
"""
import argparse
import collections
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
RUN = HERE.parent
BASELINE = RUN.parent.parent / 's1-06/run-43889560779/accept-v2'
sys.path.insert(0, str(BASELINE))
sys.path.insert(0, str(HERE))
STD = Path('/root/verify-rust-std-ch8-s1-04-w13')
CONTROL = Path('/root/kani-ch8-s1-07-w13')
SOURCE_SHA = '5be85699b8826e3286c0bf89efb9affefac0acb5'
TOOL_SHA = '0aac16ef62da9e9d5645782d458593e5d78143ba'
CONTROL_SHA = 'b37f6f75c5b7b77e84297cd7104f9c0868502fd4'
ENTRY_SHA = '036c5c1a956ac2971588d508a71c592e3d71d143'
REQUEST_SHA = '6c483ce754cd8e99c01953bf4c40a145b10529d7990aa52c28ef32c00b980cd7'
EXPORT_PREFIX = '/home/runner/work/kani/kani/export/'
BINARIES = {'cbmc', 'kani_compiler', 'kani_driver'}
SORTING = 'slice::sort::shared::smallsort::'
MODEL = SORTING + 'verify::sorting_model::'
LOCATION_IDS = {
    SORTING + 'small_sort_general_with_scratch::<' + ty + ', ' + MODEL + 'KeyLess<' + ty + '>>.unreachable.1'
    for ty in ('u8', MODEL + 'NonCopyByte')
}
CHECK_BUCKETS = ('failure', 'unreachable', 'undetermined', 'error', 'unknown', 'other')
COVER_BUCKETS = ('satisfied', 'unsatisfiable', 'unreachable', 'undetermined', 'error', 'unknown', 'other')


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def read(path):
    return json.loads(path.read_bytes())


def digest(data):
    return hashlib.sha256(data).hexdigest()


def git_bytes(repo, revision, path):
    return subprocess.check_output(['git', '-C', str(repo), 'show', revision + ':' + path])


def tree(repo, revision):
    return subprocess.check_output(['git', '-C', str(repo), 'rev-parse', revision + '^{tree}'], text=True).strip()


def source_path(value):
    need(isinstance(value, str) and value.startswith(EXPORT_PREFIX), 'invalid export source path')
    return value[len(EXPORT_PREFIX):]


def inventory(h, properties):
    """Reconcile every ID/class/status and full special-record payload, not counts alone."""
    need(isinstance(properties, list) and properties, 'missing/empty rich inventory')
    need(all(isinstance(p, dict) for p in properties), 'wrong property type')
    by = {p.get('id'): p for p in properties}
    need(None not in by and '' not in by and len(by) == len(properties), 'missing/duplicate ID')
    need(all(isinstance(p['id'], str) and p['id'].rsplit('.', 2)[-2] == p.get('class') for p in properties), 'ID/class mismatch')
    checks, covers = h['checks'], h['covers']
    for buckets, names in ((checks, CHECK_BUCKETS), (covers, COVER_BUCKETS)):
        need(type(buckets['total']) is int and buckets['total'] >= 0, 'invalid total')
        for key in names:
            need(isinstance(buckets[key], list) and all(isinstance(x, str) and x for x in buckets[key]), 'bucket type')
            need(len(buckets[key]) == len(set(buckets[key])), 'duplicate bucket ID')
        need(not any(buckets[k] for k in ('undetermined', 'error', 'unknown', 'other')), 'unknown/incomplete status')
    need(not covers['unsatisfiable'], 'unsatisfied cover')
    need(type(checks['success']) is int and checks['success'] >= 0, 'success type')
    need(checks['total'] == checks['success'] + sum(len(checks[k]) for k in CHECK_BUCKETS), 'check partition')
    need(covers['total'] == sum(len(covers[k]) for k in COVER_BUCKETS), 'cover partition')
    need(h['n_properties'] == len(properties) == checks['total'] + covers['total'], 'property total')
    for names, buckets, is_cover in ((CHECK_BUCKETS, checks, False), (COVER_BUCKETS, covers, True)):
        for key in names:
            expected = {p['id'] for p in properties if (p.get('class') == 'cover') == is_cover and p.get('status') == key.upper()}
            need(set(buckets[key]) == expected, 'exact ID/class/status bucket mismatch:' + key)
    need(checks['success'] == sum(p.get('class') != 'cover' and p.get('status') == 'SUCCESS' for p in properties), 'success count')
    need(all(p.get('status') in ({'SATISFIED', 'UNREACHABLE'} if p.get('class') == 'cover' else {'SUCCESS', 'FAILURE', 'UNREACHABLE'}) for p in properties), 'unknown status')
    need(all(isinstance(p.get('class'), str) and p['class'] and isinstance(p.get('description'), str) and p['description'] and isinstance(p.get('location_display'), str) and p['location_display'] for p in properties), 'incomplete property fields')
    failures = [p for p in properties if p.get('status') == 'FAILURE']
    need(type(h['n_failed']) is int and h['n_failed'] == len(failures) == len(h['failed_properties']), 'failure count')
    for field, selected in (('failed_properties', failures), ('unsupported_constructs', [p for p in properties if p['class'] == 'unsupported_construct'])):
        exported = {p['id']: p for p in h[field]}
        need(len(exported) == len(h[field]) and set(exported) == {p['id'] for p in selected}, 'special record ID set:' + field)
        for p in selected:
            need(all(exported[p['id']].get(k) == p.get(k) for k in ('id', 'class', 'status', 'description', 'file', 'line')), 'special record mismatch:' + field)
    verdict = 'FAILURE' if failures else 'SUCCESS'
    need(h['outcome'] == {'kind': 'COMPLETED', 'verdict': verdict}, 'verdict/inventory mismatch')
    return by


def exception_key(record):
    return tuple(record.get(k) for k in ('group', 'selector', 'id', 'class', 'description', 'status', 'location_display'))


def location_exception(record, policy):
    """Exact approved tuples only; never repair file/line or remove the check."""
    return (record.get('id') in LOCATION_IDS and record.get('class') == 'unreachable'
            and record.get('status') == 'SUCCESS' and record.get('description') == 'unreachable code'
            and record.get('location_display') == 'library/core/src/lib.rs:0:0 in function ' + record['id'].rsplit('.unreachable.', 1)[0]
            and record.get('file') is None and record.get('line') is None
            and exception_key(record) in {exception_key(x) for x in policy['records']})


def binary_state(before, after):
    def valid(snapshot):
        if not isinstance(snapshot, dict) or snapshot.get('required_hashes_present') is not True:
            return False
        bins = snapshot.get('binaries')
        return isinstance(bins, dict) and set(bins) == BINARIES and all(
            isinstance(v, dict) and isinstance(v.get('path'), str) and v['path'] and
            re.fullmatch('[0-9a-f]{64}', str(v.get('sha256', ''))) for v in bins.values())
    if not valid(before) or not valid(after):
        return 'UNKNOWN_MISSING_REQUIRED_SNAPSHOT'
    return 'MATCH' if all(before['binaries'][k]['sha256'] == after['binaries'][k]['sha256'] for k in BINARIES) else 'UNKNOWN_BINARY_DRIFT'


def snapshot_gate(rec):
    state = binary_state(rec.get('tool_fingerprints_before'), rec.get('tool_fingerprints_after'))
    if state != 'MATCH':
        return state
    if rec.get('execution', {}).get('child_shutdown_verified') is not True or rec.get('snapshot_errors') != []:
        return 'UNKNOWN_SHUTDOWN_OR_SNAPSHOT_ERROR'
    for phase, field in [('BEFORE_CHILD', 'tool_fingerprints_before'), ('AFTER_CHILD_SHUTDOWN', 'tool_fingerprints_after')]:
        snap = rec[field]
        if not (snap.get('required_binaries') == ['kani_driver', 'kani_compiler', 'cbmc']
                and snap.get('missing_binaries') == [] and snap.get('phase') == phase
                and snap.get('snapshot_completed') is True and snap.get('state') == 'COMPLETE'):
            return 'UNKNOWN_SNAPSHOT_PHASE_OR_COMPLETION'
    return 'MATCH'


def negative_oracle(row, h, by, request):
    if row['expected'] != 'DETECTED':
        need(row['expected'] == 'SUCCESS' and h['outcome']['verdict'] == 'SUCCESS', 'unexpected positive verdict')
        return None
    oracle = row.get('oracle')
    need(isinstance(oracle, dict), 'missing predeclared oracle')
    pid = oracle['property_id']
    p = by.get(pid)
    need(p and h['checks']['failure'] == [pid] and p['status'] == 'FAILURE' and p['class'] == oracle['class'], 'negative sole failure ID/class/status')
    need(source_path(p['file']) == oracle['file'] and str(p['line']) == str(oracle['line']), 'negative source coordinates')
    if oracle.get('description'):
        need(p['description'] == oracle['description'], 'negative description')
    if row['variant'] in request.get('variants', {}):
        variant = request['variants'][row['variant']]
        data = git_bytes(CONTROL, CONTROL_SHA, 'ch8-s1-control/' + variant['patch'])
        need(digest(data) == variant['sha256'], 'variant patch SHA')
        marker = oracle.get('intended_message') or row.get('failure_description') or variant.get('marker')
        need(marker and marker in data.decode(), 'predeclared variant marker')
        source_evidence = {'patch': variant['patch'], 'sha256': digest(data), 'marker': marker}
    else:
        data = git_bytes(STD, SOURCE_SHA, oracle['file'])
        lines = data.decode().splitlines()
        start = int(oracle['line']) - 1
        need(digest(data) == oracle['source_sha256'] and lines[start:start+len(oracle['assertion_context'])] == oracle['assertion_context'], 'oracle source binding')
        source_evidence = {'file': oracle['file'], 'sha256': digest(data), 'line': oracle['line'], 'context': oracle['assertion_context']}
    return {'binding': 'EXACT_PREDECLARED_SOLE_FAILURE', 'property': p, 'source': source_evidence}


def verify_inputs():
    inputs = read(HERE / 'INPUTS.json')
    for rel, expected in inputs['files'].items():
        need(digest((RUN / rel).read_bytes()) == expected, 'input SHA:' + rel)
    packet = read(RUN / 'W11-INPUTS.json')
    for rel, expected in packet['inputs'].items():
        need(digest((RUN / rel).read_bytes()) == expected, 'intake input SHA:' + rel)
    return inputs


def analyze():
    inputs = verify_inputs()
    request = read(RUN / 'CI-REQUEST.json')
    need(digest((RUN / 'CI-REQUEST.json').read_bytes()) == REQUEST_SHA, 'request SHA')
    need(git_bytes(CONTROL, CONTROL_SHA, 'ch8-s1-control/CI-REQUEST.json') == (RUN / 'CI-REQUEST.json').read_bytes(), 'executed control request')
    need(read(RUN / 'run-identity.json')['head_sha'] == CONTROL_SHA, 'control identity')
    need(request['std_sha'] == SOURCE_SHA and request['tool_sha'] == TOOL_SHA, 'request pins')
    need(tree(STD, SOURCE_SHA) == request['std_tree'] and tree(CONTROL, TOOL_SHA) == request['tool_tree'], 'source/tool trees')
    for path, expected in request['changed_file_sha256'].items():
        need(digest(git_bytes(STD, SOURCE_SHA, path)) == expected, 'pinned source SHA:' + path)
    stock_role = read(BASELINE.parent / 'STOCK-ROLE.json')
    for excerpt in stock_role['excerpts']:
        data = git_bytes(CONTROL, TOOL_SHA, excerpt['path'])
        need(excerpt['commit'] == TOOL_SHA and digest(data) == excerpt['file_sha256'], 'stock role producer SHA')
        need(data.decode().splitlines()[excerpt['start_line']-1:excerpt['end_line']] == excerpt['lines'], 'stock role producer excerpt')
    # The request carries frozen CI-payload hashes (some refer to earlier payload
    # revisions). Executed producer source is separately bound by CONTROL_SHA.
    policy = read(BASELINE / 'LOCATION-POLICY.json')
    need(policy['decision'] == 'COORDINATOR_VARIANT_2_LOCATION_ONLY', 'policy identity')
    need(len(policy['records']) == 18 and len({x['id'] for x in policy['records']}) == 2, 'exception scope')
    provenance = {p['artifact']: p for p in read(RUN / 'PROVENANCE.json')}
    artifacts = {a['name']: a for a in read(RUN / 'artifacts-metadata.json')['artifacts']}
    need(len(artifacts) == len(provenance) == 14 and len(request['rows']) == 35, 'batch dimensions')
    rows_by = {r['id']: r for r in request['rows']}
    group_for = {rid: g['id'] for g in request['execution_groups'] for rid in g['row_ids']}
    need(set(group_for) == set(rows_by), 'group membership')
    groups, rows, exceptions, unsupported = [], [], [], []
    all_properties = 0
    for spec in sorted(request['execution_groups'], key=lambda g: g['id']):
        gid = spec['id']
        directory = RUN / 'evidence' / gid
        rec, exp, rich, comp = [read(directory / x) for x in ('receipt.json', 'export.json', 'properties.json', 'compile/receipt.json')]
        artifact_name = 'ch8-s1-05-43923266772-1-' + gid
        prov, artifact = provenance[artifact_name], artifacts[artifact_name]
        integ = read(RUN / 'artifacts' / artifact_name / 'zip-integrity.json')
        need(integ['github_digest_match'] is True and 'sha256:' + integ['sha256'] == artifact['digest'] == prov['github_zip_digest'], 'historical ZIP identity')
        need(digest((RUN / 'artifacts' / artifact_name / 'group-evidence.json.gz').read_bytes()) == prov['payload_sha256'], 'compact payload digest')
        for rel, expected in prov['projections'].items():
            need(digest((RUN / rel).read_bytes()) == expected, 'projection digest:' + rel)
        for filename, field in (('export.json', 'export_sha256'), ('properties.json', 'rich_evidence_sha256')):
            actual = digest((directory / filename).read_bytes())
            need(actual == prov['entries']['groups/' + gid + '/' + filename]['sha256'], 'original compact member digest')
            if field in rec:
                need(actual == rec[field], 'receipt export/rich digest')
        need(rec['group'] == gid and rec['request_sha256'] == comp['request_sha256'] == REQUEST_SHA, 'receipt request/group')
        need(rec['std_sha'] == comp['std_sha'] == SOURCE_SHA and rec['tool_sha'] == comp['tool_sha'] == TOOL_SHA, 'compile identity')
        need(comp['state'] == 'COMPLETE' and comp['boundary'] == 'STOCK_INITIAL_EXPORT_OBSERVED', 'compile boundary')
        need(rec['source_before'] == rec['source_after'], 'source snapshot drift')
        before = rec['source_before']
        need(before == {k: request[k] for k in ('std_sha', 'std_tree', 'tool_sha', 'tool_tree', 'changed_file_sha256')}, 'source snapshot pins')
        variant = spec['variant']
        need(rec['variant'] == variant and rec['unwind'] == spec['unwind'], 'variant/unwind')
        expected_files = dict(request['changed_file_sha256'])
        patch_sha = None
        if variant != 'production':
            v = request['variants'][variant]
            patch_sha = digest(git_bytes(CONTROL, CONTROL_SHA, 'ch8-s1-control/' + v['patch']))
            need(patch_sha == v['sha256'], 'variant SHA')
            expected_files.update(v['changed_file_sha256'])
        need(rec['source_under_test'] == {'base_std_sha': SOURCE_SHA, 'file_sha256': expected_files, 'patch_sha256': patch_sha, 'variant': variant}, 'source-under-test variant')
        execution = rec['execution']
        need(snapshot_gate(rec) == 'MATCH', 'required same-run binary snapshots/shutdown')
        need(not rec.get('original_exception') and not rec.get('execution_exception'), 'original execution exception')
        need(rec['effective_cfg'] == ' '.join('--cfg=' + x for x in request['flags']['cfg']), 'effective cfg')
        need(all(execution.get(k) is False for k in ('timed_out', 'stdout_truncated', 'stderr_truncated', 'output_truncated')) and execution.get('signal') is None and rec['phase_limited'] is False, 'interrupted/truncated run')
        need(execution['original_exit_code'] == (1 if any(rows_by[r]['expected'] == 'DETECTED' for r in spec['row_ids']) else 0), 'child exit disagrees with row verdicts')
        selected = [rows_by[rid]['selector'] for rid in spec['row_ids']]
        need(rec['selectors'] == selected and comp['selectors'] == selected, 'receipt selectors')
        argv = [EXPORT_PREFIX.replace('/export/', '/tool/') + 'scripts/kani', 'verify-std']
        for feature in request['flags']['unstable']:
            if feature != 'export-json':
                argv += ['-Z', feature]
        argv += ['--no-assert-contracts', '--jobs=1', '--harness-timeout', '600s']
        for selector in selected:
            argv += ['--harness', selector]
        argv += ['--exact', '--default-unwind', str(spec['unwind']), '-Z', 'export-json', '--export-json', '/home/runner/work/_temp/ch8-s1-receipts/groups/' + gid + '/export.json', '--output-format=regular', EXPORT_PREFIX + 'library', '--cbmc-args', '--object-bits', '12']
        need(rec['argv'] == argv, 'exact invocation flags')
        meta = read(directory / 'binding-metadata.json')
        need(meta['group_id'] == gid and meta['request_sha256'] == REQUEST_SHA
             and meta['invocation_id'] == rec['invocation_id'], 'native invocation namespace')
        need(meta['source_before'] == meta['source_after'] == rec['source_before']
             and meta['source_under_test'] == rec['source_under_test']
             and meta['variant'] == variant and meta['unwind'] == spec['unwind'], 'native source/variant context')
        need(meta['execution'] == execution and meta['argv'] == argv
             and meta['effective_cfg'] == rec['effective_cfg']
             and meta['binaries_before'] == rec['tool_fingerprints_before']
             and meta['binaries_after'] == rec['tool_fingerprints_after'], 'native execution/config/binary context')
        need(meta['configuration_sha256'] == digest(json.dumps({'flags': request['flags'], 'cfg': rec['effective_cfg'], 'argv': argv}, sort_keys=True).encode()), 'native configuration digest')
        need(meta['compilation_id'] is None and not meta['errors'] and not meta['original_exception']
             and not meta['execution_exception'], 'native retained limits/errors')
        need({r['row_id'] for r in meta['rows']} == set(spec['row_ids']), 'native row matrix')
        for artifact_ref in meta['artifacts']:
            need({k: artifact_ref[k] for k in ('bytes', 'sha256')} == prov['entries']['groups/' + gid + '/' + artifact_ref['path']], 'native artifact manifest reference')
        need(exp['harness_selection'] == {'requested_filters': selected, 'exact': True, 'unmatched_filters': [], 'matched_count': len(selected)}, 'exact selector export')
        need(exp['kani_commit'] == TOOL_SHA and exp['kani_commit_dirty'] is False and exp['target'] == 'x86_64-unknown-linux-gnu', 'export producer/target')
        need(exp['run_state'] == 'COMPLETE' and exp['outcome'] == {'kind': 'COMPLETED'} and exp['harness_timeout_s'] == 600, 'export complete')
        need(set(exp['enabled_unstable_features']) == set(request['flags']['unstable']), 'unstable features')
        checks = exp['configuration']['checks']
        need(checks == {'memory_safety': True, 'overflow': True, 'unwinding': True, 'undefined_function': True, 'assertion_reach_checks': True, 'ignore_global_asm': False, 'extra_pointer_checks': False, 'assert_contracts': False, 'prove_safety_only': False}, 'enabled checks')
        need(exp['configuration']['cbmc_args'] == ['--object-bits', '12'] and exp['configuration']['coverage_enabled'] is False, 'CBMC configuration')
        stock = {h['name']: h for h in exp['harnesses']}
        rich_by = {h['name']: h for h in rich['harnesses']}
        need(len(stock) == len(exp['harnesses']) == len(rich_by) == len(rich['harnesses']) and set(stock) == set(rich_by) == set(selected), 'complete harness inventory')
        need(rich['error'] is None, 'rich streaming error')
        state = binary_state(rec.get('tool_fingerprints_before'), rec.get('tool_fingerprints_after'))
        group_exceptions = []
        for rid in spec['row_ids']:
            row = rows_by[rid]
            h, hp = stock[row['selector']], rich_by[row['selector']]['properties']
            by = inventory(h, hp)
            all_properties += len(hp)
            need(h['crate_name'] == 'core' and h['resolved_unwind'] == row['unwind'] == spec['unwind'] and h['attributes']['unwind_value'] in (None, row['unwind']), 'harness config')
            need(h['warnings_truncated'] == 0 and not h['warnings'] and not h['attributes']['stubs'] and not h['attributes']['verified_stubs'], 'warnings/stubs')
            need(h['is_automatically_generated'] is False and h['has_loop_contracts'] is False and h['attributes']['should_panic'] is False, 'harness execution mode')
            sb = request['source_bindings'][rid]
            data = git_bytes(STD, SOURCE_SHA, sb['file'])
            need(digest(data) == sb['sha256'], 'source binding SHA')
            lines = data.decode().splitlines()
            for loc in sb['locations']:
                need(lines[loc['line'] - 1] == loc['source'], 'source binding anchor')
            for p in hp:
                located = isinstance(p.get('file'), str) and p['file'].startswith(EXPORT_PREFIX) and str(p.get('line', '')).isdigit() and int(p['line']) > 0
                if not located:
                    entry = dict(p, group=gid, selector=row['selector'], row_id=rid)
                    need(location_exception(entry, policy), 'unapproved missing location:' + p['id'])
                    entry.update(decision='ALLOWED_LOCATION_ONLY', file_line_repaired=False, check_retained=True, stock_role='MIR_UNREACHABLE_ASSERT_FALSE_THEN_ASSUME_FALSE', precise_mir_binding='UNKNOWN_NOT_REQUIRED_BY_THIS_LOCATION_EXCEPTION')
                    exceptions.append(entry)
                    group_exceptions.append(entry['id'])
            for p in h['unsupported_constructs']:
                need(p['status'] == 'SUCCESS' and p['id'] in by and p['id'] not in h['checks']['unreachable'], 'unsupported guard not successful')
                unsupported.append(dict(p, row_id=rid, group=gid, selector=row['selector'], decision='ALLOWED_EXACT_SUCCESSFUL_UNSUPPORTED_GUARD', semantics='assert(false); assume(false)', source='kani-compiler/src/codegen_cprover_gotoc/codegen/assert.rs:278-322'))
            oracle = negative_oracle(row, h, by, request)
            rows.append({'id': rid, 'group': gid, 'selector': row['selector'], 'expected': row['expected'], 'mode': row['mode'], 'variant': variant, 'domain_N': row.get('N'), 'source_reported_verdict': h['outcome']['verdict'], 'properties': len(hp), 'inventory': 'EXACT_STOCK_RICH_RECONCILED', 'locations': 'COMPLETE_OR_EXACT_APPROVED_EXCEPTION', 'negative_oracle': oracle, 'binary_after': state, 'pending_gates': ['BINARY_AFTER_RUN_FINGERPRINT'] if state != 'MATCH' else [], 'proof_credit': 'NONE'})
            rows[-1]['successful_mir_unreachable_guard_checks'] = sum(p['class'] == 'unreachable' and p['status'] == 'SUCCESS' for p in hp)
        groups.append({'id': gid, 'rows': spec['row_ids'], 'intake_receipt_state': rec['state'], 'new_inventory_gate': 'RECONCILED_WITH_EXACT_LOCATION_EXCEPTION', 'exception_records': len(group_exceptions), 'binary_after': state, 'execution_exit': execution['original_exit_code'], 'compile': 'COMPLETE_STOCK_INITIAL_EXPORT', 'source_snapshots': 'MATCH_REQUEST', 'artifact_digest_assurance': 'REPLAYED_COMPACT_PAYLOAD_AND_PROJECTION_HASHES; ZIP_MATCH_IS_HISTORICAL_RECEIPT_ONLY'})
    need(len(exceptions) == 18 and {exception_key(x) for x in exceptions} == {exception_key(x) for x in policy['records']}, 'exception record set')
    need(all_properties == 9986, 'retained property count')
    return request, inputs, groups, rows, exceptions, unsupported


def build_report():
    request, inputs, groups, rows, exceptions, unsupported = analyze()
    import semantic
    import unreachable
    import pfc
    seed = read(BASELINE.parent / 'accept/ACCEPT.json')
    requested = {r['id']: r for r in request['rows']}
    need(set(requested) == {r['id'] for r in seed['rows']}, 'semantic navigation row set')
    for r in seed['rows']:
        spec = requested[r['id']]
        need(r['selector'] == spec['selector'], 'semantic navigation selector')
        need([s['message'] for s in r['required_success']] == spec['required_success_messages'], 'required success navigation')
        need([c['message'] for c in r['required_covers']] == spec['required_cover_messages'], 'required cover navigation')
    semantic_report = semantic.analyze(RUN, request, STD, seed)
    unreachable_report = unreachable.analyze(RUN, request, STD)
    pfc.PINNED_CONTROL_COMMIT = CONTROL_SHA
    pfc_report = pfc.analyze(RUN, request, STD, CONTROL)
    sys.path.insert(0, str(HERE))
    import native
    native_report = native.analyze(RUN, request, pfc_report, semantic_report, unreachable_report, CONTROL)
    need(native_report['integrity']['all_valid'] and native_report['integrity']['metadata_entries'] == 322, 'native metadata integrity')
    need(len(native_report['harnesses']) == 35 and all(
        r['status'] == 'EXACT_HARNESS_RECORD' and len(r['records']) == 1 and not r['invalid_refs']
        for r in native_report['harnesses']), 'native exact harness matrix')
    for harness in native_report['harnesses']:
        record = harness['records'][0]
        exp = read(RUN / 'evidence' / harness['group'] / 'export.json')
        exported = next(h for h in exp['harnesses'] if h['name'] == record['harness'])
        source = record['source']
        expected_file = exported['file'] if exported['file'].startswith(EXPORT_PREFIX) else EXPORT_PREFIX + exported['file']
        need(record['crate'] == exported['crate_name'] == 'core'
             and source['file'] == expected_file and source['start_line'] == exported['line']
             and source['end_line'] >= source['start_line'], 'native source span/export mismatch')
    need(len(native_report['pfc']) == 22, 'native PFC count')
    for binding in pfc_report['bindings']:
        native_binding = binding['native_metadata']
        need(native_binding['status'] == 'EXACT_HARNESS_RECORD' and len(native_binding['records']) == 1
             and not native_binding['invalid_refs'], 'native exact PFC ref')
        record = native_binding['records'][0]
        need(record['pfc_target_matches_report'] and record['manual_target_definition_link'], 'native manual target definition link')
        need(record['contracted_function_name'] == binding['target']['contracted_function_name'], 'native wrapper symbol export mismatch')
        need(record['attributes'] == binding['export']['attributes'], 'native harness attributes mismatch')
    # Integration below intentionally fails until all three analyses are present.
    return integrate(request, inputs, groups, rows, exceptions, unsupported,
                     semantic_report, unreachable_report, pfc_report, native_report)


def integrate(request, inputs, groups, rows, exceptions, unsupported, semantic_report, unreachable_report, pfc_report, native_report):
    row_by = {r['id']: r for r in rows}
    requested = {r['id']: r for r in request['rows']}
    pfc_by = {r['id']: r for r in pfc_report['bindings']}
    need(set(semantic_report['rows']) == set(row_by), 'semantic row set')
    need(set(pfc_by) == {r['id'] for r in rows if r['mode'] == 'PFC'}, 'PFC row set')
    need(not unreachable_report['unknown'] and not unreachable_report['structured_read_errors'], 'unreachable analysis input gap')
    ur = unreachable_report['records']
    need(len(ur) == 415 and sum(r['status_kind'] == 'check' for r in ur) == 413 and sum(r['status_kind'] == 'cover' for r in ur) == 2, 'unreachable inventory counts')
    need(len({(r['row_id'], r['property_id']) for r in ur}) == 415, 'unreachable row/property collision')
    for record in ur:
        row = row_by[record['row_id']]
        need((row['group'], row['selector']) == (record['group'], record['selector']), 'unreachable wrong row/group/selector')
        if row['id'] in pfc_by:
            record['target']['source_attribute_target'] = pfc_by[row['id']]['target']['qualified']
            record['target']['source_attribute_binding'] = pfc_by[row['id']]['static_source_binding_status']
            record['wrapper']['same_compilation_binding'] = pfc_by[row['id']]['same_compilation_binding_status']
        # A compiler check at a runtime safety site is not a required relation
        # assertion by virtue of its function's name. Unknown applicability is
        # retained unless the explicit source/domain rule justifies allowance.
        if record['status_kind'] == 'cover':
            companion_id = requested[row['id']].get('companion')
            companion = row_by.get(companion_id)
            needed = requested[row['id']].get('required_cover_messages', [])
            allowed = bool(row['expected'] == 'DETECTED' and row['negative_oracle']
                           and record['description'] not in needed and companion
                           and companion['source_reported_verdict'] == 'SUCCESS')
            need(allowed and row['id'] in {'activation-default', 'activation-override'}, 'unreachable cover not authorized negative return cover')
            need(record['site']['source_path'] == 'library/core/src/slice/sort/shared/smallsort/verify/sorting_entry_controls.rs'
                 and str(record['site']['line']) == ('20' if row['id'] == 'activation-default' else '33'), 'negative cover source site')
            record['decision'] = 'ALLOWED_EXPECTED_NEGATIVE_POST_FAILURE_RETURN_COVER'
            record['reason'] = 'Exact predeclared sole failure cuts off this return cover; same-run production companion reports SUCCESS. No positive reachability credit.'
            record['companion'] = {'id': companion_id, 'group': companion['group'], 'source_verdict': 'SUCCESS', 'run': 43923266772, 'binary_after': companion['binary_after']}
    need(sum(len(x['success']) for x in semantic_report['rows'].values()) == 127, 'required success count')
    need(sum(len(x['covers']) for x in semantic_report['rows'].values()) == 113, 'required cover count')
    for row in rows:
        rid = row['id']
        sem = semantic_report['rows'][rid]
        row['required_success'] = sem['success']
        row['required_covers'] = sem['covers']
        if any(x['binding'] not in {'EXACT_SUCCESS_SEMANTIC', 'EXACT_SUCCESS_SEMANTIC_SET'} for x in sem['success']):
            row['pending_gates'].append('REQUIRED_SUCCESS_SEMANTIC_BINDING')
        if any(x['binding'] != 'EXACT_SAT_COVER_SEMANTIC' for x in sem['covers']):
            row['pending_gates'].append('REQUIRED_COVER_SEMANTIC_BINDING')
        unreach = [r for r in ur if r['row_id'] == rid]
        row['unreachable_properties'] = [r['property_id'] for r in unreach]
        row['unreachable_decisions'] = dict(collections.Counter(r['decision'] for r in unreach))
        if any(r['decision'].startswith('BLOCK') for r in unreach):
            row['pending_gates'].append('MANDATORY_OBLIGATION_OR_SECTION_UNREACHABLE')
        if any(not r['decision'].startswith(('ALLOWED_', 'BLOCK')) for r in unreach):
            row['pending_gates'].append('UNREACHABLE_APPLICABILITY_OR_ORIGIN_UNKNOWN')
        if rid in pfc_by:
            binding = pfc_by[rid]
            need(binding['selector'] == row['selector'] and binding['execution_group'] == row['group'], 'PFC row/group/selector')
            need(binding['sites']['property_count'] == row['properties'], 'PFC same-group property count')
            need(binding['target']['source_attribute_matches_export'] is True, 'PFC pinned source target')
            if binding['same_compilation_binding_status'] != 'BOUND':
                row['pending_gates'].append('FULL_QUALIFIED_TARGET_IMPL_CONTRACT_WRAPPER_BINDING')
            row['pfc_binding'] = {'static_source': binding['static_source_binding_status'], 'same_compilation': binding['same_compilation_binding_status']}
        companion_id = requested[rid].get('companion')
        if companion_id:
            companion = row_by[companion_id]
            need(companion['source_reported_verdict'] == 'SUCCESS', 'required companion did not succeed')
            row['same_run_companion'] = {'id': companion_id, 'group': companion['group'], 'source_verdict': companion['source_reported_verdict'], 'run': 43923266772, 'source_tool_request_pins': 'MATCH', 'binary_after': companion['binary_after']}
            if companion['binary_after'] != 'MATCH':
                row['pending_gates'].append('COMPANION_BINARY_AFTER_RUN_FINGERPRINT')
    # Dependencies are evaluated after every row has its local gates.
    local_pending = {r['id']: list(r['pending_gates']) for r in rows}
    for row in rows:
        companion_id = requested[row['id']].get('companion')
        if companion_id and local_pending[companion_id]:
            row['pending_gates'].append('COMPANION_QUALIFICATION_PENDING')
        row['pending_gates'] = sorted(set(row['pending_gates']))
        row['qualification'] = 'PENDING' if row['pending_gates'] else 'QUALIFIED'
        row['independent_proof_credit'] = 'NONE'
        row['remaining_gate_details'] = {}
        if 'REQUIRED_SUCCESS_SEMANTIC_BINDING' in row['pending_gates']:
            row['remaining_gate_details']['REQUIRED_SUCCESS_SEMANTIC_BINDING'] = [
                {'message': s['message'], 'candidate_property_ids': s['candidate_property_ids'],
                 'reason': 'Several distinct assertions have the same callsite/placeholder; no per-assertion origin is exported.'}
                for s in row['required_success'] if s['binding'] not in {'EXACT_SUCCESS_SEMANTIC', 'EXACT_SUCCESS_SEMANTIC_SET'}]
        if 'UNREACHABLE_APPLICABILITY_OR_ORIGIN_UNKNOWN' in row['pending_gates']:
            row['remaining_gate_details']['UNREACHABLE_APPLICABILITY_OR_ORIGIN_UNKNOWN'] = [
                {'property_id': u['property_id'], 'decision': u['decision'], 'role': u['role'],
                 'file': u['site']['source_path'], 'line': u['site']['line'], 'reason': u['decision_basis']}
                for u in ur if u['row_id'] == row['id'] and u['decision'].startswith('UNKNOWN')]
        if row['id'] in pfc_by:
            binding = pfc_by[row['id']]
            row['remaining_gate_details']['FULL_QUALIFIED_TARGET_IMPL_CONTRACT_WRAPPER_BINDING'] = binding['native_metadata']['edges_open']
        if companion_id and local_pending[companion_id]:
            row['remaining_gate_details']['COMPANION_QUALIFICATION_PENDING'] = {'companion': companion_id, 'local_pending_gates': local_pending[companion_id]}
    unions = []
    for union in request['replacement_unions']:
        members = [row_by[r] for r in union['member_row_ids']]
        need(len(members) == 4 and {requested[r['id']]['N'] for r in members} == {0, 1, 2, 3}, 'N0..3 union dimensions')
        messages = {c['message'] for m in members for c in m['required_covers'] if c['binding'] == 'EXACT_SAT_COVER_SEMANTIC'}
        covered = set(union['required_cover_messages']) <= messages
        unions.append({'id': union['id'], 'members': union['member_row_ids'], 'N': [0, 1, 2, 3], 'same_run_source_tool_request_checks': 'MATCH', 'required_cover_union': 'BOUND' if covered else 'PENDING', 'member_qualification': {m['id']: m['qualification'] for m in members}, 'qualification': 'PENDING' if not covered or any(m['pending_gates'] for m in members) else 'QUALIFIED_BOUNDED_UNION', 'domain_limit': 'Only the fixed initialized fixture for N0..3; no completeness claim for all smallsort inputs/scratch geometries.', 'proof_credit': 'NONE'})
    decisions = collections.Counter(r['decision'] for r in ur)
    unreachable_report['summary']['decisions'] = dict(sorted(decisions.items()))
    unreachable_report['summary']['unresolved_applicability_records'] = sum(not r['decision'].startswith(('ALLOWED_', 'BLOCK')) for r in ur)
    totals = {'groups': 14, 'rows': 35, 'properties_reconciled': 9986, 'source_success': 27, 'predeclared_exact_sole_failure_negatives': sum(bool(r['negative_oracle']) for r in rows), 'inventory_reconciled_groups': 14, 'location_only_exceptions': len(exceptions), 'exception_distinct_IDs': 2, 'missing_binary_after_groups': sum(g['binary_after'] != 'MATCH' for g in groups), 'unreachable_checks_analyzed': 413, 'unreachable_covers_analyzed': 2, 'unreachable_decisions': dict(sorted(decisions.items())), 'required_success_bindings': semantic_report['summary'], 'pfc_source_bound': sum(b['static_source_binding_status'] == 'SOURCE_BOUND' for b in pfc_by.values()), 'pfc_same_compilation_pending': sum(b['same_compilation_binding_status'] != 'BOUND' for b in pfc_by.values()), 'unsupported_success_guards_exactly_linked': len(unsupported), 'rows_qualified': sum(not r['pending_gates'] for r in rows), 'replacement_unions': len(unions), 'proof_credit': 'NONE'}
    producer_paths = ['ch8-s1-control/runner.py', 'ch8-s1-control/rich_evidence.py']
    producers = [{'revision': CONTROL_SHA, 'path': p, 'sha256': digest(git_bytes(CONTROL, CONTROL_SHA, p))} for p in producer_paths]
    p = 'kani-compiler/src/codegen_cprover_gotoc/codegen/assert.rs'
    data = git_bytes(CONTROL, TOOL_SHA, p)
    need('PropertyClass::UnsupportedConstruct' in data.decode() and 'Expr::bool_false()' in data.decode(), 'unsupported producer source')
    producers.append({'revision': TOOL_SHA, 'path': p, 'sha256': digest(data), 'semantics': 'codegen_unimplemented_stmt/codegen_mimic_unimplemented call codegen_assert_assume(false, UnsupportedConstruct); prove_safety_only=false preserved.'})
    for p in ['kani-compiler/src/kani_middle/metadata.rs', 'kani_metadata/src/lib.rs',
              'kani_metadata/src/harness.rs', 'library/kani_core/src/lib.rs',
              'kani-compiler/src/codegen_cprover_gotoc/overrides/hooks.rs']:
        producers.append({'revision': TOOL_SHA, 'path': p, 'sha256': digest(git_bytes(CONTROL, TOOL_SHA, p))})
    totals['successful_mir_unreachable_guard_checks'] = sum(r['successful_mir_unreachable_guard_checks'] for r in rows)
    totals['native_metadata_files_verified'] = native_report['integrity']['metadata_entries']
    totals['native_exact_harness_records'] = len(native_report['harnesses'])
    totals['native_manual_target_definition_links'] = sum(
        p['records'][0]['manual_target_definition_link'] for p in native_report['pfc'])
    totals['pending_gate_rows'] = dict(sorted(collections.Counter(g for r in rows for g in r['pending_gates']).items()))
    pfc_report['cover_source_case_audit_reference'] = 'cover_source_case_audit'
    return {'schema': 'ch8-s1-07-offline-acceptance-v1', 'run': 43923266772, 'entry_g0': ENTRY_SHA, 'source_sha': SOURCE_SHA, 'tool_sha': TOOL_SHA, 'control_sha': CONTROL_SHA, 'request_sha256': REQUEST_SHA, 'input_manifest_sha256': digest((HERE / 'INPUTS.json').read_bytes()), 'location_policy_sha256': digest((BASELINE / 'LOCATION-POLICY.json').read_bytes()), 'qualified_acceptance': 'PENDING' if any(r['pending_gates'] for r in rows) else 'QUALIFIED_BOUNDED_SOURCE_OBSERVATIONS_ONLY', 'independent_proof_credit': 'NONE', 'totals': totals, 'groups': groups, 'rows': rows, 'location_exceptions': exceptions, 'native_analysis': native_report, 'unreachable_analysis': unreachable_report, 'pfc_analysis': pfc_report, 'semantic_binding_gaps': semantic_report['gaps'], 'cover_source_case_audit': semantic_report['source_case_audit'], 'unsupported_records': unsupported, 'replacement_unions': unions, 'producer_source': producers, 'policy': {'location_exception': 'APPLIED_EXACT_18_RECORDS_2_IDS_LOCATION_ONLY', 'success_binding': 'SEMANTIC_ROOT_MACRO_INSTANCE_CALLSITE_CONTEXT_TO_EXACT_PROPERTY; NO_ORDINAL_INFERENCE', 'all_other_gates': 'FAIL_CLOSED', 'historical_receipts_changed': False, 'binary_after_requirement': 'RETAINED_SAME_RUN_FIXED_REQUIRED_BINARIES', 'class_unreachable_success_vs_status_unreachable': 'DISTINCT', 'credit': 'SOURCE_REPORTED_BOUNDED_OBSERVATIONS; NO_INDEPENDENT_B1_B2_OR_GENERAL_PROOF'}, 'execution': {'offline_only': True, 'local_cargo_rustc_kani_cbmc': 'NOT_RUN', 'raw_logs_read': False, 'push_ci_publication_ledger_changes': False}, 'limits': ['Historical ZIP match is retained source-reported integrity evidence; this replay rehashes compact payloads and saved projections, without reading raw logs or original ZIPs.', 'Exact source/property coordinates and candidate wrapper symbols do not establish a missing compiler-origin link.', 'Every unknown role, wrapper binding, ambiguous placeholder and unqualified companion remains a separate gate; no policy proposal is applied.', 'SAT means an execution exists in this bounded fixture; it does not establish domain completeness or a general sorting theorem.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    report = build_report()
    text = json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + '\n'
    if args.write:
        (HERE / 'ACCEPT.json').write_text(text)
    else:
        need((HERE / 'ACCEPT.json').read_text() == text, 'receipt replay differs')
    print(json.dumps(report['totals'], sort_keys=True))


if __name__ == '__main__':
    main()
