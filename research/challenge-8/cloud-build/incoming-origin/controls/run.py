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


def _mir_successors(mir, block: dict) -> list[int]:
    """Decode the successor forms used by MIR terminators; unknown is fatal."""
    kind = mir.path(block, "terminator", "kind")
    if not isinstance(kind, dict) or len(kind) != 1:
        raise ValueError("MIR terminator is not a single checked variant")
    if "goto" in kind:
        return [mir.path(kind, "goto", "index")]
    if "switchInt" in kind:
        switch = kind["switchInt"]
        edges = [mir.path(edge, "index") for edge in mir.path(switch, "targets")]
        # This exporter's SwitchInt target vector includes its fallback arm.
        return list(dict.fromkeys(edges))
    if "call" in kind:
        call = kind["call"]
        edges = []
        target = mir.path(call, "target")
        if isinstance(target, dict) and "something" in target:
            edges.append(mir.path(target, "something", "index"))
        unwind = mir.path(call, "unwindAction")
        if isinstance(unwind, dict) and "cleanup" in unwind:
            edges.append(mir.path(unwind, "cleanup", "index"))
        elif not (isinstance(unwind, dict) and set(unwind) <= {"continue", "unreachable"}):
            raise ValueError("unknown MIR call unwind action")
        return list(dict.fromkeys(edges))
    if "drop" in kind:
        drop = kind["drop"]
        edges = [mir.path(drop, "target", "index")]
        unwind = mir.path(drop, "unwindAction")
        if isinstance(unwind, dict) and "cleanup" in unwind:
            edges.append(mir.path(unwind, "cleanup", "index"))
        elif not (isinstance(unwind, dict) and set(unwind) <= {"continue", "unreachable"}):
            raise ValueError("unknown MIR drop unwind action")
        return list(dict.fromkeys(edges))
    if "assert" in kind:
        assertion = kind["assert"]
        edges = [mir.path(assertion, "target", "index")]
        unwind = mir.path(assertion, "unwindAction")
        if isinstance(unwind, dict) and "cleanup" in unwind:
            edges.append(mir.path(unwind, "cleanup", "index"))
        elif not (isinstance(unwind, dict) and set(unwind) <= {"continue", "unreachable"}):
            raise ValueError("unknown MIR assert unwind action")
        return list(dict.fromkeys(edges))
    if "falseEdge" in kind:
        edge = kind["falseEdge"]
        return list(dict.fromkeys([mir.path(edge, "realTarget", "index"),
                                   mir.path(edge, "imaginaryTarget", "index")]))
    if "falseUnwind" in kind:
        edge = kind["falseUnwind"]
        result = [mir.path(edge, "realTarget", "index")]
        unwind = mir.path(edge, "unwindAction")
        if isinstance(unwind, dict) and "cleanup" in unwind:
            result.append(mir.path(unwind, "cleanup", "index"))
        elif not (isinstance(unwind, dict) and set(unwind) <= {"continue", "unreachable"}):
            raise ValueError("unknown MIR false-unwind action")
        return list(dict.fromkeys(result))
    if set(kind) <= {"return", "unwindResume", "unwindTerminate", "unreachable", "terminate"}:
        return []
    raise ValueError(f"unsupported MIR CFG terminator {list(kind)}")


def _dominators(mir, body: dict) -> tuple[dict[int, dict[int, bool]], dict[int, dict]]:
    blocks = {mir.path(block, "id", "index"): block
              for block in mir.path(body, "basicBlocks")}
    if not blocks or 0 not in blocks:
        raise ValueError("MIR CFG has no entry block")
    edges = {block_id: _mir_successors(mir, block)
             for block_id, block in blocks.items()}
    if any(successor not in blocks for values in edges.values() for successor in values):
        raise ValueError("MIR CFG edge names a missing block")
    reachable, todo = set(), [0]
    while todo:
        current = todo.pop()
        if current not in reachable:
            reachable.add(current)
            todo.extend(edges[current])
    predecessors = {block_id: set() for block_id in reachable}
    for block_id in reachable:
        for successor in edges[block_id]:
            if successor in reachable:
                predecessors[successor].add(block_id)
    dom = {block_id: ({0} if block_id == 0 else set(reachable))
           for block_id in reachable}
    changed = True
    while changed:
        changed = False
        for block_id in reachable - {0}:
            parents = predecessors[block_id]
            common = set.intersection(*(dom[parent] for parent in parents)) if parents else set()
            value = {block_id} | common
            if value != dom[block_id]:
                dom[block_id] = value
                changed = True
    return ({block_id: {other: other in members for other in reachable}
             for block_id, members in dom.items()}, blocks)


def _mir_line_col(mir, source_info: dict) -> tuple[int, int]:
    span = mir.path(source_info, "span", "regular", "lo")
    line, col = mir.path(span, "line"), mir.path(span, "col", "pos")
    if not isinstance(line, int) or not isinstance(col, int):
        raise ValueError("MIR source location is malformed")
    return line, col


def _ast_line_col(ast, location) -> tuple[int, int]:
    text = ast.loc(location)
    match = re.fullmatch(r"verified/lib\.rs\(([1-9][0-9]*),([1-9][0-9]*)(?:-[0-9]+(?:,[0-9]+)?)?\)", text)
    if match is None:
        raise ValueError(f"AST location is outside checked source: {text}")
    return int(match.group(1)), int(match.group(2))


def _ast_runtime_statements(ast, runtime) -> list:
    if not isinstance(runtime, ast.Node) or runtime.name != "Some" or len(runtime.args) != 1:
        raise ValueError("translated runtime body is not a Some block")
    body = runtime.args[0]
    if not isinstance(body, tuple) or len(body) != 2 or not isinstance(body[0], list):
        raise ValueError("translated runtime block has an unknown shape")
    return body[0]


def _ast_local_bindings(ast, runtime) -> tuple[dict[str, str], set[str]]:
    """Bind exported MIR local IDs to AST names and require a matching DeclStmt."""
    declared = set()
    for declaration in ast.nodes(runtime, "DeclStmt"):
        if len(declaration.args) != 2 or not isinstance(declaration.args[1], list):
            raise ValueError("malformed AST DeclStmt")
        for row in declaration.args[1]:
            if not isinstance(row, tuple) or len(row) != 5 or not isinstance(row[2], str):
                raise ValueError("malformed AST local declaration")
            declared.add(row[2])
    bindings: dict[str, set[str]] = {}
    for constructor in ("RustStorageLiveStmt", "RustStorageDeadStmt"):
        for event in ast.nodes(runtime, constructor):
            if len(event.args) != 4 or not all(isinstance(event.args[i], str) for i in (2, 3)):
                raise ValueError(f"malformed {constructor} local binding")
            bindings.setdefault(event.args[2], set()).add(event.args[3])
    local_names = {}
    for local, names in bindings.items():
        if len(names) != 1:
            raise ValueError(f"MIR local {local} maps to multiple AST names")
        name = next(iter(names))
        if name not in declared:
            raise ValueError(f"AST local {name} has no matching DeclStmt")
        local_names[local] = name
    return local_names, declared


def _check_ast_mir_branch_targets(ast, runtime, mir, body, blocks) -> dict:
    """Check explicit AST branch labels against source-line matched MIR edges.

    This checks emitted branch targets where the translator exposes labels. It
    does not claim that the complete MIR and AST graphs are isomorphic.
    """
    statements = _ast_runtime_statements(ast, runtime)
    labels = {}
    for index, statement in enumerate(statements):
        if isinstance(statement, ast.Node) and statement.name == "LabelStmt":
            if len(statement.args) != 2 or not isinstance(statement.args[1], str):
                raise ValueError("malformed AST block label")
            label = statement.args[1]
            if label in labels:
                raise ValueError(f"duplicate AST block label {label}")
            labels[label] = index
    label_ids = set()
    for label in labels:
        if not re.fullmatch(r"[0-9]+", label):
            raise ValueError(f"non-numeric AST MIR block label {label}")
        label_ids.add(int(label))
    if not label_ids <= set(blocks):
        raise ValueError("AST block label has no decoded MIR block")
    branch_checks = []
    for branch in ast.nodes(runtime, "IfStmt"):
        if len(branch.args) != 4:
            raise ValueError("malformed AST IfStmt")
        line = ast.location_line(branch.args[0])
        targets = []
        for arm in branch.args[2:4]:
            gotos = ast.nodes(arm, "GotoStmt")
            if len(gotos) != 1 or len(gotos[0].args) != 2:
                raise ValueError("AST IfStmt arm is not one explicit MIR goto")
            targets.append(gotos[0].args[1])
        if any(target not in labels for target in targets):
            raise ValueError("AST branch targets a missing block label")
        source_blocks = []
        for block_id, block in blocks.items():
            term = mir.path(block, "terminator")
            kind = mir.path(term, "kind")
            src_line, _ = _mir_line_col(mir, mir.path(term, "sourceInfo"))
            if src_line == line and isinstance(kind, dict) and "switchInt" in kind:
                source_blocks.append((block_id, [mir.path(row, "index") for row in
                                                  mir.path(kind, "switchInt", "targets")]))
        if len(source_blocks) != 1 or set(source_blocks[0][1]) != {int(t) for t in targets}:
            raise ValueError("AST IfStmt labels do not match its source-line MIR switch targets")
        branch_checks.append({"source_line": line, "mir_block": source_blocks[0][0],
                              "targets": sorted(int(target) for target in targets)})
    # Labels and gotos are compared against the decoded block inventory even
    # when no source-level conditional maps to the goto (for example a loop).
    gotos = []
    for node in ast.nodes(runtime, "GotoStmt"):
        if len(node.args) != 2 or not isinstance(node.args[1], str) or node.args[1] not in labels:
            raise ValueError("AST GotoStmt target has no LabelStmt")
        target = int(node.args[1])
        if target not in blocks:
            raise ValueError("AST GotoStmt target has no decoded MIR block")
        gotos.append(target)
    return {"label_count": len(labels), "goto_count": len(gotos),
            "if_branch_checks": branch_checks,
            "scope": "explicit branch labels and goto targets; not full graph equivalence"}


def _mir_label_regions(mir, blocks, labels: set[int]) -> dict[int, list[int]]:
    """Expand emitted AST labels across MIR's flattened single-successor blocks."""
    edges = {block_id: _mir_successors(mir, block) for block_id, block in blocks.items()}
    regions = {}
    claimed = set()
    for start in labels:
        region, current, seen = [], start, set()
        while current not in seen:
            if current in claimed:
                raise ValueError("AST-labelled MIR linear regions overlap")
            seen.add(current)
            claimed.add(current)
            region.append(current)
            next_blocks = edges[current]
            # A branch or call outcome is represented explicitly in AST; each
            # successor starts another emitted label or a terminal path.
            if len(next_blocks) != 1 or next_blocks[0] in labels:
                break
            current = next_blocks[0]
        if current in seen and edges[current] == [current]:
            raise ValueError("cycle inside an unlabelled MIR linear region")
        regions[start] = region
    return regions


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
        obligation_error_line = None
        if spec["kind"] == "unwind_contract_negative":
            unwind_posts = [i + 1 for i, line in enumerate(lines)
                            if "on_unwind_ens" in line]
            if len(unwind_posts) != 1:
                raise RuntimeError(f"{name} has no unique caller unwind postcondition")
            obligation_error_line = unwind_posts[0]
        case = evidence / name
        extern_spec = spec.get("extern_spec")
        if extern_spec is None:
            extern_spec_text = ""
        else:
            required = {"signature", "req", "ens", "on_unwind_ens"}
            if set(extern_spec) != required:
                raise RuntimeError(f"malformed extern spec contract for {name}")
            extern_spec_text = (extern_spec["signature"] + "\n" +
                                "//@ req " + extern_spec["req"] + ";\n" +
                                "//@ ens " + extern_spec["ens"] + ";\n" +
                                "//@ on_unwind_ens " + extern_spec["on_unwind_ens"] + ";\n")
        for tree in ("original", "verified"):
            (case / tree).mkdir(parents=True, exist_ok=True)
            (case / tree / "lib.rs").write_bytes(unit)
            (case / tree / "origin-control.rsspec").write_text(extern_spec_text)
        # execute_case runs from the case root, so the verifast_options path is
        # resolved here. Tree-local copies let the saved original/verified
        # source bundles retain the exact header input alongside each source.
        (case / "origin-control.rsspec").write_text(extern_spec_text)
        metadata[name] = {**spec, "target_line": targets[0],
                          **({"obligation_error_line": obligation_error_line}
                             if obligation_error_line is not None else {}),
                          "source_sha256": _sha(unit),
                          "extern_spec_sha256": _sha(extern_spec_text.encode()),
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
        assignments = []
        dominators, blocks = _dominators(mir, body)
        for block_id, block in blocks.items():
            term = mir.path(block, "terminator")
            kind = mir.path(term, "kind")
            if isinstance(kind, dict) and "call" in kind:
                call = kind["call"]
                callee = mir.path(call, "func", "constant", "const", "val", "ty",
                                  "kind", "fnDef", "id", "name")
                line, col = _mir_line_col(mir, mir.path(term, "sourceInfo"))
                if callee == meta["callee"] or callee.endswith("::" + meta["callee"]):
                    operands = mir.path(call, "args")
                    if len(operands) != 1 or not isinstance(operands[0], dict) or \
                            set(operands[0]) not in ({"copy"}, {"move"}):
                        raise ValueError("target MIR call does not carry one source argument")
                    argument_raw = mir.local(next(iter(operands[0].values())))
                    target_option = mir.path(call, "target")
                    if not isinstance(target_option, dict) or set(target_option) not in (
                            {"nothing"}, {"something"}):
                        raise ValueError("MIR call target is not a checked Option")
                    unwind_action = mir.path(call, "unwindAction")
                    if meta["kind"] in {"branch_unwind_positive", "local_unwind_positive",
                                         "unwind_contract_negative"} and (
                            not isinstance(unwind_action, dict) or
                            set(unwind_action) not in ({"continue"}, {"cleanup"})):
                        raise ValueError("branch callback has no MIR unwind successor")
                    mir_calls.append({"callee": callee, "source_line": line,
                                      "source_col": col, "block": block_id,
                                      "has_normal_target": "something" in target_option,
                                      "argument_raw": argument_raw,
                                      "unwind_action": unwind_action})
            for statement_index, stmt in enumerate(mir.path(block, "statements")):
                stmt_kind = mir.path(stmt, "kind")
                if isinstance(stmt_kind, dict) and "assign" in stmt_kind:
                    assignment = stmt_kind["assign"]
                    try:
                        lhs = mir.local(mir.path(assignment, "lhsPlace"))
                        rhs = mir.path(assignment, "rhsRvalue")
                        if isinstance(rhs, dict) and "use" in rhs and isinstance(rhs["use"], dict) and \
                                set(rhs["use"]) in ({"copy"}, {"move"}):
                            source_raw = mir.local(next(iter(rhs["use"].values())))
                            assignments.append({"lhs": lhs, "rhs": source_raw,
                                                "block": block_id,
                                                "statement_index": statement_index})
                    except Exception:
                        pass  # Only whole-local copy/move edges can certify this call argument.
                for key, constructor in (("storageLive", "RustStorageLiveStmt"),
                                         ("storageDead", "RustStorageDeadStmt")):
                    if isinstance(stmt_kind, dict) and key in stmt_kind:
                        local = mir.path(stmt_kind, key, "name")
                        line, col = _mir_line_col(mir, mir.path(stmt, "sourceInfo"))
                        mir_events.append({"constructor": constructor, "local": local,
                                           "line": line, "col": col, "block": block_id,
                                           "statement_index": statement_index})
        target = meta["target_line"]
        mir_calls = [row for row in mir_calls if row["source_line"] == target]
        if len(mir_calls) != 1:
            raise ValueError(f"expected one matching MIR call terminator at target; found {len(mir_calls)}")
        debug_sources = mir.vdi_map(body).get(meta["argument"], [])
        if len(debug_sources) != 1:
            raise ValueError("source argument lacks unique MIR debug-local identity")
        raw_argument = mir_calls[0]["argument_raw"]
        call_block = mir_calls[0]["block"]
        call_index = len(mir.path(blocks[call_block], "statements"))

        def resolve_use(local: str, use_block: int, use_index: int,
                        seen: frozenset[str]) -> list[str]:
            if local in seen:
                raise ValueError("cyclic MIR copy/move chain")
            candidates = [definition for definition in assignments
                          if definition["lhs"] == local and
                          dominators[use_block].get(definition["block"], False) and
                          (definition["block"] != use_block or
                           definition["statement_index"] < use_index)]
            maximal = []
            for definition in candidates:
                shadowed = any(
                    other is not definition and
                    dominators[other["block"]].get(definition["block"], False) and
                    (other["block"] != definition["block"] or
                     other["statement_index"] > definition["statement_index"])
                    for other in candidates)
                if not shadowed:
                    maximal.append(definition)
            if not maximal and local == debug_sources[0]:
                return [local]
            if len(maximal) != 1:
                raise ValueError("MIR argument local has no unique reaching copy/move definition")
            definition = maximal[0]
            return [local] + resolve_use(definition["rhs"], definition["block"],
                                         definition["statement_index"], seen | {local})

        copy_chain = resolve_use(raw_argument, call_block, call_index, frozenset())
        if meta["kind"] == "diverging_extern" and mir_calls[0]["has_normal_target"]:
            raise ValueError("diverging MIR call unexpectedly has a normal target")

        ast_tree = ast.OcamlAstText(ast_bytes.decode("utf-8")).parse()
        functions = [node for node in ast.nodes(ast_tree, "Func")
                     if len(node.args) == 13 and node.args[4] == meta["name"] and
                     node.args[10] != ast.Sym("None")]
        if len(functions) != 1:
            raise ValueError(f"expected one translated caller body; found {len(functions)}")
        runtime = functions[0].args[10]
        outcome_posts = [clause.args[1] for clause in
                         ast.nodes(functions[0].args[8], "SwitchExprClause")
                         if len(clause.args) >= 2 and isinstance(clause.args[1], str)]
        caller_unwind_post = ("returning" in outcome_posts and
                              "unwinding" in outcome_posts)
        if meta["kind"] == "unwind_contract_negative" and not caller_unwind_post:
            raise ValueError("caller AST does not expose both postcondition outcome branches")
        ast_bindings, ast_declared = _ast_local_bindings(ast, runtime)
        ast_cfg = _check_ast_mir_branch_targets(ast, runtime, mir, body, blocks)
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
        if raw_argument == debug_sources[0]:
            expected_ast_argument = meta["argument"]
        else:
            expected_ast_argument = ast_bindings.get(raw_argument)
        if expected_ast_argument is None or argument != expected_ast_argument:
            raise ValueError("AST call argument is not translated from the exact MIR call operand")
        ast_events_by_block = {}
        current_label = None
        for statement in _ast_runtime_statements(ast, runtime):
            if isinstance(statement, ast.Node) and statement.name == "LabelStmt":
                current_label = int(statement.args[1])
                ast_events_by_block.setdefault(current_label, [])
            if current_label is not None:
                for constructor in ("RustStorageLiveStmt", "RustStorageDeadStmt"):
                    for node in ast.nodes(statement, constructor):
                        if len(node.args) != 4:
                            raise ValueError(f"malformed {constructor} in labelled AST block")
                        line, col = _ast_line_col(ast, node.args[1])
                        ast_events_by_block[current_label].append(
                            {"constructor": constructor, "local": node.args[2],
                             "line": line, "col": col})
        labels = {int(statement.args[1]) for statement in _ast_runtime_statements(ast, runtime)
                  if isinstance(statement, ast.Node) and statement.name == "LabelStmt"}
        mir_regions = _mir_label_regions(mir, blocks, labels)
        checked_event_blocks = []
        matched_mir_events = []
        matched_ast_event_count = 0
        for label, region in mir_regions.items():
            ast_rows = ast_events_by_block.get(label, [])
            matched_ast_event_count += len(ast_rows)
            mir_rows = []
            for block_id in region:
                mir_rows.extend({"constructor": event["constructor"], "local": event["local"],
                                 "line": event["line"], "col": event["col"] + 1}
                                for event in sorted((item for item in mir_events
                                                     if item["block"] == block_id),
                                                    key=lambda item: item["statement_index"]))
                matched_mir_events.extend(item for item in mir_events
                                          if item["block"] == block_id)
            if ast_rows != mir_rows:
                raise ValueError(f"ordered lifecycle events differ in AST/MIR labelled region {label}")
            checked_event_blocks.extend(region)
        if len(matched_mir_events) != len(mir_events):
            raise ValueError("some MIR lifecycle events fall outside all emitted AST label regions")
        if matched_ast_event_count != sum(map(len, ast_events_by_block.values())):
            raise ValueError("some AST lifecycle events fall outside emitted AST label regions")
        return {"admitted": True, "reason": "source call remains an ordinary CallExpr; lifecycle events match MIR provenance",
                "decoded_sha256": _sha(decoded_bytes), "proof_ast_sha256": _sha(ast_bytes),
                "mir_call": mir_calls[0], "argument_copy_chain": copy_chain,
                "source_argument_mir_local": debug_sources[0],
                "ast_call": {"callee": ast_calls[0].args[1],
                             "argument": argument, "source_line": target},
                "caller_unwind_post": caller_unwind_post,
                "mir_lifecycle_count": len(mir_events),
                "ast_lifecycle_count": matched_ast_event_count,
                "ast_declared_local_count": len(ast_declared),
                "ast_mir_cfg": ast_cfg, "ordered_lifecycle_blocks": checked_event_blocks,
                "ast_mir_linear_regions": mir_regions,
                "cfg_correspondence": "target call reaching definitions, emitted branch labels, and ordered events across flattened single-successor MIR regions; not full graph equivalence"}
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
    """Check tmp's MIR lifetime and both translated callback outcomes.

    Rust MIR may encode a foreign/unwind-capable call with unwindAction=continue,
    leaving the language-level unwind outcome to the translator. In that case
    this gate checks normal MIR lifetime plus explicit AST outcomes; it does not
    claim a MIR cleanup edge or full MIR/AST unwind-graph correspondence.
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
        unwind_action = mir.path(call, "unwindAction")
        if not isinstance(unwind_action, dict) or len(unwind_action) != 1:
            raise ValueError("callback has an unknown MIR unwind action")
        if "cleanup" in unwind_action:
            cleanup = mir.path(unwind_action, "cleanup", "index")
            if normal == cleanup or cleanup not in blocks or not mir.path(blocks[cleanup], "isCleanup"):
                raise ValueError("callback cleanup target is not a distinct MIR cleanup block")
            mir_unwind_mode = "cleanup block"
        elif "continue" in unwind_action:
            cleanup = None
            mir_unwind_mode = "continue; no MIR unwind successor to audit"
        else:
            raise ValueError(f"unsupported callback MIR unwind action {list(unwind_action)}")
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
        unwind_closed = (every_path_reaches_dead(cleanup) if cleanup is not None else None)
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
        admitted = (normal_closed and (unwind_closed is not False) and len(ast_live) == 1 and
                    len(ast_dead) == len(dead) and len(switches) == 1)
        return {"admitted": admitted, "reason":
                ("normal MIR lifetime and both AST callback outcomes checked"
                 if admitted and cleanup is None else
                 "both MIR successors close live tmp" if admitted else
                 "local lifetime or translated callback outcome check failed"),
                "mir_local": tmp, "call_block": call_block, "normal_successor": normal,
                "unwind_action": unwind_action, "mir_unwind_mode": mir_unwind_mode,
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
    error_line = meta.get("obligation_error_line", target)
    at_error_line = rf"verified/lib\.rs\({error_line},\d+(?:-\d+(?:,\d+)?)?\): "
    exact_error = len(errors) == 1 and re.search(at_error_line + r"error:", errors[0]) is not None
    unwind_resource_error = (meta["kind"] == "unwind_contract_negative" and
                             meta.get("error_resource", "") in errors[0] and
                             re.search(r"\(" + re.escape(meta.get("error_address", "")) +
                                       r"(?:,|\))", errors[0]) is not None) if errors else False
    stage_inputs_ok = (execution.get("source_unchanged_at_every_stage") is True and
                       all(stages.get(stage) == code for stage, code in
                           meta["expected_stages"].items() if stage != "verifast"))
    spec_paths = [case / "origin-control.rsspec"] + [
        case / tree / "origin-control.rsspec" for tree in ("original", "verified")]
    expected_spec_sha = meta.get("extern_spec_sha256")
    spec_inputs_ok = (expected_spec_sha is not None and
                      all(path.is_file() and _sha(path.read_bytes()) == expected_spec_sha
                          for path in spec_paths) and
                      spec_paths[0].read_bytes() == spec_paths[1].read_bytes())
    stage_inputs_ok = stage_inputs_ok and spec_inputs_ok
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
                   executed and exact_error and
                   meta.get("error_contains", "Cannot prove") in errors[0] and
                   (meta["kind"] != "unwind_contract_negative" or
                    (gate.get("caller_unwind_post") is True and unwind_resource_error)))
        classification = "EXPECTED_REJECTION" if matched else "INCONCLUSIVE"
    result = {**execution, **meta, "case": name, "classification": classification,
              "semantic_evidence": classification in {"PASS_CONTROL", "EXPECTED_REJECTION"},
              "extern_spec_inputs_unchanged": spec_inputs_ok,
              "origin_gate": gate, "target_executed": executed, "errors": errors,
              "local_unwind_gate": unwind_gate,
              "unwind_log_gate": unwind_log,
              "obligation_line": target,
              "obligation_error_line": error_line,
              "unwind_resource_error": unwind_resource_error,
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
