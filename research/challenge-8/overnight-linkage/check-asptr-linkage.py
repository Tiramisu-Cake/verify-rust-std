#!/usr/bin/env python3
"""Hosted diagnostic: link actual constructor and as_mut_ptr calls to S6 bodies."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]


def load():
    import importlib.util
    path = HERE / "check-constructor-linkage.py"
    spec = importlib.util.spec_from_file_location("overnight_constructor_linkage", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("constructor linkage driver unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


LINK = load()
ASPTR = LINK.load(REPO / "research/challenge-8/overnight-s6/check-select-pointer.py",
                  "overnight_asptr_linkage_source")
VARIANTS = ("positive", "source_operand")
ASPTR_MARKER = b"pub fn sort4_checked_as_mut_ptr<Element>"
PROBE_MARKER = b"pub unsafe fn sort4_as_mut_ptr_unknown_probe"


def adapter_source(evidence: Path, variant: str, constructor):
    specialized, cert = ASPTR.source_certificate(REPO, constructor)
    source_case = evidence / ("asptr-source-" + variant)
    mutation = "operand" if variant == "source_operand" else None
    ASPTR.make_case(source_case, specialized, cert, constructor,
                    "unknown", admission=mutation)
    verified = (source_case / "verified/lib.rs").read_bytes()
    LINK.require(verified.count(ASPTR_MARKER) == 1 and
                 verified.count(PROBE_MARKER) == 1,
                 "accepted as_mut_ptr source body/probe boundaries changed")
    start = verified.index(ASPTR_MARKER)
    end = verified.index(PROBE_MARKER)
    LINK.require(start < end, "as_mut_ptr helper order changed")
    adapter = verified[start:end]
    if variant == "positive":
        LINK.require(adapter.count(specialized) == 1,
                     "positive adapter lost pinned two-cast body")
    return adapter, cert, source_case


def make_case(baseline_verified: bytes, body: bytes, ctor_cert: dict,
              adapter: bytes, case: Path, variant: str) -> dict:
    record = LINK.make_case(baseline_verified, body, ctor_cert, case,
                            "positive")
    verified_path = case / "verified/lib.rs"
    original_path = case / "original/lib.rs"
    verified = verified_path.read_bytes()
    LINK.require(verified.count(LINK.ACTUAL_MARKER) == 1 and
                 verified.count(ASPTR_MARKER) == 0,
                 "actual source already contains as_mut_ptr adapter")
    verified = verified.replace(LINK.ACTUAL_MARKER,
                                adapter + LINK.ACTUAL_MARKER, 1)
    original = LINK.CONSTRUCTOR.strip_ghost_annotations(verified)
    LINK.require(original.count(body) == verified.count(body) == 1 and
                 original.count(b"crate::mem::forget(guard);") == 1 and
                 LINK.CONSTRUCTOR.strip_ghost_annotations(verified) == original,
                 "as_mut_ptr adapter changed actual runtime body")
    verified_path.write_bytes(verified)
    original_path.write_bytes(original)
    record.update({"variant": variant,
                   "asptr_adapter_sha256": LINK.sha(adapter),
                   "asptr_source_mutation": "operand" if variant ==
                   "source_operand" else None,
                   "actual_body_byte_identical": True,
                   "original_sha256": LINK.sha(original),
                   "verified_sha256": LINK.sha(verified),
                   "scope": "constructor and as_mut_ptr linkage only; actual helper not proved"})
    LINK.write_json(case / "fixture.json", record)
    return record


def function_log(log: str, name: str) -> str:
    marker = "Verifying function '" + name + "'"
    start = log.find(marker)
    if start < 0:
        return ""
    end = log.find("Verifying function '", start + len(marker))
    return log[start:end if end >= 0 else None]


def classify(case: Path, variant: str, stages: dict) -> dict:
    frontend = all(stages.get(name, {}).get("exit") == 0 for name in (
        "normal-export", "normal-decode", "readonly-export",
        "readonly-decode", "refinement"))
    intact = all(item.get("source_unchanged") is True for item in stages.values())
    log_path = case / "full-verification.log"
    log = log_path.read_text(errors="replace") if log_path.exists() else ""
    errors = LINK.ERR.findall(log)
    fatal = [line for line in log.splitlines() if line.startswith("Fatal error:")]
    result = {"variant": variant, "classification": "INCONCLUSIVE",
              "frontend_refinement": frontend, "source_integrity": intact,
              "full_verifier_exit": stages.get("full-verification", {}).get("exit"),
              "first_error": errors[0] if errors else None,
              "fatal": fatal, "stages": stages}
    if variant == "positive":
        ctor = function_log(log,
            "sort4_certified_maybeuninit::sort4_checked_maybeuninit_new")
        asptr = function_log(log, "sort4_checked_as_mut_ptr")
        checks = {
            "constructor_certificate": "SORT4-MAYBEUNINIT: full typed constructor MIR graph accepted" in log,
            "asptr_certificate": "SORT4-AS-MUT-PTR: full typed body MIR graph accepted" in log and
                "SORT4-AS-MUT-PTR: certified SAFE local body sort4_checked_as_mut_ptr" in log,
            "constructor_redirects_exact": all(
                log.count("SORT4-MAYBEUNINIT: redirected checked external pointer call " + str(i)) == 1
                for i in (1, 2)) and
                "SORT4-MAYBEUNINIT: checked local body translated (inner=1, aggregate=1, redirected=2, expected=2)" in log,
            "asptr_redirects_exact": all(
                log.count("SORT4-AS-MUT-PTR: redirected typed external call " + str(i)) == 1
                for i in (1, 2)) and
                "SORT4-AS-MUT-PTR: checked SAFE body translated (redirected=2, expected=2)" in log,
            "constructor_proved": "Executing return statement" in ctor and
                "Leak check." in ctor,
            "asptr_proved": "Executing return statement" in asptr and
                "Leak check." in asptr,
            "actual_body_entered": "Verifying function 'select_unpredictable'" in log,
            "old_missing_calls_gone": "No such function: std::mem::MaybeUninit::<T>::new" not in log and
                "No such function: std::mem::MaybeUninit::<T>::as_mut_ptr" not in log,
            "next_blocker_typed_intrinsic": len(errors) == 1 and
                "No such function: std::intrinsics::select_unpredictable" in errors[0][3],
            "no_certificate_fatal": not fatal,
        }
        result["checks"] = checks
        if frontend and intact and stages["full-verification"]["exit"] == 1 and \
                all(checks.values()):
            result["classification"] = "CONSTRUCTOR_ASPTR_LINKED_DIAGNOSTIC"
    else:
        reason = "Fatal error: exception Failure(\"SORT4-AS-MUT-PTR: " \
                 "certificate mismatch: local body differs from exact source specialization\")"
        checks = {"exact_asptr_certificate_reason": fatal == [reason],
                  "no_function_proof": "Verifying function '" not in log,
                  "no_proof_error": not errors}
        result["checks"] = checks
        if frontend and intact and stages["full-verification"]["exit"] == 2 and \
                all(checks.values()):
            result["classification"] = "INTENDED_ASPTR_SOURCE_REJECTION"
    LINK.write_json(case / "classification.json", result)
    return result


def main() -> None:
    LINK.require(os.environ.get("GITHUB_ACTIONS") == "true" and
                 os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted" and
                 os.environ.get("RUNNER_OS") == "Linux",
                 "as_mut_ptr linkage is hosted-only")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool-home", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--compiler-sysroot", required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--deadline-epoch", type=int, required=True)
    args = parser.parse_args()
    evidence = args.evidence.resolve()
    LINK.require(not evidence.exists(), f"refusing overwrite: {evidence}")
    evidence.mkdir(parents=True)
    baseline_dir = evidence / "baseline-capture"
    LINK.ACTUAL.write_fixture(REPO, baseline_dir)
    actual_body, actual_cert = LINK.ACTUAL.source_certificate(REPO)
    ctor_cert = LINK.CONSTRUCTOR.certify_repository_sources(REPO)
    baseline_verified = (baseline_dir / "verified/lib.rs").read_bytes()
    results = []
    for variant in VARIANTS:
        try:
            adapter, asptr_cert, source_case = adapter_source(
                evidence, variant, LINK.CONSTRUCTOR)
            case = evidence / variant
            fixture = make_case(baseline_verified, actual_body,
                                ctor_cert, adapter, case, variant)
            stages = LINK.run_case(case, args)
            result = classify(case, variant, stages)
            result.update({"fixture": fixture,
                           "asptr_source_case": str(source_case.relative_to(evidence)),
                           "asptr_source_certificate": asptr_cert})
        except Exception as exc:
            result = {"variant": variant, "classification": "INCONCLUSIVE",
                      "harness_exception": f"{type(exc).__name__}: {exc}"}
        results.append(result)
        print(json.dumps({"variant": variant,
                          "classification": result["classification"]}), flush=True)
    accepted = (len(results) == len(VARIANTS) and
                results[0]["classification"] == "CONSTRUCTOR_ASPTR_LINKED_DIAGNOSTIC" and
                results[1]["classification"] == "INTENDED_ASPTR_SOURCE_REJECTION")
    LINK.write_json(evidence / "summary.json", {
        "classification": "CONSTRUCTOR_ASPTR_LINKAGE_ACCEPTED" if accepted else
                          "INCONCLUSIVE",
        "accepted_component": accepted,
        "actual_helper_proved": False,
        "actual_body_sha256": LINK.sha(actual_body),
        "actual_source_certificate": actual_cert,
        "constructor_source_certificate": ctor_cert,
        "results": results,
    })
    if not accepted:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
