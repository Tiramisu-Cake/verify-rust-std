#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Prepare the actual owner fixture with the separately certified S6 callees.

Source-only preparation. It installs no admission rule and never claims an
actual helper, nested Drop, or SAFE forget proof.
"""

from __future__ import annotations

import argparse
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
        raise RuntimeError(f"missing {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


OWNER = load(HERE / "prepare-actual-owner-projection.py",
             "linked_actual_owner_source")
LINK = load(REPO / "research/challenge-8/overnight-linkage/"
            "check-intrinsic-drop-linkage.py", "linked_actual_s6_source")


def write_case(repo: Path, out: Path, *, owner_safety_proof: bool = True,
               annotate_nested_drop: bool = True,
               safety_proof_variant: str = "positive",
               owner_literal: bool = False) -> dict:
    OWNER.require((os.environ.get("GITHUB_ACTIONS"),
                   os.environ.get("RUNNER_ENVIRONMENT"),
                   os.environ.get("RUNNER_OS")) ==
                  ("true", "github-hosted", "Linux"),
                  "linked owner source requires GitHub-hosted Linux")
    OWNER.require(repo.resolve() == REPO.resolve() and not out.exists(),
                  "linked owner repository/evidence identity changed")
    out.mkdir(parents=True)
    captured = out / "actual-baseline"
    OWNER.ACTUAL.write_fixture(repo, captured)
    actual_body, actual_cert = OWNER.ACTUAL.source_certificate(repo)
    ctor_cert = LINK.CONSTRUCTOR.certify_repository_sources(repo)
    asptr_adapter, asptr_cert, _ = LINK.ASPTR_LINK.adapter_source(
        out, "positive", LINK.CONSTRUCTOR)
    drop_body, drop_cert = LINK.DROP_SOURCE.source_certificate(
        repo, LINK.CONSTRUCTOR)
    intrinsic_cert = LINK.INTRINSIC.source_certificate(repo, LINK.CONSTRUCTOR)
    canonical = LINK.canonical_actual_contract(
        (captured / "verified/lib.rs").read_bytes())
    linked = out / "linked-s6-base"
    linked_record = LINK.make_case(canonical, actual_body, ctor_cert,
                                   asptr_adapter, drop_body, linked,
                                   "pointer_drop")
    base_verified = (linked / "verified/lib.rs").read_bytes()
    # The established LINK fixture strips block annotations while retaining
    # their blank lines. The owner preparer strips the complete annotation
    # lines. Use one deterministic strip on both sides of this projection;
    # executable tokens and the pinned actual body remain byte-identical.
    base_original = OWNER.strip_ghost(base_verified)
    OWNER.require(actual_body in base_original and
                  (linked / "original/lib.rs").read_bytes().split() ==
                  base_original.split(),
                  "linked base executable tokens changed by strip convention")
    verified = OWNER.candidate(
        base_verified, base_original, owner_safety_proof=owner_safety_proof,
        safety_proof_variant=safety_proof_variant,
        owner_literal=owner_literal,
        annotate_nested_drop=annotate_nested_drop)
    case = out / "linked-owner"
    (case / "original").mkdir(parents=True)
    (case / "verified").mkdir()
    (case / "original/lib.rs").write_bytes(base_original)
    (case / "verified/lib.rs").write_bytes(verified)
    OWNER.require(OWNER.strip_ghost(verified) == base_original and
                  verified.count(actual_body) == 0 and
                  base_original.count(actual_body) == 1,
                  "linked actual owner runtime/source identity changed")
    record = {
        "classification": "SOURCE_ONLY_FULL_S6_LINKAGE_CANDIDATE",
        "actual_helper_proved": False,
        "actual_nested_drop_proved": False,
        "actual_safe_forget_linked": False,
        "stock_s6_gate_admitted": False,
        "full_source_admission_needed": True,
        "owner_safety_proof": owner_safety_proof,
        "safety_proof_variant": safety_proof_variant,
        "owner_literal": owner_literal,
        "safety_proof_source": (
            OWNER.SAFETY_PROOFS[safety_proof_variant].decode()
            if owner_safety_proof else None),
        "actual_nested_drop_annotated": annotate_nested_drop,
        "original_sha256": OWNER.ACTUAL.digest(base_original),
        "verified_sha256": OWNER.ACTUAL.digest(verified),
        "ghost_strip_identity": True,
        "actual_source_certificate": actual_cert,
        "constructor_source_certificate": ctor_cert,
        "as_mut_ptr_source_certificate": asptr_cert,
        "intrinsic_source_certificate": intrinsic_cert,
        "pointer_drop_source_certificate": drop_cert,
        "linked_s6_source_record": linked_record,
        "local_callees_required": [
            "sort4_certified_maybeuninit::sort4_checked_maybeuninit_new",
            "sort4_checked_as_mut_ptr", "sort4_checked_pointer_drop"],
    }
    (case / "fixture.json").write_text(json.dumps(
        record, indent=2, sort_keys=True) + "\n")
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--without-safety-proof", action="store_true")
    parser.add_argument("--without-nested-drop-opens", action="store_true")
    parser.add_argument("--outcome-safety-proof", action="store_true",
                        help="source-only fn_outcome_result projection")
    args = parser.parse_args()
    print(json.dumps(write_case(
        args.repo, args.out,
        owner_safety_proof=not args.without_safety_proof,
        annotate_nested_drop=not args.without_nested_drop_opens,
        safety_proof_variant=(
            "outcome_result" if args.outcome_safety_proof else "positive")),
        indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
