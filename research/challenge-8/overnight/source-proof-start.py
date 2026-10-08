#!/usr/bin/env python3
"""Start checking a prepared actual sort4 unit; report barriers, never PASS."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time


def main():
    if (os.getenv("GITHUB_ACTIONS"), os.getenv("RUNNER_ENVIRONMENT"),
            os.getenv("RUNNER_OS")) != ("true", "github-hosted", "Linux"):
        raise SystemExit("hosted Linux required")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool-home", type=Path, required=True)
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--deadline-epoch", type=int, required=True)
    args = parser.parse_args()
    source = args.fixture / "verified/lib.rs"
    original = args.fixture / "original/lib.rs"
    if not source.is_file() or not original.is_file():
        raise SystemExit("prepared source pair missing; no proof started")
    record = json.loads((args.fixture / "fixture.json").read_text())
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    if (sha(source), sha(original)) != (
            record["verified_sha256"], record["original_sha256"]):
        raise SystemExit("source pair changed before proof start")
    env = {k: v for k, v in os.environ.items() if not k.startswith("SORT4_")}
    env["SORT4_SELECT_PROFILE"] = "experimental-s6-26.10-v1"
    env["RUSTUP_TOOLCHAIN"] = "nightly-2026-09-25"
    command = [str(args.tool_home / "bin/verifast"), "-rustc_args",
               "--edition 2021", "-verbose", "1", "verified/lib.rs"]
    seconds = min(100, args.deadline_epoch - int(time.time()) - 15)
    if seconds <= 0:
        raise SystemExit("proof-start deadline expired")
    result = subprocess.run(command, cwd=args.fixture, env=env,
                            capture_output=True, timeout=seconds, check=False)
    log = result.stdout + result.stderr
    (args.fixture / "proof-start.log").write_bytes(log)
    text = log.decode(errors="replace")
    summary = {
        "classification": "ACTUAL_FULL_SOURCE_CHECK_DIAGNOSTIC",
        "actual_sort4_proved": False, "semantic_adapter_enabled": False,
        "exit": result.returncode,
        "actual_body_started": "Verifying function 'sort4_stable'" in text,
        "first_error": next((x for x in text.splitlines()
                             if ": error:" in x or x.startswith("Fatal error:")), None),
        "source_integrity": (sha(source), sha(original)) == (
            record["verified_sha256"], record["original_sha256"]),
        "command": command,
    }
    (args.fixture / "proof-start-summary.json").write_text(json.dumps(
        summary, indent=2) + "\n")
    print(json.dumps(summary), flush=True)


if __name__ == "__main__":
    main()
