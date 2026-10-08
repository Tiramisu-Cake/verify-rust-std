#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted-only exact-std-body fixtures for a stronger unsafe forget adapter."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
HELPER = HERE.parent / "overnight-helper" / "prepare-forget-frames.py"
VARIANTS = (
    "positive", "false_normal", "owner_duplicate", "owner_wrong_value",
    "thread_duplicate", "owner_loss", "contradictory_pre",
    "weakened_unwind_admission",
)
PROOF_VARIANTS = VARIANTS[:-1]
FUNCTION = "checked_forget_owned"


def load_source_helper():
    spec = importlib.util.spec_from_file_location("forget_own_source_certificate", HELPER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"source certificate helper unavailable: {HELPER}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


SOURCE = load_source_helper()


def line_of(source: bytes, marker: bytes) -> int:
    lines = [i for i, line in enumerate(source.splitlines(), 1)
             if marker in line]
    SOURCE.require(len(lines) == 1, f"obligation marker ambiguous: {marker!r}")
    return lines[0]


def exact_std_body(repo: Path) -> tuple[bytes, dict]:
    certificate = SOURCE.source_certificate(repo)
    std = (repo / "library/core/src/mem/mod.rs").read_bytes()
    body = SOURCE.extract_braced_item(std, SOURCE.FORGET_SIGNATURE)
    SOURCE.require(body == SOURCE.FORGET_BODY,
                   "extracted std forget body differs from pinned body")
    return body, certificate


def fixture(variant: str, body: bytes) -> tuple[bytes, bytes, dict]:
    SOURCE.require(variant in VARIANTS, "unknown forget-owner variant")
    SOURCE.require(body == SOURCE.FORGET_BODY, "runtime body changed")
    pre = b"thread_token(?tid) &*& tid == currentThread &*& <T>.own(tid, t)"
    if variant == "contradictory_pre":
        pre += b" &*& false"
    base_post = b"thread_token(tid) &*& <T>.own(tid, t)"
    post = base_post
    if variant == "false_normal":
        post += b" &*& false"
    elif variant == "owner_duplicate":
        post += b" &*& <T>.own(tid, t)"
    elif variant == "owner_wrong_value":
        post = (b"thread_token(tid) &*& <T>.own(tid, ?other) &*& "
                b"other != t")
    elif variant == "thread_duplicate":
        post += b" &*& thread_token(tid)"
    elif variant == "owner_loss":
        post = b"thread_token(tid)"
    unwind = b"true" if variant == "weakened_unwind_admission" else b"false"
    header = b"use std::mem::ManuallyDrop;\n\n"
    signature = b"pub unsafe fn checked_forget_owned<T>(t: T)\n"
    contract = SOURCE.ghost(b"req " + pre + b";\nens " + post +
                            b";\non_unwind_ens " + unwind + b";")
    original = header + signature + body + b"\n"
    verified = header + signature + contract + body + b"\n"
    SOURCE.require(SOURCE.strip_ghost(verified) == original and
                   original.count(body) == 1 and
                   original.count(b"ManuallyDrop::new(t)") == 1 and
                   original.count(signature) == 1 and
                   original.count(b"unsafe fn ") == 1,
                   "source pair is not one exact-body generic unsafe adapter")
    obligation = None
    if variant in {"false_normal", "owner_duplicate", "owner_wrong_value",
                   "thread_duplicate"}:
        obligation = {"kind": "postcondition", "line": line_of(
            verified, b"ens " + post + b";"), "predicate": {
                "false_normal": "false", "owner_duplicate": "<T>.own",
                "owner_wrong_value": "other != t",
                "thread_duplicate": "thread_token",
            }[variant]}
    elif variant == "owner_loss":
        obligation = {"kind": "leak", "line": line_of(verified, b"}")}
    elif variant == "contradictory_pre":
        obligation = {"kind": "dead_code", "line": line_of(
            verified, signature.strip())}
    elif variant == "weakened_unwind_admission":
        obligation = {"kind": "source_admission", "line": line_of(
            verified, b"on_unwind_ens true;")}
    return original, verified, {
        "variant": variant,
        "target": "generic exact-body owner-preserving unsafe adapter",
        "actual_safe_forget_contract_or_redirect": False,
        "same_runtime_body_as_std_forget": True,
        "unrestricted_sized_T": True,
        "expected_obligation": obligation,
        "original_sha256": SOURCE.digest(original),
        "verified_sha256": SOURCE.digest(verified),
        "ghost_strip_identity": True,
        "only_one_public_function": True,
    }


def write_case(repo: Path, out: Path, variant: str) -> dict:
    SOURCE.require((os.environ.get("GITHUB_ACTIONS"),
                    os.environ.get("RUNNER_ENVIRONMENT"),
                    os.environ.get("RUNNER_OS")) ==
                   ("true", "github-hosted", "Linux"),
                   "forget-owner fixtures require GitHub-hosted Linux")
    body, certificate = exact_std_body(repo)
    original, verified, record = fixture(variant, body)
    SOURCE.require(not out.exists(), f"refusing to overwrite {out}")
    (out / "original").mkdir(parents=True)
    (out / "verified").mkdir()
    (out / "original/lib.rs").write_bytes(original)
    (out / "verified/lib.rs").write_bytes(verified)
    record["source_certificate"] = certificate
    (out / "fixture.json").write_text(json.dumps(
        record, indent=2, sort_keys=True) + "\n")
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--variant", required=True, choices=VARIANTS)
    args = parser.parse_args()
    print(json.dumps(write_case(args.repo, args.out, args.variant),
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
