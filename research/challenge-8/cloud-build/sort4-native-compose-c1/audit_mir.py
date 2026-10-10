#!/usr/bin/env python3
"""Read-only structural audit of saved paired complete composition MIR.

This classifies compiler evidence. It does not admit the frontend overlay or
claim any proof result; fresh source/MIR hashes still need independent review.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "overnight-callback"))
import probe  # noqa: E402


FN = 'name = "std::ops::FnMut::call_mut"'
HELPER = 'name = "c1_source_prefix"'
ADD = 'name = "std::ptr::const_ptr::<impl *const T>::add"'


def need(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)


def one(pattern: str, value: str, why: str) -> str:
    rows = re.findall(pattern, value, re.S)
    need(len(rows) == 1, why)
    return rows[0]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def records(body: str, name: str) -> list[str]:
    return probe.mir_list_records(body, name, probe.mir_balanced_pairs(body))


def body_record(decoded: bytes, function: str) -> str:
    text = decoded.decode("utf-8", errors="strict")
    # Callers can pass an already-extracted complete function record.
    if text.startswith("( defKind = ("):
        matches = [text] if f'defPath = "{function}"' in text[:200] else []
    else:
        pairs = probe.mir_balanced_pairs(text)
        bodies = probe.mir_list_records(text, "bodies =", pairs)
        matches = [body for body in bodies if
                   re.search(r'^\( defKind = .*?defPath = "' + function + r'"', body, re.S)]
    need(len(matches) == 1, f"ambiguous complete MIR function {function}")
    return matches[0]


def call_block(blocks: list[str], name: str) -> str:
    rows = [block for block in blocks if name in block]
    need(len(rows) == 1, f"ambiguous call {name}")
    block = rows[0]
    term = block[block.index("terminator = ("):]
    need(term.count("unwindAction = (continue = void)") == 1 and
         "target = (something = (index = " in term and
         "isCleanup = false" in block and "isCleanup = true" not in block,
         f"call {name} has non-direct unwind/target/cleanup")
    return block


def source_line(verified: bytes, needle: bytes) -> int:
    need(verified.count(needle) == 1, f"ambiguous source line {needle!r}")
    return verified[:verified.index(needle)].count(b"\n") + 1


def audit_helper(mode: str, record: bytes, verified: bytes) -> dict:
    body = body_record(record, "c1_source_prefix")
    blocks = records(body, "basicBlocks =")
    locals_ = records(body, "localDecls =")
    need(blocks and locals_, f"{mode}: missing complete blocks/locals")
    need(body.count(FN) == 1 and not any(x in body for x in
         ("isCleanup = true", "unwindAction = (cleanup", "kind = (drop = (")),
         f"{mode}: callback or cleanup inventory changed")
    call = call_block(blocks, FN)
    line = source_line(verified, b"let c1 = is_less/*@::<F, (&'cmp T, &'cmp T), 'cmp>@*/")
    term = call[call.index("terminator = ("):]
    span = int(one(r'callSpan = \(\s*regular = \(\s*lo = \(.*?line = (\d+)',
                   term, f"{mode}: callback span"))
    need(span == line and
         'type = (kind = (param = "F"))' in term and
         term.count('ty = (kind = (param = "T"))') >= 2 and
         'lateBoundGenericParamCount = 1' in term and
         'aggregateKind = (tuple = void)' in call,
         f"{mode}: source/F/two-T-ref callback binding changed")
    args = records(term, "args =")
    need(len(args) == 2, f"{mode}: callback arity")
    receiver, tuple_local = (probe.mir_local(arg, "callback argument") for arg in args)
    before = blocks[:blocks.index(call) + 1]
    stmts = [stmt for block in before for stmt in records(block, "statements =")]

    def assignment(local: str) -> str:
        rows = [stmt for stmt in stmts if probe.mir_lhs(stmt) == local]
        need(len(rows) == 1, f"{mode}: callback local {local} definition")
        return rows[0]

    recv = assignment(receiver)
    need("borKind = (mut = void)" in recv and
         re.search(r'place = \(\s*local = \(name = "_3"\),\s*'
                   r'projection = \[\(deref = void\)\]', recv) is not None,
         f"{mode}: callback receiver no longer reborrows F")
    tup = assignment(tuple_local)
    fields = records(tup, "operands =")
    need(len(fields) == 2 and "aggregateKind = (tuple = void)" in tup,
         f"{mode}: callback tuple form")
    refs = [probe.mir_local(field, "tuple field") for field in fields]
    need(refs[0] != refs[1], f"{mode}: callback tuple fields alias")

    def shared_ref_source(local: str) -> str:
        stmt = assignment(local)
        need("borKind = (shared = void)" in stmt,
             f"{mode}: callback shared reference {local}")
        return one(r'place = \(\s*local = \(name = "(_\d+)"\),\s*'
                   r'projection = \[\(deref = void\)\]', stmt,
                   f"{mode}: callback shared reference origin {local}")

    left = shared_ref_source(shared_ref_source(refs[0]))
    right = shared_ref_source(shared_ref_source(refs[1]))
    need(right == "_1" and left != "_1", f"{mode}: callback operand order")
    add = [block for block in before if ADD in block and
           re.search(r'destination = \(\s*local = \(name = "' + left + r'"\)',
                     block) is not None]
    need(len(add) == 1, f"{mode}: left operand no unique pointer add")
    add_term = add[0][add[0].index("terminator = ("):]
    add_args = records(add_term, "args =")
    need(len(add_args) == 2 and
         "int = (data = (h = 0, l = 1), size = 8)" in add_args[1],
         f"{mode}: left offset is not one element")
    base_copy = probe.mir_local(add_args[0], "pointer add base")
    need(re.search(r'use = \(\s*copy = \(\s*local = \(name = "_1"\)',
                   assignment(base_copy)) is not None,
         f"{mode}: pointer add does not copy v_base")
    events = []
    for block in blocks:
        events.extend(records(block, "statements ="))
        events.append(block[block.index("terminator = ("):])
    selected = [receiver, tuple_local, *refs,
                shared_ref_source(refs[0]), shared_ref_source(refs[1]),
                left, base_copy]
    need(len(set(selected)) == 8, f"{mode}: callback local inventory alias")
    local_inventory = {}
    for local in selected:
        decls = [decl for decl in locals_ if f'id = (name = "{local}")' in decl]
        need(len(decls) == 1, f"{mode}: local declaration {local}")
        live = [i for i, stmt in enumerate(events)
                if f'storageLive = (name = "{local}")' in stmt]
        dead = [i for i, stmt in enumerate(events)
                if f'storageDead = (name = "{local}")' in stmt]
        definitions = [i for i, event in enumerate(events)
                       if probe.mir_lhs(event) == local or
                       re.search(r'destination = \(\s*local = \(name = "' +
                                 re.escape(local) + r'"\)', event) is not None]
        need(len(live) == len(dead) == len(definitions) == 1 and
             live[0] < definitions[0] < dead[0],
             f"{mode}: local live/init/dead multiplicity/order {local}")
        address_taken = [i for i, event in enumerate(events)
                         if re.search(r'(?:ref|addressOf) = \(.*?place = \(\s*'
                                      r'local = \(name = "' + re.escape(local) +
                                      r'"\),\s*projection = \[\]',
                                      event, re.S) is not None]
        need(not address_taken, f"{mode}: callback local has direct MIR address-of {local}")
        declaration_index = locals_.index(decls[0])
        local_inventory[local] = {
            "declaration_sha256": sha(decls[0].encode()),
            "declaration_index": declaration_index,
            "storage_live_event_index": live[0],
            "initialization_event_index": definitions[0],
            "storage_dead_event_index": dead[0],
            "mir_direct_address_of_observed": False,
        }
    declaration_order = [name for name, _ in sorted(
        local_inventory.items(), key=lambda entry: entry[1]["declaration_index"])]
    numbers = [int(name[1:]) for name in declaration_order]
    need(numbers == list(range(numbers[0], numbers[0] + 8)),
         f"{mode}: callback local declaration sequence changed")
    return {
        "mode": mode, "classification": "STRUCTURAL_C1_MIR_AUDIT_NOT_FRONTEND_ADMISSION",
        "complete_record_sha256": sha(record), "block_count": len(blocks),
        "local_count": len(locals_), "callback_source_line": line,
        "callback_receiver": receiver, "callback_tuple": tuple_local,
        "ordered_ref_fields": refs, "ordered_source_pointers": [left, right],
        "local_inventory": local_inventory,
        "callback_local_declaration_order": declaration_order,
        "direct_continue": True,
    }


def audit_native(mode: str, record: bytes, verified: bytes) -> dict:
    body = body_record(record, "small_sort_general_with_scratch")
    blocks = records(body, "basicBlocks =")
    need(body.count(FN) == 0 and body.count(HELPER) == 1 and
         "isCleanup = true" not in body and "kind = (drop = (" not in body,
         f"{mode}: native call/cleanup inventory changed")
    call = call_block(blocks, HELPER)
    term = call[call.index("terminator = ("):]
    line = source_line(verified, b"let _c1 = c1_source_prefix(v_base, len, is_less);")
    span = int(one(r'callSpan = \(\s*regular = \(\s*lo = \(.*?line = (\d+)',
                   term, f"{mode}: native helper call span"))
    need(span == line, f"{mode}: native helper source span")
    args = records(term, "args =")
    need(len(args) == 3, f"{mode}: native helper arity")
    arg_locals = [probe.mir_local(arg, "native helper argument") for arg in args]
    before = blocks[:blocks.index(call) + 1]
    stmts = [stmt for block in before for stmt in records(block, "statements =")]

    def assignment(local: str) -> str:
        rows = [stmt for stmt in stmts if probe.mir_lhs(stmt) == local]
        need(len(rows) == 1, f"{mode}: native helper argument {local} definition")
        return rows[0]

    pointer = assignment(arg_locals[0])
    middle = one(r'operand = \(\s*move = \(\s*local = \(name = "(_\d+)"\)',
                 pointer, f"{mode}: native helper pointer cast operand")
    need("kind = (ptrToPtr = void)" in pointer and
         re.search(r'use = \(\s*copy = \(\s*local = \(name = "_6"\)',
                   assignment(middle)) is not None and
         re.search(r'use = \(\s*copy = \(\s*local = \(name = "_4"\)',
                   assignment(arg_locals[1])) is not None and
         "borKind = (mut = void)" in assignment(arg_locals[2]) and
         re.search(r'place = \(\s*local = \(name = "_3"\),\s*'
                   r'projection = \[\(deref = void\)\]',
                   assignment(arg_locals[2])) is not None,
         f"{mode}: native helper actual v_base/len/F arguments changed")
    return {
        "mode": mode, "classification": "STRUCTURAL_NATIVE_HELPER_CALL_NOT_STD_CFG",
        "complete_record_sha256": sha(record), "helper_source_line": line,
        "direct_continue": True,
        "argument_locals": arg_locals,
        "actual_arguments": "native v_base cast to const, len copied, F mutably reborrowed",
    }


def audit_case(case_dir: Path) -> dict:
    verified = (case_dir / "fixture/verified/lib.rs").read_bytes()
    rows = {}
    for mode in ("normal", "readonly"):
        rows[mode] = {
            "helper": audit_helper(
                mode, (case_dir / f"{mode}-c1_source_prefix-full-mir.txt").read_bytes(),
                verified),
            "native": audit_native(
                mode,
                (case_dir / f"{mode}-small_sort_general_with_scratch-full-mir.txt").read_bytes(),
                verified),
        }
    return {"classification": "PAIRED_STRUCTURAL_MIR_DIAGNOSTIC_NO_PROOF_CREDIT",
            "verified_source_sha256": sha(verified), "modes": rows}


if __name__ == "__main__":
    need(len(sys.argv) == 2, "usage: audit_mir.py /path/to/saved/case")
    print(json.dumps(audit_case(Path(sys.argv[1])), indent=2, sort_keys=True))
