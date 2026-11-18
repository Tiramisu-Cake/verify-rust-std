"""Independent invocation of existing static source preflight, no compiler."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import sys
import time

CONTROL = Path('/root/kani-ch8-s3-1-r2-control-w13')
SOURCE = Path('/root/verify-rust-std-ch8-s3-1-final-w13')
TOOL = Path('/root/kani-upstream-ch8-s1')
OUT = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(CONTROL / 'ch8-s1-control'))
import runner as r


def main():
    target = OUT / 'source-preflight.json'
    assert not target.exists()
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    start = time.monotonic()
    assert r.git(CONTROL, 'rev-parse', 'HEAD') == 'cb63033ffcde918f4341146e56373476b8eeb569'
    assert not r.git(CONTROL, 'status', '--porcelain=v1')
    request = r.load_request()
    source = r.verify_source(SOURCE, TOOL, request, prebuild=True)
    record = dict(state='STATIC_PASS', method='actual runner.verify_source(prebuild=True)',
                  started_utc=started, ended_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  elapsed_seconds=time.monotonic() - start, source=source,
                  request_sha256=r.sha256(r.REQUEST_PATH),
                  control_sha=r.git(CONTROL, 'rev-parse', 'HEAD'),
                  native='NOT_RUN', CI='NOT_RUN', proof_credit='NONE')
    target.write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(dict(state='STATIC_PASS', elapsed_seconds=record['elapsed_seconds'])))


if __name__ == '__main__':
    main()
