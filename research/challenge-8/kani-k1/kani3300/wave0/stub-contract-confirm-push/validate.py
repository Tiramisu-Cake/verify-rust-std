#!/usr/bin/env python3
"""Validate the push-only packet using static, disposable Git and Python mock checks."""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib
from unittest.mock import patch

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
OLD = HERE.parent / 'stub-contract-confirm'
G0 = HERE.parents[5]
CODE = HERE / 'source/tests/script-based-pre/stub-contract-confirm'
sys.path.insert(0, str(CODE))
import final_head
import runner
from check_push_identity import event_for


def read(path):
    return json.loads(path.read_text())


def static_checks():
    pins, request = read(HERE / 'PINS.json'), read(HERE / 'CI-REQUEST.json')
    control, stock = Path(pins['control']['worktree']), Path(pins['stock']['worktree'])
    prior_control = Path(read(OLD / 'PINS.json')['control']['worktree'])
    profile_path = Path('.github/stub-contract-confirm/profile.json')
    workflow_path = Path('.github/workflows/stub-contract-confirm.yml')
    profile = read(HERE / 'source' / profile_path)
    oldprofile = read(OLD / 'source' / profile_path)
    assert profile['source_sha256'] == oldprofile['source_sha256']
    assert set(profile) == set(oldprofile) and profile['schema'] == oldprofile['schema']
    assert runner.sha(HERE / 'source' / profile_path) == pins['profile_sha256']
    assert runner.sha(HERE / 'source' / workflow_path) == pins['workflow_sha256']
    for scope, root in [('source_sha256', stock), ('control_sha256', control)]:
        for path, digest in profile[scope].items():
            assert runner.sha(root / path) == digest, path
            if scope == 'control_sha256':
                assert runner.sha(HERE / 'source' / path) == digest, path
                runner.git(control, 'ls-files', '--error-unmatch', path)
    assert runner.sha(control / profile_path) == pins['profile_sha256']
    for label, root in [('control', control), ('stock', stock)]:
        for key, ref in [('head', 'HEAD'), ('tree', 'HEAD^{tree}'), ('parent', 'HEAD^')]:
            assert runner.git(root, 'rev-parse', ref) == pins[label][key]
        assert runner.git(root, 'show', '-s', '--format=%P', 'HEAD') == pins[label]['parent']
        assert runner.git(root, 'status', '--porcelain') == ''
    assert runner.git(prior_control, 'rev-parse', 'HEAD') == pins['prior']['control_commit']
    assert runner.git(prior_control, 'status', '--porcelain') == ''
    for prior_commit, directory in [(pins['prior']['package_commit'], OLD),
                                    (pins['prior']['review_commit'], HERE.parent / 'stub-contract-confirm-review-w11'),
                                    (pins['prior']['old_GO_commit'], HERE.parent / 'stub-contract-confirm-go')]:
        relative = str(directory.relative_to(G0))
        assert runner.git(G0, 'rev-parse', prior_commit + ':' + relative) == runner.git(G0, 'rev-parse', 'HEAD:' + relative)
        assert runner.git(G0, 'diff', 'HEAD', '--', relative) == ''
    for entry in read(OLD / 'MANIFEST.json')['files']:
        assert runner.sha(OLD / entry['path']) == entry['sha256']
    for name, base, digest in [('control.patch', runner.BASE, pins['control_patch_sha256']),
                               ('trigger-delta.patch', pins['prior']['control_commit'], pins['trigger_delta_patch_sha256'])]:
        assert runner.sha(HERE / name) == digest
        raw = subprocess.check_output(['git', '-C', str(control), 'diff', '--binary', base, pins['control']['head']])
        assert hashlib.sha256(raw).hexdigest() == digest
    subprocess.run(['git', '-C', str(stock), 'apply', '--check', str(HERE / 'control.patch')], check=True,
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.run(['git', '-C', str(prior_control), 'apply', '--check', str(HERE / 'trigger-delta.patch')], check=True,
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    expected_delta = {'.github/stub-contract-confirm/profile.json', '.github/workflows/slow-tests.yml',
                      str(workflow_path), *(str(Path('tests/script-based-pre/stub-contract-confirm') / name)
                      for name in ('runner.py', 'check_service.py', 'push_identity.py', 'final_head.py', 'check_push_identity.py'))}
    delta = runner.git(control, 'diff', '--no-renames', '--name-only', pins['prior']['control_commit'], 'HEAD').splitlines()
    assert set(delta) == expected_delta, delta
    assert runner.git(control, 'ls-tree', '--name-only', 'HEAD:.github/workflows') == 'stub-contract-confirm.yml'
    changed = runner.git(control, 'diff', '--name-status', runner.BASE, 'HEAD').splitlines()
    for row in changed:
        status, path = row.split('\t')
        assert path in {str(profile_path), *profile['control_sha256']} or (status == 'D' and path.startswith('.github/workflows/'))
    assert not runner.git(control, 'diff', '--name-only', runner.BASE, 'HEAD', '--',
                          'kani-compiler', 'kani-driver', 'kani_metadata', 'library', 'rust-toolchain.toml',
                          'Cargo.lock', '.github/actions', 'scripts', 'docs')
    old_runner = (OLD / 'source/tests/script-based-pre/stub-contract-confirm/runner.py').read_text()
    new_runner = (CODE / 'runner.py').read_text()
    functions = lambda text: {n.name: ast.dump(n, include_attributes=False) for n in ast.parse(text).body
                              if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
    fa, fb = functions(old_runner), functions(new_runner)
    assert fa.keys() == fb.keys() and [name for name in fa if fa[name] != fb[name]] == ['snapshot']
    a = old_runner.index("        require(value['control']['head'] == os.environ.get('SC_CONTROL_HEAD')")
    b = old_runner.index('        changes = ', a)
    projected = old_runner[:a] + """        value['push'] = push_event(ROOT, value['control'])
        request = binding(value['control']['head'], value['control']['tree'], sha(PROFILE))
        value['request'] = request
        value['request_sha256'] = hashlib.sha256(canonical(request)).hexdigest()
""" + old_runner[b:]
    projected = projected.replace('from service import execute', 'from service import execute\nfrom push_identity import push_event')
    projected = projected.replace("allowed |= path == '.github/workflows/slow-tests.yml'",
                                  "allowed |= path == '.github/workflows/stub-contract-confirm.yml'")
    assert projected == new_runner
    invariant_files = {}
    for name in ('Cargo.lock', 'Cargo.toml', 'src/lib.rs', 'service.py', 'workflow_checks.py'):
        old = OLD / 'source/tests/script-based-pre/stub-contract-confirm' / name
        new = CODE / name
        assert old.read_bytes() == new.read_bytes()
        invariant_files[name] = runner.sha(new)
    for name in ('ORACLES.md', 'result.schema.json', 'SOURCES.json'):
        assert (OLD / name).read_bytes() == (HERE / name).read_bytes()
    import yaml
    wa = yaml.load((OLD / 'source/.github/workflows/slow-tests.yml').read_text(), Loader=yaml.BaseLoader)
    wb = yaml.load((HERE / 'source' / workflow_path).read_text(), Loader=yaml.BaseLoader)
    assert wb.pop('on') == {'push': {'branches': ['stub-contract-confirm-ci/**']}}
    wa.pop('on')
    for key in ('SC_CONTROL_HEAD', 'SC_CONTROL_TREE', 'SC_REQUEST_SHA256'):
        wa['jobs']['confirm']['env'].pop(key)
    assert wa == wb
    assert (control / '.github/workflows/slow-tests.yml').exists() is False
    assert request['commands'] == read(OLD / 'CI-REQUEST.json')['commands']
    assert request['caps'] == read(OLD / 'CI-REQUEST.json')['caps']
    assert request['environment'] == read(OLD / 'CI-REQUEST.json')['environment'] == runner.ENV
    assert request['binding'] == request['request_binding'] == pins['request_binding']
    assert pins['request_binding'] == runner.binding(pins['control']['head'], pins['control']['tree'], pins['profile_sha256'])
    assert hashlib.sha256(runner.canonical(pins['request_binding'])).hexdigest() == pins['request_sha256'] == request['request_sha256']
    assert request['profile_sha256'] == pins['profile_sha256'] and request['workflow_sha256'] == pins['workflow_sha256']
    manifest = tomllib.loads((CODE / 'Cargo.toml').read_text())
    assert not any(manifest.get(k) for k in ('dependencies', 'dev-dependencies', 'build-dependencies'))
    assert manifest['workspace'] == {} and set(manifest['features']) == set(runner.SLOTS)
    assert len(list((HERE / 'source').rglob('Cargo.toml'))) == 1
    for path in HERE.rglob('*.py'):
        ast.parse(path.read_text(), filename=str(path))
    for entry in read(HERE / 'SOURCES.json')['files']:
        assert runner.sha(stock / entry['path']) == entry['sha256']
        assert runner.git(stock, 'rev-parse', 'HEAD:' + entry['path']) == entry['git_blob']
    for entry in read(HERE / 'INVENTORY.json')['control']:
        path = control / entry['path']
        assert path.stat().st_size == entry['bytes'] and runner.sha(path) == entry['sha256']
        assert runner.git(control, 'rev-parse', 'HEAD:' + entry['path']) == entry['git_blob']
    for entry in read(HERE / 'INVENTORY.json')['objects'] + read(HERE / 'SOURCES.json')['objects']:
        root = control if entry.get('role') == 'control' else stock
        raw = subprocess.check_output(['git', '-C', str(root), 'cat-file', entry['kind'], entry['git_sha1']])
        assert len(raw) == entry['bytes'] and hashlib.sha256(raw).hexdigest() == entry['content_sha256']
    result = read(HERE / 'result.json'); integrity = result.pop('integrity')
    assert hashlib.sha256(runner.canonical(result)).hexdigest() == integrity['canonical_payload_sha256']
    result['integrity'] = integrity
    assert result['classification'] == 'INCONCLUSIVE' and result['reasons'] == ['NOT_RUN']
    assert result['request_binding'] == pins['request_binding'] and result['request_sha256'] == pins['request_sha256']
    assert all(slot['observation']['outcome'] == 'NOT_RUN' for slot in result['slots'].values())
    import jsonschema
    schema = read(HERE / 'result.schema.json'); jsonschema.Draft202012Validator.check_schema(schema); jsonschema.validate(result, schema)
    gate = final_head.check(control, pins['control']['head'], pins['publication']['ref'], pins['request_sha256'], pins)
    assert gate['request_binding'] == pins['request_binding']
    env = {k: v for k, v in os.environ.items() if not k.startswith(('SC_', 'GITHUB_'))}
    with tempfile.TemporaryDirectory() as directory:
        event_path = Path(directory) / 'event.json'
        event_path.write_text(json.dumps(event_for(control, pins['control']['head'], pins['publication']['ref'])))
        env.update(GITHUB_EVENT_NAME='push', GITHUB_REPOSITORY='Tiramisu-Cake/kani', GITHUB_REF=pins['publication']['ref'],
                   GITHUB_SHA=pins['control']['head'], GITHUB_EVENT_PATH=str(event_path))
        with patch.object(runner, 'ROOT', control), patch.object(runner, 'SOURCE', stock), \
                patch.object(runner, 'PROFILE', control / profile_path), patch.dict(os.environ, env, clear=True):
            snapshot = runner.snapshot()
            assert not snapshot['problems'], snapshot
            assert snapshot['request'] == gate['request_binding'] and snapshot['request_sha256'] == gate['request_sha256']
    report = {'schema': 'stub-contract-push-invariance-v1', 'status': 'PASS', 'prior_packet_unchanged': True,
              'prior_review_and_GO_unchanged': True, 'prior_control_clean': True, 'delta_paths': delta,
              'runner_AST_functions_preserved': sorted(n for n in fa if n != 'snapshot'),
              'runner_changed_function': 'snapshot; exact projected adapter-only text checked',
              'invariant_files_sha256': invariant_files, 'stock_source_maps_equal': True,
              'compiler_setup_scripts_docs_root_lock_toolchain_unchanged': True,
              'workflow_jobs_after_dispatch_env_removal_equal': True, 'push_only_exact_filter': True,
              'schema_oracles_commands_caps_env_byte_or_structural_equal': True,
              'patch_replay': ['stock -> control', 'old125 -> new trigger-only delta'],
              'real_source_control_snapshot': 'PASS WITH SYNTHETIC_GITHUB_PUSH_PAYLOAD; CI NOT_RUN',
              'exact_candidate_final_gate': gate, 'actual_push': 'NOT_RUN'}
    if (HERE / 'INVARIANCE.json').exists():
        assert read(HERE / 'INVARIANCE.json') == report
    if (HERE / 'MANIFEST.json').exists():
        manifest = read(HERE / 'MANIFEST.json')
        paths = {str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and p.name != 'MANIFEST.json'}
        assert paths == {entry['path'] for entry in manifest['files']}
        for entry in manifest['files']:
            path = HERE / entry['path']
            assert path.stat().st_size == entry['bytes'] and runner.sha(path) == entry['sha256'], path
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify-only', action='store_true', help='Recheck identities/manifests/invariance without repeating the mock suite')
    args = parser.parse_args()
    report = static_checks()
    if not args.verify_only:
        env = os.environ | {'PYTHONDONTWRITEBYTECODE': '1'}
        process = subprocess.run([sys.executable, str(CODE / 'check_service.py')], env=env, check=True,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        service = json.loads(process.stdout)
    else:
        service = {'status': 'NOT_REPEATED', 'evidence': 'VALIDATION.json'}
    print(json.dumps({'status': 'PASS', 'scope': 'STATIC_PYTHON_DISPOSABLE_GIT_MOCK_ONLY', 'invariance': report,
                      'service': service, 'native_compiler_MIR_kani_cbmc_CI': 'NOT_RUN',
                      'publication_enable_ledger_budget_changes': False}, sort_keys=True))


if __name__ == '__main__':
    main()
