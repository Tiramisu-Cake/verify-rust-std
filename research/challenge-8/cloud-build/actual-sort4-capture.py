#!/usr/bin/env python3
"""Cloud-only, source-exact capture of the actual sort4 first-call boundary.

This is a diagnostic driver. It changes only hosted-provider guards in a
disposable proof checkout; it does not enable a verifier semantic component.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time


RESEARCH = Path("research/challenge-8")
DEPENDENCIES = {
    "overnight-sort4/capture.py": "0d993e8c36cb7684eb509e8efcfb9553b07e92e87885f4ae430269c4cb2a6060",
    "overnight-callback/probe.py": "80a39a7505748a4f20a9115a801d44e0c5d9f9a11554a0d8744963d8140fdc33",
    "overnight-callback/prepare-actual-sort4-first-call.py": "869f1a4f98cd544e1baa97c168fb74f833925b3795aa1ec718807cc8483298e0",
    "overnight-callback/admit-actual-sort4-first-call.py": "ef724694974363a4da3d65d0e8d22e8dfbc028b9f332c8b14b026636e6f49919",
    "overnight-callback/callback-cases.rs": "2701eaf2609bea993fa6a464bd7d2467bf1df7d155fbf240229f5db660b9b1a3",
    "overnight-callback/join-four-owned-cells.rs": "b35dd247226a3dd88ab8f22a50141896b5556d3a96bec1e982077060d0731e66",
}
PROVIDER_SHA = "771970340f4fa928063cfa25db451535eb60ee1b246ef63c3cda4689842be616"
O24_VERIFIED = "fddb6f1a0a90948042c99fd1037b7e939586c9e7b9e46a63367a7d876e04ccc9"
O24_ORIGINAL = "3602050e45025745d80b308802be9e552310959abcee4b95bfe8c24f8ca04b72"
O24_GRAPHS = {
    "normal": "667e43477674d9e834b462b612f498af81598ec18622f0a60337ae4fdc6b017d",
    "readonly": "925b05a8c2bb66be8ad5a7f091f8232d9e930782b5ca01067cf7d1bec349f5b5",
}
OLD_GUARD = (
    '    need(os.environ.get("GITHUB_ACTIONS") == "true" and\n'
    '         os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted" and\n'
    '         os.environ.get("RUNNER_OS") == "Linux",\n'
)
NEW_GUARD = (
    '    spec = importlib.util.spec_from_file_location(\n'
    '        "smallsort_sort4_provider", os.environ["SMALLSORT_CLOUD_PROVIDER_PATH"])\n'
    '    need(spec is not None and spec.loader is not None,\n'
    '         "Cloud provider module unavailable")\n'
    '    provider = importlib.util.module_from_spec(spec)\n'
    '    spec.loader.exec_module(provider)\n'
    '    need(provider.require_supported_provider()["provider"] == "cloud-build",\n'
    '         "identified Cloud Build required")\n'
)
PREPARE_OLD = OLD_GUARD + '         "sort4 first-call preparation requires GitHub-hosted Linux")'
ADMIT_OLD = OLD_GUARD + '         "first-call MIR admission requires GitHub-hosted Linux")'
NEW_GUARD_IMPORT = "import importlib.util\n"
SEMANTIC_OPT_INS = (
    "SORT4_HRTB_OUTPUT", "SORT4_HRTB_OUTPUT_TARGETS",
    "SORT4_STRICT_LFT_CUT", "SORT4_CALLBACK_UNWIND",
)


def need(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha(path: Path) -> str:
    return sha(path.read_bytes())


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def load_provider(path: Path):
    spec = importlib.util.spec_from_file_location("smallsort_sort4_provider_driver", path)
    need(spec is not None and spec.loader is not None, "Cloud provider module unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def overlay_guards(proof_root: Path, provider: Path, evidence: Path) -> list[dict]:
    """Replace only two obsolete GitHub identity guards in the disposable tree."""
    rows = []
    for relative, old in (
        ("overnight-callback/prepare-actual-sort4-first-call.py", PREPARE_OLD),
        ("overnight-callback/admit-actual-sort4-first-call.py", ADMIT_OLD),
    ):
        path = proof_root / RESEARCH / relative
        before = path.read_bytes()
        need(sha(before) == DEPENDENCIES[relative], f"frozen dependency differs: {relative}")
        old_bytes = old.encode()
        need(before.count(old_bytes) == 1 and before.count(NEW_GUARD_IMPORT.encode()) == 0,
             f"provider guard is not unique: {relative}")
        after = before.replace(old_bytes, NEW_GUARD.encode(), 1)
        # The replacement uses one new import; all proof/source logic is byte-identical.
        after = after.replace(b"import hashlib\n", b"import hashlib\n" + NEW_GUARD_IMPORT.encode(), 1)
        need(after.count(NEW_GUARD.encode()) == 1 and
             after.replace(NEW_GUARD.encode(), old_bytes, 1).replace(
                 b"import hashlib\n" + NEW_GUARD_IMPORT.encode(), b"import hashlib\n", 1) == before,
             f"provider overlay changed more than its guard: {relative}")
        path.write_bytes(after)
        rows.append({
            "path": str(RESEARCH / relative), "base_sha256": sha(before),
            "overlay_sha256": sha(after), "provider_sha256": file_sha(provider),
            "guard_only": True,
            "diff": "".join(difflib.unified_diff(
                before.decode().splitlines(True), after.decode().splitlines(True),
                fromfile=relative + ".base", tofile=relative + ".cloud")),
        })
    write_json(evidence / "sort4-provider-overlay.json", {"overlays": rows})
    return rows


def run_stage(name: str, command: list[str], cwd: Path, evidence: Path,
              env: dict[str, str], deadline: int, cap: int,
              source_paths: tuple[Path, ...] = ()) -> dict:
    before = {str(p): file_sha(p) for p in source_paths}
    seconds = min(cap, deadline - int(time.time()) - 15)
    if seconds <= 0:
        return {"exit": None, "skipped": "deadline and upload reserve"}
    log = evidence / f"{name}.log"
    resources = evidence / f"{name}-resources.txt"
    with log.open("wb") as output:
        result = subprocess.run(
            ["/usr/bin/time", "-v", "-o", str(resources), "timeout",
             "--signal=TERM", "--kill-after=10s", f"{seconds}s", *command],
            cwd=cwd, env=env, stdout=output, stderr=subprocess.STDOUT,
            check=False).returncode
    after = {str(p): file_sha(p) for p in source_paths}
    row = {"argv": command, "exit": result, "timeout_seconds": seconds,
           "log": log.name, "resources": resources.name,
           "source_before": before, "source_after": after,
           "source_integrity": before == after}
    write_json(evidence / f"{name}-stage.json", row)
    return row


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("proof-root", "cloud-dir", "tool-home", "schema",
                 "compiler-sysroot", "evidence"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--deadline-epoch", type=int, required=True)
    args = parser.parse_args()
    root, cloud, tool, schema, sysroot, evidence = (
        args.proof_root.resolve(), args.cloud_dir.resolve(),
        args.tool_home.resolve(), args.schema.resolve(),
        args.compiler_sysroot.resolve(), args.evidence.resolve())
    need(not evidence.exists(), "fresh evidence directory required")
    need(file_sha(cloud / "provider.py") == PROVIDER_SHA, "Cloud provider pin differs")
    provider = load_provider(cloud / "provider.py").require_supported_provider()
    need(provider["provider"] == "cloud-build" and not os.environ.get("GITHUB_ACTIONS"),
         "identified Cloud Build required; GitHub identity impersonation forbidden")
    need(root.is_dir() and tool.is_dir() and schema.is_file() and sysroot.is_dir(),
         "proof/tool/schema/sysroot inputs missing")
    need(args.deadline_epoch - int(time.time()) > 60, "insufficient deadline reserve")
    dependencies = {rel: file_sha(root / RESEARCH / rel) for rel in DEPENDENCIES}
    need(dependencies == DEPENDENCIES, "source preparation dependency closure differs")
    # The proof checkout is disposable. The caller must not pass an editing worktree.
    need(str(root).startswith("/workspace/"), "proof checkout must be under /workspace")
    evidence.mkdir(parents=True)
    write_json(evidence / "input-profile.json", {
        "provider": provider, "proof_sha": subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip(),
        "compiler_version_verbose": subprocess.check_output(
            ["rustc", "--version", "--verbose"], text=True,
            env={**os.environ, "RUSTUP_TOOLCHAIN": "nightly-2026-09-25"}),
        "dependency_sha256": dependencies, "provider_sha256": PROVIDER_SHA,
        "tool_sha256": {name: file_sha(tool / "bin" / name) for name in
                        ("verifast", "vf-rust-mir-exporter", "refinement-checker")},
        "schema_sha256": file_sha(schema),
        "target": "actual sort4_stable; diagnostic positive-size domain",
        "kernel_changed_by_this_capture": False,
    })
    overlay_guards(root, cloud / "provider.py", evidence)
    fixture = evidence / "actual-sort4-fixture"
    environment = os.environ.copy()
    environment["SMALLSORT_CLOUD_PROVIDER_PATH"] = str(cloud / "provider.py")
    environment["PATH"] = str(tool / "bin") + os.pathsep + environment.get("PATH", "")
    environment["RUSTUP_TOOLCHAIN"] = "nightly-2026-09-25"
    for name in SEMANTIC_OPT_INS:
        environment.pop(name, None)
    source_path = root / "library/core/src/slice/sort/shared/smallsort.rs"
    prepare = root / RESEARCH / "overnight-callback/prepare-actual-sort4-first-call.py"
    stages: dict[str, dict] = {}
    stages["capture"] = run_stage(
        "capture", [sys.executable, str(prepare), "--repo-root", str(root),
                    "--output", str(fixture), "--capture", "--source-checkout", str(tool),
                    "--tool-home", str(tool), "--schema", str(schema),
                    "--compiler-sysroot", str(sysroot),
                    "--deadline-epoch", str(args.deadline_epoch)],
        root, evidence, environment, args.deadline_epoch, 600, (source_path,))
    prepared = json.loads((fixture / "fixture.json").read_text()) if (
        fixture / "fixture.json").is_file() else {}
    calibration = json.loads((fixture / "calibration.json").read_text()) if (
        fixture / "calibration.json").is_file() else {}
    pair = (prepared.get("verified_sha256") == O24_VERIFIED and
            prepared.get("original_sha256") == O24_ORIGINAL and
            prepared.get("ghost_strip_identity") is True)
    support = (stages["capture"].get("exit") == 0 and
               calibration.get("support_exports_decode_refinement_all_zero") is True and
               calibration.get("source_integrity") is True)
    graph_hashes = {
        mode: calibration.get("graphs", {}).get(mode, {}).get("full_function_record_sha256")
        for mode in O24_GRAPHS
    }
    graph_match = graph_hashes == O24_GRAPHS
    admission = root / RESEARCH / "overnight-callback/admit-actual-sort4-first-call.py"
    if support and pair:
        stages["candidate-audit"] = run_stage(
            "candidate-audit", [sys.executable, str(admission), "--repo-root", str(root),
                                "--fixture", str(fixture), "--output",
                                str(evidence / "candidate-admission.json")],
            root, evidence, environment, args.deadline_epoch, 90,
            (source_path, fixture / "verified/lib.rs", fixture / "original/lib.rs"))
        stages["full-verification"] = run_stage(
            "full-verification", [str(tool / "bin/verifast"), "-rustc_args",
                                  "--edition 2021", "-verbose", "1", "verified/lib.rs"],
            fixture, evidence, environment, args.deadline_epoch, 240,
            (source_path, fixture / "verified/lib.rs", fixture / "original/lib.rs"))
    else:
        stages["candidate-audit"] = {"exit": None, "skipped": "source/support gate"}
        stages["full-verification"] = {"exit": None, "skipped": "source/support gate"}
    audit = json.loads((evidence / "candidate-admission.json").read_text()) if (
        evidence / "candidate-admission.json").is_file() else {}
    proof_log = (evidence / "full-verification.log").read_text(errors="replace") if (
        evidence / "full-verification.log").is_file() else ""
    errors = [line for line in proof_log.splitlines()
              if ": error:" in line or line.startswith("Fatal error:")]
    first_error = errors[0] if errors else None
    target_entered = "Verifying function 'sort4_stable'" in proof_log
    reserved_refusal = (target_entered and first_error is not None and
                        "verified/lib.rs(185,13-36)" in first_error and
                        "No such function: __vf_sort4_first_unwind" in first_error)
    tool_after = {name: file_sha(tool / "bin" / name) for name in
                  ("verifast", "vf-rust-mir-exporter", "refinement-checker")}
    tool_before = json.loads((evidence / "input-profile.json").read_text())["tool_sha256"]
    classification = (
        "O24_EXACT_GRAPH_RESERVED_MARKER_DIAGNOSTIC" if
        support and pair and graph_match and reserved_refusal and
        stages["candidate-audit"].get("exit") == 0 and
        audit.get("classification") == "CALIBRATION_REVIEW_REQUIRED" and
        stages["full-verification"].get("exit") not in (None, 0, 124, 137) and
        tool_after == tool_before and
        all(row.get("source_integrity") is True for row in stages.values()
            if "source_integrity" in row)
        else "SORT4_FRESH_CAPTURE_INCONCLUSIVE")
    write_json(evidence / "actual-sort4-result.json", {
        "classification": classification, "accepted": False,
        "actual_sort4_proved": False, "semantic_handler_enabled": False,
        "full_normal_post_proved": False, "full_unwind_post_proved": False,
        "proof_sha": json.loads((evidence / "input-profile.json").read_text())["proof_sha"],
        "source_pair_matches_O24": pair, "support_stages_complete": support,
        "complete_graph_sha256": graph_hashes, "complete_graph_matches_O24": graph_match,
        "candidate_audit": audit.get("classification", "NOT_ADMITTED"),
        "candidate_audit_exit": stages["candidate-audit"].get("exit"),
        "first_verifier_error": first_error, "target_entered": target_entered,
        "reserved_marker_first_refusal": reserved_refusal,
        "verifier_exit": stages["full-verification"].get("exit"),
        "tool_integrity": tool_after == tool_before,
        "stages": stages,
        "diagnostic_domain": "sized T with size_of<T> > 0; four initialized source cells and one T.own each; optional destination; arbitrary lawful F: FnMut(&T,&T)->bool, current F.own/thread/type",
        "active_normal_post": "PARTIAL: current source4/T.own, optional destination, current F.own/thread/type",
        "target_normal_post": "current source4/T.own plus initialized destination4 shadow without second T.own, current F.own/thread/type",
        "target_unwind_post": "for each of five callback panics: current source4/T.own, optional destination before any body copy, current F.own/thread/type and no borrow debt",
        "next_limitation": "The full verifier traverses returning before unwinding. Once the reserved marker is handled, a normal c1 lifetime-cut/half-token failure may prevent any observation of the direct-unwind handler; do not claim an unwind proof from AST or partial logs.",
    })
    print(json.dumps({"classification": classification,
                      "first_verifier_error": first_error,
                      "candidate_audit": audit.get("classification", "NOT_ADMITTED")},
                     sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
