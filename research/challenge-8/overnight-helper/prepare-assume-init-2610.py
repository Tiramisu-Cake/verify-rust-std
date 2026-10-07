#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Pointer-only updated assume_init fixture and fail-closed MIR capture gate.

Run only on a GitHub-hosted Actions runner. `prepare` produces source pairs;
`capture` records a complete decoded MIR body for independent review; `check`
requires a separately reviewed manifest and rejects every byte difference.
Capture is never proof acceptance or a semantic transmute rule.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path


SOURCE_SHA = {
    "library/core/src/mem/maybe_uninit.rs":
        "1230d267542337ee2842c29d8227cf8a58fe75c53a2a70efaee3922c4e8e25c0",
    "library/core/src/mem/manually_drop.rs":
        "f9cce798828cc852c00feeea9a6218c225b68d92727a5edbddc7c08a731a4f25",
    "library/core/src/mem/mod.rs":
        "b86a596a58dcb21a45e8b29b33327ca8c7bde708aa6fca158d4366e51403daf2",
    "library/core/src/intrinsics/mod.rs":
        "de4a6d2afbd1d9f725222c1f4d95a107b8202586b952ce2a619a054c6f2f1865",
}
METHOD_SIGNATURE = b"pub const unsafe fn assume_init(self) -> T"
TRANSMUTE_SIGNATURE = b"pub const unsafe fn transmute_neo<Src, Dst>(src: Src) -> Dst"
UNION_SIGNATURE = b"pub union MaybeUninit<T>"
MD_SIGNATURE = b"pub struct ManuallyDrop<T: ?Sized>"
METHOD_BODY = (
    b"{\n        // SAFETY: the caller must guarantee that `self` is initialized.\n"
    b"        // This also means that `self` must be a `value` variant.\n"
    b"        unsafe {\n"
    b"            intrinsics::assert_inhabited::<T>();\n"
    b"            // We do this via a transmute instead of `ManuallyDrop::into_inner` so that there's\n"
    b"            // no trace of `ManuallyDrop` in Miri's error messages here.\n"
    b"            transmute_neo(self)\n"
    b"        }\n    }"
)
TRANSMUTE_BODY = (
    b"{\n    const { assert!(Src::SIZE == Dst::SIZE) };\n\n"
    b"    // SAFETY: the const-assert just checked that they're the same size,\n"
    b"    // and any other safety invariants need to be upheld by the caller.\n"
    b"    unsafe { intrinsics::transmute_unchecked(src) }\n}"
)
UNION_BODY = b"{\n    uninit: (),\n    value: ManuallyDrop<T>,\n}"
MD_BODY = b"{\n    value: T,\n}"
ASSERT_INTRINSIC = b"pub const fn assert_inhabited<T>();"
TRANSMUTE_INTRINSIC = (
    b"pub const unsafe fn transmute_unchecked<Src, Dst>(src: Src) -> Dst;"
)
ADAPTER_NAME = "checked_assume_init_pointer"
TRANSMUTE_ADAPTER_NAME = "checked_transmute_neo_pointer"
POSITIVES = ("initialized", "initialized_frame")
NEGATIVES = (
    "none", "unknown", "false_post", "assert_false", "wrong_result",
    "frame_loss", "frame_duplication", "frame_wrong_value",
    "thread_loss", "thread_duplication", "no_thread",
)
VARIANTS = POSITIVES + NEGATIVES
MIR_REQUIRED_NAMES = (
    "assert_inhabited", "transmute_neo", "transmute_unchecked",
)


def require(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extract_braced_item(source: bytes, signature: bytes) -> bytes:
    require(source.count(signature) == 1,
            f"source signature absent/ambiguous: {signature.decode()}")
    opening = source.find(b"{", source.index(signature) + len(signature))
    require(opening >= 0, "source body opening is absent")
    depth = 0
    for at in range(opening, len(source)):
        if source[at] == ord("{"):
            depth += 1
        elif source[at] == ord("}"):
            depth -= 1
            if depth == 0:
                return source[opening:at + 1]
    raise ValueError("source body is unterminated")


def certify_source(repo: Path) -> tuple[bytes, dict]:
    values = {}
    for relative, expected in SOURCE_SHA.items():
        value = (repo / relative).read_bytes()
        require(digest(value) == expected,
                f"source pin mismatch: {relative}")
        values[relative] = value
    mu = values["library/core/src/mem/maybe_uninit.rs"]
    md = values["library/core/src/mem/manually_drop.rs"]
    mem = values["library/core/src/mem/mod.rs"]
    intrinsics = values["library/core/src/intrinsics/mod.rs"]
    method = extract_braced_item(mu, METHOD_SIGNATURE)
    transmute = extract_braced_item(mem, TRANSMUTE_SIGNATURE)
    union = extract_braced_item(mu, UNION_SIGNATURE)
    manually_drop = extract_braced_item(md, MD_SIGNATURE)
    require(method == METHOD_BODY, "updated assume_init body changed")
    require(transmute == TRANSMUTE_BODY, "transmute_neo body changed")
    require(union == UNION_BODY and manually_drop == MD_BODY,
            "MaybeUninit/ManuallyDrop representation changed")
    require(b"#[rustc_pub_transparent]\n" + UNION_SIGNATURE in mu and
            b"#[repr(transparent)]\n#[rustc_pub_transparent]\n" + MD_SIGNATURE in md,
            "representation attributes changed")
    require(intrinsics.count(ASSERT_INTRINSIC) == 1 and
            intrinsics.count(TRANSMUTE_INTRINSIC) == 1,
            "compiler intrinsic signatures changed")
    for signature in (ASSERT_INTRINSIC, TRANSMUTE_INTRINSIC):
        at = intrinsics.index(signature)
        require(b"#[rustc_nounwind]" in intrinsics[max(0, at - 200):at],
                f"noundwind attribute absent for {signature.decode()}")
    specialized = method.replace(b"::<T>", b"::<*const Element>")
    specialized = specialized.replace(b"transmute_neo(self)",
                                      b"transmute_neo(storage)")
    require(specialized.count(b"assert_inhabited::<*const Element>()") == 1
            and specialized.count(b"transmute_neo(storage)") == 1,
            "typed adapter substitutions changed")
    return specialized, {
        "source_sha256": SOURCE_SHA,
        "method_body_sha256": digest(method),
        "transmute_neo_body_sha256": digest(transmute),
        "union_body_sha256": digest(union),
        "manually_drop_body_sha256": digest(manually_drop),
        "adapter_body_sha256": digest(specialized),
        "compiler_intrinsics": [s.decode() for s in
                                (ASSERT_INTRINSIC, TRANSMUTE_INTRINSIC)],
        "substitutions": ["T -> *const Element", "self -> storage"],
        "representation": "MaybeUninit union value: ManuallyDrop<T>; ManuallyDrop direct value:T",
        "pointer_payload_only": True,
        "element_pointee_rights": False,
        "compiler_correspondence_trusted": True,
        "full_mir_graph_reviewed": False,
        "proof_status": "NOT_RUN",
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


def fixture_source(body: bytes, variant: str) -> tuple[bytes, bytes, dict]:
    require(variant in VARIANTS, "unknown assume_init variant")
    header = (b"#![feature(core_intrinsics, transmute_neo)]\n"
              b"#![allow(internal_features)]\n\n"
              b"use std::intrinsics;\n"
              b"use std::mem::{MaybeUninit, transmute_neo};\n\n")
    adapter_pre = (
        b"thread_token(?tid) &*& tid == currentThread &*& "
        b"std::mem::MaybeUninit::inner(storage) == some(?p) &*& "
        b"std::mem::MaybeUninit_pointer_own::<Element>()(tid, storage)"
    )
    adapter_post = (
        b"thread_token(tid) &*& result == p &*& "
        b"raw_ptr_own::<Element>()(tid, result)"
    )
    adapter_contract = ghost(b"req " + adapter_pre + b";\n"
                             b"ens " + adapter_post +
                             b";\non_unwind_ens false;")
    adapter = (b"pub unsafe fn " + ADAPTER_NAME.encode() +
               b"<Element>(storage: MaybeUninit<*const Element>) -> *const Element\n" +
               adapter_contract + body + b"\n")
    pre = b"thread_token(?tid) &*& tid == currentThread"
    if variant == "no_thread":
        pre = b"true"
    if variant == "none":
        pre += b" &*& std::mem::MaybeUninit::inner(storage) == none"
    elif variant != "unknown":
        pre += b" &*& std::mem::MaybeUninit::inner(storage) == some(?p)"
    own_tid = b"currentThread" if variant == "no_thread" else b"tid"
    pre += (b" &*& std::mem::MaybeUninit_pointer_own::<Element>()(" +
            own_tid + b", storage)")
    pre += b" &*& *frame |-> ?flag"
    post = b"thread_token(tid) &*& result == p &*& *frame |-> flag"
    if variant in {"none", "unknown"}:
        post = b"thread_token(tid) &*& *frame |-> flag"
    if variant == "no_thread":
        post = b"thread_token(?restored) &*& result == p &*& *frame |-> flag"
    if variant == "false_post":
        post += b" &*& false"
    elif variant == "wrong_result":
        post = b"thread_token(tid) &*& result != p &*& *frame |-> flag"
    elif variant == "frame_loss":
        post = b"thread_token(tid) &*& result == p"
    elif variant == "frame_duplication":
        post += b" &*& *frame |-> flag"
    elif variant == "frame_wrong_value":
        post = (b"thread_token(tid) &*& result == p &*& "
                b"*frame |-> ?changed &*& changed != flag")
    elif variant == "thread_loss":
        post = b"result == p &*& *frame |-> flag"
    elif variant == "thread_duplication":
        post += b" &*& thread_token(tid)"
    probe_contract = ghost(b"req " + pre + b";\nens " + post +
                           b";\non_unwind_ens false;")
    probe_body = b"{\n    let result = unsafe { " + ADAPTER_NAME.encode() + b"(storage) };\n"
    if variant == "assert_false":
        probe_body += b"    //@ assert false;\n"
    probe_body += b"    result\n}\n"
    probe = (b"pub unsafe fn assume_init_probe<Element>(storage: MaybeUninit<*const Element>, "
             b"frame: *mut bool) -> *const Element\n" + probe_contract + probe_body)
    verified = header + adapter + b"\n" + probe
    original = strip_ghost(verified)
    require(original.count(body) == 1 and
            original.count(ADAPTER_NAME.encode() + b"(storage)") == 1,
            "adapter body/call absent or ambiguous")
    return original, verified, {
        "variant": variant,
        "expected": "capture then full proof" if variant in POSITIVES
                    else "capture then intended proof negative",
        "expected_failure": {
            "none": "initialized wrapper requirement at adapter call",
            "unknown": "initialized wrapper requirement at adapter call",
            "false_post": "probe postcondition false",
            "assert_false": "probe assertion false",
            "wrong_result": "probe result equality",
            "frame_loss": "probe frame leak",
            "frame_duplication": "probe duplicate frame postcondition",
            "frame_wrong_value": "probe changed frame value",
            "thread_loss": "probe thread-token leak",
            "thread_duplication": "probe duplicate thread-token postcondition",
            "no_thread": "adapter thread-token precondition",
        }.get(variant),
        "actual_method_adapter": True,
        "actual_method_called": False,
        "full_mir_graph_reviewed": False,
        "primitive_rule_accepted": False,
        "original_sha256": digest(original),
        "verified_sha256": digest(verified),
        "ghost_strip_identity": True,
    }


def transmute_fixture_source(repo: Path) -> tuple[bytes, bytes, dict]:
    # This is an independent exact body copy. The assume_init adapter continues
    # calling the real public transmute_neo; no call is redirected here.
    _, source = certify_source(repo)
    mem = (repo / "library/core/src/mem/mod.rs").read_bytes()
    body = extract_braced_item(mem, TRANSMUTE_SIGNATURE)
    require(body == TRANSMUTE_BODY, "transmute_neo body no longer pinned")
    specialized = body.replace(
        b"Src::SIZE",
        b"<MaybeUninit<*const Element> as SizedTypeProperties>::SIZE"
    ).replace(
        b"Dst::SIZE",
        b"<*const Element as SizedTypeProperties>::SIZE"
    )
    require(specialized.count(b"transmute_unchecked(src)") == 1 and
            specialized.count(b"SizedTypeProperties>::SIZE") == 2,
            "transmute source specialization changed")
    header = (
        b"#![feature(core_intrinsics, sized_type_properties)]\n"
        b"#![allow(internal_features)]\n\n"
        b"use std::intrinsics;\n"
        b"use std::mem::{MaybeUninit, SizedTypeProperties};\n\n"
    )
    signature = (
        b"pub unsafe fn " + TRANSMUTE_ADAPTER_NAME.encode() +
        b"<Element>(src: MaybeUninit<*const Element>) -> *const Element\n"
    )
    contract = ghost(
        b"req thread_token(?tid) &*& tid == currentThread &*& "
        b"std::mem::MaybeUninit::inner(src) == some(?p) &*& "
        b"std::mem::MaybeUninit_pointer_own::<Element>()(tid, src);\n"
        b"ens thread_token(tid) &*& result == p &*& "
        b"raw_ptr_own::<Element>()(tid, result);\n"
        b"on_unwind_ens false;"
    )
    verified = header + signature + contract + specialized + b"\n"
    original = strip_ghost(verified)
    require(original.count(specialized) == 1,
            "local transmute body absent or ambiguous")
    return original, verified, {
        "source_certificate": source,
        "target": "transmute_neo",
        "source_body_sha256": digest(body),
        "specialized_body_sha256": digest(specialized),
        "substitutions": [
            "Src::SIZE -> <MaybeUninit<*const Element> as SizedTypeProperties>::SIZE",
            "Dst::SIZE -> <*const Element as SizedTypeProperties>::SIZE",
        ],
        "compiler_intrinsic_body_proved": False,
        "primitive_rule_accepted": False,
        "original_sha256": digest(original),
        "verified_sha256": digest(verified),
        "ghost_strip_identity": True,
    }


def write_fixture(repo: Path, out: Path, variant: str) -> dict:
    body, source = certify_source(repo)
    original, verified, case = fixture_source(body, variant)
    require(not out.exists(), f"refusing to overwrite {out}")
    (out / "original").mkdir(parents=True)
    (out / "verified").mkdir()
    (out / "original/lib.rs").write_bytes(original)
    (out / "verified/lib.rs").write_bytes(verified)
    record = {"source_certificate": source, **case}
    (out / "fixture.json").write_text(json.dumps(record, indent=2,
                                                  sort_keys=True) + "\n")
    return record


def write_transmute_fixture(repo: Path, out: Path) -> dict:
    original, verified, record = transmute_fixture_source(repo)
    require(not out.exists(), f"refusing to overwrite {out}")
    (out / "original").mkdir(parents=True)
    (out / "verified").mkdir()
    (out / "original/lib.rs").write_bytes(original)
    (out / "verified/lib.rs").write_bytes(verified)
    (out / "fixture.json").write_text(json.dumps(record, indent=2,
                                                  sort_keys=True) + "\n")
    return record


def balanced_record(decoded: str, opening: int) -> str:
    require(decoded[opening] == "(", "MIR record opening missing")
    depth = 0
    in_string = False
    escaped = False
    for at in range(opening, len(decoded)):
        ch = decoded[at]
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
        elif ch == '"':
            in_string = True
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return decoded[opening:at + 1]
    raise ValueError("MIR record is unterminated")


def complete_function_record(decoded: str, basename: str) -> tuple[str, str]:
    # Inspect the *complete* serialized function record; no block is omitted.
    matches = [match for match in re.finditer(r'defPath = "([^"]+)"', decoded)
               if match.group(1) == basename or
               match.group(1).endswith("::" + basename)]
    require(len(matches) == 1,
            f"MIR function identity absent/ambiguous: {basename}")
    match = matches[0]
    lead = decoded.rfind("    ( defKind =", 0, match.start())
    require(lead >= 0, "MIR function record opening missing")
    opening = decoded.index("(", lead)
    body = balanced_record(decoded, opening)
    require(match.group(0) in body and "basicBlocks = [" in body and
            "localDecls = [" in body and "inputs = [" in body,
            "MIR function record is incomplete")
    return match.group(1), body


def capture_mir(decoded_path: Path, out: Path, target: str = "method") -> dict:
    decoded = decoded_path.read_text(errors="strict")
    name = ADAPTER_NAME if target == "method" else TRANSMUTE_ADAPTER_NAME
    defpath, body = complete_function_record(decoded, name)
    require(not out.exists(), f"refusing to overwrite {out}")
    out.mkdir(parents=True)
    (out / "adapter-full-mir.txt").write_text(body)
    record = {
        "classification": "UNREVIEWED_CAPTURE; NOT A CERTIFICATE",
        "target": target,
        "adapter_defpath": defpath,
        "adapter_full_mir_sha256": digest(body.encode()),
        "adapter_full_mir_bytes": len(body.encode()),
        "required_name_inventory": {name: decoded.count(name)
                                    for name in MIR_REQUIRED_NAMES},
        "capture_source_sha256": digest(decoded.encode()),
        "full_mir_graph_reviewed": False,
        "primitive_rule_accepted": False,
    }
    (out / "capture.json").write_text(json.dumps(record, indent=2,
                                                sort_keys=True) + "\n")
    return record


def check_mir(decoded_path: Path, manifest_path: Path, repo: Path) -> dict:
    _, source = certify_source(repo)
    manifest = json.loads(manifest_path.read_text())
    require(manifest.get("reviewed") is True and
            manifest.get("reviewed_by") and
            manifest.get("source_sha256") == source["source_sha256"] and
            manifest.get("typed_pointer_only") is True,
            "reviewed applicability manifest is incomplete")
    decoded = decoded_path.read_text(errors="strict")
    defpath, body = complete_function_record(decoded, ADAPTER_NAME)
    require(defpath == manifest.get("adapter_defpath") and
            digest(body.encode()) == manifest.get("adapter_full_mir_sha256"),
            "complete adapter typed MIR differs from reviewed manifest")
    require(manifest.get("expected_calls") == ["assert_inhabited", "transmute_neo"] and
            all(body.count(name) == 1 for name in manifest["expected_calls"]),
            "adapter call inventory differs")
    require("transmute_unchecked" not in body,
            "adapter MIR unexpectedly inlined compiler transmute")
    return {
        "classification": "FULL_MIR_APPLICABILITY_ONLY",
        "adapter_defpath": defpath,
        "adapter_full_mir_sha256": digest(body.encode()),
        "source_sha256": SOURCE_SHA,
        "full_graph_byte_identical_to_reviewed": True,
        "primitive_rule_accepted": False,
        "proof_status": "NOT_RUN",
    }


def main() -> None:
    require(os.environ.get("GITHUB_ACTIONS") == "true" and
            os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted",
            "fixture/certificate operations are permitted only on GitHub-hosted Actions")
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="mode", required=True)
    prepare = sub.add_parser("prepare")
    prepare.add_argument("--repo", type=Path, required=True)
    prepare.add_argument("--out", type=Path, required=True)
    prepare.add_argument("--variant", choices=VARIANTS, required=True)
    transmute = sub.add_parser("prepare-transmute")
    transmute.add_argument("--repo", type=Path, required=True)
    transmute.add_argument("--out", type=Path, required=True)
    capture = sub.add_parser("capture")
    capture.add_argument("--decoded-mir", type=Path, required=True)
    capture.add_argument("--out", type=Path, required=True)
    capture.add_argument("--target", choices=("method", "transmute"),
                         default="method")
    check = sub.add_parser("check")
    check.add_argument("--decoded-mir", type=Path, required=True)
    check.add_argument("--reviewed-manifest", type=Path, required=True)
    check.add_argument("--repo", type=Path, required=True)
    args = parser.parse_args()
    if args.mode == "prepare":
        record = write_fixture(args.repo, args.out, args.variant)
    elif args.mode == "prepare-transmute":
        record = write_transmute_fixture(args.repo, args.out)
    elif args.mode == "capture":
        record = capture_mir(args.decoded_mir, args.out, args.target)
    else:
        record = check_mir(args.decoded_mir, args.reviewed_manifest, args.repo)
    print(json.dumps(record, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
