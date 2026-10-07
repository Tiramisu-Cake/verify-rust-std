#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted first-obligation diagnostic for the exact pointer select body.

The two checked callees are source-linked components. This experiment does not
accept a select_unpredictable proof, even if the verifier unexpectedly succeeds.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
from pathlib import Path


AS_MUT_PTR_DEF_PATH = 'name = "std::mem::MaybeUninit::<T>::as_mut_ptr"'
INTRINSIC_DEF_PATH = 'name = "std::intrinsics::select_unpredictable"'
INTRINSIC_ACTUAL_CERT = "SORT4-SELECT-INTRINSIC: full typed actual MIR graph accepted"
INTRINSIC_PTR_CALL_ONE = "SORT4-SELECT-INTRINSIC: modeled typed pointer call 1"
INTRINSIC_PTR_CALL_TWO = "SORT4-SELECT-INTRINSIC: modeled typed pointer call 2"
INTRINSIC_MU_CALL = "SORT4-SELECT-INTRINSIC: modeled typed wrapper call 1"
DROP_CERT = "SORT4-POINTER-DROP: full typed method MIR graph accepted"
DROP_GLUE = "SORT4-POINTER-DROP: modeled typed pointer drop 1"
DROP_REDIRECT = "SORT4-POINTER-DROP: redirected typed external method 1"
PROJECTION_OPEN_GHOSTS = (
    b"    //@ std::mem::open_MaybeUninit::<*Element>(true_ptr as *std::mem::MaybeUninit<*Element>);\n"
    b"    //@ std::mem::open_MaybeUninit::<*Element>(false_ptr as *std::mem::MaybeUninit<*Element>);\n"
)
PROJECTION_SPLIT_GHOST = b"        //@ if (condition) { } else { }\n"
PROJECTION_CLOSE_GHOSTS = (
    b"        //@ std::mem::close_MaybeUninit::<*Element>(true_ptr as *std::mem::MaybeUninit<*Element>);\n"
    b"        //@ std::mem::close_MaybeUninit::<*Element>(false_ptr as *std::mem::MaybeUninit<*Element>);\n"
)
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


def imported_prerequisite_evidence(path: Path, component: Path,
                                   constructor: Path, intrinsic: Path,
                                   drop: Path, evidence: Path) -> bool:
    """Bind old summaries to a pinned prior proof run, not this actual run."""
    data = json.loads(path.read_text())
    root = path.resolve().parent
    expected = {
        "constructor-regressions/summary.json": constructor,
        "matrix/summary.json": component,
        "intrinsic-matrix/summary.json": intrinsic,
    }
    hashes = data.get("summary_sha256", {})
    if (set(hashes) != set(expected) or
            any(source.resolve() != (root / rel).resolve() or
                hashlib.sha256(source.read_bytes()).hexdigest() != hashes[rel]
                for rel, source in expected.items())):
        return False
    profile = os.environ.get("SORT4_SELECT_PROFILE")
    source_profile = json.loads(drop.read_text()).get("source_profile", {})
    required = ("source_run_id", "source_sha", "profile", "patch_sha256",
                "archive_sha256", "effective_tool_hashes", "std_source_hashes")
    pinned_v1 = (data.get("source_run_id") == 37637630477 and
            data.get("source_sha") ==
                "de7ed9de861eea7346301f6807e242862a68c0ab" and
            data.get("profile") == profile ==
                "experimental-source-linked-select-pointer-drop-v1" and
            data.get("patch_sha256") ==
                "cd660fe9f470293cc16712a4a71714c8f5f6e802608cedb5b486c3d8a1d27413" and
            data.get("archive_sha256") ==
                "34a6fba71d964a5ed74298471da4176102fdf3bc747178cadd9a69894d91b232")
    pinned_v3 = (data.get("source_run_id") == 37651717720 and
            data.get("source_sha") ==
                "dfc1f1d740689de8f427ac549da558d64a4318eb" and
            data.get("profile") == profile ==
                "experimental-source-linked-select-pointer-drop-v3" and
            data.get("patch_sha256") ==
                "94ffc64ce15811ac0de62e55489fb1e61242883b7258aa22969bbefa9ec184e8" and
            data.get("archive_sha256") ==
                "f2c9a1dcda5785af850a51e103bc0c7d07df38c39ed9809afb33211bde997fb0" and
            data.get("source_artifact_id") == 11497076310)
    return (all(data.get(field) == source_profile.get(field) for field in required) and
            (pinned_v1 or pinned_v3) and
            drop.resolve().parents[1] == evidence.parent and
            data.get("proof_and_component_evidence_origin") ==
                "pinned original run; not current-run proofs")


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
             constructor, pointer, intrinsic=None, drop=None,
             accepted_drop_matrix: bool = False) -> dict:
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
    drop_certificate = None
    drop_reached = False
    if drop is not None:
        drop_body = function_log(log, drop.HELPER)
        lemma_body = function_log(log, "std::ptr::pointer_drop_glue_identity")
        drop_certificate = {
            "full_method_typed_mir_graph": log.count(DROP_CERT) == 1,
            "free_glue_exactly_once": log.count(DROP_GLUE) == 1,
            "actual_method_redirect_once": log.count(DROP_REDIRECT) == 1,
            "method_mir_body_unique": mir.count(f'defPath = "{drop.HELPER}"') == 1,
            "actual_method_runtime_call_retained":
                mir.count('name = "std::ptr::mut_ptr::<impl *mut T>::drop_in_place"') >= 1,
            "checked_method_return_and_leak_if_entered":
                not drop_body or ("Executing return statement" in drop_body and
                                  "Leak check." in drop_body),
            "accepted_same_profile_drop_matrix": accepted_drop_matrix,
            "no_drop_certificate_mismatch":
                "SORT4-POINTER-DROP: certificate mismatch:" not in log,
        }
        drop_reached = intrinsic_reached and all(drop_certificate.values())
    result = {
        "classification": "INCONCLUSIVE",
        "accepted_component": False,
        "full_select_proved": False,
        "tool_profile": drop.PROFILE if drop is not None else
            intrinsic.PROFILE if intrinsic is not None else pointer.PROFILE,
        "source_integrity": source_ok,
        "stage_source_integrity": stage_ok,
        "export_decode_refinement_ok": frontend_ok,
        "certificate_translation": certificate_translation,
        "both_checked_callees_reached": reached_callees,
        "intrinsic_certificate_translation": intrinsic_certificate,
        "all_three_intrinsic_calls_modeled": intrinsic_reached,
        "drop_certificate_translation": drop_certificate,
        "actual_drop_method_body_entered": bool(drop_body) if drop is not None else None,
        "actual_drop_identity_lemma_body_entered": bool(lemma_body) if drop is not None else None,
        "checked_drop_method_and_actual_redirect_reached": drop_reached,
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
    parser.add_argument("--drop-summary", type=Path)
    parser.add_argument("--imported-prerequisites", type=Path)
    parser.add_argument("--imported-v3-coordinate-controls", type=Path)
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
    drop = None
    accepted_drop_matrix = False
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
        imported = args.imported_prerequisites is not None and \
            args.drop_summary is not None and imported_prerequisite_evidence(
                args.imported_prerequisites, args.component_summary,
                args.constructor_summary, args.intrinsic_summary,
                args.drop_summary, evidence)
        if args.imported_v3_coordinate_controls is not None:
            require(imported and args.imported_prerequisites is not None and
                    os.environ.get("SORT4_SELECT_PROFILE") ==
                        "experimental-source-linked-select-pointer-drop-v3",
                    "v3 coordinate import requires pinned same-profile prerequisites")
            imported_manifest = json.loads(args.imported_prerequisites.read_text())
            coordinate_file = args.imported_v3_coordinate_controls
            require(coordinate_file.resolve().parent ==
                    args.imported_prerequisites.resolve().parent and
                    hashlib.sha256(coordinate_file.read_bytes()).hexdigest() ==
                        imported_manifest.get("coordinate_controls_sha256"),
                    "v3 coordinate controls do not match pinned import")
        intrinsic_prerequisites = {
            "same_run_or_pinned_import_evidence": same_run or imported,
            "pinned_original_proof_import_if_requested":
                args.imported_prerequisites is None or imported,
            "constructor_accepted": constructor_summary.get("constructor_acceptance") is True,
            "as_mut_ptr_accepted": prerequisite,
            "intrinsic_accepted": intrinsic_summary.get("accepted_component") is True and
                intrinsic_summary.get("classification") == "COMPONENT_ACCEPTED",
            "intrinsic_source_profile": intrinsic_summary.get("tool_profile") ==
                os.environ.get("SORT4_SELECT_PROFILE") and
                os.environ.get("SORT4_SELECT_PROFILE") in {
                    "experimental-source-linked-select-pointer-intrinsics-v1",
                    "experimental-source-linked-select-pointer-intrinsics-v2",
                    "experimental-source-linked-select-pointer-drop-v1",
                    "experimental-source-linked-select-pointer-drop-v2",
                    "experimental-source-linked-select-pointer-drop-v3",
                },
            "intrinsic_component_prerequisites":
                isinstance(intrinsic_summary.get("prerequisites"), dict) and
                all(value is True for value in
                    intrinsic_summary["prerequisites"].values()),
        }
        prerequisite = all(intrinsic_prerequisites.values())
    if args.drop_summary is not None:
        if args.intrinsic_summary is None:
            raise SystemExit("--intrinsic-summary required with --drop-summary")
        drop_summary = json.loads(args.drop_summary.read_text())
        drop_pre = {
            "same_run_evidence": args.drop_summary.resolve().parents[1] == evidence.parent,
            "drop_accepted": drop_summary.get("accepted_component") is True and
                drop_summary.get("classification") == "COMPONENT_ACCEPTED",
            "drop_same_profile": drop_summary.get("tool_profile") ==
                os.environ.get("SORT4_SELECT_PROFILE"),
        }
        prerequisite = prerequisite and all(drop_pre.values())
        accepted_drop_matrix = all(drop_pre.values())
        intrinsic_prerequisites["drop_component"] = drop_pre
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
    if args.drop_summary is not None:
        drop = load_script(
            repo_root / "research/challenge-8/check-pointer-drop.py",
            "sort4_pointer_drop_matrix_for_actual")
        diagnostic = load_script(
            repo_root / "research/challenge-8/prepare-pointer-drop-diagnostic.py",
            "sort4_pointer_drop_source_for_actual")
        drop_body, drop_source = diagnostic.source_certificate(repo_root, constructor)
        (evidence / "drop-source-certificate.json").write_text(
            json.dumps(drop_source, indent=2, sort_keys=True) + "\n")
    case, fixture = prepare_case(evidence, repo_root, constructor, pointer)
    if drop is not None:
        method = drop.helper_source(drop_body, constructor)
        original_method = constructor.strip_ghost_annotations(method)
        original = (case / "original/lib.rs").read_bytes() + b"\n" + original_method
        verified = (case / "verified/lib.rs").read_bytes() + b"\n" + method
        require(constructor.strip_ghost_annotations(verified) == original,
                "actual plus checked drop method changed runtime source")
        (case / "original/lib.rs").write_bytes(original)
        (case / "verified/lib.rs").write_bytes(verified)
        fixture["final_original_sha256"] = constructor.sha(original)
        fixture["final_verified_sha256"] = constructor.sha(verified)
        fixture["drop_method_source_sha256"] = constructor.sha(drop_body)
        fixture["tool_profile"] = drop.PROFILE
        (case / "fixture.json").write_text(
            json.dumps(fixture, indent=2, sort_keys=True) + "\n")
    if intrinsic is not None and drop is None:
        fixture["tool_profile"] = intrinsic.PROFILE
        (case / "fixture.json").write_text(
            json.dumps(fixture, indent=2, sort_keys=True) + "\n")
    cases = [(case, fixture)]
    if drop is not None:
        projected = evidence / "actual_select_pointer_drop_projection"
        shutil.copytree(case, projected)
        verified = (projected / "verified/lib.rs").read_bytes()
        insertions = (
            (b"    let false_ptr = false_val.as_mut_ptr();\n", PROJECTION_OPEN_GHOSTS),
            (b"        let guard = DropOnPanic { inner: guard };\n",
             PROJECTION_SPLIT_GHOST),
            (b"        drop.drop_in_place();\n", PROJECTION_CLOSE_GHOSTS),
        )
        for anchor, ghosts in insertions:
            require(verified.count(anchor) == 1, "actual projection anchor changed")
            verified = verified.replace(anchor, anchor + ghosts, 1)
        original = (projected / "original/lib.rs").read_bytes()
        require(constructor.strip_ghost_annotations(verified) == original,
                "projection changed actual runtime source")
        (projected / "verified/lib.rs").write_bytes(verified)
        projected_fixture = {**fixture, "variant": "actual_select_pointer_drop_projection",
                             "projection_ghosts_exact": True,
                             "final_verified_sha256": constructor.sha(verified)}
        (projected / "fixture.json").write_text(
            json.dumps(projected_fixture, indent=2, sort_keys=True) + "\n")
        cases.append((projected, projected_fixture))
    previous = os.environ.get("SORT4_SELECT_INTRINSIC_REPO_ROOT")
    previous_drop = os.environ.get("SORT4_POINTER_DROP_REPO_ROOT")
    if intrinsic is None:
        os.environ.pop("SORT4_SELECT_INTRINSIC_REPO_ROOT", None)
    else:
        os.environ["SORT4_SELECT_INTRINSIC_REPO_ROOT"] = str(repo_root)
    if drop is not None:
        os.environ["SORT4_POINTER_DROP_REPO_ROOT"] = str(repo_root)
    diagnoses = []
    ghost_controls = None
    try:
        if drop is not None and args.imported_v3_coordinate_controls is not None:
            ghost_module = load_script(
                repo_root / "research/challenge-8/check-pointer-drop-actual-ghosts.py",
                "sort4_actual_v3_completion_controls")
            imported_coordinates = json.loads(
                args.imported_v3_coordinate_controls.read_text())["cases"][:2]
            ghost_controls = ghost_module.run_controls(
                cases[1][0], args, repo_root, constructor,
                evidence / "actual-ghost-admissions", imported_coordinates)
            if not ghost_controls["accepted_controls"]:
                (evidence / "summary.json").write_text(json.dumps({
                    "classification": "INCONCLUSIVE", "accepted_component": False,
                    "full_select_proved": False, "prerequisite_component_accepted": True,
                    "actual_unit_run": False,
                    "ghost_coordinate_admission_controls": ghost_controls,
                    "projected_case_run": False}, indent=2, sort_keys=True) + "\n")
                raise SystemExit(1)
        baseline, baseline_fixture = cases[0]
        baseline_runner = constructor.run_case(
            baseline, args.schema, args.tool_home, args.compiler_sysroot,
            repo_root, baseline.name, "diagnostic", certificate_mode=True)
        diagnoses.append(classify(baseline, baseline_runner, baseline_fixture,
                                  constructor, pointer, intrinsic, drop,
                                  accepted_drop_matrix))
        baseline_reached = (diagnoses[0]["both_checked_callees_reached"] and
            (intrinsic is None or diagnoses[0]["all_three_intrinsic_calls_modeled"]) and
            (drop is None or
             diagnoses[0]["checked_drop_method_and_actual_redirect_reached"]))
        if drop is not None and ghost_controls is None:
            ghost_module = load_script(
                repo_root / "research/challenge-8/check-pointer-drop-actual-ghosts.py",
                "sort4_actual_ghost_admission_controls")
            imported_coordinates = None
            if args.imported_v3_coordinate_controls is not None:
                imported_coordinates = json.loads(
                    args.imported_v3_coordinate_controls.read_text())["cases"][:2]
            ghost_controls = ghost_module.run_controls(
                cases[1][0], args, repo_root, constructor,
                evidence / "actual-ghost-admissions", imported_coordinates)
        if len(cases) > 1 and baseline_reached and ghost_controls["accepted_controls"]:
            projected, projected_fixture = cases[1]
            projected_runner = constructor.run_case(
                projected, args.schema, args.tool_home, args.compiler_sysroot,
                repo_root, projected.name, "diagnostic", certificate_mode=True)
            diagnoses.append(classify(projected, projected_runner,
                                      projected_fixture, constructor, pointer,
                                      intrinsic, drop, accepted_drop_matrix))
    finally:
        if previous is None:
            os.environ.pop("SORT4_SELECT_INTRINSIC_REPO_ROOT", None)
        else:
            os.environ["SORT4_SELECT_INTRINSIC_REPO_ROOT"] = previous
        if previous_drop is None:
            os.environ.pop("SORT4_POINTER_DROP_REPO_ROOT", None)
        else:
            os.environ["SORT4_POINTER_DROP_REPO_ROOT"] = previous_drop
    diagnosis = diagnoses[-1]
    summary = {
        "classification": "INCONCLUSIVE",
        "accepted_component": False,
        "full_select_proved": False,
        "prerequisite_component_accepted": True,
        "intrinsic_prerequisites": intrinsic_prerequisites,
        "intrinsic_mode": intrinsic is not None,
        "drop_mode": drop is not None,
        "actual_unit_run": True,
        "baseline_component_calls_reached": baseline_reached,
        "ghost_coordinate_admission_controls": ghost_controls,
        "projected_case_run": len(diagnoses) == len(cases),
        "cases_not_run": [str(p) for p, _ in cases[len(diagnoses):]],
        "diagnosis": diagnosis,
        "diagnoses": [{"case": str(p), "diagnosis": d}
                      for (p, _), d in zip(cases, diagnoses)],
        "case": str(case),
    }
    (evidence / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "classification": summary["classification"],
        "both_checked_callees_reached": diagnosis["both_checked_callees_reached"],
        "all_three_intrinsic_calls_modeled": diagnosis["all_three_intrinsic_calls_modeled"],
        "checked_drop_method_and_actual_redirect_reached":
            diagnosis["checked_drop_method_and_actual_redirect_reached"],
        "first_causal_obligation": diagnosis["first_causal_obligation"],
        "ghost_coordinate_admission_controls_accepted":
            ghost_controls["accepted_controls"] if ghost_controls is not None else None,
        "evidence": str(evidence),
    }))
    if (drop is not None and (ghost_controls is None or
            not ghost_controls["accepted_controls"] or len(diagnoses) != len(cases))) or \
       any(not d["both_checked_callees_reached"] or
           (intrinsic is not None and not d["all_three_intrinsic_calls_modeled"]) or
           (drop is not None and not d["checked_drop_method_and_actual_redirect_reached"])
           for d in diagnoses):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
