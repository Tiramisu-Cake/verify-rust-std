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
BASELINE_SOURCE = "8629849c2d2ddde1eeb90fadb6a151dc52e626385578f89f0d86fce842c61eb8"
ORIGINAL_SOURCE = "466882d74de217766ed8d5c583596c173df47f0e6bd40da7cb1a4c931d7265a5"
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


def source_preflight(baseline: Path, proof: Path, evidence: Path) -> dict:
    """Generate both exact source pairs before any tool installation/build."""
    if git_sha(baseline) != BASELINE_SHA or git_sha(proof) == BASELINE_SHA:
        raise ValueError("O26 preflight proof checkout identities differ")
    if (evidence / "source-preflight.json").exists():
        raise ValueError("refusing existing O26 source preflight")
    root = evidence / "preflight"
    root.mkdir(parents=True, exist_ok=False)
    rows = {}
    for label, repo in (("baseline", baseline), ("candidate", proof)):
        cap = load_capture(repo, "preflight_" + label)
        cap.clear_semantic_opt_ins()
        out = root / label
        source = cap.PREP.write_case(repo, out)
        case = out / cap.PREP.CASE_NAME
        original = case / "original/lib.rs"
        verified = case / "verified/lib.rs"
        if (source["ghost_strip_identity"] is not True or
                source["original_sha256"] != sha(original.read_bytes()) or
                source["verified_sha256"] != sha(verified.read_bytes()) or
                len(source["source_order"]) != 9):
            raise ValueError(f"{label} preflight source integrity failed")
        rows[label] = {
            "proof_sha": git_sha(repo),
            "source": source,
            "original_file": str(original.relative_to(evidence)),
            "verified_file": str(verified.relative_to(evidence)),
            "source_generation_complete": True,
            "compiler_or_verifier_invoked": False,
        }
    if (rows["baseline"]["source"]["verified_sha256"] != BASELINE_SOURCE or
            rows["candidate"]["source"]["verified_sha256"] == BASELINE_SOURCE or
            rows["baseline"]["source"]["original_sha256"] != ORIGINAL_SOURCE or
            rows["candidate"]["source"]["original_sha256"] != ORIGINAL_SOURCE):
        raise ValueError("historical/candidate exact source relationship changed")
    result = {"classification": "O26_SOURCE_ONLY_PREFLIGHT",
              "preflight_complete": True, "compiler_or_verifier_invoked": False,
              "cases": rows}
    (evidence / "source-preflight.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def compare_capture(evidence: Path, label: str, output: Path) -> dict:
    preflight = json.loads((evidence / "source-preflight.json").read_text())
    prior = preflight["cases"][label]
    capture = evidence / "cases" / label / "capture"
    summary = json.loads((capture / "summary.json").read_text())
    source = summary["source"]
    case = capture / "nine-body-a1-owned-forget"
    same = (source["source_order"] == prior["source"]["source_order"] and
            source["original_sha256"] == prior["source"]["original_sha256"] and
            source["verified_sha256"] == prior["source"]["verified_sha256"] and
            (case / "original/lib.rs").read_bytes() ==
                (evidence / prior["original_file"]).read_bytes() and
            (case / "verified/lib.rs").read_bytes() ==
                (evidence / prior["verified_file"]).read_bytes())
    result = {"label": label, "exact_preflight_source_pair_reproduced": same,
              "original_sha256": source["original_sha256"],
              "verified_sha256": source["verified_sha256"]}
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if not same:
        raise ValueError(f"{label} source pair changed after preflight")
    return result


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
    a = sub.add_parser("preflight")
    for name in ("baseline", "proof", "evidence"):
        a.add_argument("--" + name, type=Path, required=True)
    a = sub.add_parser("compare")
    a.add_argument("--evidence", type=Path, required=True)
    a.add_argument("--label", choices=("baseline", "candidate"), required=True)
    a.add_argument("--output", type=Path, required=True)
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
    if args.mode == "preflight":
        result = source_preflight(args.baseline, args.proof, args.evidence)
        print(json.dumps({"classification": result["classification"],
                          "preflight_complete": True}), flush=True)
        return
    if args.mode == "compare":
        print(json.dumps(compare_capture(args.evidence, args.label,
                                         args.output), sort_keys=True), flush=True)
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
