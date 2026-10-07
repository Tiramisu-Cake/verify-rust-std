#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Reclassify the pinned S5j artifact on hosted Actions without proof execution.

The input is the downloaded GitHub artifact ZIP or its contained compact ZIP.
Only saved source, MIR, logs, hashes, and classifications are read. This script
does not call the MIR exporter, VeriFast, the refinement checker, or run_case.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import tempfile
import zipfile


RUN = "37621751848"
SOURCE_SHA = "2454e860dc75c277686f3031a311501a3cd2b9e3"
PATCH_SHA = "7bb39a84b95fd15ed5be29864c3a22774d37c660baafa694188b14970c344320"
PROFILE = "experimental-source-linked-select-pointer-intrinsics-v2"
ARTIFACT_NAME = "smallsort-select-compact-evidence-37621751848-1"
ARTIFACT_ID = 11481774726
ARTIFACT_SIZE = 3458032
INNER_NAME = "sort4-select-compact-evidence.zip"
OUTER_SHA = "1a5e4957da5db048d02cb56bc518eb8afa195be5384d60f300281ed8f0f036c7"
INNER_SHA = "5e0d333f303cab8cffc14c7e4d7a96a04c83fe2f928a37ff50e80611b85bf969"
ROOT = "current/select-pointer/"
MATRIX = ROOT + "intrinsic-matrix/"
EIGHT = {
    "source_ptr_identity", "source_mu_identity",
    "mir_ptr_operand_order", "mir_ptr_operand_source", "mir_ptr_predecessor_source",
    "mir_mu_operand_order", "mir_mu_operand_source", "mir_mu_predecessor_source",
}


def require(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(archive: zipfile.ZipFile, name: str) -> dict:
    return json.loads(archive.read(name))


def load_script(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def open_compact(path: Path) -> tuple[zipfile.ZipFile, str]:
    archive_sha = sha(path.read_bytes())
    require(archive_sha in {OUTER_SHA, INNER_SHA},
            "archive bytes differ from exact S5j compact artifact")
    outer = zipfile.ZipFile(path)
    names = outer.namelist()
    if names == [INNER_NAME]:
        require(archive_sha == OUTER_SHA, "outer artifact SHA mismatch")
        inner = outer.read(INNER_NAME)
        outer.close()
        require(sha(inner) == INNER_SHA, "inner compact ZIP SHA mismatch")
        return zipfile.ZipFile(io.BytesIO(inner)), sha(inner)
    require(archive_sha == INNER_SHA, "inner compact ZIP SHA mismatch")
    require("COMPACT-EVIDENCE-MANIFEST.json" in names,
            "expected pinned compact artifact or its inner ZIP")
    return outer, sha(path.read_bytes())


def verify_manifest(archive: zipfile.ZipFile) -> dict:
    manifest = read_json(archive, "COMPACT-EVIDENCE-MANIFEST.json")
    source = manifest["current_source"]
    require(source.get("run_id") == RUN and source.get("head_sha") == SOURCE_SHA and
            source.get("repository") == "Tiramisu-Cake/verify-rust-std" and
            source.get("run_attempt") == "1" and
            source.get("compact_artifact_name") == ARTIFACT_NAME,
            "archive origin differs from pinned S5j run/source")
    names = set(archive.namelist())
    included = [entry for entry in manifest["entries"] if entry.get("included") is True]
    require(len(included) == len(names) - 1 and
            {entry["compact_entry"] for entry in included} == names -
            {"COMPACT-EVIDENCE-MANIFEST.json"},
            "compact manifest membership differs from ZIP")
    for entry in included:
        name = entry["compact_entry"]
        require(not PurePosixPath(name).is_absolute() and ".." not in PurePosixPath(name).parts,
                "unsafe archive member path")
        data = archive.read(name)
        info = archive.getinfo(name)
        require(sha(data) == entry["sha256"] and len(data) == entry["file_size"] and
                f"{info.CRC:08x}" == entry["crc32"], f"manifest byte mismatch: {name}")
    require(sha(archive.read(ROOT + "applied.patch")) == PATCH_SHA,
            "applied tool patch differs from pinned S5j profile")
    env = archive.read(ROOT + "environment.txt").decode()
    require(f"Source SHA: {SOURCE_SHA}" in env and f"Profile: {PROFILE}" in env and
            PATCH_SHA in env, "saved hosted environment/profile identity mismatch")
    return manifest


def save_original(evidence: Path, label: str, data: bytes) -> None:
    target = evidence / "original-classifications" / label
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)


def save_corrected(evidence: Path, label: str, result: dict) -> None:
    target = evidence / "corrected-classifications" / label
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


def identity_matches(run: str, source: str, profile: str, patch: str) -> bool:
    return run == RUN and source == SOURCE_SHA and profile == PROFILE and patch == PATCH_SHA


def replay_regression_checks(classifier, originals: dict[str, dict],
                             corrected: dict[str, dict]) -> dict:
    outcomes = {}
    for label in sorted(EIGHT):
        old = originals[label]
        new = corrected[label]
        kind = old["kind"]
        mode = old["mode"]
        mutation = old["mutation"]
        reasons = classifier.admission_reasons(kind, mode, mutation)
        require(len(reasons) == 1 and len(old["fatal"]) == 1,
                "eight-case fatal/reason is not singular")
        actual = old["fatal"][0]
        old_reasons = old["expected_reasons"]
        outcomes[label] = {
            "exact_full_fatal": classifier.matches_admission_fatal(actual, reasons),
            "old_reason_rejected": all(not classifier.matches_admission_fatal(
                f'Fatal error: exception Failure("{classifier.REJECT_PREFIX}{reason}")',
                reasons) for reason in old_reasons),
            "wrong_certificate_rejected": not classifier.matches_admission_fatal(
                actual.replace("SORT4-SELECT-INTRINSIC", "SORT4-AS-MUT-PTR"), reasons),
            "wrong_stage_rejected": not classifier.matches_admission_fatal(
                actual.replace("Fatal error: exception Failure(",
                               "verified/lib.rs(4,1): error: Failure("), reasons),
            "extra_text_rejected": not classifier.matches_admission_fatal(
                actual + " trailing", reasons),
            "all_other_gates_still_true": all(v is True for key, v in
                old["admission_evidence"].items() if key != "exact_fatal") and
                all(v is True for v in new["admission_evidence"].values()),
        }
    identity_mutants = {
        "wrong_run": not identity_matches("37621751849", SOURCE_SHA, PROFILE, PATCH_SHA),
        "wrong_source": not identity_matches(RUN, "0" * 40, PROFILE, PATCH_SHA),
        "wrong_profile": not identity_matches(RUN, SOURCE_SHA,
                                               "experimental-source-linked-select-pointer-intrinsics-v1",
                                               PATCH_SHA),
        "wrong_patch": not identity_matches(RUN, SOURCE_SHA, PROFILE, "0" * 64),
    }
    passed = identity_matches(RUN, SOURCE_SHA, PROFILE, PATCH_SHA) and \
        all(identity_mutants.values()) and \
        all(all(values.values()) for values in outcomes.values())
    return {"pass": passed, "exact_case_checks": outcomes,
            "archive_identity_mutants_rejected": identity_mutants,
            "mutant_count": 4 + 4 * len(EIGHT)}


def materialize_case(archive: zipfile.ZipFile, case_prefix: str,
                     target: Path, mode: str | None = None) -> None:
    target.mkdir(parents=True, exist_ok=False)
    for name in archive.namelist():
        if not name.startswith(case_prefix) or name.endswith("/"):
            continue
        relative = PurePosixPath(name[len(case_prefix):])
        require(relative.parts and ".." not in relative.parts and
                not relative.is_absolute(), "unsafe case member")
        path = target.joinpath(*relative.parts)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(archive.read(name))
    if mode == "mir":
        # Compact packaging retains the exact wrapper copy but omits its
        # shadow-profile path. Recreate bytes only for the saved hash audit.
        wrapper = (target / "mir-exporter-wrapper.py").read_bytes()
        mirror = target / "mutation-profile/bin/vf-rust-mir-exporter"
        mirror.parent.mkdir(parents=True, exist_ok=True)
        mirror.write_bytes(wrapper)
        profile = json.loads((target / "mutation-profile.json").read_text())
        require(sha(wrapper) == profile["wrapper_sha256"],
                "saved MIR wrapper hash differs from profile record")


def replay(args: argparse.Namespace) -> dict:
    require(os.environ.get("GITHUB_ACTIONS") == "true" and
            os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted" and
            os.environ.get("RUNNER_OS") == "Linux",
            "replay requires GitHub-hosted Linux")
    require(os.environ.get("SORT4_SELECT_PROFILE") == PROFILE,
            "replay profile must equal pinned S5j v2")
    repository = Path(__file__).resolve().parents[2]
    classifier = load_script(repository / "research/challenge-8/check-select-pointer-intrinsics.py",
                             "sort4_saved_intrinsic_classifier")
    constructor = load_script(repository / "research/challenge-8/check-maybeuninit-new-pointer.py",
                              "sort4_saved_constructor_parser")
    require(classifier.PROFILE == PROFILE and PROFILE in classifier.AUTHORIZED_PROFILES,
            "current classifier profile not pinned v2")
    evidence = args.evidence.resolve()
    require(evidence.is_dir() and {path.name for path in evidence.iterdir()} == {
        "original-run.json", "original-artifact.json", "classifier-self-check.json"},
        "replay evidence directory must contain only three runner-owned metadata files")
    run_meta = json.loads((evidence / "original-run.json").read_text())
    artifact_meta = json.loads((evidence / "original-artifact.json").read_text())
    new_selfcheck = json.loads((evidence / "classifier-self-check.json").read_text())
    require(run_meta.get("id") == int(RUN) and
            run_meta.get("head_sha") == SOURCE_SHA and
            run_meta.get("head_branch") == "challenge-8/research" and
            run_meta.get("event") == "workflow_dispatch" and
            run_meta.get("path") == ".github/workflows/smallsort-research.yml" and
            run_meta.get("run_attempt") == 1 and
            run_meta.get("status") == "completed" and
            run_meta.get("conclusion") == "failure" and
            run_meta.get("repository", {}).get("full_name") ==
                "Tiramisu-Cake/verify-rust-std" and
            artifact_meta.get("id") == ARTIFACT_ID and
            artifact_meta.get("name") == ARTIFACT_NAME and
            artifact_meta.get("size_in_bytes") == ARTIFACT_SIZE and
            artifact_meta.get("expired") is False and
            artifact_meta.get("workflow_run", {}).get("id") == int(RUN) and
            artifact_meta.get("workflow_run", {}).get("head_sha") == SOURCE_SHA,
            "runner-fetched GitHub run/artifact metadata differs from pinned S5j")
    require(new_selfcheck.get("pass") is True and
            new_selfcheck.get("mutant_count") == 60 and
            new_selfcheck.get("message_mutant_count") == 10 and
            new_selfcheck.get("admission_message_mutant_count") == 28 and
            new_selfcheck.get("v2_admission_messages", {}).get("pass") is True and
            new_selfcheck["v2_admission_messages"].get("mutant_count") == 24 and
            new_selfcheck["v2_admission_messages"].get(
                "stage_and_certificate_mutant_count") == 16,
            "corrected hosted classifier self-check incomplete")
    require(args.archive.resolve().is_file() and
            args.archive.resolve() != evidence / "source-evidence.zip",
            "input artifact path missing or aliases preserved copy")
    shutil.copyfile(args.archive, evidence / "source-evidence.zip")
    archive, inner_sha = open_compact(args.archive)
    try:
        manifest = verify_manifest(archive)
        (evidence / "original-COMPACT-EVIDENCE-MANIFEST.json").write_bytes(
            archive.read("COMPACT-EVIDENCE-MANIFEST.json"))
        ctor = read_json(archive, ROOT + "constructor-regressions/summary.json")
        asptr = read_json(archive, ROOT + "matrix/summary.json")
        original_matrix = read_json(archive, MATRIX + "summary.json")
        selfcheck = read_json(archive, ROOT + "intrinsic-classifier-self-check.json")
        save_original(evidence, "intrinsic-summary.json",
                      archive.read(MATRIX + "summary.json"))
        for label, source_name in (
            ("constructor-summary.json", ROOT + "constructor-regressions/summary.json"),
            ("as-mut-ptr-summary.json", ROOT + "matrix/summary.json"),
            ("intrinsic-classifier-self-check.json", ROOT + "intrinsic-classifier-self-check.json"),
        ):
            save_original(evidence, label, archive.read(source_name))
        require(ctor.get("constructor_acceptance") is True and
                asptr.get("accepted_component") is True and
                asptr.get("classification") == "COMPONENT_ACCEPTED" and
                asptr.get("tool_profile") == PROFILE and
                original_matrix.get("tool_profile") == PROFILE and
                all(original_matrix.get("prerequisites", {}).values()) and
                selfcheck.get("pass") is True and
                selfcheck.get("mutant_count") == 60 and
                selfcheck.get("message_mutant_count") == 10 and
                selfcheck.get("admission_message_mutant_count") == 4,
                "saved same-profile constructor/as-mut-ptr/classifier gates incomplete")
        require(original_matrix.get("accepted_component") is False and
                original_matrix.get("classification") == "INCONCLUSIVE" and
                len(original_matrix.get("cases", [])) == 16 and
                len(original_matrix.get("admission_cases", [])) == 40,
                "saved matrix does not have complete 6+10+40 diagnostic shape")
        baselines = ctor.get("baselines", {})
        require(isinstance(baselines, dict) and
                baselines.get("stock_false_control", {}).get("outcome") ==
                    "EXPECTED_PROOF_FAILURE" and
                baselines.get("patched_false_control", {}).get("outcome") ==
                    "EXPECTED_PROOF_FAILURE" and
                baselines.get("stock_pointer_frame", {}).get("outcome") == "PASS" and
                baselines.get("patched_pointer_frame", {}).get("outcome") == "PASS" and
                isinstance(baselines.get("native_controls"), dict) and
                all(item.get("outcome") == "PASS" for item in
                    baselines["native_controls"].values()) and
                ctor.get("tool_home") == "/home/runner/work/_temp/select-pointer/source",
                "saved constructor/native baseline evidence missing")
        corrected_cases = []
        corrected_admissions = []
        original_admissions = {}
        corrected_admission_map = {}
        seen = set()
        with tempfile.TemporaryDirectory(prefix="sort4-s5j-replay-") as temporary:
            temp = Path(temporary)
            for original in original_matrix["cases"]:
                kind, variant = original["kind"], original["variant"]
                require(kind in classifier.KINDS and
                        variant in classifier.POSITIVES[kind] + classifier.NEGATIVES[kind],
                        "unexpected saved proof variant")
                label = f"select_{kind}_{variant}"
                require(label not in seen, "duplicate proof case")
                seen.add(label)
                prefix = MATRIX + label + "/"
                saved = read_json(archive, prefix + "diagnostic-classification.json")
                require(saved == original, "saved case differs from original matrix summary")
                save_original(evidence, label + ".json",
                              archive.read(prefix + "diagnostic-classification.json"))
                case = temp / label
                materialize_case(archive, prefix, case)
                prerequisite = variant in classifier.NEGATIVES[kind]
                corrected = json.loads(json.dumps(classifier.classify_case(
                    case, saved["runner_result"], kind, variant, constructor,
                    prerequisite)))
                require(corrected == saved and corrected["classification"] in
                        {"DIAGNOSTIC_POSITIVE", "INTENDED_PROOF_REJECTION"},
                        f"saved proof reclassification changed: {label}")
                save_corrected(evidence, label + ".json", corrected)
                corrected_cases.append(corrected)
            expected_cases = {f"select_{kind}_{variant}" for kind in classifier.KINDS
                              for variant in classifier.POSITIVES[kind] + classifier.NEGATIVES[kind]}
            require(seen == expected_cases, "proof case set differs from exact 6+10 matrix")
            changed = set()
            seen.clear()
            for original in original_matrix["admission_cases"]:
                kind, mutation, mode = original["kind"], original["mutation"], original["mode"]
                require(kind in classifier.KINDS and mode in {"source", "mir"} and
                        mutation in (classifier.SOURCE_MUTATIONS if mode == "source" else
                                     classifier.MIR_MUTATIONS), "unexpected saved admission")
                label = f"{mode}_{kind}_{mutation}"
                require(label not in seen, "duplicate admission case")
                seen.add(label)
                prefix = MATRIX + label + "/"
                saved = read_json(archive, prefix + "admission-classification.json")
                original_admissions[label] = saved
                require(saved == original, "saved admission differs from original matrix summary")
                save_original(evidence, label + ".json",
                              archive.read(prefix + "admission-classification.json"))
                case = temp / label
                materialize_case(archive, prefix, case, mode)
                corrected = json.loads(json.dumps(classifier.classify_admission(
                    case, saved["runner_result"], kind, mutation, mode, constructor)))
                require(corrected["classification"] == "INTENDED_ADMISSION_REJECTION",
                        f"admission not reclassified at exact target: {label}")
                require(all(corrected["admission_evidence"].values()),
                        f"admission evidence incomplete: {label}")
                if label in EIGHT:
                    require(saved["classification"] == "INCONCLUSIVE" and
                            saved["admission_evidence"]["exact_fatal"] is False and
                            all(v is True for k,v in saved["admission_evidence"].items()
                                if k != "exact_fatal") and
                            corrected["fatal"] == saved["fatal"] and
                            corrected["mutation_record"] == saved["mutation_record"],
                            f"eight-case reason-only delta violated: {label}")
                    changed.add(label)
                else:
                    require(corrected == saved,
                            f"unchanged admission differs under replay: {label}")
                save_corrected(evidence, label + ".json", corrected)
                corrected_admissions.append(corrected)
                corrected_admission_map[label] = corrected
            expected_admissions = {
                f"{mode}_{kind}_{mutation}" for kind in classifier.KINDS
                for mode, mutations in (("source", classifier.SOURCE_MUTATIONS),
                                        ("mir", classifier.MIR_MUTATIONS))
                for mutation in mutations}
            require(seen == expected_admissions and changed == EIGHT,
                    "admission matrix/delta differs from pinned 40/8")
        regressions = replay_regression_checks(classifier, original_admissions,
                                               corrected_admission_map)
        require(regressions["pass"], "replay message/stage/profile regression failed")
        # Existing saved classifier is the actual S5j gate; the current source
        # adds exact-message mutants and will be rerun separately by the runner.
        accepted = regressions["pass"] and len(corrected_cases) == 16 and \
            len(corrected_admissions) == 40 and \
            seen == expected_admissions and changed == EIGHT
        result = {
            "classification": "REPLAY_COMPONENT_ACCEPTED" if accepted else "INCONCLUSIVE",
            "accepted_component": accepted,
            "full_select_proved": False,
            "source_run_id": RUN,
            "source_sha": SOURCE_SHA,
            "patch_sha256": PATCH_SHA,
            "tool_profile": PROFILE,
            "input_archive_sha256": sha(args.archive.read_bytes()),
            "inner_compact_sha256": inner_sha,
            "run_metadata_sha256": sha((evidence / "original-run.json").read_bytes()),
            "artifact_metadata_sha256": sha((evidence / "original-artifact.json").read_bytes()),
            "corrected_classifier_self_check_sha256": sha(
                (evidence / "classifier-self-check.json").read_bytes()),
            "manifest_sha256": sha(archive.read("COMPACT-EVIDENCE-MANIFEST.json")),
            "original_case_count": len(original_matrix["cases"]),
            "original_admission_count": len(original_matrix["admission_cases"]),
            "corrected_case_count": len(corrected_cases),
            "corrected_admission_count": len(corrected_admissions),
            "reason_only_changes": sorted(changed),
            "raw_entries_verified": len([entry for entry in manifest["entries"]
                                         if entry.get("included") is True]),
            "same_profile_prerequisites": True,
            "regression_checks": regressions,
        }
        (evidence / "summary.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        return result
    finally:
        archive.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--evidence", required=True, type=Path)
    args = parser.parse_args()
    result = replay(args)
    print(json.dumps({"classification": result["classification"],
                      "reason_only_changes": result["reason_only_changes"]}))
    if not result["accepted_component"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
