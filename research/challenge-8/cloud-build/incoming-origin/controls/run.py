#!/usr/bin/env python3
"""Cloud-only execution hook and fail-closed origin-control classifier.

The local helpers parse saved MIR/AST artifacts. This module never dispatches a
compiler or verifier; its caller supplies the Cloud execute_case function.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "origin-controls.rs"
MANIFEST = HERE / "MANIFEST.json"
REPO = HERE.parents[4]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"missing checked parser helper: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _helpers():
    base = _load("incoming_origin_base", REPO / "research/challenge-8/merge/overnight/copy-on-drop-prove.py")
    return base.mir_helper, base.ast_helper


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def prepare(evidence: Path) -> tuple[dict, dict]:
    source = SOURCE.read_bytes()
    manifest = json.loads(MANIFEST.read_text())
    if manifest.get("schema") != "incoming-origin-controls-v1" or manifest.get("accepted") is not False:
        raise RuntimeError("origin control manifest identity mismatch")
    header = source.split(b"// CASE_BEGIN ", 1)[0]
    metadata = {}
    for spec in manifest["cases"]:
        name = spec["name"]
        begin = b"// CASE_BEGIN " + name.encode() + b"\n"
        end = b"// CASE_END " + name.encode()
        if source.count(begin) != 1 or source.count(end) != 1:
            raise RuntimeError(f"non-unique source delimiters for {name}")
        unit = header + source.split(begin, 1)[1].split(end, 1)[0]
        if unit.count(b"pub unsafe fn ") != 1 or unit.count(b"pub unsafe fn " + name.encode()) != 1:
            raise RuntimeError(f"control {name} is not isolated")
        lines = unit.decode().splitlines()
        targets = [i + 1 for i, line in enumerate(lines)
                   if "TARGET: " + spec["target"] in line]
        if len(targets) != 1:
            raise RuntimeError(f"control {name} has no unique obligation marker")
        case = evidence / name
        for tree in ("original", "verified"):
            (case / tree).mkdir(parents=True, exist_ok=True)
            (case / tree / "lib.rs").write_bytes(unit)
        metadata[name] = {**spec, "target_line": targets[0],
                          "source_sha256": _sha(unit),
                          "expected_stages": {**manifest["required_stages"],
                                              "verifast": (0 if spec["semantic_expectation"] == "PASS_CONTROL"
                                                           else 1 if spec["semantic_expectation"] == "EXPECTED_REJECTION"
                                                           else None)}}
    return manifest, metadata


def origin_gate(case: Path, meta: dict) -> dict:
    """Correlate one source call with normal MIR and an ordinary AST CallExpr.

    Storage constructors are independently matched to MIR storage events in the
    same function. Their source span may share the call's line; that alone is not
    evidence that the call was dispatched as a lifecycle event.
    """
    decoded = case / "decode.out"
    ast_path = case / "proof-ast.ml"
    if not decoded.is_file() or not ast_path.is_file():
        return {"admitted": False, "reason": "decoded MIR or proof AST missing"}
    try:
        mir, ast = _helpers()
        decoded_bytes, ast_bytes = decoded.read_bytes(), ast_path.read_bytes()
        tree = mir.CapnpText(decoded_bytes.decode("utf-8").replace(
            "variances = [invariant]", 'variances = ["invariant"]')).parse()
        bodies = [body for body in mir.path(tree, "bodies")
                  if mir.path(body, "defPath") == meta["name"]]
        if len(bodies) != 1:
            raise ValueError(f"expected one MIR body for {meta['name']}; found {len(bodies)}")
        body = bodies[0]
        mir_calls = []
        mir_events = []
        for block in mir.path(body, "basicBlocks"):
            term = mir.path(block, "terminator")
            kind = mir.path(term, "kind")
            if isinstance(kind, dict) and "call" in kind:
                call = kind["call"]
                callee = mir.path(call, "func", "constant", "const", "val", "ty",
                                  "kind", "fnDef", "id", "name")
                line = mir.path(term, "sourceInfo", "span", "regular", "lo", "line")
                if callee == meta["callee"] or callee.endswith("::" + meta["callee"]):
                    if len(mir.path(call, "args")) != 1:
                        raise ValueError("target MIR call does not carry one source argument")
                    target_option = mir.path(call, "target")
                    if not isinstance(target_option, dict) or set(target_option) not in (
                            {"nothing"}, {"something"}):
                        raise ValueError("MIR call target is not a checked Option")
                    unwind_action = mir.path(call, "unwindAction")
                    if meta["kind"] in {"branch_unwind_positive", "local_unwind_positive"} and (
                            not isinstance(unwind_action, dict) or
                            set(unwind_action) not in ({"continue"}, {"cleanup"})):
                        raise ValueError("branch callback has no MIR unwind successor")
                    mir_calls.append({"callee": callee, "source_line": line,
                                      "has_normal_target": "something" in target_option,
                                      "unwind_action": unwind_action})
            for stmt in mir.path(block, "statements"):
                stmt_kind = mir.path(stmt, "kind")
                for key, constructor in (("storageLive", "RustStorageLiveStmt"),
                                         ("storageDead", "RustStorageDeadStmt")):
                    if isinstance(stmt_kind, dict) and key in stmt_kind:
                        local = mir.path(stmt_kind, key, "name")
                        line = mir.path(stmt, "sourceInfo", "span", "regular", "lo", "line")
                        mir_events.append((constructor, local, line))
        target = meta["target_line"]
        mir_calls = [row for row in mir_calls if row["source_line"] == target]
        if len(mir_calls) != 1:
            raise ValueError(f"expected one matching MIR call terminator at target; found {len(mir_calls)}")
        if meta["kind"] == "diverging_extern" and mir_calls[0]["has_normal_target"]:
            raise ValueError("diverging MIR call unexpectedly has a normal target")

        ast_tree = ast.OcamlAstText(ast_bytes.decode("utf-8")).parse()
        functions = [node for node in ast.nodes(ast_tree, "Func")
                     if len(node.args) == 13 and node.args[4] == meta["name"] and
                     node.args[10] != ast.Sym("None")]
        if len(functions) != 1:
            raise ValueError(f"expected one translated caller body; found {len(functions)}")
        runtime = functions[0].args[10]
        ast_calls = [node for node in ast.nodes(runtime, "CallExpr")
                     if len(node.args) == 6 and isinstance(node.args[1], str) and
                     (node.args[1] == meta["callee"] or
                      node.args[1].endswith("::" + meta["callee"])) and
                     ast.location_line(node.args[0]) == target]
        if len(ast_calls) != 1:
            raise ValueError(f"target is not one ordinary AST CallExpr; found {len(ast_calls)}")
        arguments = ast_calls[0].args[4]
        if not isinstance(arguments, list) or len(arguments) != 1:
            raise ValueError("target AST call does not carry one argument")
        argument = ast.var(ast.narg(arguments[0], "LitPat", 1)[0])
        if argument != meta["argument"]:
            raise ValueError(f"target AST argument is {argument!r}, expected {meta['argument']!r}")
        observed_events = []
        for constructor in ("RustStorageLiveStmt", "RustStorageDeadStmt"):
            for node in ast.nodes(runtime, constructor):
                if len(node.args) != 4 or not isinstance(node.args[2], str):
                    raise ValueError(f"malformed {constructor} provenance fields")
                observed_events.append((constructor, node.args[2],
                                        ast.location_line(node.args[1])))
        if sorted(observed_events) != sorted(mir_events):
            raise ValueError("translated lifecycle provenance differs from caller MIR storage events")
        return {"admitted": True, "reason": "source call remains an ordinary CallExpr; lifecycle events match MIR provenance",
                "decoded_sha256": _sha(decoded_bytes), "proof_ast_sha256": _sha(ast_bytes),
                "mir_call": mir_calls[0], "ast_call": {"callee": ast_calls[0].args[1],
                                                        "argument": argument, "source_line": target},
                "mir_lifecycle_count": len(mir_events), "ast_lifecycle_count": len(observed_events)}
    except Exception as error:
        return {"admitted": False, "reason": f"origin MIR/AST correlation failed: {error}"}


def local_death_gate(case: Path, function: str = "origin_local_death_lost_cell") -> dict:
    """Bind the missing-resource negative to one tmp StorageDead provenance."""
    decoded, ast_path = case / "decode.out", case / "proof-ast.ml"
    if not decoded.is_file() or not ast_path.is_file():
        return {"admitted": False, "reason": "decoded MIR or proof AST missing"}
    try:
        mir, ast = _helpers()
        decoded_bytes, ast_bytes = decoded.read_bytes(), ast_path.read_bytes()
        tree = mir.CapnpText(decoded_bytes.decode("utf-8").replace(
            "variances = [invariant]", 'variances = ["invariant"]')).parse()
        bodies = [body for body in mir.path(tree, "bodies")
                  if mir.path(body, "defPath") == function]
        if len(bodies) != 1:
            raise ValueError("missing unique local-death MIR body")
        body = bodies[0]
        ids = mir.vdi_map(body).get("tmp", [])
        if len(ids) != 1:
            raise ValueError("missing unique tmp MIR debug-local identity")
        dead = []
        for block in mir.path(body, "basicBlocks"):
            for statement in mir.path(block, "statements"):
                kind = mir.path(statement, "kind")
                if isinstance(kind, dict) and kind.get("storageDead") == {"name": ids[0]}:
                    dead.append(mir.path(statement, "sourceInfo", "span", "regular", "lo", "line"))
        if len(dead) != 1:
            raise ValueError("tmp does not have one decoded StorageDead")
        ast_tree = ast.OcamlAstText(ast_bytes.decode("utf-8")).parse()
        funcs = [node for node in ast.nodes(ast_tree, "Func")
                 if len(node.args) == 13 and node.args[4] == function and
                 node.args[10] != ast.Sym("None")]
        if len(funcs) != 1:
            raise ValueError("missing unique local-death translated function")
        markers = [node for node in ast.nodes(funcs[0].args[10], "RustStorageDeadStmt")
                   if len(node.args) == 4 and node.args[2] == ids[0] and
                   ast.location_line(node.args[1]) == dead[0]]
        if len(markers) != 1:
            raise ValueError("tmp StorageDead does not have one dedicated translated marker")
        obligation_line = ast.location_line(markers[0].args[0])
        return {"admitted": True, "mir_local": ids[0], "mir_storage_dead_line": dead[0],
                "obligation_line": obligation_line, "decoded_sha256": _sha(decoded_bytes),
                "proof_ast_sha256": _sha(ast_bytes)}
    except Exception as error:
        return {"admitted": False, "reason": f"local death MIR/AST gate failed: {error}"}


def local_unwind_gate(case: Path, meta: dict) -> dict:
    """Require tmp's actual MIR lifetime on each call successor path.

    This intentionally rejects a mere may-unwind edge with no local cleanup.
    Unknown CFG terminators are inconclusive, never silently accepted.
    """
    decoded, ast_path = case / "decode.out", case / "proof-ast.ml"
    if not decoded.is_file() or not ast_path.is_file():
        return {"admitted": False, "reason": "decoded MIR or proof AST missing"}
    try:
        mir, ast = _helpers()
        decoded_bytes, ast_bytes = decoded.read_bytes(), ast_path.read_bytes()
        tree = mir.CapnpText(decoded_bytes.decode("utf-8").replace(
            "variances = [invariant]", 'variances = ["invariant"]')).parse()
        bodies = [body for body in mir.path(tree, "bodies")
                  if mir.path(body, "defPath") == meta["name"]]
        if len(bodies) != 1:
            raise ValueError("missing unique local-unwind MIR body")
        body = bodies[0]
        ids = mir.vdi_map(body).get("tmp", [])
        if len(ids) != 1:
            raise ValueError("missing unique tmp MIR debug-local identity")
        tmp = ids[0]
        blocks = {mir.path(block, "id", "index"): block for block in
                  mir.path(body, "basicBlocks")}
        call_sites, live, dead = [], [], []
        for block_id, block in blocks.items():
            term = mir.path(block, "terminator", "kind")
            if isinstance(term, dict) and "call" in term:
                call = term["call"]
                try:
                    callee = mir.path(call, "func", "constant", "const", "val", "ty",
                                      "kind", "fnDef", "id", "name")
                except Exception:
                    callee = None
                line = mir.path(block, "terminator", "sourceInfo", "span",
                                "regular", "lo", "line")
                if (callee == meta["callee"] or
                        isinstance(callee, str) and callee.endswith("::" + meta["callee"])) and \
                        line == meta["target_line"]:
                    call_sites.append((block_id, call))
            for statement in mir.path(block, "statements"):
                kind = mir.path(statement, "kind")
                line = mir.path(statement, "sourceInfo", "span", "regular", "lo", "line")
                if isinstance(kind, dict) and kind.get("storageLive") == {"name": tmp}:
                    live.append({"block": block_id, "source_line": line})
                if isinstance(kind, dict) and kind.get("storageDead") == {"name": tmp}:
                    dead.append({"block": block_id, "source_line": line})
        if len(call_sites) != 1 or len(live) != 1 or not dead:
            raise ValueError("missing unique callback/tmp live or any tmp death")
        call_block, call = call_sites[0]
        normal = mir.path(call, "target", "something", "index")
        cleanup = mir.path(call, "unwindAction", "cleanup", "index")
        if normal == cleanup or cleanup not in blocks or not mir.path(blocks[cleanup], "isCleanup"):
            raise ValueError("callback has no distinct MIR cleanup block")
        if live[0]["source_line"] >= meta["target_line"]:
            raise ValueError("tmp StorageLive is not before callback source line")

        def successors(kind: dict) -> list[int]:
            if "goto" in kind:
                return [mir.path(kind, "goto", "index")]
            if "switchInt" in kind:
                return [mir.path(item, "index") for item in mir.path(kind, "switchInt", "targets")]
            if "call" in kind:
                return [mir.path(kind, "call", "target", "something", "index")]
            if "drop" in kind:
                return [mir.path(kind, "drop", "target", "index")]
            if "assert" in kind:
                return [mir.path(kind, "assert", "target", "index")]
            if set(kind) <= {"return", "unwindResume", "unwindTerminate", "unreachable"}:
                return []
            raise ValueError(f"unsupported post-call MIR terminator {list(kind)}")

        def every_path_reaches_dead(start: int) -> bool:
            memo = {}
            def visit(block_id: int, ancestors: frozenset[int]) -> bool:
                if block_id in ancestors or block_id not in blocks:
                    return False
                if block_id in memo:
                    return memo[block_id]
                block = blocks[block_id]
                if any(row["block"] == block_id for row in dead):
                    memo[block_id] = True
                    return True
                next_blocks = successors(mir.path(block, "terminator", "kind"))
                result = bool(next_blocks) and all(
                    visit(next_id, ancestors | {block_id}) for next_id in next_blocks)
                memo[block_id] = result
                return result
            return visit(start, frozenset())

        normal_closed = every_path_reaches_dead(normal)
        unwind_closed = every_path_reaches_dead(cleanup)
        ast_tree = ast.OcamlAstText(ast_bytes.decode("utf-8")).parse()
        funcs = [node for node in ast.nodes(ast_tree, "Func")
                 if len(node.args) == 13 and node.args[4] == meta["name"] and
                 node.args[10] != ast.Sym("None")]
        if len(funcs) != 1:
            raise ValueError("missing unique local-unwind translated caller")
        runtime = funcs[0].args[10]
        ast_live = [node for node in ast.nodes(runtime, "RustStorageLiveStmt")
                    if len(node.args) == 4 and node.args[2] == tmp and
                    ast.location_line(node.args[1]) == live[0]["source_line"]]
        ast_dead = [node for node in ast.nodes(runtime, "RustStorageDeadStmt")
                    if len(node.args) == 4 and node.args[2] == tmp and
                    ast.location_line(node.args[1]) in {row["source_line"] for row in dead}]
        switches = []
        for switch in ast.nodes(runtime, "SwitchStmt"):
            if len(switch.args) != 3:
                continue
            outcome = switch.args[1]
            if (not isinstance(outcome, ast.Node) or outcome.name != "CallExpr" or
                    len(outcome.args) != 6 or not isinstance(outcome.args[1], str) or
                    not (outcome.args[1] == meta["callee"] or
                         outcome.args[1].endswith("::" + meta["callee"])) or
                    ast.location_line(outcome.args[0]) != meta["target_line"]):
                continue
            labels = {}
            for clause in switch.args[2]:
                if not isinstance(clause, ast.Node) or clause.name != "SwitchStmtClause" or \
                        len(clause.args) != 3:
                    raise ValueError("malformed callback outcome clause")
                labels[ast.call_name(clause.args[1])] = clause.args[2]
            if set(labels) != {"returning", "unwinding"}:
                raise ValueError("callback AST omits normal or unwind outcome")
            unwind_returns = [node for node in ast.nodes(labels["unwinding"], "ReturnStmt")
                              if len(node.args) == 2 and
                              any(call.args[1] == "unwinding" for call in
                                  ast.nodes(node.args[1], "CallExpr") if len(call.args) == 6)]
            if len(unwind_returns) != 1:
                raise ValueError("callback unwind branch has no explicit outcome return")
            switches.append({"normal": True, "unwind": True,
                             "return_line": ast.location_line(unwind_returns[0].args[0])})
        admitted = (normal_closed and unwind_closed and len(ast_live) == 1 and
                    len(ast_dead) == len(dead) and len(switches) == 1)
        return {"admitted": admitted, "reason": "both MIR successors close live tmp"
                if admitted else "tmp physical lifetime does not close on both MIR successors",
                "mir_local": tmp, "call_block": call_block, "normal_successor": normal,
                "cleanup_successor": cleanup, "storage_live": live, "storage_dead": dead,
                "normal_closed": normal_closed, "unwind_closed": unwind_closed,
                "ast_live_count": len(ast_live), "ast_dead_count": len(ast_dead),
                "ast_callback_outcomes": switches,
                "decoded_sha256": _sha(decoded_bytes), "proof_ast_sha256": _sha(ast_bytes)}
    except Exception as error:
        return {"admitted": False, "reason": f"local unwind MIR/AST gate failed: {error}"}


def unwind_log_gate(log: str, meta: dict, ast_gate: dict) -> dict:
    """Observe verifier traversal of caller normal and unwind return branches."""
    headers = [(match.start(), match.group(1)) for match in re.finditer(
        r"^\s*\d+(?:\.\d+)?s: [^\s(]+\([0-9]+,[0-9]+"
        r"(?:-[0-9]+(?:,[0-9]+)?)?\): Verifying function '([^']+)'$", log, re.M)]
    segments = []
    for index, (start, function) in enumerate(headers):
        if function == meta["name"]:
            end = headers[index + 1][0] if index + 1 < len(headers) else len(log)
            segments.append(log[start:end])
    if len(segments) != 1 or not ast_gate.get("admitted"):
        return {"admitted": False, "reason": "caller log segment or AST outcome gate missing"}
    segment = segments[0]
    returns = [int(match.group(1)) for match in re.finditer(
        r"verified/lib\.rs\(([0-9]+),\d+(?:-\d+(?:,\d+)?)?\): "
        r"(?:note: )?Executing return statement", segment)]
    unwind_line = ast_gate["ast_callback_outcomes"][0]["return_line"]
    has_unwind = unwind_line in returns
    has_normal = any(line != unwind_line for line in returns)
    leak_checks = segment.count("Leak check.")
    admitted = has_unwind and has_normal and leak_checks >= 2
    return {"admitted": admitted,
            "reason": "caller log traverses both return paths and leak checks"
            if admitted else "caller log lacks one return path or leak check",
            "return_lines": returns, "ast_unwind_return_line": unwind_line,
            "normal_return_seen": has_normal, "unwind_return_seen": has_unwind,
            "leak_check_count": leak_checks}


def classify(name: str, case: Path, meta: dict, execution: dict) -> dict:
    stages = execution.get("stages", {})
    log_path = case / "verifast.log"
    log = log_path.read_text(errors="replace") if log_path.is_file() else ""
    errors = re.findall(r"^.*\berror:.*$", log, re.M | re.I)
    death_gate = local_death_gate(case) if meta["kind"] == "local_death_negative" and stages.get("decode") == 0 else None
    target = (death_gate["obligation_line"] if death_gate and death_gate.get("admitted")
              else meta["target_line"])
    at_target = rf"verified/lib\.rs\({target},\d+(?:-\d+(?:,\d+)?)?\): "
    executed = re.search(at_target + r"(?:note: )?Executing statement", log) is not None
    exact_error = len(errors) == 1 and re.search(at_target + r"error:", errors[0]) is not None
    stage_inputs_ok = (execution.get("source_unchanged_at_every_stage") is True and
                       all(stages.get(stage) == code for stage, code in
                           meta["expected_stages"].items() if stage != "verifast"))
    gate = (origin_gate(case, meta) if stages.get("decode") == 0 and
            meta["kind"] not in {"layout_diagnostic", "ghost_frontend_diagnostic", "local_death_negative"}
            else death_gate if death_gate else
            {"admitted": False, "reason": "no call-origin correlation for diagnostic"
             if meta["kind"] in {"layout_diagnostic", "ghost_frontend_diagnostic"}
             else "decode did not pass"})
    unwind_gate = (local_unwind_gate(case, meta) if meta["kind"] == "local_unwind_positive"
                   and stages.get("decode") == 0 else None)
    unwind_log = (unwind_log_gate(log, meta, unwind_gate) if
                  meta["kind"] == "local_unwind_positive" and unwind_gate else None)
    if not stage_inputs_ok:
        classification = "SETUP_REJECTION"
    elif stages.get("verifast") != 0 and (not (case / "proof-ast.ml").is_file() or
          "The name of a user-defined function must not start with 'vf__'" in log):
        classification = "FRONTEND_REJECTION"
    elif stages.get("verifast") != 0 and not executed:
        classification = "PRE_TARGET_REJECTION"
    elif meta["kind"] == "ghost_frontend_diagnostic":
        classification = "INCONCLUSIVE"
    elif meta["kind"] == "layout_diagnostic":
        if stages.get("verifast") == 0 and executed and not errors and "0 errors found" in log:
            classification = "MODEL_LAYOUT_PASS"
        elif stages.get("verifast") == 1 and executed and exact_error and "Cannot prove" in errors[0]:
            classification = "MODEL_LAYOUT_FAILURE"
        else:
            classification = "INCONCLUSIVE"
    elif meta["semantic_expectation"] == "PASS_CONTROL":
        matched = (stages.get("verifast") == 0 and gate.get("admitted") is True and
                   executed and not errors and "0 errors found" in log and
                   (meta["kind"] not in {"ordinary_contract_positive", "branch_unwind_positive", "local_unwind_positive"} or
                    ("Leak check." in log and "Executing return statement" in log)))
        if meta["kind"] == "local_unwind_positive":
            matched = (matched and bool(unwind_gate and unwind_gate.get("admitted")) and
                       bool(unwind_log and unwind_log.get("admitted")))
        classification = "PASS_CONTROL" if matched else "INCONCLUSIVE"
    else:
        matched = (stages.get("verifast") == 1 and gate.get("admitted") is True and
                   executed and exact_error and meta.get("error_contains", "Cannot prove") in errors[0])
        classification = "EXPECTED_REJECTION" if matched else "INCONCLUSIVE"
    result = {**execution, **meta, "case": name, "classification": classification,
              "semantic_evidence": classification in {"PASS_CONTROL", "EXPECTED_REJECTION"},
              "origin_gate": gate, "target_executed": executed, "errors": errors,
              "local_unwind_gate": unwind_gate,
              "unwind_log_gate": unwind_log,
              "obligation_line": target,
              "accepted": False}
    (case / "classification.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def run(evidence: Path, args, env: dict, execute_case) -> dict:
    evidence.mkdir(parents=True, exist_ok=True)
    manifest, metadata = prepare(evidence / "controls")
    rows = {}
    for spec in manifest["cases"]:
        name = spec["name"]
        case = evidence / "controls" / name
        rows[name] = classify(name, case, metadata[name], execute_case(case, args, env))
    aggregate = {"schema": manifest["schema"], "profile": args.profile,
                 "accepted": False, "manifest_sha256": _sha(MANIFEST.read_bytes()),
                 "source_file_sha256": _sha(SOURCE.read_bytes()),
                 "controls": {name: row["classification"] for name, row in rows.items()},
                 "case_details": {name: row for name, row in rows.items()},
                 "all_matched": all(row["semantic_evidence"] for row in rows.values()
                                    if row["kind"] not in {"layout_diagnostic", "ghost_frontend_diagnostic"}),
                 "layout_diagnostics": {name: row["classification"] for name, row in rows.items()
                                        if row["kind"] == "layout_diagnostic"},
                 "ghost_frontend_diagnostic": rows["origin_ghost_reserved_call"]["classification"],
                 "evidence_class": manifest["evidence_class"]}
    (evidence / "origin-results.json").write_text(json.dumps(aggregate, indent=2) + "\n")
    return aggregate
