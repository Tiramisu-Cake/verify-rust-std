#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted-only replay of the corrected S7 forget diagnostic classifier.

Reads the immutable nine-case artifact from run 37669436220 and writes only a
separate replay-results directory.  It never runs VeriFast or rewrites source
or historical classification files.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys
from typing import Any
import zipfile


RUN_ID = "37669436220"
ARTIFACT_ID = "11503963988"
SOURCE_SHA = "a5ce1b5f71d2f0a2ecd1f74e44063ba079683b4d"
PROFILE = "experimental-source-linked-select-pointer-drop-v4"
ARCHIVE_SHA256 = "12c3f3f509fc845dd1aa1bb7d8b80f8fcf70e6ab6064af3436168f0b9489dd83"
ARCHIVE_PREFIX = "current/select-pointer/forget-guard-diagnostic/"
ARCHIVE_ENVIRONMENT = "current/select-pointer/environment.txt"
VARIANTS = (
    "helper_positive", "frame_positive", "false_assert", "wrong_post",
    "thread_loss", "thread_duplication", "frame_loss", "frame_duplication",
    "frame_wrong_value",
)
DECLARED_FUNCTIONS = (
    "checked_forget_guard", "checked_forget_guard_frame_probe",
)
OLD_CLASSIFICATION_SHA256 = {
    "helper_positive": "4f8de2c1349bf6646944fa08020d57500c841a6c1763934dd75dec4e3f48630e",
    "frame_positive": "e8f9efa91e4bc79c0bfce78e676b6c4bdb099e481071a04dde8932ed3601e76b",
    "false_assert": "434ef1d58b54fe295917c178950d18e3669da5d143b1646804f1a5c8eee623dc",
    "wrong_post": "da2b987b37b0a62b92a4816ecbfa02ce80197e4a994178a948b72edf2cd09fb5",
    "thread_loss": "08a8fc35dcd20a83bc0c5973e9e77676b5397f12d03b8164716320299e97884e",
    "thread_duplication": "a64670dd1b6483b7455d446271b4b7603a10a8978e20448301a70368bb2a691e",
    "frame_loss": "3e66eeb2e9be6cd0ed4f3560d669630044fab6e00f52f5d4c0c1214edcd05ae6",
    "frame_duplication": "f753b29fd0cad62aaf7ef1e5f05d95546139cf3c42fc8022020a7e45b2a6d512",
    "frame_wrong_value": "6940b2a9f37942ebaf35992d107b832b95219ad4cdf69a85768e86e436e7f611",
}
EXPECTED_MESSAGES = {
    "false_assert": ("Assertion might not hold. (Cannot prove false.)", "body_assertion"),
    "wrong_post": ("Cannot prove condition. (Cannot prove false.)", "postcondition"),
    "thread_loss": ("Function leaks heap chunks: thread_token(tid)", "leak"),
    "thread_duplication": ("No matching heap chunks: thread_token(tid)", "postcondition"),
    "frame_loss": ("Function leaks heap chunks: points_to<bool>(frame, flag)", "leak"),
    "frame_duplication": ("No matching heap chunks: points_to<bool>(frame, flag)", "postcondition"),
    "frame_wrong_value": ("Cannot prove false == true", "postcondition"),
}
EXPECTED_REPLAY = {
    "helper_positive": "INCONCLUSIVE",
    "frame_positive": "INCONCLUSIVE",
    "false_assert": "INTENDED_NEGATIVE",
    "wrong_post": "INTENDED_NEGATIVE",
    "thread_loss": "INTENDED_NEGATIVE",
    "thread_duplication": "INTENDED_NEGATIVE",
    "frame_loss": "INTENDED_NEGATIVE",
    "frame_duplication": "INTENDED_NEGATIVE",
    "frame_wrong_value": "INTENDED_NEGATIVE",
}


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_classifier(path: Path):
    spec = importlib.util.spec_from_file_location("forget_evidence_classifier", path)
    require(spec is not None and spec.loader is not None,
            f"cannot load classifier module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def require_hosted_linux() -> None:
    require(os.environ.get("GITHUB_ACTIONS") == "true" and
            os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted" and
            os.environ.get("RUNNER_OS") == "Linux",
            "forget classifier replay is restricted to GitHub-hosted Linux Actions")


def verify_archive_tree(root: Path, archive_path: Path) -> dict[str, Any]:
    """Pin the compact artifact and compare every selected disk file to it."""
    archive_path = archive_path.resolve(strict=True)
    archive_bytes = archive_path.read_bytes()
    archive_hash = sha(archive_bytes)
    require(archive_hash == ARCHIVE_SHA256,
            "compact artifact SHA-256 differs from the pinned run archive")
    root = root.resolve(strict=True)
    parent = root.parent
    disk_files: dict[str, bytes] = {}
    env_path = parent / "environment.txt"
    require(env_path.is_file() and not env_path.is_symlink(),
            "selected artifact environment file is missing or not regular")
    disk_files[ARCHIVE_ENVIRONMENT] = env_path.read_bytes()
    for path in root.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"symlink in selected evidence tree: {path}")
        if path.is_file():
            relative = path.relative_to(parent).as_posix()
            disk_files["current/select-pointer/" + relative] = path.read_bytes()

    with zipfile.ZipFile(archive_path, "r") as archive:
        names = archive.namelist()
        require(len(names) == len(set(names)), "compact archive contains duplicate member names")
        require(archive.testzip() is None, "compact archive CRC check failed")
        archive_files = {name for name in names if not name.endswith("/") and
                         (name == ARCHIVE_ENVIRONMENT or name.startswith(ARCHIVE_PREFIX))}
        require(archive_files == set(disk_files),
                "selected on-disk files differ from the pinned archive manifest")
        for name, content in disk_files.items():
            require(archive.read(name) == content,
                    f"selected on-disk bytes differ from pinned archive: {name}")
    return {"sha256": archive_hash, "compared_file_count": len(disk_files),
            "disk_tree_matches_archive": True}


def verify_input(root: Path, archive_path: Path, run_id: str,
                 artifact_id: str) -> dict[str, Any]:
    require(run_id == RUN_ID, f"expected immutable run {RUN_ID}")
    require(artifact_id == ARTIFACT_ID, f"expected immutable artifact {ARTIFACT_ID}")
    root = root.resolve(strict=True)
    archive_evidence = verify_archive_tree(root, archive_path)
    environment = (root.parent / "environment.txt").read_text(errors="replace")
    require(f"Source SHA: {SOURCE_SHA}\n" in environment,
            "input source SHA differs from pinned run")
    require(f"Profile: {PROFILE}\n" in environment,
            "input tool profile differs from pinned run")
    summary = json.loads((root / "summary.json").read_text())
    require(summary.get("classification") == "DIAGNOSTIC_ONLY" and
            summary.get("accepted_component") is False and
            summary.get("actual_redirected") is False,
            "input is not the immutable pre-redirect diagnostic artifact")
    raw_classifications: dict[str, bytes] = {}
    for variant in VARIANTS:
        case = root / variant
        classification_path = case / "classification.json"
        raw = classification_path.read_bytes()
        require(sha(raw) == OLD_CLASSIFICATION_SHA256[variant],
                f"historical classification changed: {variant}")
        classification = json.loads(raw)
        require(classification.get("classification") == "INCONCLUSIVE" and
                classification.get("accepted_component") is False,
                f"historical raw result is not preserved as inconclusive: {variant}")
        raw_classifications[variant] = raw
    require(len(summary.get("cases", [])) == len(VARIANTS),
            "input summary does not contain exactly the nine cases")
    return {"root": root, "summary_sha256": sha((root / "summary.json").read_bytes()),
            "old_classifications": raw_classifications,
            "archive": archive_evidence}


def source_declarations(case: Path) -> list[str]:
    text = (case / "verified/forget-items.rs").read_text()
    names = re.findall(r"^unsafe fn ([A-Za-z_][A-Za-z0-9_]*)<Element>",
                       text, flags=re.MULTILINE)
    return names


def verify_stage_integrity(case: Path, fixture: dict[str, Any]) -> bool:
    expected: dict[str, str] = {}
    for mode in ("original", "verified"):
        for name, digest in fixture["source_sha256"][mode].items():
            expected[f"{mode}/{name}"] = digest
            require(sha((case / mode / name).read_bytes()) == digest,
                    f"case source hash differs: {mode}/{name}")
    stage_paths = sorted(case.glob("*-stage.json"))
    require(bool(stage_paths), "case has no preserved stage records")
    frontend_stages = {"readonly-export", "readonly-decode", "normal-export",
                       "normal-decode", "refinement"}
    found_frontend: set[str] = set()
    for path in stage_paths:
        stage = json.loads(path.read_text())
        require(stage.get("source_unchanged") is True and
                stage.get("source_before") == expected and
                stage.get("source_after") == expected,
                f"source integrity stage mismatch: {path.name}")
        name = path.name.removesuffix("-stage.json")
        if name in frontend_stages:
            require(stage.get("exit") == 0,
                    f"front-end stage did not exit 0: {path.name}")
            found_frontend.add(name)
    require(found_frontend == frontend_stages,
            f"front-end stage evidence incomplete: {sorted(found_frontend)}")
    return True


def expected_error(variant: str, focus: dict[str, Any]) -> dict[str, Any] | None:
    if variant not in EXPECTED_MESSAGES:
        return None
    message, kind = EXPECTED_MESSAGES[variant]
    require(focus.get("expected_error_line") is not None,
            f"negative case missing expected line: {variant}")
    return {"file": focus["file"], "line": focus["expected_error_line"],
            "message": message, "function":
                "select_unpredictable::" + focus["function"], "kind": kind}


def replay_case(root: Path, variant: str, classifier) -> dict[str, Any]:
    case = root / variant
    fixture = json.loads((case / "fixture.json").read_text())
    focus = fixture["focus"]
    require(fixture.get("tool_profile") == PROFILE and
            fixture.get("v4_admission_active") is False and
            fixture.get("variant") == variant,
            f"fixture/profile mismatch: {variant}")
    declarations = source_declarations(case)
    require(declarations == list(DECLARED_FUNCTIONS),
            f"predeclared local function list differs: {variant}: {declarations}")
    verify_stage_integrity(case, fixture)
    stage = json.loads((case / "focused-verification-stage.json").read_text())
    argv = stage.get("argv", [])
    focus_arg = f"{focus['file']}:{focus['line']}"
    require("-focus" in argv and argv[argv.index("-focus") + 1] == focus_arg,
            f"verification focus differs from fixture: {variant}")
    log = (case / "verifast.log").read_text(errors="replace")
    target = "select_unpredictable::" + focus["function"]
    is_positive = focus["obligation"] == "body_return_leak"
    proof = classifier.classify_unit(
        log, int(stage["exit"]), [target], positive=is_positive,
        expected_error=expected_error(variant, focus))
    return {
        "variant": variant,
        "expected_predeclared_functions": list(DECLARED_FUNCTIONS),
        "predeclared_function_list_exact": declarations == list(DECLARED_FUNCTIONS),
        "focused_expected_function": target,
        "focus_matches_fixture": True,
        "proof": proof,
        "historical_classification_preserved": True,
        "historical_classification_sha256": sha(
            (case / "classification.json").read_bytes()),
    }


def ensure_separate_output(root: Path, output: Path) -> Path:
    root = root.resolve(strict=True)
    output = output.resolve(strict=False)
    require(output != root and root not in output.parents,
            "replay output must be outside the immutable input artifact")
    require(not output.exists(), "refuse to overwrite existing replay output")
    return output


def main() -> None:
    require_hosted_linux()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, required=True,
                        help="path to run artifact's forget-guard-diagnostic directory")
    parser.add_argument("--archive", type=Path, required=True,
                        help="pinned compact ZIP from the same Actions artifact")
    parser.add_argument("--output", type=Path, required=True,
                        help="new output directory outside the immutable artifact")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--artifact-id", required=True)
    parser.add_argument("--self-test", action="store_true",
                        help="run deterministic in-memory parser mutation checks first")
    args = parser.parse_args()
    root = args.evidence
    snapshot = verify_input(root, args.archive, args.run_id, args.artifact_id)
    output = ensure_separate_output(root, args.output)
    classifier = load_classifier(Path(__file__).with_name("forget-evidence-classifier.py"))
    mutation_result = classifier.self_test() if args.self_test else {
        "pass": True, "checks": {}, "executed": False}
    require(mutation_result.get("pass") is True,
            "classifier mutation self-test failed")

    results = [replay_case(snapshot["root"], variant, classifier)
               for variant in VARIANTS]
    actual_map = {item["variant"]: item["proof"]["classification"]
                  for item in results}
    require(actual_map == EXPECTED_REPLAY,
            f"replay classifications differ from pinned expected map: {actual_map}")
    # Re-read historical classifications after replay and compare raw bytes.
    preserved = all(
        (snapshot["root"] / variant / "classification.json").read_bytes() == raw
        for variant, raw in snapshot["old_classifications"].items())
    require(preserved, "replay changed a historical classifier output")
    output.mkdir(parents=True)
    for result in results:
        (output / f"{result['variant']}.json").write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n")
    summary = {
        "run_id": RUN_ID,
        "artifact_id": ARTIFACT_ID,
        "source_sha": SOURCE_SHA,
        "tool_profile": PROFILE,
        "input_summary_sha256": snapshot["summary_sha256"],
        "input_archive": snapshot["archive"],
        "old_classifications_preserved_byte_for_byte": preserved,
        "classifier_self_test": mutation_result,
        "cases": {item["variant"]: item["proof"]["classification"]
                  for item in results},
        "expected_cases": EXPECTED_REPLAY,
        "accepted_component": False,
        "full_select_proved": False,
        "results": results,
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2,
                                                     sort_keys=True) + "\n")
    print(json.dumps({"output": str(output),
                      "classifications": summary["cases"],
                      "old_classifications_preserved": preserved,
                      "mutation_self_test_pass": mutation_result["pass"]},
                     sort_keys=True))


if __name__ == "__main__":
    main()
