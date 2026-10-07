#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted, saved-evidence S6 classifier replay; never executes proof tools.

Pin the artifact ID, size, and compact ZIP digest after the source run finishes.
The replay preserves every original classification byte-for-byte in its output.
Only exact diagnostic reason/location predicates may change.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import tempfile
import zipfile


RUN_ID = 37637630477
SOURCE_SHA = "de7ed9de861eea7346301f6807e242862a68c0ab"
PATCH_SHA = "cd660fe9f470293cc16712a4a71714c8f5f6e802608cedb5b486c3d8a1d27413"
PROFILE = "experimental-source-linked-select-pointer-drop-v1"
ARTIFACT_NAME = "smallsort-select-compact-evidence-37637630477-1"
ARTIFACT_ID = 11490457470
ARTIFACT_SIZE = 3990694
ARCHIVE_SHA = "34a6fba71d964a5ed74298471da4176102fdf3bc747178cadd9a69894d91b232"
ROOT = "current/select-pointer/"
MATRIX = ROOT + "pointer-drop-matrix/"
SETUP_RETRY = {"source_input_type", "mir_output_type", "mir_contract"}


def require(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None,
            f"cannot import {path.name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_json(z: zipfile.ZipFile, name: str) -> dict:
    return json.loads(z.read(name))


def verify_manifest(z: zipfile.ZipFile) -> tuple[dict, set[str]]:
    manifest = read_json(z, "COMPACT-EVIDENCE-MANIFEST.json")
    source = manifest["current_source"]
    require(source.get("run_id") == str(RUN_ID) and
            source.get("head_sha") == SOURCE_SHA and
            source.get("repository") == "Tiramisu-Cake/verify-rust-std" and
            source.get("run_attempt") == "1" and
            source.get("compact_artifact_name") == ARTIFACT_NAME,
            "compact manifest source/run identity mismatch")
    names = set(z.namelist())
    included = [entry for entry in manifest["entries"]
                if entry.get("included") is True]
    require({entry["compact_entry"] for entry in included} ==
            names - {"COMPACT-EVIDENCE-MANIFEST.json"} and
            len(included) == len(names) - 1,
            "manifest membership differs from compact ZIP")
    for entry in included:
        name = entry["compact_entry"]
        path = PurePosixPath(name)
        require(not path.is_absolute() and ".." not in path.parts and
                (name.startswith(ROOT) or name.startswith("o4/")),
                "unsafe or unexpected compact entry")
        data = z.read(name)
        info = z.getinfo(name)
        require(sha(data) == entry["sha256"] and
                len(data) == entry["file_size"] and
                f"{info.CRC:08x}" == entry["crc32"],
                f"manifest byte mismatch: {name}")
    require(sha(z.read(ROOT + "applied.patch")) == PATCH_SHA,
            "saved verifier patch differs from drop-v1 pin")
    environment = z.read(ROOT + "environment.txt").decode()
    require(f"Source SHA: {SOURCE_SHA}" in environment and
            f"Profile: {PROFILE}" in environment and
            PATCH_SHA in environment,
            "saved profile/source/patch environment mismatch")
    return manifest, names


def materialize(z: zipfile.ZipFile, prefix: str, target: Path,
                mode: str | None = None) -> None:
    target.mkdir(parents=True, exist_ok=False)
    count = 0
    for name in z.namelist():
        if not name.startswith(prefix) or name.endswith("/"):
            continue
        rel = PurePosixPath(name[len(prefix):])
        require(rel.parts and not rel.is_absolute() and ".." not in rel.parts,
                "unsafe case member")
        path = target.joinpath(*rel.parts)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(z.read(name))
        count += 1
    require(count > 0, f"saved case absent: {prefix}")
    if mode == "mir":
        wrapper = (target / "mir-exporter-wrapper.py").read_bytes()
        mirror = target / "mutation-profile/bin/vf-rust-mir-exporter"
        mirror.parent.mkdir(parents=True, exist_ok=True)
        mirror.write_bytes(wrapper)
        profile = json.loads((target / "mutation-profile.json").read_text())
        require(sha(wrapper) == profile["wrapper_sha256"],
                "saved MIR wrapper copy/profile hash mismatch")


def save(evidence: Path, subtree: str, label: str, data: bytes) -> None:
    target = evidence / subtree / label
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)


def diagnostic_only_delta(old: dict, new: dict, admission: bool) -> bool:
    if old == new:
        return True
    if (old.get("classification") != "INCONCLUSIVE" or
            new.get("classification") not in {
                "DIAGNOSTIC_POSITIVE", "INTENDED_PROOF_REJECTION",
                "INTENDED_ADMISSION_REJECTION"}):
        return False
    old_copy = json.loads(json.dumps(old))
    new_copy = json.loads(json.dumps(new))
    old_copy.pop("classification", None)
    new_copy.pop("classification", None)
    if admission:
        old_copy.pop("expected_reasons", None)
        new_copy.pop("expected_reasons", None)
        old_gate = old_copy["admission_evidence"]
        new_gate = new_copy["admission_evidence"]
        if (old_gate.pop("exact_fatal") is not False or
                new_gate.pop("exact_fatal") is not True):
            return False
    else:
        for group in ("positive_evidence", "negative_evidence"):
            old_gate = old_copy[group]
            new_gate = new_copy[group]
            if (old_gate.pop("safe_prototype", None) is not False or
                    new_gate.pop("unsafe_body_entered", None) is not True):
                return False
        old_gate = old_copy["negative_evidence"]
        new_gate = new_copy["negative_evidence"]
        old_prerequisite = old_gate.pop("positive_prerequisite")
        new_prerequisite = new_gate.pop("positive_prerequisite")
        if old_prerequisite != new_prerequisite and not (
                old_prerequisite is False and new_prerequisite is True):
            return False
        changed = set()
        for field in ("target_location", "target_message"):
            if old_gate[field] != new_gate[field]:
                changed.add(field)
            old_gate.pop(field)
            new_gate.pop(field)
        if any(old["negative_evidence"][f] is not False or
               new["negative_evidence"][f] is not True for f in changed):
            return False
    return old_copy == new_copy


def replay(args: argparse.Namespace) -> dict:
    require(os.environ.get("GITHUB_ACTIONS") == "true" and
            os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted" and
            os.environ.get("RUNNER_OS") == "Linux",
            "pointer drop replay requires GitHub-hosted Linux")
    require(os.environ.get("SORT4_SELECT_PROFILE") == PROFILE,
            "replay profile must be the exact saved drop-v1 profile")
    require(ARTIFACT_ID > 0 and ARTIFACT_SIZE > 0 and
            len(ARCHIVE_SHA) == 64, "completed artifact identity not pinned")
    repo = Path(__file__).resolve().parents[2]
    classifier = load(repo / "research/challenge-8/check-pointer-drop.py",
                      "sort4_drop_saved_classifier")
    constructor = load(repo / "research/challenge-8/check-maybeuninit-new-pointer.py",
                       "sort4_drop_saved_constructor")
    require(classifier.PROFILE == PROFILE and
            sha((repo / "research/challenge-8/verifast-select-pointer-drop.patch").read_bytes())
            == PATCH_SHA, "current classifier/patch profile differs")
    evidence = args.evidence.resolve()
    require(evidence.is_dir() and
            {path.name for path in evidence.iterdir()} ==
            {"original-run.json", "original-artifact.json", "classifier-self-check.json"},
            "replay evidence directory must contain only runner metadata")
    run = json.loads((evidence / "original-run.json").read_text())
    artifact = json.loads((evidence / "original-artifact.json").read_text())
    selfcheck = json.loads((evidence / "classifier-self-check.json").read_text())
    require(run.get("id") == RUN_ID and run.get("head_sha") == SOURCE_SHA and
            run.get("head_branch") == "challenge-8/research" and
            run.get("event") == "workflow_dispatch" and
            run.get("run_attempt") == 1 and
            run.get("status") == "completed" and
            run.get("repository", {}).get("full_name") ==
              "Tiramisu-Cake/verify-rust-std" and
            artifact.get("id") == ARTIFACT_ID and
            artifact.get("name") == ARTIFACT_NAME and
            artifact.get("size_in_bytes") == ARTIFACT_SIZE and
            artifact.get("expired") is False and
            artifact.get("workflow_run", {}).get("id") == RUN_ID and
            artifact.get("workflow_run", {}).get("head_sha") == SOURCE_SHA,
            "GitHub run/artifact metadata differs from source pin")
    require(selfcheck.get("pass") is True and
            selfcheck.get("mutant_count") == 64 and
            selfcheck.get("message_mutant_count") == 12 and
            selfcheck.get("admission_message_mutant_count") == 4,
            "current hosted classifier self-check incomplete")
    require(args.archive.is_file() and sha(args.archive.read_bytes()) == ARCHIVE_SHA,
            "compact ZIP bytes differ from pinned source artifact")
    shutil.copyfile(args.archive, evidence / "source-compact-evidence.zip")
    with zipfile.ZipFile(args.archive) as z:
        manifest, names = verify_manifest(z)
        save(evidence, "original", "COMPACT-EVIDENCE-MANIFEST.json",
             z.read("COMPACT-EVIDENCE-MANIFEST.json"))
        summary = read_json(z, MATRIX + "summary.json")
        save(evidence, "original", "pointer-drop-summary.json",
             z.read(MATRIX + "summary.json"))
        require(summary.get("tool_profile") == PROFILE and
                summary.get("accepted_component") is False and
                summary.get("classification") == "INCONCLUSIVE" and
                all(summary.get("prerequisites", {}).values()) and
                len(summary.get("cases", [])) ==
                    len(classifier.POSITIVES + classifier.NEGATIVES) and
                len(summary.get("admission_cases", [])) ==
                    len(classifier.SOURCE_MUTATIONS + classifier.MIR_MUTATIONS +
                        classifier.PIN_MUTATIONS),
                "saved S6 matrix is incomplete or not the replay target")
        for name in ("constructor-regressions/summary.json",
                     "matrix/summary.json", "intrinsic-matrix/summary.json"):
            saved = read_json(z, ROOT + name)
            require(saved.get("accepted_component") is True or
                    saved.get("constructor_acceptance") is True,
                    f"accepted same-profile prerequisite missing: {name}")
            save(evidence, "original", name.replace("/", "-"), z.read(ROOT + name))
        changed = []
        pending_setup = []
        corrected_cases = []
        corrected_admissions = []
        seen = set()
        with tempfile.TemporaryDirectory(prefix="sort4-s6-replay-") as temporary:
            temp = Path(temporary)
            for old in summary["cases"]:
                variant = old["variant"]
                require(variant in classifier.POSITIVES + classifier.NEGATIVES and
                        variant not in seen, "duplicate/unknown proof case")
                seen.add(variant)
                label = f"pointer_drop_{variant}"
                prefix = MATRIX + label + "/"
                require(prefix + "diagnostic-classification.json" in names,
                        "saved proof classification absent")
                raw = z.read(prefix + "diagnostic-classification.json")
                require(json.loads(raw) == old,
                        "saved proof classification differs from summary")
                save(evidence, "original", label + ".json", raw)
                case = temp / label
                materialize(z, prefix, case)
                positive = any(item["classification"] == "DIAGNOSTIC_POSITIVE"
                               for item in corrected_cases)
                new = classifier.classify_case(case, old["runner_result"], variant,
                                               constructor, positive)
                require(diagnostic_only_delta(old, new, False),
                        f"proof reclassification changed non-diagnostic evidence: {label}")
                save(evidence, "corrected", label + ".json",
                     json.dumps(new, indent=2, sort_keys=True).encode() + b"\n")
                corrected_cases.append(new)
                if new != old:
                    changed.append(label)
            require(seen == set(classifier.POSITIVES + classifier.NEGATIVES),
                    "proof case set differs from pinned S6 matrix")
            seen.clear()
            for old in summary["admission_cases"]:
                mode, mutation = old["mode"], old["mutation"]
                allowed = {"source": classifier.SOURCE_MUTATIONS,
                           "mir": classifier.MIR_MUTATIONS,
                           "pin": classifier.PIN_MUTATIONS}
                require(mode in allowed and mutation in allowed[mode] and
                        (mode, mutation) not in seen,
                        "duplicate/unknown admission case")
                seen.add((mode, mutation))
                label = f"{mode}_{mutation}"
                prefix = MATRIX + label + "/"
                raw = z.read(prefix + "admission-classification.json")
                require(json.loads(raw) == old,
                        "saved admission classification differs from summary")
                save(evidence, "original", label + ".json", raw)
                if label in SETUP_RETRY:
                    require(old["classification"] == "INCONCLUSIVE" and
                            old["admission_evidence"]["exact_fatal"] is False and
                            old["admission_evidence"]["frontend_refinement"] is False,
                            "saved setup control unexpectedly reached admission")
                    pending_setup.append(label)
                    continue
                case = temp / label
                materialize(z, prefix, case, mode)
                new = classifier.classify_admission(case, old["runner_result"],
                                                    mutation, mode, constructor)
                require(diagnostic_only_delta(old, new, True),
                        f"admission replay changed non-diagnostic evidence: {label}")
                save(evidence, "corrected", label + ".json",
                     json.dumps(new, indent=2, sort_keys=True).encode() + b"\n")
                corrected_admissions.append(new)
                if new != old:
                    changed.append(label)
            require(seen == {(mode, mutation) for mode, variants in allowed.items()
                             for mutation in variants},
                    "admission set differs from pinned S6 matrix")
        require(all(item["classification"] == "DIAGNOSTIC_POSITIVE"
                    for item in corrected_cases
                    if item["variant"] in classifier.POSITIVES) and
                all(item["classification"] == "INTENDED_PROOF_REJECTION"
                    for item in corrected_cases
                    if item["variant"] in classifier.NEGATIVES) and
                all(item["classification"] == "INTENDED_ADMISSION_REJECTION"
                    for item in corrected_admissions) and
                set(pending_setup) == SETUP_RETRY and
                len(corrected_admissions) == len(summary["admission_cases"]) -
                    len(SETUP_RETRY),
                "saved proof/valid admission evidence failed exact diagnostic replay")
        result = {
            "classification": "REPLAY_PARTIAL_PENDING_THREE_HOSTED_CONTROLS",
            "accepted_component": False,
            "full_select_proved": False,
            "source_run_id": RUN_ID,
            "source_sha": SOURCE_SHA,
            "tool_profile": PROFILE,
            "patch_sha256": PATCH_SHA,
            "artifact_id": ARTIFACT_ID,
            "artifact_sha256": ARCHIVE_SHA,
            "manifest_sha256": sha(z.read("COMPACT-EVIDENCE-MANIFEST.json")),
            "manifest_entries_verified": len(names)-1,
            "original_case_count": len(summary["cases"]),
            "original_admission_count": len(summary["admission_cases"]),
            "corrected_proof_count": len(corrected_cases),
            "corrected_admission_count": len(corrected_admissions),
            "pending_new_hosted_controls": sorted(pending_setup),
            "diagnostic_only_changes": sorted(changed),
            "classification_correction":
                "Unsafe checked body uses its exact custom contract; a SAFE "
                "prototype marker was wrongly required by the original classifier",
            "all_original_classifications_preserved": True,
        }
        (evidence / "summary.json").write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n")
        return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--evidence", required=True, type=Path)
    args = parser.parse_args()
    result = replay(args)
    print(json.dumps({"classification": result["classification"],
                      "diagnostic_only_changes": result["diagnostic_only_changes"],
                      "pending_new_hosted_controls": result["pending_new_hosted_controls"]}))


if __name__ == "__main__":
    main()
