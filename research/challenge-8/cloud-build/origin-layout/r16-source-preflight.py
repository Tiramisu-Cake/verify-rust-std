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


def validate_phase_account(ledger: dict, control) -> None:
    """Check fixed authorization plus typed, fully accounted terminal usage."""
    if type(ledger) is not dict:
        raise ValueError("R16 phase account must be a JSON object")
    expected = {
        "phase": control.R16_PHASE,
        "owner": "merge",
        "authorization_model": "bounded-cloud-budget",
        "status": "AUTHORIZED",
        "allowed_lanes": ["merge"],
        "ceiling_build_seconds": 3600,
        "max_builds": None,
        "max_timeout_seconds": 1200,
        "start_utc": "2026-10-21T16:08:24Z",
        "main_deadline_utc": "2026-10-21T18:08:24Z",
        "deadline_utc": "2026-10-21T18:38:24Z",
        "carryover_allowed": False,
        "publication_gate_path": control.R14_GATE_PATH,
        "authorization": "CURRENT-TASK R16: autonomous source-preserving caller unsize/lifetime and actual insert_tail/CURRENT proof; independent Luna HIGH review and Cloud regressions; fresh3600 no carry.",
    }
    if any(ledger.get(key) != value for key, value in expected.items()):
        raise ValueError("R16 selected phase account differs from authorization")
    ceiling = expected["ceiling_build_seconds"]
    used = ledger.get("used_build_seconds")
    remaining = ledger.get("remaining_build_seconds")
    builds = ledger.get("builds")
    if (type(used) is not int or type(remaining) is not int or
            not 0 <= used <= ceiling or remaining != ceiling - used or
            type(builds) is not list or "active_build" not in ledger or
            ledger["active_build"] is not None):
        raise ValueError("R16 phase budget/accounting fields are malformed or unresolved")

    total = 0
    for item in builds:
        build_status = item.get("status") if type(item) is dict else None
        if (type(item) is not dict or item.get("owner") != "merge" or
                item.get("phase_id") != control.R16_PHASE or
                not isinstance(build_status, str) or build_status not in control.TERMINAL or
                item.get("accounted") is not True or
                not isinstance(item.get("build_id"), str) or not item.get("build_id") or
                type(item.get("build_seconds")) is not int or item["build_seconds"] < 0):
            raise ValueError("R16 build entry is not terminal and fully accounted")
        total += item["build_seconds"]
    if total != used:
        raise ValueError("R16 used seconds do not equal accounted terminal builds")


def validate_registration() -> str:
    sys.path.insert(0, str(HERE.parents[0]))
    import control

    commit = git("rev-parse", "HEAD").decode().strip()
    control.r16_validate_sources(control.R16_PROBE_SOURCE, commit)
    ledger = json.loads(git("show", f"{commit}:{control.R16_LEDGER_PATH}"))
    validate_phase_account(ledger, control)
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
