#!/usr/bin/env python3
"""Cloud-only complete MIR/refinement capture for the pinned generic new source copy.

This records exporter observations. It does not verify a body or link the local
copy's DefId to the external core constructor.
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
import time


HERE = Path(__file__).resolve().parent
NAMES = ("new", "local_new_call", "external_new_call")


def need(ok: bool, why: str) -> None:
    if not ok:
        raise RuntimeError(why)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def provider(cloud_dir: Path) -> dict:
    need(os.environ.get("SMALLSORT_EXECUTION_PROVIDER") == "cloud-build" and
         not os.environ.get("GITHUB_ACTIONS"), "identified Cloud Build required")
    spec = importlib.util.spec_from_file_location("generic_new_cloud_provider",
                                                  cloud_dir / "provider.py")
    need(spec is not None and spec.loader is not None, "Cloud provider absent")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    identity = module.require_supported_provider()
    need(identity["provider"] == "cloud-build", "unsupported provider")
    return identity


def balanced_item(data: str, start: int) -> str:
    need(data[start:start + 1] == "(", "decoded MIR item does not begin with (")
    depth = 0
    quoted = False
    escaped = False
    for pos in range(start, len(data)):
        char = data[pos]
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return data[start:pos + 1]
    raise RuntimeError("decoded MIR item is unbalanced")


def inventory(path: Path) -> dict:
    if not path.is_file():
        return {"observation": "UNOBSERVED", "reason": "decode output absent"}
    raw = path.read_bytes()
    mir = raw.decode("utf-8", errors="replace")
    bodies = []
    for match in re.finditer(r'(?m)^    \( defKind =', mir):
        body = balanced_item(mir, mir.index("(", match.start()))
        path_match = re.search(r'defPath = "([^"\\]*)"', body)
        if path_match is None:
            continue
        lines = body.splitlines()
        bodies.append({
            "def_path": path_match.group(1),
            "body_sha256": sha(body.encode()),
            "body_bytes": len(body.encode()),
            "nested_def_paths_exactly_as_decoded": re.findall(
                r'defPath = "([^"\\]*)"', body)[1:],
            "basic_block_markers": len(re.findall(r'\( basicBlocks =|\( basicBlock =', body)),
            "return_markers": len(re.findall(r'\breturn\b', body, re.I)),
            "unwind_action_lines": [line.strip() for line in lines
                                    if "unwindAction" in line],
            "normal_successor_lines": [line.strip() for line in lines
                                       if any(token in line for token in
                                              ("target =", "goto =", "return ="))],
            "constructor_or_union_lines": [line.strip() for line in lines
                                           if any(token in line for token in
                                                  ("MaybeUninit", "ManuallyDrop", "value", "uninit"))],
            "call_or_substitution_lines": [line.strip() for line in lines
                                           if any(token in line for token in
                                                  ("callee", "genericArgs", "substs", "Call"))],
            "field_or_move_lines": [line.strip() for line in lines
                                    if any(token in line for token in
                                           ("field", "Field", "move", "Move"))],
        })
    names = [b["def_path"] for b in bodies]
    selected = {name: [b for b in bodies if b["def_path"].split("::")[-1] == name]
                for name in NAMES}
    external = selected["external_new_call"]
    local_new = selected["new"]
    return {
        "observation": "OBSERVED", "full_decoded_sha256": sha(raw),
        "full_decoded_bytes": len(raw), "all_def_paths": names,
        "all_bodies": bodies, "selected_body_counts": {name: len(items)
                                                      for name, items in selected.items()},
        "selected_body_observation": {
            name: ("OBSERVED_UNIQUE" if len(items) == 1 else "UNOBSERVED_OR_AMBIGUOUS")
            for name, items in selected.items()},
        "union_declaration_lines": [line.strip() for line in mir.splitlines()
                                    if any(token in line for token in
                                           ("union", "source_copy::MaybeUninit", "ManuallyDrop"))],
        "external_wrapper_nested_target_def_paths": (
            external[0]["nested_def_paths_exactly_as_decoded"] if len(external) == 1
            else "UNOBSERVED"),
        "external_wrapper_call_substitution_lines": (
            external[0]["call_or_substitution_lines"] if len(external) == 1
            else "UNOBSERVED"),
        "local_constructor_field_and_move_lines": (
            local_new[0]["field_or_move_lines"] if len(local_new) == 1
            else "UNOBSERVED"),
        "local_constructor_normal_unwind_lines": (
            (local_new[0]["normal_successor_lines"] +
             local_new[0]["unwind_action_lines"]) if len(local_new) == 1
            else "UNOBSERVED"),
        "interpretation": "Raw candidate lines only; full decoded MIR is retained for review",
    }


def stage(root: Path, name: str, argv: list[str], env: dict,
          source_sha: str, deadline: float, cap_seconds: int,
          input_path: Path | None = None, output_path: Path | None = None) -> dict:
    need(sha((root / "verified/lib.rs").read_bytes()) == source_sha and
         sha((root / "original/lib.rs").read_bytes()) == source_sha,
         f"source changed before {name}")
    remaining = int(deadline - time.time()) - 15
    if remaining <= 0:
        return {"exit": None, "skipped": "deadline reserve"}
    stdout_path = output_path or root / f"{name}.log"
    stderr_path = root / f"{name}-stderr.log" if output_path else None
    started = time.monotonic()
    with stdout_path.open("wb") as out, \
            (input_path.open("rb") if input_path else open(os.devnull, "rb")) as source:
        if stderr_path:
            with stderr_path.open("wb") as err:
                try:
                    code = subprocess.run(argv, cwd=root, env=env, stdin=source,
                                          stdout=out, stderr=err,
                                          timeout=min(remaining, cap_seconds),
                                          check=False).returncode
                except subprocess.TimeoutExpired:
                    code = 124
        else:
            try:
                code = subprocess.run(argv, cwd=root, env=env, stdin=source,
                                      stdout=out, stderr=subprocess.STDOUT,
                                      timeout=min(remaining, cap_seconds),
                                      check=False).returncode
            except subprocess.TimeoutExpired:
                code = 124
    need(sha((root / "verified/lib.rs").read_bytes()) == source_sha and
         sha((root / "original/lib.rs").read_bytes()) == source_sha,
         f"source changed during {name}")
    return {"exit": code, "elapsed_seconds": time.monotonic() - started,
            "argv": argv, "source_exact": True}


def capture(a: argparse.Namespace) -> dict:
    identity = provider(a.cloud_dir)
    root = a.evidence
    need(str(root).startswith("/workspace/") and root.is_dir(),
         "existing /workspace evidence required")
    cert_path = root / "source-certificate.json"
    need(cert_path.is_file() and not (root / "capture-result.json").exists(),
         "fresh prepared source certificate required")
    cert = json.loads(cert_path.read_text())
    source_sha = cert["generated_source_sha256"]
    need(cert["provider"] == identity and
         cert["accepted"] is False and cert["actual_callee_proved"] is False and
         cert["classification"] == "GENERIC_NEW_SOURCE_EQUIVALENCE_CAPTURE_ONLY" and
         sha((root / "verified/lib.rs").read_bytes()) == source_sha and
         sha((root / "original/lib.rs").read_bytes()) == source_sha,
         "prepared source certificate or pair changed")
    tool = a.tool_home
    schema = tool / "src/rust_frontend/vf_mir/vf_mir.capnp"
    tool_paths = {name: tool / name for name in
                  ("bin/vf-rust-mir-exporter", "bin/refinement-checker",
                   "bin/verifast", "src/rust_frontend/vf_mir/vf_mir.capnp")}
    need(all(path.is_file() for path in tool_paths.values()) and
         a.compiler_sysroot.is_dir(), "frozen toolchain input absent")
    tool_sha = {name: sha(path.read_bytes()) for name, path in tool_paths.items()}
    env = os.environ.copy()
    env["RUSTUP_TOOLCHAIN"] = "nightly-2026-09-25"
    stages = {}
    for mode, extra in (("normal", []),
                        ("readonly", ["--vf-rust-mir-exporter:preprocess-readonly"])):
        stages[f"{mode}-export"] = stage(
            root, f"{mode}-export",
            [str(tool / "bin/vf-rust-mir-exporter"), "verified/lib.rs",
             f"--sysroot={a.compiler_sysroot}", "--edition", "2021",
             "--crate-type", "lib", *extra], env, source_sha,
            a.deadline_epoch, 90, output_path=root / f"{mode}-mir.bin")
        if stages[f"{mode}-export"]["exit"] == 0:
            stages[f"{mode}-decode"] = stage(
                root, f"{mode}-decode", ["capnp", "decode", str(schema), "VfMir"],
                env, source_sha, a.deadline_epoch, 60,
                input_path=root / f"{mode}-mir.bin",
                output_path=root / f"{mode}-mir.txt")
        else:
            stages[f"{mode}-decode"] = {"exit": None, "skipped": "export failure"}
    stages["refinement"] = stage(
        root, "refinement", [str(tool / "bin/refinement-checker"),
                             "--rustc-args", "--edition 2021 --crate-type lib",
                             "original/lib.rs", "verified/lib.rs"],
        env, source_sha, a.deadline_epoch, 90)
    mir = {mode: inventory(root / f"{mode}-mir.txt")
           for mode in ("normal", "readonly")}
    all_stages_zero = all(stages[name]["exit"] == 0 for name in
                          ("normal-export", "normal-decode", "readonly-export",
                           "readonly-decode", "refinement"))
    complete_three = all(row.get("selected_body_counts") ==
                         {"new": 1, "local_new_call": 1, "external_new_call": 1}
                         for row in mir.values())
    local_retained_mir_observed = all(
        isinstance(row.get("local_constructor_field_and_move_lines"), list) and
        any("field" in line.lower() for line in row["local_constructor_field_and_move_lines"]) and
        any("move" in line.lower() for line in row["local_constructor_field_and_move_lines"]) and
        isinstance(row.get("local_constructor_normal_unwind_lines"), list) and
        any(any(token in line for token in ("target =", "goto =", "return ="))
            for line in row["local_constructor_normal_unwind_lines"]) and
        any("unwindAction" in line for line in row["local_constructor_normal_unwind_lines"])
        for row in mir.values())
    complete_capture = all_stages_zero and complete_three and local_retained_mir_observed
    result = {
        "classification": ("SOURCE_MIR_CAPTURE_CANDIDATE_REVIEW_REQUIRED"
                           if complete_capture else "INCONCLUSIVE"),
        "complete_capture": complete_capture,
        "accepted": False, "actual_callee_proved": False,
        "actual_callee_linkage": "OPEN",
        "verifast_body_proof": "NOT_RUN_SOURCE_MIR_DIAGNOSTIC_ONLY",
        "verifast_dead_code_check": "UNOBSERVED_NOT_RUN_NOT_DISABLED",
        "generic_union_ownership": "OPAQUE_UNCHANGED",
        "generic_zst_and_panicking_drop": "UNRESTRICTED_SOURCE_DOMAIN_NOT_PROVED",
        "c8_safe_prototype_failure": "PRESERVED_AS_PRIOR_BARRIER",
        "source_certificate_sha256": sha(cert_path.read_bytes()),
        "source_sha256": source_sha, "provider": identity,
        "tool_file_sha256": tool_sha, "stages": stages,
        "complete_three_local_bodies": complete_three,
        "local_constructor_retained_mir_observed": local_retained_mir_observed,
        "mir": mir,
        "raw_artifact_sha256": {path.name: sha(path.read_bytes())
                                for path in root.glob("*mir.*") if path.is_file()},
    }
    (root / "capture-result.json").write_text(json.dumps(result, indent=2,
                                                          sort_keys=True) + "\n")
    return result


def main() -> None:
    p = argparse.ArgumentParser()
    for name in ("cloud-dir", "evidence", "tool-home", "compiler-sysroot"):
        p.add_argument("--" + name, type=Path, required=True)
    p.add_argument("--deadline-epoch", type=float, required=True)
    capture(p.parse_args())


if __name__ == "__main__":
    main()
