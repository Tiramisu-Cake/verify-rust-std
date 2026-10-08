#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted complete-MIR capture of actual owner with same-unit S6 callees.

The frozen S6 actual gate is expected to reject the expanded owner ghost
inventory. The opt-in O21 admission mode still never promotes the helper.
"""

from __future__ import annotations

import argparse
import hashlib
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
    parser.add_argument("--fingerprint-probe", action="store_true",
                        help="fail-closed frontend decoded-body inventory probe")
    parser.add_argument("--owner-admission", action="store_true",
                        help="exact O21 owner-unit admission, experimental")
    parser.add_argument("--admission-control", choices=(
        "positive", "wrong_contract", "wrong_ghost_order", "wrong_owner_pred"),
        default="positive", help="one exact-source admission control")
    args = parser.parse_args()
    PREP.OWNER.require(not (args.fingerprint_probe and args.owner_admission) and
                       (args.owner_admission or
                        args.admission_control == "positive"),
                       "fingerprint probe and admission controls are separate")
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
    if args.admission_control != "positive":
        path = case / "verified/lib.rs"
        verified = path.read_bytes()
        if args.admission_control == "wrong_contract":
            before = b"raw_ptr_own::<Element>()(t, result);"
            after = b"raw_ptr_own::<Element>()(t, true_val);"
        elif args.admission_control == "wrong_ghost_order":
            before = (
                b"    /*@ std::mem::open_MaybeUninit::<*Element>(true_ptr as *std::mem::MaybeUninit<*Element>); @*/\n"
                b"    /*@ std::mem::open_MaybeUninit::<*Element>(false_ptr as *std::mem::MaybeUninit<*Element>); @*/\n")
            after = (
                b"    /*@ std::mem::open_MaybeUninit::<*Element>(false_ptr as *std::mem::MaybeUninit<*Element>); @*/\n"
                b"    /*@ std::mem::open_MaybeUninit::<*Element>(true_ptr as *std::mem::MaybeUninit<*Element>); @*/\n")
        else:
            before = (
                b"    *g.inner |-> ?payload &*& <T>.own(t, payload);\n")
            after = (
                b"    *g.inner |-> ?payload &*& <T>.own(t, payload) &*& true;\n")
        PREP.OWNER.require(verified.count(before) == 1 and before != after,
                           "admission control exact mutation anchor")
        mutated = verified.replace(before, after, 1)
        PREP.OWNER.require(PREP.OWNER.strip_ghost(mutated) ==
                           (case / "original/lib.rs").read_bytes(),
                           "admission control changed executable source")
        path.write_bytes(mutated)
    if args.owner_admission:
        os.environ["SORT4_ACTUAL_OWNER_REPO_ROOT"] = str(REPO)
        os.environ["SORT4_ACTUAL_OWNER_ADMISSION"] = "1"
        os.environ.pop("SORT4_ACTUAL_OWNER_EVIDENCE_DIR", None)
        os.environ.pop("SORT4_ACTUAL_OWNER_FINGERPRINT_RUN", None)
    else:
        os.environ.pop("SORT4_ACTUAL_OWNER_ADMISSION", None)
    if args.fingerprint_probe:
        os.environ["SORT4_ACTUAL_OWNER_REPO_ROOT"] = str(REPO)
        os.environ["SORT4_ACTUAL_OWNER_EVIDENCE_DIR"] = str(case.resolve())
        os.environ["SORT4_ACTUAL_OWNER_FINGERPRINT_RUN"] = "first"
    elif not args.owner_admission:
        os.environ.pop("SORT4_ACTUAL_OWNER_REPO_ROOT", None)
        os.environ.pop("SORT4_ACTUAL_OWNER_EVIDENCE_DIR", None)
        os.environ.pop("SORT4_ACTUAL_OWNER_FINGERPRINT_RUN", None)
    stages = PREP.LINK.run_case(case, args, pointer_drop=True)
    if args.fingerprint_probe and (
            case / "full-verification.log").is_file() and (
            "SORT4-ACTUAL-OWNER: diagnostic refusal: decoded representation "
            "not reviewed; no semantic admission" in
            (case / "full-verification.log").read_text(errors="replace")):
        os.environ["SORT4_ACTUAL_OWNER_FINGERPRINT_RUN"] = "repeat"
        stages["full-verification-repeat"] = PREP.LINK.stage(
            case, "full-verification-repeat",
            [str(args.tool_home / "bin/verifast"), "-rustc_args",
             "--edition 2021", "-verbose", "1", "verified/lib.rs"],
            args, gates=True, pointer_drop=True, cap_seconds=100)
    fingerprints = {}
    if args.fingerprint_probe:
        for label in ("unit", *(f"body-{index}" for index in range(5))):
            first = case / f"actual-owner-{label}-first.marshal"
            repeat = case / f"actual-owner-{label}-repeat.marshal"
            first_bytes = first.read_bytes() if first.is_file() else None
            repeat_bytes = repeat.read_bytes() if repeat.is_file() else None
            fingerprints[label] = {
                "first_sha256": hashlib.sha256(first_bytes).hexdigest()
                    if first_bytes is not None else None,
                "repeat_sha256": hashlib.sha256(repeat_bytes).hexdigest()
                    if repeat_bytes is not None else None,
                "first_bytes": len(first_bytes) if first_bytes is not None
                    else None,
                "repeat_bytes": len(repeat_bytes) if repeat_bytes is not None
                    else None,
                "repeat_identical": first_bytes is not None and
                    repeat_bytes is not None and first_bytes == repeat_bytes,
            }
    graphs = CAPTURE.capture_graph(case, stages)
    log_path = case / "full-verification.log"
    log = log_path.read_text(errors="replace") if log_path.exists() else ""
    errors = CAPTURE.HELPER.error_info(log)
    frontend = all(stages.get(k, {}).get("exit") == 0 for k in (
        "normal-export", "normal-decode", "readonly-export",
        "readonly-decode", "refinement"))
    source_unchanged = all(
        stage.get("source_unchanged") is True
        for stage in stages.values() if stage.get("status") == "RAN")
    admission_gate = (
        "SORT4-ACTUAL-OWNER: exact source and complete decoded MIR admission only"
        in log)
    exact_source_refusal = (
        'Fatal error: exception Failure("SORT4-SELECT-INTRINSIC: '
        'certificate mismatch: owner exact verified source SHA256")')
    fatal = [line for line in log.splitlines()
             if line.startswith("Fatal error:")]
    control_isolated = (
        args.owner_admission and args.admission_control != "positive" and
        frontend and source_unchanged and not admission_gate and
        stages.get("full-verification", {}).get("exit") in (1, 2) and
        len(fatal) == 1 and fatal[0] == exact_source_refusal and
        not errors)
    record = {
        "classification": "LINKED_ACTUAL_OWNER_ADMISSION_EXPERIMENTAL"
            if args.owner_admission else "LINKED_ACTUAL_OWNER_DIAGNOSTIC_ONLY",
        "actual_helper_proved": False,
        "actual_nested_drop_proved": False,
        "actual_safe_forget_linked": False,
        "fingerprint_probe": args.fingerprint_probe,
        "owner_admission": args.owner_admission,
        "admission_control": args.admission_control,
        "owner_admission_gate_passed": admission_gate,
        "admission_control_isolated": control_isolated,
        "fingerprints": fingerprints,
        "fingerprint_repeat_complete": args.fingerprint_probe and all(
            row["repeat_identical"] for row in fingerprints.values()),
        "frontend_refinement": frontend,
        "source_integrity": source_unchanged,
        "full_mir_capture": graphs,
        "frozen_s6_actual_gate_passed":
            "SORT4-SELECT-INTRINSIC: full typed actual MIR graph accepted" in log,
        "first_error": errors[0] if errors else None,
        "fatal": fatal,
        "stages": stages,
    }
    (evidence / "summary.json").write_text(json.dumps(
        record, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: record[key] for key in (
        "classification", "frontend_refinement",
        "frozen_s6_actual_gate_passed", "first_error", "fatal")}), flush=True)


if __name__ == "__main__":
    main()
