#!/usr/bin/env python3
"""Replay static identities and synthetic Python oracles without native tools."""
import ast
import contextlib
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from unittest.mock import patch

PACKAGE = Path(__file__).resolve().parent
SOURCE = Path(sys.argv[1] if len(sys.argv) > 1 else '/root/kani-f4-uninit-only-w15')
BASE = 'b5a9678fd7c2a0f67c3fcafd90057fc2afaf9b5d'
BASE_TREE = '8585336ed35a14fe0fc157a7ca4e0d52075c0e49'
MAIN = 'faffcee3bca2770c03bd21c3bde89cc8f6f7a14e'
TEST_REL = 'tests/script-based-pre/delayed-shared-body'
TEST = SOURCE / TEST_REL
COMPILER = 'kani-compiler/src/codegen_cprover_gotoc/compiler_interface.rs'
INTAKE = PACKAGE.parent / 'f4-confirm-intake/run-44177926794/result.json'
checks = []


def git(*args):
    return subprocess.check_output(['git', *args], cwd=SOURCE).decode().strip()


def ok(name):
    checks.append(name)


def rejects(action):
    try:
        action()
    except (ValueError, KeyError, TypeError, OSError, StopIteration, subprocess.TimeoutExpired):
        return
    raise AssertionError('accepted invalid result')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


module = ast.parse((TEST / 'check.py').read_text())
assert isinstance(module.body[-1], ast.If)
ns = {'__file__': str(TEST / 'check.py'), '__name__': 'static_oracle'}
exec(compile(module, str(TEST / 'check.py'), 'exec'), ns)
subprocess.run(['bash', '-n', str(TEST / 'test.sh')], check=True)
assert os.access(TEST / 'test.sh', os.X_OK)
ok('Python AST, guarded entry point, executable shell syntax')

observed = json.loads(INTAKE.read_text())
old_runs = {label: row['harnesses'] for label, row in observed['runs'].items()}
rejects(lambda: ns['compare'](old_runs, True))
ok('observed frozen-main enabled compact inventories still reject')


def document(row):
    # Reconstruct fields omitted by the compact producer; this is an adapter fixture.
    doc = dict(copy.deepcopy(row['native_configuration']), schema_version='0.1.0',
               run_state='COMPLETE', outcome={'kind': 'COMPLETED'}, harnesses=[])
    for name, h in row['harnesses'].items():
        doc['harnesses'].append(dict(copy.deepcopy(h), name=name, covers={'total': 0},
                                    outcome={'kind': 'COMPLETED', 'verdict': h['verdict']}))
    return doc


for row in observed['runs'].values():
    wanted = row['native_configuration']['harness_selection']['requested_filters']
    parsed = ns['parse'](document(row), row['property_inventory'], wanted, row['exit'], True)
    for name in parsed:
        assert ns['signature'](parsed[name]) == ns['signature'](row['harnesses'][name])
ok('enabled compact data parse with explicitly reconstructed native envelopes')

enabled = copy.deepcopy(old_runs)
for cfg in ('delayed_first', 'control_first'):
    enabled[cfg + '/paired'] = {
        ns['NAMES'][0]: copy.deepcopy(old_runs[cfg + '/delayed_alone'][ns['NAMES'][0]]),
        ns['NAMES'][1]: copy.deepcopy(old_runs[cfg + '/control_alone'][ns['NAMES'][1]])}


def ordinary(name):
    # Synthetic identities/counts exercise the oracle; native ordinary inventories are NOT_RUN.
    props = [dict(index=1, id=name + '.pointer_dereference.1', status='SUCCESS',
                  description='dereference failure: pointer outside object bounds',
                  location='synthetic ordinary check')]
    if name == ns['NAMES'][1]:
        props.append(dict(index=2, id=name + '.assertion.1', status='SUCCESS',
                          description='assertion failed: result == 7',
                          location='synthetic initialized assertion'))
    return dict(verdict='SUCCESS', properties=props, failed_properties=[], n_failed=0,
                n_properties=len(props), unsupported_constructs=[],
                checks=dict(total=len(props), success=len(props), failure=[], unreachable=[],
                            undetermined=[], error=[], unknown=[], other=[]))


disabled = {label: {name: ordinary(name) for name in harnesses}
            for label, harnesses in enabled.items()}
for uninit, runs in ((True, enabled), (False, disabled)):
    ns['compare'](runs, uninit)
    for cfg in ('delayed_first', 'control_first'):
        for name in ns['NAMES']:
            changed = copy.deepcopy(runs)
            changed[cfg + '/paired'][name]['properties'][-1]['location'] += ' changed'
            rejects(lambda: ns['compare'](changed, uninit))
        for label in ('delayed_alone', 'paired'):
            changed = copy.deepcopy(runs)
            h = changed[cfg + '/' + label][ns['NAMES'][0]]
            h.update(verdict='SUCCESS' if uninit else 'FAILURE', failed_properties=[])
            rejects(lambda: ns['compare'](changed, uninit))
        changed = copy.deepcopy(runs)
        changed[cfg + '/paired'][ns['NAMES'][1]]['verdict'] = 'FAILURE'
        rejects(lambda: ns['compare'](changed, uninit))
    changed = copy.deepcopy(runs)
    changed['uninitialized_control']['uninitialized_control'].update(
        verdict='SUCCESS' if uninit else 'FAILURE', failed_properties=[])
    rejects(lambda: ns['compare'](changed, uninit))
ok('synthetic two-mode positives; both cfg paths reject unsafe suppression/ordinary failures/composition drift')

for mutation in ('missing', 'extra', 'status', 'description', 'multiplicity', 'assertion'):
    for uninit, runs in ((True, enabled), (False, disabled)):
        changed = copy.deepcopy(runs)
        props = changed['delayed_first/paired'][ns['NAMES'][1]]['properties']
        if mutation == 'missing':
            props.pop()
        elif mutation in ('extra', 'multiplicity'):
            props.append(copy.deepcopy(props[-1]))
        else:
            props[-1]['description' if mutation == 'assertion' else mutation] = 'changed'
        rejects(lambda: ns['compare'](changed, uninit))
changed = copy.deepcopy(enabled)
changed['control_first/paired'][ns['NAMES'][0]]['failed_properties'][0]['line'] = '99'
rejects(lambda: ns['compare'](changed, True))
changed = copy.deepcopy(disabled)
changed['uninitialized_control']['uninitialized_control']['properties'][0]['description'] = ns['UNINIT']
rejects(lambda: ns['compare'](changed, False))
ok('semantic multiplicity/assertion/site controls and disabled unexpected-uninit control')


def fixture(uninit, label, wanted):
    runs = enabled if uninit else disabled
    row = copy.deepcopy(observed['runs'][label])
    row['harnesses'] = {name: copy.deepcopy(runs[label][name]) for name in wanted}
    row['native_configuration']['enabled_unstable_features'] = (
        ['export-json', 'ghost-state', 'uninit-checks'] if uninit else ['export-json'])
    row['native_configuration']['harness_selection'] = dict(
        requested_filters=wanted, exact=True, unmatched_filters=[], matched_count=len(wanted))
    props = {name: row['harnesses'][name]['properties'] for name in wanted}
    code = int(any(h['verdict'] == 'FAILURE' for h in row['harnesses'].values()))
    return document(row), props, code


for uninit in (True, False):
    for label, harnesses in (enabled if uninit else disabled).items():
        wanted = list(harnesses)
        doc, props, code = fixture(uninit, label, wanted)
        assert set(ns['parse'](doc, props, wanted, code, uninit)) == set(wanted)
    wanted = ns['NAMES'][1:]
    for mutation in ('partial', 'exit', 'missing', 'null', 'wrong_type', 'not_run',
                     'outcome', 'unresolved', 'selection', 'filter', 'harness', 'checks',
                     'unsupported', 'partition', 'feature_cross_mode', 'feature_missing',
                     'feature_extra', 'feature_duplicate', 'coverage', 'cbmc_args', 'duplicate'):
        doc, props, code = fixture(uninit, 'control_first/control_alone', wanted)
        if mutation == 'partial':
            props[wanted[0]].pop()
        elif mutation == 'exit':
            code = 1
        elif mutation == 'missing':
            del doc['harnesses']
        elif mutation == 'null':
            doc = None
        elif mutation == 'wrong_type':
            doc['harnesses'] = 'wrong'
        elif mutation == 'not_run':
            doc['run_state'] = 'NOT_RUN'
        elif mutation == 'outcome':
            doc['harnesses'][0]['outcome'] = {'kind': 'TIMEOUT'}
        elif mutation == 'unresolved':
            props[wanted[0]][0]['status'] = 'UNKNOWN'
        elif mutation == 'selection':
            doc['harness_selection']['matched_count'] = 2
        elif mutation == 'filter':
            doc['harness_selection']['requested_filters'] = ['wrong']
        elif mutation == 'harness':
            doc['harnesses'][0]['name'] = 'wrong'
        elif mutation == 'checks':
            doc['configuration']['checks']['memory_safety'] = False
        elif mutation == 'unsupported':
            doc['harnesses'][0]['unsupported_constructs'] = [dict(props[wanted[0]][0], status='FAILURE')]
        elif mutation == 'partition':
            doc['harnesses'][0]['checks']['failure'] = ['unexpected']
        elif mutation == 'feature_cross_mode':
            doc['enabled_unstable_features'] = ['export-json'] if uninit else ['export-json', 'uninit-checks']
        elif mutation == 'feature_missing':
            doc['enabled_unstable_features'].remove('export-json')
        elif mutation == 'feature_extra':
            doc['enabled_unstable_features'].append('valid-value-checks')
        elif mutation == 'feature_duplicate':
            doc['enabled_unstable_features'].append('export-json')
        elif mutation == 'coverage':
            doc['configuration']['coverage_enabled'] = True
        elif mutation == 'cbmc_args':
            doc['configuration']['cbmc_args'] = ['--no-bounds-check']
        else:
            props[wanted[0]].append(copy.deepcopy(props[wanted[0]][-1]))
        rejects(lambda: ns['parse'](doc, props, wanted, code, uninit))
    for check in ('memory_safety', 'overflow', 'unwinding', 'undefined_function', 'assertion_reach_checks'):
        doc, props, code = fixture(uninit, 'control_first/control_alone', wanted)
        doc['configuration']['checks'][check] = False
        rejects(lambda: ns['parse'](doc, props, wanted, code, uninit))
ok('both parsers reject missing/partial/null/wrong-type/NOT_RUN/native outcome/feature/selection/check mismatches')


def stdout_for(props):
    return '\n'.join('Checking harness ' + name + '...\n' + '\n'.join(
        'Check ' + str(p['index']) + ': ' + p['id'] + '\n' + '\n'.join(
            ' - ' + key.capitalize() + ': ' + ('"' + p[key] + '"' if key == 'description' else p[key])
            for key in ('status', 'description', 'location')) for p in values)
        for name, values in props.items())


doc, props, code = fixture(False, 'control_first/control_alone', ns['NAMES'][1:])
stdout = stdout_for(props)
assert ns['inventory'](stdout) == props
rejects(lambda: ns['inventory'](stdout + '\nChecking harness ' + ns['NAMES'][1] + '...'))
ok('regular output inventory parser and duplicate harness rejection')

with tempfile.TemporaryDirectory() as temporary:
    export = Path(temporary) / 'export.json'
    for uninit in (True, False):
        doc, props, code = fixture(uninit, 'control_first/control_alone', ns['NAMES'][1:])

        def complete(args, **kwargs):
            assert not export.exists(), 'stale export retained'
            assert ('uninit-checks' in args) is uninit
            assert ('ghost-state' in args) is uninit
            export.write_text(json.dumps(doc))
            return subprocess.CompletedProcess(args, code, stdout_for(props), '')

        with patch.object(ns['subprocess'], 'run', side_effect=complete):
            export.write_text('stale')
            ns['probe'](['synthetic-kani'], ns['NAMES'][1:], export, {}, uninit)
        for error in (OSError('synthetic spawn failure'), subprocess.TimeoutExpired('synthetic-kani', 120)):
            with patch.object(ns['subprocess'], 'run', side_effect=error):
                rejects(lambda: ns['probe'](['synthetic-kani'], ns['NAMES'][1:], export, {}, uninit))
        for bad_code in (2, -9):
            with patch.object(ns['subprocess'], 'run', return_value=subprocess.CompletedProcess([], bad_code, '', 'failure')):
                rejects(lambda: ns['probe'](['synthetic-kani'], ns['NAMES'][1:], export, {}, uninit))
        for content in (None, '{', 'null'):
            def broken(args, **kwargs):
                if content is not None:
                    export.write_text(content)
                return subprocess.CompletedProcess(args, 0, '', '')
            with patch.object(ns['subprocess'], 'run', side_effect=broken), contextlib.redirect_stdout(io.StringIO()):
                rejects(lambda: ns['probe'](['synthetic-kani'], ns['NAMES'][1:], export, {}, uninit))
ok('both probes: mocked success/stale/spawn/timeout/signal/error/missing/malformed/null export')

# Mock the subprocess boundary while exercising argument/environment construction for every case.
commands = []
targets = set()


def native_fixture(args, **kwargs):
    uninit = 'uninit-checks' in args
    assert ('ghost-state' in args) is uninit
    assert kwargs['cwd'] == TEST and kwargs['timeout'] == 120
    env = kwargs['env']
    assert env['KANIFLAGS'] == env['KANI_LOG'] == '' and env['NO_COLOR'] == '1'
    assert all(key not in env for key in ('CARGO_ENCODED_RUSTFLAGS', 'CARGO_TARGET_DIR', 'CARGO_BUILD_TARGET'))
    target = args[args.index('--target-dir') + 1]
    assert target not in targets
    targets.add(target)
    wanted = [args[i + 1] for i, arg in enumerate(args) if arg == '--harness']
    assert '--exact' in args and '-j1' in args and '--output-format=regular' in args
    if args[0] == 'kani':
        assert env['RUSTFLAGS'] == '--edition=2021'
        label = 'uninitialized_control'
    else:
        assert args[:2] == ['cargo', 'kani'] and env['RUSTFLAGS'] == ''
        assert args[args.index('--manifest-path') + 1] == str(TEST / 'Cargo.toml')
        assert '--lib' in args
        cfg = 'delayed_first' if '--features' in args else 'control_first'
        if cfg == 'delayed_first':
            assert args[args.index('--features') + 1] == 'delayed-first'
        case = 'paired' if len(wanted) == 2 else ('delayed_alone' if wanted == ns['NAMES'][:1] else 'control_alone')
        label = cfg + '/' + case
    doc, props, code = fixture(uninit, label, wanted)
    export = Path(args[args.index('--export-json') + 1])
    assert not export.exists()
    export.write_text(json.dumps(doc))
    commands.append(dict(uninit=uninit, case=label, wanted=wanted,
                         features=doc['enabled_unstable_features'], exit_expected=code,
                         fixture='SYNTHETIC_EXPECTED; not native observations'))
    return subprocess.CompletedProcess(args, code, stdout_for(props), '')


poison = {key: '-Z uninit-checks' for key in ('KANIFLAGS', 'RUSTFLAGS', 'CARGO_ENCODED_RUSTFLAGS',
                                            'CARGO_TARGET_DIR', 'CARGO_BUILD_TARGET', 'KANI_LOG')}
with patch.dict(os.environ, poison), patch.object(ns['subprocess'], 'run', side_effect=native_fixture), \
        contextlib.redirect_stdout(io.StringIO()):
    ns['main']()
assert len(commands) == 14 and sum(c['uninit'] for c in commands) == 7
assert len({(c['uninit'], c['case']) for c in commands}) == 14
ok('mocked orchestration: two modes x both cfg paths/singletons/pairs plus independent controls; poisoned env removed')

compiler = (SOURCE / COMPILER).read_text()
baseline_compiler = subprocess.check_output(['git', 'show', BASE + ':' + COMPILER], cwd=SOURCE).decode()
delayed = (SOURCE / 'kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/mod.rs').read_text()
predicate = 'queries.args().ub_check.contains(&ExtraChecks::Uninit)'
assert 'args.ub_check.contains(&ExtraChecks::Uninit)' in delayed
assert 'let check_uninit = ' + predicate + ';' in compiler
loop = compiler.split('for harness in ordered_harnesses {', 1)[1].split('units.store_modifies', 1)[0]
assert '''let transformer = if check_uninit {
                                harness_transformer = shared_unit_transformer.clone();
                                &mut harness_transformer
                            } else {
                                &mut shared_unit_transformer
                            };''' in loop
assert loop.count('.clone();') == 1
assert 'template_passes.clone(),\n                                transformer,' in loop
assert 'clear_codegen_cache();' in loop
# All operations outside the narrow guard/comments/import/call-argument replacement are byte invariant.
restored = compiler.replace('use crate::args::{ExtraChecks, ReachabilityType};', 'use crate::args::ReachabilityType;')
restored = restored.replace('                    let check_uninit = ' + predicate + ';\n', '')
restored = restored.replace('body cache used by each harness', 'body cache copied into each harness')
start = restored.index('                            // Delayed uninitialized-memory checks')
end = restored.index('\n\n                            let model_path', start)
restored = restored[:start] + '''                            // Global passes use analysis targets specific to this harness. Keep their
                            // transformed bodies in a harness-local copy of the warmed body cache.
                            let mut transformer = shared_unit_transformer.clone();''' + restored[end:]
restored = restored.replace('template_passes.clone(),\n                                transformer,',
                            'template_passes.clone(),\n                                &mut transformer,')
assert restored == baseline_compiler
transform = (SOURCE / 'kani-compiler/src/kani_middle/transform/mod.rs').read_text()
assert '#[derive(Clone, Debug)]\npub struct BodyTransformation' in transform
assert git('diff', BASE, '--', 'kani-compiler/src/kani_middle') == ''
ok('exact DelayedUbPass predicate; whole clone on / shared reference off; remaining compiler lifecycle byte invariant')

changed = git('diff', '--name-only', BASE, 'HEAD').splitlines()
assert changed == sorted([COMPILER, TEST_REL + '/check.py'])
assert git('diff', BASE, '--', '.github', 'scripts', 'library', 'rust-toolchain.toml', 'Cargo.toml', 'Cargo.lock') == ''
workflows = git('ls-tree', '--name-only', 'HEAD:.github/workflows').splitlines()
assert len(workflows) == 16
for name in ('src/lib.rs', 'control.rs', 'Cargo.toml', 'test.sh', 'config.yml', 'expected'):
    assert git('rev-parse', BASE + ':' + TEST_REL + '/' + name) == git('rev-parse', 'HEAD:' + TEST_REL + '/' + name)
assert git('rev-parse', BASE + '^{tree}') == BASE_TREE
assert git('rev-parse', BASE + '^') == MAIN
assert git('rev-parse', 'HEAD^') == BASE
assert git('status', '--porcelain') == ''
assert git('diff', '--check', MAIN, 'HEAD') == ''
ok('clean direct b5 child, exact two-file delta; 16 workflows/fixtures/checks/toolchain/dependencies unchanged')

for base, filename in ((BASE, 'delta-b5.patch'), (MAIN, 'full-main.patch')):
    with tempfile.TemporaryDirectory() as temporary:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(temporary) / 'index'))
        subprocess.run(['git', 'read-tree', base], cwd=SOURCE, env=env, check=True)
        subprocess.run(['git', 'apply', '--cached', '--check', str(PACKAGE / filename)], cwd=SOURCE, env=env, check=True)
        subprocess.run(['git', 'apply', '--cached', str(PACKAGE / filename)], cwd=SOURCE, env=env, check=True)
        tree = subprocess.check_output(['git', 'write-tree'], cwd=SOURCE, env=env).decode().strip()
        assert tree == git('rev-parse', 'HEAD^{tree}')
ok('both narrow b5 patch and full main patch reproduce exact candidate tree in isolated indexes')

with tempfile.TemporaryDirectory() as temporary:
    env = dict(os.environ, GIT_INDEX_FILE=str(Path(temporary) / 'index'))
    subprocess.run(['git', 'read-tree', MAIN], cwd=SOURCE, env=env, check=True)
    subprocess.run(['git', 'apply', '--cached', str(PACKAGE / 'regression-main.patch')],
                   cwd=SOURCE, env=env, check=True)
    compiler_blob = subprocess.check_output(['git', 'rev-parse', ':' + COMPILER], cwd=SOURCE, env=env).decode().strip()
    assert compiler_blob == git('rev-parse', MAIN + ':' + COMPILER)
    for name in git('ls-tree', '-r', '--name-only', 'HEAD', '--', TEST_REL).splitlines():
        blob = subprocess.check_output(['git', 'rev-parse', ':' + name], cwd=SOURCE, env=env).decode().strip()
        assert blob == git('rev-parse', 'HEAD:' + name)
ok('regression-only patch installs exact two-mode fixture on main with main compiler unchanged')

pins = json.loads((PACKAGE / 'SOURCE-PINS.json').read_text())
assert pins['source'] == git('rev-parse', 'HEAD')
assert pins['tree'] == git('rev-parse', 'HEAD^{tree}') and pins['parent'] == BASE
for filename, sha in pins['changed_file_sha256'].items():
    assert digest(SOURCE / filename) == sha
for filename, sha in pins['full_main_changed_file_sha256'].items():
    assert digest(SOURCE / filename) == sha
for filename, sha in pins['workflow_sha256'].items():
    assert digest(SOURCE / filename) == sha
assert pins['patch_sha256'] == {name: digest(PACKAGE / name) for name in ('delta-b5.patch', 'full-main.patch', 'regression-main.patch')}
ok('source/tree/parent and changed-file/workflow/patch SHA256 binding')

request = json.loads((PACKAGE / 'CI-REQUEST.json').read_text())
assert request['reviewed_candidate'] == pins['source'] and request['reviewed_tree'] == pins['tree']
assert request['parent'] == BASE and request['authorization']['dispatch'] is False
assert request['future_final_head']['tree'] == pins['tree']
assert request['future_final_head']['parent'] == BASE and request['future_final_head']['sha'] == 'NOT_CREATED'
assert set(request['workflows']) == {'kani.yml', 'format-check.yml', 'deny.yml'}
for filename, workflow in request['workflows'].items():
    content = (SOURCE / '.github/workflows' / filename).read_text()
    jobs = re.findall(r'^  ([a-z][a-z0-9_-]*):$', content.split('\njobs:\n', 1)[1], re.MULTILINE)
    assert set(jobs) == set(workflow['jobs'])
    assert "  push:\n" in content and "      - '**'" in content
kani = (SOURCE / '.github/workflows/kani.yml').read_text()
os_list = request['workflows']['kani.yml']['jobs']['regression']['matrix_os']
assert 'os: [' + ', '.join(os_list) + ']' in kani
assert 'timeout-minutes: 380' in kani and 'timeout_minutes: 180' in kani and 'max_attempts: 2' in kani
assert request['preserve']['workflow_sha256'] == pins['workflow_sha256']
assert not any(request['actions'].values()) and request['accounting_reference']['attempts_consumed_here'] == 0
gate = {'__name__': 'static_gate', '__file__': str(PACKAGE / 'check_push_head.py')}
exec(compile((PACKAGE / 'check_push_head.py').read_text(), str(PACKAGE / 'check_push_head.py'), 'exec'), gate)
for message in ('[skip ci]', '[ci skip]', '[no ci]', '[skip actions]', '[actions skip]',
                'message\n\nskip-checks: true', '[SKIP CI]'):
    assert gate['SKIP'].search(message)
assert not gate['SKIP'].search('Isolate delayed uninitialized-memory transformations')
try:
    gate['check'](SOURCE, pins['source'])
except AssertionError as error:
    assert 'skip directive' in str(error)
else:
    raise AssertionError('skipped candidate accepted as push head')
ok('complete native push job/matrix plan and read-only final-head guard; skipped candidate rejected')

result = dict(status='PASS', assurance='STATIC_AND_SYNTHETIC_ONLY', checks=checks,
              source=pins['source'], tree=pins['tree'], parent=BASE,
              main_enabled_oracle='REJECTS_OBSERVED_COMPACT_RESULTS_WITH_ADAPTED_ENVELOPE',
              native_two_mode_runtime='NOT_RUN', disabled_native_inventory='NOT_RUN',
              compiler_build='NOT_RUN', performance='NOT_RUN', compilation_order='UNKNOWN',
              independent_review='PENDING_REVIEW14', proof_credit='NONE',
              intake_sha256=digest(INTAKE), mock_case_matrix=commands)
(PACKAGE / 'VALIDATION.json').write_text(json.dumps(result, indent=2) + '\n')
manifest_path = PACKAGE / 'MANIFEST.json'
if manifest_path.exists():
    manifest = json.loads(manifest_path.read_text())
    assert manifest['source'] == pins['source'] and manifest['tree'] == pins['tree']
    actual = {f.name: digest(f) for f in PACKAGE.iterdir() if f.is_file() and f.name != 'MANIFEST.json'}
    assert manifest['files_sha256'] == actual, 'package manifest mismatch'
print(json.dumps(dict(status='PASS', checks=len(checks), native_two_mode_runtime='NOT_RUN', source=pins['source'])))
