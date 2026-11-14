#!/usr/bin/env python3
"""Build a local git-apply delta from exact Gate B-prime0c1 files plus full-export/.

This reads immutable git objects with `git show`; it never checks out or edits
that repository and performs no network operation.
"""
from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

BASE_COMMIT = "0c1cc8a7d05184044d496b01f5ed41cebfde0cac"
BASE_TREE = "cbb04807c711a9d1bad2ac2dbe1f77538d5658b0"
OLD_PATHS = [
    ".github/workflows/kani3300-replay.yml",
    "scripts/kani3300-replay/REPLAY-CI-OVERLAY.json",
    "scripts/kani3300-replay/c1-source-binding.json",
    "scripts/kani3300-replay/gateb-prime-test-only.patch",
    "scripts/kani3300-replay/replay.py",
    "scripts/kani3300-replay/CI-REQUEST.json",
    "scripts/kani3300-replay/test_replay.py",
]


def run(argv: list[str], *, cwd: Path | None = None, check: bool = True) -> bytes:
    p = subprocess.run(argv, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and p.returncode:
        raise RuntimeError(f"{argv!r}: {p.stderr.decode(errors='replace')}")
    return p.stdout


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path("/root/kani-fix-3300-replay-c1-w15"))
    parser.add_argument("--package", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "ci-overlay-delta.patch")
    parser.add_argument("--check", action="store_true", help="verify existing patch and SHA without overwriting them")
    args = parser.parse_args()
    args.output = args.output.resolve()
    repo = args.repo.resolve()
    package = args.package.resolve()
    exported = package / "full-export"
    expected_paths = set(OLD_PATHS) - {
        "scripts/kani3300-replay/c1-source-binding.json",
        "scripts/kani3300-replay/gateb-prime-test-only.patch",
    } | {
        "scripts/kani3300-replay/sel1-source-binding.json",
        "scripts/kani3300-replay/sel1-test-only.patch",
    }
    exported_paths = {str(path.relative_to(exported)) for path in exported.rglob("*") if path.is_file()}
    if exported_paths != expected_paths:
        raise ValueError(f"full-export file inventory mismatch: {sorted(exported_paths)}")
    actual = run(["git", "-C", str(repo), "rev-parse", f"{BASE_COMMIT}^{{tree}}"]).decode().strip()
    if actual != BASE_TREE:
        raise ValueError(f"Gate B-prime base tree mismatch: {actual}")
    with tempfile.TemporaryDirectory(prefix="sel1-replay-delta-") as td:
        temp = Path(td)
        run(["git", "init", "-q", str(temp)])
        for rel in OLD_PATHS:
            data = run(["git", "-C", str(repo), "show", f"{BASE_COMMIT}:{rel}"])
            dst = temp / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(data)
        run(["git", "-C", str(temp), "add", "-A"])
        base_tree = run(["git", "-C", str(temp), "write-tree"]).decode().strip()
        (temp / "scripts/kani3300-replay/c1-source-binding.json").unlink()
        (temp / "scripts/kani3300-replay/gateb-prime-test-only.patch").unlink()
        for src in sorted(exported.rglob("*")):
            if src.is_file():
                dst = temp / src.relative_to(exported)
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, dst)
        run(["git", "-C", str(temp), "add", "-A"])
        patch = run(["git", "-C", str(temp), "-c", "diff.suppressBlankEmpty=true", "diff", "--cached", "--binary", base_tree])
        if not patch:
            raise ValueError("generated overlay delta is empty")
        digest = hashlib.sha256(patch).hexdigest()
        checksum = f"{digest}  {args.output.name}\n"
        if args.check:
            if args.output.read_bytes() != patch:
                raise ValueError("existing overlay delta differs from exact base/full-export")
            if args.output.with_suffix(args.output.suffix + ".sha256").read_text() != checksum:
                raise ValueError("existing overlay delta checksum mismatch")
        else:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_bytes(patch)
            args.output.with_suffix(args.output.suffix + ".sha256").write_text(checksum)
        # Reverse to the exact filtered baseline, then check/apply again, wholly in temp Git.
        check_patch = temp / ".git/check-overlay.patch"
        check_patch.write_bytes(patch)
        run(["git", "-C", str(temp), "apply", "--reverse", "--index", str(check_patch)])
        run(["git", "-C", str(temp), "apply", "--check", str(check_patch)])
        run(["git", "-C", str(temp), "apply", "--index", str(check_patch)])
        for rel in expected_paths:
            if (temp / rel).read_bytes() != (exported / rel).read_bytes():
                raise ValueError(f"applied delta does not reproduce export bytes: {rel}")
        for rel in set(OLD_PATHS) - expected_paths:
            if (temp / rel).exists():
                raise ValueError(f"old overlay file remains: {rel}")
        print(f"{'verified' if args.check else 'wrote'} {args.output} sha256={digest} bytes={len(patch)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
