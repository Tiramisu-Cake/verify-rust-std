#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted-only isolated regression matrix for the experimental Rust layout profile."""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BASELINE_FIXTURE = HERE / "verifast-sort4-alignment-cases.rs"
FIXTURE = HERE / "rust-fieldless-layout-cases.rs"
BASELINE_DRIVER = HERE / "prepare-and-check-sort4-alignment.py"
MARKER = re.compile(rb"(?m)^// CASE_BEGIN ([a-z0-9_]+)\r?\n(.*?)^// CASE_END \1\r?\n", re.S)
GHOST_BLOCK = re.compile(rb"/\*@.*?@\*/", re.S)
GHOST_LINE = re.compile(rb"(?m)^[ \t]*//@[^\r\n]*(?:\r?\n|$)")
HEADER = re.compile(r"^\s*\d+(?:\.\d+)?s: verified/lib\.rs\((\d+),\d+(?:-\d+(?:,\d+)?)?\): Verifying function '([^']+)'$")
EXEC = re.compile(r"^\s*\d+(?:\.\d+)?s: verified/lib\.rs\((\d+),\d+(?:-\d+(?:,\d+)?)?\): (?:note: )?(?:Executing statement|Verifying call)$")
ERROR = re.compile(r"^verified/lib\.rs\((\d+),\d+-\d+\): error: (.*)$")

POSITIVES = {
    "zst_mut_add", "repr_rust_empty", "repr_rust_empty_default",
    "repr_c_empty", "repr_c_empty_default",
    "apply_const_z", "apply_mut_z", "apply_const_u64", "apply_mut_u64",
}
NEGATIVES = {
    "negative_zst_size", "negative_zst_alignment",
    "negative_zst_nonzero_stride", "negative_assert_false",
}
UNSUPPORTED = {
    "unsupported_fielded", "unsupported_phantom_field",
    "unsupported_generic_adt", "unsupported_packed", "unsupported_transparent",
}
METADATA_CASES = {"negative_absent_layout", "metadata_control_body"}
GENERATED_APPLICATIONS = {"apply_const_z", "apply_mut_z", "apply_const_u64", "apply_mut_u64"}
PHYSICAL_CASES = (POSITIVES - GENERATED_APPLICATIONS) | NEGATIVES | UNSUPPORTED | METADATA_CASES


def digest(data):
    return hashlib.sha256(data).hexdigest()


def strip_ghost(data):
    return GHOST_LINE.sub(b"", GHOST_BLOCK.sub(b"", data))


def marked_cases(source, required=None):
    matches = list(MARKER.finditer(source))
    names = [m.group(1).decode("ascii") for m in matches]
    if len(names) != len(set(names)) or (required is not None and set(names) != set(required)):
        raise ValueError(f"fixture markers missing, duplicated, or unexpected: {names}")
    prefix = source[:matches[0].start()] if matches else source
    if any(line.strip() and not line.lstrip().startswith(b"//") for line in prefix.splitlines()):
        raise ValueError("fixture prefix must contain only line comments and blank lines")
    if b"/*@" in prefix or b"//@" in prefix:
        raise ValueError("fixture prefix must not contain VeriFast declarations")
    return prefix, {m.group(1).decode("ascii"): m.group(2) for m in matches}


def generic_application(prefix, generic_cases, wrapper_name, ty, mut):
    generic_key = "positive_generic_mut" if mut else "positive_generic_const"
    z_definition = b"#[repr(align(8))]\npub struct Z;\n" if ty == "Z" else b""
    generic_source = prefix + z_definition + generic_cases[generic_key]
    generic_fn = "positive_generic_mut" if mut else "positive_generic_const"
    ptr = "*mut" if mut else "*const"
    if ty == "Z":
        req_len, align, expected_result = "0", "8", "base"
        bytes_ty = "*u8"
    else:
        req_len, align, expected_result = "4 * std::mem::size_of::<u64>()", "std::mem::align_of::<u64>()", "base + i"
        bytes_ty = "*u8"
    wrapper = f"""
pub unsafe fn {wrapper_name}(base: {ptr} {ty}, i: usize) -> {ptr} {ty}
/*@
req array_::<u8>(base as {bytes_ty}, {req_len}, ?bytes) &*& base != 0 &*&
    base as usize % {align} == 0 &*& i <= 3;
@*//*@
ens array_::<u8>(base as {bytes_ty}, {req_len}, bytes) &*& result == {expected_result} &*&
    pointer_within_limits(result) == true &*& result as usize % {align} == 0;
@*//*@
on_unwind_ens false;
@*/
{{
    // GENERIC_CALL
    let result = {generic_fn}::<{ty}>(base, i);
    result
}}
""".encode()
    return generic_source + wrapper


def line_number(source, offset):
    return source[:offset].count(b"\n") + 1


def capnp_groups(text):
    """Return balanced parenthesis ranges, ignoring parentheses in quoted strings."""
    stack = []
    ranges = []
    quoted = False
    escaped = False
    for index, char in enumerate(text):
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
            continue
        if char == '"':
            quoted = True
        elif char == "(":
            stack.append(index)
        elif char == ")" and stack:
            ranges.append((stack.pop(), index + 1))
    return ranges


def adt_layout_context(text, type_name):
    name_re = re.compile(r'\bname\s*=\s*"([^"]+)"')
    positions = [match.start() for match in name_re.finditer(text)
                 if match.group(1) == type_name or match.group(1).endswith("::" + type_name)]
    ranges = capnp_groups(text)
    candidates = []
    for position in positions:
        for start, end in ranges:
            group = text[start:end]
            if start <= position < end and "rustLayoutInfo" in group:
                candidates.append((end - start, group))
    if not candidates:
        return None
    return min(candidates, key=lambda item: item[0])[1]


def adt_layout_info(text, type_name):
    group = adt_layout_context(text, type_name)
    if group is None:
        return None
    match = re.search(r"\brustLayoutInfo\s*=\s*", group)
    if not match:
        return None
    value_start = match.end()
    while value_start < len(group) and group[value_start].isspace():
        value_start += 1
    if value_start >= len(group) or group[value_start] != "(":
        return group[value_start:value_start + 80]
    by_start = {start: end for start, end in capnp_groups(group)}
    end = by_start.get(value_start)
    return group[value_start:end] if end else None


def adt_layout_location(text, type_name):
    name_re = re.compile(r'\bname\s*=\s*"([^"]+)"')
    positions = [match.start() for match in name_re.finditer(text)
                 if match.group(1) == type_name or match.group(1).endswith("::" + type_name)]
    ranges = capnp_groups(text)
    candidates = []
    for position in positions:
        for start, end in ranges:
            if start <= position < end and "rustLayoutInfo" in text[start:end]:
                candidates.append((end - start, start, end))
    if not candidates:
        raise ValueError(f"no source ADT record with rustLayoutInfo for {type_name}")
    _, group_start, group_end = min(candidates)
    group = text[group_start:group_end]
    marker = re.search(r"\brustLayoutInfo\s*=\s*", group)
    if not marker:
        raise ValueError(f"no rustLayoutInfo union for {type_name}")
    open_at = group_start + marker.end()
    while open_at < group_end and text[open_at].isspace():
        open_at += 1
    by_start = {start: end for start, end in capnp_groups(text)}
    end = by_start.get(open_at)
    if end is None or end > group_end:
        raise ValueError(f"malformed rustLayoutInfo union for {type_name}")
    return open_at, end


def mutate_metadata_text(text, type_name, mutation):
    layout_start, layout_end = adt_layout_location(text, type_name)
    value = text[layout_start:layout_end]
    if mutation == "absent":
        replacement = "(absent = void)"
    elif mutation in {"bad-align", "bad-size", "wrong-name", "wrong-target", "wrong-width", "wrong-span"}:
        fields = {
            "bad-align": ("abiAlignBytes", "3"),
            "bad-size": ("sizeBytes", "1"),
            "wrong-name": ("bindingAdtDefName", '"challenge_8::WrongZ"'),
            "wrong-target": ("bindingTargetTriple", '"wrong-unknown-target"'),
            "wrong-width": ("bindingPointerWidth", "8"),
        }
        if mutation == "wrong-span":
            span = re.search(r"\bbindingDefSpan\s*=\s*", value)
            if not span:
                raise ValueError("metadata mutation wrong-span could not locate bindingDefSpan")
            span_start = span.end()
            while span_start < len(value) and value[span_start].isspace():
                span_start += 1
            ends = {left: right for left, right in capnp_groups(value)}
            span_end = ends.get(span_start)
            if span_end is None:
                raise ValueError("metadata mutation wrong-span found malformed SpanData")
            inner = value[span_start:span_end]
            scalar = re.search(r"(\b(?:line|startLine|lo|start)\s*=\s*)(\d+)", inner)
            if scalar is None:
                scalar = re.search(r"(=\s*)(\d+)", inner)
            if scalar is None:
                raise ValueError("metadata mutation wrong-span found no scalar span endpoint")
            changed = inner[:scalar.start(2)] + str(int(scalar.group(2)) + 1) + inner[scalar.end(2):]
            replacement = value[:span_start] + changed + value[span_end:]
            return text[:layout_start] + replacement + text[layout_end:]
        field, replacement_value = fields[mutation]
        pattern = re.compile(rf"(\b{field}\s*=\s*)(\"[^\"]*\"|\d+)")
        replacement, count = pattern.subn(rf"\g<1>{replacement_value}", value, count=1)
        if count != 1:
            raise ValueError(f"metadata mutation {mutation} could not locate {field}")
    else:
        raise ValueError(f"unknown metadata mutation: {mutation}")
    return text[:layout_start] + replacement + text[layout_end:]


def inspect_layout_metadata(case_dir, exact_expected=None, absent_types=()):
    text_path = case_dir / "compiler-mir.txt"
    text = text_path.read_text(errors="replace") if text_path.exists() else ""
    result = {"decoded_mir_sha256": digest(text.encode()), "exact": {}, "absent": {}, "errors": []}
    if not text:
        result["errors"].append("Cap'n Proto decoded MIR text is empty")
    for type_name, expected in (exact_expected or {}).items():
        info = adt_layout_info(text, type_name)
        if info is None:
            result["exact"][type_name] = {"ok": False, "reason": "no associated rustLayoutInfo in AdtDef"}
            continue
        scalar_values = {}
        for field in ("sizeBytes", "abiAlignBytes", "bindingPointerWidth"):
            found = re.search(rf"\b{field}\s*=\s*(\d+)", info)
            scalar_values[field] = int(found.group(1)) if found else None
        bound_name = re.search(r'\bbindingAdtDefName\s*=\s*"([^"]+)"', info)
        bound_target = re.search(r'\bbindingTargetTriple\s*=\s*"([^"]+)"', info)
        bound_span = re.search(r"\bbindingDefSpan\s*=\s*(\(.*?\))", info, re.S)
        adt_context = adt_layout_context(text, type_name) or ""
        definition_span = re.search(r"\bdefSpan\s*=\s*(\(.*?\))", adt_context, re.S)
        target = re.search(r'\btargetTriple\s*=\s*"([^"]+)"', text)
        width = re.search(r"\bpointerWidth\s*=\s*(\d+)", text)
        ok = (
            "exact" in info and scalar_values["sizeBytes"] == expected[0] and
            scalar_values["abiAlignBytes"] == expected[1] and bound_name is not None and
            (bound_name.group(1) == type_name or bound_name.group(1).endswith("::" + type_name)) and bound_target is not None and
            target is not None and bound_target.group(1) == target.group(1) and
            scalar_values["bindingPointerWidth"] in (32, 64) and bound_span is not None and
            width is not None and scalar_values["bindingPointerWidth"] == int(width.group(1)) and
            "verified/lib.rs" in bound_span.group(1) and definition_span is not None and
            re.sub(r"\s+", "", bound_span.group(1)) == re.sub(r"\s+", "", definition_span.group(1))
        )
        result["exact"][type_name] = {
            "ok": ok, "observed": scalar_values,
            "binding_name": bound_name.group(1) if bound_name else None,
            "binding_target": bound_target.group(1) if bound_target else None,
            "binding_pointer_width": scalar_values["bindingPointerWidth"],
            "root_target_triple": target.group(1) if target else None,
            "root_pointer_width": int(width.group(1)) if width else None,
            "binding_span_present": bound_span is not None,
            "definition_span_matches": (bound_span is not None and definition_span is not None and
                re.sub(r"\s+", "", bound_span.group(1)) == re.sub(r"\s+", "", definition_span.group(1))),
        }
    for type_name in absent_types:
        info = adt_layout_info(text, type_name)
        absent = info is not None and re.search(r"\babsent\s*=\s*void\b", info) is not None
        result["absent"][type_name] = {"ok": absent, "layout_info": info}
    result["ok"] = bool(text) and all(v["ok"] for v in result["exact"].values()) and all(
        v["ok"] for v in result["absent"].values())
    (case_dir / "layout-metadata-audit.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def prepare_case(name, source, workdir):
    stripped = strip_ghost(source)
    case_dir = workdir / name
    (case_dir / "original").mkdir(parents=True, exist_ok=False)
    (case_dir / "verified").mkdir()
    (case_dir / "original/lib.rs").write_bytes(stripped)
    (case_dir / "verified/lib.rs").write_bytes(source)
    target = None
    target_assertion = None
    target_markers = list(re.finditer(rb"(?m)^[ \t]*// TARGET_ASSERTION[ \t]*$", source))
    if target_markers:
        target = line_number(source, target_markers[0].end()) + 1
        target_assertion = source.splitlines()[target - 1].strip().decode("utf-8", "replace")
    marker = re.search(rb"(?m)^[ \t]*// POINTER_OPERATION[ \t]*$", source)
    pointer = None
    if marker:
        pointer = line_number(source, marker.end()) + 1
    call_marker = re.search(rb"(?m)^[ \t]*// GENERIC_CALL[ \t]*$", source)
    generic_call = line_number(source, call_marker.end()) + 1 if call_marker else None
    include_generic = "apply_" in name
    metadata = {
        "case": name,
        "source_sha256": digest(source),
        "original_sha256": digest(stripped),
        "target_assertion_line": target,
        "target_assertion": target_assertion,
        "pointer_operation_line": pointer,
        "generic_call_line": generic_call,
        "generic_callee_expected": include_generic,
        "ghost_strip_exact_bytes": True,
    }
    (case_dir / "case.json").write_text(json.dumps(metadata, indent=2) + "\n")
    return case_dir, metadata


def run(argv, cwd, out, err=None, stdin=None):
    if err is None:
        err = out
        stderr = subprocess.STDOUT
        with out.open("wb") as stdout:
            try:
                return subprocess.run(list(map(str, argv)), cwd=cwd, stdin=stdin, stdout=stdout,
                                      stderr=stderr, check=False).returncode
            except OSError as exc:
                out.write_text(f"could not start stage: {exc}\n")
                return 127
    with out.open("wb") as stdout, err.open("wb") as stderr_stream:
        try:
            return subprocess.run(list(map(str, argv)), cwd=cwd, stdin=stdin, stdout=stdout,
                                  stderr=stderr_stream, check=False).returncode
        except OSError as exc:
            err.write_text(f"could not start stage: {exc}\n")
            return 127


def stages_for(name, source, case_dir, args):
    orig = case_dir / "original/lib.rs"
    verified = case_dir / "verified/lib.rs"
    initial = {"original": digest(orig.read_bytes()), "verified": digest(verified.read_bytes())}
    (case_dir / "source-before-sha256.json").write_text(json.dumps(initial, indent=2) + "\n")
    statuses = {}

    def audited(key, argv, out_name, err_name=None, stdin=None):
        before = {"original": digest(orig.read_bytes()), "verified": digest(verified.read_bytes())}
        status = run(argv, case_dir, case_dir / out_name,
                     case_dir / err_name if err_name else None, stdin=stdin)
        after = {"original": digest(orig.read_bytes()), "verified": digest(verified.read_bytes())}
        (case_dir / f"source-integrity-{key}.json").write_text(json.dumps({
            "before": before, "after": after, "unchanged": before == after,
        }, indent=2) + "\n")
        statuses[key] = status
        return before == after

    integrity = []
    integrity.append(audited("exporter", [args.source_home / "bin/vf-rust-mir-exporter", "verified/lib.rs",
        f"--sysroot={args.compiler_sysroot}", "--edition", "2021", "--crate-type", "lib",
        "--vf-rust-mir-exporter:preprocess-readonly"], "compiler-mir.bin", "exporter.log"))
    if statuses["exporter"] == 0:
        with (case_dir / "compiler-mir.bin").open("rb") as mir_input:
            integrity.append(audited("decoder", ["capnp", "decode", args.schema, "VfMir"],
                                     "compiler-mir.txt", "capnp-decode.log", stdin=mir_input))
        if statuses["decoder"] == 0:
            integrity.append(audited("verifast", [args.tool_home / "bin/verifast", "-rustc_args",
                "--edition 2021", "-verbose", "1", "verified/lib.rs"], "verifast.log"))
        else:
            statuses["verifast"] = 125
            (case_dir / "verifast.log").write_text("not run because decode failed\n")
    else:
        statuses["decoder"] = statuses["verifast"] = 125
        (case_dir / "compiler-mir.txt").write_bytes(b"")
        (case_dir / "capnp-decode.log").write_text("not run because exporter failed\n")
        (case_dir / "verifast.log").write_text("not run because exporter failed\n")
    integrity.append(audited("refinement", [args.tool_home / "bin/refinement-checker", "--rustc-args",
        "--edition 2021", "original/lib.rs", "verified/lib.rs"], "refinement.log"))
    final = {"original": digest(orig.read_bytes()), "verified": digest(verified.read_bytes())}
    unchanged = initial == final and all(integrity)
    (case_dir / "source-after-sha256.json").write_text(json.dumps(final, indent=2) + "\n")
    (case_dir / "source-unchanged.txt").write_text(f"{str(unchanged).lower()}\n")
    for stage, status in statuses.items():
        (case_dir / f"{stage}-exit-code.txt").write_text(f"{status}\n")
    return statuses, unchanged


def classify(name, source, metadata, statuses, unchanged, case_dir, layout_audit):
    log = (case_dir / "verifast.log").read_text(errors="replace")
    headers = [(int(m.group(1)), m.group(2)) for line in log.splitlines() if (m := HEADER.search(line))]
    records = [int(m.group(1)) for line in log.splitlines() if (m := EXEC.search(line))]
    caller_count = sum(fn == name for _, fn in headers)
    pointer_count = sum(line == metadata["pointer_operation_line"] for line in records) if metadata["pointer_operation_line"] else 0
    generic_call_count = sum(line == metadata["generic_call_line"] for line in records) if metadata["generic_call_line"] else 0
    generic_name = "positive_generic_mut" if "apply_mut" in name else "positive_generic_const"
    generic_count = sum(fn == generic_name for _, fn in headers)
    generic_helper = "aligned_step_mut" if "apply_mut" in name else "aligned_step_const"
    helper_count = sum(fn == generic_helper for _, fn in headers)
    errors = [(m.group(1), m.group(2)) for line in log.splitlines() if (m := ERROR.search(line))]
    stages_ok = all(statuses.get(stage) == 0 for stage in ("exporter", "decoder", "refinement")) and unchanged
    layout_ok = layout_audit["ok"]
    if name in POSITIVES:
        proof_ok = statuses.get("verifast") == 0 and caller_count == 1
        if metadata["pointer_operation_line"]:
            proof_ok = proof_ok and pointer_count >= 1
        if name.startswith("apply_"):
            proof_ok = proof_ok and generic_count == 1 and helper_count == 1 and generic_call_count >= 1
        verdict = "PASS" if stages_ok and proof_ok and layout_ok else "INCONCLUSIVE"
    elif name in NEGATIVES:
        target = metadata["target_assertion_line"]
        target_error = len(errors) == 1 and target is not None and int(errors[0][0]) == target and "Assertion might not hold" in errors[0][1]
        target_records = sum(line == target for line in records) if target is not None else 0
        body_reached = caller_count == 1 and target_records >= 1 and (not metadata["pointer_operation_line"] or pointer_count >= 1)
        expected_assertion = {
            "negative_zst_size": "//@ assert size == 1;",
            "negative_zst_alignment": "//@ assert alignment == 16;",
            "negative_zst_nonzero_stride": "//@ assert result != base;",
            "negative_assert_false": "//@ assert false;",
        }[name]
        expected_content = {
            "negative_zst_size": r"Assertion might not hold\. \(Cannot prove __result = 1\.\)$",
            "negative_zst_alignment": r"Assertion might not hold\. \(Cannot prove __result = 16\.\)$",
            "negative_zst_nonzero_stride": r"Assertion might not hold\. \(Cannot prove (?:ptr_add_\(base, i, Z_type_info\) != base|!\(ptr_add_\(base, i, Z_type_info\) = base\))\.\)$",
            "negative_assert_false": r"Assertion might not hold\. \(Cannot prove false\.\)$",
        }[name]
        target_error = (target_error and metadata["target_assertion"] == expected_assertion and
                        re.fullmatch(expected_content, errors[0][1]) is not None)
        verdict = "EXPECTED_TARGET_ASSERTION_FAILURE" if stages_ok and layout_ok and statuses.get("verifast", 0) != 0 and target_error and body_reached else "INCONCLUSIVE"
    else:
        body_ok = statuses.get("verifast") == 0 and caller_count == 1
        verdict = "UNSUPPORTED_LAYOUT_PASS" if stages_ok and body_ok and layout_ok else "INCONCLUSIVE"
    return {
        "classification": verdict,
        "stages": statuses,
        "source_unchanged_at_all_stages": unchanged,
        "caller_header_count": caller_count,
        "pointer_operation_records": pointer_count,
        "generic_call_records": generic_call_count,
        "generic_callee_header_count": generic_count if name.startswith("apply_") else None,
        "generic_helper_header_count": helper_count if name.startswith("apply_") else None,
        "target_assertion_line": metadata["target_assertion_line"],
        "layout_metadata_audit": layout_audit,
        "errors": [{"line": int(line), "message": message} for line, message in errors],
    }


def invoke_unchanged_six(args, outdir, tool_home, label):
    workdir = outdir / f"{label}-original-six-cases"
    evidence = outdir / f"{label}-original-six-evidence"
    cmd = [sys.executable, BASELINE_DRIVER, "--fixture", BASELINE_FIXTURE,
           "--workdir", workdir, "--schema", args.schema,
           "--tool-home", tool_home, "--compiler-sysroot", args.compiler_sysroot,
           "--evidence", evidence]
    evidence.mkdir(parents=True, exist_ok=False)
    status = run(cmd, ROOT, outdir / f"{label}-original-six-driver.log")
    result_file = evidence / "aggregate.json"
    if not result_file.exists():
        return {"driver_exit": status, "classification": "INCONCLUSIVE", "aggregate": None}
    aggregate = json.loads(result_file.read_text())
    if label == "experimental":
        layout_case = workdir / "positive_zst_layout"
        metadata_audit = inspect_layout_metadata(layout_case, {"Z": (0, 8)})
        (evidence / "exact-zst-metadata-audit.json").write_text(json.dumps(metadata_audit, indent=2) + "\n")
    expected = {"positive_generic_const": "PASS", "positive_generic_mut": "PASS",
                "positive_zst_layout": "PASS" if label == "experimental" else "INCONCLUSIVE",
                "positive_zst_add": "PASS" if label == "experimental" else "INCONCLUSIVE",
                "negative_source_byte_offset": "EXPECTED_FALSE_POST_FAILURE",
                "negative_destination_byte_offset": "EXPECTED_FALSE_POST_FAILURE"}
    observed = {name: aggregate["all_cases"][name]["classification"] for name in expected}
    if label == "experimental" and not metadata_audit["ok"]:
        observed["positive_zst_layout"] = "INCONCLUSIVE"
    accepted_exit = status == 0 if label == "experimental" else status == 1
    return {"driver_exit": status, "classification": "PASS" if accepted_exit and observed == expected else "INCONCLUSIVE",
            "expected": expected, "observed": observed, "aggregate": str(result_file)}


def make_mutation_tool_home(args, control_dir, mutation, function_name):
    """Create a per-control shadow profile whose exporter mutates only one named fixture."""
    # Keep shadow binaries/source symlinks outside artifact paths.
    shadow = Path(tempfile.mkdtemp(prefix="layout-control-", dir=os.environ["RUNNER_TEMP"]))
    for entry in args.tool_home.iterdir():
        destination = shadow / entry.name
        if entry.name != "bin":
            os.symlink(entry, destination, target_is_directory=entry.is_dir())
    source_bin = args.tool_home / "bin"
    shadow_bin = shadow / "bin"
    shadow_bin.mkdir()
    for entry in source_bin.iterdir():
        if entry.name != "vf-rust-mir-exporter":
            destination = shadow_bin / entry.name
            if entry.name == "verifast" and entry.is_file():
                shutil.copy2(entry, destination)
            else:
                os.symlink(entry, destination, target_is_directory=entry.is_dir())
    wrapper = shadow_bin / "vf-rust-mir-exporter"
    wrapper.write_text("""#!/usr/bin/env python3
import hashlib, json, os, subprocess, sys
from pathlib import Path
import importlib.util
sys.path.insert(0, @HELPER@)
spec = importlib.util.spec_from_file_location("layout_matrix", Path(@HELPER@) / "check-rust-fieldless-layout.py")
layout_matrix = importlib.util.module_from_spec(spec)
spec.loader.exec_module(layout_matrix)
real = @REAL_EXPORTER@
schema = @SCHEMA@
mutation = @MUTATION@
type_name = "Z"
function = @FUNCTION@
record = Path(os.environ["VF_LAYOUT_MATRIX_MUTATION_DIR"]) / "mutation-record.json"
args = sys.argv[1:]
selected = False
selected_source = None
for arg in args:
    path = Path(arg)
    if path.is_file() and path.suffix == ".rs":
        try:
            selected = function.encode() in path.read_bytes()
            if selected:
                selected_source = path
        except OSError:
            pass
        if selected:
            break
proc = subprocess.run([real, *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
sys.stderr.buffer.write(proc.stderr)
if proc.returncode != 0 or not selected:
    if selected:
        record.write_text(json.dumps({"matched": True, "exporter_exit": proc.returncode, "mutation": mutation}, indent=2) + "\\n")
    sys.stdout.buffer.write(proc.stdout)
    raise SystemExit(proc.returncode)
canonical = proc.stdout
decode = subprocess.run(["capnp", "decode", schema, "VfMir"], input=canonical, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
if decode.returncode != 0:
    sys.stderr.buffer.write(decode.stderr)
    record.write_text(json.dumps({"matched": True, "decode_exit": decode.returncode, "mutation": mutation}, indent=2) + "\\n")
    raise SystemExit(decode.returncode)
try:
    canonical_text = decode.stdout.decode()
    layout_before = layout_matrix.adt_layout_info(canonical_text, type_name)
    transformed_text = layout_matrix.mutate_metadata_text(canonical_text, type_name, mutation)
    layout_after = layout_matrix.adt_layout_info(transformed_text, type_name)
except Exception as exc:
    record.write_text(json.dumps({"matched": True, "mutation_error": str(exc), "mutation": mutation}, indent=2) + "\\n")
    sys.stderr.write("layout-matrix metadata mutation failed: " + str(exc) + "\\n")
    raise SystemExit(98)
encode = subprocess.run(["capnp", "encode", schema, "VfMir"], input=transformed_text.encode(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
if encode.returncode != 0:
    sys.stderr.buffer.write(encode.stderr)
    record.write_text(json.dumps({"matched": True, "encode_exit": encode.returncode, "mutation": mutation}, indent=2) + "\\n")
    raise SystemExit(encode.returncode)
out_dir = Path(os.environ["VF_LAYOUT_MATRIX_MUTATION_DIR"])
(out_dir / "exporter-canonical.bin").write_bytes(canonical)
(out_dir / "exporter-canonical.txt").write_bytes(decode.stdout)
(out_dir / "exporter-mutated.txt").write_text(transformed_text)
(out_dir / "exporter-mutated.bin").write_bytes(encode.stdout)
record.write_text(json.dumps({"matched": True, "exporter_exit": 0, "decode_exit": 0, "encode_exit": 0,
    "mutation": mutation, "canonical_sha256": hashlib.sha256(canonical).hexdigest(),
    "mutated_sha256": hashlib.sha256(encode.stdout).hexdigest(),
    "selected_source_path": str(selected_source),
    "selected_source_sha256": hashlib.sha256(selected_source.read_bytes()).hexdigest(),
    "layout_before": layout_before, "layout_after": layout_after}, indent=2) + "\\n")
sys.stdout.buffer.write(encode.stdout)
""".replace("@HELPER@", repr(str(HERE)))
        .replace("@REAL_EXPORTER@", repr(str(args.source_home / "bin/vf-rust-mir-exporter")))
        .replace("@SCHEMA@", repr(str(args.schema)))
        .replace("@MUTATION@", repr(mutation))
        .replace("@FUNCTION@", repr(function_name)))
    wrapper.chmod(0o755)
    (control_dir / "exporter-wrapper.py").write_bytes(wrapper.read_bytes())
    (control_dir / "shadow-profile.json").write_text(json.dumps({
        "console_sha256": digest((shadow_bin / "verifast").read_bytes()),
        "base_console_sha256": digest((args.tool_home / "bin/verifast").read_bytes()),
        "wrapper_sha256": digest(wrapper.read_bytes()),
        "actual_exporter_sha256": digest((args.source_home / "bin/vf-rust-mir-exporter").read_bytes()),
    }, indent=2) + "\n")
    return shadow


def run_metadata_controls(args, outdir, prefix, fixture_cases):
    controls = {}
    specifications = (
        ("metadata_absent", "absent", "negative_absent_layout", "negative_absent_layout", "unproved"),
        ("metadata_malformed_alignment", "bad-align", "metadata_control_body", "metadata_control_body", "malformed"),
        ("metadata_malformed_size", "bad-size", "metadata_control_body", "metadata_control_body", "malformed"),
        ("metadata_wrong_binding", "wrong-name", "metadata_control_body", "metadata_control_body", "binding mismatch"),
        ("metadata_wrong_source_span", "wrong-span", "metadata_control_body", "metadata_control_body", "binding mismatch"),
        ("metadata_wrong_target", "wrong-target", "metadata_control_body", "metadata_control_body", "binding mismatch"),
        ("metadata_wrong_pointer_width", "wrong-width", "metadata_control_body", "metadata_control_body", "binding mismatch"),
    )
    for label, mutation, source_case, verifier_fn, expected_text in specifications:
        directory = outdir / "metadata-controls" / label
        directory.mkdir(parents=True)
        workdir = directory / "case-work"
        workdir.mkdir()
        source = prefix + fixture_cases[source_case]
        case_dir, metadata = prepare_case(source_case, source, workdir)
        mutation_dir = directory / "mutation-artifacts"
        mutation_dir.mkdir()
        shadow = make_mutation_tool_home(args, mutation_dir, mutation, verifier_fn)
        old_mutation_dir = os.environ.get("VF_LAYOUT_MATRIX_MUTATION_DIR")
        old_path = os.environ.get("PATH", "")
        os.environ["VF_LAYOUT_MATRIX_MUTATION_DIR"] = str(mutation_dir)
        os.environ["PATH"] = str(shadow / "bin") + os.pathsep + old_path
        try:
            statuses, unchanged = stages_for(source_case, source, case_dir,
                argparse.Namespace(tool_home=shadow, source_home=args.source_home,
                                   schema=args.schema, compiler_sysroot=args.compiler_sysroot))
        finally:
            os.environ["PATH"] = old_path
            if old_mutation_dir is None:
                os.environ.pop("VF_LAYOUT_MATRIX_MUTATION_DIR", None)
            else:
                os.environ["VF_LAYOUT_MATRIX_MUTATION_DIR"] = old_mutation_dir
        record_path = mutation_dir / "mutation-record.json"
        record = json.loads(record_path.read_text()) if record_path.exists() else {"matched": False}
        log = (case_dir / "verifast.log").read_text(errors="replace")
        headers = [m.group(2) for line in log.splitlines() if (m := HEADER.search(line))]
        errors = [line for line in log.splitlines() if "error:" in line]
        if mutation == "absent":
            line = metadata["target_assertion_line"]
            error = ERROR.search(errors[0]) if len(errors) == 1 else None
            records = [int(m.group(1)) for entry in log.splitlines() if (m := EXEC.search(entry))]
            expected = (
                len(headers) == 1 and headers[0] == verifier_fn and error is not None and
                int(error.group(1)) == line and line in records and
                metadata["target_assertion"] == "//@ assert size == 0;" and
                error.group(2) == "Assertion might not hold. (Cannot prove __result = 0.)"
            )
        else:
            diagnostic = "RustLayoutMetadata: malformed:" if expected_text == "malformed" else "RustLayoutMetadata: binding mismatch:"
            expected = len(errors) == 1 and diagnostic in errors[0]
        layout_before = record.get("layout_before") or ""
        layout_after = record.get("layout_after") or ""
        if mutation == "absent":
            mutation_shape_ok = "exact" in layout_before and "absent = void" in layout_after
        elif mutation == "bad-align":
            mutation_shape_ok = "exact" in layout_before and re.search(r"abiAlignBytes\s*=\s*3\b", layout_after) is not None
        elif mutation == "bad-size":
            mutation_shape_ok = "exact" in layout_before and re.search(r"sizeBytes\s*=\s*1\b", layout_after) is not None
        elif mutation == "wrong-name":
            mutation_shape_ok = "exact" in layout_before and "challenge_8::WrongZ" in layout_after
        elif mutation == "wrong-target":
            mutation_shape_ok = "exact" in layout_before and "wrong-unknown-target" in layout_after
        elif mutation == "wrong-width":
            mutation_shape_ok = "exact" in layout_before and re.search(r"bindingPointerWidth\s*=\s*8\b", layout_after) is not None
        else:
            before_span = re.search(r"bindingDefSpan\s*=\s*(\(.*?\))", layout_before, re.S)
            after_span = re.search(r"bindingDefSpan\s*=\s*(\(.*?\))", layout_after, re.S)
            mutation_shape_ok = "exact" in layout_before and before_span is not None and after_span is not None and before_span.group(1) != after_span.group(1)
        ok = (
            record.get("matched") is True and record.get("exporter_exit") == 0 and
            record.get("decode_exit") == 0 and record.get("encode_exit") == 0 and
            record.get("canonical_sha256") != record.get("mutated_sha256") and
            statuses.get("exporter") == 0 and statuses.get("decoder") == 0 and
            statuses.get("refinement") == 0 and unchanged and statuses.get("verifast") != 0 and
            expected and mutation_shape_ok
        )
        result = {
            "classification": "EXPECTED_METADATA_REJECTION" if ok else "INCONCLUSIVE",
            "mutation": mutation, "expected_diagnostic_or_obligation": expected_text,
            "mutation_record": record, "stages": statuses, "vf_errors": errors,
            "vf_function_headers": headers, "source_unchanged": unchanged,
            "mutation_shape_ok": mutation_shape_ok,
        }
        controls[label] = result
        (directory / "classification.json").write_text(json.dumps(result, indent=2) + "\n")
        print(f"{label}: {result['classification']}")
    return controls


def run_native_layout_controls(args, outdir):
    results = {}
    controls = (
        ("c_nonempty", HERE / "rust-fieldless-layout-controls/positive_c_nonempty.c"),
        ("cpp_empty", HERE / "rust-fieldless-layout-controls/positive_cpp_empty.cpp"),
        ("existing_rust_generic_struct", args.source_home / "tests/rust/purely_unsafe/generic_structs.rs"),
        ("existing_c_struct", args.source_home / "tests/chars__of_struct.c"),
        ("existing_cpp_constructor", args.source_home / "tests/cxx/constructors.cpp"),
    )
    for profile, tool_home in (("stock", args.stock_home), ("experimental", args.tool_home)):
        for name, fixture in controls:
            directory = outdir / "native-layout-controls" / profile / name
            directory.mkdir(parents=True)
            log = directory / "verifast.log"
            before = digest(fixture.read_bytes())
            flags = ["-c"] if fixture.suffix in {".c", ".cpp"} else []
            if fixture.suffix == ".rs":
                flags = ["-rustc_args", "--edition 2021"]
            status = run([tool_home / "bin/verifast", *flags, "-verbose", "1", fixture],
                         ROOT, log)
            after = digest(fixture.read_bytes())
            result = {
                "classification": "PASS" if status == 0 and before == after else "INCONCLUSIVE",
                "verifast_exit": status,
                "fixture_sha256_before": before,
                "fixture_sha256_after": after,
                "source_unchanged": before == after,
                "tool_home": str(tool_home.resolve()),
            }
            (directory / "classification.json").write_text(json.dumps(result, indent=2) + "\n")
            results[f"{profile}_{name}"] = result
            print(f"{profile}_{name}: {result['classification']}")
    return results


def run_negative_classifier_selfchecks(args, outdir):
    """Exercise the new strict negative gate on synthetic evidence on hosted CI."""
    directory = outdir / "negative-classifier-selfchecks"
    directory.mkdir()
    name = "negative_zst_nonzero_stride"
    source = (FIXTURE.read_bytes())
    _, bodies = marked_cases(source)
    fixture_prefix = source[:source.find(b"// CASE_BEGIN")]
    source = fixture_prefix + bodies[name]
    case_dir, metadata = prepare_case(name, source, directory)
    pointer_line = metadata["pointer_operation_line"]
    target_line = metadata["target_assertion_line"]
    header = f"1.0s: verified/lib.rs(1,1-2): Verifying function '{name}'"
    op = f"1.1s: verified/lib.rs({pointer_line},1-10): Executing statement"
    target = f"1.2s: verified/lib.rs({target_line},1-24): Executing statement"
    error = f"verified/lib.rs({target_line},1-24): error: Assertion might not hold. (Cannot prove ptr_add_(base, i, Z_type_info) != base.)"
    expected_log = "\n".join((header, op, target, error)) + "\n"
    variants = {
        "intended_target": (expected_log, {"exporter": 0, "decoder": 0, "verifast": 1, "refinement": 0}, metadata, True, "EXPECTED_TARGET_ASSERTION_FAILURE"),
        "missing_caller": ("\n".join((op, target, error)), {"exporter": 0, "decoder": 0, "verifast": 1, "refinement": 0}, metadata, True, "INCONCLUSIVE"),
        "missing_pointer_operation": ("\n".join((header, target, error)), {"exporter": 0, "decoder": 0, "verifast": 1, "refinement": 0}, metadata, True, "INCONCLUSIVE"),
        "missing_target_execution": ("\n".join((header, op, error)), {"exporter": 0, "decoder": 0, "verifast": 1, "refinement": 0}, metadata, True, "INCONCLUSIVE"),
        "wrong_assertion_text": (expected_log, {"exporter": 0, "decoder": 0, "verifast": 1, "refinement": 0}, dict(metadata, target_assertion="//@ assert result == base;"), True, "INCONCLUSIVE"),
        "wrong_vc_content": (expected_log.replace("Z_type_info) != base", "u64_type_info) != base"), {"exporter": 0, "decoder": 0, "verifast": 1, "refinement": 0}, metadata, True, "INCONCLUSIVE"),
        "wrong_location": (expected_log.replace(f"({target_line},1-24): error:", f"({target_line + 1},1-24): error:"), {"exporter": 0, "decoder": 0, "verifast": 1, "refinement": 0}, metadata, True, "INCONCLUSIVE"),
        "dead_code_instead_of_assertion": (expected_log.replace("Assertion might not hold. (Cannot prove ptr_add_(base, i, Z_type_info) != base.)", "Statement is unreachable"), {"exporter": 0, "decoder": 0, "verifast": 1, "refinement": 0}, metadata, True, "INCONCLUSIVE"),
        "export_failure": (expected_log, {"exporter": 1, "decoder": 0, "verifast": 1, "refinement": 0}, metadata, True, "INCONCLUSIVE"),
        "decode_failure": (expected_log, {"exporter": 0, "decoder": 1, "verifast": 1, "refinement": 0}, metadata, True, "INCONCLUSIVE"),
        "refinement_failure": (expected_log, {"exporter": 0, "decoder": 0, "verifast": 1, "refinement": 1}, metadata, True, "INCONCLUSIVE"),
        "false_positive_vf_zero": (expected_log, {"exporter": 0, "decoder": 0, "verifast": 0, "refinement": 0}, metadata, True, "INCONCLUSIVE"),
    }
    outcomes = {}
    original_log = case_dir / "verifast.log"
    for label, (log, statuses, trial_metadata, unchanged, expected) in variants.items():
        original_log.write_text(log)
        result = classify(name, source, trial_metadata, statuses, unchanged, case_dir,
                          {"ok": True, "exact": {"Z": (0, 8)}, "absent": {}})
        outcome = {"expected": expected, "observed": result["classification"],
                   "pass": result["classification"] == expected}
        outcomes[label] = outcome
    gate = all(item["pass"] for item in outcomes.values())
    (directory / "results.json").write_text(json.dumps({"pass": gate, "cases": outcomes}, indent=2) + "\n")
    print(f"negative classifier selfchecks: {'PASS' if gate else 'INCONCLUSIVE'} ({len(outcomes)} cases)")
    return {"classification": "PASS" if gate else "INCONCLUSIVE", "cases": outcomes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stock-home", type=Path, required=True,
                        help="separately retained official stock 26.09 profile")
    parser.add_argument("--tool-home", type=Path, required=True,
                        help="experimental source-built VeriFast profile")
    parser.add_argument("--source-home", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--compiler-sysroot", required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    if os.environ.get("GITHUB_ACTIONS") != "true" or os.environ.get("RUNNER_ENVIRONMENT") != "github-hosted" or os.environ.get("RUNNER_OS") != "Linux":
        parser.error("fieldless Rust layout matrix requires a GitHub-hosted Linux Actions runner")
    args.evidence.mkdir(parents=True, exist_ok=False)
    outdir = args.evidence
    (outdir / "cases").mkdir()
    env = {
        "stock_home": str(args.stock_home.resolve()),
        "experimental_tool_home": str(args.tool_home.resolve()),
        "source_home": str(args.source_home.resolve()),
        "compiler_sysroot": str(Path(args.compiler_sysroot).resolve()),
        "schema_sha256": digest(args.schema.read_bytes()),
        "fixture_sha256": digest(FIXTURE.read_bytes()),
        "baseline_fixture_sha256": digest(BASELINE_FIXTURE.read_bytes()),
        "tool_binary_sha256": {
            f"stock_{name}": digest((args.stock_home / "bin" / name).read_bytes())
            for name in ("verifast", "vf-rust-mir-exporter", "refinement-checker")
        } | {
            f"experimental_{name}": digest((args.tool_home / "bin" / name).read_bytes())
            for name in ("verifast", "vf-rust-mir-exporter", "refinement-checker")
        },
    }
    (outdir / "matrix-inputs.json").write_text(json.dumps(env, indent=2) + "\n")

    stock = invoke_unchanged_six(args, outdir, args.stock_home, "stock")
    (outdir / "stock-six-result.json").write_text(json.dumps(stock, indent=2) + "\n")
    six = invoke_unchanged_six(args, outdir, args.tool_home, "experimental")
    (outdir / "original-six-result.json").write_text(json.dumps(six, indent=2) + "\n")
    if stock["classification"] != "PASS":
        print("stock-profile comparison: INCONCLUSIVE", file=sys.stderr)

    prefix, wrappers = marked_cases(FIXTURE.read_bytes(), PHYSICAL_CASES)
    generic_prefix, generic_cases = marked_cases(BASELINE_FIXTURE.read_bytes(), {
        "positive_generic_const", "positive_generic_mut", "positive_zst_layout",
        "positive_zst_add", "negative_source_byte_offset", "negative_destination_byte_offset"})
    del generic_prefix
    sources = {name: prefix + body for name, body in wrappers.items()
               if name not in METADATA_CASES}
    for name, generic_key, ty, mut in (
        ("apply_const_z", "positive_generic_const", "Z", False),
        ("apply_mut_z", "positive_generic_mut", "Z", True),
        ("apply_const_u64", "positive_generic_const", "u64", False),
        ("apply_mut_u64", "positive_generic_mut", "u64", True),
    ):
        application = generic_application(prefix, generic_cases, name, ty, mut)
        # The generic helper/function bytes are copied verbatim from the passed stock fixture.
        if generic_key not in generic_cases or b"let result = base.add(i);" not in generic_cases[generic_key]:
            raise ValueError(f"stock-proved generic source body missing: {generic_key}")
        sources[name] = application

    outcomes = {}
    for name in sorted(sources):
        case_dir, metadata = prepare_case(name, sources[name], outdir / "cases")
        statuses, unchanged = stages_for(name, sources[name], case_dir, args)
        if name in POSITIVES:
            expected_layout = {}
            if name in {"zst_mut_add", "repr_rust_empty", "repr_c_empty"}:
                expected_layout = {"Z": (0, 8)} if name != "repr_c_empty" else {"CEmpty": (0, 8)}
            elif name == "repr_rust_empty_default":
                expected_layout = {"RustEmpty": (0, 1)}
            elif name == "repr_c_empty_default":
                expected_layout = {"CEmptyDefault": (0, 1)}
            elif name in {"apply_const_z", "apply_mut_z"}:
                expected_layout = {"Z": (0, 8)}
            layout_audit = inspect_layout_metadata(case_dir, expected_layout)
        elif name in NEGATIVES:
            layout_audit = inspect_layout_metadata(case_dir, {"Z": (0, 8)})
        else:
            names = {
                "unsupported_fielded": "Fielded",
                "unsupported_phantom_field": "PhantomField",
                "unsupported_generic_adt": "GenericField",
                "unsupported_packed": "PackedField",
                "unsupported_transparent": "TransparentField",
            }
            layout_audit = inspect_layout_metadata(case_dir, absent_types=(names[name],))
            source_requirements = {
                "unsupported_fielded": (b"struct Fielded", b"byte: u8"),
                "unsupported_phantom_field": (b"struct PhantomField", b"marker: PhantomData<u8>"),
                "unsupported_generic_adt": (b"struct GenericField<T>", b"marker: PhantomData<T>"),
                "unsupported_packed": (b"repr(C, packed)", b"word: u32"),
                "unsupported_transparent": (b"repr(transparent)", b"struct TransparentField(u8)"),
            }
            layout_audit["original_shape_source_evidence"] = {
                text.decode("ascii"): text in sources[name]
                for text in source_requirements[name]
            }
            layout_audit["ok"] = layout_audit["ok"] and all(
                layout_audit["original_shape_source_evidence"].values())
            (case_dir / "layout-metadata-audit.json").write_text(
                json.dumps(layout_audit, indent=2) + "\n")
        result = classify(name, sources[name], metadata, statuses, unchanged, case_dir, layout_audit)
        outcomes[name] = result
        (case_dir / "classification.json").write_text(json.dumps(result, indent=2) + "\n")
        print(f"{name}: {result['classification']}")

    required = {
        **{name: "PASS" for name in POSITIVES},
        **{name: "EXPECTED_TARGET_ASSERTION_FAILURE" for name in NEGATIVES},
        **{name: "UNSUPPORTED_LAYOUT_PASS" for name in UNSUPPORTED},
    }
    observed = {name: outcomes[name]["classification"] for name in required}
    metadata_controls = run_metadata_controls(args, outdir, prefix, wrappers)
    native_controls = run_native_layout_controls(args, outdir)
    classifier_selfchecks = run_negative_classifier_selfchecks(args, outdir)
    aggregate = {"stock_six": stock, "original_six": six, "expected": required, "observed": observed,
                 "cases": outcomes, "metadata_controls": metadata_controls,
                 "native_layout_controls": native_controls,
                 "negative_classifier_selfchecks": classifier_selfchecks}
    (outdir / "matrix-result.json").write_text(json.dumps(aggregate, indent=2) + "\n")
    failures = [f"{name}={observed[name]}" for name in required if observed[name] != required[name]]
    if six["classification"] != "PASS":
        failures.append("original_six=INCONCLUSIVE")
    if stock["classification"] != "PASS":
        failures.append("stock_six_comparison=INCONCLUSIVE")
    if failures:
        print("matrix gate inconclusive/failed: " + ", ".join(failures), file=sys.stderr)
        return 1
    control_failures = [f"{name}={value['classification']}" for name, value in metadata_controls.items()
                        if value["classification"] != "EXPECTED_METADATA_REJECTION"]
    control_failures.extend(f"{name}={value['classification']}" for name, value in native_controls.items()
                            if value["classification"] != "PASS")
    if classifier_selfchecks["classification"] != "PASS":
        control_failures.append("negative_classifier_selfchecks=INCONCLUSIVE")
    if control_failures:
        print("metadata controls inconclusive/failed: " + ", ".join(control_failures), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
