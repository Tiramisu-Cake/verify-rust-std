#!/usr/bin/env python3
"""Cloud-only full source/MIR/refinement/proof capture for two false posts."""

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import time

CASES = {"normal-false": "positive_basic",
         "unwind-false": "positive_direct_unwind"}
SUPPORT = ("normal-export", "normal-decode", "readonly-export",
           "readonly-decode", "refinement")


def need(ok: bool, why: str) -> None:
    if not ok:
        raise RuntimeError(why)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def import_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, f"missing module {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(a) -> dict:
    need(os.getenv("SMALLSORT_EXECUTION_PROVIDER") == "cloud-build" and
         not os.getenv("GITHUB_ACTIONS"), "identified Cloud Build required")
    provider = import_module("strict_cut_cloud_provider", a.cloud_dir / "provider.py")
    need(provider.require_supported_provider()["provider"] == "cloud-build",
         "unsupported Cloud provider")
    cap = import_module("strict_cut_matrix_capture",
                        a.proof_root / "research/challenge-8/overnight-lifetime/capture.py")
    manifest = json.loads((a.evidence / "source-manifest.json").read_text())
    key = a.case
    case = CASES[key]
    row = manifest["cases"][key]
    need(row["parent_case"] == case and
         row["runtime_source_unchanged"] is True and
         row["only_target_post_changed"] is True,
         "false-post source manifest differs")
    root = a.evidence / "cases" / key
    hashes = {"verified/lib.rs": row["mutant_verified_sha256"],
              "original/lib.rs": row["original_sha256"]}
    need(all(sha(root / rel) == digest for rel, digest in hashes.items()),
         "false-post source changed before capture")
    schema = a.tool_home / "src/rust_frontend/vf_mir/vf_mir.capnp"
    need(schema.is_file(), "isolated source schema missing")
    env = os.environ.copy()
    env["RUSTUP_TOOLCHAIN"] = "nightly-2026-09-25"
    env["SORT4_STRICT_LFT_CUT"] = "1"
    for flag in ("SORT4_HRTB_OUTPUT", "SORT4_HRTB_OUTPUT_TARGETS",
                 "SORT4_STRICT_LFT_TRACE", "SORT4_STRICT_LFT_RELOCATE"):
        env.pop(flag, None)
    env["PATH"] = str(a.tool_home / "bin") + os.pathsep + env.get("PATH", "")
    actual_sysroot = subprocess.check_output(
        ("rustc", "--print", "sysroot"), env=env, text=True).strip()
    need(actual_sysroot == str(a.compiler_sysroot), "compiler sysroot differs")
    stages = {}

    def stage(name: str, argv: list[str], cap_seconds: int,
              stdin: str | None = None, stdout: str | None = None) -> None:
        remaining = int(a.deadline_epoch - time.time()) - 20
        if remaining <= 0:
            stages[name] = {"exit": None, "skipped": "deadline reserve"}
        else:
            stages[name] = cap.stage(
                root, name, argv, env, hashes, min(cap_seconds, remaining),
                root / stdin if stdin else None,
                root / stdout if stdout else None)

    exporter = str(a.tool_home / "bin/vf-rust-mir-exporter")
    for mode, extra in (("normal", []),
                        ("readonly", ["--vf-rust-mir-exporter:preprocess-readonly"])):
        stage(f"{mode}-export",
              [exporter, "verified/lib.rs", f"--sysroot={actual_sysroot}",
               "--edition", "2021", "--crate-type", "lib", *extra],
              90, stdout=f"{mode}-mir.bin")
        if stages[f"{mode}-export"].get("exit") == 0:
            stage(f"{mode}-decode",
                  ["capnp", "decode", str(schema), "VfMir"], 60,
                  stdin=f"{mode}-mir.bin", stdout=f"{mode}-mir.txt")
        else:
            stages[f"{mode}-decode"] = {"exit": None, "skipped": "export failure"}
    stage("full-verification", [str(a.tool_home / "bin/verifast"),
                                "-rustc_args", "--edition 2021 --crate-type lib",
                                "-verbose", "1", "verified/lib.rs"], 180)
    stage("refinement", [str(a.tool_home / "bin/refinement-checker"),
                         "--rustc-args", "--edition 2021 --crate-type lib",
                         "original/lib.rs", "verified/lib.rs"], 90)
    inventory = {}
    for mode in ("normal", "readonly"):
        path = root / f"{mode}-mir.txt"
        mir = path.read_text(errors="replace") if path.is_file() else ""
        names = re.findall(r'defPath = "([^"]+)"', mir)
        target = cap.target_body(mir, case) if mir else None
        inventory[mode] = {
            "full_decoded_bytes": path.stat().st_size if path.is_file() else 0,
            "full_decoded_sha256": sha(path) if path.is_file() else None,
            "mir_binary_sha256": sha(root / f"{mode}-mir.bin")
            if (root / f"{mode}-mir.bin").is_file() else None,
            "target_count": names.count(case),
            "same_unit_callee_count": names.count("cut_maybe_unwind"),
            "target_body_sha256": hashlib.sha256(target.encode()).hexdigest()
            if target else None,
            "source_path_present": target is not None and
            'localPath = "verified/lib.rs"' in target,
            "ghost_decl_block_present": target is not None and
            "ghostDeclBlocks = [" in target,
            "direct_continue": "unwindAction = (continue = void)" in mir,
        }
    log_path = root / "full-verification.log"
    log = log_path.read_text(errors="replace") if log_path.is_file() else ""
    errors = [line for line in log.splitlines()
              if ": error:" in line or line.startswith("Fatal error:")]
    target_header = f"Verifying function '{case}'"
    callee_header = "Verifying function 'cut_maybe_unwind'"
    result = {
        "classification": "FALSE_POST_CAPTURE_REVIEW_REQUIRED",
        "case": key, "target_function": case,
        "source_hashes": hashes,
        "stages": stages,
        "decoded_body_inventory": inventory,
        "support_stages_complete": all(stages.get(name, {}).get("exit") == 0
                                       for name in SUPPORT),
        "target_headers": log.count(target_header),
        "callee_headers": log.count(callee_header),
        "callee_before_target": (log.count(callee_header) == 1 and
                                 log.count(target_header) == 1 and
                                 log.index(callee_header) < log.index(target_header))
        if key == "unwind-false" else None,
        "full_error_lines": errors,
        "first_error": errors[0] if errors else None,
        "accepted": False, "actual_sort4_accepted": False,
    }
    (root / "capture-result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--case", choices=CASES, required=True)
    for key in ("tool-home", "proof-root", "cloud-dir", "evidence",
                "compiler-sysroot"):
        p.add_argument("--" + key, type=Path, required=True)
    p.add_argument("--deadline-epoch", type=int, required=True)
    run(p.parse_args())


if __name__ == "__main__":
    main()
