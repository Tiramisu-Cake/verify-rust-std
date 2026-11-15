#!/usr/bin/env python3
"""Prepare exact-parent stage4 CI overlay. No native tools, push or dispatch."""
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
PACKET = HERE.parent.parent
WORKTREE = Path('/root/kani-fix-3300-c2-slices-w15')
SOURCE = '345cedfd67df679e326474385308349d609fc43d'
RECIPE = '34b8008f12ac909d53803ddb1a4da956c498c19f'
G0_INPUT = '7655cf9542'  # Resolved below to immutable full SHA.
NEW_UNITS = {
    'argument-size-units': {
        'filter': 'argument_size_tests',
        'native_names': ['kani_middle::transform::check_uninit::ty_layout::argument_size_tests::transfer_requires_complete_sized_storage'],
    },
    'marker-category-units': {
        'filter': 'marker_category_tests',
        'native_names': ['kani_middle::kani_functions::marker_category_tests::typed_marker_categories_remain_distinct'],
    },
}


def git(*args):
    return subprocess.check_output(['git', '-C', str(WORKTREE), *args])


def main():
    assert git('rev-parse', 'HEAD').decode().strip() == SOURCE
    assert not git('status', '--porcelain=v1')
    manifest = (PACKET / 'slice-04/TEST-MANIFEST.json').read_bytes()
    source_slice = json.loads((PACKET / 'slice-04/SLICE.json').read_text())
    config = json.loads(git('show', RECIPE + ':.github/c2-slices/inputs.json'))
    for key in ['nested_offset_integration_status', 'inherited_owner1_integration_heads']:
        config.pop(key, None)
    config.update(source_sha=SOURCE, source_tree=source_slice['source_tree'],
                  source_parent=source_slice['base_sha'],
                  g0_input=subprocess.check_output(['git', '-C', str(PACKET), 'rev-parse', G0_INPUT]).decode().strip(),
                  test_manifest_sha256=hashlib.sha256(manifest).hexdigest(),
                  qualification_kind=source_slice['qualification_kind'],
                  integration_status='PENDING_NATIVE_EXACT_HEAD4', integration_heads=[4, 5],
                  accepted_parent_run='43706759714', accepted_recipe_overlay=RECIPE,
                  B1_dependency=source_slice['B1_dependency'],
                  additional_units=NEW_UNITS, effective_targeted_unit_count=20,
                  packet_unit_expected_count_note='Packet scalar18 is inherited; effective exact filters are9+9+1+1=20.',
                  sensitivity={'status': 'DEFERRED_HEAD5', 'reason': 'Full8 strong oracle cases absent on head4; no substitute mutations.', 'required': '4/4 --force-rerun on first full strong-oracle head5'})
    runner = git('show', RECIPE + ':.github/c2-slices/slice03_ci.py').decode()
    anchor = '    "immutable-units": ["cargo", "test", "-p", "kani-compiler", "immutable_allocations::tests", "--", "--color", "never"],\n'
    assert runner.count(anchor) == 1
    runner = runner.replace(anchor, anchor + ''.join(
        '    ' + repr(name) + ': ' + repr(['cargo', 'test', '-p', 'kani-compiler', spec['filter'], '--', '--color', 'never']) + ',\n'
        for name, spec in NEW_UNITS.items()))
    anchor = '        good = execute(action, COMMANDS[action], out, expected)'
    assert runner.count(anchor) == 1
    runner = runner.replace(anchor,
        '        elif action in config["additional_units"]:\n'
        '            expected = {n: False for n in config["additional_units"][action]["native_names"]}\n' + anchor)
    workflow = git('show', RECIPE + ':.github/workflows/uninit-quick.yml').decode()
    workflow = workflow.replace('C2 slices 03 LAYOUT-RAW no-regression', 'C2 slices 04 STORAGE protocol and F6 qualification')
    workflow = workflow.replace('slice03_ci.py', 'slice04_ci.py').replace('c2-slices-03', 'c2-slices-04')
    workflow = workflow.replace('stage 3 manifest (318 unique selectors)', 'stage 4 manifest (413 unique selectors)')
    anchor = '      - name: Cumulative Quick and stage 4 manifest (413 unique selectors)\n'
    assert workflow.count(anchor) == 1
    extra = ''
    for action, label in [('argument-size-units', 'Argument size unit (exactly 1)'), ('marker-category-units', 'Marker category unit (exactly 1)')]:
        extra += ('      - name: ' + label + '\n'
                  "        if: ${{ !cancelled() && steps.source_guard.outcome == 'success' }}\n"
                  '        run: python3 .github/c2-slices/slice04_ci.py ' + action + '\n'
                  '        env:\n'
                  '          C2_EVIDENCE_DIR: ${{ runner.temp }}/c2-slices-04-evidence\n\n')
    workflow = workflow.replace(anchor, extra + anchor)
    ci = WORKTREE / '.github/c2-slices'
    ci.mkdir(parents=True, exist_ok=True)
    (ci / 'inputs.json').write_text(json.dumps(config, indent=2) + '\n')
    (ci / 'test-manifest.json').write_bytes(manifest)
    (ci / 'slice04_ci.py').write_text(runner)
    for name in git('ls-tree', '-r', '--name-only', SOURCE, '--', '.github/workflows').decode().splitlines():
        (WORKTREE / name).unlink()
    (WORKTREE / '.github/workflows/uninit-quick.yml').write_text(workflow)
    print('Prepared stage4 overlay only; native tools/push/dispatch NOT_RUN.')


if __name__ == '__main__':
    main()
