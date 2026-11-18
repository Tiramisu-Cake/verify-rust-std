#!/usr/bin/env python3
"""Static source checks and isolated Python oracle checks; never invoke native tools."""
import ast
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch

PACKAGE = Path(__file__).resolve().parent
SOURCE = Path(sys.argv[1] if len(sys.argv) > 1 else '/root/kani-f4-fix-w15')
BASE = 'faffcee3bca2770c03bd21c3bde89cc8f6f7a14e'
INTAKE = PACKAGE.parent / 'f4-confirm-intake/run-44177926794/result.json'
TEST = SOURCE / 'tests/script-based-pre/delayed-shared-body'
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


# Loading the module's definitions leaves its native entry point unexecuted.
module = ast.parse((TEST / 'check.py').read_text())
assert isinstance(module.body[-1], ast.If)
module.body = module.body[:-1]
ns = {'__file__': str(TEST / 'check.py'), '__name__': 'static_oracle'}
exec(compile(module, str(TEST / 'check.py'), 'exec'), ns)
ok('Python AST and guarded native entry point')
subprocess.run(['bash', '-n', str(TEST / 'test.sh')], check=True)
assert os.access(TEST / 'test.sh', os.X_OK)
ok('shell syntax and executable compiletest entry point')

observed = json.loads(INTAKE.read_text())
runs = {label: row['harnesses'] for label, row in observed['runs'].items()}
rejects(lambda: ns['compare'](runs))
ok('observed frozen-main compact results rejected by new regression oracle')

# This adapter supplies COMPLETE/envelope fields discarded by the reviewed compact producer.
# It tests parser compatibility; it cannot re-establish raw native export integrity.
def document(row):
    doc = dict(copy.deepcopy(row['native_configuration']), schema_version='0.1.0',
               run_state='COMPLETE', outcome={'kind': 'COMPLETED'}, harnesses=[])
    for name, h in row['harnesses'].items():
        doc['harnesses'].append(dict(copy.deepcopy(h), name=name, covers={'total': 0},
                                    outcome={'kind': 'COMPLETED', 'verdict': h['verdict']}))
    return doc


for row in observed['runs'].values():
    wanted = row['native_configuration']['harness_selection']['requested_filters']
    parsed = ns['parse'](document(row), row['property_inventory'], wanted, row['exit'])
    for name, h in parsed.items():
        assert ns['signature'](h) == ns['signature'](row['harnesses'][name])
        assert h['verdict'] == row['harnesses'][name]['verdict']
ok('all seven compact inventories parse with explicitly reconstructed export envelopes')

synthetic = copy.deepcopy(runs)
for mode in ('delayed_first', 'control_first'):
    synthetic[mode + '/paired'] = {
        ns['NAMES'][0]: copy.deepcopy(runs[mode + '/delayed_alone'][ns['NAMES'][0]]),
        ns['NAMES'][1]: copy.deepcopy(runs[mode + '/control_alone'][ns['NAMES'][1]])}
ns['compare'](synthetic)
ok('synthetic equal singleton/paired inventories accepted; fixed runtime remains NOT_RUN')

for label, name in [('uninitialized_control', 'uninitialized_control'),
                    ('delayed_first/delayed_alone', ns['NAMES'][0]),
                    ('control_first/paired', ns['NAMES'][0])]:
    changed = copy.deepcopy(synthetic)
    changed[label][name].update(verdict='SUCCESS', failed_properties=[])
    rejects(lambda: ns['compare'](changed))
for mutation in ('missing', 'extra', 'status', 'description', 'location', 'multiplicity'):
    changed = copy.deepcopy(synthetic)
    props = changed['delayed_first/paired'][ns['NAMES'][1]]['properties']
    if mutation == 'missing':
        props.pop()
    elif mutation in ('extra', 'multiplicity'):
        props.append(copy.deepcopy(props[-1]))
    else:
        props[-1][mutation] = 'changed'
    rejects(lambda: ns['compare'](changed))
changed = copy.deepcopy(synthetic)
changed['control_first/paired'][ns['NAMES'][1]]['verdict'] = 'FAILURE'
rejects(lambda: ns['compare'](changed))
changed = copy.deepcopy(synthetic)
changed['delayed_first/paired'][ns['NAMES'][0]]['failed_properties'][0]['line'] = '99'
rejects(lambda: ns['compare'](changed))
ok('unsafe suppression, initialized failure, wrong failure site and semantic composition mutations rejected')

row = observed['runs']['control_first/control_alone']
wanted = [ns['NAMES'][1]]
props = row['property_inventory']
for mutation in ('partial', 'exit', 'missing', 'null', 'wrong_type', 'not_run', 'unresolved',
                 'selection', 'checks', 'unsupported', 'partition'):
    doc = document(row)
    p = copy.deepcopy(props)
    code = 0
    if mutation == 'partial':
        p[wanted[0]].pop()
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
    elif mutation == 'unresolved':
        p[wanted[0]][0]['status'] = 'UNKNOWN'
    elif mutation == 'selection':
        doc['harness_selection']['matched_count'] = 2
    elif mutation == 'checks':
        doc['configuration']['checks']['memory_safety'] = False
    elif mutation == 'unsupported':
        doc['harnesses'][0]['unsupported_constructs'] = [dict(p[wanted[0]][0], status='FAILURE')]
    else:
        doc['harnesses'][0]['checks']['failure'] = ['unexpected']
    rejects(lambda: ns['parse'](doc, p, wanted, code))
ok('parser rejects partial/missing/null/wrong-type/NOT_RUN/unresolved/mismatch/weakened checks')

stdout = '\n'.join('Checking harness ' + name + '...\n' + '\n'.join(
    'Check ' + str(p['index']) + ': ' + p['id'] + '\n' + '\n'.join(
        ' - ' + key.capitalize() + ': ' + ('"' + p[key] + '"' if key == 'description' else p[key])
        for key in ('status', 'description', 'location')) for p in values)
    for name, values in props.items())
assert ns['inventory'](stdout) == props
rejects(lambda: ns['inventory'](stdout + '\nChecking harness ' + wanted[0] + '...'))
ok('regular inventory parsing and duplicate harness rejection')

with tempfile.TemporaryDirectory(dir=PACKAGE) as temporary:
    export = Path(temporary) / 'export.json'
    def complete(*args, **kwargs):
        assert not export.exists(), 'stale export retained'
        export.write_text(json.dumps(document(row)))
        return subprocess.CompletedProcess(args[0], 0, stdout, '')
    with patch.object(ns['subprocess'], 'run', side_effect=complete):
        export.write_text('stale')
        assert ns['probe'](['synthetic-kani'], wanted, export, {})[wanted[0]]['verdict'] == 'SUCCESS'
    for error in (OSError('synthetic spawn failure'), subprocess.TimeoutExpired('synthetic-kani', 120)):
        with patch.object(ns['subprocess'], 'run', side_effect=error):
            rejects(lambda: ns['probe'](['synthetic-kani'], wanted, export, {}))
    for code in (2, -9):
        with patch.object(ns['subprocess'], 'run', return_value=subprocess.CompletedProcess([], code, '', 'failure')):
            rejects(lambda: ns['probe'](['synthetic-kani'], wanted, export, {}))
    with patch.object(ns['subprocess'], 'run', return_value=subprocess.CompletedProcess([], 0, '', '')):
        rejects(lambda: ns['probe'](['synthetic-kani'], wanted, export, {}))
ok('mocked probe success/spawn/timeout/signal/error/missing export; native tools never called')

compiler = (SOURCE / 'kani-compiler/src/codegen_cprover_gotoc/compiler_interface.rs').read_text()
transform = (SOURCE / 'kani-compiler/src/kani_middle/transform/mod.rs').read_text()
assert '#[derive(Clone, Debug)]\npub struct BodyTransformation' in transform
loop = compiler.split('for harness in ordered_harnesses {', 1)[1].split('units.store_modifies', 1)[0]
assert 'let mut transformer = shared_unit_transformer.clone();' in loop
assert '&mut transformer,' in loop and '&mut shared_unit_transformer,' not in loop
assert 'clear_codegen_cache();' in loop and 'template_passes.clone(),' in loop
assert git('diff', BASE, '--', '.github', 'scripts', 'kani-compiler/src/kani_middle/transform/check_uninit') == ''
for name in ('src/lib.rs', 'control.rs', 'Cargo.toml'):
    original = PACKAGE.parent / 'f4-confirm/source/tests/script-based-pre/delayed-shared-body' / name
    assert (TEST / name).read_bytes() == original.read_bytes()
ok('harness-local global/codegen lifecycle; checks/workflows/scripts/observed Rust fixture unchanged')

assert git('rev-parse', 'HEAD^') == BASE
assert git('status', '--porcelain') == ''
changes = git('diff', '--name-status', BASE, 'HEAD').splitlines()
assert len(changes) == 9 and all(row.startswith(('A\t', 'M\t')) for row in changes)
assert git('diff', '--check', BASE, 'HEAD') == ''
with tempfile.TemporaryDirectory(dir=PACKAGE) as temporary:
    index = Path(temporary) / 'index'
    env = dict(os.environ, GIT_INDEX_FILE=str(index))
    patch_file = PACKAGE / 'fix.patch'
    subprocess.run(['git', 'read-tree', BASE], cwd=SOURCE, env=env, check=True)
    subprocess.run(['git', 'apply', '--cached', '--check', str(patch_file)], cwd=SOURCE, env=env, check=True)
    subprocess.run(['git', 'apply', '--cached', str(patch_file)], cwd=SOURCE, env=env, check=True)
    replay = subprocess.check_output(['git', 'write-tree'], cwd=SOURCE, env=env).decode().strip()
    assert replay == git('rev-parse', 'HEAD^{tree}')
ok('clean committed direct child; exact nine-file scope; isolated-index patch replay reproduces source tree')

result = {'status': 'PASS', 'scope': 'STATIC_AND_SYNTHETIC_ONLY', 'checks': checks,
          'main_oracle': 'FAIL_ON_OBSERVED_COMPACT_RESULTS', 'fixed_runtime': 'NOT_RUN',
          'main_new_test_runtime': 'NOT_RUN', 'compiler_build': 'NOT_RUN',
          'compilation_order': 'UNKNOWN', 'independent_review': 'PENDING_REVIEW14',
          'intake_sha256': hashlib.sha256(INTAKE.read_bytes()).hexdigest()}
(PACKAGE / 'VALIDATION.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'status': result['status'], 'checks': len(checks), 'fixed_runtime': 'NOT_RUN'}))
