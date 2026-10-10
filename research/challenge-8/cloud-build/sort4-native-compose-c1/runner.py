#!/usr/bin/env python3
"""Cloud-only initial capture of native-to-c1 source, MIR and verifier boundary.

The first profile intentionally does not admit the new unwind marker. It
records the exact frontend blocker before a separately reviewed tool overlay.
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


CRITICAL = (
    "src/verifast.ml",
    "src/rust_frontend/vf_mir_translator/vf_mir_translator.ml",
    "src/rust_frontend/vf_mir_translator/rust_parser.ml",
    "src/rust_frontend/vf_mir/vf_mir.capnp",
    "bin/verifast",
    "bin/vf-rust-mir-exporter",
    "bin/refinement-checker",
)


def need(ok: bool, why: str) -> None:
    if not ok:
        raise RuntimeError(why)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, sort_keys=True, indent=2) + "\n")


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, "source module unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def snapshot(a: argparse.Namespace) -> dict:
    root = a.production_source
    return {
        "base_commit": subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip(),
        "critical": {name: sha(root / name) for name in CRITICAL},
        "effective_rsspec": {
            str(path.relative_to(root)): sha(path)
            for path in sorted((root / "bin/rust").rglob("*.rsspec"))},
        "production_applied_patch_sha256": sha(a.production_applied_patch),
        "proof_sha": os.environ["PROOF_SHA"],
        "infra_sha": os.environ["INFRA_SHA"],
        "profile": "SORT4_NATIVE_COMPOSE_C1_BASELINE_CAPTURE_NO_NEW_OVERLAY",
        "accepted": False,
    }


def stage(a: argparse.Namespace, root: Path, name: str, argv: list[str],
          env: dict[str, str], cap: int, *, stdin: str | None = None,
          stdout: str | None = None) -> dict:
    seconds = min(cap, a.deadline_epoch - int(time.time()) - 15)
    result = {"name": name, "argv": argv, "state": "RUNNING",
              "started_epoch": int(time.time()), "proof_verdict": None}
    write(root / (name + "-stage.json"), result)
    write(a.evidence / "stage-progress.json", result)
    if seconds <= 0:
        result.update(state="NOT_RUN", exit=None, reason="deadline reserve")
        write(root / (name + "-stage.json"), result)
        return result
    output = root / (stdout or name + ".log")
    error = root / (name + "-stderr.log") if stdout else output
    with output.open("wb") as out:
        err = error.open("wb") if error != output else subprocess.STDOUT
        inp = (root / stdin).open("rb") if stdin else open(os.devnull, "rb")
        try:
            code = subprocess.run(
                ["/usr/bin/time", "-v", "-o", str(root / (name + "-resources.txt")),
                 "timeout", "--signal=TERM", "--kill-after=10s", str(seconds) + "s",
                 *argv], cwd=root, env=env, stdin=inp, stdout=out, stderr=err,
                check=False).returncode
        finally:
            inp.close()
            if error != output:
                err.close()
    result.update(state="TERMINAL", exit=code, finished_epoch=int(time.time()),
                  stdout=output.name, stderr=error.name,
                  stdout_sha256=sha(output), stderr_sha256=sha(error))
    (root / (name + "-exit-code.txt")).write_text(str(code) + "\n")
    write(root / (name + "-stage.json"), result)
    write(a.evidence / "stage-progress.json", result)
    if stdout is None:
        print(output.read_text(errors="replace"), flush=True)
    return result


def run(a: argparse.Namespace) -> dict:
    need(os.environ.get("SMALLSORT_EXECUTION_PROVIDER") == "cloud-build" and
         os.environ.get("LANE") == "o26-sort4-caller-entry" and
         not os.environ.get("GITHUB_ACTIONS"), "Cloud-only caller-entry lane")
    for key in ("production_source", "production_applied_patch", "stock_home",
                "compiler_sysroot", "evidence", "proof_root", "work_root", "cloud_dir"):
        need(str(getattr(a, key)).startswith("/workspace/"),
             f"{key} must be under /workspace")
    need(not a.evidence.exists(), "fresh composition evidence directory required")
    a.evidence.mkdir(parents=True)
    before = snapshot(a)
    write(a.evidence / "tool-snapshot.json", before)
    prep = load(a.proof_root / "research/challenge-8/cloud-build/sort4-native-compose-c1/prepare.py",
                "compose_prepare")
    capture = load(a.proof_root / "research/challenge-8/overnight-sort4/capture.py",
                   "compose_capture")
    root = a.evidence / "cases/positive"
    root.mkdir(parents=True)
    fixture = root / "fixture"
    cert = prep.prepare(a.proof_root, fixture, "positive")
    write(root / "source-certificate.json", cert)
    original_hashes = {name: sha(fixture / name)
                       for name in ("original/lib.rs", "verified/lib.rs")}
    write(root / "raw-input-pins.json", {
        "proof_sha": os.environ["PROOF_SHA"],
        "infra_sha": os.environ["INFRA_SHA"],
        "source_hashes": original_hashes,
        "bounded_helper_only": True,
        "actual_sort4_summary_used": False,
    })
    deps = a.work_root / "vfdeps-adf88dc"
    env = os.environ.copy()
    env["PATH"] = str(a.production_source / "bin") + ":" + str(deps / "bin") + ":" + env.get("PATH", "")
    env["LD_LIBRARY_PATH"] = ":".join(
        [str(a.compiler_sysroot / "lib"), str(a.production_source / "bin"),
         str(deps / "lib"), env.get("LD_LIBRARY_PATH", "")])
    env["CAPNP_INC_DIR"] = str(deps / "include")
    env["RUSTUP_TOOLCHAIN"] = "nightly-2026-09-25"
    # The first run is an exact baseline capture. Do not accidentally inherit
    # old bounded-sort4, C2, callback, or source-projection semantic opt-ins.
    for name in list(env):
        if name.startswith(("SORT4_", "O26_WITH_")):
            env.pop(name)
    exporter = str(a.production_source / "bin/vf-rust-mir-exporter")
    verifier = str(a.production_source / "bin/verifast")
    refiner = str(a.production_source / "bin/refinement-checker")
    schema = a.production_source / "src/rust_frontend/vf_mir/vf_mir.capnp"
    stages: dict[str, dict] = {}
    mir: dict[str, dict] = {}
    for mode in ("normal", "readonly"):
        argv = [exporter, "verified/lib.rs", "--sysroot=" + str(a.compiler_sysroot),
                "--edition", "2021"]
        if mode == "readonly":
            argv.append("--vf-rust-mir-exporter:preprocess-readonly")
        stages[mode + "-export"] = stage(a, fixture, mode + "-export", argv,
                                          env, 100, stdout=mode + "-mir.bin")
        if stages[mode + "-export"]["exit"] == 0:
            stages[mode + "-decode"] = stage(
                a, fixture, mode + "-decode", ["capnp", "decode", str(schema), "VfMir"],
                env, 60, stdin=mode + "-mir.bin", stdout=mode + "-mir.txt")
            if stages[mode + "-decode"]["exit"] == 0:
                data = (fixture / (mode + "-mir.txt")).read_text(errors="replace")
                for function in ("c1_source_prefix", "small_sort_general_with_scratch"):
                    defpath, record = capture.complete_function_record(data, function)
                    target = root / (mode + "-" + function + "-full-mir.txt")
                    target.write_text(record)
                    mir[mode + ":" + function] = {
                        "defpath": defpath, "record_sha256": sha(target),
                        "FnMut_call_mut_occurrences": record.count("FnMut::call_mut"),
                        "direct_continue_occurrences": record.count("Continue"),
                        "record_bytes": len(record.encode()),
                    }
    stages["refinement"] = stage(
        a, fixture, "refinement",
        [refiner, "--rustc-args", "--edition 2021", "original/lib.rs", "verified/lib.rs"],
        env, 120)
    support = all(stages.get(name, {}).get("exit") == 0 for name in
                  ("normal-export", "normal-decode", "readonly-export",
                   "readonly-decode", "refinement"))
    support = support and all(sha(fixture / name) == digest
                              for name, digest in original_hashes.items())
    write(root / "source-mir-admission.json", {
        "support_passed": support, "full_function_mir": mir,
        "first_c1_source_line": cert["first_c1_source_line"],
        "compiler_stage_exits": {name: item.get("exit") for name, item in stages.items()},
        "actual_caller_cfg_proved": False,
    })
    if support:
        stages["verification"] = stage(
            a, fixture, "verification",
            [verifier, "-rustc_args", "--edition 2021", "-verbose", "2",
             "verified/lib.rs"], env, 240)
    log = (fixture / "verification.log").read_text(errors="replace") if (fixture / "verification.log").is_file() else ""
    errors = [line for line in log.splitlines()
              if ": error:" in line or line.startswith("Fatal error:") or
              re.search(r"\): dead code$", line)]
    helper_entry = log.find("Verifying function 'c1_source_prefix'")
    native_entry = log.find("Verifying function 'small_sort_general_with_scratch'")
    verifier_exit = stages.get("verification", {}).get("exit")
    full_vf0 = (support and verifier_exit == 0 and not errors and
                re.search(r"0 errors found \(\d+ statements verified\)", log) is not None and
                helper_entry >= 0 and native_entry > helper_entry and
                log.count("Leak check.") >= 2)
    result = {
        "classification": "CANDIDATE_VF0_REQUIRES_RAW_REVIEW" if full_vf0 else
                          "SOURCE_MIR_CAPTURE_FRONTEND_BOUNDARY" if support else
                          "SETUP_OR_SOURCE_MIR_BLOCKER",
        "accepted": False, "case": "positive", "proof_sha": os.environ["PROOF_SHA"],
        "infra_sha": os.environ["INFRA_SHA"], "support_passed": support,
        "new_composition_proof_accepted": False,
        "diagnostic_complete": bool(support and
                                    stages.get("verification", {}).get("state") == "TERMINAL"),
        "candidate_vf0": full_vf0, "verifier_exit": verifier_exit,
        "first_error": errors[0] if errors else None,
        "all_errors": errors, "helper_entry_offset": helper_entry,
        "native_entry_offset": native_entry,
        "source_mir": mir,
        "stages": {name: item.get("exit") for name, item in stages.items()},
        "full_actual_caller_proved": False,
        "actual_sort4_proved": False,
    }
    write(root / "case-result.json", result)
    write(a.evidence / "diagnostic-audit.json", result)
    need(snapshot(a) == before, "production tool changed during composition capture")
    print(json.dumps(result, sort_keys=True), flush=True)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    for name in ("production-source", "production-applied-patch", "stock-home",
                 "compiler-sysroot", "evidence", "proof-root", "work-root", "cloud-dir"):
        parser.add_argument("--" + name, required=True, type=Path)
    parser.add_argument("--deadline-epoch", required=True, type=int)
    run(parser.parse_args())


if __name__ == "__main__":
    main()
