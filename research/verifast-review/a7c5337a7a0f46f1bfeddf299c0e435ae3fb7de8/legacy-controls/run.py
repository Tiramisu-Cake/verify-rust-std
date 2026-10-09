#!/usr/bin/env python3
"""Prepare and strictly classify incoming-span mechanism controls."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "span-controls.rs"
MANIFEST = HERE / "MANIFEST.json"
REPO = HERE.parents[4]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"missing parser helper: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _helpers():
    base = _load("incoming_span_base_prove", REPO / "research/challenge-8/merge/overnight/copy-on-drop-prove.py")
    return base.mir_helper, base.ast_helper


def retired_mir_ast_gate(case: Path, function: str = "span_retired_local_reuse") -> dict:
    """Bind retirement rejection to decoded MIR events and internal MIR-origin statements."""
    decoded = case / "decode.out"
    translated = case / "proof-ast.ml"
    if not decoded.is_file() or not translated.is_file():
        return {"admitted": False, "reason": "decoded MIR or translated proof AST absent"}
    try:
        mir, ast = _helpers()
        decode_bytes = decoded.read_bytes()
        ast_bytes = translated.read_bytes()
        raw = decode_bytes.decode("utf-8")
        raw = raw.replace("variances = [invariant]", 'variances = ["invariant"]')
        tree = mir.CapnpText(raw).parse()
        bodies = [body for body in mir.path(tree, "bodies")
                  if mir.path(body, "defPath") == function]
        if len(bodies) != 1:
            raise ValueError(f"expected one decoded MIR body for {function}")
        body = bodies[0]
        names = mir.vdi_map(body)

        def named_local(source_name: str) -> str:
            ids = names.get(source_name, [])
            if len(ids) != 1:
                raise ValueError(f"expected one MIR debug-local mapping for {source_name}")
            local_id = ids[0]
            declarations = [decl for decl in mir.path(body, "localDecls")
                            if mir.path(decl, "id", "name") == local_id]
            if len(declarations) != 1:
                raise ValueError(f"MIR local declaration identity is ambiguous for {source_name}")
            return local_id

        tmp0, tmp1 = named_local("tmp0"), named_local("tmp1")

        def events(event_name: str, local_id: str) -> list[dict]:
            result = []
            for block in mir.path(body, "basicBlocks"):
                block_id = mir.path(block, "id", "index")
                for position, statement in enumerate(mir.path(block, "statements")):
                    kind = mir.path(statement, "kind")
                    if kind.get(event_name) == {"name": local_id}:
                        if set(kind) != {event_name}:
                            raise ValueError(f"{event_name} statement has extra MIR operations")
                        line = mir.path(statement, "sourceInfo", "span", "regular", "lo", "line")
                        result.append({"block": block_id, "statement": position,
                                       "source_line": line, "local": local_id})
            return result

        dead_events = events("storageDead", tmp0)
        live_events = events("storageLive", tmp1)
        if len(dead_events) != 1 or len(live_events) != 1:
            raise ValueError("expected exactly one tmp0 StorageDead and tmp1 StorageLive")
        dead, live = dead_events[0], live_events[0]
        same_block_order = (dead["block"] == live["block"] and
                            dead["statement"] < live["statement"])
        if not same_block_order:
            raise ValueError("MIR does not order tmp0 StorageDead before tmp1 StorageLive in one block")

        ast_tree = ast.OcamlAstText(ast_bytes.decode("utf-8")).parse()
        markers = [node for node in ast.nodes(ast_tree, "RustStorageDeadStmt") +
                   ast.nodes(ast_tree, "RustStorageLiveStmt")]
        # Preserve the AST traversal order across both event constructors.
        all_nodes = []
        def walk(value):
            if isinstance(value, ast.Node):
                all_nodes.append(value)
                for arg in value.args: walk(arg)
            elif isinstance(value, (list, tuple)):
                for arg in value: walk(arg)
        walk(ast_tree)
        markers = [node for node in all_nodes if node.name in
                   {"RustStorageDeadStmt", "RustStorageLiveStmt"}]

        def translated_marker(constructor, source_name, mir_local_id, source_line):
            matches = [(index, node) for index, node in enumerate(markers)
                       if node.name == constructor and len(node.args) == 4 and
                       node.args[2] == mir_local_id and node.args[3] == source_name]
            if len(matches) != 1:
                raise ValueError(f"expected exactly one translated {constructor} event")
            index, node = matches[0]
            line = ast.location_line(node.args[1])
            if line != source_line:
                raise ValueError(f"translated {constructor} original MIR span differs")
            return {"constructor": constructor, "mir_local": mir_local_id,
                    "argument": source_name, "source_line": line}, index

        dead_marker, dead_index = translated_marker(
            "RustStorageDeadStmt", "tmp0", tmp0, dead["source_line"])
        live_marker, live_index = translated_marker(
            "RustStorageLiveStmt", "tmp1", tmp1, live["source_line"])
        ast_order = dead_index < live_index
        if not ast_order:
            raise ValueError("translated AST reverses StorageDead/StorageLive markers")
        return {
            "admitted": True,
            "reason": "decoded MIR and internal events agree on retirement order",
            "decode_sha256": hashlib.sha256(decode_bytes).hexdigest(),
            "proof_ast_sha256": hashlib.sha256(ast_bytes).hexdigest(),
            "mir_body": function,
            "locals": {"tmp0": tmp0, "tmp1": tmp1},
            "storage_dead": dead,
            "storage_live": live,
            "same_block_order": same_block_order,
            "translated_ast": {"storage_dead": dead_marker,
                                "storage_live": live_marker,
                                "order": ast_order},
        }
    except Exception as error:
        return {"admitted": False, "reason": f"retirement MIR/AST gate failed: {error}"}


def prepare(evidence: Path) -> tuple[dict, dict]:
    source = SOURCE.read_bytes()
    manifest_bytes = MANIFEST.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "incoming-span-lifetime-controls-v1" or manifest.get("accepted") is not False:
        raise RuntimeError("control manifest schema/acceptance pin mismatch")
    head = source.split(b"// CASE_BEGIN ", 1)[0]
    result = {}
    for spec in manifest["cases"]:
        function = spec["name"]
        marker = spec["target"]
        begin = b"// CASE_BEGIN " + function.encode() + b"\n"
        end = b"// CASE_END " + function.encode()
        if source.count(begin) != 1 or source.count(end) != 1:
            raise RuntimeError(f"expected unique case delimiters for {function}")
        body = source.split(begin, 1)[1].split(end, 1)[0]
        unit = head + body
        declaration = b"pub unsafe fn " + function.encode()
        if unit.count(declaration) != 1 or unit.count(b"pub unsafe fn ") != 1:
            raise RuntimeError(f"fixture {function} is not isolated")
        lines = unit.decode().splitlines()
        matches = [i + 1 for i, line in enumerate(lines) if "TARGET: " + marker in line]
        if len(matches) != 1:
            raise RuntimeError(f"expected one exact target marker for {function}")
        case = evidence / function
        for tree in ("original", "verified"):
            (case / tree).mkdir(parents=True, exist_ok=True)
            (case / tree / "lib.rs").write_bytes(unit)
        read_lines = []
        if spec.get("requires_reads_before_target"):
            for needle in (b"    let first = unsafe { *p };\n",
                           b"    let second = unsafe { *q };\n"):
                if unit.count(needle) != 1:
                    raise RuntimeError(f"required alias read absent in {function}")
                read_lines.append(unit[:unit.index(needle)].count(b"\n") + 1)
        result[function] = {
            **spec,
            "target_line": matches[0],
            "read_lines": read_lines,
            "expected_stages": {**manifest["required_stages"], "verifast": spec["verifast"]},
            "source_sha256": hashlib.sha256(unit).hexdigest(),
        }
    return manifest, result


def classify(function: str, case: Path, meta: dict, execution: dict) -> dict:
    stages = execution.get("stages", {})
    log_path = case / "verifast.log"
    log = log_path.read_text(errors="replace") if log_path.exists() else ""
    errors = re.findall(r"^.*\berror:.*$", log, re.M | re.I)
    target_line = meta["target_line"]
    line_pattern = rf"verified/lib\.rs\({target_line},\d+(?:-\d+(?:,\d+)?)?\): error:"
    exact_target = len(errors) == 1 and re.search(line_pattern, errors[0]) is not None
    target_executed = re.search(
        rf"verified/lib\.rs\({target_line},\d+(?:-\d+(?:,\d+)?)?\): "
        r"(?:note: )?Executing statement", log) is not None
    reads_executed = all(re.search(
        rf"verified/lib\.rs\({line},\d+(?:-\d+(?:,\d+)?)?\): "
        r"(?:note: )?Executing statement", log) is not None
        for line in meta["read_lines"])
    pipeline_ok = (execution.get("source_unchanged_at_every_stage") is True and
                   all(stages.get(stage) == code for stage, code in
                       meta["expected_stages"].items()))
    retirement_gate = (retired_mir_ast_gate(case, function)
                       if meta.get("requires_retired_mir_ast_gate") else None)
    if meta["expectation"] == "PASS_CONTROL":
        matched = (pipeline_ok and stages.get("verifast") == 0 and not errors and
                   target_executed and "Leak check." in log and
                   "0 errors found" in log and "Executing return statement" in log)
        classification = "PASS_CONTROL" if matched else "INCONCLUSIVE"
    else:
        intended = (exact_target and "Cannot prove" in errors[0] and
                    target_executed and
                    (not meta.get("requires_reads_before_target") or reads_executed) and
                    (not meta.get("requires_retired_mir_ast_gate") or
                     bool(retirement_gate and retirement_gate.get("admitted") is True)))
        classification = ("EXPECTED_REJECTION" if pipeline_ok and intended
                          else "INCONCLUSIVE")
    result = {**execution, **meta, "case": function, "errors": errors,
              "target_executed": target_executed,
              "reads_executed": reads_executed,
              "retired_mir_ast_gate": retirement_gate,
              "classification": classification, "accepted": False,
              "meaning": "incoming-span mechanism control only"}
    (case / "classification.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def run(evidence: Path, args, env: dict, execute_case) -> dict:
    evidence.mkdir(parents=True, exist_ok=True)
    manifest, metadata = prepare(evidence / "controls")
    results = {}
    for spec in manifest["cases"]:
        name = spec["name"]
        case = evidence / "controls" / name
        execution = execute_case(case, args, env)
        results[name] = classify(name, case, metadata[name], execution)
    aggregate = {
        "profile": args.profile,
        "accepted": False,
        "manifest_sha256": hashlib.sha256(MANIFEST.read_bytes()).hexdigest(),
        "controls": {name: row["classification"] for name, row in results.items()},
        "case_details": {name: {
            "source_sha256": row["source_sha256"],
            "target_line": row["target_line"],
            "expected_stages": row["expected_stages"],
            "read_lines": row["read_lines"],
            "classification": row["classification"],
            "retired_mir_ast_gate": row["retired_mir_ast_gate"],
        } for name, row in results.items()},
        "case_artifacts": {name: {
            "directory": f"controls/{name}",
            "log": f"controls/{name}/verifast.log",
            "classification": f"controls/{name}/classification.json",
        } for name in results},
        "all_matched": all(row["classification"] in {"PASS_CONTROL", "EXPECTED_REJECTION"}
                            for row in results.values()),
        "evidence_class": manifest["evidence_class"],
    }
    (evidence / "span-results.json").write_text(json.dumps(aggregate, indent=2) + "\n")
    return aggregate
