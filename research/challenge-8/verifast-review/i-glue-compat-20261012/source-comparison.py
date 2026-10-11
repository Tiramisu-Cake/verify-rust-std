#!/usr/bin/env python3
"""Git-object/hash inventory only; never compiles, extracts MIR or runs proof tools."""
import hashlib
import json
from pathlib import Path
import subprocess

PROJECT = Path(__file__).resolve().parents[4]
TOOL = Path('/root/verifast-maintainer-slice-i')
I = 'b6cb276afd13107c2a90ca50acbb12ff0a992dd8'
V8 = 'a158398e336edce9817f62a55733a3470a986d7b'
BASE = 'f76012fb518703b1d98e243ac4f487f16877cfcb'
SNAPSHOT = '6283377b3729e0d6bebaf115f3c44f2e0187bc41'
I_PACKAGE = '4214cbe06cad959c17ec6e87d345f1063516b167'


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])


def raw(repo, sha, path):
    return git(repo, 'show', sha + ':' + path)


def digest(data):
    return None if data is None else hashlib.sha256(data).hexdigest()


def changed(sha):
    return set(git(TOOL, 'diff', '--name-only', BASE, sha).decode().splitlines())


def main():
    assert git(TOOL, 'merge-base', I, V8).decode().strip() == BASE
    profile_bytes = raw(PROJECT, SNAPSHOT, 'research/challenge-8/cloud-build/origin-layout/GLUE-PROFILE.json')
    profile = json.loads(profile_bytes)
    i_manifest_path = 'research/challenge-8/cloud-build/verifast-slice-binding-integration/manifest.json'
    i_manifest_bytes = raw(PROJECT, I_PACKAGE, i_manifest_path)
    i_manifest = json.loads(i_manifest_bytes)
    i_paths, v8_paths = changed(I), changed(V8)
    differences = []
    for path in sorted(i_paths | v8_paths):
        versions = []
        for sha in (BASE, I, V8):
            present = subprocess.run(['git', '-C', str(TOOL), 'cat-file', '-e', sha + ':' + path],
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
            versions.append(raw(TOOL, sha, path) if present else None)
        b, i, v = versions
        differences.append({'path': path, 'base_sha256': digest(b), 'i_sha256': digest(i),
            'v8_sha256': digest(v), 'i_changed_from_base': i != b, 'v8_changed_from_base': v != b,
            'i_v8_identical': i == v})
    common_paths = ['bin/rust/aliasing.rsspec', 'bin/rust/rust_belt/aliasing.rsspec',
                    'src/frontend/parser.ml', 'src/rust_frontend/vf_mir_translator/rustbelt.ml',
                    'src/rust_frontend/vf_mir_translator/vf_mir_annot_parser.ml']
    unchanged = {}
    for path in common_paths:
        i, v = raw(TOOL, I, path), raw(TOOL, V8, path)
        assert i == v
        unchanged[path] = digest(i)
    for path, expected in i_manifest['effective_hashes'].items():
        assert digest(raw(TOOL, I, path)) == expected, path
    profile_paths = {
        'translator_sha256': 'src/rust_frontend/vf_mir_translator/vf_mir_translator.ml',
        'kernel_sha256': 'src/verifast.ml', 'parser_sha256': 'src/rust_frontend/vf_mir_translator/rust_parser.ml',
        'prelude_sha256': 'bin/rust/prelude_core.rsspec', 'stdlib_sha256': 'bin/rust/std/lib.rsspec',
        'emitter_sha256': 'src/frontend/ocaml_expr_of_ast.ml', 'ast_sha256': 'src/frontend/ast.ml',
        'sexpression_sha256': 'src/SExpressionEmitter.ml', 'verify_expr_sha256': 'src/verify_expr.ml',
        'model_sha256': 'src/verifast1.ml', 'exporter_source_sha256': 'src/rust_frontend/vf_mir_exporter/src/lib.rs',
        'schema_sha256': 'src/rust_frontend/vf_mir/vf_mir.capnp',
        'refiner_main_source_sha256': 'src/refinement_checker/main.ml',
        'refiner_core_source_sha256': 'src/refinement_checker/refinement_checker.ml'}
    for key, path in profile_paths.items():
        assert digest(raw(TOOL, V8, path)) == profile[key], (key, path)
    patches = []
    for entry in profile['ordered_patch_chain']:
        data = raw(PROJECT, SNAPSHOT, entry['path'])
        assert digest(data) == entry['sha256'], entry['path']
        patches.append(dict(entry, changed_files=[line[6:] for line in data.decode().splitlines()
            if line.startswith('+++ b/')]))
    here = Path(__file__).resolve().parent
    runner_path = 'research/challenge-8/cloud-build/origin-layout/onecell-selected-drop.py'
    fixed = here / 'integration-runner' / runner_path
    service_raw = Path('/tmp/merge-b1-v8-evidence-a9613c24')
    inventory = json.loads((service_raw / 'files-sha256.json').read_text())
    service_inputs = {}
    for name in ['allprooflogs/checked-minimal-bridge/onecell-selected-drop/extraction.json',
                 'allprooflogs/checked-minimal-bridge/onecell-selected-drop/cases/positive/classification.json',
                 'allprooflogs/checked-minimal-bridge/onecell-selected-drop/cases/positive/proof-ast.ml']:
        actual = digest((service_raw / name).read_bytes())
        assert actual == inventory[name], name
        service_inputs[name] = actual
    result = {'kind': 'STATIC_COMPATIBILITY_BLOCKER_NO_COMBINED_TOOL_SOURCE',
        'start_checkpoint': '6a4afc1cb56e25ad242199c38ebd3bb6234dc2bf',
        'policy_commit': '6e1a8e59c56669abe5e6ec2013478e45ed2cc267',
        'i_tool': I, 'i_package': I_PACKAGE, 'glue_v8_tool': V8, 'glue_project_snapshot': SNAPSHOT,
        'common_base': BASE, 'i_manifest_sha256': digest(i_manifest_bytes),
        'glue_profile_sha256': digest(profile_bytes), 'i_effective_hashes': i_manifest['effective_hashes'],
        'v8_verified_source_pins': {profile_paths[k]: profile[k] for k in profile_paths},
        'ordered_v8_patch_chain': patches, 'changed_files': differences, 'byte_identical_common_paths': unchanged,
        'combined_tool_candidate': {'base': I, 'head': None, 'status': 'BLOCKED_NOT_PREPARED_UNBUILT_NOT_RUN'},
        'integration_runner': {'base_project_commit': SNAPSHOT, 'source_path': runner_path,
            'base_sha256': digest(raw(PROJECT, SNAPSHOT, runner_path)),
            'fixed_sha256': digest(fixed.read_bytes()),
            'f1_patch_sha256': digest((here / 'integration-runner-f1.patch').read_bytes()),
            'active_merge_runner_changed': False},
        'saved_f1_service_build': 'a9613c24-8f42-4008-981b-4df6b1e9206d',
        'saved_f1_service_inputs': service_inputs,
        'saved_f1_scope': 'AST admission service only; no raw proof/qualification review or v6->v8 transfer',
        'new_proof': False, 'cloud_seconds': 0, 'profile_accepted': False}
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
