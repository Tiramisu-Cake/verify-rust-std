#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Prepare isolated sort4 alignment fixtures and classify hosted VeriFast evidence."""

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


CASES = (
    "positive_generic_const",
    "positive_generic_mut",
    "positive_zst_layout",
    "positive_zst_add",
    "negative_source_byte_offset",
    "negative_destination_byte_offset",
)
GENERIC = {
    "positive_generic_const": "aligned_step_const",
    "positive_generic_mut": "aligned_step_mut",
}
POSITIVE = set(CASES[:4])
NEGATIVE = set(CASES[4:])
CASE_MARKER = re.compile(rb"(?m)^// CASE_BEGIN ([a-z0-9_]+)\r?\n(.*?)^// CASE_END \1\r?\n", re.S)
ANNOTATION_BLOCK = re.compile(rb"/\*@.*?@\*/", re.S)
ANNOTATION_LINE = re.compile(rb"(?m)^[ \t]*//@[^\r\n]*(?:\r?\n|$)")
FUNCTION = re.compile(rb"\bfn\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?:<[^>{}]*>)?\s*\(")
LEMMA = re.compile(rb"\blem\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?:<[^>{}]*>)?\s*\(")
TIMESTAMP_HEADER = re.compile(r"^\s*\d+(?:\.\d+)?s: Verifying function '([^']+)'(?:\s|$)")
EXECUTION_RECORD = re.compile(
    r"(?:verified/)?lib\.rs\((\d+),\d+(?:-\d+(?:,\d+)?)?\): (?:note: )?(?:Executing statement|Verifying call)$"
)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def strip_annotations(data):
    return ANNOTATION_LINE.sub(b"", ANNOTATION_BLOCK.sub(b"", data))


def fail(message):
    raise SystemExit(message)


def prepare(fixture_path, workdir):
    source = fixture_path.read_bytes()
    matches = list(CASE_MARKER.finditer(source))
    names = [m.group(1).decode("ascii") for m in matches]
    if tuple(names) != CASES:
        fail(f"case markers missing, duplicated, reordered, or unexpected: {names}")
    prefix = source[: matches[0].start()]
    prefix_lines = prefix.splitlines()
    if any(line.strip() and not line.lstrip().startswith(b"//")
           for line in prefix_lines):
        fail("fixture prefix must contain only line comments and blank lines")
    if b"/*@" in prefix or b"//@" in prefix:
        fail("fixture prefix must not contain ghost annotations or declarations")

    manifest = {
        "fixture_sha256": sha(source),
        "case_order": list(CASES),
        "cases": {},
    }
    for name, match in zip(CASES, matches):
        body = match.group(2)
        verified = prefix + body
        original = strip_annotations(verified)
        # Reject proof shortcuts and any helper declaration without a body.
        if re.search(rb"\blem_auto\b|\bassume(?:_correct)?\s*\(", verified):
            fail(f"forbidden automatic lemma or assumption in {name}")
        lemmas = list(LEMMA.finditer(body))
        for lemma in lemmas:
            block_start = body.rfind(b"/*@", 0, lemma.start())
            block_end = body.find(b"@*/", lemma.end())
            if block_start < 0 or block_end < 0:
                fail(f"lemma declaration outside a closed annotation block in {name}")
            tail = body[lemma.end():block_end]
            post_keyword = tail.find(b"ens")
            post_end = tail.find(b";", post_keyword + 3) if post_keyword >= 0 else -1
            body_open = tail.find(b"{", post_end + 1) if post_end >= 0 else -1
            if body_open < 0:
                fail(f"bodyless lemma declaration in {name}: {lemma.group(1).decode()}")
            depth = 0
            body_close = -1
            for pos in range(body_open, len(tail)):
                if tail[pos:pos + 1] == b"{":
                    depth += 1
                elif tail[pos:pos + 1] == b"}":
                    depth -= 1
                    if depth == 0:
                        body_close = pos
                        break
            if body_close < 0:
                fail(f"unclosed lemma body in {name}: {lemma.group(1).decode()}")
        functions = [m.group(1).decode("ascii") for m in FUNCTION.finditer(body)]
        if functions.count(name) != 1:
            fail(f"{name}: expected exactly one Rust function named after its case, found {functions}")

        lines = verified.splitlines(keepends=True)
        line_starts = []
        offset = 0
        for line in lines:
            line_starts.append(offset)
            offset += len(line)

        def line_of(offset_in_file):
            # Fixtures are small; this deterministic linear lookup avoids an
            # additional parser whose source mapping could become ambiguous.
            return next(i + 1 for i, start in enumerate(line_starts)
                        if start <= offset_in_file < start + len(lines[i]))

        function_match = next(m for m in FUNCTION.finditer(body)
                              if m.group(1).decode("ascii") == name)
        function_line = line_of(len(prefix) + function_match.start())
        metadata = {"function_name": name, "function_source_line": function_line}

        if name in GENERIC:
            helper = GENERIC[name]
            helper_matches = [m for m in LEMMA.finditer(body)
                              if m.group(1).decode("ascii") == helper]
            if len(helper_matches) != 1:
                fail(f"{name}: expected exactly one checked lemma body named {helper}")
            metadata["helper_name"] = helper
            metadata["helper_source_line"] = line_of(len(prefix) + helper_matches[0].start())
            block_start = body.rfind(b"/*@", 0, helper_matches[0].start())
            block_end = body.find(b"@*/", helper_matches[0].end())
            if block_start < 0 or block_end < 0:
                fail(f"{name}: checked lemma must be inside a closed VeriFast annotation block")
            helper_tail = body[helper_matches[0].end():block_end]
            helper_post = helper_tail.find(b"ens")
            helper_post_end = helper_tail.find(b";", helper_post + 3)
            helper_open = helper_tail.find(b"{", helper_post_end + 1)
            if helper_post < 0 or helper_post_end < 0 or helper_open < 0:
                fail(f"{name}: checked lemma body boundaries are invalid")
            helper_depth = 0
            helper_close = -1
            for pos in range(helper_open, len(helper_tail)):
                if helper_tail[pos:pos + 1] == b"{":
                    helper_depth += 1
                elif helper_tail[pos:pos + 1] == b"}":
                    helper_depth -= 1
                    if helper_depth == 0:
                        helper_close = pos
                        break
            if helper_close < 0:
                fail(f"{name}: checked lemma body boundaries are invalid")
            metadata["helper_body_start_line"] = line_of(
                len(prefix) + helper_matches[0].end() + helper_open)
            metadata["helper_body_end_line"] = line_of(
                len(prefix) + helper_matches[0].end() + helper_close)

        marker = b"// POINTER_OPERATION"
        marker_offsets = [m.start() for m in re.finditer(re.escape(marker), body)]
        expects_pointer = name != "positive_zst_layout"
        if expects_pointer:
            if len(marker_offsets) != 1:
                fail(f"{name}: expected one POINTER_OPERATION marker, found {len(marker_offsets)}")
            marker_line = line_of(len(prefix) + marker_offsets[0])
            if marker_line >= len(lines):
                fail(f"{name}: POINTER_OPERATION marker has no following runtime statement")
            operation_line = lines[marker_line].strip()
            if b".add(" not in operation_line or operation_line.startswith(b"//"):
                fail(f"{name}: POINTER_OPERATION must immediately precede a runtime .add(...) statement")
            metadata["pointer_marker_line"] = marker_line
            metadata["pointer_operation_line"] = marker_line + 1
        elif marker_offsets:
            fail("positive_zst_layout must not claim pointer-operation coverage")

        alignment_offsets = [m.start() for m in re.finditer(b"// ALIGNMENT_OBLIGATION", body)]
        if name in NEGATIVE:
            if len(alignment_offsets) != 1:
                fail(f"{name}: expected exactly one ALIGNMENT_OBLIGATION marker")
            marker_line = line_of(len(prefix) + alignment_offsets[0])
            if marker_line >= len(lines):
                fail(f"{name}: alignment marker has no following assertion")
            assertion = lines[marker_line].strip()
            if not assertion.startswith(b"//@ assert ") or not assertion.endswith(b";"):
                fail(f"{name}: ALIGNMENT_OBLIGATION must be followed immediately by one //@ assert ...; line")
            metadata["alignment_marker_line"] = marker_line
            metadata["alignment_assertion_line"] = marker_line + 1
            metadata["alignment_assertion"] = assertion.decode("utf-8", "replace")
        elif alignment_offsets:
            fail(f"{name}: positive fixture must not contain ALIGNMENT_OBLIGATION")

        if strip_annotations(verified) != original:
            fail(f"{name}: ghost stripping changed original runtime bytes")
        case_dir = workdir / name
        (case_dir / "original").mkdir(parents=True, exist_ok=False)
        (case_dir / "verified").mkdir(parents=True, exist_ok=False)
        (case_dir / "original/lib.rs").write_bytes(original)
        (case_dir / "verified/lib.rs").write_bytes(verified)
        metadata.update({
            "verified_sha256": sha(verified),
            "original_sha256": sha(original),
            "ghost_strip_exact_bytes": True,
        })
        manifest["cases"][name] = metadata

    (workdir / "extraction.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def run_command(argv, cwd, resource_file, stdout_file, stderr_file=None):
    with stdout_file.open("wb") as stdout:
        if stderr_file is None:
            stderr_file = stdout_file
            stderr = subprocess.STDOUT
        else:
            stderr = stderr_file.open("wb")
        timed = ["/usr/bin/time", "-v", "-o", str(resource_file), *map(str, argv)]
        try:
            completed = subprocess.run(timed, cwd=cwd, stdout=stdout, stderr=stderr, check=False)
            status = completed.returncode
        except OSError as exc:
            stderr_file.write_text(f"could not start stage: {exc}\n")
            status = 127
        finally:
            if stderr_file is not stdout_file and hasattr(stderr, "close"):
                stderr.close()
    return status


def stage_case(name, metadata, args):
    case_dir = args.workdir / name
    orig = case_dir / "original/lib.rs"
    verified = case_dir / "verified/lib.rs"
    before = {str(p.relative_to(case_dir)): sha(p.read_bytes()) for p in (orig, verified)}
    (case_dir / "source-before-sha256.json").write_text(json.dumps(before, indent=2) + "\n")

    stage_integrity = {}

    def run_audited(stage, argv, resource_file, stdout_file, stderr_file=None):
        before_stage = {str(p.relative_to(case_dir)): sha(p.read_bytes()) for p in (orig, verified)}
        status = run_command(argv, case_dir, resource_file, stdout_file, stderr_file)
        after_stage = {str(p.relative_to(case_dir)): sha(p.read_bytes()) for p in (orig, verified)}
        unchanged_stage = before_stage == after_stage
        stage_integrity[stage] = {
            "before": before_stage, "after": after_stage, "unchanged": unchanged_stage,
        }
        (case_dir / f"source-integrity-{stage}.json").write_text(
            json.dumps(stage_integrity[stage], indent=2) + "\n")
        return status

    export_log = case_dir / "exporter.log"
    exporter = run_audited("exporter", [
        args.tool_home / "bin/vf-rust-mir-exporter", "verified/lib.rs",
        f"--sysroot={args.compiler_sysroot}", "--edition", "2021", "--crate-type", "lib",
        "--vf-rust-mir-exporter:preprocess-readonly",
    ], case_dir / "exporter-resources.txt", case_dir / "compiler-mir.bin", export_log)
    (case_dir / "exporter-exit-code.txt").write_text(f"{exporter}\n")

    decode_log = case_dir / "capnp-decode.log"
    if exporter == 0:
        decode_out = case_dir / "compiler-mir.txt"
        decode_before = {str(p.relative_to(case_dir)): sha(p.read_bytes()) for p in (orig, verified)}
        with (case_dir / "compiler-mir.bin").open("rb") as source, decode_out.open("wb") as output, decode_log.open("wb") as errors:
            try:
                proc = subprocess.run([
                    "/usr/bin/time", "-v", "-o", str(case_dir / "decode-resources.txt"),
                    "capnp", "decode", args.schema, "VfMir",
                ], stdin=source, stdout=output, stderr=errors, check=False)
                decode = proc.returncode
            except OSError as exc:
                errors.write(f"could not start stage: {exc}\n".encode())
                decode = 127
        decode_after = {str(p.relative_to(case_dir)): sha(p.read_bytes()) for p in (orig, verified)}
        stage_integrity["decoder"] = {
            "before": decode_before, "after": decode_after,
            "unchanged": decode_before == decode_after,
        }
        (case_dir / "source-integrity-decoder.json").write_text(
            json.dumps(stage_integrity["decoder"], indent=2) + "\n")
    else:
        decode = 125
        decode_out = case_dir / "compiler-mir.txt"
        decode_out.write_bytes(b"")
        decode_log.write_text("not run because MIR export failed\n")
        (case_dir / "decode-resources.txt").write_text("stage not run\n")
        stage_integrity["decoder"] = {"unchanged": True, "status": "not_run_export_failed"}
        (case_dir / "source-integrity-decoder.json").write_text(
            json.dumps(stage_integrity["decoder"], indent=2) + "\n")
    (case_dir / "decode-exit-code.txt").write_text(f"{decode}\n")
    if (case_dir / "compiler-mir.bin").exists():
        (case_dir / "compiler-mir-sha256.txt").write_text(sha((case_dir / "compiler-mir.bin").read_bytes()) + "\n")

    if exporter == 0 and decode == 0:
        vf = run_audited("verifast", [
            args.tool_home / "bin/verifast", "-rustc_args", "--edition 2021", "-verbose", "1", "verified/lib.rs",
        ], case_dir / "verifast-resources.txt", case_dir / "verifast.log")
    else:
        vf = 125
        (case_dir / "verifast.log").write_text("not run because export/decode failed\n")
        (case_dir / "verifast-resources.txt").write_text("stage not run\n")
        stage_integrity["verifast"] = {"unchanged": True, "status": "not_run_export_or_decode_failed"}
        (case_dir / "source-integrity-verifast.json").write_text(
            json.dumps(stage_integrity["verifast"], indent=2) + "\n")
    (case_dir / "verifast-exit-code.txt").write_text(f"{vf}\n")

    refinement = run_audited("refinement", [
        args.tool_home / "bin/refinement-checker", "--rustc-args", "--edition 2021",
        "original/lib.rs", "verified/lib.rs",
    ], case_dir / "refinement-resources.txt", case_dir / "refinement.log")
    (case_dir / "refinement-exit-code.txt").write_text(f"{refinement}\n")

    after = {str(p.relative_to(case_dir)): sha(p.read_bytes()) for p in (orig, verified)}
    (case_dir / "source-after-sha256.json").write_text(json.dumps(after, indent=2) + "\n")
    unchanged = before == after and all(value.get("unchanged", False) for value in stage_integrity.values())
    (case_dir / "source-unchanged.txt").write_text(f"{str(unchanged).lower()}\n")

    log = (case_dir / "verifast.log").read_text(errors="replace")
    headers = [m.group(1) for line in log.splitlines() if (m := TIMESTAMP_HEADER.search(line))]
    caller_count = headers.count(name)
    helper_count = headers.count(metadata.get("helper_name", "")) if metadata.get("helper_name") else 0
    records = []
    for line in log.splitlines():
        match = EXECUTION_RECORD.search(line)
        if match:
            records.append(int(match.group(1)))
    pointer_records = sum(line == record for record in records
                          for line in [metadata.get("pointer_operation_line", -1)])
    helper_records = sum(metadata.get("helper_body_start_line", -1) <= record <=
                         metadata.get("helper_body_end_line", -2) for record in records)

    result = {
        "exporter_exit": exporter,
        "decode_exit": decode,
        "verifast_exit": vf,
        "refinement_exit": refinement,
        "caller_header_count": caller_count,
        "helper_header_count": helper_count,
        "helper_execution_records": helper_records,
        "pointer_operation_records": pointer_records,
        "source_unchanged_at_every_stage": unchanged,
    }
    base_stages_ok = exporter == 0 and decode == 0 and refinement == 0 and unchanged

    if name in POSITIVE:
        vf_ok = vf == 0 and caller_count == 1
        if name in GENERIC:
            vf_ok = vf_ok and helper_count == 1 and helper_records >= 1 and pointer_records >= 1
        elif name == "positive_zst_add":
            vf_ok = vf_ok and pointer_records >= 1
        if base_stages_ok and vf_ok:
            classification = "PASS"
        else:
            classification = "INCONCLUSIVE"
    else:
        line = metadata["alignment_assertion_line"]
        line_error = re.compile(rf"(?:verified/)?lib\.rs\({line},\d+(?:-\d+(?:,\d+)?)?\): error:", re.I)
        intended_failure = any(line_error.search(entry) and "cannot prove" in entry.lower()
                               for entry in log.splitlines())
        preconditions_ok = base_stages_ok and caller_count == 1 and pointer_records >= 1
        if preconditions_ok and vf != 0 and intended_failure:
            classification = "EXPECTED_FALSE_POST_FAILURE"
        elif preconditions_ok and vf == 0:
            classification = "FALSE_ALIGNMENT_PROVED"
        else:
            classification = "INCONCLUSIVE"
    result["classification"] = classification
    result["negative_error_at_marked_alignment_assertion"] = (
        classification == "EXPECTED_FALSE_POST_FAILURE" if name in NEGATIVE else None
    )
    (case_dir / "classification.json").write_text(json.dumps(result, indent=2) + "\n")
    print(f"{name}: {classification} (export={exporter} decode={decode} vf={vf} refine={refinement}; caller={caller_count} helper={helper_count}/{helper_records} pointer={pointer_records})")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--workdir", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--tool-home", type=Path, required=True)
    parser.add_argument("--compiler-sysroot", required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    args.workdir.mkdir(parents=True, exist_ok=False)
    manifest = prepare(args.fixture, args.workdir)
    (args.evidence / "fixture-and-source-hashes.json").write_text(json.dumps({
        "fixture_sha256": manifest["fixture_sha256"],
        "cases": {name: {
            "verified_sha256": info["verified_sha256"],
            "original_sha256": info["original_sha256"],
        } for name, info in manifest["cases"].items()},
    }, indent=2) + "\n")
    results = {name: stage_case(name, manifest["cases"][name], args) for name in CASES}
    aggregate = {
        "geometry": {name: results[name]["classification"] for name in GENERIC},
        "layout": {name: results[name]["classification"] for name in ("positive_zst_layout", "positive_zst_add")},
        "negative_conclusions": {name: results[name]["classification"] for name in NEGATIVE},
        "all_cases": results,
    }
    (args.evidence / "aggregate.json").write_text(json.dumps(aggregate, indent=2) + "\n")
    unexpected = []
    for name, result in results.items():
        expected = "PASS" if name in POSITIVE else "EXPECTED_FALSE_POST_FAILURE"
        if result["classification"] != expected:
            unexpected.append(f"{name}={result['classification']}")
    if unexpected:
        print("Unexpected gate outcomes: " + ", ".join(unexpected), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
