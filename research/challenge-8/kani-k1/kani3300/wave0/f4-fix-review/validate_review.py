#!/usr/bin/env python3
"""Bounded independent static/oracle review; no native compiler or CI calls."""
import ast
import contextlib
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch as mock_patch

import yaml

OUT = Path(__file__).resolve().parent
PACKAGE = OUT.parent / 'f4-fix'
G0 = OUT.parents[5]
SOURCE = Path('/root/kani-f4-fix-w15')
PACKAGE_COMMIT = '7485bbb27a72dd463d4a9628c8627689d30e7e56'
HEAD = 'cab66681c912a3e5ee01a106faaeee5237ca0232'
TREE = '8585336ed35a14fe0fc157a7ca4e0d52075c0e49'
BASE = 'faffcee3bca2770c03bd21c3bde89cc8f6f7a14e'
checks = []


def git(repo, *args, env=None):
    return subprocess.check_output(['git', *args], cwd=repo, env=env)


def passed(name):
    checks.append(name)


def sha(data):
    return hashlib.sha256(data).hexdigest()


manifest = json.loads((PACKAGE / 'MANIFEST.json').read_text())
assert git(SOURCE, 'rev-parse', 'HEAD').decode().strip() == HEAD
assert git(SOURCE, 'rev-parse', 'HEAD^{tree}').decode().strip() == TREE
assert git(SOURCE, 'rev-parse', 'HEAD^').decode().strip() == BASE
assert git(SOURCE, 'status', '--porcelain') == b''
assert manifest['source'] == HEAD and manifest['source_tree'] == TREE
assert manifest['base'] == manifest['source_parent'] == BASE
assert git(SOURCE, 'show', '-s', '--format=%an <%ae>', HEAD).decode().strip() == 'Tiramisu-Cake <igkharin@gmail.com>'
assert '[skip ci]' in git(SOURCE, 'show', '-s', '--format=%B', HEAD).decode()
passed('exact clean source HEAD/tree/direct parent/author/skip directive')

package_paths = sorted(p for p in PACKAGE.iterdir() if p.is_file())
assert len(package_paths) == 14
for path in package_paths:
    relative = str(path.relative_to(G0))
    assert path.read_bytes() == git(G0, 'show', PACKAGE_COMMIT + ':' + relative)
    if path.name != 'MANIFEST.json':
        assert sha(path.read_bytes()) == manifest['package_files'][path.name]
for relative, identity in manifest['inputs'].items():
    assert sha((G0 / 'research/challenge-8/kani-k1' / relative).read_bytes()) == identity['sha256']
passed('all 14 package files match exact package commit; manifest and dependency hashes')

changed = git(SOURCE, 'diff', '--name-only', BASE, HEAD).decode().splitlines()
assert sorted(changed) == sorted(manifest['source_files']) and len(changed) == 9
for relative, identity in manifest['source_files'].items():
    data = git(SOURCE, 'show', HEAD + ':' + relative)
    assert sha(data) == identity['sha256']
    assert git(SOURCE, 'rev-parse', HEAD + ':' + relative).decode().strip() == identity['blob']
assert git(SOURCE, 'diff', '--check', BASE, HEAD) == b''
assert git(SOURCE, 'diff', BASE, HEAD, '--', '.github', 'scripts', 'library', 'rust-toolchain.toml', 'Cargo.lock', 'kani-dependencies') == b''
for relative, identity in manifest['preserved_standard_workflows'].items():
    assert git(SOURCE, 'show', BASE + ':' + relative) == git(SOURCE, 'show', HEAD + ':' + relative)
    assert sha(git(SOURCE, 'show', HEAD + ':' + relative)) == identity['sha256']
assert len(manifest['preserved_standard_workflows']) == 16
passed('nine-file scope; all 16 workflows and all scripts/library/toolchain/dependency pins unchanged')

patch = git(SOURCE, 'diff', '--binary', '--full-index', BASE, HEAD)
assert sha(patch) == manifest['patch_sha256'] and patch == (PACKAGE / 'fix.patch').read_bytes()
regression = git(SOURCE, 'diff', '--binary', '--full-index', BASE, HEAD, '--', 'tests')
assert regression == (PACKAGE / 'regression-main.patch').read_bytes()
assert sha(regression) == manifest['regression_main_patch_sha256']
with tempfile.TemporaryDirectory(dir=OUT) as temporary:
    env = dict(os.environ, GIT_INDEX_FILE=str(Path(temporary) / 'index'))
    git(SOURCE, 'read-tree', BASE, env=env)
    subprocess.run(['git', 'apply', '--cached', str(PACKAGE / 'regression-main.patch')], cwd=SOURCE, env=env, check=True)
    assert git(SOURCE, 'diff', '--cached', '--name-only', BASE, env=env).decode().splitlines() == sorted(p for p in changed if p.startswith('tests/'))
    assert git(SOURCE, 'diff', '--cached', BASE, '--', 'kani-compiler', env=env) == b''
passed('exact patch bytes and regression-only main patch; isolated-index regression replay')

# Replay the author's checks with only scratch/output destinations redirected.
# Preserve PACKAGE for all immutable inputs. The checked native probe is mocked.
author = (PACKAGE / 'validate.py').read_text()
assert author.count('tempfile.TemporaryDirectory(dir=PACKAGE)') == 2
assert author.count("(PACKAGE / 'VALIDATION.json').write_text") == 1
adapted = author.replace('tempfile.TemporaryDirectory(dir=PACKAGE)', 'tempfile.TemporaryDirectory(dir=OUTPUT)')
adapted = adapted.replace("(PACKAGE / 'VALIDATION.json').write_text", "(OUTPUT / 'AUTHOR-REPLAY.json').write_text")
namespace = {'__file__': str(PACKAGE / 'validate.py'), '__name__': 'review_author_replay', 'OUTPUT': OUT}
saved = sys.argv
try:
    sys.argv = [str(PACKAGE / 'validate.py'), str(SOURCE)]
    exec(compile(ast.parse(adapted), str(PACKAGE / 'validate.py'), 'exec'), namespace)
finally:
    sys.argv = saved
passed('author static/oracle/error-path checks independently replayed; original package unchanged')

# Exercise the seven-invocation orchestration using only retained or synthetic data.
# Native probe/main entry points stay mocked; scratch files stay in review scope.
oracle = namespace['ns']
original_temp = tempfile.TemporaryDirectory
with mock_patch.dict(os.environ, CARGO_ENCODED_RUSTFLAGS='inherited', CARGO_TARGET_DIR='inherited',
                     CARGO_BUILD_TARGET='inherited', RUSTFLAGS='inherited', KANIFLAGS='inherited'):
    for dataset, expected_success in ((namespace['runs'], False), (namespace['synthetic'], True)):
        calls = []
        def retained_probe(command, wanted, export, env):
            assert all(key not in env for key in ('CARGO_ENCODED_RUSTFLAGS', 'CARGO_TARGET_DIR', 'CARGO_BUILD_TARGET'))
            assert env['KANIFLAGS'] == '' and env['KANI_LOG'] == '' and env['NO_COLOR'] == '1'
            target = Path(command[command.index('--target-dir') + 1])
            assert OUT in target.parents and target not in [row[0] for row in calls]
            if command[0] == 'kani':
                label = 'uninitialized_control'
                assert wanted == ['uninitialized_control'] and env['RUSTFLAGS'] == '--edition=2021'
            else:
                assert command[:2] == ['cargo', 'kani'] and env['RUSTFLAGS'] == ''
                mode = 'delayed_first' if '--features' in command else 'control_first'
                if '--features' in command:
                    assert command[-2:] == ['--features', 'delayed-first']
                case = {tuple(oracle['NAMES']): 'paired', tuple(oracle['NAMES'][:1]): 'delayed_alone',
                        tuple(oracle['NAMES'][1:]): 'control_alone'}[tuple(wanted)]
                label = mode + '/' + case
            calls.append((target, label))
            return copy.deepcopy(dataset[label])
        def review_temporary(*args, **kwargs):
            return original_temp(*args, dir=OUT, **kwargs)
        with mock_patch.dict(oracle, probe=retained_probe), mock_patch.object(tempfile, 'TemporaryDirectory', review_temporary):
            with contextlib.redirect_stdout(io.StringIO()) as output:
                try:
                    oracle['main']()
                except ValueError as error:
                    assert not expected_success and str(error) == 'initialized harness failed'
                else:
                    assert expected_success
            assert len(calls) == 7 and {row[1] for row in calls} == set(dataset)
            assert bool(output.getvalue()) == expected_success
passed('mocked seven-invocation entry point: observed main rejected at initialized assertion; synthetic fixed accepted; cfg/targets/environment checked')

# Parse YAML with BaseLoader so the GitHub Actions key "on" remains a string.
workflows = {}
for path in sorted((SOURCE / '.github/workflows').glob('*.yml')):
    workflows[path.name] = yaml.load(path.read_text(), Loader=yaml.BaseLoader)
assert len(workflows) == 16
assert set(workflows['kani.yml']['on']) == {'pull_request', 'merge_group', 'push'}
assert workflows['kani.yml']['jobs']['regression']['strategy']['matrix']['os'] == ['macos-15-intel', 'ubuntu-22.04', 'ubuntu-24.04', 'macos-15', 'ubuntu-24.04-arm']
assert set(workflows['kani.yml']['jobs']) == {'regression', 'benchcomp-tests', 'perf', 'llbc-regression', 'documentation'}
assert set(workflows['format-check.yml']['jobs']) == {'format-check', 'clippy-check'}
assert set(workflows['deny.yml']['jobs']) == {'audit'}
assert workflows['verify-std-check.yml']['jobs']['verify-std']['strategy']['matrix']['os'] == ['ubuntu-22.04', 'macos-15']
assert workflows['bench-pr.yml']['on']['pull_request']['types'] == ['opened', 'synchronize', 'reopened', 'labeled']
assert set(workflows['extra_jobs.yml']['on']) == {'pull_request_target', 'merge_group'}
assert set(workflows['extra_jobs.yml']['jobs']) == {'auto-label'}
labeler = yaml.load((SOURCE / '.github/labeler.yml').read_text(), Loader=yaml.BaseLoader)
for label in ('Z-EndToEndBenchCI', 'Z-CompilerBenchCI'):
    assert 'kani-compiler/**' in labeler[label][0]['any'][0]['changed-files'][0]['any-glob-to-any-file']
assert set(workflows['bench-compiler.yml']['jobs']) == {'compile-timer-short', 'compile-timer-long'}
assert set(workflows['bench-e2e.yml']['jobs']) == {'perf-benchcomp'}
for name in ('bench-compiler.yml', 'bench-e2e.yml'):
    text = (SOURCE / '.github/workflows' / name).read_text()
    assert 'github.event.pull_request.head.sha' in text and 'github.event.pull_request.base.sha' in text
    assert 'ref: ${{ env.NEW_REF }}' in text
for name in ('kani.yml', 'format-check.yml', 'deny.yml', 'verify-std-check.yml'):
    assert 'pull_request' in workflows[name]['on']
request = json.loads((PACKAGE / 'CI-REQUEST.json').read_text())
assert request['source'] == HEAD and request['tree'] == TREE and request['base'] == BASE
assert set(request['standard_pr_workflows']) == {'kani.yml', 'format-check.yml', 'deny.yml', 'verify-std-check.yml', 'extra_jobs.yml', 'bench-pr.yml'}
assert all('workflow_dispatch' not in workflows[name]['on'] for name in request['standard_pr_workflows'])
assert 'script-based-pre exec' in (SOURCE / 'scripts/kani-regression.sh').read_text()
applicable = {name for name, workflow in workflows.items()
              if set(workflow['on']) & {'pull_request', 'pull_request_target'}}
missing = sorted(applicable - set(request['standard_pr_workflows']))
assert missing == ['release.yml']
release = workflows['release.yml']['jobs']
build_jobs = sorted(name for name in release if name.startswith('build_bundle_'))
assert len(build_jobs) == 4
release_matrix = ['macos-15-intel', 'macos-15', 'ubuntu-22.04', 'ubuntu-24.04', 'ubuntu-24.04-arm']
for name in ('test_bundle', 'test-use-local-toolchain'):
    assert release[name]['strategy']['matrix']['os'] == release_matrix
    assert sorted(release[name]['needs']) == build_jobs
assert release['kani_release']['if'] == "${{ github.event_name == 'push' && startsWith(github.ref, 'refs/tags/kani-') }}"
assert release['package_docker']['needs'] == 'kani_release'
passed('all 16 native trigger sets inspected: seven PR workflows; confirmed plan omission of release.yml with 14 required build/test matrix instances and intended publication skips')

assert git(SOURCE, 'status', '--porcelain') == b''
for path in package_paths:
    assert path.read_bytes() == git(G0, 'show', PACKAGE_COMMIT + ':' + str(path.relative_to(G0)))
result = dict(status='PASS', assurance='STATIC_AND_SYNTHETIC_ONLY', package_commit=PACKAGE_COMMIT,
              source=HEAD, tree=TREE, base=BASE, checks=checks,
              fixed_runtime='NOT_RUN', main_new_test_runtime='NOT_RUN', compiler_build='NOT_RUN',
              actual_compilation_order='UNKNOWN', actual_runtime_causality='UNKNOWN', proof_credit='NONE',
              author_replay_sha256=sha((OUT / 'AUTHOR-REPLAY.json').read_bytes()),
              package_manifest_sha256=sha((PACKAGE / 'MANIFEST.json').read_bytes()),
              native_tools_called=False, ci_called=False, original_package_unchanged=True,
              review_verdict='CHANGES_REQUIRED', missing_pr_workflows=missing,
              blocking_findings=[dict(id='F4-R14-1', priority='P2', owner='original15',
                                     issue='Full-standard-CI plan omits release.yml PR bundle build and test matrices')])
(OUT / 'VALIDATION.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(dict(status='PASS', independent_checks=len(checks), fixed_runtime='NOT_RUN',
                      review_verdict='CHANGES_REQUIRED', missing_pr_workflows=missing)))
