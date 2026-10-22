#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""R20 ghost-only repair candidate for the nine-body owned-forget unit.

NIGHT-CLOUD-4 (Build 6c560082) stopped at the final
`select_unpredictable(condition, true_val, false_val).assume_init()` with an
absent `MaybeUninit_pointer_own<Element>(t, MaybeUninit::new(payload))`.
For `T = *const Element` that predicate holds no pointee permission
(`raw_ptr_own` is `true`), and the S6 profile proves
`close_MaybeUninit_pointer_own` against its definition (req true). The
repair inserts that checked lemma call for the wrapper value(s) demanded at
the final select. Pure byte transform: no tool, no Cloud, no proof credit.
"""
from __future__ import annotations

FINAL_CALL = (b"        crate::intrinsics::select_unpredictable(condition, true_val, false_val)"
              b".assume_init()\n")
PAYLOAD_ASSERTS = (b"    /*@ assert *true_ptr |-> ?true_payload; @*/\n",
                   b"    /*@ assert *false_ptr |-> ?false_payload; @*/\n")
VARIANTS = ("both", "true-only", "false-only", "none", "merged", "branch", "branch-selected")
# The existing selected-wrapper ghost block immediately before the final
# select (exact O26 owner-admission text). "merged" appends the two lemma
# calls inside it, so no new ghost statement (and no new MIR block) appears.
SELECTED_BLOCK = (
    b"        /*@ if (condition) {\n"
    b"                 std::mem::close_MaybeUninit::<*Element>(true_ptr as *std::mem::MaybeUninit<*Element>);\n"
    b"             } else {\n"
    b"                 std::mem::close_MaybeUninit::<*Element>(false_ptr as *std::mem::MaybeUninit<*Element>);\n"
    b"             } @*/\n")
MERGED_TAIL = (
    b"             }\n"
    b"             std::mem::close_MaybeUninit_pointer_own::<Element>(t, std::mem::MaybeUninit::new::<*Element>(true_payload));\n"
    b"             std::mem::close_MaybeUninit_pointer_own::<Element>(t, std::mem::MaybeUninit::new::<*Element>(false_payload)); @*/\n")


# R20 S3 showed a ghost comment accepts one statement ("merged" is a parse
# error). "branch" places the two lemma calls inside both branch blocks of the
# same if/else, so it stays one ghost statement with no new MIR block.
_LEMMAS = (
    b"                 std::mem::close_MaybeUninit_pointer_own::<Element>(t, std::mem::MaybeUninit::new::<*Element>(true_payload));\n"
    b"                 std::mem::close_MaybeUninit_pointer_own::<Element>(t, std::mem::MaybeUninit::new::<*Element>(false_payload));\n")
BRANCH_BLOCK = (
    b"        /*@ if (condition) {\n"
    b"                 std::mem::close_MaybeUninit::<*Element>(true_ptr as *std::mem::MaybeUninit<*Element>);\n"
    + _LEMMAS +
    b"             } else {\n"
    b"                 std::mem::close_MaybeUninit::<*Element>(false_ptr as *std::mem::MaybeUninit<*Element>);\n"
    + _LEMMAS +
    b"             } @*/\n")


# R20 S3b showed the re-opened guard pointee is a fresh symbol
# (selected_payload): the selected wrapper must be closed with it, the
# unselected wrapper with its original payload.
def _close(payload: bytes) -> bytes:
    return (b"                 std::mem::close_MaybeUninit_pointer_own::<Element>(t, "
            b"std::mem::MaybeUninit::new::<*Element>(" + payload + b"));\n")


SELECTED_BRANCH_BLOCK = (
    b"        /*@ if (condition) {\n"
    b"                 std::mem::close_MaybeUninit::<*Element>(true_ptr as *std::mem::MaybeUninit<*Element>);\n"
    + _close(b"selected_payload") + _close(b"false_payload") +
    b"             } else {\n"
    b"                 std::mem::close_MaybeUninit::<*Element>(false_ptr as *std::mem::MaybeUninit<*Element>);\n"
    + _close(b"true_payload") + _close(b"selected_payload") +
    b"             } @*/\n")


def need(ok: bool, why: str) -> None:
    if not ok:
        raise RuntimeError("R20-FINAL-SELECT-REPAIR: " + why)


def close_line(payload: bytes) -> bytes:
    return (b"        /*@ std::mem::close_MaybeUninit_pointer_own::<Element>(t, "
            b"std::mem::MaybeUninit::new::<*Element>(" + payload + b")); @*/\n")


def repair(verified: bytes, variant: str) -> bytes:
    """Return `verified` with ghost closes before the unique final select."""
    need(variant in VARIANTS, "unknown variant")
    need(verified.count(FINAL_CALL) == 1, "one exact final MaybeUninit select")
    for line in PAYLOAD_ASSERTS:
        need(verified.count(line) == 1, "one exact payload binding")
        need(verified.index(line) < verified.index(FINAL_CALL),
             "payload binding precedes the final select")
    need(b"close_MaybeUninit_pointer_own" not in verified,
         "unit already contains a wrapper-ownership close")
    if variant in ("merged", "branch", "branch-selected"):
        need(verified.count(SELECTED_BLOCK) == 1, "one exact selected-wrapper ghost block")
        need(verified.index(SELECTED_BLOCK) < verified.index(FINAL_CALL),
             "selected block precedes the final select")
        gap = verified[verified.index(SELECTED_BLOCK) + len(SELECTED_BLOCK):verified.index(FINAL_CALL)]
        need(all(not line.strip() or (line.lstrip().startswith(b"//") and
                                      not line.lstrip().startswith(b"//@"))
                 for line in gap.splitlines()),
             "only blank/plain comment lines between the selected block and the final select")
        if variant == "branch-selected":
            need(verified.count(b"?selected_payload; @*/") == 1 and
                 verified.index(b"?selected_payload; @*/") < verified.index(SELECTED_BLOCK),
                 "selected_payload is bound before the selected block")
            result = verified.replace(SELECTED_BLOCK, SELECTED_BRANCH_BLOCK, 1)
            stripped = result
            for payload in (b"selected_payload", b"false_payload", b"true_payload", b"selected_payload"):
                stripped = stripped.replace(_close(payload), b"", 1)
            need(stripped == verified and result.count(b"close_MaybeUninit_pointer_own") == 4,
                 "branch-selected repair changed more than the two branch blocks")
            return result
        if variant == "branch":
            result = verified.replace(SELECTED_BLOCK, BRANCH_BLOCK, 1)
            need(result.replace(_LEMMAS, b"") == verified and
                 result.count(_LEMMAS) == 2, "branch repair changed more than the two branch blocks")
            return result
        merged = SELECTED_BLOCK[:-len(b"             } @*/\n")] + MERGED_TAIL
        result = verified.replace(SELECTED_BLOCK, merged, 1)
        added = MERGED_TAIL[len(b"             }\n"):-len(b" @*/\n")] + b" "
        # Ghost-only: the change is confined to one ghost comment; removing the
        # two added lemma lines restores the input byte-for-byte.
        need(result.replace(b"             }\n" + added, b"             } ", 1) == verified,
             "merged repair changed more than the ghost block")
        return result
    inserted = {"both": close_line(b"true_payload") + close_line(b"false_payload"),
                "true-only": close_line(b"true_payload"),
                "false-only": close_line(b"false_payload"),
                "none": b""}[variant]
    result = verified.replace(FINAL_CALL, inserted + FINAL_CALL, 1)
    # Ghost-only: removing exactly the inserted comment lines restores the input.
    need(result.replace(inserted, b"", 1) == verified if inserted else result == verified,
         "repair changed more than the inserted ghost lines")
    need(all(line.lstrip().startswith(b"/*@") and line.rstrip().endswith(b"@*/")
             for line in inserted.splitlines()), "inserted text is ghost-only")
    return result
