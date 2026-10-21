"""Cloud-only focused A1 stage collector; never emits proof/admission records.

This uses the pinned VeriFast ``-focus verified/lib.rs:line`` CLI. Export,
decode, and refinement still process the entire source pair before focus is
applied to symbolic body checking. The result is raw same-Build stage evidence;
compiler item IDs, body counts, native-post equality, and proof verdicts need
separate source-derived admission and classification.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
from typing import Any, Mapping


PHASE = "SORT4-A1-CHECKED-TRAIT-CONTRACT-CLOUD-2026-10-17"
HERE = Path("research/challenge-8/cloud-build/sort4-caller-entry-native")
PROFILE_BINDINGS = {
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
TR = "src/rust_frontend/vf_mir_translator/vf_mir_translator.ml"
SCHEMA = "src/rust_frontend/vf_mir/vf_mir.capnp"
EXPORTER = "src/rust_frontend/vf_mir_exporter/src/lib.rs"
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
BODY_CASES = {"P0a": "default16", "P0b": "freeze32",
              "N-default-contract": "default16",
              "N-freeze-contract": "freeze32"}
CALLER_CASES = {"P0c", "N-false31"}
INTERFACE_CASES = {"P-dispatch", "P1"}
ALL_CASES = set(BODY_CASES) | CALLER_CASES | INTERFACE_CASES
LEGACY_FLAGS = (
    "SORT4_STABLE_METHOD_BINDING", "SORT4_SELECTED_BRANCH_INTERFACE",
    "SORT4_SELECTED_COMPILER_BINDING_VERIFIED",
    "SORT4_ACTUAL_CALLER_ENTRY_PHASE", "SORT4_NATIVE_C1_BOUND_PHASE",
    "SORT4_NATIVE_OPAQUE_PHASE", "SORT4_NATIVE_C1_ZST_REPAIR_PHASE",
)
A1_ENV_IDENTITY_KEYS = (
    "SMALLSORT_EXECUTION_PROVIDER", "SORT4_A1_AUTHORIZATION_PHASE_ID",
    "SORT4_A1_PHASE_ID", "SORT4_A1_CHECKED_TRAIT_CONTRACT",
    "SORT4_A1_STAGE", "SORT4_A1_PROFILE_SHA256",
    "SORT4_A1_FORCE_LEGACY_REDIRECT", "CLOUD_BUILD_ID", "PROOF_SHA",
    "INFRA_SHA", "SORT4_A1_CHECKED_HELPER_NAME",
    "SORT4_A1_CHECKED_HELPER_SOURCE_SHA256",
    "SORT4_A1_CHECKED_HELPER_BLOCK_SHA256",
    "SORT4_A1_CHECKED_HELPER_SOURCE_START_LINE",
    "SORT4_A1_CHECKED_HELPER_SOURCE_END_LINE",
    "SORT4_A1_CHECKED_HELPER_BODY_START_LINE",
    "SORT4_A1_CHECKED_HELPER_BODY_END_LINE",
)
HELPER_ONLY_ENV_KEYS = (
    "SORT4_A1_CHECKED_HELPER_NAME", "SORT4_A1_CHECKED_HELPER_SOURCE_SHA256",
    "SORT4_A1_CHECKED_HELPER_BLOCK_SHA256",
    "SORT4_A1_CHECKED_HELPER_SOURCE_START_LINE",
    "SORT4_A1_CHECKED_HELPER_SOURCE_END_LINE",
    "SORT4_A1_CHECKED_HELPER_BODY_START_LINE",
    "SORT4_A1_CHECKED_HELPER_BODY_END_LINE",
)


def need(ok: bool, reason: str) -> None:
    if not ok:
        raise RuntimeError("A1-FOCUS: " + reason)


def _plain_json_value(value: Any) -> Any:
    """Copy immutable observer containers into lossless JSON-compatible ones."""
    if isinstance(value, Mapping):
        return {key: _plain_json_value(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_plain_json_value(item) for item in value]
    return value


def _stage_environment_sha256(env: Mapping[str, Any]) -> str:
    need(all(isinstance(key, str) and isinstance(value, str)
             for key, value in env.items()),
         "stage environment must contain string keys and values")
    encoded = json.dumps(dict(env), sort_keys=True, separators=(",", ":"),
                         ensure_ascii=True).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _a1_environment_projection(env: Mapping[str, Any]) -> dict[str, str | None]:
    return {key: env.get(key) for key in A1_ENV_IDENTITY_KEYS}


def _checked_helper_stage_environment(caller_env: Mapping[str, Any],
                                     contract: Mapping[str, Any]) -> dict[str, str]:
    need(all(isinstance(key, str) and isinstance(value, str)
             for key, value in caller_env.items()),
         "caller stage environment must be string-valued")
    need(caller_env.get("SORT4_A1_CHECKED_TRAIT_CONTRACT") == "1" and
         caller_env.get("SORT4_A1_PHASE_ID") == PHASE and
         caller_env.get("SORT4_A1_STAGE") in ("caller", "interface") and
         not any(key in caller_env for key in HELPER_ONLY_ENV_KEYS),
         "checked helper requires a caller/interface environment with A1 contract enabled")
    helper_env = dict(caller_env)
    helper_env.pop("SORT4_A1_FORCE_LEGACY_REDIRECT", None)
    helper_env["SORT4_A1_STAGE"] = "checked-helper"
    helper_env.update({
        "SORT4_A1_CHECKED_HELPER_NAME": str(contract["name"]),
        "SORT4_A1_CHECKED_HELPER_SOURCE_SHA256": str(contract["generated_source_sha256"]),
        "SORT4_A1_CHECKED_HELPER_BLOCK_SHA256": str(contract["source_sha256"]),
        "SORT4_A1_CHECKED_HELPER_SOURCE_START_LINE": str(contract["source_start_line"]),
        "SORT4_A1_CHECKED_HELPER_SOURCE_END_LINE": str(contract["source_end_line"]),
        "SORT4_A1_CHECKED_HELPER_BODY_START_LINE": str(contract["body_start_line"]),
        "SORT4_A1_CHECKED_HELPER_BODY_END_LINE": str(contract["body_end_line"]),
    })
    return helper_env


def _source_bound_caller_focus_span(binding: Any) -> tuple[int, dict[str, Any]]:
    """Read and copy a validated caller Body.span from the immutable result."""
    caller_binding = binding.get("binding") if isinstance(binding, Mapping) else None
    span = (caller_binding.get("mir_body_span")
            if isinstance(caller_binding, Mapping) else None)
    lo = span.get("lo") if isinstance(span, Mapping) else None
    hi = span.get("hi") if isinstance(span, Mapping) else None
    lo_line = lo.get("line") if isinstance(lo, Mapping) else None
    hi_line = hi.get("line") if isinstance(hi, Mapping) else None
    need(isinstance(span, Mapping) and
         isinstance(lo, Mapping) and isinstance(hi, Mapping) and
         lo.get("source_path") == "verified/lib.rs" and
         hi.get("source_path") == "verified/lib.rs" and
         isinstance(lo_line, int) and not isinstance(lo_line, bool) and
         isinstance(hi_line, int) and not isinstance(hi_line, bool) and
         lo_line > 0 and lo_line <= hi_line,
         "source-bound caller MIR Body.span required before focus")
    copied = _plain_json_value(span)
    need(isinstance(copied, dict),
         "source-bound caller MIR Body.span required before focus")
    return lo_line, copied


def _record_caller_focus_span(result: dict[str, Any], binding: Any) -> int:
    """Bind focus and its JSON-safe observation to the validated caller span."""
    line, span = _source_bound_caller_focus_span(binding)
    result["focus"] = f"verified/lib.rs:{line}"
    result["focus_source_line"] = line
    result["compiler_caller_span_observed"] = span
    return line


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_profile_binding(proof_root: Path, profile: Mapping[str, Any],
                              env: Mapping[str, str]) -> Path:
    """Validate the exact authorization-to-profile pair without Cloud tools."""
    need(isinstance(profile, Mapping), "published A1 profile must be an object")
    need(isinstance(env, Mapping), "A1 profile environment must be a mapping")
    authorization = env.get("SORT4_A1_AUTHORIZATION_PHASE_ID")
    need(isinstance(authorization, str), "unknown A1 authorization/profile binding")
    profile_name = PROFILE_BINDINGS.get(authorization)
    need(profile_name is not None, "unknown A1 authorization/profile binding")
    profile_path = Path(proof_root) / HERE / profile_name
    profile_hash = env.get("SORT4_A1_PROFILE_SHA256")
    need(isinstance(profile_hash, str) and HEX64.fullmatch(profile_hash) is not None and
         profile_path.is_file() and sha(profile_path) == profile_hash,
         "published A1 profile file SHA")
    try:
        decoded_profile = json.loads(profile_path.read_text())
    except (OSError, UnicodeError, json.JSONDecodeError):
        need(False, "published A1 profile JSON")
        raise AssertionError("unreachable")
    need(isinstance(decoded_profile, dict) and decoded_profile == profile,
         "published A1 decoded profile identity")
    need(env.get("SORT4_A1_PHASE_ID") == PHASE and
         profile.get("authorization_phase_id") == authorization and
         profile.get("phase_id") == PHASE and
         profile.get("experiment_protocol_phase_id") == PHASE and
         profile.get("profile_pin_source") == "coordinator-environment" and
         profile.get("proof_sha") in (None, "") and
         profile.get("infra_sha") in (None, "") and
         profile.get("cloud_build_enabled") is True and
         profile.get("profile_accepted") is False,
         "published A1 profile identity")
    return profile_path


def contained(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def checked_path(path: Path, root: Path, label: str) -> Path:
    value = path.resolve()
    need(contained(value, root.resolve()) and
         str(value).startswith("/workspace/"), label + " outside certified Cloud root")
    return value


def source_focus_line(source: bytes, case_id: str) -> int:
    """Choose one generated-source declaration, not a printable DefPath."""
    need(case_id in ALL_CASES, "unsupported focused A1 case")
    lines = source.decode("utf-8").splitlines()
    if case_id in INTERFACE_CASES:
        return 0
    if case_id in CALLER_CASES:
        matches = [index for index, line in enumerate(lines, 1)
                   if line.strip().startswith("fn a1_guard_observer<")]
        need(len(matches) == 1, "one certified observer declaration required")
        return matches[0]
    default = [index for index, line in enumerate(lines, 1)
               if line.strip() == "impl<T> StableSmallSortTypeImpl for T {"]
    freeze = [index for index, line in enumerate(lines, 1)
              if line.strip() == "impl<T: FreezeMarker> StableSmallSortTypeImpl for T {"]
    need(len(default) == len(freeze) == 1 and default[0] < freeze[0],
         "distinct original threshold impl declarations required")
    if BODY_CASES[case_id] == "default16":
        matches = [index for index in range(default[0] + 1, freeze[0])
                   if lines[index - 1].strip() ==
                   "default fn small_sort_threshold() -> usize {"]
    else:
        matches = [index for index in range(freeze[0] + 1, len(lines) + 1)
                   if lines[index - 1].strip() ==
                   "fn small_sort_threshold() -> usize {"]
    need(len(matches) == 1, "one exact focused threshold body declaration required")
    return matches[0]


def _cloud_gate(a, c4, ghost, tool: Path, receipt: dict,
                profile: dict, manifest: dict) -> None:
    env = os.environ
    need(env.get("SMALLSORT_EXECUTION_PROVIDER") == "cloud-build" and
         env.get("SORT4_A1_PHASE_ID") == PHASE and
         env.get("SORT4_A1_CHECKED_TRAIT_CONTRACT") == "1" and
         bool(env.get("CLOUD_BUILD_ID")) and bool(env.get("CLOUD_BUILD_PROJECT_ID")) and
         not env.get("GITHUB_ACTIONS"), "exact Cloud Build phase/provider")
    need(all(env.get(name) in (None, "", "0") for name in LEGACY_FLAGS),
         "conflicting legacy binding flag")
    for name in ("proof_root", "production_source", "work_root", "evidence",
                 "cloud_dir"):
        need(str(Path(getattr(a, name)).resolve()).startswith("/workspace/"),
             name + " outside Cloud workspace")
    # The lane installs rustup in the container and obtains this immutable
    # input from `rustc --print sysroot`; its path need not be /workspace.
    sysroot = Path(a.compiler_sysroot).resolve()
    need(sysroot.is_dir() and (sysroot / "lib").is_dir() and
         env.get("RUSTUP_TOOLCHAIN") == profile.get("compiler_toolchain") ==
         "nightly-2026-09-25" and
         profile.get("compiler_commit") ==
         "f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f",
         "pinned compiler toolchain/sysroot identity")
    observed_sysroot = subprocess.check_output(
        ["rustc", "--print", "sysroot"], text=True).strip()
    version = subprocess.check_output(
        ["rustc", "--version", "--verbose"], text=True)
    need(Path(observed_sysroot).resolve() == sysroot and
         re.search(r"(?m)^commit-hash: " + profile["compiler_commit"] + r"$", version)
         is not None and
         re.search(r"(?m)^host: " + re.escape(profile["target"]) + r"$", version)
         is not None,
         "active rustc does not match frozen Cloud compiler profile")
    need(int(a.deadline_epoch) - int(time.time()) > 120,
         "shared Build deadline insufficient for one focused case")
    proof = env.get("PROOF_SHA")
    infra = env.get("INFRA_SHA")
    profile_hash = env.get("SORT4_A1_PROFILE_SHA256")
    need(proof is not None and HEX40.fullmatch(proof) is not None and
         infra is not None and HEX40.fullmatch(infra) is not None and
         profile_hash is not None and HEX64.fullmatch(profile_hash) is not None,
         "full proof/infra/profile run pins")
    need(os.environ.get("SORT4_A1_AUTHORIZATION_PHASE_ID") ==
         env.get("SORT4_A1_AUTHORIZATION_PHASE_ID"),
         "active authorization environment differs from focused-stage environment")
    profile_path = validate_profile_binding(a.proof_root, profile, env)
    actual_proof = subprocess.check_output(
        ["git", "-C", str(a.proof_root), "rev-parse", "HEAD"], text=True).strip()
    need(actual_proof == proof, "proof checkout SHA differs")
    manifest_path = Path(a.proof_root) / HERE / "CALLER-ENTRY-MANIFEST.json"
    need(manifest_path.is_file() and
         sha(manifest_path) == profile["caller_manifest_sha256"] and
         json.loads(manifest_path.read_text()) == manifest,
         "legacy reconstruction manifest identity")
    for module, rel, expected in (
        (c4, "sort4-caller-entry-native/selected-runtime.py",
         manifest["runtime_helpers_sha256"]["selected-runtime.py"]),
        (ghost, "sort4-native-c1-bound/ghost-strip.py",
         manifest["ghost_strip_sha256"]),
    ):
        path = Path(a.cloud_dir) / rel
        need(Path(module.__file__).resolve() == path.resolve() and
             path.is_file() and sha(path) == expected,
             "loaded helper differs: " + rel)
    checked_path(tool, Path(a.work_root), "isolated tool")
    need(receipt.get("classification") == "A1_TOOL_BUILT_UNRUN_PROOF" and
         receipt.get("phase_id") == PHASE and receipt.get("build_exit") == 0 and
         receipt.get("r_patch_sha256") == profile["r_patch_sha256"] and
         receipt.get("c_patch_sha256") == profile["c_patch_sha256"] and
         receipt.get("final_translator_sha256") == profile["c_after"][TR] and
         receipt.get("final_schema_sha256") == profile["c_after"][SCHEMA] and
         receipt.get("final_exporter_sha256") == profile["c_after"][EXPORTER] and
         receipt.get("proof_credit") is False,
         "one final A1 tool reconstruction receipt")
    if profile.get("authorization_phase_id") in ("SORT4-REFERENCE-OWN-CALLER-2026-10-21-R13", "SORT4-NATIVE-P1-MATRIX-2026-10-21-R14", "SORT4-ACTUAL-BODY-2026-10-21-R15"):
        need(receipt.get("shared_reference_own_normalization") ==
             profile.get("shared_reference_own_normalization") and
             isinstance(profile.get("shared_reference_own_normalization"), dict),
             "R13 normalized spec receipt/profile binding")
    if profile.get("ghost_call_lifetime_inference") is not None:
        need(receipt.get("ghost_call_lifetime_inference") ==
             profile["ghost_call_lifetime_inference"],
             "R13 ghost-call lifetime overlay receipt/profile binding")
    _tool_identity(tool, receipt)


def _tool_identity(tool: Path, receipt: dict) -> None:
    for name, expected in ((TR, receipt["final_translator_sha256"]),
                           (SCHEMA, receipt["final_schema_sha256"]),
                           (EXPORTER, receipt["final_exporter_sha256"]),
                           ("bin/verifast", receipt["console_binary_sha256"]),
                           ("bin/vf-rust-mir-exporter", receipt["exporter_binary_sha256"])):
        need((tool / name).is_file() and sha(tool / name) == expected,
             "final A1 tool file differs: " + name)

    lifetime_overlay = receipt.get("ghost_call_lifetime_inference")
    if lifetime_overlay is not None:
        need(isinstance(lifetime_overlay, dict) and
             lifetime_overlay.get("source") == "src/verify_expr.ml" and
             lifetime_overlay.get("new_axiom_or_assumed_lemma") is False and
             sha(tool / lifetime_overlay["source"]) ==
             lifetime_overlay.get("result_sha256"),
             "ghost-call lifetime overlay source identity differs")

    normalized = receipt.get("shared_reference_own_normalization")
    if normalized is not None:
        need(isinstance(normalized, dict) and normalized.get("source") ==
             "bin/rust/rust_belt/general.rsspec" and normalized.get("shared_only") is True and
             normalized.get("new_axiom_or_assumed_lemma") is False and
             sha(tool / normalized["source"]) == normalized.get("result_sha256"),
             "normalized shared-reference spec identity differs")


def _artifact(path: Path) -> dict[str, Any]:
    return {"path": str(path), "sha256": sha(path) if path.is_file() else None,
            "bytes": path.stat().st_size if path.is_file() else None}


def _checked_cleanup_helper_contract(source: bytes, case: Mapping[str, Any],
                                     profile: Mapping[str, Any]) -> dict[str, Any] | None:
    """Validate optional source-certificate/profile pin for the checked lemma.

    Profiles/certificates predating this helper have neither declaration and
    retain the old focus behavior. A one-sided or malformed declaration is a
    prerequisite failure, never permission to run the caller focus.
    """
    pin_key = "a1_checked_cleanup_helper_sha256"
    cert_key = "checked_cleanup_helper"
    has_pin = pin_key in profile
    has_metadata = cert_key in case
    if not has_pin and not has_metadata:
        return None
    need(has_pin and has_metadata,
         "checked cleanup helper profile pin and source certificate metadata must both be present")
    metadata = case[cert_key]
    need(isinstance(metadata, Mapping),
         "checked cleanup helper certificate metadata must be an object")
    expected = profile[pin_key]
    need(isinstance(expected, str) and HEX64.fullmatch(expected) is not None and
         metadata.get("source_sha256") == expected,
         "checked cleanup helper source block does not match active profile pin")
    need(metadata.get("name") == "a1_cleanup_option_ref" and
         metadata.get("kind") == "lemma",
         "checked cleanup helper name/kind")
    for key in ("source_start_line", "source_end_line", "body_start_line",
                "body_end_line"):
        value = metadata.get(key)
        need(type(value) is int and value > 0,
             "checked cleanup helper source bounds")
    start, end = metadata["source_start_line"], metadata["source_end_line"]
    body_start, body_end = metadata["body_start_line"], metadata["body_end_line"]
    lines = source.splitlines(keepends=True)
    need(1 <= start <= body_start < body_end <= end <= len(lines),
         "checked cleanup helper source/body interval")
    block = b"".join(lines[start - 1:end])
    need(hashlib.sha256(block).hexdigest() == expected and
         lines[start - 1].strip() == b"/*@" and
         lines[end - 1].strip() == b"@*/",
         "checked cleanup helper exact ghost-block source bytes")
    body = lines[body_start - 1:body_end]
    declaration = b"lem a1_cleanup_option_ref<'a, T>"
    need(len([line for line in lines
              if re.match(rb"\s*lem\s+a1_cleanup_option_ref\b", line)]) == 1 and
         lines[body_start - 1].startswith(declaration) and
         lines[body_end - 1].strip() == b"}" and
         sum(1 for line in body if re.match(
             rb"\s*lem\s+a1_cleanup_option_ref\b", line)) == 1,
         "checked cleanup helper declaration/body source identity")
    return {**dict(metadata), "source_bytes_sha256": expected,
            "generated_source_sha256": case.get("generated_source_sha256"),
            "source_block_bytes": len(block), "proof_credit": False}


def _checked_cleanup_helper_proof(a, c4, tool: Path, receipt: Any,
                                  profile: Mapping[str, Any], fixture: Path,
                                  root: Path, env: Mapping[str, str],
                                  source_bytes: bytes, case: Mapping[str, Any],
                                  source_certificate: Path,
                                  ast_gates_module: Any,
                                  selector) -> dict[str, Any] | None:
    """Freshly prove one certified lemma in this Build, then check its AST.

    The caller passes the frozen AST selector from a1-runner.py. This function
    records a bounded raw prerequisite only; it does not classify caller proof.
    """
    profile_hash = os.environ.get("SORT4_A1_PROFILE_SHA256")
    source_pair = {name: sha(fixture / name)
                   for name in ("verified/lib.rs", "original/lib.rs")}
    try:
        contract = _checked_cleanup_helper_contract(source_bytes, case, profile)
    except Exception as exc:
        if "checked_cleanup_helper" not in profile and \
                "checked_cleanup_helper" not in case and \
                "a1_checked_cleanup_helper_sha256" not in profile:
            return None
        return {"schema": "a1-checked-cleanup-helper-prerequisite-v1",
                "status": "BLOCKED_INVALID_SOURCE_CERTIFICATE_OR_PROFILE",
                "helper_name": "a1_cleanup_option_ref", "error": str(exc),
                "build_id": os.environ.get("CLOUD_BUILD_ID"),
                "profile_sha256": profile_hash,
                "source_pair_sha256": source_pair, "proof_credit": False}
    if contract is None:
        return None
    record: dict[str, Any] = {
        "schema": "a1-checked-cleanup-helper-prerequisite-v1",
        "status": "NOT_RUN", "helper_name": contract["name"],
        "helper_kind": contract["kind"], "case_id": case.get("case_id"),
        "source_id": case.get("source_id"), "unit_id": case.get("unit_id"),
        "build_id": os.environ.get("CLOUD_BUILD_ID"),
        "profile_sha256": profile_hash,
        "source_certificate_sha256": sha(source_certificate),
        "tool_binary_path": str(tool / "bin/verifast"),
        "tool_binary_sha256": (receipt.get("console_binary_sha256")
                               if isinstance(receipt, Mapping) else None),
        "helper_source_sha256": contract["source_bytes_sha256"],
        "helper_source_start_line": contract["source_start_line"],
        "helper_source_end_line": contract["source_end_line"],
        "helper_body_start_line": contract["body_start_line"],
        "helper_body_end_line": contract["body_end_line"],
        "source_pair_sha256": source_pair,
        "proof_credit": False,
    }
    try:
        need(isinstance(receipt, Mapping) and receipt.get("proof_credit") is False and
             isinstance(receipt.get("console_binary_sha256"), str) and
             HEX64.fullmatch(receipt["console_binary_sha256"]) is not None and
             (tool / "bin/verifast").is_file() and
             sha(tool / "bin/verifast") == receipt["console_binary_sha256"],
             "checked cleanup helper requires the exact final tool receipt")
        helper_env = _checked_helper_stage_environment(env, contract)
        record["environment_identity"] = {
            "caller_mode": env.get("SORT4_A1_STAGE"),
            "helper_mode": helper_env.get("SORT4_A1_STAGE"),
            "caller_sha256": _stage_environment_sha256(env),
            "helper_sha256": _stage_environment_sha256(helper_env),
            "caller_keys": sorted(env),
            "helper_keys": sorted(helper_env),
            "caller_a1": _a1_environment_projection(env),
            "helper_a1": _a1_environment_projection(helper_env),
        }
        need(source_bytes == (fixture / "verified/lib.rs").read_bytes() and
             source_pair["verified/lib.rs"] ==
             case.get("generated_source_sha256") and
             source_pair["original/lib.rs"] == sha(fixture / "original/lib.rs") and
             os.environ.get("CLOUD_BUILD_ID") and
             isinstance(profile_hash, str) and HEX64.fullmatch(profile_hash) is not None,
             "checked cleanup helper source/Build/profile identity")
        remaining = int(a.deadline_epoch) - int(time.time())
        if remaining <= 120:
            record.update(status="NOT_RUN_DEADLINE",
                          error="shared Build deadline left no safe checked-helper stage budget",
                          deadline_remaining_seconds=max(0, remaining))
            return record
        helper_root = root / "checked-cleanup-helper"
        need(not helper_root.exists(),
             "checked cleanup helper evidence path must be fresh")
        ast_path = helper_root / "proof-ast.ml"
        command = [str(tool / "bin/verifast"), "-focus",
                   f"verified/lib.rs:{contract['body_start_line']}",
                   "-dump_ast_with_locs", str(ast_path),
                   "-rustc_args", "--edition 2021", "-verbose", "6",
                   "verified/lib.rs"]
        record["focus"] = command[2]
        stage = c4.stage(a, helper_root, "checked-cleanup-helper",
                         command, dict(helper_env), 180, cwd=fixture)
        record["stage"] = _plain_json_value(stage) if isinstance(stage, Mapping) else stage
        record["stage_log_path"] = str(helper_root / "checked-cleanup-helper.log")
        record["ast_artifact"] = _artifact(ast_path)
        record["ast_sha256"] = record["ast_artifact"].get("sha256")
        if isinstance(stage, Mapping) and stage.get("classification") == "NOT_RUN_DEADLINE":
            record.update(status="NOT_RUN_DEADLINE",
                          error=stage.get("reason", "helper stage not run before shared deadline"))
            return record
        need(isinstance(stage, Mapping) and type(stage.get("exit")) is int and
             stage.get("argv") == command and stage.get("cwd") == str(fixture),
             "checked cleanup helper stage command/result identity")
        log_path = helper_root / "checked-cleanup-helper.log"
        need(isinstance(stage.get("log_sha256"), str) and
             HEX64.fullmatch(stage["log_sha256"]) is not None and
             log_path.is_file() and sha(log_path) == stage["log_sha256"],
             "checked cleanup helper verifier log receipt missing or changed")
        record["source_pair_unchanged_after_stage"] = (
            source_pair == {name: sha(fixture / name)
                            for name in ("verified/lib.rs", "original/lib.rs")})
        need(record["source_pair_unchanged_after_stage"],
             "source pair changed during checked cleanup helper proof")
        _tool_identity(tool, dict(receipt))
        record["tool_identity_unchanged_after_stage"] = True
        if stage.get("exit") != 0:
            record.update(status="HELPER_VERIFIER_FAILED",
                          error="checked cleanup helper verifier stage did not exit zero")
            return record
        need(ast_path.is_file() and ast_path.stat().st_size > 0,
             "checked cleanup helper verifier AST artifact missing or empty")
        selection = selector(ast_path.read_text(encoding="utf-8"),
                             ast_gates_module, source_bytes, contract)
        need(isinstance(selection, Mapping) and
             selection.get("classification") ==
             "ONE_SOURCE_INTERVAL_SELECTED_CHECKED_LEMMA" and
             selection.get("proof_credit") is False and
             selection.get("selected", {}).get("name") == contract["name"] and
             selection.get("selected", {}).get("kind") == "lemma" and
             selection.get("selected", {}).get("func_span") ==
             (contract["body_start_line"], contract["body_end_line"]),
             "checked cleanup helper AST selection incomplete")
        record.update(status="HELPER_BODY_VERIFIED_SAME_BUILD",
                      ast_selection=_plain_json_value(selection),
                      verifier_exit=0)
        return record
    except Exception as exc:
        record.update(status="BLOCKED_CHECKED_HELPER_PREREQUISITE",
                      error=f"{type(exc).__name__}: {exc}")
        return record


def _support_cache_key(a, tool: Path, fixture: Path, env: Mapping[str, str],
                      receipt: Mapping[str, Any]) -> str:
    """Key only exact same-Build paired support bytes and execution config."""
    source_pair = {name: sha(fixture / name)
                   for name in ("verified/lib.rs", "original/lib.rs")}
    tool_files = {
        "console": sha(tool / "bin/verifast"),
        "exporter": sha(tool / "bin/vf-rust-mir-exporter"),
        "schema": sha(tool / "src/rust_frontend/vf_mir/vf_mir.capnp"),
        "refiner": sha(tool / "bin/refinement-checker"),
    }
    config = {key: env.get(key) for key in (
        "RUSTUP_TOOLCHAIN", "RUSTFLAGS", "RUSTC_WRAPPER", "SORT4_A1_PHASE_ID",
        "SORT4_A1_CHECKED_TRAIT_CONTRACT", "SORT4_A1_STAGE",
        "SORT4_A1_PROFILE_SHA256", "SORT4_A1_FORCE_LEGACY_REDIRECT")}
    identity = {"build_id": os.environ["CLOUD_BUILD_ID"],
                "source_pair_sha256": source_pair, "tool_sha256": tool_files,
                "tool_receipt": {key: receipt.get(key) for key in (
                    "final_translator_sha256", "final_schema_sha256",
                    "final_exporter_sha256", "console_binary_sha256",
                    "exporter_binary_sha256")},
                "sysroot": str(Path(a.compiler_sysroot).resolve()),
                "compiler_toolchain": os.environ.get("RUSTUP_TOOLCHAIN"),
                "target": os.environ.get("CARGO_BUILD_TARGET"),
                "config": config, "support_target": "a1_guard_observer",
                "proof_credit": False}
    return hashlib.sha256(json.dumps(identity, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


def _cached_support(a, root: Path, fixture: Path, *, key: str,
                    support_cache: dict[str, dict]) -> tuple[dict, dict] | None:
    entry = support_cache.get(key)
    if entry is None:
        return None
    expected_pair = {name: sha(fixture / name)
                     for name in ("verified/lib.rs", "original/lib.rs")}
    if entry.get("source_pair_sha256") != expected_pair or \
            entry.get("build_id") != os.environ["CLOUD_BUILD_ID"] or \
            entry.get("paired_support", {}).get("paired_support_passed") is not True:
        support_cache.pop(key, None)
        return None
    artifacts = entry.get("artifacts", {})
    names = ("normal-mir.bin", "normal-mir.txt", "readonly-mir.bin",
             "readonly-mir.txt", "normal-a1_guard_observer-full-mir.txt",
             "readonly-a1_guard_observer-full-mir.txt")
    for name in names:
        item = artifacts.get(name)
        src = Path(item.get("path", "")) if isinstance(item, Mapping) else Path()
        if not src.is_file() or sha(src) != item.get("sha256"):
            support_cache.pop(key, None)
            return None
    root.mkdir(parents=True, exist_ok=False)
    copied = {}
    for name in names:
        src = Path(artifacts[name]["path"])
        dst = root / name
        shutil.copy2(src, dst)
        if sha(dst) != artifacts[name]["sha256"]:
            raise RuntimeError("A1-FOCUS: paired support cache copy identity mismatch")
        copied[name] = {**artifacts[name], "path": str(dst)}
    rows = dict(entry["stages"])
    for name, row in rows.items():
        rows[name] = {**row, "reused_support": True,
                      "same_build_identity_validated": True}
    support = {**entry["paired_support"],
               "source_pair_sha256": expected_pair,
               "cached_from_support_key": key,
               "same_build_identity_validated": True,
               "proof_credit": False}
    return rows, support


def _remember_support(a, root: Path, source_pair: Mapping[str, str],
                      rows: Mapping[str, Any], support: Mapping[str, Any],
                      support_cache: dict[str, dict], key: str) -> None:
    if support.get("paired_support_passed") is not True:
        return
    names = ("normal-mir.bin", "normal-mir.txt", "readonly-mir.bin",
             "readonly-mir.txt", "normal-a1_guard_observer-full-mir.txt",
             "readonly-a1_guard_observer-full-mir.txt")
    artifacts = {}
    for name in names:
        path = root / name
        if not path.is_file():
            return
        artifacts[name] = {"path": str(path), "sha256": sha(path)}
    support_cache[key] = {"build_id": os.environ["CLOUD_BUILD_ID"],
                          "source_pair_sha256": dict(source_pair),
                          "stages": dict(rows), "paired_support": dict(support),
                          "artifacts": artifacts, "proof_credit": False}


def record_parser_diagnostic(exc, root: Path, evidence: Path) -> None:
    """Persist bounded error context without converting failure to a result."""
    diagnostic = getattr(exc, "parser_diagnostic", None)
    if isinstance(diagnostic, dict) and diagnostic.get("call") in ("normal", "readonly"):
        path = root / (diagnostic["call"] + "-mir.txt")
        diagnostic = dict(diagnostic,
            source_relative_path=str(path.relative_to(evidence)),
            source_bytes_sha256=sha(path),
            transformations=["UTF-8 strict decoding", "universal newlines: CRLF/CR to LF"],
            parser_input_binding="ACTUAL_CALL_INPUT_RECORDED")
        (root / "parser-input-diagnostic.json").write_text(
            json.dumps(diagnostic, indent=2, sort_keys=True) + "\n")
        exc.parser_diagnostic = diagnostic


def collect_focus(a, c4, ghost, tool: Path, receipt: dict, profile: dict,
                  manifest: dict, source_certificate: Path, fixture: Path,
                  case_id: str, *, inventory_module, call_binding_module,
                  ast_gates_module=None, checked_helper_selector=None,
                  focus_case_id: str | None = None,
                  support_cache: dict[str, dict] | None = None,
                  evidence_id: str | None = None,
                  control_env: Mapping[str, str] | None = None,
                  parser_preflight: bool = False) -> dict:
    """Collect paired full-unit stages and one focused AST/verifier observation.

    This function does not classify pass/fail or populate A1Admission. Every
    fixture receives its own directory; identical positive source bytes are
    still checked afresh and no stage result is reused across cases.
    """
    _cloud_gate(a, c4, ghost, tool, receipt, profile, manifest)
    need(case_id in ALL_CASES, "unsupported certified source case")
    focus_case_id = focus_case_id or case_id
    need(focus_case_id in ALL_CASES, "unsupported A1 focus case")
    fixture = checked_path(fixture, Path(a.evidence), "case fixture")
    source_certificate = checked_path(source_certificate, Path(a.evidence),
                                      "source certificate")
    need(source_certificate.name == "source-certificate.json" and
         source_certificate.is_file(), "certified A1 fixture package required")
    cert = json.loads(source_certificate.read_text())
    need(cert.get("phase_id") == PHASE and
         cert.get("schema") == "a1-source-certified-fixtures-v1" and
         cert.get("proof_credit") is False and
         cert.get("execution_performed") is False,
         "source certificate provenance")
    case = cert["cases"][case_id]
    unit_path = checked_path(source_certificate.parent / case["source_file"],
                             source_certificate.parent, "certified Rust unit")
    verified = fixture / "verified/lib.rs"
    original = fixture / "original/lib.rs"
    need(unit_path.is_file() and verified.is_file() and original.is_file() and
         unit_path.read_bytes() == verified.read_bytes() and
         sha(verified) == case["generated_source_sha256"] and
         original.read_bytes() == ghost.strip_ghost(verified.read_bytes()) and
         isinstance(case.get("source_id"), str) and
         isinstance(case.get("unit_id"), str),
         "exact certified verified/original source pair")
    declaration_line = source_focus_line(verified.read_bytes(), focus_case_id)
    stage_mode = ("bodies" if focus_case_id in BODY_CASES else
                  "caller" if focus_case_id in CALLER_CASES else "interface")
    if stage_mode == "caller":
        need((fixture / "a1-threshold-summary.receipt").is_file(),
             "caller publication requires the two-body receipt")
    root_name = (evidence_id if evidence_id is not None else
                 case_id if focus_case_id == case_id else
                 case_id + "--focus-" + focus_case_id)
    need(isinstance(root_name, str) and re.fullmatch(r"[A-Za-z0-9_.-]+", root_name),
         "safe isolated evidence key")
    root = Path(a.evidence) / "focus" / root_name
    need(not root.exists(), "focused case evidence directory already exists")
    env = c4.clean_env(a, tool)
    env.update(SORT4_A1_PHASE_ID=PHASE,
               SORT4_A1_CHECKED_TRAIT_CONTRACT="1",
               SORT4_A1_STAGE=stage_mode,
               SORT4_A1_PROFILE_SHA256=os.environ["SORT4_A1_PROFILE_SHA256"])
    if control_env is not None:
        need(dict(control_env) == {"SORT4_A1_FORCE_LEGACY_REDIRECT": "1"} and
             stage_mode == "caller",
             "only isolated caller legacy-redirect control is supported")
        env.update(control_env)
    # The capture target is unique in the full decoded stream. It does not
    # filter the exporter or translator and is not a claim about focused body.
    cache_key = (_support_cache_key(a, tool, fixture, env, receipt)
                 if support_cache is not None else None)
    cached = (_cached_support(a, root, fixture, key=cache_key,
                              support_cache=support_cache)
              if support_cache is not None else None)
    if cached is None:
        rows, support = c4.source_support(a, tool, fixture, root, env,
                                          target="a1_guard_observer")
        if support_cache is not None and cache_key is not None:
            _remember_support(a, root,
                              {"verified/lib.rs": sha(verified),
                               "original/lib.rs": sha(original)},
                              rows, support, support_cache, cache_key)
    else:
        rows, support = cached
    result: dict[str, Any] = {
        "classification": "RAW_FOCUSED_STAGE_UNCLASSIFIED",
        "case_id": case_id, "focus_case_id": focus_case_id,
        "evidence_root": str(root),
        "source_id": case["source_id"],
        "unit_id": case["unit_id"],
        "build_id": os.environ["CLOUD_BUILD_ID"],
        "focus": None, "focus_stage": stage_mode,
        "focus_source_line": None,
        "source_declaration_line": declaration_line,
        "focus_is_export_or_translation_filter": False,
        "source_pair_sha256": {"verified": sha(verified), "original": sha(original)},
        "source_certificate_sha256": sha(source_certificate),
        "paired_support": support,
        "stages": dict(rows),
        "artifacts": {name: _artifact(root / name) for name in
                      ("normal-mir.bin", "normal-mir.txt",
                       "readonly-mir.bin", "readonly-mir.txt")},
        "body_count_observed": None,
        "compiler_item_identity_observed": None,
        "native_post_ast_equality_observed": None,
        "verdict": "UNCLASSIFIED", "proof_credit": False,
    }
    helper_applicable = (focus_case_id in CALLER_CASES or focus_case_id == "P1")
    helper_declared = ("a1_checked_cleanup_helper_sha256" in profile or
                       "checked_cleanup_helper" in case)
    if helper_applicable and helper_declared:
        result["checked_helper_required"] = True
        if support.get("paired_support_passed") is not True:
            helper_proof = {
                "schema": "a1-checked-cleanup-helper-prerequisite-v1",
                "status": "NOT_RUN_PAIRED_SOURCE_SUPPORT_FAILED",
                "helper_name": "a1_cleanup_option_ref",
                "error": "paired source support did not complete; caller focus skipped",
                "build_id": os.environ.get("CLOUD_BUILD_ID"),
                "profile_sha256": os.environ.get("SORT4_A1_PROFILE_SHA256"),
                "source_pair_sha256": result["source_pair_sha256"],
                "proof_credit": False,
            }
        elif ast_gates_module is None or not callable(checked_helper_selector):
            helper_proof = {
                "schema": "a1-checked-cleanup-helper-prerequisite-v1",
                "status": "BLOCKED_CHECKED_HELPER_AST_GATE_UNAVAILABLE",
                "helper_name": "a1_cleanup_option_ref",
                "error": "pinned AST gate and checked helper selector are required",
                "build_id": os.environ.get("CLOUD_BUILD_ID"),
                "profile_sha256": os.environ.get("SORT4_A1_PROFILE_SHA256"),
                "source_pair_sha256": result["source_pair_sha256"],
                "proof_credit": False,
            }
        else:
            helper_proof = _checked_cleanup_helper_proof(
                a, c4, tool, receipt, profile, fixture, root, env,
                verified.read_bytes(), case, source_certificate,
                ast_gates_module, checked_helper_selector)
        if helper_proof is None:
            helper_proof = {
                "schema": "a1-checked-cleanup-helper-prerequisite-v1",
                "status": "BLOCKED_CHECKED_HELPER_METADATA_MISSING",
                "helper_name": "a1_cleanup_option_ref",
                "error": "helper declaration appeared but no validated prerequisite record was produced",
                "build_id": os.environ.get("CLOUD_BUILD_ID"),
                "profile_sha256": os.environ.get("SORT4_A1_PROFILE_SHA256"),
                "source_pair_sha256": result["source_pair_sha256"],
                "proof_credit": False,
            }
        result["checked_helper_proof"] = helper_proof
        result["checked_helper_proof_path"] = str(root / "checked-cleanup-helper-proof.json")
        (root / "checked-cleanup-helper-proof.json").write_text(
            json.dumps(_plain_json_value(helper_proof), indent=2, sort_keys=True) + "\n")
        if helper_proof.get("status") != "HELPER_BODY_VERIFIED_SAME_BUILD":
            result["classification"] = "BLOCKED_CHECKED_HELPER_PREREQUISITE"
            result["caller_verification_status"] = (
                "NOT_RUN_DEADLINE" if "DEADLINE" in
                str(helper_proof.get("status")) else
                "NOT_RUN_CHECKED_HELPER_PREREQUISITE")
            result["proof_attempted"] = False
            result_path = root / "a1-focus-raw-observation.json"
            with result_path.open("x") as output:
                output.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
            return result
        remaining = int(a.deadline_epoch) - int(time.time())
        if remaining <= 120:
            helper_proof["status"] = "HELPER_BODY_VERIFIED_CALLER_NOT_RUN_DEADLINE"
            helper_proof["error"] = "shared Build deadline left no safe caller verification budget"
            (root / "checked-cleanup-helper-proof.json").write_text(
                json.dumps(_plain_json_value(helper_proof), indent=2, sort_keys=True) + "\n")
            result["classification"] = "BLOCKED_CHECKED_HELPER_PREREQUISITE"
            result["caller_verification_status"] = "NOT_RUN_DEADLINE"
            result["proof_attempted"] = False
            result_path = root / "a1-focus-raw-observation.json"
            with result_path.open("x") as output:
                output.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
            return result
    if support.get("paired_support_passed") is not True:
        result["classification"] = "BLOCKED_PREVERIFIER_STAGE"
        if parser_preflight:
            result.update(parser_preflight_passed=False, proof_attempted=False,
                reason="paired export/decode/refinement/capture or source identity prerequisite failed",
                first_blocker={"case_id": case_id, "event": "preflight_prerequisite_failed",
                    "stage": "paired-source-support", "causal_status": "UNKNOWN",
                    "execution_started": True,
                    "reason": "paired source support failed; retain stage exits and capture errors"})
    else:
        source_text = verified.read_text(encoding="utf-8")
        normal_text = (root / "normal-mir.txt").read_text(encoding="utf-8")
        readonly_text = (root / "readonly-mir.txt").read_text(encoding="utf-8")
        try:
            inventory = inventory_module.observe(case_id, normal_text, readonly_text,
                                                 cert, source_text)
        except inventory_module.InventoryError as exc:
            try:
                record_parser_diagnostic(exc, root, Path(a.evidence))
            except (OSError, ValueError, TypeError) as diagnostic_error:
                exc.parser_diagnostic_persist_error = type(diagnostic_error).__name__
            raise
        if parser_preflight:
            need(sha(verified) == case["generated_source_sha256"] and
                 original.read_bytes() == ghost.strip_ghost(verified.read_bytes()),
                 "source pair changed during focused stages")
            _tool_identity(tool, receipt)
            result.update(classification="PARSER_SOURCE_BINDING_PREFLIGHT_ONLY",
                          parser_preflight_passed=True, proof_attempted=False)
            (root / "parser-preflight.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
            with (root / "a1-focus-raw-observation.json").open("x") as output:
                output.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
            return result
        line = 0
        if focus_case_id in BODY_CASES:
            selected_impl = BODY_CASES[focus_case_id]
            candidates = [row for row in inventory["inventory"]["impls"]
                          if row["impl"] == selected_impl]
            need(len(candidates) == 1, "one numeric compiler impl for body focus")
            items = [item for item in candidates[0]["items"]
                     if item["name"] == "small_sort_threshold"]
            need(len(items) == 1, "one numeric compiler threshold item")
            span = items[0]["body"]["mir_span"]
            signature = items[0]["body"]["fn_sig_span"]
            need(span[0][0] == span[1][0] == "verified/lib.rs" and
                 span[0][1] > 0 and span[0][1] <= span[1][1],
                 "focused threshold MIR span")
            need(signature[0][1] == declaration_line and
                 signature[0][0] == "verified/lib.rs",
                 "source declaration differs from compiler fnSigSpan")
            line = span[0][1]
            result["compiler_item_identity_observed"] = {
                "impl": selected_impl,
                "compiler_impl_id": str(candidates[0]["impl_def_index"]),
                "compiler_item_id": str(items[0]["def_index"]),
                "mir_span": span,
                "fn_sig_span": signature}
        elif case_id in CALLER_CASES:
            binding = call_binding_module.observe(
                focus_case_id, normal_text, readonly_text, cert, source_text)
            line = _record_caller_focus_span(result, binding)
        result["focus"] = f"verified/lib.rs:{line}"
        result["focus_source_line"] = line
        ast_path = root / "proof-ast.ml"
        need(not ast_path.exists() and
             not (fixture / "proof-ast.ml").exists(),
             "focused AST output path must be fresh before verification")
        command = [str(tool / "bin/verifast"), "-focus", result["focus"],
                   "-dump_ast_with_locs", str(ast_path),
                   "-rustc_args", "--edition 2021", "-verbose", "6",
                   "verified/lib.rs"]
        result["stages"]["verification"] = c4.stage(
            a, root, "verification", command, env, 240, cwd=fixture)
        result["artifacts"]["proof-ast.ml"] = _artifact(ast_path)
        if not ast_path.is_file():
            result["classification"] = "BLOCKED_AST_DIAGNOSTIC_STAGE"
    need(sha(verified) == case["generated_source_sha256"] and
         original.read_bytes() == ghost.strip_ghost(verified.read_bytes()),
         "source pair changed during focused stages")
    _tool_identity(tool, receipt)
    result_path = root / "a1-focus-raw-observation.json"
    with result_path.open("x") as output:
        output.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result
