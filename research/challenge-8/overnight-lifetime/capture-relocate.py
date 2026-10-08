#!/usr/bin/env python3
"""Hosted-only exact-source/MIR capture for TEST-only c1 local relocation."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time


HERE = Path(__file__).resolve().parent
SOURCE_SHA = "66bf5a6edc0188f560e72ac5a6a5636f2dcda47c65aa295ac21008fc7702e2d8"
ORIGINAL_SHA = "9b41aef507c8c61ec786bfacc8e12ede656286213e393a0d07436a8879dc569e"
TARGET_MIR_SHA = {
    "normal": "10356bf128753db09e17b968e859957121cb3f5a2684c3b608abd4152f150f76",
    "readonly": "9fdee7643ff66e8f3a12fc37b489100b7280ded0489a20ab1da11c67f24032c4",
}
PATCH_SHA = "e7189430eca9a48ed49d280131bd22987af8d05ed43a88f9c4a5c9767e57bb9e"
EXPORTER_SHA = "b00c75f43ab4d89bf85f5e62a5114a238b89b720d4598d90423347b9d97ac796"
REFINER_SHA = "b049c8d1b0bb350f77664e1c75c5a95966c5839984abc25c7cb629c0cba04d28"
SCHEMA_SHA = "f48fcf29b99717c2e0cb37d4708b47eccaa3270b999e4a84093e37fbd51b7469"


def load_cut_capture():
    path = HERE / "capture.py"
    spec = importlib.util.spec_from_file_location("cut_capture_for_relocation", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("CUT capture module missing")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool-home", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--deadline-epoch", type=float, default=time.time() + 600)
    args = parser.parse_args()
    cut = load_cut_capture()
    cut.need(os.getenv("GITHUB_ACTIONS") == "true" and
             os.getenv("RUNNER_ENVIRONMENT") == "github-hosted" and
             os.getenv("RUNNER_OS") == "Linux", "hosted GitHub Linux required")
    cut.need(not args.out.exists(), "fresh evidence directory required")
    patch = HERE / "verifast-cut-relocate-callback-TESTONLY.patch"
    cut.need(cut.sha(patch.read_bytes()) == PATCH_SHA,
             "reviewed relocation patch SHA missing or changed")
    cut.need(cut.sha((args.tool_home / "bin/vf-rust-mir-exporter").read_bytes()) == EXPORTER_SHA,
             "exporter pin changed")
    cut.need(cut.sha((args.tool_home / "bin/refinement-checker").read_bytes()) == REFINER_SHA,
             "refiner pin changed")
    schema = args.tool_home / "src/rust_frontend/vf_mir/vf_mir.capnp"
    cut.need(cut.sha(schema.read_bytes()) == SCHEMA_SHA, "schema pin changed")
    source = cut.select_case(cut.TEMPLATE.read_bytes(), "positive_f_bound")
    original = cut.strip_ghost(source)
    cut.need(cut.sha(source) == SOURCE_SHA and cut.sha(original) == ORIGINAL_SHA,
             "relocation source pair changed")
    args.out.mkdir(parents=True)
    root = args.out / "callback-positive"
    (root / "verified").mkdir(parents=True)
    (root / "original").mkdir()
    (root / "verified/lib.rs").write_bytes(source)
    (root / "original/lib.rs").write_bytes(original)
    source_hashes = {"verified/lib.rs": SOURCE_SHA, "original/lib.rs": ORIGINAL_SHA}
    env = os.environ.copy()
    env["RUSTUP_TOOLCHAIN"] = "nightly-2026-09-25"
    env["SORT4_STRICT_LFT_CUT"] = "1"
    env["SORT4_HRTB_OUTPUT"] = "1"
    env["SORT4_HRTB_OUTPUT_TARGETS"] = "callback_positive"
    env["PATH"] = str(args.tool_home / "bin") + os.pathsep + env.get("PATH", "")
    sysroot = subprocess.run(["rustc", "--print", "sysroot"], check=True,
                             env=env, capture_output=True, text=True).stdout.strip()

    def stage(name: str, argv: list[str], seconds: int,
              input_name: str | None = None, output_name: str | None = None,
              extra_env: dict[str, str] | None = None) -> dict:
        remaining = int(args.deadline_epoch - time.time()) - 15
        if remaining <= 0:
            return {"exit": None, "skipped": "deadline reserve"}
        selected_env = env.copy()
        selected_env.pop("SORT4_STRICT_LFT_RELOCATE", None)
        if extra_env:
            selected_env.update(extra_env)
        return cut.stage(root, name, argv, selected_env, source_hashes,
                         min(seconds, remaining),
                         root / input_name if input_name else None,
                         root / output_name if output_name else None)

    stages: dict[str, dict] = {}
    exporter = str(args.tool_home / "bin/vf-rust-mir-exporter")
    for mode, extra in (("normal", []),
                        ("readonly", ["--vf-rust-mir-exporter:preprocess-readonly"])):
        stages[f"{mode}-export"] = stage(
            f"{mode}-export", [exporter, "verified/lib.rs", f"--sysroot={sysroot}",
                                "--edition", "2021", "--crate-type", "lib", *extra],
            90, output_name=f"{mode}-mir.bin")
        if stages[f"{mode}-export"]["exit"] == 0:
            stages[f"{mode}-decode"] = stage(
                f"{mode}-decode", ["capnp", "decode", str(schema), "VfMir"],
                60, input_name=f"{mode}-mir.bin", output_name=f"{mode}-mir.txt")
        else:
            stages[f"{mode}-decode"] = {"exit": None, "skipped": "export failure"}
    stages["refinement"] = stage(
        "refinement", [str(args.tool_home / "bin/refinement-checker"),
                       "--rustc-args", "--edition 2021 --crate-type lib",
                       "original/lib.rs", "verified/lib.rs"], 90)
    body_hashes: dict[str, str | None] = {}
    for mode in ("normal", "readonly"):
        mir_path = root / f"{mode}-mir.txt"
        decoded = mir_path.read_text(errors="replace") if mir_path.exists() else ""
        body = cut.target_body(decoded, "callback_positive")
        body_hashes[mode] = cut.sha(body.encode()) if body else None
    admission = (all(stages[k]["exit"] == 0 for k in
                     ("normal-export", "normal-decode", "readonly-export",
                      "readonly-decode", "refinement")) and
                 body_hashes == TARGET_MIR_SHA)
    if admission:
        vf = [str(args.tool_home / "bin/verifast"),
              "-rustc_args", "--edition 2021 --crate-type lib",
              "-verbose", "1", "verified/lib.rs"]
        stages["baseline-verification"] = stage(
            "baseline-verification", vf, 180)
        stages["relocated-verification"] = stage(
            "relocated-verification", vf, 180,
            extra_env={"SORT4_STRICT_LFT_RELOCATE": "1"})
    else:
        stages["baseline-verification"] = {"exit": None, "skipped": "MIR admission failed"}
        stages["relocated-verification"] = {"exit": None, "skipped": "MIR admission failed"}
    base_log = (root / "baseline-verification.log").read_text(errors="replace") \
        if (root / "baseline-verification.log").exists() else ""
    moved_log = (root / "relocated-verification.log").read_text(errors="replace") \
        if (root / "relocated-verification.log").exists() else ""
    error_lines = lambda log: [line for line in log.splitlines()
                               if ": error:" in line or line.startswith("Fatal error:")]
    baseline_errors = error_lines(base_log)
    moved_errors = error_lines(moved_log)
    base_target_entries = base_log.count("Verifying function 'callback_positive'")
    moved_target_entries = moved_log.count("Verifying function 'callback_positive'")
    original_boundary = (stages["baseline-verification"]["exit"] in (1, 2) and
                         base_target_entries == 1 and len(baseline_errors) == 1 and
                         baseline_errors[0].startswith(
                             "verified/lib.rs(84,9-38): error: Strict lifetime binding "
                             "has unresolved inference in entry outer type"))
    moved_lines = [line for line in moved_log.splitlines()
                   if "STRICT-RELOCATE inner=" in line]
    all_moved = (len(moved_lines) == 6 and
                 all(f"inner=_{n} " in "\n".join(moved_lines) for n in range(27, 33)))
    one_insertion = moved_log.count(
        "STRICT-RELOCATE outer_removed=6 inner_insertions=1") == 1
    final_source_hashes = {path: cut.sha((root / path).read_bytes())
                           for path in source_hashes}
    final_source_exact = final_source_hashes == source_hashes and \
        cut.strip_ghost((root / "verified/lib.rs").read_bytes()) == \
        (root / "original/lib.rs").read_bytes()
    dead_code_lines = [line for line in moved_log.splitlines()
                       if "dead code" in line.lower()]
    zero_errors = (stages["relocated-verification"]["exit"] == 0 and
                   len(moved_errors) == 0 and not dead_code_lines and
                   len(re.findall(r"(?m)^0 errors found ", moved_log)) == 1)
    verified_leak_lines = [line for line in moved_log.splitlines()
                           if "verified/lib.rs(" in line and "Leak check." in line]
    if not admission or not original_boundary or not final_source_exact:
        classification = "INCONCLUSIVE_SETUP_OR_BASELINE"
    elif not all_moved or not one_insertion:
        classification = "INCONCLUSIVE_RELOCATION_GATE_OR_AST_TRACE"
    elif moved_target_entries != 1:
        classification = "INCONCLUSIVE_TARGET_PROOF_ENTRY"
    elif zero_errors and verified_leak_lines:
        classification = "FIXTURE_FULL_VF0_DIAGNOSTIC_ONLY"
    elif stages["relocated-verification"]["exit"] in (1, 2) and \
            len(moved_errors) == 1:
        classification = "NEXT_PROOF_BLOCKER_DIAGNOSTIC_ONLY"
    else:
        classification = "INCONCLUSIVE_RELOCATED_VERIFICATION"
    result = {
        "classification": classification,
        "accepted": False, "actual_sort4_proved": False,
        "source_hashes": source_hashes,
        "final_source_hashes": final_source_hashes,
        "source_pair_exact_at_end": final_source_exact,
        "body_hashes": body_hashes,
        "body_admission": admission, "baseline_first_boundary_preserved": original_boundary,
        "baseline_first_error": baseline_errors[0] if baseline_errors else None,
        "relocated_declaration_trace_six": all_moved,
        "relocated_exactly_one_inner_insertion": one_insertion,
        "stages": stages, "cut_verifier_sha256": cut.sha((args.tool_home / "bin/verifast").read_bytes()),
        "patch_sha256": PATCH_SHA,
        "baseline_proof_entries": base_target_entries,
        "relocated_proof_entries": moved_target_entries,
        "relocated_errors": moved_errors,
        "relocated_first_error": moved_errors[0] if moved_errors else None,
        "relocated_dead_code": dead_code_lines,
        "relocated_full_zero_errors": zero_errors,
        "relocated_leak_checks": moved_log.count("Leak check."),
        "relocated_verified_source_leak_checks": verified_leak_lines,
    }
    (args.out / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    cut.need(admission and original_boundary and final_source_exact and
             all_moved and one_insertion,
             "relocation fixture source/MIR or AST-trace admission failed")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"relocation diagnostic capture failed: {exc}", file=sys.stderr)
        raise
