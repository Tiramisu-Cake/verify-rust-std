#!/usr/bin/env python3
"""Conservative evidence inventory for the unaccepted seventh component.

This records completed diagnostic gates. It never grants theorem or profile
acceptance and never promotes an uncalibrated control to a proof negative.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe_digest(path: Path):
    try:
        return digest(path)
    except OSError:
        return None


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError):
        return None


def exit_zero(path: Path) -> bool:
    try:
        return path.read_text(encoding="ascii").strip() == "0"
    except OSError:
        return False


def exit_value(path: Path):
    try:
        value = path.read_text(encoding="ascii").strip()
        return int(value) if re.fullmatch(r"[0-9]+", value) else None
    except OSError:
        return None


def file_exists(path: Path) -> bool:
    return path.is_file() and path.stat().st_size > 0


def group_status(evidence: Path, name: str) -> str:
    try:
        return (evidence / f"{name}-exit-code.txt").read_text(
            encoding="ascii").strip()
    except OSError:
        return "NOT_RUN"


def case_inventory(root: Path, name: str, expected_profile: str):
    aggregate = read_json(root / "aggregate.json")
    result = read_json(root / "results.json")
    cases = result.get("cases") if isinstance(result, dict) else None
    row = cases.get(name) if isinstance(cases, dict) else None
    case = root / "cases" / name
    profile_ok = (isinstance(result, dict) and isinstance(result.get("profile"), str)
                  and result["profile"].startswith(expected_profile + ";"))
    common = (isinstance(aggregate, dict) and
              aggregate.get("evidence_collection_completed") is True and
              aggregate.get("classifier_controls_passed") is True and
              isinstance(row, dict) and profile_ok and
              row.get("source_unchanged_at_every_stage") is True and
              row.get("source_before") == row.get("source_after") and
              isinstance(row.get("source_after"), dict) and
              isinstance(row.get("stages"), dict) and
              row.get("case") == name and
              file_exists(case / "verified/lib.rs") and
              file_exists(case / "original/lib.rs") and
              file_exists(case / "verifast.log") and
              all(exit_value(case / f"{stage}-exit-code.txt") is not None and
                  exit_value(case / f"{stage}-exit-code.txt") ==
                  row["stages"].get(stage)
                  for stage in ("exporter", "decode", "verifast", "refinement")) and
              isinstance(row.get("classifier_fail_closed_mutations"), dict) and
              bool(row["classifier_fail_closed_mutations"]) and
              all(row["classifier_fail_closed_mutations"].values()))
    if common:
        common = (row["source_after"].get("verified/lib.rs") ==
                  safe_digest(case / "verified/lib.rs") and
                  row["source_after"].get("original/lib.rs") ==
                  safe_digest(case / "original/lib.rs"))
    return {"case": name, "complete": bool(common),
            "raw_classification": row.get("classification") if isinstance(row, dict) else None,
            "row": row, "case_dir": case, "profile_match": bool(profile_ok)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--tool-home", type=Path, required=True)
    args = parser.parse_args()
    pin = read_json(args.manifest)
    if not isinstance(pin, dict):
        pin = {}
    build = read_json(args.evidence / "build/seven-profile-manifest.json")
    preflight = read_json(args.evidence / "preflight/or-join-preflight.json")
    translator = Path("src/rust_frontend/vf_mir_translator/vf_mir_translator.ml")
    build_dir = args.evidence / "build"
    manifest_ok = (pin.get("component") == "MIR-OR-JOIN-LIVENESS" and
                   pin.get("admission_state") == "EXPERIMENTAL_CLOUD_TRIAL" and
                   isinstance(build, dict) and build.get("accepted") is False and
                   exit_zero(args.evidence / "build-wrapper-exit-code.txt") and
                   build.get("component_manifest_sha256") == safe_digest(args.manifest) and
                   build.get("component_patch_sha256") == pin.get("component_patch_sha256") and
                   safe_digest(args.manifest.parent / "or-join-liveness.patch") ==
                       pin.get("component_patch_sha256") and
                   build.get("baseline_translator_sha256") == pin.get("baseline_translator_sha256") and
                   safe_digest(build_dir / "translator.six.ml") ==
                       pin.get("baseline_translator_sha256") and
                   build.get("component_translator_sha256") == pin.get("component_translator_sha256") and
                   safe_digest(build_dir / "translator.seven.ml") ==
                       pin.get("component_translator_sha256") and
                   safe_digest(args.tool_home / translator) ==
                       pin.get("component_translator_sha256") and
                   build.get("base_six_console_sha256") ==
                       pin.get("baseline_console_sha256") and
                   build.get("base_six_full_diff_sha256") ==
                       pin.get("baseline_applied_profile_sha256") and
                   safe_digest(build_dir / "base-six-applied-profile.patch") ==
                       pin.get("baseline_applied_profile_sha256") and
                   isinstance(build.get("seven_full_diff_sha256"), str) and
                   build.get("seven_full_diff_sha256") ==
                       safe_digest(build_dir / "full-seven-applied-profile.patch") and
                   build.get("kernel_unchanged") is True and
                   build.get("parser_unchanged") is True and
                   build.get("prelude_unchanged") is True and
                   build.get("stdlib_unchanged") is True and
                   build.get("exporter_unchanged") is True and
                   build.get("refiner_unchanged") is True and
                   exit_zero(args.evidence / "build/seven-build-exit-code.txt") and
                   exit_zero(args.evidence / "preflight-exit-code.txt") and
                   exit_zero(args.evidence / "source-admission-exit-code.txt") and
                   isinstance(preflight, dict) and preflight.get("accepted") is False and
                   preflight.get("fixture_sha256") == pin.get("admitted_fixture_sha256") and
                   preflight.get("verified_sha256") == pin.get("admitted_source_sha256") and
                   preflight.get("retained_pointer_prove_sha256") ==
                       pin.get("retained_pointer_prove_sha256") and
                       safe_digest(args.manifest.parent.parent / "pointer-prove.py") ==
                       pin.get("retained_pointer_prove_sha256") and
                   safe_digest(args.fixture) == pin.get("admitted_fixture_sha256") and
                   isinstance(build.get("seven_console_sha256"), str) and
                   safe_digest(args.tool_home / "bin/verifast") ==
                       build.get("seven_console_sha256"))
    positive = case_inventory(args.evidence / "actual", "bidirectional_merge_len23", args.profile)
    row = positive["row"] if isinstance(positive["row"], dict) else {}
    case = positive["case_dir"]
    support = read_json(case / "stack-proof-ast-status.json")
    panic = read_json(case / "panic-macro-origin.json")
    verified = case / "verified/lib.rs"
    source_same = (positive["complete"] and isinstance(preflight, dict) and
                   safe_digest(verified) == preflight.get("verified_sha256") and
                   safe_digest(verified) == pin.get("admitted_source_sha256") and
                   safe_digest(case / "original/lib.rs") ==
                       preflight.get("original_sha256"))
    positive_full = (manifest_ok and source_same and
                     exit_zero(args.evidence / "actual-bounded-exit-code.txt") and
                     row.get("classification") == "PASS" and
                     row.get("full_positive_gate") is True and
                     row.get("dead_code_records") == [] and
                     row.get("error_lines") == [] and
                     isinstance(row.get("stages"), dict) and
                     all(row["stages"].get(s) == 0 for s in
                         ("exporter", "decode", "verifast", "refinement")) and
                     isinstance(support, dict) and support.get("status") == "AST_LINKED" and
                     support.get("exit_code") == 0 and
                     isinstance(panic, dict) and
                     isinstance(row.get("panic_macro_origin"), dict) and
                     row["panic_macro_origin"].get("accepted") is True and
                     file_exists(case / "normal-decode.out") and
                     file_exists(case / "normal-exporter.out") and
                     file_exists(case / "proof-ast.ml") and
                     file_exists(case / "stack-roles.json") and
                     file_exists(case / "verifast.log"))
    guard = pin.get("admitted_guard_line")
    if positive_full:
        log = (case / "verifast.log").read_text(errors="replace")
        panic_line = guard + 1 if type(guard) is int else None
        positive_full = (panic_line is not None and
                         re.search(r"(?m)^.*verified/lib\.rs\(" + str(panic_line) +
                                   r",\d+(?:-\d+)?\): (?:note: )?Executing statement", log)
                         is not None and
                         "MIR-OR-JOIN-LIVENESS: exact source/MIR/AST join admission failed"
                         not in log)
    calibrated = case_inventory(args.evidence / "calibrated-real-dead",
                                "unreachable_body_after_panic", args.profile)
    dead_row = calibrated["row"] if isinstance(calibrated["row"], dict) else {}
    calibrated_dead = (manifest_ok and calibrated["complete"] and
                       exit_zero(args.evidence / "calibrated-real-dead-exit-code.txt") and
                       dead_row.get("classification") == "EXPECTED_DEAD_CODE" and
                       dead_row.get("expected_dead_code_gate") is True and
                       dead_row.get("stages") == {"exporter": 0, "decode": 0,
                                                  "verifast": 1, "refinement": 0})
    control_names = ("dead_real_return", "dead_panic_body",
                     "dead_source_break", "dead_source_continue")
    control_result = read_json(args.evidence / "uncalibrated-liveness-controls/results.json")
    controls = {}
    for name in control_names:
        item = case_inventory(args.evidence / "uncalibrated-liveness-controls",
                              name, args.profile)
        controls[name] = {
            "classification": "CALIBRATION_ONLY" if item["complete"] else "INCONCLUSIVE",
            "raw_classification": item["raw_classification"],
            "complete": item["complete"],
        }
    control_cases = control_result.get("cases") if isinstance(control_result, dict) else None
    calibration_complete = (exit_zero(args.evidence / "uncalibrated-liveness-controls-exit-code.txt") and
                            isinstance(control_cases, dict) and
                            set(control_cases) == set(control_names) and
                            all(c["complete"] for c in controls.values()))
    diagnostic_complete = bool(manifest_ok and positive["complete"] and
                               calibrated["complete"] and calibration_complete)
    report = {
        "component": "MIR-OR-JOIN-LIVENESS",
        "profile": args.profile,
        "classification": "DIAGNOSTIC_COMPLETE_UNACCEPTED" if diagnostic_complete else "INCONCLUSIVE",
        "accepted": False,
        "component_gates_complete": False,
        "diagnostic_complete": diagnostic_complete,
        "base_six_profile_accepted": False,
        "tool_source_admission_complete": bool(manifest_ok),
        "actual_bounded_full_positive": bool(positive_full),
        "actual_bounded_raw_classification": positive["raw_classification"],
        "calibrated_real_dead_proof_negative": bool(calibrated_dead),
        "calibrated_real_dead_raw_classification": calibrated["raw_classification"],
        "new_liveness_controls": controls,
        "new_liveness_controls_calibration_complete": bool(calibration_complete),
        "group_status": {name: group_status(args.evidence, name) for name in
                         ("calibrated-real-dead", "uncalibrated-liveness-controls",
                          "actual-bounded")},
        "invalid_shape_admission_controls": "NOT_RUN",
        "same_source_six_component_comparison": "NOT_RUN",
        "live_panic_body_coverage": bool(positive_full),
        "notes": ["Positive/negative classifications are conditional diagnostics only.",
                  "New controls lack preregistered proof-negative oracles.",
                  "No kernel, source safety, or general profile acceptance follows."],
    }
    (args.evidence / "seven-audit.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
