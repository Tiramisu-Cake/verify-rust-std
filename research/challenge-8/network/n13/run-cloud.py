#!/usr/bin/env python3
"""Cloud-only runner for the bounded N13 mathematical proof matrix.

This runner records observations and gate results. It does not grant Rust
safety, ownership, unwind, or Challenge proof credit.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import traceback
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
NETWORKS = HERE.parents[1] / "networks"
ROOT = HERE.parents[3]
PROFILE_RELATIVE = Path("research/challenge-8/cloud-build/network-n13/N13-EXECUTION-PROFILE-20261023-N3.json")
SOURCE_RELATIVE = Path("library/core/src/slice/sort/shared/smallsort.rs")
SOURCE_SHA256 = "85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1"
SOURCE_BLOB = "40939f922bcb6fdc7ee0d30427fa861827043827"
TOOL_SHA256 = "dc672335da76fe1bb06cf7ebca916185c34edb65466df0a937645a437c7f0ecc"
TOOL_ARCHIVE_SHA256 = "da1b619fa63ba73c12ce591638ced90fd2471add6f181d0e3310657fe4df98aa"
CALL_COUNTS = {9: 25, 13: 45}
STAGES = ("preflight", "exact", "controls", "regressions")
SHA_RE = re.compile(r"[0-9a-f]{64}\Z")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def evidence_snapshot(directory: Path) -> list[dict[str, Any]]:
    snapshot = []
    for path in sorted(directory.iterdir()):
        if path.name == "results.json" or not path.is_file():
            continue
        raw = path.read_bytes()
        snapshot.append({"name": path.name, "size": len(raw), "sha256": digest(raw)})
    return snapshot


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module {name} from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_dependencies():
    sys.path.insert(0, str(NETWORKS))
    prove = load_module("n13_cloud_prove", NETWORKS / "prove.py")
    # prove-ranks imports `prove`, so bind the same source-bound module.
    sys.modules["prove"] = prove
    ranks = load_module("n13_cloud_prove_ranks", NETWORKS / "prove-ranks.py")
    return prove, ranks


def load_profile(environ: dict[str, str]) -> tuple[dict[str, Any], dict[str, str]]:
    infra_root = Path(environ.get("INFRA_ROOT", "/workspace/infra")).resolve()
    path = infra_root / PROFILE_RELATIVE
    raw = path.read_bytes()
    actual_sha = digest(raw)
    expected_sha = environ.get("NETWORK_PROFILE_SHA256", "")
    require(SHA_RE.fullmatch(expected_sha) is not None, "NETWORK_PROFILE_SHA256 must be set to a SHA256")
    require(actual_sha == expected_sha, "execution profile SHA256 mismatch")
    profile = json.loads(raw)
    require(isinstance(profile, dict), "execution profile must be an object")
    require(profile.get("schema") == "smallsort-network-n13-execution-profile-v1",
            "unexpected execution profile schema")
    require(profile.get("status") == "REVIEWED_PINNED", "execution profile is not reviewed and pinned")
    require(profile.get("accepted") is True and profile.get("proof_credit") is False,
            "execution profile admission fields are invalid")
    return profile, {"path": str(path), "sha256": actual_sha}


def source_identity(prove, pairs: list[tuple[int, int]], lines: list[int]) -> dict[str, Any]:
    path = Path(prove.SOURCE).resolve()
    raw = path.read_bytes()
    require(path == (ROOT / SOURCE_RELATIVE).resolve(), "actual SmallSort source path mismatch")
    require(digest(raw) == SOURCE_SHA256 == prove.SOURCE_SHA256,
            "actual SmallSort source SHA256 mismatch")
    blob = subprocess.check_output(["git", "hash-object", str(path)], cwd=ROOT, text=True).strip()
    require(blob == SOURCE_BLOB, "actual SmallSort source blob mismatch")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    require(len(pairs) == CALL_COUNTS[13] and len(lines) == CALL_COUNTS[13],
            "current-source exact N13 schedule count mismatch")
    require(all(type(a) is int and type(b) is int and 0 <= a < b < 13 for a, b in pairs),
            "current-source exact N13 schedule contains invalid indexes")
    return {
        "commit": commit,
        "path": str(SOURCE_RELATIVE),
        "git_blob": blob,
        "sha256": digest(raw),
        "call_count": len(pairs),
        "schedule_sha256": digest(json.dumps(
            [{"step": i + 1, "a": a, "b": b, "line": lines[i]}
             for i, (a, b) in enumerate(pairs)], sort_keys=True, separators=(",", ":")).encode()),
        "calls": [{"step": i + 1, "a": a, "b": b, "line": lines[i]}
                  for i, (a, b) in enumerate(pairs)],
    }


def tool_identity(tool_home: Path, profile: dict[str, Any]) -> dict[str, Any]:
    configured = profile.get("tool")
    require(isinstance(configured, dict), "profile tool record missing")
    relative_tool = configured.get("console_path")
    require(isinstance(relative_tool, str) and relative_tool == "bin/verifast",
            "profile console path is outside the pinned tool layout")
    tool = (tool_home / relative_tool).resolve(strict=True)
    require(tool.is_file(), "pinned VeriFast console is not a file")
    raw = tool.read_bytes()
    actual = digest(raw)
    require(actual == TOOL_SHA256, "stock VeriFast 26.09 console SHA256 mismatch")
    require(configured.get("console_sha256") == actual, "profile console SHA256 differs from tool")
    require(configured.get("source_commit") == "809de4596839b739dd999f9e462242c835e3af46",
            "profile is not pinned to stock VeriFast 26.09")
    require(configured.get("archive_sha256") == TOOL_ARCHIVE_SHA256,
            "profile archive SHA256 differs from the pinned stock VeriFast archive")
    require(configured.get("args") == ["-c", "-verbose", "1"],
            "profile verifier arguments differ from the pinned recipe")
    require(configured.get("patches") == [], "tool patches are outside this task")
    return {"path": str(tool), "sha256": actual, "profile": configured.get("profile"),
            "source_commit": configured.get("source_commit"), "archive_sha256": configured.get("archive_sha256"),
            "args": configured.get("args"), "patches": configured.get("patches")}


def matrix(stage: str, prove, ranks, pairs: list[tuple[int, int]]) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []

    def add(name: str, source: str, target: str, timeout: int, negative: dict | None = None):
        require(isinstance(source, str) and source.strip(), f"generator returned no source for {name}")
        cases.append({"name": name, "source": source, "target": target,
                      "timeout_seconds": timeout, "negative": negative})

    if stage == "preflight":
        add("network13_generic_swo_bridge", ranks.generic_bridge(), "generic-swo-bridge", 180)
        add("network13_domain13_members", ranks.domain13_members(), "domain13-members", 180)
    elif stage == "exact":
        add("network13_finite_swo_order", ranks.composition(13, pairs, True), "exact-n13-full-post", 300)
    elif stage == "controls":
        source, metadata = ranks.negative_missing_equiv_trans()
        add("network13_negative_missing_equiv_trans", source, "missing-equiv-trans", 180, metadata)
        for kind in ("membership", "order"):
            source, metadata = ranks.negative_exact_post(kind, pairs)
            add(f"network13_negative_exact_{kind}", source, f"exact-n13-{kind}-post", 300, metadata)
    elif stage == "regressions":
        pairs9, _lines9 = prove.extract(9)
        add("network9_finite_swo_order", ranks.composition(9, pairs9, True), "exact-n9-regression", 180)
        add("network13_symbolic_swo_composition", ranks.composition(13, pairs, False),
            "universal-n13-regression", 240)
    else:
        raise RuntimeError(f"unknown stage: {stage}")
    return cases


def validate_result(result: Any, spec: dict[str, Any], source_sha: str) -> tuple[bool, dict[str, Any]]:
    """Fail closed on malformed run_case results while retaining their raw fields."""
    if not isinstance(result, dict):
        return False, {"runner_error": "run_case result must be an object", "raw_result_type": type(result).__name__}
    observed = dict(result)
    required = ("case", "negative", "exit", "source_sha256", "log_sha256", "source_unchanged", "accepted",
                "expected_bodies", "visited_bodies", "errors", "leak_checks", "return_checks")
    missing = [key for key in required if key not in result]
    if missing:
        observed["runner_error"] = "run_case result missing fields: " + ", ".join(missing)
        return False, observed
    if (result["case"] != spec["name"] or result["negative"] != spec["negative"] or
            type(result["exit"]) is not int or result["source_sha256"] != source_sha or
            not isinstance(result["log_sha256"], str) or SHA_RE.fullmatch(result["log_sha256"]) is None or
            type(result["source_unchanged"]) is not bool or type(result["accepted"]) is not bool or
            not isinstance(result["expected_bodies"], list) or
            not isinstance(result["visited_bodies"], list) or
            not isinstance(result["errors"], list) or type(result["leak_checks"]) is not int or
            type(result["return_checks"]) is not int):
        observed["runner_error"] = "run_case result contains null or wrong-typed fields"
        return False, observed
    bodies = result["expected_bodies"]
    visited = result["visited_bodies"]
    if not bodies or any(not isinstance(x, str) for x in bodies) or visited != bodies:
        observed["runner_error"] = "body inventory is incomplete or mismatched"
        return False, observed
    if result["source_unchanged"] is not True:
        observed["runner_error"] = "generated source changed during verification"
        return False, observed
    negative = spec["negative"]
    if negative is None:
        valid = (result["accepted"] is True and result["exit"] == 0 and not result["errors"] and
                 result["leak_checks"] >= len(bodies) and result["return_checks"] >= len(bodies))
    else:
        controls = result.get("classifier_rejection_controls")
        valid = (result["accepted"] is True and result["exit"] == 1 and len(result["errors"]) == 1 and
                 result["leak_checks"] >= len(bodies) - 1 and result["return_checks"] >= len(bodies) - 1 and
                 isinstance(controls, dict) and len(controls) == 7 and
                 set(controls) == {"other_line", "other_predicate", "no_body_execution",
                                   "no_target_execution", "other_column", "timeout", "source_changed"} and
                 all(value is True for value in controls.values()))
        expected_bodies = negative.get("expected_bodies")
        if expected_bodies is not None:
            valid = valid and bodies == expected_bodies
        target_line = negative.get("target_line")
        if type(target_line) is not int or target_line <= 0:
            valid = False
    if not valid:
        observed["runner_error"] = observed.get("runner_error", "case acceptance gate failed")
    return bool(valid), observed


def main(argv: list[str] | None = None, environ: dict[str, str] | None = None,
         dependencies=None) -> int:
    environ = dict(os.environ if environ is None else environ)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool-home", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--stage", choices=STAGES, required=True)
    args = parser.parse_args(argv)
    evidence = args.evidence.resolve()
    if evidence.exists():
        require(not evidence.is_symlink() and evidence.is_dir(),
                "evidence path must be a regular directory")
        require(not any(evidence.iterdir()), "evidence directory must be empty")
    else:
        evidence.mkdir(parents=True)
    summary: dict[str, Any] = {
        "schema": "smallsort-network-n13-cloud-run-v1", "stage": args.stage,
        "proof_credit": False, "complete": False, "cases": [], "errors": [],
    }

    def save():
        (evidence / "results.json").write_text(json.dumps(summary, indent=2, sort_keys=True, default=str) + "\n")

    save()
    try:
        infra_root = Path(environ.get("INFRA_ROOT", "/workspace/infra")).resolve()
        provider = load_module("n13_cloud_provider", infra_root / "research/challenge-8/cloud-build/provider.py")
        provider_identity = provider.require_supported_provider()
        require(isinstance(provider_identity, dict) and provider_identity.get("provider") == "cloud-build",
                "Cloud Build provider required")
        profile, profile_identity = load_profile(environ)
        require(profile.get("source", {}).get("sha256") == SOURCE_SHA256,
                "execution profile source SHA256 mismatch")
        require(profile.get("source", {}).get("git_blob") == SOURCE_BLOB,
                "execution profile source blob mismatch")
        summary["execution_profile"] = profile_identity
        summary["provider"] = provider_identity
        prove, ranks = dependencies if dependencies is not None else load_dependencies()
        pairs, lines = prove.extract(13)
        summary["source"] = source_identity(prove, pairs, lines)
        summary["tool"] = tool_identity(args.tool_home.resolve(), profile)
        stage_profile = profile.get("stages", {}).get(args.stage)
        if not isinstance(stage_profile, dict):
            known_targets = profile.get("stages", {})
            if isinstance(known_targets, dict) and args.stage in STAGES:
                summary["cases"].append({"name": args.stage, "state": "NOT_RUN",
                                         "reason": "execution profile has no stage record"})
            raise RuntimeError("execution profile has no stage record")
        specs = matrix(args.stage, prove, ranks, pairs)
        expected_targets = stage_profile.get("targets")
        actual_targets = [s["target"] for s in specs]
        if args.stage == "controls":
            actual_targets.append("classifier-reject-controls-7")
        summary["cases"] = [{"name": spec["name"], "target": spec["target"],
                             "generated_sha256": digest(spec["source"].encode()),
                             "timeout_seconds": spec["timeout_seconds"], "state": "NOT_RUN",
                             "reason": "stage admission pending"} for spec in specs]
        if not isinstance(expected_targets, list) or expected_targets != actual_targets:
            for row in summary["cases"]:
                row["reason"] = "execution profile target list mismatch"
            raise RuntimeError("execution profile target list mismatch")
        limit = stage_profile.get("timeout_seconds")
        if type(limit) is not int or sum(s["timeout_seconds"] for s in specs) > limit or limit > 1200:
            for row in summary["cases"]:
                row["reason"] = "stage case timeout envelope is invalid"
            raise RuntimeError("stage case timeout envelope is invalid")
        summary["targets"] = [{"name": s["name"], "target": s["target"],
                               "generated_sha256": digest(s["source"].encode()),
                               "timeout_seconds": s["timeout_seconds"]} for s in specs]
        if args.stage == "controls":
            summary["targets"].append({
                "name": "classifier-reject-controls-7", "target": "classifier-reject-controls-7",
                "controls": ["other_line", "other_predicate", "no_body_execution",
                             "no_target_execution", "other_column", "timeout", "source_changed"],
                "generated_sha256": digest(json.dumps(
                    ["other_line", "other_predicate", "no_body_execution", "no_target_execution",
                     "other_column", "timeout", "source_changed"], separators=(",", ":")).encode()),
                "timeout_seconds": 0,
            })
        summary["stage_timeout_seconds"] = limit
        save()
        for spec, row in zip(specs, summary["cases"]):
            row.pop("reason", None)
            row["snapshot_before"] = evidence_snapshot(evidence)
            row["state"] = "RUNNING"
            save()
            original_timeout = prove.TIMEOUT_SECONDS
            try:
                prove.TIMEOUT_SECONDS = spec["timeout_seconds"]
                result = prove.run_case((args.tool_home.resolve() / "bin/verifast").resolve(), evidence,
                                        spec["name"], spec["source"], spec["negative"])
                valid, result_record = validate_result(result, spec, row["generated_sha256"])
                row["result"] = result_record
                row["state"] = "OBSERVED_VALID" if valid else "INCONCLUSIVE"
                row["gate"] = valid
            except BaseException as exc:
                row["state"] = "ERROR"
                row["exception"] = {"type": type(exc).__name__, "message": str(exc),
                                    "traceback": traceback.format_exc()}
                for field in ("returncode", "output", "stderr"):
                    value = getattr(exc, field, None)
                    if value is not None:
                        row["exception"][field] = value.decode(errors="replace") if isinstance(value, bytes) else value
                if isinstance(exc, SystemExit):
                    row["exit"] = exc.code
            finally:
                prove.TIMEOUT_SECONDS = original_timeout
                row["snapshot_after"] = evidence_snapshot(evidence)
                save()
        summary["complete"] = (len(summary["cases"]) == len(specs) and bool(specs) and
                               all(row.get("gate") is True for row in summary["cases"]))
    except BaseException as exc:
        summary["errors"].append({"type": type(exc).__name__, "message": str(exc),
                                  "traceback": traceback.format_exc()})
        if isinstance(exc, SystemExit):
            summary["errors"][-1]["exit"] = exc.code
    finally:
        save()
    print("NETWORK_N13_RUN", json.dumps({"stage": args.stage, "complete": summary["complete"],
                                         "case_count": len(summary["cases"]),
                                         "error_count": len(summary["errors"])}), flush=True)
    return 0 if summary["complete"] else 2


if __name__ == "__main__":
    sys.exit(main())
