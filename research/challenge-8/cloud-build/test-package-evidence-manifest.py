#!/usr/bin/env python3
"""Regression tests for bounded, lossless evidence manifest packaging."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
PACKAGER = HERE / "package-evidence.py"
LIMIT = 8 * 1024 * 1024


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def make_input(root: Path, *, large_audit: bool, include_audit: bool = True,
               audit_payload_bytes: int = 0, pretty_audit: bool = False,
               invalid_audit: bool = False, audit_companion_collision: bool = False) -> dict[str, bytes]:
    config = {
        "steps": [{"id": "execute", "name": "proof-image",
                   "env": ["LANE=stock", "INFRA_SHA=" + "1" * 40,
                           "PROOF_SHA=" + "2" * 40]}]
    }
    files = {
        "run-exit.txt": b"0\n",
        "full-stdout.log": b"stdout\n",
        "full-stderr.log": b"stderr\n",
        "submitted-config.json": (json.dumps(config, sort_keys=True) + "\n").encode(),
        "environment.txt": b"LANE=stock\n",
        "allprooflogs/cases/case.json": b'{"case":"fixture"}\n',
        "allprooflogs/stage.log": b"stage\n",
    }
    if include_audit:
        audit = {"accepted": False, "diagnostic_complete": False}
        if large_audit:
            # The parsed audit is valid and faithfully duplicated into the
            # manifest. Pretty-printing it alone pushes the old representation
            # beyond the manifest limit while compact JSON remains bounded.
            audit["events"] = [{"i": i, "ok": False} for i in range(245_000)]
        if audit_payload_bytes:
            audit["payload"] = "x" * audit_payload_bytes
        files["allprooflogs/proof-audit.json"] = (
            b'{"accepted":false,"padding":"' + b"x" * (LIMIT + 1) if invalid_audit else
            ((json.dumps(audit, sort_keys=True, indent=2) if pretty_audit else
              json.dumps(audit, sort_keys=True, separators=(",", ":"))) + "\n").encode())
    if audit_companion_collision:
        files["allprooflogs/proof-audit.json.original-bytes"] = b"preexisting companion\n"
    for rel, data in files.items():
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    return files


def package(evidence: Path, out: Path) -> subprocess.CompletedProcess:
    config = json.loads((evidence / "submitted-config.json").read_text())
    config_sha = sha((evidence / "submitted-config.json").read_bytes())
    env = os.environ.copy()
    env.update({
        "CLOUD_BUILD_ID": "synthetic-package-test",
        "INFRA_SHA": "1" * 40,
        "PROOF_SHA": "2" * 40,
        "LANE": "stock",
        "SUBMITTED_CONFIG_SHA": config_sha,
        "PROOF_IMAGE": "proof-image",
    })
    return subprocess.run(
        [sys.executable, str(PACKAGER), "--evidence", str(evidence), "--out", str(out)],
        env=env, capture_output=True, text=True, check=False)


def reattest(out: Path, mutate_manifest) -> None:
    """Rewrite only manifest metadata and regenerate the synthetic receipt."""
    with tarfile.open(out / "evidence.tar.gz", "r:gz") as archive:
        members = {member.name: archive.extractfile(member).read()
                   for member in archive if member.isfile()}
    manifest = json.loads(members["manifest.json"])
    mutate_manifest(manifest)
    members["manifest.json"] = (json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n").encode()
    temporary = out / "rewritten-evidence.tar.gz"
    with tarfile.open(temporary, "w:gz") as archive:
        for name, data in sorted(members.items()):
            info = tarfile.TarInfo(name)
            info.size = len(data)
            info.mode = 0o644
            import io
            archive.addfile(info, io.BytesIO(data))
    temporary.replace(out / "evidence.tar.gz")
    (out / "manifest.json").write_bytes(members["manifest.json"])
    archive_hash = sha((out / "evidence.tar.gz").read_bytes())
    (out / "archive.sha256").write_text(f"{archive_hash}  evidence.tar.gz\n")
    (out / "upload-complete.json").write_text(json.dumps({
        "uploaded": True, "archive_sha256": archive_hash,
        "build_id": manifest["build_id"],
        "text_logs_index_sha256": manifest["text_logs_index_sha256"],
    }))


def verify(out: Path, manifest: dict, verifier: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([
        sys.executable, str(verifier or HERE / "verify-evidence.py"), "--directory", str(out),
        "--expected-build-id", "synthetic-package-test", "--expected-lane", "stock",
        "--expected-infra-sha", "1" * 40, "--expected-proof-sha", "2" * 40,
        "--expected-config-sha", manifest["submitted_config_sha256"],
    ], capture_output=True, text=True, check=False)


class ManifestPackagingTests(unittest.TestCase):
    def test_large_manifest_is_compact_and_archive_is_lossless(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            evidence, out = root / "evidence", root / "out"
            original = make_input(evidence, large_audit=True)
            result = package(evidence, out)
            self.assertEqual(result.returncode, 0, result.stderr)

            manifest_bytes = (out / "manifest.json").read_bytes()
            manifest = json.loads(manifest_bytes)
            audit = json.loads(original["allprooflogs/proof-audit.json"])
            pretty_manifest_bytes = len((json.dumps(manifest, sort_keys=True, indent=2) + "\n").encode())
            self.assertLessEqual(len(original["allprooflogs/proof-audit.json"]), LIMIT)
            self.assertGreater(pretty_manifest_bytes, LIMIT)
            self.assertLessEqual(len(manifest_bytes), LIMIT)
            self.assertEqual(manifest["proof_audit"], audit)
            self.assertEqual(len(manifest["proof_audit"]["events"]), 245_000)

            with tarfile.open(out / "evidence.tar.gz", "r:gz") as archive:
                members = {member.name: archive.extractfile(member).read()
                           for member in archive if member.isfile()}
            inventory_bytes = members["files-sha256.json"]
            inventory = json.loads(inventory_bytes)
            self.assertEqual(manifest["files_inventory_sha256"], sha(inventory_bytes))
            self.assertEqual(set(inventory), set(members) - {"manifest.json", "files-sha256.json"})
            for name, expected_hash in inventory.items():
                self.assertEqual(sha(members[name]), expected_hash, name)
            for name, data in original.items():
                self.assertEqual(members[name], data, name)
                self.assertEqual(manifest["input_sha256"][name], sha(data), name)
            self.assertNotIn("config_fields", manifest)
            config = original["submitted-config.json"]
            self.assertEqual(manifest["config_fields_reference"], {
                "path": "submitted-config.json", "sha256": sha(config),
                "size_bytes": len(config),
            })

            archive_bytes = (out / "evidence.tar.gz").read_bytes()
            archive_hash = sha(archive_bytes)
            (out / "archive.sha256").write_text(f"{archive_hash}  evidence.tar.gz\n")
            (out / "upload-complete.json").write_text(json.dumps({
                "uploaded": True, "archive_sha256": archive_hash,
                "build_id": manifest["build_id"],
                "text_logs_index_sha256": manifest["text_logs_index_sha256"],
            }))
            verified = verify(out, manifest)
            self.assertEqual(verified.returncode, 0, verified.stderr)
            self.assertIn('"integrity_verified": true', verified.stdout)

            reattest(out, lambda value: value["config_fields_reference"].update(sha256="0" * 64))
            rejected = verify(out, manifest)
            self.assertEqual(rejected.returncode, 1)
            self.assertIn("submitted-config reference/hash/size mismatch", rejected.stderr)

            reattest(out, lambda value: value.update(config_fields_reference=None))
            null_reference = verify(out, manifest)
            self.assertEqual(null_reference.returncode, 1)
            self.assertIn("submitted-config reference/hash/size mismatch", null_reference.stderr)

            # Schema-v1 packages without the optional compact reference remain valid.
            reattest(out, lambda value: value.pop("config_fields_reference"))
            legacy = verify(out, manifest)
            self.assertEqual(legacy.returncode, 0, legacy.stderr)

    def test_oversized_pretty_audit_is_canonicalized_losslessly(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            evidence, out = root / "evidence", root / "out"
            original = make_input(evidence, large_audit=True, pretty_audit=True)
            original_audit = original["allprooflogs/proof-audit.json"]
            self.assertGreater(len(original_audit), LIMIT)
            result = package(evidence, out)
            self.assertEqual(result.returncode, 0, result.stderr)

            with tarfile.open(out / "evidence.tar.gz", "r:gz") as archive:
                members = {member.name: archive.extractfile(member).read()
                           for member in archive if member.isfile()}
            manifest = json.loads(members["manifest.json"])
            audit_path = "allprooflogs/proof-audit.json"
            companion_path = audit_path + ".original-bytes"
            canonical = members[audit_path]
            descriptor, = manifest["proof_audit_canonicalizations"]
            self.assertEqual(json.loads(canonical), json.loads(original_audit))
            self.assertEqual(members[companion_path], original_audit)
            self.assertLessEqual(len(canonical), LIMIT)
            self.assertLess(len(canonical), len(original_audit))
            self.assertEqual(descriptor, {
                "source_path": audit_path,
                "canonical_path": audit_path,
                "original_bytes_path": companion_path,
                "original_sha256": sha(original_audit),
                "original_size_bytes": len(original_audit),
                "canonical_sha256": sha(canonical),
                "canonical_size_bytes": len(canonical),
                "encoding": "UTF-8 JSON; sorted keys; compact separators; trailing LF",
            })
            self.assertFalse(manifest["verification_accepted"])
            self.assertFalse(manifest["proof_audit"]["accepted"])
            for name, data in original.items():
                if name != audit_path:
                    self.assertEqual(members[name], data, name)
                    self.assertEqual(manifest["input_sha256"][name], sha(data), name)
            self.assertEqual(manifest["input_sha256"][audit_path], sha(canonical))
            self.assertEqual(manifest["input_sha256"][companion_path], sha(original_audit))
            inventory = json.loads(members["files-sha256.json"])
            self.assertEqual(set(inventory), set(members) - {"manifest.json", "files-sha256.json"})
            self.assertEqual(inventory[audit_path], sha(canonical))
            self.assertEqual(inventory[companion_path], sha(original_audit))

            archive_hash = sha((out / "evidence.tar.gz").read_bytes())
            (out / "archive.sha256").write_text(f"{archive_hash}  evidence.tar.gz\n")
            (out / "upload-complete.json").write_text(json.dumps({
                "uploaded": True, "archive_sha256": archive_hash,
                "build_id": manifest["build_id"],
                "text_logs_index_sha256": manifest["text_logs_index_sha256"],
            }))
            verified = verify(out, manifest)
            self.assertEqual(verified.returncode, 0, verified.stderr)
            self.assertIn('"integrity_verified": true', verified.stdout)

            reattest(out, lambda value: value["proof_audit_canonicalizations"][0].update(
                original_bytes_path="missing.original-bytes"))
            tampered = verify(out, manifest)
            self.assertEqual(tampered.returncode, 1)
            self.assertIn("invalid proof-audit canonicalization descriptor", tampered.stderr)

            # The established verifier ignores the additive descriptor and
            # accepts the bounded canonical audit plus inventoried byte archive.
            baseline = subprocess.run(
                ["git", "show", "4017cc:research/challenge-8/cloud-build/verify-evidence.py"],
                cwd=HERE.parents[2], capture_output=True, check=True)
            old_verifier = root / "old-verify-evidence.py"
            old_verifier.write_bytes(baseline.stdout)
            reattest(out, lambda value: value["proof_audit_canonicalizations"].__setitem__(0, descriptor))
            old_verified = verify(out, manifest, verifier=old_verifier)
            self.assertEqual(old_verified.returncode, 0, old_verified.stderr)
            self.assertIn('"integrity_verified": true', old_verified.stdout)

    def test_missing_audit_is_preserved_as_incomplete(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            evidence, out = root / "evidence", root / "out"
            make_input(evidence, large_audit=False, include_audit=False)
            result = package(evidence, out)
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads((out / "manifest.json").read_bytes())
            self.assertFalse(manifest["evidence_complete"])
            self.assertFalse(manifest["verification_accepted"])
            self.assertIn("allprooflogs/proof-audit.json", manifest["missing_mandatory"])

    def test_symlink_input_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            evidence, out = root / "evidence", root / "out"
            make_input(evidence, large_audit=False)
            (evidence / "unsupported-link").symlink_to(evidence / "run-exit.txt")
            result = package(evidence, out)
            self.assertEqual(result.returncode, 1)
            self.assertIn("symlink in evidence", result.stderr)

    def test_compact_manifest_over_limit_reports_size_without_truncation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            evidence, out = root / "evidence", root / "out"
            make_input(evidence, large_audit=False, audit_payload_bytes=LIMIT - 1024)
            original_audit = (evidence / "allprooflogs/proof-audit.json").stat().st_size
            self.assertLessEqual(original_audit, LIMIT)
            result = package(evidence, out)
            self.assertEqual(result.returncode, 1)
            self.assertIn("external manifest exceeds 8 MiB", result.stderr)
            self.assertIn("encoded_bytes=", result.stderr)
            self.assertIn("limit_bytes=8388608", result.stderr)
            self.assertIn("largest_5_field_values_bytes=", result.stderr)
            self.assertFalse((out / "evidence.tar.gz").exists())

    def test_oversized_audit_rejects_invalid_or_unhelpful_canonicalization(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            evidence, out = root / "evidence", root / "out"
            make_input(evidence, large_audit=False, audit_payload_bytes=LIMIT)
            result = package(evidence, out)
            self.assertEqual(result.returncode, 1)
            self.assertIn("no bounded size reduction", result.stderr)
            self.assertIn("original_bytes=", result.stderr)
            self.assertIn("canonical_bytes=", result.stderr)
            self.assertIn("limit_bytes=8388608", result.stderr)
            self.assertFalse((out / "evidence.tar.gz").exists())

            make_input(evidence / "invalid", large_audit=False, invalid_audit=True)
            invalid = package(evidence / "invalid", out / "invalid-out")
            self.assertEqual(invalid.returncode, 1)
            self.assertIn("invalid JSON", invalid.stderr)

            make_input(evidence / "collision", large_audit=True, pretty_audit=True,
                       audit_companion_collision=True)
            collision = package(evidence / "collision", out / "collision-out")
            self.assertEqual(collision.returncode, 1)
            self.assertIn("companion path collision", collision.stderr)


if __name__ == "__main__":
    unittest.main()
