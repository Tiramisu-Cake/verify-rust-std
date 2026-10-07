#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted fail-closed classifier checks for the exact S6 pointer-drop matrix."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path


def load_classifier(repo_root: Path):
    path = repo_root / "research/challenge-8/check-pointer-drop.py"
    spec = importlib.util.spec_from_file_location("sort4_pointer_drop_classifier", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("pointer drop classifier loader unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_gate(name: str, gate, fields: tuple[str, ...]) -> dict:
    good = dict.fromkeys(fields, True)
    baseline = gate(good) is True
    false_mutants = {field: gate({**good, field: False}) is False for field in fields}
    missing_mutants = {
        field: gate({key: value for key, value in good.items() if key != field}) is False
        for field in fields
    }
    return {
        "gate": name,
        "baseline_accepts": baseline,
        "false_mutants_rejected": false_mutants,
        "missing_mutants_rejected": missing_mutants,
        "pass": baseline and all(false_mutants.values()) and all(missing_mutants.values()),
    }


def check_proof_messages(classifier) -> dict:
    exemplars = {
        "wrong_preserved": "verified/lib.rs(26,102-104): error: Cannot prove "
            "condition. (Cannot prove !(changed = value).)",
        "false_post": "verified/lib.rs(26,102-104): error: Cannot prove "
            "condition. (Cannot prove false.)",
        "assert_false": "verified/lib.rs(26,102-104): error: Assertion might "
            "not hold. (Cannot prove false.)",
        "lost_cell": "verified/lib.rs(32,1): error: Function leaks heap "
            "chunks: points_to<*const Element>(slot, value)",
        "duplicate_frame": "verified/lib.rs(26,102-104): error: No matching "
            "heap chunks: [f]points_to<u8>(frame, frame_value)",
        "none_init": "verified/lib.rs(29,5-48): error: No matching heap "
            "chunks: points_to<*const Element>(slot, ?value)",
        "unknown_init": "verified/lib.rs(29,5-48): error: Cannot prove that "
            "'state' is an instance of constructor 'some'",
    }
    mutants = {
        "wrong_value": ("wrong_preserved", exemplars["wrong_preserved"].replace(
            "changed = value", "changed = other")),
        "wrong_path": ("wrong_preserved", exemplars["wrong_preserved"].replace(
            "verified/lib.rs", "other/lib.rs")),
        "generic_failure": ("wrong_preserved", exemplars["false_post"]),
        "wrong_cell_type": ("lost_cell", exemplars["lost_cell"].replace(
            "*const Element", "u8")),
        "wrong_cell_binding": ("lost_cell", exemplars["lost_cell"].replace(
            "(slot, value)", "(other, value)")),
        "wrong_frame_binding": ("duplicate_frame", exemplars["duplicate_frame"].replace(
            "(frame, frame_value)", "(other, frame_value)")),
        "none_wrong_resource": ("none_init", exemplars["none_init"].replace(
            "points_to", "other_predicate")),
        "unknown_wrong_constructor": ("unknown_init", exemplars["unknown_init"].replace(
            "'some'", "'none'")),
    }
    accepts = {name: classifier.matches_negative_message(name, message)
               for name, message in exemplars.items()}
    rejects = {name: not classifier.matches_negative_message(variant, message)
               for name, (variant, message) in mutants.items()}
    return {
        "exact_messages_accepted": accepts,
        "mutants_rejected": rejects,
        "mutant_count": len(mutants),
        "pass": all(accepts.values()) and all(rejects.values()),
    }


def check_admission_message(classifier) -> dict:
    reasons = classifier.admission_reasons("source", "contract")
    exact = ('Fatal error: exception Failure("SORT4-POINTER-DROP: '
             'certificate mismatch: method exported SAFE contract")')
    mutants = {
        "wrong_reason": exact.replace("method exported SAFE contract",
                                      "method output type"),
        "wrong_certificate": exact.replace("SORT4-POINTER-DROP", "SORT4-SELECT-INTRINSIC"),
        "wrong_stage": exact.replace("Fatal error: exception Failure(",
                                     "verified/lib.rs(4,1): error: Failure("),
        "trailing_text": exact + " additional error",
    }
    return {
        "exact_accepts": classifier.matches_admission_fatal(exact, reasons),
        "mutants_rejected": {
            name: not classifier.matches_admission_fatal(message, reasons)
            for name, message in mutants.items()
        },
        "mutant_count": len(mutants),
        "pass": classifier.matches_admission_fatal(exact, reasons) and
            all(not classifier.matches_admission_fatal(message, reasons)
                for message in mutants.values()),
    }


def main() -> None:
    if os.environ.get("GITHUB_ACTIONS") != "true" or \
            os.environ.get("RUNNER_ENVIRONMENT") != "github-hosted" or \
            os.environ.get("RUNNER_OS") != "Linux":
        raise SystemExit("pointer drop self-check requires GitHub-hosted Linux Actions")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    classifier = load_classifier(Path(__file__).resolve().parents[2])
    gates = [
        check_gate("positive", classifier.strict_positive_evidence, (
            "source_exact", "stage_integrity", "frontend_refinement",
            "typed_mir_identity", "full_certificate", "modeled_drop_call",
            "safe_prototype", "helper_return_leak", "probe_return_leak",
            "verifier_success",
        )),
        check_gate("negative", classifier.strict_negative_evidence, (
            "positive_prerequisite", "source_exact", "stage_integrity",
            "frontend_refinement", "typed_mir_identity", "full_certificate",
            "modeled_drop_call", "safe_prototype", "helper_return_leak",
            "probe_entered", "one_verifier_error", "target_location",
            "target_message",
        )),
        check_gate("admission", classifier.strict_admission_evidence, (
            "source_exact", "stage_integrity", "frontend_refinement",
            "mutant_exact", "exact_fatal", "before_proof", "verifier_exit_two",
        )),
    ]
    proof = check_proof_messages(classifier)
    admission = check_admission_message(classifier)
    result = {
        "pass": all(item["pass"] for item in gates) and proof["pass"] and admission["pass"],
        "groups": gates,
        "proof_messages": proof,
        "admission_message": admission,
        "mutant_count": sum(2 * len(item["false_mutants_rejected"]) for item in gates),
        "message_mutant_count": proof["mutant_count"],
        "admission_message_mutant_count": admission["mutant_count"],
    }
    evidence = args.evidence.resolve()
    evidence.parent.mkdir(parents=True, exist_ok=True)
    evidence.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"pass": result["pass"], "mutant_count": result["mutant_count"]}))
    if not result["pass"]:
        raise SystemExit("pointer drop classifier self-check failed")


if __name__ == "__main__":
    main()
