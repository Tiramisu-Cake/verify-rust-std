#!/usr/bin/env python3
"""W14 exact delta checks and independent temporary Rust-text mutations only."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.with_name('batch-r1')
G = HERE.parents[5]
S = Path('/root/verify-rust-std-ch8-s2-cfg-r1-w13')
C = Path('/root/kani-ch8-s2-cfg-r1-w13')
sys.path.insert(0, str(C / 'ch8-s1-control'))
import cfg_pfc
import check_package
import runner
import yaml

PKG = '0a4cef493f858d0e91d3ebccfbbab0b8d32d0119'
TASK = '7b829344c9cdd8c25ec59294bb9015201638a879'
OLD_S = '97ac4d39d7f959ea70b1f57785ffd1fd66ecd22a'
OLD_C = 'fc058c97335e4a064c7827b8534b3af2f7460bc3'
OLD_REVIEW = '0468ccf26c879a03ca83b1d5955be5e860c2b442'
BATCH = 'library/core/src/slice/sort/shared/smallsort/verify/sorting_s2_batch.rs'
HELPER = 'library/core/src/slice/sort/shared/smallsort/verify/helper_contracts.rs'
VERIFY = 'library/core/src/slice/sort/shared/smallsort/verify.rs'
PFC = '#[kani::proof_for_contract(sort8_stable)]'


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])


def sha(data):
    return hashlib.sha256(data).hexdigest()


def leaves(a, b, path=''):
    if isinstance(a, dict) and isinstance(b, dict):
        return [x for key in sorted(set(a) | set(b)) for x in
                (leaves(a[key], b[key], path + '/' + key) if key in a and key in b
                 else [{'path': path + '/' + key, 'before': a.get(key), 'after': b.get(key)}])]
    if isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        return [x for i, (v, w) in enumerate(zip(a, b)) for x in leaves(v, w, path + '/' + str(i))]
    return [] if a == b else [{'path': path, 'before': a, 'after': b}]


def main():
    ids = json.loads((PACKAGE / 'IDENTITIES.json').read_text())
    git(G, 'merge-base', '--is-ancestor', PKG, 'HEAD')
    pkgrel = PACKAGE.relative_to(G).as_posix()
    names = git(G, 'ls-tree', '-r', '--name-only', PKG, '--', pkgrel).decode().splitlines()
    assert len(names) == 28
    committed = [{'path': name, 'sha256': sha(git(G, 'show', PKG + ':' + name))} for name in names]
    assert all((G / x['path']).read_bytes() == git(G, 'show', PKG + ':' + x['path']) for x in committed)
    identities = {}
    for label, repo in [('source', S), ('control', C)]:
        actual = git(repo, 'rev-parse', 'HEAD', 'HEAD^{tree}', 'HEAD^').decode().splitlines()
        assert actual == [ids[label]['sha'], ids[label]['tree'], ids[label]['parent']]
        assert not git(repo, 'status', '--porcelain')
        identities[label] = dict(zip(['sha', 'tree', 'parent'], actual))
    request = runner.load_request()
    assert sha((PACKAGE / 'CI-REQUEST.json').read_bytes()) == '779126ddc8aa3e5cabd9b9968f0e1cd853c4e1b60a95a21ff4eb42d5a0c7ca74'
    source_paths = git(S, 'diff', '--name-only', OLD_S, ids['source']['sha']).decode().splitlines()
    assert source_paths == [BATCH]
    old = git(S, 'show', OLD_S + ':' + BATCH)
    current = (S / BATCH).read_bytes()
    assert current.startswith(old) and len(current[len(old):].splitlines()) == 13
    source_delta = {'paths': source_paths, 'numstat': git(S, 'diff', '--numstat', OLD_S, ids['source']['sha']).decode().strip(),
                    'unchanged_prefix_sha256': sha(old), 'appended_text': current[len(old):].decode()}
    def tree_entries(commit):
        return {entry.split('\t', 1)[1]: entry.split('\t', 1)[0]
                for entry in git(C, 'ls-tree', '-r', commit).decode().splitlines()}
    before_entries = tree_entries(OLD_C)
    after_entries = tree_entries(ids['control']['sha'])
    before_paths, after_paths = set(before_entries), set(after_entries)
    changed = set(git(C, 'diff', '--name-only', OLD_C, ids['control']['sha']).decode().splitlines())
    assert len(changed) == 10
    unchanged = sorted((before_paths & after_paths) - changed)
    assert all(before_entries[p] == after_entries[p] for p in unchanged)
    control_delta = {'changed_paths': sorted(changed), 'unchanged_tracked_files': len(unchanged),
                     'unchanged_control_payload': [p for p in unchanged if p.startswith('ch8-s1-control/')]}
    oldreq = json.loads(git(C, 'show', OLD_C + ':ch8-s1-control/CI-REQUEST.json'))
    reqdiff = leaves(oldreq, request)
    rowdiff = leaves(oldreq['rows'], request['rows'])
    assert len(rowdiff) == 6 and all(x['path'].endswith('/oracle/source_sha256') for x in rowdiff)
    assert oldreq['flags'] == request['flags'] and oldreq['execution_groups'] == request['execution_groups']
    assert oldreq['budgets'] == {**request['budgets'], 'planned_rows_seconds': 21000, 'projected_group_count': 14}
    for rel in ('batch', 'review-batch', 'go', 'postrun'):
        path = HERE.with_name(rel).relative_to(G).as_posix()
        assert not git(G, 'diff', TASK, PKG, '--', path)
    old_review_path = HERE.with_name('review-batch').relative_to(G).as_posix()
    assert not git(G, 'diff', OLD_REVIEW, PKG, '--', old_review_path)

    baseline = cfg_pfc.check(S, request)
    assert baseline == json.loads((PACKAGE / 'CFG-PFC-MAP.json').read_text())
    assert len(baseline['rows']) == 11
    assert sum(len(r['stub_verified']) for r in baseline['rows']) == 6
    assert baseline['qualification_from_registration'] is False and baseline['compilation'] == 'NOT_RUN'
    assert 'sort8_registration_only' not in [r['id'] for r in request['rows']]
    rows = [{**r, 'required_covers': request['rows'][i]['required_cover_count'],
             'expected': request['rows'][i]['expected']} for i, r in enumerate(baseline['rows'])]
    assert sum(r['required_covers'] for r in rows) == 20
    assert sum(r['expected'] == 'DETECTED' for r in rows) == 6

    # Independent text fixtures start from exact pinned source blobs, not the
    # author's S2-SOURCE fixture. Reseal hashes after every semantic mutation.
    files = {rel: (S / rel).read_bytes() for rel in baseline['source_files_sha256']}
    mutations = []
    def trial(name, replacements, expected, message=None):
        with tempfile.TemporaryDirectory(prefix='w14-cfg-') as tmp:
            root = Path(tmp)
            mutated = dict(files)
            for rel, oldtext, newtext in replacements:
                if oldtext is None:
                    mutated[rel] = newtext
                else:
                    text = mutated[rel].decode()
                    assert oldtext in text, (name, oldtext)
                    mutated[rel] = text.replace(oldtext, newtext).encode()
            for rel, data in mutated.items():
                path = root / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
            req = copy.deepcopy(request)
            req['cfg_pfc_source_sha256'] = {rel: sha(data) for rel, data in mutated.items()}
            try:
                result = cfg_pfc.check(root, req)
            except cfg_pfc.GateError as exc:
                actual, detail = 'REJECT', str(exc)
            else:
                actual, detail = 'ACCEPT', result['status']
            assert actual == expected, (name, actual, detail)
            assert message is None or message in detail, (name, detail)
            mutations.append({'name': name, 'expected': expected, 'actual': actual,
                              'diagnostic': detail, 'source_hashes_resealed': True})

    trial('old97ac_exact_observed_missing_sort8_class', [(BATCH, None, old)], 'REJECT', 'sort8_stable) has no active matching')
    trial('delete_sort8_registration', [(BATCH, PFC, '#[kani::proof]')], 'REJECT', 'sort8_stable) has no active matching')
    trial('inactive_sort8_pfc_not_assumed_cfg', [(BATCH, PFC, '#[cfg(not(kani_smallsort_s2_assumed))]\n' + PFC)], 'REJECT', 'no active matching')
    trial('inactive_nested_cfg_attr_pfc', [(BATCH, PFC, '#[cfg_attr(all(kani,not(any(kani_smallsort_controls,kani_smallsort_s2_assumed))),kani::proof_for_contract(sort8_stable))]')], 'REJECT', 'no active matching')
    trial('cfg_attr_disables_pfc_function', [(BATCH, PFC, '#[cfg_attr(all(kani,kani_smallsort_controls),cfg(not(kani_smallsort_sorting)))]\n' + PFC)], 'REJECT', 'no active matching')
    trial('foreign_existing_same_basename_via_module_alias', [
        (HELPER, None, files[HELPER] + b'\n#[kani::ensures(|_| true)]\npub(super) fn sort8_stable() {}\n'),
        (BATCH, PFC, 'use super::helper_contracts as foreign;\n#[kani::proof_for_contract(foreign::sort8_stable)]')], 'REJECT', 'no active matching')
    trial('foreign_target_on_stub_with_correct_pfc_remaining', [(BATCH, '#[kani::stub_verified(sort8_stable)]', '#[kani::stub_verified(super::helper_contracts::sort8_stable)]')], 'REJECT', 'unresolved/foreign stub target')
    trial('inactive_target_function', [('library/core/src/slice/sort/shared/smallsort.rs', 'unsafe fn sort8_stable<', '#[cfg(not(kani_smallsort_s2_assumed))]\nunsafe fn sort8_stable<')], 'REJECT', 'unresolved/foreign stub target')
    trial('inactive_manifest_root', [(BATCH, 'fn general32_weak()', '#[cfg(not(kani_smallsort_controls))]\nfn general32_weak()')], 'REJECT', 'manifest root inactive/missing')
    trial('inactive_provider_module', [(VERIFY, 'mod helper_contracts;', '#[cfg(not(kani_smallsort_controls))]\nmod helper_contracts;')], 'REJECT', 'inactive module')
    trial('unknown_cfg_fails_closed', [(BATCH, PFC, '#[cfg(target_os = "linux")]\n' + PFC)], 'REJECT', 'unknown cfg')
    trial('glob_import_fails_closed', [(BATCH, PFC, 'use super::super::*;\n' + PFC)], 'REJECT', 'unsupported glob')
    trial('nested_active_cfg_attr_and_explicit_alias_match', [
        (BATCH, PFC, 'use crate::slice::sort::shared::smallsort::sort8_stable as target8;\n#[cfg_attr(all(kani,any(kani_smallsort_s2_assumed,not(kani_smallsort_controls))),crate::kani::proof_for_contract(target8))]')], 'ACCEPT')
    trial('ordinary_stub_needs_no_registration', [
        (BATCH, '#[kani::stub_verified(sort8_stable)]', '#[kani::stub(sort8_stable,unused_replacement)]'),
        (BATCH, PFC, '#[kani::proof]')], 'ACCEPT')
    # The last fixture tests registration requirements only; its replacement is
    # deliberately not compiled or offered as a semantic positive summary.

    workflow = check_package.load_yaml((C / '.github/workflows/ch8-s2.yml').read_text())
    workflow_mutations = []
    with tempfile.TemporaryDirectory(prefix='w14-yaml-') as tmp:
        for name, mutate in [
            ('preflight_after_build', lambda steps: steps.insert(steps.index(next(s for s in steps if s['name'] == 'Build exact stock tool once')) + 1,
                steps.pop(steps.index(next(s for s in steps if s['name'] == 'Check all source identities'))))),
            ('preflight_skipped', lambda steps: next(s for s in steps if s['name'] == 'Check all source identities').update({'if': '${{ false }}'})),
            ('preflight_failure_ignored', lambda steps: next(s for s in steps if s['name'] == 'Check all source identities').update({'continue-on-error': True})),
            ('cfg_tests_removed', lambda steps: next(s for s in steps if s['name'] == 'Validate control and synthetic wrapper').update({'run': 'python3 -m unittest test_runner.py'})),
        ]:
            doc = copy.deepcopy(workflow)
            mutate(doc['jobs']['s2_batch']['steps'])
            path = Path(tmp) / 'fixture.yml'
            path.write_text(yaml.safe_dump(doc))
            try:
                check_package.check_yaml(path)
            except AssertionError:
                workflow_mutations.append({'name': name, 'actual': 'REJECT'})
            else:
                raise AssertionError(name + ' accepted')

    return {'schema': 'ch8-s2-w14-r1-independent-checks-v1', 'status': 'PASS',
            'candidate_package': PKG, 'committed_package_files': committed, 'identities': identities,
            'source_delta': source_delta, 'control_delta': control_delta, 'request_leaf_delta': reqdiff,
            'all_11_cfg_contexts': rows, 'all_active_provider_slice_uses': baseline['checked_active_slice_uses'],
            'mutations': mutations, 'workflow_mutations': workflow_mutations,
            'immutable_old_package_review_go_postrun': 'UNCHANGED',
            'proof_credit': 'NONE', 'compilation_verification_ci': 'NOT_RUN'}


if __name__ == '__main__':
    print(json.dumps(main(), indent=2) + '\n', end='')
