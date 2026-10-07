#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted-only first-causal S6 transfer diagnostic; never confers acceptance.

Each requested family has one independent, canonical positive fixture. Full
NORMAL and readonly MIR, stage logs, source hashes and the first verifier error
are saved even when the old exact typed MIR certificate correctly rejects.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import traceback
from pathlib import Path


PROFILE = "experimental-s6-26.10-v1"
FAMILIES = ("constructor", "as_mut_ptr", "intrinsic_ptr", "intrinsic_mu", "pointer_drop")
SCRIPTS = {
    "constructor": "check-maybeuninit-new-pointer.py",
    "as_mut_ptr": "check-select-pointer.py",
    "intrinsic": "check-select-pointer-intrinsics.py",
    "pointer_drop": "check-pointer-drop.py",
    "drop_source": "prepare-pointer-drop-diagnostic.py",
}


def load(name: str):
    path = Path(__file__).with_name(SCRIPTS[name])
    spec = importlib.util.spec_from_file_location("s6_2610_" + name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record_normal_export(case: Path, args: argparse.Namespace) -> dict:
    source = case / "verified/lib.rs"
    before = sha(source)
    env = os.environ.copy()
    env["PATH"] = str(args.tool_home / "bin") + os.pathsep + env.get("PATH", "")
    exporter = [
        "timeout", "--signal=TERM", "--kill-after=10s", "300s",
        str(args.tool_home / "bin/vf-rust-mir-exporter"), "verified/lib.rs",
        f"--sysroot={args.compiler_sysroot}", "--edition", "2021",
        "--crate-type", "lib",
    ]
    with (case / "compiler-mir-normal.bin").open("wb") as out, \
            (case / "normal-export.log").open("wb") as err:
        exported = subprocess.run(exporter, cwd=case, env=env, stdout=out,
                                  stderr=err, check=False).returncode
    decoded = 125
    if exported == 0:
        with (case / "compiler-mir-normal.bin").open("rb") as inp, \
                (case / "compiler-mir-normal.txt").open("wb") as out, \
                (case / "normal-decode.log").open("wb") as err:
            decoded = subprocess.run([
                "timeout", "--signal=TERM", "--kill-after=10s", "300s",
                "capnp", "decode", str(args.schema), "VfMir",
            ], cwd=case, env=env, stdin=inp, stdout=out, stderr=err,
                check=False).returncode
    else:
        (case / "compiler-mir-normal.txt").write_bytes(b"")
        (case / "normal-decode.log").write_text("not run: NORMAL export failed\n")
    after = sha(source)
    result = {
        "export_exit": exported, "decode_exit": decoded,
        "source_sha256_before": before, "source_sha256_after": after,
        "source_unchanged": before == after,
        "normal_mir_sha256": sha(case / "compiler-mir-normal.bin"),
        "normal_mir_text_sha256": sha(case / "compiler-mir-normal.txt"),
    }
    (case / "normal-export-summary.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def first_causal(case: Path, result: dict, normal: dict) -> dict:
    log = (case / "verifast.log").read_text(errors="replace")
    fatal = [line for line in log.splitlines() if line.startswith("Fatal error:")]
    errors = [line for line in log.splitlines() if ": error:" in line]
    expected_certificate = bool(fatal and
        ("certificate mismatch" in fatal[0] or
         "unsupported certified union shape" in fatal[0]))
    return {
        "status": "DIAGNOSTIC_ONLY",
        "accepted_component": False,
        "normal": normal,
        "readonly_and_proof": result,
        "first_fatal": fatal[0] if fatal else None,
        "first_proof_error": errors[0] if errors else None,
        "strict_mir_certificate_rejected": expected_certificate,
        "readonly_mir_sha256": sha(case / "compiler-mir.bin"),
        "readonly_mir_text_sha256": sha(case / "compiler-mir.txt"),
        "full_verifier_exit": result.get("verifast_exit"),
        "source_integrity": result.get("stage_integrity"),
    }


def prepare(family: str, case: Path, repo: Path, constructor, source_cert: dict):
    if family == "constructor":
        constructor.prepare_constructor_case(case.parent, source_cert,
                                             case.name, "positive")
    elif family == "as_mut_ptr":
        module = load("as_mut_ptr")
        body, cert = module.source_certificate(repo, constructor)
        module.make_case(case, body, cert, constructor, "unknown")
        return cert
    elif family in ("intrinsic_ptr", "intrinsic_mu"):
        module = load("intrinsic")
        cert = module.source_certificate(repo, constructor)
        kind = "ptr" if family.endswith("ptr") else "mu"
        variant = "symbolic" if kind == "ptr" else "unknown"
        module.make_case(case, kind, variant, cert, constructor)
        return cert
    elif family == "pointer_drop":
        module = load("pointer_drop")
        diagnostic = load("drop_source")
        body, cert = diagnostic.source_certificate(repo, constructor)
        module.make_case(case, "initialized", cert, body, constructor)
        return cert
    else:
        raise ValueError(f"unknown family: {family}")
    return source_cert


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool-home", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--compiler-sysroot", required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--families", nargs="+", choices=FAMILIES,
                        default=list(FAMILIES))
    args = parser.parse_args()
    if (os.environ.get("GITHUB_ACTIONS"),
        os.environ.get("RUNNER_ENVIRONMENT"),
        os.environ.get("RUNNER_OS")) != ("true", "github-hosted", "Linux"):
        raise SystemExit("S6 executable diagnostics require GitHub-hosted Linux")
    if os.environ.get("SORT4_SELECT_PROFILE") != PROFILE:
        raise SystemExit(f"SORT4_SELECT_PROFILE must be {PROFILE}")
    repo = Path(__file__).resolve().parents[3]
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=False)
    identity = {
        "source_sha": subprocess.check_output(
            ["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip(),
        "patch_sha256": sha(Path(__file__).with_name(
            "verifast-s6-26.10-candidate.patch")),
        "console_sha256": sha(args.tool_home / "bin/verifast"),
        "exporter_sha256": sha(args.tool_home / "bin/vf-rust-mir-exporter"),
        "refiner_sha256": sha(args.tool_home / "bin/refinement-checker"),
        "schema_sha256": sha(args.schema),
        "compiler_sysroot": args.compiler_sysroot,
    }
    (evidence / "identity.json").write_text(
        json.dumps(identity, indent=2, sort_keys=True) + "\n")
    constructor = load("constructor")
    source_cert = constructor.certify_repository_sources(repo)
    (evidence / "constructor-source-certificate.json").write_text(
        json.dumps(source_cert, indent=2, sort_keys=True) + "\n")
    rows = {}
    for family in args.families:
        case = evidence / family
        try:
            cert = prepare(family, case, repo, constructor, source_cert)
            (case / "s6-source-certificate.json").write_text(
                json.dumps(cert, indent=2, sort_keys=True) + "\n")
            normal = record_normal_export(case, args)
            env_keys = ("SORT4_SELECT_INTRINSIC_REPO_ROOT", "SORT4_POINTER_DROP_REPO_ROOT")
            saved = {key: os.environ.get(key) for key in env_keys}
            if family.startswith("intrinsic"):
                os.environ[env_keys[0]] = str(repo)
            if family == "pointer_drop":
                os.environ[env_keys[1]] = str(repo)
            try:
                result = constructor.run_case(case, args.schema, args.tool_home,
                    args.compiler_sysroot, repo, family, "diagnostic",
                    certificate_mode=True)
            finally:
                for key, value in saved.items():
                    if value is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = value
            row = first_causal(case, result, normal)
            (case / "s6-diagnostic.json").write_text(
                json.dumps(row, indent=2, sort_keys=True) + "\n")
            rows[family] = {
                "normal_export_exit": normal["export_exit"],
                "normal_decode_exit": normal["decode_exit"],
                "readonly_export_exit": result.get("exporter_exit"),
                "readonly_decode_exit": result.get("decode_exit"),
                "refinement_exit": result.get("refinement_exit"),
                "full_verifier_exit": result.get("verifast_exit"),
                "first_fatal": row["first_fatal"],
                "first_proof_error": row["first_proof_error"],
                "strict_mir_certificate_rejected": row["strict_mir_certificate_rejected"],
            }
        except Exception as exc:
            case.mkdir(exist_ok=True)
            (case / "harness-exception.txt").write_text(traceback.format_exc())
            rows[family] = {
                "status": "INCONCLUSIVE_SETUP_OR_HARNESS",
                "exception": f"{type(exc).__name__}: {exc}",
            }
        (evidence / "summary.json").write_text(json.dumps({
            "profile": PROFILE, "status": "DIAGNOSTIC_ONLY",
            "accepted_component": False, "requested_families": args.families,
            "identity": identity,
            "completed_families": rows,
            "not_run": [name for name in args.families if name not in rows],
        }, indent=2, sort_keys=True) + "\n")
    print(json.dumps(rows, sort_keys=True))


if __name__ == "__main__":
    main()
