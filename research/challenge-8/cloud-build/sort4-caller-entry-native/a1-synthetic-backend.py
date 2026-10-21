"""Cloud-only transport of synthetic VfMir into the unchanged translator.

This adapter intentionally replaces the exporter transport in a disposable tool
facade. Its output has no compiler/refinement/proof provenance. It does not
classify a translator refusal or admit a summary. Importing it is inert.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import re
import time

PHASE = "SORT4-A1-CHECKED-TRAIT-CONTRACT-CLOUD-2026-10-17"
MUTATIONS = frozenset({"binder_collapse", "alpha_valid", "free_region_input",
                       "input_region_swap", "no_F", "remove_fnmut", "remove_output",
                       "change_fnmut", "change_output", "duplicate_impl_method"})

INTENDED_DIAGNOSTICS = {
    "binder_collapse": ("A1 duplicate scoped region alias or identity",),
    "free_region_input": ("A1 free input region in", "A1 free required-item region"),
    "input_region_swap": ("A1 required item lost a distinct input borrow or F",),
    # Removing F from both compiler and HIR generic arrays while retaining it
    # in typeParams now fails the stricter identity-table guard first.
    "no_F": ("A1 HIR/compiler method generic mismatch",
             "A1 type parameter identity table mismatch"),
    "remove_fnmut": ("A1 missing FnMut/Output clause pair",),
    "remove_output": ("A1 missing FnMut/Output clause pair",),
    "duplicate_impl_method": ("SORT4-A1-CONTRACT: full impl method inventory differs",),
}


def _need(ok: bool, why: str) -> None:
    if not ok:
        raise RuntimeError("A1-SYNTHETIC-BACKEND: " + why)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _archive_synthetic_tool_facade(root: Path, facade: Path,
                                   console_sha256: str | None,
                                   wrapper_sha256: str | None) -> Path:
    """Record and unlink only generated facade symlinks; retain regular files."""
    _need(facade.parent == root and facade.name == "synthetic-tool" and
          not facade.is_symlink() and facade.is_dir(),
          "expected generated synthetic tool facade")
    links = []
    directories = [facade]
    bin_dir = facade / "bin"
    for entry in sorted(facade.iterdir(), key=lambda path: path.name):
        if entry.is_symlink():
            links.append((entry, {"path": entry.relative_to(facade).as_posix(),
                                  "target": os.readlink(entry), "kind": "symlink"}))
        elif entry == bin_dir and entry.is_dir():
            directories.append(bin_dir)
    if bin_dir in directories:
        for entry in sorted(bin_dir.iterdir(), key=lambda path: path.name):
            if entry.is_symlink():
                links.append((entry, {"path": entry.relative_to(facade).as_posix(),
                                      "target": os.readlink(entry), "kind": "symlink"}))

    def existing_file_hash(path):
        if path.is_symlink() or not path.is_file():
            return None
        return _sha(path)

    console = bin_dir / "verifast"
    wrapper = bin_dir / "vf-rust-mir-exporter"
    if bin_dir.is_symlink() or not bin_dir.is_dir():
        actual_console_sha = actual_wrapper_sha = None
    else:
        actual_console_sha = existing_file_hash(console)
        actual_wrapper_sha = existing_file_hash(wrapper)
    manifest = {
        "schema": "a1-synthetic-tool-facade-archive-v1",
        "facade_path": "synthetic-tool",
        "facade_retained": True,
        "symlinks_removed_after_recording": False,
        "symlinks": [row for _, row in links],
        "console": {"path": "synthetic-tool/bin/verifast",
                    "sha256": actual_console_sha,
                    "expected_sha256": console_sha256},
        "transport_wrapper": {"path": "synthetic-tool/bin/vf-rust-mir-exporter",
                              "sha256": actual_wrapper_sha,
                              "expected_sha256": wrapper_sha256},
        "targets_dereferenced_for_archive": False,
        "proof_credit": False,
    }
    manifest_path = root / "synthetic-tool-facade-manifest.json"
    _need(not manifest_path.exists() and not manifest_path.is_symlink(),
          "synthetic facade manifest destination already exists")
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                             encoding="utf-8")

    # Readlink targets remain data only; unlink links inside the facade, never follow them.
    for path, row in links:
        _need(path.is_symlink() and os.readlink(path) == row["target"],
              "synthetic facade link changed before cleanup")
        path.unlink()
    manifest["symlinks_removed_after_recording"] = True
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                             encoding="utf-8")
    _need(console_sha256 is None or actual_console_sha == console_sha256,
          "synthetic facade console changed during invocation")
    _need(wrapper_sha256 is None or actual_wrapper_sha == wrapper_sha256,
          "synthetic facade wrapper changed during invocation")
    return manifest_path


def _invoke_with_facade_cleanup(action, cleanup):
    """Always archive after invocation and preserve a primary invocation error."""
    invocation_error = None
    try:
        return action()
    except BaseException as exc:
        invocation_error = exc
        raise
    finally:
        try:
            cleanup()
        except BaseException as cleanup_error:
            if invocation_error is None:
                raise
            invocation_error.add_note(
                f"synthetic facade cleanup also failed: {type(cleanup_error).__name__}: "
                f"{cleanup_error}")


def _workspace(path: Path) -> Path:
    resolved = path.resolve()
    _need(str(resolved).startswith("/workspace/"), "isolated Cloud path required")
    return resolved


def inject(a, c4, mutator, *, tool: Path, fixture: Path, root: Path,
           baseline_decoded: Path, baseline_sha256: str,
           mutation: str, env: dict[str, str], impl_def_index: int | None = None) -> dict:
    """Observe one actual translator invocation on one explicitly synthetic input.

    ``baseline_sha256`` must be the same-Build paired-export observation supplied
    by the caller. This helper verifies byte continuity, not that provenance.
    All source/tool pins and the validity of that observation remain mandatory
    gates in the outer runner. No fake compiler results are produced here.
    """
    _need(os.environ.get("SMALLSORT_EXECUTION_PROVIDER") == "cloud-build" and
          os.environ.get("SORT4_A1_PHASE_ID") == PHASE and
          bool(os.environ.get("CLOUD_BUILD_ID")), "exact authorized Cloud phase")
    _need(env.get("SMALLSORT_EXECUTION_PROVIDER") == "cloud-build" and
          env.get("SORT4_A1_PHASE_ID") == PHASE and
          env.get("SORT4_A1_CHECKED_TRAIT_CONTRACT") == "1" and
          env.get("SORT4_A1_STAGE") == "interface", "interface-only synthetic stage")
    _need(not env.get("SORT4_A1_FORCE_LEGACY_REDIRECT"), "separate redirect control required")
    _need(int(a.deadline_epoch) - int(time.time()) > 30, "shared deadline exhausted")
    tool, fixture, root, baseline_decoded = map(
        _workspace, (tool, fixture, root, baseline_decoded))
    _need(mutation in MUTATIONS, "unknown isolated mutation")
    _need(not root.exists(), "synthetic case destination already exists")
    _need(_sha(baseline_decoded) == baseline_sha256, "baseline decoded input changed")
    fixed = {path: _sha(path) for path in (
        tool / "bin/verifast", tool / "bin/vf-rust-mir-exporter",
        tool / "src/rust_frontend/vf_mir/vf_mir.capnp",
        fixture / "verified/lib.rs", fixture / "original/lib.rs")}
    original = baseline_decoded.read_text(encoding="utf-8", errors="strict")
    _need(len(mutator.parse_records(original)) == 1,
          "one complete VfMir message required; no ignored trailing messages")
    modified, metadata = mutator.mutate_required_fn(
        original, mutation, impl_def_index=impl_def_index)
    _need(metadata.get("synthetic") is True and
          metadata.get("compiler_derived") is False and
          metadata.get("refinement_derived") is False and
          metadata.get("proof_credit") is False, "explicit synthetic provenance required")
    root.mkdir(parents=True)
    decoded, encoded = root / "synthetic-vfmir.txt", root / "synthetic-vfmir.bin"
    decoded.write_text(modified, encoding="utf-8")
    decoded_sha = _sha(decoded)
    schema = tool / "src/rust_frontend/vf_mir/vf_mir.capnp"
    stages = {}
    stages["synthetic-encode"] = c4.stage(
        a, root, "synthetic-encode", ["capnp", "encode", str(schema), "VfMir"],
        env, 30, cwd=fixture, stdin=decoded, stdout=encoded)
    if stages["synthetic-encode"].get("exit") != 0:
        return {"classification": "INCONCLUSIVE_SYNTHETIC_TRANSPORT",
                "stages": stages, "synthetic": True, "proof_credit": False}
    _need(encoded.is_file() and encoded.stat().st_size > 0, "empty synthetic message")

    # rust_fe.run_vf_mir_exporter resolves a sibling of Sys.executable_name.
    # Symlink its unchanged support tree only while the synthetic invocation runs;
    # finalization records the links as data and removes links from this facade.
    # Neither the candidate exporter nor its production source is edited.
    facade = root / "synthetic-tool"
    facade_created = [False]
    facade_manifest = []
    console_sha = _sha(tool / "bin/verifast")
    message_sha = _sha(encoded)
    wrapper_sha = None
    console = facade / "bin" / "verifast"
    wrapper = facade / "bin" / "vf-rust-mir-exporter"
    argv = [str(console), "-focus", "verified/lib.rs:0", "-dump_ast_with_locs",
            str(root / "synthetic-ast.ml"), "-rustc_args", "--edition 2021",
            "verified/lib.rs"]

    def create_and_invoke_translator():
        nonlocal wrapper_sha
        facade.mkdir()
        facade_created[0] = True
        for entry in tool.iterdir():
            if entry.name != "bin":
                (facade / entry.name).symlink_to(entry, target_is_directory=entry.is_dir())
        bin_dir = facade / "bin"
        bin_dir.mkdir()
        for entry in (tool / "bin").iterdir():
            if entry.name not in {"verifast", "vf-rust-mir-exporter"}:
                (bin_dir / entry.name).symlink_to(entry, target_is_directory=entry.is_dir())
        shutil.copy2(tool / "bin/verifast", console)
        _need(_sha(console) == console_sha, "synthetic console differs from candidate")
        # All interpolated values use Python repr in Python source, never shell code.
        wrapper.write_text(
            "#!/usr/bin/python3\nimport hashlib, pathlib, sys\n"
            "if len(sys.argv)<2 or sys.argv[1]!='verified/lib.rs': sys.exit(91)\n"
            "p=pathlib.Path(" + repr(str(encoded)) + ")\n"
            "b=p.read_bytes()\n"
            "if hashlib.sha256(b).hexdigest()!=" + repr(message_sha) + ": sys.exit(92)\n"
            "sys.stdout.buffer.write(b)\n", encoding="ascii")
        wrapper.chmod(0o755)
        wrapper_sha = _sha(wrapper)
        stages["synthetic-translator"] = c4.stage(
            a, root, "synthetic-translator", argv, env, 60, cwd=fixture)
        _need(_sha(console) == console_sha and _sha(tool / "bin/verifast") == console_sha and
              _sha(wrapper) == wrapper_sha and _sha(encoded) == message_sha and
              _sha(decoded) == decoded_sha and _sha(baseline_decoded) == baseline_sha256 and
              all(_sha(path) == digest for path, digest in fixed.items()),
              "synthetic invocation changed its source, tool, input, console or wrapper")
        return stages["synthetic-translator"]

    def archive_facade():
        if facade_created[0]:
            facade_manifest.append(_archive_synthetic_tool_facade(
                root, facade, console_sha, wrapper_sha))

    _invoke_with_facade_cleanup(create_and_invoke_translator, archive_facade)
    return {"classification": "SYNTHETIC_TRANSLATOR_OBSERVATION_UNCLASSIFIED",
            "stages": stages, "mutation": metadata,
            "build_id": os.environ["CLOUD_BUILD_ID"],
            "baseline_decoded_sha256": baseline_sha256,
            "decoded_input_sha256": decoded_sha,
            "synthetic_message_sha256": message_sha,
            "source_pair_sha256": {
                "verified": _sha(fixture / "verified/lib.rs"),
                "original": _sha(fixture / "original/lib.rs")},
            "console_sha256": console_sha, "transport_wrapper_sha256": wrapper_sha,
            "facade_manifest_path": str(facade_manifest[0]),
            "facade_manifest_sha256": _sha(facade_manifest[0]),
            "ast_path": str(root / "synthetic-ast.ml"),
            "synthetic": True, "compiler_derived": False,
            "refinement_derived": False, "summary_available": False,
            "proof_credit": False}


def classify(observation: dict, *, mutation: str, verifier_log: str | None) -> dict:
    """Classify the observed translator stage for a synthetic-only message.

    A matching expected string without a terminal translator invocation is
    insufficient. Alpha renaming is representation-only and requires an
    actual successful translation plus the emitted AST. No result grants
    compiler, refinement, or proof credit.
    """
    result = {"classification": "INCONCLUSIVE_SYNTHETIC_TRANSLATOR",
              "mutation": mutation, "proof_credit": False,
              "compiler_derived": False, "refinement_derived": False}
    stages = observation.get("stages", {})
    translator = stages.get("synthetic-translator")
    ast_path = Path(observation.get("ast_path", ""))
    if not isinstance(translator, dict) or not isinstance(translator.get("exit"), int):
        return {**result, "reason": "translator stage did not reach a terminal exit"}
    if mutation == "alpha_valid":
        if translator["exit"] == 0 and ast_path.is_file() and ast_path.stat().st_size > 0:
            return {**result, "classification": "SYNTHETIC_REPRESENTATION_ACCEPTED",
                    "stage": "interface", "exit": 0,
                    "ast_sha256": _sha(ast_path), "summary_available": False}
        return {**result, "reason": "alpha-renamed interface did not translate successfully"}
    if verifier_log is None or not isinstance(verifier_log, str):
        return {**result, "reason": "translator diagnostic unavailable"}
    diagnostics = [line for line in verifier_log.splitlines()
                   if "error:" in line or line.startswith(("Fatal error:", "error:"))]
    first = diagnostics[0] if diagnostics else None
    accepted = INTENDED_DIAGNOSTICS.get(mutation, ())
    if mutation == "no_F":
        # This mutation is classified only when the translator terminated at
        # the interface stage and emitted one exact recognized refusal. A
        # later unrelated diagnostic or a message that merely embeds the
        # expected text must not turn another failure into the intended one.
        if (translator.get("classification") != "TERMINAL" or
                type(translator.get("exit")) is not int):
            return {**result, "reason": "synthetic translator stage is not terminal",
                    "stage": "interface", "exit": translator["exit"]}
        if len(diagnostics) != 1:
            return {**result, "reason": "expected exactly one no_F translator diagnostic",
                    "stage": "interface", "exit": translator["exit"],
                    "first_diagnostic": first, "diagnostic_count": len(diagnostics)}
        match = (re.fullmatch(
            r"verified/lib\.rs\([1-9][0-9]*,[1-9][0-9]*(?:-[1-9][0-9]*(?:,[1-9][0-9]*)?)?\): error: (.+)",
            first) if first is not None else None)
        message = match.group(1) if match else None
        if translator["exit"] != 0 and message in accepted:
            return {**result, "classification": "SYNTHETIC_REFUSAL_OBSERVED",
                    "stage": "interface", "exit": translator["exit"],
                    "first_diagnostic": first, "diagnostic_match": message,
                    "summary_available": False}
        return {**result, "reason": "observed terminal diagnostic differs from intended refusal",
                "stage": "interface", "exit": translator["exit"],
                "first_diagnostic": first}
    if translator["exit"] != 0 and first and any(text in first for text in accepted):
        return {**result, "classification": "SYNTHETIC_REFUSAL_OBSERVED",
                "stage": "interface", "exit": translator["exit"],
                "first_diagnostic": first, "diagnostic_match": next(
                    text for text in accepted if text in first),
                "summary_available": False}
    return {**result, "reason": "observed terminal diagnostic differs from intended refusal",
            "stage": "interface", "exit": translator["exit"],
            "first_diagnostic": first}
