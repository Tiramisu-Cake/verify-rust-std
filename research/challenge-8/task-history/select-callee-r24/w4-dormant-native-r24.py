#!/usr/bin/env python3
"""Statically compose the dormant native overlay; never compile or prepare std."""
from __future__ import annotations
import argparse
import difflib
import hashlib
import importlib.util
import json
import re
from pathlib import Path
import subprocess
import tempfile

BASE_SHA256 = 'f83bd98b5d466314782e47ddc2d80356a0d0736b6cfc03ade59409eb01313806'
C5_SHA256 = 'bac19f063c2fee2bf62961f025ad27c3468c2322e9347d79165b2dae4438da43'
HISTORY_REL = Path('research/challenge-8/task-history/select-callee-r24')
TRANSLATOR_REL = Path('src/rust_frontend/vf_mir_translator/vf_mir_translator.ml')
PATCH_REL = Path('research/challenge-8/cloud-build/sort4-caller-entry-native/w4-dormant-native-r24.patch')
DEPENDENCIES = {
    'w4-c5-dormant-port-r24.patch': 'ea6de460a62fc63ff3b54a10bdb3836ac9855967719bdf300ccfa06d10eb43b4',
    'w4-dormant-call-binding-r24.py': '122faf335c643a03d5d91d071fa65e1dd5b7dd711a049efcd12837a38ba8201c',
    'w4-caller-input-certificates-r24.py': 'c65fbb26c91d98b2f5268e5e72301903d2f450e2f5c79ac17138f99712328ca8',
    'W4-CONTROL-DATA-ALL37-INPUTS.json': '1bc11197642bc057b6c7558777e56b6f8c04f0108d4115119193d7bb2f5ec8ea',
}

def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()

def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def generate(base: bytes, repo: Path) -> bytes:
    if sha(base) != BASE_SHA256:
        raise ValueError('exact F83 base required')
    history = repo / HISTORY_REL
    for name, expected in DEPENDENCIES.items():
        if sha((history / name).read_bytes()) != expected:
            raise ValueError('authoring dependency differs: ' + name)
    with tempfile.TemporaryDirectory(prefix='r24-dormant-static-') as tmp:
        root = Path(tmp)
        target = root / TRANSLATOR_REL
        target.parent.mkdir(parents=True)
        target.write_bytes(base)
        patch = (history / 'w4-c5-dormant-port-r24.patch').resolve()
        subprocess.run(['git', '-C', str(root), 'apply', '--check', str(patch)], check=True)
        subprocess.run(['git', '-C', str(root), 'apply', str(patch)], check=True)
        c5 = target.read_bytes()
        if sha(c5) != C5_SHA256:
            raise ValueError('C5 port output identity differs')
        subprocess.run(['git', '-C', str(root), 'apply', '--reverse', '--check', str(patch)], check=True)
        subprocess.run(['git', '-C', str(root), 'apply', '--reverse', str(patch)], check=True)
        if target.read_bytes() != base:
            raise ValueError('C5 patch reverse did not restore exact base')
    binding = load(history / 'w4-dormant-call-binding-r24.py', 'r24_dormant_binding_generator')
    inputs = load(history / 'w4-caller-input-certificates-r24.py', 'r24_dormant_inputs_generator')
    result = binding.generate(c5.decode())
    anchor = '  module Sort4R24W4Calls = struct\n'
    if result.count(anchor) != 1:
        raise ValueError('unique call module required')
    result = result.replace(anchor, inputs.ocaml_module(
        (history / 'W4-CONTROL-DATA-ALL37-INPUTS.json').read_bytes()) + anchor, 1)
    added_requests = set(re.findall(r'\b\w+_requested\b', result)) - set(re.findall(r'\b\w+_requested\b', base.decode()))
    if added_requests:
        raise ValueError('unrelated legacy diagnostic flags in closed port: ' + ', '.join(sorted(added_requests)))
    for name in ('validate_actual_scope_relocation', 'wrap_actual_deferred_suffix',
                 'run_actual_cmp_scope_controls', 'run_actual_deferred_scope_controls',
                 'run_actual_indexed_scope_controls'):
        if len(re.findall(r'let(?: rec)?\s+' + name + r'\b', result)) != 1 or result.count(name) < 2:
            raise ValueError('missing C5 helper definition/use: ' + name)
    if 'Sort4R24W4Caller.active := true' in result:
        raise ValueError('dormant candidate cannot activate caller')
    for symbol in ('checked_r24_pointer_outcome', 'Sort4R24CheckedPointerOutcomes',
                   'Sort4MutR24CheckedPointerOutcomes', 'Sort4MutableA1Primitives'):
        if result.count(symbol) != base.decode().count(symbol):
            raise ValueError('existing R24 branch inventory differs: ' + symbol)
    return result.encode()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--base', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    base = args.base.read_bytes()
    result = generate(base, args.repo)
    patch = ''.join(difflib.unified_diff(base.decode().splitlines(True),
        result.decode().splitlines(True), fromfile='a/' + TRANSLATOR_REL.as_posix(),
        tofile='b/' + TRANSLATOR_REL.as_posix())).encode()
    (args.repo / PATCH_REL).write_bytes(patch)
    args.output.write_bytes(result)
    manifest = {
        'schema': 'select-r24-w4-dormant-native-manifest-v1',
        'base_translator_sha256': BASE_SHA256, 'c5_port_translator_sha256': C5_SHA256,
        'result_translator_sha256': sha(result),
        'patch': {'path': PATCH_REL.as_posix(), 'sha256': sha(patch)},
        'authoring_dependencies': {str(HISTORY_REL / k): v for k, v in DEPENDENCIES.items()},
        'dormant': True, 'activation_paths': [], 'callee_qualification': False,
        'body_proof_run': False, 'caller_body_proof_admission': False,
        'accepted': False, 'publication_allowed': False, 'proof_credit': 0,
        'scope': 'Compile/identity only. C5 scope and ordinary call machinery dormant. No caller activation or qualification transfer.',
    }
    (args.repo / HISTORY_REL / 'W4-DORMANT-NATIVE-MANIFEST.json').write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'result_sha256': sha(result), 'patch_sha256': sha(patch),
                      'patch_bytes': len(patch), 'proof_credit': 0}))

if __name__ == '__main__':
    main()
