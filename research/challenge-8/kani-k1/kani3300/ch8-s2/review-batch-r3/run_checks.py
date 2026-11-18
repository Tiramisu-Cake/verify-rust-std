#!/usr/bin/env python3
"""W14 exact-object/static delta review. No compiler, runner execution or CI.

Run with PYTHONDONTWRITEBYTECODE=1. Author preflight output is redirected here;
author paths stay immutable. Only final candidate's new gate tests are executed.
"""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
PACK = HERE.parent / 'batch-r3'
G0 = HERE.parents[5]
REVIEWED = 'ba7286f5f77277aed531eaaab601e94396dec909'
ids = json.loads((PACK / 'IDENTITIES.json').read_text())
S = Path(ids['source']['worktree'])
C = Path(ids['control']['worktree'])
T = Path('/root/kani-upstream-ch8-s1')
Q = C / 'ch8-s1-control'


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(name):
    return json.loads((PACK / name).read_text())


def write(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2) + '\n')


def main():
    started = time.time()
    assert git(G0, 'rev-parse', 'HEAD').decode().strip() == REVIEWED
    relpack = str(PACK.relative_to(G0))
    files = git(G0, 'ls-tree', '-r', '--name-only', REVIEWED, relpack).decode().splitlines()
    assert len(files) == 45
    for rel in files:
        assert (G0 / rel).read_bytes() == git(G0, 'show', REVIEWED + ':' + rel)
    manifest = (PACK / 'MANIFEST.sha256').read_text().splitlines()
    assert len(manifest) == 44
    for line in manifest:
        digest, rel = line.split(maxsplit=1)
        assert sha((PACK / rel).read_bytes()) == digest
    for label, repo in [('source', S), ('control', C), ('tool', T)]:
        assert git(repo, 'rev-parse', 'HEAD').decode().strip() == ids[label]['sha']
        assert git(repo, 'rev-parse', 'HEAD^{tree}').decode().strip() == ids[label]['tree']
        assert not git(repo, 'status', '--porcelain=v1')
    for label, repo in [('source', S), ('control', C)]:
        assert git(repo, 'show', '-s', '--format=%P', 'HEAD').decode().strip() == ids[label]['parent']
    # Exact diff bytes AND index replay are distinct checks.
    patch_checks = []
    for p in read('PATCHES.json'):
        repo = S if p['path'].startswith('SOURCE-') else C
        data = git(repo, 'diff', '--binary', '--full-index', p['base'], p['target'])
        assert data == (PACK / p['path']).read_bytes(), p['path']
        patch_checks.append({'path': p['path'], 'sha256': sha(data), 'exact_git_diff': True})

    sys.path.insert(0, str(Q))
    import contract_stacks as stacks
    import cfg_pfc as cfg
    import runner
    r = runner.load_request()
    old = json.loads(git(C, 'show', ids['control']['derivation_control'] + ':ch8-s1-control/CI-REQUEST.json'))
    invariant_keys = ['rows', 'source_bindings', 'variants', 'budgets', 'execution_groups',
                      'replacement_unions', 'formal_expected_inventory',
                      'diagnostic_assumed_inventory', 'qualification_inventory', 'flags',
                      'future_runs', 'proof_credit', 'runtime_smallsort_base_sha256']
    for key in invariant_keys:
        assert old[key] == r[key], key
    old_runner = git(C, 'show', ids['control']['derivation_control'] + ':ch8-s1-control/runner.py')
    for key in ['sha', 'tree']:
        old_runner = old_runner.replace(
            git(S, 'rev-parse', ids['source']['derivation_source'] + ('^{tree}' if key == 'tree' else '')).strip(),
            ids['source'][key].encode())
    assert old_runner == (Q / 'runner.py').read_bytes()
    source_paths = git(S, 'diff', '--name-only', ids['source']['derivation_source'], 'HEAD').decode().splitlines()
    assert source_paths == [stacks.SMALLSORT]
    assert git(S, 'show', ids['source']['derivation_source'] + ':' + stacks.SMALLSORT).decode() == stacks.frozen()
    for rel, digest in read('INHERITANCE.json')['byte_identical_package_files'].items():
        baseline = git(G0, 'show', ids['frozen_package_g0'] + ':' + str((PACK.parent / 'batch-r2-r1' / rel).relative_to(G0)))
        assert sha(baseline) == digest and baseline == (PACK / rel).read_bytes()
    for rec in read('INHERITANCE.json')['identity_only_rebound_maps']:
        baseline = json.loads(git(G0, 'show', ids['frozen_package_g0'] + ':' + str((PACK.parent / 'batch-r2-r1' / rec['file']).relative_to(G0))))
        candidate = read(rec['file'])
        assert [k for k in candidate if baseline[k] != candidate[k]] == ['source_sha']
        assert candidate['source_sha'] == ids['source']['sha']
    for f in read('MACRO-TRACE.json')['files']:
        repo = T if f['repo'] == 'stock_tool' else S
        data = git(repo, 'show', f['commit'] + ':' + f['file'])
        assert sha(data) == f['sha256']
        lines = data.decode().splitlines()
        for anchor in f['anchors']:
            assert lines[anchor['line'] - 1] == anchor['source']
        if 'unchanged_from' in f:
            assert data == git(repo, 'show', f['unchanged_from'] + ':' + f['file'])

    # Re-execute reviewed static preflight with every write redirected to ownpaths.
    spec = importlib.util.spec_from_file_location('author_preflight', PACK / 'validate_package.py')
    pre = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pre)
    pre.write = lambda name, value: write('FINAL-' + name, value)
    pre.main()

    # Independently account literal contract paths, including inactive cfg arms.
    doc = read('CONTRACT-STACK-MAP.json')
    regex = re.compile(r'(?:crate::kani|kani|safety)::(?:requires|modifies|ensures)\(')
    literal, attributed = 0, 0
    active = set(doc['contexts'][0]['effective_cfg'])
    by_function = {f['function']: f for f in doc['functions']}
    checked = []
    for mod in doc['modules']:
        text = (S / mod['file']).read_text()
        literal += len(regex.findall(cfg.spelling(cfg.tokens(text))))
        for name, item, attrs in stacks.declarations(text, active):
            fullname = mod['module'] + '::' + '::'.join(name)
            rec = by_function[fullname]
            declared = [cfg.spelling(a) for a in item['attrs']]
            assert declared == rec['declared_attrs_before_cfg']
            assert rec['cfg_availability'] == {'module_chain_active': True,
                'effective_cfg': sorted(active), 'context_rows': [row['id'] for row in r['rows']]}
            attributed += sum(len(regex.findall(a)) for a in declared)
            checked.append(fullname)
    assert len(checked) == len(set(checked)) == 321
    assert literal == attributed == 91

    # Newly added gate tests, once on final dc1. This is NOT the precursor33 suite.
    command = [sys.executable, '-m', 'unittest', '-v', 'test_contract_stacks']
    t0 = time.time()
    test = subprocess.run(command, cwd=Q, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'),
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (HERE / 'FINAL-GATE-TESTS.txt').write_bytes(test.stdout)
    assert test.returncode == 0, test.stdout.decode()

    # Additional real order/deletion mutations absent from named author subcases.
    mutations = []
    source = (S / stacks.SMALLSORT).read_text()
    frame = '#[cfg_attr(kani, crate::kani::modifies(v_base.wrapping_add(a_pos), v_base.wrapping_add(b_pos)))]\n'
    post = next(line + '\n' for line in source.splitlines() if line.startswith('#[cfg_attr(') and 'crate::kani::ensures(|_| !verify::sorting_s2_swap' in line)
    assert frame + post in source
    cases = {'swap_frame_post_reordered': source.replace(frame + post, post + frame, 1),
             'swap_frame_deleted': source.replace(frame, '', 1),
             'swap_post_deleted': source.replace(post, '', 1)}
    with tempfile.TemporaryDirectory(prefix='w14-contract-mutations-') as tmp:
        root = Path(tmp)
        target = root / stacks.SMALLSORT
        target.parent.mkdir(parents=True)
        for label, text in cases.items():
            request = copy.deepcopy(r)
            target.write_text(text)
            request['contract_stack_source_sha256'][stacks.SMALLSORT] = sha(text.encode())
            try:
                stacks.check(root, request)
            except cfg.GateError as error:
                assert 'exact r2-preserving normalization' in str(error)
                mutations.append({'case': label, 'result': 'REJECTED', 'reason': str(error)})
            else:
                raise AssertionError(label)
    write('PINS.json', {'reviewed_g0': REVIEWED, 'task_id': ids['task_id'],
        'source': ids['source'], 'control': ids['control'], 'tool': ids['tool'],
        'frozen_package_g0': ids['frozen_package_g0'],
        'frozen_review_g0': ids['frozen_review_g0'],
        'author_identity_snapshot': ids})
    write('VALIDATION.json', {'state': 'STATIC_PASS', 'package_files': len(files),
        'manifest_hashes': len(manifest), 'patch_exact_diff_checks': patch_checks,
        'invariant_request_keys': invariant_keys, 'source_delta_paths': source_paths,
        'active_modules': 23, 'functions': len(checked), 'contract_stacks': 19,
        'identical_effective_contexts': 11, 'attributed_literal_contract_paths': literal,
        'macro_trace_anchors_and_hashes': 'MATCH', 'runner_two_identity_literals': 'MATCH',
        'final_gate_tests': {'argv': command, 'cwd': str(Q), 'control': ids['control']['sha'],
            'request_sha256': sha((Q / 'CI-REQUEST.json').read_bytes()), 'exit': test.returncode,
            'count': 7, 'elapsed_seconds': round(time.time() - t0, 3)},
        'additional_negative_cases': mutations, 'precursor33': read('TEST-PROVENANCE.json'),
        'precursor33_status': 'AUTHOR_RECORDED_PASS_ON_67eb_ONLY; NOT_REEXECUTED',
        'compiler': 'NOT_RUN', 'macro_expansion': 'NOT_RUN', 'MIR_lookup': 'NOT_RUN',
        'model_execution': 'NOT_RUN', 'qualification': 'NOT_RUN', 'proof_credit': 'NONE',
        'elapsed_seconds': round(time.time() - started, 3)})
    print('W14 STATIC_PASS: exact45/44, six patches, final preflight, 19stacks/11contexts/91paths, 7final gate tests + 3negative mutations')


if __name__ == '__main__':
    main()
