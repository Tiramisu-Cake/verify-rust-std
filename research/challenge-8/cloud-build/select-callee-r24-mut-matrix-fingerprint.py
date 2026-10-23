#!/usr/bin/env python3
"""R24 source/MIR fingerprint for the closed mutable ownership matrix; never proves."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys
import traceback
from types import SimpleNamespace
from typing import Any

SCHEMA = 'select-r24-mut-matrix-fingerprint-v1'
MODE_REL = Path('research/challenge-8/task-history/select-callee-r24/P2-MUT-MATRIX-FINGERPRINT-MODE.json')
MODE_SHA256 = '0f8c816ff1e588cd8f2cb066fae862ea17b07103397b5282982cb1c86cc84317'
PINS_REL = Path('research/challenge-8/task-history/select-callee-r24/P2-MUT-CAPTURE-PINS.json')
PINS_SHA256 = 'b10d8f472fd9babc5e73cb7a8da14ad691b0563975d0d6d956366165a47401d0'
OLD_ADAPTER_SHA256 = '96e770129d1fc08e798e4b3ce8ad3bfe5b7ba01b68dafd0e6dfa3e0c8957f756'
R21_NEGATIVE_SHA256 = '8a23499c9852dfdc9973cca186daa83dcc2f7836642c40627ab1def6dd763772'
R24_PHASE = 'SORT4-ACTUAL-SELECT-2026-10-24-R24'
R21_PHASE = 'SORT4-ACTUAL-SELECT-2026-10-23-R21'
R24_PHASE_ENV = 'SORT4_R24_SESSION_PHASE_ID'
R21_PHASE_ENV = 'SORT4_R20_CALLEE_PHASE_ID'
LANE = 'o26-select-callee-r20'
POSITIVE_BUILD = 'b606d510-6832-483e-8168-afe8ef5fe9b4'
EXPECTED_ORIGINAL_SHA256 = '3bf0bf792c8135bf964f19b3aaadef38b8ca5ee9ec95107029ad99d28a807aaa'
EXPECTED_VERIFIED_SHA256 = '74b20681c4c34cdc9ecd0fbb7fb3d44c51941e5d9640ede5705c5d6b6fa25165'
CONTRACT_SHA256 = 'dc985de2e2a0e1a95e6c12c4b9cb78c4042d9d45f949d78904a999e82262b870'
VARIANTS = (
    'positive', 'omit-selected-own', 'omit-unselected-own', 'no-retained-half',
    'callee-false-normal', 'callee-owner-duplicate', 'callee-owner-loss',
    'callee-thread-duplicate',
)
SNAPSHOT_NAMES = ('unit', *(f'body-{index}' for index in range(9)))
FIXED_BODY_INDICES = (0, 1, 2, 3, 4, 5, 8)
SUMMARY_REL = Path('cases/r24-mut-matrix-fingerprint/MUT-MATRIX-FINGERPRINT.json')
MATRIX_ROOT_REL = SUMMARY_REL.parent
POSITIVE_ORIGINAL_REL = Path('source-preparation/nine-body/nine-body-mut/original/lib.rs')
POSITIVE_VERIFIED_REL = Path('source-preparation/nine-body/nine-body-mut/verified/lib.rs')


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def need(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError('R24-MUT-MATRIX-FINGERPRINT: ' + message)


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


def load_old_adapter(cloud_dir: Path):
    return _load(cloud_dir / 'select-callee-r24-mut-capture.py',
                 'r24_mut_matrix_frozen_positive_adapter', OLD_ADAPTER_SHA256)


def load_negative_transform(repo: Path):
    return _load(repo / 'research/challenge-8/overnight-assume-actual/r21_fractional_forget.py',
                 'r24_mut_matrix_r21_negative_transform', R21_NEGATIVE_SHA256)


def _validate_matrix_mode(args, old) -> tuple[dict[str, Any], dict[str, Any]]:
    env = dict(os.environ)
    allowed_sort4 = {R24_PHASE_ENV, R21_PHASE_ENV, 'SORT4_SELECT_PROFILE'}
    proof_flags = sorted(key for key in env if
        key.startswith('SORT4_') and
        (key not in allowed_sort4 or
         (key == 'SORT4_SELECT_PROFILE' and
          env.get(key) != 'experimental-s6-26.10-v1')))
    need(not proof_flags, 'ambient R20/R21/R24 proof opt-ins refused: ' + ', '.join(proof_flags))
    need(env.get('SORT4_SELECT_PROFILE') == 'experimental-s6-26.10-v1',
         'exact runner SORT4_SELECT_PROFILE required')
    mode_path = Path(args.matrix_mode_file)
    expected_mode_path = Path(args.repo) / MODE_REL
    need(mode_path.resolve() == expected_mode_path.resolve() and
         mode_path.is_file() and not mode_path.is_symlink(),
         'exact mutable matrix mode path required')
    mode_raw = mode_path.read_bytes()
    need(args.matrix_mode_sha256 == MODE_SHA256 and sha(mode_raw) == MODE_SHA256,
         'mutable matrix mode hash differs')
    try:
        mode = json.loads(mode_raw)
    except (ValueError, UnicodeDecodeError) as exc:
        raise RuntimeError('R24-MUT-MATRIX-FINGERPRINT: matrix mode malformed') from exc
    expected_mode = {
        'enabled': True, 'independent_proof_credit': 0, 'owner': 'select-sort4',
        'phase_id': R24_PHASE, 'positive_evidence_build': POSITIVE_BUILD,
        'positive_pins_file': PINS_REL.as_posix(), 'positive_pins_sha256': PINS_SHA256,
        'proof_admission': False, 'publication_allowed': False,
        'route_phase_id': R21_PHASE,
        'schema': 'select-r24-mut-matrix-fingerprint-mode-v1', 'source_only': True,
        'variant_order': list(VARIANTS),
    }
    need(mode == expected_mode, 'mutable matrix mode fields/bounds/variant order differ')
    pins_path = Path(args.repo) / PINS_REL
    need(pins_path.is_file() and not pins_path.is_symlink() and
         mode['positive_pins_file'] == PINS_REL.as_posix(),
         'positive pin manifest path differs')
    pins_raw = pins_path.read_bytes()
    need(sha(pins_raw) == PINS_SHA256, 'positive pin manifest hash differs')
    try:
        pins = json.loads(pins_raw)
    except (ValueError, UnicodeDecodeError) as exc:
        raise RuntimeError('R24-MUT-MATRIX-FINGERPRINT: positive pin manifest malformed') from exc
    _validate_pins(pins)
    old._validate_route(dict(os.environ))
    old._validate_mode(args)
    return mode, pins


def _validate_pins(pins: dict[str, Any]) -> None:
    need(isinstance(pins, dict) and pins.get('schema') == 'select-r24-mut-positive-capture-pins-v1' and
         pins.get('build_id') == POSITIVE_BUILD and
         pins.get('status') == 'COMPLETE_SOURCE_REPORTED_CAPTURE_ONLY' and
         pins.get('accepted') is False and pins.get('proof_credit') == 0 and
         pins.get('body_proof_run') is False and pins.get('typed_admission') is False and
         pins.get('publication_allowed') is False,
         'positive pin record schema, source-only status, or proof boundaries differ')
    source = pins.get('source')
    need(isinstance(source, dict) and
         source.get('original_sha256') == EXPECTED_ORIGINAL_SHA256 and
         source.get('verified_sha256') == EXPECTED_VERIFIED_SHA256 and
         source.get('specialization') == 'T = *mut Element; Element unrestricted' and
         source.get('contract_text_sha256') == CONTRACT_SHA256,
         'positive source identity pins differ')
    need(set(pins.get('snapshots', {})) == set(SNAPSHOT_NAMES),
         'positive ten-snapshot names differ')
    for name in SNAPSHOT_NAMES:
        row = pins['snapshots'][name]
        need(isinstance(row, dict) and row.get('file') == f'actual-nested-9-{name}.marshal' and
             type(row.get('bytes')) is int and row['bytes'] > 0 and
             isinstance(row.get('sha256'), str) and re.fullmatch(r'[0-9a-f]{64}', row['sha256']),
             'positive snapshot pin malformed: ' + name)
    for mode, expected in (
        ('normal', 'df9a9e3ddf2fbab08133473d57b226c89ecf6c3b9785f68e79fbc236e5fd1cd1'),
        ('readonly', 'fea41b1dd6a4ae912c20e53c9afc8de24906f5934b89aadd15b92d6f48a1eb91'),
    ):
        row = pins.get(mode)
        need(isinstance(row, dict) and row.get('classification') == 'COMPLETE_NINE_BODY_CAPTURE_ONLY' and
             row.get('exact_body_count_and_order') is True and row.get('decoded_sha256') == expected,
             'positive decoded MIR pin differs: ' + mode)


def _read_source_pair(evidence: Path, old_summary: dict[str, Any], old,
                      pins: dict[str, Any]) -> tuple[bytes, bytes, dict[str, Any], Path, Any]:
    records = old_summary.get('source_records')
    need(isinstance(records, dict), 'positive capture source records missing')
    source = records.get('final_nine_body')
    need(isinstance(source, dict), 'positive nine-body source record missing')
    original_meta, verified_meta = records.get('original'), records.get('verified')
    need(isinstance(original_meta, dict) and isinstance(verified_meta, dict),
         'positive physical source paths missing')
    old_root = evidence / 'cases/r24-mut-capture'
    need(original_meta.get('path') == POSITIVE_ORIGINAL_REL.as_posix() and
         verified_meta.get('path') == POSITIVE_VERIFIED_REL.as_posix(),
         'positive source paths are not canonical old-capture-relative paths')
    original_path = old_root / POSITIVE_ORIGINAL_REL
    verified_path = old_root / POSITIVE_VERIFIED_REL
    original, _ = old._safe_artifact(old_root, original_path)
    verified, _ = old._safe_artifact(old_root, verified_path)
    need(sha(original) == pins['source']['original_sha256'] and
         sha(verified) == pins['source']['verified_sha256'] and
         source.get('original_sha256') == sha(original) and
         source.get('verified_sha256') == sha(verified) and
         source.get('specialization') == 'T = *mut Element; Element unrestricted' and
         records.get('contract_text_sha256') == CONTRACT_SHA256,
         'regenerated mutable positive sourcepair differs from b606 pins')
    source_view = old_root / 'source-repository'
    writers = old.load_source_writers(source_view)
    owner = writers['owner']
    need(owner.strip_ghost(verified) == original,
         'regenerated mutable positive source fails ghost-strip identity')
    return original, verified, source, old_root, owner


def _validate_positive_capture(old_summary: dict[str, Any], pins: dict[str, Any],
                               evidence: Path, old) -> tuple[bytes, bytes, dict[str, Any], Path, Any]:
    provider_record = old_summary.get('provider_record')
    need(old_summary.get('complete') is True and
         old_summary.get('classification') == 'MUTABLE_SOURCE_MIR_CAPTURE_ONLY' and
         old_summary.get('native_build_id') == os.environ.get('CLOUD_BUILD_ID') and
         isinstance(provider_record, dict) and
         provider_record.get('build_id') == os.environ.get('CLOUD_BUILD_ID'),
         'frozen positive capture is incomplete or not from current native build')
    original, verified, source, old_root, owner = _read_source_pair(evidence, old_summary, old, pins)
    need(sha(original) == pins['source']['original_sha256'] and
         sha(verified) == pins['source']['verified_sha256'],
         'frozen positive sourcepair fails b606 manifest')
    full = old_summary.get('full_body_capture')
    need(isinstance(full, dict), 'frozen positive full-body capture missing')
    fingerprint = old_summary.get('fingerprint')
    need(isinstance(fingerprint, dict), 'frozen positive fingerprint missing')
    for mode in ('normal', 'readonly'):
        row = full.get(mode)
        need(isinstance(row, dict) and
             row.get('classification') == 'COMPLETE_NINE_BODY_CAPTURE_ONLY' and
             row.get('exact_body_count_and_order') is True and
             row.get('whole_decoded_mir_sha256') == pins[mode]['decoded_sha256'] and
             isinstance(row.get('bodies'), list) and len(row['bodies']) == 9,
             'regenerated positive decoded MIR/body inventory differs: ' + mode)
    case = old_root / 'source-preparation/nine-body/nine-body-mut'
    _validate_snapshot_files(case, fingerprint, pins['snapshots'], SNAPSHOT_NAMES)
    return original, verified, source, old_root, owner


def _validate_snapshot_files(case: Path, fingerprint: dict[str, Any],
                             expected: dict[str, Any] | None,
                             names: tuple[str, ...]) -> list[dict[str, Any]]:
    rows = fingerprint.get('snapshots')
    need(isinstance(rows, dict) and set(rows) == set(names), 'snapshot row names differ')
    bound = []
    for name in names:
        row = rows.get(name)
        need(isinstance(row, dict) and row.get('file') == f'actual-nested-9-{name}.marshal',
             'snapshot record malformed: ' + name)
        path = case / row['file']
        need(path.is_file() and not path.is_symlink(), 'snapshot missing or symlinked: ' + name)
        data = path.read_bytes()
        need(type(row.get('bytes')) is int and row['bytes'] == len(data) and len(data) > 0 and
             row.get('sha256') == sha(data), 'snapshot physical bytes/hash differ: ' + name)
        if expected is not None:
            pin = expected[name]
            need(len(data) == pin['bytes'] and sha(data) == pin['sha256'],
                 'positive snapshot does not reproduce b606 pin: ' + name)
        bound.append({'file': path.name, 'bytes': len(data), 'sha256': sha(data)})
    return bound


def _copy_variant(case: Path, original: bytes, positive_verified: bytes,
                  source: dict[str, Any], variant: str, transform, owner) -> dict[str, Any]:
    need(not case.exists() and not case.is_symlink(), 'fresh matrix variant case required')
    original_dir, verified_dir = case / 'original', case / 'verified'
    original_dir.mkdir(parents=True)
    verified_dir.mkdir()
    verified = positive_verified if variant == 'positive' else transform(positive_verified, variant)
    need(isinstance(verified, bytes), 'variant transform returned nonbytes')
    original_path, verified_path = original_dir / 'lib.rs', verified_dir / 'lib.rs'
    original_path.write_bytes(original)
    verified_path.write_bytes(verified)
    need(owner.strip_ghost(verified) == original,
         'variant ghost-strip identity differs: ' + variant)
    original_sha, verified_sha = sha(original), sha(verified)
    if variant == 'positive':
        need(verified_sha == source.get('verified_sha256'), 'fresh positive source hash differs')
    else:
        need(verified_sha != EXPECTED_VERIFIED_SHA256,
             'negative variant did not change verified source: ' + variant)
    current = dict(source)
    current.update({'original_sha256': original_sha, 'verified_sha256': verified_sha,
                    'ghost_strip_identity': True, 'typed_mir_binding_established': False,
                    'translator_admission': 'NOT_IMPLEMENTED', 'helper_proof_status': 'NOT_RUN',
                    'publication_status': 'NOT_PUBLISHED', 'proof_credit': 0})
    return current


def _body_map(full: Any, mode: str) -> dict[int, dict[str, Any]]:
    need(isinstance(full, dict) and isinstance(full.get(mode), dict),
         'full-body mode missing: ' + mode)
    rows = full[mode].get('bodies')
    need(isinstance(rows, list) and len(rows) == 9 and all(isinstance(row, dict) for row in rows),
         'full-body rows malformed: ' + mode)
    return {row.get('index'): row for row in rows}


def _full_body_artifact_errors(case: Path, full: Any) -> list[str]:
    errors = []
    if not isinstance(full, dict):
        return ['full-body artifact inventory missing']
    for mode in ('normal', 'readonly'):
        row = full.get(mode)
        if not isinstance(row, dict) or not isinstance(row.get('bodies'), list):
            errors.append(mode + ' full-body rows missing')
            continue
        for item in row['bodies']:
            if not isinstance(item, dict):
                errors.append(mode + ' full-body row malformed')
                continue
            path = case / str(item.get('file', ''))
            if (not path.is_file() or path.is_symlink() or
                    type(item.get('bytes')) is not int or
                    path.stat().st_size != item.get('bytes') or
                    sha(path.read_bytes()) != item.get('sha256')):
                errors.append(mode + ' full-body file size/hash differs at index ' +
                              str(item.get('index')))
    return errors


def _fixed_body_unchanged(row: dict[str, Any], baseline_full: dict[str, Any]) -> list[str]:
    errors = []
    for mode in ('normal', 'readonly'):
        current, baseline = _body_map(row.get('full_body_capture'), mode), _body_map(baseline_full, mode)
        for index in FIXED_BODY_INDICES:
            if current.get(index, {}).get('sha256') != baseline.get(index, {}).get('sha256'):
                errors.append(f'{mode} body-{index} changed outside allowed 6/7 sites')
    current_snaps = (row.get('fingerprint') or {}).get('snapshots')
    base_snaps = (baseline_full.get('_positive_snapshots') or {})
    if not isinstance(current_snaps, dict):
        errors.append('variant snapshot rows missing')
    else:
        for name in ('body-0', 'body-1', 'body-2', 'body-3', 'body-4', 'body-5', 'body-8'):
            if (current_snaps.get(name, {}).get('sha256') !=
                    base_snaps.get(name, {}).get('sha256')):
                errors.append(f'{name} snapshot changed outside allowed bodies 6/7')
    return errors


def _capture_one(old, capture, args, capture_root: Path, case: Path, source: dict[str, Any],
                 owner, variant: str, current_build: str) -> dict[str, Any]:
    row: dict[str, Any] = {
        'variant': variant, 'case_path': case.as_posix(), 'complete': False,
        'status': 'INCOMPLETE_SOURCE_REPORTED_FINGERPRINT',
        'native_build_id': current_build, 'source_unchanged': False,
        'ghost_strip_identity': False, 'original_sha256': source.get('original_sha256'),
        'verified_sha256': source.get('verified_sha256'), 'source': source,
        'stages': {}, 'guard_capture': None, 'full_body_capture': None,
        'fingerprint': None, 'artifact_inventory': [], 'incomplete_reasons': [],
        'body_proof_run': False, 'typed_admission': False,
        'semantic_rule_enabled': False, 'accepted': False, 'proof_credit': 0,
        'publication_allowed': False,
    }
    capture.clear_semantic_opt_ins()
    capture_args = SimpleNamespace(tool_home=Path(args.tool_home), schema=Path(args.schema),
        compiler_sysroot=str(args.compiler_sysroot), deadline_epoch=int(args.deadline_epoch),
        first_barrier=False, fingerprint_probe=False)
    guard = capture.GUARD.capture_case(case, source, capture_args)
    row['guard_capture'] = guard
    stages = guard.get('stages') if isinstance(guard, dict) else None
    row['stages'] = stages if isinstance(stages, dict) else {}
    full = capture.full_body_capture(case, source, stages if isinstance(stages, dict) else {})
    row['full_body_capture'] = full
    errors = old._capture_errors(capture, source, case, guard, full, None,
                                 require_fingerprint=False)
    errors.extend(_full_body_artifact_errors(case, full))
    if not errors:
        capture.clear_semantic_opt_ins()
        fingerprint = capture.refusal_fingerprint(case, source, capture_args)
        row['fingerprint'] = fingerprint
        errors.extend(old._capture_errors(capture, source, case, guard, full, fingerprint))
    errors.extend(old._final_source_pair_errors(capture_root, case, source, owner))
    row['source_unchanged'] = (isinstance(guard, dict) and guard.get('source_unchanged') is True and
        isinstance(row.get('fingerprint'), dict) and
        isinstance(row['fingerprint'].get('stage'), dict) and
        row['fingerprint']['stage'].get('source_unchanged') is True)
    row['ghost_strip_identity'] = not old._final_source_pair_errors(
        capture_root, case, source, owner)
    if row['fingerprint'] is not None:
        try:
            _validate_snapshot_files(case, row['fingerprint'], None, SNAPSHOT_NAMES)
        except BaseException as exc:
            errors.append('physical snapshot validation failed: ' + type(exc).__name__)
    if errors:
        row['incomplete_reasons'] = errors
        return row
    row['complete'] = True
    row['status'] = 'COMPLETE_SOURCE_REPORTED_FINGERPRINT'
    return row


def _positive_row_from_old(old, capture, evidence: Path, old_summary: dict[str, Any],
                           source: dict[str, Any], old_root: Path,
                           owner, current_build: str) -> dict[str, Any]:
    case = old_root / 'source-preparation/nine-body/nine-body-mut'
    guard, full, fingerprint = (old_summary.get('guard_capture'),
                                old_summary.get('full_body_capture'),
                                old_summary.get('fingerprint'))
    errors = old._capture_errors(capture, source, case, guard, full, fingerprint)
    errors.extend(_full_body_artifact_errors(case, full))
    errors.extend(old._final_source_pair_errors(old_root, case, source, owner))
    guard_unchanged = isinstance(guard, dict) and guard.get('source_unchanged') is True
    fingerprint_stage = fingerprint.get('stage') if isinstance(fingerprint, dict) else None
    fingerprint_unchanged = (isinstance(fingerprint_stage, dict) and
                              fingerprint_stage.get('source_unchanged') is True)
    row = {'variant': 'positive', 'case_path': case.relative_to(evidence).as_posix(),
        'complete': not errors,
        'status': ('COMPLETE_SOURCE_REPORTED_FINGERPRINT' if not errors else
                   'INCOMPLETE_SOURCE_REPORTED_FINGERPRINT'),
        'native_build_id': current_build, 'provider_record': old_summary.get('provider_record'),
        'source_unchanged': not errors and guard_unchanged and fingerprint_unchanged,
        'ghost_strip_identity': not errors, 'original_sha256': source.get('original_sha256'),
        'verified_sha256': source.get('verified_sha256'), 'source': source,
        'stages': old_summary.get('stages', {}), 'guard_capture': guard,
        'full_body_capture': full, 'fingerprint': fingerprint,
        'artifact_inventory': [], 'incomplete_reasons': errors,
        'body_proof_run': False, 'typed_admission': False,
        'semantic_rule_enabled': False, 'accepted': False, 'proof_credit': 0,
        'publication_allowed': False}
    try:
        row['artifact_inventory'] = _inventory(case, evidence, evidence / SUMMARY_REL)
    except BaseException as exc:
        row['complete'] = False
        row['status'] = 'INCOMPLETE_SOURCE_REPORTED_FINGERPRINT'
        row['incomplete_reasons'].append('positive artifact inventory failed: ' + type(exc).__name__)
    return row


def _inventory(root: Path, evidence: Path, summary_path: Path) -> list[dict[str, Any]]:
    rows = []
    for path in sorted(root.rglob('*')):
        if path == summary_path:
            continue
        if path.is_symlink():
            raise RuntimeError('R24-MUT-MATRIX-FINGERPRINT: artifact symlink: ' + str(path))
        if path.is_file():
            data = path.read_bytes()
            rows.append({'path': path.relative_to(evidence).as_posix(),
                         'bytes': len(data), 'sha256': sha(data)})
        elif not path.is_dir():
            raise RuntimeError('R24-MUT-MATRIX-FINGERPRINT: nonregular artifact: ' + str(path))
    return rows


def _write_summary(path: Path, summary: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name('.' + path.name + '.tmp')
    temp.write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    os.replace(temp, path)


def run(args, *, old_adapter=None, positive_pins_loader=None,
        capture_loader=None, source_loader=None, transform_loader=None,
        pins_validator=_validate_pins) -> dict[str, Any]:
    if old_adapter is None:
        old_adapter = load_old_adapter(Path(args.cloud_dir))
    old = old_adapter
    old._validate_route(dict(os.environ))
    old._validate_mode(args)
    mode, official_pins = _validate_matrix_mode(args, old)
    pins = positive_pins_loader(Path(args.repo)) if positive_pins_loader else official_pins
    pins_validator(pins)
    repo, cloud_dir, evidence = Path(args.repo), Path(args.cloud_dir), Path(args.evidence)
    need(repo.is_dir() and cloud_dir.is_dir() and evidence.is_dir() and not evidence.is_symlink(),
         'repo, cloud-dir and evidence root must exist')
    root, summary_path = evidence / MATRIX_ROOT_REL, evidence / SUMMARY_REL
    need(not root.exists() and not root.is_symlink(), 'fresh mutable matrix evidence path required')
    root.mkdir(parents=True)
    summary: dict[str, Any] = {
        'schema': SCHEMA, 'classification': 'INCOMPLETE_MUTABLE_MATRIX_FINGERPRINT',
        'complete': False, 'mode_manifest': {'path': MODE_REL.as_posix(), 'sha256': MODE_SHA256},
        'positive_pins': {'path': PINS_REL.as_posix(), 'sha256': PINS_SHA256,
                          'build_id': POSITIVE_BUILD},
        'positive_evidence_build': POSITIVE_BUILD, 'r24_session_phase_id': R24_PHASE,
        'r21_route_phase_id': R21_PHASE, 'native_build_id': os.environ.get('CLOUD_BUILD_ID'),
        'provider_record': None, 'variant_order': list(VARIANTS), 'source_only': True, 'rows': {},
        'location_control': {'complete': False, 'reproduces_positive_pins': False,
                             'native_build_id': os.environ.get('CLOUD_BUILD_ID')},
        'artifact_inventory': [], 'incomplete_reasons': [],
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
            summary['artifact_inventory'] = _inventory(root, evidence, summary_path)
        except BaseException as inventory_error:
            summary['artifact_inventory_error'] = type(inventory_error).__name__ + ': ' + str(inventory_error)
            summary['complete'] = False
            summary['classification'] = 'INCOMPLETE_MUTABLE_MATRIX_FINGERPRINT'
            summary['incomplete_reasons'] = list(summary.get('incomplete_reasons', [])) + [
                'artifact inventory failed: ' + type(inventory_error).__name__]
        _write_summary(summary_path, summary)

    try:
        summary['rows']['positive'] = {
            'variant': 'positive', 'complete': False,
            'status': 'INCOMPLETE_SOURCE_REPORTED_FINGERPRINT',
            'native_build_id': os.environ.get('CLOUD_BUILD_ID'),
            'source_unchanged': False, 'ghost_strip_identity': False,
            'incomplete_reasons': ['frozen positive capture not yet validated'],
            'body_proof_run': False, 'typed_admission': False,
            'semantic_rule_enabled': False, 'accepted': False,
            'proof_credit': 0, 'publication_allowed': False,
        }
        old_summary = old.run(args)
        if not isinstance(old_summary, dict) or old_summary.get('complete') is not True:
            summary['rows']['positive']['incomplete_reasons'] = [
                'frozen positive adapter returned incomplete capture']
            summary['incomplete_reasons'].append('frozen positive capture incomplete')
            save_partial()
            return summary
        try:
            original, positive_verified, positive_source, old_root, owner = \
                _validate_positive_capture(old_summary, pins, evidence, old)
        except RuntimeError as validation_error:
            summary['rows']['positive']['incomplete_reasons'] = [str(validation_error)]
            summary['incomplete_reasons'].append(str(validation_error))
            save_partial()
            return summary
        current_build = os.environ.get('CLOUD_BUILD_ID')
        provider_record = old_summary.get('provider_record')
        if not isinstance(provider_record, dict) or provider_record.get('build_id') != current_build:
            summary['rows']['positive']['incomplete_reasons'] = [
                'current native provider/build binding differs']
            summary['incomplete_reasons'].extend(summary['rows']['positive']['incomplete_reasons'])
            save_partial()
            return summary
        summary['provider_record'] = provider_record
        if capture_loader is None:
            capture_loader = old.load_capture_runtime
        runtime = capture_loader(repo, cloud_dir, evidence)
        capture = runtime['capture'] if isinstance(runtime, dict) else runtime
        if source_loader is None:
            source_loader = old.load_source_writers
        source_view = old_root / 'source-repository'
        writers = source_loader(source_view)
        owner = writers['owner']
        positive_row = _positive_row_from_old(old, capture, evidence, old_summary,
                                               positive_source, old_root, owner, current_build)
        positive_row['provider_record'] = provider_record
        summary['rows']['positive'] = positive_row
        if not positive_row['complete']:
            summary['incomplete_reasons'].append('regenerated positive fingerprint row incomplete')
            save_partial()
            return summary
        if transform_loader is None:
            transform = load_negative_transform(repo)._negative_from_positive
        else:
            transform = transform_loader(repo)

        baseline_full = dict(old_summary['full_body_capture'])
        baseline_full['_positive_snapshots'] = old_summary['fingerprint']['snapshots']
        distinct_hashes = {positive_row['verified_sha256']}
        variant_roots = root / 'variants'
        variant_roots.mkdir()
        location_case = root / 'location-control'
        location_source = _copy_variant(location_case, original, positive_verified,
            positive_source, 'positive', transform, owner)
        location_row = _capture_one(old, capture, args, root, location_case, location_source,
                                    owner, 'positive-location-control', current_build)
        location_row['provider_record'] = provider_record
        location_row['case_path'] = location_case.relative_to(evidence).as_posix()
        try:
            location_row['artifact_inventory'] = _inventory(location_case, evidence, summary_path)
        except BaseException as exc:
            location_row['complete'] = False
            location_row['status'] = 'INCOMPLETE_SOURCE_REPORTED_FINGERPRINT'
            location_row['incomplete_reasons'].append('location artifact inventory failed: ' + type(exc).__name__)
        if location_row['complete']:
            try:
                _validate_snapshot_files(location_case, location_row['fingerprint'],
                                         pins['snapshots'], SNAPSHOT_NAMES)
                need(location_row['original_sha256'] == pins['source']['original_sha256'] and
                     location_row['verified_sha256'] == pins['source']['verified_sha256'],
                     'location-control source does not reproduce positive source pins')
                unchanged_errors = _fixed_body_unchanged(location_row, baseline_full)
                need(not unchanged_errors, '; '.join(unchanged_errors))
                location_row['reproduces_positive_pins'] = True
            except BaseException as exc:
                location_row['complete'] = False
                location_row['status'] = 'INCOMPLETE_SOURCE_REPORTED_FINGERPRINT'
                location_row['incomplete_reasons'].append('location positive pin mismatch: ' + type(exc).__name__)
        summary['location_control'] = location_row
        for variant in VARIANTS[1:]:
            case = variant_roots / variant
            source = _copy_variant(case, original, positive_verified, positive_source,
                                   variant, transform, owner)
            row = _capture_one(old, capture, args, root, case, source, owner, variant, current_build)
            row['provider_record'] = provider_record
            row['case_path'] = case.relative_to(evidence).as_posix()
            try:
                row['artifact_inventory'] = _inventory(case, evidence, summary_path)
            except BaseException as exc:
                row['complete'] = False
                row['status'] = 'INCOMPLETE_SOURCE_REPORTED_FINGERPRINT'
                row['incomplete_reasons'].append('row artifact inventory failed: ' + type(exc).__name__)
            if row['complete']:
                row['incomplete_reasons'].extend(_fixed_body_unchanged(row, baseline_full))
                if row['incomplete_reasons']:
                    row['complete'] = False
                    row['status'] = 'INCOMPLETE_SOURCE_REPORTED_FINGERPRINT'
            if row['complete']:
                distinct_hashes.add(row['verified_sha256'])
            summary['rows'][variant] = row
        rows_ok = (list(summary['rows']) == list(VARIANTS) and
                   all(row.get('complete') is True and
                       row.get('status') == 'COMPLETE_SOURCE_REPORTED_FINGERPRINT' and
                       row.get('native_build_id') == current_build and
                       row.get('source_unchanged') is True and
                       row.get('ghost_strip_identity') is True
                       for row in summary['rows'].values()) and
                   len(distinct_hashes) == len(VARIANTS))
        location_ok = (location_row.get('complete') is True and
                       location_row.get('reproduces_positive_pins') is True and
                       location_row.get('native_build_id') == current_build)
        if not rows_ok:
            summary['incomplete_reasons'].append('one or more matrix rows incomplete or source hashes not distinct')
        if not location_ok:
            summary['incomplete_reasons'].append('positive location-control did not reproduce b606 pins')
        summary['complete'] = rows_ok and location_ok
        if summary['complete']:
            summary['classification'] = 'SOURCE_REPORTED_MUTABLE_MATRIX_FINGERPRINT_ONLY'
        else:
            summary['classification'] = 'INCOMPLETE_MUTABLE_MATRIX_FINGERPRINT'
        save_partial()
        return summary
    except BaseException as exc:
        summary['complete'] = False
        summary['classification'] = 'INCOMPLETE_MUTABLE_MATRIX_FINGERPRINT'
        summary['incomplete_reasons'].append(type(exc).__name__ + ': ' + str(exc))
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
                 'compiler-sysroot', 'mode-file', 'matrix-mode-file'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--deadline-epoch', type=int, required=True)
    parser.add_argument('--mode-sha256', required=True)
    parser.add_argument('--matrix-mode-sha256', required=True)
    result = run(parser.parse_args())
    print(json.dumps({'classification': result['classification'],
                      'complete': result['complete'], 'body_proof_run': False,
                      'proof_credit': 0}, sort_keys=True), flush=True)
    if result.get('complete') is not True:
        raise SystemExit(4)


if __name__ == '__main__':
    main()
