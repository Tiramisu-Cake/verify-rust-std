#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted S7b full-unit diagnostic for the exact generic forget body only."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys


PROFILE = "experimental-source-linked-select-pointer-drop-v4"
EXPECTED_TIMED_FUNCTIONS = (
    "u32_sync", "u32_share_mono", "init_ref_readonly_points_to_shared",
    "std::mem::close_MaybeUninit_pointer_own",
    "std::mem::select_MaybeUninit_pointer_own",
    "std::ptr::pointer_drop_glue_identity", "checked_forget_generic",
)
PATCH_SHA = "c7cc08a995bac5879901f4fe08030f09d23bdfefb1a3ab5893be12a8dd1f8fc1"
MEM_SHA = "1db195d24508e4eef81163672d008667765c2c121f4fa70f8752742e11106273"
MANUALLY_DROP_SHA = "17e8e41866d3eadcfdc6f1a516e4ed9dd5555e10ad725aac3b04aec7c759731b"
MAYBE_DANGLING_SHA = "1cf24b2ec36fff143f329f2ef6db5b4d47cfa798da7f30d88b554b712c8f4b53"
FORGET_SOURCE = b"pub const fn forget<T>(t: T) {\n    let _ = ManuallyDrop::new(t);\n}"
FORGET_BODY = b"{\n    let _ = ManuallyDrop::new(t);\n}"
PREFIX = b"use std::mem::ManuallyDrop;\n\nunsafe fn checked_forget_generic<T>(t: T)\n"
GHOST = (b"\n/*@\nreq thread_token(?tid) &*& tid == currentThread;\n@*/"
         b"\n/*@\nens thread_token(tid);\n@*/"
         b"\n/*@\non_unwind_ens false;\n@*/\n")
VERIFIED = PREFIX + GHOST + FORGET_BODY + b"\n"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError(reason)


def strip_ghost(data: bytes) -> bytes:
    return re.sub(rb"/\*@.*?@\*/", b"", data, flags=re.S)


ORIGINAL = strip_ghost(VERIFIED)


def strict_classifier():
    path = Path(__file__).with_name("forget-evidence-classifier.py")
    spec = importlib.util.spec_from_file_location("forget_evidence_classifier", path)
    require(spec is not None and spec.loader is not None,
            "strict forget evidence classifier missing")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def certificate(repo: Path) -> dict:
    expected = {
        "mem": ("library/core/src/mem/mod.rs", MEM_SHA),
        "manually_drop": ("library/core/src/mem/manually_drop.rs", MANUALLY_DROP_SHA),
        "maybe_dangling": ("library/core/src/mem/maybe_dangling.rs", MAYBE_DANGLING_SHA),
    }
    for name, (relative, digest) in expected.items():
        require(sha((repo / relative).read_bytes()) == digest,
                f"pinned {name} source differs")
    mem = (repo / expected["mem"][0]).read_bytes()
    require(mem.count(FORGET_SOURCE) == 1 and VERIFIED.count(FORGET_BODY) == 1,
            "exact core forget body differs")
    require(sha((repo / "research/challenge-8/verifast-select-pointer-drop.patch")
                .read_bytes()) == PATCH_SHA, "frozen v4 patch differs")
    require(strip_ghost(VERIFIED) == ORIGINAL and
            ORIGINAL.count(b"unsafe fn checked_forget_generic<T>(t: T)") == 1 and
            VERIFIED.count(b"unsafe fn ") == 1,
            "standalone single-function source differs")
    return {
        "classification": "SOURCE_LINKED_DIAGNOSTIC_ONLY",
        "accepted_component": False, "actual_redirected": False,
        "profile": PROFILE, "patch_sha256": PATCH_SHA,
        "std_source_sha256": {name: digest for name, (_, digest) in expected.items()},
        "forget_body_sha256": sha(FORGET_BODY),
        "predeclared_functions": ["checked_forget_generic"],
        "expected_timed_verifier_functions": list(EXPECTED_TIMED_FUNCTIONS),
        "by_value_premise": "thread_token(?tid) &*& tid == currentThread",
        "post": "thread_token(tid); on_unwind_ens false",
        "trusted_boundary": "existing ManuallyDrop::new identity lowering",
        "no_guard_own_or_generic_safe_forget_summary": True,
    }


def fixture(evidence: Path, source_certificate: dict) -> dict:
    original = evidence / "original"
    verified = evidence / "verified"
    original.mkdir(parents=True)
    verified.mkdir()
    (original / "lib.rs").write_bytes(ORIGINAL)
    (verified / "lib.rs").write_bytes(VERIFIED)
    record = {
        "source_certificate": source_certificate,
        "original_sha256": sha(ORIGINAL),
        "verified_sha256": sha(VERIFIED),
        "ghost_strip_identity": strip_ghost(VERIFIED) == ORIGINAL,
        "predeclared_functions": ["checked_forget_generic"],
        "original_body_count": ORIGINAL.count(FORGET_BODY),
        "verified_body_count": VERIFIED.count(FORGET_BODY),
    }
    require(record["ghost_strip_identity"] and
            record["original_body_count"] == record["verified_body_count"] == 1,
            "S7b source construction differs")
    (evidence / "fixture.json").write_text(json.dumps(record, indent=2,
        sort_keys=True) + "\n")
    return record


def run_stage(name: str, argv: list[str], root: Path, env: dict,
              fixture_record: dict, seconds: int,
              stdin_name: str | None = None,
              stdout_name: str | None = None) -> dict:
    paths = (root / "original/lib.rs", root / "verified/lib.rs")
    expected = {"original/lib.rs": fixture_record["original_sha256"],
                "verified/lib.rs": fixture_record["verified_sha256"]}
    before = {str(p.relative_to(root)): sha(p.read_bytes()) for p in paths}
    output = root / (stdout_name or f"{name}.log")
    error_path = root / f"{name}-stderr.log" if stdout_name else output
    with output.open("wb") as stdout:
        stderr = error_path.open("wb") if error_path != output else subprocess.STDOUT
        try:
            with ((root / stdin_name).open("rb") if stdin_name else
                  open(os.devnull, "rb")) as stdin:
                completed = subprocess.run([
                    "/usr/bin/time", "-v", "-o", str(root / f"{name}-resources.txt"),
                    "timeout", "--signal=TERM", "--kill-after=10s", f"{seconds}s",
                    *argv], cwd=root, stdin=stdin, stdout=stdout, stderr=stderr,
                    env=env, check=False)
                status = completed.returncode
        except OSError as exc:
            status = 127
            (stderr if error_path != output else stdout).write(
                f"stage launch error: {exc}\n".encode())
        finally:
            if error_path != output:
                stderr.close()
    after = {str(p.relative_to(root)): sha(p.read_bytes()) for p in paths}
    record = {"argv": argv, "exit": status, "timeout_seconds": seconds,
              "source_before": before, "source_after": after,
              "source_exact": before == after == expected,
              "stdout": output.name, "stderr": error_path.name}
    (root / f"{name}-stage.json").write_text(json.dumps(record, indent=2,
        sort_keys=True) + "\n")
    return record


def run(evidence: Path, args, fixture_record: dict) -> dict:
    env = os.environ.copy()
    for key in ("SORT4_MAYBEUNINIT_REPO_ROOT", "SORT4_SELECT_INTRINSIC_REPO_ROOT",
                "SORT4_POINTER_DROP_REPO_ROOT"):
        env.pop(key, None)
    env["PATH"] = str(args.tool_home / "bin") + os.pathsep + env.get("PATH", "")
    stages = {}
    stages["readonly-export"] = run_stage("readonly-export", [
        str(args.tool_home / "bin/vf-rust-mir-exporter"), "verified/lib.rs",
        f"--sysroot={args.compiler_sysroot}", "--edition", "2021",
        "--crate-type", "lib", "--vf-rust-mir-exporter:preprocess-readonly"],
        evidence, env, fixture_record, 60, stdout_name="readonly-mir.bin")
    if stages["readonly-export"]["exit"] == 0:
        stages["readonly-decode"] = run_stage("readonly-decode", [
            "capnp", "decode", str(args.schema), "VfMir"], evidence, env,
            fixture_record, 60, "readonly-mir.bin", "readonly-mir.txt")
    stages["normal-export"] = run_stage("normal-export", [
        str(args.tool_home / "bin/vf-rust-mir-exporter"), "verified/lib.rs",
        f"--sysroot={args.compiler_sysroot}", "--edition", "2021"],
        evidence, env, fixture_record, 60, stdout_name="normal-mir.bin")
    if stages["normal-export"]["exit"] == 0:
        stages["normal-decode"] = run_stage("normal-decode", [
            "capnp", "decode", str(args.schema), "VfMir"], evidence, env,
            fixture_record, 60, "normal-mir.bin", "normal-mir.txt")
    stages["full-verification"] = run_stage("full-verification", [
        str(args.tool_home / "bin/verifast"), "-rustc_args", "--edition 2021",
        "-verbose", "1", "verified/lib.rs"], evidence, env,
        fixture_record, 120)
    stages["refinement"] = run_stage("refinement", [
        str(args.tool_home / "bin/refinement-checker"), "--rustc-args",
        "--edition 2021", "original/lib.rs", "verified/lib.rs"],
        evidence, env, fixture_record, 60)
    return stages


def classify(evidence: Path, stages: dict) -> dict:
    log = (evidence / "full-verification.log").read_text(errors="replace")
    classifier = strict_classifier()
    strict = classifier.classify_unit(
        log, stages["full-verification"]["exit"], EXPECTED_TIMED_FUNCTIONS,
        positive=True)
    timed_headers = strict["actual_function_names"]
    unit_headers = re.findall(
        r"(?m)^\s*\d+(?:\.\d+)?s: verified/lib\.rs\([^)]*\): "
        r"Verifying function '([^']+)'", log)
    target_functions = [item for item in strict["timed_functions"]
                        if item["function"] == "checked_forget_generic"]
    errors = [line for line in log.splitlines() if ": error:" in line]
    sources_exact = all(record["source_exact"] for record in stages.values())
    full_stages = ("readonly-export", "readonly-decode", "normal-export",
                   "normal-decode", "full-verification", "refinement")
    all_exit_zero = all(stages.get(name, {}).get("exit") == 0 for name in full_stages)
    body_seen = (len(target_functions) == 1 and
                 target_functions[0]["body_execution_seen"])
    return_seen = (len(target_functions) == 1 and
                   target_functions[0]["return_seen"])
    leak_seen = (len(target_functions) == 1 and
                 target_functions[0]["leak_check_seen"])
    no_focus = "-focus" not in stages["full-verification"]["argv"]
    positive = (sources_exact and all_exit_zero and no_focus and
                strict["accepted"] and not errors and
                unit_headers == ["checked_forget_generic"] and
                len(target_functions) == 1 and body_seen and return_seen and leak_seen)
    result = {
        "classification": "DIAGNOSTIC_POSITIVE" if positive else "INCONCLUSIVE",
        "accepted_component": False, "actual_redirected": False,
        "generic_safe_forget_proved": False,
        "source_integrity": sources_exact,
        "all_required_stage_exits_zero": all_exit_zero,
        "predeclared_functions": ["checked_forget_generic"],
        "expected_timed_verifier_functions": EXPECTED_TIMED_FUNCTIONS,
        "timed_verifier_headers": timed_headers,
        "unit_verifier_headers": unit_headers,
        "exact_predeclared_header_set":
            unit_headers == ["checked_forget_generic"],
        "target_header_count": len(target_functions),
        "strict_full_unit_evidence": strict,
        "target_body_execution": body_seen,
        "target_return": return_seen,
        "target_leak_check": leak_seen,
        "dead_code_gate_complete": stages["full-verification"]["exit"] == 0,
        "first_error": errors[0] if errors else None,
        "all_errors": errors,
        "normal_mir_sha256": sha((evidence / "normal-mir.txt").read_bytes())
            if (evidence / "normal-mir.txt").exists() else None,
        "readonly_mir_sha256": sha((evidence / "readonly-mir.txt").read_bytes())
            if (evidence / "readonly-mir.txt").exists() else None,
        "stages": stages,
    }
    (evidence / "summary.json").write_text(json.dumps(result, indent=2,
        sort_keys=True) + "\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--construction-preflight", action="store_true")
    parser.add_argument("--preflight-manifest", type=Path)
    parser.add_argument("--tool-home", type=Path)
    parser.add_argument("--schema", type=Path)
    parser.add_argument("--compiler-sysroot")
    args = parser.parse_args()
    require(args.construction_preflight != bool(args.preflight_manifest),
            "choose hosted preflight or exact manifest-bound full diagnostic")
    require(os.environ.get("GITHUB_ACTIONS") == "true" and
            os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted" and
            os.environ.get("RUNNER_OS") == "Linux" and
            os.environ.get("SORT4_SELECT_PROFILE") == PROFILE,
            "S7b needs frozen v4 GitHub-hosted profile")
    for key in ("SORT4_MAYBEUNINIT_REPO_ROOT", "SORT4_SELECT_INTRINSIC_REPO_ROOT",
                "SORT4_POINTER_DROP_REPO_ROOT"):
        require(key not in os.environ, "S7b cannot activate admission routes")
    repo = Path(__file__).resolve().parents[2]
    require(strict_classifier().self_test()["pass"],
            "strict timed-header classifier self-test failed")
    source_certificate = certificate(repo)
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=False)
    record = fixture(evidence, source_certificate)
    if args.construction_preflight:
        (evidence / "construction-preflight.json").write_text(json.dumps(record,
            indent=2, sort_keys=True) + "\n")
        print(json.dumps({"classification": "DIAGNOSTIC_CONSTRUCTION_PREFLIGHT",
                          "source_exact": True}))
        return
    require(args.tool_home is not None and args.schema is not None and
            args.compiler_sysroot is not None,
            "full diagnostic requires frozen tools, schema, sysroot")
    require(json.loads(args.preflight_manifest.read_text()) == record,
            "new S7b source pair differs from hosted preflight")
    stages = run(evidence, args, record)
    result = classify(evidence, stages)
    print(json.dumps({"classification": result["classification"],
                      "all_required_stage_exits_zero":
                          result["all_required_stage_exits_zero"]}))


if __name__ == "__main__":
    main()
