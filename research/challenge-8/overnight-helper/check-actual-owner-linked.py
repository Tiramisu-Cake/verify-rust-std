#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted complete-MIR capture of actual owner with same-unit S6 callees.

The frozen S6 actual gate is expected to reject the expanded owner ghost
inventory. This runner records that boundary; it never promotes the helper.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"missing {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PREP = load(HERE / "prepare-actual-owner-linked.py",
            "actual_owner_linked_preparer")
CAPTURE = load(HERE / "check-actual-owner-projection.py",
               "actual_owner_linked_mir_capture")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool-home", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--compiler-sysroot", required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--deadline-epoch", type=int, required=True)
    parser.add_argument("--without-safety-proof", action="store_true")
    parser.add_argument("--without-nested-drop-opens", action="store_true")
    parser.add_argument("--fingerprint-probe", action="store_true",
                        help="fail-closed frontend decoded-body inventory probe")
    args = parser.parse_args()
    PREP.OWNER.require((os.environ.get("GITHUB_ACTIONS"),
                        os.environ.get("RUNNER_ENVIRONMENT"),
                        os.environ.get("RUNNER_OS")) ==
                       ("true", "github-hosted", "Linux"),
                       "linked owner capture requires GitHub-hosted Linux")
    evidence = args.evidence.resolve()
    PREP.write_case(REPO, evidence,
                    owner_safety_proof=not args.without_safety_proof,
                    annotate_nested_drop=not args.without_nested_drop_opens)
    case = evidence / "linked-owner"
    if args.fingerprint_probe:
        os.environ["SORT4_ACTUAL_OWNER_REPO_ROOT"] = str(REPO)
        os.environ["SORT4_ACTUAL_OWNER_EVIDENCE_DIR"] = str(case.resolve())
        os.environ["SORT4_ACTUAL_OWNER_FINGERPRINT_RUN"] = "first"
    else:
        os.environ.pop("SORT4_ACTUAL_OWNER_REPO_ROOT", None)
        os.environ.pop("SORT4_ACTUAL_OWNER_EVIDENCE_DIR", None)
        os.environ.pop("SORT4_ACTUAL_OWNER_FINGERPRINT_RUN", None)
    stages = PREP.LINK.run_case(case, args, pointer_drop=True)
    if args.fingerprint_probe and (
            case / "full-verification.log").is_file() and (
            "SORT4-ACTUAL-OWNER: diagnostic refusal: decoded representation "
            "not reviewed; no semantic admission" in
            (case / "full-verification.log").read_text(errors="replace")):
        os.environ["SORT4_ACTUAL_OWNER_FINGERPRINT_RUN"] = "repeat"
        stages["full-verification-repeat"] = PREP.LINK.stage(
            case, "full-verification-repeat",
            [str(args.tool_home / "bin/verifast"), "-rustc_args",
             "--edition 2021", "-verbose", "1", "verified/lib.rs"],
            args, gates=True, pointer_drop=True, cap_seconds=100)
    fingerprints = {}
    if args.fingerprint_probe:
        for label in ("unit", *(f"body-{index}" for index in range(5))):
            first = case / f"actual-owner-{label}-first.marshal"
            repeat = case / f"actual-owner-{label}-repeat.marshal"
            first_bytes = first.read_bytes() if first.is_file() else None
            repeat_bytes = repeat.read_bytes() if repeat.is_file() else None
            fingerprints[label] = {
                "first_sha256": hashlib.sha256(first_bytes).hexdigest()
                    if first_bytes is not None else None,
                "repeat_sha256": hashlib.sha256(repeat_bytes).hexdigest()
                    if repeat_bytes is not None else None,
                "first_bytes": len(first_bytes) if first_bytes is not None
                    else None,
                "repeat_bytes": len(repeat_bytes) if repeat_bytes is not None
                    else None,
                "repeat_identical": first_bytes is not None and
                    repeat_bytes is not None and first_bytes == repeat_bytes,
            }
    graphs = CAPTURE.capture_graph(case, stages)
    log_path = case / "full-verification.log"
    log = log_path.read_text(errors="replace") if log_path.exists() else ""
    errors = CAPTURE.HELPER.error_info(log)
    frontend = all(stages.get(k, {}).get("exit") == 0 for k in (
        "normal-export", "normal-decode", "readonly-export",
        "readonly-decode", "refinement"))
    record = {
        "classification": "LINKED_ACTUAL_OWNER_DIAGNOSTIC_ONLY",
        "actual_helper_proved": False,
        "actual_nested_drop_proved": False,
        "actual_safe_forget_linked": False,
        "fingerprint_probe": args.fingerprint_probe,
        "fingerprints": fingerprints,
        "fingerprint_repeat_complete": args.fingerprint_probe and all(
            row["repeat_identical"] for row in fingerprints.values()),
        "frontend_refinement": frontend,
        "source_integrity": all(
            stage.get("source_unchanged") is True
            for stage in stages.values() if stage.get("status") == "RAN"),
        "full_mir_capture": graphs,
        "frozen_s6_actual_gate_passed":
            "SORT4-SELECT-INTRINSIC: full typed actual MIR graph accepted" in log,
        "first_error": errors[0] if errors else None,
        "fatal": [line for line in log.splitlines()
                  if line.startswith("Fatal error:")],
        "stages": stages,
    }
    (evidence / "summary.json").write_text(json.dumps(
        record, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: record[key] for key in (
        "classification", "frontend_refinement",
        "frozen_s6_actual_gate_passed", "first_error", "fatal")}), flush=True)


if __name__ == "__main__":
    main()
