#!/usr/bin/env python3
"""Hosted diagnostic: link two actual MaybeUninit::new calls to checked S6 body.

This is constructor linkage only. Later actual helper operations remain unmodeled.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError(reason)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None,
            f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
CONSTRUCTOR = load(REPO / "research/challenge-8/overnight-s6/check-maybeuninit-new-pointer.py",
                   "overnight_constructor_linkage_source")
ACTUAL = load(REPO / "research/challenge-8/overnight-helper/prepare-actual-helper-capture.py",
              "overnight_actual_linkage_source")
VARIANTS = ("positive", "wrong_active_field", "extra_union_field")
MODULE_MARKER = b"mod sort4_certified_maybeuninit"
ACTUAL_MARKER = b"pub fn select_unpredictable<Element>("
ERR = re.compile(r"^(.+?)\((\d+),([^)]*)\): error: (.*)$", re.M)


def write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def source_hashes(case: Path) -> dict[str, str]:
    return {relative: sha((case / relative).read_bytes()) for relative in
            ("original/lib.rs", "verified/lib.rs")}


def make_case(baseline_verified: bytes, body: bytes, cert: dict,
              case: Path, variant: str) -> dict:
    require(variant in VARIANTS, f"unknown variant: {variant}")
    _, source, component = CONSTRUCTOR.constructor_source(cert, variant)
    union_body = CONSTRUCTOR.extract_braced_item(source, MODULE_MARKER)
    module = MODULE_MARKER + b" " + union_body + b"\n"
    require(source.count(module) == 1,
            "local constructor module differs from S6 source builder")
    verified = CONSTRUCTOR.enable_crate_feature(
        baseline_verified, b"transparent_unions")
    require(verified.count(ACTUAL_MARKER) == 1 and
            verified.count(body) == 1 and verified.count(MODULE_MARKER) == 0,
            "actual helper source has changed or already contains adapter")
    verified = verified.replace(ACTUAL_MARKER, module + b"\n" + ACTUAL_MARKER, 1)
    original = CONSTRUCTOR.strip_ghost_annotations(verified)
    require(CONSTRUCTOR.strip_ghost_annotations(verified) == original and
            verified.count(body) == original.count(body) == 1 and
            original.count(b"crate::mem::forget(guard);") == 1,
            "auxiliary linkage changed actual runtime body or ghost strip")
    require(not case.exists(), f"refusing overwrite: {case}")
    (case / "original").mkdir(parents=True)
    (case / "verified").mkdir()
    (case / "original/lib.rs").write_bytes(original)
    (case / "verified/lib.rs").write_bytes(verified)
    record = {
        "variant": variant,
        "actual_body_sha256": sha(body),
        "actual_body_byte_identical": True,
        "actual_new_call_count": body.count(b"MaybeUninit::new("),
        "local_module_sha256": sha(module),
        "local_module_source_variant": component["variant"],
        "original_sha256": sha(original),
        "verified_sha256": sha(verified),
        "ghost_strip_identity": True,
        "scope": "constructor linkage only; actual helper not proved",
    }
    require(record["actual_new_call_count"] == 2,
            "actual constructor call count changed")
    write_json(case / "fixture.json", record)
    return record


def stage(case: Path, name: str, command: list[str], args,
          *, input_name: str | None = None, output_name: str | None = None,
          env_constructor: bool = False, cap_seconds: int = 90) -> dict:
    remaining = int(args.deadline_epoch - time.time()) - 25
    if remaining < 8:
        record = {"status": "NOT_RUN_DEADLINE", "exit": None,
                  "source_unchanged": None}
        write_json(case / f"{name}-stage.json", record)
        return record
    before = source_hashes(case)
    env = os.environ.copy()
    for key in ("SORT4_MAYBEUNINIT_REPO_ROOT",
                "SORT4_SELECT_INTRINSIC_REPO_ROOT",
                "SORT4_POINTER_DROP_REPO_ROOT"):
        env.pop(key, None)
    if env_constructor:
        env["SORT4_MAYBEUNINIT_REPO_ROOT"] = str(REPO)
    env["PATH"] = str(args.tool_home / "bin") + os.pathsep + env.get("PATH", "")
    stdout = case / (output_name or f"{name}.log")
    stderr = case / f"{name}-stderr.log" if output_name else stdout
    timeout = max(8, min(cap_seconds, remaining))
    with (case / input_name).open("rb") if input_name else open(os.devnull, "rb") as inp:
        with stdout.open("wb") as out:
            if stderr == stdout:
                result = subprocess.run(
                    ["timeout", "--signal=TERM", "--kill-after=10s",
                     f"{timeout}s", *command], cwd=case, stdin=inp,
                    stdout=out, stderr=subprocess.STDOUT, env=env, check=False)
            else:
                with stderr.open("wb") as err:
                    result = subprocess.run(
                        ["timeout", "--signal=TERM", "--kill-after=10s",
                         f"{timeout}s", *command], cwd=case, stdin=inp,
                        stdout=out, stderr=err, env=env, check=False)
    after = source_hashes(case)
    record = {"status": "RAN" if result.returncode != 124 else "TIMED_OUT",
              "exit": result.returncode, "argv": command,
              "constructor_gate_active": env_constructor,
              "source_unchanged": before == after,
              "source_before": before, "source_after": after,
              "stdout": stdout.name, "stderr": stderr.name}
    write_json(case / f"{name}-stage.json", record)
    return record


def run_case(case: Path, args) -> dict:
    exporter = str(args.tool_home / "bin/vf-rust-mir-exporter")
    stages = {}
    stages["normal-export"] = stage(case, "normal-export", [
        exporter, "verified/lib.rs", f"--sysroot={args.compiler_sysroot}",
        "--edition", "2021"], args, output_name="normal-mir.bin")
    stages["readonly-export"] = stage(case, "readonly-export", [
        exporter, "verified/lib.rs", f"--sysroot={args.compiler_sysroot}",
        "--edition", "2021", "--crate-type", "lib",
        "--vf-rust-mir-exporter:preprocess-readonly"], args,
        output_name="readonly-mir.bin")
    for mode in ("normal", "readonly"):
        if stages[f"{mode}-export"]["exit"] == 0:
            stages[f"{mode}-decode"] = stage(case, f"{mode}-decode", [
                "capnp", "decode", str(args.schema), "VfMir"], args,
                input_name=f"{mode}-mir.bin", output_name=f"{mode}-mir.txt",
                cap_seconds=40)
    four = all(stages.get(k, {}).get("exit") == 0 for k in (
        "normal-export", "normal-decode", "readonly-export", "readonly-decode"))
    if four:
        stages["full-verification"] = stage(case, "full-verification", [
            str(args.tool_home / "bin/verifast"), "-rustc_args",
            "--edition 2021", "-verbose", "1", "verified/lib.rs"], args,
            env_constructor=True, cap_seconds=100)
        stages["refinement"] = stage(case, "refinement", [
            str(args.tool_home / "bin/refinement-checker"), "--rustc-args",
            "--edition 2021", "original/lib.rs", "verified/lib.rs"], args,
            cap_seconds=70)
    return stages


def classify(case: Path, variant: str, stages: dict) -> dict:
    complete = all(stages.get(k, {}).get("exit") == 0 for k in (
        "normal-export", "normal-decode", "readonly-export",
        "readonly-decode", "refinement"))
    intact = all(item.get("source_unchanged") is True for item in stages.values())
    log = (case / "full-verification.log").read_text(errors="replace") if \
        (case / "full-verification.log").exists() else ""
    errors = ERR.findall(log)
    fatal = [line for line in log.splitlines() if line.startswith("Fatal error:")]
    result = {"variant": variant, "classification": "INCONCLUSIVE",
              "frontend_refinement": complete, "source_integrity": intact,
              "full_verifier_exit": stages.get("full-verification", {}).get("exit"),
              "first_error": errors[0] if errors else None,
              "fatal": fatal, "stages": stages}
    if variant == "positive":
        constructor_name = "sort4_certified_maybeuninit::sort4_checked_maybeuninit_new"
        start = log.find("Verifying function '" + constructor_name + "'")
        end = log.find("Verifying function 'select_unpredictable'", start + 1)
        constructor_log = log[start:end] if start >= 0 and end > start else ""
        checks = {
            "certified_source_and_full_mir": log.count(
                "SORT4-MAYBEUNINIT: certified local body " + constructor_name) == 1,
            "first_actual_call_redirected": log.count(
                "SORT4-MAYBEUNINIT: redirected checked external pointer call 1") == 1,
            "second_actual_call_redirected": log.count(
                "SORT4-MAYBEUNINIT: redirected checked external pointer call 2") == 1,
            "exact_two_call_count": "redirected=2, expected=2" in log,
            "local_constructor_proved": "Executing return statement" in constructor_log and
                "Leak check." in constructor_log,
            "actual_body_entered": end > start,
            "old_missing_new_error_gone": "No such function: std::mem::MaybeUninit::<T>::new" not in log,
            "no_certificate_fatal": not fatal,
            "next_blocker_after_linkage": bool(errors) and
                "No such function: std::mem::MaybeUninit::<T>::as_mut_ptr" in errors[0][3],
        }
        result["checks"] = checks
        if complete and intact and stages["full-verification"]["exit"] == 1 and \
                all(checks.values()) and len(errors) == 1:
            result["classification"] = "CONSTRUCTOR_LINKED_DIAGNOSTIC"
    else:
        reason = ("local constructor runtime body differs from repository"
                  if variant == "wrong_active_field" else
                  "certified union fields or types differ")
        checks = {"exact_certificate_reason": len(fatal) == 1 and
                  fatal[0] == ("Fatal error: exception Failure(\"SORT4-MAYBEUNINIT: "
                               "certificate mismatch: " + reason + "\")"),
                  "no_function_proof": "Verifying function '" not in log,
                  "no_proof_error": not errors}
        result["checks"] = checks
        if complete and intact and stages["full-verification"]["exit"] == 2 and \
                all(checks.values()):
            result["classification"] = "INTENDED_SOURCE_CERTIFICATE_REJECTION"
    write_json(case / "classification.json", result)
    return result


def main() -> None:
    require(os.environ.get("GITHUB_ACTIONS") == "true" and
            os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted" and
            os.environ.get("RUNNER_OS") == "Linux",
            "constructor linkage is hosted-only")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool-home", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--compiler-sysroot", required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--deadline-epoch", type=int, required=True)
    args = parser.parse_args()
    evidence = args.evidence.resolve()
    require(not evidence.exists(), f"refusing overwrite: {evidence}")
    evidence.mkdir(parents=True)
    baseline_dir = evidence / "baseline-capture"
    baseline = ACTUAL.write_fixture(REPO, baseline_dir)
    actual_body, actual_cert = ACTUAL.source_certificate(REPO)
    constructor_cert = CONSTRUCTOR.certify_repository_sources(REPO)
    baseline_verified = (baseline_dir / "verified/lib.rs").read_bytes()
    results = []
    for variant in VARIANTS:
        case = evidence / variant
        try:
            fixture = make_case(baseline_verified, actual_body,
                                constructor_cert, case, variant)
            stages = run_case(case, args)
            outcome = classify(case, variant, stages)
            outcome["fixture"] = fixture
        except Exception as exc:
            outcome = {"variant": variant, "classification": "INCONCLUSIVE",
                       "harness_exception": f"{type(exc).__name__}: {exc}"}
        results.append(outcome)
        print(json.dumps({"variant": variant,
                          "classification": outcome["classification"]}), flush=True)
    accepted = (len(results) == len(VARIANTS) and
                results[0]["classification"] == "CONSTRUCTOR_LINKED_DIAGNOSTIC" and
                all(item["classification"] == "INTENDED_SOURCE_CERTIFICATE_REJECTION"
                    for item in results[1:]))
    summary = {"classification": "CONSTRUCTOR_LINKAGE_ACCEPTED" if accepted else
               "INCONCLUSIVE", "accepted_component": accepted,
               "actual_helper_proved": False,
               "actual_body_sha256": sha(actual_body),
               "actual_source_certificate": actual_cert,
               "constructor_source_certificate": constructor_cert,
               "baseline_capture": baseline, "results": results}
    write_json(evidence / "summary.json", summary)
    if not accepted:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
