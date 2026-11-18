#!/usr/bin/env python3
"""Read-only identity gate for a future nonskip repair sibling above published6f."""

import json
from pathlib import Path
import re
import subprocess
import sys


SKIP = re.compile(r'\[(?:skip ci|ci skip|no ci|skip actions|actions skip)\]|'
                  r'skip-checks:\s*true', re.IGNORECASE)


def check_metadata(pins, head, tree, parents, commits):
    errors = []
    candidate = pins['candidate']
    base = pins['published_failed_base']
    if not re.fullmatch(r'[0-9a-f]{40}', head):
        errors.append('full lowercase final SHA required')
    if head in (candidate['sha'], base['sha'], pins['main']['sha']):
        errors.append('new nonskip repair sibling required')
    if tree != candidate['tree']:
        errors.append('tree differs from reviewed repair candidate')
    if parents != [base['sha']]:
        errors.append('sole published6f parent required')
    if [c['sha'] for c in commits] != [base['sha'], head]:
        errors.append('complete main..final range must be published6f then final')
    if not commits or any(SKIP.search(c['message']) for c in commits):
        errors.append('whole main..final range must be present and nonskip')
    if candidate['sha'] in [c['sha'] for c in commits]:
        errors.append('skipped candidate must stay outside published range')
    return errors


def main():
    if len(sys.argv) != 3 or not re.fullmatch(r'[0-9a-f]{40}', sys.argv[2]):
        print('usage: check_push_head.py SOURCE_REPO FINAL_FULL_SHA', file=sys.stderr)
        return 2
    repo, head = sys.argv[1:]
    pins = json.loads(Path(__file__).with_name('SOURCE-PINS.json').read_text())

    def git(*args):
        return subprocess.check_output(['git', '-C', repo, *args], text=True).strip()

    try:
        for key in ('candidate', 'published_failed_base', 'main'):
            obj = pins[key]
            if git('show', '-s', '--format=%T', obj['sha']) != obj['tree']:
                raise ValueError(key + ' tree binding mismatch')
            if git('show', '-s', '--format=%P', obj['sha']) != obj['parent']:
                raise ValueError(key + ' parent binding mismatch')
        tree = git('show', '-s', '--format=%T', head)
        parents = git('show', '-s', '--format=%P', head).split()
        shas = git('rev-list', '--reverse', pins['main']['sha'] + '..' + head).split()
        commits = [{'sha': sha, 'message': git('show', '-s', '--format=%B', sha)} for sha in shas]
        errors = check_metadata(pins, head, tree, parents, commits)
    except (ValueError, subprocess.CalledProcessError) as error:
        print(json.dumps({'status': 'REJECT', 'error': str(error), 'authorization_granted': False}))
        return 1
    print(json.dumps({'status': 'REJECT' if errors else 'MATCH', 'head': head,
                      'tree': tree, 'parents': parents, 'range': shas,
                      'errors': errors, 'authorization_granted': False}, indent=2))
    return bool(errors)


if __name__ == '__main__':
    sys.exit(main())
