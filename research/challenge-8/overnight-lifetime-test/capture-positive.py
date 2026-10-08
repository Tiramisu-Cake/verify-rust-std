#!/usr/bin/env python3
"""Hosted-only lawful positive for a later TEST-only strict-cut metadata probe.

This script never installs a verifier patch. It runs on the already separate
CUT console and does not count as an actual Rust target proof.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "positive.rs"
SOURCE_SHA256 = "f4f2c6e75f35dc25bf2d8021669624ceb20caa0286417acf86bf28e1d540364d"
CUT_PATCH_SHA256 = "d557082b0c17771acd7386ad6caca7bc139877cf1ca513d9570da210b1b542d8"
TARGET = "lifetime_test_positive"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def need(value: bool, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def load_cut_capture():
    path = HERE.parent / "overnight-lifetime" / "capture.py"
    need(path.is_file(), "CUT capture helper missing")
    spec = importlib.util.spec_from_file_location("overnight_cut_capture", path)
    need(spec is not None and spec.loader is not None, "CUT capture import unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool-home", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--deadline-epoch", type=float, default=time.time() + 600)
    args = parser.parse_args()
    need(os.getenv("GITHUB_ACTIONS") == "true" and
         os.getenv("RUNNER_ENVIRONMENT") == "github-hosted" and
         os.getenv("RUNNER_OS") == "Linux", "hosted GitHub Linux required")
    need(not args.out.exists(), "fresh evidence directory required")
    need(args.tool_home.is_dir(), "CUT console home missing")
    cut, cut_path = load_cut_capture()
    cut_patch = HERE.parent / "overnight-lifetime" / "verifast-strict-lft-cut-26.10.patch"
    need(sha(cut_patch.read_bytes()) == CUT_PATCH_SHA256, "CUT patch bytes changed")
    source = SOURCE.read_bytes()
    need(sha(source) == SOURCE_SHA256, "lawful test source changed")
    need(source.count(b"pub unsafe fn lifetime_test_positive<T>()") == 1 and
         source.count(b"pub unsafe fn ") == 1 and
         source.count(b"let probe = 0;") == 1 and
         source.count(b"let_lft 'cmp = cmp_k;") == 1 and
         source.count(b"close live::<T>();") == 1 and
         source.count(b"open live::<T>();") == 1 and
         source.count(b"end_lft_binding::<'cmp>();") == 1 and
         source.count(b"end_lifetime(cmp_k);") == 1,
         "lawful positive source inventory changed")
    for relative in ("bin/verifast", "bin/vf-rust-mir-exporter",
                     "bin/refinement-checker", "src/rust_frontend/vf_mir/vf_mir.capnp"):
        need((args.tool_home / relative).is_file(), f"CUT console component missing: {relative}")
    args.out.mkdir(parents=True)
    root = args.out / "positive"
    (root / "verified").mkdir(parents=True)
    (root / "original").mkdir()
    original = cut.strip_ghost(source)
    need(original != source and cut.strip_ghost(source) == original,
         "ghost strip identity failed")
    (root / "verified/lib.rs").write_bytes(source)
    (root / "original/lib.rs").write_bytes(original)
    source_hashes = {"verified/lib.rs": sha(source), "original/lib.rs": sha(original)}
    env = os.environ.copy()
    env["RUSTUP_TOOLCHAIN"] = "nightly-2026-09-25"
    env["SORT4_STRICT_LFT_CUT"] = "1"
    env.pop("SORT4_STRICT_LFT_TEST", None)
    env.pop("SORT4_HRTB_OUTPUT", None)
    env.pop("SORT4_HRTB_OUTPUT_TARGETS", None)
    env["PATH"] = str(args.tool_home / "bin") + os.pathsep + env.get("PATH", "")
    compiler = subprocess.run(["rustc", "--print", "sysroot"], env=env,
                              check=True, capture_output=True, text=True)
    sysroot = compiler.stdout.strip()
    schema = args.tool_home / "src/rust_frontend/vf_mir/vf_mir.capnp"

    def run(name: str, command: list[str], seconds: int,
            input_name: str | None = None, output_name: str | None = None) -> dict:
        remaining = int(args.deadline_epoch - time.time()) - 15
        if remaining <= 0:
            return {"exit": None, "skipped": "deadline reserve"}
        return cut.stage(root, name, command, env, source_hashes,
                         min(seconds, remaining),
                         root / input_name if input_name else None,
                         root / output_name if output_name else None)

    stages: dict[str, dict] = {}
    exporter = str(args.tool_home / "bin/vf-rust-mir-exporter")
    for mode, extra in (("normal", []),
                        ("readonly", ["--vf-rust-mir-exporter:preprocess-readonly"])):
        stages[f"{mode}-export"] = run(
            f"{mode}-export", [exporter, "verified/lib.rs", f"--sysroot={sysroot}",
                                "--edition", "2021", "--crate-type", "lib", *extra],
            90, output_name=f"{mode}-mir.bin")
        if stages[f"{mode}-export"]["exit"] == 0:
            stages[f"{mode}-decode"] = run(
                f"{mode}-decode", ["capnp", "decode", str(schema), "VfMir"],
                60, input_name=f"{mode}-mir.bin", output_name=f"{mode}-mir.txt")
        else:
            stages[f"{mode}-decode"] = {"exit": None, "skipped": "export failure"}
    stages["full-verification"] = run(
        "full-verification", [str(args.tool_home / "bin/verifast"),
                              "-rustc_args", "--edition 2021 --crate-type lib",
                              "-verbose", "2", "verified/lib.rs"], 180)
    stages["refinement"] = run(
        "refinement", [str(args.tool_home / "bin/refinement-checker"),
                       "--rustc-args", "--edition 2021 --crate-type lib",
                       "original/lib.rs", "verified/lib.rs"], 90)
    decoded = {}
    for mode in ("normal", "readonly"):
        path = root / f"{mode}-mir.txt"
        mir = path.read_text(errors="replace") if path.exists() else ""
        body = cut.target_body(mir, TARGET)
        decoded[mode] = {
            "full_sha256": sha(path.read_bytes()) if path.exists() else None,
            "target_count": re.findall(r'defPath = "([^"]+)"', mir).count(TARGET),
            "target_body_sha256": sha(body.encode()) if body else None,
            "target_source_path_present": body is not None and
                                          'localPath = "verified/lib.rs"' in body,
            "ghost_decl_block_present": body is not None and
                                        "ghostDeclBlocks = [" in body,
            "source_marker_present": body is not None and
                                     "end_lft_binding" in body,
        }
    log_path = root / "full-verification.log"
    log = log_path.read_text(errors="replace") if log_path.exists() else ""
    stages_ok = all(stages[k]["exit"] == 0 for k in
                    ("normal-export", "normal-decode", "readonly-export",
                     "readonly-decode", "full-verification", "refinement"))
    inventory_ok = all(row["target_count"] == 1 and
                       row["target_body_sha256"] is not None and
                       row["target_source_path_present"] and
                       row["ghost_decl_block_present"] and
                       row["source_marker_present"]
                       for row in decoded.values())
    proof_ok = (stages_ok and inventory_ok and
                log.count(f"Verifying function '{TARGET}'") == 1 and
                "0 errors found" in log and "Leak check." in log and
                not any(": error:" in line or ": dead code" in line
                        for line in log.splitlines()))
    summary = {
        "classification": "LAWFUL_TEST_SOURCE_CANDIDATE" if proof_ok else "INCONCLUSIVE",
        "accepted": False, "actual_sort4_proved": False,
        "source_sha256": SOURCE_SHA256, "source_hashes": source_hashes,
        "cut_patch_sha256": CUT_PATCH_SHA256,
        "cut_capture_sha256": sha(cut_path.read_bytes()),
        "cut_verifier_sha256": sha((args.tool_home / "bin/verifast").read_bytes()),
        "exporter_sha256": sha((args.tool_home / "bin/vf-rust-mir-exporter").read_bytes()),
        "refiner_sha256": sha((args.tool_home / "bin/refinement-checker").read_bytes()),
        "schema_sha256": sha(schema.read_bytes()),
        "test_injection_enabled": False, "stages": stages, "decoded": decoded,
        "full_proof_target_headers": log.count(f"Verifying function '{TARGET}'"),
        "full_error_lines": [line for line in log.splitlines()
                             if ": error:" in line or line.startswith("Fatal error:")],
        "full_dead_code_lines": [line for line in log.splitlines()
                                 if ": dead code" in line],
    }
    (args.out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    need(proof_ok, "lawful test source is not a proven positive")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"lawful CUT test-source capture failed: {exc}", file=sys.stderr)
        raise
