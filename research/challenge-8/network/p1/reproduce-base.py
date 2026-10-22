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
  3. a1-tool-r17.py reconstruct(), source part (build excluded): CALLER-ENTRY-MANIFEST strict
     patches (3), selected-runtime.py PATCHES (C4 chain, 10; read with
     ast.literal_eval, not executed), native c1-capture/c1-bound/c4-combined
     -> c4 base 66e266d3..., selected e484d9f9..., then R, signature,
     reference-own, C, R15/R16/R17 overlays -> final translator = profile
     actual_c2_recovery_overlay.result_sha256. The final build is not run.
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
SELECTED = 'e484d9f95202c876957a5d5ab349c6a40bc04dbcf813db4b373819402d807e64'
PROFILE = 'A1-ACTUAL-C3-R19-PROFILE-2026-10-22.json'
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
    c4_base = filesha(TR)
    rows.append({'checkpoint': '3a', 'translator_sha256': c4_base})
    # 3b: zst, dead-code identity, focus scope (+ lifetime), slice, threshold, selected.
    c1 = 'cloud-build/sort4-native-c1-bound/'
    for profile_rel, patch_rel, allowed in (
            (c1 + 'ZST-REPAIR-TOOL-MANIFEST.json', c1 + 'rust-zst-size.patch', {'src/verifast1.ml'}),
            (c1 + 'NATIVE-DEAD-CODE-IDENTITY-DIAGNOSTIC-MANIFEST.json', c1 + 'native-dead-code-identity-diagnostic.patch',
             {'src/verify_expr.ml', 'src/vfconsole/vfconsole.ml'})):
        legacy = json.loads(show(profile_rel))
        need(legacy['tool_head'] == TOOL and legacy['kernel_sha256'] == manifest['kernel_sha256'], 'legacy profile ' + patch_rel)
        apply(patch_rel, legacy['patch_sha256'], allowed,
              {path: legacy['files'][path]['base_sha256'] for path in allowed},
              {path: legacy['files'][path]['result_sha256'] for path in allowed})
    profile = json.loads(show(native_dir + PROFILE))
    focus = 'src/verify_expr.ml'
    focus_manifest_raw = show(c1 + 'NATIVE-RUST-FOCUS-DEAD-CODE-SCOPE-MANIFEST.json')
    need(hashlib.sha256(focus_manifest_raw).hexdigest() == profile['focus_dead_code_scope_manifest_sha256'], 'focus manifest pin')
    focus_manifest = json.loads(focus_manifest_raw)
    apply(c1 + 'native-rust-focus-dead-code-scope.patch', focus_manifest['patch_sha256'], {focus},
          {focus: focus_manifest['files'][focus]['base_sha256']}, {focus: focus_manifest['files'][focus]['result_sha256']})
    lifetime = profile.get('ghost_call_lifetime_inference')
    if lifetime is not None:
        need(lifetime.get('new_axiom_or_assumed_lemma') is False, 'lifetime overlay premise')
        apply(native_dir + 'ghost-call-lifetime-inference-r13.patch', lifetime['patch_sha256'], {focus},
              {focus: lifetime['base_sha256']}, {focus: lifetime['result_sha256']})
    threshold_raw = show(native_dir + 'STABLE-THRESHOLD-BINDING-PINS.json')
    selected_raw = show(native_dir + 'SELECTED-BRANCH-BINDING-PINS.json')
    need(hashlib.sha256(threshold_raw).hexdigest() == profile['stable_threshold_pins_sha256'], 'threshold pins')
    need(hashlib.sha256(selected_raw).hexdigest() == manifest['selected_binding_pins_sha256'], 'selected pins')
    threshold, selected_pins = json.loads(threshold_raw), json.loads(selected_raw)
    apply('caller-entry/verifast-slice-as-mut-ptr.patch', manifest['as_mut_ptr_patch_sha256'], {TR},
          {TR: manifest['c4_base_translator_sha256']}, {TR: manifest['as_mut_ptr_translator_sha256']})
    apply(native_dir + 'stable-threshold-binding.patch', threshold['patch_sha256'], {TR},
          {TR: threshold['base_translator_sha256']}, {TR: threshold['result_translator_sha256']})
    apply(native_dir + 'selected-branch-binding.patch', selected_pins['patch_sha256'], {TR},
          {TR: selected_pins['base_translator_sha256']}, {TR: SELECTED})
    rows.append({'checkpoint': '3b', 'translator_sha256': filesha(TR)})
    # 3c: R, native signature, reference-own, C, R15, R16, R17 phase, R17 c2 overlays.
    schema = 'src/rust_frontend/vf_mir/vf_mir.capnp'
    exporter = 'src/rust_frontend/vf_mir_exporter/src/lib.rs'
    r_before, r_rep, r_after = profile['r_before'], profile['r_representation_after'], profile['r_after']
    need(r_before[TR] == SELECTED and profile['c_before'] == r_after, 'R/C map shape')
    apply(native_dir + 'required-item-representation-hir-partition-r2-2026-10-20.patch', profile['r_patch_sha256'],
          {TR, schema, exporter}, r_before, r_rep)
    sig_raw = show(native_dir + 'NATIVE-SMALL-SORT-IMPL-SIGNATURE-MANIFEST.json')
    need(hashlib.sha256(sig_raw).hexdigest() == profile['native_signature_manifest_sha256'], 'signature manifest pin')
    sig = json.loads(sig_raw)
    need(sig['patch_sha256'] == profile['native_signature_patch_sha256'] and
         sig['files'][TR]['base_sha256'] == r_rep[TR] and sig['files'][TR]['result_sha256'] == r_after[TR], 'signature chain')
    apply(native_dir + 'native-small-sort-impl-signature.patch', sig['patch_sha256'], {TR}, {TR: r_rep[TR]}, {TR: r_after[TR]})
    ref = profile['shared_reference_own_normalization']
    need(ref['source'] == 'bin/rust/rust_belt/general.rsspec' and ref['new_axiom_or_assumed_lemma'] is False, 'reference-own manifest')
    apply(native_dir + 'shared-reference-own-normalization-r13.patch', ref['patch_sha256'], {ref['source']},
          {ref['source']: ref['base_sha256']}, {ref['source']: ref['result_sha256']})
    apply(native_dir + 'checked-threshold-contract.patch', profile['c_patch_sha256'], {TR},
          {TR: profile['c_before'][TR]}, {TR: profile['c_after'][TR]})

    def overlay(key, stem, source):
        decl = profile[key]
        raw = show(native_dir + stem)
        need(hashlib.sha256(raw).hexdigest() == decl['manifest_sha256'], 'overlay manifest ' + stem)
        m = json.loads(raw)
        need(m.get('new_axiom_or_assumed_lemma') is False and m.get('proof_credit') is False and
             m['patch_sha256'] == decl['patch_sha256'] and m['result_sha256'] == decl['result_sha256'], 'overlay declaration ' + key)
        apply(native_dir + decl['patch'], m['patch_sha256'], {source}, {source: m['base_sha256']}, {source: m['result_sha256']})

    overlay('actual_c1_recovery_overlay', 'ACTUAL-SORT4-C1-RECOVERY-R15-MANIFEST.json', TR)
    overlay('merge_fractions_ast_dump_overlay', 'MERGE-FRACTIONS-AST-DUMP-R15-MANIFEST.json', 'src/frontend/ocaml_expr_of_ast.ml')
    need(profile['authorization_phase_id'] == 'SORT4-ACTUAL-C2-2026-10-21-R17', 'profile authorization (R17 route)')
    for key, stem, source, flag in (
            ('r16_c1_phase_binding', 'R16-C1-PHASE-BINDING-MANIFEST.json', TR, None),
            ('strict_entry_diagnostic', 'STRICT-ENTRY-DIAGNOSTIC-R16-MANIFEST.json', KERNEL, None),
            ('actual_scope_relocation', 'ACTUAL-SORT4-SCOPE-RELOCATION-R16-MANIFEST.json', TR, 'actual_scope_relocation_enabled'),
            ('actual_deferred_scope_relocation', 'ACTUAL-SORT4-DEFERRED-SCOPE-R16-MANIFEST.json', TR, 'actual_deferred_scope_relocation_enabled'),
            ('actual_referent_address', 'ACTUAL-SORT4-REFERENT-ADDRESS-R16-MANIFEST.json', TR, 'actual_referent_address_enabled')):
        if flag is None or profile.get(flag) is True:
            overlay(key, stem, source)
    overlay('r17_c1_phase_binding', 'R17-C1-PHASE-BINDING-MANIFEST.json', TR)
    if profile.get('actual_c2_recovery_enabled') is True:
        overlay('actual_c2_recovery_overlay', 'ACTUAL-SORT4-C2-RECOVERY-R17-MANIFEST.json', TR)
    translator = filesha(TR)
    need(translator == profile['actual_c2_recovery_overlay']['result_sha256'], 'final translator = R19 c2-overlay result')
    rows.append({'checkpoint': '3c', 'translator_sha256': translator})
    record = {'tool': TOOL, 'select_commit': select, 'patches': rows, 'frozen20_diff_sha256': FROZEN20,
              'refreshed_translator_sha256': REFRESHED_TRANSLATOR, 'c4_base_translator_sha256': c4_base,
              'selected_translator_sha256': SELECTED, 'final_translator_sha256': translator, 'profile': PROFILE,
              'build': 'NOT_RUN (Cloud only)'}
    (out / 'base.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({'steps': len(rows), 'final_translator_sha256': translator}))


if __name__ == '__main__':
    main()
