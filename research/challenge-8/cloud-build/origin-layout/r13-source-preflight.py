#!/usr/bin/env python3
"""Static R13 gate proving the normal R11 proof inputs remain byte-identical."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASELINE_COMMIT = "0c1d0d7861813bcc48d765eba869d30c2658f1cc"
BASELINE_RECIPE = "research/challenge-8/cloud-build/recipes/merge.json"
PROFILE_PATH = "research/challenge-8/cloud-build/origin-layout/GLUE-PROFILE.json"
TOOL_COMMIT = "660b576b6b1608db913c51e0785b443a8733396f"
PROFILE_SHA256 = "eb61e49397cd9973ec12d1675bd8bd4867c7374de22e7c1c6a8a58e991266375"
DISPATCHER_PATH = "research/challenge-8/cloud-build/run-merge.sh"
DISPATCHER_SHA256 = "128b5d83523b426e11a124cb768249bb48119f3f8be68f9a3499450a1adf1158"
FROZEN_COUNT = 158
FROZEN_PATHLIST_SHA256 = "1c76ea3f70d5a81fae6ddc36d9ee96fa823102debfd61d2b48dde669c9e8d7f4"
FROZEN_AGGREGATE_SHA256 = "00b6dd4757542c4ea01d29ccbfe632fd227610ff0ce6253cb5b6ebae00cc40da"
MODE_PATH = "research/challenge-8/cloud-build/origin-layout/R13-UPLOAD-MODE-20261021.json"
R13_ALLOWED = {
    MODE_PATH,
    "research/challenge-8/cloud-build/origin-layout/CURRENT-RECOVERY-R13-UPLOAD-BUDGET-20261021.json",
    "research/challenge-8/cloud-build/origin-layout/r13-phase-service-test.py",
    "research/challenge-8/cloud-build/origin-layout/r13-synthetic-upload.py",
    "research/challenge-8/cloud-build/origin-layout/r13-synthetic-upload-service-test.py",
    "research/challenge-8/cloud-build/origin-layout/r13-archive-size-guard.py",
    "research/challenge-8/cloud-build/origin-layout/r13-archive-size-guard-service-test.py",
    "research/challenge-8/cloud-build/origin-layout/r13-upload-config-service-test.py",
    "research/challenge-8/cloud-build/origin-layout/r13-source-preflight.py",
    "research/challenge-8/cloud-build/origin-layout/r13-source-preflight-service-test.py",
}
REQUIRED_R13 = R13_ALLOWED - {"research/challenge-8/cloud-build/origin-layout/r13-source-preflight-service-test.py"}
R12_ONLY = {
    "research/challenge-8/cloud-build/origin-layout/R12-UPLOAD-MODE-20261021.json",
    "research/challenge-8/cloud-build/origin-layout/CURRENT-RECOVERY-R12-UPLOAD-BUDGET-20261021.json",
    "research/challenge-8/cloud-build/origin-layout/r12-phase-service-test.py",
    "research/challenge-8/cloud-build/origin-layout/r12-synthetic-upload.py",
    "research/challenge-8/cloud-build/origin-layout/r12-synthetic-upload-service-test.py",
    "research/challenge-8/cloud-build/origin-layout/r12-upload-config-service-test.py",
    "research/challenge-8/cloud-build/origin-layout/r12-source-preflight.py",
    "research/challenge-8/cloud-build/origin-layout/r12-source-preflight-service-test.py",
}
GIT_SHA = re.compile(r"[0-9a-f]{40}\Z")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(ROOT), *args])


def frozen_paths() -> list[str]:
    raw = git("show", f"{BASELINE_COMMIT}:{BASELINE_RECIPE}")
    recipe = json.loads(raw)
    paths = recipe.get("proof_paths")
    if not isinstance(paths, list) or paths != sorted(set(paths)):
        raise ValueError("R13 baseline merge recipe is not canonical")
    return [p for p in paths
            if not p.endswith(".md") and "BUDGET" not in p.rsplit("/", 1)[-1].upper()]


def aggregate(paths: list[str], read_bytes) -> tuple[str, list[str]]:
    digest = hashlib.sha256()
    mismatches: list[str] = []
    for path in paths:
        try:
            content = read_bytes(path)
        except (OSError, subprocess.CalledProcessError, ValueError):
            mismatches.append(path)
            continue
        digest.update(path.encode("utf-8") + b"\0" + sha(content).encode("ascii") + b"\n")
    return digest.hexdigest(), mismatches


def read_worktree(path: str) -> bytes:
    target = ROOT / path
    if target.is_symlink() or not target.is_file():
        raise ValueError(f"frozen R11 path is missing or not a regular file: {path}")
    return target.read_bytes()


def validate_mode() -> None:
    mode_path = ROOT / MODE_PATH
    if mode_path.is_symlink() or not mode_path.is_file():
        raise ValueError("R13 upload mode card is missing or not a regular file")
    card = json.loads(mode_path.read_bytes())
    if not isinstance(card, dict) or card.get("schema") != "merge-r13-upload-mode-v1":
        raise ValueError("R13 upload mode card schema is invalid")
    mode = card.get("mode")
    if mode == "synthetic-upload":
        expected = {
            "schema": "merge-r13-upload-mode-v1", "mode": "synthetic-upload",
            "payload_bytes": 268435456, "threshold_bytes": 157286400,
            "archive_limit_bytes": 536870912,
            "threshold_source": "https://docs.cloud.google.com/storage/docs/parallel-composite-uploads",
            "proof_attempted": False,
        }
        if (set(card) != set(expected) or card != expected or
                type(card.get("payload_bytes")) is not int or
                type(card.get("threshold_bytes")) is not int or
                type(card.get("archive_limit_bytes")) is not int or
                card.get("proof_attempted") is not False):
            raise ValueError("R13 synthetic-upload mode card differs from its fixed contract")
    elif mode == "proof-r11":
        expected = {"schema": "merge-r13-upload-mode-v1", "mode": "proof-r11",
                    "archive_limit_bytes": 536870912}
        if (card != expected or set(card) != set(expected) or
                type(card.get("archive_limit_bytes")) is not int):
            raise ValueError("R13 proof-r11 mode card must bind the exact archive cap")
    else:
        raise ValueError("R13 upload mode is neither synthetic-upload nor proof-r11")


def validate_recipe(paths: list[str]) -> None:
    recipe_path = ROOT / "research/challenge-8/cloud-build/recipes/merge.json"
    recipe = json.loads(recipe_path.read_bytes())
    proof_paths = recipe.get("proof_paths")
    if not isinstance(proof_paths, list) or proof_paths != sorted(set(proof_paths)):
        raise ValueError("current merge recipe proof paths are not canonical")
    current = set(proof_paths)
    missing = set(paths) - current
    baseline_recipe = json.loads(git("show", f"{BASELINE_COMMIT}:{BASELINE_RECIPE}"))
    if (recipe.get("entrypoint") != baseline_recipe.get("entrypoint") or
            recipe.get("infra_paths") != baseline_recipe.get("infra_paths")):
        raise ValueError("R13 recipe changed the baseline entrypoint or infra path set")
    extra = current - set(baseline_recipe["proof_paths"])
    if missing:
        raise ValueError(f"current recipe removed frozen R11 proof paths: {sorted(missing)}")
    if extra & R12_ONLY:
        raise ValueError(f"R13 recipe retains retired R12-only additions: {sorted(extra & R12_ONLY)}")
    if not REQUIRED_R13 <= extra or extra - R13_ALLOWED:
        raise ValueError(f"R13 recipe additions differ from the bounded allowlist: {sorted(extra)}")
    for path in proof_paths:
        target = ROOT / path
        if target.is_symlink() or not target.is_file():
            raise ValueError(f"merge recipe references a missing or non-regular file: {path}")


def validate_selected_additions(paths: list[str]) -> None:
    """Bind new R13 registration inputs to the selected source commit too."""
    recipe_path = "research/challenge-8/cloud-build/recipes/merge.json"
    selected_recipe = git("show", f"HEAD:{recipe_path}")
    current_recipe = (ROOT / recipe_path).read_bytes()
    if selected_recipe != current_recipe:
        raise ValueError("R13 current merge recipe differs from selected committed source")
    recipe = json.loads(selected_recipe)
    baseline = json.loads(git("show", f"{BASELINE_COMMIT}:{BASELINE_RECIPE}"))
    additions = set(recipe["proof_paths"]) - set(baseline["proof_paths"])
    for path in sorted(additions):
        selected = git("show", f"HEAD:{path}")
        current = read_worktree(path)
        if selected != current:
            raise ValueError(f"R13 registered addition differs from selected committed source: {path}")


def validate_dispatcher() -> None:
    current = read_worktree(DISPATCHER_PATH)
    selected = git("show", f"HEAD:{DISPATCHER_PATH}")
    if sha(current) != DISPATCHER_SHA256 or sha(selected) != DISPATCHER_SHA256:
        raise ValueError("R13 dispatcher differs from the exact reviewed wrapper bytes")


def main() -> None:
    try:
        if git("rev-parse", "--verify", f"{BASELINE_COMMIT}^{{commit}}").decode().strip() != BASELINE_COMMIT:
            raise ValueError("R13 baseline source commit is unavailable")
        paths = frozen_paths()
        pathlist_hash = sha(("\n".join(paths) + "\n").encode("utf-8"))
        if len(paths) != FROZEN_COUNT or pathlist_hash != FROZEN_PATHLIST_SHA256:
            raise ValueError("R13 baseline frozen-path inventory differs from its pinned identity")
        base_aggregate, base_missing = aggregate(
            paths, lambda path: git("show", f"{BASELINE_COMMIT}:{path}"))
        head_aggregate, head_missing = aggregate(
            paths, lambda path: git("show", f"HEAD:{path}"))
        worktree_aggregate, worktree_missing = aggregate(paths, read_worktree)
        if base_missing or base_aggregate != FROZEN_AGGREGATE_SHA256:
            raise ValueError(f"R13 baseline frozen proof inputs do not match pinned aggregate: {base_missing}")
        if head_missing or head_aggregate != FROZEN_AGGREGATE_SHA256:
            raise ValueError(f"R13 committed source changed a frozen R11 proof input: {head_missing}")
        if worktree_missing or worktree_aggregate != FROZEN_AGGREGATE_SHA256:
            raise ValueError(f"R13 working tree changed a frozen R11 proof input: {worktree_missing}")
        profile_bytes = read_worktree(PROFILE_PATH)
        if sha(profile_bytes) != PROFILE_SHA256:
            raise ValueError("R13 selected R11 profile bytes differ from the exact reviewed profile")
        profile = json.loads(profile_bytes)
        if (profile.get("profile") != "experimental-merge-label-storage-r11-v1" or
                profile.get("accepted") is not False or profile.get("qualification") != "OPEN" or
                profile.get("effective_tool_commit") != TOOL_COMMIT):
            raise ValueError("R13 selected profile does not retain the open R11 candidate identity")
        validate_mode()
        validate_recipe(paths)
        validate_selected_additions(paths)
        validate_dispatcher()
        preflight = HERE / "r11-source-preflight.py"
        subprocess.run([sys.executable, str(preflight)], cwd=ROOT, check=True)
        print(f"R13 normal-proof freeze PASS: {len(paths)} baseline R11 files byte-identical; "
              "R11 tool/profile/pins/patch composition PASS; no compiler/proof invoked")
    except (OSError, ValueError, KeyError, json.JSONDecodeError,
            subprocess.CalledProcessError) as error:
        print(f"R13 source preflight FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
