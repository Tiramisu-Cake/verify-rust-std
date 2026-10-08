#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted-only nine-body exact-source A1 plus actual owner/forget fixture."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"missing source preparer: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


SEVEN = load(HERE.parent / "overnight-guard-actual" /
             "prepare-actual-nested-drop.py", "nine_body_seven_source")
A1 = load(HERE.parent / "overnight-helper" /
          "prepare-assume-init-2610.py", "nine_body_a1_source")
CASE_NAME = "nine-body-a1-owned-forget"
ORDER = (
    "sort4_certified_maybeuninit::sort4_checked_maybeuninit_new",
    "sort4_checked_as_mut_ptr", "sort4_checked_pointer_drop",
    "sort4_checked_generic_drop", A1.TRANSMUTE_ADAPTER_NAME,
    A1.ADAPTER_NAME, "checked_forget_owned", "select_unpredictable",
    "<select_unpredictable::DropOnPanic<T> as std::ops::Drop>::drop",
)
OLD_FEATURE = b"#![feature(core_intrinsics)]\n"
NEW_FEATURE = (
    b"#![feature(core_intrinsics, transmute_neo, sized_type_properties)]\n"
)
OLD_IMPORT = b"use std::mem::MaybeUninit;\n"
NEW_IMPORT = b"use std::mem::{SizedTypeProperties, transmute_neo};\n"


def require(ok: bool, why: str) -> None:
    SEVEN.require(ok, why)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def a1_pair(repo: Path) -> tuple[bytes, dict]:
    _, verified, record = A1.linkage_fixture_source(repo)
    transmute_marker = b"pub unsafe fn " + A1.TRANSMUTE_ADAPTER_NAME.encode()
    assume_marker = b"pub unsafe fn " + A1.ADAPTER_NAME.encode()
    require(verified.count(transmute_marker) ==
            verified.count(assume_marker) == 1 and
            verified.index(transmute_marker) < verified.index(assume_marker),
            "A1 local adapter pair missing or reordered")
    pair = verified[verified.index(transmute_marker):].rstrip() + b"\n\n"
    require(pair.count(b"transmute_unchecked(src)") == 1 and
            pair.count(b"transmute_neo(storage)") == 1 and
            pair.count(transmute_marker) == pair.count(assume_marker) == 1,
            "A1 exact source body or call inventory changed")
    return pair, record


def write_case(repo: Path, out: Path) -> dict:
    require((os.environ.get("GITHUB_ACTIONS"),
             os.environ.get("RUNNER_ENVIRONMENT"),
             os.environ.get("RUNNER_OS")) ==
            ("true", "github-hosted", "Linux"),
            "nine-body preparation requires GitHub-hosted Linux")
    require(repo.resolve() == REPO.resolve() and not out.exists(),
            "nine-body repository/evidence identity changed")
    out.mkdir(parents=True)
    seven_out = out / "seven-body-source"
    seven_record = SEVEN.write_case(repo, seven_out, with_owned_forget=True)
    seven_case = seven_out / "seven-body-owned-forget"
    seven_verified = (seven_case / "verified/lib.rs").read_bytes()
    seven_original = (seven_case / "original/lib.rs").read_bytes()
    pair, a1_record = a1_pair(repo)
    actual_marker = SEVEN.ACTUAL_MARKER
    insert_marker = SEVEN.FORGET_MARKER
    require(seven_verified.count(OLD_FEATURE) == 1 and
            seven_verified.count(NEW_FEATURE) == 0 and
            seven_verified.count(OLD_IMPORT) == 1 and
            seven_verified.count(NEW_IMPORT) == 0 and
            seven_verified.count(insert_marker) == 1 and
            seven_verified.count(actual_marker) == 1 and
            seven_verified.index(insert_marker) <
                seven_verified.index(actual_marker) and
            all(seven_verified.count(name.encode()) == 0 for name in
                (A1.TRANSMUTE_ADAPTER_NAME, A1.ADAPTER_NAME)),
            "seven-body import, feature, or insertion boundary changed")
    verified = seven_verified.replace(OLD_FEATURE, NEW_FEATURE, 1)
    verified = verified.replace(OLD_IMPORT, OLD_IMPORT + NEW_IMPORT, 1)
    verified = verified.replace(insert_marker, pair + insert_marker, 1)
    original = SEVEN.OWNER.OWNER.strip_ghost(verified)
    actual_body, actual_cert = SEVEN.OWNER.OWNER.ACTUAL.source_certificate(repo)
    require(SEVEN.OWNER.OWNER.strip_ghost(seven_verified) == seven_original and
            original.count(actual_body) == seven_original.count(actual_body) == 1 and
            verified[verified.index(actual_marker):] ==
                seven_verified[seven_verified.index(actual_marker):] and
            original[original.index(actual_marker):] ==
                seven_original[seven_original.index(actual_marker):] and
            verified.count(b"safety_proof {") == 1 and
            verified.count(SEVEN.OWNER.OWNER.OWNER_PRED) == 1 and
            verified.count(SEVEN.OWNER.OWNER.NESTED_DROP_GHOST) == 1 and
            verified.count(b"crate::mem::forget(guard);") == 1 and
            verified.count(b"crate::intrinsics::select_unpredictable(") == 3 and
            all(verified.count((b"pub unsafe fn " + name.encode())) == 1
                for name in (A1.TRANSMUTE_ADAPTER_NAME, A1.ADAPTER_NAME)),
            "nine-body source changed actual runtime or guard protocol")
    case = out / CASE_NAME
    (case / "original").mkdir(parents=True)
    (case / "verified").mkdir()
    (case / "original/lib.rs").write_bytes(original)
    (case / "verified/lib.rs").write_bytes(verified)
    record = {
        "classification": "SOURCE_ONLY_NINE_BODY_A1_ACTUAL_CAPTURE",
        "source_order": list(ORDER),
        "original_sha256": sha(original),
        "verified_sha256": sha(verified),
        "ghost_strip_identity": SEVEN.OWNER.OWNER.strip_ghost(verified) == original,
        "actual_helper_suffix_exact_seven_body": True,
        "actual_helper_body_exact_std": True,
        "actual_helper_proved": False,
        "actual_safe_forget_linked": False,
        "a1_linkage_admitted_in_nine_body": False,
        "semantic_frontend_enabled": False,
        "a1_pair_sha256": sha(pair),
        "a1_linkage_source_certificate": a1_record,
        "seven_body_source_certificate":
            seven_record["owned_forget_seven_body"],
        "actual_source_certificate": actual_cert,
    }
    (case / "fixture.json").write_text(json.dumps(
        record, indent=2, sort_keys=True) + "\n")
    (out / "source-summary.json").write_text(json.dumps(
        record, indent=2, sort_keys=True) + "\n")
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(write_case(args.repo, args.out),
                     indent=2, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
