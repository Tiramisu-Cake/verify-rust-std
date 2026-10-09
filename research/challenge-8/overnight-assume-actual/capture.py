#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted-only complete nine-body MIR/refinement and optional refusal dump."""

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
        raise RuntimeError(f"missing capture module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PREP = load(HERE / "prepare.py", "nine_body_source")
GUARD = load(HERE.parent / "overnight-guard-actual" /
             "capture-actual-nested-drop.py", "nine_body_guard_capture")
LINK = GUARD.LINK
MIR = GUARD.CAPTURE.A1
DIAGNOSTIC_TEXT = (
    "SORT4-ACTUAL-NESTED-FINGERPRINT: diagnostic refusal: "
    "snapshot complete; no proof rule admitted"
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def clear_semantic_opt_ins() -> None:
    for key in (
        "SORT4_MAYBEUNINIT_REPO_ROOT", "SORT4_SELECT_INTRINSIC_REPO_ROOT",
        "SORT4_POINTER_DROP_REPO_ROOT", "SORT4_GUARD_REPO_ROOT",
        "SORT4_GUARD_TEMPLATE_REPO_ROOT", "SORT4_ACTUAL_OWNER_REPO_ROOT",
        "SORT4_ACTUAL_OWNER_ADMISSION", "SORT4_ACTUAL_FORGET_REPO_ROOT",
        "SORT4_A1_LINK_REPO_ROOT", "SORT4_G1_CALL_REPO_ROOT",
        "SORT4_STRICT_LFT_CUT", "SORT4_HRTB_OUTPUT",
        "SORT4_HRTB_OUTPUT_TARGETS", "SORT4_NESTED_FINGERPRINT_MODE",
        "SORT4_NESTED_FINGERPRINT_EVIDENCE_DIR",
        "SORT4_NESTED_FINGERPRINT_SOURCE_SHA256",
    ):
        os.environ.pop(key, None)


def full_body_capture(case: Path, source: dict, stages: dict) -> dict:
    expected = source["source_order"]
    result = {}
    for mode in ("normal", "readonly"):
        if stages.get(f"{mode}-decode", {}).get("exit") != 0:
            result[mode] = {"classification": "DECODE_UNAVAILABLE"}
            continue
        decoded = (case / f"{mode}-mir.txt").read_text(errors="strict")
        rows = []
        offsets = []
        for index, name in enumerate(expected):
            marker = f'defPath = "{name}"'
            PREP.require(decoded.count(marker) == 1,
                         f"{mode}: nine-body DefPath absent/duplicate: {name}")
            offsets.append(decoded.index(marker))
            actual_name, body = MIR.complete_function_record(decoded, name)
            PREP.require(actual_name == name and body,
                         f"{mode}: complete body identity mismatch: {name}")
            path = case / f"{mode}-body-{index}-full-mir.txt"
            path.write_text(body)
            rows.append({"index": index, "defpath": actual_name,
                         "file": path.name, "bytes": len(body.encode()),
                         "sha256": sha(body.encode())})
        PREP.require(offsets == sorted(offsets),
                     f"{mode}: nine-body source/MIR order changed")
        result[mode] = {
            "classification": "COMPLETE_NINE_BODY_CAPTURE_ONLY",
            "whole_decoded_mir_file": f"{mode}-mir.txt",
            "whole_decoded_mir_sha256": sha(decoded.encode()),
            "exact_body_count_and_order": True,
            "bodies": rows,
        }
    return result


def refusal_fingerprint(case: Path, source: dict, args) -> dict:
    os.environ["SORT4_NESTED_FINGERPRINT_MODE"] = "9"
    os.environ["SORT4_NESTED_FINGERPRINT_EVIDENCE_DIR"] = str(case.resolve())
    os.environ["SORT4_NESTED_FINGERPRINT_SOURCE_SHA256"] = \
        source["verified_sha256"]
    try:
        stage = LINK.stage(case, "nine-body-fingerprint-refusal", [
            str(args.tool_home / "bin/verifast"), "-rustc_args",
            "--edition 2021", "-verbose", "1", "verified/lib.rs"],
            args, gates=False, pointer_drop=False, cap_seconds=100)
    finally:
        clear_semantic_opt_ins()
    log_path = case / "nine-body-fingerprint-refusal.log"
    log = log_path.read_text(errors="replace") if log_path.is_file() else ""
    snapshots = {}
    for label in ("unit", *(f"body-{index}" for index in range(9))):
        path = case / f"actual-nested-9-{label}.marshal"
        data = path.read_bytes() if path.is_file() else None
        snapshots[label] = {
            "file": path.name,
            "bytes": len(data) if data is not None else None,
            "sha256": sha(data) if data is not None else None,
        }
    intended = (stage.get("exit") == 2 and
                stage.get("source_unchanged") is True and
                DIAGNOSTIC_TEXT in log and
                not LINK.LINK.ERR.findall(log) and
                all(item["bytes"] is not None and item["bytes"] > 0
                    for item in snapshots.values()))
    return {
        "classification": "INTENDED_DIAGNOSTIC_REFUSAL_NO_PROOF_RULE"
            if intended else "INCONCLUSIVE_FINGERPRINT",
        "stage": stage,
        "expected_refusal_seen": DIAGNOSTIC_TEXT in log,
        "all_ten_snapshots": all(item["bytes"] is not None and
                                 item["bytes"] > 0
                                 for item in snapshots.values()),
        "snapshots": snapshots,
        "body_proof_run": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool-home", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--compiler-sysroot", required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--deadline-epoch", type=int, required=True)
    parser.add_argument("--fingerprint", action="store_true",
                        help="diagnostic refusal dump only, after paired MIR/refinement")
    source_modes = parser.add_mutually_exclusive_group()
    source_modes.add_argument("--wrapper-rebase", action="store_true",
                              help="separate source-only wrapper-owner ghost candidate")
    source_modes.add_argument("--wrapper-input-relation", action="store_true",
                              help="separate source-only selected-input equality diagnostic")
    source_modes.add_argument("--wrapper-input-relation-shadow", action="store_true",
                              help="blocked source-only shadow-binding revision diagnostic")
    args = parser.parse_args()
    PREP.require((os.environ.get("GITHUB_ACTIONS"),
                  os.environ.get("RUNNER_ENVIRONMENT"),
                  os.environ.get("RUNNER_OS")) ==
                 ("true", "github-hosted", "Linux"),
                 "nine-body capture requires GitHub-hosted Linux")
    evidence = args.evidence.resolve()
    clear_semantic_opt_ins()
    if args.wrapper_input_relation_shadow:
        for key in ("SORT4_WRAPPER_REBASE_REPO_ROOT", "SORT4_WRAPPER_REBASE_ADMISSION",
                    "SORT4_WRAPPER_INPUT_RELATION_REPO_ROOT",
                    "SORT4_WRAPPER_INPUT_RELATION_ADMISSION"):
            os.environ.pop(key, None)
        preparer = load(HERE / "prepare-wrapper-input-relation-shadow.py",
                        "nine_body_wrapper_input_relation_shadow_source")
    elif args.wrapper_input_relation:
        preparer = load(HERE / "prepare-wrapper-input-relation.py",
                        "nine_body_wrapper_input_relation_source")
    elif args.wrapper_rebase:
        preparer = load(HERE / "prepare-wrapper-rebase.py",
                        "nine_body_wrapper_rebase_source")
    else:
        preparer = PREP
    source = preparer.write_case(REPO, evidence)
    case = evidence / preparer.CASE_NAME
    args.first_barrier = False
    args.fingerprint_probe = False
    guard = GUARD.capture_case(case, source, args)
    stages = guard["stages"]
    full = full_body_capture(case, source, stages)
    complete = (guard["frontend_refinement"] is True and
                all(row.get("exact_body_count_and_order") is True
                    for row in full.values()) and
                source["ghost_strip_identity"] is True and
                sha((case / "original/lib.rs").read_bytes()) ==
                    source["original_sha256"] and
                sha((case / "verified/lib.rs").read_bytes()) ==
                    source["verified_sha256"])
    fingerprint = None
    if args.fingerprint and complete:
        fingerprint = refusal_fingerprint(case, source, args)
    record = {
        "classification": "NINE_BODY_SOURCE_MIR_CALIBRATION_ONLY" if complete
            else "INCONCLUSIVE_NINE_BODY_CAPTURE",
        "source": source,
        "frontend_refinement_and_full_body_capture": complete,
        "full_body_capture": full,
        "guard_capture": guard,
        "fingerprint": fingerprint,
        "actual_helper_proved": False,
        "actual_safe_forget_linked": False,
        "a1_nine_body_admission": False,
        "semantic_rule_enabled": False,
    }
    if args.wrapper_rebase:
        record["source_mode"] = "wrapper-rebase-source-only"
    elif args.wrapper_input_relation:
        record["source_mode"] = "wrapper-input-relation-source-only"
    elif args.wrapper_input_relation_shadow:
        record["source_mode"] = "wrapper-input-relation-shadow-source-only"
    (evidence / "summary.json").write_text(json.dumps(
        record, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"classification": record["classification"],
                      "source_sha256": source["verified_sha256"],
                      "frontend_refinement_and_full_body_capture": complete,
                      "fingerprint": fingerprint["classification"]
                          if fingerprint else None}), flush=True)


if __name__ == "__main__":
    main()
