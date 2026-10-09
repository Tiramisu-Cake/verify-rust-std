#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Blocked Cloud-only source revision for exact R3 Rust-shadow ghost bindings."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
CASE_NAME = "nine-body-wrapper-input-relation-shadow"
PROFILE = HERE / "O26-WRAPPER-INPUT-RELATION-SHADOW-DRAFT.json"


def need(ok: bool, why: str) -> None:
    if not ok:
        raise RuntimeError(why)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def reviewed_profile() -> tuple[dict, dict[str, str]]:
    profile = json.loads(PROFILE.read_text())
    need(profile.get("status") == "REVIEWED_SOURCE_ONLY_SHADOW_BINDING" and
         profile.get("verification_accepted") is False and
         profile.get("parent_case") == "nine-body-wrapper-input-relation" and
         re.fullmatch(r"[0-9a-f]{64}",
                      str(profile.get("parent_verified_sha256"))) is not None and
         profile.get("original_sha256") ==
             "466882d74de217766ed8d5c583596c173df47f0e6bd40da7cb1a4c931d7265a5",
         "shadow source revision is blocked until the fresh capture is reviewed")
    normal = profile.get("reviewed_normal_shadow_internal_names")
    readonly = profile.get("reviewed_readonly_shadow_internal_names")
    need(isinstance(normal, dict) and normal == readonly and
         set(normal) == {"true_val", "false_val"} and
         all(isinstance(internal, str) and
             re.fullmatch(surface + r"_[1-9][0-9]*", internal) is not None
             for surface, internal in normal.items()) and
         len(set(normal.values())) == 2,
         "NORMAL/readonly observed shadow-local names are absent or differ")
    return profile, normal


def revised_comments(parent, names: dict[str, str]) -> tuple[dict[str, bytes], tuple]:
    old = dict(parent.FINAL_ASSERTIONS)
    need(set(old) == {
        "current_true_wrapper_matches_input",
        "current_false_wrapper_matches_input",
        "shadow_true_wrapper_matches_input",
        "shadow_false_wrapper_matches_input",
        "conditional_wrapper_matches_input",
    }, "parent R3 nine-command inventory changed")
    true_name = names["true_val"].encode()
    false_name = names["false_val"].encode()
    changed = {
        "shadow_true_wrapper_matches_input": old[
            "shadow_true_wrapper_matches_input"].replace(
                b"inner(true_val)", b"inner(" + true_name + b")"),
        "shadow_false_wrapper_matches_input": old[
            "shadow_false_wrapper_matches_input"].replace(
                b"inner(false_val)", b"inner(" + false_name + b")"),
        "conditional_wrapper_matches_input": old[
            "conditional_wrapper_matches_input"].replace(
                b"{ true_val }", b"{ " + true_name + b" }").replace(
                b"{ false_val }", b"{ " + false_name + b" }"),
    }
    need(all(changed[key] != old[key] and changed[key].count(b"/*@") == 1 and
             changed[key].count(b"@*/") == 1 and
             changed[key].endswith(b"@*/\n")
             for key in changed) and
         old["shadow_true_wrapper_matches_input"].count(b"inner(true_val)") == 1 and
         old["shadow_false_wrapper_matches_input"].count(b"inner(false_val)") == 1 and
         old["conditional_wrapper_matches_input"].count(b"{ true_val }") == 1 and
         old["conditional_wrapper_matches_input"].count(b"{ false_val }") == 1,
         "three exact late ghost substitutions differ")
    rows = tuple((region, tuple((name, changed.get(name, comment))
                               for name, comment in commands))
                 for region, commands in parent.REGIONS)
    need(len(rows) == 3 and sum(len(commands) for _, commands in rows) == 9,
         "parent R3 ghost region inventory changed")
    return changed, rows


def write_case(repo: Path, out: Path) -> dict:
    profile, names = reviewed_profile()  # Current DRAFT refuses before writing.
    from importlib import util
    spec = util.spec_from_file_location("o26_parent_input_relation", HERE /
                                        "prepare-wrapper-input-relation.py")
    need(spec is not None and spec.loader is not None,
         "parent input-relation preparer absent")
    parent = util.module_from_spec(spec)
    spec.loader.exec_module(parent)
    provider = parent.load(repo / "research/challenge-8/cloud-build/provider.py",
                           "o26_input_relation_shadow_provider")
    provider.require_supported_provider()
    need(repo.resolve() == REPO.resolve() and not out.exists(),
         "shadow-revision repository/evidence identity changed")
    out.mkdir(parents=True)
    parent_root = out / "parent-r3-source"
    parent_record = parent.write_case(repo, parent_root)
    parent_case = parent_root / parent.CASE_NAME
    before = (parent_case / "verified/lib.rs").read_bytes()
    original = (parent_case / "original/lib.rs").read_bytes()
    need(sha(before) == parent_record.get("verified_sha256") ==
         profile["parent_verified_sha256"] and
         sha(original) == parent_record.get("original_sha256") ==
         profile["original_sha256"] and
         parent_record.get("ghost_strip_identity") is True and
         parent_record.get("verified_source_reversible_three_input_relation_insertions") is True and
         parent_record.get("classification") ==
             "SOURCE_ONLY_WRAPPER_INPUT_RELATION_DIAGNOSTIC_NOT_ACCEPTED",
         "observed parent R3 source pair differs")

    changed, regions = revised_comments(parent, names)
    old = dict(parent.FINAL_ASSERTIONS)
    after = before
    for name in changed:
        need(after.count(old[name]) == 1 and after.count(changed[name]) == 0,
             f"{name}: old/new ghost occurrence differs")
        after = after.replace(old[name], changed[name], 1)
    restored = after
    for name in changed:
        restored = restored.replace(changed[name], old[name], 1)
    need(after != before and restored == before and
         parent.R2.BASE.SEVEN.OWNER.OWNER.strip_ghost(after) == original and
         before.count(b"crate::intrinsics::select_unpredictable(") ==
         after.count(b"crate::intrinsics::select_unpredictable(") == 3 and
         before.count(b"crate::mem::forget(guard);") ==
         after.count(b"crate::mem::forget(guard);") == 1 and
         before.count(b".assume_init()") == after.count(b".assume_init()") == 1,
         "shadow revision changed runtime or more than three late ghost comments")

    region_records = []
    comment_records = []
    for index, (region_name, commands) in enumerate(regions):
        region = b"".join(comment for _, comment in commands)
        region_records.append({"index": index, "name": region_name,
                               **parent.source_span(after, region)})
        for name, comment in commands:
            comment_records.append({"index": len(comment_records), "name": name,
                                    "region": region_name, "utf8": comment.decode(),
                                    **parent.source_span(after, comment)})
    need(len(region_records) == 3 and len(comment_records) == 9 and
         [row["name"] for row in comment_records] ==
         [name for _, commands in parent.REGIONS for name, _ in commands] and
         [row["byte_start"] for row in comment_records] ==
         sorted(row["byte_start"] for row in comment_records),
         "shadow-revised ghost order differs")

    case = out / CASE_NAME
    (case / "verified").mkdir(parents=True)
    (case / "original").mkdir()
    (case / "verified/lib.rs").write_bytes(after)
    (case / "original/lib.rs").write_bytes(original)
    record = {
        "classification": "SOURCE_ONLY_SHADOW_BINDING_REVISION_NOT_ACCEPTED",
        "case_name": CASE_NAME,
        "parent_case": str(parent_case.relative_to(out)),
        "parent_verified_sha256": profile["parent_verified_sha256"],
        "verified_sha256": sha(after),
        "original_sha256": sha(original),
        "ghost_strip_identity": True,
        "source_order": parent_record["source_order"],
        "inserted_ghost_regions": region_records,
        "inserted_ghost_comments": comment_records,
        "changed_late_comment_names": sorted(changed),
        "shadow_internal_names": names,
        "verified_source_reversible_three_late_comment_substitutions": True,
        "actual_runtime_unchanged": True,
        "full_mir_refinement_and_proof": "NOT_RUN",
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
