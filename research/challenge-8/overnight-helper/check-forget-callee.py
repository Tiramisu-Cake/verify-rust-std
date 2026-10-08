#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted full-body and negative matrix for the exact generic forget callee."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import time
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


HELPER = load(HERE / "check-helper.py", "overnight_g1c_shared_runner")
CALLEE = load(HERE / "prepare-forget-callee.py", "overnight_g1c_fixture")
FUNC = "checked_forget_generic"


def classify(case: Path, stages: dict, variant: str,
             preamble: tuple[str, ...]) -> dict:
    fixture = json.loads((case / "fixture.json").read_text())
    original = (case / "original/lib.rs").read_bytes()
    verified = (case / "verified/lib.rs").read_bytes()
    source_ok = (CALLEE.G1.strip_ghost(verified) == original and
                 HELPER.digest(original) == fixture["original_sha256"] and
                 HELPER.digest(verified) == fixture["verified_sha256"] and
                 all(item.get("source_unchanged") is True for item in stages.values()
                     if item.get("status") == "RAN"))
    frontend = all(stages.get(name, {}).get("exit") == 0 for name in (
        "normal-export", "normal-decode", "readonly-export",
        "readonly-decode", "refinement"))
    log_path = case / "full-verification.log"
    log = log_path.read_text(errors="replace") if log_path.exists() else ""
    timed = HELPER.CLASSIFIER.timed_functions(log)
    names = [item.function for item in timed]
    target = [item for item in timed if item.function == FUNC]
    exact_functions = names == [*preamble, FUNC]
    errors = HELPER.error_info(log)
    fatal = [line for line in log.splitlines() if line.startswith("Fatal error:")]
    exit_code = stages.get("full-verification", {}).get("exit")
    obligation = fixture["expected_obligation"]
    no_setup = source_ok and frontend and exact_functions and not fatal and \
        exit_code is not None
    body_complete = (len(target) == 1 and target[0].body_execution_seen and
                     target[0].return_seen and target[0].leak_check_seen)
    classification = "INCONCLUSIVE"
    if (variant == "positive" and no_setup and exit_code == 0 and
            not errors and body_complete and "dead code" not in log.lower()):
        classification = "CALLEE_BODY_PROVED"
    elif variant == "contradictory_pre" and no_setup and exit_code == 1:
        marker = f"verified/lib.rs({obligation['line']},1-"
        dead = [line for line in log.splitlines() if
                line.startswith(marker) and line.endswith(": dead code")]
        if not errors and dead and not body_complete:
            classification = "INTENDED_DEAD_CODE_NEGATIVE"
    elif variant != "positive" and no_setup and exit_code == 1 and \
            len(errors) == 1:
        error = errors[0]
        if (error["file"] == "verified/lib.rs" and
                int(error["line"]) == obligation["line"] and
                obligation["message"] in error["message"] and
                (variant != "thread_loss" or target[0].body_execution_seen)):
            classification = "INTENDED_PROOF_NEGATIVE"
    capture = {}
    for mode in ("normal", "readonly"):
        if stages.get(f"{mode}-decode", {}).get("exit") == 0:
            name, body = HELPER.A1.complete_function_record(
                (case / f"{mode}-mir.txt").read_text(errors="strict"), FUNC)
            capture[mode] = {
                "defpath": name, "full_mir_sha256": HELPER.digest(body.encode()),
                "full_mir_bytes": len(body.encode()),
                "review_status": "CAPTURE_ONLY"}
    return {
        "variant": variant, "classification": classification,
        "actual_safe_forget_linked": False,
        "source_integrity": source_ok, "frontend_refinement": frontend,
        "exact_timed_functions": exact_functions, "timed_functions": names,
        "full_body_return_leak_seen": body_complete,
        "first_error": errors[0] if errors else None,
        "fatal": fatal, "full_mir_capture": capture, "stages": stages,
    }


def main() -> None:
    HELPER.require((os.environ.get("GITHUB_ACTIONS"),
                    os.environ.get("RUNNER_ENVIRONMENT"),
                    os.environ.get("RUNNER_OS")) ==
                   ("true", "github-hosted", "Linux"),
                   "generic forget callee matrix requires hosted Actions")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool-home", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--compiler-sysroot", required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--deadline-epoch", type=int, required=True)
    parser.add_argument("--s6-specs", default=None)
    args = parser.parse_args()
    preamble = tuple(args.s6_specs.split(",")) if args.s6_specs else \
        HELPER.G1_PREAMBLE_DEFAULT
    HELPER.require(len(set(preamble)) == len(preamble),
                   "timed function preamble duplicated")
    evidence = args.evidence.resolve()
    HELPER.require(not evidence.exists(), "refusing to overwrite evidence")
    evidence.mkdir(parents=True)
    rows = []
    for variant in CALLEE.VARIANTS:
        if args.deadline_epoch - time.time() < 35:
            rows.append({"variant": variant,
                         "classification": "NOT_RUN_DEADLINE"})
            continue
        case = evidence / variant
        try:
            CALLEE.write_case(REPO, case, variant)
            stages = HELPER.run_case(case, args, prove=True)
            result = classify(case, stages, variant, preamble)
        except Exception as exc:
            result = {"variant": variant, "classification": "INCONCLUSIVE",
                      "harness_exception": f"{type(exc).__name__}: {exc}"}
        HELPER.require(case.exists() or "harness_exception" in result,
                       "G1c case missing")
        (evidence / f"{variant}-result.json").write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n")
        rows.append(result)
        print(json.dumps({"variant": variant,
                          "classification": result["classification"],
                          "first_error": result.get("first_error")}), flush=True)
    accepted = [row["classification"] for row in rows] == [
        "CALLEE_BODY_PROVED", "INTENDED_PROOF_NEGATIVE",
        "INTENDED_PROOF_NEGATIVE", "INTENDED_PROOF_NEGATIVE",
        "INTENDED_DEAD_CODE_NEGATIVE"]
    summary = {"classification": "G1C_COMPONENT_CANDIDATE" if accepted else
               "INCONCLUSIVE", "accepted_component": False,
               "actual_safe_forget_linked": False, "rows": rows,
               "all_declared_executed": not any(
                   row["classification"] == "NOT_RUN_DEADLINE" for row in rows),
               "source_trust": "exact std forget/ManuallyDrop bodies; identity lowering"}
    (evidence / "summary.json").write_text(json.dumps(
        summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"classification": summary["classification"],
                      "all_declared_executed": summary["all_declared_executed"]}))


if __name__ == "__main__":
    main()
