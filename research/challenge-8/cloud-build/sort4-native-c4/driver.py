#!/usr/bin/env python3
"""Cloud-only native diagnostics with separately pinned capture-only extension.

Every case retains its raw source, paired MIR, refinement and full verifier log.
Collector completion is never a proof verdict. Only reviewed pinned deltas apply.
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
from types import SimpleNamespace


ROOT = Path("research/challenge-8/cloud-build")
FROZEN_HERE = ROOT / "sort4-native-c4"
OPAQUE_PHASE = "SORT4-NATIVE-OPAQUE-CLOUD-2026-10-10"
OPAQUE_SESSION = os.environ.get("SORT4_NATIVE_OPAQUE_PHASE") == "1"
C1_ZST_REPAIR_PHASE = "SORT4-NATIVE-C1-ZST-REPAIR-CLOUD-2026-10-11"
C1_ZST_REPAIR_SESSION = os.environ.get("SORT4_NATIVE_C1_ZST_REPAIR_PHASE") == "1"
HERE = ROOT / ("sort4-native-c1-bound" if C1_ZST_REPAIR_SESSION else
               "sort4-native-opaque" if OPAQUE_SESSION else "sort4-native-c4")
TRANSLATOR = Path("src/rust_frontend/vf_mir_translator/vf_mir_translator.ml")
KERNEL = Path("src/verifast.ml")
FINAL_TRANSLATOR = "1eab6eb54fe5c23d53ca72a6d9dfcbbff09c09ffaf26c48a4f450f5068a8d313"
FINAL_KERNEL = "37ed2550d276abccbbe0a9ced678137ef587f80782bcff763062df394c2a440c"
FINAL_SOURCE = "ba9e6ad3633004c3d934c590462443951ddd6dec80a5df9ffb687ec940958c6f"
FINAL_PRE_AST = "0ed31137cf55a2ed47ed624a6c61591e4aaf96371df3c2979fc10ce8d95bb222"
PHASE = (C1_ZST_REPAIR_PHASE if C1_ZST_REPAIR_SESSION else OPAQUE_PHASE if OPAQUE_SESSION
         else "SORT4-NATIVE-C4-CLOUD-2026-10-10")
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
BOUND_SOURCE = "7ebcf7cd435c31b3f4669ac6f31a62fd45fcb2c7fa03500bdfbc44ccaca01742"
BOUND_ORIGINAL = "7c35a7e01915233308d113b081f26784c4ad5aaf6f7049dc209d126e3eb326a1"
BOUND_NORMAL_MIR = "8e9adcccd136d3c1ee4dc1e7bd929c3cd60883f497178eab24da40f60754dee4"
BOUND_READONLY_MIR = "bde6d797d56e0e11e9837fc922f6def819c6931d1349f42c5b36d4570e2001aa"
BOUND_PRE_AST = "18973de5dd5ff1a9c94652fd808d42ffe2297096adb8a3cc1980f74a554ccea5"
BOUND_CASE_CONTROLS = {
    "native-c1-bound-positive": ("1", "none", "0"),
    "native-c1-bound-default-off": ("0", "none", "0"),
    "native-c1-bound-false-normal": ("1", "normal_false", "0"),
    "native-c1-bound-false-unwind": ("1", "unwind_false", "0"),
    "native-c1-bound-source-refusal": ("1", "none", "0"),
    "native-c1-bound-extra-body": ("1", "none", "0"),
    "native-c1-bound-malformed": ("bad", "none", "0"),
    "native-c1-bound-mixed": ("1", "none", "1"),
}


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
        "fresh_console_used_for_all_cases": not (
            OPAQUE_SESSION or C1_ZST_REPAIR_SESSION),
        "fresh_console_used_for_frozen_profile_cases": not (
            OPAQUE_SESSION or C1_ZST_REPAIR_SESSION),
        "frozen_source_and_non_console_binaries_match": True,
        "accepted": False})
    save(a.evidence / "frozen-tool-snapshot.json", after)
    return tool, before


def build_native_capture_tool(a, historical, base: Path, env: dict[str, str]) -> Path:
    """Separate source-pinned capture-only profile; never replace frozen C4."""
    profile_path = a.proof_root / HERE / "NATIVE-C1-CAPTURE-PROFILE.json"
    profile = json.loads(profile_path.read_text())
    need(OPAQUE_SESSION and profile.get("mode") == "CAPTURE_ONLY_ALWAYS_REFUSE" and
         profile.get("profile_accepted") is False and
         profile.get("base_translator_sha256") == FINAL_TRANSLATOR and
         profile.get("kernel_sha256") == FINAL_KERNEL,
         "native C1 capture profile differs")
    patch = a.proof_root / HERE / "native-c1-capture-only.patch"
    need(sha(patch) == profile["patch_sha256"] and
         [line for line in patch.read_text().splitlines()
          if line.startswith(("--- ", "+++ "))] ==
         [f"--- a/{TRANSLATOR}", f"+++ b/{TRANSLATOR}"],
         "native capture patch is not the pinned translator-only delta")
    before = historical.snapshot(a, base)
    tool = a.work_root / "sort4-native-opaque-c1-capture-source"
    need(not tool.exists(), "native capture isolated tool already exists")
    shutil.copytree(base, tool, symlinks=True)
    need(historical.snapshot(a, tool) == before, "native capture copy differs")
    root = a.evidence / "native-c1-capture-tool"
    for operation, argv in (("check", ["apply", "--check"]), ("apply", ["apply"])):
        row = stage(a, root, f"patch-{operation}",
                    ["git", "-C", str(tool), *argv, str(patch)], env, 60, cwd=tool)
        need(row.get("exit") == 0, f"native capture patch {operation} failed")
    need(sha(tool / TRANSLATOR) == profile["translator_sha256"] and
         sha(tool / KERNEL) == FINAL_KERNEL, "native capture source pin differs")
    (tool / "bin/verifast").unlink(missing_ok=True)
    row = stage(a, root, "console-build",
                ["make", "-C", str(tool / "src"), "../bin/verifast",
                 "WITHOUT_LABLGTK=yes", "VERBOSE=yes"], clean_env(a, tool), 600, cwd=tool)
    need(row.get("exit") == 0, "native capture console build failed")
    after = historical.snapshot(a, tool)
    need(after["head"] == before["head"] and
         after["critical"][str(TRANSLATOR)] == profile["translator_sha256"] and
         all(after["critical"][key] == value for key, value in before["critical"].items()
             if key != str(TRANSLATOR)) and
         all(after[key] == before[key] for key in ("effective_rsspec", "proof_std", "modified_names")) and
         all(after["binaries"][key] == value for key, value in before["binaries"].items()
             if key != "bin/verifast"), "native capture changed other frozen inputs")
    save(root / "effective-profile.json", {"profile": profile,
         "profile_sha256": sha(profile_path), "snapshot": after,
         "proof_credit": False, "mode": "CAPTURE_ONLY_ALWAYS_REFUSE"})
    return tool


def build_native_bound_tool(a, historical, base: Path, env: dict[str, str]) -> Path:
    """Build the pinned capture+bound chain plus dead-code identity diagnostics."""
    need(C1_ZST_REPAIR_SESSION, "native C1 ZST repair tool is outside its exact phase")
    capture_dir = a.proof_root / ROOT / "sort4-native-opaque"
    capture_profile_path = capture_dir / "NATIVE-C1-CAPTURE-PROFILE.json"
    capture = json.loads(capture_profile_path.read_text())
    bound_profile_path = a.proof_root / HERE / "NATIVE-C1-BOUND-TOOL-MANIFEST.json"
    bound = json.loads(bound_profile_path.read_text())
    need(capture.get("mode") == "CAPTURE_ONLY_ALWAYS_REFUSE" and
         capture.get("base_translator_sha256") == FINAL_TRANSLATOR and
         capture.get("translator_sha256") ==
         "86952a6ac4a61ac854d8a9886cff98ee143a0e75ccf8148fb84e07c0a14ce544" and
         capture.get("kernel_sha256") == FINAL_KERNEL and
         capture.get("verified_source_sha256") == BOUND_SOURCE and
         capture.get("original_source_sha256") == BOUND_ORIGINAL and
         capture.get("normal_full_mir_sha256") == BOUND_NORMAL_MIR and
         capture.get("readonly_full_mir_sha256") == BOUND_READONLY_MIR and
         capture.get("native_pre_ast_sha256") == BOUND_PRE_AST and
         bound.get("base_translator_sha256") == capture["translator_sha256"] and
         bound.get("translator_sha256") ==
         "381e80ebe9a789877ee9d0e860da386f7692f54879b39775e01267f0db6f53d6" and
         bound.get("patch_sha256") ==
         "eea19eda3723a0f60970df751c7600c326f98ad476d41f61e3f39442beb88693" and
         bound.get("kernel_sha256") == FINAL_KERNEL and
         bound.get("tool_head") == "f76012fb518703b1d98e243ac4f487f16877cfcb" and
         bound.get("profile_accepted") is False and
         set(bound) == {"tool_head", "base_translator_sha256", "translator_sha256",
                        "patch_sha256", "kernel_sha256", "profile_accepted"},
         "native C1 bound chain differs from reviewed frozen base")
    patches = (
        (capture_dir / "native-c1-capture-only.patch", capture, "capture"),
        (a.proof_root / HERE / "native-c1-bound.patch", bound, "bound"),
    )
    before = historical.snapshot(a, base)
    need(before["critical"][str(TRANSLATOR)] == FINAL_TRANSLATOR and
         before["critical"][str(KERNEL)] == FINAL_KERNEL,
         "native C1 bound base is not frozen C4")
    tool = a.work_root / "sort4-native-c1-bound-isolated-source"
    need(not tool.exists(), "native C1 bound isolated tool already exists")
    shutil.copytree(base, tool, symlinks=True)
    need(historical.snapshot(a, tool) == before,
         "native C1 bound copy differs from frozen C4")
    root = a.evidence / "native-c1-bound-tool"
    for patch, manifest, label in patches:
        need(sha(patch) == manifest["patch_sha256"] and
             [line for line in patch.read_text().splitlines()
              if line.startswith(("--- ", "+++ "))] ==
             [f"--- a/{TRANSLATOR}", f"+++ b/{TRANSLATOR}"] and
             sha(tool / TRANSLATOR) == manifest["base_translator_sha256"],
             f"native C1 {label} patch or base pin differs")
        for operation, argv in (("check", ["apply", "--check"]),
                                ("apply", ["apply"])):
            row = stage(a, root, f"{label}-patch-{operation}",
                        ["git", "-C", str(tool), *argv, str(patch)], env,
                        60, cwd=tool)
            need(row.get("exit") == 0, f"native C1 {label} patch {operation} failed")
        need(sha(tool / TRANSLATOR) == manifest["translator_sha256"] and
             sha(tool / KERNEL) == FINAL_KERNEL,
             f"native C1 {label} result pin differs")
    diagnostic_manifest_path = a.proof_root / HERE / "NATIVE-DEAD-CODE-IDENTITY-DIAGNOSTIC-MANIFEST.json"
    diagnostic_patch = a.proof_root / HERE / "native-dead-code-identity-diagnostic.patch"
    diagnostic = json.loads(diagnostic_manifest_path.read_text())
    diagnostic_files = diagnostic.get("files", {})
    need(diagnostic.get("tool_head") == "f76012fb518703b1d98e243ac4f487f16877cfcb" and
         diagnostic.get("mode") == "DIAGNOSTIC_ONLY_PRESERVE_DEAD_CODE_REFUSAL" and
         diagnostic.get("profile_accepted") is False and
         diagnostic.get("kernel_sha256") == FINAL_KERNEL and
         sha(diagnostic_patch) == diagnostic.get("patch_sha256") and
         set(diagnostic_files) == {"src/vfconsole/vfconsole.ml", "src/verify_expr.ml"} and
         [line for line in diagnostic_patch.read_text().splitlines()
          if line.startswith(("--- ", "+++ "))] == [
              "--- a/src/vfconsole/vfconsole.ml", "+++ b/src/vfconsole/vfconsole.ml",
              "--- a/src/verify_expr.ml", "+++ b/src/verify_expr.ml"],
         "dead-code identity diagnostic manifest or patch differs")
    for rel, pins in diagnostic_files.items():
        need(sha(tool / rel) == pins["base_sha256"],
             f"dead-code diagnostic base hash differs: {rel}")
    for operation, argv in (("check", ["apply", "--check"]), ("apply", ["apply"])):
        row = stage(a, root, f"dead-code-diagnostic-patch-{operation}",
                    ["git", "-C", str(tool), *argv, str(diagnostic_patch)], env,
                    60, cwd=tool)
        need(row.get("exit") == 0,
             f"dead-code diagnostic patch {operation} failed")
    for rel, pins in diagnostic_files.items():
        need(sha(tool / rel) == pins["result_sha256"],
             f"dead-code diagnostic result hash differs: {rel}")
    zst_manifest_path = a.proof_root / HERE / "ZST-REPAIR-TOOL-MANIFEST.json"
    zst_manifest = json.loads(zst_manifest_path.read_text())
    zst_patch = a.proof_root / HERE / "rust-zst-size.patch"
    zst_file_pins = zst_manifest.get("files", {})
    need(C1_ZST_REPAIR_SESSION and
         zst_manifest.get("mode") == "RUST_ZST_SIZE_EXPERIMENTAL" and
         zst_manifest.get("tool_head") == before["head"] and
         zst_manifest.get("kernel_sha256") == FINAL_KERNEL and
         zst_manifest.get("profile_accepted") is False and
         sha(zst_patch) == zst_manifest.get("patch_sha256") and
         set(zst_file_pins) == {"src/verifast1.ml"} and
         [line for line in zst_patch.read_text().splitlines()
          if line.startswith(("--- ", "+++ "))] == [
              "--- a/src/verifast1.ml", "+++ b/src/verifast1.ml"],
         "Rust ZST repair manifest or patch differs")
    zst_rel = "src/verifast1.ml"
    need(sha(tool / zst_rel) == zst_file_pins[zst_rel]["base_sha256"],
         "Rust ZST repair base hash differs")
    for operation, argv in (("check", ["apply", "--check"]), ("apply", ["apply"])):
        row = stage(a, root, f"zst-repair-patch-{operation}",
                    ["git", "-C", str(tool), *argv, str(zst_patch)], env,
                    60, cwd=tool)
        need(row.get("exit") == 0, f"Rust ZST repair patch {operation} failed")
    need(sha(tool / zst_rel) == zst_file_pins[zst_rel]["result_sha256"] and
         sha(tool / KERNEL) == FINAL_KERNEL,
         "Rust ZST repair result hash or kernel differs")
    (tool / "bin/verifast").unlink(missing_ok=True)
    row = stage(a, root, "console-build",
                ["make", "-C", str(tool / "src"), "../bin/verifast",
                 "WITHOUT_LABLGTK=yes", "VERBOSE=yes"], clean_env(a, tool),
                600, cwd=tool)
    need(row.get("exit") == 0, "native C1 bound console build failed")
    after = historical.snapshot(a, tool)
    permitted_modified_names = set(before["modified_names"]) | set(diagnostic_files) | {zst_rel}
    need(after["head"] == before["head"] and
         after["critical"][str(TRANSLATOR)] == bound["translator_sha256"] and
         all(after["critical"][key] == value
             for key, value in before["critical"].items()
             if key not in (str(TRANSLATOR), zst_rel)) and
         all(after[key] == before[key] for key in
             ("effective_rsspec", "proof_std")) and
         set(after["modified_names"]) == permitted_modified_names and
         all(after["binaries"][key] == value
             for key, value in before["binaries"].items()
             if key != "bin/verifast"),
        "native C1 ZST repair build changed frozen semantics or unexpected files")
    save(root / "effective-profile.json", {
        "capture_profile_sha256": sha(capture_profile_path),
        "bound_profile_sha256": sha(bound_profile_path),
        "diagnostic_manifest_sha256": sha(diagnostic_manifest_path),
        "diagnostic_patch_sha256": sha(diagnostic_patch),
        "capture_patch_sha256": sha(patches[0][0]),
        "bound_patch_sha256": sha(patches[1][0]),
        "diagnostic_files": diagnostic_files,
        "zst_repair_manifest_sha256": sha(zst_manifest_path),
        "zst_repair_patch_sha256": sha(zst_patch),
        "zst_repair_files": {zst_rel: {"base_sha256": zst_file_pins[zst_rel]["base_sha256"],
                                        "result_sha256": sha(tool / zst_rel)}},
        "effective_profile_sha256": {"translator": sha(tool / TRANSLATOR),
                                     "kernel": sha(tool / KERNEL),
                                     "verifast1": sha(tool / zst_rel),
                                     "console": sha(tool / "bin/verifast")},
        "mode": zst_manifest["mode"],
        "snapshot": after, "accepted": False,
        "frozen_c4_tool_unchanged": True})
    return tool


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
              if ": error:" in line or line.startswith(("Fatal error:", "error:", "error["))
              or re.fullmatch(r"verified/lib\.rs\(\d+,\d+(?:-\d+)?\): dead code", line)]
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
                env: dict[str, str], *, target: str, ast: bool = True,
                require_paired_support: bool = False,
                required_full_mir: tuple[str, str] | None = None,
                verbosity: int | None = None) -> dict:
    input_sha = {name: sha(fixture / name)
                 for name in ("verified/lib.rs", "original/lib.rs")}
    rows, support = source_support(a, tool, fixture, root, env, target=target)
    if require_paired_support:
        need(support["paired_support_passed"],
             "native C1 bound paired MIR/refinement pre-verifier gate failed")
    if required_full_mir is not None:
        need(support["full_mir"].get("normal", {}).get("sha256") ==
             required_full_mir[0] and
             support["full_mir"].get("readonly", {}).get("sha256") ==
             required_full_mir[1] and
             support["source_pair_sha256"] == input_sha,
             "native C1 bound exact normal/readonly MIR pre-verifier gate failed")
    if verbosity is None:
        verbosity = 4 if C1_ZST_REPAIR_SESSION else 2
    command = [str(tool / "bin/verifast"), "-rustc_args", "--edition 2021",
               "-verbose", str(verbosity), "verified/lib.rs"]
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


def native_zst_model_diagnostics(a, patched_tool: Path,
                                 env: dict[str, str]) -> dict:
    """Run compact source/refinement/verifier gates on the experimental tool."""
    ghost = load(a.cloud_dir / "sort4-native-entry-c1/c2_discovery.py",
                 "native_c4_zst_gate_ghost_strip")
    module = load(a.proof_root / HERE / "zst_model_gates.py", "native_c4_zst_gates")
    results = {}
    for name, gate in module.GATES.items():
        source = gate["source"]
        root = a.evidence / "zst-model" / name
        fixture = root / "fixture"
        (fixture / "verified").mkdir(parents=True, exist_ok=True)
        (fixture / "original").mkdir(exist_ok=True)
        verified = source.encode()
        original = ghost.strip_ghost(verified)
        (fixture / "verified/lib.rs").write_bytes(verified)
        (fixture / "original/lib.rs").write_bytes(original)
        save(root / "source-certificate.json", {
            "case": name, "target": gate["target"],
            "verified_sha256": sha(fixture / "verified/lib.rs"),
            "original_sha256": sha(fixture / "original/lib.rs"),
            "paired_source_generated_from_inline_constant": True,
            "gate_contract": "positive VF0" if gate["positive"] else
                             "negative at exact annotated assertion",
            "assertion": gate.get("assertion"), "proof_credit": False})
        try:
            result = verify_case(a, patched_tool, fixture, root, env,
                                 target=gate["target"], ast=True,
                                 require_paired_support=True, verbosity=6)
        except Exception as exc:
            result = {"classification": "ZST_MODEL_GATE_SETUP_OR_COLLECTOR_ERROR",
                      "first_causal_stage": "COLLECTOR", "reason": str(exc),
                      "source_pair_immutable": True, "proof_credit": False}
        log_path = root / "verification.log"
        log = log_path.read_text(errors="replace") if log_path.is_file() else ""
        expected_line = next((i for i, line in enumerate(source.splitlines(), 1)
                              if gate.get("assertion") and
                              "//@ assert " + gate["assertion"] + ";" in line), None)
        first_error = result.get("first_error") or ""
        locations = re.findall(r"verified/lib\.rs\((\d+),(\d+)(?:-\d+)?\)", first_error)
        intended = (expected_line is not None and gate.get("expected_error", "Cannot prove") in first_error and
                    any(int(line) == expected_line for line, _ in locations))
        if gate["positive"]:
            passed = (result.get("stages", {}).get("verification") == 0 and
                      result.get("support", {}).get("paired_support_passed") is True and
                      result.get("first_causal_stage") == "NONE_OBSERVED")
            classification = "POSITIVE_VF0" if passed else "POSITIVE_GATE_FAILED"
        else:
            passed = (result.get("stages", {}).get("verification") not in (None, 0) and
                      result.get("first_causal_stage") == "verification" and intended)
            classification = "INTENDED_ASSERTION_NEGATIVE" if passed else "NEGATIVE_WRONG_OR_INCONCLUSIVE"
        result.update(gate_passed=passed, gate_classification=classification,
                      expected_assertion_line=expected_line,
                      first_error_assertion_locations=locations,
                      intended_assertion_location_observed=intended,
                      diagnostic_only=True, proof_credit=False,
                      patched_console_sha256=sha(patched_tool / "bin/verifast"))
        save(root / "case-result.json", result)
        results[name] = result
    c_results = {}
    for name, source in module.C_CONTROLS.items():
        root = a.evidence / "zst-model" / name
        root.mkdir(parents=True, exist_ok=True)
        extension = ".cpp" if name.startswith("cpp") else ".c"
        fixture = root / (name + extension)
        fixture.write_text(source)
        row = stage(a, root, "verification",
                    [str(patched_tool / "bin/verifast"), "-c", "-verbose", "2", str(fixture)],
                    env, 120, cwd=a.proof_root)
        log = (root / "verification.log").read_text(errors="replace")
        errors = [line for line in log.splitlines() if ": error:" in line or
                  line.startswith(("Fatal error:", "error:", "error["))]
        c_results[name] = {"exit": row.get("exit"), "positive_size_control":
                           row.get("exit") == 0 and not errors,
                           "first_error": errors[0] if errors else None,
                           "source_sha256": sha(fixture), "source": str(fixture),
                           "proof_credit": False}
        save(root / "case-result.json", c_results[name])
    all_passed = all(row.get("gate_passed") for row in results.values()) and all(
        row.get("positive_size_control") for row in c_results.values())
    output = {"classification": "ZST_REPAIR_MODEL_GATES_PASS" if all_passed else
              "ZST_REPAIR_MODEL_GATES_FAILED",
              "tool_role": "ISOLATED_RUST_ZST_SIZE_EXPERIMENTAL_TOOL",
              "tool_hashes": {"translator": sha(patched_tool / TRANSLATOR),
                              "kernel": sha(patched_tool / KERNEL),
                              "verifast1": sha(patched_tool / "src/verifast1.ml"),
                              "console": sha(patched_tool / "bin/verifast")},
              "gate_source_sha256": sha(a.proof_root / HERE / "zst_model_gates.py"),
              "paired_support_required": True, "proof_credit": False,
              "gates_passed": all_passed, "cases": results,
              "c_cpp_controls": c_results}
    save(a.evidence / "zst-model-diagnostics.json", output)
    return output

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


def supplied_cases(a, tool: Path, env: dict[str, str],
                   capture_tool: Path | None = None,
                   bound_tool: Path | None = None) -> dict:
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
        if C1_ZST_REPAIR_SESSION:
            need(list(BOUND_CASE_CONTROLS) == profile["followup_cases"] and
                 bound_tool is not None,
                 "native C1 bound cases or isolated tool differ")
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
        case_tool = tool
        case_env = active.copy()
        capture_case = name in profile.get("native_c1_capture_cases", [])
        default_off_case = name in profile.get("native_c1_capture_default_off_cases", [])
        if capture_case or default_off_case:
            need(OPAQUE_SESSION and capture_tool is not None,
                 "exact native C1 capture tool is missing")
            case_tool = capture_tool
            case_env = {**active, **clean_env(a, case_tool)}
            case_env.update({key: value for key, value in active.items()
                             if key.startswith("SORT4_")})
            case_env["SORT4_NATIVE_OPAQUE_C1_CAPTURE"] = "1" if capture_case else "0"
        if C1_ZST_REPAIR_SESSION:
            need(bound_tool is not None, "native C1 bound tool is missing")
            case_tool = bound_tool
            case_env = {**active, **clean_env(a, case_tool)}
            case_env.update({key: value for key, value in active.items()
                             if key.startswith("SORT4_")})
            opt_in, control, c4_mixed = BOUND_CASE_CONTROLS[name]
            case_env.update(SORT4_NATIVE_OPAQUE_C1_BOUND=opt_in,
                            SORT4_NATIVE_OPAQUE_C1_BOUND_CONTROL=control,
                            SORT4_ACTUAL_C4_BOUND_PREFIX_TEST=c4_mixed)
        root = a.evidence / "supplied" / name
        fixture = root / "fixture"
        (fixture / "verified").mkdir(parents=True)
        (fixture / "original").mkdir()
        verified = unit.encode()
        if not verified.endswith(b"\n"):
            verified += b"\n"
        if C1_ZST_REPAIR_SESSION:
            expected = (BOUND_SOURCE if name not in
                        ("native-c1-bound-source-refusal", "native-c1-bound-extra-body")
                        else None)
            if expected is not None:
                need(hashlib.sha256(verified).hexdigest() == expected,
                     f"native C1 bound exact source differs: {name}")
            else:
                need(hashlib.sha256(verified).hexdigest() != BOUND_SOURCE,
                     f"native C1 bound refusal source did not mutate: {name}")
        original = ghost.strip_ghost(verified)
        if C1_ZST_REPAIR_SESSION and expected is not None:
            need(hashlib.sha256(original).hexdigest() == BOUND_ORIGINAL,
                 f"native C1 bound exact original source differs: {name}")
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
            result = verify_case(a, case_tool, fixture, root, case_env,
                                 target=target,
                                 ast=not (capture_case or C1_ZST_REPAIR_SESSION),
                                 require_paired_support=C1_ZST_REPAIR_SESSION,
                                 required_full_mir=(BOUND_NORMAL_MIR, BOUND_READONLY_MIR)
                                 if C1_ZST_REPAIR_SESSION and expected is not None else None)
        except Exception as exc:
            result = {"classification": "SUPPLIED_CASE_SETUP_OR_COLLECTOR_ERROR",
                      "first_causal_stage": "COLLECTOR", "reason": str(exc),
                      "raw_preserved": True, "proof_credit": False}
            save(root / "case-result.json", result)
        if checked_capture is not None:
            result["checked_mir_diagnostic"] = checked_capture
            save(root / "case-result.json", result)
        result["effective_tool"] = {"translator_sha256": sha(case_tool / TRANSLATOR),
            "kernel_sha256": sha(case_tool / KERNEL),
            "console_sha256": sha(case_tool / "bin/verifast"),
            "native_c1_capture_only": capture_case,
            "native_c1_capture_default_off": default_off_case,
            "native_c1_bound": C1_ZST_REPAIR_SESSION}
        if capture_case:
            captured = fixture / "native-c1-capture-pre-ast.ml"
            if captured.is_file():
                shutil.copy2(captured, root / captured.name)
            log = root / "verification.log"
            raw = log.read_text(errors="replace") if log.is_file() else ""
            result["native_capture_classification"] = native_capture_classification(
                raw, result.get("verifier_exit"), captured.is_file())
            result["native_pre_ast_sha256"] = sha(captured) if captured.is_file() else None
            result["accepted"] = False
            result["callable_summary"] = False
        if C1_ZST_REPAIR_SESSION:
            pre = fixture / "native-c1-bound-pre-ast.ml"
            post = fixture / "native-c1-bound-post-ast.ml"
            for artifact in (pre, post):
                if artifact.is_file():
                    shutil.copy2(artifact, root / artifact.name)
            log = root / "verification.log"
            raw = log.read_text(errors="replace") if log.is_file() else ""
            result["native_bound_classification"] = native_bound_classification(
                name, raw, result.get("verifier_exit"),
                pre.is_file(), post.is_file())
            result["native_bound_candidate_binding"] = (
                name == "native-c1-bound-positive" and
                result["native_bound_classification"] ==
                    "NATIVE_C1_BOUND_VF0_CANDIDATE_RAW_REVIEW_REQUIRED" and
                result.get("first_causal_stage") == "NONE_OBSERVED" and
                result.get("source_pair_immutable") is True and
                result.get("support", {}).get("paired_support_passed") is True and
                sha(fixture / "verified/lib.rs") == BOUND_SOURCE and
                sha(fixture / "original/lib.rs") == BOUND_ORIGINAL and
                result.get("support", {}).get("full_mir", {}).get(
                    "normal", {}).get("sha256") == BOUND_NORMAL_MIR and
                result.get("support", {}).get("full_mir", {}).get(
                    "readonly", {}).get("sha256") == BOUND_READONLY_MIR and
                "NATIVE-OPAQUE-C1-BOUND admitted" in raw and
                "control=none NOT_CALLABLE_SUMMARY" in raw and
                "Verifying function 'small_sort_general_with_scratch'" in raw and
                "0 errors found (" in raw)
            result["native_bound_candidate_scope"] = (
                "exact source-linked internal C1 bounded entry; raw review required; "
                "external SmallSort caller and callable summary not proved")
            result["native_bound_pre_ast_sha256"] = sha(pre) if pre.is_file() else None
            result["native_bound_post_ast_sha256"] = sha(post) if post.is_file() else None
            result["native_bound_controls"] = {
                "opt_in": opt_in, "control": control, "c4_mixed": c4_mixed}
            result["accepted"] = False
            result["callable_summary"] = False
        save(root / "case-result.json", result)
        results[name] = result
        save(a.evidence / "supplied-results.json", results)
    return {"classification": "SUPPLIED_CASES_RECORDED", "cases": results,
            "proof_credit": False}


def native_capture_classification(raw: str, verifier_exit: int | None, artifact: bool) -> str:
    if verifier_exit not in (1, 2) or "Verifying function 'small_sort_general_with_scratch'" in raw:
        return "NATIVE_CAPTURE_INCONCLUSIVE_NOT_PROOF"
    if "NATIVE-OPAQUE-C1-CAPTURE: FULL_ORIGINAL_AST_CAPTURED_NOT_PROOF" in raw and artifact:
        return "FULL_ORIGINAL_AST_CAPTURED_NOT_PROOF"
    if "NATIVE-OPAQUE-C1-CAPTURE: verified source SHA256 differs" in raw and not artifact:
        return "SOURCE_HASH_ADMISSION_REFUSAL_NOT_SEMANTIC_NEGATIVE"
    if "NATIVE-OPAQUE-C1-CAPTURE: isolated exact-one body, unwind and full checks required" in raw and not artifact:
        return "EXACT_ONE_BODY_ADMISSION_REFUSAL_NOT_SEMANTIC_NEGATIVE"
    return "NATIVE_CAPTURE_INCONCLUSIVE_NOT_PROOF"


def native_bound_classification(name: str, raw: str,
                                verifier_exit: int | None,
                                pre_artifact: bool, post_artifact: bool) -> str:
    """Conservative local classification; retained logs decide proof credit."""
    target_entered = "Verifying function 'small_sort_general_with_scratch'" in raw
    admitted = "NATIVE-OPAQUE-C1-BOUND admitted" in raw
    if name == "native-c1-bound-positive":
        if (verifier_exit == 0 and pre_artifact and post_artifact and
                target_entered and admitted and
                "control=none NOT_CALLABLE_SUMMARY" in raw):
            return "NATIVE_C1_BOUND_VF0_CANDIDATE_RAW_REVIEW_REQUIRED"
        return "NATIVE_C1_BOUND_POSITIVE_INCONCLUSIVE_NOT_PROOF"
    if name in ("native-c1-bound-false-normal", "native-c1-bound-false-unwind"):
        control = "normal_false" if name.endswith("normal") else "unwind_false"
        if (verifier_exit in (1, 2) and pre_artifact and post_artifact and
                target_entered and admitted and
                f"control={control} NOT_CALLABLE_SUMMARY" in raw):
            return "NATIVE_C1_BOUND_FALSE_CONTROL_RAW_REVIEW_REQUIRED"
        return "NATIVE_C1_BOUND_FALSE_CONTROL_INCONCLUSIVE_NOT_PROOF"
    refusals = {
        "native-c1-bound-source-refusal":
            "NATIVE-OPAQUE-C1-BOUND: verified source SHA256 differs",
        "native-c1-bound-extra-body":
            "NATIVE-OPAQUE-C1-BOUND: isolated exact-one body, unwind and full checks required",
        "native-c1-bound-malformed":
            "NATIVE-OPAQUE-C1-BOUND: malformed opt-in",
        "native-c1-bound-mixed":
            "NATIVE-OPAQUE-C1-BOUND: exact isolated bound environment required",
    }
    if (name in refusals and verifier_exit in (1, 2) and
            refusals[name] in raw and not pre_artifact and not post_artifact and
            not target_entered and not admitted):
        return "NATIVE_C1_BOUND_ADMISSION_REFUSAL_NOT_SEMANTIC_NEGATIVE"
    if name == "native-c1-bound-default-off":
        if not admitted and not pre_artifact and not post_artifact:
            return "NATIVE_C1_BOUND_DEFAULT_OFF_RAW_OUTCOME_REVIEW_REQUIRED"
        return "NATIVE_C1_BOUND_DEFAULT_OFF_INCONCLUSIVE_NOT_PROOF"
    return "NATIVE_C1_BOUND_INCONCLUSIVE_NOT_PROOF"


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
           os.environ.get("SORT4_NATIVE_C4_PHASE") is None and
           not C1_ZST_REPAIR_SESSION) or
          (C1_ZST_REPAIR_SESSION and
           os.environ.get("SORT4_NATIVE_C1_ZST_REPAIR_PHASE_ID") == PHASE and
           os.environ.get("SORT4_NATIVE_C4_PHASE") is None and
           os.environ.get("SORT4_NATIVE_OPAQUE_PHASE") is None) or
          (not OPAQUE_SESSION and not C1_ZST_REPAIR_SESSION and
           os.environ.get("SORT4_NATIVE_C4_PHASE") == "1" and
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
    if C1_ZST_REPAIR_SESSION:
        need(profile.get("native_c1_bound_tool_manifest") ==
             "NATIVE-C1-BOUND-TOOL-MANIFEST.json" and
             profile.get("native_c1_bound_verified_source_sha256") ==
             BOUND_SOURCE and
             profile.get("native_c1_bound_original_source_sha256") ==
             BOUND_ORIGINAL and
             profile.get("native_c1_bound_normal_full_mir_sha256") ==
             BOUND_NORMAL_MIR and
             profile.get("native_c1_bound_readonly_full_mir_sha256") ==
             BOUND_READONLY_MIR and
             profile.get("native_c1_bound_require_paired_refinement_before_verifier")
             is True and
         profile.get("zst_repair_tool_manifest") == "ZST-REPAIR-TOOL-MANIFEST.json" and
             profile.get("followup_cases") == list(BOUND_CASE_CONTROLS) and
             profile.get("case_file") == "followup-cases.rs" and
             profile.get("native_c1_capture_cases") is None,
             "native C1 bound exact experimental profile differs")
    historical = load(a.cloud_dir / "sort4-c1-current-recovery.py", "native_c4_historical")
    env = clean_env(a, a.production_source)
    try:
        production_before = historical.snapshot(a, a.production_source)
        tool, before = build_frozen_c4(a, historical, env)
        save(a.evidence / "production-before.json", production_before)
        active = clean_env(a, tool)
        followup = profile["run_mode"] == "FROZEN_C4_INDEPENDENT_FOLLOWUP"
        reuse_admission = followup and profile.get("prior_fresh_admission_build") is not None
        fixture = None
        if not ((OPAQUE_SESSION or C1_ZST_REPAIR_SESSION) and followup and reuse_admission):
            fixture = prepare_c4(a, historical, active)
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
        capture_tool = None
        if OPAQUE_SESSION and profile.get("native_c1_capture_cases"):
            capture_tool = build_native_capture_tool(a, historical, tool, active)
        bound_tool = build_native_bound_tool(a, historical, tool, active) if C1_ZST_REPAIR_SESSION else None
        if C1_ZST_REPAIR_SESSION:
            old_identity = a.evidence / "input-identity.json"
            baseline_identity = json.loads(old_identity.read_text())
            need(baseline_identity.get("source_sha256") == historical.SOURCE and
                 baseline_identity.get("complete_mir_sha256") == historical.GRAPH,
                 "historical C1 baseline input identity differs")
            baseline_path = a.evidence / "historical-c1-baseline-input-identity.json"
            shutil.copy2(old_identity, baseline_path)
            save(old_identity, {
                "phase": PHASE, "scope": "source-linked internal native C1 bounded entry",
                "external_small_sort_caller_bound": False,
                "proof_sha": baseline_identity["proof_sha"],
                "production_head": baseline_identity["production_head"],
                "production_patch_sha256": baseline_identity["production_patch_sha256"],
                "historical_baseline_input_identity": baseline_path.name,
                "historical_baseline_input_identity_sha256": sha(baseline_path),
                "source_sha256": BOUND_SOURCE,
                "original_sha256": BOUND_ORIGINAL,
                "complete_mir_sha256": {"normal": BOUND_NORMAL_MIR,
                                        "readonly": BOUND_READONLY_MIR},
                "pre_ast_sha256": BOUND_PRE_AST,
                "paired_refinement_required_before_verifier": True,
                "tool_translator_sha256": sha(bound_tool / TRANSLATOR),
                "tool_kernel_sha256": sha(bound_tool / KERNEL),
                "tool_console_sha256": sha(bound_tool / "bin/verifast"),
                "bound_manifest_sha256": sha(a.proof_root / HERE /
                                             "NATIVE-C1-BOUND-TOOL-MANIFEST.json"),
                "actual_unwind": "exact internal FnMut C1 direct Continue",
                "normal_post": "target full native CURRENT source, scratch MU, F.own and thread",
                "unwind_post": "target full native CURRENT source, scratch MU, F.own and thread after direct C1 cleanup",
                "accepted": False, "proof_credit": False})
        zst_model = (native_zst_model_diagnostics(a, bound_tool, clean_env(a, bound_tool))
                     if C1_ZST_REPAIR_SESSION else None)
        if C1_ZST_REPAIR_SESSION and not zst_model.get("gates_passed"):
            supplied = {"classification": "SKIPPED_MODEL_GATES_FAILED",
                        "cases": {}, "proof_credit": False}
        else:
            supplied = supplied_cases(a, tool, active, capture_tool, bound_tool)
        native_c4_capture = None
        native_c4_bound = None
        if C1_ZST_REPAIR_SESSION and profile.get("native_c4_mode") is not None:
            need(profile["native_c4_mode"] in ("CAPTURE_ONLY", "BOUND_CANDIDATE") and
                 zst_model.get("gates_passed") is True and
                 supplied.get("cases", {}).get("native-c1-bound-positive", {}).get(
                     "native_bound_candidate_binding") is True,
                 "native C4 capture requires fresh full model gates and native C1")
            fresh = supplied["cases"]
            need(all(fresh.get(name, {}).get("native_bound_classification") ==
                     "NATIVE_C1_BOUND_FALSE_CONTROL_RAW_REVIEW_REQUIRED"
                     for name in ("native-c1-bound-false-normal", "native-c1-bound-false-unwind")) and
                 all(fresh.get(name, {}).get("native_bound_classification") ==
                     "NATIVE_C1_BOUND_ADMISSION_REFUSAL_NOT_SEMANTIC_NEGATIVE"
                     for name in ("native-c1-bound-source-refusal", "native-c1-bound-extra-body",
                                  "native-c1-bound-malformed", "native-c1-bound-mixed")),
                 "native C4 requires complete fresh C1 control matrix")
            save(a.evidence / "native-c1-before-c4.json", supplied)
            c4_module = load(a.cloud_dir / "sort4-native-c1-bound/native-c4-driver.py",
                             "native_c4_capture_module")
            c4_namespace = SimpleNamespace(load=load, stage=stage,
                clean_env=clean_env, source_support=source_support, save=save)
            if profile["native_c4_mode"] == "BOUND_CANDIDATE":
                native_c4_bound = c4_module.run_bound(a, bound_tool, active, c4_namespace)
            else:
                native_c4_capture = c4_module.run(a, bound_tool, active, c4_namespace)
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
        if capture_tool is not None:
            expected_capture = {
                "native-c1-capture-preast": "FULL_ORIGINAL_AST_CAPTURED_NOT_PROOF",
                "native-c1-capture-sourcehash-refusal": "SOURCE_HASH_ADMISSION_REFUSAL_NOT_SEMANTIC_NEGATIVE",
                "native-c1-capture-extra-body-refusal": "EXACT_ONE_BODY_ADMISSION_REFUSAL_NOT_SEMANTIC_NEGATIVE"}
            components_complete = components_complete and all(
                supplied["cases"].get(name, {}).get("native_capture_classification") == wanted
                for name, wanted in expected_capture.items())
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
                  "zst_model_diagnostics": zst_model,
                  "native_c4_capture": native_c4_capture,
                  "native_c4_bound": native_c4_bound,
                  "admission": admission,
                  "comment_admission": comment_admission,
                  "run_mode": profile["run_mode"],
                  "collector_pass_is_proof": False}
        if C1_ZST_REPAIR_SESSION:
            cases = supplied.get("cases", {})
            refusal_names = (
                "native-c1-bound-source-refusal", "native-c1-bound-extra-body",
                "native-c1-bound-malformed", "native-c1-bound-mixed")
            result["experimental_native_c1_bound"] = {
                "candidate_internal_binding": cases.get(
                    "native-c1-bound-positive", {}).get(
                        "native_bound_candidate_binding") is True,
                "false_controls_ready_for_raw_review": all(
                    cases.get(name, {}).get("native_bound_classification") ==
                    "NATIVE_C1_BOUND_FALSE_CONTROL_RAW_REVIEW_REQUIRED"
                    for name in ("native-c1-bound-false-normal",
                                 "native-c1-bound-false-unwind")),
                "admission_controls_exact": all(
                    cases.get(name, {}).get("native_bound_classification") ==
                    "NATIVE_C1_BOUND_ADMISSION_REFUSAL_NOT_SEMANTIC_NEGATIVE"
                    for name in refusal_names),
                "default_off_raw_review_required": cases.get(
                    "native-c1-bound-default-off", {}).get(
                        "native_bound_classification") ==
                        "NATIVE_C1_BOUND_DEFAULT_OFF_RAW_OUTCOME_REVIEW_REQUIRED",
                "profile_accepted": False, "proof_credit": False,
                "external_small_sort_caller_bound": False,
                "callable_summary": False}
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
