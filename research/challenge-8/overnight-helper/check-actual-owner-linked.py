#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted complete-MIR capture of actual owner with same-unit S6 callees.

The frozen S6 actual gate is expected to reject the expanded owner ghost
inventory. This runner records that boundary; it never promotes the helper.
"""

from __future__ import annotations

import argparse
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
    stages = PREP.LINK.run_case(case, args, pointer_drop=True)
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
