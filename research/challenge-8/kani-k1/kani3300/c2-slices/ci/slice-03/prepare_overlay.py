#!/usr/bin/env python3
"""Prepare CI-only stage3 overlay from the accepted stage2 recipe; never dispatch."""
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
PACKET = HERE.parent.parent
WORKTREE = Path('/root/kani-fix-3300-c2-slices-w15')
SOURCE = 'd0345ddf4f70d10caf5ee34ddca402867264379e'
RECIPE = '536f1d20d127987cdd860bc6367acc9fff90c5cb'
G0_INPUT = 'fc82cfd8b40d653b71ff2b2ba383682bc185165e'


def git(*args):
    return subprocess.check_output(['git', '-C', str(WORKTREE), *args])


def main():
    assert git('rev-parse', 'HEAD').decode().strip() == SOURCE
    assert not git('status', '--porcelain=v1')
    manifest = (PACKET / 'slice-03/TEST-MANIFEST.json').read_bytes()
    source_slice = json.loads((PACKET / 'slice-03/SLICE.json').read_text())
    config = json.loads(git('show', RECIPE + ':.github/c2-slices/inputs.json'))
    config.update(source_sha=SOURCE, source_tree=source_slice['source_tree'],
                  source_parent=source_slice['base_sha'], g0_input=G0_INPUT,
                  test_manifest_sha256=hashlib.sha256(manifest).hexdigest(),
                  qualification_kind=source_slice['qualification_kind'],
                  integration_status='PENDING', integration_heads=[4, 5],
                  nested_offset_integration_status='PENDING_HEAD4',
                  accepted_parent_run='43701587141', accepted_recipe_overlay=RECIPE,
                  B1_dependency=source_slice['B1_dependency'])
    # The accepted runner is byte-identical: no new execution or result policy.
    runner = git('show', RECIPE + ':.github/c2-slices/slice02_ci.py')
    workflow = git('show', RECIPE + ':.github/workflows/uninit-quick.yml').decode()
    workflow = workflow.replace('C2 slices 02 IMMUTABLE qualification',
                                'C2 slices 03 LAYOUT-RAW qualification')
    workflow = workflow.replace('slice02_ci.py', 'slice03_ci.py')
    workflow = workflow.replace('c2-slices-02', 'c2-slices-03')
    workflow = workflow.replace('stage 2 manifest (317 unique selectors)',
                                'stage 3 manifest (336 unique selectors)')
    assert 'slice02' not in workflow and '317 unique' not in workflow
    ci = WORKTREE / '.github/c2-slices'
    ci.mkdir(parents=True, exist_ok=True)
    (ci / 'inputs.json').write_text(json.dumps(config, indent=2) + '\n')
    (ci / 'test-manifest.json').write_bytes(manifest)
    (ci / 'slice03_ci.py').write_bytes(runner)
    for name in git('ls-tree', '-r', '--name-only', SOURCE, '--', '.github/workflows').decode().splitlines():
        (WORKTREE / name).unlink()
    (WORKTREE / '.github/workflows/uninit-quick.yml').write_text(workflow)
    print('Prepared stage3 CI-only files; no build/push/dispatch.')


if __name__ == '__main__':
    main()
