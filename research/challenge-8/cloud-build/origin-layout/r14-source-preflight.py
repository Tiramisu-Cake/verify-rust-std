#!/usr/bin/env python3
"""Static R14 gate for the exact R13 publication probe and frozen R11 proof."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASELINE_COMMIT = "0c1d0d7861813bcc48d765eba869d30c2658f1cc"
PROBE_SOURCE = "c9b5151735c352d212752c5fe644adcd3543b68d"
BASELINE_RECIPE = "research/challenge-8/cloud-build/recipes/merge.json"
PROFILE_PATH = "research/challenge-8/cloud-build/origin-layout/GLUE-PROFILE.json"
PROFILE_SHA256 = "eb61e49397cd9973ec12d1675bd8bd4867c7374de22e7c1c6a8a58e991266375"
TOOL_COMMIT = "660b576b6b1608db913c51e0785b443a8733396f"
MODE_PATH = "research/challenge-8/cloud-build/origin-layout/R13-UPLOAD-MODE-20261021.json"
GATE_PATH = "research/challenge-8/cloud-build/origin-layout/R14-PUBLICATION-GATE-20261021.json"
LEDGER_PATH = "research/challenge-8/cloud-build/origin-layout/CURRENT-RECOVERY-R14-PROOF-RETRY-BUDGET-20261021.json"
R14_ADDITIONS = {
    GATE_PATH,
    LEDGER_PATH,
    "research/challenge-8/cloud-build/origin-layout/r14-source-preflight.py",
}
LOCAL_TEST_PATHS = {
    "research/challenge-8/cloud-build/origin-layout/r14-phase-service-test.py",
    "research/challenge-8/cloud-build/origin-layout/r14-source-preflight-service-test.py",
}
FROZEN_COUNT = 158
FROZEN_PATHLIST_SHA256 = "1c76ea3f70d5a81fae6ddc36d9ee96fa823102debfd61d2b48dde669c9e8d7f4"
FROZEN_AGGREGATE_SHA256 = "00b6dd4757542c4ea01d29ccbfe632fd227610ff0ce6253cb5b6ebae00cc40da"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(ROOT), *args])


def frozen_paths() -> list[str]:
    recipe = json.loads(git("show", f"{BASELINE_COMMIT}:{BASELINE_RECIPE}"))
    paths = recipe.get("proof_paths")
    if not isinstance(paths, list) or paths != sorted(set(paths)):
        raise ValueError("R14 baseline recipe is not canonical")
    return [p for p in paths if not p.endswith(".md") and "BUDGET" not in p.rsplit("/", 1)[-1].upper()]


def aggregate(paths: list[str], read_bytes) -> tuple[str, list[str]]:
    digest = hashlib.sha256()
    missing = []
    for path in paths:
        try:
            content = read_bytes(path)
        except (OSError, subprocess.CalledProcessError, ValueError):
            missing.append(path)
            continue
        digest.update(path.encode() + b"\0" + sha(content).encode() + b"\n")
    return digest.hexdigest(), missing


def read_worktree(path: str) -> bytes:
    target = ROOT / path
    if target.is_symlink() or not target.is_file():
        raise ValueError(f"R14 proof input is missing or not a regular file: {path}")
    return target.read_bytes()


def validate_recipe_and_additions() -> None:
    raw = read_worktree(BASELINE_RECIPE)
    recipe = json.loads(raw)
    baseline_probe = json.loads(git("show", f"{PROBE_SOURCE}:{BASELINE_RECIPE}"))
    paths = recipe.get("proof_paths")
    if not isinstance(paths, list) or paths != sorted(set(paths)):
        raise ValueError("R14 recipe proof paths are not canonical")
    sys.path.insert(0, str(HERE.parent))
    import control
    control.r14_validate_recipe_delta(baseline_probe, recipe, R14_ADDITIONS)
    for path in paths:
        read_worktree(path)
    for path in sorted(R14_ADDITIONS):
        if git("show", f"HEAD:{path}") != read_worktree(path):
            raise ValueError(f"R14 registration differs from selected committed source: {path}")
    if git("show", f"HEAD:{BASELINE_RECIPE}") != raw:
        raise ValueError("R14 current recipe differs from selected committed source")


def validate_mode_and_gate() -> None:
    mode_raw = git("show", f"HEAD:{MODE_PATH}")
    mode = json.loads(mode_raw)
    if mode != {"schema": "merge-r13-upload-mode-v1", "mode": "proof-r11", "archive_limit_bytes": 536870912}:
        raise ValueError("R14 must select the existing R13 proof-r11 mode with its 512MiB cap")
    if read_worktree(MODE_PATH) != mode_raw:
        raise ValueError("R14 selected mode card differs from its committed source")
    if not read_worktree(GATE_PATH):
        raise ValueError("R14 publication gate is empty")


def validate_local_tests() -> None:
    """Keep service harnesses committed and tested without uploading them."""
    for path in sorted(LOCAL_TEST_PATHS):
        selected = git("show", f"HEAD:{path}")
        if selected != read_worktree(path):
            raise ValueError(f"R14 local service test differs from selected committed source: {path}")


def validate_frozen_inputs() -> None:
    paths = frozen_paths()
    pathlist_hash = sha(("\n".join(paths) + "\n").encode())
    if len(paths) != FROZEN_COUNT or pathlist_hash != FROZEN_PATHLIST_SHA256:
        raise ValueError("R14 frozen R11 input inventory differs from its pinned identity")
    readers = (
        lambda path: git("show", f"{BASELINE_COMMIT}:{path}"),
        lambda path: git("show", f"HEAD:{path}"),
        read_worktree,
    )
    labels = ("R14 baseline", "R14 selected source", "R14 worktree")
    for label, reader in zip(labels, readers):
        digest, missing = aggregate(paths, reader)
        if missing or digest != FROZEN_AGGREGATE_SHA256:
            raise ValueError(f"{label} changed a frozen R11 proof input: {missing}")
    profile = json.loads(read_worktree(PROFILE_PATH))
    if (sha(read_worktree(PROFILE_PATH)) != PROFILE_SHA256 or
            profile.get("profile") != "experimental-merge-label-storage-r11-v1" or
            profile.get("accepted") is not False or profile.get("qualification") != "OPEN" or
            profile.get("effective_tool_commit") != TOOL_COMMIT):
        raise ValueError("R14 changed the exact open R11 candidate profile")


def main() -> None:
    try:
        sys.path.insert(0, str(HERE.parent))
        import control
        if git("rev-parse", "--verify", f"{BASELINE_COMMIT}^{{commit}}").decode().strip() != BASELINE_COMMIT:
            raise ValueError("R14 frozen baseline source is unavailable")
        if git("rev-parse", "--verify", f"{PROBE_SOURCE}^{{commit}}").decode().strip() != PROBE_SOURCE:
            raise ValueError("R14 exact R13 publication probe source is unavailable")
        validate_frozen_inputs()
        validate_recipe_and_additions()
        validate_mode_and_gate()
        validate_local_tests()
        control.r14_read_selected_gate(git("rev-parse", "HEAD").decode().strip())
        control.r14_validate_retry_sources(PROBE_SOURCE, git("rev-parse", "HEAD").decode().strip())
        subprocess.run([sys.executable, str(HERE / "r11-source-preflight.py")], cwd=ROOT, check=True)
        print("R14 publication gate and R11 proof source preflight PASS; no compiler/proof/Cloud invoked")
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError, SystemExit) as error:
        print(f"R14 source preflight FAIL: {error}", file=sys.stderr)
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
