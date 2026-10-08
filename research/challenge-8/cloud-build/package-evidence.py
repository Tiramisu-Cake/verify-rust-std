#!/usr/bin/env python3
"""Package Cloud Build evidence without admitting incomplete proof results."""

from __future__ import annotations

import hashlib
import json
import os
import argparse
from pathlib import Path, PurePosixPath
import re
import sys
import tarfile
import tempfile


EVIDENCE = Path("/workspace/evidence")
OUT = Path("/workspace/out")
ARCHIVE_NAME = "evidence.tar.gz"
SHA_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_json_or_none(value: bytes | None):
    if value is None:
        return None
    try:
        return json.loads(value)
    except (ValueError, UnicodeDecodeError):
        return None


def cloud_config_matches(config, lane: str, infra_sha: str, proof_sha: str,
                         proof_image: str) -> bool:
    if not isinstance(config, dict):
        return False
    steps = config.get("steps")
    if not isinstance(steps, list) or not steps or not isinstance(steps[0], dict):
        return False
    step = steps[0]
    if step.get("id") != "execute":
        return False
    env = step.get("env")
    if not isinstance(env, list):
        return False
    values = {}
    for item in env:
        if isinstance(item, str) and "=" in item:
            key, value = item.split("=", 1)
            values[key] = value
    return (values.get("LANE") == lane and values.get("INFRA_SHA") == infra_sha and
            values.get("PROOF_SHA") == proof_sha and
            (not proof_image or step.get("name") == proof_image))
def fail(message: str) -> None:
    raise ValueError(message)


def safe_rel(rel: str) -> str:
    p = PurePosixPath(rel)
    if p.is_absolute() or not p.parts or any(part in ("", ".", "..") for part in p.parts):
        fail(f"unsafe archive path: {rel}")
    return p.as_posix()


def collect(root: Path) -> dict[str, bytes]:
    result: dict[str, bytes] = {}
    for path in sorted(root.rglob("*")):
        rel = safe_rel(path.relative_to(root).as_posix())
        if any(part.lower() in {"home", "credential", "credentials", "toolchain", "toolchains"}
               for part in PurePosixPath(rel).parts):
            fail(f"private/toolchain path forbidden in evidence input: {rel}")
        if path.is_symlink():
            fail(f"symlink in evidence: {rel}")
        if path.is_dir():
            continue
        if not path.is_file():
            fail(f"non-regular evidence entry: {rel}")
        result[rel] = path.read_bytes()
    return result


def main() -> int:
    try:
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument("--evidence", type=Path, default=EVIDENCE)
        parser.add_argument("--out", type=Path, default=OUT)
        args = parser.parse_args()
        env = os.environ
        build_id = env.get("CLOUD_BUILD_ID", "").strip()
        infra_sha = env.get("INFRA_SHA", "").lower()
        proof_sha = env.get("PROOF_SHA", "").lower()
        lane = env.get("LANE", "").strip()
        config_sha = env.get("SUBMITTED_CONFIG_SHA", "").lower()
        proof_image = env.get("PROOF_IMAGE", "")
        invalid_pins = [name for name, value in (("INFRA_SHA", infra_sha), ("PROOF_SHA", proof_sha),
                                                   ("SUBMITTED_CONFIG_SHA", config_sha))
                        if not SHA_RE.fullmatch(value)]
        metadata_valid = bool(build_id and lane and not invalid_pins)

        payload = collect(args.evidence)
        for reserved in ("summary.json", "manifest.json", "files-sha256.json"):
            if reserved in payload:
                payload[f"input-{reserved}"] = payload.pop(reserved)
        required = ("run-exit.txt", "full-stdout.log", "full-stderr.log",
                    "submitted-config.json", "environment.txt")
        missing = [name for name in required if name not in payload]
        case_paths = [p for p in payload if p.startswith("allprooflogs/cases/")]

        config_bytes = payload.get("submitted-config.json", b"")
        config_valid = bool(config_bytes) and digest(config_bytes) == config_sha
        if not config_bytes:
            config_bytes = b'{"missing":true}\n'
        try:
            config = json.loads(config_bytes) if config_bytes else None
        except (ValueError, UnicodeDecodeError):
            config = None
            config_valid = False
        config_valid = (config_valid and cloud_config_matches(
            config, lane, infra_sha, proof_sha, proof_image))
        try:
            exit_code = int(payload["run-exit.txt"].decode("ascii").strip())
        except (ValueError, UnicodeDecodeError, KeyError):
            exit_code = None

        audit_path = next((name for name in ("allprooflogs/proof-audit.json", "proof-audit.json")
                           if name in payload), None)
        proof_audit = None
        if audit_path is not None:
            try:
                proof_audit = json.loads(payload[audit_path])
            except (ValueError, UnicodeDecodeError):
                proof_audit = None
            if not isinstance(proof_audit, dict) or not isinstance(proof_audit.get("accepted"), bool):
                proof_audit = None
        smoke = lane in ("smoke-success", "smoke-error", "smoke-timeout")
        complete = (exit_code is not None and not missing and config_valid and metadata_valid)
        if not smoke:
            stage_artifacts = [p for p in payload if p.startswith("allprooflogs/") and
                               not p.startswith("allprooflogs/cases/") and
                               (p.endswith(".log") or p.endswith("-exit-code.txt") or
                                p.endswith("-resources.txt"))]
            complete = complete and bool(case_paths) and proof_audit is not None and bool(stage_artifacts)
        else:
            stage_artifacts = []
        if not smoke and proof_audit is None:
            complete = False
        smoke_success = lane == "smoke-success" and exit_code == 0 and complete
        accepted = (not smoke and exit_code == 0 and proof_audit is not None and
                    proof_audit.get("accepted") is True and complete)
        if lane == "smoke-error" and exit_code == 42:
            failure_class = "infrastructure-probe-error"
        elif lane == "smoke-timeout" and exit_code == 124:
            failure_class = "infrastructure-probe-timeout"
        elif exit_code is None:
            failure_class = "incomplete-or-unknown-status"
        elif exit_code != 0:
            failure_class = "run-failed"
        elif not complete:
            failure_class = "incomplete-evidence"
        else:
            failure_class = "none"

        summary = {
            "schema_version": 1, "build_id": build_id, "lane": lane,
            "run_exit_code": exit_code, "failure_class": failure_class,
            "evidence_complete": complete, "smoke_success": smoke_success,
            "verification_accepted": accepted,
            "missing_mandatory": (missing + ([] if smoke or case_paths else ["allprooflogs/cases/*"]) +
                                  ([] if smoke or proof_audit is not None else ["allprooflogs/proof-audit.json"]) +
                                  ([] if smoke or stage_artifacts else ["allprooflogs stage logs/resource/exit files"]) +
                                  ([] if config_valid else ["valid submitted config/hash"]) +
                                  ([] if metadata_valid else ["valid build/lane/pin metadata"])),
        }
        manifest = {
            **summary,
            "infra_sha": infra_sha, "proof_sha": proof_sha,
            "pins": {"infra_sha": infra_sha, "proof_sha": proof_sha,
                     "submitted_config_sha256": config_sha,
                     "proof_image": proof_image},
            "submitted_config_sha256": config_sha,
            "submitted_config_actual_sha256": digest(config_bytes),
            "proof_image": proof_image,
            "invalid_pins": invalid_pins,
            "config_fields": config if isinstance(config, dict) else None,
            "input_sha256": {p: digest(b) for p, b in sorted(payload.items())},
            "environment": {k: v for k, v in sorted(env.items())
                            if k.startswith("SMALLSORT_") and not any(
                                secret in k.upper() for secret in ("TOKEN", "KEY", "PASSWORD", "CREDENTIAL", "SECRET"))},
            "profile_hashes": parse_json_or_none(next((v for k, v in sorted(payload.items())
                                                        if Path(k).name == "profile-hashes.json"), None)),
            "tools": parse_json_or_none(next((v for k, v in sorted(payload.items())
                                               if Path(k).name == "tools.json"), None)),
            "proof_audit": proof_audit,
            "proof_audit_path": audit_path,
            "proof_stage_artifacts": stage_artifacts,
            "smoke_scope": "infrastructure-probe-only" if smoke else None,
            "environment_sha256": (digest(payload["environment.txt"])
                                    if "environment.txt" in payload else None),
            "inventory_excludes": ["manifest.json", "files-sha256.json"],
        }
        out = args.out
        out.mkdir(parents=True, exist_ok=True)
        # Replace only this package's known output names; preserve unrelated files.
        files = dict(payload)
        files["summary.json"] = (json.dumps(summary, sort_keys=True, indent=2) + "\n").encode()
        if config_bytes:
            files["submitted-config.json"] = config_bytes
        inventory = {p: digest(b) for p, b in sorted(files.items())}
        files["files-sha256.json"] = (json.dumps(inventory, sort_keys=True, indent=2) + "\n").encode()
        manifest["files_inventory_sha256"] = digest(files["files-sha256.json"])
        files["manifest.json"] = (json.dumps(manifest, sort_keys=True, indent=2) + "\n").encode()

        archive = out / ARCHIVE_NAME
        with tempfile.NamedTemporaryFile(dir=out, prefix=".evidence-", delete=False) as tmp:
            temp_name = tmp.name
        try:
            with tarfile.open(temp_name, "w:gz") as tar:
                for rel, data in sorted(files.items()):
                    info = tarfile.TarInfo(safe_rel(rel))
                    info.size = len(data)
                    info.mode = 0o644
                    import io
                    tar.addfile(info, io.BytesIO(data))
            Path(temp_name).replace(archive)
        finally:
            Path(temp_name).unlink(missing_ok=True)
        (out / "summary.json").write_bytes(files["summary.json"])
        (out / "manifest.json").write_bytes(files["manifest.json"])
        if config_bytes:
            (out / "submitted-config.json").write_bytes(config_bytes)
        (out / "files-sha256.json").write_bytes(files["files-sha256.json"])
        archive_sha = digest_file(archive)
        (out / "archive.sha256").write_text(f"{archive_sha}  {ARCHIVE_NAME}\n")
        print(json.dumps({**summary, "archive_sha256": archive_sha}, sort_keys=True))
        return 0
    except Exception as exc:
        print(f"evidence packaging failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
