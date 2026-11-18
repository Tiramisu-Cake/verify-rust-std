#!/usr/bin/env python3
"""Check a future publication head against the reviewed source pins; read-only."""

import json
from pathlib import Path
import re
import subprocess
import sys


SKIP = re.compile(
    r"\[(?:skip ci|ci skip|no ci|skip actions|actions skip)\]|skip-checks:\s*true",
    re.IGNORECASE,
)


def check_metadata(pins, head, tree, parents, commits):
    """Validate supplied git metadata without creating or publishing a commit."""
    errors = []
    if not re.fullmatch(r"[0-9a-f]{40}", head):
        errors.append("final head must be a full lowercase SHA")
    if head in (pins["candidate"]["sha"], pins["main"]["sha"]):
        errors.append("final head must be a new nonskip sibling of the local candidate")
    if tree != pins["candidate"]["tree"]:
        errors.append("final tree differs from the reviewed candidate")
    if parents != [pins["main"]["sha"]]:
        errors.append("final head must have exactly the reviewed main as its parent")
    if [entry["sha"] for entry in commits] != [head]:
        errors.append("whole main..final range must contain exactly the final sibling")
    if not commits or any(SKIP.search(entry["message"]) for entry in commits):
        errors.append("whole publication range must be present and free of skip directives")
    return errors


def main():
    if len(sys.argv) != 3:
        print("usage: check_push_head.py SOURCE_REPOSITORY FINAL_FULL_SHA", file=sys.stderr)
        return 2
    repo, head = sys.argv[1:]
    if not re.fullmatch(r"[0-9a-f]{40}", head):
        print("final head must be a full lowercase SHA", file=sys.stderr)
        return 2
    pins = json.loads(Path(__file__).with_name("SOURCE-PINS.json").read_text())

    def git(*args):
        return subprocess.check_output(["git", "-C", repo, *args], text=True).strip()

    try:
        candidate = pins["candidate"]["sha"]
        if git("show", "-s", "--format=%T", candidate) != pins["candidate"]["tree"]:
            raise ValueError("candidate tree binding changed")
        if git("show", "-s", "--format=%P", candidate) != pins["main"]["sha"]:
            raise ValueError("candidate parent binding changed")
        tree = git("show", "-s", "--format=%T", head)
        parents = git("show", "-s", "--format=%P", head).split()
        shas = git("rev-list", f'{pins["main"]["sha"]}..{head}').split()
        commits = [{"sha": sha, "message": git("show", "-s", "--format=%B", sha)} for sha in shas]
        errors = check_metadata(pins, head, tree, parents, commits)
    except (subprocess.CalledProcessError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1
    print(json.dumps({"head": head, "tree": tree, "parents": parents, "range": shas,
                      "errors": errors, "status": "REJECT" if errors else "MATCH",
                      "authorization_granted": False}, indent=2))
    return bool(errors)


if __name__ == "__main__":
    sys.exit(main())
