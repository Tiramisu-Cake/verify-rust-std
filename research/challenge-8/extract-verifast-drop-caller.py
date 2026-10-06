#!/usr/bin/env python3
"""Prepare isolated same-unit local-Drop caller proof fixtures.

The exact CopyOnDrop source block and its currently reviewed method contract
are obtained from extract-verifast-drop.py. This file only assembles caller
fixtures; all Rust compilation, MIR export, and VeriFast execution are hosted.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
from pathlib import Path


FIXTURE_SHA256 = "73cda1789bfb1ab3c1a3ec7a5a85a5ba305019579d5f716b59015f34d8538e30"
SOURCE_SHA256 = "32574fd06623190132f213cbfeaeca5bd466e3c802ca97a2174e24fd3c240959"
CASES = (
    "cleanup_one",
    "cleanup_callback",
    "negative_missing_source",
    "negative_missing_destination",
    "negative_missing_own",
    "negative_unannotated_drop",
    "unsupported_extra_field",
    "unsupported_copy_bound",
)
PREFIX = b"#![no_std]\nuse core::ptr;\n\n"
CASE_RE = re.compile(rb"(?ms)^// CASE_BEGIN ([a-z_]+)\n(.*?)^// CASE_END \1\n")
GHOST_BLOCK_RE = re.compile(rb"(?s)/\*@.*?@\*/")
GHOST_LINE_RE = re.compile(rb"(?m)^\s*//@[^\n]*(?:\n|$)")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_direct_extractor(path: Path):
    spec = importlib.util.spec_from_file_location("verifast_drop_extractor", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load the direct Drop extractor")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def extract_cases(fixture: bytes) -> dict[str, bytes]:
    cases = {match.group(1).decode(): match.group(2) for match in CASE_RE.finditer(fixture)}
    if set(cases) != set(CASES) or len(CASES) != len(list(CASE_RE.finditer(fixture))):
        raise ValueError("caller fixture markers are missing, duplicated, or unexpected")
    return cases


def function_line(source: bytes, name: str) -> int:
    match = re.search(rb"(?m)^pub (?:unsafe )?fn " + re.escape(name.encode()) + rb"\b", source)
    if match is None:
        raise ValueError(f"caller function not found: {name}")
    return source[: match.start()].count(b"\n") + 1


def source_line_containing(source: bytes, token: bytes) -> int:
    match = re.search(rb"(?m)^.*" + re.escape(token) + rb".*$", source)
    if match is None:
        raise ValueError(f"caller source anchor missing: {token!r}")
    return source[: match.start()].count(b"\n") + 1


def scope_end_line(source: bytes) -> int:
    anchor = source.find(b"let _guard =")
    if anchor < 0:
        raise ValueError("local guard construction anchor missing")
    close = source.find(b"\n}", anchor)
    if close < 0:
        raise ValueError("local guard scope end not found")
    return source[: close + 1].count(b"\n") + 1


def strip_ghost(source: bytes) -> bytes:
    stripped = GHOST_BLOCK_RE.sub(b"", source)
    stripped = GHOST_LINE_RE.sub(b"", stripped)
    return stripped


def assemble_drop_block(
    original_drop: bytes, verified_drop: bytes, caller: bytes
) -> tuple[bytes, bytes]:
    if not original_drop.startswith(PREFIX) or not verified_drop.startswith(PREFIX):
        raise ValueError("direct extractor emitted an unexpected crate prefix")
    original_block = original_drop[len(PREFIX) :]
    verified_block = verified_drop[len(PREFIX) :]
    verified = PREFIX + verified_block + b"\n" + caller
    original_caller = strip_ghost(caller)
    original = PREFIX + original_block + b"\n" + original_caller
    if strip_ghost(verified) != original:
        raise ValueError("caller fixture ghost stripping changed non-ghost bytes")
    return original, verified


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--direct-extractor", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()

    source_bytes = args.source.read_bytes()
    if sha256(source_bytes) != SOURCE_SHA256:
        raise ValueError("pinned SmallSort source SHA-256 mismatch")
    fixture_bytes = args.fixture.read_bytes()
    fixture_hash = sha256(fixture_bytes)
    if fixture_hash != FIXTURE_SHA256:
        raise ValueError("caller fixture SHA-256 mismatch")
    cases = extract_cases(fixture_bytes)
    if args.output.exists() or args.evidence.exists():
        raise FileExistsError("refusing to overwrite caller extraction evidence")

    direct = load_direct_extractor(args.direct_extractor)
    direct_dir = args.output / "direct-drop"
    direct_evidence = args.output / "direct-drop-extraction.json"
    direct.extract(args.source, direct_dir, direct_evidence)
    direct_report = json.loads(direct_evidence.read_text())
    if direct_report.get("source_sha256") != SOURCE_SHA256 or not direct_report.get("ghost_strip_exact_bytes"):
        raise ValueError("canonical direct Drop extraction audit failed")
    canonical_original = (direct_dir / "original" / "lib.rs").read_bytes()
    canonical_verified = (direct_dir / "verified" / "lib.rs").read_bytes()

    report_cases: dict[str, dict[str, object]] = {}
    for name in CASES:
        if name == "negative_unannotated_drop":
            original, verified = assemble_drop_block(canonical_original, canonical_original, cases[name])
        else:
            original, verified = assemble_drop_block(canonical_original, canonical_verified, cases[name])
        case_dir = args.output / name
        if case_dir.exists():
            raise FileExistsError(f"refusing to reuse case directory: {case_dir}")
        original_path = case_dir / "original" / "lib.rs"
        verified_path = case_dir / "verified" / "lib.rs"
        original_path.parent.mkdir(parents=True)
        verified_path.parent.mkdir(parents=True)
        original_path.write_bytes(original)
        verified_path.write_bytes(verified)
        expected = "frontend_reject" if name.startswith("unsupported_") else (
            "generic_reject" if name == "negative_unannotated_drop" else
            "fail" if name.startswith("negative_") else "pass"
        )
        report_cases[name] = {
            "expected": expected,
            "original": str(original_path),
            "original_sha256": sha256(original),
            "verified": str(verified_path),
            "verified_sha256": sha256(verified),
            "ghost_strip_exact_bytes": strip_ghost(verified) == original,
            "drop_contract_present": name != "negative_unannotated_drop",
            "target_copy_call_line": direct_report["target_copy_call_line"],
            "caller_function_line": function_line(verified, name),
            "caller_record_line": source_line_containing(verified, b"let _guard ="),
            "caller_drop_line": scope_end_line(verified),
            "callback_call_line": source_line_containing(verified, b"callback();") if name == "cleanup_callback" else None,
        }
        if not report_cases[name]["ghost_strip_exact_bytes"]:
            raise ValueError(f"ghost strip audit failed for {name}")

    # The deliberately false postcondition is a separate full-unit body gate.
    # Its precondition remains the reviewed satisfiable contract; only the
    # destination equality obligation is made impossible after the copy.
    broken_name = "negative_broken_drop_post"
    # Isolate the defective explicit callee contract: there is no caller here
    # whose failed use of an invalid summary could masquerade as a body failure.
    broken_caller = b""
    original, verified = assemble_drop_block(canonical_original, canonical_verified, broken_caller)
    correct_post = b"dst[..len] |-> src_values &*&"
    false_post = b"dst[..len] |-> ?actual_values &*& actual_values != src_values &*&"
    if verified.count(correct_post) != 1:
        raise ValueError("could not uniquely locate the direct Drop destination postcondition")
    verified = verified.replace(correct_post, false_post, 1)
    if strip_ghost(verified) != original:
        raise ValueError("broken-postcondition fixture changed Rust bytes outside ghost comments")
    broken_dir = args.output / broken_name
    if broken_dir.exists():
        raise FileExistsError(f"refusing to reuse case directory: {broken_dir}")
    (broken_dir / "original").mkdir(parents=True)
    (broken_dir / "verified").mkdir(parents=True)
    (broken_dir / "original" / "lib.rs").write_bytes(original)
    (broken_dir / "verified" / "lib.rs").write_bytes(verified)
    report_cases[broken_name] = {
        "expected": "actual_drop_body_failure",
        "original": str(broken_dir / "original" / "lib.rs"),
        "original_sha256": sha256(original),
        "verified": str(broken_dir / "verified" / "lib.rs"),
        "verified_sha256": sha256(verified),
        "ghost_strip_exact_bytes": strip_ghost(verified) == original,
        "drop_contract_present": True,
        "target_copy_call_line": direct_report["target_copy_call_line"],
        "broken_postcondition": "destination values differ from copied source values",
    }

    report = {
        "selection": "verifast_local_drop_caller_gate",
        "source_sha256": SOURCE_SHA256,
        "fixture_sha256": fixture_hash,
        "direct_drop_contract_sha256": direct_report["contract_sha256"],
        "direct_drop_block_sha256": direct_report["block_sha256"],
        "direct_drop_block_bytes": direct_report["block_bytes"],
        "target_name": direct_report["expected_target_name"],
        "cases": report_cases,
        "all_ghost_strip_audits_exact": all(bool(v["ghost_strip_exact_bytes"]) for v in report_cases.values()),
    }
    args.evidence.parent.mkdir(parents=True, exist_ok=True)
    args.evidence.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
