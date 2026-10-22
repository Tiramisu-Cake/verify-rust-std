#!/usr/bin/env python3
"""Fail-closed source/profile checks and non-credit audit for R21 body route."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from typing import Any

HERE = Path('research/challenge-8/cloud-build/sort4-caller-entry-native')
PROFILE = HERE / 'A1-ACTUAL-BODY-R21-TRANSPORT-PROFILE.json'
EXECUTION_PHASE = 'SORT4-ACTUAL-SELECT-2026-10-23-R21'
EXECUTION_LANE = 'o26-sort4-body-r21'
BACKEND_PHASE = 'SORT4-A1-CHECKED-TRAIT-CONTRACT-CLOUD-2026-10-17'
BACKEND_AUTHORIZATION = 'SORT4-ACTUAL-C2-2026-10-21-R17'
HEX64 = re.compile(r'[0-9a-f]{64}\Z')

PROOF_SCALAR_FILE_PINS = {
    'a1_actual_body_sha256': HERE / 'a1-actual-body-r21.py',
    'a1_tool_sha256': HERE / 'a1-tool-r21.py',
    'a1_cleanup_helper_sha256': HERE / 'a1-cleanup-helper.py',
    'a1_ghost_grammar_sha256': HERE / 'a1-ghost-grammar.py',
}
INFRA_SCALAR_FILE_PINS = {
    'a1_entry_sha256': HERE / 'a1-entry-r21.py',
    'a1_runner_sha256': HERE / 'a1-runner-r21.py',
    'caller_driver_sha256': HERE / 'driver.py',
}
STD_FILES = {
    'library/core/src/marker.rs',
    'library/core/src/slice/sort/shared/mod.rs',
    'library/core/src/slice/sort/shared/smallsort.rs',
    'library/core/src/slice/sort/stable/quicksort.rs',
}
BODY_DEPENDENCY_PATHS = {
    'capture.py': Path('research/challenge-8/overnight-sort4/capture.py'),
}


def sha_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def _need(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError('R21 body route: ' + why)


def _digest(value: object) -> bool:
    return isinstance(value, str) and HEX64.fullmatch(value) is not None


def require_route(env: dict[str, str], profile: dict[str, Any]) -> None:
    _need(env.get('SMALLSORT_EXECUTION_PROVIDER') == 'cloud-build' and
          env.get('SORT4_R21_BODY_PHASE_ID') == EXECUTION_PHASE and
          env.get('LANE') == EXECUTION_LANE and
          bool(env.get('CLOUD_BUILD_ID')) and not env.get('GITHUB_ACTIONS'),
          'fresh Cloud execution route differs')
    _need(env.get('SORT4_A1_PHASE_ID') == BACKEND_PHASE and
          env.get('SORT4_A1_AUTHORIZATION_PHASE_ID') == BACKEND_AUTHORIZATION and
          env.get('SORT4_A1_CHECKED_TRAIT_CONTRACT') == '1',
          'R17 backend protocol environment differs')
    _need(profile.get('execution_authority_phase_id') == EXECUTION_PHASE and
          profile.get('execution_lane') == EXECUTION_LANE and
          profile.get('phase') == EXECUTION_PHASE and
          profile.get('authorization_phase_id') == BACKEND_AUTHORIZATION and
          profile.get('experiment_protocol_phase_id') == BACKEND_PHASE and
          profile.get('phase_id') == BACKEND_PHASE and
          profile.get('execution_mode') == 'actual-sort4-body-v1' and
          profile.get('body_action') == 'full-body-c1-recovery' and
          profile.get('cloud_build_enabled') is True,
          'profile route/backend phase binding differs')
    _need(all(profile.get(key) is False for key in (
        'accepted', 'admitted', 'proof_credit', 'independent_credit',
        'profile_accepted', 'formal_verification_passed',
        'admission_record_created')),
        'profile must not claim acceptance, admission or proof credit')


def validate_profile(profile: object, expected_sha: str,
                     env: dict[str, str], proof_root: Path,
                     infra_root: Path) -> dict[str, Any]:
    """Validate route identity and pins from their declared transport roots."""
    _need(isinstance(profile, dict), 'profile must be a JSON object')
    assert isinstance(profile, dict)
    _need(_digest(expected_sha), 'profile SHA256 is malformed')
    profile_path = proof_root / PROFILE
    _need(profile_path.is_file() and sha_file(profile_path) == expected_sha,
          'profile file SHA256 differs from the admitted pin')
    _need(env.get('SORT4_A1_PROFILE_SHA256') == expected_sha,
          'profile environment SHA256 differs')
    require_route(env, profile)

    for field, relative in PROOF_SCALAR_FILE_PINS.items():
        expected = profile.get(field)
        path = proof_root / relative
        _need(_digest(expected) and path.is_file() and sha_file(path) == expected,
              'pinned source differs: ' + field)

    for field, relative in INFRA_SCALAR_FILE_PINS.items():
        expected = profile.get(field)
        path = infra_root / relative
        _need(_digest(expected) and path.is_file() and sha_file(path) == expected,
              'infra-pinned source differs: ' + field)

    helper_pins = profile.get('a1_helper_sha256')
    _need(isinstance(helper_pins, dict), 'A1 helper pin map is missing')
    assert isinstance(helper_pins, dict)
    for name in ('a1-ast-gates.py', 'a1-fixtures.py', 'a1-tool-r21.py'):
        expected = helper_pins.get(name)
        _need(_digest(expected), 'required A1 helper pin is malformed: ' + name)
        path = proof_root / HERE / name
        _need(path.is_file() and sha_file(path) == expected,
              'required A1 helper differs: ' + name)
    _need(helper_pins['a1-tool-r21.py'] == profile.get('a1_tool_sha256'),
          'A1 tool pin fields disagree')

    for field in ('a1_checked_cleanup_helper_sha256',
                  'a1_checked_cleanup_import_sha256',
                  'reference_own_probe_sha256'):
        _need(_digest(profile.get(field)), 'required cleanup/AST helper pin is malformed: ' + field)
    probe = proof_root / HERE / 'a1-reference-own-probe-r17.py'
    _need(probe.is_file() and sha_file(probe) == profile['reference_own_probe_sha256'],
          'reference-own AST helper differs')

    std_pins = profile.get('std_source_sha256')
    _need(isinstance(std_pins, dict) and set(std_pins) == STD_FILES,
          'std source pin inventory differs')
    assert isinstance(std_pins, dict)
    for relative, expected in std_pins.items():
        path = proof_root / relative
        _need(_digest(expected) and path.is_file() and sha_file(path) == expected,
              'std source identity differs: ' + relative)

    dependencies = profile.get('actual_body_dependencies_sha256')
    _need(isinstance(dependencies, dict) and dependencies,
          'actual-body fixture pin inventory is missing')
    assert isinstance(dependencies, dict)
    for name, expected in dependencies.items():
        relative = BODY_DEPENDENCY_PATHS.get(name, HERE / name)
        path = proof_root / relative
        _need(_digest(expected) and path.is_file() and sha_file(path) == expected,
              'actual-body fixture source differs: ' + name)

    semantics = profile.get('a1_focus_semantics_sha256')
    _need(isinstance(semantics, dict) and semantics and
          all(isinstance(k, str) and _digest(v) for k, v in semantics.items()),
          'pinned tool AST/kernel semantic hash inventory is malformed')
    return profile


def preflight(proof_root: Path, infra_root: Path, profile_sha256: str,
              env: dict[str, str]) -> dict[str, Any]:
    path = proof_root / PROFILE
    _need(path.is_file(), 'R21 profile is missing')
    try:
        profile = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError('R21 body route: profile is unreadable JSON') from exc
    validate_profile(profile, profile_sha256, env, proof_root, infra_root)
    return {'classification': 'R21_BODY_SOURCE_PREFLIGHT',
            'profile_sha256': profile_sha256,
            'source_files_checked': len(STD_FILES),
            'proof_scalar_source_files_checked': len(PROOF_SCALAR_FILE_PINS),
            'infra_source_files_checked': len(INFRA_SCALAR_FILE_PINS),
            'body_dependency_files_checked': len(profile['actual_body_dependencies_sha256']),
            'entry_runner_tool_and_helpers_checked': True,
            'proof_credit': False}


def _diagnostic_state(value: object) -> tuple[str, str | None]:
    if value is None:
        return 'NULL', None
    if not isinstance(value, dict):
        return 'WRONG_TYPE', None
    body = value.get('body_target')
    if not isinstance(body, dict):
        return ('PARTIAL' if body is None else 'WRONG_TYPE'), None
    status = body.get('status')
    if status == 'NOT_RUN':
        return 'NOT_RUN', status
    required = ('schema', 'classification', 'proof_credit', 'accepted',
                'verification_accepted', 'profile_accepted', 'body_target')
    if (all(key in value for key in required) and isinstance(status, str) and
            status not in ('UNKNOWN', '')):
        return 'BODY_DIAGNOSTIC_PRESENT', status
    return 'PARTIAL', status if isinstance(status, str) else None


def summarize_diagnostic(raw: bytes | None, runner_exit: int,
                         failed_stage: str) -> dict[str, Any]:
    """Preserve diagnostic payload and process outcome without proof inference."""
    payload: object = None
    raw_text = None
    if raw is None:
        state = 'MISSING'
    else:
        raw_text = raw.decode('utf-8', errors='replace')
        try:
            payload = json.loads(raw_text)
            state, body_status = _diagnostic_state(payload)
        except json.JSONDecodeError:
            state, body_status = 'INVALID_JSON', None
    if raw is None:
        body_status = None
    process = ('TIMEOUT' if runner_exit in (124, 137) else
               'SUCCESS_EXIT' if runner_exit == 0 else 'ERROR_EXIT')
    out: dict[str, Any] = {
        'schema': 'r21-body-route-audit-v1',
        'runner_exit': runner_exit,
        'failed_stage': failed_stage,
        'process_status': process,
        'body_diagnostic_state': state,
        'body_status': body_status,
        'body_diagnostic': payload if isinstance(payload, (dict, list)) else None,
        'accepted': False,
        'proof_credit': False,
    }
    if state in ('WRONG_TYPE', 'INVALID_JSON') and raw_text is not None:
        out['body_diagnostic_raw'] = raw_text
    return out


def audit(evidence: Path, output: Path, runner_exit: int,
          failed_stage: str, proof_root: Path, infra_root: Path,
          profile_sha256: str,
          env: dict[str, str]) -> dict[str, Any]:
    try:
        preflight(proof_root, infra_root, profile_sha256, env)
        pin_status = {'classification': 'PREFLIGHT_MATCH'}
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        # The terminal audit must still preserve the original runner result if
        # a pin or route check itself failed during startup or after execution.
        pin_status = {'classification': 'PREFLIGHT_MISMATCH', 'reason': str(exc)}
    diagnostic_path = evidence / 'diagnostic-audit.json'
    raw = diagnostic_path.read_bytes() if diagnostic_path.is_file() else None
    result = summarize_diagnostic(raw, runner_exit, failed_stage)
    result.update(profile_sha256=profile_sha256, profile_preflight=pin_status,
                  diagnostic_path=str(diagnostic_path),
                  diagnostic_sha256=sha_bytes(raw) if raw is not None else None)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='mode', required=True)
    p = sub.add_parser('preflight')
    p.add_argument('--proof-root', type=Path, required=True)
    p.add_argument('--infra-root', type=Path, required=True)
    p.add_argument('--profile-sha256', required=True)
    p.add_argument('--evidence', type=Path, required=True)
    p = sub.add_parser('audit')
    p.add_argument('--proof-root', type=Path, required=True)
    p.add_argument('--infra-root', type=Path, required=True)
    p.add_argument('--evidence', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--profile-sha256', required=True)
    p.add_argument('--runner-exit', type=int, required=True)
    p.add_argument('--failed-stage', required=True)
    args = parser.parse_args(argv)
    try:
        if args.mode == 'preflight':
            result = preflight(args.proof_root, args.infra_root,
                               args.profile_sha256, dict(os.environ))
            args.evidence.mkdir(parents=True, exist_ok=True)
            (args.evidence / 'body-route-preflight.json').write_text(
                json.dumps(result, indent=2, sort_keys=True) + '\n')
        else:
            result = audit(args.evidence, args.output, args.runner_exit,
                           args.failed_stage, args.proof_root,
                           args.infra_root,
                           args.profile_sha256, dict(os.environ))
        print(json.dumps(result, sort_keys=True))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
