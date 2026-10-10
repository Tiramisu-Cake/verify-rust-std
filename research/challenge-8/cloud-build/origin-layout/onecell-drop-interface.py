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
CASES = ("direct_positive", "canonical_no_effect", "canonical_positive",
         "body_entry_false", "body_post_false", "canonical_entry_false",
         "canonical_call_post_false", "duplicate_effect_close",
         "missing_source_quarter", "missing_destination_gap",
         "wrong_effect_signature", "missing_effect_definition")


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
    [1/4]src[..1] |-> cons(?current, nil) &*& dst[..1] |-> _ &*&
    <u64>.own(t, current) &*&
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
    pointer_within_limits(dst) == true &*&
    (src as usize + std::mem::size_of::<u64>() <= dst as usize ||
        dst as usize + std::mem::size_of::<u64>() <= src as usize) &*&
    pointer_within_limits(dst + 1) == true;
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
EFFECT_NAME = b"CopyOnDrop_drop_effect"
EFFECT_DEF = (b"pred CopyOnDrop_drop_effect(t: thread_id_t, src: *const u64, "
              b"dst: *mut u64, len: usize;) =\n"
              b"    len == 1 &*& type_interp::<u64>() &*&\n"
              b"    [1/4]src[..1] |-> cons(?current, nil) &*&\n"
              b"    dst[..1] |-> cons(current, nil) &*& <u64>.own(t, current);\n")
EFFECT_DECL = (b"pred CopyOnDrop_drop_effect(t: thread_id_t, src: *const u64, "
               b"dst: *mut u64, len: usize;);\n")
EFFECT_CLOSE = b"    close CopyOnDrop_drop_effect(_t, guard_src, guard_dst, guard_len);\n"
EFFECT_DUPLICATE = (b"    close CopyOnDrop_drop_effect(_t, guard_src, guard_dst, guard_len); "
                    b"// TARGET: duplicate onecell effect resources\n")
EFFECT_WRONG_DEF = (b"pred CopyOnDrop_drop_effect(t: thread_id_t, src: *const u64, "
                    b"dst: *mut u64, len: u32;) =\n"
                    b"    len == 1 &*& type_interp::<u64>() &*&\n"
                    b"    [1/4]src[..1] |-> cons(?current, nil) &*&\n"
                    b"    dst[..1] |-> cons(current, nil) &*& <u64>.own(t, current);\n")
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
        "schema": "source-linked-u64-onecell-drop-effect-v1",
        "profile": "SOURCE_LINKED_U64_ONECELL_DROP_EFFECT",
        "accepted": False,
        "source_sha256": source.SOURCE_SHA256,
        "source_git_blob": source.SOURCE_GIT_BLOB,
        "source_block_sha256": source.BLOCK_SHA256,
        "source_block_bytes": source.BLOCK_BYTES,
        "generic_source_block": generic_block.decode("ascii"),
        "specialized_contract_sha256": _sha(contract),
        "specialized_original_sha256": _sha(original),
        "scope": "source-linked mechanical u64 specialization; not monomorphic MIR, actual glue, generic/ZST/comparator/user-Drop proof",
        "claim": "explicit len1 normal-effect predicate bridges generated fields/padding posts to the checked body payload; no glue/caller credit",
        "normal_payload_posts": ["thread token", "opaque CopyOnDrop_drop_effect carrying type_interp, source quarter, copied destination singleton, and u64 own"],
        "body_pre": ["three guard fields and padding", "len == 1", "source quarter singleton",
                     "uninitialized destination singleton", "src/dst singleton separation",
                     "typed bounds/alignment/no-overflow for src and dst"],
        "canonical_bridge": ["open canonical FBC and own", "bind fields and len one",
                             "derive source and destination alignment/limits from typed storage",
                             "package singleton source/destination arrays", "checked body-contract call",
                             "close exact explicit normal-effect predicate after call"],
        "u64_own_omission_negative": "NOT_APPLICABLE; no empty u64 own resource is supplied or claimed",
        "cases": {},
    }

    for name in CASES:
        case_contract = contract
        case_own = own
        canonical = name != "direct_positive"
        use_effect = canonical and name != "canonical_no_effect"
        effect_contents = (EFFECT_DEF if name not in
                           {"wrong_effect_signature", "missing_effect_definition"} else
                           EFFECT_WRONG_DEF
                           if name == "wrong_effect_signature" else
                           EFFECT_DECL)
        effect_fragment = b"/*@\n" + effect_contents + b"@*/\n\n"
        ghosts: list[bytes] = ([case_own, alignment_lemmas, contract] if canonical
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
                b"    *v.dst |-?-> ?old_gap;",
                "missing source quarter and tied owner")
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
            if use_effect:
                bridge += EFFECT_CLOSE
                if name == "duplicate_effect_close":
                    bridge += EFFECT_DUPLICATE
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
            if use_effect:
                ghosts.insert(2, effect_fragment)
        else:
            ghosts[0] = case_contract

        verified = original
        if verified.count(b"}\n\nimpl Drop for CopyOnDrop {") != 1:
            raise ValueError("custom one-cell predicate insertion anchor changed")
        if canonical:
            verified = _replace_once(
                verified, b"}\n\nimpl Drop for CopyOnDrop {",
                b"}\n\n" + case_own + alignment_lemmas +
                (effect_fragment if use_effect else b"") +
                b"impl Drop for CopyOnDrop {",
                "one-cell own insertion")
        verified = _replace_once(verified, signature, signature + case_contract,
                                 "one-cell contract insertion")
        if name in {"body_entry_false", "body_post_false"}:
            original_body_open = original.index(b"{", original.index(signature) + len(signature))
            offset = (original_body_open + len(case_contract) +
                      (len(case_own) + len(alignment_lemmas) +
                       (len(effect_fragment) if use_effect else 0)
                       if canonical else 0))
            if verified[offset:offset + 1] != b"{":
                raise ValueError("Drop body offset no longer matches runtime brace")
            newline = verified.index(b"\n", offset) + 1
            marker = BODY_FALSE if name == "body_entry_false" else POST_FALSE
            if name == "body_entry_false":
                verified = verified[:newline] + marker + verified[newline:]
            else:
                post_fragment = b"\n" + marker + b"\n"
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
            "case": name, "canonical": canonical, "uses_effect": use_effect,
            "effect_fixture_kind": ("wrong_signature" if name == "wrong_effect_signature" else
                                    "missing_definition" if name == "missing_effect_definition" else
                                    "exact" if use_effect else "absent"),
            "original_sha256": _sha(original), "verified_sha256": _sha(verified),
            "contract_sha256": _sha(case_contract),
            "contract_header_sha256": _sha(case_contract.split(b"safety_proof {\n", 1)[0]),
            "ghost_fragments": [part.decode("ascii") for part in ghosts],
            "source_copy_line": _line(verified, copy_call),
            "call_line": _line(verified, CALL) if canonical else None,
            "effect_close_line": (_line(verified, EFFECT_CLOSE) if use_effect else None),
            "duplicate_effect_line": (_line(verified, EFFECT_DUPLICATE)
                                       if name == "duplicate_effect_close" else None),
            "false_line": _line(verified, false_token) if false_token else None,
            "body_false_line": (_line(verified, BODY_FALSE if name == "body_entry_false"
                                       else POST_FALSE) if name in
                                {"body_entry_false", "body_post_false"} else None),
            "expected_missing": ("source_singleton" if name == "missing_source_quarter" else
                                 "destination_singleton" if name == "missing_destination_gap" else None),
            "expected_qualification_failure": ("wrong_effect_signature" if name == "wrong_effect_signature" else
                                               "missing_effect_definition" if name == "missing_effect_definition" else None),
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
    expected_effect = ({
        "exact": b"/*@\n" + EFFECT_DEF + b"@*/\n\n",
        "wrong_signature": b"/*@\n" + EFFECT_WRONG_DEF + b"@*/\n\n",
        "missing_definition": b"/*@\n" + EFFECT_DECL + b"@*/\n\n",
        "absent": b"",
    }.get(row.get("effect_fixture_kind"), None))
    effect_fixture_ok = (EFFECT_NAME not in verified if
                         row.get("effect_fixture_kind") == "absent" else
                         expected_effect is not None and
                         verified.count(expected_effect) == 1 and
                         ((row.get("effect_fixture_kind") == "exact" and
                           verified.count(EFFECT_DEF) == 1 and EFFECT_DECL not in verified) or
                          (row.get("effect_fixture_kind") == "wrong_signature" and
                           verified.count(EFFECT_WRONG_DEF) == 1 and EFFECT_DECL not in verified) or
                          (row.get("effect_fixture_kind") == "missing_definition" and
                           verified.count(EFFECT_DECL) == 1 and EFFECT_DEF not in verified)))
    effect_close_ok = (verified.count(EFFECT_CLOSE) == 1 if row.get("uses_effect")
                       else EFFECT_NAME not in verified)
    integrity = (exact and runtime and accepted_shape and no_escape and
                 effect_fixture_ok and effect_close_ok)
    return {"admitted": integrity,
            "runtime_equal_after_ghost_strip": exact,
            "runtime_copy_keeps_dynamic_self_len": runtime,
            "onecell_payload_contract_shape": accepted_shape,
            "root_interval_premises_absent": b"self as usize" not in contract,
            "no_assume_leak_or_freeze": no_escape,
            "effect_fixture_integrity": effect_fixture_ok,
            "effect_definition_exact_current_tie": row.get("effect_fixture_kind") == "exact",
            "effect_call_count_matches_fixture": effect_close_ok}


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


def _effect_ast_gate(case: Path, row: dict, proof_base, drop_module) -> dict:
    """Admit the existing body bindings plus exactly one normal-only effect."""
    path = case / "proof-ast.ml"
    if not path.is_file():
        return {"admitted": False, "reason": "proof AST absent"}
    try:
        ast = proof_base.ast_helper
        tree = ast.OcamlAstText(path.read_text(errors="replace")).parse()
        base = drop_module._ast_gate(case, row, proof_base)
        funcs = [node for node in ast.nodes(tree, "Func") if
                 len(node.args) == 13 and node.args[4] in
                 drop_module._target_names(proof_base)]
        declarations = [node for node in funcs if node.args[10] == ast.Sym("None")]
        bodies = [node for node in funcs if isinstance(node.args[10], ast.Node) and
                  node.args[10].name == "Some"]
        if len(funcs) != 2 or len(declarations) != 1 or len(bodies) != 1:
            return {"admitted": False, "reason": "qualified Drop AST declaration/body count differs",
                    "base_body_gate": base}
        generated = declarations[0].args[8]
        generated_call_names = [node.args[1] for node in ast.nodes(generated, "CallExpr")
                                if len(node.args) > 1 and isinstance(node.args[1], str)]
        switches = [node for node in ast.nodes(generated, "SwitchExpr") if
                    len(node.args) == 4 and isinstance(node.args[2], list) and
                    len(node.args[2]) == 2 and all(
                        isinstance(arm, ast.Node) and arm.name == "SwitchExprClause" and
                        len(arm.args) == 4 for arm in node.args[2])]
        if len(switches) != 1:
            return {"admitted": False, "reason": "generated Drop outcomes differ",
                    "base_body_gate": base}
        arms = {}
        for arm in switches[0].args[2]:
            tag, binders, assertion = arm.args[1], arm.args[2], arm.args[3]
            calls = [node for node in ast.nodes(assertion, "CallExpr")
                     if len(node.args) == 6 and isinstance(node.args[1], str)]
            fields = []
            for node in ast.nodes(assertion, "PointsTo"):
                field = node.args[1] if len(node.args) >= 2 else None
                if (isinstance(field, ast.Node) and field.name == "Read" and
                        len(field.args) == 3):
                    fields.append(field.args[2])
            arms[tag] = {"binders": binders, "assertion": assertion,
                         "calls": [call.args[1] for call in calls],
                         "call_nodes": calls, "fields": fields}
        normal, unwind = arms.get("returning", {}), arms.get("unwinding", {})
        expected_common = {"struct_CopyOnDrop_padding", "thread_token"}
        def is_effect_name(name):
            # These fixtures are rooted directly in the crate module, so the
            # uniquely qualified sibling symbol is the unprefixed exact name.
            return name == EFFECT_NAME.decode()

        effect_calls = [node for node in normal.get("call_nodes", [])
                        if is_effect_name(node.args[1])]
        unwind_effects = [node for node in unwind.get("call_nodes", [])
                          if is_effect_name(node.args[1])]
        normal_common = [name for name in normal.get("calls", [])
                         if not is_effect_name(name)]
        unwind_common = [name for name in unwind.get("calls", [])
                         if not is_effect_name(name)]
        normal_counts = {name: normal_common.count(name) for name in set(normal_common)}
        unwind_counts = {name: unwind_common.count(name) for name in set(unwind_common)}
        effect_args_ok = False
        effect_arg_names = []
        field_variables = {}
        for node in ast.nodes(normal.get("assertion"), "PointsTo"):
            if len(node.args) < 4:
                continue
            read = node.args[1]
            if (isinstance(read, ast.Node) and read.name == "Read" and
                    len(read.args) == 3 and read.args[2] in ("src", "dst", "len")):
                try:
                    field_pattern = ast.narg(node.args[3], "VarPat", 2)
                    if not isinstance(field_pattern[1], str):
                        continue
                    field_variables[read.args[2]] = field_pattern[1]
                except (ValueError, TypeError, ast.AdmissionError):
                    pass
        thread_calls = [node for node in normal.get("call_nodes", [])
                        if node.args[1] == "thread_token"]
        thread_variable = None
        if len(thread_calls) == 1:
            token_args = ast.narg(thread_calls[0], "CallExpr", 6)[4]
            if isinstance(token_args, list) and len(token_args) == 1:
                try:
                    thread_variable = ast.var(ast.narg(token_args[0], "LitPat", 1)[0])
                except (ValueError, TypeError, ast.AdmissionError):
                    pass
        if len(effect_calls) == 1:
            call_args = ast.narg(effect_calls[0], "CallExpr", 6)
            patterns = call_args[4]
            if (call_args[2] == [] and call_args[3] == [] and
                    call_args[5] == ast.Sym("PredFamCall") and
                    isinstance(patterns, list) and len(patterns) == 4):
                try:
                    effect_arg_names = [ast.var(ast.narg(pattern, "LitPat", 1)[0])
                                        for pattern in patterns]
                    effect_args_ok = (
                        len(set(effect_arg_names)) == 4 and
                        field_variables == {"src": effect_arg_names[1],
                                            "dst": effect_arg_names[2],
                                            "len": effect_arg_names[3]} and
                        thread_variable == effect_arg_names[0])
                except (ValueError, TypeError, ast.AdmissionError):
                    effect_args_ok = False
        prototype = bodies[0].args[7][1] if isinstance(bodies[0].args[7], tuple) else None
        proof = (prototype.args[0][1] if isinstance(prototype, ast.Node) and
                 prototype.name == "Some" and
                 isinstance(prototype.args[0], tuple) else [])
        opens = [node.args[2] for node in ast.nodes(proof, "Open") if len(node.args) >= 3]
        closes = [node.args[2] for node in ast.nodes(proof, "Close") if len(node.args) >= 3]
        effect_post = (
            normal.get("binders") == ["result"] and unwind.get("binders") == [] and
            normal.get("fields") == unwind.get("fields") == ["src", "dst", "len"] and
            len(ast.nodes(normal.get("assertion"), "PointsTo")) == 3 and
            len(ast.nodes(unwind.get("assertion"), "PointsTo")) == 3 and
            not unwind_effects and len(effect_calls) == 1 and effect_args_ok and
            all(normal_counts.get(name) == 1 and unwind_counts.get(name) == 1
                for name in expected_common) and
            set(normal_counts) == expected_common and
            set(unwind_counts) == expected_common and
            generated_call_names.count("CopyOnDrop_full_borrow_content") == 1 and
            not any(token in repr(generated) for token in
                    ("src_values", "old_gap", "completed_payload")))
        body_linkage = (
            base.get("runtime_dynamic_copy_count") == 1 and
            base.get("runtime_copy_field_origins") == [0, 1, 2] and
            base.get("fbc_fields") == ["src", "dst", "len"] and
            base.get("custom_own_count") == 1 and
            base.get("prototype_opens") ==
                ["CopyOnDrop_full_borrow_content", "CopyOnDrop_own"] and
            "call" in base.get("prototype_calls", []) and
            closes.count("CopyOnDrop_drop_effect") ==
                (2 if row["case"] == "duplicate_effect_close" else 1) and
            not ast.nodes(proof, "Assume") and not ast.nodes(proof, "Leak"))
        return {"admitted": effect_post and body_linkage,
                "generated_normal_only_effect": effect_post,
                "generated_unwind_unchanged_effect_absent": not unwind_effects,
                "effect_argument_count_and_uniqueness": effect_args_ok,
                "effect_argument_names": effect_arg_names,
                "generated_field_variables": field_variables,
                "generated_outcome_fields": {tag: arm["fields"] for tag, arm in arms.items()},
                "generated_outcome_calls": {tag: arm["calls"] for tag, arm in arms.items()},
                "generated_call_names": generated_call_names,
                "body_linkage": body_linkage, "base_body_gate": base,
                "prototype_closes": closes}
    except Exception as error:
        return {"admitted": False, "reason": f"structured one-cell effect AST admission: {error}"}


def _classify(name: str, case: Path, row: dict, execution: dict,
              drop_module, proof_base, consumer) -> dict:
    stages = execution.get("stages", {})
    source = _source_gate(case, row)
    mir = (_mir_gate(case, row, proof_base, drop_module)
           if stages.get("decode") == 0 else {"admitted": False})
    ast = ((_effect_ast_gate(case, row, proof_base, drop_module)
            if row.get("uses_effect") else
            drop_module._ast_gate(case, row, proof_base))
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
        # A call-pre refusal counts only at its intended storage predicate.
        # Earlier pure geometry failures remain INCONCLUSIVE at the same line.
        error = errors[0]
        predicate = ("array" if row["expected_missing"] == "source_singleton"
                     else "array_" if row["expected_missing"] == "destination_singleton"
                     else None)
        matched_target = bool(
            call_line and predicate and re.search(
                rf"verified/lib\.rs\({call_line},\d+.*\): error: "
                rf"No matching heap chunks?: (?:\[[^\]]+\])?{predicate}<u64>\(", error))
    if admission and name == "duplicate_effect_close" and \
            stages.get("verifast") == 1 and len(errors) == 1:
        line = row.get("duplicate_effect_line")
        matched_target = bool(line and re.search(
            rf"verified/lib\.rs\({line},\d+.*\): error:", errors[0]))
    positive = (setup and stages.get("verifast") == 0 and not errors and
                bool(segment) and copy_seen and return_seen and leak_seen and
                "0 errors found" in log)
    qualification_diagnostics = "\n".join(
        (case / f"{stage}.log").read_text(errors="replace")
        for stage in ("exporter", "decode")
        if (case / f"{stage}.log").is_file())
    qualification_rejection = (
        bool(row.get("expected_qualification_failure")) and
        source.get("admitted") is True and
        execution.get("source_files_unchanged") is True and
        any(stages.get(stage) == 1 for stage in ("exporter", "decode")) and
        "Malformed CopyOnDrop_drop_effect opt-in predicate" in qualification_diagnostics)
    no_effect_refusal = (
        name == "canonical_no_effect" and admission and
        stages.get("verifast") == 1 and copy_seen and return_seen and leak_seen and
        bool(errors) and ast.get("generated_contract_structural_gate") is True and
        not ast.get("generated_outcome_calls", {}).get("returning", []).count("CopyOnDrop_drop_effect"))
    classification = ("EXPECTED_EFFECT_QUALIFICATION_REJECTION" if qualification_rejection else
                      "EXPECTED_NO_EFFECT_PAYLOAD_LEAK_REFUSAL" if no_effect_refusal else
                      "EXPECTED_REJECTION" if matched_target else
                      "DIRECT_STRONG_PRE_BODY_PASS_CONDITIONAL" if
                      positive and name == "direct_positive" else
                      "ONECELL_BODY_INTERFACE_PASS_FRAGMENT_ONLY" if positive else
                      "INCONCLUSIVE")
    if positive and name == "canonical_positive" and ast.get("admitted") is True:
        classification = "CANONICAL_ONECELL_EFFECT_INTERFACE_PASS_FRAGMENT_ONLY"
    generated_payload_frontier = (
        name == "canonical_no_effect" and copy_seen and return_seen and leak_seen and
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
            "generated_prototype_payload_effect": (
                "explicit normal-only effect admitted by AST gate; unwind unchanged; no glue/caller credit"
                if row.get("uses_effect") else
                "generated fields/padding post omits payload; retained no-effect refusal control"),
            "qualification_diagnostic": ("Malformed CopyOnDrop_drop_effect opt-in predicate"
                                         if qualification_rejection else None),
            "effect_scope": ("normal generated post only; unwind unchanged; no compiler glue/caller construction credit"
                             if row.get("uses_effect") else "no explicit effect; canonical no-effect is a retained refusal control"
                             if name == "canonical_no_effect" else None),
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
        execution["source_files_unchanged"] = before == after
        receipts = consumer._stage_receipts(case, execution.get("stages", {}), before)
        execution["source_unchanged_at_every_stage"] = before == after and receipts["admitted"]
        execution["stage_receipt_gate"] = receipts
        classified = _classify(name, case, row, execution,
                               drop_module, proof_base, consumer)
        (case / "classification.json").write_text(json.dumps(
            classified, indent=2, sort_keys=True) + "\n")
        results[name] = classified["classification"]
    aggregate = {"schema": "source-linked-u64-onecell-drop-effect-v1",
                 "profile": extraction["profile"], "tool_profile": args.profile,
                 "accepted": False, "actual_callee_or_glue_credit": False,
                 "receipt_sha256": identity["receipt_sha256"], "cases": results,
                 "stage_contract": {
                     "ordinary_cases": {"exporter": 0, "decode": 0, "refinement": 0,
                                        "source_unchanged_at_every_stage": True},
                     "qualification_negative_cases": {
                         "cases": ["wrong_effect_signature", "missing_effect_definition"],
                         "expected": {"early_stage": ["exporter", "decode"],
                                      "diagnostic": "Malformed CopyOnDrop_drop_effect opt-in predicate"}},
                     "positive": {"case": "canonical_positive", "verifast": 0,
                                  "required": ["source-linked body copy", "normal return", "leak check"],
                                  "required_effect": "normal generated post includes exact same-file effect; unwind remains unchanged",
                                  "credit": "canonical one-cell body interface only; caller/glue construction not tested"},
                     "no_effect_control": {"case": "canonical_no_effect", "verifast": 1,
                                           "expected": "retained generated-post payload leak/refusal"},
                     "direct_conditional": {"case": "direct_positive", "verifast": 0,
                                            "credit": "strong-pre body only; default-own compatibility is vacuous"},
                     "targeted_negative_verifast": 1,
                     "targeted_negative_cases": {
                         name: {"false_line": extraction["cases"][name]["false_line"],
                                "target_line": extraction["cases"][name]["duplicate_effect_line"],
                                "expected_missing": extraction["cases"][name]["expected_missing"]}
                         for name in CASES if extraction["cases"][name]["false_line"] is not None or
                         extraction["cases"][name]["expected_missing"] is not None or
                         extraction["cases"][name]["duplicate_effect_line"] is not None}},
                 "scope": extraction["scope"],
                 "normal_payload_posts": extraction["normal_payload_posts"],
                 "generic_zst_comparator_user_drop": "UNSUPPORTED"}
    (evidence / "aggregate.json").write_text(json.dumps(aggregate, indent=2,
                                                         sort_keys=True) + "\n")
    return aggregate
