#!/usr/bin/env python3
"""W14 independent bounded review checks. No compiler, runner, CI or raw logs.

Reads exact Git objects and compact committed projections. Writes this review's
VALIDATION.json only. Predicted relocated IDs below are synthetic, not observed
S1-08 compiler output and not a proposed relaxation of the exact oracle.
"""
import collections
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
G0 = HERE.parents[5]
S1 = HERE.parent
RUN = S1 / 's1-07/run-43923266772'
STD = Path('/root/verify-rust-std-ch8-s1-08-w13')
CTL = Path('/root/kani-ch8-s1-08-w13')
OLDCTL = Path('/root/kani-ch8-s1-07-w13')
BASE = '5be85699b8826e3286c0bf89efb9affefac0acb5'
NEW = '99e8456d200fff1299ee5756279cddb23921dc65'
CONTROL = '9ccd882ef2460fbc97400594e7e3dfc884a4a997'
CPARENT = '9208b373c0a08a265fa0d7493a6529e331065271'
EXECUTED = 'b37f6f75c5b7b77e84297cd7104f9c0868502fd4'
TOOL = '0aac16ef62da9e9d5645782d458593e5d78143ba'
SMALL = 'library/core/src/slice/sort/shared/smallsort.rs'
PREFIX = 'library/core/src/slice/sort/shared/smallsort/verify/'
NAMESPACE = '/home/runner/work/kani/kani/export/'


def git(repo, *args, env=None):
    return subprocess.check_output(['git', '-C', str(repo), *args], env=env)


def blob(repo, sha, path):
    return git(repo, 'show', sha + ':' + path)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def identities():
    result = {}
    for rel, commit in [('s1-07/run-43923266772/accept-u', '16e36c4a2c244bb23ae71c80e5aa6db5f95e5338'),
                        ('s1-07/run-43923266772/accept-pfc', '013f288ca5111c0587e087567d2ec4182856be1d'),
                        ('s1-08', '8ea1c1d370f4076eb6ed4aeaa0a96898499ce580')]:
        root = S1 / rel
        names = git(G0, 'ls-tree', '-r', '--name-only', commit, str(root.relative_to(G0))).decode().splitlines()
        result[rel] = {'commit': commit, 'files': {}}
        for name in names:
            expected = blob(G0, commit, name)
            assert (G0 / name).read_bytes() == expected, name
            result[rel]['files'][name] = sha(expected)
    for repo, child, parent in [(STD, NEW, BASE), (CTL, CONTROL, CPARENT)]:
        assert git(repo, 'rev-list', '--parents', '-n', '1', child).decode().split() == [child, parent]
    chain = git(CTL, 'rev-list', '--max-count=5', CONTROL).decode().splitlines()
    assert chain[-1] == TOOL and len(chain) == 5
    assert git(CTL, 'rev-parse', CPARENT + '^{tree}') == git(OLDCTL, 'rev-parse', EXECUTED + '^{tree}')
    ids = read(S1/'s1-08/IDENTITIES.json')
    for repo, commit, group in [(STD, NEW, 'source'), (CTL, CONTROL, 'control'), (CTL, TOOL, 'tool')]:
        assert git(repo, 'rev-parse', commit + '^{tree}').decode().strip() == ids[group]['tree']
    return {'components': result, 'control_ancestry_depth_5': chain,
            'reviewed_parent_tree_equals_executed_s107': True}


def u_inventory():
    request = read(RUN/'CI-REQUEST.json')
    prior = read(RUN/'accept/ACCEPT.json')['unreachable_analysis']['records']
    reported = read(RUN/'accept-u/U.json')
    expected = {(r['group'], r['row_id'], r['selector'], r['property_id']) for r in prior
                if r['decision'].startswith('UNKNOWN')}
    actual = {(r['group'], r['row_id'], r['harness'], r['property_id']) for r in reported['records']}
    assert expected == actual and len(actual) == 187
    for group in request['execution_groups']:
        rich = read(RUN/'evidence'/group['id']/'properties.json')
        export = read(RUN/'evidence'/group['id']/'export.json')
        for h in rich['harnesses']:
            checks = {p['id'] for p in h['properties'] if p['status'] == 'UNREACHABLE' and p['class'] != 'cover'}
            historical = {p['property_id'] for p in prior if p['group'] == group['id'] and
                          p['selector'] == h['name'] and p['status_kind'] == 'check'}
            eh = next(x for x in export['harnesses'] if x['name'] == h['name'])
            assert checks == historical == set(eh['checks']['unreachable'])
    for a in reported['source_anchors'].values():
        repo = STD if a['repo'] == 'std' else CTL
        data = blob(repo, a['commit'], a['path']).decode()
        part = '\n'.join(data.splitlines()[a['start_line']-1:a['end_line']])
        assert sha(part.encode()) == a['sha256']
    # Independent state enumeration of index/counter induction, not data samples
    # claiming to prove arbitrary usize arithmetic or the sorting relation.
    transitions = 0
    for n in range(33):
        i = 1
        while i < n:
            assert 0 <= i-1 < i < n <= 32
            assert i+1 <= n
            i += 1
        for outer in range(n):
            assert 0 <= outer < n <= 32 and outer+1 <= n
        for j in range(n):
            for count in range(j+1):
                for inc in (0, 1):
                    assert 0 <= count+inc <= j+1 <= n <= 32
                    transitions += 1
    assert transitions == 11968
    # Shift overflow is a RHS-width check, NOT a check that no LHS bits are lost.
    assert all(1 <= width-1 for width in (8, 16, 32, 64))
    assert (((1 << 64)-1) << 1) & ((1 << 64)-1) == (1 << 64)-2
    assert all('sorting' not in r['operation'] for r in reported['records'])
    return {'same_run_unreachable_inventory': 'EXACT', 'reviewed_new_safety_records': len(actual),
            'families': dict(collections.Counter(r['rule'] for r in reported['records'])),
            'active_post_counter_induction_transitions': transitions,
            'sorting_relation_credit': 'NONE'}


def pfc_relations():
    report = read(RUN/'accept-pfc/PFC.json')
    request = read(RUN/'CI-REQUEST.json')
    allrows = {r['id']: r for r in request['rows'] if r['mode'] == 'PFC'}
    assert set(allrows) == {b['id'] for b in report['bindings']} and len(allrows) == 22
    symbols = sorted(report['demangling_dictionary'])
    decoded = subprocess.check_output(['c++filt', '-i', '-s', 'rust'], input='\n'.join(symbols)+'\n', text=True).splitlines()
    assert dict(zip(symbols, decoded)) == report['demangling_dictionary']
    results = []
    for b in report['bindings']:
        row = allrows[b['id']]
        group = b['group']
        rich = read(RUN/'evidence'/group/'properties.json')
        exp = read(RUN/'evidence'/group/'export.json')
        meta = read(RUN/'evidence'/group/'binding-metadata.json')
        h = next(x for x in exp['harnesses'] if x['name'] == row['selector'])
        ps = next(x['properties'] for x in rich['harnesses'] if x['name'] == row['selector'])
        c = b['contract']
        assert h['contract']['contracted_function_name'] == c['raw_symbol']
        assert report['demangling_dictionary'][c['raw_symbol']] == c['decoded_modifies_wrapper']
        assert h['contract']['recursion_tracker'] is None
        assert h['attributes']['stubs'] == h['attributes']['verified_stubs'] == []
        for e in c['ensures']:
            assert ps.count(e['property']) == 1
            assert re.sub(r'\s+', '', e['property']['description']) == re.sub(r'\s+', '', e['source_clause']['expression'])
            assert e['property']['status'] == ('FAILURE' if row['expected'] == 'DETECTED' else 'SUCCESS')
            assert e['property']['id'].rsplit('.assertion.', 1)[0].endswith('::'+c['check_wrapper'].split('::')[-1])
        for q in c['diagnostics']:
            assert ps.count(q) == 1 and q['status'] == 'SUCCESS'
            assert q['description'].count(c['raw_symbol']) == 2
        assert c['requires'] and all(q['assertion_ids'] == [] for q in c['requires'])
        assert all(ps.count(q) == 1 and q['status'] == 'SUCCESS' for q in c['modifies']['write_site_properties'])
        native = b['native']
        entry = next(x for x in meta['native_metadata'] if x['path'] == native['metadata_path'])
        assert sha(entry['text'].encode()) == entry['sha256'] == native['sha256']
        doc = json.loads(entry['text'])
        nh = doc
        for key in native['pointer'].split('/')[1:]:
            nh = nh[int(key)] if isinstance(nh, list) else nh[key]
        assert nh['pretty_name'] == row['selector'] and nh['contract'] == h['contract']
        assert nh['attributes'] == h['attributes']
        if row['expected'] == 'DETECTED':
            failed = [p for p in ps if p['status'] == 'FAILURE']
            assert len(failed) == 1 and failed[0]['id'] == row['oracle']['property_id']
        results.append({'id': b['id'], 'type': b['type'], 'trait': b['trait'],
                        'impl_header': b['selected_impl']['header'], 'ensures_line': c['ensures'][0]['source_clause']['line'],
                        'native_sha256': entry['sha256'], 'native_pointer': native['pointer']})
    for a in report['producer_semantics'].values():
        data = blob(CTL, TOOL, a['path'])
        assert sha(data) == a['sha256']
        assert data.decode().splitlines()[a['start_line']-1:a['end_line']] == a['lines']
    assert len({x['impl_header'] for x in results}) == 6
    return {'chains': results, 'producer_anchors_sha256_checked': len(report['producer_semantics']),
            'assurance': 'BOUNDED_SOURCE_REPORTED_PROFILES_V4_TRUST_PINNED_STOCK_COMPILER',
            'independent_AST_MIR_provenance': 'NOT_CLAIMED', 'proof_credit': 'NONE'}


# Independent token comparison. Whitespace is ignored outside literal/comment
# tokens; operands and every token outside the exact rewritten calls must agree.
ROLES = {'S1_ENTRY_MODEL_ENABLED': 'model_enabled', 'S1_MODEL_ENABLED': 'model_enabled',
         'S1_EXACT_TRAIT_THRESHOLD': 's1_exact_trait_threshold', 'S1_ENTRY_TYPE_LAYOUT': 'type_layout',
         'S1_ENTRY_POST_INDEPENDENT_CALLER': 'post_independent_caller',
         'S1_LEFT_CANARY': 'left_canary', 'S1_RIGHT_CANARY': 'right_canary',
         'S1_N1_VALUE_UNCHANGED': 'n1_value_unchanged', 'S1_N0_EMPTY_UNCHANGED': 'n0_empty_unchanged',
         'S1_IDENTITY_CHECKER': 'identity_checker', 'S1_CONSTRUCTED_SORTED_PERMUTATION': 'constructed_sorted_permutation',
         'S1_FNMUT_TWO_PROJECTIONS': 'fnmut_two_projections', 'S1_FNONCE_TWO_PROJECTIONS': 'fnonce_two_projections',
         'S1_ELEMENT_LAYOUT': 'element_layout', 'S1_COMPARATOR_ZST_ELEMENT_NO_DROP': 'comparator_zst_element_no_drop'}


def tokens(text):
    return re.findall(r'//[^\n]*|/\*.*?\*/|"(?:\\.|[^"\\])*"|::|\w+|[^\s]', text, re.S)


def canonical(text, new):
    ts = tokens(text)
    out, changed = [], []
    i = 0
    while i < len(ts):
        lead = ['kani', '::', 'assert', '('] if new else ['assert', '!', '(']
        if ts[i:i+len(lead)] != lead:
            out.append(ts[i]); i += 1; continue
        end = i+len(lead)
        depth = 1
        while depth:
            depth += (ts[end] == '(') - (ts[end] == ')')
            end += 1
        args = ts[i+len(lead):end-1]
        if new:
            # , concat ! ( stringify ! ( $ name ) , "::role" )
            marker = [',', 'concat', '!', '(', 'stringify', '!', '(', '$', 'name', ')', ',']
            split = next((j for j in range(len(args)) if args[j:j+11] == marker), None)
            if split is None:
                # The pre-existing S1_SCRATCH_PREFIX_VALID kani::assert is
                # unchanged and must compare verbatim, outside the rewrite.
                out.extend(ts[i:end]); i = end; continue
            assert len(args[split:]) == 13 and args[-1] == ')'
            role = json.loads(args[-2])[2:]
            assert json.loads(args[-2]).startswith('::') and role in ROLES.values()
            cond = args[:split]
        else:
            if len(args) < 2 or args[-2] != ',' or args[-1][0] != '"' or json.loads(args[-1]) not in ROLES:
                out.extend(ts[i:end]); i = end; continue
            role = ROLES[json.loads(args[-1])]
            cond = args[:-2]
        out.append(('CHECK', tuple(cond), role))
        changed.append({'role': role, 'operand_tokens': cond})
        i = end
    return out, changed


def s108():
    package = S1/'s1-08'
    request = read(package/'EMBEDDED-CI-REQUEST.json')
    manifest = read(package/'ROLE-MAP.json')
    manifest_files = []
    for line in (package/'MANIFEST.sha256').read_text().splitlines():
        digest, name = line.split('  ', 1)
        assert sha((package/name).read_bytes()) == digest, name
        manifest_files.append(name)
    producers = read(package/'PRODUCER-SOURCE.json')['files']
    for p in producers:
        repo = STD if p['revision'] == NEW else CTL
        assert sha(blob(repo, p['revision'], p['path'])) == p['sha256']
    changes = {}
    for filename, count in [('sorting_entry_smoke.rs', 16), ('sorting_model_controls.rs', 7)]:
        path = PREFIX + filename
        old = blob(STD, BASE, path).decode()
        new = blob(STD, NEW, path).decode()
        oc, ops = canonical(old, False)
        nc, nps = canonical(new, True)
        assert oc == nc and ops == nps and len(ops) == count
        changes[path] = {'calls': count, 'operand_and_order_tokens': 'EXACT',
                         'all_other_tokens_including_negatives_and_covers': 'EXACT'}
    assert sum(len(r['required_success_messages']) for r in request['rows']) == 127
    entries = manifest['required_success_bindings']
    assert [(e['row_id'], e['expected_message']) for e in entries] == [(r['id'], m) for r in request['rows'] for m in r['required_success_messages']]
    assert sum(e['binding_kind'] == 'EXACT_ROLE_LABEL' for e in entries) == 111
    assert sum(e['binding_kind'].startswith('EXACT_SUCCESS_SEMANTIC') for e in entries) == 16
    assert all(e['observed_s108_property_ids'] is None and e['observed_s108_status'] == 'NOT_RUN' for e in entries)
    # Read-only calls: these functions return reports; their __main__ writers
    # are deliberately not executed. They test identities, not admission.
    sys.path.insert(0, str(package))
    sys.path.insert(0, str(CTL/'ch8-s1-control'))
    package_check = module('review_package_check', package/'verify_package.py')
    artifact_check = module('review_artifact_check', package/'verify_artifacts.py')
    static = package_check.check(CTL, STD)
    artifacts = artifact_check.check()
    return {'independent_token_comparison': changes, 'author_static_check_replayed_read_only': static,
            'artifact_reconstruction_replayed_read_only': artifacts,
            'package_manifest_verified_files': manifest_files, 'producer_sha256_checked': producers,
            'required_bindings': 127, 'future_labels': 111, 'preserved_semantic_bindings': 16,
            'runtime_observations': 'NOT_RUN'}


def stale_oracle_reproducer():
    request = read(S1/'s1-08/EMBEDDED-CI-REQUEST.json')
    matcher = module('review_negative_matcher', CTL/'ch8-s1-control/negative_oracle.py')
    path = PREFIX+'sorting_model_controls.rs'
    old = blob(STD, BASE, path).decode().splitlines()
    new = blob(STD, NEW, path).decode().splitlines()
    results = []
    for rid, oldline, newline in [('activation_descending_rejected', 100, 95), ('activation_effectful_rejected', 106, 101)]:
        row = next(r for r in request['rows'] if r['id'] == rid)
        o = row['oracle']
        assert old[oldline-1] == new[newline-1] and '|' in new[newline-1]
        coords = re.search(r'\.rs:(\d+):(\d+): (\d+):(\d+)\}', o['property_id'])
        assert coords and int(coords[1]) == int(coords[3]) == oldline
        assert new[oldline-1] != old[oldline-1]
        predicted = o['property_id'].replace(f'.rs:{oldline}:{coords[2]}: {oldline}:{coords[4]}}}',
                                              f'.rs:{newline}:{coords[2]}: {newline}:{coords[4]}}}')
        h = {'name': row['selector'], 'outcome': {'kind': 'COMPLETED', 'verdict': 'FAILURE'},
             'n_failed': 1, 'n_properties': 1, 'checks': {'total': 1, 'success': 0, 'failure': [predicted],
                **{k: [] for k in ('undetermined', 'error', 'unknown', 'other', 'unreachable')}},
             'covers': {'total': 0, **{k: [] for k in ('satisfied', 'unsatisfiable', 'unreachable', 'undetermined', 'error', 'unknown', 'other')}},
             'unsupported_constructs': [], 'failed_properties': [{'id': predicted, 'file': o['export_file'],
                'line': str(o['line']), 'class': 'assertion', 'status': 'FAILURE'}]}
        refreshed = {**o, 'property_id': predicted}
        assert matcher.matches(h, o) is False and matcher.matches(h, refreshed) is True
        results.append({'row': rid, 'old_closure_line': oldline, 'new_closure_line': newline,
                        'exact_old_new_closure_text': new[newline-1], 'new_text_at_stale_line': new[oldline-1],
                        'committed_oracle_id': o['property_id'], 'synthetic_relocated_id': predicted,
                        'committed_oracle_matches_relocated_synthetic': False,
                        'refreshed_oracle_matches_same_synthetic': True})
    return {'finding': 'W14-S108-01', 'reproducer': 'STATIC_SOURCE_COORDINATES_AND_SYNTHETIC_MATCHER_ONLY',
            'compiler_observation': 'NOT_RUN', 'cases': results}


def main():
    result = {'schema': 'w14-independent-review-validation-v1', 'identities': identities(),
              'U': u_inventory(), 'PFC': pfc_relations(), 'S1_08': s108(),
              'finding_reproducer': stale_oracle_reproducer(),
              'compiler_rustfmt_full_runner_CI_push_ledger': 'NOT_RUN', 'independent_B1_B2_credit': 'NONE'}
    (HERE/'VALIDATION.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'validation': 'PASS', 'finding_reproduced': result['finding_reproducer']['finding'],
                      'U_records': 187, 'PFC_chains': 22, 'runtime': 'NOT_RUN'}))


if __name__ == '__main__':
    main()
