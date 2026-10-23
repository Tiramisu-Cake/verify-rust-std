#!/usr/bin/env python3
"""R24 source-reported classification of the seven exact mutable refusal controls."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import traceback
from typing import Any

DIAGNOSTIC_MODE_REL = Path('research/challenge-8/task-history/select-callee-r24/P2-MUT-MATRIX-PROOF-MODE.json')
DIAGNOSTIC_MODE_SHA = '7870ea7c985914a1af049f685d62291bfe8d9768c0e4719c40422106d559fa94'
TARGET_MAP_REL = Path('research/challenge-8/task-history/select-callee-r24/P2-MUT-CONTROL-TARGETS.json')
TARGET_MAP_SHA = 'b4cd8df6d8a38f43741c41f49fb9c991fd36e813586e3564435f6e65746a8b86'
TARGET_HELPER_REL = Path('research/challenge-8/cloud-build/select-callee-r24-mut-control-targets.py')
TARGET_HELPER_SHA = 'f5968c00c51c49b3c58299d7a747683d530a770104b256a9595eb504730c467f'
DIAGNOSTIC_WRAPPER_REL = Path('research/challenge-8/cloud-build/select-callee-r24-mut-matrix-proof.py')
DIAGNOSTIC_WRAPPER_SHA = 'f0907ded785ed659309277a497d8425f882dbd492da2d6c3e81cdc4b1088cbf8'
CLASSIFIED_MODE_REL = Path('research/challenge-8/task-history/select-callee-r24/P2-MUT-CLASSIFIED-PROOF-MODE.json')
CLASSIFIED_MODE_SHA = '3e17c17a993f01e8d136effd2ec3026f11825ef30793eb5178d9fe2f787131b7'
CLASSIFIED_SCHEMA = 'select-r24-mut-classified-proof-v1'
CLASSIFIED_AUDIT_SCHEMA = 'select-r24-mut-classified-proof-audit-v1'
R24 = 'SORT4-ACTUAL-SELECT-2026-10-24-R24'
R21 = 'SORT4-ACTUAL-SELECT-2026-10-23-R21'
POSITIVE = 'positive'
NEGATIVES = ('callee-false-normal', 'callee-owner-duplicate', 'callee-owner-loss',
             'callee-thread-duplicate', 'no-retained-half', 'omit-selected-own',
             'omit-unselected-own')
SUMMARY_REL = Path('cases/r24-mut-matrix-proof/MUT-CLASSIFIED-PROOF.json')
AUDIT_REL = Path('cases/r24-mut-matrix-proof/MUT-CLASSIFIED-PROOF-AUDIT.json')


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def need(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError('R24-MUT-CLASSIFIED-PROOF: ' + message)


def write_json(path: Path, record: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name('.' + path.name + '.tmp')
    temp.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    os.replace(temp, path)


def _load_pinned(path: Path, name: str, expected: str):
    need(path.is_file() and not path.is_symlink() and digest(path.read_bytes()) == expected,
         'pinned module hash differs: ' + path.name)
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, 'pinned module unavailable: ' + path.name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    need(digest(path.read_bytes()) == expected, 'pinned module changed while loading')
    return module


def load_services(cloud_dir: Path):
    diagnostic = _load_pinned(cloud_dir / DIAGNOSTIC_WRAPPER_REL.name,
        'r24_mut_classified_diagnostic_wrapper', DIAGNOSTIC_WRAPPER_SHA)
    target_validator = _load_pinned(cloud_dir / TARGET_HELPER_REL.name,
        'r24_mut_classified_control_targets', TARGET_HELPER_SHA)
    return diagnostic, target_validator


def _expected_classified_mode(lib, targets) -> dict[str, Any]:
    return {
        'accepted': False,
        'const_regression': 'FULL8_REQUIRED_SAME_TOOL',
        'diagnostic_mode_file': DIAGNOSTIC_MODE_REL.as_posix(),
        'diagnostic_mode_sha256': DIAGNOSTIC_MODE_SHA,
        'diagnostic_only': True,
        'enabled': True,
        'independent_proof_credit': 0,
        'lane': lib.LANE,
        'owner': 'select-sort4',
        'phase_id': R24,
        'profile': lib.PROFILE,
        'proof_mode': 'all8',
        'publication_allowed': False,
        'route_phase_id': R21,
        'schema': 'select-r24-mut-classified-proof-mode-v1',
        'target_map_file': TARGET_MAP_REL.as_posix(),
        'target_map_sha256': TARGET_MAP_SHA,
        'validator_file': TARGET_HELPER_REL.as_posix(),
        'validator_sha256': TARGET_HELPER_SHA,
        'frozen_wrapper_file': DIAGNOSTIC_WRAPPER_REL.as_posix(),
        'frozen_wrapper_sha256': DIAGNOSTIC_WRAPPER_SHA,
        'targets_pinned': True,
        'variant_order': [POSITIVE, *lib.VARIANTS[1:]],
    }


def validate_classified_mode(repo: Path, path: Path, lib, targets) -> dict[str, Any]:
    need(path.resolve() == (repo / CLASSIFIED_MODE_REL).resolve() and path.is_file() and
         not path.is_symlink() and
         digest(path.read_bytes()) == CLASSIFIED_MODE_SHA,
         'exact classified-proof mode file/path/hash required')
    mode = json.loads(path.read_text(encoding='utf-8'))
    expected = _expected_classified_mode(lib, targets)
    need(mode == expected, 'classified mode fields, identities, bounds, or order differ')
    return mode


def _read_regular(root: Path, rel: str) -> tuple[bytes, Path]:
    need(isinstance(rel, str) and not Path(rel).is_absolute() and '..' not in Path(rel).parts,
         'unsafe evidence-relative artifact path')
    path = root / rel
    try:
        need(path.resolve().is_relative_to(root.resolve()) and path.is_file() and
             not path.is_symlink(), 'artifact missing, symlinked, or outside evidence: ' + rel)
        cursor = path.parent
        while cursor != root and cursor != cursor.parent:
            need(not cursor.is_symlink(), 'artifact parent is symlinked: ' + rel)
            cursor = cursor.parent
    except OSError as exc:
        raise RuntimeError('R24-MUT-CLASSIFIED-PROOF: artifact cannot be resolved: ' + rel) from exc
    return path.read_bytes(), path


def _source_map(evidence: Path, pins: dict[str, Any], diag_report: dict[str, Any], diag):
    sources: dict[str, bytes] = {}
    paths: dict[str, str] = {}
    errors = []
    for variant in NEGATIVES:
        row = diag_report.get('rows', {}).get(variant)
        if not isinstance(row, dict):
            errors.append(variant + ': diagnostic row missing/wrong type')
            continue
        rel = row.get('case_path')
        if not isinstance(rel, str) or Path(rel).is_absolute() or '..' in Path(rel).parts:
            errors.append(variant + ': unsafe/missing case path')
            continue
        try:
            original, original_path = _read_regular(evidence, rel + '/original/lib.rs')
            verified, verified_path = _read_regular(evidence, rel + '/verified/lib.rs')
            expected_original = pins['source']['original_sha256']
            expected_verified = pins['cases'][variant]['source']['verified_sha256']
            if digest(original) != expected_original:
                errors.append(variant + ': physical original source hash differs from matrix pins')
            if digest(verified) != expected_verified:
                errors.append(variant + ': physical verified source hash differs from matrix pins')
            if row.get('source_before') != {'original/lib.rs': expected_original,
                                             'verified/lib.rs': expected_verified} or \
                    row.get('source_after') != row.get('source_before') or row.get('source_intact') is not True:
                errors.append(variant + ': diagnostic wrapper source observation differs')
            sources[variant] = verified
            paths[variant] = rel
        except BaseException as exc:
            errors.append(variant + ': source read failed: ' + type(exc).__name__ + ': ' + str(exc))
    return sources, paths, errors


def _classify_rows(*, evidence: Path, diag_report: dict[str, Any], pins: dict[str, Any],
                   target_map: dict[str, Any], diag, lib, target_validator,
                   tool_home: Path, build_id: str, candidate: str) -> tuple[dict[str, Any], dict[str, Any], list[str]]:
    errors: list[str] = []
    if not isinstance(diag_report, dict):
        return {}, {}, ['diagnostic matrix result missing/null/wrong type']
    if diag_report.get('complete') is not True or diag_report.get('classification') != \
            'COMPLETE_DIAGNOSTIC_COLLECTION_TARGETS_UNPINNED':
        return {}, {}, ['diagnostic matrix report is incomplete or already classified']
    diagnostic_rows = diag_report.get('rows')
    expected_all = list(lib.VARIANTS)
    if not isinstance(diagnostic_rows, dict) or set(diagnostic_rows) != set(expected_all):
        return {}, {}, ['diagnostic matrix row set differs from exact all8']
    if diag_report.get('native_build_id') != build_id:
        errors.append('diagnostic matrix Build ID differs from current Cloud Build')
    if diag_report.get('candidate') != candidate:
        errors.append('diagnostic matrix proof candidate differs from current PROOF_SHA')
    if (diag_report.get('targets_pinned') is not False or diag_report.get('accepted') is not False or
        diag_report.get('publication_allowed') is not False or diag_report.get('proof_credit') != 0):
        errors.append('diagnostic matrix boundary claims differ')
    if (diag_report.get('r24_session_phase_id') != R24 or diag_report.get('r21_route_phase_id') != R21 or
        diag_report.get('provider') != 'cloud-build' or diag_report.get('lane') != lib.LANE or
        diag_report.get('profile') != lib.PROFILE or
        diag_report.get('matrix_pins_ref') != {'path': lib.PINS_REL.as_posix(), 'sha256': lib.PINS_SHA256} or
        diag_report.get('positive_evidence_ref') != {'path': diag.POSITIVE_REL.as_posix(),
                                                     'sha256': diag.POSITIVE_SHA}):
        errors.append('diagnostic matrix current route/provider/profile/pins differs')
    sources, paths, source_errors = _source_map(evidence, pins, diag_report, diag)
    errors.extend(source_errors)
    spec_rel = 'bin/rust/std/lib.rsspec'
    spec_path = tool_home / spec_rel
    try:
        spec_bytes, _ = _read_regular(tool_home, spec_rel)
    except BaseException as exc:
        spec_bytes = b''
        errors.append('current tool spec unavailable: ' + type(exc).__name__ + ': ' + str(exc))
    tool_hashes = diag_report.get('tool_hashes')
    spec_hash = digest(spec_bytes)
    if not isinstance(tool_hashes, dict) or tool_hashes.get(spec_rel) != spec_hash:
        errors.append('current tool spec does not match same-tool profile hash')
    tool_spec_identity = str(spec_path.resolve())
    try:
        validated_map = target_validator.validate_target_map(
            target_map, sources, spec_bytes, tool_spec_file=tool_spec_identity,
            tool_home=tool_home)
    except BaseException as exc:
        validated_map = None
        errors.append('pinned target map validation failed: ' + type(exc).__name__ + ': ' + str(exc))
    classified: dict[str, Any] = {}
    positive_row = diagnostic_rows.get(POSITIVE)
    if isinstance(positive_row, dict):
        if (positive_row.get('classification') != 'POSITIVE_STAGE_RAN_SOURCE_REPORTED' or
            positive_row.get('stage_exit') != 0 or positive_row.get('source_intact') is not True or
            positive_row.get('errors') != [] or positive_row.get('native_marker_count') != 1):
            errors.append('positive current stage is not the clean source-reported row')
        classified[POSITIVE] = {
            'variant': POSITIVE,
            'classification': 'POSITIVE_STAGE_RAN_SOURCE_REPORTED',
            'diagnostic_row': positive_row,
            'targets_pinned': False,
            'accepted': False,
            'proof_credit': 0,
            'errors': [],
        }
    else:
        errors.append('positive diagnostic row missing/wrong type')

    for variant in NEGATIVES:
        row = diagnostic_rows.get(variant)
        row_errors: list[str] = []
        if not isinstance(row, dict):
            classified[variant] = {'variant': variant, 'classification': 'UNKNOWN_UNCLASSIFIED',
                                   'errors': ['diagnostic row missing/wrong type'], 'accepted': False,
                                   'proof_credit': 0, 'targets_pinned': False}
            errors.append(variant + ': diagnostic row missing/wrong type')
            continue
        case_rel = row.get('case_path')
        stage = row.get('original_stage_record')
        source_hashes = row.get('source_before')
        expected_pair = {'original/lib.rs': pins['source']['original_sha256'],
                         'verified/lib.rs': pins['cases'][variant]['source']['verified_sha256']}
        expected_log_rel = target_validator.CURRENT_LOG_RELATIVE.format(variant=variant)
        log_rel = case_rel + '/r24-mut-proof-' + variant + '.log' if isinstance(case_rel, str) else ''
        try:
            log_bytes, log_path = _read_regular(evidence, log_rel)
            log_text = log_bytes.decode('utf-8', errors='strict')
        except BaseException as exc:
            log_bytes, log_text, log_path = b'', '', evidence
            row_errors.append('current proof log missing/wrong type: ' + type(exc).__name__)
        if re.search(r'Fatal error:|TranslatorFailed', log_text, re.IGNORECASE):
            row_errors.append('current proof log contains fatal/native translator failure')
        observation = {
            'build_id': build_id,
            'variant': variant,
            'source_hashes': source_hashes,
            'tool_spec_sha256': spec_hash,
            'log_path': expected_log_rel,
            'log_sha256': digest(log_bytes),
            'stage': stage,
        }
        expected_argv = [str(tool_home / 'bin/verifast'), '-rustc_args', '--edition 2021',
                         '-verbose', '1', 'verified/lib.rs']
        if (row.get('source_before') != expected_pair or row.get('source_after') != expected_pair or
            row.get('source_intact') is not True or not isinstance(stage, dict) or
            stage.get('status') != 'RAN' or type(stage.get('exit')) is not int or
            stage.get('exit') != 1 or stage.get('source_unchanged') is not True or
            stage.get('source_before') != expected_pair or stage.get('source_after') != expected_pair or
            stage.get('intrinsic_gate_active') is not False or stage.get('pointer_drop_gate_active') is not False or
            stage.get('argv') != expected_argv or stage.get('stdout') != 'r24-mut-proof-' + variant + '.log' or
            stage.get('stderr') != 'r24-mut-proof-' + variant + '.log'):
            row_errors.append('negative stage source/exit/gates/argv/log identity differs')
        if validated_map is None:
            row_errors.append('validated target map unavailable')
            matched = None
        else:
            try:
                matched = target_validator.match_first_and_only_error(
                    variant, target_map, sources, spec_bytes, log_text,
                    log_bytes=log_bytes, log_observation=observation,
                    expected_build_id=build_id, tool_spec_file=tool_spec_identity,
                    tool_home=tool_home)
            except BaseException as exc:
                matched = None
                row_errors.append('current diagnostic failed exact target match: ' +
                                  type(exc).__name__ + ': ' + str(exc))
        if row.get('stage_exit') != 1 or row.get('stage_status') != 'RAN' or \
                row.get('source_intact') is not True or row.get('errors') != []:
            row_errors.append('negative diagnostic library row is not conservative expected refusal')
        log_record = row.get('log')
        if not isinstance(log_record, dict) or log_record.get('sha256') != digest(log_bytes) or log_record.get('path') != log_rel:
            row_errors.append('diagnostic matrix log inventory differs from physical log')
        if matched is not None and not row_errors:
            classified[variant] = {
                'variant': variant,
                'classification': 'NEGATIVE_SOLE_TARGET_MATCHED_SOURCE_REPORTED',
                'target_match': matched,
                'diagnostic_row': row,
                'targets_pinned': True,
                'accepted': False,
                'proof_credit': 0,
                'errors': row_errors,
            }
        else:
            classified[variant] = {'variant': variant, 'classification': 'UNKNOWN_UNCLASSIFIED',
                'target_match': matched, 'diagnostic_row': row, 'targets_pinned': False,
                'accepted': False, 'proof_credit': 0, 'errors': row_errors}
        errors.extend(f'{variant}: {item}' for item in row_errors)
    if validated_map is None: return classified, {}, errors
    return classified, validated_map, errors


def _context(args, env: dict[str, str], diag, lib, targets):
    build = env.get('CLOUD_BUILD_ID')
    diag._validate_context(args, env, lib)
    mode = validate_classified_mode(Path(args.repo), Path(args.classified_mode_file), lib, targets)
    diag.validate_mode(Path(args.repo), Path(args.matrix_proof_mode_file), lib)
    need(env.get('PROOF_SHA') == args.candidate, 'exact current PROOF_SHA candidate required')
    return build, mode


def _load_target_map(repo: Path):
    path = repo / TARGET_MAP_REL
    need(path.is_file() and not path.is_symlink() and digest(path.read_bytes()) == TARGET_MAP_SHA,
         'exact pinned target-map file/hash required')
    value = json.loads(path.read_text(encoding='utf-8'))
    need(isinstance(value, dict), 'target-map input is not an object')
    return value


def run(args, *, diag=None, targets=None, diagnostic_runner=None, env=None) -> dict[str, Any]:
    env = dict(os.environ if env is None else env)
    args.repo, args.evidence, args.tool_home = (Path(args.repo).resolve(),
        Path(args.evidence).resolve(), Path(args.tool_home).resolve())
    if diag is None or targets is None:
        loaded_diag, loaded_targets = load_services(Path(args.cloud_dir))
        diag = diag or loaded_diag
        targets = targets or loaded_targets
    lib = diag.load_library(Path(args.cloud_dir))
    build, mode = _context(args, env, diag, lib, targets)
    target_map = _load_target_map(Path(args.repo))
    need(Path(args.evidence).is_dir() and not Path(args.evidence).is_symlink(),
         'fresh evidence root missing/symlinked')
    output = Path(args.evidence) / SUMMARY_REL
    need(not output.exists() and not output.is_symlink(), 'fresh classified proof output required')
    report: dict[str, Any] = {
        'schema': CLASSIFIED_SCHEMA, 'classification': 'INCOMPLETE_CLASSIFIED_MUTABLE_PROOF',
        'complete': False, 'candidate': args.candidate, 'native_build_id': build,
        'r24_session_phase_id': R24, 'r21_route_phase_id': R21,
        'provider': env.get('SMALLSORT_EXECUTION_PROVIDER'), 'lane': env.get('LANE'),
        'profile': env.get('SORT4_SELECT_PROFILE'),
        'classified_mode_ref': {'path': CLASSIFIED_MODE_REL.as_posix(),
            'sha256': CLASSIFIED_MODE_SHA, 'mode': mode},
        'diagnostic_mode_ref': {'path': DIAGNOSTIC_MODE_REL.as_posix(),
            'sha256': DIAGNOSTIC_MODE_SHA},
        'target_map_ref': {'path': TARGET_MAP_REL.as_posix(), 'sha256': TARGET_MAP_SHA},
        'target_validator_ref': {'path': TARGET_HELPER_REL.as_posix(), 'sha256': TARGET_HELPER_SHA},
        'diagnostic_wrapper_ref': {'path': DIAGNOSTIC_WRAPPER_REL.as_posix(), 'sha256': DIAGNOSTIC_WRAPPER_SHA},
        'diagnostic_summary_ref': None, 'original_proof_summary_ref': None,
        'target_validation': None, 'rows': {}, 'errors': [],
        'targets_pinned': False, 'accepted': False, 'publication_allowed': False,
        'proof_credit': 0, 'verification_accepted': False,
    }

    def save(exc=None):
        if exc is not None:
            report['exception'] = {'type': type(exc).__name__, 'message': str(exc),
                                   'traceback': traceback.format_exc()}
        write_json(output, report)

    try:
        diagnostic = diagnostic_runner(args, diag, lib) if diagnostic_runner else diag.run(args, lib=lib)
        diag_path = Path(args.evidence) / diag.SUMMARY_REL
        proof_path = Path(args.evidence) / diag.ORIGINAL_PROOF_REL
        if diag_path.is_file() and not diag_path.is_symlink():
            report['diagnostic_summary_ref'] = {'path': diag.SUMMARY_REL.as_posix(),
                'sha256': digest(diag_path.read_bytes())}
        else:
            report['errors'].append('diagnostic summary missing/symlinked')
        if proof_path.is_file() and not proof_path.is_symlink():
            report['original_proof_summary_ref'] = {'path': diag.ORIGINAL_PROOF_REL.as_posix(),
                'sha256': digest(proof_path.read_bytes())}
        else:
            report['errors'].append('original mutable proof summary missing/symlinked')
        pins = lib._load_pins(Path(args.repo))
        rows, validated_map, classification_errors = _classify_rows(
            evidence=Path(args.evidence), diag_report=diagnostic, pins=pins,
            target_map=target_map, diag=diag, lib=lib, target_validator=targets,
            tool_home=Path(args.tool_home), build_id=build, candidate=args.candidate)
        report['rows'] = rows
        report['target_validation'] = validated_map or None
        report['errors'].extend(classification_errors)
        report['complete'] = (not report['errors'] and set(rows) == {POSITIVE, *NEGATIVES} and
                              all(row.get('errors') == [] for row in rows.values()))
        report['classification'] = ('COMPLETE_SOURCE_REPORTED_NEGATIVE_TARGET_CLASSIFICATION'
            if report['complete'] else 'INCOMPLETE_CLASSIFIED_MUTABLE_PROOF')
        report['targets_pinned'] = bool(report['complete'] and validated_map and
            all(rows[name].get('targets_pinned') is True for name in NEGATIVES))
        report['accepted'] = False
        report['publication_allowed'] = False
        report['proof_credit'] = 0
        report['verification_accepted'] = False
        save()
        return report
    except BaseException as exc:
        report['errors'].append(type(exc).__name__ + ': ' + str(exc))
        try: save(exc)
        except BaseException as save_exc:
            if hasattr(exc, 'add_note'):
                exc.add_note('partial classified-proof summary write failed: ' +
                    type(save_exc).__name__ + ': ' + str(save_exc))
        raise


def audit(args, *, diag=None, targets=None, env=None) -> dict[str, Any]:
    env = dict(os.environ if env is None else env)
    args.repo, args.evidence = Path(args.repo).resolve(), Path(args.evidence).resolve()
    if args.tool_home is not None: args.tool_home = Path(args.tool_home).resolve()
    if diag is None or targets is None:
        loaded_diag, loaded_targets = load_services(Path(args.cloud_dir))
        diag, targets = diag or loaded_diag, targets or loaded_targets
    lib = diag.load_library(Path(args.cloud_dir))
    errors: list[str] = []
    build = env.get('CLOUD_BUILD_ID')
    mode = None
    target_map = None
    pins = None
    try:
        build, mode = _context(args, env, diag, lib, targets)
        target_map = _load_target_map(Path(args.repo))
        pins = lib._load_pins(Path(args.repo))
    except BaseException as exc:
        errors.append(type(exc).__name__ + ': ' + str(exc))
    summary_path = Path(args.evidence) / SUMMARY_REL
    try: report = json.loads(summary_path.read_text(encoding='utf-8'))
    except (OSError, ValueError): report = None
    diag_audit = None
    # Re-run the frozen diagnostic root audit against physical artifacts. Use the final audit path
    # temporarily; this wrapper replaces it below with its own separate audit record.
    if args.tool_home is None:
        errors.append('current tool home unavailable for classified root audit')
    else:
        try:
            diag_audit = diag.audit(args, lib=lib, env=env)
            if not isinstance(diag_audit, dict) or diag_audit.get('evidence_complete') is not True:
                errors.append('underlying diagnostic root audit is incomplete')
        except BaseException as exc:
            errors.append('underlying diagnostic root audit raised: ' + type(exc).__name__ + ': ' + str(exc))
    if not isinstance(report, dict):
        errors.append('classified proof summary missing/wrong type')
    else:
        if (report.get('schema') != CLASSIFIED_SCHEMA or report.get('complete') is not True or
            report.get('classification') != 'COMPLETE_SOURCE_REPORTED_NEGATIVE_TARGET_CLASSIFICATION' or
            report.get('candidate') != env.get('PROOF_SHA') or report.get('native_build_id') != build or
            report.get('targets_pinned') is not True or report.get('accepted') is not False or
            report.get('publication_allowed') is not False or report.get('proof_credit') != 0 or
            report.get('verification_accepted') is not False or report.get('errors') != []):
            errors.append('classified summary identity/completeness/boundary differs')
        if (report.get('r24_session_phase_id') != R24 or report.get('r21_route_phase_id') != R21 or
            report.get('provider') != 'cloud-build' or report.get('lane') != lib.LANE or
            report.get('profile') != lib.PROFILE or report.get('classified_mode_ref') != {
                'path': CLASSIFIED_MODE_REL.as_posix(), 'sha256': CLASSIFIED_MODE_SHA, 'mode': mode} or
            report.get('target_map_ref') != {'path': TARGET_MAP_REL.as_posix(), 'sha256': TARGET_MAP_SHA}):
            errors.append('classified summary context/mode/target refs differ')
        if (target_map is not None and pins is not None and args.tool_home is not None):
            diag_path = Path(args.evidence) / diag.SUMMARY_REL
            proof_path = Path(args.evidence) / diag.ORIGINAL_PROOF_REL
            try:
                diag_report = json.loads(diag_path.read_text(encoding='utf-8'))
                rows, validated_map, row_errors = _classify_rows(
                    evidence=Path(args.evidence), diag_report=diag_report, pins=pins,
                    target_map=target_map, diag=diag, lib=lib, target_validator=targets,
                    tool_home=Path(args.tool_home), build_id=build, candidate=env.get('PROOF_SHA'))
                errors.extend(row_errors)
                if rows != report.get('rows') or validated_map != report.get('target_validation'):
                    errors.append('fresh classified rows/map differ from saved summary')
                for ref, path in ((report.get('diagnostic_summary_ref'), diag_path),
                                  (report.get('original_proof_summary_ref'), proof_path)):
                    if (not isinstance(ref, dict) or not path.is_file() or path.is_symlink() or
                        ref.get('sha256') != digest(path.read_bytes())):
                        errors.append('underlying diagnostic/source proof reference hash changed')
            except BaseException as exc:
                errors.append('classified physical audit failed: ' + type(exc).__name__ + ': ' + str(exc))
    result = {'schema': CLASSIFIED_AUDIT_SCHEMA,
        'scope': 'SOURCE_REPORTED_SEVEN_NEGATIVE_TARGET_MATCHES_NO_ACCEPTANCE',
        'runner_exit': args.runner_exit, 'failed_stage': args.failed_stage,
        'diagnostic_root_audit': diag_audit,
        'evidence_complete': not errors, 'errors': errors,
        'classified_summary': report,
        'verification_accepted': False, 'accepted': False,
        'publication_allowed': False, 'proof_credit': 0,
        'targets_pinned': False}
    write_json(Path(args.output), result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('run', 'audit'))
    for name in ('repo', 'cloud-dir', 'evidence', 'classified-mode-file', 'matrix-proof-mode-file'):
        parser.add_argument('--' + name, type=Path, required=True)
    for name in ('tool-home', 'schema', 'compiler-sysroot', 'mode-file', 'matrix-mode-file', 'output'):
        parser.add_argument('--' + name, type=Path)
    for name in ('mode-sha256', 'matrix-mode-sha256', 'candidate', 'failed-stage'):
        parser.add_argument('--' + name)
    parser.add_argument('--deadline-epoch', type=int)
    parser.add_argument('--runner-exit', type=int)
    args = parser.parse_args()
    diag, targets = load_services(args.cloud_dir)
    if args.action == 'run':
        need(all(getattr(args, n) is not None for n in ('tool_home','schema','compiler_sysroot',
             'deadline_epoch','candidate','mode_file','mode_sha256','matrix_mode_file','matrix_mode_sha256')),
             'classified proof run arguments incomplete')
        result = run(args, diag=diag, targets=targets)
        print(json.dumps({'complete': result['complete'], 'classification': result['classification'],
            'targets_pinned': result['targets_pinned'], 'accepted': False, 'proof_credit': 0}, sort_keys=True))
        if result.get('complete') is not True: raise SystemExit(4)
    else:
        need(args.output is not None and args.runner_exit is not None and args.failed_stage is not None,
             'classified audit arguments incomplete')
        result = audit(args, diag=diag, targets=targets)
        print(json.dumps({'evidence_complete': result['evidence_complete'],
            'verification_accepted': False, 'proof_credit': 0}, sort_keys=True))
        if result.get('evidence_complete') is not True: raise SystemExit(4)


if __name__ == '__main__':
    main()
