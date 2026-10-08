#!/usr/bin/env python3
"""Hosted diagnostic for actual typed select and pointer-drop linkage."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
ASPTR_LINK = None


def load_modules():
    import importlib.util
    import sys
    path = HERE / "check-asptr-linkage.py"
    spec = importlib.util.spec_from_file_location("overnight_actual_asptr_link", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("as_mut_ptr linkage driver unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ASPTR_LINK = load_modules()
LINK = ASPTR_LINK.LINK
CONSTRUCTOR = LINK.CONSTRUCTOR
DROP = LINK.load(REPO / "research/challenge-8/overnight-s6/check-pointer-drop.py",
                 "overnight_actual_pointer_drop")
DROP_SOURCE = LINK.load(
    REPO / "research/challenge-8/overnight-s6/prepare-pointer-drop-diagnostic.py",
    "overnight_actual_pointer_drop_source")
INTRINSIC = LINK.load(
    REPO / "research/challenge-8/overnight-s6/check-select-pointer-intrinsics.py",
    "overnight_actual_typed_intrinsic_source")
VARIANTS = ("intrinsic_only", "pointer_drop", "pointer_drop_source_operand")
DROP_MARKER = b"pub unsafe fn sort4_checked_pointer_drop<Element>"
DROP_CALL = b"std::ptr::drop_in_place(slot)"
CAPTURE_CONTRACT = (
    b"/*@\nreq thread_token(?t) &*& t == currentThread;\n@*/\n"
    b"/*@\nens thread_token(t) &*& (result as pointer) ==\n"
    b"    (if condition { true_val as pointer } else { false_val as pointer });\n@*/\n"
    b"/*@\non_unwind_ens false;\n@*/\n"
)
INTRINSIC_GATE_CONTRACT = (
    b"/*@\nreq thread_token(?t) &*& t == currentThread;\n@*/"
    b"/*@\nens thread_token(t) &*& (result as pointer) ==\n"
    b"        (if condition { true_val as pointer } else { false_val as pointer });\n@*/"
    b"/*@ on_unwind_ens false; @*/\n"
)


def canonical_actual_contract(source: bytes) -> bytes:
    LINK.require(source.count(CAPTURE_CONTRACT) == 1 and
                 source.count(INTRINSIC_GATE_CONTRACT) == 0,
                 "O4 actual capture contract no longer has exact reviewed bytes")
    adjusted = source.replace(CAPTURE_CONTRACT, INTRINSIC_GATE_CONTRACT, 1)
    LINK.require(CONSTRUCTOR.strip_ghost_annotations(adjusted) ==
                 CONSTRUCTOR.strip_ghost_annotations(source),
                 "intrinsic gate contract formatting changed runtime Rust")
    LINK.require(adjusted.count(b"req thread_token(?t) &*& t == currentThread;") == 1 and
                 adjusted.count(b"ens thread_token(t) &*& (result as pointer) ==") == 1 and
                 adjusted.count(b"on_unwind_ens false;") == 1,
                 "actual full contract clauses changed")
    return adjusted


def make_case(baseline_verified: bytes, actual_body: bytes, ctor_cert: dict,
              asptr_adapter: bytes, drop_body: bytes, case: Path,
              variant: str) -> dict:
    record = ASPTR_LINK.make_case(baseline_verified, actual_body, ctor_cert,
                                  asptr_adapter, case, "positive")
    verified_path = case / "verified/lib.rs"
    original_path = case / "original/lib.rs"
    verified = verified_path.read_bytes()
    if variant != "intrinsic_only":
        method = DROP.helper_source(drop_body, CONSTRUCTOR)
        LINK.require(method.count(DROP_MARKER) == 1 and
                     method.count(DROP_CALL) == 1,
                     "source-certified pointer-drop method changed")
        if variant == "pointer_drop_source_operand":
            method = method.replace(
                DROP_CALL,
                b"std::ptr::drop_in_place(core::ptr::null_mut::<*const Element>())",
                1)
        LINK.require(verified.count(DROP_MARKER) == 0 and
                     verified.count(LINK.ACTUAL_MARKER) == 1,
                     "actual fixture already contains pointer-drop adapter")
        verified = verified.replace(LINK.ACTUAL_MARKER,
                                    method + b"\n" + LINK.ACTUAL_MARKER, 1)
    original = CONSTRUCTOR.strip_ghost_annotations(verified)
    LINK.require(original.count(actual_body) == verified.count(actual_body) == 1 and
                 original.count(b"crate::mem::forget(guard);") == 1 and
                 CONSTRUCTOR.strip_ghost_annotations(verified) == original,
                 "linkage changed actual runtime body")
    verified_path.write_bytes(verified)
    original_path.write_bytes(original)
    record.update({
        "variant": variant,
        "actual_body_byte_identical": True,
        "actual_full_contract_format": "S6 exact source/MIR gate; same full clauses as O4 capture",
        "intrinsic_activation": True,
        "pointer_drop_activation": variant != "intrinsic_only",
        "drop_source_mutation": "operand" if variant.endswith("operand") else None,
        "original_sha256": LINK.sha(original),
        "verified_sha256": LINK.sha(verified),
        "scope": "typed intrinsic/pointer-drop translation diagnostic; actual helper not proved",
    })
    LINK.write_json(case / "fixture.json", record)
    return record


def stage(case: Path, name: str, command: list[str], args,
          *, input_name: str | None = None, output_name: str | None = None,
          gates: bool = False, pointer_drop: bool = False,
          cap_seconds: int = 90) -> dict:
    remaining = int(args.deadline_epoch - time.time()) - 25
    if remaining < 8:
        record = {"status": "NOT_RUN_DEADLINE", "exit": None,
                  "source_unchanged": None}
        LINK.write_json(case / f"{name}-stage.json", record)
        return record
    before = LINK.source_hashes(case)
    env = os.environ.copy()
    for key in ("SORT4_MAYBEUNINIT_REPO_ROOT",
                "SORT4_SELECT_INTRINSIC_REPO_ROOT",
                "SORT4_POINTER_DROP_REPO_ROOT"):
        env.pop(key, None)
    if gates:
        env["SORT4_MAYBEUNINIT_REPO_ROOT"] = str(REPO)
        env["SORT4_SELECT_INTRINSIC_REPO_ROOT"] = str(REPO)
        if pointer_drop:
            env["SORT4_POINTER_DROP_REPO_ROOT"] = str(REPO)
    env["PATH"] = str(args.tool_home / "bin") + os.pathsep + env.get("PATH", "")
    stdout = case / (output_name or f"{name}.log")
    stderr = case / f"{name}-stderr.log" if output_name else stdout
    timeout = max(8, min(cap_seconds, remaining))
    with (case / input_name).open("rb") if input_name else open(os.devnull, "rb") as inp:
        with stdout.open("wb") as out:
            if stderr == stdout:
                result = subprocess.run(
                    ["timeout", "--signal=TERM", "--kill-after=10s",
                     f"{timeout}s", *command], cwd=case, stdin=inp,
                    stdout=out, stderr=subprocess.STDOUT, env=env, check=False)
            else:
                with stderr.open("wb") as err:
                    result = subprocess.run(
                        ["timeout", "--signal=TERM", "--kill-after=10s",
                         f"{timeout}s", *command], cwd=case, stdin=inp,
                        stdout=out, stderr=err, env=env, check=False)
    after = LINK.source_hashes(case)
    record = {"status": "RAN" if result.returncode != 124 else "TIMED_OUT",
              "exit": result.returncode, "argv": command,
              "intrinsic_gate_active": gates,
              "pointer_drop_gate_active": gates and pointer_drop,
              "source_unchanged": before == after,
              "source_before": before, "source_after": after,
              "stdout": stdout.name, "stderr": stderr.name}
    LINK.write_json(case / f"{name}-stage.json", record)
    return record


def run_case(case: Path, args, *, pointer_drop: bool) -> dict:
    exporter = str(args.tool_home / "bin/vf-rust-mir-exporter")
    stages = {}
    stages["normal-export"] = stage(case, "normal-export", [
        exporter, "verified/lib.rs", f"--sysroot={args.compiler_sysroot}",
        "--edition", "2021"], args, output_name="normal-mir.bin")
    stages["readonly-export"] = stage(case, "readonly-export", [
        exporter, "verified/lib.rs", f"--sysroot={args.compiler_sysroot}",
        "--edition", "2021", "--crate-type", "lib",
        "--vf-rust-mir-exporter:preprocess-readonly"], args,
        output_name="readonly-mir.bin")
    for mode in ("normal", "readonly"):
        if stages[f"{mode}-export"]["exit"] == 0:
            stages[f"{mode}-decode"] = stage(case, f"{mode}-decode", [
                "capnp", "decode", str(args.schema), "VfMir"], args,
                input_name=f"{mode}-mir.bin", output_name=f"{mode}-mir.txt",
                cap_seconds=40)
    four = all(stages.get(k, {}).get("exit") == 0 for k in (
        "normal-export", "normal-decode", "readonly-export", "readonly-decode"))
    if four:
        stages["full-verification"] = stage(case, "full-verification", [
            str(args.tool_home / "bin/verifast"), "-rustc_args",
            "--edition 2021", "-verbose", "1", "verified/lib.rs"], args,
            gates=True, pointer_drop=pointer_drop, cap_seconds=100)
        stages["refinement"] = stage(case, "refinement", [
            str(args.tool_home / "bin/refinement-checker"), "--rustc-args",
            "--edition 2021", "original/lib.rs", "verified/lib.rs"], args,
            cap_seconds=70)
    return stages


def classify(case: Path, variant: str, stages: dict) -> dict:
    frontend = all(stages.get(name, {}).get("exit") == 0 for name in (
        "normal-export", "normal-decode", "readonly-export",
        "readonly-decode", "refinement"))
    intact = all(item.get("source_unchanged") is True for item in stages.values())
    log_path = case / "full-verification.log"
    log = log_path.read_text(errors="replace") if log_path.exists() else ""
    errors = LINK.ERR.findall(log)
    fatal = [line for line in log.splitlines() if line.startswith("Fatal error:")]
    result = {"variant": variant, "classification": "INCONCLUSIVE",
              "frontend_refinement": frontend, "source_integrity": intact,
              "full_verifier_exit": stages.get("full-verification", {}).get("exit"),
              "first_error": errors[0] if errors else None,
              "fatal": fatal, "stages": stages}
    if variant == "pointer_drop_source_operand":
        reason = ('Fatal error: exception Failure("SORT4-POINTER-DROP: '
                  'certificate mismatch: method source body differs from pinned source")')
        checks = {"exact_source_certificate_reason": fatal == [reason],
                  "no_function_proof": "Verifying function '" not in log,
                  "no_proof_error": not errors}
        result["checks"] = checks
        if frontend and intact and stages["full-verification"]["exit"] == 2 and \
                all(checks.values()):
            result["classification"] = "INTENDED_DROP_SOURCE_REJECTION"
    else:
        ctor = ASPTR_LINK.function_log(
            log, "sort4_certified_maybeuninit::sort4_checked_maybeuninit_new")
        asptr = ASPTR_LINK.function_log(log, "sort4_checked_as_mut_ptr")
        drop = ASPTR_LINK.function_log(log, "sort4_checked_pointer_drop")
        checks = {
            "constructor_certificate": "SORT4-MAYBEUNINIT: full typed constructor MIR graph accepted" in log,
            "asptr_certificate": "SORT4-AS-MUT-PTR: full typed body MIR graph accepted" in log,
            "actual_intrinsic_full_graph": "SORT4-SELECT-INTRINSIC: full typed actual MIR graph accepted" in log,
            "intrinsic_exact_counts": "SORT4-SELECT-INTRINSIC: checked SAFE adapter translated (ptr=2, wrapper=1)" in log,
            "ptr_intrinsic_calls": all(log.count(
                "SORT4-SELECT-INTRINSIC: modeled typed pointer call " + str(i)) == 1
                for i in (1, 2)),
            "mu_intrinsic_call": log.count(
                "SORT4-SELECT-INTRINSIC: modeled typed wrapper call 1") == 1,
            "constructor_asptr_redirects": all(log.count(
                marker) == 1 for marker in (
                "SORT4-MAYBEUNINIT: redirected checked external pointer call 1",
                "SORT4-MAYBEUNINIT: redirected checked external pointer call 2",
                "SORT4-AS-MUT-PTR: redirected typed external call 1",
                "SORT4-AS-MUT-PTR: redirected typed external call 2")),
            "constructor_proved": "Executing return statement" in ctor and "Leak check." in ctor,
            "asptr_proved": "Executing return statement" in asptr and "Leak check." in asptr,
            "actual_body_entered": "Verifying function 'select_unpredictable'" in log,
            "no_certificate_fatal": not fatal,
            "no_old_missing_call": not any(
                "No such function: " + name in log for name in (
                    "std::mem::MaybeUninit::<T>::new",
                    "std::mem::MaybeUninit::<T>::as_mut_ptr",
                    "std::intrinsics::select_unpredictable")),
            "verifier_completed_or_named_error":
                (stages.get("full-verification", {}).get("exit") == 0 and not errors) or
                (stages.get("full-verification", {}).get("exit") == 1 and len(errors) == 1),
        }
        if variant == "pointer_drop":
            checks.update({
                "drop_full_mir_certificate": "SORT4-POINTER-DROP: full typed method MIR graph accepted" in log,
                "drop_glue_once": log.count("SORT4-POINTER-DROP: modeled typed pointer drop 1") == 1,
                "actual_drop_redirect_once": log.count("SORT4-POINTER-DROP: redirected typed external method 1") == 1,
                "drop_exact_counts": "SORT4-POINTER-DROP: checked unsafe method translated (glue=1, redirected=1)" in log,
                "local_drop_method_proved": "Executing return statement" in drop and "Leak check." in drop,
                "no_old_missing_drop": "No such function: std::ptr::mut_ptr::<impl *mut T>::drop_in_place" not in log,
            })
        result["checks"] = checks
        if frontend and intact and all(checks.values()):
            result["classification"] = (
                "INTRINSIC_TRANSLATION_DIAGNOSTIC" if variant == "intrinsic_only"
                else "INTRINSIC_DROP_TRANSLATION_DIAGNOSTIC")
    LINK.write_json(case / "classification.json", result)
    return result


def main() -> None:
    LINK.require(os.environ.get("GITHUB_ACTIONS") == "true" and
                 os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted" and
                 os.environ.get("RUNNER_OS") == "Linux",
                 "intrinsic/drop linkage is hosted-only")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool-home", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--compiler-sysroot", required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--deadline-epoch", type=int, required=True)
    args = parser.parse_args()
    evidence = args.evidence.resolve()
    LINK.require(not evidence.exists(), f"refusing overwrite: {evidence}")
    evidence.mkdir(parents=True)
    baseline_dir = evidence / "baseline-capture"
    LINK.ACTUAL.write_fixture(REPO, baseline_dir)
    actual_body, actual_cert = LINK.ACTUAL.source_certificate(REPO)
    ctor_cert = CONSTRUCTOR.certify_repository_sources(REPO)
    asptr_adapter, asptr_cert, _ = ASPTR_LINK.adapter_source(
        evidence, "positive", CONSTRUCTOR)
    drop_body, drop_cert = DROP_SOURCE.source_certificate(REPO, CONSTRUCTOR)
    intrinsic_cert = INTRINSIC.source_certificate(REPO, CONSTRUCTOR)
    baseline_verified = canonical_actual_contract(
        (baseline_dir / "verified/lib.rs").read_bytes())
    results = []
    for variant in VARIANTS:
        try:
            case = evidence / variant
            fixture = make_case(baseline_verified, actual_body, ctor_cert,
                                asptr_adapter, drop_body, case, variant)
            stages = run_case(case, args, pointer_drop=variant != "intrinsic_only")
            result = classify(case, variant, stages)
            result["fixture"] = fixture
        except Exception as exc:
            result = {"variant": variant, "classification": "INCONCLUSIVE",
                      "harness_exception": f"{type(exc).__name__}: {exc}"}
        results.append(result)
        print(json.dumps({"variant": variant,
                          "classification": result["classification"],
                          "first_error": result.get("first_error")}), flush=True)
    accepted = [r["classification"] for r in results] == [
        "INTRINSIC_TRANSLATION_DIAGNOSTIC",
        "INTRINSIC_DROP_TRANSLATION_DIAGNOSTIC",
        "INTENDED_DROP_SOURCE_REJECTION"]
    LINK.write_json(evidence / "summary.json", {
        "classification": "TYPED_LINKAGE_DIAGNOSTIC_ACCEPTED" if accepted else
                          "INCONCLUSIVE",
        "accepted_component": accepted,
        "actual_helper_proved": False,
        "compiler_intrinsic_correspondence_trusted": True,
        "compiler_drop_glue_correspondence_trusted": True,
        "actual_body_sha256": LINK.sha(actual_body),
        "actual_source_certificate": actual_cert,
        "constructor_source_certificate": ctor_cert,
        "asptr_source_certificate": asptr_cert,
        "intrinsic_source_certificate": intrinsic_cert,
        "drop_source_certificate": drop_cert,
        "results": results,
    })
    if not accepted:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
