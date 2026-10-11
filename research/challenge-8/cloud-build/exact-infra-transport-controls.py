#!/usr/bin/env python3
"""Cloud-only negative controls for an already restored exact recipe archive."""
from __future__ import annotations

import argparse
import copy
import gzip
import importlib.util
import json
import os
from pathlib import Path
import re
import tempfile


ROOT = "research/challenge-8/cloud-build/"
REQUIRED = {
    "o26-r3-ghost-scope-test": (
        "exact-infra-transport-controls.py", "source-input.py", "provider.py",
        "o26-recipe.py", "o26-refresh-audit.py", "o26-refresh-recipe.py",
        "o26-r3-profile.py", "o26-r3-ghost-scope-test.py",
        "o26-wrapper-profile.py", "run-o26-refresh.sh",
        "run-o26-wrapper-r3-profile.sh", "run-o26-r3-ghost-scope-lane.sh",
        "run-o26-r3-ghost-scope-test.sh",
        "recipes/o26-refresh.json", "recipes/o26-r3-ghost-scope-test.json",
        "night-select-sort4/R3-GHOST-SCOPE-TEST-CARD.md",
    ),
    "o26-shadow-generic-sort4-diagnostics": (
        "exact-infra-transport-controls.py", "o26-recipe.py",
        "o26-refresh-audit.py", "o26-refresh-recipe.py", "provider.py",
        "source-input.py", "run-o26-refresh.sh",
        "recipes/o26-refresh.json", "recipes/o26-input-relation-capture.json",
        "recipes/o26-input-relation-shadow-capture.json",
        "recipes/o26-generic-sort4-postmark-diagnostics.json",
        "run-o26-input-relation-shadow-capture.sh",
        "run-o26-generic-sort4-postmark-diagnostics.sh",
        "run-o26-shadow-generic-sort4-diagnostics.sh",
        "run-sort4-postmark-print-test.sh", "sort4-postmark-print-audit.py",
        "actual-sort4-capture.py", "sort4-ast-audit.py",
    ),
    "o26-input-relation-shadow-capture": (
        "exact-infra-transport-controls.py", "o26-recipe.py",
        "o26-refresh-audit.py", "o26-refresh-recipe.py", "provider.py",
        "recipes/o26-refresh.json", "recipes/o26-input-relation-capture.json",
        "source-input.py", "run-o26-refresh.sh",
        "run-o26-input-relation-capture.sh",
        "run-o26-input-relation-shadow-capture.sh",
    ),
    "o26-wrapper-r3-nested-diagnostics": (
        "exact-infra-transport-controls.py", "o26-recipe.py",
        "o26-refresh-audit.py", "o26-refresh-recipe.py", "provider.py",
        "recipes/o26-refresh.json", "recipes/o26-wrapper-input-relation-r3.json",
        "source-input.py", "o26-r3-profile.py", "o26-r3-controls.py", "o26-r3-audit.py",
        "o26-wrapper-profile.py", "run-o26-wrapper-r3-profile.sh", "run-o26-refresh.sh",
        "run-o26-wrapper-r3-nested-diagnostics.sh", "run-o26-r3-nested-order-test.sh",
        "o26-r3-nested-order-test.py", "night-select-sort4/WRAPPER-R3-PROFILE-CARD.md",
    ),
    "o26-generic-sort4-postmark-diagnostics": (
        "exact-infra-transport-controls.py", "o26-recipe.py",
        "o26-refresh-audit.py", "o26-refresh-recipe.py", "provider.py",
        "recipes/o26-refresh.json", "recipes/o26-generic-new-capture.json",
        "source-input.py", "run-o26-refresh.sh",
        "run-o26-generic-sort4-postmark-diagnostics.sh",
        "run-sort4-postmark-print-test.sh", "sort4-postmark-print-audit.py",
        "actual-sort4-capture.py", "sort4-ast-audit.py",
        "night-select-sort4/GENERIC-POSTMARK-DIAGNOSTICS-CARD.md",
    ),
    "o26-wrapper-input-relation-r3": (
        "exact-infra-transport-controls.py", "o26-recipe.py",
        "o26-refresh-audit.py", "o26-refresh-recipe.py", "provider.py",
        "recipes/o26-refresh.json", "source-input.py",
        "o26-r3-profile.py", "o26-r3-controls.py", "o26-r3-audit.py",
        "o26-wrapper-profile.py",
        "run-o26-wrapper-input-relation-r3.sh", "run-o26-wrapper-r3-profile.sh",
        "run-o26-refresh.sh", "night-select-sort4/WRAPPER-R3-PROFILE-CARD.md",
    ),
    "o26-generic-new-capture": (
        "exact-infra-transport-controls.py", "o26-recipe.py",
        "o26-refresh-audit.py", "o26-refresh-recipe.py", "provider.py",
        "recipes/o26-refresh.json",
        "run-o26-generic-new-capture.sh", "run-o26-refresh.sh",
        "source-input.py",
        "night-select-sort4/GENERIC-NEW-CAPTURE-CARD.md",
    ),
    "o26-strict-cut-controls": (
        "cut-relocate-audit.py", "cut-relocate-provider-overlay.py",
        "cut-trace-provider-overlay.py", "exact-infra-transport-controls.py",
        "o26-recipe.py", "o26-refresh-audit.py", "o26-refresh-recipe.py",
        "run-cut-relocate.sh", "run-o26-refresh.sh",
        "run-o26-strict-cut-controls.sh", "run-strict-cut-controls.sh",
        "strict-cut-controls-audit.py",
    ),
    "o26-strict-cut-false-posts": (
        "cut-relocate-audit.py", "cut-relocate-provider-overlay.py",
        "cut-trace-provider-overlay.py", "exact-infra-transport-controls.py",
        "o26-recipe.py", "o26-refresh-audit.py", "o26-refresh-recipe.py",
        "run-cut-relocate.sh", "run-o26-refresh.sh",
        "run-o26-strict-cut-false-posts.sh", "run-strict-cut-controls.sh",
        "strict-cut-controls-audit.py", "run-strict-cut-false-posts.sh",
        "strict-cut-false-posts-prepare.py", "strict-cut-false-posts-capture.py",
        "strict-cut-false-posts-audit.py",
    ),
    "o26-strict-cut-reuse-false-posts": (
        "cut-relocate-audit.py", "cut-relocate-provider-overlay.py",
        "cut-trace-provider-overlay.py", "exact-infra-transport-controls.py",
        "o26-recipe.py", "o26-refresh-audit.py", "o26-refresh-recipe.py",
        "provider.py", "source-input.py", "verify-evidence.py",
        "recipes/o26-refresh.json", "recipes/o26-strict-cut-reuse-false-posts.json",
        "recipes/o26-strict-cut-false-posts.json",
        "run-cut-relocate.sh", "run-o26-refresh.sh",
        "run-o26-strict-cut-reuse-false-posts.sh",
        "run-strict-cut-reuse-controls.sh", "strict-cut-reuse-controls.py",
        "strict-cut-controls-audit.py", "run-strict-cut-false-posts.sh",
        "strict-cut-false-posts-prepare.py", "strict-cut-false-posts-capture.py",
        "strict-cut-false-posts-audit.py",
        "night-select-sort4/STRICT-CUT-REUSE-FALSE-POSTS-CARD.md",
    ),
    "o26-input-relation-capture": (
        "o26-recipe.py", "o26-refresh-audit.py", "o26-refresh-recipe.py",
        "run-o26-input-relation-capture.sh", "run-o26-refresh.sh",
    ),
    "o26-recovery-tests": (
        "actual-sort4-capture.py", "cut-relocate-audit.py",
        "cut-relocate-provider-overlay.py",
        "o26-recipe.py", "o26-refresh-audit.py", "o26-refresh-recipe.py",
        "run-cut-relocate.sh",
        "run-o26-recovery-tests.sh", "run-o26-refresh.sh",
        "run-sort4-ast-probe.sh", "sort4-ast-audit.py",
    ),
    "o26-wrapper-controls": (
        "o26-recipe.py", "o26-refresh-audit.py", "o26-refresh-recipe.py",
        "o26-wrapper-controls-audit.py", "o26-wrapper-profile-a1.py",
        "o26-wrapper-profile-comp19.py", "o26-wrapper-profile.py",
        "run-o26-refresh.sh", "run-o26-wrapper-comp19-test.sh",
        "run-o26-wrapper-controls.sh", "run-o26-wrapper-profile.sh",
    ),
}


def need(condition: bool, why: str) -> None:
    if not condition:
        raise SystemExit(why)


def load_source(path: Path):
    spec = importlib.util.spec_from_file_location("exact_infra_source_input", path)
    need(spec is not None and spec.loader is not None, "restored transport module absent")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def reject(label: str, action, expected: str) -> dict:
    try:
        action()
    except SystemExit as failure:
        reason = str(failure)
        need(reason.startswith(expected), f"{label} refused at unexpected check: {reason}")
        return {"control": label, "refused": True,
                "predicate": expected, "reason": reason}
    raise SystemExit(f"{label} was accepted")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--infra", type=Path, required=True)
    parser.add_argument("--lane", required=True)
    a = parser.parse_args()
    need(re.fullmatch(r"[a-z][a-z0-9-]{0,63}", a.lane) is not None and
         os.environ.get("LANE") == a.lane and
         os.environ.get("SMALLSORT_EXECUTION_PROVIDER") == "cloud-build" and
         not os.environ.get("GITHUB_ACTIONS"), "invalid exact transport control lane/provider")
    need(a.archive == Path("/workspace/evidence/source-input.gz") and
         a.evidence == Path("/workspace/evidence") and
         a.infra == Path("/workspace/infra"), "exact transport paths differ")
    source = load_source(a.infra / ROOT / "source-input.py")
    payload = source.decode_payload(a.archive.read_bytes())
    need(payload.get("schema") == source.SHARED_SCHEMA and
         payload.get("lane") == a.lane, "restored archive schema/lane differs")
    recipe = source.validate_recipe(payload.get("recipe", {}), a.lane)
    need(recipe.get("infra_transport") == source.EXACT_INFRA_TRANSPORT,
         "exact recipe marker absent")
    reviewed = a.lane in REQUIRED
    required = {ROOT + name for name in REQUIRED.get(a.lane, ())}
    required.add(recipe["entrypoint"])
    need(required.issubset(recipe["infra_paths"]),
         "reviewed transitive Cloud runner dependency absent from recipe")
    restored_recipe = json.loads((a.infra / source.RECIPE_PREFIX / (a.lane + ".json")).read_text())
    need(recipe == restored_recipe, "recipe differs from restored committed object")
    if a.lane == "o26-generic-new-capture":
        canonical = source.validate_recipe(json.loads((a.infra / source.RECIPE_PREFIX /
                              "o26-refresh.json").read_text()), "o26-refresh")
        profile = json.loads((Path("/workspace/proof") /
            "research/challenge-8/overnight-assume-actual/O26-REFRESH-PROFILE.json").read_text())
        refresh = {"research/challenge-8/" + row["path"]
                   for row in profile["refresh_patches"]}
        generic = {"research/challenge-8/overnight-generic-select/" + name
                   for name in ("CLOUD-GENERIC-NEW-SOURCE-CARD.md", "SOURCE-PINS.json",
                                "prepare.py", "capture.py")}
        need(set(canonical["proof_paths"]) | refresh | generic <=
             set(recipe["proof_paths"]),
             "generic capture recipe omits canonical or refresh proof dependency")
    if a.lane == "o26-input-relation-shadow-capture":
        parent = source.validate_recipe(json.loads((a.infra / source.RECIPE_PREFIX /
                   "o26-input-relation-capture.json").read_text()),
                   "o26-input-relation-capture")
        shadow = {"research/challenge-8/overnight-assume-actual/" + name for name in
                  ("prepare-wrapper-input-relation-shadow.py",
                   "O26-WRAPPER-INPUT-RELATION-SHADOW-DRAFT.json",
                   "CLOUD-WRAPPER-INPUT-RELATION-SHADOW-CAPTURE-CARD.md",
                   "O26-WRAPPER-INPUT-RELATION-PROFILE.json")}
        need((set(parent["proof_paths"]) | shadow).issubset(recipe["proof_paths"]) and
             set(parent["infra_paths"]).issubset(recipe["infra_paths"]),
             "shadow capture recipe omits input-relation parent or source dependency")
    if a.lane == "o26-shadow-generic-sort4-diagnostics":
        lanes=("o26-input-relation-shadow-capture",
               "o26-generic-sort4-postmark-diagnostics")
        parents=[source.validate_recipe(json.loads((a.infra / source.RECIPE_PREFIX /
                   (lane + ".json")).read_text()), lane) for lane in lanes]
        need(all(set(parent["proof_paths"]).issubset(recipe["proof_paths"]) and
                 set(parent["infra_paths"]).issubset(recipe["infra_paths"])
                 for parent in parents),
             "compound recipe omits shadow or generic/postmark parent closure")
    if a.lane == "o26-generic-sort4-postmark-diagnostics":
        parent = source.validate_recipe(json.loads((a.infra / source.RECIPE_PREFIX /
                         "o26-generic-new-capture.json").read_text()), "o26-generic-new-capture")
        canonical = source.validate_recipe(json.loads((a.infra / source.RECIPE_PREFIX /
                         "o26-refresh.json").read_text()), "o26-refresh")
        profile = json.loads((Path("/workspace/proof/research/challenge-8") /
                        "overnight-assume-actual/O26-REFRESH-PROFILE.json").read_text())
        refresh = {"research/challenge-8/" + row["path"] for row in profile["refresh_patches"]}
        postmark = {"research/challenge-8/" + path for path in
            ("overnight-callback/ACTUAL-SORT4-POSTMARK-PRINT-TEST.json",
             "overnight-callback/verifast-actual-sort4-postmark-print-TEST.patch",
             "overnight-callback/CLOUD-ACTUAL-SORT4-POSTMARK-PRINT-TEST-CARD.md",
             "overnight-sort4/capture.py", "overnight-callback/probe.py",
             "overnight-callback/prepare-actual-sort4-first-call.py",
             "overnight-callback/admit-actual-sort4-first-call.py",
             "overnight-callback/callback-cases.rs", "overnight-callback/join-four-owned-cells.rs")}
        postmark.add("library/core/src/slice/sort/shared/smallsort.rs")
        need((set(parent["proof_paths"]) | set(canonical["proof_paths"]) | refresh | postmark).issubset(recipe["proof_paths"]),
             "combined generic/postmark recipe omits canonical or scenario proof dependency")
    if a.lane in ("o26-wrapper-input-relation-r3", "o26-wrapper-r3-nested-diagnostics"):
        canonical = source.validate_recipe(json.loads((a.infra / source.RECIPE_PREFIX /
                              "o26-refresh.json").read_text()), "o26-refresh")
        proof_root = Path("/workspace/proof/research/challenge-8")
        profile = json.loads((proof_root / "overnight-assume-actual/O26-REFRESH-PROFILE.json").read_text())
        refresh = {"research/challenge-8/" + row["path"] for row in profile["refresh_patches"]}
        r2 = json.loads((proof_root / "overnight-assume-actual/O26-WRAPPER-REBASE-PROFILE.json").read_text())
        r3 = json.loads((proof_root / "overnight-assume-actual/O26-WRAPPER-INPUT-RELATION-PROFILE.json").read_text())
        variants = {"research/challenge-8/" + r2["component23_patch"],
                    "research/challenge-8/" + r3["component24_patch"]}
        variants.update("research/challenge-8/overnight-assume-actual/" + name for name in
                        ("O26-WRAPPER-REBASE-PROFILE.json", "O26-WRAPPER-INPUT-RELATION-PROFILE.json",
                         "prepare-wrapper-rebase.py", "prepare-wrapper-input-relation.py", "capture.py"))
        need((set(canonical["proof_paths"]) | refresh | variants).issubset(recipe["proof_paths"]),
             "R3 recipe omits canonical or profile proof dependency")
    if a.lane == "o26-strict-cut-reuse-false-posts":
        parent = source.validate_recipe(json.loads((a.infra / source.RECIPE_PREFIX /
                   "o26-strict-cut-false-posts.json").read_text()), "o26-strict-cut-false-posts")
        need(set(parent["proof_paths"]).issubset(recipe["proof_paths"]),
             "strict reuse recipe omits canonical or historical matrix proof dependency")
    if a.lane == "o26-wrapper-r3-nested-diagnostics":
        parent = source.validate_recipe(json.loads((a.infra / source.RECIPE_PREFIX /
                   "o26-wrapper-input-relation-r3.json").read_text()), "o26-wrapper-input-relation-r3")
        nested = {"research/challenge-8/overnight-assume-actual/" + name for name in
                  ("O26-R3-NESTED-BEFORE-OUTER-TEST.json", "verifast-r3-nested-before-outer-TEST.patch",
                   "CLOUD-R3-NESTED-BEFORE-OUTER-TEST-CARD.md")}
        need((set(parent["proof_paths"]) | nested).issubset(recipe["proof_paths"]),
             "R3 nested recipe omits parent or TEST proof dependency")
    certificate = json.loads((a.evidence / "source-input-certificate.json").read_text())
    need(certificate.get("lane") == a.lane and certificate.get("recipe") == recipe and
         certificate.get("infra", {}).get("commit") == os.environ.get("INFRA_SHA"),
         "restored source certificate differs")
    pool = {row["oid"]: row for row in payload["shared_objects"]}
    need(len(pool) == len(payload["shared_objects"]), "duplicate shared source object")
    record = copy.deepcopy(payload["infra"])
    record["objects"] = [pool[ref["oid"]] for ref in record["objects"]]
    selected = source.expected_infra_paths(record, recipe)
    need([row["path"] for row in certificate["infra"]["restored_paths"]] == selected,
         "certified infrastructure closure differs")

    missing = copy.deepcopy(record)
    dependency = ROOT + REQUIRED[a.lane][0] if reviewed else recipe["entrypoint"]
    missing["paths"] = [row for row in missing["paths"] if row["path"] != dependency]
    need(len(missing["paths"]) + 1 == len(record["paths"]),
         "control dependency was not a selected input")
    controls = [reject("missing_transitive_input",
                       lambda: source.expected_infra_paths(missing, recipe),
                       "exact recipe infrastructure path set differs")]

    extra = copy.deepcopy(record)
    extra["paths"].append({"path": ROOT + "unlisted-transitive-module.py"})
    controls.append(reject("extra_transitive_input",
                           lambda: source.expected_infra_paths(extra, recipe),
                           "exact recipe infrastructure path set differs"))

    bad_mode = copy.deepcopy(record)
    bad_mode["paths"][0]["mode"] = "120000"
    controls.append(reject("nonregular_selected_input",
                           lambda: source.expected_infra_paths(bad_mode, recipe),
                           "exact recipe infrastructure input is not a regular file"))

    bad_hash = copy.deepcopy(record)
    bad_hash["paths"][0]["sha256"] = "0" * 64
    no_blob = copy.deepcopy(record)
    missing_oid = no_blob["paths"][0]["oid"]
    no_blob["objects"] = [row for row in no_blob["objects"]
                          if row["oid"] != missing_oid]
    need(len(no_blob["objects"]) + 1 == len(record["objects"]),
         "selected object closure test cannot isolate an object")
    with tempfile.TemporaryDirectory(prefix="exact-infra-controls-", dir="/workspace") as temporary:
        scratch = Path(temporary)
        controls.append(reject("selected_path_hash_mismatch",
                               lambda: source.restore_repo(bad_hash, scratch / "bad-hash", selected),
                               "committed path bytes differ"))
        controls.append(reject("missing_selected_git_object",
                               lambda: source.restore_repo(no_blob, scratch / "missing-object", selected),
                               f"git show {record['commit']}:{no_blob['paths'][0]['path']} failed:"))
    output = {"classification": "EXACT_INFRA_TRANSPORT_CONTROLS_COMPLETE",
              "diagnostic_complete": True, "verification_accepted": False,
              "accepted": False, "lane": a.lane,
              "infra_commit": record["commit"], "selected_infra_paths": len(selected),
              "reviewed_transitive_dependency_set": reviewed,
              "mandatory_selected_dependencies": sorted(required),
              "controls": controls}
    (a.evidence / "exact-infra-transport-controls.json").write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"classification": output["classification"],
                      "controls": len(controls)}, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
