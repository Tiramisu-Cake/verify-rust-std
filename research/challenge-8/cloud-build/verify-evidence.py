#!/usr/bin/env python3
"""Verify a downloaded evidence package and uploader receipt without extraction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
import tarfile


ARCHIVE = "evidence.tar.gz"
SHA_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_name(name: str) -> str:
    path = PurePosixPath(name)
    if path.is_absolute() or not path.parts or any(p in ("", ".", "..") for p in path.parts):
        raise ValueError(f"unsafe archive path: {name}")
    if path.as_posix() != name:
        raise ValueError(f"non-canonical archive path: {name}")
    return path.as_posix()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True,
                        help="downloaded directory containing archive and copies")
    parser.add_argument("--expected-infra-sha")
    parser.add_argument("--expected-proof-sha")
    parser.add_argument("--expected-config-sha")
    parser.add_argument("--expected-build-id")
    parser.add_argument("--expected-lane")
    args = parser.parse_args()
    try:
        root = args.directory
        archive = root / ARCHIVE
        if archive.is_symlink() or not archive.is_file():
            raise ValueError(f"missing regular archive: {ARCHIVE}")
        archive_hash = sha_file(archive)
        sha_path = root / "archive.sha256"
        if sha_path.is_symlink() or not sha_path.is_file():
            raise ValueError("missing regular archive.sha256")
        if sha_path.read_text().strip() != f"{archive_hash}  {ARCHIVE}":
            raise ValueError("archive.sha256 does not match downloaded archive")
        receipt_path = root / "upload-complete.json"
        if receipt_path.is_symlink() or not receipt_path.is_file():
            raise ValueError("missing regular upload-complete.json")
        receipt = json.loads(receipt_path.read_bytes())
        if receipt.get("uploaded") is not True or receipt.get("archive_sha256") != archive_hash:
            raise ValueError("upload receipt does not attest this archive hash")

        members: dict[str, str] = {}
        small_files: dict[str, bytes] = {}
        with tarfile.open(archive, "r:gz") as tar:
            for member in tar:
                name = safe_name(member.name)
                if name in members:
                    raise ValueError(f"duplicate archive path: {name}")
                if not member.isfile():
                    raise ValueError(f"archive entry is not a regular file: {name}")
                stream = tar.extractfile(member)
                if stream is None:
                    raise ValueError(f"cannot read archive entry: {name}")
                digest = hashlib.sha256()
                size = 0
                keep = (name in ("summary.json", "manifest.json", "submitted-config.json", "files-sha256.json")
                        or PurePosixPath(name).name == "proof-audit.json")
                chunks = [] if keep else None
                while True:
                    chunk = stream.read(1024 * 1024)
                    if not chunk:
                        break
                    digest.update(chunk)
                    size += len(chunk)
                    if chunks is not None:
                        chunks.append(chunk)
                if size != member.size:
                    raise ValueError(f"truncated archive entry: {name}")
                members[name] = digest.hexdigest()
                if chunks is not None:
                    small_files[name] = b"".join(chunks)

        for name in ("summary.json", "manifest.json", "submitted-config.json", "files-sha256.json"):
            copy = root / name
            if copy.is_symlink() or not copy.is_file() or sha_file(copy) != members.get(name):
                raise ValueError(f"external copy missing or differs from archive: {name}")
        manifest = json.loads(small_files["manifest.json"])
        summary = json.loads(small_files["summary.json"])
        inventory = json.loads(small_files["files-sha256.json"])
        if manifest.get("files_inventory_sha256") != sha(small_files["files-sha256.json"]):
            raise ValueError("manifest inventory digest mismatch")
        expected_members = set(members) - {"manifest.json", "files-sha256.json"}
        if set(inventory) != expected_members:
            raise ValueError("inventory does not cover every archive payload file")
        for name, expected_hash in inventory.items():
            if members[name] != expected_hash:
                raise ValueError(f"payload hash mismatch: {name}")
        for name, expected_hash in manifest.get("input_sha256", {}).items():
            if inventory.get(name) != expected_hash:
                raise ValueError(f"input hash mismatch or input absent from inventory: {name}")
        config_hash = sha(small_files["submitted-config.json"])
        if manifest.get("submitted_config_actual_sha256") != config_hash:
            raise ValueError("manifest actual submitted-config file hash mismatch")
        try:
            config = json.loads(small_files["submitted-config.json"])
        except (ValueError, UnicodeDecodeError):
            config = None
        steps = config.get("steps") if isinstance(config, dict) else None
        env = {}
        config_matches = False
        if isinstance(steps, list) and steps and isinstance(steps[0], dict):
            step = steps[0]
            for item in step.get("env", []):
                if isinstance(item, str) and "=" in item:
                    key, value = item.split("=", 1)
                    env[key] = value
            config_matches = (step.get("id") == "execute" and
                              env.get("LANE") == manifest.get("lane") and
                              env.get("INFRA_SHA") == manifest.get("infra_sha") and
                              env.get("PROOF_SHA") == manifest.get("proof_sha") and
                              (not manifest.get("proof_image") or
                               step.get("name") == manifest.get("proof_image")))
        config_valid = (config_matches and config_hash == manifest.get("submitted_config_sha256"))
        if manifest.get("environment_sha256") is not None:
            if "environment.txt" not in inventory or inventory["environment.txt"] != manifest["environment_sha256"]:
                raise ValueError("manifest environment hash mismatch")
        if manifest.get("build_id") != receipt.get("build_id"):
            raise ValueError("receipt build_id does not match manifest")
        for field, arg in (("infra_sha", args.expected_infra_sha),
                           ("proof_sha", args.expected_proof_sha),
                           ("submitted_config_sha256", args.expected_config_sha),
                           ("build_id", args.expected_build_id), ("lane", args.expected_lane)):
            if arg is not None and manifest.get(field) != arg:
                raise ValueError(f"expected {field} mismatch")
        for key in ("build_id", "lane", "run_exit_code", "failure_class", "evidence_complete",
                    "smoke_success", "verification_accepted", "missing_mandatory"):
            if manifest.get(key) != summary.get(key):
                raise ValueError(f"summary/manifest mismatch: {key}")
        # Integrity is independent of proof outcome. Never infer proof success from upload.
        lane = manifest.get("lane")
        smoke = lane in ("smoke-success", "smoke-error", "smoke-timeout")
        if manifest.get("smoke_scope") != ("infrastructure-probe-only" if smoke else None):
            raise ValueError("smoke scope marker is inconsistent with lane")
        proof_audit = manifest.get("proof_audit")
        proof_audit_file = None
        complete_inputs = (manifest.get("run_exit_code") is not None and config_valid and
                           all(name in inventory for name in ("run-exit.txt", "full-stdout.log",
                                                              "full-stderr.log", "submitted-config.json",
                                                              "environment.txt")))
        if not smoke:
            audit_path = manifest.get("proof_audit_path")
            try:
                proof_audit_file = json.loads(small_files[audit_path]) if audit_path in small_files else None
            except (ValueError, UnicodeDecodeError):
                proof_audit_file = None
            stage_artifacts = [name for name in inventory if name.startswith("allprooflogs/") and
                               not name.startswith("allprooflogs/cases/") and
                               (name.endswith(".log") or name.endswith("-exit-code.txt") or
                                name.endswith("-resources.txt"))]
            complete_inputs = (complete_inputs and
                               any(name.startswith("allprooflogs/cases/") for name in inventory) and
                               proof_audit_file is not None and proof_audit_file == proof_audit and
                               bool(stage_artifacts) and
                               manifest.get("proof_stage_artifacts") == stage_artifacts)
        accepted = (not smoke and manifest.get("run_exit_code") == 0 and complete_inputs and
                    isinstance(proof_audit, dict) and proof_audit.get("accepted") is True and
                    manifest.get("evidence_complete") is True)
        if manifest.get("verification_accepted") is not accepted:
            raise ValueError("verification acceptance flag is inconsistent with evidence and proof audit")
        smoke_success = (lane == "smoke-success" and manifest.get("run_exit_code") == 0 and
                         complete_inputs and manifest.get("evidence_complete") is True)
        if manifest.get("smoke_success") is not smoke_success:
            raise ValueError("smoke-success flag is inconsistent with lane and evidence")
        print(json.dumps({"integrity_verified": True, "archive_sha256": archive_hash,
                          "build_id": manifest.get("build_id"), "lane": manifest.get("lane"),
                          "run_exit_code": manifest.get("run_exit_code"),
                          "failure_class": manifest.get("failure_class"),
                          "verification_accepted": accepted}, sort_keys=True))
        return 0
    except Exception as exc:
        print(f"evidence verification failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
