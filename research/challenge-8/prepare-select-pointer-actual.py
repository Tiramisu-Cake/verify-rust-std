#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted first-obligation diagnostic for the exact pointer select body.

The two checked callees are source-linked components. This experiment does not
accept a select_unpredictable proof, even if the verifier unexpectedly succeeds.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
from pathlib import Path


AS_MUT_PTR_DEF_PATH = 'name = "std::mem::MaybeUninit::<T>::as_mut_ptr"'
INTRINSIC_DEF_PATH = 'name = "std::intrinsics::select_unpredictable"'
INTRINSIC_ACTUAL_CERT = "SORT4-SELECT-INTRINSIC: full typed actual MIR graph accepted"
INTRINSIC_PTR_CALL_ONE = "SORT4-SELECT-INTRINSIC: modeled typed pointer call 1"
INTRINSIC_PTR_CALL_TWO = "SORT4-SELECT-INTRINSIC: modeled typed pointer call 2"
INTRINSIC_MU_CALL = "SORT4-SELECT-INTRINSIC: modeled typed wrapper call 1"
CONSTRUCTOR_CERT = "SORT4-MAYBEUNINIT: full typed constructor MIR graph accepted"
AS_MUT_PTR_CERT = "SORT4-AS-MUT-PTR: full typed body MIR graph accepted"
AS_MUT_PTR_TRANSLATED = "SORT4-AS-MUT-PTR: checked SAFE body translated (redirected=2, expected=2)"
CONSTRUCTOR_TRANSLATED = (
    "SORT4-MAYBEUNINIT: checked local body translated "
    "(inner=1, aggregate=1, redirected=2, expected=2)"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load_script(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None,
            f"could not load {path.name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def checked_as_mut_ptr_helper(body: bytes, constructor, pointer) -> bytes:
    # Match the accepted component's source contract and body byte for byte.
    contract = (
        b"req thread_token(?t) &*& t == currentThread &*& "
        b"*storage |-> ?value &*& " + pointer.POINTER_OWN + b";\n"
        b"ens thread_token(t) &*& *storage |-> value &*& "
        + pointer.POINTER_OWN + b" &*& "
        b"(result as pointer) == (storage as pointer);\n"
        b"on_unwind_ens false;"
    )
    helper = (
        pointer.LOCAL_SIGNATURE.encode() + b"\n" +
        constructor.ghost_block(contract) + body + b"\n"
    )
    require(helper.startswith(pointer.LOCAL_SIGNATURE.encode() + b"\n"),
            "checked as_mut_ptr signature changed")
    require(helper.count(body) == 1, "checked as_mut_ptr body is not unique")
    return helper


def prepare_case(evidence: Path, repo_root: Path, constructor, pointer) -> tuple[Path, dict]:
    constructor_cert = constructor.certify_repository_sources(repo_root)
    as_mut_ptr_body, as_mut_ptr_cert = pointer.source_certificate(repo_root, constructor)
    select = constructor.load_select_module(repo_root)
    exact_select_body = select.extract_body(
        (repo_root / "library/core/src/hint.rs").read_bytes())
    (evidence / "constructor-source-certificate.json").write_text(
        json.dumps(constructor_cert, indent=2, sort_keys=True) + "\n")
    (evidence / "as-mut-ptr-source-certificate.json").write_text(
        json.dumps(as_mut_ptr_cert, indent=2, sort_keys=True) + "\n")
    base_case = constructor.make_actual_callee_case(
        evidence, repo_root, constructor_cert)
    verified_base = (base_case / "verified/lib.rs").read_bytes()
    original_base = (base_case / "original/lib.rs").read_bytes()
    require(constructor.strip_ghost_annotations(verified_base) == original_base,
            "constructor plus select adapter changed runtime source")
    require(verified_base.count(exact_select_body) == 1 and
            original_base.count(exact_select_body) == 1,
            "actual select body is not byte-exact and unique")
    require(b"ens thread_token(t) &*& (result as pointer) ==\n"
            b"        (if condition { true_val as pointer } else { false_val as pointer });"
            in verified_base and
            b"on_unwind_ens false;" in verified_base,
            "actual select lost its full pointer result or unwind post")
    require(verified_base.count(b".as_mut_ptr()") == 2,
            "actual select must retain both as_mut_ptr calls")
    helper = checked_as_mut_ptr_helper(as_mut_ptr_body, constructor, pointer)
    original_helper = constructor.strip_ghost_annotations(helper)
    case = evidence / "actual_select_after_constructor_and_as_mut_ptr"
    (case / "original").mkdir(parents=True)
    (case / "verified").mkdir()
    original = original_base + b"\n" + original_helper
    verified = verified_base + b"\n" + helper
    require(constructor.strip_ghost_annotations(verified) == original,
            "combined verified source differs beyond ghost annotations")
    require(verified.count(exact_select_body) == 1 and
            original.count(exact_select_body) == 1,
            "appending as_mut_ptr changed actual select body")
    require(verified.count(select.INTRINSIC_CALL) == 3 and
            all(fragment in verified for fragment in select.REQUIRED_BODY_FRAGMENTS),
            "select lost an intrinsic, guard, drop, forget, or assume_init")
    require(verified.count(constructor.RUST_SOURCE_NEW_CALL) == 2 and
            verified.count(b".as_mut_ptr()") == 2,
            "select lost one of its four external MaybeUninit calls")
    require(verified.count(pointer.LOCAL_SIGNATURE.encode()) == 1 and
            verified.count(as_mut_ptr_body) == 1,
            "checked as_mut_ptr source body is not unique")
    (case / "original/lib.rs").write_bytes(original)
    (case / "verified/lib.rs").write_bytes(verified)
    fixture = json.loads((base_case / "fixture.json").read_text())
    fixture.update({
        "variant": "actual_select_after_constructor_and_as_mut_ptr",
        "tool_profile": pointer.PROFILE,
        "source_select_body_sha256": constructor.sha(exact_select_body),
        "source_as_mut_ptr_body_sha256": constructor.sha(as_mut_ptr_body),
        "base_original_sha256": constructor.sha(original_base),
        "base_verified_sha256": constructor.sha(verified_base),
        "final_original_sha256": constructor.sha(original),
        "final_verified_sha256": constructor.sha(verified),
        "select_body_exact_and_unique": True,
        "verified_ghost_strip_exact": True,
        "external_constructor_call_count": 2,
        "external_as_mut_ptr_call_count": 2,
        "intrinsic_call_count": 3,
        "expected_first_obligation": (
            "two certified pointer callees translated in exact actual select; "
            "first remaining resource or intrinsic obligation recorded without acceptance"
        ),
    })
    (case / "fixture.json").write_text(
        json.dumps(fixture, indent=2, sort_keys=True) + "\n")
    return case, fixture


def function_log(log: str, name: str) -> str:
    marker = f"Verifying function '{name}'"
    start = log.find(marker)
    if start < 0:
        return ""
    end = log.find("Verifying function '", start + len(marker))
    return log[start:end if end >= 0 else None]


def obligation_kind(message: str | None, verifier_exit: int | None) -> str:
    if message is None:
        return "no_reported_error" if verifier_exit == 0 else "unreported_verifier_failure"
    if "certificate mismatch" in message or "SORT4-AS-MUT-PTR:" in message or \
            "SORT4-MAYBEUNINIT:" in message:
        return "component_certificate_or_translation"
    if "select_unpredictable" in message or "intrinsic" in message:
        return "intrinsic_select"
    if "No such function" in message:
        return "unresolved_callee"
    if re.search(r"No matching heap|Cannot prove|leaks heap|borrow|lifetime", message, re.I):
        return "resource_or_proof"
    if "unsupported" in message.lower():
        return "unsupported_operation"
    return "other_verifier_error"


def classify(case: Path, runner_result: dict, fixture: dict,
             constructor, pointer, intrinsic=None) -> dict:
    log = (case / "verifast.log").read_text(errors="replace")
    mir = (case / "compiler-mir.txt").read_text(errors="replace")
    verified = (case / "verified/lib.rs").read_bytes()
    original = (case / "original/lib.rs").read_bytes()
    errors = [line for line in log.splitlines() if ": error:" in line]
    fatal = next((line for line in log.splitlines()
                  if "Fatal error:" in line), None)
    first_error = errors[0] if errors else fatal
    first_line_match = re.search(r"verified/lib\.rs\((\d+),(\d+)",
                                 first_error or "")
    error_position = log.find(first_error) if first_error else -1
    preceding = re.findall(r"Verifying function '([^']+)'",
                           log[:error_position]) if error_position >= 0 else []
    first_function = preceding[-1] if preceding else None
    stage = runner_result.get("stage_integrity", {})
    stage_ok = set(stage) == {"exporter", "decode", "verifast", "refinement"} and \
        all(item.get("unchanged") is True for item in stage.values())
    frontend_ok = (
        runner_result.get("exporter_exit") == 0 and
        runner_result.get("decode_exit") == 0 and
        runner_result.get("refinement_exit") == 0
    )
    source_ok = (
        constructor.sha(verified) == fixture["final_verified_sha256"] and
        constructor.sha(original) == fixture["final_original_sha256"] and
        constructor.strip_ghost_annotations(verified) == original
    )
    constructor_redirects = log.count(
        "SORT4-MAYBEUNINIT: redirected checked external pointer call")
    as_mut_ptr_redirects = log.count(
        "SORT4-AS-MUT-PTR: redirected typed external call")
    constructor_body = function_log(log, constructor.CERT_FUNCTION_PATH)
    as_mut_ptr_body = function_log(log, pointer.HELPER_NAME)
    actual_body = function_log(log, "select_unpredictable")
    certificate_translation = {
        "constructor_full_typed_mir": log.count(CONSTRUCTOR_CERT) == 1,
        "as_mut_ptr_full_typed_mir": log.count(AS_MUT_PTR_CERT) == 1,
        "constructor_safe_body_translated": CONSTRUCTOR_TRANSLATED in log,
        "as_mut_ptr_safe_body_translated": AS_MUT_PTR_TRANSLATED in log,
        "constructor_redirects_two": constructor_redirects == 2,
        "as_mut_ptr_redirects_two": as_mut_ptr_redirects == 2,
        "constructor_external_mir_calls_two": mir.count(
            f'name = "{constructor.MIR_EXTERNAL_NEW.decode()}"') == 2,
        "as_mut_ptr_external_mir_calls_two": mir.count(AS_MUT_PTR_DEF_PATH) == 2,
        "select_mir_body_unique": mir.count('defPath = "select_unpredictable"') == 1,
        "checked_as_mut_ptr_mir_body_unique": mir.count(
            f'defPath = "{pointer.HELPER_NAME}"') == 1,
    }
    reached_callees = frontend_ok and stage_ok and source_ok and \
        all(certificate_translation.values())
    intrinsic_certificate = None
    intrinsic_reached = False
    if intrinsic is not None:
        intrinsic_certificate = {
            "full_actual_typed_mir_graph": log.count(INTRINSIC_ACTUAL_CERT) == 1,
            "first_pointer_call_modeled": log.count(INTRINSIC_PTR_CALL_ONE) == 1,
            "second_pointer_call_modeled": log.count(INTRINSIC_PTR_CALL_TWO) == 1,
            "wrapper_call_modeled": log.count(INTRINSIC_MU_CALL) == 1,
            "all_three_intrinsics_in_compiler_mir": mir.count(INTRINSIC_DEF_PATH) == 3,
            "no_intrinsic_certificate_mismatch":
                "SORT4-SELECT-INTRINSIC: certificate mismatch:" not in log,
        }
        intrinsic_reached = reached_callees and all(intrinsic_certificate.values())
    result = {
        "classification": "INCONCLUSIVE",
        "accepted_component": False,
        "full_select_proved": False,
        "tool_profile": intrinsic.PROFILE if intrinsic is not None else pointer.PROFILE,
        "source_integrity": source_ok,
        "stage_source_integrity": stage_ok,
        "export_decode_refinement_ok": frontend_ok,
        "certificate_translation": certificate_translation,
        "both_checked_callees_reached": reached_callees,
        "intrinsic_certificate_translation": intrinsic_certificate,
        "all_three_intrinsic_calls_modeled": intrinsic_reached,
        "actual_select_verification_entered": bool(actual_body),
        "actual_select_return_seen": "Executing return statement" in actual_body,
        "actual_select_leak_check_seen": "Leak check." in actual_body,
        "checked_constructor_verification_entered": bool(constructor_body),
        "checked_constructor_return_seen": "Executing return statement" in constructor_body,
        "checked_constructor_leak_check_seen": "Leak check." in constructor_body,
        "checked_as_mut_ptr_verification_entered": bool(as_mut_ptr_body),
        "checked_as_mut_ptr_return_seen": "Executing return statement" in as_mut_ptr_body,
        "checked_as_mut_ptr_leak_check_seen": "Leak check." in as_mut_ptr_body,
        "first_causal_obligation": {
            "verifier_error": first_error,
            "function": first_function,
            "kind": obligation_kind(first_error, runner_result.get("verifast_exit")),
            "source_line": int(first_line_match.group(1)) if first_line_match else None,
            "source_column": int(first_line_match.group(2)) if first_line_match else None,
            "error_count": len(errors),
            "fatal_certificate_or_translator_error": fatal,
            "verifier_exit": runner_result.get("verifast_exit"),
        },
        "unexpected_verifier_success": runner_result.get("verifast_exit") == 0,
        "runner_result": runner_result,
    }
    (case / "diagnostic-classification.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stock-home", type=Path, required=True)
    parser.add_argument("--tool-home", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--compiler-sysroot", required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--component-summary", type=Path, required=True)
    parser.add_argument("--constructor-summary", type=Path)
    parser.add_argument("--intrinsic-summary", type=Path)
    args = parser.parse_args()
    if os.environ.get("GITHUB_ACTIONS") != "true" or \
            os.environ.get("RUNNER_ENVIRONMENT") != "github-hosted" or \
            os.environ.get("RUNNER_OS") != "Linux":
        raise SystemExit("actual select diagnostic requires GitHub-hosted Linux Actions")
    repo_root = Path(__file__).resolve().parents[2]
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=False)
    component = json.loads(args.component_summary.read_text())
    prerequisite = component.get("accepted_component") is True and \
        component.get("classification") == "COMPONENT_ACCEPTED"
    intrinsic = None
    intrinsic_prerequisites = None
    if args.intrinsic_summary is not None:
        if args.constructor_summary is None:
            raise SystemExit("--constructor-summary is required with --intrinsic-summary")
        constructor_summary = json.loads(args.constructor_summary.read_text())
        intrinsic_summary = json.loads(args.intrinsic_summary.read_text())
        same_run = (
            args.component_summary.resolve().parents[1] == evidence.parent and
            args.constructor_summary.resolve().parents[1] == evidence.parent and
            args.intrinsic_summary.resolve().parents[1] == evidence.parent
        )
        intrinsic_prerequisites = {
            "same_run_evidence": same_run,
            "constructor_accepted": constructor_summary.get("constructor_acceptance") is True,
            "as_mut_ptr_accepted": prerequisite,
            "intrinsic_accepted": intrinsic_summary.get("accepted_component") is True and
                intrinsic_summary.get("classification") == "COMPONENT_ACCEPTED",
            "intrinsic_source_profile": intrinsic_summary.get("tool_profile") ==
                "experimental-source-linked-select-pointer-intrinsics-v1" and
                os.environ.get("SORT4_SELECT_PROFILE") ==
                "experimental-source-linked-select-pointer-intrinsics-v1",
            "intrinsic_component_prerequisites":
                isinstance(intrinsic_summary.get("prerequisites"), dict) and
                all(value is True for value in
                    intrinsic_summary["prerequisites"].values()),
        }
        prerequisite = all(intrinsic_prerequisites.values())
    if not prerequisite:
        summary = {
            "classification": "INCONCLUSIVE",
            "accepted_component": False,
            "full_select_proved": False,
            "prerequisite_component_accepted": False,
            "intrinsic_prerequisites": intrinsic_prerequisites,
            "actual_unit_run": False,
        }
        (evidence / "summary.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n")
        raise SystemExit(1)
    constructor = load_script(
        repo_root / "research/challenge-8/check-maybeuninit-new-pointer.py",
        "sort4_constructor_matrix_for_actual")
    pointer = load_script(
        repo_root / "research/challenge-8/check-select-pointer.py",
        "sort4_as_mut_ptr_matrix_for_actual")
    if args.intrinsic_summary is not None:
        intrinsic = load_script(
            repo_root / "research/challenge-8/check-select-pointer-intrinsics.py",
            "sort4_select_intrinsic_matrix_for_actual")
        intrinsic_source = intrinsic.source_certificate(repo_root, constructor)
        (evidence / "intrinsic-source-certificate.json").write_text(
            json.dumps(intrinsic_source, indent=2, sort_keys=True) + "\n")
    case, fixture = prepare_case(evidence, repo_root, constructor, pointer)
    if intrinsic is not None:
        fixture["tool_profile"] = intrinsic.PROFILE
        (case / "fixture.json").write_text(
            json.dumps(fixture, indent=2, sort_keys=True) + "\n")
    previous = os.environ.get("SORT4_SELECT_INTRINSIC_REPO_ROOT")
    if intrinsic is None:
        os.environ.pop("SORT4_SELECT_INTRINSIC_REPO_ROOT", None)
    else:
        os.environ["SORT4_SELECT_INTRINSIC_REPO_ROOT"] = str(repo_root)
    try:
        runner_result = constructor.run_case(
            case, args.schema, args.tool_home, args.compiler_sysroot, repo_root,
            "actual_select_after_constructor_and_as_mut_ptr", "diagnostic",
            certificate_mode=True)
    finally:
        if previous is None:
            os.environ.pop("SORT4_SELECT_INTRINSIC_REPO_ROOT", None)
        else:
            os.environ["SORT4_SELECT_INTRINSIC_REPO_ROOT"] = previous
    diagnosis = classify(case, runner_result, fixture, constructor, pointer, intrinsic)
    summary = {
        "classification": "INCONCLUSIVE",
        "accepted_component": False,
        "full_select_proved": False,
        "prerequisite_component_accepted": True,
        "intrinsic_prerequisites": intrinsic_prerequisites,
        "intrinsic_mode": intrinsic is not None,
        "actual_unit_run": True,
        "diagnosis": diagnosis,
        "case": str(case),
    }
    (evidence / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "classification": summary["classification"],
        "both_checked_callees_reached": diagnosis["both_checked_callees_reached"],
        "all_three_intrinsic_calls_modeled": diagnosis["all_three_intrinsic_calls_modeled"],
        "first_causal_obligation": diagnosis["first_causal_obligation"],
        "evidence": str(evidence),
    }))
    if not diagnosis["both_checked_callees_reached"] or \
            (intrinsic is not None and not diagnosis["all_three_intrinsic_calls_modeled"]):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
