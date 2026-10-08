#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted-only full MIR/refinement/proof matrix for exact-body forget owner."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sys
import time
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


HELPER = load(HERE.parent / "overnight-helper" / "check-helper.py",
              "forget_own_hosted_stages")
PREP = load(HERE / "prepare.py", "forget_own_hosted_fixture")


def one(text: str, pattern: str) -> bool:
    return len(re.findall(pattern, text)) == 1


def mir_inventory(decoded: str) -> dict:
    defpath, body = HELPER.A1.complete_function_record(decoded, PREP.FUNCTION)
    checks = {
        "generic_T": one(body, r'inputs = \[\(kind = \(param = "T"\)\)\]'),
        "one_normal_post": one(body, r'ens thread_token\('),
        "false_unwind_contract": one(body, r'on_unwind_ens false;'),
        "single_manually_drop_new": one(
            body, r'name = "std::mem::ManuallyDrop::<T>::new"'),
        "single_call": one(body, r'kind = \(\s*call = \('),
        "move_parameter": one(
            body, r'rhsRvalue = \(\s*use = \(\s*move = \(\s*local = '
                  r'\(name = "_1"\)'),
        "move_to_new": one(
            body, r'args = \[\s*\( move = \(\s*local = \(name = "_3"\)'),
        "normal_successor": one(
            body, r'target = \(something = \(index = 1\)\)'),
        "cleanup_successor": one(
            body, r'unwindAction = \(cleanup = \(index = 2\)\)'),
        "return": one(body, r'kind = \(return = void\)'),
        "unwind_resume": one(body, r'kind = \(unwindResume = void\)'),
        "cleanup_block": one(body, r'isCleanup = true'),
    }
    return {"defpath": defpath,
            "full_mir_sha256": HELPER.digest(body.encode()),
            "full_mir_bytes": len(body.encode()),
            "checks": checks, "exact_pinned_shape": all(checks.values())}


def intended_error(error: dict, variant: str, obligation: dict) -> bool:
    if error["file"] != "verified/lib.rs" or \
            int(error["line"]) != obligation["line"]:
        return False
    message = error["message"]
    if variant == "false_normal":
        return "Cannot prove false" in message
    if variant == "owner_duplicate":
        return "No matching heap chunks: own(T_typeid)(" in message
    if variant == "owner_wrong_value":
        return (("No matching heap chunks: own(T_typeid)(" in message) or
                "Cannot prove condition." in message)
    if variant == "thread_duplicate":
        return "No matching heap chunks: thread_token(tid)" in message
    if variant == "owner_loss":
        return "Function leaks heap chunks: own(T_typeid)(" in message
    return False


def classify(case: Path, stages: dict, variant: str,
             preamble: tuple[str, ...]) -> dict:
    fixture = json.loads((case / "fixture.json").read_text())
    original = (case / "original/lib.rs").read_bytes()
    verified = (case / "verified/lib.rs").read_bytes()
    source_ok = (PREP.SOURCE.strip_ghost(verified) == original and
                 HELPER.digest(original) == fixture["original_sha256"] and
                 HELPER.digest(verified) == fixture["verified_sha256"] and
                 fixture["source_certificate"]["source_exact"] is True and
                 all(stage.get("source_unchanged") is True for stage in
                     stages.values() if stage.get("status") == "RAN"))
    capture = {}
    for mode in ("normal", "readonly"):
        if stages.get(f"{mode}-decode", {}).get("exit") == 0:
            capture[mode] = mir_inventory(
                (case / f"{mode}-mir.txt").read_text(errors="strict"))
    frontend = (all(stages.get(name, {}).get("exit") == 0 for name in (
        "normal-export", "normal-decode", "readonly-export",
        "readonly-decode", "refinement")) and
        len(capture) == 2 and
        all(item["exact_pinned_shape"] for item in capture.values()))
    log_path = case / "full-verification.log"
    log = log_path.read_text(errors="replace") if log_path.exists() else ""
    timed = HELPER.CLASSIFIER.timed_functions(log)
    names = [item.function for item in timed]
    target = [item for item in timed if item.function == PREP.FUNCTION]
    exact_functions = names == [*preamble, PREP.FUNCTION]
    errors = HELPER.error_info(log)
    fatal = [line for line in log.splitlines() if line.startswith("Fatal error:")]
    exit_code = stages.get("full-verification", {}).get("exit")
    complete = (len(target) == 1 and target[0].body_execution_seen and
                target[0].return_seen and target[0].leak_check_seen)
    no_setup = source_ok and frontend and exact_functions and not fatal
    obligation = fixture["expected_obligation"]
    classification = "INCONCLUSIVE"
    if (variant == "positive" and no_setup and exit_code == 0 and
            not errors and complete and "dead code" not in log.lower() and
            re.search(r"0 errors found \(\d+ statements verified\)", log)):
        classification = "OWNER_PRESERVING_CALLEE_PROVED"
    elif (variant == "contradictory_pre" and no_setup and exit_code == 1 and
          not errors and len(target) == 1 and not complete):
        marker = f"verified/lib.rs({obligation['line']},1-"
        dead = [line for line in log.splitlines() if
                line.startswith(marker) and line.endswith(": dead code")]
        if dead:
            classification = "INTENDED_DEAD_CODE_NEGATIVE"
    elif (variant not in ("positive", "contradictory_pre") and no_setup and
          exit_code == 1 and len(errors) == 1 and len(target) == 1 and
          target[0].body_execution_seen and
          intended_error(errors[0], variant, obligation)):
        classification = "INTENDED_POST_OR_LEAK_NEGATIVE"
    return {
        "variant": variant, "classification": classification,
        "actual_safe_forget_linked": False,
        "source_integrity": source_ok,
        "frontend_refinement_and_mir": frontend,
        "exact_timed_functions": exact_functions,
        "timed_functions": names,
        "full_body_return_leak_seen": complete,
        "first_error": errors[0] if errors else None,
        "fatal": fatal, "full_mir_capture": capture,
        "stages": stages,
    }


def main() -> None:
    HELPER.require((os.environ.get("GITHUB_ACTIONS"),
                    os.environ.get("RUNNER_ENVIRONMENT"),
                    os.environ.get("RUNNER_OS")) ==
                   ("true", "github-hosted", "Linux"),
                   "forget-owner matrix requires GitHub-hosted Linux")
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
    for variant in PREP.VARIANTS:
        if args.deadline_epoch - time.time() < 35:
            result = {"variant": variant,
                      "classification": "NOT_RUN_DEADLINE"}
        else:
            case = evidence / variant
            try:
                PREP.write_case(REPO, case, variant)
                if variant == "weakened_unwind_admission":
                    fixture = json.loads((case / "fixture.json").read_text())
                    weakened = (case / "verified/lib.rs").read_bytes()
                    source_identity = (PREP.SOURCE.strip_ghost(weakened) ==
                                       (case / "original/lib.rs").read_bytes())
                    admitted = (fixture["source_certificate"]["source_exact"] and
                                weakened.count(b"on_unwind_ens false;") == 1 and
                                weakened.count(b"on_unwind_ens true;") == 0)
                    result = {
                        "variant": variant,
                        "classification": "INTENDED_UNWIND_ADMISSION_REJECT"
                            if source_identity and not admitted else "INCONCLUSIVE",
                        "source_integrity": source_identity,
                        "full_verification_run": False,
                        "reason": "target certificate requires false unwind",
                    }
                else:
                    stages = HELPER.run_case(case, args, prove=True)
                    result = classify(case, stages, variant, preamble)
            except Exception as exc:
                result = {"variant": variant, "classification": "INCONCLUSIVE",
                          "harness_exception": f"{type(exc).__name__}: {exc}"}
        (evidence / f"{variant}-result.json").write_text(json.dumps(
            result, indent=2, sort_keys=True) + "\n")
        rows.append(result)
        print(json.dumps({"variant": variant,
                          "classification": result["classification"],
                          "first_error": result.get("first_error")}), flush=True)
    classifications = [row["classification"] for row in rows]
    expected = ["OWNER_PRESERVING_CALLEE_PROVED",
                *("INTENDED_POST_OR_LEAK_NEGATIVE" for _ in range(5)),
                "INTENDED_DEAD_CODE_NEGATIVE",
                "INTENDED_UNWIND_ADMISSION_REJECT"]
    ready = classifications == expected
    summary = {
        "classification": "UNSAFE_ADAPTER_COMPONENT_CANDIDATE" if ready else
                          "INCONCLUSIVE",
        "accepted_actual_safe_forget_link": False,
        "accepted_std_proof": False,
        "all_declared_executed": not any(
            value == "NOT_RUN_DEADLINE" for value in classifications),
        "rows": rows,
        "source_trust": "exact pinned std forget and ManuallyDrop::new bodies",
    }
    (evidence / "summary.json").write_text(json.dumps(
        summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"classification": summary["classification"],
                      "all_declared_executed": summary["all_declared_executed"]}))


if __name__ == "__main__":
    main()
