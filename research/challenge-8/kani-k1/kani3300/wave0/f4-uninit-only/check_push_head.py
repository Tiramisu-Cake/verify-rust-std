#!/usr/bin/env python3
"""Read-only identity/skip gate for an owner-created future native push head."""
import json
from pathlib import Path
import re
import subprocess
import sys

PACKAGE = Path(__file__).resolve().parent
SKIP = re.compile(r'\[(?:skip ci|ci skip|no ci|skip actions|actions skip)\]|^skip-checks\s*:\s*true\s*$',
                  re.IGNORECASE | re.MULTILINE)


def check(source_dir, final):
    pins = json.loads((PACKAGE / 'SOURCE-PINS.json').read_text())

    def git(*args):
        return subprocess.check_output(['git', *args], cwd=source_dir).decode().strip()

    candidate = pins['source']
    final = git('rev-parse', '--verify', final + '^{commit}')
    assert git('rev-parse', candidate + '^{tree}') == pins['tree'], 'candidate tree mismatch'
    assert git('show', '-s', '--format=%P', candidate) == pins['parent'], 'candidate parent mismatch'
    assert git('rev-parse', final + '^{tree}') == pins['tree'], 'final tree mismatch'
    assert git('show', '-s', '--format=%P', final) == pins['parent'], 'final must be a direct sibling with parent b5'
    commits = git('rev-list', pins['parent'] + '..' + final).splitlines()
    assert commits == [final], 'unexpected commits in pushed b5..HEAD range'
    for commit in commits:
        assert not SKIP.search(git('show', '-s', '--format=%B', commit)), 'skip directive in pushed range'
    assert final != candidate, 'publish the owner-created no-skip sibling'
    return dict(status='IDENTITY_AND_SKIP_GATE_PASS', reviewed_source=candidate,
                trigger_sha=final, trigger_tree=pins['tree'], parent=pins['parent'],
                pushed_range=commits, authorization='SEPARATE_REVIEW_AND_OWNER_GO_REQUIRED')


if __name__ == '__main__':
    try:
        assert len(sys.argv) == 3, 'usage: check_push_head.py SOURCE_DIR FUTURE_FINAL_SHA'
        print(json.dumps(check(sys.argv[1], sys.argv[2]), indent=2))
    except (AssertionError, subprocess.CalledProcessError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
