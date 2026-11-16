#!/usr/bin/env python3
"""Offline fix1 identity/scope audit. Git and Python only; no dispatch/proof."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

OLD = '242ca631743080daa98850d9d385a8079fbe581f'
CONTROL = '741b7183b4d6e9d752c0b7951206d7257f69f951'
REVIEW = '2ed50d63e09619470b53c1702f6ae987f4454b78'
TREE = '452b26330b97fc9b9816c28c64240bd667b2d4c0'
TOOL = '0aac16ef62da9e9d5645782d458593e5d78143ba'
DELTA = sorted(['.github/workflows/ch8-prof-off.yml',
                'ch8-prof-off-control/CI-REQUEST.json',
                'ch8-prof-off-control/check_package.py',
                'ch8-prof-off-control/workflow_repo.py',
                'ch8-prof-off-control/test_workflow_repo.py'])


def audit(repo):
    def git(*args):
        return subprocess.check_output(['git', '-C', str(repo), *args])
    assert git('rev-parse', 'HEAD').decode().strip() == CONTROL
    assert git('rev-parse', CONTROL+'^{tree}').decode().strip() == TREE
    assert git('rev-parse', REVIEW+'^{tree}').decode().strip() == TREE
    assert git('rev-list', '--parents', '-n', '1', CONTROL).decode().split() == [CONTROL, TOOL]
    assert git('rev-list', '--parents', '-n', '1', REVIEW).decode().split() == [REVIEW, OLD]
    assert not git('status', '--porcelain=v1').strip()
    assert sorted(git('diff', '--name-only', OLD, CONTROL).decode().splitlines()) == DELTA
    here = repo/'ch8-prof-off-control'
    request = json.loads((here/'CI-REQUEST.json').read_text())
    old_request = json.loads(git('show', OLD+':ch8-prof-off-control/CI-REQUEST.json'))
    exempt = {'ci_payload_sha256', 'ci_changed_paths'}
    assert {k:v for k,v in request.items() if k not in exempt} == {k:v for k,v in old_request.items() if k not in exempt}
    assert sorted(git('diff', '--name-only', TOOL, CONTROL).decode().splitlines()) == request['ci_changed_paths']
    expected_payload = set(old_request['ci_payload_sha256']) | {
        'ch8-prof-off-control/workflow_repo.py', 'ch8-prof-off-control/test_workflow_repo.py'}
    assert set(request['ci_payload_sha256']) == expected_payload
    for rel, digest in request['ci_payload_sha256'].items():
        assert hashlib.sha256((repo/rel).read_bytes()).hexdigest() == digest, rel
    for name in ('manifest.json', 'runner.py', 'kani-version.toml', 'test_profiles.py', 'test_runner.py', 'test_batch.py'):
        assert git('show', OLD+':ch8-prof-off-control/'+name) == (here/name).read_bytes(), name
    assert len(request['rows']) == 62
    sys.path.insert(0, str(here))
    spec = importlib.util.spec_from_file_location('fix1_check_package', here/'check_package.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    yaml_check = module.check_yaml(repo/'.github/workflows/ch8-prof-off.yml')
    return {'state':'PASS_STATIC_ONLY', 'control':CONTROL, 'control_tree':TREE,
            'control_parent':TOOL, 'review_candidate':REVIEW, 'review_baseline':OLD,
            'review_candidate_same_tree':True, 'delta_paths':DELTA,
            'frozen_request_except_payload_inventory':'IDENTICAL',
            'manifest_rows':62, 'manifest_sha256':request['manifest_sha256'],
            'control_request_sha256':hashlib.sha256((here/'CI-REQUEST.json').read_bytes()).hexdigest(),
            'yaml':yaml_check, 'qualification':'NOT_RUN', 'proof_credit':'NONE'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=Path, required=True)
    print(json.dumps(audit(parser.parse_args().repo.resolve()), indent=2))
