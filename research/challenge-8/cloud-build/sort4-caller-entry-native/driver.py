#!/usr/bin/env python3
"""Cloud-only, unaccepted native caller-entry and slice pointer diagnostic.

This executable reconstructs the pinned current native C4 tool. It verifies
the copied canonical slice cast before applying the one-symbol call binding.
The unfiltered caller prefix records its first actual obstruction separately.
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
import time


REL = Path("research/challenge-8")
HERE = REL / "cloud-build/sort4-caller-entry-native"
C1 = REL / "cloud-build/sort4-native-c1-bound"
TR = Path("src/rust_frontend/vf_mir_translator/vf_mir_translator.ml")
KERNEL = Path("src/verifast.ml")
HEADER = ("#![feature(freeze, rustc_attrs, core_intrinsics)]\n"
          "#![allow(internal_features, dead_code, unused_variables, unreachable_code)]\n"
          "use core::intrinsics;\n"
          "use std::marker::Freeze;\n"
          "use std::mem::{size_of, MaybeUninit};\n"
          "#[unsafe(rustc_allow_lifetime_dependent_specialization)]\n"
          "pub(crate) trait FreezeMarker {}\n"
          "impl<T: Freeze> FreezeMarker for T {}\n\n")
CASES = {
    "canonical-generic": "canonical_slice_as_mut_ptr",
    "canonical-mu": "canonical_slice_as_mut_ptr_mu",
    "consumer-positive": "native_slice_pointer_consumer",
    "consumer-wrong-pointer": "native_slice_pointer_consumer",
    "consumer-missing-raw-rights": "native_slice_pointer_consumer",
    "actual-unfiltered-prefix": "small_sort_general_with_scratch",
}


def need(ok: bool, why: str) -> None:
    if not ok:
        raise RuntimeError("CALLER-ENTRY: " + why)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def git(root: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(root), *args])


def pinned_file(path: Path, expected: str, label: str) -> None:
    need(path.is_file() and sha(path) == expected, f"{label} SHA differs: {path}")


def validate_slice_source_bytes(raw: bytes, manifest: dict) -> str:
    need(hashlib.sha256(raw).hexdigest() == manifest["actual_slice_source_sha256"],
         "same-version slice source SHA")
    method = (b"pub const fn as_mut_ptr(&mut self) -> *mut T {\n"
              b"        self as *mut [T] as *mut T\n    }")
    need(raw.count(method) == 1, "same-version canonical method body")
    return method.decode()


def phase_gate(manifest: dict, env: dict) -> None:
    need(env.get("SMALLSORT_EXECUTION_PROVIDER") == "cloud-build" and
         env.get("LANE") == "o26-sort4-c1-current-recovery" and
         env.get("SORT4_ACTUAL_CALLER_ENTRY_PHASE") == "1" and
         env.get("SORT4_ACTUAL_CALLER_ENTRY_PHASE_ID") ==
         "SORT4-ACTUAL-CALLER-ENTRY-CLOUD-2026-10-11" and
         not env.get("GITHUB_ACTIONS"), "authorized Cloud phase and lane only")
    need(manifest["mode"] == "NATIVE_CALLER_ENTRY_AND_SLICE_AS_MUT_PTR_DIAGNOSTIC" and
         manifest["phase_id"] == env["SORT4_ACTUAL_CALLER_ENTRY_PHASE_ID"] and
         manifest["cloud_build_enabled"] is True and
         manifest["profile_accepted"] is False and
         manifest["actual_caller_proved"] is False and
         manifest["callable_summary"] is False, "experimental manifest mode")


def source_certificate(a, manifest: dict) -> dict:
    std = a.proof_root / "library/core/src/slice/mod.rs"
    small = a.proof_root / "library/core/src/slice/sort/shared/smallsort.rs"
    pinned_file(small, manifest["actual_smallsort_source_sha256"], "SmallSort source")
    method = validate_slice_source_bytes(std.read_bytes(), manifest)
    small_text = small.read_text()
    exact = (
        "    let len = v.len();\n    if len < 2 {\n        return;\n    }\n\n"
        "    if scratch.len() < len + 16 {\n        intrinsics::abort();\n    }\n\n"
        "    let v_base = v.as_mut_ptr();\n    let len_div_2 = len / 2;"
    )
    need(small_text.count(exact) == 1, "actual unfiltered entry statements")
    need(small_text.count("let scratch_base = scratch.as_mut_ptr() as *mut T;") == 1 and
         small_text.count("let presorted_len = if const { size_of::<T>() <= 16 } && len >= 16 {") == 1 and
         small_text.count("} else if len >= 8 {\n            // SAFETY: scratch_base is valid and has enough space.\n            sort4_stable(v_base, scratch_base, is_less);") == 1,
         "actual scratch/branch/first-call source boundary")
    return {"slice_sha256": sha(std), "smallsort_sha256": sha(small),
            "canonical_method_body": method,
            "actual_entry_has_len_early_return": True,
            "actual_entry_has_evaluated_len_plus_16_abort": True,
            "actual_first_sort4_callsite": "smallsort.rs:254",
            "body_byte_match_required_before_binding": True,
            "profile_accepted": False}


def source_admission_controls(a, manifest: dict) -> dict:
    """Refuse source modifications before any translated pointer-call claim."""
    std = (a.proof_root / "library/core/src/slice/mod.rs").read_text()
    method = "pub const fn as_mut_ptr(&mut self) -> *mut T {\n        self as *mut [T] as *mut T\n    }"
    need(validate_slice_source_bytes(std.encode(), manifest) == method,
         "positive canonical source gate")
    changed = {
        "wrong-source": std.replace(method, method.replace("self as *mut [T]", "self as *const [T]"), 1),
        "extra-body": std.replace(method, method.replace("        self as", "        let _extra = 0;\n        self as"), 1),
        "malformed": std.replace(method, method[:-1], 1),
    }
    rows = {}
    for name, source in changed.items():
        need(source != std, "nontrivial source admission mutation " + name)
        try:
            validate_slice_source_bytes(source.encode(), manifest)
            reason = None
        except RuntimeError as exc:
            reason = str(exc)
        refused = reason is not None
        rows[name] = {"classification": "SOURCE_ADMISSION_REFUSAL_NOT_PROOF_NEGATIVE"
                      if refused else "SOURCE_ADMISSION_CONTROL_FAILED",
                      "mutation_sha256": hashlib.sha256(source.encode()).hexdigest(),
                      "refused_before_verifier": refused, "refusal_reason": reason,
                      "proof_credit": False}
    need(all(row["refused_before_verifier"] for row in rows.values()),
         "source admission controls")
    save(a.evidence / "source-admission-controls.json", rows)
    return rows


def phase_admission_control(a, manifest: dict) -> dict:
    malformed = dict(os.environ)
    malformed["SORT4_ACTUAL_CALLER_ENTRY_PHASE_ID"] = "MALFORMED-PHASE-ID"
    try:
        phase_gate(manifest, malformed)
        reason = None
    except RuntimeError as exc:
        reason = str(exc)
    need(reason is not None, "malformed phase ID must refuse")
    result = {"classification": "MALFORMED_PHASE_ADMISSION_REFUSAL_NOT_PROOF_NEGATIVE",
              "refused_before_verifier": True, "refusal_reason": reason,
              "proof_credit": False}
    save(a.evidence / "phase-admission-control.json", result)
    return result


def apply(a, helper, tool: Path, env: dict, name: str, patch: Path,
          pin: str, allowed: set[str], *, before: dict[str, str] | None = None,
          after: dict[str, str] | None = None) -> dict:
    pinned_file(patch, pin, name + " patch")
    headers = [line[6:] for line in patch.read_text().splitlines()
               if line.startswith(("--- a/", "+++ b/"))]
    need(len(headers) % 2 == 0 and set(headers) == allowed and
         all(headers[i] == headers[i + 1] for i in range(0, len(headers), 2)),
         name + " patch touches unexpected source")
    prior = {path: sha(tool / path) for path in allowed}
    for path, value in (before or {}).items():
        need(prior[path] == value, name + " base file " + path)
    root = a.evidence / "tool" / name
    for op in ("check", "apply"):
        args = ["git", "-C", str(tool), "apply"]
        if op == "check":
            args.append("--check")
        args.append(str(patch))
        row = helper.stage(a, root, op, args, env, 90, cwd=tool)
        need(row.get("exit") == 0, name + " git apply " + op)
    actual = {path: sha(tool / path) for path in allowed}
    for path, value in (after or {}).items():
        need(actual[path] == value, name + " result file " + path)
    result = {"patch": str(patch.relative_to(a.proof_root)), "sha256": pin,
              "before": prior, "after": actual}
    save(root / "patch-identity.json", result)
    return result


def reconstruct(a, helper, audit, manifest: dict, env: dict) -> tuple[Path, dict, dict]:
    tool = a.work_root / "sort4-caller-entry-native-isolated-source"
    need(not tool.exists(), "isolated source already exists")
    production = audit.snapshot(a.production_source, a.proof_root)
    need(production["head"] == manifest["tool_head"] and
         production["critical"][str(KERNEL)] != "", "production source head")
    shutil.copytree(a.production_source, tool, symlinks=True)
    need(audit.snapshot(tool, a.proof_root) == production,
         "isolated copy differs from production")
    chain = []
    for index, (rel, pin) in enumerate(manifest["strict_patches"]):
        allowed = {str(TR), str(KERNEL)} if index == 0 else {str(TR)}
        chain.append(apply(a, helper, tool, env, f"strict-{index}",
                           a.proof_root / REL / rel, pin, allowed))
    need(sha(tool / KERNEL) == manifest["kernel_sha256"], "strict kernel pin")
    need(len(helper.PATCHES) == 10, "C4 historical patch chain length")
    for index, (profile_rel, field, patch_rel, base_field, result_field) in enumerate(helper.PATCHES):
        profile = json.loads((a.proof_root / REL / profile_rel).read_text())
        before = {str(TR): helper.field(profile, base_field)} if base_field else None
        after = {str(TR): helper.field(profile, result_field)} if result_field else None
        chain.append(apply(a, helper, tool, env, f"c4-{index}",
                           a.proof_root / REL / patch_rel,
                           helper.field(profile, field), {str(TR)},
                           before=before, after=after))
    need(sha(tool / TR) == helper.FINAL_TRANSLATOR,
         "frozen C4 translator result")
    frozen_path = a.proof_root / REL / "cloud-build/sort4-native-c4/FROZEN-C4-SNAPSHOT.json"
    pinned_file(frozen_path, manifest["frozen_c4_snapshot_sha256"], "frozen C4 snapshot")
    frozen = json.loads(frozen_path.read_text())
    pre_native = audit.snapshot(tool, a.proof_root)
    need(pre_native["critical"] == frozen["critical"] and
         pre_native["effective_rsspec"] == frozen["effective_rsspec"] and
         pre_native["proof_std"] == frozen["proof_std"] and
         pre_native["modified_hashes"] == frozen["modified_hashes"] and
         pre_native["modified_names"] == frozen["modified_names"],
         "frozen C4 source-profile identity")
    save(a.evidence / "frozen-c4-source-snapshot.json", pre_native)

    native_steps = (
        ("native-c1-capture", REL / "cloud-build/sort4-native-opaque/NATIVE-C1-CAPTURE-PROFILE.json",
         REL / "cloud-build/sort4-native-opaque/native-c1-capture-only.patch", "patch_sha256"),
        ("native-c1-bound", C1 / "NATIVE-C1-BOUND-TOOL-MANIFEST.json",
         C1 / "native-c1-bound.patch", "patch_sha256"),
        ("native-c4-combined", C1 / "NATIVE-C4-BOUND-MANIFEST.json",
         C1 / "native-c4-bound-combined.patch", "combined_patch_sha256"),
    )
    for name, profile_rel, patch_rel, field in native_steps:
        profile = json.loads((a.proof_root / profile_rel).read_text())
        need(profile["tool_head"] == manifest["tool_head"] and
             profile["kernel_sha256"] == manifest["kernel_sha256"] and
             profile["profile_accepted"] is False, name + " profile identity")
        chain.append(apply(a, helper, tool, env, name, a.proof_root / patch_rel,
                           profile[field], {str(TR)},
                           before={str(TR): profile["base_translator_sha256"]},
                           after={str(TR): (profile.get("translator_sha256") or
                                            profile["bound_translator_sha256"])}))
    need(sha(tool / TR) == manifest["c4_base_translator_sha256"],
         "current native C4 translator")
    for name, profile_rel, patch_rel, allowed in (
        ("zst-size", C1 / "ZST-REPAIR-TOOL-MANIFEST.json",
         C1 / "rust-zst-size.patch", {"src/verifast1.ml"}),
        ("dead-code-identity", C1 / "NATIVE-DEAD-CODE-IDENTITY-DIAGNOSTIC-MANIFEST.json",
         C1 / "native-dead-code-identity-diagnostic.patch",
         {"src/verify_expr.ml", "src/vfconsole/vfconsole.ml"}),
    ):
        profile = json.loads((a.proof_root / profile_rel).read_text())
        need(profile["tool_head"] == manifest["tool_head"] and
             profile["kernel_sha256"] == manifest["kernel_sha256"] and
             profile["profile_accepted"] is False, name + " profile identity")
        chain.append(apply(a, helper, tool, env, name, a.proof_root / patch_rel,
                           profile["patch_sha256"], allowed,
                           before={path: profile["files"][path]["base_sha256"] for path in allowed},
                           after={path: profile["files"][path]["result_sha256"] for path in allowed}))
    base_result_path = a.proof_root / C1 / "NATIVE-C4-BASE-RESULT-MANIFEST.json"
    pinned_file(base_result_path, manifest["fresh_c4_effective_profile_manifest_sha256"],
                "fresh native C4 result manifest")
    base_result = json.loads(base_result_path.read_text())
    expected = base_result["fresh_3b743_observed_native_c4_effective_profile"]["after"]
    before_build = audit.snapshot(tool, a.proof_root)
    compare_source_snapshot(before_build, expected, {"bin/verifast"})
    need(before_build["critical"][str(TR)] == manifest["c4_base_translator_sha256"],
         "pre-slice translator")
    save(a.evidence / "pre-slice-source-snapshot.json", before_build)
    save(a.evidence / "patch-chain.json", chain)
    (tool / "bin/verifast").unlink(missing_ok=True)
    built = helper.stage(a, a.evidence / "tool", "pre-slice-console-build",
                         ["make", "-C", str(tool / "src"), "../bin/verifast",
                          "WITHOUT_LABLGTK=yes", "VERBOSE=yes"],
                         helper.clean_env(a, tool), 900, cwd=tool)
    need(built.get("exit") == 0, "pre-slice console build")
    after_build = audit.snapshot(tool, a.proof_root)
    compare_source_snapshot(after_build, expected, set())
    save(a.evidence / "pre-slice-effective-snapshot.json", after_build)
    return tool, expected, production


def compare_source_snapshot(actual: dict, expected: dict, ignored_binary: set[str]) -> None:
    need(actual["head"] == expected["head"] and
         actual["critical"] == expected["critical"] and
         actual["effective_rsspec"] == expected["effective_rsspec"] and
         actual["proof_std"] == expected["proof_std"] and
         actual["modified_names"] == expected["modified_names"] and
         actual["modified_hashes"] == expected["modified_hashes"] and
         all(actual["binaries"][name] == value for name, value in expected["binaries"].items()
             if name not in ignored_binary),
         "effective non-console profile differs")


def case_source(template: str, name: str) -> str:
    pattern = rf"(?ms)^// CASE_BEGIN {re.escape(name)}\n(.*?)^// CASE_END {re.escape(name)}$"
    matches = re.findall(pattern, template)
    need(len(matches) == 1, "unique case block " + name)
    return HEADER + matches[0].rstrip() + "\n"


def make_fixture(a, helper, ghost, manifest: dict, name: str) -> tuple[Path, dict]:
    template_path = a.proof_root / HERE / "caller-entry-cases.rs"
    pinned_file(template_path, manifest["source_template_sha256"], "source template")
    text = template_path.read_text()
    need(set(re.findall(r"(?m)^// CASE_BEGIN ([^\s]+)$", text)) == set(CASES),
         "case inventory")
    source = case_source(text, name).encode()
    original = ghost.strip_ghost(source)
    fixture = a.evidence / "cases" / name / "fixture"
    (fixture / "verified").mkdir(parents=True)
    (fixture / "original").mkdir()
    (fixture / "verified/lib.rs").write_bytes(source)
    (fixture / "original/lib.rs").write_bytes(original)
    cert = {"case": name, "target": CASES[name], "verified_sha256": sha(fixture / "verified/lib.rs"),
            "original_sha256": sha(fixture / "original/lib.rs"),
            "ghost_stripped_byte_identical": original == ghost.strip_ghost(source),
            "source_template_sha256": sha(template_path),
            "full_generated_posts_required": True, "proof_credit": False}
    if name.startswith("canonical"):
        body = ("slice as *mut [T] as *mut T" if name == "canonical-generic" else
                "slice as *mut [MaybeUninit<T>] as *mut MaybeUninit<T>")
        need(source.count(body.encode()) == 1 and
             (body.replace("slice", "self") == "self as *mut [T] as *mut T"
              if name == "canonical-generic" else True),
             "canonical generic cast source")
        cert["canonical_body_after_parameter_rename"] = body.replace("slice", "self")
    if name.startswith("consumer"):
        need(original.count(b"v.as_mut_ptr()") == 1 and
             original.count(b"scratch.as_mut_ptr()") == 1,
             "both actual native slice calls")
    if name == "actual-unfiltered-prefix":
        for token in (b"if len < 2", b"scratch.len() < len + 16",
                      b"intrinsics::abort()", b"v.as_mut_ptr()",
                      b"scratch.as_mut_ptr() as *mut T", b"len >= 16",
                      b"else if len >= 8"):
            need(original.count(token) == 1, "unfiltered entry token " + repr(token))
        need(b"size_of::<T>() == 0" not in original and
             b"assume(" not in original and b"sort4_stable(" not in original,
             "prefix diagnostic boundary/no supplied domain")
    save(fixture.parent / "source-certificate.json", cert)
    return fixture, cert


def classify(name: str, result: dict, root: Path, source: str) -> dict:
    first = result.get("first_error") or ""
    pair = result.get("support", {}).get("paired_support_passed") is True
    ast = (result.get("stages", {}).get("proof-ast-diagnostic") == 0 and
           result.get("proof_ast_sha256") is not None)
    stage = result.get("first_causal_stage")
    exit_code = result.get("stages", {}).get("verification")
    if name in ("canonical-generic", "canonical-mu", "consumer-positive"):
        passed = (pair and ast and result.get("source_pair_immutable") is True and
                  stage == "NONE_OBSERVED" and exit_code == 0)
        label = "FRESH_VF0_CANDIDATE_RAW_REVIEW_REQUIRED" if passed else "POSITIVE_FIRST_OBLIGATION"
    elif name in ("consumer-wrong-pointer", "consumer-missing-raw-rights"):
        assertion = ("v_base != source_base" if name == "consumer-wrong-pointer" else
                     "unrelated[..1] |-> ?unrelated_values")
        lines = [i for i, line in enumerate(source.splitlines(), 1)
                 if assertion in line]
        locations = [int(x) for x in re.findall(r"verified/lib\.rs\((\d+),", first)]
        expected_error = ("Cannot prove" if name == "consumer-wrong-pointer" else
                          "No matching heap chunks")
        passed = (pair and ast and result.get("source_pair_immutable") is True and
                  stage == "verification" and exit_code not in (None, 0) and
                  len(lines) == 1 and lines[0] in locations and
                  expected_error in first)
        label = "INTENDED_ASSERTION_NEGATIVE_RAW_REVIEW_REQUIRED" if passed else "NEGATIVE_FIRST_OBLIGATION_WRONG_OR_INCONCLUSIVE"
    else:
        passed = False
        label = "UNFILTERED_ENTRY_FIRST_OBLIGATION_DIAGNOSTIC_NO_PROOF_CREDIT"
    return {"classification": label, "gate_passed": passed,
            "first_causal_stage": stage, "first_error": first or None,
            "verifier_exit": exit_code, "paired_support_passed": pair,
            "proof_ast_captured": ast,
            "proof_credit": False, "actual_caller_proved": False,
            "full_log_sha256": sha(root / "verification.log") if (root / "verification.log").is_file() else None,
            "proof_ast_sha256": result.get("proof_ast_sha256")}


def verify_one(a, helper, tool: Path, env: dict, fixture: Path,
               name: str, *, root_override: Path | None = None) -> dict:
    root = root_override or fixture.parent
    try:
        result = helper.verify_case(a, tool, fixture, root, env,
                                    target=CASES[name], ast=True,
                                    require_paired_support=False, verbosity=6)
    except Exception as exc:
        result = {"classification": "COLLECTOR_OR_SETUP_FAILURE_NO_NEGATIVE_CREDIT",
                  "reason": str(exc), "first_causal_stage": "COLLECTOR",
                  "stages": {}, "support": {}, "source_pair_immutable": False}
    source = (fixture / "verified/lib.rs").read_text()
    gate = classify(name, result, root, source)
    result.update(gate)
    save(root / "case-result.json", result)
    return result


def run(a) -> None:
    for path in (a.production_source, a.production_applied_patch, a.stock_home,
                 a.compiler_sysroot, a.evidence, a.proof_root, a.work_root, a.cloud_dir):
        need(str(path).startswith("/workspace/") and "/../" not in str(path) and
             "/./" not in str(path), "unsafe path " + str(path))
    need(not a.evidence.exists() and a.deadline_epoch - time.time() > 120,
         "fresh evidence and sufficient time required")
    need(git(a.proof_root, "rev-parse", "HEAD").decode().strip() ==
         os.environ.get("PROOF_SHA"), "proof SHA differs")
    need(git(a.production_source, "diff", "--binary", "HEAD") ==
         a.production_applied_patch.read_bytes(), "production patch differs")
    manifest = json.loads((a.proof_root / HERE / "CALLER-ENTRY-MANIFEST.json").read_text())
    phase_gate(manifest, os.environ)
    a.evidence.mkdir(parents=True)
    save(a.evidence / "input-identity.json", {"proof_sha": os.environ["PROOF_SHA"],
         "manifest_sha256": sha(a.proof_root / HERE / "CALLER-ENTRY-MANIFEST.json"),
         "production_head": git(a.production_source, "rev-parse", "HEAD").decode().strip(),
         "production_patch_sha256": sha(a.production_applied_patch),
         "profile_accepted": False})
    try:
        helper_path = a.cloud_dir / "sort4-native-c4/driver.py"
        audit_path = a.cloud_dir / "sort4-first-scope-audit.py"
        capture_path = a.proof_root / REL / "overnight-sort4/capture.py"
        ghost_path = a.cloud_dir / "sort4-native-c1-bound/ghost-strip.py"
        for path, pin in ((helper_path, manifest["runtime_helpers_sha256"]["sort4-native-c4/driver.py"]),
                          (audit_path, manifest["runtime_helpers_sha256"]["sort4-first-scope-audit.py"]),
                          (capture_path, manifest["runtime_helpers_sha256"]["overnight-sort4/capture.py"]),
                          (ghost_path, manifest["ghost_strip_sha256"])):
            pinned_file(path, pin, "runtime helper")
        def load(path: Path, label: str):
            spec = importlib.util.spec_from_file_location(label, path)
            need(spec is not None and spec.loader is not None, "module " + str(path))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
        c4 = load(helper_path, "caller_c4_pure_helpers")
        audit = load(audit_path, "caller_snapshot_pure_helper")
        ghost = load(ghost_path, "caller_ghost_strip")
        cert = source_certificate(a, manifest)
        save(a.evidence / "actual-source-certificate.json", cert)
        source_controls = source_admission_controls(a, manifest)
        phase_control = phase_admission_control(a, manifest)
        tool, expected, production = reconstruct(a, c4, audit, manifest, os.environ.copy())
        env = c4.clean_env(a, tool)
        cases = {}
        # Keep this independent of component success: it records the original
        # entry obstruction under the current pre-binding tool.
        fixture, _ = make_fixture(a, c4, ghost, manifest, "actual-unfiltered-prefix")
        cases["actual-unfiltered-prefix"] = verify_one(a, c4, tool, env, fixture,
                                                        "actual-unfiltered-prefix")
        for name in ("canonical-generic", "canonical-mu"):
            fixture, _ = make_fixture(a, c4, ghost, manifest, name)
            cases[name] = verify_one(a, c4, tool, env, fixture, name)
        consumer_fixture, _ = make_fixture(a, c4, ghost, manifest, "consumer-positive")
        default_root = a.evidence / "cases" / "consumer-default-off"
        default_result = c4.verify_case(a, tool, consumer_fixture, default_root,
                                        env, target=CASES["consumer-positive"],
                                        ast=True, require_paired_support=False,
                                        verbosity=6)
        first_default = default_result.get("first_error") or ""
        default_line = next(i for i, line in enumerate(
            (consumer_fixture / "verified/lib.rs").read_text().splitlines(), 1)
            if "v.as_mut_ptr()" in line)
        default_locations = [int(x) for x in re.findall(
            r"verified/lib\.rs\((\d+),", first_default)]
        default_pass = (default_result.get("first_causal_stage") == "verification" and
                        default_result.get("support", {}).get("paired_support_passed") is True and
                        default_result.get("source_pair_immutable") is True and
                        default_line in default_locations and
                        "No such function" in first_default and
                        "as_mut_ptr" in first_default)
        default_control = {
            "classification": ("DEFAULT_OFF_EXACT_METHOD_REFUSAL_NOT_PROOF_NEGATIVE"
                               if default_pass else "DEFAULT_OFF_FIRST_OBLIGATION_INCONCLUSIVE"),
            "refused_before_binding": default_pass,
            "first_error": first_default or None,
            "expected_call_line": default_line,
            "verifier_exit": default_result.get("verifier_exit"),
            "source_pair_immutable": default_result.get("source_pair_immutable"),
            "proof_credit": False}
        save(default_root / "default-off-control.json", default_control)
        component_ready = all(cases[name]["gate_passed"] for name in
                              ("canonical-generic", "canonical-mu"))
        if component_ready and default_pass:
            patch = a.proof_root / REL / "caller-entry/verifast-slice-as-mut-ptr.patch"
            apply(a, c4, tool, env, "slice-as-mut-ptr", patch,
                  manifest["as_mut_ptr_patch_sha256"], {str(TR)},
                  before={str(TR): manifest["c4_base_translator_sha256"]},
                  after={str(TR): manifest["as_mut_ptr_translator_sha256"]})
            (tool / "bin/verifast").unlink(missing_ok=True)
            row = c4.stage(a, a.evidence / "tool", "slice-binding-console-build",
                           ["make", "-C", str(tool / "src"), "../bin/verifast",
                            "WITHOUT_LABLGTK=yes", "VERBOSE=yes"],
                           c4.clean_env(a, tool), 900, cwd=tool)
            need(row.get("exit") == 0, "slice binding console build")
            after = audit.snapshot(tool, a.proof_root)
            need(after["critical"][str(TR)] == manifest["as_mut_ptr_translator_sha256"] and
                 after["binaries"]["bin/verifast"] != expected["binaries"]["bin/verifast"] and
                 all(after["critical"][key] == expected["critical"][key]
                     for key in expected["critical"] if key != str(TR)) and
                 all(after["modified_hashes"][key] == value
                     for key, value in expected["modified_hashes"].items()
                     if key != str(TR)) and
                 after["modified_names"] == expected["modified_names"] and
                 after["effective_rsspec"] == expected["effective_rsspec"] and
                 after["proof_std"] == expected["proof_std"] and
                 all(after["binaries"][key] == value for key, value in expected["binaries"].items()
                     if key != "bin/verifast") and
                 after["head"] == expected["head"],
                 "post-binding profile differs beyond translator/console")
            save(a.evidence / "post-binding-effective-snapshot.json", after)
            env = c4.clean_env(a, tool)
            cases["actual-unfiltered-prefix-postbinding"] = verify_one(
                a, c4, tool, env,
                a.evidence / "cases" / "actual-unfiltered-prefix" / "fixture",
                "actual-unfiltered-prefix",
                root_override=a.evidence / "cases" / "actual-unfiltered-prefix-postbinding")
            for name in ("consumer-positive", "consumer-wrong-pointer",
                         "consumer-missing-raw-rights"):
                fixture = (consumer_fixture if name == "consumer-positive" else
                           make_fixture(a, c4, ghost, manifest, name)[0])
                cases[name] = verify_one(a, c4, tool, env, fixture, name)
        save(a.evidence / "diagnostic-audit.json", {
            "classification": ("SLICE_COMPONENT_AND_CONSUMER_CANDIDATE_RAW_REVIEW_REQUIRED"
                               if component_ready and default_pass and all(cases.get(name, {}).get("gate_passed")
                               for name in ("consumer-positive", "consumer-wrong-pointer",
                                            "consumer-missing-raw-rights")) else
                               "FIRST_CAUSAL_OBLIGATION_OPEN_NO_CALLER_PROOF"),
            "component_ready_before_binding": component_ready,
            "default_off_control": default_control,
            "source_admission_controls": source_controls,
            "phase_admission_control": phase_control,
            "cases": {name: {key: result.get(key) for key in
                     ("classification", "gate_passed", "first_causal_stage", "first_error",
                      "verifier_exit", "paired_support_passed", "full_log_sha256")}
                     for name, result in cases.items()},
            "tool_before_binding_translator": manifest["c4_base_translator_sha256"],
            "tool_after_binding_translator": (manifest["as_mut_ptr_translator_sha256"]
                                              if component_ready and default_pass else None),
            "actual_caller_proved": False, "callable_summary": False,
            "profile_accepted": False, "proof_credit": False})
        need(audit.snapshot(a.production_source, a.proof_root) == production,
             "production source mutated during diagnostics")
    except Exception as exc:
        save(a.evidence / "collector-error.json", {
            "classification": "SETUP_OR_COLLECTOR_ERROR_NOT_PROOF_VERDICT",
            "reason": str(exc), "profile_accepted": False, "proof_credit": False})
        raise


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("production-source", "production-applied-patch", "stock-home",
                 "compiler-sysroot", "evidence", "proof-root", "work-root", "cloud-dir"):
        p.add_argument("--" + name, type=Path, required=True)
    p.add_argument("--deadline-epoch", type=int, required=True)
    run(p.parse_args())


if __name__ == "__main__":
    main()
