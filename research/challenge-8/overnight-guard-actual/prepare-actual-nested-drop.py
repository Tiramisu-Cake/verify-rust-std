#!/usr/bin/env python3
"""Hosted source-only six-body fixture for the actual qualified guard Drop."""

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


OWNER = load(REPO / "research/challenge-8/overnight-helper/"
             "prepare-actual-owner-linked.py", "actual_nested_owner_source")
H2 = load(REPO / "research/challenge-8/overnight-guard/"
          "capture-guard-linkage.py", "actual_nested_generic_method_source")
FORGET = load(REPO / "research/challenge-8/overnight-forget-own/"
              "prepare.py", "actual_owned_forget_source")
ACTUAL_MARKER = b"pub fn select_unpredictable<Element>("
METHOD_MARKER = b"pub unsafe fn sort4_checked_generic_drop<T>(slot: *mut T)"
FORGET_MARKER = b"pub unsafe fn checked_forget_owned<T>(t: T)"
DROP_MARKER = b"impl<T> Drop for DropOnPanic<T> {"


def require(ok: bool, why: str) -> None:
    OWNER.OWNER.require(ok, why)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_case(repo: Path, out: Path, *, with_owned_forget: bool = False) -> dict:
    require((os.environ.get("GITHUB_ACTIONS"),
             os.environ.get("RUNNER_ENVIRONMENT"),
             os.environ.get("RUNNER_OS")) ==
            ("true", "github-hosted", "Linux"),
            "actual nested capture requires GitHub-hosted Linux")
    require(repo.resolve() == REPO.resolve() and not out.exists(),
            "actual nested repository/evidence identity changed")
    out.mkdir(parents=True)
    base = out / "linked-owner-base"
    base_record = OWNER.write_case(repo, base)
    base_case = base / "linked-owner"
    old_verified = (base_case / "verified/lib.rs").read_bytes()
    old_original = (base_case / "original/lib.rs").read_bytes()
    method_body, method_cert = H2.H2A.source_certificate()
    method = H2.checked_method(method_body)
    require(old_verified.count(ACTUAL_MARKER) == 1 and
            old_original.count(ACTUAL_MARKER) == 1 and
            old_verified.count(DROP_MARKER) == 1 and
            old_verified.count(METHOD_MARKER) == 0 and
            method.count(METHOD_MARKER) == 1 and
            method.count(method_body) == 1,
            "actual nested source insertion boundary changed")
    at = old_verified.index(ACTUAL_MARKER)
    verified = old_verified[:at] + method + b"\n" + old_verified[at:]
    original = OWNER.OWNER.strip_ghost(verified)
    actual_body, actual_cert = OWNER.OWNER.ACTUAL.source_certificate(repo)
    require(OWNER.OWNER.strip_ghost(old_verified) == old_original and
            old_original.count(actual_body) == 1 and
            original.count(actual_body) == 1 and
            verified.count(ACTUAL_MARKER) ==
              verified.count(METHOD_MARKER) ==
              verified.count(DROP_MARKER) == 1 and
            verified.count(OWNER.OWNER.OWNER_PRED) == 1 and
            verified.count(OWNER.OWNER.NESTED_DROP_GHOST) == 1 and
            verified.count(b"safety_proof {") == 1 and
            verified.count(b"crate::mem::forget(guard);") == 1 and
            verified.count(b"crate::intrinsics::select_unpredictable(") == 3 and
            original.count(b"crate::mem::forget(guard);") == 1 and
            original.count(b"crate::intrinsics::select_unpredictable(") == 3,
            "actual nested runtime/ghost/contract inventory changed")
    case = out / "six-body"
    (case / "original").mkdir(parents=True)
    (case / "verified").mkdir()
    (case / "original/lib.rs").write_bytes(original)
    (case / "verified/lib.rs").write_bytes(verified)
    record = {
        "classification": "SOURCE_ONLY_ACTUAL_NESTED_DROP_SIX_BODY",
        "actual_helper_proved": False,
        "actual_nested_drop_proved": False,
        "generic_method_proved_in_this_unit": False,
        "frontend_gate_installed": False,
        "original_sha256": sha(original),
        "verified_sha256": sha(verified),
        "ghost_strip_identity": OWNER.OWNER.strip_ghost(verified) == original,
        "source_order": [
            "sort4_certified_maybeuninit::sort4_checked_maybeuninit_new",
            "sort4_checked_as_mut_ptr", "sort4_checked_pointer_drop",
            "sort4_checked_generic_drop", "select_unpredictable",
            "<select_unpredictable::DropOnPanic<T> as std::ops::Drop>::drop",
        ],
        "base_linked_owner_source": base_record,
        "generic_method_source_certificate": method_cert,
        "actual_source_certificate": actual_cert,
    }
    (case / "fixture.json").write_text(json.dumps(
        record, indent=2, sort_keys=True) + "\n")
    if with_owned_forget:
        owned_body, owned_cert = FORGET.exact_std_body(repo)
        _, owned_verified, owned_record = FORGET.fixture(
            "positive", owned_body)
        import_line = b"use std::mem::MaybeUninit;\n"
        owned_import = b"use std::mem::ManuallyDrop;\n"
        owned_header = owned_import + b"\n"
        require(owned_verified.startswith(owned_header) and
                verified.count(import_line) == 1 and
                verified.count(owned_import) == 0 and
                verified.count(FORGET_MARKER) == 0,
                "owner-preserving callee import/source boundary changed")
        owned_method = owned_verified[len(owned_header):]
        require(owned_method.count(FORGET_MARKER) == 1 and
                owned_method.count(owned_body) == 1,
                "owner-preserving exact callee source changed")
        owned = verified.replace(import_line, import_line + owned_import, 1)
        at = owned.index(ACTUAL_MARKER)
        owned = owned[:at] + owned_method + b"\n" + owned[at:]
        original_open = OWNER.OWNER.OPEN_OWNER
        saved = (
            b"        /*@ assert <select_unpredictable::DropOnPanic<*Element>>.own(t, ?saved_guard); @*/\n"
        )
        returned_open = (
            b"        /*@ open <select_unpredictable::DropOnPanic<*Element>>.own(t, saved_guard); @*/\n"
            b"        /*@ assert *saved_guard.inner |-> ?selected_payload; @*/\n"
            b"        /*@ open raw_ptr_own::<Element>()(t, selected_payload); @*/\n"
        )
        forget_call = b"        crate::mem::forget(guard);\n"
        require(owned.count(original_open) == 1 and
                owned.count(forget_call) == 1 and
                owned.count(saved) == 0 and
                owned.count(returned_open) == 0,
                "owner-preserving ghost transfer anchor changed")
        owned = owned.replace(original_open, saved, 1)
        owned = owned.replace(forget_call, forget_call + returned_open, 1)
        owned_original = OWNER.OWNER.strip_ghost(owned)
        require(owned_original.count(actual_body) == 1 and
                owned_original.count(owned_body) == 1 and
                owned.count(FORGET_MARKER) == 1 and
                owned.count(OWNER.OWNER.OWNER_PRED) == 1 and
                owned.count(b"safety_proof {") == 1 and
                owned.count(OWNER.OWNER.NESTED_DROP_GHOST) == 1 and
                owned.count(b"crate::mem::forget(guard);") == 1 and
                owned.count(b"crate::intrinsics::select_unpredictable(") == 3,
                "owner-preserving seven-body executable inventory changed")
        owned_case = out / "seven-body-owned-forget"
        (owned_case / "original").mkdir(parents=True)
        (owned_case / "verified").mkdir()
        (owned_case / "original/lib.rs").write_bytes(owned_original)
        (owned_case / "verified/lib.rs").write_bytes(owned)
        owned_case_record = {
            "classification": "SOURCE_ONLY_ACTUAL_OWNED_FORGET_SEVEN_BODY",
            "actual_helper_proved": False,
            "actual_nested_drop_proved": False,
            "actual_safe_forget_linked": False,
            "original_sha256": sha(owned_original),
            "verified_sha256": sha(owned),
            "ghost_strip_identity": OWNER.OWNER.strip_ghost(owned) ==
                owned_original,
            "source_order": record["source_order"][:4] +
                ["checked_forget_owned"] + record["source_order"][4:],
            "generic_pointer_drop_source_certificate": method_cert,
            "owner_preserving_forget_source_certificate": owned_cert,
            "owner_preserving_forget_positive_fixture": owned_record,
            "actual_source_certificate": actual_cert,
        }
        (owned_case / "fixture.json").write_text(json.dumps(
            owned_case_record, indent=2, sort_keys=True) + "\n")
        record["owned_forget_seven_body"] = owned_case_record
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--with-owned-forget", action="store_true")
    args = parser.parse_args()
    print(json.dumps(write_case(args.repo, args.out,
                                with_owned_forget=args.with_owned_forget),
                     indent=2, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
