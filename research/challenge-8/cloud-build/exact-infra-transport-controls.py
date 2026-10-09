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
    "o26-recovery-tests": (
        "actual-sort4-capture.py", "cut-relocate-audit.py",
        "cut-relocate-provider-overlay.py", "nested-proof-order-audit.py",
        "o26-recipe.py", "o26-refresh-audit.py", "o26-refresh-recipe.py",
        "run-cut-relocate.sh", "run-nested-proof-order-test.sh",
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
    payload = json.loads(gzip.decompress(a.archive.read_bytes()))
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
