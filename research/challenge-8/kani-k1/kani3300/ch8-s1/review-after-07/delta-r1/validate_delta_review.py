#!/usr/bin/env python3
"""Independent W14 delta checks: exact structured replay, gates and oracle fix.

Does not re-run U/PFC audits or open evidence archives. Composer CLI load() would
re-read archive payloads and rerun all upstream replays, so its pure composition
and semantic mutations are exercised with independently pinned structured inputs.
Only this directory's VALIDATION.json is written.
"""
import collections
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
G0 = HERE.parents[6]
S1 = HERE.parent.parent
RUN = S1/'s1-07/run-43923266772'
COMPOSER = '0a97c61cce9f6fca1acc9ab35509e314012b7bfa'
PACKAGE = 'd5dcb0fa5db210116101f440048a4f1fae7c2d20'
SOURCE = '99e8456d200fff1299ee5756279cddb23921dc65'
FIX = '7c41333f9bfcfd7eb4e0ede7bd316443090c9025'
OLD = '9ccd882ef2460fbc97400594e7e3dfc884a4a997'
PARENT = '9208b373c0a08a265fa0d7493a6529e331065271'
STD = Path('/root/verify-rust-std-ch8-s1-08-w13')
CTL = Path('/root/kani-ch8-s1-08-fix-w13')


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])


def blob(repo, commit, path):
    return git(repo, 'show', commit+':'+path)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def pin_directory(path, commit):
    rel = str(path.relative_to(G0))
    names = git(G0, 'ls-tree', '-r', '--name-only', commit, rel).decode().splitlines()
    out = {}
    for name in names:
        data = blob(G0, commit, name)
        assert (G0/name).read_bytes() == data, name
        out[name] = sha(data)
    return out


def composer_check():
    files = pin_directory(RUN/'accept-v3', COMPOSER)
    module = mod('replay', RUN/'accept-v3/replay.py')
    manifest = read(RUN/'accept-v3/INPUTS.json')
    assert sha((RUN/'accept-v3/INPUTS.json').read_bytes()) == module.MANIFEST_SHA
    hashes, archive_references = {}, {}
    for rel, item in manifest['files'].items():
        if rel.endswith('.gz'):
            # Check immutable Git tree identity without opening archive contents.
            original = git(G0, 'ls-tree', item['commit'], '--', rel)
            current = git(G0, 'ls-tree', 'HEAD', '--', rel)
            assert original == current and original
            archive_references[rel] = original.decode().strip()
            continue
        data = blob(G0, item['commit'], rel)
        assert (G0/rel).read_bytes() == data and sha(data) == item['sha256'], rel
        hashes[rel] = sha(data)
    args = tuple(read(RUN/rel) for rel in ('CI-REQUEST.json', 'accept/ACCEPT.json',
                                          'accept-u/U.json', 'accept-pfc/PFC.json', 'accept-u/INPUTS.json'))
    report = module.compose(*args)
    data = module.encoded(report)
    assert data == (RUN/'accept-v3/ACCEPT.json').read_bytes()
    assert data == module.encoded(module.compose(*args))
    # Independent gate derivation, starting from the unchanged exact receipt.
    req, baseline, u, pfc, _ = args
    specs = {r['id']: r for r in req['rows']}
    oldrows = {r['id']: r for r in baseline['rows']}
    rows = {r['id']: r for r in report['rows']}
    ukeys = {(r['row_id'], r['property_id']) for r in u['records']}
    original_unknown = {(r['row_id'], r['property_id']) for r in baseline['unreachable_analysis']['records']
                        if r['decision'].startswith('UNKNOWN')}
    assert ukeys == original_unknown and len(ukeys) == 187
    pkeys = {r['id'] for r in pfc['bindings']}
    assert pkeys == {r['id'] for r in req['rows'] if r['mode'] == 'PFC'}
    local = {}
    for rid, old in oldrows.items():
        gates = set(old['pending_gates']) - {module.CG}
        # Both previously reviewed components are complete on these exact pins.
        gates.discard(module.UG)
        if rid in pkeys:
            gates.discard(module.PG)
        if any(s['binding'] not in module.EXACT_SUCCESS for s in old['required_success']):
            gates.add(module.SG)
        if any(c['binding'] != 'EXACT_SAT_COVER_SEMANTIC' for c in old['required_covers']):
            gates.add('REQUIRED_COVER_SEMANTIC_BINDING')
        local[rid] = gates
        assert rows[rid]['local_pending_gates'] == sorted(gates)
        for field in ('required_success', 'required_covers', 'negative_oracle', 'inventory',
                      'locations', 'binary_after', 'source_reported_verdict', 'same_run_companion'):
            assert rows[rid].get(field) == old.get(field), (rid, field)
    memo = {}
    def qualified(rid, stack=()):
        if rid in memo:
            return memo[rid]
        if rid not in local or local[rid] or rid in stack:
            return False
        cid = specs[rid].get('companion')
        result = not cid or qualified(cid, stack+(rid,))
        memo[rid] = result
        return result
    independent = {rid for rid in rows if qualified(rid)}
    assert independent == {rid for rid, r in rows.items() if r['qualification'] == 'QUALIFIED'}
    for rid, row in rows.items():
        gates = set(local[rid])
        cid = specs[rid].get('companion')
        if cid and cid not in independent:
            gates.add(module.CG)
        assert row['pending_gates'] == sorted(gates)
    assert report['qualified_acceptance'] == 'PENDING'
    assert all(u['qualification'] == 'PENDING' for u in report['replacement_unions'])
    success = [s for r in report['rows'] for s in r['required_success']]
    assert sum(s['binding'] not in module.EXACT_SUCCESS for s in success) == 111
    assert len(success) == 127
    for field in ('groups', 'location_exceptions', 'unsupported_records', 'native_analysis',
                  'semantic_binding_gaps', 'cover_source_case_audit', 'producer_source'):
        assert report[field] == baseline[field], field
    for row in report['rows']:
        for ref in row['component_consumption']['U']:
            item = u['records'][int(ref['pointer'].split('/')[-1])]
            assert item['row_id'] == row['id'] and item['property_id'] == ref['property_id']
            assert sha(module.encoded(item)) == ref['record_sha256']
        ref = row['component_consumption']['PFC']
        if ref:
            item = pfc['bindings'][int(ref['pointer'].split('/')[-1])]
            assert item['id'] == row['id'] and sha(module.encoded(item)) == ref['record_sha256']
    # Reuse only the new composer's bounded semantic mutations. Upstream audits
    # and archive-reading load() are deliberately not repeated.
    saved_load = module.load
    module.load = lambda: copy.deepcopy(args)
    try:
        tests = mod('composer_review_mutations', RUN/'accept-v3/test_replay.py')
        suite = unittest.defaultTestLoader.loadTestsFromModule(tests)
        result = unittest.TextTestRunner(verbosity=1).run(suite)
        assert result.wasSuccessful()
    finally:
        module.load = saved_load
    return {'commit': COMPOSER, 'files': files, 'structured_dependency_sha256': hashes,
            'archive_reference_Git_identity_only_NO_CONTENT_READ': archive_references,
            'structured_semantic_replay': 'EXACT_BYTE_MATCH_TWICE', 'ACCEPT_sha256': sha(data),
            'independently_qualified_rows': sorted(independent), 'totals': report['totals'],
            'semantic_mutation_tests': result.testsRun, 'mutation_failures': len(result.failures),
            'mutation_errors': len(result.errors),
            'upstream_U_PFC_full_audits_and_archive_reading_CLI_load': 'NOT_REPEATED'}


def repair_check():
    package = S1/'s1-08-r1'
    pins = pin_directory(package, PACKAGE)
    # Old candidate and reviewed components must remain immutable.
    immutable = {}
    for path, commit in [(S1/'s1-08', '8ea1c1d370f4076eb6ed4aeaa0a96898499ce580'),
                         (RUN/'accept-u', '16e36c4a2c244bb23ae71c80e5aa6db5f95e5338'),
                         (RUN/'accept-pfc', '013f288ca5111c0587e087567d2ec4182856be1d')]:
        immutable[str(path.relative_to(S1))] = pin_directory(path, commit)
    assert git(CTL, 'rev-list', '--parents', '-n', '1', FIX).decode().split() == [FIX, PARENT]
    assert git(CTL, 'rev-list', '--parents', '-n', '1', OLD).decode().split() == [OLD, PARENT]
    assert git(CTL, 'merge-base', OLD, FIX).decode().strip() == PARENT
    request_raw = blob(CTL, FIX, 'ch8-s1-control/CI-REQUEST.json')
    assert request_raw == (package/'EMBEDDED-CI-REQUEST.json').read_bytes()
    assert sha(request_raw) == '77ae11136368b592f044da3f881408c87453d9bf5f28c3fd1a5eb0fcc1431c7e'
    req = json.loads(request_raw)
    old = json.loads(blob(CTL, OLD, 'ch8-s1-control/CI-REQUEST.json'))
    changed = []
    for a, b in zip(old['rows'], req['rows'], strict=True):
        norm = copy.deepcopy(b)
        if a.get('oracle') and a['oracle']['property_id'] != b['oracle']['property_id']:
            changed.append(a['id'])
            norm['oracle']['property_id'] = a['oracle']['property_id']
        assert a == norm
    assert changed == ['activation_descending_rejected', 'activation_effectful_rejected']
    for key in old.keys() - {'schema', 'rows', 'ci_payload_sha256', 'ci_changed_paths'}:
        assert old[key] == req[key]
    for rel, expected in req['ci_payload_sha256'].items():
        committed = blob(CTL, FIX, rel)
        assert sha(committed) == expected and committed == (CTL/rel).read_bytes()
    for line in (package/'MANIFEST.sha256').read_text().splitlines():
        expected, name = line.split('  ', 1)
        assert sha((package/name).read_bytes()) == expected
    sys.path.insert(0, str(package))
    sys.path.insert(0, str(CTL/'ch8-s1-control'))
    s = mod('oracle_source', CTL/'ch8-s1-control/oracle_source.py')
    matcher = mod('negative_oracle', CTL/'ch8-s1-control/negative_oracle.py')
    model = 'library/core/src/slice/sort/shared/smallsort/verify/sorting_model_controls.rs'
    text = blob(STD, SOURCE, model).decode()
    cases = []
    for rid, line, col, endcol, stale in [('activation_descending_rejected', 95, 32, 48, 100),
                                        ('activation_effectful_rejected', 101, 21, 37, 106)]:
        # Independently take the exact closure declaration from the named root.
        start = text.index('fn '+rid+'() {')
        end = text.index('\n}', start)
        body = text[start:end]
        token = '|a: &u8, b: &u8|'
        assert body.count(token) == 1
        pos = text.index(token, start, end)
        actual_line = text.count('\n', 0, pos)+1
        actual_col = pos-text.rfind('\n', 0, pos)
        assert (actual_line, actual_col, actual_col+len(token)) == (line, col, endcol)
        row = next(r for r in req['rows'] if r['id'] == rid)
        oracle = row['oracle']
        assert f'.rs:{line}:{col}: {line}:{endcol}}}' in oracle['property_id']
        helper = blob(STD, SOURCE, model).decode().splitlines()[oracle['line']-1]
        assert helper == oracle['source_line'] and 'enabled::<T, F>()' in helper
        t = mod('repair_fixture_'+rid, CTL/'ch8-s1-control/test_s108r1.py')
        synthetic = t.harness(oracle)
        assert matcher.matches(synthetic, oracle)
        previous = next(r['oracle'] for r in old['rows'] if r['id'] == rid)
        assert not matcher.matches(synthetic, previous)
        assert not matcher.matches(t.harness(previous), oracle)
        assert s.closure_span(text, rid)['start_line'] == line
        cases.append({'root': rid, 'source_line': line, 'columns': [col, endcol],
                      'exact_declaration': token, 'fixed_exact_id': oracle['property_id'],
                      'new_synthetic_matches_fixed': True, 'stale_cross_match': False,
                      'compiler_observation': 'NOT_RUN'})
    # Return values only: do not execute the package scripts' __main__ writers.
    delta = mod('repair_delta_check', package/'validate_delta.py').check()
    artifacts = mod('repair_artifacts', package/'verify_artifacts.py').check()
    static = mod('repair_static', package/'verify_package.py').check(CTL, STD)
    return {'package_commit': PACKAGE, 'source': SOURCE, 'control': FIX, 'package_files': pins,
            'immutable_originals': immutable, 'repair_cases': cases,
            'original_to_fixed_changed_paths': git(CTL, 'diff', '--name-only', OLD, FIX).decode().splitlines(),
            'author_delta_check_replayed_read_only': delta,
            'three_patch_tree_reconstructions': artifacts,
            'static_package_preflight_replayed_read_only': static,
            'W14_S108_01': 'CLOSED_ON_FIXED_PINS_ONLY'}


if __name__ == '__main__':
    result = {'schema': 'w14-delta-r1-independent-validation-v1', 'composer': composer_check(),
              'repair': repair_check(), 'CI_push_ledger_compiler_full_runner': 'NOT_RUN',
              'new_independent_B1_B2_proof_credit': 'NONE'}
    (HERE/'VALIDATION.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'validation': 'PASS', 'closure_finding': result['repair']['W14_S108_01'],
                      'composer_replay': result['composer']['structured_semantic_replay']}))
