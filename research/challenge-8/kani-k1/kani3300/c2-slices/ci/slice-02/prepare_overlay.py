#!/usr/bin/env python3
"""Prepare local CI files only on exact stage2 source. Never build/push/dispatch."""
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
PACKET = HERE.parent.parent
WORKTREE = Path('/root/kani-fix-3300-c2-slices-w15')
SOURCE = 'b0a5a4fff9122ae4dabcc9808568c0d15fbe9b12'
RECIPE = '4f5dc3732c8fbaa94c814c41d184534148a1d312'


def git(*args):
    return subprocess.check_output(['git', '-C', str(WORKTREE), *args])


def main():
    assert git('rev-parse', 'HEAD').decode().strip() == SOURCE
    assert not git('status', '--porcelain=v1')
    manifest = (PACKET / 'slice-02/TEST-MANIFEST.json').read_bytes()
    source_slice = json.loads((PACKET / 'slice-02/SLICE.json').read_text())
    config = json.loads(git('show', RECIPE + ':.github/c2-slices/inputs.json'))
    config.update(source_sha=SOURCE, source_tree=source_slice['source_tree'],
                  source_parent=source_slice['base_sha'],
                  g0_input='ff3ce29e4f6694f28b0d6fcf025e70cfeae8f378',
                  test_manifest_sha256=hashlib.sha256(manifest).hexdigest(),
                  qualification_kind=source_slice['qualification_kind'],
                  integration_status='PENDING', integration_heads=[3, 4, 5],
                  accepted_parent_run='43696666260', accepted_recipe_overlay=RECIPE,
                  B1_dependency=source_slice['B1_dependency'])
    runner = git('show', RECIPE + ':.github/c2-slices/slice01_ci.py').decode()
    runner = runner.replace('"B1 parent mismatch"', '"source parent mismatch"')
    runner = runner.replace(
        '    "units": ["cargo", "test", "-p", "kani-compiler", "active_call_tests", "--", "--color", "never"],',
        '    "units": ["cargo", "test", "-p", "kani-compiler", "active_call_tests", "--", "--color", "never"],\n'
        '    "immutable-units": ["cargo", "test", "-p", "kani-compiler", "immutable_allocations::tests", "--", "--color", "never"],')
    runner = runner.replace('        good = execute(action, COMMANDS[action], out, expected)',
        '        elif action == "immutable-units":\n'
        '            expected = {"codegen_cprover_gotoc::context::immutable_allocations::tests::" + n: False for n in manifest["immutable_unit_names"]}\n'
        '        good = execute(action, COMMANDS[action], out, expected)')
    assert runner.count('"immutable-units"') == 2
    workflow = git('show', RECIPE + ':.github/workflows/uninit-quick.yml').decode()
    workflow = workflow.replace('C2 slices 01 ANALYSIS no-regression', 'C2 slices 02 IMMUTABLE qualification')
    workflow = workflow.replace('slice01_ci.py', 'slice02_ci.py').replace('c2-slices-01', 'c2-slices-02')
    anchor = '      - name: Quick and complete stage 1 manifest (311 unique selectors)\n'
    assert workflow.count(anchor) == 1
    workflow = workflow.replace(anchor,
        '      - name: Immutable allocations units (exactly 9)\n'
        "        if: ${{ !cancelled() && steps.source_guard.outcome == 'success' }}\n"
        '        run: python3 .github/c2-slices/slice02_ci.py immutable-units\n'
        '        env:\n'
        '          C2_EVIDENCE_DIR: ${{ runner.temp }}/c2-slices-02-evidence\n\n'
        '      - name: Cumulative Quick and stage 2 manifest (317 unique selectors)\n')
    ci = WORKTREE / '.github/c2-slices'
    ci.mkdir(parents=True, exist_ok=True)
    (ci / 'inputs.json').write_text(json.dumps(config, indent=2) + '\n')
    (ci / 'test-manifest.json').write_bytes(manifest)
    (ci / 'slice02_ci.py').write_text(runner)
    workflows = WORKTREE / '.github/workflows'
    for name in git('ls-tree', '-r', '--name-only', SOURCE, '--', '.github/workflows').decode().splitlines():
        (WORKTREE / name).unlink()
    (workflows / 'uninit-quick.yml').write_text(workflow)
    print('Prepared stage2 CI-only files; no build/push/dispatch.')


if __name__ == '__main__':
    main()
