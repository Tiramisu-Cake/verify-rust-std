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
                intended_stage = target_header not in proof_log
            else:
                intended_stage = (bool(errors) and target_header in proof_log and
                                  proof_log.index(target_header) < proof_log.index(errors[0]))
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


def actual(a, fixture: Path, tool: Path, env: dict[str, str]) -> dict:
    verified = fixture / "verified/lib.rs"
    original = fixture / "original/lib.rs"
    before = (sha(verified), sha(original))
    need(before == (SOURCE, ORIGINAL), "actual fixture changed before test")
    env = env.copy()
    env["LD_LIBRARY_PATH"] = f"{a.compiler_sysroot}/lib:{tool}/bin:" + env.get("LD_LIBRARY_PATH", "")
    env["SMALLSORT_CLOUD_PROVIDER_PATH"] = str(a.cloud_dir / "provider.py")
    env.pop("SORT4_HRTB_OUTPUT", None)
    env.pop("SORT4_HRTB_OUTPUT_TARGETS", None)
    env.pop("SORT4_CALLBACK_UNWIND", None)
    env.pop("SORT4_STRICT_LFT_TRACE", None)
    env.pop("SORT4_STRICT_LFT_RELOCATE", None)
    verifier = [str(tool / "bin/verifast"), "-rustc_args", "--edition 2021",
                "-verbose", "1", "verified/lib.rs"]
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
                   errors[0].startswith("verified/lib.rs(") and
                   on_log.index(target) < on_log.index(errors[0]))
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
                "last_completed_stage": sorted(
                    p.name for p in a.evidence.glob("*-stage.json"))[-1:]})
        raise


if __name__ == "__main__":
    main()
