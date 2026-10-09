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
                    mir_calls.append({"callee": callee, "source_line": line,
                                      "has_normal_target": "something" in target_option})
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


def classify(name: str, case: Path, meta: dict, execution: dict) -> dict:
    stages = execution.get("stages", {})
    log_path = case / "verifast.log"
    log = log_path.read_text(errors="replace") if log_path.is_file() else ""
    errors = re.findall(r"^.*\berror:.*$", log, re.M | re.I)
    target = meta["target_line"]
    at_target = rf"verified/lib\.rs\({target},\d+(?:-\d+(?:,\d+)?)?\): "
    executed = re.search(at_target + r"(?:note: )?Executing statement", log) is not None
    exact_error = len(errors) == 1 and re.search(at_target + r"error:", errors[0]) is not None
    stage_inputs_ok = (execution.get("source_unchanged_at_every_stage") is True and
                       all(stages.get(stage) == code for stage, code in
                           meta["expected_stages"].items() if stage != "verifast"))
    gate = (origin_gate(case, meta) if stages.get("decode") == 0
            and meta["kind"] != "layout_diagnostic" else
            {"admitted": False, "reason": "no origin correlation for layout diagnostic"
             if meta["kind"] == "layout_diagnostic" else "decode did not pass"})
    if not stage_inputs_ok:
        classification = "SETUP_REJECTION"
    elif stages.get("verifast") != 0 and (not (case / "proof-ast.ml").is_file() or
          "The name of a user-defined function must not start with 'vf__'" in log):
        classification = "FRONTEND_REJECTION"
    elif stages.get("verifast") != 0 and not executed:
        classification = "PRE_TARGET_REJECTION"
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
                   (meta["kind"] != "ordinary_contract_positive" or
                    ("Leak check." in log and "Executing return statement" in log)))
        classification = "PASS_CONTROL" if matched else "INCONCLUSIVE"
    else:
        matched = (stages.get("verifast") == 1 and gate.get("admitted") is True and
                   executed and exact_error and "Cannot prove" in errors[0])
        classification = "EXPECTED_REJECTION" if matched else "INCONCLUSIVE"
    result = {**execution, **meta, "case": name, "classification": classification,
              "semantic_evidence": classification in {"PASS_CONTROL", "EXPECTED_REJECTION"},
              "origin_gate": gate, "target_executed": executed, "errors": errors,
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
                                    if row["kind"] != "layout_diagnostic"),
                 "layout_diagnostic": rows["origin_unit_layout"]["classification"],
                 "evidence_class": manifest["evidence_class"]}
    (evidence / "origin-results.json").write_text(json.dumps(aggregate, indent=2) + "\n")
    return aggregate
