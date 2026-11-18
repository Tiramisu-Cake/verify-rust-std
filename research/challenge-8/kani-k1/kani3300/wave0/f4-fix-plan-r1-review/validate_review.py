#!/usr/bin/env python3
"""Read-only plan-delta review replay; no compiler, source tests or CI actions."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import yaml

HERE = Path(__file__).resolve().parent
G0 = HERE.parents[5]
PREFIX = 'research/challenge-8/kani-k1/kani3300/wave0/'
PACKAGE_PATH = PREFIX + 'f4-fix-plan-r1'
PACKAGE = G0 / PACKAGE_PATH
NEW = '9743a4a1d073e5c1591a1a20ab4756140241d57e'
OLD = '7485bbb27a72dd463d4a9628c8627689d30e7e56'
REVIEW = 'cbfd888f274a0666f09af79d98ef4b8b8061f497'
TASK = '4817b5ddf0c1526432b9c7fa3b16a9ba81a85bb7'
REPO = Path('/root/kani-f4-fix-w15')
SOURCE = 'cab66681c912a3e5ee01a106faaeee5237ca0232'
TREE = '8585336ed35a14fe0fc157a7ca4e0d52075c0e49'
BASE = 'faffcee3bca2770c03bd21c3bde89cc8f6f7a14e'
WORKFLOWS = ['kani.yml', 'format-check.yml', 'deny.yml', 'verify-std-check.yml',
             'extra_jobs.yml', 'bench-pr.yml', 'release.yml']
OS = ['macos-15-intel', 'macos-15', 'ubuntu-22.04', 'ubuntu-24.04', 'ubuntu-24.04-arm']
BUILDS = {
    'build_bundle_macos_x86_64': ('macos-15-intel', 'x86_64-apple-darwin'),
    'build_bundle_macos_aarch64': ('macos-15', 'aarch64-apple-darwin'),
    'build_bundle_linux_x86_64': ('ubuntu-22.04', 'x86_64-unknown-linux-gnu'),
    'build_bundle_linux_aarch64': ('ubuntu-24.04-arm', 'aarch64-unknown-linux-gnu'),
}


def git(repo, *args):
    return subprocess.check_output(['git', *args], cwd=repo)


def blob(repo, ref, path):
    return git(repo, 'show', ref + ':' + path)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def check(ok, reason):
    if not ok:
        raise ValueError(reason)


def main():
    check(not sys.argv[1:], 'no arguments supported')
    files = git(G0, 'ls-tree', '-r', '--name-only', NEW, '--', PACKAGE_PATH).decode().splitlines()
    check(len(files) == 9, 'not nine package files')
    hashes = {}
    for path in files:
        data = blob(G0, NEW, path)
        check((G0 / path).read_bytes() == data, 'uncommitted input: ' + path)
        hashes[Path(path).name] = digest(data)
    changed = git(G0, 'diff', '--name-status', TASK, NEW).decode().splitlines()
    check(set(changed) == {'A\t' + path for path in files}, 'delta extends beyond nine new files')
    old_counts = {}
    for ref, directory in [(OLD, 'f4-fix'), (REVIEW, 'f4-fix-review')]:
        paths = git(G0, 'ls-tree', '-r', '--name-only', ref, '--', PREFIX + directory).decode().splitlines()
        old_counts[directory] = len(paths)
        for path in paths:
            check(blob(G0, NEW, path) == blob(G0, ref, path) == (G0 / path).read_bytes(),
                  'historical input modified: ' + path)
    check(git(REPO, 'rev-parse', 'HEAD').decode().strip() == SOURCE, 'source HEAD changed')
    check(git(REPO, 'rev-parse', SOURCE + '^{tree}').decode().strip() == TREE, 'source tree changed')
    check(git(REPO, 'rev-parse', SOURCE + '^').decode().strip() == BASE, 'source parent changed')
    check(not git(REPO, 'status', '--porcelain'), 'source worktree dirty')
    old_manifest = json.loads(blob(G0, OLD, PREFIX + 'f4-fix/MANIFEST.json'))
    new_manifest = json.loads((PACKAGE / 'MANIFEST.json').read_text())
    for key in ['source_files', 'preserved_standard_workflows']:
        check(new_manifest[key] == old_manifest[key], 'source inventory changed')
        for path, row in old_manifest[key].items():
            check(digest(blob(REPO, SOURCE, path)) == row['sha256'], 'source bytes changed')
            check(git(REPO, 'rev-parse', SOURCE + ':' + path).decode().strip() == row['blob'],
                  'source blob changed')
    for path in ['.github', 'scripts']:
        check(git(REPO, 'rev-parse', SOURCE + ':' + path) == git(REPO, 'rev-parse', BASE + ':' + path),
              'workflow/script tree changed')
    names = git(REPO, 'ls-tree', '--name-only', SOURCE + ':.github/workflows').decode().splitlines()
    check(len(names) == 16, 'workflow count')
    docs = {name: yaml.load(blob(REPO, SOURCE, '.github/workflows/' + name), Loader=yaml.BaseLoader)
            for name in names}
    applicable = {name: doc for name, doc in docs.items()
                  if set(doc['on']) & {'pull_request', 'pull_request_target'}}
    check(set(applicable) == set(WORKFLOWS), 'applicable workflow set')
    check(all('workflow_dispatch' not in doc['on'] for doc in applicable.values()), 'dispatch claim')
    plan = json.loads((PACKAGE / 'CI-REQUEST.json').read_text())
    check(plan['standard_pr_workflows'] == WORKFLOWS, 'request workflow inventory')
    check(plan['native_events'] == {name: doc['on'] for name, doc in applicable.items()}, 'events differ')
    jobs = docs['release.yml']['jobs']
    coverage = plan['release_pr_coverage']
    matrices = ['test-use-local-toolchain', 'test_bundle']
    check(set(jobs) == set(BUILDS) | set(matrices) | {'kani_release', 'package_docker'}, 'release job IDs')
    check(set(coverage['required_build_jobs']) == set(BUILDS), 'build inventory')
    check(set(coverage['required_test_matrices']) == set(matrices), 'test inventory')
    expected_instances = []
    for name, (runner, platform) in BUILDS.items():
        job = jobs[name]
        check('if' not in job and job['runs-on'] == runner, 'conditional/wrong build runner')
        actions = [s for s in job['steps'] if s.get('uses') == './.github/actions/build-bundle']
        check(len(actions) == 1 and actions[0]['with']['platform'] == platform, 'build platform')
        check(coverage['required_build_jobs'][name] == {'runs-on': runner, 'platform': platform}, 'build request')
        expected_instances.append({'job_id': name, 'os': runner})
    expanded = {}
    for name in matrices:
        job = jobs[name]
        check('if' not in job and set(job['needs']) == set(BUILDS), 'conditional/missing test dependency')
        matrix = job['strategy']['matrix']
        check(set(matrix) == {'os', 'include'} and matrix['os'] == OS, 'full OS matrix')
        check(coverage['required_test_matrices'][name] == {
            'runs-on': job['runs-on'], 'needs': job['needs'], 'matrix': matrix}, 'matrix/route request')
        # Apply include rows to the original OS combinations; no row may add an instance.
        rows = [{'os': os} for os in OS]
        for include in matrix['include']:
            matches = [row for row in rows if 'os' not in include or row['os'] == include['os']]
            check(bool(matches), 'include adds instance')
            for row in matches:
                row.update(include)
        expanded[name] = rows
        expected_instances.extend({'job_id': name, 'os': row['os']} for row in rows)
    check(len(expected_instances) == coverage['required_instance_count'] == 14, '14-instance count')
    check(coverage['required_instances'] == expected_instances, '14-instance identity')
    check(jobs['kani_release']['if'] == "${{ github.event_name == 'push' && startsWith(github.ref, 'refs/tags/kani-') }}",
          'release skip predicate')
    check(jobs['package_docker']['needs'] == 'kani_release' and 'if' not in jobs['package_docker'], 'Docker skip')
    check(set(coverage['intentional_pr_skips']) == {'kani_release', 'package_docker'}, 'skip inventory')
    replay_raw = subprocess.check_output([sys.executable, str(PACKAGE / 'validate_plan.py')], cwd=G0)
    replay = json.loads(replay_raw)
    check(replay == json.loads((PACKAGE / 'VALIDATION.json').read_text()), 'recorded validation differs')
    manifest_replay = subprocess.check_output(
        [sys.executable, str(PACKAGE / 'validate_plan.py'), '--check-manifest'], cwd=G0).decode().strip()
    # Exercise the submitted gate with independently selected omissions, each from the intact plan.
    namespace = {'__file__': str(PACKAGE / 'validate_plan.py'), '__name__': 'review_gate_input'}
    exec(compile((PACKAGE / 'validate_plan.py').read_bytes(), str(PACKAGE / 'validate_plan.py'), 'exec'), namespace)
    namespace['plan_gate'](plan, applicable, coverage)
    rejected = []
    mutations = [('workflow', name) for name in WORKFLOWS] + [('build', name) for name in BUILDS]
    mutations += [('os', (name, os)) for name in matrices for os in OS]
    for kind, identity in mutations:
        candidate = copy.deepcopy(plan)
        if kind == 'workflow':
            candidate['standard_pr_workflows'].remove(identity)
        elif kind == 'build':
            del candidate['release_pr_coverage']['required_build_jobs'][identity]
        else:
            name, os = identity
            candidate['release_pr_coverage']['required_test_matrices'][name]['matrix']['os'].remove(os)
        try:
            namespace['plan_gate'](candidate, applicable, coverage)
        except ValueError:
            rejected.append({'kind': kind, 'identity': identity})
        else:
            raise ValueError('omission accepted: ' + str(identity))
    print(json.dumps({
        'status': 'PASS', 'scope': 'STATIC_CI_PLAN_DELTA_ONLY', 'package_commit': NEW,
        'source': SOURCE, 'tree': TREE, 'parent': BASE, 'package_files_checked': hashes,
        'historical_files_unchanged': old_counts, 'source_files_checked': len(old_manifest['source_files']),
        'preserved_workflow_count': len(names), 'applicable_pr_workflows': WORKFLOWS,
        'release_build_count': len(BUILDS), 'expanded_test_matrices': expanded,
        'release_required_instances': expected_instances, 'release_required_instance_count': 14,
        'author_replay_matches_committed_validation': True,
        'author_rejected_mutation_count': replay['rejected_mutation_count'],
        'author_manifest_replay': manifest_replay,
        'independent_omission_mutations_rejected': rejected,
        'independent_omission_mutation_count': len(rejected),
        'compiler_build': 'NOT_RUN', 'fixed_runtime': 'NOT_RUN', 'full_ci': 'NOT_RUN',
        'performance': 'NOT_RUN', 'proof_credit': 'NONE', 'attempts_consumed': 0,
        'ledger_modified': False}, indent=2))


if __name__ == '__main__':
    main()
