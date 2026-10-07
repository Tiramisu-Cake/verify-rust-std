#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted stock-VeriFast harness for isolated merge pointer/index projections."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FIXTURE = HERE / "pointer-cases.rs"
MERGE_PROVE = HERE / "prove.py"
TIMEOUT_SECONDS = 30
CASE_MARKER = re.compile(rb"(?m)^// CASE_BEGIN ([a-z0-9_]+)\r?\n(.*?)^// CASE_END \1\r?\n", re.S)
ANNOTATION_BLOCK = re.compile(rb"/\*@.*?@\*/", re.S)
ANNOTATION_LINE = re.compile(rb"(?m)^[ \t]*//@[^\r\n]*(?:\r?\n|$)")
FN = re.compile(rb"\b(?:pub\s+)?(?:unsafe\s+)?fn\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?:<[^>{}]*>)?\s*\(")
LEMMA = re.compile(rb"\blem\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?:<[^>{}]*>)?\s*\(")
EXPECTED_ERROR = re.compile(rb"(?m)^\s*// EXPECT_ERROR (\{[^\r\n]*\})\s*$")
TARGET = re.compile(rb"// TARGET(?:_NEGATIVE)?(?:\s|$)")

HEADER_ANY = re.compile(r"^\s*\d+(?:\.\d+)?s: ([^\s(]+)\((\d+),\d+(?:-\d+(?:,\d+)?)?\): Verifying function '([^']+)'$", re.M)
EXECUTION = re.compile(r"^\s*\d+(?:\.\d+)?s: ([^\s(]+)\((\d+),\d+-\d+\): (?:note: )?Executing statement$", re.M)
RETURN = re.compile(r"^\s*\d+(?:\.\d+)?s: ([^\n]*?): Executing return statement$", re.M)
ERROR = re.compile(r"^.*?: error: .*$", re.M)
DEAD = re.compile(r"^.*?: dead code(?:\s|$).*$", re.M | re.I)
ASSERTION_ERROR = re.compile(
    r"^verified/lib\.rs\((\d+),(\d+)-(\d+)\): error: Assertion might not hold\. \(Cannot prove ([^\n]*)\.\)$",
    re.M,
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def strip_annotations(data: bytes) -> bytes:
    return ANNOTATION_LINE.sub(b"", ANNOTATION_BLOCK.sub(b"", data))


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
    result: dict[str, tuple[int, int]] = {}
    for match in FN.finditer(source):
        name = match.group(1).decode("ascii")
        body_open = re.search(rb"(?m)^\{[ \t]*$", source[match.end():])
        if body_open is None:
            raise RuntimeError(f"missing function body: {name}")
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
    matches = list(CASE_MARKER.finditer(raw))
    if not matches:
        raise RuntimeError("pointer-cases.rs has no CASE_BEGIN/CASE_END cases")
    names = [m.group(1).decode("ascii") for m in matches]
    if len(names) != len(set(names)):
        raise RuntimeError(f"duplicate case names: {names}")
    if selected is not None:
        unknown = sorted(set(selected) - set(names))
        if unknown:
            raise RuntimeError(f"--cases names absent from fixture: {unknown}")
        selected_set = set(selected)
        matches = [match for match in matches if match.group(1).decode("ascii") in selected_set]
        names = [match.group(1).decode("ascii") for match in matches]
        if not names:
            raise RuntimeError("--cases selected no cases")
    prefix = raw[:matches[0].start()]
    # The prefix is shared setup only. Body accounting includes any declarations
    # there, so they remain subject to the same exact-body verification gate.
    cases = {}
    files = {}
    for name, match in zip(names, matches):
        body = match.group(2)
        verified = prefix + body
        original = strip_annotations(verified)
        if strip_annotations(verified) != original:
            raise RuntimeError(f"{name}: ghost stripping is not byte deterministic")
        if re.search(rb"\bassume(?:_correct)?\s*\(|\blemma_auto\b", verified):
            raise RuntimeError(f"{name}: assumptions and automatic lemmas are forbidden")
        all_names = body_names(verified)
        if strip_annotations(verified) != original:
            raise RuntimeError(f"{name}: original runtime bytes changed during ghost stripping")

        declared = list(EXPECTED_ERROR.finditer(body))
        if len(declared) > 1:
            raise RuntimeError(f"{name}: expected at most one predeclared EXPECT_ERROR")
        expected = None
        target_offsets = [m.start() for m in TARGET.finditer(body)]
        if declared:
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
            "expected_bodies": all_names,
            "rust_function_names": [m.group(1).decode("ascii") for m in FN.finditer(verified)],
            "function_line_ranges": line_ranges(verified),
            "verified_sha256": sha(verified),
            "original_sha256": sha(original),
            "ghost_strip_exact_bytes": True,
        }
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
    if exporter == 0 and decoder == 0:
        verifier = run_stage(name, "verifast", [
            str(args.tool_home / "bin/verifast"), "-rustc_args", "--edition 2021",
            "-verbose", "1", "verified/lib.rs",
        ], case_dir, combine_output=True)
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
    }, log, unchanged)
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
            r"error:|unsupported|not yet supported|todo:|failed|timeout|cannot prove|cannot establish",
            line, re.I)]
        stage_diagnostics[stage] = {
            "exit_code": result["stages"].get(stage),
            "first_diagnostic": candidates[0] if candidates else next((line.strip() for line in lines if line.strip()), ""),
        }
    result["stage_diagnostics"] = stage_diagnostics
    result["first_failure"] = next(({
        "stage": stage, "exit_code": stage_diagnostics[stage]["exit_code"],
        "diagnostic": stage_diagnostics[stage]["first_diagnostic"],
    } for stage in ("exporter", "decode", "verifast", "refinement")
       if stage_diagnostics[stage]["exit_code"] not in (0, 125)), None)
    (case_dir / "classification.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def classify(name: str, metadata: dict, stages: dict[str, int], log: str,
             unchanged: bool, mutation_checks: bool = True) -> dict:
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
    classification = "PASS" if unchanged and full_stages and full_vf else "INCONCLUSIVE"
    if negative is not None:
        classification = "EXPECTED_FALSE_ASSERTION" if negative_ok else "INCONCLUSIVE"
    elif metadata.get("unclassified_target"):
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
        "expected_error": negative,
        "observed_error": error_evidence,
        "full_positive_gate": full_stages and full_vf and unchanged,
    }
    if mutation_checks:
        checks = classifier_mutations(metadata, stages, log, unchanged, result)
        result["classifier_fail_closed_mutations"] = checks
        if not all(checks.values()):
            result["classification"] = "INCONCLUSIVE"
    return result


def classifier_mutations(metadata: dict, stages: dict[str, int], log: str,
                         unchanged: bool, baseline: dict) -> dict[str, bool]:
    """Hosted self-checks: perturb exact evidence and ensure no false acceptance."""
    checks: dict[str, bool] = {}
    case = metadata["case"]
    if metadata.get("expected_error") is None:
        # Positive class must fail closed on a single missing proof or integrity gate.
        for key in ("exporter", "decode", "verifast", "refinement"):
            mutant_stages = dict(stages)
            mutant_stages[key] = 124
            checks[f"positive_stage_{key}"] = classify(case, metadata, mutant_stages, log, unchanged, False)["classification"] != "PASS"
        for label, mutant_log, mutant_unchanged in (
            ("missing_body", re.sub(r"^.*Verifying function .*\n", "", log, flags=re.M), unchanged),
            ("error", log + "verified/lib.rs(1,1-2): error: synthetic\n", unchanged),
            ("dead_code", log + "verified/lib.rs(1,1-2): dead code\n", unchanged),
            ("source_changed", log, False),
        ):
            checks[f"positive_{label}"] = classify(case, metadata, stages, mutant_log, mutant_unchanged, False)["classification"] != "PASS"
        timeout_stages = dict(stages)
        timeout_stages["verifast"] = 124
        checks["positive_timeout"] = classify(case, metadata, timeout_stages, log, unchanged, False)["classification"] != "PASS"
        # Remove execution/return/leak traces independently.
        for label, mutant_log in (
            ("no_execution", re.sub(r"^.*Executing statement\n", "", log, flags=re.M)),
            ("no_return", re.sub(r"^.*Executing return statement\n", "", log, flags=re.M)),
            ("no_leak", log.replace("Leak check.", "Leak check removed.")),
        ):
            checks[f"positive_{label}"] = classify(case, metadata, stages, mutant_log, unchanged, False)["classification"] != "PASS"
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
    parser.add_argument("--cases", default="all",
                        help="comma-separated fixture cases, or all (default)")
    args = parser.parse_args()
    if (os.environ.get("GITHUB_ACTIONS") != "true" or
            os.environ.get("RUNNER_ENVIRONMENT") != "github-hosted" or
            os.environ.get("RUNNER_OS") != "Linux" or
            os.environ.get("GITHUB_REF") != "refs/heads/challenge-8/merge"):
        raise RuntimeError("pointer proof harness is restricted to hosted Linux Actions on challenge-8/merge")
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
    manifest, _files = read_cases(FIXTURE, args.workdir, selected)
    (args.evidence / "fixture-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    results = {}
    for name in manifest["case_order"]:
        results[name] = stage_case(name, manifest["cases"][name], args, args.schema)
        print(f"{name}: {results[name]['classification']}", flush=True)
        (args.evidence / "results.json").write_text(json.dumps({
            "scope": "isolated pointer/index projection fixtures; refinement is not whole bidirectional_merge",
            "profile": "official-stock-VeriFast-26.09",
            "source_admission_sha256": sha(admission_path.read_bytes()),
            "cases": results,
        }, indent=2) + "\n")
    controls_ok = all(all(result["classifier_fail_closed_mutations"].values())
                      for result in results.values())
    (args.evidence / "aggregate.json").write_text(json.dumps({
        "evidence_collection_completed": True, "classifier_controls_passed": controls_ok,
        "cases": {name: row["classification"] for name, row in results.items()},
        "scope": "projections only; no whole bidirectional_merge refinement claim",
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
