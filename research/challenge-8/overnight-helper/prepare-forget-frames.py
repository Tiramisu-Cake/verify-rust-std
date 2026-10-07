#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Generate isolated source-linked generic-forget/frame proof cases.

This is fixture preparation, never a proof classifier. The hosted runner must
check NORMAL/readonly MIR, refinement, full VeriFast and the named negatives.
Do not run this on the editing server; it is intended for GitHub-hosted jobs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path


SOURCE_SHA = {
    "library/core/src/mem/mod.rs":
        "b86a596a58dcb21a45e8b29b33327ca8c7bde708aa6fca158d4366e51403daf2",
    "library/core/src/mem/manually_drop.rs":
        "f9cce798828cc852c00feeea9a6218c225b68d92727a5edbddc7c08a731a4f25",
}
FORGET_SIGNATURE = b"pub const fn forget<T>(t: T)"
FORGET_BODY = b"{\n    let _ = ManuallyDrop::new(t);\n}"
MD_SIGNATURE = b"pub const fn new(value: T) -> ManuallyDrop<T>"
MD_BODY = b"{\n        ManuallyDrop { value }\n    }"
POSITIVES = ("symbolic_frame", "two_frames")
NEGATIVES = (
    "false_post", "assert_false", "frame_loss", "frame_duplication",
    "frame_wrong_value", "cell_loss", "cell_duplication",
    "cell_wrong_value", "thread_loss", "thread_duplication",
    "no_cell", "no_thread", "contradictory_pre",
)
VARIANTS = POSITIVES + NEGATIVES


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError(reason)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extract_braced_item(source: bytes, signature: bytes) -> bytes:
    require(source.count(signature) == 1,
            f"source item is absent or ambiguous: {signature.decode()}")
    at = source.index(signature) + len(signature)
    opening = source.find(b"{", at)
    require(opening >= 0, "source item body is absent")
    depth = 0
    for cursor in range(opening, len(source)):
        if source[cursor] == ord("{"):
            depth += 1
        elif source[cursor] == ord("}"):
            depth -= 1
            if depth == 0:
                return source[opening:cursor + 1]
    raise ValueError("source item body is unterminated")


def source_certificate(repo: Path) -> dict:
    values = {}
    for relative, expected in SOURCE_SHA.items():
        value = (repo / relative).read_bytes()
        require(digest(value) == expected,
                f"pinned std source changed: {relative}")
        values[relative] = value
    forget = extract_braced_item(values["library/core/src/mem/mod.rs"],
                                 FORGET_SIGNATURE)
    md = extract_braced_item(values["library/core/src/mem/manually_drop.rs"],
                             MD_SIGNATURE)
    require(forget == FORGET_BODY, "exact forget body changed")
    require(md == MD_BODY, "direct-field ManuallyDrop::new changed")
    return {
        "source_sha256": SOURCE_SHA,
        "forget_signature": FORGET_SIGNATURE.decode(),
        "forget_body_sha256": digest(forget),
        "manually_drop_new_body_sha256": digest(md),
        "source_exact": True,
        "tool_profile": "VF26.10 plus independently accepted CFG/S6 components",
        "proof_status": "NOT_RUN",
        "trusted_boundary": "ManuallyDrop identity and destructor suppression",
        "actual_call_redirect": False,
    }


def ghost(clauses: bytes) -> bytes:
    lines = clauses.splitlines()
    require(len(lines) == 3 and
            lines[0].startswith(b"req ") and
            lines[1].startswith(b"ens ") and
            lines[2].startswith(b"on_unwind_ens ") and
            all(line.endswith(b";") for line in lines),
            "contract must have separate complete req/ens/unwind clauses")
    return b"".join(b"/*@\n" + line + b"\n@*/\n" for line in lines)


def strip_ghost(data: bytes) -> bytes:
    data = re.sub(rb"/\*@.*?@\*/(?:\r?\n)?", b"", data, flags=re.S)
    return re.sub(rb"(?m)^[ \t]*//@[^\r\n]*(?:\r?\n|$)", b"", data)


def helper(variant: str, annotated: bool) -> bytes:
    post = b"thread_token(tid)"
    if variant == "thread_loss":
        post = b"true"
    elif variant == "thread_duplication":
        post += b" &*& thread_token(tid)"
    contract = ghost(b"req thread_token(?tid) &*& tid == currentThread;\n"
                     b"ens " + post + b";\non_unwind_ens false;")
    if not annotated:
        contract = strip_ghost(contract)
    return (b"unsafe fn checked_forget_generic<T>(t: T)\n" + contract +
            FORGET_BODY + b"\n")


def probe(variant: str, annotated: bool) -> bytes:
    two = variant == "two_frames"
    pre = b"thread_token(?tid) &*& tid == currentThread"
    if variant == "no_thread":
        pre = b"true"
    if variant == "contradictory_pre":
        pre += b" &*& false"
    if variant != "no_cell":
        pre += b" &*& *slot |-> ?value"
    pre += b" &*& *frame |-> ?flag"
    if two:
        pre += b" &*& *frame2 |-> ?flag2"

    post = b"thread_token(tid) &*& *slot |-> value &*& *frame |-> flag"
    if variant == "no_cell":
        post = b"thread_token(tid) &*& *slot |-> _ &*& *frame |-> flag"
    if variant == "no_thread":
        post = b"thread_token(?restored) &*& *slot |-> value &*& *frame |-> flag"
    if two:
        post += b" &*& *frame2 |-> flag2"
    if variant == "false_post":
        post += b" &*& false"
    elif variant == "frame_loss":
        post = b"thread_token(tid) &*& *slot |-> value"
    elif variant == "frame_duplication":
        post += b" &*& *frame |-> flag"
    elif variant == "frame_wrong_value":
        post = (b"thread_token(tid) &*& *slot |-> value &*& "
                b"*frame |-> ?changed &*& changed != flag")
    elif variant == "cell_loss":
        post = b"thread_token(tid) &*& *frame |-> flag"
    elif variant == "cell_duplication":
        post += b" &*& *slot |-> value"
    elif variant == "cell_wrong_value":
        post = (b"thread_token(tid) &*& *slot |-> ?changed &*& "
                b"changed != value &*& *frame |-> flag")

    contract = ghost(b"req " + pre + b";\nens " + post +
                     b";\non_unwind_ens false;")
    if not annotated:
        contract = strip_ghost(contract)
    # The two positive frame obligations use the exact forget runtime body
    # in this function.  Calling the separate checked helper would leave a
    # synthetic `unwind=continue` successor which VeriFast's mandatory
    # dead-code gate rejects even when its false-unwind contract is proved.
    # The call linkage is a distinct, still-open obligation.
    if variant in POSITIVES:
        body = FORGET_BODY + b"\n"
    else:
        body = b"{\n    unsafe { checked_forget_generic(t); }\n"
        if variant == "assert_false" and annotated:
            body += b"    //@ assert false;\n"
        body += b"}\n"
    extra = b", frame2: *mut bool" if two else b""
    # Public entry permits an external caller to rely on this proved contract.
    return (b"pub unsafe fn checked_forget_frame_probe<T, Element>(\n"
            b"    t: T, slot: *mut *const Element, frame: *mut bool" + extra +
            b"\n)\n" + contract + body)


def fixture(variant: str) -> tuple[bytes, bytes, dict]:
    require(variant in VARIANTS, "unknown forget/frame variant")
    header = b"use std::mem::ManuallyDrop;\n\n"
    if variant in POSITIVES:
        # Keep the independently proved generic callee in the negative/call
        # fixtures.  An uncalled private callee here would itself be rejected
        # by the mandatory dead-code gate.
        verified = header + probe(variant, True)
        original = header + probe(variant, False)
    else:
        verified = header + helper(variant, True) + b"\n" + probe(variant, True)
        original = header + helper(variant, False) + b"\n" + probe(variant, False)
    require(strip_ghost(verified) == original,
            "ghost stripping changed runtime fixture")
    body_count = 1
    call_count = 0 if variant in POSITIVES else 1
    require(original.count(FORGET_BODY) == body_count and
            original.count(b"checked_forget_generic(t)") == call_count,
            "exact generic forget body/call inventory changed")
    return original, verified, {
        "variant": variant,
        "expected": "full verifier PASS" if variant in POSITIVES
                    else "named proof/leak/dead-code negative",
        "expected_failure": {
            "false_post": "probe postcondition false",
            "assert_false": "probe body assertion false",
            "frame_loss": "probe leak of frame",
            "frame_duplication": "probe postcondition duplicate frame",
            "frame_wrong_value": "probe postcondition changed frame value",
            "cell_loss": "probe leak of initialized slot",
            "cell_duplication": "probe postcondition duplicate slot",
            "cell_wrong_value": "probe postcondition changed slot pointer",
            "thread_loss": "helper leak of thread token",
            "thread_duplication": "helper postcondition duplicate token",
            "no_cell": "probe postcondition missing initialized slot",
            "no_thread": "probe call precondition missing thread token",
            "contradictory_pre": "mandatory dead-code gate",
        }.get(variant),
        "normal_post_preserves": ["thread", "initialized pointer slot", "frame"],
        "unwind_post": "false",
        "generic_argument": "unrestricted sized T",
        "element_rights": False,
        "actual_call_redirect": False,
        "positive_is_direct_body_frame_proof": variant in POSITIVES,
        "separate_call_linkage_proved": False,
        "original_sha256": digest(original),
        "verified_sha256": digest(verified),
        "ghost_strip_identity": True,
    }


def write_case(repo: Path, out: Path, variant: str) -> dict:
    source = source_certificate(repo)
    original, verified, case = fixture(variant)
    require(not out.exists(), f"refusing to overwrite {out}")
    (out / "original").mkdir(parents=True)
    (out / "verified").mkdir()
    (out / "original/lib.rs").write_bytes(original)
    (out / "verified/lib.rs").write_bytes(verified)
    record = {"source_certificate": source, **case}
    (out / "fixture.json").write_text(json.dumps(record, indent=2,
                                                  sort_keys=True) + "\n")
    return record


def main() -> None:
    require(os.environ.get("GITHUB_ACTIONS") == "true" and
            os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted",
            "fixture generation is permitted only on GitHub-hosted Actions")
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--variant", choices=VARIANTS, required=True)
    args = parser.parse_args()
    print(json.dumps(write_case(args.repo, args.out, args.variant),
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
