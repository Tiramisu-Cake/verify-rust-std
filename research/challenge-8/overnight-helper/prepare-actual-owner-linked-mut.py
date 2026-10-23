#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Prepare an inactive `*mut Element` S6 owner-linked source candidate.

This parallel source writer calls the mutable fixture writer directly. It may
reuse generic source builders for constructor/as-mut-pointer/drop linkage, but
all emitted `*const Element` fixture types are rewritten by an exact counted
adapter and every reused typed certificate is explicitly downgraded to source
text only. No const helper writer, translator admission, MIR binding, or proof
is reused.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
MUT_WRITER_SHA256 = "803062cd1bb500a600c278d3a03385f27e432b83ca8b0f6a5f141c6754a8a53e"
OWNER_SHA256 = "6680e74fda839501db3c9221f026a3398ce5d903a8134733b6f5375c165afbb8"
PROVIDER_ADAPTER_SHA256 = "04fd1ca82bdbfb7f837a49ed303199024208c85124cf1a45b7893f6d20ed1871"
SOURCE_BUILDER_SHAS = {
    "constructor": "2d4c7f3ee027ae55cb016321d26f59d5ece28cddcc780c10efedb39ed19c3ded",
    "as_mut_ptr": "83759a12cccbcc61b3cd3b5c139102c86ba63404aabd355a78a6d41b247e2082",
    "pointer_drop": "0f09d6c2541c2cfd3f07f790a959501f2c93253d30419f414e8b8258d5f758ae",
    "pointer_drop_source": "f76c562be450e0ee45d71dc776eca00069354a72165c8099f098d04436c0dc45",
    "select_intrinsic": "2ae562b94149fa13a6bc8c1b02cdab66050d8744da9f3fb46ee0eebc6088093b",
}
MUT_SIG = (
    b"pub fn select_unpredictable<Element>(\n"
    b"    condition: bool,\n    true_val: *mut Element,\n"
    b"    false_val: *mut Element,\n) -> *mut Element\n"
)
ACTUAL_MARKER = b"pub fn select_unpredictable<Element>("
CAPTURE_CONTRACT = (
    b"/*@\nreq thread_token(?t) &*& t == currentThread;\n@*/\n"
    b"/*@\nens thread_token(t) &*& (result as pointer) ==\n"
    b"    (if condition { true_val as pointer } else { false_val as pointer });\n@*/\n"
    b"/*@\non_unwind_ens false;\n@*/\n"
)
INTRINSIC_GATE_CONTRACT = (
    b"/*@\nreq thread_token(?t) &*& t == currentThread;\n@*/"
    b"/*@\nens thread_token(t) &*& (result as pointer) ==\n"
    b"        (if condition { true_val as pointer } else { false_val as pointer });\n@*/"
    b"/*@ on_unwind_ens false; @*/\n"
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)


def load(path: Path, name: str, expected_sha: str | None = None):
    raw = path.read_bytes()
    if expected_sha is not None:
        require(sha(raw) == expected_sha, f"pinned source changed: {path.name}")
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None,
            f"source adapter unavailable: {path.name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_modules():
    owner = load(HERE / "prepare-actual-owner-projection.py",
                 "p2_mut_owner_projection_source", OWNER_SHA256)
    writer = load(HERE / "prepare-actual-helper-capture-mut-parallel.py",
                  "p2_mut_source_fixture_writer", MUT_WRITER_SHA256)
    cloud = load(HERE / "mut_source_cloud_provider.py",
                 "p2_mut_cloud_provider_module", PROVIDER_ADAPTER_SHA256)
    s6 = REPO / "research/challenge-8/overnight-s6"
    constructor = load(s6 / "check-maybeuninit-new-pointer.py",
                       "p2_mut_constructor_source", SOURCE_BUILDER_SHAS["constructor"])
    asptr = load(s6 / "check-select-pointer.py", "p2_mut_asptr_source",
                 SOURCE_BUILDER_SHAS["as_mut_ptr"])
    drop = load(s6 / "check-pointer-drop.py", "p2_mut_drop_adapter_source",
                SOURCE_BUILDER_SHAS["pointer_drop"])
    drop_source = load(s6 / "prepare-pointer-drop-diagnostic.py",
                       "p2_mut_drop_source", SOURCE_BUILDER_SHAS["pointer_drop_source"])
    intrinsic = load(s6 / "check-select-pointer-intrinsics.py",
                     "p2_mut_intrinsic_source",
                     SOURCE_BUILDER_SHAS["select_intrinsic"])
    return owner, writer, constructor, asptr, drop, drop_source, intrinsic, cloud


def require_cloud_provider() -> dict:
    module = load(HERE / "mut_source_cloud_provider.py",
                  "p2_mut_owner_cloud_provider", PROVIDER_ADAPTER_SHA256)
    return module.require_cloud_provider()


def rewrite_component(source: bytes, expected_count: int,
                      expected_signature: bytes, label: str) -> tuple[bytes, dict]:
    """Rewrite one source-builder component at a fixed inventory boundary."""
    require(isinstance(source, bytes), f"{label}: source must be bytes")
    require(source.count(b"*const Element") == expected_count,
            f"{label}: expected exactly {expected_count} const Element type sites")
    for unsupported in (b"*const *const Element", b"*const *mut Element",
                       b"*mut *mut Element", b"***const Element",
                       b"***mut Element"):
        require(unsupported not in source,
                f"{label}: unsupported pointer depth/kind: {unsupported.decode()}")
    converted = source.replace(b"*const Element", b"*mut Element")
    require(converted.count(b"*const Element") == 0 and
            converted.count(expected_signature) == 1,
            f"{label}: exact mutable signature or pointer-kind conversion differs")
    return converted, {"source_component": label,
                       "const_element_type_sites": expected_count,
                       "mutable_signature": expected_signature.decode(),
                       "typed_mir_binding_established": False}


def apply_owner_projection(verified: bytes, original: bytes) -> tuple[bytes, dict]:
    owner = load_modules()[0]
    require(verified.count(MUT_SIG) == 1 and b"*const Element" not in verified,
            "owner projection input is not the exact mutable source")
    projected = owner.candidate(verified, original, owner_safety_proof=True,
                                safety_proof_variant="outcome_result",
                                owner_literal=True,
                                annotate_nested_drop=True)
    require(owner.strip_ghost(projected) == original,
            "mutable owner projection changed runtime bytes")
    return projected, {
        "owner_projection_sha256": sha(projected),
        "owner_projection_dependency_sha256": OWNER_SHA256,
        "ghost_strip_identity": True,
        "typed_mir_binding_established": False,
    }


def canonical_actual_contract(source: bytes, constructor) -> bytes:
    require(source.count(CAPTURE_CONTRACT) == 1 and
            source.count(INTRINSIC_GATE_CONTRACT) == 0,
            "mutable capture contract no longer has the reviewed exact bytes")
    def clauses(value: bytes) -> bytes:
        return b" ".join(value.replace(b"/*@", b" ").replace(
            b"@*/", b" ").split())
    require(clauses(CAPTURE_CONTRACT) == clauses(INTRINSIC_GATE_CONTRACT) and
            constructor.strip_ghost_annotations(CAPTURE_CONTRACT).strip() == b"" and
            constructor.strip_ghost_annotations(INTRINSIC_GATE_CONTRACT).strip() == b"",
            "S6 contract conversion changed clauses or crossed ghost boundary")
    canonical = source.replace(CAPTURE_CONTRACT, INTRINSIC_GATE_CONTRACT, 1)
    require(canonical.count(b"req thread_token(?t) &*& t == currentThread;") == 1 and
            canonical.count(b"ens thread_token(t) &*& (result as pointer) ==") == 1 and
            canonical.count(b"on_unwind_ens false;") == 1,
            "canonical full S6 contract clauses changed")
    return canonical


def build_linked_pair(repo: Path, out: Path) -> dict:
    owner, writer, constructor, asptr, drop, drop_source, intrinsic, _ = load_modules()
    provider = require_cloud_provider()
    require(repo.resolve() == REPO.resolve() and not out.exists(),
            "mutable owner-linked repository/output identity changed")
    out.mkdir(parents=True)
    # This call is intentionally to the mutable writer, not its const sibling.
    fixture_dir = out / "mutable-actual-baseline"
    fixture_record = writer.write_fixture(repo, fixture_dir)
    base_verified = (fixture_dir / "verified/lib.rs").read_bytes()
    original = (fixture_dir / "original/lib.rs").read_bytes()
    actual_body, actual_cert = writer.source_certificate(repo)
    require(base_verified.count(MUT_SIG) == 1 and
            owner.strip_ghost(base_verified) == original,
            "mutable base fixture source identity changed")

    ctor_cert = constructor.certify_repository_sources(repo)
    _, ctor_source, ctor_component = constructor.constructor_source(
        ctor_cert, "positive")
    union_body = constructor.extract_braced_item(
        ctor_source, b"mod sort4_certified_maybeuninit")
    ctor_module = b"mod sort4_certified_maybeuninit " + union_body + b"\n"
    require(ctor_source.count(ctor_module) == 1,
            "constructor module differs from its pinned source builder")
    ctor_signature = (
        b"pub fn sort4_checked_maybeuninit_new<Element>(val: *mut Element) "
        b"-> MaybeUninit<*mut Element>")
    ctor_module, ctor_rewrite = rewrite_component(
        ctor_module, 2, ctor_signature, "MaybeUninit constructor module")

    matrix = asptr.load_matrix(repo)
    specialized, asptr_cert = asptr.source_certificate(repo, matrix)
    asptr_contract = (
        b"req thread_token(?t) &*& t == currentThread &*& "
        b"*storage |-> ?value &*& " + asptr.POINTER_OWN + b";\n"
        b"ens thread_token(t) &*& *storage |-> value &*& " +
        asptr.POINTER_OWN + b" &*& "
        b"(result as pointer) == (storage as pointer);\n"
        b"on_unwind_ens false;"
    )
    asptr_adapter = (
        asptr.LOCAL_SIGNATURE.encode() + b"\n" +
        matrix.ghost_block(asptr_contract) + specialized + b"\n")
    asptr_signature = (
        b"pub fn sort4_checked_as_mut_ptr<Element>(storage: &mut "
        b"std::mem::MaybeUninit<*mut Element>) -> *mut *mut Element")
    asptr_adapter, asptr_rewrite = rewrite_component(
        asptr_adapter, 3, asptr_signature, "as_mut_ptr adapter")

    drop_body, drop_cert = drop_source.source_certificate(repo, constructor)
    drop_adapter = drop.helper_source(drop_body, constructor)
    drop_signature = (
        b"pub unsafe fn sort4_checked_pointer_drop<Element>(slot: *mut *mut Element)")
    drop_adapter, drop_rewrite = rewrite_component(
        drop_adapter, 1, drop_signature, "pointer-drop adapter")
    intrinsic_cert = intrinsic.source_certificate(repo, constructor)

    canonical = canonical_actual_contract(base_verified, constructor)
    canonical = constructor.enable_crate_feature(canonical,
                                                  b"transparent_unions")
    require(canonical.count(actual_body) == 1,
            "mutable actual body changed before linkage assembly")
    require(canonical.count(ACTUAL_MARKER) == 1,
            "mutable actual helper insertion boundary changed")
    support = (ctor_module + b"\n" + asptr_adapter + b"\n" +
               drop_adapter + b"\n")
    linked_verified = canonical.replace(ACTUAL_MARKER,
                                        support + ACTUAL_MARKER, 1)
    require(linked_verified.count(MUT_SIG) == 1 and
            b"*const Element" not in linked_verified and
            linked_verified.count(ctor_signature) == 1 and
            linked_verified.count(asptr_signature) == 1 and
            linked_verified.count(drop_signature) == 1 and
            linked_verified.count(actual_body) == 1 and
            linked_verified.count(b"crate::mem::forget(guard);") == 1 and
            linked_verified.count(b"crate::intrinsics::select_unpredictable(") == 3,
            "mutable S6 source assembly/type inventory changed")
    linked_original = owner.strip_ghost(linked_verified)

    projected, owner_stage = apply_owner_projection(linked_verified,
                                                    linked_original)
    final_dir = out / "owner-linked-mut"
    (final_dir / "original").mkdir(parents=True)
    (final_dir / "verified").mkdir()
    (final_dir / "original/lib.rs").write_bytes(linked_original)
    (final_dir / "verified/lib.rs").write_bytes(projected)
    record = {
        "classification": "SOURCE_ONLY_MUTABLE_OWNER_LINKED_CANDIDATE",
        "specialization": "T = *mut Element; Element unrestricted",
        "actual_helper_proved": False,
        "actual_nested_drop_proved": False,
        "actual_safe_forget_linked": False,
        "typed_mir_binding_established": False,
        "translator_admission": "NOT_IMPLEMENTED",
        "helper_proof_status": "NOT_RUN",
        "publication_status": "NOT_PUBLISHED",
        "proof_credit": 0,
        "original_sha256": sha(linked_original),
        "verified_sha256": sha(projected),
        "ghost_strip_identity": owner.strip_ghost(projected) == linked_original,
        "mutable_fixture_writer_sha256": MUT_WRITER_SHA256,
        "const_fixture_writer_loaded": False,
        "provider": provider,
        "source_type_rewrites": [ctor_rewrite, asptr_rewrite, drop_rewrite],
        "owner_stage": owner_stage,
        "actual_body_sha256": sha(actual_body),
        "actual_source_certificate": actual_cert,
        "raw_shared_source_records_for_generation_only": {
            "constructor": ctor_cert,
            "as_mut_ptr": asptr_cert,
            "pointer_drop": drop_cert,
            "select_intrinsic": intrinsic_cert,
            "constructor_component": ctor_component,
        },
        "raw_shared_source_records_admitted_for_mut": False,
    }
    (final_dir / "fixture.json").write_text(json.dumps(
        record, indent=2, sort_keys=True) + "\n")
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build_linked_pair(args.repo, args.out),
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
