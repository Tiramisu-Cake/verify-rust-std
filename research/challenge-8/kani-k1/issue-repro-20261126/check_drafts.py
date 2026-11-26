#!/usr/bin/env python3
"""Compare the repro sources in the control with the code blocks of the two issue drafts.

A draft's code block is the text strictly between the only "```rust" line and the next "```" line,
with one trailing newline. Usage:

    check_drafts.py CONTROL_DIR            # verify, exit 1 on any mismatch
    check_drafts.py CONTROL_DIR --write    # (re)create the files from the drafts, then verify
"""
import hashlib
import sys
from pathlib import Path

DRAFTS = Path("/root/smallsort-pr-drafts")
PAIRS = {
    "bool_order.rs": DRAFTS / "ISSUE-KANI-BOOL-ORDER-DRAFT.md",
    "cast.rs": DRAFTS / "ISSUE-KANI-VV-ARRAY-ELEM-CAST-DRAFT.md",
}


def block(draft):
    lines = draft.read_bytes().split(b"\n")
    starts = [i for i, line in enumerate(lines) if line == b"```rust"]
    if len(starts) != 1:
        raise SystemExit(f"{draft}: expected exactly one ```rust block, found {len(starts)}")
    end = lines.index(b"```", starts[0] + 1)
    return b"\n".join(lines[starts[0] + 1:end]) + b"\n"


def main():
    control = Path(sys.argv[1]).resolve(strict=True)
    write = sys.argv[2:] == ["--write"]
    ok = True
    for name, draft in PAIRS.items():
        expected = block(draft)
        target = control / name
        if write:
            target.write_bytes(expected)
        actual = target.read_bytes()
        same = actual == expected
        ok &= same
        print(f"{'MATCH' if same else 'MISMATCH'} {name} sha256={hashlib.sha256(actual).hexdigest()} "
              f"draft_block_sha256={hashlib.sha256(expected).hexdigest()} bytes={len(actual)} "
              f"draft={draft.name} draft_sha256={hashlib.sha256(draft.read_bytes()).hexdigest()}")
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
