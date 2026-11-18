#!/usr/bin/env python3
"""Read-only gate for the coordinator's exact proposed publication head."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / 'source/tests/script-based-pre/stub-contract-confirm'))
import final_head


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('repository', type=Path)
    parser.add_argument('final_sha')
    parser.add_argument('ref')
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--derive-request', action='store_true')
    mode.add_argument('--request', help='Exact expected canonical request SHA256 for the proposed final head')
    args = parser.parse_args()
    try:
        pins = json.loads((HERE / 'PINS.json').read_text())
        report = final_head.check(args.repository, args.final_sha, args.ref, args.request, pins)
        print(json.dumps(report, indent=2, sort_keys=True))
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
