#!/usr/bin/env python3
"""Reproduce the first two stages of Select's overlay base (Git apply only).

Purpose: the base on which a Network P1 overlay-admission patch must be
written (r4/SELECT-REQUESTS.md). No build, no proof tool, no runner execution.
Usage: reproduce-base.py VERIFAST_REPO SELECT_COMMIT OUT_DIR  (OUT_DIR must not exist)
Stages, as in Select's run-o26-refresh.sh @10e13a41:
  1. O26-PROFILE-MANIFEST.json patches_in_application_order on f76012fb
     -> `git diff` SHA256 6c4c5a77... (frozen20 applied diff)
  2. O26-REFRESH-PROFILE.json refresh_patches
     -> vf_mir_translator.ml SHA256 0862e635...
  3a. a1-tool-r17.py reconstruct(), first part: CALLER-ENTRY-MANIFEST strict
     patches (3), selected-runtime.py PATCHES (C4 chain, 10; read with
     ast.literal_eval, not executed), native c1-capture/c1-bound/c4-combined
     -> translator = manifest c4_base_translator_sha256, kernel = kernel_sha256.
The rest of stage 3 (zst, dead-code, focus scope, lifetime, slice, threshold,
selected, R, signature, reference-own, C, R15-R19 overlays) is NOT reproduced.
"""
import ast
import hashlib
import io
import json
import subprocess
import sys
import tarfile
from pathlib import Path

TOOL = 'f76012fb518703b1d98e243ac4f487f16877cfcb'
FROZEN20 = '6c4c5a7708af3bdec585abd308d37383a7de522a1aaecf2c01e1f94181324c25'
REFRESHED_TRANSLATOR = '0862e635075edd06a827c567710a3e1125ac03aa122e95149db755a1fddce48a'
TR = 'src/rust_frontend/vf_mir_translator/vf_mir_translator.ml'
KERNEL = 'src/verifast.ml'
HERE = Path(__file__).resolve().parent


def sh(*args, **kw):
    return subprocess.run(args, check=True, capture_output=True, **kw).stdout


def need(ok, why):
    if not ok:
        raise SystemExit('P1 BASE REFUSED: ' + why)


def main():
    need(len(sys.argv) == 4, 'usage: reproduce-base.py VERIFAST_REPO SELECT_COMMIT OUT_DIR')
    repo, select, out = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
    need(not out.exists(), 'OUT_DIR must not exist')
    src = out / 'src'
    src.mkdir(parents=True)
    tarfile.open(fileobj=io.BytesIO(sh('git', '-C', str(repo), 'archive', TOOL))).extractall(src, filter='data')
    sh('git', '-C', str(src), 'init', '-q')
    sh('git', '-C', str(src), 'add', '-A')
    sh('git', '-C', str(src), '-c', 'user.email=n@l', '-c', 'user.name=network', 'commit', '-qm', 'f76012fb')
    show = lambda rel: sh('git', '-C', str(HERE), 'show', f'{select}:research/challenge-8/{rel}')
    rows = []
    for stage, manifest, key in ((1, 'overnight-linkage/O26-PROFILE-MANIFEST.json', 'patches_in_application_order'),
                                 (2, 'overnight-assume-actual/O26-REFRESH-PROFILE.json', 'refresh_patches')):
        for row in json.loads(show(manifest))[key]:
            patch = show(row['path'])
            need(hashlib.sha256(patch).hexdigest() == row['sha256'], 'patch SHA ' + row['path'])
            subprocess.run(['git', '-C', str(src), 'apply', '-'], input=patch, check=True)
            rows.append({'stage': stage, 'path': row['path'], 'sha256': row['sha256']})
        if stage == 1:
            need(hashlib.sha256(sh('git', '-C', str(src), 'diff')).hexdigest() == FROZEN20, 'frozen20 diff SHA')
    translator = hashlib.sha256((src / TR).read_bytes()).hexdigest()
    need(translator == REFRESHED_TRANSLATOR, 'refreshed translator SHA')
    filesha = lambda rel: hashlib.sha256((src / rel).read_bytes()).hexdigest()

    def apply(rel, pin, allowed, before=None, after=None):
        patch = show(rel)
        need(hashlib.sha256(patch).hexdigest() == pin, 'patch SHA ' + rel)
        heads = [l[6:] for l in patch.decode().splitlines() if l.startswith(('--- a/', '+++ b/'))]
        need(set(heads) == set(allowed), 'patch touches unexpected source: ' + rel)
        for path, value in (before or {}).items():
            need(filesha(path) == value, 'base file ' + path + ' for ' + rel)
        subprocess.run(['git', '-C', str(src), 'apply', '-'], input=patch, check=True)
        for path, value in (after or {}).items():
            need(filesha(path) == value, 'result file ' + path + ' for ' + rel)
        rows.append({'stage': '3a', 'path': rel, 'sha256': pin})

    native_dir = 'cloud-build/sort4-caller-entry-native/'
    manifest = json.loads(show(native_dir + 'CALLER-ENTRY-MANIFEST.json'))
    need(manifest['tool_head'] == TOOL, 'caller manifest tool head')
    for index, (rel, pin) in enumerate(manifest['strict_patches']):
        apply(rel, pin, {TR, KERNEL} if index == 0 else {TR})
    need(filesha(KERNEL) == manifest['kernel_sha256'], 'strict kernel pin')
    runtime = show(native_dir + 'selected-runtime.py').decode()
    tree = ast.parse(runtime)
    consts = {t.id: node.value for node in tree.body if isinstance(node, ast.Assign)
              for t in node.targets if isinstance(t, ast.Name)}
    patches = ast.literal_eval(consts['PATCHES'])
    final_translator = ast.literal_eval(consts['FINAL_TRANSLATOR'])
    need(len(patches) == 10, 'C4 chain cardinality')
    field = lambda data, dotted: [data := data[k] for k in dotted.split('.')][-1]
    for profile_rel, pin_field, patch_rel, base_field, result_field in patches:
        legacy = json.loads(show(profile_rel))
        apply(patch_rel, field(legacy, pin_field), {TR},
              {TR: field(legacy, base_field)} if base_field else None,
              {TR: field(legacy, result_field)} if result_field else None)
    need(filesha(TR) == final_translator, 'frozen C4 translator')
    for profile_rel, patch_rel, pin_field in (
            ('cloud-build/sort4-native-opaque/NATIVE-C1-CAPTURE-PROFILE.json',
             'cloud-build/sort4-native-opaque/native-c1-capture-only.patch', 'patch_sha256'),
            ('cloud-build/sort4-native-c1-bound/NATIVE-C1-BOUND-TOOL-MANIFEST.json',
             'cloud-build/sort4-native-c1-bound/native-c1-bound.patch', 'patch_sha256'),
            ('cloud-build/sort4-native-c1-bound/NATIVE-C4-BOUND-MANIFEST.json',
             'cloud-build/sort4-native-c1-bound/native-c4-bound-combined.patch', 'combined_patch_sha256')):
        legacy = json.loads(show(profile_rel))
        need(legacy['tool_head'] == TOOL and legacy['kernel_sha256'] == manifest['kernel_sha256'], 'native legacy profile')
        apply(patch_rel, legacy[pin_field], {TR}, {TR: legacy['base_translator_sha256']},
              {TR: legacy.get('translator_sha256') or legacy['bound_translator_sha256']})
    need(filesha(TR) == manifest['c4_base_translator_sha256'], 'native C4 translator')
    translator = filesha(TR)
    record = {'tool': TOOL, 'select_commit': select, 'patches': rows, 'frozen20_diff_sha256': FROZEN20,
              'refreshed_translator_sha256': REFRESHED_TRANSLATOR, 'c4_base_translator_sha256': translator,
              'stage3_rest': 'NOT_REPRODUCED'}
    (out / 'base.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({'patches': len(rows), 'c4_base_translator_sha256': translator}))


if __name__ == '__main__':
    main()
