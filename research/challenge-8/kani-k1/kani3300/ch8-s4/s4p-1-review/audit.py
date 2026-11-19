#!/usr/bin/env python3
"""Bounded offline independent review; no compiler, CI, network or full Validate."""
import ast
import hashlib
import importlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
PACKET = HERE.parent / 's4p-1'
G0 = HERE.parents[5]
AUTHOR = '590dd6360f5b4c92eab9fff30aa0d2e7d8d942ce'
D = lambda b: hashlib.sha256(b).hexdigest()

def git(repo, *args, env=None):
    return subprocess.check_output(['git', '-C', str(repo), *args], env=env).decode().strip()

def blob(repo, commit, name):
    return subprocess.check_output(['git', '-C', str(repo), 'show', commit + ':' + name])

def main():
    started = time.monotonic()
    pins = json.loads((PACKET / 'PINS.json').read_text())
    result = {'schema': 's4p-1-independent14-audit-v1', 'author': AUTHOR,
              'native_CI_full_validate_raw_GCS': 'NOT_RUN', 'proof_credit': 'NONE'}
    identities = {}
    for name in ('source', 'control', 'tool'):
        item = pins[name]; repo = Path(item['repo'])
        observed = {'sha': git(repo, 'rev-parse', 'HEAD'),
                    'tree': git(repo, 'rev-parse', 'HEAD^{tree}'),
                    'parents': git(repo, 'show', '-s', '--format=%P', 'HEAD').split(),
                    'dirty': git(repo, 'status', '--porcelain=v1')}
        assert all(observed[k] == item[k] for k in ('sha', 'tree', 'parents'))
        assert observed['dirty'] == ''
        identities[name] = observed
    result['identities'] = identities
    manifest = {}
    for line in (PACKET / 'MANIFEST.sha256').read_text().splitlines():
        sha, rel = line.split('  ', 1)
        assert rel not in manifest
        raw = (PACKET / rel).read_bytes()
        assert D(raw) == sha
        assert raw == blob(G0, AUTHOR, str((PACKET / rel).relative_to(G0)))
        manifest[rel] = sha
    actual = {str(p.relative_to(PACKET)) for p in PACKET.rglob('*') if p.is_file()}
    assert actual == set(manifest) | {'MANIFEST.sha256'}
    assert (PACKET / 'MANIFEST.sha256').read_bytes() == blob(G0, AUTHOR, str((PACKET / 'MANIFEST.sha256').relative_to(G0)))
    result['packet'] = {'files': len(actual), 'hashes': len(manifest),
                        'manifest_sha256': D((PACKET / 'MANIFEST.sha256').read_bytes()), 'exact_author_bytes': True}
    for entry in json.loads((PACKET / 'DEPENDENCIES.json').read_text())['entries']:
        assert D(blob(entry['repo'], entry['commit'], entry['path'])) == entry['sha256']
    src = Path(pins['source']['repo']); ctl = Path(pins['control']['repo'])
    delta = git(src, 'diff', '--name-status', pins['source']['reference'], pins['source']['sha']).splitlines()
    assert delta == ['M\tlibrary/core/src/slice/sort/shared/smallsort/verify.rs',
                     'A\tlibrary/core/src/slice/sort/shared/smallsort/verify/sorting_s4_partition.rs']
    verify = 'library/core/src/slice/sort/shared/smallsort/verify.rs'
    assert blob(src, pins['source']['sha'], verify).startswith(blob(src, pins['source']['reference'], verify))
    result['source_preservation'] = {'whole_tree_delta': delta, 'old_verify_prefix_unchanged': True}
    control_delta = git(ctl, 'diff', '--name-only', pins['control']['reference'], pins['control']['sha']).splitlines()
    assert control_delta == json.loads((PACKET / 'CONTROL-PRESERVATION.json').read_text())['changed_paths']
    result['control_preservation'] = {'exact_delta_paths': control_delta,
                                      'all_other_reference_tree_entries': 'IDENTICAL'}
    replays = []
    for spec in json.loads((PACKET / 'PATCHES.json').read_text()):
        repo = src if spec['file'].startswith('SOURCE') else ctl
        with tempfile.TemporaryDirectory(prefix='s4p-review-index-') as tmp:
            env = dict(os.environ, GIT_INDEX_FILE=str(Path(tmp) / 'index'))
            git(repo, 'read-tree', spec['base'], env=env)
            git(repo, 'apply', '--cached', '--whitespace=nowarn', str(PACKET / spec['file']), env=env)
            tree = git(repo, 'write-tree', env=env)
            assert tree == spec['expected_tree'] == pins['source' if repo == src else 'control']['tree']
            replays.append({'patch': spec['file'], 'base': spec['base'], 'tree': tree, 'status': 'EXACT_TREE_PASS'})
    result['independent_patch_replays'] = replays
    sys.path.insert(0, str(ctl / 'ch8-s1-control'))
    import runner, s4p_policy, s4p_profile, check_package
    request = runner.load_request()
    assert (ctl / 'ch8-s1-control/CI-REQUEST.json').read_bytes() == (PACKET / 'CI-REQUEST.json').read_bytes()
    assert D((PACKET / 'CI-REQUEST.json').read_bytes()) == pins['request']['sha256']
    assert D((ctl / '.github/workflows/ch8-s2.yml').read_bytes()) == pins['request']['workflow_sha256']
    for rel, sha in request['ci_payload_sha256'].items():
        assert D(blob(ctl, pins['control']['sha'], rel)) == sha
    fixture = json.loads((ctl / 'ch8-s1-control/S4P-SOURCE.json').read_text())
    assert all((src / rel).read_text() == text for rel, text in fixture.items())
    result['source_and_payload'] = {'source_files': len(fixture), 'control_payload_hashes': len(request['ci_payload_sha256']),
                                   'request_sha256': pins['request']['sha256'], 'workflow_sha256': pins['request']['workflow_sha256']}
    gate = s4p_policy.validate_source(src, request)
    result['fresh_source_gates'] = {name: {'status': report['status'], 'files': len(report['source_files_sha256'])}
                                    for name, report in gate['reports'].items()}
    projections = gate['reports']['contract_stacks']['cfg_projection_invariance']
    cfgsets = [set(x['effective_cfg']) for x in projections]
    import s4p_contract_stacks as stacks
    keys = sorted(stacks.ACTIVE | {'kani_smallsort_s3_leaf', 'kani_smallsort_s4_partition'})
    finding = {'id': 'R14-01', 'file': 'ch8-s1-control/s4p_contract_stacks.py', 'line': 109,
               'keys': keys, 'expected_combinations': 1 << len(keys), 'actual_combinations': len(cfgsets),
               'sorting_flag_present_in_any_projection': any('kani_smallsort_sorting' in x for x in cfgsets),
               'active_s2_guard_projection_count': sum(stacks.ACTIVE <= x for x in cfgsets),
               'projection_cfgs': [sorted(x) for x in cfgsets]}
    assert finding['expected_combinations'] == 32 and finding['actual_combinations'] == 16
    assert finding['sorting_flag_present_in_any_projection'] is False
    assert finding['active_s2_guard_projection_count'] == 0
    recorded = json.loads((PACKET / 'MAP-CONTRACT_STACKS.json').read_text())['cfg_projection_invariance']
    assert projections == recorded
    result['reproduced_finding'] = finding
    result['workflow_static'] = check_package.check_yaml(ctl / '.github/workflows/ch8-s2.yml')
    final = json.loads((PACKET / 'FINAL-VALIDATE.json').read_text())
    for stream in ('stdout', 'stderr'):
        spec = final[stream]; raw = (PACKET / spec['file']).read_bytes()
        assert len(raw) == spec['bytes'] and D(raw) == spec['sha256']
    summary = json.loads((PACKET / 'FINAL-VALIDATE.stdout').read_text().splitlines()[-1])
    assert sum(summary['test_counts'].values()) == 302
    assert final['exit_code'] == 0 and summary['success'] and not summary['errors'] and not summary['failures']
    assert final['control_sha'] == pins['control']['sha'] and final['request_sha256'] == pins['request']['sha256']
    assert final['script_sha256'] == D((ctl / 'ch8-s1-control/s4p_validate.py').read_bytes())
    assert final['command'] == 'python3 check_package.py control --repo ..\npython3 s4p_validate.py\n'
    assert final['margin_at_18_minutes'] == 1080 / final['elapsed_seconds'] >= 1.5
    err = (PACKET / 'FINAL-VALIDATE.stderr').read_text()
    assert len(re.findall(r'^Ran \d+ tests? in ', err, re.M)) == 5
    result['author_final_validate'] = {'assurance': 'RETAINED_EXACT_LOCAL_TEST_RECORD_CHECKED; NOT_REEXECUTED',
        'tests': 302, 'suite_counts': summary['test_counts'], 'exit': final['exit_code'],
        'wall_seconds': final['elapsed_seconds'], 'margin': final['margin_at_18_minutes']}
    from validate_tokens import cached_tokens
    modules = [importlib.import_module(n) for n in ('cfg_pfc', 's3_cfg_pfc', 's32_cfg_pfc', 's34_cfg_pfc', 's4p_cfg_pfc')]
    originals = {m.__name__: m.tokens for m in modules}
    corpus = ['', 'fn a() {}', '\nfn a() {}', '/* nested /* a */ b */ fn b() {}',
              'let a = r##"attribute #[cfg(x)]"##;', 'let c = \'x\';',
              (src / s4p_policy.LEAF).read_text()]
    expected = {m.__name__: [m.tokens(t) for t in corpus] for m in modules}
    with cached_tokens() as stats:
        for m in modules:
            for text, want in zip(corpus, expected[m.__name__]):
                first = m.tokens(text); first.clear()
                assert m.tokens(text) == want and m.tokens(text) is not m.tokens(text)
            for _ in range(2):
                try: m.tokens('/* unterminated')
                except m.GateError: pass
                else: raise AssertionError('lexer exception swallowed')
        cache_stats = {name: item.cache_info()._asdict() for name, item in stats.items()}
    assert all(m.tokens is originals[m.__name__] for m in modules)
    try:
        with cached_tokens(): raise RuntimeError('restore after exception')
    except RuntimeError: pass
    assert all(m.tokens is originals[m.__name__] for m in modules)
    imports = []
    for file in (ctl / 'ch8-s1-control').glob('*.py'):
        if 'validate_tokens' in file.read_text(): imports.append(file.name)
        ast.parse(file.read_text(), filename=str(file))
    assert sorted(imports) == ['s4p_validate.py', 'test_s4p_boundary.py']
    result['lexer_cache'] = {'equivalence': 'PASS', 'full_text_and_line_coordinates': 'PASS',
        'fresh_lists': 'PASS', 'exceptions_uncached': 'PASS', 'normal_and_exceptional_restore': 'PASS',
        'callers': sorted(imports), 'stats': cache_stats,
        'scope': 'PURE_LEXER_ONLY; NO_GATE_SOURCE_IDENTITY_RESULT_OR_EXCEPTION_CACHE'}
    for item in pins.values():
        if isinstance(item, dict) and 'repo' in item:
            assert not git(item['repo'], 'status', '--porcelain=v1')
    result['elapsed_seconds'] = time.monotonic() - started
    result['status'] = 'REVIEW_FINDING_REPRODUCED_OTHER_CHECKS_PASS'
    (HERE / 'AUDIT.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'finding': finding['id'], 'elapsed_seconds': result['elapsed_seconds']}))

if __name__ == '__main__': main()
