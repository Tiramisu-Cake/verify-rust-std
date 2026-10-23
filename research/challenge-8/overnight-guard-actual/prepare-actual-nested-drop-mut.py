#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Extend mutable owner-linked source with generic Drop and owned-forget."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
OWNER_LINKED_PATH = REPO / "research/challenge-8/overnight-helper/prepare-actual-owner-linked-mut.py"
OWNER_LINKED_SHA256 = "1656b8f84ec8216ccf6e7079a5417d1699d76ac16b05cb6f622bf31d3ef2d8a8"
PROVIDER_ADAPTER_PATH = REPO / "research/challenge-8/overnight-helper/mut_source_cloud_provider.py"
PROVIDER_ADAPTER_SHA256 = "04fd1ca82bdbfb7f837a49ed303199024208c85124cf1a45b7893f6d20ed1871"
SAVED_GUARD = (
    b"        /*@ assert <select_unpredictable::DropOnPanic<*Element>>.own(t, ?saved_guard); @*/\n"
)
RETURNED_GUARD = (
    b"        /*@ open <select_unpredictable::DropOnPanic<*Element>>.own(t, saved_guard); @*/\n"
    b"        /*@ assert *saved_guard.inner |-> ?selected_payload; @*/\n"
    b"        /*@ open raw_ptr_own::<Element>()(t, selected_payload); @*/\n"
)
ACTUAL_MARKER = b"pub fn select_unpredictable<Element>("
METHOD_MARKER = b"pub unsafe fn sort4_checked_generic_drop<T>(slot: *mut T)"
FORGET_MARKER = b"pub unsafe fn checked_forget_owned<T>(t: T)"
DROP_MARKER = b"impl<T> Drop for DropOnPanic<T> {"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)


def load(path: Path, name: str, expected: str | None = None):
    raw = path.read_bytes()
    if expected:
        require(sha(raw) == expected, f"pinned source changed: {path.name}")
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None,
            f"source dependency unavailable: {path.name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def modules():
    linked = load(OWNER_LINKED_PATH, "p2_mut_owner_linked_source",
                  OWNER_LINKED_SHA256)
    h2 = load(REPO / "research/challenge-8/overnight-guard/capture-guard-linkage.py",
              "p2_mut_generic_drop_source")
    forget = load(REPO / "research/challenge-8/overnight-forget-own/prepare.py",
                  "p2_mut_owned_forget_source")
    return linked, h2, forget


def require_cloud_provider() -> dict:
    require(sha(PROVIDER_ADAPTER_PATH.read_bytes()) == PROVIDER_ADAPTER_SHA256,
            "pinned mutable Cloud provider adapter changed")
    module = load(PROVIDER_ADAPTER_PATH, "p2_mut_nested_cloud_provider")
    return module.require_cloud_provider()


def insert_generic_drop(verified: bytes, original: bytes, method: bytes,
                        strip_ghost) -> tuple[bytes, bytes, dict]:
    require(verified.count(ACTUAL_MARKER) == 1 and
            verified.count(DROP_MARKER) == 1 and
            verified.count(METHOD_MARKER) == 0 and
            method.count(METHOD_MARKER) == 1,
            "mutable generic-drop insertion boundary changed")
    require(b"*const Element" not in verified and
            verified.count(b"*mut Element") >= 3,
            "nested-drop input is not mutable-specialized source")
    old_actual = original[original.index(ACTUAL_MARKER):]
    at = verified.index(ACTUAL_MARKER)
    out = verified[:at] + method + b"\n" + verified[at:]
    runtime = strip_ghost(out)
    require(runtime[runtime.index(ACTUAL_MARKER):] == old_actual and
            runtime.count(METHOD_MARKER) == 1 and out.count(METHOD_MARKER) == 1 and
            out.count(b"crate::mem::forget(guard);") == 1 and
            out.count(b"crate::intrinsics::select_unpredictable(") == 3,
            "generic-drop insertion changed runtime or helper inventory")
    return runtime, out, {"method_source_sha256": sha(method),
                 "generic_drop_inserted_once": True,
                 "ghost_strip_identity": True}


def insert_owned_forget(verified: bytes, original: bytes, owned_method: bytes,
                       import_line: bytes, strip_ghost) -> tuple[bytes, bytes, dict]:
    require(verified.count(import_line) == 1 and
            verified.count(FORGET_MARKER) == 0 and
            owned_method.count(FORGET_MARKER) == 1 and
            verified.count(SAVED_GUARD) == 0 and
            verified.count(RETURNED_GUARD) == 0,
            "owned-forget insertion boundary changed")
    old_actual = original[original.index(ACTUAL_MARKER):]
    own = verified.replace(import_line, import_line + b"use std::mem::ManuallyDrop;\n", 1)
    marker = own.index(ACTUAL_MARKER)
    own = own[:marker] + owned_method + b"\n" + own[marker:]
    owner_open = (
        b"        /*@ open <select_unpredictable::DropOnPanic<*Element>>.own(t, guard); @*/\n"
        b"        /*@ assert *guard.inner |-> ?selected_payload; @*/\n"
        b"        /*@ open raw_ptr_own::<Element>()(t, selected_payload); @*/\n"
    )
    require(own.count(owner_open) == 1,
            "owner-projection guard open anchor missing/ambiguous")
    own = own.replace(owner_open, SAVED_GUARD, 1)
    forget_call = b"        crate::mem::forget(guard);\n"
    require(own.count(forget_call) == 1,
            "checked forget runtime call missing/ambiguous")
    own = own.replace(forget_call, forget_call + RETURNED_GUARD, 1)
    runtime = strip_ghost(own)
    require(runtime[runtime.index(ACTUAL_MARKER):] == old_actual and
            runtime.count(FORGET_MARKER) == 1 and own.count(FORGET_MARKER) == 1 and
            own.count(SAVED_GUARD) == own.count(RETURNED_GUARD) == 1 and
            own.count(b"crate::mem::forget(guard);") == 1,
            "owned-forget transfer changed runtime or witness inventory")
    return runtime, own, {"owned_forget_source_sha256": sha(owned_method),
                          "saved_guard_transfer": True,
                          "ghost_strip_identity": True}


def owner_projection(linked):
    owner = linked.load_modules()[0]
    require(callable(getattr(owner, "strip_ghost", None)),
            "pinned owner projection lacks ghost-strip service")
    return owner


def write_case(owner_linked_dir: Path, out: Path, repo: Path = REPO) -> dict:
    linked, h2, forget = modules()
    provider = require_cloud_provider()
    require(repo.resolve() == REPO.resolve() and not out.exists(),
            "mutable nested-drop repository/output identity changed")
    owner = owner_projection(linked)
    base_record = json.loads((owner_linked_dir / "fixture.json").read_text())
    base_verified = (owner_linked_dir / "verified/lib.rs").read_bytes()
    base_original = (owner_linked_dir / "original/lib.rs").read_bytes()
    require(base_record.get("classification") ==
            "SOURCE_ONLY_MUTABLE_OWNER_LINKED_CANDIDATE" and
            base_record.get("typed_mir_binding_established") is False and
            base_record.get("helper_proof_status") == "NOT_RUN" and
            owner.strip_ghost(base_verified) == base_original,
            "mutable owner-linked input identity/status differs")
    out.mkdir(parents=True)
    body, method_cert = h2.H2A.source_certificate()
    method = h2.checked_method(body)
    six_original, six_verified, method_stage = insert_generic_drop(
        base_verified, base_original, method, owner.strip_ghost)
    six_dir = out / "six-body-mut"
    (six_dir / "original").mkdir(parents=True)
    (six_dir / "verified").mkdir()
    (six_dir / "original/lib.rs").write_bytes(six_original)
    (six_dir / "verified/lib.rs").write_bytes(six_verified)
    six_record = {
        "classification": "SOURCE_ONLY_MUTABLE_NESTED_DROP_SIX_BODY",
        "specialization": "T = *mut Element; Element unrestricted",
        "actual_helper_proved": False,
        "actual_nested_drop_proved": False,
        "typed_mir_binding_established": False,
        "helper_proof_status": "NOT_RUN",
        "original_sha256": sha(six_original),
        "verified_sha256": sha(six_verified),
        "ghost_strip_identity": True,
        "base_owner_linked_record": base_record,
        "generic_drop_source_certificate_for_generation_only": method_cert,
        "method_stage": method_stage,
        "provider": provider,
    }
    (six_dir / "fixture.json").write_text(json.dumps(six_record, indent=2, sort_keys=True) + "\n")

    owned_body, owned_cert = forget.exact_std_body(repo)
    _, owned_verified, owned_record = forget.fixture("positive", owned_body)
    header = b"use std::mem::ManuallyDrop;\n\n"
    require(owned_verified.startswith(header),
            "checked forget fixture import/header changed")
    owned_method = owned_verified[len(header):]
    seven_original, seven_verified, owned_stage = insert_owned_forget(
        six_verified, six_original, owned_method,
        b"use std::mem::MaybeUninit;\n", owner.strip_ghost)
    seven_dir = out / "seven-body-owned-forget-mut"
    (seven_dir / "original").mkdir(parents=True)
    (seven_dir / "verified").mkdir()
    (seven_dir / "original/lib.rs").write_bytes(seven_original)
    (seven_dir / "verified/lib.rs").write_bytes(seven_verified)
    seven_record = {
        "classification": "SOURCE_ONLY_MUTABLE_OWNED_FORGET_SEVEN_BODY",
        "specialization": "T = *mut Element; Element unrestricted",
        "actual_helper_proved": False,
        "actual_safe_forget_linked": False,
        "typed_mir_binding_established": False,
        "helper_proof_status": "NOT_RUN",
        "original_sha256": sha(seven_original),
        "verified_sha256": sha(seven_verified),
        "ghost_strip_identity": True,
        "source_order": six_record.get("source_order", [])[:4] +
            ["checked_forget_owned", "select_unpredictable"],
        "owned_forget_std_body_sha256": sha(owned_body),
        "owned_forget_source_certificate_for_generation_only": owned_cert,
        "owned_forget_fixture_source_record": owned_record,
        "base_six_record": six_record,
        "owned_stage": owned_stage,
        "provider": provider,
    }
    (seven_dir / "fixture.json").write_text(json.dumps(seven_record, indent=2, sort_keys=True) + "\n")
    return {"six_body": six_record, "seven_body": seven_record}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--owner-linked", type=Path, required=True)
    parser.add_argument("--repo", type=Path, default=REPO)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(write_case(args.owner_linked, args.out, args.repo),
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
