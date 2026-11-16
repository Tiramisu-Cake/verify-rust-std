#!/usr/bin/env python3
"""Read-only static identity/delta checks; never invokes compilers/verifiers."""
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
CONTROL = Path('/root/kani-ch8-s1k-list-w13')
STD = Path('/root/verify-rust-std-ch8-s1-pprime-w13')
TOOL = Path('/root/kani-upstream-ch8-s1')
OLD = '8c8ac10d675fff41d5ec1b2684c6f673cd6bfaf2'
CANDIDATE = 'c03363b3b0a83fa9e78c4841720cb48ee7638c6a'
TOOL_SHA = '0aac16ef62da9e9d5645782d458593e5d78143ba'


def git(*args):
    return subprocess.check_output(['git', '-C', str(CONTROL), *args])


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    assert git('rev-parse', 'HEAD').decode().strip() == CANDIDATE
    assert git('rev-list', '--parents', '-n', '1', 'HEAD').decode().split() == [CANDIDATE, TOOL_SHA]
    assert not git('status', '--porcelain').strip()
    paths = git('diff', '--name-only', OLD, CANDIDATE).decode().splitlines()
    assert paths == ['ch8-s1-control/'+s for s in ['CI-REQUEST.json', 'check_package.py', 'runner.py', 'test_package.py', 'test_runner.py']], paths
    old_data = git('show', OLD+':ch8-s1-control/CI-REQUEST.json')
    data = (CONTROL/'ch8-s1-control/CI-REQUEST.json').read_bytes()
    old, current = json.loads(old_data), json.loads(data)
    assert sorted(k for k in current if current[k] != old[k]) == ['budgets', 'ci_payload_sha256']
    assert current['budgets'] == {**old['budgets'], 'list_seconds':1500, 'planned_list_seconds':1500}
    def literal_rows(value):
        return value.split(b'  "rows": [', 1)[1].split(b'  "ci_payload_sha256": {', 1)[0]
    assert literal_rows(old_data) == literal_rows(data)
    assert current['rows'] == old['rows'] and len(current['rows']) == 23
    old_runner = git('show', OLD+':ch8-s1-control/runner.py').decode()
    runner = (CONTROL/'ch8-s1-control/runner.py').read_text()
    def functions(source):
        return {n.name:ast.get_source_segment(source,n) for n in ast.parse(source).body if isinstance(n,ast.FunctionDef)}
    previous, present = functions(old_runner), functions(runner)
    unchanged = ['verify_source','_source_root','_variant_info','build_argv','ci_env','parse_export',
                 'binary_fingerprints','_run_variant','_row_base','_artifact_size','run_rows','main']
    for name in unchanged: assert previous[name] == present[name], name
    # Original post-execute inventory validation/freeze logic is exact, including PFC relation.
    assert previous['list_inventory'].split('    if (listing.get(',1)[1] == present['_freeze_inventory'].split('    if (listing.get(',1)[1]
    for rel, sha in current['ci_payload_sha256'].items():
        assert digest((CONTROL/rel).read_bytes()) == sha, rel
    for rel, sha in current['changed_file_sha256'].items():
        assert digest((STD/rel).read_bytes()) == sha, rel
    workflow = '.github/workflows/ch8-s1.yml'
    assert (CONTROL/workflow).read_bytes() == git('show', OLD+':'+workflow)
    env = {**os.environ, 'PYTHONDONTWRITEBYTECODE':'1', 'GITHUB_REPOSITORY':'Tiramisu-Cake/kani',
           'GITHUB_EVENT_NAME':'push', 'GITHUB_REF':'refs/heads/uninit-ci/ch8-s1k-list-w13',
           'GITHUB_RUN_ATTEMPT':'1', 'GITHUB_SHA':CANDIDATE}
    subprocess.run(['python3',str(CONTROL/'ch8-s1-control/check_package.py'),'control','--repo',str(CONTROL)], env=env, check=True, stdout=subprocess.PIPE)
    subprocess.run(['python3',str(CONTROL/'ch8-s1-control/runner.py'),'check-source','--std',str(STD),'--tool',str(TOOL)], env=env, check=True, stdout=subprocess.PIPE)
    subprocess.run(['git','-C',str(CONTROL),'diff','--check',TOOL_SHA,CANDIDATE],check=True)
    print(json.dumps({'state':'PASS_STATIC_ONLY','candidate':CANDIDATE,
        'tree':git('rev-parse','HEAD^{tree}').decode().strip(),'parent':TOOL_SHA,
        'delta_vs_previous':paths,'row_count':23,'literal_rows_sha256':digest(literal_rows(data)),
        'unchanged_functions':unchanged,'inventory_binding_logic':'BYTE_IDENTICAL',
        'workflow':'BYTE_IDENTICAL','std_sha':current['std_sha'],'std_tree':current['std_tree'],
        'budgets':current['budgets'],'source_and_control_identity':'PASS',
        'proof_rows':'ALL_23_NOT_RUN','proof_credit':'NONE'},indent=2))


if __name__ == '__main__':
    main()
