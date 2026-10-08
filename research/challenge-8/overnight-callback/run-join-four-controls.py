#!/usr/bin/env python3
"""Hosted-only ordinary join-four lemma and resource controls."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import time

import probe


HERE = Path(__file__).resolve().parent
CASES = ("positive", "missing_owner", "duplicate_owner", "wrong_cell")
FUNCTION = b"pub unsafe fn join_four_control<T, F>("
PRE_THIRD = b"    *(base + 2) |-> ?x2 &*& <T>.own(t, x2) &*&\n"
POST_F = b"    *is_less |-> f &*& <F>.own(t, f);\n"
JOIN_CALL = b"    //@ join_four_owned_cells::<T>(base, t);\n"
TIMED_HEADER = re.compile(
    r"(?m)^\s*\d+(?:\.\d+)?s: verified/lib\.rs\([^)]*\): "
    r"Verifying function 'join_four_control'")


def need(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)


def prepared_source(case: str) -> bytes:
    template = (HERE / "join-four-control.rs").read_bytes()
    lemma = (HERE / "join-four-owned-cells.rs").read_bytes()
    need(template.count(FUNCTION) == 1 and
         template.count(PRE_THIRD) == 1 and
         template.count(POST_F) == 1 and
         template.count(JOIN_CALL) == 1 and
         lemma.count(b"lem join_four_owned_cells<T>(") == 1,
         "join-four control template changed shape")
    if case == "missing_owner":
        template = template.replace(
            PRE_THIRD, b"    *(base + 2) |-> ?x2 &*&\n", 1)
    elif case == "duplicate_owner":
        template = template.replace(
            POST_F, b"    *is_less |-> f &*& <F>.own(t, f) &*&\n"
            b"    <T>.own(t, x0);\n", 1)
    elif case == "wrong_cell":
        template = template.replace(
            JOIN_CALL, b"    //@ join_four_owned_cells::<T>(base + 1, t);\n", 1)
    else:
        need(case == "positive", "unknown join-four control")
    return template.replace(FUNCTION, lemma + b"\n" + FUNCTION, 1)


def run_case(args: argparse.Namespace, case: str) -> dict:
    directory = args.evidence / case
    need(not directory.exists(), f"refusing to overwrite join-four case: {case}")
    (directory / "original").mkdir(parents=True)
    (directory / "verified").mkdir()
    source = prepared_source(case)
    original = probe.strip_ghost(source)
    positive_original = probe.strip_ghost(prepared_source("positive"))
    need(original == positive_original,
         f"{case}: resource control changed the runtime source")
    (directory / "verified/lib.rs").write_bytes(source)
    (directory / "original/lib.rs").write_bytes(original)
    profile = probe.source_certificate(args.repo_root, args.source_checkout,
                                       args.tool_home)
    record = {
        **profile,
        "case": case,
        "classification": "PREPARED_UNVERIFIED_JOIN_FOUR_CONTROL",
        "actual_sort4_proved": False,
        "ordinary_lemma_source_sha256": probe.sha(
            (HERE / "join-four-owned-cells.rs").read_bytes()),
        "verified_sha256": probe.sha(source),
        "original_sha256": probe.sha(original),
        "runtime_source_same_as_positive": True,
        "expected_obligation": {
            "positive": "ordinary lemma body, caller post and leak all pass",
            "missing_owner": "join_four_owned_cells precondition: third T.own",
            "duplicate_owner": "caller post: extra first T.own",
            "wrong_cell": "join_four_owned_cells precondition: fifth cell",
        }[case],
        "expected_stage": "full-verification",
    }
    (directory / "fixture.json").write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n")
    if args.prepare_only:
        return record

    hashes = {"original/lib.rs": record["original_sha256"],
              "verified/lib.rs": record["verified_sha256"]}
    environment = os.environ.copy()
    environment["PATH"] = (str(args.tool_home / "bin") + os.pathsep +
                           environment.get("PATH", ""))
    for key in ("SORT4_HRTB_OUTPUT", "SORT4_HRTB_OUTPUT_TARGETS",
                "SORT4_STRICT_LFT_CUT", "SORT4_CALLBACK_UNWIND"):
        environment.pop(key, None)
    stages: dict[str, dict] = {}

    def execute(name: str, argv: list[str], cap: int,
                stdin_name: str | None = None,
                stdout_name: str | None = None) -> dict:
        remaining = args.deadline_epoch - int(time.time())
        seconds = min(cap, remaining - 10) if remaining > 10 else None
        if seconds is None:
            return {"exit": None, "skipped": "artifact and cleanup reserve"}
        return probe.run_stage(name, argv, directory, environment, hashes,
                               seconds, stdin_name, stdout_name)

    exporter = str(args.tool_home / "bin/vf-rust-mir-exporter")
    for mode in ("normal", "readonly"):
        switches = (["--vf-rust-mir-exporter:preprocess-readonly"]
                    if mode == "readonly" else [])
        stages[f"{mode}-export"] = execute(
            f"{mode}-export",
            [exporter, "verified/lib.rs", f"--sysroot={args.compiler_sysroot}",
             "--edition", "2021", *switches], 90,
            stdout_name=f"{mode}-mir.bin")
        if stages[f"{mode}-export"]["exit"] == 0:
            stages[f"{mode}-decode"] = execute(
                f"{mode}-decode", ["capnp", "decode", str(args.schema), "VfMir"],
                60, f"{mode}-mir.bin", f"{mode}-mir.txt")
        else:
            stages[f"{mode}-decode"] = {
                "exit": None, "skipped": f"{mode} export failed"}
    stages["full-verification"] = execute(
        "full-verification",
        [str(args.tool_home / "bin/verifast"), "-rustc_args", "--edition 2021",
         "-verbose", "1", "verified/lib.rs"], 180)
    stages["refinement"] = execute(
        "refinement",
        [str(args.tool_home / "bin/refinement-checker"), "--rustc-args",
         "--edition 2021", "original/lib.rs", "verified/lib.rs"], 90)
    log_path = directory / "full-verification.log"
    log = log_path.read_text(errors="replace") if log_path.is_file() else ""
    errors = [line for line in log.splitlines() if ": error:" in line]
    fatal = [line for line in log.splitlines()
             if line.startswith("Fatal error:")]
    support = all(stages[name].get("exit") == 0 for name in (
        "normal-export", "normal-decode", "readonly-export",
        "readonly-decode", "refinement"))
    source_exact = all(row.get("source_exact") is True
                       for row in stages.values() if "source_exact" in row)
    if case == "positive" and support and source_exact and \
            stages["full-verification"].get("exit") == 0 and \
            not errors and not fatal and TIMED_HEADER.search(log) and \
            "0 errors found" in log and "Leak check." in log:
        classification = "JOIN_FOUR_POSITIVE_CANDIDATE_REVIEW_REQUIRED"
    elif case != "positive" and support and source_exact and \
            stages["full-verification"].get("exit") == 1 and \
            not fatal and TIMED_HEADER.search(log) and len(errors) == 1:
        classification = "JOIN_FOUR_NEGATIVE_CANDIDATE_REVIEW_REQUIRED"
    else:
        classification = "INCONCLUSIVE"
    result = {
        **record,
        "classification": classification,
        "support_exports_decode_refinement_all_zero": support,
        "source_integrity": source_exact,
        "first_error": errors[0] if errors else None,
        "fatal_lines": fatal,
        "stages": stages,
    }
    (directory / "outcome.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"case": case, "classification": classification,
                      "first_error": result["first_error"]}, sort_keys=True),
          flush=True)
    return result


def main() -> None:
    probe.hosted_only()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--source-checkout", type=Path, required=True)
    parser.add_argument("--tool-home", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--compiler-sysroot", required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--deadline-epoch", type=int, required=True)
    parser.add_argument("--case", choices=(*CASES, "all"), default="all")
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()
    for attr in ("repo_root", "source_checkout", "tool_home", "schema",
                 "evidence"):
        setattr(args, attr, getattr(args, attr).resolve())
    need(args.schema.is_file() and args.source_checkout.is_dir() and
         args.tool_home.is_dir(), "pinned hosted inputs missing")
    need(not args.evidence.exists(), "refusing to overwrite join-four evidence")
    args.evidence.mkdir(parents=True)
    names = CASES if args.case == "all" else (args.case,)
    outcomes = {name: run_case(args, name) for name in names}
    if "positive" in outcomes and outcomes["positive"]["classification"] != \
            "JOIN_FOUR_POSITIVE_CANDIDATE_REVIEW_REQUIRED":
        for name in names:
            if name != "positive" and "stages" in outcomes[name]:
                outcomes[name]["classification"] = "INCONCLUSIVE_POSITIVE_SETUP"
                (args.evidence / name / "outcome.json").write_text(
                    json.dumps(outcomes[name], indent=2, sort_keys=True) + "\n")
    if "positive" not in outcomes:
        for name in names:
            if "stages" in outcomes[name]:
                outcomes[name]["classification"] = "INCONCLUSIVE_NO_POSITIVE_BASELINE"
                (args.evidence / name / "outcome.json").write_text(
                    json.dumps(outcomes[name], indent=2, sort_keys=True) + "\n")
    (args.evidence / "summary.json").write_text(json.dumps({
        "cases": outcomes,
        "all_accepted": False,
        "actual_sort4_proved": False,
    }, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
