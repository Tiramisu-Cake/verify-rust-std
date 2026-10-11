#!/usr/bin/env python3
"""Cloud-only concrete-u64 specialization of the source-linked one-cell witness.

This helper reuses the established one-cell source extractor only from its
Cloud entrypoint.  It preserves that adapter's literal-one recovery witness;
it does not execute ``CopyOnDrop::drop`` or claim actual drop-glue coverage.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OLD = ROOT / "research/challenge-8/merge/overnight/guard-ownership/insertion-onecell"
SOURCE = ROOT / "library/core/src/slice/sort/shared/smallsort.rs"
def _profile_identity() -> str:
    selected = os.environ.get("SMALLSORT_MERGE_PROFILE")
    if not selected:
        return "experimental-merge-qualified-guard-onecell-v1"
    profile = json.loads(Path(selected).read_text()).get("profile")
    if profile not in ("experimental-merge-actual-glue-observation-v2",
                       "experimental-merge-actual-glue-observation-v3",
                            "experimental-merge-actual-glue-body-v8",
                       "experimental-merge-selected-drop-receiver-v4"):
        raise RuntimeError("unsupported concrete-u64 experimental profile identity")
    return profile


PROFILE = _profile_identity()
CASES = ("positive", "after_fbc_false", "after_recovery_false",
         "missing_held_owner", "double_physical_fbc")
POST_FBC_LADDER = (
    b"        //@ assert gap_guard.src == held_ref; // LADDER: FBC pointer identity\n"
    b"        //@ assert gap_guard.dst == tail; // LADDER: FBC destination identity\n"
    b"        //@ assert gap_guard.len == 1; // LADDER: FBC literal-one length\n"
    b"        //@ let fbc_src = gap_guard.src;\n"
    b"        //@ assert [1/4](*fbc_src |-> ?fbc_current); // LADDER: source quarter\n"
    b"        //@ assert [1/4](*held_ref |-> fbc_current); // LADDER: held reference quarter\n"
)
FBC_FIELD_FRAME = (
    b"        //@ merge_fractions gap_guard.src |-> _;\n"
    b"        //@ merge_fractions gap_guard.dst |-> _;\n"
    b"        //@ merge_fractions gap_guard.len |-> _;\n"
    b"        //@ open [1/2]<CopyOnDrop>.own(t, gap_guard);\n"
    b"        //@ open [1/2]<CopyOnDrop>.own(t, gap_guard);\n"
    b"        //@ merge_fractions points_to::<u64>(gap_guard.src as *mut u64, _);\n"
    b"        //@ merge_fractions points_to_::<u64>(gap_guard.dst, _);\n"
    b"        //@ merge_fractions type_interp::<u64>();\n"
)
POST_COPY_LADDER = (
    b"        //@ assert recovery_src == held_ref; // LADDER: copy pointer identity\n"
    b"        //@ assert [1/4](*held_ref |-> copied); // LADDER: conserved reference quarter\n"
)


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"required pinned module unavailable: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _file_sha(path: Path) -> str:
    return _sha(path.read_bytes())


def _blob(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def _line(data: bytes, needle: bytes) -> int:
    if data.count(needle) != 1:
        raise ValueError(f"expected a unique source-linked statement: {needle!r}")
    return data[:data.index(needle)].count(b"\n") + 1


def _rewrite_types(raw: bytes) -> bytes:
    """Instantiate type spellings without touching runtime logic."""
    replacements = (
        (b"CopyOnDrop_full_borrow_content::<T>",
         b"CopyOnDrop_full_borrow_content"),
        (b"CopyOnDrop<T>", b"CopyOnDrop"),
        (b"pred<T> <CopyOnDrop>", b"pred <CopyOnDrop>"),
        (b"unsafe fn insertion_onecell<T>", b"unsafe fn insertion_onecell"),
        (b"lem initialized_storage_alignment<T>",
         b"lem initialized_storage_alignment"),
        (b"lem uninitialized_storage_alignment<T>",
         b"lem uninitialized_storage_alignment"),
        (b"initialized_storage_alignment::<T>(", b"initialized_storage_alignment("),
        (b"uninitialized_storage_alignment::<T>(", b"uninitialized_storage_alignment("),
        (b"<T>.own", b"<u64>.own"),
        (b"::<T>", b"::<u64>"),
    )
    result = raw
    for before, after in replacements:
        result = result.replace(before, after)
    # Remaining stand-alone T tokens are the pointer/size/alignment parameters
    # of the now-concrete function, predicates and helper lemmas.
    result = re.sub(rb"\bT\b", b"u64", result)
    # A full canonical FBC hides existential field witnesses. Retain half of
    # the precise fields as a frame, conserving all original permissions.
    # The separately labelled duplicate-full-FBC negative is kept full.
    for verb in (b"close", b"open"):
        token = verb + b" CopyOnDrop_full_borrow_content(t, &gap_guard)();\n"
        result = result.replace(token, verb + b" [1/2]CopyOnDrop_full_borrow_content(t, &gap_guard)();\n")
    # This source-linked scalar protocol borrows half of an existing const
    # half-share. Preserve its exact quarter when packing the nonprecise own.
    # Folding still consumes that physical share; no resource is introduced.
    result = result.replace(b"[?f](*v.src |-> ?current)",
                            b"[1/4](*v.src |-> ?current)")
    if re.search(rb"\bT\b|CopyOnDrop<T>|insertion_onecell<T>", result):
        raise ValueError("concrete specialization retained an uninstantiated T")
    return result


def _specialize(raw: bytes, prep) -> bytes:
    result = _rewrite_types(raw)
    if result.count(prep.READ) != 1 or result.count(prep.GUARD) != 1 or \
            result.count(prep.COPY) != 1:
        raise ValueError("specialization changed or duplicated a runtime anchor")
    return result


def _adapt_concrete_recovery(verified: bytes, prep) -> bytes:
    """Use stable ghost pointer locals in only the concrete specialized file."""
    geometry = _rewrite_types(prep.DESTINATION_GEOMETRY)
    recovery = _rewrite_types(prep.RECOVER)
    bindings = (b"        //@ let recovery_src = gap_guard.src;\n"
                b"        //@ let recovery_dst = gap_guard.dst;\n")
    adapted_recovery = recovery.replace(b"gap_guard.src", b"recovery_src").replace(
        b"gap_guard.dst", b"recovery_dst")
    if verified.count(geometry) != 1 or verified.count(recovery) != 1:
        raise ValueError("concrete recovery adaptation anchors are not unique")
    verified = verified.replace(geometry, geometry + bindings, 1)
    opened = _rewrite_types(prep.FBC_OPEN + prep.OWN_OPEN)
    if verified.count(opened) != 1:
        raise ValueError("FBC entailment ladder anchor is not unique")
    verified = verified.replace(opened, _rewrite_types(prep.FBC_OPEN) +
                                FBC_FIELD_FRAME + POST_FBC_LADDER, 1)
    end_ref = b"        //@ end_ref_readonly(held_ref);\n"
    adapted_recovery = adapted_recovery.replace(end_ref, POST_COPY_LADDER + end_ref, 1)
    return verified.replace(recovery, adapted_recovery, 1)


def _source_gate(case: Path, metadata: dict, prep) -> dict:
    original = (case / "original/lib.rs").read_bytes()
    verified = (case / "verified/lib.rs").read_bytes()
    stripped = verified
    for ghost in metadata["ghost_fragments"]:
        token = ghost.encode("ascii")
        if stripped.count(token) != 1:
            return {"admitted": False, "reason": "ghost strip anchor is not unique"}
        stripped = stripped.replace(token, b"", 1)
    anchors = (prep.READ, prep.GUARD, prep.COPY)
    exact_anchors = all(original.count(anchor) == verified.count(anchor) == 1
                        for anchor in anchors)
    # CopyOnDrop itself is the only intended occurrence of "Copy" in the
    # generated runtime/type names; test the source text after removing it.
    no_escape_hatches = (not any(word in verified for word in
                                 (b"assume", b"leak", b"Freeze")) and
                         b"Copy" not in verified.replace(b"CopyOnDrop", b""))
    admitted = (exact_anchors and stripped == original and
                _sha(original) == metadata["original_sha256"] and
                _sha(verified) == metadata["verified_sha256"] and
                not re.search(rb"\bT\b", verified) and no_escape_hatches and
                b"on_unwind_ens false" not in verified and
                b"thread_token(t)" in verified and
                b"*tail |-> held &*& <u64>.own(t, held);" in verified and
                b"*tail |-> ?unwound &*& <u64>.own(t, unwound);" in verified and
                ((metadata["case"] == "missing_held_owner" and
                  b"*tail |-> ?held &*& <u64>.own(t, held);" not in verified) or
                 (metadata["case"] != "missing_held_owner" and
                  b"*tail |-> ?held &*& <u64>.own(t, held);" in verified)))
    return {"admitted": admitted,
            "runtime_exact_after_ghost_strip": stripped == original,
            "runtime_anchor_counts": {anchor.decode(): original.count(anchor)
                                       for anchor in anchors},
            "concrete_u64": not bool(re.search(rb"\bT\b", verified)),
            "full_normal_unwind_posts_present":
                b"thread_token(t)" in verified and
                b"*tail |-> held &*& <u64>.own(t, held);" in verified and
                b"on_unwind_ens thread_token(t)" in verified and
                b"*tail |-> ?unwound &*& <u64>.own(t, unwound);" in verified,
            "no_false_unwind_post": b"on_unwind_ens false" not in verified}


def _validate_receipt(args, receipt: dict, provider: dict, proof_sha: str) -> dict:
    """Bind classification to the parent's already-validated Cloud profile receipt."""
    if not isinstance(receipt, dict):
        raise TypeError("validated_receipt must be a dictionary")
    if getattr(args, "profile", None) != PROFILE or receipt.get("profile") != PROFILE:
        raise RuntimeError("concrete-u64 consumer profile identity differs")
    if receipt.get("accepted") is not False:
        raise RuntimeError("experimental profile receipt must remain unaccepted")
    receipt_provider = receipt.get("provider")
    if not isinstance(receipt_provider, dict) or \
            receipt_provider.get("build_id") != provider.get("build_id"):
        raise RuntimeError("Cloud provider/build identity differs from validated receipt")
    if receipt.get("proof_sha") != proof_sha:
        raise RuntimeError("Cloud proof SHA differs from validated receipt")

    tool_home = Path(args.tool_home)
    tool_files = {
        "vf-rust-mir-exporter": tool_home / "bin/vf-rust-mir-exporter",
        "verifast": tool_home / "bin/verifast",
        "refinement-checker": tool_home / "bin/refinement-checker",
    }
    receipt_tools = receipt.get("tool_sha256")
    if not isinstance(receipt_tools, dict):
        raise RuntimeError("validated receipt has no tool_sha256 map")
    actual_tools = {}
    for name, path in tool_files.items():
        if not path.is_file():
            raise RuntimeError(f"pinned tool binary missing: {path}")
        actual_tools[name] = _file_sha(path)
        if receipt_tools.get(name) != actual_tools[name]:
            raise RuntimeError(f"actual {name} hash differs from validated receipt")

    profile_evidence_value = receipt.get("profile_evidence")
    if not isinstance(profile_evidence_value, (str, Path)):
        raise RuntimeError("validated receipt has no profile_evidence path")
    profile_evidence = Path(profile_evidence_value).resolve()
    profile_build_path = profile_evidence / "profile-build.json"
    if not profile_build_path.is_file():
        raise RuntimeError("pinned profile-build.json is absent")
    profile_build = json.loads(profile_build_path.read_text())
    if (profile_build.get("profile") != PROFILE or profile_build.get("build_exit") != 0 or
            profile_build.get("proof_sha") != proof_sha or
            profile_build.get("provider", {}).get("build_id") != provider.get("build_id")):
        raise RuntimeError("profile-build receipt identity or completion differs")
    profile_tool_hashes = {
        "vf-rust-mir-exporter": profile_build.get("exporter_sha256"),
        "verifast": profile_build.get("console_sha256"),
        "refinement-checker": profile_build.get("refiner_sha256"),
    }
    if profile_tool_hashes != actual_tools:
        raise RuntimeError("tool binaries differ from the pinned profile-build receipt")
    if profile_build.get("accepted") is True:
        raise RuntimeError("experimental profile-build receipt unexpectedly claims acceptance")

    schema = Path(args.schema)
    if not schema.is_file():
        raise RuntimeError("pinned MIR schema is absent")
    schema_sha = _file_sha(schema)
    if receipt.get("schema_sha256") != schema_sha:
        raise RuntimeError("MIR schema hash differs from validated receipt")
    if profile_build.get("schema_sha256") not in (None, schema_sha):
        raise RuntimeError("profile-build MIR schema hash differs")

    compiler_version = receipt.get("rustc_version", receipt.get("compiler_version"))
    if not isinstance(compiler_version, str) or \
            "f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f" not in compiler_version or \
            "2026-09-24" not in compiler_version:
        raise RuntimeError("compiler version receipt differs from frozen nightly pin")
    toolchain = receipt.get("rustc_toolchain")
    if toolchain != "nightly-2026-09-25":
        raise RuntimeError("compiler toolchain receipt differs from frozen nightly pin")
    for key in ("rustc_version", "compiler_version"):
        pinned_version = profile_build.get(key)
        if pinned_version is not None and pinned_version != compiler_version:
            raise RuntimeError(f"profile-build compiler identity differs: {key}")

    # Require a JSON-roundtrippable receipt before hashing/recording the exact
    # parent input. This is metadata validation only; no toolchain is invoked.
    receipt_bytes = json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode()
    return {"receipt": receipt, "receipt_sha256": _sha(receipt_bytes),
            "profile_evidence": str(profile_evidence),
            "profile_build_sha256": _file_sha(profile_build_path),
            "actual_tool_sha256": actual_tools, "schema_sha256": schema_sha,
            "rustc_version": compiler_version,
            "rustc_toolchain": toolchain}


def _stage_receipts(case: Path, stages: dict, baseline: dict) -> dict:
    expected = ("exporter", "decode", "verifast", "refinement")
    rows = {}
    valid = True
    current = _hashes(case)
    for name in expected:
        path = case / f"{name}-stage.json"
        if not path.is_file():
            rows[name] = {"present": False, "admitted": False,
                          "reason": "required stage receipt missing"}
            valid = False
            continue
        try:
            data = json.loads(path.read_text())
        except Exception as error:
            rows[name] = {"present": True, "admitted": False,
                          "reason": f"invalid stage receipt: {error}"}
            valid = False
            continue
        code = stages.get(name)
        source_before = data.get("source_before", {})
        source_after = data.get("source_after", {})
        status = data.get("status")
        status_ok = status is None or status in {"SUCCESS", "SUCCEEDED", "COMPLETED"}
        stage_valid = (data.get("stage") == name and status_ok and
                       isinstance(code, int) and data.get("exit_code") == code and
                       data.get("source_unchanged") is True and
                       source_before == source_after and
                       source_before.get("original/lib.rs") == baseline.get("original/lib.rs") and
                       source_after.get("original/lib.rs") == baseline.get("original/lib.rs") and
                       source_before.get("verified/lib.rs") == baseline.get("verified/lib.rs") and
                       source_after.get("verified/lib.rs") == baseline.get("verified/lib.rs") and
                       source_before.get("small_sort_source") == _file_sha(SOURCE) and
                       source_after.get("small_sort_source") == _file_sha(SOURCE) and
                       current.get("original/lib.rs") == baseline.get("original/lib.rs") and
                       current.get("verified/lib.rs") == baseline.get("verified/lib.rs"))
        rows[name] = {"present": True, "admitted": stage_valid,
                      "exit_code": data.get("exit_code"), "callback_exit_code": code,
                      "source_unchanged": data.get("source_unchanged"),
                      "status": data.get("status")}
        valid = valid and stage_valid
    return {"admitted": valid, "stages": rows}


def _mir_gate(case: Path, metadata: dict, mir) -> dict:
    path = case / "decode.out"
    if not path.is_file():
        return {"admitted": False, "reason": "decoded MIR absent"}
    raw = path.read_text(errors="replace")
    try:
        parsed = mir.CapnpText(raw.replace("variances = [invariant]",
                                           'variances = ["invariant"]')).parse()
        adts = []
        cursor = mir.path(parsed, "adtDefs")
        while isinstance(cursor, dict) and "cons" in cursor:
            adts.append(mir.path(cursor, "cons", "h"))
            cursor = mir.path(cursor, "cons", "t")
        guards = [adt for adt in adts if mir.path(adt, "id", "name") == "CopyOnDrop"]
        bodies = [body for body in mir.path(parsed, "bodies")
                  if mir.path(body, "defPath") == "insertion_onecell"]
        if len(guards) != 1 or len(bodies) != 1:
            return {"admitted": False, "guard_count": len(guards),
                    "body_count": len(bodies)}
        fields = mir.path(guards[0], "variants")[0]["fields"]
        blocks = mir.path(bodies[0], "basicBlocks")
        debug = mir.path(bodies[0], "varDebugInfo")
        guard_debug = [row for row in debug
                       if mir.path(row, "name", "name") == "gap_guard"]
        aggregates = []
        terminators = []
        for block in blocks:
            terminators.append(mir.path(block, "terminator", "kind"))
            for statement in mir.path(block, "statements"):
                assignment = mir.assignment(statement)
                if assignment is None:
                    continue
                rhs = mir.path(assignment, "rhsRvalue")
                if not isinstance(rhs, dict) or "aggregate" not in rhs:
                    continue
                adt = mir.path(rhs["aggregate"], "aggregateKind", "adt")
                if isinstance(adt, dict) and mir.path(adt, "adtId", "name") == "CopyOnDrop":
                    aggregates.append({
                        "line": mir.path(statement, "sourceInfo", "span", "regular",
                                         "lo", "line"),
                        "operands": len(mir.path(rhs["aggregate"], "operands")),
                        "fields": [mir.path(field, "name") for field in
                                   mir.path(adt, "fields")],
                    })
        names = [mir.path(field, "name", "name") for field in fields]
        admitted = (names == ["src", "dst", "len"] and
                    mir.path(guards[0], "implementsDrop") is False and
                    len(guard_debug) == len(aggregates) == 1 and
                    aggregates[0]["line"] == metadata["guard_line"] and
                    aggregates[0]["operands"] == 3 and
                    aggregates[0]["fields"] == names and
                    any(isinstance(kind, dict) and "return" in kind
                        for kind in terminators) and "u64" in raw)
        return {"admitted": admitted, "field_names": names,
                "implements_drop": mir.path(guards[0], "implementsDrop"),
                "guard_local_count": len(guard_debug), "guard_aggregates": aggregates,
                "contains_u64": "u64" in raw,
                "return_terminator_present": any(
                    isinstance(kind, dict) and "return" in kind for kind in terminators)}
    except Exception as error:
        return {"admitted": False, "reason": f"MIR admission failed closed: {error}"}


def _ast_gate(case: Path, metadata: dict, ast) -> dict:
    path = case / "proof-ast.ml"
    if not path.is_file():
        return {"admitted": False, "reason": "proof AST absent"}
    try:
        tree = ast.OcamlAstText(path.read_text(errors="replace")).parse()
        own = [node for node in ast.nodes(tree, "TypePredDef")
               if len(node.args) == 5 and node.args[1] == [] and
               node.args[3] == "own" and "CopyOnDrop" in repr(node.args[2])]
        fbc = [node for node in ast.nodes(tree, "PredCtorDecl")
               if len(node.args) == 7 and
               node.args[1] == "CopyOnDrop_full_borrow_content"]
        bodies = [node for node in ast.nodes(tree, "Func")
                  if len(node.args) == 13 and node.args[4] == "insertion_onecell" and
                  node.args[10] != ast.Sym("None")]
        if len(own) != 1 or len(fbc) != 1 or len(bodies) != 1:
            return {"admitted": False, "own_count": len(own), "fbc_count": len(fbc),
                    "body_count": len(bodies)}
        own_body, fbc_body, runtime = own[0].args[4], fbc[0].args[6], bodies[0].args[10]
        runtime_calls = [node.args[1] for node in ast.nodes(runtime, "CallExpr")
                         if len(node.args) > 1 and isinstance(node.args[1], str)]
        fbc_points = ast.nodes(fbc_body, "PointsTo")
        fbc_calls = [node.args[1] for node in ast.nodes(fbc_body, "CallExpr")
                     if len(node.args) > 1 and isinstance(node.args[1], str)]
        read_assignments = [node.args for node in ast.nodes(runtime, "AssignExpr")
                            if len(node.args) == 4 and
                            ast.location_line(node.args[0]) == metadata["read_line"]]

        def local(value):
            return value.args[1] if isinstance(value, ast.Node) and \
                value.name == "Var" and len(value.args) == 2 else None

        def is_node(value, name: str, arity: int | None = None) -> bool:
            return (isinstance(value, ast.Node) and value.name == name and
                    (arity is None or len(value.args) == arity))

        def is_u64_type(value) -> bool:
            # The pinned AST spells u64 as Some(ConstTypeExpr(loc,
            # ManifestTypeExpr(loc, Int(Unsigned, FixedWidthRank(3))))).
            # Check the full type tree rather than accepting a substring.
            if not is_node(value, "Some", 1):
                return False
            const = value.args[0]
            if not is_node(const, "ConstTypeExpr", 2):
                return False
            manifest = const.args[1]
            if not is_node(manifest, "ManifestTypeExpr", 2):
                return False
            integer = manifest.args[1]
            if not is_node(integer, "Int", 2) or integer.args[0] != ast.Sym("Unsigned"):
                return False
            rank = integer.args[1]
            return is_node(rank, "FixedWidthRank", 1) and rank.args[0] == 3

        read_linked = False
        concrete_tmp = False
        tmp_types = []
        if len(read_assignments) == 3:
            first, load, init = read_assignments
            pvar, loaded, tmp = local(first[1]), local(load[1]), local(init[1])
            deref = load[3]
            deref_ptr = local(deref.args[1]) if isinstance(deref, ast.Node) and \
                deref.name == "Deref" and len(deref.args) == 2 else None
            read_linked = (first[2] == ast.Sym("Mutation") and
                           local(first[3]) == "tail" and pvar is not None and
                           load[2] == ast.Sym("Mutation") and loaded is not None and
                           deref_ptr == pvar and init[2] == ast.Sym("Initialization") and
                           tmp == "tmp" and local(init[3]) == loaded)
            tmp_types = []
            for decl in ast.nodes(runtime, "DeclStmt"):
                if len(decl.args) != 2 or not isinstance(decl.args[1], list):
                    continue
                for binding in decl.args[1]:
                    if isinstance(binding, tuple) and len(binding) >= 3 and binding[2] == "tmp":
                        tmp_types.append(binding[1])
            concrete_tmp = len(tmp_types) == 1 and is_u64_type(tmp_types[0])
        guard_types = [node for node in ast.nodes(runtime, "StructTypeExpr")
                       if ast.location_line(node.args[0]) == metadata["guard_line"] and
                       "CopyOnDrop" in repr(node)]
        physical = ast.nodes(own_body, "PointsTo")
        calls_own = [node for node in ast.nodes(own_body, "TypePredExpr")
                     if len(node.args) >= 2 and node.args[-1] == "own"]
        false_nodes = ast.nodes(own_body, "False")
        close = [node for node in ast.nodes(runtime, "Close")
                 if "CopyOnDrop_full_borrow_content" in repr(node)]
        opened = [node for node in ast.nodes(runtime, "Open")
                  if "CopyOnDrop_full_borrow_content" in repr(node)]
        copy_line = metadata["copy_line"]
        copy_call = [node for node in ast.nodes(runtime, "CallExpr")
                     if len(node.args) > 1 and isinstance(node.args[1], str) and
                     "copy_nonoverlapping" in node.args[1] and
                     ast.location_line(node.args[0]) == copy_line]
        admitted = (read_linked and concrete_tmp and len(guard_types) == 1 and
                    len(fbc_points) == 3 and "CopyOnDrop_own" in fbc_calls and
                    len(physical) >= 2 and len(calls_own) == 1 and not false_nodes and
                    len(close) >= 1 and len(opened) == 1 and len(copy_call) == 1 and
                    not any(name in {"assume", "#assume", "leak"}
                            for name in runtime_calls))
        return {"admitted": admitted, "read_linked": read_linked,
                "concrete_u64_tmp": concrete_tmp,
                "tmp_ast_type": repr(tmp_types[0]) if len(tmp_types) == 1 else None,
                "guard_type_count": len(guard_types),
                "fbc_field_count": len(fbc_points), "own_physical_points": len(physical),
                "own_recursive_count": len(calls_own), "false_in_own_count": len(false_nodes),
                "fbc_close_count": len(close), "fbc_open_count": len(opened),
                "literal_one_copy_call_count": len(copy_call),
                "own_recursive_lines": [ast.location_line(node.args[0])
                                        for node in calls_own],
                "fbc_field_lines": [ast.location_line(node.args[0])
                                    for node in fbc_points],
                "runtime_calls": runtime_calls}
    except Exception as error:
        return {"admitted": False, "reason": f"AST admission failed closed: {error}"}


def _classify(name: str, case: Path, meta: dict, execution: dict,
              prep, mir, ast) -> dict:
    stages = execution.get("stages", {})
    source = _source_gate(case, meta, prep)
    mir_result = _mir_gate(case, meta, mir) if stages.get("decode") == 0 else \
        {"admitted": False, "reason": "decode did not pass"}
    ast_result = _ast_gate(case, meta, ast)
    log_path = case / "verifast.log"
    log = log_path.read_text(errors="replace") if log_path.is_file() else ""
    errors = [line for line in log.splitlines() if re.search(r"\berror:", line, re.I)]
    dead = [line for line in log.splitlines() if re.search(r"dead code", line, re.I)]
    headers = list(re.finditer(
        r"^\s*\d+(?:\.\d+)?s: [^\s(]+\([0-9]+,[0-9]+"
        r"(?:-[0-9]+(?:,[0-9]+)?)?\): Verifying function '([^']+)'$", log, re.M))
    segments = []
    for index, match in enumerate(headers):
        if match.group(1) == "insertion_onecell":
            end = headers[index + 1].start() if index + 1 < len(headers) else len(log)
            segments.append(log[match.start():end])
    body = len(segments) == 1
    segment = segments[0] if body else ""

    def executed_at(line: int) -> bool:
        return bool(re.search(rf"verified/lib\.rs\({line},\d+(?:-\d+(?:,\d+)?)?\): "
                              r"(?:note: )?Executing statement", segment))

    copy_executed = executed_at(meta["copy_line"])
    stages_ok = (execution.get("source_unchanged_at_every_stage") is True and
                 all(stages.get(stage) == 0 for stage in
                     ("exporter", "decode", "refinement")) and source["admitted"] and
                 mir_result.get("admitted") is True and ast_result.get("admitted") is True and
                 body and not dead)
    result_class = "INCONCLUSIVE"
    matched = False
    reason = "one or more source/MIR/AST/execution gates did not reach the target"
    if name == "positive":
        matched = (stages_ok and stages.get("verifast") == 0 and copy_executed and
                   not errors and "Executing return statement" in segment and
                   "Leak check." in segment and "0 errors found" in log)
        result_class = "PASS_FRAGMENT_ONLY" if matched else "INCONCLUSIVE"
        reason = ("concrete-u64 source-linked direct recovery witness passed source/refinement, "
                  "literal-one copy, return and leak gates; actual Drop/glue remains OPEN"
                  if matched else reason)
    else:
        target = meta.get("target") or {}
        target_line = target.get("line")
        errors_at_target = [line for line in errors if target_line is not None and
                            re.search(rf"verified/lib\.rs\({target_line},\d+(?:-\d+)?\): error:", line)]
        if name == "after_fbc_false":
            matched = (stages_ok and stages.get("verifast") == 1 and len(errors) == 1 and
                       len(errors_at_target) == 1 and "Cannot prove false" in errors[0] and
                       executed_at(meta["fbc_open_line"]) and not copy_executed)
            reason = "false assertion classified only after canonical FBC open and before recovery"
        elif name == "after_recovery_false":
            matched = (stages_ok and stages.get("verifast") == 1 and len(errors) == 1 and
                       len(errors_at_target) == 1 and "Cannot prove false" in errors[0] and
                       copy_executed)
            reason = ("recovery false matched after the literal-one copy" if matched else
                      "first recovery/copy failure retained; recovery false not credited")
        elif name == "missing_held_owner":
            # A primitive u64 has no nontrivial logical-own payload to remove:
            # VeriFast may synthesize/consume this ownership predicate. Keep
            # the generated case and its Cloud observation, but never count it
            # as an authority negative for this concrete domain.
            matched = False
            result_class = "NOT_APPLICABLE_CONCRETE_EMPTY_OWN"
            reason = ("retained diagnostic only: u64 ownership is empty/autoproducible, "
                      "so absence of an explicit held owner is not an intended negative")
        elif name == "double_physical_fbc":
            fbc_lines = ast_result.get("fbc_field_lines", [])
            allowed = {target_line}
            if fbc_lines:
                allowed.add(fbc_lines[0])
            exact = [line for line in errors if any(
                re.search(rf"verified/lib\.rs\({where},\d+(?:-\d+)?\): error:", line)
                for where in allowed)]
            matched = (stages_ok and stages.get("verifast") == 1 and len(errors) == 1 and
                       len(exact) == 1 and "No matching heap chunks" in errors[0] and
                       "CopyOnDrop_src" in errors[0])
            reason = "duplicate physical FBC consumption rejected at its field obligation" if matched else \
                "duplicate-FBC negative did not reach its exact field-resource rejection"
        if name != "missing_held_owner":
            result_class = "EXPECTED_REJECTION" if matched else "INCONCLUSIVE"
    row = {**execution, "case": name, "classification": result_class,
           "semantic_evidence": matched, "accepted": False, "reason": reason,
           "source_gate": source, "mir_gate": mir_result, "ast_gate": ast_result,
           "verifier_errors": errors, "verifier_dead_code": dead,
           "target_executed": executed_at(target_line) if name != "positive" and
           (target_line := (meta.get("target") or {}).get("line")) else False,
           "copy_executed": copy_executed}
    row["derived_ladder"] = {
        label: {"line": line, "executed": executed_at(line)}
        for label, line in meta.get("derived_ladder_lines", {}).items()
    }
    if name != "positive" and meta.get("target") and \
            name in {"after_fbc_false", "after_recovery_false"}:
        row["target_executed"] = executed_at(meta["target"]["line"])
    (case / "classification.json").write_text(json.dumps(row, indent=2, sort_keys=True) + "\n")
    return row


def run(evidence: Path, args, env: dict, execute_case,
        validated_receipt: dict) -> dict:
    """Prepare/classify isolated cases; caller supplies the pinned Cloud executor."""
    if not callable(execute_case):
        raise TypeError("execute_case callback is required")
    prep = _load("concrete_onecell_prepare", OLD / "prepare.py")
    # This call enforces the same hosted-Cloud boundary as the established
    # one-cell driver.  No source extraction is performed at import time.
    proof = _load("concrete_onecell_base_proof", OLD / "prove.py")
    provider, proof_sha = proof.base.require_hosted_cloud()
    receipt_identity = _validate_receipt(args, validated_receipt, provider, proof_sha)
    if evidence.exists():
        raise FileExistsError(f"refusing to reuse concrete-u64 evidence: {evidence}")
    source = SOURCE.read_bytes()
    if _sha(source) != prep.SOURCE_SHA or _blob(source) != prep.SOURCE_BLOB:
        raise ValueError("pinned SmallSort source identity changed")
    evidence.mkdir(parents=True)
    staging = evidence / ".generic-source-extraction"
    generic_output = staging / "cases"
    generic_report = staging / "extraction.json"
    extraction = prep.extract(generic_output, generic_report, SOURCE)

    # Confirm that the actual Drop implementation is source-pinned and that
    # its src/dst/len operands correspond to the concrete guard fields.  The
    # executed recovery statement below remains the explicit literal-one
    # adapter, not the actual Drop body.
    drop_source = _load("concrete_onecell_drop_source", OLD.parents[1] /
                        "copy-on-drop-prepare.py")
    if source.count(drop_source.COPY_CALL) != 1:
        raise ValueError("actual CopyOnDrop Drop copy-call source anchor changed")
    direct_copy = prep.COPY.strip()
    expected_direct = b"ptr::copy_nonoverlapping(gap_guard.src, gap_guard.dst, 1);"
    if direct_copy != expected_direct or b"len: 1" not in prep.GUARD:
        raise ValueError("literal-one recovery witness no longer matches one-cell guard")
    actual_copy = drop_source.COPY_CALL
    if actual_copy.strip() != b"ptr::copy_nonoverlapping(self.src, self.dst, self.len);":
        raise ValueError("pinned actual CopyOnDrop copy operands changed")

    cases_root = evidence / "cases"
    rows = {}
    for name in CASES:
        generic_case = generic_output / name
        case = cases_root / name
        (case / "original").mkdir(parents=True)
        (case / "verified").mkdir()
        original = _specialize((generic_case / "original/lib.rs").read_bytes(), prep)
        verified = _adapt_concrete_recovery(
            _specialize((generic_case / "verified/lib.rs").read_bytes(), prep), prep)
        # Specialization is textual but source-specific and conservative: the
        # two runtime files must still differ only by the recorded ghost bytes.
        generic_meta = extraction["cases"][name]
        # Preserve a direct list of ghost insertions from the generated case;
        # source-level exact stripping is checked against the independently
        # specialized original below, not inferred from an execution result.
        generic_verified = (generic_case / "verified/lib.rs").read_bytes()
        generic_original = (generic_case / "original/lib.rs").read_bytes()
        specialized_verified = _adapt_concrete_recovery(_specialize(generic_verified, prep), prep)
        if _specialize(generic_original, prep) != original or \
                specialized_verified != verified:
            raise ValueError(f"{name}: specialization was not deterministic")
        # The existing prepare module has already validated its full ghost
        # strip. Recheck it post-specialization using the same authored chunks.
        # Use generic equality as the authoritative structural check, then
        # separately require concrete runtime equality. No source bytes are
        # silently exempted by a failed recovery check.
        if _specialize(generic_original, prep) != original or \
                not all(anchor in original and anchor in verified for anchor in
                        (prep.READ, prep.GUARD, prep.COPY)):
            raise ValueError(f"{name}: specialized source/runtime anchor mismatch")
        (case / "original/lib.rs").write_bytes(original)
        (case / "verified/lib.rs").write_bytes(verified)
        source_runtime_equal = _ghost_strip_equal(original, verified, prep, name)
        if not source_runtime_equal:
            raise ValueError(f"{name}: specialized ghost strip changed runtime source")
        target = generic_meta["target"]
        row = dict(generic_meta)
        for field in ("original_sha256", "verified_sha256"):
            row[field] = _sha((case / ("original/lib.rs" if field == "original_sha256"
                                       else "verified/lib.rs")).read_bytes())
        for field in ("read_line", "guard_line", "copy_line", "fbc_close_line", "fbc_open_line",
                      "source_limits_line", "alignment_lemma_line", "source_identity_line",
                      "constructor_span_line", "own_close_line"):
            generic_anchor = getattr(prep, {
                "read_line": "READ", "guard_line": "GUARD", "copy_line": "COPY",
                "fbc_close_line": "FBC_CLOSE", "fbc_open_line": "FBC_OPEN",
                "source_limits_line": "SOURCE_LIMITS", "alignment_lemma_line": "ALIGNMENT",
                "source_identity_line": "SOURCE_IDENTITY", "constructor_span_line": "CONSTRUCTOR_SPAN",
                "own_close_line": "MISSING_OWNER_CLOSE" if name == "missing_held_owner" else "OWN_CLOSE",
            }[field])
            row[field] = _line(verified, _rewrite_types(generic_anchor))
        target_anchor = {
            "after_fbc_false": prep.FBC_FALSE,
            "after_recovery_false": prep.FALSE,
            "missing_held_owner": prep.READ,
            "double_physical_fbc": prep.DOUBLE_FBC_CLOSE,
        }.get(name)
        if target_anchor is not None:
            specialized_target = _rewrite_types(target_anchor)
            if verified.count(specialized_target) != 1:
                raise ValueError(f"{name}: specialized target anchor is not unique")
            target = dict(target or {})
            target["line"] = _line(verified, specialized_target)
        row["target"] = target
        row["case"] = name
        row["geometry_lines"] = [_line(verified, _rewrite_types(item))
                                 for item in prep.GEOMETRY]
        row["derived_ladder_lines"] = {
            "fbc_identity": _line(verified, POST_FBC_LADDER.splitlines(keepends=True)[0]),
            "fbc_dst_identity": _line(verified, POST_FBC_LADDER.splitlines(keepends=True)[1]),
            "fbc_length": _line(verified, POST_FBC_LADDER.splitlines(keepends=True)[2]),
            "fbc_src_quarter": _line(verified, POST_FBC_LADDER.splitlines(keepends=True)[4]),
            "fbc_held_quarter": _line(verified, POST_FBC_LADDER.splitlines(keepends=True)[5]),
            "copy_identity": _line(verified, POST_COPY_LADDER.splitlines(keepends=True)[0]),
            "copy_held_quarter": _line(verified, POST_COPY_LADDER.splitlines(keepends=True)[1]),
        }
        row["ghost_fragments"] = [_rewrite_types(part).decode("ascii") for part in
                                  _ghost_fragments(prep, name)]
        row["runtime_ghost_strip_equal"] = True
        post_fbc_lines = [row["alignment_lemma_line"], row["source_limits_line"],
                          *row["geometry_lines"]]
        if not (row["constructor_span_line"] < row["own_close_line"] <
                row["fbc_close_line"] < row["fbc_open_line"] < min(post_fbc_lines)):
            raise ValueError(f"{name}: pre-FBC and post-FBC source checks crossed")
        row["separation_checks"] = {
            "pre_fbc_constructor_span_line": row["constructor_span_line"],
            "fbc_close_line": row["fbc_close_line"],
            "fbc_open_line": row["fbc_open_line"],
            "post_fbc_source_alignment_line": row["alignment_lemma_line"],
            "post_fbc_source_limits_line": row["source_limits_line"],
            "post_fbc_geometry_lines": row["geometry_lines"],
            "pre_post_fbc_order_admitted": True,
        }
        rows[name] = row

    # Keep the reusable staging inputs only until all five specialized cases
    # are materialized; deleting them prevents a generic case from being
    # mistaken for the concrete-u64 proof input.
    shutil.rmtree(staging)
    (evidence / "metadata.json").write_text(json.dumps(rows, indent=2, sort_keys=True) + "\n")
    environment = {"profile": getattr(args, "profile", PROFILE),
                   "helper_profile": PROFILE, "proof_sha": proof_sha,
                   "provider": provider,
                   "validated_receipt": receipt_identity["receipt"],
                   "validated_receipt_sha256": receipt_identity["receipt_sha256"],
                   "profile_build_sha256": receipt_identity["profile_build_sha256"],
                   "actual_tool_sha256": receipt_identity["actual_tool_sha256"],
                   "schema_sha256": receipt_identity["schema_sha256"],
                   "rustc_version": receipt_identity["rustc_version"],
                   "rustc_toolchain": receipt_identity["rustc_toolchain"],
                   "source_sha256": extraction["source_sha256"],
                   "source_git_blob": extraction["source_git_blob"],
                   "source_block_sha256": extraction["source_block_sha256"],
                   "source_struct_sha256": extraction["source_struct_sha256"],
                   "actual_drop_copy_sha256": _sha(actual_copy),
                   "actual_drop_copy_line": _line(source, actual_copy),
                   "actual_drop_copy": actual_copy.decode(),
                   "executed_recovery_copy": direct_copy.decode(),
                   "copy_call_instantiation": {
                       "actual_copy_body": actual_copy.decode(),
                       "source_argument": "self.src -> gap_guard.src",
                       "destination_argument": "self.dst -> gap_guard.dst",
                       "length_argument": "self.len = guard.len = 1",
                       "direct_recovery_statement": direct_copy.decode(),
                       "actual_drop_body_executed": False,
                   },
                   "copy_scope": "direct literal-one recovery witness; actual Drop/glue OPEN",
                   "domain": "concrete u64 only; no generic, ZST, caller, comparator, or user Drop claim",
                   "claim_scope": "PASS_FRAGMENT_ONLY means only the concrete-u64 direct recovery witness; actual Drop/glue remains OPEN",
                   "accepted": False, "cases": {}}
    for name in CASES:
        case = cases_root / name
        metadata = rows[name]
        before = _hashes(case)
        execution = execute_case(case, args, env)
        after = _hashes(case)
        stage_gate = _stage_receipts(case, execution.get("stages", {}), before)
        unchanged = before == after and stage_gate["admitted"]
        execution["source_unchanged_at_every_stage"] = unchanged
        execution["source_before"] = before
        execution["source_after"] = after
        execution["stage_receipt_gate"] = stage_gate
        classified = _classify(name, case, metadata, execution, prep,
                               proof.mir, proof.ast)
        environment["cases"][name] = classified["classification"]
    summary = {"schema": "concrete-u64-onecell-consumer-v1", **environment,
               "case_details": {name: json.loads(
                   (cases_root / name / "classification.json").read_text()) for name in CASES},
               "normal_post_contract": "full conditional normal post retained",
               "normal_post_credit": "PASS_FRAGMENT_ONLY" if
               environment["cases"].get("positive") == "PASS_FRAGMENT_ONLY" else "INCONCLUSIVE",
               "unwind_credit": "NOT_EXERCISED: quiescent witness has no panicking runtime call",
               "mutable_fbc": "separate close/open and post-FBC false case",
               "held_recovery": "first failure visible; after_recovery_false only counts after copy",
               "accepted": False}
    (evidence / "concrete-u64-results.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return summary


def _ghost_fragments(prep, name: str) -> tuple[bytes, ...]:
    contract = prep.CONTRACT
    if name == "missing_held_owner":
        contract = contract.replace(
            b"*tail |-> ?held &*& <T>.own(t, held);", b"*tail |-> ?held;", 1)
    close = (prep.MISSING_OWNER_CLOSE if name == "missing_held_owner" else prep.OWN_CLOSE)
    middle = prep.SOURCE_IDENTITY + prep.CONSTRUCTOR_GEOMETRY + close + prep.FBC_CLOSE
    if name == "double_physical_fbc":
        middle += prep.DOUBLE_FBC_CLOSE
    middle += prep.FBC_OPEN + FBC_FIELD_FRAME + POST_FBC_LADDER
    if name == "after_fbc_false":
        middle += prep.FBC_FALSE
    middle += prep.ALIGNMENT + prep.SOURCE_LIMITS + b"".join(prep.GEOMETRY) + prep.DESTINATION_GEOMETRY
    # Snapshot guard fields while the canonical predicate is open. The
    # post-copy ghost-expression grammar rejects direct field dereferences.
    middle += (b"        //@ let recovery_src = gap_guard.src;\n"
               b"        //@ let recovery_dst = gap_guard.dst;\n")
    recovery = prep.RECOVER.replace(b"gap_guard.src", b"recovery_src").replace(
        b"gap_guard.dst", b"recovery_dst")
    recovery = recovery.replace(b"        //@ end_ref_readonly(held_ref);\n",
                                POST_COPY_LADDER + b"        //@ end_ref_readonly(held_ref);\n", 1)
    recovery += prep.FALSE if name == "after_recovery_false" else b""
    return (prep.OWN, prep.ALIGNMENT_LEMMA, contract, prep.ANNOTATIONS,
            middle, recovery)


def _ghost_strip_equal(original: bytes, verified: bytes, prep, name: str) -> bool:
    stripped = verified
    for chunk in _ghost_fragments(prep, name):
        specialized = _rewrite_types(chunk)
        if stripped.count(specialized) != 1:
            return False
        stripped = stripped.replace(specialized, b"", 1)
    return stripped == original


def _hashes(case: Path) -> dict:
    paths = ("original/lib.rs", "verified/lib.rs")
    return {**{path: _sha((case / path).read_bytes()) for path in paths},
            "small_sort_source": _sha(SOURCE.read_bytes())}
