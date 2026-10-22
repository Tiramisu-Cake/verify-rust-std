#!/usr/bin/env python3
"""Preserve R21 fractional proof observations without granting acceptance."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

BASE_SHA256 = '83d2d0940fcb255a58b97db8d6161ec3b39660a62905f89a33f926a96d3099ba'
VARIANTS = ('positive', 'omit-selected-own', 'omit-unselected-own',
            'no-retained-half', 'callee-false-normal', 'callee-owner-duplicate',
            'callee-owner-loss', 'callee-thread-duplicate')


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
    for variant in VARIANTS:
        row = rows[variant]
        if not isinstance(row, dict):
            return False
        stage = row.get('stage')
        if (row.get('status') != 'COMPLETE' or
                row.get('source_intact_after_stages') is not True or
                row.get('normal_unwind_nested_drop_gates') is not True or
                not isinstance(stage, dict) or stage.get('status') != 'RAN' or
                type(stage.get('exit')) is not int):
            return False
        for key in ('preflight_capture_check', 'postflight_capture_check'):
            if not isinstance(row.get(key), dict) or row[key].get('complete') is not True:
                return False
        expected = ('POSITIVE_VERIFIED_SOURCE_REPORTED' if variant == 'positive' else
                    'EXPECTED_CALLEE_CONTRACT_REJECTION' if variant.startswith('callee-') else
                    'EXPECTED_SAME_SITE_FINAL_SELECT_FAILURE')
        if (row.get('classification') != expected or
                (stage['exit'] == 0) != (variant == 'positive')):
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
