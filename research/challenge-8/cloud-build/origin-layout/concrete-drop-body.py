#!/usr/bin/env python3
"""Cloud-only, source-linked u64 CopyOnDrop body/interface diagnostic.

The parent supplies a validated experimental-profile receipt and Cloud stage
executor. Importing this module prepares nothing and executes no toolchain.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCE = ROOT / "library/core/src/slice/sort/shared/smallsort.rs"
CASES = ("direct_positive", "direct_first_body_false", "canonical_dst_pre",
         "canonical_positive", "prototype_false", "first_body_false")


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"pinned module unavailable: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _line(data: bytes, token: bytes) -> int:
    if data.count(token) != 1:
        raise ValueError(f"nonunique source/ghost anchor: {token!r}")
    return data[:data.index(token)].count(b"\n") + 1


def _specialize(data: bytes) -> bytes:
    """Use the same explicit type-token substitution for original and verified."""
    result = data.replace(b"CopyOnDrop_full_borrow_content::<T>",
                          b"CopyOnDrop_full_borrow_content")
    result = result.replace(b"CopyOnDrop<T>", b"CopyOnDrop")
    result = result.replace(b"impl<T> Drop", b"impl Drop")
    result = result.replace(b"pred<T> <CopyOnDrop>", b"pred <CopyOnDrop>")
    result = result.replace(b"::<T>", b"::<u64>")
    result = re.sub(rb"\bT\b", b"u64", result)
    if re.search(rb"\bT\b|CopyOnDrop<T>|impl<T>", result):
        raise ValueError("generic token remained after concrete substitution")
    return result


def _target_names(base) -> set[str]:
    concrete = base.TARGET.replace("CopyOnDrop<T>", "CopyOnDrop")
    return {concrete, concrete.replace("core::ops::Drop", "std::ops::Drop")}


def _body_segment(log: str, base, row: dict) -> str:
    header = re.compile(
        r"^\s*\d+(?:\.\d+)?s: [^\s(]+\([0-9]+,[0-9]+"
        r"(?:-[0-9]+(?:,[0-9]+)?)?\): Verifying function '([^']+)'$",
        re.M)
    found = list(header.finditer(log))
    matching = []
    for i, item in enumerate(found):
        if item.group(1) not in _target_names(base):
            continue
        end = found[i + 1].start() if i + 1 < len(found) else len(log)
        matching.append(log[item.start():end])
    if len(matching) == 1:
        return matching[0]
    # A separate prototype check may use the same qualified name. Select the
    # runtime body only through its exact prepared source location. Never
    # credit an ambiguous same-name header by position alone.
    wanted = (row["body_false_line"] or row["source_copy_line"])
    located = [segment for segment in matching if re.search(
        rf"verified/lib\.rs\({wanted},\d+.*\): (?:note: )?Executing statement",
        segment)]
    return located[0] if len(located) == 1 else ""


def _source_inputs():
    b = _load("concrete_drop_pinned_source", ROOT /
              "research/challenge-8/merge/overnight/copy-on-drop-prepare.py")
    one = _load("concrete_drop_onecell_own", ROOT /
                "research/challenge-8/merge/overnight/guard-ownership/insertion-onecell/prepare.py")
    raw = SOURCE.read_bytes()
    if _sha(raw) != b.SOURCE_SHA256 or b.git_blob(raw) != b.SOURCE_GIT_BLOB or \
            raw.count(b.BLOCK_START) != 1 or raw.count(b.BLOCK_END) != 1:
        raise ValueError("actual SmallSort source identity/anchors changed")
    start = raw.index(b.BLOCK_START)
    end = raw.index(b.BLOCK_END, start) + len(b"}\n\n")
    block = raw[start:end]
    if len(block) != b.BLOCK_BYTES or _sha(block) != b.BLOCK_SHA256 or \
            block.count(b.DROP_SIGNATURE) != 1 or block.count(b.COPY_CALL) != 1:
        raise ValueError("actual CopyOnDrop three-field/Drop block changed")
    original = _specialize(b.CRATE_PREFIX + block)
    if (original.count(b"struct CopyOnDrop {\n") != 1 or
            original.count(b"impl Drop for CopyOnDrop {\n") != 1 or
            original.count(_specialize(b.COPY_CALL)) != 1 or
            original.count(b"src: *const u64") != 1 or
            original.count(b"dst: *mut u64") != 1 or
            original.count(b"len: usize") != 1):
        raise ValueError("concrete Drop representation/source call changed")
    contract = _specialize(b.CONTRACT)
    if _specialize(b.CONTRACT.split(b"safety_proof {\n", 1)[0]) != \
            contract.split(b"safety_proof {\n", 1)[0] or \
            contract.count(b"on_unwind_ens false") != 1 or \
            contract.count(b"dst[..len] |-> _") != 1 or \
            contract.count(b"dst[..len] |-> src_values") != 1:
        raise ValueError("historical full direct contract changed")
    own = _specialize(one.OWN).replace(
        b"[?f](*v.src |-> ?current)", b"[1/4](*v.src |-> ?current)")
    if (own.count(b"[1/4](*v.src |-> ?current)") != 1 or
            own.count(b"*v.dst |-?-> ?old_gap") != 1 or
            own.count(b"v.len == 1") != 1 or
            own.count(b"<u64>.own(t, current)") != 1):
        raise ValueError("one-cell own must conserve quarter and uninitialized gap")
    return b, original, contract, own


FIELD_BIND = (b"    assert (*self).src |-> ?guard_src &*& "
              b"(*self).dst |-> ?guard_dst &*& (*self).len |-> ?guard_len;\n")
DST_PRE = b"    assert guard_dst[..guard_len] |-> _; // TARGET: initialized destination entailment\n"
LEN_ONE = b"    assert guard_len == 1;\n"
ROOT_LIMITS = b"    points_to_limits::<CopyOnDrop>(self as *mut CopyOnDrop);\n"
CALL = b"    call();\n"
PROTOTYPE_FALSE = b"    assert false; // TARGET: canonical prototype entry\n"
BODY_FALSE = b"        //@ assert false; // TARGET: first concrete Drop body statement\n"
GEOMETRY_LABELS = ("root_nonnull", "root_limits", "root_no_overflow",
                   "root_alignment", "root_source_disjoint",
                   "root_destination_disjoint")


def _geometry():
    g = _load("concrete_drop_geometry_source", ROOT /
              "research/challenge-8/merge/overnight/guard-ownership/drop-geometry/prepare.py")
    return tuple(_specialize(part) for part in g.GEOMETRY)


def _prepare(evidence: Path) -> dict:
    b, original, contract, own = _source_inputs()
    # Retain the exact generic block for saved-data outer binding replay;
    # replay must not invoke this Cloud-only source preparer.
    source_bytes = SOURCE.read_bytes()
    if _sha(source_bytes) != b.SOURCE_SHA256:
        raise ValueError("source changed while retaining the checked Drop block")
    block_start = source_bytes.index(b.BLOCK_START)
    block_end = source_bytes.index(b.BLOCK_END, block_start) + len(b"}\n\n")
    generic_block = source_bytes[block_start:block_end]
    if _sha(generic_block) != b.BLOCK_SHA256:
        raise ValueError("retained Drop block identity differs")
    geometry = _geometry()
    if evidence.exists():
        raise FileExistsError(f"refusing to reuse concrete Drop evidence: {evidence}")
    cases = evidence / "cases"
    cases.mkdir(parents=True)
    source_copy = _specialize(b.COPY_CALL)
    signature = _specialize(b.DROP_SIGNATURE)
    proof_open = _specialize(
        b"    open CopyOnDrop_full_borrow_content::<T>(_t, self)();\n"
        b"    open <CopyOnDrop<T>>.own(_t, *self);\n")
    if contract.count(proof_open) != 1:
        raise ValueError("historical safety_proof FBC/own opening changed")
    output = {"profile": "SOURCE_LINKED_U64_BODY_DIAGNOSTIC",
              "accepted": False, "source_sha256": b.SOURCE_SHA256,
              "source_git_blob": b.SOURCE_GIT_BLOB,
              "source_block_sha256": b.BLOCK_SHA256,
              "generic_source_block": generic_block.decode("ascii"),
              "generic_contract_sha256": _sha(b.CONTRACT),
              "concrete_contract_sha256": _sha(contract),
              "concrete_original_sha256": _sha(original),
              "substitution": ["CopyOnDrop_full_borrow_content::<T> -> CopyOnDrop_full_borrow_content",
                               "CopyOnDrop<T> -> CopyOnDrop",
                               "impl<T> Drop -> impl Drop", "::<T> -> ::<u64>",
                               "whole-token T -> u64"],
              "scope": "source-linked u64 body; not compiler monomorphic MIR or natural glue",
              "cases": {}}
    for name in CASES:
        canonical = name not in {"direct_positive", "direct_first_body_false"}
        case_contract = contract
        ghost = []
        if canonical:
            ghost.append(own)
            inserted = b""
            if name == "prototype_false":
                inserted += PROTOTYPE_FALSE
            if name == "canonical_dst_pre":
                inserted += FIELD_BIND + LEN_ONE + DST_PRE + CALL
            else:
                inserted += ROOT_LIMITS + FIELD_BIND + b"".join(geometry) + \
                    LEN_ONE + DST_PRE + CALL
            case_contract = contract.replace(proof_open, proof_open + inserted, 1)
            if case_contract == contract or \
                    case_contract.split(b"safety_proof {\n", 1)[0] != \
                    contract.split(b"safety_proof {\n", 1)[0]:
                raise ValueError("canonical case changed full req/ens/unwind")
            ghost.append(case_contract)
        else:
            # The generated safe-Drop prototype requires an explicit checked
            # invocation of the strong body contract in safety_proof.
            case_contract = contract.replace(proof_open, proof_open + CALL, 1)
            if case_contract == contract or \
                    case_contract.split(b"safety_proof {\n", 1)[0] != \
                    contract.split(b"safety_proof {\n", 1)[0]:
                raise ValueError("direct control changed full req/ens/unwind")
            ghost.append(case_contract)
        verified = original
        if canonical:
            marker = b"}\n\nimpl Drop for CopyOnDrop {"
            if verified.count(marker) != 1:
                raise ValueError("custom own insertion point changed")
            verified = verified.replace(marker, b"}\n\n" + own +
                                        b"impl Drop for CopyOnDrop {", 1)
        if verified.count(signature) != 1:
            raise ValueError("Drop signature count changed")
        verified = verified.replace(signature, signature + case_contract, 1)
        if name in {"first_body_false", "direct_first_body_false"}:
            # Search the runtime brace in the original before inserting a
            # safety_proof brace into the annotation.
            body_open = original.index(b"{", original.index(signature) + len(signature))
            offset = body_open + len(case_contract) + (len(own) if canonical else 0)
            if verified[offset:offset + 1] != b"{":
                raise ValueError("first-body marker no longer maps to runtime brace")
            newline = verified.index(b"\n", offset) + 1
            verified = verified[:newline] + BODY_FALSE + verified[newline:]
            ghost.append(BODY_FALSE)
        stripped = verified
        for item in ghost:
            if stripped.count(item) != 1:
                raise ValueError(f"{name}: ghost strip item is not unique")
            stripped = stripped.replace(item, b"", 1)
        if stripped != original or verified.count(source_copy) != 1:
            raise ValueError(f"{name}: runtime differs after ghost strip")
        case = cases / name
        (case / "original").mkdir(parents=True)
        (case / "verified").mkdir()
        (case / "original/lib.rs").write_bytes(original)
        (case / "verified/lib.rs").write_bytes(verified)
        row = {"case": name, "canonical": canonical,
               "original_sha256": _sha(original), "verified_sha256": _sha(verified),
               "contract_sha256": _sha(case_contract),
               "contract_header_sha256": _sha(case_contract.split(b"safety_proof {\n", 1)[0]),
               "ghost_fragments": [item.decode("ascii") for item in ghost],
               "source_copy_line": _line(verified, source_copy),
               "fbc_open_line": _line(verified, _specialize(
                   b"    open CopyOnDrop_full_borrow_content::<T>(_t, self)();\n")),
               "own_open_line": _line(verified, _specialize(
                   b"    open <CopyOnDrop<T>>.own(_t, *self);\n")),
               "field_bind_line": _line(verified, FIELD_BIND) if canonical else None,
               "layout_lines": {label: _line(verified, statement)
                                for label, statement in zip(GEOMETRY_LABELS, geometry)}
                               if canonical and name != "canonical_dst_pre" else {},
               "dst_pre_line": _line(verified, DST_PRE) if canonical else None,
               "call_line": _line(verified, CALL),
               "body_false_line": _line(verified, BODY_FALSE) if
                                  name in {"first_body_false", "direct_first_body_false"}
                                  else None,
               "prototype_false_line": _line(verified, PROTOTYPE_FALSE) if
                                       name == "prototype_false" else None}
        output["cases"][name] = row
    (evidence / "extraction.json").write_text(json.dumps(output, indent=2,
                                                        sort_keys=True) + "\n")
    return output


def _source_gate(case: Path, row: dict, contract_header: bytes) -> dict:
    original = (case / "original/lib.rs").read_bytes()
    verified = (case / "verified/lib.rs").read_bytes()
    stripped = verified
    for part in row["ghost_fragments"]:
        token = part.encode("ascii")
        if stripped.count(token) != 1:
            return {"admitted": False, "reason": "ghost fragment count differs"}
        stripped = stripped.replace(token, b"", 1)
    contract = row["ghost_fragments"][1 if row["canonical"] else 0].encode()
    admitted = (stripped == original and _sha(original) == row["original_sha256"] and
                _sha(verified) == row["verified_sha256"] and
                _sha(contract.split(b"safety_proof {\n", 1)[0]) == _sha(contract_header) and
                b"ptr::copy_nonoverlapping(self.src, self.dst, self.len);" in verified and
                b"on_unwind_ens false" in contract and
                not any(token in verified for token in
                        (b"assume_correct", b"//@ assume", b"//@ leak", b"Freeze")))
    return {"admitted": admitted, "runtime_equal_after_ghost_strip": stripped == original,
            "conditional_initialized_dst": True,
            "uninitialized_onecell_own": row["canonical"]}


def _mir_gate(case: Path, base) -> dict:
    path = case / "decode.out"
    if not path.is_file():
        return {"admitted": False, "reason": "decoded MIR absent"}
    try:
        mir = base.mir_helper
        decoded = path.read_text(errors="replace")
        # This disposable specialization removes the sole type parameter.
        # The exporter must therefore report exactly one empty ADT variance
        # list; the generic helper's one-invariant normalization is inapplicable.
        if len(re.findall(r"\bvariances\s*=", decoded)) != 1 or not re.search(
                r"\bvariances\s*=\s*\[\s*\]", decoded):
            return {"admitted": False,
                    "reason": "concrete ADT must have exactly one empty variance list"}
        tree = mir.CapnpText(decoded).parse()
        adt = mir.path(tree, "adtDefs", "cons", "h")
        fields = mir.path(adt, "variants")[0]["fields"]
        bodies = [body for body in mir.path(tree, "bodies") if
                  mir.path(body, "defPath") in _target_names(base)]
        if (mir.path(adt, "id", "name") != "CopyOnDrop" or
                mir.path(adt, "kind") != {"structKind": None} or
                mir.path(adt, "variances") != [] or
                mir.path(tree, "adtDefs", "cons", "t") != {"nil": None} or
                [mir.path(field, "name", "name") for field in fields] !=
                ["src", "dst", "len"] or len(bodies) != 1):
            return {"admitted": False, "reason": "qualified ADT/body shape differs"}
        calls = []
        blocks = mir.path(bodies[0], "basicBlocks")
        for index, block in enumerate(blocks):
            kind = mir.path(block, "terminator", "kind")
            if isinstance(kind, dict) and "call" in kind:
                calls.append((index, block, kind["call"]))
        if len(calls) != 1:
            return {"admitted": False, "reason": "Drop MIR call count differs",
                    "call_count": len(calls)}
        index, block, call = calls[0]
        statements = mir.path(block, "statements")
        writes = {}
        projected_self_writes = []
        for position, statement in enumerate(statements):
            assign = mir.assignment(statement)
            if assign is None:
                continue
            lhs = mir.path(assign, "lhsPlace")
            if base.local_name(lhs) == "_1" and mir.path(lhs, "projection"):
                projected_self_writes.append(position)
            if not mir.path(lhs, "projection"):
                writes.setdefault(base.local_name(lhs), []).append((position, assign))
        origins = []
        for operand in mir.path(call, "args"):
            place = next(iter(operand.values())) if (
                isinstance(operand, dict) and len(operand) == 1 and
                next(iter(operand)) in ("copy", "move")) else None
            name = (base.local_name(place) if place is not None and
                    not mir.path(place, "projection") else None)
            origins.append(base.field_origin(name, writes, "_1", len(statements))
                           if name is not None else None)
        admitted = (index == 0 and not projected_self_writes and
                    mir.call_name(call) == base.MIR_COPY_CALLEE and
                    len(origins) == 3 and all(origin is not None for origin in origins) and
                    [origin[0] for origin in origins] == [0, 1, 2])
        return {"admitted": admitted, "body_count": len(bodies),
                "field_names": [mir.path(field, "name", "name") for field in fields],
                "call_count": len(calls), "operand_field_origins":
                    [origin[0] for origin in origins if origin is not None],
                "dynamic_source_operand": len(origins) == 3 and
                    origins[2] is not None and origins[2][0] == 2}
    except Exception as error:
        return {"admitted": False, "reason": f"structured MIR admission: {error}"}


def _ast_gate(case: Path, row: dict, base) -> dict:
    path = case / "proof-ast.ml"
    if not path.is_file():
        return {"admitted": False, "reason": "proof AST absent"}
    try:
        ast = base.ast_helper
        tree = ast.OcamlAstText(path.read_text(errors="replace")).parse()
        funcs = [node for node in ast.nodes(tree, "Func") if
                 len(node.args) == 13 and node.args[4] in
                 _target_names(base)]
        bodies = [node for node in funcs if isinstance(node.args[10], ast.Node) and
                  node.args[10].name == "Some"]
        declarations = [node for node in funcs if node.args[10] == ast.Sym("None")]
        if len(funcs) != 2 or len(bodies) != 1 or len(declarations) != 1:
            return {"admitted": False, "reason": "Drop declaration/body count differs"}
        body = bodies[0]
        generated = declarations[0].args[8]
        outcomes = [node for node in ast.nodes(generated, "SwitchExpr") if
                    len(node.args) == 4 and isinstance(node.args[2], list) and
                    len(node.args[2]) == 2 and all(
                        isinstance(arm, ast.Node) and arm.name == "SwitchExprClause" and
                        len(arm.args) == 4 for arm in node.args[2])]
        generated_arms = {}
        if len(outcomes) == 1:
            switch = outcomes[0]
            for arm in switch.args[2]:
                tag, binders, assertion = arm.args[1], arm.args[2], arm.args[3]
                calls = [node.args[1] for node in ast.nodes(assertion, "CallExpr")
                         if len(node.args) > 1 and isinstance(node.args[1], str)]
                fields = []
                for node in ast.nodes(assertion, "PointsTo"):
                    field = node.args[1] if len(node.args) >= 2 else None
                    if (isinstance(field, ast.Node) and field.name == "Read" and
                            len(field.args) == 3):
                        fields.append(field.args[2])
                generated_arms[tag] = {"binders": binders, "fields": fields,
                                       "calls": calls, "body": assertion}
        normal = generated_arms.get("returning", {})
        unwind = generated_arms.get("unwinding", {})
        generated_pre_calls = [node.args[1] for node in ast.nodes(generated, "CallExpr")
                               if len(node.args) > 1 and isinstance(node.args[1], str)]
        generated_shape = (
            len(outcomes) == 1 and len(generated_arms) == 2 and
            normal.get("binders") == ["result"] and unwind.get("binders") == [] and
            normal.get("fields") == unwind.get("fields") == ["src", "dst", "len"] and
            repr(normal.get("body")) == repr(unwind.get("body")) and
            "CopyOnDrop_full_borrow_content" in generated_pre_calls and
            all("struct_CopyOnDrop_padding" in arm.get("calls", []) and
                "thread_token" in arm.get("calls", [])
                for arm in (normal, unwind)) and
            not any(token in repr(generated) for token in
                    ("src_values", "old_gap", "completed_payload")))
        prototype = body.args[7][1] if isinstance(body.args[7], tuple) else None
        proof = (prototype.args[0][1] if isinstance(prototype, ast.Node) and
                 prototype.name == "Some" and
                 isinstance(prototype.args[0], tuple) else [])
        opens = [node.args[2] for node in ast.nodes(proof, "Open") if len(node.args) >= 3]
        calls = [node.args[1] for node in ast.nodes(proof, "CallExpr") if
                 len(node.args) > 1 and isinstance(node.args[1], str)]
        runtime = body.args[10].args[0][0]
        copy = [node for node in ast.nodes(runtime, "CallExpr") if
                len(node.args) > 1 and node.args[1] == base.AST_COPY_CALLEE and
                ast.location_line(node.args[0]) == row["source_copy_line"]]
        switches = [node for node in ast.nodes(runtime, "SwitchStmt") if
                    len(node.args) == 3 and node.args[1] in copy]
        origins = []
        if len(copy) == len(switches) == 1:
            _, origins = base.ast_copy_operand_field_origins(
                runtime, switches[0], copy[0], row["source_copy_line"])
        fbc = [node for node in ast.nodes(tree, "PredCtorDecl") if
               len(node.args) >= 2 and node.args[1] ==
               "CopyOnDrop_full_borrow_content"]
        field_names = []
        if len(fbc) == 1:
            for node in ast.nodes(fbc[0].args[-1], "PointsTo"):
                field = node.args[1] if len(node.args) >= 2 else None
                if (isinstance(field, ast.Node) and field.name == "Read" and
                        len(field.args) == 3):
                    field_names.append(field.args[2])
        own = [node for node in ast.nodes(tree, "TypePredDef") if
               len(node.args) >= 4 and node.args[3] == "own" and
               "CopyOnDrop" in repr(node.args[2])]
        expected_opens = ["CopyOnDrop_full_borrow_content", "CopyOnDrop_own"]
        admitted = (generated_shape and opens == expected_opens and len(copy) == 1 and
                    len(switches) == 1 and origins == [0, 1, 2] and
                    field_names == ["src", "dst", "len"] and len(fbc) == 1 and
                    (len(own) == 1 if row["canonical"] else True) and
                    "call" in calls and
                    not ast.nodes(proof, "Assume") and not ast.nodes(proof, "Leak"))
        return {"admitted": admitted, "fbc_fields": field_names,
                "custom_own_count": len(own), "prototype_opens": opens,
                "prototype_calls": calls, "runtime_dynamic_copy_count": len(copy),
                "runtime_copy_field_origins": origins,
                "generated_contract_structural_gate": generated_shape,
                "generated_outcome_tags": list(generated_arms),
                "generated_outcome_fields": {tag: arm["fields"] for tag, arm in
                                             generated_arms.items()},
                "generated_outcome_calls": {tag: arm["calls"] for tag, arm in
                                            generated_arms.items()}}
    except Exception as error:
        return {"admitted": False, "reason": f"structured AST admission: {error}"}


def _classify(name: str, case: Path, row: dict, execution: dict,
              contract_header: bytes, base, consumer) -> dict:
    stages = execution.get("stages", {})
    source = _source_gate(case, row, contract_header)
    mir = _mir_gate(case, base) if stages.get("decode") == 0 else {"admitted": False}
    ast = _ast_gate(case, row, base) if stages.get("decode") == 0 else {"admitted": False}
    log = ((case / "verifast.log").read_text(errors="replace") if
           (case / "verifast.log").is_file() else "")
    errors = [line for line in log.splitlines() if re.search(r"\berror:", line, re.I)]
    dead = [line for line in log.splitlines() if re.search(r"dead code", line, re.I)]
    segment = _body_segment(log, base, row)
    copy_line = row["source_copy_line"]
    copy_seen = bool(re.search(rf"verified/lib\.rs\({copy_line},\d+.*\): "
                               r"(?:note: )?Executing statement", segment))
    return_seen = "Executing return statement" in segment
    leak_seen = "Leak check." in segment
    setup = (execution.get("source_unchanged_at_every_stage") is True and
             all(stages.get(stage) == 0 for stage in
                 ("exporter", "decode", "refinement")) and
             source["admitted"] and mir.get("admitted") is True and
             ast.get("admitted") is True and not dead)
    frontier = "setup_or_admission"
    if setup:
        if name == "canonical_dst_pre":
            dst_line = row["dst_pre_line"]
            prefixes = (row["fbc_open_line"], row["own_open_line"],
                        row["field_bind_line"])
            prefix_seen = all(re.search(
                rf"verified/lib\.rs\({line},\d+.*\): (?:note: )?Executing statement",
                log) for line in prefixes)
            exact_dst_error = (len(errors) == 1 and dst_line is not None and
                               bool(re.search(rf"verified/lib\.rs\({dst_line},\d+.*\): error:",
                                              errors[0])))
            frontier = ("onecell_initialized_destination_entailment"
                        if prefix_seen and exact_dst_error else
                        "canonical_dst_pre_first_failure_unclassified")
        else:
            for label, line in row["layout_lines"].items():
                if any(re.search(rf"verified/lib\.rs\({line},\d+.*\): error:", e)
                       for e in errors):
                    frontier = "root_geometry:" + label
                    break
            else:
                if row["dst_pre_line"] and any(re.search(
                    rf"verified/lib\.rs\({row['dst_pre_line']},\d+.*\): error:", e)
                    for e in errors):
                    frontier = "onecell_initialized_destination_entailment"
                elif row["call_line"] and any(re.search(
                    rf"verified/lib\.rs\({row['call_line']},\d+.*\): error:", e)
                    for e in errors):
                    frontier = "strong_pre_or_canonical_compatibility"
                elif copy_seen and return_seen and leak_seen and errors:
                    frontier = "canonical_post_or_residual_payload_leak"
                elif copy_seen and return_seen and errors:
                    frontier = "return_or_canonical_post_before_leak"
                elif copy_seen:
                    frontier = "body_copy_or_direct_post"
                elif segment:
                    frontier = "body_entry_before_copy"
                else:
                    frontier = "canonical_prototype_before_body"
    expected_false_line = row["prototype_false_line"] or row["body_false_line"]
    matched_false = (setup and expected_false_line is not None and
                     stages.get("verifast") == 1 and len(errors) == 1 and
                     bool(re.search(
                         rf"verified/lib\.rs\({expected_false_line},\d+-\d+\): "
                         r"error: Assertion might not hold\. \(Cannot prove false\.\)",
                         errors[0])) and
                     (bool(segment) if row["body_false_line"] else not bool(segment)) and
                     not copy_seen)
    positive = (setup and stages.get("verifast") == 0 and not errors and
                bool(segment) and copy_seen and return_seen and leak_seen and
                "0 errors found" in log)
    if matched_false:
        status = "EXPECTED_REJECTION"
    elif positive and name == "direct_positive":
        status = "CONDITIONAL_INITIALIZED_DST_BODY_PASS"
    elif positive:
        status = "SOURCE_LINKED_CANONICAL_DIAGNOSTIC_PASS"
    else:
        status = "INCONCLUSIVE"
    body_observations = {"source_linked_body_segment": bool(segment),
                         "copy_executed": copy_seen,
                         "return_seen": return_seen, "leak_seen": leak_seen,
                         "global_verifier_errors": len(errors)}
    return {"case": name, "classification": status, "accepted": False,
            "actual_callee_or_glue_credit": False,
            "source_gate": source, "mir_gate": mir, "ast_gate": ast,
            "first_frontier": frontier, "verifier_errors": errors,
            "dead_code_records": dead, "body_seen": bool(segment),
            "dynamic_copy_executed": copy_seen,
            "return_seen": return_seen, "leak_seen": leak_seen,
            "body_observations_without_independent_credit": body_observations,
            "matched_false": matched_false, "stages": stages,
            "stage_receipt_gate": execution.get("stage_receipt_gate"),
            "parent_execution": execution}


def run(evidence: Path, args, env: dict, execute_case,
        validated_receipt: dict) -> dict:
    """Run only inside the parent's hosted Cloud runner and validated profile."""
    if not callable(execute_case):
        raise TypeError("execute_case callback required")
    consumer = _load("concrete_drop_receipt_gate", HERE / "concrete-consumer.py")
    proof = _load("concrete_drop_hosted_gate", ROOT /
                  "research/challenge-8/merge/overnight/copy-on-drop-prove.py")
    provider, proof_sha = proof.require_hosted_cloud()
    identity = consumer._validate_receipt(args, validated_receipt, provider, proof_sha)
    extraction = _prepare(evidence)
    (evidence / "receipt.json").write_text(json.dumps(identity, indent=2,
                                                     sort_keys=True) + "\n")
    _, _, contract, _ = _source_inputs()
    contract_header = contract.split(b"safety_proof {\n", 1)[0]
    statuses = {}
    for name in CASES:
        case = evidence / "cases" / name
        before = consumer._hashes(case)
        execution = execute_case(case, args, env)
        after = consumer._hashes(case)
        receipt = consumer._stage_receipts(case, execution.get("stages", {}), before)
        execution["source_unchanged_at_every_stage"] = (
            before == after and receipt["admitted"])
        execution["stage_receipt_gate"] = receipt
        classified = _classify(name, case, extraction["cases"][name], execution,
                               contract_header, proof, consumer)
        (case / "classification.json").write_text(json.dumps(classified,
                                            indent=2, sort_keys=True) + "\n")
        statuses[name] = classified["classification"]
    result = {"profile": "SOURCE_LINKED_U64_BODY_DIAGNOSTIC",
              "tool_profile": args.profile, "accepted": False,
              "actual_callee_or_glue_credit": False,
              "receipt_sha256": identity["receipt_sha256"],
              "cases": statuses}
    (evidence / "aggregate.json").write_text(json.dumps(result, indent=2,
                                                    sort_keys=True) + "\n")
    return result
