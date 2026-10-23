#!/usr/bin/env python3
"""Preserve R21 fractional proof observations without granting acceptance."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import uuid

BASE_SHA256 = '83d2d0940fcb255a58b97db8d6161ec3b39660a62905f89a33f926a96d3099ba'
VARIANTS = ('positive', 'omit-selected-own', 'omit-unselected-own',
            'no-retained-half', 'callee-false-normal', 'callee-owner-duplicate',
            'callee-owner-loss', 'callee-thread-duplicate')
_SHA256 = re.compile(r'^[0-9a-f]{64}$')
TARGET_HELPER_SHA256 = '5c51ae49766ec7f8dda5ac548555773bce34398462376a4ff56653d6bef91e93'


def _sha256(value):
    return isinstance(value, str) and _SHA256.fullmatch(value) is not None


def complete_matrix(proof):
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
            not _sha256(dependencies.get('target_map_sha256')) or
            not _sha256(dependencies.get('target_map_canonical_sha256')) or
            dependencies.get('target_map_canonical_sha256') !=
                proof.get('diagnostic_target_map_sha256') or
            not _sha256(dependencies.get('tool_spec_sha256')) or
            dependencies.get('target_helper_sha256') != TARGET_HELPER_SHA256):
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
                stage.get('source_unchanged') is not True or
                stage.get('source_before') != expected_sources or
                stage.get('source_after') != expected_sources):
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
        if (row.get('classification') != expected or
                (stage['exit'] == 0) != (variant == 'positive')):
            return False
        if variant != 'positive':
            target = validation['targets'].get(variant)
            observed = row.get('diagnostic_target_observation')
            if (not isinstance(target, dict) or
                    row.get('expected_diagnostic_target') != target or
                    not isinstance(observed, dict) or
                    observed.get('variant') != variant or
                    observed.get('matches_first_and_only_error') is not True or
                    observed.get('provenance_status') !=
                        'CALLER_DECLARED_PRIOR_OBSERVATION_CONSISTENT_NOT_AUTHENTICATED' or
                    observed.get('accepted') is not False or
                    observed.get('proof_credit') is not False or
                    observed.get('target') != {key: target.get(key) for key in
                        ('file', 'line', 'start_column', 'end_column', 'message')} or
                    observed.get('log_sha256') != row.get('log_sha256') or
                    not _sha256(row.get('log_sha256'))):
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
        complete_matrix(proof))
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
