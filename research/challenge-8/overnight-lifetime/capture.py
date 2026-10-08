#!/usr/bin/env python3
"""Hosted-only 26.10 strict lifetime-cut regression capture.

All results are diagnostic until the complete source/MIR/kernel review and
combined-profile regressions described in MATRIX.md have passed.
"""

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


HERE = Path(__file__).resolve().parent
TEMPLATE = HERE / "cases.rs"
EXPECTED_TEMPLATE_SHA256 = "7cb5c8a8a2541da30af188c8731ee13276c59b206e5ed58a78e909852719359e"
POSITIVE = ("positive_basic", "ordinary_unmarked",
            "positive_early_return", "positive_direct_unwind",
            "positive_f_bound")
NEGATIVE = (
    "negative_wrong_marker", "negative_duplicate_marker",
    "negative_marker_outside_binding", "negative_unknown_binding",
    "negative_nested_marker", "negative_malformed_marker",
    "negative_type_name_after_cut", "negative_type_argument_after_cut",
    "negative_typed_chunk_survives_cut", "negative_unclosed_fractional_access",
    "negative_reserved_half_after_lifetime_end", "negative_end_lifetime_twice",
)
ALL = POSITIVE + NEGATIVE
BLOCK_COMMENT = re.compile(rb"/\*@.*?@\*/(?:\r?\n)?", re.S)
LINE_COMMENT = re.compile(rb"(?m)^[ \t]*//@[^\r\n]*(?:\r?\n|$)")
CASE_BEGIN = re.compile(rb"(?m)^// CASE_BEGIN ([a-z0-9_]+)\r?\n")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def need(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def strip_ghost(source: bytes) -> bytes:
    return LINE_COMMENT.sub(b"", BLOCK_COMMENT.sub(b"", source))


def target_name(case: str) -> str:
    # The accepted callback hook admits only this exact local DefPath.
    return "callback_positive" if case == "positive_f_bound" else case


def select_case(template: bytes, name: str) -> bytes:
    matches = list(CASE_BEGIN.finditer(template))
    need(len(matches) == len(ALL) and
         {m.group(1).decode() for m in matches} == set(ALL),
         "lifetime case inventory changed")
    matches = [m for m in matches if m.group(1).decode() == name]
    need(len(matches) == 1, "selected lifetime case is not unique")
    marker = matches[0]
    close = b"// CASE_END " + name.encode()
    end = template.find(close, marker.end())
    need(end >= 0 and template.find(close, end + 1) == -1,
         "selected lifetime case has no unique end")
    header = template[:CASE_BEGIN.search(template).start()]
    body = template[marker.end():end]
    need(b"// CASE_BEGIN " not in body and b"// CASE_END " not in body,
         "selected lifetime case contains another case")
    verified = header + body
    generic_targets = {"positive_f_bound", "negative_typed_chunk_survives_cut"}
    target = (b"pub unsafe fn " + target_name(name).encode() +
              (b"<" if name in generic_targets else b"("))
    need(verified.count(target) == 1, "target function source shape changed")
    expected_count = 2 if name == "positive_direct_unwind" else 1
    need(verified.count(b"pub unsafe fn ") == expected_count,
         "selected lifetime case has unexpected callee bodies")
    expected_markers = (0 if name == "ordinary_unmarked" else
                        2 if name == "negative_duplicate_marker" else 1)
    need(verified.count(b"end_lft_binding::") == expected_markers,
         "selected lifetime case has unexpected cut marker inventory")
    return verified


def balanced_mir_item(source: str, start: int) -> str:
    need(source[start:start + 1] == "(", "MIR body must start with '('")
    depth = 0
    quoted = False
    escaped = False
    for index in range(start, len(source)):
        char = source[index]
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return source[start:index + 1]
    raise ValueError("MIR body has no closing parenthesis")


def target_body(decoded: str, name: str) -> str | None:
    marker = f'defPath = "{name}"'
    if decoded.count(marker) != 1:
        return None
    at = decoded.index(marker)
    start = decoded.rfind("    ( defKind =", 0, at)
    if start < 0:
        return None
    body = balanced_mir_item(decoded, decoded.index("(", start))
    return body if marker in body else None


def stage(root: Path, name: str, args: list[str], env: dict[str, str],
          source_hashes: dict[str, str], seconds: int,
          stdin_path: Path | None = None, stdout_path: Path | None = None) -> dict:
    before = {p: sha((root / p).read_bytes()) for p in source_hashes}
    need(before == source_hashes, f"source changed before {name}")
    separate_stderr = stdout_path is not None
    stdout_path = stdout_path or root / f"{name}.log"
    stderr_path = root / f"{name}-stderr.log" if separate_stderr else stdout_path
    with stdout_path.open("wb") as stdout:
        with (stderr_path.open("wb") if stderr_path != stdout_path else open(os.devnull, "wb")) as error_output:
            with (stdin_path.open("rb") if stdin_path else open(os.devnull, "rb")) as input_stream:
                started = time.monotonic()
                try:
                    result = subprocess.run(args, cwd=root, env=env, stdin=input_stream,
                                            stdout=stdout,
                                            stderr=(error_output if stderr_path != stdout_path
                                                    else subprocess.STDOUT),
                                            timeout=seconds, check=False)
                    code = result.returncode
                except subprocess.TimeoutExpired:
                    code = 124
                elapsed = time.monotonic() - started
    after = {p: sha((root / p).read_bytes()) for p in source_hashes}
    need(after == source_hashes, f"source changed during {name}")
    return {"exit": code, "elapsed_seconds": elapsed,
            "source_exact": True, "args": args}


def expected_error(name: str, log: str, code: int) -> bool:
    errors = [line for line in log.splitlines()
              if ": error:" in line or line.startswith("Fatal error:")]
    if len(errors) != 1 or code not in (1, 2):
        return False
    error = errors[0]
    if name in ("negative_wrong_marker", "negative_marker_outside_binding",
                "negative_unknown_binding", "negative_nested_marker"):
        return "end_lft_binding needs one enclosing ghost block containing only its let_lft declaration" in error
    if name == "negative_malformed_marker":
        return "end_lft_binding expects exactly one named lifetime type and no arguments" in error
    if name == "negative_duplicate_marker":
        return "Strict lifetime binding expects exactly one cut marker per body" in error
    if name == "negative_typed_chunk_survives_cut":
        return "A lifetime-scoped heap chunk is still live at the binding end" in error
    if name in ("negative_type_name_after_cut", "negative_type_argument_after_cut"):
        return "cmp" in error and any(word in error.lower() for word in
                                      ("no such", "unknown", "unbound", "not in scope", "undeclared"))
    if name in ("negative_unclosed_fractional_access",
                "negative_reserved_half_after_lifetime_end",
                "negative_end_lifetime_twice"):
        return "lifetime_token" in error and "No matching" in error
    return False


def run_case(name: str, template: bytes, tool_home: Path, output: Path,
             sysroot: str, env: dict[str, str], deadline: float,
             opt_in: bool) -> dict:
    env = env.copy()
    if name == "positive_f_bound":
        # This isolated case is the accepted callback-positive protocol with
        # a cut added after its sole call; only this body needs HRTB matching.
        env["SORT4_HRTB_OUTPUT"] = "1"
        env["SORT4_HRTB_OUTPUT_TARGETS"] = target_name(name)
    else:
        env.pop("SORT4_HRTB_OUTPUT", None)
        env.pop("SORT4_HRTB_OUTPUT_TARGETS", None)
    root = output / (name if opt_in else name + "-without-opt-in")
    root.mkdir(parents=True, exist_ok=False)
    (root / "original").mkdir()
    (root / "verified").mkdir()
    verified = select_case(template, name)
    original = strip_ghost(verified)
    (root / "verified/lib.rs").write_bytes(verified)
    (root / "original/lib.rs").write_bytes(original)
    hashes = {"verified/lib.rs": sha(verified), "original/lib.rs": sha(original)}
    schema = tool_home / "src/rust_frontend/vf_mir/vf_mir.capnp"
    need(schema.is_file(), "pinned source schema missing")
    stages: dict[str, dict] = {}

    def run(stage_name: str, argv: list[str], cap: int,
            input_name: str | None = None, output_name: str | None = None) -> dict:
        remaining = int(deadline - time.time()) - 15
        if remaining <= 0:
            return {"exit": None, "skipped": "deadline reserve"}
        return stage(root, stage_name, argv, env, hashes, min(cap, remaining),
                     root / input_name if input_name else None,
                     root / output_name if output_name else None)

    exporter = str(tool_home / "bin/vf-rust-mir-exporter")
    for mode, extra in (("normal", []),
                        ("readonly", ["--vf-rust-mir-exporter:preprocess-readonly"])):
        stages[f"{mode}-export"] = run(
            f"{mode}-export", [exporter, "verified/lib.rs", f"--sysroot={sysroot}",
                                "--edition", "2021", "--crate-type", "lib", *extra],
            90, output_name=f"{mode}-mir.bin")
        if stages[f"{mode}-export"]["exit"] == 0:
            stages[f"{mode}-decode"] = run(
                f"{mode}-decode", ["capnp", "decode", str(schema), "VfMir"],
                60, input_name=f"{mode}-mir.bin", output_name=f"{mode}-mir.txt")
        else:
            stages[f"{mode}-decode"] = {"exit": None, "skipped": "export failure"}

    stages["full-verification"] = run(
        "full-verification", [str(tool_home / "bin/verifast"),
                              "-rustc_args", "--edition 2021 --crate-type lib",
                              "-verbose", "1", "verified/lib.rs"], 180)
    stages["refinement"] = run(
        "refinement", [str(tool_home / "bin/refinement-checker"),
                       "--rustc-args", "--edition 2021 --crate-type lib",
                       "original/lib.rs", "verified/lib.rs"], 90)

    support = all(stages.get(s, {}).get("exit") == 0 for s in
                  ("normal-export", "normal-decode", "readonly-export",
                   "readonly-decode", "refinement"))
    body_inventory = {}
    for mode in ("normal", "readonly"):
        path = root / f"{mode}-mir.txt"
        mir = path.read_text(errors="replace") if path.is_file() else ""
        names = re.findall(r'defPath = "([^"]+)"', mir)
        selected = target_body(mir, target_name(name))
        body_inventory[mode] = {
            "target_count": names.count(target_name(name)),
            "same_unit_callee_count": names.count("cut_maybe_unwind"),
            "source_path_present": selected is not None and
                                   'localPath = "verified/lib.rs"' in selected,
            "ghost_decl_block_present": selected is not None and
                                        "ghostDeclBlocks = [" in selected,
            "full_decoded_bytes": path.stat().st_size if path.is_file() else 0,
            "full_decoded_sha256": sha(path.read_bytes()) if path.is_file() else None,
            "target_body_sha256": sha(selected.encode()) if selected else None,
        }
    body_audit_ok = all(row["target_count"] == 1 and
                        row["same_unit_callee_count"] ==
                        (1 if name == "positive_direct_unwind" else 0) and
                        row["source_path_present"] and
                        row["ghost_decl_block_present"]
                        for row in body_inventory.values())
    log_path = root / "full-verification.log"
    log = log_path.read_text(errors="replace") if log_path.exists() else ""
    code = stages["full-verification"]["exit"]
    named = log.count(f"Verifying function '{target_name(name)}'")
    callee = log.count("Verifying function 'cut_maybe_unwind'")
    direct_unwind = True
    if name == "positive_direct_unwind":
        direct_unwind = all("name = \"cut_maybe_unwind\"" in
                            (root / f"{mode}-mir.txt").read_text(errors="replace") and
                            "unwindAction = (continue = void)" in
                            (root / f"{mode}-mir.txt").read_text(errors="replace")
                            for mode in ("normal", "readonly")
                            if (root / f"{mode}-mir.txt").is_file())
    status = "INCONCLUSIVE"
    if support and body_audit_ok and not opt_in and name == "positive_basic" and \
            code in (1, 2) and len([line for line in log.splitlines()
                                     if "Strict lifetime binding requires explicit overnight opt-in" in line]) == 1:
        status = "OPT_IN_ABSENT_INTENDED_REJECTION_CANDIDATE"
    if support and body_audit_ok and name in POSITIVE and code == 0 and named == 1 and \
            (name != "positive_direct_unwind" or (callee == 1 and direct_unwind)):
        status = "POSITIVE_CANDIDATE_REVIEW_REQUIRED"
    if support and body_audit_ok and name in NEGATIVE and expected_error(name, log, code):
        status = "INTENDED_NEGATIVE_CANDIDATE_REVIEW_REQUIRED"
    result = {
        "case": name, "classification": status, "stages": stages,
        "strict_lifetime_opt_in": opt_in,
        "source_hashes": hashes, "source_strip_identity": strip_ghost(verified) == original,
        "normal_post": (
            "thread/type resources, both T cells/owners, comparator F cell/owner"
            if name == "positive_f_bound" else
            "full lifetime token returned" if name in POSITIVE else
            "negative fixture's stated contract"),
        "unwind_post": (
            "thread/type resources, both T cells/owners, comparator F cell/owner"
            if name == "positive_f_bound" else
            "full lifetime token returned on direct unwind"
            if name == "positive_direct_unwind" else "fixture-specific"),
        "target_headers": named, "callee_headers": callee,
        "decoded_body_inventory": body_inventory,
        "decoded_body_inventory_ok": body_audit_ok,
        "direct_unwind_mir_candidate": direct_unwind,
        "full_error_lines": [line for line in log.splitlines()
                             if ": error:" in line or line.startswith("Fatal error:")],
        "accepted": False,
    }
    (root / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool-home", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--deadline-epoch", type=float, default=time.time() + 1800)
    parser.add_argument("--case", choices=ALL, action="append")
    parser.add_argument("--without-opt-in", action="store_true")
    args = parser.parse_args()
    need(os.getenv("GITHUB_ACTIONS") == "true" and
         os.getenv("RUNNER_ENVIRONMENT") == "github-hosted" and
         os.getenv("RUNNER_OS") == "Linux", "hosted GitHub Linux required")
    need(not args.out.exists(), "evidence directory must be fresh")
    args.out.mkdir(parents=True)
    need(args.tool_home.is_dir(), "source-built VeriFast home missing")
    for path in ("bin/verifast", "bin/vf-rust-mir-exporter", "bin/refinement-checker"):
        need((args.tool_home / path).is_file(), f"missing tool {path}")
    env = os.environ.copy()
    env["RUSTUP_TOOLCHAIN"] = "nightly-2026-09-25"
    if args.without_opt_in:
        env.pop("SORT4_STRICT_LFT_CUT", None)
    else:
        env["SORT4_STRICT_LFT_CUT"] = "1"
    env["PATH"] = str(args.tool_home / "bin") + os.pathsep + env.get("PATH", "")
    compiler = subprocess.run(["rustc", "--print", "sysroot"], env=env,
                              check=True, capture_output=True, text=True)
    sysroot = compiler.stdout.strip()
    template = TEMPLATE.read_bytes()
    need(sha(template) == EXPECTED_TEMPLATE_SHA256,
         "lifetime source template differs from reviewed bytes")
    cases = args.case or list(ALL)
    need(not args.without_opt_in or cases == ["positive_basic"],
         "without-opt-in control requires only --case positive_basic")
    results = [run_case(name, template, args.tool_home, args.out, sysroot,
                        env, args.deadline_epoch, not args.without_opt_in)
               for name in cases]
    summary = {"classification": "DIAGNOSTIC_ONLY_UNTIL_REVIEW",
               "patch_sha256": sha((HERE / "verifast-strict-lft-cut-26.10.patch").read_bytes()),
               "template_sha256": sha(template), "cases": results}
    (args.out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    need(all(r["classification"] != "INCONCLUSIVE" for r in results),
         "one or more lifetime-cut cases are inconclusive")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"lifetime capture error: {exc}", file=sys.stderr)
        raise
