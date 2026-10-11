#!/usr/bin/env python3
"""Replay selected MIR admission on saved b229 data; never invokes toolchains."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
AUDITOR = HERE / "selected-proof.py"
RAW = Path("/tmp/select-binding-prefix-b229-raw/allprooflogs/cases/sort4-c1-current-recovery")
BUILD_ID = "b22985f8-7aae-4058-9e3e-bae10f222a6f"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_auditor():
    spec = importlib.util.spec_from_file_location("selected_proof_replay", AUDITOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load selected-proof parser")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def replay_case(auditor, case: str, target: str, caller: str,
                query: bool, source_path: Path, mir_dir: Path,
                maps: dict) -> dict:
    paths = {mode: mir_dir / (mode + "-mir.txt")
             for mode in ("normal", "readonly")}
    result = auditor.full_mir_admission(
        paths, source_path.read_text(), caller, query_fixture=query,
        local_maps=maps)
    return {"case": case, "target": target,
            "source_sha256": sha(source_path),
            "mir_sha256": result["mir_sha256"],
            "raw_per_mode_maps": result["raw_per_mode_maps"],
            "normal_readonly_semantic_equality":
                result["normal_readonly_semantic_equality"],
            "semantic_calls": auditor.semantic_mir_calls(result["structural_summary"]),
            "negative_controls": result["negative_controls"],
            "admission": "PASS", "proof_credit": False}


def main() -> None:
    auditor = load_auditor()
    query_dir = RAW / "compiler-binding"
    query_maps = {mode: {"root": ["_16", "_17", "_18"],
                         "helper": ["_5", "_6", "_7"]}
                  for mode in ("normal", "readonly")}
    query = replay_case(
        auditor, "binding_selected_freeze", "binding_selected_freeze",
        "binding_selected_freeze", True,
        query_dir / "normal-fixture/verified/lib.rs", query_dir, query_maps)

    positive_dir = RAW / "cases/selected-branch-positive"
    positive_maps = {
        "normal": {"root": ["_17", "_18", "_19"],
                   "helper": ["_5", "_6", "_7"]},
        "readonly": {"root": ["_16", "_17", "_18"],
                     "helper": ["_5", "_6", "_7"]},
    }
    positive = replay_case(
        auditor, "selected-branch-positive", "selected_freeze_basecase",
        "selected_freeze_basecase", False,
        positive_dir / "fixture/verified/lib.rs",
        positive_dir / "pre-binding", positive_maps)
    if query["semantic_calls"] != positive["semantic_calls"]:
        raise RuntimeError("consumer/query semantic MIR call graphs differ")
    positive["query_graph_semantic_match"] = True
    query["query_graph_semantic_match"] = True

    old = json.loads((RAW / "selected-proof-audit.json").read_text())
    raw_manifest = RAW.parents[2] / "manifest.json"
    manifest = json.loads(raw_manifest.read_text())
    report = {
        "replay_kind": "saved-data-classifier-parser-only",
        "build_id": BUILD_ID,
        "replay_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python3 research/challenge-8/cloud-build/sort4-caller-entry-native/replay-selected-mir.py",
        "raw_root": str(RAW),
        "raw_manifest_sha256": sha(raw_manifest),
        "auditor_sha256": sha(AUDITOR),
        "original_input_identity": {
            "proof_sha": manifest.get("proof_sha"),
            "infra_sha": manifest.get("infra_sha"),
            "lane": manifest.get("lane"),
            "proof_image": manifest.get("proof_image"),
            "effective_profile_hashes": manifest.get("profile_hashes", {}).get(
                "allprooflogs/profile-hashes.json", {}).get("actual", {}),
            "effective_profile_hashes_sha256": manifest.get("profile_hashes", {}).get(
                "allprooflogs/profile-hashes.json", {}).get("actual_sha256"),
            "source_certificate_sha256": manifest.get("input_sha256", {}).get(
                "allprooflogs/cases/sort4-c1-current-recovery/actual-source-certificate.json"),
        },
        "previous_verdict_artifact_sha256": sha(
            RAW / "selected-proof-audit.json"),
        "previous_verdict": {
            "classification": old.get("classification"),
            "reason": old.get("reason"),
            "selected_consumer_binding_gate_open": old.get("binding_gate_open"),
            "proof_credit": old.get("proof_credit"),
        },
        "replayed": [query, positive],
        "not_replayed": {
            "selected-branch-false-bound-31": "NOT_RUN: no observed exact MIR local map",
            "selected-branch-missing-source-array": "NOT_RUN: no observed exact MIR local map",
        },
        "compiler_or_verifier_executed": False,
        "proof_credit": False,
    }
    out = HERE / "REPLAY-SELECTED-MIR-B229.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"result": str(out),
                      "previous_verdict": report["previous_verdict"],
                      "replayed": [{"case": row["case"],
                                    "admission": row["admission"],
                                    "mir_sha256": row["mir_sha256"]}
                                   for row in report["replayed"]],
                      "not_replayed": report["not_replayed"],
                      "proof_credit": False}, indent=2))


if __name__ == "__main__":
    main()
