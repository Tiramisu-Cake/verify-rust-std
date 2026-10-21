"""Cloud-only A1 source reconstruction; inert until ``reconstruct`` is called.

The legacy selected-branch chain is replayed from committed inputs. No cached
translator, evidence archive, or host /tmp file is an input. Compilation happens
once, after the R and C patches, under the caller's shared Build deadline.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import time


PHASE = "SORT4-A1-CHECKED-TRAIT-CONTRACT-CLOUD-2026-10-17"
REL = Path("research/challenge-8")
HERE = REL / "cloud-build/sort4-caller-entry-native"
C1 = REL / "cloud-build/sort4-native-c1-bound"
TR = "src/rust_frontend/vf_mir_translator/vf_mir_translator.ml"
SCHEMA = "src/rust_frontend/vf_mir/vf_mir.capnp"
EXPORTER = "src/rust_frontend/vf_mir_exporter/src/lib.rs"
KERNEL = "src/verifast.ml"
R_PATCH = HERE / "required-item-representation-hir-partition-r2-2026-10-20.patch"
C_PATCH = HERE / "checked-threshold-contract.patch"
NATIVE_SIGNATURE_PATCH = HERE / "native-small-sort-impl-signature.patch"
NATIVE_SIGNATURE_MANIFEST = HERE / "NATIVE-SMALL-SORT-IMPL-SIGNATURE-MANIFEST.json"
SELECTED = "e484d9f95202c876957a5d5ab349c6a40bc04dbcf813db4b373819402d807e64"
FOCUS_SCOPE_MANIFEST = C1 / "NATIVE-RUST-FOCUS-DEAD-CODE-SCOPE-MANIFEST.json"
FOCUS_SCOPE_PATCH = C1 / "native-rust-focus-dead-code-scope.patch"
FOCUS_SCOPE_FILE = "src/verify_expr.ml"
FOCUS_PROFILE_NAMES = {
    "SORT4-ACTUAL-LIFETIME-2026-10-21-R16":
        "A1-ACTUAL-LIFETIME-R16-PROFILE-2026-10-21.json",
    "SORT4-ACTUAL-BODY-2026-10-21-R15":
        "A1-ACTUAL-BODY-R15-PROFILE-2026-10-21.json",
    "SORT4-PACKAGE-SCOPE-NATIVE-PROOF-2026-10-20-R6":
        "A1-SCOPE-S3-PROFILE-2026-10-20.json",
    "SORT4-PACKAGING-NATIVE-PROOF-2026-10-20-R7":
        "A1-PACKAGING-R7-PROFILE-2026-10-20.json",
    "SORT4-POST-MIGRATION-NATIVE-PROOF-2026-10-20-R8":
        "A1-POST-MIGRATION-R8-PROFILE-2026-10-20.json",
    "SORT4-NATIVE-INTERFACE-PROOF-2026-10-20-R9":
        "A1-NATIVE-INTERFACE-R9-PROFILE-2026-10-20.json",
    "SORT4-DELIVERABLE-NATIVE-PROOF-2026-10-20-R10":
        "A1-DELIVERABLE-NATIVE-R10-PROFILE-2026-10-20.json",
    "SORT4-CHECKED-CALLER-NATIVE-PROOF-2026-10-21-R11":
        "A1-CHECKED-CALLER-R11-PROFILE-2026-10-21.json",
    "SORT4-CHECKED-HELPER-CALLER-2026-10-21-R12":
        "A1-CHECKED-HELPER-R12-PROFILE-2026-10-21.json",
    "SORT4-REFERENCE-OWN-CALLER-2026-10-21-R13":
        "A1-REFERENCE-OWN-R13-PROFILE-2026-10-21.json",
    "SORT4-NATIVE-P1-MATRIX-2026-10-21-R14":
        "A1-NATIVE-MATRIX-R14-PROFILE-2026-10-21.json",
}


def need(ok: bool, reason: str) -> None:
    if not ok:
        raise RuntimeError("A1-TOOL: " + reason)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pinned(path: Path, digest: str, label: str) -> None:
    need(path.is_file() and sha(path) == digest, label + " SHA differs: " + str(path))


def save(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def native_signature_overlay_maps(profile: dict, manifest: dict) -> tuple[dict, dict, dict]:
    """Validate the exact R2 -> native signature -> C source dependency chain."""
    affected = {TR, SCHEMA, EXPORTER}
    before = profile.get("r_representation_after")
    after = profile.get("r_after")
    need(isinstance(before, dict) and isinstance(after, dict) and
         set(before) == set(after) == affected,
         "native signature R representation/source maps")
    need(isinstance(manifest, dict) and
         manifest.get("mode") == "SCHEMA_BOUND_IMPL_SIGNATURE_SPECIALIZATION" and
         isinstance(manifest.get("files"), dict) and
         set(manifest["files"]) == {TR}, "native signature manifest shape/mode")
    row = manifest["files"][TR]
    need(isinstance(row, dict) and row.get("base_sha256") == before[TR] and
         row.get("result_sha256") == after[TR] and before[TR] != after[TR] and
         all(before[k] == after[k] for k in (SCHEMA, EXPORTER)) and
         manifest.get("patch_sha256") == profile.get("native_signature_patch_sha256"),
         "native signature exact overlay dependency pins")
    need(profile.get("c_before") == after and
         isinstance(profile.get("c_after"), dict) and
         set(profile["c_after"]) == affected and
         all(profile["c_after"][k] == after[k] for k in (SCHEMA, EXPORTER)),
         "native signature C dependency/source maps")
    digests = [*before.values(), *after.values(), *profile["c_after"].values(),
               manifest.get("patch_sha256")]
    need(all(isinstance(v, str) and len(v) == 64 and
             all(c in "0123456789abcdef" for c in v) for v in digests),
         "native signature malformed SHA256 dependency")
    return before, {TR: before[TR]}, {TR: after[TR]}


def classify_focus_dead_code_stage(stage: object, expected: str,
                                   log_bytes: bytes | None) -> dict:
    """Classify only the intended dead-code control, preserving incomplete stages."""
    if not isinstance(stage, dict):
        return {"classification": "INCONCLUSIVE_MALFORMED_STAGE", "proof_credit": False}
    if stage.get("classification") != "TERMINAL":
        return {"classification": str(stage.get("classification", "NOT_RUN")),
                "proof_credit": False}
    code = stage.get("exit")
    if not isinstance(code, int) or isinstance(code, bool):
        return {"classification": "INCONCLUSIVE_MISSING_EXIT", "proof_credit": False}
    digest = stage.get("log_sha256")
    if (not isinstance(digest, str) or len(digest) != 64 or
            any(char not in "0123456789abcdef" for char in digest) or
            log_bytes is None):
        return {"classification": "INCONCLUSIVE_MISSING_LOG", "proof_credit": False}
    if hashlib.sha256(log_bytes).hexdigest() != digest:
        return {"classification": "INCONCLUSIVE_LOG_IDENTITY_MISMATCH",
                "proof_credit": False}
    log_text = log_bytes.decode("utf-8", errors="replace")
    all_dead_code = [line for line in log_text.splitlines()
                     if line.endswith(": dead code")]
    diagnostics = [line for line in all_dead_code if expected in line]
    if code == 1 and diagnostics:
        return {"classification": "EXPECTED_DEAD_CODE_REJECTION",
                "dead_code_diagnostics": diagnostics,
                "all_dead_code_diagnostics": all_dead_code,
                "proof_credit": False}
    if code == 0 and not all_dead_code:
        return {"classification": "PASS_NO_IN_SCOPE_DEAD_CODE",
                "dead_code_diagnostics": [],
                "all_dead_code_diagnostics": [], "proof_credit": False}
    return {"classification": "INCONCLUSIVE_WRONG_PREDICATE_OR_EXIT",
            "dead_code_diagnostics": diagnostics,
            "all_dead_code_diagnostics": all_dead_code,
            "proof_credit": False}


def run_focus_dead_code_scope_regression(a, c4, tool: Path, profile: dict,
                                        evidence: Path) -> dict:
    """Run tiny C frontend controls before the P0a target stage."""
    work = Path(a.work_root) / "a1-focus-dead-code-scope-regression"
    need(not work.exists(), "focus dead-code regression work path already exists")
    work.mkdir(parents=True)
    source = work / "focus-dead-code.c"
    source.write_text("""int dead_body(void)
    //@ requires true;
    //@ ensures result == 0;
{
    int x = 0;
    if (0) {
        x = 1;
    }
    return 0;
}

int clean_body(void)
    //@ requires true;
    //@ ensures result == 0;
{
    return 0;
}
""")
    lines = source.read_text().splitlines()
    dead_focus = next(i for i, line in enumerate(lines, 1)
                      if line.startswith("int dead_body"))
    clean_focus = next(i for i, line in enumerate(lines, 1)
                       if line.startswith("int clean_body"))
    dead_statement_line = next(i for i, line in enumerate(lines, 1)
                               if line.strip() == "x = 1;")
    expected_dead = f"{source.name}({dead_statement_line},"
    env = c4.clean_env(a, tool)
    console = tool / "bin/verifast"
    controls = (
        ("selected-dead-code-negative", [str(console), "-shared", "-focus",
         f"{source}:{dead_focus}", str(source)], "EXPECTED_DEAD_CODE_REJECTION"),
        ("excluded-function-positive", [str(console), "-shared", "-focus",
         f"{source}:{clean_focus}", str(source)], "PASS_NO_IN_SCOPE_DEAD_CODE"),
        ("no-focus-dead-code-negative", [str(console), "-shared", str(source)],
         "EXPECTED_DEAD_CODE_REJECTION"),
    )
    results = {}
    stage_root = evidence / "focus-dead-code-scope-regression"
    for name, argv, want in controls:
        row = c4.stage(a, stage_root, name, argv, env, 45, cwd=work)
        log_path = stage_root / f"{name}.log"
        log_bytes = log_path.read_bytes() if log_path.is_file() else None
        result = classify_focus_dead_code_stage(row, expected_dead, log_bytes)
        result.update({"argv": argv, "expected_classification": want,
                       "exit": row.get("exit") if isinstance(row, dict) else None,
                       "stage_classification": row.get("classification")
                       if isinstance(row, dict) else None,
                       "log_sha256": row.get("log_sha256")
                       if isinstance(row, dict) else None})
        results[name] = result
    profile_name = FOCUS_PROFILE_NAMES.get(
        os.environ.get("SORT4_A1_AUTHORIZATION_PHASE_ID"))
    need(profile_name is not None, "focus dead-code authorization profile")
    receipt = {"classification": "FOCUS_DEAD_CODE_SCOPE_REGRESSION",
               "controls": results,
               "expected_dead_code_location_prefix": expected_dead,
               "expected_dead_code_line": dead_statement_line,
               "profile_accepted": False,
               "profile_sha256": sha(Path(a.proof_root) / HERE / profile_name),
               "source_sha256": sha(source),
               "tool_binary_sha256": sha(console),
               "proof_credit": False}
    save(evidence / "focus-dead-code-scope-regression-receipt.json", receipt)
    need(all(results[name]["classification"] == want
             for name, _, want in controls),
         "focus dead-code registration regression controls")
    return receipt


def cloud_gate(a, profile: dict, manifest: dict) -> None:
    env = os.environ
    need(env.get("SMALLSORT_EXECUTION_PROVIDER") == "cloud-build" and
         env.get("SORT4_A1_PHASE_ID") == PHASE and
         env.get("SORT4_A1_CHECKED_TRAIT_CONTRACT") == "1" and
         bool(env.get("CLOUD_BUILD_ID")) and bool(env.get("CLOUD_BUILD_PROJECT_ID")) and
         not env.get("GITHUB_ACTIONS"), "exact Cloud Build A1 phase/provider")
    for key in ("proof_root", "production_source", "work_root", "evidence", "cloud_dir"):
        path = Path(getattr(a, key)).resolve()
        need(str(path).startswith("/workspace/"), key + " must be under /workspace")
    need(int(a.deadline_epoch) - int(time.time()) > 30,
         "shared Build deadline exhausted")
    need(profile["phase_id"] == PHASE and
         profile["tool_head"] == manifest["tool_head"] ==
         "f76012fb518703b1d98e243ac4f487f16877cfcb" and
         profile["selected_base_translator_sha256"] == SELECTED and
         profile["kernel_sha256"] == manifest["kernel_sha256"] and
         profile["profile_accepted"] is False,
         "A1 profile and frozen tool identity")
    need(not any(env.get(name) for name in (
        "SORT4_SELECTED_COMPILER_BINDING_VERIFIED", "SORT4_STABLE_METHOD_BINDING",
        "SORT4_ACTUAL_CALLER_ENTRY_PHASE", "SORT4_NATIVE_C1_BOUND_PHASE",
        "SORT4_NATIVE_OPAQUE_PHASE", "SORT4_NATIVE_C1_ZST_REPAIR_PHASE")),
         "legacy selected/native opt-ins must be off")


def reconstruct(a, c4, audit, driver, manifest: dict, profile: dict) -> tuple[Path, dict]:
    """Replay committed source patches, then build the final A1 tool once.

    ``c4``, ``audit`` and ``driver`` are the pinned, import-inspected helpers
    already loaded by the A1 runner. Their staged git application and snapshot
    functions share ``a.deadline_epoch``; this function never dispatches a job.
    """
    cloud_gate(a, profile, manifest)
    root = Path(a.proof_root)
    work = Path(a.work_root)
    evidence = Path(a.evidence) / "a1-tool"
    cloud_dir = Path(a.cloud_dir)
    for module, rel, digest in (
        (c4, "sort4-caller-entry-native/selected-runtime.py",
         manifest["runtime_helpers_sha256"]["selected-runtime.py"]),
        (audit, "sort4-first-scope-audit.py",
         manifest["runtime_helpers_sha256"]["sort4-first-scope-audit.py"]),
        (driver, "sort4-caller-entry-native/driver.py",
         profile["caller_driver_sha256"]),
    ):
        path = cloud_dir / rel
        need(Path(module.__file__).resolve() == path.resolve(),
             "helper loaded from unexpected path: " + rel)
        pinned(path, digest, "loaded helper " + rel)
    pinned(root / HERE / "CALLER-ENTRY-MANIFEST.json",
           profile["caller_manifest_sha256"], "legacy caller manifest")
    need(json.loads((root / HERE / "CALLER-ENTRY-MANIFEST.json").read_text()) == manifest,
         "passed legacy manifest differs from pinned bytes")
    tool = work / "a1-checked-trait-contract-isolated-source"
    need(not tool.exists(), "isolated A1 tool already exists")
    production = audit.snapshot(a.production_source, root)
    need(production["head"] == manifest["tool_head"] and
         production["critical"][KERNEL] != "", "production source identity")
    shutil.copytree(a.production_source, tool, symlinks=True)
    need(audit.snapshot(tool, root) == production, "production copy differs")
    env = c4.clean_env(a, tool)
    chain = []

    def apply(name: str, rel: Path, digest: str, allowed: set[str],
              before: dict[str, str] | None = None,
              after: dict[str, str] | None = None) -> None:
        chain.append(driver.apply(a, c4, tool, env, name, root / rel,
                                  digest, allowed, before=before, after=after))

    strict = manifest["strict_patches"]
    need(len(strict) == 3 and len(c4.PATCHES) == 10,
         "legacy strict/C4 chain cardinality")
    for index, (rel, digest) in enumerate(strict):
        apply(f"a1-strict-{index}", REL / rel, digest,
              {TR, KERNEL} if index == 0 else {TR})
    need(sha(tool / KERNEL) == manifest["kernel_sha256"], "strict kernel pin")
    for index, (profile_rel, field, patch_rel, base_field, result_field) in enumerate(c4.PATCHES):
        legacy = json.loads((root / REL / profile_rel).read_text())
        apply(f"a1-c4-{index}", REL / patch_rel, c4.field(legacy, field), {TR},
              before={TR: c4.field(legacy, base_field)} if base_field else None,
              after={TR: c4.field(legacy, result_field)} if result_field else None)
    need(sha(tool / TR) == c4.FINAL_TRANSLATOR, "frozen C4 translator")
    frozen_path = root / REL / "cloud-build/sort4-native-c4/FROZEN-C4-SNAPSHOT.json"
    pinned(frozen_path, manifest["frozen_c4_snapshot_sha256"], "frozen C4 snapshot")
    frozen = json.loads(frozen_path.read_text())
    pre_native = audit.snapshot(tool, root)
    need(all(pre_native[key] == frozen[key] for key in
             ("critical", "effective_rsspec", "proof_std", "modified_hashes",
              "modified_names")), "frozen C4 source profile")

    native = (
        ("a1-native-c1-capture", REL / "cloud-build/sort4-native-opaque/NATIVE-C1-CAPTURE-PROFILE.json",
         REL / "cloud-build/sort4-native-opaque/native-c1-capture-only.patch", "patch_sha256"),
        ("a1-native-c1-bound", C1 / "NATIVE-C1-BOUND-TOOL-MANIFEST.json",
         C1 / "native-c1-bound.patch", "patch_sha256"),
        ("a1-native-c4-combined", C1 / "NATIVE-C4-BOUND-MANIFEST.json",
         C1 / "native-c4-bound-combined.patch", "combined_patch_sha256"),
    )
    for name, profile_rel, patch_rel, field in native:
        legacy = json.loads((root / profile_rel).read_text())
        need(legacy["tool_head"] == manifest["tool_head"] and
             legacy["kernel_sha256"] == manifest["kernel_sha256"] and
             legacy["profile_accepted"] is False, name + " legacy profile")
        apply(name, patch_rel, legacy[field], {TR},
              before={TR: legacy["base_translator_sha256"]},
              after={TR: legacy.get("translator_sha256") or
                     legacy["bound_translator_sha256"]})
    need(sha(tool / TR) == manifest["c4_base_translator_sha256"],
         "native C4 translator")
    for name, profile_rel, patch_rel, allowed in (
        ("a1-zst-size", C1 / "ZST-REPAIR-TOOL-MANIFEST.json",
         C1 / "rust-zst-size.patch", {"src/verifast1.ml"}),
        ("a1-dead-code-identity", C1 / "NATIVE-DEAD-CODE-IDENTITY-DIAGNOSTIC-MANIFEST.json",
         C1 / "native-dead-code-identity-diagnostic.patch",
         {"src/verify_expr.ml", "src/vfconsole/vfconsole.ml"}),
    ):
        legacy = json.loads((root / profile_rel).read_text())
        need(legacy["tool_head"] == manifest["tool_head"] and
             legacy["kernel_sha256"] == manifest["kernel_sha256"] and
             legacy["profile_accepted"] is False, name + " legacy profile")
        apply(name, patch_rel, legacy["patch_sha256"], allowed,
              before={path: legacy["files"][path]["base_sha256"] for path in allowed},
              after={path: legacy["files"][path]["result_sha256"] for path in allowed})

    base_path = root / HERE / "SELECTED-BASE-SNAPSHOT.json"
    pinned(base_path, manifest["fresh_c4_effective_profile_manifest_sha256"],
           "selected base snapshot")
    expected = json.loads(base_path.read_text())[
        "fresh_3b743_observed_native_c4_effective_profile"]["after"]
    pre_slice = audit.snapshot(tool, root)
    driver.compare_source_snapshot(pre_slice, expected, {"bin/verifast"})
    need(pre_slice["critical"][TR] == manifest["c4_base_translator_sha256"],
         "pre-slice translator")

    lifetime_overlay = profile.get("ghost_call_lifetime_inference")
    if lifetime_overlay is not None:
        need(profile.get("authorization_phase_id") in
             ("SORT4-REFERENCE-OWN-CALLER-2026-10-21-R13", "SORT4-NATIVE-P1-MATRIX-2026-10-21-R14", "SORT4-ACTUAL-BODY-2026-10-21-R15", "SORT4-ACTUAL-LIFETIME-2026-10-21-R16") and
             isinstance(lifetime_overlay, dict) and
             lifetime_overlay.get("source") == FOCUS_SCOPE_FILE and
             lifetime_overlay.get("base_sha256") ==
             profile["focus_dead_code_scope_result_sha256"] and
             lifetime_overlay.get("new_axiom_or_assumed_lemma") is False,
             "exact R13 ghost-call lifetime overlay required")

    focus_scope_path = root / FOCUS_SCOPE_MANIFEST
    pinned(focus_scope_path, profile["focus_dead_code_scope_manifest_sha256"],
           "Rust focus dead-code scope manifest")
    focus_scope = json.loads(focus_scope_path.read_text())
    need(focus_scope["tool_head"] == manifest["tool_head"] and
         focus_scope["kernel_sha256"] == manifest["kernel_sha256"] and
         focus_scope["profile_accepted"] is False and
         focus_scope["mode"] == "RUST_FUNCTION_FOCUS_SCOPED_DEAD_CODE_REGISTRATION" and
         focus_scope["patch_sha256"] == profile["focus_dead_code_scope_patch_sha256"] and
         focus_scope["files"][FOCUS_SCOPE_FILE]["result_sha256"] ==
         profile["focus_dead_code_scope_result_sha256"] and
         profile["a1_focus_semantics_sha256"][FOCUS_SCOPE_FILE] ==
         (lifetime_overlay["result_sha256"] if lifetime_overlay is not None else
          profile["focus_dead_code_scope_result_sha256"]),
         "A1 Rust focus dead-code scope profile identity")
    apply("a1-rust-focus-dead-code-scope", FOCUS_SCOPE_PATCH,
          focus_scope["patch_sha256"], {FOCUS_SCOPE_FILE},
          before={FOCUS_SCOPE_FILE:
                  focus_scope["files"][FOCUS_SCOPE_FILE]["base_sha256"]},
          after={FOCUS_SCOPE_FILE:
                 focus_scope["files"][FOCUS_SCOPE_FILE]["result_sha256"]})

    if lifetime_overlay is not None:
        apply("a1-ghost-call-lifetime-inference",
              HERE / "ghost-call-lifetime-inference-r13.patch",
              lifetime_overlay["patch_sha256"], {FOCUS_SCOPE_FILE},
              before={FOCUS_SCOPE_FILE: lifetime_overlay["base_sha256"]},
              after={FOCUS_SCOPE_FILE: lifetime_overlay["result_sha256"]})

    threshold_path = root / HERE / "STABLE-THRESHOLD-BINDING-PINS.json"
    selected_path = root / HERE / "SELECTED-BRANCH-BINDING-PINS.json"
    pinned(threshold_path, profile["stable_threshold_pins_sha256"],
           "stable-threshold pins")
    pinned(selected_path, manifest["selected_binding_pins_sha256"],
           "selected-branch pins")
    threshold = json.loads(threshold_path.read_text())
    selected = json.loads(selected_path.read_text())
    need(threshold["base_translator_sha256"] == manifest["as_mut_ptr_translator_sha256"] and
         selected["base_translator_sha256"] == threshold["result_translator_sha256"] and
         selected["result_translator_sha256"] == SELECTED,
         "slice/threshold/selected translator chain")
    apply("a1-slice-as-mut-ptr", REL / "caller-entry/verifast-slice-as-mut-ptr.patch",
          manifest["as_mut_ptr_patch_sha256"], {TR},
          before={TR: manifest["c4_base_translator_sha256"]},
          after={TR: manifest["as_mut_ptr_translator_sha256"]})
    apply("a1-stable-threshold", HERE / "stable-threshold-binding.patch",
          threshold["patch_sha256"], {TR},
          before={TR: threshold["base_translator_sha256"]},
          after={TR: threshold["result_translator_sha256"]})
    apply("a1-selected-branch", HERE / "selected-branch-binding.patch",
          selected["patch_sha256"], {TR},
          before={TR: selected["base_translator_sha256"]},
          after={TR: SELECTED})
    need(sha(tool / TR) == SELECTED, "exact e484 selected translator")

    r_before = profile["r_before"]
    r_after = profile["r_after"]
    c_before = profile["c_before"]
    c_after = profile["c_after"]
    affected = {TR, SCHEMA, EXPORTER}
    need(set(r_before) == set(r_after) == set(c_before) == set(c_after) == affected and
         r_before[TR] == SELECTED and c_before == r_after and
         all(c_after[key] == c_before[key] for key in (SCHEMA, EXPORTER)),
         "R/C exact file-map shape and ordering")
    signature_manifest_path = root / NATIVE_SIGNATURE_MANIFEST
    pinned(signature_manifest_path, profile["native_signature_manifest_sha256"],
           "native impl signature manifest")
    signature_manifest = json.loads(signature_manifest_path.read_text())
    representation_after, signature_before, signature_after = native_signature_overlay_maps(
        profile, signature_manifest)
    apply("a1-required-item-R", R_PATCH, profile["r_patch_sha256"],
          {TR, SCHEMA, EXPORTER}, before=r_before, after=representation_after)
    apply("a1-native-impl-signature", NATIVE_SIGNATURE_PATCH,
          profile["native_signature_patch_sha256"], {TR},
          before=signature_before, after=signature_after)
    reference_own = None
    if profile.get("authorization_phase_id") in ("SORT4-REFERENCE-OWN-CALLER-2026-10-21-R13", "SORT4-NATIVE-P1-MATRIX-2026-10-21-R14", "SORT4-ACTUAL-BODY-2026-10-21-R15", "SORT4-ACTUAL-LIFETIME-2026-10-21-R16"):
        reference_own = profile.get("shared_reference_own_normalization")
        need(isinstance(reference_own, dict) and reference_own.get("source") ==
             "bin/rust/rust_belt/general.rsspec" and
             reference_own.get("shared_only") is True and
             reference_own.get("new_axiom_or_assumed_lemma") is False,
             "exact R13 shared-reference normalization manifest required")
        spec_path = reference_own["source"]
        need(expected["effective_rsspec"].get(spec_path) == reference_own["base_sha256"],
             "R13 normalization source applicability differs")
        apply("a1-shared-reference-own-normalization",
              HERE / "shared-reference-own-normalization-r13.patch",
              reference_own["patch_sha256"], {spec_path},
              before={spec_path: reference_own["base_sha256"]},
              after={spec_path: reference_own["result_sha256"]})

    # Capture a separately built native-reference console before C/G exists.
    # R repairs representation only; this binary cannot add the checked
    # threshold contract or aliases supplied by C. Its AST is an independent
    # execution reference for native-interface preservation, never a proof.
    (tool / "bin/verifast").unlink(missing_ok=True)
    reference_build = c4.stage(
        a, evidence, "a1-R-only-native-reference-build",
        ["make", "-C", str(tool / "src"), "build-vf-rust-mir-exporter",
         "../bin/verifast", "WITHOUT_LABLGTK=yes", "VERBOSE=yes"],
        c4.clean_env(a, tool), 900, cwd=tool)
    need(reference_build.get("exit") == 0, "R-only native reference build")
    need(all(sha(tool / key) == value for key, value in r_after.items()),
         "R-only native reference source drift")
    reference_console = tool / "bin/verifast-a1-native-reference"
    need(not reference_console.exists(), "native reference binary already exists")
    shutil.copy2(tool / "bin/verifast", reference_console)
    native_reference = {
        "kind": "separately-built-R-only-native-reference",
        "console_path": str(reference_console),
        "console_binary_sha256": sha(reference_console),
        "translator_sha256": r_after[TR],
        "schema_sha256": r_after[SCHEMA],
        "exporter_source_sha256": r_after[EXPORTER],
        "exporter_binary_sha256": sha(tool / "bin/vf-rust-mir-exporter"),
        "r_patch_sha256": profile["r_patch_sha256"],
        "native_signature_patch_sha256": profile["native_signature_patch_sha256"],
        "native_signature_manifest_sha256": profile["native_signature_manifest_sha256"],
        "focus_dead_code_scope_patch_sha256":
            profile["focus_dead_code_scope_patch_sha256"],
        "focus_dead_code_scope_source_sha256": sha(tool / FOCUS_SCOPE_FILE),
        "c_patch_applied": False,
        "shared_reference_own_normalization": reference_own,
        "ghost_call_lifetime_inference": lifetime_overlay,
        "build_id": os.environ["CLOUD_BUILD_ID"],
        "build_exit": reference_build["exit"], "proof_credit": False}
    save(evidence / "R-only-native-reference-receipt.json", native_reference)
    apply("a1-checked-threshold-C", C_PATCH, profile["c_patch_sha256"],
          {TR}, before={TR: c_before[TR]}, after={TR: c_after[TR]})

    # R15 overlays are exact, separately pinned and applied after the R-only
    # reference has been frozen. They never enter that reference binary.
    if profile.get("body_action") == "full-body-c1-recovery":
        need(profile.get("authorization_phase_id") in ("SORT4-ACTUAL-BODY-2026-10-21-R15", "SORT4-ACTUAL-LIFETIME-2026-10-21-R16") and
             all(isinstance(profile.get(key), dict) for key in (
                 "actual_c1_recovery_overlay", "merge_fractions_ast_dump_overlay")),
             "complete c1 candidate requires both exact R15 overlays")
    r15_overlays = {}
    overlay_names = set()
    for key, stem, source in (
        ("actual_c1_recovery_overlay", "ACTUAL-SORT4-C1-RECOVERY-R15-MANIFEST.json", TR),
        ("merge_fractions_ast_dump_overlay", "MERGE-FRACTIONS-AST-DUMP-R15-MANIFEST.json",
         "src/frontend/ocaml_expr_of_ast.ml"),
    ):
        declaration = profile.get(key)
        if declaration is None:
            continue
        need(profile.get("authorization_phase_id") in ("SORT4-ACTUAL-BODY-2026-10-21-R15", "SORT4-ACTUAL-LIFETIME-2026-10-21-R16") and
             isinstance(declaration, dict), "R15 overlay authorization")
        pinned(root / HERE / stem, declaration["manifest_sha256"], "R15 overlay manifest")
        overlay = json.loads((root / HERE / stem).read_text())
        need(overlay["source"] == source and overlay["new_axiom_or_assumed_lemma"] is False and
             overlay["proof_credit"] is False and
             overlay["patch_sha256"] == declaration["patch_sha256"] and
             overlay["result_sha256"] == declaration["result_sha256"], "R15 exact overlay declaration")
        if key == "actual_c1_recovery_overlay":
            need(overlay["base_sha256"] == c_after[TR] and overlay["runtime_body_cut"] is False,
                 "R15 complete-runtime translator applicability")
        else:
            need(overlay["proof_semantics_changed"] is False and
                 overlay["constructor"] == "MergeFractionsStmt" and
                 overlay["fields"] == ["of_loc l", "of_expr e"], "diagnostic serialization only")
        apply(key, HERE / declaration["patch"], overlay["patch_sha256"], {source},
              before={source: overlay["base_sha256"]}, after={source: overlay["result_sha256"]})
        overlay_names.add(source)
        r15_overlays[key] = overlay

    before_build = audit.snapshot(tool, root)
    need(sha(tool / TR) == (r15_overlays.get("actual_c1_recovery_overlay", {}).get(
         "result_sha256", c_after[TR])), "effective final translator identity")
    expected_specs = dict(expected["effective_rsspec"])
    normalized_names = set()
    if reference_own is not None:
        expected_specs[reference_own["source"]] = reference_own["result_sha256"]
        normalized_names.add(reference_own["source"])
        need(before_build["modified_hashes"].get(reference_own["source"]) ==
             reference_own["result_sha256"], "R13 exact normalized spec hash")
    focus_path = FOCUS_SCOPE_FILE
    focus_result = (lifetime_overlay["result_sha256"] if lifetime_overlay is not None
                    else profile["focus_dead_code_scope_result_sha256"])
    need(before_build["critical"][KERNEL] == manifest["kernel_sha256"] and
         sha(tool / focus_path) == focus_result and
         all(before_build["critical"][key] == value for key, value in
             expected["critical"].items()
             if key not in (TR, SCHEMA, focus_path)) and
         before_build["effective_rsspec"] == expected_specs and
         before_build["proof_std"] == expected["proof_std"] and
         before_build["head"] == expected["head"] and
         set(before_build["modified_names"]) - set(expected["modified_names"]) <=
             ({TR, SCHEMA, EXPORTER, focus_path} | normalized_names | overlay_names) and
         all(before_build["modified_hashes"][key] == value for key, value in
             expected["modified_hashes"].items()
             if key not in ({TR, SCHEMA, EXPORTER, focus_path} | overlay_names)) and
         before_build["modified_hashes"].get(focus_path) == focus_result,
         "R/C changed only certified source components")
    # R16 changes are applied only after the complete historical R/C snapshot
    # has passed unchanged. Each has its own exact source/base/result pin.
    r16_overlays = {}
    if profile.get("authorization_phase_id") == "SORT4-ACTUAL-LIFETIME-2026-10-21-R16":
        for key, stem, source, diagnostic in (
            ("r16_c1_phase_binding", "R16-C1-PHASE-BINDING-MANIFEST.json", TR, False),
            ("strict_entry_diagnostic", "STRICT-ENTRY-DIAGNOSTIC-R16-MANIFEST.json", KERNEL, True),
            ("actual_scope_relocation", "ACTUAL-SORT4-SCOPE-RELOCATION-R16-MANIFEST.json", TR, False),
            ("actual_deferred_scope_relocation", "ACTUAL-SORT4-DEFERRED-SCOPE-R16-MANIFEST.json", TR, False),
        ):
            declaration = profile.get(key)
            if key == "actual_scope_relocation" and profile.get("actual_scope_relocation_enabled") is not True:
                need(declaration is None, "inactive scope candidate cannot declare a relocation overlay")
                continue
            if key == "actual_deferred_scope_relocation" and profile.get("actual_deferred_scope_relocation_enabled") is not True:
                need(declaration is None, "inactive deferred candidate cannot declare an overlay")
                continue
            need(isinstance(declaration, dict), "R16 exact overlay declaration required")
            pinned(root / HERE / stem, declaration["manifest_sha256"], "R16 overlay manifest")
            overlay = json.loads((root / HERE / stem).read_text())
            need(overlay["source"] == source and
                 overlay["new_axiom_or_assumed_lemma"] is False and
                 overlay["proof_credit"] is False and
                 overlay["patch_sha256"] == declaration["patch_sha256"] and
                 overlay["result_sha256"] == declaration["result_sha256"],
                 "R16 exact overlay source/pins")
            if diagnostic:
                need(overlay["proof_semantics_changed"] is False and
                     overlay["base_sha256"] == manifest["kernel_sha256"],
                     "R16 unchanged strict freeze applicability")
            elif key == "r16_c1_phase_binding":
                need(overlay["base_sha256"] == r15_overlays["actual_c1_recovery_overlay"]["result_sha256"] and
                     overlay["authorization_phase_id"] == profile["authorization_phase_id"],
                     "R16 exact c1 phase association")
            elif key == "actual_scope_relocation":
                need(key == "actual_scope_relocation" and
                     overlay["base_sha256"] == r16_overlays["r16_c1_phase_binding"]["result_sha256"] and
                     overlay["authorization_phase_id"] == profile["authorization_phase_id"] and
                     overlay["runtime_operations_changed"] is False and
                     overlay["kernel_checks_changed"] is False and
                     overlay["declaration_only"] is True,
                     "R16 declaration-only exact-source relocation")
            else:
                need(key == "actual_deferred_scope_relocation" and
                     profile.get("actual_scope_relocation_enabled") is True and
                     overlay["base_sha256"] == r16_overlays["actual_scope_relocation"]["result_sha256"] and
                     overlay["authorization_phase_id"] == profile["authorization_phase_id"] and
                     overlay["runtime_operations_changed"] is False and
                     overlay["kernel_checks_changed"] is False and
                     overlay["declaration_only"] is True,
                     "R16 deferred declaration exact-source overlay")
            apply(key, HERE / declaration["patch"], overlay["patch_sha256"], {source},
                  before={source: overlay["base_sha256"]}, after={source: overlay["result_sha256"]})
            r16_overlays[key] = overlay
        before_build = audit.snapshot(tool, root)
    save(evidence / "patch-chain.json", chain)
    save(evidence / "pre-build-source-snapshot.json", before_build)

    (tool / "bin/verifast").unlink(missing_ok=True)
    build = c4.stage(a, evidence, "a1-final-schema-exporter-console-build",
                     ["make", "-C", str(tool / "src"),
                      "build-vf-rust-mir-exporter", "../bin/verifast",
                      "WITHOUT_LABLGTK=yes", "VERBOSE=yes"],
                     c4.clean_env(a, tool), 900, cwd=tool)
    need(build.get("exit") == 0, "single final schema/exporter/console build")
    final = audit.snapshot(tool, root)
    need(final["critical"] == before_build["critical"] and
         final["modified_names"] == before_build["modified_names"] and
         final["modified_hashes"] == before_build["modified_hashes"] and
         final["effective_rsspec"] == before_build["effective_rsspec"] and
         final["proof_std"] == before_build["proof_std"] and
         final["head"] == before_build["head"] and
         all(final["binaries"][key] == value for key, value in
             before_build["binaries"].items()
             if key not in ("bin/verifast", "bin/vf-rust-mir-exporter")) and
         all((tool / key).is_file() for key in
             ("bin/verifast", "bin/vf-rust-mir-exporter")) and
         audit.snapshot(a.production_source, root) == production,
         "final source/binary freeze or production preservation")
    focus_regression = run_focus_dead_code_scope_regression(
        a, c4, tool, profile, evidence)
    receipt = {"classification": "A1_TOOL_BUILT_UNRUN_PROOF",
               "phase_id": PHASE, "tool_head": final["head"],
               "selected_base_translator_sha256": SELECTED,
               "r_patch_sha256": profile["r_patch_sha256"],
               "c_patch_sha256": profile["c_patch_sha256"],
               "reconstruction_patch_count": len(chain),
               "final_translator_sha256": final["critical"][TR],
               "final_schema_sha256": final["critical"][SCHEMA],
               "final_exporter_sha256": sha(tool / EXPORTER),
               "final_kernel_sha256": final["critical"][KERNEL],
               "rust_focus_dead_code_scope_sha256": focus_result,
               "focus_dead_code_scope_regression": focus_regression,
               "exporter_binary_sha256": final["binaries"]["bin/vf-rust-mir-exporter"],
               "console_binary_sha256": final["binaries"]["bin/verifast"],
               "build_exit": build["exit"], "native_reference": native_reference,
               "shared_reference_own_normalization": reference_own,
               "ghost_call_lifetime_inference": lifetime_overlay,
               "r15_overlays": r15_overlays, "r16_overlays": r16_overlays, "proof_credit": False}
    save(evidence / "reconstruction-receipt.json", receipt)
    return tool, receipt
