#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted source-only THREADONLY frame candidate; no proof rule is enabled."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
CASE_NAME = "nine-body-wrapper-input-relation-frame"
PARENT_SHA256 = "a95aff14592b167c62c53c7ed726128ee86c7c19768cfe613504cdec841f8463"
R2_PARENT_SHA256 = "11067f06ba7c745cfb221a559fb29778eba8d7b6e65f6db1a814ff7ce72bdfd4"
ORIGINAL_SHA256 = "466882d74de217766ed8d5c583596c173df47f0e6bd40da7cb1a4c931d7265a5"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"missing frame source dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


INPUT = load(HERE / "prepare-wrapper-input-relation.py",
             "o26_wrapper_input_relation_for_frame")
OWNER = INPUT.R2.BASE.SEVEN.OWNER.OWNER
FORGET = INPUT.R2.BASE.SEVEN.FORGET


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


SAVED_GUARD = (
    b"        /*@ assert <select_unpredictable::DropOnPanic<*Element>>.own(t, ?saved_guard); @*/\n"
)
RETURNED_GUARD = (
    b"        /*@ open <select_unpredictable::DropOnPanic<*Element>>.own(t, saved_guard); @*/\n"
    b"        /*@ assert *saved_guard.inner |-> ?selected_payload; @*/\n"
    b"        /*@ open raw_ptr_own::<Element>()(t, selected_payload); @*/\n"
)
GUARD_CREATE = b"        let guard = DropOnPanic { inner: guard };\n"
DROP_CALL = b"        drop.drop_in_place();\n"
FORGET_CALL = b"        crate::mem::forget(guard);\n"

REMOVALS = (
    ("outer_guard_owner_branch_fold", OWNER.CLOSE_OWNER_LITERAL,
     DROP_CALL, "before"),
    ("saved_guard_owner_assertion", SAVED_GUARD,
     FORGET_CALL, "before"),
    ("post_forget_guard_owner_payload_projection", RETURNED_GUARD,
     FORGET_CALL, "after"),
)


def source_span(source: bytes, fragment: bytes) -> dict:
    start = source.index(fragment)
    end = start + len(fragment)
    line_start = source.rfind(b"\n", 0, start) + 1
    end_line_start = source.rfind(b"\n", 0, end) + 1
    return {"byte_start": start, "byte_end_exclusive": end,
            "line_start_one_based": source.count(b"\n", 0, start) + 1,
            "column_start_zero_based": start - line_start,
            "line_end_one_based": source.count(b"\n", 0, end) + 1,
            "column_end_zero_based": end - end_line_start,
            "bytes": len(fragment), "sha256": sha(fragment)}


def forget_contracts() -> tuple[bytes, bytes, bytes, bytes]:
    signature = b"pub unsafe fn checked_forget_owned<T>(t: T)\n"
    body = b"{\n    let _ = ManuallyDrop::new(t);\n}"
    old = (b"/*@\nreq thread_token(?tid) &*& tid == currentThread &*& <T>.own(tid, t);\n@*/\n"
           b"/*@\nens thread_token(tid) &*& <T>.own(tid, t);\n@*/\n"
           b"/*@\non_unwind_ens false;\n@*/\n")
    new = (b"/*@\nreq thread_token(?tid) &*& tid == currentThread;\n@*/\n"
           b"/*@\nens thread_token(tid);\n@*/\n"
           b"/*@\non_unwind_ens false;\n@*/\n")
    FORGET.SOURCE.require(
        body == FORGET.SOURCE.FORGET_BODY,
        "exact same-body SAFE forget helper contract/body changed")
    return signature, body, old, new


def write_case(repo: Path, out: Path) -> dict:
    provider = load(repo / "research/challenge-8/cloud-build/provider.py",
                    "o26_frame_capture_provider")
    provider.require_supported_provider()
    FORGET.SOURCE.require(repo.resolve() == REPO.resolve() and not out.exists(),
                          "THREADONLY frame repo/evidence identity changed")
    out.mkdir(parents=True)
    parent_root = out / "r2-source"
    parent = INPUT.write_case(repo, parent_root)
    parent_case = parent_root / INPUT.CASE_NAME
    before = (parent_case / "verified/lib.rs").read_bytes()
    original = (parent_case / "original/lib.rs").read_bytes()
    FORGET.SOURCE.require(
        sha(before) == parent["verified_sha256"] == PARENT_SHA256 and
        parent.get("parent_verified_sha256") == R2_PARENT_SHA256 and
        sha(original) == parent["original_sha256"] == ORIGINAL_SHA256 and
        parent.get("ghost_strip_identity") is True and
        parent.get("verified_source_reversible_three_input_relation_insertions") is True and
        parent.get("source_order") == list(INPUT.R2.BASE.ORDER),
        "exact R2 input-relation parent/source order differs")

    signature, forget_body, old_contract, new_contract = forget_contracts()
    old_helper = signature + old_contract + forget_body + b"\n"
    new_helper = signature + new_contract + forget_body + b"\n"
    FORGET.SOURCE.require(before.count(signature) == 1 and
                          before.count(forget_body) == 1 and
                          before.count(old_contract) == 1 and
                          before.count(new_contract) == 0 and
                          before.count(old_helper) == 1 and
                          all(before.count(block) == 1 and
                              block.startswith(b"        /*@") and
                              block.endswith(b"@*/\n")
                              for _, block, _, _ in REMOVALS),
                          "exact owner ghost/helper contract removal inventory differs")
    for _, _, anchor, _ in REMOVALS:
        FORGET.SOURCE.require(before.count(anchor) == 1,
                              "frame ghost removal anchor absent/ambiguous")
    for i, (name, block, anchor, side) in enumerate(REMOVALS):
        FORGET.SOURCE.require(before.index(block) < before.index(anchor)
                              if side == "before" else
                              before.index(block) > before.index(anchor),
                              f"{name}: expected source order changed")
    FORGET.SOURCE.require(
        before.index(GUARD_CREATE) < before.index(OWNER.CLOSE_OWNER_LITERAL) < before.index(DROP_CALL) <
        before.index(SAVED_GUARD) <
        before.index(FORGET_CALL) < before.index(RETURNED_GUARD) <
        before.index(OWNER.CLOSE_SELECTED),
        "outer frame-removal blocks moved or selected-cell close changed")

    after = before.replace(old_contract, new_contract, 1)
    FORGET.SOURCE.require(after.count(new_helper) == 1,
                          "thread-only contract is not attached to exact helper body")
    block_records = []
    for index, (name, block, anchor, side) in enumerate(REMOVALS):
        block_records.append({"index": index, "name": name, "anchor": anchor.decode(),
                              "utf8": block.decode(),
                              "anchor_side": side, **source_span(before, block)})
        FORGET.SOURCE.require(after.count(block) == 1,
                              f"{name}: exact removal block changed")
        after = after.replace(block, b"", 1)

    restored = after.replace(new_contract, old_contract, 1)
    for name, block, anchor, side in reversed(REMOVALS):
        if side == "before":
            restored = restored.replace(anchor, block + anchor, 1)
        else:
            restored = restored.replace(anchor, anchor + block, 1)
    strip = OWNER.strip_ghost
    FORGET.SOURCE.require(
        after != before and restored == before and
        all(after.count(block) == 0 for _, block, _, _ in REMOVALS) and
        after.count(new_contract) == 1 and after.count(old_contract) == 0 and
        strip(after) == original and sha(original) == ORIGINAL_SHA256 and
        after.count(b"crate::intrinsics::select_unpredictable(") == 3 and
        after.count(b"crate::mem::forget(guard);") == 1 and
        after.count(b".assume_init()") == 1 and
        after.count(signature) == before.count(signature) == 1 and
        after.count(FORGET.SOURCE.FORGET_BODY) ==
        before.count(FORGET.SOURCE.FORGET_BODY) == 1 and
        all(after.count(block) == 0 for _, block, _, _ in REMOVALS),
        "frame candidate is not reversible or changed runtime/ghost stripping")

    case = out / CASE_NAME
    (case / "verified").mkdir(parents=True)
    (case / "original").mkdir()
    (case / "verified/lib.rs").write_bytes(after)
    (case / "original/lib.rs").write_bytes(original)
    record = {
        "classification": "SOURCE_ONLY_THREADONLY_FRAME_CAPTURE_NOT_ACCEPTED",
        "case_name": CASE_NAME,
        "parent_case": "r2-source/" + INPUT.CASE_NAME,
        "parent_verified_sha256": PARENT_SHA256,
        "parent_parent_verified_sha256": R2_PARENT_SHA256,
        "verified_sha256": sha(after),
        "original_sha256": sha(original),
        "ghost_strip_identity": strip(after) == original,
        "source_order": list(parent["source_order"]),
        "removed_owner_ghost_blocks": block_records,
        "forget_helper": {
            "signature": signature.decode().strip(),
            "runtime_body_sha256": sha(forget_body),
            "old_contract_utf8": old_contract.decode(),
            "new_thread_only_contract_utf8": new_contract.decode(),
            "runtime_body_same_as_std_forget": True,
            "old_contract_sha256": sha(old_contract),
            "new_thread_only_contract_sha256": sha(new_contract),
            "own_requirement_removed": True,
            "own_ens_removed": True,
            "unwind_false_preserved": True,
            "same_public_generic_signature": True,
        },
        "verified_source_reversible_frame_transform": True,
        "actual_runtime_unchanged": True,
        "actual_calls_and_selected_cell_ghosts_retained": True,
        "selected_cell_never_folded_into_guard_owner": True,
        "full_mir_refinement_and_proof": "NOT_RUN",
        "old_r3_certificate_expected_to_refuse": True,
        "semantic_frontend_enabled": False,
        "actual_helper_proved": False,
        "actual_safe_forget_linked": False,
        "verification_accepted": False,
        "accepted": False,
    }
    for path in (case / "fixture.json", out / "source-summary.json"):
        path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(write_case(args.repo, args.out), indent=2, sort_keys=True),
          flush=True)


if __name__ == "__main__":
    main()
