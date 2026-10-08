#!/usr/bin/env python3
"""Hosted full NORMAL/readonly MIR calibration for six-body actual nested Drop."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"missing actual nested capture module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PREP = load(HERE / "prepare-actual-nested-drop.py",
            "actual_nested_six_body_source")
CAPTURE = load(REPO / "research/challenge-8/overnight-helper/"
               "check-actual-owner-projection.py",
               "actual_nested_outer_mir_capture")
LINK = PREP.OWNER.LINK
METHOD = "sort4_checked_generic_drop"
NESTED = "<select_unpredictable::DropOnPanic<T> as std::ops::Drop>::drop"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def capture_case(case: Path, source: dict, args) -> dict:
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
    complete_export = all(stages.get(k, {}).get("exit") == 0 for k in (
        "normal-export", "normal-decode", "readonly-export", "readonly-decode"))
    if complete_export:
        stages["refinement"] = LINK.stage(case, "refinement", [
            str(args.tool_home / "bin/refinement-checker"), "--rustc-args",
            "--edition 2021", "original/lib.rs", "verified/lib.rs"], args,
            cap_seconds=70)
        if (args.fingerprint_probe and
                stages["refinement"]["exit"] == 0):
            mode = str(len(source["source_order"]))
            PREP.require(mode in ("6", "7"),
                         "diagnostic probe only covers six/seven bodies")
            probe_env = {
                "SORT4_NESTED_FINGERPRINT_MODE": mode,
                "SORT4_NESTED_FINGERPRINT_EVIDENCE_DIR":
                    str(case.resolve()),
                "SORT4_NESTED_FINGERPRINT_SOURCE_SHA256":
                    source["verified_sha256"],
            }
            before_env = {key: os.environ.get(key)
                          for key in probe_env}
            try:
                os.environ.update(probe_env)
                stages["fingerprint-probe"] = LINK.stage(
                    case, "fingerprint-probe", [
                        str(args.tool_home / "bin/verifast"), "-rustc_args",
                        "--edition 2021", "-verbose", "1",
                        "verified/lib.rs"], args, gates=False,
                    pointer_drop=False, cap_seconds=100)
            finally:
                for key, value in before_env.items():
                    if value is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = value
        if args.first_barrier:
            stages["first-barrier"] = LINK.stage(case, "first-barrier", [
                str(args.tool_home / "bin/verifast"), "-rustc_args",
                "--edition 2021", "-verbose", "1", "verified/lib.rs"],
                args, gates=False, pointer_drop=False, cap_seconds=100)
    graph = CAPTURE.capture_graph(case, stages) if complete_export else {}
    full = {}
    expected = source["source_order"]
    for mode in ("normal", "readonly"):
        if stages.get(f"{mode}-decode", {}).get("exit") != 0:
            continue
        decoded = (case / f"{mode}-mir.txt").read_text(errors="strict")
        order = []
        for name in expected:
            marker = f'defPath = "{name}"'
            PREP.require(decoded.count(marker) == 1,
                         f"{mode} exact body count: {name}")
            order.append(decoded.index(marker))
        method_name, method_body = CAPTURE.A1.complete_function_record(
            decoded, METHOD)
        (case / f"{mode}-generic-method-full-mir.txt").write_text(method_body)
        full[mode] = {
            "exact_body_order": order == sorted(order),
            "expected_defpaths": expected,
            "generic_method_defpath": method_name,
            "generic_method_full_mir_sha256": sha(method_body.encode()),
            "nested_drop_ghost_call_count": graph.get(mode, {}).get(
                "nested_drop_ghost_call_count"),
            "outer_full_mir_sha256": graph.get(mode, {}).get(
                "outer_full_mir_sha256"),
            "nested_full_mir_sha256": graph.get(mode, {}).get(
                "nested_drop_full_mir_sha256"),
            "complete_decoded_text_sha256": sha(decoded.encode()),
        }
    refine = stages.get("refinement", {}).get("exit") == 0
    intact = all(stage.get("source_unchanged") is True
                 for stage in stages.values() if stage.get("status") == "RAN")
    first_log = (case / "first-barrier.log")
    first_text = first_log.read_text(errors="replace") if first_log.is_file() else ""
    probe_files = {}
    if args.fingerprint_probe:
        mode = str(len(source["source_order"]))
        for label in ["unit"] + [f"body-{n}" for n in range(int(mode))]:
            path = case / f"actual-nested-{mode}-{label}.marshal"
            if path.is_file():
                data = path.read_bytes()
                probe_files[label] = {
                    "file": path.name, "bytes": len(data),
                    "sha256": sha(data),
                }
    probe_text = (case / "fingerprint-probe.log").read_text(
        errors="replace") if (case / "fingerprint-probe.log").is_file() else ""
    probe_complete = (args.fingerprint_probe and
        len(probe_files) == len(source["source_order"]) + 1 and
        "SORT4-ACTUAL-NESTED-FINGERPRINT: diagnostic refusal: snapshot complete; no proof rule admitted"
          in probe_text and
        stages.get("fingerprint-probe", {}).get("exit") == 2)
    record = {
        "classification": "SOURCE_MIR_CAPTURE_ONLY",
        "actual_helper_proved": False,
        "actual_nested_drop_proved": False,
        "same_unit_generic_method_proved": False,
        "source_certificate": source,
        "frontend_refinement": complete_export and refine and intact,
        "source_unchanged": intact,
        "complete_graphs": full,
        "outer_nested_capture": graph,
        "first_barrier_requested": args.first_barrier,
        "first_barrier_exit": stages.get("first-barrier", {}).get("exit"),
        "first_barrier_errors": LINK.LINK.ERR.findall(first_text),
        "first_barrier_fatal": [line for line in first_text.splitlines()
                                if line.startswith("Fatal error:")],
        "fingerprint_probe_requested": args.fingerprint_probe,
        "fingerprint_probe_complete_diagnostic": probe_complete,
        "fingerprint_probe_files": probe_files,
        "fingerprint_probe_fatal": [line for line in probe_text.splitlines()
                                   if line.startswith("Fatal error:")],
        "stages": stages,
    }
    LINK.LINK.write_json(case / "capture-summary.json", record)
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool-home", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--compiler-sysroot", required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--deadline-epoch", type=int, required=True)
    parser.add_argument("--first-barrier", action="store_true",
                        help="run one ungated verifier diagnostic; no proof claim")
    parser.add_argument("--with-owned-forget", action="store_true",
                        help="also capture seven-body owner-preserving source")
    parser.add_argument("--fingerprint-probe", action="store_true",
                        help="dump complete eager decoded MIR; always refuses proof")
    args = parser.parse_args()
    PREP.require((os.environ.get("GITHUB_ACTIONS"),
                  os.environ.get("RUNNER_ENVIRONMENT"),
                  os.environ.get("RUNNER_OS")) ==
                 ("true", "github-hosted", "Linux"),
                 "actual nested capture requires GitHub-hosted Linux")
    for key in (
        "SORT4_MAYBEUNINIT_REPO_ROOT", "SORT4_SELECT_INTRINSIC_REPO_ROOT",
        "SORT4_POINTER_DROP_REPO_ROOT", "SORT4_GUARD_REPO_ROOT",
        "SORT4_GUARD_TEMPLATE_REPO_ROOT", "SORT4_ACTUAL_OWNER_REPO_ROOT",
        "SORT4_ACTUAL_OWNER_ADMISSION", "SORT4_A1_LINK_REPO_ROOT",
        "SORT4_G1_CALL_REPO_ROOT"):
        os.environ.pop(key, None)
    evidence = args.evidence.resolve()
    source = PREP.write_case(REPO, evidence,
                             with_owned_forget=args.with_owned_forget)
    six = capture_case(evidence / "six-body", source, args)
    seven = None
    if args.with_owned_forget:
        seven = capture_case(evidence / "seven-body-owned-forget",
                             source["owned_forget_seven_body"], args)
    record = {
        "classification": "SIX_AND_SEVEN_BODY_SOURCE_MIR_CAPTURE_ONLY"
            if args.with_owned_forget else "SIX_BODY_SOURCE_MIR_CAPTURE_ONLY",
        "actual_helper_proved": False,
        "actual_nested_drop_proved": False,
        "actual_safe_forget_linked": False,
        "six_body": six,
        "seven_body": seven,
    }
    LINK.LINK.write_json(evidence / "summary.json", record)
    print(json.dumps({
        "classification": record["classification"],
        "six_frontend_refinement": six["frontend_refinement"],
        "seven_frontend_refinement":
            seven["frontend_refinement"] if seven else None,
        "six_graphs": six["complete_graphs"],
        "seven_graphs": seven["complete_graphs"] if seven else None,
        "six_fingerprint_diagnostic":
            six["fingerprint_probe_complete_diagnostic"],
        "seven_fingerprint_diagnostic":
            seven["fingerprint_probe_complete_diagnostic"] if seven else None,
    }, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
