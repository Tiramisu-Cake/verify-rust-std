#!/usr/bin/env python3
"""Audit exact selected merge groups and their required evidence artifacts."""
from __future__ import annotations

import json
from pathlib import Path
import sys

from selection import KNOWN_GROUPS, load

# Paths are relative to allprooflogs. Pointer proof harness groups must publish
# both an aggregate and the source admission it consumed. Other groups publish
# their retained runner's exact results, admission, or preparation output.
POINTER_GROUPS = {
    "rust-profile-smoke": "checked-profile-smoke",
    "rust-unwind-baselines": "checked-baselines",
    "callback-model-diagnostics": "checked-callback-model",
    "tuple2-resource-diagnostics": "checked-m2-resources",
    "callback-borrow-diagnostic": "checked-callback-borrow",
    "prepared-hrtb-diagnostics": "checked-hrtb-prepared",
    "callback-cleanup-diagnostics": "checked-cleanup",
    "copy-model-diagnostics": "checked-copy",
    "wrapping-acceptance": "checked-wrapping",
    "pointer-bridge-diagnostic": "checked-pointer-bridge",
    "pointer-domain-bridge": "checked-pointer-domain",
    "owned-array-resource-diagnostic": "checked-owned-array",
    "scratch-option-resource-diagnostic": "checked-scratch-options",
    "concrete-zst-diagnostic": "checked-concrete-zst",
    "experimental-rust-regression": "checked-rust-regression",
    "tuple-layout-entry-diagnostics": "checked-tuple-layout",
    "trace-entry-tuple-diagnostics": "checked-trace-entry",
    "usize-primitive-diagnostics": "checked-usize-multiple",
    "stack-address-admission-diagnostics": "checked-stack-address",
    "stack-address-role-controls": "checked-stack-role-controls",
    "pointer-quartet-trace-entry-negative": "checked-z3-quartet-full-entry",
    "pointer-quartet-trace-diagnostic": "checked-pointer-trace-quartets",
    "actual-callee-applicability": "checked-actual",
    "bidirectional-option-stages": "checked-bidirectional-stages",
    "bidirectional-len23-diagnostic": "checked-bidirectional-small",
    "pointer-modular-trace-entry-negative": "checked-pointer-modular-trace-entry-negative",
    "pointer-modular-trace-diagnostic": "checked-pointer-modular-trace",
    "source-pair-turnover-resource-diagnostic": "checked-source-pair-turnover",
    "cleanup-recovery-hidden-type-diagnostic": "checked-cleanup-recovery-hidden-type",
}
OTHER_ARTIFACTS = {
    "G2-compatibility": [
        "cases/checked-g2/results.json", "cases/checked-g2/source-admission.json",
    ],
    "A-compatibility": [
        "cases/checked-a/results.json", "cases/checked-a/source-admission.json",
    ],
    "B-compatibility": [
        "cases/checked-b/results.json", "cases/checked-b/source-admission.json",
    ],
    "native-baselines": ["cases/checked-native/results.json"],
    "tuple2-shape-admission": [
        "cases/checked-m2-shape/aggregate.json",
        "cases/checked-m2-shape/m2-admission.json",
    ],
    "hrtb-admission-certificate": [
        "cases/checked-hrtb-admission/aggregate.json",
        "cases/checked-hrtb-admission/hrtb-admission-certificate.json",
    ],
    "usize-source-admission": ["usize-source-admission.json"],
    "stack-address-role-control-preparation": [
        "stack-address-role-controls/admission.json",
        "stack-address-role-controls/stack-address-control-cases.rs",
    ],
    "actual-source-preparation": [
        "actual-cases.rs", "actual-cases.admission.json",
    ],
    "bidirectional-small-source-preparation": [
        "bidirectional-small-cases.rs", "bidirectional-small-cases.admission.json",
    ],
}


def audit(root: Path, selection_path: Path, run_status: int,
          proof_sha: str, build_id: str) -> dict:
    evidence = root / "allprooflogs"
    cases = evidence / "cases"
    selection = load(selection_path)
    resolved_path = root / "selection-resolved.json"
    resolved = json.loads(resolved_path.read_text())
    selection_hash = sha256_file(selection_path)
    if (resolved.get("selection_sha256") != selection_hash or
            resolved.get("groups") != selection.get("groups") or
            resolved.get("runtime_probe") != selection.get("runtime_probe") or
            resolved.get("mode") != selection.get("mode")):
        raise SystemExit("resolved merge selection does not match committed selection")
    selected = set(selection["groups"])
    not_run = KNOWN_GROUPS - selected

    def read_names(path: Path, expected_status: bool) -> tuple[list[str], dict[str, str]]:
        rows: list[str] = []
        values: dict[str, str] = {}
        if not path.is_file():
            return rows, values
        for line in path.read_text(errors="replace").splitlines():
            parts = line.split()
            if expected_status and len(parts) == 2:
                name, code = parts
                rows.append(name)
                values[name] = code
            elif not expected_status and len(parts) == 2 and parts[1] == "NOT_RUN":
                rows.append(parts[0])
                values[parts[0]] = parts[1]
            else:
                rows.append("_MALFORMED_")
        return rows, values

    status_rows, observed = read_names(evidence / "group-status.txt", True)
    skipped_rows, skipped = read_names(evidence / "group-not-run.txt", False)
    status_unique = len(status_rows) == len(set(status_rows))
    skipped_unique = len(skipped_rows) == len(set(skipped_rows))
    skipped_have_no_exit_records = all(
        not (evidence / f"group-{group}-exit-code.txt").exists()
        for group in not_run)
    groups_exact = (status_unique and skipped_unique and
                    set(observed) == selected and set(skipped) == not_run and
                    set(observed).isdisjoint(skipped) and
                    skipped_have_no_exit_records and
                    all(value == "0" for value in observed.values()))

    mandatory: dict[str, list[str]] = {}
    for group in selected:
        if group in POINTER_GROUPS:
            name = POINTER_GROUPS[group]
            mandatory[group] = [
                f"cases/{name}/aggregate.json",
                f"cases/{name}/full-small-sort-source-admission.json",
            ]
        elif group in OTHER_ARTIFACTS:
            mandatory[group] = OTHER_ARTIFACTS[group]
        else:
            raise SystemExit("selected group has no artifact policy: " + group)
    def valid_artifact(path: str) -> bool:
        item = evidence / path
        if not item.is_file() or item.is_symlink():
            return False
        if item.suffix == ".json":
            try:
                value = json.loads(item.read_text())
            except (OSError, ValueError):
                return False
            return isinstance(value, (dict, list))
        return item.stat().st_size > 0

    artifact_status = {
        group: all(valid_artifact(path) for path in paths)
        for group, paths in mandatory.items()
    }
    for group, dirname in POINTER_GROUPS.items():
        if group not in selected or not artifact_status.get(group, False):
            continue
        try:
            case_dir = evidence / f"cases/{dirname}"
            aggregate = json.loads((case_dir / "aggregate.json").read_text())
            fixture = json.loads((case_dir / "fixture-manifest.json").read_text())
            results = json.loads((case_dir / "results.json").read_text())
            fixture_is_object = isinstance(fixture, dict)
            results_is_object = isinstance(results, dict)
            aggregate_is_object = isinstance(aggregate, dict)
            case_order = fixture.get("case_order") if fixture_is_object else None
            fixture_cases = fixture.get("cases") if fixture_is_object else None
            result_cases = results.get("cases") if results_is_object else None
            aggregate_cases = aggregate.get("cases") if aggregate_is_object else None
            case_sets_valid = (
                isinstance(case_order, list) and bool(case_order) and
                all(isinstance(name, str) for name in case_order) and
                len(case_order) == len(set(case_order)) and
                isinstance(fixture_cases, dict) and bool(fixture_cases) and
                isinstance(result_cases, dict) and bool(result_cases) and
                isinstance(aggregate_cases, dict) and bool(aggregate_cases) and
                set(case_order) == set(fixture_cases) ==
                set(result_cases) == set(aggregate_cases)
            )
            artifact_status[group] = (
                aggregate_is_object and
                aggregate.get("evidence_collection_completed") is True and
                case_sets_valid)
        except (OSError, ValueError):
            artifact_status[group] = False

    # The three stock mathematical proof components each emit a source
    # certificate and bind its exact bytes from results.json.
    stock_source_dirs = {
        "G2-compatibility": "checked-g2",
        "A-compatibility": "checked-a",
        "B-compatibility": "checked-b",
    }
    for group, dirname in stock_source_dirs.items():
        if group not in selected or not artifact_status.get(group, False):
            continue
        try:
            case_dir = evidence / "cases" / dirname
            results = json.loads((case_dir / "results.json").read_text())
            admission = case_dir / "source-admission.json"
            artifact_status[group] = (
                isinstance(results, dict) and
                results.get("source_admission_sha256") == sha256_file(admission)
            )
        except (OSError, ValueError):
            artifact_status[group] = False
    # Every selected run_one must retain its own process log and exact exit row.
    stage_status = {}
    for group in selected:
        exit_file = evidence / f"group-{group}-exit-code.txt"
        log_file = evidence / f"group-{group}.log"
        try:
            code = int(exit_file.read_text().strip())
        except (OSError, ValueError):
            code = None
        stage_status[group] = {
            "log": log_file.is_file(),
            "exit_code_file": exit_file.is_file(),
            "exit_code": code,
            "matches_status": observed.get(group) == str(code) if code is not None else False,
        }
    stages_complete = all(row["log"] and row["exit_code_file"] and row["exit_code"] == 0 and row["matches_status"]
                          for row in stage_status.values())

    def raw_cases(aggregate_rel: str, group: str) -> dict:
        if group not in selected:
            return {"classification": "NOT_RUN"}
        try:
            value = json.loads((evidence / aggregate_rel).read_text())
            return value.get("cases", {}) if isinstance(value, dict) else {"_aggregate": "MALFORMED"}
        except (OSError, ValueError):
            return {"_aggregate": "MISSING_OR_MALFORMED"}

    quartet_cases = raw_cases("cases/checked-pointer-trace-quartets/aggregate.json",
                              "pointer-quartet-trace-diagnostic")
    actual_merge_cases = raw_cases("cases/checked-actual/aggregate.json",
                                   "actual-callee-applicability")
    bidirectional_cases = raw_cases("cases/checked-bidirectional-small/aggregate.json",
                                    "bidirectional-len23-diagnostic")
    modular_entry_cases = raw_cases("cases/checked-pointer-modular-trace-entry-negative/aggregate.json",
                                    "pointer-modular-trace-entry-negative")
    modular_trace_cases = raw_cases("cases/checked-pointer-modular-trace/aggregate.json",
                                    "pointer-modular-trace-diagnostic")
    pair_turnover_cases = raw_cases("cases/checked-source-pair-turnover/aggregate.json",
                                    "source-pair-turnover-resource-diagnostic")
    cleanup_hidden_cases = raw_cases("cases/checked-cleanup-recovery-hidden-type/aggregate.json",
                                     "cleanup-recovery-hidden-type-diagnostic")

    panic_candidates = []
    for path in cases.glob("**/panic-macro-origin.json"):
        try:
            cert = json.loads(path.read_text())
        except (OSError, ValueError):
            continue
        if (cert.get("status") == "PANIC_MACRO_BODY_ORIGIN_LINKED" and
                cert.get("require_final") is True and
                cert.get("expected_compiler_panic_rs_sha256") ==
                "b63eeb2d8e1fa130d3582253fd043fdcd722d16031b289c25f2437e2edda87dd" and
                cert.get("compiler_panic_rs_sha256") ==
                "b63eeb2d8e1fa130d3582253fd043fdcd722d16031b289c25f2437e2edda87dd"):
            panic_candidates.append(str(path.relative_to(root)))
    panic_required = "bidirectional-len23-diagnostic" in selected
    panic_ok = (not panic_required or any(
        item.startswith("allprooflogs/cases/checked-bidirectional-small/")
        for item in panic_candidates))

    runtime = {"name": "callback-destination-frame-probe",
               "source_alias": "366fcc78e20741bc7116a32884839061e68594f1",
               "is_verifast_theorem_or_caller_counterexample": False}
    runtime_required = selection["runtime_probe"]
    if runtime_required:
        runtime_case = cases / "callback-destination-frame-probe"
        try:
            runtime_status = int((evidence / "callback-destination-frame-driver-exit-code.txt").read_text().strip())
            observation = json.loads((runtime_case / "runtime-observation.json").read_text())
            source_admission = json.loads((runtime_case / "source-admission.json").read_text())
        except (OSError, ValueError):
            runtime_status, observation = None, {"classification": "INCONCLUSIVE_NOT_REPORTED"}
            source_admission = {}
        runtime_artifacts = all(path.is_file() for path in (
            runtime_case / "callback-destination-frame-probe.rs",
            runtime_case / "source-admission.json",
            runtime_case / "runtime-observation.json",
            evidence / "callback-destination-frame-driver.log",
            evidence / "callback-destination-frame-source-admission.log",
            evidence / "callback-destination-frame-source-admission-exit-code.txt",
            evidence / "callback-destination-frame-compiler-version.log",
            evidence / "callback-destination-frame-compiler-version-exit-code.txt",
            evidence / "callback-destination-frame-compiler-sysroot.log",
            evidence / "callback-destination-frame-compiler-sysroot-exit-code.txt",
            evidence / "callback-destination-frame-compile.log",
            evidence / "callback-destination-frame-compile-exit-code.txt",
            evidence / "callback-destination-frame-run.log",
            evidence / "callback-destination-frame-run-exit-code.txt",
        ))
        runtime_stage_exit_codes = {}
        for stage in ("source-admission", "compiler-version", "compiler-sysroot",
                      "compile", "run"):
            try:
                runtime_stage_exit_codes[stage] = int(
                    (evidence / f"callback-destination-frame-{stage}-exit-code.txt").read_text().strip())
            except (OSError, ValueError):
                runtime_stage_exit_codes[stage] = None
        source_admitted = (
            source_admission.get("admitted") is True and
            source_admission.get("source_pin_matches") is True and
            source_admission.get("whole_merge_up_byte_equal") is True and
            source_admission.get("source_sha256") ==
                "85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1" and
            source_admission.get("expected_source_sha256") ==
                "85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1" and
            source_admission.get("source_git_blob") == "40939f922bcb6fdc7ee0d30427fa861827043827" and
            source_admission.get("expected_source_git_blob") ==
                "40939f922bcb6fdc7ee0d30427fa861827043827" and
            source_admission.get("probe_sha256") == source_admission.get("copied_probe_sha256") and
            source_admission.get("actual_merge_up_sha256") ==
                source_admission.get("copied_merge_up_sha256"))
        runtime.update({"driver_exit_code": runtime_status,
                        "source_admission": source_admission,
                        "source_admission_pinned_and_byte_equal": source_admitted,
                        "runtime_observation": observation,
                        "stage_exit_codes": runtime_stage_exit_codes,
                        "artifacts_complete": runtime_artifacts})
        runtime_ok = (
            runtime_status == 0 and runtime_artifacts and
            observation.get("classification") ==
                "OBSERVED_DESTINATION_FRAME_CHANGE_ON_CALLBACK_UNWIND" and
            observation.get("source_admitted") is True and source_admitted and
            observation.get("compile_exit_code") == 0 and
            observation.get("run_exit_code") == 0 and
            observation.get("compiler_commit") ==
                "f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f" and
            observation.get("compiler_host") == "x86_64-unknown-linux-gnu" and
            isinstance(observation.get("compiler_binary_sha256"), str) and
            len(observation["compiler_binary_sha256"]) == 64 and
            observation.get("binary_sha256") and
            all(code == 0 for code in runtime_stage_exit_codes.values()))
    else:
        runtime.update({"driver_exit_code": "NOT_RUN",
                        "runtime_observation": {"classification": "NOT_RUN"},
                        "artifacts_complete": True})
        runtime_ok = True

    artifacts_complete = all(artifact_status.values()) and stages_complete and panic_ok and runtime_ok
    complete = (run_status == 0 and groups_exact and artifacts_complete and
                (cases.is_dir() or not any("cases/" in p for ps in mandatory.values() for p in ps)))
    mode_class = "FULL_TRANSFER_DIAGNOSTIC" if selection["full_transfer"] else "PARTIAL_DIAGNOSTIC"
    audit_row = {
        "schema": "smallsort-merge-cloud-diagnostic-v1",
        "lane": "merge", "proof_sha": proof_sha,
        "execution_provider": "cloud-build", "execution_id": build_id,
        "accepted": False, "diagnostic_complete": complete,
        "classification": mode_class if complete else "INCONCLUSIVE",
        "full_transfer": selection["full_transfer"], "selection_mode": selection["mode"],
        "selection_sha256": selection_hash,
        "selected_groups": sorted(selected), "not_run_groups": sorted(not_run),
        "mandatory_group_statuses": observed,
        "observed_group_set_exact": groups_exact,
        "not_run_groups_have_no_exit_records": skipped_have_no_exit_records,
        "per_group_stage_records": stage_status,
        "per_group_mandatory_artifacts": artifact_status,
        "mandatory_artifacts_complete": artifacts_complete,
        "final_panic_origin_certificates": panic_candidates,
        "panic_certificate_required": panic_required,
        "panic_certificate_complete": panic_ok,
        "theorem_statuses": {
            "whole_small_sort_challenge": "NOT_PROVEN",
            "g2_quartet_trace_cases": quartet_cases,
            "g2_modular_entry_control_cases": modular_entry_cases,
            "g2_modular_trace_cases": modular_trace_cases,
            "actual_bidirectional_len2_len3_cases": bidirectional_cases,
            "actual_merge_up_down_cases": actual_merge_cases,
            "source_pair_turnover_cases": pair_turnover_cases,
            "cleanup_recovery_hidden_type_cases": cleanup_hidden_cases,
        },
        "separate_runtime_candidate": runtime,
        "raw_group_status_path": "allprooflogs/group-status.txt",
        "raw_not_run_group_path": "allprooflogs/group-not-run.txt",
        "note": "Collector completion does not change per-case theorem classifications or establish a whole-function theorem.",
    }
    return audit_row


def sha256_file(path: Path) -> str:
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if len(sys.argv) != 6:
        raise SystemExit("usage: merge-audit.py EVIDENCE_ROOT SELECTION_JSON RUN_STATUS PROOF_SHA BUILD_ID")
    root = Path(sys.argv[1])
    row = audit(root, Path(sys.argv[2]), int(sys.argv[3]), sys.argv[4], sys.argv[5])
    (root / "proof-audit.json").write_text(json.dumps(row, indent=2, sort_keys=True) + "\n")
    return 0 if row["diagnostic_complete"] else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"merge evidence audit failed: {error}", file=sys.stderr)
        sys.exit(2)
