#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Inactive source-only adapter for a prepared P2 mutable owner unit.

Input is an already prepared original/verified source pair containing the
mutable actual helper and checked forget callee. This adapter layers the
existing owner projection, seven-body saved-guard transfer, and R21/R20
fractional source transforms without editing the const route. It does not
extract std source, compile, export/decode MIR, admit a translator gate, or
prove the unit. The input must come from a separately authorized exact-source
preparation/capture route.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
OWNER_SHA256 = "6680e74fda839501db3c9221f026a3398ce5d903a8134733b6f5375c165afbb8"
FRACTIONAL_SHA256 = "8a23499c9852dfdc9973cca186daa83dcc2f7836642c40627ab1def6dd763772"
MUT_WRITER_SHA256 = "d205ec1b557b199e1a314bc5664197554309b45ce6825b4f3b51917babc13d61"
CONTRACT_SHA256 = "dc985de2e2a0e1a95e6c12c4b9cb78c4042d9d45f949d78904a999e82262b870"
PROVIDER_ADAPTER_SHA256 = "04fd1ca82bdbfb7f837a49ed303199024208c85124cf1a45b7893f6d20ed1871"
PROVIDER_ADAPTER_PATH = HERE.parent / "overnight-helper" / "mut_source_cloud_provider.py"
ACTUAL_HELPER_CONTRACT = (
    b"/*@\nreq thread_token(?t) &*& t == currentThread;\n@*/\n"
    b"/*@\nens thread_token(t) &*& (result as pointer) ==\n"
    b"    (if condition { true_val as pointer } else { false_val as pointer });\n@*/\n"
    b"/*@\non_unwind_ens false;\n@*/\n")
MUT_SIGNATURE = (
    b"pub fn select_unpredictable<Element>(\n"
    b"    condition: bool,\n    true_val: *mut Element,\n"
    b"    false_val: *mut Element,\n) -> *mut Element\n"
)
SAVED_GUARD = (
    b"        /*@ assert <select_unpredictable::DropOnPanic<*Element>>.own(t, ?saved_guard); @*/\n"
)
RETURNED_GUARD = (
    b"        /*@ open <select_unpredictable::DropOnPanic<*Element>>.own(t, saved_guard); @*/\n"
    b"        /*@ assert *saved_guard.inner |-> ?selected_payload; @*/\n"
    b"        /*@ open raw_ptr_own::<Element>()(t, selected_payload); @*/\n"
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)


def require_cloud_provider() -> dict:
    raw = PROVIDER_ADAPTER_PATH.read_bytes()
    require(sha(raw) == PROVIDER_ADAPTER_SHA256,
            "pinned mutable Cloud provider adapter changed")
    spec = importlib.util.spec_from_file_location(
        "p2_mut_alternate_cloud_provider", PROVIDER_ADAPTER_PATH)
    require(spec is not None and spec.loader is not None,
            "mutable Cloud provider adapter unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.require_cloud_provider()


def load_pinned(path: Path, expected: str, module_name: str):
    raw = path.read_bytes()
    require(sha(raw) == expected, f"pinned transform changed: {path.name}")
    spec = importlib.util.spec_from_file_location(module_name, path)
    require(spec is not None and spec.loader is not None,
            f"cannot load pinned transform: {path.name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_dependencies():
    owner = load_pinned(HERE.parent / "overnight-helper" /
                        "prepare-actual-owner-projection.py", OWNER_SHA256,
                        "p2_mut_owner_projection")
    fractional = load_pinned(HERE / "r21_fractional_forget.py", FRACTIONAL_SHA256,
                             "p2_mut_r21_fractional")
    writer = load_pinned(HERE.parent / "overnight-helper" /
                         "prepare-actual-helper-capture-mut.py", MUT_WRITER_SHA256,
                         "p2_mut_fixture_writer_pin")
    return owner, fractional, writer


def validate_pair(original: bytes, verified: bytes, record: dict) -> None:
    owner, _, writer = load_dependencies()
    require(record.get("classification") == "MUTABLE_OWNER_INPUT_CAPTURE_ONLY" and
            record.get("input_stage") == "PRE_OWNER_PROJECTION_FULL_UNIT",
            "input is not a pre-owner-projection mutable full-unit source pair")
    require(record.get("actual_helper_proved") is False and
            record.get("helper_proof_status", "NOT_RUN") == "NOT_RUN" and
            record.get("semantic_frontend_enabled", False) is False,
            "input record claims proof or frontend admission")
    require(verified.count(writer.MUT_SIGNATURE) == 1 and
            b"*const Element" not in verified,
            "input is not the exact mutable specialization or mixes pointer kinds")
    require(sha(ACTUAL_HELPER_CONTRACT) == CONTRACT_SHA256 and
            record.get("contract_text_sha256") == CONTRACT_SHA256,
            "input P2 contract hash is missing or differs")
    require(verified.count(writer.MUT_SIGNATURE) == 1 and
            verified.count(ACTUAL_HELPER_CONTRACT) == 1 and
            verified.index(ACTUAL_HELPER_CONTRACT) ==
                verified.index(writer.MUT_SIGNATURE) + len(writer.MUT_SIGNATURE),
            "exact P2 helper contract is absent or outside its signature boundary")
    actual_contract = verified[verified.index(ACTUAL_HELPER_CONTRACT):
                               verified.index(ACTUAL_HELPER_CONTRACT) +
                               len(ACTUAL_HELPER_CONTRACT)]
    require(sha(actual_contract) == record["contract_text_sha256"],
            "verified P2 contract bytes differ from their mandatory hash")
    require(record.get("original_sha256") == sha(original) and
            record.get("verified_sha256") == sha(verified),
            "input source pair does not match its recorded hashes")
    require(owner.strip_ghost(verified) == original,
            "input ghost strip differs from original runtime source")
    require(verified.count(b"pub unsafe fn checked_forget_owned<T>(t: T)") == 1,
            "input lacks the unique checked forget callee")
    require(verified.count(b"crate::mem::forget(guard);\n") == 1 and
            verified.count(b"crate::intrinsics::select_unpredictable(") == 3,
            "input actual helper call/forget inventory changed")


def _add_saved_guard_transfer(owner, projected: bytes) -> bytes:
    """Apply the established seven-body guard witness placement exactly."""
    require(projected.count(owner.OPEN_OWNER) == 1,
            "owner-projection returned-guard open anchor missing/ambiguous")
    require(projected.count(SAVED_GUARD) == 0 and projected.count(RETURNED_GUARD) == 0,
            "saved-guard transfer already present")
    out = projected.replace(owner.OPEN_OWNER, SAVED_GUARD, 1)
    forget_call = b"        crate::mem::forget(guard);\n"
    require(out.count(forget_call) == 1,
            "unique actual forget call anchor missing/ambiguous")
    out = out.replace(forget_call, forget_call + RETURNED_GUARD, 1)
    require(out.count(SAVED_GUARD) == out.count(RETURNED_GUARD) == 1,
            "saved/returned guard witness inventory differs")
    return out


def transform_pair(original: bytes, verified: bytes, record: dict) -> tuple[bytes, dict]:
    validate_pair(original, verified, record)
    owner, fractional, _ = load_dependencies()
    # R21's owner-close anchor is the reviewed nominal logical aggregate used
    # by the nine-body route; keep the runtime guard expression unchanged.
    owner_projected = owner.candidate(verified, original, owner_literal=True)
    require(owner.strip_ghost(owner_projected) == original,
            "owner projection changed runtime source")
    transferred = _add_saved_guard_transfer(owner, owner_projected)
    require(owner.strip_ghost(transferred) == original,
            "saved-guard source adapter changed runtime source")
    final = fractional.transform(transferred, "positive")
    require(owner.strip_ghost(final) == original,
            "R21/R20 mutable candidate changed runtime source")
    require(final.count(MUT_SIGNATURE) == 1 and b"*const Element" not in final,
            "final candidate changed pointer kind or signature depth")
    repair = fractional._load_pinned("r20_final_select_repair.py",
                                     "p2_mut_r20_repair_identity",
                                     fractional.PINNED_REPAIR_SHA256)
    require(final.count(repair.SELECTED_BRANCH_BLOCK) == 1 and
            final.count(fractional.FORGET_HALF_CONTRACT) == 1 and
            final.count(fractional.CONSTRUCTOR_OWN_RELEASE) == 1,
            "R20/R21 expected selected/fractional source stage is incomplete")
    stages = {
        "input_original_sha256": sha(original),
        "input_verified_sha256": sha(verified),
        "owner_projection_sha256": sha(owner_projected),
        "saved_guard_transfer_sha256": sha(transferred),
        "final_verified_sha256": sha(final),
        "runtime_source_preserved": True,
        "owner_projection_dependency_sha256": OWNER_SHA256,
        "r20_repair_dependency_sha256": fractional.PINNED_REPAIR_SHA256,
        "r21_fractional_dependency_sha256": FRACTIONAL_SHA256,
        "mutable_fixture_writer_sha256": MUT_WRITER_SHA256,
        "contract_text_sha256": sha(ACTUAL_HELPER_CONTRACT),
    }
    return final, stages


def write_candidate(input_dir: Path, output_dir: Path) -> dict:
    provider = require_cloud_provider()
    require(not output_dir.exists(), f"refusing to overwrite {output_dir}")
    original = (input_dir / "original/lib.rs").read_bytes()
    verified = (input_dir / "verified/lib.rs").read_bytes()
    record = json.loads((input_dir / "fixture.json").read_text())
    final, stages = transform_pair(original, verified, record)
    (output_dir / "original").mkdir(parents=True)
    (output_dir / "verified").mkdir()
    (output_dir / "original/lib.rs").write_bytes(original)
    (output_dir / "verified/lib.rs").write_bytes(final)
    out_record = {
        "classification": "MUTABLE_SOURCE_CANDIDATE; CAPTURE ONLY",
        "specialization": "T = *mut Element; Element unrestricted",
        "source_order": record.get("source_order", []),
        "original_sha256": sha(original),
        "verified_sha256": sha(final),
        "ghost_strip_identity": True,
        "stages": stages,
        "provider": provider,
        "required_future_capture": [
            "fresh verified/original source identities",
            "NORMAL and readonly typed MIR complete unit/body hashes",
            "source/unit/body/snapshot pins and exact ordered ghost inventory",
        ],
        "translator_admission": "NOT_IMPLEMENTED",
        "helper_proof_status": "NOT_RUN",
        "publication_status": "NOT_PUBLISHED",
        "proof_credit": 0,
    }
    (output_dir / "fixture.json").write_text(json.dumps(
        out_record, indent=2, sort_keys=True) + "\n")
    return out_record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True,
                        help="already prepared full-unit original/verified pair")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(write_candidate(args.input, args.out),
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
