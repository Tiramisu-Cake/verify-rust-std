#!/usr/bin/env python3
"""Reproduce the first two stages of Select's overlay base (Git apply only).

Purpose: the base on which a Network P1 overlay-admission patch must be
written (r4/SELECT-REQUESTS.md). No build, no proof tool, no runner execution.
Usage: reproduce-base.py VERIFAST_REPO SELECT_COMMIT OUT_DIR  (OUT_DIR must not exist)
Stages, as in Select's run-o26-refresh.sh @10e13a41:
  1. O26-PROFILE-MANIFEST.json patches_in_application_order on f76012fb
     -> `git diff` SHA256 6c4c5a77... (frozen20 applied diff)
  2. O26-REFRESH-PROFILE.json refresh_patches
     -> vf_mir_translator.ml SHA256 0862e635...
Stage 3 (A1 overlays, a1-tool-r17.py reconstruct) is NOT reproduced here.
"""
import hashlib
import io
import json
import subprocess
import sys
import tarfile
from pathlib import Path

TOOL = 'f76012fb518703b1d98e243ac4f487f16877cfcb'
FROZEN20 = '6c4c5a7708af3bdec585abd308d37383a7de522a1aaecf2c01e1f94181324c25'
REFRESHED_TRANSLATOR = '0862e635075edd06a827c567710a3e1125ac03aa122e95149db755a1fddce48a'
TR = 'src/rust_frontend/vf_mir_translator/vf_mir_translator.ml'
HERE = Path(__file__).resolve().parent


def sh(*args, **kw):
    return subprocess.run(args, check=True, capture_output=True, **kw).stdout


def need(ok, why):
    if not ok:
        raise SystemExit('P1 BASE REFUSED: ' + why)


def main():
    need(len(sys.argv) == 4, 'usage: reproduce-base.py VERIFAST_REPO SELECT_COMMIT OUT_DIR')
    repo, select, out = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
    need(not out.exists(), 'OUT_DIR must not exist')
    src = out / 'src'
    src.mkdir(parents=True)
    tarfile.open(fileobj=io.BytesIO(sh('git', '-C', str(repo), 'archive', TOOL))).extractall(src, filter='data')
    sh('git', '-C', str(src), 'init', '-q')
    sh('git', '-C', str(src), 'add', '-A')
    sh('git', '-C', str(src), '-c', 'user.email=n@l', '-c', 'user.name=network', 'commit', '-qm', 'f76012fb')
    show = lambda rel: sh('git', '-C', str(HERE), 'show', f'{select}:research/challenge-8/{rel}')
    rows = []
    for stage, manifest, key in ((1, 'overnight-linkage/O26-PROFILE-MANIFEST.json', 'patches_in_application_order'),
                                 (2, 'overnight-assume-actual/O26-REFRESH-PROFILE.json', 'refresh_patches')):
        for row in json.loads(show(manifest))[key]:
            patch = show(row['path'])
            need(hashlib.sha256(patch).hexdigest() == row['sha256'], 'patch SHA ' + row['path'])
            subprocess.run(['git', '-C', str(src), 'apply', '-'], input=patch, check=True)
            rows.append({'stage': stage, 'path': row['path'], 'sha256': row['sha256']})
        if stage == 1:
            need(hashlib.sha256(sh('git', '-C', str(src), 'diff')).hexdigest() == FROZEN20, 'frozen20 diff SHA')
    translator = hashlib.sha256((src / TR).read_bytes()).hexdigest()
    need(translator == REFRESHED_TRANSLATOR, 'refreshed translator SHA')
    record = {'tool': TOOL, 'select_commit': select, 'patches': rows, 'frozen20_diff_sha256': FROZEN20,
              'refreshed_translator_sha256': translator, 'stage3_a1_overlays': 'NOT_REPRODUCED'}
    (out / 'base.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({'patches': len(rows), 'refreshed_translator_sha256': translator}))


if __name__ == '__main__':
    main()
