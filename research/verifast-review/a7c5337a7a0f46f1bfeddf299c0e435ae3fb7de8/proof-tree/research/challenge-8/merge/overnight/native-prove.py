#!/usr/bin/env python3
"""Hosted-only independent real C/C++ baseline checks with strict body gates."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent

def sha(data):
    return hashlib.sha256(data).hexdigest()

def gate(status, log, unchanged, name):
    visited = re.findall(r"^\s*\d+(?:\.\d+)?s: .*: Verifying function '([^']+)'$", log, re.M)
    return (status == 0 and unchanged and visited == [name] and
            'error:' not in log and 'Dead code' not in log and
            'Executing statement' in log and 'Executing return statement' in log and
            'Leak check.' in log and
            re.search(r"0 errors found \(\d+ statements verified\)\s*$", log) is not None)

def main():
    if (os.environ.get('GITHUB_ACTIONS') != 'true' or
        os.environ.get('RUNNER_ENVIRONMENT') != 'github-hosted' or
        os.environ.get('GITHUB_REF') != 'refs/heads/overnight/merge-26.10'):
        raise RuntimeError('native proofs require own hosted Actions branch')
    parser = argparse.ArgumentParser()
    parser.add_argument('--tool-home', type=Path, required=True)
    parser.add_argument('--evidence', type=Path, required=True)
    args = parser.parse_args()
    args.evidence.mkdir(exist_ok=False)
    rows = {}
    for extension, name in [('c', 'overnight_c_arithmetic_identity'),
                            ('cpp', 'overnight_cpp_arithmetic_identity(int)')]:
        original = HERE / ('baseline.' + extension)
        data = original.read_bytes()
        path = args.evidence / original.name
        path.write_bytes(data)
        argv = ['timeout', '--signal=TERM', '--kill-after=5s', '60s',
                str(args.tool_home / 'bin/verifast'), '-c', '-verbose', '1', str(path)]
        result = subprocess.run(argv, capture_output=True, text=True)
        log = result.stdout + result.stderr
        (args.evidence / (extension + '.log')).write_text(log)
        unchanged = path.read_bytes() == data and original.read_bytes() == data
        passed = gate(result.returncode, log, unchanged, name)
        controls = {
            'status': not gate(1, log, True, name),
            'source': not gate(0, log, False, name),
            'other_body': not gate(0, log, True, name + '_wrong'),
            'error': not gate(0, log + '\nerror: test\n', True, name),
            'dead': not gate(0, log + '\nDead code\n', True, name),
            'no_return': not gate(0, log.replace('Executing return statement', 'removed'), True, name),
            'no_leak': not gate(0, log.replace('Leak check.', 'removed'), True, name),
        }
        rows[extension] = dict(accepted=passed and all(controls.values()),
            status=result.returncode, command=argv, source_sha256=sha(data),
            source_unchanged=unchanged, log_sha256=sha(log.encode()),
            expected_body=name, controls=controls)
        print(extension + ': ' + ('PASS' if rows[extension]['accepted'] else 'INCONCLUSIVE'), flush=True)
        (args.evidence / 'results.json').write_text(json.dumps(rows, indent=2) + '\n')
    return 0 if all(row['accepted'] for row in rows.values()) else 1

if __name__ == '__main__':
    raise SystemExit(main())
