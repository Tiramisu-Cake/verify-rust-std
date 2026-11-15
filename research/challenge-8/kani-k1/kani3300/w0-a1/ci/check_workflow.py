#!/usr/bin/env python3
"""Offline YAML1.2/context/shell/binding checker. Never invokes a Rust tool."""
import ast
import copy
import hashlib
import importlib.util
import json
import os
import tempfile
from pathlib import Path
import re
import subprocess

import yaml

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('accepted_gatea_checker', HERE.parents[1] / 'sel1-c2/gatea/check_workflow.py')
gatea = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gatea)
ROWS = ['stable_freeze_u64_n32', 'unstable_general_nocopy_u64_n32', 'unstable_network_u64_n32',
        'stable_freeze_u64_n8', 'stable_freeze_u64_n16', 'unstable_general_nocopy_u64_n8',
        'unstable_general_nocopy_u64_n16', 'unstable_network_u64_n18']
BASE = 'control/scripts/ch8-w0-a1'


def validate(doc):
    assert set(doc) == {'name', 'on', 'permissions', 'concurrency', 'jobs'}
    assert doc['on'] == {'push': {'branches': ['uninit-ci/ch8-w0-a1-r1-*', 'uninit-ci/ch8-w0-a1-r2-*']}}
    assert doc['permissions'] == {'contents': 'read'}
    assert doc['concurrency'] == {'group': 'ch8-w0-a1', 'cancel-in-progress': False}
    assert set(doc['jobs']) == {'r1', 'r2'}
    for stage, job in doc['jobs'].items():
        assert job['if'] == "${{ github.repository == 'Tiramisu-Cake/kani' && startsWith(github.ref, 'refs/heads/uninit-ci/ch8-w0-a1-" + stage + "-') }}"
        assert job['runs-on'] == 'ubuntu-24.04'
        assert job['timeout-minutes'] == (60 if stage == 'r1' else 90)
        assert job['strategy'] == {'fail-fast': False, 'max-parallel': 1, 'matrix': {'root': ROWS} if stage == 'r1' else {'pin': ['baseline', 'sel1']}}
        gatea.check_contexts(job['if'], {'github', 'needs', 'vars', 'inputs'})
        gatea.check_contexts(job.get('env', {}), {'github', 'needs', 'strategy', 'matrix', 'vars', 'secrets', 'inputs'})
        ids = {s['id'] for s in job['steps'] if 'id' in s}
        assert len(ids) == sum('id' in s for s in job['steps'])
        for step in job['steps']:
            assert ('uses' in step) != ('run' in step)
            allowed = {'github', 'needs', 'strategy', 'matrix', 'vars', 'secrets', 'inputs', 'env', 'steps', 'job'}
            gatea.check_contexts({k:v for k,v in step.items() if k != 'env'}, allowed)
            gatea.check_contexts(step.get('env', {}), allowed | {'runner'})
            assert all(x in ids for x in re.findall(r'steps\.([\w-]+)\.', json.dumps(step)))
            if 'run' in step:
                shell = re.sub(r'\$\{\{.*?\}\}', 'STATIC', step['run'], flags=re.S)
                subprocess.run(['bash', '-n'], input=shell.encode(), check=True, capture_output=True)
                for code in re.findall(r"python3 - <<'PYCODE'\n(.*?)\nPYCODE", shell, re.S):
                    tree = ast.parse(code)
                    assert not any(isinstance(n, ast.Constant) and isinstance(n.value, str) and r'\n' in n.value for n in ast.walk(tree)), 'literal backslash-n in generated inline Python output'
        steps = {s['name']:s for s in job['steps']}
        checkouts = [s for s in job['steps'] if s.get('uses', '').startswith('actions/checkout@')]
        assert len(checkouts) == 2
        assert checkouts[0]['with'] == {'ref':'${{ github.sha }}','path':'control','fetch-depth':2,'persist-credentials':False}
        assert checkouts[1]['with'] == {'ref':'${{ steps.pin.outputs.sha }}','path':'export','fetch-depth':2,'persist-credentials':False}
        guard = steps['Require first attempt and same-tree trigger']
        assert guard['working-directory'] == 'control'
        assert "os.environ['GITHUB_RUN_ATTEMPT'] == '1'" in guard['run']
        assert "head == os.environ['GITHUB_SHA']" in guard['run']
        assert "'HEAD^1^{tree}'" in guard['run'] and "'HEAD^'" in guard['run']
        assert steps['Python wrapper preflight']['working-directory'] == BASE
        assert steps['Setup this pin dependencies'] == {'name':'Setup this pin dependencies','uses':'./export/.github/actions/setup','with':{'os':'ubuntu-24.04','kani_dir':'export'}}
        assert steps['Build exact export']['working-directory'] == 'export'
        assert steps['Build exact export']['run'] == 'cargo build-dev -- --release'
        run = steps['Run exact cases once']
        assert run.get('working-directory', '.') == '.'
        if stage == 'r1':
            assert '--std "$RUNNER_TEMP/ch8-a1-std"' in run['run']
            assert '--repo "$GITHUB_WORKSPACE/export"' in run['run']
            assert '--binary "$GITHUB_WORKSPACE/export/scripts/kani"' in run['run']
            assert '--out "$RUNNER_TEMP/ch8-a1-receipt/${{ matrix.root }}"' in run['run']
            assert '<= 2340' in run['run']
            prepare = steps['Prepare isolated std']
            assert prepare.get('working-directory', '.') == '.'
            assert '--destination "$RUNNER_TEMP/ch8-a1-std"' in prepare['run']
        else:
            assert "for row in req['r2']['rows']:" in run['run'] and '<= 1140' in run['run']
            assert "'export/scripts/kani'" in run['run']
            assert "'--stage', 'r2'" in run['run']
        assert steps['Fallback NOT_RUN receipts']['if'] == 'always()'
        assert 'if not receipt.exists():' in steps['Fallback NOT_RUN receipts']['run']
        assert steps['Bound receipt upload']['if'] == 'always()'
        upload = steps['Upload bounded receipts']
        assert upload['if'] == 'always()'
        assert upload['env'] == {'RECEIPT_ROOT':'${{ runner.temp }}/ch8-a1-receipt'}
        assert upload['with']['path'] == '${{ env.RECEIPT_ROOT }}/'
        assert upload['with']['retention-days'] == 7 and upload['with']['if-no-files-found'] == 'error'


def main():
    doc = yaml.load((HERE/'ch8-w0-a1.yml').read_text(), Loader=gatea.Loader)
    validate(doc)
    mutations = [
        ('dispatch-only', lambda d:d.update(on={'workflow_dispatch':None})),
        ('grandparent-tree-guard', lambda d:d['jobs']['r1']['steps'][1].update(run=d['jobs']['r1']['steps'][1]['run'].replace('HEAD^1^{tree}', 'HEAD~2^{tree}'))),
        ('literal-newline-output', lambda d:d['jobs']['r1']['steps'][1].update(run=d['jobs']['r1']['steps'][1]['run'].replace("'\\n'", "'\\\\n'"))),
        ('runner-job-env', lambda d:d['jobs']['r1'].update(env={'BAD':'${{ runner.temp }}'})),
        ('shallow-export', lambda d:d['jobs']['r1']['steps'][4]['with'].update({'fetch-depth':1})),
        ('nested-export', lambda d:d['jobs']['r1']['steps'][4]['with'].update(path='control/export')),
        ('wrong-setup-cwd', lambda d:d['jobs']['r1']['steps'][6]['with'].update(kani_dir='control/export')),
        ('wrong-binary-prefix', lambda d:d['jobs']['r1']['steps'][9].update(run=d['jobs']['r1']['steps'][9]['run'].replace('$GITHUB_WORKSPACE/export/scripts/kani','$GITHUB_WORKSPACE/control/export/scripts/kani'))),
    ]
    rejected=[]
    for name, mutate in mutations:
        bad=copy.deepcopy(doc); mutate(bad)
        try: validate(bad)
        except AssertionError: rejected.append(name)
        else: raise AssertionError(('mutation accepted',name))
    try: yaml.load('a: 1\na: 2\n', Loader=gatea.Loader)
    except AssertionError: rejected.append('duplicate-yaml-key')
    else: raise AssertionError('duplicate key accepted')
    req=json.loads((HERE/'CI-REQUEST.json').read_text())
    assert [r['id'] for r in req['r1']['rows']] == ROWS
    assert len(req['r2']['rows']) == 6
    assert req['r1']['aggregate_job_minutes'] == 480 and req['r2']['aggregate_job_minutes'] == 180
    assert req['dispatches'] == {'mandatory':2,'reserve':1,'a1_cap':3,'item1_cap':18,'overall_cap':32,'retry':'NONE'}
    import sys
    sys.path.insert(0,str(HERE))
    import a1
    a1.load_request()
    for row in req['r1']['rows']:
        argv=row['argv']
        assert argv[0:5] == ['<KANI>','verify-std','-Z','unstable-options','./library']
        assert argv[argv.index('--harness')+1] == row['selector'] and '--exact' in argv
        assert argv[argv.index('--harness-timeout')+1] == '600s'
        assert argv[argv.index('--jobs')+1] == '1'
        assert argv[-3:] == ['--cbmc-args','--object-bits','12']
        assert '--no-assert-contracts' in argv and 'uninit-checks' in argv
        assert row['environment'] == {'NO_COLOR':'1','RUSTFLAGS':'--cfg kani_smallsort_controls'}
    assert all('valid-value' not in x and 'disable' not in x for stage in ['r1','r2'] for r in req[stage]['rows'] for x in r['argv'])
    repo=Path('/root/kani-fix-ch8-w0-a1-w15')
    def git(*args):return subprocess.check_output(['git','-C',str(repo),*args])
    counts={}
    for name,pin in req['pins'].items():
        binding=json.loads((HERE/pin['binding']).read_text())
        assert binding['export_sha']==pin['sha'] and binding['export_tree']==pin['tree']
        assert git('rev-parse',pin['sha']+'^{tree}').decode().strip()==pin['tree']
        for path,digest in binding['files'].items():
            assert hashlib.sha256(git('show',pin['sha']+':'+path)).hexdigest()==digest,path
        for path,oid in binding['subtrees'].items():
            assert git('rev-parse',pin['sha']+':'+path).decode().strip()==oid,path
        tests=set(git('ls-tree','-r','--name-only',pin['sha'],'--','tests/expected/uninit','tests/json-handler').decode().splitlines())
        assert tests == {p for p in binding['files'] if p.startswith(('tests/expected/uninit/','tests/json-handler/'))}
        counts[name]={'files':len(binding['files']),'tests':len(tests),'subtrees':len(binding['subtrees'])}
    for row in req['r2']['rows']:
        assert hashlib.sha256((HERE/row['fixture']).read_bytes()).hexdigest()==row['fixture_sha256']
    assert hashlib.sha256((HERE/req['std']['patch']).read_bytes()).hexdigest()==req['std']['patch_sha256']
    assert (HERE/'CI-REQUEST.json').read_bytes() == (HERE.parent/'CI-REQUEST.json').read_bytes()
    stdrepo=Path('/root/verify-rust-std-ch8-w0-a1-w15')
    manifest=json.loads((HERE.parent/'std/MANIFEST.json').read_text())
    def stdgit(*args, env=None):
        return subprocess.check_output(['git','-C',str(stdrepo),*args],env=env)
    assert stdgit('rev-parse','HEAD').decode().strip() == req['std']['package_sha'] == manifest['commit']
    assert set(stdgit('diff','--name-only',manifest['parent'],manifest['commit']).decode().splitlines()) == {
        'library/core/src/slice/sort/shared/smallsort/verify.rs',
        'library/core/src/slice/sort/shared/smallsort/verify/wave0_a1.rs'}
    for path,digest in req['std']['patched_files'].items():
        assert hashlib.sha256(stdgit('show',manifest['commit']+':'+path)).hexdigest()==digest
    for artifact,base,expected_library in [
        ('combined-from-70ba.patch',manifest['frozen_source_commit'],manifest['library_tree']),
        ('overlay-from-6075.patch',manifest['parent'],manifest['library_tree'])]:
        patch=HERE.parent/'std'/artifact
        assert hashlib.sha256(patch.read_bytes()).hexdigest()==manifest['patches'][artifact]['sha256']
        with tempfile.TemporaryDirectory(prefix='ch8-a1-index-') as temp:
            env=dict(os.environ,GIT_INDEX_FILE=str(Path(temp)/'index'))
            stdgit('read-tree',base,env=env)
            stdgit('apply','--cached','--check',str(patch),env=env)
            stdgit('apply','--cached',str(patch),env=env)
            tree=stdgit('write-tree',env=env).decode().strip()
            assert stdgit('rev-parse',tree+':library').decode().strip()==expected_library
            if artifact=='overlay-from-6075.patch': assert tree==manifest['tree']
    assert not (repo.parent/'Cargo.toml').exists(), 'sibling checkout parent cannot be a Cargo workspace'
    print(json.dumps({'status':'PASS','yaml':'YAML1.2_DUPLICATES_REJECTED','mutations_rejected':rejected,'source_binding':counts,'rows':{'r1':8,'r2':6},'limitation':'offline targeted checker; no actionlint, Rust compilation or runtime verification'},indent=2))

if __name__ == '__main__': main()
