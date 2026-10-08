#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted-only cache for one SHA-pinned source-built VeriFast console."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import sys
import tempfile
from pathlib import Path


PROFILE_ID = "vf26.10-w1-m2-c1-cleanup-usize-ubuntu22.04-v1"
SCHEMA = "vf-source-console-cache-v1"
CONSOLE_SHA256 = "3a08722cedc2f07daf26dfde2f46b8710662028ca5924212c4d1d92d68b70f1a"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
GIT_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
REQUIRED_PROFILE_KEYS = {
    "profile_id", "runner_os", "runner_version", "source_commit",
    "wrapping_patch", "callback_patch", "copy_patch", "cleanup_patch", "usize_patch",
    "release_console", "release_exporter", "release_refiner", "vfdeps_archive",
    "decoder_revision", "build_toolchain", "build_script", "cache_helper", "applied_patch",
    "kernel_original", "kernel_patched", "translator_original", "translator_patched",
    "parser_original", "parser_patched", "prelude_original", "prelude_patched",
    "stdlib_original", "stdlib_patched", "z3_runtime",
}


class CacheMiss(Exception):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hosted_guard() -> None:
    if (os.environ.get("GITHUB_ACTIONS") != "true" or
            os.environ.get("RUNNER_ENVIRONMENT") != "github-hosted" or
            os.environ.get("RUNNER_OS") != "Linux"):
        raise RuntimeError("console cache is restricted to GitHub-hosted Linux Actions")
    if os.environ.get("GITHUB_REF") != "refs/heads/overnight/merge-26.10":
        raise RuntimeError("console cache is restricted to overnight/merge-26.10")
    if not GIT_SHA_RE.fullmatch(os.environ.get("GITHUB_SHA", "")):
        raise RuntimeError("a full GITHUB_SHA is required for console-cache provenance")


def read_profile(path: Path) -> tuple[bytes, dict[str, str]]:
    raw = path.read_bytes()
    try:
        lines = raw.decode("ascii").splitlines()
    except UnicodeDecodeError as exc:
        raise CacheMiss("profile is not ASCII") from exc
    values: dict[str, str] = {}
    for line in lines:
        if not line or "=" not in line:
            raise CacheMiss("profile has a malformed or empty line")
        key, value = line.split("=", 1)
        if not re.fullmatch(r"[a-z][a-z0-9_]*", key) or not value or key in values:
            raise CacheMiss("profile has an invalid or duplicate key/value")
        if "\r" in value or "\n" in value:
            raise CacheMiss("profile value contains a newline")
        values[key] = value
    if values.get("profile_id") != PROFILE_ID:
        raise CacheMiss("current build profile ID does not match the admitted cache profile")
    if set(values) != REQUIRED_PROFILE_KEYS:
        raise CacheMiss("profile input set differs from the reviewed cache contract")
    for key, value in values.items():
        if key.endswith(("patch", "console", "exporter", "refiner", "archive", "toolchain",
                         "script", "helper", "applied_patch", "original", "patched", "runtime")):
            if key in {"decoder_revision", "source_commit"}:
                continue
            if not SHA256_RE.fullmatch(value):
                raise CacheMiss(f"profile field {key} is not a SHA-256")
    if not GIT_SHA_RE.fullmatch(values["source_commit"]):
        raise CacheMiss("source commit is not a full Git SHA")
    return raw, values


def manifest_for(profile: bytes, producer_sha: str) -> dict[str, str]:
    return {
        "schema": SCHEMA,
        "profile_id": PROFILE_ID,
        "profile_sha256": sha256(profile),
        "console_sha256": CONSOLE_SHA256,
        "producer_actions_sha": producer_sha,
        "producer_actions_ref": "refs/heads/overnight/merge-26.10",
        "producer_runner_environment": "github-hosted",
        "producer_runner_os": "Linux",
    }


def manifest_bytes(manifest: dict[str, str]) -> bytes:
    return (json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")


def regular_file(path: Path) -> bool:
    try:
        mode = path.lstat().st_mode
    except OSError:
        return False
    return stat.S_ISREG(mode)


def validate_cache(cache_dir: Path, profile: bytes) -> tuple[dict[str, str], bytes]:
    try:
        mode = cache_dir.lstat().st_mode
    except OSError as exc:
        raise CacheMiss("cache directory is absent") from exc
    if not stat.S_ISDIR(mode):
        raise CacheMiss("cache path is not a real directory")
    names = {entry.name for entry in cache_dir.iterdir()}
    if names != {"manifest.json", "verifast"}:
        raise CacheMiss("cache directory must contain only manifest.json and verifast")
    manifest_path = cache_dir / "manifest.json"
    binary_path = cache_dir / "verifast"
    if not regular_file(manifest_path) or not regular_file(binary_path):
        raise CacheMiss("cache manifest and console must be regular non-symlink files")
    raw_manifest = manifest_path.read_bytes()
    try:
        manifest = json.loads(raw_manifest)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CacheMiss("cache manifest is invalid JSON") from exc
    if not isinstance(manifest, dict) or set(manifest) != {
            "schema", "profile_id", "profile_sha256", "console_sha256", "producer_actions_sha",
            "producer_actions_ref", "producer_runner_environment", "producer_runner_os"}:
        raise CacheMiss("cache manifest fields differ from the reviewed schema")
    try:
        canonical = manifest_bytes(manifest)
    except (TypeError, ValueError, UnicodeEncodeError) as exc:
        raise CacheMiss("cache manifest contains unsupported values") from exc
    if raw_manifest != canonical:
        raise CacheMiss("cache manifest is not in canonical encoding")
    producer_sha = manifest.get("producer_actions_sha")
    if not isinstance(producer_sha, str) or not GIT_SHA_RE.fullmatch(producer_sha):
        raise CacheMiss("producer Actions SHA is malformed")
    expected = manifest_for(profile, producer_sha)
    if manifest != expected:
        raise CacheMiss("cache manifest does not match current profile and admitted console")
    payload = binary_path.read_bytes()
    if sha256(payload) != CONSOLE_SHA256:
        raise CacheMiss("cached console bytes do not match the admitted console SHA-256")
    return manifest, payload


def record(evidence: Path, name: str, value: dict) -> None:
    evidence.mkdir(parents=True, exist_ok=True)
    target = evidence / name
    if target.exists():
        raise RuntimeError(f"refusing to overwrite cache evidence: {target}")
    target.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def restore(cache_dir: Path, profile_path: Path, destination: Path, evidence: Path) -> bool:
    try:
        profile, _ = read_profile(profile_path)
    except CacheMiss as exc:
        record(evidence, "console-cache-restore.json", {"mode": "miss", "reason": str(exc)})
        print(f"Console cache miss: {exc}", file=sys.stderr)
        return False
    result: dict = {"mode": "miss", "profile_sha256": sha256(profile)}
    try:
        manifest, payload = validate_cache(cache_dir, profile)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=destination.parent, prefix=".verifast-cache-", delete=False) as tmp:
            tmp.write(payload)
            tmp_path = Path(tmp.name)
        os.chmod(tmp_path, 0o755)
        if sha256(tmp_path.read_bytes()) != CONSOLE_SHA256:
            tmp_path.unlink(missing_ok=True)
            raise CacheMiss("temporary installed console failed SHA-256 recheck")
        os.replace(tmp_path, destination)
        if sha256(destination.read_bytes()) != CONSOLE_SHA256:
            raise RuntimeError("installed console failed post-copy SHA-256 recheck")
        result.update({"mode": "hit", "reason": "exact profile and admitted payload verified",
                       "producer_actions_sha": manifest["producer_actions_sha"],
                       "console_sha256": CONSOLE_SHA256})
    except CacheMiss as exc:
        result["reason"] = str(exc)
        record(evidence, "console-cache-restore.json", result)
        print(f"Console cache miss: {exc}", file=sys.stderr)
        return False
    record(evidence, "console-cache-restore.json", result)
    return True


def publish(cache_dir: Path, profile_path: Path, binary: Path,
            evidence: Path, producer_sha: str) -> bool:
    try:
        profile, _ = read_profile(profile_path)
    except CacheMiss as exc:
        record(evidence, "console-cache-publish.json", {
            "mode": "not_published", "reason": str(exc)})
        return False
    result: dict = {"mode": "not_published", "profile_sha256": sha256(profile)}
    if not GIT_SHA_RE.fullmatch(producer_sha):
        result["reason"] = "producer Actions SHA is malformed"
    elif not regular_file(binary):
        result["reason"] = "built console is not a regular file"
    elif sha256(binary.read_bytes()) != CONSOLE_SHA256:
        result["reason"] = "built console differs from the admitted console SHA-256"
    else:
        manifest = manifest_for(profile, producer_sha)
        if cache_dir.is_symlink() or (cache_dir.exists() and not cache_dir.is_dir()):
            result["reason"] = "cache destination is not a real directory; refusing to replace it"
        elif cache_dir.exists() and any(cache_dir.iterdir()):
            result["reason"] = "cache destination is nonempty; refusing to replace it"
        else:
            if cache_dir.exists():
                cache_dir.rmdir()
            cache_dir.parent.mkdir(parents=True, exist_ok=True)
            staging = Path(tempfile.mkdtemp(prefix=".console-cache-", dir=cache_dir.parent))
            try:
                shutil.copyfile(binary, staging / "verifast")
                os.chmod(staging / "verifast", 0o755)
                (staging / "manifest.json").write_bytes(manifest_bytes(manifest))
                validate_cache(staging, profile)
                os.rename(staging, cache_dir)
                result.update({"mode": "published", "producer_actions_sha": producer_sha,
                               "console_sha256": CONSOLE_SHA256})
            except Exception:
                shutil.rmtree(staging, ignore_errors=True)
                raise
    record(evidence, "console-cache-publish.json", result)
    if result["mode"] != "published":
        print(f"Console cache not published: {result['reason']}", file=sys.stderr)
        return False
    return True


def self_test(profile_path: Path, binary: Path, evidence: Path) -> bool:
    profile, _ = read_profile(profile_path)
    payload = binary.read_bytes()
    if sha256(payload) != CONSOLE_SHA256:
        record(evidence, "console-cache-self-test.json", {
            "status": "not_run", "reason": "no admitted console bytes available"})
        return False
    producer = os.environ["GITHUB_SHA"]
    manifest = manifest_for(profile, producer)
    checks: dict[str, bool] = {}
    with tempfile.TemporaryDirectory(prefix="console-cache-audit-") as temp:
        root = Path(temp)

        def directory(name: str, current_manifest: dict[str, str] = manifest,
                      current_payload: bytes = payload, extra: bool = False,
                      symlink: bool = False) -> Path:
            target = root / name
            target.mkdir()
            (target / "manifest.json").write_bytes(manifest_bytes(current_manifest))
            if symlink:
                (target / "verifast").symlink_to(binary)
            else:
                (target / "verifast").write_bytes(current_payload)
            if extra:
                (target / "unexpected").write_text("extra")
            return target

        good = directory("good")
        try:
            validate_cache(good, profile)
            checks["valid_exact_cache_accepted"] = True
        except CacheMiss:
            checks["valid_exact_cache_accepted"] = False
        bad_key = dict(manifest, profile_sha256="0" * 64)
        checks["wrong_profile_key_rejected"] = rejects(directory("bad-key", bad_key), profile)
        bad_console = dict(manifest, console_sha256="0" * 64)
        checks["wrong_console_hash_rejected"] = rejects(directory("bad-console", bad_console), profile)
        bad_producer = dict(manifest, producer_actions_sha="not-a-sha")
        checks["bad_producer_sha_rejected"] = rejects(directory("bad-producer", bad_producer), profile)
        checks["corrupt_payload_rejected"] = rejects(directory("corrupt", manifest,
                                                               payload[:-1] + bytes([payload[-1] ^ 1])), profile)
        missing_payload = root / "missing-payload"
        missing_payload.mkdir()
        (missing_payload / "manifest.json").write_bytes(manifest_bytes(manifest))
        checks["missing_payload_rejected"] = rejects(missing_payload, profile)
        checks["extra_file_rejected"] = rejects(directory("extra", manifest, extra=True), profile)
        checks["symlink_payload_rejected"] = rejects(directory("symlink", manifest, symlink=True), profile)
        # Invalid restores must not create or overwrite the requested target.
        destination = root / "protected-output"
        destination.write_bytes(b"sentinel")
        profile_path = root / "profile.txt"
        profile_path.write_bytes(profile)
        restored = restore(root / "corrupt", profile_path, destination, root / "audit-evidence")
        checks["invalid_cache_does_not_change_destination"] = (
            not restored and destination.read_bytes() == b"sentinel")
    result = {"status": "PASS" if all(checks.values()) else "FAIL",
              "profile_sha256": sha256(profile), "checks": checks}
    record(evidence, "console-cache-self-test.json", result)
    return result["status"] == "PASS"


def rejects(cache_dir: Path, profile: bytes) -> bool:
    try:
        validate_cache(cache_dir, profile)
        return False
    except CacheMiss:
        return True


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    restore_parser = sub.add_parser("restore")
    restore_parser.add_argument("--cache-dir", type=Path, required=True)
    restore_parser.add_argument("--profile", type=Path, required=True)
    restore_parser.add_argument("--destination", type=Path, required=True)
    restore_parser.add_argument("--evidence", type=Path, required=True)
    publish_parser = sub.add_parser("publish")
    publish_parser.add_argument("--cache-dir", type=Path, required=True)
    publish_parser.add_argument("--profile", type=Path, required=True)
    publish_parser.add_argument("--binary", type=Path, required=True)
    publish_parser.add_argument("--evidence", type=Path, required=True)
    publish_parser.add_argument("--producer-sha", required=True)
    audit_parser = sub.add_parser("self-test")
    audit_parser.add_argument("--profile", type=Path, required=True)
    audit_parser.add_argument("--binary", type=Path, required=True)
    audit_parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    hosted_guard()
    if args.command == "restore":
        return 0 if restore(args.cache_dir, args.profile, args.destination, args.evidence) else 1
    if args.command == "publish":
        return 0 if publish(args.cache_dir, args.profile, args.binary, args.evidence,
                            args.producer_sha) else 1
    return 0 if self_test(args.profile, args.binary, args.evidence) else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print(f"console cache error: {error}", file=sys.stderr)
        sys.exit(2)
