#!/usr/bin/env python3
"""Static R11 profile/source applicability gate; never builds or proves."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TOOL = Path("/root/verifast-merge-actual-glue")
PROFILE_NAME = "experimental-merge-label-storage-r11-v1"
PHASE_ID = "MERGE-LABEL-STORAGE-INVARIANT-R11-2026-10-21"
BASELINE_PATH = "research/challenge-8/cloud-build/origin-layout/R11-BASELINE-PROFILE-20261021.json"
STARTING_TOOL_COMMIT = "bb557d43c4196694c7af50ff2150ce56a269e17d"
CANDIDATE_TOOL_COMMIT = "a3a22f98e0e48f25af6741f3291c31a6d96e5119"
BASELINE_SHA256 = "c3f5d286777ffd388e1eb0894ad0ff9e8f1f87f72424291041cb800385f7c979"
R11_TOOL_PATHS = {
    "src/verifast.ml",
    "src/rust_frontend/vf_mir_translator/vf_mir_translator.ml",
}
SOURCE_PINS = {
    "src/rust_frontend/vf_mir_exporter/src/lib.rs": "exporter_source_sha256",
    "src/rust_frontend/vf_mir/vf_mir.capnp": "schema_sha256",
    "src/refinement_checker/main.ml": "refiner_main_source_sha256",
    "src/refinement_checker/refinement_checker.ml": "refiner_core_source_sha256",
    "src/rust_frontend/vf_mir_translator/vf_mir_translator.ml": "translator_sha256",
    "src/rust_frontend/vf_mir_translator/rust_parser.ml": "parser_sha256",
    "src/frontend/ast.ml": "ast_sha256",
    "src/frontend/ocaml_expr_of_ast.ml": "emitter_sha256",
    "src/SExpressionEmitter.ml": "sexpression_sha256",
    "src/verifast.ml": "kernel_sha256",
    "src/verifast1.ml": "model_sha256",
    "src/verify_expr.ml": "verify_expr_sha256",
    "bin/rust/prelude_core.rsspec": "prelude_sha256",
    "bin/rust/std/lib.rsspec": "stdlib_sha256",
    "src/frontend/verifast0.ml": "options_source_sha256",
    "src/vfconsole/vfconsole.ml": "console_source_sha256",
    "src/vfide/vfide.ml": "ide_source_sha256",
}
REQUIRED_PROOF_PATHS = {
    BASELINE_PATH,
    "research/challenge-8/cloud-build/origin-layout/R11-START-20261021.json",
    "research/challenge-8/cloud-build/origin-layout/R11-SESSION-20261021.md",
    "research/challenge-8/cloud-build/origin-layout/R11-LABEL-STORAGE-DESIGN-20261021.md",
    "research/challenge-8/cloud-build/origin-layout/R11-INPUTS-20261021.json",
    "research/challenge-8/cloud-build/origin-layout/CURRENT-RECOVERY-R11-BUDGET-20261021.json",
    "research/challenge-8/cloud-build/origin-layout/r11-phase-service-test.py",
    "research/challenge-8/cloud-build/origin-layout/r11-source-preflight.py",
    "research/challenge-8/cloud-build/origin-layout/r11-registration-service-test.py",
    "research/challenge-8/cloud-build/origin-layout/r11-trace-service-test.py",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(TOOL), *args])


def validate_profile(profile: dict, baseline: dict, baseline_sha: str,
                     current_tool_commit: str) -> None:
    if not isinstance(profile, dict) or profile.get("schema") != "smallsort-tracked-md-profile-v1":
        raise ValueError("R11 selected profile schema differs")
    if (profile.get("profile") != PROFILE_NAME or profile.get("accepted") is not False or
            profile.get("qualification") != "OPEN"):
        raise ValueError("R11 profile identity/status differs")
    if baseline_sha != BASELINE_SHA256 or baseline.get("profile") != "experimental-merge-moving-gap-r10-v1":
        raise ValueError("R11 baseline is not the exact captured R10 selected profile")
    if profile.get("previous_profile_sha256") != baseline_sha:
        raise ValueError("R11 previous-profile pin differs from captured R10 baseline")
    registration = profile.get("r11_registration")
    expected = {
        "schema": "merge-r11-profile-registration-v1",
        "phase_id": PHASE_ID,
        "baseline_profile_path": BASELINE_PATH,
        "baseline_profile_sha256": BASELINE_SHA256,
        "starting_tool_commit": STARTING_TOOL_COMMIT,
        "candidate_tool_commit": CANDIDATE_TOOL_COMMIT,
        "tool_source_paths": sorted(R11_TOOL_PATHS),
        "source_applicability": "label-storage-invariant annotation temporary; exact body/local/Live/ghost-call/Dead and label-invariant binding; unchanged R10 resource model",
    }
    if registration != expected:
        raise ValueError("R11 profile registration receipt differs")
    candidate = profile.get("effective_tool_commit")
    if (candidate != CANDIDATE_TOOL_COMMIT or current_tool_commit != candidate or
            profile.get("guard_return_trace_tool_commit") != candidate):
        raise ValueError("R11 profile does not bind the exact reviewed two-file diagnostic tool commit")
    chain = profile.get("ordered_patch_chain")
    baseline_chain = baseline.get("ordered_patch_chain")
    if (not isinstance(chain, list) or not isinstance(baseline_chain, list) or
            len(chain) != len(baseline_chain) or len(chain) != 19 or
            chain[:-1] != baseline_chain[:-1] or
            chain[-1].get("path") != baseline_chain[-1].get("path") or
            chain[-1].get("sha256") != profile.get("guard_return_trace_patch_sha256")):
        raise ValueError("R11 patch chain must retain the R10 chain except its regenerated cumulative final patch")
    for key in SOURCE_PINS.values():
        if key not in ("kernel_sha256", "translator_sha256") and profile.get(key) != baseline.get(key):
            raise ValueError(f"R11 source pin differs from captured R10 baseline: {key}")


def validate_tool_checkout(profile: dict, baseline: dict, head: str) -> None:
    if git("diff", "--name-only", baseline["effective_tool_commit"], head).decode().splitlines() != sorted(R11_TOOL_PATHS):
        raise ValueError("R11 tool delta must touch exactly the two reviewed diagnostic source files")
    for relative, key in SOURCE_PINS.items():
        if sha(git("show", f"{head}:{relative}")) != profile.get(key):
            raise ValueError(f"R11 selected-tool source pin mismatch: {relative}")


def main() -> None:
    baseline_path = HERE / "R11-BASELINE-PROFILE-20261021.json"
    baseline_raw = baseline_path.read_bytes()
    baseline_sha = sha(baseline_raw)
    baseline = json.loads(baseline_raw)
    profile_path = HERE / "GLUE-PROFILE.json"
    profile = json.loads(profile_path.read_bytes())
    head = git("rev-parse", "HEAD").decode().strip()
    validate_profile(profile, baseline, baseline_sha, head)
    validate_tool_checkout(profile, baseline, head)
    patch_path = ROOT / "research/challenge-8/cloud-build/origin-layout/r9-guard-return-trace.patch"
    patch_hash = sha(patch_path.read_bytes())
    if patch_hash != profile.get("guard_return_trace_patch_sha256"):
        raise ValueError("R11 cumulative final patch does not match the selected profile pin")
    chain = profile["ordered_patch_chain"]
    patches = []
    touched = set()
    for row in chain:
        patch = ROOT / row["path"]
        if sha(patch.read_bytes()) != row["sha256"]:
            raise ValueError(f"R11 patch chain entry is not pinned: {patch}")
        patches.append(patch)
        for line in subprocess.check_output(
                ["git", "apply", "--numstat", str(patch)], text=True).splitlines():
            touched.add(line.split("\t", 2)[2])
    with tempfile.TemporaryDirectory(prefix="r11-static-source-composition-") as temp:
        subprocess.run(["git", "init", "--quiet", temp], check=True)
        tree = set(git("ls-tree", "-r", "--name-only", profile["verifast_commit"]).decode().splitlines())
        for relative in touched & tree:
            output = Path(temp) / relative
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(git("show", f"{profile['verifast_commit']}:{relative}"))
        for patch in patches:
            subprocess.run(["git", "-C", temp, "-c", "core.whitespace=cr-at-eol",
                            "apply", "--check", str(patch)], check=True)
            subprocess.run(["git", "-C", temp, "-c", "core.whitespace=cr-at-eol",
                            "apply", "--whitespace=error", str(patch)], check=True)
        for relative in touched:
            if (Path(temp) / relative).read_bytes() != git(f"show", f"{head}:{relative}"):
                raise ValueError(f"R11 composed patch result differs from selected tool source: {relative}")
    overlay_path = ROOT / "research/challenge-8/merge/cloud-build/provider-overlays.py"
    overlay_tree = ast.parse(overlay_path.read_bytes())
    overlay_files = next(ast.literal_eval(node.value) for node in overlay_tree.body
                         if isinstance(node, ast.Assign) and
                         any(isinstance(target, ast.Name) and target.id == "FILES"
                             for target in node.targets))
    if len(overlay_files) != 18:
        raise ValueError("R11 provider overlay must retain exactly 18 source pins")
    for relative, expected in overlay_files.items():
        if sha((ROOT / relative).read_bytes()) != expected:
            raise ValueError(f"R11 provider overlay source pin mismatch: {relative}")
    recipe = json.loads((ROOT / "research/challenge-8/cloud-build/recipes/merge.json").read_bytes())
    proof_paths = recipe.get("proof_paths")
    if not isinstance(proof_paths, list) or proof_paths != sorted(set(proof_paths)):
        raise ValueError("R11 merge recipe proof paths are not canonical")
    if not REQUIRED_PROOF_PATHS <= set(proof_paths):
        raise ValueError("R11 registration/preflight is absent from the exact proof recipe")
    for relative in proof_paths:
        if not (ROOT / relative).is_file():
            raise ValueError(f"R11 recipe references a missing path: {relative}")
    print("R11 exact two-file source delta, 19-patch composition, 18-overlay and recipe closure PASS; no compiler/proof credit")


if __name__ == "__main__":
    main()
