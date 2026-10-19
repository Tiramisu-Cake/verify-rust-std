#!/usr/bin/env python3
"""Cloud-only receiver/end-token negative controls for generated Drop glue.

The compiler translator's separately profiled diagnostic modes alter only the
caller finish sequence for the qualified generated-glue path. This runner
reuses an already prepared positive source pair and the existing staged case
executor; import is inert and no source preparation is performed here.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import sys


HERE = Path(__file__).resolve().parent
V7_PROFILE = "experimental-merge-actual-glue-body-v7"
V8_PROFILE = "experimental-merge-actual-glue-body-v8"
V7_CONTROLS = {
    "omit_end": "SMALLSORT_DROP_RECEIVER_CONTROL=omit_end",
    "wrong_end": "SMALLSORT_DROP_RECEIVER_CONTROL=wrong_end",
    "duplicate_end": "SMALLSORT_DROP_RECEIVER_CONTROL=duplicate_end",
}
RETIREMENT_CONTROL = {"post_retirement_drop":
                      "SMALLSORT_DROP_RECEIVER_CONTROL=post_retirement_drop"}
GLUE_NAME = "__vf_generated_drop_glue"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"required hosted classifier unavailable: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _call_rows(runtime, ast) -> list[dict]:
    rows = []
    for node in ast.nodes(runtime, "CallExpr"):
        if len(node.args) == 6 and isinstance(node.args[1], str):
            rows.append({"callee": node.args[1], "loc": ast.loc(node.args[0]), "node": node})
    return rows


def _argument_kind(call, ast) -> list[str | None]:
    args = ast.narg(call, "CallExpr", 6)[4]
    if not isinstance(args, list) or len(args) != 1:
        return ["invalid", None]
    pattern = ast.narg(args[0], "LitPat", 1)[0]
    if isinstance(pattern, ast.Node) and pattern.name == "Var":
        return ["receiver", ast.var(pattern)]
    if isinstance(pattern, ast.Node) and pattern.name == "AddressOf":
        pointer = ast.narg(pattern, "AddressOf", 2)[1]
        return ["address", ast.var(pointer)]
    return ["invalid", None]


def _inspect_ast(path: Path, ast, expected_drop_loc: str) -> dict:
    tree = ast.OcamlAstText(path.read_text(errors="replace")).parse()
    functions = [node for node in ast.nodes(tree, "Func")
                 if len(node.args) == 13 and node.args[4] == "natural_onecell"]
    bodies = [node for node in functions if isinstance(node.args[10], ast.Node) and
              node.args[10].name == "Some"]
    if len(functions) != 1 or len(bodies) != 1:
        return {"admitted": False, "reason": "caller AST body is absent or nonunique"}
    runtime = bodies[0].args[10].args[0]
    calls = _call_rows(runtime, ast)
    drop_calls = [row for row in calls if row["callee"] == GLUE_NAME]
    if len(drop_calls) != 1 or drop_calls[0]["loc"] != expected_drop_loc:
        return {"admitted": False, "reason": "generated caller call target/location differs",
                "generated_call_count": len(drop_calls),
                "generated_call_locs": [row["loc"] for row in drop_calls]}
    receiver_kind, receiver_name = _argument_kind(drop_calls[0]["node"], ast)
    ends = [row for row in calls if row["callee"] == "end_ref_mut" and
            row["loc"] == expected_drop_loc]
    end_arguments = [_argument_kind(row["node"], ast) for row in ends]
    opens = [row for row in calls if row["callee"] == "open_points_to" and
             row["loc"] == expected_drop_loc]
    open_arguments = [_argument_kind(row["node"], ast) for row in opens]
    physical_reopens = [kind for kind in open_arguments if kind[0] == "address"]
    # The syntax export also exposes the two return/unwind branches. Require
    # one generated call switch and record the branch-local end-call counts.
    switches = []
    for node in ast.nodes(runtime, "SwitchStmt"):
        if (len(node.args) == 3 and isinstance(node.args[1], ast.Node) and
                node.args[1].name == "CallExpr" and len(node.args[1].args) == 6 and
                node.args[1].args[1] == GLUE_NAME and ast.loc(node.args[1].args[0]) == expected_drop_loc):
            arms = []
            for arm in node.args[2]:
                if isinstance(arm, ast.Node) and len(arm.args) == 3:
                    tag = arm.args[1].args[1] if isinstance(arm.args[1], ast.Node) else None
                    all_arm_end_calls = [call for call in ast.nodes(arm.args[2], "CallExpr")
                                         if len(call.args) == 6 and call.args[1] == "end_ref_mut"]
                    arm_end_calls = [call for call in all_arm_end_calls
                                     if ast.loc(call.args[0]) == expected_drop_loc]
                    arms.append({"tag": tag,
                                 "all_end_count": len(all_arm_end_calls),
                                 "end_count": len(arm_end_calls),
                                 "other_end_locs": [ast.loc(call.args[0]) for call in all_arm_end_calls
                                                    if ast.loc(call.args[0]) != expected_drop_loc],
                                 "end_arguments": [_argument_kind(call, ast)
                                                   for call in arm_end_calls]})
            switches.append(arms)
    return {"admitted": True, "generated_call_loc": drop_calls[0]["loc"],
            "receiver_argument": [receiver_kind, receiver_name],
            "end_count_at_drop_loc": len(ends),
            "all_end_count": sum(1 for row in calls if row["callee"] == "end_ref_mut"),
            "end_arguments_at_drop_loc": end_arguments,
            "open_points_to_count_at_drop_loc": len(opens),
            "open_points_to_arguments_at_drop_loc": open_arguments,
            "physical_reopen_count": len(physical_reopens),
            "physical_reopen_arguments": physical_reopens,
            "outcome_switch_count": len(switches),
            "outcome_arms": switches[0] if len(switches) == 1 else []}


def _inspect_retirement_ast(path: Path, ast, expected_drop_loc: str,
                            expected_mir_local: str) -> dict:
    """Bind a second call directly after the exact guard's Rust StorageDead."""
    tree = ast.OcamlAstText(path.read_text(errors="replace")).parse()
    functions = [node for node in ast.nodes(tree, "Func")
                 if len(node.args) == 13 and node.args[4] == "natural_onecell"]
    bodies = [node for node in functions if isinstance(node.args[10], ast.Node) and
              node.args[10].name == "Some"]
    if len(functions) != 1 or len(bodies) != 1:
        return {"admitted": False, "reason": "caller AST body is absent or nonunique"}
    runtime = bodies[0].args[10].args[0]
    calls = _call_rows(runtime, ast)
    generated = [row for row in calls if row["callee"] == GLUE_NAME]
    if len(generated) != 2:
        return {"admitted": False, "reason": "expected natural and post-retirement calls exactly once each",
                "generated_call_count": len(generated),
                "generated_call_locs": [row["loc"] for row in generated]}
    if any(row["loc"] != expected_drop_loc for row in generated):
        return {"admitted": False, "reason": "generated call moved from the caller Drop span",
                "generated_call_locs": [row["loc"] for row in generated]}
    receiver_args = [_argument_kind(row["node"], ast) for row in generated]
    if receiver_args[0][0] != "receiver" or receiver_args[1] != receiver_args[0]:
        return {"admitted": False, "reason": "post-retirement call does not reuse the first receiver",
                "generated_receiver_arguments": receiver_args}

    storage_matches = []
    storage_for_local = []
    adjacent_calls = []
    event_order = []

    def visit(value):
        if isinstance(value, ast.Node):
            if value.name == "CallExpr" and len(value.args) == 6 and value.args[1] == GLUE_NAME:
                event_order.append(("call", value))
            elif value.name == "RustStorageDeadStmt" and len(value.args) == 4:
                if value.args[2] == expected_mir_local:
                    storage_for_local.append(value)
                if (value.args[2] == expected_mir_local and value.args[3] == "gap_guard" and
                        ast.loc(value.args[1]) == expected_drop_loc):
                    event_order.append(("storage", value))
            for child in value.args:
                visit(child)
        elif isinstance(value, (list, tuple)):
            for child in value:
                visit(child)

    def inspect_siblings(value):
        if isinstance(value, (list, tuple)):
            for index, child in enumerate(value):
                if (isinstance(child, ast.Node) and child.name == "RustStorageDeadStmt" and
                        len(child.args) == 4 and child.args[2] == expected_mir_local and
                        child.args[3] == "gap_guard" and ast.loc(child.args[1]) == expected_drop_loc):
                    storage_matches.append(child)
                    if index + 1 < len(value):
                        following = value[index + 1]
                        if isinstance(following, ast.Node) and following.name == "ExprStmt":
                            expr = ast.narg(following, "ExprStmt", 1)[0]
                            if (isinstance(expr, ast.Node) and expr.name == "CallExpr" and
                                    len(expr.args) == 6 and expr.args[1] == GLUE_NAME):
                                adjacent_calls.append(expr)
                inspect_siblings(child)
        elif isinstance(value, ast.Node):
            inspect_siblings(value.args)

    visit(runtime)
    inspect_siblings(runtime)
    storage_positions = [index for index, (kind, _) in enumerate(event_order) if kind == "storage"]
    call_positions = [index for index, (kind, _) in enumerate(event_order) if kind == "call"]
    ordered = (len(storage_positions) == 1 and len(call_positions) == 2 and
               call_positions[0] < storage_positions[0] < call_positions[1])
    direct_call = (len(storage_matches) == 1 and len(adjacent_calls) == 1 and
                   adjacent_calls[0] is generated[1]["node"])
    return {"admitted": (len(storage_for_local) == 1 and len(storage_matches) == 1 and
                         direct_call and ordered),
            "guard_mir_local": expected_mir_local,
            "guard_storage_dead_count": len(storage_for_local),
            "guard_storage_dead_loc": (ast.loc(storage_matches[0].args[1])
                                       if storage_matches else None),
            "generated_call_count": len(generated),
            "generated_call_locs": [row["loc"] for row in generated],
            "generated_receiver_arguments": receiver_args,
            "storage_dead_immediately_precedes_second_call": direct_call,
            "natural_call_storage_dead_second_call_order": ordered,
            "second_call_after_retirement_count": len(adjacent_calls)}


def _expected_ast(mode: str, details: dict, positive_receiver: tuple[str, str | None]) -> bool:
    if not details.get("admitted") or details.get("receiver_argument") != list(positive_receiver):
        return False
    arms = details.get("outcome_arms", [])
    if len(arms) != 2 or {arm.get("tag") for arm in arms} != {"returning", "unwinding"}:
        return False
    if mode == "omit_end":
        return (details.get("end_count_at_drop_loc") == 0 and details.get("all_end_count") == 0 and
                details.get("physical_reopen_count") == 2 and
                details.get("physical_reopen_arguments") == [["address", "gap_guard"]] * 2 and
                all(arm["end_count"] == arm["all_end_count"] == 0 for arm in arms))
    if mode == "wrong_end":
        return (details.get("end_count_at_drop_loc") == 2 and
                details.get("physical_reopen_count") == 2 and
                details.get("physical_reopen_arguments") == [["address", "gap_guard"]] * 2 and
                all(arm["end_count"] == arm["all_end_count"] == 1 and
                    not arm["other_end_locs"] and
                    arm["end_arguments"] == [["address", "gap_guard"]] for arm in arms) and
                details.get("end_arguments_at_drop_loc") == [["address", "gap_guard"],
                                                               ["address", "gap_guard"]])
    if mode == "duplicate_end":
        receiver = positive_receiver[1]
        return (details.get("end_count_at_drop_loc") == 4 and
                details.get("physical_reopen_count") == 2 and
                details.get("physical_reopen_arguments") == [["address", "gap_guard"]] * 2 and
                all(arm["end_count"] == arm["all_end_count"] == 2 and
                    not arm["other_end_locs"] and
                    arm["end_arguments"] == [["receiver", receiver], ["receiver", receiver]]
                    for arm in arms) and
                details.get("end_arguments_at_drop_loc") == [["receiver", receiver]] * 4)
    return False


def _glue_markers_precede_error(log: str, glue_gate: dict, error: str,
                                drop_module) -> bool:
    headers = list(re.finditer(r"(?m)^.*Verifying function '([^']+)'[^\n]*$", log))
    matching = [header for header in headers
                if drop_module._is_generated_glue_name(header.group(1))]
    if len(matching) != 1:
        return False
    start = matching[0].start()
    later = [header.start() for header in headers if header.start() > start]
    end = min(later) if later else len(log)
    segment = log[start:end]
    target_at = log.find(error)
    if target_at < 0 or target_at < end:
        return False

    def positions(location: str | None, marker: str) -> list[int]:
        if not location:
            return []
        return [start + match.start() for match in re.finditer(
            rf"(?m)^.*{re.escape(location)}: (?:note: )?{marker}[^\n]*$", segment)]

    copy = positions(glue_gate.get("receiver_copy_loc"), "Executing statement")
    method = positions(glue_gate.get("selected_method_call_loc"), "Verifying call")
    ret = [start + m.start() for m in re.finditer(r"(?m)^.*Executing return statement\s*$", segment)]
    call_loc = glue_gate.get("selected_method_call_loc")
    span = re.fullmatch(r"(.+)\(([1-9][0-9]*),[0-9]+-([1-9][0-9]*),[0-9]+\)",
                        call_loc or "")
    leak = []
    if span is not None:
        file_name, _, end_line = span.groups()
        leak_loc = re.compile(rf"(?m)^.*{re.escape(file_name)}\({end_line},[0-9]+(?:-[0-9]+)?\): Leak check\.$")
        leak = [start + m.start() for m in leak_loc.finditer(segment)]
    return (len(copy) == 1 and len(method) == 1 and len(ret) == 1 and len(leak) == 1 and
            copy[0] < method[0] < ret[0] < leak[0] < target_at)


def _target_error_and_call_trace(log: str, mode: str, drop_loc: str) -> dict:
    """Match the first failing callee precondition and its exact caller call.

    VeriFast reports a failed called-method precondition at the assertion or
    predicate definition that could not be consumed, then annotates the call
    site.  The primary error location therefore need not be the caller's Drop
    span.  Both ends are required here; a same-text error elsewhere is not a
    receiver-control result.
    """
    expected = {
        "omit_end": ("^" + re.escape(drop_loc) + r": error: No matching heap chunks: "
                     r"\[_\]points_to<CopyOnDrop>\(gap_guard_addr, _\)"),
        "wrong_end": (r"(?:^|/)aliasing\.rsspec\(68,9-26\): error: No matching heap chunks: "
                      r"ref_mut_end_token<CopyOnDrop>\(gap_guard_addr, _\)"),
        "duplicate_end": (r"(?:^|/)aliasing\.rsspec\(68,9-26\): error: No matching heap chunks: "
                          r"ref_mut_end_token<CopyOnDrop>\(fn_outcome_result\(outcome1\), _\)"),
        "post_retirement_drop": (r"^verified/lib\.rs\(53,17-20\): error: No matching heap chunks: "
                                 r"CopyOnDrop_src\(fn_outcome_result\(outcome1\), _\)"),
    }
    pattern = expected.get(mode)
    if pattern is None:
        return {"matched": False, "reason": "unknown receiver control"}
    lines = log.splitlines()
    errors = [(i, line) for i, line in enumerate(lines) if re.search(r"\berror:", line, re.I)]
    exact = [(i, line) for i, line in errors if re.search(pattern, line)]
    caller_note = f"{drop_loc}: note: Verifying call"
    trace = []
    if len(exact) == 1:
        error_index = exact[0][0]
        # The source excerpt and caret follow the primary error; the call-site
        # note is attached to that same diagnostic within this bounded block.
        trace = [(i, line) for i, line in enumerate(lines[error_index + 1:error_index + 12],
                                                     error_index + 1)
                 if line.strip().endswith(caller_note)]
    # The omitted-end diagnostic is a direct call-site points_to failure, so
    # the primary error itself is the exact Drop call and the trailing note is
    # only "Consuming points_to chunk". Other modes fail in the callee contract
    # and must carry the call-site note.
    direct_callsite = mode == "omit_end" and len(exact) == 1 and \
        exact[0][1].startswith(drop_loc + ": error:") and \
        any(line.strip() == f"{drop_loc}: note: Consuming points_to chunk"
            for line in lines[exact[0][0] + 1:exact[0][0] + 8])
    call_trace_ok = len(trace) == 1 if mode != "omit_end" else direct_callsite
    matched = len(errors) == len(exact) == 1 and call_trace_ok
    return {"matched": matched, "error_count": len(errors),
            "exact_error_count": len(exact),
            "error_line": exact[0][1] if len(exact) == 1 else None,
            "error_line_number": exact[0][0] + 1 if len(exact) == 1 else None,
            "caller_drop_note": (trace[0][1] if len(trace) == 1 else
                                 (f"{drop_loc}: direct points_to call failure" if direct_callsite else None)),
            "caller_note_line_number": (trace[0][0] + 1 if len(trace) == 1 else
                                        (exact[0][0] + 1 if direct_callsite else None)),
            "caller_drop_loc": drop_loc}


def _classify(case: Path, mode: str, execution: dict, source_before: dict,
              source_after: dict, positive_drop_loc: str, positive_receiver: tuple,
              positive_glue_body: dict, ast, drop_module, mir_helper) -> dict:
    stages = execution.get("stages", {})
    original_stages = execution.get("original_export_stages", {})
    proof_ast = case / "proof-ast.ml"
    log_path = case / "verifast.log"
    log = log_path.read_text(errors="replace") if log_path.is_file() else ""
    errors = [line for line in log.splitlines() if re.search(r"\berror:", line, re.I)]
    dead = [line for line in log.splitlines() if re.search(r"dead code", line, re.I)]
    retirement = mode == "post_retirement_drop"
    mir_gate = (drop_module._natural_drop_mir_gate(case, {}, mir_helper)
                if retirement and stages.get("decode") == 0 else {"admitted": False})
    guard_local = mir_gate.get("guard_debug_local")
    if isinstance(guard_local, dict):
        guard_local = guard_local.get("name", guard_local.get("local"))
    if isinstance(guard_local, int):
        guard_local = f"_{guard_local}"
    ast_evidence = ((_inspect_retirement_ast(proof_ast, ast, positive_drop_loc, guard_local)
                     if retirement and isinstance(guard_local, str) else
                     {"admitted": False, "reason": "actual Drop MIR guard binding unavailable"})
                    if retirement else
                    _inspect_ast(proof_ast, ast, positive_drop_loc)
                    if stages.get("decode") == 0 and proof_ast.is_file() else
                    {"admitted": False, "reason": "proof AST missing or decode failed"})
    ast_matched = (_expected_ast(mode, ast_evidence, positive_receiver)
                   if not retirement else bool(mir_gate.get("admitted") and
                       ast_evidence.get("admitted") and ast_evidence.get("guard_storage_dead_loc") == positive_drop_loc))
    glue_gate = drop_module._generated_glue_proof_gate(log, positive_glue_body)
    stages_ready = (stages.get("exporter") == 0 and stages.get("decode") == 0 and
                    stages.get("refinement") == 0 and stages.get("verifast") == 1 and
                    original_stages == {"exporter": 0, "decode": 0})
    unchanged = (source_before == source_after and
                 execution.get("source_unchanged_at_every_stage") is True)
    target = _target_error_and_call_trace(log, mode, positive_drop_loc)
    target_errors = [target["error_line"]] if target.get("matched") else []
    # The generated callee must complete its own copied-receiver call, Return,
    # and leak check. The caller failure is admitted only at the actual Drop
    # statement location from the positive AST binding.
    if retirement:
        call_markers = [m.start() for m in re.finditer(
            rf"(?m)^.*{re.escape(positive_drop_loc)}: Verifying call[^\n]*$", log)]
        free_markers = [m.start() for m in re.finditer(
            rf"(?m)^.*{re.escape(positive_drop_loc)}: Freeing locals\.[^\n]*$", log)]
        # The qualified normal path verifies create_ref_mut, glue, and
        # end_ref_mut before retirement; the injected glue is the fourth call.
        retirement_log = (len(call_markers) == 4 and len(free_markers) >= 1 and
                          call_markers[2] < min(free_markers) < call_markers[3] <
                          (log.find(target_errors[0]) if len(target_errors) == 1 else -1))
    else:
        retirement_log = False
    matched = (stages_ready and unchanged and ast_matched and
               glue_gate.get("admitted") is True and len(errors) == 1 and
               len(target_errors) == 1 and not dead and
               _glue_markers_precede_error(log, glue_gate, target_errors[0], drop_module) and
               (not retirement or retirement_log))
    return {"case": mode, "classification": ("EXPECTED_POST_RETIREMENT_DROP_REJECTION" if retirement else
            "EXPECTED_RECEIVER_END_REJECTION") if matched else "INCONCLUSIVE",
            "accepted": False, "premises_supplied": False,
            "post_retirement_claim": "NOT_RUN",
            "stages": stages, "original_export_stages": original_stages,
            "source_sha256_before": source_before, "source_sha256_after": source_after,
            "source_unchanged_at_every_stage": unchanged,
            "positive_drop_call_loc": positive_drop_loc,
            "ast_control_evidence": ast_evidence,
            "actual_drop_mir_gate": mir_gate if retirement else "NOT_RUN",
            "retirement_log_order_admitted": retirement_log,
            "ast_control_matched": ast_matched,
            "generated_glue_body_gate": glue_gate,
            "expected_error_predicate": (
                "CopyOnDrop_src(fn_outcome_result(outcome1), _)" if retirement else
                "[_]points_to<CopyOnDrop>(gap_guard_addr, _)" if mode == "omit_end" else
                "ref_mut_end_token<CopyOnDrop>(" +
                ("fn_outcome_result(outcome1)" if mode == "duplicate_end" else "gap_guard_addr") + ", _)"),
            "target_error_and_caller_trace": target,
            "errors": errors, "dead_code": dead,
            "target_error_matched": len(target_errors) == 1,
            "generated_glue_markers_precede_caller_error": bool(target_errors) and
                _glue_markers_precede_error(log, glue_gate, target_errors[0], drop_module),
            "classification_reason": (None if matched else
                "requires source-stable successful exporter/decode/refinement, exact AST mutation, "
                "generated body call/Return/leak, and first targeted caller Drop proof error")}


def run(evidence: Path, args, env: dict, base, positive_case: Path, execute_case) -> dict:
    """Run caller end-token controls through the current full staged executor."""
    evidence = Path(evidence)
    positive_case = Path(positive_case)
    if evidence.exists():
        raise FileExistsError(f"refusing to reuse generated-glue receiver controls: {evidence}")
    evidence.mkdir(parents=True)
    cases_root = evidence / "cases"
    cases_root.mkdir()
    profile_label = getattr(args, "profile", "")
    if profile_label == V7_PROFILE:
        controls = V7_CONTROLS
    elif profile_label in (V8_PROFILE, "experimental-merge-guard-addressability-v1"):
        controls = {**V7_CONTROLS, **RETIREMENT_CONTROL}
    else:
        controls = {}
    status = {name: "NOT_RUN" for name in controls}
    aggregate = {"schema": "generated-glue-receiver-end-controls-v1",
                 "profile": getattr(args, "profile", None), "accepted": False,
                 "all_matched": False, "cases": status,
                 "post_retirement_claim": "NOT_RUN", "premises_supplied": False}
    if not controls:
        aggregate["reason"] = "receiver diagnostics require the explicitly pinned body-v7 or body-v8 profile"
        (evidence / "aggregate.json").write_text(json.dumps(aggregate, indent=2) + "\n")
        return aggregate
    if not callable(execute_case):
        raise TypeError("existing full execute_case callback required")
    positive_result_path = positive_case / "classification.json"
    if not positive_result_path.is_file():
        aggregate["reason"] = "positive classification receipt missing"
        (evidence / "aggregate.json").write_text(json.dumps(aggregate, indent=2) + "\n")
        return aggregate
    positive = json.loads(positive_result_path.read_text())
    positive_ast = positive.get("caller_ast_evidence", {})
    positive_glue = positive_ast.get("body_glue_evidence", {})
    positive_calls = [row for row in positive_ast.get("call_nodes", [])
                      if row.get("callee") == GLUE_NAME]
    if (positive.get("classification") != "NATURAL_DROP_CALLER_AND_EFFECT_PASS_FRAGMENT_ONLY" or
            positive.get("accepted") is not False or
            positive.get("stages", {}).get("exporter") != 0 or
            positive.get("stages", {}).get("decode") != 0 or
            positive.get("stages", {}).get("verifast") != 0 or
            positive.get("stages", {}).get("refinement") != 0 or
            positive.get("source_unchanged_at_every_stage") is not True or
            positive.get("generated_glue_proof_gate", {}).get("admitted") is not True or
            positive_ast.get("admitted") is not True or positive_glue.get("admitted") is not True or
            len(positive_calls) != 1):
        aggregate["reason"] = "positive actual-glue route has not passed all source/AST/body/refinement gates"
        aggregate["positive_gate"] = {"classification": positive.get("classification"),
            "stages": positive.get("stages"),
            "source_unchanged_at_every_stage": positive.get("source_unchanged_at_every_stage"),
            "generated_glue_proof_gate": positive.get("generated_glue_proof_gate"),
            "caller_ast_admitted": positive_ast.get("admitted"),
            "glue_ast_admitted": positive_glue.get("admitted")}
        (evidence / "aggregate.json").write_text(json.dumps(aggregate, indent=2) + "\n")
        return aggregate
    drop_loc = positive_calls[0].get("loc")
    if not isinstance(drop_loc, str) or not re.fullmatch(
            r"verified/lib\.rs\([1-9][0-9]*,[0-9]+-[0-9]+\)", drop_loc):
        aggregate["reason"] = "positive generated caller Drop location is malformed"
        (evidence / "aggregate.json").write_text(json.dumps(aggregate, indent=2) + "\n")
        return aggregate
    ast = base.ast_helper
    drop_module = _load("generated_glue_receiver_ast_gate",
                        HERE / "onecell-selected-drop.py")
    positive_ast_path = positive_case / "proof-ast.ml"
    try:
        positive_inspection = _inspect_ast(positive_ast_path, ast, drop_loc)
        if (not positive_inspection.get("admitted") or
                positive_inspection.get("end_count_at_drop_loc") != 2 or
                positive_inspection.get("all_end_count") != 2 or
                positive_inspection.get("physical_reopen_count") != 2 or
                positive_inspection.get("physical_reopen_arguments") != [["address", "gap_guard"]] * 2):
            raise ValueError("positive receiver/end AST shape is not the expected caller interface")
        positive_receiver = positive_inspection.get("receiver_argument")
        if positive_receiver[0] != "receiver":
            raise ValueError("positive generated caller call does not pass its receiver variable")
        receiver_pair = tuple(positive_receiver)
        if (positive_inspection.get("end_arguments_at_drop_loc") != [list(receiver_pair), list(receiver_pair)] or
                any(arm.get("end_arguments") != [list(receiver_pair)] for arm in
                    positive_inspection.get("outcome_arms", []))):
            raise ValueError("positive return/unwind arms do not end the exact generated receiver")
    except Exception as error:
        aggregate["reason"] = f"positive AST receiver binding audit failed: {error}"
        (evidence / "aggregate.json").write_text(json.dumps(aggregate, indent=2) + "\n")
        return aggregate
    aggregate["positive_drop_call_loc"] = drop_loc
    aggregate["positive_receiver"] = positive_receiver
    aggregate["positive_ast_sha256"] = _sha(positive_ast_path)
    aggregate["positive_classification_sha256"] = _sha(positive_result_path)
    for mode in controls:
        case = cases_root / mode
        case.mkdir()
        for subdir in ("original", "verified"):
            shutil.copytree(positive_case / subdir, case / subdir)
        extern = positive_case / "origin-control.rsspec"
        if extern.is_file():
            shutil.copy2(extern, case / extern.name)
        source_before = base.hashes(case)
        child_env = dict(env)
        child_env["SMALLSORT_DROP_RECEIVER_CONTROL"] = mode
        execution = execute_case(case, args, child_env)
        source_after = base.hashes(case)
        result = _classify(case, mode, execution, source_before, source_after,
                           drop_loc, tuple(positive_receiver), positive_glue,
                           ast, drop_module, base.mir_helper)
        result["profile"] = profile_label
        result["translator_diagnostic"] = controls[mode]
        result["execution_receipt"] = execution
        (case / "classification.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        status[mode] = result["classification"]
    aggregate["cases"] = status
    aggregate["all_matched"] = (bool(controls) and set(status) == set(controls) and
        all(value == ("EXPECTED_POST_RETIREMENT_DROP_REJECTION" if name == "post_retirement_drop"
                      else "EXPECTED_RECEIVER_END_REJECTION") for name, value in status.items()))
    aggregate["controls"] = {name: json.loads((cases_root / name / "classification.json").read_text())
                             for name in controls}
    aggregate["next_gate"] = "caller receiver/end qualification; negative controls supply no proof credit"
    (evidence / "aggregate.json").write_text(json.dumps(aggregate, indent=2, sort_keys=True) + "\n")
    return aggregate
