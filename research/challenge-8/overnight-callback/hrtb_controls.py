#!/usr/bin/env python3
"""Hosted-only isolated HRTB matcher controls; no callback proof claim."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import time

import probe


CASES = (
    "bool_match_off", "bool_match", "nonbool_rhs", "missing_projection",
    "wrong_f", "wrong_t", "unequal_lifetimes", "wrong_method_lifetime",
    "nonlifetime_method_arg", "shadowed_f", "shadowed_t",
    "duplicate_projection", "no_matching_trait",
    "second_unannotated", "second_body",
)
EXPECT_CALLS = {
    "bool_match_off": 1, "bool_match": 1, "nonbool_rhs": 1,
    "missing_projection": 1, "wrong_f": 1, "wrong_t": 1,
    "unequal_lifetimes": 1, "wrong_method_lifetime": 1,
    "nonlifetime_method_arg": 1,
    "shadowed_f": 1, "shadowed_t": 1, "duplicate_projection": 1,
    "no_matching_trait": 0, "second_unannotated": 2,
    "second_body": 2,
}
EXPECT_REGISTRATIONS = {
    "bool_match_off": 0, "bool_match": 1, "nonbool_rhs": 0,
    "missing_projection": 0, "wrong_f": 0, "wrong_t": 0,
    "unequal_lifetimes": 0, "wrong_method_lifetime": 0,
    "nonlifetime_method_arg": 0,
    "shadowed_f": 0, "shadowed_t": 0,
    "duplicate_projection": 0, "no_matching_trait": 0,
    "second_unannotated": 1, "second_body": 1,
}
SHADOW_CASES = {"shadowed_f", "shadowed_t"}
DECLARED_FUNCTIONS = {
    "second_body": ["first_body", "second_body"],
}
CALL_TRACE = re.compile(
    r"(?m)^CHALLENGE8_HRTB_CALL registered=([01]) "
    r"call=verified/lib\.rs\((\d+),[^\n]+$")
EQ_TRACE = re.compile(
    r"(?m)^CHALLENGE8_HRTB_EQ F=F T=T lifetime='cmp "
    r"call=verified/lib\.rs\((\d+),[^\n]+$")
TIMED_HEADER = re.compile(r"(?m)^\s*\d+(?:\.\d+)?s: "
                          r"verified/lib\.rs\([^)]*\): Verifying function '")
SHADOW_FATAL = ('Fatal error: exception Failure("CHALLENGE8_HRTB: '
                'local ghost type-scope certificate mismatch")')


def select_source(template: bytes, case: str) -> bytes:
    selected = "bool_match" if case == "bool_match_off" else case
    begin = f"// HRTB_BEGIN {selected}\n".encode()
    end = f"// HRTB_END {selected}\n".encode()
    all_begins = [f"// HRTB_BEGIN {name}\n".encode()
                  for name in CASES if name != "bool_match_off"]
    all_ends = [f"// HRTB_END {name}\n".encode()
                for name in CASES if name != "bool_match_off"]
    probe.need(all(template.count(marker) == 1
                   for marker in (*all_begins, *all_ends)),
               "HRTB template section missing or duplicated")
    start = template.index(begin) + len(begin)
    stop = template.index(end, start)
    first_case = min(template.index(marker) for marker in all_begins)
    source = template[:first_case] + template[start:stop]
    probe.need(source.count(b"pub unsafe fn ") ==
               len(DECLARED_FUNCTIONS.get(case, [selected])),
               "HRTB control function count changed")
    return source


def call_lines(source: bytes) -> list[int]:
    return [line for line, text in enumerate(source.decode().splitlines(), 1)
            if re.search(r"\bcompare(?:/\*@::<[^\n]*>@\*/)?\(left, right\)", text)]


def run_case(args: argparse.Namespace, case: str) -> dict:
    directory = args.evidence / case
    directory.mkdir(parents=True, exist_ok=False)
    (directory / "original").mkdir()
    (directory / "verified").mkdir()
    template_path = Path(__file__).with_name("hrtb-controls.rs")
    template = template_path.read_bytes()
    source = select_source(template, case)
    original = probe.strip_ghost(source)
    lines = call_lines(source)
    expected_source_calls = 1 if case == "no_matching_trait" else EXPECT_CALLS[case]
    probe.need(len(lines) == expected_source_calls,
               f"{case}: exact call line count changed")
    (directory / "verified/lib.rs").write_bytes(source)
    (directory / "original/lib.rs").write_bytes(original)
    profile = probe.source_certificate(args.repo_root, args.source_checkout,
                                       args.tool_home)
    record = {
        **profile,
        "case": case,
        "classification": "PREPARED_MATCHER_CONTROL",
        "template_sha256": probe.sha(template),
        "verified_sha256": probe.sha(source),
        "original_sha256": probe.sha(original),
        "ghost_strip_exact": probe.strip_ghost(source) == original,
        "call_lines": lines,
        "expected_fnmut_calls": EXPECT_CALLS[case],
        "expected_registrations": EXPECT_REGISTRATIONS[case],
        "predeclared_functions": DECLARED_FUNCTIONS.get(
            case, ["bool_match" if case == "bool_match_off" else case]),
        "hrtb_output_opt_in": case != "bool_match_off",
        "actual_sort4_proved": False,
        "full_callback_proved": False,
        "classification_limit": "translator matcher control, not an ownership proof",
    }
    (directory / "fixture.json").write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n")
    if args.prepare_only:
        return record

    hashes = {"verified/lib.rs": record["verified_sha256"],
              "original/lib.rs": record["original_sha256"]}
    environment = os.environ.copy()
    environment["PATH"] = (str(args.tool_home / "bin") + os.pathsep +
                           environment.get("PATH", ""))
    environment.pop("SORT4_HRTB_OUTPUT", None)
    environment.pop("SORT4_HRTB_OUTPUT_TARGETS", None)
    for key in ("SORT4_MAYBEUNINIT_REPO_ROOT", "SORT4_SELECT_INTRINSIC_REPO_ROOT",
                "SORT4_POINTER_DROP_REPO_ROOT", "SORT4_MAYBEUNINIT_NEW_REPO_ROOT"):
        environment.pop(key, None)
    stages: dict[str, dict] = {}

    def execute(name: str, argv: list[str], cap: int,
                stdin_name: str | None = None,
                stdout_name: str | None = None,
                opt_in: bool = False) -> dict:
        remaining = args.deadline_epoch - int(time.time())
        seconds = min(cap, remaining - 10) if remaining > 10 else None
        if seconds is None:
            return {"exit": None, "skipped": "artifact and cleanup reserve"}
        stage_env = environment.copy()
        if opt_in:
            stage_env["SORT4_HRTB_OUTPUT"] = "1"
            stage_env["SORT4_HRTB_OUTPUT_TARGETS"] = ",".join(
                record["predeclared_functions"])
        return probe.run_stage(name, argv, directory, stage_env, hashes,
                               seconds, stdin_name, stdout_name)

    exporter = str(args.tool_home / "bin/vf-rust-mir-exporter")
    for mode in ("normal", "readonly"):
        switches = (["--vf-rust-mir-exporter:preprocess-readonly"]
                    if mode == "readonly" else [])
        stages[f"{mode}-export"] = execute(
            f"{mode}-export",
            [exporter, "verified/lib.rs", f"--sysroot={args.compiler_sysroot}",
             "--edition", "2021", *switches],
            90, stdout_name=f"{mode}-mir.bin")
        if stages[f"{mode}-export"]["exit"] == 0:
            stages[f"{mode}-decode"] = execute(
                f"{mode}-decode",
                ["capnp", "decode", str(args.schema), "VfMir"],
                60, f"{mode}-mir.bin", f"{mode}-mir.txt")
        else:
            stages[f"{mode}-decode"] = {
                "exit": None, "skipped": f"{mode} export failed"}

    stages["full-verification"] = execute(
        "full-verification",
        [str(args.tool_home / "bin/verifast"), "-rustc_args", "--edition 2021",
         "-verbose", "1", "verified/lib.rs"],
        180, opt_in=case != "bool_match_off")
    stages["refinement"] = execute(
        "refinement",
        [str(args.tool_home / "bin/refinement-checker"), "--rustc-args",
         "--edition 2021", "original/lib.rs", "verified/lib.rs"], 90)

    full_log_path = directory / "full-verification.log"
    full_log = full_log_path.read_text(errors="replace") \
        if full_log_path.is_file() else ""
    call_trace = [(int(registered), int(line))
                  for registered, line in CALL_TRACE.findall(full_log)]
    eq_trace = [int(line) for line in EQ_TRACE.findall(full_log)]
    fatal_lines = [line for line in full_log.splitlines()
                   if line.startswith("Fatal error:")]
    errors = [line for line in full_log.splitlines() if ": error:" in line]
    normal_mir_path = directory / "normal-mir.txt"
    normal_mir = normal_mir_path.read_text(errors="replace") \
        if normal_mir_path.is_file() else ""
    mir_calls = normal_mir.count('name = "core::ops::FnMut::call_mut"')
    projection_count = normal_mir.count(
        'defId = "core::ops::FnOnce::Output"')
    fnmut_trait_count = normal_mir.count('defId = "core::ops::FnMut"')
    clause_shape_ok = (
        (projection_count == 0 and fnmut_trait_count == 1)
        if case == "missing_projection" else
        (projection_count >= 2 and fnmut_trait_count >= 1)
        if case == "duplicate_projection" else
        (projection_count >= 1 and fnmut_trait_count == 0)
        if case == "no_matching_trait" else
        (projection_count == 2 and fnmut_trait_count == 2)
        if case == "second_body" else
        (projection_count == 1 and fnmut_trait_count == 1))
    support = all(stages[name].get("exit") == 0 for name in (
        "normal-export", "normal-decode", "readonly-export",
        "readonly-decode", "refinement"))
    source_exact = all(stage.get("source_exact") is True
                       for stage in stages.values() if "source_exact" in stage)
    trace_expected = ([1 if line == lines[0] else 0 for line in lines]
                      if case in {"bool_match", "second_unannotated",
                                  "second_body"} else
                      [0 for _ in lines])
    expected_trace = list(zip(trace_expected, lines))
    classification = "INCONCLUSIVE"
    if case in SHADOW_CASES:
        if support and source_exact and mir_calls == 1 and \
                clause_shape_ok and \
                stages["full-verification"]["exit"] == 2 and \
                fatal_lines == [SHADOW_FATAL] and not errors and \
                not call_trace and not eq_trace:
            classification = "INTENDED_LOCAL_TYPE_SCOPE_ADMISSION_REJECTION"
    elif case == "duplicate_projection" and support and source_exact and \
            projection_count < 2:
        classification = "INCONCLUSIVE_DUPLICATE_NOT_EXPORTED"
    elif support and source_exact and clause_shape_ok and \
            mir_calls == EXPECT_CALLS[case] and \
            stages["full-verification"]["exit"] == 1 and not fatal_lines and \
            TIMED_HEADER.search(full_log) is not None and len(errors) == 1 and \
            ("No matching heap chunks" in errors[0] or
             "Type mismatch" in errors[0]) and \
            call_trace == ([] if case in {"bool_match_off", "no_matching_trait"}
                           else expected_trace) and \
            eq_trace == ([] if case in {"bool_match_off", "no_matching_trait"} else
                         [line for reg, line in expected_trace if reg == 1]):
        classification = "MATCHER_CONTROL_EXPECTED_TRACE_ONLY"
    result = {
        **record,
        "classification": classification,
        "accepted_hrtb_component": False,
        "support_exports_decode_refinement_all_zero": support,
        "source_integrity": source_exact,
        "mir_fnmut_calls": mir_calls,
        "mir_fn_once_output_projections": projection_count,
        "mir_fnmut_trait_clauses": fnmut_trait_count,
        "mir_clause_shape_expected": clause_shape_ok,
        "call_trace": call_trace,
        "equality_trace_lines": eq_trace,
        "first_error": errors[0] if errors else None,
        "fatal_lines": fatal_lines,
        "stages": stages,
    }
    (directory / "outcome.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"case": case, "classification": classification,
                      "first_error": result["first_error"],
                      "call_trace": call_trace,
                      "equality_trace_lines": eq_trace},
                     sort_keys=True), flush=True)
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
    probe.need(args.schema.is_file() and args.source_checkout.is_dir() and
               args.tool_home.is_dir(), "pinned tool/source inputs missing")
    args.evidence.mkdir(parents=True, exist_ok=False)
    names = CASES if args.case == "all" else (args.case,)
    outcomes = {}
    for name in names:
        if not args.prepare_only and args.deadline_epoch - int(time.time()) <= 15:
            outcomes[name] = {"classification": "NOT_RUN",
                              "reason": "artifact and cleanup reserve"}
        else:
            outcomes[name] = run_case(args, name)
    summary = {
        "cases": outcomes,
        "all_accepted": False,
        "actual_sort4_proved": False,
        "full_callback_proved": False,
    }
    (args.evidence / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
