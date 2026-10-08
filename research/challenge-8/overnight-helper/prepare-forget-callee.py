#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Generate hosted-only single-public-callee source-exact forget fixtures."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
VARIANTS = ("positive", "false_post", "thread_loss",
            "thread_duplication", "contradictory_pre")


def load_g1():
    path = HERE / "prepare-forget-frames.py"
    spec = importlib.util.spec_from_file_location("overnight_g1c_source", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("G1 source preparer unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


G1 = load_g1()


def line_of(source: bytes, marker: bytes, *, exact: bool = False) -> int:
    matches = [line for line, text in enumerate(source.splitlines(), 1)
               if (text.strip() == marker if exact else marker in text)]
    G1.require(len(matches) == 1, "callee obligation marker ambiguous")
    return matches[0]


def fixture(variant: str) -> tuple[bytes, bytes, dict]:
    G1.require(variant in VARIANTS, "unknown G1c variant")
    pre = b"thread_token(?tid) &*& tid == currentThread"
    if variant == "contradictory_pre":
        pre += b" &*& false"
    post = b"thread_token(tid)"
    if variant == "false_post":
        post = b"false"
    elif variant == "thread_loss":
        post = b"true"
    elif variant == "thread_duplication":
        post += b" &*& thread_token(tid)"
    header = b"use std::mem::ManuallyDrop;\n\n"
    signature = b"pub unsafe fn checked_forget_generic<T>(t: T)\n"
    contract = G1.ghost(b"req " + pre + b";\nens " + post +
                        b";\non_unwind_ens false;")
    verified = header + signature + contract + G1.FORGET_BODY + b"\n"
    original = G1.strip_ghost(verified)
    G1.require(original == header + signature + G1.FORGET_BODY + b"\n" and
               verified.count(G1.FORGET_BODY) == 1 and
               original.count(b"checked_forget_generic<T>") == 1 and
               original.count(b"ManuallyDrop::new(t)") == 1,
               "single exact generic forget body changed")
    if variant == "positive":
        obligation = None
    elif variant == "false_post":
        obligation = {"line": line_of(verified, b"ens false;", exact=True),
                      "message": "Cannot prove false"}
    elif variant == "thread_loss":
        obligation = {"line": line_of(verified, b"}", exact=True),
                      "message": "Function leaks heap chunks: thread_token(tid)"}
    elif variant == "thread_duplication":
        obligation = {
            "line": line_of(verified,
                            b"ens thread_token(tid) &*& thread_token(tid);",
                            exact=True),
            "message": "No matching heap chunks: thread_token(tid)"}
    else:
        obligation = {"line": line_of(verified, signature.strip(), exact=True),
                      "message": "dead code"}
    return original, verified, {
        "variant": variant,
        "target": "independently callable generic unsafe forget body",
        "single_public_function": True,
        "runtime_body_exact_std_forget": True,
        "same_source_contract_as_safe_forget": False,
        "actual_safe_call_redirect": False,
        "expected_obligation": obligation,
        "original_sha256": G1.digest(original),
        "verified_sha256": G1.digest(verified),
        "ghost_strip_identity": True,
    }


def write_case(repo: Path, out: Path, variant: str) -> dict:
    G1.require(os.environ.get("GITHUB_ACTIONS") == "true" and
               os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted",
               "G1c case preparation requires GitHub-hosted Actions")
    certificate = G1.source_certificate(repo)
    original, verified, record = fixture(variant)
    G1.require(not out.exists(), f"refusing to overwrite {out}")
    (out / "original").mkdir(parents=True)
    (out / "verified").mkdir()
    (out / "original/lib.rs").write_bytes(original)
    (out / "verified/lib.rs").write_bytes(verified)
    record["source_certificate"] = certificate
    (out / "fixture.json").write_text(json.dumps(record, indent=2,
                                                  sort_keys=True) + "\n")
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--variant", choices=VARIANTS, required=True)
    args = parser.parse_args()
    print(json.dumps(write_case(args.repo, args.out, args.variant),
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
