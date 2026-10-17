#!/usr/bin/env python3
"""Pure Git-object transport tests; no compiler or verifier is invoked."""
from __future__ import annotations

import base64
import gzip
import hashlib
import importlib.util
import json
import lzma
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


SOURCE_PATH = Path(__file__).with_name("source-input.py")
SPEC = importlib.util.spec_from_file_location("source_input_transport_test", SOURCE_PATH)
assert SPEC is not None and SPEC.loader is not None
source = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(source)


LANE = "source-codec-test"
RECIPE_PATH = source.RECIPE_PREFIX + LANE + ".json"
UTF8_PATH = "library/core/src/utf8.txt"
BINARY_PATH = "library/core/src/binary.bin"


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode().strip()


class SourceTransportTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "init", "--quiet", str(self.repo)], check=True)
        git(self.repo, "config", "user.email", "transport-test@example.invalid")
        git(self.repo, "config", "user.name", "transport test")
        self.utf8 = b"\xef\xbb\xbfalpha\r\nna\xc3\xafve \xe2\x98\x83\r\n"
        self.binary = b"\x00\xff\x80\xfe\x00"
        for path in source.EXACT_INFRA_CORE:
            self.write(path, b"# infra fixture\n")
        self.write("research/challenge-8/cloud-build/test-entry.sh", b"#!/bin/sh\nexit 0\n")
        self.write(UTF8_PATH, self.utf8)
        self.write(BINARY_PATH, self.binary)
        self.infra_paths = sorted(set(source.EXACT_INFRA_CORE +
                                      ("research/challenge-8/cloud-build/test-entry.sh",)))
        self.proof_paths = sorted((UTF8_PATH, BINARY_PATH))
        self.recipe = {
            "schema": "smallsort-cloud-recipe-v1",
            "lane": LANE,
            "entrypoint": "research/challenge-8/cloud-build/test-entry.sh",
            "infra_paths": self.infra_paths,
            "proof_paths": self.proof_paths,
            "infra_transport": source.EXACT_INFRA_TRANSPORT,
        }
        self.write(RECIPE_PATH, (json.dumps(self.recipe, sort_keys=True, indent=2) + "\n").encode())
        git(self.repo, "add", ".")
        subprocess.run(["git", "-C", str(self.repo), "-c", "user.email=transport-test@example.invalid",
                        "-c", "user.name=transport test", "commit", "--quiet", "-m", "fixture"], check=True)
        self.commit = git(self.repo, "rev-parse", "HEAD")

    def tearDown(self):
        self.temp.cleanup()

    def write(self, path: str, data: bytes):
        target = self.repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)

    def recipe_with_codec(self, codec: str | None):
        recipe = dict(self.recipe)
        if codec is not None:
            recipe["source_transport_codec"] = codec
        self.write(RECIPE_PATH, (json.dumps(recipe, sort_keys=True, indent=2) + "\n").encode())
        subprocess.run(["git", "-C", str(self.repo), "add", RECIPE_PATH], check=True)
        subprocess.run(["git", "-C", str(self.repo), "-c", "user.email=transport-test@example.invalid",
                        "-c", "user.name=transport test", "commit", "--quiet", "-m", "codec"], check=True)
        self.commit = git(self.repo, "rev-parse", "HEAD")

    def archive(self):
        return source.make_payload(self.repo, self.commit, self.commit, LANE)

    def test_compact_roundtrip_preserves_utf8_and_binary_fallback_and_closure(self):
        self.recipe_with_codec(source.SOURCE_TRANSPORT_CODEC)
        archive = self.archive()
        payload, raw = source.decode_payload(archive)
        self.assertEqual(payload["schema"], source.SHARED_SCHEMA)
        self.assertEqual(payload["recipe"]["source_transport_codec"], source.SOURCE_TRANSPORT_CODEC)
        rows = {item["oid"]: item for item in payload["shared_objects"]}
        utf8_oid = git(self.repo, "rev-parse", self.commit + ":" + UTF8_PATH)
        binary_oid = git(self.repo, "rev-parse", self.commit + ":" + BINARY_PATH)
        self.assertEqual(rows[utf8_oid]["data_utf8"].encode("utf-8"), self.utf8)
        self.assertNotIn("data_base64", rows[utf8_oid])
        self.assertEqual(rows[binary_oid]["compression"], "gzip")
        self.assertEqual(gzip.decompress(base64.b64decode(rows[binary_oid]["data_base64"])), self.binary)
        self.assertLess(len(archive), len(raw))

        old_workspace = source.WORKSPACE
        old_env = {key: os.environ.get(key) for key in ("LANE", "INFRA_SHA", "PROOF_SHA")}
        restore_root = self.root / "restore"
        restore_root.mkdir()
        try:
            source.WORKSPACE = restore_root
            os.environ.update(LANE=LANE, INFRA_SHA=self.commit, PROOF_SHA=self.commit)
            archive_path = restore_root / "input.gz"
            evidence = restore_root / "evidence"
            archive_path.write_bytes(archive)
            result = source.restore_archive(archive_path, evidence)
            self.assertEqual(result["schema"], source.SHARED_SCHEMA)
            self.assertEqual((restore_root / "proof" / UTF8_PATH).read_bytes(), self.utf8)
            self.assertEqual((restore_root / "proof" / BINARY_PATH).read_bytes(), self.binary)
            self.assertEqual(git(restore_root / "proof", "rev-parse", "HEAD"), self.commit)
        finally:
            source.WORKSPACE = old_workspace
            for key, value in old_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

    def test_legacy_transport_remains_gzip_shared_schema_and_decodes(self):
        archive = self.archive()
        payload, _ = source.decode_payload(archive)
        self.assertEqual(payload["schema"], source.SHARED_SCHEMA)
        self.assertNotIn("source_transport_codec", payload["recipe"])
        self.assertTrue(all("data_utf8" not in row for row in payload["shared_objects"]))
        self.assertEqual(archive, self.archive())

    def test_direct_restore_rejects_corrupt_size_oid_and_ambiguous_utf8(self):
        record, _ = source.repo_record(self.repo, self.commit, self.proof_paths)
        bad_size = json.loads(json.dumps(record))
        next(row for row in bad_size["objects"] if row["type"] == "blob")["size"] += 1
        bad_oid = json.loads(json.dumps(record))
        next(row for row in bad_oid["objects"] if row["type"] == "blob")["oid"] = "0" * 40
        for index, bad in enumerate((bad_size, bad_oid)):
            with self.subTest(index=index), tempfile.TemporaryDirectory() as tmp:
                with self.assertRaises(SystemExit):
                    source.restore_repo(bad, Path(tmp) / "dest", self.proof_paths)

        utf8_record, _ = source.repo_record(self.repo, self.commit, [UTF8_PATH])
        blob = next(row for row in utf8_record["objects"] if row["type"] == "blob")
        blob["data_utf8"] = self.utf8.decode("utf-8-sig")
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(SystemExit):
            source.restore_repo(utf8_record, Path(tmp) / "dest", [UTF8_PATH])

    def test_unknown_and_ambiguous_codec_tags_are_rejected(self):
        invalid = dict(self.recipe, source_transport_codec="xz-whatever")
        with self.assertRaises(SystemExit):
            source.validate_recipe(invalid, LANE)
        envelope = {"schema": source.COMPACT_SCHEMA,
                    "transport_codec": source.SOURCE_TRANSPORT_CODEC,
                    "payload_xz_base64": "", "extra": True}
        raw = (json.dumps(envelope) + "\n").encode()
        with self.assertRaises(SystemExit):
            source.decode_payload(gzip.compress(raw, mtime=0))
        tagged_legacy = {"schema": source.SHARED_SCHEMA, "lane": LANE,
                         "recipe": dict(self.recipe, source_transport_codec=source.SOURCE_TRANSPORT_CODEC)}
        with self.assertRaises(SystemExit):
            source.decode_payload(gzip.compress(json.dumps(tagged_legacy).encode(), mtime=0))
        legacy_utf8 = {"schema": source.SCHEMA, "lane": LANE,
                       "infra": {"objects": []},
                       "proof": {"objects": [{"oid": "0" * 40, "type": "blob",
                                               "size": 0, "data_utf8": ""}]}}
        with self.assertRaises(SystemExit):
            source.decode_payload(gzip.compress(json.dumps(legacy_utf8).encode(), mtime=0))
        duplicate_tag = (b'{"schema":"' + source.COMPACT_SCHEMA.encode() +
                         b'","schema":"' + source.COMPACT_SCHEMA.encode() +
                         b'","transport_codec":"' + source.SOURCE_TRANSPORT_CODEC.encode() +
                         b'","payload_xz_base64":""}')
        with self.assertRaises(SystemExit):
            source.decode_payload(gzip.compress(duplicate_tag, mtime=0))

    def test_unknown_inner_codec_and_truncated_xz_are_rejected(self):
        self.recipe_with_codec(source.SOURCE_TRANSPORT_CODEC)
        payload, raw = source.decode_payload(self.archive())
        envelope = {"schema": source.COMPACT_SCHEMA,
                    "transport_codec": "unknown",
                    "payload_xz_base64": base64.b64encode(raw).decode()}
        with self.assertRaises(SystemExit):
            source.decode_payload(gzip.compress(json.dumps(envelope).encode(), mtime=0))
        envelope["transport_codec"] = source.SOURCE_TRANSPORT_CODEC
        envelope["payload_xz_base64"] = base64.b64encode(b"\xfd7zXZ\x00bad").decode()
        with self.assertRaises(SystemExit):
            source.decode_payload(gzip.compress(json.dumps(envelope).encode(), mtime=0))

    def test_outer_and_compact_decoders_enforce_limits_and_reject_truncation(self):
        old_limit = source.MAX_DECODED_PAYLOAD
        try:
            source.MAX_DECODED_PAYLOAD = 64
            oversized_legacy = gzip.compress(json.dumps({"schema": source.SCHEMA,
                                                          "lane": LANE,
                                                          "infra": {}, "proof": {},
                                                          "padding": "x" * 100}).encode(), mtime=0)
            with self.assertRaises(SystemExit):
                source.decode_payload(oversized_legacy)

            inner = (json.dumps({"schema": source.SHARED_SCHEMA,
                                 "recipe": {"source_transport_codec": source.SOURCE_TRANSPORT_CODEC},
                                 "padding": "x" * 100}).encode())
            envelope = {"schema": source.COMPACT_SCHEMA,
                        "transport_codec": source.SOURCE_TRANSPORT_CODEC,
                        "payload_xz_base64": base64.b64encode(
                            lzma.compress(inner, format=lzma.FORMAT_XZ)).decode()}
            with self.assertRaises(SystemExit):
                source.decode_payload(gzip.compress(json.dumps(envelope).encode(), mtime=0))
        finally:
            source.MAX_DECODED_PAYLOAD = old_limit

        valid_gzip = gzip.compress(b'{"schema":"smallsort-git-source-input-v1"}', mtime=0)
        with self.assertRaises(SystemExit):
            source.decode_payload(valid_gzip[:-5])


if __name__ == "__main__":
    unittest.main()
