#!/usr/bin/env python3
"""R24 Cloud-only source/MIR diagnostic capture for mutable P2; never proves."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import uuid
import subprocess
import sys
import traceback
from types import SimpleNamespace
from typing import Any

SCHEMA = 'select-r24-mut-capture-summary-v1'
MODE_SHA256 = '5ac2662dc74c166f17c01d11c7b44aa716ead91cc1ab24d6ee5fd6ad405ce624'
MODE_REL = Path('research/challenge-8/task-history/select-callee-r24/P2-MUT-CAPTURE-MODE.json')
R24_PHASE_ENV = 'SORT4_R24_SESSION_PHASE_ID'
R24_PHASE = 'SORT4-ACTUAL-SELECT-2026-10-24-R24'
R21_PHASE_ENV = 'SORT4_R20_CALLEE_PHASE_ID'
R21_PHASE = 'SORT4-ACTUAL-SELECT-2026-10-23-R21'
LANE = 'o26-select-callee-r20'
SOURCE_CHAIN_COMMIT = '17142eb2eba8e62a757e90552dffc592f79cec4e'
PROVIDER_SHA256 = '771970340f4fa928063cfa25db451535eb60ee1b246ef63c3cda4689842be616'
FRACTIONAL_SHA256 = '9cb4dee13b134f1ba328b35c23e667c4ef73961cf980147fdda8f9cb56d16c71'
O26_SHA256 = '464eef45b08b8724eba949289eff9cd745f48d65d0031ffae5675738856d562c'
REFRESH_SHA256 = '2cd963cc3d28c69370260cd2154e7284e189fea953928c3fc829f2fd53766af3'
CAPTURE_SHA256 = 'ffc3653263e86c5afa4f82440f10a2207e75ad8083bdad5f784597fe0dbaa84f'
CONTRACT_SHA256 = 'dc985de2e2a0e1a95e6c12c4b9cb78c4042d9d45f949d78904a999e82262b870'
MUTABLE_SOURCE_FILES = {
    'helper_writer': ('research/challenge-8/overnight-helper/prepare-actual-helper-capture-mut-parallel.py',
        '803062cd1bb500a600c278d3a03385f27e432b83ca8b0f6a5f141c6754a8a53e'),
    'owner_writer': ('research/challenge-8/overnight-helper/prepare-actual-owner-linked-mut.py',
        '1656b8f84ec8216ccf6e7079a5417d1699d76ac16b05cb6f622bf31d3ef2d8a8'),
    'nested_drop_writer': ('research/challenge-8/overnight-guard-actual/prepare-actual-nested-drop-mut.py',
        '20ea2cb3089549bdfa6ccfb134a7b8bcc681ec05f2d405ea7570042bbcc7bb5b'),
    'nine_body_writer': ('research/challenge-8/overnight-assume-actual/prepare-actual-nine-body-mut.py',
        '9b226ee015cc3f5404f4075d29c36abda45222087c7854b2b48e4cd9b44a5600'),
    'fingerprint_request': ('research/challenge-8/overnight-helper/prepare-mut-fingerprint-request.py',
        'b373e5836205ffb48e1cbd9dbd413939f5a26e49ee876103233c2ae4b2821bcd'),
    'mutable_provider': ('research/challenge-8/overnight-helper/mut_source_cloud_provider.py',
        '04fd1ca82bdbfb7f837a49ed303199024208c85124cf1a45b7893f6d20ed1871'),
}
EXPECTED_ORDER = [
    'sort4_certified_maybeuninit::sort4_checked_maybeuninit_new',
    'sort4_checked_as_mut_ptr', 'sort4_checked_pointer_drop',
    'sort4_checked_generic_drop', 'checked_transmute_neo_pointer',
    'checked_assume_init_pointer', 'checked_forget_owned',
    'select_unpredictable',
    '<select_unpredictable::DropOnPanic<T> as std::ops::Drop>::drop',
]
MUT_SIGNATURE = (
    b"pub fn select_unpredictable<Element>(\n"
    b"    condition: bool,\n    true_val: *mut Element,\n"
    b"    false_val: *mut Element,\n) -> *mut Element\n"
)
MUT_PREFIX = (b'#![feature(core_intrinsics)]\n#![allow(internal_features)]\n\n'
              b'use std::mem::MaybeUninit;\nuse std::{intrinsics, mem};\n\n')
BASELINE_SOURCE_PINS = {
    'hint_sha256': 'ce89716d46b8060db2c2da1aef1d4bcccf90e0804fc021d4470c55203501315f',
    'maybe_uninit_sha256': '1230d267542337ee2842c29d8227cf8a58fe75c53a2a70efaee3922c4e8e25c0',
}
RUNTIME_SENTINELS = (
    b'struct DropOnPanic<T> {', b'impl<T> Drop for DropOnPanic<T> {',
    b'unsafe { self.inner.drop_in_place() }',
    b'let guard = DropOnPanic { inner: guard };', b'drop.drop_in_place();',
    b'crate::mem::forget(guard);',
    b'crate::intrinsics::select_unpredictable(condition, true_val, false_val).assume_init()',
)
REQUEST_REL = Path('source-preparation/R24-MUT-CAPTURE-REQUEST.json')
SNAPSHOT_NAMES = ('unit', *(f'body-{index}' for index in range(9)))
REFUSAL_MARKER = (
    'SORT4-ACTUAL-NESTED-FINGERPRINT: diagnostic refusal: '
    'snapshot complete; no proof rule admitted')
CAPTURE_LOG = 'nine-body-fingerprint-refusal.log'
SUMMARY_REL = Path('cases/r24-mut-capture/MUT-CAPTURE-SUMMARY.json')
BLOCKED_OPT_INS = {
    'SORT4_R20_FINAL_SELECT_REPAIR', 'SORT4_R21_FRACTIONAL_FORGET',
    'SORT4_R21_FRACTIONAL_VARIANT', 'SORT4_R24_CHECKED_POINTER_OUTCOMES',
    'SORT4_MAYBEUNINIT_REPO_ROOT', 'SORT4_SELECT_INTRINSIC_REPO_ROOT',
    'SORT4_POINTER_DROP_REPO_ROOT', 'SORT4_GUARD_REPO_ROOT',
    'SORT4_GUARD_TEMPLATE_REPO_ROOT', 'SORT4_ACTUAL_OWNER_REPO_ROOT',
    'SORT4_ACTUAL_OWNER_ADMISSION', 'SORT4_ACTUAL_OWNER_NINE_ADMISSION',
    'SORT4_ACTUAL_FORGET_REPO_ROOT', 'SORT4_A1_LINK_REPO_ROOT',
    'SORT4_G1_CALL_REPO_ROOT', 'SORT4_STRICT_LFT_CUT', 'SORT4_HRTB_OUTPUT',
    'SORT4_HRTB_OUTPUT_TARGETS', 'SORT4_NESTED_FINGERPRINT_MODE',
    'SORT4_NESTED_FINGERPRINT_EVIDENCE_DIR',
    'SORT4_NESTED_FINGERPRINT_SOURCE_SHA256',
}


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def need(ok: bool, why: str) -> None:
    if not ok:
        raise RuntimeError('R24-MUT-CAPTURE: ' + why)


def _load(path: Path, name: str, expected: str):
    need(path.is_file() and not path.is_symlink() and sha(path.read_bytes()) == expected,
         'pinned module differs: ' + str(path))
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, 'module unavailable: ' + str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    need(sha(path.read_bytes()) == expected, 'module changed during import: ' + str(path))
    return module


def _validate_mode(args) -> dict[str, Any]:
    mode_path = Path(args.mode_file)
    expected_path = Path(args.repo) / MODE_REL
    need(mode_path.resolve() == expected_path.resolve() and
         mode_path.is_file() and not mode_path.is_symlink(),
         'exact R24 mode manifest path required')
    raw = mode_path.read_bytes()
    need(args.mode_sha256 == MODE_SHA256 and sha(raw) == MODE_SHA256,
         'R24 mutable capture mode hash differs')
    try:
        mode = json.loads(raw)
    except (ValueError, UnicodeDecodeError) as exc:
        raise RuntimeError('R24-MUT-CAPTURE: mode manifest is malformed') from exc
    expected = {
        'const_matrix_assurance': 'SOURCE_REPORTED',
        'const_matrix_source_evidence_build': 'db09fcc8-f33f-42c5-9d40-50c2c3d63658',
        'enabled': True, 'independent_proof_credit': 0,
        'owner': 'select-sort4', 'phase_id': R24_PHASE,
        'proof_admission': False, 'publication_allowed': False,
        'route_phase_id': R21_PHASE,
        'schema': 'select-r24-mut-capture-mode-v1',
        'source_chain_commit': SOURCE_CHAIN_COMMIT, 'source_only': True,
    }
    need(mode == expected, 'mode manifest fields or capture-only boundaries differ')
    return mode


def _validate_route(env: dict[str, str]) -> None:
    need(env.get('SMALLSORT_EXECUTION_PROVIDER') == 'cloud-build' and
         env.get(R24_PHASE_ENV) == R24_PHASE and
         env.get(R21_PHASE_ENV) == R21_PHASE and env.get('LANE') == LANE and
         not env.get('GITHUB_ACTIONS'),
         'exact live R24/R21 Cloud lane required')
    bad = sorted(key for key in env if key in BLOCKED_OPT_INS or
                 key.startswith('SORT4_R21_FRACTIONAL_'))
    need(not bad, 'ambient proof opt-ins refused: ' + ', '.join(bad))


def load_provider(cloud_dir: Path):
    return _load(cloud_dir / 'provider.py', 'r24_mut_capture_provider', PROVIDER_SHA256)


def _validate_overlay_receipt(repo: Path, cloud_dir: Path, evidence: Path,
                              fractional, o26) -> dict[str, Any]:
    receipt_path = evidence / 'candidate-provider-overlay.json'
    need(receipt_path.is_file() and not receipt_path.is_symlink(),
         'approved O26 provider-overlay receipt missing')
    try:
        receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        raise RuntimeError('R24-MUT-CAPTURE: provider-overlay receipt malformed') from exc
    provider_path = cloud_dir / 'provider.py'
    need(provider_path.is_file() and sha(provider_path.read_bytes()) == o26.PROVIDER_SHA and
         receipt.get('provider_sha256') == o26.PROVIDER_SHA and
         receipt.get('proof_sha') == o26.git_sha(repo),
         'O26 provider overlay receipt identity differs')
    paths = [path.as_posix() for path in o26.OVERLAYS]
    rows = receipt.get('files')
    need(isinstance(rows, list) and [row.get('path') if isinstance(row, dict) else None
         for row in rows] == paths, 'O26 guard-only overlay inventory differs')
    validated = []
    for rel_path, row in zip(o26.OVERLAYS, rows):
        rel = rel_path.as_posix()
        need(set(row) == {'path', 'original_sha256', 'cloud_overlay_sha256',
                          'guard_only', 'diff'} and row.get('guard_only') is True,
             'O26 overlay receipt row malformed: ' + rel)
        committed = subprocess.check_output(
            ['git', '-C', str(repo), 'show', 'HEAD:' + rel],
            stderr=subprocess.PIPE)
        need(sha(committed) == row.get('original_sha256'),
             'committed O26 overlay source hash differs: ' + rel)
        if rel == 'research/challenge-8/overnight-assume-actual/capture.py':
            need(sha(committed) == CAPTURE_SHA256,
                 'committed mode-9 capture source pin differs')
        expected = fractional._derive_o26_guard_overlay(committed, rel, o26)
        current_path = repo / rel_path
        need(current_path.is_file() and current_path.read_bytes() == expected and
             sha(expected) == row.get('cloud_overlay_sha256'),
             'current file is not the exact committed O26 guard-only overlay: ' + rel)
        before, after = committed.decode('utf-8'), expected.decode('utf-8')
        import difflib
        expected_diff = ''.join(difflib.unified_diff(
            before.splitlines(True), after.splitlines(True),
            fromfile=rel + '.committed', tofile=rel + '.cloud-guard'))
        need(row.get('diff') == expected_diff,
             'O26 overlay receipt diff is not the exact provider guard rewrite: ' + rel)
        validated.append({'path': rel, 'original_sha256': sha(committed),
                          'cloud_overlay_sha256': sha(expected), 'guard_only': True})
    return {'receipt_sha256': sha(receipt_path.read_bytes()), 'files': validated}


def load_capture_runtime(repo: Path, cloud_dir: Path, evidence: Path):
    fractional = _load(cloud_dir / 'select-callee-r21-fractional.py',
                       'r24_mut_capture_fractional_loader', FRACTIONAL_SHA256)
    o26 = fractional.load(cloud_dir / 'o26-recipe.py', 'r24_mut_capture_o26', O26_SHA256)
    refresh = fractional.load(cloud_dir / 'o26-refresh-recipe.py',
                              'r24_mut_capture_refresh', REFRESH_SHA256)
    overlays = _validate_overlay_receipt(repo, cloud_dir, evidence, fractional, o26)
    capture = o26.load_capture(repo, 'r24_mut_capture')
    need(callable(getattr(capture, 'full_body_capture', None)) and
         callable(getattr(capture, 'refusal_fingerprint', None)) and
         callable(getattr(capture, 'clear_semantic_opt_ins', None)) and
         callable(getattr(capture.GUARD, 'capture_case', None)),
         'pinned O26 capture services are incomplete')
    need(isinstance(refresh.BODIES, (tuple, list)) and len(refresh.BODIES) == 9,
         'pinned O26 nine-body service interface differs')
    return {'capture': capture, 'fractional': fractional, 'o26': o26,
            'refresh': refresh, 'overlays': overlays}


def load_source_writers(repo: Path):
    modules = {}
    for name, (rel, expected) in MUTABLE_SOURCE_FILES.items():
        modules[name] = _load(repo / rel, 'r24_mut_capture_' + name, expected)
    owner_modules = modules['owner_writer'].load_modules()
    need(isinstance(owner_modules, tuple) and owner_modules and
         callable(getattr(owner_modules[0], 'strip_ghost', None)),
         'pinned mutable source chain lacks ghost stripper')
    modules['owner'] = owner_modules[0]
    return modules


def _prepare_source_view(repo: Path, cloud_dir: Path,
                         capture_root: Path) -> tuple[Path, list[dict[str, Any]]]:
    """Copy pinned source inputs from committed recipe blobs, excluding Cloud overlays."""
    infra_root = Path(subprocess.check_output(
        ['git', '-C', str(cloud_dir), 'rev-parse', '--show-toplevel'], text=True).strip())
    recipe_rel = 'research/challenge-8/cloud-build/recipes/o26-select-callee-r20.json'
    recipe_raw = subprocess.check_output(['git', '-C', str(infra_root), 'show', 'HEAD:' + recipe_rel])
    recipe = json.loads(recipe_raw.decode('utf-8'))
    paths = recipe.get('proof_paths')
    need(isinstance(paths, list) and paths and all(isinstance(item, str) for item in paths),
         'committed O26 recipe proof path list is malformed')
    expected = {rel for rel, _ in MUTABLE_SOURCE_FILES.values()}
    need(expected.issubset(set(paths)),
         'committed O26 recipe omits a pinned mutable source dependency')
    source_view = capture_root / 'source-repository'
    source_view.mkdir()
    rows = []
    for rel in paths:
        need(not Path(rel).is_absolute() and '..' not in Path(rel).parts,
             'O26 proof path escapes source view: ' + rel)
        mode = subprocess.check_output(['git', '-C', str(repo), 'ls-tree', 'HEAD', '--', rel],
                                       text=True).split()
        need(len(mode) >= 3 and mode[0] in ('100644', '100755'),
             'O26 proof path is missing, nonregular, or symlinked: ' + rel)
        raw = subprocess.check_output(['git', '-C', str(repo), 'show', 'HEAD:' + rel])
        destination = source_view / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        need(not destination.exists() and not destination.is_symlink(),
             'source-view destination already exists: ' + rel)
        destination.write_bytes(raw)
        rows.append({'path': destination.relative_to(capture_root).as_posix(),
                     'bytes': len(raw), 'sha256': sha(raw)})
    provider_raw = (cloud_dir / 'provider.py').read_bytes()
    need(sha(provider_raw) == PROVIDER_SHA256,
         'infra checkout native provider pin differs')
    provider_rel = 'research/challenge-8/cloud-build/provider.py'
    provider_destination = source_view / provider_rel
    provider_destination.parent.mkdir(parents=True, exist_ok=True)
    need(not provider_destination.exists() and not provider_destination.is_symlink(),
         'source-view provider destination already exists')
    provider_destination.write_bytes(provider_raw)
    rows.append({'path': provider_destination.relative_to(capture_root).as_posix(),
                 'bytes': len(provider_raw), 'sha256': sha(provider_raw),
                 'source': 'PINNED_INFRA_CHECKOUT'})
    return source_view, rows


def _read_json(path: Path) -> dict[str, Any]:
    need(path.is_file() and not path.is_symlink(), 'expected source record missing: ' + str(path))
    value = json.loads(path.read_text(encoding='utf-8'))
    need(isinstance(value, dict), 'source record is not an object: ' + str(path))
    return value


def _make_capture_request(base_dir: Path, base_record: dict[str, Any], owner,
                          provider_record: dict[str, Any]) -> dict[str, Any]:
    """Validate the physical const-independent mutable baseline and emit a pending request."""
    original_path, verified_path = base_dir / 'original/lib.rs', base_dir / 'verified/lib.rs'
    original, _ = _safe_artifact(base_dir, original_path)
    verified, _ = _safe_artifact(base_dir, verified_path)
    cert = base_record.get('source_certificate')
    need(original.startswith(MUT_PREFIX + MUT_SIGNATURE) and original.endswith(b'\n'),
         'mutable baseline source prefix/signature boundary differs')
    exact_body = original[len(MUT_PREFIX + MUT_SIGNATURE):-1]
    need(base_record.get('fixture_signature') == MUT_SIGNATURE.decode() and
         base_record.get('contract_text_sha256') == CONTRACT_SHA256 and
         base_record.get('original_sha256') == sha(original) and
         base_record.get('verified_sha256') == sha(verified) and
         base_record.get('ghost_strip_identity') is True and
         owner.strip_ghost(verified) == original and
         verified.count(MUT_SIGNATURE) == 1 and b'*const' not in verified and
         original.count(b'*mut Element') == 3 and verified.count(b'/*@') == 3 and
         exact_body.startswith(b'{\n') and exact_body.endswith(b'}'),
         'mutable baseline source hashes, signature, or ghost-strip identity differ')
    need(isinstance(cert, dict) and
         all(cert.get(key) == value for key, value in BASELINE_SOURCE_PINS.items()) and
         cert.get('target_specialization') == 'T = *mut Element; Element unrestricted' and
         cert.get('runtime_body_exact') is True and
         cert.get('guard_and_drop_body_retained') is True and
         cert.get('actual_forget_redirect') is False and
         cert.get('actual_assume_init_redirect') is False and
         cert.get('fixture_writer_is_const_independent') is True and
         cert.get('helper_proof_status') == 'NOT_RUN' and
         cert.get('exact_body_sha256') == sha(exact_body) and
         cert.get('provider') == provider_record,
         'mutable baseline source certificate is missing or differs')
    for sentinel in RUNTIME_SENTINELS:
        need(original.count(sentinel) == 1,
             'mutable baseline runtime sentinel absent or ambiguous: ' + sentinel.decode())
    need(base_record.get('capture_only') is True and
         base_record.get('typed_mir_binding_established') is False and
         base_record.get('translator_admission') == 'NOT_IMPLEMENTED' and
         base_record.get('helper_proof_status') == 'NOT_RUN' and
         base_record.get('publication_status') == 'NOT_PUBLISHED' and
         type(base_record.get('proof_credit')) is int and base_record.get('proof_credit') == 0,
         'mutable baseline status claims admission, proof, or publication')
    return {
        'schema': 'select-r24-mut-capture-request-v1',
        'classification': 'STATIC_REQUEST_ONLY; NOT CLOUD EVIDENCE',
        'source_generation': 'CONST_INDEPENDENT_MUTABLE_PARALLEL',
        'legacy_request_status': 'NOT_USED_UNSUPPORTED_CONST_PAIR_INPUT',
        'fixture': {
            'original_sha256': sha(original), 'verified_sha256': sha(verified),
            'hint_source_sha256': cert['hint_sha256'],
            'maybe_uninit_source_sha256': cert['maybe_uninit_sha256'],
            'exact_body_sha256': cert.get('exact_body_sha256'),
            'contract_text_sha256': CONTRACT_SHA256,
            'signature': MUT_SIGNATURE.decode(), 'ghost_strip_identity': True,
            'runtime_body_exact': True,
        },
        'required_cloud_outputs': [
            {'name': name, 'status': 'PENDING_CLOUD_CAPTURE'} for name in (
                'verified_source_identity', 'original_source_identity',
                'normal_decoded_unit_and_body', 'readonly_decoded_unit_and_body',
                'snapshot_inventory_and_hashes')],
        'proof_status': 'NOT_RUN', 'translator_admission': 'NOT_IMPLEMENTED',
        'publication_status': 'NOT_PUBLISHED', 'proof_credit': 0,
    }


def _run_source_chain(repo: Path, root: Path, writers,
                     provider_record: dict[str, Any]) -> dict[str, Any]:
    owner_out = root / 'owner-linked'
    owner_result = writers['owner_writer'].build_linked_pair(repo, owner_out)
    owner_dir = owner_out / 'owner-linked-mut'
    owner_record = _read_json(owner_dir / 'fixture.json')
    base_dir = owner_out / 'mutable-actual-baseline'
    request_path = root / REQUEST_REL.name
    request = _make_capture_request(base_dir, _read_json(base_dir / 'fixture.json'),
                                    writers['owner'], provider_record)
    request_path.write_text(json.dumps(request, indent=2, sort_keys=True) + '\n',
                            encoding='utf-8')
    nested_out = root / 'nested-drop'
    nested_result = writers['nested_drop_writer'].write_case(owner_dir, nested_out, repo)
    seven_dir = nested_out / 'seven-body-owned-forget-mut'
    seven_record = _read_json(seven_dir / 'fixture.json')
    nine_out = root / 'nine-body'
    final_result = writers['nine_body_writer'].write_case(seven_dir, nine_out, repo)
    case = nine_out / 'nine-body-mut'
    final_record = _read_json(case / 'fixture.json')
    return {'owner_result': owner_result, 'owner_record': owner_record,
            'base_record': _read_json(base_dir / 'fixture.json'),
            'request': request, 'request_path': request_path,
            'nested_result': nested_result, 'seven_record': seven_record,
            'final_result': final_result, 'final_record': final_record,
            'case': case, 'owner': writers['owner']}


def _safe_artifact(root: Path, path: Path) -> tuple[bytes, dict[str, Any]]:
    need(not path.is_symlink() and path.is_file(), 'artifact missing or symlinked: ' + str(path))
    resolved_root, resolved = root.resolve(), path.resolve()
    need(resolved.is_relative_to(resolved_root), 'artifact escaped capture root: ' + str(path))
    data = path.read_bytes()
    return data, {'path': path.relative_to(root).as_posix(),
                  'bytes': len(data), 'sha256': sha(data)}


def _artifact_inventory(root: Path, evidence: Path, summary_path: Path) -> list[dict[str, Any]]:
    rows = []
    for path in sorted(root.rglob('*')):
        if path == summary_path:
            continue
        if path.is_symlink():
            raise RuntimeError('R24-MUT-CAPTURE: capture artifact is a symlink: ' + str(path))
        if path.is_file():
            _, row = _safe_artifact(root, path)
            row['path'] = (root / row['path']).relative_to(evidence).as_posix()
            rows.append(row)
        elif not path.is_dir():
            raise RuntimeError('R24-MUT-CAPTURE: capture artifact is not a regular file: ' + str(path))
    return rows


def _write_summary(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name('.' + path.name + '.tmp')
    temp.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    os.replace(temp, path)


def _capture_errors(capture, source: dict[str, Any], case: Path,
                    guard: object, full: object, fingerprint: object,
                    *, require_fingerprint: bool = True) -> list[str]:
    errors = []
    if not isinstance(guard, dict):
        return ['guard capture result is not an object']
    stages = guard.get('stages')
    required_stages = ('normal-export', 'normal-decode', 'readonly-export',
                       'readonly-decode', 'refinement')
    if not isinstance(stages, dict):
        errors.append('capture stages missing or wrong type')
        stages = {}
    for name in required_stages:
        row = stages.get(name)
        if (not isinstance(row, dict) or row.get('status') != 'RAN' or
                type(row.get('exit')) is not int or row.get('exit') != 0):
            errors.append(name + ' did not complete with exit 0')
    if guard.get('frontend_refinement') is not True or guard.get('source_unchanged') is not True:
        errors.append('paired source refinement or source integrity is incomplete')
    for name in ('normal-mir.bin', 'readonly-mir.bin'):
        path = case / name
        if not path.is_file() or path.is_symlink() or path.stat().st_size <= 0:
            errors.append(name + ' binary artifact is missing or empty')
    if not isinstance(full, dict) or set(full) != {'normal', 'readonly'}:
        errors.append('NORMAL/readonly full-body inventory differs')
    else:
        for mode in ('normal', 'readonly'):
            row = full.get(mode)
            if (not isinstance(row, dict) or
                    row.get('classification') != 'COMPLETE_NINE_BODY_CAPTURE_ONLY' or
                    row.get('exact_body_count_and_order') is not True or
                    not isinstance(row.get('bodies'), list) or
                    len(row.get('bodies', [])) != 9):
                errors.append(mode + ' nine-body capture is incomplete')
                continue
            if not all(isinstance(item, dict) for item in row['bodies']):
                errors.append(mode + ' body inventory contains a malformed row')
                continue
            if row.get('whole_decoded_mir_file') != f'{mode}-mir.txt':
                errors.append(mode + ' decoded unit artifact name differs')
            decoded_path = case / f'{mode}-mir.txt'
            if (not decoded_path.is_file() or decoded_path.is_symlink() or
                    sha(decoded_path.read_bytes()) != row.get('whole_decoded_mir_sha256')):
                errors.append(mode + ' decoded unit hash differs')
            if [item.get('defpath') for item in row['bodies']] != source.get('source_order'):
                errors.append(mode + ' body order differs from source record')
            for index, item in enumerate(row['bodies']):
                expected_file = f'{mode}-body-{index}-full-mir.txt'
                if (not isinstance(item, dict) or item.get('index') != index or
                        item.get('file') != expected_file):
                    errors.append(mode + ' body index differs')
                    break
                path = case / expected_file
                if (not path.is_file() or path.is_symlink() or
                        sha(path.read_bytes()) != item.get('sha256')):
                    errors.append(mode + ' body artifact hash differs: ' + str(index))
                    break
    if not isinstance(fingerprint, dict) and require_fingerprint:
        errors.append('mode-9 diagnostic fingerprint missing')
    elif isinstance(fingerprint, dict):
        stage = fingerprint.get('stage')
        if (fingerprint.get('classification') != 'INTENDED_DIAGNOSTIC_REFUSAL_NO_PROOF_RULE' or
                fingerprint.get('expected_refusal_seen') is not True or
                fingerprint.get('all_ten_snapshots') is not True or
                fingerprint.get('body_proof_run') is not False or
                not isinstance(stage, dict) or stage.get('status') != 'RAN' or
                type(stage.get('exit')) is not int or stage.get('exit') != 2):
            errors.append('native mode-9 diagnostic refusal is incomplete or unexpected')
        if fingerprint.get('fingerprint_probe_fatal'):
            errors.append('native mode-9 probe reported a fatal diagnostic')
        log = case / CAPTURE_LOG
        try:
            log_text = log.read_bytes().decode('utf-8', errors='strict')
        except (OSError, UnicodeDecodeError):
            log_text = ''
        if log_text.splitlines().count(REFUSAL_MARKER) != 1:
            errors.append('native mode-9 refusal marker is missing, duplicated, or malformed')
        snapshots = fingerprint.get('snapshots')
        if not isinstance(snapshots, dict) or set(snapshots) != set(SNAPSHOT_NAMES):
            errors.append('mode-9 snapshot inventory differs from unit plus nine bodies')
        else:
            for name in SNAPSHOT_NAMES:
                row = snapshots.get(name)
                expected_file = f'actual-nested-9-{name}.marshal'
                path = case / expected_file
                if (not isinstance(row, dict) or row.get('file') != expected_file or
                        type(row.get('bytes')) is not int or row.get('bytes') <= 0 or
                        not isinstance(row.get('sha256'), str) or not path.is_file() or
                        path.is_symlink() or path.stat().st_size != row.get('bytes') or
                        sha(path.read_bytes()) != row.get('sha256')):
                    errors.append('mode-9 snapshot missing/partial/mismatched: ' + name)
    return errors


def run(args, *, provider_loader=load_provider, capture_loader=load_capture_runtime,
        source_loader=load_source_writers, source_view_builder=_prepare_source_view) -> dict[str, Any]:
    env = dict(os.environ)
    _validate_route(env)
    _validate_mode(args)
    repo, cloud_dir, evidence = Path(args.repo), Path(args.cloud_dir), Path(args.evidence)
    need(repo.is_dir() and cloud_dir.is_dir() and evidence.is_dir() and
         not evidence.is_symlink(), 'repo, cloud-dir and evidence root must exist')
    mode_record_path = Path(args.mode_file)
    root = evidence / SUMMARY_REL.parent
    summary_path = evidence / SUMMARY_REL
    need(not root.exists() and not root.is_symlink(), 'fresh mutable capture evidence path required')
    provider = provider_loader(cloud_dir)
    provider_record = provider.require_supported_provider()
    need(isinstance(provider_record, dict) and
         provider_record.get('provider') == 'cloud-build' and
         provider_record.get('build_id') == env.get('CLOUD_BUILD_ID') and
         provider_record.get('project') == 'smallsort-ci' and
         provider_record.get('region') == 'global' and
         provider_record.get('os') == 'ubuntu-22.04' and
         provider_record.get('arch') == 'x86_64',
         'genuine native Cloud provider record is incomplete or mismatched')
    native_id = provider_record.get('build_id')
    try:
        canonical_native_id = str(uuid.UUID(native_id))
    except (ValueError, TypeError, AttributeError):
        canonical_native_id = None
    need(canonical_native_id == native_id,
         'native Cloud build ID is not a canonical UUID')
    capture_root = root
    capture_root.mkdir(parents=True, exist_ok=False)
    summary: dict[str, Any] = {
        'schema': SCHEMA, 'classification': 'INCOMPLETE_MUTABLE_SOURCE_MIR_CAPTURE',
        'complete': False, 'source_chain_commit': SOURCE_CHAIN_COMMIT,
        'r24_session_phase_id': R24_PHASE, 'r21_route_phase_id': R21_PHASE,
        'provider_record': provider_record, 'native_build_id': provider_record['build_id'],
        'mode_manifest': {'path': MODE_REL.as_posix(),
                          'sha256': MODE_SHA256},
            'source_records': {}, 'source_view_inventory': [], 'stages': {}, 'full_body_capture': None,
        'guard_capture': None, 'provider_overlay_identity': None,
        'source_chain_dependencies': {name: digest for name, (_, digest)
                                      in MUTABLE_SOURCE_FILES.items()},
        'fingerprint': None, 'artifact_inventory': [], 'incomplete_reasons': [],
        'diagnostic_verifier_invoked': False, 'actual_callee_proof_invoked': False,
        'body_proof_run': False, 'typed_admission': False,
        'semantic_rule_enabled': False, 'accepted': False, 'proof_credit': 0,
        'publication_allowed': False,
    }
    capture = None

    def save_partial(error: BaseException | None = None):
        if error is not None:
            summary['exception'] = {'type': type(error).__name__, 'message': str(error),
                                    'traceback': traceback.format_exc()}
        try:
            summary['artifact_inventory'] = _artifact_inventory(
                capture_root, evidence, summary_path)
        except BaseException as inventory_error:
            summary['artifact_inventory_error'] = type(inventory_error).__name__ + ': ' + str(inventory_error)
            summary['complete'] = False
            summary['classification'] = 'INCOMPLETE_MUTABLE_SOURCE_MIR_CAPTURE'
            summary['incomplete_reasons'] = list(summary.get('incomplete_reasons', [])) + [
                'artifact inventory failed: ' + type(inventory_error).__name__]
        _write_summary(summary_path, summary)

    try:
        runtime = capture_loader(repo, cloud_dir, evidence)
        capture = runtime['capture']
        source_view, source_view_inventory = source_view_builder(repo, cloud_dir, capture_root)
        writers = source_loader(source_view)
        capture.clear_semantic_opt_ins()
        source_root = capture_root / 'source-preparation'
        source_root.mkdir()
        chain = _run_source_chain(source_view, source_root, writers, provider_record)
        base_record = chain['base_record']
        final_record = chain['final_record']
        request = chain['request']
        case = chain['case']
        need(request.get('schema') == 'select-r24-mut-capture-request-v1' and
             request.get('classification') == 'STATIC_REQUEST_ONLY; NOT CLOUD EVIDENCE' and
             request.get('source_generation') == 'CONST_INDEPENDENT_MUTABLE_PARALLEL' and
             request.get('legacy_request_status') == 'NOT_USED_UNSUPPORTED_CONST_PAIR_INPUT' and
             request.get('proof_status') == 'NOT_RUN' and
             request.get('translator_admission') == 'NOT_IMPLEMENTED' and
             request.get('publication_status') == 'NOT_PUBLISHED' and
             request.get('proof_credit') == 0,
             'static mutable fingerprint request status was inflated')
        request_fixture = request.get('fixture')
        need(isinstance(request_fixture, dict) and
             request_fixture.get('contract_text_sha256') == CONTRACT_SHA256 and
             base_record.get('contract_text_sha256') == CONTRACT_SHA256,
             'mutable source request contract hash differs from the planned P2 interface')
        need(base_record.get('fixture_signature', '').count('*mut Element') == 3 and
             base_record.get('capture_only') is True and
             base_record.get('typed_mir_binding_established') is False and
             base_record.get('helper_proof_status') == 'NOT_RUN' and
             base_record.get('publication_status') == 'NOT_PUBLISHED' and
             base_record.get('proof_credit') == 0,
             'mutable baseline source record is not capture-only')
        need(final_record.get('classification') ==
             'SOURCE_ONLY_MUTABLE_NINE_BODY_A1_FRACTIONAL_CAPTURE' and
             final_record.get('specialization') == 'T = *mut Element; Element unrestricted' and
             final_record.get('source_order') == EXPECTED_ORDER and
             final_record.get('ghost_strip_identity') is True and
             final_record.get('typed_mir_binding_established') is False and
             final_record.get('translator_admission') == 'NOT_IMPLEMENTED' and
             final_record.get('helper_proof_status') == 'NOT_RUN' and
             final_record.get('publication_status') == 'NOT_PUBLISHED' and
             final_record.get('proof_credit') == 0,
             'mutable nine-body source record differs or claims admission')
        original_path, verified_path = case / 'original/lib.rs', case / 'verified/lib.rs'
        original, original_art = _safe_artifact(capture_root, original_path)
        verified, verified_art = _safe_artifact(capture_root, verified_path)
        need(sha(original) == final_record.get('original_sha256') and
             sha(verified) == final_record.get('verified_sha256') and
             chain['owner'].strip_ghost(verified) == original and
             b'*const Element' not in verified and
             verified.count(b'*mut Element') >= 3,
             'final mutable source pair hash, ghost-strip identity, or pointer kind differs')
        summary['source_records'] = {
            'baseline': base_record, 'owner_linked': chain['owner_record'],
            'seven_body': chain['seven_record'], 'final_nine_body': final_record,
            'static_fingerprint_request': request,
            'static_request_file': chain['request_path'].relative_to(evidence).as_posix(),
            'original': original_art, 'verified': verified_art,
            'original_sha256': sha(original), 'verified_sha256': sha(verified),
            'contract_text_sha256': base_record.get('contract_text_sha256'),
            'specialization': final_record['specialization'],
            'source_view_generation': 'COMMITTED_O26_RECIPE_PROOF_PATHS',
        }
        summary['source_view_inventory'] = source_view_inventory
        summary['provider_overlay_identity'] = runtime.get('overlays')
        need(not case.is_symlink() and case.resolve().is_relative_to(capture_root.resolve()),
             'final mutable source directory escaped capture root')
        args_capture = SimpleNamespace(tool_home=Path(args.tool_home), schema=Path(args.schema),
            compiler_sysroot=str(args.compiler_sysroot), deadline_epoch=int(args.deadline_epoch),
            first_barrier=False, fingerprint_probe=False)
        capture.clear_semantic_opt_ins()
        guard = capture.GUARD.capture_case(case, final_record, args_capture)
        summary['guard_capture'] = guard
        stages = guard.get('stages') if isinstance(guard, dict) else None
        full = capture.full_body_capture(case, final_record, stages or {})
        summary['stages'] = stages if isinstance(stages, dict) else {}
        summary['full_body_capture'] = full
        initial_errors = _capture_errors(capture, final_record, case, guard, full, None,
                                         require_fingerprint=False)
        fingerprint = None
        if not initial_errors:
            capture.clear_semantic_opt_ins()
            fingerprint = capture.refusal_fingerprint(case, final_record, args_capture)
            summary['diagnostic_verifier_invoked'] = True
        summary['fingerprint'] = fingerprint
        errors = initial_errors or _capture_errors(capture, final_record, case, guard, full, fingerprint)
        if errors:
            summary['incomplete_reasons'] = errors
            save_partial()
            return summary
        summary['complete'] = True
        summary['classification'] = 'MUTABLE_SOURCE_MIR_CAPTURE_ONLY'
        summary['incomplete_reasons'] = []
        save_partial()
        if summary.get('complete') is not True:
            return summary
        return summary
    except BaseException as exc:
        try:
            save_partial(exc)
        except BaseException:
            pass
        raise
    finally:
        if capture is not None:
            try:
                capture.clear_semantic_opt_ins()
            except BaseException:
                pass


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('repo', 'cloud-dir', 'evidence', 'tool-home', 'schema',
                 'compiler-sysroot', 'mode-file'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--deadline-epoch', type=int, required=True)
    parser.add_argument('--mode-sha256', required=True)
    result = run(parser.parse_args())
    print(json.dumps({'classification': result['classification'],
                      'complete': result['complete'],
                      'body_proof_run': False, 'proof_credit': 0}, sort_keys=True), flush=True)
    if result.get('complete') is not True:
        raise SystemExit(4)


if __name__ == '__main__':
    main()
