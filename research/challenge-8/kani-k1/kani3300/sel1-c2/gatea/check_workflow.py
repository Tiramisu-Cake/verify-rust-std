#!/usr/bin/env python3
"""Offline, bounded Gate A YAML/context/binding checks; no toolchain invocation."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess

import yaml

HERE = Path(__file__).resolve().parent
SOURCE = '14bc57fdb99960240c4944845a3d985c8af4dcf7'
TREE = '1efb6e4dfa69d346df8e23741d11839b1932403d'
WORKFLOW = '.github/workflows/kani3300-sel1-c2-gatea.yml'


class Loader(yaml.SafeLoader):
    pass


# YAML 1.2: GitHub's `on` must remain a string. Reject duplicate keys.
Loader.yaml_implicit_resolvers = {
    k: [(tag, rx) for tag, rx in values if tag != 'tag:yaml.org,2002:bool']
    for k, values in Loader.yaml_implicit_resolvers.items()
}
Loader.add_implicit_resolver('tag:yaml.org,2002:bool', re.compile(r'^(?:true|false)$'), list('tf'))


def mapping(loader, node):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        assert key not in result, ('duplicate YAML key', key)
        result[key] = loader.construct_object(value_node)
    return result


Loader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)


def check_contexts(node, allowed):
    if isinstance(node, dict):
        for value in node.values():
            check_contexts(value, allowed)
    elif isinstance(node, list):
        for value in node:
            check_contexts(value, allowed)
    elif isinstance(node, str):
        for expr in re.findall(r'\$\{\{(.*?)\}\}', node, re.S):
            expr = re.sub(r"'[^']*'", '', expr)
            for context in re.findall(r'(?<![\w.])([A-Za-z_]\w*)\s*\.', expr):
                assert context in allowed, ('unavailable context', context, allowed)


def validate(doc):
    assert doc['on'] == {'push': {'branches': ['uninit-ci/sel1-c2-gatea-*']}}
    assert doc['permissions'] == {'contents': 'read'}
    assert doc['concurrency']['cancel-in-progress'] is False
    assert set(doc['jobs']) == {'regression', 'summary'}
    assert set(doc) <= {'name', 'on', 'permissions', 'concurrency', 'env', 'jobs'}
    check_contexts(doc.get('env', {}), {'github', 'vars', 'secrets', 'inputs'})
    reg = doc['jobs']['regression']
    assert reg['strategy'] == {'fail-fast': False, 'max-parallel': 3,
                               'matrix': {'os': ['ubuntu-24.04', 'ubuntu-24.04-arm', 'macos-15']}}
    assert reg['timeout-minutes'] == 360
    assert reg['runs-on'] == '${{ matrix.os }}'
    assert reg['env'] == {'GATE_OUTPUT': '${{ github.workspace }}/artifacts/${{ matrix.os }}'}
    for name, job in doc['jobs'].items():
        assert job['if'] == ("${{ github.repository == 'Tiramisu-Cake/kani' }}" if name == 'regression'
                             else "${{ always() && github.repository == 'Tiramisu-Cake/kani' }}")
        check_contexts(job['if'], {'github', 'needs', 'vars', 'inputs'})
        check_contexts(job.get('env', {}), {'github', 'needs', 'strategy', 'matrix', 'vars', 'secrets', 'inputs'})
        ids = {step['id'] for step in job['steps'] if 'id' in step}
        assert len(ids) == sum('id' in step for step in job['steps'])
        for step in job['steps']:
            assert ('uses' in step) != ('run' in step)
            assert set(step) <= {'name', 'id', 'uses', 'with', 'env', 'if', 'run', 'working-directory', 'shell'}
            # Per owner checklist runner.* is permitted only in step env.
            check_contexts({k: v for k, v in step.items() if k != 'env'},
                           {'github', 'needs', 'strategy', 'matrix', 'vars', 'secrets', 'inputs', 'env', 'steps', 'job'})
            check_contexts(step.get('env', {}),
                           {'github', 'needs', 'strategy', 'matrix', 'vars', 'secrets', 'inputs', 'env', 'steps', 'job', 'runner'})
            for ident in re.findall(r'steps\.([\w-]+)\.', json.dumps(step)):
                assert ident in ids, ('unknown step', ident)
            if step.get('uses', '').startswith('actions/checkout@'):
                assert step['with']['fetch-depth'] >= 2
                assert step['with']['persist-credentials'] is False
            if step.get('uses', '').startswith('actions/upload-artifact@'):
                assert step['if'] == 'always()'
                assert step['with']['retention-days'] == 14
                assert step['with']['if-no-files-found'] == 'error'
            if 'run' in step:
                shell = re.sub(r'\$\{\{.*?\}\}', 'STATIC', step['run'], flags=re.S)
                subprocess.run(['bash', '-n'], input=shell.encode(), check=True, capture_output=True)
    steps = reg['steps']
    control = next(s for s in steps if s.get('name') == 'Control checkout at exact dispatched overlay SHA')
    export = next(s for s in steps if s.get('id') == 'export')
    assert control['with']['path'] == 'control' and control['with']['ref'] == '${{ github.sha }}'
    assert export['with']['path'] == 'export' and export['with']['ref'] == SOURCE
    setup = next(s for s in steps if s.get('id') == 'setup')
    assert setup['uses'] == './export/.github/actions/setup'
    assert setup['with'] == {'os': '${{ matrix.os }}', 'kani_dir': 'export'}
    for step in steps:
        if 'run' not in step or 'kani3300-gate/' not in step['run']:
            continue
        if step.get('id') == 'regression':
            assert step['working-directory'] == 'export'
            assert 'python3 ../control/scripts/kani3300-gate/receipt.py run --binding ../control/' in step['run']
        else:
            assert step['working-directory'] == 'control'
        if '--source-dir' in step['run']:
            assert '--source-dir ../export' in step['run']
    for ident in ('postsetup', 'postregression'):
        assert next(s for s in steps if s.get('id') == ident)['if'] == "always() && steps.preflight.outcome == 'success'"
    summary = doc['jobs']['summary']
    assert summary['needs'] == ['regression']
    aggregate = next(s for s in summary['steps'] if 'aggregate --binding' in s.get('run', ''))
    assert aggregate['if'] == 'always()'
    assert "--matrix-result '${{ needs.regression.result }}'" in aggregate['run']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path('/root/kani-fix-3300-sel1-c2-w15'))
    args = parser.parse_args()
    repo = args.repo
    def git(*argv):
        return subprocess.check_output(['git', '-C', str(repo), *argv])
    assert git('rev-parse', SOURCE + '^{tree}').decode().strip() == TREE
    full = HERE / 'full-export'
    paths = [p.relative_to(full) for p in full.rglob('*') if p.is_file()]
    for rel in paths:
        assert (full / rel).read_bytes() == (repo / rel).read_bytes(), ('export copy differs', str(rel))
    assert list((repo / '.github/workflows').iterdir()) == [repo / WORKFLOW]
    doc = yaml.load((repo / WORKFLOW).read_text(), Loader=Loader)
    validate(doc)
    binding = json.loads((repo / 'scripts/kani3300-gate/binding.json').read_text())
    assert binding['state'] == 'SEL1_C2_FROZEN'
    assert (binding['export_sha'], binding['export_tree']) == (SOURCE, TREE)
    for rel, digest in binding['files'].items():
        assert hashlib.sha256(git('show', SOURCE + ':' + rel)).hexdigest() == digest, rel
    for kind in ('subtrees', 'submodule_pins'):
        for rel, oid in binding[kind].items():
            assert git('rev-parse', SOURCE + ':' + rel).decode().strip() == oid, rel
    for rel, target in binding['symlinks'].items():
        assert git('show', SOURCE + ':' + rel).decode() == target, rel
    observer = (repo / 'scripts/kani3300-gate/receipt.py').read_text()
    constants = {n.targets[0].id: ast.literal_eval(n.value) for n in ast.parse(observer).body
                 if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)
                 and n.targets[0].id in ('FROZEN_SHA', 'FROZEN_TREE', 'HOOK')}
    assert constants['FROZEN_SHA'] == SOURCE and constants['FROZEN_TREE'] == TREE
    assert 'if [[ -z ${KANI_GATE_OWNER_PID-} ]]; then' in constants['HOOK']
    assert '$0 ==' not in constants['HOOK']
    # Exact accepted stage mapping applies because regression bytes are unchanged against C2.
    assert git('show', SOURCE + ':scripts/kani-regression.sh') == git('show', '8e299aa624:scripts/kani-regression.sh')
    assert len(binding['stages']) == 33
    changed = git('diff', '--name-only', SOURCE).decode().splitlines()
    assert all(p.startswith(('.github/workflows/', 'scripts/kani3300-gate/')) for p in changed)
    # Qualify the checker on the prior failures, without running any workflow.
    import copy
    rejected = []
    mutations = [
        ('dispatch-only', lambda d: d.update(on={'workflow_dispatch': None})),
        ('runner-job-env', lambda d: d['jobs']['regression']['env'].update(BAD='${{ runner.temp }}')),
        ('shallow-export', lambda d: next(s for s in d['jobs']['regression']['steps'] if s.get('id') == 'export')['with'].update({'fetch-depth': 1})),
        ('nested-checkout', lambda d: next(s for s in d['jobs']['regression']['steps'] if s.get('id') == 'export')['with'].update(path='control/export')),
    ]
    for label, mutate in mutations:
        bad = copy.deepcopy(doc)
        mutate(bad)
        try:
            validate(bad)
        except AssertionError:
            rejected.append(label)
        else:
            raise AssertionError(('checker accepted mutation', label))
    print(json.dumps({'status': 'PASS', 'yaml_context_shell_binding_checks': 'PASS',
                      'known_error_mutations_rejected': rejected, 'files': len(binding['files']),
                      'subtrees': len(binding['subtrees']), 'submodules': len(binding['submodule_pins']),
                      'symlinks': len(binding['symlinks']), 'stages': 33,
                      'limitation': 'targeted offline checker, not full actionlint or runtime qualification'}, indent=2))


if __name__ == '__main__':
    main()
