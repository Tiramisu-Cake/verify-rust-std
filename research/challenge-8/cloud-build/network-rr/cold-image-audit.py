#!/usr/bin/env python3
"""Create a non-credit cold-image diagnostic audit from synthetic-safe inputs."""

import argparse
import json
from pathlib import Path
import re

REGISTRY = 'us-central1-docker.pkg.dev/smallsort-ci/smallsort-tools/refinedrust-g1'
RR_LOCK_SHA256 = 'b66b9e281478be8263eab9ba210964cdd8f1db92535b7b81305f50dea03682aa'
MISSING = object()


def summarize(status, receipt, build_id):
    result = {
        'accepted': False,
        'classification': 'INCONCLUSIVE',
        'diagnostic_complete': False,
        'proof_credit': False,
        'lane': 'network-rr-g1',
        'stage': 'cold-image',
        'build_id': build_id,
        'evidence_root': 'allprooflogs',
    }
    if not isinstance(status, dict):
        result['failure_class'] = 'wrong-type-status'
        return result
    code = status.get('exit_code')
    if type(code) is not int:
        result['failure_class'] = 'missing-exit-code' if 'exit_code' not in status else 'wrong-type-exit-code'
        return result
    result['stage_exit_status'] = code
    if status.get('stage') != 'cold-image':
        result['failure_class'] = 'source-stage-mismatch'
        return result
    if status.get('build_id') != build_id:
        result['failure_class'] = 'build-id-mismatch'
        return result
    state = status.get('state', MISSING)
    if state == 'NOT_RUN':
        result['failure_class'] = 'not-run'
        return result
    if code == 124:
        result['failure_class'] = 'timeout'
        return result
    if code != 0:
        result['failure_class'] = 'stage-error'
        return result
    if state is MISSING:
        result['failure_class'] = 'missing-state'
        return result
    if state is None:
        result['failure_class'] = 'null-state'
        return result
    if not isinstance(state, str):
        result['failure_class'] = 'wrong-type-state'
        return result
    if state != 'COMPLETE':
        result['failure_class'] = 'unexpected-state'
        return result
    if receipt is MISSING:
        result['failure_class'] = 'missing-receipt'
        return result
    if receipt is None:
        result['failure_class'] = 'null-receipt'
        return result
    if not isinstance(receipt, dict):
        result['failure_class'] = 'wrong-type-receipt'
        return result
    digest = receipt.get('image_digest')
    if (receipt.get('schema') != 'refinedrust-g1-registry-image-receipt-v1' or
            receipt.get('stage') != 'cold-image' or receipt.get('build_id') != build_id):
        result['failure_class'] = 'source-stage-mismatch'
        return result
    if not isinstance(digest, str) or not re.fullmatch(re.escape(REGISTRY) + r'@sha256:[0-9a-f]{64}', digest):
        result['failure_class'] = 'invalid-registry-digest'
        return result
    for field in ('internal_receipt_sha256', 'cargo_lock_sha256'):
        value = receipt.get(field)
        if not isinstance(value, str) or not re.fullmatch(r'[0-9a-f]{64}', value):
            result['failure_class'] = 'partial-receipt'
            return result
    if receipt['cargo_lock_sha256'] != RR_LOCK_SHA256:
        result['failure_class'] = 'cargo-lock-mismatch'
        return result
    result.update(classification='COLD_IMAGE_BUILT', diagnostic_complete=True,
                  failure_class='none', image_digest=digest)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--status', type=Path, required=True)
    parser.add_argument('--receipt', type=Path, required=True)
    parser.add_argument('--build-id', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        status = json.loads(args.status.read_text())
    except (OSError, ValueError):
        status = None
    try:
        receipt = json.loads(args.receipt.read_text())
    except OSError:
        receipt = MISSING
    except ValueError:
        receipt = None
    args.output.write_text(json.dumps(summarize(status, receipt, args.build_id),
                                     indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
