#!/usr/bin/env python3
"""Package Cloud Build evidence without admitting incomplete proof results."""

from __future__ import annotations

import hashlib
import json
import os
import argparse
from pathlib import Path, PurePosixPath
import re
import shutil
import sys
import tarfile
import tempfile


EVIDENCE = Path("/workspace/evidence")
OUT = Path("/workspace/out")
ARCHIVE_NAME = "evidence.tar.gz"
SHA_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
TEXT_LOG_CHUNK_BYTES = 8 * 1024 * 1024
METADATA_MAX_BYTES = 8 * 1024 * 1024
INVENTORY_MAX_BYTES = 8 * 1024 * 1024


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def compact_json_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def parse_json_or_none(value: bytes | None):
    if value is None:
        return None
    try:
        return json.loads(value)
    except (ValueError, UnicodeDecodeError):
        return None


def named_json(payload: dict[str, bytes], *basenames: str) -> dict[str, object]:
    wanted = set(basenames)
    return {path: parsed for path, raw in sorted(payload.items())
            if Path(path).name in wanted and (parsed := parse_json_or_none(raw)) is not None}


def write_text_log_chunks(payload: dict[str, bytes], out: Path) -> tuple[bytes, dict[str, object]]:
    chunk_root = out / "text-logs"
    if chunk_root.is_symlink():
        fail("text-logs output path is a symlink")
    if chunk_root.exists():
        shutil.rmtree(chunk_root)
    chunk_root.mkdir(parents=True)
    entries = []
    chunk_count = 0
    for source_path, data in sorted(payload.items()):
        if Path(source_path).suffix.lower() not in (".log", ".txt"):
            continue
        safe_rel(source_path)
        path_id = hashlib.sha256(source_path.encode("utf-8")).hexdigest()
        try:
            data.decode("utf-8", errors="strict")
            encoding_note = "valid UTF-8; split on code-point boundaries where possible; original bytes preserved"
            utf8 = True
        except UnicodeDecodeError:
            encoding_note = "not valid UTF-8; treated as raw bytes without decoding or modification"
            utf8 = False
        chunks = []
        offset = 0
        index = 0
        while offset < len(data) or index == 0:
            end = min(offset + TEXT_LOG_CHUNK_BYTES, len(data))
            if utf8 and end < len(data):
                while end > offset and (data[end] & 0xC0) == 0x80:
                    end -= 1
            if end <= offset and len(data):
                fail(f"cannot form bounded text chunk for {source_path}")
            part = data[offset:end]
            rel = f"text-logs/{path_id}.part-{index:06d}.txt"
            target = out / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(part)
            chunks.append({"path": rel, "sha256": digest(part), "size_bytes": len(part)})
            chunk_count += 1
            offset = end
            index += 1
            if not data:
                break
        source_sha = digest(data)
        entries.append({
            "source_path": source_path, "sha256": source_sha, "size_bytes": len(data),
            "encoding_note": encoding_note, "chunks": chunks,
            "reconstruction": {"method": "concatenate-in-listed-order",
                               "sha256": source_sha, "size_bytes": len(data)},
        })
    index = {
        "schema_version": 1, "chunk_size_limit_bytes": TEXT_LOG_CHUNK_BYTES,
        "chunk_directory": "text-logs", "source_count": len(entries),
        "chunk_count": chunk_count, "files": entries,
    }
    encoded = (json.dumps(index, sort_keys=True, indent=2) + "\n").encode("utf-8")
    if len(encoded) > METADATA_MAX_BYTES:
        fail("text log index exceeds 8 MiB; cannot publish complete index")
    return encoded, index


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


def collect(root: Path) -> tuple[dict[str, bytes], list[dict[str, object]]]:
    result: dict[str, bytes] = {}
    exclusions = []
    listed = list(root.rglob("*"))
    profile_manifests = {}
    for path in listed:
        rel = path.relative_to(root).as_posix()
        parts = PurePosixPath(rel).parts
        if path.name == "mutation-profile.json" and parts[:2] == ("allprooflogs", "cases") and len(parts) >= 4 and (
                path.parent / "mutation-profile" / "bin").exists():
            if path.is_symlink() or not path.is_file():
                fail(f"mutation profile identity manifest is not a regular file: {rel}")
            raw = path.read_bytes()
            profile = parse_json_or_none(raw)
            identity_fields = ("base_console_sha256", "shadow_console_sha256",
                               "real_exporter_sha256", "wrapper_sha256")
            if not isinstance(profile, dict) or any(
                    not isinstance(profile.get(key), str) or
                    not re.fullmatch(r"[0-9a-f]{64}", profile[key])
                    for key in identity_fields):
                fail(f"mutation profile lacks required hash identities: {rel}")
            profile_manifests[rel] = {"sha256": digest(raw),
                                      "identities": {key: profile[key] for key in identity_fields}}
    for path in sorted(root.rglob("*")):
        rel = safe_rel(path.relative_to(root).as_posix())
        parts = PurePosixPath(rel).parts
        bin_index = next((i for i in range(len(parts) - 1)
                          if parts[i:i + 2] == ("mutation-profile", "bin")), None)
        if bin_index is not None:
            prefix = PurePosixPath(*parts[:bin_index + 2]).as_posix()
            case_manifest = PurePosixPath(*parts[:bin_index], "mutation-profile.json").as_posix()
            identity = profile_manifests.get(case_manifest)
            if identity is None:
                fail(f"refusing mutation tool-tree exclusion without identity manifest: {case_manifest}")
            if path.is_symlink():
                kind = "symlink"
                identity_sha = hashlib.sha256(os.readlink(path).encode("utf-8")).hexdigest()
            elif path.is_dir():
                kind = "directory"
                identity_sha = None
            elif path.is_file():
                kind = "regular-file"
                identity_sha = None
            else:
                fail(f"unsupported mutation profile entry: {rel}")
            exclusions.append({
                "path": rel, "kind": kind, "identity_sha256": identity_sha,
                "case_profile_manifest": case_manifest,
                "case_profile_manifest_sha256": identity["sha256"],
                "mutation_profile_identities": identity["identities"],
                "reason": "Duplicate disposable mutation-profile/bin tool tree; historical REVIEW.md:260 permits excluding */mutation-profile/bin/** after preserving case artifacts.",
            })
            continue
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
    return result, exclusions


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

        payload, artifact_exclusions = collect(args.evidence)
        for reserved in ("summary.json", "manifest.json", "files-sha256.json", "text-logs-index.json"):
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
        config_steps = config.get("steps") if isinstance(config, dict) else None
        first_step = config_steps[0] if isinstance(config_steps, list) and config_steps else None
        env_items = first_step.get("env", []) if isinstance(first_step, dict) else []
        config_env = dict(item.split("=", 1) for item in env_items
                          if isinstance(item, str) and "=" in item) if isinstance(env_items, list) else {}
        source_mode = config_env.get("SOURCE_MODE", "public-git")
        source_certificate = parse_json_or_none(payload.get("source-input-certificate.json"))
        source_valid = source_mode == "public-git"
        if source_mode == "pinned-objects":
            source_valid = (isinstance(source_certificate, dict) and
                isinstance(source_certificate.get("infra"), dict) and
                isinstance(source_certificate.get("proof"), dict) and
                digest(payload.get("source-input.gz", b"")) == config_env.get("SOURCE_INPUT_SHA256") and
                source_certificate.get("archive_sha256") == config_env.get("SOURCE_INPUT_SHA256") and
                source_certificate.get("lane") == lane and
                source_certificate.get("infra", {}).get("commit") == infra_sha and
                source_certificate.get("infra", {}).get("head") == infra_sha and
                source_certificate.get("proof", {}).get("commit") == proof_sha and
                source_certificate.get("proof", {}).get("head") == proof_sha)
        try:
            exit_code = int(payload["run-exit.txt"].decode("ascii").strip())
        except (ValueError, UnicodeDecodeError, KeyError):
            exit_code = None

        audit_path = next((name for name in ("allprooflogs/proof-audit.json", "proof-audit.json")
                           if name in payload), None)
        proof_audit = None
        if audit_path is not None:
            if len(payload[audit_path]) > METADATA_MAX_BYTES:
                fail(f"oversized metadata entry: {audit_path}")
            try:
                proof_audit = json.loads(payload[audit_path])
            except (ValueError, UnicodeDecodeError):
                proof_audit = None
            if not isinstance(proof_audit, dict) or not isinstance(proof_audit.get("accepted"), bool):
                proof_audit = None
        smoke = lane in ("smoke-success", "smoke-error", "smoke-timeout")
        complete = (exit_code is not None and not missing and config_valid and metadata_valid and source_valid)
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
        out = args.out
        out.mkdir(parents=True, exist_ok=True)
        text_logs_index_bytes, text_logs_index = write_text_log_chunks(payload, out)
        text_logs_index_sha = digest(text_logs_index_bytes)
        text_logs_complete = all(path in payload for path in
                                 ("full-stdout.log", "full-stderr.log", "environment.txt"))
        if text_logs_index.get("source_count", 0) == 0:
            text_logs_complete = False
        complete = complete and text_logs_complete
        smoke_success = lane == "smoke-success" and exit_code == 0 and complete
        accepted = (not smoke and exit_code == 0 and proof_audit is not None and
                    proof_audit.get("accepted") is True and complete)
        diagnostic_complete = (not smoke and exit_code == 0 and complete and
                               proof_audit is not None and
                               proof_audit.get("diagnostic_complete") is True)
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
            "diagnostic_complete": diagnostic_complete,
            "text_logs_complete": text_logs_complete,
            "text_logs_index_sha256": text_logs_index_sha,
            "missing_mandatory": (missing + ([] if smoke or case_paths else ["allprooflogs/cases/*"]) +
                                  ([] if smoke or proof_audit is not None else ["allprooflogs/proof-audit.json"]) +
                                  ([] if smoke or stage_artifacts else ["allprooflogs stage logs/resource/exit files"]) +
                                  ([] if config_valid else ["valid submitted config/hash"]) +
                                  ([] if metadata_valid else ["valid build/lane/pin metadata"]) +
                                  ([] if source_valid else ["valid pinned source archive/certificate"]) +
                                  ([] if text_logs_complete else ["complete text-log chunk index"])),
        }
        manifest = {
            **summary,
            "infra_sha": infra_sha, "proof_sha": proof_sha,
            "historical_comparison": parse_json_or_none(payload.get("comparison-manifest.json")),
            "source_delivery": {"mode": source_mode, "valid": source_valid, "certificate": source_certificate},
            "tool_profile": {
                "verifast_source_sha": "f76012fb518703b1d98e243ac4f487f16877cfcb",
                "std_base_sha": "cd371e035c7e573760c43bf934d53e8118ee3e7d",
                "rust_toolchain": "nightly-2026-09-25",
                "compiler_commit": "f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f",
                "patches_in_application_order": ([
                    {"path": "overnight-s6/verifast-s6-26.10-candidate.patch", "sha256": "20f7d07ac9bdaca7c46f737b89925dfac3f4cef66c3f5d48aa9634ac949dbc1c"},
                    {"path": "verifast-manuallydrop-new-cfg-2610.patch", "sha256": "593d09405379974ffbc475c2e0b65d648d8a6913f55b765dd0c3bebdc0922781"},
                ] if lane == "constructor" else []),
                "scope": "constructor-only historical component" if lane == "constructor" else "stock baseline" if lane == "stock" else "no proof tools executed",
            },
            "pins": {"infra_sha": infra_sha, "proof_sha": proof_sha,
                     "submitted_config_sha256": config_sha,
                     "proof_image": proof_image},
            "submitted_config_sha256": config_sha,
            "submitted_config_actual_sha256": digest(config_bytes),
            "proof_image": proof_image,
            "invalid_pins": invalid_pins,
            "config_fields_reference": {
                "path": "submitted-config.json",
                "sha256": digest(config_bytes),
                "size_bytes": len(config_bytes),
            },
            "input_sha256": {p: digest(b) for p, b in sorted(payload.items())},
            "environment": {k: v for k, v in sorted(env.items())
                            if k.startswith("SMALLSORT_") and not any(
                                secret in k.upper() for secret in ("TOKEN", "KEY", "PASSWORD", "CREDENTIAL", "SECRET"))},
            "profile_hashes": named_json(payload, "profile-hashes.json"),
            "tools": named_json(payload, "tools.json", "binary-hashes.json",
                                "profile-binary-hashes.json"),
            "specification_hashes": named_json(payload, "stock-spec-hashes.json", "spec-audit.json"),
            "source_component_hashes": named_json(payload, "source-component-hashes.json"),
            "std_export_source": named_json(payload, "std-export-source.json"),
            "provider_overlays": named_json(payload, "provider-overlay-manifest.json"),
            "artifact_exclusions": {
                "patterns": ["*/mutation-profile/bin/**"],
                "justification": "Duplicate disposable MIR mutation tool trees are excluded as allowed by research/challenge-8/overnight-s6/REVIEW.md:260; all case sources, wrappers, mutation records, MIR, logs, fixture and classification files remain included.",
                "entries": artifact_exclusions,
            },
            "text_log_delivery": {
                "mode": "external-byte-exact-chunks",
                "index_path": "text-logs-index.json",
                "index_sha256": text_logs_index_sha,
                "index_size_bytes": len(text_logs_index_bytes),
                "chunk_size_limit_bytes": TEXT_LOG_CHUNK_BYTES,
                "source_count": text_logs_index["source_count"],
                "chunk_count": text_logs_index["chunk_count"],
                "complete": text_logs_complete,
                "reconstruction": "concatenate listed chunks in order; verify source SHA-256 and byte size",
            },
            "proof_audit": proof_audit,
            "proof_audit_path": audit_path,
            "proof_stage_artifacts": stage_artifacts,
            "smoke_scope": "infrastructure-probe-only" if smoke else None,
            "environment_sha256": (digest(payload["environment.txt"])
                                    if "environment.txt" in payload else None),
            "inventory_excludes": ["manifest.json", "files-sha256.json"],
        }
        # Replace only this package's known output names; preserve unrelated files.
        files = dict(payload)
        files["text-logs-index.json"] = text_logs_index_bytes
        files["summary.json"] = (json.dumps(summary, sort_keys=True, indent=2) + "\n").encode()
        if config_bytes:
            files["submitted-config.json"] = config_bytes
        inventory = {p: digest(b) for p, b in sorted(files.items())}
        files["files-sha256.json"] = (json.dumps(inventory, sort_keys=True, indent=2) + "\n").encode()
        if len(files["files-sha256.json"]) > INVENTORY_MAX_BYTES:
            fail("file hash inventory exceeds 8 MiB")
        manifest["files_inventory_sha256"] = digest(files["files-sha256.json"])
        # The manifest repeats parsed proof-audit and input-hash data that also
        # live in canonical archive members. Keep the established schema and
        # every value, but serialize without indentation so structural data
        # does not consume the external 8 MiB metadata allowance twice over.
        # verify-evidence.py compares decoded JSON values, not their whitespace.
        files["manifest.json"] = compact_json_bytes(manifest)
        if len(files["summary.json"]) > METADATA_MAX_BYTES:
            fail("external summary exceeds 8 MiB")
        if len(files["manifest.json"]) > METADATA_MAX_BYTES:
            field_sizes = sorted(
                ((key, len(compact_json_bytes(value)) - 1) for key, value in manifest.items()),
                key=lambda item: (-item[1], item[0]))
            largest = ",".join(f"{key}={size}" for key, size in field_sizes[:5])
            fail(f"external manifest exceeds 8 MiB: encoded_bytes={len(files['manifest.json'])} "
                 f"limit_bytes={METADATA_MAX_BYTES}; largest_5_field_values_bytes={largest}")

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
        (out / "text-logs-index.json").write_bytes(text_logs_index_bytes)
        archive_sha = digest_file(archive)
        (out / "archive.sha256").write_text(f"{archive_sha}  {ARCHIVE_NAME}\n")
        print(json.dumps({**summary, "archive_sha256": archive_sha}, sort_keys=True))
        return 0
    except Exception as exc:
        print(f"evidence packaging failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
