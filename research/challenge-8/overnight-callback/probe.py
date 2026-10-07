#!/usr/bin/env python3
"""Generate and run the one-call callback diagnostic on GitHub-hosted Linux."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time


PROFILE_SOURCE = "f76012fb518703b1d98e243ac4f487f16877cfcb"
SMALLSORT_SHA256 = "85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1"
STOCK_FNMUT_SHA256 = "599abd73bc551804b41f2d82aeb9c4a42d4c1c2b40396cbabfb2099c0abe1564"
SOURCE_CALL = b"is_less(&*v_base.add(1), &*v_base);"
CASES = ("callback_positive", "callback_false_post")
GHOST_BLOCK = re.compile(rb"/\*@.*?@\*/", re.S)
GHOST_LINE = re.compile(rb"(?m)^[ \t]*//@[^\r\n]*(?:\r?\n|$)")


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hosted_only() -> None:
    need(os.environ.get("GITHUB_ACTIONS") == "true" and
         os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted" and
         os.environ.get("RUNNER_OS") == "Linux",
         "callback probe is hosted-only (GitHub-hosted Linux required)")


def strip_ghost(data: bytes) -> bytes:
    data = GHOST_BLOCK.sub(b"", data)
    return GHOST_LINE.sub(b"", data)


def source_certificate(repo_root: Path, source_checkout: Path,
                       tool_home: Path) -> dict:
    source = repo_root / "library/core/src/slice/sort/shared/smallsort.rs"
    source_bytes = source.read_bytes()
    need(sha(source_bytes) == SMALLSORT_SHA256,
         "pinned SmallSort 26.10 source hash differs")
    need(source_bytes.count(SOURCE_CALL) == 1,
         "actual first comparator call is missing or ambiguous")

    vf_head = subprocess.run(
        ["git", "-C", str(source_checkout), "rev-parse", "HEAD"],
        check=True, capture_output=True, text=True).stdout.strip()
    need(vf_head == PROFILE_SOURCE,
         f"VeriFast source base differs: {vf_head}")
    effective_specs = tool_home / "bin/rust/std/lib.rsspec"
    effective_bytes = effective_specs.read_bytes()
    start_anchor = b"    trait FnMut<Args> {"
    end_anchor = b"    trait Fn<Args> {"

    def fnmut_clause(data: bytes) -> bytes:
        start = data.find(start_anchor)
        end = data.find(end_anchor, start + len(start_anchor))
        need(start >= 0 and end > start,
             "cannot locate the stock FnMut contract")
        return data[start:end]

    clause = fnmut_clause(effective_bytes)
    need(sha(clause) == STOCK_FNMUT_SHA256,
         "active profile changed the pinned stock FnMut contract")
    need(b"<Args>.own(t, args)" in clause and
         b"<Self>.own(t, self0)" in clause and
         b"<Self>.own(t, self1)" in clause and
         b"on_unwind_ens thread_token(t)" in clause,
         "stock FnMut resource contract shape differs")
    return {
        "classification": "SOURCE_BOUND_CALLBACK_DIAGNOSTIC",
        "proof_sha": subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
            check=True, capture_output=True, text=True).stdout.strip(),
        "verifast_source_base": vf_head,
        "small_sort_source": str(source.relative_to(repo_root)),
        "small_sort_sha256": sha(source_bytes),
        "actual_first_call": SOURCE_CALL.decode(),
        "stock_fnmut_clause_sha256": STOCK_FNMUT_SHA256,
        "active_fnmut_clause_matches_stock": True,
        "tool_home_fnmut_spec_sha256": sha(effective_bytes),
        "predeclared_functions": ["callback_positive", "callback_false_post"],
        "trusted_boundary": "stock 26.10 FnMut contract and compiler/source correspondence",
        "actual_sort4_proved": False,
    }


def select_case(template: bytes, name: str) -> bytes:
    begin = f"// CASE_BEGIN {name}\n".encode()
    end = f"// CASE_END {name}\n".encode()
    need(template.count(begin) == 1 and template.count(end) == 1,
         f"fixture case markers for {name} are missing or duplicated")
    start = template.index(begin) + len(begin)
    stop = template.index(end, start)
    need(stop > start, f"fixture case {name} is empty")
    return template[:template.index(begin)] + template[start:stop]


def generate_case(repo_root: Path, source_checkout: Path, tool_home: Path,
                  case_name: str, destination: Path) -> dict:
    need(case_name in CASES, f"unknown fixture case: {case_name}")
    template_path = Path(__file__).with_name("callback-cases.rs")
    template = template_path.read_bytes()
    selected = select_case(template, case_name)
    original = strip_ghost(selected)
    need(strip_ghost(selected) == original,
         "verified fixture does not strip to its original source")
    need(selected.count(b"pub unsafe fn " + case_name.encode()) == 1 and
         selected.count(b"is_less/*@::<F, (&'cmp T, &'cmp T), 'cmp>@*/(&*left, &*right)") == 1,
         "selected fixture is not a single exact generic callback call")
    need(original.count(b"is_less(&*left, &*right)") == 1,
         "ghost-free fixture call expression differs")

    destination.mkdir(parents=True, exist_ok=False)
    (destination / "original").mkdir()
    (destination / "verified").mkdir()
    (destination / "original/lib.rs").write_bytes(original)
    (destination / "verified/lib.rs").write_bytes(selected)
    record = source_certificate(repo_root, source_checkout, tool_home)
    target_contract_lines = [
        n for n, line in enumerate(selected.decode().splitlines(), 1)
        if case_name == "callback_false_post" and
        "ens " in line and "false;" in line
    ]
    if case_name == "callback_false_post":
        need(len(target_contract_lines) == 1,
             "false-post target line missing or ambiguous")
    record.update({
        "case": case_name,
        "template_sha256": sha(template),
        "verified_sha256": sha(selected),
        "original_sha256": sha(original),
        "ghost_strip_exact": strip_ghost(selected) == original,
        "target_function_count": 1,
        "actual_callback_call_count": 1,
        "expected_false_post_line": target_contract_lines[0]
            if target_contract_lines else None,
        "domain": "generic sized T and F: FnMut(&T, &T) -> bool; two separated initialized slots",
        "normal_post": "current full T resources for both slots and current F resource; unconstrained bool",
        "unwind_post": "current full T resources for both slots and current F resource; no result or rollback",
        "proof_premises": [],
        "effective_patches": "provided common O2/O3 tool profile; FnMut contract must remain stock",
    })
    (destination / "fixture.json").write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n")
    return record


def run_stage(name: str, argv: list[str], root: Path, env: dict[str, str],
              source_hashes: dict[str, str], timeout_seconds: int,
              stdin_name: str | None = None,
              stdout_name: str | None = None) -> dict:
    paths = {rel: root / rel for rel in source_hashes}
    before = {rel: sha(path.read_bytes()) for rel, path in paths.items()}
    need(before == source_hashes,
         f"source differs before stage {name}")
    stdout_path = root / (stdout_name or f"{name}.log")
    stderr_path = root / f"{name}-stderr.log" if stdout_name else stdout_path
    with stdout_path.open("wb") as stdout:
        stderr = stderr_path.open("wb") if stderr_path != stdout_path else subprocess.STDOUT
        try:
            stdin = (root / stdin_name).open("rb") if stdin_name else open(os.devnull, "rb")
            try:
                status = subprocess.run(
                    ["/usr/bin/time", "-v", "-o", str(root / f"{name}-resources.txt"),
                     "timeout", "--signal=TERM", "--kill-after=10s",
                     f"{timeout_seconds}s", *argv],
                    cwd=root, env=env, stdin=stdin, stdout=stdout, stderr=stderr,
                    check=False).returncode
            finally:
                stdin.close()
        except OSError as exc:
            status = 127
            (stderr if stderr_path != stdout_path else stdout).write(
                f"stage launch error: {exc}\n".encode())
        finally:
            if stderr_path != stdout_path:
                stderr.close()
    after = {rel: sha(path.read_bytes()) for rel, path in paths.items()}
    record = {
        "argv": argv, "exit": status, "timeout_seconds": timeout_seconds,
        "source_before": before, "source_after": after,
        "source_exact": before == after == source_hashes,
        "stdout": stdout_path.name, "stderr": stderr_path.name,
    }
    (root / f"{name}-stage.json").write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n")
    return record


def run_case(repo_root: Path, source_checkout: Path, tool_home: Path,
             schema: Path, compiler_sysroot: str, evidence: Path,
             case_name: str, deadline_epoch: int) -> dict:
    case_dir = evidence / case_name
    fixture = generate_case(repo_root, source_checkout, tool_home,
                            case_name, case_dir)
    hash_tool = lambda path: sha(path.read_bytes())
    compiler = subprocess.run(
        ["rustc", "--version", "--verbose"], check=True,
        capture_output=True, text=True).stdout
    fixture["hosted_profile"] = {
        "compiler_version_verbose": compiler,
        "tool_hashes": {
            name: hash_tool(tool_home / "bin" / name)
            for name in ("verifast", "vf-rust-mir-exporter", "refinement-checker")
        },
        "schema_sha256": hash_tool(schema),
        "effective_fnmut_contract_sha256": sha(
            (tool_home / "bin/rust/std/lib.rsspec").read_bytes()),
    }
    (case_dir / "fixture.json").write_text(
        json.dumps(fixture, indent=2, sort_keys=True) + "\n")
    source_hashes = {
        "original/lib.rs": fixture["original_sha256"],
        "verified/lib.rs": fixture["verified_sha256"],
    }
    env = os.environ.copy()
    for key in ("SORT4_MAYBEUNINIT_REPO_ROOT", "SORT4_SELECT_INTRINSIC_REPO_ROOT",
                "SORT4_POINTER_DROP_REPO_ROOT", "SORT4_MAYBEUNINIT_NEW_REPO_ROOT"):
        env.pop(key, None)
    env["PATH"] = str(tool_home / "bin") + os.pathsep + env.get("PATH", "")
    stages: dict[str, dict] = {}

    def stage_budget(cap: int) -> int | None:
        remaining = deadline_epoch - int(time.time())
        return min(cap, remaining - 10) if remaining > 10 else None

    def execute(name: str, argv: list[str], cap: int,
                stdin_name: str | None = None,
                stdout_name: str | None = None) -> dict:
        seconds = stage_budget(cap)
        if seconds is None:
            return {"exit": None, "skipped": "artifact and cleanup reserve"}
        return run_stage(name, argv, case_dir, env, source_hashes, seconds,
                         stdin_name, stdout_name)

    exporter = str(tool_home / "bin/vf-rust-mir-exporter")
    stages["normal-export"] = execute(
        "normal-export", [exporter, "verified/lib.rs",
                          f"--sysroot={compiler_sysroot}", "--edition", "2021"],
        90, stdout_name="normal-mir.bin")
    if stages["normal-export"]["exit"] == 0:
        stages["normal-decode"] = execute(
            "normal-decode", ["capnp", "decode", str(schema), "VfMir"],
            60, "normal-mir.bin", "normal-mir.txt")
    else:
        stages["normal-decode"] = {"exit": None, "skipped": "normal export failed"}

    stages["readonly-export"] = execute(
        "readonly-export", [exporter, "verified/lib.rs",
                            f"--sysroot={compiler_sysroot}", "--edition", "2021",
                            "--vf-rust-mir-exporter:preprocess-readonly"],
        90, stdout_name="readonly-mir.bin")
    if stages["readonly-export"]["exit"] == 0:
        stages["readonly-decode"] = execute(
            "readonly-decode", ["capnp", "decode", str(schema), "VfMir"],
            60, "readonly-mir.bin", "readonly-mir.txt")
    else:
        stages["readonly-decode"] = {"exit": None, "skipped": "readonly export failed"}

    verifier_argv = [str(tool_home / "bin/verifast"),
                     "-rustc_args", "--edition 2021", "-verbose", "1",
                     "-dump_ast_with_locs", "verified-ast.txt", "verified/lib.rs"]
    stages["full-verification"] = execute(
        "full-verification", verifier_argv, 180)
    stages["refinement"] = execute(
        "refinement", [str(tool_home / "bin/refinement-checker"),
                       "--rustc-args", "--edition 2021",
                       "original/lib.rs", "verified/lib.rs"], 90)

    full_log_path = case_dir / "full-verification.log"
    full_log = full_log_path.read_text(errors="replace") if full_log_path.is_file() else ""
    target_headers = re.findall(
        rf"(?m)^\s*\d+(?:\.\d+)?s: verified/lib\.rs\([^)]*\): Verifying function '{re.escape(case_name)}'",
        full_log)
    errors = [line for line in full_log.splitlines() if ": error:" in line]
    source_integrity = all(
        row.get("source_exact") is True for row in stages.values()
        if "source_exact" in row)
    support_stages = ("normal-export", "normal-decode", "readonly-export",
                      "readonly-decode", "refinement")
    support_ok = all(stages.get(name, {}).get("exit") == 0 for name in support_stages)
    classification = "INCONCLUSIVE"
    intended_negative = False
    if case_name == "callback_false_post" and support_ok and source_integrity and \
            stages["full-verification"]["exit"] == 1 and len(target_headers) == 1 and \
            len(errors) == 1:
        line = fixture["expected_false_post_line"]
        intended_negative = any(
            "Cannot prove false" in error and
            re.search(rf"verified/lib\.rs\({line},", error) is not None
            for error in errors)
        if intended_negative:
            classification = "INTENDED_FALSE_NORMAL_POST"
    if case_name == "callback_positive" and support_ok and source_integrity and \
            stages["full-verification"]["exit"] == 0 and len(target_headers) == 1:
        classification = "DIAGNOSTIC_POSITIVE_CANDIDATE_REVIEW_REQUIRED"
    result = {
        "classification": classification,
        "accepted_callback_component": False,
        "actual_sort4_proved": False,
        "case": case_name,
        "source_integrity": source_integrity,
        "support_exports_decode_refinement_all_zero": support_ok,
        "target_timed_header_count": len(target_headers),
        "target_timed_headers": target_headers,
        "first_error": errors[0] if errors else None,
        "all_errors": errors,
        "intended_false_post": intended_negative,
        "normal_mir_sha256": sha((case_dir / "normal-mir.txt").read_bytes())
            if (case_dir / "normal-mir.txt").is_file() else None,
        "readonly_mir_sha256": sha((case_dir / "readonly-mir.txt").read_bytes())
            if (case_dir / "readonly-mir.txt").is_file() else None,
        "stages": stages,
    }
    (case_dir / "outcome.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"case": case_name,
                      "classification": classification,
                      "first_error": result["first_error"],
                      "stages": {name: stage.get("exit")
                                 for name, stage in stages.items()}},
                     sort_keys=True), flush=True)
    return result


def main() -> None:
    hosted_only()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--source-checkout", type=Path, required=True)
    parser.add_argument("--tool-home", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--compiler-sysroot", required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--case", choices=(*CASES, "all"), default="all")
    parser.add_argument("--deadline-epoch", type=int, required=True)
    parser.add_argument("--prepare-only", action="store_true",
                        help="generate/hash isolated source pairs without invoking tools")
    args = parser.parse_args()
    args.repo_root = args.repo_root.resolve()
    args.source_checkout = args.source_checkout.resolve()
    args.tool_home = args.tool_home.resolve()
    args.schema = args.schema.resolve()
    args.evidence = args.evidence.resolve()
    need(args.schema.is_file() and args.tool_home.is_dir() and
         args.source_checkout.is_dir(), "pinned tool/source inputs are missing")
    args.evidence.mkdir(parents=True, exist_ok=False)
    names = CASES if args.case == "all" else (args.case,)
    outcomes = {}
    if args.prepare_only:
        for case_name in names:
            record = generate_case(
                args.repo_root, args.source_checkout, args.tool_home,
                case_name, args.evidence / case_name)
            outcomes[case_name] = {
                "classification": "PREPARED_NOT_RUN",
                "ghost_strip_exact": record["ghost_strip_exact"],
                "verified_sha256": record["verified_sha256"],
                "original_sha256": record["original_sha256"],
            }
    else:
        for case_name in names:
            if args.deadline_epoch - int(time.time()) <= 15:
                outcomes[case_name] = {"classification": "NOT_RUN",
                                       "reason": "artifact and cleanup reserve"}
                continue
            outcomes[case_name] = run_case(
                args.repo_root, args.source_checkout, args.tool_home,
                args.schema, args.compiler_sysroot, args.evidence,
                case_name, args.deadline_epoch)
    aggregate = {
        "profile_source_base": PROFILE_SOURCE,
        "cases": outcomes,
        "all_accepted": False,
        "actual_sort4_proved": False,
    }
    (args.evidence / "summary.json").write_text(
        json.dumps(aggregate, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
