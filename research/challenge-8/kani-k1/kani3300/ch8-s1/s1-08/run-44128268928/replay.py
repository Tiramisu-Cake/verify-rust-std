#!/usr/bin/env python3
"""Offline exact collector replay and diagnostics. Never executes runner.main or tools."""
import collections
import difflib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
BASE = HERE.parent.parent
OLD = HERE.parent / 'run-44095954742'
S107 = BASE / 's1-07/run-43923266772'
DIAG = OLD / 'cell-diagnostic'
CONTROL = Path('/root/kani-ch8-s1-08-cell-retry-fix-w13')
STD = Path('/root/verify-rust-std-ch8-s1-08-w13')
HEAD = '4336dfed5af21660b9ac82907107be839ce13977'
REVIEWED = 'e27ec119eeac798d43d6bc056a449fa7576a5e94'
PAIR = ['stable_default_cell', 'unstable_default_cell']
RUN = 44128268928
GID = 'cell-u34'
UNKNOWN = 'UNKNOWN_NOT_EXPORTED_BY_PINNED_PRODUCER'


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


# Reuse exact intake13 bounded reader, invariant checks and preview sanitizer.
h = module('intake13_helpers', OLD / 'intake.py')
need, sha, read, clean = h.require, h.sha, h.read, h.without_previews


def write(name, value):
    p = HERE / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + '\n')


def gitraw(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])


def blob(commit, path):
    return gitraw(CONTROL, 'show', commit + ':' + path)


def ref(path, commit=None):
    if commit:
        top = Path(h.git(HERE, 'rev-parse', '--show-toplevel'))
        need(gitraw(HERE, 'show', commit + ':' + str(path.relative_to(top))) == path.read_bytes(),
             'immutable referenced bytes at ' + commit + ': ' + str(path))
    return {'path': str(path.relative_to(HERE)) if path.is_relative_to(HERE) else
            str(Path(__import__('os').path.relpath(path, HERE))),
            'sha256': sha(path.read_bytes()), **({'g0_commit': commit} if commit else {})}


def validate_selection(collected):
    need(len(collected['rows']) == 35, 'full declared collector view')
    selected = [row for row in collected['rows'] if row['id'] in PAIR]
    need([x['id'] for x in selected] == PAIR, 'exact ordered selected pair')
    need(all(x.get('group') == GID and x.get('status') == 'OBSERVED' and
             x.get('outcome') == 'RECORDED' for x in selected), 'atomic complete observed pair')
    need(len(collected['missing_groups']) == 13 and GID not in collected['missing_groups'], '13 unselected reference groups')
    need(all(x.get('status') == 'NOT_RUN' and x['outcome'] == 'UNKNOWN'
             for x in collected['rows'] if x['id'] not in PAIR), 'reference rows remain NOT_RUN UNKNOWN')
    return selected


def validate_origin(terminal, group, request, request_hash):
    need(terminal['selected_groups'] == [GID], 'exact selected group')
    need([x['id'] for x in terminal['rows'] if x.get('status') == 'OBSERVED'] == PAIR, 'terminal exact observed pair')
    need(len(terminal['rows']) == 35 and all(x.get('status') == 'NOT_SELECTED' and x['outcome'] == 'UNKNOWN'
         for x in terminal['rows'] if x['id'] not in PAIR), 'terminal unselected reference rows')
    source = {k: request[k] for k in ('std_sha', 'std_tree', 'tool_sha', 'tool_tree', 'changed_file_sha256')}
    need(group['source_before'] == group['source_after'] == source, 'source snapshots match exact request')
    need(all(terminal[k] == request[k] for k in ('std_sha', 'std_tree', 'tool_sha', 'tool_tree')), 'terminal source/tool')
    need(group['request_sha256'] == terminal['request_sha256'] == request_hash, 'origin request mismatch')
    need(terminal['state'] == group['state'] == 'COMPLETE', 'atomic complete group/terminal')
    need(group['selectors'] == request['execution_scope']['selectors'] and group['variant'] == 'production', 'selectors/variant')
    need(group['source_under_test']['file_sha256'] == request['changed_file_sha256'] and
         group['source_under_test']['patch_sha256'] is None, 'production source under test')
    need(group['group_budget_seconds'] == group['timeout_seconds'] == 3300 and
         group['argv'][group['argv'].index('--harness-timeout') + 1] == '1200s' and
         [x['timeout_seconds'] for x in request['rows'] if x['id'] in PAIR] == [1200, 1200], 'exact timeout profile')


def inventories(stock, rich):
    rows = []
    need(rich['state'] == 'COMPLETE' and rich['error'] is None, 'full rich inventory')
    for harness in stock['harnesses']:
        matches = [x for x in rich['harnesses'] if x['name'] == harness['name']]
        need(len(matches) == 1, 'unique rich root')
        props = matches[0]['properties']
        byid = {p['id']: p for p in props}
        need(len(byid) == len(props) == harness['n_properties'], 'stock/rich inventory count/uniqueness')
        need(harness['outcome'] == {'kind': 'COMPLETED', 'verdict': 'SUCCESS'}, 'source outcome remains exact')
        for bucket, ids in harness['checks'].items():
            if not isinstance(ids, list):
                continue
            for pid in ids:
                need(pid in byid and byid[pid]['class'] != 'cover' and
                     byid[pid]['status'] == bucket.upper(), 'stock/rich check status')
        for bucket, ids in harness['covers'].items():
            if not isinstance(ids, list):
                continue
            for pid in ids:
                need(pid in byid and byid[pid]['class'] == 'cover' and
                     byid[pid]['status'] == ('SATISFIED' if bucket == 'satisfied' else bucket.upper()), 'stock/rich cover status')
        checks = [p for p in props if p['class'] != 'cover']
        covers = [p for p in props if p['class'] == 'cover']
        need(len(checks) == harness['checks']['total'] and len(covers) == harness['covers']['total'], 'complete stock/rich partition totals')
        for bucket, value in harness['checks'].items():
            if bucket != 'total':
                count = sum(p['status'] == bucket.upper() for p in checks)
                need(count == (len(value) if isinstance(value,list) else value), 'complete stock/rich check partition counts')
        rows.append((harness, props))
    need(sorted(h['name'].rsplit('::', 1)[1] for h in stock['harnesses']) == sorted(PAIR), 'stock exact pair')
    return rows


def compatibility(request, group, stock):
    old = read(OLD / 'CI-REQUEST.json')
    delta = {k: {'old': old.get(k), 'retry': request.get(k)} for k in sorted(old.keys() | request.keys())
             if old.get(k) != request.get(k)}
    expected_keys = {'schema', 'rows', 'ci_payload_sha256', 'budgets', 'reservations', 'batch_policy',
                     'ci_changed_paths', 'workflow_stages', 'artifact_policy', 'execution_scope'}
    gates = {'only_reviewed_request_delta_keys': set(delta) == expected_keys}
    old_rows = {x['id']: x for x in old['rows']}
    row_delta = []
    for row in request['rows']:
        prior = old_rows[row['id']]
        diff = {k: {'old': prior.get(k), 'retry': row.get(k)} for k in sorted(row.keys() | prior.keys())
                if row.get(k) != prior.get(k)}
        if diff:
            row_delta.append({'id': row['id'], 'fields': diff})
    gates['semantic_rows_equal_except_selected_600_to_1200'] = row_delta == [
        {'id': rid, 'fields': {'timeout_seconds': {'old': 600, 'retry': 1200}}} for rid in PAIR]
    equal_fields = sorted((old.keys() | request.keys()) - expected_keys)
    gates['all_other_request_fields_equal'] = all(old.get(k) == request.get(k) for k in equal_fields)
    gates['ROLE_MAP_equal'] = (OLD / 'ROLE-MAP.json').read_bytes() == (HERE / 'ROLE-MAP.json').read_bytes()
    changes = []
    allpaths = set(gitraw(CONTROL, 'ls-tree', '-r', '--name-only', HEAD, 'ch8-s1-control', '.github/workflows').decode().splitlines())
    oldpaths = set(gitraw(CONTROL, 'ls-tree', '-r', '--name-only', '7c41333f9bfcfd7eb4e0ede7bd316443090c9025', 'ch8-s1-control', '.github/workflows').decode().splitlines())
    invariants = []
    difftext = []
    for path in sorted(allpaths | oldpaths):
        a = blob('7c41333f9bfcfd7eb4e0ede7bd316443090c9025', path) if path in oldpaths else b''
        b = blob(HEAD, path) if path in allpaths else b''
        record = {'path': path, 'old_sha256': sha(a) if path in oldpaths else None,
                  'retry_sha256': sha(b) if path in allpaths else None}
        if a == b:
            invariants.append(record)
        else:
            changes.append(record)
            if path != 'ch8-s1-control/CI-REQUEST.json':
                difftext.extend(difflib.unified_diff(a.decode().splitlines(True), b.decode().splitlines(True),
                                                    fromfile='7c/' + path, tofile='4336/' + path))
    (HERE / 'CONTROL-DELTA.diff').write_text(''.join(difftext))
    gates['only_reviewed_control_paths_changed'] = {x['path'] for x in changes} == {
        '.github/workflows/ch8-s1.yml', 'ch8-s1-control/CI-REQUEST.json', 'ch8-s1-control/check_package.py',
        'ch8-s1-control/runner.py', 'ch8-s1-control/cell_retry_profile.py',
        'ch8-s1-control/test_cell_retry.py', 'ch8-s1-control/test_package.py'}
    binary_records = []
    canonical = lambda snap: {k: v['sha256'] for k, v in snap['binaries'].items()}
    for p in sorted((OLD / 'evidence').glob('*/receipt.json')):
        g = read(p)
        export_path = p.parent / 'export.json'
        e = read(export_path)
        binary_records.append({'group': p.parent.name, 'receipt': ref(p, '6d300f3ab9801c808612b562588af06e0f7b4ff9'),
            'export': ref(export_path, '6d300f3ab9801c808612b562588af06e0f7b4ff9'),
            'old_before_sha256': canonical(g['tool_fingerprints_before']),
            'old_after_sha256': canonical(g['tool_fingerprints_after']),
            'retry_sha256': canonical(group['tool_fingerprints_before']),
            'binary_identity_equal': canonical(g['tool_fingerprints_before']) == canonical(g['tool_fingerprints_after']) ==
                                     canonical(group['tool_fingerprints_before']) == canonical(group['tool_fingerprints_after']),
            'version_identity_equal': e['tools'] == stock['tools'] and e['kani_commit'] == stock['kani_commit'],
            'old_tools': e['tools'], 'retry_tools': stock['tools']})
    gates['protected_binaries_all_13_origins_equal'] = len(binary_records) == 13 and all(x['binary_identity_equal'] and x['version_identity_equal'] for x in binary_records)
    old_cell = read(DIAG / 'structured/receipt.json')
    old_export = read(DIAG / 'structured/export.json')
    actual = {}
    for k in ('configuration', 'target', 'enabled_unstable_features', 'tools', 'kani_commit', 'kani_commit_dirty', 'harness_selection'):
        actual['export.' + k] = {'old': old_export.get(k), 'retry': stock.get(k), 'equal': old_export.get(k) == stock.get(k)}
    for k in ('effective_cfg', 'unwind', 'selectors', 'variant', 'source_under_test'):
        actual['group.' + k] = {'old': old_cell.get(k), 'retry': group.get(k), 'equal': old_cell.get(k) == group.get(k)}
    normargv = lambda a: [a[i] if i == 0 or a[i-1] != '--harness-timeout' else '<REVIEWED_TIMEOUT>' for i in range(len(a))]
    actual['argv_except_timeout'] = {'old': old_cell['argv'], 'retry': group['argv'], 'equal': normargv(old_cell['argv']) == normargv(group['argv'])}
    oh = {x['name']: x for x in old_export['harnesses']}
    for harness in stock['harnesses']:
        for k in ('resolved_solver', 'resolved_unwind', 'contract', 'attributes', 'is_bounded', 'crate_name'):
            actual[harness['name'] + '.' + k] = {'old': oh[harness['name']].get(k), 'retry': harness.get(k), 'equal': k in oh[harness['name']] and k in harness and oh[harness['name']][k] == harness[k]}
    gates['actual_semantic_config_solver_equal'] = all(x['equal'] for x in actual.values())
    review_paths = [BASE/'s1-08-cell-retry-review-r1/REVIEW.json', BASE/'s1-08-cell-retry-review-r1/VALIDATION.json', BASE/'s1-08-cell-retry-review-r1/REVIEW.md']
    report = {'schema': 's108-retry-compatibility-v1', 'status': 'PASS_FOR_NEXT_STAGE' if all(gates.values()) else 'MISMATCH',
        'gates': gates, 'request_delta': delta, 'row_delta': row_delta,
        'equal_request_fields': equal_fields, 'control_changed_paths': changes, 'control_byte_invariance': invariants,
        'actual_semantic_configuration': actual, 'protected_binaries_across_origins': binary_records,
        'review_guarantee_transfer': {'review_g0': '86c0b15f2f3ade2074e746eaccede68c8a291cbb', 'refs': [ref(p, '86c0b15f2f3ade2074e746eaccede68c8a291cbb') for p in review_paths],
            'scope': 'Reviewed runtime scheduling/timeout/test changes; unchanged decoder/native/snapshot/location/flags/ROLE-MAP by byte invariance; no new compiler audit'},
        'allowed_deltas': ['cell timeout600 to1200', 'derived child3300/envelope3310 and selected scheduling/artifact metadata', 'preflight/tests and associated payload hashes'],
        'unknown_fields': {'compiler_identity_status': UNKNOWN, 'compilation_id': UNKNOWN,
                           'independent_AST_MIR_contract_binding': UNKNOWN},
        'qualification': 'PENDING_OFFLINE', 'independent_proof_credit': 'NONE', 'composite_acceptance': 'NOT_CREATED'}
    write('COMPATIBILITY.json', report)
    return report


def timing(request, group, stock):
    baselines = [('s107', S107 / 'evidence/cell-u34/export.json', S107 / 'evidence/cell-u34/receipt.json', S107 / 'CI-REQUEST.json'),
                 ('s108_diagnostic929f', DIAG / 'structured/export.json', DIAG / 'structured/receipt.json', OLD / 'CI-REQUEST.json')]
    rows = []
    for harness in stock['harnesses']:
        rid = harness['name'].rsplit('::', 1)[1]
        comps = []
        for name, ep, rp, qp in baselines:
            e, g, q = map(read, (ep, rp, qp))
            prior, = [x for x in e['harnesses'] if x['name'] == harness['name']]
            a, b = prior['resources']['verification_time_s'], harness['resources']['verification_time_s']
            completed = prior['outcome'].get('kind') == harness['outcome'].get('kind') == 'COMPLETED'
            row_old, = [x for x in q['rows'] if x['id'] == rid]
            row_new, = [x for x in request['rows'] if x['id'] == rid]
            comps.append({'baseline': name, 'refs': [ref(p) for p in (ep, rp, qp)],
                'baseline_raw_verification_time_s': a, 'retry_raw_verification_time_s': b,
                'baseline_outcome': prior['outcome'], 'retry_outcome': harness['outcome'],
                'baseline_limit_s': e['harness_timeout_s'], 'retry_limit_s': stock['harness_timeout_s'],
                'completed_descriptive_ratio_retry_over_baseline': b/a if completed and a > 0 else None,
                'completed_descriptive_delta_s': b-a if completed else None,
                'cohort': 'COMPLETED_COMPLETED' if completed else 'BASELINE_TIMEOUT_CENSORED',
                'causal_or_same_profile_ratio': None,
                'censoring': None if completed else {'baseline_cutoff_s': 600, 'baseline_reported_elapsed_s': a,
                    'baseline_completion_time_s': None, 'interpretation': 'Right-censored old observation; no exact slowdown or fit600 inference'},
                'source_delta': {'baseline': q['std_sha'], 'retry': request['std_sha']},
                'request_delta': {'baseline': sha(qp.read_bytes()), 'retry': sha((HERE/'CI-REQUEST.json').read_bytes())},
                'control_delta': {'baseline': read(S107/'collected.json').get('control_sha') if name == 's107' else '21592884db439389364b416dea1515bfa9d8018e', 'retry': HEAD},
                'row_delta': {k: {'baseline': row_old.get(k), 'retry': row_new.get(k)} for k in sorted(row_old.keys()|row_new.keys()) if row_old.get(k)!=row_new.get(k)},
                'request_profile_delta': {k:{'baseline':q.get(k),'retry':request.get(k)} for k in ('flags','tool_sha','tool_tree','batch_policy','budgets','execution_scope','workflow_stages') if q.get(k)!=request.get(k)},
                'actual_config_delta': {k:{'baseline':e.get(k),'retry':stock.get(k)} for k in ('configuration','tools','enabled_unstable_features','harness_timeout_s','target') if e.get(k)!=stock.get(k)},
                'group_argv_delta': {'baseline':g['argv'],'retry':group['argv']}})
        rows.append({'row_id': rid, 'comparisons': comps})
    origin_deltas = []
    def leaves(a,b,pointer=''):
        if a == b: return []
        if isinstance(a,dict) and isinstance(b,dict):
            return [x for k in sorted(a.keys()|b.keys()) for x in leaves(a.get(k),b.get(k),pointer+'/'+k)]
        if isinstance(a,list) and isinstance(b,list) and len(a)==len(b):
            return [x for i,(av,bv) in enumerate(zip(a,b)) for x in leaves(av,bv,pointer+'/'+str(i))]
        return [{'pointer':pointer,'baseline':a,'retry':b}]
    for name,ep,rp,qp in baselines:
        baseline_head = read(S107/'collected.json')['control_sha'] if name=='s107' else '21592884db439389364b416dea1515bfa9d8018e'
        changed = gitraw(CONTROL,'diff','--name-only',baseline_head,HEAD,'ch8-s1-control','.github/workflows').decode().splitlines()
        origin_deltas.append({'baseline':name,'baseline_trigger':baseline_head,'retry_trigger':HEAD,
            'complete_request_field_delta':leaves(read(qp),request),
            'control_changed_paths':changed,
            'notes':'All request differences retained, including source/contract/label coordinates and payload hashes; no causal label claim.'})
    report = {'schema': 's108-cell-two-row-timing-v1', 'rows': rows, 'origin_deltas':origin_deltas, 'group_execution': clean(group['execution']),
        'scope': 'Separate two-row descriptive comparison; old35pairs immutable', 'fit600': 'NOT_ESTABLISHED',
        'label_causality': 'NOT_ESTABLISHED', 'measured_composite_runtime': None,
        'per_root_process_metrics': 'UNKNOWN_NO_SEPARATE_PROCESS_ATTRIBUTION', 'proof_credit': 'NONE'}
    write('TIMING-CELL.json', report)
    return report


def main():
    pins = read(BASE / 's1-08-composition-plan/INPUTS.json')
    need(h.git(CONTROL, 'rev-parse', HEAD+'^{tree}') == h.git(CONTROL, 'rev-parse', REVIEWED+'^{tree}') == pins['retry']['tree'], 'trigger/reviewed tree')
    need(h.git(CONTROL, 'rev-parse', HEAD+'^') == h.git(CONTROL, 'rev-parse', REVIEWED+'^') == pins['retry']['parent'], 'exact parents')
    request_bytes = (HERE / 'CI-REQUEST.json').read_bytes()
    need(sha(request_bytes) == pins['retry']['request_sha256'], 'exact request pin')
    need(request_bytes == blob(HEAD, 'ch8-s1-control/CI-REQUEST.json'), 'trigger request bytes')
    request = json.loads(request_bytes)
    for rel, expected in request['ci_payload_sha256'].items():
        raw = blob(HEAD, rel)
        need(sha(raw) == expected, 'exact control payload '+rel)
        if rel.startswith('ch8-s1-control/'):
            need((HERE/'replay-control'/rel.removeprefix('ch8-s1-control/')).read_bytes() == raw, 'replay payload '+rel)
    for p in (HERE/'replay-control').rglob('*'):
        if p.is_file(): need(p.read_bytes() == blob(HEAD,'ch8-s1-control/'+str(p.relative_to(HERE/'replay-control'))), 'exact replay tree member')
    need(h.git(STD,'rev-parse',request['std_sha']+'^{tree}') == request['std_tree'] and
         h.git(CONTROL,'rev-parse',request['tool_sha']+'^{tree}') == request['tool_tree'], 'source/tool trees')
    for rel, expected in request['changed_file_sha256'].items():
        need(sha(gitraw(STD,'show',request['std_sha']+':'+rel)) == expected, 'exact std file '+rel)
    need(sha((HERE/'ROLE-MAP.json').read_bytes()) == pins['common']['role_map_sha256'], 'ROLE-MAP')
    sys.path.insert(0, str(HERE/'replay-control'))
    import runner as r
    import collect
    need(r.load_request() == request, 'exact pinned request loader')
    identity, artifacts, jobs = map(read, (HERE/'run-identity.json', HERE/'artifacts-metadata.json', HERE/'jobs-metadata.json'))
    need(identity['id'] == RUN and identity['run_attempt'] == 1 and identity['head_sha'] == HEAD and
         identity['head_commit']['tree_id'] == pins['retry']['tree'] and identity['status'] == 'completed' and
         identity['conclusion'] == 'success' and identity['head_branch'] == pins['retry']['branch'] and
         identity['event'] == 'push' and identity['path'] == '.github/workflows/ch8-s1.yml', 'terminal attempt/head/tree')
    job, = jobs['jobs']
    attempt_jobs=read(HERE/'jobs-attempt1.json')
    exact_job,=attempt_jobs['jobs']
    need(attempt_jobs['total_count']==1 and exact_job['id']==job['id'] and exact_job['run_id']==RUN and
         exact_job['run_attempt']==1 and exact_job['head_sha']==HEAD and exact_job['status']=='completed' and
         exact_job['conclusion']=='success', 'attempt1 exact job identity')
    need(job['run_id'] == RUN and job['name'] == 's1_cell (cell-u34)' and job['status'] == 'completed' and
         job['conclusion'] == 'success' and all(x['conclusion'] == 'success' for x in job['steps']), 'terminal selected job/steps')
    artifact, = artifacts['artifacts']
    need(artifact['name'] == pins['retry']['expected_compact_artifact_name'] and not artifact['expired'] and
         artifact['workflow_run']['id'] == RUN and artifact['workflow_run']['head_sha'] == HEAD and
         artifact['workflow_run']['head_branch'] == identity['head_branch'], 'artifact embedded origin')
    root = HERE/'artifacts'/artifact['name']
    zipinfo = read(root/'zip-integrity.json')
    need(zipinfo['github_digest_match'] and artifact['digest'] == 'sha256:'+zipinfo['sha256'] and
         artifact['size_in_bytes'] == zipinfo['bytes'], 'ZIP pre-extraction digest attestation')
    need(sha((root/'group-evidence.json.gz').read_bytes()) == zipinfo['payload_sha256'], 'compact payload digest')
    doc, files, data, size = h.compact(root)
    allowed = {'receipt.json','setup/receipt.json','job-status.json',*[rid+'/receipt.json' for rid in PAIR],
               *['groups/cell-u34/'+name for name in ('receipt.json','export.json','properties.json','binding-metadata.json','compile/receipt.json')]}
    need(set(files) == allowed, 'exact structured compact namespace')
    terminal, group, stock, rich, meta, comp = [files[k] for k in ('receipt.json','groups/cell-u34/receipt.json','groups/cell-u34/export.json',
        'groups/cell-u34/properties.json','groups/cell-u34/binding-metadata.json','groups/cell-u34/compile/receipt.json')]
    validate_origin(terminal, group, request, sha(request_bytes))
    collected = collect.collect([root], request)
    selected = validate_selection(collected)
    # Exact unmodified collector result and separate sanitized 35-row view.
    write('collector-exact.json', collected)
    write('collected.json', {**clean(collected), 'qualified_acceptance':'PENDING_OFFLINE',
          'collector_original_qualification':collected['qualified_acceptance']})
    for rel in allowed:
        dest = HERE/'evidence'/rel
        dest.parent.mkdir(parents=True,exist_ok=True)
        if rel.endswith('receipt.json'): dest.write_text(json.dumps(clean(files[rel]),indent=2,sort_keys=True)+'\n')
        else: dest.write_bytes(data[rel])
    need(comp['state'] == 'COMPLETE' and comp['request_sha256'] == sha(request_bytes), 'compile complete/request')
    need(meta['state'] == 'CAPTURED_AVAILABLE_FIELDS' and meta['errors'] == [] and
         meta['source_before'] == meta['source_after'] == group['source_before'] and
         meta['execution'] == group['execution'], 'metadata context')
    need(meta['configuration_sha256'] == sha(json.dumps({'flags':request['flags'],'cfg':group['effective_cfg'],'argv':group['argv']},sort_keys=True).encode()),'configuration digest')
    need(meta['requirements_sha256'] == request['binding_metadata_requirements_sha256'] and meta['compiler_identity_status'] == UNKNOWN and meta['compilation_id'] is None, 'metadata known gaps')
    for phase, snap in [('BEFORE_CHILD',group['tool_fingerprints_before']),('AFTER_CHILD_SHUTDOWN',group['tool_fingerprints_after'])]:
        need(snap['phase'] == phase and snap['state'] == 'COMPLETE' and snap['snapshot_completed'] is True and
             snap['required_binaries'] == ['kani_driver','kani_compiler','cbmc'] and snap['missing_binaries'] == [], 'snapshot phase/completion')
    need(r.fingerprints_match(group['tool_fingerprints_before'],group['tool_fingerprints_after']) and not group['snapshot_errors'], 'before/after binary invariance')
    ex = group['execution']
    need(ex['child_shutdown_verified'] is True and ex['original_exit_code'] == 0 and ex['signal'] is None and not ex['timed_out'] and
         not ex.get('termination_reason') and all(ex[k] is False for k in ('stdout_truncated','stderr_truncated','output_truncated')), 'exit/shutdown/truncation')
    need(not group.get('original_exception') and not group.get('execution_exception') and not meta.get('original_exception') and not meta.get('execution_exception'), 'original exceptions')
    need(stock['harness_timeout_s'] == 1200 and stock['run_state'] == 'COMPLETE', 'stock timeout/completion')
    for rid in PAIR:
        receipt=files[rid+'/receipt.json']
        observed,=[x for x in selected if x['id']==rid]
        need(receipt==observed, 'exact row receipt equals terminal/collector row')
        need(receipt['root_timeout_seconds']==1200 and receipt['original_exit'] is None and
             receipt['per_root_rss_kib'] is None and receipt['group_original_exit']==ex['original_exit_code'] and
             receipt['group_export_sha256']==sha(data['groups/cell-u34/export.json']) and
             receipt['rich_evidence_sha256']==sha(data['groups/cell-u34/properties.json']), 'row timeout/unknown process metrics/digests')
    need(files['job-status.json']['job_status']=='success' and files['job-status.json']['request_sha256']==sha(request_bytes), 'embedded job status/request')
    setup=files['setup/receipt.json']
    need(setup['original_exit_code']==0 and setup['child_shutdown_verified'] is True and
         setup['timed_out'] is False and setup['signal'] is None, 'setup completion')
    pairs = inventories(stock,rich)
    diagnostics, partitions, locations, rows = [], [], [], []
    for harness, props in pairs:
        rid = harness['name'].rsplit('::',1)[1]
        spec, = [x for x in request['rows'] if x['id'] == rid]
        native, = [x for x in meta['rows'] if x['row_id'] == rid]
        need(all(x == UNKNOWN for x in native['binding_gaps'].values()), 'preserve native gaps')
        parsed = r.parse_export(HERE/'evidence/groups/cell-u34/export.json', spec,
                source_binding=request['source_bindings'][rid], std=STD, group_selectors=group['selectors'])
        need(parsed['state'] == 'RECORDED_OBSERVATION', 'stock parse '+rid)
        exceptions = [x for x in rich['location_exceptions'] if x['harness'] == harness['name']]
        nullable = [p for p in props if p['file'] is None or p['line'] is None]
        need(nullable == [x['property'] for x in exceptions], 'exact nullable exception set')
        need(all(p['class'] == 'unreachable' and p['status'] == 'SUCCESS' and p['description'] == 'unreachable code' and p['file'] is None and p['line'] is None for p in nullable), 'exception exact fields')
        locations.extend({'row_id':rid,**x} for x in exceptions)
        statuses = {s:[p['id'] for p in props if p['status']==s] for s in sorted({p['status'] for p in props})}
        classes = {c:[p['id'] for p in props if p['class']==c] for c in sorted({p['class'] for p in props})}
        pfc = [p for p in props if p['class'] in ('single_top_level_call','no_recursive_call','assigns') or
               'sorting_model::post' in p['description']]
        partitions.append({'row_id':rid,'inventory_complete':True,'inventory_count':len(props),'by_status':statuses,'by_class':classes,
            'U_sites':[p for p in props if p['status']=='UNREACHABLE'], 'PFC_candidate_sites':pfc,
            'PFC_scope':'DIAGNOSTIC_CANDIDATES_ONLY; full native inventory available; concrete Profiles-v4 chain must be rebuilt at acceptance',
            'native_harness_records':native['native_harness_records'], 'binding_gaps':native['binding_gaps'],
            'full_inventory_ref':'evidence/groups/cell-u34/properties.json', 'native_ref':'evidence/groups/cell-u34/binding-metadata.json',
            'qualification':'PENDING_OFFLINE','proof_credit':'NONE'})
        for role in read(HERE/'ROLE-MAP.json')['required_success_bindings']:
            if role['row_id']!=rid: continue
            matches=[p for p in props if p['class']=='assertion' and p['description']==role['expected_description'] and
                     p.get('line') in {str(x) for x in role['source']['allowed_property_lines']} and isinstance(p.get('file'),str) and
                     p['file'].endswith('/'+role['source']['file'])]
            diagnostics.append({'row_id':rid,'role':role['role'],'binding_kind':role['binding_kind'],
                'expected_description':role['expected_description'],'status':'FOUND_SUCCESS' if len(matches)==1 and matches[0]['status']=='SUCCESS' else 'MISSING_OR_DUPLICATE_OR_NON_SUCCESS',
                'properties':matches,'inventory_complete':True,'qualification':'PENDING_OFFLINE'})
        covers=[{'message':msg,'properties':[p for p in props if p['class']=='cover' and p['description']==msg]} for msg in spec['required_cover_messages']]
        need(all(len(x['properties'])==1 and x['properties'][0]['status']=='SATISFIED' for x in covers), 'required SAT covers')
        observed, = [x for x in selected if x['id']==rid]
        rows.append({**clean(observed), 'evidence':{'raw_outcome':harness['outcome'],'verification_time_s':harness['resources']['verification_time_s'],
            'stock_property_count':harness['n_properties'],'rich_property_count':len(props),'inventory_complete':True,
            'stock_checks':harness['checks'],'stock_covers':harness['covers'],'required_covers':covers,
            'location_exceptions':exceptions,'native_harness_records':native['native_harness_records'],'binding_gaps':native['binding_gaps'],
            'per_root_process_exit':None,'per_root_wall_seconds':None,'per_root_rss_kib':None,
            'per_root_measurement_scope':'UNKNOWN_NO_SEPARATE_PROCESS_ATTRIBUTION', 'group_original_exit':ex['original_exit_code'],
            'group_elapsed_seconds':ex['elapsed_seconds'],'group_rss_peak_kib':ex['rss_peak_kib'],
            'inventory_ref':'evidence/groups/cell-u34/properties.json','stock_ref':'evidence/groups/cell-u34/export.json',
            'native_ref':'evidence/groups/cell-u34/binding-metadata.json'}, 'qualified_acceptance':'PENDING_OFFLINE','group_admitted':False,'proof_credit':'NONE'})
    need(len(diagnostics)==10 and all(x['status']=='FOUND_SUCCESS' for x in diagnostics), '10 required role diagnostics')
    write('LABEL-COVERAGE.json',{'scope':'ALL10_SELECTED_REQUIRED_ROLES_DIAGNOSTIC_ONLY','records':diagnostics})
    write('INVENTORY-PARTITIONS.json',{'rows':partitions,'qualification':'PENDING_OFFLINE','proof_credit':'NONE'})
    write('LOCATION-EXCEPTIONS.json',{'records':locations,'policy':request['location_exception_policy'],'admission':'PENDING_OFFLINE'})
    origin={'repository':'Tiramisu-Cake/kani','run_id':RUN,'attempt':1,'trigger_sha':HEAD,'reviewed_control_sha':REVIEWED,
        'control_tree':pins['retry']['tree'],'parent':pins['retry']['parent'],'request_sha256':sha(request_bytes),
        'std_sha':request['std_sha'],'tool_sha':request['tool_sha'],'group':GID,'invocation_id':group['invocation_id'],
        'artifact_id':artifact['id'],'artifact_name':artifact['name'],'artifact_digest':artifact['digest']}
    write('selected-cell.json',{'schema':'s108-selected-cell-intake-v1','origin':origin,'rows':rows,'group_state':'COMPLETE',
        'qualification':'PENDING_OFFLINE','group_admitted':False,'proof_credit':'NONE','group':clean(group)})
    c = compatibility(request,group,stock)
    t = timing(request,group,stock)
    inputs={'task':'TASK-CH8-S1-08-RETRY-INTAKE-W13.md','prepared_task_g0':'dad394c5948af7dde9f6195b5e7d461f6b040a8d',
        'prepared_task':ref(BASE.parent.parent/'TASK-CH8-S1-08-RETRY-INTAKE-W13.md','dad394c5948af7dde9f6195b5e7d461f6b040a8d'),
        'authority':'Explicit current owner/coordinator issuance after TERMINAL completed success; pipeline authorized; packet PREPARATION_ONLY is not runtime GO',
        'origin':origin,'composition_plan':ref(BASE/'s1-08-composition-plan/INPUTS.json'),
        'original_intake_g0':pins['original']['intake_g0'],'original_intake_path':'../run-44095954742/',
        'package_g0':pins['retry']['package_g0'],'review_g0':pins['retry']['review_g0'],
        'ledger_reference_only':pins['accounting'],'outputs':'THIS_DIRECTORY_ONLY', 'no_new_execution':True}
    write('INPUTS.json',inputs)
    write('PROVENANCE.json',{'origin':origin,'metadata_source':'GitHub connected read-only GET tools; exact attempt1 run + jobs/artifact metadata',
        'download':'One selected compact artifact only; ZIP digest/bytes verified before opening members; ZIP not retained',
        'zip_attestation':zipinfo,'compact_uncompressed_bytes':size,'embedded_members':{k:{x:v[x] for x in ('bytes','sha256','encoding')} for k,v in doc['files'].items()},
        'projection_policy':'stock/rich/native exact bytes; receipt projections remove only stdout/stderr previews. Exact compact original retained.',
        'helper_reuse':ref(OLD/'intake.py',pins['original']['intake_g0']), 'replay':'Unmodified trigger collector with own request and one selected artifact only',
        'original_evidence':'Read-only refs only; no old artifact download; no mixed collector',
        'exceptions':{'original_exception':group.get('original_exception'),'execution_exception':group.get('execution_exception'),
                      'field_presence':{k:k in group for k in ('original_exception','execution_exception')},
                      'note':'Absent group exception fields remain absent in original; null here is a presence-qualified projection'},
        'native_files':len(meta['native_metadata']),'native_bytes':sum(x['bytes'] for x in meta['native_metadata']),
        'proof_credit':'NONE','qualification':'PENDING_OFFLINE'})
    validation={'schema':'s108-retry-intake-validation-v1','status':'PASS' if all(c['gates'].values()) else 'COMPATIBILITY_MISMATCH',
        'terminal':'completed success','exact_origin':True,'compact_integrity':True,'exact_collector_replay':True,
        'declared_groups':14,'selected_complete_groups':1,'unselected_missing_reference_groups':13,
        'declared_rows':35,'observed_rows':2,'unselected_NOT_RUN_UNKNOWN_rows':33,
        'stock_properties':sum(len(p) for _,p in pairs),'rich_properties':sum(len(p) for _,p in pairs),
        'required_role_label_diagnostics':len(diagnostics),'required_SAT_covers':sum(len(x['evidence']['required_covers']) for x in rows),
        'U_sites':sum(len(x['U_sites']) for x in partitions),'location_exceptions':len(locations),
        'native_files':len(meta['native_metadata']),'native_bytes':sum(x['bytes'] for x in meta['native_metadata']),
        'stock_rich_native_reconciliation':True,'source_binary_before_after_shutdown_exit_checks':True,
        'compatibility_gates':c['gates'],'qualification':'PENDING_OFFLINE','independent_proof_credit':'NONE',
        'admission':'NOT_GRANTED','runner_compiler_verifier_CI_push_ledger':'NOT_RUN_NOT_MODIFIED'}
    write('VALIDATION.json',validation)
    print(json.dumps(validation,sort_keys=True))


if __name__ == '__main__':
    main()
