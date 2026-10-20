#!/usr/bin/env python3
"""Static source/patch composition only; no compiler or actual proof preparation."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TOOL = Path('/root/verifast-merge-actual-glue')

def sha(data):
    return hashlib.sha256(data).hexdigest()

def git(*args):
    return subprocess.check_output(['git', '-C', str(TOOL), *args])

def main():
    baseline = (HERE/'R7-BASELINE-PROFILE-20261020.json').read_bytes()
    assert sha(baseline) == '13f0a97def3835372eb5e31de1ddc02cd9768df4b95c93f8c1076e59e0596b92'
    old = json.loads(baseline)
    profile = json.loads((HERE/'GLUE-PROFILE.json').read_bytes())
    assert profile['profile'] == 'experimental-merge-late-callback-recovery-r7-v1'
    assert profile['accepted'] is False and len(profile['ordered_patch_chain']) == 17
    assert profile['ordered_patch_chain'][:-1] == old['ordered_patch_chain']
    head = profile['effective_tool_commit']
    changed = git('diff', '--name-only', old['effective_tool_commit'], head).decode().splitlines()
    assert changed == ['src/rust_frontend/vf_mir_translator/vf_mir_translator.ml'], changed
    sources = {'src/rust_frontend/vf_mir_translator/vf_mir_translator.ml':'translator_sha256',
        'src/rust_frontend/vf_mir_exporter/src/lib.rs':'exporter_source_sha256',
        'src/rust_frontend/vf_mir/vf_mir.capnp':'schema_sha256',
        'src/refinement_checker/main.ml':'refiner_main_source_sha256',
        'src/refinement_checker/refinement_checker.ml':'refiner_core_source_sha256',
        'src/rust_frontend/vf_mir_translator/rust_parser.ml':'parser_sha256',
        'src/frontend/ast.ml':'ast_sha256','src/frontend/ocaml_expr_of_ast.ml':'emitter_sha256',
        'src/SExpressionEmitter.ml':'sexpression_sha256','src/verifast.ml':'kernel_sha256',
        'src/verifast1.ml':'model_sha256','src/verify_expr.ml':'verify_expr_sha256',
        'bin/rust/prelude_core.rsspec':'prelude_sha256','bin/rust/std/lib.rsspec':'stdlib_sha256'}
    for path, key in sources.items():
        assert sha(git('show', head+':'+path)) == profile[key], path
        if key != 'translator_sha256':
            assert profile[key] == old[key], path
    patches = []
    paths = set()
    for row in profile['ordered_patch_chain']:
        patch = ROOT/row['path']
        assert sha(patch.read_bytes()) == row['sha256'], patch
        patches.append(patch)
        for line in subprocess.check_output(['git','apply','--numstat',str(patch)],text=True).splitlines():
            paths.add(line.split('\t',2)[2])
    with tempfile.TemporaryDirectory(prefix='r7-static-source-composition-') as temp:
        target = Path(temp)
        subprocess.run(['git','init','--quiet',temp],check=True)
        tree = set(git('ls-tree','-r','--name-only',profile['verifast_commit']).decode().splitlines())
        for path in paths & tree:
            output = target/path
            output.parent.mkdir(parents=True,exist_ok=True)
            output.write_bytes(git('show',profile['verifast_commit']+':'+path))
        for patch in patches:
            subprocess.run(['git','-C',temp,'-c','core.whitespace=cr-at-eol','apply','--check',str(patch)],check=True)
            subprocess.run(['git','-C',temp,'-c','core.whitespace=cr-at-eol','apply','--whitespace=error',str(patch)],check=True)
        for path in paths:
            assert (target/path).read_bytes() == git('show',head+':'+path), path
    adapter = ROOT/'research/challenge-8/merge/cloud-build/provider-overlays.py'
    files = next(ast.literal_eval(n.value) for n in ast.parse(adapter.read_bytes()).body
        if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='FILES' for t in n.targets))
    assert len(files) == 18
    for path, expected in files.items():
        assert sha((ROOT/path).read_bytes()) == expected, path
    recipe = json.loads((ROOT/'research/challenge-8/cloud-build/recipes/merge.json').read_bytes())
    assert recipe['proof_paths'] == sorted(set(recipe['proof_paths']))
    for path in recipe['proof_paths']:
        assert (ROOT/path).is_file(), path
    print('R7 static17patch/18base/source-pin closure PASS; no compiler/proof credit')

if __name__ == '__main__':
    main()
