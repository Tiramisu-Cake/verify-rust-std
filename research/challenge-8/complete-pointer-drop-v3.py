#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted S6v3 completion from authenticated full-matrix evidence.

The original proofs and two accepted coordinate controls retain their source
run identity. This invocation executes only the sixteen setup-repaired NORMAL
MIR admission controls and, after strict composite acceptance, the actual body.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import zipfile


RUN_ID = 37651717720
SOURCE_SHA = "dfc1f1d740689de8f427ac549da558d64a4318eb"
PATCH_SHA = "94ffc64ce15811ac0de62e55489fb1e61242883b7258aa22969bbefa9ec184e8"
PROFILE = "experimental-source-linked-select-pointer-drop-v3"
ARTIFACT_ID = 11497076310
ARTIFACT_NAME = "smallsort-select-compact-evidence-37651717720-1"
ARCHIVE_SHA = "f2c9a1dcda5785af850a51e103bc0c7d07df38c39ed9809afb33211bde997fb0"
ROOT = "current/select-pointer/"
SAVED = ("constructor-regressions/summary.json", "matrix/summary.json",
         "intrinsic-matrix/summary.json", "pointer-drop-matrix/summary.json",
         "actual-drop-integration/actual-ghost-admissions/summary.json")


def require(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def archive(args: argparse.Namespace) -> zipfile.ZipFile:
    require(args.archive.is_file() and sha(args.archive.read_bytes()) == ARCHIVE_SHA,
            "pinned v3 compact ZIP differs")
    z = zipfile.ZipFile(args.archive)
    manifest = json.loads(z.read("COMPACT-EVIDENCE-MANIFEST.json"))
    source = manifest["current_source"]
    require(source.get("run_id") == str(RUN_ID) and
            source.get("head_sha") == SOURCE_SHA and
            source.get("repository") == "Tiramisu-Cake/verify-rust-std" and
            source.get("run_attempt") == "1" and
            source.get("compact_artifact_name") == ARTIFACT_NAME,
            "saved v3 manifest source/run identity differs")
    names = set(z.namelist())
    included = [entry for entry in manifest["entries"] if entry.get("included") is True]
    require(len(included) == len(names) - 1 and
            {entry["compact_entry"] for entry in included} ==
                names - {"COMPACT-EVIDENCE-MANIFEST.json"},
            "saved v3 compact membership differs")
    for entry in included:
        name = entry["compact_entry"]
        path = PurePosixPath(name)
        require(not path.is_absolute() and ".." not in path.parts and
                (name.startswith(ROOT) or name.startswith("o4/")),
                "unsafe saved compact member")
        content = z.read(name)
        require(sha(content) == entry["sha256"] and
                len(content) == entry["file_size"] and
                f"{z.getinfo(name).CRC:08x}" == entry["crc32"],
                f"saved v3 compact member differs: {name}")
    require(sha(z.read(ROOT + "applied.patch")) == PATCH_SHA and
            f"Source SHA: {SOURCE_SHA}" in z.read(ROOT + "environment.txt").decode() and
            f"Profile: {PROFILE}" in z.read(ROOT + "environment.txt").decode(),
            "saved v3 semantic profile differs")
    return z


def validate_metadata(args: argparse.Namespace) -> None:
    run = json.loads(args.original_run.read_text())
    artifact = json.loads(args.original_artifact.read_text())
    require(run.get("id") == RUN_ID and run.get("head_sha") == SOURCE_SHA and
            run.get("run_attempt") == 1 and
            run.get("repository", {}).get("full_name") ==
                "Tiramisu-Cake/verify-rust-std" and
            artifact.get("id") == ARTIFACT_ID and
            artifact.get("name") == ARTIFACT_NAME and
            artifact.get("expired") is False and
            artifact.get("workflow_run", {}).get("id") == RUN_ID,
            "saved v3 GitHub run/artifact metadata differs")


def original_acceptance(z: zipfile.ZipFile) -> tuple[dict, list[dict]]:
    summaries = {name: json.loads(z.read(ROOT + name)) for name in SAVED}
    ctor = summaries[SAVED[0]]
    asptr, intrinsic, drop, controls = (summaries[name] for name in SAVED[1:])
    native = ctor.get("baselines", {}).get("native_controls", {})
    baselines = ctor.get("baselines", {})
    require(ctor.get("constructor_acceptance") is True and
            ctor.get("constructor_cases_not_run") == 0 and
            ctor.get("mir_mutation_cases_not_run") == 0 and
            len(native) == 10 and len(baselines) == 5 and
            all(item.get("outcome") == "PASS" and
                item.get("source_unchanged") is True for item in native.values()) and
            all(baselines[name].get("outcome") == expected for name, expected in (
                ("patched_false_control", "EXPECTED_PROOF_FAILURE"),
                ("patched_pointer_frame", "PASS"),
                ("stock_false_control", "EXPECTED_PROOF_FAILURE"),
                ("stock_pointer_frame", "PASS"))),
            "saved v3 constructor/baseline acceptance differs")
    for name, summary in (("as-mut-ptr", asptr), ("intrinsic", intrinsic),
                          ("pointer-drop", drop)):
        require(summary.get("accepted_component") is True and
                summary.get("classification") == "COMPONENT_ACCEPTED" and
                summary.get("tool_profile") == PROFILE and
                summary.get("full_select_proved") is False,
                f"saved v3 {name} acceptance differs")
    require(len(drop.get("cases", [])) == 13 and
            len(drop.get("admission_cases", [])) == 22 and
            not drop.get("cases_not_run") and
            not drop.get("admission_cases_not_run") and
            sum(item.get("classification") == "DIAGNOSTIC_POSITIVE"
                for item in drop["cases"]) == 2 and
            sum(item.get("classification") == "INTENDED_PROOF_REJECTION"
                for item in drop["cases"]) == 11 and
            all(item.get("classification") == "INTENDED_ADMISSION_REJECTION"
                for item in drop["admission_cases"]),
            "saved v3 S6 matrix cases differ")
    cases = controls.get("cases", [])
    require(controls.get("tool_profile") == PROFILE and
            len(cases) == 18 and
            [case.get("mutation") for case in cases[:2]] ==
                ["regular_hi", "explicit_end"] and
            all(case.get("classification") == "INTENDED_ADMISSION_REJECTION"
                for case in cases[:2]) and
            all(case.get("classification") == "INCONCLUSIVE" for case in cases[2:]),
            "saved v3 coordinate/setup classifications differ")
    return summaries, cases[:2]


def retain_original(z: zipfile.ZipFile, evidence: Path) -> dict:
    target = evidence / "saved-profile-evidence"
    target.mkdir()
    manifest = z.read("COMPACT-EVIDENCE-MANIFEST.json")
    (target / "COMPACT-EVIDENCE-MANIFEST.json").write_bytes(manifest)
    identities = {}
    for name in z.namelist():
        if not name.startswith(ROOT) or name.endswith("/"):
            continue
        content = z.read(name)
        dest = target.joinpath(*PurePosixPath(name).parts)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(content)
        identities[name] = sha(content)
    report = {"source_run_id": RUN_ID, "source_artifact_id": ARTIFACT_ID,
              "source_archive_sha256": ARCHIVE_SHA,
              "original_manifest_sha256": sha(manifest),
              "retained_entry_count": len(identities),
              "retained_entry_sha256": identities,
              "classification": "raw original evidence; not current-run proofs"}
    (target / "retention-report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report


def materialize_case(z: zipfile.ZipFile, prefix: str, target: Path) -> None:
    target.mkdir(parents=True, exist_ok=False)
    count = 0
    for name in z.namelist():
        if not name.startswith(prefix) or name.endswith("/"):
            continue
        rel = PurePosixPath(name[len(prefix):])
        require(rel.parts and not rel.is_absolute() and ".." not in rel.parts,
                "unsafe saved case member")
        dest = target.joinpath(*rel.parts)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(z.read(name))
        count += 1
    require(count > 0, "saved case missing")


def replay_coordinates(z: zipfile.ZipFile, evidence: Path,
                       original: list[dict], repo: Path) -> dict:
    """Reclassify saved raw artifacts without invoking any proof tool."""
    ghosts = load(repo / "research/challenge-8/check-pointer-drop-actual-ghosts.py",
                  "v3_replay_ghosts")
    constructor = load(repo / "research/challenge-8/check-maybeuninit-new-pointer.py",
                       "v3_replay_constructor")
    root = evidence / "coordinate-replay"
    root.mkdir()
    canonical = root / "canonical-projection"
    materialize_case(z, ROOT + "actual-drop-integration/"
                     "actual_select_pointer_drop_projection/", canonical)
    results = []
    for mutation, saved in zip(("regular_hi", "explicit_end"), original):
        target = root / ("normal_" + mutation)
        materialize_case(z, ROOT + "actual-drop-integration/"
                         "actual-ghost-admissions/normal_" + mutation + "/", target)
        wrapper = (target / "mir-exporter-wrapper.py").read_bytes()
        restored = target / "mutation-profile/bin/vf-rust-mir-exporter"
        restored.parent.mkdir(parents=True, exist_ok=True)
        restored.write_bytes(wrapper)
        profile = json.loads((target / "mutation-profile.json").read_text())
        require(sha(wrapper) == profile["wrapper_sha256"],
                "saved normal MIR wrapper differs")
        runner = json.loads((target / "classification.json").read_text())
        result = ghosts.classify(target, runner, canonical, mutation, constructor)
        old_bytes = z.read(ROOT + "actual-drop-integration/"
            "actual-ghost-admissions/normal_" + mutation +
            "/admission-classification.json")
        old = json.loads(old_bytes)
        require(old == saved and result == old,
                "saved coordinate classification changed under unchanged classifier")
        results.append({"mutation": mutation, "source_run_id": RUN_ID,
                        "original_classification_sha256": sha(old_bytes),
                        "reclassification_unchanged": True})
    summary = {"source_run_id": RUN_ID, "proof_tools_invoked": False,
               "unchanged_classifier": True, "accepted": len(results) == 2,
               "cases": results}
    (root / "summary.json").write_text(json.dumps(summary, indent=2,
        sort_keys=True) + "\n")
    return summary


def preflight(args: argparse.Namespace, repo: Path) -> None:
    require(os.environ.get("GITHUB_ACTIONS") == "true" and
            os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted" and
            os.environ.get("RUNNER_OS") == "Linux", "hosted-only preflight")
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=False)
    z = archive(args)
    _, coordinates = original_acceptance(z)
    require([case["mutation"] for case in coordinates] ==
            ["regular_hi", "explicit_end"], "coordinate controls absent")
    require(sha(args.schema.read_bytes()) ==
            "7f3ebce320a33bcb956d51b8387754729e6516f4d15ba8dfdc61e6e36f90dfd9",
            "preflight schema differs")
    ghosts = load(repo / "research/challenge-8/check-pointer-drop-actual-ghosts.py",
                  "v3_preflight_ghosts")
    constructor = load(repo / "research/challenge-8/check-maybeuninit-new-pointer.py",
                       "v3_preflight_constructor")
    canonical = z.read(ROOT +
        "actual-drop-integration/actual-ghost-admissions/normal_regular_hi/"
        "canonical-normal-mir.txt").decode()
    require(sha(canonical.encode()) == ghosts.NORMAL_TEXT_SHA,
            "preflight canonical NORMAL MIR differs")
    outcomes = []
    for mutation in ghosts.MUTATIONS[2:]:
        result = {"mutation": mutation, "diagnostic_only": True,
                  "is_proof": False, "is_component_acceptance": False}
        try:
            changed = ghosts.mutate_actual_ghost_mir(canonical, mutation, constructor)
            require(changed != canonical, "preflight mutation unchanged")
            encoded = subprocess.run(
                ["capnp", "encode", str(args.schema), "VfMir"],
                input=changed.encode(), stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, check=False)
            result.update({"encode_exit": encoded.returncode,
                           "mutated_text_sha256": sha(changed.encode()),
                           "mutated_bin_sha256": sha(encoded.stdout),
                           "encode_stderr": encoded.stderr.decode(errors="replace")})
            require(encoded.returncode == 0, "preflight capnp encode failed")
            result["classification"] = "DIAGNOSTIC_PRECHECK_READY"
        except Exception as exc:
            result.update({"classification": "DIAGNOSTIC_SETUP_INCONCLUSIVE",
                           "error": f"{type(exc).__name__}: {exc}"})
        outcomes.append(result)
    accepted = len(outcomes) == 16 and all(
        item["classification"] == "DIAGNOSTIC_PRECHECK_READY" for item in outcomes)
    summary = {"classification": "DIAGNOSTIC_PRECHECK_READY" if accepted else
               "DIAGNOSTIC_SETUP_INCONCLUSIVE", "ready": accepted,
               "is_proof": False, "is_component_acceptance": False,
               "source_run_id": RUN_ID, "source_archive_sha256": ARCHIVE_SHA,
               "schema_sha256": sha(args.schema.read_bytes()), "cases": outcomes}
    (evidence / "summary.json").write_text(json.dumps(summary, indent=2,
        sort_keys=True) + "\n")
    print(json.dumps({"preflight_ready": accepted, "case_count": len(outcomes)}))
    if not accepted:
        raise SystemExit(1)


def complete(args: argparse.Namespace, repo: Path) -> None:
    require(os.environ.get("GITHUB_ACTIONS") == "true" and
            os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted" and
            os.environ.get("RUNNER_OS") == "Linux" and
            os.environ.get("SORT4_SELECT_PROFILE") == PROFILE,
            "hosted exact v3 completion profile required")
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=False)
    validate_metadata(args)
    z = archive(args)
    summaries, coordinates = original_acceptance(z)
    helper = load(repo / "research/challenge-8/complete-pointer-drop.py",
                  "v3_existing_profile_helper")
    profile = argparse.Namespace(RUN_ID=RUN_ID, SOURCE_SHA=SOURCE_SHA,
        PATCH_SHA=PATCH_SHA, PROFILE=PROFILE, ARCHIVE_SHA=ARCHIVE_SHA,
        ARTIFACT_ID=ARTIFACT_ID, ARTIFACT_NAME=ARTIFACT_NAME, ROOT=ROOT)
    provenance = helper.validate_profile(z, argparse.Namespace(
        current_environment=args.current_environment,
        current_patch_identities=args.current_patch_identities,
        current_specification_audit=args.current_specification_audit), repo, profile)
    retained = retain_original(z, evidence)
    require(retained["retained_entry_count"] > 0,
            "original v3 raw evidence was not retained")
    coordinate_replay = replay_coordinates(z, evidence, coordinates, repo)
    require(coordinate_replay["accepted"], "coordinate replay was incomplete")
    precheck = json.loads(args.preflight_summary.read_text())
    ghosts = load(repo / "research/challenge-8/check-pointer-drop-actual-ghosts.py",
                  "v3_completion_ghosts")
    require(precheck.get("ready") is True and
            precheck.get("source_run_id") == RUN_ID and
            precheck.get("source_archive_sha256") == ARCHIVE_SHA and
            precheck.get("schema_sha256") == sha(args.schema.read_bytes()) and
            [item.get("mutation") for item in precheck.get("cases", [])] ==
                list(ghosts.MUTATIONS[2:]) and
            all(item.get("classification") == "DIAGNOSTIC_PRECHECK_READY" and
                item.get("encode_exit") == 0 and
                item.get("is_proof") is False and
                item.get("is_component_acceptance") is False
                for item in precheck.get("cases", [])),
            "hosted 16-control preflight differs")
    imported = evidence / "imported-prerequisites"
    imported.mkdir()
    digest_map = {}
    for name in SAVED[:4]:
        data = z.read(ROOT + name)
        path = imported / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        digest_map[name] = sha(data)
    coordinate_path = imported / "coordinate-controls.json"
    coordinate_path.write_bytes(z.read(ROOT + SAVED[4]))
    provenance_path = imported / "provenance.json"
    provenance_path.write_text(json.dumps({**provenance,
        "source_artifact_id": ARTIFACT_ID, "source_artifact_name": ARTIFACT_NAME,
        "source_run_url":
            f"https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/{RUN_ID}",
        "summary_sha256": {k: v for k, v in digest_map.items()
                           if k != SAVED[3]},
        "coordinate_controls_sha256": sha(coordinate_path.read_bytes()),
        "proof_and_component_evidence_origin":
            "pinned original run; not current-run proofs"},
        indent=2, sort_keys=True) + "\n")
    # This summary reports provenance, not new proof execution. All source
    # classifications and the 16 prior setup failures remain in retained raw logs.
    composite = evidence / "pointer-drop-matrix"
    composite.mkdir()
    drop = summaries[SAVED[3]]
    drop["source_profile"] = provenance
    drop["imported_source_run_id"] = RUN_ID
    drop["imported_source_artifact_id"] = ARTIFACT_ID
    drop["current_run_proof_count"] = 0
    (composite / "summary.json").write_text(json.dumps(drop, indent=2,
        sort_keys=True) + "\n")
    print(json.dumps({"source_run_id": RUN_ID, "imported_s6_proofs": 13,
                      "imported_s6_admissions": 22,
                      "imported_coordinate_controls": len(coordinates),
                      "new_control_count": 16}))
    actual = [sys.executable,
        str(repo / "research/challenge-8/prepare-select-pointer-actual.py"),
        "--stock-home", str(args.stock_home), "--tool-home", str(args.tool_home),
        "--schema", str(args.schema), "--compiler-sysroot", args.compiler_sysroot,
        "--evidence", str(evidence / "actual-drop-integration"),
        "--component-summary", str(imported / SAVED[1]),
        "--constructor-summary", str(imported / SAVED[0]),
        "--intrinsic-summary", str(imported / SAVED[2]),
        "--drop-summary", str(composite / "summary.json"),
        "--imported-prerequisites", str(provenance_path),
        "--imported-v3-coordinate-controls", str(coordinate_path)]
    raise SystemExit(subprocess.run(actual, check=False).returncode)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    for name in ("original_run", "original_artifact", "current_environment",
                 "current_patch_identities", "current_specification_audit",
                 "preflight_summary", "stock_home", "tool_home"):
        parser.add_argument("--" + name.replace("_", "-"), type=Path)
    parser.add_argument("--compiler-sysroot")
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[2]
    if args.preflight_only:
        preflight(args, repo)
    else:
        for name in ("original_run", "original_artifact", "current_environment",
                     "current_patch_identities", "current_specification_audit",
                     "preflight_summary", "stock_home", "tool_home",
                     "compiler_sysroot"):
            require(getattr(args, name) is not None, f"--{name.replace('_', '-')} required")
        complete(args, repo)


if __name__ == "__main__":
    main()
