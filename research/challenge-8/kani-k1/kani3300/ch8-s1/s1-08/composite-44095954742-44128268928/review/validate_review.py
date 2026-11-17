#!/usr/bin/env python3
"""Bounded independent review; writes only review/VALIDATION.json.

Exact candidate and intake bytes, separate read-only collectors, structured gates,
and targeted adapter mutations. No compiler, verifier, full runner or network.
"""
import collections
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ACCEPT = HERE.parent / 'accept'
ROOT = HERE.parents[7]
CANDIDATE = '3c40a15d37890c8b5ef7ba49308e81279a494b05'
TASK = '65353172b301b5ce1aafb7030adfa0686fe86c2e'
ACCEPT_SHA = '76addef689c8808658be0bc85619b413d279ce9d692e4199822ea2284e2b97c2'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + '\n').encode()


def read(path):
    return json.loads(path.read_bytes())


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args])


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def check(ok, message):
    if not ok:
        raise AssertionError(message)


def main():
    candidate_files = git('ls-tree', '-r', '--name-only', CANDIDATE, str(ACCEPT.relative_to(ROOT))).decode().splitlines()
    before = {p: digest((ROOT / p).read_bytes()) for p in candidate_files}
    for rel in candidate_files:
        check((ROOT / rel).read_bytes() == git('show', CANDIDATE + ':' + rel), 'candidate bytes: ' + rel)
    check(digest((ACCEPT / 'ACCEPT.json').read_bytes()) == ACCEPT_SHA, 'issued ACCEPT hash')
    task_path = 'research/challenge-8/kani-k1/TASK-CH8-S1-08-COMPOSITE-REVIEW-W14.md'
    check((ROOT / task_path).read_bytes() == git('show', TASK + ':' + task_path), 'issued task bytes')
    manifest = read(ACCEPT / 'INPUTS.json')
    for rel, pin in manifest['files'].items():
        raw = (ROOT / rel).read_bytes()
        check(digest(raw) == pin['sha256'], 'manifest raw SHA: ' + rel)
        check(raw == git('show', pin['commit'] + ':' + rel), 'manifest commit: ' + rel)
    inputs_before = {p: digest((ROOT / p).read_bytes()) for p in manifest['files']}
    replay = subprocess.run([sys.executable, '-I', '-B', str(ACCEPT / 'replay.py')], capture_output=True, text=True, timeout=180)
    check(replay.returncode == 0, 'default replay: ' + replay.stderr)
    replay_result = json.loads(replay.stdout)
    check(replay_result['replay'] == 'MATCH' and replay_result['sha256'] == ACCEPT_SHA, 'default replay equality')
    m = load('independent_composite_review_target', ACCEPT / 'replay.py')
    report = read(ACCEPT / 'ACCEPT.json')
    b = m.load(False)
    b['replays'] = report['origin_replays']  # Their actual execution was just checked by the CLI.
    rebuilt, omap, compatibility = m.compose(b)
    check(encoded(rebuilt) == (ACCEPT / 'ACCEPT.json').read_bytes(), 'pure composition bytes')
    check(encoded(omap) == (ACCEPT / 'ORIGIN-MAP.json').read_bytes(), 'origin map bytes')
    check(encoded(compatibility) == (ACCEPT / 'COMPATIBILITY.json').read_bytes(), 'compatibility bytes')
    hashes = {}
    for origin, ob in b['origins'].items():
        path = m.runpath(origin) / ('runner-collected.json' if origin == 'original' else 'collector-exact.json')
        hashes[origin] = {'raw_file_sha256': digest(path.read_bytes()),
                          'canonical_sanitized_json_sha256': digest(encoded(ob['collected']))}
        check(hashes[origin]['raw_file_sha256'] == report['origin_replays'][origin]['immutable_receipt']['sha256'], 'raw receipt identity')
        check(hashes[origin]['canonical_sanitized_json_sha256'] == report['origin_replays'][origin]['collector_receipt_sha256'], 'canonical receipt identity')
        check(digest((m.runpath(origin) / 'CI-REQUEST.json').read_bytes()) == m.REQUESTS[origin], 'raw request identity')
        hashes[origin]['raw_request_sha256'] = m.REQUESTS[origin]
        hashes[origin]['canonical_request_sha256'] = digest(encoded(ob['request']))
        check(hashes[origin]['canonical_request_sha256'] == manifest['canonical_requests'][origin], 'canonical request identity')
    rows = {r['id']: r for r in report['rows']}
    req = b['origins']['original']['request']
    specs = {r['id']: r for r in req['rows']}
    roles = read(m.runpath('original') / 'ROLE-MAP.json')['required_success_bindings']
    raw_properties = {}
    origin_totals = {}
    expected_u = set()
    for origin, ob in b['origins'].items():
        counts = collections.Counter()
        for gid, g in ob['groups'].items():
            for h in g['properties.json']['harnesses']:
                rid, = [s['id'] for s in req['rows'] if s['selector'] == h['name'] and s['variant'] == g['receipt.json']['variant']]
                props = {p['id']: p for p in h['properties']}
                raw_properties[rid] = props
                counts['rows'] += 1
                counts['properties'] += len(props)
                for p in props.values():
                    if p['status'] == 'UNREACHABLE':
                        expected_u.add((origin, rid, p['id']))
                        counts['U_covers' if p['class'] == 'cover' else 'U_checks'] += 1
                row = rows[rid]
                check(row['origin_key'] == str(m.RUNS[origin]) + '/1', 'row origin')
                check(row['evidence_hashes'] == omap['origins'][origin]['groups'][gid]['projection_hashes'], 'origin projection hashes')
                for role in row['required_success']:
                    expected, = [s for s in roles if (s['row_id'], s['role']) == (rid, role['role'])]
                    source = expected['source']
                    text = m.source_text(source['file'])
                    check(digest(text.encode()) == source['sha256'], 'whole source hash')
                    for site in source['sites']:
                        check('\n'.join(text.splitlines()[site['line']-1:site.get('end_line', site['line'])]).strip() == site['text'].strip(), 'fresh source span')
                        check(digest(site['text'].encode()) == site['sha256'], 'site hash')
                    check(role['binding'] == expected['binding_kind'], 'required role binding')
                    check(len(role['properties']) == (3 if role['binding'] == 'EXACT_SUCCESS_SEMANTIC_SET' else 1), 'role instance cardinality')
                    for p in role['properties']:
                        raw = props[p['id']]
                        check(raw['status'] == 'SUCCESS' and raw['class'] == 'assertion' and raw['description'] == expected['expected_description'], 'actual role property')
                        check(p['sha256'] == digest(encoded(raw)) and p['origin_key'] == row['origin_key'], 'role actual hash/origin')
                        check(raw['file'] == m.PREFIX + source['file'] and int(raw['line']) in source['allowed_property_lines'], 'actual source role site')
                    counts['required_roles'] += 1
                for cover in row['required_covers']:
                    check(cover['property']['origin_key'] == row['origin_key'] and props[cover['property']['id']]['status'] == 'SATISFIED', 'actual SAT cover origin')
                    check(cover['binding'] == 'EXACT_SAT_COVER_SEMANTIC', 'cover semantic order')
                    counts['required_SAT_covers'] += 1
                failures = [p for p in props.values() if p['status'] == 'FAILURE']
                if specs[rid]['expected'] == 'DETECTED':
                    check(len(failures) == 1 and failures[0] == row['negative_oracle']['property'], 'sole negative oracle')
                    check(failures[0]['id'] == specs[rid]['oracle']['property_id'], 'exact predeclared negative')
                    counts['negatives'] += 1
                else:
                    check(not failures, 'unexpected failure')
        origin_totals[str(m.RUNS[origin]) + '/1'] = dict(counts)
    got_u = set()
    for record in report['U_records']:
        rid = record['row_id']; row = rows[rid]
        origin = 'retry' if row['origin_key'] == '44128268928/1' else 'original'
        key = (origin, rid, record['property_id'])
        check(key not in got_u, 'duplicate U')
        got_u.add(key)
        raw = raw_properties[rid][record['property_id']]
        check(raw['status'] == 'UNREACHABLE' and raw['class'] == record['class'] and raw['description'] == record['description'], 'actual U property')
        check(record['origin_key'] == row['origin_key'] and record['native_root'] == row['native_root'] and record['evidence_sha256'] == row['evidence_hashes'], 'U origin binding')
        check(record['source_sha256'] == digest(m.source_text(record['site']['source_path']).encode()), 'U actual source SHA')
        check(record['decision'].startswith('ALLOWED_') and raw['class'] not in {'assigns', 'frees', 'postcondition'}, 'U mandatory distinction')
    check(got_u == expected_u, 'all and only actual U coverage')
    pfc = {p['id']: p for p in report['PFC_bindings']}
    for rid, chain in pfc.items():
        row = rows[rid]
        check(chain['origin_key'] == row['origin_key'] and chain['invocation_id'] == omap['origins']['retry' if row['origin_key'] == '44128268928/1' else 'original']['groups'][row['group']]['invocation_id'], 'PFC origin/invocation')
        check(m.helpers()[6].pfc_chain(chain, row, specs[rid], req), 'full PFC chain consumer')
        check(digest(encoded(chain)) == row['PFC']['sha256'], 'PFC consumed hash')
        origin_totals[row['origin_key']]['PFC'] = origin_totals[row['origin_key']].get('PFC', 0) + 1
    # Independent least-fixed-point calculation; do not accept expected 35 as a seed.
    local = {rid for rid, r in rows.items() if not r['local_pending_gates'] and all(s['binding'] != 'PENDING' for s in r['required_success'])
             and all(c['binding'] == 'EXACT_SAT_COVER_SEMANTIC' for c in r['required_covers'])
             and not r['U']['pending'] and (r['mode'] != 'PFC' or rid in pfc)}
    qualified = set()
    while True:
        new = {rid for rid in local if not specs[rid].get('companion') or (specs[rid]['companion'] in qualified
               and rows[rid]['origin_key'] == rows[specs[rid]['companion']]['origin_key'] == '44095954742/1')}
        if new == qualified:
            break
        qualified = new
    check(qualified == {rid for rid, row in rows.items() if row['qualification'] == 'QUALIFIED'}, 'independent row qualification')
    for union in req['replacement_unions']:
        members = union['member_row_ids']
        check(len(set(members)) == 4 and {rows[r]['domain_N'] for r in members} == {0, 1, 2, 3}, 'union domain')
        check(all(r in qualified and rows[r]['origin_key'] == '44095954742/1' for r in members), 'union all members/own origin')
    checks = []
    def case(name, fn, reject=False):
        try:
            result = fn()
        except (ValueError, KeyError, TypeError, IndexError) as exc:
            check(reject, name + ': unexpected rejection: ' + str(exc))
            checks.append({'case': name, 'status': 'PASS', 'result': 'REJECTED', 'reason': str(exc)})
        else:
            check(not reject and result, name + ': gate accepted mutation')
            checks.append({'case': name, 'status': 'PASS', 'result': 'DISCRIMINATED'})
    # Replay the 39 NEW author tests with its sole receipt write captured in memory.
    # No unchanged upstream test suite is run and accept/MUTATIONS.json is untouched.
    author = load('independent_review_author_tests', ACCEPT / 'test_replay.py')
    captured = []
    def capture(path, raw):
        check(path == ACCEPT / 'MUTATIONS.json', 'unexpected author-test write')
        captured.append(json.loads(raw))
        return len(raw)
    with patch.object(Path, 'write_bytes', capture), contextlib.redirect_stdout(io.StringIO()):
        author.main()
    check(len(captured) == 1 and captured[0]['status'] == 'PASS' and captured[0]['tests'] == 39, '39 author adapter tests')
    # Reviewer-owned mutations target the three new source adapters below outer hashes.
    rid = 'model_u8_n0_3'; row = rows[rid]
    role = next(s for s in roles if s['row_id'] == rid and s['role'] == 'fnonce_two_projections')
    props = list(raw_properties[rid].values())
    case('multiline_48_49_actual_source_and_property', lambda: m.role_binding(row, role, props)['binding'] == 'EXACT_ROLE_LABEL')
    bad_role = copy.deepcopy(role); bad_role['source']['sites'][0]['end_line'] = 48
    case('multiline_truncated_source_site', lambda: m.role_binding(row, bad_role, props), True)
    bad_role = copy.deepcopy(role); bad_role['source']['sites'][0]['sha256'] = 'f' * 64
    case('multiline_wrong_site_hash', lambda: m.role_binding(row, bad_role, props), True)
    bad_props = copy.deepcopy(props)
    target = next(p for p in bad_props if p['description'] == role['expected_description'])
    target['line'] = '49'; target['location_display'] = target['location_display'].replace(':61:1 ', ':49:1 ')
    case('multiline_foreign_property_line', lambda: m.role_binding(row, role, bad_props)['binding'] == 'PENDING')
    model_path = role['source']['file']; actual_source = m.source_text(model_path)
    source_original = m.source_text
    def cover_mutant(text):
        with patch.object(m, 'source_text', lambda p: text if p == model_path else source_original(p)):
            return m.cover_binding(row, row['required_covers'][0]['message'], props)['binding'] == 'PENDING'
    positive = row['required_covers'][0]['source']
    case('positive_actual_operations_after_assume_before_covers', lambda: positive['operation_source_lines'] == [34, 42, 43, 45, 47, 48, 50, 51]
         and max(positive['assumption_source_lines']) < min(positive['operation_source_lines'])
         and max(positive['operation_source_lines']) < min(positive['cover_source_lines']))
    case('positive_missing_assumption', lambda: cover_mutant(actual_source.replace('kani::assume(len <= 3);', '/* removed */')))
    lines = actual_source.splitlines(); lines[33], lines[51] = lines[51], lines[33]
    case('positive_cover_before_operation', lambda: cover_mutant('\n'.join(lines) + '\n'))
    uid = 'freeze_copy_u8_n0'; urow = rows[uid]
    with_specs = copy.deepcopy(rows)
    for key, value in with_specs.items():
        value['spec'] = specs[key]
    target_record = next(r for r in report['U_records'] if r['row_id'] == uid and r['site']['line'] == '128')
    target_id = target_record['property_id']
    def one_u(bundle=b, current_rows=with_specs):
        return next(r for r in m.unreachable(bundle, 'original', current_rows) if r['row_id'] == uid and r['property_id'] == target_id)
    case('N1_guard_actual_N0_U128', lambda: one_u()['decision'] == 'ALLOWED_EXPECTED_BRANCH_UNREACHABLE')
    rcopy = copy.deepcopy(with_specs); rcopy[uid]['domain_N'] = 1
    case('N1_guard_applicable_N1_stays_unresolved', lambda: not one_u(current_rows=rcopy)['decision'].startswith('ALLOWED_'))
    smoke_path = target_record['site']['source_path']; smoke = m.source_text(smoke_path)
    def bad_guard():
        with patch.object(m, 'source_text', lambda p: smoke.replace('if $exact_n == 1 {', 'if $exact_n != 1 {') if p == smoke_path else source_original(p)):
            one_u()
    case('N1_guard_source_inversion', bad_guard, True)
    changed = copy.deepcopy(b)
    group = changed['origins']['original']['groups'][urow['group']]
    h = next(h for h in group['properties.json']['harnesses'] if h['name'] == urow['selector'])
    target = next(p for p in h['properties'] if p['id'] == target_id)
    target['line'] = '137'; target['location_display'] = target['location_display'].replace(':128:', ':137:')
    case('N1_guard_old137_exception_not_reused', lambda: not one_u(bundle=changed)['decision'].startswith('ALLOWED_'))
    def mandatory(kind):
        v = copy.deepcopy(b); g = v['origins']['original']['groups'][urow['group']]
        props = next(h['properties'] for h in g['properties.json']['harnesses'] if h['name'] == urow['selector'])
        if kind == 'role':
            pid = next(s for s in urow['required_success'] if s['role'] == 'post_independent_caller')['properties'][0]['id']
            p = next(p for p in props if p['id'] == pid)
        else:
            p = next(p for p in props if p['class'] == kind)
        p['status'] = 'UNREACHABLE'
        stock = next(h for h in g['export.json']['harnesses'] if h['name'] == urow['selector'])
        stock['checks']['success'] -= 1; stock['checks']['unreachable'].append(p['id'])
        rec = next(r for r in m.unreachable(v, 'original', with_specs) if r['row_id'] == uid and r['property_id'] == p['id'])
        return rec['decision'] == 'BLOCK_MANDATORY_POST_FRAME_RELATION_UNREACHABLE'
    for kind in ('role', 'assigns', 'frees'):
        case('mandatory_' + kind + '_U_blocked', lambda kind=kind: mandatory(kind))
    p, pb = m.pfc_bundle(b, 'original')
    chain = pfc[uid]
    pprops = copy.deepcopy(list(raw_properties[uid].values()))
    next(prop for prop in pprops if prop['id'] == chain['contract']['ensures'][0]['property']['id'])['status'] = 'UNREACHABLE'
    stock = next(h for h in b['origins']['original']['groups'][urow['group']]['export.json']['harnesses'] if h['name'] == urow['selector'])
    case('mandatory_actual_PFC_ensures_U_rejected', lambda: p.contract_properties(pb, specs[uid], stock, pprops, chain['selected_impl'], chain['type'], chain['trait']), True)
    # Check source-reported compatibility below the manifest using actual groups.
    for field in ('configuration', 'target', 'enabled_unstable_features'):
        v = copy.deepcopy(b)
        v['origins']['retry']['groups']['cell-u34']['export.json'][field] = None
        case('compatibility_actual_' + field, lambda v=v: m.compatibility(v)['status'] == 'PENDING')
    inputs_after = {p: digest((ROOT / p).read_bytes()) for p in manifest['files']}
    after = {p: digest((ROOT / p).read_bytes()) for p in candidate_files}
    check(inputs_before == inputs_after and before == after, 'all candidate/intake inputs unchanged')
    result = {'schema': 's108-composite-independent-review-validation-v1', 'status': 'PASS',
              'review_task_commit': TASK, 'candidate_commit': CANDIDATE, 'candidate_raw_sha256': before,
              'manifest_inputs_checked': len(manifest['files']), 'actual_default_read_only_replay': replay_result,
              'collector_hash_distinctions': hashes, 'compatibility_gates': compatibility['gates'],
              'derived_qualified_rows': len(qualified), 'derived_qualified_row_ids': sorted(qualified),
              'origin_component_totals': origin_totals, 'actual_U_coverage': len(got_u),
              'new_U128_records': sum(r['site']['source_path'].endswith('sorting_entry_smoke.rs') and r['site']['line'] == '128' for r in report['U_records']),
              'reviewer_targeted_checks': checks, 'author_new_mutations_independently_replayed': captured[0]['receipts'],
              'unchanged_upstream_tests_repeated': 0, 'candidate_and_inputs_unchanged': True,
              'independent_compiler_AST_MIR_B1_B2_general_credit': 'NONE',
              'execution': 'OFFLINE_STRUCTURED_ONLY; NO_SUBAGENTS_CI_VERIFIER_COMPILER_FULL_RUNNER_PUSH_LEDGER',
              'accounting_reference_only': {'item2': '9/14', 'total': '35/40', 'modified': False}}
    (HERE / 'VALIDATION.json').write_bytes(encoded(result))
    print(json.dumps({'status': 'PASS', 'qualified_rows': len(qualified), 'reviewer_targeted_checks': len(checks), 'author_new_mutations': 39}, sort_keys=True))


if __name__ == '__main__':
    main()
