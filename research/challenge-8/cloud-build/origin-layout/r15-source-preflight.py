#!/usr/bin/env python3
"""Static R15 registration, source-closure, history, and transport gate."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
LOCAL_TEST_PATHS = {
    "research/challenge-8/cloud-build/origin-layout/r15-phase-service-test.py",
    "research/challenge-8/cloud-build/origin-layout/r15-source-preflight-service-test.py",
}


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(ROOT), *args], stderr=subprocess.PIPE)


def read_worktree(path: str) -> bytes:
    target = ROOT / path
    if target.is_symlink() or not target.is_file():
        raise ValueError(f"R15 input unavailable: {path}")
    return target.read_bytes()


def validate_local_tests() -> None:
    for path in sorted(LOCAL_TEST_PATHS):
        if git("show", f"HEAD:{path}") != read_worktree(path):
            raise ValueError(f"R15 local service test differs from selected source: {path}")


def validate_registration() -> str:
    sys.path.insert(0, str(HERE.parents[0]))
    import control

    commit = git("rev-parse", "HEAD").decode().strip()
    control.r15_validate_sources(control.R15_PROBE_SOURCE, commit)
    ledger_raw = git("show", f"{commit}:{control.R15_LEDGER_PATH}")
    ledger = json.loads(ledger_raw)
    if (ledger.get("phase") != control.R15_PHASE or ledger.get("owner") != "merge" or
            ledger.get("status") != "AUTHORIZED" or
            ledger.get("start_utc") != "2026-10-21T14:12:12Z" or
            ledger.get("main_deadline_utc") != "2026-10-21T16:12:12Z" or
            ledger.get("deadline_utc") != "2026-10-21T16:42:12Z" or
            ledger.get("ceiling_build_seconds") != 3600 or
            ledger.get("allowed_lanes") != ["merge"] or
            ledger.get("max_timeout_seconds") != 1200 or
            ledger.get("carryover_allowed") is not False):
        raise ValueError("R15 selected phase account differs from authorization")
    return commit


def main() -> None:
    try:
        validate_local_tests()
        commit = validate_registration()
        print(f"R15 source preflight PASS for {commit}; no compiler/proof/Cloud")
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError, SystemExit) as error:
        print(f"R15 source preflight FAIL: {error}", file=sys.stderr)
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
