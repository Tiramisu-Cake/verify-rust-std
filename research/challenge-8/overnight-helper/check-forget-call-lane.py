#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted full-MIR/first-barrier capture for a checked generic forget call."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
CALLEE_NAME = "checked_forget_generic"
CALLER_NAME = "checked_forget_call_probe"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


CALLEE = load(HERE / "prepare-forget-callee.py", "g1_call_callee")
HELPER = load(HERE / "check-helper.py", "g1_call_runner")
A1 = load(HERE / "prepare-assume-init-2610.py", "g1_call_mir")


def source_pair() -> tuple[bytes, bytes, dict]:
    callee_original, callee_verified, callee_fixture = CALLEE.fixture("positive")
    req = b"req thread_token(?tid) &*& tid == currentThread &*& *frame |-> ?flag;"
    ens = b"ens thread_token(tid) &*& *frame |-> flag;"
    unw = b"on_unwind_ens false;"
    probe = (
        b"\npub unsafe fn checked_forget_call_probe<T>(t: T, frame: *mut bool)\n" +
        CALLEE.G1.ghost(req + b"\n" + ens + b"\n" + unw) +
        b"{\n    unsafe { checked_forget_generic(t); }\n}\n"
    )
    verified = callee_verified + probe
    original = CALLEE.G1.strip_ghost(verified)
    CALLEE.G1.require(original == callee_original +
                      CALLEE.G1.strip_ghost(probe) and
                      verified.count(CALLEE.G1.FORGET_BODY) == 1 and
                      verified.count(b"checked_forget_generic(t);") == 1,
                      "exact generic callee/caller source changed")
    return original, verified, callee_fixture


def write_case(repo: Path, case: Path) -> dict:
    CALLEE.G1.require(os.environ.get("GITHUB_ACTIONS") == "true" and
                      os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted",
                      "G1 call fixture requires GitHub-hosted Actions")
    CALLEE.G1.require(not case.exists(), "refusing to overwrite G1 call case")
    original, verified, callee_fixture = source_pair()
    (case / "original").mkdir(parents=True)
    (case / "verified").mkdir()
    (case / "original/lib.rs").write_bytes(original)
    (case / "verified/lib.rs").write_bytes(verified)
    record = {
        "classification": "GENERIC_CALL_LANE_CAPTURE_ONLY",
        "callee_source_certificate": CALLEE.G1.source_certificate(repo),
        "callee_contract": {
            "pre": "thread_token(?tid) * tid==currentThread",
            "normal": "thread_token(tid)", "unwind": "false",
            "source_target": callee_fixture["target"]},
        "caller_contract": {
            "pre": "thread_token(?tid) * tid==currentThread * *frame|->flag",
            "normal": "thread_token(tid) * *frame|->flag",
            "unwind": "false"},
        "original_sha256": HELPER.digest(original),
        "verified_sha256": HELPER.digest(verified),
        "ghost_strip_identity": True,
        "callee_qualified_in_same_unit": False,
        "actual_safe_forget_linked": False,
    }
    (case / "fixture.json").write_text(json.dumps(
        record, indent=2, sort_keys=True) + "\n")
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool-home", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--compiler-sysroot", required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--deadline-epoch", type=int, required=True)
    args = parser.parse_args()
    HELPER.require((os.environ.get("GITHUB_ACTIONS"),
                    os.environ.get("RUNNER_ENVIRONMENT"),
                    os.environ.get("RUNNER_OS")) ==
                   ("true", "github-hosted", "Linux"),
                   "G1 call lane requires hosted Linux")
    case = args.evidence.resolve()
    write_case(REPO, case)
    os.environ.pop("SORT4_G1_CALL_ROOT", None)
    stages = HELPER.run_case(case, args, prove=True)
    capture = {}
    for mode in ("normal", "readonly"):
        if stages.get(f"{mode}-decode", {}).get("exit") != 0:
            continue
        decoded = (case / f"{mode}-mir.txt").read_text(errors="strict")
        capture[mode] = {}
        for name in (CALLEE_NAME, CALLER_NAME):
            defpath, body = A1.complete_function_record(decoded, name)
            (case / f"{mode}-{name}-full-mir.txt").write_text(body)
            capture[mode][name] = {
                "defpath": defpath, "full_mir_sha256": HELPER.digest(body.encode()),
                "full_mir_bytes": len(body.encode()),
                "review_status": "CAPTURE_ONLY"}
    verified = (case / "verified/lib.rs").read_bytes()
    original = (case / "original/lib.rs").read_bytes()
    log_path = case / "full-verification.log"
    log = log_path.read_text(errors="replace") if log_path.exists() else ""
    errors = HELPER.error_info(log)
    result = {
        "classification": "GENERIC_CALL_LANE_DIAGNOSTIC_ONLY",
        "component_accepted": False,
        "actual_safe_forget_linked": False,
        "source_integrity": CALLEE.G1.strip_ghost(verified) == original and
            all(s.get("source_unchanged") is True for s in stages.values()
                if s.get("status") == "RAN"),
        "frontend_refinement": all(stages.get(k, {}).get("exit") == 0 for k in
            ("normal-export", "normal-decode", "readonly-export",
             "readonly-decode", "refinement")),
        "full_mir_capture": capture,
        "first_error": errors[0] if errors else None,
        "fatal": [line for line in log.splitlines()
                  if line.startswith("Fatal error:")],
        "full_verifier_exit": stages.get("full-verification", {}).get("exit"),
        "stages": stages,
    }
    (case / "summary.json").write_text(json.dumps(
        result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"classification": result["classification"],
                      "frontend_refinement": result["frontend_refinement"],
                      "first_error": result["first_error"],
                      "fatal": result["fatal"]}), flush=True)


if __name__ == "__main__":
    main()
