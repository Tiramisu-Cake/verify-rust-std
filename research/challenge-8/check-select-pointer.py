#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted, source-linked diagnostic for the pointer as_mut_ptr storage cast.

The helper is safe and uses an elided mutable-reference lifetime, as the real
method does. Its callers are unsafe proof probes. These are deliberately partial
diagnostics, not a method summary or a full select_unpredictable proof.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
from pathlib import Path


MAYBE_UNINIT_SHA256 = "7d588bf99e1bd7293b4b9c40fd71a6d5ed71ec6945920b166fc0c90547785702"
SOURCE_SIGNATURE = b"pub const fn as_mut_ptr(&mut self) -> *mut T"
SOURCE_BODY = (
    b"{\n"
    b"        // `MaybeUninit` and `ManuallyDrop` are both `repr(transparent)` so we can cast the pointer.\n"
    b"        self as *mut _ as *mut T\n"
    b"    }"
)
HELPER_NAME = "sort4_checked_as_mut_ptr"
VARIANTS = (
    "unknown", "none", "some", "wrong_result", "false_post",
    "assert_false", "duplicate_frame", "lost_cell",
)
POSITIVES = {"unknown", "none", "some"}
NEGATIVES = set(VARIANTS) - POSITIVES


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load_matrix(repo_root: Path):
    path = repo_root / "research/challenge-8/check-maybeuninit-new-pointer.py"
    spec = importlib.util.spec_from_file_location("sort4_constructor_matrix", path)
    require(spec is not None and spec.loader is not None, "constructor matrix loader unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source_certificate(repo_root: Path, matrix) -> tuple[bytes, dict]:
    path = repo_root / "library/core/src/mem/maybe_uninit.rs"
    source = path.read_bytes()
    require(sha(source) == MAYBE_UNINIT_SHA256, "MaybeUninit source pin changed")
    body = matrix.extract_braced_item(source, SOURCE_SIGNATURE)
    require(body == SOURCE_BODY, "as_mut_ptr expression or comment changed")
    require(body.count(b"self") == 1 and body.count(b"*mut T") == 1,
            "expected exactly one receiver identifier and one target cast")
    # A free function cannot name its parameter `self`. This is the only body
    # substitution; T is instantiated as *const Element in the resulting cast.
    specialized = body.replace(b"self", b"storage").replace(
        b"*mut T", b"*mut *const Element")
    require(specialized.count(b"storage as *mut _ as *mut *const Element") == 1,
            "specialized body no longer contains the exact source expression")
    return specialized, {
        "source_path": str(path),
        "source_sha256": sha(source),
        "source_signature": SOURCE_SIGNATURE.decode(),
        "source_body_sha256": sha(body),
        "source_body_exact": True,
        "body_substitutions": [
            "sole receiver identifier self -> storage (free-function syntax)",
            "sole type occurrence T -> *const Element (pointer specialization)",
        ],
        "specialized_body_sha256": sha(specialized),
        "adapter_limit": "ordinary non-const safe function; the generic const method is not proved",
        "target_obligation": (
            "result preserves the complete modeled storage pointer, wrapper cell, "
            "opaque wrapper-value ownership and unrelated frame; thread preserved "
            "and no unwind"
        ),
        "initialization_domain": "unknown/none/some ghost states; the cast does not read the value",
        "ownership_limit": (
            "certificate_mode=False keeps the profile's original opaque MaybeUninit own; "
            "callers must supply and receive that exact resource. This does not introduce "
            "or prove pointer-value ownership"
        ),
    }


def probe_name(variant: str) -> str:
    return "sort4_as_mut_ptr_" + variant + "_probe"


def target_line(verified: bytes, marker: bytes) -> int | None:
    return next((index for index, line in enumerate(verified.splitlines(), 1)
                 if marker in line), None)


def make_case(case_dir: Path, specialized: bytes, certificate: dict,
              matrix, variant: str) -> None:
    require(variant in VARIANTS, f"unknown as_mut_ptr diagnostic variant: {variant}")
    # Keep the cast body unannotated. Contracts are the only difference between
    # original and verified files; the helper is checked through its own body.
    contract = (
        b"req thread_token(?t) &*& t == currentThread &*& "
        b"*storage |-> ?value &*& "
        b"<std::mem::MaybeUninit<*const Element>>.own(t, value);\n"
        b"ens thread_token(t) &*& *storage |-> value &*& "
        b"<std::mem::MaybeUninit<*const Element>>.own(t, value) &*& "
        b"(result as pointer) == (storage as pointer);\n"
        b"on_unwind_ens false;"
    )
    helper = (
        b"pub fn " + HELPER_NAME.encode() +
        b"<Element>(storage: &mut std::mem::MaybeUninit<*const Element>) "
        b"-> *mut *const Element\n" + matrix.ghost_block(contract) +
        specialized + b"\n"
    )
    state = {
        "unknown": b"",
        "none": b" &*& std::mem::MaybeUninit::inner(value) == none",
        "some": b" &*& std::mem::MaybeUninit::inner(value) == some(?p)",
    }.get(variant, b"")
    state_post = {
        "unknown": b"",
        "none": b" &*& std::mem::MaybeUninit::inner(value) == none",
        "some": b" &*& std::mem::MaybeUninit::inner(value) == some(p)",
    }.get(variant, b"")
    resources = (
        b"thread_token(t) &*& *storage |-> value &*& "
        b"<std::mem::MaybeUninit<*const Element>>.own(t, value) &*& "
        b"[f](*frame |-> frame_value)"
    )
    pre = (
        b"req thread_token(?t) &*& t == currentThread &*& "
        b"*storage |-> ?value &*& "
        b"<std::mem::MaybeUninit<*const Element>>.own(t, value) &*& "
        b"[?f](*frame |-> ?frame_value)" + state + b";\n"
    )
    post = resources + state_post + b" &*& (result as pointer) == (storage as pointer)"
    if variant == "wrong_result":
        post = resources + b" &*& (result as pointer) != (storage as pointer)"
    elif variant == "false_post":
        post = b"false"
    elif variant == "duplicate_frame":
        post = resources + b" &*& [f](*frame |-> frame_value) &*& " \
            b"(result as pointer) == (storage as pointer)"
    elif variant == "lost_cell":
        post = (
            b"thread_token(t) &*& "
            b"<std::mem::MaybeUninit<*const Element>>.own(t, value) &*& "
            b"[f](*frame |-> frame_value) &*& "
            b"(result as pointer) == (storage as pointer)"
        )
    probe_contract = pre + b"// TARGET_POSTCONDITION\nens " + post + b";\n" + \
        b"on_unwind_ens false;"
    probe_body = b"{\n    let result = " + HELPER_NAME.encode() + b"(storage);\n"
    if variant == "assert_false":
        probe_body += b"    // TARGET_ASSERTION\n    //@ assert false;\n"
    probe_body += b"    result\n}\n"
    probe = (
        b"pub unsafe fn " + probe_name(variant).encode() +
        b"<Element>(storage: &mut std::mem::MaybeUninit<*const Element>, "
        b"frame: *const u8) -> *mut *const Element\n" +
        matrix.ghost_block(probe_contract) + probe_body
    )
    verified = helper + b"\n" + probe
    original = matrix.strip_ghost_annotations(verified)
    require(original.count(specialized) == 1, "source body is not unique in fixture")
    require(original.count(HELPER_NAME.encode()) == 2, "expected one body and one caller")
    require(matrix.strip_ghost_annotations(verified) == original,
            "ghost stripping changed executable Rust")
    case_dir.mkdir(parents=True, exist_ok=False)
    matrix.write_case(case_dir, original, verified, {
        **certificate,
        "variant": variant,
        "probe_name": probe_name(variant),
        "target_postcondition_line": target_line(verified, b"TARGET_POSTCONDITION"),
        "target_assertion_line": target_line(verified, b"TARGET_ASSERTION"),
        "probe_signature_line": target_line(verified, b"pub unsafe fn " + probe_name(variant).encode()),
        "probe_return_line": target_line(verified, b"    result"),
        "expected_stage": "verifier",
        "expected_predicate": {
            "wrong_result": "modeled result pointer inequality",
            "false_post": "false normal postcondition",
            "assert_false": "false assertion after checked helper call",
            "duplicate_frame": "second fractional frame cell",
            "lost_cell": "unreturned storage points-to chunk at leak check",
        }.get(variant, "pointer equality, wrapper cell/own and fractional frame"),
        "expected_location": (
            "named probe assertion" if variant == "assert_false" else
            "named probe leak check" if variant == "lost_cell" else
            "named probe normal postcondition"),
        "expected_class": "DIAGNOSTIC_POSITIVE" if variant in POSITIVES else
            "INTENDED_PROOF_REJECTION",
        "local_function_path_suffix": HELPER_NAME,
        "expected_external_call_count": 0,
        "ghost_stripped_equal": True,
        "intentionally_partial": True,
        "no_method_summary_or_translator_change": True,
    })


def function_log(log: str, name: str) -> str:
    marker = f"Verifying function '{name}'"
    start = log.find(marker)
    end = log.find("Verifying function '", start + len(marker)) if start >= 0 else -1
    return log[start:end if end >= 0 else None] if start >= 0 else ""


def classify(case_dir: Path, runner_result: dict, certificate: dict,
             variant: str, prerequisite_positive: bool) -> dict:
    mir = (case_dir / "compiler-mir.txt").read_text(errors="replace")
    log = (case_dir / "verifast.log").read_text(errors="replace")
    verified = (case_dir / "verified/lib.rs").read_bytes()
    original = (case_dir / "original/lib.rs").read_bytes()
    fixture = json.loads((case_dir / "fixture.json").read_text())
    helper_log = function_log(log, HELPER_NAME)
    probe_log = function_log(log, probe_name(variant))
    stripped = re.sub(rb"/\*@.*?@\*/", b"", verified, flags=re.S)
    stripped = re.sub(rb"(?m)^[ \t]*//@[^\r\n]*(?:\r?\n|$)", b"", stripped)
    stage_integrity = runner_result.get("stage_integrity", {})
    integrity = set(stage_integrity) == {"exporter", "decode", "verifast", "refinement"} and \
        all(item.get("unchanged") is True for item in stage_integrity.values())
    frontend_ok = (
        certificate["source_body_exact"] and
        verified != original and original == stripped and
        runner_result.get("exporter_exit") == 0 and
        runner_result.get("decode_exit") == 0 and
        runner_result.get("refinement_exit") == 0 and
        integrity and
        mir.count(f'defPath = "{HELPER_NAME}"') == 1 and
        mir.count(f'defPath = "{probe_name(variant)}"') == 1
    )
    helper_checked = (
        frontend_ok and
        f"Function '{HELPER_NAME}': Function prototype implementation check" in log and
        "Executing return statement" in helper_log and "Leak check." in helper_log and
        not any(": error:" in line for line in helper_log.splitlines())
    )
    errors = [line for line in log.splitlines() if ": error:" in line]
    first_error = errors[0] if errors else None
    error_line_match = re.search(r"verified/lib\.rs\((\d+),", first_error or "")
    error_line = int(error_line_match.group(1)) if error_line_match else None
    entered_probe = bool(probe_log)
    marker_line = fixture["target_assertion_line"] if variant == "assert_false" else \
        fixture["target_postcondition_line"]
    if variant == "lost_cell":
        target_location = error_line == fixture["probe_signature_line"]
        target_message = bool(first_error and "leaks heap chunks" in first_error)
    else:
        target_location = isinstance(marker_line, int) and error_line in {
            marker_line + 1, fixture["probe_return_line"]}
        target_message = bool(first_error and (
            "Cannot prove" in first_error or "Assertion might not hold" in first_error or
            "No matching heap" in first_error))
    if variant == "assert_false":
        target_location = isinstance(fixture["target_assertion_line"], int) and \
            error_line == fixture["target_assertion_line"] + 1
        target_message = bool(first_error and "Cannot prove false" in first_error)
    positive_pass = (
        variant in POSITIVES and frontend_ok and helper_checked and
        runner_result.get("verifast_exit") == 0 and entered_probe and
        "Executing return statement" in probe_log and "Leak check." in probe_log
    )
    intended_negative = (
        variant in NEGATIVES and prerequisite_positive and frontend_ok and helper_checked and
        runner_result.get("verifast_exit") == 1 and len(errors) == 1 and
        entered_probe and first_error is not None and first_error in probe_log and
        target_location and target_message
    )
    result = {
        "classification": (
            "DIAGNOSTIC_POSITIVE" if positive_pass else
            "INTENDED_PROOF_REJECTION" if intended_negative else "INCONCLUSIVE"
        ),
        "accepted_component": False,
        "full_select_proved": False,
        "tool_profile": "experimental-source-linked-maybeuninit-pointer-own-v2",
        "source_certificate": certificate,
        "runner_result": runner_result,
        "full_helper_mir_identity_count": mir.count(f'defPath = "{HELPER_NAME}"'),
        "full_probe_mir_identity_count": mir.count(f'defPath = "{probe_name(variant)}"'),
        "helper_entered": bool(helper_log),
        "helper_checked": helper_checked,
        "helper_return_seen": "Executing return statement" in helper_log,
        "helper_leak_check_seen": "Leak check." in helper_log,
        "frame_probe_entered": entered_probe,
        "frame_probe_return_seen": "Executing return statement" in probe_log,
        "frame_probe_leak_check_seen": "Leak check." in probe_log,
        "first_verifier_error": first_error,
        "first_verifier_error_line": error_line,
        "intended_negative_location": target_location if variant in NEGATIVES else None,
        "intended_negative_message": target_message if variant in NEGATIVES else None,
        "positive_prerequisite_passed": prerequisite_positive,
        "stage_source_integrity": integrity,
    }
    (case_dir / "diagnostic-classification.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def check_select(args: argparse.Namespace) -> dict:
    if os.environ.get("GITHUB_ACTIONS") != "true" or \
            os.environ.get("RUNNER_ENVIRONMENT") != "github-hosted" or \
            os.environ.get("RUNNER_OS") != "Linux":
        raise SystemExit("as_mut_ptr diagnostic requires GitHub-hosted Linux Actions")
    repo_root = Path(__file__).resolve().parents[2]
    matrix = load_matrix(repo_root)
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=False)
    specialized, certificate = source_certificate(repo_root, matrix)
    (evidence / "source-certificate.json").write_text(
        json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    results = []
    for variant in VARIANTS:
        prerequisite_positive = bool(results) and all(
            item["classification"] == "DIAGNOSTIC_POSITIVE" for item in results
            if item["variant"] in POSITIVES)
        if variant in NEGATIVES and not prerequisite_positive:
            break
        case_dir = evidence / ("as_mut_ptr_" + variant)
        make_case(case_dir, specialized, certificate, matrix, variant)
        runner_result = matrix.run_case(
            case_dir, args.schema, args.tool_home, args.compiler_sysroot, repo_root,
            "as_mut_ptr_" + variant, "diagnostic", certificate_mode=False)
        result = classify(case_dir, runner_result, certificate, variant,
                          prerequisite_positive)
        result["variant"] = variant
        results.append(result)
        if variant in POSITIVES and result["classification"] != "DIAGNOSTIC_POSITIVE":
            break
    summary = {
        "classification": "DIAGNOSTIC_MATRIX_PASS" if len(results) == len(VARIANTS) and
            all(item["classification"] == "DIAGNOSTIC_POSITIVE" for item in results
                if item["variant"] in POSITIVES) and
            all(item["classification"] == "INTENDED_PROOF_REJECTION" for item in results
                if item["variant"] in NEGATIVES) else "INCONCLUSIVE",
        "accepted_component": False,
        "full_select_proved": False,
        "source_certificate": certificate,
        "cases": results,
        "cases_not_run": list(VARIANTS[len(results):]),
    }
    (evidence / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stock-home", type=Path, required=True)
    parser.add_argument("--tool-home", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--compiler-sysroot", required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    result = check_select(args)
    print(json.dumps({"classification": result["classification"],
                      "evidence": str(args.evidence.resolve())}))


if __name__ == "__main__":
    main()
