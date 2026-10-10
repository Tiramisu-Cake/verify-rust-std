#!/usr/bin/env python3
"""Cloud-only native diagnostics on the exact frozen C4 translator and kernel.

Every case retains its raw source, paired MIR, refinement and full verifier log.
Collector completion is never a proof verdict. No verifier source is edited here.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time


ROOT = Path("research/challenge-8/cloud-build")
FROZEN_HERE = ROOT / "sort4-native-c4"
OPAQUE_PHASE = "SORT4-NATIVE-OPAQUE-CLOUD-2026-10-10"
OPAQUE_SESSION = os.environ.get("SORT4_NATIVE_OPAQUE_PHASE") == "1"
HERE = ROOT / ("sort4-native-opaque" if OPAQUE_SESSION else "sort4-native-c4")
TRANSLATOR = Path("src/rust_frontend/vf_mir_translator/vf_mir_translator.ml")
KERNEL = Path("src/verifast.ml")
FINAL_TRANSLATOR = "1eab6eb54fe5c23d53ca72a6d9dfcbbff09c09ffaf26c48a4f450f5068a8d313"
FINAL_KERNEL = "37ed2550d276abccbbe0a9ced678137ef587f80782bcff763062df394c2a440c"
FINAL_SOURCE = "ba9e6ad3633004c3d934c590462443951ddd6dec80a5df9ffb687ec940958c6f"
FINAL_PRE_AST = "0ed31137cf55a2ed47ed624a6c61591e4aaf96371df3c2979fc10ce8d95bb222"
PHASE = OPAQUE_PHASE if OPAQUE_SESSION else "SORT4-NATIVE-C4-CLOUD-2026-10-10"
PATCHES = (
    ("overnight-callback/ACTUAL-SORT4-AST-SCOPE-TEST.json", "profile_components.overlay_patch_sha256", "overnight-callback/verifast-actual-sort4-first-scope-TEST.patch", None, None),
    ("overnight-callback/ACTUAL-SORT4-C1-OUTPUT-EQ-TEST.json", "patch_sha256", "overnight-callback/verifast-actual-sort4-c1-output-eq-TEST.patch", None, None),
    ("overnight-callback/ACTUAL-SORT4-C1-DEBT-CONTROLS-TEST.json", "patch_sha256", "overnight-callback/verifast-actual-sort4-c1-debt-controls-TEST.patch", None, None),
    ("cloud-build/sort4-native-entry-c1/C1-PREFIX-PROFILE.json", "patch_sha256", "cloud-build/sort4-native-entry-c1/verifast-actual-c1-prefix-TEST.patch", "base_translator_sha256", "patched_translator_sha256"),
    ("cloud-build/sort4-native-entry-c1/C2-DISCOVERY-PROFILE.json", "patch_sha256", "cloud-build/sort4-native-entry-c1/verifast-actual-c2-discovery-TEST.patch", "base_translator_sha256", "patched_translator_sha256"),
    ("cloud-build/sort4-c2-bound-prefix/profile.json", "patch_sha256", "cloud-build/sort4-c2-bound-prefix/verifast-c2-bound-prefix-TEST.patch", "base_translator_sha256", "patched_translator_sha256"),
    ("cloud-build/sort4-c3-bound-prefix/capture-profile.json", "incremental_patch_sha256", "cloud-build/sort4-c3-bound-prefix/verifast-c3-capture-TEST.patch", "base_translator_sha256", "patched_translator_sha256"),
    ("cloud-build/sort4-c3-bound-prefix/profile.json", "patch_sha256", "cloud-build/sort4-c3-bound-prefix/verifast-c3-bound-prefix-TEST.patch", "base_translator_sha256", "patched_translator_sha256"),
    ("cloud-build/sort4-c4-bound-prefix/capture-profile.json", "incremental_patch_sha256", "cloud-build/sort4-c4-bound-prefix/verifast-c4-capture-TEST.patch", "base_translator_sha256", "patched_translator_sha256"),
    ("cloud-build/sort4-c4-bound-prefix/profile.json", "patch_sha256", "cloud-build/sort4-c4-bound-prefix/verifast-c4-bound-prefix-TEST.patch", "base_translator_sha256", "patched_translator_sha256"),
)
DISABLED_C_SCOPES = (
    "SORT4_ACTUAL_C1_PREFIX_TEST", "SORT4_ACTUAL_C2_DISCOVERY_TEST",
    "SORT4_ACTUAL_C2_BOUND_PREFIX_TEST", "SORT4_ACTUAL_C3_CAPTURE_TEST",
    "SORT4_ACTUAL_C3_BOUND_PREFIX_TEST", "SORT4_ACTUAL_C4_CAPTURE_TEST",
    "SORT4_ACTUAL_C4_BOUND_PREFIX_TEST", "SORT4_C2_DISCOVERY",
)
CONTROLS = ("normal-false-post", "c1-unwind-false-assert",
            "c2-unwind-false-assert", "c3-unwind-false-assert",
            "c4-unwind-false-assert")
NATIVE = ("source-typed-frame-positive", "source-typed-missing-T-negative",
          "source-typed-missing-F-negative")


def need(value: bool, reason: str) -> None:
    if not value:
        raise RuntimeError(reason)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, f"missing module {path}")
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def field(data: dict, dotted: str):
    value = data
    for key in dotted.split("."):
        value = value[key]
    return value


def stage(a, root: Path, name: str, argv: list[str], env: dict[str, str],
          cap: int = 180, *, cwd: Path | None = None,
          stdin: Path | None = None, stdout: Path | None = None) -> dict:
    root.mkdir(parents=True, exist_ok=True)
    seconds = min(cap, a.deadline_epoch - int(time.time()) - 30)
    row = {"argv": argv, "cwd": str(cwd or root), "timeout_seconds": max(seconds, 0),
           "proof_verdict": None, "classification": "NOT_RUN_DEADLINE"}
    save(root / f"{name}-stage.json", row)
    if seconds <= 0:
        return row
    log_path = root / f"{name}.log"
    resource = root / f"{name}-resources.txt"
    with log_path.open("wb") as log:
        inp = stdin.open("rb") if stdin else subprocess.DEVNULL
        out = stdout.open("wb") if stdout else log
        try:
            code = subprocess.run(
                ["/usr/bin/time", "-v", "-o", str(resource), "timeout",
                 "--signal=TERM", "--kill-after=10s", f"{seconds}s", *argv],
                cwd=cwd or root, env={**env, "PWD": str(cwd or root)},
                stdin=inp, stdout=out, stderr=log, check=False).returncode
        finally:
            if stdin:
                inp.close()
            if stdout:
                out.close()
    row.update(exit=code, classification="TERMINAL", log_sha256=sha(log_path),
               resources=resource.name,
               stdout_sha256=sha(stdout) if stdout and stdout.is_file() else None)
    save(root / f"{name}-stage.json", row)
    save(a.evidence / "stage-progress.json", {"case": root.name, "stage": name,
                                              "exit": code, "proof_verdict": None})
    return row


def clean_env(a, tool: Path) -> dict[str, str]:
    env = {key: value for key, value in os.environ.items()
           if not key.startswith(("SORT4_", "O26_WITH_"))}
    deps = a.work_root / "vfdeps-adf88dc"
    need(all((deps / part).is_dir() for part in ("bin", "include", "lib")),
         "frozen vfdeps are missing")
    env.update(PATH=f"{tool / 'bin'}:{deps / 'bin'}:{env.get('PATH', '')}",
               LD_LIBRARY_PATH=f"{a.compiler_sysroot / 'lib'}:{tool / 'bin'}:{deps / 'lib'}",
               CAPNP_INC_DIR=str(deps / "include"),
               RUSTUP_TOOLCHAIN="nightly-2026-09-25",
               SMALLSORT_CLOUD_PROVIDER_PATH=str(a.cloud_dir / "provider.py"))
    return env


def build_frozen_c4(a, historical, env: dict[str, str]) -> tuple[Path, dict]:
    base, _, before = historical.setup(a, env)
    need(before["critical"][str(KERNEL)] == FINAL_KERNEL,
         "strict base kernel differs from frozen C4")
    tool = a.work_root / "sort4-native-c4-isolated-source"
    need(not tool.exists(), "isolated C4 tool already exists")
    shutil.copytree(base, tool, symlinks=True)
    need(historical.snapshot(a, tool) == before, "isolated tool copy differs")
    patch_rows = []
    for index, (manifest_rel, pin, patch_rel, base_pin, after_pin) in enumerate(PATCHES):
        manifest_path = a.proof_root / "research/challenge-8" / manifest_rel
        patch = a.proof_root / "research/challenge-8" / patch_rel
        manifest = json.loads(manifest_path.read_text())
        need(sha(patch) == field(manifest, pin), f"patch pin differs: {patch_rel}")
        headers = [line for line in patch.read_text().splitlines()
                   if line.startswith(("--- ", "+++ "))]
        need(headers == [f"--- a/{TRANSLATOR}", f"+++ b/{TRANSLATOR}"],
             f"non-translator patch refused: {patch_rel}")
        prior = sha(tool / TRANSLATOR)
        if base_pin:
            need(prior == field(manifest, base_pin),
                 f"base translator pin differs: {patch_rel}")
        check = stage(a, a.evidence / "tool", f"patch-{index}-check",
                      ["git", "-C", str(tool), "apply", "--check", str(patch)], env,
                      60, cwd=tool)
        need(check.get("exit") == 0, f"patch check failed: {patch_rel}")
        applied = stage(a, a.evidence / "tool", f"patch-{index}-apply",
                        ["git", "-C", str(tool), "apply", str(patch)], env,
                        60, cwd=tool)
        need(applied.get("exit") == 0, f"patch apply failed: {patch_rel}")
        after = sha(tool / TRANSLATOR)
        if after_pin:
            need(after == field(manifest, after_pin),
                 f"result translator pin differs: {patch_rel}")
        patch_rows.append({"patch": patch_rel, "sha256": sha(patch),
                           "before_translator_sha256": prior,
                           "after_translator_sha256": after})
    need(sha(tool / TRANSLATOR) == FINAL_TRANSLATOR, "final C4 translator differs")
    need(sha(tool / KERNEL) == FINAL_KERNEL, "frozen C4 kernel changed")
    save(a.evidence / "patch-chain.json", patch_rows)
    (tool / "bin/verifast").unlink(missing_ok=True)
    active = clean_env(a, tool)
    built = stage(a, a.evidence / "tool", "final-console-build",
                  ["make", "-C", str(tool / "src"), "../bin/verifast",
                   "WITHOUT_LABLGTK=yes", "VERBOSE=yes"], active, 900, cwd=tool)
    need(built.get("exit") == 0, "final C4 console build failed")
    after = historical.snapshot(a, tool)
    frozen_file = a.proof_root / FROZEN_HERE / "FROZEN-C4-SNAPSHOT.json"
    expected = json.loads(frozen_file.read_text())
    need(after["head"] == before["head"] and
         after["critical"][str(TRANSLATOR)] == FINAL_TRANSLATOR and
         after["critical"][str(KERNEL)] == FINAL_KERNEL and
         all(after["critical"][key] == value for key, value in before["critical"].items()
             if key != str(TRANSLATOR)) and
         after["effective_rsspec"] == before["effective_rsspec"] and
         after["proof_std"] == before["proof_std"] and
         set(after["modified_names"]) == set(before["modified_names"]) and
         all(after["binaries"][key] == value for key, value in before["binaries"].items()
             if key != "bin/verifast"), "C4 build changed frozen non-translator inputs")
    need(all(after.get(key) == expected.get(key) for key in
             ("head", "critical", "effective_rsspec", "proof_std")) and
         after["modified_hashes"] == expected["modified_hashes"] and
         after["modified_names"] == expected["modified_names"] and
         after["tracked_diff_sha256"] == expected["tracked_diff_sha256"] and
         all(after["binaries"][key] == value
             for key, value in expected["binaries"].items() if key != "bin/verifast"),
         "fresh C4 effective tool snapshot differs from pinned reviewed C4")
    save(a.evidence / "frozen-tool-identity.json", {
        "expected_snapshot_sha256": sha(frozen_file),
        "expected_console_sha256": expected["binaries"]["bin/verifast"],
        "fresh_console_sha256": after["binaries"]["bin/verifast"],
        "fresh_console_used_for_all_cases": True,
        "frozen_source_and_non_console_binaries_match": True,
        "accepted": False})
    save(a.evidence / "frozen-tool-snapshot.json", after)
    return tool, before


def prepare_c4(a, historical, env: dict[str, str]) -> Path:
    baseline = historical.baseline(a, clean_env(a, a.production_source))
    c2 = load(a.cloud_dir / "sort4-native-entry-c1/c2_discovery.py", "native_c4_c2")
    c3 = load(a.cloud_dir / "sort4-c3-bound-prefix/driver.py", "native_c4_c3")
    c4 = load(a.cloud_dir / "sort4-c4-bound-prefix/driver.py", "native_c4_c4")
    pin = json.loads((a.proof_root / c2.PIN).read_text())
    draft = (a.proof_root / c2.DRAFT).read_bytes()
    c2_fixture = a.evidence / "c2-discovery-fixture"
    shutil.copytree(baseline, c2_fixture, symlinks=True)
    verified = c2_fixture / "verified/lib.rs"
    source, cert = c2.prepare_c2_bytes(verified.read_bytes(),
                                      (c2_fixture / "original/lib.rs").read_bytes(),
                                      draft, pin)
    verified.write_bytes(source)
    save(a.evidence / "c2-source-certificate.json", cert)
    c3.prepare(a)
    fixture, c4_cert = c4.prepare(a)
    profile = json.loads((a.proof_root / ROOT / "sort4-c4-bound-prefix/profile.json").read_text())
    need(sha(fixture / "verified/lib.rs") == FINAL_SOURCE == profile["source_sha256"] and
         c4_cert["ghost_strip_byte_identical"] is True,
         "fresh exact C4 source correspondence differs")
    return fixture


def first_failure(root: Path, stages: dict[str, dict], name: str = "verification") -> dict:
    order = ("normal-export", "normal-decode", "readonly-export", "readonly-decode",
             "refinement", name)
    first_stage = next((key for key in order if stages.get(key, {}).get("exit") != 0), None)
    log = root / f"{first_stage}.log" if first_stage else root / f"{name}.log"
    raw = log.read_text(errors="replace") if log.is_file() else ""
    errors = [line for line in raw.splitlines()
              if ": error:" in line or line.startswith(("Fatal error:", "error:", "error["))]
    return {"first_causal_stage": first_stage or "NONE_OBSERVED",
            "first_error": errors[0] if errors else None,
            "first_stage_log_sha256": sha(log) if log.is_file() else None,
            "verifier_exit": stages.get(name, {}).get("exit"),
            "collector_pass_is_proof": False}


def source_support(a, tool: Path, fixture: Path, root: Path,
                   env: dict[str, str], *, target: str) -> tuple[dict, dict]:
    root.mkdir(parents=True, exist_ok=True)
    schema = tool / "src/rust_frontend/vf_mir/vf_mir.capnp"
    original = {name: sha(fixture / name)
                for name in ("verified/lib.rs", "original/lib.rs")}
    rows = {}
    capture = load(a.proof_root / "research/challenge-8/overnight-sort4/capture.py",
                   "native_c4_graph")
    mir = {}
    for mode in ("normal", "readonly"):
        argv = [str(tool / "bin/vf-rust-mir-exporter"), "verified/lib.rs",
                "--sysroot=" + str(a.compiler_sysroot), "--edition", "2021"]
        if mode == "readonly":
            argv.append("--vf-rust-mir-exporter:preprocess-readonly")
        binary = root / f"{mode}-mir.bin"
        decoded = root / f"{mode}-mir.txt"
        rows[f"{mode}-export"] = stage(a, root, f"{mode}-export", argv, env,
                                       100, cwd=fixture, stdout=binary)
        if rows[f"{mode}-export"].get("exit") == 0:
            rows[f"{mode}-decode"] = stage(a, root, f"{mode}-decode",
                                           ["capnp", "decode", str(schema), "VfMir"],
                                           env, 60, cwd=fixture, stdin=binary,
                                           stdout=decoded)
            if rows[f"{mode}-decode"].get("exit") == 0:
                try:
                    defpath, record = capture.complete_function_record(
                        decoded.read_text(errors="replace"), target)
                    path = root / f"{mode}-{target}-full-mir.txt"
                    path.write_text(record)
                    mir[mode] = {"defpath": defpath, "sha256": sha(path),
                                 "bytes": path.stat().st_size}
                except Exception as exc:
                    mir[mode] = {"capture_error": str(exc), "proof_credit": False}
    rows["refinement"] = stage(a, root, "refinement",
                               [str(tool / "bin/refinement-checker"), "--rustc-args",
                                "--edition 2021", "original/lib.rs", "verified/lib.rs"],
                               env, 120, cwd=fixture)
    paired = all(rows.get(key, {}).get("exit") == 0 for key in
                 ("normal-export", "normal-decode", "readonly-export",
                  "readonly-decode", "refinement"))
    paired = paired and all(mode in mir and "sha256" in mir[mode]
                            for mode in ("normal", "readonly"))
    paired = paired and original == {name: sha(fixture / name) for name in original}
    support = {"paired_support_passed": paired, "source_pair_sha256": original,
               "full_mir": mir, "target": target, "proof_credit": False}
    save(root / "source-support.json", support)
    return rows, support


def verify_case(a, tool: Path, fixture: Path, root: Path,
                env: dict[str, str], *, target: str, ast: bool = True) -> dict:
    input_sha = {name: sha(fixture / name)
                 for name in ("verified/lib.rs", "original/lib.rs")}
    rows, support = source_support(a, tool, fixture, root, env, target=target)
    command = [str(tool / "bin/verifast"), "-rustc_args", "--edition 2021",
               "-verbose", "2", "verified/lib.rs"]
    if ast:
        rows["proof-ast-diagnostic"] = stage(a, root, "proof-ast-diagnostic",
                                             [str(tool / "bin/verifast"),
                                              "-dump_ast_with_locs", "proof-ast.ml",
                                              "-rustc_args", "--edition 2021",
                                              "verified/lib.rs"], env, 90, cwd=fixture)
        ast_path = fixture / "proof-ast.ml"
        if ast_path.is_file():
            shutil.copy2(ast_path, root / "proof-ast.ml")
    rows["verification"] = stage(a, root, "verification", command, env,
                                  240, cwd=fixture)
    result = {"accepted": False, "actual_sort4_proved": False,
              "callable_summary": False, "support": support,
              "stages": {name: row.get("exit") for name, row in rows.items()},
              **first_failure(root, rows)}
    result["source_pair_immutable"] = input_sha == {
        name: sha(fixture / name) for name in input_sha}
    result["proof_ast_sha256"] = sha(root / "proof-ast.ml") if (
        root / "proof-ast.ml").is_file() else None
    result["classification"] = ("FRESH_FULL_VF0_CANDIDATE_RAW_REVIEW_REQUIRED"
                                if support["paired_support_passed"] and
                                rows["verification"].get("exit") == 0 and
                                result["first_causal_stage"] == "NONE_OBSERVED" and
                                result["source_pair_immutable"] else
                                "FIRST_CAUSAL_STAGE_DIAGNOSTIC")
    save(root / "case-result.json", result)
    return result


def verify_c4_reuse_support(a, tool: Path, fixture: Path, root: Path,
                            env: dict[str, str], support: dict) -> dict:
    """Controls share an immutable source pair and the fresh paired C4 capture."""
    before = {name: sha(fixture / name)
              for name in ("verified/lib.rs", "original/lib.rs")}
    need(before == support["source_pair_sha256"], "C4 control source differs")
    row = stage(a, root, "verification",
                [str(tool / "bin/verifast"), "-rustc_args", "--edition 2021",
                 "-verbose", "2", "verified/lib.rs"], env, 240, cwd=fixture)
    log = (root / "verification.log").read_text(errors="replace")
    errors = [line for line in log.splitlines()
              if ": error:" in line or line.startswith(("Fatal error:", "error:", "error["))]
    entries = list(re.finditer(
        r"(?m)^\s*\d+(?:\.\d+)?s: .*: Verifying function 'sort4_stable'", log))
    first = errors[0] if errors else None
    result = {"classification": "C4_CONTROL_RAW_OUTCOME_RECORDED",
              "accepted": False, "proof_credit": False,
              "source_pair_sha256": before,
              "source_pair_immutable": before == {name: sha(fixture / name)
                                                  for name in before},
              "reused_fresh_support": support["paired_support_passed"],
              "full_mir_support_sha256": {key: value["sha256"]
                                          for key, value in support["full_mir"].items()},
              "verifier_exit": row.get("exit"),
              "first_causal_stage": "verification" if row.get("exit") != 0 else
                                    "NONE_OBSERVED",
              "first_error": first, "first_error_after_target_entry":
                  len(entries) == 1 and first is not None and
                  entries[0].start() < log.find(first),
              "target_entry_count": len(entries),
              "not_callable_summary_marker": "NOT_CALLABLE_SUMMARY" in log,
              "return_seen": "Executing return statement" in log,
              "leak_seen": "Leak check." in log,
              "pre_ast_sha256": sha(root / "actual-c4-bound-pre-ast.ml") if
                  (root / "actual-c4-bound-pre-ast.ml").is_file() else None,
              "post_ast_sha256": sha(root / "actual-c4-bound-post-ast.ml") if
                  (root / "actual-c4-bound-post-ast.ml").is_file() else None,
              "full_log_sha256": sha(root / "verification.log")}
    result["candidate_full_vf0"] = (
        row.get("exit") == 0 and not errors and len(entries) == 1 and
        result["not_callable_summary_marker"] and result["return_seen"] and
        result["leak_seen"] and "0 errors found (" in log and
        result["source_pair_immutable"])
    if result["candidate_full_vf0"]:
        result["classification"] = "FRESH_C4_VF0_CANDIDATE_RAW_REVIEW_REQUIRED"
    save(root / "case-result.json", result)
    return result


def c4_cases(a, tool: Path, fixture: Path, env: dict[str, str]) -> dict:
    profile = json.loads((a.proof_root / ROOT / "sort4-c4-bound-prefix/profile.json").read_text())
    capture_profile = json.loads((a.proof_root / ROOT / "sort4-c4-bound-prefix/capture-profile.json").read_text())
    active = env.copy()
    active.update({key: "0" for key in DISABLED_C_SCOPES})
    active.update(SORT4_ACTUAL_AST_SCOPE_TEST="1", SORT4_STRICT_LFT_CUT="1",
                  SORT4_C1_OUTPUT_EQ="0", SORT4_C1_PREFIX_CONTROL="none",
                  SORT4_C2_BOUND_CONTROL="none", SORT4_C3_BOUND_CONTROL="none",
                  SORT4_C4_BOUND_CONTROL="none")
    root = a.evidence / "c4"
    rows, support = source_support(a, tool, fixture, root, active, target="sort4_stable")
    need(support["paired_support_passed"], "exact C4 source/MIR/refinement support failed")
    for mode in ("normal", "readonly"):
        expected = profile[f"{mode}_full_mir_sha256"]
        need(support["full_mir"][mode]["sha256"] == expected,
             f"C4 {mode} full MIR pin differs")
    capture_env = active.copy()
    capture_env.update(SORT4_ACTUAL_C4_CAPTURE_TEST="1",
                       SORT4_C4_CAPTURE_SOURCE_SHA256=FINAL_SOURCE)
    capture = stage(a, root, "c4-pre-ast-capture",
                    [str(tool / "bin/verifast"), "-rustc_args", "--edition 2021",
                     "-verbose", "2", "verified/lib.rs"], capture_env, 180,
                    cwd=fixture)
    ast = fixture / capture_profile["pre_ast"]
    raw = (root / "c4-pre-ast-capture.log").read_text(errors="replace")
    need(capture.get("exit") in (1, 2) and
         capture_profile["expected_refusal"] in raw and
         ast.is_file() and sha(ast) == FINAL_PRE_AST == profile["pre_ast_sha256"],
         "fresh exact C4 pre-AST capture/refusal differs")
    shutil.copy2(ast, root / ast.name)
    active["SORT4_ACTUAL_C4_BOUND_PREFIX_TEST"] = "1"
    positive = a.evidence / "c4-positive"
    shutil.copytree(fixture, positive, symlinks=True)
    result = {"positive": verify_c4_reuse_support(a, tool, positive, positive,
                                                   active, support),
              "controls": {}, "accepted": False,
              "callable_summary": "NOT_CALLABLE_SUMMARY"}
    for control in CONTROLS:
        case = a.evidence / "c4-controls" / control
        shutil.copytree(fixture, case, symlinks=True)
        case_env = active.copy()
        case_env["SORT4_C4_BOUND_CONTROL"] = control
        result["controls"][control] = verify_c4_reuse_support(
            a, tool, case, case, case_env, support)
        save(a.evidence / "c4-results.json", result)
    return result


def native_cases(a, tool: Path, env: dict[str, str]) -> dict:
    prep = load(a.proof_root / "research/challenge-8/caller-entry/prepare.py",
                "native_c4_caller_prepare")
    active = env.copy()
    active.update({key: "0" for key in DISABLED_C_SCOPES})
    active.update(SORT4_ACTUAL_AST_SCOPE_TEST="0", SORT4_STRICT_LFT_CUT="1",
                  SORT4_C1_OUTPUT_EQ="0", SORT4_C1_PREFIX_CONTROL="none",
                  SORT4_C2_BOUND_CONTROL="none", SORT4_C3_BOUND_CONTROL="none",
                  SORT4_C4_BOUND_CONTROL="none")
    results = {}
    for name in NATIVE:
        root = a.evidence / "native" / name
        root.mkdir(parents=True)
        fixture = root / "fixture"
        try:
            cert = prep.prepare(a.proof_root, fixture, name)
            save(root / "source-certificate.json", cert)
            results[name] = verify_case(a, tool, fixture, root, active,
                                        target="small_sort_general_with_scratch")
        except Exception as exc:
            results[name] = {"classification": "NATIVE_CASE_SETUP_OR_COLLECTOR_ERROR",
                             "first_causal_stage": "COLLECTOR", "reason": str(exc),
                             "raw_preserved": True, "proof_credit": False}
        results[name]["actual_caller_proved"] = False
        save(root / "case-result.json", results[name])
    save(a.evidence / "native-results.json", results)
    return results


def supplied_cases(a, tool: Path, env: dict[str, str]) -> dict:
    """Run complete, isolated user supplied source units; preserve every failure."""
    profile = json.loads((a.proof_root / HERE / "profile.json").read_text())
    case_file = profile.get("case_file", "cases.rs")
    need(case_file in ("cases.rs", "followup-cases.rs"), "case file is not an exact phase input")
    source_file = a.proof_root / HERE / case_file
    if not source_file.is_file():
        return {"classification": "NOT_SUPPLIED", "cases": {}}
    text = source_file.read_text()
    blocks = re.findall(
        r"(?ms)^// CASE_BEGIN ([a-z][a-z0-9-]*)\n(.*?)^// CASE_END \1\s*$",
        text)
    need(blocks and len(blocks) == text.count("// CASE_BEGIN") ==
         text.count("// CASE_END") and len({name for name, _ in blocks}) == len(blocks),
         "ambiguous supplied case boundaries")
    if profile.get("run_mode") == "FROZEN_C4_INDEPENDENT_FOLLOWUP":
        need([name for name, _ in blocks] == profile.get("followup_cases"),
             "follow-up cases differ from exact profile")
        excerpt_file = a.proof_root / FROZEN_HERE / "SLICE-EXPRESSION-SOURCE.json"
        excerpt = json.loads(excerpt_file.read_text())
        need(excerpt.get("source_path") == "library/core/src/slice/mod.rs" and
             excerpt.get("source_git_blob") == "16b5766ba08362bbf6ab13e127d71c7d920eccf7" and
             excerpt.get("source_excerpt_sha256") == "1cdcbe5e0573f8b70e8d9a7d861d1e86533710fb3e18b9a4fde8303c07e2922b" and
             excerpt.get("source_excerpt") == "pub const fn as_mut_ptr(&mut self) -> *mut T {\n        self as *mut [T] as *mut T\n    }",
             "reviewed primitive expression excerpt differs")
        tree_entry = subprocess.check_output(
            ["git", "-C", str(a.proof_root), "ls-tree", "HEAD", excerpt["source_path"]],
            env=env, text=True).split()
        need(tree_entry[:3] == ["100644", "blob", excerpt["source_git_blob"]],
             "proof tree primitive implementation blob differs")
        save(a.evidence / "slice-expression-source-correspondence.json", {
            "metadata_sha256": sha(excerpt_file), "source_tree_blob_checked": True,
            "full_source_blob_transported": False, "correspondence": excerpt,
            "method_call_binding_proved": False, "actual_callee_summary_admitted": False,
            "scope": "Reviewed implementation-expression component only"})
    ghost = load(a.cloud_dir / "sort4-native-entry-c1/c2_discovery.py",
                 "native_c4_ghost_strip")
    active = env.copy()
    active.update({key: "0" for key in DISABLED_C_SCOPES})
    active.update(SORT4_ACTUAL_AST_SCOPE_TEST="0", SORT4_STRICT_LFT_CUT="1",
                  SORT4_C1_OUTPUT_EQ="0", SORT4_C1_PREFIX_CONTROL="none",
                  SORT4_C2_BOUND_CONTROL="none", SORT4_C3_BOUND_CONTROL="none",
                  SORT4_C4_BOUND_CONTROL="none")
    results = {}
    for name, unit in blocks:
        root = a.evidence / "supplied" / name
        fixture = root / "fixture"
        (fixture / "verified").mkdir(parents=True)
        (fixture / "original").mkdir()
        verified = unit.encode()
        if not verified.endswith(b"\n"):
            verified += b"\n"
        original = ghost.strip_ghost(verified)
        (fixture / "verified/lib.rs").write_bytes(verified)
        (fixture / "original/lib.rs").write_bytes(original)
        names = re.findall(r"\b(?:pub\s+)?(?:unsafe\s+)?fn\s+([A-Za-z_][A-Za-z_0-9]*)\s*[(<]",
                           unit)
        target = ("small_sort_general_with_scratch"
                  if "small_sort_general_with_scratch" in names else
                  next((symbol for symbol in names if symbol.startswith(("native_", "case_"))),
                       names[-1] if names else "__no_function__"))
        save(root / "source-certificate.json", {
            "case": name, "case_block_source_sha256": sha(source_file),
            "verified_sha256": sha(fixture / "verified/lib.rs"),
            "original_sha256": sha(fixture / "original/lib.rs"),
            "ghost_strip_byte_identical": True, "target": target,
            "actual_sort4_summary_used": False, "accepted": False})
        # Diagnostic compiler capture only. The stock exporter appends
        # overflow_checks=off; preserve an independent checked MIR route.
        checked_capture = None
        if OPAQUE_SESSION and name == "checked-add-overflow-reproducer":
            compiler = a.compiler_sysroot / "bin/rustc"
            need(compiler.is_file(), "pinned compiler missing for checked MIR capture")
            checked_mir = root / "rustc-overflow-checks-on.mir"
            checked_row = stage(a, root, "rustc-checked-mir-capture",
                [str(compiler), "--sysroot=" + str(a.compiler_sysroot),
                 "--edition=2021", "--crate-type=lib", "--emit=mir",
                 "-C", "overflow-checks=on", "-C", "panic=unwind",
                 "-C", "opt-level=0", "-Z", "mir-opt-level=0",
                 "verified/lib.rs", "-o", str(checked_mir)], active,
                100, cwd=fixture)
            checked_capture = {"exit": checked_row.get("exit"),
                "source_sha256": sha(fixture / "verified/lib.rs"),
                "mir_sha256": sha(checked_mir) if checked_mir.is_file() else None,
                "compiler_sha256": sha(compiler),
                "diagnostic_only": True, "proof_credit": False,
                "exporter_default_overflow_checks": "off_unconditionally_appended"}
            save(root / "checked-mir-capture.json", checked_capture)
        try:
            result = verify_case(a, tool, fixture, root, active, target=target)
        except Exception as exc:
            result = {"classification": "SUPPLIED_CASE_SETUP_OR_COLLECTOR_ERROR",
                      "first_causal_stage": "COLLECTOR", "reason": str(exc),
                      "raw_preserved": True, "proof_credit": False}
            save(root / "case-result.json", result)
        if checked_capture is not None:
            result["checked_mir_diagnostic"] = checked_capture
            save(root / "case-result.json", result)
        results[name] = result
        save(a.evidence / "supplied-results.json", results)
    return {"classification": "SUPPLIED_CASES_RECORDED", "cases": results,
            "proof_credit": False}


def admission_classification(raw: str, verifier_exit: int | None) -> str:
    """Pure saved-data classifier; these are pre-target admission refusals only."""
    if verifier_exit not in (1, 2) or "Verifying function 'sort4_stable'" in raw:
        return "ADMISSION_REFUSAL_INCONCLUSIVE"
    if 'Failure("SORT4-C4-BOUND: isolated exact-one body, unwind/full checks required")' in raw:
        return "EXTRA_RUNTIME_BODY_EXACT_ONE_BODY_ADMISSION_REFUSAL"
    if 'Failure("SORT4-C4-BOUND: verified source SHA256 differs")' in raw:
        return "SOURCE_HASH_ADMISSION_REFUSAL"
    return "ADMISSION_REFUSAL_INCONCLUSIVE"


def refusal(a, tool: Path, fixture: Path, env: dict[str, str], *, comment_only: bool = False) -> dict:
    patch = a.proof_root / ROOT / "sort4-c4-bound-prefix/verifast-c4-bound-prefix-TEST.patch"
    patch_text = patch.read_text()
    hash_gate = 'failwith "SORT4-C4-BOUND: verified source SHA256 differs"'
    body_gate = 'failwith "SORT4-C4-BOUND: isolated exact-one body, unwind/full checks required"'
    need(hash_gate in patch_text and body_gate in patch_text,
         "frozen C4 source/body admission guards absent")
    root = a.evidence / ("admission-comment-only" if comment_only else "admission-extra-runtime-body")
    shutil.copytree(fixture, root, symlinks=True)
    addition = (b"\n// frozen source fingerprint mutation diagnostic\n" if comment_only else
                b"\nfn __vf_unrelated_runtime_body() {}\n")
    for name in ("verified/lib.rs", "original/lib.rs"):
        path = root / name
        path.write_bytes(path.read_bytes() + addition)
    active = env.copy()
    active.update({key: "0" for key in DISABLED_C_SCOPES})
    active.update(SORT4_ACTUAL_AST_SCOPE_TEST="1", SORT4_STRICT_LFT_CUT="1",
                  SORT4_ACTUAL_C4_BOUND_PREFIX_TEST="1",
                  SORT4_C1_OUTPUT_EQ="0", SORT4_C1_PREFIX_CONTROL="none",
                  SORT4_C2_BOUND_CONTROL="none", SORT4_C3_BOUND_CONTROL="none",
                  SORT4_C4_BOUND_CONTROL="none")
    result = verify_case(a, tool, root, root, active, target="sort4_stable", ast=False)
    raw = (root / "verification.log").read_text(errors="replace")
    classification = admission_classification(raw, result["verifier_exit"])
    result.update(classification=classification,
                  mutation="comment-only" if comment_only else "extra-runtime-body",
                  added_runtime_body=None if comment_only else "__vf_unrelated_runtime_body",
                  exact_one_runtime_body_guard_reached=classification == "EXTRA_RUNTIME_BODY_EXACT_ONE_BODY_ADMISSION_REFUSAL",
                  exact_one_runtime_body_guard_static=True,
                  c4_bound_patch_sha256=sha(patch),
                  guard_order="Observed first refusal only; lexical patch order does not determine execution order",
                  semantic_negative=False, proof_credit=False)
    save(root / "case-result.json", result)
    return result


def run(a) -> None:
    need(os.environ.get("SMALLSORT_EXECUTION_PROVIDER") == "cloud-build" and
         os.environ.get("LANE") == "o26-sort4-c1-current-recovery" and
         ((OPAQUE_SESSION and
           os.environ.get("SORT4_NATIVE_OPAQUE_PHASE_ID") == PHASE and
           os.environ.get("SORT4_NATIVE_C4_PHASE") is None) or
          (not OPAQUE_SESSION and os.environ.get("SORT4_NATIVE_C4_PHASE") == "1" and
           os.environ.get("SORT4_NATIVE_C4_PHASE_ID") == PHASE)) and
         not os.environ.get("GITHUB_ACTIONS"), "exact Cloud native-C4 phase required")
    for key in ("production_source", "production_applied_patch", "stock_home",
                "compiler_sysroot", "evidence", "proof_root", "work_root", "cloud_dir"):
        need(str(getattr(a, key)).startswith("/workspace/"), f"unsafe {key} path")
    profile_path = a.proof_root / HERE / "profile.json"
    profile = json.loads(profile_path.read_text())
    need(profile.get("cloud_enabled") is True and
         profile.get("profile_accepted") is False and
         profile.get("dispatch_authorized") is True and
         profile.get("run_mode") in ("FROZEN_C4_COMPATIBILITY_AND_RESOURCE_PREPARATION", "FROZEN_C4_INDEPENDENT_FOLLOWUP") and
         profile.get("tool_head") == "f76012fb518703b1d98e243ac4f487f16877cfcb",
         "native-C4 experimental profile is not Cloud-enabled")
    need(profile.get("phase_id") == PHASE and
         profile.get("frozen_translator_sha256") == FINAL_TRANSLATOR and
         profile.get("frozen_kernel_sha256") == FINAL_KERNEL and
         profile.get("frozen_snapshot_file") == "FROZEN-C4-SNAPSHOT.json" and
         profile.get("native_slice_alias_overlay") is False and
         profile.get("strict_cut_draft") is False and
         profile.get("native_cases") == list(NATIVE) and
         profile.get("c4_controls") == list(CONTROLS),
         "native-C4 profile differs from frozen final C4 pins")
    historical = load(a.cloud_dir / "sort4-c1-current-recovery.py", "native_c4_historical")
    env = clean_env(a, a.production_source)
    try:
        production_before = historical.snapshot(a, a.production_source)
        tool, before = build_frozen_c4(a, historical, env)
        save(a.evidence / "production-before.json", production_before)
        active = clean_env(a, tool)
        fixture = prepare_c4(a, historical, active)
        followup = profile["run_mode"] == "FROZEN_C4_INDEPENDENT_FOLLOWUP"
        if followup:
            need(profile.get("prior_fresh_c4_build") == "d5a0f8da-a2ed-416c-9eac-a9ffff926c87" and
                 profile.get("prior_fresh_c4_proof_infra") == "e12df71d57923d346ba0640b9bd0ea23d2835365",
                 "follow-up prior fresh C4 provenance differs")
            c4 = {"classification": "NOT_RUN_UNCHANGED_PRIOR_FRESH_PASS", "proof_credit": False,
                  "prior_build": profile["prior_fresh_c4_build"]}
            native = {"classification": "NOT_RUN_UNCHANGED_PRIOR_ALIAS_BLOCKER", "proof_credit": False}
        else:
            c4 = c4_cases(a, tool, fixture, active)
            native = native_cases(a, tool, active)
        supplied = supplied_cases(a, tool, active)
        reuse_admission = followup and profile.get("prior_fresh_admission_build") is not None
        if reuse_admission:
            need(profile.get("prior_fresh_admission_build") == "3584fb04-e237-4d66-9c85-60de4df059c4" and
                 profile.get("prior_fresh_admission_proof_infra") == "285220a384d050e046d1e8709b79a52bd602e675" and
                 profile.get("admission_cases") == [], "prior fresh admission provenance differs")
            admission = {"classification": "NOT_RUN_PRIOR_FRESH_EXACT_ONE_BODY_REFUSAL", "proof_credit": False,
                         "prior_build": profile["prior_fresh_admission_build"]}
            comment_admission = {"classification": "NOT_RUN_PRIOR_FRESH_SOURCE_HASH_REFUSAL", "proof_credit": False,
                                 "prior_build": profile["prior_fresh_admission_build"]}
        else:
            admission = refusal(a, tool, fixture, active)
            comment_admission = refusal(a, tool, fixture, active, comment_only=True) if followup else None
        components_complete = (
            bool(supplied.get("cases")) and
            all("verification" in value.get("stages", {}) and
                value.get("source_pair_immutable") is True
                for value in supplied.get("cases", {}).values()) and
            (reuse_admission or admission.get("classification") == "EXTRA_RUNTIME_BODY_EXACT_ONE_BODY_ADMISSION_REFUSAL"))
        complete = (components_complete and (reuse_admission or comment_admission.get("classification") ==
                    "SOURCE_HASH_ADMISSION_REFUSAL")) if followup else (
            c4["positive"].get("verifier_exit") == 0 and
            c4["positive"].get("reused_fresh_support") is True and
            len(c4["controls"]) == len(CONTROLS) and
            all("verifier_exit" in value for value in c4["controls"].values()) and
            len(native) == len(NATIVE) and
            all("verification" in value.get("stages", {}) and
                value.get("source_pair_immutable") is True
                for value in native.values()) and
            components_complete)
        result = {"classification": "NATIVE_ON_FROZEN_C4_DIAGNOSTICS_RECORDED",
                  "diagnostic_complete": complete,
                  "verification_accepted": False,
                  "phase": PHASE, "accepted": False, "actual_sort4_proved": False,
                  "actual_caller_proved": False, "callable_summary": False,
                  "frozen_translator_sha256": FINAL_TRANSLATOR,
                  "frozen_kernel_sha256": FINAL_KERNEL,
                  "c4": c4, "native": native, "supplied": supplied,
                  "admission": admission,
                  "comment_admission": comment_admission,
                  "run_mode": profile["run_mode"],
                  "collector_pass_is_proof": False}
        save(a.evidence / "diagnostic-audit.json", result)
        need(historical.snapshot(a, tool)["critical"][str(TRANSLATOR)] == FINAL_TRANSLATOR and
             historical.snapshot(a, tool)["critical"][str(KERNEL)] == FINAL_KERNEL and
             historical.snapshot(a, a.production_source) == production_before,
             "tool identities changed after diagnostics")
        print(json.dumps({"classification": result["classification"],
                          "native_first_stage": native if followup else {key: value["first_causal_stage"]
                                                 for key, value in native.items()},
                          "admission": admission["classification"]}), flush=True)
    except Exception as exc:
        if a.evidence.is_dir():
            save(a.evidence / "collector-error.json",
                 {"classification": "SETUP_OR_COLLECTOR_ERROR_NOT_PROOF_VERDICT",
                  "reason": str(exc), "raw_preserved": True})
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("production-source", "production-applied-patch", "stock-home",
                 "compiler-sysroot", "evidence", "proof-root", "work-root", "cloud-dir"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--deadline-epoch", type=int, required=True)
    run(parser.parse_args())


if __name__ == "__main__":
    main()
