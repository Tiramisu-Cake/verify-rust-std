#!/usr/bin/env python3
"""Audit exact selected merge groups and their required evidence artifacts."""
from __future__ import annotations

import json
import hashlib
from pathlib import Path
import re
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
    "native-source-pair-turnover-resource-diagnostic": "checked-native-source-pair-turnover",
    "native-source-pair-turnover-stock-diagnostic": "checked-native-source-pair-turnover-stock",
    "cleanup-recovery-hidden-type-diagnostic": "checked-cleanup-recovery-hidden-type",
    "current-owner-handoff-resource-diagnostic": "checked-current-owner-handoff",
    "current-owner-handoff-stock-diagnostic": "checked-current-owner-handoff-stock",
    "checked-current-owner-permutation": "checked-current-owner-permutation",
    "checked-current-owner-permutation-stock": "checked-current-owner-permutation-stock",
}
PERMUTATION_GROUPS = {
    "checked-current-owner-permutation": {
        "directory": "checked-current-owner-permutation",
        "profile": "experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1",
    },
    "checked-current-owner-permutation-stock": {
        "directory": "checked-current-owner-permutation-stock",
        "profile": "stock-26.10-current-owner-permutation",
    },
}
PERMUTATION_CASES = (
    "current_owner_transposition",
    "current_owner_transposition_false_entry",
    "current_owner_transposition_double_owner_calibration",
)
BOUNDED_REQUIRED_BODIES = {
    "merge_up", "merge_down", "panic_on_ord_violation", "bidirectional_merge",
    "bidirectional_small_left_cell_association",
    "bidirectional_small_current_cell_alias",
}
DROP_GROUPS = {
    "actual-copy-on-drop-resource-diagnostic": {
        "directory": "actual-copy-on-drop-resource-diagnostic",
        "profile": "experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1",
    },
    "actual-copy-on-drop-stock-diagnostic": {
        "directory": "actual-copy-on-drop-stock-diagnostic",
        "profile": "stock-26.10",
    },
}
DROP_CASES = ("positive", "first_body_false")
DROP_STAGES = ("exporter", "decode", "verifast", "refinement")
DROP_SOURCE_SHA256 = "85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1"
DROP_SOURCE_BLOB = "40939f922bcb6fdc7ee0d30427fa861827043827"
DROP_BLOCK_SHA256 = "caff1edbfa3a8d9fd29459e49c43abd0f8f987f9061c75e7bf6ecedbbba26a6a"
OR_JOIN_GROUP = "mir-or-join-seven-diagnostic"
OR_JOIN_PROFILE = "experimental-merge-six-plus-mir-or-join-liveness-v1-unaccepted"
OR_JOIN_COMPONENT = Path(
    "research/challenge-8/merge/overnight/or-join-liveness")
OR_JOIN_MINIMUM_ARTIFACTS = [
    f"cases/{OR_JOIN_GROUP}/manifest-PINNED-INPUTS.json",
    f"cases/{OR_JOIN_GROUP}/seven-audit.json",
    f"cases/{OR_JOIN_GROUP}/seven-run-exit-code.txt",
    f"cases/{OR_JOIN_GROUP}/preflight.log",
    f"cases/{OR_JOIN_GROUP}/preflight-exit-code.txt",
    f"cases/{OR_JOIN_GROUP}/work-budget.txt",
    *[f"cases/{OR_JOIN_GROUP}/{name}-exit-code.txt" for name in
      ("calibrated-real-dead", "uncalibrated-liveness-controls", "actual-bounded")],
]
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
            if group in PERMUTATION_GROUPS:
                mandatory[group].extend([
                    f"cases/{name}/fixture-manifest.json",
                    f"cases/{name}/results.json",
                ])
        elif group in DROP_GROUPS:
            dirname = DROP_GROUPS[group]["directory"]
            mandatory[group] = [
                f"cases/{dirname}/environment.json",
                f"cases/{dirname}/extraction.json",
                f"cases/{dirname}/results.json",
                f"cases/{dirname}/aggregate.json",
                *[f"cases/{dirname}/cases/{case}/classification.json" for case in DROP_CASES],
            ]
        elif group == OR_JOIN_GROUP:
            mandatory[group] = OR_JOIN_MINIMUM_ARTIFACTS
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

    def audit_current_owner_permutation(group: str, spec: dict) -> bool:
        base = cases / spec["directory"]
        fixture_path = (Path(__file__).resolve().parents[4] /
                        "research/challenge-8/merge/overnight/current-owner-permutation-cases.rs")
        try:
            aggregate = json.loads((base / "aggregate.json").read_text())
            fixture = json.loads((base / "fixture-manifest.json").read_text())
            results = json.loads((base / "results.json").read_text())
            admission_path = base / "full-small-sort-source-admission.json"
            admission = json.loads(admission_path.read_text())
            if not all(isinstance(value, dict) for value in
                       (aggregate, fixture, results, admission)):
                return False
            case_order = fixture.get("case_order")
            metadata = fixture.get("cases")
            rows = results.get("cases")
            raw_aggregate = aggregate.get("cases")
            if (case_order != list(PERMUTATION_CASES) or
                    not isinstance(metadata, dict) or not isinstance(rows, dict) or
                    not isinstance(raw_aggregate, dict) or
                    set(metadata) != set(PERMUTATION_CASES) or
                    set(rows) != set(PERMUTATION_CASES) or
                    set(raw_aggregate) != set(PERMUTATION_CASES) or
                    any(not isinstance(rows.get(name), dict) for name in PERMUTATION_CASES) or
                    raw_aggregate != {name: rows[name].get("classification")
                                      for name in PERMUTATION_CASES} or
                    fixture.get("fixture_sha256") != sha256_file(fixture_path) or
                    not isinstance(results.get("profile"), str) or
                    results.get("profile", "").split(";", 1)[0] != spec["profile"] or
                    results.get("source_admission_sha256") != sha256_file(admission_path) or
                    aggregate.get("evidence_collection_completed") is not True or
                    aggregate.get("classifier_controls_passed") is not True):
                return False
            if (admission.get("full_source_sha256") !=
                    "85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1"):
                return False
            for name in PERMUTATION_CASES:
                meta = metadata[name]
                row = rows[name]
                if not isinstance(meta, dict) or not isinstance(row, dict):
                    return False
                if (meta.get("case") != name or meta.get("ghost_strip_exact_bytes") is not True or
                        meta.get("expected_bodies") != [name] or
                        row.get("accepted") is not False or
                        row.get("source_unchanged_at_every_stage") is not True or
                        row.get("source_before") != row.get("source_after") or
                        not isinstance(row.get("source_before"), dict) or
                        row["source_before"].get("original/lib.rs") != meta.get("original_sha256") or
                        row["source_before"].get("verified/lib.rs") != meta.get("verified_sha256")):
                    return False
                case_dir = base / "cases" / name
                for rel, expected in (("original/lib.rs", meta.get("original_sha256")),
                                      ("verified/lib.rs", meta.get("verified_sha256"))):
                    path = case_dir / rel
                    if (not path.is_file() or path.is_symlink() or
                            sha256_file(path) != expected):
                        return False
                unchanged_hashes = row.get("source_before")
                if (not isinstance(unchanged_hashes, dict) or
                        unchanged_hashes.get("original/lib.rs") != sha256_file(case_dir / "original/lib.rs") or
                        unchanged_hashes.get("verified/lib.rs") != sha256_file(case_dir / "verified/lib.rs")):
                    return False
                stages = row.get("stages")
                if not isinstance(stages, dict) or set(stages) != {"exporter", "decode", "verifast", "refinement"}:
                    return False
                for stage, code in stages.items():
                    paths = (case_dir / f"{stage}.out", case_dir / f"{stage}.log",
                             case_dir / f"{stage}-resources.txt", case_dir / f"{stage}-exit-code.txt",
                             case_dir / f"source-integrity-{stage}.json")
                    if any(not path.is_file() or path.is_symlink() for path in paths):
                        return False
                    integrity = json.loads(paths[-1].read_text())
                    if (int(paths[3].read_text().strip()) != code or
                            integrity.get("exit_code") != code or integrity.get("unchanged") is not True or
                            integrity.get("source_before") != unchanged_hashes or
                            integrity.get("source_after") != unchanged_hashes):
                        return False
                classification = row.get("classification")
                bodies = meta.get("expected_bodies")
                body_execution = row.get("body_execution_records")
                body_records = row.get("per_body_records")
                classifier_controls = row.get("classifier_fail_closed_mutations")
                if (not isinstance(bodies, list) or bodies != [name] or
                        not isinstance(body_execution, dict) or not isinstance(body_records, dict) or
                        not isinstance(classifier_controls, dict) or not classifier_controls or
                        not all(value is True for value in classifier_controls.values()) or
                        any(not isinstance(body_records.get(body), dict) for body in bodies) or
                        any(type(stages.get(stage)) is not int for stage in stages)):
                    return False
                if name == "current_owner_transposition_false_entry":
                    expected = meta.get("expected_error")
                    observed_error = row.get("observed_error")
                    if (meta.get("negative") is not True or
                            meta.get("unclassified_target") is not False or
                            not isinstance(expected, dict) or
                            row.get("expected_error") != expected or classification not in
                            {"EXPECTED_FALSE_ASSERTION", "INCONCLUSIVE"}):
                        return False
                    if classification == "EXPECTED_FALSE_ASSERTION" and (
                            expected.get("stage") != "verifast" or
                            expected.get("predicate") != "false" or
                            expected.get("line") != meta.get("marked_target_line") or
                            row.get("full_positive_gate") is not False or
                            row.get("stages") != {"exporter": 0, "decode": 0, "verifast": 1, "refinement": 0} or
                            not isinstance(observed_error, dict) or
                            any(observed_error.get(key) != expected.get(key) for key in
                                ("line", "column_start", "column_end", "predicate")) or
                            observed_error.get("target_executed") is not True or
                            any(body_execution.get(body, 0) <= 0 for body in bodies) or
                            row.get("dead_code_records")):
                        return False
                elif name == "current_owner_transposition_double_owner_calibration":
                    if (meta.get("negative") is not False or
                            meta.get("unclassified_target") is not True or
                            meta.get("expected_error") is not None or
                            meta.get("expected_rejection") is not None or
                            meta.get("expected_dead") is not None or
                            classification not in {"PASS", "INCONCLUSIVE"}):
                        return False
                    if classification == "PASS" and not row.get("full_positive_gate"):
                        return False
                else:
                    if (meta.get("negative") is not False or
                            meta.get("expected_error") is not None or
                            classification not in {"PASS", "INCONCLUSIVE"}):
                        return False
                    if classification == "PASS" and not row.get("full_positive_gate"):
                        return False
                if classification == "PASS":
                    if (not all(stages.get(stage) == 0 for stage in stages) or
                            row.get("error_lines") or row.get("dead_code_records") or
                            any(body_execution.get(body, 0) <= 0 for body in bodies) or
                            any(body_records.get(body, {}).get("return", 0) <= 0 or
                                body_records.get(body, {}).get("leak", 0) <= 0 for body in bodies) or
                            not row.get("classifier_fail_closed_mutations") or
                            not all(row["classifier_fail_closed_mutations"].values())):
                        return False
            return True
        except (OSError, ValueError, KeyError, TypeError, AttributeError):
            return False

    permutation_cases: dict[str, dict] = {}
    for group, spec in PERMUTATION_GROUPS.items():
        if group in selected:
            valid = artifact_status.get(group, False) and audit_current_owner_permutation(group, spec)
            artifact_status[group] = valid
            try:
                aggregate = json.loads((cases / spec["directory"] / "aggregate.json").read_text())
                permutation_cases[group] = {
                    "accepted": False,
                    "raw_case_statuses": aggregate.get("cases", {}),
                    "double_owner_calibration": aggregate.get("cases", {}).get(
                        "current_owner_transposition_double_owner_calibration", "INCONCLUSIVE"),
                    "double_owner_interpretation": "CALIBRATION_ONLY_NO_INTENDED_ORACLE",
                    "audit_valid": valid,
                }
            except (OSError, ValueError, TypeError, AttributeError):
                permutation_cases[group] = {"classification": "INCONCLUSIVE", "accepted": False,
                                            "cases": {}, "audit_valid": False}
        else:
            permutation_cases[group] = {"classification": "NOT_RUN", "accepted": False, "cases": {}}

    bounded_source_pin: dict = {"classification": "NOT_RUN", "accepted": False}
    bounded_source_pin_ok = "bidirectional-small-source-preparation" not in selected
    if "bidirectional-small-source-preparation" in selected:
        try:
            pin_path = root / "bounded-source-pin.json"
            pin = json.loads(pin_path.read_text())
            pin_cases = root / "bounded-source-pin/cases"
            extracted = json.loads((pin_cases / "extraction.json").read_text())
            case_meta = extracted.get("cases", {}).get("bidirectional_merge_len23", {})
            fixture_path = evidence / "bidirectional-small-cases.rs"
            admission_path = evidence / "bidirectional-small-cases.admission.json"
            actual_source = (Path(__file__).resolve().parents[4] /
                             "library/core/src/slice/sort/shared/smallsort.rs")
            harness = (Path(__file__).resolve().parents[4] /
                       "research/challenge-8/merge/overnight/pointer-prove.py")
            original = pin_cases / "bidirectional_merge_len23/original/lib.rs"
            verified = pin_cases / "bidirectional_merge_len23/verified/lib.rs"
            build_runtime = evidence / "build/source-build-runtime.txt"
            runtime_first = build_runtime.read_text(errors="replace").splitlines()[0].split()
            fresh_console = runtime_first[0] if len(runtime_first) == 2 else None
            admission = json.loads(admission_path.read_text())
            body_meta = admission.get("cases", {}).get("bidirectional_merge", {})
            source_signature = "unsafe fn bidirectional_merge<T: FreezeMarker, F: FnMut(&T, &T) -> bool>("
            guard_statement = "if left != left_end || right != right_end {"
            actual_bytes = actual_source.read_bytes()
            verified_bytes = verified.read_bytes()
            actual_signature_line = actual_bytes[:actual_bytes.index(source_signature.encode())].count(b"\n") + 1
            actual_guard_line = actual_bytes[:actual_bytes.index(guard_statement.encode())].count(b"\n") + 1
            verified_signature_line = verified_bytes[:verified_bytes.index(source_signature.encode())].count(b"\n") + 1
            verified_guard_line = verified_bytes[:verified_bytes.index(guard_statement.encode())].count(b"\n") + 1
            actual_body_start = actual_bytes.index(source_signature.encode())
            actual_body_end = actual_bytes.index(b"\n}\n", actual_body_start) + 2
            actual_body_sha256 = hashlib.sha256(actual_bytes[actual_body_start:actual_body_end]).hexdigest()
            extracted_body_names = checked_body_names(verified_bytes)
            bounded_source_pin_ok = (
                pin.get("schema") == "smallsort-bounded-source-pin-v1" and
                pin.get("accepted") is False and
                pin.get("admission_state") == "PINNED_LITERAL_CANDIDATE" and
                pin.get("classification") == "SOURCE_PROVENANCE_ONLY" and
                pin.get("case") == "bidirectional_merge_len23" and
                pin.get("small_sort_source_sha256") ==
                    "85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1" ==
                    sha256_file(actual_source) == pin.get("small_sort_source_sha256") and
                pin.get("fixture_sha256") == sha256_file(fixture_path) ==
                    extracted.get("fixture_sha256") and
                pin.get("retained_pointer_prove_sha256") == sha256_file(harness) and
                pin.get("verified_lib_sha256") == sha256_file(verified) ==
                    case_meta.get("verified_sha256") and
                pin.get("original_lib_sha256") == sha256_file(original) ==
                    case_meta.get("original_sha256") and
                case_meta.get("ghost_strip_exact_bytes") is True and
                case_meta.get("expected_bodies") == extracted_body_names and
                BOUNDED_REQUIRED_BODIES.issubset(set(extracted_body_names)) and
                body_meta.get("exact_source_sha256") == pin.get("actual_bidirectional_body_sha256") == actual_body_sha256 and
                pin.get("base_stock_console_sha256") ==
                    "9b7650ad3ab0dad3b8974ae9ba1c662ab2cd897ce1dd07215dedcbe460249ee1" and
                pin.get("fresh_experimental_console_sha256") == fresh_console and
                pin.get("source_signature") == source_signature and
                actual_bytes.count(source_signature.encode()) == 1 and
                verified_bytes.count(source_signature.encode()) == 1 and
                pin.get("guard_statement") == guard_statement and
                actual_bytes.count(guard_statement.encode()) == 1 and
                verified_bytes.count(guard_statement.encode()) == 1 and
                pin.get("actual_source_signature_line") == actual_signature_line == 754 and
                pin.get("actual_source_guard_line") == actual_guard_line == 831 and
                pin.get("verified_signature_line") == verified_signature_line > 0 and
                pin.get("verified_guard_line") == verified_guard_line > verified_signature_line and
                pin.get("expected_bodies") == extracted_body_names
            )
            bounded_source_pin = {
                "classification": pin.get("classification", "INCONCLUSIVE"),
                "admission_state": pin.get("admission_state", "INCONCLUSIVE"),
                "accepted": False,
                "audit_valid": bounded_source_pin_ok,
                "fixture_sha256": pin.get("fixture_sha256"),
                "actual_bidirectional_body_sha256": pin.get("actual_bidirectional_body_sha256"),
                "expected_bodies": pin.get("expected_bodies"),
                "small_sort_source_sha256": pin.get("small_sort_source_sha256"),
                "actual_source_signature_line": pin.get("actual_source_signature_line"),
                "actual_source_guard_line": pin.get("actual_source_guard_line"),
                "verified_signature_line": pin.get("verified_signature_line"),
                "verified_guard_line": pin.get("verified_guard_line"),
                "base_stock_console_sha256": pin.get("base_stock_console_sha256"),
                "fresh_experimental_console_sha256": pin.get("fresh_experimental_console_sha256"),
            }
        except (OSError, ValueError, KeyError, TypeError, IndexError, AttributeError):
            bounded_source_pin = {"classification": "INCONCLUSIVE", "accepted": False,
                                  "audit_valid": False}

    def audit_copy_on_drop(group: str, spec: dict) -> bool:
        base = cases / spec["directory"]
        try:
            environment = json.loads((base / "environment.json").read_text())
            extraction = json.loads((base / "extraction.json").read_text())
            results = json.loads((base / "results.json").read_text())
            aggregate = json.loads((base / "aggregate.json").read_text())
            if (not all(isinstance(item, dict) for item in
                        (environment, extraction, results, aggregate)) or
                    environment.get("profile") != spec["profile"] or
                    environment.get("proof_sha") != proof_sha or
                    environment.get("cloud_build_id") != build_id or
                    environment.get("provider") != "cloud-build" or
                    environment.get("semantic_profile_accepted") is not False or
                    environment.get("small_sort_source_sha256") != DROP_SOURCE_SHA256 or
                    environment.get("small_sort_source_git_blob") != DROP_SOURCE_BLOB or
                    environment.get("schema_sha256") != "f48fcf29b99717c2e0cb37d4708b47eccaa3270b999e4a84093e37fbd51b7469" or
                    Path(environment.get("profile_evidence", "")).resolve() !=
                        (evidence / ("build" if spec["profile"] != "stock-26.10" else "")).resolve() or
                    results.get("profile") != spec["profile"] or
                    results.get("accepted") is not False or
                    aggregate.get("accepted") is not False or
                    aggregate.get("stages_collected") is not True or
                    aggregate.get("classification") not in {"PARTIAL_DIAGNOSTIC", "INCONCLUSIVE"}):
                return False
            compiler = environment.get("compiler_version_verbose", "")
            profile_pins = environment.get("profile_pins")
            tool_hashes = environment.get("tool_hashes")
            if (not isinstance(profile_pins, dict) or not isinstance(tool_hashes, dict) or
                    "commit-hash: f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f" not in compiler or
                    "host: x86_64-unknown-linux-gnu" not in compiler or
                    not isinstance(environment.get("compiler_rustc_sha256"), str) or
                    len(environment["compiler_rustc_sha256"]) != 64 or
                    not isinstance(environment.get("compiler_driver_hashes"), dict) or
                    not environment["compiler_driver_hashes"] or
                    any(not isinstance(value, str) or len(value) != 64
                        for value in environment["compiler_driver_hashes"].values()) or
                    not all(isinstance(value, str) and len(value) == 64
                            for value in tool_hashes.values())):
                return False
            if spec["profile"] == "experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1":
                expected_outputs = {
                    "kernel_patched": "100eebae92c770a0b8cd57e2639588761f881316dd522fc3b9a9b1ec6fd91cd6",
                    "translator_patched": "ffd6fe925364b8274d61f094d43211f9463e0dc3e98ae545d3f528f2da0cf6c0",
                    "parser_patched": "8ed673086183323058aac5e0e21399e4532d1e74b97c5d41105827e8643107bd",
                    "prelude_patched": "d1079bc94ceafe6595c7ce216f9c93e3436d22d849bd31bcb0cf442dd183e751",
                    "stdlib_patched": "d92e5044bbb2692e7b006fc649df361fe80bf878b69b5a2bb80635a27330f227",
                    "z3_runtime": "1837668dc531d14b3a4fffc0b690b77929d29c41868f98a89686f5ff64da95ea",
                    "applied_patch_sha256": "b163d3e36b695304cbc6c84d025af7bd5d679a5fb553356baa8b8362dea1b927",
                }
                if any(profile_pins.get(key) != value for key, value in expected_outputs.items()):
                    return False
                if (tool_hashes.get("bin/verifast") != profile_pins.get("experimental_console_sha256") or
                        tool_hashes.get("bin/vf-rust-mir-exporter") != profile_pins.get("bin/vf-rust-mir-exporter") or
                        tool_hashes.get("bin/refinement-checker") != profile_pins.get("bin/refinement-checker")):
                    return False
            elif spec["profile"] == "stock-26.10":
                expected_stock = {
                    "bin/verifast": "9b7650ad3ab0dad3b8974ae9ba1c662ab2cd897ce1dd07215dedcbe460249ee1",
                    "bin/vf-rust-mir-exporter": "b00c75f43ab4d89bf85f5e62a5114a238b89b720d4598d90423347b9d97ac796",
                    "bin/refinement-checker": "b049c8d1b0bb350f77664e1c75c5a95966c5839984abc25c7cb629c0cba04d28",
                    "prelude_sha256": "d7058d43557a2b5147eb1377e85bb67d04b94c83594b6c1c27650c9c571841b5",
                }
                if any(profile_pins.get(key) != value for key, value in expected_stock.items()):
                    return False
                if any(tool_hashes.get(key) != value for key, value in expected_stock.items()
                       if key != "prelude_sha256"):
                    return False
            if (extraction.get("selection") != "copy_on_drop_actual_count_n_diagnostic" or
                    extraction.get("source_sha256") != DROP_SOURCE_SHA256 or
                    extraction.get("source_git_blob") != DROP_SOURCE_BLOB or
                    extraction.get("block_sha256") != DROP_BLOCK_SHA256 or
                    extraction.get("block_bytes") != 364 or
                    extraction.get("target") != "<CopyOnDrop<T> as core::ops::Drop>::drop"):
                return False
            result_cases = results.get("cases")
            aggregate_cases = aggregate.get("cases")
            extraction_cases = extraction.get("cases")
            if (not all(isinstance(value, dict) for value in
                        (result_cases, aggregate_cases, extraction_cases)) or
                    set(result_cases) != set(DROP_CASES) or
                    set(aggregate_cases) != set(DROP_CASES) or
                    set(extraction_cases) != set(DROP_CASES)):
                return False
            if aggregate_cases != {name: result_cases[name].get("classification")
                                   for name in DROP_CASES}:
                return False
            for case in DROP_CASES:
                case_dir = base / "cases" / case
                metadata = extraction_cases[case]
                row = result_cases[case]
                classification_path = case_dir / "classification.json"
                classification = json.loads(classification_path.read_text())
                if (not isinstance(row, dict) or not isinstance(classification, dict) or
                        row.get("accepted") is not False or classification.get("accepted") is not False or
                        row != classification or
                        row.get("case") != case or
                        row.get("classification") not in {"PASS_COMPONENT_ONLY", "EXPECTED_FALSE_ASSERTION", "INCONCLUSIVE"}):
                    return False
                for rel, expected in (("original/lib.rs", metadata.get("original_sha256")),
                                      ("verified/lib.rs", metadata.get("verified_sha256"))):
                    source_path = case_dir / rel
                    if (not source_path.is_file() or source_path.is_symlink() or
                            sha256_file(source_path) != expected):
                        return False
                initial = classification.get("initial_source_hashes")
                final = classification.get("final_source_hashes")
                source_before_record = json.loads((case_dir / "source-before.json").read_text())
                if (classification.get("source_unchanged_at_every_stage") is not True or
                        not isinstance(initial, dict) or final != initial or
                        source_before_record != initial or
                        initial.get("small_sort_source") != DROP_SOURCE_SHA256 or
                        initial.get("original/lib.rs") != metadata.get("original_sha256") or
                        initial.get("verified/lib.rs") != metadata.get("verified_sha256")):
                    return False
                stages = classification.get("stages")
                if not isinstance(stages, dict) or set(stages) != set(DROP_STAGES):
                    return False
                for stage in DROP_STAGES:
                    stage_json = case_dir / f"{stage}-stage.json"
                    stage_log = case_dir / f"{stage}.log"
                    stage_out = case_dir / ("compiler-mir.bin" if stage == "exporter" else f"{stage}.out")
                    stage_resources = case_dir / f"{stage}-resources.txt"
                    stage_exit = case_dir / f"{stage}-exit-code.txt"
                    if not all(path.is_file() and not path.is_symlink()
                               for path in (stage_json, stage_log, stage_out,
                                            stage_resources, stage_exit)):
                        return False
                    stage_record = json.loads(stage_json.read_text())
                    if (not isinstance(stage_record, dict) or
                            stage_record.get("exit_code") != stages.get(stage) or
                            int(stage_exit.read_text().strip()) != stages.get(stage)):
                        return False
                    if stage_record.get("status") == "NOT_RUN":
                        if stage != "decode" or stages.get("exporter") == 0:
                            return False
                    elif (stage_record.get("source_unchanged") is not True or
                          stage_record.get("source_before") != initial or
                          stage_record.get("source_after") != final):
                        return False
                mir_binary = case_dir / "compiler-mir.bin"
                mir_hash_file = case_dir / "compiler-mir-sha256.txt"
                if (not all(path.is_file() and not path.is_symlink()
                            for path in (mir_binary, mir_hash_file)) or
                        mir_hash_file.read_text().strip() != sha256_file(mir_binary)):
                    return False
            return True
        except (OSError, ValueError, KeyError, TypeError):
            return False

    for group, spec in DROP_GROUPS.items():
        if group in selected:
            artifact_status[group] = artifact_status.get(group, False) and audit_copy_on_drop(group, spec)

    or_join_status = {
        "component": "MIR-OR-JOIN-LIVENESS",
        "profile": OR_JOIN_PROFILE,
        "accepted": False,
        "component_gates_complete": False,
        "manifest_admission_state": "MISSING",
        "raw_seven_audit": None,
        "artifact_hash_bindings_valid": False,
        "diagnostic_complete": False,
        "note": "coverage-origin experiment remains separate from theorem and profile acceptance",
    }
    def audit_or_join() -> bool:
        base = cases / OR_JOIN_GROUP
        try:
            manifest_path = base / "manifest-PINNED-INPUTS.json"
            manifest = json.loads(manifest_path.read_text())
            seven = json.loads((base / "seven-audit.json").read_text())
            original_manifest = (Path(__file__).resolve().parents[4] /
                                OR_JOIN_COMPONENT / "PINNED-INPUTS.json")
            manifest_bytes_match = (original_manifest.is_file() and
                                    manifest_path.read_bytes() == original_manifest.read_bytes())
            or_join_status.update({
                "manifest_admission_state": manifest.get("admission_state"),
                "manifest_sha256": sha256_file(manifest_path),
                "raw_seven_audit": seven,
                "diagnostic_complete": seven.get("diagnostic_complete") is True,
            })
            raw_groups = base / "group-status.txt"
            or_join_status["raw_component_group_statuses"] = (
                raw_groups.read_text(errors="replace").splitlines()
                if raw_groups.is_file() else [])
            minimum = all((evidence / rel).is_file() and not (evidence / rel).is_symlink()
                          for rel in OR_JOIN_MINIMUM_ARTIFACTS)
            run_status_path = base / "seven-run-exit-code.txt"
            run_status = int(run_status_path.read_text().strip()) if run_status_path.is_file() else None
            group_exit = evidence / f"group-{OR_JOIN_GROUP}-exit-code.txt"
            external_status = int(group_exit.read_text().strip()) if group_exit.is_file() else None
            inner_group_names = ("calibrated-real-dead", "uncalibrated-liveness-controls",
                                 "actual-bounded")
            raw_inner_groups = seven.get("group_status")
            inner_statuses_bound = isinstance(raw_inner_groups, dict) and set(raw_inner_groups) == set(inner_group_names)
            if inner_statuses_bound:
                inner_statuses_bound = all(
                    (base / f"{name}-exit-code.txt").read_text().strip() == raw_inner_groups[name]
                    for name in inner_group_names)
            budget_text = (base / "work-budget.txt").read_text(errors="replace")
            budget_match = re.search(r"\bbudget=([0-9]+)\b", budget_text)
            lane_budget_lines = (root / "lane-work-budget.txt").read_text(errors="replace").splitlines()
            lane_budget_match = next((re.fullmatch(r"mir_or_join_work_seconds=([0-9]+)", line)
                                      for line in lane_budget_lines
                                      if line.startswith("mir_or_join_work_seconds=")), None)
            inner_budget = int(budget_match.group(1)) if budget_match else None
            outer_budget = int(lane_budget_match.group(1)) if lane_budget_match else None
            budget_bound = (inner_budget is not None and inner_budget == outer_budget and
                            1 <= inner_budget <= 900)
            or_join_status["raw_inner_group_statuses"] = raw_inner_groups
            or_join_status["inner_group_statuses_bound"] = bool(inner_statuses_bound)
            or_join_status["work_budget_seconds"] = inner_budget
            or_join_status["outer_work_budget_seconds"] = outer_budget
            component_identity = (
                seven.get("component") == "MIR-OR-JOIN-LIVENESS" and
                seven.get("profile") == OR_JOIN_PROFILE and
                seven.get("accepted") is False and
                seven.get("component_gates_complete") is False and
                seven.get("base_six_profile_accepted") is False and
                seven.get("invalid_shape_admission_controls") == "NOT_RUN" and
                seven.get("same_source_six_component_comparison") == "NOT_RUN")
            pin_fields = (
                manifest.get("component") == "MIR-OR-JOIN-LIVENESS" and
                manifest.get("verifast_commit") == "f76012fb518703b1d98e243ac4f487f16877cfcb" and
                manifest.get("baseline_profile") == "existing-six-patch-experimental-unaccepted" and
                manifest.get("admission_state") == "EXPERIMENTAL_CLOUD_TRIAL" and
                all(isinstance(manifest.get(key), str) and
                    len(manifest[key]) == 64 and
                    all(ch in "0123456789abcdef" for ch in manifest[key])
                    for key in ("baseline_applied_profile_sha256",
                                "baseline_translator_sha256", "baseline_console_sha256",
                                "baseline_kernel_sha256", "baseline_parser_sha256",
                                "baseline_prelude_sha256", "baseline_stdlib_sha256",
                                "release_exporter_sha256", "release_refiner_sha256",
                                "component_patch_sha256", "component_translator_sha256",
                                "admission_checker_sha256", "preflight_checker_sha256",
                                "audit_checker_sha256", "retained_pointer_prove_sha256",
                                "diagnostic_source_sha256", "admitted_fixture_sha256",
                                "admitted_source_sha256")) and
                isinstance(manifest.get("admitted_signature_line"), int) and
                isinstance(manifest.get("admitted_guard_line"), int) and
                manifest.get("admitted_signature_line") > 0 and
                manifest.get("admitted_guard_line") > manifest.get("admitted_signature_line"))
            pin_bindings = False
            full_evidence_valid = False
            if pin_fields:
                preflight = json.loads((base / "preflight/or-join-preflight.json").read_text())
                fixture = evidence / "bidirectional-small-cases.rs"
                harness = (Path(__file__).resolve().parents[4] /
                           "research/challenge-8/merge/overnight/pointer-prove.py")
                actual_source = base / "actual/cases/bidirectional_merge_len23/verified/lib.rs"
                pin_bindings = (
                    preflight.get("accepted") is False and
                    preflight.get("fixture_sha256") == manifest.get("admitted_fixture_sha256") ==
                        sha256_file(fixture) and
                    preflight.get("verified_sha256") == manifest.get("admitted_source_sha256") ==
                        sha256_file(actual_source) and
                    preflight.get("retained_pointer_prove_sha256") ==
                        manifest.get("retained_pointer_prove_sha256") == sha256_file(harness))
                if seven.get("diagnostic_complete") is True:
                    complete_paths = [
                        "build/seven-profile-manifest.json",
                        "build/seven-build-exit-code.txt",
                        "build/seven-source-home.txt",
                        "build/translator.six.ml", "build/translator.seven.ml",
                        "build/full-seven-applied-profile.patch",
                        "build/base-six-applied-profile.patch",
                        "build/seven-modified-files.txt", "build/seven-profile-hashes.txt",
                        "preflight/or-join-preflight.json",
                        "preflight/extraction.json",
                        "preflight/bidirectional_merge_len23/original/lib.rs",
                        "preflight/bidirectional_merge_len23/verified/lib.rs",
                        "source-admission.log", "source-admission-exit-code.txt",
                        "actual/aggregate.json", "actual/results.json",
                        "calibrated-real-dead/aggregate.json",
                        "calibrated-real-dead/results.json",
                        "uncalibrated-liveness-controls/aggregate.json",
                        "uncalibrated-liveness-controls/results.json",
                    ]
                    complete_files = all(
                        (base / rel).is_file() and not (base / rel).is_symlink()
                        for rel in complete_paths)
                    build = json.loads((base / "build/seven-profile-manifest.json").read_text())
                    actual_results = json.loads((base / "actual/results.json").read_text())
                    actual_aggregate = json.loads((base / "actual/aggregate.json").read_text())
                    dead_results = json.loads((base / "calibrated-real-dead/results.json").read_text())
                    dead_aggregate = json.loads((base / "calibrated-real-dead/aggregate.json").read_text())
                    control_results = json.loads((base / "uncalibrated-liveness-controls/results.json").read_text())
                    control_aggregate = json.loads((base / "uncalibrated-liveness-controls/aggregate.json").read_text())
                    case_name = "bidirectional_merge_len23"
                    actual_row = actual_results.get("cases", {}).get(case_name, {})
                    dead_row = dead_results.get("cases", {}).get("unreachable_body_after_panic", {})
                    control_rows = control_results.get("cases", {})
                    expected_controls = {"dead_real_return", "dead_panic_body",
                                         "dead_source_break", "dead_source_continue"}
                    build_home = Path((base / "build/seven-source-home.txt").read_text().strip())
                    seven_console = build_home / "bin/verifast"
                    actual_case = base / "actual/cases" / case_name
                    preflight_source = base / "preflight" / case_name / "verified/lib.rs"
                    full_evidence_valid = (
                        complete_files and build.get("accepted") is False and
                        build.get("source_commit") == manifest.get("verifast_commit") and
                        build.get("base_six_console_sha256") == manifest.get("baseline_console_sha256") and
                        build.get("base_six_full_diff_sha256") ==
                            manifest.get("baseline_applied_profile_sha256") and
                        build.get("seven_full_diff_sha256") ==
                            sha256_file(base / "build/full-seven-applied-profile.patch") and
                        build.get("component_manifest_sha256") == sha256_file(manifest_path) and
                        build.get("component_patch_sha256") == manifest.get("component_patch_sha256") and
                        build.get("baseline_translator_sha256") == manifest.get("baseline_translator_sha256") and
                        build.get("component_translator_sha256") == manifest.get("component_translator_sha256") and
                        build.get("kernel_unchanged") is True and build.get("parser_unchanged") is True and
                        build.get("prelude_unchanged") is True and build.get("stdlib_unchanged") is True and
                        build.get("exporter_unchanged") is True and build.get("refiner_unchanged") is True and
                        (base / "build/seven-modified-files.txt").read_text().splitlines() ==
                            ["src/rust_frontend/vf_mir_translator/vf_mir_translator.ml"] and
                        sha256_file(seven_console) == build.get("seven_console_sha256") and
                        actual_aggregate.get("evidence_collection_completed") is True and
                        actual_aggregate.get("classifier_controls_passed") is True and
                        set(actual_results.get("cases", {})) == {case_name} and
                        set(actual_aggregate.get("cases", {})) == {case_name} and
                        preflight.get("verified_sha256") == sha256_file(preflight_source) ==
                            sha256_file(actual_case / "verified/lib.rs") and
                        preflight.get("original_sha256") == sha256_file(actual_case / "original/lib.rs") and
                        isinstance(actual_row, dict) and isinstance(dead_row, dict) and
                        actual_row.get("classification") == seven.get("actual_bounded_raw_classification") and
                        seven.get("actual_bounded_full_positive") ==
                            (actual_row.get("full_positive_gate") is True) and
                        actual_aggregate.get("cases", {}).get(case_name) == actual_row.get("classification") and
                        dead_aggregate.get("evidence_collection_completed") is True and
                        dead_aggregate.get("classifier_controls_passed") is True and
                        set(dead_results.get("cases", {})) == {"unreachable_body_after_panic"} and
                        set(dead_aggregate.get("cases", {})) == {"unreachable_body_after_panic"} and
                        dead_row.get("classification") == seven.get("calibrated_real_dead_raw_classification") and
                        seven.get("calibrated_real_dead_proof_negative") ==
                            (dead_row.get("expected_dead_code_gate") is True) and
                        dead_aggregate.get("cases", {}).get("unreachable_body_after_panic") ==
                            dead_row.get("classification") and
                        control_aggregate.get("evidence_collection_completed") is True and
                        control_aggregate.get("classifier_controls_passed") is True and
                        set(control_rows) == expected_controls == set(seven.get("new_liveness_controls", {})) ==
                            set(control_aggregate.get("cases", {})) and
                        all(isinstance(row, dict) and
                            control_aggregate["cases"].get(name) == row.get("classification")
                            for name, row in control_rows.items()) and
                        all(seven["new_liveness_controls"][name].get("raw_classification") ==
                            control_rows[name].get("classification") and
                            seven["new_liveness_controls"][name].get("classification") in
                                {"CALIBRATION_ONLY", "INCONCLUSIVE"} and
                            seven["new_liveness_controls"][name].get("complete") is True
                            for name in expected_controls)
                    )
            or_join_status["artifact_hash_bindings_valid"] = bool(
                manifest_bytes_match and pin_bindings and
                (seven.get("diagnostic_complete") is not True or full_evidence_valid))
            or_join_status["complete_evidence_hash_bindings_valid"] = bool(full_evidence_valid)
            or_join_status["run_script_exit_code"] = run_status
            or_join_status["lane_group_exit_code"] = external_status
            return bool(minimum and manifest_bytes_match and component_identity and
                        run_status is not None and external_status is not None and
                        inner_statuses_bound and budget_bound and
                        (not pin_fields or pin_bindings) and
                        (seven.get("diagnostic_complete") is not True or full_evidence_valid))
        except (OSError, ValueError, KeyError, TypeError):
            return False

    if OR_JOIN_GROUP in selected:
        artifact_status[OR_JOIN_GROUP] = (
            artifact_status.get(OR_JOIN_GROUP, False) and audit_or_join())

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
    native_pair_cases = raw_cases("cases/checked-native-source-pair-turnover/aggregate.json",
                                  "native-source-pair-turnover-resource-diagnostic")
    native_stock_pair_cases = raw_cases("cases/checked-native-source-pair-turnover-stock/aggregate.json",
                                        "native-source-pair-turnover-stock-diagnostic")
    cleanup_hidden_cases = raw_cases("cases/checked-cleanup-recovery-hidden-type/aggregate.json",
                                     "cleanup-recovery-hidden-type-diagnostic")

    copy_on_drop_resource_cases = raw_cases(
        "cases/actual-copy-on-drop-resource-diagnostic/aggregate.json",
        "actual-copy-on-drop-resource-diagnostic")
    copy_on_drop_stock_cases = raw_cases(
        "cases/actual-copy-on-drop-stock-diagnostic/aggregate.json",
        "actual-copy-on-drop-stock-diagnostic")

    owner_handoff_cases = raw_cases("cases/checked-current-owner-handoff/aggregate.json",
                                    "current-owner-handoff-resource-diagnostic")

    stock_owner_handoff_cases = raw_cases("cases/checked-current-owner-handoff-stock/aggregate.json",
                                          "current-owner-handoff-stock-diagnostic")

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

    artifacts_complete = (all(artifact_status.values()) and stages_complete and panic_ok and
                          runtime_ok and bounded_source_pin_ok)
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
        "bounded_source_pin": bounded_source_pin,
        "mandatory_artifacts_complete": artifacts_complete,
        "final_panic_origin_certificates": panic_candidates,
        "panic_certificate_required": panic_required,
        "panic_certificate_complete": panic_ok,
        "theorem_statuses": {
            "whole_small_sort_challenge": "NOT_PROVEN",
            "current_owner_permutation_diagnostics": permutation_cases,
            "current_owner_handoff_cases": owner_handoff_cases,
            "stock_current_owner_handoff_cases": stock_owner_handoff_cases,
            "g2_quartet_trace_cases": quartet_cases,
            "g2_modular_entry_control_cases": modular_entry_cases,
            "g2_modular_trace_cases": modular_trace_cases,
            "actual_bidirectional_len2_len3_cases": bidirectional_cases,
            "actual_merge_up_down_cases": actual_merge_cases,
            "source_pair_turnover_cases": pair_turnover_cases,
            "native_source_pair_turnover_cases": native_pair_cases,
            "stock_native_source_pair_turnover_cases": native_stock_pair_cases,
            "cleanup_recovery_hidden_type_cases": cleanup_hidden_cases,
            "actual_copy_on_drop_resource_cases": copy_on_drop_resource_cases,
            "actual_copy_on_drop_stock_cases": copy_on_drop_stock_cases,
        },
        "separate_semantic_component": {
            "mir_or_join_liveness": or_join_status,
        },
        "separate_runtime_candidate": runtime,
        "raw_group_status_path": "allprooflogs/group-status.txt",
        "raw_not_run_group_path": "allprooflogs/group-not-run.txt",
        "note": "Collector completion does not change per-case theorem classifications or establish a whole-function theorem.",
    }
    return audit_row


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checked_body_names(source: bytes) -> list[str]:
    function_pattern = re.compile(
        rb"(?m)^[ \t]*(?:pub\s+)?(?:unsafe\s+)?fn\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?:<[^\r\n{}]*>)?\s*\(")
    lemma_pattern = re.compile(rb"\blem\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?:<[^>{}]*>)?\s*\(")
    names = ([match.group(1).decode("ascii") for match in function_pattern.finditer(source)] +
             [match.group(1).decode("ascii") for match in lemma_pattern.finditer(source)])
    if not names or len(names) != len(set(names)):
        raise ValueError("bounded source pin has missing/duplicate checked body names")
    return names


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
