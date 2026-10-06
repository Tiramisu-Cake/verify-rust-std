#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Prepare a hosted VeriFast diagnostic for the actual select_unpredictable body.

This script only extracts and annotates source. Compilation, MIR export, VeriFast,
and refinement checking must run on the GitHub-hosted workflow.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path


EXPECTED_HINT_BLOB = "fe59166363b9cc049c0d48f4349f4dc9c0e458b8"
EXPECTED_HINT_SHA256 = "d94ef86fbdac952fe7c9a6028536e15539b33dc188966fa4e9340fa7d94c30f8"
SIGNATURE = (
    b"pub const fn select_unpredictable<T>(condition: bool, true_val: T, false_val: T) -> T\n"
    b"where\n    T: [const] Destruct,\n{"
)
AFTER_FUNCTION = b"\n\n/// The expected temporal locality"
INTRINSIC_CALL = b"crate::intrinsics::select_unpredictable("
REQUIRED_BODY_FRAGMENTS = (
    b"let mut true_val = MaybeUninit::new(true_val);",
    b"let mut false_val = MaybeUninit::new(false_val);",
    b"struct DropOnPanic<T> {",
    b"unsafe { self.inner.drop_in_place() }",
    b"let guard = crate::intrinsics::select_unpredictable(condition, true_ptr, false_ptr);",
    b"let drop = crate::intrinsics::select_unpredictable(condition, false_ptr, true_ptr);",
    b"drop.drop_in_place();",
    b"crate::mem::forget(guard);",
    b"crate::intrinsics::select_unpredictable(condition, true_val, false_val).assume_init()",
)

# This adapter makes exactly the callee instantiation used by sort4:
# target T = *const Element, with no bound on Element. It removes only the
# const/Destruct surface so the body can be exported by the pinned compiler.
# The extracted Rust body itself is byte-identical to core::hint's body.
PREFIX = b"""#![feature(core_intrinsics)]
#![allow(internal_features)]

use std::mem::MaybeUninit;
use std::{intrinsics, mem};

pub fn select_unpredictable<Element>(
    condition: bool,
    true_val: *const Element,
    false_val: *const Element,
) -> *const Element
/*@
req thread_token(?t) &*& t == currentThread;
@*//*@
ens thread_token(t) &*& (result as pointer) ==
        (if condition { true_val as pointer } else { false_val as pointer });
@*//*@ on_unwind_ens false; @*/
"""

ORIGINAL_PREFIX = b"""#![feature(core_intrinsics)]
#![allow(internal_features)]

use std::mem::MaybeUninit;
use std::{intrinsics, mem};

pub fn select_unpredictable<Element>(
    condition: bool,
    true_val: *const Element,
    false_val: *const Element,
) -> *const Element

"""


def strip_ghost_contract(data: bytes) -> bytes:
    return re.sub(rb"/\*@.*?@\*/", b"", data, flags=re.S)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extract_body(source: bytes) -> bytes:
    if source.count(SIGNATURE) != 1:
        raise ValueError("expected exactly one pinned select_unpredictable signature")
    if sha256(source) != EXPECTED_HINT_SHA256:
        raise ValueError(f"hint.rs SHA-256 mismatch: {sha256(source)}")
    start = source.index(SIGNATURE) + len(SIGNATURE) - 1  # include opening brace

    # The target body contains nested Rust blocks. Ignore braces in comments and
    # literals while finding its exact closing brace.
    depth = 0
    i = start
    state = "code"
    block_depth = 0
    while i < len(source):
        byte = source[i]
        nxt = source[i + 1] if i + 1 < len(source) else 0
        if state == "line_comment":
            if byte == 0x0A:
                state = "code"
        elif state == "block_comment":
            if byte == 0x2F and nxt == 0x2A:
                block_depth += 1
                i += 1
            elif byte == 0x2A and nxt == 0x2F:
                block_depth -= 1
                i += 1
                if block_depth == 0:
                    state = "code"
        elif state == "string":
            if byte == 0x5C:
                i += 1
            elif byte == 0x22:
                state = "code"
        elif state == "char":
            if byte == 0x5C:
                i += 1
            elif byte == 0x27:
                state = "code"
        elif byte == 0x2F and nxt == 0x2F:
            state = "line_comment"
            i += 1
        elif byte == 0x2F and nxt == 0x2A:
            state = "block_comment"
            block_depth = 1
            i += 1
        elif byte == 0x22:
            state = "string"
        elif byte == 0x27:
            # The extracted body has no lifetimes or byte/char literals. Treat
            # apostrophes as chars only when a closing quote is nearby.
            closing = source.find(b"'", i + 1, min(len(source), i + 8))
            if closing >= 0:
                state = "char"
        elif byte == 0x7B:
            depth += 1
        elif byte == 0x7D:
            depth -= 1
            if depth == 0:
                body = source[start:i + 1]
                if source[i + 1:i + 1 + len(AFTER_FUNCTION)] != AFTER_FUNCTION:
                    raise ValueError("selected body no longer ends at the expected source anchor")
                return body
        i += 1
    raise ValueError("unterminated select_unpredictable body")


def prepare(source_path: Path, output: Path, evidence_path: Path) -> None:
    source = source_path.read_bytes()
    source_hash = sha256(source)
    if source_hash != EXPECTED_HINT_SHA256:
        raise ValueError(f"hint.rs SHA-256 mismatch: {source_hash}")
    blob = subprocess.check_output(["git", "hash-object", str(source_path)], text=True).strip()
    if blob != EXPECTED_HINT_BLOB:
        raise ValueError(f"hint.rs Git blob mismatch: {blob}")
    body = extract_body(source)
    if body.count(INTRINSIC_CALL) != 3:
        raise ValueError("the exact body must contain all three intrinsic selections")
    missing = [fragment.decode("ascii") for fragment in REQUIRED_BODY_FRAGMENTS if fragment not in body]
    if missing:
        raise ValueError("the source body changed; missing required fragments: " + ", ".join(missing))

    original = ORIGINAL_PREFIX + body + b"\n"
    verified = PREFIX + body + b"\n"
    if strip_ghost_contract(verified) != original:
        raise ValueError("adapter source differs beyond the documented signature and ghost contract")
    if original.count(body) != 1 or verified.count(body) != 1:
        raise ValueError("runtime body extraction is not unique")

    if output.exists() or evidence_path.exists():
        raise FileExistsError("refusing to overwrite prior select-callee evidence")
    (output / "original").mkdir(parents=True)
    (output / "verified").mkdir()
    (output / "original/lib.rs").write_bytes(original)
    (output / "verified/lib.rs").write_bytes(verified)
    body_line = verified[:verified.index(body)].count(b"\n") + 1
    (output / "extraction.json").write_text(json.dumps({
        "selection": "verifast_sort4_select_actual_callee",
        "source_path": str(source_path),
        "source_blob": EXPECTED_HINT_BLOB,
        "source_sha256": source_hash,
        "target_signature": "core::hint::select_unpredictable<T> where T: [const] Destruct",
        "adapter_signature": "select_unpredictable<Element>(..., *const Element, *const Element) -> *const Element",
        "adapter_domain": "exact target instantiation T = *const Element; Element unrestricted and no Copy bound",
        "adapter_notes": [
            "non-const proof adapter for the pinned 2026-02-05 compiler",
            "the complete Rust function body is byte-identical to the pinned target body",
            "namespaces map crate::mem and crate::intrinsics to std aliases; no intrinsic body/spec is supplied",
            "thread_token is returned; raw pointer values carry no Element ownership, and arbitrary abstract frame is preserved by the function frame rule",
            "this is a callee component only and does not prove selected storage ownership or actual sort4 integration",
        ],
        "body_source_line_in_fixture": body_line,
        "body_bytes": len(body),
        "body_sha256": sha256(body),
        "intrinsic_call_count": body.count(INTRINSIC_CALL),
        "drop_on_panic_body_retained": True,
        "original_sha256": sha256(original),
        "verified_sha256": sha256(verified),
        "verified_equals_original_after_ghost_strip": True,
        "full_pointer_model_equality_post": True,
        "unwind_post": "false for the *const Element instantiation; a failed proof remains inconclusive",
    }, indent=2, sort_keys=True) + "\n")
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(json.dumps({
        "source_sha256": source_hash,
        "body_sha256": sha256(body),
        "original_sha256": sha256(original),
        "verified_sha256": sha256(verified),
        "body_exact": True,
        "intrinsic_calls": 3,
        "ghost_strip_exact": True,
    }, indent=2, sort_keys=True) + "\n")


def file_hashes(paths: tuple[Path, ...], root: Path) -> dict[str, str]:
    return {str(path.relative_to(root)): sha256(path.read_bytes()) for path in paths}


def run_stage(argv: list[str | Path], cwd: Path, resource_path: Path,
              stdout_path: Path, stderr_path: Path | None = None) -> int:
    stderr_path = stdout_path if stderr_path is None else stderr_path
    with stdout_path.open("wb") as stdout:
        stderr = subprocess.STDOUT if stderr_path == stdout_path else stderr_path.open("wb")
        try:
            completed = subprocess.run(
                ["/usr/bin/time", "-v", "-o", str(resource_path), *map(str, argv)],
                cwd=cwd, stdout=stdout, stderr=stderr, check=False,
            )
            return completed.returncode
        except OSError as exc:
            stderr_path.write_text(f"could not start stage: {exc}\n")
            return 127
        finally:
            if stderr_path != stdout_path and hasattr(stderr, "close"):
                stderr.close()


def run_diagnostic(workdir: Path, schema: Path, tool_home: Path,
                   compiler_sysroot: str, evidence: Path) -> dict:
    if os.environ.get("GITHUB_ACTIONS") != "true" or \
            os.environ.get("RUNNER_ENVIRONMENT") != "github-hosted" or \
            os.environ.get("RUNNER_OS") != "Linux":
        raise RuntimeError("select_unpredictable verification requires GitHub-hosted Linux Actions")
    case = workdir / "actual_select_pointer"
    original = case / "original/lib.rs"
    verified = case / "verified/lib.rs"
    paths = (original, verified)
    before = file_hashes(paths, case)
    integrity = {}

    def audited(stage: str, argv: list[str | Path], stdout: Path,
                resources: Path, stderr: Path | None = None) -> int:
        pre = file_hashes(paths, case)
        status = run_stage(argv, case, resources, stdout, stderr)
        post = file_hashes(paths, case)
        integrity[stage] = {"before": pre, "after": post, "unchanged": pre == post}
        (case / f"source-integrity-{stage}.json").write_text(
            json.dumps(integrity[stage], indent=2, sort_keys=True) + "\n")
        (case / f"{stage}-exit-code.txt").write_text(f"{status}\n")
        return status

    exporter = audited("exporter", [
        tool_home / "bin/vf-rust-mir-exporter", "verified/lib.rs",
        f"--sysroot={compiler_sysroot}", "--edition", "2021", "--crate-type", "lib",
        "--vf-rust-mir-exporter:preprocess-readonly",
    ], case / "compiler-mir.bin", case / "exporter-resources.txt", case / "exporter.log")

    decode_log = case / "capnp-decode.log"
    if exporter == 0:
        pre = file_hashes(paths, case)
        with (case / "compiler-mir.bin").open("rb") as source, \
                (case / "compiler-mir.txt").open("wb") as decoded, decode_log.open("wb") as errors:
            try:
                proc = subprocess.run([
                    "/usr/bin/time", "-v", "-o", str(case / "decode-resources.txt"),
                    "capnp", "decode", str(schema), "VfMir",
                ], stdin=source, stdout=decoded, stderr=errors, check=False)
                decode = proc.returncode
            except OSError as exc:
                errors.write(f"could not start decoder: {exc}\n".encode())
                decode = 127
        post = file_hashes(paths, case)
        integrity["decoder"] = {"before": pre, "after": post, "unchanged": pre == post}
    else:
        decode = 125
        (case / "compiler-mir.txt").write_bytes(b"")
        decode_log.write_text("not run because MIR export failed\n")
        (case / "decode-resources.txt").write_text("stage not run\n")
        integrity["decoder"] = {"unchanged": True, "status": "not_run_export_failed"}
    (case / "decode-exit-code.txt").write_text(f"{decode}\n")
    (case / "source-integrity-decoder.json").write_text(
        json.dumps(integrity["decoder"], indent=2, sort_keys=True) + "\n")

    if exporter == 0 and decode == 0:
        vf = audited("verifast", [
            tool_home / "bin/verifast", "-rustc_args", "--edition 2021",
            "-verbose", "1", "verified/lib.rs",
        ], case / "verifast.log", case / "verifast-resources.txt")
    else:
        vf = 125
        (case / "verifast.log").write_text("not run because export/decode failed\n")
        (case / "verifast-resources.txt").write_text("stage not run\n")
        integrity["verifast"] = {"unchanged": True, "status": "not_run_export_or_decode_failed"}
        (case / "verifast-exit-code.txt").write_text("125\n")

    refinement = audited("refinement", [
        tool_home / "bin/refinement-checker", "--rustc-args", "--edition 2021",
        "original/lib.rs", "verified/lib.rs",
    ], case / "refinement.log", case / "refinement-resources.txt")
    after = file_hashes(paths, case)
    all_unchanged = before == after and all(item.get("unchanged", False)
                                            for item in integrity.values())
    (case / "source-after-sha256.json").write_text(json.dumps(after, indent=2, sort_keys=True) + "\n")
    log = (case / "verifast.log").read_text(errors="replace")
    first_error = next((line for line in log.splitlines() if ": error:" in line), None)
    headers = re.findall(
        r"^\s*\d+(?:\.\d+)?s: verified/lib\.rs\(\d+,\d+(?:-\d+(?:,\d+)?)?\): "
        r"Verifying function '([^']+)'$", log, re.M,
    )
    expected_header_count = sum(name == "select_unpredictable" for name in headers)
    stages_ok = exporter == 0 and decode == 0 and refinement == 0 and all_unchanged
    if stages_ok and vf == 0 and expected_header_count == 1:
        outcome = "PASS"
    elif exporter != 0 or decode != 0 or refinement != 0 or not all_unchanged:
        outcome = "INCONCLUSIVE_EXPORT_DECODE_REFINEMENT_OR_INTEGRITY"
    else:
        outcome = "INCONCLUSIVE_VERIFAST_PROOF_OR_FRONTEND_BLOCKER"
    missing_intrinsic = bool(first_error and re.search(
        r"(?:not found|unknown|unresolved|no function|no declaration).*"
        r"(?:std::intrinsics::select_unpredictable|select_unpredictable)|"
        r"(?:std::intrinsics::select_unpredictable|select_unpredictable).*"
        r"(?:not found|unknown|unresolved|no function|no declaration)",
        first_error, re.I,
    ))
    result = {
        "outcome": outcome,
        "exporter_exit": exporter,
        "decode_exit": decode,
        "verifast_exit": vf,
        "refinement_exit": refinement,
        "actual_callee_header_count": expected_header_count,
        "verifast_headers": headers,
        "first_verifast_error": first_error,
        "first_error_is_unresolved_select_intrinsic": missing_intrinsic,
        "source_unchanged_at_every_stage": all_unchanged,
        "stage_integrity": integrity,
    }
    (evidence / "classification.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main() -> None:
    if os.environ.get("GITHUB_ACTIONS") != "true" or \
            os.environ.get("RUNNER_ENVIRONMENT") != "github-hosted" or \
            os.environ.get("RUNNER_OS") != "Linux":
        raise SystemExit("select-callee extraction/checks require GitHub-hosted Linux Actions")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--workdir", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--tool-home", type=Path, required=True)
    parser.add_argument("--compiler-sysroot", required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    args.workdir.mkdir(parents=True, exist_ok=False)
    args.evidence.mkdir(parents=True, exist_ok=False)
    case = args.workdir / "actual_select_pointer"
    prepare(args.source, case, args.workdir / "extraction-integrity.json")
    result = run_diagnostic(args.workdir, args.schema, args.tool_home,
                            args.compiler_sysroot, args.evidence)
    print(json.dumps(result, sort_keys=True))
    if result["outcome"] == "PASS":
        return
    raise SystemExit(1)


if __name__ == "__main__":
    main()
