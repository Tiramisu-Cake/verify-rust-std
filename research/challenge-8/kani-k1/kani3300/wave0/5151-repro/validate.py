#!/usr/bin/env python3
# Copyright Kani Contributors
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Check package identities and reconstruct the control tree without compiling."""

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile


HERE = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(repo, *args, env=None):
    return subprocess.run(
        ['git', '-C', str(repo), *args], check=True, env=env,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    ).stdout


def validate(control):
    request = json.loads((HERE / 'CI-REQUEST.json').read_text())
    identity = request['control']
    assert git(control, 'rev-parse', 'HEAD').decode().strip() == identity['sha']
    assert git(control, 'rev-parse', 'HEAD^{tree}').decode().strip() == identity['tree']
    assert not git(control, 'status', '--porcelain=v1', '--untracked-files=no')
    message = git(control, 'show', '-s', '--format=%B', identity['sha']).decode()
    assert '[skip ci]' in message
    author = git(control, 'show', '-s', '--format=%an <%ae>', identity['sha']).decode().strip()
    assert author == 'Tiramisu-Cake <igkharin@gmail.com>'
    assert digest(control / identity['request_path']) == identity['request_sha256']
    control_request = json.loads((control / identity['request_path']).read_text())
    assert request['part1'] == control_request
    for relative, expected in control_request['payload_sha256'].items():
        assert digest(control / relative) == expected, relative

    patch = HERE / 'CONTROL.patch'
    assert digest(patch) == identity['patch_sha256']
    assert patch.read_bytes() == git(control, 'diff', '--binary', identity['base_sha'], identity['sha'])
    with tempfile.TemporaryDirectory(prefix='ch8-5151-index-') as directory:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(directory) / 'index'))
        git(control, 'read-tree', identity['base_sha'], env=env)
        git(control, 'apply', '--cached', '--whitespace=nowarn', str(patch), env=env)
        assert git(control, 'write-tree', env=env).decode().strip() == identity['tree']

    test_directory = Path('tests/expected/uninit/issue-5151')
    test_files = sorted((control / test_directory).iterdir())
    assert len(test_files) == 6
    for path in test_files:
        assert (HERE / test_directory / path.name).read_bytes() == path.read_bytes(), path
    original = (HERE / test_directory / 'original-empty-drop.rs').read_text()
    issue_code = original[original.index('use core::mem::MaybeUninit;'):]
    source = json.loads((HERE / 'SOURCES.json').read_text())
    assert hashlib.sha256(issue_code.encode()).hexdigest() == source['reproducer_utf8_sha256']

    challenge2 = json.loads((HERE / 'CHALLENGE2-SOURCES.json').read_text())
    for relative, expected in challenge2['inventory_sha256'].items():
        assert digest(HERE / relative) == expected, relative
    with (HERE / 'challenge2-candidates.csv').open() as stream:
        candidates = list(csv.DictReader(stream))
    assert len(candidates) == challenge2['candidate_count'] == 56
    assert len({row['fully_qualified_harness_id'] for row in candidates}) == 56
    with (HERE / 'challenge2-static-harnesses.csv').open() as stream:
        ids = list(csv.DictReader(stream))
    assert len(ids) == challenge2['static_harnesses_count'] == 393
    assert all(value == 0 for value in request['accounting'].values())
    return {
        'state': 'PASS_STATIC_ONLY', 'control_sha': identity['sha'],
        'control_tree': identity['tree'], 'patch_reconstruction': 'EXACT_TREE_MATCH',
        'test_files_identical': len(test_files), 'original_issue_body': 'BYTE_IDENTICAL',
        'source_candidates': len(candidates), 'static_harness_ids': len(ids),
        'runtime': 'NOT_RUN', 'proof_obligations_closed': 0,
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--control', type=Path)
    arguments = parser.parse_args()
    request = json.loads((HERE / 'CI-REQUEST.json').read_text())
    control = arguments.control or Path(request['control']['worktree'])
    print(json.dumps(validate(control), indent=2))
