#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted G1 call-CFG proof/admission matrix; never classifies actual std."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
CALLEE_SHA = "c493d14bf8a7bcbd3d3ab98655218798470a46042c5001572b50a3d4a3fff154"
CALLER_SHA = "1f1f8e96cc210ea50d53744e6aa41cf73e5eff81ae5f10be777eb05d8a706504"
POSITIVE_ORIGINAL_SHA = "d355336bb9e2542be2ee2e9199a6421440194661a1cdcc51181d36bfa7c480cb"
POSITIVE_VERIFIED_SHA = "57ba4210babe42d84dde65722e4be54ac176ce6a27264dfdd64a12f9d822cee0"
VARIANTS = ("positive", "false_post", "frame_loss", "frame_duplication",
            "thread_loss", "thread_duplication", "wrong_value",
            "wrong_callee", "weakened_callee_unwind")
ADMISSION_FATAL = {
    "wrong_callee":
        'Fatal error: exception Failure("G1-CALL-CFG: source/MIR certificate mismatch: exact caller post or runtime body/source suffix")',
    "weakened_callee_unwind":
        'Fatal error: exception Failure("G1-CALL-CFG: source/MIR certificate mismatch: exact checked callee and caller source prefix")',
}


def exact_admission_rejection(variant: str, *, frontend: bool,
                              source_integrity: bool, proof: int | None,
                              headers: dict, fatal: list[str]) -> bool:
    return (variant in ADMISSION_FATAL and frontend and source_integrity and
            proof in (1, 2) and
            headers == {LANE.CALLEE_NAME: 0, LANE.CALLER_NAME: 0} and
            fatal == [ADMISSION_FATAL[variant]])


def classifier_guard_selfcheck() -> None:
    """Hosted-only replay of O18's common early refusal and both target reasons."""
    zero = {LANE.CALLEE_NAME: 0, LANE.CALLER_NAME: 0}
    common = ['Fatal error: exception Failure("G1-CALL-CFG: source/MIR '
              'certificate mismatch: callee/caller signature source span")']
    for variant, expected in ADMISSION_FATAL.items():
        baseline = dict(frontend=True, source_integrity=True, proof=2,
                        headers=zero)
        HELPER.require(not exact_admission_rejection(
            variant, **baseline, fatal=common),
            "O18 common signature-span refusal misclassified")
        HELPER.require(exact_admission_rejection(
            variant, **baseline, fatal=[expected]),
            "specific admission refusal not recognized")
        HELPER.require(not exact_admission_rejection(
            variant, **(baseline | {"frontend": False}), fatal=[expected]) and
            not exact_admission_rejection(
                variant, **(baseline | {"source_integrity": False}),
                fatal=[expected]) and
            not exact_admission_rejection(
                variant, **(baseline | {"headers":
                    {LANE.CALLEE_NAME: 1, LANE.CALLER_NAME: 0}}),
                fatal=[expected]),
            "admission refusal missing setup or no-body guard")


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


LANE = load(HERE / "check-forget-call-lane.py", "overnight_g1_cfg_lane")
HELPER = LANE.HELPER
CALLEE = LANE.CALLEE
A1 = LANE.A1


def source_pair(variant: str) -> tuple[bytes, bytes, dict]:
    HELPER.require(variant in VARIANTS, "unknown G1 CFG variant")
    original, verified, callee_fixture = LANE.source_pair()
    normal_post = b"ens thread_token(tid) &*& *frame |-> flag;"
    replacements = {
        "false_post": b"ens thread_token(tid) &*& *frame |-> flag &*& false;",
        "frame_loss": b"ens thread_token(tid);",
        "frame_duplication":
            b"ens thread_token(tid) &*& *frame |-> flag &*& *frame |-> flag;",
        "thread_loss": b"ens *frame |-> flag;",
        "thread_duplication":
            b"ens thread_token(tid) &*& thread_token(tid) &*& *frame |-> flag;",
        "wrong_value": b"ens thread_token(tid) &*& *frame |-> !flag;",
    }
    if variant in replacements:
        HELPER.require(verified.count(normal_post) == 1,
                       "caller normal post anchor changed")
        verified = verified.replace(normal_post, replacements[variant], 1)
    elif variant == "wrong_callee":
        call = b"checked_forget_generic(t);"
        HELPER.require(verified.count(call) == 1, "caller call anchor changed")
        verified = verified.replace(call, b"std::mem::forget(t);", 1)
    elif variant == "weakened_callee_unwind":
        # Admission control only: the local callee loses its false-unwind
        # certificate while its executable Rust and MIR stay unchanged.
        anchor = b"on_unwind_ens false;"
        HELPER.require(verified.count(anchor) == 2,
                       "both callee and caller unwind contracts required")
        verified = verified.replace(anchor, b"on_unwind_ens true;", 1)
    original = CALLEE.G1.strip_ghost(verified)
    if variant not in ("wrong_callee",):
        HELPER.require(HELPER.digest(original) == POSITIVE_ORIGINAL_SHA,
                       "proof variant changed executable Rust")
    HELPER.require(CALLEE.G1.strip_ghost(verified) == original,
                   "verified/original ghost-strip mismatch")
    return original, verified, callee_fixture


def source_gate(variant: str, original: bytes, verified: bytes) -> bool:
    if variant in ("weakened_callee_unwind", "wrong_callee"):
        return False
    if variant == "positive":
        return (HELPER.digest(original) == POSITIVE_ORIGINAL_SHA and
                HELPER.digest(verified) == POSITIVE_VERIFIED_SHA)
    return HELPER.digest(original) == POSITIVE_ORIGINAL_SHA and (
            verified.count(b"pub unsafe fn checked_forget_generic<T>(t: T)") == 1 and
            verified.count(b"on_unwind_ens false;") == 2)


def graph_gate(case: Path, variant: str) -> tuple[bool, dict]:
    graphs = {}
    for mode in ("normal", "readonly"):
        text = (case / f"{mode}-mir.txt").read_text(errors="strict")
        graphs[mode] = {}
        for function in (LANE.CALLEE_NAME, LANE.CALLER_NAME):
            defpath, body = A1.complete_function_record(text, function)
            digest = HELPER.digest(body.encode())
            graphs[mode][function] = {"defpath": defpath, "sha256": digest}
            (case / f"{mode}-{function}-full-mir.txt").write_text(body)
            if function == LANE.CALLEE_NAME:
                if variant == "weakened_callee_unwind":
                    # This control changes exactly one ghost contract field;
                    # every typed MIR field and span must stay identical.
                    weakened = 'raw = "/*@\\non_unwind_ens true;\\n@*/"'
                    original = 'raw = "/*@\\non_unwind_ens false;\\n@*/"'
                    HELPER.require(body.count(weakened) == 1 and
                                   HELPER.digest(body.replace(
                                       weakened, original, 1).encode()) ==
                                   CALLEE_SHA,
                                   f"{mode} weakened callee graph drift")
                else:
                    HELPER.require(digest == CALLEE_SHA,
                                   f"{mode} checked generic callee graph drift")
            if function == LANE.CALLER_NAME and variant in (
                    "positive", "weakened_callee_unwind"):
                HELPER.require(digest == CALLER_SHA,
                               f"{mode} exact caller graph drift")
            if function == LANE.CALLER_NAME and variant != "wrong_callee":
                HELPER.require(
                    body.count('name = "checked_forget_generic"') == 1 and
                    'move = (' in body and 'projection = []' in body and
                    'unwindAction = (cleanup = ' in body and
                    'target = (something = ' in body,
                    f"{mode} caller typed call/cleanup shape changed")
    return True, graphs


def classify(case: Path, variant: str, stages: dict, graphs: dict,
             source_admitted: bool) -> dict:
    log = (case / "full-verification.log").read_text(errors="replace") if (
        case / "full-verification.log").is_file() else ""
    errors = HELPER.error_info(log)
    headers = {name: len(re.findall(
        rf"(?m)^\s*\d+(?:\.\d+)?s: verified/lib\.rs\([^)]*\): Verifying function '{name}'",
        log)) for name in (LANE.CALLEE_NAME, LANE.CALLER_NAME)}
    frontend = all(stages.get(name, {}).get("exit") == 0 for name in (
        "normal-export", "normal-decode", "readonly-export",
        "readonly-decode", "refinement"))
    proof = stages.get("full-verification", {}).get("exit")
    source_integrity = CALLEE.G1.strip_ghost(
        (case / "verified/lib.rs").read_bytes()) == (
        case / "original/lib.rs").read_bytes() and all(
            stage.get("source_unchanged") is True for stage in stages.values()
            if stage.get("status") == "RAN")
    fatal = [line for line in log.splitlines()
             if line.startswith("Fatal error:")]
    caller_ens_lines = [index for index, line in enumerate(
        (case / "verified/lib.rs").read_bytes().splitlines(), 1)
        if line.strip().startswith(b"ens ")]
    caller_ens_line = caller_ens_lines[-1] if len(caller_ens_lines) == 2 else None
    classification = "INCONCLUSIVE"
    preproof_rejection = exact_admission_rejection(
        variant, frontend=frontend, source_integrity=source_integrity,
        proof=proof, headers=headers, fatal=fatal)
    if variant == "weakened_callee_unwind" and not source_admitted and \
            preproof_rejection:
        classification = "INTENDED_SOURCE_CERT_REJECTION"
    elif variant == "wrong_callee" and not source_admitted and \
            preproof_rejection:
        classification = "INTENDED_EXACT_SOURCE_ADMISSION_REJECTION"
    elif frontend and source_integrity and source_admitted and headers == {
            LANE.CALLEE_NAME: 1, LANE.CALLER_NAME: 1}:
        if variant == "positive" and proof == 0 and not errors and \
                "dead code" not in log:
            classification = "EXPERIMENTAL_G1_CALL_PROOF_CANDIDATE"
        elif variant in ("false_post", "frame_duplication",
                         "thread_duplication", "wrong_value") and proof == 1 and \
                len(errors) == 1 and \
                errors[0]["file"] == "verified/lib.rs" and \
                caller_ens_line is not None and \
                errors[0]["line"] == str(caller_ens_line) and \
                ("Cannot prove false" in errors[0]["message"] if
                 variant == "false_post" else
                 errors[0]["message"] == "Cannot prove flag == !(flag)" if
                 variant == "wrong_value" else
                 "No matching heap chunks" in errors[0]["message"]):
            classification = "INTENDED_NORMAL_POST_NEGATIVE"
        elif variant in ("frame_loss", "thread_loss") and proof == 1 and \
                len(errors) == 1 and "leak" in errors[0]["message"].lower() and \
                errors[0]["file"] == "verified/lib.rs":
            classification = "INTENDED_RESOURCE_LEAK_NEGATIVE"
    return {
        "classification": classification, "variant": variant,
        "component_accepted": False, "actual_safe_forget_linked": False,
        "source_admitted": source_admitted, "frontend_refinement": frontend,
        "source_integrity": source_integrity, "fatal": fatal,
        "graphs": graphs, "callee_caller_headers": headers,
        "full_verifier_exit": proof, "first_error": errors[0] if errors else None,
        "stages": stages,
    }


def main() -> None:
    HELPER.require((os.environ.get("GITHUB_ACTIONS"),
                    os.environ.get("RUNNER_ENVIRONMENT"),
                    os.environ.get("RUNNER_OS")) ==
                   ("true", "github-hosted", "Linux"),
                   "G1 CFG matrix requires GitHub-hosted Linux")
    classifier_guard_selfcheck()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool-home", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--compiler-sysroot", required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--deadline-epoch", type=int, required=True)
    parser.add_argument("--variant", choices=VARIANTS, default="positive")
    args = parser.parse_args()
    args.evidence = args.evidence.resolve()
    HELPER.require(not args.evidence.exists(), "refusing to overwrite evidence")
    original, verified, _ = source_pair(args.variant)
    case = args.evidence
    (case / "original").mkdir(parents=True)
    (case / "verified").mkdir()
    (case / "original/lib.rs").write_bytes(original)
    (case / "verified/lib.rs").write_bytes(verified)
    (case / "fixture.json").write_text(json.dumps({
        "variant": args.variant, "original_sha256": HELPER.digest(original),
        "verified_sha256": HELPER.digest(verified),
        "callee_source_certificate": CALLEE.G1.source_certificate(LANE.REPO),
        "same_unit_callee_required": True,
        "normal_post_preserved_for_positive": True,
        "callee_unwind_post": "true" if args.variant ==
            "weakened_callee_unwind" else "false",
        "caller_unwind_post": "false", "source_only_diagnostic": True,
    }, indent=2, sort_keys=True) + "\n")
    source_admitted = source_gate(args.variant, original, verified)
    os.environ["SORT4_G1_CALL_REPO_ROOT"] = str(LANE.REPO)
    stages = HELPER.run_case(case, args, prove=False)
    frontend = all(stages.get(name, {}).get("exit") == 0 for name in (
        "normal-export", "normal-decode", "readonly-export",
        "readonly-decode", "refinement"))
    graphs = {}
    if frontend:
        _, graphs = graph_gate(case, args.variant)
    if frontend and (source_admitted or args.variant in (
            "wrong_callee", "weakened_callee_unwind")):
        stages["full-verification"] = HELPER.run_stage(
            case, "full-verification",
            [str(args.tool_home / "bin/verifast"), "-rustc_args",
             "--edition 2021", "-verbose", "1", "verified/lib.rs"],
            args, cap_seconds=100)
    result = classify(case, args.variant, stages, graphs, source_admitted)
    (case / "summary.json").write_text(json.dumps(
        result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"variant": args.variant,
                      "classification": result["classification"],
                      "first_error": result["first_error"]}), flush=True)


if __name__ == "__main__":
    main()
