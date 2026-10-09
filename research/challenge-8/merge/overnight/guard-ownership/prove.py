#!/usr/bin/env python3
"""Cloud-only proof stages for the exact-source CopyOnDrop payload-own cases."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import platform
from pathlib import Path
import re
import shutil
import subprocess
import sys


HERE = Path(__file__).resolve().parent
PARENT = HERE.parent


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"missing pinned module {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


prep = load("guard_payload_preparation", HERE / "prepare.py")
base = load("pinned_direct_drop_proof", PARENT / "copy-on-drop-prove.py")
ast_helper = base.ast_helper


def own_ast_gate(case_dir: Path, expects_payload: bool) -> dict:
    path = case_dir / "proof-ast.ml"
    if not path.is_file():
        return {"admitted": False, "reason": "proof AST absent"}
    tree = ast_helper.OcamlAstText(path.read_text(errors="replace")).parse()
    def local_copy_on_drop_type(value) -> bool:
        if not isinstance(value, ast_helper.Node):
            return False
        if value.name == "ConstructedTypeExpr" and len(value.args) == 3:
            name, type_args = value.args[1:]
            exact_name = name == "CopyOnDrop"
        elif value.name == "StructTypeExpr" and len(value.args) == 5:
            option, type_args = value.args[1], value.args[4]
            exact_name = (isinstance(option, ast_helper.Node) and
                          option.name == "Some" and
                          option.args == ["CopyOnDrop"])
        else:
            return False
        return (exact_name and isinstance(type_args, list) and
                len(type_args) == 1 and
                isinstance(type_args[0], ast_helper.Node) and
                type_args[0].name == "IdentTypeExpr" and
                len(type_args[0].args) == 3 and
                type_args[0].args[1] == ast_helper.Sym("None") and
                type_args[0].args[2] == "T")

    definitions = [n for n in ast_helper.nodes(tree, "TypePredDef")
                   if len(n.args) == 5 and n.args[1] == ["T"] and
                   n.args[3] == "own" and
                   local_copy_on_drop_type(n.args[2])]
    if len(definitions) != 1:
        return {"admitted": False, "reason": "custom CopyOnDrop own count differs",
                "definition_count": len(definitions)}
    node = definitions[0]
    definition = node.args[4]
    right = (isinstance(definition, ast_helper.Node) and
             definition.name == "Right" and len(definition.args) == 3 and
             definition.args[0] == ["t", "v"] and
             isinstance(definition.args[1], ast_helper.Node) and
             definition.args[1].name == "Some" and
             definition.args[1].args == [2])
    body = definition.args[2] if right else None
    no_false = right and not ast_helper.nodes(body, "False")
    calls = [n.args[1] for n in ast_helper.nodes(body, "CallExpr")
             if len(n.args) >= 2 and isinstance(n.args[1], str)] if right else []
    points_to = ast_helper.nodes(body, "PointsTo") if right else []
    payload = (len(points_to) >= 2 and "foreach" in calls and
               any(name in {"own", "own::<T>"} or name.endswith("_own")
                   for name in calls) and
               "src_values" in repr(body))
    functions = [n for n in ast_helper.nodes(tree, "Func")
                 if len(n.args) == 13 and n.args[4] == prep.B.TARGET and
                 n.args[10] != ast_helper.Sym("None")]
    prototype = functions[0].args[7] if len(functions) == 1 else None
    opens = []
    if isinstance(prototype, tuple) and len(prototype) == 2 and \
            isinstance(prototype[1], ast_helper.Node) and \
            prototype[1].name == "Some":
        opens = [n.args[2] for n in ast_helper.nodes(prototype[1], "Open")
                  if len(n.args) >= 3]
    admitted = (right and no_false and payload == expects_payload and
                len(functions) == 1 and opens ==
                ["CopyOnDrop_full_borrow_content", "CopyOnDrop_own"])
    return {"admitted": admitted, "definition_count": len(definitions),
            "body_sha256": base.sha(repr(body).encode()) if body is not None else None,
            "own_is_explicit_right": right, "own_is_nonfalse": no_false,
            "false_node_count": len(ast_helper.nodes(body, "False")) if right else None,
            "points_to_count": len(points_to), "call_names": calls,
            "payload_in_own_ast": payload, "prototype_opens": opens,
            "runtime_drop_function_count": len(functions)}


def stage_gate(case_dir: Path, name: str, metadata: dict, row: dict) -> dict:
    log = (case_dir / "verifast.log").read_text(errors="replace")
    segment, _ = base.actual_drop_log_segment(log)
    prototype_seen = "Function prototype implementation check" in log
    body_seen = bool(segment)
    errors = [line for line in log.splitlines() if re.search(r"\berror:", line, re.I)]
    dead = [line for line in log.splitlines() if re.search(r"dead code", line, re.I)]
    try:
        expected_ast = own_ast_gate(case_dir, name != "missing_payload")
    except Exception as error:
        expected_ast = {"admitted": False,
                        "reason": f"custom-own AST admission failed closed: {error}"}
    stages = row["stages"]
    common = (stages["exporter"] == 0 and stages["decode"] == 0 and
              stages["refinement"] == 0 and
              row["source_unchanged_at_every_stage"] and
              row["mir_admission"].get("admitted") is True and
              expected_ast["admitted"] and prototype_seen and not dead)
    reason = ""
    direct_recheck = None
    if name == "positive":
        matched = (common and stages["verifast"] == 0 and not errors and
                   body_seen and row["verifier_admission"]["positive_gate"] and
                   "0 errors found" in log)
        reason = "prototype and actual full-post body, dynamic copy, return/leak"
    elif name == "constructor":
        try:
            direct_recheck = base.verifier_admission(
                case_dir, "positive", metadata, stages["verifast"],
                row["mir_admission"])
        except Exception as error:
            direct_recheck = {"positive_gate": False,
                              "reason": f"actual Drop recheck failed closed: {error}"}
        headers = [(match.start(), match.group(1)) for match in re.finditer(
            r"^\s*\d+(?:\.\d+)?s: [^\s(]+\([0-9]+,[0-9]+"
            r"(?:-[0-9]+(?:,[0-9]+)?)?\): Verifying function '([^']+)'$",
            log, re.M)]
        witness_segments = []
        for index, (start, function) in enumerate(headers):
            if function.endswith("source_guard_construction") or \
                    function.startswith("source_guard_construction<"):
                end = headers[index + 1][0] if index + 1 < len(headers) else len(log)
                witness_segments.append(log[start:end])
        source = base.ROOT / "library/core/src/slice/sort/shared/smallsort.rs"
        source_lines = source.read_bytes().splitlines()
        linked = (source_lines[metadata["source_constructor_line"] - 1] ==
                  prep.CONSTRUCTOR_LINE and
                  metadata["source_constructor_line_sha256"] ==
                  prep.sha(prep.CONSTRUCTOR_LINE))
        witness = witness_segments[0] if len(witness_segments) == 1 else ""
        witness_line = metadata["witness_constructor_line"]
        statement_seen = bool(re.search(
            rf"verified/lib\.rs\({witness_line},[0-9]+(?:-[0-9]+(?:,[0-9]+)?)?\): "
            r"(?:note: )?Executing statement", witness))
        matched = (common and linked and stages["verifast"] == 0 and
                   not errors and body_seen and
                   direct_recheck.get("positive_gate") is True and
                   len(witness_segments) == 1 and statement_seen and
                   "Executing return statement" in witness and "Leak check." in witness and
                   "0 errors found" in log)
        reason = "exact source constructor under separately supplied current payload"
    elif name == "first_body_false":
        matched = (common and stages["verifast"] == 1 and body_seen and
                   row["verifier_admission"]["matched_negative_gate"])
        reason = "actual first-body assertion after successful prototype"
    elif name == "prototype_false":
        oracle = metadata["intended_failure"]
        target = oracle["line"]
        # No actual-body entry, copy, return or leak is allowed before this
        # matched control. The direct contract remains unchanged.
        exact = any(re.search(
            rf"verified/lib\.rs\({target},{oracle['column_start']}-{oracle['column_end']}\): "
            r"error: Assertion might not hold\. \(Cannot prove false\.\)",
            line) for line in errors)
        matched = (common and stages["verifast"] == 1 and exact and
                   len(errors) == 1 and not body_seen and
                   row["verifier_admission"]["copy_call_verifying_records"] == 0)
        reason = "own-open assertion in prototype before actual body"
    else:
        # The missing-payload control has no target assertion. Its intended
        # location is the unchanged direct Drop source-array requirement. A
        # setup/frontend/geometry failure is classified INCONCLUSIVE.
        req_line = metadata["intended_failure"]["source_requirement_line"]
        first_missing_hint = any(re.search(
            rf"verified/lib\.rs\({req_line},[0-9]+(?:-[0-9]+(?:,[0-9]+)?)?\): "
            r"error:.*(?:chunk|predicate|points.to|source)", line, re.I)
            for line in errors)
        # Until the first full Cloud log identifies the exact verifier error
        # predicate and location, this negative is calibration only. A broad
        # textual hint must never be counted as an intended rejection.
        matched = False
        reason = "missing-payload calibration; exact error oracle pending Cloud evidence"
    return {"matched": bool(matched), "expected": reason,
            "prototype_seen": prototype_seen, "actual_body_seen": body_seen,
            "global_errors": errors, "dead_code_records": dead,
            "custom_own_ast": expected_ast,
            "actual_drop_positive_recheck": direct_recheck,
            "missing_payload_first_requirement_hint": first_missing_hint if name == "missing_payload" else None,
            "classification": ("PASS_COMPONENT_ONLY" if name in {"positive", "constructor"}
                               else "EXPECTED_REJECTION") if matched else "INCONCLUSIVE",
            "accepted": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool-home", type=Path, required=True)
    parser.add_argument("--compiler-sysroot", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--capnp-include", type=Path, action="append", default=[])
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--profile-evidence", type=Path, required=True)
    parser.add_argument("--stage-seconds", type=int, default=90)
    parser.add_argument("--verifier-seconds", type=int, default=base.TIMEOUT_SECONDS)
    args = parser.parse_args()
    if not 1 <= args.stage_seconds <= 600 or not 1 <= args.verifier_seconds <= 600:
        raise RuntimeError("per-stage limits must be 1..600 seconds")
    if args.profile not in {"stock-26.10", base.EXPERIMENTAL_PROFILE}:
        raise RuntimeError("only pinned stock or experimental profile admitted")
    provider, proof_sha = base.require_hosted_cloud()
    if args.evidence.exists():
        raise RuntimeError("refusing to reuse evidence directory")
    if not args.tool_home.is_dir() or not args.schema.is_file() or \
            not args.compiler_sysroot.is_dir() or \
            any(not path.is_dir() for path in args.capnp_include):
        raise RuntimeError("hosted tool/schema/sysroot inputs missing")
    pins = base.validate_profile(args)
    if base.file_sha(args.schema) != base.STOCK_SCHEMA_SHA:
        raise RuntimeError("frozen MIR schema changed")
    for relative in ("bin/verifast", "bin/vf-rust-mir-exporter",
                     "bin/refinement-checker"):
        if not (args.tool_home / relative).is_file():
            raise RuntimeError(f"pinned tool absent: {relative}")
    source = base.ROOT / "library/core/src/slice/sort/shared/smallsort.rs"
    args.evidence.mkdir(parents=True)
    extraction = prep.extract(source, args.evidence / "cases",
                              args.evidence / "extraction.json")
    if extraction["direct_contract_sha256"] != prep.sha(prep.B.CONTRACT) or \
            extraction["custom_own_sha256"] != prep.sha(prep.OWN):
        raise RuntimeError("prepared contract/own identity mismatch")
    env = dict(os.environ)
    env["LD_LIBRARY_PATH"] = ":".join(filter(None, [
        str(args.compiler_sysroot / "lib"), str(args.tool_home / "bin"),
        env.get("LD_LIBRARY_PATH", "")]))
    rustc = shutil.which("rustc")
    capnp = shutil.which("capnp")
    if rustc is None or capnp is None:
        raise RuntimeError("hosted compiler or capnp absent")
    compiler_version = subprocess.run([rustc, "--version", "--verbose"],
        capture_output=True, text=True, check=True).stdout
    if (os.environ.get("RUSTUP_TOOLCHAIN") != "nightly-2026-09-25" or
            "commit-hash: f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f" not in compiler_version or
            "host: x86_64-unknown-linux-gnu" not in compiler_version or
            platform.machine().lower() not in {"x86_64", "amd64"}):
        raise RuntimeError("hosted compiler pin differs")
    sysroot = subprocess.run([rustc, "--print", "sysroot"],
        capture_output=True, text=True, check=True).stdout.strip()
    if Path(sysroot).resolve() != args.compiler_sysroot.resolve():
        raise RuntimeError("hosted sysroot differs")
    drivers = {str(p): base.file_sha(p) for p in sorted(
        (args.compiler_sysroot / "lib").glob("librustc_driver-*.so"))}
    if not drivers:
        raise RuntimeError("hosted compiler driver absent")
    header = {"diagnostic_profile": prep.PROFILE, "tool_profile": args.profile,
              "tool_pins": pins, "provider": provider, "proof_sha": proof_sha,
              "source_sha256": base.file_sha(source),
              "source_git_blob": prep.B.SOURCE_GIT_BLOB,
              "schema_sha256": base.file_sha(args.schema),
              "rustc_sha256": base.file_sha(Path(rustc)),
              "compiler_version": compiler_version, "compiler_drivers": drivers,
              "compiler_sysroot": sysroot, "capnp_sha256": base.file_sha(Path(capnp)),
              "accepted": False}
    (args.evidence / "environment.json").write_text(json.dumps(header, indent=2) + "\n")
    rows = {}
    for name in ("positive", "prototype_false", "first_body_false",
                 "missing_payload", "constructor"):
        metadata = extraction["cases"][name]
        row = base.run_case(name, metadata, args, env)
        result = stage_gate(args.evidence / "cases" / name, name, metadata, row)
        rows[name] = {"stages": row["stages"], "direct_body": row,
                      "payload_gate": result}
        (args.evidence / "results.json").write_text(json.dumps({
            "profile": prep.PROFILE, "accepted": False, "cases": rows}, indent=2) + "\n")
    bridge_cases = ("positive", "prototype_false", "first_body_false", "constructor")
    aggregate = {"profile": prep.PROFILE, "accepted": False,
                 "conditional_bridge_pass": all(rows[name]["payload_gate"]["matched"]
                                                for name in bridge_cases),
                 "missing_payload_negative_status": "CALIBRATION_ONLY",
                 "scope": "conditional nonvacuous own to exact direct Drop; caller/glue/forget OPEN",
                 "cases": {k: v["payload_gate"]["classification"] for k, v in rows.items()}}
    (args.evidence / "aggregate.json").write_text(json.dumps(aggregate, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"guard payload-own hosted proof failed: {error}", file=sys.stderr)
        raise SystemExit(2)
