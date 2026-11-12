#!/usr/bin/env python3
"""Source/package integrity checks only. Never opens or extracts raw CI artifacts."""
import hashlib
import json
from pathlib import Path
import subprocess

P = Path(__file__).resolve().parent
R = P.parents[4]
K = Path('/root/kani-fix-3300-c1l')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return sha(json.dumps(value, sort_keys=True, separators=(',', ':')).encode())


def git(repo, *args):
    return subprocess.check_output(['git', *args], cwd=repo)


def read(name):
    return json.loads((P / name).read_text())


# Every prepared JSON document is parseable; observations never upgraded by this check.
for path in P.rglob('*.json'):
    json.loads(path.read_text())
m = read('CASE-MANIFEST.json')
s = m['source']
assert git(K, 'rev-parse', 'HEAD').decode().strip() == s['adapter_commit']
assert git(K, 'rev-parse', 'HEAD^{tree}').decode().strip() == s['adapter_tree']
assert git(K, 'rev-parse', 'HEAD^').decode().strip() == s['diagnostic_parent']
assert not git(K, 'status', '--porcelain')
patch = git(K, 'diff', '--binary', '--unified=0', s['diagnostic_parent'], s['adapter_commit'])
assert patch == (P / 'diagnostic-adapter.patch').read_bytes()
assert sha(patch) == s['adapter_patch_sha256']
changed = git(K, 'diff', '--name-only', s['diagnostic_parent'], s['adapter_commit']).decode().splitlines()
assert set(changed) == {
    'kani-compiler/src/kani_middle/d0_diagnostics.rs',
    'kani-compiler/src/codegen_cprover_gotoc/compiler_interface.rs',
    'kani-compiler/src/codegen_cprover_gotoc/codegen/operand.rs',
    'kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/mod.rs',
}
git(K, 'diff', '--check', s['diagnostic_parent'], s['adapter_commit'])
config = read('CONFIG.json')
assert sha((P / 'CONFIG.json').read_bytes()) == m['config_file_sha256']
assert canonical(config) == m['configuration_canonical_sha256']
assert '--only-codegen' in config['argv_template']
assert '--target' not in config['argv_template']  # not a standalone Kani CLI argument
assert '--target=x86_64-unknown-linux-gnu' in config['environment_template']['RUSTFLAGS']
assert '--harness' in config['argv_template'] and '--exact' in config['argv_template']
assert not any(x in config['argv_template'] for x in ['--export-json', '--cbmc-args', '--trace'])
assert config['solver']['required_exec_count'] == 0
expect = {x['case']: x for x in read('EXPECTED-BINDINGS.json')['cases']}
assert len(expect) == len(m['cases']) == 6
for row in m['cases']:
    cm = read(row['manifest'])
    assert sha((P / row['manifest']).read_bytes()) == row['manifest_sha256']
    assert cm['case'] == row['case'] and cm['source'] == s
    assert cm['harness']['expected_pretty_roots'] == [row['case']]
    assert cm['harness']['expected_root_count'] == cm['harness']['units'] == 1
    assert cm['harness']['exact'] and cm['harness']['reachability'] == 'Harnesses'
    assert cm['configuration_canonical_sha256'] == canonical(cm['configuration'])
    assert cm['configuration']['global_config_canonical_sha256'] == canonical(config)
    source = (R / cm['input']['path']).read_bytes()
    pinned = git(R, 'show', cm['input']['commit'] + ':' + cm['input']['path'])
    assert source == pinned
    assert sha(source) == cm['input']['sha256'] == row['fixture_sha256']
    assert len(source) == cm['input']['bytes']
    assert cm['observed']['compiler'] == 'NOT_RUN'
    assert cm['observed']['compiler_exit'] is None and cm['observed']['solver_exit'] is None
    e = expect[row['case']]
    assert e['observed']['compiler'] == e['observed']['runtime_initializedness'] == 'NOT_RUN'
    assert not e['observed']['proof_credit']
    for side in ['left', 'right']:
        exp = e['semantic_expectations_only'][side]
        assert exp['expected_some_mask_if_immutable_allocation'] == [v is not None for v in exp['source_referent_bytes_if_constant']]
for row in m['planning_inputs']:
    assert sha(git(R, 'show', row['commit'] + ':' + row['path'])) == row['sha256']
for row in read('SOURCE-API.json')['files']:
    b = git(K, 'show', row['commit'] + ':' + row['path'])
    assert sha(b) == row['sha256'] and b == (K / row['path']).read_bytes()
    lines = b.decode().splitlines()
    for anchor in row['anchors']:
        assert anchor['lines'] == [i + 1 for i, line in enumerate(lines) if anchor['literal'] in line]
contract = read('OUTPUT-CONTRACT.json')
assert contract['field_contract']['operands']['cardinality'] == 2
assert contract['field_contract']['full_byte_checks']['cardinality'] == 2
assert contract['field_contract']['runtime']['initializedness'] == 'NOT_RUN'
assert 'instance_data' in contract['files']['CASE/compiler/PID-SEQUENCE-STAGE.json']['required']
assert contract['limits_bytes']['case'] * 6 + contract['limits_bytes']['shared_metadata'] <= contract['limits_bytes']['curated_packet']
assert config['limits']['observer_bytes'] + 65536 == config['limits']['case_bytes']
for f, limit in [('NOTES.md', 30), ('RESULT-KANI3300-C1L.md', 15)]:
    assert len((P / f).read_text().splitlines()) <= limit
print(json.dumps({'status': 'PASS_SOURCE_STATIC_ONLY', 'cases': 6, 'adapter_commit': s['adapter_commit'],
                  'changed_compiler_paths': len(changed), 'fixture_hashes': 'MATCH_PINNED_UNCHANGED',
                  'config_canonical_sha256': canonical(config), 'compiler_and_runtime': 'NOT_RUN'}))
