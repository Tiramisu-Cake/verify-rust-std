#!/usr/bin/env python3
"""Replay the legacy mapping gate against extracted, immutable saved evidence."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path


CASES = ("prefix-native", "source-frame-positive", "bridge-positive",
         "range-negative", "duplicate-negative")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load service module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def replay(evidence_root: Path, repo_root: Path) -> dict:
    """Read saved artifacts and produce a compact no-proof-credit replay record."""
    extracted = evidence_root / "extracted"
    evidence = extracted / "allprooflogs/cases/sort4-caller-entry"
    manifest = json.loads((extracted / "manifest.json").read_text())
    source_input = json.loads((extracted / "source-input-certificate.json").read_text())
    previous = json.loads((evidence / "diagnostic-audit.json").read_text())
    collector_path = repo_root / "research/challenge-8/cloud-build/sort4-caller-entry.py"
    parser_path = repo_root / "research/challenge-8/cloud-build/strict-cut-false-posts-audit.py"
    collector = load_module(collector_path, "legacy_mapping_replay_collector")
    parser = load_module(parser_path, "legacy_mapping_replay_parser")
    original_auditor = next(row["sha256"] for row in source_input["infra"]["restored_paths"]
                            if row["path"] == "research/challenge-8/cloud-build/sort4-caller-entry.py")
    case_rows = {}
    for case in CASES:
        root = evidence / "cases" / case
        fixture = root / "fixture"
        cert = json.loads((root / "source-certificate.json").read_text())
        saved = json.loads((root / "case-result.json").read_text())
        log_path = fixture / "verification.log"
        log = log_path.read_text(errors="replace")
        entries = parser.proof_entries(log, "small_sort_general_with_scratch")
        entry = entries[0] if len(entries) == 1 else None
        mapping = collector.caller_mapping(
            root, fixture, cert,
            (root / "normal-full-prefix-mir.txt").read_text(),
            (root / "readonly-full-prefix-mir.txt").read_text(),
            log[entry:] if entry is not None else "", entry,
        )
        audit_row = previous["cases"][case]
        dead_code = [line for line in log.splitlines() if re.search(r"\): dead code$", line)]
        old_verdict = audit_row.get("classification")
        new_verdict = ("STRICT_DEAD_CODE_REJECTION_AFTER_SELECTED_PATH_FILTER"
                       if collector.legacy_dead_code_vf1(dead_code) else old_verdict)
        inputs = [root / "source-certificate.json", fixture / "actual-caller.rs",
                  fixture / "original/lib.rs", fixture / "verified/lib.rs", log_path,
                  root / "normal-full-prefix-mir.txt", root / "readonly-full-prefix-mir.txt"]
        case_rows[case] = {
            "old_case_verdict": old_verdict,
            "replayed_case_verdict": new_verdict,
            "verdict_change_reason": "VF1 dead-code refusal retained by current classifier" if new_verdict != old_verdict else None,
            "old_mapping_gate": audit_row.get("source_mir_proof_mapping", {}).get("status"),
            "replayed_mapping_gate": mapping.get("status"),
            "mapping_gate_unchanged": mapping.get("status") == audit_row.get("source_mir_proof_mapping", {}).get("status"),
            "verifier_exit": audit_row.get("verifier_exit"),
            "first_error": audit_row.get("first_error"),
            "dead_code_vf1_locations": dead_code,
            "proof_credit": False,
            "input_sha256": {str(path.relative_to(extracted)): sha(path) for path in inputs},
        }
    diagnostic_path = evidence / "diagnostic-audit.json"
    build_id = manifest.get("build_id")
    output = repo_root / "research/challenge-8/cloud-build/sort4-native-entry-c1/SERVICE-REPLAY-4A7EEDC5.json"
    command = ("python3 research/challenge-8/cloud-build/sort4-native-entry-c1/replay_legacy_mapping.py "
               f"--evidence-root {evidence_root} --repo-root {repo_root}")
    return {
        "classification": "SERVICE_REPLAY_NO_PROOF_CREDIT",
        "accepted": False,
        "proof_credit": "NONE",
        "build_id": build_id,
        "lane": manifest.get("lane"),
        "proof_sha": manifest.get("proof_sha"),
        "infra_sha": manifest.get("infra_sha"),
        "proof_image": manifest.get("proof_image"),
        "profile_hashes": manifest.get("profile_hashes"),
        "tool_snapshot_sha256": previous.get("tool_snapshot_sha256"),
        "source_input_archive_sha256": source_input.get("archive_sha256"),
        "previous_diagnostic_audit_sha256": sha(diagnostic_path),
        "original_auditor_sha256": original_auditor,
        "replay_auditor_sha256": sha(collector_path),
        "replay_command": command + f" --output {output}",
        "case_results": case_rows,
        "replay_scope": "Legacy mapping and VF1 classifier replay only; old evidence is read-only; no new proof result.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-root", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = replay(args.evidence_root, args.repo_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({case: {key: row[key] for key in (
        "old_case_verdict", "replayed_case_verdict", "old_mapping_gate",
        "replayed_mapping_gate", "verifier_exit", "proof_credit")}
        for case, row in result["case_results"].items()}, sort_keys=True))


if __name__ == "__main__":
    main()
