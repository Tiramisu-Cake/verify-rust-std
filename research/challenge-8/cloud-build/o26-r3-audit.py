#!/usr/bin/env python3
"""Fail-closed Cloud audit for bounded R3 admission and changed-component controls."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re


CASE = "nine-body-wrapper-input-relation"
SOURCE = "a95aff14592b167c62c53c7ed726128ee86c7c19768cfe613504cdec841f8463"
ORIGINAL = "466882d74de217766ed8d5c583596c173df47f0e6bd40da7cb1a4c931d7265a5"
PREFIX = (
    "sort4_certified_maybeuninit::sort4_checked_maybeuninit_new",
    "sort4_checked_as_mut_ptr", "sort4_checked_pointer_drop",
    "sort4_checked_generic_drop", "checked_transmute_neo_pointer",
    "checked_assume_init_pointer", "checked_forget_owned",
)
OWNER_KEYS = ("source_owner", "source_outcome", "forget_move_to_copy",
              "forget_cleanup_to_wrong_block")
FIRST_ERROR = re.compile(r"(?m)^.*: error: .*|^Fatal error:.*$|^Error:.*$")
OPEN_GATES = (
    "nested Drop same-version proof before outer not observed under lexical R3 order",
    "R3 recertified one-item AST scheduling TEST and its mutation controls",
    "independent body-7 and ghost-CFG target-obligation negatives",
    "full target normal/unwind/leak/dead/validity proof review",
    "generic ownership and actual sort4 remain open",
)


def need(ok: bool, why: str) -> None:
    if not ok:
        raise RuntimeError(why)


def read(path: Path) -> dict:
    need(path.is_file(), f"missing R3 evidence: {path}")
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    need(path.is_file() and path.stat().st_size > 0,
         f"empty or missing R3 artifact: {path}")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifacts(root: Path, paths: list[Path]) -> dict:
    result = {}
    for path in paths:
        need(path.is_relative_to(root), f"R3 artifact outside evidence: {path}")
        result[str(path.relative_to(root))] = {
            "sha256": sha(path), "bytes": path.stat().st_size}
    need(len(result) == len(paths), "duplicate R3 artifact path")
    return result


def audit(a) -> dict:
    e = a.evidence
    manifest = read(e / "profile-manifest.json")
    capture = read(e / "capture-check.json")
    proof = read(e / "proof-summary.json")
    positive = read(e / "r3-positive-stage.json")
    off = read(e / "r2-old-certificate-stage.json")
    controls = read(e / "controls-summary.json")
    identity = read(e / "tool-identity.json")
    identity_after = read(e / "tool-identity-after.json")
    r2_before = read(e / "r2-tool-before.json")
    case = e / "capture" / CASE
    need(a.runner_exit == 0 and
         manifest.get("classification") ==
         "EXPERIMENTAL_O26_WRAPPER_INPUT_RELATION_COMPONENT24_NOT_ACCEPTED" and
         manifest.get("verification_accepted") is False and
         manifest.get("kernel_modified") is False and
         manifest.get("source", {}).get("verified_sha256") == SOURCE and
         manifest.get("source", {}).get("original_sha256") == ORIGINAL and
         capture.get("classification") ==
         "R3_SOURCE_MIR_GRAPH_PINNED_DIAGNOSTIC" and
         capture.get("normal_readonly_refinement_complete") is True and
         capture.get("all_nine_body_records_and_ten_marshal_files_hashed") is True and
         capture.get("typed_outer_mir_exact") is True and
         capture.get("accepted") is False and
         identity == identity_after and
         identity.get("r2") == r2_before and
         identity.get("only_translator_and_console_changed") is True and
         identity.get("kernel_parser_schema_specs_exporter_refiner_unchanged") is True,
         "R3 source/capture/tool identity incomplete")
    need(sha(case / "verified/lib.rs") == SOURCE and
         sha(case / "original/lib.rs") == ORIGINAL,
         "R3 current full source pair changed")
    for mode, expected in (
        ("normal", "5b241f4f51d9ba7e72dd4d24cf295a95a8f64d7750867821dc70dac982609509"),
        ("readonly", "c5fe3880640143c2805697f8fb4c46f380fc62eb01f3344ee1ec606e7aadf121"),
    ):
        need(sha(case / f"{mode}-mir.txt") == expected and
             sha(case / f"{mode}-mir.bin"),
             f"R3 {mode} full MIR changed")
    log_path = case / "r3-positive.log"
    text = log_path.read_text(errors="replace")
    positions = [text.find("Verifying function '" + name + "'")
                 for name in PREFIX]
    outer = text.find("Verifying function 'select_unpredictable'")
    errors_before_outer = (outer < 0 or FIRST_ERROR.search(text[:outer]) is not None)
    all_errors = FIRST_ERROR.findall(text)
    need(positive.get("status") == "RAN" and
         positive.get("exit") in (0, 1, 2) and
         positive.get("source_unchanged") is True and
         positive.get("source_before") == positive.get("source_after") and
         positive.get("source_before", {}).get("verified/lib.rs") == SOURCE and
         positive.get("source_before", {}).get("original/lib.rs") == ORIGINAL and
         positive.get("intrinsic_gate_active") is True and
         positive.get("pointer_drop_gate_active") is True and
         all(p >= 0 for p in positions) and positions == sorted(positions) and
         outer > positions[-1] and not errors_before_outer and
         (not all_errors if positive.get("exit") == 0 else
          len(all_errors) == 1 and ": error:" in all_errors[0]) and
         proof.get("stage") == positive and
         proof.get("seven_prefix_headers_in_order") is True and
         proof.get("outer_header_after_prefix") is True and
         proof.get("full_proof_exit") == positive.get("exit") and
         proof.get("actual_nested_drop_verified_before_outer") is False and
         proof.get("accepted") is False,
         "R3 positive did not reach first outer proof boundary cleanly")
    off_log = (case / "r2-old-certificate-refusal.log").read_text(errors="replace")
    expected_off = ('Fatal error: exception Failure("SORT4-SELECT-INTRINSIC: '
                    'certificate mismatch: owner exact verified source SHA256")')
    need(off.get("status") == "RAN" and off.get("exit") == 2 and
         off.get("source_unchanged") is True and
         off.get("source_before") == off.get("source_after") and
         off.get("source_before", {}).get("verified/lib.rs") == SOURCE and
         [line for line in off_log.splitlines()
          if line.startswith("Fatal error:")] == [expected_off] and
         "Verifying function '" not in off_log,
         "R2 old certificate did not refuse R3 source at exact pin")
    owner = controls.get("owner17", [])
    need(controls.get("classification") ==
         "R3_CHANGED_COMPONENT_NEGATIVES_COMPLETE" and
         controls.get("production_tool_unchanged") is True and
         controls.get("accepted") is False and len(owner) == 4 and
         [row.get("variant") for row in owner] == list(OWNER_KEYS) and
         all(row.get("intended_component17_refusal") is True and
             row.get("accepted") is False for row in owner) and
         controls.get("a1", {}).get("classification") ==
         "R3_A1_MOVE_COPY_NEGATIVE" and
         controls["a1"].get("intended_refusal") is True and
         controls.get("safe_forget", {}).get("classification") ==
         "R3_SAFE_FORGET_MOVE_COPY_NEGATIVE" and
         controls["safe_forget"].get("intended_refusal") is True,
         "R3 independent component17/A1/SAFE-forget controls incomplete")
    for row in owner:
        control_case = (e / "controls" /
                        ("owner17-" + row["variant"]) / "source" / CASE)
        need(read(control_case / "control-result.json") == row,
             f"R3 {row['variant']} control summary differs from case")
    for key, label in (("outer_assume_init_move_to_copy", "a1"),
                       ("forget_move_to_copy", "safe_forget")):
        control_root = e / "controls" / key
        result = read(control_root / "test-result.json")
        need(result == controls[label] and
             result.get("test_tool_identity") ==
             read(control_root / "test-tool-identity.json") and
             result.get("mutation") == key and
             result.get("accepted") is False and
             result.get("verification_accepted") is False,
             f"R3 {key} TEST result/identity differs from summary")
    paths = [e / name for name in (
        "profile-manifest.json", "capture-check.json", "proof-summary.json",
        "r3-positive-stage.json", "r2-old-certificate-stage.json",
        "controls-summary.json", "tool-identity.json",
        "tool-identity-after.json", "r2-tool-before.json",
        "capture/summary.json")]
    paths += [case / rel for rel in (
        "verified/lib.rs", "original/lib.rs", "normal-mir.bin",
        "normal-mir.txt", "readonly-mir.bin", "readonly-mir.txt",
        "capture-summary.json", "r3-positive.log",
        "r2-old-certificate-refusal.log")]
    paths += [case / f"{mode}-body-{i}-full-mir.txt"
              for mode in ("normal", "readonly") for i in range(9)]
    paths += [case / f"actual-nested-9-{label}.marshal"
              for label in ("unit", *(f"body-{i}" for i in range(9)))]
    for key in OWNER_KEYS:
        root = e / "controls" / ("owner17-" + key) / "source" / CASE
        paths += [root / rel for rel in
                  ("verified/lib.rs", "original/lib.rs", "normal-mir.bin",
                   "normal-mir.txt", "readonly-mir.bin", "readonly-mir.txt",
                   "capture-summary.json",
                   "proof-stage.json", "control-result.json",
                   "r3-owner-" + key + ".log")]
        if key not in ("source_owner", "source_outcome"):
            paths += [root / rel for rel in
                      ("mutation-record.json", "mutation-profile.json",
                       "canonical-mir.bin", "mutated-mir.bin",
                       "canonical-mir.txt", "mutated-mir.txt",
                       "mir-exporter-wrapper.py")]
    for key in ("outer_assume_init_move_to_copy", "forget_move_to_copy"):
        root = e / "controls" / key
        paths += [root / name for name in
                  ("test-result.json", "test-tool-identity.json",
                   "test-owner-hash-delta.patch", "test-console-build.log")]
        for branch in ("source", "test-case"):
            sub = root / branch / CASE if branch == "source" else root / branch
            paths += [sub / rel for rel in
                      ("verified/lib.rs", "original/lib.rs", "mutation-record.json",
                       "mutation-profile.json", "canonical-mir.bin",
                       "mutated-mir.bin", "canonical-mir.txt",
                       "mutated-mir.txt", "mir-exporter-wrapper.py")]
            if branch == "source":
                paths.append(sub / "capture-summary.json")
        source_case = root / "source" / CASE
        paths += [source_case / f"actual-nested-9-{label}.marshal"
                  for label in ("unit", *(f"body-{i}" for i in range(9)))]
        paths += [source_case / ("r3-" + key + "-owner-refusal.log")]
        paths += [root / "test-case" / ("r3-" + key + "-target-refusal.log")]
    return {"classification": "WRAPPER_R3_PROFILE_DIAGNOSTIC_COMPLETE",
            "diagnostic_complete": True, "verification_accepted": False,
            "accepted": False, "actual_helper_proved": False,
            "actual_nested_drop_verified_before_outer": False,
            "source_mir_refinement_complete": True,
            "r3_source_and_graph_pinned": True,
            "old_r2_certificate_refusal": True,
            "seven_same_version_callees_before_outer": True,
            "first_source_error_after_outer_header": all_errors[0]
            if all_errors else None,
            "full_positive_exit": positive["exit"],
            "component17_source_unit_controls_complete": True,
            "a1_move_copy_negative_complete": True,
            "safe_forget_move_copy_negative_complete": True,
            "artifacts": artifacts(e, paths), "open_gates": OPEN_GATES}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--evidence", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--runner-exit", type=int, required=True)
    p.add_argument("--failed-stage", required=True)
    a = p.parse_args()
    try:
        result = audit(a)
    except Exception as exc:
        result = {"classification": "INCONCLUSIVE", "diagnostic_complete": False,
                  "verification_accepted": False, "accepted": False,
                  "actual_helper_proved": False,
                  "actual_nested_drop_verified_before_outer": False,
                  "reason": str(exc), "runner_exit": a.runner_exit,
                  "failed_stage": a.failed_stage, "open_gates": OPEN_GATES}
    a.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if result["classification"] == "INCONCLUSIVE":
        raise SystemExit("R3 profile diagnostic inconclusive: " + result["reason"])


if __name__ == "__main__":
    main()
