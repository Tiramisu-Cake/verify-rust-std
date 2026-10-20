#!/usr/bin/env python3
"""Static R9 patch/profile closure check; no compiler, preparation, or proof."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TOOL = Path('/root/verifast-merge-actual-glue')
PROFILE_NAME = 'experimental-merge-moving-gap-r10-v1'
BASELINE_SHA256 = '838ade9927ebba82b8df61283fdd8189e71b673ac91eadf897806d0bfaa80cc1'
R9_TOOL_PATHS = sorted([
    'src/rust_frontend/vf_mir_translator/vf_mir_translator.ml',
    'src/verifast.ml',
])
SOURCE_PINS = {
    'src/rust_frontend/vf_mir_exporter/src/lib.rs': 'exporter_source_sha256',
    'src/rust_frontend/vf_mir/vf_mir.capnp': 'schema_sha256',
    'src/refinement_checker/main.ml': 'refiner_main_source_sha256',
    'src/refinement_checker/refinement_checker.ml': 'refiner_core_source_sha256',
    'src/rust_frontend/vf_mir_translator/vf_mir_translator.ml': 'translator_sha256',
    'src/rust_frontend/vf_mir_translator/rust_parser.ml': 'parser_sha256',
    'src/frontend/ast.ml': 'ast_sha256',
    'src/frontend/ocaml_expr_of_ast.ml': 'emitter_sha256',
    'src/SExpressionEmitter.ml': 'sexpression_sha256',
    'src/verifast.ml': 'kernel_sha256',
    'src/verifast1.ml': 'model_sha256',
    'src/verify_expr.ml': 'verify_expr_sha256',
    'bin/rust/prelude_core.rsspec': 'prelude_sha256',
    'bin/rust/std/lib.rsspec': 'stdlib_sha256',
    'src/frontend/verifast0.ml': 'options_source_sha256',
    'src/vfconsole/vfconsole.ml': 'console_source_sha256',
    'src/vfide/vfide.ml': 'ide_source_sha256',
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(*args: str) -> bytes:
    return subprocess.check_output(['git', '-C', str(TOOL), *args])


def main() -> None:
    baseline_path = HERE / 'R9-BASELINE-PROFILE-20261020.json'
    baseline_raw = baseline_path.read_bytes()
    assert sha(baseline_raw) == BASELINE_SHA256
    baseline = json.loads(baseline_raw)
    profile_path = HERE / 'GLUE-PROFILE.json'
    profile_raw = profile_path.read_bytes()
    profile = json.loads(profile_raw)
    assert profile.get('schema') == 'smallsort-tracked-md-profile-v1'
    assert profile.get('profile') == PROFILE_NAME and profile.get('accepted') is False
    assert profile.get('qualification') == 'OPEN'
    chain = profile.get('ordered_patch_chain')
    assert isinstance(chain, list) and len(chain) == 19
    assert chain[:18] == baseline['ordered_patch_chain']
    assert chain[-2]['path'] == 'research/challenge-8/cloud-build/origin-layout/r8-owned-array-allocation.patch'
    assert chain[-1]['path'] == 'research/challenge-8/cloud-build/origin-layout/r9-guard-return-trace.patch'
    assert chain[-1]['sha256'] == profile['guard_return_trace_patch_sha256']
    assert profile['owned_array_allocation_patch_sha256'] == baseline['owned_array_allocation_patch_sha256']
    assert profile['owned_array_allocation_tool_commit'] == baseline['owned_array_allocation_tool_commit']

    head = profile['effective_tool_commit']
    assert git('rev-parse', 'HEAD').decode().strip() == head
    changed = git('diff', '--name-only', baseline['effective_tool_commit'], head).decode().splitlines()
    assert changed == R9_TOOL_PATHS, changed
    baseline_source = baseline['kernel_sha256']
    assert profile['kernel_sha256'] != baseline_source
    for relative, key in SOURCE_PINS.items():
        assert sha(git('show', f'{head}:{relative}')) == profile[key], relative
        if relative not in R9_TOOL_PATHS:
            assert profile[key] == baseline[key], relative

    patches = []
    touched = set()
    for row in chain:
        patch = ROOT / row['path']
        assert sha(patch.read_bytes()) == row['sha256'], patch
        patches.append(patch)
        for line in subprocess.check_output(['git', 'apply', '--numstat', str(patch)], text=True).splitlines():
            touched.add(line.split('\t', 2)[2])
    with tempfile.TemporaryDirectory(prefix='r10-static-source-composition-') as temp:
        target = Path(temp)
        subprocess.run(['git', 'init', '--quiet', temp], check=True)
        tree = set(git('ls-tree', '-r', '--name-only', profile['verifast_commit']).decode().splitlines())
        for relative in touched & tree:
            output = target / relative
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(git(f'show', f"{profile['verifast_commit']}:{relative}"))
        for patch in patches:
            subprocess.run(['git', '-C', temp, '-c', 'core.whitespace=cr-at-eol',
                            'apply', '--check', str(patch)], check=True)
            subprocess.run(['git', '-C', temp, '-c', 'core.whitespace=cr-at-eol',
                            'apply', '--whitespace=error', str(patch)], check=True)
        for relative in touched:
            assert (target / relative).read_bytes() == git(f'show', f'{head}:{relative}'), relative

    overlay = ROOT / 'research/challenge-8/merge/cloud-build/provider-overlays.py'
    overlay_tree = ast.parse(overlay.read_bytes())
    files = next(ast.literal_eval(node.value) for node in overlay_tree.body
                 if isinstance(node, ast.Assign) and
                 any(isinstance(target, ast.Name) and target.id == 'FILES' for target in node.targets))
    assert len(files) == 18
    for relative, expected in files.items():
        assert sha((ROOT / relative).read_bytes()) == expected, relative
    recipe_path = ROOT / 'research/challenge-8/cloud-build/recipes/merge.json'
    recipe = json.loads(recipe_path.read_bytes())
    assert recipe['proof_paths'] == sorted(set(recipe['proof_paths']))
    for relative in recipe['proof_paths']:
        assert (ROOT / relative).is_file(), relative
    required = {
        'research/challenge-8/cloud-build/origin-layout/R9-BASELINE-PROFILE-20261020.json',
        'research/challenge-8/cloud-build/origin-layout/r9-source-preflight.py',
        'research/challenge-8/cloud-build/origin-layout/r9-wiring-service-test.py',
        'research/challenge-8/cloud-build/origin-layout/r9-marker-service-test.py',
        'research/challenge-8/cloud-build/origin-layout/r9-guard-return-controls.py',
        'research/challenge-8/cloud-build/origin-layout/r9-guard-return-controls-service-test.py',
        'research/challenge-8/cloud-build/origin-layout/r8-freshness-controls.py',
        'research/challenge-8/cloud-build/origin-layout/r9-guard-return-trace.patch',
    }
    assert required <= set(recipe['proof_paths'])
    compile_preflight = (HERE / 'compile-preflight.sh').read_text()
    for pin in ('options_source_sha256', 'console_source_sha256', 'ide_source_sha256'):
        assert pin in compile_preflight
    print('R10 static19patch/18retained-base/17source-pin/recipe closure PASS; no compiler/proof credit')


if __name__ == '__main__':
    main()
