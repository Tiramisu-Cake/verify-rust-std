#!/usr/bin/env python3
"""Preserve R21 fractional proof observations without granting acceptance."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

BASE_SHA256 = '83d2d0940fcb255a58b97db8d6161ec3b39660a62905f89a33f926a96d3099ba'


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
        proof.get('schema') == 'r21-fractional-classified-proof-v1' and
        proof.get('complete') is True and proof.get('accepted') is False and
        proof.get('proof_credit') is False)
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
