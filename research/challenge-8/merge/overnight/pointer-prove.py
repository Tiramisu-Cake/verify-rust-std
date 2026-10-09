#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted stock-VeriFast harness for isolated merge pointer/index projections."""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
FIXTURE = HERE / "wrapping-cases.rs"
MERGE_PROVE = HERE.parent / "stock-26.10/prove.py"
TIMEOUT_SECONDS = 30
EXPECTED_COMPILER_PANIC_SHA256 = "b63eeb2d8e1fa130d3582253fd043fdcd722d16031b289c25f2437e2edda87dd"
CASE_MARKER = re.compile(rb"(?m)^// CASE_BEGIN ([a-z0-9_]+)\r?\n(.*?)^// CASE_END \1\r?\n", re.S)
ANNOTATION_BLOCK = re.compile(rb"/\*@.*?@\*/", re.S)
ANNOTATION_LINE = re.compile(rb"(?m)^[ \t]*//@[^\r\n]*(?:\r?\n|$)")
FN = re.compile(rb"(?m)^[ \t]*(?:pub\s+)?(?:unsafe\s+)?fn\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?:<[^\r\n{}]*>)?\s*\(")
LEMMA = re.compile(rb"\blem\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?:<[^>{}]*>)?\s*\(")
EXPECTED_ERROR = re.compile(rb"(?m)^\s*// EXPECT_ERROR (\{[^\r\n]*\})\s*$")
EXPECTED_REJECTION = re.compile(rb"(?m)^\s*// EXPECT_REJECTION (\{[^\r\n]*\})\s*$")
EXPECTED_DEAD = re.compile(rb"(?m)^\s*// EXPECT_DEAD (\{[^\r\n]*\})\s*$")
TARGET = re.compile(rb"// TARGET(?:_NEGATIVE)?(?:\s|:|$)")

HEADER_ANY = re.compile(r"^\s*\d+(?:\.\d+)?s: ([^\s(]+)\((\d+),\d+(?:-\d+(?:,\d+)?)?\): Verifying function '([^']+)'$", re.M)
EXECUTION = re.compile(r"^\s*\d+(?:\.\d+)?s: ([^\s(]+)\((\d+),\d+-\d+(?:,\d+)?\): (?:note: )?Executing statement$", re.M)
RETURN = re.compile(r"^\s*\d+(?:\.\d+)?s: ([^\n]*?): Executing return statement$", re.M)
ERROR = re.compile(r"^.*?: error: .*$", re.M)
DEAD = re.compile(r"(?m)^.*?: dead code(?:[ \t][^\r\n]*)?$", re.I)
DEAD_RECORD = re.compile(
    r"^([^()\r\n]+)\((\d+),(\d+)(?:-(\d+))?\): dead code[ \t]*$"
)
ASSERTION_ERROR = re.compile(
    r"^verified/lib\.rs\((\d+),(\d+)-(\d+)\): error: Assertion might not hold\. \(Cannot prove ([^\n]*)\.\)$",
    re.M,
)


def resolve_target_coordinate(value: object, target_line: int, label: str) -> int:
    """Resolve only a small, explicit relative-coordinate grammar; never eval it."""
    if not isinstance(value, str):
        raise ValueError(f"{label} must be TARGET, TARGET+N, or TARGET-N")
    match = re.fullmatch(r"TARGET(?:([+-])([1-9][0-9]*))?", value)
    if match is None:
        raise ValueError(f"{label} must be TARGET, TARGET+N, or TARGET-N")
    if match.group(1) is None:
        resolved = target_line
    else:
        distance = int(match.group(2))
        resolved = target_line + distance if match.group(1) == "+" else target_line - distance
    if resolved < 1:
        raise ValueError(f"{label} resolves before the start of the source")
    return resolved


def parse_dead_records(log: str) -> list[dict]:
    records = []
    for line in DEAD.findall(log):
        match = DEAD_RECORD.fullmatch(line)
        if match is None:
            # The line is still dead-code evidence, but it cannot satisfy the
            # exact location oracle.
            continue
        filename, lineno, column_start, column_end = match.groups()
        records.append({
            "file": filename,
            "line": int(lineno),
            "column_start": int(column_start),
            "column_end": int(column_end) if column_end is not None else None,
            "message": "dead code",
        })
    return records


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def strip_annotations(data: bytes) -> bytes:
    return ANNOTATION_LINE.sub(b"", ANNOTATION_BLOCK.sub(b"", data))


def check_assumption_boundary(name: str, verified: bytes, mutations: bool = True) -> dict | None:
    """Admit the single actual runtime assume, never a ghost proof assumption.

    The caller has already run the frozen whole-source admission gate. This
    extra byte check binds the only exception to the unchanged complete actual
    bidirectional body; it supplies no verifier summary or assumption itself.
    """
    forbidden = list(re.finditer(rb"\bassume(?:_correct)?\s*\(|\blemma_auto\b", verified))
    if not forbidden:
        return None
    runtime_line = b"        intrinsics::assume(len_div_2 != 0); // This can avoid useless code-gen."
    if len(forbidden) != 1 or verified.count(runtime_line) != 1:
        raise RuntimeError(f"{name}: assumptions and automatic lemmas are forbidden")
    line_start = verified.index(runtime_line)
    if forbidden[0].start() != line_start + runtime_line.index(b"assume("):
        raise RuntimeError(f"{name}: only the exact actual runtime assume is admissible")
    actual_source = (ROOT / "library/core/src/slice/sort/shared/smallsort.rs").read_bytes()
    signature = b"unsafe fn bidirectional_merge<T: FreezeMarker, F: FnMut(&T, &T) -> bool>("
    if actual_source.count(signature) != 1:
        raise RuntimeError(f"{name}: ambiguous pinned bidirectional source")
    start = actual_source.index(signature)
    ending = re.search(rb"(?m)^}\r?\n", actual_source[start:])
    if ending is None:
        raise RuntimeError(f"{name}: missing pinned bidirectional body")
    actual = actual_source[start:start + ending.end()].rstrip(b"\r\n")
    original = strip_annotations(verified)
    if original.count(actual) != 1 or original.count(runtime_line) != 1:
        raise RuntimeError(f"{name}: runtime assume requires byte-identical actual body")
    certificate = {"kind": "actual_runtime_assume", "function": "bidirectional_merge",
                   "exact_body_sha256": sha(actual), "statement": runtime_line.decode(),
                   "obligation": "runtime primitive still requires its Boolean precondition; no ghost assumption"}
    if mutations:
        checks = {}
        for label, changed in (
            ("extra_ghost_assume", verified + b"\n//@ assume(false);\n"),
            ("automatic_lemma", verified + b"\n//@ lemma_auto fake();\n"),
            ("wrong_runtime_condition", verified.replace(runtime_line, runtime_line.replace(b"!= 0", b"== 0"))),
            ("ghost_instead_of_runtime", verified.replace(runtime_line, b"/*@\n" + runtime_line + b"\n@*/")),
            ("wrong_function", verified.replace(signature, signature.replace(b"bidirectional_merge", b"other_merge"))),
        ):
            try:
                check_assumption_boundary(name, changed, False)
                checks[label] = False
            except RuntimeError:
                checks[label] = True
        if not all(checks.values()):
            raise RuntimeError(f"{name}: runtime assumption boundary did not fail closed")
        certificate["fail_closed_mutations"] = checks
    return certificate


def body_names(source: bytes) -> list[str]:
    functions = [m.group(1).decode("ascii") for m in FN.finditer(source)]
    lemmas = [m.group(1).decode("ascii") for m in LEMMA.finditer(source)]
    names = functions + lemmas
    if not names or len(names) != len(set(names)):
        raise RuntimeError(f"each isolated case must have unique checked body names; found {names}")
    return names


def line_ranges(source: bytes) -> dict[str, tuple[int, int]]:
    """Conservative brace ranges for proving that each recorded line is in a body."""
    text = source.decode("utf-8")
    # Preserve line/byte coordinates while ignoring braces in specification
    # comments. Actual std has its opening brace on the signature line; ghost
    # injection must not change that runtime spelling to suit this scanner.
    masked = ANNOTATION_LINE.sub(lambda m: re.sub(rb"[^\r\n]", b" ", m.group()),
        ANNOTATION_BLOCK.sub(lambda m: re.sub(rb"[^\r\n]", b" ", m.group()), source))
    masked_text = masked.decode("utf-8")
    result: dict[str, tuple[int, int]] = {}
    for match in FN.finditer(source):
        name = match.group(1).decode("ascii")
        body_open = re.search(rb"\{", masked[match.end():])
        if body_open is None:
            raise RuntimeError(f"missing function body: {name}")
        opening = len(source[:match.end() + body_open.start()].decode("utf-8"))
        depth, closing = 0, -1
        for offset in range(opening, len(text)):
            if masked_text[offset] == "{":
                depth += 1
            elif masked_text[offset] == "}":
                depth -= 1
                if depth == 0:
                    closing = offset
                    break
        if closing < 0:
            raise RuntimeError(f"unclosed function body: {name}")
        result[name] = (text.count("\n", 0, opening) + 1, text.count("\n", 0, closing) + 1)
    for match in LEMMA.finditer(source):
        name = match.group(1).decode("ascii")
        body_open = re.search(rb"(?m)^\{[ \t]*$", source[match.end():])
        if body_open is None:
            raise RuntimeError(f"missing checked lemma body: {name}")
        opening = len(source[:match.end() + body_open.start()].decode("utf-8"))
        depth, closing = 0, -1
        for offset in range(opening, len(text)):
            if text[offset] == "{":
                depth += 1
            elif text[offset] == "}":
                depth -= 1
                if depth == 0:
                    closing = offset
                    break
        if closing < 0:
            raise RuntimeError(f"unclosed checked lemma body: {name}")
        result[name] = (text.count("\n", 0, opening) + 1, text.count("\n", 0, closing) + 1)
    return result


def read_cases(fixture: Path, workdir: Path, selected: list[str] | None = None) -> tuple[dict, dict[str, tuple[bytes, bytes]]]:
    raw = fixture.read_bytes()
    all_matches = list(CASE_MARKER.finditer(raw))
    if not all_matches:
        raise RuntimeError("pointer-cases.rs has no CASE_BEGIN/CASE_END cases")
    names = [m.group(1).decode("ascii") for m in all_matches]
    if len(names) != len(set(names)):
        raise RuntimeError(f"duplicate case names: {names}")
    # A selected later case must not inherit earlier fixture bodies as helpers.
    # The first marker follows only the file-level comments; each case is standalone.
    prefix = raw[:all_matches[0].start()]
    matches = all_matches
    if selected is not None:
        unknown = sorted(set(selected) - set(names))
        if unknown:
            raise RuntimeError(f"--cases names absent from fixture: {unknown}")
        selected_set = set(selected)
        matches = [match for match in matches if match.group(1).decode("ascii") in selected_set]
        names = [match.group(1).decode("ascii") for match in matches]
        if not names:
            raise RuntimeError("--cases selected no cases")
    # The prefix is shared setup only. Body accounting includes any declarations
    # there, so they remain subject to the same exact-body verification gate.
    cases = {}
    files = {}
    for name, match in zip(names, matches):
        body = match.group(2)
        verified = prefix + body
        original = strip_annotations(verified)
        # Expected-diagnostic JSON is an ordinary line comment; messages may
        # quote the marker name without introducing a runtime expression.
        if b"mir_stack_addr" in EXPECTED_REJECTION.sub(b"", original):
            raise RuntimeError(f"{name}: stack address marker outside ghost annotations")
        if strip_annotations(verified) != original:
            raise RuntimeError(f"{name}: ghost stripping is not byte deterministic")
        runtime_assumption = check_assumption_boundary(name, verified)
        all_names = body_names(verified)
        ranges = line_ranges(verified)
        if strip_annotations(verified) != original:
            raise RuntimeError(f"{name}: original runtime bytes changed during ghost stripping")

        declared = list(EXPECTED_ERROR.finditer(body))
        if len(declared) > 1:
            raise RuntimeError(f"{name}: expected at most one predeclared EXPECT_ERROR")
        dead_declared = list(EXPECTED_DEAD.finditer(body))
        if len(dead_declared) > 1:
            raise RuntimeError(f"{name}: expected at most one predeclared EXPECT_DEAD")
        expected = None
        expected_dead = None
        target_offsets = [m.start() for m in TARGET.finditer(body)]
        if declared:
            if dead_declared:
                raise RuntimeError(f"{name}: EXPECT_ERROR and EXPECT_DEAD cannot be combined")
            try:
                expected = json.loads(declared[0].group(1).decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise RuntimeError(f"{name}: malformed EXPECT_ERROR JSON: {exc}") from exc
            required = {"stage", "predicate", "line", "column_start", "column_end"}
            if set(expected) != required:
                raise RuntimeError(f"{name}: EXPECT_ERROR fields must be exactly {sorted(required)}")
            if expected["stage"] != "verifast" or not isinstance(expected["predicate"], str):
                raise RuntimeError(f"{name}: only exact VeriFast assertion predicates are classifiable")
            if not expected["predicate"]:
                raise RuntimeError(f"{name}: EXPECT_ERROR predicate cannot be empty")
            if len(target_offsets) != 1:
                raise RuntimeError(f"{name}: a negative requires exactly one // TARGET")
            prefix_body_lines = (prefix.count(b"\n") +
                                 body[:target_offsets[0]].count(b"\n") + 1)
            if expected["line"] == "TARGET":
                expected["line"] = prefix_body_lines
            elif expected["line"] != prefix_body_lines:
                raise RuntimeError(f"{name}: EXPECT_ERROR line must equal the marked TARGET line {prefix_body_lines}")
            if not (isinstance(expected["column_start"], int) and
                    isinstance(expected["column_end"], int) and
                    1 <= expected["column_start"] < expected["column_end"]):
                raise RuntimeError(f"{name}: invalid EXPECT_ERROR column range")
        elif dead_declared:
            if len(target_offsets) != 1:
                raise RuntimeError(f"{name}: EXPECT_DEAD requires exactly one // TARGET")
            if list(EXPECTED_REJECTION.finditer(body)):
                raise RuntimeError(f"{name}: EXPECT_DEAD cannot be combined with EXPECT_REJECTION")
            try:
                expected_dead = json.loads(dead_declared[0].group(1).decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise RuntimeError(f"{name}: malformed EXPECT_DEAD JSON: {exc}") from exc
            if (not isinstance(expected_dead, dict) or
                    set(expected_dead) != {"target_line", "predecessor_line", "dead_records"}):
                raise RuntimeError(f"{name}: EXPECT_DEAD fields must be target_line, predecessor_line, dead_records")
            target_line = (prefix.count(b"\n") +
                           body[:target_offsets[0]].count(b"\n") + 1)
            try:
                expected_dead["target_line"] = resolve_target_coordinate(
                    expected_dead["target_line"], target_line, "EXPECT_DEAD.target_line")
                expected_dead["predecessor_line"] = resolve_target_coordinate(
                    expected_dead["predecessor_line"], target_line, "EXPECT_DEAD.predecessor_line")
            except ValueError as exc:
                raise RuntimeError(f"{name}: {exc}") from exc
            if expected_dead["predecessor_line"] != target_line - 1:
                raise RuntimeError(f"{name}: predecessor_line must identify the immediately preceding source line")
            records = expected_dead["dead_records"]
            if not isinstance(records, list) or len(records) != 2:
                raise RuntimeError(f"{name}: EXPECT_DEAD requires exactly two ordered dead_records")
            normalized_records = []
            for index, record in enumerate(records):
                if not isinstance(record, dict) or set(record) != {
                        "file", "line", "column_start", "column_end", "message"}:
                    raise RuntimeError(f"{name}: malformed EXPECT_DEAD record {index}")
                if record["file"] != "verified/lib.rs" or record["message"] != "dead code":
                    raise RuntimeError(f"{name}: EXPECT_DEAD records must name verified/lib.rs dead code")
                try:
                    line = resolve_target_coordinate(record["line"], target_line,
                                                     f"EXPECT_DEAD.dead_records[{index}].line")
                except ValueError as exc:
                    raise RuntimeError(f"{name}: {exc}") from exc
                start = record["column_start"]
                end = record["column_end"]
                if type(start) is not int or start < 1 or (end is not None and
                        (type(end) is not int or end <= start)):
                    raise RuntimeError(f"{name}: invalid dead-code column range in record {index}")
                normalized_records.append({"file": record["file"], "line": line,
                    "column_start": start, "column_end": end, "message": record["message"]})
            expected_dead["dead_records"] = normalized_records
            if normalized_records[0]["line"] != target_line:
                raise RuntimeError(f"{name}: TARGET must be the first dead-code record")
            if (normalized_records[0]["column_start"] != 5 or
                    normalized_records[0]["column_end"] != 6 or
                    normalized_records[1] != {"file": "verified/lib.rs", "line": target_line + 1,
                        "column_start": 2, "column_end": None, "message": "dead code"}):
                raise RuntimeError(f"{name}: EXPECT_DEAD must name the exact expression and closing-brace diagnostics")
            owner_names = [body_name for body_name in all_names
                           if ranges[body_name][0] <= target_line <= ranges[body_name][1]]
            if len(owner_names) != 1:
                raise RuntimeError(f"{name}: TARGET must be inside exactly one checked body")
            owner = ranges[owner_names[0]]
            if not (owner[0] <= expected_dead["predecessor_line"] <= owner[1]) or any(
                    not (owner[0] <= record["line"] <= owner[1])
                    for record in normalized_records):
                raise RuntimeError(f"{name}: predecessor and dead records must stay inside TARGET's body")
            if name != "unreachable_body_after_panic" or all_names != [name]:
                raise RuntimeError(f"{name}: EXPECT_DEAD is reserved for the exact panic baseline body")
            source_lines = verified.decode("utf-8").splitlines()
            predecessor_text = source_lines[expected_dead["predecessor_line"] - 1].strip()
            target_text = source_lines[target_line - 1].strip()
            if (re.fullmatch(r'assert!\(false, "unreachable-body baseline"\);', predecessor_text) is None or
                    re.match(r"^0\s*// TARGET\b", target_text) is None or
                    source_lines[target_line].strip() != "}"):
                raise RuntimeError(f"{name}: EXPECT_DEAD source anchor changed")
            expected_dead["owner_body"] = owner_names[0]
        elif target_offsets:
            if len(target_offsets) != 1:
                raise RuntimeError(f"{name}: expected at most one TARGET marker")
            # Calibration negatives can deliberately lack a final diagnostic
            # oracle. They still run all applicable stages and remain
            # INCONCLUSIVE regardless of what a later log happens to show.

        case_dir = workdir / name
        (case_dir / "original").mkdir(parents=True, exist_ok=False)
        (case_dir / "verified").mkdir(parents=True, exist_ok=False)
        orig_path = case_dir / "original/lib.rs"
        verified_path = case_dir / "verified/lib.rs"
        orig_path.write_bytes(original)
        verified_path.write_bytes(verified)
        meta = {
            "case": name,
            "negative": expected is not None,
            "unclassified_target": bool(target_offsets) and expected is None,
            "case_scope": ("negative obligation; no acceptance without exact predeclared metadata"
                           if target_offsets else
                           "operation support probe only: true normal post; establishes no pointer/index bridge"
                          if re.search(rb"\bens\s+true\s*;", verified) else
                          "isolated pointer/index proof projection"),
            "expected_error": expected,
            "expected_dead": expected_dead,
            "marked_target_line": (prefix.count(b"\n") +
                                   body[:target_offsets[0]].count(b"\n") + 1
                                   if target_offsets else None),
            "expected_bodies": all_names,
            "rust_function_names": [m.group(1).decode("ascii") for m in FN.finditer(verified)],
            "function_line_ranges": ranges,
            "verified_sha256": sha(verified),
            "original_sha256": sha(original),
            "ghost_strip_exact_bytes": True,
        }
        rejection_matches = list(EXPECTED_REJECTION.finditer(body))
        if rejection_matches:
            if len(rejection_matches) != 1 or len(target_offsets) != 1 or expected is not None:
                raise RuntimeError(f"{name}: exactly one distinct rejection oracle and TARGET required")
            rejection = json.loads(rejection_matches[0].group(1))
            if not isinstance(rejection, dict):
                raise RuntimeError(f"{name}: rejection oracle must be a JSON object")
            rejection_fields = {"kind", "error_file", "error_line", "column_start", "column_end", "message"}
            if set(rejection) not in (rejection_fields, rejection_fields | {"error_end_line"}):
                raise RuntimeError(f"{name}: invalid rejection oracle fields")
            if rejection["kind"] not in (
                    "primitive_precondition", "memory_permission", "unwind_post",
                    "tuple_resource", "leak_check", "frontend_admission"):
                raise RuntimeError(f"{name}: unsupported rejection kind")
            target_line = prefix.count(b"\n") + body[:target_offsets[0]].count(b"\n") + 1
            rejection["target_line"] = target_line
            if rejection["error_line"] == "TARGET":
                rejection["error_line"] = target_line
            error_end_line = rejection.get("error_end_line", rejection["error_line"])
            if (not isinstance(rejection["error_file"], str) or not rejection["error_file"] or
                    type(rejection["error_line"]) is not int or rejection["error_line"] < 1 or
                    type(error_end_line) is not int or error_end_line < rejection["error_line"] or
                    type(rejection["column_start"]) is not int or rejection["column_start"] < 1 or
                    type(rejection["column_end"]) is not int or
                    rejection["column_end"] < 1 or
                    (error_end_line == rejection["error_line"] and
                     rejection["column_end"] <= rejection["column_start"]) or
                    not isinstance(rejection["message"], str) or not rejection["message"]):
                raise RuntimeError(f"{name}: rejection oracle requires an exact positive location and message")
            target_owners = [body_name for body_name in all_names
                             if ranges[body_name][0] <= target_line <= ranges[body_name][1]]
            if len(target_owners) != 1:
                raise RuntimeError(f"{name}: rejection TARGET must lie in exactly one checked body")
            meta["expected_rejection"] = rejection
            # A validated exact oracle classifies this TARGET; retain strict outer audit.
            meta["unclassified_target"] = False
            meta["marked_target_line"] = target_line
            meta["negative"] = True
            meta["case_scope"] = (
                "exact cleanup frontend admission rejection; checked body must remain unentered"
                if rejection["kind"] == "frontend_admission" else
                "exact intended proof/resource rejection; marked checked body must execute"
            )
        meta["runtime_assumption_boundary"] = runtime_assumption
        (case_dir / "metadata.json").write_text(json.dumps(meta, indent=2) + "\n")
        cases[name] = meta
        files[name] = (orig_path.read_bytes(), verified_path.read_bytes())
    manifest = {"fixture_sha256": sha(raw), "case_order": names, "cases": cases}
    (workdir / "extraction.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest, files


def hashes(case_dir: Path) -> dict[str, str]:
    return {
        "original/lib.rs": sha((case_dir / "original/lib.rs").read_bytes()),
        "verified/lib.rs": sha((case_dir / "verified/lib.rs").read_bytes()),
    }


def run_stage(name: str, stage: str, argv: list[str], case_dir: Path,
              timeout_seconds: int = TIMEOUT_SECONDS, stdin_path: Path | None = None,
              combine_output: bool = False) -> int:
    before = hashes(case_dir)
    stdout_path, stderr_path = case_dir / f"{stage}.out", case_dir / f"{stage}.log"
    resources = case_dir / f"{stage}-resources.txt"
    bounded_argv = ["timeout", "--signal=TERM", "--kill-after=2s", f"{timeout_seconds}s", *argv]
    cmd = ["/usr/bin/time", "-v", "-o", str(resources), *bounded_argv]
    try:
        with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
            output = stderr if combine_output else stdout
            if stdin_path is None:
                completed = subprocess.run(cmd, cwd=case_dir, stdout=output,
                                           stderr=subprocess.STDOUT if combine_output else stderr,
                                           timeout=timeout_seconds + 5, check=False)
            else:
                with stdin_path.open("rb") as source:
                    completed = subprocess.run(cmd, cwd=case_dir, stdin=source, stdout=output,
                                               stderr=subprocess.STDOUT if combine_output else stderr,
                                               timeout=timeout_seconds + 5, check=False)
        status = completed.returncode
    except subprocess.TimeoutExpired as exc:
        status = 124
        with stderr_path.open("ab") as stderr:
            stderr.write(f"\nSTAGE_TIMEOUT after {timeout_seconds}s: {exc}\n".encode())
    except OSError as exc:
        status = 127
        stderr_path.write_text(f"could not start stage: {exc}\n")
    after = hashes(case_dir)
    integrity = {"stage": stage, "command": cmd, "exit_code": status,
                 "source_before": before, "source_after": after,
                 "unchanged": before == after}
    (case_dir / f"source-integrity-{stage}.json").write_text(json.dumps(integrity, indent=2) + "\n")
    (case_dir / f"{stage}-exit-code.txt").write_text(f"{status}\n")
    return status


def stage_case(name: str, metadata: dict, args, schema: Path) -> dict:
    case_dir = args.workdir / name
    orig = case_dir / "original/lib.rs"
    verified = case_dir / "verified/lib.rs"
    initial = hashes(case_dir)
    (case_dir / "source-before-sha256.json").write_text(json.dumps(initial, indent=2) + "\n")
    exporter = run_stage(name, "exporter", [
        str(args.tool_home / "bin/vf-rust-mir-exporter"), "verified/lib.rs",
        f"--sysroot={args.compiler_sysroot}", "--edition", "2021", "--crate-type", "lib",
        "--vf-rust-mir-exporter:preprocess-readonly",
    ], case_dir)
    mir = case_dir / "exporter.out"
    (case_dir / "compiler-mir.bin").write_bytes(mir.read_bytes())
    if exporter == 0:
        decoder = run_stage(name, "decode", ["capnp", "decode", str(schema), "VfMir"],
                            case_dir, stdin_path=mir)
    else:
        decoder = 125
        (case_dir / "decode.out").write_bytes(b"")
        (case_dir / "decode.log").write_text("not run because readonly MIR export failed\n")
        (case_dir / "decode-resources.txt").write_text("stage not run\n")
        (case_dir / "source-integrity-decode.json").write_text(json.dumps({
            "stage": "decode", "exit_code": decoder, "unchanged": hashes(case_dir) == initial,
            "status": "not_run_export_failed", "source_before": hashes(case_dir),
            "source_after": hashes(case_dir),
        }, indent=2) + "\n")
        (case_dir / "decode-exit-code.txt").write_text(f"{decoder}\n")
    (case_dir / "compiler-mir-sha256.txt").write_text(sha(mir.read_bytes()) + "\n")
    stack_stages: dict[str, int] = {}
    stack_requested = b"mir_stack_addr" in verified.read_bytes()
    if stack_requested and name in {"bidirectional_merge_len2", "bidirectional_merge_len23"}:
        # Stock VF uses normal in-memory ghost preprocessing, unlike the
        # independent readonly export above. Bind actual IDs to that mode.
        normal_command = [str(args.tool_home / "bin/vf-rust-mir-exporter"),
                          "verified/lib.rs", f"--sysroot={args.compiler_sysroot}",
                          "--edition", "2021"]
        stack_stages["normal_exporter"] = run_stage(
            name, "normal-exporter", normal_command, case_dir)
        normal_mir = case_dir / "normal-exporter.out"
        stack_stages["normal_decode"] = (
            run_stage(name, "normal-decode", ["capnp", "decode", str(schema), "VfMir"],
                      case_dir, stdin_path=normal_mir)
            if stack_stages["normal_exporter"] == 0 else 125)
        if stack_stages["normal_decode"] == 0:
            provenance = case_dir / "normal-exporter-provenance.json"
            provenance.write_text(json.dumps({
                "normal_preprocess": True, "command": normal_command,
                "source_sha256": initial["verified/lib.rs"],
                "source_unchanged": hashes(case_dir) == initial,
                "mir_sha256": sha(normal_mir.read_bytes()),
                "decoded_sha256": sha((case_dir / "normal-decode.out").read_bytes()),
                "github_sha": os.environ["GITHUB_SHA"],
                "github_run_id": os.environ["GITHUB_RUN_ID"],
            }, indent=2) + "\n")
            stack_command = [sys.executable, str(HERE / "stack-address-admission.py"),
                "--decoded-normal", str(case_dir / "normal-decode.out"),
                "--mir", str(normal_mir), "--source", str(verified),
                "--provenance", str(provenance),
                "--expected-source-sha256", initial["verified/lib.rs"], "--require-final"]
            stack_stages["roles"] = run_stage(name, "stack-roles", stack_command +
                ["--output", str(case_dir / "stack-roles.json")], case_dir)
        else:
            stack_stages["roles"] = 125
    if exporter == 0 and decoder == 0:
        prover_args = ["-prover", args.prover] if args.prover else []
        verifier = run_stage(name, "verifast", [
            str(args.tool_home / "bin/verifast"), "-rustc_args", "--edition 2021",
            *prover_args,
            "-verbose", "1", "-dump_ast_with_locs", "proof-ast.ml", "verified/lib.rs",
        ], case_dir, timeout_seconds=args.verifier_seconds, combine_output=True)
    else:
        verifier = 125
        (case_dir / "verifast.out").write_bytes(b"")
        (case_dir / "verifast.log").write_text("not run because readonly MIR export/decode failed\n")
        (case_dir / "verifast-resources.txt").write_text("stage not run\n")
        (case_dir / "source-integrity-verifast.json").write_text(json.dumps({
            "stage": "verifast", "exit_code": verifier, "unchanged": hashes(case_dir) == initial,
            "status": "not_run_export_or_decode_failed", "source_before": hashes(case_dir),
            "source_after": hashes(case_dir),
        }, indent=2) + "\n")
        (case_dir / "verifast-exit-code.txt").write_text(f"{verifier}\n")

    if stack_stages:
        # Same-input syntactic linkage is independent of the body proof.
        # Its success never substitutes for any existing verifier gate.
        if stack_stages.get("roles") == 0 and (case_dir / "proof-ast.ml").is_file():
            stack_stages["proof_ast"] = run_stage(name, "stack-proof-ast", [
                sys.executable, str(HERE / "stack-proof-ast-admission.py"),
                "--proof-ast", str(case_dir / "proof-ast.ml"),
                "--roles", str(case_dir / "stack-roles.json"),
                "--source", str(verified),
                "--output", str(case_dir / "stack-proof-ast.json"),
            ], case_dir)
        else:
            stack_stages["proof_ast"] = 125
        (case_dir / "stack-proof-ast-status.json").write_text(json.dumps({
            "status": "AST_LINKED" if stack_stages["proof_ast"] == 0 else "OPEN",
            "exit_code": stack_stages["proof_ast"],
            "proof_ast_sha256": (sha((case_dir / "proof-ast.ml").read_bytes())
                if (case_dir / "proof-ast.ml").is_file() else None),
        }, indent=2) + "\n")
        if (stack_stages.get("roles") == 0 and
                (case_dir / "proof-ast.ml").is_file()):
            panic_macro_stage = run_stage(name, "panic-macro-origin", [
                sys.executable, str(HERE / "panic-macro-admission.py"),
                "--normal-decoded", str(case_dir / "normal-decode.out"),
                "--normal-mir", str(case_dir / "normal-exporter.out"),
                "--proof-ast", str(case_dir / "proof-ast.ml"),
                "--source", str(verified),
                "--provenance", str(case_dir / "normal-exporter-provenance.json"),
                "--compiler-sysroot", str(args.compiler_sysroot),
                "--verifast-log", str(case_dir / "verifast.log"),
                "--require-final",
                "--expected-compiler-panic-sha256", EXPECTED_COMPILER_PANIC_SHA256,
                "--output", str(case_dir / "panic-macro-origin.json"),
            ], case_dir)
            stack_stages["panic_macro_origin"] = panic_macro_stage

    panic_macro_evidence = None
    if "panic_on_ord_violation" in metadata["expected_bodies"]:
        certificate_path = case_dir / "panic-macro-origin.json"
        certificate = None
        if certificate_path.is_file():
            try:
                certificate = json.loads(certificate_path.read_text())
            except (OSError, json.JSONDecodeError):
                certificate = None
        def file_sha(path: Path) -> str | None:
            return sha(path.read_bytes()) if path.is_file() else None
        panic_source = verified.read_bytes()
        panic_log = (case_dir / "verifast.log").read_bytes()
        panic_macro_evidence = {
            "certificate": certificate,
            "support_stages": dict(stack_stages),
            "source_sha256": sha(panic_source),
            "source_initial_sha256": initial.get("verified/lib.rs"),
            "normal_mir_sha256": file_sha(case_dir / "normal-exporter.out"),
            "normal_decoded_sha256": file_sha(case_dir / "normal-decode.out"),
            "proof_ast_sha256": file_sha(case_dir / "proof-ast.ml"),
            "verifast_log_sha256": sha(panic_log),
            "github_sha": os.environ.get("GITHUB_SHA"),
            "github_run_id": os.environ.get("GITHUB_RUN_ID"),
            "expected_compiler_panic_sha256": EXPECTED_COMPILER_PANIC_SHA256,
            "compiler_panic_path": str((Path(args.compiler_sysroot) /
                "lib/rustlib/src/rust/library/core/src/panic.rs").resolve()),
        }

    # Refinement is independent of VF success, and always receives the stripped
    # original and full ghost-annotated projection.
    refinement = run_stage(name, "refinement", [
        str(args.tool_home / "bin/refinement-checker"), "--rustc-args", "--edition 2021",
        "original/lib.rs", "verified/lib.rs",
    ], case_dir)
    after = hashes(case_dir)
    all_integrity = [json.loads(path.read_text()) for path in sorted(case_dir.glob("source-integrity-*.json"))]
    unchanged = initial == after and all(item.get("unchanged") is True for item in all_integrity)
    (case_dir / "source-after-sha256.json").write_text(json.dumps(after, indent=2) + "\n")
    (case_dir / "source-unchanged.txt").write_text(f"{str(unchanged).lower()}\n")
    log_path = case_dir / "verifast.log"
    log = log_path.read_text(errors="replace")
    result = classify(name, metadata, {
        "exporter": exporter, "decode": decoder, "verifast": verifier,
        "refinement": refinement,
    }, log, unchanged, panic_macro_evidence=panic_macro_evidence)
    result.update({"case": name, "case_scope": metadata["case_scope"],
                   "source_before": initial, "source_after": after,
                   "source_unchanged_at_every_stage": unchanged,
                   "refinement_scope": "isolated Rust projection fixture only; not refinement of full bidirectional_merge"})
    stage_diagnostics = {}
    for stage in ("exporter", "decode", "verifast", "refinement"):
        chunks = []
        for path in (case_dir / f"{stage}.log", case_dir / f"{stage}.out"):
            if path.is_file():
                chunks.append(path.read_text(errors="replace"))
        lines = "\n".join(chunks).splitlines()
        candidates = [line.strip() for line in lines if re.search(
            r"error:|dead code|unsupported|not yet supported|todo:|failed|timeout|cannot prove|cannot establish",
            line, re.I)]
        stage_diagnostics[stage] = {
            "exit_code": result["stages"].get(stage),
            "first_diagnostic": candidates[0] if candidates else next((line.strip() for line in lines if line.strip()), ""),
        }
    if stack_stages:
        stack_complete = all(code == 0 for code in stack_stages.values())
        result["stack_address_admission"] = {"stages": stack_stages,
                                             "complete": stack_complete}
        if not stack_complete:
            result["classification"] = "INCONCLUSIVE"
            result["additional_admission_failure"] = "normal-MIR/role/proof-AST stack address certificate incomplete"
    if ("panic_on_ord_violation" in metadata["expected_bodies"] and
            not result["panic_macro_origin"]["accepted"]):
        result["classification"] = "INCONCLUSIVE"
        result["full_positive_gate"] = False
        result["additional_admission_failure"] = (
            "panic macro-origin certificate rejected: " +
            result["panic_macro_origin"]["reason"])
    result["stage_diagnostics"] = stage_diagnostics
    result["first_failure"] = next(({
        "stage": stage, "exit_code": stage_diagnostics[stage]["exit_code"],
        "diagnostic": stage_diagnostics[stage]["first_diagnostic"],
    } for stage in ("exporter", "decode", "verifast", "refinement")
       if stage_diagnostics[stage]["exit_code"] not in (0, 125)), None)
    (case_dir / "classification.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


PANIC_ORIGIN_CONTROL_NAMES = {
    "wrong_owner", "wrong_literal", "wrong_unwind_edge", "wrong_macro_span",
    "duplicate_owner", "wrong_source_hash", "wrong_compiler_version",
    "wrong_compiler_path", "wrong_compiler_source_hash", "missing_macro_call_log",
    "missing_unwind_return_log", "initializers_only_log", "ast_return_suppressed",
}


def panic_macro_execution_credit(metadata: dict, log: str,
                                 evidence: dict | None) -> tuple[int, dict]:
    """Credit external panic! spans only from a final same-input certificate."""
    result = {"accepted": False, "credited_records": 0, "reason": "missing certificate context"}
    if "panic_on_ord_violation" not in metadata.get("expected_bodies", []):
        return 0, {"accepted": True, "credited_records": 0, "reason": "not applicable"}
    try:
        if not isinstance(evidence, dict):
            return 0, result
        cert = evidence.get("certificate")
        if not isinstance(cert, dict):
            return 0, result
        expected_stages = {
            "normal_exporter": 0, "normal_decode": 0, "roles": 0,
            "proof_ast": 0, "panic_macro_origin": 0,
        }
        if evidence.get("support_stages") != expected_stages:
            result["reason"] = "normal MIR/role/AST/final-certificate stages incomplete"
            return 0, result
        if cert.get("status") != "PANIC_MACRO_BODY_ORIGIN_LINKED" or cert.get("require_final") is not True:
            result["reason"] = "certificate is calibration-only or not final"
            return 0, result
        if cert.get("function") != "panic_on_ord_violation":
            result["reason"] = "certificate owner mismatch"
            return 0, result
        for field in ("source_sha256", "normal_mir_sha256", "normal_decoded_sha256",
                      "proof_ast_sha256", "verifast_log_sha256"):
            if (not isinstance(evidence.get(field), str) or
                    cert.get(field) != evidence[field]):
                result["reason"] = f"certificate {field} does not match current input"
                return 0, result
        if evidence.get("source_initial_sha256") != evidence.get("source_sha256"):
            result["reason"] = "checked source differs from initial source snapshot"
            return 0, result
        github_sha = evidence.get("github_sha")
        github_run_id = evidence.get("github_run_id")
        if (not isinstance(github_sha, str) or not re.fullmatch(r"[0-9a-f]{40}", github_sha) or
                cert.get("github_sha") != github_sha or
                not isinstance(github_run_id, str) or not github_run_id.isdigit() or
                cert.get("github_run_id") != github_run_id):
            result["reason"] = "certificate GitHub source/run does not match current job"
            return 0, result
        if (evidence.get("expected_compiler_panic_sha256") != EXPECTED_COMPILER_PANIC_SHA256 or
                cert.get("expected_compiler_panic_rs_sha256") != EXPECTED_COMPILER_PANIC_SHA256 or
                cert.get("compiler_panic_rs_sha256") != EXPECTED_COMPILER_PANIC_SHA256 or
                cert.get("compiler_panic_rs") != evidence.get("compiler_panic_path")):
            result["reason"] = "compiler panic source pin/path mismatch"
            return 0, result
        counts = cert.get("log")
        if (type(cert.get("body_execution_records")) is not int or
                cert["body_execution_records"] != 3 or not isinstance(counts, dict) or
                type(counts.get("body_execution_records")) is not int or
                counts["body_execution_records"] != 3 or
                counts.get("verified_macro_calls") != 2 or
                counts.get("unwind_return_records") != 1 or
                counts.get("leak_check_records") != 1):
            result["reason"] = "certificate execution/return/leak counts are not exact"
            return 0, result
        controls = cert.get("negative_controls")
        if (not isinstance(controls, list) or len(controls) != len(PANIC_ORIGIN_CONTROL_NAMES) or
                set(controls) != PANIC_ORIGIN_CONTROL_NAMES):
            result["reason"] = "certificate fail-closed control set is incomplete"
            return 0, result
        if (cert.get("original_source_sha256") != "85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1" or
                cert.get("original_source_git_blob") != "40939f922bcb6fdc7ee0d30427fa861827043827"):
            result["reason"] = "certificate actual-source pin mismatch"
            return 0, result
        if sha(log.encode("utf-8")) != evidence.get("verifast_log_sha256"):
            result["reason"] = "current VeriFast log bytes differ from certificate input"
            return 0, result
    except (AttributeError, KeyError, TypeError, ValueError):
        result["reason"] = "malformed panic-origin certificate context"
        return 0, result
    return 3, {"accepted": True, "credited_records": 3,
               "reason": "final same-input panic macro origin certificate"}


def classify(name: str, metadata: dict, stages: dict[str, int], log: str,
             unchanged: bool, mutation_checks: bool = True,
             panic_macro_evidence: dict | None = None) -> dict:
    header_matches = list(HEADER_ANY.finditer(log))
    own_headers = [m for m in header_matches if m.group(1).endswith("verified/lib.rs")]
    headers = [m.group(3) for m in own_headers]
    execution_lines = [int(m.group(2)) for m in EXECUTION.finditer(log)
                       if m.group(1).endswith("verified/lib.rs")]
    ranges = metadata["function_line_ranges"]
    body_execution = {
        function: sum(ranges[function][0] <= line <= ranges[function][1] for line in execution_lines)
        for function in metadata["expected_bodies"]
    }
    panic_credit, panic_origin_status = panic_macro_execution_credit(
        metadata, log, panic_macro_evidence)
    if "panic_on_ord_violation" in body_execution:
        body_execution["panic_on_ord_violation"] += panic_credit
    body_records = {}
    for index, match in enumerate(header_matches):
        if not match.group(1).endswith("verified/lib.rs"):
            continue
        end = header_matches[index + 1].start() if index + 1 < len(header_matches) else len(log)
        segment = log[match.end():end]
        function = match.group(3)
        body_records[function] = {
            "return": len(RETURN.findall(segment)),
            "leak": len(re.findall(r"\bLeak check\.", segment)),
        }
    errors = ERROR.findall(log)
    dead_code = DEAD.findall(log)
    leak_checks = len(re.findall(r"\bLeak check\.", log))
    return_checks = sum(record["return"] for record in body_records.values())
    leak_checks = sum(record["leak"] for record in body_records.values())
    bodies_ok = sorted(headers) == sorted(metadata["expected_bodies"])
    full_stages = all(stages.get(stage) == 0 for stage in ("exporter", "decode", "verifast", "refinement"))
    full_vf = (stages.get("verifast") == 0 and not errors and not dead_code and bodies_ok and
               all(body_execution.get(function, 0) > 0 for function in metadata["expected_bodies"]) and
               all(body_records.get(function, {}).get("return", 0) > 0 and
                   body_records.get(function, {}).get("leak", 0) > 0
                   for function in metadata["expected_bodies"]) and
               re.search(
                   r"0 errors found \(\d+ statements verified\)"
                   r"(?: \(target: x86_64-unknown-linux-gnu \(LP64\)\))?\s*$",
                   log,
               ) is not None)
    negative = metadata.get("expected_error")
    negative_ok = False
    error_evidence = None
    if negative is not None:
        error_matches = list(ASSERTION_ERROR.finditer(log))
        if len(error_matches) == 1:
            match = error_matches[0]
            line, col_start, col_end, predicate = match.groups()
            target_exec = int(line) in execution_lines
            error_evidence = {"line": int(line), "column_start": int(col_start),
                              "column_end": int(col_end), "predicate": predicate,
                              "target_executed": target_exec}
            negative_ok = (
                negative["stage"] == "verifast" and stages.get("exporter") == 0 and
                stages.get("decode") == 0 and stages.get("refinement") == 0 and
                stages.get("verifast") == 1 and unchanged and bodies_ok and
                not dead_code and len(errors) == 1 and target_exec and
                body_execution.get(next((body for body in metadata["expected_bodies"]
                                         if ranges[body][0] <= int(line) <= ranges[body][1]), ""), 0) > 0 and
                int(line) == negative["line"] and int(col_start) == negative["column_start"] and
                int(col_end) == negative["column_end"] and predicate == negative["predicate"]
            )
    expected_dead = metadata.get("expected_dead")
    expected_dead_ok = False
    dead_evidence = parse_dead_records(log)
    classification = ("PASS" if unchanged and full_stages and full_vf and
                      panic_origin_status["accepted"] else "INCONCLUSIVE")
    if negative is not None:
        classification = "EXPECTED_FALSE_ASSERTION" if negative_ok else "INCONCLUSIVE"
    elif expected_dead is not None:
        target_line = expected_dead["target_line"]
        predecessor_line = expected_dead["predecessor_line"]
        expected_owner = expected_dead["owner_body"]
        expected_records = expected_dead["dead_records"]
        body_range = ranges.get(expected_owner, (0, -1))
        target_inside_owner = body_range[0] <= target_line <= body_range[1]
        predecessor_inside_owner = body_range[0] <= predecessor_line <= body_range[1]
        dead_inside_owner = all(body_range[0] <= record["line"] <= body_range[1]
                                for record in expected_records)
        expected_dead_ok = (
            stages == {"exporter": 0, "decode": 0, "verifast": 1, "refinement": 0} and
            unchanged and bodies_ok and metadata["expected_bodies"] == [expected_owner] and
            metadata.get("marked_target_line") == target_line and
            target_inside_owner and predecessor_inside_owner and dead_inside_owner and
            expected_records[0]["line"] == target_line and
            expected_dead["predecessor_line"] == target_line - 1 and
            body_execution.get(expected_owner, 0) > 0 and
            predecessor_line in execution_lines and target_line not in execution_lines and
            body_records.get(expected_owner, {}).get("return", 0) > 0 and
            body_records.get(expected_owner, {}).get("leak", 0) > 0 and
            not errors and len(dead_code) == 2 and len(dead_evidence) == 2 and
            dead_evidence == expected_records
        )
        classification = "EXPECTED_DEAD_CODE" if expected_dead_ok else "INCONCLUSIVE"
    elif metadata.get("unclassified_target"):
        classification = "INCONCLUSIVE"
    rejection = metadata.get("expected_rejection")
    rejection_ok = False
    admission_rejection = bool(rejection and rejection["kind"] == "frontend_admission")
    if rejection:
        matching = re.findall(
            r"^([^\n]+?)\((\d+),(\d+)-(?:((?:\d+),))?(\d+)\): error: ([^\n]+)$",
            log, re.M)
        if len(matching) == 1:
            filename, line, start, end_line_prefix, end, message = matching[0]
            observed_end_line = int(end_line_prefix[:-1]) if end_line_prefix else int(line)
            rejection_ok = (
                filename.endswith(rejection["error_file"]) and
                int(line) == rejection["error_line"] and
                observed_end_line == rejection.get("error_end_line", rejection["error_line"]) and
                int(start) == rejection["column_start"] and
                int(end) == rejection["column_end"] and message == rejection["message"] and
                stages == {"exporter": 0, "decode": 0, "verifast": 1, "refinement": 0} and
                unchanged and not dead_code and len(errors) == 1 and
                rejection["target_line"] == metadata["marked_target_line"] and
                any(ranges[function][0] <= rejection["target_line"] <= ranges[function][1]
                    for function in metadata["expected_bodies"]) and
                ((admission_rejection and len(metadata["expected_bodies"]) == 1 and not own_headers and
                  all(body_execution.get(function, 0) == 0 for function in metadata["expected_bodies"])) or
                 (not admission_rejection and bodies_ok and rejection["target_line"] in execution_lines and
                  all(body_execution.get(function, 0) > 0 for function in metadata["expected_bodies"])))
            )
        classification = (
            "EXPECTED_ADMISSION_REJECTION" if rejection_ok and admission_rejection else
            "EXPECTED_REJECTION" if rejection_ok else "INCONCLUSIVE"
        )
    if ("panic_on_ord_violation" in metadata["expected_bodies"] and
            not panic_origin_status["accepted"]):
        classification = "INCONCLUSIVE"
    result = {
        "classification": classification,
        "stages": stages,
        "expected_bodies": metadata["expected_bodies"],
        "visited_bodies": headers,
        "body_execution_records": body_execution,
        "per_body_records": body_records,
        "return_records": return_checks,
        "leak_check_records": leak_checks,
        "error_lines": errors,
        "dead_code_records": dead_code,
        "expected_dead_code": expected_dead,
        "observed_dead_code_records": dead_evidence,
        "expected_dead_code_gate": expected_dead_ok,
        "expected_error": negative,
        "observed_error": error_evidence,
        "full_positive_gate": (full_stages and full_vf and unchanged and
                               ("panic_on_ord_violation" not in metadata["expected_bodies"] or
                                panic_origin_status["accepted"])),
        "expected_rejection": rejection,
        "intended_rejection_gate": rejection_ok,
        "rejection_class": ("frontend_admission" if admission_rejection else
                            "proof" if rejection else None),
        "admission_body_entered": (bool(own_headers) or
                                   any(body_execution.get(function, 0) > 0
                                       for function in metadata["expected_bodies"]))
                                  if admission_rejection else None,
        "panic_macro_origin": panic_origin_status,
    }
    if mutation_checks:
        checks = classifier_mutations(metadata, stages, log, unchanged, result,
                                      panic_macro_evidence)
        if rejection:
            expected_rejection_status = ("EXPECTED_ADMISSION_REJECTION" if admission_rejection
                                         else "EXPECTED_REJECTION")
            for stage in stages:
                mutant = dict(stages)
                mutant[stage] = 124
                checks[f"rejection_stage_{stage}"] = classify(name, metadata, mutant, log, unchanged, False)["classification"] != expected_rejection_status
            rejection_mutants = [
                ("source_changed", log, False),
                ("extra_error", log + "verified/lib.rs(1,1-2): error: unrelated\n", unchanged),
                ("dead_code", log + "verified/lib.rs(1,1-2): dead code\n", unchanged),
                ("message", log.replace(rejection["message"], "unrelated failure"), unchanged),
                ("file", log.replace(rejection["error_file"], "unrelated-file.rs"), unchanged),
            ]
            if admission_rejection:
                target = rejection["target_line"]
                fabricated_entry = log + (
                    f"0.001s: verified/lib.rs({target},1-2): Verifying function '"
                    f"{metadata['expected_bodies'][0]}'\n"
                    f"0.002s: verified/lib.rs({target},1-2): Executing statement\n"
                )
                checks["rejection_fabricated_body_execution"] = classify(
                    name, metadata, stages, fabricated_entry, unchanged, False
                )["classification"] != expected_rejection_status
            else:
                rejection_mutants.append((
                    "missing_body", re.sub(r"^.*Verifying function .*\n", "", log, flags=re.M), unchanged))
                rejection_mutants.append((
                    "missing_execution", re.sub(r"^.*Executing statement\n", "", log, flags=re.M), unchanged))
            for label, changed_log, changed_source in rejection_mutants:
                checks[f"rejection_{label}"] = classify(name, metadata, stages, changed_log, changed_source, False)["classification"] != expected_rejection_status
            rejection_location_fields = ["error_line", "column_start", "column_end", "target_line"]
            if "error_end_line" in rejection:
                rejection_location_fields.append("error_end_line")
            for field in rejection_location_fields:
                changed_meta = dict(metadata)
                changed_meta["expected_rejection"] = dict(rejection)
                changed_meta["expected_rejection"][field] += 1
                checks[f"rejection_{field}"] = classify(name, changed_meta, stages, log, unchanged, False)["classification"] != expected_rejection_status
            changed_kind = dict(metadata)
            changed_kind["expected_rejection"] = dict(rejection)
            changed_kind["expected_rejection"]["kind"] = (
                "memory_permission" if admission_rejection else "frontend_admission")
            checks["rejection_kind"] = classify(
                name, changed_kind, stages, log, unchanged, False
            )["classification"] != expected_rejection_status
        result["classifier_fail_closed_mutations"] = checks
        if not all(checks.values()):
            result["classification"] = "INCONCLUSIVE"
    return result


def classifier_mutations(metadata: dict, stages: dict[str, int], log: str,
                         unchanged: bool, baseline: dict,
                         panic_macro_evidence: dict | None = None) -> dict[str, bool]:
    """Hosted self-checks: perturb exact evidence and ensure no false acceptance."""
    checks: dict[str, bool] = {}
    case = metadata["case"]
    expected_dead = metadata.get("expected_dead")
    if expected_dead is not None:
        expected_class = "EXPECTED_DEAD_CODE"
        for key in ("exporter", "decode", "verifast", "refinement"):
            mutant_stages = dict(stages)
            mutant_stages[key] = 124
            checks[f"dead_stage_{key}"] = classify(
                case, metadata, mutant_stages, log, unchanged, False)["classification"] != expected_class

        owner = expected_dead["owner_body"]
        predecessor = expected_dead["predecessor_line"]
        target = expected_dead["target_line"]
        own_header = next((match for match in HEADER_ANY.finditer(log)
                           if match.group(1).endswith("verified/lib.rs") and
                           match.group(3) == owner), None)
        missing_body = log
        if own_header is not None:
            line_end = log.find("\n", own_header.start())
            missing_body = log[:own_header.start()] + log[line_end + 1:]
        checks["dead_missing_body"] = classify(
            case, metadata, stages, missing_body, unchanged, False)["classification"] != expected_class

        execution_pattern = re.compile(
            rf"(?m)^\s*\d+(?:\.\d+)?s: verified/lib\.rs\({predecessor},\d+-\d+\): "
            r"(?:note: )?Executing statement\r?\n?"
        )
        missing_predecessor = execution_pattern.sub("", log)
        checks["dead_missing_predecessor_execution"] = classify(
            case, metadata, stages, missing_predecessor, unchanged, False)["classification"] != expected_class
        missing_all_execution = re.sub(r"(?m)^.*Executing statement\r?\n?", "", log)
        checks["dead_missing_execution"] = classify(
            case, metadata, stages, missing_all_execution, unchanged, False)["classification"] != expected_class
        target_execution = log + f"0.001s: verified/lib.rs({target},1-2): Executing statement\n"
        checks["dead_target_executed"] = classify(
            case, metadata, stages, target_execution, unchanged, False)["classification"] != expected_class
        checks["dead_source_changed"] = classify(
            case, metadata, stages, log, False, False)["classification"] != expected_class
        checks["dead_extra_error"] = classify(
            case, metadata, stages, log + "verified/lib.rs(1,1-2): error: synthetic\n",
            unchanged, False)["classification"] != expected_class

        owner_start = own_header.start() if own_header is not None else 0
        owner_return = next((match for match in re.finditer(
            r"(?m)^.*: Executing return statement\r?\n?", log)
            if match.start() >= owner_start), None)
        missing_return = (log if owner_return is None else
                          log[:owner_return.start()] + log[owner_return.end():])
        checks["dead_missing_return"] = classify(
            case, metadata, stages, missing_return, unchanged, False
        )["classification"] != expected_class
        owner_leak = next((match for match in re.finditer(
            r"(?m)^.*: Leak check\.\r?\n?", log)
            if match.start() >= owner_start), None)
        missing_leak = (log if owner_leak is None else
                        log[:owner_leak.start()] + log[owner_leak.end():])
        checks["dead_missing_leak"] = classify(
            case, metadata, stages, missing_leak, unchanged, False
        )["classification"] != expected_class

        observed_dead_lines = DEAD.findall(log)
        for index, label in ((0, "first"), (1, "second")):
            if index < len(observed_dead_lines):
                removed = log.replace(observed_dead_lines[index] + "\n", "", 1)
                if removed == log:
                    removed = log.replace(observed_dead_lines[index], "", 1)
                checks[f"dead_removed_{label}"] = classify(
                    case, metadata, stages, removed, unchanged, False)["classification"] != expected_class
                wrong_file = observed_dead_lines[index].replace("verified/lib.rs", "wrong.rs", 1)
                checks[f"dead_wrong_file_{label}"] = classify(
                    case, metadata, stages, log.replace(observed_dead_lines[index], wrong_file, 1),
                    unchanged, False)["classification"] != expected_class
                wrong_message = observed_dead_lines[index].replace("dead code", "dead-code", 1)
                checks[f"dead_wrong_message_{label}"] = classify(
                    case, metadata, stages, log.replace(observed_dead_lines[index], wrong_message, 1),
                    unchanged, False)["classification"] != expected_class
                location = DEAD_RECORD.fullmatch(observed_dead_lines[index])
                if location is not None:
                    old = observed_dead_lines[index]
                    line_mutant = re.sub(r"\((\d+),", lambda m: f"({int(m.group(1)) + 1},", old, count=1)
                    checks[f"dead_wrong_line_{label}"] = classify(
                        case, metadata, stages, log.replace(old, line_mutant, 1),
                        unchanged, False)["classification"] != expected_class
                    col_mutant = re.sub(r",(\d+)(?:-\d+)?\): dead code$",
                                        lambda m: f",{int(m.group(1)) + 1}): dead code", old, count=1)
                    checks[f"dead_wrong_column_{label}"] = classify(
                        case, metadata, stages, log.replace(old, col_mutant, 1),
                        unchanged, False)["classification"] != expected_class
        checks["dead_extra_record"] = classify(
            case, metadata, stages, log + "verified/lib.rs(12,2): dead code\n",
            unchanged, False)["classification"] != expected_class

        wrong_target = dict(metadata)
        wrong_target["expected_dead"] = dict(expected_dead)
        wrong_target["expected_dead"]["target_line"] = target + 1
        checks["dead_wrong_target_oracle"] = classify(
            case, wrong_target, stages, log, unchanged, False)["classification"] != expected_class
        wrong_predecessor = dict(metadata)
        wrong_predecessor["expected_dead"] = dict(expected_dead)
        wrong_predecessor["expected_dead"]["predecessor_line"] = predecessor + 1
        checks["dead_wrong_predecessor_oracle"] = classify(
            case, wrong_predecessor, stages, log, unchanged, False)["classification"] != expected_class
        return checks

    if metadata.get("expected_error") is None:
        # Positive class must fail closed on a single missing proof or integrity gate.
        for key in ("exporter", "decode", "verifast", "refinement"):
            mutant_stages = dict(stages)
            mutant_stages[key] = 124
            checks[f"positive_stage_{key}"] = classify(
                case, metadata, mutant_stages, log, unchanged, False,
                panic_macro_evidence=panic_macro_evidence)["classification"] != "PASS"
        for label, mutant_log, mutant_unchanged in (
            ("missing_body", re.sub(r"^.*Verifying function .*\n", "", log, flags=re.M), unchanged),
            ("error", log + "verified/lib.rs(1,1-2): error: synthetic\n", unchanged),
            ("dead_code", log + "verified/lib.rs(1,1-2): dead code\n", unchanged),
            ("source_changed", log, False),
        ):
            checks[f"positive_{label}"] = classify(
                case, metadata, stages, mutant_log, mutant_unchanged, False,
                panic_macro_evidence=panic_macro_evidence)["classification"] != "PASS"
        timeout_stages = dict(stages)
        timeout_stages["verifast"] = 124
        checks["positive_timeout"] = classify(
            case, metadata, timeout_stages, log, unchanged, False,
            panic_macro_evidence=panic_macro_evidence)["classification"] != "PASS"
        # Remove execution/return/leak traces independently.
        for label, mutant_log in (
            ("no_execution", re.sub(r"^.*Executing statement\n", "", log, flags=re.M)),
            ("no_return", re.sub(r"^.*Executing return statement\n", "", log, flags=re.M)),
            ("no_leak", log.replace("Leak check.", "Leak check removed.")),
        ):
            checks[f"positive_{label}"] = classify(
                case, metadata, stages, mutant_log, unchanged, False,
                panic_macro_evidence=panic_macro_evidence)["classification"] != "PASS"
    else:
        # An accepted negative must cease to classify when any exact component
        # changes, or when a setup/refinement/unrelated failure is substituted.
        expected = metadata["expected_error"]
        diagnostic = ASSERTION_ERROR.search(log)
        line_mutant = log
        column_mutant = log
        predicate_mutant = log
        if diagnostic is not None:
            diagnostic_text = diagnostic.group(0)
            changed_line = diagnostic_text.replace(
                f"verified/lib.rs({expected['line']},", f"verified/lib.rs({expected['line'] + 1},", 1)
            changed_column = diagnostic_text.replace(
                f"verified/lib.rs({expected['line']},{expected['column_start']}-{expected['column_end']})",
                f"verified/lib.rs({expected['line']},1-2)", 1)
            predicate_span = diagnostic.span(4)
            predicate_mutant = (log[:predicate_span[0]] + "synthetic_unrelated_predicate" +
                                log[predicate_span[1]:])
            line_mutant = log[:diagnostic.start()] + changed_line + log[diagnostic.end():]
            column_mutant = log[:diagnostic.start()] + changed_column + log[diagnostic.end():]
        own_header = next((match for match in HEADER_ANY.finditer(log)
                           if match.group(1).endswith("verified/lib.rs") and
                           match.group(3) in metadata["expected_bodies"]), None)
        missing_body_mutant = log
        if own_header is not None:
            line_end = log.find("\n", own_header.start())
            missing_body_mutant = log[:own_header.start()] + log[line_end + 1:]
        predicates = {"line": line_mutant, "column": column_mutant,
                      "predicate": predicate_mutant}
        for label, mutant in predicates.items():
            checks[f"negative_{label}"] = classify(case, metadata, stages, mutant, unchanged, False)["classification"] != "EXPECTED_FALSE_ASSERTION"
        checks["negative_missing_body"] = classify(case, metadata, stages, missing_body_mutant,
                                                    unchanged, False)["classification"] != "EXPECTED_FALSE_ASSERTION"
        for label, key, value in (("export", "exporter", 1), ("decode", "decode", 1),
                                  ("refinement", "refinement", 1), ("timeout", "verifast", 124)):
            mutant_stages = dict(stages)
            mutant_stages[key] = value
            checks[f"negative_{label}_stage"] = classify(case, metadata, mutant_stages, log, unchanged, False)["classification"] != "EXPECTED_FALSE_ASSERTION"
        checks["negative_source_changed"] = classify(case, metadata, stages, log, False, False)["classification"] != "EXPECTED_FALSE_ASSERTION"
        checks["negative_missing_target_execution"] = classify(case, metadata, stages,
            re.sub(rf"^.*\({expected['line']},\d+-\d+\): Executing statement\n", "", log, flags=re.M), unchanged, False)["classification"] != "EXPECTED_FALSE_ASSERTION"
    if "panic_on_ord_violation" in metadata.get("expected_bodies", []):
        valid_count, _ = panic_macro_execution_credit(metadata, log, panic_macro_evidence)
        checks["panic_origin_exact_three_records"] = valid_count == 3
        if valid_count != 3 or not isinstance(panic_macro_evidence, dict):
            checks["panic_origin_mutation_controls_not_run"] = False
        else:
            mutations = {}
            missing = copy.deepcopy(panic_macro_evidence)
            missing["certificate"] = None
            mutations["missing_certificate"] = (missing, log)
            stale = copy.deepcopy(panic_macro_evidence)
            stale["certificate"]["github_run_id"] = str(
                int(stale["certificate"].get("github_run_id", "0")) + 1)
            mutations["stale_certificate"] = (stale, log)
            owner = copy.deepcopy(panic_macro_evidence)
            owner["certificate"]["function"] = "some_other_function"
            mutations["wrong_owner"] = (owner, log)
            extra = copy.deepcopy(panic_macro_evidence)
            extra["certificate"]["body_execution_records"] = 4
            extra["certificate"]["log"]["body_execution_records"] = 4
            mutations["extra_execution_count"] = (extra, log)
            source = copy.deepcopy(panic_macro_evidence)
            source["source_sha256"] = "0" * 64
            mutations["wrong_source"] = (source, log)
            mutations["wrong_log"] = (copy.deepcopy(panic_macro_evidence),
                                      log + "\nsynthetic log mutation\n")
            compiler = copy.deepcopy(panic_macro_evidence)
            compiler["expected_compiler_panic_sha256"] = "0" * 64
            mutations["wrong_compiler"] = (compiler, log)
            calibration = copy.deepcopy(panic_macro_evidence)
            calibration["certificate"]["status"] = "CALIBRATION"
            calibration["certificate"]["require_final"] = False
            mutations["calibration_only"] = (calibration, log)
            incomplete_stage = copy.deepcopy(panic_macro_evidence)
            incomplete_stage["support_stages"]["proof_ast"] = 1
            mutations["incomplete_support_stage"] = (incomplete_stage, log)

            for label, (mutant_evidence, mutant_log) in mutations.items():
                credited, _ = panic_macro_execution_credit(metadata, mutant_log, mutant_evidence)
                mutant_classification = classify(
                    case, metadata, stages, mutant_log, unchanged, False,
                    panic_macro_evidence=mutant_evidence)["classification"]
                checks[f"panic_origin_{label}"] = credited == 0 and mutant_classification != "PASS"
    return checks


def load_admission() -> dict:
    spec = importlib.util.spec_from_file_location("merge_source_admission", MERGE_PROVE)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load merge/prove.py source admission")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # This function only reads the pinned file and builds a certificate. It does
    # not run a verifier, generator, compiler, or mutate the checkout.
    return module.admit_source()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tool-home", type=Path, required=True)
    parser.add_argument("--compiler-sysroot", required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--fixture", type=Path, default=FIXTURE)
    parser.add_argument("--profile", default="experimental-merge-wrapping-01-v1")
    parser.add_argument("--scope", default="isolated pointer/index projection fixtures; refinement is not whole bidirectional_merge")
    parser.add_argument("--cases", default="all",
                        help="comma-separated fixture cases, or all (default)")
    parser.add_argument("--verifier-seconds", type=int, default=TIMEOUT_SECONDS,
                        help="per-case hosted verifier limit, at most 600 seconds")
    parser.add_argument("--prover", choices=("Redux", "Z3v4.5"),
                        help="explicit existing bundled backend; default remains console default")
    args = parser.parse_args()
    if not 1 <= args.verifier_seconds <= 600:
        raise RuntimeError("verifier limit must be between 1 and 600 seconds")
    if (os.environ.get("GITHUB_ACTIONS") != "true" or
            os.environ.get("RUNNER_ENVIRONMENT") != "github-hosted" or
            os.environ.get("RUNNER_OS") != "Linux" or
            os.environ.get("GITHUB_REF") != "refs/heads/overnight/merge-26.10"):
        raise RuntimeError("pointer proof harness is restricted to hosted Linux Actions on overnight/merge-26.10")
    if args.evidence.exists():
        raise RuntimeError(f"refusing to reuse evidence directory: {args.evidence}")
    args.evidence.mkdir(parents=True)
    args.workdir = args.evidence / "cases"
    args.workdir.mkdir()
    admission = load_admission()
    admission_path = args.evidence / "full-small-sort-source-admission.json"
    admission_path.write_text(json.dumps(admission, indent=2) + "\n")
    tool = args.tool_home / "bin/verifast"
    for required in (tool, args.tool_home / "bin/vf-rust-mir-exporter",
                     args.tool_home / "bin/refinement-checker", args.schema):
        if not required.is_file():
            raise RuntimeError(f"required pinned hosted tool/schema missing: {required}")
    selected = None if args.cases == "all" else args.cases.split(",")
    if selected is not None and (any(not name for name in selected) or len(selected) != len(set(selected))):
        raise RuntimeError("--cases must be 'all' or a unique comma-separated case list")
    manifest, _files = read_cases(args.fixture, args.workdir, selected)
    (args.evidence / "fixture-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    results = {}
    for name in manifest["case_order"]:
        results[name] = stage_case(name, manifest["cases"][name], args, args.schema)
        print(f"{name}: {results[name]['classification']}", flush=True)
        (args.evidence / "results.json").write_text(json.dumps({
            "scope": args.scope,
            "profile": args.profile + "; base26.10-f76012fb518703b1d98e243ac4f487f16877cfcb; compiler-nightly-2026-09-25",
            "source_admission_sha256": sha(admission_path.read_bytes()),
            "cases": results,
        }, indent=2) + "\n")
    controls_ok = all(all(result["classifier_fail_closed_mutations"].values())
                      for result in results.values())
    (args.evidence / "aggregate.json").write_text(json.dumps({
        "evidence_collection_completed": True, "classifier_controls_passed": controls_ok,
        "cases": {name: row["classification"] for name, row in results.items()},
        "scope": args.scope,
    }, indent=2) + "\n")
    # Expected frontend/refinement/proof blockers are evidence, not harness
    # failures. A completed run remains green while preserving INCONCLUSIVE.
    return 0 if controls_ok else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print(f"pointer proof preparation failed: {error}", file=sys.stderr)
        sys.exit(2)
