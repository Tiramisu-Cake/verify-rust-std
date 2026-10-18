#!/usr/bin/env python3
"""Static source/hash/patch preflight only; never compile/extract/verify."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
TOOL = Path('/root/verifast-merge-actual-glue')
OLD_TOOL = 'd928cb1d7ac60c257daa537fa65577f41135f832'
TRANSLATOR = 'src/rust_frontend/vf_mir_translator/vf_mir_translator.ml'
OLD_DECL = b'      let first_fnmut_calls = ref []'
NEW_DECL = (b'      let first_fnmut_calls :\n'
            b'          (Ast.loc * [ `Continue | `Cleanup | `Other ]) list ref = ref []')


def git(*args):
    return subprocess.check_output(['git', '-C', str(TOOL), *args])


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    profile = json.loads((HERE/'GLUE-PROFILE.json').read_text())
    old = json.loads((HERE/'GLUE-PROFILE-FIRST-CALLBACK-PRE-TYPE-FIX-20261018.json').read_text())
    new_tool = profile['effective_tool_commit']
    before = git('show', f'{OLD_TOOL}:{TRANSLATOR}')
    after = git('show', f'{new_tool}:{TRANSLATOR}')
    assert before.count(OLD_DECL) == 1 and before.replace(OLD_DECL, NEW_DECL) == after
    assert git('diff', '--name-only', OLD_TOOL, new_tool).decode().splitlines() == [TRANSLATOR]
    assert after == (TOOL/TRANSLATOR).read_bytes()
    assert sha(after) == profile['translator_sha256']
    source_pins = {
        TRANSLATOR: 'translator_sha256',
        'src/rust_frontend/vf_mir_exporter/src/lib.rs': 'exporter_source_sha256',
        'src/rust_frontend/vf_mir/vf_mir.capnp': 'schema_sha256',
        'src/refinement_checker/main.ml': 'refiner_main_source_sha256',
        'src/refinement_checker/refinement_checker.ml': 'refiner_core_source_sha256',
        'src/rust_frontend/vf_mir_translator/rust_parser.ml': 'parser_sha256',
        'src/frontend/ast.ml': 'ast_sha256',
        'src/frontend/ocaml_expr_of_ast.ml': 'emitter_sha256',
        'src/SExpressionEmitter.ml': 'sexpression_sha256',
        'src/verifast.ml': 'kernel_sha256',
        'src/verifast1.ml': 'model_sha256',
        'src/verify_expr.ml': 'verify_expr_sha256',
        'bin/rust/prelude_core.rsspec': 'prelude_sha256',
        'bin/rust/std/lib.rsspec': 'stdlib_sha256',
    }
    for path, key in source_pins.items():
        assert sha(git('show', f'{new_tool}:{path}')) == profile[key], (path, key)
    assert after.count(b'first_fnmut_calls') == 4  # definition, two mentions in writer, consumer
    assert b'let translate_fn_call (fn_call_data_cpn : FnCallDataRd.t) (loc : Ast.loc)' in after
    allowed = {'translator_sha256', 'effective_tool_commit', 'first_callback_tool_commit',
               'previous_effective_tool_commit', 'first_callback_patch_sha256',
               'ordered_patch_chain', 'previous_first_callback_profile_sha256', 'build_candidate_revision'}
    changed = {key for key in set(old)|set(profile) if old.get(key) != profile.get(key)}
    assert changed == allowed, changed
    assert old['ordered_patch_chain'][:-1] == profile['ordered_patch_chain'][:-1]
    assert len(profile['ordered_patch_chain']) == 14
    patches = []
    paths = set()
    for row in profile['ordered_patch_chain']:
        path = REPO/row['path']
        assert sha(path.read_bytes()) == row['sha256'], row['path']
        patches.append(path)
        numstat = subprocess.check_output(['git', 'apply', '--numstat', str(path)], text=True)
        paths.update(line.split('\t', 2)[2] for line in numstat.splitlines())
    with tempfile.TemporaryDirectory(prefix='fnmut-type-source-only-') as temp:
        temp = Path(temp)
        subprocess.run(['git', 'init', '--quiet', str(temp)], check=True)
        tree = git('ls-tree', '-r', '--name-only', profile['verifast_commit']).decode().splitlines()
        for path in paths.intersection(tree):
            dest = temp/path
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(git('show', f"{profile['verifast_commit']}:{path}"))
        for patch in patches:
            subprocess.run(['git', '-C', str(temp), 'apply', '--check', str(patch)], check=True)
            subprocess.run(['git', '-C', str(temp), 'apply', '--whitespace=error', str(patch)], check=True)
        for path in paths:
            assert (temp/path).read_bytes() == git('show', f'{new_tool}:{path}'), path
    adapter = REPO/'research/challenge-8/merge/cloud-build/provider-overlays.py'
    pins = next(ast.literal_eval(node.value) for node in ast.parse(adapter.read_bytes()).body
                if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'FILES' for t in node.targets))
    assert len(pins) == 18
    for path, expected in pins.items():
        assert sha((REPO/path).read_bytes()) == expected, path
    recipe = json.loads((REPO/'research/challenge-8/cloud-build/recipes/merge.json').read_text())
    assert set(pins).issubset(recipe['proof_paths'])
    changes = []
    for path in recipe['proof_paths']:
        base = subprocess.check_output(['git', '-C', str(REPO), 'show', f'a8899491:{path}'])
        if base != (REPO/path).read_bytes():
            changes.append(path)
    assert set(changes) == {'research/challenge-8/cloud-build/origin-layout/GLUE-PROFILE.json',
                            'research/challenge-8/cloud-build/origin-layout/first-callback.patch'}, changes
    report = {'schema': 'first-fnmut-closed-type-source-preflight-v1',
              'tool': new_tool, 'translator_sha256': sha(after),
              'profile_sha256': sha((HERE/'GLUE-PROFILE.json').read_bytes()),
              'profile_changed_fields': sorted(changed), 'ordered_patches_checked_applied': len(patches), 'profile_source_pins_matched': len(source_pins),
              'reconstructed_source_files_equal_tool_commit': len(paths),
              'base_inputs_strict_hashes_matched': len(pins), 'proof_recipe_changed_paths': changes,
              'compiler_or_extraction_or_verifier_executed': False, 'result': 'PASS_STATIC_ONLY'}
    (HERE/'TYPE-FIX-SOURCE-PREFLIGHT-20261018.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
