#!/usr/bin/env python3
"""Hosted diagnostic for a minimal concrete-u64 one-cell Drop interface.

Importing this module is inert.  ``prepare`` only writes source-linked proof
fixtures when the hosted runner calls it; it never invokes a compiler,
extractor, VeriFast, or a subprocess.
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
CASES = ("direct_positive", "canonical_positive", "body_entry_false",
         "body_post_false", "canonical_entry_false", "canonical_call_post_false",
         "missing_source_quarter", "missing_destination_gap")


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


def _proof_syntax(data: bytes) -> bytes:
    """Turn inherited line annotations into statements inside safety_proof."""
    return data.replace(b"//@ ", b"")


def _specialize(data: bytes) -> bytes:
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


def _specialize_alignment_lemmas(data: bytes) -> bytes:
    result = _specialize(data)
    result = result.replace(b"lem initialized_storage_alignment<u64>",
                            b"lem initialized_storage_alignment")
    result = result.replace(b"lem uninitialized_storage_alignment<u64>",
                            b"lem uninitialized_storage_alignment")
    result = result.replace(b"initialized_storage_alignment::<u64>(",
                            b"initialized_storage_alignment(")
    result = result.replace(b"uninitialized_storage_alignment::<u64>(",
                            b"uninitialized_storage_alignment(")
    return result


def _source_inputs():
    source = _load("onecell_drop_pinned_source", ROOT /
                   "research/challenge-8/merge/overnight/copy-on-drop-prepare.py")
    one = _load("onecell_drop_own_source", ROOT /
                "research/challenge-8/merge/overnight/guard-ownership/insertion-onecell/prepare.py")
    raw = SOURCE.read_bytes()
    if (_sha(raw) != source.SOURCE_SHA256 or
            source.git_blob(raw) != source.SOURCE_GIT_BLOB or
            raw.count(source.BLOCK_START) != 1 or raw.count(source.BLOCK_END) != 1):
        raise ValueError("actual SmallSort source identity/anchors changed")
    start = raw.index(source.BLOCK_START)
    end = raw.index(source.BLOCK_END, start) + len(b"}\n\n")
    block = raw[start:end]
    if (len(block) != source.BLOCK_BYTES or _sha(block) != source.BLOCK_SHA256 or
            block.count(source.DROP_SIGNATURE) != 1 or
            block.count(source.COPY_CALL) != 1):
        raise ValueError("actual CopyOnDrop three-field/Drop block changed")
    original = _specialize(source.CRATE_PREFIX + block)
    copy_call = _specialize(source.COPY_CALL)
    signature = _specialize(source.DROP_SIGNATURE)
    if (original.count(b"struct CopyOnDrop {\n") != 1 or
            original.count(b"impl Drop for CopyOnDrop {\n") != 1 or
            original.count(copy_call) != 1 or
            original.count(b"src: *const u64") != 1 or
            original.count(b"dst: *mut u64") != 1 or
            original.count(b"len: usize") != 1):
        raise ValueError("concrete Drop representation/body changed")
    own = _specialize(one.OWN).replace(
        b"[?f](*v.src |-> ?current)", b"[1/4](*v.src |-> ?current)")
    alignment_lemmas = _specialize_alignment_lemmas(one.ALIGNMENT_LEMMA)
    if (own.count(b"[1/4](*v.src |-> ?current)") != 1 or
            own.count(b"*v.dst |-?-> ?old_gap") != 1 or
            own.count(b"v.len == 1") != 1 or
            own.count(b"<u64>.own(t, current)") != 1):
        raise ValueError("canonical one-cell predicate shape changed")
    return source, one, original, signature, copy_call, own, alignment_lemmas


# This separate contract is intentionally specialized to len == 1.  It retains
# the source quarter and owner, replaces only the destination gap, and omits
# both historical root/payload interval clauses.  It still requires the
# source/destination non-overlap needed by copy_nonoverlapping.
ONECELL_CONTRACT = b"""/*@
req thread_token(?t) &*& t == currentThread &*& type_interp::<u64>() &*&
    (*self).src |-> ?src &*& (*self).dst |-> ?dst &*& (*self).len |-> ?len &*&
    struct_CopyOnDrop_padding(self) &*& len == 1 &*&
    0 < std::mem::size_of::<u64>() &*&
    std::mem::size_of::<u64>() <= isize::MAX &*&
    src as usize != 0 &*& dst as usize != 0 &*&
    src as usize % std::mem::align_of::<u64>() == 0 &*&
    dst as usize % std::mem::align_of::<u64>() == 0 &*&
    object_pointer_within_limits(src, std::mem::size_of::<u64>()) == true &*&
    object_pointer_within_limits(dst, std::mem::size_of::<u64>()) == true &*&
    src as usize <= usize::MAX - std::mem::size_of::<u64>() &*&
    dst as usize <= usize::MAX - std::mem::size_of::<u64>() &*&
    pointer_within_limits(src) == true &*& pointer_within_limits(src + 1) == true &*&
    pointer_within_limits(dst) == true &*& pointer_within_limits(dst + 1) == true &*&
    (src as usize + std::mem::size_of::<u64>() <= dst as usize ||
        dst as usize + std::mem::size_of::<u64>() <= src as usize) &*&
    [1/4]src[..1] |-> cons(?current, nil) &*& dst[..1] |-> _ &*&
    <u64>.own(t, current);
@*//*@
ens thread_token(t) &*& type_interp::<u64>() &*&
    (*self).src |-> src &*& (*self).dst |-> dst &*& (*self).len |-> 1 &*&
    struct_CopyOnDrop_padding(self) &*&
    [1/4]src[..1] |-> cons(current, nil) &*&
    dst[..1] |-> cons(current, nil) &*& <u64>.own(t, current);
@*//*@ on_unwind_ens false; @*//*@
safety_proof {
    open CopyOnDrop_full_borrow_content(_t, self)();
    open <CopyOnDrop>.own(_t, *self);
}
@*/"""

FIELD_BIND = (b"    assert (*self).src |-> ?guard_src &*& "
              b"(*self).dst |-> ?guard_dst &*& (*self).len |-> ?guard_len;\n")
LEN_ONE = b"    assert guard_len == 1;\n"
SOURCE_ARRAY = (
    b"    points_to_limits::<u64>(guard_src as *mut u64);\n"
    b"    assert pointer_within_limits(guard_src + 1) == true;\n"
    b"    close [1/4]array::<u64>(guard_src + 1, 0, nil);\n"
    b"    assert [1/4](*guard_src |-> ?source_current);\n"
    b"    close [1/4]array::<u64>(guard_src, 1, cons(source_current, nil));\n")
DEST_ARRAY = (
    b"    points_to__limits::<u64>(guard_dst);\n"
    b"    assert pointer_within_limits(guard_dst + 1) == true;\n"
    b"    close array_::<u64>(guard_dst + 1, 0, nil);\n"
    b"    assert *guard_dst |-?-> ?old_gap;\n"
    b"    close array_::<u64>(guard_dst, 1, cons(old_gap, nil));\n")
CALL = b"    call();\n"
CANONICAL_ENTRY_FALSE = b"    assert false; // TARGET: canonical onecell proof entry\n"
CANONICAL_FALSE = b"    assert false; // TARGET: canonical onecell call post\n"
BODY_FALSE = b"        //@ assert false; // TARGET: onecell Drop body entry\n"
POST_FALSE = b"        //@ assert false; // TARGET: onecell Drop normal post"


def _replace_once(data: bytes, before: bytes, after: bytes, label: str) -> bytes:
    if data.count(before) != 1:
        raise ValueError(f"{label}: source anchor is not unique")
    return data.replace(before, after, 1)


def _prepare(evidence: Path) -> dict:
    source, one, original, signature, copy_call, own, alignment_lemmas = _source_inputs()
    if evidence.exists():
        raise FileExistsError(f"refusing to reuse onecell Drop evidence: {evidence}")
    cases_dir = evidence / "cases"
    cases_dir.mkdir(parents=True)
    generic_block = source.BLOCK_START
    raw = SOURCE.read_bytes()
    start = raw.index(source.BLOCK_START)
    end = raw.index(source.BLOCK_END, start) + len(b"}\n\n")
    generic_block = raw[start:end]
    contract = _specialize(ONECELL_CONTRACT)
    source_geometry = tuple(_proof_syntax(_specialize(part)).replace(
        b"gap_guard.src", b"guard_src").replace(b"gap_guard.dst", b"guard_dst")
        for part in one.GEOMETRY)
    destination_geometry = _proof_syntax(_specialize_alignment_lemmas(
        one.DESTINATION_GEOMETRY)).replace(
        b"gap_guard.src", b"guard_src").replace(b"gap_guard.dst", b"guard_dst")
    source_limits = _proof_syntax(_specialize(one.SOURCE_LIMITS)).replace(
        b"gap_guard.src", b"guard_src")
    source_alignment = _proof_syntax(_specialize_alignment_lemmas(one.ALIGNMENT)).replace(
        b"gap_guard.src", b"guard_src")
    if any(b"//@" in part for part in
           (b"".join(source_geometry), destination_geometry,
            source_limits, source_alignment)):
        raise ValueError("line annotation remained inside safety_proof bridge")
    if (contract.count(b"len == 1") != 1 or
            b"self as usize" in contract or
            b"currentThread" not in contract or
            b"[1/4]src[..1] |-> cons(?current, nil)" not in contract or
            b"dst[..1] |-> cons(current, nil)" not in contract or
            b"on_unwind_ens false" not in contract):
        raise ValueError("one-cell body contract obligations changed")

    metadata = {
        "schema": "source-linked-u64-onecell-drop-interface-v1",
        "profile": "SOURCE_LINKED_U64_ONECELL_DROP_INTERFACE",
        "accepted": False,
        "source_sha256": source.SOURCE_SHA256,
        "source_git_blob": source.SOURCE_GIT_BLOB,
        "source_block_sha256": source.BLOCK_SHA256,
        "source_block_bytes": source.BLOCK_BYTES,
        "generic_source_block": generic_block.decode("ascii"),
        "specialized_contract_sha256": _sha(contract),
        "specialized_original_sha256": _sha(original),
        "scope": "source-linked mechanical u64 specialization; not monomorphic MIR, actual glue, generic/ZST/comparator/user-Drop proof",
        "claim": "separate len1 body interface omits root-to-payload intervals; still requires src/dst singleton nonoverlap",
        "normal_payload_posts": ["preserved source quarter", "current copied destination singleton", "u64 own"],
        "body_pre": ["three guard fields and padding", "len == 1", "source quarter singleton",
                     "uninitialized destination singleton", "src/dst singleton separation",
                     "typed bounds/alignment/no-overflow for src and dst"],
        "canonical_bridge": ["open canonical FBC and own", "bind fields and len one",
                             "derive source and destination alignment/limits from typed storage",
                             "package singleton source/destination arrays", "checked body-contract call"],
        "cases": {},
    }

    for name in CASES:
        case_contract = contract
        case_own = own
        canonical = name != "direct_positive"
        ghosts: list[bytes] = ([own, alignment_lemmas, contract] if canonical
                               else [contract])
        proof_open = (b"    open CopyOnDrop_full_borrow_content(_t, self)();\n"
                      b"    open <CopyOnDrop>.own(_t, *self);\n")
        if contract.count(proof_open) != 1:
            raise ValueError("canonical safety proof opening changed")
        bridge = (FIELD_BIND + LEN_ONE + source_alignment + source_limits +
                  b"".join(source_geometry) + destination_geometry +
                  SOURCE_ARRAY + DEST_ARRAY)
        if name == "missing_source_quarter":
            case_own = _replace_once(
                case_own,
                b"    [1/4](*v.src |-> ?current) &*& *v.dst |-?-> ?old_gap &*&\n"
                b"    <u64>.own(t, current);",
                b"    *v.dst |-?-> ?old_gap;", "missing source quarter")
            ghosts[0] = case_own
            # Keep the source conversion out so the first unavailable payload
            # is observed at the checked body-contract call.
            bridge = FIELD_BIND + LEN_ONE + destination_geometry + DEST_ARRAY
        elif name == "missing_destination_gap":
            case_own = _replace_once(
                case_own, b"*v.dst |-?-> ?old_gap &*& ", b"",
                "missing destination gap")
            ghosts[0] = case_own
            bridge = (FIELD_BIND + LEN_ONE + source_alignment + source_limits +
                      b"".join(source_geometry) + SOURCE_ARRAY)
        if canonical:
            bridge += CALL
            if name == "canonical_call_post_false":
                bridge += CANONICAL_FALSE
            case_contract = _replace_once(
                case_contract, proof_open, proof_open + bridge,
                "canonical proof bridge")
        else:
            case_contract = _replace_once(
                case_contract, proof_open, proof_open + CALL,
                "direct strong-pre body call")
        if name == "canonical_entry_false":
            case_contract = _replace_once(
                case_contract, b"safety_proof {\n",
                b"safety_proof {\n" + CANONICAL_ENTRY_FALSE,
                "canonical proof entry negative")
        if canonical:
            ghosts[2] = case_contract
        else:
            ghosts[0] = case_contract

        verified = original
        if verified.count(b"}\n\nimpl Drop for CopyOnDrop {") != 1:
            raise ValueError("custom one-cell predicate insertion anchor changed")
        if canonical:
            verified = _replace_once(
                verified, b"}\n\nimpl Drop for CopyOnDrop {",
                b"}\n\n" + case_own + alignment_lemmas +
                b"impl Drop for CopyOnDrop {",
                "one-cell own insertion")
        verified = _replace_once(verified, signature, signature + case_contract,
                                 "one-cell contract insertion")
        if name in {"body_entry_false", "body_post_false"}:
            original_body_open = original.index(b"{", original.index(signature) + len(signature))
            offset = (original_body_open + len(case_contract) +
                      (len(case_own) + len(alignment_lemmas) if canonical else 0))
            if verified[offset:offset + 1] != b"{":
                raise ValueError("Drop body offset no longer matches runtime brace")
            newline = verified.index(b"\n", offset) + 1
            marker = BODY_FALSE if name == "body_entry_false" else POST_FALSE
            if name == "body_entry_false":
                verified = verified[:newline] + marker + verified[newline:]
            else:
                post_fragment = b"\n" + marker
                verified = _replace_once(verified, copy_call,
                                         copy_call + post_fragment, "post negative")
                marker = post_fragment
            ghosts.append(marker)
        false_token = ({"body_entry_false": BODY_FALSE,
                        "body_post_false": POST_FALSE,
                        "canonical_entry_false": CANONICAL_ENTRY_FALSE,
                        "canonical_call_post_false": CANONICAL_FALSE}.get(name))

        stripped = verified
        for ghost in ghosts:
            if stripped.count(ghost) != 1:
                raise ValueError(f"{name}: ghost strip item is not unique")
            stripped = stripped.replace(ghost, b"", 1)
        if stripped != original or verified.count(copy_call) != 1:
            raise ValueError(f"{name}: runtime differs after ghost strip")

        case_dir = cases_dir / name
        (case_dir / "original").mkdir(parents=True)
        (case_dir / "verified").mkdir()
        (case_dir / "original/lib.rs").write_bytes(original)
        (case_dir / "verified/lib.rs").write_bytes(verified)
        metadata["cases"][name] = {
            "case": name, "canonical": canonical,
            "original_sha256": _sha(original), "verified_sha256": _sha(verified),
            "contract_sha256": _sha(case_contract),
            "contract_header_sha256": _sha(case_contract.split(b"safety_proof {\n", 1)[0]),
            "ghost_fragments": [part.decode("ascii") for part in ghosts],
            "source_copy_line": _line(verified, copy_call),
            "call_line": _line(verified, CALL) if canonical else None,
            "false_line": _line(verified, false_token) if false_token else None,
            "body_false_line": (_line(verified, BODY_FALSE if name == "body_entry_false"
                                       else POST_FALSE) if name in
                                {"body_entry_false", "body_post_false"} else None),
            "expected_missing": ("source_singleton" if name == "missing_source_quarter" else
                                 "destination_singleton" if name == "missing_destination_gap" else None),
            "root_interval_premises": False,
        }
    metadata["specialized_own_sha256"] = _sha(own)
    metadata["specialized_alignment_lemmas_sha256"] = _sha(alignment_lemmas)
    (evidence / "extraction.json").write_text(json.dumps(metadata, indent=2,
                                                         sort_keys=True) + "\n")
    return metadata


def _source_gate(case: Path, row: dict) -> dict:
    original = (case / "original/lib.rs").read_bytes()
    verified = (case / "verified/lib.rs").read_bytes()
    stripped = verified
    for text in row["ghost_fragments"]:
        token = text.encode("ascii")
        if stripped.count(token) != 1:
            return {"admitted": False, "reason": "ghost strip anchor count differs"}
        stripped = stripped.replace(token, b"", 1)
    exact = stripped == original
    runtime = b"ptr::copy_nonoverlapping(self.src, self.dst, self.len);" in verified
    contract = next((text.encode("ascii") for text in row["ghost_fragments"]
                     if b"safety_proof {" in text.encode("ascii")), b"")
    accepted_shape = (b"len == 1" in contract and
                      b"[1/4]src[..1] |-> cons(?current, nil)" in contract and
                      b"dst[..1] |-> cons(current, nil)" in contract and
                      b"on_unwind_ens false" in contract and
                      b"self as usize" not in contract)
    no_escape = not any(token in verified for token in
                        (b"assume_correct", b"//@ assume", b"//@ leak", b"Freeze"))
    return {"admitted": exact and runtime and accepted_shape and no_escape,
            "runtime_equal_after_ghost_strip": exact,
            "runtime_copy_keeps_dynamic_self_len": runtime,
            "onecell_payload_contract_shape": accepted_shape,
            "root_interval_premises_absent": b"self as usize" not in contract,
            "no_assume_leak_or_freeze": no_escape}


def _mir_gate(case: Path, row: dict, proof_base, drop_module) -> dict:
    """Bind the checked body copy and targeted body ghost to exact MIR spans."""
    path = case / "decode.out"
    if not path.is_file():
        return {"admitted": False, "reason": "decoded MIR absent"}
    try:
        mir = proof_base.mir_helper
        decoded = path.read_text(errors="replace")
        if (len(re.findall(r"\bvariances\s*=", decoded)) != 1 or
                not re.search(r"\bvariances\s*=\s*\[\s*\]", decoded)):
            return {"admitted": False,
                    "reason": "concrete ADT must have exactly one empty variance list"}
        tree = mir.CapnpText(decoded).parse()
        adt = mir.path(tree, "adtDefs", "cons", "h")
        fields = mir.path(adt, "variants")[0]["fields"]
        bodies = [body for body in mir.path(tree, "bodies") if
                  mir.path(body, "defPath") in drop_module._target_names(proof_base)]
        if (mir.path(adt, "id", "name") != "CopyOnDrop" or
                mir.path(adt, "kind") != {"structKind": None} or
                mir.path(adt, "variances") != [] or
                mir.path(tree, "adtDefs", "cons", "t") != {"nil": None} or
                [mir.path(field, "name", "name") for field in fields] !=
                ["src", "dst", "len"] or len(bodies) != 1):
            return {"admitted": False, "reason": "qualified ADT/body shape differs"}
        calls = []
        for index, block in enumerate(mir.path(bodies[0], "basicBlocks")):
            kind = mir.path(block, "terminator", "kind")
            if isinstance(kind, dict) and "call" in kind:
                calls.append((index, block, kind["call"]))
        runtime_calls, ghost_calls = [], []
        for item in calls:
            callee = mir.call_name(item[2])
            span_line = mir.path(item[2], "callSpan", "regular", "lo", "line")
            if callee == proof_base.MIR_COPY_CALLEE and span_line == row["source_copy_line"]:
                runtime_calls.append(item)
            elif (callee == "VeriFast_ghost_command" and
                  row.get("body_false_line") is not None and
                  span_line == row["body_false_line"]):
                ghost_calls.append(item)
            else:
                return {"admitted": False, "reason": "unrecognized Drop MIR call",
                        "callee": callee, "span_line": span_line}
        if (len(runtime_calls) != 1 or
                len(ghost_calls) != int(row.get("body_false_line") is not None)):
            return {"admitted": False, "reason": "Drop runtime/ghost call count differs",
                    "runtime_call_count": len(runtime_calls),
                    "ghost_call_count": len(ghost_calls)}
        copy_index, copy_block, call = runtime_calls[0]
        ghost_index = ghost_calls[0][0] if ghost_calls else None
        if row["case"] == "body_entry_false":
            order_ok = ghost_index is not None and ghost_index < copy_index
        elif row["case"] == "body_post_false":
            order_ok = ghost_index is not None and ghost_index > copy_index
        else:
            order_ok = ghost_index is None
        statements = mir.path(copy_block, "statements")
        writes = {}
        projected_self_writes = []
        for position, statement in enumerate(statements):
            assign = mir.assignment(statement)
            if assign is None:
                continue
            lhs = mir.path(assign, "lhsPlace")
            if mir.local_name(lhs) == "_1" and mir.path(lhs, "projection"):
                projected_self_writes.append(position)
            if not mir.path(lhs, "projection"):
                writes.setdefault(mir.local_name(lhs), []).append((position, assign))
        origins = []
        for operand in mir.path(call, "args"):
            place = next(iter(operand.values())) if (
                isinstance(operand, dict) and len(operand) == 1 and
                next(iter(operand)) in ("copy", "move")) else None
            name = (mir.local_name(place) if place is not None and
                    not mir.path(place, "projection") else None)
            origins.append(mir.field_origin(name, writes, "_1", len(statements))
                           if name is not None else None)
        admitted = (order_ok and not projected_self_writes and
                    mir.call_name(call) == proof_base.MIR_COPY_CALLEE and
                    len(origins) == 3 and all(origin is not None for origin in origins) and
                    [origin[0] for origin in origins] == [0, 1, 2])
        return {"admitted": admitted, "field_names": [
                    mir.path(field, "name", "name") for field in fields],
                "runtime_copy_count": len(runtime_calls),
                "targeted_body_ghost_count": len(ghost_calls),
                "targeted_body_ghost_order_valid": order_ok,
                "operand_field_origins": [origin[0] for origin in origins
                                          if origin is not None]}
    except Exception as error:
        return {"admitted": False, "reason": f"structured one-cell MIR admission: {error}"}


def _classify(name: str, case: Path, row: dict, execution: dict,
              drop_module, proof_base, consumer) -> dict:
    stages = execution.get("stages", {})
    source = _source_gate(case, row)
    mir = (_mir_gate(case, row, proof_base, drop_module)
           if stages.get("decode") == 0 else {"admitted": False})
    ast = (drop_module._ast_gate(case, row, proof_base)
           if stages.get("decode") == 0 else {"admitted": False})
    log_path = case / "verifast.log"
    log = log_path.read_text(errors="replace") if log_path.is_file() else ""
    errors = [line for line in log.splitlines() if re.search(r"\berror:", line, re.I)]
    dead = [line for line in log.splitlines() if re.search(r"dead code", line, re.I)]
    segment = drop_module._body_segment(log, proof_base, row)
    copy_seen = bool(re.search(
        rf"verified/lib\.rs\({row['source_copy_line']},\d+.*\): "
        r"(?:note: )?Executing statement", segment))
    return_seen = "Executing return statement" in segment
    leak_seen = "Leak check." in segment
    admission = (execution.get("source_unchanged_at_every_stage") is True and
                 all(stages.get(stage) == 0 for stage in ("exporter", "decode", "refinement")) and
                 source["admitted"] and mir.get("admitted") is True and
                 ast.get("admitted") is True)
    setup = admission and not dead
    matched_target = False
    if admission and row.get("false_line") is not None and stages.get("verifast") == 1 and len(errors) == 1:
        false_error = bool(re.search(
            rf"verified/lib\.rs\({row['false_line']},\d+-\d+\): "
            r"error: Assertion might not hold\. \(Cannot prove false\.\)", errors[0]))
        dead_after_target = all(
            (match := re.search(r"verified/lib\.rs\((\d+),", record)) is not None and
            int(match.group(1)) > row["false_line"] for record in dead)
        matched_target = false_error and dead_after_target
    if admission and not dead and row.get("expected_missing") and \
            stages.get("verifast") == 1 and len(errors) == 1:
        call_line = row.get("call_line")
        matched_target = bool(call_line and re.search(
            rf"verified/lib\.rs\({call_line},\d+.*\): error:", errors[0]))
    positive = (setup and stages.get("verifast") == 0 and not errors and
                bool(segment) and copy_seen and return_seen and leak_seen and
                "0 errors found" in log)
    classification = ("EXPECTED_REJECTION" if matched_target else
                      "DIRECT_STRONG_PRE_BODY_PASS_CONDITIONAL" if
                      positive and name == "direct_positive" else
                      "ONECELL_BODY_INTERFACE_PASS_FRAGMENT_ONLY" if positive else
                      "INCONCLUSIVE")
    if positive and name == "canonical_positive":
        classification = "CANONICAL_ONECELL_BODY_INTERFACE_PASS_FRAGMENT_ONLY"
    generated_payload_frontier = (
        name == "canonical_positive" and copy_seen and return_seen and leak_seen and
        bool(errors) and ast.get("admitted") is True and
        "src_values" not in repr(ast.get("generated_outcome_fields", {})))
    first_frontier = ("generated_drop_post_omits_payload_or_residual_payload_leak"
                      if generated_payload_frontier else
                      "none_observed" if positive else "unclassified")
    return {"case": name, "classification": classification, "accepted": False,
            "source_gate": source, "mir_gate": mir, "ast_gate": ast,
            "stages": stages, "targeted_negative_matched": matched_target,
            "first_frontier": first_frontier,
            "copy_seen": copy_seen, "return_seen": return_seen,
            "leak_seen": leak_seen, "verifier_errors": errors,
            "dead_code_records": dead,
            "generated_prototype_payload_effect": "payload remains outside generated fields/padding post; no assumed effect, leak, or glue credit",
            "caller_construction": "NOT_TESTED; explicit caller resource construction is a separate obligation",
            "direct_positive_scope": ("conditional strong-pre body only; default generated own is not canonical applicability"
                                      if name == "direct_positive" else None)}


def run(evidence: Path, args, env: dict, execute_case,
        validated_receipt: dict) -> dict:
    """Prepare and classify cases inside the validated hosted runner only."""
    if not callable(execute_case):
        raise TypeError("execute_case callback required")
    consumer = _load("onecell_drop_receipt_gate", HERE / "concrete-consumer.py")
    drop_module = _load("onecell_drop_existing_admission", HERE / "concrete-drop-body.py")
    proof_base = _load("onecell_drop_hosted_runner_gate", ROOT /
                  "research/challenge-8/merge/overnight/copy-on-drop-prove.py")
    provider, proof_sha = proof_base.require_hosted_cloud()
    identity = consumer._validate_receipt(args, validated_receipt, provider, proof_sha)
    extraction = _prepare(evidence)
    (evidence / "receipt.json").write_text(json.dumps(identity, indent=2,
                                                       sort_keys=True) + "\n")
    results = {}
    for name in CASES:
        case = evidence / "cases" / name
        row = extraction["cases"][name]
        before = consumer._hashes(case)
        execution = execute_case(case, args, env)
        after = consumer._hashes(case)
        receipts = consumer._stage_receipts(case, execution.get("stages", {}), before)
        execution["source_unchanged_at_every_stage"] = before == after and receipts["admitted"]
        execution["stage_receipt_gate"] = receipts
        classified = _classify(name, case, row, execution,
                               drop_module, proof_base, consumer)
        (case / "classification.json").write_text(json.dumps(
            classified, indent=2, sort_keys=True) + "\n")
        results[name] = classified["classification"]
    aggregate = {"schema": "source-linked-u64-onecell-drop-interface-v1",
                 "profile": extraction["profile"], "tool_profile": args.profile,
                 "accepted": False, "actual_callee_or_glue_credit": False,
                 "receipt_sha256": identity["receipt_sha256"], "cases": results,
                 "stage_contract": {
                     "all_cases": {"exporter": 0, "decode": 0, "refinement": 0,
                                   "source_unchanged_at_every_stage": True},
                     "positive": {"case": "canonical_positive", "verifast": 0,
                                  "required": ["source-linked body copy", "normal return", "leak check"],
                                  "credit": "body interface only; caller construction not tested"},
                     "direct_conditional": {"case": "direct_positive", "verifast": 0,
                                            "credit": "strong-pre body only; default-own compatibility is vacuous"},
                     "targeted_negative_verifast": 1,
                     "targeted_negative_cases": {
                         name: {"line": extraction["cases"][name]["false_line"],
                                "expected_missing": extraction["cases"][name]["expected_missing"]}
                         for name in CASES if extraction["cases"][name]["false_line"] is not None or
                         extraction["cases"][name]["expected_missing"] is not None}},
                 "scope": extraction["scope"],
                 "normal_payload_posts": extraction["normal_payload_posts"],
                 "generic_zst_comparator_user_drop": "UNSUPPORTED"}
    (evidence / "aggregate.json").write_text(json.dumps(aggregate, indent=2,
                                                         sort_keys=True) + "\n")
    return aggregate
