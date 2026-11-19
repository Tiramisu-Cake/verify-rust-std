#!/usr/bin/env python3
"""Exact reporting delta only; never execute intake main, native or policy readers."""
import ast
import copy
import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
G0 = HERE.parents[5]
PARENT = HERE.parent
BASE = PARENT / 'run-44416629057'
CANDIDATE = PARENT / 'run-44416629057-r1'
PRIOR = PARENT / 'run-44416629057-review-w14'
TASK = ADMISSION = 'f74025e493a627962842e8f7bc6a2766d33dd300'
BASE_COMMIT = 'd29ab46dbbb45d7106fa30c3ac04bb419a2ac286'
PRIOR_COMMIT = 'a9fe0055aab3279e3f5bb71bde9667925da80e65'
CANDIDATE_COMMIT = '31c1dbfc7ca2df34b28bb5eb7ee81bc207ee5642'
POSITIVE = ('s3_swap_u8_geometry', 's3_sort4_u8_separate',
            's3_sort4_u8_same_alloc', 's3_merge8_u8_separate')
checks, bindings, adverse, inherited = [], [], [], []


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_bytes())


def need(condition, label):
    assert condition, label
    checks.append(label)


def meta(data):
    return {'sha256': sha(data), 'bytes': len(data)}


def committed(directory, commit):
    relative = str(directory.relative_to(G0))
    names = subprocess.check_output(
        ['git', '-C', str(G0), 'ls-tree', '-r', '--name-only', commit, '--', relative]
    ).decode().splitlines()
    need(bool(names), 'nonempty exact committed input ' + relative)
    need(set(names) == {str(p.relative_to(G0)) for p in directory.rglob('*') if p.is_file()},
         'exact file set ' + relative)
    for name in names:
        data = (G0 / name).read_bytes()
        frozen = subprocess.check_output(['git', '-C', str(G0), 'show', commit + ':' + name])
        need(data == frozen, 'exact committed bytes ' + name)
        bindings.append({'commit': commit, 'path': name, **meta(data)})


def canon(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'), sort_keys=True).encode()


def same_projection(before, after, label):
    need(canon(before) == canon(after), label)
    inherited.append({'projection': label, 'canonical_sha256': sha(canon(before)),
                      'comparison': 'equal canonical bytes; containing original files pinned separately'})


def differences(before, after, pointer=''):
    if type(before) is not type(after):
        return [pointer]
    if isinstance(before, dict):
        return [p for key in sorted(before.keys() | after.keys())
                for p in ([pointer + '/' + key] if key not in before or key not in after
                          else differences(before[key], after[key], pointer + '/' + key))]
    if isinstance(before, list):
        return [pointer] if len(before) != len(after) else [
            p for i, (a, b) in enumerate(zip(before, after))
            for p in differences(a, b, pointer + '/' + str(i))]
    return [] if before == after else [pointer]


def reject(records, expected, root, mutation, validator):
    before = canon(expected)
    try:
        validator(records, expected)
    except (AssertionError, KeyError, TypeError):
        adverse.append({'root': root, 'mutation': mutation, 'result': 'REJECT',
                        'baseline_sha256': sha(before),
                        'provenance': 'deep copy of unchanged NATIVE.json guard array; memory only'})
    else:
        raise AssertionError('adverse reporting case accepted: ' + root + ' ' + mutation)
    need(canon(expected) == before, root + ' adverse baseline preserved: ' + mutation)


def main():
    # Hash/binding inheritance only: no decompression, raw/native replay or source audit.
    for directory, commit in ((BASE, BASE_COMMIT), (PRIOR, PRIOR_COMMIT),
                              (CANDIDATE, CANDIDATE_COMMIT)):
        committed(directory, commit)
    task_path = G0 / 'research/challenge-8/kani-k1/TASK-CH8-S3-R2-REPORT-DELTA-W14.md'
    need(task_path.read_bytes() == subprocess.check_output(
        ['git', '-C', str(G0), 'show', TASK + ':' + str(task_path.relative_to(G0))]),
        'exact f740 task bytes; owner /new14 overrides prepared reuse')
    bindings.append({'commit': TASK, 'path': str(task_path.relative_to(G0)), **meta(task_path.read_bytes())})
    manifest = load(CANDIDATE / 'MANIFEST.json')
    hashes = dict((name, digest) for digest, name in
                  (line.split('  ', 1) for line in (CANDIDATE / 'MANIFEST.sha256').read_text().splitlines()))
    need(set(manifest['files']) == set(hashes), 'candidate two manifest file sets agree')
    for name, record in manifest['files'].items():
        need(meta((CANDIDATE / name).read_bytes()) == record and hashes[name] == record['sha256'],
             'candidate manifest SHA256/length ' + name)
    change_map = load(CANDIDATE / 'CHANGE-MAP.json')
    need(set(change_map['files']) == set(manifest['files']) - {'CHANGE-MAP.json'}, 'complete change map')
    for name, entry in change_map['files'].items():
        before = meta((BASE / name).read_bytes()) if (BASE / name).is_file() else None
        after = meta((CANDIDATE / name).read_bytes())
        need(entry['before'] == before and entry['after'] == after, 'change map bindings ' + name)
        expected = 'ADDED' if before is None else 'UNCHANGED' if before == after else 'CHANGED'
        need(entry['disposition'] == expected, 'change map disposition ' + name)
        if expected == 'UNCHANGED':
            need((BASE / name).read_bytes() == (CANDIDATE / name).read_bytes(), 'inherited bytes ' + name)
            inherited.append({'file': name, **after, 'comparison': 'exact original file bytes'})

    old, new = load(BASE / 'QUALIFICATION.json'), load(CANDIDATE / 'QUALIFICATION.json')
    old_inv, new_inv = load(BASE / 'INVENTORY.json'), load(CANDIDATE / 'INVENTORY.json')
    native = load(CANDIDATE / 'NATIVE.json')
    findings = load(PRIOR / 'FINDINGS.json')
    need(findings['disposition'] == 'REQUEST_CHANGES' and
         [f['id'] for f in findings['findings']] == ['W14-01', 'W14-02'], 'exact two prior blockers')
    # Reuse only the two pure reporting helpers, never imports/main or evidence readers.
    tree = ast.parse((CANDIDATE / 'replay.py').read_text())
    helpers = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ('domain', 'validate_guards')]
    need(len(helpers) == 2, 'isolated reporting helper set')
    ns = {}
    exec(compile(ast.Module(body=helpers, type_ignores=[]), '<candidate reporting helpers>', 'exec'), ns)
    domain, validator = ns['domain'], ns['validate_guards']
    rows = {r['id']: r for r in new['rows']}
    fixture = rows['sort13_weak']['bindings']['negative_fixture']
    need(fixture['fixture'] == list(range(12, -1, -1)) and fixture['fixture_line'] == 147 and
         fixture['ordinary_stub'] == 's2_swap_seam -> weak_swap' and
         fixture['commit'] == '513341f41ce53833a279571401c924bdddddb6c8' and
         fixture['sha256'] == rows['sort13_weak']['bindings']['source_binding']['sha256'] and
         fixture['caller_line'] == 148 and fixture['literal_failure_line'] == 149 and
         fixture['stub_attribute_line'] == 144, 'W14-01 fixed source/seam binding matches inherited finding')
    need(domain('sort13_weak') == rows['sort13_weak']['bindings']['source_domain'] and
         '[12u8,11,10,9,8,7,6,5,4,3,2,1,0]' in domain('sort13_weak') and
         's2_swap_seam -> weak_swap' in domain('sort13_weak') and
         'arbitrary' not in domain('sort13_weak'), 'W14-01 helper and report domain agree')
    for r in new['rows']:
        if r['id'] != 'sort13_weak':
            need(domain(r['id']) == r['bindings']['source_domain'] ==
                 next(x for x in old['rows'] if x['id'] == r['id'])['bindings']['source_domain'],
                 r['id'] + ' unchanged domain and helper')

    prior_guards = {r['id']: r['unsupported_constructs'] for r in findings['findings'][1]['evidence']}
    for rid in POSITIVE:
        exact = native[rid]['harness']['unsupported_constructs']
        validator(exact, prior_guards[rid])
        need(len(exact) == 4 and all(x['status'] == 'SUCCESS' for x in exact), rid + ' four SUCCESS guards')
        for view in (rows[rid]['unsupported_constructs'],
                     next(x for x in new_inv['selected'] if x['id'] == rid)['unsupported_constructs'],
                     new['successful_unsupported_guard_inventory']['roots'][rid]):
            need(view == exact, rid + ' exact guard projection including order and trace_available')
        for status in ('FAILURE', 'FAILED', 'UNKNOWN', 'UNREACHABLE', 'UNDETERMINED', None, 0):
            bad = copy.deepcopy(exact); bad[0]['status'] = status
            reject(bad, exact, rid, 'status=' + repr(status), validator)
        for field in ('status', 'id', 'description', 'class', 'file', 'line', 'trace_available'):
            bad = copy.deepcopy(exact); del bad[0][field]
            reject(bad, exact, rid, 'missing ' + field, validator)
            bad = copy.deepcopy(exact); bad[0][field] = 'altered'
            reject(bad, exact, rid, 'altered ' + field, validator)
        for label, bad in [('empty', []), ('missing guard', copy.deepcopy(exact[:-1])),
                           ('null array', None), ('wrong array type', {}),
                           ('duplicate', [copy.deepcopy(exact[0])] * 4)]:
            reject(bad, exact, rid, label, validator)
    need(new['successful_unsupported_guard_inventory']['total'] == 16 and
         new['successful_unsupported_guard_inventory']['per_completed_positive'] == 4 and
         set(new['successful_unsupported_guard_inventory']['roots']) == set(POSITIVE), 'W14-02 exact four roots/16 total')

    # Only these reporting deltas may be removed to recover the complete original objects.
    q = copy.deepcopy(new)
    for key in ('successful_unsupported_guard_inventory', 'location_metadata_admission_reference', 'overall_qualification'):
        q.pop(key)
    q['decision_required'] = old['decision_required']
    for i, row in enumerate(q['rows']):
        if row['id'] in POSITIVE: row.pop('unsupported_constructs')
        if row['id'] == 's3_sort4_u8_same_alloc':
            for key in ('S1_assessment', 'admission'): row[key] = old['rows'][i][key]
        if row['id'] == 'sort13_weak':
            row['bindings'].pop('negative_fixture')
            row['bindings']['source_domain'] = old['rows'][i]['bindings']['source_domain']
    same_projection(old, q, 'qualification minus enumerated reporting corrections; all42 U/roles/covers/PFC/context/statuses')
    need(len(new['U_instances']) == 42, 'all42 U records retained')
    inv = copy.deepcopy(new_inv)
    for r in inv['selected']:
        if r['id'] in POSITIVE: r.pop('unsupported_constructs')
    same_projection(old_inv, inv, 'complete inventory minus four guard projections; protected epochs/namespace/provenance')
    for name, added in [('PROVENANCE.json', ('inherited_validation', 'reporting_correction')),
                        ('INPUTS.json', ('reporting_correction',)),
                        ('METADATA-GAP.json', ('location_metadata_admission_reference',))]:
        a, b = load(BASE / name), load(CANDIDATE / name)
        for key in added: b.pop(key)
        if name == 'METADATA-GAP.json': b['remaining'] = a['remaining']
        same_projection(a, b, name + ' inherited fields')
    need(all(r['strict_expected_match'] is False for r in new['rows']) and
         new['strict_policy'] == old['strict_policy'] and
         new['producer_policy_outcome'] == old['producer_policy_outcome'], 'strict0/9 and historical producer/policy unchanged')

    ref = load(CANDIDATE / 'ADMISSION-REFERENCE.json')
    admission_path = G0 / ref['path']
    data = subprocess.check_output(['git', '-C', str(G0), 'show', ADMISSION + ':' + ref['path']])
    need(ref['commit'] == ADMISSION and data == admission_path.read_bytes() and
         sha(data) == ref['sha256'] and json.loads(data) == ref['decision'], 'full exact f740 admission binding')
    bindings.append({'commit': ADMISSION, 'path': ref['path'], **meta(data)})
    decision = ref['decision']; prop = decision['exact_property']
    need(prop['file'] is None and prop['line'] is None and
         decision['status'] == 'ADMITTED_EXACT_LOCATION_METADATA_GATE_ONLY' and
         decision['originating_positive_source_coordinate'] == 'UNKNOWN' and
         decision['applied_to_runtime_reader_or_request'] is False and
         decision['counts']['SUCCESS'] == 351 and decision['counts']['UNREACHABLE'] == 5 and
         decision['counts']['covers'] == 7 and decision['counts']['missing_location_records'] == 1 and
         len(decision['constraints']) == 8, 'location-only gate retains nulls/counts/protected constraints and origin UNKNOWN')

    # Execute only the renderer prefix producing QUALIFICATION.md, with in-memory output.
    renderer = ast.parse((CANDIDATE / 'render.py').read_text())
    start = next(i for i, n in enumerate(renderer.body) if isinstance(n, ast.Assign) and
                 any(isinstance(t, ast.Name) and t.id == 'q' for t in n.targets))
    end = next(i for i, n in enumerate(renderer.body) if isinstance(n, ast.Assign) and
               any(isinstance(t, ast.Name) and t.id == 'ct' for t in n.targets))
    outputs = {}
    env = {'read': lambda name: load(CANDIDATE / name),
           'text': lambda name, value: outputs.update({name: value.rstrip() + '\n'})}
    exec(compile(ast.Module(body=renderer.body[start:end], type_ignores=[]), '<qualification renderer only>', 'exec'), env)
    need(set(outputs) == {'QUALIFICATION.md'} and outputs['QUALIFICATION.md'].encode() ==
         (CANDIDATE / 'QUALIFICATION.md').read_bytes(), 'qualification renderer reproduces committed report in memory')
    prose = outputs['QUALIFICATION.md']
    need('four SUCCESS' in prose and 'sixteen total' in prose and
         'unsupported_constructs arrays are empty' not in prose and
         '13 arbitrary independent full bytes' not in prose and
         '[12u8,11,10,9,8,7,6,5,4,3,2,1,0]' in prose, 'both corrected prose assertions match exact bindings')
    for rid in POSITIVE:
        for guard in prior_guards[rid]:
            need('| ' + rid + ' | ' + guard['id'] + ' | ' in prose, rid + ' rendered native guard ' + guard['id'])
    for name in ('RESULT.md', 'HANDOFF.md'):
        text = (CANDIDATE / name).read_text()
        need('[12u8,11,10,9,8,7,6,5,4,3,2,1,0]' in text and 'sixteen total' in text and
             '13 arbitrary independent full bytes' not in text and 'UNKNOWN' in text, name + ' corrected scope/guard consistency')
    # Persist compact reproducible review evidence, never mutate inputs.
    (HERE / 'EXACT-INPUTS.json').write_text(json.dumps({
        'task_commit': TASK, 'candidate_commit': CANDIDATE_COMMIT, 'base_commit': BASE_COMMIT,
        'prior_review_commit': PRIOR_COMMIT, 'admission_commit': ADMISSION,
        'settings': 'high/FastOFF/no subagents',
        'owner_override': '03:27 explicit /new14 overrides prepared reuse',
        'files': bindings}, indent=2) + '\n')
    (HERE / 'VALIDATION.json').write_text(json.dumps({
        'status': 'PASS', 'scope': 'short reporting delta and exact-byte inheritance only',
        'checks_count': len(checks), 'checks': checks, 'adverse_cases': adverse,
        'adverse_cases_count': len(adverse), 'inherited': inherited,
        'changed_json_pointers': {name: differences(load(BASE / name), load(CANDIDATE / name))
                                  for name in ('QUALIFICATION.json', 'INVENTORY.json', 'PROVENANCE.json', 'INPUTS.json', 'METADATA-GAP.json', 'RESULT.json')},
        'prior_broad_1501_checks': 'INHERITED_NOT_RERUN',
        'author_160_checks': 'SOURCE_REPORTED; reviewer tests recorded separately here',
        'strict_predicate': 'UNCHANGED; prior audit and author isolated predicate test inherited, not rerun',
        'native_executed': False, 'full_audit_executed': False, 'source_audit_executed': False,
        'policy_reader_executed_or_modified': False, 'CI_executed': False,
        'artifact_decompressed_or_reacquired': False,
        'proof_credit': 'NONE'}, indent=2) + '\n')
    print(json.dumps({'status': 'PASS', 'checks': len(checks), 'adverse': len(adverse),
                      'bindings': len(bindings), 'W14-01': 'CLOSED', 'W14-02': 'CLOSED'}))


if __name__ == '__main__':
    main()
