"""Cloud-only transport of synthetic VfMir into the unchanged translator.

This adapter intentionally replaces the exporter transport in a disposable tool
facade. Its output has no compiler/refinement/proof provenance. It does not
classify a translator refusal or admit a summary. Importing it is inert.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import shutil
import time

PHASE = "SORT4-A1-CHECKED-TRAIT-CONTRACT-CLOUD-2026-10-17"
MUTATIONS = frozenset({"binder_collapse", "alpha_valid", "free_region_input",
                       "input_region_swap", "no_F", "remove_fnmut", "remove_output",
                       "change_fnmut", "change_output", "duplicate_impl_method"})


def _need(ok: bool, why: str) -> None:
    if not ok:
        raise RuntimeError("A1-SYNTHETIC-BACKEND: " + why)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
    # Copy the console bytes, symlink its unchanged support tree, and place a
    # bounded replay program only at that sibling in this disposable facade.
    # Neither the built candidate exporter nor its production source is edited.
    facade = root / "synthetic-tool"
    facade.mkdir()
    for entry in tool.iterdir():
        if entry.name != "bin":
            (facade / entry.name).symlink_to(entry, target_is_directory=entry.is_dir())
    bin_dir = facade / "bin"
    bin_dir.mkdir()
    for entry in (tool / "bin").iterdir():
        if entry.name not in {"verifast", "vf-rust-mir-exporter"}:
            (bin_dir / entry.name).symlink_to(entry, target_is_directory=entry.is_dir())
    console = bin_dir / "verifast"
    shutil.copy2(tool / "bin/verifast", console)
    console_sha = _sha(tool / "bin/verifast")
    _need(_sha(console) == console_sha, "synthetic console differs from candidate")
    message_sha = _sha(encoded)
    wrapper = bin_dir / "vf-rust-mir-exporter"
    # All interpolated values use Python repr in Python source, never shell code.
    wrapper.write_text(
        "#!/usr/bin/python3\nimport hashlib, pathlib, sys\n"
        "if len(sys.argv)<2 or sys.argv[1]!='verified/lib.rs': sys.exit(91)\n"
        "p=pathlib.Path(" + repr(str(encoded)) + ")\n"
        "b=p.read_bytes()\n"
        "if hashlib.sha256(b).hexdigest()!=" + repr(message_sha) + ": sys.exit(92)\n"
        "sys.stdout.buffer.write(b)\n", encoding="ascii")
    wrapper.chmod(0o755)
    argv = [str(console), "-focus", "verified/lib.rs:0", "-dump_ast_with_locs",
            str(root / "synthetic-ast.ml"), "-rustc_args", "--edition 2021",
            "verified/lib.rs"]
    stages["synthetic-translator"] = c4.stage(
        a, root, "synthetic-translator", argv, env, 60, cwd=fixture)
    _need(_sha(console) == console_sha and _sha(tool / "bin/verifast") == console_sha and
          _sha(encoded) == message_sha and _sha(baseline_decoded) == baseline_sha256 and
          all(_sha(path) == digest for path, digest in fixed.items()),
          "synthetic invocation changed its source, tool, input or console")
    return {"classification": "SYNTHETIC_TRANSLATOR_OBSERVATION_UNCLASSIFIED",
            "stages": stages, "mutation": metadata,
            "baseline_decoded_sha256": baseline_sha256,
            "synthetic_message_sha256": message_sha,
            "console_sha256": console_sha, "transport_wrapper_sha256": _sha(wrapper),
            "ast_path": str(root / "synthetic-ast.ml"),
            "synthetic": True, "compiler_derived": False,
            "refinement_derived": False, "summary_available": False,
            "proof_credit": False}
