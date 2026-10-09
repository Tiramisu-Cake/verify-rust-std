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


SIX_COMPARISON_PROFILE = "experimental-merge-six-same-source-comparison-v1-unaccepted"


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
    parser.add_argument("--six-home", type=Path, required=True)
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
                       safe_digest(build_dir / "full-seven-applied-profile.patch") ==
                       pin.get("expected_seven_full_diff_sha256") and
                   safe_digest(args.six_home / "bin/verifast") ==
                       pin.get("baseline_console_sha256") ==
                       build.get("base_six_console_sha256") and
                   safe_digest(args.six_home / "bin/vf-rust-mir-exporter") ==
                       safe_digest(args.tool_home / "bin/vf-rust-mir-exporter") ==
                       pin.get("release_exporter_sha256") and
                   safe_digest(args.six_home / "bin/refinement-checker") ==
                       safe_digest(args.tool_home / "bin/refinement-checker") ==
                       pin.get("release_refiner_sha256") and
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
    driver = read_json(args.evidence / "admission-controls/control-driver.json")
    driver_status = group_status(args.evidence, "admission-controls")
    driver_observed = (manifest_ok and driver_status == "0" and
                       isinstance(driver, dict) and driver.get("accepted") is False and
                       driver.get("proof_accepted") is False and
                       driver.get("tool_homes_unchanged") is True and
                       driver.get("full_shape_matrix_complete") is True and
                       isinstance(driver.get("modes"), dict) and
                       len(driver["modes"]) == 17 and
                       isinstance(driver.get("source_hash_gate"), dict) and
                       driver["source_hash_gate"].get("classification") ==
                           "EXPECTED_SOURCE_HASH_REFUSAL" and
                       driver["source_hash_gate"].get("stage") ==
                           "SOURCE_ADMISSION_BEFORE_EXPORT" and
                       driver["source_hash_gate"].get("exit_code") == 2 and
                       driver.get("classification") == "ADMISSION_CONTROLS_OBSERVED_UNACCEPTED")
    six = case_inventory(args.evidence / "six-comparison", "bidirectional_merge_len23",
                         SIX_COMPARISON_PROFILE)
    six_row = six["row"] if isinstance(six["row"], dict) else {}
    six_case = six["case_dir"]
    six_results = read_json(args.evidence / "six-comparison/results.json")
    six_fixture = read_json(args.evidence / "six-comparison/fixture-manifest.json")
    six_source_admission = args.evidence / "six-comparison/full-small-sort-source-admission.json"
    seven_source_admission = args.evidence / "actual/full-small-sort-source-admission.json"
    six_support = read_json(six_case / "stack-proof-ast-status.json")
    six_panic = read_json(six_case / "panic-macro-origin.json")
    six_provenance = read_json(six_case / "normal-exporter-provenance.json")
    seven_provenance = read_json(case / "normal-exporter-provenance.json")
    six_source_same = (
        six["complete"] and source_same and
        safe_digest(six_case / "verified/lib.rs") == safe_digest(verified) ==
            pin.get("admitted_source_sha256") and
        safe_digest(six_case / "original/lib.rs") == safe_digest(case / "original/lib.rs") and
        isinstance(six_results, dict) and
        six_results.get("source_admission_sha256") ==
            safe_digest(six_source_admission) == safe_digest(seven_source_admission) and
        isinstance(six_fixture, dict) and
        six_fixture.get("fixture_sha256") == pin.get("admitted_fixture_sha256") and
        six_fixture.get("case_order") == ["bidirectional_merge_len23"])
    normal_same = (
        six_source_same and
        file_exists(six_case / "normal-exporter.out") and
        file_exists(six_case / "normal-decode.out") and
        safe_digest(six_case / "normal-exporter.out") ==
            safe_digest(case / "normal-exporter.out") and
        safe_digest(six_case / "normal-decode.out") ==
            safe_digest(case / "normal-decode.out") and
        isinstance(six_provenance, dict) and isinstance(seven_provenance, dict) and
        isinstance(six_provenance.get("command"), list) and
        isinstance(seven_provenance.get("command"), list) and
        len(six_provenance["command"]) == 5 and
        len(seven_provenance["command"]) == 5 and
        six_provenance["command"][0] ==
            str(args.six_home / "bin/vf-rust-mir-exporter") and
        seven_provenance["command"][0] ==
            str(args.tool_home / "bin/vf-rust-mir-exporter") and
        six_provenance["command"][1:] == seven_provenance["command"][1:] and
        six_provenance["command"][1] == "verified/lib.rs" and
        isinstance(six_provenance["command"][2], str) and
        six_provenance["command"][2].startswith("--sysroot=/workspace/") and
        six_provenance["command"][3:] == ["--edition", "2021"] and
        all(p.get("normal_preprocess") is True and
            p.get("source_unchanged") is True and
            p.get("source_sha256") == pin.get("admitted_source_sha256") and
            p.get("mir_sha256") == safe_digest(six_case / "normal-exporter.out") and
            p.get("decoded_sha256") == safe_digest(six_case / "normal-decode.out")
            for p in (six_provenance, seven_provenance)))
    expected_bodies = row.get("expected_bodies")
    full_six_body_coverage = (
        isinstance(expected_bodies, list) and len(expected_bodies) == 11 and
        len(set(expected_bodies)) == 11 and
        six_row.get("expected_bodies") == expected_bodies and
        isinstance(six_row.get("visited_bodies"), list) and
        sorted(six_row["visited_bodies"]) == sorted(expected_bodies) and
        isinstance(six_row.get("body_execution_records"), dict) and
        all(type(six_row["body_execution_records"].get(name)) is int and
            six_row["body_execution_records"][name] > 0 for name in expected_bodies) and
        isinstance(six_row.get("per_body_records"), dict) and
        six_row["per_body_records"] == row.get("per_body_records") and
        all(type(six_row["per_body_records"][name].get(k)) is int and
            six_row["per_body_records"][name][k] > 0
            for name in expected_bodies for k in ("return", "leak")) and
        six_row.get("return_records") == row.get("return_records") ==
            sum(six_row["per_body_records"][name]["return"] for name in expected_bodies) and
        six_row.get("leak_check_records") == row.get("leak_check_records") ==
            sum(six_row["per_body_records"][name]["leak"] for name in expected_bodies))
    guard = pin.get("admitted_guard_line")
    exact_dead = (f"verified/lib.rs({guard},51-{guard + 2},10): dead code"
                  if type(guard) is int and guard > 0 else None)
    six_log_path = six_case / "verifast.log"
    six_log = six_log_path.read_text(errors="replace") if six_log_path.is_file() else ""
    dead_lines = [line for line in six_log.splitlines()
                  if re.search(r": dead code(?:[ \t].*)?$", line, re.IGNORECASE)]
    sole_synthetic_dead = (
        exact_dead is not None and dead_lines == [exact_dead] and
        six_row.get("dead_code_records") == [exact_dead] and
        six_row.get("error_lines") == [] and
        re.search(r"(?m)^.*?: error: .*$", six_log) is None)
    six_comparison_complete = (
        manifest_ok and positive_full and six_source_same and normal_same and
        exit_zero(args.evidence / "six-comparison-exit-code.txt") and
        six_row.get("classification") == "INCONCLUSIVE" and
        six_row.get("full_positive_gate") is False and
        six_row.get("expected_dead_code") is None and
        six_row.get("expected_rejection") is None and
        six_row.get("stages") == {"exporter": 0, "decode": 0,
                                  "verifast": 1, "refinement": 0} and
        full_six_body_coverage and sole_synthetic_dead and
        isinstance(six_row.get("stack_address_admission"), dict) and
        six_row["stack_address_admission"].get("complete") is True and
        isinstance(six_support, dict) and six_support.get("status") == "AST_LINKED" and
        six_support.get("exit_code") == 0 and
        isinstance(six_panic, dict) and
        six_panic.get("status") == "PANIC_MACRO_BODY_ORIGIN_LINKED" and
        isinstance(six_row.get("panic_macro_origin"), dict) and
        six_row["panic_macro_origin"].get("accepted") is True)
    six_status = group_status(args.evidence, "six-comparison")
    six_comparison = {
        "classification": ("SAME_SOURCE_COVERAGE_DIFFERENCE_UNACCEPTED"
                           if six_comparison_complete else
                           "NOT_RUN" if six_status == "NOT_RUN" else "INCONCLUSIVE"),
        "accepted": False, "proof_negative": False,
        "group_status": six_status,
        "raw_classification": six["raw_classification"],
        "stages": six_row.get("stages"),
        "source_identical": bool(six_source_same),
        "normal_mir_identical": bool(normal_same),
        "all_eleven_bodies_and_return_leak_records": bool(full_six_body_coverage),
        "exact_sole_synthetic_dead_record": bool(sole_synthetic_dead),
        "expected_dead_record": exact_dead,
        "observed_dead_lines": dead_lines,
        "complete": bool(six_comparison_complete),
    }
    diagnostic_complete = bool(manifest_ok and positive["complete"] and
                               positive_full and calibrated["complete"] and
                               calibrated_dead and
                               calibration_complete and driver_observed and
                               six_comparison_complete)
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
                          "actual-bounded", "admission-controls", "six-comparison")},
        "invalid_shape_admission_controls": {
            "classification": ("OBSERVED_UNACCEPTED" if driver_observed else
                               "NOT_RUN" if driver_status == "NOT_RUN" else "INCONCLUSIVE"),
            "group_status": driver_status,
            "report_sha256": safe_digest(args.evidence / "admission-controls/control-driver.json"),
            "raw_report": driver,
            "accepted": False,
            "full_shape_matrix_complete": bool(driver_observed),
        },
        "same_source_six_component_comparison": six_comparison,
        "live_panic_body_coverage": bool(positive_full),
        "notes": ["Positive/negative classifications are conditional diagnostics only.",
                  "New controls lack preregistered proof-negative oracles.",
                  "No kernel, source safety, or general profile acceptance follows."],
    }
    (args.evidence / "seven-audit.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
