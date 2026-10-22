"""Inactive source-only controls for the R21 final-select repair candidate.

These transforms remove one ghost ownership-close line per branch. They do
not run preparation, extraction, compilation, verification, or Cloud work and
cannot produce proof credit.
"""
from __future__ import annotations

import hashlib


PINNED_REPAIR_SOURCE_SHA256 = (
    "3646b05602b7dce35cd4b2ab8f74d8cfe280d65df2637ac4f6cc0a128dd7e2a3")
FINAL_CALL = (b"        crate::intrinsics::select_unpredictable(condition, true_val, false_val)"
              b".assume_init()\n")
PAYLOAD_ASSERTS = (
    b"    /*@ assert *true_ptr |-> ?true_payload; @*/\n",
    b"    /*@ assert *false_ptr |-> ?false_payload; @*/\n")
SELECTED_PAYLOAD_ASSERT = (
    b"        /*@ assert *saved_guard.inner |-> ?selected_payload; @*/\n")


def _close(payload: bytes) -> bytes:
    return (b"                 std::mem::close_MaybeUninit_pointer_own::<Element>(t, "
            b"std::mem::MaybeUninit::new::<*Element>(" + payload + b"));\n")


# This block is copied from SELECTED_BRANCH_BLOCK in the source file pinned
# above. Synthetic tests assert equality with that constant and pin its file.
SELECTED_BRANCH_BLOCK = (
    b"        /*@ if (condition) {\n"
    b"                 std::mem::close_MaybeUninit::<*Element>(true_ptr as *std::mem::MaybeUninit<*Element>);\n"
    + _close(b"selected_payload") + _close(b"false_payload") +
    b"             } else {\n"
    b"                 std::mem::close_MaybeUninit::<*Element>(false_ptr as *std::mem::MaybeUninit<*Element>);\n"
    + _close(b"true_payload") + _close(b"selected_payload") +
    b"             } @*/\n")
SELECTED_BRANCH_BLOCK_SHA256 = (
    "1b8f099d28b1f52b094a600e16b9040b0ca4c5daeca63c4d25717acdddc18c6e")

VARIANTS = ("omit-selected-own", "omit-unselected-own")


def _need(ok: bool, why: str) -> None:
    if not ok:
        raise RuntimeError("R21-FINAL-SELECT-CONTROLS: " + why)


def _allowed_gap(raw: bytes) -> bool:
    return all(not line.strip() or (line.lstrip().startswith(b"//") and
                                    not line.lstrip().startswith(b"//@"))
               for line in raw.splitlines())


def transform(verified: bytes, variant: str) -> bytes:
    """Return a control input by omitting the named ownership close per branch.

    `verified` must already contain the exact branch-selected repair block. The
    returned bytes differ only by removing exactly two close-lemma lines from
    that one existing ghost if/else block.
    """
    _need(variant in VARIANTS, "unknown control variant")
    _need(isinstance(verified, bytes), "verified source must be bytes")
    _need(hashlib.sha256(SELECTED_BRANCH_BLOCK).hexdigest() ==
          SELECTED_BRANCH_BLOCK_SHA256,
          "embedded selected branch block differs from its source pin")
    _need(verified.count(FINAL_CALL) == 1,
          "one exact final MaybeUninit select")
    _need(verified.count(SELECTED_BRANCH_BLOCK) == 1,
          "one exact pinned branch-selected source block")
    block_start = verified.index(SELECTED_BRANCH_BLOCK)
    for line in PAYLOAD_ASSERTS:
        _need(verified.count(line) == 1 and
              verified.index(line) < block_start,
              "one exact payload binding before the selected block")
    _need(verified.count(SELECTED_PAYLOAD_ASSERT) == 1 and
          verified.index(SELECTED_PAYLOAD_ASSERT) < block_start,
          "one selected payload binding before the selected block")
    final_start = verified.index(FINAL_CALL)
    _need(block_start < final_start,
          "selected block precedes the final select")
    gap = verified[block_start + len(SELECTED_BRANCH_BLOCK):final_start]
    _need(_allowed_gap(gap),
          "only blank/plain comment lines between selected block and final select")
    _need(verified.count(b"close_MaybeUninit_pointer_own") == 4,
          "input has exactly the four branch-selected wrapper closes")

    selected_close = _close(b"selected_payload")
    if variant == "omit-selected-own":
        target_block = SELECTED_BRANCH_BLOCK.replace(selected_close, b"", 2)
        _need(SELECTED_BRANCH_BLOCK.count(selected_close) == 2,
              "selected wrapper-close lines are unique in both branches")
    else:
        true_unselected_close = _close(b"false_payload")
        false_unselected_close = _close(b"true_payload")
        _need(SELECTED_BRANCH_BLOCK.count(true_unselected_close) == 1 and
              SELECTED_BRANCH_BLOCK.count(false_unselected_close) == 1,
              "unselected wrapper-close lines are unique in their branches")
        target_block = SELECTED_BRANCH_BLOCK.replace(true_unselected_close, b"", 1)
        target_block = target_block.replace(false_unselected_close, b"", 1)

    _need(target_block.count(b"close_MaybeUninit::<*Element>") == 2 and
          target_block.count(b"close_MaybeUninit_pointer_own") == 2 and
          target_block.count(b"if (condition)") == 1 and
          target_block.count(b"} else {") == 1,
          "control must retain the single branch and both wrapper closes")
    result = verified.replace(SELECTED_BRANCH_BLOCK, target_block, 1)
    _need(result.replace(target_block, SELECTED_BRANCH_BLOCK, 1) == verified,
          "control changed bytes beyond the exact omitted close lines")
    _need(result.count(FINAL_CALL) == 1 and
          result.count(b"close_MaybeUninit_pointer_own") == 2,
          "control final-select and remaining close counts")
    return result
