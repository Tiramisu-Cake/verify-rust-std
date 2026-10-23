#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Build the inactive mutable nine-body source candidate from seven-body input."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
R21_SHA256 = "8a23499c9852dfdc9973cca186daa83dcc2f7836642c40627ab1def6dd763772"
A1_SHA256 = "875e0f14bda4971c812bfb5ed34e04ae46caddba1506c4f3f5a6093c807e7b40"
PROVIDER_ADAPTER_PATH = REPO / "research/challenge-8/overnight-helper/mut_source_cloud_provider.py"
PROVIDER_ADAPTER_SHA256 = "04fd1ca82bdbfb7f837a49ed303199024208c85124cf1a45b7893f6d20ed1871"
A1_PATH = REPO / "research/challenge-8/overnight-helper/prepare-assume-init-2610.py"
OLD_FEATURE = b"#![feature(core_intrinsics)]\n"
NEW_FEATURE = b"#![feature(core_intrinsics, transmute_neo, sized_type_properties)]\n"
OLD_IMPORT = b"use std::mem::MaybeUninit;\n"
NEW_IMPORT = b"use std::mem::{SizedTypeProperties, transmute_neo};\n"
ACTUAL_MARKER = b"pub fn select_unpredictable<Element>("
TRANSMUTE_NAME = "checked_transmute_neo_pointer"
ASSUME_NAME = "checked_assume_init_pointer"
EXPECTED_ORDER = (
    "sort4_certified_maybeuninit::sort4_checked_maybeuninit_new",
    "sort4_checked_as_mut_ptr", "sort4_checked_pointer_drop",
    "sort4_checked_generic_drop", TRANSMUTE_NAME, ASSUME_NAME,
    "checked_forget_owned", "select_unpredictable",
    "<select_unpredictable::DropOnPanic<T> as std::ops::Drop>::drop",
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None,
            f"source transform unavailable: {path.name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def require_cloud_provider() -> dict:
    require(sha(PROVIDER_ADAPTER_PATH.read_bytes()) == PROVIDER_ADAPTER_SHA256,
            "pinned mutable Cloud provider adapter changed")
    module = load(PROVIDER_ADAPTER_PATH, "p2_mut_nine_cloud_provider")
    return module.require_cloud_provider()


def load_a1():
    require(A1_PATH.is_file() and sha(A1_PATH.read_bytes()) == A1_SHA256,
            "pinned A1 source builder changed")
    spec = importlib.util.spec_from_file_location("p2_mut_nine_a1_source", A1_PATH)
    require(spec is not None and spec.loader is not None,
            "generic A1 source builder unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def adapt_a1_pair_mut(pair: bytes, a1) -> tuple[bytes, dict]:
    """Specialize the pinned const-pointer A1 source pair to mutable pointers.

    The two components have fixed source inventories from the pinned builder:
    four pointer-type sites in the transmute adapter and three in assume_init.
    Only the pointer type spelling changes; reverse substitution must recover
    the complete input pair byte-for-byte.
    """
    tx_marker = b"pub unsafe fn " + a1.TRANSMUTE_ADAPTER_NAME.encode()
    as_marker = b"pub unsafe fn " + a1.ADAPTER_NAME.encode()
    const_sig_tx = (tx_marker +
        b"<Element>(src: MaybeUninit<*const Element>) -> *const Element\n")
    const_sig_as = (as_marker +
        b"<Element>(storage: MaybeUninit<*const Element>) -> *const Element\n")
    mut_sig_tx = (tx_marker +
        b"<Element>(src: MaybeUninit<*mut Element>) -> *mut Element\n")
    mut_sig_as = (as_marker +
        b"<Element>(storage: MaybeUninit<*mut Element>) -> *mut Element\n")
    require(isinstance(pair, bytes) and pair.count(tx_marker) == 1 and
            pair.count(as_marker) == 1 and pair.index(tx_marker) < pair.index(as_marker),
            "A1 local adapter pair missing, duplicated, or reordered")
    tx_at, as_at = pair.index(tx_marker), pair.index(as_marker)
    tx_component, as_component = pair[tx_at:as_at], pair[as_at:]
    require(tx_component.count(const_sig_tx) == 1 and
            tx_component.count(b"*const Element") == 4 and
            tx_component.count(b"transmute_unchecked(src)") == 1 and
            tx_component.count(b"<MaybeUninit<*const Element> as SizedTypeProperties>::SIZE") == 1 and
            tx_component.count(b"<*const Element as SizedTypeProperties>::SIZE") == 1,
            "pinned A1 transmute adapter types/body differ from the finite inventory")
    require(as_component.count(const_sig_as) == 1 and
            as_component.count(b"*const Element") == 3 and
            as_component.count(b"assert_inhabited::<*const Element>()") == 1 and
            as_component.count(b"transmute_neo(storage)") == 1,
            "pinned A1 assume_init adapter types/body differ from the finite inventory")
    mut_pair = pair.replace(b"*const Element", b"*mut Element")
    require(mut_pair.count(b"*const Element") == 0 and
            mut_pair.count(mut_sig_tx) == 1 and mut_pair.count(mut_sig_as) == 1 and
            mut_pair.count(b"<MaybeUninit<*mut Element> as SizedTypeProperties>::SIZE") == 1 and
            mut_pair.count(b"<*mut Element as SizedTypeProperties>::SIZE") == 1 and
            mut_pair.count(b"assert_inhabited::<*mut Element>()") == 1 and
            mut_pair.count(b"transmute_unchecked(src)") == 1 and
            mut_pair.count(b"transmute_neo(storage)") == 1 and
            mut_pair.replace(b"*mut Element", b"*const Element") == pair,
            "finite mutable A1 adaptation changed source outside pointer specialization")
    return mut_pair, {
        "a1_builder_sha256": A1_SHA256,
        "const_pointer_type_sites": {"transmute": 4, "assume_init": 3},
        "mutable_pointer_type_sites": {"transmute": 4, "assume_init": 3},
        "runtime_generic_body_preserved_by_reverse_substitution": True,
        "typed_mir_binding_established": False,
    }


def a1_source_pair(repo: Path) -> tuple[bytes, dict]:
    a1 = load_a1()
    _, verified, record = a1.linkage_fixture_source(repo)
    tx_marker = b"pub unsafe fn " + a1.TRANSMUTE_ADAPTER_NAME.encode()
    require(verified.count(tx_marker) == 1,
            "A1 linkage source lacks its unique callee boundary")
    pair = verified[verified.index(tx_marker):].rstrip() + b"\n\n"
    require(pair.count(b"transmute_unchecked(src)") == 1 and
            pair.count(b"transmute_neo(storage)") == 1,
            "A1 exact source body/call inventory changed")
    mutable_pair, adaptation = adapt_a1_pair_mut(pair, a1)
    return mutable_pair, {"source_certificate_for_generation_only": record,
                          "mutable_source_adaptation": adaptation}


def insert_a1_pair(seven_original: bytes, seven_verified: bytes,
                   pair: bytes, a1_record: dict, strip_ghost) -> tuple[bytes, bytes, dict]:
    a1 = load_a1()
    tx_marker = b"pub unsafe fn " + a1.TRANSMUTE_ADAPTER_NAME.encode()
    as_marker = b"pub unsafe fn " + a1.ADAPTER_NAME.encode()
    require(seven_verified.count(OLD_FEATURE) == 1 and
            seven_verified.count(NEW_FEATURE) == 0 and
            seven_verified.count(OLD_IMPORT) == 1 and
            seven_verified.count(NEW_IMPORT) == 0 and
            seven_verified.count(tx_marker) == 0 and
            seven_verified.count(as_marker) == 0 and
            seven_verified.count(ACTUAL_MARKER) == 1,
            "mutable seven-body A1 insertion boundary changed")
    mut_sig_tx = (tx_marker +
        b"<Element>(src: MaybeUninit<*mut Element>) -> *mut Element\n")
    mut_sig_as = (as_marker +
        b"<Element>(storage: MaybeUninit<*mut Element>) -> *mut Element\n")
    require(pair.count(tx_marker) == pair.count(as_marker) == 1 and
            pair.index(tx_marker) < pair.index(as_marker) and
            pair.count(mut_sig_tx) == pair.count(mut_sig_as) == 1 and
            pair.count(b"<MaybeUninit<*mut Element> as SizedTypeProperties>::SIZE") == 1 and
            pair.count(b"<*mut Element as SizedTypeProperties>::SIZE") == 1 and
            pair.count(b"assert_inhabited::<*mut Element>()") == 1 and
            pair.count(b"transmute_unchecked(src)") == 1 and
            pair.count(b"transmute_neo(storage)") == 1 and
            b"*const Element" not in pair,
            "A1 mutable source pair missing, const-specialized, or reordered")
    verified = seven_verified.replace(OLD_FEATURE, NEW_FEATURE, 1)
    verified = verified.replace(OLD_IMPORT, OLD_IMPORT + NEW_IMPORT, 1)
    at = verified.index(ACTUAL_MARKER)
    verified = verified[:at] + pair + b"\n\n" + verified[at:]
    original = strip_ghost(verified)
    actual_at = verified.index(ACTUAL_MARKER)
    old_actual_at = seven_verified.index(ACTUAL_MARKER)
    require(verified[actual_at:] == seven_verified[old_actual_at:] and
            original[original.index(ACTUAL_MARKER):] ==
                seven_original[seven_original.index(ACTUAL_MARKER):] and
            verified.count(b"*mut Element") >= 3 and
            b"*const Element" not in verified and
            verified.count(b"crate::mem::forget(guard);") == 1 and
            verified.count(b"crate::intrinsics::select_unpredictable(") == 3,
            "A1 insertion changed actual helper bytes, pointer kind, or call inventory")
    return original, verified, {
        "a1_pair_sha256": sha(pair),
        "a1_source_certificate_for_generation_only": a1_record,
        "a1_pair_inserted_before_actual_helper": True,
        "ghost_strip_identity": True,
        "typed_mir_binding_established": False,
    }


def apply_fractional_candidate(original: bytes, verified: bytes, record: dict) -> tuple[bytes, dict]:
    require(record.get("specialization") == "T = *mut Element; Element unrestricted" and
            verified.count(b"*const Element") == 0 and
            verified.count(b"crate::mem::forget(guard);") == 1,
            "fractional input is not the exact mutable seven/nine-body candidate")
    path = HERE / "r21_fractional_forget.py"
    require(sha(path.read_bytes()) == R21_SHA256,
            "pinned R21 fractional transform changed")
    module = load(path, "p2_mut_nine_r21_fractional")
    candidate = module.transform(verified, "positive")
    linked_path = REPO / "research/challenge-8/overnight-helper/prepare-actual-owner-linked-mut.py"
    linked_spec = importlib.util.spec_from_file_location(
        "p2_mut_nine_mut_owner_linked", linked_path)
    require(linked_spec is not None and linked_spec.loader is not None,
            "mutable owner-linked source adapter unavailable")
    linked = importlib.util.module_from_spec(linked_spec)
    sys.modules[linked_spec.name] = linked
    linked_spec.loader.exec_module(linked)
    owner = linked.load_modules()[0]
    require(owner.strip_ghost(candidate) == original and
            candidate.count(b"*const Element") == 0,
            "R20/R21 mutable candidate changed runtime or pointer kind")
    return candidate, {
        "fractional_transform_sha256": sha(path.read_bytes()),
        "r20_repair_sha256": module.PINNED_REPAIR_SHA256,
        "verified_sha256": sha(candidate),
        "runtime_source_preserved": True,
        "typed_mir_binding_established": False,
    }


def write_case(seven_body_dir: Path, out: Path, repo: Path = REPO) -> dict:
    provider = require_cloud_provider()
    require(repo.resolve() == REPO.resolve() and not out.exists(),
            "mutable nine-body repository/output identity changed")
    record = json.loads((seven_body_dir / "fixture.json").read_text())
    seven_original = (seven_body_dir / "original/lib.rs").read_bytes()
    seven_verified = (seven_body_dir / "verified/lib.rs").read_bytes()
    require(record.get("classification") ==
            "SOURCE_ONLY_MUTABLE_OWNED_FORGET_SEVEN_BODY" and
            record.get("typed_mir_binding_established") is False and
            record.get("helper_proof_status") == "NOT_RUN",
            "mutable seven-body input record/status differs")
    require(record.get("original_sha256") == sha(seven_original) and
            record.get("verified_sha256") == sha(seven_verified),
            "mutable seven-body source bytes differ from record")
    pair, a1_record = a1_source_pair(repo)
    # Use the owner module from the mutable source route; it never loads the
    # const fixture writer.
    linked_path = REPO / "research/challenge-8/overnight-helper/prepare-actual-owner-linked-mut.py"
    linked_spec = importlib.util.spec_from_file_location(
        "p2_mut_nine_owner_linked", linked_path)
    require(linked_spec is not None and linked_spec.loader is not None,
            "mutable owner-linked source adapter unavailable")
    linked = importlib.util.module_from_spec(linked_spec)
    sys.modules[linked_spec.name] = linked
    linked_spec.loader.exec_module(linked)
    owner = linked.load_modules()[0]
    original, a1_verified, a1_stage = insert_a1_pair(
        seven_original, seven_verified, pair, a1_record, owner.strip_ghost)
    require(owner.strip_ghost(a1_verified) == original,
            "A1 source insertion changed ghost-strip identity")
    pre_fractional_record = dict(record,
        specialization="T = *mut Element; Element unrestricted")
    fractional, fractional_stage = apply_fractional_candidate(
        original, a1_verified, pre_fractional_record)
    case = out / "nine-body-mut"
    (case / "original").mkdir(parents=True)
    (case / "verified").mkdir()
    (case / "original/lib.rs").write_bytes(original)
    (case / "verified/lib.rs").write_bytes(fractional)
    final_record = {
        "classification": "SOURCE_ONLY_MUTABLE_NINE_BODY_A1_FRACTIONAL_CAPTURE",
        "specialization": "T = *mut Element; Element unrestricted",
        "source_order": list(EXPECTED_ORDER),
        "original_sha256": sha(original),
        "verified_sha256": sha(fractional),
        "ghost_strip_identity": owner.strip_ghost(fractional) == original,
        "actual_helper_proved": False,
        "actual_safe_forget_linked": False,
        "typed_mir_binding_established": False,
        "translator_admission": "NOT_IMPLEMENTED",
        "helper_proof_status": "NOT_RUN",
        "publication_status": "NOT_PUBLISHED",
        "proof_credit": 0,
        "seven_body_input_record": record,
        "provider": provider,
        "a1_stage": a1_stage,
        "fractional_stage": fractional_stage,
        "required_cloud_capture": [
            "fresh exact original/verified source identities",
            "NORMAL and readonly full decoded unit and all nine body hashes",
            "source, unit, body, snapshot, ordered ghost and cleanup pins",
        ],
    }
    (case / "fixture.json").write_text(json.dumps(
        final_record, indent=2, sort_keys=True) + "\n")
    return final_record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seven-body", type=Path, required=True)
    parser.add_argument("--repo", type=Path, default=REPO)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(write_case(args.seven_body, args.out, args.repo),
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
