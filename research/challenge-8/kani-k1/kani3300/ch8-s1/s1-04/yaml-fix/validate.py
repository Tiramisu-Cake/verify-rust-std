#!/usr/bin/env python3
"""Read-only YAML-fix closure; no network, compiler, proof or dispatch."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch
import yaml

CONTROL = Path('/root/kani-ch8-s1-04-yaml-w13')
STD = Path('/root/verify-rust-std-ch8-s1-04-w13')
TOOL = Path('/root/kani-upstream-ch8-s1')
OLD = '5fd538730869103cb7108cd823f58b1dac924960'
PARENT = '40b5d9cf48900ff1e227e1fbba24cb5b2edbf8d5'
CANDIDATE = '2a532e5913173d6af4490c25d74c587f7bf1a749'
sys.path.insert(0, str(CONTROL/'ch8-s1-control'))
import check_package
import runner


def git(*args):
    return subprocess.check_output(['git', '-C', str(CONTROL), *args], text=True).strip()


def main():
    assert git('rev-parse', 'HEAD') == CANDIDATE
    assert git('rev-list', '--parents', '-n', '1', 'HEAD').split() == [CANDIDATE, PARENT]
    assert '[skip ci]' not in git('log', '-1', '--format=%B').lower()
    assert git('log', '-1', '--format=%an <%ae>') == 'Tiramisu-Cake <igkharin@gmail.com>'
    changed = git('diff', '--name-only', OLD, 'HEAD').splitlines()
    expected = ['.github/workflows/ch8-s1.yml', 'ch8-s1-control/CI-REQUEST.json',
                'ch8-s1-control/check_package.py', 'ch8-s1-control/test_package.py']
    assert changed == expected
    request_path = CONTROL/'ch8-s1-control/CI-REQUEST.json'
    assert (Path(__file__).parent/'CI-REQUEST.json').read_bytes() == request_path.read_bytes()
    request = runner.load_request()
    prior = json.loads(git('show', OLD+':ch8-s1-control/CI-REQUEST.json'))
    assert {k:v for k,v in request.items() if k != 'ci_payload_sha256'} == {
        k:v for k,v in prior.items() if k != 'ci_payload_sha256'}
    updated = sorted(k for k,v in request['ci_payload_sha256'].items()
                     if prior['ci_payload_sha256'][k] != v)
    assert updated == [expected[0], expected[2], expected[3]]
    current = CONTROL/'.github/workflows/ch8-s1.yml'
    original = git('show', OLD+':.github/workflows/ch8-s1.yml')+'\n'
    assert yaml.load(original, Loader=yaml.BaseLoader) == yaml.load(
        current.read_text(), Loader=yaml.BaseLoader)
    with tempfile.TemporaryDirectory() as directory:
        old_yaml = Path(directory)/'old.yml'
        old_yaml.write_text(original)
        try:
            check_package.check_yaml(old_yaml)
        except AssertionError as exc:
            original_rejection = str(exc)
            assert 'concurrency.cancel-in-progress: expected native boolean' == original_rejection
        else:
            raise AssertionError('quoted workflow was accepted')
    yaml_result = check_package.check_yaml(current)
    env = {'GITHUB_REPOSITORY':'Tiramisu-Cake/kani', 'GITHUB_EVENT_NAME':'push',
           'GITHUB_REF':'refs/heads/uninit-ci/ch8-s1k-yaml-fix-static',
           'GITHUB_RUN_ATTEMPT':'1', 'GITHUB_SHA':CANDIDATE}
    with patch.dict(os.environ, env):
        control_result = check_package.control(CONTROL)
    source_result = runner.verify_source(STD, TOOL, request)
    return {'offline_closure':'PASS', 'control_sha':CANDIDATE,
            'control_parent':PARENT, 'control_tree':git('rev-parse', 'HEAD^{tree}'),
            'prior_control_sha':OLD, 'delta_paths':changed,
            'updated_payload_hash_paths':updated,
            'request_sha256':hashlib.sha256(request_path.read_bytes()).hexdigest(),
            'std_sha':source_result['std_sha'], 'tool_sha':source_result['tool_sha'],
            'yaml':yaml_result, 'prior_yaml_rejected':original_rejection,
            'workflow_values_and_schedule':'UNCHANGED_BASELOADER_DOCUMENT_EQUALITY',
            'control_preflight':control_result['status'],
            'control_environment':'LOCAL_SIMULATED_CI_ENV_READ_ONLY',
            'source_identity_preflight':'PASS_LOCAL_READ_ONLY',
            'scheduled_rows':len(request['rows']), 'groups':len(request['execution_groups']),
            'unions':len(request['replacement_unions']),
            'github_server_acceptance':'NOT_RUN', 'proof_execution':'NOT_RUN',
            'proof_credit':'NONE', 'dispatch':'NOT_RUN'}


if __name__ == '__main__':
    print(json.dumps(main(), indent=2))
