#!/usr/bin/env python3
"""Fail-closed archive size and publication-mode check; this module never uploads."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import stat
import sys
import uuid
from collections.abc import Mapping

MODE_SCHEMA = "merge-r13-upload-mode-v1"
POLICY_SCHEMA = "smallsort-upload-policy-v1"
ARCHIVE_LIMIT_BYTES = 536_870_912
SYNTHETIC_PAYLOAD_BYTES = 268_435_456
DOCUMENTED_THRESHOLD_BYTES = 157_286_400
THRESHOLD_SOURCE = "https://docs.cloud.google.com/storage/docs/parallel-composite-uploads"
SHA1_RE = re.compile(r"[0-9a-f]{40}\Z")
HUMAN_SIZE_RE = re.compile(r"([1-9][0-9]*)([KMGT]?)(?:i?B)?\Z", re.IGNORECASE)


def parse_sdk_threshold(value: object) -> int:
    """Parse the positive byte or binary human-unit values accepted by gcloud."""
    if not isinstance(value, str):
        raise ValueError("effective SDK threshold must be a string")
    text = value.strip()
    match = HUMAN_SIZE_RE.fullmatch(text)
    if not match:
        raise ValueError("effective SDK threshold is missing or malformed")
    magnitude = int(match.group(1))
    unit = match.group(2).upper()
    multiplier = 1024 ** ("KMG T".replace(" ", "").index(unit) + 1) if unit else 1
    return magnitude * multiplier


def _failure(diag: dict, reason: str) -> dict:
    diag["accepted"] = False
    diag["reason"] = reason
    return diag


def validate_archive_size(size: object, card: object, policy: object, env: object) -> dict:
    """Pure validator returning a compact diagnostic for acceptance or refusal."""
    env = env if isinstance(env, Mapping) else {}
    card_obj = card if isinstance(card, dict) else {}
    mode = card_obj.get("mode") if isinstance(card_obj.get("mode"), str) else None
    diag = {
        "actual_archive_bytes": size if type(size) is int and size >= 0 else None,
        "archive_limit_bytes": ARCHIVE_LIMIT_BYTES,
        "effective_threshold_bytes": None,
        "mode": mode,
        "threshold_source": card_obj.get("threshold_source") if isinstance(card_obj.get("threshold_source"), str) else None,
        "source": {"infra_sha": env.get("INFRA_SHA"), "proof_sha": env.get("PROOF_SHA")},
        "build_id": env.get("CLOUD_BUILD_ID"),
        "accepted": False,
        "reason": "unvalidated",
    }
    if type(size) is not int or size < 0:
        return _failure(diag, "actual archive size must be a nonnegative integer")
    if not isinstance(card, dict) or card.get("schema") != MODE_SCHEMA:
        return _failure(diag, "R13 mode card has an unknown schema")
    if mode == "synthetic-upload":
        expected = {"schema", "mode", "payload_bytes", "threshold_bytes", "archive_limit_bytes",
                    "threshold_source", "proof_attempted"}
        if set(card) != expected:
            return _failure(diag, "R13 synthetic mode card has an invalid field set")
        if (type(card.get("payload_bytes")) is not int or card["payload_bytes"] != SYNTHETIC_PAYLOAD_BYTES or
                type(card.get("threshold_bytes")) is not int or card["threshold_bytes"] != DOCUMENTED_THRESHOLD_BYTES or
                type(card.get("archive_limit_bytes")) is not int or card["archive_limit_bytes"] != ARCHIVE_LIMIT_BYTES or
                card.get("threshold_source") != THRESHOLD_SOURCE or card.get("proof_attempted") is not False):
            return _failure(diag, "R13 synthetic mode card disagrees with the reviewed size contract")
    elif mode == "proof-r11":
        if set(card) != {"schema", "mode", "archive_limit_bytes"}:
            return _failure(diag, "R13 proof mode card has an invalid field set")
        if type(card.get("archive_limit_bytes")) is not int or card["archive_limit_bytes"] != ARCHIVE_LIMIT_BYTES:
            return _failure(diag, "R13 proof mode card has the wrong archive limit")
    else:
        return _failure(diag, "R13 mode card is neither synthetic-upload nor proof-r11")

    if not isinstance(policy, dict) or policy.get("schema") != POLICY_SCHEMA:
        return _failure(diag, "upload policy is missing or has an unknown schema")
    if policy.get("parallel_composite_upload_enabled_effective") != "False":
        return _failure(diag, "effective parallel composite upload policy is not False")
    try:
        threshold = parse_sdk_threshold(policy.get("parallel_composite_upload_threshold"))
    except ValueError as error:
        return _failure(diag, str(error))
    diag["effective_threshold_bytes"] = threshold

    for key, env_key in (("infra_sha", "INFRA_SHA"), ("proof_sha", "PROOF_SHA")):
        identity = env.get(env_key)
        if not isinstance(identity, str) or not SHA1_RE.fullmatch(identity):
            return _failure(diag, f"{env_key} must be a full lowercase 40-digit SHA")
        if policy.get(key) != identity:
            return _failure(diag, f"upload policy {key} does not match the runtime environment")
    build_id = env.get("CLOUD_BUILD_ID")
    if not isinstance(build_id, str):
        return _failure(diag, "CLOUD_BUILD_ID is missing")
    try:
        parsed_build = uuid.UUID(build_id)
    except (ValueError, AttributeError):
        return _failure(diag, "CLOUD_BUILD_ID must be a UUID")
    if str(parsed_build) != build_id.lower() or policy.get("build_id") != build_id:
        return _failure(diag, "upload policy build_id does not match the runtime UUID")

    if size > ARCHIVE_LIMIT_BYTES:
        return _failure(diag, "compressed archive exceeds the 536870912-byte publication limit")
    if mode == "synthetic-upload" and size <= threshold:
        return _failure(diag, "synthetic archive must exceed the effective SDK composite threshold")
    diag["accepted"] = True
    diag["reason"] = "archive size and publication policy accepted"
    return diag


def _read_json(path: Path, label: str):
    try:
        mode = path.lstat().st_mode
    except OSError as error:
        raise ValueError(f"{label} is unavailable: {error.strerror or type(error).__name__}") from error
    if stat.S_ISLNK(mode) or not stat.S_ISREG(mode):
        raise ValueError(f"{label} must be a regular non-symlink file")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeDecodeError) as error:
        raise ValueError(f"{label} is not readable valid JSON") from error


def _write_diagnostic(path: Path, diagnostic: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(diagnostic, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--mode-card", required=True, type=Path)
    parser.add_argument("--policy", required=True, type=Path)
    parser.add_argument("--diagnostic", required=True, type=Path)
    args = parser.parse_args(argv)

    base = {
        "actual_archive_bytes": None, "archive_limit_bytes": ARCHIVE_LIMIT_BYTES,
        "effective_threshold_bytes": None, "mode": None, "threshold_source": None,
        "source": {"infra_sha": os.environ.get("INFRA_SHA"), "proof_sha": os.environ.get("PROOF_SHA")},
        "build_id": os.environ.get("CLOUD_BUILD_ID"), "accepted": False,
    }
    try:
        try:
            archive_mode = args.archive.lstat().st_mode
        except OSError as error:
            raise ValueError(f"archive is unavailable: {error.strerror or type(error).__name__}") from error
        if stat.S_ISLNK(archive_mode) or not stat.S_ISREG(archive_mode):
            raise ValueError("archive must be a regular non-symlink file")
        size = args.archive.stat().st_size
        base["actual_archive_bytes"] = size
        card = _read_json(args.mode_card, "R13 mode card")
        policy = _read_json(args.policy, "upload policy")
        diagnostic = validate_archive_size(size, card, policy, os.environ)
    except (OSError, ValueError) as error:
        base["reason"] = str(error)
        diagnostic = base
    _write_diagnostic(args.diagnostic, diagnostic)
    print(json.dumps(diagnostic, sort_keys=True))
    return 0 if diagnostic.get("accepted") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
