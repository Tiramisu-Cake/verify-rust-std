#!/usr/bin/env python3
"""Same-tool R24 requalification of the frozen const-callee matrix.

This wrapper only records source-reported qualification inputs.  It does not
publish a caller summary or assign independent proof credit. After fresh
qualification, a separate refusal-only driver checks contract inputs; it never
admits a caller body.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from typing import Any, Callable


SCHEMA = 'select-r24-w4-const-qualification-v1'
SUMMARY_REL = Path('cases/r24-w4-const-qualification/W4-CONST-QUALIFICATION.json')
AUDIT_REL = Path('cases/r24-w4-const-qualification/W4-CONST-QUALIFICATION-AUDIT.json')
WORK_REL = Path('cases/r24-w4-const-qualification/work')
MODE_REL = Path('research/challenge-8/task-history/select-callee-r24/W4-CONST-QUALIFICATION-MODE.json')
MODE_SHA256 = '6d429030afb060ed6e65588163ace77bdd0c6ebb6ac6be3a01809dcb857b9a11'
CAPTURE_MODE_REL = Path('research/challenge-8/task-history/select-callee-r24/W4-CAPTURE-MODE.json')
CAPTURE_MODE_SHA256 = '1d251b0d1a48ec1c3310e9ae179f7a750b8608ec57c31a4da3b46ce6e12fe0a3'
CAPTURE_PINS_REL = Path('research/challenge-8/task-history/select-callee-r24/W4-CAPTURE-PINS.json')
CAPTURE_PINS_SHA256 = 'f81b062111436a7ab8a40e9776fdc1d1138a7861b5a6d95e018201ee93d5b6a0'
NATIVE_FINGERPRINT_PINS_REL = Path('research/challenge-8/task-history/select-callee-r24/W4-NATIVE-FINGERPRINT-PINS.json')
NATIVE_FINGERPRINT_PINS_SHA256 = 'dc0e26e5bf6af68ef0a3b28f8c6410d13b1b8d1bd6848976b1ef3efdb106844d'
W4_INPUTS_REL = Path('research/challenge-8/task-history/select-callee-r24/W4-INPUTS-QUALIFICATION.json')
W4_INPUTS_SHA256 = '03a5e3b3afa601592a61e3f7a01c1485e674ac9f03ff8689c52c220361d75dce'
CONST_QUALIFICATION_REL = Path('research/challenge-8/task-history/select-callee-r24/CONST-CALLEE-QUALIFICATION.json')
CONST_QUALIFICATION_SHA256 = '1d50cc12011cd8bae26f1a69fee7e43579ab3ef9bacf5708eac33875a4a00794'
P2_INTERFACE_REL = Path('research/challenge-8/task-history/select-callee-r23/P2-INTERFACE.json')
P2_INTERFACE_SHA256 = '656b15c1f295db2f7935f14067cf17067f04186994009715772157eb97fd2322'
FRACTIONAL_PINS_REL = Path('research/challenge-8/task-history/select-callee-r23/FRACTIONAL-FINGERPRINT-INPUT.json')
FRACTIONAL_PINS_SHA256 = '939eb916bb8a0b460c698e0a297a8fc12acdadf68fa7e10d297b4b7ce5de67b5'
TARGET_MAP_REL = Path('research/challenge-8/task-history/select-callee-r24/CONTROL-TARGETS.json')
TARGET_MAP_SHA256 = 'a6bde55bf08490352cae04fbaa61aa85f33a94890d52e8fe3147f50859e588dc'
TARGET_INTENT_REL = Path('target-inputs/const-control-target-intent.json')
TARGET_INTENT_RECEIPT_REL = Path('target-inputs/const-control-target-intent-receipt.json')
TARGET_INTENT_SCHEMA = 'select-r24-w4-const-derived-target-intent-v1'
CONSEQUENCE_REL = Path('research/challenge-8/cloud-build/select-callee-r24-w4-const-consequence.py')
CONSEQUENCE_SHA256 = 'bf89a183e39fddf17ea6247859775b4d0bb72febae635df67b15fccf744de420'
CONTRACT_REL = Path('research/challenge-8/cloud-build/select-callee-r24-w4-contract-inputs.py')
CONTRACT_SHA256 = '9d91e549f41e40899afb4a97de2c1329d2abf188f6c5c37a91543cfb54ba64fa'
CONTRACT_MODE_REL = Path('research/challenge-8/task-history/select-callee-r24/W4-CONTRACT-INPUTS-MODE.json')
CONTRACT_MODE_SHA256 = '2ffe2da0dc2cd5356a6a83bae7dcae27dad15cac720e5a24c9cf616c39894707'
R21_ENTRY_REL = Path('research/challenge-8/cloud-build/select-callee-r21-fractional-proof-entry.py')
R21_ENTRY_SHA256 = '0947e128a10cadd69c615b5da54b5647a31568ecc0f7e0d229681c862c54263d'
R21_AUDIT_REL = Path('research/challenge-8/cloud-build/select-callee-r21-proof-audit.py')
R21_AUDIT_SHA256 = '336d5c4c2b24917f91bcca70a6c443ae45a66f3cc024eca5580f2684fb08baed'
O26_RECIPE_REL = Path('research/challenge-8/cloud-build/o26-refresh-recipe.py')
O26_RECIPE_SHA256 = '2cd963cc3d28c69370260cd2154e7284e189fea953928c3fc829f2fd53766af3'
CAPTURE_REL = Path('research/challenge-8/overnight-assume-actual/capture.py')
CAPTURE_SHA256 = 'ffc3653263e86c5afa4f82440f10a2207e75ad8083bdad5f784597fe0dbaa84f'
PREPARE_REL = Path('research/challenge-8/overnight-assume-actual/prepare.py')
PREPARE_SHA256 = '8edc8d63ce49fb60701dd1eb0005a4af5f3a046234fee9d631345de68fdbae49'
CAPTURE_CLOUD_OVERLAY_SHA256 = 'eddf624a7ecc59b9fac4595fc95629e5ab22e26efd12be2ba53e44fbbc40ff66'
PREPARE_CLOUD_OVERLAY_SHA256 = '79de389749b4a40b9a1fa364993931055e5309902bd422d226c405eda8b028b2'
O26_PROVIDER_REL = Path('research/challenge-8/cloud-build/provider.py')
O26_PROVIDER_SHA256 = '771970340f4fa928063cfa25db451535eb60ee1b246ef63c3cda4689842be616'
O26_BASE_REL = Path('research/challenge-8/cloud-build/o26-recipe.py')
O26_BASE_SHA256 = '464eef45b08b8724eba949289eff9cd745f48d65d0031ffae5675738856d562c'
O26_OVERLAY_FILES = {
    'research/challenge-8/overnight-assume-actual/prepare.py':
        ('8edc8d63ce49fb60701dd1eb0005a4af5f3a046234fee9d631345de68fdbae49',
         '79de389749b4a40b9a1fa364993931055e5309902bd422d226c405eda8b028b2'),
    'research/challenge-8/overnight-assume-actual/capture.py':
        ('ffc3653263e86c5afa4f82440f10a2207e75ad8083bdad5f784597fe0dbaa84f',
         'eddf624a7ecc59b9fac4595fc95629e5ab22e26efd12be2ba53e44fbbc40ff66'),
    'research/challenge-8/overnight-guard-actual/prepare-actual-nested-drop.py':
        ('eb73621ac35f7d3b0259b148f59a5411c4ae07216c352d5a103fc59ea76f9faa',
         'ca8de412b0fd61f7e403a1d774320f783ae547b8dbe4eff107ae2a2ad9e3219c'),
    'research/challenge-8/overnight-helper/prepare-actual-owner-linked.py':
        ('1c8e52efa2882d39369645f3b1def48ae67532bb11df31a11ec23d0625887169',
         '2109b951d9421a3d5a22de0897274230983d5b64db9f0a206848c006d267a3f6'),
    'research/challenge-8/overnight-helper/prepare-actual-owner-projection.py':
        ('6680e74fda839501db3c9221f026a3398ce5d903a8134733b6f5375c165afbb8',
         'c5bd11c6c3d56f987ef8c8e037ca87a0818e0f5290de4aeb5ded026e1f36ac07'),
}
NATIVE_CAPTURE_REL = Path('research/challenge-8/overnight-sort4/capture.py')
NATIVE_CAPTURE_SHA256 = '0d993e8c36cb7684eb509e8efcfb9553b07e92e87885f4ae430269c4cb2a6060'

R24_PHASE = 'SORT4-ACTUAL-SELECT-2026-10-24-R24'
R21_PHASE = 'SORT4-ACTUAL-SELECT-2026-10-23-R21'
R24_PHASE_ENV = 'SORT4_R24_SESSION_PHASE_ID'
R21_PHASE_ENV = 'SORT4_R20_CALLEE_PHASE_ID'
LANE = 'o26-select-callee-r20'
PROFILE = 'experimental-s6-26.10-v1'
VARIANTS = (
    'positive', 'omit-selected-own', 'omit-unselected-own', 'no-retained-half',
    'callee-false-normal', 'callee-owner-duplicate', 'callee-owner-loss',
    'callee-thread-duplicate',
)
TOOL_HASHES_8A = {
    'bin/refinement-checker': 'b049c8d1b0bb350f77664e1c75c5a95966c5839984abc25c7cb629c0cba04d28',
    'bin/rust/std/lib.rsspec': 'd33b2a7a284557002b4f7afe3d5e63f813e51f818c588712d743b4b46f9bedaf',
    'bin/verifast': '01eaa29335277643e2c16dd35b561e2aecee867fbdd64cf13b8eb1d082602cd6',
    'bin/vf-rust-mir-exporter': 'b00c75f43ab4d89bf85f5e62a5114a238b89b720d4598d90423347b9d97ac796',
    'src/frontend/ocaml_expr_of_ast.ml': 'f32f1a9abd3f31c211b3ac633eca130e3298ab6e8fe39e5b489c69401efc1f94',
    'src/rust_frontend/vf_mir/vf_mir.capnp': 'f48fcf29b99717c2e0cb37d4708b47eccaa3270b999e4a84093e37fbd51b7469',
    'src/rust_frontend/vf_mir_translator/rust_parser.ml': '6a866aa5d469a1677ae1ac1bcdd675e4c059dcde449872b9cd1700d4b2e51246',
    'src/rust_frontend/vf_mir_translator/vf_mir_translator.ml': '8a0260169bd2345070755e268edb640eaa4f02c261bef3330d7b33698e4ce007',
}
NATIVE_TOOL_HASHES = {
    'bin/refinement-checker': 'b049c8d1b0bb350f77664e1c75c5a95966c5839984abc25c7cb629c0cba04d28',
    'bin/rust/std/lib.rsspec': 'd33b2a7a284557002b4f7afe3d5e63f813e51f818c588712d743b4b46f9bedaf',
    'bin/rust/rust_belt/general.rsspec': 'ef2ff16dffd472bbc5fd7fa17e7f13a03d83919520da5ce7e2d7095194790d1d',
    'bin/verifast': '33b693fa92790864db503fa69657e572fd2699350e6c7e1b4b2ffc3998108fe0',
    'bin/vf-rust-mir-exporter': 'b00c75f43ab4d89bf85f5e62a5114a238b89b720d4598d90423347b9d97ac796',
    'src/frontend/ocaml_expr_of_ast.ml': 'f32f1a9abd3f31c211b3ac633eca130e3298ab6e8fe39e5b489c69401efc1f94',
    'src/rust_frontend/vf_mir/vf_mir.capnp': 'f48fcf29b99717c2e0cb37d4708b47eccaa3270b999e4a84093e37fbd51b7469',
    'src/rust_frontend/vf_mir_translator/rust_parser.ml': '6a866aa5d469a1677ae1ac1bcdd675e4c059dcde449872b9cd1700d4b2e51246',
    'src/rust_frontend/vf_mir_translator/vf_mir_translator.ml': '5170c56386f092d55a42251594eb4b080073f58828cbe1dcf44053b5bdc99942',
}
TARGET_SPEC_SHA256 = NATIVE_TOOL_HASHES['bin/rust/std/lib.rsspec']
NATIVE_ORIGINAL_SHA256 = 'b4b0070e224cc60eba58a2116c0009fdda2e3ae599c67344194a709215a374db'
NATIVE_VERIFIED_SHA256 = 'e3fb9d257609d07b8a54afd135d219e6f531fa274364b9671f87e07e93d0d663'
SOURCE_SHA256 = '85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1'
CONST_ORIGINAL_SHA256 = '466882d74de217766ed8d5c583596c173df47f0e6bd40da7cb1a4c931d7265a5'
CONST_BASE_VERIFIED_SHA256 = '1798132ff7a1585db7367779365c88e5ef5f417adcff0bf82779bf6a674945e6'
CONST_MATRIX_REPORT_REL = Path('cases/r21-fractional-proof/r21-fractional-proof.json')
CONST_MATRIX_AUDIT_REL = Path('const-regression-audit.json')


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def need(ok: bool, why: str) -> None:
    if not ok:
        raise RuntimeError('R24-W4-CONST-QUALIFICATION: ' + why)


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name('.' + path.name + '.tmp')
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    os.replace(tmp, path)


def _load(path: Path, name: str, expected_sha: str):
    need(expected_sha != 'PENDING' and path.is_file() and not path.is_symlink() and
         sha(path.read_bytes()) == expected_sha, 'pinned module missing or changed: ' + str(path))
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, 'cannot load pinned module: ' + str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    need(sha(path.read_bytes()) == expected_sha, 'module changed during import: ' + str(path))
    return module


def _load_json(repo: Path, rel: Path, expected_sha: str) -> dict[str, Any]:
    path = repo / rel
    need(expected_sha != 'PENDING' and path.is_file() and not path.is_symlink() and
         sha(path.read_bytes()) == expected_sha, 'pinned JSON missing or changed: ' + rel.as_posix())
    value = json.loads(path.read_text(encoding='utf-8'))
    need(type(value) is dict, 'pinned JSON has wrong type: ' + rel.as_posix())
    return value


def _canonical_json(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n').encode()


def _target_spec_identity(home: Path) -> tuple[Path, bytes]:
    """Read the exact contained lib.rsspec used to name spec diagnostics."""
    root = home.resolve()
    path = root / 'bin/rust/std/lib.rsspec'
    need(path.resolve() == path and path.is_relative_to(root) and
         not path.is_symlink() and path.is_file(),
         'target-intent lib.rsspec path is missing, symlinked, or outside tool home')
    raw = path.read_bytes()
    need(sha(raw) == TARGET_SPEC_SHA256,
         'target-intent lib.rsspec bytes differ from the pinned spec')
    return path, raw


def _target_intent_material(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any], bytes, bytes]:
    """Derive only the two absolute spec paths; leave historical input untouched."""
    source_path = args.repo / TARGET_MAP_REL
    need(not source_path.is_symlink() and source_path.is_file(),
         'historical control target map is missing or unsafe')
    original_raw = source_path.read_bytes()
    need(sha(original_raw) == TARGET_MAP_SHA256,
         'historical control target map raw SHA-256 differs')
    try:
        original = json.loads(original_raw.decode('utf-8'))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise RuntimeError('historical control target map is invalid JSON') from exc
    need(type(original) is dict and set(original) == {'schema', 'targets'} and
         original.get('schema') == 'select-r22-control-target-map-v1' and
         type(original.get('targets')) is dict,
         'historical control target map schema or shape differs')
    target_map = json.loads(json.dumps(original))
    targets = target_map['targets']
    need(set(targets) == {'callee-false-normal', 'callee-owner-duplicate',
         'callee-owner-loss', 'callee-thread-duplicate', 'no-retained-half',
         'omit-selected-own', 'omit-unselected-own'},
         'historical control target map row inventory differs')
    need(all(type(row) is dict for row in targets.values()),
         'historical control target map contains a missing/null/wrong-type row')
    old_path, old_raw = _target_spec_identity(args.tool_home)
    new_path, new_raw = _target_spec_identity(args.native_tool_home)
    need(old_raw == new_raw, 'old and native lib.rsspec bytes differ')
    old_identity, new_identity = str(old_path), str(new_path)
    rewrites = []
    for variant, line in (('omit-selected-own', 462), ('omit-unselected-own', 463)):
        row = targets.get(variant)
        need(type(row) is dict and row.get('file') == old_identity and
             row.get('line') == line and
             row.get('tool_spec_sha256') == sha(old_raw),
             'historical spec target path or identity differs: ' + variant)
        row['file'] = new_identity
        rewrites.append({'variant': variant, 'line': line,
                         'from': old_identity, 'to': new_identity})
    expected = json.loads(json.dumps(original))
    for item in rewrites:
        expected['targets'][item['variant']]['file'] = item['to']
    need(target_map == expected, 'derived target intent changed an unapproved field')
    derived_raw = _canonical_json(target_map)
    canonical_map_sha = sha(json.dumps(target_map, sort_keys=True,
                                       separators=(',', ':')).encode())
    receipt = {
        'schema': TARGET_INTENT_SCHEMA,
        'semantics': 'DERIVED_TARGET_INTENT_NOT_NEW_OBSERVATION',
        'historical_map_path': TARGET_MAP_REL.as_posix(),
        'historical_map_raw_sha256': sha(original_raw),
        'historical_map_bytes': len(original_raw),
        'derived_map_path': TARGET_INTENT_REL.as_posix(),
        'derived_map_raw_sha256': sha(derived_raw),
        'derived_map_canonical_sha256': canonical_map_sha,
        'derived_map_bytes': len(derived_raw),
        'frozen_tool_home': str(args.tool_home.resolve()),
        'native_tool_home': str(args.native_tool_home.resolve()),
        'old_spec_path': old_identity, 'new_spec_path': new_identity,
        'old_spec_sha256': sha(old_raw), 'new_spec_sha256': sha(new_raw),
        'rewrites': rewrites,
        'all_other_fields_preserved': True,
        'historical_observed_fields_reused_as_prior_input': True,
        'new_path_observed': False,
        'current_acceptance': False, 'publication_allowed': False,
        'proof_credit': 0,
    }
    return target_map, receipt, derived_raw, _canonical_json(receipt)


def _target_intent_matrix_errors(matrix: object, receipt: object) -> list[str]:
    if type(matrix) is not dict or type(receipt) is not dict:
        return ['matrix/target-intent binding record missing or wrong type']
    dependencies = matrix.get('entry_dependencies')
    if type(dependencies) is not dict:
        return ['matrix entry dependency binding missing or wrong type']
    errors = []
    if dependencies.get('target_map_sha256') != receipt.get('derived_map_raw_sha256'):
        errors.append('R21 entry consumed a different target-intent raw map')
    if dependencies.get('target_map_canonical_sha256') != receipt.get('derived_map_canonical_sha256'):
        errors.append('R21 entry canonical target-intent digest differs')
    if matrix.get('diagnostic_target_map_sha256') != receipt.get('derived_map_canonical_sha256'):
        errors.append('R21 matrix diagnostic target-map digest differs')
    if dependencies.get('tool_spec_sha256') != receipt.get('new_spec_sha256'):
        errors.append('R21 entry target-intent tool-spec digest differs')
    return errors


def _write_target_intent(args: argparse.Namespace, work: Path) -> dict[str, Any]:
    _, receipt, derived_raw, receipt_raw = _target_intent_material(args)
    map_path, receipt_path = work / TARGET_INTENT_REL, work / TARGET_INTENT_RECEIPT_REL
    work_abs = Path(os.path.abspath(work))
    need(work.resolve() == work_abs and
         map_path.resolve() == work_abs / TARGET_INTENT_REL and
         receipt_path.resolve() == work_abs / TARGET_INTENT_RECEIPT_REL,
         'target-intent output path escapes or aliases the work subtree')
    for path in (map_path, receipt_path):
        need(not path.exists() and not path.is_symlink(),
             'derived target-intent output already exists: ' + str(path))
        path.parent.mkdir(parents=True, exist_ok=True)
    map_path.write_bytes(derived_raw)
    receipt_path.write_bytes(receipt_raw)
    need(map_path.is_file() and not map_path.is_symlink() and
         receipt_path.is_file() and not receipt_path.is_symlink() and
         map_path.read_bytes() == derived_raw and receipt_path.read_bytes() == receipt_raw,
         'derived target-intent files failed physical write verification')
    return receipt


def _validate_target_intent(args: argparse.Namespace, work: Path,
                            saved_receipt: object) -> list[str]:
    try:
        _, receipt, derived_raw, receipt_raw = _target_intent_material(args)
    except BaseException as exc:
        return ['target-intent recomputation failed: ' + type(exc).__name__ + ': ' + str(exc)]
    errors = []
    work_abs = Path(os.path.abspath(work))
    if work.resolve() != work_abs:
        errors.append('target-intent work root is symlinked or aliased')
    if saved_receipt != receipt:
        errors.append('target-intent receipt differs from recomputed derivation')
    for path, expected in ((work / TARGET_INTENT_REL, derived_raw),
                           (work / TARGET_INTENT_RECEIPT_REL, receipt_raw)):
        expected_path = work_abs / path.relative_to(work)
        if path.resolve() != expected_path or not path.resolve().is_relative_to(work_abs):
            errors.append('target-intent artifact escapes or aliases work: ' + str(path))
            continue
        if path.is_symlink() or not path.is_file():
            errors.append('target-intent artifact missing/unsafe: ' + str(path))
        else:
            try:
                if path.read_bytes() != expected:
                    errors.append('target-intent artifact changed: ' + str(path))
            except OSError:
                errors.append('target-intent artifact unreadable: ' + str(path))
    return errors


def expected_mode() -> dict[str, Any]:
    """Return the canonical mode body; the raw mode hash is pinned by the caller."""
    return {
        'schema': 'select-r24-w4-const-qualification-mode-v1',
        'enabled': True, 'owner': 'select-sort4', 'phase_id': R24_PHASE,
        'route_phase_id': R21_PHASE, 'lane': LANE, 'profile': PROFILE,
        'capture_mode_path': CAPTURE_MODE_REL.as_posix(),
        'capture_mode_sha256': CAPTURE_MODE_SHA256,
        'capture_pins_path': CAPTURE_PINS_REL.as_posix(),
        'capture_pins_sha256': CAPTURE_PINS_SHA256,
        'native_fingerprint_pins_path': NATIVE_FINGERPRINT_PINS_REL.as_posix(),
        'native_fingerprint_pins_sha256': NATIVE_FINGERPRINT_PINS_SHA256,
        'w4_inputs_path': W4_INPUTS_REL.as_posix(),
        'w4_inputs_sha256': W4_INPUTS_SHA256,
        'native_tool_hashes': NATIVE_TOOL_HASHES,
        'native_original_source_sha256': NATIVE_ORIGINAL_SHA256,
        'native_verified_source_sha256': NATIVE_VERIFIED_SHA256,
        'frozen_const_qualification_path': CONST_QUALIFICATION_REL.as_posix(),
        'frozen_const_qualification_sha256': CONST_QUALIFICATION_SHA256,
        'published_p2_interface_path': P2_INTERFACE_REL.as_posix(),
        'published_p2_interface_sha256': P2_INTERFACE_SHA256,
        'fractional_pins_path': FRACTIONAL_PINS_REL.as_posix(),
        'fractional_pins_sha256': FRACTIONAL_PINS_SHA256,
        'target_map_path': TARGET_MAP_REL.as_posix(),
        'target_map_sha256': TARGET_MAP_SHA256,
        'r21_entry_path': R21_ENTRY_REL.as_posix(),
        'r21_entry_sha256': R21_ENTRY_SHA256,
        'r21_audit_path': R21_AUDIT_REL.as_posix(),
        'r21_audit_sha256': R21_AUDIT_SHA256,
        'o26_recipe_path': O26_RECIPE_REL.as_posix(),
        'o26_recipe_sha256': O26_RECIPE_SHA256,
        'capture_path': CAPTURE_REL.as_posix(), 'capture_sha256': CAPTURE_SHA256,
        'prepare_path': PREPARE_REL.as_posix(), 'prepare_sha256': PREPARE_SHA256,
        'cloud_capture_overlay_sha256': CAPTURE_CLOUD_OVERLAY_SHA256,
        'cloud_prepare_overlay_sha256': PREPARE_CLOUD_OVERLAY_SHA256,
        'provider_path': O26_PROVIDER_REL.as_posix(),
        'provider_sha256': O26_PROVIDER_SHA256,
        'o26_base_path': O26_BASE_REL.as_posix(), 'o26_base_sha256': O26_BASE_SHA256,
        'o26_cloud_guard_overlay_files': {
            path: {'original_sha256': before, 'cloud_overlay_sha256': after}
            for path, (before, after) in O26_OVERLAY_FILES.items()},
        'native_capture_path': NATIVE_CAPTURE_REL.as_posix(),
        'native_capture_sha256': NATIVE_CAPTURE_SHA256,
        'consequence_path': CONSEQUENCE_REL.as_posix(),
        'consequence_sha256': CONSEQUENCE_SHA256,
        'consequence_mode': 'ordinary-checked-callee-post-consequence',
        'postqualification_diagnostic_path': CONTRACT_REL.as_posix(),
        'postqualification_diagnostic_sha256': CONTRACT_SHA256,
        'postqualification_diagnostic_mode_path': CONTRACT_MODE_REL.as_posix(),
        'postqualification_diagnostic_mode_sha256': CONTRACT_MODE_SHA256,
        'postqualification_diagnostic_only': True,
        'variants': list(VARIANTS),
        'ordinary_callee_proof_stages_enabled': True,
        'caller_body_proof_admission': False,
        'accepted': False, 'publication_allowed': False,
        'independent_proof_credit': 0,
    }


def _mode(args: argparse.Namespace) -> dict[str, Any]:
    path = args.mode_file
    need(path.resolve() == (args.repo / MODE_REL).resolve() and path.is_file() and
         not path.is_symlink() and MODE_SHA256 != 'PENDING' and
         sha(path.read_bytes()) == MODE_SHA256, 'qualification mode path/hash differs')
    mode = json.loads(path.read_text(encoding='utf-8'))
    need(type(mode) is dict and mode == expected_mode(), 'qualification mode contract differs')
    return mode


def _tool_identity(home: Path, expected: dict[str, str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for rel, digest in expected.items():
        path = home / rel
        need(path.is_file() and not path.is_symlink(), 'tool file missing/symlinked: ' + rel)
        actual = sha(path.read_bytes())
        need(actual == digest, 'tool identity differs: ' + rel)
        result[rel] = actual
    return result


def _context(args: argparse.Namespace, env: dict[str, str], *, require_live_deadline: bool = True) -> None:
    for name in ('repo', 'cloud_dir', 'evidence', 'tool_home', 'native_tool_home',
                 'schema', 'compiler_sysroot', 'capture_mode_file', 'mode_file'):
        path = getattr(args, name)
        if name not in ('compiler_sysroot',):
            setattr(args, name, Path(path).resolve())
        else:
            need(isinstance(path, (str, Path)) and str(path), 'compiler sysroot missing')
            setattr(args, name, Path(path).resolve())
    deadline_ok = (type(args.deadline_epoch) is int and args.deadline_epoch > int(time.time())
                   if require_live_deadline else
                   type(args.deadline_epoch) is int and args.deadline_epoch > 0)
    need(args.native_tool_home != args.tool_home and deadline_ok,
         'native home must be separate and deadline must be valid')
    need(args.compiler_sysroot.is_dir(), 'compiler sysroot path is missing or not a directory')
    need(re.fullmatch(r'[0-9a-f]{40}', args.candidate or '') is not None,
         'candidate must be a full commit SHA')
    need(env.get('SMALLSORT_EXECUTION_PROVIDER') == 'cloud-build' and
         env.get(R24_PHASE_ENV) == R24_PHASE and env.get(R21_PHASE_ENV) == R21_PHASE and
         env.get('SORT4_SELECT_PROFILE') == PROFILE and env.get('LANE') == LANE and
         not env.get('GITHUB_ACTIONS') and
         bool(env.get('CLOUD_BUILD_ID')),
         'exact R24/R21 Cloud route required')
    need(not any(key.startswith('SORT4_') and key not in
                 {R24_PHASE_ENV, R21_PHASE_ENV, 'SORT4_SELECT_PROFILE'} for key in env),
         'ambient SORT4 opt-ins are forbidden')


def _validate_pins(args: argparse.Namespace) -> dict[str, Any]:
    _load_json(args.repo, CONTRACT_MODE_REL, CONTRACT_MODE_SHA256)
    contract_driver = args.cloud_dir / CONTRACT_REL.name
    need(CONTRACT_SHA256 != 'PENDING' and contract_driver.is_file() and
         not contract_driver.is_symlink() and
         sha(contract_driver.read_bytes()) == CONTRACT_SHA256,
         'postqualification diagnostic helper differs')
    capture_mode = args.capture_mode_file
    need(capture_mode.resolve() == (args.repo / CAPTURE_MODE_REL).resolve() and
         capture_mode.is_file() and not capture_mode.is_symlink() and
         sha(capture_mode.read_bytes()) == CAPTURE_MODE_SHA256,
         'frozen W4 capture mode differs')
    capture_pins = _load_json(args.repo, CAPTURE_PINS_REL, CAPTURE_PINS_SHA256)
    native_pins = _load_json(args.repo, NATIVE_FINGERPRINT_PINS_REL,
                             NATIVE_FINGERPRINT_PINS_SHA256)
    inputs = _load_json(args.repo, W4_INPUTS_REL, W4_INPUTS_SHA256)
    old_const = _load_json(args.repo, CONST_QUALIFICATION_REL, CONST_QUALIFICATION_SHA256)
    _load_json(args.repo, FRACTIONAL_PINS_REL, FRACTIONAL_PINS_SHA256)
    _load_json(args.repo, TARGET_MAP_REL, TARGET_MAP_SHA256)
    p2_interface = _load_json(args.repo, P2_INTERFACE_REL, P2_INTERFACE_SHA256)
    overlay = _validate_cloud_overlay(args)
    need(capture_pins.get('schema') == 'select-r24-w4-capture-pins-v1' and
         capture_pins.get('source', {}).get('original_sha256') == NATIVE_ORIGINAL_SHA256 and
         capture_pins.get('source', {}).get('verified_sha256') == NATIVE_VERIFIED_SHA256,
         'frozen W4 source inputs differ')
    need(native_pins.get('native_tool_source_hashes') ==
         {k: v for k, v in NATIVE_TOOL_HASHES.items() if k != 'bin/verifast' and
          k != 'bin/rust/rust_belt/general.rsspec'} and
         native_pins.get('native_verifier_binary', {}).get('sha256') ==
         NATIVE_TOOL_HASHES['bin/verifast'] and
         native_pins.get('original_source_sha256') == NATIVE_ORIGINAL_SHA256 and
         native_pins.get('verified_source_sha256') == NATIVE_VERIFIED_SHA256,
         'native W4 fingerprint identities differ')
    need(inputs.get('candidate') == 'f12824a149a175acdf0b7e6b2620e28acca67ca2' and
         inputs.get('native_body_inventory') == ['sort4_stable'] and
         inputs.get('typed_call_linkage') == 'UNKNOWN' and
         inputs.get('actual_body_proof_status') == 'UNKNOWN' and
         inputs.get('native_body', {}).get('sha256') ==
         native_pins.get('native_body', {}).get('sha256') and
         inputs.get('native_unit', {}).get('sha256') ==
         native_pins.get('native_unit', {}).get('sha256'),
         'W4 source-reported input record does not bind the native source snapshots')
    need(old_const.get('schema') == 'select-r24-const-callee-qualification-v1' and
         old_const.get('status') == 'QUALIFIED_UNDER_EXACT_EXPERIMENTAL_PROFILE' and
         old_const.get('tool_hashes') == TOOL_HASHES_8A and
         old_const.get('accepted') is True and old_const.get('proof_credit') == 0,
         'frozen 8a const qualification input differs')
    input_native_hashes = {k: v for k, v in NATIVE_TOOL_HASHES.items()
                           if k not in ('bin/verifast', 'bin/rust/rust_belt/general.rsspec')}
    input_native_hashes['bin/verifast'] = NATIVE_TOOL_HASHES['bin/verifast']
    need(inputs.get('schema') == 'select-r24-w4-inputs-qualification-v1' and
         inputs.get('status') == 'SOURCE_REPORTED_INPUTS_READY_FOR_CHECKED_CALLEE_DEPENDENCY' and
         inputs.get('typed_call_linkage') == 'UNKNOWN' and
         inputs.get('accepted') is False and inputs.get('proof_credit') == 0 and
         inputs.get('native_tool_hashes') == input_native_hashes and
         p2_interface.get('status') == 'PUBLISHED' and
         p2_interface.get('proof_credit') == 0,
         'qualified W4 input or published P2 dependency differs')
    return {'capture_pins': capture_pins, 'native_pins': native_pins,
            'w4_inputs': inputs, 'p2_interface': p2_interface,
            'cloud_overlay': overlay}


def _validate_cloud_overlay(args: argparse.Namespace) -> dict[str, Any]:
    """Require the pre-existing, pinned provider-only Cloud guard overlay."""
    provider = args.repo / O26_PROVIDER_REL
    recipe = args.cloud_dir / O26_BASE_REL.name
    refresh = args.cloud_dir / O26_RECIPE_REL.name
    need(provider.is_file() and not provider.is_symlink() and
         sha(provider.read_bytes()) == O26_PROVIDER_SHA256,
         'pinned Cloud provider module differs')
    need(recipe.is_file() and not recipe.is_symlink() and
         sha(recipe.read_bytes()) == O26_BASE_SHA256,
         'pinned O26 base recipe differs')
    need(refresh.is_file() and not refresh.is_symlink() and
         sha(refresh.read_bytes()) == O26_RECIPE_SHA256,
         'pinned O26 refresh wrapper differs')
    overlay_path = args.evidence / 'candidate-provider-overlay.json'
    need(overlay_path.is_file() and not overlay_path.is_symlink(),
         'existing O26 provider overlay receipt is missing')
    overlay = json.loads(overlay_path.read_text(encoding='utf-8'))
    need(type(overlay) is dict and overlay.get('proof_sha') == args.candidate and
         overlay.get('provider_sha256') == O26_PROVIDER_SHA256,
         'O26 provider overlay receipt context differs')
    rows = overlay.get('files')
    need(type(rows) is list and len(rows) == 5,
         'O26 provider overlay file inventory differs')
    by_path = {row.get('path'): row for row in rows if type(row) is dict}
    if set(by_path) != set(O26_OVERLAY_FILES):
        need(False, 'O26 provider overlay path inventory differs')
    for rel, (source_sha, cloud_sha) in O26_OVERLAY_FILES.items():
        row = by_path.get(rel)
        path = args.repo / rel
        need(type(row) is dict and row.get('original_sha256') == source_sha and
             row.get('cloud_overlay_sha256') == cloud_sha and row.get('guard_only') is True and
             path.is_file() and not path.is_symlink() and sha(path.read_bytes()) == cloud_sha,
             'Cloud provider guard overlay differs: ' + rel)
    return {'path': str(overlay_path), 'sha256': sha(overlay_path.read_bytes()),
            'proof_sha': overlay['proof_sha'], 'files': rows}


def _run_command(name: str, argv: list[str], *, cwd: Path,
                 env: dict[str, str], deadline: int) -> dict[str, Any]:
    remaining = deadline - int(time.time())
    if remaining <= 0:
        return {'status': 'TIMEOUT', 'exit': 124, 'stdout': '', 'stderr': 'deadline elapsed'}
    try:
        result = subprocess.run(argv, cwd=cwd, env=env, text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                timeout=remaining, check=False)
        return {'status': 'RAN', 'exit': result.returncode,
                'stdout': result.stdout, 'stderr': result.stderr}
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout.decode(errors='replace') if isinstance(exc.stdout, bytes) else (exc.stdout or '')
        stderr = exc.stderr.decode(errors='replace') if isinstance(exc.stderr, bytes) else (exc.stderr or '')
        return {'status': 'TIMEOUT', 'exit': 124, 'stdout': stdout, 'stderr': stderr}


def _stage_record(name: str, argv: list[str], result: object) -> dict[str, Any]:
    if type(result) is not dict:
        return {'name': name, 'status': 'WRONG_TYPE', 'argv': argv,
                'exit': None, 'stdout': '', 'stderr': '', 'errors': ['runner result is not an object']}
    status = result.get('status')
    exit_code = result.get('exit')
    out = result.get('stdout', '')
    err = result.get('stderr', '')
    errors = []
    if status != 'RAN': errors.append('stage did not report RAN')
    if type(exit_code) is not int: errors.append('stage exit is missing or wrong type')
    if type(out) is not str or type(err) is not str: errors.append('stage output is missing or wrong type')
    return {'name': name, 'status': status if isinstance(status, str) else 'UNKNOWN',
            'argv': argv, 'exit': exit_code if type(exit_code) is int else None,
            'stdout': out if isinstance(out, str) else '',
            'stderr': err if isinstance(err, str) else '', 'errors': errors}


def _read_object(path: Path) -> dict[str, Any] | None:
    try:
        if path.is_symlink() or not path.is_file(): return None
        value = json.loads(path.read_text(encoding='utf-8'))
        return value if type(value) is dict else None
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None


def _stage_commands(args: argparse.Namespace, work: Path) -> list[tuple[str, list[str]]]:
    py = sys.executable
    recipe = args.cloud_dir / O26_RECIPE_REL.name
    capture = args.repo / CAPTURE_REL
    fractional = args.cloud_dir / R21_ENTRY_REL.name
    audit = args.cloud_dir / R21_AUDIT_REL.name
    case_capture = work / 'cases/candidate/capture'
    target_intent = work / TARGET_INTENT_REL
    return [
        ('source-preflight', [py, str(recipe), 'preflight', '--repo', str(args.repo),
                              '--cloud-dir', str(args.cloud_dir), '--evidence', str(work)]),
        ('candidate-capture', [py, str(capture), '--tool-home', str(args.native_tool_home),
                               '--schema', str(args.schema), '--compiler-sysroot', str(args.compiler_sysroot),
                               '--evidence', str(case_capture), '--deadline-epoch', str(args.deadline_epoch),
                               '--fingerprint']),
        ('candidate-source-compare', [py, str(recipe), 'compare', '--evidence', str(work)]),
        ('candidate-proof', [py, str(recipe), 'proof', '--repo', str(args.repo),
                             '--cloud-dir', str(args.cloud_dir), '--evidence', str(work),
                             '--tool-home', str(args.native_tool_home), '--schema', str(args.schema),
                             '--compiler-sysroot', str(args.compiler_sysroot),
                             '--deadline-epoch', str(args.deadline_epoch)]),
        ('r21-fractional-proof', [py, str(fractional), '--repo', str(args.repo),
                                 '--cloud-dir', str(args.cloud_dir), '--evidence', str(work),
                                 '--tool-home', str(args.native_tool_home), '--schema', str(args.schema),
                                 '--compiler-sysroot', str(args.compiler_sysroot),
                                 '--deadline-epoch', str(args.deadline_epoch),
                                 '--pins-json', str(args.repo / FRACTIONAL_PINS_REL),
                                 '--positive-ast-inventory', '--checked-pointer-outcomes',
                                 '--target-map', str(target_intent)]),
        ('const-regression-audit', [py, str(audit), '--evidence', str(work),
                                    '--output', str(work / CONST_MATRIX_AUDIT_REL),
                                    '--runner-exit', '0', '--failed-stage', 'complete']),
    ]


def _validate_stage_outputs(name: str, work: Path, stage: dict[str, Any], *,
                           native_home: Path | None = None,
                           build_id: str | None = None) -> list[str]:
    errors = list(stage.get('errors', []))
    if stage.get('status') != 'RAN' or type(stage.get('exit')) is not int:
        return errors + ['stage result absent, NOT_RUN, timeout, or wrong type']
    if stage['exit'] != 0:
        return errors + [f'{name} command exited {stage["exit"]}']
    if name == 'source-preflight':
        record = _read_object(work / 'source-preflight.json')
        source = record.get('source') if record else None
        if type(source) is not dict or record.get('source_generation_complete') is not True or \
           source.get('original_sha256') != CONST_ORIGINAL_SHA256 or \
           source.get('verified_sha256') != CONST_BASE_VERIFIED_SHA256 or \
           source.get('ghost_strip_identity') is not True:
            errors.append('fresh preflight source pair differs from const matrix input')
    elif name == 'candidate-capture':
        summary = _read_object(work / 'cases/candidate/capture/summary.json')
        if not summary or summary.get('frontend_refinement_and_full_body_capture') is not True:
            errors.append('fresh source/MIR capture is missing or incomplete')
        if not summary or summary.get('actual_helper_proved') is not False:
            errors.append('capture source report boundary differs')
    elif name == 'candidate-source-compare':
        compare = _read_object(work / 'cases/candidate/capture-compare.json')
        if not compare or compare.get('capture_complete') is not True:
            errors.append('fresh source/snapshot comparison is incomplete')
    elif name == 'candidate-proof':
        record = _read_object(work / 'cases/candidate/proof-stage.json')
        stage_data = record.get('stage') if record else None
        if type(stage_data) is not dict or type(stage_data.get('exit')) is not int or \
           stage_data.get('status') != 'RAN' or stage_data.get('source_unchanged') is not True:
            errors.append('baseline proof stage is missing, partial, or source-dirty')
        if type(stage_data) is dict:
            expected_argv = [str(native_home / 'bin/verifast') if native_home else None,
                             '-rustc_args', '--edition 2021', '-verbose', '1',
                             'verified/lib.rs']
            if stage_data.get('argv') != expected_argv:
                errors.append('baseline proof stage argv differs from native tool')
            if stage_data.get('stdout') != 'refreshed-proof.log' or \
               stage_data.get('stderr') != 'refreshed-proof.log':
                errors.append('baseline proof stage output target differs')
            source_capture = _read_object(work / 'cases/candidate/capture/summary.json')
            source = source_capture.get('source') if source_capture else None
            expected_sources = ({'original/lib.rs': source.get('original_sha256'),
                                 'verified/lib.rs': source.get('verified_sha256')}
                                if type(source) is dict else None)
            if expected_sources is None or stage_data.get('source_before') != expected_sources or \
               stage_data.get('source_after') != expected_sources:
                errors.append('baseline proof source-stage-target binding differs')
            if native_home:
                case = work / 'cases/candidate/capture/nine-body-a1-owned-forget'
                for label, field in (('stdout', 'refreshed-proof.log'),
                                     ('stderr', 'refreshed-proof.log')):
                    path = case / field
                    if path.is_symlink() or not path.is_file():
                        errors.append('baseline proof physical output missing/unsafe: ' + label)
            if stage_data.get('exit') == 124:
                errors.append('baseline proof timed out')
        if record and record.get('actual_verification_accepted') is not False:
            errors.append('baseline source report acceptance boundary differs')
    elif name == 'r21-fractional-proof':
        record = _read_object(work / CONST_MATRIX_REPORT_REL)
        if not record or record.get('complete') is not True or \
           record.get('variant_order') != list(VARIANTS):
            errors.append('fresh const eight-row matrix is missing or incomplete')
        errors.extend(_validate_matrix_rows(record, native_home=native_home,
                                            build_id=build_id))
        if record and (record.get('accepted') is not False or record.get('proof_credit') is not False):
            errors.append('matrix source report acceptance boundary differs')
    elif name == 'const-regression-audit':
        record = _read_object(work / CONST_MATRIX_AUDIT_REL)
        if not record or record.get('evidence_complete') is not True:
            errors.append('frozen const matrix audit is incomplete')
        if record and (record.get('accepted') is not False or
                       record.get('verification_accepted') is not False or
                       record.get('proof_credit') is not False):
            errors.append('frozen const audit acceptance boundary differs')
    return errors


def _stage_artifacts(name: str, work: Path) -> dict[str, Any]:
    paths = {
        'source-preflight': [work / 'source-preflight.json'],
        'candidate-capture': [work / 'cases/candidate/capture/summary.json'],
        'candidate-source-compare': [work / 'cases/candidate/capture-compare.json'],
        'candidate-proof': [work / 'cases/candidate/proof-stage.json'],
        'r21-fractional-proof': [work / CONST_MATRIX_REPORT_REL],
        'const-regression-audit': [work / CONST_MATRIX_AUDIT_REL],
    }.get(name, [])
    result = []
    for path in paths:
        if path.is_symlink() or not path.is_file():
            continue
        raw = path.read_bytes()
        result.append({'path': path.relative_to(work).as_posix(),
                       'bytes': len(raw), 'sha256': sha(raw)})
    return {'files': result}


def _copy_provider_overlay_receipt(outer_evidence: Path, work: Path,
                                  validated: object) -> dict[str, Any]:
    """Copy the already-validated outer receipt byte-for-byte into the R21 subtree."""
    need(type(validated) is dict, 'validated provider overlay record missing')
    source = outer_evidence / 'candidate-provider-overlay.json'
    destination = work / 'candidate-provider-overlay.json'
    need(source.is_file() and not source.is_symlink(),
         'authoritative provider overlay receipt missing/unsafe')
    raw_before = source.read_bytes()
    source_sha = sha(raw_before)
    need(source_sha == validated.get('sha256'),
         'authoritative provider overlay receipt changed after validation')
    need(not destination.exists() and not destination.is_symlink(),
         'R21-subtree provider overlay receipt target already exists')
    with destination.open('xb') as output:
        output.write(raw_before)
        output.flush()
        os.fsync(output.fileno())
    need(destination.is_file() and not destination.is_symlink(),
         'R21-subtree provider overlay receipt copy missing/unsafe')
    copied = destination.read_bytes()
    raw_after = source.read_bytes()
    need(raw_after == raw_before and copied == raw_before and sha(copied) == source_sha,
         'provider overlay receipt copy is not byte-identical to authoritative input')
    return {'authoritative_path': 'candidate-provider-overlay.json',
            'work_path': 'candidate-provider-overlay.json',
            'bytes': len(raw_before), 'sha256': source_sha,
            'byte_identical': True}


def _validate_provider_overlay_copy(outer_evidence: Path, work: Path,
                                    binding: object) -> list[str]:
    errors = []
    if type(binding) is not dict:
        return ['provider overlay receipt copy binding missing/wrong type']
    if binding.get('authoritative_path') != 'candidate-provider-overlay.json' or \
       binding.get('work_path') != 'candidate-provider-overlay.json' or \
       binding.get('byte_identical') is not True:
        errors.append('provider overlay receipt path or copy boundary differs')
    paths = (outer_evidence / 'candidate-provider-overlay.json',
             work / 'candidate-provider-overlay.json')
    raw = []
    for path in paths:
        if path.is_symlink() or not path.is_file():
            errors.append('provider overlay receipt missing/unsafe: ' + str(path))
            raw.append(None)
        else:
            try: raw.append(path.read_bytes())
            except OSError:
                errors.append('provider overlay receipt unreadable: ' + str(path))
                raw.append(None)
    if raw[0] is not None and raw[1] is not None:
        if raw[0] != raw[1]: errors.append('provider overlay receipt copy bytes changed')
        if sha(raw[0]) != binding.get('sha256') or len(raw[0]) != binding.get('bytes'):
            errors.append('authoritative provider overlay receipt identity changed')
    return errors


def _physical_stage_log(work: Path, stage: dict[str, Any]) -> dict[str, Any]:
    relroot = Path('stage-records')
    root = work / relroot
    root.mkdir(parents=True, exist_ok=True)
    name = stage['name']
    files = {}
    for field in ('stdout', 'stderr'):
        raw = stage.get(field, '').encode('utf-8')
        path = root / f'{name}.{field}.txt'
        need(not path.exists() and not path.is_symlink(), 'stage log target already exists: ' + name)
        path.write_bytes(raw)
        files[field] = {'path': (relroot / path.name).as_posix(),
                        'bytes': len(raw), 'sha256': sha(raw)}
    return files


def _source_observation(work: Path) -> dict[str, Any]:
    capture = _read_object(work / 'cases/candidate/capture/summary.json')
    if not capture:
        return {'complete': False, 'errors': ['capture summary missing or invalid']}
    source = capture.get('source')
    if type(source) is not dict:
        return {'complete': False, 'errors': ['capture source record missing']}
    case = work / 'cases/candidate/capture/nine-body-a1-owned-forget'
    rows = {}
    errors = []
    for label in ('original', 'verified'):
        path = case / label / 'lib.rs'
        expected = source.get(label + '_sha256')
        if path.is_symlink() or not path.is_file() or type(expected) is not str:
            errors.append(label + ' source file missing/unsafe or hash absent')
            continue
        raw = path.read_bytes()
        rows[label] = {'path': str(path.relative_to(work)), 'bytes': len(raw),
                       'sha256': sha(raw), 'expected_sha256': expected,
                       'intact': sha(raw) == expected}
        if sha(raw) != expected:
            errors.append(label + ' source changed')
    if source.get('original_sha256') != CONST_ORIGINAL_SHA256 or \
       source.get('verified_sha256') != CONST_BASE_VERIFIED_SHA256 or \
       source.get('ghost_strip_identity') is not True:
        errors.append('captured source pair differs from W4 input pins')
    return {'complete': not errors, 'source': source, 'files': rows, 'errors': errors}


def _validate_matrix_rows(record: object, *, native_home: Path | None = None,
                          build_id: str | None = None) -> list[str]:
    errors: list[str] = []
    if type(record) is not dict:
        return ['matrix summary missing or wrong type']
    if record.get('schema') != 'r21-fractional-classified-proof-v1':
        errors.append('matrix summary schema differs')
    if record.get('complete') is not True or record.get('variant_order') != list(VARIANTS) or \
       record.get('body_proof_run') is not True:
        errors.append('matrix summary is incomplete or variant order differs')
    rows = record.get('rows')
    if type(rows) is not dict or set(rows) != set(VARIANTS):
        errors.append('matrix row inventory differs')
    else:
        for variant in VARIANTS:
            row = rows.get(variant)
            if type(row) is not dict:
                errors.append('matrix row has wrong type: ' + variant)
                continue
            if row.get('variant') != variant:
                errors.append('matrix row identity differs: ' + variant)
            if row.get('status') != 'COMPLETE':
                errors.append('matrix row incomplete: ' + variant)
            if row.get('normal_unwind_nested_drop_gates') is not True:
                errors.append('full normal/unwind/nested-Drop gates missing: ' + variant)
            observation = row.get('current_stage_observation')
            if type(observation) is not dict or observation.get('status') != 'RAN' or \
               type(observation.get('exit')) is not int or \
               observation.get('source_unchanged') is not True:
                errors.append('proof stage missing/partial/source-dirty: ' + variant)
            if native_home is not None and type(observation) is dict:
                expected_argv = [str(native_home / 'bin/verifast'), '-rustc_args',
                                 '--edition 2021', '-verbose', '1', 'verified/lib.rs']
                if observation.get('argv') != expected_argv:
                    errors.append('matrix source-stage-target command differs: ' + variant)
            expected_class = ('POSITIVE_VERIFIED_SOURCE_REPORTED' if variant == 'positive' else
                              'EXPECTED_SAME_SITE_TYPED_FAILURE' if variant in
                              {'omit-selected-own', 'omit-unselected-own', 'no-retained-half'} else
                              'EXPECTED_CALLEE_CONTRACT_REJECTION')
            if row.get('classification') != expected_class:
                errors.append('matrix outcome classification differs: ' + variant)
    if record.get('accepted') is not False or record.get('proof_credit') is not False:
        errors.append('matrix summary acceptance boundary differs')
    pins = record.get('pins')
    if type(pins) is not dict or pins.get('base_original_sha256') != CONST_ORIGINAL_SHA256 or \
       pins.get('base_verified_sha256') != CONST_BASE_VERIFIED_SHA256:
        errors.append('matrix base source pair differs from frozen const source pins')
    if native_home is not None and record.get('tool_home') != str(native_home):
        errors.append('matrix tool home differs from the current native tool')
    if build_id is not None and (record.get('current_build_id') != build_id or
                                 record.get('checked_pointer_outcomes_requested') is not True):
        errors.append('matrix current Build/checked-outcome context differs')
    return errors


def _read_native_files(args: argparse.Namespace) -> dict[str, Any]:
    result = {}
    for rel, expected in NATIVE_TOOL_HASHES.items():
        path = args.native_tool_home / rel
        if path.is_symlink() or not path.is_file():
            result[rel] = {'regular': False, 'sha256': None, 'bytes': None}
            continue
        raw = path.read_bytes()
        result[rel] = {'regular': True, 'sha256': sha(raw), 'bytes': len(raw),
                       'expected_sha256': expected, 'matches': sha(raw) == expected}
    return result


def _validate_native_identities(before: object, after: object) -> list[str]:
    errors = []
    if type(before) is not dict or type(after) is not dict:
        return ['native tool identity inventory missing or wrong type']
    if set(before) != set(NATIVE_TOOL_HASHES) or set(after) != set(NATIVE_TOOL_HASHES):
        errors.append('native tool identity inventory is incomplete')
    for rel, expected in NATIVE_TOOL_HASHES.items():
        a, b = before.get(rel), after.get(rel)
        for label, row in (('before', a), ('after', b)):
            if type(row) is not dict or row.get('regular') is not True or \
               row.get('sha256') != expected or row.get('bytes', 0) <= 0:
                errors.append(f'{label} native tool identity differs: {rel}')
        if type(a) is dict and type(b) is dict and a != b:
            errors.append('native tool changed during qualification: ' + rel)
    return errors


def _save_summary(path: Path, record: dict[str, Any]) -> None:
    _write(path, record)


def _contract_module(args: argparse.Namespace, module: Any | None):
    if module is None:
        module = _load(args.cloud_dir / CONTRACT_REL.name,
                       'r24_w4_contract_inputs', CONTRACT_SHA256)
    need(getattr(module, 'SCHEMA', None) == 'select-r24-w4-contract-inputs-v1' and
         getattr(module, 'SUMMARY_REL', None) ==
         Path('cases/r24-w4-contract-inputs/W4-CONTRACT-INPUTS.json') and
         getattr(module, 'AUDIT_REL', None) ==
         Path('cases/r24-w4-contract-inputs/W4-CONTRACT-INPUTS-AUDIT.json') and
         callable(getattr(module, 'run', None)) and callable(getattr(module, 'audit', None)),
         'postqualification diagnostic API differs')
    return module


def _contract_args(args: argparse.Namespace, work: Path, module: Any,
                   runner_exit: int, failed_stage: str) -> argparse.Namespace:
    child = argparse.Namespace(**vars(args))
    child.evidence = work
    child.const_mode_file = args.mode_file
    child.mode_file = args.repo / CONTRACT_MODE_REL
    child.output = work / module.AUDIT_REL
    child.runner_exit = runner_exit
    child.failed_stage = failed_stage
    return child


def _contract_boundary_errors(record: object, *, audited: bool = False) -> list[str]:
    if type(record) is not dict or record.get('complete') is not True:
        return ['contract-input diagnostic missing, partial, or wrong type']
    errors = []
    if audited and record.get('evidence_complete') is not True:
        errors.append('contract-input diagnostic physical audit incomplete')
    if record.get('accepted') is not False or record.get('publication_allowed') is not False or \
       type(record.get('proof_credit')) is not int or record.get('proof_credit') != 0 or \
       record.get('caller_body_proof_admission') is not False or \
       record.get('typed_call_linkage') != 'UNKNOWN':
        errors.append('contract-input diagnostic exceeded its reporting boundary')
    return errors


def run(args: argparse.Namespace, *, command_runner: Callable[..., object] = _run_command,
        consequence_module: Any | None = None,
        contract_module: Any | None = None,
        env: dict[str, str] | None = None) -> dict[str, Any]:
    live_env = dict(os.environ)
    selected_env = live_env if env is None else dict(env)
    need(selected_env == live_env, 'Cloud route environment must be the live process environment')
    _context(args, selected_env)
    mode = _mode(args)
    pins = _validate_pins(args)
    need(args.schema.resolve() == (args.native_tool_home / 'src/rust_frontend/vf_mir/vf_mir.capnp').resolve(),
         'schema must come from the native qualification tool home')
    tool_before = _tool_identity(args.tool_home, TOOL_HASHES_8A)
    native_before = _read_native_files(args)
    need(not any(row.get('matches') is not True for row in native_before.values()),
         'native tool identity is incomplete before qualification')
    outer_evidence = args.evidence
    work = outer_evidence / WORK_REL
    need(not work.exists() and not work.is_symlink(), 'qualification evidence subtree already exists')
    work.mkdir(parents=True, exist_ok=False)
    record_path = outer_evidence / SUMMARY_REL
    record: dict[str, Any] = {
        'schema': SCHEMA, 'complete': False,
        'classification': 'INCOMPLETE_CONST_REQUALIFICATION',
        'assurance': 'SOURCE_REPORTED', 'candidate': args.candidate,
        'mode_path': MODE_REL.as_posix(), 'mode_sha256': MODE_SHA256,
        'build_id': selected_env.get('CLOUD_BUILD_ID'),
        'phase_id': R24_PHASE, 'route_phase_id': R21_PHASE,
        'lane': LANE, 'profile': PROFILE,
        'evidence_root': str(outer_evidence), 'work_evidence_root': str(work),
        'native_tool_home': str(args.native_tool_home),
        'native_schema': str(args.schema), 'native_tool_hashes_before': native_before,
        'native_tool_hashes_after': None, 'native_tool_hashes_after_each_stage': [],
        'frozen_capture_tool_home': str(args.tool_home),
        'frozen_capture_tool_hashes': tool_before,
        'input_pins': {'capture_pins': CAPTURE_PINS_SHA256,
                       'native_fingerprint_pins': NATIVE_FINGERPRINT_PINS_SHA256,
                       'frozen_const_qualification': CONST_QUALIFICATION_SHA256,
                       'published_p2_interface': P2_INTERFACE_SHA256},
        'provider_overlay_receipt_binding': None,
        'target_intent_receipt': None,
        'target_intent_map_path': (work / TARGET_INTENT_REL).relative_to(outer_evidence).as_posix(),
        'target_intent_receipt_path': (work / TARGET_INTENT_RECEIPT_REL).relative_to(outer_evidence).as_posix(),
        'stages': [], 'source_observation': None,
        'matrix_summary_path': (work / CONST_MATRIX_REPORT_REL).relative_to(outer_evidence).as_posix(),
        'matrix_audit_path': (work / CONST_MATRIX_AUDIT_REL).relative_to(outer_evidence).as_posix(),
        'consequence_summary_path': None, 'postqualification_diagnostic': None,
        'postqualification_diagnostic_audit': None, 'errors': [],
        'accepted': False, 'publication_allowed': False, 'proof_credit': 0,
        'caller_body_proof_admission': False,
        'w4_caller_body_proof_status': 'UNKNOWN',
    }
    _save_summary(record_path, record)
    try:
        record['provider_overlay_receipt_binding'] = _copy_provider_overlay_receipt(
            outer_evidence, work, pins.get('cloud_overlay'))
        record['target_intent_receipt'] = _write_target_intent(args, work)
        _save_summary(record_path, record)
        for name, argv in _stage_commands(args, work):
            result = command_runner(name, argv, cwd=args.repo, env=selected_env,
                                    deadline=args.deadline_epoch)
            stage = _stage_record(name, argv, result)
            stage['physical_logs'] = _physical_stage_log(work, stage)
            stage.pop('stdout', None)
            stage.pop('stderr', None)
            stage['errors'].extend(_validate_stage_outputs(
                name, work, stage, native_home=args.native_tool_home,
                build_id=selected_env.get('CLOUD_BUILD_ID')))
            stage['artifact_reports'] = _stage_artifacts(name, work)
            record['stages'].append(stage)
            native_stage_hashes = _read_native_files(args)
            record['native_tool_hashes_after_each_stage'].append(
                {'stage': name, 'hashes': native_stage_hashes})
            stage['errors'].extend(_validate_native_identities(native_before, native_stage_hashes))
            if name == 'candidate-capture' or record['source_observation'] is not None:
                record['source_observation'] = _source_observation(work)
                if not record['source_observation'].get('complete'):
                    stage['errors'].extend(record['source_observation'].get('errors', []))
            if stage['errors']:
                record['errors'].extend(f'{name}: {e}' for e in stage['errors'])
            _save_summary(record_path, record)
            if stage['errors']:
                break
        if not record['errors'] and len(record['stages']) == 6:
            matrix = _read_object(work / CONST_MATRIX_REPORT_REL)
            matrix_audit = _read_object(work / CONST_MATRIX_AUDIT_REL)
            need(type(matrix) is dict and type(matrix_audit) is dict,
                 'matrix artifacts unavailable after frozen audit')
            record['errors'].extend(_target_intent_matrix_errors(
                matrix, record.get('target_intent_receipt')))
            _save_summary(record_path, record)
            need(not record['errors'], 'R21 matrix target-intent binding differs')
            if consequence_module is None:
                consequence_path = args.cloud_dir / CONSEQUENCE_REL.name
                consequence_module = _load(consequence_path, 'r24_w4_const_consequence',
                                           CONSEQUENCE_SHA256)
            consequence_args = argparse.Namespace(**vars(args))
            consequence_args.evidence = work
            consequence_args.native_tool_home = args.native_tool_home
            consequence_args.runner_exit = 0
            consequence_args.failed_stage = 'complete'
            consequence = consequence_module.run(
                consequence_args, const_matrix_audit=matrix_audit,
                const_matrix_summary=matrix)
            need(type(consequence) is dict, 'consequence runner returned wrong type')
            record['consequence'] = consequence
            path = work / Path(getattr(consequence_module, 'SUMMARY_REL',
                                        Path('cases/r24-w4-const-consequence/W4-CONST-CONSEQUENCE.json')))
            record['consequence_summary_path'] = path.relative_to(outer_evidence).as_posix()
            if consequence.get('complete') is not True or consequence.get('body_proof_run') is not True or \
               consequence.get('call_linkage') != 'UNKNOWN' or consequence.get('accepted') is not False or \
               consequence.get('publication_allowed') is not False or consequence.get('proof_credit') != 0:
                record['errors'].append('consequence record incomplete or boundary differs')
            consequence_audit = consequence_module.audit(
                consequence_args, const_matrix_audit=matrix_audit,
                const_matrix_summary=matrix)
            record['consequence_audit'] = consequence_audit
            if type(consequence_audit) is not dict or \
               consequence_audit.get('complete') is not True or \
               consequence_audit.get('evidence_complete') is not True:
                record['errors'].append('consequence read-only audit incomplete')
            if not record['errors']:
                contract_module = _contract_module(args, contract_module)
                contract_args = _contract_args(args, work, contract_module, 0, 'complete')
                prerequisites = dict(const_matrix_summary=matrix, const_matrix_audit=matrix_audit,
                                     consequence_summary=consequence,
                                     consequence_audit=consequence_audit)
                diagnostic = contract_module.run(contract_args, **prerequisites)
                record['postqualification_diagnostic'] = diagnostic
                record['errors'].extend(_contract_boundary_errors(diagnostic))
                _save_summary(record_path, record)
                diagnostic_audit = contract_module.audit(contract_args, **prerequisites)
                record['postqualification_diagnostic_audit'] = diagnostic_audit
                record['errors'].extend(_contract_boundary_errors(diagnostic_audit, audited=True))
        record['source_observation'] = _source_observation(work)
    except BaseException as exc:
        record['errors'].append('exception: ' + type(exc).__name__ + ': ' + str(exc))
        record['source_observation'] = _source_observation(work)
        record['native_tool_hashes_after'] = _read_native_files(args)
        record['native_identity_errors'] = _validate_native_identities(
            record['native_tool_hashes_before'], record['native_tool_hashes_after'])
        try:
            _save_summary(record_path, record)
        except BaseException as write_error:
            try: exc.add_note('partial qualification summary write failed: ' + repr(write_error))
            except Exception: pass
        raise
    record['native_tool_hashes_after'] = _read_native_files(args)
    record['native_identity_errors'] = _validate_native_identities(
        record['native_tool_hashes_before'], record['native_tool_hashes_after'])
    if record['native_identity_errors']:
        record['errors'].extend(record['native_identity_errors'])
    record['errors'].extend(_validate_target_intent(
        args, work, record.get('target_intent_receipt')))
    record['tool_hashes_before'] = tool_before
    try:
        tool_after = _tool_identity(args.tool_home, TOOL_HASHES_8A)
    except BaseException as exc:
        tool_after = None
        record['errors'].append('frozen tool identity postcheck failed: ' + type(exc).__name__)
    record['tool_hashes_after'] = tool_after
    if tool_after != tool_before:
        record['errors'].append('frozen capture tool changed during qualification')
    record['complete'] = not record['errors'] and \
        record.get('source_observation', {}).get('complete') is True and \
        record.get('consequence', {}).get('complete') is True and \
        type(record.get('postqualification_diagnostic')) is dict and \
        record['postqualification_diagnostic'].get('complete') is True
    record['classification'] = ('CONST_CALLEE_REQUALIFIED_WITH_CONTRACT_INPUT_DIAGNOSTIC_SOURCE_REPORTED'
                                if record['complete'] else 'INCOMPLETE_CONST_REQUALIFICATION')
    record['accepted'] = False
    record['publication_allowed'] = False
    record['proof_credit'] = 0
    _save_summary(record_path, record)
    return record


def audit(args: argparse.Namespace, *, consequence_module: Any | None = None,
          contract_module: Any | None = None,
          env: dict[str, str] | None = None) -> dict[str, Any]:
    live_env = dict(os.environ)
    selected_env = live_env if env is None else dict(env)
    args.evidence = Path(args.evidence).resolve()
    raw_output = Path(args.output)
    need(not raw_output.is_symlink(), 'audit output must not be a symlink')
    args.output = raw_output.resolve()
    expected_output = (args.evidence / AUDIT_REL).resolve()
    need(args.output == expected_output and not args.output.exists() and
         not args.output.is_symlink(),
         'audit output must stay inside qualification evidence subtree')
    try:
        _context(args, selected_env, require_live_deadline=False)
        _mode(args)
        _validate_pins(args)
    except BaseException as exc:
        preflight = {
            'schema': 'select-r24-w4-const-qualification-v1-audit',
            'complete': False, 'evidence_complete': False,
            'candidate': getattr(args, 'candidate', None),
            'build_id': selected_env.get('CLOUD_BUILD_ID'),
            'phase_id': R24_PHASE, 'route_phase_id': R21_PHASE,
            'runner_exit': getattr(args, 'runner_exit', None),
            'failed_stage': getattr(args, 'failed_stage', None),
            'summary_path': SUMMARY_REL.as_posix(), 'summary_sha256': None,
            'errors': ['preflight: ' + type(exc).__name__ + ': ' + str(exc)],
            'accepted': False, 'publication_allowed': False, 'proof_credit': 0,
            'caller_body_proof_admission': False,
            'w4_caller_body_proof_status': 'UNKNOWN',
        }
        _write(args.output, preflight)
        return preflight
    summary_path = args.evidence / SUMMARY_REL
    source = _read_object(summary_path)
    errors: list[str] = []
    if source is None:
        errors.append('qualification summary missing or wrong type')
    else:
        if source.get('complete') is not True:
            errors.append('qualification source summary incomplete')
        if source.get('schema') != SCHEMA or source.get('candidate') != args.candidate:
            errors.append('qualification summary context differs')
        if source.get('build_id') != selected_env.get('CLOUD_BUILD_ID') or \
           source.get('mode_sha256') != MODE_SHA256:
            errors.append('qualification current Build/mode identity differs')
        if source.get('native_tool_home') != str(args.native_tool_home) or \
           source.get('native_schema') != str(args.schema) or \
           source.get('frozen_capture_tool_home') != str(args.tool_home):
            errors.append('qualification tool-home/schema identity differs')
        if source.get('phase_id') != R24_PHASE or source.get('route_phase_id') != R21_PHASE or \
           source.get('lane') != LANE or source.get('profile') != PROFILE:
            errors.append('qualification summary route identity differs')
        if source.get('accepted') is not False or source.get('publication_allowed') is not False or \
           source.get('proof_credit') != 0:
            errors.append('qualification summary boundary differs')
        work = args.evidence / WORK_REL
        if source.get('work_evidence_root') != str(work):
            errors.append('work evidence root differs')
        if source.get('target_intent_map_path') != (work / TARGET_INTENT_REL).relative_to(
                args.evidence).as_posix() or source.get('target_intent_receipt_path') != (
                work / TARGET_INTENT_RECEIPT_REL).relative_to(args.evidence).as_posix():
            errors.append('target-intent summary paths differ')
        errors.extend(_validate_provider_overlay_copy(
            args.evidence, work, source.get('provider_overlay_receipt_binding')))
        errors.extend(_validate_target_intent(args, work,
                                               source.get('target_intent_receipt')))
        actual_source = _source_observation(work)
        if source.get('source_observation') != actual_source or actual_source.get('complete') is not True:
            errors.append('source pair changed or summary observation differs')
        matrix = _read_object(work / CONST_MATRIX_REPORT_REL)
        errors.extend(_validate_matrix_rows(matrix, native_home=args.native_tool_home,
                                            build_id=selected_env.get('CLOUD_BUILD_ID')))
        errors.extend(_target_intent_matrix_errors(
            matrix, source.get('target_intent_receipt')))
        matrix_audit = _read_object(work / CONST_MATRIX_AUDIT_REL)
        if type(matrix_audit) is not dict or matrix_audit.get('evidence_complete') is not True:
            errors.append('frozen matrix audit missing/incomplete')
        if type(matrix_audit) is dict and (matrix_audit.get('accepted') is not False or
            matrix_audit.get('verification_accepted') is not False or
            matrix_audit.get('proof_credit') is not False):
            errors.append('frozen matrix audit boundary differs')
        try:
            refresh = _load(args.cloud_dir / O26_RECIPE_REL.name.replace(
                'o26-recipe', 'o26-refresh-recipe'),
                'r24_const_requal_o26_refresh', O26_RECIPE_SHA256)
            refresh.compare(work)
        except BaseException as exc:
            errors.append('fresh source/snapshot compare recheck failed: ' +
                          type(exc).__name__ + ': ' + str(exc))
        expected_stages = _stage_commands(args, work)
        saved_stages = source.get('stages') if type(source.get('stages')) is list else []
        if len(saved_stages) != len(expected_stages):
            errors.append('qualification stage inventory incomplete')
        for expected, actual in zip(expected_stages, saved_stages):
            if type(actual) is not dict or actual.get('name') != expected[0] or \
               actual.get('argv') != expected[1]:
                errors.append('qualification command identity differs: ' + expected[0])
                continue
            log_records = actual.get('physical_logs')
            if type(log_records) is not dict:
                errors.append('physical stage log inventory missing/wrong type')
                log_records = {}
            for channel, meta in log_records.items():
                if channel not in ('stdout', 'stderr') or type(meta) is not dict:
                    errors.append('physical stage log metadata malformed')
                    continue
                rel = Path(meta.get('path', ''))
                if rel.is_absolute() or '..' in rel.parts:
                    errors.append('physical stage log path unsafe')
                    continue
                path = work / rel
                if path.is_symlink() or not path.is_file():
                    errors.append('physical stage log missing/unsafe')
                    continue
                raw = path.read_bytes()
                if len(raw) != meta.get('bytes') or sha(raw) != meta.get('sha256'):
                    errors.append('physical stage log changed')
            errors.extend(_validate_stage_outputs(actual.get('name', ''), work, actual,
                native_home=args.native_tool_home, build_id=selected_env.get('CLOUD_BUILD_ID')))
            if actual.get('artifact_reports') != _stage_artifacts(actual.get('name', ''), work):
                errors.append('stage report artifacts changed: ' + expected[0])
        if matrix is not None:
            r21_audit = _load(args.cloud_dir / R21_AUDIT_REL.name,
                              'r24_const_requal_r21_audit', R21_AUDIT_SHA256)
            fresh_matrix_audit_path = work / CONST_MATRIX_AUDIT_REL
            fresh_matrix_audit = r21_audit.audit(argparse.Namespace(
                evidence=work, output=fresh_matrix_audit_path,
                runner_exit=0, failed_stage='complete'))
            if type(fresh_matrix_audit) is not dict or \
               fresh_matrix_audit.get('evidence_complete') is not True:
                errors.append('read-only R21 matrix audit recheck incomplete')
            if type(matrix_audit) is dict and fresh_matrix_audit != matrix_audit:
                errors.append('frozen R21 matrix audit changed on recheck')
            matrix_audit = fresh_matrix_audit
        if consequence_module is None:
            consequence_module = _load(args.cloud_dir / CONSEQUENCE_REL.name,
                                       'r24_w4_const_consequence_audit', CONSEQUENCE_SHA256)
        consequence_args = argparse.Namespace(**vars(args))
        consequence_args.evidence = work
        consequence_args.runner_exit = args.runner_exit
        consequence_args.failed_stage = args.failed_stage
        consequence = consequence_module.audit(
            consequence_args, const_matrix_audit=matrix_audit,
            const_matrix_summary=matrix)
        if type(consequence) is not dict or consequence.get('complete') is not True or \
           consequence.get('evidence_complete') is not True:
            errors.append('consequence physical audit incomplete')
        try:
            contract_module = _contract_module(args, contract_module)
            child = _contract_args(args, work, contract_module, args.runner_exit, args.failed_stage)
            consequence_summary = _read_object(work / consequence_module.SUMMARY_REL)
            diagnostic_audit = contract_module.audit(
                child, const_matrix_summary=matrix, const_matrix_audit=matrix_audit,
                consequence_summary=consequence_summary, consequence_audit=consequence)
            errors.extend(_contract_boundary_errors(diagnostic_audit, audited=True))
            saved_diagnostic = source.get('postqualification_diagnostic')
            physical_diagnostic = _read_object(work / contract_module.SUMMARY_REL)
            errors.extend(_contract_boundary_errors(physical_diagnostic))
            if saved_diagnostic != physical_diagnostic:
                errors.append('contract-input diagnostic summary changed after run')
        except BaseException as exc:
            errors.append('contract-input diagnostic audit failed: ' + type(exc).__name__ + ': ' + str(exc))
        before = source.get('native_tool_hashes_before')
        after = _read_native_files(args)
        errors.extend(_validate_native_identities(before, after))
        if source.get('native_tool_hashes_after') != after:
            errors.append('native tools differ from final run identity inventory')
        per_stage = source.get('native_tool_hashes_after_each_stage')
        source_stages = source.get('stages') if type(source.get('stages')) is list else []
        if type(per_stage) is not list or len(per_stage) != len(source_stages):
            errors.append('native per-stage identity inventory is incomplete')
        else:
            for item in per_stage:
                if type(item) is not dict or item.get('stage') not in {
                        'source-preflight', 'candidate-capture', 'candidate-source-compare',
                        'candidate-proof', 'r21-fractional-proof', 'const-regression-audit'}:
                    errors.append('native per-stage identity row malformed')
                    continue
                errors.extend(_validate_native_identities(before, item.get('hashes')))
        try:
            old_before = _tool_identity(args.tool_home, TOOL_HASHES_8A)
            if old_before != source.get('tool_hashes_before') or \
               old_before != source.get('tool_hashes_after'):
                errors.append('frozen 8a tool identity changed')
        except BaseException:
            errors.append('frozen 8a tool identity unavailable')
    audit_record = {
        'schema': 'select-r24-w4-const-qualification-v1-audit',
        'complete': not errors, 'evidence_complete': not errors,
        'candidate': args.candidate, 'build_id': selected_env.get('CLOUD_BUILD_ID'),
        'phase_id': R24_PHASE, 'route_phase_id': R21_PHASE,
        'runner_exit': args.runner_exit, 'failed_stage': args.failed_stage,
        'summary_path': SUMMARY_REL.as_posix(), 'summary_sha256':
            sha(summary_path.read_bytes()) if summary_path.is_file() and not summary_path.is_symlink() else None,
        'errors': errors, 'accepted': False, 'publication_allowed': False,
        'proof_credit': 0, 'caller_body_proof_admission': False,
        'w4_caller_body_proof_status': 'UNKNOWN',
    }
    _write(args.output, audit_record)
    return audit_record


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='action', required=True)
    for action in ('run', 'audit'):
        p = subs.add_parser(action)
        for name in ('repo', 'cloud-dir', 'evidence', 'tool-home', 'native-tool-home',
                     'schema', 'compiler-sysroot', 'capture-mode-file', 'mode-file'):
            p.add_argument('--' + name, type=Path, required=True)
        p.add_argument('--deadline-epoch', type=int, required=True)
        p.add_argument('--candidate', required=True)
        if action == 'audit':
            p.add_argument('--output', type=Path, required=True)
            p.add_argument('--runner-exit', type=int, required=True)
            p.add_argument('--failed-stage', required=True)
    args = parser.parse_args(argv)
    record = run(args) if args.action == 'run' else audit(args)
    print(json.dumps({'complete': record.get('complete'), 'accepted': False,
                      'publication_allowed': False, 'proof_credit': 0}))
    return 0 if record.get('complete') is True else 4


if __name__ == '__main__':
    raise SystemExit(main())

