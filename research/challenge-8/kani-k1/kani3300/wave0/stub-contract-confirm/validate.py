#!/usr/bin/env python3
"""Check immutable packet content using static and Python synthetic operations."""
import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tomllib

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
CODE = HERE / 'source/tests/script-based-pre/stub-contract-confirm'
sys.path.insert(0, str(CODE))
import runner


def run():
    pins = json.loads((HERE / 'PINS.json').read_text())
    request = json.loads((HERE / 'CI-REQUEST.json').read_text())
    profile = json.loads((HERE / 'source/.github/stub-contract-confirm/profile.json').read_text())
    control, stock = Path(pins['control']['worktree']), Path(pins['stock']['worktree'])
    assert runner.sha(HERE / 'control.patch') == pins['control_patch_sha256']
    assert runner.sha(HERE / 'fix-clear-error.patch') == pins['fix_candidate_patch_sha256']
    for label, root in [('control_sha256', HERE / 'source'), ('source_sha256', stock)]:
        for path, digest in profile[label].items():
            assert runner.sha(root / path) == digest, path
    assert runner.sha(HERE / 'source/.github/stub-contract-confirm/profile.json') == pins['profile_sha256']
    assert request['request_binding'] == request['binding'] == pins['request_binding']
    assert request['profile_sha256'] == pins['profile_sha256']
    assert request['patch_sha256'] == pins['control_patch_sha256']
    assert hashlib.sha256(runner.canonical(pins['request_binding'])).hexdigest() == pins['request_sha256']
    sources = json.loads((HERE / 'SOURCES.json').read_text())
    for entry in sources['files']:
        assert runner.sha(stock / entry['path']) == entry['sha256']
        assert runner.git(stock, 'rev-parse', 'HEAD:' + entry['path']) == entry['git_blob']
    for entry in sources['objects']:
        raw = subprocess.check_output(['git', '-C', str(stock), 'cat-file', entry['kind'], entry['git_sha1']])
        assert len(raw) == entry['bytes'] and hashlib.sha256(raw).hexdigest() == entry['content_sha256']
    diff = subprocess.check_output(['git', '-C', str(control), 'diff', '--binary', runner.BASE, 'HEAD'])
    assert hashlib.sha256(diff).hexdigest() == pins['control_patch_sha256']
    for role, root in [('control', control), ('stock', stock)]:
        for key, ref in [('head', 'HEAD'), ('tree', 'HEAD^{tree}'), ('parent', 'HEAD^')]:
            assert runner.git(root, 'rev-parse', ref) == pins[role][key]
        assert runner.git(root, 'status', '--porcelain') == '', role + ' dirty'
    for path, digest in profile['control_sha256'].items():
        assert runner.sha(control / path) == digest
        runner.git(control, 'ls-files', '--error-unmatch', path)
    assert runner.git(control, 'diff', '--name-only', runner.BASE, 'HEAD', '--',
                      'kani-compiler', 'kani-driver', 'library', 'rust-toolchain.toml', 'Cargo.lock') == ''
    for patch in ('control.patch', 'fix-clear-error.patch'):
        subprocess.run(['git', '-C', str(stock), 'apply', '--check', str(HERE / patch)], check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    manifest = tomllib.loads((CODE / 'Cargo.toml').read_text())
    assert not any(manifest.get(k) for k in ('dependencies', 'dev-dependencies', 'build-dependencies'))
    assert manifest['workspace'] == {} and set(manifest['features']) == set(runner.SLOTS)
    assert len(list((HERE / 'source').rglob('Cargo.toml'))) == 1
    for file in (HERE / 'source').rglob('*.py'):
        ast.parse(file.read_text(), filename=str(file))
    result = json.loads((HERE / 'result.json').read_text())
    digest = result.pop('integrity')
    assert hashlib.sha256(runner.canonical(result)).hexdigest() == digest['canonical_payload_sha256']
    result['integrity'] = digest
    assert result['classification'] == 'INCONCLUSIVE' and result['reasons'] == ['NOT_RUN']
    assert all(slot['observation']['outcome'] == 'NOT_RUN' for slot in result['slots'].values())
    schema = json.loads((HERE / 'result.schema.json').read_text())
    # jsonschema is available in the preparation environment; native CI uses producer validation.
    import jsonschema
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(result, schema)
    env = os.environ | {'PYTHONDONTWRITEBYTECODE': '1', 'SC_CONTROL_HEAD': pins['control']['head'],
                        'SC_CONTROL_TREE': pins['control']['tree'], 'SC_REQUEST_SHA256': pins['request_sha256']}
    from unittest.mock import patch
    with patch.object(runner, 'ROOT', control), patch.object(runner, 'SOURCE', stock), \
            patch.object(runner, 'PROFILE', control / '.github/stub-contract-confirm/profile.json'), patch.dict(os.environ, env):
        before = runner.snapshot()
        assert not before['problems'], before
    service = subprocess.run([sys.executable, str(CODE / 'check_service.py')], env=env, check=True,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    tests = json.loads(service.stdout)
    import check_service
    changed_tools = check_service.state()
    changed_tools['source_after']['tools'] = {'compiler': 'changed'}
    assert runner.classify(changed_tools)[0] == 'INCONCLUSIVE'
    manifest_path = HERE / 'MANIFEST.json'
    if manifest_path.exists():
        for entry in json.loads(manifest_path.read_text())['files']:
            path = HERE / entry['path']
            assert path.stat().st_size == entry['bytes'] and runner.sha(path) == entry['sha256'], path
    return {'status': 'PASS', 'scope': 'STATIC_PYTHON_MOCK_ONLY', 'service': tests,
            'source_preflight': before, 'patch_apply_checks': ['control.patch', 'fix-clear-error.patch'],
            'schema': 'Draft202012 PASS; prepared result NOT_RUN',
            'native_main': 'NOT_RUN', 'native_fixed': 'NOT_RUN', 'CI': 'NOT_RUN',
            'ledger_or_accounting_changes': False}


if __name__ == '__main__':
    report = run()
    print(json.dumps(report, sort_keys=True))
