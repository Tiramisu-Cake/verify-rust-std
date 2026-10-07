#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Prepare and check the narrowly certified MaybeUninit constructor profile.

All compilation, MIR export/decode, VeriFast, and refinement work is guarded
for GitHub-hosted Linux Actions. This script only prepares disposable fixtures;
it never edits repository Rust sources.
"""

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


HINT_SHA256 = "d94ef86fbdac952fe7c9a6028536e15539b33dc188966fa4e9340fa7d94c30f8"
HINT_BLOB = "fe59166363b9cc049c0d48f4349f4dc9c0e458b8"
MAYBE_UNINIT_SHA256 = "7d588bf99e1bd7293b4b9c40fd71a6d5ed71ec6945920b166fc0c90547785702"
MANUALLY_DROP_SHA256 = "17e8e41866d3eadcfdc6f1a516e4ed9dd5555e10ad725aac3b04aec7c759731b"
MAYBE_DANGLING_SHA256 = "1cf24b2ec36fff143f329f2ef6db5b4d47cfa798da7f30d88b554b712c8f4b53"

SELECT_SCRIPT = "prepare-and-check-sort4-select.py"
CERT_MODULE = "sort4_certified_maybeuninit"
CERT_FUNCTION = "sort4_checked_maybeuninit_new"
CERT_FUNCTION_PATH = f"{CERT_MODULE}::{CERT_FUNCTION}"
CERT_DIAGNOSTIC = "SORT4-MAYBEUNINIT:"
RUST_SOURCE_NEW_CALL = b"MaybeUninit::new("
MIR_EXTERNAL_NEW = b"std::mem::MaybeUninit::<T>::new"
UNION_SIGNATURE = b"pub union MaybeUninit<T>"
NEW_SIGNATURE = b"pub const fn new(val: T) -> MaybeUninit<T>"
EXPECTED_NEW_BODY = b"{\n        MaybeUninit { value: ManuallyDrop::new(val) }\n    }"
INTRINSIC_SELECT = b"crate::intrinsics::select_unpredictable("


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def extract_braced_item(source: bytes, signature: bytes) -> bytes:
    require(source.count(signature) == 1,
            f"expected one source item signature: {signature.decode('ascii')}")
    start = source.index(signature)
    opening = source.find(b"{", start + len(signature))
    require(opening >= 0, "source item has no opening brace")
    depth = 0
    state = "code"
    block_depth = 0
    i = opening
    while i < len(source):
        byte = source[i]
        nxt = source[i + 1] if i + 1 < len(source) else 0
        if state == "line":
            if byte == 10:
                state = "code"
        elif state == "block":
            if byte == 47 and nxt == 42:
                block_depth += 1
                i += 1
            elif byte == 42 and nxt == 47:
                block_depth -= 1
                i += 1
                if block_depth == 0:
                    state = "code"
        elif state == "string":
            if byte == 92:
                i += 1
            elif byte == 34:
                state = "code"
        elif state == "char":
            if byte == 92:
                i += 1
            elif byte == 39:
                state = "code"
        elif byte == 47 and nxt == 47:
            state = "line"
            i += 1
        elif byte == 47 and nxt == 42:
            state = "block"
            block_depth = 1
            i += 1
        elif byte == 34:
            state = "string"
        elif byte == 39:
            closing = source.find(b"'", i + 1, min(len(source), i + 10))
            if closing >= 0:
                state = "char"
        elif byte == 123:
            depth += 1
        elif byte == 125:
            depth -= 1
            if depth == 0:
                return source[opening:i + 1]
        i += 1
    raise ValueError("unterminated source item")


def load_select_module(repo_root: Path):
    path = repo_root / "research/challenge-8" / SELECT_SCRIPT
    spec = importlib.util.spec_from_file_location("sort4_select_prepare", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load the existing select fixture preparer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def certify_repository_sources(repo_root: Path) -> dict:
    paths = {
        "hint": repo_root / "library/core/src/hint.rs",
        "maybe_uninit": repo_root / "library/core/src/mem/maybe_uninit.rs",
        "manually_drop": repo_root / "library/core/src/mem/manually_drop.rs",
        "maybe_dangling": repo_root / "library/core/src/mem/maybe_dangling.rs",
    }
    contents = {key: path.read_bytes() for key, path in paths.items()}
    expected = {
        "hint": HINT_SHA256,
        "maybe_uninit": MAYBE_UNINIT_SHA256,
        "manually_drop": MANUALLY_DROP_SHA256,
        "maybe_dangling": MAYBE_DANGLING_SHA256,
    }
    actual = {key: sha(value) for key, value in contents.items()}
    for key in expected:
        require(actual[key] == expected[key],
                f"pinned {key} source SHA-256 mismatch: {actual[key]}")
    hint_blob = subprocess.check_output(
        ["git", "-C", str(repo_root), "hash-object", str(paths["hint"])],
        text=True,
    ).strip()
    require(hint_blob == HINT_BLOB, f"pinned hint.rs blob mismatch: {hint_blob}")

    hint_body = load_select_module(repo_root).extract_body(contents["hint"])
    require(hint_body.count(INTRINSIC_SELECT) == 3,
            "pinned select body must retain exactly three intrinsics")
    require(hint_body.count(RUST_SOURCE_NEW_CALL) == 2,
            "pinned select body must retain exactly two MaybeUninit::new calls")

    union = extract_braced_item(contents["maybe_uninit"], UNION_SIGNATURE)
    new_body = extract_braced_item(contents["maybe_uninit"], NEW_SIGNATURE)
    require(union == b"{\n    uninit: (),\n    value: ManuallyDrop<T>,\n}",
            "pinned MaybeUninit union field definition changed")
    require(new_body == EXPECTED_NEW_BODY,
            "pinned MaybeUninit::new body changed")
    return {
        "repository_root": str(repo_root),
        "files": {
            key: {"path": str(paths[key]), "sha256": actual[key]}
            for key in paths
        },
        "hint_git_blob": hint_blob,
        "hint_body_sha256": sha(hint_body),
        "hint_intrinsic_call_count": hint_body.count(INTRINSIC_SELECT),
        "hint_external_maybeuninit_new_call_count": hint_body.count(RUST_SOURCE_NEW_CALL),
        "external_mir_constructor_def_path": MIR_EXTERNAL_NEW.decode("ascii"),
        "union_item_sha256": sha(union),
        "constructor_body_sha256": sha(new_body),
        "constructor_body_exact": True,
        "union_fields_exact": True,
        "manuallydrop_and_maybedangling_source_pinned": True,
        "exported_def_id_limitation": (
            "MIR exporter serializes def_path_str only; this source/MIR certificate "
            "is an explicit local-copy applicability link, not DefId equality"
        ),
    }


def ghost_block(contract: bytes) -> bytes:
    return b"\n/*@\n" + contract + b"\n@*/\n"


def strip_ghost_annotations(data: bytes) -> bytes:
    data = re.sub(rb"/\*@.*?@\*/", b"", data, flags=re.S)
    return re.sub(rb"(?m)^[ \t]*//@[^\r\n]*(?:\r?\n|$)", b"", data)


def constructor_source(cert: dict, variant: str = "positive") -> tuple[bytes, bytes, dict]:
    maybe_source = (Path(cert["files"]["maybe_uninit"]["path"])).read_bytes()
    union = extract_braced_item(maybe_source, UNION_SIGNATURE)
    fields = union[1:-1]
    body = extract_braced_item(maybe_source, NEW_SIGNATURE)
    require(body == EXPECTED_NEW_BODY, "constructor body no longer matches pinned expression")

    # The source's manual Copy impl is not part of this constructor proof;
    # pointer instantiation is Copy without adding a local Clone body.
    union_attrs = b"#[repr(transparent)]\n"
    local_union = union_attrs + b"pub union MaybeUninit<T> " + union + b"\n"
    helper_contract = (
        b"req thread_token(?t) &*& t == currentThread;\n"
        b"ens thread_token(t) &*& "
        b"std::mem::MaybeUninit::inner(result) == some(val);\n"
        b"on_unwind_ens false;"
    )
    signature = (
        b"pub fn " + CERT_FUNCTION.encode() +
        b"<Element>(val: *const Element) -> MaybeUninit<*const Element>"
    )
    helper_annotation = ghost_block(helper_contract)
    helper_body = body
    if variant == "wrong_active_field":
        helper_body = b"{\n        MaybeUninit { uninit: () }\n    }"
    elif variant == "wrong_value":
        helper_body = b"{\n        MaybeUninit { value: ManuallyDrop::new(std::ptr::null::<Element>()) }\n    }"

    local_module = (
        b"mod " + CERT_MODULE.encode() + b" {\n"
        b"    use std::mem::ManuallyDrop;\n"
        + local_union
        + b"\n    " + signature + helper_annotation + b"    " + helper_body + b"\n"
        b"}\n"
    )

    probe_contract = (
        b"req thread_token(?t) &*& t == currentThread &*& "
        b"[?f]*val |-> ?slot_value &*& *other |-> ?other_value;\n"
        b"ens thread_token(t) &*& [f]*val |-> slot_value &*& "
        b"*other |-> other_value &*& result == val;\n"
        b"on_unwind_ens false;"
    )
    probe_assert = (
        b"    //@ assert std::mem::MaybeUninit::inner(wrapped) == some(val);\n"
        b"    // TARGET_FRAME_ASSERTION\n"
        b"    //@ assert [f]*val |-> slot_value &*& *other |-> other_value;\n"
    )
    probe_signature = (
        b"pub fn sort4_checked_maybeuninit_frame_probe<Element>(\n"
        b"    val: *const Element, other: *mut u8,\n"
        b") -> *const Element\n"
    )
    if variant == "wrong_inner_post":
        probe_signature = (
            b"pub fn sort4_checked_maybeuninit_wrong_value_probe<Element>(\n"
            b"    val: *const Element, wrong: *const Element, other: *mut u8,\n"
            b") -> *const Element\n"
        )
        probe_contract = (
            b"req thread_token(?t) &*& t == currentThread &*& "
            b"(val as pointer) != (wrong as pointer) &*& "
            b"[?f]*val |-> ?slot_value &*& *other |-> ?other_value;\n"
            b"ens thread_token(t) &*& [f]*val |-> slot_value &*& "
            b"*other |-> other_value &*& result == val;\n"
            b"on_unwind_ens false;"
        )
        probe_assert = (
            b"    // TARGET_ASSERTION\n"
            b"    //@ assert std::mem::MaybeUninit::inner(wrapped) == some(wrong);\n"
            b"    //@ assert [f]*val |-> slot_value &*& *other |-> other_value;\n"
        )
    elif variant == "false_assert":
        probe_assert = (
            b"    // TARGET_ASSERTION\n"
            b"    //@ assert false;\n"
            b"    //@ assert [f]*val |-> slot_value &*& *other |-> other_value;\n"
        )
    elif variant == "resource_duplication":
        probe_assert = (
            b"    //@ assert std::mem::MaybeUninit::inner(wrapped) == some(val);\n"
            b"    // TARGET_ASSERTION\n"
            b"    //@ assert [f]*val |-> slot_value &*& [f]*val |-> slot_value;\n"
        )
    elif variant == "false_postcondition":
        probe_signature = (
            b"pub unsafe fn sort4_checked_maybeuninit_false_post_probe<Element>(\n"
            b"    val: *const Element, wrong: *const Element, other: *mut u8,\n"
            b") -> *const Element\n"
        )
        probe_contract = (
            b"req thread_token(?t) &*& t == currentThread &*& "
            b"(val as pointer) != (wrong as pointer) &*& "
            b"[?f]*val |-> ?slot_value &*& *other |-> ?other_value;\n"
            b"// TARGET_POSTCONDITION\n"
            b"ens thread_token(t) &*& [f]*val |-> slot_value &*& "
            b"*other |-> other_value &*& result == wrong;\n"
            b"on_unwind_ens false;"
        )
        probe_assert = (
            b"    //@ assert std::mem::MaybeUninit::inner(wrapped) == some(val);\n"
            b"    // TARGET_RETURN\n"
        )
    probe_signature = probe_signature.replace(b"pub fn ", b"pub unsafe fn ", 1)
    probe = (
        probe_signature
        + ghost_block(probe_contract)
        + b"{\n"
        b"    let wrapped = std::mem::MaybeUninit::new(val);\n"
        + probe_assert
        + b"    val\n"
        b"}\n"
    )
    if variant == "renamed_function":
        local_module = local_module.replace(
            CERT_FUNCTION.encode(), b"sort4_checked_maybeuninit_new_impostor", 1)
        probe = probe.replace(CERT_FUNCTION.encode(),
                              b"sort4_checked_maybeuninit_new_impostor")
    elif variant == "nonpointer_input":
        local_module = local_module.replace(
            b"<Element>(val: *const Element) -> MaybeUninit<*const Element>",
            b"<Element>(val: Element) -> MaybeUninit<Element>", 1)
    elif variant == "extra_union_field":
        local_module = local_module.replace(
            b"#[repr(transparent)]", b"#[repr(C)]", 1)
        local_module = local_module.replace(
            b"    value: ManuallyDrop<T>,\n", b"    value: ManuallyDrop<T>,\n    extra: u8,\n", 1)

    prefix = local_module + b"\n" + probe
    original_prefix = strip_ghost_annotations(prefix)
    verified_prefix = prefix
    require(strip_ghost_annotations(verified_prefix) == original_prefix,
            "constructor fixture changes runtime source beyond its declared variant")
    fixture_union = extract_braced_item(local_module, UNION_SIGNATURE)
    metadata = {
        "variant": variant,
        "local_function_path_suffix": CERT_FUNCTION_PATH,
        "expected_external_call_count": 1,
        "expected_union_fields": ["uninit: ()", "value: ManuallyDrop<T>"],
        "constructor_runtime_body_sha256": sha(body),
        "fixture_body_sha256": sha(helper_body),
        "fixture_union_fields_sha256": sha(fixture_union[1:-1]),
        "ghost_stripped_equal": True,
        "target_assertion_line": next((i for i, line in enumerate(verified_prefix.splitlines(), 1)
                                        if b"TARGET_ASSERTION" in line), None),
        "target_postcondition_line": next((i for i, line in enumerate(verified_prefix.splitlines(), 1)
                                           if b"TARGET_POSTCONDITION" in line), None),
        "target_return_line": next((i for i, line in enumerate(verified_prefix.splitlines(), 1)
                                     if b"TARGET_RETURN" in line), None),
    }
    return original_prefix, verified_prefix, metadata


def write_case(case_dir: Path, original: bytes, verified: bytes, metadata: dict) -> None:
    stripped = strip_ghost_annotations(verified)
    require(stripped == original,
            f"{case_dir.name}: original/verified runtime sources differ after ghost stripping")
    (case_dir / "original").mkdir(parents=True, exist_ok=False)
    (case_dir / "verified").mkdir()
    (case_dir / "original/lib.rs").write_bytes(original)
    (case_dir / "verified/lib.rs").write_bytes(verified)
    metadata["original_sha256"] = sha(original)
    metadata["verified_sha256"] = sha(verified)
    metadata["fixture_runtime_equal_after_ghost_strip"] = stripped == original
    (case_dir / "fixture.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")


def file_hashes(paths: tuple[Path, ...], root: Path) -> dict[str, str]:
    return {str(path.relative_to(root)): sha(path.read_bytes()) for path in paths}


def run_stage(argv: list[str | Path], cwd: Path, resource_path: Path,
              stdout_path: Path, stderr_path: Path | None = None,
              env: dict[str, str] | None = None) -> int:
    stderr_path = stdout_path if stderr_path is None else stderr_path
    with stdout_path.open("wb") as stdout:
        stderr = subprocess.STDOUT if stderr_path == stdout_path else stderr_path.open("wb")
        try:
            completed = subprocess.run(
                ["/usr/bin/time", "-v", "-o", str(resource_path),
                 "timeout", "--signal=TERM", "--kill-after=10s", "300s",
                 *map(str, argv)],
                cwd=cwd, stdout=stdout, stderr=stderr, check=False, env=env,
            )
            return completed.returncode
        except OSError as exc:
            stderr_path.write_text(f"could not start stage: {exc}\n")
            return 127
        finally:
            if stderr_path != stdout_path and hasattr(stderr, "close"):
                stderr.close()


def run_case(case_dir: Path, schema: Path, tool_home: Path, sysroot: str,
             repo_root: Path, mode: str, expect: str,
             certificate_mode: bool = True) -> dict:
    original = case_dir / "original/lib.rs"
    verified = case_dir / "verified/lib.rs"
    paths = (original, verified)
    base_env = os.environ.copy()
    if certificate_mode:
        base_env["SORT4_MAYBEUNINIT_REPO_ROOT"] = str(repo_root)
    else:
        base_env.pop("SORT4_MAYBEUNINIT_REPO_ROOT", None)
    stage_integrity = {}

    def audited(stage: str, argv: list[str | Path], stdout: Path,
                resources: Path, stderr: Path | None = None) -> int:
        before = file_hashes(paths, case_dir)
        status = run_stage(argv, case_dir, resources, stdout, stderr, base_env)
        after = file_hashes(paths, case_dir)
        stage_integrity[stage] = {"before": before, "after": after, "unchanged": before == after}
        (case_dir / f"source-integrity-{stage}.json").write_text(
            json.dumps(stage_integrity[stage], indent=2, sort_keys=True) + "\n")
        (case_dir / f"{stage}-exit-code.txt").write_text(f"{status}\n")
        return status

    exporter = audited("exporter", [
        tool_home / "bin/vf-rust-mir-exporter", "verified/lib.rs",
        f"--sysroot={sysroot}", "--edition", "2021", "--crate-type", "lib",
        "--vf-rust-mir-exporter:preprocess-readonly",
    ], case_dir / "compiler-mir.bin", case_dir / "exporter-resources.txt",
       case_dir / "exporter.log")
    if exporter == 0:
        before = file_hashes(paths, case_dir)
        with (case_dir / "compiler-mir.bin").open("rb") as source, \
                (case_dir / "compiler-mir.txt").open("wb") as decoded, \
                (case_dir / "capnp-decode.log").open("wb") as errors:
            try:
                proc = subprocess.run([
                    "/usr/bin/time", "-v", "-o", str(case_dir / "decode-resources.txt"),
                    "timeout", "--signal=TERM", "--kill-after=10s", "300s",
                    "capnp", "decode", str(schema), "VfMir",
                ], stdin=source, stdout=decoded, stderr=errors, check=False,
                    cwd=case_dir, env=base_env)
                decode = proc.returncode
            except OSError as exc:
                errors.write(f"could not start decoder: {exc}\n".encode())
                decode = 127
        after = file_hashes(paths, case_dir)
        stage_integrity["decode"] = {"before": before, "after": after, "unchanged": before == after}
    else:
        decode = 125
        (case_dir / "compiler-mir.txt").write_bytes(b"")
        (case_dir / "capnp-decode.log").write_text("not run because MIR export failed\n")
        (case_dir / "decode-resources.txt").write_text("stage not run\n")
        stage_integrity["decode"] = {"unchanged": True, "status": "not_run_export_failed"}
    (case_dir / "decode-exit-code.txt").write_text(f"{decode}\n")

    if exporter == 0 and decode == 0:
        vf = audited("verifast", [
            tool_home / "bin/verifast", "-rustc_args", "--edition 2021",
            "-verbose", "1", "verified/lib.rs",
        ], case_dir / "verifast.log", case_dir / "verifast-resources.txt")
    else:
        vf = 125
        (case_dir / "verifast.log").write_text("not run because export/decode failed\n")
        (case_dir / "verifast-resources.txt").write_text("stage not run\n")
        stage_integrity["verifast"] = {"unchanged": True, "status": "not_run_export_or_decode_failed"}

    refinement = audited("refinement", [
        tool_home / "bin/refinement-checker", "--rustc-args", "--edition 2021",
        "original/lib.rs", "verified/lib.rs",
    ], case_dir / "refinement.log", case_dir / "refinement-resources.txt")
    log = (case_dir / "verifast.log").read_text(errors="replace")
    headers = re.findall(
        r"^\s*\d+(?:\.\d+)?s: verified/lib\.rs\((\d+),\d+(?:-\d+(?:,\d+)?)?\): "
        r"Verifying function '([^']+)'$", log, re.M)
    errors = [line for line in log.splitlines() if ": error:" in line]
    diagnostic_seen = CERT_DIAGNOSTIC in log
    applicability_diagnostic_seen = bool(re.search(
        r"SORT4-MAYBEUNINIT: (?:certificate mismatch|unsupported certified union shape)", log))
    certified_body_seen = "certified local body" in log
    translated_body_seen = "checked local body translated (inner=1, aggregate=1" in log
    sources_unchanged = all(x.get("unchanged", False) for x in stage_integrity.values())
    base_ok = exporter == 0 and decode == 0 and refinement == 0 and sources_unchanged
    helper_headers = sum(name.endswith(CERT_FUNCTION) for _, name in headers)
    probe_headers = sum(name.endswith("sort4_checked_maybeuninit_frame_probe") for _, name in headers)
    decoded_mir = (case_dir / "compiler-mir.txt").read_text(errors="replace")
    external_call_count_mir = decoded_mir.count(f'name = "{MIR_EXTERNAL_NEW.decode()}"')
    redirect_count = log.count("redirected checked external pointer call")
    fixture = json.loads((case_dir / "fixture.json").read_text())
    error_lines = []
    for entry in errors:
        match = re.search(r"verified/lib\.rs\((\d+),", entry)
        if match:
            error_lines.append(int(match.group(1)))
    target_assertion_line = fixture.get("target_assertion_line")
    execution_lines = [int(match.group(1)) for entry in log.splitlines()
                       if (match := re.search(
                           r"verified/lib\.rs\((\d+),\d+(?:-\d+(?:,\d+)?)?\): "
                           r"(?:note: )?(?:Executing statement|Verifying call)$", entry))]
    targeted_error = (
        isinstance(target_assertion_line, int) and len(errors) == 1 and
        error_lines == [target_assertion_line + 1] and
        target_assertion_line + 1 in execution_lines
    )
    false_variant = fixture.get("variant") in {"false_assert", "stock_false_control"}
    resource_variant = fixture.get("variant") == "resource_duplication"
    false_post_variant = fixture.get("variant") == "false_postcondition"
    intended_false_message = (
        expect != "proof_negative" or not errors or
        ("Cannot prove false" in errors[0] if false_variant else
         "No matching heap" in errors[0] if resource_variant else
         "Cannot prove" in errors[0] if false_post_variant else
         "Assertion might not hold" in errors[0])
    )
    constructor_probe = fixture.get("variant") not in {
        "stock_false_control", "stock_pointer_frame"
    }
    expected_constructor_calls = 1 if constructor_probe else 0
    expected_proof_failure = (
        expect == "proof_negative" and base_ok and vf == 1 and targeted_error
        and intended_false_message and not applicability_diagnostic_seen
        and external_call_count_mir == expected_constructor_calls
        and redirect_count == expected_constructor_calls
    )
    if false_post_variant:
        target_postcondition = fixture.get("target_postcondition_line")
        target_return = fixture.get("target_return_line")
        expected_proof_failure = (
            expect == "proof_negative" and base_ok and vf == 1 and
            isinstance(target_postcondition, int) and len(errors) == 1 and
            error_lines == [target_postcondition + 1] and
            isinstance(target_return, int) and target_return + 1 in execution_lines and
            intended_false_message and not applicability_diagnostic_seen and
            external_call_count_mir == 1 and redirect_count == 1
        )
    if expect == "positive":
        outcome = "PASS" if (
            base_ok and vf == 0 and helper_headers == 1 and probe_headers == 1
            and certified_body_seen and translated_body_seen
            and external_call_count_mir == 1 and redirect_count == 1
        ) else "INCONCLUSIVE"
    elif expect == "control_positive":
        control_headers = sum(name.endswith("stock_pointer_frame") for _, name in headers)
        outcome = "PASS" if base_ok and vf == 0 and control_headers == 1 else "INCONCLUSIVE"
    elif expect == "proof_negative":
        outcome = "EXPECTED_PROOF_FAILURE" if expected_proof_failure else "INCONCLUSIVE"
    elif expect == "applicability_reject":
        outcome = "EXPECTED_APPLICABILITY_REJECT" if (
            exporter == 0 and decode == 0 and refinement == 0 and vf == 1
            and applicability_diagnostic_seen
        ) else "INCONCLUSIVE"
    elif expect == "actual_callee":
        actual_headers = sum(name == "select_unpredictable" for _, name in headers)
        log_bundle = "\n".join(
            (case_dir / name).read_text(errors="replace")
            for name in ("exporter.log", "verifast.log") if (case_dir / name).exists())
        redirect_count = log_bundle.count("redirected checked external pointer call")
        redirect_evidence = redirect_count == 2 and \
            "checked local body translated (inner=1, aggregate=1, redirected=2" in log_bundle
        outcome = "CALLEE_PASS" if (
            base_ok and vf == 0 and actual_headers == 1 and redirect_evidence
            and helper_headers == 1 and certified_body_seen and translated_body_seen
            and external_call_count_mir == 2
        ) else "CALLEE_INCONCLUSIVE"
    else:
        outcome = "INCONCLUSIVE"
    result = {
        "case": case_dir.name,
        "mode": mode,
        "expected_class": expect,
        "outcome": outcome,
        "exporter_exit": exporter,
        "decode_exit": decode,
        "verifast_exit": vf,
        "refinement_exit": refinement,
        "verified_function_headers": headers,
        "certifier_diagnostic_seen": diagnostic_seen,
        "certifier_applicability_rejection_seen": applicability_diagnostic_seen,
        "certified_local_body_evidence": certified_body_seen,
        "checked_local_body_translation_evidence": translated_body_seen,
        "targeted_negative_error": targeted_error,
        "first_verifast_error": errors[0] if errors else None,
        "checked_constructor_header_count": helper_headers,
        "frame_probe_header_count": probe_headers,
        "external_maybeuninit_new_defpath_count_in_mir": external_call_count_mir,
        "checked_external_pointer_redirect_count": redirect_count,
        "source_unchanged_at_every_stage": sources_unchanged,
        "stage_integrity": stage_integrity,
    }
    (case_dir / "classification.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


CONSTRUCTOR_CASES = [
    ("constructor_positive", "positive", "positive"),
    ("wrong_inner_post", "wrong_inner_post", "proof_negative"),
    ("false_assert", "false_assert", "proof_negative"),
    ("false_postcondition", "false_postcondition", "proof_negative"),
    ("resource_duplication", "resource_duplication", "proof_negative"),
    ("wrong_active_field", "wrong_active_field", "applicability_reject"),
    ("wrong_value", "wrong_value", "applicability_reject"),
    ("renamed_function", "renamed_function", "applicability_reject"),
    ("nonpointer_input", "nonpointer_input", "applicability_reject"),
    ("extra_union_field", "extra_union_field", "applicability_reject"),
]


def prepare_constructor_case(evidence: Path, cert: dict,
                             name: str, variant: str) -> Path:
    original_prefix, verified_prefix, metadata = constructor_source(cert, variant)
    case_dir = evidence / name
    case_dir.mkdir(parents=True, exist_ok=False)
    write_case(case_dir, original_prefix, verified_prefix, metadata)
    return case_dir


def prepare_stock_false_control(evidence: Path) -> Path:
    case_dir = evidence / "stock_false_control"
    verified = b"""pub fn stock_false_control()\n/*@\nreq true;\nens true;\non_unwind_ens false;\n@*/\n{\n    // TARGET_ASSERTION\n    //@ assert false;\n}\n"""
    original = strip_ghost_annotations(verified)
    metadata = {
        "variant": "stock_false_control",
        "target_assertion_line": next(
            i for i, line in enumerate(verified.splitlines(), 1)
            if b"TARGET_ASSERTION" in line),
        "local_function_path_suffix": "stock_false_control",
        "expected_external_call_count": 0,
    }
    case_dir.mkdir(parents=True, exist_ok=False)
    write_case(case_dir, original, verified, metadata)
    return case_dir


def prepare_stock_pointer_frame(evidence: Path) -> Path:
    case_dir = evidence / "stock_pointer_frame"
    verified = b"""pub unsafe fn stock_pointer_frame(p: *const u8, other: *mut u8) -> u8
/*@
req thread_token(?t) &*& t == currentThread &*& [?f]*p |-> ?pv &*& *other |-> ?ov;
ens thread_token(t) &*& [f]*p |-> pv &*& *other |-> ov &*& result == pv;
on_unwind_ens false;
@*/
{
    unsafe { *p }
}
"""
    original = strip_ghost_annotations(verified)
    metadata = {"variant": "stock_pointer_frame", "expected_external_call_count": 0}
    case_dir.mkdir(parents=True, exist_ok=False)
    write_case(case_dir, original, verified, metadata)
    return case_dir


def run_native_controls(evidence: Path, repo_root: Path,
                        stock_home: Path, tool_home: Path) -> dict:
    fixtures = (
        ("c_nonempty", repo_root / "research/challenge-8/rust-fieldless-layout-controls/positive_c_nonempty.c"),
        ("cpp_empty", repo_root / "research/challenge-8/rust-fieldless-layout-controls/positive_cpp_empty.cpp"),
    )
    results = {}
    for profile, home in (("stock", stock_home), ("patched", tool_home)):
        for name, fixture in fixtures:
            case_dir = evidence / "native-controls" / profile / name
            case_dir.mkdir(parents=True, exist_ok=False)
            before = sha(fixture.read_bytes())
            status = run_stage(
                [home / "bin/verifast", "-c", "-verbose", "1", fixture],
                repo_root, case_dir / "resources.txt", case_dir / "verifast.log",
            )
            after = sha(fixture.read_bytes())
            outcome = "PASS" if status == 0 and before == after else "INCONCLUSIVE"
            result = {"outcome": outcome, "verifast_exit": status,
                      "source_sha256_before": before, "source_sha256_after": after,
                      "source_unchanged": before == after, "tool_home": str(home.resolve())}
            (case_dir / "classification.json").write_text(
                json.dumps(result, indent=2, sort_keys=True) + "\n")
            results[f"{profile}_{name}"] = result
    return results


def make_actual_callee_case(evidence: Path, repo_root: Path,
                            cert: dict) -> Path:
    select = load_select_module(repo_root)
    target = evidence / "actual_select_after_constructor"
    target.mkdir(parents=True, exist_ok=False)
    prepared = target / "prepared"
    prepared.mkdir()
    select_case = prepared / "actual_select_pointer"
    select.prepare(repo_root / "library/core/src/hint.rs", select_case,
                   prepared / "extraction-integrity.json")
    original_prefix, verified_prefix, metadata = constructor_source(cert, "positive")
    frame_probe_marker = b"pub unsafe fn sort4_checked_maybeuninit_frame_probe"
    original_module = original_prefix.split(frame_probe_marker, 1)[0]
    verified_module = verified_prefix.split(frame_probe_marker, 1)[0]
    # Keep the actual select body and its two standard constructor calls byte-identical.
    for variant_name, module_prefix in (("original", original_module),
                                        ("verified", verified_module)):
        path = select_case / variant_name / "lib.rs"
        data = path.read_bytes()
        path.write_bytes(data + b"\n" + module_prefix)
    original = select_case / "original/lib.rs"
    verified = select_case / "verified/lib.rs"
    require(verified.read_bytes().count(RUST_SOURCE_NEW_CALL) == 2,
            "actual select adapter must retain both external constructor calls")
    select_meta = json.loads((select_case / "extraction.json").read_text())
    metadata.update({
        "actual_select_original_sha256_before_helper": select_meta["original_sha256"],
        "actual_select_verified_sha256_before_helper": select_meta["verified_sha256"],
        "external_constructor_call_count": verified.read_bytes().count(RUST_SOURCE_NEW_CALL),
        "actual_select_body_sha256": select_meta["body_sha256"],
        "helper_source_sha256": sha(verified_module),
        "verified_ghost_strip_exact": strip_ghost_annotations(verified.read_bytes())
            == original.read_bytes(),
    })
    (target / "fixture.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    # run_case expects the original and verified at the case root.
    final = evidence / "actual_select_after_constructor_run"
    final.mkdir()
    (final / "original").mkdir()
    (final / "verified").mkdir()
    (final / "original/lib.rs").write_bytes(original.read_bytes())
    (final / "verified/lib.rs").write_bytes(verified.read_bytes())
    (final / "fixture.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    return final


def quarantine_false_assert_success(evidence: Path, case_name: str,
                                    result: dict) -> None:
    if case_name not in {"stock_false_control", "patched_false_control", "false_assert"}:
        return
    if result.get("verifast_exit") != 0:
        return
    record = {
        "status": "PROFILE_QUARANTINED",
        "reason": "a deliberately false assertion unexpectedly verified",
        "case": case_name,
        "verifast_exit": result.get("verifast_exit"),
        "classification": result,
        "profile_must_not_be_used": True,
        "remaining_constructor_cases": "NOT_RUN",
        "actual_callee": "NOT_RUN",
    }
    (evidence / "FALSE-ASSERT-PROFILE-QUARANTINED.json").write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n")
    raise SystemExit(
        f"profile quarantined: false assertion unexpectedly verified in {case_name}")


def main() -> None:
    if os.environ.get("GITHUB_ACTIONS") != "true" or \
            os.environ.get("RUNNER_ENVIRONMENT") != "github-hosted" or \
            os.environ.get("RUNNER_OS") != "Linux":
        raise SystemExit("MaybeUninit constructor checks require GitHub-hosted Linux Actions")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stock-home", type=Path, required=True)
    parser.add_argument("--tool-home", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--compiler-sysroot", required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument(
        "--feasibility-only", action="store_true",
        help="run the constructor positive as a partial diagnostic; never accept the profile",
    )
    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parents[2]
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=False)
    source_cert = certify_repository_sources(repo_root)
    (evidence / "source-certificate.json").write_text(
        json.dumps(source_cert, indent=2, sort_keys=True) + "\n")

    stock_control = prepare_stock_false_control(evidence)
    stock_false_result = run_case(stock_control, args.schema, args.stock_home,
                                  args.compiler_sysroot, repo_root,
                                  "stock_false_control", "proof_negative",
                                  certificate_mode=False)
    quarantine_false_assert_success(evidence, "stock_false_control", stock_false_result)
    patched_false_dir = evidence / "patched_false_control"
    patched_false_dir.mkdir(parents=True, exist_ok=False)
    verified_false = (stock_control / "verified/lib.rs").read_bytes()
    original_false = (stock_control / "original/lib.rs").read_bytes()
    write_case(patched_false_dir, original_false, verified_false,
               json.loads((stock_control / "fixture.json").read_text()))
    patched_false_result = run_case(patched_false_dir, args.schema, args.tool_home,
                                    args.compiler_sysroot, repo_root,
                                    "patched_false_control", "proof_negative",
                                    certificate_mode=False)
    quarantine_false_assert_success(evidence, "patched_false_control", patched_false_result)

    stock_frame_dir = prepare_stock_pointer_frame(evidence)
    stock_frame_result = run_case(stock_frame_dir, args.schema, args.stock_home,
                                  args.compiler_sysroot, repo_root,
                                  "stock_pointer_frame", "control_positive",
                                  certificate_mode=False)
    patched_frame_dir = evidence / "patched_pointer_frame"
    patched_frame_dir.mkdir(parents=True, exist_ok=False)
    write_case(patched_frame_dir,
               (stock_frame_dir / "original/lib.rs").read_bytes(),
               (stock_frame_dir / "verified/lib.rs").read_bytes(),
               json.loads((stock_frame_dir / "fixture.json").read_text()))
    patched_frame_result = run_case(patched_frame_dir, args.schema, args.tool_home,
                                    args.compiler_sysroot, repo_root,
                                    "patched_pointer_frame", "control_positive",
                                    certificate_mode=False)
    native_results = run_native_controls(evidence, repo_root, args.stock_home, args.tool_home)
    baseline_results = {
        "stock_false_control": stock_false_result,
        "patched_false_control": patched_false_result,
        "stock_pointer_frame": stock_frame_result,
        "patched_pointer_frame": patched_frame_result,
        "native_controls": native_results,
    }
    baselines_ok = (
        stock_false_result["outcome"] == "EXPECTED_PROOF_FAILURE" and
        patched_false_result["outcome"] == "EXPECTED_PROOF_FAILURE" and
        stock_frame_result["outcome"] == "PASS" and
        patched_frame_result["outcome"] == "PASS" and
        all(item["outcome"] == "PASS" for item in native_results.values())
    )
    if not baselines_ok:
        (evidence / "summary.json").write_text(json.dumps({
            "constructor_acceptance": False,
            "constructor_cases": [],
            "constructor_cases_not_run": len(CONSTRUCTOR_CASES),
            "baselines": baseline_results,
            "actual_callee_status": "NOT_RUN",
        }, indent=2, sort_keys=True) + "\n")
        raise SystemExit("stock/patched pointer, false-assertion, or C/C++ baseline did not pass")

    results = []
    first_name, first_variant, first_expectation = CONSTRUCTOR_CASES[0]
    positive_dir = prepare_constructor_case(evidence, source_cert, first_name, first_variant)
    results.append(run_case(positive_dir, args.schema, args.tool_home,
                            args.compiler_sysroot, repo_root,
                            "constructor", first_expectation))
    if args.feasibility_only:
        feasibility_pass = results[0]["outcome"] == "PASS"
        (evidence / "constructor-negatives-not-run.json").write_text(json.dumps({
            "status": "NOT_RUN",
            "reason": "C4 feasibility-only mode; no acceptance matrix or full MIR gate",
            "remaining_cases": [name for name, _, _ in CONSTRUCTOR_CASES[1:]],
        }, indent=2, sort_keys=True) + "\n")
        (evidence / "actual-callee-not-run.json").write_text(json.dumps({
            "status": "NOT_RUN",
            "reason": "C4 feasibility-only mode does not authorize callee acceptance",
        }, indent=2, sort_keys=True) + "\n")
        summary = {
            "profile_status": "UNACCEPTED",
            "feasibility_only": True,
            "feasibility_result": "PASS" if feasibility_pass else "INCONCLUSIVE",
            "constructor_acceptance": False,
            "baselines": baseline_results,
            "constructor_cases": results,
            "constructor_cases_not_run": len(CONSTRUCTOR_CASES) - len(results),
            "remaining_constructor_cases": [name for name, _, _ in CONSTRUCTOR_CASES[1:]],
            "actual_callee_status": "NOT_RUN",
            "source_certificate": source_cert,
            "tool_home": str(args.tool_home.resolve()),
            "stock_home": str(args.stock_home.resolve()),
            "compiler_sysroot": args.compiler_sysroot,
            "schema": str(args.schema.resolve()),
        }
        (evidence / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
        print(json.dumps({
            "profile_status": "UNACCEPTED",
            "feasibility_result": summary["feasibility_result"],
            "actual_callee_status": "NOT_RUN",
        }, sort_keys=True))
        if not feasibility_pass:
            raise SystemExit(1)
        return
    if results[0]["outcome"] == "PASS":
        for case_name, variant, expectation in CONSTRUCTOR_CASES[1:]:
            case_dir = prepare_constructor_case(evidence, source_cert, case_name, variant)
            case_result = run_case(case_dir, args.schema, args.tool_home,
                                   args.compiler_sysroot, repo_root,
                                   "constructor", expectation)
            results.append(case_result)
            quarantine_false_assert_success(evidence, case_name, case_result)
    else:
        (evidence / "constructor-negatives-not-run.json").write_text(json.dumps({
            "status": "NOT_RUN",
            "reason": "constructor positive did not pass; proof and applicability controls are gated",
            "remaining_cases": [name for name, _, _ in CONSTRUCTOR_CASES[1:]],
        }, indent=2, sort_keys=True) + "\n")

    constructor_acceptance = (
        len(results) == len(CONSTRUCTOR_CASES) and
        results[0]["outcome"] == "PASS" and
        all(item["outcome"] == "EXPECTED_PROOF_FAILURE" for item in results[1:5]) and
        all(item["outcome"] == "EXPECTED_APPLICABILITY_REJECT" for item in results[5:])
    )
    final_callee = None
    if constructor_acceptance:
        callee_case = make_actual_callee_case(evidence, repo_root, source_cert)
        final_callee = run_case(callee_case, args.schema, args.tool_home,
                                args.compiler_sysroot, repo_root,
                                "actual_callee", "actual_callee")
    else:
        (evidence / "actual-callee-not-run.json").write_text(json.dumps({
            "status": "NOT_RUN",
            "reason": "full constructor acceptance matrix did not pass",
        }, indent=2, sort_keys=True) + "\n")

    summary = {
        "constructor_acceptance": constructor_acceptance,
        "baselines": baseline_results,
        "constructor_cases": results,
        "constructor_cases_not_run": len(CONSTRUCTOR_CASES) - len(results),
        "actual_callee": final_callee,
        "actual_callee_status": (
            final_callee["outcome"] if final_callee else "NOT_RUN"
        ),
        "tool_home": str(args.tool_home.resolve()),
        "stock_home": str(args.stock_home.resolve()),
        "compiler_sysroot": args.compiler_sysroot,
        "schema": str(args.schema.resolve()),
        "source_certificate": source_cert,
    }
    (evidence / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "constructor_acceptance": constructor_acceptance,
        "actual_callee_status": summary["actual_callee_status"],
        "cases": {item["case"]: item["outcome"] for item in results},
    }, sort_keys=True))
    if not constructor_acceptance:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
