"""Cloud-only native diagnostics with separately pinned capture-only extension.

Every case retains its raw source, paired MIR, refinement and full verifier log.
Collector completion is never a proof verdict. Only reviewed pinned deltas apply.
"""

from __future__ import annotations

import argparse

import hashlib

import importlib.util

import json

import os

from pathlib import Path

import re

import shutil

import subprocess

import sys

import time

from types import SimpleNamespace

ROOT = Path("research/challenge-8/cloud-build")

FROZEN_HERE = ROOT / "sort4-native-c4"

OPAQUE_PHASE = "SORT4-NATIVE-OPAQUE-CLOUD-2026-10-10"

OPAQUE_SESSION = os.environ.get("SORT4_NATIVE_OPAQUE_PHASE") == "1"

C1_ZST_REPAIR_PHASE = "SORT4-NATIVE-C1-ZST-REPAIR-CLOUD-2026-10-11"

C1_ZST_REPAIR_SESSION = os.environ.get("SORT4_NATIVE_C1_ZST_REPAIR_PHASE") == "1"

HERE = ROOT / ("sort4-native-c1-bound" if C1_ZST_REPAIR_SESSION else
               "sort4-native-opaque" if OPAQUE_SESSION else "sort4-native-c4")

TRANSLATOR = Path("src/rust_frontend/vf_mir_translator/vf_mir_translator.ml")

KERNEL = Path("src/verifast.ml")

FINAL_TRANSLATOR = "1eab6eb54fe5c23d53ca72a6d9dfcbbff09c09ffaf26c48a4f450f5068a8d313"

FINAL_KERNEL = "37ed2550d276abccbbe0a9ced678137ef587f80782bcff763062df394c2a440c"

FINAL_SOURCE = "ba9e6ad3633004c3d934c590462443951ddd6dec80a5df9ffb687ec940958c6f"

FINAL_PRE_AST = "0ed31137cf55a2ed47ed624a6c61591e4aaf96371df3c2979fc10ce8d95bb222"

PHASE = (C1_ZST_REPAIR_PHASE if C1_ZST_REPAIR_SESSION else OPAQUE_PHASE if OPAQUE_SESSION
         else "SORT4-NATIVE-C4-CLOUD-2026-10-10")

PATCHES = (
    ("overnight-callback/ACTUAL-SORT4-AST-SCOPE-TEST.json", "profile_components.overlay_patch_sha256", "overnight-callback/verifast-actual-sort4-first-scope-TEST.patch", None, None),
    ("overnight-callback/ACTUAL-SORT4-C1-OUTPUT-EQ-TEST.json", "patch_sha256", "overnight-callback/verifast-actual-sort4-c1-output-eq-TEST.patch", None, None),
    ("overnight-callback/ACTUAL-SORT4-C1-DEBT-CONTROLS-TEST.json", "patch_sha256", "overnight-callback/verifast-actual-sort4-c1-debt-controls-TEST.patch", None, None),
    ("cloud-build/sort4-native-entry-c1/C1-PREFIX-PROFILE.json", "patch_sha256", "cloud-build/sort4-native-entry-c1/verifast-actual-c1-prefix-TEST.patch", "base_translator_sha256", "patched_translator_sha256"),
    ("cloud-build/sort4-native-entry-c1/C2-DISCOVERY-PROFILE.json", "patch_sha256", "cloud-build/sort4-native-entry-c1/verifast-actual-c2-discovery-TEST.patch", "base_translator_sha256", "patched_translator_sha256"),
    ("cloud-build/sort4-c2-bound-prefix/profile.json", "patch_sha256", "cloud-build/sort4-c2-bound-prefix/verifast-c2-bound-prefix-TEST.patch", "base_translator_sha256", "patched_translator_sha256"),
    ("cloud-build/sort4-c3-bound-prefix/capture-profile.json", "incremental_patch_sha256", "cloud-build/sort4-c3-bound-prefix/verifast-c3-capture-TEST.patch", "base_translator_sha256", "patched_translator_sha256"),
    ("cloud-build/sort4-c3-bound-prefix/profile.json", "patch_sha256", "cloud-build/sort4-c3-bound-prefix/verifast-c3-bound-prefix-TEST.patch", "base_translator_sha256", "patched_translator_sha256"),
    ("cloud-build/sort4-c4-bound-prefix/capture-profile.json", "incremental_patch_sha256", "cloud-build/sort4-c4-bound-prefix/verifast-c4-capture-TEST.patch", "base_translator_sha256", "patched_translator_sha256"),
    ("cloud-build/sort4-c4-bound-prefix/profile.json", "patch_sha256", "cloud-build/sort4-c4-bound-prefix/verifast-c4-bound-prefix-TEST.patch", "base_translator_sha256", "patched_translator_sha256"),
)

DISABLED_C_SCOPES = (
    "SORT4_ACTUAL_C1_PREFIX_TEST", "SORT4_ACTUAL_C2_DISCOVERY_TEST",
    "SORT4_ACTUAL_C2_BOUND_PREFIX_TEST", "SORT4_ACTUAL_C3_CAPTURE_TEST",
    "SORT4_ACTUAL_C3_BOUND_PREFIX_TEST", "SORT4_ACTUAL_C4_CAPTURE_TEST",
    "SORT4_ACTUAL_C4_BOUND_PREFIX_TEST", "SORT4_C2_DISCOVERY",
)

CONTROLS = ("normal-false-post", "c1-unwind-false-assert",
            "c2-unwind-false-assert", "c3-unwind-false-assert",
            "c4-unwind-false-assert")

NATIVE = ("source-typed-frame-positive", "source-typed-missing-T-negative",
          "source-typed-missing-F-negative")

BOUND_SOURCE = "7ebcf7cd435c31b3f4669ac6f31a62fd45fcb2c7fa03500bdfbc44ccaca01742"

BOUND_ORIGINAL = "7c35a7e01915233308d113b081f26784c4ad5aaf6f7049dc209d126e3eb326a1"

BOUND_NORMAL_MIR = "8e9adcccd136d3c1ee4dc1e7bd929c3cd60883f497178eab24da40f60754dee4"

BOUND_READONLY_MIR = "bde6d797d56e0e11e9837fc922f6def819c6931d1349f42c5b36d4570e2001aa"

BOUND_PRE_AST = "18973de5dd5ff1a9c94652fd808d42ffe2297096adb8a3cc1980f74a554ccea5"

BOUND_CASE_CONTROLS = {
    "native-c1-bound-positive": ("1", "none", "0"),
    "native-c1-bound-default-off": ("0", "none", "0"),
    "native-c1-bound-false-normal": ("1", "normal_false", "0"),
    "native-c1-bound-false-unwind": ("1", "unwind_false", "0"),
    "native-c1-bound-source-refusal": ("1", "none", "0"),
    "native-c1-bound-extra-body": ("1", "none", "0"),
    "native-c1-bound-malformed": ("bad", "none", "0"),
    "native-c1-bound-mixed": ("1", "none", "1"),
}

def need(value: bool, reason: str) -> None:
    if not value:
        raise RuntimeError(reason)

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")

def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, f"missing module {path}")
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

def field(data: dict, dotted: str):
    value = data
    for key in dotted.split("."):
        value = value[key]
    return value

def stage(a, root: Path, name: str, argv: list[str], env: dict[str, str],
          cap: int = 180, *, cwd: Path | None = None,
          stdin: Path | None = None, stdout: Path | None = None) -> dict:
    root.mkdir(parents=True, exist_ok=True)
    seconds = min(cap, a.deadline_epoch - int(time.time()) - 30)
    row = {"argv": argv, "cwd": str(cwd or root), "timeout_seconds": max(seconds, 0),
           "proof_verdict": None, "classification": "NOT_RUN_DEADLINE"}
    save(root / f"{name}-stage.json", row)
    if seconds <= 0:
        return row
    log_path = root / f"{name}.log"
    resource = root / f"{name}-resources.txt"
    with log_path.open("wb") as log:
        inp = stdin.open("rb") if stdin else subprocess.DEVNULL
        out = stdout.open("wb") if stdout else log
        try:
            code = subprocess.run(
                ["/usr/bin/time", "-v", "-o", str(resource), "timeout",
                 "--signal=TERM", "--kill-after=10s", f"{seconds}s", *argv],
                cwd=cwd or root, env={**env, "PWD": str(cwd or root)},
                stdin=inp, stdout=out, stderr=log, check=False).returncode
        finally:
            if stdin:
                inp.close()
            if stdout:
                out.close()
    row.update(exit=code, classification="TERMINAL", log_sha256=sha(log_path),
               resources=resource.name,
               stdout_sha256=sha(stdout) if stdout and stdout.is_file() else None)
    save(root / f"{name}-stage.json", row)
    save(a.evidence / "stage-progress.json", {"case": root.name, "stage": name,
                                              "exit": code, "proof_verdict": None})
    return row

def clean_env(a, tool: Path) -> dict[str, str]:
    env = {key: value for key, value in os.environ.items()
           if not key.startswith(("SORT4_", "O26_WITH_"))}
    deps = a.work_root / "vfdeps-adf88dc"
    need(all((deps / part).is_dir() for part in ("bin", "include", "lib")),
         "frozen vfdeps are missing")
    env.update(PATH=f"{tool / 'bin'}:{deps / 'bin'}:{env.get('PATH', '')}",
               LD_LIBRARY_PATH=f"{a.compiler_sysroot / 'lib'}:{tool / 'bin'}:{deps / 'lib'}",
               CAPNP_INC_DIR=str(deps / "include"),
               RUSTUP_TOOLCHAIN="nightly-2026-09-25",
               SMALLSORT_CLOUD_PROVIDER_PATH=str(a.cloud_dir / "provider.py"))
    return env

def first_failure(root: Path, stages: dict[str, dict], name: str = "verification") -> dict:
    order = ("normal-export", "normal-decode", "readonly-export", "readonly-decode",
             "refinement", name)
    first_stage = next((key for key in order if stages.get(key, {}).get("exit") != 0), None)
    log = root / f"{first_stage}.log" if first_stage else root / f"{name}.log"
    raw = log.read_text(errors="replace") if log.is_file() else ""
    errors = [line for line in raw.splitlines()
              if ": error:" in line or line.startswith(("Fatal error:", "error:", "error["))
              or re.fullmatch(r"verified/lib\.rs\(\d+,\d+(?:-\d+)?\): dead code", line)]
    return {"first_causal_stage": first_stage or "NONE_OBSERVED",
            "first_error": errors[0] if errors else None,
            "first_stage_log_sha256": sha(log) if log.is_file() else None,
            "verifier_exit": stages.get(name, {}).get("exit"),
            "collector_pass_is_proof": False}

def source_support(a, tool: Path, fixture: Path, root: Path,
                   env: dict[str, str], *, target: str) -> tuple[dict, dict]:
    root.mkdir(parents=True, exist_ok=True)
    schema = tool / "src/rust_frontend/vf_mir/vf_mir.capnp"
    original = {name: sha(fixture / name)
                for name in ("verified/lib.rs", "original/lib.rs")}
    rows = {}
    capture = load(a.proof_root / "research/challenge-8/overnight-sort4/capture.py",
                   "native_c4_graph")
    mir = {}
    for mode in ("normal", "readonly"):
        argv = [str(tool / "bin/vf-rust-mir-exporter"), "verified/lib.rs",
                "--sysroot=" + str(a.compiler_sysroot), "--edition", "2021"]
        if mode == "readonly":
            argv.append("--vf-rust-mir-exporter:preprocess-readonly")
        binary = root / f"{mode}-mir.bin"
        decoded = root / f"{mode}-mir.txt"
        rows[f"{mode}-export"] = stage(a, root, f"{mode}-export", argv, env,
                                       100, cwd=fixture, stdout=binary)
        if rows[f"{mode}-export"].get("exit") == 0:
            rows[f"{mode}-decode"] = stage(a, root, f"{mode}-decode",
                                           ["capnp", "decode", str(schema), "VfMir"],
                                           env, 60, cwd=fixture, stdin=binary,
                                           stdout=decoded)
            if rows[f"{mode}-decode"].get("exit") == 0:
                try:
                    defpath, record = capture.complete_function_record(
                        decoded.read_text(errors="replace"), target)
                    path = root / f"{mode}-{target}-full-mir.txt"
                    path.write_text(record)
                    mir[mode] = {"defpath": defpath, "sha256": sha(path),
                                 "bytes": path.stat().st_size}
                except Exception as exc:
                    mir[mode] = {"capture_error": str(exc), "proof_credit": False}
    rows["refinement"] = stage(a, root, "refinement",
                               [str(tool / "bin/refinement-checker"), "--rustc-args",
                                "--edition 2021", "original/lib.rs", "verified/lib.rs"],
                               env, 120, cwd=fixture)
    paired = all(rows.get(key, {}).get("exit") == 0 for key in
                 ("normal-export", "normal-decode", "readonly-export",
                  "readonly-decode", "refinement"))
    paired = paired and all(mode in mir and "sha256" in mir[mode]
                            for mode in ("normal", "readonly"))
    paired = paired and original == {name: sha(fixture / name) for name in original}
    support = {"paired_support_passed": paired, "source_pair_sha256": original,
               "full_mir": mir, "target": target, "proof_credit": False}
    save(root / "source-support.json", support)
    return rows, support

def verify_case(a, tool: Path, fixture: Path, root: Path,
                env: dict[str, str], *, target: str, ast: bool = True,
                require_paired_support: bool = False,
                required_full_mir: tuple[str, str] | None = None,
                verbosity: int | None = None) -> dict:
    input_sha = {name: sha(fixture / name)
                 for name in ("verified/lib.rs", "original/lib.rs")}
    rows, support = source_support(a, tool, fixture, root, env, target=target)
    if require_paired_support:
        need(support["paired_support_passed"],
             "native C1 bound paired MIR/refinement pre-verifier gate failed")
    if required_full_mir is not None:
        need(support["full_mir"].get("normal", {}).get("sha256") ==
             required_full_mir[0] and
             support["full_mir"].get("readonly", {}).get("sha256") ==
             required_full_mir[1] and
             support["source_pair_sha256"] == input_sha,
             "native C1 bound exact normal/readonly MIR pre-verifier gate failed")
    if verbosity is None:
        verbosity = 4 if C1_ZST_REPAIR_SESSION else 2
    command = [str(tool / "bin/verifast"), "-rustc_args", "--edition 2021",
               "-verbose", str(verbosity), "verified/lib.rs"]
    if ast:
        rows["proof-ast-diagnostic"] = stage(a, root, "proof-ast-diagnostic",
                                             [str(tool / "bin/verifast"),
                                              "-dump_ast_with_locs", "proof-ast.ml",
                                              "-rustc_args", "--edition 2021",
                                              "verified/lib.rs"], env, 90, cwd=fixture)
        ast_path = fixture / "proof-ast.ml"
        if ast_path.is_file():
            shutil.copy2(ast_path, root / "proof-ast.ml")
    rows["verification"] = stage(a, root, "verification", command, env,
                                  240, cwd=fixture)
    result = {"accepted": False, "actual_sort4_proved": False,
              "callable_summary": False, "support": support,
              "stages": {name: row.get("exit") for name, row in rows.items()},
              **first_failure(root, rows)}
    result["source_pair_immutable"] = input_sha == {
        name: sha(fixture / name) for name in input_sha}
    result["proof_ast_sha256"] = sha(root / "proof-ast.ml") if (
        root / "proof-ast.ml").is_file() else None
    result["classification"] = ("FRESH_FULL_VF0_CANDIDATE_RAW_REVIEW_REQUIRED"
                                if support["paired_support_passed"] and
                                rows["verification"].get("exit") == 0 and
                                result["first_causal_stage"] == "NONE_OBSERVED" and
                                result["source_pair_immutable"] else
                                "FIRST_CAUSAL_STAGE_DIAGNOSTIC")
    save(root / "case-result.json", result)
    return result

if __name__ == "__main__":
    main()
