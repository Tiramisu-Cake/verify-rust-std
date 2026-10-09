#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Cloud-only source-only wrapper-owner rebase, separate from canonical O26."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
CASE_NAME = "nine-body-wrapper-rebase"
CANONICAL_SOURCE = "1798132ff7a1585db7367779365c88e5ef5f417adcff0bf82779bf6a674945e6"
CANONICAL_ORIGINAL = "466882d74de217766ed8d5c583596c173df47f0e6bd40da7cb1a4c931d7265a5"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"missing canonical preparer: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BASE = load(HERE / "prepare.py", "o26_canonical_prepare_for_rebase")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


BEFORE_OPEN = (
    b"    /*@ std::mem::open_MaybeUninit::<*Element>(true_ptr as *std::mem::MaybeUninit<*Element>); @*/\n"
)
BEFORE_FINAL = (
    b"        // Note that it is important to use the values here. Reading from the pointer we got makes\n"
)
SAVE_OLD = b"""    /*@ assert *(true_ptr as *std::mem::MaybeUninit<*Element>) |-> ?old_true_wrapper &*&
        std::mem::MaybeUninit_pointer_own::<Element>()(t, old_true_wrapper); @*/
    /*@ assert *(false_ptr as *std::mem::MaybeUninit<*Element>) |-> ?old_false_wrapper &*&
        std::mem::MaybeUninit_pointer_own::<Element>()(t, old_false_wrapper); @*/
"""
REBASE_BOTH = b"""        /*@ assert *(true_ptr as *std::mem::MaybeUninit<*Element>) |-> ?current_true_wrapper; @*/
        /*@ assert *(false_ptr as *std::mem::MaybeUninit<*Element>) |-> ?current_false_wrapper; @*/
        /*@ open std::mem::MaybeUninit_pointer_own::<Element>()(t, old_true_wrapper); @*/
        /*@ match std::mem::MaybeUninit::inner(old_true_wrapper) {
            none => {}
            some(p) => { open raw_ptr_own::<Element>()(t, p); }
        } @*/
        /*@ open std::mem::MaybeUninit_pointer_own::<Element>()(t, old_false_wrapper); @*/
        /*@ match std::mem::MaybeUninit::inner(old_false_wrapper) {
            none => {}
            some(p) => { open raw_ptr_own::<Element>()(t, p); }
        } @*/
        /*@ std::mem::close_MaybeUninit_pointer_own::<Element>(t, current_true_wrapper); @*/
        /*@ std::mem::close_MaybeUninit_pointer_own::<Element>(t, current_false_wrapper); @*/
"""


def write_case(repo: Path, out: Path) -> dict:
    provider = load(repo / "research/challenge-8/cloud-build/provider.py",
                    "o26_wrapper_rebase_provider")
    provider.require_supported_provider()
    BASE.require(repo.resolve() == REPO.resolve() and not out.exists(),
                 "wrapper rebase repository/evidence identity changed")
    out.mkdir(parents=True)
    canonical_root = out / "canonical-source"
    canonical = BASE.write_case(repo, canonical_root)
    old_case = canonical_root / BASE.CASE_NAME
    before = (old_case / "verified/lib.rs").read_bytes()
    original = (old_case / "original/lib.rs").read_bytes()
    BASE.require(sha(before) == canonical["verified_sha256"] == CANONICAL_SOURCE and
                 sha(original) == canonical["original_sha256"] == CANONICAL_ORIGINAL and
                 canonical["ghost_strip_identity"] is True and
                 canonical["source_order"] == list(BASE.ORDER),
                 "canonical O26 source pair differs")
    BASE.require(before.count(BEFORE_OPEN) == before.count(BEFORE_FINAL) == 1 and
                 before.index(BEFORE_OPEN) < before.index(BEFORE_FINAL) and
                 all(block not in before for block in (SAVE_OLD, REBASE_BOTH)),
                 "wrapper rebase insertion boundary changed")
    after = before.replace(BEFORE_OPEN, SAVE_OLD + BEFORE_OPEN, 1)
    after = after.replace(BEFORE_FINAL, REBASE_BOTH + BEFORE_FINAL, 1)
    BASE.require(after != before and
                 after.replace(SAVE_OLD, b"", 1).replace(REBASE_BOTH, b"", 1) == before and
                 after.count(SAVE_OLD) == after.count(REBASE_BOTH) == 1 and
                 BASE.SEVEN.OWNER.OWNER.strip_ghost(after) == original,
                 "wrapper rebase changed runtime or more than two ghost blocks")
    case = out / CASE_NAME
    (case / "verified").mkdir(parents=True)
    (case / "original").mkdir()
    (case / "verified/lib.rs").write_bytes(after)
    (case / "original/lib.rs").write_bytes(original)
    record = {
        "classification": "O26_WRAPPER_REBASE_SOURCE_ONLY_CAPTURE_NOT_PROOF",
        "case_name": CASE_NAME,
        "canonical_case": str(old_case.relative_to(out)),
        "canonical_verified_sha256": CANONICAL_SOURCE,
        "verified_sha256": sha(after),
        "original_sha256": sha(original),
        "ghost_strip_identity": True,
        "source_order": list(BASE.ORDER),
        "inserted_ghost_blocks": [
            {"name": "save_two_old_wrapper_owners", "sha256": sha(SAVE_OLD),
             "before": BEFORE_OPEN.decode().strip()},
            {"name": "consume_old_restore_current", "sha256": sha(REBASE_BOTH),
             "before": BEFORE_FINAL.decode().strip()},
        ],
        "verified_source_reversible_two_insertions": True,
        "actual_runtime_unchanged": True,
        "full_mir_refinement_and_proof": "NOT_RUN",
        "old_certificate_expected_to_refuse": True,
        "semantic_frontend_enabled": False,
        "verification_accepted": False,
    }
    for path in (case / "fixture.json", out / "source-summary.json"):
        path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    return record


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    print(json.dumps(write_case(args.repo, args.out), indent=2, sort_keys=True),
          flush=True)


if __name__ == "__main__":
    main()
