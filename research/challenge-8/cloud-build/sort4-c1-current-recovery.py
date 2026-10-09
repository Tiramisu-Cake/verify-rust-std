#!/usr/bin/env python3
"""Cloud-only actual sort4 c1 CURRENT diagnostic; never an accepted profile.

The exact AST overlay consumes the reserved first-unwind marker and moves the
source debt close, pair recovery, join, and original unwind return across a
strict lifetime exit. This driver requires source/MIR/tool identities, executes
the affected strict controls, then retains the complete actual verifier trace.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from types import SimpleNamespace


PATCH = Path("research/challenge-8/overnight-callback/verifast-actual-sort4-first-scope-TEST.patch")
DEBT_PATCH = Path("research/challenge-8/overnight-callback/verifast-actual-sort4-c1-debt-controls-TEST.patch")
DEBT_MANIFEST = Path("research/challenge-8/overnight-callback/ACTUAL-SORT4-C1-DEBT-CONTROLS-TEST.json")
PREFIX_PATCH = Path("research/challenge-8/cloud-build/sort4-native-entry-c1/verifast-actual-c1-prefix-TEST.patch")
PREFIX_PROFILE = Path("research/challenge-8/cloud-build/sort4-native-entry-c1/C1-PREFIX-PROFILE.json")
PREFIX_CARD = Path("research/challenge-8/cloud-build/sort4-native-entry-c1/C1-PREFIX-SEMANTIC-CARD.md")
OUTPUT_PATCH = Path("research/challenge-8/overnight-callback/verifast-actual-sort4-c1-output-eq-TEST.patch")
OUTPUT_MANIFEST = Path("research/challenge-8/overnight-callback/ACTUAL-SORT4-C1-OUTPUT-EQ-TEST.json")
MANIFEST = Path("research/challenge-8/overnight-callback/ACTUAL-SORT4-AST-SCOPE-TEST.json")
TRANSLATOR = Path("src/rust_frontend/vf_mir_translator/vf_mir_translator.ml")
KERNEL = Path("src/verifast.ml")
SOURCE = "fddb6f1a0a90948042c99fd1037b7e939586c9e7b9e46a63367a7d876e04ccc9"
ORIGINAL = "3602050e45025745d80b308802be9e552310959abcee4b95bfe8c24f8ca04b72"
AST = "dc7e8487ae46470ebcb9f964cb158c44d9bf75042cffa79d465f4d7e67001d39"
GRAPH = {"normal": "667e43477674d9e834b462b612f498af81598ec18622f0a60337ae4fdc6b017d",
         "readonly": "925b05a8c2bb66be8ad5a7f091f8232d9e930782b5ca01067cf7d1bec349f5b5"}
FIRST = "verified/lib.rs(185,13-36): error: No such function: __vf_sort4_first_unwind"
CONTROLS = ("positive_basic", "positive_direct_unwind",
            "negative_wrong_marker", "negative_duplicate_marker",
            "negative_typed_chunk_survives_cut", "negative_unclosed_fractional_access")
FALSE_POSTS = ("normal-false", "unwind-false")


def need(ok: bool, why: str) -> None:
    if not ok:
        raise RuntimeError(why)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def read(path: Path) -> dict:
    need(path.is_file(), f"missing {path}")
    value = json.loads(path.read_text())
    need(isinstance(value, dict), f"invalid record {path}")
    return value


def module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, f"module unavailable {path}")
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def git(root: Path, *args: str) -> bytes:
    return subprocess.check_output(("git", "-C", str(root), *args))


def stage(a, name: str, command: list[str], *, cwd: Path | None = None,
          env: dict[str, str] | None = None, cap: int = 600) -> int:
    seconds = min(cap, a.deadline_epoch - int(time.time()) - 30)
    need(seconds > 0, f"deadline before {name}")
    log = a.evidence / f"{name}.log"
    resource = a.evidence / f"{name}-resources.txt"
    log.parent.mkdir(parents=True, exist_ok=True)
    record(a.evidence / "stage-progress.json", {
        "stage": name, "status": "RUNNING", "argv": command,
        "started_epoch": int(time.time()), "proof_verdict": "NO_VERDICT"})
    with log.open("wb") as output:
        code = subprocess.run(
            ("/usr/bin/time", "-v", "-o", str(resource), "timeout",
             "--signal=TERM", "--kill-after=10s", f"{seconds}s", *command),
            cwd=cwd, env=env, stdout=output, stderr=subprocess.STDOUT,
            check=False).returncode
    (a.evidence / f"{name}-exit-code.txt").write_text(f"{code}\n")
    record(a.evidence / f"{name}-stage.json", {
        "argv": command, "cwd": str(cwd) if cwd else None,
        "exit": code, "timeout_seconds": seconds, "log": str(log.relative_to(a.evidence)),
        "resources": str(resource.relative_to(a.evidence))})
    record(a.evidence / "stage-progress.json", {
        "stage": name, "status": "TERMINAL", "exit": code,
        "finished_epoch": int(time.time()), "proof_verdict": "NO_VERDICT"})
    return code


def snapshot(a, root: Path) -> dict:
    audit = module(a.cloud_dir / "sort4-first-scope-audit.py", "c1_scope_snapshot")
    return audit.snapshot(root, a.proof_root)


def setup(a, env: dict[str, str]) -> tuple[Path, Path, dict]:
    need(os.environ.get("SMALLSORT_EXECUTION_PROVIDER") == "cloud-build" and
         os.environ.get("LANE") == "o26-sort4-c1-current-recovery" and
         not os.environ.get("GITHUB_ACTIONS"), "Cloud c1 lane required")
    for path in (a.production_source, a.production_applied_patch, a.stock_home,
                 a.compiler_sysroot, a.evidence, a.proof_root, a.work_root,
                 a.cloud_dir):
        need(str(path).startswith("/workspace/") and "/../" not in str(path)
             and "/./" not in str(path), f"unsafe path {path}")
    need(not a.evidence.exists(), "fresh evidence directory required")
    need(a.deadline_epoch - time.time() > 120, "insufficient Cloud time")
    need(git(a.proof_root, "rev-parse", "HEAD").decode().strip() ==
         os.environ.get("PROOF_SHA"), "proof SHA differs")
    need(git(a.production_source, "diff", "--binary", "HEAD") ==
         a.production_applied_patch.read_bytes(), "production patch differs")
    manifest = read(a.proof_root / MANIFEST)
    patch = a.proof_root / PATCH
    need(sha(patch) == manifest["profile_components"]["overlay_patch_sha256"],
         "exact AST overlay patch SHA differs")
    need(manifest["source"] == {"verified_sha256": SOURCE,
                                "ghost_stripped_sha256": ORIGINAL} and
         manifest["pre_rewrite_ast_func_sha256"] == AST and
         {mode: manifest["complete_typed_mir"][f"{mode}_record_sha256"]
          for mode in GRAPH} == GRAPH and
         manifest["complete_typed_mir"]["first_unwind"] == "Continue",
         "exact source/MIR/AST certificate differs")
    lines = patch.read_text().splitlines()
    need([s for s in lines if s.startswith(("--- ", "+++ "))] ==
         [f"--- a/{TRANSLATOR}", f"+++ b/{TRANSLATOR}"],
         "overlay must touch only translator")
    a.evidence.mkdir(parents=True)
    record(a.evidence / "input-identity.json", {
        "proof_sha": os.environ["PROOF_SHA"],
        "production_head": git(a.production_source, "rev-parse", "HEAD").decode().strip(),
        "production_patch_sha256": sha(a.production_applied_patch),
        "ast_overlay_sha256": sha(patch), "manifest_sha256": sha(a.proof_root / MANIFEST),
        "source_sha256": SOURCE, "original_sha256": ORIGINAL,
        "complete_mir_sha256": GRAPH, "pre_ast_sha256": AST,
        "actual_unwind": "first FnMut direct Continue",
        "normal_post": "full source4/T.own, optional destination and CURRENT F.own/thread/type, with destination initialization still a target obligation",
        "unwind_post": "full source4/T.own, optional destination, CURRENT F.own/thread/type and no outstanding c1 borrow debt",
        "accepted": False})
    (a.evidence / "PROFILE-STATUS.txt").write_text(
        "SORT4_C1_CURRENT_RECOVERY_DIAGNOSTIC_ONLY_NOT_ACCEPTED\n")
    base = a.work_root / "cut-relocation-isolated-source"
    relocation = a.evidence / "relocation"
    args = ["--production-source", str(a.production_source),
            "--production-applied-patch", str(a.production_applied_patch),
            "--stock-home", str(a.stock_home), "--compiler-sysroot", str(a.compiler_sysroot),
            "--evidence", str(relocation), "--deadline-epoch", str(a.deadline_epoch),
            "--proof-root", str(a.proof_root), "--work-root", str(a.work_root),
            "--cloud-dir", str(a.cloud_dir)]
    need(not base.exists(), "strict isolated source already exists")
    need(stage(a, "strict-relocation", ["bash", str(a.cloud_dir / "run-cut-relocate.sh"),
                                        *args], env=env, cap=1000) == 0,
         "strict relocation failed; no actual c1 proof")
    relocation_audit = read(relocation / "diagnostic-audit.json")
    source_audit = read(relocation / "source-audit.json")
    relocation_classifier = module(a.cloud_dir / "cut-relocate-audit.py",
                                   "c1_relocation_classifier")
    # Recompute the old diagnostic from its unchanged raw artifacts. The
    # classifier has no `diagnostic_match` field: its exact `checks` map and
    # stage exits carry the proof boundary.
    replay = relocation_classifier.classify(relocation / "relocation", 0, source_audit)
    checks = relocation_audit.get("checks", {})
    exits = relocation_audit.get("stage_exits", {})
    need(relocation_audit.get("classification") == "FIXTURE_FULL_VF0_DIAGNOSTIC_ONLY" and
         relocation_audit == replay and relocation_audit.get("raw_capture_exit") == 0 and
         set(checks) == {"translated_ids_patch_pin", "support", "exact_source_pair",
                         "complete_target_mir_pins", "direct_unwind_continue",
                         "baseline_boundary", "ast_six_removed_one_inserted",
                         "relocated_proof_entry", "diagnostic_outcome"} and
         all(value is True for value in checks.values()) and
         all(exits.get(key) == 0 for key in
             ("normal-export", "normal-decode", "readonly-export",
              "readonly-decode", "refinement", "relocated-verification")) and
         exits.get("baseline-verification") in (1, 2) and
         relocation_audit.get("relocated_first_error") is None and
         relocation_audit.get("unwind_storage_dead_assumed") is False and
         relocation_audit.get("accepted") is False and
         relocation_audit.get("actual_sort4_proved") is False,
         "strict relocation proof gate differs")
    base_snapshot = snapshot(a, base)
    need(base_snapshot["critical"][str(KERNEL)] ==
         sha(relocation / "cut-verifast-before-relocation.ml") and
         base_snapshot["binaries"]["bin/verifast"] ==
         source_audit["relocation_console_sha256"],
         "frozen d557 kernel/strict console differs")
    record(a.evidence / "strict-base-snapshot.json", base_snapshot)
    return base, patch, base_snapshot


def baseline(a, env: dict[str, str]) -> Path:
    root = a.evidence / "baseline"
    env = env.copy()
    env["LD_LIBRARY_PATH"] = f"{a.compiler_sysroot}/lib:{a.production_source}/bin:" + env.get("LD_LIBRARY_PATH", "")
    for key in ("SORT4_ACTUAL_AST_SCOPE_TEST", "SORT4_STRICT_LFT_CUT"):
        env.pop(key, None)
    env["SORT4_ACTUAL_C1_PREFIX_TEST"] = "0"
    env["SORT4_C1_PREFIX_CONTROL"] = "none"
    command = [sys.executable, str(a.cloud_dir / "actual-sort4-capture.py"),
               "--proof-root", str(a.proof_root), "--cloud-dir", str(a.cloud_dir),
               "--tool-home", str(a.production_source), "--schema",
               str(a.production_source / "src/rust_frontend/vf_mir/vf_mir.capnp"),
               "--compiler-sysroot", str(a.compiler_sysroot), "--evidence", str(root),
               "--deadline-epoch", str(a.deadline_epoch)]
    need(stage(a, "actual-baseline", command, env=env, cap=850) == 0,
         "fresh actual O24 capture failed")
    audit = module(a.cloud_dir / "sort4-ast-audit.py", "c1_ast_baseline")
    exact = audit.preflight(root)
    need(exact["baseline_refusal"] == FIRST and
         sha(root / "actual-sort4-fixture/verified/lib.rs") == SOURCE and
         sha(root / "actual-sort4-fixture/original/lib.rs") == ORIGINAL,
         "fresh exact source/MIR/first reserved marker differs")
    record(a.evidence / "baseline-check.json", exact)
    return root / "actual-sort4-fixture"


def build_overlay(a, base: Path, patch: Path, old: dict, env: dict[str, str]) -> Path:
    target = a.work_root / "sort4-c1-current-isolated-source"
    need(not target.exists(), "c1 test source already exists")
    need(stage(a, "c1-source-copy", ["cp", "-a", str(base), str(target)], cap=120) == 0,
         "isolated strict source copy failed")
    need(snapshot(a, target) == old, "isolated copy changed strict tool")
    need(stage(a, "c1-patch-check", ["git", "-C", str(target), "apply", "--check",
                                     str(patch)], cap=60) == 0, "AST patch cannot apply")
    need(stage(a, "c1-patch-apply", ["git", "-C", str(target), "apply", str(patch)],
               cap=60) == 0, "AST patch apply failed")
    output_patch = a.proof_root / OUTPUT_PATCH
    output_manifest = read(a.proof_root / OUTPUT_MANIFEST)
    need(sha(output_patch) == output_manifest["patch_sha256"] and
         output_manifest["source_sha256"] == SOURCE and output_manifest["pre_ast_sha256"] == AST,
         "c1 compiler Output equality patch/inputs differ")
    need(stage(a, "c1-output-patch-check", ["git", "-C", str(target), "apply", "--check", str(output_patch)], cap=60) == 0,
         "c1 Output equality patch cannot apply")
    need(stage(a, "c1-output-patch-apply", ["git", "-C", str(target), "apply", str(output_patch)], cap=60) == 0,
         "c1 Output equality patch apply failed")
    debt_patch = a.proof_root / DEBT_PATCH
    debt_manifest = read(a.proof_root / DEBT_MANIFEST)
    need(sha(debt_patch) == debt_manifest["patch_sha256"], "c1 negative debt patch pin differs")
    need(stage(a, "c1-debt-patch-check", ["git", "-C", str(target), "apply", "--check", str(debt_patch)], cap=60) == 0,
         "c1 debt control patch cannot apply")
    need(stage(a, "c1-debt-patch-apply", ["git", "-C", str(target), "apply", str(debt_patch)], cap=60) == 0,
         "c1 debt control patch apply failed")
    prefix_manifest = read(a.proof_root / PREFIX_PROFILE)
    prefix_patch = a.proof_root / PREFIX_PATCH
    need(prefix_manifest.get("classification") ==
         "EXPERIMENTAL_ACTUAL_C1_BOUNDED_PREFIX_NOT_CALLABLE_SUMMARY" and
         prefix_manifest.get("profile_accepted") is False and
         prefix_manifest.get("source_sha256") == SOURCE and
         prefix_manifest.get("pre_ast_sha256") == AST and
         prefix_manifest.get("kernel_changed") is False and
         prefix_manifest.get("memory_model_changed") is False and
         sha(target / TRANSLATOR) == prefix_manifest.get("base_translator_sha256") and
         sha(prefix_patch) == prefix_manifest.get("patch_sha256"),
         "bounded-prefix profile/base translator/patch pin differs")
    prefix_lines = prefix_patch.read_text().splitlines()
    need([s for s in prefix_lines if s.startswith(("--- ", "+++ "))] ==
         [f"--- a/{TRANSLATOR}", f"+++ b/{TRANSLATOR}"],
         "bounded-prefix patch must touch only translator")
    need(stage(a, "c1-prefix-patch-check", ["git", "-C", str(target), "apply", "--check",
                                             str(prefix_patch)], cap=60) == 0,
         "bounded-prefix patch cannot apply after firstscope/output/debt patches")
    need(stage(a, "c1-prefix-patch-apply", ["git", "-C", str(target), "apply",
                                             str(prefix_patch)], cap=60) == 0,
         "bounded-prefix patch apply failed")
    need(sha(target / TRANSLATOR) == prefix_manifest.get("patched_translator_sha256"),
         "bounded-prefix patched translator pin differs")
    need(sha(target / KERNEL) == old["critical"][str(KERNEL)],
         "AST overlay changed frozen strict kernel")
    patched_translator = sha(target / TRANSLATOR)
    (a.evidence / "patched-translator.sha256").write_text(patched_translator + "\n")
    (target / "bin/verifast").unlink()
    env = env.copy()
    env["LD_LIBRARY_PATH"] = f"{a.compiler_sysroot}/lib:{target}/bin:" + env.get("LD_LIBRARY_PATH", "")
    need(stage(a, "c1-console-build", ["make", "-C", str(target / "src"),
                                       "../bin/verifast", "WITHOUT_LABLGTK=yes",
                                       "VERBOSE=yes"], env=env, cap=900) == 0,
         "isolated translator console build failed")
    need(sha(target / TRANSLATOR) == patched_translator,
         "translator changed during console build")
    new = snapshot(a, target)
    need(new["head"] == old["head"] and
         new["critical"][str(KERNEL)] == old["critical"][str(KERNEL)] and
         new["effective_rsspec"] == old["effective_rsspec"] and
         new["proof_std"] == old["proof_std"] and
         new["binaries"]["bin/verifast"] != old["binaries"]["bin/verifast"] and
         all(new["critical"][key] == value for key, value in old["critical"].items()
             if key != str(TRANSLATOR)) and
         all(new["binaries"][key] == value for key, value in old["binaries"].items()
             if key != "bin/verifast") and
         set(new["modified_names"]) == set(old["modified_names"]),
         "isolated tool changed outside translator/console")
    record(a.evidence / "c1-tool-snapshot.json", new)
    record(a.evidence / "c1-prefix-profile-inputs.json", {
        "profile_sha256": sha(a.proof_root / PREFIX_PROFILE),
        "patch_sha256": sha(prefix_patch), "semantic_card_sha256": sha(a.proof_root / PREFIX_CARD),
        "base_translator_sha256": prefix_manifest["base_translator_sha256"],
        "patched_translator_sha256": patched_translator,
        "source_sha256": SOURCE, "pre_ast_sha256": AST, "complete_typed_mir": GRAPH,
        "kernel_sha256_unchanged": new["critical"][str(KERNEL)] == old["critical"][str(KERNEL)],
        "effective_rsspec_unchanged": new["effective_rsspec"] == old["effective_rsspec"],
        "proof_std_unchanged": new["proof_std"] == old["proof_std"],
        "accepted": False})
    return target


def strict_controls(a, tool: Path, env: dict[str, str]) -> dict:
    # The relocation driver overlays only capture-relocate. Adapt the frozen
    # strict matrix capture's provider guard in the disposable proof checkout.
    controls = a.evidence / "controls"
    controls.mkdir()
    need(stage(a, "strict-capture-provider-overlay",
               [sys.executable, str(a.cloud_dir / "cut-trace-provider-overlay.py"),
                "--proof-root", str(a.proof_root), "--cloud-dir", str(a.cloud_dir),
                "--evidence", str(controls)], cap=30) == 0,
         "strict control provider adaptation failed")
    capture = a.proof_root / "research/challenge-8/overnight-lifetime/capture.py"
    capture_module = module(capture, "c1_strict_capture")
    rows = {}
    false_audit = module(a.cloud_dir / "strict-cut-false-posts-audit.py", "c1_false_audit")
    env = env.copy()
    env["SMALLSORT_CLOUD_PROVIDER_PATH"] = str(a.cloud_dir / "provider.py")
    env["LD_LIBRARY_PATH"] = f"{a.compiler_sysroot}/lib:{tool}/bin:" + env.get("LD_LIBRARY_PATH", "")
    env.pop("SORT4_ACTUAL_AST_SCOPE_TEST", None)
    env.pop("SORT4_STRICT_LFT_CUT", None)
    env["SORT4_ACTUAL_C1_PREFIX_TEST"] = "0"
    env["SORT4_C1_PREFIX_CONTROL"] = "none"
    for key in CONTROLS:
        path = controls / "cases" / key
        command = [sys.executable, str(capture), "--tool-home", str(tool),
                   "--out", str(path), "--deadline-epoch", str(a.deadline_epoch),
                   "--case", key]
        need(stage(a, f"controls/capture-{key}", command, env=env, cap=260) == 0,
             f"strict control {key} setup/proof inconclusive")
        row = read(path / key / "result.json")
        record(path / "raw-case-result.json", row)
        expected = ("POSITIVE_CANDIDATE_REVIEW_REQUIRED" if key.startswith("positive_")
                    else "INTENDED_NEGATIVE_CANDIDATE_REVIEW_REQUIRED")
        need(row.get("classification") == expected and
             row.get("decoded_body_inventory_ok") is True and
             row.get("source_strip_identity") is True and
             (key != "positive_direct_unwind" or row.get("direct_unwind_mir_candidate") is True),
             f"strict control {key} changed first obligation")
        proof_log = (path / key / "full-verification.log").read_text(errors="replace")
        proof_exit = row["stages"]["full-verification"]["exit"]
        if key == "positive_direct_unwind":
            target_header = "Verifying function 'positive_direct_unwind'"
            callee_entries = false_audit.proof_entries(proof_log, "cut_maybe_unwind")
            target_entries = false_audit.proof_entries(proof_log, "positive_direct_unwind")
            need(len(callee_entries) == len(target_entries) == 1 and
                 callee_entries[0] < target_entries[0],
                 "direct unwind callee proof must precede target proof")
        if key.startswith("negative_"):
            target_header = "Verifying function '" + key + "'"
            errors = row.get("full_error_lines", [])
            if key in ("negative_wrong_marker", "negative_duplicate_marker"):
                # These deliberately fail during marker translation, before
                # verification; they cannot count as resource negatives.
                intended_stage = not false_audit.proof_entries(proof_log, key)
            else:
                entries = false_audit.proof_entries(proof_log, key)
                intended_stage = (bool(errors) and len(entries) == 1 and
                                  entries[0] < proof_log.index(errors[0]))
            need(capture_module.expected_error(key, proof_log, proof_exit) and
                 len(errors) == 1 and errors[0].startswith("verified/lib.rs(") and
                 intended_stage,
                 f"strict control {key} missed its intended predicate/location")
        else:
            need(proof_exit == 0 and not row.get("full_error_lines") and
                 "Leak check." in proof_log,
                 f"strict positive {key} did not complete its proof/leak checks")
        rows[key] = {"classification": expected,
                     "first_error": (row.get("full_error_lines") or [None])[0],
                     "source_hashes": row.get("source_hashes"),
                     "stage_exits": {k: v.get("exit") for k, v in row.get("stages", {}).items()}}
        record(path / "gate-result.json", {"gate_passed": True, **rows[key]})
    false = a.evidence / "false-posts"
    false.mkdir()
    prepare = module(a.cloud_dir / "strict-cut-false-posts-prepare.py", "c1_false_prepare")
    manifest = prepare.prepare(a.proof_root, controls, false)
    need(set(manifest["cases"]) == set(FALSE_POSTS), "false post source set differs")
    false_capture = a.cloud_dir / "strict-cut-false-posts-capture.py"
    for key in FALSE_POSTS:
        command = [sys.executable, str(false_capture), "--case", key,
                   "--tool-home", str(tool), "--proof-root", str(a.proof_root),
                   "--cloud-dir", str(a.cloud_dir), "--evidence", str(false),
                   "--compiler-sysroot", str(a.compiler_sysroot),
                   "--deadline-epoch", str(a.deadline_epoch)]
        need(stage(a, f"false-posts/capture-{key}", command, env=env, cap=340) == 0,
             f"false post {key} capture failed")
    ns = SimpleNamespace(controls_evidence=controls, evidence=false)
    false_rows = {}
    for key in FALSE_POSTS:
        row = false_audit.audit_case(ns, key, capture_module, prepare)
        record(false / "cases" / key / "audit-result.json", row)
        need(row["classification"] == "FALSE_POST_FIRST_BOUNDARY_CANDIDATE_REVIEW_REQUIRED",
             f"{key}: first false post obligation changed")
        false_rows[key] = row
    result = {"classification": "AFFECTED_STRICT_CONTROLS_AND_FALSE_POSTS_CANDIDATE",
              "accepted": False, "controls": rows, "false_posts": false_rows,
              "whole_17_matrix_repeated": False}
    record(a.evidence / "controls-check.json", result)
    return result


def actual_prefix(a, fixture: Path, tool: Path, env: dict[str, str],
                  original_header_posts: str) -> dict:
    """Run bounded c1 prefix and its intended proof controls; never a summary."""
    verified = fixture / "verified/lib.rs"
    original = fixture / "original/lib.rs"
    source_pair = (sha(verified), sha(original))
    need(source_pair == (SOURCE, ORIGINAL), "prefix source pair differs")
    verifier = [str(tool / "bin/verifast"), "-rustc_args", "--edition 2021",
                "-verbose", "2", "verified/lib.rs"]
    base = env.copy()
    base["LD_LIBRARY_PATH"] = f"{a.compiler_sysroot}/lib:{tool}/bin:" + base.get("LD_LIBRARY_PATH", "")
    base["SMALLSORT_CLOUD_PROVIDER_PATH"] = str(a.cloud_dir / "provider.py")
    base["SORT4_ACTUAL_AST_SCOPE_TEST"] = "1"
    base["SORT4_STRICT_LFT_CUT"] = "1"
    base["SORT4_C1_OUTPUT_EQ"] = "1"
    base["SORT4_ACTUAL_C1_PREFIX_TEST"] = "1"
    base["SORT4_C1_PREFIX_CONTROL"] = "none"
    base.pop("SORT4_C1_DEBT_CONTROL", None)
    baseline_audit = read(a.evidence / "baseline-check.json")
    prefix_support = {
        "source_pair_sha256": list(source_pair), "pre_ast_sha256": AST,
        "complete_typed_mir": GRAPH,
        "normal_mir_complete": baseline_audit.get("complete_graph_sha256", {}).get("normal") == GRAPH["normal"],
        "readonly_mir_complete": baseline_audit.get("complete_graph_sha256", {}).get("readonly") == GRAPH["readonly"],
        "proof_std_sha256": snapshot(a, tool)["proof_std"],
        "kernel_sha256": sha(tool / KERNEL), "unwind_paths_enabled": True,
        "one_runtime_body_enforced_by_patch": True,
        "full_source_and_mir_admission_before_prefix": True,
        "accepted": False}
    need(prefix_support["normal_mir_complete"] and prefix_support["readonly_mir_complete"] and
         prefix_support["unwind_paths_enabled"],
         "prefix support proof mode/full MIR baseline differs")
    record(a.evidence / "prefix-support-gate.json", prefix_support)

    # The already-existing full-target run is a required c2 control with prefix
    # explicitly disabled. It must fail at the original source-195 token blocker.
    full = (a.evidence / "actual-on.log").read_text(errors="replace")
    full_errors = [s for s in full.splitlines() if ": error:" in s or s.startswith("Fatal error:")]
    full_code = int((a.evidence / "actual-on-exit-code.txt").read_text().strip())
    need(full_code in (1, 2) and len(full_errors) == 1 and
         full_errors[0].startswith("verified/lib.rs(195,") and
         "ref_precreated_token" in full_errors[0],
         "fresh prefix-off full-target control did not reproduce c2 source-195 blocker")
    record(a.evidence / "prefix-off-full-target-control.json", {
        "classification": "FULL_TARGET_CONTROL_C2_SOURCE195_BLOCKER_NO_PROOF_CREDIT",
        "prefix_env": "0/default-off", "exit": full_code,
        "first_error": full_errors[0], "source_sha256": SOURCE,
        "log_sha256": sha(a.evidence / "actual-on.log"), "proof_credit": False})

    def run_case(name: str, case_env: dict[str, str], *, cwd: Path = fixture,
                 command: list[str] = verifier) -> tuple[int, str, list[str], list[int]]:
        code = stage(a, name, command, cwd=cwd, env=case_env, cap=850)
        log = (a.evidence / f"{name}.log").read_text(errors="replace")
        errors = [s for s in log.splitlines() if ": error:" in s or s.startswith("Fatal error:")]
        entries = module(a.cloud_dir / "strict-cut-false-posts-audit.py",
                         "prefix_proof_entries").proof_entries(log, "sort4_stable")
        return code, log, errors, entries

    def prefix_admission(log: str, control: str) -> bool:
        markers = [s for s in log.splitlines()
                   if s.startswith("SORT4-ACTUAL-C1-PREFIX-ONLY admitted ")]
        source_rows = re.findall(
            r"SORT4-ACTUAL-AST-SCOPE-TEST admitted source=([0-9a-f]{64}) "
            r"pre_ast=([0-9a-f]{64}) post_ast=([0-9a-f]{64}) "
            r"header_posts=([0-9a-f]{64})", log)
        return (len(markers) == 1 and f"control={control} " in markers[0] and
                len(source_rows) == 1 and source_rows[0][0] == SOURCE and
                source_rows[0][1] == AST and "NOT_CALLABLE_SUMMARY" in markers[0])

    def prefix_ast_inventory(path: Path) -> dict:
        if not path.is_file() or path.stat().st_size == 0:
            return {"status": "NOT_CONFIRMED", "reason": "post-splice AST dump missing"}
        text = path.read_text(errors="replace")
        name_hits = list(re.finditer(r'"sort4_stable",\s*\[', text))
        spans = {}
        for hit in name_hits:
            func_starts = list(re.finditer(r"Func\s*\(", text[:hit.start()]))
            func_start = func_starts[-1] if func_starts else None
            start = func_start.start() if func_start else -1
            opening = func_start.end() - 1 if func_start else -1
            if opening < 0:
                continue
            depth, quoted, escaped, end = 0, False, False, None
            for index in range(opening, len(text)):
                char = text[index]
                if quoted:
                    if escaped:
                        escaped = False
                    elif char == "\\":
                        escaped = True
                    elif char == '"':
                        quoted = False
                    continue
                if char == '"':
                    quoted = True
                elif char == "(":
                    depth += 1
                elif char == ")":
                    depth -= 1
                    if depth == 0:
                        end = index + 1
                        break
            if end is not None and hit.start() < end:
                spans[start] = text[start:end]
        if len(spans) != 1:
            return {"status": "NOT_CONFIRMED", "reason": "named prefix AST function absent or ambiguous",
                    "name_occurrences": len(name_hits), "function_spans": len(spans),
                    "ast_sha256": sha(path)}
        body = next(iter(spans.values()))
        calls = [(int(line), callee) for line, callee in re.findall(
            r'CallExpr\s*\(\s*loc\s+"verified/lib.rs\((\d+),[^"]+"\s*,\s*"([^"]+)"', body)]
        # The runtime comparator is the exact resolved FnMut call. OutputEq
        # also inserts a ghost registration CallExpr at this same source span;
        # keep it separately so it cannot inflate the runtime inventory.
        c1_calls = [(line, callee) for line, callee in calls if line == 190]
        c1_fnmut = [(line, callee) for line, callee in c1_calls
                    if callee == "std::ops::FnMut::call_mut"]
        ghost_equality = [(line, callee) for line, callee in c1_calls
                          if "register_type_projection_equality" in callee]
        other_c1_calls = [(line, callee) for line, callee in c1_calls
                          if (line, callee) not in c1_fnmut + ghost_equality]
        selectors = [(line, callee) for line, callee in calls
                     if "select" in callee.lower()]
        copies = [(line, callee) for line, callee in calls
                  if "copy_nonoverlapping" in callee.lower() or callee.lower() in ("copy", "copy_from_slice")]
        confirmed = (len(c1_fnmut) == 1 and len(ghost_equality) == 1 and
                     not other_c1_calls and not selectors and not copies)
        return {"status": "CONFIRMED_SOURCE_LINKED_PREFIX_RUNTIME_INVENTORY" if confirmed else "NOT_CONFIRMED",
                "source": "verified/lib.rs", "named_function": "sort4_stable",
                "named_function_ast_sha256": hashlib.sha256(body.encode()).hexdigest(),
                "c1_source_line": 190, "fnmut_calls_at_c1": c1_fnmut,
                "ghost_type_equality_registration_at_c1": ghost_equality,
                "other_calls_at_c1_rejected": other_c1_calls,
                "selector_calls_in_named_function": selectors,
                "copy_calls_in_named_function": copies,
                "runtime_inventory": {"FnMut": len(c1_fnmut), "selector": len(selectors), "copy": len(copies)},
                "ast_sha256": sha(path), "proof_verdict": None}

    # The pinned translator emits the changed target declaration itself during
    # this exact VF0 invocation. Clear stale output immediately before proof;
    # preserve/hash the emitted bytes before any negative-control runs.
    ast_live = fixture / "actual-c1-prefix-post-ast.ml"
    if ast_live.exists():
        ast_live.unlink()
    positive_code, positive_log, positive_errors, positive_entries = run_case(
        "actual-prefix-on", base)
    ast_evidence = a.evidence / "actual-c1-prefix-post-ast.ml"
    if ast_live.is_file() and ast_live.stat().st_size > 0:
        ast_evidence.write_bytes(ast_live.read_bytes())
    ast_inventory = prefix_ast_inventory(ast_evidence)
    ast_inventory["ast_serializer_sha256"] = sha(ast_evidence) if ast_evidence.is_file() else None
    positive_stage = read(a.evidence / "actual-prefix-on-stage.json")
    ast_inventory["same_invocation"] = "actual-prefix-on"
    ast_inventory["same_invocation_log_sha256"] = sha(a.evidence / "actual-prefix-on.log")
    ast_inventory["same_invocation_stage_sha256"] = sha(a.evidence / "actual-prefix-on-stage.json")
    ast_inventory["same_invocation_exit"] = positive_stage.get("exit")
    ast_inventory["emitted_before_target_verification_by_pinned_translator"] = True
    prefix_lines = [s for s in positive_log.splitlines()
                    if s.startswith("SORT4-ACTUAL-C1-PREFIX-ONLY admitted ")]
    admitted_lines = re.findall(
        r"SORT4-ACTUAL-AST-SCOPE-TEST admitted source=([0-9a-f]{64}) "
        r"pre_ast=([0-9a-f]{64}) post_ast=([0-9a-f]{64}) "
        r"header_posts=([0-9a-f]{64})", positive_log)
    prefix_fields = (re.search(r"post_ast=([0-9a-f]{64}) NOT_CALLABLE_SUMMARY$",
                               prefix_lines[0]) if len(prefix_lines) == 1 else None)
    prefix_post = prefix_fields.group(1) if prefix_fields else None
    ast_inventory["positive_prefix_post_ast_marker_sha256"] = prefix_post
    ast_inventory["serializer_sha256_is_distinct_from_node_sha256"] = (
        ast_inventory.get("ast_serializer_sha256") is not None and prefix_post is not None and
        ast_inventory["ast_serializer_sha256"] != prefix_post)
    prefix_marker_ok = (len(prefix_lines) == 1 and "normal_boundary=after_source194" in prefix_lines[0] and
                        "before_c2=source195" in prefix_lines[0] and
                        "fnmut=1 outcomes=normal,direct_unwind" in prefix_lines[0] and
                        "NOT_CALLABLE_SUMMARY" in prefix_lines[0])
    positive_admission_ok = (len(admitted_lines) == 1 and admitted_lines[0][0] == SOURCE and
                             admitted_lines[0][1] == AST and
                             admitted_lines[0][2] == prefix_post and
                             admitted_lines[0][3] == original_header_posts)
    ast_inventory["marker_and_ast_share_positive_invocation"] = (
        prefix_post is not None and positive_stage.get("exit") == positive_code and
        ast_inventory.get("same_invocation") == "actual-prefix-on" and
        ast_inventory.get("status") == "CONFIRMED_SOURCE_LINKED_PREFIX_RUNTIME_INVENTORY" and
        positive_admission_ok)
    record(a.evidence / "actual-prefix-post-splice-ast.json", ast_inventory)
    dead_code_lines = [s for s in positive_log.splitlines()
                       if re.search(r"\): dead code$", s)]
    target_segment = positive_log[positive_entries[0]:] if len(positive_entries) == 1 else ""
    prefix_helper_parser = module(a.cloud_dir / "strict-cut-false-posts-audit.py",
                                   "prefix_positive_helper_entries")
    prefix_helpers = {}
    for helper in ("recover_pair", "join_four_owned_cells"):
        helper_entries = prefix_helper_parser.proof_entries(positive_log, helper)
        before_caller = (len(helper_entries) == 1 and len(positive_entries) == 1 and
                         helper_entries[0] < positive_entries[0])
        segment = (positive_log[helper_entries[0]:positive_entries[0]]
                   if before_caller else "")
        prefix_helpers[helper] = {"entries": len(helper_entries),
                                  "verified_before_target": before_caller,
                                  "return_seen": "Executing return statement" in segment,
                                  "leak_seen": "Leak check." in segment,
                                  "error_absent_before_target": ": error:" not in segment}
    prefix_helpers_ok = all(row["verified_before_target"] and row["return_seen"] and
                            row["leak_seen"] and row["error_absent_before_target"]
                            for row in prefix_helpers.values())
    positive_body_ok = (positive_code == 0 and not positive_errors and len(positive_entries) == 1 and
                        prefix_helpers_ok and not dead_code_lines and "0 errors found (" in positive_log and
                        "Leak check." in positive_log and prefix_admission(positive_log, "none"))
    # Full VF0/post/leak checks support only this bounded trace theorem. Never
    # turn this result into a callable summary for sort4_stable.
    prefix_positive = (positive_body_ok and prefix_marker_ok and positive_admission_ok and
                       ast_inventory.get("marker_and_ast_share_positive_invocation") is True and
                       ast_inventory.get("serializer_sha256_is_distinct_from_node_sha256") is True and
                       ast_inventory.get("status") ==
                       "CONFIRMED_SOURCE_LINKED_PREFIX_RUNTIME_INVENTORY")
    record(a.evidence / "actual-prefix-positive-result.json", {
        "classification": ("PREFIX_ONLY_BOUNDED_C1_THEOREM" if prefix_positive else
                           "PREFIX_ONLY_NOT_CONFIRMED_POST_SPLICE_AST" if positive_body_ok else
                           "PREFIX_ONLY_FIRST_BLOCKER_DIAGNOSTIC"),
        "accepted": False, "actual_sort4_proved": False,
        "full_body_exit_zero": False, "full_summary": False,
        "callable_summary": "PREFIX_ONLY_NOT_CALLABLE_SUMMARY",
        "exit": positive_code, "first_error": positive_errors[0] if positive_errors else None,
        "target_function_entry_seen": len(positive_entries) == 1,
        "same_unit_helpers_verified_before_prefix_target": prefix_helpers,
        "exactly_one_prefix_only_marker": len(prefix_lines) == 1,
        "source_pre_ast_and_original_header_posts_match": positive_admission_ok,
        "positive_post_ast_sha256_captured": prefix_post,
        "post_splice_ast_inventory": ast_inventory,
        "bounded_full_vf0_normal_unwind_post_return_leak": prefix_positive,
        "dead_code_diagnostics": dead_code_lines,
        "log_mentions_normal_return_after_target_header": "Executing return statement" in target_segment,
        "log_mentions_recovery_after_target_header": "recover_pair" in target_segment,
        "log_mentions_join_after_target_header": "join_four_owned_cells" in target_segment,
        "log_mentions_unwind_after_target_header": "unwind" in target_segment.lower(),
        "log_mentions_leak_check": "Leak check." in positive_log,
        "source_pair_sha256": list(source_pair),
        "raw_precondition_debts": ["positive-size T", "source4 ownership", "CURRENT F cell/ownership/thread/type subset", "optional destination", "stock type interpretation"],
        "native_entry_subset_theorem": "separate prerequisite only; does not discharge positive-size, type_interp, or dst4 debts",
        "raw_log_sha256": sha(a.evidence / "actual-prefix-on.log"),
        "proof_credit_scope": "bounded prefix termination only"})

    # Existing exact debt negatives must remain attached to recover_pair under
    # the new prefix projection.
    proof_parser = module(a.cloud_dir / "strict-cut-false-posts-audit.py", "prefix_debt_entries")
    debt_rows = {}
    expected_callee_error = (
        "verified/lib.rs(68,29-30): error: No matching heap chunks: "
        "comparison_debt<T>(t, _, ptr_add_(v_base, 1, T_typeid), v_base, _, _, _, _)")
    for mode, source_line, call_span in (
            ("normal-missing-close", 193, "verified/lib.rs(193,30-31): note: Verifying call"),
            ("unwind-missing-close", 187, "verified/lib.rs(187,32-33): note: Verifying call")):
        case_env = base.copy()
        case_env["SORT4_C1_DEBT_CONTROL"] = mode
        name = "actual-prefix-" + mode
        code, log, errors, entries = run_case(name, case_env)
        helper_entries = proof_parser.proof_entries(log, "recover_pair")
        call_note_hits = [m.start() for m in re.finditer(re.escape(call_span), log)]
        caller_note = log.find("note: Verifying function 'sort4_stable'", log.find(errors[0]) if errors else 0)
        intended = (code == 1 and len(errors) == 1 and len(entries) == 1 and
                    len(helper_entries) == 1 and entries[0] < log.index(errors[0]) and
                    helper_entries[0] < entries[0] and
                    prefix_admission(log, "none") and
                    errors[0] == expected_callee_error and
                    len(call_note_hits) == 1 and log.index(errors[0]) < call_note_hits[0] < caller_note and
                    source_line in (193, 187))
        debt_rows[mode] = {"classification": "INTENDED_MISSING_C1_DEBT" if intended else "INCONCLUSIVE_WRONG_FIRST_OBLIGATION",
                           "exit": code, "first_error": errors[0] if errors else None,
                           "expected_callee_predicate_location": "verified/lib.rs(68,29-30): comparison_debt<T>",
                           "expected_mode_callsite_note": call_span,
                           "callsite_note_count": len(call_note_hits),
                           "caller_body_entry_before_callee_error": bool(entries and errors and entries[0] < log.index(errors[0])),
                           "recover_pair_proved_before_caller": bool(helper_entries and entries and helper_entries[0] < entries[0]),
                           "intended_resource_negative": intended,
                           "log_sha256": sha(a.evidence / f"{name}.log")}
    record(a.evidence / "actual-prefix-debt-controls.json", debt_rows)

    # Fresh exact first-error expectations for these four prefix mutations are
    # not available yet. Record first error and branch observations, but keep
    # every control inconclusive until a saved fresh replay pins predicate and
    # location. Never infer intent from a generic postcondition word.
    control_rows = {}
    for control in ("normal-false-post", "unwind-false-post",
                    "normal-omit-join", "unwind-omit-join"):
        case_env = base.copy()
        case_env["SORT4_C1_PREFIX_CONTROL"] = control
        name = "actual-prefix-control-" + control
        code, log, errors, entries = run_case(name, case_env)
        entry = entries[0] if len(entries) == 1 else -1
        target_log = log[entry:] if entry >= 0 else ""
        mode_branch = ("normal-return" if control.startswith("normal-") else "direct-unwind")
        branch_observation = {
            "normal_return_event_after_body_entry": "Executing return statement" in target_log,
            "unwind_event_after_body_entry": "unwind" in target_log.lower(),
            "join_call_trace_after_body_entry": [line for line in target_log.splitlines()
                if "Verifying call" in line and "join_four_owned_cells" in line],
            "prefix_control_marker_admitted": prefix_admission(log, control)}
        control_rows[control] = {"classification": "INCONCLUSIVE_UNPINNED_EXPECTED_FIRST_OBLIGATION",
                                 "exit": code, "first_error": errors[0] if errors else None,
                                 "first_error_count": len(errors),
                                 "target_body_entry_count": len(entries),
                                 "target_body_entry_before_first_error": bool(entries and errors and entry < log.index(errors[0])),
                                 "recover_pair_and_join_helpers_before_target": {
                                     name: bool((hits := proof_parser.proof_entries(log, name)) and entries and hits[0] < entries[0])
                                     for name in ("recover_pair", "join_four_owned_cells")},
                                 "expected_branch": mode_branch,
                                 "expected_first_stage_predicate_location": None,
                                 "expected_control_semantics": control,
                                 "join_omission_injected_by_pinned_patch": (control.endswith("omit-join") and
                                                                            prefix_admission(log, control)),
                                 "branch_observations_not_proof": branch_observation,
                                 "intended_negative": False,
                                 "reason": "no fresh saved prefix replay pins this control's exact first stage/predicate/location",
                                 "log_sha256": sha(a.evidence / f"{name}.log")}
    record(a.evidence / "actual-prefix-negative-controls.json", control_rows)

    # Mutate a disposable fixture's exact source bytes. This must be rejected
    # by the pinned source hash before any target body proof is entered.
    mutant = a.evidence / "source-changed-c1-operand-fixture"
    need(not mutant.exists(), "source-hash mutant fixture already exists")
    need(stage(a, "prefix-source-mutant-copy", ["cp", "-a", str(fixture), str(mutant)], cap=120) == 0,
         "source-hash mutant fixture copy failed")
    mutant_source = (mutant / "verified/lib.rs").read_bytes()
    operand = b"v_base.add(1)"
    need(mutant_source.count(operand) == 1,
         "source mutant expected exactly one first c1 operand")
    (mutant / "verified/lib.rs").write_bytes(mutant_source.replace(operand, b"v_base.add(2)", 1))
    mutant_env = base.copy()
    name = "actual-prefix-source-hash-control"
    code, log, errors, entries = run_case(name, mutant_env, cwd=mutant)
    source_refusal = (code in (1, 2) and len(errors) == 1 and
                      "verified source SHA256" in errors[0] and not entries and
                      "Verifying function 'sort4_stable'" not in log)
    source_control = {"classification": "EXACT_SOURCE_HASH_REFUSAL_NOT_RESOURCE_NEGATIVE" if source_refusal else
                      "INCONCLUSIVE_SOURCE_MUTATION_CONTROL",
                      "exit": code, "first_error": errors[0] if errors else None,
                      "target_body_entered": bool(entries),
                      "mutated_source_sha256": sha(mutant / "verified/lib.rs"),
                      "intended_refusal": source_refusal,
                      "log_sha256": sha(a.evidence / f"{name}.log")}
    record(a.evidence / "actual-prefix-source-hash-control.json", source_control)
    need((sha(verified), sha(original)) == source_pair,
         "prefix controls changed pinned actual source pair")
    result = {"classification": "PREFIX_ONLY_NOT_CALLABLE_SUMMARY",
              "accepted": False, "actual_sort4_proved": False,
              "full_body_exit_zero": False, "full_summary": False,
              "positive": read(a.evidence / "actual-prefix-positive-result.json"),
              "missing_debt_controls": debt_rows,
              "missing_debt_controls_all_intended": all(r["intended_resource_negative"] for r in debt_rows.values()),
              "post_and_join_controls": control_rows,
              "post_and_join_controls_all_intended": False,
              "source_hash_control": source_control,
              "all_controls_intended": all(r["intended_resource_negative"] for r in debt_rows.values()) and
                                       all(r["intended_negative"] for r in control_rows.values()) and source_refusal,
              "proof_credit_scope": "bounded prefix only; never a callable actual_sort4 summary"}
    record(a.evidence / "actual-prefix-diagnostic-audit.json", result)
    return result


def actual(a, fixture: Path, tool: Path, env: dict[str, str]) -> dict:
    verified = fixture / "verified/lib.rs"
    original = fixture / "original/lib.rs"
    before = (sha(verified), sha(original))
    need(before == (SOURCE, ORIGINAL), "actual fixture changed before test")
    env = env.copy()
    env["SORT4_ACTUAL_C1_PREFIX_TEST"] = "0"
    env["SORT4_C1_PREFIX_CONTROL"] = "none"
    env["LD_LIBRARY_PATH"] = f"{a.compiler_sysroot}/lib:{tool}/bin:" + env.get("LD_LIBRARY_PATH", "")
    env["SMALLSORT_CLOUD_PROVIDER_PATH"] = str(a.cloud_dir / "provider.py")
    env.pop("SORT4_HRTB_OUTPUT", None)
    env.pop("SORT4_HRTB_OUTPUT_TARGETS", None)
    env.pop("SORT4_CALLBACK_UNWIND", None)
    env.pop("SORT4_STRICT_LFT_TRACE", None)
    env.pop("SORT4_STRICT_LFT_RELOCATE", None)
    env.pop("SORT4_C1_DEBT_CONTROL", None)
    verifier = [str(tool / "bin/verifast"), "-rustc_args", "--edition 2021",
                "-verbose", "2", "verified/lib.rs"]
    off = env.copy()
    off["SORT4_ACTUAL_AST_SCOPE_TEST"] = "0"
    off.pop("SORT4_STRICT_LFT_CUT", None)
    off_code = stage(a, "actual-off", verifier, cwd=fixture, env=off, cap=420)
    off_log = (a.evidence / "actual-off.log").read_text(errors="replace")
    off_errors = [s for s in off_log.splitlines()
                  if ": error:" in s or s.startswith("Fatal error:")]
    record(a.evidence / "actual-off-result.json", {
        "exit": off_code, "errors": off_errors, "raw_log": "actual-off.log",
        "kind": "admission_control_only_not_resource_negative"})
    need(off_code in (1, 2) and len(off_errors) == 1 and
         "Strict lifetime binding requires explicit overnight opt-in" in off_errors[0] and
         "SORT4-ACTUAL-AST-SCOPE-TEST admitted" not in off_log,
         "default-off/strict opt-in control changed")
    on = env.copy()
    on["SORT4_ACTUAL_AST_SCOPE_TEST"] = "1"
    on["SORT4_STRICT_LFT_CUT"] = "1"
    on["SORT4_C1_OUTPUT_EQ"] = "0"
    noeq_code = stage(a, "actual-output-eq-off", verifier, cwd=fixture, env=on, cap=420)
    noeq_log = (a.evidence / "actual-output-eq-off.log").read_text(errors="replace")
    noeq_errors = [s for s in noeq_log.splitlines() if ": error:" in s or s.startswith("Fatal error:")]
    noeq_ok = noeq_code == 1 and len(noeq_errors) == 1 and noeq_errors[0] == (
        "verified/lib.rs(190,18-89): error: Type mismatch. Actual: "
        "<F as std::ops::FnOnce<std_tuple_2_<&'cmp T, &'cmp T>>>::Output. Expected: bool.")
    record(a.evidence / "actual-output-eq-off-result.json", {
        "exit": noeq_code, "errors": noeq_errors, "intended_type_obligation": noeq_ok,
        "resource_negative": False, "raw_log": "actual-output-eq-off.log"})
    need(noeq_ok and "SORT4-C1-OUTPUT-EQ " not in noeq_log,
         "c1 Output equality OFF missed exact original type obligation")
    on["SORT4_C1_OUTPUT_EQ"] = "1"
    on["SORT4_ACTUAL_C1_PREFIX_TEST"] = "0"
    on["SORT4_C1_PREFIX_CONTROL"] = "none"
    on_code = stage(a, "actual-on", verifier, cwd=fixture, env=on, cap=850)
    on_log = (a.evidence / "actual-on.log").read_text(errors="replace")
    record(a.evidence / "actual-on-raw-result.json", {
        "exit": on_code, "raw_log": "actual-on.log", "source_hashes": list(before),
        "proof_verdict": "PENDING_SEPARATE_AUDIT"})
    admitted = re.findall(
        r"SORT4-ACTUAL-AST-SCOPE-TEST admitted source=([0-9a-f]{64}) "
        r"pre_ast=([0-9a-f]{64}) post_ast=([0-9a-f]{64}) "
        r"header_posts=([0-9a-f]{64})", on_log)
    errors = [s for s in on_log.splitlines()
              if ": error:" in s or s.startswith("Fatal error:")]
    output_eq_sites = [line for line in on_log.splitlines() if line.startswith("SORT4-C1-OUTPUT-EQ ")]
    output_eq_ok = (len(output_eq_sites) == 1 and
                    "compiler_clause=unique_F_T_bool" in output_eq_sites[0] and
                    "verified/lib.rs(190," in output_eq_sites[0] and
                    "count=1 later_calls=0" in output_eq_sites[0])
    admitted_ok = (len(admitted) == 1 and admitted[0][0] == SOURCE and
                   admitted[0][1] == AST and admitted[0][2] != AST)
    marker_absent = not any("No such function: __vf_sort4_first_unwind" in s
                            for s in errors)
    target = "Verifying function 'sort4_stable'"
    proof_parser = module(a.cloud_dir / "strict-cut-false-posts-audit.py", "c1_actual_entries")
    caller_entries = proof_parser.proof_entries(on_log, "sort4_stable")
    entered = len(caller_entries) == 1
    helper_rows = {}
    for name in ("recover_pair", "join_four_owned_cells"):
        entries = proof_parser.proof_entries(on_log, name)
        before_caller = entered and len(entries) == 1 and entries[0] < caller_entries[0]
        segment = on_log[entries[0]:caller_entries[0]] if before_caller else ""
        helper_rows[name] = {"entries": len(entries), "before_caller": before_caller,
                             "return_seen": "Executing return statement" in segment,
                             "leak_seen": "Leak check." in segment,
                             "error_absent": ": error:" not in segment}
    helpers_ok = all(row["before_caller"] and row["return_seen"] and
                     row["leak_seen"] and row["error_absent"] for row in helper_rows.values())
    record(a.evidence / "same-unit-callee-gate.json", {
        "gate_passed": helpers_ok, "proof_sha": os.environ["PROOF_SHA"],
        "source_sha256": before[0], "actual_on_log_sha256": sha(a.evidence / "actual-on.log"),
        "helpers": helper_rows})
    complete = (output_eq_ok and helpers_ok and admitted_ok and marker_absent and entered and on_code == 0 and
                not errors and "Leak check." in on_log and
                re.search(r"0 errors found \(\d+ statements verified\)", on_log) is not None)
    substantive = (output_eq_ok and helpers_ok and admitted_ok and marker_absent and entered and
                   on_code in (1, 2) and bool(errors) and
                   (errors[0].startswith("verified/lib.rs(") or
                    (errors[0].startswith("/workspace/") and "/bin/rust/" in errors[0] and
                     ".rsspec(" in errors[0])) and
                   caller_entries[0] < on_log.index(errors[0]))
    debt_manifest = read(a.proof_root / DEBT_MANIFEST)
    need(admitted_ok and admitted[0][2] == debt_manifest["positive_post_ast_sha256"] and
         admitted[0][3] == debt_manifest["header_posts_sha256"],
         "positive c1 AST/posts changed under negative-control console")
    debt_rows = {}
    for mode, source_line in (("normal-missing-close", 193), ("unwind-missing-close", 187)):
        case_env = on.copy()
        case_env["SORT4_C1_DEBT_CONTROL"] = mode
        case_name = "actual-" + mode
        code = stage(a, case_name, verifier, cwd=fixture, env=case_env, cap=420)
        case_log = (a.evidence / (case_name + ".log")).read_text(errors="replace")
        case_errors = [line for line in case_log.splitlines() if ": error:" in line or line.startswith("Fatal error:")]
        entries = proof_parser.proof_entries(case_log, "sort4_stable")
        intended = (code == 1 and len(case_errors) == 1 and len(entries) == 1 and
                    case_errors[0].startswith(f"verified/lib.rs({source_line},") and
                    "No matching heap chunks: comparison_debt<T>" in case_errors[0] and
                    entries[0] < case_log.index(case_errors[0]))
        row = {"mode": mode, "exit": code, "first_error": case_errors[0] if case_errors else None,
               "intended_resource_negative": intended, "source_sha256": sha(verified),
               "log_sha256": sha(a.evidence / (case_name + ".log")),
               "classification": "INTENDED_MISSING_C1_DEBT" if intended else "INCONCLUSIVE_WRONG_FIRST_OBLIGATION"}
        debt_rows[mode] = row
        record(a.evidence / (case_name + "-result.json"), row)
    debt_controls_ok = all(row["intended_resource_negative"] for row in debt_rows.values())
    need((sha(verified), sha(original)) == before,
         "actual source pair changed during verification")
    result = {
        "classification": ("EXPERIMENTAL_FULL_BODY_VF0_NOT_ACCEPTED" if complete else
                           "C1_FIRST_SUBSTANTIVE_BLOCKER_DIAGNOSTIC" if substantive else
                           "INCONCLUSIVE_SETUP_OR_AST_ADMISSION"),
        "accepted": False, "diagnostic_complete": complete or substantive,
        "actual_sort4_proved": False,
        "continuation_representation_observed": admitted_ok and marker_absent and entered,
        "c1_normal_resource_recovery": "NOT_PROVED_BY_THIS_DIAGNOSTIC",
        "c1_direct_unwind_resource_recovery": "NOT_PROVED_BY_THIS_DIAGNOSTIC",
        "full_body_exit_zero_diagnostic": complete,
        "normal_and_unwind_path_independently_proved": False,
        "actual_on_exit": on_code, "first_error": errors[0] if errors else None,
        "off_first_error": off_errors[0], "admission_hashes": admitted[0] if admitted else None,
        "actual_debt_controls": debt_rows,
        "actual_debt_controls_all_intended": debt_controls_ok,
        "compiler_c1_output_equality": {"gate_passed": output_eq_ok, "sites": output_eq_sites},
        "same_unit_recovery_callees_verified_before_caller": helpers_ok,
        "target_header_seen": entered, "reserved_handler_refusal_absent": marker_absent,
        "raw_log_paths": {"off": "actual-off.log", "on": "actual-on.log"},
        "raw_observations_not_path_proofs": {
            "c1_source_call": [s for s in on_log.splitlines()
                               if "verified/lib.rs(190" in s and "Verifying call" in s][:12],
            "debt": [s for s in on_log.splitlines() if "end_lft_binding" in s][:12],
            "pair_recovery": [s for s in on_log.splitlines() if "recover_pair" in s][:12],
            "four_cell_join": [s for s in on_log.splitlines() if "join_four_owned_cells" in s][:12],
            "return": [s for s in on_log.splitlines() if "Executing return statement" in s][:12],
            "normal_post": [s for s in on_log.splitlines()
                            if "postcondition" in s.lower() or "ensuring" in s.lower()][:24],
            "unwind": [s for s in on_log.splitlines() if "unwinding" in s.lower()][:24],
            "leak_check": [s for s in on_log.splitlines() if "Leak check." in s][:12]},
        "mutation_controls": ("NOT_RUN_READY_FOR_REVIEWED_AST_MUTANTS" if complete else
                              "NOT_RUN_BASELINE_NOT_COMPLETE"),
        "mutation_control_limit": "Source/hash admission failures are frontend refusals, not missing-debt/wrong-edge/duplicate resource negatives; separate reviewed AST mutants are required",
        "open_gates": ["actual c2 through c5 and select/copy calls", "full destination initialization",
                       "unrestricted generic/ZST", "all-path liveness and alias/escape mutations",
                       "pointer provenance, ownership, no-cut/S6 integration", "functional composition"]}
    prefix_result = actual_prefix(a, fixture, tool, env, admitted[0][3])
    result["bounded_prefix"] = prefix_result
    result["actual_sort4_proved"] = False
    record(a.evidence / "actual-on-result.json", result)
    record(a.evidence / "diagnostic-audit.json", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("production-source", "production-applied-patch", "stock-home",
                 "compiler-sysroot", "evidence", "proof-root", "work-root", "cloud-dir"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--deadline-epoch", type=int, required=True)
    a = parser.parse_args()
    env = os.environ.copy()
    deps = a.work_root / "vfdeps-adf88dc"
    env["PATH"] = f"{deps}/bin:" + env.get("PATH", "")
    env["CAPNP_INC_DIR"] = str(deps / "include")
    env["RUSTUP_TOOLCHAIN"] = "nightly-2026-09-25"
    env["SMALLSORT_CLOUD_PROVIDER_PATH"] = str(a.cloud_dir / "provider.py")
    need((deps / "bin").is_dir() and (deps / "include").is_dir() and
         (deps / "lib").is_dir(), "frozen vfdeps missing")
    env["LD_LIBRARY_PATH"] = f"{a.compiler_sysroot}/lib:{deps}/lib:" + env.get("LD_LIBRARY_PATH", "")
    try:
        base, patch, old = setup(a, env)
        fixture = baseline(a, env)
        tool = build_overlay(a, base, patch, old, env)
        controls = strict_controls(a, tool, env)
        need(set(controls["controls"]) == set(CONTROLS) and
             set(controls["false_posts"]) == set(FALSE_POSTS),
             "explicit prerequisite gate set incomplete")
        record(a.evidence / "actual-admission-prerequisites.json", {
            "gates_passed": True, "controls_check_sha256": sha(a.evidence / "controls-check.json"),
            "baseline_check_sha256": sha(a.evidence / "baseline-check.json"),
            "tool_snapshot_sha256": sha(a.evidence / "c1-tool-snapshot.json"),
            "reuse_saved_controls": False, "actual_started_only_after_gates": True})
        result = actual(a, fixture, tool, env)
        need(snapshot(a, base) == old and
             git(a.production_source, "diff", "--binary", "HEAD") ==
             a.production_applied_patch.read_bytes(),
             "source/tool identity changed after c1 diagnostic")
        print(json.dumps({"classification": result["classification"],
                          "first_error": result["first_error"]}, sort_keys=True), flush=True)
    except Exception as exc:
        if a.evidence.is_dir():
            record(a.evidence / "collector-error.json", {
                "classification": "AUDIT_OR_STAGE_ERROR_NOT_PROOF_VERDICT",
                "reason": str(exc), "existing_actual_results_preserved": True})
            if not (a.evidence / "diagnostic-audit.json").exists():
                record(a.evidence / "diagnostic-audit.json", {
                "classification": "INCONCLUSIVE_SETUP_OR_GATE",
                "reason": str(exc), "accepted": False, "diagnostic_complete": False,
                "actual_sort4_proved": False,
                "last_stage": (read(a.evidence / "stage-progress.json")
                               if (a.evidence / "stage-progress.json").is_file() else None)})
        raise


if __name__ == "__main__":
    main()
