#!/usr/bin/env python3
"""Verify a downloaded evidence package and uploader receipt without extraction."""

from __future__ import annotations

import argparse
import hashlib
from decimal import Decimal
import json
from pathlib import Path, PurePosixPath
import re
import sys
import tarfile

MAX_TEXT_CHUNK_BYTES = 8 * 1024 * 1024
MAX_METADATA_BYTES = 8 * 1024 * 1024
MAX_INVENTORY_BYTES = 8 * 1024 * 1024
MAX_ORIGINAL_AUDIT_BYTES = 64 * 1024 * 1024


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


def audit_canonicalization_matches(original_bytes: bytes, canonical_bytes: bytes) -> bool:
    def reject_constant(value):
        raise ValueError(f"invalid JSON constant: {value}")
    try:
        original = json.loads(original_bytes, parse_constant=reject_constant)
        canonical = json.loads(canonical_bytes, parse_constant=reject_constant)
        return (isinstance(original, dict) and isinstance(original.get("accepted"), bool)
                and json.loads(original_bytes, parse_float=Decimal, parse_int=Decimal) ==
                    json.loads(canonical_bytes, parse_float=Decimal, parse_int=Decimal)
                and canonical_bytes == (json.dumps(original, sort_keys=True,
                    separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True,
                        help="downloaded directory containing archive and copies")
    parser.add_argument("--expected-infra-sha")
    parser.add_argument("--expected-proof-sha")
    parser.add_argument("--expected-config-sha")
    parser.add_argument("--expected-build-id")
    parser.add_argument("--expected-lane")
    parser.add_argument("--require-text-logs", action="store_true")
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
        member_sizes: dict[str, int] = {}
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
                keep = (name in ("summary.json", "manifest.json", "submitted-config.json", "files-sha256.json", "source-input-certificate.json")
                        or name == "text-logs-index.json"
                        or PurePosixPath(name).name == "proof-audit.json")
                limit = (MAX_INVENTORY_BYTES if name == "files-sha256.json" else MAX_METADATA_BYTES)
                if keep and member.size > limit:
                    raise ValueError(f"oversized metadata entry: {name}")
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
                member_sizes[name] = size
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
        if "proof_audit_canonicalizations" in manifest:
            canonicalizations = manifest["proof_audit_canonicalizations"]
            if not isinstance(canonicalizations, list):
                raise ValueError("proof-audit canonicalization descriptor must be a list")
            seen_sources = set()
            seen_companions = set()
            for descriptor in canonicalizations:
                if not isinstance(descriptor, dict):
                    raise ValueError("invalid proof-audit canonicalization descriptor")
                source_path = safe_name(descriptor.get("source_path", ""))
                canonical_path = safe_name(descriptor.get("canonical_path", ""))
                original_path = safe_name(descriptor.get("original_bytes_path", ""))
                original_hash = descriptor.get("original_sha256")
                canonical_hash = descriptor.get("canonical_sha256")
                original_size = descriptor.get("original_size_bytes")
                canonical_size = descriptor.get("canonical_size_bytes")
                if (source_path != canonical_path or
                        PurePosixPath(source_path).name != "proof-audit.json" or
                        original_path != source_path + ".original-bytes" or
                        source_path in seen_sources or original_path in seen_companions or
                        descriptor.get("encoding") !=
                        "UTF-8 JSON; sorted keys; compact separators; trailing LF" or
                        not re.fullmatch(r"[0-9a-f]{64}", str(original_hash)) or
                        not re.fullmatch(r"[0-9a-f]{64}", str(canonical_hash)) or
                        not isinstance(original_size, int) or isinstance(original_size, bool) or
                        original_size <= MAX_METADATA_BYTES or
                        original_size > MAX_ORIGINAL_AUDIT_BYTES or
                        not isinstance(canonical_size, int) or isinstance(canonical_size, bool) or
                        canonical_size <= 0 or canonical_size > MAX_METADATA_BYTES or
                        canonical_size >= original_size):
                    raise ValueError(f"invalid proof-audit canonicalization descriptor: {source_path}")
                seen_sources.add(source_path)
                seen_companions.add(original_path)
                if (inventory.get(source_path) != canonical_hash or
                        members.get(source_path) != canonical_hash or
                        member_sizes.get(source_path) != canonical_size or
                        inventory.get(original_path) != original_hash or
                        members.get(original_path) != original_hash or
                        member_sizes.get(original_path) != original_size or
                        source_path not in small_files):
                    raise ValueError(f"proof-audit canonicalization path/hash/size mismatch: {source_path}")
                with tarfile.open(archive, "r:gz") as canonical_archive:
                    original_member = canonical_archive.getmember(original_path)
                    original_stream = canonical_archive.extractfile(original_member)
                    if original_stream is None:
                        raise ValueError(f"cannot read original proof-audit bytes: {original_path}")
                    original_bytes = original_stream.read(MAX_ORIGINAL_AUDIT_BYTES + 1)
                if len(original_bytes) != original_size or sha(original_bytes) != original_hash:
                    raise ValueError(f"proof-audit original bytes hash/size mismatch: {source_path}")
                if not audit_canonicalization_matches(original_bytes, small_files[source_path]):
                    raise ValueError(f"proof-audit canonicalization content/encoding mismatch: {source_path}")
        config_hash = sha(small_files["submitted-config.json"])
        if manifest.get("submitted_config_actual_sha256") != config_hash:
            raise ValueError("manifest actual submitted-config file hash mismatch")
        config_reference = manifest.get("config_fields_reference")
        if "config_fields_reference" in manifest and config_reference != {
                "path": "submitted-config.json", "sha256": config_hash,
                "size_bytes": len(small_files["submitted-config.json"])}:
            raise ValueError("manifest submitted-config reference/hash/size mismatch")
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
        source_mode = env.get("SOURCE_MODE", "public-git")
        source_valid = source_mode == "public-git"
        source_certificate = None
        if "source-input-certificate.json" in small_files:
            source_certificate = json.loads(small_files["source-input-certificate.json"])
        if source_mode == "pinned-objects":
            source_valid = (isinstance(source_certificate, dict) and
                isinstance(source_certificate.get("infra"), dict) and
                isinstance(source_certificate.get("proof"), dict) and
                members.get("source-input.gz") == env.get("SOURCE_INPUT_SHA256") and
                source_certificate.get("archive_sha256") == env.get("SOURCE_INPUT_SHA256") and
                source_certificate.get("lane") == manifest.get("lane") and
                source_certificate.get("infra", {}).get("commit") == env.get("INFRA_SHA") and
                source_certificate.get("infra", {}).get("head") == env.get("INFRA_SHA") and
                source_certificate.get("proof", {}).get("commit") == env.get("PROOF_SHA") and
                source_certificate.get("proof", {}).get("head") == env.get("PROOF_SHA"))
        delivery = manifest.get("source_delivery")
        if delivery is not None and delivery != {"mode": source_mode, "valid": source_valid,
                                                  "certificate": source_certificate}:
            raise ValueError("source delivery certificate/hash flag differs from archived evidence")

        if manifest.get("environment_sha256") is not None:
            if "environment.txt" not in inventory or inventory["environment.txt"] != manifest["environment_sha256"]:
                raise ValueError("manifest environment hash mismatch")
        has_text_log_index = "text-logs-index.json" in small_files
        require_text_logs = (args.require_text_logs or
                             "text_logs_index_sha256" in manifest or
                             "text_logs_index_sha256" in summary)
        if require_text_logs and not has_text_log_index:
            raise ValueError("archive is missing required text-logs-index.json")
        index_hash = None
        if has_text_log_index:
            index_bytes = small_files["text-logs-index.json"]
            index_hash = sha(index_bytes)
            if (manifest.get("text_logs_index_sha256") != index_hash or
                    summary.get("text_logs_index_sha256") != index_hash or
                    manifest.get("text_log_delivery", {}).get("index_sha256") != index_hash or
                    manifest.get("text_log_delivery", {}).get("index_size_bytes") != len(index_bytes)):
                raise ValueError("text log index digest/size differs from archive/manifest/summary")
            external_index = root / "text-logs-index.json"
            if external_index.exists() or external_index.is_symlink():
                if external_index.is_symlink() or not external_index.is_file() or sha_file(external_index) != index_hash:
                    raise ValueError("separately downloaded text log index differs from archive")
            if receipt.get("text_logs_index_sha256") not in (None, index_hash):
                raise ValueError("upload receipt text-log index hash mismatch")
            if require_text_logs and receipt.get("text_logs_index_sha256") != index_hash:
                raise ValueError("upload receipt does not attest required text-log index")
            log_index = json.loads(index_bytes)
        else:
            log_index = None
            if (root / "text-logs-index.json").exists() or (root / "text-logs-index.json").is_symlink():
                raise ValueError("external text log index is absent from archive")
        if log_index is not None and (log_index.get("schema_version") != 1 or
                                      log_index.get("chunk_size_limit_bytes") != MAX_TEXT_CHUNK_BYTES):
            raise ValueError("unsupported text log index schema or chunk limit")
        log_files = log_index.get("files") if log_index is not None else []
        if not isinstance(log_files, list):
            raise ValueError("text log index files must be a list")
        source_paths = [item.get("source_path") for item in log_files if isinstance(item, dict)]
        expected_logs = {name for name in inventory if PurePosixPath(name).suffix.lower() in (".log", ".txt")}
        if (log_index is not None and
                (len(source_paths) != len(log_files) or len(set(source_paths)) != len(source_paths) or
                 set(source_paths) != expected_logs)):
            raise ValueError("text log index does not cover every archived .log/.txt source exactly once")
        declared_chunks = set()
        total_chunks = 0
        for entry in log_files:
            source_path = safe_name(entry.get("source_path", ""))
            if (entry.get("sha256") != members.get(source_path) or
                    entry.get("size_bytes") != member_sizes.get(source_path)):
                raise ValueError(f"text log source hash/size mismatch: {source_path}")
            if entry.get("encoding_note") not in (
                    "valid UTF-8; split on code-point boundaries where possible; original bytes preserved",
                    "not valid UTF-8; treated as raw bytes without decoding or modification"):
                raise ValueError(f"invalid text-log encoding note: {source_path}")
            chunks = entry.get("chunks")
            if not isinstance(chunks, list) or not chunks:
                raise ValueError(f"text log has no chunks: {source_path}")
            source_path_id = hashlib.sha256(source_path.encode("utf-8")).hexdigest()
            chunk_size_sum = 0
            for i, chunk in enumerate(chunks):
                chunk_path = safe_name(chunk.get("path", ""))
                expected_chunk_path = f"text-logs/{source_path_id}.part-{i:06d}.txt"
                if chunk_path != expected_chunk_path or chunk_path in declared_chunks:
                    raise ValueError(f"non-deterministic or duplicate text chunk path: {chunk_path}")
                declared_chunks.add(chunk_path)
                size = chunk.get("size_bytes")
                chunk_hash = chunk.get("sha256")
                if (not isinstance(size, int) or size < 0 or size > MAX_TEXT_CHUNK_BYTES or
                        not re.fullmatch(r"[0-9a-f]{64}", str(chunk_hash))):
                    raise ValueError(f"invalid chunk hash/size: {chunk_path}")
                chunk_size_sum += size
                total_chunks += 1
            reconstruction = entry.get("reconstruction")
            if (chunk_size_sum != entry.get("size_bytes") or
                    reconstruction != {"method": "concatenate-in-listed-order",
                                       "sha256": entry.get("sha256"),
                                       "size_bytes": entry.get("size_bytes")}):
                raise ValueError(f"text log reconstruction metadata mismatch: {source_path}")
        if (log_index is not None and (log_index.get("source_count") != len(log_files) or
                log_index.get("chunk_count") != total_chunks or
                manifest.get("text_log_delivery", {}).get("source_count") != len(log_files) or
                manifest.get("text_log_delivery", {}).get("chunk_count") != total_chunks)):
            raise ValueError("text log index counts disagree")
        chunks_dir = root / "text-logs"
        chunks_downloaded = chunks_dir.exists()
        if chunks_downloaded and log_index is None:
            raise ValueError("downloaded text chunks have no archive index")
        if chunks_dir.is_symlink():
            raise ValueError("downloaded text-logs path is a symlink")
        if chunks_downloaded:
            downloaded = {}
            for path in chunks_dir.rglob("*"):
                if path.is_symlink():
                    raise ValueError(f"symlink in downloaded text logs: {path}")
                if path.is_file():
                    downloaded[path.relative_to(root).as_posix()] = path
                elif not path.is_dir():
                    raise ValueError(f"non-regular downloaded text log entry: {path}")
            if set(downloaded) != declared_chunks:
                raise ValueError("downloaded text log chunks do not match the index")
            for entry in log_files:
                reconstructed = hashlib.sha256()
                reconstructed_size = 0
                for chunk in entry["chunks"]:
                    path = downloaded[chunk["path"]]
                    if path.stat().st_size != chunk["size_bytes"] or sha_file(path) != chunk["sha256"]:
                        raise ValueError(f"downloaded text log chunk hash/size mismatch: {chunk['path']}")
                    with path.open("rb") as stream:
                        for data in iter(lambda: stream.read(1024 * 1024), b""):
                            reconstructed.update(data)
                            reconstructed_size += len(data)
                if reconstructed.hexdigest() != entry["sha256"] or reconstructed_size != entry["size_bytes"]:
                    raise ValueError(f"downloaded text log reconstruction failed: {entry['source_path']}")
        logs_complete = (True if log_index is None else
                         all(name in expected_logs for name in
                             ("full-stdout.log", "full-stderr.log", "environment.txt")) and bool(log_files))
        if (log_index is not None and
                (manifest.get("text_logs_complete") is not logs_complete or
                 summary.get("text_logs_complete") is not logs_complete or
                 manifest.get("text_log_delivery", {}).get("complete") is not logs_complete)):
            raise ValueError("text log completeness flag disagrees with archived inputs")
        if manifest.get("build_id") != receipt.get("build_id"):
            raise ValueError("receipt build_id does not match manifest")
        for field, arg in (("infra_sha", args.expected_infra_sha),
                           ("proof_sha", args.expected_proof_sha),
                           ("submitted_config_sha256", args.expected_config_sha),
                           ("build_id", args.expected_build_id), ("lane", args.expected_lane)):
            if arg is not None and manifest.get(field) != arg:
                raise ValueError(f"expected {field} mismatch")
        for key in ("build_id", "lane", "run_exit_code", "failure_class", "evidence_complete",
                    "smoke_success", "verification_accepted", "missing_mandatory",
                    "text_logs_complete", "text_logs_index_sha256"):
            if manifest.get(key) != summary.get(key):
                raise ValueError(f"summary/manifest mismatch: {key}")
        # Integrity is independent of proof outcome. Never infer proof success from upload.
        lane = manifest.get("lane")
        smoke = lane in ("smoke-success", "smoke-error", "smoke-timeout")
        if manifest.get("smoke_scope") != ("infrastructure-probe-only" if smoke else None):
            raise ValueError("smoke scope marker is inconsistent with lane")
        proof_audit = manifest.get("proof_audit")
        proof_audit_file = None
        complete_inputs = (manifest.get("run_exit_code") is not None and config_valid and source_valid and
                           logs_complete and
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
                          "verification_accepted": accepted,
                          "text_log_index_verified": True,
                          "text_log_chunks_downloaded": chunks_downloaded}, sort_keys=True))
        return 0
    except Exception as exc:
        print(f"evidence verification failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
