#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted source-only diagnostic for actual select's truthful guard owner.

This prepares an exact-runtime ghost candidate; it installs no frontend rule
and claims no proof of the actual helper, generic forget, or nested Drop.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
OWNER_PRED = (
    b"/*@\npred<T> <select_unpredictable::DropOnPanic<T>>.own(t, g) =\n"
    b"    *g.inner |-> ?payload &*& <T>.own(t, payload);\n@*/\n"
)
SAFETY_PROOFS = {
    "positive": (
        b"/*@\nsafety_proof {\n"
        b"    let r = call();\n"
        b"    open raw_ptr_own::<Element>()(_t, r);\n"
        b"}\n@*/\n"
    ),
    "outcome_result": (
        b"/*@\nsafety_proof {\n"
        b"    let outcome = call();\n"
        b"    open raw_ptr_own::<Element>()(_t, fn_outcome_result(outcome));\n"
        b"}\n@*/\n"
    ),
    "omitted_open": (
        b"/*@\nsafety_proof {\n"
        b"    let r = call();\n"
        b"}\n@*/\n"
    ),
    "wrong_pointer": (
        b"/*@\nsafety_proof {\n"
        b"    let r = call();\n"
        b"    open raw_ptr_own::<Element>()(_t, true_val);\n"
        b"}\n@*/\n"
    ),
}
SAFETY_ANCHOR = b"/*@\non_unwind_ens false;\n@*/\n{\n"
# The linked S6 actual contract has adjacent annotation blocks.  Its tail
# uniquely identifies the actual function; the standalone anchor also occurs
# in two of the linked helper callees, so it cannot be counted globally.
S6_LINKED_SAFETY_ANCHOR = b"@*//*@ on_unwind_ens false; @*/\n{\n"
NESTED_DROP_CALL = b"            unsafe { self.inner.drop_in_place() }\n"
NESTED_DROP_GHOST = (
    b"            //@ open <select_unpredictable::DropOnPanic<T>>.full_borrow_content(_t, self)();\n"
    b"            //@ open <select_unpredictable::DropOnPanic<T>>.own(_t, ?g);\n"
)
OPEN_WRAPPERS = (
    b"    /*@ std::mem::open_MaybeUninit::<*Element>(true_ptr as *std::mem::MaybeUninit<*Element>); @*/\n"
    b"    /*@ std::mem::open_MaybeUninit::<*Element>(false_ptr as *std::mem::MaybeUninit<*Element>); @*/\n"
    b"    /*@ assert *true_ptr |-> ?true_payload; @*/\n"
    b"    /*@ assert *false_ptr |-> ?false_payload; @*/\n"
)
CLOSE_OWNER = (
    b"        /*@ if (condition) {\n"
    b"                 close raw_ptr_own::<Element>()(t, true_payload);\n"
    b"                 close <select_unpredictable::DropOnPanic<*Element>>.own(t, guard);\n"
    b"             } else {\n"
    b"                 close raw_ptr_own::<Element>()(t, false_payload);\n"
    b"                 close <select_unpredictable::DropOnPanic<*Element>>.own(t, guard);\n"
    b"             } @*/\n"
)
CLOSE_OWNER_LITERAL = CLOSE_OWNER.replace(
    b"own(t, guard);",
    b"own(t, select_unpredictable::DropOnPanic::<*Element> { inner: guard });")
CLOSE_UNSELECTED = (
    b"        /*@ if (condition) {\n"
    b"                 std::mem::close_MaybeUninit::<*Element>(false_ptr as *std::mem::MaybeUninit<*Element>);\n"
    b"             } else {\n"
    b"                 std::mem::close_MaybeUninit::<*Element>(true_ptr as *std::mem::MaybeUninit<*Element>);\n"
    b"             } @*/\n"
)
OPEN_OWNER = (
    b"        /*@ open <select_unpredictable::DropOnPanic<*Element>>.own(t, guard); @*/\n"
    b"        /*@ assert *guard.inner |-> ?selected_payload; @*/\n"
    b"        /*@ open raw_ptr_own::<Element>()(t, selected_payload); @*/\n"
)
CLOSE_SELECTED = (
    b"        /*@ if (condition) {\n"
    b"                 std::mem::close_MaybeUninit::<*Element>(true_ptr as *std::mem::MaybeUninit<*Element>);\n"
    b"             } else {\n"
    b"                 std::mem::close_MaybeUninit::<*Element>(false_ptr as *std::mem::MaybeUninit<*Element>);\n"
    b"             } @*/\n"
)
INSERTIONS = (
    (b"    let false_ptr = false_val.as_mut_ptr();\n", OPEN_WRAPPERS),
    (b"        let guard = DropOnPanic { inner: guard };\n", CLOSE_OWNER),
    (b"        drop.drop_in_place();\n", CLOSE_UNSELECTED + OPEN_OWNER),
    (b"        crate::mem::forget(guard);\n", CLOSE_SELECTED),
)


def load_actual():
    path = HERE / "prepare-actual-helper-capture.py"
    spec = importlib.util.spec_from_file_location("overnight_actual_owner_base", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("actual helper source preparer unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ACTUAL = load_actual()


def require(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)


def strip_ghost(source: bytes) -> bytes:
    source = re.sub(rb"(?m)^[ \t]*/\*@.*?@\*/(?:\r?\n)?", b"", source,
                    flags=re.S)
    source = re.sub(rb"/\*@.*?@\*/(?:\r?\n)?", b"", source, flags=re.S)
    return re.sub(rb"(?m)^[ \t]*//@[^\r\n]*(?:\r?\n|$)", b"", source)


def candidate(base_verified: bytes, base_original: bytes,
              owner_post_completion: bool = False,
              owner_safety_proof: bool = False,
              safety_proof_variant: str = "positive",
              owner_literal: bool = False,
              annotate_nested_drop: bool = False) -> bytes:
    verified = base_verified
    require(not (owner_post_completion and owner_safety_proof),
            "completion and stock safety proof are separate experiments")
    require(safety_proof_variant == "positive" or owner_safety_proof,
            "a safety negative requires the stock safety proof lane")
    require(safety_proof_variant in SAFETY_PROOFS,
            "unknown safety proof variant")
    normal_posts = (
        b"\n    (if condition { true_val as pointer } else { false_val as pointer });",
        b"\n        (if condition { true_val as pointer } else { false_val as pointer });",
    )
    matches = [post for post in normal_posts if verified.count(post) == 1]
    require(len(matches) == 1 and
            sum(verified.count(post) for post in normal_posts) == 1,
            "normal pointer post changed or ambiguous")
    normal_post = matches[0]
    if not owner_post_completion:
        # Historical O16 diagnostic: this stronger implementation post is
        # rejected by the generic std prototype before any body proof.
        after = normal_post[:-1] + b" &*& raw_ptr_own::<Element>()(t, result);"
        verified = verified.replace(normal_post, after, 1)
    if owner_safety_proof:
        anchors = [anchor for anchor in (SAFETY_ANCHOR,
                                       S6_LINKED_SAFETY_ANCHOR)
                   if verified.count(anchor) == 1]
        require(len(anchors) == 1,
                "actual contract/safety proof insertion anchor changed")
        proof = SAFETY_PROOFS[safety_proof_variant]
        require(proof.count(b"call();") == 1 and
                b"assume(" not in proof and b"assume_correct" not in proof and
                proof.count(b"safety_proof {") == 1,
                "safety proof changed its single-call/trust boundary")
        verified = verified.replace(
            anchors[0],
            anchors[0][:-2] + proof + b"{\n",
            1)
    if annotate_nested_drop:
        require(verified.count(NESTED_DROP_CALL) == 1,
                "actual nested Drop unsafe call anchor changed")
        verified = verified.replace(
            NESTED_DROP_CALL, NESTED_DROP_GHOST + NESTED_DROP_CALL, 1)
    require(CLOSE_OWNER_LITERAL.count(
        b"select_unpredictable::DropOnPanic::<*Element> { inner: guard }") == 2,
        "owner logical aggregate must occur in both branches exactly")
    for anchor, ghost in INSERTIONS:
        if owner_literal and anchor == b"        let guard = DropOnPanic { inner: guard };\n":
            ghost = CLOSE_OWNER_LITERAL
        require(verified.count(anchor) == 1,
                f"actual owner insertion anchor ambiguous: {anchor.decode()}")
        verified = verified.replace(anchor, anchor + ghost, 1)
    require(verified.endswith(b"}\n") and verified.count(OWNER_PRED) == 0,
            "actual helper final source boundary changed")
    verified += OWNER_PRED
    require(strip_ghost(verified) == base_original,
            "ghost projection changed actual runtime bytes")
    require(verified.count(b"crate::mem::forget(guard);") == 1 and
            verified.count(b"unsafe { self.inner.drop_in_place() }") == 1 and
            verified.count(b"crate::intrinsics::select_unpredictable(") == 3,
            "actual call/destructor inventory changed")
    require(verified.count(b"safety_proof {") == int(owner_safety_proof),
            "actual safety proof admission inventory changed")
    require(verified.count(NESTED_DROP_GHOST) == int(annotate_nested_drop),
            "actual nested Drop ghost inventory changed")
    return verified


def write_case(repo: Path, out: Path,
               owner_post_completion: bool = False,
               owner_safety_proof: bool = False,
               safety_proof_variant: str = "positive",
               owner_literal: bool = False,
               annotate_nested_drop: bool = False) -> dict:
    require(os.environ.get("GITHUB_ACTIONS") == "true" and
            os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted" and
            os.environ.get("RUNNER_OS") == "Linux",
            "actual owner fixture requires GitHub-hosted Linux")
    require(not out.exists(), f"refusing to overwrite {out}")
    base = out / "baseline"
    base_record = ACTUAL.write_fixture(repo, base)
    base_verified = (base / "verified/lib.rs").read_bytes()
    base_original = (base / "original/lib.rs").read_bytes()
    verified = candidate(base_verified, base_original,
                         owner_post_completion=owner_post_completion,
                         owner_safety_proof=owner_safety_proof,
                         safety_proof_variant=safety_proof_variant,
                         owner_literal=owner_literal,
                         annotate_nested_drop=annotate_nested_drop)
    case = out / "owner-projection"
    (case / "original").mkdir(parents=True)
    (case / "verified").mkdir()
    (case / "original/lib.rs").write_bytes(base_original)
    (case / "verified/lib.rs").write_bytes(verified)
    record = {
        "classification": "SOURCE_AND_MIR_CAPTURE_ONLY",
        "actual_helper_proved": False,
        "actual_nested_drop_proved": False,
        "actual_safe_forget_linked": False,
        "owner_post_completion": owner_post_completion,
        "owner_safety_proof": owner_safety_proof,
        "safety_proof_variant": safety_proof_variant,
        "owner_literal": owner_literal,
        "safety_proof_source": (SAFETY_PROOFS[safety_proof_variant].decode()
                                if owner_safety_proof else None),
        "actual_nested_drop_annotated": annotate_nested_drop,
        "nested_drop_ghost_source": (NESTED_DROP_GHOST.decode()
                                     if annotate_nested_drop else None),
        "actual_nested_drop_proved": False,
        "actual_normal_post": "prototype-compatible thread plus exact full selected pointer",
        "full_pointer_value_post_status": (
            "requires separately checked completion lemma; no actual helper proof"
            if owner_post_completion else
            "full post retained; stock safety_proof must pass"
            if owner_safety_proof else "O16 prototype-incompatible diagnostic"),
        "target_specialization": "T = *const Element; Element unrestricted",
        "source_certificate": base_record["source_certificate"],
        "original_sha256": ACTUAL.digest(base_original),
        "verified_sha256": ACTUAL.digest(verified),
        "baseline_original_sha256": base_record["original_sha256"],
        "ghost_strip_identity": True,
        "qualified_nominal_owner": OWNER_PRED.decode(),
        "ordered_ghost_blocks": [
            OPEN_WRAPPERS.decode(),
            (CLOSE_OWNER_LITERAL if owner_literal
             else CLOSE_OWNER).decode(),
            CLOSE_UNSELECTED.decode(), OPEN_OWNER.decode(),
            CLOSE_SELECTED.decode()],
        "expected_call_inventory": {
            "pointer_select": 2, "wrapper_select": 1,
            "pointer_drop": 1, "safe_forget": 1, "assume_init": 1},
    }
    (case / "fixture.json").write_text(json.dumps(record, indent=2,
                                                  sort_keys=True) + "\n")
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--owner-post-completion", action="store_true",
                        help="keep prototype-compatible post; require separate checked lemma")
    parser.add_argument("--owner-safety-proof", action="store_true",
                        help="full post with stock proof of safe prototype compatibility")
    parser.add_argument("--safety-proof-variant", choices=tuple(SAFETY_PROOFS),
                        default="positive")
    parser.add_argument("--annotate-nested-drop", action="store_true",
                        help="insert two truthful ghost opens in exact nested Drop")
    args = parser.parse_args()
    print(json.dumps(write_case(args.repo, args.out,
                                owner_post_completion=args.owner_post_completion,
                                owner_safety_proof=args.owner_safety_proof,
                                safety_proof_variant=args.safety_proof_variant,
                                annotate_nested_drop=args.annotate_nested_drop),
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
