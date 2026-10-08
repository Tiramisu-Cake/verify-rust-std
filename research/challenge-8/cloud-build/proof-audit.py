#!/usr/bin/env python3
"""Strictly summarize B stock diagnostics or C constructor evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

from provider import require_supported_provider


STOCK_CLASSIFICATIONS = {
    "u32_positive": "POSITIVE",
    "raw_positive": "POSITIVE",
    "u32_false_post": "INTENDED_NEGATIVE",
    "raw_false_post": "INTENDED_NEGATIVE",
    "u32_contradictory_pre": "INTENDED_DEAD_CODE_REJECTION",
    "forget_positive": "INCONCLUSIVE",
    "forget_false_post": "INTENDED_NEGATIVE",
    "forget_contradictory_pre": "INTENDED_DEAD_CODE_REJECTION",
    "ordinary_unwind": "POSITIVE",
    "false_unwind": "INTENDED_NEGATIVE",
    "shared_cleanup": "POSITIVE",
}

CONSTRUCTOR_OUTCOMES = {
    "constructor_positive": "PASS",
    "nonpointer_identity": "PASS",
    "nonpointer_missing_own": "EXPECTED_OPAQUE_OWNERSHIP_REJECT",
    "wrong_inner_post": "EXPECTED_PROOF_FAILURE",
    "false_uninit": "EXPECTED_PROOF_FAILURE",
    "false_assert": "EXPECTED_PROOF_FAILURE",
    "false_postcondition": "EXPECTED_PROOF_FAILURE",
    "resource_duplication": "EXPECTED_PROOF_FAILURE",
    "wrong_active_field": "EXPECTED_APPLICABILITY_REJECT",
    "wrong_operand": "EXPECTED_APPLICABILITY_REJECT",
    "wrong_return": "EXPECTED_APPLICABILITY_REJECT",
    "extra_operation": "EXPECTED_APPLICABILITY_REJECT",
    "renamed_function": "EXPECTED_APPLICABILITY_REJECT",
    "wrong_binding": "EXPECTED_APPLICABILITY_REJECT",
    "nonpointer_input": "EXPECTED_APPLICABILITY_REJECT",
    "extra_union_field": "EXPECTED_APPLICABILITY_REJECT",
}


def read_json(path: Path):
    return json.loads(path.read_text())


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact_dead_code(root: Path, name: str, item: dict) -> dict:
    fixture = read_json(root / name / "fixture.json")
    source = (root / name / "verified/lib.rs").read_text()
    function = fixture["functions"][-1]
    start = next(i for i, line in enumerate(source.splitlines(), 1)
                 if f"unsafe fn {function}" in line)
    end = len(source.splitlines())
    span = f"verified/lib.rs({start},1-{end},2): dead code"
    messages = item.get("dead_code_diagnostics", [])
    log = (root / name / "full-verification.log").read_text(errors="replace")
    raw_dead = [line for line in log.splitlines() if line.endswith(": dead code")]
    strict = item.get("strict_original_classification", {})
    timed = [x for x in strict.get("timed_functions", [])
             if x.get("function") == function]
    passed = (span in raw_dead and messages == raw_dead and
              all(x.startswith("verified/lib.rs(") for x in raw_dead)
              and strict.get("error_count") == 0 and len(timed) == 1
              and timed[0].get("body_execution_seen") is False)
    return {"accepted": passed, "expected_span": span,
            "observed_dead_code_diagnostics": messages,
            "raw_log_dead_code_diagnostics": raw_dead,
            "strict_original_classification": strict.get("classification"),
            "target_body_execution": timed[0].get("body_execution_seen") if len(timed) == 1 else None}


def stock_audit(root: Path) -> dict:
    raw = read_json(root / "summary.json")
    actual_names = set(raw)
    expected_names = set(STOCK_CLASSIFICATIONS)
    rows = {}
    for name, expected in STOCK_CLASSIFICATIONS.items():
        item = raw.get(name)
        if not isinstance(item, dict):
            rows[name] = {"raw": None, "decision": "MISSING", "accepted": False}
            continue
        raw_class = item.get("classification")
        dead_case = name in ("u32_contradictory_pre", "forget_contradictory_pre")
        dead = exact_dead_code(root, name, item) if dead_case else None
        if dead_case:
            accepted = (raw_class in ("INTENDED_DEAD_CODE_REJECTION", "INCONCLUSIVE")
                        and dead["accepted"]
                        and item.get("frontend_all_zero") is True
                        and item.get("source_integrity") is True)
        else:
            accepted = raw_class == expected
        rows[name] = {
            "raw_classification": raw_class,
            "strict_original_classification": item.get("strict_original_classification"),
            "historical_decision": raw_class if dead_case else expected,
            "accepted": accepted,
            "source_integrity": item.get("source_integrity"),
            "frontend_all_zero": item.get("frontend_all_zero"),
            "stages": item.get("stages"),
            "exact_dead_code_gate": dead,
        }
    complete = actual_names == expected_names and all(x["accepted"] for x in rows.values())
    return {
        "accepted": complete,
        "classification": "STOCK_CHAIN_OPERATIONAL_WITH_HISTORICAL_LIMITS" if complete else "INCONCLUSIVE",
        "expected_case_count": 11,
        "actual_case_count": len(actual_names),
        "cases": rows,
        "dead_code_classifier_limit": any(
            rows[name]["raw_classification"] == "INCONCLUSIVE"
            for name in ("u32_contradictory_pre", "forget_contradictory_pre")
            if name in rows),
        "policy": "No classifier output is relabeled. The generic-forget positive retains its historical INCONCLUSIVE result; its intended false-post remains an exact negative. Contradictory-pre outcomes use only the existing checker's exact-span dead-code clause and preserve its strict original class.",
        "source_certificate": read_json(root / "source-certificate.json")
            if (root / "source-certificate.json").exists() else None,
    }


def constructor_audit(root: Path) -> dict:
    data = read_json(root / "summary.json")
    cases = {item.get("case"): item.get("outcome")
             for item in data.get("constructor_cases", [])}
    mir_cases = data.get("mir_mutation_cases", [])
    baselines = data.get("baselines", {})
    native = baselines.get("native_controls", {})
    baseline_controls = {
        "stock_false_control": baselines.get("stock_false_control", {}).get("outcome") == "EXPECTED_PROOF_FAILURE",
        "patched_false_control": baselines.get("patched_false_control", {}).get("outcome") == "EXPECTED_PROOF_FAILURE",
        "stock_pointer_frame": baselines.get("stock_pointer_frame", {}).get("outcome") == "PASS",
        "patched_pointer_frame": baselines.get("patched_pointer_frame", {}).get("outcome") == "PASS",
        "native_controls_count": len(native) == 10,
        "native_controls_all_pass": all(x.get("outcome") == "PASS" for x in native.values()),
    }
    cases_ok = cases == CONSTRUCTOR_OUTCOMES
    mir_ok = len(mir_cases) == 9 and all(
        item.get("outcome") == "EXPECTED_MIR_APPLICABILITY_REJECT"
        for item in mir_cases
    )
    accepted = (
        data.get("constructor_acceptance") is True and cases_ok and mir_ok and
        all(baseline_controls.values()) and data.get("actual_callee_status") == "NOT_RUN"
    )
    return {
        "accepted": accepted,
        "classification": "CONSTRUCTOR_COMPONENT_ACCEPTED" if accepted else "INCONCLUSIVE",
        "constructor_acceptance": data.get("constructor_acceptance"),
        "constructor_case_count": len(cases),
        "constructor_cases_match": cases_ok,
        "constructor_cases": cases,
        "mir_mutation_count": len(mir_cases),
        "all_nine_mir_reject": mir_ok,
        "baseline_controls": baseline_controls,
        "actual_callee_status": data.get("actual_callee_status"),
        "source_certificate": data.get("source_certificate"),
        "source_tool_paths": {
            "tool_home": data.get("tool_home"),
            "stock_home": data.get("stock_home"),
            "compiler_sysroot": data.get("compiler_sysroot"),
        },
    }


def main() -> int:
    provider = require_supported_provider()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lane", choices=("stock", "constructor"), required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--diagnostic-exit-code", type=int, default=0)
    args = parser.parse_args()
    root = args.evidence.resolve()
    result = stock_audit(root) if args.lane == "stock" else constructor_audit(root)
    result["diagnostic_exit_code"] = args.diagnostic_exit_code
    if args.diagnostic_exit_code != 0:
        result["accepted"] = False
        result["classification"] = "INCONCLUSIVE"
    result.update({"lane": args.lane, "provider": provider})
    result["raw_summary_sha256"] = digest(root / "summary.json")
    output = args.output.resolve() if args.output else root / "proof-audit.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    comparison = {
        "historical_stock_baseline": {
            "proof_sha": "a0cfd30e066acbaf1b5406cd9773f54388cc45be",
            "actions_run": "37694000195",
            "known_positive": ["u32_positive", "raw_positive", "ordinary_unwind", "shared_cleanup"],
            "intended_false_posts": ["u32_false_post", "raw_false_post", "forget_false_post", "false_unwind"],
            "strict_inconclusive": ["forget_positive", "u32_contradictory_pre", "forget_contradictory_pre"],
            "dead_code_note": "two contradictory-pre controls had exact dead-code diagnostics; strict classifier remained INCONCLUSIVE",
            "verifast_source_commit": "f76012fb518703b1d98e243ac4f487f16877cfcb",
            "rust_toolchain": "nightly-2026-09-25",
            "repository_std_commit": "cd371e035c7e573760c43bf934d53e8118ee3e7d",
        },
        "historical_accepted_constructor": {
            "proof_sha": "1378f0ffc8342233349fae3df5a938c4a021c8d7",
            "actions_run": "37700450091",
            "verifast_source_commit": "f76012fb518703b1d98e243ac4f487f16877cfcb",
            "verifast_archive_sha256": "5ad2a65997457fd5996a27f93107ef7e52c90c0d12b63b6e67f7acbc73e90efd",
            "rust_toolchain": "nightly-2026-09-25",
            "repository_std_commit": "cd371e035c7e573760c43bf934d53e8118ee3e7d",
            "s6_patch_sha256": "20f7d07ac9bdaca7c46f737b89925dfac3f4cef66c3f5d48aa9634ac949dbc1c",
            "cfg_patch_sha256": "593d09405379974ffbc475c2e0b65d648d8a6913f55b765dd0c3bebdc0922781",
            "actual_callee_status": "NOT_RUN",
        },
        "current_lane": args.lane,
        "current_source_certificate": result.get("source_certificate"),
        "current_tool_source_paths": result.get("source_tool_paths"),
        "raw_evidence_sha256": result["raw_summary_sha256"],
        "runner_environment_sha256": digest(root.parent / "environment.txt")
            if (root.parent / "environment.txt").exists() else None,
        "profile_hashes_sha256": digest(root.parent / "profile-hashes.json")
            if (root.parent / "profile-hashes.json").exists() else None,
        "profile_binary_hashes_sha256": digest(root.parent / "profile-binary-hashes.json")
            if (root.parent / "profile-binary-hashes.json").exists() else None,
        "comparison_scope": "same source/tool pins and constructor component scope; actual-callee remains outside acceptance",
    }
    (output.parent / "comparison-manifest.json").write_text(json.dumps(comparison, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"classification": result["classification"], "accepted": result["accepted"]}, sort_keys=True))
    return 0 if result["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
