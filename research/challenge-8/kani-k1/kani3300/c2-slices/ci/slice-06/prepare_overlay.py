#!/usr/bin/env python3
"""Prepare stage6 from accepted5 recipe. Git/Python only; no CI execution."""
import hashlib
import json
from pathlib import Path
import subprocess
HERE = Path(__file__).resolve().parent
PACKET = HERE.parent.parent
WORKTREE = Path('/root/kani-fix-3300-c2-slices-w15')
SOURCE = '3f5242bb1539fb88196d7e503b722f0905f2b46c'
RECIPE = 'ce56d3d467dd9aeec0fc7abc6a2444ee066e85f6'
G0_INPUT = '75c4267aa8'


def git(*args):
    return subprocess.check_output(['git', '-C', str(WORKTREE), *args])


def main():
    assert git('rev-parse', 'HEAD').decode().strip() == SOURCE
    assert not git('status', '--porcelain=v1')
    source = json.loads((PACKET/'slice-06/SLICE.json').read_text())
    manifest = (PACKET/'slice-06/TEST-MANIFEST.json').read_bytes()
    config = json.loads(git('show', RECIPE+':.github/c2-slices/inputs.json'))
    g0_sha = subprocess.check_output(['git','-C',str(PACKET),'rev-parse',G0_INPUT]).decode().strip()
    config.update(source_sha=SOURCE, source_tree=source['source_tree'], source_parent=source['base_sha'], g0_input=g0_sha,
                  test_manifest_sha256=hashlib.sha256(manifest).hexdigest(), qualification_kind=source['qualification_kind'],
                  integration_status='PENDING_NATIVE_EXACT_HEAD6', integration_heads=[6], accepted_parent_run='43715788377',
                  accepted_recipe_overlay=RECIPE)
    config['sensitivity']['classification_basis'] = 'Completed native verdict/N plus intended golden mismatch; repaired-write local var_N labels may renumber. See accepted5 run43715788377.'
    ci = WORKTREE/'.github/c2-slices'
    ci.mkdir(parents=True, exist_ok=True)
    (ci/'test-manifest.json').write_bytes(manifest)
    mutations = json.loads(git('show', RECIPE+':.github/c2-slices/sensitivity-manifest.json'))
    mutations.update(source_candidate=SOURCE, source_tree=source['source_tree'], base=source['base_sha'], execution='NOT_RUN')
    for row in mutations['variants']:
        data = git('show', RECIPE+':.github/c2-slices/'+row['patch'])
        assert hashlib.sha256(data).hexdigest() == row['patch_sha256']
        assert hashlib.sha256(git('show', SOURCE+':'+row['mutated_path'])).hexdigest() == row['input_sha256']
        target=ci/row['patch']; target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(data)
    (ci/'sensitivity-manifest.json').write_text(json.dumps(mutations,indent=2)+'\n')
    config['sensitivity']['manifest_sha256'] = hashlib.sha256((ci/'sensitivity-manifest.json').read_bytes()).hexdigest()
    (ci/'inputs.json').write_text(json.dumps(config,indent=2)+'\n')
    (ci/'sensitivity.py').write_bytes((HERE/'sensitivity.py').read_bytes())
    runner = git('show', RECIPE+':.github/c2-slices/slice05_ci.py')
    (ci/'slice06_ci.py').write_bytes(runner)
    workflow = git('show', RECIPE+':.github/workflows/uninit-quick.yml').decode()
    workflow = workflow.replace('C2 slices 05 CLOSURE and deferred integration qualification', 'C2 slices 06 E1 and composition qualification')
    workflow = workflow.replace('slice05_ci.py','slice06_ci.py').replace('c2-slices-05','c2-slices-06')
    workflow = workflow.replace('stage 5 manifest (460 unique selectors)', 'stage 6 manifest (471 unique selectors)')
    for path in git('ls-tree','-r','--name-only',SOURCE,'--','.github/workflows').decode().splitlines():
        (WORKTREE/path).unlink()
    (WORKTREE/'.github/workflows/uninit-quick.yml').write_text(workflow)
    print('Prepared exact-head6 overlay from accepted run43715788377; builds/push/dispatch NOT_RUN.')


if __name__ == '__main__':
    main()
