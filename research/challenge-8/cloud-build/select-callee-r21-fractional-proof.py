#!/usr/bin/env python3
"""Inactive classified proof runner for R21 fractional-forget fingerprints.

The caller supplies the completed S2d fingerprint JSON and the already-loaded
R20 classified helper, O26 proof-stage callback, and mode-9 capture callback.
This module contains no guessed source or MIR hashes and registers no lane.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import time
import traceback
from typing import Any, Callable

SCHEMA = 'r21-fractional-proof-pins-v1'
RECORD_SCHEMA = 'r21-fractional-classified-proof-v1'
VARIANTS = (
    'positive', 'omit-selected-own', 'omit-unselected-own', 'no-retained-half',
    'callee-false-normal', 'callee-owner-duplicate', 'callee-owner-loss',
    'callee-thread-duplicate',
)
SAME_SITE_NEGATIVES = {'omit-selected-own', 'omit-unselected-own', 'no-retained-half'}
CALLEE_NEGATIVES = set(VARIANTS) - {'positive'} - SAME_SITE_NEGATIVES
EXPECTED_REFUSAL = 'INTENDED_DIAGNOSTIC_REFUSAL_NO_PROOF_RULE'
FINAL_SELECT_DIAGNOSTIC = 'Cannot prove result6 ='
CALLEE_DIAGNOSTIC = 'checked_forget_owned'
R20_OPT_IN = 'SORT4_R20_FINAL_SELECT_REPAIR'
FRACTIONAL_PREFIX = 'SORT4_R21_FRACTIONAL_'
STAGE_RESERVE_SECONDS = 150
CHECKED_FORGET_SIGNATURE = b'pub unsafe fn checked_forget_owned<T>(t: T)\n'
CHECKED_FORGET_BODY = b'{\n    let _ = ManuallyDrop::new(t);\n}'


def sha(data: bytes) -> str:
    import hashlib
    return hashlib.sha256(data).hexdigest()


def need(ok: bool, why: str) -> None:
    if not ok:
        raise RuntimeError('R21-FRACTIONAL-PROOF: ' + why)


def write(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name('.' + path.name + '.tmp')
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n')
    os.replace(tmp, path)


def _is_sha(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(r'[0-9a-f]{64}', value) is not None


def _snapshot_rows(value: object, label: str) -> dict[str, dict[str, Any]]:
    need(isinstance(value, dict), label + ' snapshots must be an object')
    expected_keys = {'unit', *(f'body-{i}' for i in range(9))}
    need(set(value) == expected_keys, label + ' snapshot labels differ from unit + nine bodies')
    rows: dict[str, dict[str, Any]] = {}
    for name, row in value.items():
        need(isinstance(row, dict), label + ' snapshot row has wrong type: ' + name)
        need(set(row) == {'file', 'bytes', 'sha256'},
             label + ' snapshot row key inventory differs: ' + name)
        filename, byte_count, digest = row.get('file'), row.get('bytes'), row.get('sha256')
        expected_filename = f'actual-nested-9-{name}.marshal'
        need(filename == expected_filename and type(byte_count) is int and byte_count > 0 and
             _is_sha(digest), label + ' snapshot row malformed: ' + name)
        rows[name] = {'file': filename, 'bytes': byte_count, 'sha256': digest}
    return rows


def fingerprint_to_pins(record: object) -> dict[str, Any]:
    """Derive strict proof pins only from a completed fractional fingerprint."""
    need(isinstance(record, dict) and
         record.get('schema') == 'r21-fractional-forget-fingerprint-v1' and
         record.get('complete') is True and record.get('accepted') is False and
         record.get('proof_credit') is False and record.get('body_proof_run') is False,
         'input fractional fingerprint is missing or incomplete')
    base = record.get('base_source')
    need(isinstance(base, dict) and _is_sha(base.get('original_sha256')) and
         _is_sha(base.get('verified_sha256')), 'base source pins malformed')
    need(record.get('variant_order') == list(VARIANTS), 'variant order differs')
    rows = record.get('variants')
    need(isinstance(rows, dict) and set(rows) == set(VARIANTS), 'variant inventory differs')
    snapshot_pins = record.get('snapshot_pins')
    need(isinstance(snapshot_pins, dict) and set(snapshot_pins) ==
         {'unit', *(f'body-{i}' for i in range(9))} and
         all(_is_sha(item) for item in snapshot_pins.values()),
         'default snapshot pin inventory malformed')
    location = record.get('location_control')
    need(isinstance(location, dict) and location.get('reproduces_pinned') is True and
         location.get('source_intact_after_stages') is True and
         isinstance(location.get('fingerprint_check'), dict) and
         location['fingerprint_check'].get('complete') is True and
         location['fingerprint_check'].get('snapshots_match_default_pins') is True,
         'baseline location control is not source- and snapshot-bound')
    location_fp = location.get('fingerprint')
    location_snapshots = _snapshot_rows(
        location_fp.get('snapshots') if isinstance(location_fp, dict) else None,
        'location-control')
    need({name: item['sha256'] for name, item in location_snapshots.items()} == snapshot_pins,
         'baseline location-control unit/body hashes differ from default pins')
    need(isinstance(location_fp, dict) and
         location_fp.get('classification') == EXPECTED_REFUSAL and
         location_fp.get('expected_refusal_seen') is True and
         location_fp.get('all_ten_snapshots') is True and
         location_fp.get('body_proof_run') is False,
         'baseline location-control fingerprint is not diagnostic-only')
    cases: dict[str, Any] = {}
    for variant in VARIANTS:
        row = rows[variant]
        need(isinstance(row, dict) and row.get('status') == 'COMPLETE' and
             row.get('source_intact_after_stages') is True and
             row.get('original_preserved') is True and
             row.get('original_sha256') == base['original_sha256'] and
             _is_sha(row.get('verified_sha256')),
             'fingerprint case is incomplete or source-unbound: ' + variant)
        fp = row.get('fingerprint')
        check = row.get('fingerprint_check')
        need(isinstance(fp, dict) and isinstance(check, dict) and
             check.get('complete') is True and
             type(check.get('snapshots_match_default_pins')) is bool and
             fp.get('body_proof_run') is False,
             'fingerprint stage is not a complete diagnostic-only case: ' + variant)
        stage = fp.get('stage')
        expected_source_pair = {'original/lib.rs': base['original_sha256'],
                                'verified/lib.rs': row['verified_sha256']}
        need(isinstance(stage, dict) and stage.get('status') == 'RAN' and
             stage.get('exit') == 2 and stage.get('source_unchanged') is True and
             stage.get('source_before') == expected_source_pair and
             stage.get('source_after') == expected_source_pair and
             stage.get('intrinsic_gate_active') is False and
             stage.get('pointer_drop_gate_active') is False and
             stage.get('stdout') == 'nine-body-fingerprint-refusal.log' and
             stage.get('stderr') == 'nine-body-fingerprint-refusal.log',
             'fingerprint source stage is unbound or unexpected: ' + variant)
        snapshots = _snapshot_rows(fp.get('snapshots'), variant)
        case_hashes = {name: item['sha256'] for name, item in snapshots.items()}
        need(check['snapshots_match_default_pins'] == (case_hashes == snapshot_pins),
             'per-case default-snapshot comparison is inconsistent: ' + variant)
        unchanged_bodies = {f'body-{index}' for index in (*range(6), 8)}
        need(all(case_hashes[name] == snapshot_pins[name] for name in unchanged_bodies),
             'fractional variant changed a body outside the confirmed 6/7 edit sites: ' + variant)
        mir_check = row.get('normal_mir_check')
        need(isinstance(mir_check, dict) and mir_check.get('complete') is True,
             'normal MIR export/decode incomplete: ' + variant)
        cases[variant] = {'verified_sha256': row['verified_sha256'],
                          'snapshots': snapshots}
    return {'schema': SCHEMA, 'base_original_sha256': base['original_sha256'],
            'base_verified_sha256': base['verified_sha256'],
            'snapshot_pins': dict(snapshot_pins), 'cases': cases,
            'variant_order': list(VARIANTS)}


def load_fingerprint_pins(path: Path) -> dict[str, Any]:
    """Read and validate the exact JSON emitted by the fingerprint-only lane."""
    try:
        record = json.loads(path.read_text())
    except (OSError, ValueError) as exc:
        raise RuntimeError('R21-FRACTIONAL-PROOF: cannot read fingerprint pin JSON: ' +
                           str(exc)) from exc
    return fingerprint_to_pins(record)


def validate_pins(pins: object) -> dict[str, Any]:
    need(isinstance(pins, dict) and pins.get('schema') == SCHEMA,
         'proof pin manifest schema missing')
    need(set(pins) == {'schema', 'base_original_sha256', 'base_verified_sha256',
                       'snapshot_pins', 'cases', 'variant_order'},
         'proof pin manifest key inventory differs')
    need(_is_sha(pins.get('base_original_sha256')) and
         _is_sha(pins.get('base_verified_sha256')), 'base hashes malformed')
    need(pins.get('variant_order') == list(VARIANTS), 'proof variant order differs')
    defaults = pins.get('snapshot_pins')
    need(isinstance(defaults, dict) and set(defaults) ==
         {'unit', *(f'body-{i}' for i in range(9))} and
         all(_is_sha(x) for x in defaults.values()), 'default unit/body hashes malformed')
    cases = pins.get('cases')
    need(isinstance(cases, dict) and set(cases) == set(VARIANTS), 'proof case inventory differs')
    for variant in VARIANTS:
        row = cases[variant]
        need(isinstance(row, dict) and set(row) == {'verified_sha256', 'snapshots'} and
             _is_sha(row.get('verified_sha256')),
             'verified source pin malformed: ' + variant)
        snapshots = _snapshot_rows(row.get('snapshots'), variant)
        hashes = {name: value['sha256'] for name, value in snapshots.items()}
        unchanged_bodies = {f'body-{index}' for index in (*range(6), 8)}
        need(all(hashes[name] == defaults[name] for name in unchanged_bodies),
             'case changed a body outside the confirmed 6/7 edit sites: ' + variant)
    return pins


def require_route(env: dict[str, str], phase_key: str, phase_value: str,
                  opt_in_key: str) -> None:
    need(isinstance(phase_key, str) and phase_key and isinstance(phase_value, str) and
         phase_value and env.get('SMALLSORT_EXECUTION_PROVIDER') == 'cloud-build' and
         env.get(phase_key) == phase_value and not env.get('GITHUB_ACTIONS'),
         'exact Cloud phase required')
    need(isinstance(opt_in_key, str) and opt_in_key.startswith(FRACTIONAL_PREFIX) and
         opt_in_key not in env and R20_OPT_IN not in env and
         not any(key.startswith(FRACTIONAL_PREFIX) for key in env),
         'fractional opt-in must be new and absent from ambient environment')


def _expected_argv(tool_home: Path) -> list[str]:
    return [str(tool_home / 'bin/verifast'), '-rustc_args', '--edition 2021',
            '-verbose', '1', 'verified/lib.rs']


def _validate_capture(result: object, case: Path, original_sha: str,
                      verified_sha: str, pins: dict[str, dict[str, Any]],
                      tool_home: Path) -> dict[str, Any]:
    errors: list[str] = []
    if not isinstance(result, dict):
        return {'complete': False, 'errors': ['capture result is not an object'],
                'returned': result}
    stage = result.get('stage')
    expected_sources = {'original/lib.rs': original_sha,
                        'verified/lib.rs': verified_sha}
    if not isinstance(stage, dict):
        errors.append('capture stage missing or wrong type')
    else:
        if (stage.get('status') != 'RAN' or type(stage.get('exit')) is not int or
                stage.get('exit') != 2):
            errors.append('capture stage is not the intended diagnostic refusal exit 2')
        if (stage.get('source_before') != expected_sources or
                stage.get('source_after') != expected_sources or
                stage.get('source_unchanged') is not True):
            errors.append('capture source stage target mismatch')
        if stage.get('intrinsic_gate_active') is not False or \
                stage.get('pointer_drop_gate_active') is not False:
            errors.append('capture semantic gates are active')
        if stage.get('argv') != [str(tool_home / 'bin/verifast'), '-rustc_args',
                                 '--edition 2021', '-verbose', '1', 'verified/lib.rs']:
            errors.append('capture verifier argv differs')
        if (stage.get('stdout') != 'nine-body-fingerprint-refusal.log' or
                stage.get('stderr') != 'nine-body-fingerprint-refusal.log'):
            errors.append('capture log target differs')
    if result.get('classification') != EXPECTED_REFUSAL or \
            result.get('expected_refusal_seen') is not True or \
            result.get('all_ten_snapshots') is not True or \
            result.get('body_proof_run') is not False:
        errors.append('capture is not the complete diagnostic-only mode-9 result')
    observed = result.get('snapshots')
    if not isinstance(observed, dict) or set(observed) != set(pins):
        errors.append('capture unit/body snapshot inventory differs')
    else:
        for name, expected in pins.items():
            item = observed.get(name)
            if not isinstance(item, dict):
                errors.append(name + ': snapshot missing or wrong type')
                continue
            filename, byte_count, digest = item.get('file'), item.get('bytes'), item.get('sha256')
            path = case / expected['file']
            if (filename != expected['file'] or byte_count != expected['bytes'] or
                    digest != expected['sha256'] or not path.is_file() or
                    path.stat().st_size != expected['bytes'] or
                    sha(path.read_bytes()) != expected['sha256']):
                errors.append(name + ': snapshot pin or physical bytes mismatch')
    return {'complete': not errors, 'errors': errors, 'stage': stage,
            'snapshots': observed, 'returned': result}


def _classify(r20, variant: str, stage: object, log_text: object,
              expected_sources: dict[str, str], observed_sources: dict[str, str | None],
              tool_home: Path) -> tuple[str, str]:
    # R20's classifier binds exact argv, source pair, gate bits and log paths.
    # The valid row name maps this new same-unit call to its positive opt-in slot.
    bound = r20.classify_bound_row('merged-optin', stage, log_text,
        expected_argv=_expected_argv(tool_home), expected_sources=expected_sources,
        observed_sources=observed_sources)
    if bound in ('NOT_RUN_OR_INCONCLUSIVE', 'SOURCE_STAGE_TARGET_MISMATCH'):
        return bound, bound
    if not isinstance(stage, dict):
        return bound, 'NOT_RUN_OR_INCONCLUSIVE'
    if variant == 'positive':
        expected = (bound == 'POSITIVE_VERIFIED_SOURCE_REPORTED')
        return bound, 'POSITIVE_VERIFIED_SOURCE_REPORTED' if expected else 'POSITIVE_FAILED'
    if not isinstance(log_text, str) or not log_text.strip() or stage.get('exit') == 0:
        return bound, 'CONTROL_NOT_REJECTED'
    if variant in SAME_SITE_NEGATIVES:
        okay = FINAL_SELECT_DIAGNOSTIC in log_text
        return bound, 'EXPECTED_SAME_SITE_FINAL_SELECT_FAILURE' if okay else 'CONTROL_FAILURE_TARGET_MISMATCH'
    okay = CALLEE_DIAGNOSTIC in log_text and ': error:' in log_text
    return bound, 'EXPECTED_CALLEE_CONTRACT_REJECTION' if okay else 'CONTROL_FAILURE_TARGET_MISMATCH'


def proof_batch(*, evidence: Path, original: bytes, base_verified: bytes,
                fingerprint_record: object, transform: Callable[[bytes, str], bytes],
                r20, proof_stage: Callable, refusal_fingerprint: Callable,
                tool_home: Path, schema: Path, compiler_sysroot: Path,
                deadline_epoch: int, phase_key: str, phase_value: str,
                opt_in_key: str, env: dict[str, str]) -> dict[str, Any]:
    """Run eight classified same-unit proof rows using injected pinned services."""
    require_route(env, phase_key, phase_value, opt_in_key)
    live_env = dict(os.environ)
    require_route(live_env, phase_key, phase_value, opt_in_key)
    env_keys = {key for key in set(env) | set(live_env)
                if key in ('SMALLSORT_EXECUTION_PROVIDER', phase_key, R20_OPT_IN) or
                key.startswith(FRACTIONAL_PREFIX)}
    need(all(env.get(key) == live_env.get(key) for key in env_keys),
         'caller route environment differs from the live process environment')
    pins = validate_pins(fingerprint_to_pins(fingerprint_record))
    need(sha(original) == pins['base_original_sha256'] and
         sha(base_verified) == pins['base_verified_sha256'],
         'base source bytes differ from the S2d fingerprint input')
    root = evidence / 'cases/r21-fractional-proof'
    root.mkdir(parents=True, exist_ok=False)
    record: dict[str, Any] = {
        'schema': RECORD_SCHEMA, 'classification': 'R21_FRACTIONAL_CLASSIFIED_PROOF_INCOMPLETE',
        'complete': False, 'variant_order': list(VARIANTS),
        'pins': pins, 'rows': {}, 'body_proof_run': True,
        'accepted': False, 'proof_credit': False,
    }
    path = root / 'r21-fractional-proof.json'

    def save() -> None:
        record['complete'] = False
        record['accepted'] = False
        record['proof_credit'] = False
        write(path, record)

    save()
    try:
        for variant in VARIANTS:
            row: dict[str, Any] = {'variant': variant, 'status': 'PENDING'}
            record['rows'][variant] = row
            save()
            try:
                if deadline_epoch - int(time.time()) < STAGE_RESERVE_SECONDS:
                    row.update(status='NOT_RUN', reason='shared deadline reserve',
                               preflight_capture={'status': 'NOT_RUN'},
                               stage={'status': 'NOT_RUN'},
                               postflight_capture={'status': 'NOT_RUN'},
                               classification='NOT_RUN_OR_INCONCLUSIVE')
                    save()
                    continue
                candidate = transform(base_verified, variant)
                need(isinstance(candidate, bytes), 'transform result is not bytes: ' + variant)
                need(candidate.count(CHECKED_FORGET_SIGNATURE) == 1 and
                     candidate.count(CHECKED_FORGET_BODY) == 1,
                     'candidate does not contain one same-unit checked_forget_owned body')
                expected_sha = pins['cases'][variant]['verified_sha256']
                need(sha(candidate) == expected_sha,
                     'transformed source differs from per-case pin: ' + variant)
                case = root / 'variants' / variant / 'nine-body-a1-owned-forget'
                (case / 'original').mkdir(parents=True)
                (case / 'verified').mkdir()
                (case / 'original/lib.rs').write_bytes(original)
                (case / 'verified/lib.rs').write_bytes(candidate)
                row.update(status='PREPARED', original_sha256=sha(original),
                           verified_sha256=expected_sha,
                           source_intact_before_stage=True)
                save()
                expected_sources = {'original/lib.rs': sha(original),
                                    'verified/lib.rs': expected_sha}
                expected_snapshots = pins['cases'][variant]['snapshots']
                row['preflight_capture'] = refusal_fingerprint(
                    case, {'verified_sha256': expected_sha},
                    type('CaptureArgs', (), {'tool_home': tool_home,
                        'schema': schema, 'compiler_sysroot': str(compiler_sysroot),
                        'deadline_epoch': deadline_epoch})())
                row['preflight_capture_check'] = _validate_capture(
                    row['preflight_capture'], case, sha(original), expected_sha,
                    expected_snapshots, tool_home)
                save()
                if not row['preflight_capture_check']['complete']:
                    row.update(status='INCOMPLETE',
                               classification='SNAPSHOT_OR_CAPTURE_MISMATCH')
                    save()
                    continue

                try:
                    os.environ[opt_in_key] = '1'
                    stage = proof_stage(case=case, name='r20-merged-optin',
                        tool_home=tool_home, schema=schema,
                        compiler_sysroot=compiler_sysroot,
                        deadline_epoch=deadline_epoch, variant=variant)
                except BaseException as exc:
                    row.update(status='EXCEPTION', stage={'status': 'EXCEPTION'},
                               exception_type=type(exc).__name__, exception=str(exc),
                               traceback=traceback.format_exc())
                    save()
                    raise
                finally:
                    os.environ.pop(opt_in_key, None)
                row['stage'] = stage
                log_path = case / 'r20-merged-optin.log'
                log_text = log_path.read_text(errors='replace') if log_path.is_file() else None
                observed_sources = {name: (sha((case / name).read_bytes())
                    if (case / name).is_file() else None) for name in expected_sources}
                bound, classification = _classify(r20, variant, stage, log_text,
                    expected_sources, observed_sources, tool_home)
                row.update(bound_verdict=bound, classification=classification,
                           normal_unwind_nested_drop_gates=(
                               isinstance(stage, dict) and
                               stage.get('intrinsic_gate_active') is True and
                               stage.get('pointer_drop_gate_active') is True),
                           observed_sources_after_stage=observed_sources,
                           log_file=log_path.name if log_path.is_file() else None,
                           log_sha256=sha(log_path.read_bytes()) if log_path.is_file() else None)
                save()
                if deadline_epoch - int(time.time()) < STAGE_RESERVE_SECONDS:
                    row['postflight_capture'] = {'status': 'NOT_RUN',
                                                 'reason': 'shared deadline reserve'}
                    row.update(status='INCOMPLETE', postflight_capture_check={
                        'complete': False, 'errors': ['post-proof snapshot reserve']})
                    save()
                    continue
                row['postflight_capture'] = refusal_fingerprint(
                    case, {'verified_sha256': expected_sha},
                    type('CaptureArgs', (), {'tool_home': tool_home,
                        'schema': schema, 'compiler_sysroot': str(compiler_sysroot),
                        'deadline_epoch': deadline_epoch})())
                row['postflight_capture_check'] = _validate_capture(
                    row['postflight_capture'], case, sha(original), expected_sha,
                    expected_snapshots, tool_home)
                source_intact = all((case / name).is_file() and
                                    sha((case / name).read_bytes()) == digest
                                    for name, digest in expected_sources.items())
                row['source_intact_after_stages'] = source_intact
                expected_outcome = (classification == 'POSITIVE_VERIFIED_SOURCE_REPORTED'
                    if variant == 'positive' else
                    classification in ('EXPECTED_SAME_SITE_FINAL_SELECT_FAILURE',
                                        'EXPECTED_CALLEE_CONTRACT_REJECTION'))
                row['status'] = ('COMPLETE' if expected_outcome and source_intact and
                    row['postflight_capture_check'].get('complete') is True else 'INCOMPLETE')
                save()
            except BaseException as exc:
                row.update(status='EXCEPTION', exception_type=type(exc).__name__,
                           exception=str(exc), traceback=traceback.format_exc())
                save()
                raise
        complete = (set(record['rows']) == set(VARIANTS) and
                    all(record['rows'][name].get('status') == 'COMPLETE'
                        for name in VARIANTS))
        record.update(complete=complete,
            classification=('R21_FRACTIONAL_CLASSIFIED_PROOF_COMPLETE' if complete
                            else 'R21_FRACTIONAL_CLASSIFIED_PROOF_INCOMPLETE'))
        write(path, record)
        return record
    except BaseException as exc:
        record['complete'] = False
        record['terminal_exception'] = {'type': type(exc).__name__,
                                        'message': str(exc),
                                        'traceback': traceback.format_exc()}
        save()
        raise
