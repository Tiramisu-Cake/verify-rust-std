#!/usr/bin/env python3
"""Fail-closed provenance audit for the print-only actual-sort4 AST probe."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re


VERIFIED = "fddb6f1a0a90948042c99fd1037b7e939586c9e7b9e46a63367a7d876e04ccc9"
ORIGINAL = "3602050e45025745d80b308802be9e552310959abcee4b95bfe8c24f8ca04b72"
GRAPHS = {
    "normal": "667e43477674d9e834b462b612f498af81598ec18622f0a60337ae4fdc6b017d",
    "readonly": "925b05a8c2bb66be8ad5a7f091f8232d9e930782b5ca01067cf7d1bec349f5b5",
}
CALLS = {"std::ops::FnMut::call_mut": 5,
         "std::hint::select_unpredictable": 8,
         "std::ptr::copy_nonoverlapping": 4}
TRANSLATOR = "src/rust_frontend/vf_mir_translator/vf_mir_translator.ml"
PRODUCTION_TRANSLATOR = "0862e635075edd06a827c567710a3e1125ac03aa122e95149db755a1fddce48a"
FULL_FUNC_SNAPSHOT = "dc7e8487ae46470ebcb9f964cb158c44d9bf75042cffa79d465f4d7e67001d39"
PROBE_PATCH = "83a609b0b428dbb224c88b1482c6974f5184ccdfbad1d180dec666af42e31deb"


def need(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def preflight(base: Path) -> dict:
    result = load(base / "actual-sort4-result.json")
    candidate = load(base / "candidate-admission.json")
    fixture = base / "actual-sort4-fixture"
    prepared = load(fixture / "fixture.json")
    need(result["classification"] == "O24_EXACT_GRAPH_RESERVED_MARKER_DIAGNOSTIC" and
         result["source_pair_matches_O24"] is True and
         result["support_stages_complete"] is True and
         result["complete_graph_matches_O24"] is True and
         result["reserved_marker_first_refusal"] is True and
         result["tool_integrity"] is True and
         result["actual_sort4_proved"] is False,
         "fresh baseline is not exact O24 reserved-marker diagnostic")
    need(sha(fixture / "verified/lib.rs") == VERIFIED and
         sha(fixture / "original/lib.rs") == ORIGINAL and
         prepared["ghost_strip_identity"] is True and
         candidate["classification"] == "CALIBRATION_REVIEW_REQUIRED" and
         candidate["source_sha256"] == VERIFIED and
         candidate["original_sha256"] == ORIGINAL,
         "whole source pair/candidate calibration differs")
    for mode, expected in GRAPHS.items():
        row = candidate["paired_complete_typed_mir"][mode]
        need(row["complete_function_sha256"] == expected and
             result["complete_graph_sha256"][mode] == expected and
             row["call_counts"] == CALLS and
             row["all_selected_call_actions_direct_continue"] is True and
             row["all_graph_cleanup_and_drop_absent"] is True and
             row["first_call_source_line"] == 190 and
             row["first_pointer_origin"] == "v_base.add(1)" and
             row["second_pointer_origin"] == "v_base" and
             row["first_call_unwind"] == "Continue" and
             row["first_call_normal_target"].isdigit(),
             f"{mode}: complete typed first-call/CFG gate differs")
    return {"classification": "EXACT_O24_AST_PROBE_PREFLIGHT_ONLY",
            "source_sha256": VERIFIED, "original_sha256": ORIGINAL,
            "complete_graph_sha256": GRAPHS,
            "candidate_audit": "CALIBRATION_REVIEW_REQUIRED",
            "baseline_refusal": result["first_verifier_error"],
            "actual_sort4_proved": False, "frontend_semantics_accepted": False}


def first_error(log: str) -> str | None:
    errors = [line for line in log.splitlines()
              if ": error:" in line or line.startswith("Fatal error:")]
    return errors[0] if errors else None


def classify(args: argparse.Namespace) -> dict:
    prior = preflight(args.baseline)
    production = args.production_source
    probe = args.probe_source
    need(sha(production / TRANSLATOR) == PRODUCTION_TRANSLATOR and
         (production / "src/verifast.ml").read_bytes() ==
         (probe / "src/verifast.ml").read_bytes() and
         (production / "src/rust_frontend/vf_mir/vf_mir.capnp").read_bytes() ==
         (probe / "src/rust_frontend/vf_mir/vf_mir.capnp").read_bytes(),
         "production translator, kernel, or schema changed")
    off_log = args.probe_off_log.read_text(errors="replace")
    off_error = first_error(off_log)
    need(args.probe_off_exit not in (0, 124, 137) and
         "Verifying function 'sort4_stable'" in off_log and
         off_error == prior["baseline_refusal"] and
         "SORT4-AST-PROBE:" not in off_log and
         args.probe_off_output.is_dir() and
         not any(args.probe_off_output.iterdir()),
         "probe-console off control changed refusal or emitted AST data")
    log = args.probe_log.read_text(errors="replace")
    error = first_error(log)
    need(args.probe_exit not in (0, 124, 137) and
         "Verifying function 'sort4_stable'" in log and
         error == off_error and
         "verified/lib.rs(185,13-36)" in error and
         "No such function: __vf_sort4_first_unwind" in error,
         "probe altered stock reserved-marker first refusal")
    snapshot = args.probe_output / "sort4-ast-decl.marshal"
    trace = args.probe_output / "sort4-ast-scope.txt"
    inputs = args.probe_output.parent / "inputs-sha256.txt"
    input_rows = inputs.read_text().splitlines() if inputs.is_file() else []
    need(sum(row.startswith(PROBE_PATCH + "  ") and
             row.endswith("/verifast-actual-sort4-ast-scope-PROBE.patch")
             for row in input_rows) == 1,
         "R2 print-only patch pin absent")
    need(snapshot.is_file() and snapshot.stat().st_size > 0 and trace.is_file() and
         sha(snapshot) == FULL_FUNC_SNAPSHOT,
         "full AST snapshot or ordered scope trace absent")
    lines = trace.read_text().splitlines()
    need(lines and lines[0].startswith(f"O24 verified_sha256={VERIFIED} ") and
         "normal_blocks=55 locals=137" in lines[0],
         "probe header source/body inventory differs")
    cmp_paths = []
    first_paths = []
    detail_tags = []
    for line in lines[1:]:
        match = re.match(r"^\d+ (\S+) (.+) (\S+)$", line)
        need(match is not None, "malformed ordered AST trace row")
        path, tag, _location = match.groups()
        need(re.search(r" node_sha256=[0-9a-f]{64}$", tag) is not None,
             "R2 trace row lacks full-node SHA-256")
        detail_tags.append((path, tag))
        if tag.startswith("BlockStmt ") and "cmp_lifetime=true" in tag:
            cmp_paths.append(path)
        if tag.startswith("SwitchStmt ") and "fnmut=true" in tag and \
           "first_source_line_190=true" in tag:
            first_paths.append(path)
    need("SORT4-AST-PROBE: snapshot=" in log,
         "probe did not announce completed AST dump")
    if len(first_paths) != 1:
        observation = "AST_FIRST_CALL_SWITCH_AMBIGUOUS"
    elif len(cmp_paths) != 1:
        observation = "AST_CMP_LIFETIME_BLOCK_ABSENT_OR_AMBIGUOUS"
    elif first_paths[0].startswith(cmp_paths[0] + "/block["):
        observation = "AST_FIRST_CALL_INSIDE_UNIQUE_CMP_BLOCK"
    else:
        observation = "AST_FIRST_CALL_OUTSIDE_CMP_BLOCK"
    returning = any(line.split(" ", 2)[1].startswith(first_paths[0] +
                    "/arm[0:returning]") for line in lines[1:]) if len(first_paths) == 1 else False
    unwinding = any(line.split(" ", 2)[1].startswith(first_paths[0] +
                     "/arm[1:unwinding]") for line in lines[1:]) if len(first_paths) == 1 else False
    if len(first_paths) == 1 and (not returning or not unwinding):
        observation = "AST_FIRST_CALL_ARMS_MISSING_OR_REORDERED"
    def observed(path: str, marker: str) -> str:
        return "OBSERVED" if any(p == path and marker in tag
                                 for p, tag in detail_tags) else "UNOBSERVED"
    detail_observation = {
        "root_local_declarations": "OBSERVED" if sum(
            path.startswith("root[") and "/local[" in path and
            "LocalDecl name=" in tag for path, tag in detail_tags) >= 100
            else "UNOBSERVED",
        "cmp_typeid_declaration": observed("root[138]/decl[0]", "TypeWithTypeidDecl"),
        "cmp_block_free_metadata": observed("root[138]", "locals_to_free=["),
        "first_fnmut_operands": observed("root[138]/block[32]", "expr=Call("),
        "normal_debt_close": observed("root[138]/block[33]/pure", "Close pred="),
        "normal_recovery_call": observed("root[138]/block[35]/pure", "recover_pair"),
        "local_assignment_descriptors": "OBSERVED" if any(
            "expr=Assign(" in tag for _, tag in detail_tags) else "UNOBSERVED",
    }
    return {**prior, "classification": "PRINT_ONLY_AST_SCOPE_DIAGNOSTIC",
            "scope_observation": observation, "cmp_block_paths": cmp_paths,
            "r2_detail_observation": detail_observation,
            "first_call_switch_paths": first_paths,
            "first_call_returning_arm_zero": returning,
            "first_call_unwinding_arm_one": unwinding,
            "snapshot_sha256": sha(snapshot), "snapshot_bytes": snapshot.stat().st_size,
            "trace_sha256": sha(trace), "probe_first_error": error,
            "probe_off_first_error": off_error,
            "probe_off_verifier_exit": args.probe_off_exit,
            "probe_off_ast_output_empty": True,
            "probe_verifier_exit": args.probe_exit,
            "actual_sort4_proved": False, "direct_unwind_proved": False,
            "frontend_semantics_accepted": False,
            "normal_first_limit": "The verifier checks returning before unwinding; this AST observation does not test direct unwind."}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("preflight", "classify"))
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--probe-log", type=Path)
    parser.add_argument("--probe-exit", type=int)
    parser.add_argument("--probe-output", type=Path)
    parser.add_argument("--probe-off-log", type=Path)
    parser.add_argument("--probe-off-exit", type=int)
    parser.add_argument("--probe-off-output", type=Path)
    parser.add_argument("--production-source", type=Path)
    parser.add_argument("--probe-source", type=Path)
    args = parser.parse_args()
    need(not args.output.exists(), "refusing to overwrite audit output")
    if args.command == "preflight":
        result = preflight(args.baseline)
    else:
        need(all(value is not None for value in
                 (args.probe_log, args.probe_exit, args.probe_output,
                  args.probe_off_log, args.probe_off_exit,
                  args.probe_off_output,
                  args.production_source, args.probe_source)),
             "classify requires probe on/off logs, exits, outputs and both source trees")
        result = classify(args)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"classification": result["classification"],
                      "scope_observation": result.get("scope_observation")},
                     sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
