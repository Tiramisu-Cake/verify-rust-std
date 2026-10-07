#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""One hosted, deadline-bounded G1 proof matrix and A1 MIR diagnostic.

This driver builds no tools and changes no installed specification. G1 status
is experimental even when every case passes. A1 only captures source/MIR;
absence of a pointer-only primitive rule remains INCONCLUSIVE.
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


def require(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)


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
G1 = load(HERE / "prepare-forget-frames.py", "overnight_g1_driver")
A1 = load(HERE / "prepare-assume-init-2610.py", "overnight_a1_driver")
ACTUAL = load(HERE / "prepare-actual-helper-capture.py", "overnight_actual_driver")
CLASSIFIER = load(HERE.parent / "forget-evidence-classifier.py",
                  "overnight_forget_strict_classifier")
STAGE_NAMES = (
    "readonly-export", "readonly-decode", "normal-export", "normal-decode",
    "full-verification", "refinement",
)
G1_PREAMBLE_DEFAULT = (
    "u32_sync", "u32_share_mono", "init_ref_readonly_points_to_shared",
    "std::mem::close_MaybeUninit_pointer_own",
    "std::mem::select_MaybeUninit_pointer_own",
    "std::ptr::pointer_drop_glue_identity",
)
ERR = re.compile(r"^(?P<file>.+?)\((?P<line>\d+),(?P<cols>[^)]*)\): error: (?P<message>.*)$")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source_hashes(case: Path) -> dict[str, str]:
    return {relative: digest((case / relative).read_bytes()) for relative in
            ("original/lib.rs", "verified/lib.rs")}


def run_stage(case: Path, name: str, command: list[str], args,
              *, stdin_file: str | None = None, stdout_file: str | None = None,
              cap_seconds: int = 100) -> dict:
    remaining = args.deadline_epoch - time.time() - 12
    if remaining < 5:
        return {"name": name, "status": "SKIPPED_DEADLINE", "exit": None,
                "remaining_seconds": remaining}
    timeout_seconds = max(5, min(cap_seconds, int(remaining)))
    before = source_hashes(case)
    stdout_path = case / (stdout_file or f"{name}.log")
    stderr_path = case / f"{name}-stderr.log" if stdout_file else stdout_path
    env = os.environ.copy()
    env["PATH"] = str(args.tool_home / "bin") + os.pathsep + env.get("PATH", "")
    env.pop("SORT4_MAYBEUNINIT_REPO_ROOT", None)
    env.pop("SORT4_SELECT_INTRINSIC_REPO_ROOT", None)
    env.pop("SORT4_POINTER_DROP_REPO_ROOT", None)
    with ((case / stdin_file).open("rb") if stdin_file else
          open(os.devnull, "rb")) as inp:
        with stdout_path.open("wb") as out:
            if stderr_path != stdout_path:
                with stderr_path.open("wb") as err:
                    completed = subprocess.run(
                        ["timeout", "--signal=TERM", "--kill-after=10s",
                         f"{timeout_seconds}s", *command],
                        cwd=case, stdin=inp, stdout=out, stderr=err,
                        env=env, check=False)
            else:
                completed = subprocess.run(
                    ["timeout", "--signal=TERM", "--kill-after=10s",
                     f"{timeout_seconds}s", *command],
                    cwd=case, stdin=inp, stdout=out,
                    stderr=subprocess.STDOUT, env=env, check=False)
    after = source_hashes(case)
    record = {"name": name, "argv": command, "exit": completed.returncode,
              "timeout_seconds": timeout_seconds,
              "status": "RAN" if completed.returncode != 124 else "TIMED_OUT",
              "source_before": before, "source_after": after,
              "source_unchanged": before == after,
              "stdout": stdout_path.name, "stderr": stderr_path.name}
    (case / f"{name}-stage.json").write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n")
    return record


def run_case(case: Path, args, *, prove: bool) -> dict:
    exporter = str(args.tool_home / "bin/vf-rust-mir-exporter")
    stages = {}
    stages["readonly-export"] = run_stage(case, "readonly-export", [
        exporter, "verified/lib.rs", f"--sysroot={args.compiler_sysroot}",
        "--edition", "2021", "--crate-type", "lib",
        "--vf-rust-mir-exporter:preprocess-readonly"], args,
        stdout_file="readonly-mir.bin", cap_seconds=80)
    if stages["readonly-export"]["exit"] == 0:
        stages["readonly-decode"] = run_stage(case, "readonly-decode", [
            "capnp", "decode", str(args.schema), "VfMir"], args,
            stdin_file="readonly-mir.bin", stdout_file="readonly-mir.txt",
            cap_seconds=40)
    stages["normal-export"] = run_stage(case, "normal-export", [
        exporter, "verified/lib.rs", f"--sysroot={args.compiler_sysroot}",
        "--edition", "2021"], args,
        stdout_file="normal-mir.bin", cap_seconds=80)
    if stages["normal-export"]["exit"] == 0:
        stages["normal-decode"] = run_stage(case, "normal-decode", [
            "capnp", "decode", str(args.schema), "VfMir"], args,
            stdin_file="normal-mir.bin", stdout_file="normal-mir.txt",
            cap_seconds=40)
    frontend_four_ok = all(stages.get(name, {}).get("exit") == 0 for name in (
        "readonly-export", "readonly-decode", "normal-export", "normal-decode"))
    if prove and frontend_four_ok:
        stages["full-verification"] = run_stage(case, "full-verification", [
            str(args.tool_home / "bin/verifast"), "-rustc_args", "--edition 2021",
            "-verbose", "1", "verified/lib.rs"], args, cap_seconds=100)
    if frontend_four_ok:
        stages["refinement"] = run_stage(case, "refinement", [
            str(args.tool_home / "bin/refinement-checker"), "--rustc-args",
            "--edition 2021", "original/lib.rs", "verified/lib.rs"], args,
            cap_seconds=70)
    return stages


def line_of(source: bytes, fragment: bytes) -> int:
    lines = source.splitlines()
    indexes = [index for index, line in enumerate(lines, 1) if fragment in line]
    require(len(indexes) == 1,
            f"source obligation is absent/ambiguous: {fragment.decode()}")
    return indexes[0]


def negative_obligation(variant: str, source: bytes) -> dict | None:
    if variant in G1.POSITIVES:
        return None
    helper = variant in {"thread_loss", "thread_duplication"}
    function = "checked_forget_generic" if helper else "checked_forget_frame_probe"
    if variant == "contradictory_pre":
        return {"function": function, "kind": "dead_code",
                "line": line_of(source, b"pub unsafe fn checked_forget_frame_probe")}
    if variant == "assert_false":
        return {"function": function, "kind": "assertion",
                "line": line_of(source, b"//@ assert false;"),
                "message_contains": "Cannot prove false"}
    if variant == "no_thread":
        return {"function": function, "kind": "call_precondition",
                "line": line_of(source, b"req thread_token(?tid) &*& tid == currentThread;"),
                "message_contains": "thread_token"}
    if variant.endswith("_loss"):
        if helper:
            # A helper leak is reported at its return/closing brace.
            closing = source.index(G1.FORGET_BODY) + len(G1.FORGET_BODY) - 1
            line = source[:closing].count(b"\n") + 1
        else:
            line = len(source.splitlines())
        return {"function": function, "kind": "leak", "line": line,
                "message_contains": "Function leaks heap chunks"}
    if variant in {"frame_duplication", "frame_wrong_value", "cell_duplication",
                   "cell_wrong_value", "thread_duplication", "false_post", "no_cell"}:
        contract_lines = [index for index, line in enumerate(source.splitlines(), 1)
                          if line.startswith(b"ens ")]
        require(len(contract_lines) == 2, "G1 contract post lines changed")
        line = contract_lines[0] if helper else contract_lines[1]
        if variant in {"frame_wrong_value", "cell_wrong_value", "false_post"}:
            message = "Cannot prove"
        else:
            message = "No matching heap chunks"
        return {"function": function, "kind": "postcondition", "line": line,
                "message_contains": message}
    return {"function": function, "kind": "call_precondition",
            "line": line_of(source, b"checked_forget_generic(t);"),
            "message_contains": "points_to"}


def error_info(log: str) -> list[dict]:
    return [match.groupdict() | {"raw": line}
            for line in log.splitlines()
            if (match := ERR.match(line)) is not None]


def classify_g1(case: Path, stages: dict, variant: str,
                s6_specs: tuple[str, ...]) -> dict:
    verified = (case / "verified/lib.rs").read_bytes()
    original = (case / "original/lib.rs").read_bytes()
    fixture = json.loads((case / "fixture.json").read_text())
    frontend = all(stages.get(name, {}).get("exit") == 0 for name in (
        "readonly-export", "readonly-decode", "normal-export",
        "normal-decode", "refinement"))
    source_ok = (G1.strip_ghost(verified) == original and
                 digest(verified) == fixture["verified_sha256"] and
                 digest(original) == fixture["original_sha256"] and
                 all(record.get("source_unchanged") for record in stages.values()
                     if record.get("status") == "RAN"))
    verifier = stages.get("full-verification", {})
    log = (case / "full-verification.log").read_text(errors="replace") if (
        case / "full-verification.log").exists() else ""
    timed = CLASSIFIER.timed_functions(log)
    names = [item.function for item in timed]
    expected = [*s6_specs, "checked_forget_generic"]
    if variant not in {"thread_loss", "thread_duplication",
                       "contradictory_pre"}:
        expected.append("checked_forget_frame_probe")
    obligation = negative_obligation(variant, verified)
    errors = error_info(log)
    exact_timed = names == expected
    no_setup = frontend and source_ok and verifier.get("exit") is not None
    positive = (variant in G1.POSITIVES and no_setup and
                verifier["exit"] == 0 and exact_timed and not errors and
                all(item.body_execution_seen and item.return_seen and
                    item.leak_check_seen for item in timed) and
                "dead code" not in log.lower())
    negative = False
    if (variant in G1.NEGATIVES and no_setup and verifier["exit"] == 1 and
            exact_timed and obligation is not None):
        if obligation["kind"] == "dead_code":
            # The mandatory dead-code gate emits a distinct diagnostic rather
            # than a `: error:` line.  Require the target public function's
            # source span and actual unreachability inside that function.
            marker = f"verified/lib.rs({obligation['line']},1-"
            dead_lines = [line for line in log.splitlines()
                          if line.startswith(marker) and line.endswith(": dead code")]
            negative = (not errors and len(dead_lines) >= 1 and
                        any("dead code" in line.lower() and
                            "verified/lib.rs(" in line for line in log.splitlines()))
        elif len(errors) != 1:
            negative = False
        else:
            first = errors[0]
            location = (first["file"].endswith("verified/lib.rs") and
                        int(first["line"]) == obligation["line"])
            message = obligation.get("message_contains", "") in first["message"]
            function_body = next((item for item in timed
                                  if item.function == obligation["function"]), None)
            reached = function_body is not None and function_body.body_execution_seen
            if obligation["kind"] == "leak":
                reached = reached and function_body.return_seen and function_body.leak_check_seen
            negative = bool(location and message and reached)
    return {
        "variant": variant,
        "classification": "EXPERIMENTAL_POSITIVE" if positive else
                          "INTENDED_PROOF_NEGATIVE" if negative else "INCONCLUSIVE",
        "accepted_component": False,
        "actual_helper_proved": False,
        "source_integrity": source_ok,
        "frontend_refinement": frontend,
        "expected_timed_functions": expected,
        "actual_timed_functions": names,
        "exact_timed_functions": exact_timed,
        "first_error": errors[0] if errors else None,
        "error_count": len(errors),
        "expected_obligation": obligation,
        "verifier_exit": verifier.get("exit"),
        "stages": stages,
    }


def run_all(args) -> dict:
    require(os.environ.get("GITHUB_ACTIONS") == "true" and
            os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted" and
            os.environ.get("RUNNER_OS") == "Linux",
            "helper checks require GitHub-hosted Linux Actions")
    require(CLASSIFIER.self_test()["pass"],
            "strict timed-header classifier self-test failed")
    evidence = args.evidence.resolve()
    require(not evidence.exists(), f"refusing to overwrite {evidence}")
    evidence.mkdir(parents=True)
    variants = tuple(args.g1_variants.split(",")) if args.g1_variants else G1.VARIANTS
    require(variants and len(set(variants)) == len(variants) and
            all(item in G1.VARIANTS for item in variants),
            "G1 variant list invalid")
    s6_specs = tuple(args.s6_specs.split(",")) if args.s6_specs else G1_PREAMBLE_DEFAULT
    require(len(set(s6_specs)) == len(s6_specs), "S6 expected header list duplicated")
    results: dict[str, object] = {"g1": [], "a1": {}, "actual": None}
    # Capture both new std dependencies first; a long G1 negative matrix must
    # not consume the entire single hosted job before their MIR is recorded.
    for target in ("method", "transmute"):
        if args.deadline_epoch - time.time() < 35:
            results["a1"][target] = {"classification": "NOT_RUN_DEADLINE"}
            continue
        case = evidence / f"a1-{target}"
        try:
            if target == "method":
                A1.write_fixture(REPO, case, "initialized")
            else:
                A1.write_transmute_fixture(REPO, case)
            stages = run_case(case, args, prove=True)
            capture = None
            if stages.get("normal-decode", {}).get("exit") == 0:
                capture = A1.capture_mir(case / "normal-mir.txt",
                                         evidence / f"a1-{target}-capture", target)
            result = {"classification": "UNREVIEWED_CAPTURE" if capture else
                                        "INCONCLUSIVE",
                      "target": target, "capture": capture, "stages": stages,
                      "primitive_rule_accepted": False}
        except Exception as exc:
            result = {"classification": "INCONCLUSIVE", "target": target,
                      "harness_exception": f"{type(exc).__name__}: {exc}"}
        (evidence / f"a1-{target}-result.json").write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n")
        results["a1"][target] = result
    for variant in variants:
        case = evidence / f"g1-{variant}"
        try:
            G1.write_case(REPO, case, variant)
            stages = run_case(case, args, prove=True)
            result = classify_g1(case, stages, variant, s6_specs)
        except Exception as exc:
            result = {"variant": variant, "classification": "INCONCLUSIVE",
                      "harness_exception": f"{type(exc).__name__}: {exc}"}
        (evidence / f"g1-{variant}-result.json").write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n")
        results["g1"].append(result)
        if args.deadline_epoch - time.time() < 35:
            break
    if args.actual_capture and args.deadline_epoch - time.time() >= 35:
        case = evidence / "actual-helper"
        try:
            ACTUAL.write_fixture(REPO, case)
            stages = run_case(case, args, prove=True)
            capture = None
            if stages.get("normal-decode", {}).get("exit") == 0:
                capture = ACTUAL.capture_mir(case / "normal-mir.txt",
                                             evidence / "actual-helper-capture")
            result = {"classification": "UNREVIEWED_CAPTURE" if capture else
                                        "INCONCLUSIVE", "capture": capture,
                      "stages": stages, "actual_helper_proved": False}
        except Exception as exc:
            result = {"classification": "INCONCLUSIVE",
                      "harness_exception": f"{type(exc).__name__}: {exc}"}
        (evidence / "actual-helper-result.json").write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n")
        results["actual"] = result
    observed_variants = {item["variant"] for item in results["g1"]}
    results["g1_all_declared_executed"] = (
        observed_variants == set(G1.VARIANTS))
    results["g1_all_positives_experimental"] = (
        set(G1.POSITIVES) <= observed_variants and all(
        item.get("classification") == "EXPERIMENTAL_POSITIVE"
        for item in results["g1"] if item["variant"] in G1.POSITIVES))
    results["g1_all_negatives_intended"] = (
        set(G1.NEGATIVES) <= observed_variants and all(
        item.get("classification") == "INTENDED_PROOF_NEGATIVE"
        for item in results["g1"] if item["variant"] in G1.NEGATIVES))
    results["accepted_component"] = False
    results["overall_classification"] = "EXPERIMENTAL_DIAGNOSTIC_ONLY"
    (evidence / "summary.json").write_text(json.dumps(results, indent=2,
                                                       sort_keys=True) + "\n")
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool-home", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--compiler-sysroot", required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--deadline-epoch", type=int, required=True)
    parser.add_argument("--s6-specs", default=None,
                        help="ordered comma-separated expected S6 timed preamble")
    parser.add_argument("--g1-variants", default=None,
                        help="comma-separated subset, default all declared variants")
    parser.add_argument("--actual-capture", action="store_true")
    args = parser.parse_args()
    result = run_all(args)
    print(json.dumps({key: result[key] for key in (
        "g1_all_declared_executed", "g1_all_positives_experimental",
        "g1_all_negatives_intended", "overall_classification")},
        indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
