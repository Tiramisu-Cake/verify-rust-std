#!/usr/bin/env python3
"""Hosted H2a capture of the source-exact, generic pointer-drop method copy.

This driver does not activate or accept a new frontend rule. In particular,
its proof cases cannot establish actual DropOnPanic linkage by themselves.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]


def load(path: Path, name: str):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


LINK = load(HERE.parent / "overnight-linkage/check-constructor-linkage.py",
            "guard_generic_pointer_linkage_runner")
CONSTRUCTOR = LINK.CONSTRUCTOR
DROP_SOURCE = load(HERE.parent / "overnight-s6/prepare-pointer-drop-diagnostic.py",
                   "guard_generic_pointer_source")
ACTUAL = LINK.ACTUAL
METHOD = b"sort4_checked_generic_drop"
PROBE = b"sort4_generic_drop_probe"
VARIANTS = ("positive", "missing_owner", "false_normal_post",
            "false_unwind_post")


def require(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)


def source_certificate() -> tuple[bytes, dict]:
    _, pointer_cert = DROP_SOURCE.source_certificate(REPO, CONSTRUCTOR)
    body = DROP_SOURCE.METHOD_BODY.replace(
        b"drop_in_place(self)", b"std::ptr::drop_in_place(slot)", 1)
    require(body.count(b"std::ptr::drop_in_place(slot)") == 1 and
            body.count(b"self") == 0 and
            DROP_SOURCE.METHOD_BODY.count(b"drop_in_place(self)") == 1,
            "generic method copy differs from pinned std body")
    actual_body, actual_cert = ACTUAL.source_certificate(REPO)
    require(actual_body.count(b"impl<T> Drop for DropOnPanic<T>") == 1 and
            actual_body.count(b"unsafe { self.inner.drop_in_place() }") == 1,
            "actual nested generic Drop body changed")
    return body, {
        "method_std_source": pointer_cert,
        "generic_copy_body_sha256": LINK.sha(body),
        "generic_binding_changes": ["self -> slot", "free call -> std::ptr::drop_in_place"],
        "actual_nested_drop_body_sha256": LINK.sha(actual_body),
        "actual_source_certificate": actual_cert,
        "source_exact": True,
        "typed_mir_gate": "PENDING_CAPTURE",
        "actual_call_redirect": False,
        "nominal_owner_proved": False,
    }


def contract(pre: bytes, post: bytes, unwind: bytes) -> bytes:
    require(pre.startswith(b"req ") and post.startswith(b"ens ") and
            unwind.startswith(b"on_unwind_ens ") and
            all(x.endswith(b";") for x in (pre, post, unwind)),
            "incomplete generic drop contract")
    return CONSTRUCTOR.ghost_block(b"\n".join((pre, post, unwind)))


def source_pair(body: bytes, variant: str) -> tuple[bytes, bytes]:
    require(variant in VARIANTS, "unknown H2a variant")
    method_common = b"thread_token(t)"
    probe_common = b"thread_token(t) &*& type_interp::<T>()"
    method_contract = contract(
        b"req thread_token(?t) &*& t == currentThread &*& "
        b"*slot |-> ?value &*& <T>.own(t, value);",
        b"ens " + method_common + b" &*& *slot |-> _;",
        b"on_unwind_ens " + method_common + b" &*& *slot |-> _;")
    method = (b"pub unsafe fn " + METHOD + b"<T>(slot: *mut T)\n" +
              method_contract + body + b"\n\n")
    pre = (b"req thread_token(?t) &*& t == currentThread &*& type_interp::<T>() &*& *slot |-> ?value" +
           (b"" if variant == "missing_owner" else b" &*& <T>.own(t, value)") +
           b" &*& [?f](*frame |-> ?frame_value);")
    retained = probe_common + b" &*& *slot |-> _ &*& [f](*frame |-> frame_value)"
    post = b"ens " + (b"false" if variant == "false_normal_post" else retained) + b";"
    unwind = b"on_unwind_ens " + (
        b"false" if variant == "false_unwind_post" else retained) + b";"
    probe = (b"pub unsafe fn " + PROBE + b"<T>(slot: *mut T, frame: *const u8)\n" +
             contract(pre, post, unwind) +
             b"{ unsafe { sort4_checked_generic_drop(slot) } }\n")
    verified = b"#![allow(dead_code)]\n\n" + method + probe
    original = CONSTRUCTOR.strip_ghost_annotations(verified)
    require(original.count(body) == verified.count(body) == 1 and
            original.count(b"std::ptr::drop_in_place(slot)") == 1 and
            CONSTRUCTOR.strip_ghost_annotations(verified) == original,
            "ghost source pair changed generic method runtime body")
    return original, verified


def run_case(case: Path, args) -> dict:
    exporter = str(args.tool_home / "bin/vf-rust-mir-exporter")
    stages = {}
    stages["normal-export"] = LINK.stage(case, "normal-export", [
        exporter, "verified/lib.rs", f"--sysroot={args.compiler_sysroot}",
        "--edition", "2021"], args, output_name="normal-mir.bin")
    stages["readonly-export"] = LINK.stage(case, "readonly-export", [
        exporter, "verified/lib.rs", f"--sysroot={args.compiler_sysroot}",
        "--edition", "2021", "--crate-type", "lib",
        "--vf-rust-mir-exporter:preprocess-readonly"], args,
        output_name="readonly-mir.bin")
    for mode in ("normal", "readonly"):
        if stages[f"{mode}-export"]["exit"] == 0:
            stages[f"{mode}-decode"] = LINK.stage(case, f"{mode}-decode", [
                "capnp", "decode", str(args.schema), "VfMir"], args,
                input_name=f"{mode}-mir.bin", output_name=f"{mode}-mir.txt",
                cap_seconds=40)
    four = all(stages.get(k, {}).get("exit") == 0 for k in (
        "normal-export", "normal-decode", "readonly-export", "readonly-decode"))
    if four:
        stages["full-verification"] = LINK.stage(case, "full-verification", [
            str(args.tool_home / "bin/verifast"), "-rustc_args", "--edition 2021",
            "-verbose", "1", "verified/lib.rs"], args, cap_seconds=100)
        stages["refinement"] = LINK.stage(case, "refinement", [
            str(args.tool_home / "bin/refinement-checker"), "--rustc-args",
            "--edition 2021", "original/lib.rs", "verified/lib.rs"], args,
            cap_seconds=70)
    return stages


def classify(case: Path, variant: str, stages: dict) -> dict:
    complete = all(stages.get(k, {}).get("exit") == 0 for k in (
        "normal-export", "normal-decode", "readonly-export", "readonly-decode",
        "refinement"))
    intact = all(s.get("source_unchanged") is True for s in stages.values())
    log = (case / "full-verification.log").read_text(errors="replace") if \
        (case / "full-verification.log").exists() else ""
    errors = LINK.ERR.findall(log)
    fatal = [line for line in log.splitlines() if line.startswith("Fatal error:")]
    method_name, probe_name = METHOD.decode(), PROBE.decode()
    method_log = LINK.function_log(log, method_name) if hasattr(LINK, "function_log") else ""
    if not method_log:
        start = log.find("Verifying function '" + method_name + "'")
        end = log.find("Verifying function '", start + 1) if start >= 0 else -1
        method_log = log[start:end if end >= 0 else None] if start >= 0 else ""
    probe_start = log.find("Verifying function '" + probe_name + "'")
    probe_end = log.find("Verifying function '", probe_start + 1) if probe_start >= 0 else -1
    probe_log = log[probe_start:probe_end if probe_end >= 0 else None] if probe_start >= 0 else ""
    result = {
        "variant": variant, "classification": "DIAGNOSTIC_ONLY",
        "component_accepted": False, "actual_drop_proved": False,
        "frontend_refinement": complete, "source_integrity": intact,
        "full_verifier_exit": stages.get("full-verification", {}).get("exit"),
        "first_error": errors[0] if errors else None, "fatal": fatal,
        "generic_method_entered": bool(method_log),
        "generic_method_return_and_leak": "Executing return statement" in method_log and
            "Leak check." in method_log,
        "probe_entered": bool(probe_log),
        "probe_return_and_leak": "Executing return statement" in probe_log and
            "Leak check." in probe_log,
        "stages": stages,
    }
    if variant == "positive" and complete and intact and \
            stages["full-verification"]["exit"] == 0 and \
            result["generic_method_return_and_leak"] and \
            result["probe_return_and_leak"] and not errors and not fatal:
        result["classification"] = "GENERIC_METHOD_LOCAL_PROOF_DIAGNOSTIC"
    elif variant != "positive" and complete and intact and \
            stages["full-verification"]["exit"] == 1 and len(errors) == 1 and \
            not fatal and result["generic_method_return_and_leak"] and \
            result["probe_entered"]:
        result["classification"] = "TARGET_PROBE_FAILURE_DIAGNOSTIC"
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
    body, certificate = source_certificate()
    LINK.write_json(evidence / "source-certificate.json", certificate)
    results = []
    for variant in args.variants:
        case = evidence / variant
        case.mkdir()
        (case / "original").mkdir()
        (case / "verified").mkdir()
        original, verified = source_pair(body, variant)
        (case / "original/lib.rs").write_bytes(original)
        (case / "verified/lib.rs").write_bytes(verified)
        LINK.write_json(case / "fixture.json", {
            "variant": variant, "source_certificate": certificate,
            "original_sha256": LINK.sha(original),
            "verified_sha256": LINK.sha(verified),
            "source_exact": CONSTRUCTOR.strip_ghost_annotations(verified) == original,
            "actual_runtime_modified": False,
        })
        results.append(classify(case, variant, run_case(case, args)))
    LINK.write_json(evidence / "summary.json", {
        "classification": "H2A_CAPTURE_DIAGNOSTIC_ONLY",
        "component_accepted": False,
        "actual_drop_proved": False,
        "source_certificate": certificate,
        "results": results,
    })


if __name__ == "__main__":
    main()
