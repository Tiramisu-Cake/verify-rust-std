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
VARIANTS = ("positive", "method_operand", "guard_operand")
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
                variant: str) -> tuple[bytes, bytes]:
    require(variant in VARIANTS, "unknown H2 linkage variant")
    original, verified = H2B.guard_source(struct_body, drop_body,
                                          "owner_positive")
    # The concrete scalar witness is a separate H2b admission case.  This
    # fixture isolates the generic callee and SAFE Drop body so a witness
    # parser failure cannot mask their first causal proof obligation.
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
    if variant == "guard_operand":
        marker = H2B.ACTUAL_DROP_CALL
        require(verified.count(marker) == 1, "guard operand mutant not unique")
        verified = verified.replace(
            marker, b"unsafe { core::ptr::null_mut::<T>().drop_in_place() }", 1)
    original = H2A.CONSTRUCTOR.strip_ghost_annotations(verified)
    require(H2A.CONSTRUCTOR.strip_ghost_annotations(verified) == original and
            original.count(METHOD_SIGNATURE) == 1 and
            original.count(GUARD_SIGNATURE) == 1 and
            (original.count(drop_body) == 1 if variant != "guard_operand" else
             original.count(drop_body) == 0),
            "H2 linkage fixture runtime identity changed")
    return original, verified


def classify(case: Path, variant: str, stages: dict) -> dict:
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
        "stages": stages,
    }
    expected_gate_reason = {
        "method_operand": "local method exact contract/body",
        "guard_operand": "local guard exact source/ghost owner",
    }.get(variant)
    if complete and intact and expected_gate_reason is not None and \
            result["full_verifier_exit"] == 2 and not errors and \
            len(fatal) == 1 and \
            "SORT4-GENERIC-GUARD: certificate mismatch: " + expected_gate_reason in fatal[0] and \
            not result["gate_accepted"] and \
            not result["local_generic_method_entered"] and \
            not result["local_guard_drop_entered"]:
        result["classification"] = "EXACT_SOURCE_GATE_REJECTION_DIAGNOSTIC"
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
                                         variant)
        (case / "original/lib.rs").write_bytes(original)
        (case / "verified/lib.rs").write_bytes(verified)
        LINK.write_json(case / "fixture.json", {
            "variant": variant, "certificate": cert,
            "original_sha256": LINK.sha(original),
            "verified_sha256": LINK.sha(verified),
            "actual_generic_drop_runtime_body_exact": variant != "guard_operand",
            "local_generic_method_runtime_body_exact": variant != "method_operand",
            "actual_nested_def_path_proved": False,
        })
        results.append(classify(case, variant, H2A.run_case(case, args)))
    LINK.write_json(evidence / "summary.json", {
        "classification": "H2_GENERIC_GUARD_LINKAGE_DIAGNOSTIC_ONLY",
        "component_accepted": False,
        "actual_nested_drop_proved": False,
        "source_certificate": cert,
        "results": results,
    })


if __name__ == "__main__":
    main()
