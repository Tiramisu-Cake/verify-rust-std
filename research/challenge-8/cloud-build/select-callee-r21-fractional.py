#!/usr/bin/env python3
"""R21 Cloud-only fractional-forget MIR/refusal fingerprints; no proof mode."""
from __future__ import annotations

import argparse
import difflib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback
from typing import Any, Callable

ROOT = Path('research/challenge-8')
TRANSFORM_REL = ROOT / 'overnight-assume-actual/r21_fractional_forget.py'
TRANSFORM_SHA256 = '8a23499c9852dfdc9973cca186daa83dcc2f7836642c40627ab1def6dd763772'
TRANSFORM_REPAIR_SHA256 = '3646b05602b7dce35cd4b2ab8f74d8cfe280d65df2637ac4f6cc0a128dd7e2a3'
TRANSFORM_CONTROLS_SHA256 = '533c3d9be5249a40b2f0ad701cfaff6e95e688ecfb5b9c024c5dd2a56dc5124d'
R20_HELPER_SHA256 = '83d2d0940fcb255a58b97db8d6161ec3b39660a62905f89a33f926a96d3099ba'
O26_RECIPE_SHA256 = '464eef45b08b8724eba949289eff9cd745f48d65d0031ffae5675738856d562c'
O26_REFRESH_SHA256 = '2cd963cc3d28c69370260cd2154e7284e189fea953928c3fc829f2fd53766af3'
CAPTURE_SHA256 = 'ffc3653263e86c5afa4f82440f10a2207e75ad8083bdad5f784597fe0dbaa84f'
R20_AUDIT_HELPER_SHA256 = '83d2d0940fcb255a58b97db8d6161ec3b39660a62905f89a33f926a96d3099ba'
BASE_VERIFIED_SHA256 = '1798132ff7a1585db7367779365c88e5ef5f417adcff0bf82779bf6a674945e6'
ORIGINAL_SHA256 = '466882d74de217766ed8d5c583596c173df47f0e6bd40da7cb1a4c931d7265a5'
CASE = 'nine-body-a1-owned-forget'
PHASE = 'SORT4-ACTUAL-SELECT-2026-10-23-R21'
PHASE_ENV = 'SORT4_R20_CALLEE_PHASE_ID'
R20_OPT_IN = 'SORT4_R20_FINAL_SELECT_REPAIR'
FRACTIONAL_PREFIX = 'SORT4_R21_FRACTIONAL'
STAGE_RESERVE_SECONDS = 150
VARIANTS = (
    'positive', 'omit-selected-own', 'omit-unselected-own', 'no-retained-half',
    'callee-false-normal', 'callee-owner-duplicate', 'callee-owner-loss',
    'callee-thread-duplicate',
)
EXPECTED_REFUSAL = 'INTENDED_DIAGNOSTIC_REFUSAL_NO_PROOF_RULE'


def sha(raw: bytes) -> str:
    import hashlib
    return hashlib.sha256(raw).hexdigest()


def need(ok: bool, why: str) -> None:
    if not ok:
        raise RuntimeError('R21-FRACTIONAL-FINGERPRINT: ' + why)


def write(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name('.' + path.name + '.tmp')
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n')
    os.replace(tmp, path)


def load(path: Path, name: str, expected: str | None = None):
    if expected is not None:
        need(path.is_file() and sha(path.read_bytes()) == expected,
             'pinned module differs: ' + str(path))
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None,
         'module spec unavailable: ' + str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    if expected is not None:
        need(sha(path.read_bytes()) == expected,
             'module changed during import: ' + str(path))
    return module


def require_cloud(env: dict[str, str]) -> None:
    need(env.get('SMALLSORT_EXECUTION_PROVIDER') == 'cloud-build' and
         env.get(PHASE_ENV) == PHASE and not env.get('GITHUB_ACTIONS'),
         'fresh R21 Cloud callee phase required')
    need(R20_OPT_IN not in env and
         not any(key.startswith(FRACTIONAL_PREFIX) for key in env),
         'ambient R20/R21 fractional semantic opt-in refused')


def _derive_o26_guard_overlay(committed: bytes, rel: str, o26) -> bytes:
    """Recompute exactly the guard-only byte rewrite used by o26.overlay."""
    try:
        before = committed.decode('utf-8')
    except UnicodeDecodeError as exc:
        raise RuntimeError('R21-FRACTIONAL-FINGERPRINT: committed overlay source is not UTF-8: ' + rel) from exc
    guards = [guard for guard in o26.GUARD_VARIANTS if before.count(guard) == 1]
    need(len(guards) == 1, 'committed provider guard is absent or ambiguous: ' + rel)
    after = before.replace(guards[0], '_o26_cloud_provider_ok()', 1)
    anchor = 'from pathlib import Path\n'
    need(after.count(anchor) == 1 and 'import importlib.util' in after,
         'provider overlay insertion anchors differ: ' + rel)
    after = after.replace(anchor, anchor + o26.HELPER, 1)
    try:
        compile(after, rel, 'exec')
    except SyntaxError as exc:
        raise RuntimeError('R21-FRACTIONAL-FINGERPRINT: recomputed provider overlay fails syntax: ' + rel) from exc
    return after.encode('utf-8')


def validate_o26_provider_overlay(repo: Path, cloud_dir: Path, evidence: Path,
                                  o26, *, expected_source_sha256: str,
                                  expected_original_sha256: str,
                                  committed_reader: Callable | None = None
                                  ) -> dict[str, Any]:
    """Bind O26's provider receipt and preflight to committed and current bytes."""
    receipt_path = evidence / 'candidate-provider-overlay.json'
    need(receipt_path.is_file(), 'O26 provider overlay receipt is missing')
    try:
        receipt = json.loads(receipt_path.read_text())
    except (OSError, ValueError) as exc:
        raise RuntimeError('R21-FRACTIONAL-FINGERPRINT: provider overlay receipt is unreadable') from exc
    need(isinstance(receipt, dict), 'O26 provider overlay receipt has wrong type')
    provider_path = cloud_dir / 'provider.py'
    need(provider_path.is_file() and sha(provider_path.read_bytes()) == o26.PROVIDER_SHA and
         receipt.get('provider_sha256') == o26.PROVIDER_SHA,
         'O26 provider module receipt pin differs')
    need(receipt.get('proof_sha') == o26.git_sha(repo),
         'provider receipt proof checkout identity differs')
    expected_paths = [path.as_posix() for path in o26.OVERLAYS]
    rows = receipt.get('files')
    need(isinstance(rows, list) and [row.get('path') if isinstance(row, dict) else None
         for row in rows] == expected_paths,
         'provider receipt overlay file inventory differs')

    if committed_reader is None:
        def committed_reader(path: Path) -> bytes:
            return subprocess.check_output(['git', '-C', str(repo), 'show',
                                             'HEAD:' + path.as_posix()])

    capture_rel = ROOT / 'overnight-assume-actual/capture.py'
    validated = []
    for rel_path, entry in zip(o26.OVERLAYS, rows):
        rel = rel_path.as_posix()
        expected_keys = {'path', 'original_sha256', 'cloud_overlay_sha256',
                         'guard_only', 'diff'}
        need(set(entry) == expected_keys and entry.get('guard_only') is True,
             'provider receipt row malformed or not guard-only: ' + rel)
        committed = committed_reader(rel_path)
        need(sha(committed) == entry.get('original_sha256'),
             'committed provider-overlay source hash differs: ' + rel)
        if rel_path == capture_rel:
            need(sha(committed) == CAPTURE_SHA256,
                 'committed mode-9 capture source pin differs')
        expected_bytes = _derive_o26_guard_overlay(committed, rel, o26)
        current_path = repo / rel_path
        need(current_path.is_file(), 'overlaid source file is missing: ' + rel)
        current = current_path.read_bytes()
        need(current == expected_bytes and
             sha(current) == entry.get('cloud_overlay_sha256'),
             'current source differs from exact O26 guard overlay: ' + rel)
        before_text = committed.decode('utf-8')
        after_text = expected_bytes.decode('utf-8')
        expected_diff = ''.join(difflib.unified_diff(
            before_text.splitlines(True), after_text.splitlines(True),
            fromfile=rel + '.committed', tofile=rel + '.cloud-guard'))
        need(entry.get('diff') == expected_diff,
             'provider overlay receipt diff differs from recomputed guard rewrite: ' + rel)
        validated.append({'path': rel, 'original_sha256': sha(committed),
                          'cloud_overlay_sha256': sha(current), 'guard_only': True})

    preflight_path = evidence / 'source-preflight.json'
    need(preflight_path.is_file(), 'O26 source-only preflight receipt is missing')
    try:
        preflight = json.loads(preflight_path.read_text())
    except (OSError, ValueError) as exc:
        raise RuntimeError('R21-FRACTIONAL-FINGERPRINT: source preflight receipt is unreadable') from exc
    need(isinstance(preflight, dict), 'O26 source preflight receipt has wrong type')
    source = preflight.get('source')
    expected_source = {'original_sha256': expected_original_sha256,
                       'verified_sha256': expected_source_sha256}
    need(isinstance(source, dict) and
         preflight.get('classification') == 'O26_REFRESH_SOURCE_ONLY_PREFLIGHT' and
         preflight.get('source_generation_complete') is True and
         preflight.get('compiler_or_verifier_invoked') is False and
         source.get('ghost_strip_identity') is True and
         isinstance(source.get('source_order'), list) and len(source['source_order']) == 9 and
         len(set(source['source_order'])) == 9,
         'O26 source-only preflight receipt is incomplete or malformed')
    need(_is_digest(expected_source['original_sha256']) and
         _is_digest(expected_source['verified_sha256']) and
         source.get('original_sha256') == expected_source['original_sha256'] and
         source.get('verified_sha256') == expected_source['verified_sha256'],
         'O26 source preflight source hashes malformed')
    files = preflight.get('files')
    need(isinstance(files, dict) and set(files) == {'original', 'verified'},
         'O26 source preflight file inventory differs')
    for key, digest in expected_source.items():
        label = key.removesuffix('_sha256')
        relative = Path(files[label]) if isinstance(files[label], str) else Path('/')
        need(not relative.is_absolute() and '..' not in relative.parts,
             'O26 source preflight file path escapes evidence root: ' + label)
        path = evidence / relative
        need(path.is_file() and sha(path.read_bytes()) == digest,
             'O26 preflight source bytes differ: ' + key)
    return {'overlay_receipt_sha256': sha(receipt_path.read_bytes()),
            'preflight_receipt_sha256': sha(preflight_path.read_bytes()),
            'files': validated, 'source': expected_source}


def _is_digest(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        char in '0123456789abcdef' for char in value)


def pinned_dependencies(repo: Path, cloud_dir: Path, evidence: Path | None = None):
    transform = load(repo / TRANSFORM_REL, 'r21_fractional_transform', TRANSFORM_SHA256)
    need(getattr(transform, 'PINNED_REPAIR_SHA256', None) == TRANSFORM_REPAIR_SHA256 and
         getattr(transform, 'PINNED_CONTROLS_SHA256', None) == TRANSFORM_CONTROLS_SHA256 and
         getattr(transform, 'BASELINE_SHA256_PREFIX', None) == BASE_VERIFIED_SHA256[:8] and
         tuple(getattr(transform, 'VARIANTS', ())) == VARIANTS,
         'fractional transform core pins or variant inventory differ')
    r20 = load(cloud_dir / 'select-callee-r20.py', 'r21_fractional_r20', R20_HELPER_SHA256)
    o26 = load(cloud_dir / 'o26-recipe.py', 'r21_fractional_o26', O26_RECIPE_SHA256)
    refresh = load(cloud_dir / 'o26-refresh-recipe.py', 'r21_fractional_refresh', O26_REFRESH_SHA256)
    need(evidence is not None, 'O26 evidence directory is required for overlay binding')
    need(isinstance(getattr(refresh, 'UNIT', None), str) and
         isinstance(getattr(refresh, 'BODIES', None), (list, tuple)) and
         len(refresh.BODIES) == 9 and all(isinstance(x, str) for x in refresh.BODIES),
         'O26 default snapshot pin inventory malformed')
    validate_o26_provider_overlay(repo, cloud_dir, evidence, o26,
        expected_source_sha256=refresh.SOURCE,
        expected_original_sha256=refresh.ORIGINAL)
    return transform, r20, o26, refresh


def snapshot_pins(refresh) -> dict[str, str]:
    return {'unit': refresh.UNIT,
            **{f'body-{index}': digest for index, digest in enumerate(refresh.BODIES)}}


def validate_export_decode(rows: object, output_root: Path) -> dict[str, Any]:
    errors = []
    complete = True
    if not isinstance(rows, dict):
        return {'complete': False, 'errors': ['export_decode result is not an object'],
                'returned': rows}
    result: dict[str, Any] = {'complete': False, 'errors': errors, 'returned': rows}
    for stage_name, expected_name in (('export', 'normal-mir.bin'),
                                      ('decode', 'normal-mir.txt')):
        stage = rows.get(stage_name)
        if not isinstance(stage, dict):
            errors.append(stage_name + ': missing or wrong-type stage')
            complete = False
            continue
        if stage.get('status') != 'RAN' or type(stage.get('exit')) is not int:
            errors.append(stage_name + ': not a terminal RAN stage')
            complete = False
            continue
        if stage['exit'] != 0:
            errors.append(stage_name + ': nonzero stage exit')
            complete = False
            continue
        output_name = stage.get('output')
        output_sha = stage.get('output_sha256')
        if (output_name != expected_name or not isinstance(output_sha, str) or
                len(output_sha) != 64):
            errors.append(stage_name + ': output identity malformed')
            complete = False
            continue
        path = output_root / output_name
        if (not path.is_file() or path.stat().st_size == 0 or
                sha(path.read_bytes()) != output_sha):
            errors.append(stage_name + ': output bytes differ from stage record')
            complete = False
    result['complete'] = complete and not errors
    return result


def fingerprint_argv(tool_home: Path) -> list[str]:
    return [str(tool_home / 'bin/verifast'), '-rustc_args',
            '--edition 2021', '-verbose', '1', 'verified/lib.rs']


def validate_fingerprint(result: object, case: Path,
                         source_hashes: dict[str, str],
                         pins: dict[str, str], expected_argv: list[str]
                         ) -> dict[str, Any]:
    errors: list[str] = []
    complete = True
    if not isinstance(result, dict):
        return {'complete': False, 'errors': ['fingerprint result is not an object'],
                'returned': result, 'source_stage_match': False,
                'snapshots_match': False}
    stage = result.get('stage')
    if not isinstance(stage, dict):
        errors.append('fingerprint stage missing or wrong type')
        complete = False
        stage_match = False
    else:
        if stage.get('status') != 'RAN' or type(stage.get('exit')) is not int:
            errors.append('fingerprint stage not terminal RAN')
            complete = False
        if (stage.get('source_before') != source_hashes or
                stage.get('source_after') != source_hashes or
                stage.get('source_unchanged') is not True):
            errors.append('fingerprint source-stage-target mismatch')
            complete = False
            stage_match = False
        else:
            stage_match = True
        if stage.get('exit') != 2:
            errors.append('fingerprint exit is not the expected diagnostic refusal (2)')
            complete = False
        if stage.get('argv') != expected_argv:
            errors.append('fingerprint verifier argv/target differs')
            complete = False
        if (stage.get('stdout') != 'nine-body-fingerprint-refusal.log' or
                stage.get('stderr') != 'nine-body-fingerprint-refusal.log'):
            errors.append('fingerprint stdout/stderr target differs')
            complete = False
        if stage.get('intrinsic_gate_active') is not False or \
                stage.get('pointer_drop_gate_active') is not False:
            errors.append('fingerprint semantic gates were not disabled')
            complete = False
    if result.get('body_proof_run') is not False:
        errors.append('body proof was not explicitly marked NOT_RUN')
        complete = False
    if not isinstance(result.get('classification'), str):
        errors.append('fingerprint classification missing or wrong type')
        complete = False
    snapshots = result.get('snapshots')
    snapshots_match = isinstance(snapshots, dict) and set(snapshots) == set(pins)
    if not snapshots_match:
        errors.append('fingerprint snapshot key inventory differs')
        complete = False
    if isinstance(snapshots, dict):
        for label, expected_sha in pins.items():
            row = snapshots.get(label)
            if not isinstance(row, dict):
                errors.append(label + ': snapshot row missing or wrong type')
                complete = False
                snapshots_match = False
                continue
            filename, byte_count, actual_sha = row.get('file'), row.get('bytes'), row.get('sha256')
            if (not isinstance(filename, str) or Path(filename).name != filename or
                    type(byte_count) is not int or byte_count <= 0 or
                    not isinstance(actual_sha, str) or len(actual_sha) != 64):
                errors.append(label + ': malformed snapshot row')
                complete = False
                snapshots_match = False
                continue
            path = case / filename
            if (not path.is_file() or path.stat().st_size != byte_count or
                    sha(path.read_bytes()) != actual_sha):
                errors.append(label + ': snapshot bytes differ from record')
                complete = False
                snapshots_match = False
                continue
            if actual_sha != expected_sha:
                snapshots_match = False
    if result.get('all_ten_snapshots') is not True:
        errors.append('capture did not attest all ten snapshots')
        complete = False
    if result.get('expected_refusal_seen') is not True or \
            result.get('classification') != EXPECTED_REFUSAL:
        errors.append('existing intended diagnostic refusal was not observed')
        complete = False
    return {'complete': complete and not errors,
            'errors': errors,
            'classification': result.get('classification'),
            'stage': stage,
            'source_stage_match': stage_match,
            'snapshots_match_default_pins': snapshots_match,
            'body_proof_run': False,
            'returned': result}


def _snapshot_copy(original: bytes, verified: bytes, case: Path) -> None:
    (case / 'original').mkdir(parents=True)
    (case / 'verified').mkdir()
    (case / 'original/lib.rs').write_bytes(original)
    (case / 'verified/lib.rs').write_bytes(verified)


def _checkpoint(path: Path, record: dict[str, Any]) -> None:
    record['complete'] = False
    record['accepted'] = False
    record['proof_credit'] = False
    record['body_proof_run'] = False
    write(path, record)


def fingerprint_batch(a, *, transform, export_decode: Callable,
                      cap, refresh, env: dict[str, str],
                      dependencies: dict[str, str] | None = None) -> dict[str, Any]:
    """Run eight source fingerprints under injectable stage dependencies."""
    require_cloud(env)
    need(a.deadline_epoch > int(time.time()), 'shared deadline has elapsed')
    pins = snapshot_pins(refresh)
    need(set(pins) == {'unit', *(f'body-{i}' for i in range(9))} and
         all(isinstance(value, str) and len(value) == 64 for value in pins.values()),
         'baseline unit/body snapshot pins malformed')
    base = Path(a.evidence) / 'cases/candidate/capture' / CASE
    source_original = base / 'original/lib.rs'
    source_verified = base / 'verified/lib.rs'
    need(source_original.is_file() and source_verified.is_file(),
         'captured candidate nine-body source is missing')
    original = source_original.read_bytes()
    verified = source_verified.read_bytes()
    need(sha(original) == ORIGINAL_SHA256 and sha(verified) == BASE_VERIFIED_SHA256,
         'owner-projection base source identities differ')

    root = Path(a.evidence) / 'cases/r21-fractional-fingerprint'
    root.mkdir(parents=True, exist_ok=False)
    record: dict[str, Any] = {
        'schema': 'r21-fractional-forget-fingerprint-v1',
        'classification': 'R21_FRACTIONAL_FINGERPRINT_ONLY',
        'mode': 'fingerprint', 'complete': False,
        'base_source': {'original_sha256': ORIGINAL_SHA256,
                        'verified_sha256': BASE_VERIFIED_SHA256,
                        'base_verified_file': 'base/' + CASE + '/verified/lib.rs'},
        'snapshot_pins': pins, 'variants': {},
        'variant_order': list(VARIANTS),
        'dependencies': dependencies or {},
        'accepted': False, 'proof_credit': False, 'body_proof_run': False,
    }
    _snapshot_copy(original, verified, root / 'base' / CASE)
    base_original = root / 'base' / CASE / 'original/lib.rs'
    base_verified = root / 'base' / CASE / 'verified/lib.rs'
    record_path = root / 'r21-fractional-fingerprint.json'
    _checkpoint(record_path, record)

    def save() -> None:
        _checkpoint(record_path, record)

    cap.clear_semantic_opt_ins()
    control_case = root / 'location-control' / CASE
    _snapshot_copy(original, verified, control_case)
    control_row: dict[str, Any] = {
        'original_sha256': ORIGINAL_SHA256,
        'verified_sha256': BASE_VERIFIED_SHA256,
        'status': 'PENDING',
    }
    record['location_control'] = control_row
    save()
    try:
        if a.deadline_epoch - int(time.time()) < STAGE_RESERVE_SECONDS:
            control_row.update(status='NOT_RUN', reason='shared deadline reserve',
                               fingerprint={'status': 'NOT_RUN'})
            save()
            raise SystemExit(3)
        try:
            default_result = cap.refusal_fingerprint(
                control_case, {'verified_sha256': BASE_VERIFIED_SHA256}, a)
            control_check = validate_fingerprint(default_result, control_case,
                {'original/lib.rs': ORIGINAL_SHA256,
                 'verified/lib.rs': BASE_VERIFIED_SHA256}, pins,
                fingerprint_argv(a.tool_home))
            control_row.update(status='RAN', fingerprint_check=control_check,
                               fingerprint=default_result,
                               reproduces_pinned=(control_check['complete'] and
                                   control_check['snapshots_match_default_pins']))
            control_row['source_intact_after_stages'] = (
                (control_case / 'original/lib.rs').is_file() and
                (control_case / 'verified/lib.rs').is_file() and
                sha((control_case / 'original/lib.rs').read_bytes()) == ORIGINAL_SHA256 and
                sha((control_case / 'verified/lib.rs').read_bytes()) == BASE_VERIFIED_SHA256)
        except BaseException as exc:
            control_row.update(status='EXCEPTION', exception_type=type(exc).__name__,
                               exception=str(exc), traceback=traceback.format_exc())
            save()
            raise
        finally:
            cap.clear_semantic_opt_ins()
        save()

        for variant in VARIANTS:
            case_root = root / 'variants' / variant
            case = case_root / CASE
            row: dict[str, Any] = {'status': 'PENDING', 'variant': variant}
            record['variants'][variant] = row
            save()
            try:
                candidate = transform(verified, variant)
                need(isinstance(candidate, bytes), 'transform returned non-bytes for ' + variant)
                _snapshot_copy(original, candidate, case)
                row.update(status='PREPARED', original_sha256=sha(original),
                           base_verified_sha256=sha(verified),
                           verified_sha256=sha(candidate),
                           original_preserved=(sha((case / 'original/lib.rs').read_bytes()) == ORIGINAL_SHA256))
                save()
                if a.deadline_epoch - int(time.time()) < STAGE_RESERVE_SECONDS:
                    row.update(status='NOT_RUN', reason='shared deadline reserve',
                               normal_mir={'status': 'NOT_RUN', 'reason': 'shared deadline reserve'},
                               fingerprint={'status': 'NOT_RUN', 'reason': 'shared deadline reserve'})
                    save()
                    continue

                mir_root = case_root / 'normal-mir'
                try:
                    mir = export_decode(case, mir_root, a)
                    mir_check = validate_export_decode(mir, mir_root)
                    row.update(normal_mir=mir, normal_mir_check=mir_check)
                except BaseException as exc:
                    row.update(normal_mir={'status': 'EXCEPTION'},
                               normal_mir_exception_type=type(exc).__name__,
                               normal_mir_exception=str(exc),
                               normal_mir_traceback=traceback.format_exc())
                    save()
                    raise
                save()

                if a.deadline_epoch - int(time.time()) < STAGE_RESERVE_SECONDS:
                    row.update(fingerprint={'status': 'NOT_RUN',
                                            'reason': 'shared deadline reserve'})
                    row['status'] = 'INCOMPLETE'
                    save()
                    continue
                cap.clear_semantic_opt_ins()
                try:
                    result = cap.refusal_fingerprint(
                        case, {'verified_sha256': row['verified_sha256']}, a)
                    fp_check = validate_fingerprint(result, case,
                        {'original/lib.rs': ORIGINAL_SHA256,
                         'verified/lib.rs': row['verified_sha256']}, pins,
                        fingerprint_argv(a.tool_home))
                    row.update(fingerprint=result, fingerprint_check=fp_check)
                except BaseException as exc:
                    row.update(fingerprint={'status': 'EXCEPTION'},
                               fingerprint_exception_type=type(exc).__name__,
                               fingerprint_exception=str(exc),
                               fingerprint_traceback=traceback.format_exc())
                    save()
                    raise
                finally:
                    cap.clear_semantic_opt_ins()

                source_intact = (
                    (case / 'original/lib.rs').is_file() and
                    (case / 'verified/lib.rs').is_file() and
                    sha((case / 'original/lib.rs').read_bytes()) == ORIGINAL_SHA256 and
                    sha((case / 'verified/lib.rs').read_bytes()) == row['verified_sha256'])
                row['source_intact_after_stages'] = source_intact
                row['status'] = ('COMPLETE' if source_intact and
                                 row.get('normal_mir_check', {}).get('complete') is True and
                                 row.get('fingerprint_check', {}).get('complete') is True
                                 else 'INCOMPLETE')
                save()
            except BaseException as exc:
                row.update(status='EXCEPTION', exception_type=type(exc).__name__,
                           exception=str(exc), traceback=traceback.format_exc())
                save()
                raise

        all_complete = (control_row.get('reproduces_pinned') is True and
                        control_row.get('source_intact_after_stages') is True and
                        base_original.is_file() and base_verified.is_file() and
                        sha(base_original.read_bytes()) == ORIGINAL_SHA256 and
                        sha(base_verified.read_bytes()) == BASE_VERIFIED_SHA256 and
                        set(record['variants']) == set(VARIANTS) and
                        all(record['variants'][name].get('status') == 'COMPLETE'
                            for name in VARIANTS))
        record.update(complete=all_complete,
                      classification=('R21_FRACTIONAL_FINGERPRINT_COMPLETE'
                                      if all_complete else
                                      'R21_FRACTIONAL_FINGERPRINT_INCOMPLETE'))
        write(record_path, record)
        if not all_complete:
            raise SystemExit(4)
        return record
    except BaseException as exc:
        if record.get('complete') is not True:
            record['complete'] = False
            record['terminal_exception'] = {'type': type(exc).__name__,
                                            'message': str(exc),
                                            'traceback': traceback.format_exc()}
            save()
        raise


def fingerprint(a) -> dict[str, Any]:
    """Load exact pinned dependencies and run the eight R21 fingerprints."""
    require_cloud(dict(os.environ))
    transform, r20, o26, refresh = pinned_dependencies(a.repo, a.cloud_dir, a.evidence)
    cap = o26.load_capture(a.repo, 'r21_fractional_fingerprint')
    need(callable(getattr(cap, 'refusal_fingerprint', None)) and
         callable(getattr(cap, 'clear_semantic_opt_ins', None)),
         'pinned capture module lacks mode-9 fingerprint interface')
    deps: dict[str, Any] = {'transform_sha256': TRANSFORM_SHA256,
        'transform_repair_sha256': TRANSFORM_REPAIR_SHA256,
        'transform_controls_sha256': TRANSFORM_CONTROLS_SHA256,
        'r20_helper_sha256': R20_HELPER_SHA256,
        'o26_recipe_sha256': O26_RECIPE_SHA256,
        'o26_refresh_sha256': O26_REFRESH_SHA256,
        'capture_sha256': CAPTURE_SHA256}
    args = argparse.Namespace(**vars(a))
    args.compiler_sysroot = str(a.compiler_sysroot)
    record = fingerprint_batch(args, transform=transform.transform,
        export_decode=r20.export_decode, cap=cap, refresh=refresh,
        env=dict(os.environ), dependencies=deps)
    return record


def audit(a) -> dict[str, Any]:
    """Extend the pinned R20 source audit with this R21 incremental record."""
    helper_path = Path(__file__).resolve().parent / 'select-callee-r20.py'
    helper = load(helper_path, 'r21_fractional_audit_base',
                  R20_AUDIT_HELPER_SHA256)
    base_args = argparse.Namespace(evidence=a.evidence, output=a.output,
        runner_exit=a.runner_exit, failed_stage=a.failed_stage)
    base = helper.audit(base_args)
    need(isinstance(base, dict), 'pinned R20 audit did not return an object')
    record = dict(base)
    record['schema'] = 'r21-fractional-select-callee-audit-v1'
    record['base_audit_schema'] = base.get('schema')
    fp_path = a.evidence / 'cases/r21-fractional-fingerprint/r21-fractional-fingerprint.json'
    try:
        fingerprint_record = json.loads(fp_path.read_text()) if fp_path.is_file() else None
        fp_status = ('missing' if not fp_path.is_file() else
                     'null' if fingerprint_record is None else
                     'object' if isinstance(fingerprint_record, dict) else 'wrong-type')
    except (OSError, ValueError) as exc:
        fingerprint_record = {'unreadable': str(exc)}
        fp_status = 'unreadable'
    record['fractional_fingerprint'] = fingerprint_record
    record['fractional_fingerprint_status'] = fp_status
    record['accepted'] = False
    record['verification_accepted'] = False
    record['proof_credit'] = False
    record['evidence_complete'] = (
        base.get('evidence_complete') is True and
        isinstance(fingerprint_record, dict) and
        fingerprint_record.get('complete') is True)
    write(a.output, record)
    return record


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='mode', required=True)
    f = sub.add_parser('fingerprint', help='record source/MIR/refusal fingerprints only')
    for name in ('repo', 'cloud-dir', 'evidence', 'tool-home', 'schema', 'compiler-sysroot'):
        f.add_argument('--' + name, type=Path, required=True)
    f.add_argument('--deadline-epoch', type=int, required=True)
    d = sub.add_parser('audit', help='extend R20 source audit with R21 fingerprint status')
    d.add_argument('--evidence', type=Path, required=True)
    d.add_argument('--output', type=Path, required=True)
    d.add_argument('--runner-exit', type=int, required=True)
    d.add_argument('--failed-stage', required=True)
    args = parser.parse_args(argv)
    if args.mode == 'audit':
        audit(args)
        return 0
    if args.mode != 'fingerprint':
        parser.error('only MODE=fingerprint exists')
    require_cloud(dict(os.environ))
    try:
        record = fingerprint(args)
    except BaseException:
        raise
    print(json.dumps({'classification': record.get('classification'),
                      'complete': record.get('complete'),
                      'accepted': False, 'proof_credit': False}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
