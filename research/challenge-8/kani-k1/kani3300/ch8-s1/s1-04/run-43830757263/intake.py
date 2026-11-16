#!/usr/bin/env python3
"""Offline S1-04 intake: structured JSON only; never launches a verifier."""
import argparse
import copy
import difflib
import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
CONTROL = '205b0e98c771a7e6c6b8ec28414494868bcca4e0'
RUN = 43830757263


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    path = HERE / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def scrub(value):
    if isinstance(value, dict):
        return {k: scrub(v) for k, v in value.items() if k not in ('stdout', 'stderr')}
    if isinstance(value, list):
        return [scrub(v) for v in value]
    return value


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--scratch', type=Path, required=True)
    ap.add_argument('--control', type=Path, required=True)
    ap.add_argument('--std', type=Path, required=True)
    args = ap.parse_args()
    control = args.control.resolve()
    assert subprocess.check_output(['git', '-C', str(control), 'rev-parse', 'HEAD'], text=True).strip() == CONTROL
    assert not subprocess.check_output(['git', '-C', str(control), 'status', '--porcelain'], text=True)
    payload = control / 'ch8-s1-control'
    sys.path.insert(0, str(payload))
    r = importlib.import_module('runner')
    req = r.load_request()
    assert subprocess.check_output(['git', '-C', str(args.std), 'rev-parse', 'HEAD'], text=True).strip() == req['std_sha']
    for rel, digest in req['ci_payload_sha256'].items():
        assert sha(control / rel) == digest, rel
    request_hash = sha(payload / 'CI-REQUEST.json')
    meta = read(args.scratch / 'artifacts-metadata.json')
    run = read(args.scratch / 'run-metadata.json')
    assert run['databaseId'] == RUN and run['headSha'] == CONTROL
    assert run['status'] == 'completed' and len(run['jobs']) == 14
    assert len(meta['artifacts']) == meta['total_count'] == 14
    roots = sorted(p for p in (args.scratch / 'artifacts').iterdir() if (p / 'receipt.json').is_file())
    assert len(roots) == 14 and {p.name for p in roots} == {a['name'] for a in meta['artifacts']}
    command = [sys.executable, str(payload / 'collect.py')]
    for root in roots:
        command += ['--root', str(root)]
    command += ['--out', str(HERE / 'collected.json')]
    subprocess.run(command, check=True)
    collected = read(HERE / 'collected.json')
    assert collected['missing_groups'] == [] and len(collected['rows']) == 35
    observed = {row['id']: row for row in collected['rows']}
    expected_source = {k: req[k] for k in ('std_sha', 'std_tree', 'tool_sha', 'tool_tree', 'changed_file_sha256')}
    groups, rows, inventory, excerpts = [], [], [], []
    raw_by_id = {}
    for root in roots:
        terminal = read(root / 'receipt.json')
        assert terminal['stop_reason'] is None
        gid, = terminal['selected_groups']
        job, = [j for j in run['jobs'] if j['name'].endswith('(' + gid + ')')]
        assert job['conclusion'] == 'failure'
        for step in job['steps']:
            if step['name'] in ('Validate control and synthetic wrapper', 'Build exact stock tool once'):
                assert step['conclusion'] == 'success'
        dest = root / 'groups' / gid
        group, compile_receipt, export = (read(dest / name) for name in ('receipt.json', 'compile/receipt.json', 'export.json'))
        assert group['state'] == 'COMPLETE' and group['source_before'] == group['source_after'] == expected_source
        assert group['request_sha256'] == request_hash
        assert compile_receipt['state'] == 'COMPLETE' and compile_receipt['boundary'] == 'STOCK_INITIAL_EXPORT_OBSERVED'
        assert sha(dest / 'export.json') == group['export_sha256']
        assert export['run_state'] == 'COMPLETE' and export['kani_commit'] == req['tool_sha'] and export['kani_commit_dirty'] is False
        assert set(group['selectors']) == {h['name'] for h in export['harnesses']}
        assert len(group['selectors']) == len(export['harnesses'])
        before, after = (group['tool_fingerprints_' + side] for side in ('before', 'after'))
        assert before['required_hashes_present'] and after['required_hashes_present']
        assert {k: v['sha256'] for k, v in before['binaries'].items()} == {k: v['sha256'] for k, v in after['binaries'].items()}
        execution = group['execution']
        assert not execution['timed_out'] and execution['signal'] is None and 'termination_reason' not in execution
        all_success = all(h['outcome'] == {'kind': 'COMPLETED', 'verdict': 'SUCCESS'} for h in export['harnesses'])
        assert execution['original_exit_code'] == (0 if all_success else 1)
        groups.append({'id': gid, 'job_id': job['databaseId'], 'job_conclusion': job['conclusion'],
                       'compile_state': compile_receipt['state'], 'compile_elapsed_upper_bound_seconds': compile_receipt['elapsed_upper_bound_seconds'],
                       'compile_exit_code': None, 'compile_exit_scope': 'NO_SEPARATE_COMPILER_PROCESS_EXIT_IN_BATCH',
                       'group_execution': execution, 'terminal_state': terminal['state'], 'stop_reason': terminal['stop_reason'],
                       'source_snapshots_equal': True, 'row_ids': [], 'proof_credit': 'NONE'})
        for h in export['harnesses']:
            row, = [q for q in req['rows'] if q['selector'] == h['name'] and q['variant'] == group['variant']]
            rid = row['id']
            assert rid not in raw_by_id
            raw_by_id[rid] = (dest / 'export.json', group, h)
            parsed = r.parse_export(dest / 'export.json', row, source_binding=req['source_bindings'][rid],
                                    std=Path('/home/runner/work/kani/kani/export'), group_selectors=group['selectors'])
            assert parsed == observed[rid]['export'], rid
            assert h['outcome']['kind'] == 'COMPLETED'
            assert h['n_properties'] == h['checks']['total'] + h['covers']['total']
            checks = h['checks']
            assert checks['total'] == checks['success'] + sum(len(checks[k]) for k in ('failure', 'unreachable', 'undetermined', 'error', 'unknown', 'other'))
            assert h['n_failed'] == len(checks['failure']) == len(h['failed_properties'])
            assert set(checks['failure']) == {p['id'] for p in h['failed_properties']}
            assert h['covers']['total'] == sum(len(v) for k, v in h['covers'].items() if k != 'total')
            rows.append({'id': rid, 'group': gid, 'selector': h['name'], 'mode': row['mode'], 'variant': row['variant'],
                         'raw_outcome': h['outcome'], 'verification_time_s': h['resources'].get('verification_time_s'),
                         'checks': checks, 'covers': h['covers'], 'failed_properties': h['failed_properties'],
                         'unsupported_constructs': h['unsupported_constructs'], 'export_source': {'file': h['file'], 'line': h['line']},
                         'oracle_state': parsed['state'], 'oracle_outcome': parsed['outcome'],
                         'timed_out': False, 'timeout_seconds': 600, 'timeout_scope': observed[rid]['timeout_scope'],
                         'per_root_rss_kib': None, 'per_root_rss_status': observed[rid]['per_root_rss_status'],
                         'group_rss_peak_kib': execution['rss_peak_kib'], 'proof_credit': 'NONE'})
            groups[-1]['row_ids'].append(rid)
        artifact, = [a for a in meta['artifacts'] if a['name'] == root.name]
        assert not artifact['expired'] and artifact['workflow_run']['head_sha'] == CONTROL
        files = []
        for name in ('receipt.json', 'compile/receipt.json', 'export.json'):
            original = dest / name
            target = 'evidence/' + gid + '/' + name
            if name == 'export.json':
                (HERE / target).parent.mkdir(parents=True, exist_ok=True)
                (HERE / target).write_bytes(original.read_bytes())
            else:
                write(target, scrub(read(original)))
            files.append({'source': str(original), 'original_sha256': sha(original), 'saved': target,
                          'saved_sha256': sha(HERE / target), 'projection': 'EXACT_EXPORT_BYTES' if name == 'export.json' else 'JSON_WITHOUT_STDOUT_STDERR'})
        inventory.append({'artifact': artifact, 'terminal_receipt_sha256': sha(root / 'receipt.json'), 'files': files})
        excerpts.append({'group': gid, 'stdout': group['stdout'], 'stderr': group['stderr'],
                         'scope': 'EXISTING_BOUNDED_RECEIPT_HEAD_TAIL_ONLY; RAW_LOG_FILES_NOT_OPENED'})
    order = {q['id']: i for i, q in enumerate(req['rows'])}
    rows.sort(key=lambda q: order[q['id']])
    assert len(rows) == 35 and sum(q['raw_outcome']['verdict'] == 'SUCCESS' for q in rows) == 27
    assert sum(q['oracle_outcome'] == 'EXPECTED' for q in rows) == 6
    write('GROUPS.json', groups)
    write('ROWS.json', rows)
    write('BOUNDED-EXCERPTS.json', excerpts)
    write('run-metadata.json', run)
    write('PROVENANCE.json', {'run': RUN, 'g0_input': 'dfa49651efee40fc8c95ba88e9d49def3202c75a',
                              'control_sha': CONTROL, 'std_sha': req['std_sha'], 'tool_sha': req['tool_sha'],
                              'request_sha256': request_hash, 'collector_sha256': sha(payload / 'collect.py'),
                              'collection_command': command, 'artifact_count': len(roots), 'inventory': inventory,
                              'archive_digest_assurance': 'GITHUB_METADATA_ONLY; gh run download extracted artifacts; no independent ZIP digest verification',
                              'source_and_binary_identity_assurance': 'RECEIPT_REPORTED; export hash and cross-file identities checked offline; no independent parser-input binding',
                              'raw_logs_opened': False, 'proof_credit': 'NONE'})
    # Minimal candidate: retain invocation anchors and additionally pin the exact
    # macro-generated function declaration; never admit arbitrary source lines.
    fixed = copy.deepcopy(req)
    for rid in ('model_u8_n0_3', 'model_cell_n0_3', 'model_noncopy_n0_3'):
        binding = fixed['source_bindings'][rid]
        source = args.std / binding['file']
        assert sha(source) == binding['sha256']
        declaration = source.read_text().splitlines()[28]
        assert declaration == '        fn $name() {'
        binding['locations'].append({'line': 29, 'source': declaration})
    original_text = (payload / 'CI-REQUEST.json').read_text()
    patched_text = json.dumps(fixed, indent=2) + '\n'
    patch = ''.join(difflib.unified_diff(original_text.splitlines(True), patched_text.splitlines(True),
                                       fromfile='a/ch8-s1-control/CI-REQUEST.json', tofile='b/ch8-s1-control/CI-REQUEST.json'))
    (HERE / 'source-binding-fix.patch').write_text(patch)
    subprocess.run(['git', '-C', str(control), 'apply', '--check', str(HERE / 'source-binding-fix.patch')], check=True)
    # Replay static parsing only. The original receipts/collector are immutable.
    replay = []
    for rid in ('model_u8_n0_3', 'model_cell_n0_3', 'model_noncopy_n0_3'):
        export_path, group, h = raw_by_id[rid]
        row = next(q for q in req['rows'] if q['id'] == rid)
        def parse(binding):
            return r.parse_export(export_path, row, source_binding=binding,
                                  std=Path('/home/runner/work/kani/kani/export'), group_selectors=group['selectors'])
        assert observed[rid]['export']['state'] == 'WRONG_SOURCE_BINDING'
        parsed = parse(fixed['source_bindings'][rid])
        assert parsed['state'] == 'INCOMPLETE_CHECK_INVENTORY' and parsed['outcome'] == 'UNKNOWN'
        for field, value in (('selector', 'wrong'), ('crate', 'wrong'), ('mode', 'PFC'), ('file', 'wrong.rs'), ('locations', [{'line': 30, 'source': 'wrong'}])):
            mutation = copy.deepcopy(fixed['source_bindings'][rid]); mutation[field] = value
            assert parse(mutation)['state'] == 'WRONG_SOURCE_BINDING', (rid, field)
        replay.append({'id': rid, 'before': 'WRONG_SOURCE_BINDING', 'after': parsed['state'], 'outcome': parsed['outcome'], 'negative_mutations_rejected': 5})
    write('VALIDATION.json', {'state': 'PASS', 'groups': 14, 'rows': 35, 'unchanged_parser_replays': 35,
                             'git_apply_check': 'PASS_ON_PINNED_CONTROL',
                             'minimal_binding_patch_replays': replay, 'patch_sha256': sha(HERE / 'source-binding-fix.patch'),
                             'local_verifier_execution': 'NOT_RUN', 'candidate_review': 'NOT_RUN; required before future submission',
                             'original_collected_json_unchanged_by_patch': True, 'proof_credit': 'NONE'})
    print(json.dumps({'state': 'PASS', 'groups': len(groups), 'rows': len(rows), 'raw_success': 27,
                      'raw_failure': 8, 'oracle_expected': 6, 'oracle_unknown': 29, 'proof_credit': 'NONE'}))


if __name__ == '__main__':
    main()
