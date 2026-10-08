#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted diagnostic capture for the exact actual helper owner projection."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
DROP_DEF_PATH = "<select_unpredictable::DropOnPanic<T> as std::ops::Drop>::drop"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PREP = load(HERE / "prepare-actual-owner-projection.py", "owner_projection_source")
HELPER = load(HERE / "check-helper.py", "owner_projection_runner")
A1 = load(HERE / "prepare-assume-init-2610.py", "owner_projection_mir")


def exact_drop_record(decoded: str) -> str:
    marker = f'defPath = "{DROP_DEF_PATH}"'
    if decoded.count(marker) != 1:
        raise ValueError("actual nested Drop MIR body absent/ambiguous")
    start = decoded.rfind("    ( defKind =", 0, decoded.index(marker))
    if start < 0:
        raise ValueError("actual nested Drop MIR record opening missing")
    record = A1.balanced_record(decoded, decoded.index("(", start))
    if marker not in record or "basicBlocks = [" not in record:
        raise ValueError("actual nested Drop MIR record incomplete")
    return record


def capture_graph(case: Path, stages: dict) -> dict:
    result = {}
    for mode in ("normal", "readonly"):
        if stages.get(f"{mode}-decode", {}).get("exit") != 0:
            continue
        decoded = (case / f"{mode}-mir.txt").read_text(errors="strict")
        name, outer = A1.complete_function_record(decoded, "select_unpredictable")
        drop = exact_drop_record(decoded)
        (case / f"{mode}-actual-helper-full-mir.txt").write_text(outer)
        (case / f"{mode}-nested-drop-full-mir.txt").write_text(drop)
        result[mode] = {
            "outer_defpath": name,
            "outer_full_mir_sha256": HELPER.digest(outer.encode()),
            "nested_drop_defpath": DROP_DEF_PATH,
            "nested_drop_full_mir_sha256": HELPER.digest(drop.encode()),
            "decoded_full_mir_sha256": HELPER.digest(decoded.encode()),
            "nominal_owner_exported":
                "pred<T> <select_unpredictable::DropOnPanic<T>>.own" in decoded,
            "forget_call_present": 'name = "std::mem::forget"' in outer,
            "shared_cleanup_present": "isCleanup = true" in outer,
            "classification": "CAPTURE_ONLY; FULL GRAPH NOT YET CERTIFIED",
        }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool-home", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--compiler-sysroot", required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--deadline-epoch", type=int, required=True)
    parser.add_argument("--prove", action="store_true",
                        help="capture first stock proof/parser barrier; never accept")
    args = parser.parse_args()
    HELPER.require((os.environ.get("GITHUB_ACTIONS"),
                    os.environ.get("RUNNER_ENVIRONMENT"),
                    os.environ.get("RUNNER_OS")) ==
                   ("true", "github-hosted", "Linux"),
                   "actual owner capture requires GitHub-hosted Linux")
    evidence = args.evidence.resolve()
    PREP.write_case(REPO, evidence)
    case = evidence / "owner-projection"
    # The first run measures source/parser/MIR applicability without silently
    # enabling an unrelated local guard or actual-helper admission overlay.
    os.environ.pop("SORT4_GUARD_REPO_ROOT", None)
    os.environ.pop("SORT4_ACTUAL_OWNER_REPO_ROOT", None)
    os.environ.pop("SORT4_ACTUAL_FORGET_REPO_ROOT", None)
    stages = HELPER.run_case(case, args, prove=args.prove)
    verified = (case / "verified/lib.rs").read_bytes()
    original = (case / "original/lib.rs").read_bytes()
    graph = capture_graph(case, stages)
    log_path = case / "full-verification.log"
    log = log_path.read_text(errors="replace") if log_path.exists() else ""
    errors = HELPER.error_info(log)
    result = {
        "classification": "ACTUAL_OWNER_PROJECTION_DIAGNOSTIC_ONLY",
        "actual_helper_proved": False,
        "actual_nested_drop_proved": False,
        "actual_safe_forget_linked": False,
        "source_integrity": (PREP.strip_ghost(verified) == original and
                             all(stage.get("source_unchanged") is True
                                 for stage in stages.values()
                                 if stage.get("status") == "RAN")),
        "frontend_refinement": all(stages.get(key, {}).get("exit") == 0
                                   for key in ("normal-export", "normal-decode",
                                               "readonly-export", "readonly-decode",
                                               "refinement")),
        "full_mir_capture": graph,
        "first_error": errors[0] if errors else None,
        "fatal": [line for line in log.splitlines()
                  if line.startswith("Fatal error:")],
        "stages": stages,
    }
    (evidence / "summary.json").write_text(json.dumps(
        result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"classification": result["classification"],
                      "frontend_refinement": result["frontend_refinement"],
                      "first_error": result["first_error"],
                      "fatal": result["fatal"]}), flush=True)


if __name__ == "__main__":
    main()
