#!/usr/bin/env python3
"""Run isolated tuple-2 ownership controls against a pinned hosted tool profile."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time


VF_PIN = "f76012fb518703b1d98e243ac4f487f16877cfcb"
PARSER_REL = "src/rust_frontend/vf_mir_translator/rust_parser.ml"
SPEC_REL = "bin/rust/std/lib.rsspec"
TRANSLATOR_REL = "src/rust_frontend/vf_mir_translator/vf_mir_translator.ml"
PARSER_BASE_SHA256 = "b26422aff8a6091181485a1355fc60e3a2afde5c8bff2bbe5176fdee07b08622"
PRELUDE_SHA256 = "d7058d43557a2b5147eb1377e85bb67d04b94c83594b6c1c27650c9c571841b5"
FNMUT_SHA256 = "599abd73bc551804b41f2d82aeb9c4a42d4c1c2b40396cbabfb2099c0abe1564"
STANDALONE_FILES = (PARSER_REL,)
CUMULATIVE_FILES = (SPEC_REL, PARSER_REL, TRANSLATOR_REL)
CASES = (
    "tuple2_close_generic", "tuple2_open_generic", "tuple2_noncopy_refs",
    "tuple2_share_compat",
    "tuple2_false_post", "tuple2_resource_loss", "tuple2_resource_duplication",
    "tuple1_opaque_control", "tuple3_opaque_control", "tuple4_opaque_control",
    "unrelated_struct_opaque_control",
)
POSITIVE = {"tuple2_close_generic", "tuple2_open_generic", "tuple2_noncopy_refs",
            "tuple2_share_compat"}
POST_NEGATIVE = {
    "tuple2_false_post", "tuple2_resource_loss", "tuple2_resource_duplication"
}
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
         "tuple-2 hosted tests require GitHub-hosted Linux")


def strip_ghost(source: bytes) -> bytes:
    return GHOST_LINE.sub(b"", GHOST_BLOCK.sub(b"", source))


def select_case(template: bytes, name: str) -> bytes:
    all_begin = [f"// CASE_BEGIN {case}\n".encode() for case in CASES]
    all_end = [f"// CASE_END {case}\n".encode() for case in CASES]
    need(all(template.count(marker) == 1 for marker in (*all_begin, *all_end)),
         "case markers missing or duplicated")
    begin = f"// CASE_BEGIN {name}\n".encode()
    end = f"// CASE_END {name}\n".encode()
    start = template.index(begin) + len(begin)
    stop = template.index(end, start)
    first = min(template.index(marker) for marker in all_begin)
    need(start >= first and stop > start, f"invalid case boundary: {name}")
    return template[:first] + template[start:stop]


def normal_ens_span(source: bytes) -> tuple[int, int] | None:
    lines = source.decode().splitlines()
    starts = [i for i, line in enumerate(lines)
              if re.match(r"^\s*ens\b", line)]
    if len(starts) != 1:
        return None
    start = starts[0]
    for end in range(start, len(lines)):
        if ";" in lines[end]:
            return start + 1, end + 1
        if "@*/" in lines[end]:
            return None
    return None


def target_line(source: bytes, case_name: str) -> int | None:
    if case_name in POST_NEGATIVE:
        span = normal_ens_span(source)
        if span is None:
            return None
        first, last = span
        if case_name == "tuple2_false_post":
            matches = [i for i, line in enumerate(source.decode().splitlines(), 1)
                       if first <= i <= last and re.search(r"\bfalse\s*;", line)]
            return matches[0] if len(matches) == 1 else None
        return first
    if case_name in {"tuple1_opaque_control", "tuple3_opaque_control",
                     "tuple4_opaque_control", "unrelated_struct_opaque_control"}:
        matches = [i for i, line in enumerate(source.decode().splitlines(), 1)
                   if "//@ close " in line]
        return matches[0] if len(matches) == 1 else None
    return None


def verify_source_profile(repo_root: Path, source: Path, tool_home: Path,
                          evidence: Path, cumulative: bool) -> dict:
    head = subprocess.run(["git", "-C", str(source), "rev-parse", "HEAD"],
                          check=True, capture_output=True, text=True).stdout.strip()
    need(head == VF_PIN, f"unexpected VeriFast source pin: {head}")
    base = subprocess.run(
        ["git", "-C", str(source), "show", f"HEAD:{PARSER_REL}"],
        check=True, capture_output=True).stdout
    need(sha(base) == PARSER_BASE_SHA256, "pinned parser base hash differs")
    changed = subprocess.run(
        ["git", "-C", str(source), "diff", "--name-only"],
        check=True, capture_output=True, text=True).stdout.splitlines()
    expected_files = list(CUMULATIVE_FILES if cumulative else STANDALONE_FILES)
    need(changed == expected_files,
         f"unexpected modified source files for cumulative={cumulative}: {changed}")
    status = subprocess.run(
        ["git", "-C", str(source), "status", "--porcelain", "--untracked-files=all"],
        check=True, capture_output=True, text=True).stdout.splitlines()
    expected_status = [f" M {rel}" for rel in expected_files]
    need(status == expected_status,
         f"source checkout has staged/untracked/unexpected changes: {status}")

    patch = Path(__file__).with_name("verifast-tuple2-own-26.10.patch").read_bytes()
    actual_diff = subprocess.run(
        ["git", "-C", str(source), "diff", "--no-ext-diff", "--unified=3",
         "--", PARSER_REL], check=True, capture_output=True).stdout
    canonical_diff = b"\n".join(
        line for line in actual_diff.splitlines()
        if not line.startswith(b"index ")) + b"\n"
    need(canonical_diff == patch,
         "source parser diff does not exactly match the reviewed standalone patch")

    full_diff = subprocess.run(
        ["git", "-C", str(source), "diff", "--no-ext-diff", "--unified=3"],
        check=True, capture_output=True).stdout
    (evidence / "effective-source-diff.patch").write_bytes(full_diff)
    per_file = {}
    for rel in expected_files:
        base_file = subprocess.run(
            ["git", "-C", str(source), "show", f"HEAD:{rel}"],
            check=True, capture_output=True).stdout
        current_file = (source / rel).read_bytes()
        file_diff = subprocess.run(
            ["git", "-C", str(source), "diff", "--no-ext-diff", "--unified=3",
             "--", rel], check=True, capture_output=True).stdout
        per_file[rel] = {
            "base_sha256": sha(base_file),
            "current_sha256": sha(current_file),
            "diff_sha256": sha(file_diff),
        }

    prelude = source / "bin/rust/prelude.rsspec"
    need(sha(prelude.read_bytes()) == PRELUDE_SHA256,
         "source prelude changed; tuple-2 share/spec must remain stock")
    active_prelude = tool_home / "bin/rust/prelude.rsspec"
    need(sha(active_prelude.read_bytes()) == PRELUDE_SHA256,
         "active tool-home prelude differs from stock tuple-2 share definition")
    parser = (source / PARSER_REL).read_bytes()
    need(parser.count(b'sn = "std_tuple_2_" && tparams = ["T1"; "T2"]') == 1 and
         b'field_own "T1" "0", field_own "T2" "1"' in parser,
         "patched parser lacks the exact tuple-2 field-own body")
    shape_guard_parts = (
        b'&&\n            (match body with',
        b'| Left ([],\n                     [Field (_, Real, IdentTypeExpr (_, None, "T1"), "0", Instance, Public, false, None);',
        b'Field (_, Real, IdentTypeExpr (_, None, "T2"), "1", Instance, Public, false, None)],\n                     [], false) -> true',
        b'| _ -> false) then',
    )
    need(all(part in parser for part in shape_guard_parts),
         "tuple2-own branch lacks the exact two-public-field AST guard")
    shape_guard = b"\n".join(shape_guard_parts)

    spec = (tool_home / "bin/rust/std/lib.rsspec").read_bytes()
    start = spec.find(b"    trait FnMut<Args> {")
    end = spec.find(b"    trait Fn<Args> {", start + 1)
    need(start >= 0 and end > start and sha(spec[start:end]) == FNMUT_SHA256,
         "active FnMut contract differs from stock")
    executables = [tool_home / "bin" / name for name in
                   ("verifast", "vf-rust-mir-exporter", "refinement-checker")]
    need(all(path.is_file() for path in executables),
         "patched source tool home is incomplete")
    return {
        "source_base": head,
        "parser_base_sha256": sha(base),
        "patched_parser_sha256": sha(parser),
        "patch_sha256": sha(patch),
        "applied_diff_exact": True,
        "tuple2_exact_two_field_shape_guard": True,
        "tuple2_shape_guard_sha256": sha(shape_guard),
        "shape_mismatch_control": "non-matching AST body falls through existing opaque branch",
        "shape_mismatch_control_kind": "static_exact_parser_patch_certificate_not_runtime_probe",
        "source_changed_files": changed,
        "cumulative_profile": cumulative,
        "effective_source_diff_sha256": sha(full_diff),
        "effective_source_diff_path_from_evidence_root": "effective-source-diff.patch",
        "source_file_hashes": per_file,
        "prelude_sha256": sha(prelude.read_bytes()),
        "active_tool_home_prelude_sha256": sha(active_prelude.read_bytes()),
        "stock_fnmut_clause_sha256": FNMUT_SHA256,
        "tool_hashes": {path.name: sha(path.read_bytes()) for path in executables},
        "repo_head": subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
            check=True, capture_output=True, text=True).stdout.strip(),
        "source_build_log_required_for_acceptance": True,
    }


def run_stage(name: str, argv: list[str], case_dir: Path, env: dict[str, str],
              source_hashes: dict[str, str], timeout_seconds: int,
              stdin_name: str | None = None,
              stdout_name: str | None = None) -> dict:
    paths = {rel: case_dir / rel for rel in source_hashes}
    before = {rel: sha(path.read_bytes()) for rel, path in paths.items()}
    need(before == source_hashes, f"fixture changed before {name}")
    stdout_path = case_dir / (stdout_name or f"{name}.log")
    stderr_path = case_dir / f"{name}-stderr.log" if stdout_name else stdout_path
    with stdout_path.open("wb") as stdout:
        stderr = (stderr_path.open("wb") if stderr_path != stdout_path
                  else subprocess.STDOUT)
        try:
            stdin = ((case_dir / stdin_name).open("rb") if stdin_name
                     else open(os.devnull, "rb"))
            try:
                result = subprocess.run(
                    ["/usr/bin/time", "-v", "-o", str(case_dir / f"{name}-resources.txt"),
                     "timeout", "--signal=TERM", "--kill-after=10s",
                     f"{timeout_seconds}s", *argv],
                    cwd=case_dir, env=env, stdin=stdin, stdout=stdout,
                    stderr=stderr, check=False).returncode
            finally:
                stdin.close()
        finally:
            if stderr_path != stdout_path:
                stderr.close()
    after = {rel: sha(path.read_bytes()) for rel, path in paths.items()}
    record = {
        "argv": argv, "exit": result, "timeout_seconds": timeout_seconds,
        "source_before": before, "source_after": after,
        "source_exact": before == after == source_hashes,
        "stdout": stdout_path.name, "stderr": stderr_path.name,
    }
    (case_dir / f"{name}-stage.json").write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n")
    return record


def run_case(repo_root: Path, tool_home: Path, schema: Path,
             compiler_sysroot: str, root: Path, name: str,
             deadline_epoch: int, profile: dict) -> dict:
    template = Path(__file__).with_name("tuple2-own-cases.rs").read_bytes()
    verified = select_case(template, name)
    original = strip_ghost(verified)
    need(strip_ghost(verified) == original, "ghost strip did not preserve the case")
    case_dir = root / name
    case_dir.mkdir(parents=True, exist_ok=False)
    (case_dir / "original").mkdir()
    (case_dir / "verified").mkdir()
    (case_dir / "original/lib.rs").write_bytes(original)
    (case_dir / "verified/lib.rs").write_bytes(verified)
    line = target_line(verified, name)
    if name in POST_NEGATIVE or name.endswith("opaque_control"):
        need(line is not None, f"intended target location missing for {name}")
    hashes = {"original/lib.rs": sha(original), "verified/lib.rs": sha(verified)}
    fixture = {
        **profile, "case": name, "template_sha256": sha(template),
        "verified_sha256": hashes["verified/lib.rs"],
        "original_sha256": hashes["original/lib.rs"],
        "ghost_strip_exact": True, "expected_target_line": line,
        "domain": "generic structural tuple ownership; no Copy/Clone premise",
        "callback_source_modified": False,
    }
    (case_dir / "fixture.json").write_text(
        json.dumps(fixture, indent=2, sort_keys=True) + "\n")
    env = os.environ.copy()
    env["PATH"] = str(tool_home / "bin") + os.pathsep + env.get("PATH", "")

    def budget(cap: int) -> int | None:
        left = deadline_epoch - int(time.time())
        return min(cap, left - 10) if left > 10 else None

    def run(name: str, argv: list[str], cap: int,
            stdin: str | None = None, stdout: str | None = None) -> dict:
        seconds = budget(cap)
        if seconds is None:
            return {"exit": None, "skipped": "artifact/deadline reserve"}
        return run_stage(name, argv, case_dir, env, hashes, seconds, stdin, stdout)

    exporter = str(tool_home / "bin/vf-rust-mir-exporter")
    stage = run("normal-export", [exporter, "verified/lib.rs",
                                  f"--sysroot={compiler_sysroot}", "--edition", "2021"],
                90, stdout="normal-mir.bin")
    stages = {"normal-export": stage}
    if stage.get("exit") == 0:
        stages["normal-decode"] = run(
            "normal-decode", ["capnp", "decode", str(schema), "VfMir"],
            60, "normal-mir.bin", "normal-mir.txt")
    else:
        stages["normal-decode"] = {"exit": None, "skipped": "normal export failed"}
    stage = run("readonly-export", [exporter, "verified/lib.rs",
                                    f"--sysroot={compiler_sysroot}", "--edition", "2021",
                                    "--vf-rust-mir-exporter:preprocess-readonly"],
                90, stdout="readonly-mir.bin")
    stages["readonly-export"] = stage
    if stage.get("exit") == 0:
        stages["readonly-decode"] = run(
            "readonly-decode", ["capnp", "decode", str(schema), "VfMir"],
            60, "readonly-mir.bin", "readonly-mir.txt")
    else:
        stages["readonly-decode"] = {"exit": None, "skipped": "readonly export failed"}
    verifier = str(tool_home / "bin/verifast")
    stages["full-verification"] = run(
        "full-verification", [verifier, "-rustc_args", "--edition 2021",
                              "-verbose", "1", "verified/lib.rs"], 180)
    stages["refinement"] = run(
        "refinement", [str(tool_home / "bin/refinement-checker"),
                       "--rustc-args", "--edition 2021",
                       "original/lib.rs", "verified/lib.rs"], 90)

    log = (case_dir / "full-verification.log").read_text(errors="replace")
    headers = re.findall(
        rf"(?m)^\s*\d+(?:\.\d+)?s: verified/lib\.rs\([^)]*\): Verifying function '{re.escape(name)}'",
        log)
    errors = [line for line in log.splitlines() if ": error:" in line]
    support = ("normal-export", "normal-decode", "readonly-export",
               "readonly-decode", "refinement")
    support_ok = all(stages.get(key, {}).get("exit") == 0 for key in support)
    integrity = all(row.get("source_exact") is True for row in stages.values()
                     if "source_exact" in row)
    intended = False
    classification = "INCONCLUSIVE"
    if name in POSITIVE and support_ok and integrity and \
            stages["full-verification"].get("exit") == 0 and len(headers) == 1:
        classification = "POSITIVE_CANDIDATE_REVIEW_REQUIRED"
    elif name in POST_NEGATIVE and support_ok and integrity and \
            stages["full-verification"].get("exit") == 1 and len(headers) == 1 and \
            len(errors) == 1:
        span = normal_ens_span(verified)
        match = re.search(r"verified/lib\.rs\((\d+),", errors[0])
        located = span is not None and match is not None and \
            span[0] <= int(match.group(1)) <= span[1]
        expected_error = ("Cannot prove false" in errors[0]
                          if name == "tuple2_false_post" else
                          any(fragment in errors[0] for fragment in
                              ("Cannot prove", "No matching heap chunks",
                               "Cannot produce")))
        intended = located and expected_error
        if intended:
            classification = "INTENDED_RESOURCE_POST_NEGATIVE"
    elif name.endswith("opaque_control") and support_ok and integrity and \
            stages["full-verification"].get("exit") == 1 and len(headers) == 1 and \
            len(errors) == 1 and "No matching heap chunks" in errors[0]:
        match = re.search(r"verified/lib\.rs\((\d+),", errors[0])
        intended = match is not None and int(match.group(1)) == line
        if intended:
            classification = "EXPECTED_OPAQUE_SCOPE_CONTROL"
    result = {
        "case": name, "classification": classification,
        "accepted_component": False, "actual_sort4_proved": False,
        "support_all_zero": support_ok, "source_integrity": integrity,
        "target_header_count": len(headers), "target_headers": headers,
        "first_error": errors[0] if errors else None,
        "all_errors": errors, "intended_negative": intended,
        "expected_target_line": line, "stages": stages,
    }
    (case_dir / "outcome.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"case": name, "classification": classification,
                      "first_error": result["first_error"]}, sort_keys=True), flush=True)
    return result


def main() -> None:
    hosted_only()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--source-checkout", type=Path, required=True,
                        help="f76012fb checkout with the selected reviewed source profile")
    parser.add_argument("--tool-home", type=Path, required=True,
                        help="full source-built tool home from that patched checkout")
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--compiler-sysroot", required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--deadline-epoch", type=int, required=True)
    parser.add_argument("--case", choices=(*CASES, "all"), default="all")
    parser.add_argument("--cumulative-profile", action="store_true",
                        help=("allow exactly the stock S6/A1/CFG source files "
                              "plus the exact tuple-2 parser patch"))
    args = parser.parse_args()
    args.repo_root = args.repo_root.resolve()
    args.source_checkout = args.source_checkout.resolve()
    args.tool_home = args.tool_home.resolve()
    args.schema = args.schema.resolve()
    args.evidence = args.evidence.resolve()
    need(args.schema.is_file() and args.source_checkout.is_dir() and
         args.tool_home.is_dir(), "pinned source-build inputs are missing")
    args.evidence.mkdir(parents=True, exist_ok=False)
    profile = verify_source_profile(args.repo_root, args.source_checkout,
                                    args.tool_home, args.evidence,
                                    args.cumulative_profile)
    names = CASES if args.case == "all" else (args.case,)
    outcomes = {}
    for name in names:
        if args.deadline_epoch - int(time.time()) <= 15:
            outcomes[name] = {"classification": "NOT_RUN",
                              "reason": "artifact/deadline reserve"}
            continue
        outcomes[name] = run_case(
            args.repo_root, args.tool_home, args.schema,
            args.compiler_sysroot, args.evidence, name,
            args.deadline_epoch, profile)
    callback_dir = args.evidence / "callback"
    callback_argv = [
        "python3", str(Path(__file__).with_name("probe.py")),
        "--repo-root", str(args.repo_root),
        "--source-checkout", str(args.source_checkout),
        "--tool-home", str(args.tool_home), "--schema", str(args.schema),
        "--compiler-sysroot", args.compiler_sysroot,
        "--evidence", str(callback_dir),
        "--deadline-epoch", str(args.deadline_epoch),
    ]
    result = subprocess.run(callback_argv, check=False, env=os.environ.copy())
    outcomes["unchanged-callback"] = {
        "classification": "CALLBACK_RUNNER_EXIT_RECORDED",
        "exit": result.returncode,
        "evidence": str(callback_dir),
    }
    summary = {
        "profile": profile, "cases": outcomes,
        "component_accepted": False, "actual_sort4_proved": False,
        "source_build_log_required_for_acceptance": True,
    }
    (args.evidence / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
