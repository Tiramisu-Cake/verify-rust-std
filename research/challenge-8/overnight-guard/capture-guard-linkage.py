#!/usr/bin/env python3
"""Hosted diagnostic: checked generic method beside source-exact SAFE guard Drop.

This is a local-DefPath source/MIR capture and later H2 frontend gate probe.
It never asserts that the actual nested Drop or outer helper is proved.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path


HERE = Path(__file__).resolve().parent


def load(name: str, path: Path):
    import importlib.util
    import sys
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"missing H2 capture module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


H2A = load("h2_generic_method_link_capture", HERE / "capture-generic-pointer-drop.py")
H2B = load("h2_guard_owner_link_capture", HERE / "capture-guard-owner.py")
LINK = H2A.LINK
REPO = H2A.REPO
VARIANTS = ("positive", "method_operand", "guard_operand",
            "owner_predicate", "field_visibility", "missing_cell",
            "wrong_target", "duplicate_owner_post")
METHOD_SIGNATURE = b"pub unsafe fn sort4_checked_generic_drop<T>(slot: *mut T)"
PROBE_SIGNATURE = b"pub unsafe fn sort4_generic_drop_probe<T>"
GUARD_SIGNATURE = b"struct DropOnPanic<T>"
WITNESS_SIGNATURE = b"pub unsafe fn guard_owner_u32_witness("


def require(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)


def checked_method(body: bytes) -> bytes:
    _, verified = H2A.source_pair(body, "positive")
    require(verified.count(METHOD_SIGNATURE) == 1 and
            verified.count(PROBE_SIGNATURE) == 1,
            "H2a source pair changed method/probe boundaries")
    begin, end = verified.index(METHOD_SIGNATURE), verified.index(PROBE_SIGNATURE)
    require(begin < end, "H2a method order changed")
    method = verified[begin:end]
    require(method.count(body) == 1 and method.count(PROBE_SIGNATURE) == 0,
            "H2a certified body escaped the local method")
    return method


def source_pair(method: bytes, struct_body: bytes, drop_body: bytes,
                variant: str, template_active: bool = False) -> tuple[bytes, bytes]:
    require(variant in VARIANTS, "unknown H2 linkage variant")
    require(template_active or variant in VARIANTS[:3],
            "H2b source controls require the separate template overlay")
    owner_variant = (variant if variant in ("missing_cell", "wrong_target")
                     else "owner_positive")
    original, verified = H2B.guard_source(struct_body, drop_body,
                                          owner_variant)
    if not template_active:
        # Keep the original H2a isolation unchanged: the concrete witness is
        # an independent H2b obligation, never a prerequisite for H2a.
        start = verified.index(WITNESS_SIGNATURE)
        end = verified.index(b"impl<T> Drop for DropOnPanic<T>", start)
        require(start < end and verified.count(WITNESS_SIGNATURE) == 1,
                "H2b witness boundary changed")
        verified = verified[:start] + verified[end:]
    require(verified.startswith(b"#![allow(dead_code)]\n\n") and
            verified.count(GUARD_SIGNATURE) == 1 and
            verified.count(METHOD_SIGNATURE) == 0,
            "guard fixture prefix/identity changed")
    if variant == "method_operand":
        marker = b"std::ptr::drop_in_place(slot)"
        require(method.count(marker) == 1, "method operand mutant not unique")
        method = method.replace(marker,
                                b"std::ptr::drop_in_place(slot.wrapping_add(0))", 1)
    verified = verified.replace(
        b"#![allow(dead_code)]\n\n",
        b"#![allow(dead_code)]\n\n" + method + b"\n", 1)
    if template_active:
        _, ordinary = H2B.ordinary_source()
        preamble = b"#![allow(dead_code)]\n\n"
        require(ordinary.startswith(preamble) and
                ordinary.count(b"impl Drop for OrdinaryDrop") == 1,
                "ordinary Drop same-unit control changed")
        verified += b"\n" + ordinary[len(preamble):]
    if variant == "guard_operand":
        marker = H2B.ACTUAL_DROP_CALL
        require(verified.count(marker) == 1, "guard operand mutant not unique")
        verified = verified.replace(
            marker, b"unsafe { core::ptr::null_mut::<T>().drop_in_place() }", 1)
    if variant == "owner_predicate":
        marker = b"*g.inner |-> ?payload &*& <T>.own(t, payload);"
        require(verified.count(marker) == 1,
                "nominal owner source mutant is not unique")
        verified = verified.replace(
            marker, b"*g.inner |-> ?payload &*& <T>.own(t, payload) &*& true;", 1)
    if variant == "field_visibility":
        marker = b"inner: *mut T"
        require(verified.count(marker) == 1,
                "private guard field source mutant is not unique")
        verified = verified.replace(marker, b"pub inner: *mut T", 1)
    if variant == "duplicate_owner_post":
        marker = (b"ens thread_token(t) &*& type_interp::<T>() &*& "
                  b"<DropOnPanic<T>>.own(t, result);")
        require(verified.count(marker) == 1,
                "owner-duplication post control is not unique")
        verified = verified.replace(
            marker, marker[:-1] + b" &*& *slot |-> ?duplicate;", 1)
    original = H2A.CONSTRUCTOR.strip_ghost_annotations(verified)
    require(H2A.CONSTRUCTOR.strip_ghost_annotations(verified) == original and
            original.count(METHOD_SIGNATURE) == 1 and
            original.count(GUARD_SIGNATURE) == 1 and
            (original.count(WITNESS_SIGNATURE) ==
             (0 if variant in ("missing_cell", "wrong_target") else 1)
             if template_active else
             original.count(WITNESS_SIGNATURE) == 0) and
            (original.count(b"impl Drop for OrdinaryDrop") == 1 if template_active
             else original.count(b"impl Drop for OrdinaryDrop") == 0) and
            (original.count(drop_body) == 1 if variant != "guard_operand" else
             original.count(drop_body) == 0),
            "H2 linkage fixture runtime identity changed")
    return original, verified


def classify(case: Path, variant: str, stages: dict,
             template_active: bool = False) -> dict:
    complete = all(stages.get(k, {}).get("exit") == 0 for k in (
        "normal-export", "normal-decode", "readonly-export", "readonly-decode",
        "refinement"))
    intact = all(s.get("source_unchanged") is True for s in stages.values())
    log = (case / "full-verification.log").read_text(errors="replace") if \
        (case / "full-verification.log").exists() else ""
    errors = LINK.ERR.findall(log)
    fatal = [line for line in log.splitlines() if line.startswith("Fatal error:")]
    gate_line = "SORT4-GENERIC-GUARD: source/MIR local link accepted"
    method_start = log.find("Verifying function 'sort4_checked_generic_drop'")
    method_end = log.find("Verifying function '", method_start + 1) if method_start >= 0 else -1
    method_log = log[method_start:method_end if method_end >= 0 else None] if \
        method_start >= 0 else ""
    guard_start = log.find("Verifying function '<DropOnPanic<T> as std::ops::Drop>::drop'")
    guard_end = log.find("Verifying function '", guard_start + 1) if guard_start >= 0 else -1
    guard_log = log[guard_start:guard_end if guard_end >= 0 else None] if \
        guard_start >= 0 else ""
    def segment(name: str) -> str:
        begin = log.find("Verifying function '" + name + "'")
        ending = log.find("Verifying function '", begin + 1) if begin >= 0 else -1
        return log[begin:ending if ending >= 0 else None] if begin >= 0 else ""

    ctor_log = segment("guard_owner_from_initialized_slot")
    witness_log = segment("guard_owner_u32_witness")
    ordinary_log = segment("<OrdinaryDrop as std::ops::Drop>::drop")
    def two_outcomes(segment_log: str) -> bool:
        # A single observed return is insufficient: SAFE Drop has normal and
        # unwind continuations, both of which must close and leak-check.
        returns = [line for line in segment_log.splitlines()
                   if "Executing return statement" in line]
        leaks = [line for line in segment_log.splitlines()
                 if "Leak check." in line and ": note:" not in line]
        return len(returns) == len(leaks) == 2 and all(
            segment_log.find(returns[index]) < segment_log.find(leaks[index])
            for index in range(2))
    result = {
        "variant": variant, "classification": "H2_LINKAGE_DIAGNOSTIC_ONLY",
        "component_accepted": False, "actual_nested_drop_proved": False,
        "frontend_refinement": complete, "source_integrity": intact,
        "full_verifier_exit": stages.get("full-verification", {}).get("exit"),
        "first_error": errors[0] if errors else None, "fatal": fatal,
        "gate_accepted": gate_line in log,
        "local_generic_method_entered": bool(method_log),
        "local_generic_method_return_and_leak":
            "Executing return statement" in method_log and
            "Leak check." in method_log,
        "local_guard_drop_entered": bool(guard_log),
        "local_guard_drop_return_and_leak":
            "Executing return statement" in guard_log and
            "Leak check." in guard_log,
        "method_normal_and_unwind_return_leak": two_outcomes(method_log),
        "guard_normal_and_unwind_return_leak": two_outcomes(guard_log),
        "constructor_return_leak": "Executing return statement" in ctor_log and
            "Leak check." in ctor_log,
        "concrete_u32_witness_return_leak":
            "Executing return statement" in witness_log and
            "Leak check." in witness_log,
        "ordinary_drop_return_leak":
            "Executing return statement" in ordinary_log and
            "Leak check." in ordinary_log,
        "template_overlay_requested": template_active,
        "owner_constructor_entered": bool(ctor_log),
        "stages": stages,
    }
    expected_gate_reason = {
        "method_operand": "local method exact contract/body",
        "guard_operand": "local guard exact source/ghost owner",
        "owner_predicate": "fixture source marker: /*@",
        "field_visibility": "local guard exact source/ghost owner",
    }.get(variant)
    if complete and intact and expected_gate_reason is not None and \
            result["full_verifier_exit"] == 2 and not errors and \
            len(fatal) == 1 and \
            "SORT4-GENERIC-GUARD: certificate mismatch: " + expected_gate_reason in fatal[0] and \
            not result["gate_accepted"] and \
            not result["local_generic_method_entered"] and \
            not result["local_guard_drop_entered"]:
        result["classification"] = "EXACT_SOURCE_GATE_REJECTION_DIAGNOSTIC"
    elif complete and intact and template_active and \
            variant in ("missing_cell", "wrong_target") and \
            result["full_verifier_exit"] == 1 and len(errors) == 1 and \
            result["gate_accepted"] and not fatal and \
            result["method_normal_and_unwind_return_leak"] and \
            result["owner_constructor_entered"] and \
            not result["local_guard_drop_entered"] and \
            errors[0][0] == "verified/lib.rs" and \
            errors[0][3].startswith("No matching heap chunks: points_to<T>(") and \
            b"*g.inner |-> ?payload" in \
                (case / "verified/lib.rs").read_bytes().splitlines()[int(errors[0][1]) - 1]:
        result["classification"] = "H2B_OWNER_CONSTRUCTION_NEGATIVE"
    elif complete and intact and template_active and \
            variant == "duplicate_owner_post" and \
            result["full_verifier_exit"] == 1 and len(errors) == 1 and \
            result["gate_accepted"] and not fatal and \
            result["method_normal_and_unwind_return_leak"] and \
            result["owner_constructor_entered"] and \
            not result["local_guard_drop_entered"] and \
            errors[0][0] == "verified/lib.rs" and \
            "No matching heap chunks: points_to" in errors[0][3] and \
            b"*slot |-> ?duplicate" in \
                (case / "verified/lib.rs").read_bytes().splitlines()[int(errors[0][1]) - 1]:
        result["classification"] = "H2B_NO_DUPLICATE_CELL_NEGATIVE"
    elif complete and intact and variant == "positive" and template_active and \
            result["full_verifier_exit"] == 0 and not errors and not fatal and \
            result["gate_accepted"] and \
            result["method_normal_and_unwind_return_leak"] and \
            result["guard_normal_and_unwind_return_leak"] and \
            result["constructor_return_leak"] and \
            result["concrete_u32_witness_return_leak"] and \
            result["ordinary_drop_return_leak"]:
        result["classification"] = "H2B_LOCAL_NOMINAL_DROP_CANDIDATE_PROVED"
    elif complete and intact and variant == "positive" and \
            result["gate_accepted"] and \
            result["local_generic_method_return_and_leak"] and \
            result["local_guard_drop_entered"] and not fatal:
        result["classification"] = "LOCAL_METHOD_LINKED_GUARD_PROOF_PENDING"
    LINK.write_json(case / "classification.json", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool-home", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--compiler-sysroot", required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--deadline-epoch", type=int, required=True)
    parser.add_argument("--variants", nargs="+", choices=VARIANTS,
                        default=["positive"])
    parser.add_argument("--guard-root", type=Path,
                        help="activate an exact H2 frontend gate on hosted runner")
    parser.add_argument("--template-root", type=Path,
                        help="activate separate nominal SAFE Drop post candidate")
    args = parser.parse_args()
    require(os.environ.get("GITHUB_ACTIONS") == "true" and
            os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted" and
            os.environ.get("RUNNER_OS") == "Linux", "GitHub-hosted Linux required")
    evidence = args.evidence.resolve()
    require(not evidence.exists(), f"refusing overwrite: {evidence}")
    evidence.mkdir(parents=True)
    method_body, method_cert = H2A.source_certificate()
    struct_body, drop_body, guard_cert = H2B.source_certificate()
    method = checked_method(method_body)
    cert = {"generic_method": method_cert, "guard": guard_cert,
            "local_method_sha256": LINK.sha(method),
            "actual_nested_def_path_proved": False}
    LINK.write_json(evidence / "source-certificate.json", cert)
    if args.guard_root is not None:
        require(args.guard_root.resolve() == REPO,
                "H2 frontend root must be exact repository root")
        os.environ["SORT4_GUARD_REPO_ROOT"] = str(REPO)
    else:
        os.environ.pop("SORT4_GUARD_REPO_ROOT", None)
    if args.template_root is not None:
        require(args.guard_root is not None and
                args.template_root.resolve() == REPO,
                "template requires the same source-certified guard root")
        os.environ["SORT4_GUARD_TEMPLATE_REPO_ROOT"] = str(REPO)
    else:
        os.environ.pop("SORT4_GUARD_TEMPLATE_REPO_ROOT", None)
    results = []
    for variant in args.variants:
        case = evidence / variant
        case.mkdir()
        (case / "original").mkdir()
        (case / "verified").mkdir()
        original, verified = source_pair(method, struct_body, drop_body,
                                         variant, args.template_root is not None)
        (case / "original/lib.rs").write_bytes(original)
        (case / "verified/lib.rs").write_bytes(verified)
        LINK.write_json(case / "fixture.json", {
            "variant": variant, "certificate": cert,
            "original_sha256": LINK.sha(original),
            "verified_sha256": LINK.sha(verified),
            "actual_generic_drop_runtime_body_exact": variant != "guard_operand",
            "actual_guard_adt_exact": variant != "field_visibility",
            "local_generic_method_runtime_body_exact": variant != "method_operand",
            "template_overlay_requested": args.template_root is not None,
            "same_unit_ordinary_drop_control": args.template_root is not None,
            "same_unit_concrete_owner_witness": args.template_root is not None,
            "actual_nested_def_path_proved": False,
        })
        results.append(classify(case, variant, H2A.run_case(case, args),
                                args.template_root is not None))
    LINK.write_json(evidence / "summary.json", {
        "classification": "H2_GENERIC_GUARD_LINKAGE_DIAGNOSTIC_ONLY",
        "component_accepted": False,
        "actual_nested_drop_proved": False,
        "source_certificate": cert,
        "results": results,
    })


if __name__ == "__main__":
    main()
