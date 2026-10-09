#!/usr/bin/env python3
"""Classify O26 Cloud evidence without promoting diagnostics to a proof."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re


BASELINE_SOURCE = "8629849c2d2ddde1eeb90fadb6a151dc52e626385578f89f0d86fce842c61eb8"
BASELINE_SHA = "c19e4c50470d32199178d5229a2819554fc6b2f1"
SHADOW_LOCATION = re.compile(r"verified/lib\.rs\(198,\s*77-82\)")
STALE_REASON = "certificate mismatch: owner exact verified source SHA256"


def read(path: Path):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return None


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def case_audit(ev: Path, label: str) -> dict:
    root = ev / "cases" / label
    summary = read(root / "capture/summary.json")
    proof = read(root / "proof-stage.json")
    if summary is None or proof is None:
        return {"complete": False, "reason": "capture or proof stage missing"}
    case = root / "capture/nine-body-a1-owned-forget"
    source = summary.get("source", {})
    full = summary.get("full_body_capture", {})
    files_ok = True
    for mode in ("normal", "readonly"):
        part = full.get(mode, {})
        whole = case / part.get("whole_decoded_mir_file", "missing")
        files_ok &= (whole.is_file() and
                     digest(whole) == part.get("whole_decoded_mir_sha256"))
        bodies = part.get("bodies", [])
        files_ok &= len(bodies) == 9
        for index, row in enumerate(bodies):
            path = case / row.get("file", "missing")
            files_ok &= (row.get("index") == index and path.is_file() and
                         digest(path) == row.get("sha256") and
                         row.get("bytes", 0) > 0)
    fingerprint = summary.get("fingerprint") or {}
    snaps = fingerprint.get("snapshots", {})
    files_ok &= set(snaps) == {"unit", *(f"body-{n}" for n in range(9))}
    for row in snaps.values():
        path = case / row.get("file", "missing")
        files_ok &= (path.is_file() and digest(path) == row.get("sha256") and
                     path.stat().st_size == row.get("bytes") and row.get("bytes", 0) > 0)
    source_ok = (summary.get("frontend_refinement_and_full_body_capture") is True and
                 source.get("ghost_strip_identity") is True and
                 (case / "original/lib.rs").is_file() and
                 (case / "verified/lib.rs").is_file() and
                 digest(case / "original/lib.rs") == source.get("original_sha256") and
                 digest(case / "verified/lib.rs") == source.get("verified_sha256"))
    stage = proof.get("stage", {})
    log = case / ("historical-proof.log" if label == "baseline" else
                  "stale-certificate.log")
    text = log.read_text(errors="replace") if log.is_file() else ""
    if label == "baseline":
        expected = (proof.get("proof_sha") == BASELINE_SHA and
                    source.get("verified_sha256") == BASELINE_SOURCE and
                    "Verifying function 'select_unpredictable'" in text and
                    SHADOW_LOCATION.search(text) is not None and
                    "DropOnPanic" in text and "Element" in text and
                    STALE_REASON not in text)
        classification = "HISTORICAL_GUARD_SHADOW_REPRODUCED" if expected else "INCONCLUSIVE_BASELINE"
    else:
        expected = (source.get("verified_sha256") != BASELINE_SOURCE and
                    STALE_REASON in text and
                    "SORT4-ACTUAL-OWNER-NINE: exact source and complete decoded MIR admission only" not in text)
        classification = "STALE_CERTIFICATE_REJECTED" if expected else "INCONCLUSIVE_STALE_GATE"
    complete = (source_ok and files_ok and
                fingerprint.get("classification") ==
                    "INTENDED_DIAGNOSTIC_REFUSAL_NO_PROOF_RULE" and
                stage.get("source_unchanged") is True and
                stage.get("exit") not in (None, 0, 124, 137) and expected)
    return {
        "complete": complete, "classification": classification,
        "source_mir_refinement_complete": source_ok,
        "nine_bodies_each_mode_and_ten_marshal_snapshots": files_ok,
        "fingerprint_classification": fingerprint.get("classification"),
        "verified_source_sha256": source.get("verified_sha256"),
        "original_source_sha256": source.get("original_sha256"),
        "proof_exit": stage.get("exit"),
        "expected_first_obligation": expected,
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--evidence", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--runner-exit", type=int, required=True)
    p.add_argument("--failed-stage", required=True)
    args = p.parse_args()
    ev = args.evidence
    baseline = case_audit(ev, "baseline")
    candidate = case_audit(ev, "candidate")
    profile = read(ev / "profile-hashes.json")
    original_equal = (baseline.get("original_source_sha256") is not None and
                      baseline.get("original_source_sha256") ==
                          candidate.get("original_source_sha256"))
    complete = (args.runner_exit == 0 and baseline.get("complete") is True and
                candidate.get("complete") is True and profile is not None and
                original_equal)
    console_equal = profile.get("console_byte_identical") if profile else None
    record = {
        "lane": "o26", "classification":
            ("DIAGNOSTIC_COMPLETE_BYTE_IDENTICAL_PROFILE" if console_equal else
             "DIAGNOSTIC_COMPLETE_REBUILT_PROFILE") if complete else "INCONCLUSIVE",
        "diagnostic_complete": complete,
        "verification_accepted": False,
        "accepted": False,
        "actual_helper_proved": False,
        "candidate_certificate_refreshed": False,
        "baseline": baseline, "candidate": candidate,
        "runtime_original_equal": original_equal,
        "profile_hashes_available": profile is not None,
        "console_byte_identical_to_historical": console_equal,
        "runner_exit": args.runner_exit, "failed_stage": args.failed_stage,
        "evidence_root": "allprooflogs",
    }
    args.output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: record[k] for k in (
        "classification", "diagnostic_complete", "verification_accepted")}), flush=True)


if __name__ == "__main__":
    main()
