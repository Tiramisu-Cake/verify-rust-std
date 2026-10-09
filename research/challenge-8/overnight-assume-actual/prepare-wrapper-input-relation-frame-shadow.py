#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Cloud-only late ghost-name revision of the exact FRAME source candidate."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
CASE_NAME = "nine-body-wrapper-input-relation-frame-shadow"
PROFILE = HERE / "O26-WRAPPER-INPUT-RELATION-FRAME-SHADOW-SOURCE.json"
FRAME_SOURCE = "8543e99940897e3289f9f57fe3edc30fa4cffbba713b68aab36eb49d3faac816"
ORIGINAL = "466882d74de217766ed8d5c583596c173df47f0e6bd40da7cb1a4c931d7265a5"
FRAME_PROFILE = HERE / "O26-R3-FRAME-TEST.json"
FRAME_TRANSLATOR = "a8421aac6bc2863e6df8d5ca9fc94b15251123f5203cf92d271529a595bad243"
OBSERVED_BINDINGS = {
    "normal": {
        "true_val": {"input": "_2", "wrapper": "_6", "input_span": [137, 4, 12],
                     "wrapper_span": [155, 154, 166]},
        "false_val": {"input": "_3", "wrapper": "_8", "input_span": [138, 4, 13],
                      "wrapper_span": [156, 8, 21]},
    },
    "readonly": {
        "true_val": {"input": "_2", "wrapper": "_4", "input_span": [137, 4, 12],
                     "wrapper_span": [155, 90, 102]},
        "false_val": {"input": "_3", "wrapper": "_6", "input_span": [138, 4, 13],
                      "wrapper_span": [156, 8, 21]},
    },
}


def need(ok: bool, why: str) -> None:
    if not ok:
        raise RuntimeError(why)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, f"missing FRAME source dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def reviewed_bindings() -> tuple[dict, dict[str, str]]:
    profile = json.loads(PROFILE.read_text())
    parent_profile = json.loads(FRAME_PROFILE.read_text())
    normal = profile.get("reviewed_normal_shadow_internal_names")
    readonly = profile.get("reviewed_readonly_shadow_internal_names")
    exact = {"true_val": "true_val_1", "false_val": "false_val_1"}
    need(profile.get("status") == "REVIEWED_SOURCE_ONLY_FRAME_SHADOW_BINDING" and
         profile.get("verification_accepted") is False and profile.get("accepted") is False and
         profile.get("parent_verified_sha256") == FRAME_SOURCE and
         profile.get("original_sha256") == ORIGINAL and
         profile.get("parent_case") == "nine-body-wrapper-input-relation-frame" and
         profile.get("parent_translator_sha256") == FRAME_TRANSLATOR and
         profile.get("observed_bindings") == OBSERVED_BINDINGS and
         profile.get("runtime_unchanged") is True and
         profile.get("target_posts_unchanged") is True and
         parent_profile.get("classification") == "EXPERIMENTAL_O26_R3_FRAME_TEST_NOT_ACCEPTED" and
         parent_profile.get("test_translator_sha256") == FRAME_TRANSLATOR and
         parent_profile.get("source", {}).get("verified_sha256") == FRAME_SOURCE and
         parent_profile.get("source", {}).get("original_sha256") == ORIGINAL and
         normal == readonly == exact,
         "FRAME-shadow capture pins or observed NORMAL/readonly bindings differ")
    return profile, exact


def late_comments(frame, names: dict[str, str]) -> tuple[dict[str, bytes], tuple]:
    old = dict(frame.INPUT.FINAL_ASSERTIONS)
    expected = {"current_true_wrapper_matches_input", "current_false_wrapper_matches_input",
                "shadow_true_wrapper_matches_input", "shadow_false_wrapper_matches_input",
                "conditional_wrapper_matches_input"}
    need(set(old) == expected, "FRAME parent final ghost assertion inventory changed")
    true_name, false_name = names["true_val"].encode(), names["false_val"].encode()
    changed = {
        "shadow_true_wrapper_matches_input": old["shadow_true_wrapper_matches_input"].replace(
            b"inner(true_val)", b"inner(" + true_name + b")"),
        "shadow_false_wrapper_matches_input": old["shadow_false_wrapper_matches_input"].replace(
            b"inner(false_val)", b"inner(" + false_name + b")"),
        "conditional_wrapper_matches_input": old["conditional_wrapper_matches_input"].replace(
            b"{ true_val }", b"{ " + true_name + b" }").replace(
            b"{ false_val }", b"{ " + false_name + b" }"),
    }
    need(all(changed[key] != old[key] and changed[key].count(b"/*@") == 1 and
             changed[key].count(b"@*/") == 1 and changed[key].endswith(b"@*/\n")
             for key in changed) and
         old["shadow_true_wrapper_matches_input"].count(b"inner(true_val)") == 1 and
         old["shadow_false_wrapper_matches_input"].count(b"inner(false_val)") == 1 and
         old["conditional_wrapper_matches_input"].count(b"{ true_val }") == 1 and
         old["conditional_wrapper_matches_input"].count(b"{ false_val }") == 1,
         "exact three late FRAME ghost substitutions differ")
    regions = tuple((region, tuple((name, changed.get(name, comment))
                                  for name, comment in commands))
                    for region, commands in frame.INPUT.REGIONS)
    need(len(regions) == 3 and sum(len(rows) for _, rows in regions) == 9,
         "FRAME source command inventory changed")
    return changed, regions


def write_case(repo: Path, out: Path) -> dict:
    profile, names = reviewed_bindings()
    frame = load(HERE / "prepare-wrapper-input-relation-frame.py", "frame_shadow_parent")
    need(repo.resolve() == REPO.resolve() and not out.exists(),
         "FRAME-shadow repository/evidence identity changed")
    out.mkdir(parents=True)
    parent_root = out / "parent-frame-source"
    parent_record = frame.write_case(repo, parent_root)
    parent_case = parent_root / frame.CASE_NAME
    before = (parent_case / "verified/lib.rs").read_bytes()
    original = (parent_case / "original/lib.rs").read_bytes()
    need(sha(before) == parent_record.get("verified_sha256") == FRAME_SOURCE and
         sha(original) == parent_record.get("original_sha256") == ORIGINAL and
         parent_record.get("ghost_strip_identity") is True and
         parent_record.get("classification") ==
             "SOURCE_ONLY_THREADONLY_FRAME_CAPTURE_NOT_ACCEPTED" and
         parent_record.get("actual_runtime_unchanged") is True,
         "exact FRAME parent source pair or runtime certificate differs")

    changed, regions = late_comments(frame, names)
    old = dict(frame.INPUT.FINAL_ASSERTIONS)
    after = before
    for name in changed:
        need(after.count(old[name]) == 1 and after.count(changed[name]) == 0,
             f"{name}: parent/revised comment occurrence differs")
        after = after.replace(old[name], changed[name], 1)
    restored = after
    for name in changed:
        restored = restored.replace(changed[name], old[name], 1)
    strip = frame.OWNER.strip_ghost
    need(after != before and restored == before and strip(after) == original and
         sha(original) == ORIGINAL and
         before.count(b"crate::intrinsics::select_unpredictable(") ==
             after.count(b"crate::intrinsics::select_unpredictable(") == 3 and
         before.count(b"crate::mem::forget(guard);") ==
             after.count(b"crate::mem::forget(guard);") == 1 and
         before.count(b".assume_init()") == after.count(b".assume_init()") == 1,
         "FRAME-shadow revision changed runtime or comments outside the exact three substitutions")

    comment_rows, region_rows = [], []
    for index, (region_name, commands) in enumerate(regions):
        region = b"".join(comment for _, comment in commands)
        region_rows.append({"index": index, "name": region_name,
                            **frame.source_span(after, region)})
        for name, comment in commands:
            comment_rows.append({"index": len(comment_rows), "name": name,
                "region": region_name, "utf8": comment.decode(),
                **frame.source_span(after, comment)})
    need(len(comment_rows) == 9 and len(region_rows) == 3 and
         [row["byte_start"] for row in comment_rows] ==
             sorted(row["byte_start"] for row in comment_rows),
         "FRAME-shadow ghost comments are not a complete ordered nine-command source record")

    case = out / CASE_NAME
    (case / "verified").mkdir(parents=True)
    (case / "original").mkdir()
    (case / "verified/lib.rs").write_bytes(after)
    (case / "original/lib.rs").write_bytes(original)
    record = {
        "classification": "SOURCE_ONLY_FRAME_SHADOW_CAPTURE_NOT_ACCEPTED",
        "case_name": CASE_NAME,
        "parent_case": str(parent_case.relative_to(out)),
        "parent_verified_sha256": FRAME_SOURCE,
        "verified_sha256": sha(after),
        "original_sha256": sha(original),
        "ghost_strip_identity": strip(after) == original,
        "source_order": parent_record["source_order"],
        "parent_verified_source_transform": parent_record,
        "inserted_ghost_regions": region_rows,
        "inserted_ghost_comments": comment_rows,
        "changed_late_comment_names": sorted(changed),
        "shadow_internal_names": names,
        "verified_source_reversible_three_late_comment_substitutions": True,
        "actual_runtime_unchanged": True,
        "full_mir_refinement_and_proof": "NOT_RUN",
        "semantic_frontend_enabled": False,
        "verification_accepted": False,
        "accepted": False,
    }
    for path in (case / "fixture.json", out / "source-summary.json"):
        path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(write_case(args.repo, args.out), indent=2, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
