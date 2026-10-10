#!/usr/bin/env python3
"""Audit exact selected merge groups and their required evidence artifacts."""
from __future__ import annotations

import json
import hashlib
import importlib.util
from pathlib import Path
import re
import shutil
import sys
import tempfile

from selection import KNOWN_GROUPS, load

# Paths are relative to allprooflogs. Pointer proof harness groups must publish
# both an aggregate and the source admission it consumed. Other groups publish
# their retained runner's exact results, admission, or preparation output.
POINTER_GROUPS = {
    "current-owner-memory-cell-diagnostic": "checked-current-owner-memory-cell",
    "current-owner-memory-cell-stock-diagnostic": "checked-current-owner-memory-cell-stock",
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
    "guard-payload-own-diagnostic": {
        "directory": "guard-payload-own-diagnostic",
        "profile": "experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1",
    },
    "guard-payload-own-stock-diagnostic": {
        "directory": "guard-payload-own-stock-diagnostic",
        "profile": "stock-26.10",
    },
    "actual-copy-on-drop-resource-diagnostic": {
        "directory": "actual-copy-on-drop-resource-diagnostic",
        "profile": "experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1",
    },
    "actual-copy-on-drop-stock-diagnostic": {
        "directory": "actual-copy-on-drop-stock-diagnostic",
        "profile": "stock-26.10",
    },
}
GUARD_CONSTRUCTION_GROUPS = {
    "guard-construction-fragment-diagnostic": {
        "directory": "guard-construction-fragment-diagnostic",
        "profile": "experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1",
    },
    "guard-construction-fragment-stock-diagnostic": {
        "directory": "guard-construction-fragment-stock-diagnostic",
        "profile": "stock-26.10",
    },
}
GUARD_CONSTRUCTION_V3_GROUPS = {
    "guard-construction-nonprecise-v3-diagnostic": {
        "directory": "guard-construction-nonprecise-v3-diagnostic",
        "profile": "experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1",
    },
    "guard-construction-nonprecise-v3-stock-diagnostic": {
        "directory": "guard-construction-nonprecise-v3-stock-diagnostic",
        "profile": "stock-26.10",
    },
}
GUARD_CONSTRUCTION_V4_GROUPS = {
    "guard-construction-fbc-v4-diagnostic": {
        "directory": "guard-construction-fbc-v4-diagnostic",
        "profile": "experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1",
    },
    "guard-construction-fbc-v4-stock-diagnostic": {
        "directory": "guard-construction-fbc-v4-stock-diagnostic",
        "profile": "stock-26.10",
    },
}
GUARD_CONSTRUCTION_V4_PROFILE = "copy-on-drop-source-construction-canonical-fbc-fragment-v4"
GUARD_CONSTRUCTION_V4_ROUNDTRIP_SHA256 = hashlib.sha256(
    b"        //@ close <CopyOnDrop<T>>.own(t, drop_guard);\n"
    b"        //@ close CopyOnDrop_full_borrow_content::<T>(t, &drop_guard)();\n"
    b"        //@ open CopyOnDrop_full_borrow_content::<T>(t, &drop_guard)();\n"
    b"        //@ open <CopyOnDrop<T>>.own(t, drop_guard);\n"
    b"        //@ assert scratch_base[..len] |-> ?current_src_values &*& v_base[..len] |-> _ &*& foreach(current_src_values, own::<T>(t));\n"
    b"        //@ close <CopyOnDrop<T>>.own(t, drop_guard);\n").hexdigest()
GUARD_GEOMETRY_GROUPS = {
    "guard-drop-geometry-v3-diagnostic": "experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1",
    "guard-drop-geometry-v3-stock-diagnostic": "stock-26.10",
}
GUARD_GEOMETRY_CASES = ("positive", "prototype_false", "first_body_false")
ONECELL_GROUP = "insertion-onecell-guard-diagnostic"
ONECELL_PROFILE = "experimental-merge-origin-layout-concrete-u64-v1"
ONECELL_DIAGNOSTIC = "insert-tail-onecell-mutable-fbc-held-recovery-v1"
ONECELL_CASES = ("positive", "after_fbc_false", "after_recovery_false", "missing_held_owner",
                 "double_physical_fbc")
ONECELL_CAMPAIGN = "incoming-origin-controls-only-v1"
ONECELL_CAMPAIGN_CASES = set()
ONECELL_CAMPAIGN_MD_SOURCE_SHA256 = "047d5f3245c0e81fe718899e11b611b1da9d7aa21b3c6e18347a5b95c923197e"
LAYOUT_CONTROL_CASES = (
    "unit_ghost_size", "unit_ghost_alignment", "unit_runtime_size",
    "unit_runtime_alignment", "unit_wrapper_runtime_size", "scalar_wrapper_runtime_size",
    "unit_positive_extent_false", "unit_wrong_alignment_false",
    "unit_generic_instantiation", "scalar_generic_instantiation",
    "unknown_struct_no_positivity", "unit_pointer_zero_step",
    "unit_pointer_unequal_false", "unit_local_storage",
)
CONCRETE_U64_CASES = (
    "positive", "after_fbc_false", "after_recovery_false",
    "missing_held_owner", "double_physical_fbc",
)
NATIVE_UNIT_SMOKES = (
    ("c", "unit_name_c_smoke"),
    ("cpp", "unit_name_cpp_smoke()"),
)
ONECELL_CAMPAIGN_BASELINE = {
    "build_id": "d1bfa119-b1d4-4667-8c2b-21d37b215aef",
    "proof_sha": "633c0c09cda0f4c40c6664722209f2a9d5792b4b",
    "profile_sha256": "11ccd16ec9df56e7165cf75b1800d48b367c3b65f20c9ea8656fc2b7779bed90",
    "results_sha256": "937e9050fb0d5b111c015785ba818b4dd3fa94cf756aaee73f65701d8cad36b2",
}
ONECELL_MD_CASES = ("positive_manually_drop_after_merge",
                    "negative_missing_precreated_reference",
                    "negative_missing_reference_initialization",
                    "negative_read_without_permission")
GUARD_CONSTRUCTION_V3_PROFILE = "copy-on-drop-source-construction-full-source-nonprecise-current-fragment-v3b"
GUARD_CONSTRUCTION_V3_ROUNDTRIP_SHA256 = hashlib.sha256(
    b"        //@ close <CopyOnDrop<T>>.own(t, drop_guard);\n"
    b"        //@ open <CopyOnDrop<T>>.own(t, drop_guard);\n"
    b"        //@ assert scratch_base[..len] |-> ?current_src_values &*& v_base[..len] |-> _ &*& foreach(current_src_values, own::<T>(t));\n"
    b"        //@ close <CopyOnDrop<T>>.own(t, drop_guard);\n").hexdigest()
GUARD_CONSTRUCTION_CASES = ("positive", "first_body_false")
GUARD_CONSTRUCTION_STAGES = ("exporter", "decode", "verifast", "refinement")
GUARD_CONSTRUCTION_LINE_SHA256 = "d897a2aa7abcb8d87502dc83a048aba909641931a08fa8102ab77b5252414fdb"
DROP_CASES = ("positive", "first_body_false")
DROP_STAGES = ("exporter", "decode", "verifast", "refinement")
DROP_SOURCE_SHA256 = "85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1"
DROP_SOURCE_BLOB = "40939f922bcb6fdc7ee0d30427fa861827043827"
DROP_BLOCK_SHA256 = "caff1edbfa3a8d9fd29459e49c43abd0f8f987f9061c75e7bf6ecedbbba26a6a"
GUARD_CONSTRUCTION_SOURCE_SHA256 = DROP_SOURCE_SHA256
GUARD_CONSTRUCTION_SOURCE_BLOB = DROP_SOURCE_BLOB
GUARD_CONSTRUCTION_BLOCK_SHA256 = DROP_BLOCK_SHA256
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
    *[f"cases/{OR_JOIN_GROUP}/{name}{suffix}" for name in
      ("calibrated-real-dead", "uncalibrated-liveness-controls",
       "actual-bounded", "admission-controls", "six-comparison")
      for suffix in ("-exit-code.txt", ".log", "-resources.txt")],
    *[f"cases/{OR_JOIN_GROUP}/{name}-exit-code.txt" for name in
      ("calibrated-real-dead", "uncalibrated-liveness-controls", "actual-bounded",
       "admission-controls", "six-comparison")],
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


SPAN_CONTROL_NAMES = {
    "span_positive",
    "span_retired_local_reuse",
    "span_overlap",
    "span_raw_arbitrary",
    "span_lost_incoming_authority",
    "span_zero_extent",
}


def onecell_negative_site_matches(name: str, source: str, error: str,
                                  expected_lines: set[int]) -> bool:
    location = re.search(r"verified/lib\.rs\((\d+),", error)
    if location is None:
        return False
    line = int(location.group(1))
    if line in expected_lines:
        return True
    lines = source.splitlines()
    if name == "missing_held_owner":
        sites = [i + 1 for i, text in enumerate(lines)
                 if text.strip() == "<T>.own(t, current);"]
        return (sites == [line] and
                "No matching heap chunks: own(T_typeid)" in error)
    if name == "double_physical_fbc":
        starts = [i for i, text in enumerate(lines)
                  if text == "struct CopyOnDrop<T> {"]
        if len(starts) != 1:
            return False
        start = starts[0]
        fields = ("    src: *const T,", "    dst: *mut T,", "    len: usize,")
        if tuple(lines[start + 1:start + 4]) != fields:
            return False
        for offset, field in enumerate(("src", "dst", "len"), 2):
            if line == start + offset:
                return f"No matching heap chunks: CopyOnDrop_{field}<T>(" in error
    return False


def audit_origin_controls(base: Path, aggregate: dict, profile: str) -> tuple[bool, dict]:
    controls_dir = Path(__file__).resolve().parents[2] / "cloud-build/incoming-origin/controls"
    summary = json.loads((base / "origin-results.json").read_text())
    runner_spec = importlib.util.spec_from_file_location("origin_audit_classifier", controls_dir / "run.py")
    runner = importlib.util.module_from_spec(runner_spec)
    runner_spec.loader.exec_module(runner)
    valid = (summary == aggregate.get("origin_controls") and summary.get("profile") == profile and
             summary.get("accepted") is False and
             summary.get("manifest_sha256") == sha256_file(controls_dir / "MANIFEST.json") and
             summary.get("source_file_sha256") == sha256_file(controls_dir / "origin-controls.rs"))
    with tempfile.TemporaryDirectory(prefix="merge-origin-audit-") as temporary:
        _, metadata = runner.prepare(Path(temporary) / "controls")
        valid = valid and set(summary.get("controls", {})) == set(metadata) == set(summary.get("case_details", {}))
        for name, meta in metadata.items():
            case = base / "controls" / name
            row = json.loads((case / "classification.json").read_text())
            valid = (valid and row == summary["case_details"][name] and
                     row.get("source_sha256") == meta["source_sha256"] == sha256_file(case / "verified/lib.rs") ==
                     sha256_file(case / "original/lib.rs") and row.get("source_unchanged_at_every_stage") is True and
                     row.get("source_before") == row.get("source_after") and
                     row["source_before"].get("verified/lib.rs") == meta["source_sha256"] and
                     row["source_before"].get("original/lib.rs") == meta["source_sha256"])
            for stage, code in row.get("stages", {}).items():
                stage_data = json.loads((case / (stage + "-stage.json")).read_text())
                valid = valid and stage_data.get("exit_code") == code == int((case / (stage + "-exit-code.txt")).read_text())
            replay = Path(temporary) / "controls" / name
            for filename in ("original/lib.rs", "verified/lib.rs",
                             "origin-control.rsspec", "original/origin-control.rsspec",
                             "verified/origin-control.rsspec"):
                source = case / filename
                if source.is_file():
                    destination = replay / filename
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes(source.read_bytes())
            for filename in ("verifast.log", "decode.out", "proof-ast.ml",
                             "verifast-stage.json"):
                source = case / filename
                if source.is_file():
                    (replay / filename).write_bytes(source.read_bytes())
            classified = runner.classify(name, replay, meta, row)
            # JSON object keys are strings on disk; the live classifier can
            # return integer CFG-region keys. Compare the exact persisted shape.
            replay_row = json.loads(json.dumps(classified))
            valid = valid and replay_row == row and summary["controls"][name] == row.get("classification")
    return bool(valid), summary


def _audit_four_stage_case(case: Path, row: dict) -> bool:
    """Bind each nested diagnostic's four stage receipts to its row."""
    stages = row.get("stages")
    before, after = row.get("source_before"), row.get("source_after")
    if (not isinstance(stages, dict) or set(stages) !=
            {"exporter", "decode", "verifast", "refinement"} or
            row.get("source_unchanged_at_every_stage") is not True or
            not isinstance(before, dict) or before != after):
        return False
    for relative in ("original/lib.rs", "verified/lib.rs"):
        try:
            source_hash = sha256_file(case / relative)
        except OSError:
            return False
        if before.get(relative) != source_hash or after.get(relative) != source_hash:
            return False
    for stage, code in stages.items():
        if not isinstance(code, int) or isinstance(code, bool):
            return False
        try:
            receipt = json.loads((case / f"{stage}-stage.json").read_text())
            exit_code = int((case / f"{stage}-exit-code.txt").read_text().strip())
        except (OSError, ValueError, TypeError):
            return False
        if receipt.get("stage") != stage or receipt.get("exit_code") != code or exit_code != code:
            return False
        if receipt.get("status") == "NOT_RUN":
            if code != 125 or not isinstance(receipt.get("reason"), str) or not receipt["reason"]:
                return False
            continue
        if (receipt.get("source_before") != before or receipt.get("source_after") != after or
                receipt.get("source_unchanged") is not True):
            return False
    return True


def audit_combined_candidate_gates(base: Path, aggregate: dict,
                                  environment: dict, proof_sha: str,
                                  build_id: str, tracked_build: Path) -> dict:
    """Bind and replay the gates added to the combined one-cell candidate.

    Old artifacts have neither field and remain on the legacy path. Presence
    opts into strict validation; an absent conditional body run is represented
    as NOT_RUN and never as a pass.
    """
    result = {"applicable": False, "combined_profile_smoke": "NOT_RUN",
              "concrete_drop_body": "NOT_RUN", "artifact_bindings_valid": True}
    smoke_path = base / "combined-profile-smoke.json"
    drop_summary = aggregate.get("concrete_drop_body_diagnostic")
    drop_root = base / "concrete-drop-body"
    has_drop = drop_root.exists() or drop_summary is not None
    if not smoke_path.exists() and not has_drop:
        return result
    result["applicable"] = True
    valid = True
    if smoke_path.exists() and drop_summary is None:
        valid = False
        result["concrete_drop_body"] = "INCONCLUSIVE"
        result["concrete_drop_body_error"] = "new combined-candidate artifacts omit conditional Drop status"
    try:
        if not smoke_path.is_file():
            raise ValueError("combined-candidate smoke receipt missing")
        receipt = json.loads(smoke_path.read_text())
        smoke_root = base / "combined-profile-smoke"
        combined = json.loads((smoke_root / "aggregate.json").read_text())
        results = json.loads((smoke_root / "results.json").read_text())
        admission_path = smoke_root / "full-small-sort-source-admission.json"
        admission = json.loads(admission_path.read_text())
        fixture = json.loads((smoke_root / "fixture-manifest.json").read_text())
        expected_profile = environment.get("profile")
        expected_results_profile = (
            expected_profile + "; base26.10-f76012fb518703b1d98e243ac4f487f16877cfcb; "
            "compiler-nightly-2026-09-25")
        valid = (receipt.get("profile") == expected_profile and
                 receipt.get("proof_sha") == proof_sha == environment.get("proof_sha") and
                 receipt.get("provider") == environment.get("provider") and
                 receipt.get("provider", {}).get("build_id") == build_id and
                 receipt.get("tool_sha256") == environment.get("tool_sha256") and
                 receipt.get("schema_sha256") == environment.get("schema_sha256") and
                 receipt.get("rustc_version") == environment.get("rustc_version") and
                 receipt.get("rustc_toolchain") == environment.get("rustc_toolchain") and
                 receipt.get("accepted") is False and receipt.get("exit_code") == 0 and
                 results.get("profile") == expected_results_profile and
                 results.get("source_admission_sha256") == sha256_file(admission_path) and
                 admission.get("source_git_commit") == "cd371e035c7e573760c43bf934d53e8118ee3e7d" and
                 admission.get("full_source_sha256") == DROP_SOURCE_SHA256 and
                 combined.get("evidence_collection_completed") is True and
                 combined.get("classifier_controls_passed") is True and
                 combined.get("cases") == {"ordinary_call_normal_unwind": "PASS"} and
                 fixture.get("cases", {}).get("ordinary_call_normal_unwind") is not None and
                 results.get("cases", {}).get("ordinary_call_normal_unwind", {}).get("classification") == "PASS")
        case_name = "ordinary_call_normal_unwind"
        case_root = smoke_root / "cases" / case_name
        metadata = json.loads((case_root / "metadata.json").read_text())
        row = json.loads((case_root / "classification.json").read_text())
        stored = results["cases"][case_name]
        pointer_path = Path(__file__).resolve().parents[1] / "overnight/pointer-prove.py"
        spec = importlib.util.spec_from_file_location("combined_candidate_pointer_classifier", pointer_path)
        pointer = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = pointer
        spec.loader.exec_module(pointer)
        source_before = row.get("source_before", {})
        source_after = row.get("source_after", {})
        unchanged = (row.get("source_unchanged_at_every_stage") is True and
                     source_before == source_after and
                     source_before.get("original/lib.rs") == sha256_file(case_root / "original/lib.rs") == metadata.get("original_sha256") and
                     source_before.get("verified/lib.rs") == sha256_file(case_root / "verified/lib.rs") == metadata.get("verified_sha256"))
        stages = row.get("stages", {})
        valid = valid and row == stored and metadata.get("case") == case_name and unchanged
        valid = (valid and fixture.get("case_order") == [case_name] and
                 fixture.get("cases", {}).get(case_name) == metadata and
                 fixture.get("fixture_sha256") == pointer.sha(
                     (Path(__file__).resolve().parents[1] / "overnight/baseline-cases.rs").read_bytes()) and
                 json.loads((case_root / "source-before-sha256.json").read_text()) == source_before and
                 json.loads((case_root / "source-after-sha256.json").read_text()) == source_after)
        if set(stages) != {"exporter", "decode", "verifast", "refinement"}:
            valid = False
        for stage, code in stages.items():
            stage_receipt = json.loads((case_root / f"source-integrity-{stage}.json").read_text())
            valid = (valid and int((case_root / f"{stage}-exit-code.txt").read_text()) == code and
                     stage_receipt.get("stage") == stage and
                     stage_receipt.get("exit_code") == code and
                     stage_receipt.get("source_before") == source_before and
                     stage_receipt.get("source_after") == source_after and
                     stage_receipt.get("unchanged") is True)
        log = (case_root / "verifast.log").read_text(errors="replace")
        replay = pointer.classify(case_name, metadata, stages, log, unchanged)
        derived = ("classification", "stages", "expected_bodies", "visited_bodies",
                   "body_execution_records", "per_body_records", "return_records",
                   "leak_check_records", "error_lines", "dead_code_records",
                   "full_positive_gate", "classifier_fail_closed_mutations")
        valid = (valid and all(replay.get(key) == row.get(key) for key in derived) and
                 all(replay.get("classifier_fail_closed_mutations", {}).values()))
        result["combined_profile_smoke"] = "REPLAYED_PASS" if valid else "INCONCLUSIVE"
    except (OSError, ValueError, KeyError, TypeError, AttributeError, ImportError) as error:
        valid = False
        result["combined_profile_smoke"] = "INCONCLUSIVE"
        result["combined_profile_smoke_error"] = str(error)

    if has_drop:
        try:
            if not isinstance(drop_summary, dict):
                raise ValueError("conditional concrete Drop summary missing")
            if drop_summary.get("classification") == "NOT_RUN":
                drop_valid = (not drop_root.exists() and
                              drop_summary.get("accepted") is False and
                              drop_summary.get("actual_callee_or_glue_credit") is False)
                result["concrete_drop_body"] = "NOT_RUN" if drop_valid else "INCONCLUSIVE"
            else:
                # The nested classifier consumes only the retained sources,
                # decoded MIR, AST and verifier logs; it does not extract or
                # invoke any toolchain.
                module_path = Path(__file__).resolve().parents[2] / "cloud-build/origin-layout/concrete-drop-body.py"
                spec = importlib.util.spec_from_file_location("outer_concrete_drop_body_audit", module_path)
                body = importlib.util.module_from_spec(spec)
                sys.modules[spec.name] = body
                spec.loader.exec_module(body)
                prep_path = Path(__file__).resolve().parents[1] / "overnight/copy-on-drop-prepare.py"
                prep_spec = importlib.util.spec_from_file_location("outer_drop_source_pins", prep_path)
                source_pin = importlib.util.module_from_spec(prep_spec)
                sys.modules[prep_spec.name] = source_pin
                prep_spec.loader.exec_module(source_pin)
                own_module_path = Path(__file__).resolve().parents[1] / "overnight/guard-ownership/insertion-onecell/prepare.py"
                own_module_spec = importlib.util.spec_from_file_location("outer_drop_own_pins", own_module_path)
                own_module = importlib.util.module_from_spec(own_module_spec)
                sys.modules[own_module_spec.name] = own_module
                own_module_spec.loader.exec_module(own_module)
                extraction = json.loads((drop_root / "extraction.json").read_text())
                if set(extraction.get("cases", {})) != set(body.CASES):
                    raise ValueError("conditional Drop evidence omits a required current case")
                generic_block = extraction.get("generic_source_block", "").encode("ascii")
                if (len(generic_block) != source_pin.BLOCK_BYTES or
                        body._sha(generic_block) != source_pin.BLOCK_SHA256 or
                        generic_block.count(source_pin.DROP_SIGNATURE) != 1 or
                        generic_block.count(source_pin.COPY_CALL) != 1 or
                        extraction.get("source_sha256") != source_pin.SOURCE_SHA256):
                    raise ValueError("retained generic source block does not match pinned source identity")
                original_source = body._specialize(source_pin.CRATE_PREFIX + generic_block)
                contract = body._specialize(source_pin.CONTRACT)
                own = body._specialize(own_module.OWN).replace(
                    b"[?f](*v.src |-> ?current)", b"[1/4](*v.src |-> ?current)")
                receipt = json.loads((drop_root / "receipt.json").read_text())
                consumer_path = module_path.with_name("concrete-consumer.py")
                consumer_spec = importlib.util.spec_from_file_location(
                    "outer_concrete_drop_consumer_audit", consumer_path)
                consumer = importlib.util.module_from_spec(consumer_spec)
                sys.modules[consumer_spec.name] = consumer
                consumer_spec.loader.exec_module(consumer)
                proof_path = Path(__file__).resolve().parents[1] / "overnight/copy-on-drop-prove.py"
                proof_spec = importlib.util.spec_from_file_location("outer_concrete_drop_proof_audit", proof_path)
                proof = importlib.util.module_from_spec(proof_spec)
                sys.modules[proof_spec.name] = proof
                proof_spec.loader.exec_module(proof)
                profile_build = json.loads((tracked_build / "profile-build.json").read_text())
                body_aggregate = json.loads((drop_root / "aggregate.json").read_text())
                expected_tools = {"receipt": environment,
                                  "receipt_sha256": consumer._sha(json.dumps(
                                      environment, sort_keys=True, separators=(",", ":")).encode()),
                                  "profile_evidence": environment.get("profile_evidence"),
                                  "actual_tool_sha256": environment.get("tool_sha256"),
                                  "schema_sha256": environment.get("schema_sha256"),
                                  "profile_build_sha256": sha256_file(
                                      tracked_build / "profile-build.json")}
                drop_valid = (drop_summary.get("accepted") is False and
                              drop_summary.get("actual_callee_or_glue_credit") is False and
                              drop_summary.get("profile") == "SOURCE_LINKED_U64_BODY_DIAGNOSTIC" and
                              drop_summary == body_aggregate and
                              drop_summary.get("tool_profile") == environment.get("profile") and
                              set(drop_summary.get("cases", {})) == set(body.CASES) and
                              drop_summary.get("receipt_sha256") == receipt.get("receipt_sha256") and
                              receipt.get("receipt") == environment and
                              receipt.get("receipt_sha256") == expected_tools["receipt_sha256"] and
                              drop_summary.get("cases") == aggregate.get("concrete_drop_body_diagnostic", {}).get("cases") and
                              extraction.get("accepted") is False and
                              extraction.get("profile") == "SOURCE_LINKED_U64_BODY_DIAGNOSTIC" and
                              set(extraction.get("cases", {})) == set(body.CASES) and
                              extraction.get("source_sha256") == source_pin.SOURCE_SHA256 and
                              extraction.get("source_block_sha256") == source_pin.BLOCK_SHA256 and
                              extraction.get("generic_contract_sha256") == body._sha(source_pin.CONTRACT) and
                              extraction.get("concrete_contract_sha256") == body._sha(contract) and
                              extraction.get("concrete_original_sha256") == body._sha(original_source) and
                              profile_build.get("proof_sha") == proof_sha and
                              profile_build.get("provider", {}).get("build_id") == build_id and
                              profile_build.get("provider") == environment.get("provider") and
                              profile_build.get("profile") == environment.get("profile") and
                              profile_build.get("build_exit") == 0 and
                              profile_build.get("schema_sha256") in
                                  (None, environment.get("schema_sha256")) and
                              profile_build.get("accepted") is False and
                              receipt.get("profile_build_sha256") == expected_tools["profile_build_sha256"] and
                              receipt.get("actual_tool_sha256") == expected_tools["actual_tool_sha256"] and
                              receipt.get("schema_sha256") == expected_tools["schema_sha256"] and
                              receipt.get("rustc_version") == environment.get("rustc_version") and
                              receipt.get("rustc_toolchain") == environment.get("rustc_toolchain"))
                contract_header = contract.split(b"safety_proof {\n", 1)[0]
                proof_open = body._specialize(
                    b"    open CopyOnDrop_full_borrow_content::<T>(_t, self)();\n"
                    b"    open <CopyOnDrop<T>>.own(_t, *self);\n")
                source_copy = body._specialize(source_pin.COPY_CALL)
                for name in body.CASES:
                    case = drop_root / "cases" / name
                    meta = extraction.get("cases", {}).get(name)
                    row = json.loads((case / "classification.json").read_text())
                    original = case / "original/lib.rs"
                    verified = case / "verified/lib.rs"
                    execution = row.get("parent_execution", {})
                    before = consumer._hashes(case)
                    stage_gate = consumer._stage_receipts(case, execution.get("stages", {}), before)
                    recorded_stage_gate = execution.get("stage_receipt_gate")
                    unchanged = (execution.get("source_unchanged_at_every_stage") is True and
                                 row.get("source_gate", {}).get("runtime_equal_after_ghost_strip") is True)
                    drop_valid = drop_valid and recorded_stage_gate == stage_gate and unchanged
                    execution["stage_receipt_gate"] = stage_gate
                    canonical = name not in {"direct_positive", "direct_first_body_false"}
                    case_contract = contract
                    expected_ghost = []
                    if canonical:
                        inserted = (body.PROTOTYPE_FALSE if name == "prototype_false" else b"")
                        if name == "canonical_dst_pre":
                            inserted += body.FIELD_BIND + body.LEN_ONE + body.DST_PRE + body.CALL
                        elif name == "canonical_dst_shape_probe":
                            inserted += (body.FIELD_BIND + body.LEN_ONE +
                                         body.DST_SHAPE_ROUNDTRIP + body.DST_PRE + body.CALL)
                        else:
                            inserted += body.ROOT_LIMITS
                            if name == "canonical_alignment_probe":
                                inserted += body.ALIGNMENT_ROUNDTRIP
                            inserted += body.FIELD_BIND + b"".join(body._geometry()) + \
                                body.LEN_ONE + body.DST_PRE + body.CALL
                        case_contract = contract.replace(proof_open, proof_open + inserted, 1)
                        expected_ghost.extend([own, case_contract])
                    else:
                        case_contract = contract.replace(proof_open, proof_open + body.CALL, 1)
                        expected_ghost.append(case_contract)
                    if name in {"first_body_false", "direct_first_body_false"}:
                        expected_ghost.append(body.BODY_FALSE)
                    verified_bytes = verified.read_bytes()
                    expected_lines = {
                        "source_copy_line": body._line(verified_bytes, source_copy),
                        "fbc_open_line": body._line(verified_bytes, body._specialize(
                            b"    open CopyOnDrop_full_borrow_content::<T>(_t, self)();\n")),
                        "own_open_line": body._line(verified_bytes, body._specialize(
                            b"    open <CopyOnDrop<T>>.own(_t, *self);\n")),
                        "call_line": body._line(verified_bytes, body.CALL),
                        "body_false_line": body._line(verified_bytes, body.BODY_FALSE)
                            if name in {"first_body_false", "direct_first_body_false"} else None,
                        "prototype_false_line": body._line(verified_bytes, body.PROTOTYPE_FALSE)
                            if name == "prototype_false" else None,
                    }
                    if canonical:
                        expected_lines.update({
                            "field_bind_line": body._line(verified_bytes, body.FIELD_BIND),
                            "layout_lines": ({label: body._line(verified_bytes, item)
                                              for label, item in zip(body.GEOMETRY_LABELS,
                                                                     body._geometry())}
                                             if name not in {"canonical_dst_pre",
                                                             "canonical_dst_shape_probe"} else {}),
                            "dst_pre_line": body._line(verified_bytes, body.DST_PRE),
                        })
                        if name == "canonical_alignment_probe":
                            expected_lines["alignment_probe_lines"] = {
                                label: body._line(verified_bytes, item)
                                for label, item in zip(
                                    ("open_aggregate", "to_u8s", "from_u8s", "close_aggregate"),
                                    body.ALIGNMENT_ROUNDTRIP.splitlines(keepends=True))}
                        if name == "canonical_dst_shape_probe":
                            expected_lines["dst_shape_probe_lines"] = {
                                label: body._line(verified_bytes, item)
                                for label, item in zip(
                                    ("singleton_limits", "endpoint", "empty_tail", "singleton_array"),
                                    body.DST_SHAPE_ROUNDTRIP.splitlines(keepends=True))}
                    else:
                        expected_lines.update({"field_bind_line": None,
                                               "layout_lines": {}, "dst_pre_line": None})
                    replay = body._classify(name, case, meta, execution,
                                             contract_header, proof, consumer)
                    drop_valid = (drop_valid and meta is not None and
                                  meta.get("case") == name and
                                  meta.get("canonical") is canonical and
                                  meta.get("ghost_fragments") == [part.decode("ascii")
                                                                   for part in expected_ghost] and
                                  meta.get("original_sha256") == body._sha(original_source) and
                                  all(meta.get(field) == value
                                      for field, value in expected_lines.items()) and
                                  meta.get("contract_header_sha256") == body._sha(contract_header) and
                                  meta.get("contract_sha256") == body._sha(
                                      meta["ghost_fragments"][1 if meta["canonical"] else 0].encode()) and
                                  before.get("original/lib.rs") == meta.get("original_sha256") == sha256_file(original) and
                                  before.get("verified/lib.rs") == meta.get("verified_sha256") == sha256_file(verified) and
                                  body._source_gate(case, meta, contract_header).get("admitted") is True and
                                  replay == row)
                result["concrete_drop_body"] = "REPLAYED_DIAGNOSTIC" if drop_valid else "INCONCLUSIVE"
                valid = valid and drop_valid
        except (OSError, ValueError, KeyError, TypeError, AttributeError, ImportError, IndexError) as error:
            valid = False
            result["concrete_drop_body"] = "INCONCLUSIVE"
            result["concrete_drop_body_error"] = str(error)
    result["artifact_bindings_valid"] = valid
    return result


def audit_onecell_nested_controls(base: Path, aggregate: dict,
                                  tracked_build: Path) -> dict:
    """Replay unit-layout and concrete-u64 classifiers from retained artifacts.

    Semantic classifications are reported as observations; this audit checks
    source/helper reproducibility and artifact bindings without upgrading the
    profile or requiring the expected proof outcomes to pass.
    """
    report = {"artifact_bindings_valid": False, "accepted": False,
              "layout_controls": "INCONCLUSIVE",
              "concrete_u64_consumer": "INCONCLUSIVE",
              "native_unit_smokes": {"c": "INCONCLUSIVE", "cpp": "INCONCLUSIVE"}}
    try:
        layout_path = Path(__file__).resolve().parents[2] / "cloud-build/origin-layout/layout-controls.py"
        consumer_path = Path(__file__).resolve().parents[2] / "cloud-build/origin-layout/concrete-consumer.py"
        spec = importlib.util.spec_from_file_location("onecell_layout_audit", layout_path)
        layout = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(layout)
        spec = importlib.util.spec_from_file_location("onecell_concrete_audit", consumer_path)
        consumer = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = consumer
        spec.loader.exec_module(consumer)

        valid = aggregate.get("accepted") is False
        layout_root = base / "layout-controls"
        layout_summary = json.loads((layout_root / "summary.json").read_text())
        valid = valid and layout_summary == aggregate.get("layout_controls")
        with tempfile.TemporaryDirectory(prefix="onecell-layout-audit-") as temporary:
            metadata = layout.prepare(Path(temporary) / "prepared")
            valid = valid and set(metadata) == set(LAYOUT_CONTROL_CASES) == set(layout_summary.get("cases", {}))
            for name, meta in metadata.items():
                case = layout_root / name
                row = json.loads((case / "classification.json").read_text())
                valid = valid and row == layout_summary["cases"].get(name)
                source_hashes = {}
                for tree in ("original", "verified"):
                    source_hashes[f"{tree}/lib.rs"] = sha256_file(case / f"{tree}/lib.rs")
                    valid = valid and source_hashes[f"{tree}/lib.rs"] == meta["source_sha256"]
                before = row.get("source_before", {})
                after = row.get("source_after", {})
                valid = (valid and before.get("original/lib.rs") == meta["source_sha256"] and
                         before.get("verified/lib.rs") == meta["source_sha256"] and
                         after.get("original/lib.rs") == meta["source_sha256"] and
                         after.get("verified/lib.rs") == meta["source_sha256"] and
                         before.get("small_sort_source") == DROP_SOURCE_SHA256 and
                         after.get("small_sort_source") == DROP_SOURCE_SHA256)
                execution = {key: row[key] for key in
                             ("stages", "source_unchanged_at_every_stage", "source_before", "source_after")
                             if key in row}
                replay = Path(temporary) / "replay" / name
                (replay / "original").mkdir(parents=True)
                (replay / "verified").mkdir()
                for filename in ("original/lib.rs", "verified/lib.rs", "verifast.log"):
                    shutil.copyfile(case / filename, replay / filename)
                classified = layout.classify(replay, meta, execution)
                valid = valid and classified == row and _audit_four_stage_case(case, row)
        report["layout_controls"] = ("REPLAYED_DIAGNOSTIC" if valid else "INCONCLUSIVE")

        concrete_root = base / "concrete-u64"
        concrete_summary = json.loads((concrete_root / "concrete-u64-results.json").read_text())
        concrete_metadata = json.loads((concrete_root / "metadata.json").read_text())
        environment = json.loads((base / "environment.json").read_text())
        profile_build = json.loads((tracked_build / "profile-build.json").read_text())
        valid = valid and concrete_summary == aggregate.get("concrete_u64_consumer")
        valid = valid and concrete_summary.get("schema") == "concrete-u64-onecell-consumer-v1" and \
                concrete_summary.get("accepted") is False and \
                set(concrete_summary.get("case_details", {})) == \
                set(concrete_metadata) == set(CONCRETE_U64_CASES)
        receipt = concrete_summary.get("validated_receipt")
        receipt_digest = (hashlib.sha256(json.dumps(
            receipt, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            if isinstance(receipt, dict) else None)
        provider = concrete_summary.get("provider")
        build_provider = profile_build.get("provider")
        build_id = (provider.get("build_id") if isinstance(provider, dict) else None)
        valid = (valid and receipt == environment and
                 concrete_summary.get("validated_receipt_sha256") == receipt_digest and
                 concrete_summary.get("profile") == aggregate.get("profile") ==
                 environment.get("profile") == concrete_summary.get("helper_profile") and
                 concrete_summary.get("accepted") is False and
                 concrete_summary.get("proof_sha") == environment.get("proof_sha") ==
                 profile_build.get("proof_sha") and
                 provider == environment.get("provider") == build_provider and
                 isinstance(build_id, str) and build_id and
                 environment.get("cloud_build_id") == build_id and
                 profile_build.get("provider", {}).get("build_id") == build_id and
                 profile_build.get("profile") == concrete_summary.get("profile") and
                 profile_build.get("accepted") is False)
        # Import only static helpers/constants. The extraction and proof entry
        # points are deliberately never called by this audit.
        old = consumer._load("onecell_concrete_prepare_audit", consumer.OLD / "prepare.py")
        stage_proof = consumer._load("onecell_concrete_stage_helpers_audit",
                                     consumer.OLD.parents[1] / "copy-on-drop-prove.py")
        with tempfile.TemporaryDirectory(prefix="onecell-concrete-audit-") as temporary:
            for name in CONCRETE_U64_CASES:
                case = concrete_root / "cases" / name
                row = json.loads((case / "classification.json").read_text())
                valid = valid and row == concrete_summary["case_details"].get(name)
                meta = concrete_metadata[name]
                original = (case / "original/lib.rs").read_bytes()
                verified = (case / "verified/lib.rs").read_bytes()
                expected_ghosts = [consumer._rewrite_types(part).decode("ascii")
                                   for part in consumer._ghost_fragments(old, name)]
                valid = valid and meta.get("case") == name and \
                    meta.get("original_sha256") == consumer._sha(original) and \
                    meta.get("verified_sha256") == consumer._sha(verified) and \
                    meta.get("ghost_fragments") == expected_ghosts and \
                    meta.get("runtime_ghost_strip_equal") is True and \
                    consumer._ghost_strip_equal(original, verified, old, name)
                # Independently bind the persisted per-case metadata to the
                # pinned source anchors and classifier helper constants.
                anchor_fields = {
                    "read_line": old.READ, "guard_line": old.GUARD, "copy_line": old.COPY,
                    "fbc_close_line": old.FBC_CLOSE, "fbc_open_line": old.FBC_OPEN,
                    "source_limits_line": old.SOURCE_LIMITS,
                    "alignment_lemma_line": old.ALIGNMENT,
                    "source_identity_line": old.SOURCE_IDENTITY,
                    "constructor_span_line": old.CONSTRUCTOR_SPAN,
                    "own_close_line": (old.MISSING_OWNER_CLOSE if name == "missing_held_owner"
                                       else old.OWN_CLOSE),
                }
                for field, anchor in anchor_fields.items():
                    valid = valid and meta.get(field) == consumer._line(
                        verified, consumer._rewrite_types(anchor))
                valid = valid and meta.get("geometry_lines") == [
                    consumer._line(verified, consumer._rewrite_types(anchor))
                    for anchor in old.GEOMETRY]
                target_anchor = (old.FBC_FALSE if name == "after_fbc_false" else
                                 old.FALSE if name == "after_recovery_false" else
                                 old.READ if name == "missing_held_owner" else
                                 old.DOUBLE_FBC_CLOSE if name == "double_physical_fbc" else None)
                expected_target = None if target_anchor is None else {
                    "line": consumer._line(verified, consumer._rewrite_types(target_anchor)),
                    "column_start": target_anchor.index(
                        b"false" if target_anchor in (old.FALSE, old.FBC_FALSE) else
                        b"tail.read" if target_anchor == old.READ else b"close") + 1,
                    "predicate": "false" if target_anchor in (old.FALSE, old.FBC_FALSE) else
                    "held owner" if target_anchor == old.READ else "physical FBC"}
                valid = valid and meta.get("target") == expected_target
                execution = {key: row[key] for key in
                             ("stages", "source_unchanged_at_every_stage", "source_before",
                              "source_after", "stage_receipt_gate")
                             if key in row}
                stage_gate = consumer._stage_receipts(case, execution.get("stages", {}),
                                                       execution.get("source_before", {}))
                valid = valid and execution.get("stage_receipt_gate") == stage_gate and \
                    _audit_four_stage_case(case, row)
                replay = Path(temporary) / name
                (replay / "original").mkdir(parents=True)
                (replay / "verified").mkdir()
                for filename in ("original/lib.rs", "verified/lib.rs", "decode.out", "proof-ast.ml", "verifast.log"):
                    shutil.copyfile(case / filename, replay / filename)
                replayed = consumer._classify(name, replay, meta, execution,
                                              old, stage_proof.mir_helper, stage_proof.ast_helper)
                valid = valid and replayed == row
        report["concrete_u64_consumer"] = ("REPLAYED_DIAGNOSTIC" if valid else "INCONCLUSIVE")

        native_valid = True
        native_report = {}
        for suffix, function in NATIVE_UNIT_SMOKES:
            log_path = tracked_build / f"native-unit-{suffix}.log"
            exit_path = tracked_build / f"native-unit-{suffix}-exit-code.txt"
            log = log_path.read_text(errors="replace")
            code = int(exit_path.read_text().strip())
            errors = [line for line in log.splitlines() if re.search(r"\berror:", line, re.I)]
            smoke_ok = (code == 0 and not errors and "0 errors found" in log and
                        re.search(rf"Verifying function '{re.escape(function)}'", log) is not None)
            native_report[suffix] = {"exit_code": code, "errors": errors,
                                     "function_seen": function in log,
                                     "zero_errors": "0 errors found" in log,
                                     "complete": smoke_ok}
            native_valid = native_valid and smoke_ok
        report["native_unit_smokes"] = native_report
        report["compiler_layout_fact"] = layout.classify_compiler_facts(
            tracked_build, layout_path.parent / "compiler-layout.rs", environment, profile_build)
        report["artifact_bindings_valid"] = bool(
            valid and native_valid and report["compiler_layout_fact"]["valid"])
        report["classification"] = ("EVIDENCE_COMPLETE_DIAGNOSTIC"
                                    if report["artifact_bindings_valid"] else "INCONCLUSIVE")
        report["accepted"] = False
    except (OSError, ValueError, KeyError, TypeError, AttributeError, ImportError) as error:
        report["reason"] = str(error)
    return report


def audit_span_controls(base: Path, aggregate: dict, profile: str) -> tuple[bool, bool]:
    controls_dir = (Path(__file__).resolve().parents[2] /
                    "cloud-build/incoming-span-lifetime/controls")
    manifest_path = controls_dir / "MANIFEST.json"
    runner_path = controls_dir / "run.py"
    summary = json.loads((base / "span-results.json").read_text())
    manifest = json.loads(manifest_path.read_text())
    runner_spec = importlib.util.spec_from_file_location(
        "incoming_span_lifetime_controls", runner_path)
    runner = importlib.util.module_from_spec(runner_spec)
    runner_spec.loader.exec_module(runner)
    valid = (manifest.get("schema") == "incoming-span-lifetime-controls-v1" and
             manifest.get("accepted") is False and
             {item.get("name") for item in manifest.get("cases", [])} == SPAN_CONTROL_NAMES and
             summary == aggregate.get("allocation_span_controls") and
             summary.get("manifest_sha256") == sha256_file(manifest_path) and
             summary.get("profile") == profile and summary.get("accepted") is False and
             set(summary.get("controls", {})) == SPAN_CONTROL_NAMES and
             set(summary.get("case_details", {})) == SPAN_CONTROL_NAMES and
             set(summary.get("case_artifacts", {})) == SPAN_CONTROL_NAMES)
    if not valid:
        return False, False
    matched = True
    # Use the package's pure saved-log classifier with fresh metadata derived
    # from its pinned source and manifest. It writes only under this temp dir.
    with tempfile.TemporaryDirectory(prefix="merge-span-audit-") as temp_dir:
        _, metadata = runner.prepare(Path(temp_dir) / "prepared")
        for name in sorted(SPAN_CONTROL_NAMES):
            case = base / "controls" / name
            row = json.loads((case / "classification.json").read_text())
            source = case / "verified/lib.rs"
            stages = row.get("stages", {})
            before = row.get("source_before", {})
            source_sha = sha256_file(source)
            valid = (valid and row.get("case") == name and row.get("accepted") is False and
                     source_sha == sha256_file(case / "original/lib.rs") ==
                     metadata[name].get("source_sha256") == row.get("source_sha256") and
                     before.get("verified/lib.rs") == source_sha and
                     before.get("original/lib.rs") == source_sha and
                     row.get("source_after") == before and
                     row.get("source_unchanged_at_every_stage") is True and
                     summary["controls"][name] == row.get("classification") and
                     summary["case_details"][name].get("source_sha256") == source_sha and
                     summary["case_details"][name].get("target_line") ==
                     metadata[name].get("target_line"))
            expected_artifacts = {
                "directory": f"controls/{name}",
                "log": f"controls/{name}/verifast.log",
                "classification": f"controls/{name}/classification.json",
            }
            valid = valid and summary["case_artifacts"][name] == expected_artifacts
            source_unchanged = True
            for stage in ("exporter", "decode", "verifast", "refinement"):
                data = json.loads((case / f"{stage}-stage.json").read_text())
                stage_unchanged = data.get("source_unchanged") is True
                source_unchanged = source_unchanged and stage_unchanged
                valid = (valid and data.get("exit_code") == stages.get(stage) ==
                         int((case / f"{stage}-exit-code.txt").read_text()) and
                         stage_unchanged)
            temp_case = Path(temp_dir) / name
            temp_case.mkdir(parents=True, exist_ok=True)
            (temp_case / "verifast.log").write_bytes((case / "verifast.log").read_bytes())
            if name == "span_retired_local_reuse":
                decode_bytes = (case / "decode.out").read_bytes()
                ast_bytes = (case / "proof-ast.ml").read_bytes()
                (temp_case / "decode.out").write_bytes(decode_bytes)
                (temp_case / "proof-ast.ml").write_bytes(ast_bytes)
                gate = runner.retired_mir_ast_gate(temp_case, name)
                valid = (valid and gate.get("admitted") is True and
                         gate.get("decode_sha256") == hashlib.sha256(decode_bytes).hexdigest() and
                         gate.get("proof_ast_sha256") == hashlib.sha256(ast_bytes).hexdigest() and
                         row.get("retired_mir_ast_gate") == gate and
                         summary["case_details"][name].get("retired_mir_ast_gate") == gate)
            execution = {key: row[key] for key in
                         ("stages", "source_unchanged_at_every_stage") if key in row}
            execution["source_unchanged_at_every_stage"] = source_unchanged
            independent = runner.classify(name, temp_case, metadata[name], execution)
            derived_keys = ("case", "classification", "accepted", "meaning",
                            "target_line", "read_lines", "expected_stages", "source_sha256",
                            "expectation", "target_executed", "reads_executed",
                            "retired_mir_ast_gate")
            valid = (valid and all(independent.get(key) == row.get(key)
                                   for key in derived_keys) and
                     summary["case_details"][name].get("classification") ==
                     independent.get("classification") and
                     summary["case_details"][name].get("expected_stages") ==
                     independent.get("expected_stages") and
                     summary["case_details"][name].get("read_lines") ==
                     independent.get("read_lines"))
            matched = matched and independent.get("classification") != "INCONCLUSIVE"
    valid = (valid and summary.get("all_matched") is matched and
             aggregate.get("allocation_span_controls_match") is matched)
    return bool(valid), bool(matched)


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

    def raw_cases(aggregate_rel: str, group: str) -> dict:
        if group not in selected:
            return {"classification": "NOT_RUN"}
        try:
            value = json.loads((evidence / aggregate_rel).read_text())
            return value.get("cases", {}) if isinstance(value, dict) else {"_aggregate": "MALFORMED"}
        except (OSError, ValueError):
            return {"_aggregate": "MISSING_OR_MALFORMED"}


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
                *[f"cases/{dirname}/cases/{case}/classification.json" for case in
                  (("positive", "prototype_false", "first_body_false", "missing_payload", "constructor")
                   if group.startswith("guard-payload-own") else DROP_CASES)],
            ]
        elif group in GUARD_CONSTRUCTION_GROUPS:
            dirname = GUARD_CONSTRUCTION_GROUPS[group]["directory"]
            mandatory[group] = [
                f"cases/{dirname}/environment.json",
                f"cases/{dirname}/extraction.json",
                f"cases/{dirname}/results.json",
                f"cases/{dirname}/aggregate.json",
                *[f"cases/{dirname}/cases/{case}/classification.json"
                  for case in GUARD_CONSTRUCTION_CASES],
            ]
        elif group in GUARD_CONSTRUCTION_V3_GROUPS:
            dirname = GUARD_CONSTRUCTION_V3_GROUPS[group]["directory"]
            mandatory[group] = [
                f"cases/{dirname}/environment.json",
                f"cases/{dirname}/extraction.json",
                f"cases/{dirname}/results.json",
                f"cases/{dirname}/aggregate.json",
                *[f"cases/{dirname}/cases/{case}/classification.json"
                  for case in GUARD_CONSTRUCTION_CASES],
            ]
        elif group in GUARD_CONSTRUCTION_V4_GROUPS:
            dirname = GUARD_CONSTRUCTION_V4_GROUPS[group]["directory"]
            mandatory[group] = [f"cases/{dirname}/{name}.json" for name in
                                ("environment", "extraction", "results", "aggregate")]
            mandatory[group].extend(f"cases/{dirname}/cases/{name}/classification.json"
                                    for name in GUARD_CONSTRUCTION_CASES)
        elif group in GUARD_GEOMETRY_GROUPS:
            mandatory[group] = [f"cases/{group}/{name}.json" for name in
                                ("environment", "extraction", "results", "aggregate")]
            mandatory[group].extend(f"cases/{group}/cases/{name}/classification.json"
                                    for name in GUARD_GEOMETRY_CASES)
        elif group == ONECELL_GROUP:
            mandatory[group] = [
                "tracked-md-build/profile-build.json",
                "tracked-md-build/profile-input.json",
                "tracked-md-build/tracked-md.patch",
                "tracked-md-build/emitter.patched.ml",
                "tracked-md-build/kernel.patched.ml",
                "tracked-md-build/allocation-span.patch",
                f"cases/{group}/span-results.json",
            ]
            mandatory[group].extend(f"cases/{group}/{name}.json" for name in
                                    ("environment", "extraction", "results", "aggregate"))
            mandatory[group].extend(f"cases/{group}/cases/{name}/classification.json"
                                    for name in ONECELL_CASES)
            mandatory[group].extend(f"cases/{group}/md-controls/{name}/classification.json"
                                    for name in ONECELL_MD_CASES)
            mandatory[group].extend(
                f"cases/{group}/controls/{name}/classification.json"
                for name in sorted(SPAN_CONTROL_NAMES))
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
        # Successful stages can be silent. Keep their log files mandatory,
        # while the exit ledgers and audited stage evidence carry the result.
        if path.startswith(f"cases/{OR_JOIN_GROUP}/") and item.name in {
            "preflight.log", "calibrated-real-dead.log",
            "uncalibrated-liveness-controls.log", "actual-bounded.log",
            "admission-controls.log", "six-comparison.log",
        }:
            return True
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
                        row.get("accepted", False) is not False or
                        row.get("source_unchanged_at_every_stage") is not True or
                        row.get("source_before") != row.get("source_after") or
                        not isinstance(row.get("source_before"), dict) or
                        row["source_before"].get("original/lib.rs") != meta.get("original_sha256") or
                        row["source_before"].get("verified/lib.rs") != meta.get("verified_sha256")):
                    return False
                case_dir = base / "cases" / name
                verified_case = case_dir / "verified/lib.rs"
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
                actual_body_names = checked_body_names(verified_case.read_bytes())
                if (not isinstance(bodies, list) or bodies != actual_body_names or
                        len(bodies) != len(set(bodies)) or name not in bodies or
                        row.get("expected_bodies") != bodies or
                        not isinstance(body_execution, dict) or not isinstance(body_records, dict) or
                        not set(body_records).issubset(set(bodies)) or
                        not isinstance(row.get("error_lines"), list) or
                        not isinstance(row.get("dead_code_records"), list) or
                        type(row.get("full_positive_gate")) is not bool or
                        not isinstance(classifier_controls, dict) or not classifier_controls or
                        not all(value is True for value in classifier_controls.values()) or
                        any(not isinstance(body_execution.get(body), int) for body in bodies) or
                        any(not isinstance(value, dict) for value in body_records.values()) or
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
                            body_execution.get(name, 0) <= 0 or
                            len(row.get("error_lines", [])) != 1 or
                            row.get("dead_code_records")):
                        return False
                elif name == "current_owner_transposition_double_owner_calibration":
                    expected = meta.get("expected_rejection")
                    target_line = meta.get("marked_target_line")
                    expected_message = (
                        "No matching heap chunks: foreach<T>(cons(head("
                        "transposition_values(T_typeid, vs, i, j)), nil), own0(T_typeid, t))")
                    exact_error = (f"verified/lib.rs({target_line},95-102): error: "
                                   f"{expected_message}")
                    if (meta.get("negative") is not True or
                            meta.get("unclassified_target") is not False or
                            meta.get("expected_error") is not None or
                            meta.get("expected_dead") is not None or
                            row.get("expected_error") is not None or
                            not isinstance(expected, dict) or
                            expected != {
                                "kind": "memory_permission",
                                "error_file": "verified/lib.rs",
                                "error_line": target_line,
                                "column_start": 95,
                                "column_end": 102,
                                "message": expected_message,
                                "target_line": target_line,
                            } or
                            type(target_line) is not int or target_line <= 0 or
                            row.get("expected_rejection") != expected or
                            row.get("rejection_class") != "proof" or
                            type(row.get("intended_rejection_gate")) is not bool or
                            classification not in {"EXPECTED_REJECTION", "INCONCLUSIVE"}):
                        return False
                    if classification == "EXPECTED_REJECTION":
                        first_failure = row.get("first_failure")
                        target_log = (case_dir / "verifast.log").read_text(errors="replace")
                        if (row.get("intended_rejection_gate") is not True or
                                row.get("full_positive_gate") is not False or
                                stages != {"exporter": 0, "decode": 0,
                                           "verifast": 1, "refinement": 0} or
                                row.get("error_lines") != [exact_error] or
                                row.get("dead_code_records") != [] or
                                not isinstance(first_failure, dict) or
                                first_failure.get("stage") != "verifast" or
                                first_failure.get("exit_code") != 1 or
                                first_failure.get("diagnostic") != exact_error or
                                not all(body_execution.get(body, 0) > 0 for body in bodies) or
                                not re.search(rf"(?m)^.*verified/lib\.rs\({target_line},"
                                              r"\d+(?:-\d+)?\): (?:note: )?Executing statement$",
                                              target_log)):
                            return False
                else:
                    if (meta.get("negative") is not False or
                            meta.get("expected_error") is not None or
                            meta.get("unclassified_target") is not False or
                            row.get("expected_error") is not None or
                            classification not in {"PASS", "INCONCLUSIVE"}):
                        return False
                if classification == "PASS":
                    if (name == "current_owner_transposition_false_entry" or
                            row.get("full_positive_gate") is not True or
                            not all(stages.get(stage) == 0 for stage in stages) or
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
                double_owner = aggregate.get("cases", {}).get(
                    "current_owner_transposition_double_owner_calibration", "INCONCLUSIVE")
                permutation_cases[group] = {
                    "accepted": False,
                    "raw_case_statuses": aggregate.get("cases", {}),
                    "double_owner_intended_negative": double_owner,
                    "double_owner_interpretation": (
                        "FRESH_MATCHED_FOREACH_OWNER_CHUNK_REFUSAL_ONLY_UNACCEPTED"
                        if valid and double_owner == "EXPECTED_REJECTION" else
                        "INTENDED_NEGATIVE_INCONCLUSIVE" if valid else
                        "AUDIT_INVALID_NO_NEGATIVE_CREDIT"),
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
        if group.startswith("guard-payload-own"):
            continue
        if group in selected:
            artifact_status[group] = artifact_status.get(group, False) and audit_copy_on_drop(group, spec)

    guard_construction_reports = {}
    guard_construction_v3_reports = {}
    guard_construction_v4_reports = {}

    def audit_guard_construction(group: str, spec: dict, variant: str = "v2") -> bool:
        base = cases / spec["directory"]
        reports = (guard_construction_v4_reports if variant == "v4" else
                   guard_construction_v3_reports if variant == "v3" else guard_construction_reports)
        try:
            environment = json.loads((base / "environment.json").read_text())
            extraction = json.loads((base / "extraction.json").read_text())
            results = json.loads((base / "results.json").read_text())
            aggregate = json.loads((base / "aggregate.json").read_text())
            provider_info = environment.get("provider")
            diagnostic_profile = (GUARD_CONSTRUCTION_V4_PROFILE if variant == "v4" else
                                  GUARD_CONSTRUCTION_V3_PROFILE if variant == "v3" else
                                  "copy-on-drop-source-construction-full-source-fragment-v2")
            if (environment.get("accepted") is not False or
                    environment.get("diagnostic_profile") != diagnostic_profile or
                    environment.get("tool_profile") != spec["profile"] or
                    environment.get("source_sha256") != GUARD_CONSTRUCTION_SOURCE_SHA256 or
                    environment.get("source_git_blob") != GUARD_CONSTRUCTION_SOURCE_BLOB or
                    environment.get("proof_sha") != proof_sha or
                    not isinstance(provider_info, dict) or
                    provider_info.get("provider") != "cloud-build" or
                    environment.get("schema_sha256") != "f48fcf29b99717c2e0cb37d4708b47eccaa3270b999e4a84093e37fbd51b7469" or
                    extraction.get("profile") != diagnostic_profile or
                    extraction.get("accepted") is not False or
                    extraction.get("source_sha256") != GUARD_CONSTRUCTION_SOURCE_SHA256 or
                    extraction.get("source_git_blob") != GUARD_CONSTRUCTION_SOURCE_BLOB or
                    extraction.get("complete_guard_drop_block_sha256") != GUARD_CONSTRUCTION_BLOCK_SHA256 or
                    extraction.get("source_constructor_line") != 279 or
                    extraction.get("source_constructor_sha256") != GUARD_CONSTRUCTION_LINE_SHA256 or
                    extraction.get("no_drop_impl_in_fragment") is not True or
                    extraction.get("full_source_permission_only") is not True or
                    extraction.get("unsafe_wrapper_for_conditional_explicit_contract") is not True):
                return False
            if variant in {"v3", "v4"}:
                pins = environment.get("profile_pins")
                compiler = environment.get("rustc_version", "")
                drivers = environment.get("compiler_drivers")
                expected_profile_evidence = (evidence /
                    ("build" if spec["profile"] != "stock-26.10" else "")).resolve()
                actual_profile_evidence = Path(environment.get("profile_evidence", "")).resolve()
                if (extraction.get("profile") != diagnostic_profile or
                        extraction.get("nonprecise_own") is not True or
                        extraction.get("own_payload_body_matches_v2") is not True or
                        extraction.get("v2_full_source_own_sha256") !=
                            "d223c896071993d9070361ddabbee0cce1b03fefbb71c1568f89556618916233" or
                        extraction.get("constructor_contract_sha256") !=
                            "628a914e2ebb529f7a2a0e514436cec53c46702ffeb360714467b6ff8de3c2aa" or
                        extraction.get("exact_own_sha256") !=
                            "01369778e4adf0c338b1ba40d4be956cccbfad917bc99bf7a6aaf4fb07c6868f" or
                        not isinstance(extraction.get("roundtrip_sha256"), str) or
                        extraction.get("roundtrip_sha256") !=
                            (GUARD_CONSTRUCTION_V4_ROUNDTRIP_SHA256 if variant == "v4" else
                             GUARD_CONSTRUCTION_V3_ROUNDTRIP_SHA256) or
                        "commit-hash: f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f" not in compiler or
                        "host: x86_64-unknown-linux-gnu" not in compiler or
                        not isinstance(environment.get("rustc_sha256"), str) or
                        not re.fullmatch(r"[0-9a-f]{64}", environment["rustc_sha256"]) or
                        not isinstance(environment.get("capnp_sha256"), str) or
                        not re.fullmatch(r"[0-9a-f]{64}", environment["capnp_sha256"]) or
                        not isinstance(drivers, dict) or not drivers or
                        any(not isinstance(value, str) or
                            not re.fullmatch(r"[0-9a-f]{64}", value)
                            for value in drivers.values()) or not isinstance(pins, dict)):
                    return False
                if (environment.get("cloud_build_id") != build_id or
                        provider_info.get("build_id") != build_id or
                        actual_profile_evidence != expected_profile_evidence or
                        Path(environment.get("tool_home", "")).name !=
                            ("source" if spec["profile"] != "stock-26.10" else "verifast-26.10") or
                        Path(environment.get("schema_path", "")).name != "vf_mir.capnp" or
                        not environment.get("compiler_sysroot", "").endswith(
                            "nightly-2026-09-25-x86_64-unknown-linux-gnu") or
                        environment.get("rustc_sha256") !=
                            "dda7234360b7f578ca8b0ddcb80145646fa61a67c1720a5abc7051b35c9fcb71" or
                        environment.get("capnp_sha256") !=
                            "450cbc621cf98bc9e704dd1691cdd16ebfcafe15d4122c24b3326973d4766019" or
                        len(drivers) != 1 or next(iter(drivers.values())) !=
                            "892e036a701998dd196197e2d1bcd249fd80ade067d42915b7e02ed7dfdef707"):
                    return False
                if spec["profile"] == "stock-26.10":
                    expected_pins = {
                        "bin/verifast": "9b7650ad3ab0dad3b8974ae9ba1c662ab2cd897ce1dd07215dedcbe460249ee1",
                        "bin/vf-rust-mir-exporter": "b00c75f43ab4d89bf85f5e62a5114a238b89b720d4598d90423347b9d97ac796",
                        "bin/refinement-checker": "b049c8d1b0bb350f77664e1c75c5a95966c5839984abc25c7cb629c0cba04d28",
                        "prelude_sha256": "d7058d43557a2b5147eb1377e85bb67d04b94c83594b6c1c27650c9c571841b5",
                        "spec_manifest_sha256": "4a0911303bbb087f1f50ce85524197edbb541f31c72e8133dfbcc9cf528e03a0",
                        "spec_checks_sha256": "2adb5f85e2077a96e2db6b97da9af17d9324ad3c586187292854970e63078da4",
                    }
                    if (any(pins.get(key) != value for key, value in expected_pins.items()) or
                            pins.get("spec_resource_count") != 58):
                        return False
                else:
                    expected_pins = {
                        "kernel_patched": "100eebae92c770a0b8cd57e2639588761f881316dd522fc3b9a9b1ec6fd91cd6",
                        "translator_patched": "ffd6fe925364b8274d61f094d43211f9463e0dc3e98ae545d3f528f2da0cf6c0",
                        "parser_patched": "8ed673086183323058aac5e0e21399e4532d1e74b97c5d41105827e8643107bd",
                        "prelude_patched": "d1079bc94ceafe6595c7ce216f9c93e3436d22d849bd31bcb0cf442dd183e751",
                        "stdlib_patched": "d92e5044bbb2692e7b006fc649df361fe80bf878b69b5a2bb80635a27330f227",
                        "z3_runtime": "1837668dc531d14b3a4fffc0b690b77929d29c41868f98a89686f5ff64da95ea",
                        "applied_patch_sha256": "b163d3e36b695304cbc6c84d025af7bd5d679a5fb553356baa8b8362dea1b927",
                        "profile_manifest_sha256": "1c0611b783c2e1a88c32f515fb5e594d18ef7a9877ff158a9386f87a1e16e0ac",
                        "experimental_console_sha256": "354436b99d7225e86271f211a43969b0c7f11f3c7f823a7d718abe00946a4f47",
                        "bin/vf-rust-mir-exporter": "b00c75f43ab4d89bf85f5e62a5114a238b89b720d4598d90423347b9d97ac796",
                        "bin/refinement-checker": "b049c8d1b0bb350f77664e1c75c5a95966c5839984abc25c7cb629c0cba04d28",
                    }
                    if (any(pins.get(key) != value for key, value in expected_pins.items()) or
                            pins.get("build_runtime_sha256") !=
                            sha256_file(evidence / "build/source-build-runtime.txt")):
                        return False
            result_cases = results.get("cases")
            aggregate_cases = aggregate.get("cases")
            extraction_cases = extraction.get("cases")
            names = set(GUARD_CONSTRUCTION_CASES)
            if (results.get("profile") != diagnostic_profile or
                    aggregate.get("profile") != diagnostic_profile or
                    results.get("accepted") is not False or aggregate.get("accepted") is not False or
                    not all(isinstance(value, dict) for value in
                            (result_cases, aggregate_cases, extraction_cases)) or
                    set(result_cases) != names or set(aggregate_cases) != names or
                    set(extraction_cases) != names or
                    aggregate_cases != {name: result_cases[name].get("classification") for name in names}):
                return False
            raw_cases = {}
            case_evidence = {}
            for name in GUARD_CONSTRUCTION_CASES:
                meta = extraction_cases[name]
                row = result_cases[name]
                case_dir = base / "cases" / name
                classification_path = case_dir / "classification.json"
                classification = json.loads(classification_path.read_text())
                if (not isinstance(row, dict) or not isinstance(classification, dict) or
                        row != classification or row.get("accepted") is not False or
                        row.get("case") != name or
                        row.get("classification") not in {
                            "PASS_FRAGMENT_ONLY", "EXPECTED_FALSE_ASSERTION", "INCONCLUSIVE"} or
                        meta.get("runtime_source_identical_after_ghost_strip") is not True or
                        meta.get("source_statement_line") != 279 or
                        meta.get("source_statement_sha256") != GUARD_CONSTRUCTION_LINE_SHA256 or
                        type(meta.get("verified_statement_line")) is not int):
                    return False
                if variant in {"v3", "v4"} and row.get("classification") != "INCONCLUSIVE":
                    ast_gate = row.get("ast_admission")
                    if (not isinstance(ast_gate, dict) or
                            ast_gate.get("admitted") is not True or
                            ast_gate.get("own_precision") != "nonprecise" or
                            ast_gate.get("own_precision_is_expected") is not True or
                            ast_gate.get("generated_fbc_matches_expected_precision_and_payload") is not True or
                            ast_gate.get("payload_roundtrip_open_assert_close") is not True or
                            ast_gate.get("own_open_count") != 1 or
                            ast_gate.get("own_close_count") != 2 or
                            ast_gate.get("payload_roundtrip_assertion_count") != 1 or
                            ast_gate.get("full_supplied_pre_shape") is not True or
                            ast_gate.get("full_normal_post_shape") is not True or
                            ast_gate.get("literal_unwind_false") is not True or
                            ast_gate.get("runtime_assume_count") != 0):
                        return False
                if variant == "v4":
                    if (extraction.get("canonical_fbc_packaging_only") is not True or
                            extraction.get("parent_v3b_profile") != GUARD_CONSTRUCTION_V3_PROFILE or
                            extraction.get("parent_v3b_roundtrip_sha256") != GUARD_CONSTRUCTION_V3_ROUNDTRIP_SHA256 or
                            extraction.get("fbc_roundtrip_sha256") != GUARD_CONSTRUCTION_V4_ROUNDTRIP_SHA256 or
                            meta.get("fbc_roundtrip_sha256") != GUARD_CONSTRUCTION_V4_ROUNDTRIP_SHA256):
                        return False
                    if row.get("classification") != "INCONCLUSIVE" and (
                            ast_gate.get("fbc_close_count") != 1 or
                            ast_gate.get("fbc_open_count") != 1 or
                            ast_gate.get("fbc_roundtrip_same_guard_and_ordered") is not True):
                        return False
                for rel, key in (("original/lib.rs", "original_sha256"),
                                 ("verified/lib.rs", "verified_sha256")):
                    path = case_dir / rel
                    if not path.is_file() or path.is_symlink() or sha256_file(path) != meta.get(key):
                        return False
                initial = row.get("initial_source_hashes")
                final = row.get("final_source_hashes")
                source_before = json.loads((case_dir / "source-before.json").read_text())
                if (row.get("source_unchanged_at_every_stage") is not True or
                        not isinstance(initial, dict) or final != initial or source_before != initial or
                        initial.get("small_sort_source") != GUARD_CONSTRUCTION_SOURCE_SHA256 or
                        initial.get("original/lib.rs") != meta.get("original_sha256") or
                        initial.get("verified/lib.rs") != meta.get("verified_sha256")):
                    return False
                stages = row.get("stages")
                if not isinstance(stages, dict) or set(stages) != set(GUARD_CONSTRUCTION_STAGES):
                    return False
                for stage in GUARD_CONSTRUCTION_STAGES:
                    stage_json = case_dir / f"{stage}-stage.json"
                    stage_log = case_dir / f"{stage}.log"
                    stage_out = case_dir / ("compiler-mir.bin" if stage == "exporter" else f"{stage}.out")
                    stage_resources = case_dir / f"{stage}-resources.txt"
                    stage_exit = case_dir / f"{stage}-exit-code.txt"
                    if not all(path.is_file() and not path.is_symlink() for path in
                               (stage_json, stage_log, stage_out, stage_resources, stage_exit)):
                        return False
                    stage_record = json.loads(stage_json.read_text())
                    code = stages.get(stage)
                    if (type(code) is not int or stage_record.get("exit_code") != code or
                            int(stage_exit.read_text().strip()) != code):
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
                if (not mir_binary.is_file() or mir_binary.is_symlink() or
                        not mir_hash_file.is_file() or mir_hash_file.is_symlink() or
                        mir_hash_file.read_text().strip() != sha256_file(mir_binary)):
                    return False
                mir_gate = row.get("mir_admission")
                ast_gate = row.get("ast_admission")
                if (not isinstance(mir_gate, dict) or type(mir_gate.get("admitted")) is not bool or
                        not isinstance(ast_gate, dict) or type(ast_gate.get("admitted")) is not bool or
                        type(row.get("constructor_body_count")) is not int or
                        type(row.get("source_statement_executed")) is not bool or
                        not isinstance(row.get("global_errors"), list) or
                        not isinstance(row.get("dead_code_records"), list)):
                    return False
                log = (case_dir / "verifast.log").read_text(errors="replace")
                headers = [(match.start(), match.group(1)) for match in re.finditer(
                    r"^\s*\d+(?:\.\d+)?s: [^\s(]+\([0-9]+,[0-9]+"
                    r"(?:-[0-9]+(?:,[0-9]+)?)?\): Verifying function '([^']+)'$",
                    log, re.M)]
                body_segments = []
                for index, (start, function) in enumerate(headers):
                    if function == "source_guard_construction" or function.startswith(
                            "source_guard_construction<"):
                        end = headers[index + 1][0] if index + 1 < len(headers) else len(log)
                        body_segments.append(log[start:end])
                body_segment = body_segments[0] if len(body_segments) == 1 else ""
                log_errors = [line for line in log.splitlines()
                              if re.search(r"\berror:", line, re.I)]
                log_dead = [line for line in log.splitlines()
                            if re.search(r"dead code", line, re.I)]
                statement_seen = bool(re.search(
                    rf"verified/lib\.rs\({meta['verified_statement_line']},[0-9]+"
                    r"(?:-[0-9]+(?:,[0-9]+)?)?\): (?:note: )?Executing statement",
                    body_segment))
                if (row.get("global_errors") != log_errors or
                        row.get("dead_code_records") != log_dead or
                        row.get("source_statement_executed") is not statement_seen):
                    return False
                common = (row.get("source_unchanged_at_every_stage") is True and
                          stages.get("exporter") == 0 and stages.get("decode") == 0 and
                          stages.get("refinement") == 0 and mir_gate.get("admitted") is True and
                          ast_gate.get("admitted") is True and len(body_segments) == 1 and
                          statement_seen and not log_dead)
                if name == "positive":
                    expected_classification = (
                        "PASS_FRAGMENT_ONLY" if common and stages.get("verifast") == 0 and
                        not log_errors and "Executing return statement" in body_segment and
                        "Leak check." in body_segment and "0 errors found" in log
                        else "INCONCLUSIVE")
                else:
                    oracle = meta.get("intended_failure", {})
                    target_error = (len(log_errors) == 1 and
                        bool(re.search(
                            rf"verified/lib\.rs\({oracle.get('line')},{oracle.get('column_start')}-"
                            rf"{oracle.get('column_end')}\): error: Assertion might not hold\. "
                            r"\(Cannot prove false\.\)", log_errors[0])))
                    expected_classification = (
                        "EXPECTED_FALSE_ASSERTION" if common and
                        stages.get("verifast") == 1 and target_error and
                        "Executing return statement" not in body_segment and
                        "Leak check." not in body_segment else "INCONCLUSIVE")
                if row.get("classification") != expected_classification:
                    return False
                case_evidence[name] = {
                    "classification": row["classification"],
                    "stages": stages,
                    "source_hashes_unchanged": row.get("source_unchanged_at_every_stage"),
                    "runtime_source_identical_after_ghost_strip": meta.get(
                        "runtime_source_identical_after_ghost_strip"),
                    "mir_admitted": mir_gate.get("admitted"),
                    "ast_admitted": ast_gate.get("admitted"),
                    "own_precision": ast_gate.get("own_precision"),
                    "fbc_roundtrip_same_guard_and_ordered": ast_gate.get("fbc_roundtrip_same_guard_and_ordered"),
                    "payload_roundtrip_open_assert_close": ast_gate.get(
                        "payload_roundtrip_open_assert_close"),
                    "constructor_body_count": row.get("constructor_body_count"),
                    "source_statement_executed": statement_seen,
                    "positive_return_seen": "Executing return statement" in body_segment,
                    "positive_leak_check_seen": "Leak check." in body_segment,
                    "global_errors": log_errors,
                    "dead_code_records": log_dead,
                }
                if row["classification"] == "PASS_FRAGMENT_ONLY":
                    if (name != "positive" or stages != {"exporter": 0, "decode": 0,
                            "verifast": 0, "refinement": 0} or
                            mir_gate.get("admitted") is not True or ast_gate.get("admitted") is not True or
                            row.get("constructor_body_count") != 1 or
                            row.get("source_statement_executed") is not True or
                            row.get("global_errors") or row.get("dead_code_records") or
                            len(body_segments) != 1 or
                            "Executing return statement" not in body_segment or
                            "Leak check." not in body_segment or
                            "0 errors found" not in log):
                        return False
                if row["classification"] == "EXPECTED_FALSE_ASSERTION":
                    oracle = meta.get("intended_failure")
                    if (name != "first_body_false" or not isinstance(oracle, dict) or
                            stages != {"exporter": 0, "decode": 0, "verifast": 1, "refinement": 0} or
                            mir_gate.get("admitted") is not True or ast_gate.get("admitted") is not True or
                            row.get("constructor_body_count") != 1 or
                            row.get("source_statement_executed") is not True or
                            len(row.get("global_errors", [])) != 1 or row.get("dead_code_records") or
                            len(body_segments) != 1 or
                            "Executing return statement" in body_segment or
                            "Leak check." in body_segment):
                        return False
                    expected = re.compile(
                        rf"verified/lib\.rs\({oracle['line']},{oracle['column_start']}-{oracle['column_end']}\): "
                        r"error: Assertion might not hold\. \(Cannot prove false\.\)")
                    if not any(expected.search(line) for line in row["global_errors"]):
                        return False
                raw_cases[name] = row["classification"]
            expected_fragment_pass = (
                raw_cases["positive"] == "PASS_FRAGMENT_ONLY" and
                raw_cases["first_body_false"] == "EXPECTED_FALSE_ASSERTION")
            if aggregate.get("fragment_pass") is not expected_fragment_pass:
                return False
            reports[group] = {
                "classification": "EVIDENCE_COMPLETE_DIAGNOSTIC",
                "accepted": False, "artifact_bindings_valid": True,
                "raw_case_classifications": raw_cases,
                "case_evidence": case_evidence,
                "fragment_pass": expected_fragment_pass,
                "actual_drop_compatibility": "OPEN",
                "scope": ("isolated actual construction/physical canonical-FBC packaging fragment; Drop/caller OPEN" if variant == "v4" else
                          "isolated nonprecise-own constructor fragment with exact payload "
                          "roundtrip; no Drop/caller compatibility" if variant == "v3" else
                          "isolated constructor fragment only; no Drop/caller compatibility"),
            }
            return True
        except (OSError, ValueError, KeyError, TypeError, AttributeError):
            reports[group] = {
                "classification": "INCONCLUSIVE", "accepted": False,
                "artifact_bindings_valid": False,
            }
            return False

    for group, spec in GUARD_CONSTRUCTION_GROUPS.items():
        if group not in selected:
            guard_construction_reports[group] = {
                "classification": "NOT_RUN", "accepted": False,
                "artifact_bindings_valid": False,
                "raw_case_classifications": {name: "NOT_RUN" for name in GUARD_CONSTRUCTION_CASES},
            }
        else:
            construction_valid = audit_guard_construction(group, spec)
            artifact_status[group] = artifact_status.get(group, False) and construction_valid
            if group not in guard_construction_reports:
                raw = raw_cases(f"cases/{spec['directory']}/aggregate.json", group)
                cases_raw = raw.get("cases", raw) if isinstance(raw, dict) else {}
                guard_construction_reports[group] = {
                    "classification": "INCONCLUSIVE", "accepted": False,
                    "artifact_bindings_valid": False,
                    "raw_case_classifications": cases_raw,
                    "actual_drop_compatibility": "OPEN",
                }

    for group, spec in GUARD_CONSTRUCTION_V3_GROUPS.items():
        if group not in selected:
            guard_construction_v3_reports[group] = {
                "classification": "NOT_RUN", "accepted": False,
                "artifact_bindings_valid": False,
                "raw_case_classifications": {name: "NOT_RUN" for name in GUARD_CONSTRUCTION_CASES},
                "actual_drop_compatibility": "OPEN",
            }
        else:
            construction_valid = audit_guard_construction(group, spec, variant="v3")
            artifact_status[group] = artifact_status.get(group, False) and construction_valid
            if group not in guard_construction_v3_reports:
                raw = raw_cases(f"cases/{spec['directory']}/aggregate.json", group)
                cases_raw = raw.get("cases", raw) if isinstance(raw, dict) else {}
                guard_construction_v3_reports[group] = {
                    "classification": "INCONCLUSIVE", "accepted": False,
                    "artifact_bindings_valid": False,
                    "raw_case_classifications": cases_raw,
                    "actual_drop_compatibility": "OPEN",
                }

    for group, spec in GUARD_CONSTRUCTION_V4_GROUPS.items():
        if group not in selected:
            guard_construction_v4_reports[group] = {"classification": "NOT_RUN", "accepted": False}
            continue
        construction_valid = audit_guard_construction(group, spec, variant="v4")
        artifact_status[group] = artifact_status.get(group, False) and construction_valid
        if group not in guard_construction_v4_reports:
            guard_construction_v4_reports[group] = {"classification": "INCONCLUSIVE", "accepted": False,
                                                    "artifact_bindings_valid": False,
                                                    "raw_case_classifications": raw_cases(f"cases/{spec['directory']}/aggregate.json", group)}

    guard_geometry_reports = {}
    for group, profile in GUARD_GEOMETRY_GROUPS.items():
        if group not in selected:
            guard_geometry_reports[group] = {"classification": "NOT_RUN", "accepted": False}
            continue
        try:
            helper_path = Path(__file__).resolve().parent / "guard-geometry-audit.py"
            helper_spec = importlib.util.spec_from_file_location("guard_geometry_outer_audit", helper_path)
            helper = importlib.util.module_from_spec(helper_spec)
            helper_spec.loader.exec_module(helper)
            report = helper.audit_geometry(root, group, profile, proof_sha, build_id)
            guard_geometry_reports[group] = report
            artifact_status[group] = artifact_status.get(group, False) and report["artifact_bindings_valid"]
        except (OSError, ValueError, KeyError, TypeError, AttributeError, ImportError) as error:
            artifact_status[group] = False
            guard_geometry_reports[group] = {"classification": "INCONCLUSIVE", "accepted": False,
                                            "artifact_bindings_valid": False, "reason": str(error)}

    onecell_report = {"classification": "NOT_RUN", "accepted": False,
                      "actual_drop_glue": "OPEN"}
    if ONECELL_GROUP in selected:
        try:
            component = selection_path.parent.parent / "overnight/guard-ownership/insertion-onecell"
            pins = json.loads((component / "PROFILE.json").read_text())
            build = json.loads((evidence / "tracked-md-build/profile-build.json").read_text())
            profile_input = json.loads((evidence / "tracked-md-build/profile-input.json").read_text())
            base = cases / ONECELL_GROUP
            environment = json.loads((base / "environment.json").read_text())
            extraction = json.loads((base / "extraction.json").read_text())
            results = json.loads((base / "results.json").read_text())
            aggregate = json.loads((base / "aggregate.json").read_text())
            names = set(ONECELL_CASES) | set(ONECELL_MD_CASES)
            case_classes = aggregate.get("cases", {})
            build_identity = (pins == profile_input and
                build.get("schema") == pins.get("schema") == "smallsort-tracked-md-profile-v1" and
                re.fullmatch(r"[0-9a-f]{64}", pins.get("emitter_sha256", "")) is not None and
                build.get("emitter_sha256") == pins.get("emitter_sha256") and
                build.get("profile") == pins.get("profile") == ONECELL_PROFILE and
                build.get("accepted") is False and build.get("build_exit") == 0 and
                build.get("proof_sha") == proof_sha and
                build.get("provider", {}).get("build_id") == build_id and
                sha256_file(evidence / "tracked-md-build/tracked-md.patch") ==
                    pins.get("patch_sha256") == sha256_file(component / "tracked-md.patch") and
                sha256_file(evidence / "tracked-md-build/emitter.patched.ml") == pins.get("emitter_sha256") and
                sha256_file(evidence / "tracked-md-build/kernel.patched.ml") == pins.get("kernel_sha256") and
                sha256_file(evidence / "tracked-md-build/model.patched.ml") == pins.get("model_sha256") and
                sha256_file(evidence / "tracked-md-build/unit-layout.patch") ==
                    pins.get("unit_layout_patch_sha256") == sha256_file(component.parents[3] / "cloud-build/origin-layout/unit-layout.patch") and
                sha256_file(evidence / "tracked-md-build/allocation-span.patch") ==
                    pins.get("allocation_span_patch_sha256") == sha256_file(component / "allocation-span.patch") and
                all(build.get(key) == value for key, value in pins.items()) and
                re.fullmatch(r"[0-9a-f]{64}", build.get("console_sha256", "")))
            extraction_identity = (
                extraction.get("profile") == ONECELL_DIAGNOSTIC and
                extraction.get("source_sha256") == DROP_SOURCE_SHA256 and
                extraction.get("source_git_blob") == DROP_SOURCE_BLOB and
                extraction.get("source_block_sha256") == DROP_BLOCK_SHA256 and
                extraction.get("source_read_sha256") ==
                    hashlib.sha256(b"        let tmp = ManuallyDrop::new(tail.read());\n").hexdigest() and
                extraction.get("source_guard_sha256") == hashlib.sha256(
                    b"        let mut gap_guard = CopyOnDrop { src: &*tmp, dst: tail, len: 1 };\n").hexdigest() and
                extraction.get("no_drop_impl_in_fragment") is True and
                extraction.get("supplied_entry_resources") is True and
                extraction.get("accepted") is False and
                set(extraction.get("cases", {})) == set(ONECELL_CASES))
            environment_identity = (
                environment.get("profile") == ONECELL_PROFILE and
                environment.get("accepted") is False and
                environment.get("proof_sha") == proof_sha and
                environment.get("cloud_build_id") == build_id and
                environment.get("provider", {}).get("build_id") == build_id and
                environment.get("schema_sha256") ==
                    "f48fcf29b99717c2e0cb37d4708b47eccaa3270b999e4a84093e37fbd51b7469" and
                environment.get("source_sha256") == DROP_SOURCE_SHA256 and
                environment.get("tool_sha256", {}).get("verifast") == build.get("console_sha256") and
                environment.get("tool_sha256", {}).get("vf-rust-mir-exporter") ==
                    pins.get("exporter_sha256") and
                environment.get("tool_sha256", {}).get("refinement-checker") ==
                    pins.get("refiner_sha256") and
                (Path(environment.get("profile_evidence", "")).resolve() ==
                    Path("/workspace/evidence/allprooflogs/tracked-md-build") or
                 Path(environment.get("profile_evidence", "")).resolve() ==
                    (evidence / "tracked-md-build").resolve()))
            rows_valid = (isinstance(results, dict) and set(results) == names and
                          set(case_classes) == names and aggregate.get("profile") == ONECELL_PROFILE and
                          aggregate.get("accepted") is False and
                          aggregate.get("actual_drop_glue") == "OPEN")
            campaign_mode = aggregate.get("campaign") == ONECELL_CAMPAIGN
            dependency = aggregate.get("md_dependency_basis")
            dependency_valid = (isinstance(dependency, dict) and
                dependency.get("classification") == "NOT_RUN_ON_NEW_PROFILE" and
                dependency.get("source_sha256") == ONECELL_CAMPAIGN_MD_SOURCE_SHA256 and
                dependency.get("historical_build_id") == ONECELL_CAMPAIGN_BASELINE["build_id"] and
                dependency.get("historical_profile_sha256") == ONECELL_CAMPAIGN_BASELINE["profile_sha256"] and
                dependency.get("historical_results_sha256") == ONECELL_CAMPAIGN_BASELINE["results_sha256"] and
                dependency.get("proof_sha") == proof_sha and
                sha256_file(selection_path.parent.parent.parent /
                    "verifast-tracked-manually-drop-regressions.rs") ==
                    ONECELL_CAMPAIGN_MD_SOURCE_SHA256)
            rows_valid = (rows_valid and (
                (campaign_mode and dependency_valid and
                 aggregate.get("md_regressions_matched") is False) or
                (not campaign_mode and dependency is None)))
            if rows_valid:
                for name in names:
                    case = base / ("cases" if name in ONECELL_CASES else "md-controls") / name
                    row = results[name]
                    retained = json.loads((case / "classification.json").read_text())
                    orig = case / "original/lib.rs"
                    verified = case / "verified/lib.rs"
                    meta = extraction["cases"].get(name) if name in ONECELL_CASES else None
                    stages = row.get("stages", {})
                    before = row.get("source_before", {})
                    rows_valid = (row == retained and row.get("accepted") is False and
                        row.get("case") == name and case_classes[name] == row.get("classification") and
                        row.get("source_unchanged_at_every_stage") is True and
                        row.get("source_after") == before and
                        before.get("small_sort_source") == DROP_SOURCE_SHA256 and
                        before.get("original/lib.rs") == sha256_file(orig) and
                        before.get("verified/lib.rs") == sha256_file(verified) and
                        set(stages) == {"exporter", "decode", "verifast", "refinement"} and
                        (meta is None or (meta.get("original_sha256") == sha256_file(orig) and
                            meta.get("verified_sha256") == sha256_file(verified) and
                            meta.get("runtime_ghost_strip_equal") is True and
                            meta.get("source_read_line") == 550 and
                            meta.get("source_guard_line") == 551)))
                    if not rows_valid:
                        break
                    for stage in stages:
                        stage_row = json.loads((case / f"{stage}-stage.json").read_text())
                        rows_valid = (stage_row.get("exit_code") == stages[stage] and
                                      int((case / f"{stage}-exit-code.txt").read_text()) == stages[stage] and
                                      (stage_row.get("status") == "NOT_RUN" or
                                       stage_row.get("source_unchanged") is True))
                        if not rows_valid:
                            break
                    if not rows_valid:
                        break
                    if row.get("classification") == "NOT_RUN":
                        expected_not_run = (
                            campaign_mode and
                            ((name in ONECELL_CASES and
                              row.get("reason") == "runtime extent bridge absent; origin-only change cannot cure separation") or
                             (name in ONECELL_MD_CASES and
                              row.get("reason") == "allocation-span campaign; MD controls NOT_RUN on new profile"))
                        ) or (not campaign_mode and name in ONECELL_CASES and
                              row.get("reason") == "isolated MD gates did not pass" and
                              aggregate.get("md_regressions_matched") is False)
                        rows_valid = (expected_not_run and all(value == 125 for value in stages.values()))
                    elif name in ONECELL_CASES and row.get("classification") != "INCONCLUSIVE":
                        rows_valid = (row.get("source_admission", {}).get("admitted") is True and
                                      row.get("mir_admission", {}).get("admitted") is True and
                                      row.get("ast_admission", {}).get("admitted") is True and
                                      stages.get("exporter") == stages.get("decode") ==
                                      stages.get("refinement") == 0)
                        log = (case / "verifast.log").read_text(errors="replace")
                        log_errors = [line for line in log.splitlines()
                                      if re.search(r"\berror:", line, re.I)]
                        if name == "positive":
                            rows_valid = (rows_valid and row.get("classification") ==
                                          "PASS_FRAGMENT_ONLY" and stages.get("verifast") == 0 and
                                          not log_errors and "Leak check." in log and
                                          "0 errors found" in log and row.get("copy_executed") is True)
                        else:
                            target = meta.get("target", {})
                            expected_line = target.get("line")
                            if name == "missing_held_owner":
                                expected_lines = {expected_line, meta.get("own_close_line")}
                            else:
                                expected_lines = {expected_line}
                            error_line = re.search(r"verified/lib\.rs\((\d+),", log_errors[0]) \
                                if len(log_errors) == 1 else None
                            predicate = ("Cannot prove false" if name in
                                         {"after_fbc_false", "after_recovery_false"}
                                         else "No matching heap chunks")
                            rows_valid = (rows_valid and row.get("classification") ==
                                          "EXPECTED_REJECTION" and stages.get("verifast") == 1 and
                                          error_line is not None and
                                          onecell_negative_site_matches(
                                              name, verified.read_text(), log_errors[0], expected_lines) and
                                          predicate in log_errors[0])
                    if not rows_valid:
                        break
            rows_valid_before_controls = rows_valid
            spans_valid, spans_matched = audit_span_controls(base, aggregate, ONECELL_PROFILE)
            origin_valid, origin_summary = audit_origin_controls(base, aggregate, ONECELL_PROFILE)
            nested_controls = audit_onecell_nested_controls(
                base, aggregate, evidence / "tracked-md-build")
            candidate_gates = audit_combined_candidate_gates(
                base, aggregate, environment, proof_sha, build_id,
                evidence / "tracked-md-build")
            rows_valid = (rows_valid and spans_valid and origin_valid and
                          nested_controls.get("artifact_bindings_valid") is True)
            if candidate_gates.get("applicable"):
                rows_valid = rows_valid and candidate_gates.get("artifact_bindings_valid") is True
            expected_md = (False if campaign_mode else
                all(results[name].get("classification") == "REGRESSION_MATCHED"
                    for name in ONECELL_MD_CASES)) if rows_valid else False
            expected_fragment = (spans_matched and ((dependency_valid and
                results["positive"].get("classification") == "PASS_FRAGMENT_ONLY" and
                results["after_recovery_false"].get("classification") == "EXPECTED_REJECTION")
                if campaign_mode else (expected_md and
                results["positive"].get("classification") == "PASS_FRAGMENT_ONLY" and
                all(results[name].get("classification") == "EXPECTED_REJECTION"
                    for name in ONECELL_CASES if name != "positive")))) if rows_valid else False
            rows_valid = (rows_valid and aggregate.get("md_regressions_matched") is expected_md and
                          aggregate.get("fragment_pass") is expected_fragment)
            mandatory_artifacts_valid = bool(artifact_status.get(ONECELL_GROUP, False))
            valid = bool(mandatory_artifacts_valid and build_identity and
                         extraction_identity and environment_identity and rows_valid)
            artifact_status[ONECELL_GROUP] = valid
            onecell_report = {"classification": "EVIDENCE_COMPLETE_DIAGNOSTIC" if valid else "INCONCLUSIVE",
                              "accepted": False, "artifact_bindings_valid": valid,
                              "binding_checks": {"mandatory_artifacts": mandatory_artifacts_valid,
                                                 "profile_build": bool(build_identity),
                                                 "source_extraction": extraction_identity,
                                                 "environment_receipt": environment_identity,
                                                 "case_rows": rows_valid,
                                                 "case_rows_before_controls": rows_valid_before_controls,
                                                 "span_controls": spans_valid,
                                                 "origin_controls": origin_valid,
                                                 "nested_receipts": nested_controls.get("artifact_bindings_valid") is True,
                                                 "combined_candidate_gates": (
                                                     candidate_gates.get("artifact_bindings_valid") is True
                                                     if candidate_gates.get("applicable") else "NOT_RUN"),
                                                 "campaign_mode": campaign_mode,
                                                 "md_dependency": dependency_valid,
                                                 "expected_md": expected_md,
                                                 "expected_fragment": expected_fragment,
                                                 "aggregate_md": aggregate.get("md_regressions_matched"),
                                                 "aggregate_fragment": aggregate.get("fragment_pass")},
                              "fragment_pass": aggregate.get("fragment_pass") is True if valid else False,
                              "campaign": aggregate.get("campaign"),
                              "md_dependency_basis": dependency if valid else None,
                              "raw_case_classifications": case_classes,
                              "allocation_span_controls": aggregate.get("allocation_span_controls"),
                              "origin_controls": origin_summary,
                              "nested_controls": nested_controls,
                              "combined_candidate_gates": candidate_gates,
                              "native_origin_exit": int((evidence / "tracked-md-build/native-origin-exit-code.txt").read_text()),
                              "actual_drop_glue": "OPEN"}
        except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
            artifact_status[ONECELL_GROUP] = False
            onecell_report = {"classification": "INCONCLUSIVE", "accepted": False,
                              "artifact_bindings_valid": False, "reason": str(error),
                              "actual_drop_glue": "OPEN"}

    guard_payload_reports = {}
    for group in ("guard-payload-own-diagnostic", "guard-payload-own-stock-diagnostic"):
        if group not in selected:
            guard_payload_reports[group] = {"classification": "NOT_RUN", "accepted": False}
            continue
        base = cases / group
        valid = artifact_status.get(group, False)
        try:
            extraction = json.loads((base / "extraction.json").read_text())
            results = json.loads((base / "results.json").read_text())
            aggregate = json.loads((base / "aggregate.json").read_text())
            names = {"positive", "prototype_false", "first_body_false", "missing_payload", "constructor"}
            valid = valid and (set(extraction["cases"]) == set(results["cases"]) == set(aggregate["cases"]) == names and
                              results.get("accepted") is False and aggregate.get("accepted") is False and
                              extraction.get("source_sha256") == DROP_SOURCE_SHA256 and
                              extraction.get("source_git_blob") == DROP_SOURCE_BLOB and
                              extraction.get("source_block_sha256") == DROP_BLOCK_SHA256)
            for name in names:
                meta = extraction["cases"][name]
                row = results["cases"][name]
                direct = row["direct_body"]
                gate = row["payload_gate"]
                case_dir = base / "cases" / name
                valid = valid and (gate.get("accepted") is False and
                                   direct.get("source_unchanged_at_every_stage") is True and
                                   direct.get("stages") == row.get("stages") and
                                   aggregate["cases"][name] == gate.get("classification") and
                                   meta.get("runtime_source_identical_after_ghost_strip") is True)
                for relative, key in (("original/lib.rs", "original_sha256"), ("verified/lib.rs", "verified_sha256")):
                    valid = valid and sha256_file(case_dir / relative) == meta.get(key)
                for stage, code in row["stages"].items():
                    valid = valid and stage in DROP_STAGES and type(code) is int and \
                        int((case_dir / (stage + "-exit-code.txt")).read_text()) == code and \
                        (case_dir / (stage + ".log")).is_file()
            guard_payload_reports[group] = {"accepted": False, "artifact_bindings_valid": valid,
                "raw_case_statuses": aggregate["cases"],
                "conditional_bridge_pass": aggregate.get("conditional_bridge_pass", False),
                "scope": "annotation-only own/FBC/conditional construction diagnostic; actual caller/glue/forget OPEN"}
        except (OSError, ValueError, TypeError, KeyError, AttributeError):
            valid = False
            guard_payload_reports[group] = {"accepted": False, "artifact_bindings_valid": False,
                                           "classification": "INCONCLUSIVE"}
        artifact_status[group] = valid

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
                                 "actual-bounded", "admission-controls", "six-comparison")
            raw_inner_groups = seven.get("group_status")
            inner_statuses_bound = isinstance(raw_inner_groups, dict) and set(raw_inner_groups) == set(inner_group_names)
            if inner_statuses_bound:
                inner_statuses_bound = all(
                    (base / f"{name}-exit-code.txt").read_text().strip() == raw_inner_groups[name] and
                    all((base / f"{name}{suffix}").is_file() and
                        not (base / f"{name}{suffix}").is_symlink()
                        for suffix in ("-exit-code.txt", ".log", "-resources.txt"))
                    for name in inner_group_names)
            raw_status_rows = {}
            if raw_groups.is_file():
                for line in raw_groups.read_text(errors="replace").splitlines():
                    fields = line.split()
                    if len(fields) >= 2 and fields[0] in inner_group_names:
                        raw_status_rows.setdefault(fields[0], []).append(fields[1])
            group_status_file_bound = (
                isinstance(raw_inner_groups, dict) and
                set(raw_status_rows) == set(inner_group_names) and
                all(len(raw_status_rows[name]) == 1 and
                    raw_status_rows[name][0] == raw_inner_groups.get(name)
                    for name in inner_group_names))
            budget_text = (base / "work-budget.txt").read_text(errors="replace")
            budget_match = re.search(r"\bbudget=([0-9]+)\b", budget_text)
            lane_budget_lines = (root / "lane-work-budget.txt").read_text(errors="replace").splitlines()
            lane_budget_match = next((re.fullmatch(r"mir_or_join_work_seconds=([0-9]+)", line)
                                      for line in lane_budget_lines
                                      if line.startswith("mir_or_join_work_seconds=")), None)
            inner_budget = int(budget_match.group(1)) if budget_match else None
            outer_budget = int(lane_budget_match.group(1)) if lane_budget_match else None
            budget_bound = (inner_budget is not None and inner_budget == outer_budget and
                            1 <= inner_budget <= 1300)
            or_join_status["raw_inner_group_statuses"] = raw_inner_groups
            or_join_status["inner_group_statuses_bound"] = bool(inner_statuses_bound)
            or_join_status["group_status_file_bound"] = bool(group_status_file_bound)
            or_join_status["work_budget_seconds"] = inner_budget
            or_join_status["outer_work_budget_seconds"] = outer_budget
            controls = seven.get("invalid_shape_admission_controls")
            component_identity = (
                seven.get("component") == "MIR-OR-JOIN-LIVENESS" and
                seven.get("profile") == OR_JOIN_PROFILE and
                seven.get("accepted") is False and
                seven.get("component_gates_complete") is False and
                seven.get("base_six_profile_accepted") is False and
                isinstance(controls, dict) and
                isinstance(raw_inner_groups, dict) and
                controls.get("accepted") is False and
                type(controls.get("full_shape_matrix_complete")) is bool and
                controls.get("group_status") == raw_inner_groups.get("admission-controls") and
                controls.get("classification") in {"OBSERVED_UNACCEPTED", "NOT_RUN", "INCONCLUSIVE"} and
                isinstance(seven.get("same_source_six_component_comparison"), dict))
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
                                "audit_checker_sha256", "control_driver_sha256",
                                "control_exporter_sha256", "retained_pointer_prove_sha256",
                                "diagnostic_source_sha256", "admitted_fixture_sha256",
                                "admitted_source_sha256", "expected_seven_full_diff_sha256")) and
                manifest.get("control_driver_sha256") ==
                    sha256_file(Path(__file__).resolve().parents[4] /
                                OR_JOIN_COMPONENT / "control-driver.py") and
                manifest.get("control_exporter_sha256") ==
                    sha256_file(Path(__file__).resolve().parents[4] /
                                OR_JOIN_COMPONENT / "control-exporter.py") and
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
                        build.get("seven_full_diff_sha256") == manifest.get("expected_seven_full_diff_sha256") ==
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
            driver_report_path = base / "admission-controls/control-driver.json"
            raw_driver_report = controls.get("raw_report") if isinstance(controls, dict) else None
            reported_driver_sha = controls.get("report_sha256") if isinstance(controls, dict) else None
            driver_report_file_valid = False
            if driver_report_path.is_file() and not driver_report_path.is_symlink():
                driver_json = json.loads(driver_report_path.read_text())
                driver_report_file_valid = (
                    isinstance(driver_json, dict) and raw_driver_report == driver_json and
                    reported_driver_sha == sha256_file(driver_report_path) and
                    driver_json.get("accepted") is False and
                    driver_json.get("proof_accepted") is False and
                    driver_json.get("tool_homes_unchanged") in {True, None} and
                    driver_json.get("classification") in
                        {"ADMISSION_CONTROLS_OBSERVED_UNACCEPTED", "INCONCLUSIVE"})
            elif raw_driver_report is None:
                driver_report_file_valid = reported_driver_sha is None
            driver_status_value = (raw_inner_groups.get("admission-controls")
                                   if isinstance(raw_inner_groups, dict) else None)
            required_modes = {
                "roundtrip", "storage-live-34", "storage-live-36", "goto-38-34",
                "goto-38-36", "statement-count-34", "statement-count-36",
                "real-statement-34", "predecessor-32", "comparison-eq-33",
                "comparison-eq-35", "branch-order-33", "branch-order-35",
                "span-column-34", "span-column-36", "panic-callee", "panic-unwind"}
            shape_matrix_bound = False
            if isinstance(raw_driver_report, dict) and raw_driver_report.get("full_shape_matrix_complete") is True:
                modes = raw_driver_report.get("modes")
                source_gate = raw_driver_report.get("source_hash_gate")
                shape_matrix_bound = (
                    isinstance(modes, dict) and set(modes) == required_modes and
                    modes["roundtrip"].get("classification") == "ADMISSION_PASS_ONLY" and
                    all(modes[mode].get("classification") == "EXPECTED_FRONTEND_REFUSAL"
                        for mode in required_modes - {"roundtrip"}) and
                    all(row.get("official_refinement_exit") == 0 and row.get("source_unchanged") is True
                        and row.get("proof_accepted") is False for row in modes.values()) and
                    isinstance(source_gate, dict) and source_gate.get("classification") == "EXPECTED_SOURCE_HASH_REFUSAL" and
                    source_gate.get("stage") == "SOURCE_ADMISSION_BEFORE_EXPORT" and
                    source_gate.get("exit_code") == 2 and source_gate.get("accepted") is False and
                    source_gate.get("original_source_sha256") == manifest.get("admitted_source_sha256") and
                    source_gate.get("mutated_source_sha256") == sha256_file(base / "admission-controls/source-hash-gate/lib.rs") and
                    source_gate.get("stdout_sha256") == sha256_file(base / "admission-controls/source-hash-gate/stdout") and
                    source_gate.get("stderr_sha256") == sha256_file(base / "admission-controls/source-hash-gate/stderr"))
                for mode in required_modes:
                    row = modes[mode]
                    mode_case = base / "admission-controls/cases" / mode
                    mode_log = ((mode_case / "verifast.stdout").read_text(errors="replace") +
                                (mode_case / "verifast.stderr").read_text(errors="replace"))
                    shape_matrix_bound = bool(shape_matrix_bound and
                        hashlib.sha256(mode_log.encode()).hexdigest() == row.get("log_sha256") and
                        (mode == "roundtrip" or row.get("verifast_exit") == 1))
                    if row.get("proof_ast_sha256") is not None:
                        shape_matrix_bound = bool(shape_matrix_bound and
                            sha256_file(mode_case / "proof-ast.ml") == row["proof_ast_sha256"])
                    for role, key in (("manual", "manual_certificate"), ("frontend", "frontend_certificate")):
                        cert_path = base / "admission-controls/calls" / mode / role / "certificate.json"
                        certificate = json.loads(cert_path.read_text())
                        shape_matrix_bound = bool(shape_matrix_bound and certificate == row.get(key) and
                            certificate.get("classification") == "MESSAGE_CERTIFIED" and
                            certificate.get("exact_semantic_tree_match") is True and
                            certificate.get("source_sha256") == manifest.get("admitted_source_sha256") and
                            certificate.get("official_exporter_sha256") == manifest.get("release_exporter_sha256"))
            shape_report_valid = (
                isinstance(controls, dict) and controls.get("full_shape_matrix_complete") ==
                (isinstance(raw_driver_report, dict) and raw_driver_report.get("full_shape_matrix_complete") is True) and
                (controls.get("full_shape_matrix_complete") is not True or shape_matrix_bound))
            comparison = seven.get("same_source_six_component_comparison")
            comparison_bound = (
                isinstance(comparison, dict) and comparison.get("accepted") is False and
                comparison.get("proof_negative") is False and
                comparison.get("group_status") == raw_inner_groups.get("six-comparison") and
                type(comparison.get("complete")) is bool and
                (comparison.get("classification") == "SAME_SOURCE_COVERAGE_DIFFERENCE_UNACCEPTED") ==
                    comparison.get("complete") and
                (comparison.get("classification") == "NOT_RUN") ==
                    (comparison.get("group_status") == "NOT_RUN") and
                comparison.get("classification") in {
                    "NOT_RUN", "INCONCLUSIVE", "SAME_SOURCE_COVERAGE_DIFFERENCE_UNACCEPTED"})
            if comparison_bound and comparison.get("complete") is True:
                six_root = base / "six-comparison"
                six_results = json.loads((six_root / "results.json").read_text())
                six_aggregate = json.loads((six_root / "aggregate.json").read_text())
                six_row = six_results.get("cases", {}).get("bidirectional_merge_len23", {})
                comparison_bound = bool(
                    set(six_results.get("cases", {})) == {"bidirectional_merge_len23"} and
                    six_aggregate.get("evidence_collection_completed") is True and
                    six_aggregate.get("classifier_controls_passed") is True and
                    six_aggregate.get("cases", {}).get("bidirectional_merge_len23") == six_row.get("classification") ==
                        comparison.get("raw_classification") and
                    comparison.get("stages") == six_row.get("stages"))
                six_case = six_root / "cases/bidirectional_merge_len23"
                if comparison.get("classification") == "SAME_SOURCE_COVERAGE_DIFFERENCE_UNACCEPTED":
                    comparison_bound = bool(comparison_bound and
                        all(comparison.get(key) is True for key in (
                            "source_identical", "normal_mir_identical", "all_eleven_bodies_and_return_leak_records",
                            "exact_sole_synthetic_dead_record")) and
                        six_row.get("error_lines") == [] and
                        six_row.get("stages") == {"exporter": 0, "decode": 0, "verifast": 1, "refinement": 0} and
                        six_row.get("dead_code_records") == comparison.get("observed_dead_lines") and
                        sha256_file(six_case / "verified/lib.rs") == manifest.get("admitted_source_sha256") and
                        sha256_file(six_case / "original/lib.rs") == preflight.get("original_sha256") and
                        sha256_file(six_case / "normal-exporter.out") ==
                            sha256_file(base / "actual/cases/bidirectional_merge_len23/normal-exporter.out"))
            trial_mode = manifest.get("trial_mode", "FULL_TARGET")
            trial_file = base / "trial-mode.txt"
            trial_bound = (trial_mode in {"FULL_TARGET", "SHAPE_CONTROLS_ONLY"} and
                trial_file.is_file() and not trial_file.is_symlink() and
                trial_file.read_text().strip() == trial_mode == seven.get("trial_mode") and
                type(seven.get("shape_controls_complete_in_this_run")) is bool and
                type(seven.get("shape_actual_capture_complete")) is bool)
            shape_capture_bound = False
            if trial_bound and trial_mode == "SHAPE_CONTROLS_ONLY":
                capture_root = base / "actual"
                capture = capture_root / "cases/bidirectional_merge_len23"
                capture_results = json.loads((capture_root / "results.json").read_text())
                capture_aggregate = json.loads((capture_root / "aggregate.json").read_text())
                capture_row = capture_results.get("cases", {}).get("bidirectional_merge_len23", {})
                provenance_path = capture / "normal-exporter-provenance.json"
                provenance = json.loads(provenance_path.read_text())
                build = json.loads((base / "build/seven-profile-manifest.json").read_text())
                shape_capture_bound = bool(
                    pin_bindings and
                    set(capture_results.get("cases", {})) == {"bidirectional_merge_len23"} and
                    capture_aggregate.get("evidence_collection_completed") is True and
                    capture_aggregate.get("classifier_controls_passed") is True and
                    capture_aggregate.get("cases", {}).get("bidirectional_merge_len23") ==
                        capture_row.get("classification") == seven.get("short_capture_harness_classification") and
                    capture_row.get("source_unchanged_at_every_stage") is True and
                    capture_row.get("source_before") == capture_row.get("source_after") and
                    all(capture_row.get("stages", {}).get(stage) == 0 and
                        (capture / f"{stage}-exit-code.txt").read_text().strip() == "0"
                        for stage in ("exporter", "decode", "refinement")) and
                    int((capture / "verifast-exit-code.txt").read_text().strip()) ==
                        capture_row.get("stages", {}).get("verifast") and
                    (capture / "proof-ast.ml").is_file() and
                    (capture / "proof-ast.ml").stat().st_size > 0 and
                    provenance.get("normal_preprocess") is True and
                    provenance.get("source_unchanged") is True and
                    provenance.get("proof_sha") == proof_sha and
                    provenance.get("execution_id") == build_id and
                    provenance.get("source_sha256") == manifest.get("admitted_source_sha256") and
                    provenance.get("mir_sha256") == sha256_file(capture / "normal-exporter.out") and
                    provenance.get("decoded_sha256") == sha256_file(capture / "normal-decode.out") and
                    (capture / "normal-exporter-exit-code.txt").read_text().strip() == "0" and
                    (capture / "normal-decode-exit-code.txt").read_text().strip() == "0" and
                    build.get("seven_full_diff_sha256") == manifest.get("expected_seven_full_diff_sha256") ==
                        sha256_file(base / "build/full-seven-applied-profile.patch") and
                    seven.get("diagnostic_complete") is False and
                    seven.get("actual_bounded_full_positive") is False and
                    seven.get("actual_bounded_raw_classification") == "INCONCLUSIVE" and
                    all(raw_inner_groups.get(name) == "NOT_RUN" for name in
                        ("calibrated-real-dead", "uncalibrated-liveness-controls", "six-comparison")))
            shape_flag_bound = bool(trial_bound and
                (trial_mode != "SHAPE_CONTROLS_ONLY" or
                 seven.get("shape_actual_capture_complete") is not True or shape_capture_bound) and
                (seven.get("shape_controls_complete_in_this_run") is not True or
                 (trial_mode == "SHAPE_CONTROLS_ONLY" and shape_capture_bound and
                  shape_matrix_bound and driver_report_file_valid and driver_status_value == "0")))
            or_join_status["trial_mode"] = trial_mode
            or_join_status["trial_mode_binding_valid"] = bool(trial_bound)
            or_join_status["shape_capture_binding_valid"] = bool(shape_capture_bound)
            or_join_status["shape_controls_complete_in_this_run"] = seven.get("shape_controls_complete_in_this_run") is True
            or_join_status["same_source_six_component_comparison"] = comparison
            or_join_status["same_source_comparison_binding_valid"] = bool(comparison_bound)
            driver_classification_valid = (
                (controls.get("classification") == "OBSERVED_UNACCEPTED" and
                 driver_status_value == "0" and driver_report_file_valid and
                 isinstance(raw_driver_report, dict) and
                 raw_driver_report.get("classification") == "ADMISSION_CONTROLS_OBSERVED_UNACCEPTED" and
                 raw_driver_report.get("tool_homes_unchanged") is True and shape_matrix_bound) or
                (controls.get("classification") == "NOT_RUN" and
                 driver_status_value == "NOT_RUN" and raw_driver_report is None and
                 reported_driver_sha is None and driver_report_file_valid) or
                (controls.get("classification") == "INCONCLUSIVE" and
                 driver_report_file_valid and
                 (driver_status_value not in {"0", "NOT_RUN"} or
                  (driver_status_value == "0" and isinstance(raw_driver_report, dict) and
                   raw_driver_report.get("classification") in
                       {"INCONCLUSIVE", "ADMISSION_CONTROLS_OBSERVED_UNACCEPTED"})))
            ) if isinstance(controls, dict) else False
            or_join_status["invalid_shape_admission_controls"] = {
                "classification": controls.get("classification") if isinstance(controls, dict) else "INCONCLUSIVE",
                "group_status": driver_status_value,
                "report_sha256": reported_driver_sha,
                "raw_report": raw_driver_report,
                "accepted": False,
                "full_shape_matrix_complete": controls.get("full_shape_matrix_complete") is True,
                "full_shape_matrix_binding_valid": bool(shape_matrix_bound),
                "report_binding_valid": bool(driver_report_file_valid),
                "status_valid": bool(driver_classification_valid),
            }
            or_join_status["artifact_hash_bindings_valid"] = bool(
                manifest_bytes_match and pin_fields and pin_bindings and
                driver_report_file_valid and driver_classification_valid and shape_report_valid and comparison_bound and shape_flag_bound and
                (seven.get("diagnostic_complete") is not True or full_evidence_valid))
            or_join_status["complete_evidence_hash_bindings_valid"] = bool(full_evidence_valid)
            or_join_status["run_script_exit_code"] = run_status
            or_join_status["lane_group_exit_code"] = external_status
            return bool(minimum and manifest_bytes_match and component_identity and
                        run_status is not None and external_status is not None and
                        inner_statuses_bound and group_status_file_bound and
                        driver_report_file_valid and driver_classification_valid and shape_report_valid and comparison_bound and shape_flag_bound and budget_bound and
                        pin_fields and pin_bindings and
                        (seven.get("diagnostic_complete") is not True or full_evidence_valid))
        except (OSError, ValueError, KeyError, TypeError, AttributeError):
            return False

    if OR_JOIN_GROUP in selected:
        # Collect the component's raw report even when a mandatory file is
        # absent; that absence must still make the combined audit fail.
        audited_or_join = audit_or_join()
        artifact_status[OR_JOIN_GROUP] = (
            artifact_status.get(OR_JOIN_GROUP, False) and audited_or_join)

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
            "guard_construction_fragment_diagnostics": guard_construction_reports,
            "guard_construction_nonprecise_v3_diagnostics": guard_construction_v3_reports,
            "guard_construction_canonical_fbc_v4_diagnostics": guard_construction_v4_reports,
            "guard_payload_own_diagnostics": guard_payload_reports,
            "canonical_fbc_drop_geometry_v3": guard_geometry_reports,
            "insertion_onecell_guard_fragment": onecell_report,
            "physical_memory_cell_cases": raw_cases("cases/checked-current-owner-memory-cell/aggregate.json", "current-owner-memory-cell-diagnostic"),
            "stock_physical_memory_cell_cases": raw_cases("cases/checked-current-owner-memory-cell-stock/aggregate.json", "current-owner-memory-cell-stock-diagnostic"),
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
