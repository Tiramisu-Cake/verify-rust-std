#!/usr/bin/env python3
"""Validate committed Q overlay/bindings without invoking setup or any Rust tool."""
from pathlib import Path
import ast
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import yaml

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
FULL = HERE / 'full-export'
PAYLOAD = FULL / '.github/c2-slices'
REPO = Path('/root/kani-fix-3300-sel1-c2-w15')
SOURCE_REPO = Path('/root/kani-fix-3300-sel1-c2-w14')
SOURCE = '14bc57fdb99960240c4944845a3d985c8af4dcf7'
TREE = '1efb6e4dfa69d346df8e23741d11839b1932403d'
BASE = '8e299aa6243bc5f06a29c51e98aafa9564478220'
RECIPE = '8288537e7c57b04d2462ff0c5bf1af38ab9d4451'


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(['git', '-C', str(REPO), *args])


def main():
    meta = read(HERE / 'LOCAL-CI.json')
    overlay = meta['commit']
    assert git('rev-parse', 'HEAD').decode().strip() == overlay
    assert not git('status', '--porcelain')
    assert git('rev-parse', overlay + '^').decode().strip() == SOURCE
    assert git('rev-parse', SOURCE + '^').decode().strip() == BASE
    assert git('rev-parse', SOURCE + '^{tree}').decode().strip() == TREE
    assert git('rev-parse', overlay + '^{tree}').decode().strip() == meta['tree']
    assert git('show', '-s', '--format=%an <%ae>%n%cn <%ce>', overlay).decode().splitlines() == [
        'Tiramisu-Cake <igkharin@gmail.com>'] * 2
    changed = git('diff', '--name-only', SOURCE, overlay).decode().splitlines()
    assert changed and all(p.startswith(('.github/workflows/', '.github/c2-slices/')) for p in changed)
    assert git('diff', '--binary', '--full-index', SOURCE, overlay) == (HERE / 'ci-only-template.patch').read_bytes()
    subprocess.run(['git', '-C', str(REPO), 'diff', '--check', SOURCE, overlay,
                    '--', '.', ':(glob,exclude)**/*.patch'], check=True)
    overlay_data = read(HERE / 'CI-OVERLAY.json')
    inventory = read(HERE / 'TEMPLATE-INVENTORY.json')
    request = read(HERE / 'CI-REQUEST.json')
    assert overlay_data['request_sha256'] == sha(HERE / 'CI-REQUEST.json')
    assert overlay_data['patch_sha256'] == inventory['ci_patch_sha256'] == sha(HERE / 'ci-only-template.patch')
    assert overlay_data['source_binding_sha256'] == request['source_binding_sha256'] == sha(HERE / 'SOURCE-BINDING.json')
    assert request['review_sha256'] == sha(HERE.parent / 'review/REVIEW.md')
    assert request['overlay_sha'] == overlay_data['overlay_sha'] == overlay
    assert request['source_sha'] == overlay_data['source_sha'] == SOURCE
    assert request['source_tree'] == overlay_data['source_tree'] == TREE
    for rel, digest in overlay_data['files_sha256'].items():
        file = FULL / rel
        assert sha(file) == digest == inventory['files']['full-export/' + rel]
        assert file.read_bytes() == git('show', overlay + ':' + rel)
        if file.suffix == '.py':
            ast.parse(file.read_text(), str(file))
        elif file.suffix == '.json':
            read(file)
    assert set(overlay_data['files_sha256']) == set(git('ls-tree', '-r', '--name-only', overlay,
                                                     '--', '.github/c2-slices').decode().splitlines()) | {'.github/workflows/uninit-quick.yml'}
    workflows = git('ls-tree', '-r', '--name-only', overlay, '--', '.github/workflows').decode().splitlines()
    assert workflows == ['.github/workflows/uninit-quick.yml']
    workflow = yaml.load((FULL / workflows[0]).read_text(), Loader=yaml.BaseLoader)
    assert set(workflow['on']) == {'workflow_dispatch'}
    job = workflow['jobs']['uninit']
    assert job['if'] == "${{ github.repository == 'Tiramisu-Cake/kani' }}"
    assert job['runs-on'] == 'ubuntu-24.04' and job['timeout-minutes'] == '120'
    assert workflow['env']['RUST_TEST_THREADS'] == '2'
    assert workflow['env']['SEL1_C2_SOURCE_DIR'] == '${{ github.workspace }}/export'
    assert workflow['env']['C2_EVIDENCE_DIR'] == '${{ runner.temp }}/sel1-c2-quick-evidence'
    assert job['steps'][0]['with']['path'] == 'control'
    assert job['steps'][1]['with']['path'] == 'export' and job['steps'][1]['with']['ref'] == SOURCE
    assert all(s['if'] == '${{ always() }}' for s in job['steps'][-2:])
    assert job['steps'][-1]['with']['retention-days'] == '14'
    assert job['steps'][-1]['with']['if-no-files-found'] == 'error'
    os.environ['SEL1_C2_SOURCE_DIR'] = str(SOURCE_REPO)
    sys.path.insert(0, str(PAYLOAD))
    import slice07_ci as ci
    config, manifest = ci.inputs()
    assert (config['source_sha'], config['source_tree'], config['source_parent']) == (SOURCE, TREE, BASE)
    assert config['recipe_sha256'] == request['workflow_sha256'] == sha(FULL / workflows[0])
    assert config['sel1_controls_sha256'] == sha(PAYLOAD / 'sel1-controls.json')
    selected = ci.suites(manifest)
    counts = {s: dict(selectors=len(r), ignored=sum(x['existing_path_ignore'] for x in r.values()))
              for (s, _), r in selected.items()}
    assert counts == {'kani': dict(selectors=53, ignored=3), 'expected': dict(selectors=408, ignored=6),
                      'ui': dict(selectors=17, ignored=0), 'script-based-pre': dict(selectors=3, ignored=0),
                      'json-handler': dict(selectors=17, ignored=0), 'std-checks': dict(selectors=2, ignored=0)}
    assert sum(r['selectors'] for r in counts.values()) == manifest['deduplicated_selector_count'] == 500
    controls = read(PAYLOAD / 'sel1-controls.json')
    assert controls['candidate'] == SOURCE and len(controls['selectors']) == 29
    assert sum(r['expected_result'] == 'SUCCESS' for r in controls['selectors']) == 12
    assert all('[expected] ' + r['file'].removeprefix('tests/') in selected['expected', 'expected']
               for r in controls['selectors'])
    for name in ['structural-manifest.json', 'structural-mixed.rs', 'structural_compare.py']:
        assert (PAYLOAD / name).read_bytes() == git('show', RECIPE + ':.github/c2-slices/' + name)
    old_s5 = json.loads(git('show', RECIPE + ':.github/c2-slices/sensitivity-manifest.json'))
    sensitivity = read(PAYLOAD / 'sensitivity-manifest.json')
    assert sensitivity['variants'] == old_s5['variants']
    assert ci.sensitivity.SOURCE_SHA == SOURCE
    assert sensitivity['source_candidate'] == SOURCE and sensitivity['source_tree'] == TREE
    for r in sensitivity['variants']:
        assert sha(PAYLOAD / r['patch']) == r['patch_sha256']
        subprocess.run(['git', '-C', str(SOURCE_REPO), 'apply', '--check', str(PAYLOAD / r['patch'])], check=True)
    structural = read(PAYLOAD / 'structural-manifest.json')
    calls = ci.structural.invocations(structural)
    assert len(calls) == 11 and sum(len(c['selectors']) for c in calls[7:]) == 18
    assert sum(r['expected_exit'] == 1 for r in calls) == 7
    binding = read(HERE / 'SOURCE-BINDING.json')
    assert binding['source_sha'] == SOURCE and binding['source_tree'] == TREE
    assert len(binding['compiler_unit_names']) == 76
    files = {f['path']: f['identity'] for g in manifest['groups'] for r in g['selectors'] for f in r['files']}
    assert all(binding['files'][p] == ident for p, ident in files.items())
    # Verify the live, exact read-only source checkout once, including all tracked non-CI entries.
    with tempfile.TemporaryDirectory() as tmp:
        ci.snapshot('package-static', Path(tmp))
        snapshot = read(Path(tmp) / 'source-package-static.json')
        assert not snapshot['problems']
        actual = {r['path']: r for r in snapshot['files']}
        for p, ident in binding['files'].items():
            if ci.ci_path(p):
                data = git('show', SOURCE + ':' + p)
                assert hashlib.sha256(data).hexdigest() == ident['sha256']
            else:
                assert actual[p]['sha256'] == ident['sha256']
                assert actual[p]['blob'] == actual[p]['actual_blob'] == ident['blob']
                assert actual[p]['mode'] == actual[p]['actual_mode'] == ident['mode']
    result = dict(status='PASS_STATIC_AND_SYNTHETIC_ONLY', source_sha=SOURCE, source_tree=TREE,
                  source_parent=BASE, overlay_sha=overlay, overlay_tree=meta['tree'],
                  CI_only=True, source_snapshot_entries=len(snapshot['files']),
                  source_binding_files=len(binding['files']), selectors=500, select_controls=29,
                  intended_select_success=12, intended_select_negative_or_refusal=17,
                  compiler_units=76, targeted_units=28, suite_counts=counts,
                  S5_variants=4, S5_patches_unchanged=True, S5_apply_check='PASS',
                  F7_invocations=11, F7_comparisons=18, F7_expected_exit1_invocations=7,
                  workflow='manual fork-only, sibling control/export, external evidence',
                  synthetic_tests=dict(quick=10, structural=15, sensitivity=13, seam_tool=10),
                  native_fmt_build_clippy_LLBC_Kani='NOT_RUN', push='NOT_RUN', CI='NOT_RUN',
                  cloud_spend=0, freeze=False, formal_proof_credit='NOT_ESTABLISHED')
    (HERE / 'VALIDATION.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
