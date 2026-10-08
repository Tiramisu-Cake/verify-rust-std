#!/usr/bin/env python3
"""Hosted-only, fail-closed source preparation for the first actual sort4 call.

This does not run a verifier or activate the proposed frontend cut. The
result is a calibration fixture, never an accepted sort4 proof.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "overnight-sort4"))
import capture as sort4_capture  # noqa: E402 - the pinned project-owned source extractor
import probe  # noqa: E402


FIRST_CALL = b"        let c1 = is_less(&*v_base.add(1), &*v_base);"
UNSAFE_ANCHOR = sort4_capture.BORROW_PREFIX_UNSAFE_ANCHOR
CUT = b"        //@ end_lft_binding::<'cmp>();\n"
MARKER = b"""        /*@ {
            __vf_sort4_first_unwind();
            { close comparison_debt::<T>(t, cmp_k, v_base + 1, v_base, left_ref, right_ref, left_fraction, right_fraction); }
            { recover_pair::<T>(v_base + 1, v_base); }
            { join_four_owned_cells::<T>(v_base, t); }
        } @*/
"""
NORMAL_AFTER_CALL = b"""
        //@ close comparison_debt::<T>(t, cmp_k, v_base + 1, v_base, left_ref, right_ref, left_fraction, right_fraction);
        //@ end_lft_binding::<'cmp>();
        //@ recover_pair::<T>(v_base + 1, v_base);
        //@ join_four_owned_cells::<T>(v_base, t);"""


def need(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError(reason)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hosted_only() -> None:
    need(os.environ.get("GITHUB_ACTIONS") == "true" and
         os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted" and
         os.environ.get("RUNNER_OS") == "Linux",
         "sort4 first-call preparation requires GitHub-hosted Linux")


def callback_ghost_prefix() -> bytes:
    template = (HERE / "callback-cases.rs").read_bytes()
    begin = b"/*@\npred comparison_debt<T>("
    end = b"// CASE_BEGIN callback_positive\n"
    need(template.count(begin) == template.count(end) == 1,
         "checked callback debt/recovery prefix is missing or ambiguous")
    prefix = template[template.index(begin):template.index(end)]
    need(prefix.count(b"lem recover_pair<T>(") == 1 and
         b"nonghost_callers_only" in prefix and
         prefix.count(b"end_lifetime(k);") == 1,
         "checked callback recovery lemma shape changed")
    return prefix


def prepare(repo: Path, output: Path) -> dict:
    need(not output.exists(), "refusing to overwrite existing first-call fixture")
    source = (repo / sort4_capture.SOURCE_REL).read_bytes()
    target, source_certificate = sort4_capture.source_certificate(repo, source)
    need(target.count(FIRST_CALL) == 1 and
         target.count(UNSAFE_ANCHOR) == 1,
         "first actual call or enclosing unsafe scope is ambiguous")
    need(target.count(b"let c2 = is_less(") == 1 and
         target.index(FIRST_CALL) < target.index(b"let c2 = is_less("),
         "first and second comparator order changed")
    need(MARKER.count(b"__vf_sort4_first_unwind();") == 1 and
         NORMAL_AFTER_CALL.count(CUT) == 1,
         "source-written unwind/cut marker inventory changed")

    annotated_call = (sort4_capture.BORROW_PREFIX_FIRST_CALL.replace(
        FIRST_CALL, MARKER + FIRST_CALL, 1) + NORMAL_AFTER_CALL)
    need(annotated_call.count(FIRST_CALL) == 1,
         "first-call borrow preparation changed the actual call")
    verified_target = target.replace(FIRST_CALL, annotated_call, 1)
    verified_target = verified_target.replace(
        UNSAFE_ANCHOR, sort4_capture.BORROW_PREFIX_LIFETIME_SCOPE, 1)
    brace = verified_target.index(b"{")
    debt_and_recovery = callback_ghost_prefix()
    join = (HERE / "join-four-owned-cells.rs").read_bytes()
    need(join.startswith(b"/*@\nlem join_four_owned_cells<T>(") and
         join.rstrip().endswith(b"@*/") and
         b"assume(" not in join and b"assume_correct" not in join,
         "checked join-four lemma source changed shape")
    verified = (sort4_capture.PREFIX + sort4_capture.MEMORY_PRE_INTERIOR_LEMMA +
                sort4_capture.BORROW_PREFIX_SPLIT_LEMMA + debt_and_recovery +
                join + verified_target[:brace] +
                sort4_capture.MEMORY_PRE_CONTRACT + verified_target[brace:])
    original = sort4_capture.strip_ghost(verified)
    need(original == sort4_capture.PREFIX + target,
         "ghost stripping failed to recover exact full sort4 runtime body")
    need(original.count(target) == 1 and
         verified.count(FIRST_CALL) == 1 and
         verified.count(b"let c2 = is_less(") == 1 and
         verified.count(CUT) == 1 and
         verified.count(b"__vf_sort4_first_unwind();") == 1,
         "first-call source marker or full runtime inventory changed")

    (output / "original").mkdir(parents=True)
    (output / "verified").mkdir()
    (output / "original/lib.rs").write_bytes(original)
    (output / "verified/lib.rs").write_bytes(verified)
    record = {
        "classification": "CALIBRATION_ONLY_FIRST_ACTUAL_CALL_UNADMITTED",
        "actual_sort4_proved": False,
        "semantic_frontend_enabled": False,
        "full_runtime_body_unchanged": True,
        "ghost_strip_identity": True,
        "source_certificate": source_certificate,
        "original_sha256": sha(original),
        "verified_sha256": sha(verified),
        "debt_recovery_source_sha256": sha(debt_and_recovery),
        "join_four_source_sha256": sha(join),
        "first_call_source": FIRST_CALL.decode(),
        "marker_count": 1,
        "strict_lifetime_cut_count": 1,
        "expected_full_typed_mir_inventory": {
            "FnMut_call_mut": 5,
            "select_unpredictable": 8,
            "copy_nonoverlapping": 4,
            "first_call_ordered_source_cells": [1, 0],
            "first_call_unwind": "Continue",
            "first_call_cleanup": False,
        },
        "admission": {
            "paired_complete_typed_mir": "PENDING_HOSTED_CALIBRATION",
            "first_call_operand_alias_and_provenance": "PENDING_REVIEW",
            "all_source_mir_cleanup_edges": "PENDING_REVIEW",
            "strict_lifetime_kernel": "PENDING_HOSTED_GATES",
            "first_call_frontend_overlay": "NOT_IMPLEMENTED",
            "full_normal_sort4_post": "NOT_PROVED",
            "full_unwind_sort4_post": "NOT_PROVED",
        },
    }
    (output / "fixture.json").write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n")
    return record


def capture_calibration(args: argparse.Namespace, record: dict) -> dict:
    """Export and refine only; deliberately omit full verifier invocation."""
    tool_home = args.tool_home.resolve()
    schema = args.schema.resolve()
    source_checkout = args.source_checkout.resolve()
    need(tool_home.is_dir() and schema.is_file() and source_checkout.is_dir(),
         "pinned hosted tool/schema/source checkout is missing")
    profile = probe.source_certificate(args.repo_root.resolve(),
                                       source_checkout, tool_home)
    fixture = args.output.resolve()
    hashes = {"original/lib.rs": record["original_sha256"],
              "verified/lib.rs": record["verified_sha256"]}
    environment = os.environ.copy()
    environment["PATH"] = (str(tool_home / "bin") + os.pathsep +
                           environment.get("PATH", ""))
    for key in ("SORT4_HRTB_OUTPUT", "SORT4_HRTB_OUTPUT_TARGETS",
                "SORT4_STRICT_LFT_CUT", "SORT4_CALLBACK_UNWIND"):
        environment.pop(key, None)
    stages: dict[str, dict] = {}

    def execute(name: str, argv: list[str], cap: int,
                stdin_name: str | None = None,
                stdout_name: str | None = None) -> dict:
        remaining = args.deadline_epoch - int(time.time())
        seconds = min(cap, remaining - 10) if remaining > 10 else None
        if seconds is None:
            return {"exit": None, "skipped": "artifact and cleanup reserve"}
        return probe.run_stage(name, argv, fixture, environment, hashes,
                               seconds, stdin_name, stdout_name)

    exporter = str(tool_home / "bin/vf-rust-mir-exporter")
    graphs = {}
    for mode in ("normal", "readonly"):
        switches = (["--vf-rust-mir-exporter:preprocess-readonly"]
                    if mode == "readonly" else [])
        stages[f"{mode}-export"] = execute(
            f"{mode}-export",
            [exporter, "verified/lib.rs", f"--sysroot={args.compiler_sysroot}",
             "--edition", "2021", *switches], 100,
            stdout_name=f"{mode}-mir.bin")
        if stages[f"{mode}-export"]["exit"] == 0:
            stages[f"{mode}-decode"] = execute(
                f"{mode}-decode", ["capnp", "decode", str(schema), "VfMir"],
                60, f"{mode}-mir.bin", f"{mode}-mir.txt")
        else:
            stages[f"{mode}-decode"] = {
                "exit": None, "skipped": f"{mode} export failed"}
        if stages[f"{mode}-decode"]["exit"] == 0:
            graphs[mode] = sort4_capture.graph_inventory(
                fixture / f"{mode}-mir.txt", fixture, mode)
    stages["refinement"] = execute(
        "refinement",
        [str(tool_home / "bin/refinement-checker"), "--rustc-args",
         "--edition 2021", "original/lib.rs", "verified/lib.rs"], 120)
    support = all(stages[name].get("exit") == 0 for name in (
        "normal-export", "normal-decode", "readonly-export",
        "readonly-decode", "refinement"))
    source_exact = all(row.get("source_exact") is True
                       for row in stages.values() if "source_exact" in row)
    result = {
        **profile,
        "classification": ("CALIBRATION_PAIRED_MIR_REVIEW_REQUIRED"
                           if support and source_exact else
                           "CALIBRATION_SETUP_INCONCLUSIVE"),
        "actual_sort4_proved": False,
        "semantic_frontend_enabled": False,
        "full_verification_invoked": False,
        "source_integrity": source_exact,
        "support_exports_decode_refinement_all_zero": support,
        "graphs": graphs,
        "stages": stages,
    }
    (fixture / "calibration.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main() -> None:
    hosted_only()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--capture", action="store_true")
    parser.add_argument("--source-checkout", type=Path)
    parser.add_argument("--tool-home", type=Path)
    parser.add_argument("--schema", type=Path)
    parser.add_argument("--compiler-sysroot")
    parser.add_argument("--deadline-epoch", type=int)
    args = parser.parse_args()
    record = prepare(args.repo_root.resolve(), args.output.resolve())
    if args.capture:
        need(all((args.source_checkout, args.tool_home, args.schema,
                  args.compiler_sysroot, args.deadline_epoch)),
             "--capture requires pinned tool, schema, compiler and deadline")
        calibration = capture_calibration(args, record)
        classification = calibration["classification"]
    else:
        classification = record["classification"]
    print(json.dumps({"classification": classification,
                      "verified_sha256": record["verified_sha256"]},
                     sort_keys=True))


if __name__ == "__main__":
    main()
