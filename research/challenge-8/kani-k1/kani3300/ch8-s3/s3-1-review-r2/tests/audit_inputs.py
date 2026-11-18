"""Independent exact-byte and provenance audit. Does not run native tools."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

G0 = Path('/root/verify-rust-std-kani3300-g0')
REL = 'research/challenge-8/kani-k1/kani3300/ch8-s3/'
PKG = G0 / REL / 's3-1-r2'
OUT = G0 / REL / 's3-1-review-r2'
PACKAGE = '008fcb7705e658643582668ebfabb5f2e340e95d'
FROZEN = 'fc29b93b1e333b73e55e2872701c80d9927f3b02'
OLDPKG = '0902ad2d84e5e5c4d9bb3b01d5c7f7671e84b38d'
REVIEW = '27040e2cd8d3564e5d0a929b8f68ca38a5a61432'


def git(repo, *args, env=None):
    return subprocess.check_output(['git', '-C', str(repo), *args], env=env)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(name):
    return json.loads((PKG / name).read_text())


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        assert path.read_bytes() == data, path
    else:
        path.write_bytes(data)


def main():
    record = dict(schema='independent14-path-delta-input-audit-v1', package=PACKAGE,
                  started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), checks={})
    checks = record['checks']
    names = git(G0, 'ls-tree', '-r', '--name-only', PACKAGE, '--', REL + 's3-1-r2/').decode().splitlines()
    assert len(names) == 65
    for name in names:
        data = git(G0, 'show', PACKAGE + ':' + name)
        assert (G0 / name).read_bytes() == data, name
        save(OUT / 'inputs/package' / Path(name).relative_to(REL + 's3-1-r2'), data)
    entries = (PKG / 'MANIFEST.sha256').read_text().splitlines()
    assert len(entries) == 64
    manifested = set()
    for line in entries:
        digest, name = line.split('  ', 1)
        assert sha((PKG / name).read_bytes()) == digest, name
        manifested.add(name)
    assert manifested == {str(Path(n).relative_to(REL + 's3-1-r2')) for n in names} - {'MANIFEST.sha256'}
    checks['package'] = dict(files=65, manifest_entries=64, complete=True, status='EXACT_COMMITTED_BYTES_MATCH')
    for name, commit in [('s3-1-r1', OLDPKG), ('s3-1-review-r1', REVIEW),
                         ('run-44405927807', read('PINS.json')['intake'])]:
        files = git(G0, 'ls-tree', '-r', '--name-only', commit, '--', REL + name + '/').decode().splitlines()
        assert files
        for path in files:
            assert (G0 / path).read_bytes() == git(G0, 'show', commit + ':' + path), path
        checks[name + '_immutable'] = dict(commit=commit, files=len(files), status='EXACT_BYTES_MATCH')
    inputs = read('INPUTS.json')
    for dep in inputs['dependencies']:
        data = git(G0, 'show', dep['commit'] + ':' + dep['path'])
        assert sha(data) == dep['sha256'] and len(data) == dep['bytes']
        assert git(G0, 'rev-parse', dep['commit'] + ':' + dep['path']).decode().strip() == dep['blob']
        assert (PKG / dep['copy']).read_bytes() == data
    checks['dependency_copies'] = dict(count=len(inputs['dependencies']), status='COMMIT_BLOB_HASH_BYTES_MATCH')
    pins = read('PINS.json')
    for role in ('control', 'source', 'tool'):
        pin = pins[role]
        repo = Path(pin['worktree'])
        for rev, key in [('HEAD', 'sha'), ('HEAD^{tree}', 'tree')]:
            assert git(repo, 'rev-parse', rev).decode().strip() == pin[key]
        assert git(repo, 'show', '-s', '--format=%P', 'HEAD').decode().strip() == pin['parent']
        assert not git(repo, 'status', '--porcelain=v1')
        checks[role] = dict(pin, clean=True)
    control = Path(pins['control']['worktree'])
    source = Path(pins['source']['worktree'])
    request = read('CI-REQUEST.json')
    req_bytes = (PKG / 'CI-REQUEST.json').read_bytes()
    workflow = (PKG / 'WORKFLOW.yml').read_bytes()
    assert req_bytes == (control / 'ch8-s1-control/CI-REQUEST.json').read_bytes()
    assert workflow == (control / '.github/workflows/ch8-s2.yml').read_bytes()
    assert sha(req_bytes) == pins['request_sha256']
    assert sha(workflow) == pins['workflow_sha256']
    assert workflow == git(control, 'show', FROZEN + ':.github/workflows/ch8-s2.yml')
    for key, repo in [('ci_payload_sha256', control), ('changed_file_sha256', source),
                      ('cfg_pfc_source_sha256', source), ('ordinary_contract_source_sha256', source),
                      ('contract_stack_source_sha256', source), ('lexical_source_sha256', source)]:
        for name, digest in request[key].items():
            assert sha((repo / name).read_bytes()) == digest, (key, name)
    old_request = json.loads(git(control, 'show', FROZEN + ':ch8-s1-control/CI-REQUEST.json'))
    changed_keys = sorted(k for k in old_request.keys() | request.keys() if old_request.get(k) != request.get(k))
    assert changed_keys == ['ci_changed_paths', 'ci_payload_sha256', 's3_path_control_precursor']
    checks['request_workflow'] = dict(request_sha256=sha(req_bytes), workflow_sha256=sha(workflow),
                                    changed_request_keys=changed_keys, payloads_and_source_hashes='MATCH')
    for scope in inputs['immutable_source_scope_maps']:
        data = (PKG / scope['file']).read_bytes()
        assert sha(data) == scope['sha256']
        assert data == git(G0, 'show', OLDPKG + ':' + REL + 's3-1-r1/' + scope['file'])
    checks['six_source_maps'] = 'EXACT_BYTES_MATCH; source semantic review inherited only for frozen identities'
    patches = []
    for patch in read('PATCHES.json'):
        assert sha((PKG / patch['patch']).read_bytes()) == patch['sha256']
        repo = source if patch['patch'].startswith('SOURCE') else control
        with tempfile.TemporaryDirectory() as d:
            env = dict(os.environ, GIT_INDEX_FILE=d + '/index')
            git(repo, 'read-tree', patch['base'], env=env)
            git(repo, 'apply', '--cached', '--whitespace=nowarn', str(PKG / patch['patch']), env=env)
            tree = git(repo, 'write-tree', env=env).decode().strip()
            assert tree == patch['tree']
        patches.append(dict(patch=patch['patch'], tree=tree, status='EXACT_TREE_MATCH'))
    checks['patch_replays'] = patches
    for chain in read('ANCESTRY.json'):
        actual = git(pins[chain['kind']]['worktree'], 'rev-list', '--first-parent',
                     '--max-count=' + str(chain['depth']), chain['head']).decode().splitlines()
        assert actual == chain['chain']
    checks['ancestry'] = '7/5/2 MATCH'
    paths = git(control, 'diff', '--name-only', FROZEN, pins['control']['sha']).decode().splitlines()
    assert paths == inputs['delta_paths']
    checks['delta_paths'] = paths
    for name in paths + ['ch8-s1-control/runner.py', 'ch8-s1-control/s3_evidence.py',
                         'ch8-s1-control/s3_snapshots.py', 'ch8-s1-control/s3_profile.py',
                         'ch8-s1-control/s3_policy.py', '.github/workflows/ch8-s2.yml']:
        save(OUT / 'inputs/control' / name, git(control, 'show', pins['control']['sha'] + ':' + name))
    assert (PKG / 'FIXTURE-REGRESSION.py').read_bytes() == (control / 'ch8-s1-control/test_s3_paths.py').read_bytes()
    final = read('FINAL-VALIDATE.json')
    validation = read('VALIDATION.json')
    assert sha((PKG / 'FINAL-VALIDATE.json').read_bytes()) == validation['final_record_sha256']
    for name, key in [('run_final_validate.py', 'script_sha256'), ('FINAL-VALIDATE.stdout.txt', 'stdout_sha256'),
                      ('FINAL-VALIDATE.stderr.txt', 'stderr_sha256')]:
        assert sha((PKG / name).read_bytes()) == final[key]
    for key in ('control_sha', 'control_tree', 'source_sha', 'source_tree'):
        role, field = key.split('_')
        assert final[key] == pins[role][field]
    for key in ('request_sha256', 'workflow_sha256'):
        assert final[key] == pins[key]
    tracked = git(control, 'ls-tree', '-r', '--name-only', pins['control']['sha']).decode().splitlines()
    actual = {name: sha((control / name).read_bytes()) for name in tracked if (control / name).is_file()}
    assert actual == final['tracked_worktree_sha256']
    assert final['state'] == 'PASS' and final['execution_count'] == 1
    assert (final['monotonic_end_ns'] - final['monotonic_start_ns']) / 1e9 == final['elapsed_seconds']
    assert final['margin'] == 1080 / final['elapsed_seconds'] and final['margin'] >= 1.5
    assert len(final['commands_executed']) == 2 and all(x['exit_code'] == 0 for x in final['commands_executed'])
    summary = validation['test_summary']
    assert summary['legacy_tests'] == 136 and summary['s3_tests'] == 56 and summary['success']
    assert summary['failures'] == summary['errors'] == 0
    transcript = (PKG / 'FINAL-VALIDATE.stderr.txt').read_text()
    assert 'Ran 136 tests' in transcript and 'Ran 56 tests' in transcript
    stdout = (PKG / 'FINAL-VALIDATE.stdout.txt').read_text().splitlines()
    assert json.loads(stdout[-1]) == summary
    gates = read('SOURCE-GATES.json')
    assert gates['state'] == 'STATIC_PASS'
    for name, digest in gates['source_gate_files'].items():
        assert sha((control / 'ch8-s1-control' / name).read_bytes()) == digest
    for key in ('control_sha', 'control_tree', 'request_sha256', 'workflow_sha256'):
        assert gates[key] == final[key]
    checks['author_final_validate'] = dict(tests=192, recorded_execution_count=1,
        tracked_files=len(actual), elapsed_seconds=final['elapsed_seconds'], margin=final['margin'],
        receipt_script_transcripts_and_exact_tree='MATCH', independently_witnessed=False, rerun=False)
    # Read intake summaries as data. These are not runtime evidence of this review.
    diff = json.loads((PKG / 'inputs/intake/BEFORE-DIFF.json').read_text())
    assert diff['cause'] == 'PATH_STRING_REPRESENTATION_MISMATCH_WITH_EQUAL_RECORDED_HASHES'
    for comparison in diff['comparisons']:
        assert comparison['sha256_equal']
        if comparison['binary'] != 'cbmc':
            assert not comparison['path_equal'] and [x['field'] for x in comparison['differing_fields']] == ['path']
    checks['historical_intake'] = dict(status='UNCHANGED_STOPPED_PREFIX0', physical_identity='UNKNOWN',
                                      native='SOURCE_REPORTED_LITERAL_ONLY', qualification=0, proof_credit=0)
    record['ended_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    record['status'] = 'PASS'
    save(OUT / 'INPUT-AUDIT.json', (json.dumps(record, indent=2) + '\n').encode())
    print(json.dumps(dict(status='PASS', package_files=65, manifest_entries=64, patches=len(patches),
                          author_tests=192, margin=final['margin'])))


if __name__ == '__main__':
    main()
