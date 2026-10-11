#!/usr/bin/env python3
"""Isolated pinned-object transport roundtrip; never imports proof tooling."""

from __future__ import annotations

import base64
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile


HERE = Path(__file__).resolve()
REPO = HERE.parents[4]
SOURCE_INPUT = REPO / "research/challenge-8/cloud-build/source-input.py"
RECEIPT = HERE.with_name("SOURCE-INPUT-TRANSPORT-SERVICE-RECEIPT.json")
LIMIT_PARTS = 191
PART_CHARS = 3990


def load_source_input():
    spec = importlib.util.spec_from_file_location("source_input_transport_test", SOURCE_INPUT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def encode_payload(payload: dict) -> bytes:
    raw = (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()
    return gzip.compress(raw, compresslevel=9, mtime=0)


def unpack_object_stream(module, record: dict) -> bytes:
    packed = base64.b64decode(record["data_base64"], validate=True)
    return gzip.decompress(packed) if record["encoding"] == "gzip" else module.lzma.decompress(packed)


def pack_object_stream(module, record: dict, data: bytes) -> None:
    packed = (gzip.compress(data, compresslevel=9, mtime=0) if record["encoding"] == "gzip"
              else module.lzma.compress(data, preset=6))
    record["data_base64"] = base64.b64encode(packed).decode("ascii")


def rejected(module, archive_bytes: bytes, root: Path) -> str:
    workspace = root / "workspace"
    workspace.mkdir(parents=True)
    archive = workspace / "input.gz"
    archive.write_bytes(archive_bytes)
    module.WORKSPACE = workspace
    os.environ.update({"LANE": "merge", "INFRA_SHA": SHA, "PROOF_SHA": SHA})
    try:
        module.restore_archive(archive, workspace / "evidence")
    except SystemExit as error:
        return str(error)
    raise AssertionError("corrupt archive was accepted")


SHA = subprocess.check_output(
    ["git", "-C", str(REPO), "rev-parse", "HEAD"], text=True
).strip()


def main() -> None:
    module = load_source_input()
    source_payload = module.make_payload(REPO, SHA, SHA, "merge")
    encoded_chars = len(base64.b64encode(source_payload))
    parts = (encoded_chars + PART_CHARS - 1) // PART_CHARS
    assert parts <= LIMIT_PARTS, f"source transport still needs {parts} slots"

    with tempfile.TemporaryDirectory(prefix="source-input-transport-") as temporary:
        root = Path(temporary)
        workspace = root / "roundtrip-workspace"
        workspace.mkdir()
        archive = workspace / "source.gz"
        archive.write_bytes(source_payload)
        module.WORKSPACE = workspace
        os.environ.update({"LANE": "merge", "INFRA_SHA": SHA, "PROOF_SHA": SHA})
        certificate = module.restore_archive(archive, workspace / "evidence")
        assert certificate["infra"]["head"] == SHA
        assert certificate["proof"]["head"] == SHA
        assert certificate["archive_sha256"] == hashlib.sha256(source_payload).hexdigest()

        payload = json.loads(gzip.decompress(source_payload))
        assert payload["schema"] == module.SHARED_STREAM_SCHEMA
        objects = payload["shared_objects"]
        assert objects and len({item["oid"] for item in objects}) == len(objects)

        legacy = json.loads(json.dumps(payload))
        legacy_stream = unpack_object_stream(module, legacy["object_stream"])
        del legacy["object_stream"]
        legacy["schema"] = module.SHARED_SCHEMA
        for item in legacy["shared_objects"]:
            start = item.pop("offset")
            raw_object = legacy_stream[start:start + item["size"]]
            packed_gzip = gzip.compress(raw_object, mtime=0)
            packed_xz = module.lzma.compress(raw_object, preset=6)
            item["compression"] = "xz" if len(packed_xz) < len(packed_gzip) else "gzip"
            item["data_base64"] = base64.b64encode(
                packed_xz if item["compression"] == "xz" else packed_gzip
            ).decode("ascii")
        legacy_workspace = root / "legacy-workspace"
        legacy_workspace.mkdir()
        legacy_archive = legacy_workspace / "source.gz"
        legacy_archive.write_bytes(encode_payload(legacy))
        module.WORKSPACE = legacy_workspace
        legacy_certificate = module.restore_archive(legacy_archive, legacy_workspace / "evidence")
        assert legacy_certificate["infra"]["head"] == SHA
        assert legacy_certificate["proof"]["head"] == SHA

        bad_offset = json.loads(json.dumps(payload))
        bad_offset["shared_objects"][0]["offset"] += 1
        bad_offset_bytes = encode_payload(bad_offset)
        offset_message = rejected(module, bad_offset_bytes, root / "bad-offset")
        assert "noncontiguous" in offset_message

        bad_identity = json.loads(json.dumps(payload))
        stream = bytearray(unpack_object_stream(module, bad_identity["object_stream"]))
        first = next(item for item in bad_identity["shared_objects"] if item["size"] > 0)
        stream[first["offset"]] ^= 1
        pack_object_stream(module, bad_identity["object_stream"], bytes(stream))
        identity_message = rejected(module, encode_payload(bad_identity), root / "bad-identity")
        assert "Git object identity check failed" in identity_message

        missing_object = json.loads(json.dumps(payload))
        missing_entry = missing_object["shared_objects"].pop()
        missing_oid = missing_entry["oid"]
        truncated_stream = unpack_object_stream(module, missing_object["object_stream"])[
            :missing_entry["offset"]
        ]
        pack_object_stream(module, missing_object["object_stream"], truncated_stream)
        missing_message = rejected(module, encode_payload(missing_object), root / "missing-object")
        assert (missing_oid in missing_message or "invalid shared-object reference" in missing_message), missing_message

    receipt = {
        "classification": "PASS_SERVICE_ONLY",
        "commit": SHA,
        "schema": payload["schema"],
        "object_stream_encoding": payload["object_stream"]["encoding"],
        "archive_sha256": hashlib.sha256(source_payload).hexdigest(),
        "archive_bytes": len(source_payload),
        "base64_chars": encoded_chars,
        "part_chars": PART_CHARS,
        "parts": parts,
        "part_limit": LIMIT_PARTS,
        "shared_object_count": len(objects),
        "infra_restored_paths": len(certificate["infra"]["restored_paths"]),
        "proof_restored_paths": len(certificate["proof"]["restored_paths"]),
        "roundtrip_original_heads": True,
        "legacy_v2_restore_compatible": True,
        "corruptions_rejected": {
            "noncontiguous_offset": True,
            "changed_object_bytes_git_oid": True,
            "missing_referenced_object": True,
        },
        "compiler_extractor_verifier_executed": False,
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
