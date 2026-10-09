#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Cloud-only source diagnostic for the selected input-pointer equality."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
CASE_NAME = "nine-body-wrapper-input-relation"
R2_SOURCE = "11067f06ba7c745cfb221a559fb29778eba8d7b6e65f6db1a814ff7ce72bdfd4"
ORIGINAL_SOURCE = "466882d74de217766ed8d5c583596c173df47f0e6bd40da7cb1a4c931d7265a5"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"missing source preparer: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


R2 = load(HERE / "prepare-wrapper-rebase.py", "o26_wrapper_rebase_for_input_relation")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


SHADOW_ANCHOR = b"    let mut true_val = MaybeUninit::new(true_val);\n"
PAYLOAD_ANCHOR = b"    /*@ assert *false_ptr |-> ?false_payload; @*/\n"
FINAL_CLOSE_ANCHOR = (
    b"        /*@ std::mem::close_MaybeUninit_pointer_own::<Element>(t, current_false_wrapper); @*/\n"
)

INPUT_BINDINGS = (
    ("save_true_input", b"/*@ let saved_true_input = true_val; @*/"),
    ("save_false_input", b"/*@ let saved_false_input = false_val; @*/"),
)
PAYLOAD_ASSERTIONS = (
    ("true_payload_matches_input", b"    /*@ assert true_payload == saved_true_input; @*/\n"),
    ("false_payload_matches_input", b"    /*@ assert false_payload == saved_false_input; @*/\n"),
)
FINAL_ASSERTIONS = (
    ("current_true_wrapper_matches_input",
     b"        /*@ assert std::mem::MaybeUninit::inner(current_true_wrapper) == some(saved_true_input); @*/\n"),
    ("current_false_wrapper_matches_input",
     b"        /*@ assert std::mem::MaybeUninit::inner(current_false_wrapper) == some(saved_false_input); @*/\n"),
    ("shadow_true_wrapper_matches_input",
     b"        /*@ assert std::mem::MaybeUninit::inner(true_val) == some(saved_true_input); @*/\n"),
    ("shadow_false_wrapper_matches_input",
     b"        /*@ assert std::mem::MaybeUninit::inner(false_val) == some(saved_false_input); @*/\n"),
    ("conditional_wrapper_matches_input",
     b"        /*@ assert std::mem::MaybeUninit::inner(if condition { true_val } else { false_val }) == some(if condition { saved_true_input } else { saved_false_input }); @*/\n"),
)
REGIONS = (
    ("before_rust_shadow", INPUT_BINDINGS),
    ("after_opened_payloads", PAYLOAD_ASSERTIONS),
    ("after_rebased_wrapper_closes", FINAL_ASSERTIONS),
)


def source_span(source: bytes, fragment: bytes) -> dict:
    R2.BASE.require(source.count(fragment) == 1, "inserted ghost fragment absent or repeated")
    start = source.index(fragment)
    end = start + len(fragment)
    line_start = source.rfind(b"\n", 0, start) + 1
    end_line_start = source.rfind(b"\n", 0, end) + 1
    return {
        "byte_start": start,
        "byte_end_exclusive": end,
        "line_start_one_based": source.count(b"\n", 0, start) + 1,
        "column_start_zero_based": start - line_start,
        "line_end_one_based": source.count(b"\n", 0, end) + 1,
        "column_end_zero_based": end - end_line_start,
        "bytes": len(fragment),
        "sha256": sha(fragment),
    }


def write_case(repo: Path, out: Path) -> dict:
    provider = load(repo / "research/challenge-8/cloud-build/provider.py",
                    "o26_input_relation_provider")
    provider.require_supported_provider()
    R2.BASE.require(repo.resolve() == REPO.resolve() and not out.exists(),
                    "input-relation repository/evidence identity changed")
    out.mkdir(parents=True)
    parent_root = out / "r2-source"
    parent = R2.write_case(repo, parent_root)
    parent_case = parent_root / R2.CASE_NAME
    before = (parent_case / "verified/lib.rs").read_bytes()
    original = (parent_case / "original/lib.rs").read_bytes()
    R2.BASE.require(
        sha(before) == parent["verified_sha256"] == R2_SOURCE and
        sha(original) == parent["original_sha256"] == ORIGINAL_SOURCE and
        parent["ghost_strip_identity"] is True and
        parent["verified_source_reversible_two_insertions"] is True and
        parent["source_order"] == list(R2.BASE.ORDER),
        "exact R2 source pair or certificate differs",
    )

    anchors = (SHADOW_ANCHOR, PAYLOAD_ANCHOR, FINAL_CLOSE_ANCHOR)
    regions = tuple(b"".join(comment for _, comment in rows)
                    for _, rows in REGIONS)
    comments = tuple(comment for _, rows in REGIONS for _, comment in rows)
    R2.BASE.require(
        all(before.count(anchor) == 1 for anchor in anchors) and
        list(map(before.index, anchors)) == sorted(map(before.index, anchors)) and
        all(before.count(region) == 0 for region in regions) and
        all(before.count(comment) == 0 and comment.count(b"/*@") == 1 and
            comment.count(b"@*/") == 1 and
            comment.endswith(b"@*/" if index < 2 else b"@*/\n")
            for index, comment in enumerate(comments)),
        "input-relation insertion boundary or command inventory changed",
    )
    after = before.replace(SHADOW_ANCHOR, regions[0] + SHADOW_ANCHOR, 1)
    after = after.replace(PAYLOAD_ANCHOR, PAYLOAD_ANCHOR + regions[1], 1)
    after = after.replace(FINAL_CLOSE_ANCHOR, FINAL_CLOSE_ANCHOR + regions[2], 1)
    restored = after
    for region in regions:
        restored = restored.replace(region, b"", 1)
    R2.BASE.require(
        after != before and restored == before and
        all(after.count(region) == 1 for region in regions) and
        all(after.count(comment) == 1 for comment in comments) and
        R2.BASE.SEVEN.OWNER.OWNER.strip_ghost(after) == original and
        sha(original) == ORIGINAL_SOURCE and
        before.count(b"crate::intrinsics::select_unpredictable(") ==
        after.count(b"crate::intrinsics::select_unpredictable(") == 3 and
        before.count(b"crate::mem::forget(guard);") ==
        after.count(b"crate::mem::forget(guard);") == 1 and
        before.count(b".assume_init()") == after.count(b".assume_init()") == 1,
        "input-relation candidate changed runtime or inserted ghost regions",
    )

    region_records = []
    comment_records = []
    for index, ((region_name, rows), region) in enumerate(zip(REGIONS, regions)):
        region_records.append({"index": index, "name": region_name,
                               **source_span(after, region)})
        for comment_name, comment in rows:
            comment_records.append({
                "index": len(comment_records), "name": comment_name,
                "region": region_name, "utf8": comment.decode(),
                **source_span(after, comment),
            })
    R2.BASE.require(
        len(region_records) == 3 and len(comment_records) == 9 and
        [row["byte_start"] for row in region_records] ==
        sorted(row["byte_start"] for row in region_records) and
        [row["byte_start"] for row in comment_records] ==
        sorted(row["byte_start"] for row in comment_records),
        "input-relation source certificate ordering changed",
    )

    case = out / CASE_NAME
    (case / "verified").mkdir(parents=True)
    (case / "original").mkdir()
    (case / "verified/lib.rs").write_bytes(after)
    (case / "original/lib.rs").write_bytes(original)
    record = {
        "classification": "SOURCE_ONLY_WRAPPER_INPUT_RELATION_DIAGNOSTIC_NOT_ACCEPTED",
        "case_name": CASE_NAME,
        "parent_case": str(parent_case.relative_to(out)),
        "parent_verified_sha256": R2_SOURCE,
        "verified_sha256": sha(after),
        "original_sha256": sha(original),
        "ghost_strip_identity": True,
        "source_order": list(R2.BASE.ORDER),
        "inserted_ghost_regions": region_records,
        "inserted_ghost_comments": comment_records,
        "verified_source_reversible_three_input_relation_insertions": True,
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(write_case(args.repo, args.out), indent=2, sort_keys=True),
          flush=True)


if __name__ == "__main__":
    main()
