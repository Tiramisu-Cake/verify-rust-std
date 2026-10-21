#!/usr/bin/env python3
"""Generate a non-proof upload payload for the isolated R13 Cloud probe."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from datetime import datetime, timezone

MODE_SCHEMA = "merge-r13-upload-mode-v1"
MANIFEST_SCHEMA = "smallsort-r13-synthetic-upload-v1"
AUDIT_SCHEMA = "smallsort-merge-cloud-diagnostic-v1"
MIN_PAYLOAD_BYTES = 256 * 1024 * 1024
SYNTHETIC_PAYLOAD_BYTES = 256 * 1024 * 1024
COMPOSITE_THRESHOLD_BYTES = 150 * 1024 * 1024
ARCHIVE_LIMIT_BYTES = 512 * 1024 * 1024
THRESHOLD_SOURCE = "https://docs.cloud.google.com/storage/docs/parallel-composite-uploads"
CHUNK_BYTES = 1024 * 1024
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
GIT_SHA_RE = re.compile(r"[0-9a-f]{40}\Z")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_mode_card(path: Path) -> tuple[str, bytes]:
    path = Path(path)
    try:
        mode = path.lstat().st_mode
    except FileNotFoundError as error:
        raise ValueError("R13 mode card is missing") from error
    import stat
    if stat.S_ISLNK(mode) or not stat.S_ISREG(mode):
        raise ValueError("R13 mode card must be a regular non-symlink file")
    raw = path.read_bytes()
    try:
        card = json.loads(raw)
    except (ValueError, UnicodeDecodeError) as error:
        raise ValueError("R13 mode card is not valid JSON") from error
    if not isinstance(card, dict) or card.get("schema") != MODE_SCHEMA or card.get("mode") not in {
            "synthetic-upload", "proof-r11"}:
        raise ValueError("R13 mode card has an unknown schema, field set, or mode")
    if card["mode"] == "synthetic-upload" and (
            set(card) != {"schema", "mode", "payload_bytes", "threshold_bytes",
                          "archive_limit_bytes", "threshold_source", "proof_attempted"} or
            type(card.get("payload_bytes")) is not int or
            card.get("payload_bytes") != SYNTHETIC_PAYLOAD_BYTES or
            type(card.get("threshold_bytes")) is not int or
            card.get("threshold_bytes") != COMPOSITE_THRESHOLD_BYTES or
            type(card.get("archive_limit_bytes")) is not int or
            card.get("archive_limit_bytes") != ARCHIVE_LIMIT_BYTES or
            card.get("threshold_source") != THRESHOLD_SOURCE or
            card.get("proof_attempted") is not False):
        raise ValueError("R13 synthetic mode card disagrees with the reviewed payload/threshold/archive cap")
    if card["mode"] == "proof-r11" and (
            set(card) != {"schema", "mode", "archive_limit_bytes"} or
            type(card.get("archive_limit_bytes")) is not int or
            card.get("archive_limit_bytes") != ARCHIVE_LIMIT_BYTES):
        raise ValueError("R13 proof-r11 mode card must bind the exact archive cap")
    return card["mode"], raw


def write_random_payload(path: Path, size_bytes: int, *, chunk_bytes: int = CHUNK_BYTES,
                         random_bytes=os.urandom) -> tuple[int, str]:
    """Stream random data into an exclusively created file and return size/SHA256."""
    if type(size_bytes) is not int or size_bytes < 0:
        raise ValueError("payload size must be a nonnegative integer")
    if type(chunk_bytes) is not int or chunk_bytes <= 0:
        raise ValueError("payload chunk size must be a positive integer")
    path = Path(path)
    digest = hashlib.sha256()
    written = 0
    with path.open("xb") as stream:
        while written < size_bytes:
            request = min(chunk_bytes, size_bytes - written)
            data = random_bytes(request)
            if not isinstance(data, bytes) or len(data) != request:
                raise ValueError("random source returned an invalid chunk")
            stream.write(data)
            digest.update(data)
            written += len(data)
        stream.flush()
        os.fsync(stream.fileno())
    return written, digest.hexdigest()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _write_new_json(path: Path, value: dict) -> None:
    encoded = (json.dumps(value, sort_keys=True, indent=2) + "\n").encode("utf-8")
    with path.open("xb") as stream:
        stream.write(encoded)
        stream.flush()
        os.fsync(stream.fileno())


def _write_atomic_json(path: Path, value: dict) -> None:
    tmp = path.with_name(path.name + ".tmp")
    if tmp.exists() or tmp.is_symlink():
        raise ValueError("refusing to reuse R13 audit temporary path")
    encoded = (json.dumps(value, sort_keys=True, indent=2) + "\n").encode("utf-8")
    with tmp.open("xb") as stream:
        stream.write(encoded)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(tmp, path)


def _validate_runtime(evidence: Path, mode_card: Path, env: dict[str, str]):
    mode, card_bytes = read_mode_card(mode_card)
    if mode != "synthetic-upload":
        raise ValueError("synthetic generator requires mode synthetic-upload")
    if (env.get("R13_UPLOAD_REQUIRED") != "true" or env.get("LANE") != "merge" or
            env.get("SMALLSORT_EXECUTION_PROVIDER") != "cloud-build" or
            env.get("SOURCE_MODE") != "pinned-objects"):
        raise ValueError("R13 synthetic upload requires pinned merge Cloud Build execution")
    build_id = env.get("CLOUD_BUILD_ID", "")
    infra_sha = env.get("INFRA_SHA", "")
    proof_sha = env.get("PROOF_SHA", "")
    source_input_sha = env.get("SOURCE_INPUT_SHA256", "")
    if not build_id or not GIT_SHA_RE.fullmatch(infra_sha) or not GIT_SHA_RE.fullmatch(proof_sha):
        raise ValueError("R13 synthetic upload lacks exact Build/source identities")
    if not SHA256_RE.fullmatch(source_input_sha):
        raise ValueError("R13 synthetic upload lacks the pinned source archive SHA256")
    evidence = Path(evidence)
    if evidence.is_symlink() or not evidence.is_dir():
        raise ValueError("R13 evidence root must be an existing real directory")
    cert_path = evidence / "source-input-certificate.json"
    if cert_path.is_symlink() or not cert_path.is_file():
        raise ValueError("R13 synthetic upload requires the pinned source certificate")
    try:
        certificate = json.loads(cert_path.read_text())
    except (ValueError, UnicodeDecodeError) as error:
        raise ValueError("R13 source certificate is invalid JSON") from error
    proof_record = certificate.get("proof") if isinstance(certificate, dict) else None
    infra_record = certificate.get("infra") if isinstance(certificate, dict) else None
    if (not isinstance(certificate, dict) or not isinstance(proof_record, dict) or
            not isinstance(infra_record, dict) or certificate.get("lane") != "merge" or
            certificate.get("archive_sha256") != source_input_sha or
            proof_record.get("commit") != proof_sha or proof_record.get("head") != proof_sha or
            infra_record.get("commit") != infra_sha or infra_record.get("head") != infra_sha):
        raise ValueError("R13 source certificate does not match current pinned Build inputs")
    return {
        "mode_card_sha256": sha256_bytes(card_bytes),
        "mode_card": json.loads(card_bytes),
        "build_id": build_id,
        "infra_sha": infra_sha,
        "proof_sha": proof_sha,
        "source_input_sha256": source_input_sha,
        "source_certificate_sha256": sha256_bytes(cert_path.read_bytes()),
    }


def _generate_synthetic(evidence: Path, mode_card: Path, env: dict[str, str],
                        payload_size_bytes: int = MIN_PAYLOAD_BYTES,
                        random_bytes=os.urandom, clock=_utc_now) -> dict:
    """Internal generator entry; payload_size_bytes is test-only, never CLI-controlled."""
    if type(payload_size_bytes) is not int or payload_size_bytes < 0:
        raise ValueError("internal payload size must be a nonnegative integer")
    identity = _validate_runtime(evidence, mode_card, env)
    allprooflogs = evidence / "allprooflogs"
    case_root = allprooflogs / "cases" / "synthetic-upload"
    audit_path = allprooflogs / "proof-audit.json"
    stage_log = allprooflogs / "r13-synthetic-upload.log"
    stage_exit = allprooflogs / "r13-synthetic-upload-exit-code.txt"
    for path in (allprooflogs, allprooflogs / "cases", case_root):
        if path.is_symlink():
            raise ValueError("R13 output path must not be a symlink")
    if audit_path.exists() or audit_path.is_symlink() or stage_log.exists() or stage_log.is_symlink() or stage_exit.exists() or stage_exit.is_symlink() or case_root.exists():
        raise ValueError("refusing to reuse existing R13 synthetic evidence paths")
    case_root.mkdir(parents=True)
    payload_path = case_root / "payload.bin"
    manifest_path = case_root / "manifest.json"
    started = clock()
    audit = {
        "schema": AUDIT_SCHEMA, "lane": "merge", "accepted": False,
        "proof_attempted": False, "independent_credit": 0,
        "diagnostic_complete": False, "classification": "SYNTHETIC_UPLOAD_INCOMPLETE",
        "mode": "synthetic-upload", "build_id": identity["build_id"],
        "source": {"infra_sha": identity["infra_sha"], "proof_sha": identity["proof_sha"]},
    }
    _write_new_json(audit_path, audit)
    try:
        actual_size, payload_sha = write_random_payload(
            payload_path, payload_size_bytes, random_bytes=random_bytes)
        completed = clock()
        manifest = {
            "schema": MANIFEST_SCHEMA, "status": "COMPLETE", "mode": "synthetic-upload",
            "build_id": identity["build_id"],
            "source": {"infra_sha": identity["infra_sha"], "proof_sha": identity["proof_sha"],
                       "source_input_sha256": identity["source_input_sha256"],
                       "source_certificate_sha256": identity["source_certificate_sha256"]},
            "mode_card": identity["mode_card"], "mode_card_sha256": identity["mode_card_sha256"],
            "upload_size_contract": {"payload_bytes": SYNTHETIC_PAYLOAD_BYTES,
                                     "threshold_bytes": COMPOSITE_THRESHOLD_BYTES,
                                     "archive_limit_bytes": ARCHIVE_LIMIT_BYTES,
                                     "threshold_source": THRESHOLD_SOURCE},
            "payload": {"path": "allprooflogs/cases/synthetic-upload/payload.bin",
                        "size_bytes": actual_size, "sha256": payload_sha,
                        "chunk_bytes": CHUNK_BYTES, "encoding": "os.urandom; incompressible random bytes"},
            "started_at_utc": started, "completed_at_utc": completed,
            "proof_attempted": False, "accepted": False, "independent_credit": 0,
        }
        _write_new_json(manifest_path, manifest)
        stage_record = {
            "stage": "r13-synthetic-upload-generation", "status": "COMPLETE",
            "build_id": identity["build_id"], "payload_bytes": actual_size,
            "payload_sha256": payload_sha, "started_at_utc": started,
            "completed_at_utc": completed,
        }
        stage_log.write_text(json.dumps(stage_record, sort_keys=True) + "\n")
        stage_exit.write_text("0\n")
        audit.update({
            "diagnostic_complete": True,
            "classification": "SYNTHETIC_UPLOAD_PAYLOAD_READY",
            "synthetic_upload": {"manifest": "allprooflogs/cases/synthetic-upload/manifest.json",
                                 "payload_bytes": actual_size, "payload_sha256": payload_sha},
        })
        _write_atomic_json(audit_path, audit)
        return manifest
    except BaseException as error:
        try:
            stage_log.write_text(json.dumps({"stage": "r13-synthetic-upload-generation",
                                             "status": "FAILED", "error": type(error).__name__,
                                             "started_at_utc": started, "failed_at_utc": clock()},
                                            sort_keys=True) + "\n")
            stage_exit.write_text("1\n")
            audit["classification"] = "SYNTHETIC_UPLOAD_GENERATION_FAILED"
            audit["failed_stage"] = "r13-synthetic-upload-generation"
            _write_atomic_json(audit_path, audit)
        except OSError:
            pass
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    mode_parser = sub.add_parser("mode", help="validate a mode card and print its mode")
    mode_parser.add_argument("mode_card", type=Path)
    generate_parser = sub.add_parser("generate", help="generate the fixed-size Cloud payload")
    generate_parser.add_argument("mode_card", type=Path)
    generate_parser.add_argument("evidence", type=Path)
    args = parser.parse_args(argv)
    try:
        mode, _ = read_mode_card(args.mode_card)
        if args.command == "mode":
            print(mode)
            return 0
        if mode != "synthetic-upload":
            raise ValueError("generate command requires synthetic-upload mode")
        evidence = args.evidence
        if not str(evidence).startswith("/workspace/"):
            raise ValueError("R13 synthetic evidence must remain inside /workspace")
        manifest = _generate_synthetic(evidence, args.mode_card, dict(os.environ),
                                       payload_size_bytes=SYNTHETIC_PAYLOAD_BYTES)
        print(json.dumps({"synthetic_upload": "COMPLETE", "payload_bytes": manifest["payload"]["size_bytes"],
                          "payload_sha256": manifest["payload"]["sha256"]}, sort_keys=True))
        return 0
    except Exception as error:
        print(f"R13 synthetic upload refused/failed: {type(error).__name__}: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
