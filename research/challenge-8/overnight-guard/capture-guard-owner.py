#!/usr/bin/env python3
"""Hosted diagnostic for truthful nominal guard ownership and SAFE Drop body.

The local DropOnPanic DefPath is a source-equivalent stand-in, not the actual
function-local DefPath. Nothing here admits an actual-call redirect or a new
generated Drop template.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path


HERE = Path(__file__).resolve().parent
CAPTURE = None


def load():
    import importlib.util
    import sys
    path = HERE / "capture-generic-pointer-drop.py"
    spec = importlib.util.spec_from_file_location("guard_generic_drop_capture", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("H2a capture runner unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


CAPTURE = load()
LINK = CAPTURE.LINK
ACTUAL = CAPTURE.ACTUAL
CONSTRUCTOR = CAPTURE.CONSTRUCTOR
REPO = CAPTURE.REPO
VARIANTS = ("owner_positive", "missing_cell", "wrong_target", "ordinary_drop")
STRUCT_SIGNATURE = b"struct DropOnPanic<T>"
DROP_SIGNATURE = b"fn drop(&mut self)"
ACTUAL_DROP_CALL = b"unsafe { self.inner.drop_in_place() }"
OWNER_PRED = (
    b"/*@\npred<T> <DropOnPanic<T>>.own(t, g) =\n"
    b"    *g.inner |-> ?payload &*& <T>.own(t, payload);\n@*/\n"
)
OPEN_OWNER = (
    b"/*@ open <DropOnPanic<T>>.full_borrow_content(_t, self)(); @*/"
    b"/*@ open <DropOnPanic<T>>.own(_t, ?g); @*/"
)


def require(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)


def source_certificate() -> tuple[bytes, bytes, dict]:
    actual_body, actual_cert = ACTUAL.source_certificate(REPO)
    require(actual_body.count(STRUCT_SIGNATURE) == 1 and
            actual_body.count(DROP_SIGNATURE) == 1 and
            actual_body.count(ACTUAL_DROP_CALL) == 1,
            "actual guard source is no longer unique")
    struct_body = CONSTRUCTOR.extract_braced_item(actual_body, STRUCT_SIGNATURE)
    drop_body = CONSTRUCTOR.extract_braced_item(actual_body, DROP_SIGNATURE)
    require(struct_body.count(b"inner: *mut T") == 1 and
            struct_body.count(b"pub inner") == 0 and
            drop_body.count(ACTUAL_DROP_CALL) == 1 and
            drop_body.count(b"// SAFETY: Must be guaranteed on construction of local type `DropOnPanic`.") == 1,
            "actual private field or generic Drop body changed")
    return struct_body, drop_body, {
        "actual_source_certificate": actual_cert,
        "actual_guard_struct_body_sha256": LINK.sha(struct_body),
        "actual_generic_drop_body_sha256": LINK.sha(drop_body),
        "actual_guard_field": "private inner: *mut T",
        "actual_nested_drop_def_path": "<select_unpredictable::DropOnPanic<T> as std::ops::Drop>::drop",
        "local_capture_drop_def_path": "<DropOnPanic<T> as std::ops::Drop>::drop",
        "same_runtime_body": True,
        "same_nominal_def_path": False,
        "actual_call_redirect": False,
        "template_extension_active": False,
    }


def owner_constructor(variant: str) -> bytes:
    require(variant in VARIANTS[:3], "not a guard owner variant")
    params = b"slot: *mut T" + (b", other: *mut T" if variant == "wrong_target" else b"")
    cell = b"*other |-> ?value" if variant == "wrong_target" else b"*slot |-> ?value"
    pre = (b"req thread_token(?t) &*& t == currentThread &*& type_interp::<T>() &*& " +
           (b"" if variant == "missing_cell" else cell + b" &*& ") +
           (b"<T>.own(t, ?value);" if variant == "missing_cell" else
            b"<T>.own(t, value) &*& slot != other;" if variant == "wrong_target" else
            b"<T>.own(t, value);"))
    post = (b"ens thread_token(t) &*& type_interp::<T>() &*& "
            b"<DropOnPanic<T>>.own(t, result);")
    fn = (b"pub unsafe fn guard_owner_from_initialized_slot<T>(" + params +
          b") -> DropOnPanic<T>\n" +
          CAPTURE.contract(pre, post, b"on_unwind_ens false;") +
          b"{\n    let guard = DropOnPanic { inner: slot };\n"
          b"    //@ close <DropOnPanic<T>>.own(t, guard);\n"
          b"    guard\n}\n")
    return fn


def concrete_u32_witness() -> bytes:
    """Transfer one actual u32 slot cell into the nominal guard owner."""
    return (
        b"pub unsafe fn guard_owner_u32_witness(slot: *mut u32) -> DropOnPanic<u32>\n" +
        CAPTURE.contract(
            b"req thread_token(?t) &*& t == currentThread &*& type_interp::<u32>() &*& *slot |-> ?value;",
            b"ens thread_token(t) &*& type_interp::<u32>() &*& <DropOnPanic<u32>>.own(t, result);",
            b"on_unwind_ens false;") +
        b"{\n"
        b"    //@ close u32_own(t, value);\n"
        b"    unsafe { guard_owner_from_initialized_slot(slot) }\n"
        b"}\n")


def ordinary_source() -> tuple[bytes, bytes]:
    verified = (
        b"#![allow(dead_code)]\n\n"
        b"pub struct OrdinaryDrop { pub value: u32 }\n"
        b"impl Drop for OrdinaryDrop {\n"
        b"    fn drop(&mut self) {\n"
        b"        //@ open <OrdinaryDrop>.full_borrow_content(_t, self)();\n"
        b"        //@ open <OrdinaryDrop>.own(_t, ?ordinary);\n"
        b"    }\n}\n")
    original = CONSTRUCTOR.strip_ghost_annotations(verified)
    require(original.count(b"pub struct OrdinaryDrop") == 1 and
            CONSTRUCTOR.strip_ghost_annotations(verified) == original,
            "ordinary Drop control runtime changed")
    return original, verified


def guard_source(struct_body: bytes, drop_body: bytes,
                 variant: str) -> tuple[bytes, bytes]:
    require(variant in VARIANTS[:3], "not a guard owner variant")
    require(drop_body.count(ACTUAL_DROP_CALL) == 1,
            "actual unsafe generic Drop call not unique")
    annotated_body = drop_body.replace(ACTUAL_DROP_CALL,
                                       OPEN_OWNER + ACTUAL_DROP_CALL, 1)
    require(ACTUAL.strip_ghost(annotated_body) == drop_body,
            "ghost opening changed actual generic Drop runtime body")
    actual_struct = STRUCT_SIGNATURE + b" " + struct_body
    actual_impl = (b"impl<T> Drop for DropOnPanic<T> {\n"
                   b"    fn drop(&mut self) " + annotated_body + b"\n}\n")
    verified = (b"#![allow(dead_code)]\n\n" + actual_struct + b"\n\n" +
                OWNER_PRED + b"\n" + owner_constructor(variant) +
                (b"\n" + concrete_u32_witness() if variant == "owner_positive" else b"") +
                b"\n" + actual_impl)
    original = CONSTRUCTOR.strip_ghost_annotations(verified)
    require(original.count(drop_body) == 1 and
            original.count(struct_body) == 1 and
            verified.count(annotated_body) == 1 and
            CONSTRUCTOR.strip_ghost_annotations(verified) == original,
            "local source copy changed pinned actual runtime body")
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
    close_lines = [number for number, line in enumerate(
        (case / "verified/lib.rs").read_bytes().splitlines(), 1)
        if b"//@ close <DropOnPanic<T>>.own(t, guard);" in line]
    constructor = "guard_owner_from_initialized_slot"
    start = log.find("Verifying function '" + constructor + "'")
    end = log.find("Verifying function '", start + 1) if start >= 0 else -1
    ctor_log = log[start:end if end >= 0 else None] if start >= 0 else ""
    witness_name = "guard_owner_u32_witness"
    witness_start = log.find("Verifying function '" + witness_name + "'")
    witness_end = log.find("Verifying function '", witness_start + 1) if witness_start >= 0 else -1
    witness_log = log[witness_start:witness_end if witness_end >= 0 else None] if witness_start >= 0 else ""
    ordinary_log = log[log.find("Verifying function '<OrdinaryDrop as std::ops::Drop>::drop'"):] \
        if "Verifying function '<OrdinaryDrop as std::ops::Drop>::drop'" in log else ""
    result = {
        "variant": variant, "classification": "DIAGNOSTIC_ONLY",
        "component_accepted": False, "actual_nested_drop_proved": False,
        "frontend_refinement": complete, "source_integrity": intact,
        "full_verifier_exit": stages.get("full-verification", {}).get("exit"),
        "first_error": errors[0] if errors else None, "fatal": fatal,
        "owner_constructor_entered": bool(ctor_log),
        "owner_constructor_return_and_leak": "Executing return statement" in ctor_log and
            "Leak check." in ctor_log,
        "concrete_u32_witness_return_and_leak": "Executing return statement" in witness_log and
            "Leak check." in witness_log,
        "owner_close_line": close_lines[0] if len(close_lines) == 1 else None,
        "ordinary_drop_entered": bool(ordinary_log),
        "ordinary_drop_return_and_leak": "Executing return statement" in ordinary_log and
            "Leak check." in ordinary_log,
        "stages": stages,
    }
    if variant == "owner_positive" and complete and intact and \
            result["owner_constructor_return_and_leak"] and \
            result["concrete_u32_witness_return_and_leak"] and not fatal:
        result["classification"] = "OWNER_CONSTRUCTED_DIAGNOSTIC"
    elif variant == "ordinary_drop" and complete and intact and \
            stages["full-verification"]["exit"] == 0 and \
            result["ordinary_drop_return_and_leak"] and not errors and not fatal:
        result["classification"] = "ORDINARY_DROP_STOCK_PROOF_DIAGNOSTIC"
    elif variant in ("missing_cell", "wrong_target") and complete and intact and \
            stages["full-verification"]["exit"] == 1 and len(errors) == 1 and \
            len(close_lines) == 1 and \
            errors[0][0] == "verified/lib.rs" and \
            errors[0][3].startswith("No matching heap chunks: points_to<T>(") and \
            b"*g.inner |-> ?payload" in (case / "verified/lib.rs").read_bytes().splitlines()[int(errors[0][1]) - 1] and \
            result["owner_constructor_entered"] and \
            "Executing statement" in ctor_log and not fatal:
        result["classification"] = "OWNER_CONSTRUCTION_FAILURE_DIAGNOSTIC"
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
                        default=list(VARIANTS))
    args = parser.parse_args()
    require(os.environ.get("GITHUB_ACTIONS") == "true" and
            os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted" and
            os.environ.get("RUNNER_OS") == "Linux", "GitHub-hosted Linux required")
    evidence = args.evidence.resolve()
    require(not evidence.exists(), f"refusing overwrite: {evidence}")
    evidence.mkdir(parents=True)
    struct_body, drop_body, cert = source_certificate()
    LINK.write_json(evidence / "source-certificate.json", cert)
    results = []
    for variant in args.variants:
        case = evidence / variant
        case.mkdir()
        (case / "original").mkdir()
        (case / "verified").mkdir()
        original, verified = ordinary_source() if variant == "ordinary_drop" else \
            guard_source(struct_body, drop_body, variant)
        (case / "original/lib.rs").write_bytes(original)
        (case / "verified/lib.rs").write_bytes(verified)
        LINK.write_json(case / "fixture.json", {
            "variant": variant,
            "source_certificate": cert if variant != "ordinary_drop" else None,
            "actual_drop_runtime_body_exact": variant != "ordinary_drop",
            "local_def_path_only": variant != "ordinary_drop",
            "original_sha256": LINK.sha(original),
            "verified_sha256": LINK.sha(verified),
            "ghost_strip_identity": CONSTRUCTOR.strip_ghost_annotations(verified) == original,
        })
        results.append(classify(case, variant, CAPTURE.run_case(case, args)))
    LINK.write_json(evidence / "summary.json", {
        "classification": "H2B_SAFE_DROP_CAPTURE_DIAGNOSTIC_ONLY",
        "component_accepted": False,
        "actual_nested_drop_proved": False,
        "source_certificate": cert,
        "results": results,
    })


if __name__ == "__main__":
    main()
