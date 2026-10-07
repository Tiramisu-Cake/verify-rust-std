#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Source-pinned direct transmute_neo body proof and negative fixtures.

Fixture generation belongs on GitHub-hosted Actions only.  It does not
redirect the actual std call or classify proof results.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent


def load_a1():
    spec = importlib.util.spec_from_file_location(
        "overnight_a1_primitive_source", HERE / "prepare-assume-init-2610.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("A1 source certificate module missing")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


A1 = load_a1()
POSITIVES = ("symbolic", "frame")
NEGATIVES = (
    "none", "unknown", "false_post", "wrong_result", "frame_loss",
    "frame_duplication", "thread_loss", "thread_duplication",
    "no_thread", "element_rights",
)
VARIANTS = POSITIVES + NEGATIVES
TYPE_CONTROLS = ("wrong_source", "mutable_pointer_source",
                 "different_element", "box_source",
                 "wrong_destination")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def specialized_body(repo: Path) -> tuple[bytes, dict]:
    _, source = A1.certify_source(repo)
    raw = A1.extract_braced_item(
        (repo / "library/core/src/mem/mod.rs").read_bytes(),
        A1.TRANSMUTE_SIGNATURE)
    A1.require(raw == A1.TRANSMUTE_BODY, "transmute body source changed")
    body = raw.replace(
        b"Src::SIZE",
        b"<MaybeUninit<*const Element> as SizedTypeProperties>::SIZE"
    ).replace(
        b"Dst::SIZE", b"<*const Element as SizedTypeProperties>::SIZE"
    )
    A1.require(body.count(b"transmute_unchecked(src)") == 1 and
               body.count(b"SizedTypeProperties>::SIZE") == 2,
               "exact specialized body has changed")
    return body, source


def fixture_source(repo: Path, variant: str) -> tuple[bytes, bytes, dict]:
    A1.require(variant in VARIANTS, "unknown A1 primitive variant")
    body, source = specialized_body(repo)
    frame_case = variant in {"frame", "frame_loss", "frame_duplication",
                             "element_rights"}
    pre = b"thread_token(?tid) &*& tid == currentThread"
    if variant == "no_thread":
        pre = b"true"
    if variant == "none":
        pre += b" &*& std::mem::MaybeUninit::inner(src) == none"
    elif variant != "unknown":
        pre += b" &*& std::mem::MaybeUninit::inner(src) == some(?p)"
    own_tid = b"currentThread" if variant == "no_thread" else b"tid"
    pre += (b" &*& std::mem::MaybeUninit_pointer_own::<Element>()(" +
            own_tid + b", src)")
    if frame_case:
        pre += b" &*& *frame |-> ?flag"

    post = b"thread_token(tid) &*& result == p &*& raw_ptr_own::<Element>()(tid, result)"
    if variant in {"none", "unknown"}:
        post = b"thread_token(tid)"
    elif variant == "no_thread":
        post = b"thread_token(?restored) &*& result == p"
    if frame_case:
        post += b" &*& *frame |-> flag"
    if variant == "false_post":
        post += b" &*& false"
    elif variant == "wrong_result":
        post = (b"thread_token(tid) &*& result != p &*& "
                b"raw_ptr_own::<Element>()(tid, result)")
    elif variant == "frame_loss":
        post = (b"thread_token(tid) &*& result == p &*& "
                b"raw_ptr_own::<Element>()(tid, result)")
    elif variant == "frame_duplication":
        post += b" &*& *frame |-> flag"
    elif variant == "thread_loss":
        post = b"result == p &*& raw_ptr_own::<Element>()(tid, result)"
    elif variant == "thread_duplication":
        post += b" &*& thread_token(tid)"
    elif variant == "element_rights":
        post += b" &*& *result |-> _"

    signature = (
        b"pub unsafe fn checked_transmute_neo_pointer<Element>(\n"
        b"    src: MaybeUninit<*const Element>, frame: *mut bool\n"
        b") -> *const Element\n"
    )
    header = (
        b"#![feature(core_intrinsics, sized_type_properties)]\n"
        b"#![allow(internal_features)]\n\n"
        b"use std::intrinsics;\n"
        b"use std::mem::{MaybeUninit, SizedTypeProperties};\n\n"
    )
    contract = A1.ghost(b"req " + pre + b";\nens " + post +
                        b";\non_unwind_ens false;")
    verified = header + signature + contract + body + b"\n"
    original = A1.strip_ghost(verified)
    A1.require(original.count(body) == 1 and
               original.count(b"transmute_unchecked(src)") == 1 and
               A1.strip_ghost(verified) == original,
               "direct primitive runtime source changed")
    verified_lines = verified.splitlines()
    post_line = next(i for i, line in enumerate(verified_lines, 1)
                     if line.startswith(b"ens "))
    cast_line = next(i for i, line in enumerate(verified_lines, 1)
                     if b"intrinsics::transmute_unchecked(src)" in line)
    closing_line = len(verified_lines)
    expected = {
        "none": ("primitive initialized-inner precondition", cast_line),
        "unknown": ("primitive initialized-inner precondition", cast_line),
        "no_thread": ("primitive thread-token precondition", cast_line),
        "false_post": ("false postcondition", post_line),
        "wrong_result": ("complete pointer equality postcondition", post_line),
        "frame_loss": ("independent frame leak", closing_line),
        "frame_duplication": ("duplicate frame postcondition", post_line),
        "thread_loss": ("thread-token leak", closing_line),
        "thread_duplication": ("duplicate thread-token postcondition", post_line),
        "element_rights": ("missing Element points-to postcondition", post_line),
    }
    return original, verified, {
        "variant": variant,
        "source_certificate": source,
        "target": "exact local transmute_neo body",
        "normal_post": post.decode(),
        "unwind_post": "false",
        "actual_call_linkage": False,
        "element_pointee_rights_in_pre": False,
        "expected": "experimental positive" if variant in POSITIVES else
                    "named proof negative",
        "expected_stage": "full-verification",
        "expected_obligation": ({"predicate": expected[variant][0],
                                 "fixture_line": expected[variant][1],
                                 "file": "verified/lib.rs"}
                                if variant in NEGATIVES else None),
        "source_body_sha256": digest(body),
        "original_sha256": digest(original),
        "verified_sha256": digest(verified),
        "ghost_strip_identity": True,
    }


def write_case(repo: Path, out: Path, variant: str) -> dict:
    original, verified, record = fixture_source(repo, variant)
    A1.require(not out.exists(), f"refusing to overwrite {out}")
    (out / "original").mkdir(parents=True)
    (out / "verified").mkdir()
    (out / "original/lib.rs").write_bytes(original)
    (out / "verified/lib.rs").write_bytes(verified)
    (out / "fixture.json").write_text(json.dumps(record, indent=2,
                                                 sort_keys=True) + "\n")
    return record


def type_control_source(repo: Path, control: str) -> tuple[bytes, bytes, dict]:
    A1.require(control in TYPE_CONTROLS, "unknown A1 type control")
    _, source = A1.certify_source(repo)
    src, dst = {
        "wrong_source": (b"usize", b"*const Element"),
        "mutable_pointer_source": (b"MaybeUninit<*mut Element>",
                                   b"*const Element"),
        "different_element": (b"MaybeUninit<*const u8>",
                              b"*const Element"),
        "box_source": (b"Box<Element>", b"*const Element"),
        "wrong_destination": (b"MaybeUninit<*const Element>", b"usize"),
    }[control]
    raw = A1.extract_braced_item(
        (repo / "library/core/src/mem/mod.rs").read_bytes(),
        A1.TRANSMUTE_SIGNATURE)
    A1.require(raw == A1.TRANSMUTE_BODY, "source body changed")
    body = raw.replace(b"Src::SIZE", b"<" + src +
                       b" as SizedTypeProperties>::SIZE").replace(
        b"Dst::SIZE", b"<" + dst + b" as SizedTypeProperties>::SIZE")
    header = (
        b"#![feature(core_intrinsics, sized_type_properties)]\n"
        b"#![allow(internal_features)]\n\n"
        b"use std::intrinsics;\n"
        b"use std::mem::{MaybeUninit, SizedTypeProperties};\n\n"
    )
    signature = (b"pub unsafe fn checked_transmute_type_control<Element>(\n"
                 b"    src: " + src + b"\n) -> " + dst + b"\n")
    contract = A1.ghost(
        b"req thread_token(?tid) &*& tid == currentThread;\n"
        b"ens thread_token(tid);\n"
        b"on_unwind_ens false;"
    )
    verified = header + signature + contract + body + b"\n"
    original = A1.strip_ghost(verified)
    A1.require(original.count(body) == 1 and
               original.count(b"transmute_unchecked(src)") == 1,
               "type control body changed")
    cast_line = next(i for i, line in enumerate(verified.splitlines(), 1)
                     if b"intrinsics::transmute_unchecked(src)" in line)
    return original, verified, {
        "control": control,
        "classification": "SYNTHETIC_TYPE_CONTROL; NOT ACTUAL STD BODY PROOF",
        "source_certificate": source,
        "source_type": src.decode(),
        "destination_type": dst.decode(),
        "expected": "full verifier rejects at cast typecheck",
        "expected_stage": "full-verification",
        "expected_obligation": {
            "predicate": "typed source/destination rejection",
            "fixture_line": cast_line,
            "file": "verified/lib.rs",
        },
        "original_sha256": digest(original),
        "verified_sha256": digest(verified),
        "ghost_strip_identity": True,
    }


def write_type_control(repo: Path, out: Path, control: str) -> dict:
    original, verified, record = type_control_source(repo, control)
    A1.require(not out.exists(), f"refusing to overwrite {out}")
    (out / "original").mkdir(parents=True)
    (out / "verified").mkdir()
    (out / "original/lib.rs").write_bytes(original)
    (out / "verified/lib.rs").write_bytes(verified)
    (out / "fixture.json").write_text(json.dumps(record, indent=2,
                                                 sort_keys=True) + "\n")
    return record


def main() -> None:
    A1.require(os.environ.get("GITHUB_ACTIONS") == "true" and
               os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted",
               "A1 primitive fixtures require GitHub-hosted Actions")
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--variant", choices=VARIANTS)
    parser.add_argument("--type-control", choices=TYPE_CONTROLS)
    args = parser.parse_args()
    A1.require((args.variant is None) != (args.type_control is None),
               "choose exactly one variant or type control")
    record = (write_type_control(args.repo, args.out, args.type_control)
              if args.type_control else
              write_case(args.repo, args.out, args.variant))
    print(json.dumps(record,
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
