"""Cloud-only parser controls for the checked Option cleanup ghost lemma.

This stage tests the smallest grammar unit that contains the import, lemma,
and an exported Rust Option anchor. It never establishes helper proof or caller
summary credit; the caller-pair helper proof remains mandatory.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import time
from typing import Any, Mapping


HEX64 = re.compile(r"[0-9a-f]{64}\Z")
VARIANTS = ("positive", "negative_fully_qualified",
            "negative_import_inside_block")


def _sha_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _sha_file(path: Path) -> str:
    return _sha_bytes(path.read_bytes())


def _tool_hashes(tool: Path) -> dict[str, str]:
    files = {
        "bin/verifast": tool / "bin/verifast",
        "translator": tool / "src/rust_frontend/vf_mir_translator/vf_mir_translator.ml",
        "schema": tool / "src/rust_frontend/vf_mir/vf_mir.capnp",
        "exporter": tool / "src/rust_frontend/vf_mir_exporter/src/lib.rs",
        "kernel": tool / "src/verifast.ml",
    }
    _need(all(path.is_file() for path in files.values()),
          "one or more reconstructed tool identity files are missing")
    return {name: _sha_file(path) for name, path in files.items()}


def _tool_identity_sha256(hashes: Mapping[str, str]) -> str:
    return _sha_bytes(json.dumps(dict(hashes), sort_keys=True,
                                 separators=(",", ":")).encode("ascii"))


def _need(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError("A1-GHOST-GRAMMAR: " + message)


def _workspace_path(path: Path, label: str) -> Path:
    resolved = path.resolve()
    _need(str(resolved).startswith("/workspace/"), label + " must be under /workspace")
    return resolved


def _profile_guard(a, profile: Mapping[str, Any], receipt: Mapping[str, Any],
                   tool: Path) -> dict[str, str]:
    _need(isinstance(profile, Mapping) and
          profile.get("ghost_grammar_preflight_enabled") is True,
          "R12 grammar preflight profile flag required")
    _need(profile.get("profile_pin_source") == "coordinator-environment" and
          profile.get("cloud_build_enabled") is True and
          profile.get("profile_accepted") is False,
          "coordinator-pinned experimental profile required")
    auth = profile.get("authorization_phase_id")
    protocol = profile.get("experiment_protocol_phase_id")
    phase = profile.get("phase_id")
    env_auth = os.environ.get("SORT4_A1_AUTHORIZATION_PHASE_ID")
    env_phase = os.environ.get("SORT4_A1_PHASE_ID")
    profile_hash = os.environ.get("SORT4_A1_PROFILE_SHA256")
    build_id = os.environ.get("CLOUD_BUILD_ID")
    project_id = os.environ.get("CLOUD_BUILD_PROJECT_ID")
    _need(os.environ.get("SMALLSORT_EXECUTION_PROVIDER") == "cloud-build" and
          isinstance(build_id, str) and bool(build_id) and
          isinstance(project_id, str) and bool(project_id),
          "active Cloud Build provider/Build/project identity required")
    _need(isinstance(auth, str) and auth and env_auth == auth and
          isinstance(protocol, str) and phase == protocol and env_phase == phase,
          "authorization and historical protocol phase bindings differ")
    _need(isinstance(profile_hash, str) and HEX64.fullmatch(profile_hash) is not None,
          "exact coordinator profile SHA required")
    _need(isinstance(receipt, Mapping) and receipt.get("classification") ==
          "A1_TOOL_BUILT_UNRUN_PROOF" and receipt.get("proof_credit") is False and
          receipt.get("build_exit") == 0 and receipt.get("tool_head") ==
          profile.get("tool_head") and receipt.get("phase_id") == phase,
          "same-run reconstructed tool receipt required")
    hashes = _tool_hashes(tool)
    binary_sha = hashes["bin/verifast"]
    _need(HEX64.fullmatch(str(receipt.get("console_binary_sha256", ""))) is not None and
          receipt["console_binary_sha256"] == binary_sha,
          "active console binary differs from reconstruction receipt")
    for field, key in (("final_translator_sha256", "translator"),
                       ("final_schema_sha256", "schema"),
                       ("final_exporter_sha256", "exporter"),
                       ("final_kernel_sha256", "kernel")):
        expected = receipt.get(field)
        _need(isinstance(expected, str) and HEX64.fullmatch(expected) is not None and
              hashes[key] == expected,
              "active tool source differs from reconstruction receipt: " + field)
    _workspace_path(Path(a.evidence), "evidence root")
    _workspace_path(tool, "reconstructed tool")
    return {"build_id": build_id, "project_id": project_id,
            "authorization_phase_id": auth, "phase_id": phase,
            "profile_sha256": profile_hash, "tool_binary_sha256": binary_sha,
            "tool_hashes": hashes,
            "tool_identity_sha256": _tool_identity_sha256(hashes)}


def _source_variants(fixture_helper, ghost) -> dict[str, dict[str, Any]]:
    import_bytes = fixture_helper.OPTION_CLEANUP_IMPORT
    lemma = fixture_helper.OPTION_CLEANUP_LEMMA
    _need(isinstance(import_bytes, bytes) and isinstance(lemma, bytes) and
          import_bytes.startswith(b"//@ use std::option::") and
          lemma.startswith(b"/*@\nlem a1_cleanup_option_ref<'a, T>") and
          lemma.endswith(b"@*/\n"), "passed fixture module helper bytes changed")
    anchor = (b"\npub fn grammar_anchor<'a, T>(value: "
              b"std::option::Option<&'a T>) { let _ = value; }\n")
    positive = import_bytes + lemma + anchor
    qualified_lemma = lemma.replace(b"Option::None", b"std::option::Option::None").replace(
        b"Option::Some", b"std::option::Option::Some")
    qualified = qualified_lemma + anchor
    bare_import = import_bytes.removeprefix(b"//@ ")
    in_block = lemma.replace(b"/*@\n", b"/*@\n" + bare_import, 1) + anchor
    _need(positive != qualified and positive != in_block and qualified != in_block,
          "grammar controls must be distinct source units")
    result = {}
    for name, source, expected_kind, expected_text in (
            ("positive", positive, "positive", None),
            ("negative_fully_qualified", qualified, "constructor", 
             "Not a constructor of type std::option::Option"),
            ("negative_import_inside_block", in_block, "parse", "Parse error")):
        original = ghost.strip_ghost(source)
        _need(isinstance(original, bytes) and original != source,
              "ghost-stripped original must preserve the runtime anchor only")
        result[name] = {"verified": source, "original": original,
                        "source_sha256": _sha_bytes(source),
                        "original_sha256": _sha_bytes(original),
                        "expected_failure_kind": expected_kind,
                        "expected_diagnostic": expected_text}
    return result


def _expected_line(source: bytes, needle: bytes) -> int:
    matches = [index for index, line in enumerate(source.splitlines(), 1)
               if needle in line]
    _need(len(matches) == 1, "expected diagnostic source anchor is ambiguous")
    return matches[0]


def _diagnostic_lines(log_bytes: bytes) -> list[str]:
    lines = log_bytes.decode("utf-8", errors="replace").splitlines()
    return [line for line in lines if ": error:" in line or
            "Parse error" in line or line.startswith(("Fatal error:", "error:", "error["))]


def _matches_expected_negative(case: Mapping[str, Any], log_bytes: bytes) -> dict[str, Any]:
    expected = case["expected_diagnostic"]
    needle = (b"std::option::Option::None" if case["expected_failure_kind"] == "constructor"
              else b"lem a1_cleanup_option_ref")
    line = _expected_line(case["verified"], needle)
    diagnostics = _diagnostic_lines(log_bytes)
    matches = [entry for entry in diagnostics
               if expected in entry and re.search(
                   r"verified/lib\.rs\(" + str(line) + r",[^)]*\)", entry)]
    return {"expected_diagnostic": expected, "expected_source_line": line,
            "diagnostics": diagnostics, "matched": len(diagnostics) == 1 and
            len(matches) == 1}


def _one_variant(a, c4, tool: Path, fixture_helper, ghost, ast_gates,
                 checked_helper_selector, root: Path, name: str,
                 case: Mapping[str, Any], identity: Mapping[str, str],
                 env: Mapping[str, str]) -> dict[str, Any]:
    result: dict[str, Any] = {
        "variant": name, "source_sha256": case["source_sha256"],
        "original_sha256": case["original_sha256"],
        "source_pair_sha256": {"verified/lib.rs": case["source_sha256"],
                               "original/lib.rs": case["original_sha256"]},
        "expected_failure_kind": case["expected_failure_kind"],
        "proof_credit": False, "caller_receipt": False,
        "status": "NOT_RUN"}
    fixture = root / name / "fixture"
    stage_root = root / name / "stage"
    try:
        _need(not fixture.exists() and not stage_root.exists(),
              "fresh grammar evidence directories required")
        _workspace_path(fixture, "variant fixture")
        _workspace_path(stage_root, "variant stage")
        fixture.mkdir(parents=True)
        stage_root.mkdir(parents=True)
        verified = fixture / "verified" / "lib.rs"
        original = fixture / "original" / "lib.rs"
        verified.parent.mkdir(parents=True)
        original.parent.mkdir(parents=True)
        _workspace_path(verified, "verified grammar source")
        _workspace_path(original, "original grammar source")
        verified.write_bytes(case["verified"])
        original.write_bytes(case["original"])
        _need(_sha_file(verified) == case["source_sha256"] and
              _sha_file(original) == case["original_sha256"] and
              original.read_bytes() == ghost.strip_ghost(verified.read_bytes()),
              "written exact source pair does not match ghost stripping")
        body_line = (fixture_helper._checked_cleanup_helper_metadata(
            case["verified"])["body_start_line"] if name == "positive" else
            _expected_line(case["verified"], b"lem a1_cleanup_option_ref"))
        ast_path = stage_root / "proof-ast.ml"
        command = [str(tool / "bin/verifast"), "-focus",
                   f"verified/lib.rs:{body_line}", "-dump_ast_with_locs",
                   str(ast_path), "-rustc_args", "--edition 2021", "-verbose", "6",
                   "verified/lib.rs"]
        stage = c4.stage(a, stage_root, "ghost-grammar", command, dict(env), 180,
                         cwd=fixture)
        result["stage"] = dict(stage) if isinstance(stage, Mapping) else stage
        result["stage_root"] = str(stage_root)
        result["focus_line"] = body_line
        result["ast_path"] = str(ast_path)
        result["ast_sha256"] = _sha_file(ast_path) if ast_path.is_file() else None
        log_path = stage_root / "ghost-grammar.log"
        result["log_path"] = str(log_path)
        log_bytes = log_path.read_bytes() if log_path.is_file() else None
        result["log_sha256"] = _sha_bytes(log_bytes) if log_bytes is not None else None
        if not isinstance(stage, Mapping):
            result.update(status="INCONCLUSIVE_MALFORMED_STAGE",
                          error="stage result is not a mapping")
        elif stage.get("classification") != "TERMINAL":
            result.update(status="NOT_RUN_OR_PARTIAL",
                          stage_classification=stage.get("classification"))
        elif type(stage.get("exit")) is not int:
            result.update(status="INCONCLUSIVE_MALFORMED_EXIT",
                          error="terminal stage exit must be an integer")
        elif not isinstance(log_bytes, bytes) or stage.get("log_sha256") != result["log_sha256"]:
            result.update(status="INCONCLUSIVE_MISSING_OR_MISMATCHED_LOG",
                          error="terminal log missing or hash differs")
        elif name == "positive":
            if stage["exit"] != 0 or not ast_path.is_file():
                result.update(status="GRAMMAR_POSITIVE_FAILED",
                              error="positive grammar stage did not exit zero with AST")
            else:
                metadata = fixture_helper._checked_cleanup_helper_metadata(
                    case["verified"])
                metadata["source_bytes_sha256"] = metadata["source_sha256"]
                selection = checked_helper_selector(
                    ast_path.read_text(encoding="utf-8"), ast_gates,
                    case["verified"], metadata)
                _need(isinstance(selection, Mapping) and
                      selection.get("classification") ==
                      "ONE_SOURCE_INTERVAL_SELECTED_CHECKED_LEMMA" and
                      selection.get("body_count_from_intervals") == 1 and
                      selection.get("selected", {}).get("name") ==
                      "a1_cleanup_option_ref" and
                      selection.get("selected", {}).get("kind") == "lemma" and
                      selection.get("proof_credit") is False,
                      "positive AST did not select exactly the manual helper lemma")
                result.update(status="GRAMMAR_POSITIVE_PASS",
                              ast_selection=dict(selection))
        else:
            if stage["exit"] == 0:
                result.update(status="GRAMMAR_NEGATIVE_UNEXPECTED_PASS",
                              diagnostic_match={"matched": False,
                                                "diagnostics": _diagnostic_lines(log_bytes)})
            else:
                match = _matches_expected_negative(case, log_bytes)
                result.update(status="EXPECTED_GRAMMAR_REJECTION" if match["matched"]
                              else "GRAMMAR_NEGATIVE_UNEXPECTED_FAILURE",
                              diagnostic_match=match)
    except Exception as exc:
        result.update(status="INCONCLUSIVE_EXCEPTION",
                      exception_type=type(exc).__name__, exception=str(exc))
    try:
        active_hashes = _tool_hashes(tool)
        active_sha = active_hashes["bin/verifast"]
    except Exception as exc:
        active_sha = None
        active_hashes = None
        result["post_stage_binary_error"] = f"{type(exc).__name__}: {exc}"
    result["post_stage_tool_binary_sha256"] = active_sha
    result["tool_binary_sha256_after"] = active_sha
    result["same_active_binary_after_stage"] = (
        active_sha == identity["tool_binary_sha256"])
    result["tool_hashes_after"] = active_hashes
    result["tool_identity_sha256_after"] = (
        _tool_identity_sha256(active_hashes) if active_hashes is not None else None)
    result["same_active_tool_after_stage"] = (
        active_hashes == identity["tool_hashes"])
    if not result["same_active_binary_after_stage"] or not result["same_active_tool_after_stage"]:
        result.update(status="INCONCLUSIVE_TOOL_BINARY_CHANGED")
    return result


def run(a, c4, tool, tool_receipt, profile, fixture_helper, ghost, ast_gates,
        checked_helper_selector) -> dict[str, Any]:
    """Run isolated Cloud parser controls and return a non-credit record.

    The return is always structured, including guard failures, stage
    exceptions, deadline results, and malformed metadata. No caller gate may
    consume this record as helper-body proof or a caller receipt.
    """
    record: dict[str, Any] = {
        "schema": "a1-ghost-grammar-preflight-v1",
        "status": "GRAMMAR_PREFLIGHT_INCONCLUSIVE",
        "proof_credit": False, "caller_receipt": False,
        "variants": {}}
    try:
        identity = _profile_guard(a, profile, tool_receipt, Path(tool))
        record.update(identity)
        import_sha = _sha_bytes(fixture_helper.OPTION_CLEANUP_IMPORT)
        _need(profile.get("a1_checked_cleanup_import_sha256") == import_sha,
              "standalone Option cleanup import differs from profile pin")
        record["checked_cleanup_import_sha256"] = import_sha
        variants = _source_variants(fixture_helper, ghost)
        root = _workspace_path(Path(a.evidence) / "a1-ghost-grammar",
                               "fresh grammar evidence root")
        _need(not root.exists(), "grammar evidence root must be fresh")
        root.mkdir(parents=True)
        env = c4.clean_env(a, Path(tool))
        _need(isinstance(env, dict) and
              not any(key.startswith(("SORT4_A1_", "O26_WITH_")) for key in env),
              "minimal grammar environment must omit A1 macros and stage controls")
        _need(env.get("RUSTUP_TOOLCHAIN") == profile.get("compiler_toolchain"),
              "minimal grammar stage compiler toolchain differs from profile")
        provider = env.get("SMALLSORT_CLOUD_PROVIDER_PATH")
        _need(isinstance(provider, str) and Path(provider).is_file(),
              "active Cloud provider source path required")
        _workspace_path(Path(provider), "Cloud provider source")
        record["source_identity"] = {
            name: {"verified_source_sha256": case["source_sha256"],
                  "original_source_sha256": case["original_sha256"],
                  "source_pair_sha256": {
                      "verified/lib.rs": case["source_sha256"],
                      "original/lib.rs": case["original_sha256"]}}
            for name, case in variants.items()}
        for name in VARIANTS:
            record["variants"][name] = _one_variant(
                a, c4, Path(tool), fixture_helper, ghost, ast_gates,
                checked_helper_selector, root, name, variants[name], identity, env)
        expected_status = {
            "positive": "GRAMMAR_POSITIVE_PASS",
            "negative_fully_qualified": "EXPECTED_GRAMMAR_REJECTION",
            "negative_import_inside_block": "EXPECTED_GRAMMAR_REJECTION",
        }
        record["status"] = ("GRAMMAR_PREFLIGHT_PASS"
                            if all(record["variants"].get(name, {}).get("status") == status
                                   for name, status in expected_status.items())
                            else "GRAMMAR_PREFLIGHT_INCONCLUSIVE")
        record["evidence_root"] = str(root)
        record["proof_credit"] = False
        record["caller_receipt"] = False
    except Exception as exc:
        record.update(status="GRAMMAR_PREFLIGHT_BLOCKED",
                      error_type=type(exc).__name__, error=str(exc))
    return record
