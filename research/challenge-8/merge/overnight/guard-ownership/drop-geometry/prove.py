#!/usr/bin/env python3
"""Cloud-only staged canonical CopyOnDrop FBC geometry diagnostic."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys


HERE = Path(__file__).resolve().parent


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"missing pinned module {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


prep = load("guard_geometry_preparation", HERE / "prepare.py")
base = load("pinned_actual_drop_stages_geometry", HERE.parents[1] / "copy-on-drop-prove.py")
ast = base.ast_helper
CASES = ("positive", "prototype_false", "first_body_false")


def own_and_geometry_ast_gate(case_dir: Path, name: str, metadata: dict) -> dict:
    path = case_dir / "proof-ast.ml"
    if not path.is_file():
        return {"admitted": False, "reason": "proof AST missing"}
    tree = ast.OcamlAstText(path.read_text(errors="replace")).parse()
    own = [node for node in ast.nodes(tree, "TypePredDef")
           if len(node.args) == 5 and node.args[1] == ["T"] and
           node.args[3] == "own" and "CopyOnDrop" in repr(node.args[2])]
    if len(own) != 1:
        return {"admitted": False, "reason": "CopyOnDrop custom own count differs",
                "own_count": len(own)}
    definition = own[0].args[4]
    right = (isinstance(definition, ast.Node) and definition.name == "Right" and
             len(definition.args) == 3 and definition.args[0] == ["t", "v"] and
             definition.args[1] == ast.Sym("None"))
    own_body = definition.args[2] if right else None
    own_calls = [node.args[1] for node in ast.nodes(own_body, "CallExpr")
                 if len(node.args) > 1 and isinstance(node.args[1], str)]
    own_payload = (right and not ast.nodes(own_body, "False") and
                   len(ast.nodes(own_body, "PointsTo")) == 2 and
                   "foreach" in own_calls and "own" in own_calls and
                   all(token in repr(own_body) for token in
                       ("src_values", "v", "src", "dst", "len")))
    fbc_declarations = [node for node in ast.nodes(tree, "PredCtorDecl")
                        if len(node.args) == 7 and
                        node.args[1] == "CopyOnDrop_full_borrow_content"]
    fbc_shape = False
    if len(fbc_declarations) == 1:
        fbc = fbc_declarations[0]
        body = fbc.args[6]
        fields = ast.nodes(body, "PointsTo")
        names = []
        for field in fields:
            read = field.args[1] if len(field.args) == 4 else None
            if (isinstance(read, ast.Node) and read.name == "Read" and
                    len(read.args) == 3 and isinstance(read.args[1], ast.Node) and
                    read.args[1].name == "Var" and read.args[1].args[-1] == "l"):
                names.append(read.args[2])
        calls = [node.args[1] for node in ast.nodes(body, "CallExpr")
                 if len(node.args) == 6]
        initializers = ast.nodes(body, "InitializerList")
        casts = [node for node in ast.nodes(body, "CastExpr")
                 if len(node.args) == 3 and isinstance(node.args[1], ast.Node) and
                 node.args[1].name == "StructTypeExpr" and
                 "CopyOnDrop" in repr(node.args[1]) and
                 isinstance(node.args[2], ast.Node) and
                 node.args[2].name == "InitializerList"]
        values = []
        if len(initializers) == 1 and len(initializers[0].args) == 2:
            for pair in initializers[0].args[1]:
                if isinstance(pair, tuple) and len(pair) == 2 and \
                        pair[0] == ast.Sym("None") and \
                        isinstance(pair[1], ast.Node) and pair[1].name == "Var":
                    values.append(pair[1].args[-1])
        fbc_shape = (fbc.args[2] == ["T"] and fbc.args[5] == ast.Sym("None") and
                     [pair[1] for pair in fbc.args[3]] == ["tid", "l"] and
                     fbc.args[4] == [] and len(fields) == 3 and
                     names == ["src", "dst", "len"] and
                     sorted(calls) == ["CopyOnDrop_own", "struct_CopyOnDrop_padding"] and
                     len(casts) == 1 and values == ["src", "dst", "len"] and
                     not ast.nodes(body, "False"))
    functions = [node for node in ast.nodes(tree, "Func")
                 if len(node.args) == 13 and node.args[4] in
                 {prep.B.TARGET, prep.B.TARGET.replace("core::ops::Drop", "std::ops::Drop")} and
                 isinstance(node.args[10], ast.Node) and node.args[10].name == "Some"]
    if len(functions) != 1:
        return {"admitted": False, "reason": "actual Drop body count differs",
                "own_payload": bool(own_payload), "fbc_shape": bool(fbc_shape),
                "drop_body_count": len(functions)}
    prototype_option = functions[0].args[7]
    proof = (prototype_option[1] if isinstance(prototype_option, tuple) and
             len(prototype_option) == 2 else None)
    proof_tuple = (proof.args[0] if isinstance(proof, ast.Node) and
                   proof.name == "Some" and len(proof.args) == 1 else None)
    statements = (proof_tuple[1] if isinstance(proof_tuple, tuple) and
                  len(proof_tuple) == 3 and isinstance(proof_tuple[1], list) else [])
    opens = [node for node in ast.nodes(statements, "Open")]
    open_names = [node.args[2] for node in opens if len(node.args) >= 3]
    assertions = ast.nodes(statements, "Assert")
    expected = metadata["geometry_assertions"]
    geometry_lines = [row["line"] for row in expected]
    actual_by_line = {row["line"]: [node for node in assertions
                                   if ast.location_line(node.args[0]) == row["line"]]
                      for row in expected}
    binding = [node for node in assertions
               if ast.location_line(node.args[0]) == metadata["field_binding_line"]]
    geometry_nodes = [actual_by_line[row["line"]][0]
                      for row in expected if len(actual_by_line[row["line"]]) == 1]
    geometry_text = [repr(node.args[1]) if len(node.args) >= 2 else ""
                     for node in geometry_nodes]
    geometry_expr_shape = (len(geometry_nodes) == 6 and
                           all("self" in text and "CopyOnDrop" in text
                               for text in geometry_text) and
                           "Mod" in geometry_text[1] and
                           "object_pointer_within_limits" in geometry_text[2] and
                           "MaxValue" in geometry_text[3] and
                           "guard_src" in geometry_text[4] and
                           "guard_dst" in geometry_text[5] and
                           all("guard_len" in geometry_text[index] for index in (4, 5)))
    false_line = (metadata.get("intended_failure") or {}).get("line")
    false_assertions = [node for node in assertions if ast.nodes(node, "False")]
    expected_false = 1 if name == "prototype_false" else 0
    false_shape = (len(false_assertions) == expected_false and
                   (not expected_false or
                    ast.location_line(false_assertions[0].args[0]) == false_line))
    order = ([ast.location_line(node.args[0]) for node in opens] +
             ([false_line] if expected_false else []) +
             [metadata["field_binding_line"]] + geometry_lines)
    ordered = (open_names == ["CopyOnDrop_full_borrow_content", "CopyOnDrop_own"] and
               len(opens) == 2 and all(a < b for a, b in zip(order, order[1:])) and
               len(binding) == 1 and len(ast.nodes(binding[0], "PointsTo")) == 3 and
               all(alias in repr(binding[0]) for alias in
                   ("guard_src", "guard_dst", "guard_len")) and
               len(assertions) == 7 + expected_false and false_shape)
    admitted = bool(own_payload and fbc_shape and ordered and geometry_expr_shape)
    return {"admitted": admitted, "own_precision": "nonprecise",
            "own_payload": bool(own_payload), "own_false_node_count": len(ast.nodes(own_body, "False")),
            "generated_fbc_nonprecise_exact_fields_padding_own": bool(fbc_shape),
            "prototype_open_names": open_names, "field_binding_line": metadata["field_binding_line"],
            "six_geometry_assertions_ordered": bool(ordered and geometry_expr_shape),
            "geometry_assertion_lines": geometry_lines,
            "prototype_false_ast_at_target": bool(false_shape),
            "prototype_assertion_count": len(assertions),
            "actual_drop_body_count": len(functions)}


def geometry_gate(case_dir: Path, name: str, meta: dict, row: dict) -> dict:
    try:
        shape = own_and_geometry_ast_gate(case_dir, name, meta)
    except Exception as error:
        shape = {"admitted": False, "reason": f"geometry AST admission failed closed: {error}"}
    log = (case_dir / "verifast.log").read_text(errors="replace")
    segment, _ = base.actual_drop_log_segment(log)
    errors = [line for line in log.splitlines() if re.search(r"\berror:", line, re.I)]
    dead = [line for line in log.splitlines() if re.search(r"dead code", line, re.I)]
    stages = row["stages"]
    prototype_seen = "Function prototype implementation check" in log
    common = (row["source_unchanged_at_every_stage"] is True and
              stages["exporter"] == stages["decode"] == stages["refinement"] == 0 and
              row["mir_admission"].get("admitted") is True and
              shape.get("admitted") is True and prototype_seen and not dead)
    matched = False
    if name == "positive":
        matched = (common and stages["verifast"] == 0 and not errors and
                   row["verifier_admission"].get("positive_gate") is True and
                   bool(segment) and "0 errors found" in log)
    elif name == "first_body_false":
        matched = (common and stages["verifast"] == 1 and
                   row["verifier_admission"].get("matched_negative_gate") is True and
                   bool(segment) and len(errors) == 1)
    else:
        oracle = meta["intended_failure"]
        exact = any(re.search(
            rf"verified/lib\.rs\({oracle['line']},{oracle['column_start']}-{oracle['column_end']}\): "
            r"error: Assertion might not hold\. \(Cannot prove false\.\)", line)
            for line in errors)
        matched = (common and stages["verifast"] == 1 and exact and len(errors) == 1 and
                   not segment and
                   row["verifier_admission"].get("copy_call_verifying_records") == 0)
    frontier = []
    for assertion in meta["geometry_assertions"]:
        at_line = [error for error in errors if re.search(
            rf"verified/lib\.rs\({assertion['line']},[0-9]+(?:-[0-9]+(?:,[0-9]+)?)?\): error:",
            error)]
        if at_line:
            frontier.append({"label": assertion["label"], "line": assertion["line"],
                             "errors": at_line})
    classification = ("PASS_COMPONENT_ONLY" if name == "positive" else
                      "EXPECTED_FALSE_ASSERTION") if matched else "INCONCLUSIVE"
    return {"classification": classification, "matched": bool(matched),
            "accepted": False, "own_ast_admission": shape,
            "prototype_seen": prototype_seen, "actual_body_seen": bool(segment),
            "geometry_frontier": frontier[0] if frontier else None,
            "global_errors": errors, "dead_code_records": dead,
            "actual_drop_compatibility": "CHECKED_FOR_THIS_CASE" if matched and name !=
                "prototype_false" else "OPEN"}


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
    if args.profile not in {"stock-26.10", base.EXPERIMENTAL_PROFILE} or \
            not 1 <= args.stage_seconds <= 600 or not 1 <= args.verifier_seconds <= 600:
        raise RuntimeError("profile or stage limits outside pinned allowlist")
    provider, proof_sha = base.require_hosted_cloud()
    if args.evidence.exists():
        raise RuntimeError("refusing to reuse geometry evidence path")
    if not args.tool_home.is_dir() or not args.schema.is_file() or \
            not args.compiler_sysroot.is_dir() or \
            any(not path.is_dir() for path in args.capnp_include):
        raise RuntimeError("hosted tool/schema/sysroot input absent")
    pins = base.validate_profile(args)
    if base.file_sha(args.schema) != base.STOCK_SCHEMA_SHA:
        raise RuntimeError("frozen MIR schema differs")
    for relative in ("bin/verifast", "bin/vf-rust-mir-exporter",
                     "bin/refinement-checker"):
        if not (args.tool_home / relative).is_file():
            raise RuntimeError(f"pinned tool missing: {relative}")
    source = base.ROOT / "library/core/src/slice/sort/shared/smallsort.rs"
    args.evidence.mkdir(parents=True)
    extraction = prep.extract(source, args.evidence / "cases",
                              args.evidence / "extraction.json")
    if (extraction["direct_original_contract_sha256"] != prep.P.sha(prep.B.CONTRACT) or
            extraction["custom_own_sha256"] != prep.P.sha(prep.V3.OWN)):
        raise RuntimeError("geometry source profile changed")
    env = dict(os.environ)
    env["LD_LIBRARY_PATH"] = ":".join(filter(None, [
        str(args.compiler_sysroot / "lib"), str(args.tool_home / "bin"),
        env.get("LD_LIBRARY_PATH", "")]))
    rustc, capnp = shutil.which("rustc"), shutil.which("capnp")
    if rustc is None or capnp is None:
        raise RuntimeError("hosted compiler/capnp missing")
    version = subprocess.run([rustc, "--version", "--verbose"],
                             capture_output=True, text=True, check=True).stdout
    if (os.environ.get("RUSTUP_TOOLCHAIN") != "nightly-2026-09-25" or
            "commit-hash: f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f" not in version or
            "host: x86_64-unknown-linux-gnu" not in version or
            platform.machine().lower() not in {"x86_64", "amd64"}):
        raise RuntimeError("hosted compiler identity differs")
    sysroot = subprocess.run([rustc, "--print", "sysroot"],
                             capture_output=True, text=True, check=True).stdout.strip()
    if Path(sysroot).resolve() != args.compiler_sysroot.resolve():
        raise RuntimeError("hosted sysroot differs")
    drivers = {str(path): base.file_sha(path) for path in sorted(
        (args.compiler_sysroot / "lib").glob("librustc_driver-*.so"))}
    if not drivers:
        raise RuntimeError("hosted compiler driver absent")
    tool_hashes = {relative: base.file_sha(args.tool_home / relative)
                   for relative in ("bin/verifast", "bin/vf-rust-mir-exporter",
                                    "bin/refinement-checker", pins["prelude_path"])}
    environment = {"diagnostic_profile": prep.PROFILE, "tool_profile": args.profile,
                   "profile": args.profile, "tool_pins": pins, "profile_pins": pins,
                   "provider": "cloud-build", "provider_info": provider,
                   "cloud_build_id": provider["build_id"], "proof_sha": proof_sha,
                   "cloud_project": provider["project"],
                   "cloud_region": provider["region"],
                   "source_sha256": base.file_sha(source),
                   "source_git_blob": prep.B.SOURCE_GIT_BLOB,
                   "small_sort_source_sha256": base.file_sha(source),
                   "small_sort_source_git_blob": prep.B.SOURCE_GIT_BLOB,
                   "schema_sha256": base.file_sha(args.schema),
                   "rustc_sha256": base.file_sha(Path(rustc)),
                   "compiler_rustc_path": rustc,
                   "compiler_rustc_sha256": base.file_sha(Path(rustc)),
                   "rustc_version": version, "compiler_drivers": drivers,
                   "compiler_version_verbose": version,
                   "compiler_driver_hashes": drivers,
                   "compiler_sysroot": sysroot, "capnp_sha256": base.file_sha(Path(capnp)),
                   "compiler_rustc_sysroot": sysroot,
                   "capnp_path": capnp,
                   "tool_hashes": tool_hashes,
                   "stage_timeout_seconds": args.verifier_seconds,
                   "capnp_include_dirs": [str(path) for path in
                                           dict.fromkeys([args.schema.parent,
                                                           *args.capnp_include])],
                   "profile_evidence": str(args.profile_evidence.resolve()),
                   "tool_home": str(args.tool_home.resolve()),
                   "schema_path": str(args.schema.resolve()),
                   "accepted": False}
    (args.evidence / "environment.json").write_text(json.dumps(environment, indent=2) + "\n")
    rows = {}
    for name in CASES:
        meta = extraction["cases"][name]
        direct = base.run_case(name, meta, args, env)
        gate = geometry_gate(args.evidence / "cases" / name, name, meta, direct)
        rows[name] = {"stages": direct["stages"], "direct_body": direct,
                      "geometry_gate": gate}
        (args.evidence / "results.json").write_text(json.dumps({
            "profile": args.profile, "diagnostic_profile": prep.PROFILE,
            "accepted": False, "cases": rows}, indent=2) + "\n")
    complete = (rows["positive"]["geometry_gate"]["classification"] ==
                "PASS_COMPONENT_ONLY" and all(
                    rows[name]["geometry_gate"]["classification"] ==
                    "EXPECTED_FALSE_ASSERTION" for name in
                    ("prototype_false", "first_body_false")))
    aggregate = {"diagnostic_profile": prep.PROFILE, "tool_profile": args.profile,
                 "accepted": False, "stages_collected": True,
                 "component_pass": complete, "actual_drop_compatibility":
                     "CHECKED_CONDITIONAL_DIRECT_ONLY" if complete else "OPEN",
                 "canonical_generic_drop_and_glue": "OPEN",
                 "cases": {name: row["geometry_gate"]["classification"]
                           for name, row in rows.items()}}
    (args.evidence / "aggregate.json").write_text(json.dumps(aggregate, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"geometry hosted proof failed: {error}", file=sys.stderr)
        raise SystemExit(2)
