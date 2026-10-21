#!/usr/bin/env python3
"""Static R14 source gate."""
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
        raise ValueError("R14 baseline recipe")
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
        raise ValueError(f"R14 input unavailable: {path}")
    return target.read_bytes()


def validate_recipe_and_additions() -> None:
    raw = read_worktree(BASELINE_RECIPE)
    recipe = json.loads(raw)
    baseline_probe = json.loads(git("show", f"{PROBE_SOURCE}:{BASELINE_RECIPE}"))
    paths = recipe.get("proof_paths")
    if not isinstance(paths, list) or paths != sorted(set(paths)):
        raise ValueError("R14 recipe paths")
    sys.path.insert(0, str(HERE.parent))
    import control
    control.r14_validate_recipe_delta(baseline_probe, recipe, R14_ADDITIONS)
    for path in paths:
        read_worktree(path)
    for path in sorted(R14_ADDITIONS | {MODE_PATH}):
        if git("show", f"HEAD:{path}") != read_worktree(path):
            raise ValueError(f"R14 selected source mismatch: {path}")
    if git("show", f"HEAD:{BASELINE_RECIPE}") != raw:
        raise ValueError("R14 recipe source mismatch")


def validate_local_tests() -> None:
    """Keep service harnesses committed and tested without uploading them."""
    for path in sorted(LOCAL_TEST_PATHS):
        selected = git("show", f"HEAD:{path}")
        if selected != read_worktree(path):
            raise ValueError(f"R14 local test source mismatch: {path}")


def validate_frozen_inputs() -> None:
    paths = frozen_paths()
    pathlist_hash = sha(("\n".join(paths) + "\n").encode())
    if len(paths) != FROZEN_COUNT or pathlist_hash != FROZEN_PATHLIST_SHA256:
        raise ValueError("R14 frozen inventory")
    readers = (
        lambda path: git("show", f"{BASELINE_COMMIT}:{path}"),
        lambda path: git("show", f"HEAD:{path}"),
        read_worktree,
    )
    labels = ("R14 baseline", "R14 selected source", "R14 worktree")
    for label, reader in zip(labels, readers):
        digest, missing = aggregate(paths, reader)
        if missing or digest != FROZEN_AGGREGATE_SHA256:
            raise ValueError(f"{label} frozen input mismatch: {missing}")
def main() -> None:
    try:
        sys.path.insert(0, str(HERE.parent))
        import control
        if git("rev-parse", "--verify", f"{BASELINE_COMMIT}^{{commit}}").decode().strip() != BASELINE_COMMIT:
            raise ValueError("R14 baseline unavailable")
        if git("rev-parse", "--verify", f"{PROBE_SOURCE}^{{commit}}").decode().strip() != PROBE_SOURCE:
            raise ValueError("R14 probe unavailable")
        validate_frozen_inputs()
        validate_recipe_and_additions()
        validate_local_tests()
        control.r14_read_selected_gate(git("rev-parse", "HEAD").decode().strip())
        control.r14_validate_retry_sources(PROBE_SOURCE, git("rev-parse", "HEAD").decode().strip())
        subprocess.run([sys.executable, str(HERE / "r11-source-preflight.py")], cwd=ROOT, check=True)
        print("R14 source gate PASS; no compiler/proof/Cloud")
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError, SystemExit) as error:
        print(f"R14 preflight FAIL: {error}", file=sys.stderr)
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
