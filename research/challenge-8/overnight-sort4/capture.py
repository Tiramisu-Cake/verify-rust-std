#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Capture exact sort4_stable source, full MIR, and the first verifier boundary.

This hosted-only diagnostic is intentionally not an actual sort4 proof.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time


SOURCE_REL = Path("library/core/src/slice/sort/shared/smallsort.rs")
SOURCE_SHA256 = "85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1"
SOURCE_BLOB = "40939f922bcb6fdc7ee0d30427fa861827043827"
FUNCTION_HEADER = (
    b"pub unsafe fn sort4_stable<T, F: FnMut(&T, &T) -> bool>(\n"
    b"    v_base: *const T,\n"
    b"    dst: *mut T,\n"
    b"    is_less: &mut F,\n"
    b") "
)
NEXT_SOURCE_ANCHOR = (
    b"\n\n/// SAFETY: The caller MUST guarantee that v_base is valid for 8 reads and"
)
SOURCE_CALL_COUNTS = {
    b"is_less(": 5,
    b"hint::select_unpredictable(": 8,
    b"ptr::copy_nonoverlapping(": 4,
}
FNMUT_TARGET = "FnMut::call_mut"
GHOST_BLOCK = re.compile(rb"/\*@.*?@\*/(?:\r?\n)?", re.S)
FNMUT_CALL_NAME = re.compile(r'fnDef = \(\s*id = \(\s*name = "([^"]+)"')
FUNCTION_DEF = re.compile(r'defPath = "([^"]+)"')

PREFIX = (
    b"#![feature(const_trait_impl)]\n"
    b"#![allow(internal_features)]\n\n"
    b"use std::{hint, ptr};\n\n"
)
CAPTURE_CONTRACT = b"""/*@
req thread_token(?t) &*& t == currentThread &*&
    type_interp::<T>() &*& type_interp::<F>() &*&
    *is_less |-> ?less_before &*& <F>.own(t, less_before);
@*/
/*@
ens thread_token(t) &*& type_interp::<T>() &*& type_interp::<F>() &*&
    *is_less |-> ?less_after &*& <F>.own(t, less_after);
@*/
/*@
on_unwind_ens thread_token(t) &*& type_interp::<T>() &*& type_interp::<F>() &*&
    *is_less |-> ?less_after &*& <F>.own(t, less_after);
@*/
"""


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def strip_ghost(source: bytes) -> bytes:
    return GHOST_BLOCK.sub(b"", source)


def extract_target(source: bytes) -> tuple[bytes, int]:
    require(source.count(FUNCTION_HEADER) == 1,
            "actual sort4_stable signature is absent or ambiguous")
    start = source.index(FUNCTION_HEADER)
    open_brace = start + len(FUNCTION_HEADER)
    require(source[open_brace:open_brace + 1] == b"{",
            "signature no longer ends at the actual function body")
    tail = source.find(NEXT_SOURCE_ANCHOR, open_brace)
    require(tail > open_brace and source[tail - 1:tail] == b"}",
            "function closing brace or next source anchor changed")
    target = source[start:tail]
    for fragment, expected in SOURCE_CALL_COUNTS.items():
        require(target.count(fragment) == expected,
                f"actual source call inventory changed: {fragment.decode()}")
    require(target.count(b"ptr::copy_nonoverlapping(") == 4,
            "actual four-copy tail is missing or ambiguous")
    require(target.index(b"let c1 = is_less(") <
            target.index(b"ptr::copy_nonoverlapping(min, dst, 1);"),
            "comparisons must remain before the first destination write")
    require(target.rfind(b"let c5 = is_less(") <
            target.index(b"ptr::copy_nonoverlapping(min, dst, 1);"),
            "last comparison must remain before the first destination write")
    return target, start


def source_certificate(repo: Path, source: bytes | None = None) -> tuple[bytes, dict]:
    path = repo / SOURCE_REL
    actual = path.read_bytes() if source is None else source
    actual_sha = digest(actual)
    require(actual_sha == SOURCE_SHA256,
            f"SmallSort source hash mismatch: {actual_sha}")
    blob = subprocess.run(["git", "-C", str(repo), "hash-object", str(path)],
                          check=True, capture_output=True, text=True).stdout.strip()
    require(blob == SOURCE_BLOB, f"SmallSort source Git blob mismatch: {blob}")
    target, start = extract_target(actual)
    return target, {
        "source_path": str(SOURCE_REL),
        "source_sha256": SOURCE_SHA256,
        "source_git_blob": SOURCE_BLOB,
        "target_byte_start": start,
        "target_source_sha256": digest(target),
        "target_signature": FUNCTION_HEADER.decode() + "{",
        "target_runtime_source_exact": True,
        "generic_domain": "all sized T; F: FnMut(&T, &T) -> bool",
        "source_call_counts": {
            "FnMut_callback_expression": SOURCE_CALL_COUNTS[b"is_less("],
            "select_unpredictable": SOURCE_CALL_COUNTS[b"hint::select_unpredictable("],
            "copy_nonoverlapping": SOURCE_CALL_COUNTS[b"ptr::copy_nonoverlapping("],
        },
        "all_five_comparisons_precede_first_write": True,
    }


def source_certificate_control(repo: Path, source: bytes,
                               source_record: dict) -> dict:
    old = b"let c1 = is_less(&*v_base.add(1), &*v_base);"
    altered = b"let c1 = false;"
    require(source.count(old) == 1,
            "cannot construct the one-token source-alter control")
    changed = source.replace(old, altered, 1)
    rejected = False
    try:
        source_certificate(repo, changed)
    except ValueError as exc:
        rejected = "SmallSort source hash mismatch" in str(exc)
    require(rejected, "source certificate accepted an altered comparator operation")
    return {
        "classification": "EXPECTED_SOURCE_CERTIFICATE_REJECTION",
        "alteration": "replace the first actual comparator call with `false`",
        "original_source_sha256": source_record["source_sha256"],
        "altered_source_sha256": digest(changed),
        "rejected_at": "pinned source SHA before extraction or MIR",
    }


def write_fixture(repo: Path, out: Path) -> dict:
    source = (repo / SOURCE_REL).read_bytes()
    target, source_record = source_certificate(repo, source)
    negative = source_certificate_control(repo, source, source_record)
    open_brace = target.index(b"{")
    verified = (PREFIX + target[:open_brace] + CAPTURE_CONTRACT +
                target[open_brace:])
    original = strip_ghost(verified)
    require(original == PREFIX + target,
            "ghost stripping did not recover exact source signature and body")
    require(original.count(target) == strip_ghost(verified).count(target) == 1,
            "target source function is duplicated or changed")
    require(not out.exists(), f"refusing to overwrite fixture directory: {out}")
    (out / "original").mkdir(parents=True)
    (out / "verified").mkdir()
    (out / "original/lib.rs").write_bytes(original)
    (out / "verified/lib.rs").write_bytes(verified)
    record = {
        "classification": "CAPTURE_ONLY_NOT_A_SORT4_PROOF",
        "source_certificate": source_record,
        "source_alter_control": negative,
        "capture_contract": "thread/type resources and current comparator resource only; no element or pointer permissions",
        "full_generic_safety_contract": "NOT_PROVED",
        "normal_target_posts": "capture-only token/type resources and current comparator resource",
        "unwind_target_posts": "capture-only token/type resources and current comparator resource",
        "normal_source_sha256": digest(original),
        "verified_source_sha256": digest(verified),
        "ghost_strip_identity": strip_ghost(verified) == original,
        "runtime_body_and_signature_unchanged": True,
        "sorting_property_claimed": False,
        "actual_sort4_proved": False,
    }
    require(record["ghost_strip_identity"], "fixture source pair differs after ghost stripping")
    (out / "fixture.json").write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n")
    return record


def balanced_record(decoded: str, opening: int) -> str:
    require(decoded[opening] == "(", "MIR function record opening missing")
    depth = 0
    in_string = False
    escaped = False
    for at in range(opening, len(decoded)):
        ch = decoded[at]
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
        elif ch == '"':
            in_string = True
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return decoded[opening:at + 1]
    raise ValueError("MIR function record is unterminated")


def complete_function_record(decoded: str, basename: str) -> tuple[str, str]:
    matches = [match for match in FUNCTION_DEF.finditer(decoded)
               if match.group(1) == basename or
               match.group(1).endswith("::" + basename)]
    require(len(matches) == 1,
            f"MIR target function is absent or ambiguous: {basename}")
    match = matches[0]
    lead = decoded.rfind("    ( defKind =", 0, match.start())
    require(lead >= 0, "MIR function record start is missing")
    opening = decoded.index("(", lead)
    record = balanced_record(decoded, opening)
    require(match.group(0) in record and "basicBlocks = [" in record and
            "localDecls = [" in record and "inputs = [" in record,
            "target MIR record is not the complete typed function graph")
    return match.group(1), record


def graph_inventory(decoded_path: Path, out: Path, mode: str) -> dict:
    decoded = decoded_path.read_text(errors="strict")
    defpath, record = complete_function_record(decoded, "sort4_stable")
    fnmut_calls = FNMUT_CALL_NAME.findall(record)
    fnmut_calls = [name for name in fnmut_calls if FNMUT_TARGET in name]
    require(len(fnmut_calls) == SOURCE_CALL_COUNTS[b"is_less("],
            f"MIR callback call count differs from exact source: {len(fnmut_calls)}")
    block_at = record.index("basicBlocks = [")
    locals_at = record.index("localDecls = [")
    require(locals_at < block_at, "pinned MIR local/block field order changed")
    block_section = record[block_at:]
    block_ids = re.findall(r"\( id = \(index = (\d+)\)", block_section)
    require(bool(block_ids), "complete target record has no decodable basic blocks")
    unwind_lines = [line.strip() for line in record.splitlines()
                    if "unwindAction =" in line]
    require(len(unwind_lines) >= len(fnmut_calls),
            "MIR omitted one or more comparator call unwind actions")
    cleanup_lines = [line.strip() for line in record.splitlines()
                     if "isCleanup = true" in line]
    targets = FNMUT_CALL_NAME.findall(record)
    path = out / f"{mode}-sort4-full-mir.txt"
    path.write_text(record)
    inventory = {
        "classification": "UNREVIEWED_COMPLETE_GRAPH_CAPTURE",
        "mode": mode,
        "def_path": defpath,
        "decoded_mir_sha256": digest(decoded.encode()),
        "full_function_record_path": path.name,
        "full_function_record_sha256": digest(record.encode()),
        "full_function_record_bytes": len(record.encode()),
        "complete_record_fields_present": ["inputs", "localDecls", "basicBlocks"],
        "basic_block_indices": block_ids,
        "basic_block_count": len(block_ids),
        "local_declaration_count": len(re.findall(r"id = \(name = \"", record[locals_at:block_at])),
        "source_comparator_calls": SOURCE_CALL_COUNTS[b"is_less("],
        "mir_fnmut_call_targets": fnmut_calls,
        "mir_call_target_names": targets,
        "unwind_action_lines": unwind_lines,
        "unwind_action_count": len(unwind_lines),
        "cleanup_block_marker_lines": cleanup_lines,
        "cleanup_block_count": len(cleanup_lines),
        "cleanup_inventory_reviewed": False,
    }
    (out / f"{mode}-graph-inventory.json").write_text(
        json.dumps(inventory, indent=2, sort_keys=True) + "\n")
    return inventory


def run_stage(name: str, argv: list[str], root: Path, env: dict[str, str],
              fixture_hashes: dict[str, str], deadline: int,
              cap: int, stdin_name: str | None = None,
              stdout_name: str | None = None) -> dict:
    paths = {rel: root / rel for rel in fixture_hashes}
    before = {rel: digest(path.read_bytes()) for rel, path in paths.items()}
    require(before == fixture_hashes, f"fixture source changed before {name}")
    seconds = min(cap, deadline - int(time.time()) - 10)
    if seconds <= 0:
        return {"exit": None, "skipped": "deadline/artifact reserve"}
    stdout_path = root / (stdout_name or f"{name}.log")
    stderr_path = root / f"{name}-stderr.log" if stdout_name else stdout_path
    with stdout_path.open("wb") as stdout:
        stderr = stderr_path.open("wb") if stderr_path != stdout_path else subprocess.STDOUT
        try:
            stdin = (root / stdin_name).open("rb") if stdin_name else open(os.devnull, "rb")
            try:
                result = subprocess.run(
                    ["/usr/bin/time", "-v", "-o", str(root / f"{name}-resources.txt"),
                     "timeout", "--signal=TERM", "--kill-after=10s",
                     f"{seconds}s", *argv],
                    cwd=root, env=env, stdin=stdin, stdout=stdout,
                    stderr=stderr, check=False).returncode
            finally:
                stdin.close()
        finally:
            if stderr_path != stdout_path:
                stderr.close()
    after = {rel: digest(path.read_bytes()) for rel, path in paths.items()}
    record = {
        "argv": argv, "exit": result, "timeout_seconds": seconds,
        "fixture_before": before, "fixture_after": after,
        "fixture_integrity": before == after == fixture_hashes,
        "stdout": stdout_path.name, "stderr": stderr_path.name,
    }
    (root / f"{name}-stage.json").write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n")
    return record


def execute(args: argparse.Namespace) -> dict:
    require(os.environ.get("GITHUB_ACTIONS") == "true" and
            os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted" and
            os.environ.get("RUNNER_OS") == "Linux",
            "sort4 capture is restricted to GitHub-hosted Linux")
    args.repo_root = args.repo_root.resolve()
    args.tool_home = args.tool_home.resolve()
    args.schema = args.schema.resolve()
    args.evidence = args.evidence.resolve()
    require(args.schema.is_file() and args.tool_home.is_dir(),
            "pinned hosted tool inputs are missing")
    args.evidence.mkdir(parents=True, exist_ok=False)
    fixture_dir = args.evidence / "fixture"
    fixture = write_fixture(args.repo_root, fixture_dir)
    hashes = {"original/lib.rs": fixture["normal_source_sha256"],
              "verified/lib.rs": fixture["verified_source_sha256"]}
    env = os.environ.copy()
    env["PATH"] = str(args.tool_home / "bin") + os.pathsep + env.get("PATH", "")
    tool_names = ("verifast", "vf-rust-mir-exporter", "refinement-checker")
    tool_hashes = {name: digest((args.tool_home / "bin" / name).read_bytes())
                   for name in tool_names}
    source_hash_before = fixture["source_certificate"]["source_sha256"]
    compiler = subprocess.run(["rustc", "--version", "--verbose"],
                              check=True, capture_output=True, text=True).stdout
    profile = {
        "proof_sha": subprocess.run(
            ["git", "-C", str(args.repo_root), "rev-parse", "HEAD"],
            check=True, capture_output=True, text=True).stdout.strip(),
        "source_sha256": fixture["source_certificate"]["source_sha256"],
        "tool_hashes": tool_hashes,
        "schema_sha256": digest(args.schema.read_bytes()),
        "compiler_version_verbose": compiler,
        "capture_only": True,
        "actual_sort4_proved": False,
    }
    (args.evidence / "hosted-profile.json").write_text(
        json.dumps(profile, indent=2, sort_keys=True) + "\n")

    exporter = str(args.tool_home / "bin/vf-rust-mir-exporter")
    verifier = str(args.tool_home / "bin/verifast")
    stages: dict[str, dict] = {}

    def run(name: str, argv: list[str], cap: int,
            stdin: str | None = None, stdout: str | None = None) -> dict:
        return run_stage(name, argv, fixture_dir, env, hashes,
                         args.deadline_epoch, cap, stdin, stdout)

    stages["normal-export"] = run(
        "normal-export", [exporter, "verified/lib.rs",
                          f"--sysroot={args.compiler_sysroot}", "--edition", "2021"],
        100, stdout="normal-mir.bin")
    if stages["normal-export"].get("exit") == 0:
        stages["normal-decode"] = run(
            "normal-decode", ["capnp", "decode", str(args.schema), "VfMir"],
            60, "normal-mir.bin", "normal-mir.txt")
    else:
        stages["normal-decode"] = {"exit": None, "skipped": "normal export failed"}
    stages["readonly-export"] = run(
        "readonly-export", [exporter, "verified/lib.rs",
                            f"--sysroot={args.compiler_sysroot}", "--edition", "2021",
                            "--vf-rust-mir-exporter:preprocess-readonly"],
        100, stdout="readonly-mir.bin")
    if stages["readonly-export"].get("exit") == 0:
        stages["readonly-decode"] = run(
            "readonly-decode", ["capnp", "decode", str(args.schema), "VfMir"],
            60, "readonly-mir.bin", "readonly-mir.txt")
    else:
        stages["readonly-decode"] = {"exit": None, "skipped": "readonly export failed"}

    normal_graph = None
    readonly_graph = None
    if stages["normal-decode"].get("exit") == 0:
        normal_graph = graph_inventory(fixture_dir / "normal-mir.txt",
                                       args.evidence, "normal")
    if stages["readonly-decode"].get("exit") == 0:
        readonly_graph = graph_inventory(fixture_dir / "readonly-mir.txt",
                                         args.evidence, "readonly")

    stages["full-verification"] = run(
        "full-verification", [verifier, "-rustc_args", "--edition 2021",
                              "-verbose", "1", "verified/lib.rs"], 240)
    stages["refinement"] = run(
        "refinement", [str(args.tool_home / "bin/refinement-checker"),
                       "--rustc-args", "--edition 2021",
                       "original/lib.rs", "verified/lib.rs"], 120)
    full_log = (fixture_dir / "full-verification.log").read_text(errors="replace")
    headers = re.findall(
        r"(?m)^\s*\d+(?:\.\d+)?s: verified/lib\.rs\([^)]*\): Verifying function 'sort4_stable'",
        full_log)
    errors = [line for line in full_log.splitlines() if ": error:" in line]
    support_keys = ("normal-export", "normal-decode", "readonly-export",
                    "readonly-decode", "refinement")
    support_ok = all(stages.get(key, {}).get("exit") == 0 for key in support_keys)
    source_after = (args.repo_root / SOURCE_REL).read_bytes()
    source_repository_integrity = digest(source_after) == source_hash_before
    fixture_integrity = all(row.get("fixture_integrity") is True
                            for row in stages.values()
                            if "fixture_integrity" in row)
    tool_hashes_after = {
        name: digest((args.tool_home / "bin" / name).read_bytes())
        for name in tool_names
    }
    tool_integrity = tool_hashes_after == tool_hashes
    source_integrity = fixture_integrity and source_repository_integrity
    graph_complete = normal_graph is not None and readonly_graph is not None
    result = {
        "classification": "CAPTURE_ONLY_NOT_A_SORT4_PROOF",
        "accepted_component": False,
        "actual_sort4_proved": False,
        "full_generic_safety_contract_proved": False,
        "support_export_decode_refinement_all_zero": support_ok,
        "full_graphs_captured": graph_complete,
        "normal_graph": normal_graph,
        "readonly_graph": readonly_graph,
        "source_integrity": source_integrity,
        "fixture_integrity": fixture_integrity,
        "repository_source_integrity": source_repository_integrity,
        "tool_integrity": tool_integrity,
        "tool_hashes_before": tool_hashes,
        "tool_hashes_after": tool_hashes_after,
        "target_verifier_header_count": len(headers),
        "target_verifier_headers": headers,
        "full_verification_exit": stages["full-verification"].get("exit"),
        "first_verifier_error": errors[0] if errors else None,
        "all_verifier_errors": errors,
        "source_alter_control": fixture["source_alter_control"],
        "fixture": fixture,
        "stages": stages,
    }
    (args.evidence / "outcome.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"classification": result["classification"],
                      "first_verifier_error": result["first_verifier_error"],
                      "stages": {key: row.get("exit") for key, row in stages.items()},
                      "full_graphs_captured": graph_complete}, sort_keys=True),
          flush=True)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--tool-home", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--compiler-sysroot", required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--deadline-epoch", type=int, required=True)
    args = parser.parse_args()
    args.compiler_sysroot = str(Path(args.compiler_sysroot).resolve())
    execute(args)


if __name__ == "__main__":
    main()
