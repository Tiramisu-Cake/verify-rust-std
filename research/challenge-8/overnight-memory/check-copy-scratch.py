#!/usr/bin/env python3
"""Hosted M1 capture; stock summary diagnostic, never actual copy acceptance."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
driver_path = HERE.parent / "overnight-helper/check-helper.py"
spec = importlib.util.spec_from_file_location("overnight_m1_driver", driver_path)
assert spec and spec.loader
DRIVER = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = DRIVER
spec.loader.exec_module(DRIVER)


def sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def main() -> None:
    DRIVER.require(os.environ.get("GITHUB_ACTIONS") == "true" and
                   os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted",
                   "executable diagnostics require GitHub-hosted runner")
    parser = argparse.ArgumentParser()
    for name in ("tool-home", "schema", "compiler-sysroot", "evidence"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--deadline-epoch", type=float, required=True)
    args = parser.parse_args()
    args.evidence.mkdir(parents=True, exist_ok=False)
    actual = (REPO / "library/core/src/slice/sort/shared/smallsort.rs").read_bytes()
    call = b"ptr::copy_nonoverlapping(min, dst, 1);"
    DRIVER.require(sha(actual) == "85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1" and actual.count(call) == 1, "pinned actual copy source changed")
    profile = {"std_smallsort_sha256": sha(actual),
               "scope": "isolated generic operation at count1; stock summary",
               "actual_wrapper_verified": False,
               "new_primitive_accepted": False,
               "generic_zst_contract_closed": False}
    outcomes = {}
    for variant in ("initialized", "uninitialized", "false_post", "owner_creation"):
        case = args.evidence / variant
        (case / "original").mkdir(parents=True)
        (case / "verified").mkdir()
        destination = (b"dst[..1] |-?-> cons(none, nil)" if variant == "uninitialized"
                       else b"dst[..1] |-> ?old_values")
        pre = (b"thread_token(?tid) &*& tid == currentThread &*& "
               b"src[..1] |-> ?values &*& " + destination +
               b" &*& *frame |-> ?flag &*& std::mem::size_of::<T>() > 0")
        post = (b"thread_token(tid) &*& src[..1] |-> values &*& "
                b"dst[..1] |-> values &*& *frame |-> flag")
        if variant == "false_post":
            post += b" &*& false"
        if variant == "owner_creation":
            post += b" &*& <T>.own(tid, head(values))"
        contract = (b"/*@\nreq " + pre + b";\n@*/\n/*@\nens " + post +
                    b";\n@*/\n/*@\non_unwind_ens false;\n@*/\n")
        verified = (b"pub unsafe fn copy_scratch_probe<T>(src: *const T, dst: *mut T, frame: *mut bool)\n" +
                    contract + b"{\n    unsafe { std::ptr::copy_nonoverlapping(src, dst, 1); }\n}\n")
        original = DRIVER.A1.strip_ghost(verified)
        (case / "original/lib.rs").write_bytes(original)
        (case / "verified/lib.rs").write_bytes(verified)
        fixture = {**profile, "variant": variant,
                   "original_sha256": sha(original), "verified_sha256": sha(verified),
                   "runtime_body": "unsafe { std::ptr::copy_nonoverlapping(src, dst, 1); }"}
        (case / "fixture.json").write_text(json.dumps(fixture, indent=2) + "\n")
        stages = DRIVER.run_case(case, args, prove=True)
        log_path = case / "full-verification.log"
        log = log_path.read_text(errors="replace") if log_path.exists() else ""
        errors = DRIVER.error_info(log)
        frontend = all(stages.get(key, {}).get("exit") == 0 for key in
                       ("normal-export", "normal-decode", "readonly-export",
                        "readonly-decode", "refinement"))
        intact = all(stage.get("source_unchanged") for stage in stages.values())
        intact = intact and (case / "original/lib.rs").read_bytes() == original and \
                 (case / "verified/lib.rs").read_bytes() == verified
        target = log[log.find("Verifying function 'copy_scratch_probe'"):]
        body = ("Executing return statement" in target and "Leak check." in target)
        exit_code = stages.get("full-verification", {}).get("exit")
        label = "INCONCLUSIVE"
        if frontend and intact and variant == "initialized" and exit_code == 0 and \
                body and not errors and "dead code" not in log.lower():
            label = "STOCK_INITIALIZED_CONTROL_PASS"
        elif frontend and intact and exit_code == 1 and len(errors) == 1:
            label = "CAPTURED_PROOF_BOUNDARY_UNREVIEWED"
        record = {"classification": label, "stages": stages,
                  "errors": errors, "target_return_leak": body,
                  "frontend_refinement": frontend, "source_integrity": intact,
                  "accepted": False, "actual_sort4_proved": False,
                  "actual_copy_wrapper_proved": False}
        outcomes[variant] = record
        (case / "classification.json").write_text(json.dumps(record, indent=2) + "\n")
        print(json.dumps({"variant": variant, "classification": label, "errors": errors}))
    (args.evidence / "summary.json").write_text(json.dumps(outcomes, indent=2) + "\n")


if __name__ == "__main__":
    main()
