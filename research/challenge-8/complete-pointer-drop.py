#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted S6 completion from pinned same-profile evidence and three new controls.

Saved proofs are classified again from their original logs; only previously
misconfigured admission controls execute. Every imported proof keeps its run ID.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
from pathlib import PurePosixPath
import re
import shutil
import subprocess
import sys
import zipfile


def require(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot load {path.name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def tool_hashes(environment: str) -> dict[str, str]:
    require("Schema and effective profile hashes:\n" in environment and
            "Stock identities:\n" in environment, "missing effective tool section")
    section = environment.split("Schema and effective profile hashes:\n", 1)[1]
    section = section.replace("Stock identities:\n", "", 1)
    hashes = {}
    for line in section.splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  (/.+)", line)
        require(match is not None, "invalid effective tool hash line")
        digest, path = match.groups()
        if "/source/" in path:
            key = "source/" + path.split("/source/", 1)[1]
        elif "/verifast-26.09/" in path:
            key = "stock/" + path.split("/verifast-26.09/", 1)[1]
        else:
            raise ValueError("unknown effective tool path")
        require(key not in hashes, f"duplicate effective tool key: {key}")
        hashes[key] = digest
    required = {
        "source/src/rust_frontend/vf_mir/vf_mir.capnp",
        "source/bin/verifast", "source/bin/vf-rust-mir-exporter",
        "source/bin/refinement-checker", "source/bin/vf-cxx-ast-exporter",
        "source/bin/libz3.so", "source/bin/rust/std/lib.rsspec",
        "stock/bin/verifast", "stock/bin/vf-rust-mir-exporter",
        "stock/bin/refinement-checker",
    }
    require(required <= hashes.keys() and
            len([key for key in hashes if key.endswith(".rsspec")]) >= 10,
            "effective tool hash set incomplete")
    return hashes


def validate_profile(z: zipfile.ZipFile, args: argparse.Namespace,
                     repo: Path, replay) -> dict:
    old = z.read(replay.ROOT + "environment.txt").decode()
    current = args.current_environment.read_text()
    require("Profile: " + replay.PROFILE in current and
            replay.PATCH_SHA in current, "new runner profile/patch differs")
    for label in ("Base source", "Compiler", "Target"):
        old_line = next((line for line in old.splitlines()
                         if line.startswith(label + ": ")), None)
        current_line = next((line for line in current.splitlines()
                             if line.startswith(label + ": ")), None)
        require(old_line is not None and old_line == current_line,
                f"{label} differs from original proof environment")
    old_versions = old.split("rustc 1.", 1)[1].split(
        "Schema and effective profile hashes:\n", 1)[0]
    current_versions = current.split("rustc 1.", 1)[1].split(
        "Schema and effective profile hashes:\n", 1)[0]
    require(old_versions == current_versions,
            "hosted compiler and tool version identities differ")
    old_tools, new_tools = tool_hashes(old), tool_hashes(current)
    require(old_tools == new_tools,
            "effective tool byte hashes differ: " +
            ", ".join(sorted(key for key in old_tools.keys() | new_tools.keys()
                             if old_tools.get(key) != new_tools.get(key))))
    for name, current_path in (
        ("patch-source-identities.json", args.current_patch_identities),
        ("specification-audit.json", args.current_specification_audit),
    ):
        require(json.loads(z.read(replay.ROOT + name)) ==
                json.loads(current_path.read_bytes()),
                f"current {name} differs from original proof profile")
    require(sha((repo / "research/challenge-8/verifast-select-pointer-drop.patch").read_bytes())
            == replay.PATCH_SHA, "current semantic patch changed")
    source_files = {
        "constructor-regressions/source-certificate.json":
            {"hint": "library/core/src/hint.rs",
             "manually_drop": "library/core/src/mem/manually_drop.rs",
             "maybe_dangling": "library/core/src/mem/maybe_dangling.rs",
             "maybe_uninit": "library/core/src/mem/maybe_uninit.rs"},
        "matrix/source-certificate.json":
            {"source": "library/core/src/mem/maybe_uninit.rs"},
        "intrinsic-matrix/source-certificate.json":
            {"source": "library/core/src/intrinsics/mod.rs"},
        "pointer-drop-matrix/source-certificate.json":
            {"method_source": "library/core/src/ptr/mut_ptr.rs",
             "compiler_glue_source": "library/core/src/ptr/mod.rs"},
    }
    source_digests = {}
    for cert_name, mapping in source_files.items():
        cert = json.loads(z.read(replay.ROOT + cert_name))
        for key, source_path in mapping.items():
            expected = (cert["files"][key]["sha256"] if key in
                        {"hint", "manually_drop", "maybe_dangling", "maybe_uninit"}
                        else cert[key + "_sha256"])
            actual = sha((repo / source_path).read_bytes())
            require(expected == actual, f"same-profile std source changed: {source_path}")
            source_digests[source_path] = actual
    return {"source_run_id": replay.RUN_ID, "source_sha": replay.SOURCE_SHA,
            "profile": replay.PROFILE, "patch_sha256": replay.PATCH_SHA,
            "archive_sha256": replay.ARCHIVE_SHA,
            "effective_tool_hashes": old_tools, "std_source_hashes": source_digests}


def copy_prerequisites(z: zipfile.ZipFile, evidence: Path, replay,
                       provenance: dict) -> tuple[Path, Path, Path, Path]:
    imported = evidence / "imported-prerequisites"
    imported.mkdir()
    paths = []
    digest_map = {}
    for rel in ("constructor-regressions/summary.json", "matrix/summary.json",
                "intrinsic-matrix/summary.json"):
        content = z.read(replay.ROOT + rel)
        path = imported / rel
        path.parent.mkdir(parents=True)
        path.write_bytes(content)
        digest_map[rel] = sha(content)
        paths.append(path)
    manifest = imported / "provenance.json"
    manifest.write_text(json.dumps({**provenance,
        "source_artifact_id": replay.ARTIFACT_ID,
        "source_artifact_name": replay.ARTIFACT_NAME,
        "source_run_url": f"https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/{replay.RUN_ID}",
        "summary_sha256": digest_map,
        "proof_and_component_evidence_origin": "pinned original run; not current-run proofs",
    }, indent=2, sort_keys=True) + "\n")
    return (*paths, manifest)


def retain_saved_profile(z: zipfile.ZipFile, evidence: Path, replay) -> dict:
    """Keep original raw logs/MIR/metadata in the new compact artifact."""
    target = evidence / "saved-profile-evidence"
    target.mkdir()
    manifest = z.read("COMPACT-EVIDENCE-MANIFEST.json")
    (target / "COMPACT-EVIDENCE-MANIFEST.json").write_bytes(manifest)
    count = 0
    byte_count = len(manifest)
    entries = {}
    for name in z.namelist():
        if not name.startswith(replay.ROOT) or name.endswith("/"):
            continue
        relative = PurePosixPath(name)
        require(not relative.is_absolute() and ".." not in relative.parts,
                "unsafe saved evidence path")
        content = z.read(name)
        path = target.joinpath(*relative.parts)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        entries[name] = sha(content)
        count += 1
        byte_count += len(content)
    require(count > 0, "original profile evidence absent")
    report = {"source_run_id": replay.RUN_ID,
              "source_artifact_id": replay.ARTIFACT_ID,
              "source_archive_sha256": replay.ARCHIVE_SHA,
              "original_manifest_sha256": sha(manifest),
              "retained_entry_count": count,
              "retained_uncompressed_bytes": byte_count,
              "retained_entry_sha256": entries,
              "classification": "raw original evidence; not current-run proofs"}
    (target / "retention-report.json").write_text(json.dumps(report, indent=2,
        sort_keys=True) + "\n")
    return report


def run_controls(args: argparse.Namespace, evidence: Path, repo: Path,
                 matrix, constructor, diagnostic) -> list[dict]:
    body, source_cert = diagnostic.source_certificate(repo, constructor)
    controls = evidence / "new-hosted-controls"
    controls.mkdir()
    results = []
    for mode, mutation in (("source", "input_type"),
                           ("mir", "output_type"),
                           ("mir", "contract")):
        label = f"{mode}_{mutation}"
        case = controls / label
        try:
            matrix.make_case(case, matrix.POSITIVES[0], source_cert, body,
                             constructor, admission=mutation if mode == "source" else None)
            home = (matrix.make_mir_mutation_tool_home(
                args.tool_home, args.schema, repo, case, mutation)
                if mode == "mir" else args.tool_home)
            runner = matrix.run_hosted_case(case, args, repo, constructor, home)
            result = matrix.classify_admission(case, runner, mutation, mode,
                                               constructor)
        except Exception as exc:
            case.mkdir(parents=True, exist_ok=True)
            result = {"mode": mode, "mutation": mutation,
                      "classification": "INCONCLUSIVE", "accepted_component": False,
                      "harness_exception": f"{type(exc).__name__}: {exc}"}
            (case / "admission-classification.json").write_text(
                json.dumps(result, indent=2, sort_keys=True) + "\n")
        results.append(result)
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("archive", "original_run", "original_artifact",
                 "current_environment", "current_patch_identities",
                 "current_specification_audit", "classifier_summary", "stock_home",
                 "tool_home", "schema", "evidence"):
        parser.add_argument("--" + name.replace("_", "-"), type=Path, required=True)
    parser.add_argument("--compiler-sysroot", required=True)
    args = parser.parse_args()
    require(os.environ.get("GITHUB_ACTIONS") == "true" and
            os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted" and
            os.environ.get("RUNNER_OS") == "Linux", "GitHub-hosted Linux required")
    repo = Path(__file__).resolve().parents[2]
    scripts = repo / "research/challenge-8"
    replay = load(scripts / "replay-pointer-drop.py", "drop_saved_replay")
    matrix = load(scripts / "check-pointer-drop.py", "drop_completion_matrix")
    constructor = load(scripts / "check-maybeuninit-new-pointer.py", "drop_completion_constructor")
    diagnostic = load(scripts / "prepare-pointer-drop-diagnostic.py", "drop_completion_source")
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=False)
    require(args.archive.is_file() and
            sha(args.archive.read_bytes()) == replay.ARCHIVE_SHA,
            "original compact artifact byte hash differs")
    with zipfile.ZipFile(args.archive) as z:
        replay.verify_manifest(z)
        provenance = validate_profile(z, args, repo, replay)
        retained = retain_saved_profile(z, evidence, replay)
        ctor, asptr, intrinsic, manifest = copy_prerequisites(
            z, evidence, replay, provenance)
    replay_dir = evidence / "pointer-drop-replay"
    replay_dir.mkdir()
    shutil.copyfile(args.original_run, replay_dir / "original-run.json")
    shutil.copyfile(args.original_artifact, replay_dir / "original-artifact.json")
    shutil.copyfile(args.classifier_summary, replay_dir / "classifier-self-check.json")
    replay_result = replay.replay(argparse.Namespace(
        archive=args.archive, evidence=replay_dir))
    results = run_controls(args, evidence, repo, matrix, constructor, diagnostic)
    corrected = replay_dir / "corrected"
    proof_files = sorted(corrected.glob("pointer_drop_*.json"))
    admission_files = sorted(path for path in corrected.glob("*.json")
                             if not path.name.startswith("pointer_drop_"))
    proof = [json.loads(path.read_text()) for path in proof_files]
    admission = [json.loads(path.read_text()) for path in admission_files]
    require(len(proof) == len(matrix.POSITIVES + matrix.NEGATIVES) and
            len(admission) == len(matrix.SOURCE_MUTATIONS + matrix.MIR_MUTATIONS +
                                  matrix.PIN_MUTATIONS) - 3,
            "replayed case count differs from complete matrix")
    admission += results
    accepted = (replay_result["classification"] ==
                "REPLAY_PARTIAL_PENDING_THREE_HOSTED_CONTROLS" and
                all(item["classification"] == "DIAGNOSTIC_POSITIVE" for item in proof
                    if item["variant"] in matrix.POSITIVES) and
                all(item["classification"] == "INTENDED_PROOF_REJECTION" for item in proof
                    if item["variant"] in matrix.NEGATIVES) and
                len(admission) == 22 and
                all(item["classification"] == "INTENDED_ADMISSION_REJECTION"
                    for item in admission))
    complete = evidence / "pointer-drop-matrix"
    complete.mkdir()
    summary = {
        "classification": "COMPONENT_ACCEPTED" if accepted else "INCONCLUSIVE",
        "accepted_component": accepted, "full_select_proved": False,
        "tool_profile": replay.PROFILE, "source_profile": provenance,
        "replayed_proofs_source_run": replay.RUN_ID,
        "replayed_admissions_source_run": replay.RUN_ID,
        "new_controls_run": os.environ.get("GITHUB_RUN_ID"),
        "original_classifications_preserved_at": str(replay_dir / "original"),
        "original_raw_evidence_retention": {
            "source_run_id": retained["source_run_id"],
            "retained_entry_count": retained["retained_entry_count"],
            "retention_report": str(evidence / "saved-profile-evidence/retention-report.json"),
        },
        "cases": proof, "admission_cases": admission,
        "new_hosted_control_count": len(results),
        "source_proof_case_count": len(proof),
        "source_admission_case_count": len(admission_files),
        "prerequisites": {"same_profile_byte_identical": True,
                          "source_std_identical": True,
                          "original_matrix_replayed": True},
    }
    (complete / "summary.json").write_text(json.dumps(summary, indent=2,
        sort_keys=True) + "\n")
    print(json.dumps({"S6_classification": summary["classification"],
                      "proofs_imported": len(proof),
                      "admissions_imported": len(admission_files),
                      "admissions_new": len(results)}))
    if not accepted:
        raise SystemExit(1)
    actual = [sys.executable, str(scripts / "prepare-select-pointer-actual.py"),
        "--stock-home", str(args.stock_home), "--tool-home", str(args.tool_home),
        "--schema", str(args.schema), "--compiler-sysroot", args.compiler_sysroot,
        "--evidence", str(evidence / "actual-drop-integration"),
        "--component-summary", str(asptr), "--constructor-summary", str(ctor),
        "--intrinsic-summary", str(intrinsic), "--drop-summary",
        str(complete / "summary.json"), "--imported-prerequisites", str(manifest)]
    raise SystemExit(subprocess.run(actual, check=False).returncode)


if __name__ == "__main__":
    main()
