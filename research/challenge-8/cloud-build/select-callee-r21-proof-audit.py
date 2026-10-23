#!/usr/bin/env python3
"""Preserve R21 fractional proof observations without granting acceptance."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import uuid

BASE_SHA256 = '83d2d0940fcb255a58b97db8d6161ec3b39660a62905f89a33f926a96d3099ba'
VARIANTS = ('positive', 'omit-selected-own', 'omit-unselected-own',
            'no-retained-half', 'callee-false-normal', 'callee-owner-duplicate',
            'callee-owner-loss', 'callee-thread-duplicate')
R24_SESSION_PHASE = 'SORT4-ACTUAL-SELECT-2026-10-24-R24'
R24_CHECKED_POINTER_MARKER = (
    'SORT4-R24-CHECKED-POINTER-OUTCOMES: pointer_drop=1 '
    'assume_init=1; raw MIR cleanup retained')
_SHA256 = re.compile(r'^[0-9a-f]{64}$')
TARGET_HELPER_SHA256 = 'ef48182797f89dc813f4dda167fbc6c0c3eedc4f4feb49eb06afd59dacd2833d'
_TARGET_DIAGNOSTIC_MARKERS = (
    'error:', 'fatal error', 'cannot prove', 'no matching heap chunks',
    'function leaks heap chunks', 'assertion failure', 'verification failed',
)
_TARGET_LOCATION = re.compile(
    r'^(?P<file>.+)\((?P<line>[1-9][0-9]*),(?P<start>[1-9][0-9]*)-'
    r'(?P<end>[1-9][0-9]*)\): (?P<message>\S.*)$')


def _sha256(value):
    return isinstance(value, str) and _SHA256.fullmatch(value) is not None


def _current_log_diagnostic(raw: bytes):
    try:
        text = raw.decode('utf-8', errors='strict')
    except UnicodeDecodeError:
        return None
    diagnostics = []
    for index, source_line in enumerate(text.splitlines(), 1):
        line = source_line.strip()
        if any(marker in line.casefold() for marker in _TARGET_DIAGNOSTIC_MARKERS):
            diagnostics.append((index, line))
    if len(diagnostics) != 1:
        return None
    line_number, line = diagnostics[0]
    match = _TARGET_LOCATION.fullmatch(line)
    if match is None:
        return None
    return {
        'diagnostic_line': line_number,
        'file': match.group('file'),
        'line': int(match.group('line')),
        'start_column': int(match.group('start')),
        'end_column': int(match.group('end')),
        'message': match.group('message'),
    }


def complete_matrix(proof, *, evidence_root=None, native_build_id=None,
                    native_r24_session_phase_id=None):
    if (not isinstance(proof, dict) or
            proof.get('schema') != 'r21-fractional-classified-proof-v1' or
            proof.get('complete') is not True or
            proof.get('body_proof_run') is not True or
            proof.get('accepted') is not False or proof.get('proof_credit') is not False or
            proof.get('variant_order') != list(VARIANTS)):
        return False
    rows = proof.get('rows')
    if not isinstance(rows, dict) or set(rows) != set(VARIANTS):
        return False
    validation = proof.get('diagnostic_target_validation')
    pins = proof.get('pins')
    dependencies = proof.get('entry_dependencies')
    if (not isinstance(validation, dict) or
            validation.get('schema') != 'select-r22-control-target-validation-v1' or
            validation.get('status') != 'TARGET_MAP_VALIDATED_NOT_ACCEPTED' or
            validation.get('accepted') is not False or
            validation.get('proof_credit') is not False or
            validation.get('provenance_status') !=
                'CALLER_DECLARED_PRIOR_OBSERVATIONS_CONSISTENT_NOT_AUTHENTICATED' or
            validation.get('target_map_sha256') !=
                proof.get('diagnostic_target_map_sha256') or
            proof.get('target_map_unchanged') is not True or
            proof.get('tool_spec_unchanged') is not True or
            set(validation.get('targets', {})) != set(VARIANTS) - {'positive'} or
            not isinstance(pins, dict) or not isinstance(pins.get('cases'), dict) or
            not isinstance(dependencies, dict) or
            proof.get('r24_session_phase_id') != R24_SESSION_PHASE or
            proof.get('checked_pointer_outcomes_requested') is not True or
            native_r24_session_phase_id != R24_SESSION_PHASE or
            not _sha256(dependencies.get('target_map_sha256')) or
            not _sha256(dependencies.get('target_map_canonical_sha256')) or
            dependencies.get('target_map_canonical_sha256') !=
                proof.get('diagnostic_target_map_sha256') or
            not _sha256(dependencies.get('tool_spec_sha256')) or
            dependencies.get('target_helper_sha256') != TARGET_HELPER_SHA256):
        return False
    try:
        canonical_build_id = str(uuid.UUID(native_build_id))
    except (ValueError, AttributeError, TypeError):
        return False
    provider_record = dependencies.get('provider_record')
    tool_home_value = proof.get('tool_home')
    if not isinstance(tool_home_value, str) or not Path(tool_home_value).is_absolute():
        return False
    expected_argv = [str(Path(tool_home_value) / 'bin/verifast'), '-rustc_args',
                     '--edition 2021', '-verbose', '1', 'verified/lib.rs']
    if (canonical_build_id != native_build_id.lower() or
            proof.get('current_build_id') != canonical_build_id or
            not isinstance(provider_record, dict) or
            provider_record.get('provider') != 'cloud-build' or
            provider_record.get('build_id') != canonical_build_id or
            provider_record.get('project') != 'smallsort-ci' or
            provider_record.get('region') != 'global' or
            provider_record.get('os') != 'ubuntu-22.04' or
            provider_record.get('arch') != 'x86_64' or
            not isinstance(evidence_root, Path) or not evidence_root.is_dir()):
        return False
    target_tool_hashes = {target.get('tool_spec_sha256')
                          for target in validation['targets'].values()
                          if isinstance(target, dict)}
    if target_tool_hashes != {dependencies['tool_spec_sha256']}:
        return False
    for variant in VARIANTS:
        row = rows[variant]
        if not isinstance(row, dict):
            return False
        stage = row.get('stage')
        expected_source = pins['cases'].get(variant, {}).get('verified_sha256')
        original_source = pins.get('base_original_sha256')
        expected_sources = {'original/lib.rs': original_source,
                            'verified/lib.rs': expected_source}
        if (not _sha256(expected_source) or not _sha256(original_source) or
                row.get('verified_sha256') != expected_source or
                row.get('observed_sources_after_stage') != expected_sources or
                row.get('status') != 'COMPLETE' or
                row.get('source_intact_after_stages') is not True or
                row.get('normal_unwind_nested_drop_gates') is not True or
                not isinstance(stage, dict) or stage.get('status') != 'RAN' or
                type(stage.get('exit')) is not int or
                stage.get('intrinsic_gate_active') is not True or
                stage.get('pointer_drop_gate_active') is not True or
                stage.get('r24_checked_pointer_outcomes_requested') is not True or
                stage.get('source_unchanged') is not True or
                stage.get('argv') != expected_argv or
                stage.get('stdout') != 'r20-merged-optin.log' or
                stage.get('stderr') != 'r20-merged-optin.log' or
                row.get('log_file') != 'r20-merged-optin.log' or
                stage.get('source_before') != expected_sources or
                stage.get('source_after') != expected_sources):
            return False
        current = row.get('current_stage_observation')
        expected_log_path = (
            f'cases/r21-fractional-proof/variants/{variant}/'
            'nine-body-a1-owned-forget/r20-merged-optin.log')
        if (not isinstance(current, dict) or
                current.get('schema') != 'select-current-stage-target-observation-v1' or
                current.get('build_id') != canonical_build_id or
                current.get('variant') != variant or
                current.get('source_hashes') != expected_sources or
                current.get('tool_spec_sha256') != dependencies.get('tool_spec_sha256') or
                current.get('argv') != stage.get('argv') or
                current.get('stdout') != stage.get('stdout') or
                current.get('stderr') != stage.get('stderr') or
                current.get('status') != stage.get('status') or
                current.get('exit') != stage.get('exit') or
                current.get('intrinsic_gate_active') is not True or
                current.get('pointer_drop_gate_active') is not True or
                current.get('r24_checked_pointer_outcomes_requested') is not True or
                current.get('source_before') != stage.get('source_before') or
                current.get('source_after') != stage.get('source_after') or
                current.get('source_unchanged') is not True or
                current.get('log_path') != expected_log_path or
                current.get('preflight_capture_check') != row.get('preflight_capture_check') or
                current.get('postflight_capture_check') != row.get('postflight_capture_check') or
                current.get('log_sha256') != row.get('log_sha256') or
                not _sha256(current.get('log_sha256'))):
            return False
        if ((variant == 'positive' and stage.get('exit') != 0) or
                (variant != 'positive' and stage.get('exit') != 1)):
            return False
        log_path = evidence_root / expected_log_path
        try:
            relative_parts = Path(expected_log_path).parts
            cursor = evidence_root.resolve()
            symlink_component = False
            for part in relative_parts:
                cursor = cursor / part
                symlink_component = symlink_component or cursor.is_symlink()
            if (symlink_component or not log_path.is_file() or
                    not log_path.resolve().is_relative_to(evidence_root.resolve())):
                return False
            log_bytes = log_path.read_bytes()
        except OSError:
            return False
        physical_log_sha = hashlib.sha256(log_bytes).hexdigest()
        if physical_log_sha != current.get('log_sha256'):
            return False
        try:
            log_text = log_bytes.decode('utf-8', errors='strict')
        except UnicodeDecodeError:
            return False
        if log_text.splitlines().count(R24_CHECKED_POINTER_MARKER) != 1:
            return False
        if variant != 'positive':
            target_pin = validation['targets'].get(variant)
            provenance = target_pin.get('provenance') if isinstance(target_pin, dict) else None
            try:
                provenance_build = str(uuid.UUID(provenance['build_id']))
            except (ValueError, AttributeError, TypeError, KeyError):
                provenance_build = None
            if (not isinstance(target_pin, dict) or
                    target_pin.get('variant') != variant or
                    target_pin.get('observed') is not True or
                    target_pin.get('source_sha256') != expected_source or
                    not _sha256(target_pin.get('tool_spec_sha256')) or
                    not isinstance(provenance, dict) or
                    set(provenance) != {'build_id', 'brief_log_sha256',
                        'brief_log_index', 'archive_id', 'request_id'} or
                    provenance_build != provenance.get('build_id') or
                    not _sha256(provenance.get('brief_log_sha256')) or
                    type(provenance.get('brief_log_index')) is not int or
                    provenance.get('brief_log_index') <= 0 or
                    not isinstance(provenance.get('archive_id'), str) or
                    not provenance.get('archive_id').strip() or
                    not isinstance(provenance.get('request_id'), str) or
                    not provenance.get('request_id').strip() or
                    not _sha256(target_pin.get('log_sha256'))):
                return False
        for key in ('preflight_capture_check', 'postflight_capture_check'):
            if not isinstance(row.get(key), dict) or row[key].get('complete') is not True:
                return False
            snapshots = row[key].get('snapshots')
            expected_snapshots = pins['cases'][variant].get('snapshots')
            if not isinstance(snapshots, dict) or not isinstance(expected_snapshots, dict) or \
                    set(snapshots) != set(expected_snapshots):
                return False
            for name, expected_snapshot in expected_snapshots.items():
                got = snapshots.get(name)
                if (not isinstance(got, dict) or not isinstance(expected_snapshot, dict) or
                        any(got.get(field) != expected_snapshot.get(field)
                            for field in ('file', 'bytes', 'sha256'))):
                    return False
        expected = ('POSITIVE_VERIFIED_SOURCE_REPORTED' if variant == 'positive' else
                    'EXPECTED_CALLEE_CONTRACT_REJECTION' if variant.startswith('callee-') else
                    'EXPECTED_SAME_SITE_TYPED_FAILURE')
        expected_bound = ('POSITIVE_VERIFIED_SOURCE_REPORTED' if variant == 'positive'
                          else 'POSITIVE_FAILED')
        if (row.get('classification') != expected or
                row.get('bound_verdict') != expected_bound or
                (stage['exit'] == 0) != (variant == 'positive')):
            return False
        if variant != 'positive':
            target = validation['targets'].get(variant)
            observed = row.get('diagnostic_target_observation')
            physical_diagnostic = _current_log_diagnostic(log_bytes)
            if (not isinstance(target, dict) or
                    row.get('expected_diagnostic_target') != target or
                    not isinstance(observed, dict) or
                    observed.get('variant') != variant or
                    observed.get('current_build_id') != canonical_build_id or
                    observed.get('log_path') != expected_log_path or
                    observed.get('matches_first_and_only_error') is not True or
                    observed.get('provenance_status') !=
                        'CALLER_DECLARED_PRIOR_OBSERVATION_CONSISTENT_NOT_AUTHENTICATED' or
                    observed.get('accepted') is not False or
                    observed.get('proof_credit') is not False or
                    observed.get('target') != {key: target.get(key) for key in
                        ('file', 'line', 'start_column', 'end_column', 'message')} or
                    observed.get('log_sha256') != row.get('log_sha256') or
                    not _sha256(row.get('log_sha256')) or
                    physical_diagnostic != {
                        'diagnostic_line': observed.get('diagnostic_line'),
                        **{key: target.get(key) for key in
                           ('file', 'line', 'start_column', 'end_column', 'message')},
                    }):
                return False
    return True


def read_record(path: Path):
    if not path.is_file():
        return 'missing', None
    try:
        value = json.loads(path.read_text())
    except (OSError, ValueError) as exc:
        return 'unreadable', {'error': str(exc)}
    return ('null' if value is None else
            'object' if isinstance(value, dict) else 'wrong-type'), value


def audit(args, *, base_audit=None):
    if base_audit is None:
        path = Path(__file__).with_name('select-callee-r20.py')
        if hashlib.sha256(path.read_bytes()).hexdigest() != BASE_SHA256:
            raise RuntimeError('R21 proof audit base pin differs')
        spec = importlib.util.spec_from_file_location('r21_proof_audit_base', path)
        if spec is None or spec.loader is None:
            raise RuntimeError('R21 proof audit base unavailable')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        base_audit = module.audit
    base = base_audit(args)
    if not isinstance(base, dict):
        raise RuntimeError('R21 proof base audit returned wrong type')
    status, proof = read_record(args.evidence /
        'cases/r21-fractional-proof/r21-fractional-proof.json')
    record = dict(base)
    record.update(schema='r21-fractional-proof-audit-v1',
                  base_audit_schema=base.get('schema'),
                  fractional_proof_status=status, fractional_proof=proof,
                  accepted=False, verification_accepted=False, proof_credit=False)
    record['evidence_complete'] = (
        base.get('evidence_complete') is True and status == 'object' and
        complete_matrix(proof, evidence_root=args.evidence,
                        native_build_id=os.environ.get('CLOUD_BUILD_ID'),
                        native_r24_session_phase_id=os.environ.get(
                            'SORT4_R24_SESSION_PHASE_ID')))
    args.output.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--runner-exit', type=int, required=True)
    parser.add_argument('--failed-stage', required=True)
    audit(parser.parse_args())


if __name__ == '__main__':
    main()
