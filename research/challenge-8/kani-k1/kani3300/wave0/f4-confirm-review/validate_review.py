"""Independent static and synthetic validation of the immutable F4 candidate."""
import ast
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch

OUT = Path(__file__).resolve().parent
PACKAGE = OUT.parent / 'f4-confirm'
G0 = PACKAGE.parents[5]
SOURCE = Path('/root/kani-f4-confirm-w15')
CANDIDATE = '1bd7d58e6cafc64c36c4012651751c038d3e9c64'
MAIN = 'faffcee3bca2770c03bd21c3bde89cc8f6f7a14e'
CONTROL = '1ec3318f5e2c39afb701aa7a5578d4ea0a721224'
TREE = '34a402bd4ebbabf3ec611327097475c8cb46cfba'
FIXTURE = SOURCE / 'tests/script-based-pre/delayed-shared-body'
CHECKS = []


def command(argv, cwd=SOURCE, env=None):
    try:
        return subprocess.check_output(argv, cwd=cwd, stderr=subprocess.PIPE, env=env)
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(exc.stderr.decode(errors='replace')) from exc


def git(*args, cwd=SOURCE, env=None):
    return command(['git', *args], cwd=cwd, env=env).decode().strip()


def digest(value):
    return hashlib.sha256(value).hexdigest()


def record(name, details):
    CHECKS.append({'name': name, 'status': 'PASS', 'details': details})


assert git('rev-parse', 'HEAD') == CONTROL
assert git('rev-parse', 'HEAD^{tree}') == TREE
assert git('show', '-s', '--format=%P', CONTROL) == MAIN
assert git('rev-parse', MAIN + '^{tree}') == '09b828b47c93e90e140e8c41f9048109a2f4a786'
assert not git('status', '--porcelain=v1')
prefix = str(PACKAGE.relative_to(G0))
files = git('ls-tree', '-r', '--name-only', CANDIDATE, '--', prefix, cwd=G0).splitlines()
assert len(files) == 25
for path in files:
    assert (G0 / path).read_bytes() == command(['git', 'show', CANDIDATE + ':' + path], cwd=G0)
assert not git('diff', CANDIDATE, 'HEAD', '--', prefix, cwd=G0)
manifest = json.loads((PACKAGE / 'SOURCES.json').read_text())
for path, entry in manifest['files'].items():
    value = (PACKAGE / entry['package_path']).read_bytes()
    assert digest(value) == entry['sha256']
    assert value == command(['git', 'show', CONTROL + ':' + path]) == (SOURCE / path).read_bytes()
    assert git('ls-tree', CONTROL, '--', path).split()[0] == entry['mode']
assert digest((PACKAGE / 'control.patch').read_bytes()) == manifest['patch_sha256']
profile = json.loads((SOURCE / '.github/f4-confirm/profile.json').read_text())
for path, expected in profile['source_sha256'].items():
    assert digest((SOURCE / path).read_bytes()) == expected
request = json.loads((PACKAGE / 'CI-REQUEST.json').read_text())
assert request['caps'] == profile['caps']
assert request['profile']['sha256'] == digest((SOURCE / '.github/f4-confirm/profile.json').read_bytes())
assert request['workflow']['sha256'] == digest((SOURCE / request['workflow']['file']).read_bytes())
assert request['validation']['sha256'] == digest((PACKAGE / 'VALIDATION.json').read_bytes())
assert request['validation']['diagnosis_sha256'] == digest((PACKAGE / 'DIAGNOSIS.json').read_bytes())
assert request['validation']['source_trace_sha256'] == digest((PACKAGE / 'SOURCE-TRACE.json').read_bytes())
assert request['validation']['source_manifest_sha256'] == digest((PACKAGE / 'SOURCES.json').read_bytes())
trace = json.loads((PACKAGE / 'SOURCE-TRACE.json').read_text())
for revision, paths in trace['sha256'].items():
    for path, expected in paths.items():
        assert digest(command(['git', 'show', revision + ':' + path])) == expected
record('exact_bytes_and_pins', {'committed_package_files': len(files), 'source_files': len(manifest['files']),
                               'main': MAIN, 'control': CONTROL, 'tree': TREE,
                               'source_trace_hashes': 'both revisions match'})

with tempfile.TemporaryDirectory(dir=OUT, prefix='.patch-') as temporary:
    repo = Path(temporary)
    git('init', '-q', cwd=repo)
    common = Path(git('rev-parse', '--git-common-dir')).resolve()
    (repo / '.git/objects/info/alternates').write_text(str(common / 'objects') + '\n')
    git('read-tree', MAIN, cwd=repo)
    git('apply', '--cached', '--binary', str(PACKAGE / 'control.patch'), cwd=repo)
    assert git('write-tree', cwd=repo) == TREE
record('patch_reconstruction', {'tree': TREE, 'isolated_index_and_objects': True})

for path in FIXTURE.glob('*.py'):
    ast.parse(path.read_text(), filename=str(path))
command(['bash', '-n', str(FIXTURE / 'test.sh')])
git('diff', '--check', MAIN, CONTROL)
git('diff', '--check', CANDIDATE + '^', CANDIDATE, '--', prefix, cwd=G0)
import yaml
workflow = yaml.safe_load((SOURCE / request['workflow']['file']).read_text())
job = workflow['jobs']['confirm']
assert job['timeout-minutes'] == profile['caps']['job_minutes']
assert sum('uses' in step and 'upload-artifact@' in step['uses'] for step in job['steps']) == 1
assert 7 * 120 < profile['caps']['probe_step_minutes'] * 60
assert 30 * 60 + 16 * 60 + 16 * 60 < 90 * 60
service_env = os.environ | {'PYTHONDONTWRITEBYTECODE': '1'}
service = json.loads(command([sys.executable, str(FIXTURE / 'check_service.py')], env=service_env))
assert service['status'] == 'PASS'
record('syntax_workflow_caps_and_author_service_controls', service)

sys.path.insert(0, str(FIXTURE))
import runner
from service import execute, regular_inventory
with tempfile.TemporaryDirectory(dir=OUT, prefix='.shallow-') as temporary:
    checkout = Path(temporary) / 'source'
    git('clone', '-q', '--depth=3', '--no-checkout', '--reference', str(common),
        '--branch', 'w15/f4-confirm-main-20261117', common.as_uri(), str(checkout))
    git('checkout', '-q', '--detach', CONTROL, cwd=checkout)
    with patch.object(runner, 'ROOT', checkout), patch.object(runner, 'PROFILE', checkout / '.github/f4-confirm/profile.json'), \
            patch.dict(os.environ, {'F4_PROFILE_SHA256': request['profile']['sha256']}):
        snapshot = runner.snapshot()
        assert snapshot['problems'] == [] and snapshot['shallow'] == 'true'
        assert snapshot['control'] == CONTROL and snapshot['tree'] == TREE
record('actual_depth_three_control_preflight', snapshot)

# Execute the author's fixture constructors and synthetic tests in memory; no native runner.
namespace = {'__name__': 'f4_review_synthetic', '__file__': str(FIXTURE / 'check_service.py')}
import contextlib
import io
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile((FIXTURE / 'check_service.py').read_text(), str(FIXTURE / 'check_service.py'), 'exec'), namespace)
sample = namespace['sample']
doc, native = sample(runner.NAMES)
for entry in doc['harnesses']:
    prop = entry['unsupported_constructs'][0]
    prop['status'] = 'UNREACHABLE'
    entry['checks']['success'] -= 1
    entry['checks']['unreachable'].append(prop['id'])
    next(p for p in native['property_inventory'][entry['name']] if p['id'] == prop['id'])['status'] = 'UNREACHABLE'
assert runner.parse_document(doc, runner.NAMES, native)

with tempfile.TemporaryDirectory(dir=OUT, prefix='.native-') as temporary:
    root = Path(temporary)
    long_error = execute([sys.executable, '-c',
        'import sys; print("BEGIN_ERROR", file=sys.stderr); '
        '[print("x"*150, file=sys.stderr) for _ in range(300)]; '
        'print("FINAL_ERROR", file=sys.stderr); sys.exit(73)'], root, 2)
    assert long_error['exit'] == 73 and long_error['stderr_first_lines'][0] == 'BEGIN_ERROR'
    assert long_error['stderr_tail'][-1] == 'FINAL_ERROR'
    assert len(long_error['stderr_first_lines']) <= 18 and len(long_error['stderr_tail']) <= 8
    for state in ('TIMEOUT', 'SPAWN_ERROR', 'NOT_RUN'):
        failed_native = {'termination': state, 'exit': -9 if state == 'TIMEOUT' else None,
                         'signal': 9 if state == 'TIMEOUT' else None,
                         'stderr_first_lines': ['head'], 'stderr_tail': ['tail']}
        with patch.object(runner, 'execute', return_value=copy.deepcopy(failed_native)):
            value = runner.probe(['synthetic'], runner.NAMES, root / 'absent.json', {})
        assert value['classification'] == 'UNKNOWN' and value['reason'] == state
        assert all(value[key] == expected for key, expected in failed_native.items())
    runs = namespace['six_runs']()
    value = {'schema': 'kani-f4-confirm-v2', 'classification': 'DEFECT_ABSENT_FOR_TEST', 'runs': runs}
    with patch.object(runner, 'OUT', root), patch.object(runner, 'RESULT', root / 'result.json'), \
            patch.object(runner, 'snapshot', return_value={'problems': ['synthetic source-stage mismatch']}):
        runner.save(value)
        assert runner.finish() == 2
        assert json.loads((root / 'result.json').read_text())['classification'] == 'INCONCLUSIVE'
record('independent_extra_error_paths', ['matching UNREACHABLE unsupported-class accepted',
       '45KiB stderr preserves first and final diagnostics plus exit 73',
       'TIMEOUT/SPAWN_ERROR/NOT_RUN stay UNKNOWN with native records intact',
       'post-run source-stage mismatch forces INCONCLUSIVE'])

assert not git('status', '--porcelain=v1')
result = {'schema': 'ch8-f4-independent-validation-v1', 'status': 'PASS',
          'assurance': 'STATIC_AND_SYNTHETIC_ONLY', 'candidate_g0': CANDIDATE,
          'checks': CHECKS, 'runtime': 'NOT_RUN', 'actual_compilation_order': 'UNKNOWN',
          'compiler_verifier_full_runner': 'NOT_RUN', 'CI_push_ledger_subagents': False}
(OUT / 'VALIDATION.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
print(json.dumps({'status': 'PASS', 'checks': len(CHECKS), 'runtime': 'NOT_RUN'}))
