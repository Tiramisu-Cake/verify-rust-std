#!/usr/bin/env python3
"""Hosted source generation only; run before downloading/building VeriFast."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


def main() -> None:
    if tuple(os.getenv(k) for k in (
            "GITHUB_ACTIONS", "RUNNER_ENVIRONMENT", "RUNNER_OS")) != (
                "true", "github-hosted", "Linux"):
        raise SystemExit("source preflight requires GitHub-hosted Linux")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    out = args.evidence.resolve()
    if out.exists():
        raise SystemExit("refusing existing source-preflight evidence")
    out.mkdir(parents=True)
    tasks = {
        "owner-nine": [sys.executable,
            str(repo / "research/challenge-8/overnight-assume-actual/prepare.py"),
            "--repo", str(repo), "--out", str(out / "owner-nine")],
        "sort4": [sys.executable,
            str(repo / "research/challenge-8/overnight-callback/prepare-actual-sort4-first-call.py"),
            "--repo-root", str(repo), "--output", str(out / "sort4"),
            "--prepare-only"],
    }
    rows = {}
    for name, command in tasks.items():
        try:
            result = subprocess.run(command, cwd=repo, capture_output=True,
                                    timeout=60, check=False)
        except subprocess.TimeoutExpired as exc:
            result = subprocess.CompletedProcess(command, 124, exc.stdout or b"",
                                                  exc.stderr or b"source preflight timed out")
        except OSError as exc:
            result = subprocess.CompletedProcess(command, 2, b"", str(exc).encode())
        (out / f"{name}.log").write_bytes(result.stdout + result.stderr)
        source_files = sorted((out / name).rglob("lib.rs"))
        rows[name] = {
            "exit": result.returncode, "command": command,
            "classification": "SOURCE_GENERATION_AND_EXACT_STRIP_PASS"
                if result.returncode == 0 else "PREPARATION_FAILED",
            "source_sha256": {
                str(p.relative_to(out)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in source_files},
            "verifier_or_compiler_invoked": False,
        }
        print(json.dumps({"component": name, **rows[name]}), flush=True)
    (out / "summary.json").write_text(json.dumps({
        "classification": "HOSTED_SOURCE_PREFLIGHT_ONLY",
        "verifier_build_started": False, "components": rows,
        "all_passed": all(row["exit"] == 0 for row in rows.values()),
    }, indent=2) + "\n")
    # Components remain independently reviewable even if one fails. The runner
    # reads their statuses and invokes only the successfully prepared routes.


if __name__ == "__main__":
    main()
