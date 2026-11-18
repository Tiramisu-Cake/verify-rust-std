#!/usr/bin/env python3
"""Read-only frozen YAML/metadata gate. Never runs CI, compiler or source tests."""
import copy
import difflib
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import yaml

PACKAGE = Path(__file__).resolve().parent
G0 = PACKAGE.parents[5]
SOURCE_REPO = Path('/root/kani-f4-fix-w15')
OLD = '7485bbb27a72dd463d4a9628c8627689d30e7e56'
REVIEW = 'cbfd888f274a0666f09af79d98ef4b8b8061f497'
SOURCE = 'cab66681c912a3e5ee01a106faaeee5237ca0232'
TREE = '8585336ed35a14fe0fc157a7ca4e0d52075c0e49'
BASE = 'faffcee3bca2770c03bd21c3bde89cc8f6f7a14e'
OLD_PATH = 'research/challenge-8/kani-k1/kani3300/wave0/f4-fix'
REVIEW_PATH = 'research/challenge-8/kani-k1/kani3300/wave0/f4-fix-review'
SIX = ['kani.yml', 'format-check.yml', 'deny.yml', 'verify-std-check.yml',
       'extra_jobs.yml', 'bench-pr.yml']


def git(repo, *args):
    return subprocess.check_output(['git', *args], cwd=repo)


def blob(repo, ref, path):
    return git(repo, 'show', ref + ':' + path)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def frozen_contract():
    names = git(SOURCE_REPO, 'ls-tree', '--name-only', SOURCE + ':.github/workflows').decode().splitlines()
    workflows = {name: yaml.load(blob(SOURCE_REPO, SOURCE, '.github/workflows/' + name),
                                Loader=yaml.BaseLoader) for name in names}
    applicable = {name: value for name, value in workflows.items()
                  if {'pull_request', 'pull_request_target'} & set(value['on'])}
    require(set(applicable) == set(SIX + ['release.yml']), 'unexpected applicable PR workflow set')
    require(all('workflow_dispatch' not in value['on'] for value in applicable.values()),
            'unexpected workflow_dispatch')
    jobs = workflows['release.yml']['jobs']
    builds = {}
    matrices = {}
    for name, job in jobs.items():
        if name in ('kani_release', 'package_docker'):
            continue
        require('if' not in job, 'required release job unexpectedly conditional')
        if 'strategy' in job:
            matrix = job['strategy']['matrix']
            require(set(matrix) == {'os', 'include'}, 'unsupported frozen matrix shape')
            require(len(matrix['os']) == len(set(matrix['os'])) == 5, 'five distinct OS values required')
            # Every include overlays an existing OS combination, adding no instance.
            require(all('os' not in row or row['os'] in matrix['os'] for row in matrix['include']),
                    'include adds an unexpected instance')
            matrices[name] = {'runs-on': job['runs-on'], 'needs': job['needs'], 'matrix': matrix}
        else:
            actions = [step for step in job['steps'] if step.get('uses') == './.github/actions/build-bundle']
            require(len(actions) == 1, 'not an actual bundle build')
            builds[name] = {'runs-on': job['runs-on'], 'platform': actions[0]['with']['platform']}
    require(len(builds) == 4 and set(matrices) == {'test_bundle', 'test-use-local-toolchain'},
            'wrong release build/test jobs')
    require(all(set(job['needs']) == set(builds) for job in matrices.values()), 'missing build dependency')
    require(jobs['kani_release']['if'] == "${{ github.event_name == 'push' && startsWith(github.ref, 'refs/tags/kani-') }}",
            'release publication is not tag-push gated')
    require(jobs['package_docker']['needs'] == 'kani_release' and 'if' not in jobs['package_docker'],
            'Docker publication dependency differs')
    instances = [{'job_id': name, 'os': job['runs-on']} for name, job in builds.items()]
    instances += [{'job_id': name, 'os': os} for name, job in matrices.items() for os in job['matrix']['os']]
    require(len(instances) == 14, 'not 14 PR instances')
    release = {
        'required_build_jobs': builds, 'required_test_matrices': matrices,
        'required_instances': instances, 'required_instance_count': len(instances),
        'intentional_pr_skips': {
            'kani_release': {key: jobs['kani_release'][key] for key in ('if', 'needs')},
            'package_docker': {'needs': jobs['package_docker']['needs'],
                               'reason': 'Dependency kani_release is tag-push gated and skipped on PR.'}}}
    return applicable, release


def plan_gate(plan, applicable, release):
    require(plan['source'] == SOURCE and plan['tree'] == TREE and plan['base'] == BASE,
            'source identities differ')
    require(plan['standard_pr_workflows'] == SIX + ['release.yml'], 'seven-workflow PR inventory differs')
    require(plan['native_events'] == {name: value['on'] for name, value in applicable.items()},
            'native event inventory differs')
    require(plan['release_pr_coverage'] == release, 'release build/matrix/instance/skip inventory differs')
    require(plan['fixed_runtime'] == 'NOT_RUN' and plan['attempts_consumed'] == 0 and
            plan['ledger_modified'] is False and plan['item1'] == {
                'used_reference': 27, 'cap_reference': 28, 'remaining_attempt_authorized': False},
            'runtime/authorization/accounting changed')
    require(plan['applicable_benchmark_labels'] == ['Z-EndToEndBenchCI', 'Z-CompilerBenchCI'],
            'benchmark labels differ')


def reject(plan, applicable, release):
    try:
        plan_gate(plan, applicable, release)
    except (ValueError, KeyError, TypeError):
        return
    raise ValueError('mutation unexpectedly accepted')


def check_manifest():
    manifest = json.loads((PACKAGE / 'MANIFEST.json').read_text())
    actual = {p.name for p in PACKAGE.iterdir() if p.is_file()} - {'MANIFEST.json'}
    require(actual == set(manifest['package_files']), 'package inventory differs')
    for name, expected in manifest['package_files'].items():
        require(sha((PACKAGE / name).read_bytes()) == expected, 'package hash differs: ' + name)
    for row in manifest['immutable_references']:
        data = blob(G0, row['commit'], row['path'])
        require(sha(data) == row['sha256'], 'immutable input hash differs')
        require((G0 / row['path']).read_bytes() == data, 'old package/review working bytes differ')
    print('PASS: exact package hashes and immutable old748/cbfd references')


def main():
    if sys.argv[1:] == ['--check-manifest']:
        check_manifest()
        return
    require(not sys.argv[1:], 'usage: validate_plan.py [--check-manifest]')
    require(git(SOURCE_REPO, 'rev-parse', 'HEAD').decode().strip() == SOURCE, 'source HEAD changed')
    require(git(SOURCE_REPO, 'rev-parse', SOURCE + '^{tree}').decode().strip() == TREE, 'source tree changed')
    require(git(SOURCE_REPO, 'rev-parse', SOURCE + '^').decode().strip() == BASE, 'source parent changed')
    require(git(SOURCE_REPO, 'status', '--porcelain') == b'', 'source worktree dirty')
    old_manifest = json.loads(blob(G0, OLD, OLD_PATH + '/MANIFEST.json'))
    for path, row in old_manifest['source_files'].items():
        require(sha(blob(SOURCE_REPO, SOURCE, path)) == row['sha256'], 'source/test bytes differ')
    require(len(old_manifest['preserved_standard_workflows']) == 16, 'not sixteen frozen workflows')
    for path, row in old_manifest['preserved_standard_workflows'].items():
        require(sha(blob(SOURCE_REPO, SOURCE, path)) == row['sha256'], 'workflow bytes differ')
    for path in ('.github', 'scripts'):
        require(git(SOURCE_REPO, 'rev-parse', SOURCE + ':' + path) ==
                git(SOURCE_REPO, 'rev-parse', BASE + ':' + path), 'standard workflow/scripts tree differs')
    applicable, release = frozen_contract()
    plan = json.loads((PACKAGE / 'CI-REQUEST.json').read_text())
    plan_gate(plan, applicable, release)
    old_plan = json.loads(blob(G0, OLD, OLD_PATH + '/CI-REQUEST.json'))
    reject(old_plan, applicable, release)
    rejected = ['old six-workflow request']
    for workflow in plan['standard_pr_workflows']:
        changed = copy.deepcopy(plan)
        changed['standard_pr_workflows'].remove(workflow)
        reject(changed, applicable, release)
        rejected.append('remove workflow ' + workflow)
    for job in release['required_build_jobs']:
        changed = copy.deepcopy(plan)
        del changed['release_pr_coverage']['required_build_jobs'][job]
        reject(changed, applicable, release)
        rejected.append('remove build ' + job)
    for job, matrix in release['required_test_matrices'].items():
        for os in matrix['matrix']['os']:
            changed = copy.deepcopy(plan)
            changed['release_pr_coverage']['required_test_matrices'][job]['matrix']['os'].remove(os)
            reject(changed, applicable, release)
            rejected.append('remove matrix OS ' + job + '/' + os)
    for instance in release['required_instances']:
        changed = copy.deepcopy(plan)
        changed['release_pr_coverage']['required_instances'].remove(instance)
        reject(changed, applicable, release)
        rejected.append('remove instance ' + instance['job_id'] + '/' + instance['os'])
    for mutation in ('drop_matrix_job', 'rename_build', 'artifact_route', 'native_event', 'skip_required'):
        changed = copy.deepcopy(plan)
        coverage = changed['release_pr_coverage']
        if mutation == 'drop_matrix_job':
            del coverage['required_test_matrices']['test_bundle']
        elif mutation == 'rename_build':
            coverage['required_build_jobs']['display-name'] = coverage['required_build_jobs'].pop('build_bundle_macos_x86_64')
        elif mutation == 'artifact_route':
            coverage['required_test_matrices']['test_bundle']['matrix']['include'][0]['prev_job'] = 'wrong artifact'
        elif mutation == 'native_event':
            del changed['native_events']['release.yml']['pull_request']
        else:
            coverage['intentional_pr_skips']['test_bundle'] = {'reason': 'release workflow'}
        reject(changed, applicable, release)
        rejected.append(mutation)
    expected_diff = ''.join(''.join(difflib.unified_diff(
        blob(G0, OLD, OLD_PATH + '/' + name).decode().splitlines(True),
        (PACKAGE / name).read_text().splitlines(True), fromfile='old748/f4-fix/' + name,
        tofile='new/f4-fix-plan-r1/' + name, n=0)) for name in ('CI-REQUEST.json', 'CI-REQUEST.md'))
    require((PACKAGE / 'METADATA.diff').read_text() == expected_diff, 'old-to-new request delta differs')
    print(json.dumps({
        'status': 'PASS', 'scope': 'STATIC_PLAN_DELTA_ONLY',
        'source': SOURCE, 'tree': TREE, 'base': BASE,
        'applicable_pr_workflows': plan['standard_pr_workflows'],
        'release_required_instance_count': len(release['required_instances']),
        'release_required_instances': release['required_instances'],
        'checks': ['exact source/test hashes and clean immutable source identity',
                   'all 16 workflow hashes and frozen .github/scripts trees unchanged',
                   'seven applicable PR workflows/native events derived from frozen YAML; no workflow_dispatch',
                   'four build jobs/platforms and both full five-OS matrices with artifact routes/needs',
                   'only tag-gated kani_release/dependent package_docker intentionally skip on PR',
                   'exact old-to-new CI request diff'],
        'rejected_mutation_count': len(rejected), 'rejected_mutations': rejected,
        'compiler_build': 'NOT_RUN', 'fixed_runtime': 'NOT_RUN', 'full_ci': 'NOT_RUN',
        'proof_credit': 'NONE', 'review14': 'PENDING_PLAN_DELTA_REVIEW',
        'attempts_consumed': 0, 'ledger_modified': False}, indent=2))


if __name__ == '__main__':
    main()
