#!/usr/bin/env python3
"""Capture or check the complete typed-MIR first-call certificate, hosted only.

Calibration never admits semantics. Admission additionally requires a separate
reviewed manifest pinning both complete function records and the source pair.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "overnight-sort4"))
import capture as sort4_capture  # noqa: E402
import probe  # noqa: E402


CALL_NAMES = {
    "std::ops::FnMut::call_mut": 5,
    "std::hint::select_unpredictable": 8,
    "std::ptr::copy_nonoverlapping": 4,
}
ADD_NAME = "std::ptr::const_ptr::<impl *const T>::add"


def need(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hosted_only() -> None:
    need(os.environ.get("GITHUB_ACTIONS") == "true" and
         os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted" and
         os.environ.get("RUNNER_OS") == "Linux",
         "first-call MIR admission requires GitHub-hosted Linux")


def one(pattern: str, value: str, why: str) -> str:
    rows = re.findall(pattern, value, re.S)
    need(len(rows) == 1, why)
    return rows[0]


def block_id(block: str) -> str:
    return one(r'^\( id = \(index = (\d+)\)', block,
               "MIR block id missing or duplicated")


def terminator(block: str) -> str:
    at = block.find("terminator = (")
    need(at >= 0, "MIR call block has no terminator")
    return block[at:]


def destination_local(term: str) -> str:
    return one(r'destination = \(\s*local = \(name = "(_\d+)"\)', term,
               "call destination local missing or duplicated")


def target_block(term: str) -> str:
    return one(r'target = \(something = \(index = (\d+)\)\)', term,
               "normal successor missing or duplicated")


def call_line(term: str) -> int:
    return int(one(r'callSpan = \(\s*regular = \(\s*lo = \(.*?line = (\d+)',
                   term, "source call span is missing or duplicated"))


def verify_direct_call(block: str, name: str) -> None:
    need(block.count(f'name = "{name}"') == 1 and
         block.count("unwindAction = (continue = void)") == 1 and
         "isCleanup = false" in block and
         "isCleanup = true" not in block and
         target_block(terminator(block)).isdigit(),
         f"typed MIR {name} action/cleanup/successor changed")


def audit(mode: str, decoded: bytes, verified: bytes) -> dict:
    text = decoded.decode(errors="strict")
    defpath, body = sort4_capture.complete_function_record(text, "sort4_stable")
    pairs = probe.mir_balanced_pairs(body)
    blocks = probe.mir_list_records(body, "basicBlocks =", pairs)
    locals_ = probe.mir_list_records(body, "localDecls =", pairs)
    need(blocks and locals_, "complete typed MIR blocks or local declarations absent")
    names = sort4_capture.FNMUT_CALL_NAME.findall(body)
    for name, count in CALL_NAMES.items():
        need(names.count(name) == count,
             f"{mode}: full MIR call inventory differs for {name}")
    need("isCleanup = true" not in body and
         "unwindAction = (cleanup" not in body and
         "unwindAction = (terminate" not in body and
         "kind = (drop = (" not in body,
         f"{mode}: new cleanup, Drop or unsupported unwind in full graph")
    for name in CALL_NAMES:
        calls = [block for block in blocks if f'name = "{name}"' in block]
        need(len(calls) == CALL_NAMES[name],
             f"{mode}: call appears outside a unique MIR block")
        for block in calls:
            verify_direct_call(block, name)

    source_lines = verified.decode(errors="strict").splitlines()
    c1_lines = [index for index, line in enumerate(source_lines, 1)
                if "let c1 = is_less" in line]
    base_lines = [index for index, line in enumerate(source_lines, 1)
                  if line.strip() == "v_base: *const T,"]
    need(len(c1_lines) == len(base_lines) == 1,
         "first source call or v_base input declaration ambiguous")
    base_decl = [row for row in locals_ if 'id = (name = "_1")' in row]
    need(len(base_decl) == 1 and
         re.search(rf'line = {base_lines[0]},\s*col =', base_decl[0]) is not None and
         "rawPtr = (" in base_decl[0] and
         'ty = (kind = (param = "T"))' in base_decl[0],
         f"{mode}: MIR input _1 no longer denotes v_base<T>")

    fnmut_blocks = [block for block in blocks
                    if 'name = "std::ops::FnMut::call_mut"' in block]
    first = [block for block in fnmut_blocks
             if call_line(terminator(block)) == c1_lines[0]]
    need(len(first) == 1, f"{mode}: first FnMut source span is ambiguous")
    first_block = first[0]
    first_id = block_id(first_block)
    first_term = terminator(first_block)
    need('type = (kind = (param = "F"))' in first_term and
         first_term.count('ty = (kind = (param = "T"))') >= 2 and
         "lateBoundGenericParamCount = 1" in first_term and
         "aggregateKind = (tuple = void)" in first_block,
         f"{mode}: first call F/T/two-ref tuple substitution changed")
    args = probe.mir_list_records(first_term, "args =",
                                  probe.mir_balanced_pairs(first_term))
    need(len(args) == 2, f"{mode}: first FnMut receiver/Args arity changed")
    receiver = probe.mir_local(args[0], "first FnMut receiver")
    args_local = probe.mir_local(args[1], "first FnMut Args")
    before_first = blocks[:blocks.index(first_block) + 1]
    statements = []
    for block in before_first:
        statements += probe.mir_list_records(
            block, "statements =", probe.mir_balanced_pairs(block))

    def assignment(local: str) -> str:
        rows = [stmt for stmt in statements if probe.mir_lhs(stmt) == local]
        need(len(rows) == 1, f"{mode}: ambiguous def of {local} before c1")
        return rows[0]

    recv = assignment(receiver)
    need("borKind = (mut = void)" in recv and
         re.search(r'place = \(\s*local = \(name = "_3"\),\s*'
                   r'projection = \[\(deref = void\)\]', recv) is not None,
         f"{mode}: comparator receiver is not the original F reborrow")
    tuple_stmt = assignment(args_local)
    need("aggregateKind = (tuple = void)" in tuple_stmt,
         f"{mode}: FnMut Args is not a tuple aggregate")
    fields = probe.mir_list_records(tuple_stmt, "operands =",
                                    probe.mir_balanced_pairs(tuple_stmt))
    need(len(fields) == 2, f"{mode}: FnMut Args field count changed")
    refs = [probe.mir_local(field, "first FnMut tuple field")
            for field in fields]
    need(refs[0] != refs[1], f"{mode}: first call aliases its tuple field locals")

    def deref_source(local: str) -> str:
        stmt = assignment(local)
        need("borKind = (shared = void)" in stmt,
             f"{mode}: tuple field {local} is not a shared reference")
        return one(r'place = \(\s*local = \(name = "(_\d+)"\),\s*'
                   r'projection = \[\(deref = void\)\]', stmt,
                   f"{mode}: shared reference {local} source changed")

    left_inner = deref_source(refs[0])
    left_ptr = deref_source(left_inner)
    right_inner = deref_source(refs[1])
    right_ptr = deref_source(right_inner)
    need(right_ptr == "_1" and left_ptr != "_1",
         f"{mode}: second tuple field no longer borrows v_base")
    add_blocks = [block for block in before_first
                  if f'name = "{ADD_NAME}"' in block and
                  destination_local(terminator(block)) == left_ptr]
    need(len(add_blocks) == 1,
         f"{mode}: first tuple field lacks unique v_base.add(1) origin")
    add_block = add_blocks[0]
    add_term = terminator(add_block)
    verify_direct_call(add_block, ADD_NAME)
    need(target_block(add_term) == first_id and call_line(add_term) == c1_lines[0],
         f"{mode}: pointer-add edge does not feed first callback")
    add_args = probe.mir_list_records(add_term, "args =",
                                      probe.mir_balanced_pairs(add_term))
    need(len(add_args) == 2 and
         "int = (data = (h = 0, l = 1), size = 8)" in add_args[1],
         f"{mode}: first pointer offset is not one element")
    base_copy = probe.mir_local(add_args[0], "first pointer-add base operand")
    need(re.search(r'use = \(\s*copy = \(\s*local = \(name = "_1"\)',
                   assignment(base_copy)) is not None,
         f"{mode}: first pointer-add base no longer copies v_base")
    return {
        "mode": mode,
        "classification": "STRUCTURAL_FIRST_CALL_AUDIT_NOT_YET_ADMITTED",
        "decoded_sha256": sha(decoded),
        "complete_function_sha256": sha(body.encode()),
        "def_path": defpath,
        "block_count": len(blocks),
        "call_counts": CALL_NAMES,
        "all_selected_call_actions_direct_continue": True,
        "all_graph_cleanup_and_drop_absent": True,
        "first_call_source_line": c1_lines[0],
        "first_call_block": first_id,
        "first_call_receiver_local": receiver,
        "ordered_tuple_field_locals": refs,
        "ordered_source_pointers": [left_ptr, right_ptr],
        "first_pointer_origin": "v_base.add(1)",
        "second_pointer_origin": "v_base",
        "first_call_normal_target": target_block(first_term),
        "first_call_unwind": "Continue",
    }


def main() -> None:
    hosted_only()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--reviewed-manifest", type=Path)
    args = parser.parse_args()
    fixture = args.fixture.resolve()
    verified = (fixture / "verified/lib.rs").read_bytes()
    original = (fixture / "original/lib.rs").read_bytes()
    prepared = json.loads((fixture / "fixture.json").read_text())
    need(prepared["classification"] ==
         "CALIBRATION_ONLY_FIRST_ACTUAL_CALL_UNADMITTED" and
         sha(verified) == prepared["verified_sha256"] and
         sha(original) == prepared["original_sha256"] and
         sort4_capture.strip_ghost(verified) == original,
         "prepared source pair or ghost-strip identity changed")
    actual, cert = sort4_capture.source_certificate(args.repo_root.resolve())
    need(original == sort4_capture.PREFIX + actual and
         cert == prepared["source_certificate"],
         "complete original sort4 body differs from pinned std source")
    rows = {mode: audit(mode, (fixture / f"{mode}-mir.txt").read_bytes(),
                        verified)
            for mode in ("normal", "readonly")}
    classification = "CALIBRATION_REVIEW_REQUIRED"
    if args.reviewed_manifest is not None:
        manifest = json.loads(args.reviewed_manifest.read_text())
        need(manifest.get("review_kind") ==
             "human_reviewed_exact_sort4_first_call_source_and_full_mir" and
             manifest.get("source_sha256") == sha(verified) and
             manifest.get("original_sha256") == sha(original) and
             manifest.get("normal_complete_function_sha256") ==
             rows["normal"]["complete_function_sha256"] and
             manifest.get("readonly_complete_function_sha256") ==
             rows["readonly"]["complete_function_sha256"] and
             manifest.get("first_call_aliases_reviewed") is True and
             manifest.get("all_runtime_calls_edges_and_cleanup_reviewed") is True,
             "reviewed exact whole-source/paired-full-MIR manifest rejected")
        classification = "EXACT_FIRST_CALL_SOURCE_MIR_ADMITTED_FOR_REVIEW"
    result = {
        "classification": classification,
        "actual_sort4_proved": False,
        "frontend_semantics_accepted": False,
        "source_sha256": sha(verified),
        "original_sha256": sha(original),
        "paired_complete_typed_mir": rows,
    }
    output = args.output.resolve()
    need(not output.exists(), "refusing to overwrite existing MIR admission result")
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"classification": classification,
                      "first_call_blocks": {mode: row["first_call_block"]
                                            for mode, row in rows.items()}},
                     sort_keys=True))


if __name__ == "__main__":
    main()
