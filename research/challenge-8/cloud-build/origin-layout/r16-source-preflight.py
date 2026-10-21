#!/usr/bin/env python3
"""Static R16 registration and committed-source closure gate; no Cloud calls."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
LOCAL_TEST_PATHS = {
    "research/challenge-8/cloud-build/origin-layout/r16-phase-service-test.py",
    "research/challenge-8/cloud-build/origin-layout/r16-source-preflight-service-test.py",
}


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(ROOT), *args], stderr=subprocess.PIPE)


def read_worktree(path: str) -> bytes:
    target = ROOT / path
    if target.is_symlink() or not target.is_file():
        raise ValueError(f"R16 input unavailable: {path}")
    return target.read_bytes()


def validate_local_tests() -> None:
    for path in sorted(LOCAL_TEST_PATHS):
        if git("show", f"HEAD:{path}") != read_worktree(path):
            raise ValueError(f"R16 local service test differs from selected source: {path}")


def validate_registration() -> str:
    sys.path.insert(0, str(HERE.parents[0]))
    import control

    commit = git("rev-parse", "HEAD").decode().strip()
    control.r16_validate_sources(control.R16_PROBE_SOURCE, commit)
    ledger = json.loads(git("show", f"{commit}:{control.R16_LEDGER_PATH}"))
    expected = {
        "phase": control.R16_PHASE,
        "owner": "merge",
        "authorization_model": "bounded-cloud-budget",
        "status": "AUTHORIZED",
        "allowed_lanes": ["merge"],
        "ceiling_build_seconds": 3600,
        "used_build_seconds": 0,
        "remaining_build_seconds": 3600,
        "max_builds": None,
        "max_timeout_seconds": 1200,
        "builds": [],
        "active_build": None,
        "start_utc": "2026-10-21T16:08:24Z",
        "main_deadline_utc": "2026-10-21T18:08:24Z",
        "deadline_utc": "2026-10-21T18:38:24Z",
        "carryover_allowed": False,
        "publication_gate_path": control.R14_GATE_PATH,
    }
    if any(ledger.get(key) != value for key, value in expected.items()):
        raise ValueError("R16 selected phase account differs from authorization")
    return commit


def main() -> None:
    try:
        validate_local_tests()
        commit = validate_registration()
        print(f"R16 source preflight PASS for {commit}; no compiler/proof/Cloud")
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError, SystemExit) as error:
        print(f"R16 source preflight FAIL: {error}", file=sys.stderr)
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
