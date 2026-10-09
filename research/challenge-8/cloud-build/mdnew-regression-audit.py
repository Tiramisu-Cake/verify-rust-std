#!/usr/bin/env python3
"""Fail-closed audit of pinned upstream VeriFast regression tests."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

CANDIDATE = "fc03ad9e5ab3404398404f3bba9d7bcacec01c43"
TREE = "b292b2e0549db791e57245b0218c4f519e8b821e"
BASE = "f76012fb518703b1d98e243ac4f487f16877cfcb"
BUNDLE = "b4c774a12100b6ed40a0c6368b4b026ab14738d622f3f98f179bcc4e6be0aa7d"
REF = "refs/heads/challenge8/mdnew-focused-validation"
STOCK_ARCHIVE = "5ad2a65997457fd5996a27f93107ef7e52c90c0d12b63b6e67f7acbc73e90efd"
DEPS_ARCHIVE = "8d022c93d51a1d13ec1e782d767c60462405f6865d5ee416f82d6234e93ee580"
RUSTC = "f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f"
CASES = {
    "generic_pair": ("safe_abstraction/generic_pair.rs", "bc3347926e04824a2668c1d59f31b5648ab8d4a2",
                     "04f97abdd1d8f839dd1d397f943ad04bcb38a74ada8677c395486c29c233239e",
                     ["-ignore_unwind_paths", "-ignore_ref_creation"]),
    "tree": ("safe_abstraction/tree.rs", "7ace2cbe2eee2d544766604d018a60a3f901bbdf",
             "526326f9f9c16755a9b98b5269c016122ad7b29b78c5e5c2de2e66d3305b3e71",
             ["-ignore_unwind_paths", "-ignore_ref_creation", "-allow_assume"]),
    "type_projections": ("purely_unsafe/type_projections.rs", "19fc20768d0dbe2720dca8948c38b949c31676de",
                          "7ea763a0375cd1639e0b611aa19659e4f8cd94423121949cd3085fab87f03b9a",
                          ["-ignore_unwind_paths", "-ignore_ref_creation", "-disable_overflow_check"]),
    "generic_structs": ("purely_unsafe/generic_structs.rs", "d26f94e6684bd1e6148fddc98b119a3b27877346",
                         "74e7dee2d795d2f943284ac3fc38744b30b68367821d9e0aba99b74b0917af16", []),
    "scalars": ("purely_unsafe/scalars.rs", "67a588d6755853d7a56725fab2c7492a5a07653e",
                "85da35d4093368453ade1a5f9eb702d749be3b4879126c9a46b87f56f2223c77", []),
}
ERROR = re.compile(r"(?m)^([^\n]*\.(?:rs|rsspec)\(\d+,[^\n]*?: error: [^\n]+|Fatal error:[^\n]+)")
DEAD = re.compile(r"(?m)^([^\n]*?\(\d+,[^\n]*?\): dead code)\s*$")
SUCCESS = re.compile(r"(?m)^0 errors found \(\d+ statements verified\)")
TIMEOUT_CODES = {124, 137, 143}


class AuditFailure(Exception):
    def __init__(self, message: str, kind: str = "EARLY_OR_WRONG_DIAGNOSTIC",
                 classification: str = "INCONCLUSIVE"):
        super().__init__(message)
        self.kind = kind
        self.classification = classification


def need(ok: bool, message: str, kind: str = "EARLY_OR_WRONG_DIAGNOSTIC") -> None:
    if not ok:
        raise AuditFailure(message, kind)


def read(path: Path) -> bytes:
    need(path.is_file(), f"missing evidence: {path}", "MISSING_EVIDENCE")
    return path.read_bytes()


def sha(path: Path) -> str:
    return hashlib.sha256(read(path)).hexdigest()


def json_file(path: Path) -> dict:
    try:
        value = json.loads(read(path))
    except (json.JSONDecodeError, UnicodeDecodeError) as ex:
        raise AuditFailure(f"invalid or incomplete JSON {path}: {ex}", "INCOMPLETE_EVIDENCE") from ex
    need(isinstance(value, dict), f"expected JSON object: {path}", "INCOMPLETE_EVIDENCE")
    return value


def git_text(repo: Path, *args: str) -> str:
    try:
        return subprocess.check_output(["git", "-C", str(repo), *args],
                                       text=True, stderr=subprocess.PIPE).strip()
    except (OSError, subprocess.CalledProcessError) as ex:
        raise AuditFailure(f"cannot inspect pinned Git input: {ex}", "INCOMPLETE_EVIDENCE") from ex


def verify_provenance(tool: Path, all_logs: Path, manifest: dict) -> dict:
    identities = json_file(all_logs / "identities.json")
    receipt = json_file(all_logs / "restore-receipt.json")
    runtime = json_file(all_logs / "runtime-components.json")
    certificate = json_file(all_logs.parent / "source-input-certificate.json")
    infra = identities.get("infra_sha")
    proof = identities.get("proof_sha")
    need(proof == infra == receipt.get("proof_sha") == receipt.get("infra_sha") and
         isinstance(proof, str) and re.fullmatch(r"[0-9a-f]{40}", proof) is not None,
         "proof/infra delivery identities differ")
    need(receipt.get("classification") == "RESTORED_GIT_INPUT" and
         receipt.get("base_commit") == BASE and receipt.get("candidate_commit") == CANDIDATE and
         receipt.get("candidate_ref") == REF and receipt.get("candidate_tree") == TREE and
         receipt.get("bundle_sha256") == BUNDLE and
         receipt.get("manifest_sha256") == sha(all_logs / "tool-input/manifest") and
         receipt.get("git_identity_preserved") is True,
         "restore receipt does not bind the exact tool delivery")
    need(certificate.get("lane") == "verifast-mdnew-regressions" and
         certificate.get("proof", {}).get("commit") == proof == certificate.get("proof", {}).get("head") and
         certificate.get("infra", {}).get("commit") == infra == certificate.get("infra", {}).get("head") and
         certificate.get("proof", {}).get("root_tree") == identities.get("proof_tree") and
         certificate.get("infra", {}).get("root_tree") == identities.get("infra_tree") and
         certificate.get("archive_sha256") == identities.get("source_input_archive_sha256") and
         isinstance(certificate.get("proof", {}).get("restored_paths"), list) and
         isinstance(certificate.get("infra", {}).get("restored_paths"), list),
         "source-input certificate does not bind infra and proof commits")
    bundle_path = all_logs / "tool-input/bundle"
    manifest_path = all_logs / "tool-input/manifest"
    need(sha(bundle_path) == BUNDLE,
         "source bundle bytes differ from the pinned tool delivery")
    manifest_bytes = read(manifest_path)
    delivery = json.loads(manifest_bytes)
    need(delivery.get("candidate_commit") == CANDIDATE and
         delivery.get("candidate_tree") == TREE and delivery.get("candidate_ref") == REF and
         delivery.get("bundle_sha256") == BUNDLE,
         "source manifest differs from the pinned tool delivery")
    proof_paths = certificate["proof"]["restored_paths"]
    for rel, expected in (
        (f"research/challenge-8/verifast-input/{CANDIDATE}/bundle", BUNDLE),
        (f"research/challenge-8/verifast-input/{CANDIDATE}/manifest",
         hashlib.sha256(manifest_bytes).hexdigest()),
    ):
        records = [item for item in proof_paths if item.get("path") == rel]
        need(len(records) == 1 and records[0].get("sha256") == expected,
             f"source-input certificate lacks exact restored {rel}")
    infra_paths = certificate["infra"]["restored_paths"]
    infra_root = Path(__file__).resolve().parents[3]
    for rel, path in (
        ("research/challenge-8/cloud-build/run-verifast-mdnew-cfg.sh",
         infra_root / "research/challenge-8/cloud-build/run-verifast-mdnew-cfg.sh"),
        ("research/challenge-8/cloud-build/mdnew-regression-audit.py", Path(__file__)),
        ("research/challenge-8/cloud-build/recipes/verifast-mdnew-regressions.json",
         infra_root / "research/challenge-8/cloud-build/recipes/verifast-mdnew-regressions.json"),
    ):
        records = [item for item in infra_paths if item.get("path") == rel]
        need(len(records) == 1 and records[0].get("sha256") == sha(path),
             f"source-input certificate lacks restored {rel}")
    need(manifest.get("infra_sha") == infra and manifest.get("proof_sha") == proof and
         manifest.get("candidate_commit") == CANDIDATE and manifest.get("candidate_tree") == TREE,
         "regression manifest identities differ from the pinned delivery")
    need(git_text(tool, "rev-parse", "HEAD") == CANDIDATE and
         git_text(tool, "rev-parse", "HEAD^{tree}") == TREE and
         runtime.get("baseline_source_sha") == BASE and
         runtime.get("candidate_source_sha") == CANDIDATE and
         runtime.get("candidate_tree") == TREE and
         runtime.get("stock_distribution_sha256") == STOCK_ARCHIVE and
         runtime.get("vfdeps_archive_sha256") == DEPS_ARCHIVE and
         f"commit-hash: {RUSTC}" in runtime.get("rustc_verbose", ""),
         "runtime/source-built candidate differs from the approved tool profile")
    binaries = runtime.get("console_binary_sha256", {})
    need(isinstance(binaries.get("baseline"), str) and
         re.fullmatch(r"[0-9a-f]{64}", binaries["baseline"]) is not None and
         isinstance(binaries.get("candidate"), str) and
         re.fullmatch(r"[0-9a-f]{64}", binaries["candidate"]) is not None and
         binaries["baseline"] != binaries["candidate"],
         "source-built baseline/candidate console identities are absent or equal")
    for name in ("vf-rust-mir-exporter", "refinement-checker", "vf-cxx-ast-exporter",
                 "libz3.so", "rust/std/lib.rsspec"):
        item = runtime.get("pinned_stock_binaries", {}).get(name, {})
        need(item.get("baseline_equal") is True and item.get("candidate_equal") is True and
             isinstance(item.get("sha256"), str) and
             re.fullmatch(r"[0-9a-f]{64}", item["sha256"]) is not None,
             f"unchanged stock component {name} lacks equality evidence")
    for name in ("src/rust_frontend/vf_mir_exporter",
                 "src/rust_frontend/vf_mir_decoder", "src/refinement_checker"):
        item = runtime.get("components", {}).get(name, {})
        need(isinstance(item.get("source_file_count"), int) and item["source_file_count"] > 0 and
             isinstance(item.get("source_files_sha256"), str) and
             re.fullmatch(r"[0-9a-f]{64}", item["source_files_sha256"]) is not None,
             f"unchanged source component {name} lacks its inventory")
    spec_inventory = runtime.get("specification_inventory", {})
    need(spec_inventory.get("baseline") == spec_inventory.get("candidate") ==
         runtime.get("stock_specification_inventory") and bool(spec_inventory.get("baseline")),
         "baseline/candidate/stock specification inventories differ")
    return {"infra_sha": infra, "proof_sha": proof,
            "restore_receipt_sha256": sha(all_logs / "restore-receipt.json"),
            "runtime_components_sha256": sha(all_logs / "runtime-components.json"),
            "source_certificate_sha256": sha(all_logs.parent / "source-input-certificate.json"),
            "console_binary_sha256": binaries}


def verify_case(tool: Path, all_logs: Path, row: dict) -> dict:
    name = row.get("name")
    need(name in CASES, f"unknown regression case: {name}", "INCOMPLETE_EVIDENCE")
    relative, expected_blob, expected_sha, options = CASES[name]
    need(row.get("path") == relative and row.get("options") == options,
         f"{name} invocation path/options differ from the approved upstream command")
    source = tool / "tests/rust" / relative
    need(sha(source) == expected_sha == row.get("source_sha256"),
         f"{name} source bytes differ from the pinned upstream test")
    actual_blob = git_text(tool, "rev-parse", f"{CANDIDATE}:tests/rust/{relative}")
    need(actual_blob == expected_blob == row.get("git_blob"),
         f"{name} Git blob differs from the pinned upstream test")
    code = row.get("exit_status")
    need(isinstance(code, int) and not isinstance(code, bool),
         f"{name} exit status is absent or malformed", "INCOMPLETE_EVIDENCE")
    if code in TIMEOUT_CODES:
        raise AuditFailure(f"{name} timed out (exit {code})", "TIMEOUT")
    need(code == 0, f"{name} exited {code}, expected 0")
    for field, expected_path in (
        ("stdout", f"{name}.stdout.log"),
        ("stderr", f"mdnew-regression-{name}-stderr.log"),
        ("resources", f"mdnew-regression-{name}-resources.txt"),
        ("exit_status_file", f"mdnew-regression-{name}-exit-code.txt"),
    ):
        item = row.get(field, {})
        need(item.get("path") == expected_path and isinstance(item.get("sha256"), str) and
             re.fullmatch(r"[0-9a-f]{64}", item["sha256"]) is not None,
             f"{name} {field} receipt is absent or malformed", "INCOMPLETE_EVIDENCE")
        path = all_logs / "regressions" / item["path"] if field == "stdout" else all_logs / item["path"]
        need(sha(path) == item["sha256"], f"{name} {field} digest differs", "INCOMPLETE_EVIDENCE")
    try:
        status_file = int(read(all_logs / f"mdnew-regression-{name}-exit-code.txt").decode().strip())
    except (UnicodeDecodeError, ValueError):
        raise AuditFailure(f"{name} exit-status file is malformed", "INCOMPLETE_EVIDENCE")
    need(status_file == code, f"{name} recorded exit statuses disagree", "INCOMPLETE_EVIDENCE")
    log = (all_logs / "regressions" / f"{name}.stdout.log").read_text(errors="replace")
    require_text = log + (all_logs / f"mdnew-regression-{name}-stderr.log").read_text(errors="replace")
    need(SUCCESS.search(log) is not None, f"{name} lacks a complete success summary",
         "INCOMPLETE_EVIDENCE")
    need(ERROR.search(require_text) is None, f"{name} has an unexpected verifier diagnostic")
    need(DEAD.search(require_text) is None, f"{name} has an unexpected dead-code diagnostic")
    return {"name": name, "path": relative, "source_sha256": expected_sha,
            "git_blob": expected_blob, "options": options, "exit_status": code,
            "stdout_sha256": row["stdout"]["sha256"],
            "stderr_sha256": row["stderr"]["sha256"],
            "resources_sha256": row["resources"]["sha256"],
            "complete_success_summary": True, "unexpected_dead_code": False}


def audit(tool: Path, all_logs: Path) -> dict:
    tool = tool.resolve()
    all_logs = all_logs.resolve()
    manifest = json_file(all_logs / "regressions/manifest.json")
    provenance = verify_provenance(tool, all_logs, manifest)
    rows = manifest.get("results")
    need(isinstance(rows, list), "regression result list is absent", "INCOMPLETE_EVIDENCE")
    names = [row.get("name") for row in rows if isinstance(row, dict)]
    need(len(rows) == len(CASES) and len(names) == len(CASES) and
         len(set(names)) == len(CASES) and set(names) == set(CASES),
         "regression case set is incomplete or duplicated", "INCOMPLETE_EVIDENCE")
    results = [verify_case(tool, all_logs, row) for row in rows]
    return {"classification": "UPSTREAM_TARGETED_REGRESSIONS_PASS", "accepted": True,
            "fixture_commit": CANDIDATE, "provenance": provenance,
            "completed_regressions": results,
            "scope": "five pinned upstream regressions only; focused gate and consumer acceptance not implied"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate_tool", type=Path)
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = audit(args.candidate_tool, args.evidence)
        code = 0
    except AuditFailure as ex:
        result = {"classification": ex.classification, "accepted": False,
                  "failure_kind": ex.kind, "reason": str(ex)}
        code = 2 if ex.classification == "INCONCLUSIVE" else 1
    except (OSError, UnicodeError, ValueError, TypeError, KeyError, AttributeError) as ex:
        result = {"classification": "INCONCLUSIVE", "accepted": False,
                  "failure_kind": "INCOMPLETE_EVIDENCE", "reason": str(ex)}
        code = 2
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    sys.stdout.write(rendered)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
