#!/usr/bin/env python3
"""Cloud-only source-admitted compile/run for the saved callback frame probe."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import re
import runpy
import shutil
import subprocess
import sys


EXPECTED_SOURCE_SHA256 = "85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1"
EXPECTED_SOURCE_BLOB = "40939f922bcb6fdc7ee0d30427fa861827043827"
PROBE_REL = pathlib.Path("research/challenge-8/merge/overnight/callback-destination-frame-probe.rs")
SOURCE_REL = pathlib.Path("library/core/src/slice/sort/shared/smallsort.rs")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def extract_merge_up(data: bytes) -> bytes:
    marker = b"unsafe fn merge_up<T, F: FnMut(&T, &T) -> bool>("
    if data.count(marker) != 1:
        raise ValueError("expected exactly one merge_up definition")
    start = data.index(marker)
    end = re.search(rb"(?m)^}\r?\n", data[start:])
    if end is None:
        raise ValueError("could not locate complete merge_up body")
    return data[start : start + end.end()]


def run_stage(command: list[str], timeout: int, log: pathlib.Path, cwd: pathlib.Path) -> int:
    try:
        result = subprocess.run(command, cwd=cwd, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=timeout,
                                check=False)
        log.write_bytes(result.stdout)
        return result.returncode
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout or b""
        if isinstance(output, str):
            output = output.encode()
        log.write_bytes(output + b"\nSTAGE_TIMEOUT\n")
        return 124
    except OSError as exc:
        log.write_text(f"STAGE_START_ERROR: {exc}\n")
        return 127


def main() -> int:
    if os.environ.get("SMALLSORT_EXECUTION_PROVIDER") != "cloud-build":
        raise SystemExit("runtime probe requires identified Cloud Build")
    provider_file = os.environ.get("SMALLSORT_PROVIDER_FILE", "")
    if not provider_file:
        raise SystemExit("runtime probe provider helper is missing")
    identity = runpy.run_path(provider_file)["require_supported_provider"]()
    if identity.get("provider") != "cloud-build":
        raise SystemExit("runtime probe requires Cloud Build identity")
    parser = argparse.ArgumentParser()
    parser.add_argument("--proof-root", type=pathlib.Path, required=True)
    parser.add_argument("--evidence-root", type=pathlib.Path, required=True)
    parser.add_argument("--work-root", type=pathlib.Path, required=True)
    args = parser.parse_args()
    proof = args.proof_root
    evidence = args.evidence_root / "allprooflogs"
    case_dir = evidence / "cases" / "callback-destination-frame-probe"
    scratch = args.work_root / "callback-destination-frame-probe"
    if case_dir.exists() or scratch.exists():
        raise SystemExit("refusing to reuse callback destination frame evidence/work")
    case_dir.mkdir(parents=True)
    scratch.mkdir(parents=True)
    probe = proof / PROBE_REL
    source = proof / SOURCE_REL
    copied_probe = case_dir / PROBE_REL.name
    shutil.copyfile(probe, copied_probe)
    probe_bytes = probe.read_bytes()
    source_bytes = source.read_bytes()
    source_sha = sha256(source_bytes)
    source_blob = git_blob(source_bytes)
    stage_prefix = evidence / "callback-destination-frame"

    admission = {
        "probe_path": PROBE_REL.as_posix(),
        "probe_sha256": sha256(probe_bytes),
        "copied_probe_sha256": sha256(copied_probe.read_bytes()),
        "source_path": SOURCE_REL.as_posix(),
        "source_sha256": source_sha,
        "expected_source_sha256": EXPECTED_SOURCE_SHA256,
        "source_git_blob": source_blob,
        "expected_source_git_blob": EXPECTED_SOURCE_BLOB,
        "source_pin_matches": source_sha == EXPECTED_SOURCE_SHA256 and source_blob == EXPECTED_SOURCE_BLOB,
        "whole_merge_up_byte_equal": False,
        "admitted": False,
    }
    try:
        actual_helper = extract_merge_up(source_bytes)
        copied_helper = extract_merge_up(probe_bytes)
        admission.update({
            "actual_merge_up_sha256": sha256(actual_helper),
            "copied_merge_up_sha256": sha256(copied_helper),
            "whole_merge_up_byte_equal": actual_helper == copied_helper,
        })
    except ValueError as exc:
        admission["source_admission_error"] = str(exc)
    admission["admitted"] = bool(admission["source_pin_matches"] and
                                  admission["whole_merge_up_byte_equal"])
    (case_dir / "source-admission.json").write_text(json.dumps(admission, sort_keys=True, indent=2) + "\n")
    (stage_prefix.parent / "callback-destination-frame-source-admission.log").write_text(
        json.dumps(admission, sort_keys=True, indent=2) + "\n")
    (stage_prefix.parent / "callback-destination-frame-source-admission-exit-code.txt").write_text(
        "0\n" if admission["admitted"] else "1\n")

    rustc = shutil.which("rustc") or "rustc"
    try:
        version = subprocess.run([rustc, "--version", "--verbose"], stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT, check=False, timeout=30)
        version_bytes, version_code = version.stdout, version.returncode
    except subprocess.TimeoutExpired as exc:
        raw = exc.stdout or b""
        version_bytes = raw.encode() if isinstance(raw, str) else raw
        version_code = 124
        version_bytes += b"\nVERSION_STAGE_TIMEOUT\n"
    (case_dir / "rustc-version.txt").write_bytes(version_bytes)
    (stage_prefix.parent / "callback-destination-frame-compiler-version.log").write_bytes(version_bytes)
    (stage_prefix.parent / "callback-destination-frame-compiler-version-exit-code.txt").write_text(
        f"{version_code}\n")
    version_text = version_bytes.decode("utf-8", errors="replace")
    compiler = {line.split(": ", 1)[0]: line.split(": ", 1)[1]
                for line in version_text.splitlines() if ": " in line}
    compiler_sha = sha256(version_bytes)
    try:
        sysroot_result = subprocess.run([rustc, "--print", "sysroot"], stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT, check=False, timeout=30)
        sysroot_bytes, sysroot_code = sysroot_result.stdout, sysroot_result.returncode
    except subprocess.TimeoutExpired as exc:
        raw = exc.stdout or b""
        sysroot_bytes = raw.encode() if isinstance(raw, str) else raw
        sysroot_code = 124
    (stage_prefix.parent / "callback-destination-frame-compiler-sysroot.log").write_bytes(sysroot_bytes)
    (stage_prefix.parent / "callback-destination-frame-compiler-sysroot-exit-code.txt").write_text(
        f"{sysroot_code}\n")
    sysroot_text = sysroot_bytes.decode("utf-8", errors="replace").strip()
    compiler_binary = (pathlib.Path(sysroot_text) / "bin/rustc").resolve() if sysroot_code == 0 else None
    compiler_binary_sha = (sha256(compiler_binary.read_bytes())
                           if compiler_binary is not None and compiler_binary.is_file() else None)
    result = {
        "classification": "SOURCE_ADMISSION_FAILED" if not admission["admitted"] else "INCONCLUSIVE_COMPILER_VERSION_FAILURE",
        "source_admitted": admission["admitted"],
        "compile_exit_code": None,
        "run_exit_code": None,
        "compiler_version_sha256": compiler_sha,
        "compiler_commit": compiler.get("commit-hash"),
        "compiler_host": compiler.get("host"),
        "compiler_binary_path": str(compiler_binary) if compiler_binary is not None else None,
        "compiler_binary_sha256": compiler_binary_sha,
        "compiler_sysroot_exit_code": sysroot_code,
        "binary_sha256": None,
        "compile_flags": ["--edition=2021", "-C", "panic=unwind"],
        "runtime_observation_only": True,
        "not_verifast_theorem_or_caller_counterexample": True,
        "expected_runtime_assertion": "catch_unwind observes panic and output equals 9",
    }
    compile_code = run_code = None
    compiler_matches = (compiler.get("commit-hash") == "f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f" and
                        compiler.get("host") == "x86_64-unknown-linux-gnu" and
                        compiler_binary_sha is not None)
    if admission["admitted"] and version_code == 0 and compiler_matches:
        binary = scratch / "callback-destination-frame-probe"
        compile_code = run_stage(
            [rustc, "--edition=2021", "-C", "panic=unwind", str(copied_probe), "-o", str(binary)],
            90, stage_prefix.parent / "callback-destination-frame-compile.log", proof)
        if compile_code == 0 and binary.is_file():
            result["binary_sha256"] = sha256(binary.read_bytes())
            run_code = run_stage([str(binary)], 30,
                                 stage_prefix.parent / "callback-destination-frame-run.log", proof)
            result["classification"] = (
                "OBSERVED_DESTINATION_FRAME_CHANGE_ON_CALLBACK_UNWIND"
                if run_code == 0 else "INCONCLUSIVE_RUNTIME_FAILURE")
        else:
            result["classification"] = "INCONCLUSIVE_COMPILE_FAILURE"
    else:
        if admission["admitted"] and version_code == 0:
            result["classification"] = (
                "INCONCLUSIVE_COMPILER_PIN_MISMATCH"
                if (compiler.get("commit-hash") != "f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f" or
                    compiler.get("host") != "x86_64-unknown-linux-gnu")
                else "INCONCLUSIVE_COMPILER_BINARY_UNHASHED")
        (stage_prefix.parent / "callback-destination-frame-compile.log").write_text(
            "SKIPPED: source admission, compiler version, or compiler pin gate failed\n")
        (stage_prefix.parent / "callback-destination-frame-run.log").write_text("SKIPPED\n")
    compile_code = compile_code if compile_code is not None else 125
    run_code = run_code if run_code is not None else 125
    (stage_prefix.parent / "callback-destination-frame-compile-exit-code.txt").write_text(
        f"{compile_code}\n")
    (stage_prefix.parent / "callback-destination-frame-run-exit-code.txt").write_text(
        f"{run_code}\n")
    result["compile_exit_code"] = compile_code
    result["run_exit_code"] = run_code
    result["rustc_version_command_exit_code"] = version_code
    (case_dir / "runtime-observation.json").write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    # This code reports whether the evidence row was collected; the probe's
    # compile/run classification remains independent and is recorded above.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
