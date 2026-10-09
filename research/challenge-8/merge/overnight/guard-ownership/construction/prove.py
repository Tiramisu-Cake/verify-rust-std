#!/usr/bin/env python3
"""Hosted-only staged proof of the isolated source guard constructor."""

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
        raise RuntimeError(f"missing pinned helper {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


prep = load("guard_constructor_preparation", HERE / "prepare.py")
base = load("pinned_direct_drop_stages_for_constructor", HERE.parents[1] / "copy-on-drop-prove.py")
ast = base.ast_helper
mir = base.mir_helper
TARGET = "source_guard_construction"


def mir_gate(case: Path, line: int) -> dict:
    decoded = (case / "decode.out").read_text(errors="replace")
    variance = "variances = [invariant]"
    if decoded.count(variance) != 1 or len(re.findall(r"\bvariances\s*=", decoded)) != 1:
        raise RuntimeError("fragment must contain one invariant CopyOnDrop ADT")
    tree = mir.CapnpText(decoded.replace(variance, 'variances = ["invariant"]', 1)).parse()
    adt = mir.path(tree, "adtDefs", "cons", "h")
    fields = mir.path(adt, "variants")[0]["fields"]
    exact_fields = (
        mir.path(adt, "id", "name") == "CopyOnDrop" and
        mir.path(adt, "kind") == {"structKind": None} and
        mir.path(adt, "implementsDrop") is False and
        mir.path(tree, "adtDefs", "cons", "t") == {"nil": None} and
        len(fields) == 3 and
        [mir.path(field, "name", "name") for field in fields] == ["src", "dst", "len"] and
        mir.path(fields[0], "vis") == {"restricted": None} and
        mir.path(fields[1], "vis") == {"restricted": None} and
        mir.path(fields[2], "vis") == {"restricted": None} and
        mir.path(fields[0], "ty", "kind", "rawPtr", "mutability") == {"not": None} and
        mir.path(fields[1], "ty", "kind", "rawPtr", "mutability") == {"mut": None} and
        mir.path(fields[0], "ty", "kind", "rawPtr", "ty", "kind") == {"param": "T"} and
        mir.path(fields[1], "ty", "kind", "rawPtr", "ty", "kind") == {"param": "T"} and
        mir.path(fields[2], "ty", "kind") == {"uInt": {"uSize": None}})
    bodies = [body for body in mir.path(tree, "bodies")
              if mir.path(body, "defPath") == TARGET]
    drop_bodies = [body for body in mir.path(tree, "bodies")
                   if "Drop" in mir.path(body, "defPath") and
                   mir.path(body, "defPath").endswith("::drop")]
    if len(bodies) != 1:
        return {"admitted": False, "reason": "constructor MIR body count differs",
                "target_body_count": len(bodies), "exact_fields": exact_fields}
    blocks = mir.path(bodies[0], "basicBlocks")
    if not blocks or mir.path(blocks[0], "id", "index") != 0:
        return {"admitted": False, "reason": "constructor MIR entry block absent"}
    aggregate_locations = []
    aggregate_operands = []
    simple_copies = {}
    other_aggregate_count = 0
    returns = 0
    forbidden = []
    terminators = []
    arg_names = ("scratch_base", "v_base", "len")
    debug = mir.path(bodies[0], "varDebugInfo")
    parameter_locals = {}
    for row in debug:
        name = mir.path(row, "name", "name")
        if name not in arg_names or "place" not in mir.path(row, "value"):
            continue
        place = mir.path(row, "value", "place")
        if mir.path(place, "projection"):
            continue
        parameter_locals[name] = mir.path(place, "local", "name")
    for block in blocks:
        term = mir.path(block, "terminator", "kind")
        terminators.append(list(term) if isinstance(term, dict) else term)
        if mir.path(block, "isCleanup") is True or \
                mir.path(block, "terminator", "kind") is None:
            forbidden.append("cleanup_or_empty_terminator")
        if isinstance(term, dict):
            if "return" in term:
                returns += 1
            if len(term) != 1 or not set(term) <= {"goto", "return"}:
                forbidden.append(list(term))
        else:
            forbidden.append("non_structured_terminator")
        for stmt in mir.path(block, "statements"):
            kind = mir.path(stmt, "kind")
            if isinstance(kind, dict) and any(
                    k in kind for k in ("deinit", "setDiscriminant")):
                forbidden.append("destructive_statement")
            assignment = mir.assignment(stmt)
            if assignment is None:
                continue
            rhs = mir.path(assignment, "rhsRvalue")
            lhs = mir.path(assignment, "lhsPlace")
            if isinstance(rhs, dict) and set(rhs) == {"use"} and \
                    isinstance(rhs["use"], dict) and set(rhs["use"]) == {"copy"} and \
                    mir.path(lhs, "projection") == [] and \
                    mir.path(rhs["use"]["copy"], "projection") == []:
                target = mir.path(lhs, "local", "name")
                origin = mir.path(rhs["use"]["copy"], "local", "name")
                if target in simple_copies:
                    simple_copies[target] = None
                else:
                    simple_copies[target] = origin
            if isinstance(rhs, dict) and "aggregate" in rhs:
                aggregate = rhs["aggregate"]
                kind = mir.path(aggregate, "aggregateKind")
                adt_kind = kind.get("adt") if isinstance(kind, dict) else None
                is_guard = (isinstance(adt_kind, dict) and
                            mir.path(adt_kind, "adtId", "name") == "CopyOnDrop" and
                            mir.path(adt_kind, "adtKind") == {"structKind": None} and
                            mir.path(adt_kind, "variantIdx") == 0 and
                            mir.path(adt_kind, "variantId") == "CopyOnDrop" and
                            len(mir.path(adt_kind, "genArgs")) == 1 and
                            mir.path(adt_kind, "genArgs")[0] ==
                            {"kind": {"type": {"kind": {"param": "T"}}}} and
                            [mir.path(field, "name") for field in
                             mir.path(adt_kind, "fields")] == ["src", "dst", "len"] and
                            len(mir.path(aggregate, "operands")) == 3)
                if is_guard:
                    operands = mir.path(aggregate, "operands")
                    operand_locals = []
                    for operand in operands:
                        if (not isinstance(operand, dict) or len(operand) != 1 or
                                next(iter(operand)) not in ("copy", "move")):
                            operand_locals.append(None)
                            continue
                        place = next(iter(operand.values()))
                        operand_locals.append(
                            mir.path(place, "local", "name")
                            if mir.path(place, "projection") == [] else None)
                    aggregate_operands.append(operand_locals)
                    span = mir.path(stmt, "sourceInfo", "span", "regular")
                    lo = mir.path(span, "lo")
                    hi = mir.path(span, "hi")
                    aggregate_locations.append({
                        "lo_line": mir.path(lo, "line"),
                        "hi_line": mir.path(hi, "line"),
                        "lo_file": mir.path(lo, "file", "name", "real", "localPath"),
                        "hi_file": mir.path(hi, "file", "name", "real", "localPath"),
                        "lo_col": mir.path(lo, "col", "pos"),
                        "hi_col": mir.path(hi, "col", "pos")})
                else:
                    other_aggregate_count += 1
    located = (len(aggregate_locations) == 1 and
               aggregate_locations[0]["lo_file"] == "verified/lib.rs" and
               aggregate_locations[0]["hi_file"] == "verified/lib.rs" and
               aggregate_locations[0]["lo_line"] == line and
               aggregate_locations[0]["hi_line"] == line and
               0 <= aggregate_locations[0]["lo_col"] <
               aggregate_locations[0]["hi_col"] <= len(prep.P.CONSTRUCTOR_LINE))
    operands_linked = (len(aggregate_operands) == 1 and
                       set(parameter_locals) == set(arg_names) and
                       len(set(aggregate_operands[0])) == 3 and
                       [simple_copies.get(local) for local in aggregate_operands[0]] ==
                       [parameter_locals[name] for name in arg_names])
    admitted = (exact_fields and located and operands_linked and
                other_aggregate_count == 0 and returns >= 1 and
                not forbidden and not drop_bodies)
    return {"admitted": admitted, "exact_fields": exact_fields,
            "target_body_count": len(bodies), "basic_block_count": len(blocks),
            "aggregate_locations": aggregate_locations,
            "parameter_locals": parameter_locals,
            "aggregate_operand_locals": aggregate_operands,
            "aggregate_operand_origins": [simple_copies.get(local)
                                          for local in aggregate_operands[0]]
            if len(aggregate_operands) == 1 else [],
            "ordered_operand_origin_matches_parameters": operands_linked,
            "other_aggregate_count": other_aggregate_count,
            "aggregate_on_exact_source_line": located,
            "return_terminator_count": returns,
            "terminator_kinds": terminators, "forbidden_mir_operations": forbidden,
            "drop_body_count": len(drop_bodies),
            "no_drop_impl_or_cleanup": not forbidden and not drop_bodies}


def ast_gate(case: Path, line: int) -> dict:
    path = case / "proof-ast.ml"
    if not path.is_file():
        return {"admitted": False, "reason": "proof AST missing"}
    tree = ast.OcamlAstText(path.read_text(errors="replace")).parse()
    own = [node for node in ast.nodes(tree, "TypePredDef")
           if len(node.args) == 5 and node.args[1] == ["T"] and
           node.args[3] == "own" and "CopyOnDrop" in repr(node.args[2])]
    if len(own) != 1:
        return {"admitted": False, "reason": "custom own definition count differs",
                "own_count": len(own)}
    definition = own[0].args[4]
    right = (isinstance(definition, ast.Node) and definition.name == "Right" and
             len(definition.args) == 3 and definition.args[0] == ["t", "v"] and
             isinstance(definition.args[1], ast.Node) and
             definition.args[1].name == "Some" and definition.args[1].args == [2])
    body = definition.args[2] if right else None
    calls = [node.args[1] for node in ast.nodes(body, "CallExpr")
             if len(node.args) > 1 and isinstance(node.args[1], str)] if right else []
    payload = (right and not ast.nodes(body, "False") and
               len(ast.nodes(body, "PointsTo")) >= 2 and
               "foreach" in calls and "own" in calls and
               "src_values" in repr(body))
    functions = [node for node in ast.nodes(tree, "Func")
                 if len(node.args) == 13 and node.args[4] == TARGET and
                 node.args[10] != ast.Sym("None")]
    drop_functions = [node for node in ast.nodes(tree, "Func")
                      if len(node.args) == 13 and isinstance(node.args[4], str) and
                      "Drop" in node.args[4] and node.args[4].endswith("::drop")]
    if len(functions) != 1:
        return {"admitted": False, "reason": "runtime constructor Func count differs",
                "own_payload": payload, "body_count": len(functions)}
    fn = functions[0]
    runtime = fn.args[10]
    def var_name(node):
        return node.args[1] if isinstance(node, ast.Node) and \
            node.name == "Var" and len(node.args) == 2 else None

    source_assignments = {}
    field_assignments = {}
    for node in ast.nodes(runtime, "AssignExpr"):
        if len(node.args) != 4 or ast.location_line(node.args[0]) != line:
            continue
        lhs, mode, rhs = node.args[1:]
        if mode == ast.Sym("Mutation") and var_name(lhs) and var_name(rhs):
            source_assignments.setdefault(var_name(lhs), []).append(var_name(rhs))
        if (mode == ast.Sym("Initialization") and
                isinstance(lhs, ast.Node) and lhs.name == "Select" and
                len(lhs.args) == 3 and var_name(lhs.args[1]) == "drop_guard" and
                lhs.args[2] in ("src", "dst", "len") and var_name(rhs)):
            field_assignments.setdefault(lhs.args[2], []).append(var_name(rhs))
    source_types = [node for node in ast.nodes(runtime, "StructTypeExpr")
                    if ast.location_line(node.args[0]) == line and
                    len(node.args) == 5 and
                    node.args[1] == ast.Node("Some", ["CopyOnDrop"]) and
                    len(node.args[4]) == 1 and "T" in repr(node.args[4][0])]
    initializer_exact = (len(source_types) == 1 and
                         [field_assignments.get(field) for field in
                          ("src", "dst", "len")] ==
                         [["$_5"], ["$_6"], ["$_7"]] and
                         [source_assignments.get(local) for local in
                          ("$_5", "$_6", "$_7")] ==
                         [["scratch_base"], ["v_base"], ["len"]])
    contract = fn.args[8]
    contract_shape = (isinstance(contract, ast.Node) and contract.name == "Some" and
                      len(contract.args) == 1 and isinstance(contract.args[0], tuple) and
                      len(contract.args[0]) == 2 and
                      isinstance(contract.args[0][1], tuple) and
                      contract.args[0][1][0] == "outcome" and
                      isinstance(contract.args[0][1][1], ast.Node) and
                      contract.args[0][1][1].name == "SwitchExpr")
    pre = contract.args[0][0] if contract_shape else None
    pre_calls = [node.args[1] for node in ast.nodes(pre, "CallExpr")
                 if len(node.args) > 1 and isinstance(node.args[1], str)]
    full_supplied_pre = (len(ast.nodes(pre, "PointsTo")) >= 2 and
                         pre_calls.count("thread_token") == 1 and
                         "type_interp" in pre_calls and
                         "foreach" in pre_calls and "own" in pre_calls and
                         all(name in repr(pre) for name in
                             ("scratch_base", "v_base", "len", "src_values")) and
                         len(ast.nodes(pre, "Operation")) >= 4)
    clauses = contract.args[0][1][1].args[2] if contract_shape else []
    returning = [node.args[3] for node in clauses if
                 isinstance(node, ast.Node) and node.name == "SwitchExprClause" and
                 len(node.args) == 4 and node.args[1] == "returning"]
    unwinding = [node.args[3] for node in clauses if
                 isinstance(node, ast.Node) and node.name == "SwitchExprClause" and
                 len(node.args) == 4 and node.args[1] == "unwinding"]
    normal = returning[0] if len(returning) == 1 else None
    normal_calls = [node.args[1] for node in ast.nodes(normal, "CallExpr")
                    if len(node.args) > 1 and isinstance(node.args[1], str)]
    def result_field(value, field: str) -> bool:
        return (isinstance(value, ast.Node) and value.name == "Select" and
                len(value.args) == 3 and value.args[2] == field and
                isinstance(value.args[1], ast.Node) and
                value.args[1].name == "Var" and
                value.args[1].args[-1] == "result")

    def variable(value, name: str) -> bool:
        return (isinstance(value, ast.Node) and value.name == "Var" and
                len(value.args) == 2 and value.args[1] == name)

    operations = [node for node in ast.nodes(normal, "Operation")
                  if len(node.args) == 3 and isinstance(node.args[2], list) and
                  len(node.args[2]) == 2]
    equalities = {field: any(
        node.args[1] == ast.Sym("Eq") and
        result_field(node.args[2][0], field) and variable(node.args[2][1], name)
        for node in operations)
        for field, name in (("src", "scratch_base"), ("dst", "v_base"),
                            ("len", "len"))}
    length_lower_bound = any(
        node.args[1] == ast.Sym("Le") and
        isinstance(node.args[2][0], ast.Node) and
        node.args[2][0].name == "IntLit" and
        len(node.args[2][0].args) >= 2 and
        isinstance(node.args[2][0].args[1], ast.Node) and
        node.args[2][0].args[1].name == "big_int_of_string" and
        node.args[2][0].args[1].args == ["2"] and
        result_field(node.args[2][1], "len")
        for node in operations)
    own_return_calls = [node for node in ast.nodes(normal, "ExprCallExpr")
                        if len(node.args) == 3 and
                        isinstance(node.args[1], ast.Node) and
                        node.args[1].name == "TypePredExpr" and
                        len(node.args[1].args) == 3 and
                        isinstance(node.args[1].args[1], ast.Node) and
                        node.args[1].args[1].name == "ConstructedTypeExpr" and
                        node.args[1].args[1].args[1] == "CopyOnDrop" and
                        node.args[1].args[2] == "own" and
                        len(node.args[2]) == 2 and
                        [var_name(p.args[0]) if isinstance(p, ast.Node) and
                         p.name == "LitPat" and len(p.args) == 1 else None
                         for p in node.args[2]] == ["t", "result"]]
    full_normal = (len(returning) == 1 and len(own_return_calls) == 1 and
                   normal_calls.count("thread_token") == 1 and
                   all(equalities.values()) and length_lower_bound)
    unwind_false = (len(unwinding) == 1 and
                    isinstance(unwinding[0], ast.Node) and
                    unwinding[0].name == "False")
    runtime_calls = [node.args[1] for node in ast.nodes(runtime, "CallExpr")
                     if len(node.args) > 1 and isinstance(node.args[1], str)]
    own_closes = [node for node in ast.nodes(runtime, "Close")
                  if "CopyOnDrop_own" in repr(node)]
    admitted = (payload and initializer_exact and not drop_functions and
                full_supplied_pre and
                full_normal and unwind_false and len(own_closes) == 1 and
                not any(name in {"assume", "#assume"} for name in runtime_calls) and
                fn.args[7] == (ast.Sym("None"), ast.Sym("None")))
    return {"admitted": admitted, "own_payload": payload,
            "false_node_count": len(ast.nodes(body, "False")) if right else None,
            "runtime_body_count": len(functions),
            "drop_func_count": len(drop_functions),
            "source_aggregate_count": 1 if initializer_exact else 0,
            "source_initializer_assignments": field_assignments,
            "source_operand_assignments": source_assignments,
            "full_supplied_pre_shape": full_supplied_pre,
            "full_normal_post_shape": full_normal,
            "result_field_equalities": equalities,
            "result_len_at_least_two": length_lower_bound,
            "literal_unwind_false": unwind_false,
            "own_close_count": len(own_closes),
            "runtime_assume_count": sum(name in {"assume", "#assume"}
                                        for name in runtime_calls)}


def run_case(name: str, meta: dict, args, env: dict) -> dict:
    case = args.evidence / "cases" / name
    original = base.hashes(case)
    if original["original/lib.rs"] != meta["original_sha256"] or \
            original["verified/lib.rs"] != meta["verified_sha256"] or \
            original["small_sort_source"] != prep.B.SOURCE_SHA256:
        raise RuntimeError(f"{name}: pinned source hashes differ")
    (case / "source-before.json").write_text(json.dumps(original, indent=2) + "\n")
    exporter = base.run_stage(case, "exporter", [
        str(args.tool_home / "bin/vf-rust-mir-exporter"), "verified/lib.rs",
        f"--sysroot={args.compiler_sysroot}", "--edition", "2021", "--crate-type", "lib",
        "--vf-rust-mir-exporter:preprocess-readonly"], env,
        timeout_seconds=args.stage_seconds, stdout_name="compiler-mir.bin")
    if exporter == 0:
        include = list(dict.fromkeys([args.schema.parent, *args.capnp_include]))
        command = ["capnp", "decode"]
        for directory in include:
            command += ["-I", str(directory)]
        command += [str(args.schema), "VfMir"]
        decoder = base.run_stage(case, "decode", command, env,
                                 timeout_seconds=args.stage_seconds,
                                 stdin=case / "compiler-mir.bin")
    else:
        decoder = 125
        base.not_run(case, "decode", "readonly MIR exporter failed")
    (case / "compiler-mir-sha256.txt").write_text(
        base.file_sha(case / "compiler-mir.bin") + "\n")
    vf = base.run_stage(case, "verifast", [
        str(args.tool_home / "bin/verifast"), "-rustc_args", "--edition 2021",
        "-verbose", "1", "-dump_ast_with_locs", "proof-ast.ml", "verified/lib.rs"],
        env, combine=True, timeout_seconds=args.verifier_seconds)
    refinement = base.run_stage(case, "refinement", [
        str(args.tool_home / "bin/refinement-checker"), "--rustc-args", "--edition 2021",
        "original/lib.rs", "verified/lib.rs"], env,
        timeout_seconds=args.stage_seconds)
    stages = {"exporter": exporter, "decode": decoder,
              "verifast": vf, "refinement": refinement}
    after = base.hashes(case)
    unchanged = original == after and all(
        json.loads(path.read_text()).get("source_unchanged") is True
        for path in case.glob("*-stage.json")
        if json.loads(path.read_text()).get("status") != "NOT_RUN")
    try:
        mir_result = mir_gate(case, meta["verified_statement_line"]) if decoder == 0 else \
            {"admitted": False, "reason": "decode not available"}
    except Exception as error:
        mir_result = {"admitted": False, "reason": f"MIR admission failed closed: {error}"}
    try:
        ast_result = ast_gate(case, meta["verified_statement_line"])
    except Exception as error:
        ast_result = {"admitted": False, "reason": f"AST admission failed closed: {error}"}
    log = (case / "verifast.log").read_text(errors="replace")
    headers = [(match.start(), match.group(1)) for match in re.finditer(
        r"^\s*\d+(?:\.\d+)?s: [^\s(]+\([0-9]+,[0-9]+"
        r"(?:-[0-9]+(?:,[0-9]+)?)?\): Verifying function '([^']+)'$", log, re.M)]
    segments = []
    for index, (start, function) in enumerate(headers):
        if function == TARGET or function.startswith(TARGET + "<"):
            end = headers[index + 1][0] if index + 1 < len(headers) else len(log)
            segments.append(log[start:end])
    segment = segments[0] if len(segments) == 1 else ""
    errors = [line for line in log.splitlines() if re.search(r"\berror:", line, re.I)]
    dead = [line for line in log.splitlines() if re.search(r"dead code", line, re.I)]
    statement_seen = bool(re.search(
        rf"verified/lib\.rs\({meta['verified_statement_line']},[0-9]+(?:-[0-9]+(?:,[0-9]+)?)?\): "
        r"(?:note: )?Executing statement", segment))
    common = (unchanged and exporter == decoder == refinement == 0 and
              mir_result["admitted"] and ast_result["admitted"] and
              len(segments) == 1 and statement_seen and not dead)
    if name == "positive":
        matched = (common and vf == 0 and not errors and
                   "Executing return statement" in segment and
                   "Leak check." in segment and "0 errors found" in log)
    else:
        oracle = meta["intended_failure"]
        exact = any(re.search(
            rf"verified/lib\.rs\({oracle['line']},{oracle['column_start']}-{oracle['column_end']}\): "
            r"error: Assertion might not hold\. \(Cannot prove false\.\)", line)
            for line in errors)
        matched = (common and vf == 1 and len(errors) == 1 and exact and
                   "Executing return statement" not in segment and
                   "Leak check." not in segment)
    row = {"case": name, "stages": stages,
           "source_unchanged_at_every_stage": unchanged,
           "initial_source_hashes": original, "final_source_hashes": after,
           "mir_admission": mir_result, "ast_admission": ast_result,
           "constructor_body_count": len(segments),
           "source_statement_executed": statement_seen,
           "global_errors": errors, "dead_code_records": dead,
           "classification": ("PASS_FRAGMENT_ONLY" if name == "positive" else
                              "EXPECTED_FALSE_ASSERTION") if matched else "INCONCLUSIVE",
           "accepted": False,
           "scope": "isolated source constructor; no actual Drop implementation"}
    (case / "classification.json").write_text(json.dumps(row, indent=2) + "\n")
    return row


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
            not 1 <= args.stage_seconds <= 600 or \
            not 1 <= args.verifier_seconds <= 600:
        raise RuntimeError("profile or stage limits outside pinned allowlist")
    provider, proof_sha = base.require_hosted_cloud()
    if args.evidence.exists():
        raise RuntimeError("refusing to reuse evidence directory")
    if not args.tool_home.is_dir() or not args.compiler_sysroot.is_dir() or \
            not args.schema.is_file() or any(not d.is_dir() for d in args.capnp_include):
        raise RuntimeError("pinned hosted tool/schema/sysroot inputs missing")
    pins = base.validate_profile(args)
    if base.file_sha(args.schema) != base.STOCK_SCHEMA_SHA:
        raise RuntimeError("frozen MIR schema differs")
    source = base.ROOT / "library/core/src/slice/sort/shared/smallsort.rs"
    args.evidence.mkdir(parents=True)
    extraction = prep.extract(source, args.evidence / "cases",
                              args.evidence / "extraction.json")
    if extraction["exact_own_sha256"] != prep.P.sha(prep.OWN) or \
            extraction["constructor_contract_sha256"] != prep.P.sha(prep.CONSTRUCTOR_CONTRACT) or \
            extraction["fractional_v1_own_sha256"] != prep.P.sha(prep.P.OWN) or \
            extraction["full_source_permission_only"] is not True:
        raise RuntimeError("inherited non-False own or full constructor contract differs")
    rustc = shutil.which("rustc")
    capnp = shutil.which("capnp")
    if rustc is None or capnp is None:
        raise RuntimeError("hosted rustc/capnp missing")
    version = subprocess.run([rustc, "--version", "--verbose"],
                             capture_output=True, text=True, check=True).stdout
    if (os.environ.get("RUSTUP_TOOLCHAIN") != "nightly-2026-09-25" or
            "commit-hash: f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f" not in version or
            "host: x86_64-unknown-linux-gnu" not in version or
            platform.machine().lower() not in {"x86_64", "amd64"}):
        raise RuntimeError("hosted compiler pin differs")
    sysroot = subprocess.run([rustc, "--print", "sysroot"],
                            capture_output=True, text=True, check=True).stdout.strip()
    if Path(sysroot).resolve() != args.compiler_sysroot.resolve():
        raise RuntimeError("hosted compiler sysroot differs")
    drivers = {str(path): base.file_sha(path) for path in sorted(
        (args.compiler_sysroot / "lib").glob("librustc_driver-*.so"))}
    if not drivers:
        raise RuntimeError("hosted compiler driver missing")
    env = dict(os.environ)
    env["LD_LIBRARY_PATH"] = ":".join(filter(None, [
        str(args.compiler_sysroot / "lib"), str(args.tool_home / "bin"),
        env.get("LD_LIBRARY_PATH", "")]))
    (args.evidence / "environment.json").write_text(json.dumps({
        "diagnostic_profile": prep.PROFILE, "tool_profile": args.profile,
        "profile_pins": pins, "proof_sha": proof_sha, "provider": provider,
        "source_sha256": base.file_sha(source),
        "source_git_blob": prep.B.SOURCE_GIT_BLOB,
        "schema_sha256": base.file_sha(args.schema),
        "rustc_sha256": base.file_sha(Path(rustc)), "rustc_version": version,
        "compiler_drivers": drivers, "capnp_sha256": base.file_sha(Path(capnp)),
        "accepted": False}, indent=2) + "\n")
    rows = {}
    for name in ("positive", "first_body_false"):
        rows[name] = run_case(name, extraction["cases"][name], args, env)
        (args.evidence / "results.json").write_text(json.dumps({
            "profile": prep.PROFILE, "accepted": False, "cases": rows}, indent=2) + "\n")
    aggregate = {"profile": prep.PROFILE, "accepted": False,
                 "fragment_pass": (rows["positive"]["classification"] == "PASS_FRAGMENT_ONLY" and
                                   rows["first_body_false"]["classification"] ==
                                   "EXPECTED_FALSE_ASSERTION"),
                 "actual_drop_compatibility": "OPEN",
                 "cases": {name: row["classification"] for name, row in rows.items()}}
    (args.evidence / "aggregate.json").write_text(json.dumps(aggregate, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"constructor fragment hosted proof failed: {error}", file=sys.stderr)
        raise SystemExit(2)
