#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted fail-closed mutation check for the select-pointer evidence classifier."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path


def load_classifier(repo_root: Path):
    path = repo_root / "research/challenge-8/check-select-pointer.py"
    spec = importlib.util.spec_from_file_location("sort4_select_pointer", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("select-pointer classifier loader unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_gate(name: str, gate, fields: tuple[str, ...]) -> dict:
    good = dict.fromkeys(fields, True)
    baseline = gate(good) is True
    mutants = {field: gate({**good, field: False}) is False for field in fields}
    missing = {field: gate({key: value for key, value in good.items()
                            if key != field}) is False for field in fields}
    return {
        "gate": name,
        "baseline_accepts": baseline,
        "false_mutants_rejected": mutants,
        "missing_mutants_rejected": missing,
        "pass": baseline and all(mutants.values()) and all(missing.values()),
    }


def main() -> None:
    if os.environ.get("GITHUB_ACTIONS") != "true" or \
            os.environ.get("RUNNER_ENVIRONMENT") != "github-hosted" or \
            os.environ.get("RUNNER_OS") != "Linux":
        raise SystemExit("select-pointer classifier self-check requires GitHub-hosted Linux Actions")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parents[2]
    classifier = load_classifier(repo_root)
    checks = [
        check_gate("positive", classifier.strict_positive_evidence, (
            "source_exact", "stage_integrity", "frontend_refinement", "typed_mir_identity",
            "certificate_marker", "safe_prototype", "helper_body_return_leak",
            "probe_body_return_leak", "verifier_success",
        )),
        check_gate("negative", classifier.strict_negative_evidence, (
            "positive_prerequisite", "source_exact", "stage_integrity",
            "frontend_refinement", "typed_mir_identity", "certificate_marker",
            "safe_prototype", "helper_body_return_leak", "named_probe_entered",
            "single_verifier_error", "target_location", "target_message",
            "leak_return_location",
        )),
        check_gate("admission", classifier.strict_admission_evidence, (
            "source_exact", "stage_integrity", "frontend_refinement", "mutant_exact",
            "exact_fatal", "before_proof", "verifier_exit_two",
        )),
    ]
    result = {
        "pass": all(item["pass"] for item in checks),
        "groups": checks,
        "mutant_count": sum(2 * len(item["false_mutants_rejected"]) for item in checks),
    }
    summary = args.evidence.resolve()
    summary.parent.mkdir(parents=True, exist_ok=True)
    summary.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"pass": result["pass"], "mutant_count": result["mutant_count"]}))
    if not result["pass"]:
        raise SystemExit("select-pointer classifier self-check failed")


if __name__ == "__main__":
    main()
