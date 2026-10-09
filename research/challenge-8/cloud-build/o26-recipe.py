#!/usr/bin/env python3
"""Cloud-only O26 source capture and historical-certificate diagnostic.

This file adapts only provider guards in disposable proof checkouts. It neither
refreshes a source fingerprint nor installs a new verifier rule.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys


BASELINE_SHA = "c19e4c50470d32199178d5229a2819554fc6b2f1"
PROVIDER_SHA = "771970340f4fa928063cfa25db451535eb60ee1b246ef63c3cda4689842be616"
ROOT = Path("research/challenge-8")
OVERLAYS = (
    ROOT / "overnight-assume-actual/prepare.py",
    ROOT / "overnight-assume-actual/capture.py",
    ROOT / "overnight-guard-actual/prepare-actual-nested-drop.py",
    ROOT / "overnight-helper/prepare-actual-owner-linked.py",
    ROOT / "overnight-helper/prepare-actual-owner-projection.py",
)
GUARD = (
    '(os.environ.get("GITHUB_ACTIONS"),\n'
    '             os.environ.get("RUNNER_ENVIRONMENT"),\n'
    '             os.environ.get("RUNNER_OS")) ==\n'
    '            ("true", "github-hosted", "Linux")'
)
GUARD_VARIANTS = (
    GUARD,
    '(os.environ.get("GITHUB_ACTIONS"),\n'
    '                  os.environ.get("RUNNER_ENVIRONMENT"),\n'
    '                  os.environ.get("RUNNER_OS")) ==\n'
    '                 ("true", "github-hosted", "Linux")',
    '(os.environ.get("GITHUB_ACTIONS"),\n'
    '                   os.environ.get("RUNNER_ENVIRONMENT"),\n'
    '                   os.environ.get("RUNNER_OS")) ==\n'
    '                  ("true", "github-hosted", "Linux")',
    'os.environ.get("GITHUB_ACTIONS") == "true" and\n'
    '            os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted" and\n'
    '            os.environ.get("RUNNER_OS") == "Linux"',
)
HELPER = '''\n\ndef _o26_cloud_provider_ok() -> bool:
    provider_path = Path(__file__).resolve().parents[1] / "cloud-build/provider.py"
    spec = importlib.util.spec_from_file_location("smallsort_o26_provider", provider_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("O26 provider module missing")
    provider = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(provider)
    return provider.require_supported_provider()["provider"] == "cloud-build"
'''


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_sha(repo: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()


def overlay(repo: Path, provider: Path, out: Path) -> dict:
    source = provider.read_bytes()
    if sha(source) != PROVIDER_SHA:
        raise ValueError("Cloud provider module pin differs")
    destination = repo / ROOT / "cloud-build/provider.py"
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and destination.read_bytes() != source:
        raise ValueError("proof checkout contains another provider module")
    destination.write_bytes(source)
    rows = []
    for rel in OVERLAYS:
        path = repo / rel
        before = path.read_text()
        committed = subprocess.check_output(
            ["git", "-C", str(repo), "show", f"HEAD:{rel.as_posix()}"])
        if before.encode() != committed:
            raise ValueError(f"overlay source differs from committed blob: {rel}")
        found = [guard for guard in GUARD_VARIANTS if before.count(guard) == 1]
        if len(found) != 1:
            raise ValueError(f"provider guard not unique: {rel}")
        after = before.replace(found[0], "_o26_cloud_provider_ok()", 1)
        anchor = "from pathlib import Path\n"
        if after.count(anchor) != 1 or "import importlib.util" not in after:
            raise ValueError(f"provider helper insertion anchor differs: {rel}")
        after = after.replace(anchor, anchor + HELPER, 1)
        compile(after, str(rel), "exec")
        path.write_text(after)
        rows.append({
            "path": rel.as_posix(), "original_sha256": sha(committed),
            "cloud_overlay_sha256": sha(after.encode()), "guard_only": True,
            "diff": "".join(difflib.unified_diff(
                before.splitlines(True), after.splitlines(True),
                fromfile=rel.as_posix() + ".committed",
                tofile=rel.as_posix() + ".cloud-guard")),
        })
    record = {"proof_sha": git_sha(repo), "provider_sha256": PROVIDER_SHA,
              "files": rows}
    out.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    return record


def load_capture(repo: Path, label: str):
    path = repo / ROOT / "overnight-assume-actual/capture.py"
    spec = importlib.util.spec_from_file_location("o26_capture_" + label, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("nine-body capture unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def proof_stage(repo: Path, case: Path, tool_home: Path, schema: Path,
                sysroot: Path, deadline: int, name: str, label: str) -> dict:
    cap = load_capture(repo, label)
    cap.clear_semantic_opt_ins()
    controls = {
        "SORT4_ACTUAL_OWNER_REPO_ROOT": str(repo),
        "SORT4_ACTUAL_OWNER_ADMISSION": "1",
        "SORT4_ACTUAL_OWNER_NINE_ADMISSION": "1",
        "SORT4_ACTUAL_NESTED_H2_REPO_ROOT": str(repo),
        "SORT4_ACTUAL_FORGET_OWN_REPO_ROOT": str(repo),
        "SORT4_A1_NINE_REPO_ROOT": str(repo),
    }
    try:
        os.environ.update(controls)
        args = argparse.Namespace(tool_home=tool_home, schema=schema,
                                  compiler_sysroot=str(sysroot),
                                  deadline_epoch=deadline)
        return cap.LINK.stage(case, name, [
            str(tool_home / "bin/verifast"), "-rustc_args", "--edition 2021",
            "-verbose", "1", "verified/lib.rs"], args,
            gates=True, pointer_drop=True, cap_seconds=110)
    finally:
        for key in controls:
            os.environ.pop(key, None)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="mode", required=True)
    a = sub.add_parser("overlay")
    for name in ("baseline", "proof", "provider", "evidence"):
        a.add_argument("--" + name, type=Path, required=True)
    a = sub.add_parser("proof")
    for name in ("repo", "case", "tool-home", "schema", "compiler-sysroot", "output"):
        a.add_argument("--" + name, type=Path, required=True)
    a.add_argument("--deadline-epoch", type=int, required=True)
    a.add_argument("--name", choices=("historical-proof", "stale-certificate"), required=True)
    args = p.parse_args()
    if args.mode == "overlay":
        if git_sha(args.baseline) != BASELINE_SHA:
            raise SystemExit("baseline proof SHA mismatch")
        if git_sha(args.proof) == BASELINE_SHA:
            raise SystemExit("current proof must be selected separately")
        args.evidence.mkdir(parents=True, exist_ok=True)
        for label, repo in (("baseline", args.baseline), ("candidate", args.proof)):
            overlay(repo, args.provider, args.evidence / f"{label}-provider-overlay.json")
        return
    result = proof_stage(args.repo, args.case, args.tool_home, args.schema,
                         args.compiler_sysroot, args.deadline_epoch,
                         args.name, args.name.replace("-", "_"))
    args.output.write_text(json.dumps({"proof_sha": git_sha(args.repo),
        "stage": result, "actual_verification_accepted": False},
        indent=2, sort_keys=True) + "\n")
    print(json.dumps({"name": args.name, "exit": result.get("exit"),
                      "source_unchanged": result.get("source_unchanged")}), flush=True)


if __name__ == "__main__":
    main()
