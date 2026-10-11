#!/usr/bin/env python3
"""Cloud-only staged one-cell guard and tracked-ManuallyDrop controls."""
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
        raise RuntimeError(f"missing pinned module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


md_classifier = load("md_control_classifier", HERE / "md_classifier.py")
concrete_consumer = load("concrete_u64_consumer", HERE.parents[3] / "cloud-build/origin-layout/concrete-consumer.py")
prep = load("onecell_prepare", HERE / "prepare.py")
base = load("onecell_stages", HERE.parents[1] / "copy-on-drop-prove.py")
ast = base.ast_helper
mir = base.mir_helper
PROFILE = ("experimental-merge-actual-glue-body-v8" if os.environ.get("SMALLSORT_MERGE_PROFILE") else "experimental-merge-qualified-guard-onecell-v1")
CASES = ("positive", "after_fbc_false", "after_recovery_false", "missing_held_owner",
         "double_physical_fbc")
CAMPAIGN = "incoming-origin-controls-only-v1"
CAMPAIGN_MD_SOURCE_SHA256 = "047d5f3245c0e81fe718899e11b611b1da9d7aa21b3c6e18347a5b95c923197e"
CAMPAIGN_BASELINE = {
    "build_id": "d1bfa119-b1d4-4667-8c2b-21d37b215aef",
    "proof_sha": "633c0c09cda0f4c40c6664722209f2a9d5792b4b",
    "profile_sha256": "11ccd16ec9df56e7165cf75b1800d48b367c3b65f20c9ea8656fc2b7779bed90",
    "results_sha256": "937e9050fb0d5b111c015785ba818b4dd3fa94cf756aaee73f65701d8cad36b2",
}
CAMPAIGN_RUN_CASES = ()  # Origin repair alone cannot resolve generic runtime extent.
MD_CASES = (
    "positive_manually_drop_after_merge",
    "negative_missing_precreated_reference",
    "negative_missing_reference_initialization",
    "negative_read_without_permission",
)


def source_gate(case: Path, metadata: dict) -> dict:
    original = (case / "original/lib.rs").read_bytes()
    verified = (case / "verified/lib.rs").read_bytes()
    exact = (prep.sha(original) == metadata["original_sha256"] and
             prep.sha(verified) == metadata["verified_sha256"] and
             original.count(prep.READ) == verified.count(prep.READ) == 1 and
             original.count(prep.GUARD) == verified.count(prep.GUARD) == 1 and
             original.count(prep.COPY) == verified.count(prep.COPY) == 1 and
             b"impl<T> Drop" not in original and b"impl<T> Drop" not in verified and
             verified.count(prep.OWN) == verified.count(prep.FBC_CLOSE) ==
             verified.count(prep.FBC_OPEN) == 1 and
             verified.count(prep.ANNOTATIONS) == 1 and
             verified.count(prep.RECOVER) == 1 and
             verified.count(prep.ALIGNMENT_LEMMA) == 1 and
             verified.count(prep.ALIGNMENT) == 1 and
             verified.count(prep.SOURCE_IDENTITY) == 1 and
             verified.count(prep.CONSTRUCTOR_GEOMETRY) == 1 and
             metadata.get("constructor_geometry_sha256") == prep.sha(prep.CONSTRUCTOR_GEOMETRY) and
             verified.count(prep.SOURCE_LIMITS) == 1 and
             all(verified.count(item) == 1 for item in prep.GEOMETRY) and
             verified.count(prep.DESTINATION_GEOMETRY) == 1 and
             metadata.get("destination_geometry_sha256") == prep.sha(prep.DESTINATION_GEOMETRY) and
             verified.count(b"*tail |-> held &*& <T>.own(t, held);") == 2 and
             b"on_unwind_ens thread_token(t)" in verified and
             b"on_unwind_ens false" not in verified and
             b"assume" not in verified and b"leak" not in verified and
             b"Freeze" not in verified and b"Copy" not in verified.replace(b"CopyOnDrop", b""))
    return {"admitted": exact, "read_line": metadata["read_line"],
            "guard_line": metadata["guard_line"],
            "copy_line": metadata["copy_line"],
            "exact_runtime_source_after_ghost_strip": metadata["runtime_ghost_strip_equal"]}


def mir_gate(case: Path, metadata: dict) -> dict:
    path = case / "decode.out"
    if not path.is_file():
        return {"admitted": False, "reason": "decoded MIR absent"}
    raw = path.read_text(errors="replace")
    variance = "variances = [invariant]"
    tree = mir.CapnpText(raw.replace(variance, 'variances = ["invariant"]')).parse()
    adts = []
    cursor = mir.path(tree, "adtDefs")
    while isinstance(cursor, dict) and "cons" in cursor:
        adts.append(mir.path(cursor, "cons", "h"))
        cursor = mir.path(cursor, "cons", "t")
    matches = [item for item in adts if mir.path(item, "id", "name") == "CopyOnDrop"]
    if len(matches) != 1:
        return {"admitted": False, "reason": "private CopyOnDrop ADT count differs",
                "copy_on_drop_adts": len(matches)}
    adt = matches[0]
    fields = mir.path(adt, "variants")[0]["fields"]
    bodies = [body for body in mir.path(tree, "bodies")
              if mir.path(body, "defPath") == "insertion_onecell"]
    if len(bodies) != 1:
        return {"admitted": False, "body_count": len(bodies)}
    blocks = mir.path(bodies[0], "basicBlocks")
    term_kinds = [mir.path(block, "terminator", "kind") for block in blocks]
    debug = mir.path(bodies[0], "varDebugInfo")
    guard_debug = [row for row in debug if mir.path(row, "name", "name") == "gap_guard"]
    guard_aggregates = []
    for block in blocks:
        for stmt in mir.path(block, "statements"):
            assignment = mir.assignment(stmt)
            if assignment is None:
                continue
            rhs = mir.path(assignment, "rhsRvalue")
            if not isinstance(rhs, dict) or "aggregate" not in rhs:
                continue
            aggregate = rhs["aggregate"]
            adt_kind = mir.path(aggregate, "aggregateKind", "adt")
            if not isinstance(adt_kind, dict) or \
                    mir.path(adt_kind, "adtId", "name") != "CopyOnDrop":
                continue
            source_line = mir.path(stmt, "sourceInfo", "span", "regular", "lo", "line")
            guard_aggregates.append({"source_line": source_line,
                                     "operand_count": len(mir.path(aggregate, "operands")),
                                     "field_names": [mir.path(f, "name") for f in
                                                     mir.path(adt_kind, "fields")]})
    shape = (mir.path(adt, "id", "name") == "CopyOnDrop" and
             mir.path(adt, "implementsDrop") is False and len(fields) == 3 and
             [mir.path(f, "name", "name") for f in fields] == ["src", "dst", "len"] and
             len(guard_debug) == 1 and len(guard_aggregates) == 1 and
             guard_aggregates[0]["source_line"] == metadata["guard_line"] and
             guard_aggregates[0]["operand_count"] == 3 and
             guard_aggregates[0]["field_names"] == ["src", "dst", "len"] and
             "ManuallyDrop" in raw and "copy_nonoverlapping" in raw and
             any(isinstance(kind, dict) and "return" in kind for kind in term_kinds))
    return {"admitted": shape, "body_count": len(bodies),
            "field_names": [mir.path(f, "name", "name") for f in fields],
            "implements_drop": mir.path(adt, "implementsDrop"),
            "guard_debug_count": len(guard_debug),
            "guard_aggregates": guard_aggregates,
            "basic_block_count": len(blocks),
            "terminators": term_kinds}


def ast_gate(case: Path, metadata: dict) -> dict:
    path = case / "proof-ast.ml"
    if not path.is_file():
        return {"admitted": False, "reason": "proof AST absent"}
    tree = ast.OcamlAstText(path.read_text(errors="replace")).parse()
    own = [node for node in ast.nodes(tree, "TypePredDef")
           if len(node.args) == 5 and node.args[1] == ["T"] and
           node.args[3] == "own" and "CopyOnDrop" in repr(node.args[2])]
    fbc = [node for node in ast.nodes(tree, "PredCtorDecl")
           if len(node.args) == 7 and node.args[1] == "CopyOnDrop_full_borrow_content"]
    bodies = [node for node in ast.nodes(tree, "Func")
              if len(node.args) == 13 and node.args[4] == "insertion_onecell" and
              node.args[10] != ast.Sym("None")]
    if len(own) != 1 or len(fbc) != 1 or len(bodies) != 1:
        return {"admitted": False, "own_count": len(own), "fbc_count": len(fbc),
                "body_count": len(bodies)}
    own_body = own[0].args[4]
    fbc_body = fbc[0].args[6]
    runtime = bodies[0].args[10]
    calls = [node.args[1] for node in ast.nodes(runtime, "CallExpr")
             if len(node.args) > 1 and isinstance(node.args[1], str)]
    close = [node for node in ast.nodes(runtime, "Close")
             if "CopyOnDrop_full_borrow_content" in repr(node)]
    opened = [node for node in ast.nodes(runtime, "Open")
              if "CopyOnDrop_full_borrow_content" in repr(node)]
    fields = [node for node in ast.nodes(fbc_body, "PointsTo")]
    fbc_calls = [node.args[1] for node in ast.nodes(fbc_body, "CallExpr")
                 if len(node.args) > 1 and isinstance(node.args[1], str)]
    own_points = ast.nodes(own_body, "PointsTo")
    own_recursive_calls = [node for node in ast.nodes(own_body, "TypePredExpr")
                           if len(node.args) >= 2 and node.args[-1] == "own"]
    own_recursive_lines = [ast.location_line(node.args[0]) for node in own_recursive_calls]
    fbc_field_lines = [ast.location_line(node.args[0]) for node in fields]
    read_loc = metadata["read_line"]
    guard_loc = metadata["guard_line"]
    def local_name(value):
        return (value.args[1] if isinstance(value, ast.Node) and value.name == "Var" and
                len(value.args) == 2 else None)

    # Rust's `tail.read()` is emitted as a typed load chain, not a CallExpr:
    # tail -> $_4, *$_4 -> $_3, then immutable `tmp: T = $_3`.
    read_assignments = [node.args for node in ast.nodes(runtime, "AssignExpr")
                        if len(node.args) == 4 and
                        ast.location_line(node.args[0]) == read_loc]
    read_linked = False
    immutable_tmp = False
    if len(read_assignments) == 3:
        first, load, init = read_assignments
        pvar = local_name(first[1])
        loaded = local_name(load[1])
        tmp_name = local_name(init[1])
        deref = load[3]
        deref_pointer = (local_name(deref.args[1]) if isinstance(deref, ast.Node) and
                         deref.name == "Deref" and len(deref.args) == 2 else None)
        read_linked = (
            first[2] == ast.Sym("Mutation") and local_name(first[3]) == "tail" and
            pvar is not None and
            load[2] == ast.Sym("Mutation") and loaded is not None and
            deref_pointer == pvar and
            init[2] == ast.Sym("Initialization") and tmp_name == "tmp" and
            local_name(init[3]) == loaded)
        tmp_decls = []
        for decl in ast.nodes(runtime, "DeclStmt"):
            if len(decl.args) != 2 or not isinstance(decl.args[1], list):
                continue
            for binding in decl.args[1]:
                if isinstance(binding, tuple) and len(binding) >= 3 and binding[2] == "tmp":
                    tmp_decls.append(binding)
        if len(tmp_decls) == 1:
            type_opt = tmp_decls[0][1]
            some = (type_opt.args[0] if isinstance(type_opt, ast.Node) and
                    type_opt.name == "Some" and len(type_opt.args) == 1 else None)
            const_args = (some.args if isinstance(some, ast.Node) and
                          some.name == "ConstTypeExpr" else [])
            inner = const_args[1] if len(const_args) == 2 else None
            immutable_tmp = (isinstance(inner, ast.Node) and inner.name == "IdentTypeExpr" and
                             len(inner.args) == 3 and inner.args[2] == "T")
        # The three linked locals must have exactly these single definitions.
        definition_counts = {"tmp": 0}
        if pvar is not None:
            definition_counts[pvar] = 0
        if loaded is not None:
            definition_counts[loaded] = 0
        for assignment in ast.nodes(runtime, "AssignExpr"):
            if len(assignment.args) == 4:
                name = local_name(assignment.args[1])
                if name in definition_counts:
                    definition_counts[name] += 1
        read_linked = (read_linked and immutable_tmp and
                       all(count == 1 for count in definition_counts.values()))
    guard_types = [node for node in ast.nodes(runtime, "StructTypeExpr")
                   if ast.location_line(node.args[0]) == guard_loc and
                   "CopyOnDrop" in repr(node)]
    admitted = (read_linked and len(guard_types) == 1 and
                len(fields) == 3 and "struct_CopyOnDrop_padding" in fbc_calls and
                "CopyOnDrop_own" in fbc_calls and len(own_points) >= 2 and
                len(close) >= 1 and len(opened) == 1 and
                len(ast.nodes(own_body, "False")) == 0 and
                not any(name in {"assume", "#assume", "leak"} for name in calls))
    return {"admitted": admitted, "own_count": len(own), "fbc_count": len(fbc),
            "body_count": len(bodies), "physical_fbc_field_count": len(fields),
            "fbc_calls": fbc_calls, "own_physical_points": len(own_points),
            "fbc_close_count": len(close), "fbc_open_count": len(opened),
            "read_runtime_count": len(read_assignments),
            "read_linked": read_linked, "immutable_typed_tmp": immutable_tmp,
            "own_recursive_lines": own_recursive_lines,
            "fbc_field_lines": fbc_field_lines,
            "exact_guard_type_count": len(guard_types), "runtime_calls": calls}


def execute_case(case: Path, args, env: dict) -> dict:
    source_before = base.hashes(case)
    exporter = base.run_stage(case, "exporter", [
        str(args.tool_home / "bin/vf-rust-mir-exporter"), "verified/lib.rs",
        f"--sysroot={args.compiler_sysroot}", "--edition", "2021", "--crate-type", "lib",
        ], env,
        timeout_seconds=args.stage_seconds, stdout_name="compiler-mir.bin")
    if exporter == 0:
        decode = base.run_stage(case, "decode", ["capnp", "decode", "-I",
            str(args.schema.parent), str(args.schema), "VfMir"], env,
            timeout_seconds=args.stage_seconds, stdin=case / "compiler-mir.bin")
    else:
        decode = 125
        base.not_run(case, "decode", "exporter failed")
    # Preserve both independently exported generated CFGs for inspection.
    # The official refiner still exports and compares the source pair itself.
    original_stages = {}
    if args.profile == "experimental-merge-actual-glue-body-v8":
        original_export = base.run_stage(case, "original-exporter", [
            str(args.tool_home / "bin/vf-rust-mir-exporter"), "original/lib.rs",
            f"--sysroot={args.compiler_sysroot}", "--edition", "2021", "--crate-type", "lib",
            ], env, timeout_seconds=args.stage_seconds,
            stdout_name="original-compiler-mir.bin")
        if original_export == 0:
            original_decode = base.run_stage(case, "original-decode", ["capnp", "decode", "-I",
                str(args.schema.parent), str(args.schema), "VfMir"], env,
                timeout_seconds=args.stage_seconds, stdin=case / "original-compiler-mir.bin")
        else:
            original_decode = 125
            base.not_run(case, "original-decode", "original exporter failed")
        original_stages = {"exporter": original_export, "decode": original_decode}
    vf_arguments = [str(args.tool_home / "bin/verifast"),
        "-rustc_args", "--edition 2021", "-verbose", "1", "-dump_ast_with_locs",
        "proof-ast.ml"]
    qualification_target = getattr(args, "qualification_target", None)
    if qualification_target is not None:
        if qualification_target != "ILP32":
            raise ValueError("Only the reviewed mismatched-model control is supported")
        vf_arguments.extend(["-target", qualification_target])
    extern_spec = case / "origin-control.rsspec"
    extern_spec_binding = None
    if extern_spec.is_file() and extern_spec.read_bytes():
        case_root = case.resolve()
        target_path = extern_spec.resolve()
        if target_path != case_root / "origin-control.rsspec":
            raise RuntimeError("extern spec target is outside the current case root")
        source_sha_before = base.file_sha(extern_spec)
        vf_arguments.extend(["-extern_spec", "=" + str(target_path)])
        extern_spec_binding = {
            "case_root": str(case_root),
            "target_path": str(target_path),
            "source_sha256_before": source_sha_before,
        }
    vf_arguments.append("verified/lib.rs")
    vf = base.run_stage(case, "verifast", vf_arguments, env, combine=True,
        timeout_seconds=args.verifier_seconds)
    if extern_spec_binding is not None:
        source_sha_after = base.file_sha(extern_spec)
        extern_spec_binding["source_sha256_after"] = source_sha_after
        receipt_path = case / "verifast-stage.json"
        receipt = json.loads(receipt_path.read_text())
        receipt["extern_spec_binding"] = extern_spec_binding
        receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    refinement = base.run_stage(case, "refinement", [
        str(args.tool_home / "bin/refinement-checker"), "--rustc-args", "--edition 2021",
        "original/lib.rs", "verified/lib.rs"], env,
        timeout_seconds=args.stage_seconds)
    source_after = base.hashes(case)
    unchanged = source_before == source_after and all(
        json.loads(path.read_text()).get("source_unchanged") is True
        for path in case.glob("*-stage.json")
        if json.loads(path.read_text()).get("status") != "NOT_RUN")
    return {"stages": {"exporter": exporter, "decode": decode,
                       "verifast": vf, "refinement": refinement},
            "original_export_stages": original_stages,
            **({"extern_spec_binding": extern_spec_binding} if extern_spec_binding is not None else {}),
            "source_before": source_before, "source_after": source_after,
            "source_unchanged_at_every_stage": unchanged}


def classify_onecell(name: str, case: Path, meta: dict, execution: dict) -> dict:
    stages = execution["stages"]
    try:
        mir_result = mir_gate(case, meta) if stages["decode"] == 0 else {"admitted": False}
    except Exception as error:
        mir_result = {"admitted": False, "reason": str(error)}
    try:
        ast_result = ast_gate(case, meta)
    except Exception as error:
        ast_result = {"admitted": False, "reason": str(error)}
    source_result = source_gate(case, meta)
    log = (case / "verifast.log").read_text(errors="replace")
    errors = re.findall(r"^.*\berror:.*$", log, re.M | re.I)
    dead = re.findall(r"^.*dead code.*$", log, re.M | re.I)
    headers = [(match.start(), match.group(1)) for match in re.finditer(
        r"^\s*\d+(?:\.\d+)?s: [^\s(]+\([0-9]+,[0-9]+"
        r"(?:-[0-9]+(?:,[0-9]+)?)?\): Verifying function '([^']+)'$", log, re.M)]
    segments = []
    for index, (start, function) in enumerate(headers):
        if function == "insertion_onecell" or function.startswith("insertion_onecell<"):
            end = headers[index + 1][0] if index + 1 < len(headers) else len(log)
            segments.append(log[start:end])
    body = len(segments) == 1
    segment = segments[0] if body else ""
    copy_executed = bool(re.search(
        rf"verified/lib\.rs\({meta['copy_line']},\d+(?:-\d+(?:,\d+)?)?\): "
        r"(?:note: )?Executing statement", segment))
    all_gates = (execution["source_unchanged_at_every_stage"] and
                 stages["exporter"] == stages["decode"] == stages["refinement"] == 0 and
                 source_result["admitted"] and mir_result["admitted"] and
                 ast_result["admitted"] and body and not dead)
    if name == "positive":
        matched = (all_gates and stages["verifast"] == 0 and copy_executed and
                   not errors and "Executing return statement" in segment and
                   "Leak check." in segment and "0 errors found" in log)
        classification = "PASS_FRAGMENT_ONLY" if matched else "INCONCLUSIVE"
    else:
        target = meta["target"]
        line_pattern = rf"verified/lib\.rs\({target['line']},\d+(?:-\d+)?\): error:"
        exact_line = len(errors) == 1 and re.search(line_pattern, errors[0]) is not None
        if name == "missing_held_owner" and len(errors) == 1:
            own_lines = ast_result.get("own_recursive_lines", [])
            exact_line = (len(own_lines) == 1 and
                          re.search(rf"verified/lib\.rs\({own_lines[0]},\d+(?:-\d+)?\): error:",
                                    errors[0]) is not None)
        if name == "double_physical_fbc" and len(errors) == 1:
            field_lines = ast_result.get("fbc_field_lines", [])
            exact_line = (len(field_lines) == 3 and
                          re.search(rf"verified/lib\.rs\({field_lines[0]},\d+(?:-\d+)?\): error:",
                                    errors[0]) is not None)
        if name in {"after_fbc_false", "after_recovery_false"}:
            intended = exact_line and "Cannot prove false" in errors[0]
        elif name == "missing_held_owner":
            intended = (exact_line and "No matching heap chunks" in errors[0] and
                        re.search(r"own\(T_typeid\)\(t, held\)", errors[0]) is not None)
        elif name == "double_physical_fbc":
            intended = (exact_line and "No matching heap chunks" in errors[0] and
                        "CopyOnDrop_src<T>" in errors[0])
        else:
            intended = (exact_line and "No matching heap chunks" in errors[0] and
                        re.search(r"CopyOnDrop|padding|points_to|field", errors[0], re.I) is not None)
        reached = (copy_executed if name == "after_recovery_false" else
                   f"verified/lib.rs({meta['fbc_open_line']}," in segment if name ==
                   "after_fbc_false" else
                   (re.search(rf"verified/lib\.rs\({target['line']},\d+(?:-\d+(?:,\d+)?)?\): "
                              r"(?:note: )?Executing statement", segment) is not None and
                    segment.find(f"verified/lib.rs({target['line']},") <
                    segment.find(errors[0])) if name == "double_physical_fbc" else
                   (re.search(rf"verified/lib\.rs\({meta['own_close_line']},\d+(?:-\d+(?:,\d+)?)?\): "
                              r"(?:note: )?Executing statement", segment) is not None and
                    segment.find(f"verified/lib.rs({meta['own_close_line']},") <
                    segment.find(errors[0])) if name == "missing_held_owner" else body)
        matched = (all_gates and stages["verifast"] == 1 and exact_line and
                   intended and reached and "Leak check." not in segment)
        classification = "EXPECTED_REJECTION" if matched else "INCONCLUSIVE"
    result = {**execution, "case": name, "source_admission": source_result,
              "mir_admission": mir_result, "ast_admission": ast_result,
              "body_seen": body, "copy_executed": copy_executed,
              "errors": errors, "dead_code": dead,
              "classification": classification, "accepted": False,
              "scope": "conditional quiescent one-cell fragment; actual Drop/glue OPEN"}
    (case / "classification.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def prepare_md_controls(evidence: Path) -> dict:
    source = (prep.ROOT / "research/challenge-8/verifast-tracked-manually-drop-regressions.rs").read_bytes()
    head = source.split(b"// CASE_BEGIN ", 1)[0]
    result = {}
    for name in MD_CASES:
        start = b"// CASE_BEGIN " + name.encode() + b"\n"
        end = b"// CASE_END " + name.encode()
        if source.count(start) != 1 or source.count(end) != 1:
            raise RuntimeError(f"tracked MD control {name} changed")
        body = source.split(start, 1)[1].split(end, 1)[0]
        original = head + body
        case = evidence / "md-controls" / name
        (case / "original").mkdir(parents=True)
        (case / "verified").mkdir()
        (case / "original/lib.rs").write_bytes(original)
        (case / "verified/lib.rs").write_bytes(original)
        target_line = prep.line(original, b"    let p = &*tmp as *const i32;\n") if \
            name != "negative_read_without_permission" else prep.line(
                original, b"    let result = *p;\n")
        result[name] = {"source_sha256": prep.sha(original), "target_line": target_line,
                        "read_line": prep.line(original, b"    let result = *p;\n"),
                        "spec_init_line": 88,
                        "service_control_only": name == "negative_read_without_permission"}
    return result


def classify_md(name: str, case: Path, meta: dict, execution: dict) -> dict:
    log = (case / "verifast.log").read_text(errors="replace")
    result = {**execution, **meta, **md_classifier.classify_log(name, log, meta, execution),
              "accepted": False}
    (case / "classification.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--profile-evidence", type=Path, required=True)
    parser.add_argument("--tool-home", type=Path, required=True)
    parser.add_argument("--compiler-sysroot", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--campaign", choices=(CAMPAIGN, "legacy-full-controls-v1", "bridge-minimal-v1", "len1-minimal-v1", "caller-composition-minimal-v1", "selected-drop-minimal-v1"),
                        default=CAMPAIGN)
    parser.add_argument("--stage-seconds", type=int, default=35)
    parser.add_argument("--verifier-seconds", type=int, default=50)
    args = parser.parse_args()
    if args.profile != PROFILE or not 1 <= args.stage_seconds <= 120 or \
            not 1 <= args.verifier_seconds <= 120:
        raise RuntimeError("one-cell profile or timeout outside allowlist")
    provider, proof_sha = base.require_hosted_cloud()
    if args.evidence.exists():
        raise FileExistsError("refusing to reuse one-cell evidence")
    if not args.tool_home.is_dir() or not args.profile_evidence.is_dir() or \
            not args.compiler_sysroot.is_dir() or not args.schema.is_file():
        raise RuntimeError("pinned hosted tool/evidence/sysroot/schema missing")
    profile_card = json.loads(Path(os.environ.get("SMALLSORT_MERGE_PROFILE", str(HERE / "PROFILE.json"))).read_text())
    profile_build = json.loads((args.profile_evidence / "profile-build.json").read_text())
    if profile_card.get("schema") != "smallsort-tracked-md-profile-v1" or \
            profile_card.get("profile") != PROFILE or \
            profile_build.get("profile") != PROFILE or \
            profile_build.get("build_exit") != 0 or \
            profile_build.get("proof_sha") != proof_sha or \
            profile_build.get("provider", {}).get("build_id") != provider["build_id"] or \
            profile_card.get("accepted") is not False:
        raise RuntimeError("tracked MD opt-in profile manifest differs")
    for key in ("patch_sha256", "translator_sha256", "emitter_sha256", "kernel_sha256",
                "ast_sha256", "sexpression_sha256", "verify_expr_sha256",
                "model_sha256", "unit_layout_patch_sha256", "parser_sha256", "prelude_sha256", "stdlib_sha256",
                "exporter_source_sha256", "schema_sha256", "guard_layout_patch_sha256", "refiner_main_source_sha256", "refiner_core_source_sha256", "z3_sha256"):
        if profile_build.get(key) != profile_card.get(key):
            raise RuntimeError(f"tracked MD profile pin differs: {key}")
    if profile_build.get("refiner_build_exit") != 0 or profile_build.get("refiner_built_from_source") is not True:
        raise RuntimeError("actual generated-glue profile requires official refiner source build receipt")
    if base.file_sha(HERE / "tracked-md.patch") != profile_card["patch_sha256"]:
        raise RuntimeError("tracked MD patch identity differs")
    if (base.file_sha(prep.ROOT / "research/challenge-8/verifast-tracked-manually-drop-regressions.rs")
            != CAMPAIGN_MD_SOURCE_SHA256):
        raise RuntimeError("geometry campaign tracked-MD baseline input identity differs")
    if profile_build.get("baseline_build_manifest_sha256") != base.file_sha(
            args.profile_evidence.parent / "build/console-cache-profile.txt"):
        raise RuntimeError("tracked MD build is not linked to this six-profile build")
    if (args.profile_evidence.parent / "build/source-build-exit-code.txt").read_text().strip() != "0":
        raise RuntimeError("six-profile source build did not complete")
    if base.file_sha(args.schema) != profile_card["schema_sha256"]:
        raise RuntimeError("qualified MIR schema differs from exact profile")
    source_pins = {
        "src/rust_frontend/vf_mir_exporter/src/lib.rs": "exporter_source_sha256",
        "src/rust_frontend/vf_mir/vf_mir.capnp": "schema_sha256",
        "src/rust_frontend/vf_mir_translator/vf_mir_translator.ml": "translator_sha256",
        "src/frontend/ocaml_expr_of_ast.ml": "emitter_sha256",
        "src/verifast.ml": "kernel_sha256",
        "src/verifast1.ml": "model_sha256",
        "src/frontend/ast.ml": "ast_sha256",
        "src/SExpressionEmitter.ml": "sexpression_sha256",
        "src/verify_expr.ml": "verify_expr_sha256",
        "src/rust_frontend/vf_mir_translator/rust_parser.ml": "parser_sha256",
        "bin/rust/prelude_core.rsspec": "prelude_sha256",
        "bin/rust/std/lib.rsspec": "stdlib_sha256",
        "bin/libz3.so": "z3_sha256",
        "src/refinement_checker/main.ml": "refiner_main_source_sha256",
        "src/refinement_checker/refinement_checker.ml": "refiner_core_source_sha256",
    }
    for relative, key in source_pins.items():
        if base.file_sha(args.tool_home / relative) != profile_card[key]:
            raise RuntimeError(f"tracked MD source pin differs: {relative}")
    rustc = shutil.which("rustc")
    if rustc is None:
        raise RuntimeError("hosted rustc missing")
    version = subprocess.run([rustc, "--version", "--verbose"], check=True,
                             text=True, capture_output=True).stdout
    if os.environ.get("RUSTUP_TOOLCHAIN") != "nightly-2026-09-25" or \
            "commit-hash: f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f" not in version or \
            platform.machine().lower() not in {"x86_64", "amd64"}:
        raise RuntimeError("hosted compiler pin differs")
    if Path(subprocess.check_output([rustc, "--print", "sysroot"], text=True).strip()).resolve() != \
            args.compiler_sysroot.resolve():
        raise RuntimeError("compiler sysroot pin differs")
    tool_hashes = {name: base.file_sha(args.tool_home / "bin" / name)
                   for name in ("vf-rust-mir-exporter", "verifast", "refinement-checker")}
    for binary, key in (("vf-rust-mir-exporter", "exporter_sha256"),
                        ("refinement-checker", "refiner_sha256")):
        if tool_hashes[binary] != profile_build[key]:
            raise RuntimeError(f"frozen {binary} differs from profile pin")
    if tool_hashes["verifast"] != profile_build.get("console_sha256"):
        raise RuntimeError("tracked MD console differs from built profile")
    args.evidence.mkdir(parents=True)
    extraction = prep.extract(args.evidence / "cases", args.evidence / "extraction.json")
    md_meta = prepare_md_controls(args.evidence)
    campaign_mode = args.campaign == CAMPAIGN
    env = dict(os.environ)
    env["LD_LIBRARY_PATH"] = ":".join(filter(None, [str(args.compiler_sysroot / "lib"),
        str(args.tool_home / "bin"), env.get("LD_LIBRARY_PATH", "")]))
    environment = {"profile": PROFILE, "proof_sha": proof_sha, "provider": provider,
                   "cloud_build_id": provider["build_id"], "tool_sha256": tool_hashes,
                   "profile_evidence": str(args.profile_evidence.resolve()),
                   "schema_sha256": base.file_sha(args.schema),
                   "source_sha256": base.file_sha(prep.SOURCE),
                   "rustc_version": version, "rustc_toolchain": os.environ["RUSTUP_TOOLCHAIN"], "accepted": False}
    (args.evidence / "environment.json").write_text(json.dumps(environment, indent=2) + "\n")
    # The retained lane smoke uses the six-patch binary. Run its same complete
    # ordinary normal/unwind gate on this exact combined candidate as well.
    smoke_root = args.evidence / "combined-profile-smoke"
    smoke_command = [sys.executable, str(HERE.parents[1] / "pointer-prove.py"),
        "--profile", PROFILE, "--scope", "exact combined-candidate ordinary normal/unwind smoke",
        "--tool-home", str(args.tool_home), "--compiler-sysroot", str(args.compiler_sysroot),
        "--schema", str(args.schema), "--fixture", str(HERE.parents[1] / "baseline-cases.rs"),
        "--cases", "ordinary_call_normal_unwind", "--evidence", str(smoke_root)]
    with (args.evidence / "combined-profile-smoke.log").open("w") as smoke_log:
        smoke_exit = subprocess.run(smoke_command, env=env, stdout=smoke_log,
            stderr=subprocess.STDOUT, timeout=300, check=False).returncode
    combined_smoke = json.loads((smoke_root / "aggregate.json").read_text())
    combined_smoke["exit_code"] = smoke_exit
    combined_smoke["profile"] = PROFILE
    combined_smoke["tool_sha256"] = tool_hashes
    combined_smoke["schema_sha256"] = environment["schema_sha256"]
    combined_smoke["rustc_version"] = version
    combined_smoke["rustc_toolchain"] = environment["rustc_toolchain"]
    combined_smoke["provider"] = provider
    combined_smoke["proof_sha"] = proof_sha
    combined_smoke["accepted"] = False
    (args.evidence / "combined-profile-smoke.json").write_text(
        json.dumps(combined_smoke, indent=2) + "\n")
    if (smoke_exit != 0 or combined_smoke.get("cases") !=
            {"ordinary_call_normal_unwind": "PASS"} or
            combined_smoke.get("classifier_controls_passed") is not True):
        raise RuntimeError("combined candidate mandatory smoke did not pass; retain artifacts")
    if args.campaign == "selected-drop-minimal-v1":
        control = load("selected_drop_helper_control", HERE.parents[3] / "cloud-build/origin-layout/onecell-caller-composition.py")
        helper = control.run(args.evidence / "helper-control", args, env, execute_case, environment)
        helper_matched = helper.get("cases") == {
            "positive": "BOUNDED_NORMAL_COMPOSITION_PASS_FRAGMENT_ONLY",
            "after_call_current_false": "EXPECTED_AFTER_CALL_CURRENT_REJECTION",
            "caller_entry_false": "EXPECTED_CALLER_ENTRY_REJECTION",
            "receiver_origin_probe": "EXPECTED_RECEIVER_ORIGIN_REJECTION"}
        selected = load("onecell_selected_drop", HERE.parents[3] / "cloud-build/origin-layout/onecell-selected-drop.py")
        summary = selected.run(args.evidence / "onecell-selected-drop", args, env, execute_case, environment)
        exact = set(summary.get("cases", {})) == set(selected.CASES) and len(selected.CASES) == 7
        matched = exact and helper_matched and summary.get("all_matched") is True and summary.get("accepted") is False
        aggregate = {"schema": "merge-minimal-selected-drop-v1", "profile": PROFILE,
            "campaign": "selected-drop-minimal-v1", "accepted": False,
            "all_matched": matched, "exact_case_sets": exact, "required_case_count": 7,
            "classification": "PASS_COMPONENT_DIAGNOSTIC" if matched else "INCONCLUSIVE",
            "environment": environment, "combined_profile_smoke": combined_smoke,
            "selected_drop": summary, "helper_control": helper, "helper_control_matched": helper_matched, "cases": summary.get("cases", {}),
            "panic_unwind": "NOT_RUN", "combined_profile_acceptance": False}
        # B2 is a separate actual-source diagnostic, entered only after every
        # fresh B1 gate in this same pinned campaign has qualified. No callee
        # summary, caller resource premise, or tool semantics changes here.
        b2_mode = HERE.parents[3] / "cloud-build/origin-layout/B2-ACTUAL-CAMPAIGN.json"
        if matched and b2_mode.is_file():
            mode = json.loads(b2_mode.read_text())
            if mode != {"schema": "merge-b2-actual-campaign-v1", "enabled": True,
                        "domain": "concrete-u64-guard-len1-three-cells"}:
                raise RuntimeError("B2 mode is not the exact pinned diagnostic")
            aggregate["b1_all_matched"] = True
            try:
                actual = load("actual_insert_tail_b2", HERE.parents[3] /
                              "cloud-build/origin-layout/actual-insert-tail-b2.py")
                aggregate["actual_insert_tail_b2"] = actual.run(
                    args.evidence / "actual-insert-tail-b2", args, env,
                    execute_case, environment)
                aggregate["classification"] = "INCONCLUSIVE_B2_CAUSAL_DIAGNOSTIC"
            except Exception as error:
                aggregate["actual_insert_tail_b2"] = {
                    "classification": "INCONCLUSIVE_B2_SETUP", "error": repr(error),
                    "accepted": False, "proof_credit": False}
                aggregate["classification"] = "INCONCLUSIVE_B2_SETUP"
            aggregate["panic_unwind"] = "NOT_PROVED"
            (args.evidence / "aggregate.json").write_text(json.dumps(aggregate, indent=2)+"\n")
            return 1  # A causal diagnostic never upgrades the full B2 target.
        (args.evidence / "aggregate.json").write_text(json.dumps(aggregate, indent=2)+"\n")
        return 0 if matched else 1

    if args.campaign == "caller-composition-minimal-v1":
        composition = load("onecell_caller_composition", HERE.parents[3] / "cloud-build/origin-layout/onecell-caller-composition.py")
        summary = composition.run(args.evidence / "onecell-caller-composition", args, env, execute_case, environment)
        expected = {"positive": "BOUNDED_NORMAL_COMPOSITION_PASS_FRAGMENT_ONLY",
                    "after_call_current_false": "EXPECTED_AFTER_CALL_CURRENT_REJECTION",
                    "caller_entry_false": "EXPECTED_CALLER_ENTRY_REJECTION"}
        cases = summary.get("cases", {})
        origin_outcomes = {"EXPECTED_RECEIVER_ORIGIN_REJECTION", "PROBE_ORIGIN_ESTABLISHED"}
        expected_names = set(expected) | {"receiver_origin_probe"}
        exact = (set(cases) == set(composition.CASES) == expected_names and
                 len(composition.CASES) == 4)
        matched = (exact and summary.get("qualified_fragment") is True and
                   summary.get("accepted") is False and
                   all(cases.get(name) == outcome for name, outcome in expected.items()) and
                   cases.get("receiver_origin_probe") in origin_outcomes)
        aggregate = {"schema": "merge-minimal-caller-composition-v1", "profile": PROFILE,
            "campaign": "caller-composition-minimal-v1", "accepted": False,
            "diagnostic_complete": matched, "all_matched": matched,
            "exact_case_sets": exact, "required_case_count": 4,
            "classification": "PASS_COMPONENT_DIAGNOSTIC" if matched else "INCONCLUSIVE",
            "environment": environment, "combined_profile_smoke": combined_smoke,
            "caller_composition": summary, "cases": summary.get("cases", {}),
            "actual_drop_glue": "NOT_IMPLEMENTED", "panic_unwind": "NOT_RUN",
            "combined_profile_acceptance": False}
        (args.evidence / "aggregate.json").write_text(json.dumps(aggregate, indent=2)+"\n")
        return 0 if matched else 1

    if args.campaign == "len1-minimal-v1":
        interface = load("onecell_drop_interface", HERE.parents[3] / "cloud-build/origin-layout/onecell-drop-interface.py")
        summary = interface.run(args.evidence / "onecell-drop-interface", args, env, execute_case, environment)
        exact = set(summary.get("cases", {})) == set(interface.CASES) and len(interface.CASES) == 12
        matched = (exact and summary.get("all_matched") is True and summary.get("accepted") is False and
                   summary.get("schema") == "source-linked-u64-onecell-drop-effect-v1" and
                   summary.get("cases") == interface.EXPECTED_CLASSIFICATIONS)
        aggregate = {"schema": "merge-minimal-len1-interface-v1", "profile": PROFILE,
            "campaign": "len1-minimal-v1", "accepted": False,
            "diagnostic_complete": matched, "all_matched": matched,
            "exact_case_sets": exact, "required_case_count": 12,
            "classification": "PASS_COMPONENT_DIAGNOSTIC" if matched else "INCONCLUSIVE",
            "environment": environment, "combined_profile_smoke": combined_smoke,
            "onecell_drop_interface": summary, "cases": summary.get("cases", {}),
            "actual_caller": "NOT_RUN", "actual_drop_glue": "NOT_IMPLEMENTED",
            "panic_unwind": "NOT_RUN", "combined_profile_acceptance": False}
        (args.evidence / "aggregate.json").write_text(json.dumps(aggregate, indent=2)+"\n")
        return 0 if matched else 1

    span_controls = load("allocation_span_controls", HERE.parents[3] / "cloud-build/incoming-span-lifetime/controls/run.py")
    if args.campaign == "bridge-minimal-v1":
        guard_storage_controls = load("guard_storage_controls", HERE.parents[3] / "cloud-build/origin-layout/guard-storage-controls.py")
        # Retain the full checked profile/provider/source admission above and
        # exact combined smoke; omit unrelated historical campaigns.
        span_summary = span_controls.run(args.evidence, args, env, execute_case)
        concrete_summary = concrete_consumer.run(args.evidence / "concrete-u64", args, env,
                                                 execute_case, environment)
        guard_summary = guard_storage_controls.run(args.evidence, args, env, execute_case,
                                                    args.evidence / "concrete-u64")
        concrete_cases = concrete_summary.get("cases", {})
        concrete_matched = (concrete_cases == {
            "positive": "PASS_FRAGMENT_ONLY", "after_fbc_false": "EXPECTED_REJECTION",
            "after_recovery_false": "EXPECTED_REJECTION",
            "missing_held_owner": "NOT_APPLICABLE_CONCRETE_EMPTY_OWN",
            "double_physical_fbc": "EXPECTED_REJECTION"})
        span_names = {"span_positive", "span_retired_local_reuse", "span_overlap",
                      "span_raw_arbitrary", "span_lost_incoming_authority", "span_zero_extent"}
        guard_names = {"qualified_live_guard", "guard_source_overlap_false", "guard_zero_extent_false",
                       "full_mutable_canonical_fbc_entry_false", "wrong_constness_unqualified",
                       "renamed_guard_unqualified", "generic_guard_unqualified", "zst_guard_unqualified",
                       "mismatched_verifier_pointer_model", "qualified_layout_without_storage_resources"}
        exact_case_sets = (set(span_summary.get("controls",{})) == span_names and
                           set(guard_summary.get("cases",{})) == guard_names)
        all_matched = (exact_case_sets and span_summary.get("all_matched") is True and
                       concrete_matched and guard_summary.get("all_matched") is True)
        aggregate = {"schema": "merge-minimal-guard-bridge-v1", "profile": PROFILE,
            "campaign": "bridge-minimal-v1", "accepted": False,
            "diagnostic_complete": all_matched, "all_matched": all_matched,
            "exact_case_sets": exact_case_sets, "required_case_count": 21,
            "classification": "PASS_COMPONENT_DIAGNOSTIC" if all_matched else "INCONCLUSIVE",
            "environment": environment, "combined_profile_smoke": combined_smoke,
            "allocation_span_controls": span_summary,
            "concrete_u64_consumer": concrete_summary, "guard_storage_controls": guard_summary,
            "cases": {**{"span/"+k:v for k,v in span_summary.get("controls",{}).items()},
                      **{"concrete/"+k:v for k,v in concrete_cases.items()},
                      **{"guard/"+k:v["classification"] for k,v in guard_summary.get("cases",{}).items()}},
            "len1_interface": "NOT_RUN", "actual_caller": "NOT_RUN",
            "actual_drop_glue": "NOT_IMPLEMENTED", "panic_unwind": "NOT_RUN",
            "combined_profile_acceptance": False}
        (args.evidence / "aggregate.json").write_text(json.dumps(aggregate, indent=2)+"\n")
        return 0 if all_matched else 1

    # Legacy Drop modules are not dependencies of the bounded bridge campaign.
    concrete_drop_body = load("concrete_drop_body", HERE.parents[3] / "cloud-build/origin-layout/concrete-drop-body.py")
    onecell_drop_interface = load("onecell_drop_interface", HERE.parents[3] / "cloud-build/origin-layout/onecell-drop-interface.py")

    layout_controls = load("unit_layout_controls", HERE.parents[3] / "cloud-build/origin-layout/layout-controls.py")
    origin_controls = load("incoming_origin_controls", HERE.parents[3] / "cloud-build/incoming-origin/controls/run.py")

    guard_storage_controls = load("guard_storage_controls", HERE.parents[3] / "cloud-build/origin-layout/guard-storage-controls.py")

    # Execute isolated address-span controls before any actual one-cell cases.
    mechanism_summary = span_controls.run(args.evidence, args, env, execute_case)
    origin_summary = origin_controls.run(args.evidence, args, env, execute_case)
    layout_summary = layout_controls.run(args.evidence, args, env, execute_case)
    concrete_summary = concrete_consumer.run(args.evidence / "concrete-u64", args, env, execute_case, environment)
    if concrete_summary.get("cases", {}).get("positive") == "PASS_FRAGMENT_ONLY":
        drop_body_summary = concrete_drop_body.run(
            args.evidence / "concrete-drop-body", args, env, execute_case, environment)
    else:
        drop_body_summary = {"classification": "NOT_RUN", "accepted": False,
            "reason": "concrete-u64 recovery positive has not passed",
            "actual_callee_or_glue_credit": False}
    guard_storage_summary = guard_storage_controls.run(args.evidence, args, env, execute_case, args.evidence / "concrete-u64")
    onecell_interface_summary = onecell_drop_interface.run(args.evidence / "onecell-drop-interface", args, env, execute_case, environment)
    results = {}
    md_pass = False
    if campaign_mode:
        for name in MD_CASES:
            case = args.evidence / "md-controls" / name
            before = base.hashes(case)
            for stage in ("exporter", "decode", "verifast", "refinement"):
                base.not_run(case, stage, "allocation-span campaign; MD controls NOT_RUN on new profile")
            results[name] = {"case": name, **md_meta[name], "classification": "NOT_RUN",
                "accepted": False, "reason": "allocation-span campaign; MD controls NOT_RUN on new profile",
                "stages": {stage: 125 for stage in ("exporter", "decode", "verifast", "refinement")},
                "source_before": before, "source_after": before,
                "source_unchanged_at_every_stage": True}
            (case / "classification.json").write_text(json.dumps(results[name], indent=2) + "\n")
    else:
        for name in MD_CASES:
            case = args.evidence / "md-controls" / name
            results[name] = classify_md(name, case, md_meta[name], execute_case(case, args, env))
            (args.evidence / "results.json").write_text(json.dumps(results, indent=2) + "\n")
        md_pass = all(results[name]["classification"] == "REGRESSION_MATCHED" for name in MD_CASES)
    for name in CASES:
        case = args.evidence / "cases" / name
        if campaign_mode:
            if name in CAMPAIGN_RUN_CASES and mechanism_summary.get("all_matched") is True:
                results[name] = classify_onecell(name, case, extraction["cases"][name],
                                                 execute_case(case, args, env))
            else:
                before = base.hashes(case)
                reason = ("incoming mechanism controls did not pass" if name in CAMPAIGN_RUN_CASES else "runtime extent bridge absent; origin-only change cannot cure separation")
                for stage in ("exporter", "decode", "verifast", "refinement"):
                    base.not_run(case, stage, reason)
                results[name] = {"case": name, "classification": "NOT_RUN", "accepted": False,
                    "reason": reason, "stages": {stage: 125 for stage in
                        ("exporter", "decode", "verifast", "refinement")},
                    "source_before": before, "source_after": before,
                    "source_unchanged_at_every_stage": True}
                (case / "classification.json").write_text(json.dumps(results[name], indent=2) + "\n")
        elif md_pass:
            results[name] = classify_onecell(name, case, extraction["cases"][name],
                                             execute_case(case, args, env))
        else:
            for stage in ("exporter", "decode", "verifast", "refinement"):
                base.not_run(case, stage, "isolated MD gates did not pass")
            before = base.hashes(case)
            results[name] = {"case": name, "classification": "NOT_RUN", "accepted": False,
                "reason": "isolated MD gates did not pass", "stages": {stage: 125 for stage in
                    ("exporter", "decode", "verifast", "refinement")},
                "source_before": before, "source_after": before,
                "source_unchanged_at_every_stage": True}
            (case / "classification.json").write_text(json.dumps(results[name], indent=2) + "\n")
        (args.evidence / "results.json").write_text(json.dumps(results, indent=2) + "\n")
    dependency_basis = ({"classification": "NOT_RUN_ON_NEW_PROFILE",
        "source_sha256": CAMPAIGN_MD_SOURCE_SHA256,
        "historical_build_id": CAMPAIGN_BASELINE["build_id"],
        "historical_profile_sha256": CAMPAIGN_BASELINE["profile_sha256"],
        "historical_results_sha256": CAMPAIGN_BASELINE["results_sha256"],
        "proof_sha": proof_sha}
        if campaign_mode else None)
    span_summary = json.loads((args.evidence / "span-results.json").read_text())
    controls_match = span_summary.get("all_matched") is True
    fragment_pass = (controls_match and ((campaign_mode and
        results["positive"]["classification"] == "PASS_FRAGMENT_ONLY" and
        results["after_recovery_false"]["classification"] == "EXPECTED_REJECTION") or
        (not campaign_mode and md_pass and
         results["positive"]["classification"] == "PASS_FRAGMENT_ONLY" and
         all(results[name]["classification"] == "EXPECTED_REJECTION"
             for name in CASES if name != "positive"))))
    aggregate = {"profile": PROFILE, "accepted": False,
                 "campaign": CAMPAIGN if campaign_mode else "legacy-full-controls-v1",
                 "md_regressions_matched": False if campaign_mode else md_pass,
                 "md_dependency_basis": dependency_basis,
                 "allocation_span_controls_match": controls_match,
                 "fragment_pass": fragment_pass,
                 "actual_drop_glue": "OPEN",
                 "allocation_span_controls": json.loads((args.evidence / "span-results.json").read_text()),
                 "origin_controls": origin_summary,
                 "layout_controls": layout_summary,
                 "concrete_u64_consumer": concrete_summary,
                 "concrete_drop_body_diagnostic": drop_body_summary,
                 "guard_storage_controls": guard_storage_summary,
                 "onecell_drop_interface": onecell_interface_summary,
                 "combined_profile_smoke": combined_smoke,
                 "cases": {
                     name: row["classification"] for name, row in results.items()}}
    (args.evidence / "aggregate.json").write_text(json.dumps(aggregate, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"hosted one-cell proof refused: {error}", file=sys.stderr)
        raise SystemExit(2)
