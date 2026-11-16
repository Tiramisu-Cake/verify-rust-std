#!/usr/bin/env python3
"""Static package audit only; no compiler/verifier invocation or publication."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

OLD = '6269319aecfb3328a2cffe8e2779432dbc346322'
TOOL = '0aac16ef62da9e9d5645782d458593e5d78143ba'
SOURCE = '9fa2f7f97760584f38738909625c064006d8a936'


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])


def audit(repo):
    here = repo/'ch8-prof-off-control'
    current = json.loads((here/'CI-REQUEST.json').read_text())
    previous = json.loads(git(repo, 'show', OLD+':ch8-prof-off-control/CI-REQUEST.json'))
    for key in ('rows','caps','budgets','std_sha','std_tree','tool_sha','tool_tree','changed_file_sha256','manifest_sha256'):
        assert current[key] == previous[key], key
    assert current['std_sha'] == SOURCE
    assert git(repo, 'show', OLD+':ch8-prof-off-control/manifest.json') == (here/'manifest.json').read_bytes()
    assert git(repo, 'rev-list', '--parents', '-n', '1', 'HEAD').decode().split() == [git(repo,'rev-parse','HEAD').decode().strip(), TOOL]
    assert not git(repo, 'status', '--porcelain=v1').strip()
    changed = git(repo, 'diff', '--name-only', TOOL, 'HEAD').decode().splitlines()
    assert sorted(changed) == current['ci_changed_paths']
    assert all(p.startswith(('ch8-prof-off-control/', '.github/workflows/')) for p in changed)
    for rel, digest in current['ci_payload_sha256'].items():
        assert hashlib.sha256((repo/rel).read_bytes()).hexdigest() == digest, rel
    spec = importlib.util.spec_from_file_location('batch_runner_audit', here/'runner.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    normalized = module.load_request(here/'CI-REQUEST.json')
    groups = module.batch_groups(normalized['rows'])
    assert [len(g) for g in groups] == [53, 9]
    for group in groups:
        argv = module.build_argv(Path('/synthetic/std'), Path('/synthetic/tool'), [r['selector'] for r in group], None, Path('/synthetic/out/export.json'))
        assert argv.count('--harness') == len(group)
        assert argv[argv.index('--harness-timeout')+1] == '600s'
        assert argv[argv.index('--jobs')+1] == '1'
        assert argv.count('--exact') == 1
        assert argv.count('--export-json') == 1
        assert '--default-unwind' not in argv
    return {'state':'PASS_STATIC_ONLY','previous_control':OLD,
            'control':git(repo,'rev-parse','HEAD').decode().strip(),
            'control_tree':git(repo,'rev-parse','HEAD^{tree}').decode().strip(),
            'control_parent':TOOL,'source':SOURCE,
            'manifest_rows':62,'manifest_rows_caps_budgets_source':'BYTE_OR_STRUCTURAL_IDENTICAL',
            'manifest_sha256':current['manifest_sha256'],
            'groups':[{'cfg':g[0]['cfg'],'rows':len(g)} for g in groups],
            'changed_paths':changed,'local_compiler_verifier':'NOT_RUN','proof_credit':'NONE'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--repo', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(audit(args.repo.resolve()), indent=2))
