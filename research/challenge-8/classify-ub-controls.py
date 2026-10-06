#!/usr/bin/env python3
"""Classify one Kani UB-control log, or aggregate per-harness JSON records."""

import argparse
import json
import re
import sys
from pathlib import Path


CONTROLS = {
    "positive_initialized_read": "positive",
    "positive_valid_bool_pointer_read": "positive",
    "negative_uninitialized_i32_read": "uninit",
    "negative_invalid_bool_read": "invalid_bool",
    "negative_misaligned_u32_read": "alignment",
    "negative_null_u32_read": "null",
    "negative_immutable_static_write": "immutable_write",
    "negative_immutable_static_write_observed": "immutable_write_observed",
}

PROFILES = {
    "all": [
        "positive_initialized_read",
        "positive_valid_bool_pointer_read",
        "negative_uninitialized_i32_read",
        "negative_invalid_bool_read",
        "negative_misaligned_u32_read",
        "negative_null_u32_read",
        "negative_immutable_static_write",
    ],
    "immutable_observation": [
        "positive_initialized_read",
        "positive_valid_bool_pointer_read",
        "negative_immutable_static_write_observed",
    ],
}

EXPECTED = {
    "uninit": re.compile(r"Undefined Behavior: Reading from an uninitialized", re.I),
    "invalid_bool": re.compile(r"Undefined Behavior: Invalid value of type `?bool`?", re.I),
    "alignment": re.compile(r"align(?:ed|ment|ment check)", re.I),
    "null": re.compile(r"dereference failure: pointer NULL", re.I),
    "immutable_write": re.compile(r"write to constant", re.I),
    "immutable_write_observed": re.compile(r"write to constant", re.I),
}

CHECK_RE = re.compile(r"(?ms)^Check\s+(\d+):\s*(.+?)\n(.*?)(?=^Check\s+\d+:|\Z)")
SUMMARY_RE = re.compile(
    r"(?s)Manual Harness Summary:.*?Complete\s*-\s*(\d+) successfully verified harnesses,\s*(\d+) failures,\s*(\d+) total\."
)
COVER_RE = re.compile(r"\*\*\s*(\d+) of (\d+) cover properties satisfied")


def parse_checks(log: str) -> list[dict[str, str]]:
    checks = []
    for match in CHECK_RE.finditer(log):
        body = match.group(3)
        status_match = re.search(r"(?m)^\s*-\s*Status:\s*(\S+)", body)
        description_match = re.search(r"(?m)^\s*-\s*Description:\s*(.*)$", body)
        if not status_match:
            continue
        description = description_match.group(1).strip() if description_match else ""
        checks.append(
            {
                "check_number": match.group(1).strip(),
                "property_id": match.group(2).strip(),
                "status": status_match.group(1).strip().upper(),
                "message": description.strip('"'),
            }
        )
    return checks


def classify(control: str, exit_code: int, log: str) -> dict:
    if control not in CONTROLS:
        raise ValueError(f"unknown control: {control}")

    checks = parse_checks(log)
    failures = [check for check in checks if check["status"] in {"FAILURE", "FAILED"}]
    invalid_statuses = [
        check
        for check in checks
        if check["status"] not in {"SUCCESS", "UNREACHABLE", "SATISFIED", "FAILURE", "FAILED"}
        or (check["status"] == "SATISFIED" and ".cover." not in check["property_id"])
    ]
    summary_match = SUMMARY_RE.search(log)
    harness_summary = None
    if summary_match:
        harness_summary = {
            "verified": int(summary_match.group(1)),
            "failed": int(summary_match.group(2)),
            "total": int(summary_match.group(3)),
        }
    cover_match = COVER_RE.search(log)
    covers = (
        {"satisfied": int(cover_match.group(1)), "total": int(cover_match.group(2))}
        if cover_match
        else None
    )
    marker_match = re.search(r"(?m)^\s*VERIFICATION:-\s*(SUCCESSFUL|FAILED)\s*$", log)
    verification = marker_match.group(1) if marker_match else None
    reasons: list[str] = []

    compiler_error = re.search(
        r"(?im)^\s*(?:error(?:\[E\d+\])?:|could not compile|failed to compile)", log
    )
    missing_arguments = re.search(
        r"(?i)(?:not enough arguments|missing required arguments?|the following required arguments were not provided)",
        log,
    )
    bad_frontend = bool(compiler_error or missing_arguments)
    unsupported_failure = any(
        "unsupported" in (check["property_id"] + " " + check["message"]).lower()
        for check in failures
    )
    unwind_failure = any(
        "unwind" in check["property_id"].lower()
        or "unwinding assertion" in check["message"].lower()
        for check in failures
    )
    is_positive = CONTROLS[control] == "positive"
    category = CONTROLS[control]

    if bad_frontend:
        reasons.append("frontend/compiler/unsupported-operation diagnostic present")
    if unwind_failure:
        reasons.append("an unwinding assertion failed")

    if bad_frontend or unsupported_failure or unwind_failure or invalid_statuses or not checks or not harness_summary or not verification:
        if unsupported_failure:
            reasons.append("a failed unsupported check cannot count as detector evidence")
        if invalid_statuses:
            reasons.append(f"{len(invalid_statuses)} check block(s) had a non-accepted status")
        if not checks:
            reasons.append("no regular Kani check blocks were parsed")
        if not harness_summary:
            reasons.append("final manual harness summary missing")
        if not verification:
            reasons.append("final VERIFICATION marker missing")
        status = "inconclusive"
    elif harness_summary["total"] != 1:
        reasons.append("expected exactly one selected harness")
        status = "inconclusive"
    elif is_positive:
        if (
            exit_code == 0
            and verification == "SUCCESSFUL"
            and harness_summary == {"verified": 1, "failed": 0, "total": 1}
            and not failures
            and not invalid_statuses
            and checks
            and covers is not None
            and covers["total"] == 2
            and covers["satisfied"] == 2
        ):
            status = "positive_verified"
            reasons.append("positive read control verified with both covers satisfied")
        else:
            status = "positive_failed"
            reasons.append("positive control did not verify with exactly two satisfied covers")
    elif (
        control == "negative_immutable_static_write_observed"
        and exit_code == 0
        and verification == "SUCCESSFUL"
        and harness_summary == {"verified": 1, "failed": 0, "total": 1}
        and not failures
        and not invalid_statuses
        and checks
    ):
        if covers == {"satisfied": 1, "total": 1}:
            status = "detector_missing"
            reasons.append("the store was observed by the volatile load, but no immutable-write detector rejected it")
        else:
            status = "inconclusive"
            reasons.append(f"store observability was not established by its 1/1 cover: {covers!r}")
    elif (
        exit_code == 0
        and verification == "SUCCESSFUL"
        and harness_summary == {"verified": 1, "failed": 0, "total": 1}
        and not failures
        and not invalid_statuses
        and checks
    ):
        status = "detector_missing"
        reasons.append("negative control passed; intended UB detector did not reject it")
    elif (
        exit_code == 1
        and verification == "FAILED"
        and harness_summary == {"verified": 0, "failed": 1, "total": 1}
        and len(failures) >= 1
        and not invalid_statuses
        and checks
        and all(EXPECTED[category].search(check["message"]) for check in failures)
    ):
        status = "detected"
        reasons.append(f"all {len(failures)} failed properties match the expected {category} diagnostic")
    else:
        status = "inconclusive"
        if exit_code != 1:
            reasons.append(f"expected Kani exit code 1, got {exit_code}")
        if verification != "FAILED":
            reasons.append("final verification status was not FAILED")
        if harness_summary != {"verified": 0, "failed": 1, "total": 1}:
            reasons.append("expected exactly one failed selected harness")
        if not failures:
            reasons.append("expected at least one failed check block")
        elif not all(EXPECTED[category].search(check["message"]) for check in failures):
            reasons.append(f"one or more failed checks did not match expected {category} diagnostic")
        if unwind_failure:
            reasons.append("unwind failure cannot count as detector evidence")

    return {
        "control": control,
        "kind": CONTROLS[control],
        "classification": status,
        "store_observable": (
            control == "negative_immutable_static_write_observed"
            and covers == {"satisfied": 1, "total": 1}
        ),
        "process_exit": exit_code,
        "verification": verification,
        "harness_summary": harness_summary,
        "covers": covers,
        "checks": checks,
        "failed_checks": failures,
        "invalid_status_checks": invalid_statuses,
        "reasons": reasons,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--aggregate", action="store_true")
    parser.add_argument("--profile", choices=PROFILES, default="all")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--control")
    parser.add_argument("--exit-code", type=int)
    parser.add_argument("--log", type=Path)
    parser.add_argument("records", nargs="*", type=Path)
    args = parser.parse_args()

    if args.aggregate:
        records = [json.loads(path.read_text()) for path in args.records]
        expected_names = PROFILES[args.profile]
        by_name = {record["control"]: record for record in records}
        duplicate_names = sorted(
            name for name in by_name if sum(record["control"] == name for record in records) > 1
        )
        missing = [name for name in expected_names if name not in by_name]
        ordered = [by_name[name] for name in expected_names if name in by_name]
        successful = not missing and not duplicate_names and all(
            record["classification"] == ("positive_verified" if record["kind"] == "positive" else "detected")
            for record in ordered
        )
        result = {
            "suite": "ub-controls",
            "profile": args.profile,
            "expected_controls": expected_names,
            "validated": successful,
            "missing_records": missing,
            "duplicate_records": duplicate_names,
            "controls": ordered,
            "reasons": ["all positive and negative controls validated"]
            if successful
            else ["one or more controls were missing, inconclusive, or detector-missing"],
        }
        args.out.write_text(json.dumps(result, indent=2) + "\n")
        print(f"UB controls ({args.profile}): {'VALIDATED' if successful else 'NOT VALIDATED'} ({len(ordered)}/{len(expected_names)} records)")
        return 0 if successful else 1

    if not args.control or args.exit_code is None or args.log is None:
        parser.error("single-control mode requires --control, --exit-code, and --log")
    result = classify(args.control, args.exit_code, args.log.read_text(errors="replace"))
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(
        f"{result['control']}: {result['classification']} "
        f"(exit {result['process_exit']}; {len(result['failed_checks'])} failed checks)"
    )
    if result["classification"] in {"positive_verified", "detected"}:
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
