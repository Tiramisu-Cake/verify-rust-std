#!/usr/bin/env python3
"""Exact-object, source and package preflight; no compiler or full runner."""
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def git(repo, *args, env=None):
    return subprocess.check_output(['git', '-C', str(repo), *args], env=env, text=True).strip()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2) + '\n')


def replay(repo, item):
    with tempfile.TemporaryDirectory(prefix='s2-r3-index-') as tmp:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(tmp) / 'index'))
        subprocess.run(['git', '-C', str(repo), 'read-tree', item['base']], env=env, check=True)
        subprocess.run(['git', '-C', str(repo), 'apply', '--cached', str(HERE / item['path'])],
                       env=env, check=True)
        tree = git(repo, 'write-tree', env=env)
        assert tree == item['target_tree']
        return {'patch': item['path'], 'base': item['base'], 'tree': tree, 'status': 'EXACT_TREE_MATCH'}


def shallow(repo, head, depth, endpoint):
    common = Path(git(repo, 'rev-parse', '--git-common-dir'))
    if not common.is_absolute():
        common = (repo / common).resolve()
    chain = git(repo, 'rev-list', '--first-parent', '--max-count=' + str(depth), head).splitlines()
    assert len(chain) == depth and endpoint in chain
    with tempfile.TemporaryDirectory(prefix='s2-r3-shallow-') as tmp:
        probe = Path(tmp)
        subprocess.run(['git', 'init', '-q', str(probe)], check=True)
        (probe / '.git/objects/info/alternates').write_text(str(common / 'objects') + '\n')
        subprocess.run(['git', '-C', str(probe), 'update-ref', 'refs/heads/probe', head], check=True)
        subprocess.run(['git', '-C', str(probe), 'symbolic-ref', 'HEAD', 'refs/heads/probe'], check=True)
        (probe / '.git/shallow').write_text(chain[-1] + '\n')
        assert git(probe, 'rev-parse', '--is-shallow-repository') == 'true'
        assert git(probe, 'rev-list', '--first-parent', 'HEAD').splitlines() == chain
        assert git(probe, 'cat-file', '-t', endpoint) == 'commit'
        paths = git(probe, 'diff', '--name-only', endpoint, 'HEAD').splitlines()
        assert git(probe, 'rev-parse', 'HEAD^{tree}') == git(repo, 'rev-parse', head + '^{tree}')
    return {'head': head, 'depth': depth, 'endpoint': endpoint, 'retained_chain': chain,
            'endpoint_diff_paths': paths, 'status': 'PASS_REAL_SHALLOW_GIT_METADATA_SHARED_OBJECTS'}


def main():
    ids = json.loads((HERE / 'IDENTITIES.json').read_text())
    S, C, T = Path(ids['source']['worktree']), Path(ids['control']['worktree']), Path('/root/kani-upstream-ch8-s1')
    Q = C / 'ch8-s1-control'
    sys.path.insert(0, str(Q))
    import runner
    import s2_policy
    import cfg_pfc
    import contract_stacks
    import check_package
    r = runner.load_request()
    for label, repo in [('source', S), ('control', C), ('tool', T)]:
        assert git(repo, 'rev-parse', 'HEAD') == ids[label]['sha']
        assert git(repo, 'rev-parse', 'HEAD^{tree}') == ids[label]['tree']
        assert not git(repo, 'status', '--porcelain=v1'), label
    assert git(C, 'rev-parse', 'HEAD^') == ids['control']['parent'] == r['control_parent']
    assert git(S, 'rev-parse', 'HEAD^') == ids['source']['parent']
    assert sha(Q / 'CI-REQUEST.json') == ids['control']['request_sha256']
    assert sha(C / '.github/workflows/ch8-s2.yml') == ids['control']['workflow_sha256']
    assert (HERE / 'CI-REQUEST.json').read_bytes() == (Q / 'CI-REQUEST.json').read_bytes()
    assert (HERE / 'WORKFLOW.yml').read_bytes() == (C / '.github/workflows/ch8-s2.yml').read_bytes()
    for rel, digest in json.loads((HERE / 'SOURCE-MAP.json').read_text())['files'].items():
        assert sha(S / rel) == digest, rel
    source_result = runner.verify_source(S, T, r)
    cfg = cfg_pfc.check(S, r)
    assert cfg == json.loads((HERE / 'CFG-PFC-MAP.json').read_text())
    stacks = json.loads((HERE / 'CONTRACT-STACK-MAP.json').read_text())
    # Enriched map must contain the exact unmodified gate result.
    enrichments = ('declared_attrs_before_cfg', 'cfg_availability')
    for rec in stacks['functions'] + stacks['contract_stacks']:
        for key in enrichments:
            rec.pop(key)
    coverage = stacks.pop('opaque_contract_coverage')
    assert coverage['unattributed_contract_paths'] == 0
    assert coverage['lexical_contract_paths'] == coverage['attributed_to_enumerated_functions'] == 91
    assert stacks == contract_stacks.check(S, r)
    assert len(stacks['contexts']) == 11 and len(stacks['contract_stacks']) == 19
    assert len(stacks['functions']) == 321 and len(stacks['modules']) == 23
    fixtures = json.loads((Q / 'S2-SOURCE.json').read_text())
    for rel, text in fixtures.items():
        assert (S / rel).read_text() == text, rel
    assert git(S, 'diff', '--name-only', ids['source']['derivation_source'], 'HEAD') == s2_policy.SMALLSORT
    assert (S / s2_policy.SMALLSORT).read_text() == contract_stacks.normalize(contract_stacks.frozen())
    # Existing check-source invokes s2_policy -> contract_stacks before tool setup/build.
    os.environ.update(GITHUB_REPOSITORY='Tiramisu-Cake/kani', GITHUB_EVENT_NAME='push',
                      GITHUB_REF='refs/heads/uninit-ci/ch8-s2-batch3probes-offline-r3',
                      GITHUB_RUN_ATTEMPT='1', GITHUB_SHA=ids['control']['sha'])
    control_result = check_package.control(C)
    yaml_result = check_package.check_yaml(C / '.github/workflows/ch8-s2.yml')
    # Only stock-relative path inventory was corrected after the33-test run.
    tested_control = '67ebcf4a2285976b85d986e741adde8e443b706a'
    tested_request = json.loads(git(C, 'show', tested_control + ':ch8-s1-control/CI-REQUEST.json'))
    assert git(C, 'diff', '--name-only', tested_control, 'HEAD') == 'ch8-s1-control/CI-REQUEST.json'
    assert [key for key in r if r[key] != tested_request[key]] == ['ci_changed_paths']
    proof = json.loads((HERE / 'TEST-PROVENANCE.json').read_text())
    assert proof['control_sha'] == tested_control and proof['source_sha'] == ids['source']['sha']
    assert proof['exit_code'] == 0
    assert proof['request_sha256'] == hashlib.sha256(git(C, 'show', tested_control + ':ch8-s1-control/CI-REQUEST.json').encode() + b'\n').hexdigest()
    transcript = (HERE / 'TARGETED-TESTS.txt').read_text()
    assert 'Ran 33 tests' in transcript and transcript.endswith('\nOK\n')
    invariance = json.loads((HERE / 'RUNNER-INVARIANCE.json').read_text())
    for rec in invariance['files']:
        assert sha(C / rec['file']) == rec['candidate_sha256']
        old = subprocess.check_output(['git', '-C', str(C), 'show', invariance['reference'] + ':' + rec['file']])
        assert hashlib.sha256(old).hexdigest() == rec['reference_sha256']
        if rec['status'] == 'BYTE_IDENTICAL':
            assert old == (C / rec['file']).read_bytes()
    assert all(x['status'] == 'BYTE_IDENTICAL' for x in invariance['files']
               if x['file'].endswith(('/pack_evidence.py', '/rustc_diagnostics.py', '/test_rustc_diagnostics.py')))
    patches = []
    for item in json.loads((HERE / 'PATCHES.json').read_text()):
        assert sha(HERE / item['path']) == item['sha256']
        patches.append(replay(S if item['path'].startswith('SOURCE-') else C, item))
    ancestry = [shallow(C, ids['control']['sha'], 7, ids['tool']['sha']),
                shallow(S, ids['source']['sha'], 5, ids['source']['base']),
                shallow(T, ids['tool']['sha'], 2, ids['tool']['sha'])]
    parsed = []
    for path in sorted(Q.glob('*.py')):
        ast.parse(path.read_text(), filename=str(path))
        parsed.append(path.name)
    for repo, base in [(S, ids['source']['base']), (C, ids['control']['base'])]:
        subprocess.run(['git', '-C', str(repo), 'diff', '--check', base, 'HEAD'], check=True)
    assert sum(x['required_cover_count'] for x in r['rows']) == 20
    assert sum('oracle' in x for x in r['rows']) == 6
    for row in r['rows']:
        argv = runner.build_argv(S, T, [row['selector']], 34, Path('/synthetic/export.json'))
        assert argv.count('--harness') == 1 and argv[argv.index('--harness-timeout') + 1] == '600s'
        assert '--exact' in argv and '--no-assert-contracts' in argv and '--jobs=1' in argv
    write('VALIDATION.json', {'state': 'STATIC_PASS', 'source': source_result,
                              'control': control_result, 'workflow': yaml_result,
                              'patch_replays': patches, 'checkout_depths': ancestry,
                              'python_AST_files': parsed,
                              'tests': {'count': 33, 'failures': 0, 'execution_control': tested_control,
                                        'final_control_delta': 'ci_changed_paths only; all functional inputs/code byte-identical',
                                        'final_control_source_payload_preflight': 'PASS'},
                              'contract_stacks': 19, 'contexts': 11,
                              'compilation': 'NOT_RUN', 'qualification': 'NOT_RUN', 'proof_credit': 'NONE'})
    print(f'STATIC_PASS: {len(patches)} exact patch replays; checkout7/5/2; source/control/payload/cfg/model/stack bindings;33 targeted tests inherited by exact code/input identity except path inventory.')


if __name__ == '__main__':
    main()
