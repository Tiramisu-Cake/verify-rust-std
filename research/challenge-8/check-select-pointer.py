#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted, source-linked diagnostic for the pointer as_mut_ptr storage cast.

This checks one ordinary safe body on the accepted pointer-ownership profile.
It is deliberately a partial diagnostic, not a MaybeUninit method summary or
an acceptance gate for the full select_unpredictable callee.
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
PROBE_NAME = "sort4_as_mut_ptr_frame_probe"


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
            "result preserves the complete modeled storage pointer, mutable borrow "
            "and unrelated frame; thread preserved and no unwind"
        ),
        "initialization_domain": (
            "unconstrained MaybeUninit state; the cast does not read its value. "
            "No explicit none/some setup call is introduced in this first diagnostic"
        ),
    }


def make_case(case_dir: Path, specialized: bytes, certificate: dict, matrix) -> None:
    # Keep the cast body unannotated. Contracts are the only difference between
    # original and verified files; the helper is checked through its own body.
    contract = (
        b"req thread_token(?t) &*& t == currentThread &*& "
        b"[?q]lifetime_token('a) &*& "
        b"full_borrow('a, <std::mem::MaybeUninit<*const Element>>.full_borrow_content(t, storage));\n"
        b"ens thread_token(t) &*& [q]lifetime_token('a) &*& "
        b"full_borrow('a, <std::mem::MaybeUninit<*const Element>>.full_borrow_content(t, storage)) "
        b"&*& (result as pointer) == (storage as pointer);\n"
        b"on_unwind_ens false;"
    )
    helper = (
        b"pub fn " + HELPER_NAME.encode() +
        b"<'a, Element>(storage: &'a mut std::mem::MaybeUninit<*const Element>) "
        b"-> *mut *const Element\n" + matrix.ghost_block(contract) +
        specialized + b"\n"
    )
    frame_contract = (
        b"req thread_token(?t) &*& t == currentThread &*& "
        b"[?q]lifetime_token('a) &*& "
        b"full_borrow('a, <std::mem::MaybeUninit<*const Element>>.full_borrow_content(t, storage)) "
        b"&*& [?f](*frame |-> ?frame_value);\n"
        b"ens thread_token(t) &*& [q]lifetime_token('a) &*& "
        b"full_borrow('a, <std::mem::MaybeUninit<*const Element>>.full_borrow_content(t, storage)) "
        b"&*& [f](*frame |-> frame_value) &*& "
        b"(result as pointer) == (storage as pointer);\n"
        b"on_unwind_ens false;"
    )
    probe = (
        b"pub unsafe fn " + PROBE_NAME.encode() +
        b"<'a, Element>(storage: &'a mut std::mem::MaybeUninit<*const Element>, "
        b"frame: *const u8) -> *mut *const Element\n" +
        matrix.ghost_block(frame_contract) +
        b"{\n    " + HELPER_NAME.encode() + b"(storage)\n}\n"
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
        "variant": "as_mut_ptr_existing_model_diagnostic",
        "local_function_path_suffix": HELPER_NAME,
        "expected_external_call_count": 0,
        "ghost_stripped_equal": True,
        "intentionally_partial": True,
        "no_method_summary_or_translator_change": True,
    })


def classify(case_dir: Path, runner_result: dict, certificate: dict) -> dict:
    mir = (case_dir / "compiler-mir.txt").read_text(errors="replace")
    log = (case_dir / "verifast.log").read_text(errors="replace")
    verified = (case_dir / "verified/lib.rs").read_bytes()
    original = (case_dir / "original/lib.rs").read_bytes()
    helper_marker = f"Verifying function '{HELPER_NAME}'"
    probe_marker = f"Verifying function '{PROBE_NAME}'"
    start = log.find(helper_marker)
    end = log.find("Verifying function '", start + len(helper_marker)) if start >= 0 else -1
    helper_log = log[start:end if end >= 0 else None] if start >= 0 else ""
    probe_start = log.find(probe_marker)
    probe_end = log.find("Verifying function '", probe_start + len(probe_marker)) if probe_start >= 0 else -1
    probe_log = log[probe_start:probe_end if probe_end >= 0 else None] if probe_start >= 0 else ""
    stage_integrity = runner_result.get("stage_integrity", {})
    integrity = set(stage_integrity) == {"exporter", "decode", "verifast", "refinement"} and \
        all(item.get("unchanged") is True for item in stage_integrity.values())
    candidate_pass = (
        certificate["source_body_exact"] and
        verified != original and original == re.sub(rb"/\*@.*?@\*/", b"", verified, flags=re.S) and
        runner_result.get("exporter_exit") == 0 and
        runner_result.get("decode_exit") == 0 and
        runner_result.get("refinement_exit") == 0 and
        runner_result.get("verifast_exit") == 0 and integrity and
        mir.count(f'defPath = "{HELPER_NAME}"') == 1 and
        mir.count(f'defPath = "{PROBE_NAME}"') == 1 and
        f"Function '{HELPER_NAME}': Function prototype implementation check" in log and
        "Executing return statement" in helper_log and "Leak check." in helper_log and
        "Executing return statement" in probe_log and "Leak check." in probe_log
    )
    result = {
        "classification": "DIAGNOSTIC_BODY_AND_FRAME_PASS" if candidate_pass else "INCONCLUSIVE",
        "accepted_component": False,
        "full_select_proved": False,
        "tool_profile": "experimental-source-linked-maybeuninit-pointer-own-v2",
        "source_certificate": certificate,
        "runner_result": runner_result,
        "full_helper_mir_identity_count": mir.count(f'defPath = "{HELPER_NAME}"'),
        "full_probe_mir_identity_count": mir.count(f'defPath = "{PROBE_NAME}"'),
        "helper_entered": start >= 0,
        "helper_return_seen": "Executing return statement" in helper_log,
        "helper_leak_check_seen": "Leak check." in helper_log,
        "frame_probe_entered": probe_start >= 0,
        "frame_probe_return_seen": "Executing return statement" in probe_log,
        "frame_probe_leak_check_seen": "Leak check." in probe_log,
        "first_verifier_error": next((line for line in log.splitlines() if ": error:" in line), None),
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
    case_dir = evidence / "as_mut_ptr_existing_model"
    make_case(case_dir, specialized, certificate, matrix)
    runner_result = matrix.run_case(
        case_dir, args.schema, args.tool_home, args.compiler_sysroot, repo_root,
        "as_mut_ptr_existing_model", "diagnostic", certificate_mode=False)
    result = classify(case_dir, runner_result, certificate)
    (evidence / "summary.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


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
