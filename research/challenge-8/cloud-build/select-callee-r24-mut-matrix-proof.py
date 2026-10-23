#!/usr/bin/env python3
"""Collect all eight R24 mutable proof diagnostics without admission or credit."""
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

MODE_REL = Path('research/challenge-8/task-history/select-callee-r24/P2-MUT-MATRIX-PROOF-MODE.json')
MODE_SHA = '7870ea7c985914a1af049f685d62291bfe8d9768c0e4719c40422106d559fa94'
LIB_SHA = '8a481421396de618e50f8a6b7a408ffd9f048fd94397e647c3002e1489723d0c'
PINS_REL = Path('research/challenge-8/task-history/select-callee-r24/P2-MUT-MATRIX-PINS.json')
PINS_SHA = '5aee793196c2e0ab5960f1c0ea4aab8880ca68e61d74876363e2ccf3febadbed'
POSITIVE_REL = Path('research/challenge-8/task-history/select-callee-r24/P2-MUT-POSITIVE-EVIDENCE.json')
POSITIVE_SHA = '5b6f58485534622f66c246d37e17bd2f43cd2d2e2b020cc5c4c020d30374ee2a'
R24 = 'SORT4-ACTUAL-SELECT-2026-10-24-R24'
R21 = 'SORT4-ACTUAL-SELECT-2026-10-23-R21'
SUMMARY_REL = Path('cases/r24-mut-matrix-proof/MUT-MATRIX-PROOF.json')
ORIGINAL_PROOF_REL = Path('cases/r24-mut-proof/MUT-PROOF.json')
CONST_AUDIT_REL = Path('const-regression-audit.json')
PROFILE_REL = Path('profile-hashes.json')
SCHEMA = 'select-r24-mut-matrix-proof-v1'
NEGATIVE_SENTINEL = 'negative diagnostic acceptance is not pinned'
MARKER_PREFIX = 'SORT4-R24-MUTABLE-CERTIFICATES: case='
MARKER_SUFFIX = ' bodies=9 pointer_drop=1 assume_init=1; raw MIR cleanup retained'
SOURCE_TOOL_PATHS = (
    'bin/rust/std/lib.rsspec',
    'src/frontend/ocaml_expr_of_ast.ml',
    'src/rust_frontend/vf_mir/vf_mir.capnp',
    'src/rust_frontend/vf_mir_translator/rust_parser.ml',
    'src/rust_frontend/vf_mir_translator/vf_mir_translator.ml',
)
STABLE_TRANSPORT_TOOL_PATHS = ('bin/refinement-checker', 'bin/vf-rust-mir-exporter')
TRANSLATOR_PATH = 'src/rust_frontend/vf_mir_translator/vf_mir_translator.ml'
TRANSLATOR_SHA = '8a0260169bd2345070755e268edb640eaa4f02c261bef3330d7b33698e4ce007'


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def need(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError('R24-MUT-MATRIX-PROOF: ' + message)


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name('.' + path.name + '.tmp')
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    os.replace(tmp, path)


def load_library(cloud_dir: Path):
    path = cloud_dir / 'select-callee-r24-mut-proof.py'
    need(path.is_file() and not path.is_symlink() and digest(path.read_bytes()) == LIB_SHA,
         'frozen mutable proof library hash differs')
    spec = importlib.util.spec_from_file_location('r24_mut_matrix_proof_library', path)
    need(spec is not None and spec.loader is not None, 'proof library unavailable')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    need(digest(path.read_bytes()) == LIB_SHA, 'proof library changed during import')
    return module


def load_json_pin(repo: Path, rel: Path, expected_sha: str) -> dict[str, Any]:
    path = repo / rel
    need(path.is_file() and not path.is_symlink() and digest(path.read_bytes()) == expected_sha,
         'pinned JSON identity differs: ' + rel.as_posix())
    value = json.loads(path.read_text(encoding='utf-8'))
    need(isinstance(value, dict), 'pinned JSON is not an object: ' + rel.as_posix())
    return value


def validate_mode(repo: Path, path: Path, lib) -> dict[str, Any]:
    need(path.resolve() == (repo / MODE_REL).resolve() and path.is_file() and not path.is_symlink() and
         digest(path.read_bytes()) == MODE_SHA, 'exact matrix-proof mode path/hash required')
    mode = json.loads(path.read_text(encoding='utf-8'))
    expected = {
        'accepted': False, 'const_regression': 'FULL8_REQUIRED_SAME_TOOL',
        'diagnostic_only': True, 'enabled': True, 'independent_proof_credit': 0,
        'lane': lib.LANE, 'matrix_pins_file': PINS_REL.as_posix(),
        'matrix_pins_sha256': PINS_SHA, 'owner': 'select-sort4',
        'phase_id': R24, 'positive_evidence_file': POSITIVE_REL.as_posix(),
        'positive_evidence_sha256': POSITIVE_SHA, 'profile': lib.PROFILE,
        'proof_mode': 'all8', 'publication_allowed': False,
        'route_phase_id': R21, 'schema': 'select-r24-mut-matrix-proof-mode-v1',
        'targets_pinned': False, 'variant_order': list(lib.VARIANTS),
    }
    need(mode == expected, 'matrix-proof mode fields/bounds/order differ')
    return mode


def _positive_evidence(repo: Path) -> dict[str, Any]:
    record = load_json_pin(repo, POSITIVE_REL, POSITIVE_SHA)
    need(record.get('schema') == 'select-r24-mut-positive-proof-evidence-v1' and
         record.get('status') == 'CLEAN_POSITIVE_SOURCE_REPORTED_FULLMATRIX_PENDING' and
         record.get('assurance') == 'SOURCE_REPORTED' and
         record.get('accepted') is False and record.get('publication_allowed') is False and
         record.get('proof_credit') == 0 and record.get('candidate') == '993dd9e5dbd98332aa620e3a36a64040ed8d487f' and
         record.get('build_id') == 'cb6ab304-085f-41e3-9f0a-a5cd3d0a4147',
         'positive evidence schema/status/boundary differs')
    return record


def _tool_hashes(tool_home: Path, profile_path: Path, positive: dict[str, Any]) -> dict[str, str]:
    need(profile_path.is_file() and not profile_path.is_symlink(), 'current profile-hashes.json missing')
    profile = json.loads(profile_path.read_text(encoding='utf-8'))
    actual = profile.get('actual') if isinstance(profile, dict) else None
    source_claim = positive.get('actual_tool_hashes_source_claim')
    need(isinstance(actual, dict) and isinstance(source_claim, dict) and
         set(actual) == set(source_claim), 'actual tool/profile hash inventory differs')
    result: dict[str, str] = {}
    for rel, profile_hash in actual.items():
        need(isinstance(rel, str) and not Path(rel).is_absolute() and '..' not in Path(rel).parts and
             isinstance(profile_hash, str) and re.fullmatch(r'[0-9a-f]{64}', profile_hash),
             'current profile hash row malformed')
        path = tool_home / rel
        need(path.is_file() and not path.is_symlink(), 'profile tool artifact missing/symlinked: ' + rel)
        current = digest(path.read_bytes())
        need(current == profile_hash, 'profile hash does not match physical current tool: ' + rel)
        if rel in SOURCE_TOOL_PATHS or rel in STABLE_TRANSPORT_TOOL_PATHS:
            need(profile_hash == source_claim.get(rel), 'source/spec/exporter/parser/printer pin differs: ' + rel)
        result[rel] = current
    need(set(SOURCE_TOOL_PATHS) <= set(result) and
         result.get(TRANSLATOR_PATH) == TRANSLATOR_SHA,
         'required source tool pins or mutable translator identity differ')
    return result


def _safe_case(evidence: Path, row: dict[str, Any], variant: str) -> tuple[Path, list[str]]:
    errors: list[str] = []
    rel = row.get('case_path')
    if (not isinstance(rel, str) or Path(rel).is_absolute() or '..' in Path(rel).parts):
        return evidence, ['case path is not safe evidence-relative path']
    case = evidence / rel
    try:
        if not case.resolve().is_relative_to(evidence.resolve()):
            errors.append('case path escaped evidence root')
        cursor = evidence
        for part in Path(rel).parts:
            cursor = cursor / part
            if cursor.is_symlink():
                errors.append('case path contains symlink: ' + part)
                break
    except OSError:
        errors.append('case path could not be resolved')
    if case.is_symlink() or not case.is_dir(): errors.append('case directory missing/symlinked')
    return case, errors


def _source_pair(case: Path, expected: dict[str, str]) -> tuple[dict[str, str], list[str]]:
    hashes: dict[str, str] = {}
    errors: list[str] = []
    for rel in ('original/lib.rs', 'verified/lib.rs'):
        path = case / rel
        if not _regular_under(case, path):
            errors.append('source file missing/symlinked: ' + rel)
            continue
        h = digest(path.read_bytes())
        hashes[rel] = h
        if h != expected.get(rel): errors.append('source hash differs: ' + rel)
    return hashes, errors


def _regular_under(root: Path, path: Path) -> bool:
    try:
        resolved_root, resolved = root.resolve(), path.resolve()
        if not resolved.is_relative_to(resolved_root) or path.is_symlink() or not path.is_file():
            return False
        cursor = path.parent
        while cursor != root and cursor != cursor.parent:
            if cursor.is_symlink(): return False
            cursor = cursor.parent
        return not root.is_symlink()
    except OSError:
        return False


def _stage_logs(evidence: Path, case: Path, variant: str, stage: object) -> tuple[dict[str, Any], list[str], str]:
    errors: list[str] = []
    name = 'r24-mut-proof-' + variant + '.log'
    if not isinstance(stage, dict): return {}, ['stage result missing/wrong type'], ''
    if stage.get('stdout') != name or stage.get('stderr') != name:
        errors.append('proof stdout/stderr identity differs')
    path = case / name
    if not _regular_under(case, path):
        errors.append('proof log missing/symlinked')
        return {}, errors, ''
    try:
        raw = path.read_bytes()
        text = raw.decode('utf-8', errors='strict')
    except (OSError, UnicodeDecodeError):
        return {}, errors + ['proof log unreadable'], ''
    return {'path': (case / name).relative_to(evidence).as_posix(),
            'bytes': len(raw), 'sha256': digest(raw)}, errors, text


def _expected_stage_argv(stage: dict[str, Any], tool_home: Path) -> list[str]:
    return [str(tool_home / 'bin/verifast'), '-rustc_args', '--edition 2021',
            '-verbose', '1', 'verified/lib.rs']


def validate_rows(*, summary: object, evidence: Path, pins: dict[str, Any], lib,
                  tool_home: Path, expected_tool_hashes: dict[str, str],
                  native_id: str, candidate: str) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    rows_out: dict[str, Any] = {}
    if not isinstance(summary, dict): return {}, ['original mutable proof summary missing/wrong type']
    if (summary.get('schema') != lib.SCHEMA or summary.get('proof_mode') != 'all8' or
        summary.get('proof_variants') != list(lib.VARIANTS) or summary.get('native_build_id') != native_id or
        summary.get('candidate') != candidate):
        errors.append('original proof summary identity differs')
    # Revalidate the source/MIR capture, including each fixed snapshot and location control.
    capture = summary.get('complete_source_observation')
    errors.extend(lib._validate_capture(capture, pins, native_id))
    if (summary.get('accepted') is not False or summary.get('publication_allowed') is not False or
        type(summary.get('proof_credit')) is not int or summary.get('proof_credit') != 0 or
        summary.get('complete') is not False or
        summary.get('classification') != 'INCOMPLETE_MUTABLE_PROOF' or
        summary.get('body_proof_run') is not True or summary.get('typed_admission') is not False or
        ('semantic_rule_enabled' in summary and summary.get('semantic_rule_enabled') is not False)):
        errors.append('original proof summary boundary/completeness state differs')
    expected_pins_ref = {'path': lib.PINS_REL.as_posix(), 'sha256': lib.PINS_SHA256}
    if (summary.get('r24_session_phase_id') != R24 or summary.get('r21_route_phase_id') != R21 or
        summary.get('provider') != 'cloud-build' or summary.get('lane') != lib.LANE or
        summary.get('profile') != lib.PROFILE or summary.get('pins') != expected_pins_ref):
        errors.append('original proof summary route/provider/profile/pins context differs')
    if not isinstance(capture, dict):
        return {}, errors + ['source/MIR capture observation missing or wrong type']
    if isinstance(capture, dict):
        provider = capture.get('provider_record')
        if (not isinstance(provider, dict) or provider.get('provider') != 'cloud-build' or
            provider.get('build_id') != native_id or provider.get('project') != 'smallsort-ci' or
            provider.get('region') != 'global' or provider.get('os') != 'ubuntu-22.04' or
            provider.get('arch') != 'x86_64'):
            errors.append('capture native provider/current-build identity differs')
        if capture.get('r24_session_phase_id') != R24 or capture.get('r21_route_phase_id') != R21:
            errors.append('capture phase identities differ')
    capture_rows = capture.get('rows')
    if not isinstance(capture_rows, dict) or set(capture_rows) != set(lib.VARIANTS):
        return {}, errors + ['capture rows missing or not exact all8']
    recorded_rows = summary.get('rows')
    if not isinstance(recorded_rows, dict) or set(recorded_rows) != set(lib.VARIANTS):
        return {}, errors + ['proof row inventory is not exact all8']
    for variant in lib.VARIANTS:
        source_row = capture_rows.get(variant)
        row = recorded_rows[variant]
        case, row_errors = _safe_case(evidence, row, variant) if isinstance(row, dict) else (evidence, ['proof row missing/wrong type'])
        if not isinstance(row, dict):
            rows_out[variant] = {'variant': variant, 'classification': 'UNKNOWN_UNCLASSIFIED', 'errors': row_errors}
            errors.extend(f'{variant}: {x}' for x in row_errors)
            continue
        if row.get('variant') != variant or row.get('stage_name') != 'r24-mut-proof-' + variant:
            row_errors.append('proof stage row identity differs')
        if (not isinstance(source_row, dict) or not isinstance(source_row.get('case_path'), str) or
            row.get('case_path') != source_row.get('case_path')):
            row_errors.append('proof case path differs from current fingerprint row')
        expected_pair = {'original/lib.rs': pins['source']['original_sha256'],
                         'verified/lib.rs': pins['cases'][variant]['source']['verified_sha256']}
        source_before, before_errors = _source_pair(case, expected_pair)
        source_after, after_errors = _source_pair(case, expected_pair)
        row_errors.extend(before_errors + after_errors)
        stage = row.get('proof_stage')
        if not isinstance(stage, dict):
            row_errors.append('proof stage missing/wrong type')
            stage = {}
        if stage.get('status') != 'RAN': row_errors.append('proof stage status not RAN')
        if type(stage.get('exit')) is not int: row_errors.append('proof stage exit missing/wrong type')
        if stage.get('status') in ('TIMEOUT','TIMED_OUT') or stage.get('timeout') is True or stage.get('timed_out') is True or stage.get('exit') in (124,137):
            row_errors.append('proof stage timed out')
        if stage.get('source_unchanged') is not True or stage.get('source_before') != expected_pair or stage.get('source_after') != expected_pair:
            row_errors.append('proof stage source target mismatch')
        if row.get('source_before') != expected_pair or row.get('source_after') != expected_pair or row.get('source_intact') is not True:
            row_errors.append('runner source integrity record differs')
        if stage.get('intrinsic_gate_active') is not False or stage.get('pointer_drop_gate_active') is not False:
            row_errors.append('legacy proof gates were active')
        if stage.get('argv') != _expected_stage_argv(stage, tool_home):
            row_errors.append('actual verifier argv differs')
        log_identity, log_errors, log_text = _stage_logs(evidence, case, variant, stage)
        row_errors.extend(log_errors)
        marker = MARKER_PREFIX + variant + MARKER_SUFFIX
        marker_count = log_text.count(MARKER_PREFIX)
        native_count = log_text.splitlines().count(marker)
        if native_count != 1 or marker_count != 1:
            row_errors.append('exact native marker count/variant differs')
        if re.search(r'Fatal error:|TranslatorFailed', log_text, re.IGNORECASE):
            row_errors.append('proof log contains fatal/native translator failure')
        if stage.get('build_id') not in (None, native_id): row_errors.append('stage build UUID differs')
        # The current tool hashes are stable for the whole sequence; row records bind that sequence.
        classification = 'STAGE_RAN_TARGET_UNPINNED'
        if variant == 'positive':
            if stage.get('exit') != 0: row_errors.append('positive stage exit is not zero')
            if row.get('errors') != []: row_errors.append('positive library runner recorded errors')
            if (row.get('classification') != 'POSITIVE_PROOF_STAGE_RAN_SOURCE_INTACT' or
                row.get('native_marker_seen') != 1):
                row_errors.append('positive library classification/native marker record differs')
            if stage.get('error_count') not in (None, 0) or stage.get('additional_fatal') is True or \
                    stage.get('located_errors') not in (None, [], 0) or re.search(
                        r'(?m)^.*(?:Fatal error:|error:|Cannot prove|Assertion might not hold).*$', log_text):
                row_errors.append('positive stage reports error/fatal/located diagnostics')
            classification = 'POSITIVE_STAGE_RAN_SOURCE_REPORTED'
        else:
            if stage.get('exit') != 1: row_errors.append('negative stage did not refuse with exit 1')
            if row.get('classification') != 'UNKNOWN_UNCLASSIFIED' or row.get('errors') != [NEGATIVE_SENTINEL]:
                row_errors.append('negative result classification/errors are not conservative sentinel')
            classification = 'UNKNOWN_UNCLASSIFIED'
        row_out = {
            'variant': variant, 'case_path': row.get('case_path'),
            'native_build_id': native_id,
            'stage_name': row.get('stage_name'), 'stage_status': stage.get('status'),
            'stage_exit': stage.get('exit'), 'stage_source_before': stage.get('source_before'),
            'stage_source_after': stage.get('source_after'), 'source_before': source_before,
            'source_after': source_after, 'source_intact': source_before == source_after and not before_errors + after_errors,
            'original_stage_record': row.get('proof_stage'),
            'proof_stage_exception': row.get('proof_stage_exception'),
            'native_marker_count': native_count, 'log': log_identity,
            'tool_hashes': expected_tool_hashes, 'classification': classification,
            'targets_pinned': False, 'accepted': False, 'proof_credit': 0,
            'errors': row_errors,
        }
        rows_out[variant] = row_out
        errors.extend(f'{variant}: {item}' for item in row_errors)
    return rows_out, errors


def _validate_context(args, env: dict[str, str], lib) -> str:
    build = env.get('CLOUD_BUILD_ID')
    lib._validate_route(env, build, Path(args.repo))
    need(env.get('PROOF_SHA') == args.candidate and isinstance(args.candidate, str) and
         re.fullmatch(r'[0-9a-f]{40}', args.candidate) is not None,
         'candidate must be exact committed PROOF_SHA')
    return build


def run(args, *, lib=None, library_runner=None, pins_loader=None, positive_loader=_positive_evidence,
        env=None) -> dict[str, Any]:
    env = dict(os.environ if env is None else env)
    repo, evidence, tool_home = Path(args.repo).resolve(), Path(args.evidence).resolve(), Path(args.tool_home).resolve()
    args.repo, args.evidence, args.tool_home = repo, evidence, tool_home
    if lib is None: lib = load_library(Path(args.cloud_dir))
    build = _validate_context(args, env, lib)
    validate_mode(repo, Path(args.matrix_proof_mode_file), lib)
    pins = pins_loader(repo) if pins_loader else lib._load_pins(repo)
    positive = positive_loader(repo) if positive_loader is not _positive_evidence else positive_loader(repo)
    need(evidence.is_dir() and not evidence.is_symlink(), 'evidence root missing/symlinked')
    need((evidence / CONST_AUDIT_REL).is_file(), 'same-tool const regression audit missing')
    const_audit = json.loads((evidence / CONST_AUDIT_REL).read_text(encoding='utf-8'))
    need(isinstance(const_audit, dict) and const_audit.get('evidence_complete') is True and
         const_audit.get('runner_exit', 0) == 0,
         'same-tool full const regression audit is incomplete')
    profile_file = evidence / PROFILE_REL
    tool_hashes_before = _tool_hashes(tool_home, profile_file, positive)
    mode_obj = json.loads(Path(args.matrix_proof_mode_file).read_text(encoding='utf-8'))
    summary_path = evidence / SUMMARY_REL
    need(not summary_path.exists() and not summary_path.is_symlink(), 'fresh matrix proof output required')
    report: dict[str, Any] = {
        'schema': SCHEMA, 'classification': 'INCOMPLETE_MUTABLE_MATRIX_PROOF', 'complete': False,
        'candidate': args.candidate, 'native_build_id': build, 'r24_session_phase_id': R24,
        'r21_route_phase_id': R21, 'provider': env.get('SMALLSORT_EXECUTION_PROVIDER'),
        'lane': env.get('LANE'), 'profile': env.get('SORT4_SELECT_PROFILE'),
        'mode_ref': {'path': MODE_REL.as_posix(), 'sha256': MODE_SHA, 'mode': mode_obj},
        'matrix_pins_ref': {'path': PINS_REL.as_posix(), 'sha256': PINS_SHA},
        'positive_evidence_ref': {'path': POSITIVE_REL.as_posix(), 'sha256': POSITIVE_SHA},
        'original_mut_proof_ref': None, 'const_audit_ref': {'path': CONST_AUDIT_REL.as_posix(),
             'sha256': digest((evidence/CONST_AUDIT_REL).read_bytes())},
        'profile_hashes_ref': {'path': PROFILE_REL.as_posix(),
             'sha256': digest(profile_file.read_bytes())},
        'tool_hashes': tool_hashes_before, 'rows': {}, 'errors': [],
        'targets_pinned': False, 'accepted': False, 'proof_credit': 0,
        'publication_allowed': False, 'verification_accepted': False,
    }

    def save(error=None):
        if error is not None:
            report['exception'] = {'type': type(error).__name__, 'message': str(error),
                                   'traceback': traceback.format_exc()}
        # Preserve an inventory even on failure; never rewrite the library's proof JSON.
        inv = []
        for path in sorted(evidence.rglob('r24-mut-proof-*')):
            if path.is_file() and not path.is_symlink():
                raw = path.read_bytes()
                inv.append({'path': path.relative_to(evidence).as_posix(),
                            'bytes': len(raw), 'sha256': digest(raw)})
        original_path = evidence / ORIGINAL_PROOF_REL
        if (not report.get('original_mut_proof_ref') and original_path.is_file() and
                not original_path.is_symlink()):
            report['original_mut_proof_ref'] = {'path': ORIGINAL_PROOF_REL.as_posix(),
                'sha256': digest(original_path.read_bytes())}
        report['artifact_inventory'] = inv
        write_json(summary_path, report)

    try:
        if library_runner is None:
            args.proof_mode = 'all8'
            args.proof_variants = list(lib.VARIANTS)
            library_summary = lib.run(args)
        else:
            library_summary = library_runner(args, lib)
        original_path = evidence / lib.SUMMARY_REL
        if original_path.is_file() and not original_path.is_symlink():
            report['original_mut_proof_ref'] = {'path': lib.SUMMARY_REL.as_posix(),
                'sha256': digest(original_path.read_bytes())}
        else:
            report['errors'].append('original MUT-PROOF.json missing/symlinked')
        if pins.get('source') != positive.get('source'):
            report['errors'].append('positive evidence source pins differ from matrix pins')
        rows, validation_errors = validate_rows(summary=library_summary, evidence=evidence,
            pins=pins, lib=lib, tool_home=tool_home,
            expected_tool_hashes=tool_hashes_before, native_id=build, candidate=args.candidate)
        report['source_observation_ref'] = {'native_build_id': build,
            'classification': (library_summary.get('complete_source_observation') or {}).get('classification')
                if isinstance(library_summary, dict) else None}
        report['rows'] = rows
        report['errors'].extend(validation_errors)
        tool_hashes_after = _tool_hashes(tool_home, profile_file, positive)
        if tool_hashes_after != tool_hashes_before:
            report['errors'].append('tool/profile hashes changed during eight proof stages')
        report['tool_hashes_after'] = tool_hashes_after
        profile_sha_after = digest(profile_file.read_bytes())
        if profile_sha_after != report['profile_hashes_ref']['sha256']:
            report['errors'].append('profile-hashes.json changed during eight proof stages')
        report['profile_hashes_ref_after'] = {'path': PROFILE_REL.as_posix(), 'sha256': profile_sha_after}
        if not report['original_mut_proof_ref']:
            report['errors'].append('original proof JSON reference unavailable')
        report['complete'] = not report['errors'] and set(rows) == set(lib.VARIANTS)
        report['classification'] = 'COMPLETE_DIAGNOSTIC_COLLECTION_TARGETS_UNPINNED' if report['complete'] else 'INCOMPLETE_MUTABLE_MATRIX_PROOF'
        save()
        return report
    except BaseException as exc:
        report['errors'].append(type(exc).__name__ + ': ' + str(exc))
        report['classification'] = 'INCOMPLETE_MUTABLE_MATRIX_PROOF'
        try:
            save(exc)
        except BaseException as save_exc:
            if hasattr(exc, 'add_note'):
                exc.add_note('partial matrix-proof summary write failed: ' +
                             type(save_exc).__name__ + ': ' + str(save_exc))
        raise


def audit(args, *, lib=None, env=None) -> dict[str, Any]:
    env = dict(os.environ if env is None else env)
    args.repo = Path(args.repo).resolve()
    args.evidence = Path(args.evidence).resolve()
    if args.tool_home is not None: args.tool_home = Path(args.tool_home).resolve()
    if lib is None: lib = load_library(Path(args.cloud_dir))
    errors: list[str] = []
    audited_mode = None
    pins = None
    positive = None
    try:
        build = _validate_context(args, env, lib)
        audited_mode = validate_mode(Path(args.repo), Path(args.matrix_proof_mode_file), lib)
        pins = lib._load_pins(Path(args.repo))
        positive = _positive_evidence(Path(args.repo))
        need(isinstance(pins, dict) and isinstance(positive, dict),
             'matrix pins or positive evidence unavailable/wrong type')
    except BaseException as exc:
        build = env.get('CLOUD_BUILD_ID')
        errors.append(type(exc).__name__ + ': ' + str(exc))
        pins, positive = None, None
    report_path = Path(args.evidence) / SUMMARY_REL
    try: report = json.loads(report_path.read_text(encoding='utf-8'))
    except (OSError, ValueError): report = None
    if not isinstance(report, dict): errors.append('matrix proof summary missing/wrong type')
    else:
        if args.runner_exit != 0: errors.append('wrapper runner exit is nonzero')
        if args.failed_stage != 'complete': errors.append('wrapper failed-stage status is not complete')
        if (report.get('schema') != SCHEMA or report.get('complete') is not True or
            report.get('classification') != 'COMPLETE_DIAGNOSTIC_COLLECTION_TARGETS_UNPINNED' or
            report.get('candidate') != env.get('PROOF_SHA') or report.get('native_build_id') != build or
            report.get('proof_credit') != 0 or report.get('accepted') is not False or
            report.get('publication_allowed') is not False or report.get('targets_pinned') is not False or
            report.get('verification_accepted') is not False or report.get('errors') != []):
            errors.append('matrix proof summary identity/completeness/boundary differs')
        if (report.get('r24_session_phase_id') != R24 or report.get('r21_route_phase_id') != R21 or
            report.get('provider') != 'cloud-build' or report.get('lane') != lib.LANE or
            report.get('profile') != lib.PROFILE or
            report.get('matrix_pins_ref') != {'path': PINS_REL.as_posix(), 'sha256': PINS_SHA} or
            report.get('positive_evidence_ref') != {'path': POSITIVE_REL.as_posix(), 'sha256': POSITIVE_SHA} or
            not isinstance(report.get('mode_ref'), dict) or
            report['mode_ref'].get('path') != MODE_REL.as_posix() or
            report['mode_ref'].get('sha256') != MODE_SHA or
            report['mode_ref'].get('mode') != audited_mode):
            errors.append('matrix proof context or pinned references differ')
        ref = report.get('original_mut_proof_ref')
        original_path = Path(args.evidence) / ORIGINAL_PROOF_REL
        if (not isinstance(ref, dict) or ref.get('path') != ORIGINAL_PROOF_REL.as_posix() or
            not original_path.is_file() or original_path.is_symlink() or
            ref.get('sha256') != digest(original_path.read_bytes())):
            errors.append('original MUT-PROOF ref/hash changed or unavailable')
        if args.tool_home is None:
            errors.append('current tool home unavailable for audit')
        elif isinstance(pins, dict) and isinstance(positive, dict):
            original = None
            try: original = json.loads(original_path.read_text(encoding='utf-8'))
            except (OSError, ValueError): pass
            rows, row_errors = validate_rows(summary=original, evidence=Path(args.evidence), pins=pins,
                lib=lib, tool_home=Path(args.tool_home), expected_tool_hashes=report.get('tool_hashes', {}),
                native_id=build, candidate=env.get('PROOF_SHA'))
            errors.extend(row_errors)
            if rows != report.get('rows'): errors.append('fresh row/log/source recomputation differs from wrapper summary')
            try:
                current_hashes = _tool_hashes(Path(args.tool_home), Path(args.evidence)/PROFILE_REL, positive)
                if current_hashes != report.get('tool_hashes') or current_hashes != report.get('tool_hashes_after'):
                    errors.append('current same-tool inventory differs from wrapper stage inventory')
            except BaseException as exc: errors.append('tool inventory audit failed: ' + str(exc))
        const_path = Path(args.evidence) / CONST_AUDIT_REL
        try:
            const = json.loads(const_path.read_text(encoding='utf-8'))
            if not isinstance(const, dict) or const.get('evidence_complete') is not True or const.get('runner_exit', 0) != 0:
                errors.append('same-tool const regression audit incomplete')
            if report.get('const_audit_ref', {}).get('sha256') != digest(const_path.read_bytes()):
                errors.append('const audit reference hash differs')
        except (OSError, ValueError): errors.append('same-tool const regression audit missing/malformed')
        profile_path = Path(args.evidence) / PROFILE_REL
        try:
            if report.get('profile_hashes_ref', {}).get('sha256') != digest(profile_path.read_bytes()):
                errors.append('profile hash evidence reference differs')
            if report.get('profile_hashes_ref_after') != report.get('profile_hashes_ref'):
                errors.append('profile hash evidence changed during proof stages')
        except OSError: errors.append('profile hashes file missing')
    result = {'schema': 'select-r24-mut-matrix-proof-audit-v1',
        'scope': 'SOURCE_REPORTED_DIAGNOSTIC_COLLECTION_NO_TARGET_PINS_OR_ACCEPTANCE',
        'runner_exit': args.runner_exit, 'failed_stage': args.failed_stage,
        'evidence_complete': not errors, 'errors': errors,
        'matrix_proof_summary': report, 'verification_accepted': False,
        'accepted': False, 'publication_allowed': False, 'proof_credit': 0,
        'targets_pinned': False}
    output = Path(args.output)
    write_json(output, result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('run', 'audit'))
    for name in ('repo', 'cloud-dir', 'evidence', 'matrix-proof-mode-file'):
        parser.add_argument('--' + name, type=Path, required=True)
    for name in ('tool-home', 'schema', 'compiler-sysroot', 'mode-file', 'matrix-mode-file', 'output'):
        parser.add_argument('--' + name, type=Path)
    for name in ('mode-sha256', 'matrix-mode-sha256', 'candidate', 'failed-stage'):
        parser.add_argument('--' + name)
    parser.add_argument('--deadline-epoch', type=int)
    parser.add_argument('--runner-exit', type=int)
    args = parser.parse_args()
    lib = load_library(args.cloud_dir)
    if args.action == 'run':
        needed = ('tool_home', 'schema', 'compiler_sysroot', 'deadline_epoch', 'candidate')
        need(all(getattr(args, name) is not None for name in needed), 'run arguments incomplete')
        result = run(args, lib=lib)
        print(json.dumps({'complete': result['complete'], 'classification': result['classification'],
                          'targets_pinned': False, 'accepted': False, 'proof_credit': 0}, sort_keys=True))
        if result.get('complete') is not True: raise SystemExit(4)
    else:
        need(args.output is not None and args.runner_exit is not None and args.failed_stage is not None,
             'audit arguments incomplete')
        result = audit(args, lib=lib)
        print(json.dumps({'evidence_complete': result['evidence_complete'],
                          'verification_accepted': False, 'proof_credit': 0}, sort_keys=True))
        if result.get('evidence_complete') is not True: raise SystemExit(4)


if __name__ == '__main__':
    main()
