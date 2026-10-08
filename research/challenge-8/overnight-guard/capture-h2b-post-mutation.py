#!/usr/bin/env python3
"""Hosted diagnostic for a separately reviewed test-only H2b AST-post overlay.

No mutant here is a positive proof profile. Until hosted errors are reviewed,
all mutant outcomes remain diagnostic even if the selected Drop body fails.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path


HERE = Path(__file__).resolve().parent


def load():
    import importlib.util
    import sys
    path = HERE / "capture-guard-linkage.py"
    spec = importlib.util.spec_from_file_location("h2b_testpost_linkage", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"missing local H2b linkage runner: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


LINKAGE = load()
H2A = LINKAGE.H2A
H2B = LINKAGE.H2B
LINK = LINKAGE.LINK
REPO = LINKAGE.REPO
POST_KEY = "SORT4_GUARD_TEST_POST_MUTATION"
MUTANTS = ("initialized", "t_own", "second_cell",
           "false_normal", "false_unwind")


def segment(log: str, name: str) -> str:
    begin = log.find("Verifying function '" + name + "'")
    end = log.find("Verifying function '", begin + 1) if begin >= 0 else -1
    return log[begin:end if end >= 0 else None] if begin >= 0 else ""


def two_outcomes(log: str) -> bool:
    returns = [line for line in log.splitlines()
               if "Executing return statement" in line]
    leaks = [line for line in log.splitlines()
             if "Leak check." in line and ": note:" not in line]
    return len(returns) == len(leaks) == 2 and all(
        log.find(returns[i]) < log.find(leaks[i]) for i in range(2))


def classify(case: Path, mutant: str | None, stages: dict) -> dict:
    complete = all(stages.get(k, {}).get("exit") == 0 for k in (
        "normal-export", "normal-decode", "readonly-export", "readonly-decode",
        "refinement"))
    intact = all(s.get("source_unchanged") is True for s in stages.values())
    log_file = case / "full-verification.log"
    log = log_file.read_text(errors="replace") if log_file.exists() else ""
    errors = LINK.ERR.findall(log)
    fatal = [line for line in log.splitlines() if line.startswith("Fatal error:")]
    method = segment(log, "sort4_checked_generic_drop")
    guard = segment(log, "<DropOnPanic<T> as std::ops::Drop>::drop")
    ordinary = segment(log, "<OrdinaryDrop as std::ops::Drop>::drop")
    marker = f"SORT4-GUARD-TESTPOST: {mutant} selected" if mutant else None
    result = {
        "variant": mutant or "positive_unmodified",
        "classification": "POST_MUTANT_DIAGNOSTIC_ONLY" if mutant else
            "UNMODIFIED_TEST_OVERLAY_DIAGNOSTIC_ONLY",
        "component_accepted": False, "actual_nested_drop_proved": False,
        "test_only_ast_post_profile": True,
        "frontend_refinement": complete, "source_integrity": intact,
        "full_verifier_exit": stages.get("full-verification", {}).get("exit"),
        "first_error": errors[0] if errors else None,
        "error_count": len(errors), "fatal": fatal,
        "gate_accepted": "SORT4-GENERIC-GUARD: source/MIR local link accepted" in log,
        "test_post_marker_once": log.count(marker) == 1 if marker else None,
        "generic_method_normal_unwind_return_leak": two_outcomes(method),
        "guard_entered": bool(guard),
        "guard_real_call_reached": "Verifying call" in guard,
        "guard_return_count": guard.count("Executing return statement"),
        "guard_leak_count": guard.count("Leak check."),
        "ordinary_drop_return_leak":
            "Executing return statement" in ordinary and "Leak check." in ordinary,
        "stages": stages,
    }
    if mutant is None:
        inherited = LINKAGE.classify(case, "positive", stages, True)
        if inherited["classification"] == "H2B_LOCAL_NOMINAL_DROP_CANDIDATE_PROVED":
            result["classification"] = "UNMODIFIED_LOCAL_POSITIVE_PROVED"
    elif (complete and intact and not fatal and len(errors) == 1 and
          result["full_verifier_exit"] == 1 and
          result["gate_accepted"] and result["test_post_marker_once"] and
          result["generic_method_normal_unwind_return_leak"] and
          result["guard_real_call_reached"] and
          result["guard_return_count"] >= 1):
        # This is not an intended negative yet: source location, predicate,
        # branch and first failing post must be inspected from hosted logs.
        result["classification"] = "GUARD_POST_FAILURE_REQUIRES_REVIEW"
    LINK.write_json(case / "post-mutation-classification.json", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool-home", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--compiler-sysroot", required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--deadline-epoch", type=int, required=True)
    parser.add_argument("--guard-root", type=Path, required=True)
    parser.add_argument("--template-root", type=Path, required=True)
    parser.add_argument("--mutants", nargs="+", choices=MUTANTS,
                        default=list(MUTANTS))
    args = parser.parse_args()
    LINKAGE.require(os.environ.get("GITHUB_ACTIONS") == "true" and
                    os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted" and
                    os.environ.get("RUNNER_OS") == "Linux",
                    "GitHub-hosted Linux required")
    LINKAGE.require(args.guard_root.resolve() == REPO and
                    args.template_root.resolve() == REPO,
                    "H2b post controls require same exact local root")
    evidence = args.evidence.resolve()
    LINKAGE.require(not evidence.exists(), f"refusing overwrite: {evidence}")
    evidence.mkdir(parents=True)
    os.environ["SORT4_GUARD_REPO_ROOT"] = str(REPO)
    os.environ["SORT4_GUARD_TEMPLATE_REPO_ROOT"] = str(REPO)
    method_body, method_cert = H2A.source_certificate()
    struct_body, drop_body, guard_cert = H2B.source_certificate()
    method = LINKAGE.checked_method(method_body)
    original, verified = LINKAGE.source_pair(method, struct_body, drop_body,
                                             "positive", template_active=True)
    test_patch = HERE / "verifast-h2d-test-only-drop-post-26.10.patch"
    LINKAGE.require(test_patch.exists(), "missing reviewed H2d test overlay artifact")
    cert = {"generic_method": method_cert, "guard": guard_cert,
            "actual_nested_drop_proved": False,
            "test_only_post_overlay": True,
            "test_overlay_patch_sha256": LINK.sha(test_patch.read_bytes()),
            "test_console_sha256":
                LINK.sha((args.tool_home / "bin/verifast").read_bytes()),
            "production_positive_profile": False}
    LINK.write_json(evidence / "source-certificate.json", cert)
    results = []
    for mutant in (None, *args.mutants):
        name = mutant or "positive_unmodified"
        case = evidence / name
        case.mkdir()
        (case / "original").mkdir()
        (case / "verified").mkdir()
        (case / "original/lib.rs").write_bytes(original)
        (case / "verified/lib.rs").write_bytes(verified)
        LINK.write_json(case / "fixture.json", {
            "variant": name, "source_certificate": cert,
            "original_sha256": LINK.sha(original),
            "verified_sha256": LINK.sha(verified),
            "test_post_mutation": mutant,
            "actual_nested_drop_proved": False,
        })
        if mutant is None:
            os.environ.pop(POST_KEY, None)
        else:
            os.environ[POST_KEY] = mutant
        results.append(classify(case, mutant, H2A.run_case(case, args)))
        if mutant is None and results[-1]["classification"] != \
                "UNMODIFIED_LOCAL_POSITIVE_PROVED":
            break
    os.environ.pop(POST_KEY, None)
    LINK.write_json(evidence / "summary.json", {
        "classification": "H2B_TEST_POST_MUTATIONS_DIAGNOSTIC_ONLY",
        "component_accepted": False, "actual_nested_drop_proved": False,
        "source_certificate": cert, "results": results,
    })


if __name__ == "__main__":
    main()
